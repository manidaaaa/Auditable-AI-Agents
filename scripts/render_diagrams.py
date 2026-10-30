#!/usr/bin/env python3
"""Render the Mermaid diagrams in docs/diagrams/NN-*.md to PNG and SVG in docs/diagrams/images/.

Uses mermaid-cli (expected at .tools/mermaid-cli, kept out of git) and your installed Chrome in
headless mode, with the Chrome profile kept inside .tools so nothing is written elsewhere.
Usage: python scripts/render_diagrams.py [NN-name ...]   (no arguments: render all)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs" / "diagrams"
IMAGES = DIAGRAMS / "images"
MMDC = ROOT / ".tools" / "mermaid-cli" / "node_modules" / ".bin" / "mmdc"


def render(md: Path) -> bool:
    match = re.search(r"```mermaid\n(.*?)\n```", md.read_text(encoding="utf-8"), re.S)
    if not match:
        print(f"{md.name}: no mermaid block")
        return False
    source = IMAGES / f"{md.stem}.mmd"
    source.write_text(match.group(1) + "\n", encoding="utf-8")
    ok = True
    for ext in ("png", "svg"):
        cmd = [str(MMDC), "-p", str(DIAGRAMS / "puppeteer-config.json"), "-c", str(DIAGRAMS / "mermaid-config.json"),
               "-i", str(source), "-o", str(IMAGES / f"{md.stem}.{ext}"), "-b", "white", "-s", "2"]
        result = subprocess.run(cmd, capture_output=True, text=True, env={"PUPPETEER_SKIP_DOWNLOAD": "1", "PATH": "/opt/homebrew/bin:/usr/bin:/bin"})
        if result.returncode != 0:
            print(f"{md.name}: FAILED ({ext})\n{result.stderr.strip()[:600]}")
            ok = False
            break
    if ok:
        print(f"{md.name}: ok")
    source.unlink(missing_ok=True)
    return ok


if __name__ == "__main__":
    IMAGES.mkdir(exist_ok=True)
    wanted = set(sys.argv[1:])
    files = [p for p in sorted(DIAGRAMS.glob("[0-9][0-9]-*.md")) if not wanted or p.stem in wanted]
    results = [render(p) for p in files]
    print(f"{sum(results)} of {len(results)} rendered")
    raise SystemExit(0 if all(results) else 1)
