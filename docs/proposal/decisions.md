# Locked decisions — Month 1

Updated as we proceed. Change only deliberately.

**Author:** Manikandan Sankaranarayanan · M.E. (CSE) · S Veersamy Chettiya College of Engineering · smak07.s@gmail.com  
**Profile:** `references/personal-info.md`

| Decision | Choice | Why |
|----------|--------|-----|
| Title | Auditable AI Agents: An Immutable On-Chain Audit Trail for LLM Agent Actions | Clear, demo-friendly, MEng-scoped |
| Core claim | Any modification of an anchored log (edit, delete, insert, reorder) is detected and located | Provable by test; does not depend on model quality |
| What goes on-chain | Merkle roots only, never raw logs | Cost and privacy |
| Hash function | SHA-256 | In Python `hashlib` and in Solidity `sha256()`, so Python and the contract agree |
| Entry serialisation | Canonical JSON (sorted keys, no spaces, UTF-8) | Same bytes on every machine |
| Entry linking | Each entry hashes `prev_hash` + payload | Detects deletion and reordering |
| Merkle tree | Domain-separated hashes (`0x00` leaf, `0x01` node); an unpaired node is carried up unchanged | Avoids second-preimage and duplicate-leaf issues |
| Smart contract language | Solidity | Standard, well documented |
| Chain | Local development chain (Hardhat); public testnet only if time allows | Free, fast, fake money |
| Python | Pure functions, frozen dataclasses, no shared mutable state | Aligns with paradigm-checker skill |
| Demo agent | Simple multi-step tool-using LLM agent | Agent quality is not the object of study |
| Demo UI | Streamlit | Month 4 |
| Code style | Prefer pure functions / immutable data | Easier to test and reason about |

## Research questions (locked for proposal)

1. Does the verifier detect 100% of edit, delete, insert and reorder attacks on anchored logs, and can it locate the first altered entry?
2. What is the cost (gas) versus delay trade-off as the anchoring batch size changes?
3. How much latency does logging and anchoring add to each agent step?
4. How does verification time and storage scale from 100 to 100,000 entries?

## Scope limits (state these in the thesis)

- The chain proves a log was not changed after it was anchored. It does **not** prove the agent's output was correct or truthful.
- A compromised logger could record false entries before anchoring. Signed entries are an optional extension.
- Prototype on a test chain, not audited production software.
