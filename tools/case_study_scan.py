"""Grade a ``practicum-case-study`` draft's **body** against the house style.

``reference_scan.py`` grades the reference list. ``research_ledger.py`` and
``checks_ledger.py`` grade the two fan-out records. Nothing graded the case
study's house style, and every house-style finding the clinician returned from
the first rendered Module 1 submission is in the body --
[#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277). His
framing is the ticket: *"is there some machine checkable way to get this right
every time... this prevents me from using this skill for future work."*

**The rules landed as prose in
``skills/practicum-case-study/reference/style.md`` section 1a and in
``SKILL.md``, which is exactly the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled
insufficient: a prose edit to a rule fails nothing.** This is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what
a written instruction cannot do is fail*, arriving at the same skill a third
time.

**It reads the Markdown and not the rendered ``.docx``, ruled 2026-08-19.** Every
row below is visible in the ``.md``, and the two rows whose failure is a
*rendered* one -- the bullet and the prescription table -- are read through
``docx_write.blocks``, which is the renderer's own parse rather than a copy of
it. So a line this calls a bullet is a bullet in the document. **What that does
not reach is anything the Markdown cannot show**, and most of the renderer defects
that shipped with the first submission were of exactly that kind; the blind spot
is named in ``NOT_REACHED`` rather than closed.

**Counts only by default, and ``--show`` output is PHI**, on
``research_ledger.py``'s terms and for its reason: a finished draft is written
about a patient, and several rows here quote a sentence of it. **Deliberately not
``reference_scan.py``'s exception** -- that module's output is bounded by what
its code can draw from, and this one's is not: a scaffolding phrase is a fixed
literal, but a bullet's finding is the bullet's own text.

**Some behavior is deliberately not a row, and this is the load-bearing part.**

The **em dash** is a stated preference with a stated exception -- *"generally I
prefer not to use em dashes, just saying, though I do use them sometimes"* -- so
it is **counted and never graded**. A mechanical filter on a stated preference is
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s own
defect a third time: that ticket exists because a recency rule cut a correct
claim for a property the rule did not care about, and its closing comment records
the same mistake being made again inside the fix.

Authored numbering surprises are counted and never graded. A section that opens
above 1 may deliberately continue the prior list. A drafted 1 starts another
sequence; only a different nonconsecutive transition is counted. The counts put
both shapes in front of a reader without rejecting a correct document.
[#402](https://github.com/mshamblin5150-code/clinical-skills/issues/402).

And **anything the run has to reason about**. A wrapper instruction inherited
from a pediatric case does not apply to a 26-year-old, and the correct behavior
was to fold the substance into the section that already owns it and write no
heading. No string test reaches that, and a row that approximated it would fire
on a document that got it right.

**Exit status distinguishes not having scanned from having found nothing** -- 0
clean, 1 for a defect, **2 for every way of not having scanned**: no argument, no
file, **no section this recognizes in the document**, **a skeleton that
disagrees with the one ``SKILL.md`` publishes**, and **a ``SKILL.md`` this
could not read at all**. The third limb is
``differential_scan.py``'s reasoning -- a draft whose headings are written in a
shape this cannot read would otherwise report zero defects and stand where a
graded document should. The fourth is ``guidelines_catalog.check_legend``'s: two
vocabularies for one skeleton means every section boundary here is drawn
somewhere the skill does not draw it, and a report from that is a report about a
different document. **Where a defect and a not-scanned limb both hold, 1 wins**,
on ``differential_scan.py``'s ordering, and the banner prints beside it so the
finding reads as a floor.

**The skeleton is held here and checked against ``SKILL.md`` from the command.**
``checks_ledger.py`` holds its vocabulary in the module and derives it in the
test; ``guidelines_catalog.check_legend`` parses the published Markdown *in the
command*, and #277's own second comment records why that is the third answer and
the only one a **run** hits -- a test binding is one a run never executes.
Holding *and* checking is both: every row still runs where ``SKILL.md`` is out of
reach, and the **status** says the skeleton went unchecked rather than letting a
clean set of rows stand for a scan against a skeleton nobody confirmed. That is
the fifth exit-2 limb, and it is a claim about the *check* and not about the rows.

**A clean scan is not a checked draft**,
``skills/practicum-case-study/SKILL.md`` step 9 says so beside the command, and a
test asserts that sentence is still there. **The two findings in the clinician's
list that mattered most clinically -- the missing stop criterion's *endpoint*
being the right one, and the growth-and-development section that should not have
existed -- are both in ``NOT_REACHED``.**
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import docx_write
import run_grader

REPO_ROOT = Path(__file__).resolve().parent.parent

# The skill file whose skeleton this is checked against. **The worktree's and not
# the main checkout's** -- ``SKILL.md`` is tracked, so a worktree has its own and
# resolving through ``repo_root.main_repo_root`` would grade this tree against
# another one. That is CLAUDE.md's *most of those callers want the worktree*.
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"

# The twelve skeleton sections, as ``SKILL.md`` writes them under *The skeleton,
# in order*. ``check_skeleton`` below parses that list and refuses a disagreement.
SKELETON = (
    "Sanity Check",
    "Intake block",
    "Assessment:",
    "Differential Diagnoses",
    "Most Likely Clinical Diagnosis",
    "MDM",
    "Plan:",
    "Patient Education:",
    "Rx:",
    "Faculty Questions:",
    "Signed by:",
    "References",
)

# The three intake subsections ``style.md`` section 1a names. They are not
# skeleton items -- they sit inside item 2 -- so they are held separately and are
# not part of the ``SKILL.md`` agreement check.
DEMOGRAPHICS = "Demographics"
REVIEW_OF_SYSTEMS = "Review of Systems"
PHYSICAL_EXAMINATION = "Physical Examination"
INTAKE_SECTIONS = (DEMOGRAPHICS, REVIEW_OF_SYSTEMS, PHYSICAL_EXAMINATION)

# What a finding names where the block it fired on sits under no heading this
# reads -- which is an ordinary place for one to be, since the bullet and the
# scaffolding rows cover the whole document rather than a section of it.
OUTSIDE_ANY_SECTION = "no section this reads"

# Deeper than any heading ``docx_write.blocks`` reads, so an unrecognized
# heading of any level closes a section a label paragraph opened.
LABEL_LEVEL = 99

MOST_LIKELY = "Most Likely Clinical Diagnosis"
RX = "Rx:"
SIGNED_BY = "Signed by:"

# Where ``SKILL.md`` publishes the skeleton, and the shape of one of its items.
SKELETON_OPENS = "The skeleton, in order:"
SKELETON_ITEM = re.compile(r"^\s*\d+\.\s+\*\*(?P<name>[^*]+?)\*\*")

# The closed scaffolding set, from ``style.md`` section 1a's own table. **Closed
# rather than open, and that is a ruling rather than a gap** -- both phrases were
# invented by a run, and there is no general shape for *"this sentence narrates
# the skill's discipline"*. A pattern that tried would fire on prose that reads
# perfectly well. What the closed set costs is written in ``NOT_REACHED``.
SCAFFOLDING = (
    ("Using OLDCARTS", re.compile(r"using\s+OLDCARTS", re.I)),
    ("Ordered, not assumed", re.compile(r"ordered,\s*not\s+assumed", re.I)),
    ("No known drug allergies", re.compile(r"no\s+known\s+drug\s+allergies", re.I)),
)

# The Review of Systems closer. **Matched anywhere in the section rather than only
# at its end**, deliberately: the rule is that the document *says* the unlisted
# systems were asked about, and a closer written a line early still says it. A
# position test would fail a correct document, which is the one outcome
# [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) rules
# out.
ROS_CLOSER = re.compile(r"all\s+other\s+systems?\b.{0,160}?\b(?:negative|unremarkable)", re.I | re.S)

# A paragraph wholly wrapped in ``**``, which is what setting a whole section bold
# looks like in the Markdown the renderer reads.
ALL_BOLD = re.compile(r"^\*\*(?!\s)(?:(?!\*\*).)+\*\*$", re.S)

# A date on the signature line. Three spellings, because the corpus writes the
# first and a run may write either of the others.
SIGNATURE_DATE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},\s*\d{4}\b"
    r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    re.I,
)

# A prescription that recurs, and the endpoints that close one. **A one-time dose
# states its own endpoint**, so ``once`` counts as one -- except where it opens
# ``once daily``, which is the opposite claim and is why the lookahead is there.
RECURRING = re.compile(
    r"\b(?:daily|nightly|every\s+\d+\s*(?:hour|hours|day|days|week|weeks)"
    r"|q\s?\d+\s?h|BID|TID|QID|QHS|QAM|QPM"
    r"|twice\s+(?:a|per)\s+day|three\s+times\s+(?:a|per)\s+day"
    r"|four\s+times\s+(?:a|per)\s+day|weekly|monthly)\b",
    re.I,
)
# A duration is a number and a unit, and the unit set is **every unit an order in
# this corpus is written with** rather than the two the first version had.
# ``for 3 months``, ``x 6 months``, ``for 1 year``, ``x 72 hours`` and ``for 10
# more days`` all close an order that this row then failed anyway -- a false alarm
# on a correct order, which is the one outcome
# [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) rules
# out and the whole reason the em dash is not a row. **Found by running the
# pattern over a set of realistic orders rather than by reading it**, which is
# `block_scan.py`'s and `threshold_sheet.py`'s lesson again.
DURATION = r"\d+\s*(?:hour|day|week|month|year)s?\b"
ENDPOINT = re.compile(
    r"\bx\s?" + DURATION
    + r"|\bx\s?\d+\s*doses?\b"
    + r"|\bfor\s+(?:the\s+next\s+|another\s+)?" + DURATION
    + r"|\bfor\s+\d+\s+more\s+(?:hour|day|week|month|year)s?\b"
    + r"|\buntil\b|\bthrough\b|\bto\s+complete\b|\bsingle\s+dose\b|\bone[-\s]time\b"
    + r"|\bx1\b|\bstop\b|\breassess\w*|\bdiscontinue\w*|\btaper\w*"
    + r"|\bfor\s+the\s+admission\b"
    # **``PRN`` closes an order, and that is a narrowing rather than a reading.**
    # A symptomatic order's endpoint is its indication, so asking one for a
    # duration fires on every correct PRN analgesic. What the narrowing costs is
    # declared in ``NOT_REACHED``.
    + r"|\bPRN\b"
    + r"|\bonce\b(?!\s+(?:daily|nightly|a\s+day|per\s+day|weekly|monthly|every))",
    re.I,
)

# The section 8 prescription table: six data rows, and the cell counts that make
# the merge pattern. Row 1 declares three; the drug, the ``Disp:``, the ``Sig:``
# and the signature declare one each and span the width; the last declares two, so
# the refill sits left and the DEA line right.
RX_ROW_CELLS = (3, 1, 1, 1, 1, 2)
# Which data row carries the drug order. **The stop-criterion row rests on the
# shape row exactly as ``specificity_scan.py``'s C5 rests on C2**: against a table
# of some other shape this index is a question about the run's layout rather than
# about the order, so a run that failed ``rx-table-shape`` has not been graded on
# ``no-stop-criterion``.
RX_DRUG_ROW = 1

# **Counted, never graded. This is a ruling and it is in the code so that a later
# author has to answer for changing it.** See the module docstring.
EM_DASH = "—"

BULLET_MARKER = "bullet-marker"
INTAKE_TABLE = "intake-table"
ROS_NO_CLOSER = "ros-no-closer"
EXAM_CLAIMS_UNEXAMINED = "exam-claims-unexamined"
SCAFFOLDING_PHRASE = "scaffolding-phrase"
DIAGNOSIS_ALL_BOLD = "diagnosis-all-bold"
SIGNATURE_DATE_SPLIT = "signature-date-split"
RX_TABLE_SHAPE = "rx-table-shape"
NO_STOP_CRITERION = "no-stop-criterion"

# Where each row's rule is written, so a reader knows which file to open. Keyed
# rather than built from ``KINDS``, on ``checks_ledger.ROW_TICKET``'s reasoning: a
# comprehension would assign a section to the next row automatically, so the map
# could never fail and the claim that a row cannot arrive without a written rule
# would be a claim about code that does not check it.
ROWS = {
    BULLET_MARKER: "style.md 1a, SKILL.md - never bullets, anywhere",
    INTAKE_TABLE: "style.md 1a - defined fields, never a table",
    ROS_NO_CLOSER: "style.md 1a - the ROS closes with the disclaimer",
    EXAM_CLAIMS_UNEXAMINED: "style.md 1a - and the exam does not",
    SCAFFOLDING_PHRASE: "style.md 1a - no scaffolding language, and NKDA over the expansion",
    DIAGNOSIS_ALL_BOLD: "style.md 1a - Most Likely is not bold",
    SIGNATURE_DATE_SPLIT: "style.md 1a - the signature is one line",
    RX_TABLE_SHAPE: "style.md 8 - six rows, three columns wide",
    NO_STOP_CRITERION: "style.md 8 - a drug that continues carries its stop criterion",
}
KINDS = tuple(ROWS)

# **What no row here reaches, named rather than left to be discovered.**
# ``skills/practicum-case-study/SKILL.md`` step 9 names the same items and a test
# asserts the two agree in both directions -- ``reference_scan.NOT_REACHED``
# against ``apa7.md`` section 7, which is [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s
# repair and is here for its reason: this list sat in two places on that module
# and a prose edit to either failed nothing.
# The second field records the evidence disposition for each limit. ``behavior`` means
# this module's suite drives the public scanner seam and demonstrates the blind spot.
# ``declared-reading`` means the answer requires clinical, applicability, authorship,
# or rendered-page judgment and cannot be re-derived here. It does not claim a reader
# owns the row; that separate gap remains #306. Keeping the disposition on the row
# avoids a second list that can drift.
class EvidenceDisposition(Enum):
    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"


DECLARED_LIMITS = (
    ("the voice, and it never will be", EvidenceDisposition.DECLARED_READING),
    (
        "a wrapper section that does not apply to this patient",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a stop criterion's endpoint is the right endpoint",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a drug ordered PRN needs an endpoint of its own",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "a second drug welded into one drug row, discharged by the first drug's endpoint",
        EvidenceDisposition.BEHAVIOR,
    ),
    ("whether a dose is correct", EvidenceDisposition.DECLARED_READING),
    ("whether a dose was sourced at all", EvidenceDisposition.BEHAVIOR),
    (
        "a scaffolding phrase nobody has written yet",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "anything the Markdown cannot show, which the rendered document can",
        EvidenceDisposition.DECLARED_READING,
    ),
)
NOT_REACHED = tuple(key for key, _ in DECLARED_LIMITS)


def block_text(block) -> str:
    """Everything a block says, table cells included.

    A table's ``text`` is empty because the renderer sets it cell by cell, so a
    row reading prose has to join the cells itself. Extracted after review found
    the join written at three call sites.
    """
    if block.kind == "table":
        return " ".join(cell for row in block.rows for cell in row)
    return block.text


def section_owner(sections: list) -> dict:
    """Line number to the name of the first section that owns it.

    The two rows that read the **whole document** -- the bullet and the
    scaffolding phrase -- still want to say which section a finding landed in,
    and both built this map. One copy.
    """
    owner = {}
    for section in sections:
        for block in section.blocks:
            owner.setdefault(block.line, section.name)
    return owner


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One defect. ``what`` is body prose on most rows, which is why ``--show`` is PHI."""

    where: str
    line: int
    what: str = ""


class Section:
    """A heading and the blocks under it, to the next heading of its level or shallower."""

    __slots__ = ("name", "label", "level", "line", "blocks")

    def __init__(self, name: str, label: str, level: int, line: int):
        self.name = name
        self.label = label
        self.level = level
        self.line = line
        self.blocks = []


@dataclass(frozen=True)
class Scan:
    """What one run found, and what it was able to look at.

    **An annotated dataclass rather than ``__slots__`` filled from ``**kwargs``**,
    which is what this was until review: a misspelled field there was swallowed as
    ``None`` and the row it belonged to reported clean. That is the silent-pass
    shape this whole directory exists to refuse, arriving in the object the report
    is rendered from. ``reference_scan.Scan``'s shape, taken whole.
    """

    findings: list
    sections: int
    intake_sections: int
    tables: int
    em_dashes: int
    numbered_sections_not_opening_at_one: int
    broken_numbered_transitions: int
    no_section: bool
    skeleton_disagreement: list
    skeleton_unread: bool


def normalize(label: str) -> str:
    """A heading, reduced to what makes two labels the same label.

    Drops the emphasis the corpus varies, a trailing colon, a leading list
    numeral, and the case. ``**Review of Systems:**`` and ``Review of systems``
    are one section.
    """
    text = label.strip()
    text = re.sub(r"^\d+[.)]\s*", "", text)
    text = text.replace("**", "").replace("__", "")
    text = text.strip().rstrip(":").strip()
    return re.sub(r"\s+", " ", text).lower()


KNOWN_SECTIONS = {normalize(name): name for name in SKELETON + INTAKE_SECTIONS}


def read_skeleton(text: str) -> tuple[str, ...]:
    """The skeleton ``SKILL.md`` publishes, in order.

    Reads the numbered list that follows ``SKELETON_OPENS`` and stops at the first
    line that is not one of its items, so a later numbered list in the file cannot
    be read as a continuation of this one.
    """
    at = text.find(SKELETON_OPENS)
    if at < 0:
        return ()
    names = []
    started = False
    for line in text[at + len(SKELETON_OPENS) :].splitlines():
        item = SKELETON_ITEM.match(line)
        if item:
            started = True
            names.append(item.group("name").strip())
            continue
        if started and line.strip() and not line.startswith(" "):
            break
    return tuple(names)


def check_skeleton(text: str) -> list[str]:
    """``SKELETON`` is the skeleton the skill publishes, or say how it is not.

    ``guidelines_catalog.check_legend``'s arrangement, and #277's second comment
    is why it is called from the command rather than only from the suite: a test
    binding fires for the person running the tests and never for the run writing
    the document.
    """
    published = read_skeleton(text)
    if not published:
        return ["no skeleton list in SKILL.md, so the section vocabulary cannot be read"]
    if published == SKELETON:
        return []
    failures = []
    for extra in [name for name in published if name not in SKELETON]:
        failures.append(f"SKILL.md publishes section {extra!r}, which this grader does not read")
    for missing in [name for name in SKELETON if name not in published]:
        failures.append(f"this grader reads section {missing!r}, which SKILL.md does not publish")
    if not failures:
        failures.append(
            "SKILL.md publishes the same sections in a different order than this grader holds"
        )
    return failures


def read_sections(markdown: str) -> tuple[list[Section], list]:
    """``(sections, every block)``, reading the draft the way the renderer will.

    A section opens on a **heading** this recognizes, or on a **paragraph that is
    nothing but the label** -- ``**Review of Systems:**`` on its own line, which
    is a shape a run writes and which the renderer sets as an ordinary paragraph.
    A paragraph that merely *starts* with a label and carries a value after it is
    not a heading and does not open one, which is what keeps
    ``Signed by: <name>, RN, CEN, TCRN. August 19, 2026`` a signature rather than
    an empty section.

    **At most one recognized section is open at a time, and that is a statement
    about the vocabulary rather than a simplification.** Every name this reads is
    a *peer* -- no skeleton section nests inside another, and the three intake
    subsections sit inside a skeleton item that is never written as a heading. So
    opening one closes the last, whichever shape either was written in.

    **It was a nesting stack until review**, and the bug that arrangement had is
    the reason the sentence above is written down. A label paragraph was given a
    level deeper than any heading so that it would close a sibling label; against
    a real heading it therefore closed nothing, so ``### Review of Systems``
    followed by ``**Physical Examination:**`` put the examination *inside* the
    Review of Systems and every one of its lines into both. A draft whose ROS
    carried no closer and whose examination carried one reported ``ros-no-closer``
    **zero** -- the row the clinician asked for, passing in silence on the shape
    it exists to catch.

    An **unrecognized** heading closes the open section when it outranks it, and
    always closes a label-opened one: without that, a ``### Note`` under ``Rx:``
    would put every block after it inside the prescription section.
    """
    sections: list[Section] = []
    current: Section | None = None
    every = list(docx_write.blocks(markdown))
    for block in every:
        if block.kind in ("blank", "separator"):
            continue

        opened = None
        if block.kind == "heading":
            known = KNOWN_SECTIONS.get(normalize(block.text))
            if known:
                opened = Section(known, block.text, block.level, block.line)
            elif current is not None and block.level <= current.level:
                current = None
                continue
            else:
                continue
        elif block.kind == "paragraph":
            known = KNOWN_SECTIONS.get(normalize(block.text))
            # A label paragraph carries no value of its own. ``LABEL_LEVEL`` is
            # deeper than any heading the renderer reads, so an unrecognized
            # heading of any level closes one.
            if known:
                opened = Section(known, block.text, LABEL_LEVEL, block.line)

        if opened is not None:
            current = opened
            sections.append(opened)
            continue

        if current is not None:
            current.blocks.append(block)
    return sections, every


def _bullet_findings(sections: list[Section], every: list) -> list[Finding]:
    """No bullet anywhere in the document. Ruled 2026-08-19 -- *"I abhor bullet points"*.

    Read off ``docx_write.blocks`` and so off the renderer's own reading, which is
    what makes the row a claim about the ``.docx`` rather than about the Markdown.
    """
    owner = section_owner(sections)
    return [
        Finding(BULLET_MARKER, owner.get(block.line, OUTSIDE_ANY_SECTION), block.line, block.text)
        for block in every
        if block.kind == "bullet"
    ]


def _intake_findings(sections: list[Section]) -> list[Finding]:
    """Demographics, the ROS and the exam are defined fields, never a table.

    A table is still right for a given result set, which is why this fires only
    inside the three sections section 1a names and nowhere else in the document.
    """
    findings = []
    for section in sections:
        if section.name not in INTAKE_SECTIONS:
            continue
        for block in section.blocks:
            if block.kind == "table":
                findings.append(Finding(INTAKE_TABLE, section.name, block.line, section.name))
    return findings


def _closer_findings(sections: list[Section]) -> list[Finding]:
    """The ROS closes with the disclaimer and the exam does not.

    **Two rows out of one ruling, and the second is the higher-stakes one.** A
    Review of Systems is a question set and the closer is what makes the unlisted
    systems *asked*; an examination is a set of maneuvers actually performed, and
    the same sentence there claims work that was not done.
    """
    findings = []
    for section in sections:
        carried = [
            block for block in section.blocks if ROS_CLOSER.search(block.text or block_text(block))
        ]
        if section.name == REVIEW_OF_SYSTEMS and not carried:
            findings.append(Finding(ROS_NO_CLOSER, section.name, section.line, section.name))
        if section.name == PHYSICAL_EXAMINATION:
            findings.extend(
                Finding(EXAM_CLAIMS_UNEXAMINED, section.name, block.line, block.text)
                for block in carried
            )
    return findings




def _scaffolding_findings(sections: list[Section], every: list) -> list[Finding]:
    """The closed set from section 1a's table, named phrase by phrase in the report."""
    owner = section_owner(sections)
    findings = []
    for block in every:
        text = block.text or block_text(block)
        for phrase, pattern in SCAFFOLDING:
            if pattern.search(text):
                findings.append(
                    Finding(
                        SCAFFOLDING_PHRASE,
                        owner.get(block.line, OUTSIDE_ANY_SECTION),
                        block.line,
                        phrase,
                    )
                )
    return findings


def _bold_findings(sections: list[Section]) -> list[Finding]:
    """The Most Likely Clinical Diagnosis is not wholly bold -- *"I don't do that."*

    Fires where **every** paragraph of the section is wrapped, which is what
    setting the statement bold looks like. A bolded phrase inside a sentence is
    emphasis and is left alone.
    """
    findings = []
    for section in sections:
        if section.name != MOST_LIKELY:
            continue
        paragraphs = [b for b in section.blocks if b.kind in ("paragraph", "numbered", "bullet")]
        if paragraphs and all(ALL_BOLD.match(b.text.strip()) for b in paragraphs):
            findings.append(
                Finding(DIAGNOSIS_ALL_BOLD, section.name, paragraphs[0].line, paragraphs[0].text)
            )
    return findings


def _signature_findings(sections: list[Section], every: list) -> list[Finding]:
    """The signature and the date sit on one line.

    The first submission put the date on its own line beneath, which renders as a
    stray orphan paragraph. The line is found as a block **opening** with the
    label, so a mention of the signature elsewhere in the draft is not read as one.
    """
    for block in every:
        if block.kind in ("blank", "separator", "table"):
            continue
        text = block.text.replace("**", "").strip()
        if not text.lower().startswith(SIGNED_BY.lower()):
            continue
        rest = text[len(SIGNED_BY) :].strip()
        if not rest:
            # ``## Signed by:`` as a heading of its own: the signature is the
            # first thing under it.
            for section in sections:
                if section.name == SIGNED_BY and section.blocks:
                    body = section.blocks[0]
                    if SIGNATURE_DATE.search(body.text):
                        return []
                    return [Finding(SIGNATURE_DATE_SPLIT, SIGNED_BY, body.line, body.text)]
            return [Finding(SIGNATURE_DATE_SPLIT, SIGNED_BY, block.line, text)]
        if SIGNATURE_DATE.search(rest):
            return []
        return [Finding(SIGNATURE_DATE_SPLIT, SIGNED_BY, block.line, text)]
    return []


def _rx_findings(sections: list[Section]) -> list[Finding]:
    """The prescription table's shape, and the stop criterion in its drug row.

    The header row above the ``---`` rule is a column label rather than an item,
    so it is dropped here the way ``docx_write.table_first_cells`` drops it --
    counting it would put every such table one row ahead forever.
    """
    findings = []
    for section in sections:
        if section.name != RX:
            continue
        for block in section.blocks:
            if block.kind != "table":
                continue
            rows = block.rows[1:]
            shape = tuple(len(row) for row in rows)
            if shape != RX_ROW_CELLS:
                findings.append(
                    Finding(
                        RX_TABLE_SHAPE,
                        section.name,
                        block.line,
                        "rows {r}, cells per row {s}".format(r=len(rows), s=list(shape)),
                    )
                )
                continue
            # **One cell is read as one order, and a welded second drug is not
            # reached.** `doxycycline ... x 7 days and metronidazole ... TID`
            # carries an endpoint, so the row is discharged for a second drug
            # that states none. That is
            # [#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300)'s
            # hole arriving in a second tool; declared in ``NOT_REACHED`` above
            # rather than guessed at, because splitting an order on ``and`` would
            # cut `metronidazole 500 mg PO TID and continue until the abscess
            # resolves` in half and fire this row on the first half -- a false
            # alarm on a correct order, which is #215's outcome.
            #
            # **The counterexample this comment cited until 2026-08-20 did not
            # demonstrate that**, and it was found by running the string rather
            # than by reading it: `metronidazole 500 mg PO TID and hold if the
            # creatinine rises` states no endpoint this row recognizes, so it
            # fires **whole**, and splitting it changes the verdict not at all.
            # ``test_case_study_scan.SplittingADrugRowOnAndIsRefusedHere`` runs
            # both directions now, in this module's own suite, because a comment
            # fails nothing and a measurement in a sibling's suite is not one a
            # ``case_study_scan`` author runs.
            #
            # **Ruled a reading on 2026-08-20 and this row is untouched**:
            # ``skills/practicum-case-study/SKILL.md`` step 9's ``the Rx blocks``
            # row asks a reader for the welded row.
            order = rows[RX_DRUG_ROW][0]
            if RECURRING.search(order) and not ENDPOINT.search(order):
                findings.append(Finding(NO_STOP_CRITERION, section.name, block.line, order))
    return findings


def findings(sections: list[Section], every: list) -> list[Finding]:
    """Every row, sorted by ``KINDS``.

    Sorted rather than appended in call order, on ``reference_scan.py``'s
    arrangement: which helper a row lives in is then invisible to the report, and
    the seam between them can move without a test noticing.
    """
    found = (
        _bullet_findings(sections, every)
        + _intake_findings(sections)
        + _closer_findings(sections)
        + _scaffolding_findings(sections, every)
        + _bold_findings(sections)
        + _signature_findings(sections, every)
        + _rx_findings(sections)
    )
    order = {kind: index for index, kind in enumerate(KINDS)}
    return sorted(found, key=lambda f: (order[f.kind], f.line))


def numbering_advisories(sections: list[Section]) -> tuple[int, int]:
    """Count authored top-level sequences that deserve a reader's attention.

    Neither count is a defect. A section may intentionally continue an earlier
    list above 1. A drafted 1 starts a new sequence and is not a broken
    transition. Nested items use their own level and do not participate.
    """
    not_opening_at_one = 0
    all_ordinals = []
    for section in sections:
        ordinals = [
            block.ordinal
            for block in section.blocks
            if block.kind == "numbered" and block.level == 0
        ]
        if not ordinals:
            continue
        if ordinals[0] != 1:
            not_opening_at_one += 1
        all_ordinals.extend(ordinals)
    broken_transitions = sum(
        following not in (1, current + 1)
        for current, following in zip(all_ordinals, all_ordinals[1:])
    )
    return not_opening_at_one, broken_transitions


def survey(markdown: str, skill_text: str | None) -> Scan:
    sections, every = read_sections(markdown)
    not_opening_at_one, broken_transitions = numbering_advisories(sections)
    return Scan(
        findings=findings(sections, every),
        sections=len(sections),
        intake_sections=len([s for s in sections if s.name in INTAKE_SECTIONS]),
        tables=len([b for b in every if b.kind == "table"]),
        em_dashes=sum(block.text.count(EM_DASH) for block in every)
        + sum(block_text(b).count(EM_DASH) for b in every if b.kind == "table"),
        numbered_sections_not_opening_at_one=not_opening_at_one,
        broken_numbered_transitions=broken_transitions,
        no_section=not sections,
        skeleton_disagreement=check_skeleton(skill_text) if skill_text is not None else [],
        skeleton_unread=skill_text is None,
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = ["== case study house style", "   {s}".format(s=source), ""]
    lines.append("sections read                        {n}".format(n=scan.sections))
    lines.append("  of them intake subsections         {n}".format(n=scan.intake_sections))
    lines.append("tables                               {n}".format(n=scan.tables))
    lines.append(
        "em dashes  COUNTED, NEVER GRADED     {n}".format(n=scan.em_dashes)
    )
    lines.append(
        "sections not opening at 1  COUNTED, NEVER GRADED  {n}".format(
            n=scan.numbered_sections_not_opening_at_one
        )
    )
    lines.append(
        "broken numbered transitions  COUNTED, NEVER GRADED  {n}".format(
            n=scan.broken_numbered_transitions
        )
    )
    lines.append("")
    by_kind = {kind: [] for kind in KINDS}
    for finding in scan.findings:
        by_kind[finding.kind].append(finding)
    width = max(len(kind) for kind in KINDS)
    for kind in KINDS:
        hits = by_kind[kind]
        lines.append("{k}{p}  {n}".format(k=kind, p=" " * (width - len(kind)), n=len(hits)))
        if show:
            for finding in hits:
                lines.append(
                    "    line {l} in {w}: {t}".format(l=finding.line, w=finding.where, t=finding.what)
                )
        elif hits:
            lines.append("      {r}".format(r=ROWS[kind]))
    if scan.skeleton_unread:
        lines.append("")
        lines.append("SKILL.md was not read, so the skeleton this grades against is unchecked")
    for failure in scan.skeleton_disagreement:
        lines.append("")
        lines.append("SKELETON DISAGREEMENT: {f}".format(f=failure))
    if scan.no_section:
        lines.append("")
        lines.append(
            "no section this recognizes in the document -- only the rows that read the "
            "whole document could run"
        )
    if not show and scan.findings:
        lines.append("")
        lines.append("re-run with --show for the detail. THAT OUTPUT IS PHI: read it, do not paste it.")
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    name: str
    markdown: str
    skill_text: str | None


def _load(parsed: run_grader.Parsed) -> Source:
    path = Path(parsed.source)
    try:
        markdown = path.read_text(encoding="utf-8", errors="replace")
    except OSError as failure:
        raise run_grader.SourceError(
            "case_study_scan.py: cannot read {s}: {f}".format(s=parsed.source, f=failure)
        ) from failure

    try:
        skill_text = SKILL.read_text(encoding="utf-8", errors="replace")
    except OSError:
        # The grader still works out of the checkout; it says so rather than
        # reporting a check that did not run as one that passed.
        skill_text = None

    return Source(parsed.source, markdown, skill_text)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source.markdown, source.skill_text)
    return run_grader.Grade(
        scan=scan,
        source=source.name,
        findings_failed=bool(scan.findings),
        coverage_failed=scan.no_section or bool(scan.skeleton_disagreement) or scan.skeleton_unread,
    )


GRADER = run_grader.Grader(
    usage="usage: python tools/case_study_scan.py <a draft .md> [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
    parse_error=lambda message: "case_study_scan.py: {e}".format(e=message),
    allow_extra_positionals=False,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
