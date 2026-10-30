#!/usr/bin/env python3
"""Draw the report figures (grayscale, print friendly) into assets/figures/."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "assets" / "figures"
plt.rcParams["font.family"] = "serif"
GRAY, LIGHT, DARK = "#e6e6e6", "#f5f5f5", "#222222"


def box(ax, x, y, w, h, text, fill=GRAY, size=10, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fill, ec=DARK, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, label=None, dy=0.12):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.3, color=DARK))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, ha="center", fontsize=8.5)


def new(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def architecture():
    fig, ax = new(9, 4.2)
    box(ax, 0.2, 2.9, 1.6, 0.9, "User task", LIGHT)
    box(ax, 2.4, 2.9, 2.0, 0.9, "LLM agent\n+ tools", GRAY, bold=True)
    box(ax, 5.2, 2.9, 1.9, 0.9, "Audit log\n(hash chain)", GRAY, bold=True)
    box(ax, 2.4, 1.3, 2.0, 0.9, "Log file\n(off-chain, JSONL)", LIGHT)
    box(ax, 5.2, 1.3, 1.9, 0.9, "Merkle root\nper batch", GRAY)
    box(ax, 7.6, 1.3, 1.2, 0.9, "Smart\ncontract", GRAY, bold=True)
    box(ax, 2.4, 0.2, 2.0, 0.7, "Verifier", GRAY, bold=True)
    arrow(ax, 1.8, 3.35, 2.4, 3.35)
    arrow(ax, 4.4, 3.35, 5.2, 3.35, "every step")
    arrow(ax, 5.3, 2.9, 4.3, 2.2, "save", dy=0.12)
    arrow(ax, 6.15, 2.9, 6.15, 2.2, "every B entries", dy=0.0)
    arrow(ax, 7.1, 1.75, 7.6, 1.75, "anchor()")
    arrow(ax, 3.4, 1.3, 3.4, 0.9, "load", dy=0.0)
    arrow(ax, 8.2, 1.3, 4.4, 0.55, "read roots")
    fig.savefig(OUT / "fig3_1_architecture.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def hash_chain():
    fig, ax = new(9, 2.6)
    for i, x in enumerate((0.3, 3.3, 6.3)):
        ax.add_patch(FancyBboxPatch((x, 0.5), 2.4, 1.6, boxstyle="round,pad=0.02", fc=GRAY, ec=DARK, lw=1.2))
        ax.text(x + 1.2, 1.85, f"Entry {i}", ha="center", weight="bold", fontsize=10)
        prev = "000...0 (genesis)" if i == 0 else f"hash of entry {i-1}"
        ax.text(x + 0.12, 1.4, f"index, time, content", fontsize=8.5)
        ax.text(x + 0.12, 1.05, f"prev_hash = {prev}", fontsize=8.5)
        ax.text(x + 0.12, 0.7, f"entry_hash = H(entry {i})", fontsize=8.5, weight="bold")
        if i < 2:
            arrow(ax, x + 2.4, 1.0, x + 3.0, 1.0)
    fig.savefig(OUT / "fig3_2_hash_chain.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def merkle():
    fig, ax = new(8, 4.2)
    leaves = [(0.6 + 1.9 * i, 0.3) for i in range(4)]
    for i, (x, y) in enumerate(leaves):
        box(ax, x, y, 1.4, 0.6, f"entry\nhash {i}", LIGHT if i != 2 else GRAY, size=9, bold=(i == 2))
    n01, n23 = (1.5, 1.7), (5.3, 1.7)
    box(ax, n01[0], n01[1], 1.4, 0.6, "H(0,1)", GRAY, size=9)
    box(ax, n23[0], n23[1], 1.4, 0.6, "H(2,3)", LIGHT, size=9)
    box(ax, 3.4, 3.1, 1.4, 0.7, "Merkle\nroot", GRAY, size=10, bold=True)
    for i, (x, y) in enumerate(leaves):
        parent = n01 if i < 2 else n23
        arrow(ax, x + 0.7, y + 0.6, parent[0] + 0.7, parent[1])
    arrow(ax, n01[0] + 0.7, n01[1] + 0.6, 4.1, 3.1)
    arrow(ax, n23[0] + 0.7, n23[1] + 0.6, 4.1, 3.1)
    ax.text(0.2, 3.9, "Inclusion proof for entry 2:\nsibling = entry hash 3 (right),\nsibling = H(0,1) (left)", fontsize=8.5, va="top")
    fig.savefig(OUT / "fig3_3_merkle_tree.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def attacks():
    fig, ax = new(9, 3.4)
    rows = [("Edit an entry", "caught", "caught"),
            ("Delete / insert / reorder", "caught", "caught"),
            ("Truncate the end", "NOT caught", "caught"),
            ("Rewrite + recompute later hashes", "NOT caught", "caught")]
    ax.text(3.4, 3.2, "Hash chain alone", ha="center", weight="bold", fontsize=9.5)
    ax.text(6.4, 3.2, "Chain + on-chain roots", ha="center", weight="bold", fontsize=9.5)
    for r, (name, a, b) in enumerate(rows):
        y = 2.5 - r * 0.7
        ax.text(0.1, y + 0.2, name, fontsize=9.5, va="center")
        box(ax, 2.5, y, 1.8, 0.45, a, GRAY if a == "caught" else "#bdbdbd", size=9, bold=(a != "caught"))
        box(ax, 5.5, y, 1.8, 0.45, b, GRAY, size=9)
    fig.savefig(OUT / "fig5_1_detection_matrix.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (architecture, hash_chain, merkle, attacks):
        f()
    print("wrote", *sorted(p.name for p in OUT.glob("fig*.png")))
