# 17. Flow diagram: which check catches which attack

**Notation:** Decision flow  
**Project:** Auditable AI Agents

## What it shows

For each kind of tampering, whether the hash chain alone catches it and what the on-chain roots add.

## Diagram

```mermaid
flowchart TD
  start([Attacker changes the stored log]) --> kind{"What was done?"}
  kind -- "Edit entry content, timestamp or stored hash" --> e1["Entry hash no longer matches"]
  kind -- "Delete, insert or reorder entries" --> e2["Index or link breaks"]
  kind -- "Truncate the end" --> e3["Shorter chain is still valid"]
  kind -- "Rewrite an entry and recompute later hashes" --> e4["Chain is self-consistent"]
  e1 --> c1(["Caught by hash chain: exact entry"])
  e2 --> c2(["Caught by hash chain: at or near the change"])
  e3 --> c3(["Caught only by on-chain roots: log shorter than anchored range"])
  e4 --> c4(["Caught only by on-chain roots: batch range"])
  e1 --> r["On-chain roots also differ"]
  e2 --> r
```

![Flow diagram: which check catches which attack](images/17-attack-detection-flow.png)

## Where it comes from

`tests/test_fuzz_tamper.py` runs each attack on 300 random logs and `docs/TESTING.md` section 7 lists the evidence. Entries after the last anchor are not covered by the roots until the next batch is anchored.
