"""Render a Markdown subset to a .docx, with the standard library and nothing else.

    python tools/docx_write.py <in.md> <out.docx> [--force]

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
page break and centers, because APA 7 starts the list on a new page under a bold centered
label. The switch is on the *heading*, so a document with no References section never
pays for any of it.

**The APA rules themselves are owned by
``skills/practicum-case-study/reference/apa7.md``, not by this docstring.** That sheet is
verified against apastyle.apa.org and carries the caveat that the *Publication Manual*'s
section numbers are pointers rather than checked claims, since the manual is not in this
repo. Section numbers named here and in the tests are pointers on the same terms.

**Page setup is APA 7 student paper**: Times New Roman 12 pt, double spaced, 1 inch
margins, and a page number in the top right of every page -- the ``word/header1.xml``
part, which is the only reason this archive carries a header at all. Headings are body
size at every level, distinguished the way APA distinguishes them: level 1 bold
centered, level 2 bold flush left, level 3 bold italic flush left, level 4 bold
indented. The rubric gives APA format 5 of 100 points, and this is most of what that
line can be given mechanically -- see ``skills/practicum-case-study/reference/rubric.md``.

**It refuses to overwrite a document it did not write, and that is #279.** ``output/``
is gitignored, so a destructive write here has no recovery -- and the destination is the
one file this repo produces that a human opens in an editor. Two failures, and neither is
the other's:

* **A render that raises** used to truncate the destination *before* building the content,
  turning a good document into a six-part archive with ``word/document.xml`` absent, which
  Word declines to open. The archive is built into a sibling and ``os.replace``d into place
  now -- ``guidelines_index.build``'s arrangement and its reason. **No hand edit is
  involved in this one**, so none of the three signals #279's body lists reaches it, and
  ``--force`` would not have helped: the author did intend to write.
* **A hand edit** is refused, with ``--force`` to proceed -- ruled by the clinician on
  2026-08-19 over warning, on this repo's posture that a silent destructive success is the
  worst outcome. Two signals, in ``refusal`` below: Word's ``~$`` owner file beside the
  document, which means it is open *right now*, and an archive whose part list is not
  ``PART_NAMES``, which means something other than this renderer wrote it.

**The ticket's own signal 2 -- the ``.docx`` being newer than the ``.md`` -- is not
implemented, and it cannot be.** A render writes the ``.docx`` after the ``.md``, so
*newer* is the ordinary post-render state: the test would fire on every legitimate
re-render while never once distinguishing a Word save from a render. The part-set test is
exact in the direction that matters instead, and costs one ``namelist()``.

**What that does not reach, declared rather than left to be found.** That a Word save
always changes the part list is a claim about **Word** -- it rewrites the whole package and
adds ``docProps/``, ``word/settings.xml`` and a theme -- and there is no Word in this repo
to check it against, which is ``test_docx.py``'s standing limit arriving on a guard rather
than on a document. An editor that rewrote exactly these seven parts is invisible. The
owner file is Word's alone, so a document open in anything else shows nothing. And the
check is a moment rather than a lock: a Word session that opens the file *after* ``refusal``
returns is not caught -- though ``os.replace`` then fails rather than truncating, which is
the safe direction. **``--force`` is a promise and not a backup**: there is still nothing to
recover from.

Body paragraphs take a 0.5 inch first-line indent and a table is drawn with APA's
horizontal rules rather than a grid -- both #220, and both carved out where APA carves
them out: a heading, a list item, a reference entry and a table cell take no first line,
and the one rule that is not a table edge sits on the header row's cells.

**What it still does not do is ``NOT_APPLIED`` below, not this paragraph.** That list
used to be prose here and prose again in ``apa7.md`` section 6, and a prose edit to
either failed nothing -- so it is one object now, on ``REFERENCE_HEADING``'s precedent,
and ``tools/test_docx.py`` asserts the sheet names the same items. **A rendered .docx is
not an APA-formatted document**, which is ``skills/practicum-case-study/SKILL.md`` step
9's sentence arriving one level down.

Covered by ``tools/test_docx.py``, which writes into a temp directory and reads the
result back with ``docx_read`` -- the round trip is the test, because a ``.docx`` that
Word refuses to open is indistinguishable from a good one until Word opens it.
"""

from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path

from console_codec import use_utf8

# Twips throughout. One inch is 1440.
MARGIN = 1440
HANGING = 720
FIRST_LINE = 720
LINE_DOUBLE = 480


# What this renderer does **not** apply. One object rather than prose repeated in two
# files -- ``skills/practicum-case-study/reference/apa7.md`` section 6 carries the same
# list for a reader of the skill, and ``tools/test_docx.py`` asserts the two name the
# same items. #220's own comment is why: a code regression fails a behavior test, and a
# prose edit to either copy failed nothing, so the reader who was misled was the one who
# checked the file nearer to hand.
#
# The first element is a **distinctive phrase from** the sheet's row, matched as a
# substring -- not the phrase it opens with, which two of these are not. That is what
# makes the comparison mechanical rather than a judgment about wording; the second
# element is why the row is here.
#
# **The last two rows are not #220's**, and they were not on the sheet before it either:
# they are a gap that ticket's repair surfaced. Section 6 claimed the renderer applied
# *most of* section 1, which was true and vague, and rewriting it to a checkable claim
# is what showed that two of section 1's bullets had never been on either table. Both
# are recorded rather than filed, for the reason each row states.
NOT_APPLIED = (
    (
        "title page",
        "An APA 7 student title page is a fixed set of elements -- title, author, "
        "affiliation, course number and name, instructor, due date -- and none of the "
        "six is in the Markdown this is handed. Where they come from is a "
        "``practicum-case-study`` question before it is one for this module.",
    ),
    (
        "run-in",
        "APA level 4 and 5 headings are run-in, and Markdown gives a heading its own "
        "line. Level 4 renders as the indented bold paragraph the run-in form is "
        "otherwise identical to, and level 5 is not in the subset at all.",
    ),
    (
        "alphabetized",
        "Sorting a reference list is an **edit to the document** rather than a format "
        "applied to it, and this renderer changes no word it is handed. So the order "
        "stays the author's, and ``tools/reference_scan.py`` grades it against section "
        "1 instead -- its ``list-not-sorted`` row.",
    ),
    (
        "one paragraph",
        "Section 1 wants each entry to be one paragraph, and ``body_xml`` makes a "
        "paragraph of every non-blank line -- so a hard-wrapped entry renders as two, "
        "and the second hangs on nothing. Joining them is an edit on the same terms "
        "as sorting, and it is caught as an author defect instead -- by "
        "``skills/practicum-case-study/SKILL.md`` step 7.",
    ),
)


# APA 7 section 7.8: a table carries horizontal rules only. Three of them -- above the
# header row, below the header row, below the last row -- and never a vertical one.
# Ruled unconditional by the clinician on 2026-08-19 rather than switchable, on #217's
# fourth row's precedent: the only consumer of this renderer is an APA document, and a
# parameter no caller passes is a branch nothing honestly tests.
#
# **An edge that is off is written as an explicit ``none`` rather than omitted**, because
# an omitted edge inherits from the table style -- and a table style is exactly what this
# used to draw its grid from.
def _edge(name: str, drawn: bool) -> str:
    """One border edge, drawn or explicitly off."""
    if drawn:
        return '<w:{n} w:val="single" w:sz="4" w:color="000000"/>'.format(n=name)
    return '<w:{n} w:val="none" w:sz="0" w:space="0" w:color="auto"/>'.format(n=name)


# ``CT_TblBorders`` is a sequence: top, left, bottom, right, insideH, insideV.
BORDERS = "<w:tblBorders>{edges}</w:tblBorders>".format(
    edges="".join(
        _edge(name, drawn)
        for name, drawn in (
            ("top", True),
            ("left", False),
            ("bottom", True),
            ("right", False),
            ("insideH", False),
            ("insideV", False),
        )
    )
)

# The rule under the header is the one that is not a table edge, so it is set on that
# row's cells. ``insideH`` would draw it between every pair of body rows as well.
HEADER_RULE = "<w:tcBorders>{b}</w:tcBorders>".format(b=_edge("bottom", True))

# The style is named for what it draws. It carried Word's built-in ``TableGrid`` name
# while it drew a grid; keeping that name over APA borders would be a false statement
# inside the file, and ``BORDERS`` overriding it in every ``tblPr`` would not make the
# style itself true.
TABLE_STYLE_ID = "APATable"

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


# The heading that turns a section into the reference list. APA permits the
# singular for a one-entry list, and matching only the plural silently dropped the
# hanging indent on the one list small enough for a reader to notice. **The two
# spellings do not get the same rule**: the plural keeps its prefix match, because
# no ordinary heading opens with it, while the singular has to be the whole heading
# -- ``Reference Ranges`` is a lab heading, and since a match now also centers and
# breaks the page, a wrong one is louder than a stray indent.
#
# **It is a module constant rather than an inline pattern because
# ``reference_scan.py`` imports it.** Since #217 this heading is what *applies* the
# indent, so a scanner holding its own copy of the rule could pass a document this
# renderer sets wrong -- #218, and a test asserts the two are one object.
REFERENCE_HEADING = re.compile(r"references\b|reference\s*$", re.I)


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
<w:style w:type="table" w:styleId="{table}"><w:name w:val="APA Table"/>
<w:tblPr>{borders}</w:tblPr></w:style>
</w:styles>""".format(
    w=W,
    line=LINE_DOUBLE,
    hang=HANGING,
    table=TABLE_STYLE_ID,
    borders=BORDERS,
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
    first_line: bool = False,
) -> str:
    """One paragraph. The property order is the schema's, not a preference.

    ``CT_PPrBase`` is a sequence rather than a set -- ``pStyle``, ``pageBreakBefore``,
    ``numPr``, ``ind``, then ``jc`` -- and Word refuses a file whose properties arrive
    out of order. Nothing here validates that, so the order is kept by construction.

    ``first_line`` is APA 7 section 2.24's 0.5 inch body indent, and it is a parameter
    rather than a default on ``Normal`` because the rule has carve-outs: a heading, a
    list item and a reference entry all take none, and the last of those would have its
    hanging indent cancelled by one. ``body_xml`` sets it on the plain-paragraph branch
    and nowhere else.
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
    if first_line:
        props.append('<w:ind w:firstLine="{f}"/>'.format(f=FIRST_LINE))
    if align:
        props.append('<w:jc w:val="{a}"/>'.format(a=align))
    ppr = "<w:pPr>{p}</w:pPr>".format(p="".join(props)) if props else ""
    return "<w:p>{ppr}{r}</w:p>".format(ppr=ppr, r=runs(text))


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
            # ``CT_TcPrBase`` is a sequence too: ``tcW`` before ``tcBorders``.
            cells.append(
                '<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{b}</w:tcPr>'
                '<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/></w:pPr>'
                "{r}</w:p></w:tc>".format(
                    w=cell_width,
                    b=HEADER_RULE if index == 0 else "",
                    r=runs(text, bold=index == 0),
                )
            )
        header = "<w:trPr><w:tblHeader/></w:trPr>" if index == 0 else ""
        body.append("<w:tr>{h}{c}</w:tr>".format(h=header, c="".join(cells)))
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="{s}"/>'
        '<w:tblW w:w="0" w:type="auto"/>{b}</w:tblPr>'
        "<w:tblGrid>{g}</w:tblGrid>{rows}</w:tbl><w:p/>"
    ).format(s=TABLE_STYLE_ID, b=BORDERS, g=grid, rows="".join(body))


def split_row(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_rule(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)


def table_first_cells(block: str) -> list:
    """The first cell of every row of the first Markdown table in ``block``.

    **One reader of a documentation table, not two.** Both
    ``tools/test_docx.py`` and ``tools/test_reference_scan.py`` bind a list in a
    reference sheet to a declared object in code -- ``NOT_APPLIED`` against
    ``apa7.md`` section 6, ``reference_scan.NOT_REACHED`` against its section 7 --
    and each had its own copy of this loop, comment included, until #241's review
    caught the second one being written. That is the duplication those very classes
    exist to refuse, so the loop lives here beside the ``split_row`` it is built on.

    The header row sits above the ``---`` rule and is a column label rather than an
    item; counting it would put every such table one ahead forever.
    """
    cells, started = [], False
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if started:
                break
            continue
        if is_rule(line):
            started = True
            continue
        first = split_row(line)[0]
        if started and first:
            cells.append(first.replace("**", ""))
    return cells


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
            # ``REFERENCE_HEADING`` above carries the rule and why it is a module
            # constant rather than an inline pattern.
            in_references = bool(REFERENCE_HEADING.match(text))
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

        # APA 7 section 2.24's first-line indent lands here and on no other branch:
        # a heading, a list item and a reference entry are each carved out above.
        out.append(
            para(
                stripped,
                style="Reference" if in_references else "",
                first_line=not in_references,
            )
        )
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


class RefusedToOverwrite(Exception):
    """The destination holds work this renderer did not write, or Word has it open."""


def parts(markdown: str) -> dict:
    """Every part of the archive, keyed by name, in the order it is written.

    **One object, so the guard cannot hold a different answer than the writer.**
    ``word/header1.xml`` arrived late -- on #217 -- and a part list typed by hand into
    ``written_by_this_renderer`` would have called every document produced after that
    foreign, or every one produced before it ours.
    """
    return {
        "[Content_Types].xml": CONTENT_TYPES,
        "_rels/.rels": ROOT_RELS,
        "word/_rels/document.xml.rels": DOC_RELS,
        "word/styles.xml": STYLES,
        "word/numbering.xml": NUMBERING,
        "word/header1.xml": HEADER,
        "word/document.xml": document_xml(markdown),
    }


# Derived rather than restated, on ``NOT_APPLIED``'s and ``REFERENCE_HEADING``'s terms:
# an eighth part cannot arrive with the guard below still passing.
PART_NAMES = frozenset(parts(""))


def lock_files(destination: Path) -> tuple:
    """The two names Word gives its owner file, either of which means *open right now*.

    Word prepends ``~$`` to a short name and **replaces the first two characters** of a
    long one, and that is not a rule worth remembering wrong: #279's own directory
    listing is the evidence -- ``nur5144-m1-2026-08-19.docx`` locked by
    ``~$r5144-m1-2026-08-19.docx``. Both shapes are looked for rather than the length
    threshold between them being guessed at.
    """
    candidates = [destination.with_name("~$" + destination.name)]
    if len(destination.name) > 2:
        candidates.append(destination.with_name("~$" + destination.name[2:]))
    return tuple(candidates)


def written_by_this_renderer(destination: Path) -> bool:
    """Whether the file at ``destination`` carries exactly the parts ``parts`` writes.

    **The certain direction is the positive one**: anything this renderer produced has
    this part set, because both come from one object. The module docstring carries what
    the other direction rests on and why it is not asserted. A file that will not open as
    a zip, or will not open at all, reads as not ours, which is the safe direction.
    """
    try:
        with zipfile.ZipFile(destination) as archive:
            return frozenset(archive.namelist()) == PART_NAMES
    except (OSError, zipfile.BadZipFile):
        return False


def refusal(destination: Path) -> str:
    """Why writing to ``destination`` would destroy work, or ``""`` if it would not.

    The owner file is checked first because it is the one case that is also true of a
    document this renderer *did* write -- so the part-set test would pass it -- and
    because it is the moment the write may fail on a sharing violation anyway.

    Every message names ``--force``. A refusal that does not say how to proceed is a dead
    end rather than a guard, and the run that meets one is a legitimate re-render often
    enough that it has to be.

    **The part-set message names two causes and the second one is not hypothetical.**
    ``word/header1.xml`` arrived on #217, so **every document rendered before that reads
    as foreign** -- the claim *not written by this renderer* is exactly true of it, and
    ``a Word save, most likely``, which is what this said first, is the wrong guess. Found
    by pointing the guard at the real ``output/case-studies/`` rather than by a fixture:
    of the two documents there, the one #279 was filed over reads as **ours** -- so the
    clinician had in fact not saved it, which is what he told the session that asked --
    and the older one reads as foreign for the version reason alone. That is
    ``block_scan.py``'s and ``threshold_sheet.py``'s lesson a further time.
    """
    for lock in lock_files(destination):
        if lock.exists():
            return (
                "{d} is open in Word right now -- {l} is beside it. Close the document, "
                "or pass --force to overwrite it anyway.".format(d=destination, l=lock.name)
            )
    if destination.exists() and not written_by_this_renderer(destination):
        return (
            "{d} was not written by this renderer -- either something else saved it, "
            "most likely Word, or an older version of this renderer wrote it before the "
            "part set changed. Rendering over it destroys whatever is in it, and output/ "
            "is gitignored so there is no recovery. Pass --force if that is what you "
            "want.".format(d=destination)
        )
    return ""


def partial_name(destination: Path) -> Path:
    """The sibling the archive is built into before it is moved into place.

    ``guidelines_index.build``'s arrangement with the process id added. #279's own
    parenthetical is why: #276 records a *fixed* temp name being unsafe under
    concurrency, and while this is one writer to one destination, a name carrying nothing
    is the shape that ticket is about.
    """
    return destination.with_name(
        "{n}.{pid}.building".format(n=destination.name, pid=os.getpid())
    )


def write_docx(markdown: str, destination, force: bool = False) -> Path:
    """Render ``markdown`` to ``destination``, refusing to destroy work it did not write.

    The archive is built into a sibling and moved into place, so a render that dies part
    way leaves the previous document intact rather than the truncated archive #279
    recorded. ``force`` skips ``refusal`` and nothing else -- the sibling is not a mode.

    **Building the payload before opening the sibling would be a second mechanism, and
    it was written that way first.** It reads as a guard and is not one: with the write
    going to a sibling the ordering is unobservable, so the mutation that moved it back
    inside left the whole suite green. Worse, it made the ``except`` limb below
    unreachable from the one test aimed at it -- a raise in ``document_xml`` happened
    before the sibling existed, so nothing exercised the cleanup. One mechanism, and the
    limb is now on the path the test drives.
    """
    destination = Path(destination)
    if destination.parent != Path("."):
        destination.parent.mkdir(parents=True, exist_ok=True)
    if not force:
        reason = refusal(destination)
        if reason:
            raise RefusedToOverwrite(reason)
    partial = partial_name(destination)
    partial.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in parts(markdown).items():
                archive.writestr(name, content)
        os.replace(partial, destination)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return destination


USAGE = "usage: docx_write.py <in.md> <out.docx> [--force]"


def main(argv: list) -> int:
    force = "--force" in argv
    argv = [argument for argument in argv if argument != "--force"]
    if len(argv) < 2:
        print(USAGE)
        return 2
    source = Path(argv[0])
    if not source.is_file():
        print("not a file: {p}".format(p=source))
        return 2
    try:
        written = write_docx(source.read_text(encoding="utf-8"), Path(argv[1]), force=force)
    except RefusedToOverwrite as reason:
        # 2 is every way of not having written, on ``docx_read.py``'s convention -- and
        # there is no 1 here, because a writer has no "found nothing" to report.
        print("refused: {r}".format(r=reason), file=sys.stderr)
        return 2
    print("wrote {p} ({n} bytes)".format(p=written, n=written.stat().st_size))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
