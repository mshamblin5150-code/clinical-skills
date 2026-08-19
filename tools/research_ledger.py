"""Grade the research ledger a ``practicum-case-study`` run writes before it drafts.

    python tools/research_ledger.py <a ledger file> [--show]

[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) is this.
The skill used to write an unsourced claim into the body and list it in the
``PROPOSED`` block with **verify this** against it; the clinician's ruling of
2026-08-18 is that such a claim gets **researched** instead, one agent per claim,
in parallel. **The ticket asks for a mechanism rather than an instruction**, and
the mechanism is a written record with a grader in front of it: the fan-out
produces one ledger record per claim, and this refuses the ones that did not
answer the question they were sent to answer.

**The ledger is the mechanism, not the parallelism.** A harness with no subagent
tool works the same briefs serially into the same file, and the grader cannot tell
the difference -- which is the point. ``SKILL.md`` says so where it names this
command, and a test here asserts that sentence is still there.

**One writer, and the claim list goes in before the agents go out.** N agents
appending to one Markdown file lose records to each other, and this tool has no
expected count to measure a short ledger against -- so three records where eight
claims were sent out would grade clean and the run would draft.
[#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s
shared-artifact channel, with lost writes where that ticket has leaked reads.
**Writing the headings first is what closes it rather than a new row**: a heading
whose answer never arrived carries no ``STATUS``, and a record with no ``STATUS``
already fails. ``skills/practicum-case-study/SKILL.md`` step 3 orders it that way
and a test below pins the consequence.

**The record shape**, one per claim, in a Markdown file under ``scratch/``::

    DATE: 2026-08-19

    ## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.
    STATUS: sourced
    SOURCE: peer-reviewed
    REFERENCE: Abbassi-Ghanavati, M., Greer, L. G., & Cunningham, F. G. (2009).
        Pregnancy and laboratory studies. Obstetrics and Gynecology, 114(6), 1326-1331.
    RESTATEMENT: The table gives a third-trimester white cell range of 5.6 to
        16.9 x 10^9/L in normal pregnancy.
    RECENCY: nothing newer - searched 2026-08-19; no later reference-range table
        for pregnancy exists, and obstetric texts still cite this one.

A field's value runs to the next field line or the next claim, so an APA entry may
wrap the way an APA entry wraps.

**What it checks, and which ruling each row belongs to.**

*#214, the fan-out's own contract:*

- **Every field is present and carries something.** A record missing its
  ``RESTATEMENT`` is a citation nobody checked against the claim.
- **``STATUS`` is one of two branches**, and an unrecognized one is a **failure**
  rather than a counted curiosity. This departs from ``specificity_scan.py``'s
  third-branch rule deliberately: there the keyword selects a message, here it
  selects **which tests run**, so a record reading ``STATUS: pending`` is graded on
  nothing at all and reports as clean.
- **``STATUS: unsourced`` carries a reason.** That is ``specificity_scan.py``'s
  substance test and it is here for its reason -- nobody writes *"searched PubMed,
  IDSA and UpToDate, nothing addresses this"* without having looked, and anybody
  can write ``unsourced``. An unsourced record is **not a failure**: the skill
  routes it to ``PROPOSED``, and out of the document entirely where it is a number.
  The count is printed so the run knows how many did.
- **An unsourced record may not carry a ``REFERENCE``.** The two statements
  contradict each other and nothing else in the file can tell which was meant.
- **The restatement is not the claim again.** Normalized equality only, because
  anything looser is a guess about paraphrase. This is the cheap half of the limb
  the ticket calls the one that matters most.
- **A claim carrying a number gets a restatement carrying a number.** ``A white
  count of 15,000 ...`` answered by *"the source discusses leukocytosis in
  pregnancy"* is the wrong-citation-survives-review failure at its most expensive,
  and it is the one form of it a string test can reach.

*#215, the recency rule as amended:*

- **``RECENCY`` is one of four dispositions**, and an unrecognized one is a failure
  for ``STATUS``'s reason rather than ``SOURCE``'s: it gates the row below it, so a
  record reading ``RECENCY: probably fine`` is never measured against the window at
  all. **This row was missing from the first version of this module** and was found
  by review, which is the same argument arriving at the field it was first written
  for and not at the field beside it.
- **Past five years, the record says why it stands.** ``nothing newer`` or
  ``guideline in force``, and nothing else excuses it. The first version of this
  rule cut a correct 2018 refutation and left a 1932 teaching standing by default;
  what the rule refuses is a claim that is old **and superseded**.
- **The excuse carries a reason**, on the same footing as the status. *The run must
  have looked, and must say so* is #215's own wording, and a bare ``nothing newer``
  is the assertion without the looking.
- **A reference states a year, unless an excuse stands in for one.** ``n.d.`` is
  legitimate APA, and the recency rule cannot be applied to it -- a row that could
  not be graded reads exactly like a row that passed. **Refusing it outright would
  be a rule the clinician never made**, so the escape hatch is the one he did make:
  an undated source carrying ``nothing newer`` or ``guideline in force`` with a
  reason stands, and one carrying neither is refused.

**#215's first limb reaches no row here, and that is deliberate.** *Within two years
is the target* is a target: a ``current`` disposition on a three-year-old reference
is not a defect, and grading it would refuse what the ruling merely prefers.

**What it cannot reach, and this is most of the ticket.** Whether the source is
reputable, whether it says what the restatement says it says, and whether the
numbers agree. **The last one is not an oversight**: the restatement is written in
the source's own terms *by design*, so a claim about 15,000 cells is rightly
answered with a range in ``10^9/L``, and a test comparing the digits would refuse
the correct answer. Judging a restatement against its source is a reading, and a
clean scan here is not a walked claim.

**Nor does it reach the document.** *A claim that survives the fan-out still
unsourced does not go in the body* is #214's rule and it is about the draft, which
this never sees -- so a ledger of nothing but well-formed ``unsourced`` records
exits 0, and that 0 means the records are honest rather than that the paper is. The
count is printed for exactly that reason, and ``skills/practicum-case-study/SKILL.md``
step 9 walks it.

**And it does not verify the citation, which is #214's open question 2, deferred
rather than answered here.** The format half has a written standard since #211 --
``skills/practicum-case-study/reference/apa7.md``, walked by ``practicum-case-study``
step 7 and by [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s
post-draft checkers. The truth half -- does the DOI or URL resolve, and does the
year on the page match the year in the entry -- is ``threshold_sheet.py``'s tier 2
arriving at a reference list, needs the network, and is
[#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231). **What
this module checks is that a year is *stated*, never that it is *right*.**

**Counts only by default**, on ``specificity_scan.py``'s and ``block_scan.py``'s
terms and for their reason: the ledger lives under ``scratch/`` and a claim is
transcribed from faculty material about a patient. **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** -- 0
clean, 1 for a violation, **2 for every way of not having scanned**: no argument,
no file, no ``## CLAIM:`` record in it, and **no ``DATE:`` header**. That last limb
is the one that matters. The window is measured against the day the paper is
written, so a ledger with no date was never measured by #215's rule at all, and a
clean report would read as though it had been.

**Where a violation and a missing ``DATE`` both hold, 1 wins**, on
``differential_scan.py``'s and ``filled_vitals_census.py``'s ordering and for their
reason: returning 2 would file the strongest thing known about the ledger under the
weakest heading. The banner prints either way, so an exit 1 over a dateless ledger
reads as a floor rather than the whole. **The first version of this module returned
2 there**, which is the one place it departed from both siblings without saying so.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from console_codec import use_utf8

# A record opens on a heading. The heading level is free, so the ledger can sit
# under a document heading without the parser caring.
CLAIM = re.compile(r"(?mi)^[ \t]*#+[ \t]*CLAIM[ \t]*:[ \t]*(.*?)[ \t]*$")
FIELD = re.compile(
    r"(?mi)^[ \t]*(STATUS|SOURCE|REFERENCE|RESTATEMENT|RECENCY)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
# The day the paper is written. Recency is measured against it and never against
# the clock -- a ledger graded twice a year apart has to grade the same both times.
DATE_HEADER = re.compile(r"(?mi)^[ \t]*DATE[ \t]*:[ \t]*(\d{4})-(\d{2})-(\d{2})[ \t]*$")

# An APA entry states its year in parentheses. ``2019a`` is the a/b disambiguation
# form ``reference/apa7.md`` section 3 requires, so the letter is allowed and dropped.
YEAR = re.compile(r"\((\d{4})[a-z]?(?:,[^)]*)?\)")

# The four source classes #214 names, and nothing else. A fixed vocabulary is
# ``threshold_sheet.py``'s population key for the same reason: a machine can only
# compare strings, and a mis-keyed value is a wrong *word* a reader can see.
SOURCE_CLASSES = ("society guideline", "peer-reviewed", "government", "tertiary reference")

# #215's four dispositions. The last two are the ones that excuse an old source,
# and both have to say why.
RECENCY_CURRENT = "current"
RECENCY_WITHIN_FIVE = "within five"
RECENCY_NOTHING_NEWER = "nothing newer"
RECENCY_IN_FORCE = "guideline in force"
RECENCY_VALUES = (RECENCY_CURRENT, RECENCY_WITHIN_FIVE, RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)
EXCUSES = (RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)

SOURCED = "sourced"
UNSOURCED = "unsourced"
STATUSES = (SOURCED, UNSOURCED)

# #215's "ordinarily expected" window. Past it a record has to say why it stands.
ORDINARY_WINDOW_YEARS = 5

# Anything alphanumeric after a keyword is substance. Judging whether the reason is
# a real search or a stock phrase takes a reader -- ``specificity_scan.py``'s R2.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")
DIGIT = re.compile(r"[0-9]")
NOT_ALNUM = re.compile(r"[^0-9a-z]+")

MISSING_FIELD = "missing-field"
UNKNOWN_STATUS = "unknown-status"
BARE_STATUS = "bare-status"
UNSOURCED_WITH_REFERENCE = "unsourced-with-reference"
UNKNOWN_SOURCE_CLASS = "unknown-source-class"
UNKNOWN_RECENCY = "unknown-recency"
RESTATEMENT_ECHOES_CLAIM = "restatement-echoes-claim"
NUMERIC_CLAIM_UNQUANTIFIED = "numeric-claim-unquantified"
UNDATED_REFERENCE = "undated-reference"
STALE_UNEXCUSED = "stale-unexcused"
BARE_EXCUSE = "bare-excuse"

# Every row, in report order. Kept as one tuple so the report, the counter and the
# ticket map cannot drift into listing different sets.
KINDS = (
    MISSING_FIELD,
    UNKNOWN_STATUS,
    BARE_STATUS,
    UNSOURCED_WITH_REFERENCE,
    UNKNOWN_SOURCE_CLASS,
    RESTATEMENT_ECHOES_CLAIM,
    NUMERIC_CLAIM_UNQUANTIFIED,
    UNKNOWN_RECENCY,
    UNDATED_REFERENCE,
    STALE_UNEXCUSED,
    BARE_EXCUSE,
)

# Which ruling each row belongs to, so a reader knows which ticket to go and read.
ROW_TICKET = {
    MISSING_FIELD: "#214",
    UNKNOWN_STATUS: "#214",
    BARE_STATUS: "#214",
    UNSOURCED_WITH_REFERENCE: "#214",
    UNKNOWN_SOURCE_CLASS: "#214",
    UNKNOWN_RECENCY: "#215",
    RESTATEMENT_ECHOES_CLAIM: "#214",
    NUMERIC_CLAIM_UNQUANTIFIED: "#214",
    UNDATED_REFERENCE: "#215",
    STALE_UNEXCUSED: "#215",
    BARE_EXCUSE: "#215",
}

REQUIRED_WHEN_SOURCED = ("SOURCE", "REFERENCE", "RESTATEMENT", "RECENCY")


def normalize(text: str) -> str:
    """Lowercase alphanumerics only, single-spaced.

    Used for equality and never for similarity -- anything looser would be a guess
    about paraphrase, and paraphrase is exactly what the restatement is for.
    """
    return " ".join(NOT_ALNUM.sub(" ", text.lower()).split())


# Built from ``normalize`` rather than typed, so the lookup and the comparison it
# stands in for cannot come to disagree about what a mis-keyed value looks like.
# Built once rather than per record. ``SOURCE`` can afford this and ``RECENCY``
# cannot: there the whole value is the keyword, here the keyword is a prefix with a
# reason after it, and normalizing destroys the boundary between them.
_CLASS_KEYS = frozenset(normalize(name) for name in SOURCE_CLASSES)


def keyword_of(value: str, vocabulary: tuple[str, ...]) -> tuple[str, str]:
    """Split a field value into its vocabulary keyword and the remainder.

    Longest first, so ``guideline in force`` is not read as an unrecognized value
    that happens to begin with a shorter one.
    """
    stripped = value.strip()
    lowered = stripped.lower()
    for word in sorted(vocabulary, key=len, reverse=True):
        if lowered.startswith(word):
            return word, stripped[len(word) :]
    return "", stripped


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


@dataclass(frozen=True)
class Finding:
    """One record failing one row."""

    kind: str
    claim: str
    detail: str


@dataclass(frozen=True)
class Scan:
    """Counts over one ledger, plus the findings ``--show`` prints.

    ``as_of`` is ``None`` where the ledger carried no ``DATE:`` header. Nine of the
    ten rows still grade; the window does not, and the report says so.
    """

    as_of: date | None
    records: int
    sourced: int
    unsourced: int
    unrecognized_status: int
    by_class: tuple[tuple[str, int], ...]
    outside_vocabulary: int
    standing_past_five: int
    counts: tuple[tuple[str, int], ...]
    failing_records: int
    findings: tuple[Finding, ...]


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


def record_findings(record: Record, as_of: date | None) -> list[Finding]:
    """Every row this record fails. A record can fail several.

    ``as_of`` of ``None`` means the ledger stated no date, so the window row is
    skipped and every other row still runs -- ``differential_scan.py``'s ordering,
    where a finding outranks an incomplete scan.
    """
    found: list[Finding] = []
    claim = record.claim

    if not SUBSTANCE.search(claim):
        found.append(Finding(MISSING_FIELD, claim, "CLAIM"))

    status = record.status
    if not status:
        # Unlike an unrecognized ``SPECIFICITY`` keyword, this one is a failure:
        # the branch decides which tests below run, so a record wearing a third
        # word is graded on nothing at all and prints as clean.
        found.append(Finding(UNKNOWN_STATUS, claim, record.value("STATUS")))
        return found

    if status == UNSOURCED:
        if not SUBSTANCE.search(keyword_of(record.value("STATUS"), STATUSES)[1]):
            found.append(Finding(BARE_STATUS, claim, record.value("STATUS")))
        if SUBSTANCE.search(record.value("REFERENCE")):
            found.append(Finding(UNSOURCED_WITH_REFERENCE, claim, record.value("REFERENCE")))
        return found

    for name in REQUIRED_WHEN_SOURCED:
        if not SUBSTANCE.search(record.value(name)):
            found.append(Finding(MISSING_FIELD, claim, name))

    source = normalize(record.value("SOURCE"))
    if source and source not in _CLASS_KEYS:
        found.append(Finding(UNKNOWN_SOURCE_CLASS, claim, record.value("SOURCE")))

    restatement = record.value("RESTATEMENT")
    if SUBSTANCE.search(restatement):
        if normalize(restatement) == normalize(claim):
            found.append(Finding(RESTATEMENT_ECHOES_CLAIM, claim, restatement))
        if DIGIT.search(claim) and not DIGIT.search(restatement):
            found.append(Finding(NUMERIC_CLAIM_UNQUANTIFIED, claim, restatement))

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
        elif as_of is not None and as_of.year - year > ORDINARY_WINDOW_YEARS and excuse not in EXCUSES:
            detail = f"{year}, RECENCY: {recency}"
            found.append(Finding(STALE_UNEXCUSED, claim, detail))
    return found


def survey(records: list[Record], as_of: date | None) -> Scan:
    """Count across one ledger.

    Takes parsed records rather than paths, so the counts carry no provenance of
    their own. The ledger's **name** is printed by ``format_report`` the way every
    sibling prints a run directory's -- the name, never the path.
    """
    graded = [(record, record_findings(record, as_of)) for record in records]
    found = [f for _, per_record in graded for f in per_record]
    sourced = [r for r in records if r.status == SOURCED]
    return Scan(
        as_of=as_of,
        records=len(records),
        sourced=len(sourced),
        unsourced=sum(1 for r in records if r.status == UNSOURCED),
        unrecognized_status=sum(1 for r in records if not r.status),
        by_class=tuple(
            (name, sum(1 for r in sourced if normalize(r.value("SOURCE")) == normalize(name)))
            for name in SOURCE_CLASSES
        ),
        outside_vocabulary=sum(1 for r in sourced if normalize(r.value("SOURCE")) not in _CLASS_KEYS),
        standing_past_five=sum(
            1 for r in sourced if keyword_of(r.value("RECENCY"), RECENCY_VALUES)[0] in EXCUSES
        ),
        counts=tuple((kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS),
        failing_records=sum(1 for _, per_record in graded if per_record),
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
        else f"research ledger over {source}, NO DATE HEADER - the window was not graded",
        "",
        f"  claim records read               {scan.records}",
        f"    sourced                        {scan.sourced}",
        f"    unsourced - go to PROPOSED     {scan.unsourced}",
        f"    neither status                 {scan.unrecognized_status}",
        "",
    ]
    for name, count in scan.by_class:
        lines.append(f"    {name:<30} {count}")
    lines.append(f"    {'outside the vocabulary':<30} {scan.outside_vocabulary}")
    lines.append("")
    lines.append(f"  standing past five years         {scan.standing_past_five}")
    lines.append("")
    for kind, count in scan.counts:
        lines.append(f"  {ROW_TICKET[kind]} - {kind:<28} {count}")
    lines.append("")
    lines.append(f"  records at fault                 {scan.failing_records}")
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<26} {finding.claim}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    args = [a for a in argv if not a.startswith("--")]
    show = "--show" in argv
    if not args:
        print("usage: research_ledger.py <a ledger file> [--show]", file=sys.stderr)
        return 2
    path = Path(args[0])
    # The name, never the path: a ledger sits under ``scratch/``.
    if not path.is_file():
        print(f"no ledger file named {path.name}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    records = read_records(text)
    if not records:
        print(f"no claim records found in {path.name}", file=sys.stderr)
        return 2
    stamp = DATE_HEADER.search(text)
    as_of = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3))) if stamp else None
    scan = survey(records, as_of)
    print(format_report(scan, source=path.name, show=show))
    if as_of is None:
        # Printed whichever status follows, so an exit 1 below reads as a floor
        # rather than as the whole of what is wrong.
        print(
            f"{path.name} carries no DATE: <YYYY-MM-DD> header, so the five-year"
            " window was not applied to any record in it.",
            file=sys.stderr,
        )
    if scan.failing_records:
        # 1 outranks the missing header, on ``differential_scan.py``'s ordering:
        # returning 2 would file the strongest thing known about this ledger under
        # the weakest heading.
        print(
            f"{scan.failing_records} record(s) fail the #214 fan-out contract."
            " Re-run with --show to see which, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 2 if as_of is None else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
