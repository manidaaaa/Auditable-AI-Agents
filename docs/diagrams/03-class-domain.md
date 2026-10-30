# 03. Class diagram: data model and modules

**Notation:** UML class  
**Project:** Auditable AI Agents

## What it shows

The immutable data types (frozen dataclasses) and the modules of pure functions that create and check them. Function modules are shown as classes marked `module` because Python modules group functions, not objects.

## Diagram

```mermaid
classDiagram
  class LogEntry {
    <<frozen dataclass>>
    +int index
    +float timestamp
    +Mapping payload
    +str prev_hash
    +str entry_hash
  }
  class ChainVerification {
    <<frozen dataclass>>
    +bool ok
    +int first_bad_index
    +str reason
  }
  class AnchoredBatch {
    <<frozen dataclass>>
    +str root
    +int first_index
    +int count
  }
  class AuditReport {
    <<frozen dataclass>>
    +bool ok
    +bool chain_ok
    +str chain_reason
    +int first_bad_index
    +tuple bad_batches
    +bool truncated
    +int unanchored_entries
    +tuple notes
  }
  class AnchorReceipt {
    <<frozen dataclass>>
    +int batch_id
    +int first_index
    +int count
    +str root
    +int gas_used
  }
  class chain_py {
    <<module>>
    +compute_entry_hash()
    +make_entry()
    +append_entry()
    +verify_chain()
  }
  class merkle_py {
    <<module>>
    +merkle_root()
    +merkle_proof()
    +verify_proof()
  }
  class audit_py {
    <<module>>
    +plan_batches()
    +batch_root()
    +verify_against_chain()
  }
  class agent_py {
    <<module>>
    +run_agent()
    +scripted_llm()
    +plan_from_task()
    +calculator()
    +word_count()
    +lookup_capital()
  }
  chain_py ..> LogEntry : creates
  chain_py ..> ChainVerification : returns
  audit_py ..> AnchoredBatch : reads
  audit_py ..> AuditReport : returns
  audit_py ..> merkle_py : uses
  audit_py ..> chain_py : uses
  agent_py ..> chain_py : appends entries
  agent_py ..> LogEntry : builds log of
```

![Class diagram: data model and modules](images/03-class-domain.png)

## Where it comes from

`src/domain/chain.py`, `merkle.py`, `audit.py`, `agent.py`; `AnchorReceipt` lives in `src/app/chain_client.py`. All data types are `@dataclass(frozen=True)`, so a log is a tuple that is passed along and returned, never modified.
