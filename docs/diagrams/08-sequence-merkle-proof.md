# 08. Sequence diagram: proving one entry belongs to a batch

**Notation:** UML sequence  
**Project:** Auditable AI Agents

## What it shows

How a single entry is proved to be in an anchored batch, with the Python code producing the proof and the contract checking it on-chain.

## Diagram

```mermaid
sequenceDiagram
  actor Auditor
  participant Merkle as merkle_proof
  participant Contract as AuditAnchor
  Auditor->>Merkle: merkle_proof(entry hashes, index)
  Merkle-->>Auditor: sibling hashes and sides
  Auditor->>Contract: verifyInclusion(agent, batchId, entryHash, siblings, sides)
  Contract->>Contract: leaf = sha256 of 0x00 then entryHash
  loop each proof step
    Contract->>Contract: node = sha256 of 0x01 then left then right
  end
  Contract->>Contract: compare result with the stored root
  Contract-->>Auditor: true or false
```

![Sequence diagram: proving one entry belongs to a batch](images/08-sequence-merkle-proof.png)

## Where it comes from

`merkle_proof` in `src/domain/merkle.py` and `verifyInclusion` in the contract. Both use the 0x00 leaf and 0x01 node prefixes, and the Hardhat tests check that every Python proof for trees of 1 to 100 entries verifies on-chain.
