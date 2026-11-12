---
name: defuddle
description: Extract clean Markdown from web pages with Defuddle CLI (strips nav/ads/clutter). Prefer for articles, docs pages, and blog posts when a URL must be read with minimal tokens. Falls back to opencli web_read or web_fetch if Defuddle is unavailable.
version: 1.0.0
license: MIT
metadata:
  tags: [web, markdown, extraction, defuddle, research]
---

# Defuddle — clean URL → Markdown

## When to use
- User gives a URL to read/analyze
- Docs, blog posts, articles, changelogs
- Need lower-noise text than raw HTML

## When not to use
- Authenticated-only app pages better handled by browser/site adapters
- Non-HTML binaries (PDF/DOCX) — use document skills instead

## Install check
```bash
command -v defuddle || npm install -g defuddle
```

## Usage
Always prefer Markdown output:

```bash
defuddle parse <url> --md
defuddle parse <url> --md -o content.md
defuddle parse <url> -p title
```

| Flag | Meaning |
|------|---------|
| `--md` | Markdown (default choice) |
| `--json` | HTML + markdown |
| `-p <prop>` | metadata field |

## LuckyAgent fallback order
1. `defuddle parse URL --md`
2. `opencli` action `web_read`
3. `web_fetch`
4. Site-specific `opencli` adapters when the domain has one

## Workflow
1. Run extraction.
2. Keep title + core body; drop chrome.
3. Cite the URL in the answer.
4. If extraction is empty/paywalled, say so and stop guessing.
