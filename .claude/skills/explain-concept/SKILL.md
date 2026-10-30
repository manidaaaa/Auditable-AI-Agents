---
name: explain-concept
description: Teach one concept of the Auditable Agents project in plain language (hashing, Merkle tree, gas, smart contract, tool calling and so on) using the study guide, the code and a short self-test. Use when the user wants to learn or revise a concept.
---

# Explain a concept

1. Read `docs/study/concepts-study-guide.md` and find the concept; use its definition and its self-check question.
2. Explain in three steps: an everyday analogy; the precise definition in this project; where it lives in the code (file and function from the study guide), showing a short real excerpt rather than a made-up one.
3. If the idea can be run, give one command the user can try (for example `python scripts/verify_log.py ...` or `python -m pytest -q tests/test_vectors.py`) and say what output to expect.
4. Ask the self-check question and wait for the answer before moving on. Correct mistakes gently and say what the right reasoning is.
5. Give the verified links from the study guide for further reading; do not add links that were not checked.
6. Assume the user may be new to the topic: define every technical word on first use.
