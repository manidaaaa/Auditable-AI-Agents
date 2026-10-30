"""Local LLM for the agent: any tool-calling model served by Ollama (no API key, nothing leaves the machine).

Same signature as `scripted_llm`: `llm(messages) -> action`. Uses only the standard library.
"""
from __future__ import annotations

import json
import re
import urllib.request
from typing import Any, Callable, Mapping, Sequence

from domain.agent import DEFAULT_SYSTEM_PROMPT, DEFAULT_TOOL_SPECS, LLM, Action, Message

DEFAULT_MODEL = "qwen3:8b"
DEFAULT_URL = "http://127.0.0.1:11434"
Post = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def http_post(url: str, body: Mapping[str, Any]) -> Mapping[str, Any]:
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())


def _stringify(result: Any) -> str:
    return result if isinstance(result, str) else json.dumps(result)


def to_ollama_messages(messages: Sequence[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
    last_tool = ""
    for message in messages:
        role, content = message["role"], message["content"]
        if role == "user":
            out.append({"role": "user", "content": content})
        elif role == "assistant":
            last_tool = content["tool"]
            out.append(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"function": {"name": content["tool"], "arguments": content.get("args", {})}}],
                }
            )
        else:
            out.append({"role": "tool", "tool_name": last_tool, "content": _stringify(content)})
    return out


def make_ollama_llm(
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_URL,
    post: Post = http_post,
    tool_specs: Sequence[Mapping[str, Any]] = DEFAULT_TOOL_SPECS,
    temperature: float = 0.0,
    seed: int = 42,
) -> LLM:
    tools = [
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}}
        for t in tool_specs
    ]
    options = {"temperature": temperature, "seed": seed}

    def llm(messages: Sequence[Message]) -> Action:
        reply = post(
            f"{base_url}/api/chat",
            {
                "model": model,
                "messages": to_ollama_messages(messages),
                "tools": tools,
                "stream": False,
                "think": False,
                "options": options,
            },
        )
        message = reply["message"]
        meta = {
            "model": reply.get("model", model),
            "done_reason": reply.get("done_reason"),
            "input_tokens": reply.get("prompt_eval_count"),
            "output_tokens": reply.get("eval_count"),
            "options": options,
        }
        calls = message.get("tool_calls") or []
        if calls:
            function = calls[0]["function"]
            return {"type": "tool_call", "tool": function["name"], "args": dict(function.get("arguments") or {}), "meta": meta}
        text = re.sub(r"<think>.*?</think>", "", message.get("content", ""), flags=re.S).strip()
        return {"type": "final", "content": text, "meta": meta}

    return llm
