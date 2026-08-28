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

**`stale-assign` (hourly board reissues already-shipped rows):**
1. Re-ASSIGN of a channel whose last ASSIGN is already DONE is class `stale-assign`.
2. Before inventing that channel's row, read the last ASSIGN and whether a DONE landed after it.
3. If that ASSIGN is DONE and the DONE is younger than 3 hours, skip the channel this hour (`SKIP` + reason).
4. Do not mint a new ASSIGN cron or board line for a skipped channel.
5. Re-assign only if there is no DONE, or the DONE is 3 hours or older. Do not edit the hourly cron from an assignee job.

**`mid-flight-assign` (unanswered ASSIGN is still in flight):**
1. An ASSIGN with no later DONE is class `mid-flight-assign`, not `stale-assign`.
2. `stale-assign` is a young DONE. Mid-flight is the opposite: the assignee has not reported yet.
3. Skip the channel this hour (`SKIP` + reason). Do not mint a new ASSIGN cron or board line.
4. Do not treat silence as a miss, a retry, or a second row.
5. Do not edit the hourly cron from an assignee job.

**`novel-vs-last` (prior hour's verb/artifact, per channel):**
1. A new ASSIGN must not reuse the prior hour's verb and artifact for that channel.
2. Verb = the action word. Artifact = the file, job, or surface named in the ASSIGN.
3. Same channel + same verb + same artifact as that channel's last hour is class `novel-vs-last`; skip (`SKIP` + reason).
4. Different verb or different artifact counts as novel and may ship.
5. Do not mint a new ASSIGN cron or board line for a reuse. Do not pad the same file with another copy of the last pitfall class.

**`dexsport-retired` (hourly board never assigns Dexsport):**
1. Dexsport retired 2026-08-27. No hunt, settle, fill-floor, or live-betting-desk.
2. The hourly board never assigns `#dexsport` or `#dexsport-results`.
3. `#bet` stays. Channels may remain. Do not shred the ledger from this job.
4. Skip those channels (`SKIP` + reason). Do not mint a new ASSIGN cron or board line for them.
5. Do not edit the hourly cron from an assignee job.

**`team-progress` (no tool-progress cards in #team):**
1. `#team` (parent or retro) is routing only. `⏳` / gateway tool-progress cards there are class `team-progress`.
2. A reply chip, status ping, or hourglass in `#team` is not a result. Do not post them.
3. File/skill/ledger work: SSA or one batched call so only the final reply lands, and never in `#team`.
4. Never dump intermediate reads, SSA `iteration N/150`, or renders as `#team` cards.
5. Do not edit the hourly cron from an assignee job.

**`second-hourly-board` (Mac e19381b51c80 is the only assigner):**
1. Mac cron `e19381b51c80` (`hourly-channel-tasks`) is the only hourly board assigner.
2. nbg1 and every other host never run a second hourly board.
3. A second board, duplicate ASSIGN cron, or nbg1 assigner is class `second-hourly-board`; skip (`SKIP` + reason).
4. Do not mint a new ASSIGN cron or board line from a second host.
5. Do not edit the hourly cron from an assignee job.

**`skip-mid-flight` (SKIP channel with open ASSIGN and no DONE):**
1. A channel with an ASSIGN and no later DONE is still in flight; skip it this hour (`SKIP` + reason).
2. Do not mint a new ASSIGN cron or board line while that ASSIGN is unanswered.
3. Open ASSIGN + no DONE is not a miss, a retry, or a slot for a replacement row.
4. Classify it as in-flight, not as `stale-assign` (that class is a young DONE).
5. Do not edit the hourly cron from an assignee job.

**`dead-cdp-not-skip` (dead CDP probe is not mid-flight SKIP for another channel):**
1. A dead CDP / `:9222` probe is class `dead-cdp-not-skip`, not `mid-flight-assign` or `skip-mid-flight` on a different channel.
2. Dead CDP on one surface (retired Dexsport Chrome, a probe tab) does not put `#3dvp` or any other channel in flight.
3. Still emit that other channel's row (viewer / docker / HTTP / CAD-freeze). Do not `SKIP` it because a probe died.
4. Classify the dead probe as dead, not as an unanswered ASSIGN for a sibling channel.
5. Do not edit the hourly cron from an assignee job.

**`omit-3dvp` (never omit #3dvp unless a real mid-flight ASSIGN is open):**
1. Dropping `#3dvp` from the hourly board is class `omit-3dvp` unless that channel has an unanswered ASSIGN with no later DONE.
2. A dead probe, retired Dexsport, SKIP on another channel, or empty queue does not omit `#3dvp`.
3. Still emit `#3dvp`'s row. The only legal skip is a real mid-flight ASSIGN on `#3dvp` itself (`SKIP` + reason).
4. Do not treat sibling-channel SKIP, CDP death, or "nothing for 3dvp" as grounds to drop the channel.
5. Do not edit the hourly cron from an assignee job.

**`never-assign-9222` (hourly board never emits Chrome/CDP/:9222):**
1. Chrome, CDP, or `:9222` probes are class `never-assign-9222`. The hourly board never emits them as ASSIGN rows (incident 1542640516011925545).
2. Distinguish from `dead-cdp-not-skip`: that class is a dead probe must not SKIP a sibling channel. This class is: never assign the probe itself.
3. Skip those surfaces (`SKIP` + reason). Do not mint a new ASSIGN cron or board line for Chrome/CDP/:9222.
4. Do not treat a dead or live CDP port as an hourly channel task. Viewer / docker / HTTP / CAD-freeze stay eligible on their own channels.
5. Do not edit the hourly cron from an assignee job.

## Verification

0-2 shipped artifacts with paths and an observable bar, or `[SILENT]`,
or one named blocker. Hard no list above is intact.

One operator's forum ids (not the product): `skill/references/improve-agents-forum.md`.
