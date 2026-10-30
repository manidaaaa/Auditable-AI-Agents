---
name: build-anna-report
description: Rebuild the Anna University style M.E. project report (Word file and PDF preview) from docs/report/phase1-report.md and config.json, then check it against the format guide. Use when editing or producing the report.
---

# Build the Anna University report

Rules live in `docs/anna-university/format-guide.md`; the checklist is `docs/anna-university/checklist.md`.

1. Edit content only in `docs/report/phase1-report.md` (chapters, tables, figures) and personal details only in `docs/report/config.json`. Never edit the generated `.docx` or `.pdf` by hand.
2. Table captions are a line `Table 3.1: Caption` directly above the table. Figures are `![Figure 3.1: Caption](assets/figures/file.png)`. Source files are included with `{{include:path}}`.
3. Rebuild: `python scripts/make_figures.py`, `node scripts/build_report_docx.js`, `python scripts/report_pdf.py`.
4. Validate the Word file with the docx skill's `validate.py` (needs `defusedxml` and `lxml` in the venv).
5. Read the final line printed by `report_pdf.py`: Chapter 1 to the last appendix page must be at least 25 pages for Phase I (40 for Phase II). Look at several pages of the preview PDF as images.
6. Never invent results. Every number in Chapters 4 and 5 must trace to a test or a captured run (`docs/report/demo_output.txt`). Leave `[VERIFY]` flags until the source is opened and checked.
7. Remind the user: open the Word file in Word and click Yes to update fields so the contents and the lists of tables and figures fill in; the PDF preview is not the Word layout.
