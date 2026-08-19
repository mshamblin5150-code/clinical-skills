"""Grade the post-draft checks a ``practicum-case-study`` run writes after it drafts.

    python tools/checks_ledger.py <a checks file> [--show]

[#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240) is this,
and the ticket is an asymmetry rather than a defect.
``skills/practicum-case-study/SKILL.md`` has two fan-outs and they are the same
mechanism: N agents, one record each, into one Markdown file, headings written
first so a lost record is visible, one writer. **``practicum-case-study`` step 3's
fan-out got a grader on
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) and
``practicum-case-study`` step 9's did not**, so the second one's record shape was
held by exactly what the first one's was held by before ``research_ledger.py``
existed: a sentence saying
so, and a line in a by-eye checklist. #214's argument transfers whole -- *what a
written instruction cannot do is fail* -- and this is that argument arriving at
the fan-out that had less protection, not more.

**The ledger is the mechanism, not the parallelism**, on
``research_ledger.py``'s terms and for its reason: a harness with no subagent tool
works the same briefs serially into the same file, and this cannot tell the
difference. ``skills/practicum-case-study/SKILL.md`` says so where it names this
command, and a test asserts that sentence is still there.

**The record shape**, one per check, in a Markdown file under ``scratch/``::

    ## CHECK: differential ordering
    VERDICT: defect
    FINDINGS: The differential's 1. is appendicitis, and the intake gives a
        patient of childbearing age with pelvic pain and no documented hCG. The
        pregnancy-related emergency is at 4 and has to be at 1 until the hCG is
        back.

A field's value runs to the next field line or the next heading, so a finding may
wrap the way a finding wraps.

**What it checks.** Every row belongs to #240 and every one is already written
into ``skills/practicum-case-study/SKILL.md`` step 9 -- this grades what that step
states rather than adding a rule to it.

- **Every check the table names is present.** A reader that never returned leaves
  a hole, and it is visible only if somebody counts headings against verdicts.
- **No check is recorded twice.** ``practicum-case-study`` step 9 says **one
  record per check** in as many words, so this grades what the step already asks
  rather than adding a rule to it -- which is the test every row here has to pass.
  Two verdicts under one name and nothing in the file says which was meant, which
  is ``research_ledger.py``'s contradiction reasoning and the mechanical face of
  [#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s
  lost-write shape. **It is the one row #240's own table does not list**, and that
  is why the sentence it grades is named here.
- **Every heading carries a ``VERDICT``.** The step names this failure itself and
  then leaves it to the reader who has just been told the draft is finished.
- **``VERDICT`` is one of two words**, and a third is a **failure** rather than a
  counted curiosity -- ``research_ledger.py``'s ``STATUS`` argument exactly, and
  it departs from ``specificity_scan.py``'s third-branch rule for the same reason:
  there the keyword picks a message, here it picks which rows run, so
  ``VERDICT: mostly fine`` is a record graded on nothing at all.
- **A ``defect`` carries a ``FINDINGS`` with substance in it.** That is
  ``specificity_scan.py``'s substance test: anybody can write ``defect``, and
  nobody writes the entry's position and the rule it fails without having read it.
  **The field and not merely the substance**, which is #240's own wording and is
  the stricter of the two readings: a reason typed after the keyword on the
  ``VERDICT`` line says the same thing, and it says it somewhere the record shape
  in ``practicum-case-study`` step 9 does not put it, so a reader looking for the
  finding has nowhere fixed to look. An earlier draft here accepted both and was
  caught reading looser than the ticket it implements.

**The expected set is the one place this is stronger than its sibling.**
``research_ledger.py`` has no expected count and says so, so three records where
eight claims went out grade clean. Here the table in
``skills/practicum-case-study/SKILL.md`` step 9 fixes the set, so a check nobody
spawned is a finding. **The vocabulary is held here and derived there**: a run
directory is not a checkout, so this cannot read ``SKILL.md`` at run time, and
``test_checks_ledger.py`` reads that table and asserts the two agree. That is
``spelling_scan.py``'s arrangement with the conventions table and it is here for
its reason -- a scanner holding a different answer than the file a reader opens is
worse than none, because it reads as agreement.

**A heading outside the table is counted and never graded.** A run adding a check
of its own has failed nothing, and a *misspelled* one is already caught from the
other direction by the row above. Grading it would refuse the first and report the
second twice.

**One shape the ticket names is deliberately not a row.** ``VERDICT: clean`` with
an empty ``FINDINGS`` is
[#182](https://github.com/mshamblin5150-code/clinical-skills/issues/182)'s *a
block satisfies the gate by existing*, and it is **not reachable from a string
test**: a check that ran and found nothing writes exactly what a check that
reported nothing writes. #240 says so itself in naming it -- *indistinguishable*.
Requiring a clean check to say what it examined would reach it, and that is a
change to what the step asks a reader to write rather than a grader of what it
already asks, so it is not made here.

**What it cannot reach, and it is most of the file.** Every verdict is a reading.
Whether the differential's ``1.`` really is what would kill first, whether an MDM
entry's discriminator is from this case, whether the reader looked at the draft at
all -- none of it is in the record, and a well-formed ``clean`` from a reader that
skimmed is indistinguishable from one that read. **A clean scan is not a checked
draft**, ``skills/practicum-case-study/SKILL.md`` says so beside the command, and
a test asserts that sentence is still there.

**Nor does it reach the repair.** *A finding is fixed, not handed over* is #211's
rule inherited by that step, and it is about the document, which this never sees.
So a file of well-formed ``defect`` records exits 0, and that 0 means the verdicts
are well formed rather than that the draft was mended.

**Counts only by default**, on ``research_ledger.py``'s and ``block_scan.py``'s
terms and for their reason: the file lives under ``scratch/`` and a finding
describes a draft written about a patient. **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**The one thing the default report names is a missing check, and the name comes
from this module rather than from the file.** ``EXPECTED_CHECKS`` is a fixed tuple
of table strings -- how many is that tuple's to say and is deliberately not
restated here, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms --
so printing one draws on nothing the run wrote. That is
``reference_scan.py``'s *what the code can draw on is bounded* used at the
narrowest possible width, and it is **not** this tool's ``--show`` becoming safe
to paste: a heading outside the table is never named, because that string is the
run's own text.

**Exit status distinguishes not having scanned from having found nothing** -- 0
clean, 1 for a violation, **2 for every way of not having scanned**: no argument,
no file, and **no ``## CHECK:`` record in it**. That last limb is the one that
matters, on ``differential_scan.py``'s reasoning: a checks file written in a shape
this cannot read would otherwise report zero findings and stand where a checked
draft should be. There is no dateless limb here, because nothing in this file is
measured against a date -- which is the one row of ``research_ledger.py``'s
arrangement that does not transfer.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from console_codec import use_utf8

# A record opens on a heading. The heading level is free, so the file can sit
# under a document heading without the parser caring -- ``research_ledger.py``'s
# ``CLAIM`` and its reason.
CHECK = re.compile(r"(?mi)^[ \t]*#+[ \t]*CHECK[ \t]*:[ \t]*(.*?)[ \t]*$")
FIELD = re.compile(r"(?mi)^[ \t]*(VERDICT|FINDINGS)[ \t]*:[ \t]*(.*?)[ \t]*$")

# The check table in ``skills/practicum-case-study/SKILL.md`` step 9, first column,
# verbatim. **Held here and derived there**: a run directory is not a checkout, so
# nothing at run time can read that file, and ``test_checks_ledger.py`` parses the
# table and asserts this tuple is it. ``spelling_scan.py``'s arrangement with the
# conventions table.
#
# The first two differ by a suffix, which is why the match below is equality on a
# normalized string and never a substring: a prefix test would read either one as
# satisfying both.
EXPECTED_CHECKS = (
    "the reference list",
    "the reference list, the part no command reaches",
    "differential ordering",
    "MDM completeness",
    "the Rx blocks",
    "the faculty's own to-do list",
)

CLEAN = "clean"
DEFECT = "defect"
VERDICTS = (CLEAN, DEFECT)

# Anything alphanumeric after a keyword is substance. Judging whether the finding
# is a real reading or a stock phrase takes a reader -- ``specificity_scan.py``'s
# R2, and ``research_ledger.py`` inherits it for the same field shape.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")
# What may follow a vocabulary keyword. End of value, or a separator that is not a
# letter, a digit or a hyphen.
#
# **The hyphen is excluded on purpose and it is the one character that had to be
# argued.** ``VERDICT: defect - entry 2 names none`` is the ordinary compliant
# form, so a hyphen *has* to be allowed after a space -- but allowing it welded
# makes ``defect-free`` read as ``defect``, which is a run saying the opposite of
# what it is graded as. A **spaced** hyphen is a separator and a **welded** one is
# part of the word, which is how a reader takes it too.
BOUNDARY = re.compile(r"[^0-9A-Za-z-]|$")
NOT_ALNUM = re.compile(r"[^0-9a-z]+")

MISSING_CHECK = "missing-check"
DUPLICATE_CHECK = "duplicate-check"
MISSING_VERDICT = "missing-verdict"
UNKNOWN_VERDICT = "unknown-verdict"
DEFECT_WITHOUT_FINDINGS = "defect-without-findings"

# Every row, in report order. One tuple, so the report, the counter and the ticket
# map cannot drift into listing different sets.
KINDS = (
    MISSING_CHECK,
    DUPLICATE_CHECK,
    MISSING_VERDICT,
    UNKNOWN_VERDICT,
    DEFECT_WITHOUT_FINDINGS,
)

# Which ruling each row belongs to, so a reader knows which ticket to go and read.
# **Spelled out rather than built from ``KINDS``**, and that is the whole of what
# makes the sentence above it true: a comprehension would assign #240 to a row the
# next ticket adds, so the map could never fail and a claim that a row cannot
# arrive without a ticket would be a claim about code that does not check it.
# ``KINDS`` is ordered and this is keyed, so ``format_report`` raises rather than
# mislabelling.
ROW_TICKET = {
    MISSING_CHECK: "#240",
    DUPLICATE_CHECK: "#240",
    MISSING_VERDICT: "#240",
    UNKNOWN_VERDICT: "#240",
    DEFECT_WITHOUT_FINDINGS: "#240",
}

# Wide enough for the longest kind, so the count column stays a column and lines
# up with the counts above it. ``research_ledger.py`` learned this the hard way:
# a row added there was one character over the pad and the report went ragged in
# the one output meant to be pasted into a ticket.
KIND_COLUMN = 25


def normalize(text: str) -> str:
    """Lowercase alphanumerics only, single-spaced.

    Used for equality and never for similarity. It is what lets a heading match
    the table across a capital or a separating hyphen -- *The Faculty's Own To Do
    List* is the same check -- while keeping the two reference rows apart, which
    differ by whole words rather than by punctuation.

    **``research_ledger.py``'s helper taken whole, and the limit that comes with
    it is pinned rather than widened.** Punctuation becomes a space, so dropping
    an apostrophe makes ``facultys`` a different token than ``faculty s`` and the
    heading does not match. What that costs is a **reported** miss -- the row
    below fires and names the check -- and never a silent pass, which is the
    direction that would be worth widening the rule for.
    """
    return " ".join(NOT_ALNUM.sub(" ", text.lower()).split())


# Built from ``normalize`` rather than typed, so the lookup and the comparison it
# stands in for cannot come to disagree about what an off-table heading looks like.
_EXPECTED_KEYS = {normalize(name): name for name in EXPECTED_CHECKS}


def keyword_of(value: str, vocabulary: tuple[str, ...]) -> tuple[str, str]:
    """Split a field value into its vocabulary keyword and the remainder.

    Longest first, so a longer word is not read as an unrecognized value that
    happens to begin with a shorter one.

    **A prefix is not a word, and that limb is this module's rather than
    ``research_ledger.py``'s.** That one matches on ``startswith`` alone, which is
    survivable for its vocabularies and is not for these two: ``VERDICT: cleanish``
    and ``VERDICT: cleanly not run`` both graded as ``clean`` and reported nothing,
    and ``VERDICT: defect-free`` graded as ``defect`` and was then failed for
    carrying no findings -- wrong in both directions, which is what a positional
    guess costs. So the character after the keyword has to be a boundary. **The
    same defect is latent in the sibling** -- ``RECENCY: currently under review``
    reads as ``current`` there -- and it is filed rather than reached into from
    here, because that module's rows have their own tests to move.

    This helper and ``normalize`` are **copied** from ``research_ledger.py`` rather
    than imported, and this divergence is what made the copy the right call: a
    shared helper would have had to grow a flag for which caller wanted the
    boundary, and ``console_codec.py`` is this directory's only module that exists
    to be depended on.
    """
    stripped = value.strip()
    lowered = stripped.lower()
    for word in sorted(vocabulary, key=len, reverse=True):
        if lowered.startswith(word) and BOUNDARY.match(lowered[len(word) :]):
            return word, stripped[len(word) :]
    return "", stripped


@dataclass(frozen=True)
class Record:
    """One check and the verdict the reader returned for it."""

    check: str
    fields: dict[str, str] = field(default_factory=dict)

    def value(self, name: str) -> str:
        return self.fields.get(name, "")

    @property
    def verdict(self) -> str:
        return keyword_of(self.value("VERDICT"), VERDICTS)[0]


@dataclass(frozen=True)
class Finding:
    """One check failing one row.

    ``check`` is the heading. It is the run's own text where the record exists,
    and one of ``EXPECTED_CHECKS`` where the row is ``MISSING_CHECK`` -- which is
    the only case ``format_report`` will name without ``--show``.
    """

    kind: str
    check: str
    detail: str


@dataclass(frozen=True)
class Scan:
    """Counts over one checks file, plus the findings ``--show`` prints."""

    records: int
    clean: int
    defect: int
    unrecognized_verdict: int
    expected: int
    outside_the_table: int
    counts: tuple[tuple[str, int], ...]
    failing_checks: int
    missing: tuple[str, ...]
    findings: tuple[Finding, ...]


def read_records(text: str) -> list[Record]:
    """Every check record in one file.

    A field's value runs to the next field line or the next heading, so a finding
    may wrap. A line before the first heading belongs to no record and is dropped.
    """
    records: list[Record] = []
    check: str | None = None
    fields: dict[str, str] = {}
    current: str | None = None

    def close() -> None:
        if check is not None:
            records.append(Record(check=check, fields=dict(fields)))

    for line in text.splitlines():
        heading = CHECK.match(line)
        if heading:
            close()
            check, fields, current = heading.group(1), {}, None
            continue
        if check is None:
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


def record_findings(record: Record) -> list[Finding]:
    """Every row this record fails. A record can fail more than one."""
    found: list[Finding] = []
    check = record.check

    verdict, reason = keyword_of(record.value("VERDICT"), VERDICTS)
    if not SUBSTANCE.search(record.value("VERDICT")):
        # A heading whose reader never returned. The step names this failure and
        # then leaves it to somebody counting headings against verdicts.
        return [Finding(MISSING_VERDICT, check, "VERDICT")]
    if not verdict:
        # A **failure**, not a counted third branch: the field decides which rows
        # below run, so a record wearing a third word is graded on nothing at all
        # and prints as clean. ``research_ledger.py``'s ``STATUS`` reasoning.
        return [Finding(UNKNOWN_VERDICT, check, record.value("VERDICT"))]

    if verdict == DEFECT and not SUBSTANCE.search(record.value("FINDINGS")):
        # **The field, not merely the substance.** A reason typed after the keyword
        # says the same thing in a place the record shape does not put it, so a
        # reader looking for the finding has nowhere fixed to look. #240 asks for
        # ``FINDINGS`` with substance and an earlier draft here read it looser.
        found.append(Finding(DEFECT_WITHOUT_FINDINGS, check, record.value("VERDICT")))
    return found


def set_findings(records: list[Record]) -> list[Finding]:
    """The two rows that are about the set rather than about a record.

    A missing check is the row ``research_ledger.py`` has no counterpart for, and
    a repeated one is two verdicts where the file can hold one answer.
    """
    seen: dict[str, int] = {}
    for record in records:
        key = normalize(record.check)
        seen[key] = seen.get(key, 0) + 1
    found = [
        Finding(MISSING_CHECK, name, "no heading in the file")
        for key, name in _EXPECTED_KEYS.items()
        if key not in seen
    ]
    # One finding per repeat rather than one per record: the first is the record,
    # the rest are the writes that landed on top of it. **The detail names the
    # total every time**, because an earlier draft decremented as it went and the
    # second finding of a triple read ``2 records`` -- a count that was false about
    # the file, in the one output a reader is told to trust.
    for key, total in seen.items():
        if total > 1:
            name = next(r.check for r in records if normalize(r.check) == key)
            found += [Finding(DUPLICATE_CHECK, name, f"{total} records")] * (total - 1)
    return found


def survey(records: list[Record]) -> Scan:
    """Count across one checks file.

    Takes parsed records rather than a path, so the counts carry no provenance of
    their own. The file's **name** is printed by ``format_report`` the way every
    sibling prints a run directory's -- the name, never the path.
    """
    found = set_findings(records)
    for record in records:
        found += record_findings(record)
    at_fault = {normalize(f.check) for f in found}
    return Scan(
        records=len(records),
        clean=sum(1 for r in records if r.verdict == CLEAN),
        defect=sum(1 for r in records if r.verdict == DEFECT),
        unrecognized_verdict=sum(1 for r in records if not r.verdict),
        expected=len(EXPECTED_CHECKS),
        outside_the_table=sum(1 for r in records if normalize(r.check) not in _EXPECTED_KEYS),
        counts=tuple((kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS),
        failing_checks=len(at_fault),
        missing=tuple(f.check for f in found if f.kind == MISSING_CHECK),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no text from the file unless ``show``.

    The exception is the missing-check list, and it is an exception in name only:
    those strings are ``EXPECTED_CHECKS`` members, so they are this module's own
    text and never the run's. A heading outside the table is counted and never
    named.
    """
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console where anything outside cp1252 reads like corruption in the
    # one output meant to be pasted.
    lines = [
        f"post-draft checks over {source}",
        "",
        f"  check records read               {scan.records}",
        f"    clean                          {scan.clean}",
        f"    defect                         {scan.defect}",
        f"    neither verdict                {scan.unrecognized_verdict}",
        "",
        f"  checks the skill expects         {scan.expected}",
        f"    outside the table              {scan.outside_the_table}",
        "",
    ]
    for kind, count in scan.counts:
        lines.append(f"  {ROW_TICKET[kind]} - {kind:<{KIND_COLUMN}} {count}")
    lines.append("")
    lines.append(f"  checks at fault                  {scan.failing_checks}")
    if scan.missing:
        lines.append("")
        lines.append("  no heading for (named from the skill's own table, not from the file):")
        lines += [f"    {name}" for name in scan.missing]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<{KIND_COLUMN}} {finding.check}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    args = [a for a in argv if not a.startswith("--")]
    show = "--show" in argv
    if not args:
        print("usage: checks_ledger.py <a checks file> [--show]", file=sys.stderr)
        return 2
    path = Path(args[0])
    # The name, never the path: a checks file sits under ``scratch/``.
    if not path.is_file():
        print(f"no checks file named {path.name}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    records = read_records(text)
    if not records:
        # The limb that matters. A file written in a shape this cannot read would
        # otherwise report zero findings and stand where a checked draft should be.
        print(f"no check records found in {path.name}", file=sys.stderr)
        return 2
    scan = survey(records)
    print(format_report(scan, source=path.name, show=show))
    if scan.failing_checks:
        print(
            f"{scan.failing_checks} check(s) fail the #240 record contract."
            " Re-run with --show to see which, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
