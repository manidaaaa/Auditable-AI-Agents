"""Live test against a local Hardhat chain. Skipped when node/artifacts are unavailable."""
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

web3 = pytest.importorskip("web3")
from app.chain_client import ARTIFACT, anchor_pending, deploy_anchor, local_chain, read_batches
from domain.agent import DEFAULT_TOOLS, run_agent, scripted_llm
from domain.audit import verify_against_chain

pytestmark = pytest.mark.skipif(
    not (shutil.which("npx") and ARTIFACT.exists()), reason="needs npx and `npx hardhat compile`"
)

TASK = "compute 2+2 and count words in 'x y' and capital of France"


def test_anchor_and_verify_on_local_chain():
    ticks = iter(range(1000, 2000))
    _, log = run_agent(TASK, scripted_llm, DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    with local_chain() as w3:
        sender, other = w3.eth.accounts[0], w3.eth.accounts[1]
        contract = deploy_anchor(w3, sender)

        first = anchor_pending(contract, sender, log, batch_size=5, flush=False)
        assert [(r.first_index, r.count) for r in first] == [(0, 5), (5, 5)]
        again = anchor_pending(contract, sender, log, batch_size=5, flush=True)
        assert [(r.first_index, r.count) for r in again] == [(10, len(log) - 10)]
        assert anchor_pending(contract, sender, log, batch_size=5) == ()  # idempotent

        batches = read_batches(contract, sender)
        assert verify_against_chain(log, batches).ok
        assert not verify_against_chain(log[:-1], batches).ok
        assert read_batches(contract, other) == ()  # another account sees no batches
