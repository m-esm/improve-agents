#!/usr/bin/env python3
"""Fixture ticks for scripts/improve-agents-gate.py. Stdlib only."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "improve-agents-gate.py"


def run(env):
    p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="ia-gate-"))
    ledger, jobs, state, outdir = root / "outcomes.jsonl", root / "jobs.json", root / "state.json", root / "out"
    outdir.mkdir()
    env = os.environ.copy()
    env.update({
        "IMPROVE_AGENTS_LEDGER": str(ledger),
        "IMPROVE_AGENTS_JOBS": str(jobs),
        "IMPROVE_AGENTS_STATE": str(state),
        "IMPROVE_AGENTS_OUTPUT_DIR": str(outdir),
        "IMPROVE_AGENTS_SELF_ID": "e2010b56833a",
    })
    jobs.write_text(json.dumps({"jobs": [{"id": "e2010b56833a", "name": "improve-agents", "enabled": True,
                                          "last_status": None, "last_run_at": None, "last_delivery_error": None}]}))
    ledger.write_text("")
    rc, out, err = run(env)
    assert rc == 0, err
    assert json.loads(out.strip().splitlines()[-1]) == {"wakeAgent": False}, out
    print("ok quiet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
