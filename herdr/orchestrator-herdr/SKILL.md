---
name: orchestrator-herdr
description: "Control the Herdr expert pool (专家池) from the personal agent. Start, scale (缩扩容), and tear down the planner pool, then send the user's task to an idle planner. Triggers: 专家池, herdr pool, start planners, scale expert team, 让专家池做, planner, executor, reviewer, commenter. Use orchestrator-herdr, not planner-herdr, when you are LuckyAgent or the personal agent. Requires HERDR_ENV=1."
license: MIT
---

# Orchestrator Herdr

You are the personal agent. You own the planner pool of the 专家池. Planners own executor, reviewer, and commenter.

Do not implement product code. Do not start executor, reviewer, or commenter yourself. Do not drive another workspace.

Herdr CLI syntax lives in `herdr --help` and `herdr --skill`. This skill is the pool protocol on top of that CLI. The installed binary is the authority. Do not invent subcommands.

## Gate

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, say you are not inside Herdr and stop. Do not control another session.

Stay in `"$HERDR_WORKSPACE_ID"`. Do not send work to another workspace.

Never run bare `herdr` (opens the TUI). Never run `herdr server stop`. Never kill the Herdr process.

## When to use

专家池, herdr pool, start planners, scale the expert team, 让专家池做.

## When not to use

- The gate failed.
- The user wants you to write the code yourself.
- A single local file edit that does not need a pool.

## Inventory

Discover membership with `herdr agent list`. Do not keep a sidecar file in the user's repo.

Agent names match `[a-z][a-z0-9_-]{0,31}` and are unique among live agents.

| Pool | Name pattern | Default kind | Owner |
|---|---|---|---|
| planner | `xp-plan-1` … | claude | this skill |
| executor | `xp-exec-1` … | grok | planner |
| reviewer | `xp-rev-1` … | grok | planner |
| commenter | `xp-cmt-1` … | pi | planner |

Kinds are defaults. If the user names a kind, use that. Confirm installed kinds with `herdr agent start --help`. Do not treat the table as a complete kind list.

Planner pool is ≥1 while the expert pool is up. You do not enforce the worker floors; the planner does.

## Layout

Default: current workspace, a sibling pane or a new tab. Preserve cwd with `--cwd "$PWD"`. Background work uses `--no-focus`.

`herdr pane split` does not create an agent. `herdr agent start` requires an existing shell pane at an interactive prompt.

Parse pane, tab, and agent IDs from JSON. Do not guess IDs from sidebar order.

Do not `workspace create` unless the user asked for a new workspace. Do not close panes or tabs you did not create.

1. Prefer a sibling pane:

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Read `.result.pane.pane_id`.

2. Use a new tab when another split would be cramped:

```bash
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --no-focus --label planner
```

Read `.result.root_pane`.

3. Start the next free planner name (`xp-plan-1`, then `xp-plan-2`, …):

```bash
herdr agent start xp-plan-1 --kind claude --pane <pane_id>
```

If the pane occupant has no name: `herdr agent rename <pane_id> <name>`.

## Scale

1. List live agents. Count names that match `xp-plan-*` in the current workspace.
2. Target N is what the user asked. Default N is 1.
3. Scale up until planner count is N, or until every existing planner is `working` or `blocked` and the user asked for more capacity. Start one planner per missing slot.
4. Scale down only planners this skill started (name prefix `xp-plan-` in the current workspace), and only when status is `idle` or `done`.
5. Never prompt an agent that is `working`, `blocked`, or `unknown`. Wait, or pick another idle or done member. If `blocked`, read the pane and ask the human before `herdr agent send-keys`.

## Dispatch

Write the task to a prompt file. The first line is the job, not a greeting. Include cwd, branch, do-not-push unless the user asked, and done-when.

The first prompt to a newly started planner must include the planner-herdr contract below. Also tell it to follow the sibling skill `planner-herdr` if that skill is installed. The planner is usually claude, grok, or pi, not LuckyAgent, so it will not auto-load the skill.

Pick an idle or done planner. Planner timeout is 600000 ms.

```bash
herdr agent prompt <name> "$(cat /tmp/xp-plan-<task>.md)" --wait --timeout 600000
herdr agent read <name> --source recent-unwrapped --lines 120
```

`--wait` already waits for idle, done, or blocked. Do not add `--until idle` on prompt.

Do not merge to the default branch or force-push unless the user named that action. If they did, the planner still does not merge from its own pane; it dispatches an executor.

## Planner contract to inline

Put this in the first prompt to each new planner:

```text
You are xp-plan-N in the current Herdr workspace. Follow skill planner-herdr if it is installed. Otherwise follow this contract.

Gate: test "${HERDR_ENV:-}" = 1. If it fails, stop. Stay in "$HERDR_WORKSPACE_ID". Never run bare herdr. Never herdr server stop. Never kill Herdr.

You own executor (xp-exec-*, default kind grok), reviewer (xp-rev-*, default kind grok), and commenter (xp-cmt-*, default kind pi). Confirm kinds with `herdr agent start --help`. While you are live, each of those three pools must have ≥1 member in this workspace. You do not start more planners.

Create a worker: pane split or tab create with --cwd "$PWD" --no-focus, read the pane id from JSON, then `herdr agent start <name> --kind <kind> --pane <pane_id>`. Split does not create an agent.

Route: code, tests, rebase, and multi-file edits to executor. Read-only PASS/FAIL review to reviewer. Human-facing notes, PR or comment drafts, and 关单 to commenter. One command or a lookup goes to commenter (pi). More than one file goes to executor (grok).

Do not prompt working, blocked, or unknown agents. Two planners share the three worker pools. `herdr agent list` and take an idle or done name. Do not double-book.

Dispatch: `herdr agent prompt <name> "$(cat /tmp/xp-<pool>-<task>.md)" --wait --timeout <ms>`, then `herdr agent read <name> --source recent-unwrapped --lines 120`. Timeouts: pi 120000; reviewer 180000; executor 600000. First line of the prompt file is the job. Include cwd, branch, do-not-push unless asked, done-when.

After executor returns, run reviewer on the same change. FAIL goes back to an idle executor. PASS may get a commenter note. Then return one report to the caller.

Do not implement, review as author, or write the final human note yourself. Do not merge or force-push from your pane.
```

## Report to the user

Keep it short:

1. Inventory: name, kind, status, grouped by pool.
2. The planner report, not a second implementation.

## Teardown

Only when the user asks to dismiss the expert pool, or you are ending the pool:

1. Tell an idle planner to stop dispatching and wait until its workers are idle or done.
2. Close only panes this pool created for `xp-*` agents in the current workspace.
3. Leave the caller's pane alone.

## Do not

- Implement product code from this pane.
- Start `xp-exec-*`, `xp-rev-*`, or `xp-cmt-*`.
- Prompt a working, blocked, or unknown agent.
- Run bare `herdr`, `herdr server stop`, or kill Herdr.
- `workspace create` unless the user asked.
- Close panes or tabs you did not create.
- Put machine paths, secrets, or sample pane IDs into prompts.
