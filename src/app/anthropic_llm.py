"""Real LLM for the agent: Claude through the official Anthropic SDK.

Returns a function with the same signature as `scripted_llm`: `llm(messages) -> action`.
The Anthropic API key is read from the ANTHROPIC_API_KEY environment variable by the SDK.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from domain.agent import DEFAULT_SYSTEM_PROMPT, DEFAULT_TOOL_SPECS, Action, LLM, Message

DEFAULT_MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT


def _stringify(result: Any) -> str:
    return result if isinstance(result, str) else json.dumps(result)


def make_anthropic_llm(
    client: Any | None = None,
    *,
    model: str = DEFAULT_MODEL,
    tool_specs: Sequence[Mapping[str, Any]] = DEFAULT_TOOL_SPECS,
    max_tokens: int = 4096,
    effort: str = "low",
) -> LLM:
    """Build an `llm` callable for ONE agent run.

    The raw assistant content (including thinking blocks) is kept in a closure and replayed
    unchanged on later turns, as the API requires for thinking models during tool use.
    """
    if client is None:
        import anthropic

        client = anthropic.Anthropic()
    raw_assistant: list[Any] = []

    def to_api_messages(messages: Sequence[Message]) -> list[dict[str, Any]]:
        api: list[dict[str, Any]] = []
        assistant_turns = 0
        for message in messages:
            role = message["role"]
            if role == "user":
                api.append({"role": "user", "content": message["content"]})
            elif role == "assistant":
                api.append({"role": "assistant", "content": raw_assistant[assistant_turns]})
                assistant_turns += 1
            else:  # tool result answers the tool_use of the assistant turn just before it
                tool_use = next(b for b in raw_assistant[assistant_turns - 1] if b.type == "tool_use")
                content = _stringify(message["content"])
                block = {"type": "tool_result", "tool_use_id": tool_use.id, "content": content}
                if content.startswith("error: "):
                    block["is_error"] = True
                api.append({"role": "user", "content": [block]})
        return api

    def llm(messages: Sequence[Message]) -> Action:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            tools=list(tool_specs),
            tool_choice={"type": "auto", "disable_parallel_tool_use": True},
            output_config={"effort": effort},
            messages=to_api_messages(messages),
        )
        meta = {
            "model": response.model,
            "request_id": getattr(response, "_request_id", None),
            "stop_reason": response.stop_reason,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        tool_use = next((b for b in response.content if b.type == "tool_use"), None)
        if tool_use is not None and response.stop_reason == "tool_use":
            raw_assistant.append(response.content)
            return {"type": "tool_call", "tool": tool_use.name, "args": dict(tool_use.input), "meta": meta}
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if response.stop_reason == "refusal":
            text = text or "refused by the model's safety systems"
        raw_assistant.append(response.content)
        return {"type": "final", "content": text, "meta": meta}

    return llm
