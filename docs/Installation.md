# Installation

This document provides information on building the LiteX FPGA
bitstream, flashing it to a Hermes-Lite radio, and interacting with
it.

See the LiteX documentation for full details on installation and
available commands. The instructions here are targeted at a Linux
machine (or virtual machine) with
[Docker](https://en.wikipedia.org/wiki/Docker_(software)) installed.

In cases where the example scripts in this repository are not directly
usable, one may still find some value in reviewing the implementation
of the scripts.

## Build a docker container with LiteX and Quartus

This repository contains an example docker definition in the file
`scripts/qlitex.docker`. It provides an environment for Quartus (the
FPGA synthesizer for the ECP4 chip found on the Hermes Lite radio),
LiteX, and openFPGALoader (a utility for flashing images).

To build the container, start by cloning this repository:
```
git clone https://github.com/KevinOConnor/hermes-litex

cd hermes-litex/
```

It is necessary to download the Quartus software and place it into the
`scripts/` directory (the example qlitex.docker file uses the versions
described here):
```
cd scripts/

wget 'https://downloads.intel.com/akdlm/software/acdsinst/25.1std/1129/ib_installe
rs/QuartusLiteSetup-25.1std.0.1129-linux.run'

wget 'https://downloads.intel.com/akdlm/software/acdsinst/25.1std/1129/ib_installe
rs/cyclone-25.1std.0.1129.qdz'

cd ../
```

Then one can build the docker container:
```
docker build -t qlitex -f scripts/qlitex.docker
```

The final step of building the container may take several minutes to
complete.

## Build the Hermes-Lite FPGA bitstream

This repository contains an example shell script (`scripts/qlitex.sh`)
for running the LiteX build utilizing the example docker container.

The shell script creates a `build/` sub-directory in the main source
code directory. That `build/` directory will contain the intermediate
files from LiteX and Quartus.

The LiteX build can take many options. A good starting point is:
```
./scripts/qlitex.sh bash -c 'source /litex-venv/bin/activate ; cd /project/gateware ; python -m boards.targets.hermes --output-dir /build --build --with-led-chaser --with-spi-flash --with-ethernet --timer-uptime --csr-ordering little'
```

After building the FPGA bitstream it can be compressed with:
```
./scripts/qlitex.sh quartus_cpf -c -o bitstream_compression=on /build/gateware/hermeslite_hl2b5up.sof /build/gateware/hermeslite_hl2b5up.compress.rbf
```

The above steps will build the compressed FPGA bitstream (
`build/gateware/hermeslite_hl2b5up.compress.rbf`) along with the
default LiteX "bios" software (`build/software/bios/bios.bin`).

## Flashing the Hermes-Lite hardware

This implementation is experimental! Before flashing the hardware be
sure to review the [known limitations](Features.md) and be sure you
are confident in restoring the original factory flash.

The default build runs the software directly from the flash chip.
That is, it does not need to use FPGA memory to store the software.
The amount of memory available on the FPGA is small, and it is
therefore difficult to fit the software in memory. It is also
therefore difficult to test this implementation without over-writing
the flash chip.

The default build places the compressed FPGA bitstream at the flash
offset `0` and the software at flash offset `0x80000`.

If using a common "USB Blaster clone" programmer then one may be able
to utilize the example `scripts/openfpgaloader.sh` script. The steps
to write to flash with this script are:
```
./scripts/openfpgaloader.sh --fpga-part ep4ce2217 -o 0x80000 -f /build/software/bios/bios.bin

./scripts/openfpgaloader.sh --fpga-part ep4ce2217 -f /build/gateware/hermeslite_hl2b5up.compress.rbf
```

## Interacting via UART

In the default build the LiteX "bios" software provides console access
over UART. The build uses pin `86` for "FPGA tx" and pin `89` for
"FPGA rx". Before hooking any devices to these pins be sure to review
the warning on pin voltage in [known limitations](Features.md). Pin
`86` (FPGA tx) is routed to "DB12 header 6" (row closest to the LEDS
and farthest from the ethernet jack) and Pin `89` (FPGA rx) is routed
to "DB12 header 5" (row closest to the LEDS and second farthest from
the ethernet jack). The "DB12 header 4" (row closest to the LEDS and
third farthest from the ethernet jack) may be used as GND.

If using a common "CP2102 USB to UART adapter" then one may be able to
utilize the example `scripts/litex_term.sh` script to communicate with
the bios:
```
./scripts/litex_term.sh
```

## Interacting with the LiteX "bios" software

Once connected to the LiteX console one can issue a `help` command to
list available commands. There are commands to manipulate the leds,
read/write messages on the three i2c buses, and interact with the
ethernet mdio registers.

The default "bios" software should also configure the ethernet. By
default it uses IP address `192.168.1.50` and one can ping it:
```
ping 192.168.1.50
```

## Restoring the original factory image

See the main Hermes-Lite documentation for full details on restoring
the original flash image.

If using a common "USB Blaster clone" programmer then one may be able
to utilize the example `scripts/openfpgaloader.sh` script to restore
the original image:

* Obtain the original upstream image. A good source is: https://github.com/softerhardware/Hermes-Lite2/tree/master/gateware/bitfiles/stable/20231230_74p2_883a338/hl2b5up_main

* Copy the desired "gateware" to the build directory of this repository.

* Run the script with something like: `./scripts/openfpgaloader.sh --fpga-part ep4ce2217 -f /build/hl2b5up_main.rbf`
