"""Merkle tree over entry hashes, with inclusion proofs.

Leaves are hashed as sha256(0x00 || leaf), inner nodes as sha256(0x01 || left || right).
An unpaired node is carried up unchanged, so no leaf is ever duplicated.
"""
from __future__ import annotations

import hashlib
from typing import Sequence

# A proof step is (side, sibling_hash_hex) where side is "L" or "R": where the sibling sits.
ProofStep = tuple[str, str]


def _leaf(entry_hash_hex: str) -> bytes:
    return hashlib.sha256(b"\x00" + bytes.fromhex(entry_hash_hex)).digest()


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _levels(entry_hashes: Sequence[str]) -> list[list[bytes]]:
    if not entry_hashes:
        raise ValueError("cannot build a Merkle tree from zero entries")
    levels = [[_leaf(h) for h in entry_hashes]]
    while len(levels[-1]) > 1:
        current = levels[-1]
        nxt = [_node(current[i], current[i + 1]) for i in range(0, len(current) - 1, 2)]
        if len(current) % 2:
            nxt.append(current[-1])
        levels.append(nxt)
    return levels


def merkle_root(entry_hashes: Sequence[str]) -> str:
    return _levels(entry_hashes)[-1][0].hex()


def merkle_proof(entry_hashes: Sequence[str], index: int) -> tuple[ProofStep, ...]:
    if not 0 <= index < len(entry_hashes):
        raise IndexError("entry index out of range")
    steps: list[ProofStep] = []
    position = index
    for level in _levels(entry_hashes)[:-1]:
        sibling = position ^ 1
        if sibling < len(level):
            steps.append(("R" if sibling > position else "L", level[sibling].hex()))
        position //= 2
    return tuple(steps)


def verify_proof(entry_hash: str, proof: Sequence[ProofStep], root: str) -> bool:
    current = _leaf(entry_hash)
    for side, sibling_hex in proof:
        sibling = bytes.fromhex(sibling_hex)
        current = _node(current, sibling) if side == "R" else _node(sibling, current)
    return current.hex() == root
