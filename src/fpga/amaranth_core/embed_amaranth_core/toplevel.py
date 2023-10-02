from amaranth import *
from amaranth.lib import wiring, data
from amaranth.lib.wiring import In, Out
import enum

from .resolution import *


assert 47 <= (74250000 / VID_DIV_RATIO / VID_V_TOTAL / VID_H_TOTAL) < 61, "Pixel clock out of range"


class PixelClockDiv(wiring.Component):
    clk90   : Out(1) # Pixel clock, 90 deg trailing
    clk     : Out(1) # Pixel clock
    stb     : Out(1) # Single cycle strobe at rising edge of `clk`

    def __init__(self, ratio=4):
        super().__init__()

        assert ratio >= 4 and ratio % 4 == 0, "Ratio must be at least 4 and divisible by 4"
        self.ratio = ratio

    def elaborate(self, platform):
        m = Module()

        # clk90  __/¯¯¯\_
        # clk    /¯¯¯\___
        # rgb    X--------
        # Note clock rises one cycle AFTER rgb strobe

        # Generate bitmap with ratio/2 0s (low order) followed by ratio/2 1s (high order)
        clk_reg = Signal(self.ratio, reset=((1 << (self.ratio // 2)) - 1) << (self.ratio // 2))
        m.d.sync += clk_reg.eq(clk_reg.rotate_left(1))
        m.d.comb += [
            self.clk.eq(clk_reg[0]),
            self.clk90.eq(clk_reg[self.ratio // 4]),
        ]

        stb_reg = Signal(self.ratio, reset=1)
        m.d.sync += stb_reg.eq(stb_reg.rotate_left(1))
        m.d.comb += [
            self.stb.eq(stb_reg[0])
        ]

        return m


class Toplevel(wiring.Component):
    clk             : In(1)
    rst             : In(1)
    init_done       : Out(1)

    user1           : Out(1)
    user2           : In(1)

    dbg_tx          : Out(1)
    dbg_rx          : In(1)

    video_rgb_clk   : Out(1)
    video_rgb_clk90 : Out(1)
    video_rgb       : Out(data.StructLayout({"b": 8, "g": 8, "r": 8}))
    video_de        : Out(1)
    video_skip      : Out(1)
    video_vs        : Out(1)
    video_hs        : Out(1)

    audio_mclk      : Out(1)
    audio_lrck      : Out(1) # A better name would be audio_select but this is what the i2s standard calls it
    audio_adc       : In(1)  # Unused
    audio_dac       : Out(1)

    cont1_key       : In(32)
    cont2_key       : In(32)
    cont3_key       : In(32)
    cont4_key       : In(32)
    cont1_joy       : In(32)
    cont2_joy       : In(32)
    cont3_joy       : In(32)
    cont4_joy       : In(32)
    cont1_trig      : In(16)
    cont2_trig      : In(16)
    cont3_trig      : In(16)
    cont4_trig      : In(16)

    def elaborate(self, platform):
        m = Module()

        m.domains.boot = boot = ClockDomain(reset_less=True)
        m.domains.sync = sync = ClockDomain(async_reset=True)
        m.d.comb += [
            boot.clk.eq(self.clk),
            sync.clk.eq(self.clk),
            sync.rst.eq(self.rst),
        ]

        m.d.boot += self.init_done.eq(1)

        # Video interface

        m.submodules.video_clk_div = video_clk_div = PixelClockDiv(ratio=VID_DIV_RATIO)
        m.d.comb += [
            self.video_rgb_clk.eq(video_clk_div.clk),
            self.video_rgb_clk90.eq(video_clk_div.clk90),
        ]

        video_x_count = Signal(10)
        video_y_count = Signal(10)

        # Audio interface

        audgen_silenced = Signal(1)
        audgen_channel_select = Signal(1)
        audgen_channel_internal = Signal(4)
        audgen_bit_update_stb = Signal(1)
        audgen_word_update_stb = Signal(1)
        audgen_dac = Signal(1)

        # App interface

        video_hsync_stb = Signal(1)
        video_vsync_stb = Signal(1)
        video_active = Signal(1)

        m.d.comb += [ # Hsync strobes the pixel *after* the final displayed pixel of the row; vsync strobes one pixel after final-row hsync
            video_hsync_stb.eq(video_clk_div.stb & (video_x_count == VID_H_ACTIVE + VID_H_BPORCH)),
            video_vsync_stb.eq(video_clk_div.stb & (video_x_count == VID_H_ACTIVE + VID_H_BPORCH + 1) & (video_y_count == VID_V_ACTIVE + VID_V_BPORCH - 1)),
            video_active.eq((video_x_count >= VID_H_BPORCH) & (video_x_count < VID_H_ACTIVE + VID_H_BPORCH) &
                (video_y_count >= VID_V_BPORCH) & (video_y_count < VID_V_ACTIVE + VID_V_BPORCH))
        ]

        self.app_elaborate(platform, m,
            video_clk_div.stb, video_hsync_stb, video_vsync_stb, video_x_count, video_y_count, video_active, self.video_rgb,
            audgen_silenced, audgen_channel_select, audgen_channel_internal, audgen_bit_update_stb, audgen_word_update_stb, audgen_dac)

        # Draw

        with m.If(video_clk_div.stb):
            # Vertical and horizontal sync
            m.d.sync += [
                self.video_vs.eq((video_x_count == 0) & (video_y_count == 0)),
                # HS must occur at least 3 cycles after VS
                self.video_hs.eq(video_x_count == 3),
            ]

            # Iterate screen "beam"
            m.d.sync += video_x_count.eq(video_x_count + 1)
            with m.If(video_x_count == VID_H_TOTAL - 1):
                m.d.sync += video_x_count.eq(0)
                m.d.sync += video_y_count.eq(video_y_count + 1)
                with m.If(video_y_count == VID_V_TOTAL - 1):
                    m.d.sync += video_y_count.eq(0)

            # inactive screen areas must be black
            m.d.sync += [
                self.video_de.eq(video_active)
            ]

        # Audio

        # Recreate Analogue i2s protocol from core_top.v
        # FIXME: This could be done more elegantly with Amaranth builtins instead of logic

        # Clocks

        CYCLE_48KHZ = Const(122880 * 2, Shape(width=22))
        CYCLE_OVERFLOW_VALUE = 742500
        CYCLE_OVERFLOW = Const(CYCLE_OVERFLOW_VALUE, Shape(width=22))

        audgen_accum = Signal(22, reset=CYCLE_OVERFLOW_VALUE) # Master clock
        audgen_mclk = Signal(1)
        audgen_mclk_stb = Signal(1) # Trigger on first cycle (because of accum value)

        audgen_slck_count = Signal(2, reset=3) # Serial clock # TODO: Collapse slck_count into lrck_count?
        audgen_slck = Signal(1)
        audgen_slck_update = Signal(1, reset=1) # Trigger on first cycle

        audgen_lrck_count = Signal(8) # Left-right select
        audgen_lrck = Signal(1)

        # "Master clock"
        # This produces a cycle of 1/48000/256 seconds
        m.d.sync += audgen_accum.eq(audgen_accum + CYCLE_48KHZ)
        m.d.comb += audgen_mclk_stb.eq(audgen_accum >= CYCLE_OVERFLOW)
        with m.If(audgen_mclk_stb):
            m.d.sync += [
                audgen_mclk.eq(~audgen_mclk),
                audgen_accum.eq(audgen_accum - CYCLE_OVERFLOW + CYCLE_48KHZ)
            ]

        # "Serial clock"
        # 4x period master clock, produces a cycle of 1/48000/64 seconds
        m.d.comb += audgen_slck.eq( ~audgen_slck_count[1] ) # Use counter bit as clock
        m.d.sync += audgen_slck_update.eq(0) # Update strobe is usually 0

        with m.If(audgen_mclk_stb & (~audgen_mclk)):
            m.d.sync += [
                audgen_slck_count.eq( audgen_slck_count + 1 )
            ]
            with m.If(audgen_slck_count == 2): # We are halfway through slck low, so this is a good time to run updates.
                m.d.sync += [ # FIXME: Would probably be ok to move this forward or backward?
                    audgen_slck_update.eq(1)
                ]

        # "Left-right clock" (channel select)
        # 256x period master clock / 64x period serial clock, cycle is audio-rate 48khz
        m.d.comb += audgen_lrck.eq(audgen_lrck_count[7]) # Use counter bit as clock
        with m.If(audgen_mclk_stb & (~audgen_mclk)):
            m.d.sync += [
                audgen_lrck_count.eq( audgen_lrck_count + 1 )
            ]

        # Audio generate

        m.d.comb += [ # For app interface
            audgen_channel_select.eq(audgen_lrck),
            audgen_word_update_stb.eq(0), # Will override below
            audgen_bit_update_stb.eq(0), # Will override below
        ]

        # Bits of audgen_lrck_count: ABCCCCDD
        # D: audgen_slck_count equivalent; C: audgen_channel_internal; B: audgen_silenced; A: audgen_lrck
        audgen_lrck_internal = Signal(5)
        m.d.comb += [
            audgen_channel_internal.eq(audgen_lrck_count[2:6]),
            audgen_silenced.eq(audgen_lrck_count[6]),
            audgen_lrck_internal.eq(audgen_lrck_count[2:7]) # BCCCC (audgen_channel_internal + audgen_silenced)
        ]

        with m.If(audgen_slck_update): # Update late as possible (could do so as early as implied falling edge...)
            m.d.comb += audgen_bit_update_stb.eq(1)

            with m.If(audgen_lrck_internal == 23): # Audio logic halfway through "silenced" period (FIXME could move forward or back-- Analogue sample code did this on lrck falling edge)
                m.d.comb += audgen_word_update_stb.eq(1)

        # Module output
        m.d.comb += [
            self.audio_mclk.eq(audgen_mclk),     # Master clock-- 4x the serial clock or 256x select
            self.audio_dac.eq(audgen_dac),       # Output
            self.audio_lrck.eq(audgen_lrck),     # Word select (channel)
        ]

        return m

    # "App logic" function to be overloaded by subclass
    def app_elaborate(self, platform, m,
            video_pixel_stb, video_hsync_stb, video_vsync_stb, video_x_count, video_y_count, video_active, video_rgb_out,
            audio_silenced, audio_channel_select, audio_channel_internal, audio_bit_update_stb, audio_word_update_stb, audio_dac_out):
        # Black screen, silence

        m.d.comb += [
            video_rgb_out.eq(0),
            audio_dac_out.eq(0)
        ]
