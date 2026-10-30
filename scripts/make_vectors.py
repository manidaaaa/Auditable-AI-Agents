#!/usr/bin/env python3
"""Write shared test vectors (Python-computed Merkle roots and proofs) for the Solidity tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from domain.chain import append_entry
from domain.merkle import merkle_proof, merkle_root


def build_vector(n: int) -> dict:
    entries = ()
    for i in range(n):
        entries = append_entry(entries, {"step": i, "action": f"tool_{i}"}, timestamp=1000.0 + i)
    hashes = [e.entry_hash for e in entries]
    return {
        "n": n,
        "entry_hashes": hashes,
        "root": merkle_root(hashes),
        "proofs": [
            [{"right": side == "R", "hash": sibling} for side, sibling in merkle_proof(hashes, i)]
            for i in range(n)
        ],
    }


def main() -> None:
    vectors = [build_vector(n) for n in (1, 2, 3, 5, 8, 13, 100)]
    out = ROOT / "tests" / "vectors" / "audit_vectors.json"
    out.write_text(json.dumps(vectors, indent=2), encoding="utf-8")
    print(f"wrote {len(vectors)} vectors to {out}")


if __name__ == "__main__":
    main()
