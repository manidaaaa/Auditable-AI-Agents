# UML and Flow Diagrams

**Project:** Auditable AI Agents  
Every diagram is a Mermaid file (`NN-name.md`). GitHub draws Mermaid blocks directly in the page. PNG and SVG copies for the Word report are in `images/`. All diagrams were checked against the code on 2026-10-30.

| # | Diagram | UML type | Shows |
|---|---|---|---|
| 01 | [Use case](01-use-case.md) | Use case | Actors and what each can do |
| 02 | [Component](02-component.md) | Component | Modules, layers and dependencies |
| 03 | [Class: data model and modules](03-class-domain.md) | Class | Immutable data types and function modules |
| 04 | [Class: contract and chain client](04-class-contract.md) | Class | `AuditAnchor`, `Batch`, event, Python client |
| 05 | [Sequence: agent run](05-sequence-agent-run.md) | Sequence | One agent run and every logged entry |
| 06 | [Sequence: anchoring](06-sequence-anchoring.md) | Sequence | Deploy, plan, anchor batches |
| 07 | [Sequence: verification](07-sequence-verification.md) | Sequence | Checking a stored log against the chain |
| 08 | [Sequence: Merkle proof](08-sequence-merkle-proof.md) | Sequence | Proving one entry is in a batch |
| 09 | [Activity: agent loop](09-activity-agent-loop.md) | Activity (flow) | Control flow of `run_agent` |
| 10 | [Activity: verification algorithm](10-activity-verification.md) | Activity (flow) | Hash chain check, then batch roots |
| 11 | [Activity: anchoring pipeline](11-activity-anchoring.md) | Activity (flow) | How `anchor_pending` decides and sends |
| 12 | [State: log entry](12-state-log-entry.md) | State machine | Created to Verified, and what raises suspicion |
| 13 | [State: agent run](13-state-agent-run.md) | State machine | Ways a run can end |
| 14 | [State: verification](14-state-verification.md) | State machine | Verification outcomes |
| 15 | [Deployment](15-deployment.md) | Deployment | What runs where |
| 16 | [Entity-relationship](16-er-data-model.md) | ER | Off-chain entries and on-chain batches |
| 17 | [Attack detection flow](17-attack-detection-flow.md) | Decision flow | Which check catches which attack |
| 18 | [Test architecture](18-test-architecture.md) | Map | Test suites and shared vectors |
| 19 | [Phase II plan](19-phase2-plan.md) | Gantt | Planned work next semester (illustrative dates, not yet done) |

## Notes

- **UML in Mermaid.** Mermaid has native class, sequence and state diagrams. Use case and component diagrams are drawn with its flowchart notation using UML conventions («actor», ovals for use cases, dotted «include» arrows), so they are UML in meaning rather than in the strictest drawing style.
- **Python modules as classes.** The code is mostly pure functions, so function modules appear in class diagrams as `«module»` boxes.
- **What is not drawn.** The planned dashboard and signed entries (Phase II) are not drawn as system parts; they appear only in the Gantt plan.

## Editing and re-rendering

Edit the Mermaid block in the `.md` file, then:

```bash
python scripts/render_diagrams.py            # all diagrams
python scripts/render_diagrams.py 10-activity-verification   # one diagram
```

The script needs mermaid-cli in `.tools/mermaid-cli` (kept out of git) and uses your installed Chrome in headless mode, with its profile inside `.tools`. If `.tools` is deleted, the Mermaid text still renders on GitHub; only the PNG and SVG copies need that tool.
