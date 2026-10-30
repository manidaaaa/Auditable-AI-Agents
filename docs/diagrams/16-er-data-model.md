# 16. Entity-relationship diagram: data model

**Notation:** ER (data model)  
**Project:** Auditable AI Agents

## What it shows

The data and how it is split: log entries live off-chain in a file, batches live on-chain in the contract, and each batch covers a range of entries.

## Diagram

```mermaid
erDiagram
  AGENT_RUN ||--|{ LOG_ENTRY : produces
  LOG_ENTRY |o--o| LOG_ENTRY : "prev_hash points to"
  AGENT_ACCOUNT ||--o{ BATCH : anchors
  BATCH ||--|{ LOG_ENTRY : covers
  AGENT_RUN {
    string task
    string model
  }
  LOG_ENTRY {
    int index PK
    float timestamp
    json payload
    string prev_hash
    string entry_hash
  }
  BATCH {
    int batch_id PK
    string root
    int first_index
    int count
    int timestamp
  }
  AGENT_ACCOUNT {
    string address PK
  }
```

![Entity-relationship diagram: data model](images/16-er-data-model.png)

## Where it comes from

`LOG_ENTRY` is stored in the JSON Lines file (off-chain). `BATCH` is the `Batch` struct in the contract (on-chain, per sender address). `covers` is the index range `first_index` to `first_index + count - 1`.
