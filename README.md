# improve-agents

A weekday fixer. A stdlib wake gate reads newly recorded, unacked agent-runtime
friction. Quiet ticks print `{"wakeAgent":false}` and spend zero tokens. On a
wake, the skill **agent-process-review** ships 0-2 evidenced process fixes and
posts the paths. Identifying without changing a file is a miss unless the item
is unsafe to touch.

Skill `name:` is `agent-process-review`. Clone the repo under that name.

Not a recap engine. Not 3-7 ideas (that is the recap shape; this one is 0-2).
Not an orchestrator. Not a dispatcher. Not [do-it-properly](https://github.com/m-esm/do-it-properly)
(that names the bar). Not [smart-subagents](https://github.com/m-esm/smart-subagents)
(that is the live labor toolkit).

## What a wake does

Read the digest. Ship 0-2 process fixes (skills, playbooks, SSA, this repo,
this job's cron/scripts). Isolable labor goes through live smart-subagents.
Post `src=`, path, and `done = X, proven by Y; not required: Z`.

It does not wait for a pick. If the only real fix needs prod, secrets, a
force-push, or paid quota, it posts the blocker and stops.

## Wake gate

`scripts/improve-agents-gate.py` is the cron `script`. Last stdout line is JSON
`{"wakeAgent":false|true}`. The host skips the model when the flag is false.
Quiet ticks still print that line.

Wakes on:

- smart-subagents ledger rows: `partial` / `rejected` / `blocked` /
  `env-blocked` / `rate-limited`, or `retries > 0`, or `verification_passed` is
  false
- other cron jobs: `last_status=error` or `last_delivery_error` set

The improve-agents job never qualifies itself. Pending is sticky until ack.
Ack only when the job is `ok`, delivery had no error, and the newest output
file is non-silent (not the host wake stub). At-least-once, not exactly-once.

Wire the script and the skill on your own cron. Forum ids in
`skill/references/improve-agents-forum.md` are one operator example, not the
product.

## Install

Canonical clone (or submodule) into the skill directory your agent already reads.

```bash
git clone https://github.com/m-esm/improve-agents.git \
  "$HOME/.claude/skills/agent-process-review"
```

Then point other agents at that same checkout. Prefer a symlink. If a loader
ignores symlinks, a 3-line pointer file that says "read the canonical SKILL.md"
is allowed. Do not copy the procedure.

| Agent | Typical path |
|---|---|
| Claude Code | `$HOME/.claude/skills/agent-process-review` |
| Hermes | `$HOME/.hermes/skills/software-development/agent-process-review` → symlink |
| Codex | `$HOME/.codex/skills/agent-process-review` → symlink |
| Grok | `$HOME/.grok/skills/agent-process-review` → symlink |
| Kimi | No global skill loader found. Unsupported until one exists. |

Point the weekday cron at `scripts/improve-agents-gate.py` and load
`agent-process-review`. Override paths with `IMPROVE_AGENTS_LEDGER`,
`IMPROVE_AGENTS_JOBS`, `IMPROVE_AGENTS_STATE`, `IMPROVE_AGENTS_OUTPUT_DIR`,
`IMPROVE_AGENTS_SELF_ID` if your layout is not the Hermes defaults.

Do not claim a CLI is supported until a fresh session loads the skill and a
quiet tick spends zero tokens.

### Rollback

Remove the symlink or pointer. The clone can stay. `git submodule deinit` if
you added it that way. Restore the previous cron script/prompt if you replaced
one.

## Contract check

```bash
python3 tests/check-gate.py
```

Guards quiet, wake, retry pending, ack after non-silent output, no-ack on the
wake stub, and cron delivery-error. It does not prove an agent will follow the
skill.

## License

MIT. Copyright 2026 Mohsen Esmaeili.
