# OOXML fields and layout controls

This reference explains the parts of a DOCX that generic text exporters often flatten. Use it when a conversion must remain functional after the user edits the document in Word.

## Fields and bookmarks

Word field instructions are not ordinary visible text. A robust caption/reference pattern is:

```text
bookmark start: fig_method_pipeline
field begin
  SEQ Figure \\* ARABIC
field separate
  cached displayed number
field end
bookmark end
```

A body cross-reference then contains:

```text
field begin
  REF fig_method_pipeline \\h
field separate
  cached displayed number
field end
```

Use stable bookmark names composed of letters, digits, and underscores. Prefix names by semantic kind (`fig_`, `tab_`, `eq_`, `bib_`, `sec_`) to avoid collisions. Bookmarks should wrap the generated number or another small target, not an entire paragraph that Word may rewrite unexpectedly.

Use separate sequence names for figures and tables. If equation numbering is required, use a dedicated sequence or a native equation-numbering strategy and reference the bookmark around the displayed number. Do not type a number in the caption and also insert a `SEQ` field.

After creating or changing fields, update them in a real Word-compatible renderer. `python-docx` can insert field XML but does not calculate the result. Word can update all fields with `Ctrl+A` then `F9`; a controlled Word COM or LibreOffice update/export can be used for a generated copy.

## Heading numbering

There are two valid approaches:

1. a Word multilevel list linked to Heading 1/2/3 styles; or
2. stable displayed numbers emitted by the generator.

The first is best when the user will edit/reorder sections. The second is safer when a template's numbering definitions are unreliable. Both are functional only if there is exactly one source of the visible prefix. Strip source prefixes before applying a Word list, or do not attach a list when the generator emits the prefix.

## Three-line tables

At table level, set these borders explicitly:

```text
top      = single, dark, strong
bottom   = single, dark, strong
left     = nil
right    = nil
insideH  = nil
insideV  = nil
```

At cell level, apply the top rule to the first row, a thinner bottom rule to the header row, and the strong bottom rule to the last row. Clear inherited cell borders as well as table-level borders. A table style such as `Table Grid` can reintroduce visual rules when direct borders are incomplete.

Repeat the header row with `w:tblHeader`. Add `w:cantSplit` to rows so individual rows do not break across pages. For a short table, prefer moving the caption and full table to the next page over leaving a two-row continuation with a repeated header. Do not force every long table onto one page if that would create a worse layout.

Alignment is semantic rather than positional:

- all header cells: center;
- categorical index columns: center;
- prose: left;
- numeric, percentage, fraction, dash, and `N/A`: right;
- bold does not change the alignment decision.

Normalize source wrappers before classifying a cell, for example `\\textbf{5}` should still be recognized as numeric while retaining bold formatting.

## Pagination controls

Use paragraph properties deliberately:

- `keep_with_next = True` for headings and captions when they should stay with the following block;
- `keep_with_next = False` for ordinary body paragraphs, abstracts, keywords, and reference entries unless a local exception is intentional;
- `keep_together = True` for a bibliography entry or a short paragraph that must not split;
- `page_break_before = False` when a template style carries an accidental inherited break;
- `page_break_before = True` only for an intentional major transition or a short table/figure that cannot fit sensibly.

The most damaging template bug is a hidden `keepNext` on the body style: it can chain dozens of paragraphs and create large blank regions. The second common bug is a hidden `pageBreakBefore` on a heading style: it can force every top-level section onto a new page. Inspect direct formatting and style XML rather than trusting the visual style name.

Figures should have a controlled width, centered alignment, a caption immediately after the image, and an explicit rule for what can follow on the same page. Avoid adding a page break after every figure merely because one figure needed a break.

## Relationships and media

Every image relationship referenced by `document.xml` must resolve to a real `/word/media/*` part. Preserve the original image format when Word handles it reliably; otherwise convert to a supported raster/vector format with a documented quality choice. Do not use a screenshot of a table or equation as a substitute for editable content.
