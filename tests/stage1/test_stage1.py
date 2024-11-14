from wake.testing import *
from wake.testing.fuzzing import *

from pytypes.contracts.stage1.Stage1 import Stage1


class Stage1FuzzTest(FuzzTest):
    contract: Stage1

    def pre_sequence(self):
        self.contract = Stage1.deploy()

    @flow()
    def flow_run(self):
        payload = random_bytes(0, 10_000)

        with may_revert(UnknownTransactionRevertedError(b"")):
            tx = self.contract.transact(self.contract.f.selector + payload, from_=random_account())

    #@flow()
    def flow_run_guided(self):
        x = random_int(114999999000000000000000000000000000000000000000000000000000000000000000000000, uint256.max)
        y = random_int(0, 16474011154664524427946373126085988481683748083205070504932198000989141204992)
        z = random_int(0, uint256.max)
        tx = self.contract.f(x, y, z, from_=random_account())


@chain.connect()
@on_revert(lambda e: print(e.tx.call_trace if e.tx else "Call reverted"))
def test_stage1():
    Stage1FuzzTest().run(1, 100_000)
