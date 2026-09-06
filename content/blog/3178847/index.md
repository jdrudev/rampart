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

Confluence Formatting SampleThis page is designed to test how native Confluence formatting transforms into Markdown. It includes headings, lists, tasks, decisions, panels, tables, expands, code, links, dates, statuses, emojis, and layout sections.1. Inline FormattingThis paragraph includes **bold text**, *italic text*, <u>underlined text</u>, ~~strikethrough text~~, `inline code`, subscript, superscript, red text, and highlighted text.Here is an emoji , a date , and a status lozenge > Confluence macro omitted: `status`.2. Links and Smart LinksUse a normal link when text needs to flow in a sentence: [Atlassian website](https://www.atlassian.com).[https://support.atlassian.com/confluence-cloud/](https://support.atlassian.com/confluence-cloud/)[https://www.atlassian.com/software/confluence](https://www.atlassian.com/software/confluence)3. ListsBullet ListFirst bullet item with supporting contextSecond bullet itemNested bullet item ANested bullet item BThird bullet itemNumbered ListPrepare sample contentRun transformation engineCompare Markdown outputTask List

0963670e

Confirm headings convert correctly

48561f29

Validate table rendering

1673233b

Review panel and expand output

Decision List778f191b19506487DECIDEDUse this page as the canonical formatting regression sample.153a0472UNDECIDEDDecide whether to include attachment and media examples later.Use this page as the canonical formatting regression sample.Decide whether to include attachment and media examples later.4. Panels> Confluence macro omitted: `info`note73717c2c**Note:** This note panel highlights context that should be preserved.
**Note:** This note panel highlights context that should be preserved.
> Confluence macro omitted: `tip`> Confluence macro omitted: `note`> Confluence macro omitted: `warning`5. Blockquote and CodeMarkdown conversion should preserve quoted content as a blockquote and avoid flattening it into a regular paragraph.> Confluence macro omitted: `code`6. Table FormattingFormatExampleExpected Markdown Check1Status> Confluence macro omitted: `status`Status text and color meaning are retained where possible.2Rich text**Bold**, *italic*, and `code`Inline marks remain readable.3Lists in cellsCell bullet oneCell bullet twoNested cell content does not collapse unexpectedly.4Colored cellLight blue backgroundBackground may become plain text metadata or be dropped.7. Expand Section> Confluence macro omitted: `expand`8. Two-Column LayoutLeft ColumnThis column contains summary content and a status: > Confluence macro omitted: `status`.Left item oneLeft item twoRight ColumnThis column contains a date and formatted text: .Right step oneRight step two9. Horizontal Rule and Closing NotesEnd of sample page. Use this content to validate transformation behavior across a broad set of native Confluence formatting features.
