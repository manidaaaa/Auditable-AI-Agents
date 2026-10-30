# 05. Sequence diagram: one agent run

**Notation:** UML sequence  
**Project:** Auditable AI Agents

## What it shows

What happens, in order, when the agent handles a task. Every arrow into the audit log is one appended, hash-chained entry.

## Diagram

```mermaid
sequenceDiagram
  actor Operator
  participant Agent as run_agent
  participant Model as LLM function
  participant Tool as Tool function
  participant Log as Audit log
  Operator->>Agent: task
  Agent->>Log: append task entry
  loop until final answer or step limit
    Agent->>Model: messages
    Model-->>Agent: action
    Agent->>Log: append llm_response entry
    alt action is final
      Agent->>Log: append final entry
      Agent-->>Operator: answer and new log
    else action is a tool call
      Agent->>Log: append tool_call entry
      Agent->>Tool: args
      alt tool succeeds
        Tool-->>Agent: result
        Agent->>Log: append tool_result entry
      else tool raises an error
        Tool-->>Agent: error
        Agent->>Log: append tool_error entry
      end
    end
  end
  Note over Agent,Log: if the step limit is reached a final entry saying stopped is appended
```

![Sequence diagram: one agent run](images/05-sequence-agent-run.png)

## Where it comes from

`run_agent` in `src/domain/agent.py`. Entry types: `task`, `llm_response`, `tool_call`, `tool_result`, `tool_error`, `final`.
