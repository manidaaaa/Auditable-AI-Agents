import hashlib
import importlib.util
import json
from pathlib import Path

from domain.merkle import merkle_root

ROOT = Path(__file__).resolve().parents[1]


def load_make_vectors():
    spec = importlib.util.spec_from_file_location("make_vectors", ROOT / "scripts" / "make_vectors.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stored_vectors_match_what_python_produces_now():
    stored = json.loads((ROOT / "tests" / "vectors" / "audit_vectors.json").read_text())
    module = load_make_vectors()
    assert stored == [module.build_vector(v["n"]) for v in stored]


def test_two_leaf_root_matches_the_specification_by_hand():
    a, b = "11" * 32, "22" * 32
    leaf = lambda h: hashlib.sha256(b"\x00" + bytes.fromhex(h)).digest()
    expected = hashlib.sha256(b"\x01" + leaf(a) + leaf(b)).hexdigest()
    assert merkle_root([a, b]) == expected


def test_single_leaf_root_is_the_domain_separated_leaf_hash():
    h = "ab" * 32
    assert merkle_root([h]) == hashlib.sha256(b"\x00" + bytes.fromhex(h)).hexdigest()


def test_odd_node_is_carried_up_not_duplicated():
    hs = ["01" * 32, "02" * 32, "03" * 32]
    leaf = lambda h: hashlib.sha256(b"\x00" + bytes.fromhex(h)).digest()
    node = lambda l, r: hashlib.sha256(b"\x01" + l + r).digest()
    assert merkle_root(hs) == node(node(leaf(hs[0]), leaf(hs[1])), leaf(hs[2])).hex()
    assert merkle_root(hs) != merkle_root(hs + [hs[2]])  # duplicating the last leaf gives a different root
