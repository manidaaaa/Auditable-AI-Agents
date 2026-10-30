"""End-to-end demo: agent -> audit log -> anchor on a local chain -> tamper -> verifier catches it."""
from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path

from app.chain_client import REPO_ROOT, anchor_pending, deploy_anchor, local_chain, read_batches
from app.logstore import load_log, save_log
from domain.agent import DEFAULT_TOOLS, run_agent, scripted_llm
from domain.audit import verify_against_chain
from domain.chain import compute_entry_hash

TASK = "Please compute 12*(3+4) and count words in 'auditable agents leave a trail' and find the capital of Japan."
BATCH_SIZE = 5


def show(label: str, report) -> None:
    status = "INTACT" if report.ok else "TAMPERING DETECTED"
    print(f"{label}: {status}")
    for note in report.notes:
        print(f"   - {note}")
    if report.first_bad_index is not None:
        print(f"   first suspicious entry: {report.first_bad_index}")


def main() -> None:
    log_path = REPO_ROOT / "research" / "experiments" / "agent_logs" / "demo_run.jsonl"
    answer, log = run_agent(TASK, scripted_llm, DEFAULT_TOOLS, (), time.time)
    save_log(log, log_path)
    print(f"agent answered: {answer}")
    print(f"{len(log)} audit entries saved to {log_path.relative_to(REPO_ROOT)}")

    with local_chain() as w3:
        sender = w3.eth.accounts[0]
        contract = deploy_anchor(w3, sender)
        receipts = anchor_pending(contract, sender, log, batch_size=BATCH_SIZE)
        for r in receipts:
            print(f"anchored batch {r.batch_id}: entries {r.first_index}..{r.first_index + r.count - 1}, "
                  f"root {r.root[:12]}…, gas {r.gas_used}")
        batches = read_batches(contract, sender)

        show("\nverify untouched log", verify_against_chain(load_log(log_path), batches))

        entries = load_log(log_path)
        edited = replace(entries[3], payload={**entries[3].payload, "tampered": True})
        save_log(entries[:3] + (edited,) + entries[4:], log_path)
        show("verify after editing entry 3", verify_against_chain(load_log(log_path), batches))

        # Smarter attacker: rewrite entry 3 and recompute every hash after it so the chain is consistent.
        rewritten: list = list(entries[:3])
        for e in (edited, *entries[4:]):
            prev = rewritten[-1].entry_hash
            payload = e.payload
            rewritten.append(replace(e, prev_hash=prev, entry_hash=compute_entry_hash(e.index, e.timestamp, payload, prev)))
        save_log(rewritten, log_path)
        show("verify after consistent rewrite (only the chain can catch this)",
             verify_against_chain(load_log(log_path), batches))

        save_log(entries[:-2], log_path)
        show("verify after deleting the last 2 entries", verify_against_chain(load_log(log_path), batches))
        save_log(entries, log_path)
        show("verify after restoring the original", verify_against_chain(load_log(log_path), batches))


if __name__ == "__main__":
    main()
