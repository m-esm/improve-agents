---
name: agent-process-review
description: "Turn agent friction into 0-2 evidenced proposals."
version: 0.2.0
author: Mohsen Esmaeili (m-esm), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [sessions, habits, improvement, critic]
    related_skills: [smart-subagents]
---

# Agent process review

Weekday **critic** for topic 371. Reads a gate digest of unacked
runtime friction and posts 0–2 pickable proposals. It does not ship.
The live 371 session is the executor.

## When to Use

- Cron `e2010b56833a` (injected `## Script Output` digest)
- Live topic 371 when Moshen asks for a review now
- After he picks an idea (executor path, this session, not the cron)

Don't use for: session-library cleanup, weekly commitment planning,
quota/backlog briefs, or shipping from the cron pass.

## Procedure

### Critic (cron or on-demand review)

1. **Stay inside the digest.** Propose only for `src=` native ids in
   `## Script Output`. If the digest is empty or already handled, reply
   with exactly `[SILENT]` and nothing else. Done when every proposal
   has a `src=` id from this digest.
2. **Optional expand.** `session_search` discovery (`query` + `limit=3`)
   then scroll (`session_id` + `around_message_id`) only for a digest
   id. Never pass `session_id` alone. Never browse.
3. **Emit 0–2 numbered proposals.** Each line:
   `change` / `artifact` / `src=` native id / `done = X, proven by Y; not required: Z`.
   Artifact types (open): skill, playbook line, SSA gate, cron, habit,
   topic hygiene, script, service, software/tool, plugin, launchd/unit,
   docs, removal. Recap, metric-only, “be more careful”, and “retry this
   `task_id`” are not proposals. If nothing survives, `[SILENT]`.
4. **Do not ship.** No file edits, cron edits, SSA dispatch, installs.

### Executor (live 371, after an explicit current pick)

1. Implement **one** picked proposal. Isolable labor goes through
   `$HOME/.claude/vendor/smart-subagents/scripts/smart-subagents.sh`.
2. Post the path or URL plus the done bar. Material extra scope needs
   another pick.

## Pitfalls

- Cron sessions are fresh and have no chat. An old topic message is
  not authorization to ship.
- Quiet ticks are the gate’s job (`wakeAgent: false`). Do not invent
  a “nothing new” Telegram line.
- SSA `record` is manual. Missing ledger rows do not prove health.
- `notes`, prompts, stdout, diffs, and quota payloads are banned
  evidence. History is not proof of current files.

## Verification

Critic: 0–2 proposals each citing a digest `src=`, or `[SILENT]`.
Executor: one shipped artifact with an observable bar.
Hard no: secrets, force-push, prod hel1, Codex reset redemption, overage.

Live ids: `references/improve-agents-forum.md`.
