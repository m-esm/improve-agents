#!/usr/bin/env python3
"""Fail doc-only commits when 14d product motion is DOC-ONLY. Stdlib + git."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOC_NAMES = frozenset({"SKILL.md", "README.md", "LICENSE", ".gitignore"})
INDEX_ALIASES = frozenset({"--index", "--cached", ":index"})


def is_doc_only_path(path: str) -> bool:
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    if p in DOC_NAMES:
        return True
    if p == "docs" or p.startswith("docs/"):
        return True
    if p == "skill" or p.startswith("skill/"):
        return True
    if "/" not in p and p.endswith(".md"):
        return True
    return False


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def paths_since(repo: Path, since: str = "14.days") -> list[str]:
    p = _git(repo, "log", f"--since={since}", "--name-only", "--pretty=format:")
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "git log failed")
    return [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]


def commit_paths(repo: Path, commit: str) -> list[str]:
    p = _git(repo, "log", "-1", "--name-only", "--pretty=format:", commit)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "git log -1 failed")
    return [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]


def index_paths(repo: Path) -> list[str]:
    p = _git(repo, "diff", "--cached", "--name-only")
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "git diff --cached failed")
    return [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]


def window_is_doc_only(paths: list[str]) -> bool:
    if not paths:
        return False
    return all(is_doc_only_path(p) for p in paths)


def is_doc_only_commit(paths: list[str]) -> bool:
    if not paths:
        return False
    return all(is_doc_only_path(p) for p in paths)


def check_repo(repo: Path, commit: str = "HEAD") -> int:
    """1 when 14d motion is DOC-ONLY and the commit/index is doc-only, else 0."""
    paths = index_paths(repo) if commit in INDEX_ALIASES else commit_paths(repo, commit)
    if window_is_doc_only(paths_since(repo)) and is_doc_only_commit(paths):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    repo = Path(args[0] if args else ".").resolve()
    commit = args[1] if len(args) > 1 else "HEAD"
    try:
        return check_repo(repo, commit)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
