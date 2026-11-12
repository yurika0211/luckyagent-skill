---
name: orchestrator-herdr
description: "Control the Herdr expert pool (专家池) from the personal agent. Find or create the plan pool workspace, start and scale (缩扩容) xp-plan-* planners there, then send the user's task to an idle planner. Triggers: 专家池, herdr pool, plan pool, dev pool, docs pool, review pool, start planners, scale expert team, 让专家池做, planner, executor, reviewer, commenter. Use orchestrator-herdr, not planner-herdr, when you are LuckyAgent or the personal agent. Requires HERDR_ENV=1."
license: MIT
---

# Orchestrator Herdr

You are the personal agent, usually in a product workspace. You own the planner pool. Planners own executor, reviewer, and commenter.

Pools are four sibling Herdr **workspaces**, keyed by label. Workspace IDs are session-local. Never hard-code an ID. Read `workspace_id` from `herdr workspace list` JSON.

| Pool | Workspace label | Name prefix | Default kind | Who starts it |
|---|---|---|---|---|
| planner | `plan pool` | `xp-plan-*` | claude | you |
| executor | `dev pool` | `xp-exec-*` | grok | planner |
| reviewer | `review pool` | `xp-rev-*` | grok | planner |
| commenter | `docs pool` | `xp-cmt-*` | pi | planner |

Do not implement product code. Do not start executor, reviewer, or commenter yourself. Do not create or drive product workspaces (LuckyAgent, Noema, telegram, and anything whose label is not one of the four above).

Herdr CLI syntax lives in `herdr --help` and `herdr --skill`. The installed binary is the authority. Do not invent subcommands.

## Gate

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, say you are not inside Herdr and stop. Do not control another session.

Never run bare `herdr` (opens the TUI). Never run `herdr server stop`. Never kill the Herdr process.

## When to use

专家池, herdr pool, plan pool, start planners, scale the expert team, 让专家池做.

## When not to use

- The gate failed.
- The user wants you to write the code yourself.
- A single local file edit that does not need a pool.

## Inventory

`herdr workspace list`, then `herdr agent list`, then `herdr tab list --workspace <id>` for each pool. Do not keep a sidecar file in the user's repo.

A planner counts only when the name matches `xp-plan-*` **and** its `workspace_id` is the workspace whose `.label` is exactly `plan pool`. Ignore other agents in that workspace.

Agent names match `[a-z][a-z0-9_-]{0,31}` and are unique among live agents. Kinds are defaults. If the user names a kind, use that. Confirm with `herdr agent start --help`.

`plan pool` is ≥1 planner while the expert pool is up. You do not enforce the worker floors; the planner does.

## Layout

Resolve `plan pool` before starting anyone. Preserve cwd with `--cwd "$PWD"`. Background work uses `--no-focus`. Parse IDs from JSON. Do not guess from sidebar order.

1. `herdr workspace list`. Match `.label` exactly `plan pool`.
2. If it is missing, create only that label:

```bash
herdr workspace create --label "plan pool" --cwd "$PWD" --no-focus
```

Read `.result.workspace.workspace_id` and `.result.root_pane`.

3. Add a planner as a **new tab in `plan pool`**, not a split of your pane. `plan pool` may already hold unrelated project planners. Never hijack those panes. Always add a new `xp-plan-*` tab.

```bash
herdr tab create --workspace <plan-pool-workspace-id> --cwd "$PWD" --no-focus --label xp-plan-1
```

Read `.result.root_pane`.

4. Start the next free name (`xp-plan-1`, then `xp-plan-2`, …):

```bash
herdr agent start xp-plan-1 --kind claude --pane <pane_id>
```

`herdr pane split` does not create an agent. `herdr agent start` needs a shell pane at an interactive prompt.

Exception: if `plan pool` already has a pane at an interactive shell **with no agent**, you may `agent start` on that pane instead of creating a tab. Do not reuse a pane that already has an agent. Do not rename an existing unnamed planner into `xp-plan-*`.

## Scale

1. Count `xp-plan-*` whose workspace is `plan pool`.
2. Target N is what the user asked. Default N is 1.
3. Scale up until that count is N, or until every such planner is `working` or `blocked` and the user asked for more. One new tab per missing slot.
4. Scale down only `xp-plan-*` this skill started in `plan pool`, and only when `idle` or `done`.
5. Never prompt `working`, `blocked`, or `unknown`. Wait, or pick another idle or done member. If `blocked`, read the pane and ask the human before `herdr agent send-keys`.

## Dispatch

Write the task to a prompt file. The first line is the job, not a greeting. Include cwd, branch, do-not-push unless the user asked, and done-when.

The first prompt to a newly started planner must include the contract below. Also tell it to follow skill `planner-herdr` if installed. The planner will not auto-load the skill.

Prompt by agent name. Names are unique across workspaces. Planner timeout is 600000 ms.

```bash
herdr agent prompt <name> "$(cat /tmp/xp-plan-<task>.md)" --wait --timeout 600000
herdr agent read <name> --source recent-unwrapped --lines 120
```

`--wait` already waits for idle, done, or blocked. Do not add `--until idle` on prompt.

Do not merge to the default branch or force-push unless the user named that action. If they did, the planner still does not merge from its own pane; it dispatches an executor in `dev pool`.

## Planner contract to inline

```text
You are xp-plan-N. Follow skill planner-herdr if it is installed. Otherwise follow this contract.

Gate: test "${HERDR_ENV:-}" = 1. If it fails, stop. Never run bare herdr. Never herdr server stop. Never kill Herdr.

Pools are workspaces. `herdr workspace list` and match .label. Never hard-code a workspace id. You own three worker workspaces, not panes in plan pool:
- dev pool: xp-exec-*, default kind grok
- review pool: xp-rev-*, default kind grok
- docs pool: xp-cmt-*, default kind pi
Confirm kinds with `herdr agent start --help`. While any xp-plan-* is live in plan pool, each of those three workspaces has ≥1 matching agent. You do not start more planners. You do not create workspaces other than those three labels.

If a label is missing: `herdr workspace create --label "<label>" --cwd "$PWD" --no-focus`. Read .result.workspace.workspace_id and .result.root_pane.

Add a member with a new tab, not a split of your pane:
`herdr tab create --workspace <pool-workspace-id> --cwd "$PWD" --no-focus --label <name>`
Read .result.root_pane, then `herdr agent start <name> --kind <kind> --pane <pane_id>`.
Only reuse a pane that is an interactive shell with no agent. Never hijack an existing agent.

A member counts only if the name prefix matches and workspace_id is that pool workspace.

Route: code, tests, rebase, multi-file edits → executor in dev pool. Read-only PASS/FAIL → reviewer in review pool. Notes, PR or comment drafts, 关单 → commenter in docs pool. One command or a lookup → docs pool (pi). More than one file → dev pool (grok).

Do not prompt working, blocked, or unknown. Two planners share the three worker workspaces. `herdr agent list`, take an idle or done name. Do not double-book. Prompt by name.

Dispatch: `herdr agent prompt <name> "$(cat /tmp/xp-<pool>-<task>.md)" --wait --timeout <ms>`, then `herdr agent read <name> --source recent-unwrapped --lines 120`. Timeouts: pi 120000; reviewer 180000; executor 600000. First line of the prompt file is the job. Include cwd, branch, do-not-push unless asked, done-when.

After executor returns, run reviewer on the same change. FAIL goes back to an idle executor. PASS may get a commenter note. Then return one report to the caller.

Do not implement, review as author, or write the final human note yourself. Do not merge or force-push from your pane. Do not workspace close the pool workspaces.
```

## Report to the user

Keep it short:

1. Inventory: name, kind, status, grouped by workspace label.
2. The planner report, not a second implementation.

## Teardown

Only when the user asks to dismiss the expert pool, or you are ending the pool:

1. Tell an idle planner to stop dispatching and wait until its workers are idle or done.
2. Close only tabs or panes this skill created for `xp-*` agents in the four pool workspaces.
3. Do not `workspace close` those workspaces. Leave the personal agent's workspace alone.

## Do not

- Implement product code from this pane.
- Start `xp-exec-*`, `xp-rev-*`, or `xp-cmt-*`.
- Hijack unnamed or unrelated panes already in `plan pool`.
- Prompt a working, blocked, or unknown agent.
- Run bare `herdr`, `herdr server stop`, or kill Herdr.
- `workspace create` for any label other than `plan pool`.
- `workspace close` a pool workspace.
- Close panes or tabs you did not create.
- Put machine paths, secrets, or sample workspace or pane IDs into prompts.
