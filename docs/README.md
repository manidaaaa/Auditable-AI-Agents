# Documentation

Working drafts for the Master of Engineering project by **Manikandan Sankaranarayanan** (Computer Science and Engineering, S Veersamy Chettiya College of Engineering). Every `.md` file has a matching `.pdf` beside it, produced by `scripts/md_to_pdf.py` (the IEEE abstract uses `scripts/abstract_to_pdf.py`).

Author profile for papers and forms: `references/personal-info.md`.

## Start here

| Read | For |
|---|---|
| [thesis/technologies.md](thesis/technologies.md) | Plain-language explanation of every technology used (hashing, Merkle trees, blockchain, Solidity, Hardhat, agents, Ollama) |
| [TESTING.md](TESTING.md) | How to run and understand every test, and how to try to break the system by hand |
| [notes/progress-report.md](notes/progress-report.md) | What has been done, current numbers, what remains |

## All documents

| Folder | File | Content |
|---|---|---|
| proposal | [auditable-agents.md](proposal/auditable-agents.md) | Problem, approach, deliverables, success criteria, plan |
| proposal | [decisions.md](proposal/decisions.md) | Locked choices and research questions |
| literature | [audit-trail-notes.md](literature/audit-trail-notes.md) | Reading notes, recommended base paper, gap |
| methodology | [architecture.md](methodology/architecture.md) | Layers, data flow, what each check catches |
| methodology | [evaluation-plan.md](methodology/evaluation-plan.md) | Threat model and the four experiments |
| thesis | [ieee-abstract.md](thesis/ieee-abstract.md) | IEEE conference abstract (also a one-page PDF) |
| thesis | [extended-abstract.md](thesis/extended-abstract.md) | Two-page extended abstract |
| thesis | [technologies.md](thesis/technologies.md) | Technology explainer |
| notes | [month-1-backlog.md](notes/month-1-backlog.md) | Task list |
| notes | [progress-report.md](notes/progress-report.md) | Progress and status |

Rebuild all PDFs:

```bash
python scripts/abstract_to_pdf.py docs/thesis/ieee-abstract.md
python scripts/md_to_pdf.py docs/TESTING.md docs/thesis/*.md docs/literature/audit-trail-notes.md docs/methodology/*.md docs/proposal/*.md docs/notes/progress-report.md docs/notes/month-1-backlog.md
```

(`ieee-abstract.md` is rendered by the abstract script; running the general script over it as well would overwrite the one-page PDF, so build it last.)
