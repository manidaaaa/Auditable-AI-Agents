# Month 1 backlog

## Week 1
- [x] Lock title, scope and design choices (`docs/proposal/decisions.md`)
- [x] Project scaffold, git repo, Python environment
- [x] Canonical serialisation + SHA-256 helpers
- [x] Hash-chained log entries with chain verification
- [x] Merkle tree, inclusion proofs and verification

## Week 2
- [ ] Literature notes: audit logs, Merkle trees / transparency logs, blockchain anchoring, LLM agent logging
- [ ] Draft base paper choice and IEEE abstract
- [x] Install Hardhat (2.29.1) and confirm it works on Node v26.5.0
- [x] Contract draft `contracts/AuditAnchor.sol` compiles with solc 0.8.28
- [x] Contract tests on a local chain (13 passing); Python-computed Merkle proofs verify on-chain for trees of 1–100 entries

## Week 3
- [x] Shared test vectors (`scripts/make_vectors.py` -> `tests/vectors/audit_vectors.json`)
- [x] Anchor batch roots to the local chain from Python (`src/app/chain_client.py`)
- [ ] Experiment config format (JSON)

## Week 4
- [ ] Month 1 write-up: design and tamper-test results
- [ ] Advisor/self review of scope

## Done early (Month 2 scope)
- [x] Demo agent with 3 tools; every step logged (`src/domain/agent.py`). The LLM is a deterministic stand-in (`scripted_llm`); a real LLM client with the same signature is not wired up yet
- [x] Batch planning + verifier against on-chain roots (`src/domain/audit.py`); catches edit, delete, insert, reorder, truncation and consistent rewrite
- [x] End-to-end demo: `python scripts/run_demo.py`
- [x] Live local-chain test (`tests/test_chain_integration.py`); 29 Python + 13 Hardhat tests passing

## Next
- [x] Real LLM client (`src/app/anthropic_llm.py`, Claude via the Anthropic SDK, same `llm(messages) -> action` signature); unit-tested against a fake SDK client
- [x] Local LLM client (`src/app/ollama_llm.py`): Ollama + qwen3:8b, no API key (org setup has none). Real run logged, anchored and verified end to end
- [ ] Log a Claude run if an API key becomes available: `python scripts/run_demo.py --llm anthropic`
- [ ] Measure gas vs batch size, per-step logging overhead, verification time at scale
- [ ] Literature notes and base paper

## Documentation and tests (2026-10-30)
- [x] Full test suite: 79 Python + 18 contract tests (fuzz tamper tests, vectors, tools, log store, CLI, live Ollama and chain tests)
- [x] Technology explainer, testing guide, architecture, evaluation plan, literature notes, IEEE and extended abstracts, progress report, each as .md and .pdf
- [ ] Verify every citation in `docs/literature/audit-trail-notes.md` against the source
- [ ] Run evaluation experiments 2 to 4 and replace the planned figures

## Study, Anna University report, agents (2026-10-30)
- [x] Concept study guide with verified links (`docs/study/`)
- [x] Anna University format guide, checklist, Phase I report (Word and PDF preview), figures
- [x] Agents and skills documented and prepared (`.claude/`)
- [ ] Fill in register number, supervisor, HOD, college address and month in `docs/report/config.json`
- [ ] Have the Tamil abstract checked by a Tamil speaker
- [ ] Confirm the format points listed in `docs/anna-university/format-guide.md` section 12 with your coordinator
- [ ] Run the citation-verifier on the report references
