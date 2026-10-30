# IEEE Conference Abstract (Draft)

**Target:** IEEE conference abstract / extended-abstract submission  
**Status:** Draft. Results are from automated tests and first demo runs (2026-10-30); gas, overhead and scaling studies are still to do, see `docs/methodology/evaluation-plan.md`  
**Word count (abstract body):** ~225 words (IEEE typical: 150–250)  
**Author source:** `references/personal-info.md`

---

## Title

Auditable AI Agents: An Immutable On-Chain Audit Trail for LLM Agent Actions

---

## Author Block

Manikandan Sankaranarayanan  
Department of Computer Science and Engineering  
S Veersamy Chettiya College of Engineering  
e-mail: smak07.s@gmail.com

---

## Abstract

Autonomous agents built on large language models (LLMs) call tools and act on behalf of users, yet their records are usually ordinary log files that anyone with server access can edit or delete without leaving evidence. This paper presents a tamper-evident audit trail for LLM agent actions. Each step, namely the prompt, model response, tool call, and tool result, is written to a hash-chained log, and batches of entries are folded into Merkle roots anchored in a smart contract, so only 32-byte hashes, never raw logs, are stored on-chain. A verifier recomputes hashes from the stored log, compares them with the anchored roots, and locates the first altered entry or batch. The prototype, implemented in Python and Solidity on a local Ethereum development chain, was exercised with a local open-weight model. In randomized tests, seven classes of tampering (edits to payloads, timestamps and hashes, deletion, insertion, reordering, and truncation) were detected in all 2,100 trials, with no false alarms on 300 untouched logs, and a consistently rewritten log, which defeats a hash chain alone, was caught by the on-chain roots. Python-generated Merkle proofs verified on-chain for trees of up to 100 entries, and anchoring cost roughly 80,000 to 93,000 gas per batch in a first run. Gas-versus-batch-size, overhead, and scaling studies are under way. The trail proves a log was not altered after anchoring, not that agent outputs were correct.

---

## Index Terms

LLM agents, audit trail, tamper-evident logging, Merkle tree, blockchain anchoring, smart contracts, AI accountability.

---

## Notes for submission

1. Author block filled from `references/personal-info.md`. Add city/country on conference forms if required.
2. After the evaluation experiments finish, replace the last sentences with the measured gas, overhead and scaling figures.
3. Confirm the target conference's abstract limit (some allow 150 words max; some allow 200–250). A shorter 150-word cut can drop the Python/Solidity agreement and gas sentences.
4. Do not claim the system prevents tampering or proves correctness; claim **tamper evidence after anchoring**.
5. Citations are not in the abstract; the reference list is in `docs/literature/audit-trail-notes.md` (details to be verified before submission).
