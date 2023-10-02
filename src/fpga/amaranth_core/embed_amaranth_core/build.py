# Interface with outside world

from amaranth import *
from amaranth.lib import wiring, data
from amaranth.lib.wiring import In, Out
import enum

from .app_toplevel import AppToplevel


def simulate():
    from amaranth.sim import Simulator

    sim = Simulator(AppToplevel())
    sim.add_clock(1/74.25e6)
    with sim.write_vcd("dump.vcd"):
        sim.run_until(10e-3, run_passive=True)


def capture_frame():
    import png
    from amaranth.sim import Simulator

    top = AppToplevel()
    def bench():
        written = 0
        for _frame in range(2):
            frame = _frame + 1

            rows = []
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
                print(f"frame {frame}, row {len(rows)}: {len(cols) // 3} cols")
                rows.append(cols)
                with open(f"frame{frame}.png", "wb") as file:
                    png.Writer(len(rows[0]) // 3, len(rows), greyscale=False).write(file, rows)
            print(f"frame {frame}, {len(rows)} rows")

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

    top = AppToplevel()
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

    toplevel = AppToplevel()
    with open(Path(__file__).parent.parent.parent / "core" / "amaranth_core.v", "w") as f:
        f.write(verilog.convert(toplevel, platform=IntelPlatform, name="amaranth_core", strip_internal_attrs=True))
