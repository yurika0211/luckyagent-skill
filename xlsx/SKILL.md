---
name: xlsx
description: Create, read, clean, and edit spreadsheets (.xlsx/.xlsm/.csv/.tsv). Use when the deliverable or source is tabular data, Excel models, charts in workbooks, or messy tables that must become a proper spreadsheet.
version: 1.0.0
license: MIT
metadata:
  tags: [office, excel, xlsx, csv, spreadsheet]
---

# XLSX — spreadsheets

## When to use
- Build or fix Excel workbooks
- Clean CSV/TSV into `.xlsx`
- Formulas, pivots-like summaries, basic charts
- Validate numeric models

## When not to use
- Primary deliverable is Word/PDF/HTML narrative
- Database pipeline / Google Sheets API is the real target

## Tooling preference
1. Python: `openpyxl` for xlsx read/write; `csv` module for csv/tsv.
2. LuckyAgent `csv_query` for large CSV inspection/filters.
3. Recompute/verify formulas logically; don't ship known `#REF!` / `#DIV/0!`.

## Create / edit workflow
1. Define sheets, headers, and units first.
2. Keep raw inputs separate from calculated outputs when modeling.
3. Use real Excel formulas where the user will continue editing in Excel.
4. Freeze header rows; auto-size thoughtfully; avoid merged-cell soup.
5. Write file, then spot-check row counts and sample formulas.

## Quality bar
- Zero formula errors in delivered models
- Explicit units and date formats
- Stable header names
- Preserve existing template conventions when editing a user's file
- Report output path + sheet names
