---
name: obsidian-cli
description: >
  Use the official Obsidian CLI (1.12+) for vault operations.
  Prefer CLI for index-powered ops (search, backlinks, tags, tasks, properties, bases).
  Fall back to file tools when Obsidian is not running or for simple read/write.
triggers:
  - obsidian cli
  - vault search
  - backlinks
  - vault tags
  - vault tasks
  - property set
  - base query
---

# Obsidian CLI — Agent Reference

## When to Use CLI vs File Tools

**Use CLI** when you need Obsidian's index or app features:
search, backlinks, links, tags, tasks, properties, bases, templates, outline, orphans, unresolved links

**Use file tools** for:
simple file read/write, bulk text replacement, grep across files — no app dependency

## ⚠️ Critical Gotchas (Silent Failures)

Without this skill, these commands **succeed with exit code 0 but return wrong/empty data**:

| Trap | Wrong result | Fix |
|------|-------------|-----|
| `tasks todo` | 0 results (scoped to active file only) | `tasks all todo` |
| `tags counts` | empty | `tags all counts` |
| `properties format=json` | returns YAML, not JSON | `properties format=tsv` |
| `search query="x"` | plain text, no structure | `search query="x" format=json matches` |
| `create name="x"` | opens Obsidian UI (blocking) | add `silent` flag |
| Error parsing | `$?` = 0 despite errors | parse output for `Error:` |

## Syntax Basics

```
obsidian <command> [param=value ...] [flag ...]
```

- **Vault targeting**: `vault="My Vault"` as first param, or run from inside vault dir
- **File targeting**: `path=exact/path.md` vs `file=name` (link-style resolution)
- **Params**: `key=value` — quote values with spaces: `name="My Note"`
- **Flags**: boolean switches, no `=` — e.g. `silent`, `overwrite`, `counts`, `total`
- **Structured output**: `format=json` (search, base:query), `format=tsv` (properties, tags)

## Key Commands

### Read & Write
```sh
obsidian read path=note.md
obsidian append path=note.md content="new content"
obsidian prepend path=note.md content="frontmatter content"
obsidian create path=new-note.md content="body" silent
obsidian delete path=note.md
```

### Search
```sh
obsidian search query="keywords" format=json matches
obsidian search query="section:content" format=json matches
```

### Tags
```sh
obsidian tags all counts
obsidian tags all format=json
```

### Tasks
```sh
obsidian tasks all todo
obsidian tasks all done
obsidian tasks all due:today
```

### Properties
```sh
obsidian properties path=note.md format=tsv
obsidian properties path=note.md set key=value
obsidian properties path=note.md remove key
```

### Backlinks & Links
```sh
obsidian backlinks path=note.md format=json
obsidian links path=note.md format=json
obsidian unresolved
```

### Bases
```sh
obsidian base:query path=base.base format=json
```

### Templates
```sh
obsidian templates list
obsidian templates apply template="Daily Note" path=target.md silent
```

### Utilities
```sh
obsidian orphans
obsidian outline path=note.md
obsidian stats
```