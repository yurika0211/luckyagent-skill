# luckyagent-skill

Community skills and reusable workflows for [LuckyAgent](https://github.com/yurika0211/lucky-agent) users.

## What this project is

Focused, reusable `SKILL.md` workflows that help LuckyAgent complete practical tasks more reliably. Each skill is self-contained and MIT-licensed unless a skill directory says otherwise.

## Skills

### Knowledge & notes
- [`obsidian-markdown`](./obsidian-markdown) — Obsidian Flavored Markdown
- [`obsidian-cli`](./obsidian-cli) — Official Obsidian CLI workflows
- [`obsidian-bases`](./obsidian-bases) — Obsidian Bases (`.base`)
- [`find-docs`](./find-docs) — Current library/framework docs before coding
- [`defuddle`](./defuddle) — Clean URL → Markdown extraction

### Office documents
- [`docx`](./docx) — Word documents
- [`pdf`](./pdf) — PDF read/create/merge/split
- [`pptx`](./pptx) — Slides / decks
- [`xlsx`](./xlsx) — Spreadsheets and CSV cleanup

### Design / UI
- [`better-ui`](./better-ui) — Visual polish, motion, icons, surfaces
- [`better-layout`](./better-layout) — Spacing, grouping, responsive structure
- [`better-colors`](./better-colors) — Tokens, contrast, palettes
- [`better-typography`](./better-typography) — Type scale and readability
- [`better-accessibility`](./better-accessibility) — Keyboard, focus, ARIA minima
- [`better-writing`](./better-writing) — UX microcopy
- [`better-interface`](./better-interface) — Full interface review orchestrator
- [`imagegen`](./imagegen) — Raster image generation/editing via LuckyAgent

### Hiring / verification
- [`resume-audit`](./resume-audit) — Résumé verification entry
- [`github-audit`](./github-audit) — Contribution substance audit
- [`project-check`](./project-check) — Project claim vs reality
- [`blog-check`](./blog-check) — Technical writing originality checks
- [`credential-check`](./credential-check) — Papers/patents/certs verification
- [`pipeline-pattern`](./pipeline-pattern) — Batch résumé template similarity
- [`grill`](./grill) — Interview question generation

### Other
- [`find-nearby`](./find-nearby) — Nearby places via OpenStreetMap
- [`karpathy-ponytail`](./karpathy-ponytail) — Coding behavior guidelines

## Skill layout

```text
skill-name/
├── SKILL.md          # required
├── agents/           # optional UI metadata
├── references/       # optional deep docs
├── scripts/          # optional helpers
└── assets/           # optional assets
```

## Contributing

1. Keep one coherent capability per skill.
2. Document when to use / when not to use.
3. No secrets, credentials, or machine-specific paths.
4. Prefer concise `SKILL.md`; put long reference material in `references/`.
5. Open a PR with a short rationale.

## License

MIT. See [LICENSE](LICENSE).
