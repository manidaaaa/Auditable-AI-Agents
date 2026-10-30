import itertools
import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from domain.agent import DEFAULT_TOOLS, calculator, run_agent, scripted_llm
from domain.audit import AnchoredBatch, batch_root, plan_batches, verify_against_chain
from domain.chain import compute_entry_hash, verify_chain

TASK = "Please compute 12*(3+4) and count words in 'a b c' and find the capital of Japan."


def clock():
    counter = itertools.count()
    return lambda: 1000.0 + next(counter)


def run(task=TASK):
    return run_agent(task, scripted_llm, DEFAULT_TOOLS, (), clock())


def anchored(entries, size=5):
    return tuple(AnchoredBatch(batch_root(entries, f, c), f, c) for f, c in plan_batches(len(entries), 0, size, True))


def test_agent_answers_and_logs_every_step():
    answer, log = run()
    assert answer == "Results: 84; 3; Tokyo"
    types = [e.payload["type"] for e in log]
    assert types[0] == "task" and types[-1] == "final"
    assert types.count("tool_call") == types.count("tool_result") == 3
    assert verify_chain(log).ok


def test_calculator_rejects_unsafe_input():
    with pytest.raises(ValueError):
        calculator({"expression": "__import__('os').system('echo hi')"})


def test_tool_error_is_logged_not_raised():
    tools = {**DEFAULT_TOOLS, "calculator": lambda args: 1 / 0}
    answer, log = run_agent("compute 1/0", scripted_llm, tools, (), clock())
    assert any(e.payload["type"] == "tool_error" for e in log)
    assert verify_chain(log).ok


def test_step_limit_is_logged():
    forever = lambda messages: {"type": "tool_call", "tool": "word_count", "args": {"text": "x"}}
    answer, log = run_agent("loop", forever, DEFAULT_TOOLS, (), clock(), max_steps=3)
    assert answer.startswith("stopped") and log[-1].payload["type"] == "final"


def test_plan_batches():
    assert plan_batches(12, 0, 5, True) == ((0, 5), (5, 5), (10, 2))
    assert plan_batches(12, 0, 5, False) == ((0, 5), (5, 5))
    assert plan_batches(12, 10, 5, True) == ((10, 2),)
    assert plan_batches(5, 5, 5, True) == ()


def test_untouched_log_is_intact():
    _, log = run()
    report = verify_against_chain(log, anchored(log))
    assert report.ok and report.unanchored_entries == 0


def test_edit_is_located_exactly():
    _, log = run()
    batches = anchored(log)
    edited = replace(log[3], payload={"type": "task", "content": "evil"})
    report = verify_against_chain(log[:3] + (edited,) + log[4:], batches)
    # stored entry hashes are unchanged, so roots still match; the hash chain is what catches an in-place edit
    assert not report.ok and report.first_bad_index == 3 and report.bad_batches == ()


def test_consistent_rewrite_passes_chain_but_fails_on_chain_roots():
    _, log = run()
    batches = anchored(log)
    forged = [log[0], log[1], log[2]]
    for e in (replace(log[3], payload={"type": "task", "content": "evil"}), *log[4:]):
        prev = forged[-1].entry_hash
        forged.append(replace(e, prev_hash=prev, entry_hash=compute_entry_hash(e.index, e.timestamp, e.payload, prev)))
    assert verify_chain(tuple(forged)).ok  # hash chain alone is fooled
    report = verify_against_chain(tuple(forged), batches)
    assert not report.ok and report.chain_ok and 0 in report.bad_batches


def test_truncation_is_detected():
    _, log = run()
    report = verify_against_chain(log[:-2], anchored(log))
    assert not report.ok and report.truncated


def test_entries_after_last_anchor_are_reported_not_flagged():
    _, log = run()
    report = verify_against_chain(log, anchored(log)[:-1])
    assert report.ok and report.unanchored_entries == 2
