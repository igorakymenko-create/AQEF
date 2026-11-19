# AQEF Measurement Guide — source

The Markdown source of the AQEF Measurement Guide, and the script that builds its PDF.

This source holds the text of **Measurement Guide 1.3** (19 November 2026), published as
`guides/measurement/AQEF_Measurement_Guide_1.3.pdf`. Edit these files for the next version;
do not edit the PDF.

## Files

| File | Content |
|---|---|
| `src/00-front-matter.md` | Title-page fields (version, date, basis, licence) and "Changes in …" |
| `src/01-part-1-method.md` … `src/07-part-7-judge-prompt-examples.md` | Parts 1 to 7 |
| `src/08-appendix-a-cross-reference.md` … `src/12-appendix-e-terminology-crosswalk.md` | Appendices A to E |
| `build/build.py` | Builds the PDF |
| `build/verify.py` | Compares the text of two PDFs word by word |

Files are joined in name order. A heading `# …` starts a new page and is listed in Contents;
`# PART …` and `# Appendix X — …` are the only level-1 headings. Use `##` and below inside them.

## Build

Requirements:
- Python 3 with `markdown` and `pymupdf` (`pip install markdown pymupdf`);
- `wkhtmltopdf` 0.12.x;
- fonts Carlito (body; metrically identical to Calibri), Open Sans (headings) and
  Liberation Mono (code), installed so that `fc-list` shows them.

```
python3 build/build.py AQEF_Measurement_Guide_1.4.pdf
```

The script adds page footers, the Contents page and the PDF outline. It runs wkhtmltopdf up to
four times: a long table is cut into blocks kept whole, and a block that opens a page gets its
header repeated.

## Check before publishing

Compare the new PDF's text with the previous release, and read every difference:

```
python3 build/verify.py previous.pdf new.pdf
```

It ignores layout, line breaks, hyphenation and page numbers. Table cells that wrap
differently show up as moved words; anything else is a real change and must be one you
intended.

## How this source was made (1.2)

The earlier Markdown source predated the final edits of 1.1. This source was rebuilt on
19 November 2026 from that draft and the published 1.2 PDF: every textual difference was
carried over, and the text of a PDF built from it matches the published 1.2 word for word,
except for:
- table headers that the published PDF repeated on a new page;
- five stray `*` characters after "Method interpretation and limits" paragraphs in Part 4
  (M-25, M-30, M-35, M-36, M-37), which were Markdown artefacts and are removed.

From 1.3 on, the Guide is published as built from this source, with these fonts.
