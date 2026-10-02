---
name: better-layout
description: Web layout structure — grouping, alignment, spacing scales, reading order, progressive disclosure, responsive breakpoints, RTL-aware flow. Use when structuring pages/components or reviewing spacing hierarchy.
version: 1.0.0
license: MIT
metadata:
  tags: [ui, layout, frontend, spacing]
---

# better-layout

## Principles
1. Group by meaning, not by leftover space.
2. One spacing scale (e.g. 4/8/12/16/24/32); don't invent random px.
3. Align to a grid; consistent edge gutters.
4. Reading order matches visual order (and DOM order).
5. Progressive disclosure: secondary actions quieter / nested.
6. Responsive: reflow by priority; don't only shrink fonts.
7. Use logical properties (`margin-inline`, `padding-block`) for RTL readiness.
8. Full-bleed elements should be explicit, not accidental overflow.

## Review
- List spacing inconsistencies
- Flag cramped clusters vs large empty deserts
- Check mobile stacking order
- Verify focus/reading order still sensible after reflow
