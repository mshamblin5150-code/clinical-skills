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

**What it checks.** Every row is written into
``skills/practicum-case-study/SKILL.md`` step 9, so this grades what that step
states rather than holding a rule of its own. All but one belong to #240 and
``ROWS`` says which is which -- **how many there are is ``KINDS``'s to say
and is deliberately not counted here**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.
The exception is #255's, and it is the one place that sentence had to be earned
rather than inherited -- see the row below.

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
- **A ``clean`` on a check ``SUBSTANTIATED_CLEAN`` names carries a ``FINDINGS``
  too.**
  [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255), and it
  is the row above's test applied to the other verdict:
  ``research_ledger.py``'s ``BARE_STATUS`` argument, one skill over. Anybody can
  write ``clean``; nobody writes *"walked all five MDM entries, each names a
  discriminator from this case"* without having walked them.

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

**The sixth row is the one this module did not inherit, and the distinction is
worth keeping.** ``VERDICT: clean`` with an empty ``FINDINGS`` is
[#182](https://github.com/mshamblin5150-code/clinical-skills/issues/182)'s *a
block satisfies the gate by existing* -- **not reachable from a string test**,
because a check that ran and found nothing writes exactly what a check that
reported nothing writes. #240 named it *indistinguishable* and declined to grade
it, correctly: the only thing that reaches it is requiring the ``clean`` to say
what it examined, and that is a **change to what the step asks a reader to write**
rather than a grader of what it already asks. #240's brief was a grader, and the
line between the two is what this whole directory is careful about. So it went to
the clinician as #255 and came back ruled, and the step now asks for it -- which
is what makes grading it the same kind of row as the five above rather than a rule
this module invented.

**Some rows and not every row**, which is #255's third option rather than its
headline, and both halves of that are load-bearing. ``SUBSTANTIATED_CLEAN`` names
the checks where a wrong ``clean`` is most expensive; everywhere else the shape is
still exactly what #240 declared, and the by-eye reading in
``skills/practicum-case-study/SKILL.md`` step 9 is still the only thing that
reaches it. ``the reference list`` is the clearest of the ones left out -- it is
graded by ``reference_scan.py``, so its ``clean`` is a command's exit status and
there was never a reader to have walked anything. ``filled_vitals_census.py``'s
arrangement, and **the report names the graded rows on every run** rather than
only when the row fires, because *say which is which* is the clause a report drops
in silence.

**What it buys is a shape rather than a reading**, and that was priced rather than
glossed. A lazy reader satisfies it with one stock sentence --
``specificity_scan.py``'s R2 limit, inherited here as it is by every substance
test in this directory. What changes is that the records on the rows
``SUBSTANTIATED_CLEAN`` names stop being unfalsifiable and become checkable by
eye, which is what the walk in
``skills/practicum-case-study/SKILL.md`` step 9 is for and previously had
nothing to work with.

**No count of rows or of graded checks appears in this docstring, and both used to.**
``KINDS`` and ``SUBSTANTIATED_CLEAN`` are the ones that know, a floor is all any
test pins, and a seventh row would have left six sentences here wrong at once --
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving
inside the change that cites it, which this file records happening three times
already.

**What it cannot reach, and it is most of the file.** Every verdict is a reading.
Whether the differential's ``1.`` really is what would kill first, whether an MDM
entry's discriminator is from this case, whether the reader looked at the draft at
all -- none of it is in the record, and a well-formed ``clean`` from a reader that
skimmed is indistinguishable from one that read. **#255 narrows that on the rows
``SUBSTANTIATED_CLEAN`` names and does not close it**: a stock clause is still a clause. **A clean scan is not
a checked draft**, ``skills/practicum-case-study/SKILL.md`` says so beside the
command, and a test asserts that sentence is still there.

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

Since #405, the no-record limb prints the counts-only report before its
diagnostic and exit 2. Earlier versions returned first; the moved stdout makes
the coverage failure inspectable under the shared report-before-tier-2 rule.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import run_grader

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
    # Graded by ``tools/case_study_scan.py`` rather than by a reader, on
    # ``the reference list``'s terms and for its reason: the rules are
    # mechanical, so the row is a command. Added on
    # [#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277),
    # and it is first because it is the command row for the whole draft.
    "the house style",
    "the reference list",
    "the reference list, the part no command reaches",
    "differential ordering",
    "MDM completeness",
    "the Rx blocks",
    # A correspondence between two documents rather than a shape in one, which
    # is why it is its own row and not a clause in ``the Rx blocks``: that
    # reader opens the draft, this one opens the draft and the ledger, and a
    # reader holding two jobs is how a partial read comes back looking
    # complete. Added on
    # [#299](https://github.com/mshamblin5150-code/clinical-skills/issues/299).
    "the dose against the record that sourced it",
    # A per-patient reading across every applicable threshold sheet. The keys
    # and ``CONFLICT`` gate are sheet-local, so no directory command reaches
    # this correspondence. Added on
    # [#584](https://github.com/mshamblin5150-code/clinical-skills/issues/584).
    "the threshold sheets against this patient",
    # These are separate because the first is clinical judgment over the source
    # material and draft while the second needs rendered pages and vision. A
    # reader holding both jobs could return a partial walk as one complete one.
    # Added on
    # [#306](https://github.com/mshamblin5150-code/clinical-skills/issues/306).
    "the clinical decisions no command reaches",
    # The reader gets reconstructed text rather than the raw archive, because
    # Word draws list markers from ``numbering.xml`` and the paragraph text does
    # not contain them. Added on
    # [#423](https://github.com/mshamblin5150-code/clinical-skills/issues/423).
    "the numbering in context",
    "the rendered document",
    "the faculty's own to-do list",
)

# The checks where a ``clean`` has to say what it examined -- how many is this
# tuple's own business and is deliberately counted in no sentence about it, on
# [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
# terms: it read *two* in prose across this repo until #299 made it three, the
# sweep that repaired those copies missed several, and both axes of
# ``/code-review`` had to find the rest. --
# [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255), and it
# is that ticket's **third option** rather than its headline. The argument is
# ``research_ledger.py``'s ``BARE_STATUS``, one skill over: anybody can write
# ``clean``; nobody writes *"walked all nine entries against apa7.md section 3;
# all nine hang, all nine alphabetize"* without having walked them.
#
# **Some rows rather than every row, and the asymmetry is the ruling.** These are
# the checks where a wrong ``clean`` is most expensive, and the clinician declined
# to require it of the rest -- which keeps it off ``the reference list``, the one
# row graded by a command rather than by a reader, where a ``clean`` is a tool's
# exit status and there is nothing for a reader to have walked.
# ``filled_vitals_census.py``'s arrangement exactly: grade some rows, count the
# rest, and have the report say which is which.
SUBSTANTIATED_CLEAN = (
    "differential ordering",
    "MDM completeness",
    "the dose against the record that sourced it",
    "the threshold sheets against this patient",
    "the clinical decisions no command reaches",
    "the numbering in context",
    "the rendered document",
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
CLEAN_WITHOUT_FINDINGS = "clean-without-findings"

# Which ruling each row belongs to, so a reader knows which ticket to go and read.
# **Spelled out rather than built from ``KINDS``**, and that is the whole of what
# makes the sentence above it true: a comprehension would assign #240 to a row the
# next ticket adds, so the map could never fail and a claim that a row cannot
# arrive without a ticket would be a claim about code that does not check it.
# ``KINDS`` is ordered and this is keyed, so ``format_report`` raises rather than
# mislabelling.
ROWS = {
    MISSING_CHECK: "#240",
    DUPLICATE_CHECK: "#240",
    MISSING_VERDICT: "#240",
    UNKNOWN_VERDICT: "#240",
    DEFECT_WITHOUT_FINDINGS: "#240",
    CLEAN_WITHOUT_FINDINGS: "#255",
}
KINDS = tuple(ROWS)

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

def graded_keys(names: tuple[str, ...]) -> frozenset[str]:
    """Normalized lookup keys for checks a row grades, refusing any that is not a check.

    **A typo raises here rather than becoming a silent no-op row.** A check graded
    for a string no heading in the file can ever match reports nothing forever and
    reads exactly like a rule that is running -- which is the failure this whole
    directory exists to refuse, arriving in the grader's own vocabulary.
    ``ROWS``'s reasoning, at the one other place in this module where a name
    is typed twice.

    **A function rather than a bare module-level check** so the raise can be
    exercised. A guard whose only test re-asserts the property it protects is a
    guard nothing would notice the loss of.
    """
    keys = frozenset(normalize(name) for name in names)
    unknown = keys - set(_EXPECTED_KEYS)
    if unknown:
        raise ValueError(f"not a check the table names: {sorted(unknown)}")
    return keys


_SUBSTANTIATED_KEYS = graded_keys(SUBSTANTIATED_CLEAN)


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
    guess costs. So the character after the keyword has to be a boundary.

    **The same defect was latent in the sibling and is fixed there now** --
    ``STATUS: unsourced-but-see-below`` graded **clean**, the substance row
    satisfied by the residue of its own keyword, and ``RECENCY: nothing newerish``
    did the same one field over, standing the five-year window down on an old
    reference with no excuse. (``RECENCY: currently under review`` is the case that
    ticket's title names and it is the **weaker** one: ``current`` is not an excuse
    there, so the window fired anyway and only ``UNKNOWN_RECENCY`` was lost.)
    It was filed as
    [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) rather
    than reached into from here, because that module's rows had their own tests to
    move, and it landed with the discriminating cases written first: **no test
    there distinguished ``current`` from ``currently``**, so a green run after the
    change would have proved nothing on its own.

    This helper and ``normalize`` are **copied** from ``research_ledger.py`` rather
    than imported, and the divergence is what made the copy the right call at the
    time. **#253 adopted this rule there and neither module asserts the two agree
    today**: a helper two modules happen to have written the same way is not one
    that exists to be depended on, and a test pinning the agreement would forbid
    the divergence the copy exists to permit. ``console_codec.py`` is this
    directory's only module that does exist to be depended on.
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
class Finding(run_grader.Finding):
    """One check failing one row.

    ``check`` is the heading. It is the run's own text where the record exists,
    and one of ``EXPECTED_CHECKS`` where the row is ``MISSING_CHECK`` -- which is
    the only case ``format_report`` will name without ``--show``.
    """

    check: str
    detail: str


@dataclass(frozen=True)
class Scan:
    """Counts over one checks file, plus the findings ``--show`` prints."""

    records: int
    clean: int
    # The ``clean`` records split by **whether their check has to say what it
    # walked**, and never by whether they did: a bare clean on such a row is counted
    # in ``clean_required`` and failed by the row below. That is what lets the
    # report name which rows carry the requirement rather than leaving a reader to
    # infer it from a row that counted nothing -- ``filled_vitals_census``'s
    # grade-some-count-the-rest arrangement, and the clause of it a report drops in
    # silence.
    clean_required: int
    clean_not_required: int
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


def _must_say_what_it_walked(record: Record) -> bool:
    """Is this a ``clean`` on a check whose ``clean`` has to carry a ``FINDINGS``?

    **Whether the row applies, never whether the record satisfied it**, and the
    name says *must* for that reason. The report's two counts are rows and not
    records that complied; a label reading ``saying what it walked`` reported a
    bare ``clean`` as having done the one thing it had not.
    """
    return record.verdict == CLEAN and normalize(record.check) in _SUBSTANTIATED_KEYS


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
    if _must_say_what_it_walked(record) and not SUBSTANCE.search(record.value("FINDINGS")):
        # #255, on the checks ``SUBSTANTIATED_CLEAN`` names. The row above's test,
        # applied to the other verdict and where a wrong one is most expensive. The
        # two cannot both fire: ``verdict`` is one word.
        found.append(Finding(CLEAN_WITHOUT_FINDINGS, check, record.value("VERDICT")))
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
        clean_required=sum(1 for r in records if _must_say_what_it_walked(r)),
        clean_not_required=sum(
            1 for r in records if r.verdict == CLEAN and not _must_say_what_it_walked(r)
        ),
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
        # **"must say", not "says".** These two count the *rows*, not the
        # records that complied -- a bare clean on a graded row is counted
        # here and failed below, and a label reading ``saying what it walked``
        # would have reported it as having done so. Caught by rendering the
        # report over a file of bare cleans rather than by reading the code.
        f"      must say what it walked      {scan.clean_required}",
        f"      not graded for it            {scan.clean_not_required}",
        f"    defect                         {scan.defect}",
        f"    neither verdict                {scan.unrecognized_verdict}",
        "",
        f"  checks the skill expects         {scan.expected}",
        f"    outside the table              {scan.outside_the_table}",
        "",
    ]
    for kind, count in scan.counts:
        lines.append(f"  {ROWS[kind]} - {kind:<{KIND_COLUMN}} {count}")
    lines.append("")
    lines.append(f"  checks at fault                  {scan.failing_checks}")
    if scan.missing:
        lines.append("")
        lines.append("  no heading for (named from the skill's own table, not from the file):")
        lines += [f"    {name}" for name in scan.missing]
    # Printed on every run rather than only when the row fires, because *say which
    # is which* is the half of the grade-some-count-the-rest arrangement a report
    # can drop in silence -- and a reader who cannot see which rows carry the
    # requirement reads an ungraded clean as a checked one. These strings
    # are ``SUBSTANTIATED_CLEAN`` members, so they are this module's own text on
    # exactly the terms the missing-check list is.
    lines.append("")
    lines.append("  a clean must say what it walked on (named from this module's own tuple):")
    lines += [f"    {name}" for name in SUBSTANTIATED_CLEAN]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<{KIND_COLUMN}} {finding.check}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    path: Path
    records: tuple[Record, ...]


def _load(parsed: run_grader.Parsed) -> Source:
    path = Path(parsed.source)
    if not path.is_file():
        raise run_grader.SourceError(f"no checks file named {path.name}")
    text = path.read_text(encoding="utf-8", errors="replace")
    return Source(path, tuple(read_records(text)))


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(list(source.records))
    if not source.records:
        # No record was parsed, so no row was applied. Keep the report's shape
        # without turning an unscanned source into six findings by construction.
        scan = replace(
            scan,
            counts=tuple((kind, 0) for kind in KINDS),
            failing_checks=0,
            missing=(),
            findings=(),
        )
    diagnostics: list[str] = []
    if not source.records:
        diagnostics.append(f"no check records found in {source.path.name}")
    if scan.failing_checks:
        tickets = sorted({ROWS[kind] for kind, count in scan.counts if count})
        diagnostics.append(
            f"{scan.failing_checks} check(s) fail the record contract"
            f" ({', '.join(tickets)})."
            " Re-run with --show to see which, and do not paste that output."
        )
    return run_grader.Grade(
        scan=scan,
        source=source.path.name,
        findings_failed=bool(scan.failing_checks),
        coverage_failed=not source.records,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage="usage: checks_ledger.py <a checks file> [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
