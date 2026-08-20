"""Turn the USPSTF half of the guideline corpus into a committed Markdown table.

USPSTF is 90 of the 179 source PDFs and is the only society in the corpus that is
already effectively a database: every recommendation statement carries a subject, a
population, a letter grade and often a screening interval, in a fixed structure. So this
half needs no retrieval -- it collapses into a few hundred table rows, which is what this
builder emits to ``reference/guidelines-uspstf.md``.

USPSTF recommendation statements are federal work and public domain, so unlike the
society documents their content may be committed in full. Issue #82.

Maintainer-only, like ``tools/icd10_build.py``: it takes #80's extracted directory as a
positional argument and is run once per corpus refresh. Nothing a consumer runs imports
it, and the committed Markdown is the whole deliverable.

**It is stdlib-only and opens no PDF.** #80 owns PDF decoding, glyph repair and
boilerplate stripping; this builder reads its per-page text and takes metadata titles
from its manifest. Three documents have no usable title on page 1, so that manifest
field is part of the handoff contract rather than optional decoration.

**Why the grade marker is the anchor.** A USPSTF document states each recommendation two
to four times -- in the structured abstract, in a summary figure, in the body -- and the
renderings differ. Anchoring on the letter grade rather than on any one section is what
makes a single rule cover the JAMA, Annals of Internal Medicine and 2000s-era AHRQ
layouts all at once, and it is why a document that changes its section headings still
parses.

**What this does not do.** It does not read the recommendation; it transcribes it. The
``population`` and ``interval`` columns are *derived from the statement text by the rules
below*, not quoted from a field the document declares, and where the rules find nothing
the cell says so rather than guessing. Every row carries ``filename`` and ``page`` so a
grade can be checked against the source in one jump, and that jump is the check -- the
table is an index into the corpus, not a substitute for it.

Usage::

    python tools/uspstf_table.py "C:/codeing/guidelines-text"
    python tools/uspstf_table.py "C:/codeing/guidelines-text" --out reference/guidelines-uspstf.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from console_codec import use_utf8
from guidelines_index import read_extracted_corpus

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "reference" / "guidelines-uspstf.md"

# The five USPSTF grades. Nothing else is a grade, and a sixth letter is a parse bug
# rather than a new category, so it raises instead of reaching the table.
GRADES = ("A", "B", "C", "D", "I")

NOT_STATED = "not stated"


# --------------------------------------------------------------------------------------
# Grade markers
#
# Three surface forms, all three live in the corpus:
#   "(B recommendation)" / "(I statement)" / "(Grade D recommendation)"  -- parenthetical
#   a bare "B recommendation" alone on a line                            -- summary figures
#   "This is a grade D recommendation." / "A recommendation."            -- 2000s AHRQ prose
#
# All three capture *any* letter rather than only ABCDI, so that a sixth grade reaches
# validate_grade and fails there. Matching only the five would make the constraint a
# tautology: a bogus grade would not pass through, but it would not fail either -- the
# marker simply would not match and the recommendation would vanish unrecorded.
# Confirmed across all 90 documents to introduce no false positive.
#
# The two bare-letter forms stay uppercase-only, and that is not incidental: the article
# in "unable to make a recommendation." is a lowercase letter followed by the same word.
# --------------------------------------------------------------------------------------
MARK_PAREN = re.compile(
    r"\(\s*(?:Grade[:\s]\s*)?([A-Za-z])\s*(?:recommendation|statement)\s*\)", re.I
)
MARK_LINE = re.compile(
    r"^[ \t]*(?:Grade[:\s]\s*)?([A-Z])\s+(?:recommendation|statement)\s*\.?[ \t]*$", re.M
)
MARK_SENTENCE = re.compile(
    r"(?:This is a\s+)?[Gg]rade[:\s]\s*([A-Za-z])\s+(?:recommendation|statement)\s*\."
    r"|^[ \t]*([A-Z])\s+(?:recommendation|statement)\s*\.",
    re.M,
)

# --------------------------------------------------------------------------------------
# Region labels
# --------------------------------------------------------------------------------------

# The structured-abstract recommendation field. JAMA sets the label in caps; Annals of
# Internal Medicine sets it in title case with a colon. JAMA also uses title case with
# two spaces after ``Conclusions and Recommendation``; #80 normalizes them to one, which
# remains safe because that branch requires the ``Conclusions`` prefix. A bare title-case
# "Recommendation" with neither is *not* matched on purpose -- it is how the cover line
# "US Preventive Services Task Force Recommendation Statement" reads, and matching it
# swallows the masthead as if it were a recommendation.
ABSTRACT_LABEL = re.compile(
    r"^[ \t]*(?:CONCLUSIONS? AND RECOMMENDATIONS?|RECOMMENDATIONS?)\s*:?[ \t]+"
    r"|^[ \t]*(?:Conclusions? and Recommendations?|Recommendations?)\s*:[ \t]*"
    r"|^[ \t]*Conclusions? and Recommendations?[ \t]+",
    re.M,
)

SUMMARY_LABEL = re.compile(
    r"^[ \t]*(?:SUMMARY OF RECOMMENDATIONS? AND EVIDENCE"
    r"|Summary of Recommendations? and Evidence"
    r"|Summary of\s*\n?[ \t]*Recommendations?)[ \t]*$",
    re.M,
)

# The journal citation ends the structured abstract and begins the marginalia.
CITATION = re.compile(
    r"^[ \t]*(?:JAMA|Ann Intern Med|Pediatrics|Am J Prev Med|Ann Fam Med)\b[^\n]*", re.M
)

SECTION_STOP = re.compile(
    r"^[ \t]*(?:Rationale|RATIONALE|Importance|IMPORTANCE|Preamble|PREAMBLE"
    r"|Practice Considerations|PRACTICE CONSIDERATIONS"
    r"|Clinical Considerations|CLINICAL CONSIDERATIONS"
    r"|Discussion|DISCUSSION|References|REFERENCES"
    r"|Other Considerations|OTHER CONSIDERATIONS"
    r"|Recommendations of Others|RECOMMENDATIONS OF OTHERS)[ \t]*$",
    re.M,
)

# A statement has to be attributable. Every real one names the Task Force or opens with
# the "The decision to ..." construction the C grade uses; a fragment that does neither is
# masthead or marginalia that landed between two markers.
STATEMENT_MUST_CONTAIN = re.compile(
    r"USPSTF|Preventive Services Task Force|The decision to", re.I
)

# ...and a statement must not cross out of its own region. USPSTF pages are two-column,
# so a region trimmed by heading still picks up the neighboring column: an all-caps
# abstract label or a numbered figure caption *inside* a statement means the text ran
# from one block into another, and what follows the next grade marker is not a
# recommendation. Two documents state one recommendation each and would otherwise state
# two. A parenthetical "(Figure 1)" is not a caption and stays.
STATEMENT_MUST_NOT_CONTAIN = re.compile(
    r"\b(?:IMPORTANCE|OBJECTIVE|POPULATION|EVIDENCE ASSESSMENT|EVIDENCE REVIEW"
    r"|CONCLUSIONS?|RECOMMENDATIONS?)\b"
    r"|\b(?:Figure|Table)\s*\d+\."
)

# A recommendation says "recommends", "concludes", or "the decision ... should be an
# individual one". The 2000s AHRQ layout prints the rationale for each recommendation
# *before* its grade, so a statement cut at the marker opens with "The USPSTF found good
# evidence that ..." and the recommendation itself is two sentences down.
RECOMMENDATION_VERB = re.compile(r"recommend|conclude|\bthe decision\b", re.I)

# ...and the same layout describes the recommendation it supersedes, in the past tense,
# with its old grade in the same parenthetical form. That is history, not a current row.
HISTORICAL_RECOMMENDATION = re.compile(r"\bIn (?:19|20)\d{2}, the USPSTF\b", re.I)

MIN_STATEMENT_CHARS = 30

# The document-level population field, used only when a statement carries no population
# phrase of its own.
DOC_POPULATION = re.compile(
    r"^[ \t]*(?:POPULATION|Population)\s*:?[ \t]+([^\n]*(?:\n(?![A-Z]{4,})[^\n]*)*)", re.M
)


# --------------------------------------------------------------------------------------
# Text normalization
# --------------------------------------------------------------------------------------

_LIGATURES = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\u00ad": "",
    "\u2019": "'",
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u00a0": " ",
}


def normalize(text: str) -> str:
    """Fold ligatures, curly quotes and dashes that survive PDF extraction.

    En dashes are folded to hyphens deliberately: they are cosmetic in a citation range
    and are *not* cosmetic in ``130-139 mmHg``, so every range in this table reads with
    one character rather than two that render differently per font. Issue #80.
    """
    for bad, good in _LIGATURES.items():
        text = text.replace(bad, good)
    # Control characters reach the text when a symbol font is used for a glyph the
    # extractor has no mapping for -- a >= in one document's POPULATION field arrives as
    # \x02. They are dropped rather than guessed at.
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


def unwrap(text: str) -> str:
    """Collapse a wrapped PDF paragraph onto one line, rejoining hyphenated breaks."""
    text = normalize(text)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    """Split on sentence ends, without splitting ``U.S. Preventive Services Task Force``.

    The lookbehind is the whole point: a period after a lone capital is an abbreviation,
    and splitting there leaves a statement beginning ``Preventive Services Task Force``.
    """
    return re.split(r"(?<!\b[A-Z]\.)(?<=[.;])\s+", text)


def spacing_ok(text: str) -> bool:
    """Is this region's text spaced, or did extraction glue the words together?

    Some USPSTF PDFs set justified body text with no space glyphs at all, so a whole
    paragraph extracts as ``TheUSPSTFrecommendsscreeningby...``. There is no way to put
    the spaces back, but the same statement is nearly always rendered cleanly somewhere
    else in the document, so this scores a region and lets a clean one win.
    """
    runs = re.findall(r"[A-Za-z]{2,}", text)
    if not runs:
        return False
    glued = sum(1 for r in runs if len(r) > 22)
    return glued / len(runs) < 0.02


# --------------------------------------------------------------------------------------
# Regions
# --------------------------------------------------------------------------------------


# Where a document may state its recommendations, best source first. The figure is last
# because its text comes out in layout order rather than reading order -- population,
# grade and statement arrive in whichever order the columns happen to sit.
REGION_ORDER = ("abstract", "summary", "figure")


@dataclass(frozen=True)
class Region:
    """A stretch of one page that may hold recommendation statements."""

    kind: str  # one of REGION_ORDER
    page: int  # 1-indexed, as printed in the table
    text: str

    @property
    def priority(self) -> int:
        return REGION_ORDER.index(self.kind)


@dataclass(frozen=True)
class Statement:
    """One recommendation as the document words it, with the grade it carries."""

    text: str
    grade: str


def candidate_regions(pages: list[str]) -> list[Region]:
    """Every place in a document where the recommendations may be stated.

    Ordered by :data:`REGION_ORDER`, so the figure is only trusted when nothing better
    yielded as many statements.
    """
    regions: list[Region] = []
    # Normalized first, because a label is separated from its text by a non-breaking
    # space in at least one document and every pattern below counts ordinary spaces.
    pages = [normalize(page) for page in pages]

    for i, page in enumerate(pages):
        match = ABSTRACT_LABEL.search(page)
        if match:
            regions.append(Region("abstract", i + 1, _region_body(page[match.end():])))
            break

    for i, page in enumerate(pages):
        match = SUMMARY_LABEL.search(page)
        if match:
            regions.append(Region("summary", i + 1, _region_body(page[match.end():])))
            break

    if pages:
        citation = CITATION.search(pages[0])
        if citation:
            regions.append(Region("figure", 1, pages[0][citation.end():]))

    return regions


def _region_body(tail: str) -> str:
    """Trim a region at the journal citation or the next section heading."""
    for pattern in (CITATION, SECTION_STOP):
        stop = pattern.search(tail)
        if stop:
            tail = tail[: stop.start()]
    return tail


def split_on_grade_markers(text: str) -> list[Statement]:
    """Split a region into statements, one per grade marker.

    The statement is everything between the previous marker and this one, which is how a
    document that states four recommendations in one paragraph yields four rows. Raises
    :class:`ValueError` on a marker carrying a letter that is not a USPSTF grade.
    """
    marks: list[tuple[int, int, str]] = []

    def add(match: re.Match, letter: str) -> None:
        if any(start <= match.start() < end for start, end, _ in marks):
            return
        marks.append((match.start(), match.end(), validate_grade(letter)))

    for m in MARK_PAREN.finditer(text):
        add(m, m.group(1))
    for m in MARK_LINE.finditer(text):
        add(m, m.group(1))
    for m in MARK_SENTENCE.finditer(text):
        add(m, m.group(1) or m.group(2))

    marks.sort()
    statements: list[Statement] = []
    cursor = 0
    for start, end, grade in marks:
        statements.append(Statement(unwrap(text[cursor:start]), grade))
        cursor = end
    return statements


def usable_statements(text: str) -> list[Statement]:
    """The output of :func:`split_on_grade_markers` that is actually recommendations."""
    kept = []
    for statement in split_on_grade_markers(text):
        if STATEMENT_MUST_NOT_CONTAIN.search(statement.text):
            continue
        text_ = trim_to_recommendation(statement.text)
        if len(text_) < MIN_STATEMENT_CHARS:
            continue
        if not STATEMENT_MUST_CONTAIN.search(text_):
            continue
        if HISTORICAL_RECOMMENDATION.search(text_):
            continue
        kept.append(Statement(text_, statement.grade))
    return kept


def trim_to_recommendation(statement: str) -> str:
    """Drop leading sentences that state evidence rather than the recommendation.

    Only leading ones. A JAMA recommendation is often two sentences -- what to screen and
    how to confirm it -- and both are the recommendation, so trimming to the *last*
    recommending sentence would throw half of it away.
    """
    sentences = split_sentences(statement)
    for i, sentence in enumerate(sentences):
        if RECOMMENDATION_VERB.search(sentence):
            return " ".join(sentences[i:]).strip()
    return statement


def choose_region(pages: list[str]) -> tuple[Region, list[Statement]] | None:
    """Pick the region that states the recommendations most completely and most cleanly.

    Most statements wins first, because a region that found three of four recommendations
    is missing one. Spacing breaks the tie ahead of priority, which is the whole point:
    when the abstract and the figure both state two recommendations and the abstract's
    words are glued together, the figure is the better transcription of the same two.
    """
    scored = []
    for region in candidate_regions(pages):
        statements = usable_statements(region.text)
        if statements:
            key = (-len(statements), 0 if spacing_ok(region.text) else 1, region.priority)
            scored.append((key, region, statements))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    _, region, statements = scored[0]
    return region, statements


# --------------------------------------------------------------------------------------
# Field derivation
# --------------------------------------------------------------------------------------


def validate_grade(letter: str) -> str:
    """Grades are A, B, C, D or I. Anything else fails rather than passing through."""
    grade = letter.strip().upper()
    if grade not in GRADES:
        raise ValueError(f"{grade!r} is not a USPSTF grade; expected one of {', '.join(GRADES)}")
    return grade


_POP_QUALIFIER = (
    r"(?:asymptomatic|nonpregnant|pregnant|postpartum|postmenopausal|community-dwelling"
    r"|sexually active|school-aged|average-risk|high-risk|increased-risk|unsensitized"
    r"|young|older|adult|adolescent|newly|all|the|primary care)"
)
_POP_NOUN = (
    r"(?:adults?|women|men|persons?|people|patients?|children|adolescents?|newborns?"
    r"|infants?|males?|females?|girls?|boys?|mothers?|adult population)"
)
# The population follows a preposition or one of the verbs a recommendation is written
# with. Requiring one of these is what keeps "the second most common cancer among all US
# women" out of a population cell.
POPULATION_PHRASE = re.compile(
    rf"\b(?:in|for|to|among"
    rf"|screening|screen|assess|counsel(?:ing)?|refer|offer|provide|prescribe|test)\s+"
    rf"(?P<phrase>(?:(?:{_POP_QUALIFIER})(?:\s*,\s*|\s+and\s+|\s+or\s+|\s+)){{0,4}}"
    rf"(?P<noun>{_POP_NOUN})\b(?P<rest>.*))$",
    re.I,
)

# Person nouns whose plural does not end in "s". Without these, a statement that ends
# "... to prevent osteoporotic fractures in men." reads as naming no population at all.
IRREGULAR_PLURALS = frozenset({"men", "women", "children", "people"})

# Trailing predicates that belong to the recommendation, not to the population. These are
# the only clause cuts made, and each one is a phrase the USPSTF reuses verbatim.
POPULATION_TAIL = re.compile(
    r" should be an individual one"
    r"| has no net benefit"
    r"| (?:is|are) small to none"
    r"| rather than routinely screening"
    r"|, the decision to",
    re.I,
)

# The population phrase runs to the end of its sentence, so the sentence has to be the
# one that states the recommendation. Two documents follow theirs with "Evidence
# indicates that the net benefit of screening all persons in this age group is small",
# whose trailing person-phrase is a comparison and not a population.
RECOMMENDING_SENTENCE = re.compile(r"USPSTF|recommend|The decision to", re.I)

# A person noun in the singular is usually an adjective on a condition rather than a
# population: "adolescent idiopathic scoliosis", "child maltreatment", "adult obesity".
# It only counts when what follows continues to describe people.
PERSON_CONTINUATION = re.compile(
    r"^(?:aged?|years?|who|whom|whose|with|without|in|of|and|or|at|population"
    r"|older|younger|\d|[,.;:])",
    re.I,
)


def derive_population(statement: str, fallback: str = "") -> str:
    """The population a statement applies to, quoted from the statement where possible.

    The rule is the trailing person-phrase: in the last sentence that states the
    recommendation, the first mention of adults, women, children and so on following a
    preposition or a recommending verb, taken to the end of that sentence.

    First rather than last, deliberately. Taking the last mention gives a shorter and
    tidier cell, and it silently drops half of "all sexually active women 24 years or
    younger and in women 25 years or older who are at increased risk" -- an incomplete
    population reads as a complete one, which is the failure a clinician cannot see. A
    phrase that runs long is visible; one that has been truncated is not.

    Where the statement names no population -- ``... of screening for AF.`` -- the
    document's own ``POPULATION`` abstract field stands in, and where there is neither the
    cell reads ``not stated`` rather than inventing one.
    """
    body = re.sub(r"\s*\([^)]*\)\s*$", "", statement.strip().rstrip("."))
    body = POPULATION_TAIL.split(body)[0]
    sentences = split_sentences(body)
    recommending = [s for s in sentences if RECOMMENDING_SENTENCE.search(s)]
    for sentence in reversed(recommending or sentences):
        phrase = _first_population(sentence)
        if phrase:
            return phrase
    if fallback:
        return fallback
    return NOT_STATED


def _first_population(sentence: str) -> str:
    """The earliest population phrase in one sentence that names people, or ``""``."""
    start = 0
    while True:
        match = POPULATION_PHRASE.search(sentence, start)
        if not match:
            return ""
        if _names_people(match.group("noun"), match.group("rest")):
            return re.sub(r"\s+", " ", match.group("phrase")).strip(" .,;")
        start = match.start() + 1


def _names_people(noun: str, rest: str) -> bool:
    """Does this noun refer to the people screened, or modify the condition screened for?

    A person noun in the singular is usually an adjective on a condition rather than a
    population -- "adolescent idiopathic scoliosis", "child maltreatment", "adult
    obesity". It counts only when what follows continues to describe people.
    """
    lowered = noun.lower()
    if lowered.endswith("s") or lowered in IRREGULAR_PLURALS:
        return True
    return bool(PERSON_CONTINUATION.match(rest.strip()))


INTERVAL_PHRASE = re.compile(
    r"\bevery \d+(?: to \d+)? (?:years?|months?|weeks?)\b"
    r"|\bbiennial(?:ly)?\b|\bannual(?:ly)?\b|\bevery year\b"
    r"|\b1-time\b|\bone-time\b|\bat least once\b|\bdaily\b"
    r"|\bperiodic(?:ally)?\b|\bat each visit\b|\brepeated\b",
    re.I,
)


def derive_interval(statement: str) -> str:
    """The screening interval named in the statement, verbatim and lowercased.

    Most USPSTF recommendations name no interval at all -- an I statement has nothing to
    space out, and a counseling recommendation is not periodic -- so ``not stated`` is the
    common and correct answer here, not a gap.
    """
    match = INTERVAL_PHRASE.search(statement)
    return match.group(0).lower() if match else NOT_STATED


# The masthead that follows the title in every layout. Spaces are optional throughout
# because four documents extract their masthead with no space glyphs at all --
# ``USPreventiveServicesTaskForceRecommendationStatement`` -- and a stop that needs the
# spaces leaves that run welded to the title.
TITLE_STOP = re.compile(
    r"U\.?\s*S\.?\s*Preventive\s*Services\s*Task\s*Force|USPSTF"
    r"|Recommendation\s*Statement|Reaffirmation"
    r"|Home\s*\|\s*JAMA|Clinical\s*Review\s*&\s*Education"
)

# Running heads that print above the title, and section headings that print in its place.
# Both have to be skipped rather than stopped at: four documents put all three running
# heads before the title, and breaking on the first one leaves no title at all.
TITLE_SKIP = re.compile(
    r"^\(Reprinted\)$|^Clinical Review & Education$|^JAMA \|"
    r"|^jama\.com$|^www\.annals\.org$|^\d+$|^(?:Copyright|©)\s*\d{4}"
    r"|^Summary of$|^Recommendations?$|^Summary of Recommendations?$"
)

# A fragment left after the masthead is cut has to be long enough to be a title. Cutting
# "The U.S. Preventive Services Task Force ..." otherwise leaves the word "The".
MIN_TITLE_FRAGMENT = 8


def derive_topic(pages: list[str], filename: str, metadata_title: str = "") -> str:
    """The document title, in three fallbacks.

    Page 1 first: the title runs from the top of the page until the Task Force masthead,
    which every layout puts directly after it. Then the PDF's own metadata title, which is
    cleaner than the page when the page has one but is missing or reads ``JAMA`` in twelve
    of the ninety documents. Then the filename, for the print-to-PDF web captures whose
    first page is browser chrome and whose metadata is the browser's -- those are named
    for their article.
    """
    title = _title_from_page(normalize(pages[0][:800]) if pages else "")
    if _looks_like_a_title(title):
        return title
    title = _clean_title(TITLE_STOP.split(normalize(metadata_title))[0])
    if _looks_like_a_title(title):
        return title
    slug = re.sub(r"[-_]+", " ", Path(filename).stem)
    return _clean_title(TITLE_STOP.split(slug)[0])


def _title_from_page(head: str) -> str:
    kept: list[str] = []
    for line in (l.strip() for l in head.splitlines()):
        if not line or TITLE_SKIP.search(line):
            continue
        cut = TITLE_STOP.split(line)[0].strip()
        if cut != line:
            # The masthead ends the title, and nothing below it is one. Collecting past
            # it is how the 2000s AHRQ layout, whose page opens with the recommendation
            # itself, ends up titled "typing and antibody testing for all pregnant women".
            if len(cut) >= MIN_TITLE_FRAGMENT:
                kept.append(cut)
            break
        kept.append(line)
        if len(kept) >= 3:
            break
    return _clean_title(" ".join(kept))


def _clean_title(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text).strip().strip(":-").strip()


def _looks_like_a_title(text: str) -> bool:
    """Is this a document title, or something that landed where one should be?

    Private-use characters are one tell: a print-to-PDF capture of a journal web page
    opens with an icon-font glyph followed by ``Metrics``, which is two words of nothing.
    Glued text is the other -- a title extracted without space glyphs is unreadable, and
    the metadata title of the same document usually is not.
    """
    if len(text) < 12 or len(text.split()) < 2:
        return False
    if re.search("[\ue000-\uf8ff]", text):
        return False
    return spacing_ok(text)


YEAR = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")


def derive_year(pages: list[str]) -> str:
    """Publication year, from the journal citation and then the online-publication line.

    The DOI is stripped before the year is looked for: ``doi:10.1001/jama.2023.5634``
    otherwise reads as the year 1001. Every citation-shaped line is checked rather
    than only the first: JAMA pages commonly open with a journal masthead before the
    structured abstract's dated citation.
    """
    evidence = pages[:3]
    for page in (normalize(p) for p in evidence):
        for citation in CITATION.finditer(page):
            year = YEAR.search(re.sub(r"doi:\S+", "", citation.group(0)))
            if year:
                return year.group(1)
    for page in evidence:
        for line in re.findall(r"(?:published online|copyright|\u00a9)[^\n]*", page, re.I):
            year = YEAR.search(re.sub(r"doi:\S+", "", line))
            if year:
                return year.group(1)
    return NOT_STATED


def document_population(pages: list[str]) -> str:
    """The document's ``POPULATION`` abstract field, if it declares one."""
    for page in (normalize(p) for p in pages[:3]):
        match = DOC_POPULATION.search(page)
        if match:
            text = unwrap(match.group(1))
            text = re.sub(
                r"^Th(?:is|e) (?:recommendation|statement)[^.]*?\bapplies to\s*", "", text
            )
            # Keep the first sentence: the field often runs on into exclusions.
            text = split_sentences(text)[0].strip().rstrip(".")
            if text:
                return text
    return ""


# --------------------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------------------


@dataclass
class Row:
    topic: str
    population: str
    grade: str
    interval: str
    year: str
    filename: str
    page: int
    statement: str = ""
    superseded_by: str = ""


@dataclass
class DocumentResult:
    filename: str
    rows: list[Row] = field(default_factory=list)
    reason: str = ""


def parse_document(
    pages: list[str],
    filename: str,
    metadata_title: str = "",
) -> DocumentResult:
    """Every recommendation row one document contributes, or why it contributed none."""
    if not pages:
        return DocumentResult(filename, reason="no extractable text")
    chosen = choose_region(pages)
    if chosen is None:
        return DocumentResult(filename, reason="no grade marker found in any recommendation region")
    region, statements = chosen
    topic = derive_topic(pages, filename, metadata_title)
    year = derive_year(pages)
    fallback = document_population(pages)
    rows = [
        Row(
            topic=topic,
            population=derive_population(statement.text, fallback),
            grade=statement.grade,
            interval=derive_interval(statement.text),
            year=year,
            filename=Path(filename).name,
            page=region.page,
            statement=statement.text,
        )
        for statement in statements
    ]
    return DocumentResult(filename, rows=rows)


def topic_key(topic: str) -> str:
    """Normalized topic, for deciding that two files cover the same subject."""
    key = topic.lower()
    key = re.sub(r"\b(?:screening|scr\.?)\s+for\s+", "", key)
    key = re.sub(r"[^a-z0-9 ]+", " ", key)
    key = re.sub(r"\b(?:in|for|of|the|a|an|and|to|with|us|u s)\b", " ", key)
    return re.sub(r"\s+", " ", key).strip()


def mark_superseded(rows: list[Row]) -> tuple[list[Row], list[str]]:
    """Where two files cover one topic, the older file's rows carry ``superseded-by``.

    Two files on one topic is the corpus holding an update and the statement it replaced.
    Dropping the older one would lose the provenance of a grade that has since changed, so
    it stays in the table and says what replaced it.

    Returns the rows and a list of topics where two files could not be ordered because one
    of them carries no year. Ordering them by guess is not available here -- an undated
    statement is not thereby the older one -- so the topic is reported instead of being
    quietly left unmarked, which would read exactly like a topic with no update at all.
    """
    by_topic: dict[str, dict[str, str]] = {}
    for row in rows:
        by_topic.setdefault(topic_key(row.topic), {})[row.filename] = row.year
    unresolved: list[str] = []
    for key, files in sorted(by_topic.items()):
        if len(files) > 1 and any(not year.isdigit() for year in files.values()):
            unresolved.append(f"{key}: " + ", ".join(sorted(files)))
    for row in rows:
        files = by_topic[topic_key(row.topic)]
        if len(files) < 2 or not row.year.isdigit():
            continue
        newer = [
            (year, name)
            for name, year in files.items()
            if name != row.filename and year.isdigit() and year > row.year
        ]
        if newer:
            row.superseded_by = max(newer)[1]
    return rows, unresolved


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------


def escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def render_row(*cells: str) -> str:
    return "| " + " | ".join(escape_cell(cell) for cell in cells) + " |"


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def render_markdown(results: list[DocumentResult]) -> str:
    rows, unresolved = mark_superseded([row for r in results for row in r.rows])
    rows.sort(key=lambda r: (r.topic.lower(), GRADES.index(r.grade), r.population.lower()))
    skipped = [r for r in results if not r.rows]

    graded: dict[str, int] = {g: 0 for g in GRADES}
    for row in rows:
        graded[row.grade] += 1

    out: list[str] = []
    out.append("# USPSTF recommendation statements")
    out.append("")
    out.append(
        f"{len(rows)} recommendation statements from {len(results) - len(skipped)} of "
        f"{len(results)} USPSTF documents in the guideline corpus, one row each. "
        "Built by `tools/uspstf_table.py`; see that module for how every column is derived. "
        "Issue #82."
    )
    out.append("")
    out.append(
        "**This is an index into the corpus, not a substitute for it.** Every row carries "
        "the source `filename` and the `page` the grade was read from, so any grade can be "
        "checked against the document in one jump — and a row that matters to a patient "
        "should be. `population` and `interval` are *derived from the statement text*, not "
        "quoted from a field the document declares; `not stated` means the rule found "
        "nothing there, which for `interval` is the ordinary case rather than a gap."
    )
    out.append("")
    out.append(
        "**USPSTF recommendation statements are federal work and public domain**, which is "
        "why this half of the corpus ships as a table of its own content while the society "
        "documents do not. The source PDFs stay outside this repo and are not redistributed."
    )
    out.append("")
    out.append("## Grades")
    out.append("")
    out.append("| Grade | Meaning | Rows |")
    out.append("| --- | --- | --- |")
    out.append(f"| A | Recommended; high certainty of substantial net benefit | {graded['A']} |")
    out.append(
        f"| B | Recommended; high certainty of moderate net benefit, or moderate certainty "
        f"of moderate to substantial net benefit | {graded['B']} |"
    )
    out.append(f"| C | Offer selectively, based on individual circumstances | {graded['C']} |")
    out.append(f"| D | Recommended against; no net benefit, or harms outweigh benefits | {graded['D']} |")
    out.append(f"| I | Evidence insufficient; benefits and harms cannot be weighed | {graded['I']} |")
    out.append("")
    out.append("## Supersession")
    out.append("")
    superseded = [row for row in rows if row.superseded_by]
    if superseded:
        out.append(
            f"{plural(len(superseded), 'row')} "
            f"{'comes' if len(superseded) == 1 else 'come'} from a file another file in "
            "the corpus has since replaced on the same topic. Superseded rows are kept "
            "rather than dropped — a grade that changed is worth being able to see change "
            "— and each names the newer file in its `Superseded by` cell."
        )
    else:
        out.append(
            "**None.** The check ran and found no topic covered by two files: the "
            f"{len(results)} documents normalize to {len({topic_key(r.topic) for r in rows})} "
            "distinct topics, which is what a download of the currently-published statements "
            "looks like. The `Superseded by` column is therefore empty throughout. It is not "
            "decoration — if a corpus refresh adds an update alongside the statement it "
            "replaces, the older file's rows will fill it in rather than quietly sitting "
            "beside the newer ones."
        )
    out.append("")
    if unresolved:
        out.append(
            f"**{plural(len(unresolved), 'topic')} could not be ordered**, because one of "
            "the files covering it carries no year. An undated statement is not thereby the "
            "older one, so neither row is marked and both are named here instead:"
        )
        out.append("")
        for topic in unresolved:
            out.append(f"- {topic}")
        out.append("")
    out.append("## Recommendations")
    out.append("")
    out.append("| Topic | Population | Grade | Interval | Year | Superseded by | File | Page |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        out.append(
            render_row(
                row.topic,
                row.population,
                row.grade,
                row.interval,
                row.year,
                row.superseded_by,
                f"`{row.filename}`",
                str(row.page),
            )
        )
    out.append("")
    out.append("## Statements")
    out.append("")
    out.append(
        "**Beyond the columns #82 asked for, and here for a reason.** `population` and "
        "`interval` are derived rather than quoted, and the source PDFs stay outside this "
        "repo and are not redistributed ([#87](https://github.com/mshamblin5150-code/"
        "clinical-skills/issues/87)) — so without the sentence each row was cut from, a "
        "reader with no copy of the corpus has no way to check a derived cell at all. "
        "These are quotations of public-domain federal text, transcribed rather than "
        "written, which is also why the American English rule reads them as reported "
        "rather than used."
    )
    out.append("")
    out.append("| Grade | Statement | File | Page |")
    out.append("| --- | --- | --- | --- |")
    for row in rows:
        out.append(render_row(row.grade, row.statement, f"`{row.filename}`", str(row.page)))
    out.append("")
    out.append("## Documents contributing no rows")
    out.append("")
    if skipped:
        out.append("| File | Reason |")
        out.append("| --- | --- |")
        for result in skipped:
            out.append(render_row(f"`{Path(result.filename).name}`", result.reason))
    else:
        out.append(f"None. All {len(results)} documents contributed at least one row.")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Extracted-corpus input
# --------------------------------------------------------------------------------------


def build(source_dir: Path) -> list[DocumentResult]:
    """Build rows from the USPSTF documents in #80's extracted corpus."""
    results = []
    for document in read_extracted_corpus(source_dir):
        if document.society != "USPSTF":
            continue
        results.append(
            parse_document(
                [page.text for page in document.pages],
                document.source,
                document.title or "",
            )
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "source", type=Path, help="directory holding #80's extracted text and manifest"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Markdown table to write (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})",
    )
    args = parser.parse_args(argv)

    if not args.source.is_dir():
        parser.error(f"no such directory: {args.source}")

    results = build(args.source)
    if not results:
        parser.error(f"no USPSTF documents found in {args.source}")

    args.out.write_text(render_markdown(results), encoding="utf-8", newline="\n")

    rows = sum(len(r.rows) for r in results)
    skipped = [r for r in results if not r.rows]
    print(f"{rows} rows from {len(results) - len(skipped)} of {len(results)} documents")
    for result in skipped:
        print(f"  no rows: {Path(result.filename).name} -- {result.reason}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    use_utf8()
    sys.exit(main())
