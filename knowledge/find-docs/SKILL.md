---
name: find-docs
description: Retrieve current library/framework/SDK docs and examples before coding against an API. Use for React, Next.js, Vue, Prisma, Tailwind, Django, FastAPI, cloud SDKs, CLIs, and any version-sensitive API question. Prefer live docs over training memory.
version: 1.0.0
license: MIT
metadata:
  tags: [docs, api, libraries, context7, research]
---

# Find docs — current API references

## When to use
- "How do I configure X?"
- API signatures, options, migrations
- Setup/install for a named library
- Debugging behavior that may have changed by version

## When not to use
- Pure algorithm/puzzle with no library
- Project-local code truth already in the repo (read the repo first)

## Resolution order
1. If `ctx7` / Context7 CLI exists:
   ```bash
   ctx7 library <name> "<what you need>"
   # then query docs with the resolved library id
   ```
2. Official docs via `web_search` → `web_fetch` / defuddle.
3. GitHub README/docs in the upstream repo.
4. Only then fall back to built-in knowledge, and label it as unverified.

## Workflow
1. Identify library + version constraint (from package.json, go.mod, requirements, user text).
2. Fetch current docs for that version.
3. Quote only the relevant API bits.
4. Implement with the verified surface; don't invent flags.

## Quality bar
- Version noted when known
- Link to source docs
- No confident outdated API guesses
