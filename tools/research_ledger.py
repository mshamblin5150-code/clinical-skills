"""Grade a research ledger and its optional draft/evidence companions.

    python tools/research_ledger.py <a ledger file> [--draft <a draft .md>]
        [--evidence <the evidence dump>] [--show]

The ledger is the pre-draft mechanism established by #214: one prewritten record
per claim, completed by the research and refutation passes, then graded before
drafting. ``--draft`` adds the prescription joins established by #289;
``--evidence`` adds the citation-to-evidence joins established by #298.

The complete coverage inventory is ``research_ledger.DECLARED_LIMITS``. This
docstring points to that object and states no second version of any row. Its
population was derived by an end-to-end read of this module and every record in
``docs/adr/`` on 2026-08-27; later prose-only boundaries remain reader-owned.

Counts print by default because the ledger can contain PHI. ``--show`` output is PHI;
it exposes claim details and must not be pasted. Exit 0 is clean, exit 1 reports findings,
and exit 2 means a required input or mechanically readable population was absent.
"""

from __future__ import annotations

import hashlib
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import NamedTuple

import run_grader
from run_grader import NOT_GRADED
import coursework_run
import uptodate_store
from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root
from run_grader import EvidenceDisposition
from docx_write import markdown_tables, split_row

# **The draft's reference list is parsed once, by the module that grades it.**
# ``reference_scan`` importing ``docx_write.REFERENCE_HEADING`` is the
# precedent and this is the same argument at the width of the whole list: a
# second reading in here could put an entry where the grader does not, which
# is #108's duplication and the failure ``reference_scan`` records against
# itself. A test asserts the two are one object *and* drives both.
from reference_scan import YEAR_TOKEN, read_document, year_key


class DeclaredLimit(NamedTuple):
    """One named coverage boundary and how its evidence is maintained."""

    key: str
    limit: str
    evidence: EvidenceDisposition


DECLARED_LIMITS = (
    DeclaredLimit("execution-order-unobservable", "The ledger cannot show whether claim research ran concurrently or serially.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("record-population-unbounded", "The grader has no expected claim-record population to detect omitted records.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("reason-substance-unverified", "Alphanumeric substance cannot prove that a stated search or reason happened.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("restatement-semantic-equivalence-unchecked", "Only normalized equality is rejected; semantic restatements are not compared.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("numeric-values-uncompared", "Numeric claims and restatements need numbers whose actual values are never compared.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("two-year-target-unenforced", "The preferred two-year recency target remains unenforced for sources other than UpToDate.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("doi-shape-overmatches", "The bare-DOI pattern also accepts page-range text shaped like a DOI.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("locator-opening-unverified", "A record may state a locator that its research agent never opened.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("source-reputation-unchecked", "An allowed source-class word does not establish that the source is reputable.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("source-support-unchecked", "The grader cannot determine whether a source supports its recorded restatement.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("pointer-primary-material-unverified", "The grader cannot establish that derived material has primary material retained and gradeable against it, or resolvable and independently re-opened.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("negative-search-population-unverified", "The grader cannot establish that a negative reports the corpus it read and what it did not open.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("absence-refutation-passage-quote-unverified", "The grader cannot establish that a refutation reporting absent language read and quoted the record's PASSAGE.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("sourceless-recheckability-unverified", "A clean sourceless record does not establish that a rejected source was named well enough for a reader to recheck it.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("unsourced-draft-exclusion-unchecked", "A clean ledger does not establish that unsourced claims stayed outside the draft.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("network-resolution-absent", "No grading path fetches a locator or resolves a citation over the network.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("refutation-independence-unverified", "SECOND-ROUTE cannot prove that the refuter was a different agent, that it actually took the route it declared, or that it opened anything.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("tested-heading-does-not-prove-refutation", "TESTED-HEADING proves only that the recorded fingerprint matches the current heading; it cannot prove that the refuter actually tested that heading.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("research-authenticated-route-unverified", "Nothing can see whether the browser was opened, and nothing can see whether the profile's answer was consulted.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("stated-expiry-transcription-unverified", "The grader cannot prove that a STATED-EXPIRY value was transcribed from the cited document rather than inferred.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("publication-cadence-reader-owned", "STATED-EXPIRY does not carry cadence-derived dates. Re-open the day a tree-wide count returns a SECOND citation on a published reissue cadence, or a SECOND distinct publisher in that bucket; measured 1 and 1 on 2026-08-27, at f9a501c, over 22 citations in 4 claim ledgers. This reader-owned trigger cannot fire mechanically.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("read-date-lower-bound-absent", "A source read arbitrarily long before the writing date can still pass.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("keyword-parser-copy-uncompared", "Parity with checks_ledger's intentionally copied keyword parser is not asserted.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("paywall-body-unread", "The passing paywalled disposition verifies no claim against the source body.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("page-year-first-plausible-token", "PAGE-YEAR uses the first plausible year even when that token is a page number.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("prescription-number-correctness-unchecked", "Prescription grading establishes sourcing but never whether a dose is clinically correct.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("dose-claim-accepts-any-number", "A dosed drug's claim may contain an unrelated number and satisfy the row.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("welded-drug-hidden", "A second medication welded into one order is invisible to prescription grading.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("leading-token-drug-parser", "Only the leading token identifies a medication and matching errs toward omission.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("spelled-dose-unseen", "A dose written only as words is not recognized as a numeric prescription.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("dose-versus-indication-unseen", "A drug-naming claim may quantify an indication without sourcing the prescribed dose.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("drug-sig-agreement-unseen", "Prescription grading does not compare the medication order with its Sig row.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("table-record-number-equivalence-unseen", "Equivalent or conflicting dose expressions between draft and record are not compared.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("partial-prescription-table-nonfatal", "Partially anchored prescription tables are reported but do not fail the grade.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("rx-reader-completion-unverified", "The grader cannot prove that the separate prescription reader completed its brief.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("evidence-cross-references-ungraded", "Topics merely cross-referenced by an evidence dump are outside the filed set.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("titled-copy-titles-trusted", "Membership trusts a titled copy's declared titles and does not establish that the supplied dump carried them.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("non-uptodate-evidence-unjoined", "Evidence coverage is not joined for journal, society, or government citations.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("unrecognizable-uptodate-entry-unseen", "An UpToDate citation lacking both database element and locator is invisible.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("uncited-missing-topic-unseen", "A claim derived from missing evidence is invisible when no citation names it.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("draft-rows-optional", "Prescription coverage is not graded when the caller omits the draft argument.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("evidence-rows-optional", "Evidence-topic coverage is not graded when the caller omits the evidence argument.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("evidence-without-draft-skips-references", "Evidence grading without a draft cannot inspect citations in the draft reference list.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("uptodate-initials-uncompared", "The stored UpToDate masthead check does not compare author initials.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("uptodate-trailing-surname-accepted", "An UpToDate entry that shortens a real surname to its trailing words passes.", EvidenceDisposition.BEHAVIOR),
    DeclaredLimit("non-uptodate-author-year-unchecked", "Authors and years of sources other than a stored UpToDate topic are not checked by this command; the refutation agent verifies them.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("reply-reference-label-unchecked", "The discussion-reply path omits draft grading and cannot reject a misspelled references label.", EvidenceDisposition.BEHAVIOR),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)

# A record opens on a heading. The heading level is free, so the ledger can sit
# under a document heading without the parser caring.
CLAIM = re.compile(r"(?mi)^[ \t]*#+[ \t]*CLAIM[ \t]*:[ \t]*(.*?)[ \t]*$")
FIELD = re.compile(
    r"(?mi)^[ \t]*(STATUS|SOURCE|REFERENCE|RESTATEMENT|PASSAGE|RECENCY"
    r"|RESOLVED|PAGE-YEAR|REFUTATION|TESTED-HEADING|SECOND-ROUTE|INSTRUMENTS|STATED-EXPIRY|DROPPED)"
    r"[ \t]*:[ \t]*(.*?)[ \t]*$"
)
BAR_FIELD = re.compile(
    r"(?mi)^(?P<name>SOURCE-CLASSES|RECENCY-WINDOW-YEARS|UPTODATE-RECENCY-WINDOW-YEARS)"
    r"\s*:\s*(?P<value>[^\n]+?)\s*$"
)
# The day the paper is written. Recency is measured against it and never against
# the clock -- a ledger graded twice a year apart has to grade the same both times.
DATE_HEADER = re.compile(r"(?mi)^[ \t]*DATE[ \t]*:[ \t]*(\d{4})-(\d{2})-(\d{2})[ \t]*$")

# An APA entry states its year in parentheses. ``2019a`` is the a/b disambiguation
# form ``reference/apa7.md`` section 3 requires, so the letter is allowed and dropped.
YEAR = re.compile(r"\((\d{4})[a-z]?(?:,[^)]*)?\)")

# The closed vocabulary spans both coursework pipelines. Which members a run
# permits is signed in its own bar, so admitting market evidence for a deck does
# not make it sourceable for a clinical paper.
SOURCE_CLASS_VOCABULARY = (
    "society guideline",
    "peer-reviewed",
    "government",
    "tertiary reference",
    "market source",
)

# #215's four dispositions. The last two are the ones that excuse an old source,
# and both have to say why.
RECENCY_CURRENT = "current"
RECENCY_WITHIN_FIVE = "within five"
RECENCY_NOTHING_NEWER = "nothing newer"
RECENCY_IN_FORCE = "guideline in force"
RECENCY_VALUES = (RECENCY_CURRENT, RECENCY_WITHIN_FIVE, RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)
EXCUSES = (RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)

# #231 accepts a URL or bare DOI so the record commits to a specific locator.
# #242 retained the DOI suffix's free form because the documented bare form has
# no required scheme or ``doi:`` prefix; the date and refutation rows provide the
# independent checks that made that choice affordable.
LOCATOR = re.compile(r"(?i)\bhttps?://\S+|\b10\.\d{4,9}/\S+")
# Anchored on the word rather than on the shape, because a URL is full of digits
# and one of them being date-shaped is not the agent saying when it looked.
# ``retrieved`` beside ``read`` because ``apa7.md`` section 4 calls it a retrieval
# date, so a run copying that word is writing the field right rather than wrong.
#
# **The anchor word has to be outside the URL, and the first version was not.**
# ``https://site.org/read/2026-01-02/piece`` matched, so an archive path supplied a
# read date the agent never wrote -- a locator grading itself as dated. The
# lookbehind refuses a word joined to what precedes it, and the separator between
# the word and the date may not be a slash.
READ_DATE = re.compile(
    r"(?i)(?<![/\-\w])(?:read|retrieved)\b[ \t]*[:\-]?[ \t]*(\d{4})-(\d{2})-(\d{2})"
)
# The year a page states, which is not written in parentheses the way an APA
# entry's is -- so this is the bare form and ``YEAR`` is deliberately not reused.
#
# **Restricted to plausible years, and the first version was not.** A bare
# ``\d{4}`` takes the first four-digit token, and ``PAGE-YEAR`` is documented as the
# year *and where the page says so* -- so ``on page 1327, dated 2009`` read as the
# year 1327 and reported a false disagreement against a correct record. A page
# number is not in 1900-2099. The documented form puts the asserted year first.
BARE_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")

# #231's refutation dispositions, widened by ADR 0149. The brief is to *refute*, so ``stands`` is the outcome
# of a failed attempt rather than the default.
#
# ``paywalled`` is the clinician's 2026-08-19 decision-4 disposition. It is
# available only after the clinician's Authenticated route still leaves the body
# unreadable. A resolving locator that matches the entry is evidence the document
# exists; the report keeps that weaker verification visible as its own count.
REFUTATION_STANDS = "stands"
REFUTATION_REFUTED = "refuted"
REFUTATION_PAYWALLED = "paywalled"
REFUTATION_UNREADABLE = "unreadable"
REFUTATION_VALUES = (
    REFUTATION_STANDS,
    REFUTATION_REFUTED,
    REFUTATION_PAYWALLED,
    REFUTATION_UNREADABLE,
)

# #498's three forms. A date is transcribed from the source, never inferred
# from a publication cadence. The C.F.R. citation that filed #534 is the known
# instance where ``none stated`` is the correct answer: its codification year is
# provenance and the annual reissue schedule is not a stated expiry.
STATED_EXPIRY_NONE = "none stated"
STATED_EXPIRY_DATE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})[ \t]+-[ \t]+(?P<where>.+)$"
)
STATED_EXPIRY_ESCAPE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}),[ \t]*superseded cited deliberately"
    r"[ \t]+-[ \t]+(?P<reason>.+)$",
    re.I,
)

SOURCED = "sourced"
UNSOURCED = "unsourced"
UNREADABLE = "unreadable"
STATUSES = (SOURCED, UNSOURCED, UNREADABLE)

# ``specificity_scan.py`` R2's alphanumeric substance predicate.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")
DIGIT = re.compile(r"[0-9]")
NOT_ALNUM = re.compile(r"[^0-9a-z]+")

# #253. What may follow a vocabulary keyword, so a prefix is not read as a word.
# The hyphen is excluded deliberately -- see ``keyword_of``.
BOUNDARY = re.compile(r"[^0-9A-Za-z-]|$")
SHA256 = re.compile(r"[0-9a-fA-F]{64}", re.ASCII)

MISSING_FIELD = "missing-field"
UNKNOWN_STATUS = "unknown-status"
BARE_STATUS = "bare-status"
SOURCELESS_WITH_SOURCE_FIELD = "sourceless-with-source-field"
UNKNOWN_SOURCE_CLASS = "unknown-source-class"
UNKNOWN_RECENCY = "unknown-recency"
RESTATEMENT_ECHOES_CLAIM = "restatement-echoes-claim"
NUMERIC_CLAIM_UNQUANTIFIED = "numeric-claim-unquantified"
UNDATED_REFERENCE = "undated-reference"
STALE_UNEXCUSED = "stale-unexcused"
BARE_EXCUSE = "bare-excuse"
UNRESOLVABLE_LOCATOR = "unresolvable-locator"
UNDATED_READ = "undated-read"
READ_AFTER_DATE = "read-after-date"
PAGE_YEAR_UNSTATED = "page-year-unstated"
BARE_PAGE_YEAR = "bare-page-year"
PAGE_YEAR_DISAGREES = "page-year-disagrees"
UNKNOWN_REFUTATION = "unknown-refutation"
BARE_REFUTATION = "bare-refutation"
REFUTED_CITATION = "refuted-citation"
REFUTATION_ECHOES_RESTATEMENT = "refutation-echoes-restatement"
MALFORMED_TESTED_HEADING = "malformed-tested-heading"
TESTED_HEADING_MISMATCH = "tested-heading-mismatch"
UNSPLIT_SECOND_ROUTE = "unsplit-second-route"
BARE_SECOND_ROUTE = "bare-second-route"
SECOND_ROUTE_UNCHANGED = "second-route-unchanged"
UNEXPECTED_INSTRUMENTS = "unexpected-instruments"
UNSPLIT_INSTRUMENTS = "unsplit-instruments"
BARE_INSTRUMENTS = "bare-instruments"
INSTRUMENTS_UNCHANGED = "instruments-unchanged"
UNKNOWN_STATED_EXPIRY = "unknown-stated-expiry"
STATED_EXPIRY_REACHED = "stated-expiry-reached"

# #289 and #298 add the draft and evidence grading groups. Their optional-run
# reporting follows #258's distinction between an executed zero and an omitted
# group.
CITED_TOPIC_NOT_IN_EVIDENCE = "cited-topic-not-in-evidence"
UPTODATE_REREAD_DUE = "uptodate-reread-due"
UPTODATE_MASTHEAD_DISAGREES = "uptodate-masthead-disagrees"
SOURCED_RECORD_NOT_LISTED = "sourced-record-not-listed"
BARE_DROPPED = "bare-dropped"
DROPPED_ON_SOURCELESS_RECORD = "dropped-on-sourceless-record"

# The sibling row reports an UpToDate locator whose title element is unreadable,
# on ``UNREADABLE_DRUG_ROW``'s fail-visible precedent.
UNREADABLE_UPTODATE_ENTRY = "unreadable-uptodate-entry"

UNRESEARCHED_PRESCRIPTION = "unresearched-prescription"
DOSE_NOT_CLAIMED = "dose-not-claimed"
UNREADABLE_DRUG_ROW = "unreadable-drug-row"

# Which ruling each row belongs to, so a reader knows which ticket to go and read.
ROWS = {
    CITED_TOPIC_NOT_IN_EVIDENCE: "#298",
    UPTODATE_REREAD_DUE: "#901",
    UPTODATE_MASTHEAD_DISAGREES: "#1021",
    SOURCED_RECORD_NOT_LISTED: "#1021",
    BARE_DROPPED: "#1021",
    DROPPED_ON_SOURCELESS_RECORD: "#1021",
    UNREADABLE_UPTODATE_ENTRY: "#298",
    UNRESEARCHED_PRESCRIPTION: "#289",
    DOSE_NOT_CLAIMED: "#289",
    UNREADABLE_DRUG_ROW: "#289",
    MISSING_FIELD: "#214",
    UNKNOWN_STATUS: "#214",
    BARE_STATUS: "#214",
    SOURCELESS_WITH_SOURCE_FIELD: "#214",
    UNKNOWN_SOURCE_CLASS: "#214",
    UNKNOWN_RECENCY: "#215",
    RESTATEMENT_ECHOES_CLAIM: "#214",
    NUMERIC_CLAIM_UNQUANTIFIED: "#214",
    UNDATED_REFERENCE: "#215",
    STALE_UNEXCUSED: "#215",
    BARE_EXCUSE: "#215",
    UNRESOLVABLE_LOCATOR: "#231",
    UNDATED_READ: "#231",
    READ_AFTER_DATE: "#231",
    PAGE_YEAR_UNSTATED: "#231",
    BARE_PAGE_YEAR: "#231",
    PAGE_YEAR_DISAGREES: "#231",
    UNKNOWN_REFUTATION: "#231",
    BARE_REFUTATION: "#231",
    REFUTED_CITATION: "#231",
    REFUTATION_ECHOES_RESTATEMENT: "#231",
    MALFORMED_TESTED_HEADING: "#1032",
    TESTED_HEADING_MISMATCH: "#1032",
    UNSPLIT_SECOND_ROUTE: "#500",
    BARE_SECOND_ROUTE: "#500",
    SECOND_ROUTE_UNCHANGED: "#500",
    UNEXPECTED_INSTRUMENTS: "#818",
    UNSPLIT_INSTRUMENTS: "#818",
    BARE_INSTRUMENTS: "#818",
    INSTRUMENTS_UNCHANGED: "#818",
    UNKNOWN_STATED_EXPIRY: "#498",
    STATED_EXPIRY_REACHED: "#498",
}
KINDS = tuple(ROWS)

# Report order as a lookup, built from ``KINDS`` rather than typed beside it. Every
# helper appends in whatever order its own rules read best, and ``record_findings``
# sorts once -- so which helper a row lives in is not something the report can see.
_KIND_ORDER = {kind: index for index, kind in enumerate(KINDS)}

REQUIRED_WHEN_SOURCED = (
    "SOURCE",
    "REFERENCE",
    "RESTATEMENT",
    "PASSAGE",
    "RECENCY",
    "RESOLVED",
    "PAGE-YEAR",
    "REFUTATION",
    "TESTED-HEADING",
    "SECOND-ROUTE",
    "STATED-EXPIRY",
)

REFUTATION_EVIDENCE_FIELDS = (
    "REFUTATION",
    "TESTED-HEADING",
    "SECOND-ROUTE",
)
REFUTATION_EVIDENCE_COMPLEMENT = tuple(
    field
    for field in REQUIRED_WHEN_SOURCED
    if field not in REFUTATION_EVIDENCE_FIELDS
)

# Every required sourced field makes a claim about a source. Deriving this
# population prevents a later sourced-field addition from silently escaping the
# sourceless-record rule.
SOURCE_FIELDS = REQUIRED_WHEN_SOURCED

# The #289 report group, held once so report ordering and optional-run display
# share one population.
DRAFT_ROWS = (UNRESEARCHED_PRESCRIPTION, DOSE_NOT_CLAIMED, UNREADABLE_DRUG_ROW)

# The #298 report group, on ``DRAFT_ROWS``' single-population arrangement.
EVIDENCE_ROWS = (
    CITED_TOPIC_NOT_IN_EVIDENCE,
    UPTODATE_REREAD_DUE,
    UPTODATE_MASTHEAD_DISAGREES,
    UNREADABLE_UPTODATE_ENTRY,
)

# A prescription table is the one table in a case study carrying both of
# these, and the drug row is the row above ``Disp:``. **A welded pair and a
# position read off an anchor**, never a row counted from the top of the
# table: ``differential_scan.py``'s first version read a refusal by position
# and failed in both directions at once, and #153's repair was exactly this.
# A run that omits either anchor has not written a prescription table, and
# ``main``'s exit-2 limb is what says so rather than a clean zero.
DISP = re.compile(r"(?i)^disp\b[ \t]*:")
SIG = re.compile(r"(?i)^sig\b[ \t]*:")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")

# #215's false-alarm direction governs this intentionally small parser; #300
# keeps the broader medication-identity judgment with the
# ``practicum-case-study`` step-9 reader.
DRUG_NAME = re.compile(r"[A-Za-z][A-Za-z'-]*")

# What a drug row may declare about itself. **The exemption is declared and
# never inferred**, so the rule fails closed: a row saying nothing is graded.
# ``continued home medication`` is the clinician's ruling of 2026-08-19 on
# #289's decision 1 -- a home medication continued unchanged at the patient's
# own dose is a number the run did not choose. ``delayed order`` is
# ``style.md`` section 8's existing declaration and exempts nothing: a dose
# that has not started yet is still a dose the run chose.
CONTINUED_HOME = "continued home medication"
DELAYED_ORDER = "delayed order"
DRUG_ROW_DECLARATIONS = (CONTINUED_HOME, DELAYED_ORDER)
EXEMPT_DECLARATIONS = (CONTINUED_HOME,)


def normalize(text: str) -> str:
    """Lowercase alphanumerics for the #214 equality check."""
    return " ".join(NOT_ALNUM.sub(" ", text.lower()).split())


def heading_digest(heading: str) -> str:
    """SHA-256 of a claim heading after collapsing whitespace only."""
    canonical = " ".join(heading.split())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Built from ``normalize`` rather than typed, so the lookup and the comparison it
# stands in for cannot come to disagree about what a mis-keyed value looks like.
# Built once rather than per record. ``SOURCE`` can afford this and ``RECENCY``
# cannot: there the whole value is the keyword, here the keyword is a prefix with a
# reason after it, and normalizing destroys the boundary between them.
_VOCABULARY_KEYS = frozenset(normalize(name) for name in SOURCE_CLASS_VOCABULARY)


@dataclass(frozen=True)
class LedgerBar:
    source_classes: tuple[str, ...]
    recency_window_years: int
    uptodate_recency_window_years: int | None


def read_bar(text: str) -> LedgerBar:
    """Read the per-run research decisions from a signed bar."""
    matches = tuple(BAR_FIELD.finditer(text))
    fields = {match.group("name"): match.group("value").strip() for match in matches}
    for name in (
        "SOURCE-CLASSES",
        "RECENCY-WINDOW-YEARS",
        "UPTODATE-RECENCY-WINDOW-YEARS",
    ):
        if sum(match.group("name") == name for match in matches) > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
    for name in ("SOURCE-CLASSES", "RECENCY-WINDOW-YEARS"):
        count = sum(match.group("name") == name for match in matches)
        if count == 0:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    classes = tuple(item.strip().casefold() for item in fields["SOURCE-CLASSES"].split("|"))
    if not classes or any(not item for item in classes) or len(set(classes)) != len(classes):
        raise run_grader.SourceError("bar.md SOURCE-CLASSES must be distinct values separated by |")
    unknown = tuple(item for item in classes if normalize(item) not in _VOCABULARY_KEYS)
    if unknown:
        accepted = " | ".join(SOURCE_CLASS_VOCABULARY)
        raise run_grader.SourceError(
            f"bar.md SOURCE-CLASSES has an unknown value; accepted values are {accepted}"
        )
    window = fields["RECENCY-WINDOW-YEARS"]
    if not window.isdigit() or int(window) < 1:
        raise run_grader.SourceError("bar.md RECENCY-WINDOW-YEARS must be a positive integer")
    uptodate_window = fields.get("UPTODATE-RECENCY-WINDOW-YEARS")
    if uptodate_window is not None and (
        not uptodate_window.isdigit() or int(uptodate_window) < 1
    ):
        raise run_grader.SourceError(
            "bar.md UPTODATE-RECENCY-WINDOW-YEARS must be a positive integer"
        )
    return LedgerBar(
        classes,
        int(window),
        None if uptodate_window is None else int(uptodate_window),
    )


def keyword_of(value: str, vocabulary: tuple[str, ...]) -> tuple[str, str]:
    """Split a field value into its vocabulary keyword and the remainder.

    Longest first, so ``guideline in force`` is not read as an unrecognized value
    that happens to begin with a shorter one.

    **A prefix is not a word**, and this limb is
    [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253).
    Matching on ``startswith`` alone read any value whose first token merely
    *began with* a vocabulary word as that word, and absorbed the rest of the token
    into the remainder -- which is the field the substance rows then read as a
    reason.

    **The values that graded *clean* are the ones that matter, and they are not the
    one #253's title names.** ``STATUS: unsourced-but-see-below`` produced **no
    findings at all**: the substance row was satisfied by ``-but-see-below``, the
    residue of the very keyword it was keyed on, so a record saying nothing about
    what was searched passed the row that exists to make it say so. ``RECENCY:
    nothing newerish`` and ``RECENCY: guideline in forceful terms`` did the same
    one field over, and there the excuse is what the **window** reads -- so an old
    reference with no excuse and no reason passed with nothing reported.

    **``RECENCY: currently under review`` is a weaker case than the ticket, this
    docstring and the commit that landed them all said, and the correction is the
    finding.** ``current`` is not in ``EXCUSES``, so the window fired on that value
    before the fix and fires now; ``BARE_EXCUSE`` can never fire on it at all. What
    the prefix bug suppressed there is ``UNKNOWN_RECENCY`` alone. The wrong
    consequence was copied out of #253's table while only its *keyword* column was
    re-derived -- the same failure this work caught in that table's second row,
    committed in the fix for it, and caught by the tracker sweep afterwards.
    ``REFUTATION: standstill on the publisher's side`` is the defect on the one
    verification row.

    **The hyphen is excluded from the boundary, and that was ruled rather than
    copied from the sibling.** ``RECENCY: nothing newer - searched 2026-08-19`` is
    the documented form, so a **spaced** hyphen is a separator; a **welded** one is
    part of the word. No legitimate value of the vocabularies this helper serves
    opens with a welded hyphenated form -- checked against the tree, not assumed,
    and ``test_research_ledger`` reads which vocabularies those are off this
    module rather than listing them. ``SOURCE`` is outside this helper, matched by
    normalized equality against ``_VOCABULARY_KEYS``, which is also where the corpus's
    only hyphen *inside* a vocabulary word lives: ``peer-reviewed``.

    **This adopted the sibling's rule rather than sharing its code.** The copy is
    intentional because the two record vocabularies may diverge; #143 records why
    prose must not claim a current identity between them.
    """
    stripped = value.strip()
    lowered = stripped.lower()
    for word in sorted(vocabulary, key=len, reverse=True):
        if lowered.startswith(word) and BOUNDARY.match(lowered[len(word) :]):
            return word, stripped[len(word) :]
    return "", stripped


def stated_expiry_of(value: str) -> tuple[date | None, bool, bool]:
    """Return the stated date, deliberate-supersession flag, and valid-form flag."""
    stripped = value.strip()
    if normalize(stripped) == normalize(STATED_EXPIRY_NONE):
        return None, False, True

    escaped = STATED_EXPIRY_ESCAPE.fullmatch(stripped)
    ordinary = STATED_EXPIRY_DATE.fullmatch(stripped)
    match = escaped or ordinary
    if not match:
        return None, False, False
    try:
        stated = date.fromisoformat(match.group("date"))
    except ValueError:
        return None, False, False
    detail = match.group("reason" if escaped else "where")
    if not SUBSTANCE.search(detail):
        return None, False, False
    return stated, escaped is not None, True


@dataclass(frozen=True)
class Record:
    """One claim and the fields the fan-out returned for it."""

    claim: str
    fields: dict[str, str] = field(default_factory=dict)

    def value(self, name: str) -> str:
        return self.fields.get(name, "")

    @property
    def status(self) -> str:
        return keyword_of(self.value("STATUS"), STATUSES)[0]

    @property
    def reference_year(self) -> int | None:
        match = YEAR.search(self.value("REFERENCE"))
        return int(match.group(1)) if match else None

    @property
    def page_year(self) -> int | None:
        """The year the page itself states, per #231's ``PAGE-YEAR``.

        Bare rather than parenthesized: this is what a reader copied off a cover
        page, not an APA date element.
        """
        match = BARE_YEAR.search(self.value("PAGE-YEAR"))
        return int(match.group(1)) if match else None

    @property
    def read_date(self) -> date | None:
        """The day the agent says it opened the source, or ``None``.

        A date that does not exist reads as no date at all -- the field failed to
        say when it was read, which is the finding either way.
        """
        match = READ_DATE.search(self.value("RESOLVED"))
        if not match:
            return None
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None


@dataclass(frozen=True)
class Prescription:
    """One drug row of one prescription table in the draft.

    ``drug`` uses an empty sentinel for ``UNREADABLE_DRUG_ROW``. ``order`` has
    its declaration stripped before the numeric branch runs.
    """

    drug: str
    order: str
    declaration: str = ""

    @property
    def exempt(self) -> bool:
        return self.declaration in EXEMPT_DECLARATIONS

    @property
    def states_a_dose(self) -> bool:
        """Whether the authored order carries a digit for #289's branch."""
        return bool(DIGIT.search(self.order))


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One record failing one row."""

    claim: str
    detail: str


@dataclass(frozen=True)
class MastheadScan:
    """Coverage and findings from the bounded stored-topic author read.

    The author extractors recognize APA ``Surname, initials`` elements and
    stored ``Name, degree`` elements. A joined citation in any other form is an
    unread member, is printed in the remainder, and fails rather than passing
    as an empty-to-empty comparison.
    """

    findings: tuple[Finding, ...]
    population: int
    read: int
    unread: int


@dataclass(frozen=True)
class Scan:
    """Counts over one ledger, plus the findings ``--show`` prints."""

    as_of: date | None
    records: int
    sourced: int
    unsourced: int
    unreadable: int
    unrecognized_status: int
    by_class: tuple[tuple[str, int], ...]
    outside_vocabulary: int
    recency_window_years: int
    standing_past_window: int
    # #231's visible paywall population.
    behind_a_paywall: int
    # ADR 0149's visible failed-refutation-read population.
    unreadable_refutations: int
    # #498's two always-printed expiry populations.
    stated_expiries: int
    superseded_deliberately: int
    counts: tuple[tuple[str, int], ...]
    failing_records: int
    # ``None`` is #258's sentinel for the omitted #289 group.
    prescriptions: int | None
    continued_home: int
    # The #204 partial-read census from ``half_anchored_tables``.
    half_anchored: int
    prescriptions_at_fault: int
    draft_references_at_fault: int
    # ``None`` is #258's sentinel for the omitted #298 group.
    evidence_topics: int | None
    # The omitted flag and an unfiled supplied file are different ungraded states.
    evidence_ungraded_reason: str | None
    # The #298 joined-citation population beside the carried-topic population.
    uptodate_citations: int | None
    uptodate_mastheads: MastheadScan | None
    evidence_at_fault: int
    findings: tuple[Finding, ...]


# The title element of [apa7.md](skills/_shared/reference/apa7.md)
# section 2's published form, taken between the year element and the database
# element. **The database name is matched as a word and never as a hostname**,
# which is ``reference_scan``'s recorded defect adopted rather than
# rediscovered: without the lookahead an entry that drops the database element
# has its title read out of ``www.uptodate.com`` and a garbage string is then
# compared against the dump. Both spellings of the name are live -- section 2
# requires it italicized and records that the corpus italicizes it nowhere.
UPTODATE_TITLE = re.compile(
    r"\(\s*(?:n\.d\.|\d{4}[a-z]?)\s*\)\s*\.\s*"
    r"(?P<title>.+?)"
    r"\s*\.\s*[*_]{0,2}UpToDate[*_]{0,2}\s*\.(?=\s|$)",
    re.S | re.I,
)

# **A locator pointing at an UpToDate topic**, which is what tells this an entry
# was meant to be one when ``UPTODATE_TITLE`` could not read it. Matched as a
# **host** and never as a word -- the mirror of ``UPTODATE_TITLE``'s guard, and
# for the mirror reason: there the name in a URL must not be read as the database
# element, and here the name in a *title* must not be read as a locator. So it
# requires the scheme-or-``www`` run and the path that a real topic URL carries.
UPTODATE_LOCATOR = re.compile(r"(?i)\b(?:https?://|www\.)[\w.-]*\buptodate\.com/")

# What a finding names where the citation came from the draft rather than from a
# record. ``UNREADABLE_DRUG_ROW``'s ``a prescription table`` precedent: the
# ``claim`` slot is a record heading everywhere else, and a draft entry has none.
DRAFT_LIST = "the draft's reference list"


def accumulated_evidence_topics(store: Path | None = None) -> set[str]:
    """Every topic in a deliberate per-dump manifest, across courses."""
    try:
        return uptodate_store.entitled_topics(store)
    except ValueError as error:
        raise run_grader.SourceError(f"the UpToDate store is unreadable: {error}") from error


def uptodate_topic(entry: str) -> str:
    """Read the topic element from #231's UpToDate reference form."""
    match = UPTODATE_TITLE.search(entry)
    return " ".join(match.group("title").split()) if match else ""


def cited_uptodate_entries(
    records: list[Record], entries: tuple[str, ...]
) -> list[tuple[str, str, str, str]]:
    """One citation population shared by membership and currency checks."""
    citations = [(record.claim, record.value("REFERENCE")) for record in records]
    citations.extend((DRAFT_LIST, entry) for entry in entries)
    return [
        (claim, entry, title, uptodate_store.citation_title_key(title))
        for claim, entry in citations
        for title in (uptodate_topic(entry),)
    ]


APA_AUTHOR = re.compile(
    r"(?P<surname>[A-Za-z][^,&]*?),\s*"
    r"(?P<initials>(?:[A-Z](?:[-'][A-Z])?\.\s*)+)"
)
MASTHEAD_AUTHOR = re.compile(
    r"(?:(?P<surname>[A-Za-z][^,]*),\s*(?:[A-Z]\.\s*)+,\s*"
    r"(?P<last_degree>[A-Z][A-Za-z.]*)(?=,|$)"
    r"(?:,\s*[A-Z][A-Za-z.]*(?=,|$))*"
    r"|(?P<name>[A-Za-z][^,]*),\s*"
    r"(?P<degree>[A-Z][A-Za-z.]*)(?=,|$)"
    r"(?:,\s*[A-Z][A-Za-z.]*(?=,|$))*)"
)
MASTHEAD_LINE_BOUNDARY = re.compile(
    r"(?<=[A-Za-z.])\s+(?=[A-Z](?:\.?\s+)[A-Z][^,]*,\s*[A-Z])"
)


def _unmatched_author_text(text: str, matches: list[re.Match[str]]) -> str:
    """Anything outside parsed author members other than list separators."""
    pieces: list[str] = []
    end = 0
    for match in matches:
        pieces.append(text[end : match.start()])
        end = match.end()
    pieces.append(text[end:])
    residue = re.sub(r"(?i)\band\b", "", "".join(pieces))
    return re.sub(r"[\s,&]+", "", residue)


def _apa_surnames(entry: str) -> tuple[tuple[str, ...], bool]:
    year = YEAR.search(entry)
    author_element = entry[: year.start()] if year else entry
    matches = list(APA_AUTHOR.finditer(author_element))
    names = tuple(_normalize_name(match.group("surname")) for match in matches)
    return names, bool(names) and not _unmatched_author_text(author_element, matches)


def _masthead_names(authors: str) -> tuple[tuple[str, ...], bool]:
    authors = MASTHEAD_LINE_BOUNDARY.sub(", ", authors)
    matches = list(MASTHEAD_AUTHOR.finditer(authors))
    names = tuple(
        _normalize_name(match.group("surname") or match.group("name"))
        for match in matches
    )
    joined_name = any(
        re.search(r"(?i)\band\b", match.group("surname") or match.group("name"))
        for match in matches
    )
    return (
        names,
        bool(names) and not joined_name and not _unmatched_author_text(authors, matches),
    )


def _normalize_name(name: str) -> str:
    """Fold case and spacing while preserving surname punctuation."""
    return " ".join(name.casefold().split())


def _latest_stored_topics(
    details: tuple[uptodate_store.StoredTopic, ...],
) -> tuple[uptodate_store.StoredTopic, ...]:
    """Newest topic per citation-title normalization, with an explicit tie break."""
    stored: dict[str, uptodate_store.StoredTopic] = {}
    for topic in details:
        key = uptodate_store.citation_title_key(topic.title)
        prior = stored.get(key)
        if prior is None or (topic.received_on, topic.title) > (
            prior.received_on,
            prior.title,
        ):
            stored[key] = topic
    return tuple(stored[key] for key in sorted(stored))


def uptodate_masthead_findings(
    records: list[Record],
    entries: tuple[str, ...],
    details: tuple[uptodate_store.StoredTopic, ...],
) -> MastheadScan:
    """Compare cited UpToDate authors with the accumulated validated mastheads."""
    stored = {
        uptodate_store.citation_title_key(topic.title): topic
        for topic in _latest_stored_topics(details)
    }
    found: list[Finding] = []
    population = 0
    read = 0
    unread = 0
    for claim, entry, _title, key in cited_uptodate_entries(records, entries):
        topic = stored.get(key)
        if topic is None:
            continue
        population += 1
        surnames, apa_complete = _apa_surnames(entry)
        names, masthead_complete = _masthead_names(topic.authors)
        complete = apa_complete and masthead_complete
        if not complete:
            unread += 1
        else:
            read += 1
        if not complete or len(surnames) != len(names) or any(
            name != surname and not name.endswith(f" {surname}")
            for surname, name in zip(surnames, names)
        ):
            found.append(
                Finding(
                    UPTODATE_MASTHEAD_DISAGREES,
                    claim,
                    "the APA authors do not match the stored topic masthead",
                )
            )
        year = YEAR.search(entry)
        if year is None or year.group(1) != topic.last_updated[:4]:
            found.append(
                Finding(
                    UPTODATE_MASTHEAD_DISAGREES,
                    claim,
                    "the APA year does not match the stored topic's last-updated year",
                )
            )
    return MastheadScan(
        tuple(sorted(found, key=lambda finding: _KIND_ORDER[finding.kind])),
        population,
        read,
        unread,
    )


def read_records(text: str) -> list[Record]:
    """Every claim record in one ledger.

    A field's value runs to the next field line or the next claim heading, so an
    APA entry may wrap onto a hanging-indent continuation the way APA sets one. A
    line before the first claim heading belongs to no record and is dropped --
    the ``DATE:`` header lives there.
    """
    records: list[Record] = []
    claim: str | None = None
    fields: dict[str, str] = {}
    current: str | None = None

    def close() -> None:
        if claim is not None:
            records.append(Record(claim=claim, fields=dict(fields)))

    for line in text.splitlines():
        heading = CLAIM.match(line)
        if heading:
            close()
            claim, fields, current = heading.group(1), {}, None
            continue
        if claim is None:
            continue
        named = FIELD.match(line)
        if named:
            current = named.group(1).upper()
            fields[current] = named.group(2)
            continue
        if current and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    close()
    return records


def has_substantive_refutation(record: Record) -> bool:
    """Whether a recognized refutation gives a reason beyond the restatement."""
    verdict, reason = keyword_of(record.value("REFUTATION"), REFUTATION_VALUES)
    return bool(
        verdict
        and SUBSTANCE.search(reason)
        and normalize(reason) != normalize(record.value("RESTATEMENT"))
    )


def _sourceless_findings(record: Record) -> list[Finding]:
    """The sourceless status branches: a reason and no source-claim fields.

    An ``unsourced`` or ``unreadable`` record is not a failure --
    ``skills/practicum-case-study/SKILL.md`` step 3 routes it to ``PROPOSED``.
    What is refused is one that makes either sourceless claim while carrying a
    claim about a source.
    """
    claim = record.claim
    found: list[Finding] = []
    if not SUBSTANCE.search(keyword_of(record.value("STATUS"), STATUSES)[1]):
        found.append(Finding(BARE_STATUS, claim, record.value("STATUS")))
    for name in SOURCE_FIELDS:
        if SUBSTANCE.search(record.value(name)):
            found.append(Finding(SOURCELESS_WITH_SOURCE_FIELD, claim, f"{name}: {record.value(name)}"))
    return found


def _dropped_findings(record: Record) -> list[Finding]:
    """Validate the optional reason on #1021's dropped record."""
    if "DROPPED" not in record.fields:
        return []
    found = []
    if not SUBSTANCE.search(record.value("DROPPED")):
        found.append(Finding(BARE_DROPPED, record.claim, "DROPPED"))
    if record.status != SOURCED:
        found.append(
            Finding(
                DROPPED_ON_SOURCELESS_RECORD,
                record.claim,
                f"STATUS: {record.value('STATUS')}",
            )
        )
    return found


def _contract_findings(record: Record, source_classes: tuple[str, ...]) -> list[Finding]:
    """#214's rows for a sourced record: the fields, the class, the restatement.

    Takes no ``as_of``. Nothing #214 asks of a record is measured against a date,
    and the signature is where that is visible.
    """
    claim = record.claim
    found: list[Finding] = []

    for name in REQUIRED_WHEN_SOURCED:
        if not SUBSTANCE.search(record.value(name)):
            found.append(Finding(MISSING_FIELD, claim, name))

    source = normalize(record.value("SOURCE"))
    class_keys = frozenset(normalize(name) for name in source_classes)
    if source and source not in class_keys:
        found.append(Finding(UNKNOWN_SOURCE_CLASS, claim, record.value("SOURCE")))

    restatement = record.value("RESTATEMENT")
    if SUBSTANCE.search(restatement):
        if normalize(restatement) == normalize(claim):
            found.append(Finding(RESTATEMENT_ECHOES_CLAIM, claim, restatement))
        if DIGIT.search(claim) and not DIGIT.search(restatement):
            found.append(Finding(NUMERIC_CLAIM_UNQUANTIFIED, claim, restatement))
    return found


def _recency_findings(
    record: Record, as_of: date | None, recency_window_years: int
) -> list[Finding]:
    """#215's four rows: the disposition, the excuse, the year, the window.

    **The two blocks are one helper because they are one rule read twice.** The
    vocabulary keyword and its remainder are computed here and read by both -- the
    window row asks whether an excuse stands, which is the same ``keyword_of`` split
    the disposition row grades. Cutting between them would hand the second block a
    value it did not derive, which is the sharing
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242) found
    and the reason the seam is here rather than at the six blocks it counted.

    One row here reads ``as_of``: ``STALE_UNEXCUSED``. ``None`` means the ledger
    stated no date, so the window is skipped and the other three still run.
    """
    claim = record.claim
    found: list[Finding] = []

    recency = record.value("RECENCY")
    excuse, remainder = keyword_of(recency, RECENCY_VALUES)
    if SUBSTANCE.search(recency) and not excuse:
        # ``STATUS``'s reasoning and not ``SOURCE``'s: this field gates the window
        # row below it, so a fifth disposition is a record the window never read.
        found.append(Finding(UNKNOWN_RECENCY, claim, recency))
    if excuse in EXCUSES and not SUBSTANCE.search(remainder):
        found.append(Finding(BARE_EXCUSE, claim, recency))

    if SUBSTANCE.search(record.value("REFERENCE")):
        year = record.reference_year
        excused = excuse in EXCUSES and SUBSTANCE.search(remainder)
        if year is None:
            # ``n.d.`` is legitimate APA. What is refused is an undated source with
            # nothing said about why it stands -- the clinician's own escape hatch,
            # rather than a blanket rule he never made.
            if not excused:
                found.append(Finding(UNDATED_REFERENCE, claim, record.value("REFERENCE")))
        elif as_of is not None and as_of.year - year > recency_window_years and excuse not in EXCUSES:
            detail = f"{year}, RECENCY: {recency}"
            found.append(Finding(STALE_UNEXCUSED, claim, detail))
    return found


def _citation_findings(record: Record, as_of: date | None) -> list[Finding]:
    """#231's ten rows: the locator, the page year, the refutation.

    **Self-contained, which is what made the seam worth cutting on
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242).** These
    rows share nothing with #214's and #215's but the record itself -- the echo row
    re-reads ``RESTATEMENT`` off the record rather than being handed it, so no value
    crosses the boundary.

    One row here reads ``as_of``: ``READ_AFTER_DATE``. With
    ``_recency_findings``'s window and ``_stated_expiry_findings`` those are the
    three rows in the module measured against a date, and the helper signatures
    are where a reader sees them.

    These rows require the recorded specifics that make the separate source read
    checkable in one click; #231 records the declined resolver design.
    """
    claim = record.claim
    found: list[Finding] = []

    # #231's first half: the agent was on the page, so it writes down where it was
    # and when.
    resolved = record.value("RESOLVED")
    if SUBSTANCE.search(resolved):
        if not LOCATOR.search(resolved):
            found.append(Finding(UNRESOLVABLE_LOCATOR, claim, resolved))
        read = record.read_date
        if read is None:
            found.append(Finding(UNDATED_READ, claim, resolved))
        elif as_of is not None and read > as_of:
            # The second row measured against ``DATE``, and the second one a
            # dateless ledger loses. Reading a source after the paper was written
            # is a record describing something that had not happened yet.
            found.append(Finding(READ_AFTER_DATE, claim, f"read {read.isoformat()}, DATE {as_of}"))

    # **One rule in three rows: the page and the entry agree about the year.** An
    # ``n.d.`` entry beside a page that states no year is the agreeing case and
    # passes -- refusing it would refuse legitimate APA, which is the mistake
    # ``UNDATED_REFERENCE`` was already corrected for once.
    stated = record.value("PAGE-YEAR")
    if SUBSTANCE.search(stated):
        page_year = record.page_year
        entry_year = record.reference_year
        cited = bool(SUBSTANCE.search(record.value("REFERENCE")))
        if page_year is None:
            if cited and entry_year is not None:
                found.append(Finding(PAGE_YEAR_UNSTATED, claim, stated))
        else:
            # Two things rather than one, on ``BARE_EXCUSE``'s reasoning: a year
            # alone is an assertion, a year with where it was found is a place a
            # reader can go and look.
            if not SUBSTANCE.search(BARE_YEAR.sub(" ", stated, count=1)):
                found.append(Finding(BARE_PAGE_YEAR, claim, stated))
            if cited and page_year != entry_year:
                entry = entry_year if entry_year is not None else "no year"
                found.append(
                    Finding(PAGE_YEAR_DISAGREES, claim, f"{page_year} on the page, {entry} in REFERENCE")
                )

    # #231's second half grades the refutation record shape; the skill owns the
    # second-agent workflow.
    refutation = record.value("REFUTATION")
    if SUBSTANCE.search(refutation):
        verdict, reason = keyword_of(refutation, REFUTATION_VALUES)
        if not verdict:
            # ``STATUS``'s reasoning again: it gates the row below, so an
            # unrecognized word is a record the refutation row never read.
            found.append(Finding(UNKNOWN_REFUTATION, claim, refutation))
        else:
            if not has_substantive_refutation(record):
                if not SUBSTANCE.search(reason):
                    found.append(Finding(BARE_REFUTATION, claim, refutation))
                else:
                    # The first agent re-asserting rather than a second one checking.
                    # ``RESTATEMENT_ECHOES_CLAIM``'s trick, one level up.
                    found.append(Finding(REFUTATION_ECHOES_RESTATEMENT, claim, refutation))
            if verdict == REFUTATION_REFUTED:
                # A **failure**, unlike ``unsourced``, which the skill routes to
                # ``PROPOSED`` honestly. This is a false citation sitting in the
                # ledger: the run rewrites the record or writes ``unsourced``.
                found.append(Finding(REFUTED_CITATION, claim, refutation))

    return found


def _second_route_findings(record: Record) -> list[Finding]:
    """#500's three rows over the declared two-half route difference."""
    claim = record.claim
    found: list[Finding] = []
    # The separator is a declared difference between two routes, not a
    # vocabulary: an honest combined pass has one route, writes it twice, and
    # fails the normalized equality check. ``partition`` preserves any further
    # arrows in the second half instead of inventing a third slot.
    second_route = record.value("SECOND-ROUTE")
    if SUBSTANCE.search(second_route):
        first, separator, second = second_route.partition("->")
        if not separator:
            found.append(Finding(UNSPLIT_SECOND_ROUTE, claim, second_route))
        elif not SUBSTANCE.search(first) or not SUBSTANCE.search(second):
            found.append(Finding(BARE_SECOND_ROUTE, claim, second_route))
        elif normalize(first) == normalize(second):
            found.append(Finding(SECOND_ROUTE_UNCHANGED, claim, second_route))

    return found


def _tested_heading_findings(record: Record) -> list[Finding]:
    """ADR 0219's exact binding between a refutation and its current heading."""
    tested = record.value("TESTED-HEADING")
    if not SUBSTANCE.search(tested):
        return []  # The shared required-field row owns absence.
    if not SHA256.fullmatch(tested):
        return [Finding(MALFORMED_TESTED_HEADING, record.claim, tested)]
    expected = heading_digest(record.claim)
    if tested.casefold() != expected:
        return [
            Finding(
                TESTED_HEADING_MISMATCH,
                record.claim,
                f"recorded {tested}, current {expected}",
            )
        ]
    return []


def _instrument_findings(record: Record) -> list[Finding]:
    """ADR 0149's three rows over the failed-read instrument pair."""
    claim = record.claim
    found: list[Finding] = []
    instruments = record.value("INSTRUMENTS")
    if SUBSTANCE.search(instruments):
        first, separator, second = instruments.partition("->")
        if not separator:
            found.append(Finding(UNSPLIT_INSTRUMENTS, claim, instruments))
        elif not SUBSTANCE.search(first) or not SUBSTANCE.search(second):
            found.append(Finding(BARE_INSTRUMENTS, claim, instruments))
        elif normalize(first) == normalize(second):
            found.append(Finding(INSTRUMENTS_UNCHANGED, claim, instruments))
    return found


def _stated_expiry_findings(record: Record, as_of: date | None) -> list[Finding]:
    """#498's grammar and expiry comparison against the ledger header."""
    claim = record.claim
    found: list[Finding] = []
    # The page states a date and where it states it; the grader compares
    # that transcription with the ledger's DATE header, never with the clock.
    stated_expiry = record.value("STATED-EXPIRY")
    if SUBSTANCE.search(stated_expiry):
        expiry, superseded, recognized = stated_expiry_of(stated_expiry)
        if not recognized:
            found.append(Finding(UNKNOWN_STATED_EXPIRY, claim, stated_expiry))
        elif expiry is not None and not superseded and as_of is not None and expiry <= as_of:
            found.append(
                Finding(
                    STATED_EXPIRY_REACHED,
                    claim,
                    f"stated expiry {expiry.isoformat()}, DATE {as_of.isoformat()}",
                )
            )
    return found


def record_findings(
    record: Record,
    as_of: date | None,
    *,
    source_classes: tuple[str, ...] | None = None,
    recency_window_years: int | None = None,
) -> list[Finding]:
    """Every row this record fails, in ``KINDS`` order. A record can fail several.

    ``as_of`` of ``None`` means the ledger stated no date, so the window row and the
    read-date row are skipped and every other row still runs --
    ``differential_scan.py``'s ordering, where a finding outranks an incomplete scan.

    **The rows live in helpers and the branching lives here**, on
    ``reference_scan.py``'s arrangement -- the sibling with a comparable row count,
    and the one
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242) did not
    check when it wrote that every other scanner keeps one grader. What stays here is
    the control flow the helpers cannot be written without: a record with no
    recognized ``STATUS`` is graded on nothing below it, and the two sourceless
    statuses are graded on a different set entirely.

    **Sorted by ``KINDS`` rather than by append order**, so where a helper is called
    is not something a reader of this record's findings can see. The counts were
    already ordered that way and the finding list was not, and this is what lets a
    seam move again without a report changing shape.

    **Per record, and ``survey`` does not re-sort across them.** A ledger's findings
    stay grouped by the record that raised them, which is what ``--show`` should
    print; the guarantee here is about one record's rows and no wider.
    """
    found: list[Finding] = []
    claim = record.claim
    if source_classes is None:
        source_classes = SOURCE_CLASS_VOCABULARY[:-1]
    if recency_window_years is None:
        recency_window_years = 5

    if not SUBSTANCE.search(claim):
        found.append(Finding(MISSING_FIELD, claim, "CLAIM"))

    status = record.status
    found += _dropped_findings(record)
    if not status:
        # Unlike an unrecognized ``SPECIFICITY`` keyword, this one is a failure:
        # the branch decides which tests below run, so a record wearing an
        # unrecognized word is graded on nothing at all and prints as clean.
        found.append(Finding(UNKNOWN_STATUS, claim, record.value("STATUS")))
    elif status in (UNSOURCED, UNREADABLE):
        found += _sourceless_findings(record)
    else:
        found += _contract_findings(record, source_classes)
        found += _recency_findings(record, as_of, recency_window_years)
        found += _citation_findings(record, as_of)
        found += _tested_heading_findings(record)
        found += _second_route_findings(record)
        found += _stated_expiry_findings(record, as_of)

    refutation = keyword_of(record.value("REFUTATION"), REFUTATION_VALUES)[0]
    instruments_required = status == UNREADABLE or refutation == REFUTATION_UNREADABLE
    if instruments_required and not SUBSTANCE.search(record.value("INSTRUMENTS")):
        found.append(Finding(MISSING_FIELD, claim, "INSTRUMENTS"))
    elif instruments_required:
        found += _instrument_findings(record)
    elif "INSTRUMENTS" in record.fields:
        found.append(Finding(UNEXPECTED_INSTRUMENTS, claim, record.value("INSTRUMENTS")))

    # Stable, so two findings of one kind keep the order their helper appended them in.
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind])


def _cells(line: str) -> list[str]:
    r"""The cells of one Markdown table row, unwrapped from their backticks.

    **The split is the renderer's own**, imported rather than restated, on
    ``reference_scan.py``'s ``REFERENCE_HEADING`` precedent and for its reason:
    ``docx_write.split_row`` is what decides where a cell ends in the document
    a grader actually reads, and a second reading of one table can put the
    ``Disp:`` anchor in a different row than the one that renders. It honors an
    escaped ``\|`` as a literal pipe; a copy here would not, and #215's follow-up
    is the recorded instance of that exact divergence costing a rendered cell.

    **A row's cell count varies by design and nothing here reads it.** Since
    #293 that table is three columns wide: row 1 declares three cells, the drug,
    ``Disp:``, ``Sig:`` and signature rows declare one and span, and the last
    declares two.

    The backticks are this module's own business -- ``style.md`` sets every cell
    of that table as code, and the renderer keeps them because they are content.
    """
    return [cell.strip("`").strip() for cell in split_row(line)]


def _declaration_of(order: str) -> tuple[str, str]:
    """Split a drug row into what it declares about itself and the order.

    **The boundary is #253's**, arriving at the declarations: a value merely
    *opening* with a vocabulary word is not that word, so ``Continued home
    medications reviewed:`` does not exempt the row it opens. The separator is a
    colon, which is what ``style.md`` section 8 writes.
    """
    lowered = order.lower()
    for name in sorted(DRUG_ROW_DECLARATIONS, key=len, reverse=True):
        if not lowered.startswith(name):
            continue
        rest = order[len(name) :].lstrip()
        if rest.startswith(":"):
            return name, rest[1:].strip()
    return "", order


def _drug_of(order: str) -> str:
    """Parse the medication identifier with ``DRUG_NAME``."""
    tokens = order.split()
    if not tokens:
        return ""
    token = tokens[0].strip(",;.:()")
    return token if DRUG_NAME.fullmatch(token) else ""


def _table_runs(text: str) -> list[list[list[str]]]:
    """Every Markdown table in ``text``, as rows of cells.

    **The blocks are the renderer's own**, imported rather than walked here, on
    ``_cells``'s reasoning one level up: ``docx_write.markdown_tables`` is what
    decides where a table begins and ends in the document a grader reads, and its
    own docstring refuses a second copy of the loop in as many words. This module
    had one -- written a day before that function existed, on a branch that could
    not see it -- and the two disagreed about what a table *is*: this required
    only consecutive rows and that requires a separator rule under the header, so
    a block the renderer would set as paragraphs was a prescription table here.
    Caught at the merge and by nothing either suite ran.
    """
    return [
        [_cells(line) for line in block.splitlines() if line.strip()]
        for block in markdown_tables(text)
    ]


def read_prescriptions(text: str) -> list[Prescription]:
    """Every drug row in every prescription table of a draft.

    A prescription table is a run of consecutive Markdown table lines carrying
    both a ``Disp:`` cell and a ``Sig:`` cell, and the drug row is the row above
    ``Disp:``. Any other table in the document -- the differential, the MDM, the
    faculty's questions -- carries neither and is not read.

    A pair with no readable row above ``Disp:`` yields the empty sentinel consumed
    by ``UNREADABLE_DRUG_ROW``.
    """
    return [rx for rows in _table_runs(text) for rx in _prescriptions_in(rows)]


def half_anchored_tables(text: str) -> int:
    """Count one-anchor table runs for #204's partial-read census."""
    return sum(
        1
        for rows in _table_runs(text)
        if any(DISP.match(c) for cells in rows for c in cells)
        != any(SIG.match(c) for cells in rows for c in cells)
    )


def _prescriptions_in(rows: list[list[str]]) -> list[Prescription]:
    """The drug rows of one run of table lines, empty where it is not a table of
    prescriptions."""
    opened = [index for index, cells in enumerate(rows) if any(DISP.match(c) for c in cells)]
    if not opened or not any(SIG.match(c) for cells in rows for c in cells):
        return []
    found: list[Prescription] = []
    for index in opened:
        above = rows[index - 1] if index else []
        order = next(
            (
                cell
                for cell in above
                if cell and not SEPARATOR_CELL.match(cell) and not DISP.match(cell)
            ),
            "",
        )
        declaration, order = _declaration_of(order)
        found.append(Prescription(_drug_of(order), order, declaration))
    return found


def _records_naming(drug: str, records: list[Record]) -> list[Record]:
    """Every claim heading naming this drug, as a word rather than as a prefix."""
    word = re.compile(rf"(?i)(?<![0-9A-Za-z]){re.escape(drug)}(?![0-9A-Za-z])")
    return [record for record in records if word.search(record.claim)]


def prescription_findings(
    prescriptions: list[Prescription], records: list[Record]
) -> list[Finding]:
    """Apply #289's draft-derived prescription joins.

    The set comes from the authored document on ``checks_ledger.py``'s expected-set
    precedent. Clinical dose judgment remains with the ``practicum-case-study``
    step-9 reader because it depends on indication, weight, renal function,
    pregnancy, and route.
    """
    found: list[Finding] = []
    for rx in prescriptions:
        if rx.exempt:
            continue
        if not rx.drug:
            found.append(
                Finding(
                    UNREADABLE_DRUG_ROW,
                    "a prescription table",
                    "carries Disp: and Sig: with no readable drug row above Disp:",
                )
            )
            continue
        naming = _records_naming(rx.drug, records)
        if not naming:
            found.append(
                Finding(
                    UNRESEARCHED_PRESCRIPTION,
                    rx.drug,
                    "prescribed in the draft, and no claim record names it",
                )
            )
            continue
        if rx.states_a_dose and not any(DIGIT.search(record.claim) for record in naming):
            found.append(
                Finding(
                    DOSE_NOT_CLAIMED,
                    rx.drug,
                    "the order states a dose and no claim record naming the drug states a number",
                )
            )
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind])


REFERENCE_IDENTITY_YEAR = re.compile(
    r"\(\s*(?P<year>" + YEAR_TOKEN + r")\s*(?:,[^)]*)?\)", re.I
)
CONTAINER_WORD = re.compile(
    r"\b(?:bmj|jama|journal|nejm|press|proceedings|review|uptodate)\b", re.I
)
REFERENCE_RETRIEVAL = re.compile(r"\bretrieved\b.*$", re.I | re.S)
REFERENCE_LOCATOR = re.compile(r"(?:https?://|\bdoi\s*:\s*)\S+", re.I)
TITLE_ABBREVIATIONS = frozenset(
    {
        "dr",
        "e.g",
        "etc",
        "fig",
        "i.e",
        "inc",
        "jr",
        "mr",
        "mrs",
        "ms",
        "prof",
        "sr",
        "st",
        "vs",
    }
)


def _reference_title(reference: str, start: int) -> str:
    """Read the APA title, preserving periods in initialisms and abbreviations."""
    remainder = reference[start:].lstrip(". \t")
    remainder = REFERENCE_RETRIEVAL.sub("", remainder)
    remainder = REFERENCE_LOCATOR.sub("", remainder).rstrip(". \t")
    for period in re.finditer(r"\.", remainder):
        if (
            period.start() > 0
            and period.end() < len(remainder)
            and remainder[period.start() - 1].isdigit()
            and remainder[period.end()].isdigit()
        ):
            continue
        before = re.search(r"([A-Za-z]+)$", remainder[: period.start()])
        token = before.group(1) if before is not None else ""
        prior = remainder[: period.start()]
        dotted = re.search(r"(?:[A-Za-z]\.)+[A-Za-z]$", prior)
        next_element = remainder[period.end() :].split(".", 1)[0]
        continuation = next_element.lstrip()
        abbreviation = (
            len(token) == 1 or token.casefold() in TITLE_ABBREVIATIONS or dotted
            or bool(continuation and continuation[0].islower())
        )
        container_starts = bool(
            continuation
            and continuation[0].isupper()
            and (
                CONTAINER_WORD.search(next_element)
                or re.search(r",\s*(?:\d|\()", next_element)
            )
        )
        if abbreviation and not container_starts and continuation:
            continue
        return prior
    return remainder


def reference_identity(reference: str) -> tuple[str, str, str] | None:
    """Normalized APA author phrase, bare year, and title."""
    matched = REFERENCE_IDENTITY_YEAR.search(reference)
    if matched is None:
        return None
    token = year_key(matched.group("year"))
    if token.startswith("nd"):
        bare_year = "nd"
    elif token.startswith("inpress"):
        bare_year = "inpress"
    else:
        bare_year = re.sub(r"[a-z]$", "", token)
    title = _reference_title(reference, matched.end())
    if not SUBSTANCE.search(title):
        return None
    return normalize(reference[: matched.start()]), bare_year, normalize(title)


@dataclass(frozen=True)
class ReferenceIdentity:
    author: str
    year: str
    title: str
    container: str | None
    fallback: bool = False


def reference_identities(reference: str) -> frozenset[ReferenceIdentity]:
    """Return the title identity and a bounded alias for an opaque final container.

    Plain-text APA loses the italics that distinguish a title ending in an
    initialism from its container.  When the ordinary parser finds no container
    at all, admit the final sentence element as an opaque container. Its
    normalized value must equal the other side's container when the alias is
    used. Where both titles read ordinarily, key and title alone decide the
    match; their containers do not.
    """
    identity = reference_identity(reference)
    if identity is None:
        return frozenset()
    matched = REFERENCE_IDENTITY_YEAR.search(reference)
    assert matched is not None
    remainder = reference[matched.end() :].lstrip(". \t")
    remainder = REFERENCE_RETRIEVAL.sub("", remainder)
    remainder = REFERENCE_LOCATOR.sub("", remainder).rstrip(". \t")
    title = _reference_title(reference, matched.end())
    container = None
    if normalize(title) != normalize(remainder):
        container = normalize(remainder[len(title) :].lstrip(". \t").split(",", 1)[0])
    identities = {ReferenceIdentity(*identity, container)}
    if normalize(title) == normalize(remainder):
        opaque = re.fullmatch(
            r"(?P<title>.+\b(?P<end>[A-Za-z.]+)\.)\s+[^.\r\n]+",
            remainder,
        )
        if opaque is not None:
            end = opaque.group("end")
            dotted = re.fullmatch(r"(?:[A-Za-z]\.)+[A-Za-z]", end)
            token = end.rsplit(".", 1)[-1].casefold()
            alias = normalize(opaque.group("title"))
            recognized_end = bool(
                dotted or len(token) == 1 or token in TITLE_ABBREVIATIONS
            )
            if recognized_end and SUBSTANCE.search(alias):
                identities.add(
                    ReferenceIdentity(
                        identity[0], identity[1], alias,
                        normalize(remainder[len(opaque.group("title")) :]), True,
                    )
                )
    return frozenset(identities)


def _reference_identities_match(left: ReferenceIdentity, right: ReferenceIdentity) -> bool:
    if (left.author, left.year, left.title) != (right.author, right.year, right.title):
        return False
    return not (left.fallback or right.fallback) or (
        left.container is not None and left.container == right.container
    )


def draft_reference_findings(
    records: list[Record], entries: tuple[str, ...]
) -> list[Finding]:
    """Require each non-dropped sourced record's source in the draft list."""
    listed = {identity for entry in entries for identity in reference_identities(entry)}
    found = []
    for record in records:
        if record.status != SOURCED or "DROPPED" in record.fields:
            continue
        identities = reference_identities(record.value("REFERENCE"))
        if not any(
            _reference_identities_match(identity, listed_identity)
            for identity in identities
            for listed_identity in listed
        ):
            found.append(
                Finding(
                    SOURCED_RECORD_NOT_LISTED,
                    record.claim,
                    "the sourced record's reference is absent from the draft reference list",
                )
            )
    return sorted(found, key=lambda finding: _KIND_ORDER[finding.kind])


def evidence_findings(
    records: list[Record],
    entries: tuple[str, ...],
    carried: set[str],
) -> tuple[list[Finding], int]:
    """Apply #298's citation-to-carried-topic join.

    The clinician deliberately ingests complete topic bodies, so a cited
    UpToDate topic joins against the accumulated manifest set. Findings
    de-duplicate by topic because two citations name one missing artifact.
    """
    keys = {uptodate_store.citation_title_key(title) for title in carried}
    found: list[Finding] = []
    seen: set[str] = set()
    read = 0
    for claim, entry, title, key in cited_uptodate_entries(records, entries):
        if not key:
            # Preserve an unreadable UpToDate-shaped entry in the population and
            # report it on ``UNREADABLE_DRUG_ROW``'s fail-visible precedent.
            if UPTODATE_LOCATOR.search(entry):
                read += 1
                found.append(
                    Finding(
                        UNREADABLE_UPTODATE_ENTRY,
                        claim,
                        "the locator names an UpToDate topic and the entry states"
                        " no database element, so no title could be read",
                    )
                )
            continue
        # Counted before the join and before the de-duplication, because this is
        # the row's **population**: what it read, not what it failed. Derived from
        # the one walk rather than counted a second time, so the figure and the
        # findings cannot come to disagree about what was scanned.
        read += 1
        if key in keys or key in seen:
            continue
        seen.add(key)
        found.append(Finding(CITED_TOPIC_NOT_IN_EVIDENCE, claim, title))
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind]), read


def uptodate_reread_findings(
    records: list[Record],
    entries: tuple[str, ...],
    currency_by_topic: dict[str, str],
    as_of: date | None,
    *,
    window_years: int,
    has_account: bool,
) -> list[Finding]:
    """Require a fresh read once the publisher's review month leaves the bar window."""
    if as_of is None or not has_account:
        return []
    currency = {
        uptodate_store.citation_title_key(title): stamp
        for title, stamp in currency_by_topic.items()
    }
    found: list[Finding] = []
    seen: set[str] = set()
    for claim, _entry, title, key in cited_uptodate_entries(records, entries):
        stamp = currency.get(key)
        if not key or stamp is None or key in seen:
            continue
        seen.add(key)
        try:
            reviewed_year, reviewed_month = (int(part) for part in stamp.split("-", 1))
        except (TypeError, ValueError):
            continue
        if (as_of.year, as_of.month) > (reviewed_year + window_years, reviewed_month):
            found.append(
                Finding(
                    UPTODATE_REREAD_DUE,
                    claim,
                    f"{title}; literature review current through {stamp}",
                )
            )
    return sorted(found, key=lambda finding: _KIND_ORDER[finding.kind])


def _stated_expiry_unscanned(records: Iterable[Record]) -> bool:
    """Whether sourced records all predate #498's required field."""
    sourced = [record for record in records if record.status == SOURCED]
    return bool(sourced) and not any("STATED-EXPIRY" in record.fields for record in sourced)


def survey(
    records: list[Record],
    as_of: date | None,
    prescriptions: list[Prescription] | None = None,
    half_anchored: int = 0,
    carried: set[str] | None = None,
    entries: tuple[str, ...] = (),
    *,
    source_classes: tuple[str, ...] | None = None,
    recency_window_years: int | None = None,
    uptodate_currency: dict[str, str] | None = None,
    uptodate_details: tuple[uptodate_store.StoredTopic, ...] | None = None,
    uptodate_recency_window_years: int = 2,
    uptodate_has_account: bool = True,
    evidence_ungraded_reason: str | None = None,
) -> Scan:
    """Count across one ledger.

    Takes parsed records rather than paths, so the counts carry no provenance of
    their own. The ledger's **name** is printed by ``format_report`` the way every
    sibling prints a run directory's -- the name, never the path.
    """
    if source_classes is None:
        source_classes = SOURCE_CLASS_VOCABULARY[:-1]
    if recency_window_years is None:
        recency_window_years = 5
    graded = [
        (
            record,
            record_findings(
                record,
                as_of,
                source_classes=source_classes,
                recency_window_years=recency_window_years,
            ),
        )
        for record in records
    ]
    sourced = [record for record in records if record.status == SOURCED]
    stated_expiry_unscanned = _stated_expiry_unscanned(sourced)
    if stated_expiry_unscanned:
        # The whole-ledger retired shape is coverage failure, not one repeated
        # missing-field finding per record. Other findings remain and outrank
        # the banner at the command seam.
        graded = [
            (
                record,
                [
                    finding
                    for finding in findings
                    if not (
                        finding.kind == MISSING_FIELD
                        and finding.detail == "STATED-EXPIRY"
                    )
                ],
            )
            for record, findings in graded
        ]
    # The prescription rows lead, in the findings as well as in the counts:
    # they are their own group rather than one more row of a record, and
    # ``--show`` and the count column have to agree about the order.
    on_the_draft = prescription_findings(prescriptions or [], records)
    # The evidence row leads, on the prescription rows' reasoning: it is its
    # own group rather than one more row of a record, and ``--show`` and the
    # count column have to agree about the order.
    on_the_evidence, uptodate_read = (
        ([], None)
        if carried is None
        else evidence_findings(records, entries, carried)
    )
    if carried is not None and uptodate_currency is not None:
        on_the_evidence += uptodate_reread_findings(
            records,
            entries,
            uptodate_currency,
            as_of,
            window_years=uptodate_recency_window_years,
            has_account=uptodate_has_account,
        )
        on_the_evidence.sort(key=lambda finding: _KIND_ORDER[finding.kind])
    mastheads = None
    if carried is not None and uptodate_details is not None:
        mastheads = uptodate_masthead_findings(records, entries, uptodate_details)
        on_the_evidence += list(mastheads.findings)
        on_the_evidence.sort(key=lambda finding: _KIND_ORDER[finding.kind])
    on_the_draft_references = (
        draft_reference_findings(records, entries) if prescriptions is not None else []
    )
    found = (
        on_the_evidence
        + on_the_draft_references
        + on_the_draft
        + [f for _, per_record in graded for f in per_record]
    )
    return Scan(
        as_of=as_of,
        records=len(records),
        sourced=len(sourced),
        unsourced=sum(1 for r in records if r.status == UNSOURCED),
        unreadable=sum(1 for r in records if r.status == UNREADABLE),
        unrecognized_status=sum(1 for r in records if not r.status),
        by_class=tuple(
            (name, sum(1 for r in sourced if normalize(r.value("SOURCE")) == normalize(name)))
            for name in source_classes
        ),
        outside_vocabulary=sum(
            1
            for r in sourced
            if normalize(r.value("SOURCE"))
            not in frozenset(normalize(name) for name in source_classes)
        ),
        recency_window_years=recency_window_years,
        standing_past_window=sum(
            1 for r in sourced if keyword_of(r.value("RECENCY"), RECENCY_VALUES)[0] in EXCUSES
        ),
        behind_a_paywall=sum(
            1
            for r in sourced
            if keyword_of(r.value("REFUTATION"), REFUTATION_VALUES)[0] == REFUTATION_PAYWALLED
        ),
        unreadable_refutations=sum(
            1
            for r in sourced
            if keyword_of(r.value("REFUTATION"), REFUTATION_VALUES)[0]
            == REFUTATION_UNREADABLE
        ),
        stated_expiries=sum(
            1
            for r in sourced
            if (parsed := stated_expiry_of(r.value("STATED-EXPIRY")))[2]
            and parsed[0] is not None
        ),
        superseded_deliberately=sum(
            1
            for r in sourced
            if (parsed := stated_expiry_of(r.value("STATED-EXPIRY")))[2]
            and parsed[1]
        ),
        counts=tuple((kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS),
        failing_records=sum(1 for _, per_record in graded if per_record),
        prescriptions=None if prescriptions is None else len(prescriptions),
        continued_home=sum(1 for rx in prescriptions or [] if rx.exempt),
        half_anchored=half_anchored,
        prescriptions_at_fault=len(on_the_draft),
        draft_references_at_fault=len(on_the_draft_references),
        evidence_topics=None if carried is None else len(carried),
        evidence_ungraded_reason=evidence_ungraded_reason,
        uptodate_citations=uptodate_read,
        uptodate_mastheads=mastheads,
        evidence_at_fault=len(on_the_evidence),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no claim text unless ``show``."""
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console where anything outside cp1252 reads like corruption in the
    # one output meant to be pasted.
    lines = [
        f"research ledger over {source}, as of {scan.as_of.isoformat()}"
        if scan.as_of
        else f"research ledger over {source}, NO DATE HEADER - the window was {NOT_GRADED}",
        "",
        f"  claim records read               {scan.records}",
        f"    sourced                        {scan.sourced}",
        f"    unsourced - go to PROPOSED     {scan.unsourced}",
        f"    unreadable - go to PROPOSED    {scan.unreadable}",
        f"    neither status                 {scan.unrecognized_status}",
        "",
    ]
    for name, count in scan.by_class:
        lines.append(f"    {name:<30} {count}")
    lines.append(f"    {'outside the vocabulary':<30} {scan.outside_vocabulary}")
    lines.append("")
    lines.append(
        f"  standing past {scan.recency_window_years} years"
        f"         {scan.standing_past_window}"
    )
    lines.append(f"  citations behind a paywall       {scan.behind_a_paywall}")
    lines.append(f"  unreadable refutations           {scan.unreadable_refutations}")
    lines.append(
        "  stated expiry                     "
        f"{scan.stated_expiries} of {scan.sourced} sourced records name a date"
    )
    lines.append(
        f"  superseded cited deliberately     {scan.superseded_deliberately}"
    )
    lines.append("")
    # **The coverage line, and it prints on every run rather than only a short
    # one.** #258's ruling: a reader who has learned to read the qualifier
    # takes its absence as the stronger claim, so the run that graded no
    # prescriptions says so on the same page as its clean exit.
    if scan.prescriptions is None:
        lines.append(
            f"  {'prescription drug rows':<32} {NOT_GRADED} - no --draft was given"
        )
    else:
        lines.append(f"  prescription drug rows           {scan.prescriptions}")
        lines.append(
            f"    continued unchanged, exempt    {scan.continued_home}"
        )
        lines.append(
            f"    needing a claim record         {scan.prescriptions - scan.continued_home}"
        )
        # Printed on every graded run rather than only a short one, on #258's
        # reasoning: a reader who has learned to read the qualifier takes its
        # absence as the stronger claim.
        lines.append(
            f"    tables read with one anchor    {scan.half_anchored}  ({NOT_GRADED})"
        )
    # The population this row joined against, on #258's ruling and for its
    # reason: a reader who has learned to read the qualifier takes its absence as
    # the stronger claim, so the run that graded no citation says so on the same
    # page as its clean exit.
    if scan.evidence_topics is None:
        reason = scan.evidence_ungraded_reason or "no --evidence was given"
        lines.append(
            f"  {'evidence topics carried':<32} {NOT_GRADED} - {reason}"
        )
    else:
        lines.append(f"  {'evidence topics carried':<32} {scan.evidence_topics}")
    if scan.uptodate_citations is None:
        reason = scan.evidence_ungraded_reason or "no --evidence was given"
        lines.append(
            f"  {'UpToDate citations read':<32} {NOT_GRADED} - {reason}"
        )
    else:
        # What the row read, beside what it read against. Both, because either
        # alone reads as the stronger claim: a count of topics carried says
        # nothing about whether a single citation was joined to them.
        lines.append(f"  {'UpToDate citations read':<32} {scan.uptodate_citations}")
    if not isinstance(scan.uptodate_mastheads, MastheadScan):
        lines.append(
            f"  {'UpToDate author mastheads read':<32} {NOT_GRADED} - no stored citation was joined"
        )
    else:
        lines.append(
            f"  {'UpToDate author mastheads read':<32} {scan.uptodate_mastheads.read}"
            f" of {scan.uptodate_mastheads.population}; unread {scan.uptodate_mastheads.unread}"
            " (APA Surname, initials / masthead Name, degree)"
        )
    lines.append("")
    for kind, count in scan.counts:
        # Wide enough for the longest kind, so the count column stays a column.
        # ``refutation-echoes-restatement`` is 29 and overflowed 28 on the day it
        # was added, which is the report going ragged in the one output meant to
        # be pasted into a ticket.
        # A #289 row that did not run prints as such rather than as a zero,
        # for the reason ``Scan.prescriptions`` is not an ``int``.
        shown = count
        if scan.prescriptions is None and (
            kind in DRAFT_ROWS or kind == SOURCED_RECORD_NOT_LISTED
        ):
            shown = NOT_GRADED
        if (
            scan.evidence_topics is None or scan.uptodate_citations is None
        ) and kind in EVIDENCE_ROWS:
            shown = NOT_GRADED
        lines.append(f"  {ROWS[kind]} - {kind:<31} {shown}")
    lines.append("")
    lines.append(f"  records at fault                 {scan.failing_records}")
    if scan.prescriptions is not None:
        lines.append(
            f"  prescriptions at fault           {scan.prescriptions_at_fault}"
        )
    if scan.evidence_topics is not None:
        lines.append(
            f"  evidence findings at fault       {scan.evidence_at_fault}"
        )
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<26} {finding.claim}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


# One string, so the usage line and the flags cannot drift apart.
USAGE = (
    "usage: research_ledger.py <a ledger file> [--draft <a draft .md>]"
    " [--evidence <the evidence dump>] [--show] |"
    " research_ledger.py <a ledger file> --heading-digests"
)


@dataclass(frozen=True)
class Source:
    path: Path
    records: tuple[Record, ...]
    as_of: date | None
    prescriptions: tuple[Prescription, ...] | None
    half_anchored: int
    carried: set[str] | None
    entries: tuple[str, ...]
    evidence_not_filed: bool
    stated_expiry_unscanned: bool
    draft_name: str | None
    evidence_name: str | None
    source_classes: tuple[str, ...]
    recency_window_years: int
    uptodate_currency: dict[str, str] | None
    uptodate_details: tuple[uptodate_store.StoredTopic, ...] | None
    uptodate_recency_window_years: int
    uptodate_has_account: bool


UPTODATE_ACCOUNT = re.compile(
    r"(?mi)^\s*UPTODATE-ACCOUNT\s*:\s*(?P<answer>yes|no)\s*$"
)


def clinician_has_uptodate_account(profile: Path | None = None) -> bool:
    """The explicit setup answer; absence does not manufacture a waiver."""
    path = profile or scratch_root() / "medatrax-profile.md"
    if not path.is_file():
        return True
    match = UPTODATE_ACCOUNT.search(path.read_text(encoding="utf-8", errors="replace"))
    return match is None or match.group("answer").casefold() == "yes"


def _load(parsed: run_grader.Parsed) -> Source:
    path = Path(parsed.source)
    if not path.is_file():
        raise run_grader.SourceError(f"no ledger file named {path.name}")
    bar_path = path.with_name("bar.md")
    if not bar_path.is_file():
        raise run_grader.SourceError("the ledger run needs bar.md")
    bar = read_bar(bar_path.read_text(encoding="utf-8", errors="replace"))
    text = path.read_text(encoding="utf-8", errors="replace")
    records = tuple(read_records(text))

    draft = parsed.value("--draft")
    prescriptions: tuple[Prescription, ...] | None = None
    half_anchored = 0
    draft_text = ""
    draft_name: str | None = None
    entries: tuple[str, ...] = ()
    if draft is not None:
        draft_path = Path(draft)
        draft_name = draft_path.name
        if not draft_path.is_file():
            raise run_grader.SourceError(f"no draft file named {draft_path.name}")
        if (
            coursework_run.is_submission(draft_path)
            and coursework_run.is_run_directory(path.parent)
            and not coursework_run.submission_belongs_to_run(draft_path, path.parent)
        ):
            raise run_grader.SourceError(
                f"submission {draft_path.name} does not belong to run directory {path.parent.name}"
            )
        draft_text = draft_path.read_text(encoding="utf-8", errors="replace")
        prescriptions = tuple(read_prescriptions(draft_text))
        half_anchored = half_anchored_tables(draft_text)
        entries = tuple(entry.text for entry in read_document(draft_text).entries)

    evidence = parsed.value("--evidence")
    carried: set[str] | None = None
    evidence_not_filed = False
    evidence_name: str | None = None
    uptodate_currency: dict[str, str] | None = None
    uptodate_details: tuple[uptodate_store.StoredTopic, ...] | None = None
    uptodate_window = bar.uptodate_recency_window_years or 2
    uptodate_has_account = True
    if evidence is not None:
        evidence_path = Path(evidence)
        evidence_name = evidence_path.name
        if not evidence_path.is_file():
            raise run_grader.SourceError(f"no evidence file named {evidence_path.name}")
        try:
            snapshot = uptodate_store.store_snapshot()
            evidence_not_filed = not uptodate_store.is_filed_source(
                evidence_path, snapshot=snapshot
            )
        except ValueError as error:
            raise run_grader.SourceError(
                f"the UpToDate store is unreadable: {error}"
            ) from error
        if not evidence_not_filed:
            uptodate_details = _latest_stored_topics(snapshot.topics)
            carried = {topic.title for topic in uptodate_details}
        cited_entries = [record.value("REFERENCE") for record in records] + list(entries or ())
        if any(uptodate_topic(entry) for entry in cited_entries):
            if bar.uptodate_recency_window_years is None:
                raise run_grader.SourceError(
                    "bar.md needs an UPTODATE-RECENCY-WINDOW-YEARS field when UpToDate evidence is graded"
                )
            try:
                uptodate_currency = {
                    topic.title: topic.literature_review_current_through
                    for topic in (uptodate_details or ())
                }
            except ValueError as error:
                raise run_grader.SourceError(
                    f"the UpToDate store is unreadable: {error}"
                ) from error
            uptodate_has_account = clinician_has_uptodate_account()

    stamp = DATE_HEADER.search(text)
    as_of = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3))) if stamp else None
    stated_expiry_unscanned = _stated_expiry_unscanned(records)
    return Source(
        path,
        records,
        as_of,
        prescriptions,
        half_anchored,
        carried,
        entries,
        evidence_not_filed,
        stated_expiry_unscanned,
        draft_name,
        evidence_name,
        bar.source_classes,
        bar.recency_window_years,
        uptodate_currency,
        uptodate_details,
        uptodate_window,
        uptodate_has_account,
    )


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(
        list(source.records),
        source.as_of,
        list(source.prescriptions) if source.prescriptions is not None else None,
        source.half_anchored,
        source.carried,
        source.entries,
        source_classes=source.source_classes,
        recency_window_years=source.recency_window_years,
        uptodate_currency=source.uptodate_currency,
        uptodate_details=source.uptodate_details,
        uptodate_recency_window_years=source.uptodate_recency_window_years,
        uptodate_has_account=source.uptodate_has_account,
        evidence_ungraded_reason=(
            f"{source.evidence_name} is not in the UpToDate store"
            if source.evidence_not_filed
            else None
        ),
    )
    diagnostics: list[str] = []
    if not source.records:
        diagnostics.append(f"no claim records found in {source.path.name}")
    if source.evidence_not_filed:
        diagnostics.append(
            f"{source.evidence_name} is not in the UpToDate store. Run"
            " python tools/uptodate_store.py ingest with that file, or point --evidence"
            " at the exact file that was ingested. Every other row still ran."
        )
    if source.as_of is None:
        diagnostics.append(
            f"{source.path.name} carries no DATE: <YYYY-MM-DD> header, so neither the"
            f" {source.recency_window_years}-year window, read-date check, nor stated-expiry check was applied"
            " to any record in it."
        )
    if source.stated_expiry_unscanned:
        diagnostics.append(
            f"{source.path.name} carries STATED-EXPIRY nowhere, so it predates #498's"
            " required question. Every other row still ran."
        )
    if source.prescriptions is not None and not source.prescriptions:
        diagnostics.append(
            f"no prescription table found in {source.draft_name} - a table is read by its"
            " Disp: and Sig: rows, so none of #289's rows was applied to it."
        )
    if scan.failing_records:
        diagnostics.append(
            f"{scan.failing_records} record(s) fail the #214 fan-out contract."
            " Re-run with --show to see which, and do not paste that output."
        )
    if scan.prescriptions_at_fault:
        diagnostics.append(
            f"{scan.prescriptions_at_fault} prescription(s) in {source.draft_name} reach"
            " no claim record. Re-run with --show to see which, and do not paste that output."
        )
    if scan.draft_references_at_fault:
        diagnostics.append(
            f"{scan.draft_references_at_fault} sourced record(s) reach no entry in"
            f" {source.draft_name}. Re-run with --show to see which, and do not paste that output."
        )
    if scan.evidence_at_fault:
        counts = dict(scan.counts)
        missing = counts[CITED_TOPIC_NOT_IN_EVIDENCE] + counts[UNREADABLE_UPTODATE_ENTRY]
        reread = counts[UPTODATE_REREAD_DUE]
        masthead = counts[UPTODATE_MASTHEAD_DISAGREES]
        if missing:
            diagnostics.append(
                f"{missing} UpToDate citation(s) do not resolve to the current dump or"
                " accumulated evidence manifests. Deliberately ingest the supplied dump"
                " or drop the citation. Re-run with --show to see which, and do not paste that output."
            )
        if reread:
            diagnostics.append(
                f"{reread} UpToDate topic(s) have left the signed publisher-review window."
                " Re-open them through the authenticated route and refresh their sheets."
                " Re-run with --show to see which, and do not paste that output."
            )
        if masthead:
            diagnostics.append(
                f"{masthead} UpToDate author or year comparison(s) disagree with the"
                " stored topic masthead. Re-run with --show to see which, and do not paste that output."
            )
    findings_failed = bool(
        scan.failing_records
        or scan.prescriptions_at_fault
        or scan.draft_references_at_fault
        or scan.evidence_at_fault
    )
    coverage_failed = bool(
        not source.records
        or source.as_of is None
        or source.evidence_not_filed
        or source.stated_expiry_unscanned
        or (source.prescriptions is not None and not source.prescriptions)
    )
    return run_grader.Grade(
        scan=scan,
        source=source.path.name,
        findings_failed=findings_failed,
        coverage_failed=coverage_failed,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage=USAGE,
    options=(
        run_grader.Option("--show"),
        run_grader.Option("--draft", takes_value=True, missing_value=USAGE),
        run_grader.Option("--evidence", takes_value=True, missing_value=USAGE),
    ),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    if "--heading-digests" in argv:
        use_utf8()
        require_python_floor()
        if len(argv) != 2 or argv[1] != "--heading-digests":
            print(USAGE, file=sys.stderr)
            return 2
        path = Path(argv[0])
        if not path.is_file():
            print(f"no ledger file named {path.name}", file=sys.stderr)
            return 2
        records = read_records(path.read_text(encoding="utf-8", errors="replace"))
        if not records:
            print(f"no claim records found in {path.name}", file=sys.stderr)
            return 2
        for record in records:
            print(f"{heading_digest(record.claim)}  {record.claim}")
        return 0
    return run_grader.run(GRADER, argv)
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
