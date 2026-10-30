---
name: run-all-tests
description: Run every test suite in the Auditable Agents project (Python pytest and Hardhat contract tests) and report counts, skips and failures. Use when asked to test, verify or check the project.
---

# Run all tests

1. Work from the repository root. Use the project venv: `source .venv/bin/activate` (or call `.venv/bin/python`).
2. Make sure the contract is compiled: `npx hardhat compile`.
3. Python suite with skip reasons: `python -m pytest -q -rs`.
4. Contract suite: `npx hardhat test`.
5. Report exactly: tests passed and failed per suite, and every skipped test with its reason. Expected today: 79 Python tests and 18 contract tests.
6. If tests marked `live` skip, say why: they need `npx` plus a compiled contract, or an Ollama server with `qwen3:8b` (`ollama serve`, `ollama list`). Do not call a skipped run "fully passing".
7. On a failure, show the failing assertion, then read `docs/TESTING.md` section 8 (troubleshooting) before changing code. Never edit a test to make it pass without saying so.

Do not claim anything about gas, overhead or scaling from these tests: those experiments are still to do (`docs/methodology/evaluation-plan.md`).
