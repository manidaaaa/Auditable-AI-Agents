"""Pure audit logic: batch planning and checking a stored log against anchored batches."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from domain.chain import LogEntry, verify_chain
from domain.merkle import merkle_root


@dataclass(frozen=True)
class AnchoredBatch:
    root: str  # hex, no 0x prefix
    first_index: int
    count: int


@dataclass(frozen=True)
class AuditReport:
    ok: bool
    chain_ok: bool
    chain_reason: str = ""
    first_bad_index: int | None = None
    bad_batches: tuple[int, ...] = ()
    truncated: bool = False
    unanchored_entries: int = 0
    notes: tuple[str, ...] = field(default_factory=tuple)


def plan_batches(total: int, anchored: int, batch_size: int, flush: bool) -> tuple[tuple[int, int], ...]:
    """(first_index, count) for new batches. Full batches always; a final partial one only if `flush`."""
    batches: list[tuple[int, int]] = []
    start = anchored
    while total - start >= batch_size:
        batches.append((start, batch_size))
        start += batch_size
    if flush and total - start > 0:
        batches.append((start, total - start))
    return tuple(batches)


def batch_root(entries: Sequence[LogEntry], first_index: int, count: int) -> str:
    return merkle_root([e.entry_hash for e in entries[first_index : first_index + count]])


def verify_against_chain(entries: Sequence[LogEntry], batches: Sequence[AnchoredBatch]) -> AuditReport:
    """Check the stored log against on-chain batch roots.

    The hash chain catches edits, deletions, insertions and reordering. The on-chain roots also
    catch a log that was rewritten consistently (all hashes recomputed) or truncated.
    """
    chain = verify_chain(entries)
    bad: list[int] = []
    truncated = False
    for batch_id, batch in enumerate(batches):
        if batch.first_index + batch.count > len(entries):
            truncated = True
            bad.append(batch_id)
        elif batch_root(entries, batch.first_index, batch.count) != batch.root:
            bad.append(batch_id)

    first_bad = chain.first_bad_index
    if bad and first_bad is None:
        first_bad = batches[bad[0]].first_index  # batch-level location only

    anchored = batches[-1].first_index + batches[-1].count if batches else 0
    notes = []
    if not chain.ok:
        notes.append(f"hash chain broken at entry {chain.first_bad_index}: {chain.reason}")
    if bad:
        notes.append(f"batches not matching on-chain roots: {list(bad)}")
        if chain.ok:
            first = batches[bad[0]]
            notes.append(
                f"hash chain is self-consistent, so only batch-level location is possible: "
                f"entries {first.first_index}..{first.first_index + first.count - 1}"
            )
    if truncated:
        notes.append("log is shorter than what was anchored (entries removed from the end)")
    return AuditReport(
        ok=chain.ok and not bad,
        chain_ok=chain.ok,
        chain_reason=chain.reason,
        first_bad_index=first_bad,
        bad_batches=tuple(bad),
        truncated=truncated,
        unanchored_entries=max(len(entries) - anchored, 0),
        notes=tuple(notes),
    )
