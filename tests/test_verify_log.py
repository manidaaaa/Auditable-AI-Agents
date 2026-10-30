import itertools
import subprocess
import sys
from pathlib import Path

from app.logstore import save_log
from domain.agent import DEFAULT_TOOLS, run_agent, scripted_llm

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_log.py"


def run_cli(path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def make_log(tmp_path):
    ticks = itertools.count()
    _, log = run_agent("compute 2+2 and capital of Japan", scripted_llm, DEFAULT_TOOLS, (), lambda: float(next(ticks)))
    return save_log(log, tmp_path / "run.jsonl")


def test_intact_log_exits_zero(tmp_path):
    result = run_cli(make_log(tmp_path))
    assert result.returncode == 0 and "INTACT" in result.stdout


def test_edited_log_exits_one_and_names_the_entry(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("Tokyo", "Kyoto"))
    result = run_cli(path)
    assert result.returncode == 1 and "TAMPERING DETECTED" in result.stdout


def test_no_arguments_prints_usage(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 2 and "Usage" in result.stdout
