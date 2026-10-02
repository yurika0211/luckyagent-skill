---
name: pdf
description: Read, create, merge, split, rotate, watermark, form-fill, and extract text/tables from PDF files. Use whenever the user mentions a .pdf, needs OCR on scans, or wants a PDF deliverable.
version: 1.0.0
license: MIT
metadata:
  tags: [office, pdf, documents]
---

# PDF processing

## When to use
- Extract text/tables from PDFs
- Merge, split, rotate, watermark
- Create simple PDFs
- OCR scanned pages when text layer is missing

## Tooling preference
1. `document_read` for readable text extraction when available.
2. Python: `pypdf` for merge/split/rotate/metadata; `pdfplumber` or `pypdf` for text; `reportlab` for simple creation.
3. CLI fallbacks if present: `pdftotext`, `qpdf`, `gs`.
4. OCR only when needed: `ocrmypdf` or Tesseract-based flows.

## Common recipes

### Merge
```python
from pypdf import PdfWriter, PdfReader
w = PdfWriter()
for path in paths:
    for page in PdfReader(path).pages:
        w.add_page(page)
with open(out, "wb") as f:
    w.write(f)
```

### Split one-page files
Iterate `reader.pages`, write each with `PdfWriter`.

### Create simple PDF
Use reportlab platypus or canvas; embed fonts for CJK when needed.

## Workflow
1. Identify operation and output path.
2. Prefer non-destructive outputs (new file) unless user asks to replace.
3. Verify page count and sample text after write.
4. For scans, say when OCR is required before summarizing.

## Quality bar
- Correct page order
- No accidental password lock unless requested
- State page count + output path
