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

        # setup balances, fetch latest from forked chain
        self.balances = {
            USDC: defaultdict(int),
            USDT: defaultdict(int),
        }
        for acc in chain.accounts:
            self.balances[USDC][acc] = USDC.balanceOf(acc)
            self.balances[USDT][acc] = USDT.balanceOf(acc)

        self.balances[USDC][USDC_COMET] = USDC.balanceOf(USDC_COMET)
        self.balances[USDT][USDT_COMET] = USDT.balanceOf(USDT_COMET)

        self.balances[USDC][self.contract] = 0
        self.balances[USDT][self.contract] = 0

        # deposit USDC
        amount = 100_000 * 10 ** USDC.decimals()

        mint_erc20(USDC, owner, amount)
        USDC.approve(self.contract, amount, from_=owner)
        self.contract.deposit(USDC, amount, from_=owner)

        self.balances[USDC][USDC_COMET] += amount

        # deposit USDT
        amount = 100_000 * 10 ** USDT.decimals()

        mint_erc20(USDT, owner, amount)
        USDT.approve(self.contract, amount, from_=owner)
        self.contract.deposit(USDT, amount, from_=owner)

        self.balances[USDT][USDT_COMET] += amount

    @flow()
    def flow_swap(self):
        sender = random_account()
        token_in = random.choice([USDC, USDT])
        token_out = random.choice([USDC, USDT])

        amount = random_int(0, 100 * 10 ** token_in.decimals(), edge_values_prob=0.1)
        mint_erc20(token_in, sender, amount)
        token_in.approve(self.contract, amount, from_=sender)

        self.balances[token_in][sender] += amount

        tx = self.contract.swap(token_in, token_out, amount, from_=sender)

        token_out.transferFrom(self.contract, sender, amount, from_=sender)

        self.balances[token_in][self.comets[token_in]] += amount
        self.balances[token_out][self.comets[token_out]] -= amount

        self.balances[token_in][sender] -= amount
        self.balances[token_out][sender] += amount

        logger.info(f"Swapped {amount} {token_in.symbol()} to {token_out.symbol()}")

    @invariant()
    def invariant_balances(self):
        for token, balances in self.balances.items():
            for acc, balance in balances.items():
                assert token.balanceOf(acc) == balance, f"Balance for {token.symbol()} of {acc} is incorrect"


# https://1rpc.io/eth
# https://eth.drpc.org
# https://eth.blockrazor.xyz

# https://www.infura.io/
# https://www.alchemy.com/

@chain.connect(fork="https://1rpc.io/eth")
def test_stage2():
    Stage2FuzzTest().run(1, 100_000)
