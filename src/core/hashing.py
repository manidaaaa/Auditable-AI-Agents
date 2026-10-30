"""Hashing primitives: canonical JSON and SHA-256."""
from __future__ import annotations

import hashlib
import json
from typing import Any

GENESIS_HASH: str = "0" * 64


def canonical_json(value: Any) -> bytes:
    """Deterministic bytes for a JSON-serialisable value (sorted keys, no spaces, UTF-8)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
