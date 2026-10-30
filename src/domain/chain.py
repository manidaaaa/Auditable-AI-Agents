"""Hash-chained log entries: each entry commits to the one before it."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from core.hashing import GENESIS_HASH, canonical_json, sha256_hex


@dataclass(frozen=True)
class LogEntry:
    index: int
    timestamp: float
    payload: Mapping[str, Any]
    prev_hash: str
    entry_hash: str


@dataclass(frozen=True)
class ChainVerification:
    ok: bool
    first_bad_index: int | None = None
    reason: str = ""


def compute_entry_hash(index: int, timestamp: float, payload: Mapping[str, Any], prev_hash: str) -> str:
    body = {"index": index, "timestamp": timestamp, "payload": payload, "prev_hash": prev_hash}
    return sha256_hex(canonical_json(body))


def make_entry(
    entries: Sequence[LogEntry],
    payload: Mapping[str, Any],
    timestamp: float,
) -> LogEntry:
    """Build the next entry for a chain (does not mutate `entries`)."""
    index = len(entries)
    prev_hash = entries[-1].entry_hash if entries else GENESIS_HASH
    return LogEntry(index, timestamp, payload, prev_hash, compute_entry_hash(index, timestamp, payload, prev_hash))


def append_entry(entries: Sequence[LogEntry], payload: Mapping[str, Any], timestamp: float) -> tuple[LogEntry, ...]:
    return (*entries, make_entry(entries, payload, timestamp))


def verify_chain(entries: Sequence[LogEntry]) -> ChainVerification:
    """Check indices, links and hashes. Reports the first entry that does not hold up."""
    prev_hash = GENESIS_HASH
    for position, entry in enumerate(entries):
        if entry.index != position:
            return ChainVerification(False, position, "index out of sequence (entry inserted, removed or reordered)")
        if entry.prev_hash != prev_hash:
            return ChainVerification(False, position, "prev_hash does not match the previous entry")
        if entry.entry_hash != compute_entry_hash(entry.index, entry.timestamp, entry.payload, entry.prev_hash):
            return ChainVerification(False, position, "entry content does not match its hash")
        prev_hash = entry.entry_hash
    return ChainVerification(True)
