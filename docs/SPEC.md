# Contract

`done = a zero-token-on-quiet-days critic with a stdlib wake gate, proven by python3 tests/check-gate.py; not required: Hermes core patch, daemon, weekly extra LLM, idea registry.`

## One job, two actors

- **Job:** Convert newly recorded, unacked, qualifying agent-runtime friction into 0-2 pickable, evidenced proposals.
- **Critic:** the weekday cron (skill `agent-process-review`). Never ships.
- **Executor:** a live session after an explicit current pick. Ships one picked item via live smart-subagents.

Forum / topic / cron ids are operator wiring. One example lives in `skill/references/improve-agents-forum.md`. They are not the public contract.

## Decisions

| Fight | Winner | Why |
|---|---|---|
| 3-7 ideas vs 0-2 | 0-2 | 3-7 is the recap engine |
| Two-source / 30-day vs one failure qualifies | One failure (slice 1) | A small ledger plus a two-source rule starves the critic |
| Skills: review+librarian vs review only | `agent-process-review` only | Extra skills are paid on every wake |
| Ack: batch token vs output-file-only | Sidecar pending/acked; ack only on ok + no delivery error + non-silent output | Output is saved before delivery; silent ticks also look `ok` |
| Exactly-once vs at-least-once | At-least-once | There is no durable delivery_outcome |
| `monitor_script` / `no_agent` / weekly LLM / daemon | Reject | Persist-before-run, verbatim stdout, recap, extra lifecycle |

Open, not slice 1: auto-capture of unstructured operator corrections (needs a host ingress hook).

## Wake and ack

`scripts/improve-agents-gate.py` prints digest lines (if any), then one JSON line with `wakeAgent`.

- SSA ledger: `partial` / `rejected` / `blocked` / `env-blocked` / `rate-limited`, or `retries > 0`, or `verification_passed` is false.
- Other crons: `last_status=error` or `last_delivery_error` set. The critic job never qualifies itself.
- Quiet: `{"wakeAgent":false}`. Pending is sticky on wake until ack.
- Ack: self job `ok`, no `last_delivery_error`, newest `*.md` in the output dir is non-empty and is not the host wake stub (`Script gate returned \`wakeAgent=false\``).

## Out of this repo

Hermes core patches, extra registries, landing pages, and recap-shaped 3-7 idea lists.
