# 10. Activity diagram: the verification algorithm

**Notation:** UML activity (flow)  
**Project:** Auditable AI Agents

## What it shows

The two checks inside verification: the hash chain first, then each batch root against the blockchain, and how the result is decided.

## Diagram

```mermaid
flowchart TD
  start([Start]) --> loop1["Take the next entry"]
  loop1 --> a{"Index equals its position?"}
  a -- no --> bad1["Chain broken: sequence, entry inserted removed or reordered"]
  a -- yes --> b{"prev_hash equals previous entry hash?"}
  b -- no --> bad2["Chain broken: link"]
  b -- yes --> c{"entry_hash equals recomputed hash?"}
  c -- no --> bad3["Chain broken: content changed"]
  c -- yes --> more{"More entries?"}
  more -- yes --> loop1
  more -- no --> okchain["Chain consistent"]
  bad1 --> batches
  bad2 --> batches
  bad3 --> batches
  okchain --> batches["Check each anchored batch"]
  batches --> d{"Batch reaches past the end of the log?"}
  d -- yes --> trunc["Mark truncated and batch bad"]
  d -- no --> e{"Recomputed root equals on-chain root?"}
  e -- no --> badb["Mark batch bad"]
  e -- yes --> nextb{"More batches?"}
  trunc --> nextb
  badb --> nextb
  nextb -- yes --> batches
  nextb -- no --> decide{"Chain consistent and no bad batch?"}
  decide -- yes --> intact([INTACT])
  decide -- no --> tamper([TAMPERING DETECTED])
```

![Activity diagram: the verification algorithm](images/10-activity-verification.png)

## Where it comes from

`verify_chain` in `src/domain/chain.py` and `verify_against_chain` in `src/domain/audit.py`. If only a batch fails, the report can give the batch range but not the exact entry.
