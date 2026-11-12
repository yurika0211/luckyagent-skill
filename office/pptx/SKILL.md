---
name: pptx
description: Create, read, and edit PowerPoint presentations (.pptx). Use for decks, pitch slides, slide edits, speaker notes, templates, or any task that opens or produces a .pptx.
version: 1.0.0
license: MIT
metadata:
  tags: [office, pptx, slides, presentation]
---

# PPTX — presentations

## When to use
- New pitch deck / talk slides
- Edit existing `.pptx`
- Extract slide text or notes
- Apply a cleaner visual hierarchy to slides

## When not to use
- Long-form Word/PDF report is the real deliverable
- Single image/poster better done as PNG/SVG

## Tooling preference
1. Extract text: `python -m markitdown file.pptx` or `python-pptx`.
2. Create/edit: `python-pptx`.
3. Re-read after write to verify slide count and titles.

## Create workflow
1. Lock the narrative: one message per slide.
2. Title → supporting bullets (3–6) → optional footer/source.
3. Prefer large type, high contrast, consistent margins.
4. Avoid dense paragraphs; split content across slides.
5. Write `.pptx`, then list slide titles for confirmation.

## Edit workflow
1. Inventory slides (title + short summary).
2. Change only requested slides; keep master layout when possible.
3. Verify speaker notes if they exist.

## Design defaults
- One idea per slide
- High-contrast text
- Align columns to a simple grid
- Don't decorate for decoration's sake
- If brand colors/fonts are given, follow them exactly

## Quality bar
- Readable titles
- No overflow text
- Output path + slide count reported
