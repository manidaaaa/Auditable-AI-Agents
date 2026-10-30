"""A small tool-using agent whose every step is written to a hash-chained audit log.

The model is any callable `llm(messages) -> action`. `ScriptedLLM` is a deterministic
stand-in so the demo and tests run offline; swap in a real LLM client with the same signature.
"""
from __future__ import annotations

import ast
import operator
import re
from typing import Any, Callable, Mapping, Sequence

from domain.chain import LogEntry, append_entry

Message = Mapping[str, Any]
Action = Mapping[str, Any]
LLM = Callable[[Sequence[Message]], Action]
Tool = Callable[[Mapping[str, Any]], Any]
Clock = Callable[[], float]

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def calculator(args: Mapping[str, Any]) -> float:
    return _eval_node(ast.parse(str(args["expression"]), mode="eval").body)


def word_count(args: Mapping[str, Any]) -> int:
    return len(str(args["text"]).split())


_FACTS = {"france": "Paris", "india": "New Delhi", "japan": "Tokyo", "canada": "Ottawa"}


def lookup_capital(args: Mapping[str, Any]) -> str:
    return _FACTS.get(str(args["country"]).lower(), "unknown")


DEFAULT_TOOLS: Mapping[str, Tool] = {
    "calculator": calculator,
    "word_count": word_count,
    "lookup_capital": lookup_capital,
}


def plan_from_task(task: str) -> tuple[tuple[str, dict[str, Any]], ...]:
    """Tool calls the stand-in LLM decides on, read from the task text."""
    plan: list[tuple[str, dict[str, Any]]] = []
    for expression in re.findall(r"compute ([0-9+\-*/(). ]+?)(?: and |\.|,|$)", task, re.I):
        plan.append(("calculator", {"expression": expression.strip()}))
    for text in re.findall(r"count words in '([^']*)'", task, re.I):
        plan.append(("word_count", {"text": text}))
    for country in re.findall(r"capital of ([A-Za-z]+)", task, re.I):
        plan.append(("lookup_capital", {"country": country}))
    return tuple(plan)


def scripted_llm(messages: Sequence[Message]) -> Action:
    """Deterministic stand-in for an LLM: call each planned tool once, then answer."""
    task = messages[0]["content"]
    results = [m["content"] for m in messages if m["role"] == "tool"]
    plan = plan_from_task(task)
    if len(results) < len(plan):
        tool, args = plan[len(results)]
        return {"type": "tool_call", "tool": tool, "args": args}
    return {"type": "final", "content": "Results: " + "; ".join(str(r) for r in results)}


def run_agent(
    task: str,
    llm: LLM,
    tools: Mapping[str, Tool],
    log: tuple[LogEntry, ...],
    clock: Clock,
    *,
    max_steps: int = 10,
) -> tuple[str, tuple[LogEntry, ...]]:
    """Run the agent loop, threading the audit log through every step. Returns (answer, new log)."""
    messages: list[Message] = [{"role": "user", "content": task}]
    log = append_entry(log, {"type": "task", "content": task}, clock())

    for _ in range(max_steps):
        action = dict(llm(tuple(messages)))
        log = append_entry(log, {"type": "llm_response", "action": action}, clock())

        if action["type"] == "final":
            log = append_entry(log, {"type": "final", "content": action["content"]}, clock())
            return str(action["content"]), log

        tool_name, args = action["tool"], action.get("args", {})
        log = append_entry(log, {"type": "tool_call", "tool": tool_name, "args": args}, clock())
        try:
            result: Any = tools[tool_name](args)
            log = append_entry(log, {"type": "tool_result", "tool": tool_name, "result": result}, clock())
        except Exception as error:  # a failing tool is an audited event, not a crash
            result = f"error: {error}"
            log = append_entry(log, {"type": "tool_error", "tool": tool_name, "error": str(error)}, clock())
        messages += [{"role": "assistant", "content": action}, {"role": "tool", "content": result}]

    answer = "stopped: step limit reached"
    return answer, append_entry(log, {"type": "final", "content": answer}, clock())
