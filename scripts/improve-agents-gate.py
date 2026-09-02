#!/usr/bin/env python3
"""Weekday wake gate for cron e2010b56833a.

Last stdout line is JSON ``{"wakeAgent": false|true}``. Hermes skips the
model when the flag is false. Quiet ticks must still print that line.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SELF_ID = os.environ.get("IMPROVE_AGENTS_SELF_ID", "e2010b56833a")
HOME = Path.home()
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local/state"))
LEDGER = Path(
    os.environ.get(
        "IMPROVE_AGENTS_LEDGER",
        STATE_DIR / "smart-subagents" / "outcomes.jsonl",
    )
)
JOBS = Path(os.environ.get("IMPROVE_AGENTS_JOBS", HOME / ".hermes/cron/jobs.json"))
STATE = Path(
    os.environ.get(
        "IMPROVE_AGENTS_STATE", HOME / ".hermes/cron/improve-agents-state.json"
    )
)
OUTPUT_DIR = Path(
    os.environ.get(
        "IMPROVE_AGENTS_OUTPUT_DIR",
        HOME / ".hermes/cron/output" / SELF_ID,
    )
)
BOARD_ID = os.environ.get("IMPROVE_AGENTS_BOARD_ID", "e19381b51c80")
BOARD_OUTPUT_DIR = Path(
    os.environ.get(
        "IMPROVE_AGENTS_BOARD_OUTPUT_DIR",
        HOME / ".hermes/cron/output" / BOARD_ID,
    )
)
BOOTSTRAP_AGE = timedelta(days=2)
MAX_BATCH = 12
WAKE_STUB = "Script gate returned `wakeAgent=false`"
FAIL_OUTCOMES = {
    "partial",
    "rejected",
    "blocked",
    "env-blocked",
    "rate-limited",
}
SSA_FIELDS = (
    "ts",
    "task_id",
    "worker",
    "kind",
    "size",
    "difficulty",
    "outcome",
    "retries",
    "verification_passed",
    "handoff_to",
    "exit_code",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(raw: Any) -> datetime | None:
    if not raw:
        return None
    text = str(raw).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _load_state() -> dict:
    if not STATE.exists():
        return {"pending": None, "acked": []}
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"improve-agents-gate: cannot read state: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        return {"pending": None, "acked": []}
    data.setdefault("pending", None)
    data.setdefault("acked", [])
    if not isinstance(data["acked"], list):
        data["acked"] = []
    return data


def _load_jobs() -> list[dict]:
    try:
        raw = json.loads(JOBS.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"improve-agents-gate: cannot read jobs.json: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"improve-agents-gate: jobs.json is not JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    jobs = raw.get("jobs", raw) if isinstance(raw, dict) else raw
    if not isinstance(jobs, list):
        print("improve-agents-gate: jobs.json has no job list", file=sys.stderr)
        sys.exit(1)
    return [j for j in jobs if isinstance(j, dict)]


def _self_job(jobs: list[dict]) -> dict | None:
    for job in jobs:
        if job.get("id") == SELF_ID or job.get("name") == "improve-agents":
            return job
    return None


def _newest_output() -> tuple[Path | None, str]:
    if not OUTPUT_DIR.is_dir():
        return None, ""
    files = sorted(OUTPUT_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None, ""
    path = files[-1]
    try:
        return path, path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path, ""


def _should_ack(job: dict | None, pending: dict) -> bool:
    if not job or not pending:
        return False
    if job.get("last_status") != "ok":
        return False
    if job.get("last_delivery_error"):
        return False
    path, body = _newest_output()
    if path is None or not body:
        return False
    shown = pending.get("shown_at")
    if shown:
        try:
            if path.stat().st_mtime + 0.001 < float(shown):
                return False
        except (TypeError, ValueError, OSError):
            return False
    if WAKE_STUB in body:
        return False
    return True


def _ssa_qualifies(row: dict) -> bool:
    outcome = str(row.get("outcome") or "")
    if outcome in FAIL_OUTCOMES:
        return True
    try:
        if int(row.get("retries") or 0) > 0:
            return True
    except (TypeError, ValueError):
        pass
    if row.get("verification_passed") is False:
        return True
    return False


def _ssa_native_id(row: dict) -> str:
    return f"ssa:{row.get('task_id')}"


def _ssa_line(row: dict) -> str:
    parts = ["src=ssa"]
    for key in SSA_FIELDS:
        val = row.get(key)
        if val is None or val == "":
            continue
        parts.append(f"{key}={val}")
    return " ".join(parts)


def _read_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    try:
        text = LEDGER.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("schema_version") not in (1, None):
            continue
        rows.append(row)
    return rows


def _cron_qualifies(job: dict) -> bool:
    if job.get("id") == SELF_ID:
        return False
    failed_assign = (
        (job.get("name") or "").startswith("assign-")
        and job.get("last_status") == "error"
    )
    if job.get("enabled") is False and not failed_assign:
        return False
    if job.get("last_status") == "error":
        return True
    if job.get("last_delivery_error"):
        return True
    return False


def _cron_native_id(job: dict) -> str:
    return f"cron:{job.get('id')}:{job.get('last_run_at')}"


def _cron_line(job: dict) -> str:
    err = 1 if job.get("last_delivery_error") else 0
    return (
        f"src=cron job_id={job.get('id')} name={job.get('name')} "
        f"last_status={job.get('last_status')} last_run_at={job.get('last_run_at')} "
        f"delivery_error={err}"
    )


def _latest_board() -> tuple[Path, str] | None:
    if BOARD_ID == SELF_ID or not BOARD_OUTPUT_DIR.is_dir():
        return None
    try:
        files = sorted(
            BOARD_OUTPUT_DIR.glob("*.md"), key=lambda path: path.stat().st_mtime
        )
    except OSError:
        return None
    if not files:
        return None
    path = files[-1]
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not body.strip() or body.strip() == WAKE_STUB:
        return None
    return path, body


def _board_capability_channels(body: str) -> set[str]:
    heading = re.search(r"(?m)^### CAPABILITY ROWS\b", body)
    if heading is None:
        return set()
    section = body[heading.end() :]
    next_heading = re.search(r"(?m)^#{1,3}\s+", section)
    if next_heading is not None:
        section = section[: next_heading.start()]
    pattern = re.compile(
        r"^\s*(?:[-*+]\s+)?`?#([A-Za-z0-9][A-Za-z0-9_-]*)`?\b"
        r".*\bowes ONE named capability this tick\b",
        re.IGNORECASE,
    )
    channels = set()
    for line in section.splitlines():
        match = pattern.match(line)
        if match is not None:
            channels.add(match.group(1).lower())
    return channels


def _board_skipped_channels(body: str) -> set[str]:
    responses = list(re.finditer(r"(?m)^## Response\s*$", body))
    if not responses:
        return set()
    response = body[responses[-1].end() :]
    pattern = re.compile(
        r"^\s*(?:[-*+]\s+)?#([A-Za-z0-9][A-Za-z0-9_-]*)\s*"
        r"[—–-]\s*SKIP\s*[—–-]\s*.+$",
        re.IGNORECASE,
    )
    channels = set()
    for line in response.splitlines():
        match = pattern.match(line)
        if match is not None:
            channels.add(match.group(1).lower())
    return channels


def _board_timestamp(path: Path, body: str) -> datetime | None:
    run_time = re.search(r"(?m)^\*\*Run Time:\*\*\s*(.+?)\s*$", body)
    if run_time is not None:
        raw = run_time.group(1).strip().replace(" UTC", "+00:00")
        parsed = _parse_ts(raw)
        if parsed is not None:
            return parsed
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    except OSError:
        return None


def _board_candidate() -> tuple[str, datetime | None, str] | None:
    latest = _latest_board()
    if latest is None:
        return None
    path, body = latest
    skipped = _board_capability_channels(body) & _board_skipped_channels(body)
    if not skipped:
        return None
    names = ",".join(f"#{name}" for name in sorted(skipped))
    native = f"board:{BOARD_ID}:{path.name}"
    line = f"src=board job_id={BOARD_ID} file={path.name} skipped={names}"
    return native, _board_timestamp(path, body), line


def _batch_id(ids: list[str]) -> str:
    blob = ",".join(ids).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:12]


def _bootstrap_acked(candidates: list[tuple[str, datetime | None]]) -> list[str]:
    cutoff = _now() - BOOTSTRAP_AGE
    acked = []
    for native_id, ts in candidates:
        if ts is not None and ts < cutoff:
            acked.append(native_id)
    return acked


def main() -> int:
    jobs = _load_jobs()
    me = _self_job(jobs)
    state = _load_state()
    pending = state.get("pending")

    if isinstance(pending, dict) and _should_ack(me, pending):
        acked = list(dict.fromkeys(list(state.get("acked") or []) + list(pending.get("ids") or [])))
        state = {"pending": None, "acked": acked}
        _atomic_write(STATE, state)
        pending = None

    ledger = _read_ledger()
    candidates: list[tuple[str, datetime | None, str]] = []
    for row in ledger:
        if not _ssa_qualifies(row):
            continue
        native = _ssa_native_id(row)
        if native == "ssa:None":
            continue
        candidates.append((native, _parse_ts(row.get("ts")), _ssa_line(row)))
    for job in jobs:
        if not _cron_qualifies(job):
            continue
        native = _cron_native_id(job)
        candidates.append((native, _parse_ts(job.get("last_run_at")), _cron_line(job)))
    board = _board_candidate()
    if board is not None:
        candidates.append(board)

    if not STATE.exists() and not state.get("acked"):
        state["acked"] = _bootstrap_acked([(i, t) for i, t, _ in candidates])
        _atomic_write(STATE, state)

    acked = set(state.get("acked") or [])
    fresh = [(i, t, line) for i, t, line in candidates if i not in acked]

    if isinstance(pending, dict) and pending.get("ids"):
        lines = list(pending.get("lines") or [])
        ids = list(pending.get("ids") or [])
        batch = pending.get("batch_id") or _batch_id(ids)
        for line in lines:
            print(line)
        print(
            json.dumps(
                {"pending_ids": ids, "batch_id": batch, "wakeAgent": True},
                separators=(",", ":"),
            )
        )
        return 0

    if not fresh:
        print(json.dumps({"wakeAgent": False}, separators=(",", ":")))
        return 0

    fresh.sort(key=lambda item: item[1] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    fresh = fresh[:MAX_BATCH]
    fresh.reverse()
    ids = [item[0] for item in fresh]
    lines = [item[2] for item in fresh]
    batch = _batch_id(ids)
    shown_at = _now().timestamp()
    state["pending"] = {
        "shown_at": shown_at,
        "ids": ids,
        "batch_id": batch,
        "lines": lines,
    }
    _atomic_write(STATE, state)
    for line in lines:
        print(line)
    print(
        json.dumps(
            {"pending_ids": ids, "batch_id": batch, "wakeAgent": True},
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"improve-agents-gate: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
