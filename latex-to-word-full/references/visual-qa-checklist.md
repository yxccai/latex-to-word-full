# Render-based visual QA checklist

## Render contract

The final DOCX must be rendered by a Word-compatible engine before it is declared complete. Preferred order:

1. the host's document rendering skill/tool;
2. Microsoft Word PDF export on Windows when Word is available;
3. LibreOffice headless PDF export;
4. another verified DOCX renderer, with its limitations reported.

Convert the PDF into page PNGs at a readable resolution. Use a contact sheet for orientation, then inspect individual pages at high resolution. If the renderer cannot be run, report that visual QA is incomplete rather than implying that structural checks prove the layout is correct.

## Page-by-page checks

For every page, check:

- page size, margins, header/footer, and section orientation;
- title, author, abstract, and keywords alignment;
- heading hierarchy and numbering, including the first and last occurrence of each level;
- equation glyphs, baseline alignment, line wrapping, and number/reference consistency;
- figure resolution, aspect ratio, caption placement, and whitespace below the figure;
- table top/header/bottom rules, absence of vertical rules, row splits, repeated headers, cell alignment, and numeric decimal consistency;
- body paragraph line spacing, indentation, widows/orphans, and accidental large gaps;
- lists, code, hyperlinks, footnotes, superscripts, symbols, and non-Latin text;
- bibliography entry spacing, numbering, italics, and whether an entry begins at the bottom of a page and continues at the next page;
- fields displaying values rather than field-code text or stale placeholders.

## Typical fixes

| Symptom | Likely cause | Preferred fix |
|---|---|---|
| `4.3. 4.3. Heading` | manual source prefix plus Word numbering | remove one numbering source |
| every section starts on a new page | inherited `pageBreakBefore` | clear direct/style break except intentional transitions |
| text jumps to the next page after a figure | hidden `keepNext`, forced break, or oversized image | clear body `keepNext`, remove unnecessary break, constrain image width |
| one table cell is visually offset | alignment based on source wrapper or style inheritance | normalize cell value, set direct alignment for every cell |
| vertical lines reappear in a three-line table | table style or inherited cell borders | set table and cell borders explicitly to `nil` |
| cross-reference stays at an old number | static text or fields not updated | use bookmark/`REF` field and update fields before render |
| a short bibliography entry is split | paragraph can break across pages | set `keep_together` on each entry |
| table continues with no context | header not marked repeatable | set `w:tblHeader` on the first row |
| equation becomes an image | converter rasterized math | use native OMML or an editable fallback and disclose limits |

## Final evidence to record

Keep a compact QA record with:

- input and output paths;
- renderer and render date;
- final page count;
- counts of figures, tables, inline images, `REF` fields, `SEQ` fields, and bookmarks;
- whether the source/template remained unchanged;
- known limitations or items requiring a Word field refresh.

Visual QA is iterative. When a defect is found, change the generator, style, or OOXML rule that caused it, rebuild the whole DOCX, rerender, and recheck affected pages plus the first/last pages. Avoid one-off manual edits that will disappear on the next conversion.
