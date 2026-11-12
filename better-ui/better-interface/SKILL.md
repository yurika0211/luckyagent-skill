---
name: better-interface
description: Holistic interface review that coordinates better-accessibility, better-layout, better-writing, better-typography, better-colors, and better-ui. Use when explicitly asked for a full UI/UX review of a screen, flow, or feature.
version: 1.0.0
license: MIT
metadata:
  tags: [ui, review, frontend, audit]
  related_skills: [better-accessibility, better-layout, better-writing, better-typography, better-colors, better-ui]
---

# better-interface — full review

## Modes
- **quick**: top 5–10 issues across disciplines
- **full**: systematic pass using each related skill

## Process
1. Confirm scope (screen, flow, PR, whole app area).
2. Capture structure and primary user tasks.
3. Run passes: a11y → layout → type → color → polish → copy.
4. Merge duplicates; sort by user-impact.
5. Deliver findings table + recommended fix order.

## Output
- Summary (3–6 lines)
- Findings: severity | area | issue | fix | discipline
- Suggested implementation order
- `Approve` only if no medium+ issues remain
