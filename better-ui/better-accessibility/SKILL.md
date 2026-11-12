---
name: better-accessibility
description: Practical interface accessibility — focus semantics, keyboard paths, hit targets, forms, ARIA minima, motion preferences, screen-reader names. Use when building widgets or fixing a11y bugs.
version: 1.0.0
license: MIT
metadata:
  tags: [a11y, accessibility, frontend, wcag]
---

# better-accessibility

## Non-negotiables
1. Keyboard can reach and operate all interactive controls.
2. Visible focus ring (`:focus-visible`).
3. Buttons are `<button>`; links are `<a href>`.
4. Icon-only controls have accessible names.
5. Hit targets are comfortable (aim ≥24px, prefer ~40–44px where density allows).
6. Dialogs trap focus and restore it on close.
7. Errors tie to fields via `aria-describedby` / `aria-invalid`.
8. Don't disable submit solely to enforce incomplete forms — validate and focus first error.
9. Respect `prefers-reduced-motion`.
10. Don't ship information by color alone.

## Review output
severity | location | issue | fix
End with residual risks if any.
