# 09. Activity diagram: the agent loop

**Notation:** UML activity (flow)  
**Project:** Auditable AI Agents

## What it shows

The control flow of `run_agent`, including error handling and the step limit.

## Diagram

```mermaid
flowchart TD
  start([Start]) --> t["Append task entry"]
  t --> chk{"Steps used below limit?"}
  chk -- no --> lim["Append final entry: stopped, step limit reached"]
  lim --> done([Return answer and log])
  chk -- yes --> ask["Ask the model for an action"]
  ask --> r["Append llm_response entry"]
  r --> fin{"Action is final?"}
  fin -- yes --> f["Append final entry"]
  f --> done
  fin -- no --> tc["Append tool_call entry"]
  tc --> run["Run the tool"]
  run --> err{"Tool raised an error?"}
  err -- no --> res["Append tool_result entry"]
  err -- yes --> te["Append tool_error entry"]
  res --> msg["Add assistant action and tool result to messages"]
  te --> msg
  msg --> chk
```

![Activity diagram: the agent loop](images/09-activity-agent-loop.png)

## Where it comes from

`run_agent` in `src/domain/agent.py`. Default step limit is 10.
