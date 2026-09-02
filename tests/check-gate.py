#!/usr/bin/env python3
"""Fixture ticks for scripts/improve-agents-gate.py. Stdlib only."""
import json, os, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "improve-agents-gate.py"
DOC_GATE = ROOT / "scripts" / "doc_only_gate.py"
WAKE_STUB = "Script gate returned `wakeAgent=false`"
SELF_ID = "e2010b56833a"
BOARD_ID = "e19381b51c80"


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
        self.board_outdir = self.root / "board-out"
        self.board_outdir.mkdir()
        self.env = os.environ.copy()
        self.env.update({
            "IMPROVE_AGENTS_LEDGER": str(self.ledger),
            "IMPROVE_AGENTS_JOBS": str(self.jobs_path),
            "IMPROVE_AGENTS_STATE": str(self.state_path),
            "IMPROVE_AGENTS_OUTPUT_DIR": str(self.outdir),
            "IMPROVE_AGENTS_SELF_ID": SELF_ID,
            "IMPROVE_AGENTS_BOARD_ID": BOARD_ID,
            "IMPROVE_AGENTS_BOARD_OUTPUT_DIR": str(self.board_outdir),
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

    def write_board(self, body, name="board.md"):
        path = self.board_outdir / name
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


def test_disabled_assign_error_wakes():
    fx = Fx()
    run_at = now_iso()
    fx.write_jobs(others=[{
        "id": "44228b7a3d75",
        "name": "assign-01-ssa-exit2-clone",
        "enabled": False,
        "last_status": "error",
        "last_run_at": run_at,
    }])
    payload, out = fx.tick()
    native = f"cron:44228b7a3d75:{run_at}"
    assert payload.get("wakeAgent") is True, payload
    assert payload.get("pending_ids") == [native], payload
    assert "src=cron job_id=44228b7a3d75" in out, out
    print("ok disabled assign error wakes")


def test_disabled_non_assign_error_quiet():
    fx = Fx()
    fx.write_jobs(others=[{
        "id": "failed-other",
        "name": "elsewhere",
        "enabled": False,
        "last_status": "error",
        "last_run_at": now_iso(),
    }])
    payload, _ = fx.tick()
    assert payload == {"wakeAgent": False}, payload
    print("ok disabled non-assign error quiet")


def test_board_capability_skip_wakes():
    fx = Fx()
    fx.write_board(f"""**Run Time:** {now_iso()}

Prompt example:
## Response
#bar — SKIP — example only

### CAPABILITY ROWS - a funded channel with an empty queue owes an invention
#foo - queue empty and funded; owes ONE named capability this tick
#bar - queue empty and funded; owes ONE named capability this tick

## Response
#bar — ASSIGN — useful work
#foo — SKIP — no eligible task
""")
    payload, out = fx.tick()
    native = f"board:{BOARD_ID}:board.md"
    assert payload.get("wakeAgent") is True, payload
    assert payload.get("pending_ids") == [native], payload
    assert f"src=board job_id={BOARD_ID} file=board.md skipped=#foo" in out, out
    print("ok board capability SKIP wakes")


def test_board_non_capability_skip_quiet():
    fx = Fx()
    fx.write_board("""### CAPABILITY ROWS
#foo - queue empty and funded; owes ONE named capability this tick

## Response
#infra – SKIP – not in OPEN BACKLOG or CAPABILITY this tick
""")
    payload, _ = fx.tick()
    assert payload == {"wakeAgent": False}, payload
    print("ok board non-capability SKIP quiet")


def test_board_capability_assign_quiet():
    fx = Fx()
    fx.write_board("""### CAPABILITY ROWS
#foo - queue empty and funded; owes ONE named capability this tick

## Response
#foo - ASSIGN - implement the capability
""")
    payload, _ = fx.tick()
    assert payload == {"wakeAgent": False}, payload
    print("ok board capability ASSIGN quiet")


def test_board_deferred_only_skip_quiet():
    fx = Fx()
    fx.write_board("""### CAPABILITY ROWS
(deferred to the next budget day, only 1 left: #foo)
(none - no funded capability rows)

## Response
#foo — SKIP — deferred ledger CAPABILITY work
""")
    payload, _ = fx.tick()
    assert payload == {"wakeAgent": False}, payload
    print("ok board deferred-only SKIP quiet")


def check_doc_only(repo, commit="HEAD"):
    p = subprocess.run(
        [sys.executable, str(DOC_GATE), str(repo), commit],
        capture_output=True,
        text=True,
    )
    return p.returncode, p.stdout, p.stderr


def _git(repo, args, date=None):
    cmd = [
        "git",
        "-C",
        str(repo),
        "-c",
        "user.email=gate@example.com",
        "-c",
        "user.name=Gate",
        *args,
    ]
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "Gate",
        "GIT_AUTHOR_EMAIL": "gate@example.com",
        "GIT_COMMITTER_NAME": "Gate",
        "GIT_COMMITTER_EMAIL": "gate@example.com",
    })
    if date is not None:
        stamp = date.strftime("%Y-%m-%dT%H:%M:%S +0000")
        env["GIT_AUTHOR_DATE"] = stamp
        env["GIT_COMMITTER_DATE"] = stamp
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr or p.stdout
    return p


def _init_git_repo():
    root = Path(tempfile.mkdtemp(prefix="doc-only-"))
    _git(root, ["init", "-b", "main"])
    _git(root, ["config", "commit.gpgsign", "false"])
    return root


def _commit_file(repo, relpath, content, date, msg):
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    _git(repo, ["add", "--", relpath], date=date)
    _git(repo, ["commit", "-m", msg], date=date)


def _old_product_then_skill_md(repo, extra_in_window=None):
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=20)
    mid = now - timedelta(days=5)
    recent = now - timedelta(days=1)
    _commit_file(repo, "scripts/app.py", "print(1)\n", old, "product outside 14d")
    if extra_in_window:
        rel, body = extra_in_window
        _commit_file(repo, rel, body, mid, "product inside 14d")
    _commit_file(repo, "SKILL.md", "# skill v1\n", mid, "skill md 1")
    _commit_file(repo, "SKILL.md", "# skill v2\n", recent, "skill md 2")


def test_skill_md_only_when_14d_doc_only():
    repo = _init_git_repo()
    _old_product_then_skill_md(repo)
    rc, out, err = check_doc_only(repo)
    assert rc != 0, (rc, out, err)
    print("ok doc-only skill.md fixture fails")


def test_skill_md_only_ok_when_product_in_14d():
    repo = _init_git_repo()
    _old_product_then_skill_md(repo, extra_in_window=("scripts/new.py", "print(2)\n"))
    rc, out, err = check_doc_only(repo)
    assert rc == 0, (rc, out, err)
    print("ok product motion allows skill.md")


def test_docs_plus_skill_md_when_14d_doc_only():
    repo = _init_git_repo()
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=20)
    mid = now - timedelta(days=5)
    recent = now - timedelta(days=1)
    _commit_file(repo, "scripts/app.py", "print(1)\n", old, "product outside 14d")
    _commit_file(repo, "SKILL.md", "# skill v1\n", mid, "skill md 1")
    (repo / "SKILL.md").write_text("# skill v2\n")
    (repo / "README.md").write_text("# readme\n")
    _git(repo, ["add", "--", "SKILL.md", "README.md"], date=recent)
    _git(repo, ["commit", "-m", "docs+skill"], date=recent)
    rc, out, err = check_doc_only(repo)
    assert rc != 0, (rc, out, err)
    print("ok docs+SKILL.md fixture fails")


def test_this_repo_head_runs_doc_only_gate():
    rc, out, err = check_doc_only(ROOT, "HEAD")
    assert rc == 0, (rc, out, err)
    print("ok this repo HEAD runs doc-only gate")


def test_pre_commit_blocks_docs_plus_skill_md():
    repo = _init_git_repo()
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=20)
    mid = now - timedelta(days=5)
    _commit_file(repo, "scripts/app.py", "print(1)\n", old, "product outside 14d")
    _commit_file(repo, "SKILL.md", "# skill v1\n", mid, "skill md 1")
    hooks = ROOT / "scripts" / "githooks"
    _git(repo, ["config", "core.hooksPath", str(hooks)])
    (repo / "SKILL.md").write_text("# skill v2\n")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("note\n")
    _git(repo, ["add", "--", "SKILL.md", "docs/note.md"])
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "Gate",
        "GIT_AUTHOR_EMAIL": "gate@example.com",
        "GIT_COMMITTER_NAME": "Gate",
        "GIT_COMMITTER_EMAIL": "gate@example.com",
    })
    p = subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.email=gate@example.com",
            "-c", "user.name=Gate",
            "commit", "-m", "docs+skill",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert p.returncode != 0, (p.returncode, p.stdout, p.stderr)
    print("ok pre-commit blocks docs+SKILL.md")


def main() -> int:
    test_quiet()
    test_wake()
    test_retry_pending()
    test_ack_after_non_silent()
    test_no_ack_on_wake_stub()
    test_cron_delivery_error()
    test_disabled_assign_error_wakes()
    test_disabled_non_assign_error_quiet()
    test_board_capability_skip_wakes()
    test_board_non_capability_skip_quiet()
    test_board_capability_assign_quiet()
    test_board_deferred_only_skip_quiet()
    test_skill_md_only_when_14d_doc_only()
    test_skill_md_only_ok_when_product_in_14d()
    test_docs_plus_skill_md_when_14d_doc_only()
    test_this_repo_head_runs_doc_only_gate()
    test_pre_commit_blocks_docs_plus_skill_md()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
