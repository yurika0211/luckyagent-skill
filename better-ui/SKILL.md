---
name: better-ui
description: Design-engineering polish for product UI: surfaces, motion, icons, shadows, optical alignment, micro-interactions. Use when building or reviewing components and something feels slightly off visually.
version: 1.0.0
license: MIT
metadata:
  tags: [ui, design, frontend, polish]
---

# better-ui — interface polish

## Goals
Make UI feel intentional: alignment, surfaces, motion restraint, icon consistency.

## Core checks
1. **Concentric radii**: outer radius ≈ inner radius + padding.
2. **Optical alignment**: icons/triangles often need 1px optical nudges.
3. **Elevation**: shadows for depth; borders for structure/state.
4. **Motion**: short, interruptible, respect `prefers-reduced-motion`.
5. **Press feedback**: subtle scale/opacity; never block input awkwardly.
6. **Icons**: one stroke weight family; use `currentColor`; consistent box sizes.
7. **Performance**: transition only transform/opacity when possible.

## Review output format
- Findings table: severity | location | issue | fix
- Group systemic issues once
- End with `Approve` only if no actionable polish issues

## Related
- Layout → `better-layout`
- Color → `better-colors`
- Type → `better-typography`
- A11y → `better-accessibility`
- Copy → `better-writing`
