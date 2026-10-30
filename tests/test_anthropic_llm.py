"""Tests the Claude adapter against a fake SDK client (no network, no API key)."""
import itertools
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.anthropic_llm import make_anthropic_llm
from domain.agent import DEFAULT_TOOLS, run_agent
from domain.chain import verify_chain


def block(type_, **fields):
    return SimpleNamespace(type=type_, **fields)


def reply(content, stop_reason):
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
        model="claude-opus-5-5",
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        _request_id="req_fake",
    )


class FakeClient:
    def __init__(self, replies):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._replies = iter(replies)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return next(self._replies)


def test_tool_loop_round_trip_and_audit_log():
    thinking = block("thinking", thinking="", signature="sig")
    first = [thinking, block("tool_use", id="toolu_1", name="calculator", input={"expression": "6*7"})]
    client = FakeClient([reply(first, "tool_use"), reply([block("text", text="The answer is 42.")], "end_turn")])
    llm = make_anthropic_llm(client)
    ticks = itertools.count()

    answer, log = run_agent("compute 6*7", llm, DEFAULT_TOOLS, (), lambda: float(next(ticks)))

    assert answer == "The answer is 42."
    assert verify_chain(log).ok
    second_call = client.calls[1]["messages"]
    assert second_call[1] == {"role": "assistant", "content": first}  # raw blocks (incl. thinking) replayed unchanged
    assert second_call[2]["content"] == [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "42"}]
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["tool_choice"] == {"type": "auto", "disable_parallel_tool_use": True}
    llm_entries = [e.payload["action"] for e in log if e.payload["type"] == "llm_response"]
    assert llm_entries[0]["meta"]["request_id"] == "req_fake" and llm_entries[0]["tool"] == "calculator"


def test_tool_error_is_marked_in_api_message():
    first = [block("tool_use", id="toolu_9", name="calculator", input={"expression": "1/0"})]
    client = FakeClient([reply(first, "tool_use"), reply([block("text", text="Cannot divide by zero.")], "end_turn")])
    run_agent("compute 1/0", make_anthropic_llm(client), DEFAULT_TOOLS, (), lambda: 0.0)
    result = client.calls[1]["messages"][2]["content"][0]
    assert result["is_error"] is True and result["content"].startswith("error: ")


def test_refusal_becomes_a_logged_final_answer():
    client = FakeClient([reply([], "refusal")])
    answer, log = run_agent("x", make_anthropic_llm(client), DEFAULT_TOOLS, (), lambda: 0.0)
    assert "refused" in answer and log[-1].payload["type"] == "final"
