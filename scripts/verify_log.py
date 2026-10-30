#!/usr/bin/env python3
"""Check an audit log file (JSON Lines) for hash-chain integrity. No blockchain needed.

Usage: python scripts/verify_log.py research/experiments/agent_logs/ollama_run.jsonl
Exit code 0 if intact, 1 if tampering is found.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.logstore import load_log
from domain.chain import verify_chain


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    entries = load_log(Path(argv[1]))
    result = verify_chain(entries)
    if result.ok:
        print(f"INTACT: {len(entries)} entries, hash chain verifies")
        return 0
    print(f"TAMPERING DETECTED at entry {result.first_bad_index}: {result.reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
