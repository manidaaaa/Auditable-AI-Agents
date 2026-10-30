# 11. Activity diagram: the anchoring pipeline

**Notation:** UML activity (flow)  
**Project:** Auditable AI Agents

## What it shows

How `anchor_pending` decides what to anchor and sends one transaction per new batch.

## Diagram

```mermaid
flowchart TD
  start([Start]) --> read["Read batches already on the contract"]
  read --> cnt["anchored = end of last batch, or 0 if none"]
  cnt --> plan["plan_batches(total, anchored, batch size, flush)"]
  plan --> any{"Any new batches?"}
  any -- no --> none([Return empty list])
  any -- yes --> next["Take the next planned batch"]
  next --> root["Compute the Merkle root of its entry hashes"]
  root --> tx["Send anchor(root, count) transaction"]
  tx --> wait["Wait for the receipt"]
  wait --> rec["Record batch id and gas used"]
  rec --> more{"More planned batches?"}
  more -- yes --> next
  more -- no --> done([Return receipts])
```

![Activity diagram: the anchoring pipeline](images/11-activity-anchoring.png)

## Where it comes from

`anchor_pending` in `src/app/chain_client.py` and `plan_batches` in `src/domain/audit.py`. A full batch is always anchored; a final partial batch only when `flush` is true.
