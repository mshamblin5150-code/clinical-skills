"""Render a Markdown subset to a .docx, with the standard library and nothing else.

    python tools/docx_write.py <in.md> <out.docx>

**Why this is not PyMuPDF, asked and answered once.** PyMuPDF reads and writes PDFs.
A finished case study is submitted to Canvas as a Word document, and no PDF library
authors one. A ``.docx`` is a zip archive of XML parts -- ``zipfile`` and string
formatting are the whole dependency list -- so this stays on the consumer's critical
path without putting a ``pip install`` there. See *Console codec* in ``CLAUDE.md`` for
why five tools here are allowed a dependency and the rest are not: all five open a PDF.

**The Markdown subset is deliberately small**, and it is exactly what a case study uses:

======================  ====================================================
``# .. ####``           Heading 1 to 4
``- item``              bulleted list (two spaces of indent nests one level)
``1. item``             numbered list
``| a | b |``           table, first row is the header, the ``---`` rule skipped
``**bold**``            bold run
``*italic*``            italic run
blank line              paragraph break
``---``                 ignored -- a Markdown rule is not a Word construct
======================  ====================================================

**The References heading switches the body style, and that is APA 7 rather than a
nicety.** Every paragraph after a heading whose text begins ``References`` is rendered
with a 0.5 inch hanging indent, which is what a reference list is. The switch is on the
*heading*, so a document with no References section never pays for it.

**Page setup is APA 7 student paper**: Times New Roman 12 pt, double spaced, 1 inch
margins. The rubric gives APA format 5 of 100 points, and this is the whole of what
that line can be given mechanically -- see
``skills/practicum-case-study/reference/rubric.md``.

Covered by ``tools/test_docx.py``, which writes into a temp directory and reads the
result back with ``docx_read`` -- the round trip is the test, because a ``.docx`` that
Word refuses to open is indistinguishable from a good one until Word opens it.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from console_codec import use_utf8

# Twips throughout. One inch is 1440.
MARGIN = 1440
HANGING = 720
LINE_DOUBLE = 480

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _heading_style(level: int, half_points: int) -> str:
    return (
        '<w:style w:type="paragraph" w:styleId="Heading{lv}">'
        '<w:name w:val="heading {lv}"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:keepNext/><w:outlineLvl w:val="{out}"/>'
        '<w:spacing w:before="0" w:after="0" w:line="{line}" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr></w:style>'
    ).format(lv=level, out=level - 1, line=LINE_DOUBLE, sz=half_points)


STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {w}>
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="{line}" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
{h1}{h2}{h3}{h4}
<w:style w:type="paragraph" w:styleId="Reference"><w:name w:val="Reference"/>
<w:basedOn w:val="Normal"/><w:pPr>
<w:ind w:left="{hang}" w:hanging="{hang}"/>
<w:spacing w:after="0" w:line="{line}" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/>
<w:basedOn w:val="Normal"/><w:pPr><w:contextualSpacing/></w:pPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>
<w:tblPr><w:tblBorders>
<w:top w:val="single" w:sz="4" w:color="000000"/><w:left w:val="single" w:sz="4" w:color="000000"/>
<w:bottom w:val="single" w:sz="4" w:color="000000"/><w:right w:val="single" w:sz="4" w:color="000000"/>
<w:insideH w:val="single" w:sz="4" w:color="000000"/><w:insideV w:val="single" w:sz="4" w:color="000000"/>
</w:tblBorders></w:tblPr></w:style>
</w:styles>""".format(
    w=W,
    line=LINE_DOUBLE,
    hang=HANGING,
    h1=_heading_style(1, 28),
    h2=_heading_style(2, 26),
    h3=_heading_style(3, 24),
    h4=_heading_style(4, 24),
)


def _abstract_num(num_id: int, fmt: str) -> str:
    levels = []
    for level in range(3):
        indent = 720 * (level + 1)
        if fmt == "bullet":
            marker = "•"
            font = '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr>'
        else:
            marker = "%" + str(level + 1) + "."
            font = ""
        levels.append(
            '<w:lvl w:ilvl="{lv}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
            '<w:lvlText w:val="{mark}"/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="{ind}" w:hanging="360"/></w:pPr>{font}</w:lvl>'.format(
                lv=level, fmt=fmt, mark=marker, ind=indent, font=font
            )
        )
    return '<w:abstractNum w:abstractNumId="{n}">{lv}</w:abstractNum>'.format(
        n=num_id, lv="".join(levels)
    )


NUMBERING = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {w}>
{bullet}
{decimal}
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
<w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>""".format(
    w=W, bullet=_abstract_num(0, "bullet"), decimal=_abstract_num(1, "decimal")
)


def esc(text: str) -> str:
    """XML-escape, and drop the control characters Word refuses to open a file over."""
    text = "".join(c for c in text if c >= " " or c == "\t")
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_INLINE = re.compile(r"(\*\*.+?\*\*|(?<!\*)\*[^*]+?\*(?!\*)|`[^`]+?`)", re.DOTALL)


def runs(text: str, bold: bool = False) -> str:
    """Split bold, italic and monospace spans into Word runs."""
    out = []
    for piece in _INLINE.split(text):
        if not piece:
            continue
        is_bold, is_italic, is_mono = bold, False, False
        body = piece
        if piece.startswith("**") and piece.endswith("**") and len(piece) > 4:
            is_bold, body = True, piece[2:-2]
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            is_italic, body = True, piece[1:-1]
        elif piece.startswith("`") and piece.endswith("`") and len(piece) > 2:
            is_mono, body = True, piece[1:-1]
        props = ""
        if is_bold:
            props += "<w:b/>"
        if is_italic:
            props += "<w:i/>"
        if is_mono:
            props += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
        rpr = "<w:rPr>{p}</w:rPr>".format(p=props) if props else ""
        out.append(
            '<w:r>{rpr}<w:t xml:space="preserve">{t}</w:t></w:r>'.format(rpr=rpr, t=esc(body))
        )
    return "".join(out)


def para(text: str, style: str = "", num_id: int = 0, level: int = 0) -> str:
    props = []
    if style:
        props.append('<w:pStyle w:val="{s}"/>'.format(s=style))
    if num_id:
        props.append(
            '<w:numPr><w:ilvl w:val="{lv}"/><w:numId w:val="{n}"/></w:numPr>'.format(
                lv=level, n=num_id
            )
        )
    ppr = "<w:pPr>{p}</w:pPr>".format(p="".join(props)) if props else ""
    return "<w:p>{ppr}{r}</w:p>".format(ppr=ppr, r=runs(text))


BORDERS = (
    "<w:tblBorders>"
    '<w:top w:val="single" w:sz="4" w:color="000000"/>'
    '<w:left w:val="single" w:sz="4" w:color="000000"/>'
    '<w:bottom w:val="single" w:sz="4" w:color="000000"/>'
    '<w:right w:val="single" w:sz="4" w:color="000000"/>'
    '<w:insideH w:val="single" w:sz="4" w:color="000000"/>'
    '<w:insideV w:val="single" w:sz="4" w:color="000000"/>'
    "</w:tblBorders>"
)


def table(rows: list) -> str:
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    cell_width = 9360 // width
    grid = "".join('<w:gridCol w:w="{w}"/>'.format(w=cell_width) for _ in range(width))
    body = []
    for index, row in enumerate(rows):
        cells = []
        for column in range(width):
            text = row[column] if column < len(row) else ""
            cells.append(
                '<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr>'
                '<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/></w:pPr>'
                "{r}</w:p></w:tc>".format(w=cell_width, r=runs(text, bold=index == 0))
            )
        header = "<w:trPr><w:tblHeader/></w:trPr>" if index == 0 else ""
        body.append("<w:tr>{h}{c}</w:tr>".format(h=header, c="".join(cells)))
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="0" w:type="auto"/>{b}</w:tblPr>'
        "<w:tblGrid>{g}</w:tblGrid>{rows}</w:tbl><w:p/>"
    ).format(b=BORDERS, g=grid, rows="".join(body))


def split_row(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_rule(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)


def body_xml(markdown: str) -> str:
    """Convert the Markdown subset to the payload of a ``w:body`` element."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    out = []
    in_references = False
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped or stripped in ("---", "***", "___"):
            if not in_references and not stripped:
                out.append("<w:p/>")
            index += 1
            continue

        heading = re.match(r"(#{1,4})\s+(.*)", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            in_references = bool(re.match(r"references\b", text, re.I))
            out.append(para(text, style="Heading{n}".format(n=level)))
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_rule(lines[index + 1]):
            rows = [split_row(stripped)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(split_row(lines[index].strip()))
                index += 1
            out.append(table(rows))
            continue

        bullet = re.match(r"([ \t]*)[-*+]\s+(.*)", line)
        if bullet:
            level = min(len(bullet.group(1).expandtabs(4)) // 2, 2)
            out.append(para(bullet.group(2), style="ListParagraph", num_id=1, level=level))
            index += 1
            continue

        numbered = re.match(r"([ \t]*)\d+[.)]\s+(.*)", line)
        if numbered:
            level = min(len(numbered.group(1).expandtabs(4)) // 2, 2)
            out.append(para(numbered.group(2), style="ListParagraph", num_id=2, level=level))
            index += 1
            continue

        out.append(para(stripped, style="Reference" if in_references else ""))
        index += 1

    return "".join(out)


def document_xml(markdown: str) -> str:
    sect = (
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="{m}" w:right="{m}" w:bottom="{m}" w:left="{m}" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
    ).format(m=MARGIN)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        "<w:document {w}><w:body>{b}{s}</w:body></w:document>"
    ).format(w=W, b=body_xml(markdown), s=sect)


def write_docx(markdown: str, destination) -> Path:
    destination = Path(destination)
    if destination.parent != Path("."):
        destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", ROOT_RELS)
        archive.writestr("word/_rels/document.xml.rels", DOC_RELS)
        archive.writestr("word/styles.xml", STYLES)
        archive.writestr("word/numbering.xml", NUMBERING)
        archive.writestr("word/document.xml", document_xml(markdown))
    return destination


def main(argv: list) -> int:
    if len(argv) < 2:
        print("usage: docx_write.py <in.md> <out.docx>")
        return 2
    source = Path(argv[0])
    if not source.is_file():
        print("not a file: {p}".format(p=source))
        return 2
    written = write_docx(source.read_text(encoding="utf-8"), Path(argv[1]))
    print("wrote {p} ({n} bytes)".format(p=written, n=written.stat().st_size))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
