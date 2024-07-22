# "Business logic" / Game logic / User logic

from amaranth import *
from amaranth.lib import wiring, data
from amaranth.lib.wiring import In, Out
import enum

from .resolution import *
from .toplevel import Toplevel


class RenderState(enum.Enum):
    TOP    = 0
    LEFT   = 1
    BOTTOM = 2
    RIGHT  = 3
    CURRENT = 4
    NEXT = 5

class RenderMode(enum.Enum):
    PLAIN = 0
    VERT = 1
    HORIZ = 2
    CHECKER = 3

ANIMATION_COUNTER_SIZE = 64
ANIMATION_COUNTER_MAX = 63
ROTATE_COUNTER_MAX = 3


class AppToplevel(Toplevel):
    def app_elaborate(self, platform, m,
            video_pixel_stb, video_hsync_stb, video_vsync_stb, video_x_count, video_y_count, video_active, video_rgb_out,
            audio_silenced, audio_channel_select, audio_channel_internal, audio_bit_update_stb, audio_word_update_stb, audio_dac_out):
        # App: Test pattern
        # 3 effects:
        #     * Outer sides are red, green, yellow and blue. Every 4 "beats" they grow narrower, until on the 4th beat they are 1 pixel wide.
        #     * Every "beat" the background alternates (vertical wipe) between magenta, vertical stripes, horizontal stripes, and checkerboard (stripes and checkers alternate black and white)
        #     * Every "beat" a square wave C note rises, on beat 4 it rises one octave higher.

        # Setup

        animation_counter = Signal(6) # 0..63 counter
        rotate1_counter   = Signal(2) # 0..3 counter
        rotate2_counter   = Signal(2) # 0..3 counter

        # Partial results for colors
        render_state = Signal(Shape.cast(RenderState))
        current_color_id = Signal(Shape.cast(RenderMode))
        next_color_id = Signal(Shape.cast(RenderMode))
        flash_color = Signal(24)
        current_flash_on = Signal(1)
        next_flash_on = Signal(1)
        rotate2_counter_anti = Signal(2)

        m.d.comb += rotate2_counter_anti.eq(ROTATE_COUNTER_MAX - rotate2_counter)

        def rgb(r,g,b):
            return [video_rgb_out.r.eq(r), video_rgb_out.g.eq(g), video_rgb_out.b.eq(b)]

        val = Const(VID_V_BPORCH, video_y_count.shape())
        with m.If((video_y_count >= val) & (video_y_count <= val + rotate2_counter_anti)):   # Top row red
            m.d.comb += render_state.eq(RenderState.TOP)

        val = Const(VID_V_ACTIVE + VID_V_BPORCH - 1, video_y_count.shape())
        with m.Elif((video_y_count <= val) & (video_y_count >= val - rotate2_counter_anti)): # Bottom row yellow
            m.d.comb += render_state.eq(RenderState.BOTTOM)

        val = Const(VID_H_BPORCH, video_x_count.shape())
        with m.Elif((video_x_count >= val) & (video_x_count <= val + rotate2_counter_anti)): # Left column green
            m.d.comb += render_state.eq(RenderState.LEFT)

        val = Const(VID_H_ACTIVE + VID_H_BPORCH - 1, video_x_count.shape())
        with m.Elif((video_x_count <= val) & (video_x_count >= val - rotate2_counter_anti)): # Right column blue
            m.d.comb += render_state.eq(RenderState.RIGHT)

        with m.Elif(video_y_count - VID_V_BPORCH > animation_counter * (VID_V_ACTIVE // ANIMATION_COUNTER_SIZE)):
            m.d.comb += render_state.eq(RenderState.NEXT)
        with m.Else(): # Remaining pixels, alternate black
            m.d.comb += render_state.eq(RenderState.CURRENT)

        m.d.comb += [
            current_color_id.eq(rotate1_counter+1),
            next_color_id.eq(rotate1_counter)
        ]

        with m.If(rotate1_counter[0] ^ rotate2_counter[0]):
            m.d.comb += flash_color.eq(0x0)
        with m.Else():
            m.d.comb += flash_color.eq(0xFFFFFF)

        for [flash_on, id] in [[current_flash_on, current_color_id], [next_flash_on, next_color_id]]:
            with m.Switch(id):
                with m.Case(RenderMode.PLAIN):
                    m.d.comb += flash_on.eq(0)
                with m.Case(RenderMode.VERT):
                    m.d.comb += flash_on.eq(video_x_count[0])
                with m.Case(RenderMode.HORIZ):
                    m.d.comb += flash_on.eq(video_y_count[0])
                with m.Case(RenderMode.CHECKER):
                    m.d.comb += flash_on.eq(video_x_count[0] ^ video_y_count[0])

        # Animation

        # New frame logic
        with m.If(video_vsync_stb):
            m.d.sync += animation_counter.eq(animation_counter + 1)

            with m.If(animation_counter == ANIMATION_COUNTER_MAX):
                m.d.sync += rotate1_counter.eq(rotate1_counter + 1)
                with m.If(rotate1_counter == ROTATE_COUNTER_MAX):
                    m.d.sync += rotate2_counter.eq(rotate2_counter + 1)

        # Draw logic
        with m.If(video_pixel_stb):            # inactive screen areas must be black
            m.d.sync += [
                video_rgb_out.eq(0)
            ]

            # Color selection for live pixels
            with m.If(video_active):
                with m.Switch(render_state):
                    with m.Case(RenderState.TOP): # Red
                        m.d.sync += rgb(0xFF, 0, 0)
                    with m.Case(RenderState.BOTTOM): # Yellow
                        m.d.sync += rgb(0xFF, 0xFF, 0x80)
                    with m.Case(RenderState.LEFT): # Green
                        m.d.sync += rgb(0, 0xFF, 0)
                    with m.Case(RenderState.RIGHT): # Blue
                        m.d.sync += rgb(0, 0, 0xFF)
                    for [case, flash_on, invert] in [[RenderState.CURRENT, current_flash_on, 0x0], [RenderState.NEXT, next_flash_on, 0xFFFFFF]]:
                        with m.Case(case):
                            with m.If(flash_on): # Remaining pixels, alternate black
                                m.d.sync += video_rgb_out.eq(flash_color^invert)
                            with m.Else():
                                m.d.sync += rgb(0xa0, 0x00, 0x80) # Magenta

        # Audio

        A440_OFFSET = 600
        SIGNAL_DOWNBITS = 3
        audgen_osc_saw = Signal(16)
        audgen_osc_out = Signal(16)

        with m.If(audio_bit_update_stb):
            # Convert above state logic to a waveform—- alternate 0b0000011111111111 and 0b1111100000000000 words
            m.d.sync += [
                audio_dac_out.eq( audgen_osc_out[15] ),
                audgen_osc_out.eq( audgen_osc_out << 1 )
            ]

        with m.If(audio_word_update_stb):
            m.d.sync += audgen_osc_out.eq(audgen_osc_saw >> SIGNAL_DOWNBITS)
            with m.If(~audio_channel_select):
                m.d.sync += audgen_osc_saw.eq(audgen_osc_saw + 1)

def simulate():
    from amaranth.sim import Simulator

    sim = Simulator(Toplevel())
    sim.add_clock(1/74.25e6)
    with sim.write_vcd("dump.vcd"):
        sim.run_until(10e-3, run_passive=True)


def capture_frame():
    import soundfile
    from amaranth.sim import Simulator

    top = Toplevel()
    def bench():
        written = 0
        while True:
            cols = []
            while not (yield top.video_hs): yield
            while not ((yield top.video_vs) or (yield top.video_de)): yield
            if (yield top.video_vs):
                break
            while True:
                while (yield top.video_rgb_clk90): yield
                while not (yield top.video_rgb_clk90): yield
                # at posedge of clk90
                if (yield top.video_de):
                    cols.append((yield top.video_rgb.r))
                    cols.append((yield top.video_rgb.g))
                    cols.append((yield top.video_rgb.b))
                else:
                    break
            print(f"row {len(rows)}: {len(cols) // 3} cols")
            rows.append(cols)
            with open("frame.png", "wb") as file:
                png.Writer(len(rows[0]) // 3, len(rows), greyscale=False).write(file, rows)
        print(f"{len(rows)} rows")

    sim = Simulator(top)
    sim.add_clock(1/74.25e6)
    sim.add_sync_process(bench)
    sim.run()


def capture_wav():
    import numpy as np
    import soundfile as sf
    from amaranth.sim import Simulator

    FILE_NAME = "log.wav"
    SAMPLE_RATE = 48000
    CHUNK_SIZE = SAMPLE_RATE//200
    SHRT_MAX = 32767 # No python library source for this?
    USHRT_CONVERT = 1<<16

    top = Toplevel()
    def bench():
        written = 0
        last_printed = 0

        while not (yield top.audio_mclk): yield

        while True:
            frames = []

            # Do i2s from the speaker end
            for _ in range(CHUNK_SIZE):
                frame = []
                for channel in range(2):
                    sample = 0

                    for _ in range(16):
                        sample <<= 1
                        sample |= yield top.audio_dac
                        lrck = yield top.audio_lrck
                        assert lrck == channel, f"Unexpected lrck [channel select] value (wanted {channel}, got {lrck})"
                        for _ in range(4): # Serial step
                            while (yield top.audio_mclk): yield
                            while not (yield top.audio_mclk): yield

                    if sample > SHRT_MAX: # Reinterpret unsigned as signed
                        sample -= USHRT_CONVERT
                    frame.append(sample)

                    for _ in range(16): # Blank space
                        for _ in range(4): # Serial step
                            while (yield top.audio_mclk): yield
                            while not (yield top.audio_mclk): yield
                frames.append(frame)

            # If this is first byte open write to truncate, otherwise open readwrite...
            with sf.SoundFile(FILE_NAME, mode = 'w', samplerate=SAMPLE_RATE, channels=2, subtype='PCM_16') \
                    if written == 0 \
                    else sf.SoundFile(FILE_NAME, mode = 'r+') \
                    as outfile:
                if written > 0: # ... then seek to end to append
                    outfile.seek(0,sf.SEEK_END)
                outfile.write(np.array(frames, dtype=np.int16))

            written += CHUNK_SIZE
            if written >= last_printed+SAMPLE_RATE:
                print(f"{written//SAMPLE_RATE} seconds written")
                last_printed = written

    sim = Simulator(top)
    sim.add_clock(1/74.25e6)
    sim.add_sync_process(bench)
    sim.run()


def generate():
    from pathlib import Path
    from amaranth.back import verilog
    from .platform import IntelPlatform

    toplevel = Toplevel()
    with open(Path(__file__).parent.parent.parent / "core" / "amaranth_core.v", "w") as f:
        f.write(verilog.convert(toplevel, platform=IntelPlatform, name="amaranth_core", strip_internal_attrs=True))
