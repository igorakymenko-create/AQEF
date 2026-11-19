#!/usr/bin/env python3
"""Build the AQEF Measurement Guide PDF from the Markdown sources in ../src.

Usage:  python3 build/build.py [output.pdf]

Requires: Python 3 with `markdown` and `pymupdf`; wkhtmltopdf 0.12.x;
fonts Carlito (body), Open Sans (headings) and Liberation Mono (code)
installed system-wide (fc-list must show them).

Order of files: by file name. 00-front-matter.md carries the title-page
fields in a YAML-style header, followed by the "Changes" section.
Every top-level heading (# ...) after the front matter starts a new page
and appears in Contents and in the PDF outline.
"""
import glob, html, os, re, subprocess, sys, tempfile

import markdown
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'AQEF_Measurement_Guide.pdf')

# wkhtmltopdf renders CSS points at about 0.774 of their size; S compensates,
# so that the sizes below are the sizes that end up in the PDF.
S = 1.2931
def pt(v):
    return f'{v * S:.2f}pt'

CSS = f'''
@page {{ size: A4; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: Carlito; font-size: {pt(11.6)}; color: #192a36; line-height: 1.36; }}
h1 {{ font-family: "Open Sans"; font-weight: 700; font-size: {pt(21)}; color: #12394a;
     line-height: 1.15; margin: 0 0 {pt(14)} 0; page-break-before: always; }}
h1.first {{ page-break-before: avoid; }}
h2 {{ font-family: "Open Sans"; font-weight: 700; font-size: {pt(15.5)}; color: #12394a;
     margin: {pt(16)} 0 {pt(7)} 0; line-height: 1.2; page-break-after: avoid; }}
h3 {{ font-family: "Open Sans"; font-weight: 700; font-size: {pt(12)}; color: #12394a;
     margin: {pt(11)} 0 {pt(4)} 0; page-break-after: avoid; }}
h4 {{ font-family: "Open Sans"; font-weight: 700; font-size: {pt(11)}; color: #12394a;
     margin: {pt(9)} 0 {pt(3)} 0; page-break-after: avoid; }}
p {{ margin: 0 0 {pt(6.5)} 0; }}
ul, ol {{ margin: 0 0 {pt(6.5)} 0; padding-left: {pt(16)}; }}
li {{ margin: 0 0 {pt(2.5)} 0; }}
code {{ font-family: "Liberation Mono"; font-size: {pt(9.6)}; }}
pre {{ font-family: "Liberation Mono"; font-size: {pt(7.65)}; line-height: 1.22; white-space: pre-wrap;
      word-wrap: break-word; background: #f2f5f7; border-left: {pt(2.5)} solid #12394a;
      padding: {pt(4)} {pt(6)}; margin: {pt(2)} 0 {pt(8)} 0; }}
pre code {{ font-size: inherit; }}
table {{ border-collapse: collapse; width: 100%; margin: {pt(4)} 0 {pt(9)} 0; font-size: {pt(10)};
        line-height: 1.25; page-break-inside: auto; }}
thead {{ display: table-header-group; }}
table.keep {{ page-break-inside: avoid; }}
table {{ table-layout: fixed; }}
table.cont {{ margin-top: {pt(-9)}; }}
table.cont thead {{ display: none; }}
table.cont.show {{ margin-top: 0; }}
table.cont.show thead {{ display: table-header-group; }}
tr, td, th, td > div, th > div {{ page-break-inside: avoid !important; }}
th {{ background: #e5eef1; font-weight: 700; text-align: left; }}
th, td {{ border: {pt(0.75)} solid #bdcfd7; padding: {pt(3)} {pt(4)}; vertical-align: top; }}
.title {{ padding-top: {pt(150)}; }}
.title .rule {{ width: {pt(425)}; border-top: {pt(3.75)} solid #167d80; margin-bottom: {pt(8)}; }}
.title .t {{ font-family: "Open Sans"; font-weight: 700; font-size: {pt(33)}; color: #12394a; line-height: 1.17; }}
.title .sub {{ font-weight: 700; font-size: {pt(14)}; margin-top: {pt(16)}; }}
.title .meta {{ font-size: {pt(14)}; margin-top: {pt(6)}; }}
.title .note {{ font-size: {pt(14)}; margin-top: {pt(12)}; max-width: {pt(400)}; }}
.toc h1 {{ page-break-before: always; }}
.toc a {{ display: block; color: #135e72; text-decoration: none; font-size: {pt(12)};
         padding: {pt(9)} 0 {pt(11)} 0; border-bottom: {pt(0.75)} solid #d4e3e9; }}
'''

FOOTER = 'AQEF MEASUREMENT GUIDE'
import itertools
COUNTER = itertools.count()
BLOCKS = {}
SHOW_HEAD = set()


def read_sources():
    files = sorted(glob.glob(os.path.join(SRC, '*.md')))
    front = open(files[0], encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', front, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, v = line.split(':', 1)
        meta[k.strip()] = v.strip().strip('"')
    bodies = [m.group(2)] + [open(f, encoding='utf-8').read() for f in files[1:]]
    return meta, bodies


def to_html(md_text):
    h = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'sane_lists'])
    # wkhtmltopdf splits a table row across pages unless its cells hold a block that
    # refuses to break; wrap every cell's content in one.
    h = re.sub(r'(<t[dh][^>]*>)(.*?)(</t[dh]>)', r'\1<div>\2</div>\3', h, flags=re.S)
    # wkhtmltopdf cannot keep a row whole across a page break. Every table is therefore
    # cut into blocks of at most ROWS body rows, each kept whole. A continuation block
    # hides its header, unless a previous pass found it at the top of a page (SHOW_HEAD).
    ROWS = 8
    def chunk(m):
        t = m.group(0)
        head = re.search(r'<thead>.*?</thead>', t, re.S)
        head = head.group(0) if head else ''
        rows = re.findall(r'<tr>.*?</tr>', re.sub(r'<thead>.*?</thead>', '', t, flags=re.S), re.S)
        cols = max(1, head.count('<th'))
        # one set of column widths for all blocks, from the longest text in each column
        cells = [re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S) for r in [head] + rows]
        width = [1] * cols
        for c in cells:
            for k, x in enumerate(c[:cols]):
                width[k] = max(width[k], min(60, len(re.sub(r'<[^>]+>', '', x))))
        tot = sum(width)
        colgroup = '<colgroup>' + ''.join(f'<col style="width:{100 * w / tot:.1f}%">' for w in width) + '</colgroup>'
        out = []
        for i in range(0, max(1, len(rows)), ROWS):
            n = next(COUNTER)
            cls = 'keep' if i == 0 else ('keep cont show' if n in SHOW_HEAD else 'keep cont')
            out.append(f'<table class="{cls}" data-n="{n}">{colgroup}{head}<tbody>{"".join(rows[i:i + ROWS])}</tbody></table>')
            BLOCKS[n] = re.sub(r'<[^>]+>', ' ', rows[i]) if i < len(rows) else ''
        return ''.join(out)
    h = re.sub(r'<table>.*?</table>', chunk, h, flags=re.S)
    return h


def build_html(meta, bodies):
    parts = [to_html(b) for b in bodies]
    changes, body = parts[0], '\n'.join(parts[1:])
    # Contents: every top-level heading of the body, linked by anchor.
    heads = re.findall(r'<h1>(.*?)</h1>', body)
    for i, h in enumerate(heads):
        body = body.replace(f'<h1>{h}</h1>', f'<h1 id="h{i}">{h}</h1>', 1)
    toc = ''.join(f'<a href="#h{i}">{h}</a>' for i, h in enumerate(heads))
    title = f'''<div class="title"><div class="rule"></div>
<div class="t">Measurement Guide {html.escape(meta["version"])} ·<br>{html.escape(meta["date"])}</div>
<div class="sub">{html.escape(meta["subtitle"])}</div>
<div class="meta">Informative companion to {html.escape(meta["basis"])} · {html.escape(meta["license"])}</div>
<div class="note">This guide is informative. It introduces no additional AQEF requirements, universal thresholds, or mandatory metric set.</div></div>'''
    changes = changes.replace('<h1>', '<h1 class="changes">', 1)
    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
           f'{title}{changes}<div class="toc"><h1>Contents</h1>{toc}</div>{body}</body></html>')
    return doc, heads


def render(doc_html, pdf_path):
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(doc_html)
        tmp = f.name
    subprocess.run(['wkhtmltopdf', '-q', '--page-size', 'A4', '--margin-top', '16mm',
                    '--margin-bottom', '22mm', '--margin-left', '18mm', '--margin-right', '18mm',
                    '--encoding', 'utf-8', tmp, pdf_path], check=False)
    os.unlink(tmp)


def finish(pdf_path, meta, bodies_heads):
    d = pymupdf.open(pdf_path)
    label = f'{FOOTER} {meta["version"]}'
    ffile = subprocess.run(['fc-match', '-f', '%{file}', 'Open Sans'], capture_output=True, text=True).stdout
    font = pymupdf.Font(fontfile=ffile)
    for i, page in enumerate(d):
        page.insert_font(fontname='FOOT', fontfile=ffile)
        page.insert_text((51.0, 825.75), label, fontname='FOOT', fontsize=6.75, color=(0.32, 0.41, 0.45))
        num = str(i + 1)
        w = font.text_length(num, fontsize=6.75)
        page.insert_text((544.25 - w, 825.75), num, fontname='FOOT', fontsize=6.75, color=(0.32, 0.41, 0.45))
    # Outline: title, changes, contents, then the Markdown headings of levels 1 and 2,
    # each located on the first page at or after the previous one whose text contains it.
    def norm(t):
        return re.sub(r'\s+', ' ', re.sub(r'[*`]', '', t)).strip()
    toc = [[1, f'Measurement Guide {meta["version"]} · {meta["date"]}', 1],
           [1, norm(re.sub('^#+ ', '', bodies_heads[0][1])), 2], [1, 'Contents', 3]]
    texts = [norm(page.get_text()) for page in d]
    p = 3
    for lvl, t in bodies_heads[1:]:
        key = norm(t)[:40]
        while p < len(texts) and key not in texts[p]:
            p += 1
        if p == len(texts):
            raise SystemExit(f'heading not found in PDF: {t}')
        toc.append([lvl, norm(t), p + 1])
    d.set_toc(toc)
    d.set_metadata({'title': f'AQEF Measurement Guide {meta["version"]}', 'author': 'Igor Akymenko',
                    'subject': meta['subtitle'], 'creator': 'build/build.py'})
    tmp = pdf_path + '.tmp'
    d.save(tmp, garbage=4, deflate=True)
    d.close()
    os.replace(tmp, pdf_path)


def tops(pdf_path):
    """Continuation blocks whose first row opens a page: they need their header shown."""
    d = pymupdf.open(pdf_path)
    found = set()
    for n, first in BLOCKS.items():
        words = re.sub(r'\s+', ' ', first).strip()[:30]
        if not words:
            continue
        for page in d:
            for r in page.search_for(words):
                if r.y0 < 80:
                    found.add(n)
    d.close()
    return found


def main():
    global COUNTER
    meta, bodies = read_sources()
    for _ in range(4):
        COUNTER = itertools.count()
        BLOCKS.clear()
        doc, _h = build_html(meta, bodies)
        render(doc, OUT)
        need = tops(OUT)
        if need <= SHOW_HEAD:
            break
        SHOW_HEAD.update(need)
    heads = [(len(m.group(1)), m.group(2)) for b in bodies
             for m in re.finditer(r'^(#{1,2}) (.+)$', re.sub(r'```.*?```', '', b, flags=re.S), re.M)]
    finish(OUT, meta, heads)
    print(OUT)


if __name__ == '__main__':
    main()
