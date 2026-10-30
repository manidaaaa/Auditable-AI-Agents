import itertools
from dataclasses import replace

from app.logstore import load_log, save_log
from domain.agent import DEFAULT_TOOLS, run_agent, scripted_llm
from domain.audit import AnchoredBatch, batch_root, verify_against_chain
from domain.chain import append_entry, verify_chain


def sample_log():
    ticks = itertools.count()
    return run_agent("compute 2+2 and capital of Japan", scripted_llm, DEFAULT_TOOLS, (), lambda: float(next(ticks)))[1]


def test_roundtrip_preserves_every_entry(tmp_path):
    log = sample_log()
    path = save_log(log, tmp_path / "nested" / "run.jsonl")
    assert load_log(path) == log
    assert verify_chain(load_log(path)).ok


def test_unicode_and_nested_payloads_survive(tmp_path):
    log = append_entry((), {"text": "வணக்கம் – café", "nested": {"a": [1, 2.5, None, True]}}, 1.0)
    assert load_log(save_log(log, tmp_path / "u.jsonl")) == log


def test_file_is_one_json_object_per_line(tmp_path):
    log = sample_log()
    lines = save_log(log, tmp_path / "r.jsonl").read_text().splitlines()
    assert len(lines) == len(log)


def test_editing_the_file_on_disk_is_detected(tmp_path):
    log = sample_log()
    batches = (AnchoredBatch(batch_root(log, 0, len(log)), 0, len(log)),)
    path = save_log(log, tmp_path / "r.jsonl")
    path.write_text(path.read_text().replace("Tokyo", "Kyoto"))
    report = verify_against_chain(load_log(path), batches)
    assert not report.ok and report.first_bad_index is not None


def test_empty_log_roundtrip(tmp_path):
    assert load_log(save_log((), tmp_path / "e.jsonl")) == ()
