---
name: better-colors
description: Practical product color work — OKLCH-minded palettes, contrast, semantic tokens, light/dark pairs, accent usage. Use for theme tokens, palette generation, and contrast fixes.
version: 1.0.0
license: MIT
metadata:
  tags: [ui, color, design-tokens, a11y]
---

# better-colors

## Principles
1. Prefer perceptual spaces (OKLCH/LCH mindset) for even steps.
2. Define semantic tokens (`bg`, `fg`, `muted`, `border`, `accent`, `danger`) not raw blues everywhere.
3. Body text contrast: aim WCAG AA minimum; critical text higher.
4. Don't encode information by color alone.
5. Dark mode is paired tokens, not inverted screenshots.
6. Accents sparingly; neutrals carry the UI.
7. Disabled/muted states stay readable enough to parse.

## Workflow
1. Identify brand constraints.
2. Build neutral scale + one accent scale.
3. Check contrast on real components (button, input, link, alert).
4. Document tokens where the project keeps them (CSS vars / Tailwind theme).
