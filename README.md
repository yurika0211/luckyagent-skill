# luckyagent-skill

Community skills and reusable workflows for [LuckyAgent](https://github.com/yurika0211/LuckyAgent) users.

> **Status:** Repository initialized. No skills are included yet.

## What this project is

`luckyagent-skill` is the future home for user-oriented LuckyAgent skills: focused, reusable instructions and supporting resources that help LuckyAgent users complete practical tasks more reliably.

The repository is intentionally starting empty of actual skills. Skills will be added after their scope, activation conditions, documentation, and validation requirements are agreed upon.

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
