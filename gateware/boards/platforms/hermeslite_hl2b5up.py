# Definitions for hermes lite board (hl2b5up)
#
# Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Ethernet
    ("clk125", 0, Pins("52"), IOStandard("2.5-V")),
    ("eth_clocks", 0,
        Subsignal("tx", Pins("66")),
        Subsignal("rx", Pins("53")),
        IOStandard("2.5-V")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("49")),
        Subsignal("mdio",    Pins("50")),
        Subsignal("mdc",     Pins("51")),
        Subsignal("rx_ctl",  Pins("54")),
        Subsignal("rx_data", Pins("58 59 60 64")),
        Subsignal("tx_ctl",  Pins("65")),
        Subsignal("tx_data", Pins("71 69 68 67")),
        IOStandard("2.5-V")
    ),

    # Flash (W25Q16JVSNIQ-ND)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("8")),
        Subsignal("clk",  Pins("12")),
        Subsignal("dq", Pins("6 13")),
        IOStandard("3.3-V LVTTL")
    ),

    # Leds
    ("user_led", 0, Pins("98"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("99"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("100"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("101"), IOStandard("3.3-V LVTTL")),

    # Serial - !!! uses 3.3V instead of upstream 2.5V !!!
    ("serial", 0,
        Subsignal("tx", Pins("86")),
        Subsignal("rx", Pins("89")),
        IOStandard("3.3-V LVTTL")
    ),

    # 5p49v5923 programmable clock generator
    ("i2c", 0,
        Subsignal("scl", Pins("103")),
        Subsignal("sda", Pins("104")),
        IOStandard("3.3-V LVTTL")
    ),

    # MAX11613 low-speed ADC
    ("i2c", 1,
        Subsignal("scl", Pins("33")),
        Subsignal("sda", Pins("32")),
        IOStandard("3.3-V LVTTL")
    ),

    # MCP4662 and I2C connector on back board (n2adr)
    ("i2c", 2,
        Subsignal("scl", Pins("31")),
        Subsignal("sda", Pins("30")),
        IOStandard("3.3-V LVTTL")
    ),

    # AD9866
    ("ad9866", 0,
        Subsignal("tx_data", Pins("137 141 142 143 144 10")),
        Subsignal("rx_data", Pins("120 121 125 132 133 135")),
        Subsignal("mode", Pins("136")),
        Subsignal("clk", Pins("126")),
        Subsignal("rst_n", Pins("119")),
        Subsignal("rxsync", Pins("115")),
        Subsignal("txsync", Pins("114")),
        Subsignal("txquiet_n", Pins("113")),
        Subsignal("rxclk", Pins("112")),
        Subsignal("pga5", Pins("105")),
        IOStandard("3.3-V LVTTL")
    ),
    ("spi", 0,
        Subsignal("mosi", Pins("111")),
        Subsignal("clk", Pins("110")),
        Subsignal("cs_n", Pins("106")),
        IOStandard("3.3-V LVTTL")
    ),

    # Power control
    ("power_clk_v1_2", 0, Pins("46"), IOStandard("2.5-V")),
    ("power_clk_v3_3", 0, Pins("44"), IOStandard("2.5-V")),
    ("power_en_vpa", 0, Pins("43"), IOStandard("2.5-V")),
    ("power_en_vop", 0, Pins("42"), IOStandard("2.5-V")),
    ("power_en_vbias", 0, Pins("39"), IOStandard("2.5-V")),

    # Push-to-talk controls
    ("ptt_inttr", 0, Pins("7"), IOStandard("3.3-V LVTTL")),
    ("ptt_exttr", 0, Pins("28"), IOStandard("3.3-V LVTTL")),
    ("rfsw_sel", 0, Pins("11"), IOStandard("3.3-V LVTTL")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("db1", "72 76 77 80 83 85"), # 2.5V
    ("db12", "86 87 88 89"), # 2.5V
    ("cn8", "25"),
    ("cn9", "24"),
    ("cn10", "23"),
    ("phone", "91 90"),
    ("tp2", "55"), # 2.5V
    ("tp7", "129"),
    ("tp8", "128"),
    ("tp9", "127"),
]

# Platform -----------------------------------------------------------------------------------------

# Altera commands to force pins to be available as regular IO pins
RegularIO = [
    "RESERVE_DATA0_AFTER_CONFIGURATION",
    "RESERVE_DATA1_AFTER_CONFIGURATION",
    "RESERVE_FLASH_NCE_AFTER_CONFIGURATION",
    "RESERVE_DCLK_AFTER_CONFIGURATION",
    "CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION"
]

# Disable Quartus "switch coupling" errors
NO_TOGGLE = [
    "rfsw_sel",
    "spiflash_dq[1]",
]

class Platform(AlteraPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "EP4CE22E22C8", _io, _connectors, toolchain=toolchain)
        for name in RegularIO:
            self.add_platform_command(
                "set_global_assignment -name %s \"USE AS REGULAR IO\""
                % (name,))
        for name in NO_TOGGLE:
            self.add_platform_command(
                'set_instance_assignment -name IO_MAXIMUM_TOGGLE_RATE "0 MHz" -to %s'
                % (name,))

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
