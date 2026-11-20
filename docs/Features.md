# Features and known limitations

This document provides information on known features and known
limitations of this LiteX implementation on the Hermes-Lite hardware.

This implementation is experimental.

# Features

* The LiteX infrastructure builds and runs on a hermes-lite v2.0
  "hl2b5up" radio. This includes the standard System-on-Chip (SoC)
  components such as a "vexriscv" softcore. Software is capable of
  initializing the onboard ethernet and responding to basic IP
  packets. Software can control the onboard LEDs and communicate with
  the three onboard i2c devices (5p49v5923 clock generator, MAX11613
  low-speed ADC, and MCP4662 DAC).

* The software runs "execute in place" from the onboard 16Mbit
  (2MByte) W25Q16 flash chip.

* A basic implementation with a "vexriscv lite" softcore (`--variant
  lite`), spi flash, ethernet, and basic i2c support utilizes: ~29% of
  logic elements, ~59% of M9Ks, 2 of 4 PLLs, and 0 multipliers.

# Known limitations

* The ad9866 radio is not supported. It is not possible to use the
  Hermes-Lite as an actual radio with the current implementation. The
  current implementation is experimental and is targeted at
  developers.

* This implementation defines pin `86` and pin `89` as "3.3-V LVTTL"
  (ie, using 3.3 Volts) whereas the upstream implementation defines
  them as "2.5-V" (ie, using 2.5 Volts). This was done to allow UART
  access on these pins. It is not known if this change is valid. Care
  should be taken before connecting 2.5V equipment to these pins, and
  care should be taken before connecting 3.3V equipment to these pins.

* The LiteX ethernet receive buffer is using 16 M9Ks where it should
  only need 4 M9Ks. This appears to be a bug in the upstream LiteX
  and/or migen implementation. This wastes ~18% of all available M9Ks.

* The software in this implementation can configure the ethernet port
  and utilize IP. Only connect this device to a private network where
  all other devices on the network are trusted (that is, do not
  connect it to the open internet). No networking security has been
  implemented.

* This implementation has been tested on a Hermes-Lite v2.0 device
  (with ksz9021 ethernet chip). It is unknown if this implementation
  will apply to any other hermes-lite hardware.
