# Amaranth / TT prototyping.

This is a WIP repo.

On my system (Ubuntu), these are the build steps, although they will differ on yours:

```
(cd src/fpga/amaranth_core/ && python3 -m pdm generate) && (cd src/fpga && ~/usr/intelFPGA_lite/22.1std/quartus/bin/quartus_sh --flow compile ap_core) && (rm -f ../quartus/reverse/bitstream.rbf_r && ../quartus/reverse/a.out ./src/fpga/output_files/ap_core.rbf ../quartus/reverse/bitstream.rbf_r) && (cd ../quartus/reverse && cp bitstream.rbf_r "/media/mcc/3930-6663/Cores/test.andi amaranth/bitstream.rbf_r") && (cp video.json interact.json "/media/mcc/3930-6663/Cores/test.andi amaranth/") && sync
```

Or in Windows 10 (WSL)

```
(cd src/fpga/amaranth_core/ && python.exe -m pdm generate) && (cd src/fpga && /mnt/d/intelFPGA_lite/22.1std/quartus/bin64/quartus_sh.exe --flow compile ap_core) && (rm -f ../quartus/reverse/bitstream.rbf_r && ../quartus/reverse/a.out ./src/fpga/output_files/ap_core.rbf ../quartus/reverse/bitstream.rbf_r) && (cd ../quartus/reverse && cmd.exe /c copy bitstream.rbf_r "E:\Cores\test.andi amaranth\bitstream.rbf_r") && (cmd.exe /c copy video.json "E:\Cores\test.andi amaranth\video.json")
```

This assumes JSON files besides video.json have already been configured per the Analogue documentation. Clearer build instructions are forthcoming.

## Editing

The only important files in this tree are in `src/fpga/amaranth_core/embed_amaranth_core`.

* [app_toplevel.py](src/fpga/amaranth_core/embed_amaranth_core/app_toplevel.py) - Put your "app logic" here, based on the given input and output signals
* [toplevel.py](src/fpga/amaranth_core/embed_amaranth_core/toplevel.py) - This is the amaranth fake toplevel which gets embedded into the verilog fake toplevel (which gets embedded into apf). Edit it (and possibly also [core_top.v](src/fpga/core/core_top.v)) if you need to add additional input and output signals
* [resolution.py](src/fpga/amaranth_core/embed_amaranth_core/resolution.py) - This determines the screen size and refresh rate. Create it with [scripts/resolution.py](scripts/resolution.py).
* [pyproject.toml](src/fpga/amaranth_core/pyproject.toml) - Documents the invocable pdm commands, which are implemented in [build.py](src/fpga/amaranth_core/embed_amaranth_core/build.py)

## License

This is a WIP and you are granted no rights to it. See also Analogue's legal information below.

# Analogue Core Template README
This is a template repository for a core which contains all of the core definition JSON files and FPGA starter code.

## Legal
Analogue’s Development program was created to further video game hardware preservation with FPGA technology. Analogue Developers have access to Analogue Pocket I/O’s so Developers can utilize cartridge adapters or interface with other pieces of original or bespoke hardware to support legacy media. Analogue does not support or endorse the unauthorized use or distribution of material protected by copyright or other intellectual property rights.
