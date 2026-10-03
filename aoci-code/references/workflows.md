# AOCI-CODE workflow reference

Companion to SKILL.md. Prefer live `aoci` help, Guide, and MCP schemas when they disagree with this file.

## Install identity

- Prefer a stable absolute path such as `$HOME/.local/bin/aoci` (or `aoci.exe` on Windows).
- Release package identity and source-build identity may differ by commit suffix; report what `aoci --version` prints.

Build from source:

```bash
go mod verify
mkdir -p build
make build
./build/aoci --version
```

## Init flags

```bash
aoci --repo /abs/repo init --locale zh-CN --agent codex
aoci --repo /abs/repo init --locale zh-CN --agent claude
aoci --repo /abs/repo init --locale zh-CN --agent claude --hooks
aoci --repo /abs/repo init --locale zh-CN --agent opencode
aoci --repo /abs/repo init --locale zh-CN --agent cursor
```

Host files are machine-local. Re-running `init` on another machine with committed broken paths may silently keep bad entries if keys already exist — another reason never to commit them.

## Scan

```bash
aoci --repo /abs/repo scan
aoci --repo /abs/repo scan --dry-run
aoci --repo /abs/repo scan --force   # only when intentionally replacing Baseline
```

Scan uses git ignore authority. Cognition assets must stay tracked/unignored.

## Fresh Volumes maintenance loop

```text
scan (Baseline)
 → live Guide
 → aoci_maintain (no args)
 → author full current batch from source
 → aoci_update_entry (complete batch, keep source_sha256)
 → verify + check + Guide
 → repeat Maintain while remaining work is reported
```

`aoci cognition bootstrap` is **not** for an already-initialized Volumes v1 skeleton. Zero-entry Volumes: scan → Guide → maintain.

## Overview delivery knobs

- `overview_delivery.chunk_tokens`: default 7000, range 4000–24000
- Host truncation → fail closed; user may lower chunk size and restart chain
- Maintain transport budget: `maintain_transport_budget_bytes` (default 24KiB; claude init may start 40KiB)

```bash
aoci --repo /abs/repo config set overview_delivery.chunk_tokens 7000
aoci --repo /abs/repo config set maintain_transport_budget_bytes 24576
```

## MCP command shape

```bash
/abs/aoci --repo /abs/repo mcp
```

Wire that exact argv into host MCP config.

## verify / check caveats

“Read-only” means they do not modify formal index/Baseline. They may still append local ledger / verify history when enabled. For true zero writes, use an isolated copy.

## Doctor

```bash
aoci --repo /abs/repo doctor
aoci --repo /abs/repo doctor --net   # only when user wants endpoint probe
```

Offline by default.

## UI

```bash
aoci --repo /abs/repo ui --detach --json
```

Return the panel link from JSON to the user.

## Database quick path

```bash
aoci --repo /abs/repo database source add --source-id primary --engine postgresql --database-name app --namespace public
aoci --repo /abs/repo database source access --source primary --json
# admin sets AOCI_DB_PRIMARY_DSN outside the agent chat
```

Schema-only. No secret values in git or chat.

## System cognition (derived observations)

```bash
aoci --repo /abs/repo cognition system lineage
aoci --repo /abs/repo cognition system relations
aoci --repo /abs/repo cognition system impact --object database://primary/public/orders
```

Derived views only — not a second authority layer.

## Upgrade note

After replacing `aoci` on disk, reload MCP host sessions. Confirm `cognition_receipt.mcp_service_version` and `runtime_repository_root` on next maintain/overview check_only.
