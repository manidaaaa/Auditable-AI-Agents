# 13. State diagram: agent run

**Notation:** UML state machine  
**Project:** Auditable AI Agents

## What it shows

The states of one agent run and the ways it can end.

## Diagram

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> AwaitingModel : task received and logged
  AwaitingModel --> RunningTool : action is a tool call
  RunningTool --> AwaitingModel : result or error logged
  AwaitingModel --> Finished : action is final
  AwaitingModel --> StoppedAtLimit : step limit reached
  AwaitingModel --> Refused : model refuses
  Refused --> Finished : refusal logged as final answer
  StoppedAtLimit --> Finished : stopped message logged
  Finished --> [*]
```

![State diagram: agent run](images/13-state-agent-run.png)

## Where it comes from

`run_agent` in `src/domain/agent.py`. The refusal path comes from the Claude adapter, which turns a refusal into a final answer so it is still logged.
