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
            # U+F0B7 and not U+2022. The run is set in ``Symbol``, which is a
            # symbol-encoded font: Word looks the code point up *in Symbol* rather
            # than in Unicode, and Symbol has no glyph at U+2022, so a bullet
            # written there renders as an empty box. The clinician reported exactly
            # that -- "I don't know what those square blocks are supposed to be".
            marker = ""
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


def numbering_xml(decimal_lists: int = 1) -> str:
    """The ``word/numbering.xml`` part, sized to the body that will reference it.

    **One ``w:num`` per numbered list, and that is the whole restart mechanism.**
    Word restarts a list at 1 for each ``w:num`` that points at an abstract
    definition; two lists sharing one ``numId`` are *one* list to Word, however far
    apart they sit and whatever comes between them. Before #215's follow-up every
    numbered list in the document shared ``numId`` 2, so the Differential ran 1-7,
    the MDM opened at 8 and the Plan carried on from wherever the MDM stopped --
    the clinician's *"each section that is broken up is a continuation of the
    previous section's number, that is bad, it should start over"*.

    ``numId`` 1 is the bullet list. The decimal lists are numbered from 2 up, in the
    order ``render_body`` meets them, and all of them share abstract definition 1 --
    so the format is defined once and only the restart point is per-list.
    """
    nums = ['<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>']
    for index in range(max(decimal_lists, 1)):
        nums.append(
            '<w:num w:numId="{n}"><w:abstractNumId w:val="1"/></w:num>'.format(
                n=index + 2
            )
        )
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {w}>
{bullet}
{decimal}
{nums}
</w:numbering>""".format(
        w=W,
        bullet=_abstract_num(0, "bullet"),
        decimal=_abstract_num(1, "decimal"),
        nums="\n".join(nums),
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
            inner = piece[2:-2]
            # **One level of nesting, and it is the level the corpus actually
            # writes.** A bold statement carrying an italicised organism name --
            # ``**... due to *Neisseria gonorrhoeae* ...**`` -- used to emit the
            # inner asterisks as literal text, because the outer span was consumed
            # whole and never re-split. That is the stray ``*`` the clinician found
            # in the Most Likely Clinical Diagnosis line of a graded document.
            if _INLINE.search(inner):
                out.append(runs(inner, bold=True))
                continue
            is_bold, body = True, inner
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            is_italic, body = True, piece[1:-1]
        elif piece.startswith("`") and piece.endswith("`") and len(piece) > 2:
            is_mono, body = True, piece[1:-1]
        # ``CT_RPr`` is a sequence like ``CT_PPrBase`` in ``para`` above --
        # ``rStyle``, ``rFonts``, ``b``, ``i`` -- and Word refuses a file whose
        # run properties arrive out of order. ``rFonts`` therefore goes first.
        # This was unreachable from body text until bold learned to nest, and a
        # bold span carrying a monospace one now produces both at once.
        props = ""
        if is_mono:
            props += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
        if is_bold:
            props += "<w:b/>"
        if is_italic:
            props += "<w:i/>"
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
        for column, text in enumerate(row):
            # **A short row merges rather than padding, and its last cell takes the
            # slack.** A Markdown table has no span syntax, so the number of cells a
            # row declares is the only signal available. Before #215's follow-up a
            # short row was right-padded with empties, which is why every line of an
            # ``Rx:`` block below the first sat in column 1 with two blank columns
            # beside it -- the clinician's *"everything was put into the left sided
            # column"*. One cell now spans the table, and a two-cell row puts the
            # first cell on the left and the second on the right.
            span = width - len(row) + 1 if column == len(row) - 1 else 1
            # ``CT_TcPrBase`` is a sequence: ``tcW``, ``gridSpan``, then ``tcBorders``.
            cells.append(
                '<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{g}{b}</w:tcPr>'
                '<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/>{j}</w:pPr>'
                "{r}</w:p></w:tc>".format(
                    w=cell_width * span,
                    g='<w:gridSpan w:val="{n}"/>'.format(n=span) if span > 1 else "",
                    b=HEADER_RULE if index == 0 else "",
                    j='<w:jc w:val="right"/>'
                    if len(row) > 1 and column == len(row) - 1 and span > 1
                    else "",
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


# The two spellings of a pipe that is content rather than a cell boundary. ``&#124;`` is
# what ``style.md`` section 8 wrote; the backslash is what a run reached for when it
# noticed the shape was wrong, and #293 taught ``split_row`` both.
#
# **It is declared for the reporting side, and ``split_row`` reads neither element** --
# it walks the backslash character by character because it has to look ahead, and holds
# its own ``&#124;`` literal. That is not the ``REFERENCE_HEADING`` arrangement and
# should not be read as one: nothing here makes the parser and the scanner share an
# object. What binds them is a **test** -- ``tools/test_docx.py`` asserts ``split_row``
# consumes every form named here -- because a scanner reporting a spelling the parser
# leaves alone would send a run chasing a cell that already works.
PIPE_ESCAPES = ("\\|", "&#124;")


def split_row(line: str) -> list:
    r"""Split a Markdown table row on its **unescaped** pipes.

    ``\|`` is a literal pipe in the cell, which is how a Markdown table carries a
    pipe as content at all. Before #215's follow-up this split on every ``|`` and
    left the backslash sitting in the cell, so ``Rx:`` row 1 rendered as
    ``<patient> \`` -- the clinician's *"the patient carries a \ and so do the end
    of my titles"*. ``style.md`` section 8 wrote the same pipe as ``&#124;``, which
    ``esc`` turns into a literal ``&#124;``; both spellings are handled here so the
    sheet and the runs agree.
    """
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith(r"\|"):
        line = line[:-1]
    cells, buf, index = [], [], 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line) and line[index + 1] == "|":
            buf.append("|")
            index += 2
            continue
        if char == "|":
            cells.append("".join(buf).strip())
            buf = []
            index += 1
            continue
        buf.append(char)
        index += 1
    cells.append("".join(buf).strip())
    return [c.replace("&#124;", "|") for c in cells]


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


def markdown_tables(text: str) -> list:
    """Every Markdown table in ``text``, each as the source block ``render_body`` reads.

    **One reader of a documentation table, not two** -- ``table_first_cells``'s note
    above, and the same reason. ``tools/test_docx.py`` extracts ``style.md`` section 8's
    ``Rx:`` table with this and renders it, and walks every table in the skill's
    reference sheets with it for #280's general row; a second copy of the loop is the
    duplication that function was consolidated to refuse.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    blocks, index = [], 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("|") and index + 1 < len(lines) and is_rule(lines[index + 1]):
            block = [line, lines[index + 1].strip()]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index].strip())
                index += 1
            blocks.append("\n".join(block) + "\n")
            continue
        index += 1
    return blocks


_RUN_TEXT = re.compile(r'<w:t xml:space="preserve">(.*?)</w:t>', re.DOTALL)
_TABLE_CELL = re.compile(r"<w:tc>.*?</w:tc>", re.DOTALL)

# The row's name as a reader will see it rather than the character, because a cell may
# legitimately hold a pipe once ``PIPE_ESCAPES`` is decoded and the finding is about
# *where* it landed.
CELL_SEPARATOR = "| in a table cell"

# The ticket's row is *no run contains a literal backslash or* ``&#124;``, and the escape
# limb narrows the first half to ``\\|`` because that is what the parser consumes. **A lone
# backslash is the recorded symptom itself** -- *"the patient carries a ``\``"* -- so it
# is reported where it was read off the page, in a cell. Outside a table it is left
# alone and that is declared rather than widened: a backslash in running prose is
# somebody quoting a path or a pattern, and this warning has to stay worth reading.
CELL_BACKSLASH = "a backslash in a table cell"


def _unesc(text: str) -> str:
    """``esc`` run backwards. The ampersand last, so a decoded ``&lt;`` is not re-read."""
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def separator_artifacts(markdown: str) -> list:
    r"""Runs of the rendered document carrying a cell separator as text -- #280.

    **No documented table shape may render to text containing its own separator
    syntax**, which is the general row that ticket asked for. It has three limbs
    because the defect has three forms, and **the ticket wrote only the last**:

    * a **table cell whose text holds a pipe**, which is a row declaring a width the
      grid does not have. That is the shape section 8 documented, and the reason the
      whole prescription rendered into column 1;
    * a **table cell holding a backslash**, which is the clinician's own reading of the
      rendered page and the half of the ticket's row that ``PIPE_ESCAPES`` narrows; and
    * a run anywhere carrying one of ``PIPE_ESCAPES`` **undecoded** -- which since #293
      can only happen outside a table, where nothing consumes it, so it reaches the page
      as a visible ``&#124;`` or the stray backslash the clinician read off the first
      Module 1 submission.

    **The first limb is the one with the recorded defect behind it**, and stating the
    row as the ticket did would have missed it: ``split_row`` decodes both spellings
    now, so the retired section 8 no longer puts either on the page -- it puts two
    pipes inside one cell instead, which is the same defect one layer down.

    Read off the rendered XML rather than off the Markdown, which is
    ``tools/test_docx.py``'s standing instrument: the claim is about what a reader of
    the document gets.

    **One finding per offending run, and a finding is a form and nothing else** -- a
    value of ``PIPE_ESCAPES``, ``CELL_SEPARATOR`` or ``CELL_BACKSLASH``. So the output
    is bounded by what this code can draw on rather than by what a caller remembers not
    to print, and a
    draft is written about a patient. **The first version returned the run's text
    beside the form and no caller ever read it**, which left the bounded claim resting
    on caller discipline; ``/code-review`` found it.

    **It lives here rather than in a ``tools/*_scan.py`` because it reads this module's
    own output**, and because the clinician ruled the check runs in the render command
    -- which is this one. ``reference_scan.py`` is the other arrangement and has the
    other subject: it grades a draft the renderer did not produce.

    **What it cannot reach**, named rather than left to be found. A table that renders
    cleanly and is **wrong**: a six-row ``Rx:`` whose ``Sig:`` says the wrong thing
    satisfies every limb. A **backslash outside a table**, by the decision above. And
    it cannot tell a faked width from a cell that **means** its pipe -- an author who
    writes ``\|`` deliberately gets a warning, which is the price of a row that reads
    the output rather than the intent, and is why this warns instead of refusing.
    """
    xml = body_xml(markdown)
    found = []
    for cell in _TABLE_CELL.findall(xml):
        for raw in _RUN_TEXT.findall(cell):
            text = _unesc(raw)
            if "|" in text:
                found.append(CELL_SEPARATOR)
            if "\\" in text:
                found.append(CELL_BACKSLASH)
    for raw in _RUN_TEXT.findall(xml):
        text = _unesc(raw)
        for escape in PIPE_ESCAPES:
            if escape in text:
                found.append(escape)
    return found


def body_xml(markdown: str) -> str:
    """Convert the Markdown subset to the payload of a ``w:body`` element."""
    return render_body(markdown)[0]


# The Markdown subset, as three patterns and a name for the separators. **They
# were inline in ``render_body`` and are constants because a second reader now
# exists.** ``reference_scan.py`` imports ``REFERENCE_HEADING`` for the reason
# written beside it -- a scanner holding its own copy of a rule can pass a
# document the renderer sets wrong -- and ``blocks`` below is that argument at
# the width of the whole parse rather than at one heading.
HEADING = re.compile(r"(#{1,4})\s+(.*)")
BULLET = re.compile(r"([ \t]*)[-*+]\s+(.*)")
NUMBERED = re.compile(r"([ \t]*)\d+[.)]\s+(.*)")
SEPARATORS = ("---", "***", "___")


class Block:
    """One thing the renderer will set, and the source line it opens on.

    ``kind`` is one of ``blank``, ``separator``, ``heading``, ``table``,
    ``bullet``, ``numbered`` and ``paragraph`` -- the seven branches
    ``render_body`` had, named. ``line`` is 1-indexed and nothing in this module
    reads it; it is there because a scanner reports a finding at a line.
    """

    __slots__ = ("kind", "text", "line", "level", "rows")

    def __init__(self, kind, text="", line=0, level=0, rows=()):
        self.kind = kind
        self.text = text
        self.line = line
        self.level = level
        self.rows = rows

    def __repr__(self):  # pragma: no cover - diagnostics only
        return "Block({k!r}, {t!r}, line={n})".format(k=self.kind, t=self.text, n=self.line)


def blocks(markdown: str):
    """Read the Markdown subset once, into ``Block`` objects.

    **This is the whole of the renderer's reading and there is no second copy of
    it.** ``render_body``'s own docstring already named the risk -- *a second pass
    over the same Markdown is a second parser to keep in step* -- and
    ``tools/case_study_scan.py`` is that second pass: it grades a draft on rules
    whose failure is a rendered one, so a line it calls a bullet has to be a
    bullet in the ``.docx``. Importing the three patterns would have left two
    loops that could still disagree about where a table ends; consuming this
    leaves none.

    **A fenced code block is not a branch here, and that is the renderer's
    behavior rather than an omission of this function's.** A fence opens nothing,
    so a bulleted line inside one is set as a bullet in the finished document --
    which is why ``case_study_scan.py`` grants no mention-versus-use exemption
    for one, where ``spelling_scan.py`` reading a skill file does.
    """
    lines = markdown.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        number = index + 1

        if not stripped:
            yield Block("blank", line=number)
            index += 1
            continue

        if stripped in SEPARATORS:
            yield Block("separator", stripped, line=number)
            index += 1
            continue

        heading = HEADING.match(stripped)
        if heading:
            yield Block(
                "heading",
                heading.group(2).strip(),
                line=number,
                level=len(heading.group(1)),
            )
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_rule(lines[index + 1]):
            rows = [tuple(split_row(stripped))]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(tuple(split_row(lines[index].strip())))
                index += 1
            yield Block("table", line=number, rows=tuple(rows))
            continue

        bullet = BULLET.match(line)
        if bullet:
            yield Block(
                "bullet",
                bullet.group(2),
                line=number,
                level=min(len(bullet.group(1).expandtabs(4)) // 2, 2),
            )
            index += 1
            continue

        numbered = NUMBERED.match(line)
        if numbered:
            yield Block(
                "numbered",
                numbered.group(2),
                line=number,
                level=min(len(numbered.group(1).expandtabs(4)) // 2, 2),
            )
            index += 1
            continue

        yield Block("paragraph", stripped, line=number)
        index += 1


def render_body(markdown: str):
    """``(body payload, number of decimal lists)``.

    The count is what ``numbering_xml`` has to be sized by, and it is returned
    rather than recomputed because a second pass over the same Markdown is a
    second parser to keep in step -- which is the duplication
    ``table_first_cells`` above was consolidated to refuse, and which is why the
    reading itself is ``blocks`` above rather than a loop in here.
    """
    out = []
    in_references = False
    has_content = False
    # 0 means "no list open": the next numbered line allocates a fresh ``numId``.
    decimal_id = 0
    decimal_lists = 0
    for block in blocks(markdown):
        if block.kind == "blank":
            if not in_references:
                out.append("<w:p/>")
            continue

        if block.kind == "separator":
            continue

        if block.kind == "heading":
            # ``REFERENCE_HEADING`` above carries the rule and why it is a module
            # constant rather than an inline pattern.
            in_references = bool(REFERENCE_HEADING.match(block.text))
            # A heading closes whatever list was open, so the next numbered line
            # allocates a fresh ``w:num`` and Word restarts it at 1. This is the
            # only place the counter resets: a plain paragraph *between* two
            # numbered items is a continuation of one list and must not restart it.
            decimal_id = 0
            out.append(
                para(
                    block.text,
                    style="Heading{n}".format(n=block.level),
                    # A page break on the document's first paragraph renders an empty
                    # first page, so a document that opens on its reference list takes
                    # the centering and not the break.
                    page_break=in_references and has_content,
                    align="center" if in_references else "",
                )
            )
            has_content = True
            continue

        if block.kind == "table":
            out.append(table([list(row) for row in block.rows]))
            has_content = True
            continue

        if block.kind == "bullet":
            out.append(para(block.text, style="ListParagraph", num_id=1, level=block.level))
            has_content = True
            continue

        if block.kind == "numbered":
            if not decimal_id:
                decimal_lists += 1
                decimal_id = decimal_lists + 1
            out.append(
                para(
                    block.text,
                    style="ListParagraph",
                    num_id=decimal_id,
                    level=block.level,
                )
            )
            has_content = True
            continue

        # APA 7 section 2.24's first-line indent lands here and on no other branch:
        # a heading, a list item and a reference entry are each carved out above.
        out.append(
            para(
                block.text,
                style="Reference" if in_references else "",
                first_line=not in_references,
            )
        )
        has_content = True

    return "".join(out), decimal_lists


def document_xml(markdown: str, body: str = None) -> str:
    # ``body`` is accepted so ``write_docx`` can parse once and spend the result
    # on both parts. ``render_body``'s docstring is explicit that a second pass
    # over the same Markdown is a second parser to keep in step; this function
    # took one anyway until #215's follow-up review caught it.
    if body is None:
        body = body_xml(markdown)
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
    ).format(w=W, r=R, b=body, s=sect)


def write_docx(markdown: str, destination) -> Path:
    destination = Path(destination)
    if destination.parent != Path("."):
        destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", ROOT_RELS)
        archive.writestr("word/_rels/document.xml.rels", DOC_RELS)
        archive.writestr("word/styles.xml", STYLES)
        body, decimal_lists = render_body(markdown)
        archive.writestr("word/numbering.xml", numbering_xml(decimal_lists))
        archive.writestr("word/header1.xml", HEADER)
        archive.writestr("word/document.xml", document_xml(markdown, body))
    return destination


def main(argv: list) -> int:
    if len(argv) < 2:
        print("usage: docx_write.py <in.md> <out.docx>")
        return 2
    source = Path(argv[0])
    if not source.is_file():
        print("not a file: {p}".format(p=source))
        return 2
    markdown = source.read_text(encoding="utf-8")
    written = write_docx(markdown, Path(argv[1]))
    print("wrote {p} ({n} bytes)".format(p=written, n=written.stat().st_size))
    # **Warn, never refuse** -- ruled by the clinician on 2026-08-19. #280's second
    # comment is why the command warns at all rather than the suite alone binding the
    # sheet: ``style.md`` section 8 is copied by *runs*, and a run executes commands.
    # Refusing was priced and declined -- this renderer is on the consumer's critical
    # path, and a blocked submission is a worse outcome than a separator on the page.
    #
    # Forms and a count, never a run's text. See ``separator_artifacts``.
    artifacts = separator_artifacts(markdown)
    if artifacts:
        # The two streams are buffered independently, so the warning arrives
        # above the line it qualifies unless stdout is drained first.
        sys.stdout.flush()
        print(
            "warning: {n} run(s) carry a cell separator as text rather than a cell "
            "boundary: {f}".format(
                n=len(artifacts), f=", ".join(sorted(set(artifacts)))
            ),
            file=sys.stderr,
        )
        print(
            "warning: a row faking its width renders into column 1, and an escape "
            "nothing consumed reaches the page as text. See "
            "skills/practicum-case-study/reference/style.md section 8 for a table "
            "that declares its columns. #280.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
