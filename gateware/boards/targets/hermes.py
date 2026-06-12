#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2015-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./hermes.py --uart-name=jtag_uart --build --load
# litex_term --jtag-config ../prog/openocd_usb_blaster.cfg jtag

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from boards.platforms import hermeslite_hl2b5up

from litex.soc.cores.clock import CycloneIVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster, SPIMaster
from litex.soc.cores.pwm import PWM
from litex.soc.cores.gpio import GPIOOut

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk125 = platform.request("clk125")

        # PLL
        self.pll = pll = CycloneIVPLL(speedgrade="-8")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk125, 125e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, bios_flash_offset=0, sys_clk_freq=50e6,
        with_led_chaser  = True,
        with_spi_flash   = False,
        **kwargs):
        platform = hermeslite_hl2b5up.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if with_spi_flash and bios_flash_offset:
            # Disable Integrated ROM
            kwargs["integrated_rom_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Hermes", **kwargs)

        if with_spi_flash:
            # Use SPI-Flash as ROM.

            # SPI Flash ----------------------------------------------------------------------------
            from litespi.modules import W25Q16JV_IM
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q16JV_IM(Codes.READ_1_1_2), with_master=False)

            # Add ROM linker region ----------------------------------------------------------------
            if bios_flash_offset:
                self.bus.add_region("rom", SoCRegion(
                    origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
                    size   = 512 * KILOBYTE,
                    linker = True)
                )
                self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # GPIO wires
        self.power_clk_v1_2 = PWM(platform.request("power_clk_v1_2"))
        self.power_clk_v3_3 = PWM(platform.request("power_clk_v3_3"))
        self.power_en_vpa = GPIOOut(platform.request("power_en_vpa"))
        self.power_en_vop = GPIOOut(platform.request("power_en_vop"))
        self.power_en_vbias = GPIOOut(platform.request("power_en_vbias"))
        self.ptt_inttr = GPIOOut(platform.request("ptt_inttr"))
        self.ptt_exttr = GPIOOut(platform.request("ptt_exttr"))
        self.rfsw_sel = GPIOOut(platform.request("rfsw_sel"))

        # I2C devices
        self.i2c_clock = I2CMaster(platform.request("i2c", 0))
        self.i2c_adc = I2CMaster(platform.request("i2c", 1))
        self.i2c_dac = I2CMaster(platform.request("i2c", 2))

        # ad9866
        self.spi_ad9866 = SPIMaster(platform.request("spi", 0))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=hermeslite_hl2b5up.Platform, description="LiteX SoC on Hermes-Lite.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-led-chaser", action="store_true",      help="Enable LED chaser.")
    parser.add_target_argument("--with-spi-flash",   action="store_true",     help="Add SPI flash support to the SoC")
    parser.add_target_argument("--bios-flash-offset", default="0x80000",      help="BIOS offset in SPI Flash.")
    args = parser.parse_args()

    soc = BaseSoC(
        bios_flash_offset= int(args.bios_flash_offset, 0),
        sys_clk_freq     = args.sys_clk_freq,
        with_led_chaser  = args.with_led_chaser,
        with_spi_flash   = args.with_spi_flash,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
