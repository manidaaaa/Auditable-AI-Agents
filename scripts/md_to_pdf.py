#!/usr/bin/env python3
"""Small Markdown -> PDF converter (headings, lists, tables, code blocks, bold/italic/inline code).

Usage: python scripts/md_to_pdf.py file.md [more.md ...]     (writes file.pdf next to each input)
Needs: fpdf2. Fonts: macOS system fonts (Times New Roman, Courier New, Arial Unicode).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONTS = Path("/System/Library/Fonts/Supplemental")
REPLACE = {"→": "->", "←": "<-", "✔": "[ok]", "✓": "[ok]", "≥": ">=", "≤": "<=", " ": " ", "‑": "-"}
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
M = 22  # page margin, mm


def clean(text: str) -> str:
    for a, b in REPLACE.items():
        text = text.replace(a, b)
    return text


def strip_marks(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return re.sub(r"[*`]", "", clean(text)).strip()


class Doc(FPDF):
    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("T", "", 9)
        self.cell(0, 8, str(self.page_no()), align="C")


def build(md_path: Path) -> Path:
    pdf = Doc(format="Letter")
    pdf.set_margins(M, M, M)
    pdf.set_auto_page_break(True, margin=18)
    for style, name in (("", "Times New Roman"), ("B", "Times New Roman Bold"), ("I", "Times New Roman Italic"), ("BI", "Times New Roman Bold Italic")):
        pdf.add_font("T", style, str(FONTS / f"{name}.ttf"))
    pdf.add_font("C", "", str(FONTS / "Courier New.ttf"))
    pdf.add_font("U", "", str(FONTS / "Arial Unicode.ttf"))
    pdf.set_fallback_fonts(["U"])
    pdf.add_page()
    width = pdf.w - 2 * M

    def inline(text: str, size: float, base: str = "", lh: float = 5.6) -> None:
        text = clean(text)
        for part in INLINE.split(text):
            if not part:
                continue
            if part.startswith("**") and part.endswith("**"):
                pdf.set_font("T", "B" + ("I" if "I" in base else ""), size)
                pdf.write(lh, part[2:-2])
            elif part.startswith("`") and part.endswith("`"):
                pdf.set_font("C", "", size - 1)
                pdf.write(lh, part[1:-1])
            elif part.startswith("*") and part.endswith("*") and len(part) > 2:
                pdf.set_font("T", "I" + ("B" if "B" in base else ""), size)
                pdf.write(lh, part[1:-1])
            elif part.startswith("["):
                label = re.match(r"\[([^\]]+)\]", part).group(1)
                pdf.set_font("T", base, size)
                pdf.write(lh, label)
            else:
                pdf.set_font("T", base, size)
                pdf.write(lh, part)
        pdf.ln(lh)

    def code_block(lines: list[str]) -> None:
        pdf.set_font("C", "", 8)
        pdf.set_fill_color(240, 240, 240)
        pdf.ln(1)
        for line in lines:
            line = clean(line).replace("\t", "    ")
            chunks = [line[i : i + 92] for i in range(0, max(len(line), 1), 92)] or [""]
            for chunk in chunks:
                pdf.set_x(M)
                pdf.cell(width, 4, chunk, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    def table(rows: list[list[str]]) -> None:
        header, body = rows[0], rows[1:]
        cols = len(header)
        weights = [max(8, min(60, max(len(strip_marks(r[c])) if c < len(r) else 0 for r in rows))) for c in range(cols)]
        total = sum(weights)
        widths = tuple(w / total * width for w in weights)
        pdf.set_font("T", "", 8.5)
        pdf.ln(1)
        with pdf.table(col_widths=widths, line_height=4.2, text_align="LEFT", first_row_as_headings=True,
                       borders_layout="ALL", padding=1) as t:
            for row in [header] + body:
                cells = t.row()
                for c in range(cols):
                    cells.cell(strip_marks(row[c]) if c < len(row) else "")
        pdf.ln(3)

    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            code_block(block)
        elif stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1]):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            table(rows)
            continue
        elif re.match(r"^#{1,3} ", stripped):
            level = len(stripped.split(" ")[0])
            size = {1: 19, 2: 14.5, 3: 12}[level]
            pdf.ln(4 if level > 1 else 2)
            pdf.set_x(M)
            inline(stripped[level + 1 :], size, "B", lh=size * 0.52)
            pdf.ln(1)
        elif stripped in ("---", "***"):
            pdf.ln(1)
            pdf.line(M, pdf.get_y(), pdf.w - M, pdf.get_y())
            pdf.ln(3)
        elif re.match(r"^\s*([-*]|\d+\.) ", line):
            indent = (len(line) - len(line.lstrip())) // 2
            marker = re.match(r"^\s*([-*]|\d+\.) ", line).group(1)
            bullet = "-" if marker in "-*" else marker
            pdf.set_x(M + 4 + indent * 5)
            pdf.set_font("T", "", 11)
            pdf.write(5.6, f"{bullet}  ")
            inline(re.sub(r"^\s*([-*]|\d+\.) ", "", line), 11)
        elif stripped.startswith(">"):
            pdf.set_x(M + 5)
            inline(stripped.lstrip("> ").strip(), 11, "I")
        elif stripped == "":
            pdf.ln(2)
        else:
            pdf.set_x(M)
            inline(stripped + ("" if not line.endswith("  ") else ""), 11)
        i += 1

    out = md_path.with_suffix(".pdf")
    pdf.output(str(out))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        print("wrote", build(Path(arg)))
