# Progress report

**Project:** Auditable AI Agents  
**As of:** 2026-10-30  
**Repository:** `/Users/mani-2209/AuditableAgentsProject` (local git, no remote)

---

## 1. Work log

| Step | What was done | Commit |
|---|---|---|
| 1 | Project chosen after comparing three ideas (audit trail, registry and permissions, task escrow); scaffold, proposal, locked decisions, backlog | `Initial scaffold` |
| 2 | Hash chain, Merkle tree with proofs, canonical JSON; first 18 tests | same |
| 3 | `AuditAnchor.sol` contract; Hardhat set up; Python-generated vectors verified on-chain | `Add Hardhat setup...` |
| 4 | Demo agent with 3 tools; audit logger; batch planning; verifier; web3 client; end-to-end demo with tamper scenarios | `Add demo agent, audit logger...` |
| 5 | Claude client (tested with a fake SDK, not run live: no API key in the organisation setup) | `Add Claude LLM client...` |
| 6 | Local LLM client for Ollama; Ollama installed, `qwen3:8b` downloaded (5.2 GB); real agent run logged, anchored and verified | `Add local LLM client...` |
| 7 | Complete test suite; log-verification script; documentation set and PDFs | current |

---

## 2. Current numbers

| Item | Value |
|---|---|
| Python tests | 79 passing |
| Contract tests | 18 passing |
| Tamper attack types tested | 7 (x 300 random trials each) plus consistent rewrite |
| Missed attacks / false alarms | 0 / 0 |
| Real model run | qwen3:8b, 12 entries, 3 batches, verified |
| Gas per anchor (first run) | about 79,500 to 93,100 |

---

## 3. Decisions taken along the way

- Chose the audit-trail project as the safest to finish because its core claim (tampering is detected) is provable by test and does not depend on AI model quality.
- SHA-256 everywhere so Python and Solidity agree.
- Only Merkle roots go on-chain.
- Used a local model (Ollama, qwen3:8b) because the organisation provides no Anthropic API key.
- Hardhat 2 (not 3) for familiarity; it runs on the installed Node v26.5.0 even though that version is not officially listed as supported.

---

## 4. Not done yet

- Evaluation experiments 2 to 4 (gas versus batch size, overhead, scaling).
- Streamlit dashboard.
- Verified literature review (citations are from memory).
- Public testnet run (optional).
- Signed entries and consistency proofs (optional extensions).
- Push to a remote repository.

---

## 5. Things to know

- The Ollama server was started by hand and keeps running until stopped (`pkill ollama`, or `brew services stop ollama` if started as a service).
- Demo logs in `research/experiments/agent_logs/` are git-ignored because each demo run overwrites them.
- `artifacts/`, `cache/` and `node_modules/` are git-ignored and are recreated by `npx hardhat compile` and `npm install`.
