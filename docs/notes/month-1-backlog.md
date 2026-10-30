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
- [ ] Anchor a batch root to the local chain from Python
- [ ] Experiment config format (JSON)

## Week 4
- [ ] Month 1 write-up: design and tamper-test results
- [ ] Advisor/self review of scope
