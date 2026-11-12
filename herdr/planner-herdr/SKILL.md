---
name: planner-herdr
description: "Operate a Herdr planner pool member (专家池). Ensure executor, reviewer, and commenter pools each have ≥1 member, dispatch work, and scale those pools (缩扩容). Triggers: planner, executor, reviewer, commenter, herdr pool, xp-plan, 关单. Use when you were started as xp-plan-* or the orchestrator told you to follow planner-herdr. Requires HERDR_ENV=1."
license: MIT
---

# Planner Herdr

You are a planner (`xp-plan-*`). You own the executor, reviewer, and commenter pools. The personal agent owns the planner pool via `orchestrator-herdr`.

Do not implement. Do not review as the author. Do not write the final human note yourself. Do not start more planners. Do not call `orchestrator-herdr`.

Herdr CLI syntax lives in `herdr --help` and `herdr --skill`. This skill is the pool protocol. The installed binary is the authority. Do not invent subcommands.

## Gate

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, say you are not inside Herdr and stop. Do not control another session.

Stay in `"$HERDR_WORKSPACE_ID"`. Do not send work to another workspace.

Never run bare `herdr` (opens the TUI). Never run `herdr server stop`. Never kill the Herdr process.

## When to use

You were started as a pool planner, or the orchestrator told you to follow this skill.

## When not to use

- You are the personal agent. Use `orchestrator-herdr`.
- You are an executor, reviewer, or commenter.

## Inventory

Discover membership with `herdr agent list`. Do not keep a sidecar file in the user's repo.

Agent names match `[a-z][a-z0-9_-]{0,31}` and are unique among live agents.

| Pool | Name pattern | Default kind | You start it |
|---|---|---|---|
| planner | `xp-plan-*` | claude | no |
| executor | `xp-exec-1` … | grok | yes |
| reviewer | `xp-rev-1` … | grok | yes |
| commenter | `xp-cmt-1` … | pi | yes |

Kinds are defaults. If the caller names a kind, use that. Confirm installed kinds with `herdr agent start --help`.

While ≥1 planner is live, executor, reviewer, and commenter are each ≥1. Two planners share the three worker pools.

## Ensure the worker pools

1. `herdr agent list`. Count live `xp-exec-*`, `xp-rev-*`, and `xp-cmt-*` in the current workspace.
2. If a pool is empty, start one member. Next free name is `xp-exec-1`, `xp-rev-1`, or `xp-cmt-1`, then increment.

Layout: current workspace, sibling pane or a new tab. `--cwd "$PWD"` and `--no-focus`.

`herdr pane split` does not create an agent. `herdr agent start` needs an existing shell pane at an interactive prompt.

Parse IDs from JSON. Do not guess from sidebar order. Do not `workspace create` unless the user asked. Do not close panes or tabs you did not create.

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
# read .result.pane.pane_id
herdr agent start xp-exec-1 --kind grok --pane <pane_id>
```

A new tab is cleaner when another split would be cramped:

```bash
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --no-focus --label executor
```

Read `.result.root_pane`, then `herdr agent start`.

If the pane occupant has no name: `herdr agent rename <pane_id> <name>`.

## Route

- executor: code, tests, rebase, multi-file edits.
- reviewer: read-only findings, PASS or FAIL. No edits.
- commenter: Obsidian, notes, PR or comment drafts, status, 关单. Under about 2 minutes of agent work. No product code.
- One command, a list, or a lookup: commenter (pi).
- More than one file: executor (grok).

## Scale

- Scale a worker pool up when every member of that pool is `working` or `blocked`, or the caller asked for N.
- Scale down only agents this pool started (prefix `xp-exec-`, `xp-rev-`, or `xp-cmt-` in the current workspace), and only when `idle` or `done`.
- Never prompt `working`, `blocked`, or `unknown`. Wait, or pick another idle or done member. If `blocked`, read the pane and ask the human before `herdr agent send-keys`.
- Before prompting a worker, `herdr agent list` and take an idle or done name. Do not double-book a worker another planner is using.

## Dispatch

Write a prompt file. The first line is the job, not a greeting. Include cwd, branch, do-not-push unless the user asked, and done-when.

Timeouts in ms: commenter (pi) 120000; reviewer 180000; executor 600000.

```bash
herdr agent prompt <name> "$(cat /tmp/xp-<pool>-<task>.md)" --wait --timeout <ms>
herdr agent read <name> --source recent-unwrapped --lines 120
```

`--wait` already waits for idle, done, or blocked. Do not add `--until idle` on prompt.

Loop:

1. Send implementation to an idle executor.
2. Send the same change to an idle reviewer.
3. FAIL: send the FAIL text to an idle executor. Repeat from step 2.
4. PASS: optional commenter note.
5. Reply once to the caller (the personal agent). Include worker names, status, and PASS or the remaining FAIL.

Do not merge to the default branch or force-push unless the user named that action. Then dispatch an executor. You still do not merge from this pane.

## Teardown

Only when the caller asks to dismiss the workers you started:

1. Wait until those workers are idle or done.
2. Close only panes this skill created for those `xp-exec-*`, `xp-rev-*`, and `xp-cmt-*` agents in the current workspace.
3. Leave the caller's pane and other planners alone.

## Do not

- Implement, author a review, or write the final human note in this pane.
- Start `xp-plan-*` or call `orchestrator-herdr`.
- Prompt a working, blocked, or unknown agent.
- Run bare `herdr`, `herdr server stop`, or kill Herdr.
- Close panes or tabs you did not create.
- Put machine paths, secrets, or sample pane IDs into prompts.
