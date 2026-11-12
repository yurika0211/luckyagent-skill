---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
---

# Obsidian Flavored Markdown Skill

Create and edit valid Obsidian Flavored Markdown. Obsidian extends CommonMark and GFM with wikilinks, embeds, callouts, properties, comments, and other syntax. This skill covers only Obsidian-specific extensions.

## Workflow: Creating an Obsidian Note

1. **Add frontmatter** with properties (title, tags, aliases) at the top of the file.
2. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below.
3. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections, or standard Markdown links for external URLs.
4. **Embed content** from other notes, images, or PDFs using the `![[embed]]` syntax.
5. **Add callouts** for highlighted information using `> [!type]` syntax.
6. **Verify** the note renders correctly in Obsidian's reading view.

> Use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only.

## Internal Links (Wikilinks)

```markdown
[[Note Name]]
[[Note Name|Display Text]]
[[#^block-id]]
[[Note Name#^block-id]]
```

## Embeds

```markdown
![[Image.png]]
![[Note Name]]
![[Note Name#^block-id]]
![[Document.pdf#page=3]]
```

## Callouts

```markdown
> [!note] Title
> Content here

> [!warning] 
> Content

> [!tip]
> Content

> [!info]
> Content

> [!abstract]
> Content

> [!success]
> Content

> [!question]
> Content
```

## Properties (Frontmatter)

```yaml
---
title: My Note
tags:
  - tag1
  - tag2
aliases:
  - alias1
  - alias2
created: 2025-01-01
---
```

## Comments

```markdown
%% This is a comment and won't be rendered %%
```

## Tags

```markdown
#tag-name
```