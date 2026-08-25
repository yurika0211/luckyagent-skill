# luckyagent-skill

Community skills and reusable workflows for [LuckyAgent](https://github.com/yurika0211/LuckyAgent) users.

> **Status:** Repository initialized with three Obsidian skills; more skills have been added since.

## What this project is

`luckyagent-skill` is the future home for user-oriented LuckyAgent skills: focused, reusable instructions and supporting resources that help LuckyAgent users complete practical tasks more reliably.

The repository currently includes these skills:

- [`obsidian-markdown`](./obsidian-markdown) — Create and edit Obsidian Flavored Markdown with properties, wikilinks, embeds, callouts, and tags.
- [`obsidian-cli`](./obsidian-cli) — Use the official Obsidian CLI for vault search, backlinks, tags, tasks, properties, bases, templates, and other index-powered operations.
- [`obsidian-bases`](./obsidian-bases) — Create and edit Obsidian Bases with filters, formulas, and table, card, list, or map views.
- [`find-nearby`](./find-nearby) — Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with coordinates, addresses, cities, zip codes, or Telegram location pins. No API keys needed.
- [`karpathy-ponytail`](./karpathy-ponytail)
- [`resume-audit`](./resume-audit) — Résumé verification main entry: claim extraction → timeline → domain attribution → external checks → seven-tier evidence report + interview questions.
- [`github-audit`](./github-audit) — Audit the real scale and domain attribution of open-source contributions (per-PR diff classification).
- [`project-check`](./project-check) — Check project-description fit, personal contribution boundaries, and project-type difficulty baselines.
- [`blog-check`](./blog-check) — Verify blog originality (whole-paragraph verbatim comparison + hit rate).
- [`credential-check`](./credential-check) — Verify papers/patents/competitions/certificates against authoritative sources.
- [`pipeline-pattern`](./pipeline-pattern) — Detect structural similarity across batch résumés (weight-only, never used for elimination).
- [`grill`](./grill) — Generate 3–6 trap-laden interview questions with opening scripts and scoring rubrics. — Behavioral guidelines merging Andrej Karpathy's LLM coding observations with Ponytail's laziness ladder (think before coding, simplicity, surgical changes, root-cause fixes).

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
