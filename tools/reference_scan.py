"""Grade the reference list of a finished ``practicum-case-study`` draft.

    python tools/reference_scan.py <a draft .md> --as-of <YYYY-MM-DD> [--show]

[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218) is this,
and it is the *mechanical* half of that ticket. The ticket's own third decision
asks whether the post-draft checks should be a fan-out or a tool, and answers
itself: **an agent is only needed where the check is a reading.** Differential
ordering and discriminator quality are readings and stay agents;
``skills/practicum-case-study/SKILL.md`` step 9 spawns those. A reference list
mostly is not, so it is this.

**The reason a checker exists at all is that the writer cannot see its own
reference list.** ``CLAUDE.md``'s own doctrine -- *a report by the pass that
produced it is a baseline, not a verification* -- and
[ADR 0001](../docs/adr/0001-fixture-asserts-on-named-findings.md) one level up. The
same recall that produced an entry produces the check of it, so the check has to
come from somewhere the recall does not reach. A string test is such a place.

**The rules are ``skills/_shared/reference/apa7.md``'s and this file
does not own one of them.** That sheet is checked against the *Publication Manual*;
``apa7-coverage.md`` records the item-level primary and refuting reads and binds
their verdicts to the sheet text. A row here is a second *reader* of that sheet
rather than a second copy of it.

**One line is one entry, because that is what the renderer makes.**
``docx_write.body_xml`` sets every non-blank line as its own paragraph, so a
hard-wrapped entry renders as two paragraphs and the second hangs on nothing. This
parser reads the list the way the renderer will, which is what lets a wrap be
reported as a defect rather than silently absorbed.

**That claim was published here before it was true, and it is the finding worth
keeping.** It read *exactly the way the renderer will* while this parser treated a
deeper heading as a note inside the list and ``body_xml`` ended the list on **any**
heading -- so a list split by a ``### Note`` was read as two entries and graded
clean while the renderer set the second one flush, with no indent. The silent layout
failure the heading row exists for, passing as clean, under a sentence asserting it
could not. Found by the tracker sweep on
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137), whose
subject is a generalization made from the files a pass had open, and re-derived by
rendering a document rather than by reading the renderer's source. There is a test
now that asserts the two agree on where a list ends by **running both**.

**And the heading matcher is imported from the renderer rather than restated.**
Since [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217) the
heading is what *applies* the hanging indent, centers the label and breaks the
page -- so a scanner holding its own copy of that rule could pass a document the
renderer sets wrong, which is the one failure this row exists to catch. **The
import finds the section as well as describing it**, which it did not at first:
detection was a hand-typed list of labels, and ``References and Resources`` -- which
the renderer styles on the plural's prefix match -- exited 2 as *no reference list
found* on a document whose list renders perfectly well. ``WRONG_HEADINGS`` is what
the import cannot reach: labels APA forbids that the renderer also declines, where a
list would otherwise be found by neither.

**The rows, and where each comes from.**

*The list itself, ``apa7.md`` section 1:*

- **The heading is ``References``, including for a one-entry list.** Never
  ``Works Cited``, ``Bibliography`` or ``Reference List``. The detail says whether
  the renderer would still have styled the section, because the two failures are
  not the same size: ``References Cited`` is a wrong label, and ``Reference List``
  is a wrong label **and** a reference list with no hanging indent.
- **An entry is a paragraph.** A bullet or a numbered item takes the renderer's
  list style instead of the reference style, so the indent is lost.
- **An entry carries a year element.** A line in the list with none is a
  hard-wrapped entry's second half, or prose that does not belong there.
- **Sorted is sorted**, which ``apa7.md`` section 1 says in as many words while
  retiring ``roughly alphabetical``.

*The ``a``/``b`` rule, section 3:*

- **Two entries with one author and one year take letters.**
- **The letters follow date specificity and chronology first**, then title order
  when the dates are identical, with a leading ``A``, ``An`` or ``The`` ignored;
  an explicitly numbered series retains series order.
- **Every in-text year matches its entry's year.** Section 3 rather than section 5,
  because section 3 is the one that states it: *the year-letter combination is used
  in both the in-text citation and the reference list entry, and fixing one and not
  the other is the defect.*

*Retrieval dates, section 4:*

- **A class whose ``takes_retrieval_date`` column is true takes one.**
- **A classified fixed source does not.** The command reaches only source buckets
  whose committed classifier settles the cited version's disposition. DOI presence
  alone proves neither stability nor archival status.
- **The retrieval date is on or after the exam date** under this repository's local
  submission policy. APA supplies the date's form and placement, not that deadline.
- **A date element is well formed** -- a real month, and a space after it.

*UpToDate, section 2:*

- **The database name is italicized in the entry and plain in running text.** Both
  directions, because doing it in the wrong place is the same defect wearing the
  other sign.

*Both directions of section 5:*

- **Every entry is cited in the body**, and the ruling is delete rather than cite.
- **Every citation is listed.**

*Legal reference entries, section 8:*

- **A legal entry carries the legal source name.** A section alone is
  reported as a malformed entry.
- **A supported statute or regulation resolves on its title and publication year.**
- **A supported named statute or regulation participates in ``uncited-entry``.**
  Its title and publication year are the in-text key; its code locator is not.

**What it cannot reach is ``NOT_REACHED`` below, not this paragraph.** That list
used to be written out here *and* in ``apa7.md`` section 7, and a **prose** edit to
either failed nothing --
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241), which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s
``docx_write.NOT_APPLIED`` finding arriving one artifact over. It is one object now,
and ``tools/test_reference_scan.py`` asserts the sheet names the same items in both
directions. The reasons live on the rows; what belongs here is the shape of the
answer rather than a second copy of it.

**#241 ruled the first of those rows a reading permanently rather than leaving it
open**, and the option it declined is the part worth keeping. The proposal was to
join each entry to its ``research_ledger.py`` record and read the ``SOURCE`` class
off it -- the only candidate needing no new authored data, since a record's
``REFERENCE`` field *is* the APA entry and the author-year key is already computed
on both sides. **Which classes would settle the question is
``SOURCE_CLASS_SETTLES_RETRIEVAL_DATE``'s to say and is deliberately not counted
here**; too few of them do, and a row keyed on a class that spans both answers
would fail a **correct** entry. It would also cover only entries that came from a
research claim -- never one taken from the threshold sheets, the USPSTF table or
the guideline corpus, which are struck before the fan-out and are squarely in the
class that takes no retrieval date.

**What makes that a ruling rather than a shrug is that the reading is graded.**
``skills/practicum-case-study/SKILL.md`` step 9 names the row and
``checks_ledger.EXPECTED_CHECKS`` expects it by name, so a run returning no verdict
on it fails. That is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a
written instruction cannot do is fail*, and it is the objection option 3 had to
answer before it could be closed rather than deferred. **A clean scan is still not
a checked reference list**, ``skills/practicum-case-study/SKILL.md`` step 7 says so
beside the command, and a test asserts that sentence is still there.

Three parser limits worth knowing before quoting a count. **Author matching is on
the first significant word of the entry against the first significant word of the citation** -- so two
sources whose first authors share a surname are one key here, and a citation naming
an author the entry spells differently reads as unlisted. **A parenthetical is read
as a citation when its first word looks like an author** -- a proper noun, a quoted
short title, or a lowercase name particle -- so ``(systolic, 2000 to 3000)`` is not
one and a capitalized common noun in that position still is. And **sorting compares
normalized entry elements in APA order**: punctuation and spaces inside names are
disregarded, numeric title tokens are alphabetized as words, and the date element
is replaced by its no-date/dated/in-press rank.

**Counts only by default**, on ``research_ledger.py``'s and ``block_scan.py``'s
terms and for their reason: a finished draft lives under ``output/`` and is written
about a patient. That is unchanged, and it is what makes the report the ordinary
thing to read.

**``--show`` output is safe to paste** -- ruled by the clinician on 2026-08-19,
#218's decision 1 and the last thing that ticket was open on. **This is not a
carve-out from standing rule 1; it is a statement about where the label attaches.**
``CLAUDE.md``'s subagent rule attaches PHI to the *file* a subagent read, and the
case here is different in a way that can be checked: **what the output is able to
draw from is bounded by the code rather than by anybody's care.** Every finding
detail is a reference entry, a heading, a date, or a cited author's surname and
year.

**There is exactly one aperture onto the body, and it is named here rather than
left for a reader to find.** ``UNLISTED_CITATION`` and ``INTEXT_YEAR_MISMATCH``
emit a citation key, and a key is the **first word of anything the body writes in
the shape** ``(Word, 2024)`` -- so one capitalized token of the draft's own prose
can reach the report. It is a citation author by construction, never the sentence
around it, and it is the element the ruling blesses in as many words. **The width
of that aperture is measured rather than asserted to be zero**:
``TheReportCannotCarryTheDraftsProse`` drives a marker through it and pins that
what comes out is one token and a year. Saying *the output cannot contain patient
data* without this qualification would be a claim a notch stronger than the
measurement, which is the defect this file's own header exists to warn about.

**The ruling therefore rests on a property of this module, so the property is
pinned rather than described.** ``TheReportCannotCarryTheDraftsProse`` in
``tools/test_reference_scan.py`` runs a draft whose every body line carries a
marker token through ``format_report(..., show=True)`` and asserts the marker never
appears -- and ``BODY_ROWS`` below declares the rows that read the body at all, so
a fifth one cannot arrive without firing there. Without that the ruling would erode
the first time a sixteenth row was written.

**It does not widen.** A reader spawned by ``skills/practicum-case-study/SKILL.md``
step 9 is a language model summarizing clinical prose in its own words, with no
equivalent guarantee available, so it still reports where and what is wrong rather
than the sentence. Nor does it reach ``research_ledger.py``, whose records are
claims transcribed from faculty material about a patient, nor
``checks_ledger.py``, whose records are those same readers' findings written down
-- the same prose, one file later, and
[#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240) put a
grader in front of it rather than a new ruling about it. Nor
``case_study_scan.py``, which grades the same skill's draft *body* and quotes a
sentence of it back --
[#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277), and it is
this ruling's own test being met rather than another exception: what that module
can draw from is the draft's prose, which is exactly what this one's is not. Nor
the note scanners -- ``block_scan.py``, ``specificity_scan.py``,
``differential_scan.py``, ``anchor_scan.py`` and ``filled_vitals_census.py`` all
read note text or measured values directly, and their ``--show`` output stays PHI.

**That list is the ruling's own and not a sweep of ``tools/`` for ``--show``**,
which would be wider: ``guidelines_recs.py``'s is restrained by copyright rather
than by standing rule 1, and ``phi_scan.py``'s reveals its own findings rather than
a scanned record. **And it is re-derived rather than recited** --
``TheRulingDoesNotWiden`` reads each name off the sibling's own docstring, because
an enumeration in prose that nothing checks is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

**Exit status distinguishes not having scanned from having found nothing** -- 0
clean, 1 for a violation, **2 for every way of not having scanned**: no argument,
no file, an unreadable ``--as-of``, **no reference list in the document**, and **a
reference heading with nothing under it**. Those last two are the limbs that
matter: a draft whose list was headed something this cannot recognize would
otherwise report zero defects and read as a clean list.

**A missing ``--as-of`` is exit 2 as well, and only one row needs it.** The
retrieval window is measured against the day the paper is written and never against
the clock, so a draft graded twice a year apart has to grade the same both times.
Without it that row is not applied, and a clean report would read as though it had
been. **Where a violation and a missing exam date both hold, 1 wins**, on
``differential_scan.py``'s and ``research_ledger.py``'s ordering: returning 2 would
file the strongest thing known about the draft under the weakest heading. The
banner prints either way, so the exit 1 reads as a floor.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import run_grader
from run_grader import NOT_GRADED
from discussion_artifact import (
    LETTER,
    LEGAL_CITATION,
    LEGAL_READER_MECHANISMS,
    REPUBLISHED_DATE_ELEMENT,
    LOWER,
    UPPER,
    citation_year,
    legal_citation_spans,
    legal_reference_lacks_name,
)
from docx_write import HEADING as RENDERER_MARKDOWN_HEADING
from docx_write import REFERENCE_HEADING as RENDERER_HEADING
from docx_write import blocks as renderer_blocks


@dataclass(frozen=True)
class ApaSourceClass:
    """One item of APA's Nursing Student References vocabulary."""

    item: int
    name: str
    has_form: bool
    takes_retrieval_date: bool


# A form section is ``## <n>. Reference form: <class name>``. The bind in
# ``TheNursingSourceClassTableIsBoundToTheSheet`` detects this marker and
# compares its stripped tail byte-for-byte with ``ApaSourceClass.name``.
FORM_HEADING_MARKER = "Reference form: "


# One table owns both answers. The sheet headings bind ``has_form`` in both
# directions in ``TheNursingSourceClassTableIsBoundToTheSheet``; consumers derive
# the requires-one set from the final column rather than copying it.
APA_SOURCE_CLASSES = (
    ApaSourceClass(1, "Journal article", True, False),
    ApaSourceClass(2, "Journal article with an article number", True, False),
    ApaSourceClass(3, "UpToDate article", True, True),
    ApaSourceClass(4, "Cochrane review", True, False),
    ApaSourceClass(5, "StatPearls", True, True),
    ApaSourceClass(6, "Authored or edited book", True, False),
    ApaSourceClass(7, "Chapter in an edited book", True, False),
    ApaSourceClass(8, "Report by a government agency or other group author", True, False),
    ApaSourceClass(9, "Clinical practice guideline with a group author", True, False),
    ApaSourceClass(
        10,
        "Clinical practice guideline by individual authors at a government agency, published as part of a series",
        True,
        False,
    ),
    ApaSourceClass(11, "Ethics code", True, False),
    ApaSourceClass(12, "Position statement", True, False),
    ApaSourceClass(13, "Fact sheet", True, False),
    ApaSourceClass(14, "State nursing practice act (NPA)", True, False),
    ApaSourceClass(15, "Drug information", True, False),
    ApaSourceClass(16, "Lab or diagnostic manual", True, False),
    ApaSourceClass(17, "Medical dictionary", True, False),
    ApaSourceClass(18, "Entry in a medical dictionary", True, False),
    ApaSourceClass(19, "YouTube Video", True, False),
    ApaSourceClass(20, "Podcast or podcast episode", True, False),
    ApaSourceClass(21, "Doctor of nursing practice (DNP) project", True, False),
    ApaSourceClass(22, "PowerPoint slides or lecture notes", True, False),
    ApaSourceClass(23, "Webpage on a website", True, False),
)
_APA_CLASS_BY_NAME = {item.name: item for item in APA_SOURCE_CLASSES}
RETRIEVAL_DATE_REQUIRED_CLASSES = frozenset(
    item.name for item in APA_SOURCE_CLASSES if item.takes_retrieval_date
)

COVERAGE_CLEAN = "clean"
COVERAGE_UNDECIDABLE = "undecidable"


@dataclass(frozen=True)
class ReferenceBucket:
    """Signals an entry can carry and the sheet classes those signals span."""

    name: str
    classes: tuple[str, ...]
    spans_outside_set: bool = False

    @property
    def state(self) -> str:
        if self.spans_outside_set:
            return COVERAGE_UNDECIDABLE
        forms = tuple(_APA_CLASS_BY_NAME[name].has_form for name in self.classes)
        if all(forms):
            return COVERAGE_CLEAN
        return COVERAGE_UNDECIDABLE


@dataclass(frozen=True)
class BucketCount:
    name: str
    state: str
    population: int


# The two labels APA permits, section 1. Both are matched as a whole heading here;
# the renderer is looser on the plural and this file does not copy that looseness,
# because ``References Cited`` is styled and is still the wrong label.
APA_HEADINGS = ("References",)

# Headings a document really uses for its reference list and APA forbids. This is
# how the section is *found* when the label is wrong -- without it a mislabeled
# list would read as no list at all and the scan would report nothing.
WRONG_HEADINGS = (
    "works cited",
    "works consulted",
    "bibliography",
    "reference list",
    "references cited",
    "literature cited",
    "sources",
    "citations",
)

# A date value as APA sets one. Dated works take the bare letter suffix while
# both values without a numeric year share the hyphenated suffix rule.
NONNUMERIC_DATE = r"(?:n\.d\.|in press)"
YEAR_TOKEN = r"(?:\d{4}[a-z]?|" + NONNUMERIC_DATE + r"(?:-[a-z])?)"
ENTRY_YEAR = re.compile(r"\(\s*(" + YEAR_TOKEN + r")\s*(?:,[^)]*)?\)", re.I)
LEGAL_FULL_DATE = re.compile(
    r"^(?P<title>.*\b(?:treaty|convention|agreement|protocol|charter)\b.*?)"
    r",\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},\s*(?P<year>\d{4})\.",
    re.I,
)
DATE_FREE_CONSTITUTION = re.compile(
    r"^(?:U\.S\.|[A-Z][A-Za-z. ]+)\s+Const\.\s+(?:art\.|amend\.)\s+",
)

# A parenthetical citation, and a narrative one. Both may wrap, because the corpus
# hard-wraps its prose and a long organizational author is routinely split.
#
# **The parenthetical is read in two passes rather than as one pattern**, and both
# reasons for that were found by pointing the parser at real APA shapes rather than
# at the fixtures written for it. One set of parentheses may hold several works
# separated by semicolons -- ``(Gupta & Hooton, 2025; Smith, 2021)`` -- and a single
# pattern reads only the first, so the second reads as cited nowhere. And an
# authorless work is cited by a shortened title in quotation marks, where the comma
# sits **inside** the closing quote: ``("Managing hypertension," 2024)``. Neither
# shape is exotic, and both would have reported a compliant entry as uncited.
PAREN_BLOCK = re.compile(r"\(([^()]{1,400})\)")
# A year token ends where a letter or a digit would continue it. ``\b`` is wrong
# here: ``n.d.`` ends on a period, so a word boundary after it can never hold.
YEAR_END = r"(?![A-Za-z0-9])"
CITATION_PART = re.compile(
    r"^\s*(.{1,300}?),\s*[\"'”’]?\s*("
    + REPUBLISHED_DATE_ELEMENT
    + r"|"
    + YEAR_TOKEN
    + r")"
    + YEAR_END,
    re.I | re.S,
)
# A further year of the same work, ``(Hooton, 2025a, 2025b)``. **Anchored, and
# consumed one at a time**: a free search over the remainder reads the ``1998`` in
# ``(Smith, 2021, p. 1998)`` as a second year, and the entry it invents is
# unlisted by construction.
EXTRA_YEAR = re.compile(r"^\s*,\s*(" + YEAR_TOKEN + r")" + YEAR_END, re.I)
DATE_VALUE = re.compile(r"(" + YEAR_TOKEN + r")" + YEAR_END, re.I)
EVIDENCE_COMMA_DATE = re.compile(
    r",\s*(" + REPUBLISHED_DATE_ELEMENT + r"|" + YEAR_TOKEN + r")" + YEAR_END,
    re.I,
)
DATE_SERIES = re.compile(
    r"^\s*" + YEAR_TOKEN
    + r"(?:\s*,\s*" + YEAR_TOKEN + r")*"
    + r"(?:\s*,\s*(?:pp?\.|para\.)[^()]{0,30})?\s*$",
    re.I,
)
FENCED_CODE = re.compile(r"(?ms)^(\x60\x60\x60|~~~).*?^\1[ \t]*$")
INLINE_CODE = re.compile(r"\x60+[^\x60\n]*\x60+")
NAME = r"[" + UPPER + r"](?:" + LETTER + r"|['’.\-])+"
NOT_SENTENCE_END = r"(?!(?<!v\.)(?<=[a-z’']\.)\s)"
NARRATIVE_AUTHOR_CONNECTORS = (
    "of", "for", "the", "and", "&", "on", "in", "at", r"v\."
)
NARRATIVE_AUTHOR_PHRASE = (
    NAME
    + r"(?:"
    + NOT_SENTENCE_END
    + r"\s+(?:"
    + NAME
    + r"|"
    + "|".join(NARRATIVE_AUTHOR_CONNECTORS)
    + r")){0,10}"
)
# A narrative citation's parentheses hold **the year and at most a locator**, and
# nothing else. Allowing any trailing text read ``Hypertension (2025 update)`` as a
# citation of an author named Hypertension, and invented an unlisted one.
NARRATIVE = re.compile(
    r"\b(" + NARRATIVE_AUTHOR_PHRASE + r"(?:\s+et al\.)?)"
    r"\s*\(\s*("
    + REPUBLISHED_DATE_ELEMENT
    + r"|"
    + YEAR_TOKEN
    + r")"
    + YEAR_END
    + r"(?:\s*,\s*(?:"
    + YEAR_TOKEN
    + r")"
    + YEAR_END
    + r")*"
    + r"(?:\s*,\s*(?:pp?\.|para\.)[^()]{0,30})?\s*\)"
)
CANVAS = re.compile(r"Links to an external site\.?", re.I)

# The database name as a word, never as a hostname -- ``uptodate.com`` in a URL is
# not the name being set in the entry, and matching it there would report an
# italics defect on an entry that never spells the name out. **The hostname is
# excluded by its own suffix rather than by a bare ``.``**: the name ends an APA
# element, so ``UpToDate.`` followed by ``Retrieved`` is exactly the ordinary form
# and a lookahead refusing any period read the compliant entry as no entry at all.
UPTODATE_NAME = re.compile(r"(?<![\w/\-])UpToDate(?!\w|\.[a-z]{2,})", re.I)
UPTODATE_HOST = re.compile(
    r"(?<![\w.-])(?:https?://)?(?:www\.)?uptodate\.com(?=[/:?#]|\s|$)", re.I
)
STATPEARLS_HOST = re.compile(
    r"(?<![\w.-])(?:https?://)?(?:www\.)?statpearls\.com(?=[/:?#]|\s|$)", re.I
)
COCHRANE_SIGNAL = re.compile(
    r"(?:Cochrane Database of Systematic Reviews|cochranelibrary\.com|10\.1002/14651858)",
    re.I,
)
YOUTUBE_SIGNAL = re.compile(r"(?:youtube\.com|youtu\.be)", re.I)
PODCAST_SIGNAL = re.compile(r"\[(?:Audio|Video) podcast(?: episode)?\]", re.I)
DNP_SIGNAL = re.compile(r"\[Doctor of nursing practice(?: final)? project", re.I)
SLIDES_SIGNAL = re.compile(r"\[(?:PowerPoint slides|Lecture notes)\]", re.I)
WEB_SIGNAL = re.compile(r"https?://", re.I)
# Italic, and **not bold**. ``**UpToDate**`` contains ``*UpToDate*``, so a matcher
# that only pairs the delimiters reads a bold database name as an italicized one
# and passes an entry the renderer will set in bold.
ITALIC_UPTODATE = re.compile(r"(?<!\*)\*UpToDate\*(?!\*)|(?<!_)_UpToDate_(?!_)", re.I)

DOI = re.compile(r"(?:https?://(?:dx\.)?doi\.org/|\bdoi:\s*)10\.", re.I)

RETRIEVED_ANY = re.compile(r"\bRetrieved\b", re.I)
RETRIEVED_FROM = re.compile(r"\bRetrieved\s+from\b", re.I)
RETRIEVED_DATE = re.compile(r"\bRetrieved\s+([A-Za-z]+)(\s*)(\d{1,2}),\s*(\d{4})", re.I)

MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)

# Ignored at the front of a title when the ``a``/``b`` letters are assigned,
# section 3. APA's own worked example turns on exactly this.
ARTICLES = ("a", "an", "the")
ARTICLE = re.compile(r"^(\s*[*_\"'“‘]*\s*)(?:a|an|the)\s+", re.I)

FIRST_WORD = re.compile(
    r"[*_\"'“‘]*(" + LETTER + r"(?:" + LETTER + r"|['’\-])*)"
)

# A signal phrase in front of a citation, stripped before the author is read.
# ``(e.g., Hooton, 2024)`` is ordinary APA and its first word is ``e``, so without
# this the row reports a compliant entry as cited nowhere -- exit 1 on a clean
# draft. A fixed vocabulary, on ``research_ledger.py``'s reasoning: a machine can
# only compare strings, and one outside the list is a wrong *word* a reader sees.
SIGNAL_PHRASE = re.compile(
    r"^\s*(?:e\.g\.|i\.e\.|see also|see|cf\.|as cited in|cited in|citing|reviewed in|compare)\s*,?\s+",
    re.I,
)
# Name particles that are lowercase by convention. An in-text author is otherwise a
# proper noun or a quoted title, and requiring that is what stops
# ``(systolic, 2000 to 3000)`` being read as a citation of an author named
# ``systolic``. **A capitalized common noun in that position still gets through**,
# which is the residue rather than a fix.
PARTICLES = frozenset(
    "van von de da del della di du la le ten ter bin al el dos das".split()
)

HEADING_NOT_APA = "heading-not-apa"
ENTRY_NOT_A_PARAGRAPH = "entry-not-a-paragraph"
ENTRY_HAS_NO_YEAR = "entry-has-no-year"
CANVAS_ARTIFACT = "canvas-artifact"
LIST_NOT_SORTED = "list-not-sorted"
MISSING_AB = "missing-ab"
AB_OUT_OF_TITLE_ORDER = "ab-out-of-title-order"
REQUIRES_RETRIEVAL_DATE = "requires-retrieval-date"
RETRIEVAL_DATE_ON_ARCHIVED = "retrieval-date-on-archived"
RETRIEVAL_DATE_BEFORE_EXAM = "retrieval-date-before-exam"
MALFORMED_DATE = "malformed-date"
UPTODATE_ITALICS = "uptodate-italics"
INTEXT_YEAR_MISMATCH = "intext-year-mismatch"
UNCITED_ENTRY = "uncited-entry"
UNLISTED_CITATION = "unlisted-citation"
LEGAL_REFERENCE_LACKS_NAME = "legal-reference-lacks-name"
CITATION_READER_COVERAGE = "citation-reader-coverage"
REFERENCE_BUCKETS = (
    ReferenceBucket("uptodate", ("UpToDate article",)),
    ReferenceBucket("statpearls", ("StatPearls",)),
    ReferenceBucket("legal", ("State nursing practice act (NPA)",)),
    ReferenceBucket("cochrane", ("Cochrane review",)),
    ReferenceBucket(
        "doi-work", tuple(item.name for item in APA_SOURCE_CLASSES), spans_outside_set=True
    ),
    ReferenceBucket(
        "identified-media",
        (
            "YouTube Video",
            "Podcast or podcast episode",
            "Doctor of nursing practice (DNP) project",
            "PowerPoint slides or lecture notes",
        ),
    ),
    ReferenceBucket(
        "identified-web",
        tuple(item.name for item in APA_SOURCE_CLASSES),
        spans_outside_set=True,
    ),
    ReferenceBucket(
        "unresolved", tuple(item.name for item in APA_SOURCE_CLASSES), spans_outside_set=True
    ),
)
_REFERENCE_BUCKET_BY_NAME = {bucket.name: bucket for bucket in REFERENCE_BUCKETS}

# The rows that read the draft's **body** rather than its reference list, declared
# so that a fifth one cannot arrive quietly. #218's decision 1 was ruled on a
# property of this module -- no finding detail can be a sentence of clinical prose
# -- and every row here is a row whose detail is drawn from the one region of the
# file that is clinical prose. Two of them emit a fixed string; the other two emit
# a cited author's surname and a year, which is a reference element and not a
# finding about the patient.
#
# ``TheReportCannotCarryTheDraftsProse`` in ``tools/test_reference_scan.py`` asserts
# both directions against this tuple: every row named here fires on its draft, and
# no finding marked ``where == "body"`` is missing from it. **Adding a body row
# means firing it there**, which is where the ruling gets read again.
#
# **That claim was false of the first version and the correction is the reusable
# part.** Both directions were measured against *the rows one fixture happened to
# fire*, so a fifth body row that was neither declared here nor written into that
# draft left every assertion green -- a check that could not have seen the thing it
# was named for, reading as a settled negative. The completeness half is an **AST
# walk over this module** now, on ``test_console_codec.py``'s instrument and for its
# reason: it reads every ``Finding(...)`` call carrying a literal ``"body"``,
# whether or not any draft reaches it. Found by ``/code-review`` on the branch that
# landed the ruling.
BODY_ROWS = (
    CANVAS_ARTIFACT,
    UPTODATE_ITALICS,
    INTEXT_YEAR_MISMATCH,
    UNLISTED_CITATION,
    CITATION_READER_COVERAGE,
)
NON_FINDING_BODY_ROWS = (CITATION_READER_COVERAGE,)

# Which **sheet and section** each row reads, so a reader knows where to go and
# argue with it. The sheets own the rules; this only says which one.
#
# **Not every row is ``apa7.md``'s, and the column has to say so.** The Canvas
# artifact is ``reference/style.md`` section 10 and appears nowhere in the APA
# sheet, which #218's own first comment records as an inaccuracy in the ticket
# body: *a checker built from the ticket as written would look in the wrong file
# and find nothing.* A column headed with one file name would have reproduced that.
ROWS = {
    HEADING_NOT_APA: "apa7 1",
    ENTRY_NOT_A_PARAGRAPH: "apa7 1",
    ENTRY_HAS_NO_YEAR: "apa7 1",
    CANVAS_ARTIFACT: "style 10",
    LIST_NOT_SORTED: "apa7 1",
    MISSING_AB: "apa7 3",
    AB_OUT_OF_TITLE_ORDER: "apa7 3",
    REQUIRES_RETRIEVAL_DATE: "apa7 4",
    RETRIEVAL_DATE_ON_ARCHIVED: "apa7 4",
    RETRIEVAL_DATE_BEFORE_EXAM: "apa7 4",
    MALFORMED_DATE: "apa7 4",
    UPTODATE_ITALICS: "apa7 2",
    INTEXT_YEAR_MISMATCH: "apa7 3",
    LEGAL_REFERENCE_LACKS_NAME: "apa7 8",
    UNCITED_ENTRY: "apa7 5",
    UNLISTED_CITATION: "apa7 5",
}
KINDS = tuple(ROWS)


# What a reader does because this command cannot, and
# [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) is why it is
# an object rather than a paragraph. ``apa7.md`` section 7 carried this list for a
# reader of the skill and this module's docstring carried it for a reader of the code,
# and a **prose** edit to either failed nothing -- so the reader who was misled was the
# one who checked the file nearer to hand. That is #220's finding about
# ``docx_write.NOT_APPLIED`` arriving one artifact over, and the repair is copied whole
# rather than reinvented: one object, and a test asserts the sheet names the same items
# in both directions.
#
# **The first row is what #241 was filed over, and it is ruled a reading permanently
# rather than left open.** The ticket's own option 2 was a cross-check against
# ``research_ledger.py``'s ``SOURCE`` class -- the only candidate needing no new
# authored data, since a record's ``REFERENCE`` field *is* the APA entry. Which classes
# would settle the question is ``SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`` below rather than
# a count in this comment, and the answer is that too few of them do: a row keyed on a
# class that spans both answers would fail a **correct** entry, and **a guessed answer
# here is worse than a blank one** -- ``guidelines_catalog.py --draft``'s refusal to
# derive a population, arriving at a second artifact. It would also reach only entries
# that came from a research claim, never one taken from the threshold sheets, the
# USPSTF table or the guideline corpus, which are struck before the fan-out and are
# squarely in the class that takes no retrieval date.
#
# **What makes this more than a note is that the reading is graded.**
# ``skills/practicum-case-study/SKILL.md`` step 9 names the row and
# ``checks_ledger.EXPECTED_CHECKS`` expects it, so a run that returns no verdict on that
# row fails. #214's *what a written instruction cannot do is fail*, which is the
# objection option 3 had to answer before it could be ruled rather than deferred.


# Whether knowing a ``research_ledger.py`` ``SOURCE`` class settles whether a retrieval
# date belongs. **This is #241's declined option, kept as an object rather than as a
# sentence**, because the sentence was a count -- *of the four classes only two map* --
# restated in three files with nothing re-deriving it, which is
# [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving
# inside the commit whose whole subject is a list that was copied into two. Caught by
# ``/code-review`` and by the tracker sweep independently, and the sharper form of the
# finding is theirs: that commit deliberately withheld ``len(NOT_REACHED)`` on #143's
# terms and then stated the number beside it.
#
# **The class strings are literals here and are not imported**, which is the ruling
# showing up in the dependency graph: declining option 2 means this module does not
# reach for the ledger. ADR 0110 deliberately moved the test onto the ledger's
# closed vocabulary when it admitted market evidence for a deck; the mapping remains
# a literal here so this module still does not import the ledger.
SOURCE_CLASS_SETTLES_RETRIEVAL_DATE = {
    # A journal article is archived, always. Section 4 names it outright.
    "peer-reviewed": True,
    # Section 4 names the guideline PDF outright too.
    "society guideline": True,
    # A USPSTF statement takes none; a public-health page designed to change takes one.
    "government": False,
    # UpToDate takes one and a textbook takes none, and both are this class.
    "tertiary reference": False,
    # A live listing changes and takes one; a dated vendor quote is archived and does not.
    "market source": False,
}

NOT_REACHED = (
    (
        "republished original publication date",
        "Section 31's original date element is parsed and never compared with the "
        "entry. APA's own Gilgamesh example reverses its range between the entry "
        "and citation, so joining those date elements would fail the source that defines "
        "the rule.",
    ),
    (
        "author-shaped slash span",
        "Grammar alone recognizes an author-shaped span such as (Cohort A, "
        "2013/2014), which can raise unlisted-citation even when the span is not a "
        "citation. The measured corpus supplied no such false positive.",
    ),
    (
        "unwarranted retrieval date",
        "Section 4 says a society guideline PDF, a journal article, a USPSTF statement "
        "and a textbook take no retrieval date. This refuses one only when a committed "
        "source classifier settles that the cited form is fixed. DOI presence alone is "
        "not the archive test, and an unresolved URL cannot distinguish a stable PDF "
        "from a page designed to change.",
    ),
    (
        "UpToDate last update year",
        "Section 2's date element is the topic's own last update year rather than the "
        "year it was read, and the same topic appears in one clinician's corpus under "
        "three different years. Which is which is in the companion evidence document, "
        "which this command never sees.",
    ),
    (
        "the source exists and says so",
        "Whether an entry is a real source, and whether it says what the sentence citing "
        "it says. That is "
        "[#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231) and it "
        "is answered before the draft exists rather than here: ``research_ledger.py`` "
        "grades a year an agent read off the page and a refutation a second agent "
        "returned. Neither grading module sprouts a URL fetcher: both remain offline. "
        "The research and refutation passes own their access paths, including the "
        "required Authenticated route attempt before ``paywalled`` is available. A "
        "resolving locator whose title and authors match the entry is evidence the "
        "document exists even when that route cannot reach its body.",
    ),
    (
        "legal form and authority validity",
        "The command recognizes a narrow statute/regulation subset plus date-free "
        "constitutional locators and full-date treaty forms. It does not validate cases, "
        "legislative materials, proposed rules, executive orders, patents, parallel "
        "reporters, official-version choice, state-specific form, or current legal status.",
    ),
)


def normalize(text: str) -> str:
    """NFKD-folded, mark-stripped lowercase alphanumerics, single-spaced.

    Used for ordering and for equality, never for similarity. Markdown emphasis
    falls out with the rest of the punctuation, so ``*UpToDate*`` and ``UpToDate``
    sort as one word -- which they must, since the italics are a *format* rule and
    the alphabetizing rule cannot see formatting. Combining marks are stripped
    after decomposition; this is intentionally not ``guidelines_recs.fold``, which
    deletes accented letters instead of folding them.
    """
    folded = unicodedata.normalize("NFKD", text.casefold())
    without_marks = "".join(
        character for character in folded if not unicodedata.combining(character)
    )
    return " ".join(
        "".join(character if character.isalnum() else " " for character in without_marks).split()
    )


_NUMBER_TOKEN = re.compile(r"\b\d[\d,]*\b")
_ONES = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
)
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
_SCALES = ("", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion")
_AUTHOR_ROLE = re.compile(r"\s*\([^)]*\)\.?\s*$")
_AUTHOR_USERNAME = re.compile(r"\s*\[[^]]+\]\.?\s*$")
_BIRTH_SUFFIX = re.compile(r",?\s*(Sr\.?|Jr\.?|II|III|IV|V)\.?\s*$", re.I)
_BIRTH_RANK = {"sr": "01", "jr": "02", "ii": "03", "iii": "04", "iv": "05", "v": "06"}
_MONTH_ORDER = {
    name: number
    for number, name in enumerate(
        (
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
        ),
        start=1,
    )
}
_SERIES_PART = re.compile(r"\b(?:part|volume|book)\s+(\d+|[ivx]+)\b", re.I)


def _under_thousand(value: int) -> list[str]:
    words: list[str] = []
    if value >= 100:
        words.extend((_ONES[value // 100], "hundred"))
        value %= 100
    if value >= 20:
        words.append(_TENS[value // 10])
        value %= 10
    if value:
        words.append(_ONES[value])
    return words


def numeral_words(token: str) -> str:
    """Spell a nonnegative integer for §9.49 reference-list ordering."""

    digits = token.replace(",", "")
    if not digits.isdigit():
        return token
    value = int(digits)
    if value == 0:
        return "zero"
    groups: list[str] = []
    scale = 0
    while value:
        value, group = divmod(value, 1000)
        if group:
            words = _under_thousand(group)
            if scale < len(_SCALES) and _SCALES[scale]:
                words.append(_SCALES[scale])
            elif scale >= len(_SCALES):
                return token
            groups.insert(0, " ".join(words))
        scale += 1
    return " ".join(groups)


def alphabetic_numerals(text: str) -> str:
    return _NUMBER_TOKEN.sub(lambda match: numeral_words(match.group()), text)


def ordering_text(text: str) -> str:
    """§§9.44 and 9.49 comparison with spacing and punctuation disregarded."""

    folded = unicodedata.normalize("NFKD", alphabetic_numerals(text).casefold())
    return "".join(
        character
        for character in folded
        if character.isalnum() and not unicodedata.combining(character)
    )


def author_for_ordering(text: str) -> str:
    """Remove credited roles/usernames and rank birth-order suffixes explicitly."""

    head = text.strip().rstrip(". ")
    while True:
        stripped = _AUTHOR_ROLE.sub("", head)
        if stripped == head:
            break
        head = stripped.rstrip(". ")
    if _AUTHOR_USERNAME.search(head) and _AUTHOR_USERNAME.sub("", head).strip("., "):
        head = _AUTHOR_USERNAME.sub("", head).rstrip(". ")
    suffix = _BIRTH_SUFFIX.search(head)
    if suffix is None:
        return ordering_text(head)
    token = normalize(suffix.group(1)).replace(" ", "")
    core = head[: suffix.start()]
    return f"{ordering_text(core)}birthorder{_BIRTH_RANK[token]}"


def bare_year(token: str) -> str:
    key = year_key(token)
    if re.fullmatch(r"\d{4}[a-z]", key):
        return key[:4]
    if re.fullmatch(r"(?:nd|inpress)-?[a-z]", key):
        return re.sub(r"-?[a-z]$", "", key)
    return key


def series_number(text: str) -> int | None:
    match = _SERIES_PART.search(text)
    if match is None:
        return None
    token = match.group(1).casefold()
    if token.isdigit():
        return int(token)
    values = {"i": 1, "v": 5, "x": 10}
    total = previous = 0
    for character in reversed(token):
        value = values[character]
        total += -value if value < previous else value
        previous = max(previous, value)
    return total


def without_leading_article(text: str) -> str:
    """Ignore a leading article while retaining opening quote or emphasis."""

    return ARTICLE.sub(r"\1", text, count=1)


def first_word(text: str) -> str:
    """The entry's or the citation's alphabetizing key.

    The first significant word, normalized. A leading ``a``, ``an`` or ``the`` is
    ignored while an opening quote or emphasis marker is retained. For a personal
    author the key is the surname; for an organization or an authorless work it is
    the first significant word of whatever moved to the front, which is what
    ``apa7.md`` section 1 alphabetizes by.
    """
    text = without_leading_article(text)
    match = FIRST_WORD.match(text.strip())
    return normalize(match.group(1)) if match else ""


def year_key(token: str) -> str:
    """``2019a``, ``n.d.-b`` and ``N.D.`` reduced to one comparable string."""
    return normalize(token).replace(" ", "")


def _legal_section_text(match: re.Match[str]) -> str:
    """The locator captured by the shared legal-citation grammar."""

    return (
        match.group("parenthesized_author")
        or match.group("continued_author")
        or match.group("author")
        or ""
    )


def citation_key(author: str) -> str:
    """The author key of an in-text citation, or ``""`` where it is not one.

    Two things happen here and both were found by reading real APA prose. A leading
    signal phrase is stripped, because ``(e.g., Hooton, 2024)`` alphabetizes under
    ``e`` otherwise. And what is left has to **look like an author** -- a proper
    noun, a quoted short title, or a lowercase name particle -- because the shape
    ``(<word>, <four digits>)`` is not rare in a clinical paper: without this,
    ``Range (systolic, 2000 to 3000) mL`` cites a source called ``systolic`` and the
    unlisted-citation row fires on a compliant draft.
    """
    text = SIGNAL_PHRASE.sub("", re.sub(r"\s+", " ", author)).strip()
    text = without_leading_article(text)
    match = FIRST_WORD.match(text)
    if not match:
        return ""
    word = match.group(1)
    quoted = text[: match.start(1)].strip() != ""
    if not (word[0].isupper() or quoted or word.lower() in PARTICLES):
        return ""
    return normalize(word)


@dataclass(frozen=True)
class Entry:
    """One line of the reference list, which is one rendered paragraph."""

    line: int
    text: str
    paragraph: bool

    @property
    def _year_match(self) -> re.Match[str] | None:
        return ENTRY_YEAR.search(self.text)

    @property
    def year(self) -> str:
        match = self._year_match
        if match:
            return match.group(1)
        legal_date = LEGAL_FULL_DATE.search(self.text)
        return legal_date.group("year") if legal_date else ""

    @property
    def key(self) -> str:
        return first_word(self.text)

    @property
    def _legal_match(self) -> re.Match[str] | None:
        return LEGAL_CITATION.search(self.text)

    @property
    def is_legal(self) -> bool:
        return bool(
            self._legal_match is not None
            or LEGAL_FULL_DATE.search(self.text)
            or DATE_FREE_CONSTITUTION.search(self.text)
        )

    @property
    def resolution_keys(self) -> tuple[tuple[str, str], ...]:
        """Citation-pairing keys without changing ``key``'s grouping contract."""

        keys = [(self.key, year_key(self.year))] if self.key and self.year else []
        if DATE_FREE_CONSTITUTION.search(self.text) and self.key:
            keys.append((self.key, ""))
        return tuple(dict.fromkeys(keys))

    @property
    def authors(self) -> str:
        """Everything before the year element, which is the author string section
        3's ``a``/``b`` rule is scoped to. **This is the canonical statement of
        why; the other sites point here rather than restating it.**

        **``key`` is the *first* surname and stays that way** -- it is what an
        in-text citation is matched on, where APA names one author and ``et al.``
        -- and these are two different questions. Grouping the letters on ``key``
        answered the citation-matching one: ``Hsu, K.`` and
        ``Hsu, K., & Khosropour, C.`` in one year were read as an author who had
        failed to letter two works, when APA requires neither to carry a letter
        and ``(Hsu, 2026)`` and ``(Hsu & Khosropour, 2026)`` already differ.

        **``""`` where the entry states no year**, rather than the whole entry.
        The one caller skips a yearless entry before asking, so the branch is
        unreachable today -- and falling back to the entry text would group works
        on their *titles and URLs* the moment it stopped being, which fails
        silently and in the direction that merges unlike works.

        **What this cannot reach, named rather than left to be found.** The strings
        are compared exactly after normalization, so one author written two ways --
        ``Ross, J.`` against ``Ross, J. B.`` -- splits into two groups and the row
        goes **silent** on a pair that genuinely does need letters. That is a false
        negative where the old grouping's was a false positive, and it is the safer
        of the two directions on this row: a missed letter is a defect a reader can
        still see, and a spurious one is a defect the command *told* the run to
        write. Reaching it means deciding when two author strings are one author,
        which is a reading rather than a string test.
        """
        match = self._year_match
        if match is None:
            return ""
        head = self.text[: match.start()].strip().rstrip(". ")
        while True:
            stripped = _AUTHOR_ROLE.sub("", head)
            if stripped == head:
                break
            head = stripped.rstrip(". ")
        if _AUTHOR_USERNAME.search(head) and _AUTHOR_USERNAME.sub("", head).strip("., "):
            head = _AUTHOR_USERNAME.sub("", head).rstrip(". ")
        return normalize(head)

    @property
    def citation_author(self) -> str:
        """The reference entry's first element in its in-text form."""

        match = self._year_match
        if match is None:
            return ""
        author_text = self.text[: match.start()].rstrip(". ")
        legal = LEGAL_CITATION.search(author_text)
        if legal is not None:
            return author_text[: legal.start()].rstrip("., ")
        surnames = re.findall(
            r"(?:^|(?:,\s*&?|\s+&|\s+and)\s*)(["
            + UPPER
            + r"](?:"
            + LETTER
            + r"|['’.\-])*),\s*["
            + UPPER
            + r"](?:[.\-]|\s|$)",
            author_text,
        )
        if len(surnames) == 1:
            return surnames[0]
        if len(surnames) == 2:
            return " & ".join(surnames)
        if len(surnames) > 2:
            return surnames[0] + " et al."
        return author_text

    @property
    def is_uptodate(self) -> bool:
        """The database name as a word, or its host in a URL. One property rather
        than the same disjunction written twice, once in a row and once in a count,
        where the two could come to disagree about what an UpToDate entry is."""
        return bool(UPTODATE_NAME.search(self.text) or UPTODATE_HOST.search(self.text))

    @property
    def sort_key(self) -> str:
        """What ``sorted is sorted`` compares, with the year element ranked.

        Plain normalization puts ``2019`` before ``n d``, and APA puts an undated
        work **first** among one author's entries -- so a correctly ordered list
        with an ``n.d.`` in it failed the sort row. The year is replaced by a
        four-digit rank, which sorts the way APA sorts and leaves everything else
        letter by letter.
        """
        text = without_leading_article(self.text)
        match = ENTRY_YEAR.search(text)
        if not match:
            return ordering_text(text)
        token = year_key(self.year)
        rank, letter = ("0000", token[2:]) if token.startswith("nd") else (token[:4], token[4:])
        head = author_for_ordering(text[: match.start()])
        tail = ordering_text(text[match.end() :])
        return f"{head} {rank}{letter} {tail}"

    @property
    def title(self) -> str:
        """What follows the year element, to the end of that sentence.

        Empty where the entry states no year, which is the one shape the ``a``/``b``
        rows are never asked about anyway.
        """
        match = ENTRY_YEAR.search(self.text)
        if not match:
            return ""
        rest = self.text[match.end() :].lstrip(". \t")
        head = without_leading_article(rest.split(".")[0])
        return ordering_text(head)

    @property
    def date_order(self) -> tuple[int, int, int]:
        """§9.47: year-only before fuller dates, then calendar order."""

        match = self._year_match
        if match is None:
            return (0, 0, 0)
        full = match.group(0).strip("() ")
        _year, separator, remainder = full.partition(",")
        if not separator:
            return (0, 0, 0)
        words = remainder.strip().casefold().split()
        month = _MONTH_ORDER.get(words[0].rstrip(","), 13) if words else 13
        day_match = re.search(r"\b(\d{1,2})\b", remainder)
        day = int(day_match.group(1)) if day_match else 0
        return (1, month, day)

    @property
    def series_part(self) -> int | None:
        match = self._year_match
        return series_number(self.text[match.end() :]) if match else None


def classify_entry(entry: Entry) -> ReferenceBucket:
    """Return the narrowest bucket the entry string itself can support."""

    if entry.is_uptodate:
        name = "uptodate"
    elif STATPEARLS_HOST.search(entry.text):
        name = "statpearls"
    elif entry.is_legal:
        name = "legal"
    elif COCHRANE_SIGNAL.search(entry.text):
        name = "cochrane"
    elif DOI.search(entry.text):
        name = "doi-work"
    elif any(
        signal.search(entry.text)
        for signal in (YOUTUBE_SIGNAL, PODCAST_SIGNAL, DNP_SIGNAL, SLIDES_SIGNAL)
    ):
        name = "identified-media"
    elif WEB_SIGNAL.search(entry.text):
        name = "identified-web"
    else:
        name = "unresolved"
    return _REFERENCE_BUCKET_BY_NAME[name]


def retrieval_date_disposition(bucket: ReferenceBucket) -> bool | None:
    """Return APA's answer only when the classified form settles archiving.

    ``True`` requires a retrieval date, ``False`` refuses one, and ``None`` keeps
    the semantic question with the reader. A DOI is deliberately not consulted:
    §9.16 turns on whether the cited version is archived and retrievable.
    """

    if bucket.spans_outside_set:
        return None
    answers = {
        _APA_CLASS_BY_NAME[name].takes_retrieval_date for name in bucket.classes
    }
    return answers.pop() if len(answers) == 1 else None


def summarize_buckets(
    classified: tuple[ReferenceBucket, ...],
) -> tuple[BucketCount, ...]:
    """Count one classifier result set over the declared bucket vocabulary."""

    return tuple(
        BucketCount(
            bucket.name,
            bucket.state,
            sum(found == bucket for found in classified),
        )
        for bucket in REFERENCE_BUCKETS
    )


@dataclass(frozen=True)
class Citation:
    """One in-text citation, reduced to the two things a string test can compare."""

    key: str
    year: str


@dataclass(frozen=True)
class CitationCoverage:
    """Non-grading account of which author/date split read each candidate."""

    candidates: int = 0
    evidenced: int = 0
    grammar: int = 0
    unread: int = 0
    disagreements: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Document:
    """A finished draft, split at the reference heading."""

    heading: str | None
    body: str
    entries: tuple[Entry, ...]
    citations: tuple[Citation, ...]
    citation_coverage: CitationCoverage = CitationCoverage()


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One row failed once. **Both ``where`` and ``detail`` are safe to print**,
    which is #218's decision 1 ruled on 2026-08-19 and is what ``--show`` rests on.

    *This read* ``where`` is safe to print; ``detail`` is not *until that ruling,
    and it is the sentence the ruling had to reach*: a docstring asserting the
    opposite of what the module does is this file's own worst defect class, named
    in its own header. Found by ``/code-review`` on the branch that landed the
    ruling, one screen below the paragraph announcing it.

    ``line`` is the entry this is chargeable to, or ``None`` where it is chargeable
    to no single entry -- the heading, and every row in ``BODY_ROWS``. It is what
    ``entries at fault`` counts, and it is a field rather than a prefix read back
    off ``where`` because a group row like ``list-not-sorted`` names two lines in
    its text and would otherwise be counted as a third entry.
    """

    where: str
    detail: str
    line: int | None = None


@dataclass(frozen=True)
class Scan:
    """Counts over one draft, plus the findings ``--show`` prints."""

    as_of: date | None
    heading: str | None
    entries: int
    uptodate: int
    with_doi: int
    legal: int
    citations: int
    bucket_counts: tuple[BucketCount, ...]
    undecidable_remainder: int
    counts: tuple[tuple[str, int], ...]
    entries_at_fault: int
    findings: tuple[Finding, ...]
    citation_coverage: CitationCoverage = CitationCoverage()


def _is_reference_heading(text: str) -> bool:
    """Whether this heading opens the document's reference list.

    **Anything the renderer would style is one**, which is what makes the imported
    matcher load-bearing for finding the section and not only for describing it.
    ``References and Resources`` takes the plural's prefix match, so the renderer
    hangs the list under it -- and this used to answer *no reference list found* and
    exit 2 on a document whose list renders perfectly well.

    ``WRONG_HEADINGS`` is what the import cannot reach: labels APA forbids that the
    renderer also declines to style, so a list under one of them would be found by
    neither and report nothing. ``Reference Ranges`` is in neither set, which is the
    heading the renderer's own narrowing exists for.
    """
    stripped = text.strip().strip("*_").strip()
    lowered = stripped.lower()
    return bool(RENDERER_HEADING.match(stripped)) or lowered in WRONG_HEADINGS


def _evidenced_parenthetical(
    part: str,
    entries: tuple[Entry, ...],
    body: str = "",
    start: int = 0,
) -> tuple[str, tuple[str, ...]] | None:
    """Read a parenthetical's author/date split from a reference first element."""

    for entry in entries:
        author = entry.citation_author
        key = citation_key(author)
        if not author or len(key) < 3:
            continue
        for date_match in EVIDENCE_COMMA_DATE.finditer(part):
            written = part[: date_match.start()].strip()
            first_letter = next(
                (character for character in written if character.isalpha()),
                "",
            )
            if (
                normalize(written) != normalize(author)
                or "\n" in written
                or re.search(r"(?<!v)(?<=[" + LOWER + r"’'])\.\s", written)
                or not first_letter.isupper()
                or _inside_code(body, start, start + len(part))
            ):
                continue
            dates = [date_match.group(1)]
            rest = part[date_match.end() :]
            while True:
                extra = EXTRA_YEAR.match(rest)
                if extra is None:
                    break
                dates.append(extra.group(1))
                rest = rest[extra.end() :]
            return written, tuple(dates)
    return None


def _inside_code(body: str, start: int, end: int) -> bool:
    if not body:
        return False
    return any(
        start < match.end() and match.start() < end
        for pattern in (FENCED_CODE, INLINE_CODE)
        for match in pattern.finditer(body)
    )


def _date_values(value: str) -> tuple[str, ...]:
    return tuple(match.group(1) for match in DATE_VALUE.finditer(value))


def _evidenced_narratives(
    body: str,
    entries: tuple[Entry, ...],
) -> tuple[tuple[str, tuple[str, ...], int, int], ...]:
    """Find exact reference-first-element suffixes before date parentheses."""

    found: list[tuple[str, tuple[str, ...], int, int]] = []
    seen: set[tuple[int, int, str]] = set()
    for block in PAREN_BLOCK.finditer(body):
        inside = block.group(1)
        if DATE_SERIES.fullmatch(inside) is None:
            continue
        dates = _date_values(inside)
        prefix = body[: block.start()]
        starts = [match.start() for match in re.finditer(r"\S+", prefix)]
        for entry in entries:
            author = entry.citation_author
            key = citation_key(author)
            if not author or len(key) < 3:
                continue
            normalized_author = normalize(author)
            maximum_written_tokens = len(normalized_author.split()) + 1
            for author_start in reversed(starts):
                written = prefix[author_start:].strip()
                # Moving backward can only add normalized tokens. The article rule can
                # remove at most one, so no earlier suffix can equal this author after
                # the written suffix exceeds the author's token count by one.
                if len(normalize(written).split()) > maximum_written_tokens:
                    break
                candidate = without_leading_article(written)
                if normalize(candidate) != normalized_author:
                    continue
                first_letter = next(
                    (character for character in candidate if character.isalpha()),
                    "",
                )
                if (
                    "\n" in written
                    or re.search(r"(?<!v)(?<=[" + LOWER + r"’'])\.\s", written)
                    or not first_letter.isupper()
                    or _inside_code(body, author_start, block.end())
                ):
                    break
                identity = (author_start, block.end(), key)
                if identity not in seen:
                    seen.add(identity)
                    found.append((candidate, dates, author_start, block.end()))
                break
    return tuple(found)


def citation_coverage(
    body: str,
    entries: tuple[Entry, ...] = (),
) -> CitationCoverage:
    """Account for each grammar or reference-evidenced citation candidate."""

    candidates = evidenced = unread = 0
    disagreements: list[tuple[str, str]] = []
    legal_spans = legal_citation_spans(body)
    grammar = sum(
        bool(
            match.group("parenthesized_year")
            or match.group("continued_year")
            or match.group("year")
        )
        for match in LEGAL_CITATION.finditer(body)
    )
    candidates = grammar
    narrative_evidence = _evidenced_narratives(body, entries)
    evidence_spans = tuple(
        (start, end) for _author, _dates, start, end in narrative_evidence
    )
    narrative_lines: list[str] = []
    for line in body.splitlines(keepends=True):
        if RENDERER_MARKDOWN_HEADING.match(line.strip()):
            ending = len(line) - len(line.rstrip("\r\n"))
            if ending:
                line = line[:-ending] + ";" + line[len(line) - ending + 1 :]
        narrative_lines.append(line)
    narrative_body = "".join(narrative_lines)

    for author, dates, start, end in narrative_evidence:
        candidates += len(dates)
        evidenced += len(dates)
        overlapping = next(
            (
                match
                for match in NARRATIVE.finditer(narrative_body)
                if match.start() < end and start < match.end()
            ),
            None,
        )
        if overlapping is not None:
            evidence_key = citation_key(author)
            grammar_key = citation_key(overlapping.group(1))
            if evidence_key != grammar_key:
                disagreements.append((evidence_key, grammar_key))

    for block in PAREN_BLOCK.finditer(body):
        if any(
            start <= block.start() and block.end() <= end
            for start, end in legal_spans
        ):
            continue
        offset = block.start(1)
        cursor = 0
        for part in block.group(1).split(";"):
            leading = len(part) - len(part.lstrip())
            stripped = part.strip()
            start = offset + cursor + leading
            end = start + len(stripped)
            if any(
                start < legal_end and legal_start < end
                for legal_start, legal_end in legal_spans
            ):
                cursor += len(part) + 1
                continue
            if any(s <= start and end <= e for s, e in evidence_spans):
                cursor += len(part) + 1
                continue
            evidence = _evidenced_parenthetical(stripped, entries, body, start)
            parsed = CITATION_PART.match(stripped)
            if evidence is not None:
                evidence_author, dates = evidence
                candidates += len(dates)
                evidenced += len(dates)
                if parsed is not None:
                    evidence_key = citation_key(evidence_author)
                    grammar_key = citation_key(parsed.group(1))
                    if evidence_key != grammar_key:
                        disagreements.append((evidence_key, grammar_key))
            elif parsed is not None:
                dates = [parsed.group(2)]
                rest = stripped[parsed.end() :]
                while True:
                    extra = EXTRA_YEAR.match(rest)
                    if extra is None:
                        break
                    dates.append(extra.group(1))
                    rest = rest[extra.end() :]
                candidates += len(dates)
                if citation_key(parsed.group(1)):
                    grammar += len(dates)
                else:
                    unread += len(dates)
            cursor += len(part) + 1

    for match in NARRATIVE.finditer(narrative_body):
        if any(
            start <= match.start() and match.end() <= end
            for start, end in legal_spans
        ):
            continue
        if any(start < match.end() and match.start() < end for start, end in evidence_spans):
            continue
        dates = _date_values(match.group(0)[match.start(2) - match.start() :])
        candidates += len(dates)
        if citation_key(match.group(1)):
            grammar += len(dates)
        else:
            unread += len(dates)
    return CitationCoverage(
        candidates,
        evidenced,
        grammar,
        unread,
        tuple(dict.fromkeys(disagreements)),
    )


def read_citations(
    body: str,
    entries: tuple[Entry, ...] = (),
) -> tuple[Citation, ...]:
    """Every distinct in-text citation, parenthetical and narrative.

    Deduplicated on the pair, so a source cited nine times is one key and the year
    row reports one finding rather than nine.
    """
    seen: dict[tuple[str, str], Citation] = {}
    legal_spans = legal_citation_spans(body)

    def add(author: str, token: str) -> None:
        key = citation_key(author)
        if not key:
            return
        pair = (key, year_key(citation_year(token)))
        seen.setdefault(pair, Citation(key=pair[0], year=pair[1]))

    for match in LEGAL_CITATION.finditer(body):
        token = (
            match.group("parenthesized_year")
            or match.group("continued_year")
            or match.group("year")
            or ""
        )
        pair = (normalize(_legal_section_text(match)), year_key(token))
        seen.setdefault(pair, Citation(key=pair[0], year=pair[1]))

    for block in PAREN_BLOCK.finditer(body):
        if any(
            start <= block.start() and block.end() <= end
            for start, end in legal_spans
        ):
            continue
        # One set of parentheses, several works. Splitting first is what makes the
        # second work in ``(A, 2025; B, 2021)`` visible at all.
        offset = block.start(1)
        cursor = 0
        for part in block.group(1).split(";"):
            leading = len(part) - len(part.lstrip())
            stripped = part.strip()
            start = offset + cursor + leading
            end = start + len(stripped)
            if any(
                start < legal_end and legal_start < end
                for legal_start, legal_end in legal_spans
            ):
                cursor += len(part) + 1
                continue
            evidenced = _evidenced_parenthetical(stripped, entries, body, start)
            if evidenced is not None:
                author, dates = evidenced
                for token in dates:
                    add(author, token)
                cursor += len(part) + 1
                continue
            match = CITATION_PART.match(stripped)
            if not match:
                cursor += len(part) + 1
                continue
            author = match.group(1)
            add(author, match.group(2))
            rest = stripped[match.end() :]
            while True:
                extra = EXTRA_YEAR.match(rest)
                if not extra:
                    break
                add(author, extra.group(1))
                rest = rest[extra.end() :]
            cursor += len(part) + 1
    # A rendered heading is a paragraph boundary, including when it contains a
    # citation itself. Replacing its first line-ending character with a semicolon
    # keeps all offsets stable, keeps the heading text readable, and prevents the
    # ruled narrative phrase from continuing into the following paragraph. A
    # period cannot do this because ``NAME`` deliberately admits periods.
    narrative_lines: list[str] = []
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if RENDERER_MARKDOWN_HEADING.match(stripped):
            ending = len(line) - len(line.rstrip("\r\n"))
            if ending:
                line = line[:-ending] + ";" + line[len(line) - ending + 1 :]
        narrative_lines.append(line)
    narrative_body = "".join(narrative_lines)
    evidence_narratives = _evidenced_narratives(body, entries)
    evidence_spans = tuple(
        (start, end) for _author, _dates, start, end in evidence_narratives
    )
    for author, dates, _start, _end in evidence_narratives:
        for token in dates:
            add(author, token)
    for match in NARRATIVE.finditer(narrative_body):
        if any(
            start <= match.start() and match.end() <= end
            for start, end in legal_spans
        ):
            continue
        if any(
            start < match.end() and match.start() < end
            for start, end in evidence_spans
        ):
            continue
        author = match.group(1)
        add(author, match.group(2))
        rest = match.group(0)[match.end(2) - match.start() :]
        while True:
            extra = EXTRA_YEAR.match(rest)
            if not extra:
                break
            add(author, extra.group(1))
            rest = rest[extra.end() :]
    return tuple(seen.values())


def read_document(text: str) -> Document:
    """Split a draft at its rendered reference heading and read its entries.

    ``docx_write.blocks`` is the renderer's one reading of the Markdown subset.
    Consuming it here makes the heading levels, list markers, tables, separators,
    and source line numbers the same facts the rendered document consumes. The
    reference list runs to the end of the file or to the next **rendered** heading;
    levels five and six are paragraphs because they are outside that subset.

    **This read a deeper heading as a note inside the list until the sweep on #137
    caught it**, and the divergence was the exact silent-layout failure the heading
    row exists for: the scanner read both entries and exited 0 while the renderer
    set the second one flush, with no indent. The docstring above claimed parity
    with the renderer at the time, which is what made it worth finding.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    parsed = tuple(renderer_blocks(text))
    start: int | None = None
    heading: str | None = None
    for index, block in enumerate(parsed):
        if block.kind == "heading" and _is_reference_heading(block.text):
            start, heading = index, block.text.strip().strip("*_").strip()
            break

    if start is None:
        return Document(
            heading=None,
            body=text,
            entries=(),
            citations=read_citations(text),
            citation_coverage=citation_coverage(text),
        )

    body = "\n".join(lines[: parsed[start].line - 1])
    entries: list[Entry] = []
    for block in parsed[start + 1 :]:
        if block.kind in ("blank", "separator"):
            continue
        if block.kind == "heading":
            break
        if block.kind == "table":
            # A table row is not a reference paragraph. Read the rows already
            # parsed by the renderer so the scanner grades the same structure
            # without interpreting the source block a second time.
            for row_index, row in enumerate(block.rows):
                entries.append(
                    Entry(
                        line=block.line + (0 if row_index == 0 else row_index + 1),
                        text=" | ".join(row),
                        paragraph=False,
                    )
                )
            continue
        entries.append(
            Entry(
                line=block.line,
                text=block.text,
                paragraph=block.kind == "paragraph",
            )
        )
    parsed_entries = tuple(entries)
    return Document(
        heading=heading,
        body=body,
        entries=parsed_entries,
        citations=read_citations(body, parsed_entries),
        citation_coverage=citation_coverage(body, parsed_entries),
    )


def _retrieval(entry: Entry) -> tuple[date | None, bool, bool]:
    """``(the date, an element is present, the element is malformed)``.

    ``Retrieved from`` with no date is the pre-APA-7 form. It is a missing
    retrieval date rather than a broken one, and reporting it as broken would name
    the wrong row.
    """
    if not RETRIEVED_ANY.search(entry.text):
        return None, False, False
    match = RETRIEVED_DATE.search(entry.text)
    if not match:
        return None, True, not RETRIEVED_FROM.search(entry.text)
    month = match.group(1).lower()
    if month not in MONTHS:
        return None, True, True
    # A real month with no space after it. The date still reads, so the entry has
    # its retrieval date and only the row about the date's shape fires.
    malformed = not match.group(2)
    try:
        stamp = date(int(match.group(4)), MONTHS.index(month) + 1, int(match.group(3)))
    except ValueError:
        return None, True, True
    return stamp, True, malformed


def _heading_findings(document: Document) -> list[Finding]:
    if document.heading is None or document.heading in APA_HEADINGS:
        return []
    styled = bool(RENDERER_HEADING.match(document.heading))
    detail = document.heading if styled else f"{document.heading} - the renderer applies no hanging indent"
    return [Finding(HEADING_NOT_APA, "heading", detail)]


def _entry_findings(entry: Entry, as_of: date | None) -> list[Finding]:
    found: list[Finding] = []
    where = f"entry on line {entry.line}"
    at = entry.line
    if not entry.paragraph:
        found.append(Finding(ENTRY_NOT_A_PARAGRAPH, where, entry.text, at))
    if not entry.year and not DATE_FREE_CONSTITUTION.search(entry.text):
        found.append(Finding(ENTRY_HAS_NO_YEAR, where, entry.text, at))
    if CANVAS.search(entry.text):
        found.append(Finding(CANVAS_ARTIFACT, where, entry.text, at))
    if legal_reference_lacks_name(entry.text):
        found.append(Finding(LEGAL_REFERENCE_LACKS_NAME, where, entry.text, at))

    stamp, _present, malformed = _retrieval(entry)
    if malformed:
        found.append(Finding(MALFORMED_DATE, where, entry.text, at))
    bucket = classify_entry(entry)
    retrieval_disposition = retrieval_date_disposition(bucket)
    if retrieval_disposition is True and stamp is None:
        found.append(Finding(REQUIRES_RETRIEVAL_DATE, where, entry.text, at))
    if entry.is_uptodate and UPTODATE_NAME.search(entry.text) and not ITALIC_UPTODATE.search(entry.text):
        found.append(
            Finding(UPTODATE_ITALICS, where, "the database name is not italicized in the entry", at)
        )
    if stamp is not None and retrieval_disposition is False:
        found.append(Finding(RETRIEVAL_DATE_ON_ARCHIVED, where, entry.text, at))
    if stamp is not None and as_of is not None and stamp < as_of:
        found.append(
            Finding(
                RETRIEVAL_DATE_BEFORE_EXAM,
                where,
                f"{stamp.isoformat()} is before {as_of.isoformat()}",
                at,
            )
        )
    return found


def _order_findings(entries: tuple[Entry, ...]) -> list[Finding]:
    found: list[Finding] = []
    for earlier, later in zip(entries, entries[1:]):
        if later.sort_key < earlier.sort_key:
            # Charged to the later entry, which is the one out of place. Charging
            # it to the pair would make one row count as an entry of its own.
            found.append(
                Finding(
                    LIST_NOT_SORTED,
                    f"entries on lines {earlier.line} and {later.line}",
                    later.text,
                    later.line,
                )
            )
    return found


def _disambiguation_findings(entries: tuple[Entry, ...]) -> list[Finding]:
    """The two ``a``/``b`` rows, section 3.

    Grouped on the **full author string** and the bare year, so the undisambiguated
    and the disambiguated halves of one author-year fall in the same group and the
    two rows below never both fire on it.

    **The author string and not ``Entry.key``, which is the first surname alone**
    -- ``Entry.authors`` carries the reasoning. The detail still prints the first
    surname, which is the shape the row has always printed and is what section 5's
    rows print too.
    """
    found: list[Finding] = []
    groups: dict[tuple[str, str], list[Entry]] = {}
    for entry in entries:
        if not entry.year:
            continue
        bare = bare_year(entry.year)
        groups.setdefault((entry.authors, bare), []).append(entry)

    for (_authors, bare), members in groups.items():
        if len(members) < 2:
            continue
        lettered = [e for e in members if year_key(e.year) != bare]
        if len(lettered) < len(members):
            found.append(
                Finding(
                    MISSING_AB,
                    f"{len(members)} entries, lines {members[0].line} onward",
                    f"{members[0].key} {bare}",
                    members[0].line,
                )
            )
            continue
        ordered = sorted(lettered, key=lambda e: year_key(e.year))
        date_orders = [entry.date_order for entry in ordered]
        parts = [entry.series_part for entry in ordered]
        titles = [entry.title for entry in ordered]
        if len(set(date_orders)) > 1:
            assignment_is_wrong = date_orders != sorted(date_orders)
        elif all(part is not None for part in parts) and len(set(parts)) == len(parts):
            assignment_is_wrong = parts != sorted(parts)
        else:
            assignment_is_wrong = bool(all(titles) and titles != sorted(titles))
        if assignment_is_wrong:
            found.append(
                Finding(
                    AB_OUT_OF_TITLE_ORDER,
                    f"{len(ordered)} entries, lines {ordered[0].line} onward",
                    " | ".join(f"{e.year} {e.title}" for e in ordered),
                    ordered[0].line,
                )
            )
    return found


def _citation_findings(document: Document) -> list[Finding]:
    """Both directions of section 5, plus the year the two have to agree on."""
    found: list[Finding] = []
    listed: dict[str, set[str]] = {}
    for entry in document.entries:
        for key, year in entry.resolution_keys:
            listed.setdefault(key, set()).add(year)
    cited = {citation.key for citation in document.citations}

    for citation in document.citations:
        if citation.key not in listed:
            found.append(Finding(UNLISTED_CITATION, "body", f"{citation.key} {citation.year}"))
        elif citation.year not in listed[citation.key]:
            found.append(
                Finding(
                    INTEXT_YEAR_MISMATCH,
                    "body",
                    f"{citation.key} cited as {citation.year}, listed as {'/'.join(sorted(listed[citation.key]))}",
                )
            )
    for entry in document.entries:
        entry_cited = any(key in cited for key, _year in entry.resolution_keys)
        if (
            entry.year
            and not (entry.is_legal and not entry.key)
            and (not entry.key or not entry_cited)
        ):
            found.append(Finding(UNCITED_ENTRY, f"entry on line {entry.line}", entry.text, entry.line))
    return found


def findings(document: Document, as_of: date | None) -> list[Finding]:
    """Every row this draft's reference list fails, in report order.

    ``as_of`` of ``None`` means no exam date was given, so the retrieval window is
    not applied and every other row still runs -- ``research_ledger.py``'s
    arrangement for its own dateless ledger.
    """
    found = _heading_findings(document)
    if CANVAS.search(document.body):
        found.append(Finding(CANVAS_ARTIFACT, "body", "Links to an external site."))
    if ITALIC_UPTODATE.search(document.body):
        found.append(Finding(UPTODATE_ITALICS, "body", "the database name is italicized in running text"))
    for entry in document.entries:
        found.extend(_entry_findings(entry, as_of))
    found.extend(_order_findings(document.entries))
    found.extend(_disambiguation_findings(document.entries))
    found.extend(_citation_findings(document))
    order = {kind: index for index, kind in enumerate(KINDS)}
    return sorted(found, key=lambda f: order[f.kind])


def survey(document: Document, as_of: date | None) -> Scan:
    """Count across one draft. Takes a parsed document rather than a path, so the
    counts carry no provenance of their own -- the file's **name** is printed by
    ``format_report`` the way every sibling prints a run directory's."""
    found = findings(document, as_of)
    at_fault = {f.line for f in found if f.line is not None}
    classified = tuple((entry, classify_entry(entry)) for entry in document.entries)
    bucket_counts = summarize_buckets(tuple(bucket for _, bucket in classified))
    return Scan(
        as_of=as_of,
        heading=document.heading,
        entries=len(document.entries),
        uptodate=sum(1 for e in document.entries if e.is_uptodate),
        with_doi=sum(1 for e in document.entries if DOI.search(e.text)),
        legal=sum(1 for e in document.entries if e.is_legal),
        citations=len(document.citations),
        citation_coverage=document.citation_coverage,
        bucket_counts=bucket_counts,
        undecidable_remainder=sum(
            count.population
            for count in bucket_counts
            if count.state == COVERAGE_UNDECIDABLE
        ),
        counts=tuple((kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS),
        entries_at_fault=len(at_fault),
        findings=tuple(found),
    )


def legal_reader_covered() -> str:
    """State the derived composition of the narrow code-section recognizer."""

    return (
        f"code-section recognizer coverage: {len(LEGAL_READER_MECHANISMS)} mechanisms -- "
        + ", ".join(description for _pattern, description in LEGAL_READER_MECHANISMS)
        + "."
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no entry text unless ``show``."""
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console where anything outside cp1252 reads like corruption in the
    # one output meant to be pasted.
    lines = [
        f"reference list in {source}, exam date {scan.as_of.isoformat()}"
        if scan.as_of
        else f"reference list in {source}, NO EXAM DATE - the retrieval window was {NOT_GRADED}",
        "",
        f"  reference entries read           {scan.entries}",
        f"    UpToDate entries               {scan.uptodate}",
        f"    entries carrying a DOI         {scan.with_doi}",
        f"    recognized legal-form entries  {scan.legal}",
        f"  in-text citations read           {scan.citations}",
        (
            "  citation reader coverage         "
            f"candidates {scan.citation_coverage.candidates}; "
            f"evidence {scan.citation_coverage.evidenced}; "
            f"grammar {scan.citation_coverage.grammar}; "
            f"unread {scan.citation_coverage.unread}; "
            f"key disagreement {len(scan.citation_coverage.disagreements)}"
        ),
        "",
        "  source-class coverage (advisory)",
    ]
    for count in scan.bucket_counts:
        lines.append(
            f"    {count.name:<22} {count.state:<11} {count.population}"
        )
    lines += [
        f"  {'undecidable remainder':<34} {scan.undecidable_remainder}",
        "",
        "  A supported named statute or regulation participates in uncited-entry by title and year.",
        f"  {legal_reader_covered()}",
        "",
    ]
    for kind, count in scan.counts:
        lines.append(f"  {ROWS[kind]:<9} {kind:<28} {count}")
    lines.append("")
    lines.append(f"  entries at fault                 {scan.entries_at_fault}")
    if show:
        if scan.citation_coverage.disagreements:
            lines += ["", "  citation key disagreements (safe to paste):"]
            for evidenced, grammar in scan.citation_coverage.disagreements:
                lines.append(f"    evidence {evidenced} | grammar {grammar}")
        lines += ["", "  findings (safe to paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<28} {finding.where}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    path: Path
    document: Document
    as_of: date | None


def _load(parsed: run_grader.Parsed) -> Source:
    as_of_text = parsed.value("--as-of")
    as_of: date | None = None
    if as_of_text is not None:
        try:
            as_of = date.fromisoformat(as_of_text)
        except ValueError:
            raise run_grader.SourceError(
                f"--as-of takes a YYYY-MM-DD exam date, not {as_of_text!r}"
            ) from None
    path = Path(parsed.source)
    # The name, never the path: a draft sits under ``output/`` and its path names
    # the case and often the patient.
    if not path.is_file():
        raise run_grader.SourceError(f"no draft named {path.name}")
    document = read_document(path.read_text(encoding="utf-8", errors="replace"))
    return Source(path, document, as_of)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source.document, source.as_of)
    diagnostics: list[str] = []
    if source.document.heading is None:
        diagnostics.append(f"no reference list found in {source.path.name}")
    elif not source.document.entries:
        diagnostics.append(f"no entries under the reference heading in {source.path.name}")
    if source.as_of is None:
        diagnostics.append(
            f"{source.path.name} was scanned with no --as-of <YYYY-MM-DD> exam date, so no"
            " retrieval date in it was measured against the day the paper is written."
        )
    if scan.findings:
        diagnostics.append(
            f"{len(scan.findings)} reference defect(s) against"
            " skills/_shared/reference/apa7.md."
            " Re-run with --show to see which."
        )
    return run_grader.Grade(
        scan=scan,
        source=source.path.name,
        findings_failed=bool(scan.findings),
        coverage_failed=source.as_of is None or not source.document.entries,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage="usage: reference_scan.py <a draft .md> --as-of <YYYY-MM-DD> [--show]",
    options=(
        run_grader.Option("--show"),
        run_grader.Option(
            "--as-of",
            takes_value=True,
            missing_value="--as-of takes a YYYY-MM-DD exam date after it",
        ),
    ),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
