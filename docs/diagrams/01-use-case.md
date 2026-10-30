# 01. Use case diagram

**Notation:** UML use case (drawn with Mermaid flowchart notation)  
**Project:** Auditable AI Agents

## What it shows

Who uses the system and what each actor can do. The attacker is outside the system: they act on the stored log file, and the verifier is what notices.

## Diagram

```mermaid
flowchart LR
  operator["«actor»<br/>Operator"]
  auditor["«actor»<br/>Auditor / Verifier"]
  attacker["«actor»<br/>Attacker"]
  llm["«actor»<br/>Language model"]
  chain["«actor»<br/>Blockchain"]
  logfile[("Stored log file")]
  subgraph system["Auditable Agents system"]
    uc1([Run agent task])
    uc2([Record step in audit log])
    uc3([Call tool])
    uc4([Anchor batch on chain])
    uc5([Verify log against chain])
    uc6([Locate altered entry or batch])
    uc7([Check hash chain offline])
    uc8([Verify one entry by Merkle proof])
    uc9([Choose model])
  end
  operator --- uc1
  operator --- uc4
  operator --- uc9
  auditor --- uc5
  auditor --- uc7
  auditor --- uc8
  uc1 -. include .-> uc2
  uc1 -. include .-> uc3
  uc5 -. include .-> uc6
  uc1 --- llm
  uc4 --- chain
  uc5 --- chain
  uc8 --- chain
  uc2 --> logfile
  uc5 --> logfile
  uc7 --> logfile
  attacker -. "edits, deletes, rewrites" .-> logfile
```

![Use case diagram](images/01-use-case.png)

## Where it comes from

`run_agent` (Run agent task, Record step, Call tool), `anchor_pending` (Anchor batch), `verify_against_chain` (Verify and Locate), `scripts/verify_log.py` (offline check), `verifyInclusion` (Merkle proof on-chain), the three model adapters (Choose model).
