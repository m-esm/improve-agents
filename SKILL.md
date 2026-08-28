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

**`novel-vs-last` (novel against the whole ledger, not the prior hour):**
1. A new ASSIGN must be novel against every topic in that channel's ledger (`shipped:<channel>`), not merely against the prior hour.
2. A renamed artifact is not a novel artifact. If the new file, section, or probe differs from an existing one only by a swapped token (tool name, parameter, unit, date, column, filename suffix), it is the same task; skip (`SKIP` + reason).
3. A different verb over the same surface is novel only if it can fail differently. "Document X" then "document Y" in the same file is one task, not two.
4. If the rule that would justify a row is an exact string match with a fixed legal set, one example closes it permanently. Enumerating the illegal values proves nothing new.
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

**`no-goal-source` (a row that traces to no goal on disk is a random walk):**
1. Creative forward motion needs a destination. Rows derived from the last 5 Discord messages can only vary the previous row, which is how `route=grep` became `route=eslint` and `nozzle-temp` became `bed-temp`.
2. Read the goal where it lives: 3dvp `.overnight/BACKLOG.md` + `docs/PLAN-*.md` + `docs/AGENT-LOOP.md`, mechlib `mechlib/usecases.py` + `gallery/`, onlydash sub-repo issues and unmerged branches, bet `prisma/schema.prisma`. 3dvp had 11 unchecked backlog items through 139 consecutive jobs that never assigned one.
3. If the backlog is empty, the row is a capability the product lacks, stated in one sentence. If neither exists, `SKIP`.
4. Do not shrink a row to fit an hour. A row may span ticks; say so. "Finishable in <1h" plus "Done=paste" selects for the cheapest artifact, which is a doc note.

**`calcified-misread` (the agent's own output becomes its law):**
1. A constraint an agent writes into a repo doc is read back by the next run as ground truth. A misreading therefore hardens instead of decaying.
2. Observed: mechlib AGENTS.md bans CadQuery/OpenSCAD/NopSCADlib *as a dependency for growing the vitamin catalog*. A run generalized it to "No CadQuery. No geometry.", wrote that into `wiper-kit.md`, and every later run obeyed it. In a parametric geometry library that left prose as the only legal output.
3. Before obeying a constraint quoted in a doc an agent wrote, check it against the repo's own AGENTS.md/CLAUDE.md. Quote the source line.
4. When a constraint blocks a repo's stated purpose, that is the signal it was misread, not a reason to narrow the work.

**`no-visual-proof` (green numbers are not a look):**
1. Rows that change a product close on a rendered artifact plus the sentence someone wrote after looking at it, not on a paste. `docs/AGENT-LOOP.md` in 3dvp: never claim done on green numbers alone.
2. The tooling exists and was unused: mechlib `gallery/build_gallery.py` and `gallery/collision_gate.py` (161 demos, 0 failures, 45s), 3dvp per-product `build.py` + filmstrip/shoot, onlydash the live URL.
3. Downscale PNGs to <=1600 px before reading them.

**`unequipped-row` (a task minted without its domain skill can only produce prose):**
1. Minted ASSIGN crons default to `skills=['do-it-properly']`. A geometry task arriving with no geometry skill writes notes about geometry instead of geometry.
2. Every board row states its own `skills=` and `workdir=`. Geometry: `do-it-properly,3d-print-modeling,moshen-projects`. Multi-file code: add `smart-subagents`.

**`make-work` (a row that only varies a token is not work):**
1. A board row is illegal if it differs from an already-shipped topic only by a swapped string, number, tool name, filename, date, or unit. `route=eslint` after `route=grep`, `bed-temp` after `nozzle-temp`, `awayOdds` after `homeOdds` are the same task.
2. Also illegal: appending another same-shape section to a doc that has one, adding another near-identical file to a family, recomputing a statistic over a static file, or assigning a channel whose last row is still unpushed.
3. No channel is entitled to a row, `#3dvp` and `#onlydash` included. `SKIP` with a reason when there is no legal work. An empty board is a correct board.
4. Read the ledger (`hermes cron notepad e19381b51c80 list`) and the target repo's `git log`/`git status` before assigning. The last 5 Discord messages are the weakest signal.
5. `Done=SHA` means pushed to a named remote and verified with `git ls-remote`. A local `git log -1` does not close a row.

**`never-assign-9222` (hourly board never emits Chrome/CDP/:9222):**
1. Chrome, CDP, or `:9222` probes are class `never-assign-9222`. The hourly board never emits them as ASSIGN rows (incident 1542640516011925545).
2. Distinguish from `dead-cdp-not-skip`: that class is a dead probe must not SKIP a sibling channel. This class is: never assign the probe itself.
3. Skip those surfaces (`SKIP` + reason). Do not mint a new ASSIGN cron or board line for Chrome/CDP/:9222.
4. Do not treat a dead or live CDP port as an hourly channel task. Viewer / docker / HTTP / CAD-freeze stay eligible on their own channels.
5. Do not edit the hourly cron from an assignee job.

**`not-a-wake` (one rule; nine observed instances):**
1. Only one thing wakes this agent: a raw, unbackticked, inline `<@id>` for it, in a message that also carries a DO, DONE, BLOCKED, Q, or SHA (`DISCORD_BOTS_REQUIRE_INLINE_MENTION`).
2. Everything else is SILENT. Reply `[SILENT]` or `NO_REPLY`, post no Discord echo, mint no ASSIGN cron or board line, and never edit the hourly cron from an assignee job.
3. Speak only on SHA, veto, or a named blocker.

Instances seen so far, all resolved by rule 1, none needing its own class:

| Observed | Why it is not a wake |
| --- | --- |
| hosted freeze / snapshot FYI, even with a Pawl ping | the ping carries no DO/DONE/BLOCKED/Q/SHA |
| nbg1 self-ASSIGN, in a project channel or naming nbg1's own id | nbg1 assigning itself; a second board, not a Pawl row |
| ACK-only from nbg1 | no DO/DONE/BLOCKED/Q/SHA |
| gateway progress card (`💾`/`⚙️`/`⏰`/`💻`/`📚`/`⏳`) | a card is not a message from a peer |
| Discord reply chip (reply UI / referenced message) | not a raw `<@id>` |
| `<@id>` wrapped in backticks | a code span renders as text, not a mention |
| last-8 age-out / `ch X empty` | an empty window is not a message |

Adding a tenth class for the next variant is the `card-spam` failure in a new
costume. If a new case appears, add a table row, not a block.

## Verification

0-2 shipped artifacts with paths and an observable bar, or `[SILENT]`,
or one named blocker. Hard no list above is intact.

One operator's forum ids (not the product): `skill/references/improve-agents-forum.md`.
