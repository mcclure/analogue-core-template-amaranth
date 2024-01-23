# "Business logic" / Game logic / App logic

from amaranth import *
from amaranth.utils import bits_for
from amaranth.lib import wiring, data
from amaranth.lib.wiring import In, Out
import enum

from .resolution import *
from .toplevel import Toplevel, ColorScheme


DEBUG_NO_OPENING_PAUSE = False
DEBUG_NO_CONTROLS = False

AUDIO_DIVISOR_BITS = 2
AUDIO_COARSE = False # If true, only transition between audio "lines" at screen boundary.
SPEED_LEVELS = 8
SPEED_INITIAL = 1 # 0 index

class ScribbleKind(enum.IntEnum):
    SINGLE_BLACK = 0
    SINGLE_WHITE = 1
    MANY_BLACK = 2
    MANY_WHITE = 3

AUTO_DEFAULT = 0

# app_elaborate is responsible for setting values of:
#     - audio_dac_out (always)
#     - video_rgb_out (when video_active)
class AppToplevel(Toplevel):
    def app_elaborate(self, platform, m,
            video_pixel_stb, video_hsync_stb, video_vsync_stb, video_x_count, video_y_count,  video_x_active, video_y_active, video_active, video_docked, video_rgb_out,
            audio_silenced, audio_channel_select, audio_channel_internal, audio_bit_update_stb, audio_word_update_stb, audio_dac_out):
        # App: Rule 30?

        # Setup

        # CA mechanics
        # Note: In current design, video_x_active is disregarded and VID_H_ACTIVE is read directly, on assumption VID_H_ACTIVE constant.
        # This is due to this commit's midpoint between the original all-constants size architecture and the eventual mutable-per-frame one.
        line_reset_value = (1 << (VID_H_ACTIVE//2)) # Initial state value of first line
        topline_state = Signal(VID_H_ACTIVE, reset=line_reset_value)
        active_state = Signal(VID_H_ACTIVE, reset=line_reset_value)
        audgen_state = Signal(VID_H_ACTIVE, reset=line_reset_value)
        if AUDIO_COARSE:
            audgen_state_next = Signal(VID_H_ACTIVE, reset=line_reset_value)
            audgen_state_remain = Signal(bits_for(VID_H_ACTIVE-1), reset=VID_H_ACTIVE-1)
        need_topline_copy = Signal(1) # Fires at variable time-- copy topline to active
        need_topline_backcopy = Signal(1) # Fires 1 cycle after first-row hsync-- copy active to topline

        # CA control mechanics -- on NO_OPENING_PAUSE start frozen then unfreeze immediately
        frame_frozen = Signal(1, reset=1)

        # Initial pause
        opening_countdown_timer_reset_value = ((1<<6)-1)
        opening_countdown_timer = Signal(6, reset=0 if DEBUG_NO_OPENING_PAUSE else opening_countdown_timer_reset_value)
        opening_wants_frozen = Signal(1)
        opening_countdown_timer_late_reset = Signal(1)

        # Elective pause
        pause_key_wants_frozen = Signal(1)
        need_frozen_exception = Signal(1)

        # Speed
        speed_counter = Signal(SPEED_LEVELS)
        speed_counter_mask = Signal(SPEED_LEVELS, reset=((1<<SPEED_INITIAL) - 1))

        # Automaton
        automata_rule_array = [self.interact_rule0, self.interact_rule1, self.interact_rule2, self.interact_rule3]
        automata_next = Signal(2, reset=AUTO_DEFAULT)
        automata_table = Signal(8)
        active_state_zero_last = Signal(1, reset=1)

        # Scribble
        scribble_hold = [Signal(1) for _ in range(4)]
        scribble_single = [Signal(1) for _ in range(4)]
        need_scribble = Signal(1)

        # Audio mechanics
        audio_divide_counter = Signal(AUDIO_DIVISOR_BITS, reset = AUDIO_DIVISOR_BITS and ((1<<AUDIO_DIVISOR_BITS)-1))
        audio_divide_stb = Signal(1)

        line_reset_value = None # Take me unto thine arms, GC

        # Controls

        if DEBUG_NO_CONTROLS:
            m.d.comb += [
                pause_key_wants_frozen.eq(0),
                need_frozen_exception.eq(0),
                need_topline_copy.eq(0) # May be overridden later
            ]
        else:
            cont1_key_last = Signal(self.cont1_key.shape())
            m.d.sync += cont1_key_last.eq(self.cont1_key) # TODO: Debounce

            select = Signal(1) # Modifier
            m.d.comb += select.eq(self.cont1_key[14])

            with m.If(self.cont1_key[15] & (~cont1_key_last[15])): # "Start"
                with m.If(select): # "Start + Select"
                    with m.If(pause_key_wants_frozen): # While paused, did select+start
                        m.d.sync += need_frozen_exception.eq(1) # Perform one step
                    with m.Else(): # While unpaused, did select+start
                        m.d.sync += [ # Perform one step then freeze for 64 frames
                            opening_countdown_timer_late_reset.eq(1),
                            need_frozen_exception.eq(1)
                        ]
                with m.Else():
                    m.d.sync += pause_key_wants_frozen.eq(~pause_key_wants_frozen)

            l_press = Signal(1)
            r_press = Signal(1)
            m.d.comb += [
                l_press.eq(self.cont1_key[8] & ~cont1_key_last[8]),
                r_press.eq(self.cont1_key[9] & ~cont1_key_last[9])
            ]

            with m.If(l_press & r_press): # If the user somehow does this, do nothing
                pass
            with m.Elif(l_press):
                m.d.sync += [
                    speed_counter_mask.eq(speed_counter_mask.shift_left(1)),
                    speed_counter_mask[0].eq(1)
                ]
            with m.Elif(r_press):
                m.d.sync += [
                    speed_counter_mask.eq(speed_counter_mask.shift_right(1))
                ]

            for idx, bit in enumerate([7,6,5,4]): # Y, X, B, A
                with m.If(self.cont1_key[bit] & ~cont1_key_last[bit]):
                    with m.If(select):
                        m.d.sync += scribble_single[idx].eq(1)
                    with m.Else():
                        m.d.sync += scribble_hold[idx].eq(1)    
                with m.Elif(cont1_key_last[bit] & ~self.cont1_key[bit]):
                    m.d.sync += scribble_hold[idx].eq(0)
                scribble_hold

            d_hold = []
            d_press = []
            d_release = []

            for bit in [0, 2, 3, 1]: # Up, Left, Right, Down
                hold = Signal(1)
                m.d.comb += hold.eq(self.cont1_key[bit])
                d_hold.append(hold)

                press = Signal(1)
                m.d.comb += press.eq(hold & ~cont1_key_last[bit])
                d_press.append(press)

                release = Signal(1)
                m.d.comb += release.eq(~hold & cont1_key_last[bit])
                d_release.append(release)

            with m.If(0):
                pass
            for idx,press in enumerate(d_press):
                with m.Elif(press):
                    m.d.sync += [
                        automata_next.eq(idx)
                    ]
            # TODO: Also release behavior


        # Partial results for colors

        flash_color = Signal(self.video_rgb.shape())

        # flash_color is our 1 bit video output (black/white)
        with m.If(active_state[0]):
            with m.If(active_state_zero_last): # Double black
                m.d.comb += flash_color.as_value().eq(0x000000)
            with m.Else():                     # Leading black
                with m.Switch(self.interact_color):
                    with m.Case(ColorScheme.BLACK):
                        m.d.comb += flash_color.eq(0x000000)
                    with m.Case(ColorScheme.RED):   # Pink
                        m.d.comb += [
                            flash_color.r.eq(247),
                            flash_color.g.eq(190),
                            flash_color.b.eq(24),
                        ]
                    with m.Case(ColorScheme.GREEN): # Purple
                        m.d.comb += [
                            flash_color.r.eq(255),
                            flash_color.g.eq(190),
                            flash_color.b.eq(255),
                        ]
                    with m.Case(ColorScheme.BLUE):  # Blue
                        m.d.comb += [
                            flash_color.r.eq(8),
                            flash_color.g.eq(0),
                            flash_color.b.eq(132),
                        ]
        with m.Else():
            with m.If(active_state_zero_last): # Trailing white
                with m.Switch(self.interact_color):
                    with m.Case(ColorScheme.RED): # Orange
                        m.d.comb += [
                            flash_color.r.eq(255),
                            flash_color.g.eq(207),
                            flash_color.b.eq(255),
                        ]
                    with m.Case(ColorScheme.GREEN): # Green
                        m.d.comb += [
                            flash_color.r.eq(132),
                            flash_color.g.eq(251),
                            flash_color.b.eq(24),
                        ]
                    with m.Default():
                        m.d.comb += flash_color.as_value().eq(0xFFFFFF)
            with m.Else():                     # Double white
                m.d.comb += flash_color.as_value().eq(0xFFFFFF)


        # Animation

        # Draw logic

        m.d.comb += opening_wants_frozen.eq(opening_countdown_timer != 0)

        m.d.sync += [
            need_topline_backcopy.eq(0)
        ]
        with m.If(video_pixel_stb): # Action of drawing
            # Color selection for live pixels -- toplevel handles other pixels
            with m.If(video_active):
                m.d.sync += [
                    video_rgb_out.eq(flash_color),
                    active_state.eq(active_state.rotate_right(1)), # We are always displaying the least significant bit
                    active_state_zero_last.eq(active_state[0])
                ]

            # Row finished
            with m.If(video_hsync_stb & (video_y_count >= VID_V_BPORCH) & (video_y_count < video_y_active + VID_V_BPORCH - 1)):
                # Perform rule 30
                for i in range(VID_H_ACTIVE): # For each col
                    # Calculate indices
                    pre = (i+(VID_H_ACTIVE-1))%VID_H_ACTIVE
                    nex = (i+1)%VID_H_ACTIVE
                    # Output signal
                    at = active_state[i]
                    # Input signal
                    cat = Cat(Cat(active_state[pre], at), active_state[nex])
                    # Cellular automaton definition
                    with m.Switch(cat):
                        for idx in range(8): # Case applies each possible neighbor bit combination to a bit in the register
                            with m.Case(idx):
                                m.d.sync += at.eq(automata_table[idx])

                # 1 cycle after first row is done performing CA, make that the new topline
                # (Unless we are in first second and frozen)
                with m.If(
                        (video_y_count == VID_V_BPORCH) & 
                        (~frame_frozen)):
                    m.d.sync += need_topline_backcopy.eq(1)

            # Row finished
            with m.If(video_hsync_stb):
                m.d.sync += active_state_zero_last.eq(1) # Note: this could have been done one stb earlier

            # Screen finished
            with m.If(video_vsync_stb):
                # Is the next frame paused?
                m.d.sync += [
                    speed_counter.eq(speed_counter+1)
                ]

                # Only consider this a true frame rollover if speed counter matches
                with m.If((speed_counter & speed_counter_mask)==0): # Halve speed for each bit of mask 
                    m.d.sync += \
                        frame_frozen.eq(opening_wants_frozen | pause_key_wants_frozen)
                with m.Else():
                    m.d.sync += frame_frozen.eq(1)
                with m.If(need_frozen_exception): # Note this means you can step more quickly than the speed counter
                    m.d.sync += frame_frozen.eq(0)

                if DEBUG_NO_CONTROLS:
                    m.d.comb += need_topline_copy.eq(1)
                else:
                    # Reset frozen exception
                    with m.If(need_frozen_exception):
                        m.d.sync += need_frozen_exception.eq(0)

                    # Activate scribble
                    for idx in ScribbleKind:
                        # TRIGGER DOWN SCRIBBLE NEXT FRAME
                        scribble_now = Signal(1)
                        m.d.comb += scribble_now.eq(0)
                        with m.If(scribble_single[idx]):
                            m.d.comb += scribble_now.eq(1)
                            m.d.sync += scribble_single[idx].eq(0)
                        with m.If(scribble_hold[idx]):
                            m.d.comb += scribble_now.eq(1)
                        with m.If(scribble_now):
                            many = 5
                            match idx:
                                case ScribbleKind.SINGLE_BLACK:
                                    m.d.sync += topline_state[VID_H_ACTIVE//2].eq(1)
                                case ScribbleKind.SINGLE_WHITE:
                                    m.d.sync += topline_state[VID_H_ACTIVE//2+1].eq(0)
                                case ScribbleKind.MANY_BLACK:
                                    m.d.sync += [
                                        topline_state[off*VID_H_ACTIVE//many+off].eq(1)
                                        for off in range(many) 
                                    ]
                                case ScribbleKind.MANY_WHITE:
                                    m.d.sync += [
                                        topline_state[off*VID_H_ACTIVE//many+off*2+1].eq(0)
                                        for off in range(many) 
                                    ]

                    # Do this every time, even if no button pressed, because Interact may have changed
                    with m.Switch(automata_next):
                        for idx in range(4):
                            with m.Case(idx):
                                m.d.sync += [
                                    automata_table.eq(automata_rule_array[idx])
                                ]

                    m.d.sync += need_topline_copy.eq(1)

                # Service opening timer
                with m.If(opening_countdown_timer != 0):
                    m.d.sync += opening_countdown_timer.eq(opening_countdown_timer - 1)

                # Set audio state and new active state from most recent topline state
                with m.If(~frame_frozen): # Notice frozen for *just-finished* frame
                    m.d.sync += [
                        (audgen_state_next if AUDIO_COARSE else audgen_state)
                            .eq(topline_state),
                    ]

        with m.If(need_topline_copy): # Do last because can be driven multiple ways
            m.d.sync += active_state.eq(topline_state) # Reset line renderer to frame

            if not DEBUG_NO_CONTROLS:
                m.d.sync += need_topline_copy.eq(0)

        with m.If(need_topline_backcopy): # Do last to override
            m.d.sync += [
                topline_state.eq(active_state),
                need_topline_backcopy.eq(0)
            ]

        with m.If(opening_countdown_timer_late_reset): # Do last to override
            m.d.sync += [
                opening_countdown_timer.eq(opening_countdown_timer_reset_value),
                opening_countdown_timer_late_reset.eq(0)
            ]

        # Audio

        audio_high = Signal(1)       # High when square wave high (1 bit dac effectively)
        audio_output_word_bit = Signal(1) # As audio_channel_internal increments scrolls through bits 0b0000011111111111, MSB first

        m.d.comb += audio_output_word_bit.eq(audio_channel_internal <= 5) # 1 bit dac state

        m.d.comb += audio_divide_stb.eq(audio_divide_counter == 0)
        m.d.comb += audio_high.eq( audgen_state[0] )  # Audio play is always lowest bit of audio state

        with m.If(audio_bit_update_stb):
            # Convert above state logic to a waveform—- alternate 0b0000011111111111 and 0b1111100000000000 words
            m.d.sync += audio_dac_out.eq( Mux(audio_silenced, 0, audio_output_word_bit ^ audio_high) )

        with m.If(audio_word_update_stb):
            # Audio generation app logic
            with m.If(~(video_pixel_stb & video_vsync_stb)): # Don't collide with end-of-screen copy
                with m.If(audio_divide_stb):
                    m.d.sync += audgen_state.eq( audgen_state.rotate_right(1) ) # After playing a bit, move to the next bit
                    if AUDIO_COARSE:
                        with m.If(audgen_state_remain == 0):
                            m.d.sync += [
                                audgen_state_remain.eq(audgen_state_remain.reset),
                                audgen_state.eq(audgen_state_next)
                            ]
                        with m.Else():
                            m.d.sync += audgen_state_remain.eq(audgen_state_remain-1)

                if AUDIO_DIVISOR_BITS>0:
                    m.d.sync += audio_divide_counter.eq( audio_divide_counter+1 )
