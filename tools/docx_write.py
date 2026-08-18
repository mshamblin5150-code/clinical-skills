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
nicety.** Every paragraph after a heading whose text begins ``References`` -- or the
singular ``Reference``, which APA permits for a one-entry list -- is rendered with a
0.5 inch hanging indent, which is what a reference list is. That heading also takes a
page break and centers, because APA 7 section 2.12 starts the list on a new page under a
bold centered label. The switch is on the *heading*, so a document with no References
section never pays for any of it.

**Page setup is APA 7 student paper**: Times New Roman 12 pt, double spaced, 1 inch
margins, and a page number in the top right of every page -- the ``word/header1.xml``
part, which is the only reason this archive carries a header at all. Headings are body
size at every level, distinguished the way APA distinguishes them: level 1 bold
centered, level 2 bold flush left, level 3 bold italic flush left, level 4 bold
indented. The rubric gives APA format 5 of 100 points, and this is most of what that
line can be given mechanically -- see ``skills/practicum-case-study/reference/rubric.md``.

**What it still does not do, named rather than implied by the claim above.** There is no
title page; APA level 4 and 5 headings are run-in and Markdown cannot express one, so
level 4 is rendered as the indented bold paragraph it otherwise is and level 5 is not in
the subset at all; body paragraphs take no 0.5 inch first-line indent; and a table is
drawn with a full grid rather than APA's horizontal rules. ``apa7.md`` section 6 is where
that list is kept for a reader of the skill -- #220 tracks the two of them that are
mechanical. **A rendered .docx is not an APA-formatted document**, which is
``skills/practicum-case-study/SKILL.md`` step 8's sentence arriving one level down.

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
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
</Relationships>"""

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
R = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
HEADER_ID = "rId3"

# APA 7 wants a page number in the top right of every page and nothing else in the
# header -- a student paper carries no running head. ``PAGE`` is a field code rather
# than text, so it is a ``w:fldSimple``; the ``1`` inside it is the cached result Word
# recomputes on open, and it is deliberately the only character here. Nothing in this
# part is prose, which is what keeps ``docx_read`` -- which reads ``word/document.xml``
# and no other part -- able to read back everything a document says.
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr {w}>
<w:p><w:pPr><w:jc w:val="right"/></w:pPr>
<w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple>
</w:p>
</w:hdr>""".format(w=W)


# APA 7 sets every heading at body size and distinguishes the levels by weight,
# centering and indent instead -- section 2.27. Level 4 is a run-in heading in the
# manual, which Markdown cannot express because ``#### x`` owns its own line; it is
# rendered as the indented bold paragraph the run-in form is otherwise identical to.
BODY_HALF_POINTS = 24
HEADING_LEVELS = {
    1: {"align": "center"},
    2: {},
    3: {"italic": True},
    4: {"indent": HANGING},
}


def _heading_style(level: int) -> str:
    """One heading style. The property order inside ``w:pPr`` is the schema's.

    ``CT_PPrBase`` is a sequence -- ``keepNext``, ``spacing``, ``ind``, ``jc``,
    ``outlineLvl`` -- and this used to emit ``outlineLvl`` before ``spacing``. Word
    opened those documents, which is exactly why nothing caught it; a test pins the
    order now rather than trusting that tolerance.
    """
    spec = HEADING_LEVELS[level]
    spacing = '<w:spacing w:before="0" w:after="0" w:line="{l}" w:lineRule="auto"/>'
    props = ["<w:keepNext/>", spacing.format(l=LINE_DOUBLE)]
    if spec.get("indent"):
        props.append('<w:ind w:left="{i}"/>'.format(i=spec["indent"]))
    if spec.get("align"):
        props.append('<w:jc w:val="{a}"/>'.format(a=spec["align"]))
    props.append('<w:outlineLvl w:val="{o}"/>'.format(o=level - 1))
    runs_props = "<w:b/>" + ("<w:i/>" if spec.get("italic") else "")
    return (
        '<w:style w:type="paragraph" w:styleId="Heading{lv}">'
        '<w:name w:val="heading {lv}"/><w:basedOn w:val="Normal"/>'
        "<w:pPr>{ppr}</w:pPr>"
        '<w:rPr>{rpr}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr></w:style>'
    ).format(lv=level, ppr="".join(props), rpr=runs_props, sz=BODY_HALF_POINTS)


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
    h1=_heading_style(1),
    h2=_heading_style(2),
    h3=_heading_style(3),
    h4=_heading_style(4),
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


def para(
    text: str,
    style: str = "",
    num_id: int = 0,
    level: int = 0,
    page_break: bool = False,
    align: str = "",
) -> str:
    """One paragraph. The property order is the schema's, not a preference.

    ``CT_PPrBase`` is a sequence rather than a set -- ``pStyle``, ``pageBreakBefore``,
    ``numPr``, then ``jc`` -- and Word refuses a file whose properties arrive out of
    order. Nothing here validates that, so the order is kept by construction.
    """
    props = []
    if style:
        props.append('<w:pStyle w:val="{s}"/>'.format(s=style))
    if page_break:
        props.append("<w:pageBreakBefore/>")
    if num_id:
        props.append(
            '<w:numPr><w:ilvl w:val="{lv}"/><w:numId w:val="{n}"/></w:numPr>'.format(
                lv=level, n=num_id
            )
        )
    if align:
        props.append('<w:jc w:val="{a}"/>'.format(a=align))
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
    has_content = False
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
            # APA permits the singular for a one-entry list, and matching only the
            # plural silently dropped the hanging indent on the one list small enough
            # for a reader to notice. The two spellings do not get the same rule: the
            # plural keeps its prefix match, because no ordinary heading opens with it,
            # while the singular has to be the whole heading -- ``Reference Ranges`` is
            # a lab heading, and since a match now also centers and breaks the page, a
            # wrong one is louder than a stray indent.
            in_references = bool(re.match(r"references\b|reference\s*$", text, re.I))
            out.append(
                para(
                    text,
                    style="Heading{n}".format(n=level),
                    # A page break on the document's first paragraph renders an empty
                    # first page, so a document that opens on its reference list takes
                    # the centering and not the break.
                    page_break=in_references and has_content,
                    align="center" if in_references else "",
                )
            )
            has_content = True
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_rule(lines[index + 1]):
            rows = [split_row(stripped)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(split_row(lines[index].strip()))
                index += 1
            out.append(table(rows))
            has_content = True
            continue

        bullet = re.match(r"([ \t]*)[-*+]\s+(.*)", line)
        if bullet:
            level = min(len(bullet.group(1).expandtabs(4)) // 2, 2)
            out.append(para(bullet.group(2), style="ListParagraph", num_id=1, level=level))
            has_content = True
            index += 1
            continue

        numbered = re.match(r"([ \t]*)\d+[.)]\s+(.*)", line)
        if numbered:
            level = min(len(numbered.group(1).expandtabs(4)) // 2, 2)
            out.append(para(numbered.group(2), style="ListParagraph", num_id=2, level=level))
            has_content = True
            index += 1
            continue

        out.append(para(stripped, style="Reference" if in_references else ""))
        has_content = True
        index += 1

    return "".join(out)


def document_xml(markdown: str) -> str:
    # ``headerReference`` is the first child of ``sectPr`` because the schema puts it
    # there; a reference written after ``pgSz`` is a file Word declines to open.
    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="{h}"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="{m}" w:right="{m}" w:bottom="{m}" w:left="{m}" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
    ).format(m=MARGIN, h=HEADER_ID)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        "<w:document {w} {r}><w:body>{b}{s}</w:body></w:document>"
    ).format(w=W, r=R, b=body_xml(markdown), s=sect)


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
        archive.writestr("word/header1.xml", HEADER)
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
