---
name: imagegen
description: Generate or edit raster images (concept art, product shots, covers, UI mockups, transparent cutouts) via LuckyAgent image generation tools. Use when the deliverable should be a bitmap asset, not repo-native SVG/HTML/canvas.
version: 1.0.0
license: MIT
metadata:
  tags: [image, generation, design, assets]
---

# Image generation

## When to use
- New illustration / hero / product mockup / sprite / texture
- Edit an existing image (style transfer, object remove, background)
- Variants of one concept

## When not to use
- Existing SVG/icon system should be extended in vector
- Diagrams better as pure HTML/CSS/SVG/code
- Tiny deterministic UI chrome

## LuckyAgent execution
Prefer the runtime `image_generate` tool:
- Text-to-image: supply a precise `prompt`
- Image-to-image: supply `input_path` / `input_url` when editing or referencing
- Set `size`, `output_format` (png/jpeg/webp), and destination under the allowed workspace

## Prompt pattern
1. Subject
2. Composition / camera
3. Style medium
4. Lighting / palette
5. Hard constraints (no text, transparent background, aspect)

Example:
`minimal product photo of a matte ceramic mug, centered, soft studio light, warm neutral background, no text, no logo`

## Output hygiene
1. Save under workspace paths the runtime allows.
2. If the asset belongs to a project, copy/move it into the project tree.
3. Don't overwrite existing branded assets unless asked; use `-v2` suffix.
4. Show the user the final path.

## Transparency
- Prefer PNG/WebP.
- If native transparency isn't available, generate flat chroma background and remove locally only when a reliable matte tool exists; otherwise say the limitation.

## Quality bar
- Matches requested aspect and subject
- Path reported
- No accidental extra captions/watermarks in frame unless requested
