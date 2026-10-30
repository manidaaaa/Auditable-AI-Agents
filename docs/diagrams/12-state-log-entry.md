# 12. State diagram: life of a log entry

**Notation:** UML state machine  
**Project:** Auditable AI Agents

## What it shows

The states an entry passes through from creation to verification, including what happens when the stored file is altered and later restored.

## Diagram

```mermaid
stateDiagram-v2
  [*] --> Created : make_entry
  Created --> InLog : append_entry
  InLog --> Saved : save_log
  Saved --> Unanchored : waiting for the batch to fill or be flushed
  Unanchored --> Anchored : anchor transaction mined
  Anchored --> Verified : verify passes
  Verified --> Suspect : stored file altered
  Anchored --> Suspect : stored file altered and verify fails
  Suspect --> Verified : original restored and verify passes
  Verified --> [*]
```

![State diagram: life of a log entry](images/12-state-log-entry.png)

## Where it comes from

Matches the demo: edit, consistent rewrite and truncation each move the log to Suspect, and restoring the original returns it to Verified. Entries in Unanchored are not yet protected against a consistent rewrite.
