# Auditable Agents

**Master of Engineering (Computer Science and Engineering)** — software workspace for a tamper-evident audit trail of LLM agent actions, anchored on a blockchain.

**Author:** Manikandan Sankaranarayanan · S Veersamy Chettiya College of Engineering · smak07.s@gmail.com  
**Working title:** Auditable AI Agents: An Immutable On-Chain Audit Trail for LLM Agent Actions

Concepts and plan: `docs/proposal/`. Locked choices: `docs/proposal/decisions.md`.  
Author profile: `references/personal-info.md`.

---

## Idea in one paragraph

An LLM agent's prompts, tool calls and results are logged as hash-chained entries. Batches of entry hashes are folded into a Merkle root and anchored on a blockchain. A verifier recomputes the hashes from the stored logs and compares them with the chain, so any edit, deletion, insertion or reordering is detected and located. Only hashes go on-chain; full logs stay off-chain.

---

## Quick start (Month 1)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m pytest -q tests
```

---

## Repository map

| Path | Purpose |
|------|---------|
| `docs/proposal` | Problem framing and locked decisions |
| `docs/literature` | Reading notes |
| `docs/methodology` | Methods and evaluation |
| `docs/thesis` | Long-form writing |
| `docs/notes` | Working notes and backlogs |
| `contracts` | Solidity smart contracts |
| `research/experiments` | Run logs and metrics |
| `research/data` | Raw / processed data (local dumps gitignored) |
| `src/core` | Hashing and serialisation primitives |
| `src/domain` | Log entries, hash chain, Merkle tree |
| `src/app` | Runnable entrypoints |
| `scripts` | Thin CLI wrappers |
| `tests` | Verification |
| `assets` | Figures and diagrams |
| `presentations` | Defence decks |

---

## Status

**Phase:** Month 1 — hash chain, Merkle tree and anchor contract draft.
