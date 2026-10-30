import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.hashing import canonical_json, sha256_hex
from domain.chain import append_entry, verify_chain
from domain.merkle import merkle_proof, merkle_root, verify_proof


def build_chain(n: int):
    entries = ()
    for i in range(n):
        entries = append_entry(entries, {"step": i, "action": f"tool_{i}"}, timestamp=1000.0 + i)
    return entries


def test_canonical_json_is_order_independent():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert canonical_json({"a": 1}) == b'{"a":1}'


def test_sha256_known_vector():
    assert sha256_hex(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_intact_chain_verifies():
    assert verify_chain(build_chain(10)).ok
    assert verify_chain(()).ok


def test_edit_is_detected_and_located():
    entries = build_chain(10)
    tampered = entries[:4] + (replace(entries[4], payload={"step": 4, "action": "evil"}),) + entries[5:]
    result = verify_chain(tampered)
    assert not result.ok and result.first_bad_index == 4


def test_delete_is_detected():
    entries = build_chain(10)
    result = verify_chain(entries[:3] + entries[4:])
    assert not result.ok and result.first_bad_index == 3


def test_insert_is_detected():
    entries = build_chain(10)
    extra = replace(entries[2], payload={"step": "x"})
    result = verify_chain(entries[:3] + (extra,) + entries[3:])
    assert not result.ok and result.first_bad_index == 3


def test_reorder_is_detected():
    entries = build_chain(10)
    swapped = entries[:2] + (entries[3], entries[2]) + entries[4:]
    assert not verify_chain(swapped).ok


def test_rewriting_one_entry_fully_still_breaks_later_links():
    entries = build_chain(6)
    from domain.chain import compute_entry_hash
    forged_payload = {"step": 2, "action": "forged"}
    forged = replace(
        entries[2],
        payload=forged_payload,
        entry_hash=compute_entry_hash(2, entries[2].timestamp, forged_payload, entries[2].prev_hash),
    )
    result = verify_chain(entries[:2] + (forged,) + entries[3:])
    assert not result.ok and result.first_bad_index == 3


@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 13, 100])
def test_every_proof_verifies(n):
    hashes = [e.entry_hash for e in build_chain(n)]
    root = merkle_root(hashes)
    for i, h in enumerate(hashes):
        assert verify_proof(h, merkle_proof(hashes, i), root)


def test_proof_fails_for_wrong_entry_or_root():
    hashes = [e.entry_hash for e in build_chain(7)]
    root = merkle_root(hashes)
    proof = merkle_proof(hashes, 3)
    assert not verify_proof(hashes[4], proof, root)
    assert not verify_proof(hashes[3], proof, merkle_root(hashes[:-1]))


def test_root_changes_when_any_entry_changes():
    hashes = [e.entry_hash for e in build_chain(9)]
    root = merkle_root(hashes)
    for i in range(len(hashes)):
        changed = hashes[:i] + [sha256_hex(b"other")] + hashes[i + 1:]
        assert merkle_root(changed) != root


def test_empty_tree_is_rejected():
    with pytest.raises(ValueError):
        merkle_root([])
