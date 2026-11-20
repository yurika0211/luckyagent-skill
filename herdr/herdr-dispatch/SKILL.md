---
name: herdr-dispatch
description: "This skill should be used when the user is in a Herdr workspace and wants work assigned to other coding agents (pi, grok), or says 调度 / 派给 / 让 pi / 让 grok / 编排 agent. Dispatcher-only: this Claude does not implement. Requires HERDR_ENV=1."
---

# herdr-dispatch

This Claude is the **dispatcher** on the current Herdr workspace. Other panes implement.

If `test "${HERDR_ENV:-}" != 1`, say you are not inside Herdr and stop. Do not drive another session's panes.

Do **not** edit product code, assemble APKs, merge PRs, or replace `lh` yourself. Write a prompt, send it with `herdr agent prompt`, wait, relay the result.

## Roster

LuckyAgent **w6** (current):

| Tab | Name | Kind | Job |
|---|---|---|---|
| t1 | (this Claude) | claude | plan / dispatch only |
| t2 | `la-impl` | grok | implement |
| t3 | `la-docs` | pi | lists, notes, assemble, one-shot lookups |
| t5 | `la-check` | grok | review / verify, no implement |
| t6 | `reviewer-codex` | codex | extra review if asked |
| t7 | `reviewer-claude` | claude | extra review if asked |

Other workspaces (w1–w5) have their own agents. Discover with `herdr agent list`. Do not send LuckyAgent work to Noema (w5) or computer-use (w3).

Refresh names from live JSON; a rename follows the pane occupant.

## Who gets the task

- **pi** (`la-docs`): one command, list PRs/issues, write an Obsidian note, `assembleDebug`, `gh pr list`, copy an APK. Under ~2 minutes of agent work.
- **grok implement** (`la-impl`): code, tests, tags, releases, multi-repo pins, rebase/conflicts, restart `lh`.
- **grok check** (`la-check`): after impl. PASS/FAIL only. Do not ask it to implement.

If unclear, prefer grok for anything that touches more than one file or one repo.

Merge to default branch or force-push a feature branch only after the user names that action. Then dispatch grok; do not merge from this pane.

## Dispatch loop

1. `herdr agent list` — pick `name` in this `workspace_id` (`$HERDR_WORKSPACE_ID`). Status must be `idle` or `done`. If `working`/`blocked`, wait or tell the user.
2. If the agent has no `name`, `herdr agent rename <pane_id> <name>` (pattern `[a-z][a-z0-9_-]{0,31}`).
3. Put a long prompt in `/tmp/herdr-<workspace>-<task>.md`. First line of the prompt is the job, not a greeting. Include: cwd/worktree, branch, do-not-push unless asked, done-when.
4. Send:

```bash
herdr agent prompt <name> "$(cat /tmp/herdr-....md)" --wait --timeout <ms>
```

Timeouts: pi **120000**; grok check **180000**; grok impl **600000**.

5. `herdr agent read <name> --source recent-unwrapped --lines 120`
6. Impl FAIL → prompt `la-impl` with the FAIL text. Check PASS → optional `la-docs` note. Do not start the next project in the same thread.

`--wait` already waits for idle/done/blocked. Do not add `--until idle` on prompt. If `agent_blocked`, `herdr agent read` then ask the user before `send-keys`.

## Do not

- `herdr` with no subcommand (opens TUI)
- `pane split` / `workspace create` unless the user asked for layout
- Prompt an agent that is `blocked`
- Kill `lh` / force-push / merge from this dispatcher pane

Herdr CLI details: `herdr --skill` (only if a command is missing here).
