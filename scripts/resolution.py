# Resolution calculator. Python 3
# Takes X pixel, Y pixel and (optional, assumes 60) hz framerate as arguments
# Then takes 1 line of interactive input
# Written by andi mcc with help from agg23 and whitequark
# Covered by BSD0 license in src/fpga/amaranth_core/LICENSE.txt

# Usage: python resolution.py WIDTH HEIGHT
# Then wait for prompt

FRAMERATE_HZ_DEFAULT = 60
MHZ = 1_000_000

# Range Pocket scaler can display, from docs https://www.analogue.co/developer/docs/bus-communication#video
PIXEL_MHZ_MIN = 1
PIXEL_MHZ_MAX = 50
FRAMERATE_HZ_MIN = 47
FRAMERATE_HZ_MAX = 61
RES_X_MIN = 16
RES_Y_MIN = 16
RES_X_MAX = 800
RES_Y_MAX = 720

# Speed of source clock. In Amaranth, we use the default clock for this.
REFERENCE_MHZ = 74.25

# Minimum combined size for porches
PORCH_MIN = 8

# Assume neither axis should exceed this with porch size. 100% arbitrary
PORCHED_MAX = 1024

import sys
import math
import fractions

# Import args
# Todo get click in here
_, display_x, display_y, *hz = sys.argv
display_x = int(display_x)
display_y = int(display_y)
display_hz = float(hz[0]) if hz else 60

assert display_x >= RES_X_MIN and display_y>=RES_Y_MIN, f"Minimum resolution {RES_X_MIN}x{RES_Y_MIN}"
assert display_x <= RES_X_MAX and display_y<=RES_Y_MAX, f"Maximum resolution {RES_X_MAX}x{RES_Y_MAX}"
assert display_hz >= FRAMERATE_HZ_MIN, "Minimum framerate {FRAMERATE_HZ_MIN}hz"
assert display_hz <= FRAMERATE_HZ_MAX, "Maximum framerate {FRAMERATE_HZ_MAX}hz"

# Organize options in a duct-taped priority queue
QUEUE_MAX = 10
found_queue = []

# Brute force
for candidate_x in range(display_x + PORCH_MIN, PORCHED_MAX):
	for candidate_y in range(display_y + PORCH_MIN, PORCHED_MAX):
		for candidate_divisor in range(4, 64, 4):
			clock_hz = REFERENCE_MHZ * MHZ / (candidate_divisor*candidate_y*candidate_x)
			if clock_hz < FRAMERATE_HZ_MIN or clock_hz > FRAMERATE_HZ_MAX:
				continue
			clock_error_hz = math.fabs(display_hz - clock_hz)

			underflow = len(found_queue) < QUEUE_MAX
			if underflow or found_queue[QUEUE_MAX-1][0] < clock_error_hz:
				candidate = (clock_error_hz, clock_hz, candidate_x, candidate_y, candidate_divisor)
				found_queue.append(candidate)
				found_queue.sort(key=lambda x:x[0])
				if not underflow:
					found_queue.pop()

# Results
for found_idx, found in enumerate(found_queue):
	(_, hz, x, y, divisor) = found
	print(f"({found_idx}) Divisor {divisor} ({REFERENCE_MHZ/divisor:0.3f} mhz), {x}x{y}, {hz:0.3f} fps")

picked = int(input("\nSelect preferred configuration: "))

(_, hz, x, y, divisor) = found_queue[picked]

porch_x = (x-display_x) // 2
porch_y = (y-display_y) // 2

aspect = fractions.Fraction(display_x, display_y)

print(f"""
# Top of toplevel.py

# ~{REFERENCE_MHZ/divisor:0.3f} mhz clock; {hz:0.3f} fps
VID_DIV_RATIO = {divisor}
VID_H_BPORCH = {porch_x}
VID_H_ACTIVE = {display_x}
VID_H_TOTAL  = {x}
VID_V_BPORCH = {porch_y}
VID_V_ACTIVE = {display_y}
VID_V_TOTAL  = {y}

# video.json

{{
    "video": {{
        "magic": "APF_VER_1",
        "scaler_modes": [
            {{
                "width": {display_x},
                "height": {display_y},
                "aspect_w": {aspect.numerator},
                "aspect_h": {aspect.denominator},
                "rotation": 0,
                "mirror": 0
            }}
        ]
    }}
}}

# Remember also to edit core_constraints.sdc: -divide_by {divisor}
# And toplevel.py: video_x_count, video_y_count, video_y_height must have enough bits
""")