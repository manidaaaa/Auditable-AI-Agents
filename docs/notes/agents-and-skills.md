# Agents and Skills

**Project:** Auditable AI Agents  
**As of:** 2026-10-30  
This file has two honest parts: what was actually used while this project was prepared, and what has now been prepared for you to reuse. Nothing here is padded.

---

## 1. What was used to prepare the project

### 1.1 Skills (instruction packs loaded with the Skill tool)

| Skill | Used for | How |
|---|---|---|
| `claude-api` | Writing the Claude client (`src/app/anthropic_llm.py`) | Invoked once. Its guidance shaped the client: model `claude-opus-5-5`, no forced `tool_choice`, one tool call at a time, raw model output blocks replayed unchanged. |
| `docx` (Anthropic skills) | Building the Anna University Word report | Invoked once. Its notes on page size, tables, numbering and schema validation were followed; its validator checked the file. |

### 1.2 Skill files already in the project (not run)

`.cursor/skills/IEEE-format`, `.cursor/skills/Reasrach-paper-format` (an academic-writer skill) and `.cursor/skills/paradigm-checker` were copied from your first project. They are Cursor rules. I read the two paper-format ones when preparing the report as guidance, but did not run any of the three as a skill. The paradigm checker is written for TypeScript (`const`, no `class`), so it does not apply directly to this Python project; the code follows the same idea (pure functions, immutable data) without being checked by it.

### 1.3 Subagents

**None were started.** All work was done directly in the main session. No multi-agent workflow was run.

### 1.4 Tools used

| Tool | Used for |
|---|---|
| Bash | Running tests, Hardhat, Ollama, the demo, builds |
| Read, Write, Edit | All code and documents |
| WebSearch, WebFetch | Finding the Anna University formats and checking every tutorial link |
| AskUserQuestion | Choosing the local model to download |
| Terminal tab | One check for an API key (interrupted; the organisation has no key) |
| Task list and wrap-up | Progress tracking |

### 1.5 Agents inside the product (what the system itself runs)

| Agent or model | Role |
|---|---|
| Demo agent (`src/domain/agent.py`) | A tool-using agent with a calculator, word counter and capital lookup; every step is audited |
| `scripted_llm` | Deterministic stand-in model for fast tests |
| Ollama with `qwen3:8b` | Real local model, used for the live runs |
| Claude adapter | Written and unit-tested against a fake client; never run live (no API key) |

---

## 2. What has been prepared for reuse

These live in `.claude/` and are picked up by Claude Code when you open the project folder. **They are written but not yet exercised as agents or skills**, so expect to adjust their wording after the first real use.

### 2.1 Skills (`.claude/skills/`)

| Skill | Purpose | Typical request |
|---|---|---|
| `run-all-tests` | Runs both test suites, reports counts and every skip with its reason | "Run all tests" |
| `build-anna-report` | Rebuilds the Word report and PDF preview, validates, checks the page count, reminds you to update fields in Word | "Rebuild the report" |
| `verify-citations` | Opens each source, checks authors, venue, year and pages, clears the [VERIFY] flags, never fills from memory | "Verify my references" |
| `explain-concept` | Teaches one concept: analogy, definition, real code excerpt, a command to try, a self-check question | "Explain Merkle proofs" |

### 2.2 Subagents (`.claude/agents/`)

| Agent | Tools | Purpose |
|---|---|---|
| `citation-verifier` | Read, Edit, Bash, WebFetch, WebSearch | Does the work of `verify-citations` in the background and edits the reference lists |
| `report-reviewer` | Read, Grep, Glob, Bash (read-only) | Reviews the generated report against the format guide and checklist; checks every number in Chapters 4 and 5 against tests and runs |
| `tamper-tester` | Read, Write, Bash | Red team: invents new attacks against the verifier, writes them as tests, reports any that slip through. Never changes `src/` |

### 2.3 How to use them

- A skill is invoked by name, for example `/run-all-tests`, or by asking in plain words.
- A subagent is delegated to by name, for example "use the citation-verifier agent on the report references".
- All of them respect the same rules: no invented numbers, no filling citations from memory, and no claims about gas, overhead or scaling until those experiments are run.

---

## 3. Suggested next uses

1. Run `citation-verifier` on `docs/report/phase1-report.md` before the Phase I review.
2. Run `tamper-tester` once; any attack it finds becomes either a fix or a stated limitation in the thesis.
3. Run `report-reviewer` after you fill in your register number, supervisor and dates.
