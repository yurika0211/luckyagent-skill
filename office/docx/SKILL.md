---
name: docx
description: Create, read, edit, and analyze Word documents (.docx). Use when the user mentions Word, .docx, reports, memos, letters, tracked changes, comments, headers/footers, or needs a polished Word deliverable. Do not use for PDF, spreadsheet, or slide-only tasks.
version: 1.0.0
license: MIT
metadata:
  tags: [office, word, docx, documents]
---

# DOCX — Word documents

## When to use
- Create a new `.docx`
- Read or summarize an existing Word file
- Edit structure, text, tables, images, headers/footers
- Convert content into a professional Word deliverable

## When not to use
- Primary output is PDF, PPTX, or XLSX
- Plain Markdown/Obsidian notes only

## Tooling preference (LuckyAgent)
1. Prefer runtime document tools when available (`document_read` for extraction).
2. For creation/editing, use Python with `python-docx` when installed.
3. For plain-text extraction fallbacks: `pandoc file.docx -t markdown`.
4. Legacy `.doc` → convert to `.docx` first (LibreOffice/soffice if present).

## Read workflow
1. Confirm path exists.
2. Extract text with `document_read` or pandoc.
3. If layout/XML matters, unpack the zip and inspect `word/document.xml`.
4. Report structure: headings, tables, images, comments if relevant.

## Create workflow
1. Confirm filename, audience, and required sections.
2. Build with `python-docx`: styles, heading levels, tables, page margins.
3. Keep formatting consistent; avoid one-off inline styles unless needed.
4. Write file, then re-read to verify text and section order.

## Edit workflow
1. Read original first; preserve unrelated content.
2. Make the smallest change that satisfies the request.
3. Re-open and verify changed paragraphs/tables only.
4. Do not overwrite user files without a clear target path.

## Quality bar
- Correct extension `.docx`
- Stable heading hierarchy
- Tables aligned and readable
- No placeholder lorem unless user asked for draft filler
- State output path when done
