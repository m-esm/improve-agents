#!/usr/bin/env python3
"""Fixture ticks for scripts/improve-agents-gate.py. Stdlib only."""
import json, os, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "improve-agents-gate.py"
WAKE_STUB = "Script gate returned `wakeAgent=false`"
SELF_ID = "e2010b56833a"


def run(env):
    p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


def last_json(out):
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    return json.loads(lines[-1])


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class Fx:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="ia-gate-"))
        self.ledger = self.root / "outcomes.jsonl"
        self.jobs_path = self.root / "jobs.json"
        self.state_path = self.root / "state.json"
        self.outdir = self.root / "out"
        self.outdir.mkdir()
        self.env = os.environ.copy()
        self.env.update({
            "IMPROVE_AGENTS_LEDGER": str(self.ledger),
            "IMPROVE_AGENTS_JOBS": str(self.jobs_path),
            "IMPROVE_AGENTS_STATE": str(self.state_path),
            "IMPROVE_AGENTS_OUTPUT_DIR": str(self.outdir),
            "IMPROVE_AGENTS_SELF_ID": SELF_ID,
        })
        self.write_jobs()
        self.ledger.write_text("")

    def write_jobs(self, others=None, last_status=None, last_delivery_error=None):
        jobs = [{
            "id": SELF_ID,
            "name": "improve-agents",
            "enabled": True,
            "last_status": last_status,
            "last_run_at": None,
            "last_delivery_error": last_delivery_error,
        }]
        if others:
            jobs.extend(others)
        self.jobs_path.write_text(json.dumps({"jobs": jobs}))

    def write_ledger(self, rows):
        self.ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))

    def write_output(self, body, name="review.md"):
        path = self.outdir / name
        path.write_text(body)
        return path

    def load_state(self):
        return json.loads(self.state_path.read_text())

    def tick(self):
        rc, out, err = run(self.env)
        assert rc == 0, err or out
        return last_json(out), out


def ssa(task_id, outcome="partial"):
    return {
        "schema_version": 1,
        "task_id": task_id,
        "outcome": outcome,
        "retries": 0,
        "ts": now_iso(),
    }


def test_quiet():
    payload, _ = Fx().tick()
    assert payload == {"wakeAgent": False}, payload
    print("ok quiet")


def test_wake():
    fx = Fx()
    fx.write_ledger([ssa("t1")])
    payload, out = fx.tick()
    assert payload.get("wakeAgent") is True, payload
    assert payload.get("pending_ids") == ["ssa:t1"], payload
    assert "src=ssa" in out
    state = fx.load_state()
    assert state["pending"]["ids"] == ["ssa:t1"], state
    print("ok wake")


def test_retry_pending():
    fx = Fx()
    fx.write_ledger([ssa("t1")])
    first, _ = fx.tick()
    fx.write_ledger([ssa("t1"), ssa("t2")])
    second, out = fx.tick()
    assert second.get("wakeAgent") is True, second
    assert second.get("pending_ids") == first.get("pending_ids") == ["ssa:t1"], (first, second)
    assert second.get("batch_id") == first.get("batch_id"), (first, second)
    assert "ssa:t2" not in json.dumps(second)
    assert fx.load_state()["pending"]["ids"] == ["ssa:t1"]
    assert "src=ssa" in out
    print("ok retry pending")


def test_ack_after_non_silent():
    fx = Fx()
    fx.write_ledger([ssa("t1")])
    first, _ = fx.tick()
    assert first.get("wakeAgent") is True, first
    fx.write_jobs(last_status="ok")
    time.sleep(0.05)
    fx.write_output("1. change the critic prompt / skill / src=ssa:t1 / done = X")
    payload, _ = fx.tick()
    assert payload == {"wakeAgent": False}, payload
    state = fx.load_state()
    assert state.get("pending") is None, state
    assert "ssa:t1" in state.get("acked", []), state
    print("ok ack after non-silent output")


def test_no_ack_on_wake_stub():
    fx = Fx()
    fx.write_ledger([ssa("t1")])
    first, _ = fx.tick()
    fx.write_jobs(last_status="ok")
    time.sleep(0.05)
    fx.write_output(f"host noise {WAKE_STUB} more noise")
    payload, out = fx.tick()
    assert payload.get("wakeAgent") is True, payload
    assert payload.get("pending_ids") == first.get("pending_ids") == ["ssa:t1"], payload
    assert fx.load_state()["pending"]["ids"] == ["ssa:t1"]
    assert "src=ssa" in out
    print("ok no-ack on wake stub")


def test_cron_delivery_error():
    fx = Fx()
    run_at = now_iso()
    fx.write_jobs(others=[{
        "id": "other-cron",
        "name": "elsewhere",
        "enabled": True,
        "last_status": "ok",
        "last_run_at": run_at,
        "last_delivery_error": "telegram 429",
    }])
    payload, out = fx.tick()
    assert payload.get("wakeAgent") is True, payload
    native = f"cron:other-cron:{run_at}"
    assert payload.get("pending_ids") == [native], payload
    assert "src=cron" in out
    assert "delivery_error=1" in out
    print("ok cron delivery-error signal")


def main() -> int:
    test_quiet()
    test_wake()
    test_retry_pending()
    test_ack_after_non_silent()
    test_no_ack_on_wake_stub()
    test_cron_delivery_error()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
