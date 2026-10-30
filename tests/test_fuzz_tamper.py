"""Randomised tamper tests: every attack must be caught, and an untouched log must never be flagged."""
import random
from dataclasses import replace

import pytest

from domain.audit import AnchoredBatch, batch_root, plan_batches, verify_against_chain
from domain.chain import append_entry, verify_chain

TRIALS = 300


def build(n, rng):
    log = ()
    for i in range(n):
        log = append_entry(log, {"step": i, "value": rng.randint(0, 10**6), "tool": rng.choice("abc")}, 1000.0 + i)
    return log


def anchor(log, rng):
    size = rng.randint(1, 8)
    return tuple(AnchoredBatch(batch_root(log, f, c), f, c) for f, c in plan_batches(len(log), 0, size, True))


def attack_edit_payload(log, rng):
    i = rng.randrange(len(log))
    return log[:i] + (replace(log[i], payload={**log[i].payload, "value": -1}),) + log[i + 1 :]


def attack_edit_timestamp(log, rng):
    i = rng.randrange(len(log))
    return log[:i] + (replace(log[i], timestamp=log[i].timestamp + 0.5),) + log[i + 1 :]


def attack_edit_entry_hash(log, rng):
    i = rng.randrange(len(log))
    return log[:i] + (replace(log[i], entry_hash="f" * 64),) + log[i + 1 :]


def attack_delete(log, rng):
    i = rng.randrange(len(log))
    return log[:i] + log[i + 1 :]


def attack_insert_duplicate(log, rng):
    i = rng.randrange(len(log))
    return log[: i + 1] + (log[i],) + log[i + 1 :]


def attack_swap(log, rng):
    i = rng.randrange(len(log) - 1)
    return log[:i] + (log[i + 1], log[i]) + log[i + 2 :]


def attack_truncate(log, rng):
    return log[: rng.randrange(0, len(log))]


ATTACKS = [
    attack_edit_payload,
    attack_edit_timestamp,
    attack_edit_entry_hash,
    attack_delete,
    attack_insert_duplicate,
    attack_swap,
    attack_truncate,
]


@pytest.mark.parametrize("attack", ATTACKS, ids=lambda a: a.__name__)
def test_attack_is_always_detected(attack):
    rng = random.Random(attack.__name__)
    for _ in range(TRIALS):
        log = build(rng.randint(2, 40), rng)
        batches = anchor(log, rng)
        report = verify_against_chain(attack(log, rng), batches)
        assert not report.ok, f"{attack.__name__} slipped through"


def test_untouched_logs_are_never_flagged():
    rng = random.Random(7)
    for _ in range(TRIALS):
        log = build(rng.randint(1, 40), rng)
        assert verify_chain(log).ok
        assert verify_against_chain(log, anchor(log, rng)).ok


def test_edits_are_located_at_the_edited_entry():
    rng = random.Random(11)
    for _ in range(TRIALS):
        log = build(rng.randint(2, 40), rng)
        i = rng.randrange(len(log))
        tampered = log[:i] + (replace(log[i], payload={"x": "evil"}),) + log[i + 1 :]
        assert verify_chain(tampered).first_bad_index == i


def test_consistent_rewrite_is_caught_by_anchors_not_by_the_chain():
    from domain.chain import compute_entry_hash

    rng = random.Random(3)
    for _ in range(TRIALS):
        log = build(rng.randint(3, 30), rng)
        batches = anchor(log, rng)
        i = rng.randrange(len(log))
        forged = list(log[:i])
        for e in (replace(log[i], payload={"x": "evil"}), *log[i + 1 :]):
            prev = forged[-1].entry_hash if forged else "0" * 64
            forged.append(replace(e, prev_hash=prev, entry_hash=compute_entry_hash(e.index, e.timestamp, e.payload, prev)))
        forged = tuple(forged)
        assert verify_chain(forged).ok
        assert not verify_against_chain(forged, batches).ok
