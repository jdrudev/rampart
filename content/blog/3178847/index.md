---
title: 'formatting'
description: Generated from Confluence.
date: 2026-09-06
updated: 2026-09-06
tags:
  - 'formatter'
confluence_id: '3178847'
source_url: 'https://jdru.atlassian.net/wiki/spaces/Portfolio/pages/3178847/formatting'
---

## Confluence Formatting Sample

This page is designed to test how native Confluence formatting transforms into Markdown. It includes headings, lists, tasks, decisions, panels, tables, expands, code, links, dates, statuses, emojis, and layout sections.

### 1. Inline Formatting

This paragraph includes **bold text**, *italic text*, <u>underlined text</u>, ~~strikethrough text~~, `inline code`, subscript, superscript, red text, and highlighted text.

Here is an emoji , a date , and a status lozenge > Confluence macro omitted: `status`.

### 2. Links and Smart Links

Use a normal link when text needs to flow in a sentence: [Atlassian website](https://www.atlassian.com).

- [https://support.atlassian.com/confluence-cloud/](https://support.atlassian.com/confluence-cloud/)
- [https://www.atlassian.com/software/confluence](https://www.atlassian.com/software/confluence)

### 3. Lists

#### Bullet List

- First bullet item with supporting context
- Second bullet itemNested bullet item ANested bullet item B
- Third bullet item

#### Numbered List

1. Prepare sample content
2. Run transformation engine
3. Compare Markdown output

#### Task List

- [x] Confirm headings convert correctly
- [ ] Validate table rendering
- [ ] Review panel and expand output

#### Decision List

778f191b

19506487

DECIDED

Use this page as the canonical formatting regression sample.

153a0472

UNDECIDED

Decide whether to include attachment and media examples later.

- Use this page as the canonical formatting regression sample.
- Decide whether to include attachment and media examples later.

### 4. Panels

<div class="callout callout-info"><strong>Info</strong>

**Info:** This is an informational panel for general notes.</div>

note

73717c2c

**Note:** This note panel highlights context that should be preserved.

**Note:** This note panel highlights context that should be preserved.

<div class="callout callout-success"><strong>Success</strong>

**Success:** This success panel represents a positive outcome.</div>

<div class="callout callout-note"><strong>Note</strong>

**Warning:** This warning panel calls attention to a risk.</div>

<div class="callout callout-warning"><strong>Warning</strong>

**Error:** This error panel represents a critical issue.</div>

### 5. Blockquote and Code

> Markdown conversion should preserve quoted content as a blockquote and avoid flattening it into a regular paragraph.

```
jswide760truefunction transform(input) { return input.trim().toUpperCase(); } console.log(transform('native confluence formatting'));
```

### 6. Table Formatting

|  | Format | Example | Expected Markdown Check |
| --- | --- | --- | --- |
| 1 | Status | > Confluence macro omitted: `status` | Status text and color meaning are retained where possible. |
| 2 | Rich text | **Bold**, *italic*, and `code` | Inline marks remain readable. |
| 3 | Lists in cells | Cell bullet oneCell bullet two | Nested cell content does not collapse unexpectedly. |
| 4 | Colored cell | Light blue background | Background may become plain text metadata or be dropped. |

### 7. Expand Section

<details class="expand"><summary>> Confluence macro omitted: `expand`</summary>

Click to reveal detailed transformation notes

760

This expand contains hidden content that should still be available to the ingestion pipeline.

- Nested paragraph content
- Nested list content
- Another item with **bold emphasis**

<div class="callout callout-info"><strong>Info</strong>

Panel inside an expand for nested formatting coverage.</div>

</details>

### 8. Two-Column Layout

#### Left Column

This column contains summary content and a status: > Confluence macro omitted: `status`.

- Left item one
- Left item two

#### Right Column

This column contains a date and formatted text: .

1. Right step one
2. Right step two

### 9. Horizontal Rule and Closing Notes

End of sample page. Use this content to validate transformation behavior across a broad set of native Confluence formatting features.
