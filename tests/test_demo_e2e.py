"""End-to-end: the scripted demo on a real local Hardhat chain."""
import shutil
import sys

import pytest

from app.chain_client import ARTIFACT

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not (shutil.which("npx") and ARTIFACT.exists()), reason="needs npx and `npx hardhat compile`"),
]


def test_scripted_demo_detects_every_tamper_scenario(monkeypatch, capsys):
    from app.run_demo import main

    monkeypatch.setattr(sys, "argv", ["run_demo", "--llm", "scripted"])
    main()
    out = capsys.readouterr().out
    assert "verify untouched log: INTACT" in out
    assert "verify after editing entry 3: TAMPERING DETECTED" in out
    assert "consistent rewrite" in out and out.count("TAMPERING DETECTED") == 3
    assert "verify after restoring the original: INTACT" in out
