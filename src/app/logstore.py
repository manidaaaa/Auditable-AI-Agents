"""Off-chain log storage: one JSON object per line."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from domain.chain import LogEntry


def save_log(entries: Sequence[LogEntry], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = (
        json.dumps(
            {
                "index": e.index,
                "timestamp": e.timestamp,
                "payload": e.payload,
                "prev_hash": e.prev_hash,
                "entry_hash": e.entry_hash,
            },
            sort_keys=True,
        )
        for e in entries
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_log(path: Path) -> tuple[LogEntry, ...]:
    rows = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return tuple(
        LogEntry(r["index"], r["timestamp"], r["payload"], r["prev_hash"], r["entry_hash"]) for r in rows
    )
