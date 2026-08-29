"""Extract a guideline's recommendations into machine-readable records.

    python tools/guidelines_recs.py <pdf> [--json <path>] [--show]

This is #83 gate 2's input, and it exists because of one measurement. The ticket
assumed a recommendation count could only ever be a bound -- "it over-counts by
nature, the way HEDGE does in corpus_census.py" -- and that assumption was made
against a flattened text stream. Read the same PDF's **ruled tables** instead and
the AHA/ACC 2025 hypertension guideline yields **103 numbered recommendations**,
103 unique identifiers, and **zero** rows whose Class-of-Recommendation cell fails
to parse. Measured 2026-08-16, re-derived the same day by a second reader running
this module against the PDF. An exact count can be enforced; a bound cannot, and
the difference decides whether gate 2 may refuse a commit.

**The table figure that used to sit in that sentence is gone rather than corrected
down.** It read *"in 33 tables"*; this module prints **27**, and 27 itself counts
two ``(Continued)`` continuations as separate tables, so the guideline presents 25.
Three numbers, none of them what the sentence implied, and **not one of them load
bearing** -- gate 2 keys on ``rec_id``, so the table count grades nothing. Run the
module for the figure it actually reports; a number no caller needs is a number
that goes stale unwatched, which is #143 and is how this one crossed two files and
a review before anyone re-derived it.

**Two modes, and the whole honesty of this module is in telling them apart.**
The coverage ceilings behind those modes are inventoried in ``DECLARED_LIMITS``;
this prose keeps the reasoning at the mechanism and does not stand in for that
registry.

``EXACT``
    Every row is one recommendation, the class is a cell rather than a guess, and
    the count is the count. Gate 2 may **refuse** on one.

``BOUND``
    Recommendations found by matching a marker in running text -- KDIGO's
    ``Recommendation 3.1.1`` and ``Practice Point``, ADA's ``10.5`` numbering, and
    since #173 IDSA's GRADE parenthetical. The marker also appears in tables of
    contents, in cross-references and in prose discussing **another society's**
    recommendation, so the count is an **over-report** and is labeled as one. It is
    still worth having: an over-report bounds the omission gate from the safe side,
    which is `corpus_census.py`'s ruling reused. Gate 2 may only **warn**.

**No source is silently promoted.** A document with no ruled recommendation table
comes back ``BOUND`` even if the marker count looks clean, because the thing that
makes a count exact is the table structure and not the tidiness of the answer.

**Since #173 an exact count arrives two ways, so the mode alone no longer says where
a number came from and ``counted_from`` does.** It is printed beside the mode and
written into the JSON, and it is one of three:

``ruled-table``
    A table in the document whose header row is ``COR | LOE | Recommendations``.
    AHA/ACC sets its guidelines this way, and this is what ``exact`` used to mean
    with nothing else to distinguish it from.

``curated-table``
    ``reference/guidelines-uspstf.md``, which is **also** a ruled table -- one
    recommendation per row, the grade in a cell -- and holds every recommendation
    statement in the 90 USPSTF documents, built by ``uspstf_table.py``. #173 limb 1.

``text-marker``
    The bound. Always ``BOUND``; the other two are always ``EXACT``.

**The curated limb is the one place in this module where the count is not read out
of the document in front of it, so every row is checked against the page it cites
before it is believed.** An AHA/ACC record cannot be stale -- it is read out of the
PDF as it is opened. A curated record is read out of a committed file built from a
corpus that may since have moved, which is the one objection ``exact`` does not
otherwise have to meet. A document whose rows do not check comes back as **not
scanned** rather than counted short, because a record that quietly dropped its
unverifiable rows would weaken the omission gate in the exact direction that gate
exists to cover. That check is what earns the word, and it is the answer to #173's
own prohibition: *do not promote a document to exact that is not read out of a ruled
table.*

**And the curated table is consulted first, ahead of both readings of the PDF.** The
case is real rather than defensive: a USPSTF statement quotes another society's
recommendation in GRADE terms, so reading the markers first would answer a curated
90-document society with a bound of 1 and call that a scan.

**#173 limb 2 is IDSA, and it is a bound because the strength is a sentence.** IDSA
writes *"(strong recommendation, moderate-quality evidence)"* -- newer files spell it
*"certainty of evidence"* -- and **ten** documents elide the words entirely and write
*"(strong, moderate)"*. Those are two markers rather than one alternation, because
they are two conventions and a merged pattern would report a document as using a
house style it does not.

**That ten read *three* for one merge, and how it went wrong is worth more than the
number.** It was counted over ``guidelines-text/`` -- the extracted ``.txt`` corpus,
which is **not what this module reads** -- with a hand-written pattern, and over ten
files picked because a *different* pattern had returned nothing on them. A figure
measured against the wrong input **and** over a selection, which is #137's shape and
the trap `guidelines_extract.py` records in as many words: it reads exactly like one
measured against the right input. Re-derived by running this module's own markers
over all 179 PDFs, 2026-08-19: **ten** documents carry the terse form, **none**
carries both forms, and **none of the ten is reached by any other marker here**. So
the terse limb is not a minor variant -- without it IDSA would be 20 ``bound`` and 21
counted at nothing, rather than 30 and 11. **The strength is in the parenthetical and is still not read
into ``cor``**: gate 2's class check is the one thing catching a row pinned to the
wrong recommendation, and filling it from an over-reporting marker would make that
check fire on pairings the marker invented.

**What the curated limb does not reach, named rather than left to be discovered.**
The record is only as complete as ``uspstf_table.py`` was: a graded statement its
region scoring did not pick is a recommendation gate 2 will never ask a sheet to
account for, and nothing here can see one. The ``Superseded by`` column is not read
either -- it is empty throughout today, and when a refresh fills it a superseded
recommendation will still be a row a sheet has to cite or scope out. Both are
*under*-reads of the guideline rather than over-reads of the record, so the right to
refuse stays sound; what they cost is the gate's **reach**, not its **verdict**.

**And eleven IDSA documents still come back at nothing**, because they state no
graded recommendation in either prose form this reads. That is the honest answer and
not a claim about them -- the module exits 2 and says so.

**What the second limb costs is that a marker is a marker wherever it is written.**
Two documents outside IDSA carry one GRADE parenthetical each -- a GOLD
recommendation stated that way, and a USPSTF statement quoting the American College
of Physicians -- and both are now counted. The USPSTF one is answered by the curated
table before the markers run; the GOLD one moves from *nothing counted* to a bound of
one, which is a true statement about markers and a bad description of that document.
It is a bound, the module says in as many words that a bound must not be read as a
count, and no threshold on the number would be anything but invented.

**Nothing here is PHI and standing rule 1 is not in play** -- these are published
society guidelines. Copyright is: a recommendation is the society's own expression.
So stdout prints **counts and identifiers only**, `--show` prints the text, and the
JSON is written outside every checkout on `guidelines_index.py`'s terms. Paste a
line into a ticket, never a table.

**One of the tools in ``tools/`` that is not stdlib**, because it reads a PDF:

    python -m pip install pymupdf

The import sits inside the function that opens the file, so the test suite needs
nothing installed and **nothing a consumer runs imports this at all**.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

import artifact_provenance
import guidelines_extract
from console_codec import use_utf8
from repo_root import InsideCheckout, ensure_outside_checkout

MODE_EXACT = "exact"
MODE_BOUND = "bound"
SOURCE_NOTHING_FOUND = "nothing-found"
SWEEP_MANIFEST = "manifest.json"
NOTHING_FOUND = "nothing-found"
RECOMMENDATIONS_FOUND = "recommendations-found"

# Everything this producer writes wears this prefix. The reverse remains false:
# a prefixed file need not have come from this producer, and ``recs-sweep.json``
# is the standing counter-example. ADR 0058's addenda assign #446 to build the
# whole ``DECLARED_LIMITS`` object before the other appenders; until it lands,
# this limit stays here rather than creating that object's partial predecessor.
RECS_PREFIX = "recs-"


def source_filename_matches_document(source_filename: str, document: str) -> bool:
    """Whether a source filename and a catalog/sheet document name agree."""
    built_from = Path(source_filename.strip().replace("\\", "/")).name
    expected = Path(document.strip().replace("\\", "/")).name
    if expected and Path(expected).suffix.casefold() != ".pdf":
        expected += ".pdf"
    return bool(built_from and expected and built_from.casefold() == expected.casefold())


def record_built_from_another_document(record: dict, document: str) -> str:
    """Return the record's PDF filename when it disagrees with ``document``.

    Empty means either agreement or that one side names no document, so callers
    refuse only a knowable disagreement. This deliberately reads ``source``, not
    ``doc_id``: the latter is caller-supplied free text, while ``source`` is the PDF
    path the record was built from. The comparison is on the filename because the
    corpus mount is machine-local. A threshold sheet stores a document stem while a
    catalog row stores the PDF filename, so the missing suffix is normalized here.
    """
    source = record.get("source")
    if not isinstance(source, str):
        return ""
    built_from = Path(source.replace("\\", "/")).name
    if not built_from or not document.strip():
        return ""
    return "" if source_filename_matches_document(built_from, document) else built_from


class EvidenceDisposition(Enum):
    """How a declared coverage limit can be checked."""

    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"


@dataclass(frozen=True)
class DeclaredLimit:
    """One stable name, coverage sentence, and evidence disposition."""

    key: str
    limit: str
    evidence: EvidenceDisposition


# The module docstring explains why these mechanisms exist and points here instead
# of maintaining a second inventory. The population is deliberately a floor: #589
# owns the end-to-end read of this module and its ADRs. Each later mechanism appends
# its own row rather than creating another declared-limits object.
DECLARED_LIMITS = (
    DeclaredLimit(
        "bound-count-over-reports",
        "A text-marker result can over-report incidental markers and under-report unsupported or damaged markers, so it is not an exact count.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "marker-strength-unclassified",
        "GRADE strength and certainty captured by a text marker are not assigned to the recommendation class field.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "curated-selection-floor",
        "Curated verification cannot recover a graded statement that the committed curated table omitted.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "curated-supersession-unread",
        "Curated verification does not interpret the source table's supersession metadata.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "unsupported-marker-vocabulary",
        "A document using none of the declared marker forms can return no records without establishing that it has no recommendations.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "marker-matches-anywhere",
        "Text markers match wherever they occur, including contents, cross-references, and quoted recommendations.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "unrepaired-nonmarker-limbs",
        "Curated verification and ruled-table extraction skip glyph-space reconstruction; comparison folding protects the curated limb, while ruled-table text can retain spacing damage.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "glued-run-census-floor",
        "The glued-run census sees only alphabetic runs at or above its declared length floor, so shorter welds are invisible and genuine long words are counted.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "citation-tier-zero-reader-floor",
        "Citation tier 0 cannot expose shared reconstruction errors, and it does not run at all for bound sources, which rely on tier 2 for page-text agreement.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "record-source-unreadable",
        "A recommendation record whose source is absent or unparseable matches no PDF, so a reader can neither offer it as a same-document hint nor refuse it as another document's record.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "literal-read-site-floor",
        "A read site built by indirection is invisible to a source walk keyed on the recs- filename literal.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "source-pdf-left-corpus",
        "A recommendation record whose source PDF has left the corpus cannot be rebuilt or used by the no-override drafter.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "source-pdf-verification-skipped",
        "Source-PDF digest verification does not run where the recorded corpus path is unreachable; the reader banners that skipped check.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "ownership-does-not-prove-content",
        "A trusted producer stamp establishes ownership and inputs, not that the extracted recommendation content is clinically correct.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "record-prefix-does-not-bind-source-key",
        "The producer enforces the recs- prefix, but it does not bind the remaining filename stem to a source key or document.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "registry-population-floor",
        "This registry covers the previously identified docstring ceilings and the mechanisms added with the repaired marker reader; its end-to-end module and ADR derivation remains outstanding.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "doc-id-records-escape-prefix-walk",
        "A recommendation record keyed on doc_id is invisible to a source walk keyed on the recs- filename prefix.",
        EvidenceDisposition.DECLARED_READING,
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)

# A length floor is intentionally a reporting instrument, never a gate. The limit
# it carries is the ``glued-run-census-floor`` row above, so a clean count is not a
# claim that the records contain no welded words.
GLUED_RUN_MIN_LETTERS = 26
GLUED_RUN = re.compile(rf"[A-Za-z]{{{GLUED_RUN_MIN_LETTERS},}}")

# Where a count came from, printed beside the mode and written into the JSON. The
# mode says what a gate may do with the number; this says what earned it, and #173
# is why the two are separate -- an ``exact`` count now arrives two ways.
SOURCE_RULED_TABLE = "ruled-table"
SOURCE_CURATED_TABLE = "curated-table"
SOURCE_TEXT_MARKER = "text-marker"

# The committed USPSTF recommendation table, #173 limb 1's whole input. Anchored on
# the module rather than on the working directory, on `icd10_build.py`'s terms, and
# read lazily so importing this module still needs nothing but the standard library.
REPO_ROOT = Path(__file__).resolve().parent.parent
CURATED_TABLE = REPO_ROOT / "reference" / "guidelines-uspstf.md"

# A record's ``counted_from`` limb selects the files that can change its contents.
# This is deliberately not a defaulting lookup: a legacy or foreign limb names no
# floor the clinician chose and is therefore untrusted. ADR 0030 ruling 2.
RECORD_TRUST_FLOOR = {
    SOURCE_RULED_TABLE: ("tools/guidelines_recs.py",),
    SOURCE_CURATED_TABLE: (
        "tools/guidelines_recs.py",
        "reference/guidelines-uspstf.md",
    ),
    SOURCE_TEXT_MARKER: (
        "tools/guidelines_recs.py",
        "tools/guidelines_extract.py",
    ),
    SOURCE_NOTHING_FOUND: (
        "tools/guidelines_recs.py",
        "tools/guidelines_extract.py",
        "reference/guidelines-uspstf.md",
    ),
}

SOURCE_PDF_NOT_VERIFIED = "RECOMMENDATION SOURCE PDF NOT VERIFIED"


class UntrustedRecommendationRecord(ValueError):
    """A present recommendation record whose ownership cannot be established."""

    def __init__(self, path: Path, reasons: list[str]):
        self.path = path
        self.reasons = tuple(reasons)
        super().__init__("; ".join(reasons))


def _recommendation_record(value: object, path: Path) -> dict:
    if not isinstance(value, dict) or not isinstance(value.get("recommendations"), list):
        raise ValueError(
            f"{path} holds a JSON {type(value).__name__}, not a record"
        )
    return value


def peek_recommendation_source(path: Path) -> str:
    """Return only the source PDF filename from an untrusted record.

    This is the resolver's deliberately narrow peek: selecting a candidate by its
    filename does not expose recommendation text or confer trust on the candidate.
    """
    loaded = json.loads(path.read_text(encoding="utf-8"))
    record = _recommendation_record(loaded, path)
    source = record.get("source")
    return Path(source.replace("\\", "/")).name if isinstance(source, str) else ""


def load_recommendation_record(
    path: Path,
    *,
    allow_untrusted: bool = False,
    require_source_pdf: bool = False,
) -> dict:
    """Load the selected record, enforcing its limb-specific ownership floor.

    The source PDF digest is checked when the recorded path is reachable. The sheet
    reader accepts an unreachable corpus with the same unmistakable did-not-run
    banner used by citation tier 2. ``require_source_pdf`` gives the no-override
    drafter its stricter mode: the same absence refuses instead of being bannered.
    """
    loaded = json.loads(path.read_text(encoding="utf-8"))
    record = _recommendation_record(loaded, path)
    reasons: list[str] = []
    counted_from = record.get("counted_from")
    floor = RECORD_TRUST_FLOOR.get(counted_from)
    if floor is None:
        reasons.append(
            "has absent or unrecognized counted_from"
            if counted_from is None
            else f"has unrecognized counted_from {counted_from!r}"
        )
    else:
        try:
            artifact_provenance.check_producer(
                record.get("producer"),
                path,
                allow_untrusted=allow_untrusted,
                unchanged_paths=floor,
            )
        except artifact_provenance.UntrustedProvenance as error:
            prefix = f"untrusted artifact {path}: "
            reasons.append(str(error).removeprefix(prefix))

    source = record.get("source")
    expected_sha = record.get("source_sha256")
    if not isinstance(source, str) or not source:
        reasons.append("has no source PDF path")
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        reasons.append("has no recognized source PDF sha256")
    if isinstance(source, str) and source:
        source_path = Path(source)
        if source_path.is_file():
            actual_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if isinstance(expected_sha, str) and actual_sha != expected_sha:
                reasons.append("source PDF sha256 does not match the reachable document")
        elif require_source_pdf:
            reasons.append(f"source PDF is not reachable at {source_path}")
        else:
            print(
                f"{SOURCE_PDF_NOT_VERIFIED} -- source PDF not found at {source_path}",
                file=sys.stderr,
            )

    if reasons:
        if allow_untrusted:
            artifact_provenance._trace(
                f"untrusted artifact {path}: " + "; ".join(reasons)
            )
        else:
            raise UntrustedRecommendationRecord(path, reasons)
    return record


class DidNotScan(Exception):
    """A condition under which this module has not read the document at all.

    ``guidelines_search.py``'s exit-2 convention as an exception, because the two
    conditions that raise it -- a curated table whose halves disagree, and a curated
    row that is not on the page it cites -- are both *staleness*, and reporting
    staleness as a count of zero recommendations is the one thing this module exists
    not to do.
    """

# The header row that makes a table a recommendation table. Matched on the cells
# rather than on the whole row so a trailing empty column -- which PyMuPDF emits
# for a merged title row -- does not defeat it.
#
# Both spellings appear: the AHA/ACC files write "COR" and "LOE", and the older
# ones spell the second column "LOE" too. Anything else is a data table, and a data
# table in a guideline is full of numbers that are not recommendations.
TABLE_HEADER = ("cor", "loe")

# The merged cell above the header, which names the table. This is the string a
# scoped-out recommendation is named by, so it has to survive into the record.
TABLE_TITLE = re.compile(r"^\s*Recommendations for\s+(?P<title>.+?)\s*$", re.DOTALL)

# A numbered recommendation inside such a table. The number restarts per table, so
# it is only unique alongside the page and title -- which is what `rec_id` welds.
NUMBERED = re.compile(r"^\s*(?P<number>\d+)\.\s*(?P<text>.+)$", re.DOTALL)

# A Class of Recommendation cell. The modern spelling is bare -- 1, 2a, 2b, 3 --
# and 3 carries a qualifier the older files spell out.
CLASS_CELL = re.compile(r"^\s*(?P<value>1|2a|2b|3)\b(?P<qualifier>.*)$", re.IGNORECASE | re.DOTALL)

# Text markers, for the sources that do not rule their recommendations into tables.
# Each is (society-independent name, pattern). These produce a BOUND count and the
# module says so in every place the number is printed.
TEXT_MARKERS = (
    ("recommendation", re.compile(r"\bRecommendation\s+(?P<ref>\d+(?:\.\d+)+)")),
    ("practice-point", re.compile(r"\bPractice Point\b")),
    # IDSA -- #173 limb 2. Strength and certainty are written in prose rather than
    # ruled into a table, in two renderings that are both in the corpus. They are two
    # markers rather than one alternation because they are two conventions, and a
    # merged pattern would report a document as using a house style it does not.
    #
    # ``[^)]`` matches a newline on purpose: the renderer wraps inside the
    # parenthesis -- ``(weak recommendation, low-\nquality evidence)`` is off a real
    # page -- and a pattern that could not cross the break would find nothing on the
    # documents this limb exists for.
    (
        "grade-spelled-out",
        re.compile(
            r"\((?:strong|weak|conditional)[^)]{0,120}?(?:evidence|certainty)[^)]{0,40}\)",
            re.IGNORECASE,
        ),
    ),
    # The elided rendering. Both halves are closed vocabularies and that is the whole
    # of its safety: ``strong`` is an ordinary English adjective, so a pattern that
    # accepted any following word would match prose. The four certainty words are
    # GRADE's own.
    (
        "grade-terse",
        re.compile(
            r"\((?:strong|weak|conditional)\s*,\s*(?:very low|low|moderate|high)\)",
            re.IGNORECASE,
        ),
    ),
)

_WHITESPACE = re.compile(r"\s+")


def flatten(cell: str | None) -> str:
    """A table cell as one line. PyMuPDF wraps cell text at the rendered line."""
    return _WHITESPACE.sub(" ", (cell or "").replace("\n", " ")).strip()


def is_header_row(row: list[str | None]) -> bool:
    """Whether this row is the ``COR | LOE | Recommendations`` header."""
    cells = [flatten(cell).lower() for cell in row]
    return len(cells) >= 2 and cells[0] == TABLE_HEADER[0] and cells[1] == TABLE_HEADER[1]


def table_title(row: list[str | None]) -> str | None:
    """The ``Recommendations for X`` title out of a table's merged first row.

    Returns None for any other first row, which is how a data table is rejected
    before its numbers are ever read as recommendations.

    **Only the first rendered line of the cell.** AHA/ACC sets a second line under
    most captions -- "Referenced studies that support the recommendations are
    summarized in ..." -- inside the same merged cell. Flattening the whole cell put
    that sentence into the title and therefore into every ``rec_id`` derived from
    it, which is a citation a reader has to type. Cutting at the newline is safe
    because the caption is one rendered line by construction: it is what the
    ``Recommendations for`` prefix is attached to.
    """
    first_line = "".join(cell or "" for cell in row).split("\n")[0]
    match = TABLE_TITLE.match(flatten(first_line))
    return match.group("title") if match else None


def slug(text: str) -> str:
    """A title as a stable identifier fragment: lowercase, hyphens, no punctuation.

    Truncated, because these titles run long -- "BP Treatment Threshold and the Use
    of CVD Risk Estimation to Guide Drug Treatment of Hypertension" is one of them
    -- and a `rec_id` is written into a sheet by hand and read back by eye.
    """
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned[:48].rstrip("-")


@dataclass(frozen=True)
class Recommendation:
    """One recommendation, and enough to find it again on the page.

    ``rec_id`` is the whole point of the record: it is what a threshold sheet cites
    and what gate 2 requires to be either present or scoped out by name. It is
    built from page, table and number rather than from a running counter, so
    re-running the extractor on an unchanged PDF produces the same identifiers and
    a sheet does not silently come unpinned.
    """

    rec_id: str
    doc_id: str
    page: int
    table: str
    number: int
    cor: str | None
    loe: str | None
    text: str
    mode: str


def read_table_recommendations(page_number: int, tables: list[list[list[str | None]]], doc_id: str) -> list[Recommendation]:
    """Every numbered recommendation in the ruled tables of one page.

    A table qualifies only if it carries **both** a ``Recommendations for`` title
    and a ``COR | LOE`` header. Requiring both is deliberate: the title alone also
    matches a continuation table's repeated caption, and the header alone appears
    in the front-matter legend explaining what the classes mean.
    """
    found: list[Recommendation] = []
    for rows in tables:
        if len(rows) < 3:
            continue
        title = table_title(rows[0])
        if title is None or not is_header_row(rows[1]):
            continue
        for row in rows[2:]:
            cells = [flatten(cell) for cell in row]
            if len(cells) < 3:
                continue
            numbered = NUMBERED.match(cells[-1])
            if not numbered:
                continue
            class_cell = CLASS_CELL.match(cells[0])
            found.append(
                Recommendation(
                    rec_id=f"p{page_number}/{slug(title)}/{numbered.group('number')}",
                    doc_id=doc_id,
                    page=page_number,
                    table=title,
                    number=int(numbered.group("number")),
                    cor=class_cell.group("value").lower() if class_cell else None,
                    loe=cells[1] or None,
                    text=numbered.group("text").strip(),
                    mode=MODE_EXACT,
                )
            )
    return found


def read_marker_recommendations(page_number: int, text: str, doc_id: str) -> list[Recommendation]:
    """Marker hits on one page, as an over-reporting bound.

    Every hit is a record so the caller can print where the bound comes from. The
    ``mode`` on each says ``bound``, and nothing downstream is allowed to add an
    exact count to one of these without the total becoming a bound too.
    """
    found: list[Recommendation] = []
    for name, pattern in TEXT_MARKERS:
        for index, match in enumerate(pattern.finditer(text), start=1):
            reference = match.groupdict().get("ref") if match.groupdict() else None
            found.append(
                Recommendation(
                    rec_id=f"p{page_number}/{name}/{reference or index}",
                    doc_id=doc_id,
                    page=page_number,
                    table=name,
                    number=index,
                    cor=None,
                    loe=None,
                    text=_WHITESPACE.sub(" ", text[match.start(): match.start() + 160]).strip(),
                    mode=MODE_BOUND,
                )
            )
    return found


def glued_run_census(records: list[Recommendation]) -> int:
    """Alphabetic runs at the declared floor across one document's final records."""

    return sum(len(GLUED_RUN.findall(record.text)) for record in records)


def rebuilt_page_text(page) -> str:
    """Read one page through the extraction pipeline's spacing and operator repair."""

    raw = page.get_text("rawdict")
    operators = guidelines_extract.rendered_operator_map_for_page(page, raw)
    return guidelines_extract.rebuild_text(raw, operators)


@dataclass(frozen=True)
class CuratedRow:
    """One row of ``reference/guidelines-uspstf.md``, both halves joined.

    ``statement`` comes from the second table and is the sentence the row was cut
    from. It is public-domain federal text, which is why it may sit in this repo at
    all -- see that file's own header.
    """

    topic: str
    population: str
    grade: str
    interval: str
    year: str
    statement: str
    filename: str
    page: int


def fold(text: str) -> str:
    """Letters and digits only, case-folded and NFKC-normalized.

    Used for one thing: asking whether a curated statement is on the page it cites.
    Both ends of that comparison need flattening for different reasons -- the page
    wraps mid-sentence and, on the USPSTF files, PyMuPDF's plain text loses the
    spaces between words entirely. **NFKC is the half that was not obvious.** Two of
    the corpus's rows failed this check on a typographic ligature alone: the page
    sets ``deficiency`` with U+FB01 and the table spells it out, and stripping
    non-ASCII without folding first turns that into ``deciency``. Measured
    2026-08-19: 141 of 143 rows verify without NFKC, all 143 with it.
    """
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKC", text).lower())


def _markdown_rows(markdown: str, heading: str, width: int) -> list[list[str]]:
    """The body rows of the one pipe table under ``## <heading>``.

    Keyed on the heading a table sits under rather than on its cell shape, because
    ``reference/guidelines-uspstf.md`` opens with a three-column summary of the grade
    letters -- a table whose first cell is a grade and which names no file at all.
    """
    rows: list[list[str]] = []
    current: str | None = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if current != heading or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != width or set("".join(cells)) <= set("- "):
            continue
        rows.append(cells)
    return rows[1:] if rows else rows


def parse_curated_table(markdown: str) -> dict[str, list[CuratedRow]]:
    """``reference/guidelines-uspstf.md`` as rows grouped by the file they came from.

    **The two halves are joined by position, and that join is checked rather than
    assumed.** ``uspstf_table.render_markdown`` writes both from one sorted list in
    one loop each, so they are aligned by construction -- but nothing in the file
    says so, and the failure when it stops being true is silent: every statement
    shifts by one and every record still looks well formed. So the lengths must match
    and every pair must agree on grade, file and page, and a disagreement raises
    rather than producing a best effort.
    """
    recommendations = _markdown_rows(markdown, "Recommendations", 9)
    statements = _markdown_rows(markdown, "Statements", 4)
    if not recommendations:
        raise DidNotScan(f"no '## Recommendations' table in {CURATED_TABLE.name}")
    if len(recommendations) != len(statements):
        raise DidNotScan(
            f"{CURATED_TABLE.name} has {len(recommendations)} recommendation rows and "
            f"{len(statements)} statement rows. They are written from one list, so a "
            "difference means one half was edited and the other was not."
        )

    grouped: dict[str, list[CuratedRow]] = {}
    for index, (rec, statement) in enumerate(zip(recommendations, statements), start=1):
        (
            topic,
            population,
            grade,
            interval,
            year,
            _superseded,
            _threshold_sheet,
            filename,
            page,
        ) = rec
        statement_grade, sentence, statement_file, statement_page = statement
        filename = filename.strip("`").strip()
        if (grade, filename, page) != (
            statement_grade,
            statement_file.strip("`").strip(),
            statement_page,
        ):
            raise DidNotScan(
                f"{CURATED_TABLE.name} row {index}: the Recommendations half reads "
                f"'{grade} / {filename} / {page}' and the Statements half reads "
                f"'{statement_grade} / {statement_file} / {statement_page}'. The two "
                "are joined by position, so they cannot disagree."
            )
        if not fold(sentence):
            # `curated_recommendations` asks whether the statement is ON the page it
            # cites, and an empty needle is in every haystack -- so a blank statement
            # cell would verify vacuously and hand gate 2 a recommendation to refuse a
            # sheet over whose text nobody has. Refused here rather than there, because
            # it is a defect in the table and not a mismatch with one document.
            raise DidNotScan(
                f"{CURATED_TABLE.name} row {index}: the statement for '{topic}' is "
                "empty, so there is nothing to check against the page it cites."
            )
        if not page.isdigit():
            raise DidNotScan(
                f"{CURATED_TABLE.name} row {index}: page '{page}' is not a number, so "
                "there is no page to check the statement against."
            )
        grouped.setdefault(filename, []).append(
            CuratedRow(
                topic=topic,
                population=population,
                grade=grade,
                interval=interval,
                year=year,
                statement=sentence,
                filename=filename,
                page=int(page),
            )
        )
    return grouped


def curated_records(rows: list[CuratedRow], doc_id: str) -> list[Recommendation]:
    """The curated rows of one document as records, unverified.

    ``rec_id`` welds page, topic and an ordinal within that pair, which is
    ``read_table_recommendations``'s arrangement with the topic standing in for the
    table caption. ``loe`` is None because USPSTF folds certainty into the letter and
    there is no second axis to record; the grade goes in ``cor`` **as the table
    writes it**, since gate 2 lowercases both sides of its class comparison and an
    uppercase ``I`` reads as a grade under ``--show`` where a lowercase one does not.
    """
    seen: dict[tuple[int, str], int] = {}
    found: list[Recommendation] = []
    for row in rows:
        key = (row.page, slug(row.topic))
        seen[key] = seen.get(key, 0) + 1
        found.append(
            Recommendation(
                rec_id=f"p{row.page}/{key[1]}/{seen[key]}",
                doc_id=doc_id,
                page=row.page,
                table=row.topic,
                number=seen[key],
                cor=row.grade,
                loe=None,
                text=row.statement,
                mode=MODE_EXACT,
            )
        )
    return found


def curated_recommendations(
    rows: list[CuratedRow], doc_id: str, pages: list[str]
) -> list[Recommendation]:
    """The curated rows of one document, each checked against the page it cites.

    **This check is what earns the `exact` label**, and it is the answer to the one
    objection the ruled-table sources do not have to meet. An AHA/ACC record is read
    out of the document as it is opened; a curated record is read out of a file built
    from a corpus that may since have moved. So the statement has to be on the page
    the row names, and a document whose rows do not check is reported as **not
    scanned** rather than counted short -- a record that quietly dropped its
    unverifiable rows would weaken the omission gate in exactly the direction the
    gate exists to cover.
    """
    folded: dict[int, str] = {}
    missing: list[CuratedRow] = []
    for row in rows:
        index = row.page - 1
        if index not in folded:
            folded[index] = fold(pages[index]) if 0 <= index < len(pages) else ""
        if fold(row.statement) not in folded[index]:
            missing.append(row)
    if missing:
        raise DidNotScan(
            f"{len(missing)} of {len(rows)} rows in {CURATED_TABLE.name} for "
            f"{rows[0].filename} are not on the page they cite, starting with "
            f"'{missing[0].topic}' on page {missing[0].page}. The table was built from "
            "a corpus that has since moved, or this is a different document with the "
            "same name. Rebuild it with tools/uspstf_table.py."
        )
    return curated_records(rows, doc_id)


_CURATED_CACHE: dict[str, list[CuratedRow]] | None = None


def curated_rows_for(filename: str) -> list[CuratedRow]:
    """The committed table's rows for one PDF filename, or an empty list.

    **Matched on the filename**, which is what ``uspstf_table.py`` wrote into the
    ``File`` column, so no society detection and no directory convention is involved
    -- a document is one of the curated 90 if the curated table has rows for its name,
    and is not otherwise.

    **Case-insensitively, and that is a Windows fix rather than tidiness.** ``Path.name``
    returns what the caller typed, not what the filesystem holds, so a path typed or
    pasted with different case reaches here spelled differently from the ``File``
    column -- and an exact-match miss is **silent**: the document falls through to the
    markers and comes back ``bound`` with a handful of hits where it should have come
    back ``exact``, which is the omission gate quietly losing the right to refuse.
    Two rows differing only in case would make the answer ambiguous, so that is a
    refusal rather than a pick; the committed table has none.
    """
    global _CURATED_CACHE
    if _CURATED_CACHE is None:
        if not CURATED_TABLE.is_file():
            raise DidNotScan(
                f"missing {CURATED_TABLE}. It is committed, and without it every USPSTF "
                "document in the corpus silently stops being counted -- which is why this "
                "refuses every document rather than only the ninety it would have named."
            )
        _CURATED_CACHE = parse_curated_table(CURATED_TABLE.read_text(encoding="utf-8"))
    if filename in _CURATED_CACHE:
        return _CURATED_CACHE[filename]
    lowered = filename.lower()
    matched = [name for name in _CURATED_CACHE if name.lower() == lowered]
    if len(matched) > 1:
        raise DidNotScan(
            f"{CURATED_TABLE.name} names {len(matched)} files differing only in case "
            f"from '{filename}': {', '.join(sorted(matched))}. There is no way to tell "
            "which one this document is."
        )
    return _CURATED_CACHE[matched[0]] if matched else []


def extract(
    path: Path,
    doc_id: str,
    *,
    marker_reader=rebuilt_page_text,
) -> tuple[list[Recommendation], str, str]:
    """Every recommendation in one PDF, the mode the count carries, and what earned it.

    **The curated table first, then ruled tables, then markers.** A document the
    committed USPSTF table has rows for is answered from those rows -- they are a
    ruled table with one recommendation per row and the grade in a cell, and every
    one of them is checked against the page it cites before it is believed. Reading
    the markers over such a document instead would answer one of them with a bound of
    1, because a USPSTF statement quotes another society's GRADE recommendation in
    passing.

    **Then ruled tables, and markers only if the tables found nothing.** A document
    that rules its recommendations is counted exactly; running the markers over it as
    well would add the same recommendation a second time from its own cross
    references and turn an exact count into a bound for no gain.
    """
    import pymupdf  # imported here so everything above stays importable without it

    curated = curated_rows_for(path.name)
    document = pymupdf.open(str(path))
    table_hits: list[Recommendation] = []
    try:
        if curated:
            pages = [page.get_text("text") for page in document]
            return (
                curated_recommendations(curated, doc_id, pages),
                MODE_EXACT,
                SOURCE_CURATED_TABLE,
            )
        # Table documents stop here. Reconstruction costs substantially more than a
        # plain read, so marker pages are read in a second pass only when no ruled
        # table answered the document. #446 permits this cheaper three-limb shape.
        for index, page in enumerate(document, start=1):
            try:
                tables = [table.extract() for table in page.find_tables().tables]
            except Exception:  # noqa: BLE001 - a page whose tables will not parse is not a failed document
                tables = []
            table_hits.extend(read_table_recommendations(index, tables, doc_id))
        if table_hits:
            return table_hits, MODE_EXACT, SOURCE_RULED_TABLE

        marker_hits: list[Recommendation] = []
        for index, page in enumerate(document, start=1):
            marker_hits.extend(read_marker_recommendations(index, marker_reader(page), doc_id))
        return marker_hits, MODE_BOUND, SOURCE_TEXT_MARKER
    finally:
        document.close()


def _record_payload(
    path: Path,
    doc_id: str,
    records: list[Recommendation],
    mode: str,
    counted_from: str,
    producer: dict[str, str | bool],
) -> tuple[dict[str, object], str]:
    """Serialize one standalone or sweep recommendation record."""
    outcome = RECOMMENDATIONS_FOUND if records else NOTHING_FOUND
    floor_key = counted_from if records else SOURCE_NOTHING_FOUND
    record_producer = dict(producer)
    record_producer["inputs"] = artifact_provenance.producer_file_identity(
        RECORD_TRUST_FLOOR[floor_key]
    )
    payload: dict[str, object] = {
        "doc_id": doc_id,
        "source": str(path),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "counted_from": floor_key,
        "mode": mode if records else None,
        "producer": record_producer,
        "outcome": outcome,
        "recommendations": [asdict(record) for record in records],
    }
    if records:
        payload["totals"] = {
            "recommendations": len(records),
            "tables": len({record.table for record in records}),
            "glued_runs": glued_run_census(records),
        }
    return payload, outcome


def build_sweep(
    source: Path,
    destination: Path,
    producer: dict[str, str | bool],
) -> None:
    """Write one doc-id record per corpus PDF and the sweep manifest."""
    documents: list[dict[str, str]] = []
    pdfs = sorted(
        source.rglob("*.pdf"),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    for path in pdfs:
        relative = path.relative_to(source)
        doc_id = guidelines_extract.document_id(relative)
        try:
            records, mode, counted_from = extract(path, doc_id)
        except DidNotScan as failure:
            raise DidNotScan(f"{relative.as_posix()}: {failure}") from failure
        payload, outcome = _record_payload(
            path, doc_id, records, mode, counted_from, producer
        )
        record_name = f"{doc_id}.json"
        record_path = destination / record_name
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        documents.append(
            {
                "doc_id": doc_id,
                "source": relative.as_posix(),
                "record": record_name,
                "outcome": outcome,
            }
        )
    (destination / SWEEP_MANIFEST).write_text(
        json.dumps({"schema_version": 1, "documents": documents}, indent=2)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def compare_marker_readers(path: Path, doc_id: str) -> tuple[int, int, int]:
    """Return raw count, repaired count, and changed-record count for one document.

    This is the command seam that makes #446's exposed document set re-derivable.
    It deliberately pays for two complete reads and is not used by normal builds.
    """

    repaired, _, repaired_source = extract(path, doc_id)
    if repaired_source != SOURCE_TEXT_MARKER:
        return len(repaired), len(repaired), 0
    raw, _, raw_source = extract(
        path,
        doc_id,
        marker_reader=lambda page: page.get_text("text"),
    )
    if raw_source != SOURCE_TEXT_MARKER:
        return len(raw), len(repaired), 0
    raw_by_id: dict[str, list[str]] = {}
    repaired_by_id: dict[str, list[str]] = {}
    for record in raw:
        raw_by_id.setdefault(record.rec_id, []).append(record.text)
    for record in repaired:
        repaired_by_id.setdefault(record.rec_id, []).append(record.text)
    keys = set(raw_by_id) | set(repaired_by_id)
    changed = 0
    for key in keys:
        raw_texts = Counter(raw_by_id.get(key, []))
        repaired_texts = Counter(repaired_by_id.get(key, []))
        unmatched_raw = sum((raw_texts - repaired_texts).values())
        unmatched_repaired = sum((repaired_texts - raw_texts).values())
        changed += max(unmatched_raw, unmatched_repaired)
    return len(raw), len(repaired), changed


def compare_reader_corpus(root: Path) -> tuple[int, int, int]:
    """Print changed documents and return document, changed, and record totals."""

    paths = sorted(root.rglob("*.pdf"), key=lambda path: path.relative_to(root).as_posix())
    changed_documents = 0
    changed_records = 0
    for path in paths:
        doc_id = path.relative_to(root).with_suffix("").as_posix()
        raw_count, repaired_count, changed = compare_marker_readers(path, doc_id)
        if not changed:
            continue
        changed_documents += 1
        changed_records += changed
        print(
            f"  {doc_id}  raw {raw_count}  repaired {repaired_count}  "
            f"changed {changed}"
        )
    return len(paths), changed_documents, changed_records


# Why *this* artifact stays out, which is not why the other two do: the JSON
# holds the society's own recommendation text in full, and #87 rules that stays
# outside every checkout. The detection is ``repo_root.enclosing_checkout`` --
# this module was written after #176 was filed and grew a third copy of the rule
# rather than importing one of the two that already existed, which is that
# ticket's thesis demonstrated by the ticket's own aftermath.
WHY_OUTSIDE = "This file holds the society's recommendation text in full. #87."


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "pdf",
        type=Path,
        help="guideline PDF, or a corpus directory with --compare-readers",
    )
    parser.add_argument(
        "--doc-id",
        default=None,
        help="identifier to record (default: the file stem), matching the manifest's",
    )
    parser.add_argument("--json", type=Path, default=None, help="write full records here")
    parser.add_argument(
        "--show",
        action="store_true",
        help="print recommendation text -- the society's expression, not for pasting",
    )
    parser.add_argument(
        "--compare-readers",
        action="store_true",
        help="report whether the raw and repaired marker readers differ for this document",
    )
    args = parser.parse_args(argv)
    if args.compare_readers and args.json:
        parser.error("--compare-readers does not write --json")
    if args.compare_readers and args.show:
        parser.error("--compare-readers reports counts and does not take --show")

    # Before the PDF is opened, not after the records are printed. Where the
    # JSON lands is a question about the arguments alone, and a run that reads
    # a document and then refuses to write it has spent the expensive half for
    # nothing. It also lets `test_write_guards.py` cross-check this command
    # line against its three siblings without a PDF or a PDF library.
    json_target = None
    if args.json:
        if not args.json.stem.startswith(RECS_PREFIX):
            raise SystemExit(
                f"--json target filename must start with '{RECS_PREFIX}': {args.json.name}"
            )
        try:
            json_target = ensure_outside_checkout(args.json, detail=WHY_OUTSIDE)
        except InsideCheckout as refused:
            raise SystemExit(str(refused)) from refused

    if args.compare_readers and args.pdf.is_dir():
        if args.doc_id:
            parser.error("--doc-id cannot be used with a corpus directory")
        documents, changed_documents, changed_records = compare_reader_corpus(args.pdf)
        if not documents:
            print(f"no PDFs under {args.pdf}", file=sys.stderr)
            return 2
        print("SUMMARY")
        print(f"  documents         {documents}")
        print(f"  changed documents {changed_documents}")
        print(f"  changed records   {changed_records}")
        return 0

    if not args.pdf.is_file():
        # 2 rather than 1, on `guidelines_search.py`'s arrangement: not having read
        # a document must never be reported in the same way as having read one and
        # found no recommendations in it.
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 2

    doc_id = args.doc_id or args.pdf.stem
    if args.compare_readers:
        try:
            raw_count, repaired_count, changed = compare_marker_readers(args.pdf, doc_id)
        except DidNotScan as reason:
            print(f"did not scan {args.pdf.name}", file=sys.stderr)
            print(f"  {reason}", file=sys.stderr)
            return 2
        print(f"== {doc_id}")
        print(f"  raw records      {raw_count}")
        print(f"  repaired records {repaired_count}")
        print(f"  changed records  {changed}")
        print(f"  reader changed   {'yes' if changed else 'no'}")
        return 0

    try:
        records, mode, source = extract(args.pdf, doc_id)
    except DidNotScan as reason:
        # 2 on the same reasoning as the branch below: a stale curated table is a
        # document this module has not read, and reporting it as a count would file
        # the strongest thing known about the run under the weakest heading.
        print(f"did not scan {args.pdf.name}", file=sys.stderr)
        print(f"  {reason}", file=sys.stderr)
        return 2

    if not records:
        print(f"no recommendation found in {args.pdf.name}", file=sys.stderr)
        print("Neither a ruled COR/LOE table nor a text marker. Nothing was counted,", file=sys.stderr)
        print("which is not the same as this document having no recommendations.", file=sys.stderr)
        return 2

    tables = sorted({record.table for record in records})
    glued_runs = glued_run_census(records)
    print(f"== {doc_id}")
    print(f"  mode            {mode}")
    print(f"  source          {source}")
    print(f"  recommendations {len(records)}")
    print(f"  tables          {len(tables)}")
    print(
        f"  glued runs      {glued_runs} "
        f"(alphabetic runs of at least {GLUED_RUN_MIN_LETTERS}; reports only)"
    )
    if source == SOURCE_CURATED_TABLE:
        print()
        print(f"  claim: read out of {CURATED_TABLE.name}, not out of this PDF's own")
        print("  layout. Every row was checked to be on the page it cites before it")
        print("  was counted, which is what lets the mode be 'exact'; the grade is the")
        print("  class and there is no separate level of evidence.")
    if mode == MODE_BOUND:
        print()
        print("  claim: this is an OVER-REPORT and must not be read as a count.")
        print("  A marker is matched wherever it appears, including in a table of")
        print("  contents and in prose citing another recommendation. Gate 2 warns")
        print("  on a bound and refuses only on an exact source.")

    if args.show:
        print()
        for record in records:
            classification = f"[{record.cor or '-'}/{record.loe or '-'}]"
            print(f"  {record.rec_id}  {classification}  {record.text[:110]}")

    if json_target is not None:
        # The path the guard resolved, never the one it was handed: writing to a
        # different string than the one that was checked is how a guard comes to
        # have been consulted about a path nothing wrote to.
        json_target.parent.mkdir(parents=True, exist_ok=True)
        payload, _ = _record_payload(
            args.pdf,
            doc_id,
            records,
            mode,
            source,
            artifact_provenance.current_producer(),
        )
        json_target.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"  json            {json_target}")

    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
