#!/usr/bin/env python3
"""Render the title, author block, abstract and index terms of an abstract .md as a one-page IEEE-style PDF.

Usage: python scripts/abstract_to_pdf.py docs/thesis/ieee-abstract.md   (writes ieee-abstract.pdf next to it)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF

FONTS = Path("/System/Library/Fonts/Supplemental")


def section(md: str, name: str) -> str:
    match = re.search(rf"^## {re.escape(name)}\n\n(.*?)\n\n---", md, re.S | re.M)
    if not match:
        raise SystemExit(f"section '{name}' not found")
    return match.group(1).strip()


def build(md_path: Path) -> Path:
    md = md_path.read_text(encoding="utf-8")
    title, authors = section(md, "Title"), section(md, "Author Block").splitlines()
    abstract, terms = section(md, "Abstract"), section(md, "Index Terms")

    pdf = FPDF(format="Letter")
    pdf.set_margins(25, 25, 25)
    pdf.add_page()
    for style, name in (("", "Times New Roman"), ("B", "Times New Roman Bold"), ("I", "Times New Roman Italic"), ("BI", "Times New Roman Bold Italic")):
        pdf.add_font("T", style, str(FONTS / f"{name}.ttf"))
    pdf.set_font("T", "B", 18)
    pdf.multi_cell(0, 8, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("T", "", 11)
    for line in authors:
        pdf.cell(0, 5.5, line.strip(), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("T", "BI", 10)
    pdf.write(5, "Abstract—")
    pdf.set_font("T", "B", 10)
    pdf.write(5, abstract)
    pdf.ln(9)
    pdf.set_font("T", "BI", 10)
    pdf.write(5, "Index Terms—")
    pdf.set_font("T", "I", 10)
    pdf.write(5, terms)
    out = md_path.with_suffix(".pdf")
    pdf.output(str(out))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        print("wrote", build(Path(arg)))
