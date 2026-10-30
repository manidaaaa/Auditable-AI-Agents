# 14. State diagram: verification outcome

**Notation:** UML state machine  
**Project:** Auditable AI Agents

## What it shows

The states of one verification run and the possible results.

## Diagram

```mermaid
stateDiagram-v2
  [*] --> CheckingChain
  CheckingChain --> ChainBroken : index, link or hash mismatch
  CheckingChain --> ChainConsistent : all entries pass
  ChainBroken --> CheckingBatches : still compare roots
  ChainConsistent --> CheckingBatches
  CheckingBatches --> Intact : chain consistent and every root matches
  CheckingBatches --> RootMismatch : a recomputed root differs
  CheckingBatches --> Truncated : log shorter than anchored range
  ChainBroken --> TamperingDetected : exact entry reported
  RootMismatch --> TamperingDetected : batch range reported
  Truncated --> TamperingDetected : missing entries reported
  Intact --> [*]
  TamperingDetected --> [*]
```

![State diagram: verification outcome](images/14-state-verification.png)

## Where it comes from

`verify_against_chain` returns an `AuditReport` whose `ok`, `chain_ok`, `bad_batches` and `truncated` fields encode these states.
