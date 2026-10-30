---
name: verify-citations
description: Check every reference used in the thesis, report and abstracts against its source and clear the [VERIFY] flags. Use before submitting any document that cites literature.
---

# Verify citations

Sources to check: `docs/report/phase1-report.md` (REFERENCES), `docs/literature/audit-trail-notes.md`, `docs/study/concepts-study-guide.md`.

For each reference:
1. Open the source itself (publisher page, arXiv, IETF, USENIX, NIST). Search snippets and blog summaries do not count. If the page is a PDF the fetch tool cannot read, save it and extract the text locally.
2. Confirm: all authors, exact title, venue, year, volume and pages (or RFC number, arXiv id).
3. Correct the entry in every file that uses it. Remove its `[VERIFY]` flag only after step 2 is done.
4. If a source cannot be found or opened, leave the flag and say so. Never fill in details from memory.
5. Check obsolescence (for example RFC 6962 is obsoleted by RFC 9162) and cite the current document.
6. Make sure each reference is cited in the text and each citation appears in the list. The Anna University report uses author-year style; the IEEE paper uses numbered style.
7. Report a table: reference, verified yes/no, what changed.
