import itertools

import pytest

from domain.agent import (
    DEFAULT_TOOLS,
    calculator,
    lookup_capital,
    plan_from_task,
    run_agent,
    scripted_llm,
    word_count,
)
from domain.chain import verify_chain


@pytest.mark.parametrize(
    "expression, expected",
    [("1+2", 3), ("2*(3+4)", 14), ("2**10", 1024), ("-5+2", -3), ("10/4", 2.5), ("12*(3+4)", 84), ("7", 7)],
)
def test_calculator_values(expression, expected):
    assert calculator({"expression": expression}) == expected


@pytest.mark.parametrize("bad", ["abs(1)", "x+1", "__import__('os')", "1; 2", "[1]", "'a'*3", "lambda: 1"])
def test_calculator_rejects_everything_but_arithmetic(bad):
    with pytest.raises((ValueError, SyntaxError)):
        calculator({"expression": bad})


def test_word_count():
    assert word_count({"text": "auditable agents leave a trail"}) == 5
    assert word_count({"text": ""}) == 0
    assert word_count({"text": "  spaced   out  "}) == 2


def test_lookup_capital_is_case_insensitive_and_has_fallback():
    assert lookup_capital({"country": "JAPAN"}) == "Tokyo"
    assert lookup_capital({"country": "india"}) == "New Delhi"
    assert lookup_capital({"country": "Atlantis"}) == "unknown"


def test_plan_from_task_finds_each_tool_in_order():
    plan = plan_from_task("Please compute 12*(3+4) and count words in 'a b c' and find the capital of Japan.")
    assert [name for name, _ in plan] == ["calculator", "word_count", "lookup_capital"]
    assert plan[0][1] == {"expression": "12*(3+4)"} and plan[2][1] == {"country": "Japan"}


def test_plan_from_task_empty_when_nothing_matches():
    assert plan_from_task("hello there") == ()


def test_scripted_llm_calls_tools_then_answers():
    task = [{"role": "user", "content": "compute 1+1 and capital of France"}]
    first = scripted_llm(task)
    assert first["type"] == "tool_call" and first["tool"] == "calculator"
    second = scripted_llm(task + [{"role": "assistant", "content": first}, {"role": "tool", "content": 2}])
    assert second["tool"] == "lookup_capital"
    done = scripted_llm(task + [{"role": "tool", "content": 2}, {"role": "tool", "content": "Paris"}])
    assert done["type"] == "final" and "Paris" in done["content"]


def test_unknown_tool_is_logged_as_error_not_crash():
    llm = iter([{"type": "tool_call", "tool": "rm_rf", "args": {}}, {"type": "final", "content": "done"}])
    ticks = itertools.count()
    answer, log = run_agent("x", lambda m: next(llm), DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    assert answer == "done"
    assert any(e.payload["type"] == "tool_error" and e.payload["tool"] == "rm_rf" for e in log)
    assert verify_chain(log).ok


def test_log_has_strictly_increasing_indices_and_timestamps():
    ticks = itertools.count()
    _, log = run_agent("compute 1+1", scripted_llm, DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    assert [e.index for e in log] == list(range(len(log)))
    assert [e.timestamp for e in log] == sorted(e.timestamp for e in log)
