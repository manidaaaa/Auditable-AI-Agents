# 06. Sequence diagram: anchoring batches on the chain

**Notation:** UML sequence  
**Project:** Auditable AI Agents

## What it shows

How the demo starts a local chain, deploys the contract and anchors new batches of log entries.

## Diagram

```mermaid
sequenceDiagram
  participant Demo as run_demo
  participant Client as chain_client
  participant Audit as audit and merkle
  participant Node as Hardhat node
  participant Contract as AuditAnchor
  Demo->>Client: local_chain()
  Client->>Node: start npx hardhat node
  Client-->>Demo: Web3 connection
  Demo->>Client: deploy_anchor()
  Client->>Node: deploy contract bytecode
  Node-->>Client: contract address
  Demo->>Client: anchor_pending(entries, batch size)
  Client->>Contract: batchCount and getBatch (free calls)
  Contract-->>Client: batches already anchored
  Client->>Audit: plan_batches(total, anchored, size, flush)
  Audit-->>Client: list of first index and count
  loop each new batch
    Client->>Audit: batch_root(entries, first, count)
    Audit-->>Client: Merkle root
    Client->>Contract: anchor(root, count) transaction
    Contract->>Contract: check count above zero and append Batch
    Contract-->>Client: BatchAnchored event and gas used
  end
  Client-->>Demo: AnchorReceipt list
```

![Sequence diagram: anchoring batches on the chain](images/06-sequence-anchoring.png)

## Where it comes from

`local_chain`, `deploy_anchor`, `anchor_pending` in `src/app/chain_client.py`; `plan_batches`, `batch_root` in `src/domain/audit.py`. What counts as already anchored is read from the chain, so running it twice never anchors a batch twice.
