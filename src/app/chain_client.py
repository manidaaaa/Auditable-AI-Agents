"""Talks to the AuditAnchor contract on a local Hardhat chain (the only side-effecting module)."""
from __future__ import annotations

import json
import socket
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

from web3 import Web3

from domain.audit import AnchoredBatch, batch_root, plan_batches
from domain.chain import LogEntry

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = REPO_ROOT / "artifacts" / "contracts" / "AuditAnchor.sol" / "AuditAnchor.json"


@dataclass(frozen=True)
class AnchorReceipt:
    batch_id: int
    first_index: int
    count: int
    root: str
    gas_used: int


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def local_chain(port: int | None = None) -> Iterator[Web3]:
    """Start `hardhat node`, yield a connected Web3, and stop the node afterwards."""
    port = port or free_port()
    process = subprocess.Popen(
        ["npx", "hardhat", "node", "--port", str(port)],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    w3 = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{port}"))
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError("hardhat node exited early")
            try:
                if w3.is_connected():
                    break
            except Exception:
                pass
            time.sleep(0.25)
        else:
            raise RuntimeError("hardhat node did not start in time")
        yield w3
    finally:
        process.terminate()
        process.wait(timeout=10)


def deploy_anchor(w3: Web3, sender: str):
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    factory = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    receipt = w3.eth.wait_for_transaction_receipt(factory.constructor().transact({"from": sender}))
    return w3.eth.contract(address=receipt.contractAddress, abi=artifact["abi"])


def read_batches(contract, agent: str) -> tuple[AnchoredBatch, ...]:
    count = contract.functions.batchCount(agent).call()
    rows = (contract.functions.getBatch(agent, i).call() for i in range(count))
    return tuple(AnchoredBatch(bytes(root).hex(), int(first), int(n)) for root, first, n, _ts in rows)


def anchor_pending(
    contract,
    sender: str,
    entries: Sequence[LogEntry],
    *,
    batch_size: int,
    flush: bool = True,
) -> tuple[AnchorReceipt, ...]:
    """Anchor every batch not yet on-chain. What counts as anchored is read from the chain itself."""
    w3 = contract.w3
    existing = read_batches(contract, sender)
    anchored = existing[-1].first_index + existing[-1].count if existing else 0
    receipts = []
    for first, count in plan_batches(len(entries), anchored, batch_size, flush):
        root = batch_root(entries, first, count)
        tx = contract.functions.anchor(bytes.fromhex(root), count).transact({"from": sender})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        receipts.append(AnchorReceipt(len(existing) + len(receipts), first, count, root, receipt.gasUsed))
    return tuple(receipts)
