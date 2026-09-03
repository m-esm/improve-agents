# GOAL (draft by Pawl 2026-09-03, edit freely)

For an operator running unattended agent crons (Claude Code, Hermes, Codex, Grok) who cannot babysit every session. Done means quiet ticks cost zero tokens, and a real wake ends in 0 to 2 shipped process fixes (a script, a gate, a check that fails loudly) with a proven `done =` bar, not a chat recap and not another paragraph appended to SKILL.md. It is explicitly NOT a dispatcher, not the labor engine (that is smart-subagents), and not a running list of ideas: an unshippable item gets `[SILENT]` with a receipt, never a backlog entry.

## Numbers that prove it
- gate contract: `python3 tests/check-gate.py` - today: 17/17; target: 17/17 on every commit
- shipped-fix rate per wake: run outputs under `~/.hermes/cron/output/e2010b56833a/` whose `## Response` contains `done =` and a path or SHA, over all non-`[SILENT]` outputs in the last 14d - today: unknown; target: 80%
- prose-only commits to SKILL.md in 14d (`git log --since='14 days ago' --name-only -- SKILL.md`, commits touching nothing else) - today: 25; target: under 3

source: README.md, SPEC.md, SKILL.md, tests/check-gate.py, scripts/improve-agents-gate.py
