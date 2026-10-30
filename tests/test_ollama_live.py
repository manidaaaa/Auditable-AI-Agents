"""Real local-LLM run. Skipped unless an Ollama server with qwen3:8b is reachable."""
import itertools
import json
import urllib.request

import pytest

from app.ollama_llm import DEFAULT_MODEL, DEFAULT_URL, make_ollama_llm
from domain.agent import DEFAULT_TOOLS, run_agent
from domain.chain import verify_chain


def model_available():
    try:
        with urllib.request.urlopen(f"{DEFAULT_URL}/api/tags", timeout=2) as r:
            return any(m["name"] == DEFAULT_MODEL for m in json.loads(r.read())["models"])
    except Exception:
        return False


pytestmark = [pytest.mark.live, pytest.mark.skipif(not model_available(), reason="Ollama / qwen3:8b not available")]


def test_real_model_completes_the_task_with_a_valid_audit_log():
    ticks = itertools.count()
    task = "Please compute 12*(3+4) and find the capital of Japan."
    answer, log = run_agent(task, make_ollama_llm(), DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    assert "84" in answer and "Tokyo" in answer
    assert verify_chain(log).ok
    tools_called = [e.payload["tool"] for e in log if e.payload["type"] == "tool_call"]
    assert tools_called == ["calculator", "lookup_capital"]
    meta = next(e.payload["action"]["meta"] for e in log if e.payload["type"] == "llm_response")
    assert meta["model"].startswith("qwen3")
