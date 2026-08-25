# improve-agents — reconciled spec (10-round panel)

Supervisor consolidation of 30 SSA plans (Claude pragmatic / Codex risk / Grok architecture × 10). Claude rounds 7–10 dumped JSON wrappers; load-bearing text is Codex + Grok round 10 plus Claude’s round-10 plan file.

`done = cron e2010b56833a is a zero-token-on-quiet-days critic with a stdlib wake gate, proven by fixture ticks + live job fields; not required: Hermes patch, daemon, weekly extra LLM, idea registry.`

## One job, two actors

- **Job:** Convert newly recorded, unacked, qualifying agent-runtime friction into 0–2 pickable, evidenced proposals in topic 371.
- **Critic:** cron `e2010b56833a`. Never ships.
- **Executor:** live gateway session `agent:main:telegram:group:-1004417454828:371`. Ships one picked item via live SSA.

## Decisions (disagreements resolved)

| Fight | Winner | Why |
|---|---|---|
| 3–7 ideas vs 0–2 | 0–2 | 3–7 is the recap engine |
| Two-source / 30-day vs one failure qualifies | One failure (slice 1) | Ledger is 23 rows, one day; two-source starves |
| `session_search`+`no_mcp` vs +`file` | `session_search` + `no_mcp` | File still writes; mechanism proof waits for the executor |
| Skills: review+librarian vs review only | `agent-process-review` only | Extra skills are paid on every wake |
| Ack: batch token vs output-file-only | Sidecar pending/acked; ack only on ok + no delivery error + non-silent output | Output is saved before delivery; silent ticks also look `ok` |
| Exactly-once vs at-least-once | At-least-once | executions.db has no durable delivery_outcome |
| `monitor_script` / `no_agent` / weekly LLM / daemon | Reject | Persist-before-run, verbatim stdout, recap, extra lifecycle |
| Cut over vs fire old prompt once | Cut over | Job has never run; a 3–7 recap is skip-list pollution |

Open, not slice 1: auto-capture of unstructured Moshen corrections (needs a Hermes ingress hook).

## First slice (what we ship)

1. `~/.hermes/scripts/improve-agents-gate.py` + `~/.hermes/cron/improve-agents-state.json`
2. Rewrite `agent-process-review`
3. Edit job `e2010b56833a` in place (id, schedule, delivery stay)
4. Rollback snapshot of the old prompt/skills/script
