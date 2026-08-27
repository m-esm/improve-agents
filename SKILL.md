---
name: agent-process-review
description: "Ship 0-2 evidenced process fixes from a digest."
version: 0.3.0
author: Mohsen Esmaeili (m-esm), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [sessions, habits, improvement, fix]
    related_skills: [smart-subagents, do-it-properly]
---

# Agent process review

Weekday **fixer**. Reads a gate digest of unacked runtime friction and
ships 0-2 process fixes. Identifying without changing a file is a miss
unless the item is unsafe to touch.

## When to Use

- Cron inject (`## Script Output` digest from the wake gate)
- On-demand review when the operator asks now

Don't use for: session-library cleanup, weekly commitment planning,
quota/backlog briefs, or product/prod work.

## Procedure

1. **Stay inside the digest.** Only `src=` native ids in `## Script
   Output`. Empty digest → `[SILENT]`.
2. **Optional expand.** `session_search` discovery (`query` + `limit=3`)
   then scroll (`session_id` + `around_message_id`) only for a digest
   id. Never pass `session_id` alone. Never browse.
3. **Pick 0-2 shippable items.** A recap, metric-only line, “be more
   careful”, or “retry this `task_id`” is not a fix. If nothing
   survives, `[SILENT]`.
4. **Ship.** Isolable labor goes through
   `$HOME/.claude/vendor/smart-subagents/scripts/smart-subagents.sh`.
   One-file local edits may stay in this session. Name the bar:
   `done = X, proven by Y; not required: Z`. Verify Y.
5. **Report.** For each shipped item: `src=`, artifact, path or URL,
   the done bar. Echo `batch_id`. Do not ask the operator to pick
   first.

## Allowed to touch

Skills, playbooks, SSA toolkit, this repo, Hermes cron/scripts for
this job, local process docs.

## Not allowed

Prod hosts, hel1, nbg1, live betting, secrets, force-push, Codex
reset redemption, overage. If the only real fix needs one of those,
post the blocker and stop. Do not invent a proposal instead.

## Pitfalls

- Quiet ticks are the gate (`wakeAgent: false`). No “nothing new”
  chat line.
- SSA `record` is manual. Missing ledger rows do not prove health.
- `notes`, prompts, stdout, diffs, and quota payloads are banned
  evidence.

**`[drift_skip]` pin (after provider drift):**
1. Unpinned agent crons fail closed with `[drift_skip]` and spend nothing.
2. The `cronjob` tool cannot set `model`/`provider`. Use CLI only.
3. `hermes cron edit <id> --model <model> --provider <provider>`
4. Skip `no_agent` script jobs.
5. Confirm `model` and `provider` are set; snapshots may be empty once pinned.

**Two-agent mention (bot-to-bot):**
1. First token of a peer message is a raw `<@id>` (`DISCORD_BOTS_REQUIRE_INLINE_MENTION`).
2. A reply chip is not a ping and does not wake the peer.
3. Every explanation that should continue starts with that raw id.
4. Tool-progress cards omit the mention.
5. Omit the mention = end-of-exchange.

**`card-spam` (project-channel hourglass tool-progress):**
1. `⏳` / gateway tool-progress cards in a project channel (`#3dvp`, `#bet`, `#dexsport`, …) are class `card-spam`.
2. A status ping gets one status line in that channel, then silence until a result.
3. File/skill/ledger work: SSA or one batched call so only the final reply lands.
4. Never dump intermediate reads, SSA `iteration N/150`, or renders as in-channel cards.
5. Same rule for `#team` (parent or retro): routing only, no progress stream.

## Verification

0-2 shipped artifacts with paths and an observable bar, or `[SILENT]`,
or one named blocker. Hard no list above is intact.

One operator's forum ids (not the product): `skill/references/improve-agents-forum.md`.
