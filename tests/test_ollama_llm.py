"""Tests the Ollama adapter with a fake HTTP post (no server needed)."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.ollama_llm import make_ollama_llm, to_ollama_messages
from domain.agent import DEFAULT_TOOLS, run_agent
from domain.chain import verify_chain


def tool_reply(name, args):
    return {"model": "qwen3:8b", "done_reason": "stop", "prompt_eval_count": 30, "eval_count": 8,
            "message": {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}}


def text_reply(text):
    return {"model": "qwen3:8b", "done_reason": "stop", "prompt_eval_count": 40, "eval_count": 6,
            "message": {"role": "assistant", "content": text}}


def fake_post(replies):
    calls, it = [], iter(replies)

    def post(url, body):
        calls.append((url, body))
        return next(it)

    return post, calls


def test_tool_round_trip_and_audit_log():
    post, calls = fake_post([tool_reply("calculator", {"expression": "6*7"}), text_reply("<think>x</think>It is 42.")])
    ticks = itertools.count()
    answer, log = run_agent("compute 6*7", make_ollama_llm(post=post), DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    assert answer == "It is 42."
    assert verify_chain(log).ok
    url, first = calls[0]
    assert url.endswith("/api/chat") and first["stream"] is False and first["think"] is False
    assert first["tools"][0]["function"]["name"] == "calculator"
    followup = calls[1][1]["messages"]
    assert followup[2]["tool_calls"][0]["function"] == {"name": "calculator", "arguments": {"expression": "6*7"}}
    assert followup[3] == {"role": "tool", "tool_name": "calculator", "content": "42"}
    llm_actions = [e.payload["action"] for e in log if e.payload["type"] == "llm_response"]
    assert llm_actions[0]["meta"]["input_tokens"] == 30 and llm_actions[0]["meta"]["options"]["seed"] == 42


def test_message_conversion_starts_with_system_prompt():
    msgs = to_ollama_messages([{"role": "user", "content": "hi"}])
    assert msgs[0]["role"] == "system" and msgs[1] == {"role": "user", "content": "hi"}
