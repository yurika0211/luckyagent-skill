---
name: aoci-code
description: Operate AOCI-CODE for coding agents — install/verify aoci CLI, init+scan repos, wire MCP (Codex/Claude/Cursor/OpenCode), build and maintain governed Whole-Index (aoci.txt/aoci.code.txt), Overview+Attestation, doctor/verify/check/ui, optional Database Cognition. Use for AOCI, AOCI-CODE, aoci CLI, agent repo maps, aoci_rules/overview/maintain, or persistent Git-versioned project cognition.
metadata:
  short-description: Governed AOCI-CODE workflows for repo cognition
---

# AOCI-CODE

Local-first governed cognition layer for coding agents. **AOCI** is the method; **AOCI-CODE** is the CLI + MCP implementation.

This skill is a workflow adapter around the `aoci` binary. Runtime truth is always:

1. `aoci --version` / `aoci --json capabilities`
2. live Guide / MCP tool schemas from the running binary
3. repo files: `aoci.txt`, `aoci.meta.txt`, `aoci.code.txt`, optional `aoci.database.txt`, `.aoci/`

Do not invent MCP tool names, Guide states, or batch schemas. Do not treat AOCI as RAG, AST, CodeGraph, daemon, or cloud sync.

Upstream project: https://github.com/aoci-spec/aoci-code

## Preconditions

```bash
command -v aoci || test -x "$HOME/.local/bin/aoci"
aoci --version
# preferred stable install path after build/copy:
# $HOME/.local/bin/aoci
```

If missing: install a signed release from the upstream Releases page, or build from source:

```bash
git clone https://github.com/aoci-spec/aoci-code.git aoci-code
cd aoci-code
go mod verify
mkdir -p build && make build
mkdir -p "$HOME/.local/bin"
cp -f build/aoci "$HOME/.local/bin/aoci"   # Windows: aoci.exe
chmod +x "$HOME/.local/bin/aoci"
aoci --version
```

Always pass an absolute binary path into host MCP configs. Prefer:

```bash
AOCI_BIN="$(command -v aoci)"
REPO="$(pwd -P)"   # must be absolute
aoci --repo "$REPO" <cmd>
```

Helper: `scripts/resolve_aoci.sh` prints a candidate `AOCI_BIN`.

## Decision tree

| User intent | Path |
|---|---|
| Install / upgrade CLI only | Preconditions + `doctor` |
| First-time wire a project | **Workflow A** then stop for MCP reload |
| Build first index | **Workflow B** (MCP required) |
| Normal coding with AOCI already set up | **Workflow C** |
| Context compacted / lost system view | **Workflow D** |
| Database tables cognition | **Workflow E** |
| Status / panel / diagnose | **Workflow F** |
| Uninstall / rollback questions | Read upstream docs; do not improvise destructive steps |

Detailed notes: `references/workflows.md`.

## Workflow A — Init + scan (no index yet)

Target must be a git repo. From the target repository root:

```bash
aoci --repo "$REPO" doctor
aoci --repo "$REPO" init --locale zh-CN --agent <codex|claude|opencode|cursor>
aoci --repo "$REPO" scan
```

Rules:

- `init` writes Root/Meta/empty Code Volume + agent rules. It does **not** invent business semantics.
- `scan` is mandatory. It writes Baseline. Without it, Guide blocks with `baseline_missing`.
- Host config files (`.mcp.json`, `.codex/config.toml`, `opencode.json`, `.claude/settings.json`, …) embed **machine-bound absolute paths**. `init` gitignores them; **never commit them**.
- Do **not** gitignore cognition assets: `aoci.txt`, `aoci.meta.txt`, `aoci.code.txt`, `AGENTS.md`. Ignored assets are skipped by scan and the index never forms.
- Optional: `init --hooks` only when user explicitly wants host hooks (Claude PreToolUse / Codex compact handoff). Review/trust hooks in the host UI when required.
- Cursor may only print a reference snippet; paste manually if needed.
- After MCP config is written: if current session does not show AOCI tools, refresh/reopen project session. **Stop before building the index** until MCP is live (unless host hot-reloads and tools are already visible).

Suggested user message after A:

> MCP 已写入。请重启/重载会话后再让我建立索引。

## Workflow B — Build first index (Volumes / fresh path)

Requires AOCI MCP tools in the current host session.

Order (Fresh / Volumes default — current `init` layout):

1. Confirm tools exist (`aoci_rules`, `aoci_overview`, `aoci_maintain`, `aoci_update_entry`, …).
2. `aoci_rules` once.
3. Follow **live Guide** / capability contract from the binary. Do not hard-code stage machines from memory.
4. Call ordinary no-argument `aoci_maintain`.
5. For the issued batch: author FRAS entries from **source evidence**, keep `source_sha256` bindings, submit the **complete current machine batch** in one `aoci_update_entry`.
6. Handle result: `applied` | `repair_required` | `stopped`. Repair only via the prescribed path.
7. CLI: `aoci --repo "$REPO" verify` then `aoci --repo "$REPO" check`.
8. Re-read Guide. Repeat Maintain only when a successful batch reports remaining work.
9. Optional panel: `aoci --repo "$REPO" ui --detach --json`.

Do **not** use Legacy-only onboarding commands on a fresh Volumes repo:

- `status --deep`
- `index score`
- `index agent plan`

Those are Legacy workflow surfaces, not Fresh onboarding.

Large repos take time (upstream ballpark: ~200kLOC ≈ 1 hour depending on model). Batches can resume after interrupt by calling Maintain again.

## Workflow C — Daily task with existing index

1. If rules not already reliable in context → `aoci_rules`.
2. Establish one complete ordinary `aoci_overview` (not `check_only`) + continuation + Attestation per contract.
3. While cognition remains reliable: **do not** re-dump Whole-Index every tool call.
4. Local doubts → source, tests, then `aoci_get_entries` / `aoci_search`.
5. After code/tests stabilize, end with `aoci_maintain` and complete any issued `aoci_update_entry` batch so cognition returns `aligned`.
6. `verify` / `check` when closing a cognition-changing change set.

Overview rules (critical):

- Body is start marker + exact formal index bytes + end marker.
- If `continuation_required=true`, auto-follow `next_cursor` until complete. Do not ask the user to continue; do not start business work mid-chain.
- Before Attestation completes: do not treat memory, raw `aoci.txt` file reads, or partial search as proof of complete cognition.
- `check_only=true` is a compact checkpoint only — never a substitute for full Overview when establishing cognition.

## Workflow D — Context compaction / reload

On known host compaction:

1. If rules are gone → `aoci_rules`.
2. Declare `context_compaction` with a **fresh event id** on ordinary Overview inputs (per live schema).
3. Complete cursor → confirmation → Attestation sequence.
4. Do not use `check_only` or a probe as replacement.
5. After fresh transport, if Attestation is partial/failed, continue **source-bound** work per contract; do not auto-fire a second Overview unless required.

Compacted handoff may keep receipt identity and unfinished write/Recovery state only — never Whole-Index semantics.

## Workflow E — Database Cognition (optional)

Only when user wants DB cognition. Engines: PostgreSQL, MySQL, limited openGauss 6.0.5.

```bash
aoci --repo "$REPO" database source add \
  --source-id primary \
  --engine postgresql \
  --database-name app \
  --namespace public
# credential env derived e.g. AOCI_DB_PRIMARY_DSN — set outside chat; never paste DSN/secrets into chat or index
aoci --repo "$REPO" database source access --source primary --json
```

Then follow live Guide / explicit database evidence → accept evidence hash → model authors table FRAS → maintain/update_entry binding. AOCI reads schema only (no business rows, no DDL/DML). Credentials are env **names**, never stored values.

## Workflow F — Diagnose / panel / identity

```bash
aoci --repo "$REPO" doctor
aoci --repo "$REPO" --json capabilities
aoci --repo "$REPO" status
aoci --repo "$REPO" verify
aoci --repo "$REPO" check
aoci --repo "$REPO" ui --detach --json
```

Running MCP identity comes from tool receipts (`cognition_receipt.mcp_service_version`, `runtime_repository_root`), not only files on disk. Replacing the binary does not change an already-running MCP process — reload host after upgrade.

## MCP tool surface (fixed 9)

| Kind | Tools |
|---|---|
| Read | `aoci_rules`, `aoci_overview`, `aoci_get_entries`, `aoci_search` |
| Maintain | `aoci_maintain`, `aoci_update_entry`, `aoci_remove_entry` |
| Aux | `aoci_header`, `aoci_report` |

Some hosts prefix names (`aoci_aoci_rules`). Same nine identities underneath.

`aoci mcp` is stdio; stdout is JSON-RPC only.

## Hard don'ts

- Don't commit host MCP/agent absolute-path configs.
- Don't gitignore `aoci.txt` / `aoci.meta.txt` / `aoci.code.txt` / `AGENTS.md`.
- Don't build index before Baseline `scan`.
- Don't skip Attestation and claim full-system mastery.
- Don't paste DB DSNs, passwords, tokens into chat, commits, or cognition files.
- Don't restate or fork the Guide state machine in wrappers; follow live Guide + schemas.
- Don't pretend file-segment reads of `aoci.txt` equal MCP Overview acceptance.
- Don't hard-code machine-specific absolute paths in this skill or in shared configs.

## Docs to open on demand

From an AOCI-CODE checkout or upstream tree:

- `docs/getting-started.md`
- `docs/agent-integrations.md`
- `docs/overview-delivery.md`
- `docs/cognition-volumes.md`
- `docs/install.md`
- `README.zh-CN.md` / `README.md`

Skill deep notes: `references/workflows.md`

## Minimal user prompts (official shape)

Init phase:

```text
请用本机 aoci 为该仓库 init + scan，接入当前宿主 MCP。先不要建索引；MCP 生效后停下告诉我。
```

After reload:

```text
确认 AOCI MCP 可用，然后建立 AOCI 索引；完成后给面板链接。
```

Reload cognition:

```text
请仅通过 AOCI 建立对本项目的整体框架认知，报告掌握程度，并说明是否可接手开发。
```
