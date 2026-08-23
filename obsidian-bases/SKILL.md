---
name: obsidian-bases
description: Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian.
---

# Obsidian Bases Skill

## Workflow

1. **Create the file**: Create a `.base` file in the vault with valid YAML content
2. **Define scope**: Add `filters` to select which notes appear (by tag, folder, property, or date)
3. **Add formulas** (optional): Define computed properties in the `formulas` section
4. **Configure views**: Add one or more views (`table`, `cards`, `list`, or `map`) with `order` specifying which properties to display
5. **Validate**: Verify the file is valid YAML with no syntax errors. Check that all referenced properties and formulas exist.
6. **Test in Obsidian**: Open the `.base` file in Obsidian to confirm the view renders correctly.

## Schema

Base files use the `.base` extension and contain valid YAML.

```yaml
# Global filters apply to ALL views in the base
filters:
  and: []
  or: []
  not: []

# Define formula properties that can be used across all views
formulas:
  formula_name: 'expression'

# Configure display names and settings for properties
properties:
  property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"

# Define views (table, cards, list, or map)
views:
  - name: "Table View"
    type: table
    order:
      - property_name
      - formula.formula_name
```

## Filter Syntax

```yaml
filters:
  # Single string filter
  and: ["Status = Done"]

  # Recursive filter object
  and:
    - tag: "#project"
    - or:
        - property: "priority"
          operator: ">="
          value: 3
        - property: "status"
          operator: "="
          value: "active"
```

## View Types

| Type | Description |
|------|-------------|
| `table` | Tabular view with columns |
| `cards` | Card-based layout |
| `list` | Simple list view |
| `map` | Map view with location data |