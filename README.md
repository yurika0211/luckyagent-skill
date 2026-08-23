# luckyagent-skill

Community skills and reusable workflows for [LuckyAgent](https://github.com/yurika0211/LuckyAgent) users.

> **Status:** Repository initialized with three Obsidian skills. More skills may be added later.

## What this project is

`luckyagent-skill` is the future home for user-oriented LuckyAgent skills: focused, reusable instructions and supporting resources that help LuckyAgent users complete practical tasks more reliably.

The repository currently includes these Obsidian-focused skills:

- [`obsidian-markdown`](./obsidian-markdown) — Create and edit Obsidian Flavored Markdown with properties, wikilinks, embeds, callouts, and tags.
- [`obsidian-cli`](./obsidian-cli) — Use the official Obsidian CLI for vault search, backlinks, tags, tasks, properties, bases, templates, and other index-powered operations.
- [`obsidian-bases`](./obsidian-bases) — Create and edit Obsidian Bases with filters, formulas, and table, card, list, or map views.

Each skill is self-contained and includes its own `SKILL.md`.

## Planned structure

A skill will normally live in its own directory:

```text
skill-name/
├── SKILL.md          # Required skill instructions and metadata
├── agents/           # Optional UI metadata
├── references/       # Optional detailed reference material
├── scripts/          # Optional helper scripts
└── assets/           # Optional supporting assets
```

## Contributing

Before adding a skill:

1. Open an issue describing the user problem and intended workflow.
2. Keep the skill focused on one coherent capability.
3. Document when the skill should and should not be used.
4. Avoid secrets, credentials, private data, and environment-specific assumptions.
5. Add examples and validation steps where they improve reliability.
6. Keep `SKILL.md` concise; move deep reference material into linked files.

## License

MIT. See [LICENSE](LICENSE).
