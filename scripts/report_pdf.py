#!/usr/bin/env python3
"""PDF preview of the Anna University style report (same rules as scripts/build_report_docx.js).

Usage: python scripts/report_pdf.py   -> docs/report/Phase1-Report-preview.pdf
Used to check layout and page count without Word. Needs fpdf2, uharfbuzz, fonttools and macOS fonts.
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from fontTools.ttLib import TTCollection
from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path("/System/Library/Fonts/Supplemental")
CFG = json.loads((ROOT / "docs/report/config.json").read_text(encoding="utf-8"))
SRC = (ROOT / "docs/report/phase1-report.md").read_text(encoding="utf-8")
L, R, T, B = 38, 22, 32, 28
BODY, LH, INDENT = 13, 13 * 1.5 * 0.3528, 20  # point size, 1.5 line spacing in mm, 20 mm indents
TAMIL = re.compile(r"[஀-௿]")


def roman(n: int) -> str:
    out = ""
    for v, s in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= v:
            out, n = out + s, n - v
    return out


def parse(md: str):
    md = re.sub(r"^\{\{include:(.+?)\}\}$", lambda m: "```\n" + (ROOT / m.group(1)).read_text(encoding="utf-8").rstrip() + "\n```", md, flags=re.M)
    lines, sections, cur, cap = md.split("\n"), [], None, None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            cur = {"title": line[2:].strip(), "blocks": []}
            sections.append(cur)
        elif cur is None:
            pass
        elif line.startswith("```"):
            code = []
            i += 1
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            cur["blocks"].append(("code", code))
        elif re.match(r"^Table \d+(\.\d+)?: ", line):
            cap = line.replace(": ", "  ", 1)
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s:|-]+\|?$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            cur["blocks"].append(("table", rows, cap))
            cap = None
        elif re.match(r"^!\[(.+)\]\((.+)\)$", line):
            m = re.match(r"^!\[(.+)\]\((.+)\)$", line)
            cur["blocks"].append(("image", m.group(1).replace(": ", "  ", 1), m.group(2)))
        elif line.startswith("### "):
            cur["blocks"].append(("h3", line[4:]))
        elif line.startswith("## "):
            cur["blocks"].append(("h2", line[3:]))
        elif re.match(r"^\d+\. ", line):
            cur["blocks"].append(("item", line))
        elif line.strip():
            cur["blocks"].append(("p", line.strip()))
        i += 1
    return sections


def md_inline(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"**\1**", text)
    text = re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?![*\w])", r"__\1__", text)
    return text.replace("`", "")


class Doc(FPDF):
    mode = "front"  # front (roman) or main (arabic)
    main_start = 0

    def header(self) -> None:
        if self.page_no() == 1:
            return
        label = roman(self.page_no()) if self.mode == "front" else str(self.page_no() - self.main_start + 1)
        self.set_font("T", "", 12)
        self.set_xy(self.w - R - 30, 20)
        self.cell(30, 5, label, align="R")
        self.set_y(T)


def build(prev_toc, prev_tables, prev_figures):
    sections = parse(SRC)
    doc = Doc(format="A4")
    doc.set_margins(L, T, R)
    doc.set_auto_page_break(True, margin=B)
    for style, name in (("", "Times New Roman"), ("B", "Times New Roman Bold"), ("I", "Times New Roman Italic"), ("BI", "Times New Roman Bold Italic")):
        doc.add_font("T", style, str(FONTS / f"{name}.ttf"))
    doc.add_font("C", "", str(FONTS / "Courier New.ttf"))
    ttf = Path(tempfile.gettempdir()) / "TamilSangam-Regular.ttf"
    if not ttf.exists():
        TTCollection(str(FONTS / "Tamil Sangam MN.ttc")).fonts[0].save(str(ttf))
    doc.add_font("TA", "", str(ttf))
    doc.set_fallback_fonts(["TA"])
    found: list[tuple[int, str, str]] = []  # (level, text, page label)
    tables: list[tuple[str, str]] = []
    figures: list[tuple[str, str]] = []
    W = doc.w - L - R

    def label() -> str:
        return roman(doc.page_no()) if doc.mode == "front" else str(doc.page_no() - doc.main_start + 1)

    def centred(text, size, style="B", h=None, after=0):
        doc.set_font("T", style, size)
        doc.set_x(L)
        doc.multi_cell(W, h or size * 0.52, text, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        doc.ln(after)

    def new_page(top: float = 50):
        doc.add_page()
        doc.set_y(top)

    def heading1(lines: list[str], toc: bool = True, text_for_toc: str | None = None):
        new_page()
        if toc:
            found.append((1, text_for_toc or " ".join(lines), label()))
        for ln in lines:
            centred(ln, 14, "B", 7)
        doc.ln(8)

    def para(text: str, double=False, indent=True):
        shaping = bool(TAMIL.search(text))
        doc.set_text_shaping(shaping)
        doc.set_font("TA" if shaping else "T", "", BODY)
        doc.set_x(L)
        body = md_inline(text)
        if indent:
            body = " " * 14 + body
        doc.multi_cell(W, LH * (1.33 if double else 1), body, align="J", markdown=not shaping, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        doc.set_text_shaping(False)
        doc.ln(1.5)

    def table(rows, cap):
        if cap:
            tables.append((cap, label()))
            doc.set_font("T", "", BODY)
            doc.set_x(L)
            doc.multi_cell(W, 6, cap, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        cols = len(rows[0])
        weights = [max(8, min(40, max(len(r[c]) if c < len(r) else 0 for r in rows))) for c in range(cols)]
        widths = tuple(w / sum(weights) * W for w in weights)
        doc.set_font("T", "", 11)
        with doc.table(col_widths=widths, line_height=5, text_align="LEFT", first_row_as_headings=True, padding=1) as t:
            for row in rows:
                cells = t.row()
                for c in range(cols):
                    cells.cell(re.sub(r"[*`]", "", row[c]) if c < len(row) else "")
        doc.ln(4)

    def block(b):
        kind = b[0]
        if kind == "p":
            para(b[1])
        elif kind == "h2":
            doc.ln(3)
            found.append((2, b[1], label()))
            doc.set_font("T", "B", BODY)
            doc.set_x(L + INDENT)
            doc.multi_cell(W - INDENT, 7, b[1], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif kind == "h3":
            doc.ln(2)
            found.append((3, b[1], label()))
            doc.set_font("T", "B", BODY)
            doc.set_x(L + INDENT)
            doc.multi_cell(W - INDENT, 7, b[1], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif kind == "item":
            doc.set_font("T", "", BODY)
            doc.set_x(L + INDENT)
            doc.multi_cell(W - INDENT, LH, md_inline(b[1]), align="J", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif kind == "table":
            table(b[1], b[2])
        elif kind == "image":
            figures.append((b[1], label()))
            img = ROOT / b[2]
            doc.set_x(L)
            doc.image(str(img), x=L + (W - 135) / 2, w=135)
            doc.ln(2)
            centred(b[1], BODY, "", 6, 4)
        elif kind == "code":
            doc.set_font("C", "", 7.5)
            doc.set_fill_color(242, 242, 242)
            for line in b[1]:
                line = line.replace("\t", "    ")
                for chunk in [line[i : i + 88] for i in range(0, max(len(line), 1), 88)] or [""]:
                    doc.set_x(L)
                    doc.cell(W, 3.6, chunk, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            doc.ln(2)

    def find(title):
        return next(s for s in sections if s["title"] == title)

    # ---- cover (page i, no number) ----
    doc.add_page()
    doc.set_y(40)
    centred(CFG["title"], 18, "B", 9, 14)
    centred(CFG["report_type"], 14, "B", 7, 14)
    centred("Submitted by", 14, "BI", 7, 4)
    centred(CFG["candidate"], 16, "B", 8, 2)
    centred(f"(Register No. {CFG['register_no']})", 14, "", 7, 14)
    centred("in partial fulfillment for the award of the degree of", 14, "B", 7, 8)
    centred("MASTER OF ENGINEERING IN", 16, "B", 8)
    centred(CFG["programme"], 16, "B", 8, 18)
    centred(CFG["department"], 16, "B", 8)
    centred(CFG["college"], 16, "B", 8)
    centred(CFG["affiliation"], 12, "", 6, 18)
    centred(CFG["month_year"], 14, "B", 7)

    # ---- bonafide ----
    new_page()
    centred(CFG["college"], 18, "B", 8)
    centred(CFG["affiliation"], 12, "", 6, 6)
    centred("BONAFIDE CERTIFICATE", 16, "B", 8, 8)
    kind = "Report" if CFG["report_type"].startswith("PHASE I ") else "Thesis"
    doc.set_font("T", "", BODY)
    doc.set_x(L)
    doc.multi_cell(W, LH * 1.33, " " * 14 + f"Certified that this {kind} titled “{CFG['title']}” is the bonafide work of {CFG['candidate']} (Register No. {CFG['register_no']}) who carried out the work under my supervision. Certified further that to the best of my knowledge the work reported herein does not form part of any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.", align="J", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.ln(18)
    y = doc.get_y()
    for x, who in ((L, "HOD"), (L + W / 2 + 2, "Supervisor")):
        doc.set_xy(x, y)
        doc.set_font("T", "", 11)
        name = CFG["hod_name"] if who == "HOD" else CFG["supervisor_name"]
        desig = CFG["hod_designation"] if who == "HOD" else CFG["supervisor_designation"]
        doc.multi_cell(W / 2 - 4, 5, f"<<Signature of the {who} with date>>\n{name}\n{desig}\n{CFG['department_title']}\n{CFG['college_title']}", new_x=XPos.LEFT, new_y=YPos.NEXT)

    # ---- abstracts ----
    heading1(["ABSTRACT"])
    for b in find("ABSTRACT")["blocks"]:
        para(b[1], double=True)
    heading1(["ABSTRACT (TAMIL)"])
    for b in find("ABSTRACT (TAMIL)")["blocks"]:
        para(b[1], double=True)
    new_page()
    centred("ACKNOWLEDGEMENT", 14, "B", 7, 8)
    for b in find("ACKNOWLEDGEMENT")["blocks"]:
        para(b[1], double=True)
    doc.ln(8)
    doc.set_font("T", "B", BODY)
    doc.set_x(L)
    doc.cell(W, 7, CFG["candidate"], align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---- contents, lists ----
    def listing(title, items, indent_of=lambda lvl: 0, in_toc=False):
        new_page()
        if in_toc:
            found.append((1, title, label()))
        centred(title, 14, "B", 7, 8)
        for lvl, text, pg in items:
            doc.set_font("T", "B" if lvl == 1 else "", 12)
            x0 = L + indent_of(lvl)
            doc.set_x(x0)
            w = W - indent_of(lvl) - 14
            y0 = doc.get_y()
            doc.multi_cell(w, 6.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            y1 = doc.get_y()
            doc.set_xy(doc.w - R - 14, y0)
            doc.cell(14, 6.2, pg, align="R")
            doc.set_y(y1)

    listing("TABLE OF CONTENTS", [(l, t, pg) for l, t, pg in prev_toc], lambda lvl: (lvl - 1) * 6)
    listing("LIST OF TABLES", [(1, c, pg) for c, pg in prev_tables], in_toc=True)
    listing("LIST OF FIGURES", [(1, c, pg) for c, pg in prev_figures], in_toc=True)
    heading1(["LIST OF ABBREVIATIONS"])
    for b in find("LIST OF ABBREVIATIONS")["blocks"]:
        block(b)

    # ---- main text ----
    doc.mode = "main"
    for s in sections:
        ch = re.match(r"^CHAPTER (\d+): (.+)$", s["title"])
        ap = re.match(r"^APPENDIX (\d+): (.+)$", s["title"])
        if not (ch or ap or s["title"] == "REFERENCES"):
            continue
        if ch:
            lines, toc_text = [f"CHAPTER {ch.group(1)}", ch.group(2)], f"CHAPTER {ch.group(1)}  {ch.group(2)}"
        elif ap:
            lines, toc_text = [f"APPENDIX {ap.group(1)}", ap.group(2)], f"APPENDIX {ap.group(1)}  {ap.group(2)}"
        else:
            lines, toc_text = ["REFERENCES"], "REFERENCES"
        doc.mode = "main"
        if ch and ch.group(1) == "1":
            doc.main_start = doc.page_no() + 1
        heading1(lines, text_for_toc=toc_text)
        if s["title"] == "REFERENCES":
            doc.set_font("T", "", 12)
            for b in s["blocks"]:
                doc.set_x(L)
                doc.multi_cell(W, 5.5, b[1], align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                doc.ln(2)
        else:
            for b in s["blocks"]:
                block(b)
    last_appendix_page = None
    return doc, found, tables, figures


if __name__ == "__main__":
    # build repeatedly until the page numbers printed in the contents and lists stop changing
    toc, tabs, figs = [], [], []
    for _ in range(5):
        doc, new_toc, new_tabs, new_figs = build(toc, tabs, figs)
        stable = (new_toc, new_tabs, new_figs) == (toc, tabs, figs)
        toc, tabs, figs = new_toc, new_tabs, new_figs
        if stable:
            break
    out = ROOT / "docs/report/Phase1-Report-preview.pdf"
    doc.output(str(out))
    body_pages = doc.page_no() - doc.main_start + 1
    refs = [pg for lvl, t, pg in toc if t == "REFERENCES"]
    print(f"wrote {out.relative_to(ROOT)}: {doc.page_no()} pages in total, {body_pages} numbered pages (Chapter 1 to end), references on page {refs[0] if refs else '?'}")
