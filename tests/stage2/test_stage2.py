import logging
from collections import defaultdict
from typing import Dict
from wake.testing import *
from wake.testing.fuzzing import *

from pytypes.contracts.stage2.Stage2 import Stage2
from pytypes.contracts.stage2.IComet import IComet
from pytypes.contracts.stage2.IERC20Metadata import IERC20Metadata


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

USDC = IERC20Metadata("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
USDT = IERC20Metadata("0xdAC17F958D2ee523a2206206994597C13D831ec7")

USDC_COMET = IComet("0xc3d688B66703497DAA19211EEdff47f25384cdc3")
USDT_COMET = IComet("0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840")


class Stage2FuzzTest(FuzzTest):
    contract: Stage2

    balances: Dict[IERC20Metadata, Dict[Account, int]]
    comets: Dict[IERC20Metadata, IComet]

    def pre_sequence(self) -> None:
        owner = chain.accounts[0]
        self.contract = Stage2.deploy(from_=owner)

        self.comets = {
            USDC: USDC_COMET,
            USDT: USDT_COMET,
        }

        # TODO: setup balances, fetch latest from forked chain

        # deposit USDC
        amount = 100_000 * 10 ** USDC.decimals()

        mint_erc20(USDC, owner, amount)
        USDC.approve(self.contract, amount, from_=owner)
        self.contract.deposit(USDC, amount, from_=owner)

        # deposit USDT
        amount = 100_000 * 10 ** USDT.decimals()

        mint_erc20(USDT, owner, amount)
        USDT.approve(self.contract, amount, from_=owner)
        self.contract.deposit(USDT, amount, from_=owner)

        # TODO: update balances after deposits

    @flow()
    def flow_swap(self):
        # TODO: call contract.swap() here with random parameters and update balances
        pass

    @invariant()
    def invariant_balances(self):
        # TODO: check that the balances are correct
        pass


# https://1rpc.io/eth
# https://eth.drpc.org
# https://eth.blockrazor.xyz

# https://www.infura.io/
# https://www.alchemy.com/

@chain.connect(fork="https://1rpc.io/eth")
def test_stage2():
    Stage2FuzzTest().run(1, 100_000)
