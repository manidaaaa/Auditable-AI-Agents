# 07. Sequence diagram: verifying a stored log

**Notation:** UML sequence  
**Project:** Auditable AI Agents

## What it shows

How an auditor checks a log file against the roots on the blockchain.

## Diagram

```mermaid
sequenceDiagram
  actor Auditor
  participant Store as logstore
  participant Client as chain_client
  participant Contract as AuditAnchor
  participant Verifier as verify_against_chain
  Auditor->>Store: load_log(path)
  Store-->>Auditor: entries
  Auditor->>Client: read_batches(contract, agent)
  Client->>Contract: batchCount and getBatch
  Contract-->>Client: anchored batches
  Client-->>Auditor: AnchoredBatch list
  Auditor->>Verifier: entries and batches
  Verifier->>Verifier: verify_chain over every entry
  loop each anchored batch
    Verifier->>Verifier: recompute Merkle root from stored entry hashes
    Verifier->>Verifier: compare with the on-chain root
  end
  Verifier-->>Auditor: AuditReport INTACT or TAMPERING DETECTED
```

![Sequence diagram: verifying a stored log](images/07-sequence-verification.png)

## Where it comes from

`load_log` in `src/app/logstore.py`, `read_batches` in `src/app/chain_client.py`, `verify_against_chain` in `src/domain/audit.py`.
