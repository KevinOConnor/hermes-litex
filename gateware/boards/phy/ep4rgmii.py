#
# RGMII PHY for the Cyclone IV
#
# Copyright (c) 2021 Franck Jullien <franck.jullien@collshade.fr>
# Copyright (c) 2015-2023 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput, DDRInput
from litex.build.generic_platform import *
from litex.soc.cores.clock import CycloneIVPLL

from liteeth.common import *
from liteeth.phy.common import *

# LiteEth PHY RGMII TX -----------------------------------------------------------------------------

class LiteEthPHYRGMIITX(LiteXModule):
    def __init__(self, pads):
        self.sink = sink = stream.Endpoint(eth_phy_description(8))

        # # #

        # TX Data IOs.
        # ------------
        tx_data_h = Signal(4)
        tx_data_l = Signal(4)
        self.specials += DDROutput(
            i1  = tx_data_h,
            i2  = tx_data_l,
            o   = pads.tx_data,
            clk = ClockSignal("eth_tx"),
        )

        # TX Ctl IOs.
        # -----------
        tx_ctl_h = Signal()
        tx_ctl_l = Signal()
        self.specials += DDROutput(
            i1  = tx_ctl_h,
            i2  = tx_ctl_l,
            o   = pads.tx_ctl,
            clk = ClockSignal("eth_tx"),
        )

        # Logic.
        # ------
        self.comb += sink.ready.eq(1)
        self.comb += [
            tx_ctl_h.eq(sink.valid),
            tx_ctl_l.eq(sink.valid),
            tx_data_h.eq(sink.data[:4]),
            tx_data_l.eq(sink.data[4:]),
        ]

# LiteEth PHY RGMII RX -----------------------------------------------------------------------------

class LiteEthPHYRGMIIRX(LiteXModule):
    def __init__(self, pads):
        self.source = source = stream.Endpoint(eth_phy_description(8))

        rx_ctl         = Signal(2)
        rx_ctl_reg     = Signal(2)
        self.specials += DDRInput(
            clk = ClockSignal("eth_rx"),
            i   = pads.rx_ctl,
            # XXX - order seems backwards
            o1  = rx_ctl[1],
            o2  = rx_ctl[0],
        )
        self.sync += rx_ctl_reg.eq(rx_ctl)

        rx_data        = Signal(8)
        rx_data_reg    = Signal(8)
        self.specials += DDRInput(
            clk = ClockSignal("eth_rx"),
            i   = pads.rx_data,
            # XXX - order seems backwards, but only works this way...
            o1  = rx_data[4:],
            o2  = rx_data[:4],
        )
        self.sync += rx_data_reg.eq(rx_data)

        rx_ctl_reg_d = Signal(2)
        self.sync += rx_ctl_reg_d.eq(rx_ctl_reg)

        last = Signal()
        self.comb += last.eq(~rx_ctl_reg[0] & rx_ctl_reg_d[0])
        self.sync += [
            source.valid.eq(rx_ctl_reg[0]),
            source.data.eq(rx_data_reg)
        ]
        self.comb += source.last.eq(last)

# LiteEth PHY RGMII CRG ----------------------------------------------------------------------------

class LiteEthPHYRGMIICRG(LiteXModule):
    def __init__(self, clock_pads, pads, with_hw_init_reset, hw_reset_cycles=256):
        self._reset = CSRStorage(description="PHY reset.")

        # # #

        # Clk Domains.
        # ------------
        self.cd_eth_rx         = ClockDomain(name="eth_rx")
        self.cd_eth_tx         = ClockDomain(name="eth_tx")
        self.cd_eth_tx_delayed = ClockDomain(name="eth_tx_delayed", reset_less=True)

        # TX PLL.
        # -------
        self.pll = pll = CycloneIVPLL()
        pll.register_clkin(clock_pads.rx,    freq=125e6)
        pll.create_clkout(self.cd_eth_rx,         freq=125e6, phase=0,  with_reset=False)
        pll.create_clkout(self.cd_eth_tx,         freq=125e6, phase=0,  with_reset=False)
        pll.create_clkout(self.cd_eth_tx_delayed, freq=125e6, phase=90)

        # TX Clk.
        # -------
        self.specials += DDROutput(
            i1  = 1,
            i2  = 0,
            o   = clock_pads.tx,
            clk = ClockSignal("eth_tx_delayed"),
        )

        # Reset.
        # ------
        self.reset = reset = Signal()
        if with_hw_init_reset:
            self.hw_reset = LiteEthPHYHWReset(cycles=hw_reset_cycles)
            self.comb += reset.eq(self._reset.storage | self.hw_reset.reset)
        else:
            self.comb += reset.eq(self._reset.storage)
        if hasattr(pads, "rst_n"):
            self.comb += pads.rst_n.eq(~reset)
        self.specials += [
            AsyncResetSynchronizer(self.cd_eth_tx, reset),
            AsyncResetSynchronizer(self.cd_eth_rx, reset),
        ]

# LiteEth PHY RGMII --------------------------------------------------------------------------------

class LiteEthPHYRGMII(LiteXModule):
    dw          = 8
    tx_clk_freq = 125e6
    rx_clk_freq = 125e6
    def __init__(self, clock_pads, pads, with_hw_init_reset=True, hw_reset_cycles=256):
        self.crg = LiteEthPHYRGMIICRG(clock_pads, pads, with_hw_init_reset, hw_reset_cycles)
        self.tx  = ClockDomainsRenamer("eth_tx")(LiteEthPHYRGMIITX(pads))
        self.rx  = ClockDomainsRenamer("eth_rx")(LiteEthPHYRGMIIRX(pads))
        self.sink, self.source = self.tx.sink, self.rx.source

        if hasattr(pads, "mdc"):
            self.mdio = LiteEthPHYMDIO(pads)
