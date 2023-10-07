# "Business logic" / Game logic / User logic

from amaranth import *
from amaranth.lib import wiring, data
from amaranth.lib.wiring import In, Out
import enum

from .resolution import *
from .toplevel import Toplevel

class DpadRegion(enum.Enum):
    TOP    = 0
    LEFT   = 1
    BOTTOM = 2
    RIGHT  = 3

class CompassRegion(enum.Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3

class AppToplevel(Toplevel):
    def app_elaborate(self, platform, m,
            video_pixel_stb, video_hsync_stb, video_vsync_stb, video_x_count, video_y_count, video_active, video_rgb_out,
            audio_silenced, audio_channel_select, audio_channel_internal, audio_bit_update_stb, audio_word_update_stb, audio_dac_out):
        # App: Controller test

        red_region = Signal(Shape.cast(DpadRegion))
        blue_region = Signal(Shape.cast(DpadRegion))
        green_region = Signal(Shape.cast(CompassRegion))

        cont1_key_latch = Signal(self.cont1_key.shape())

        # Intermediate values: "Where are we?"

        # Split the screen into quadrants four ways. For example
        # Coords         bottom_left_diag    top_left_diag    left_half    top_half
        # 0,0 1,0 2,0    O O O               X X O            X O O        X X X
        # 0,1 1,1 2,1    X O O               X O O            X O O        O O O
        # 0,2 1,2 2,2    X X O               O O O            X O O        O O O
        bottom_left_diag = Signal(1)
        top_left_diag = Signal(1)
        left_half = Signal(1)
        top_half = Signal(1)
        m.d.comb += [
            bottom_left_diag.eq(video_x_count < video_y_count),
            top_left_diag.eq(video_x_count < VID_V_ACTIVE-1-video_y_count),
            left_half.eq(video_x_count < VID_H_ACTIVE//2),
            top_half.eq(video_y_count < VID_V_ACTIVE//2)
        ]

        # Ready pixel

        with m.If(video_pixel_stb):
            # Diamonds
            with m.If(bottom_left_diag):
                with m.If(top_left_diag):
                    m.d.sync += [
                        red_region.eq(DpadRegion.LEFT),
                        blue_region.eq(DpadRegion.LEFT)
                    ]
                with m.Else():
                    m.d.sync += [
                        red_region.eq(DpadRegion.BOTTOM),
                        blue_region.eq(DpadRegion.BOTTOM)
                    ]
            with m.Else(): # Top or right
                with m.If(top_left_diag):
                    m.d.sync += [
                        red_region.eq(DpadRegion.TOP),
                        blue_region.eq(DpadRegion.TOP)
                    ]
                with m.Else():
                    m.d.sync += [
                        red_region.eq(DpadRegion.RIGHT),
                        blue_region.eq(DpadRegion.RIGHT)
                    ]
            # Quadrants
            with m.If(left_half):
                with m.If(top_half):
                    m.d.sync += [
                        red_region.eq(CompassRegion.TOP_LEFT)
                    ]
                with m.Else():
                    m.d.sync += [
                        red_region.eq(CompassRegion.BOTTOM_LEFT)
                    ]
            with m.Else(): # Right half
                with m.If(top_half):
                    m.d.sync += [
                        red_region.eq(CompassRegion.TOP_RIGHT)
                    ]
                with m.Else():
                    m.d.sync += [
                        red_region.eq(CompassRegion.BOTTOM_RIGHT)
                    ]


        # New frame logic
        with m.If(video_vsync_stb):
            m.d.sync += cont1_key_latch.eq(self.cont1_key)

        # Draw logic
        with m.If(video_pixel_stb):            # inactive screen areas must be black
            m.d.sync += [
                video_rgb_out.eq(0)
            ]

            # Color selection for live pixels -- see https://www.analogue.co/developer/docs/bus-communication#pad
            with m.If(video_active):
                with m.Switch(red_region): # D-pad
                    with m.Case(DpadRegion.TOP):
                        m.d.sync += video_rgb_out.r.eq(cont1_key_latch[0])
                    with m.Case(DpadRegion.BOTTOM):
                        m.d.sync += video_rgb_out.r.eq(cont1_key_latch[1])
                    with m.Case(DpadRegion.LEFT):
                        m.d.sync += video_rgb_out.r.eq(cont1_key_latch[2])
                    with m.Case(DpadRegion.RIGHT):
                        m.d.sync += video_rgb_out.r.eq(cont1_key_latch[3])
                with m.Switch(blue_region): # ABXY
                    with m.Case(DpadRegion.RIGHT):
                        m.d.sync += video_rgb_out.b.eq(cont1_key_latch[4])
                    with m.Case(DpadRegion.BOTTOM):
                        m.d.sync += video_rgb_out.b.eq(cont1_key_latch[5])
                    with m.Case(DpadRegion.TOP):
                        m.d.sync += video_rgb_out.b.eq(cont1_key_latch[6])
                    with m.Case(DpadRegion.LEFT):
                        m.d.sync += video_rgb_out.b.eq(cont1_key_latch[7])
                with m.Switch(green_region):
                    with m.Case(CompassRegion.TOP_LEFT): # Triggers, select, start
                        m.d.sync += video_rgb_out.g.eq(cont1_key_latch[8])
                    with m.Case(CompassRegion.TOP_RIGHT):
                        m.d.sync += video_rgb_out.g.eq(cont1_key_latch[9])
                    with m.Case(CompassRegion.BOTTOM_LEFT):
                        m.d.sync += video_rgb_out.g.eq(cont1_key_latch[14])
                    with m.Case(CompassRegion.BOTTOM_RIGHT):
                        m.d.sync += video_rgb_out.g.eq(cont1_key_latch[15])

        # Audio -- Silent

        m.d.comb += audio_dac_out.eq( 0 )
