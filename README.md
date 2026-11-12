# luckyagent-skill

Community skills and reusable workflows for [LuckyAgent](https://github.com/yurika0211/lucky-agent) users.

## What this project is

Focused, reusable `SKILL.md` workflows that help LuckyAgent complete practical tasks more reliably. Each skill is self-contained and MIT-licensed unless a skill directory says otherwise.

## Skills

### Herdr expert pools
- [`orchestrator-herdr`](./herdr/orchestrator-herdr) — Personal agent starts and scales the planner pool, then relays the planner report
- [`planner-herdr`](./herdr/planner-herdr) — Planner pool member runs executor, reviewer, and commenter pools

### Figma (Figma Developer Terms)
Source: [openai/skills](https://github.com/openai/skills) curated set. Requires Figma MCP / `use_figma`. Each skill directory has its own `LICENSE.TXT` (not MIT).
- [`figma`](./figma/figma) — Figma MCP entry: design context, screenshots, assets → code
- [`figma-use`](./figma/figma-use) — Mandatory prep before every `use_figma` call
- [`figma-implement-design`](./figma/figma-implement-design) — Figma → production UI with visual parity
- [`figma-generate-design`](./figma/figma-generate-design) — App/page layout → Figma
- [`figma-generate-library`](./figma/figma-generate-library) — Codebase → Figma design system / library
- [`figma-create-new-file`](./figma/figma-create-new-file) — Create a blank Figma/FigJam file
- [`figma-create-design-system-rules`](./figma/figma-create-design-system-rules) — Generate project design-system rules
- [`figma-code-connect-components`](./figma/figma-code-connect-components) — Map Figma components to code (Code Connect)

### Design / UI
- [`better-ui`](./better-ui/better-ui) — Visual polish, motion, icons, surfaces
- [`better-layout`](./better-ui/better-layout) — Spacing, grouping, responsive structure
- [`better-colors`](./better-ui/better-colors) — Tokens, contrast, palettes
- [`better-typography`](./better-ui/better-typography) — Type scale and readability
- [`better-accessibility`](./better-ui/better-accessibility) — Keyboard, focus, ARIA minima
- [`better-writing`](./better-ui/better-writing) — UX microcopy
- [`better-interface`](./better-ui/better-interface) — Full interface review orchestrator

### Office documents
- [`docx`](./office/docx) — Word documents
- [`pdf`](./office/pdf) — PDF read/create/merge/split
- [`pptx`](./office/pptx) — Slides / decks
- [`xlsx`](./office/xlsx) — Spreadsheets and CSV cleanup

### Knowledge & notes
- [`obsidian-markdown`](./obsidian/obsidian-markdown) — Obsidian Flavored Markdown
- [`obsidian-cli`](./obsidian/obsidian-cli) — Official Obsidian CLI workflows
- [`obsidian-bases`](./obsidian/obsidian-bases) — Obsidian Bases (`.base`)
- [`find-docs`](./knowledge/find-docs) — Current library/framework docs before coding
- [`defuddle`](./knowledge/defuddle) — Clean URL → Markdown extraction

### Review
- [`review-agent`](./review/review-agent) — Read-only, defect-first review of a code change
- [`security-review`](./review/security-review) — Auth, JWT, OAuth, IDOR, and secret-handling audit
- [`owasp`](./review/owasp) — OWASP 2021 Top 10 audit with file-level findings
- [`secure`](./review/secure) — Full-stack security posture score
- [`preflight`](./review/preflight) — Read-only pre-deploy gate: build, tests, secrets, status
- [`bug-triage`](./review/bug-triage) — Rank bugs and issues with reproduction evidence
- [`root-cause`](./review/root-cause) — Hypothesis-driven debugging to a proven cause

### Other
- [`find-nearby`](./other/find-nearby) — Nearby places via OpenStreetMap
- [`karpathy-ponytail`](./other/karpathy-ponytail) — Coding behavior guidelines
- [`imagegen`](./other/imagegen) — Raster image generation/editing via LuckyAgent
- [`aoci-code`](./other/aoci-code) — AOCI-CODE CLI/MCP workflows: init+scan, Overview, maintain Whole-Index

## Skill layout

Group folders (`herdr/`, `figma/`, `better-ui/`, `office/`, `obsidian/`, `review/`, `knowledge/`, `other/`) are repo organization only. LuckyAgent still expects `<skillsDir>/<skill-name>/SKILL.md` at install time (flatten or copy the inner skill dir).

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

MIT for this repository’s original content. See [LICENSE](LICENSE).

Individual skill directories may carry a different license (for example the Figma set uses the [Figma Developer Terms](https://www.figma.com/legal/developer-terms/)). Always check the skill’s own `LICENSE` / `LICENSE.TXT` before redistributing.
