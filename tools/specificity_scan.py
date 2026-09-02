"""Grade the ``SPECIFICITY`` flags on a run of ``icd10-cpt``.

    python tools/specificity_scan.py <a run directory> [--show]
    python tools/specificity_scan.py <a run directory> --brief
    python tools/specificity_scan.py <a run directory> --second-read <record.json>

``fixtures/filled-anchor`` **C5** is this, and [#56] is why it exists. The
``icd10-cpt`` step-3 template used to read ``SPECIFICITY: <complete | needs: ...>``,
so a bare ``complete`` was compliant output -- and a run that never opened a code
produced the identical line to one that opened every code and found no axis left.
The two are indistinguishable on the page, which is the same silent-failure shape
the whole ``filled-anchor`` set exists for.

**One enforced test, plus one advisory count.**

- **A flag carries substance beyond its keyword.** ``complete`` and ``needs:``
  both fail; ``complete -- I10 has no further axis`` and ``needs: site`` both
  pass. The reason is the evidence that the check happened. Nobody writes *"Z98.51
  has no further axis"* without having looked at ``Z98.51``'s axes; anybody can
  write ``complete``. **This reaches both branches deliberately** -- a ``needs:``
  naming no axis is the same defect wearing the other keyword.
- **A descriptor saying "unspecified" and flagged ``complete`` is counted for
  review, but does not fail C5 when the flag carries a reason.** Most instances
  name an axis the bedside could supply, but ``R00.1 Bradycardia, unspecified``
  and ``R19.7 Diarrhea, unspecified`` do not. No string test separates those
  cases. The reason lets a reader judge the distinction; the count makes the
  review surface visible without forcing a semantically false ``needs:``.

**What the first pass does not test, and cannot.** Whether a substantive reason is
true. [#154] found four reasons in ``filled-anchor/run-2`` that were specific,
checkable, and false. ``--brief`` now gives a fresh reader code numbers and no
worksheet answers; ``--second-read`` binds that reader's complete three-character
categories, descriptors, billability values, and inherited tabular notes to the
committed database. The reader's prose is paired with the original reason under
``--show`` and deliberately
not machine-graded. Agreement is a smoke test, never proof.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record. A
code with its descriptor is a diagnosis attached to an encounter, so nothing but
integers is printed unless ``--show`` asks; **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, which
``guidelines_search.py`` is the precedent for: 0 when every flag passes, 1 when C5
fails, and **2 for every way of not having scanned** -- no directory, no
worksheets in it, no argument at all. A run whose output landed somewhere else
would otherwise report a clean set of flags and look like a pass.

Extractor limits worth knowing before quoting a number:

- An entry opens on a line beginning ``ICD-10``, ``CPT`` or ``HCPCS`` followed by
  a code and a descriptor, and a ``SPECIFICITY`` line is paired with the most
  recent one above it. A run that writes its worksheet some other way reads here
  as having flagged nothing, which is a floor on every count and **not** on the
  exit status -- the bare-flag test still fires on an unpaired flag, because it
  needs no descriptor.
- A **differential** entry is graded on nothing, and that is enforced rather than
  assumed. It is *supposed* to carry three parts and no ``SPECIFICITY`` line --
  but a run that writes one anyway would be graded against a descriptor reading
  ``..., unspecified`` **by design**, because the skill codes a differential at
  the unspecified level on purpose. So a flag on a ``NOT FOR ENTRY`` line is
  parsed, counted, and exempt from both the C5 test and the advisory; writing one is a C4 failure, which
  counts parts, and C5 firing as well would name the wrong row. The count is
  printed rather than dropped, because a non-zero there is worth going to look at.
- ``Other ...`` is not ``unspecified``. ``R06.89 Other abnormalities of breathing``
  says the finding fits no named code, not that the documentation is thin, and it
  reads ``complete`` with a reason like anything else. ``Other specified ...`` is
  likewise not ``not specified``.
- A flag whose value starts with neither keyword is counted as unrecognized and
  **fails nothing**. The template names two branches; policing a third would be
  this script inventing a rule the skill does not state.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

import run_grader
import aar_scan

EXPECTED_COMPLETION_CHECKS = (aar_scan.EXPECTED_ROW,)
from icd10_lookup import CATEGORY_LENGTH, describe, normalize, notes_for, open_database

# ``ICD-10  M19.90  Unspecified osteoarthritis, unspecified site``. The trailing
# ``NOT FOR ENTRY`` mark belongs to the differential shape and is not descriptor.
ENTRY = re.compile(
    r"(?mi)^[ \t]*(ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    r"([A-Z0-9][A-Z0-9.]*)[ \t]+(.+?)[ \t]*$"
)
SPECIFICITY = re.compile(r"(?mi)^[ \t]*SPECIFICITY[ \t]*:[ \t]*(.*?)[ \t]*$")

# A code's own parts. These close an entry's header, so ``NOT FOR ENTRY`` is
# looked for above the first of them and never in the prose below.
FIELD = re.compile(r"(?mi)^[ \t]*(?:ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:")

# ``NOT FOR ENTRY`` at the end of any line of the entry's header, not only the
# code's own. **An official descriptor can run past a line** -- ``K27.9 Peptic
# ulcer, site unspecified, unspecified as acute or chronic, without hemorrhage or
# perforation`` is 96 characters -- and the mark then lands on the continuation. A
# single-line reading calls such an entry for-entry and then grades it on the
# descriptor test, which fires on ``..., unspecified`` **by design** in a
# differential. So the wrap produced a false C5 finding on exactly the shape the
# exemption below exists to protect. Found by a reader, in the run [#124]
# committed; no flag in that run was affected, because none of its wrapped
# differential entries carries a ``SPECIFICITY`` line at all.
NOT_FOR_ENTRY = re.compile(r"(?mi)[ \t]NOT FOR ENTRY[ \t]*$")

# The code set's own words for *an axis exists and this code does not name it*.
# ``Other specified ...`` is deliberately outside it -- see the module docstring.
UNSPECIFIED = re.compile(r"(?i)\bunspecified\b|\bnot specified\b")

# Anything alphanumeric after the keyword is substance. Judging whether it is a
# real check is R2's, and is not available to a string test.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")

BARE = "bare-flag"
UNSPECIFIED_COMPLETE = "unspecified-complete"
ROWS = {
    BARE: "fixtures/filled-anchor C5 - specificity flag carries substance",
    UNSPECIFIED_COMPLETE: "fixtures/filled-anchor C5 - unspecified descriptor advisory",
}
KINDS = tuple(ROWS)

SECOND_READ_IS_A_SMOKE_TEST = (
    "a separated second read is a smoke test and never proof: two readers can "
    "misread the same code family the same way, so agreement is cheap"
)
SECOND_READ_CODE_FIELDS = (
    "code",
    "family",
    "about",
)
SECOND_READ_FACT_FIELDS = ("code", "descriptor", "billable", "notes")


@dataclass(frozen=True)
class Flag:
    """One ``SPECIFICITY`` line and the entry it belongs to."""

    code: str
    descriptor: str
    keyword: str
    remainder: str
    value: str
    for_entry: bool = True
    system: str = ""

    @property
    def has_substance(self) -> bool:
        return bool(SUBSTANCE.search(self.remainder))


@dataclass(frozen=True)
class WorksheetEntry:
    """One code entry, including entries whose required specificity line is absent."""

    start: int
    system: str
    code: str
    descriptor: str
    for_entry: bool


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One flag raised as a C5 failure or an advisory."""

    code: str
    descriptor: str
    value: str


@dataclass(frozen=True)
class Scan:
    """Counts over a set of worksheets, plus the findings ``--show`` prints."""

    worksheets: int
    flags: int
    complete_flags: int
    needs_flags: int
    unrecognized_flags: int
    # A flag on a ``NOT FOR ENTRY`` line. C5 grades none of these, and the count is
    # reported rather than dropped: a differential is not supposed to carry one at
    # all, so a non-zero here is a C4 matter the reader should go looking at.
    not_for_entry_flags: int
    bare_flags: int
    unspecified_complete: int
    # ``unspecified_complete`` is advisory and does not contribute to this count.
    failing_flags: int = 0
    findings: tuple[Finding, ...] = ()
    advisories: tuple[Finding, ...] = ()


@dataclass
class SecondRead:
    """A separated reading, or the reason the file cannot be read as one."""

    path: Path
    codes: list[dict] = field(default_factory=list)
    read_on: str | None = None
    ok: bool = True
    why_not: str | None = None


@dataclass(frozen=True)
class SecondReadGate:
    """The machine verdict plus prose pairings it deliberately does not grade."""

    refusals: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    pairings: tuple[str, ...] = ()
    uncovered: tuple[str, ...] = ()


def _keyword(value: str) -> tuple[str, str]:
    """Split a flag value into its branch keyword and everything after it."""
    stripped = value.lstrip()
    lowered = stripped.lower()
    for keyword in ("complete", "needs"):
        if lowered.startswith(keyword):
            return keyword, stripped[len(keyword) :]
    return "", stripped


def read_entries(text: str) -> list[WorksheetEntry]:
    """Every code entry, whether or not its required ``SPECIFICITY`` line exists."""
    found = list(ENTRY.finditer(text))

    def header(index: int) -> str:
        """One entry's lines up to its first field line or the next entry.

        The span rather than the line, because a descriptor that wraps puts
        ``NOT FOR ENTRY`` on the continuation. Bounded on both sides so the mark
        cannot be borrowed from the entry below or from prose beneath the code.
        """
        start = found[index].start()
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        field = FIELD.search(text, start, end)
        return text[start : field.start() if field else end]

    return [
        WorksheetEntry(
            start=match.start(),
            system=match.group(1),
            code=match.group(2),
            descriptor=match.group(3),
            for_entry=not NOT_FOR_ENTRY.search(header(index)),
        )
        for index, match in enumerate(found)
    ]


def read_flags(text: str) -> list[Flag]:
    """Every ``SPECIFICITY`` line in one worksheet, paired with its entry.

    Pairing is positional -- the most recent entry line above the flag -- because
    the skill's template puts the two three lines apart and nothing else in the
    output carries a code and its official descriptor on one line.
    """
    entries = read_entries(text)
    flags: list[Flag] = []
    for match in SPECIFICITY.finditer(text):
        system, code, descriptor, for_entry = "", "", "", True
        for entry in entries:
            if entry.start < match.start():
                system = entry.system
                code = entry.code
                for_entry = entry.for_entry
                descriptor = NOT_FOR_ENTRY.sub("", entry.descriptor)
            else:
                break
        keyword, remainder = _keyword(match.group(1))
        flags.append(
            Flag(
                code=code,
                descriptor=descriptor,
                keyword=keyword,
                remainder=remainder,
                value=match.group(1),
                for_entry=for_entry,
                system=system,
            )
        )
    return flags


def for_entry_icd10(items: list[list[Flag | WorksheetEntry]]) -> list[Flag | WorksheetEntry]:
    """The one eligibility walk shared by the brief and its coverage gate."""
    return [
        item
        for worksheet in items
        for item in worksheet
        if item.for_entry and item.system.upper().startswith("ICD") and item.code
    ]


def brief(per_worksheet: list[list[Flag | WorksheetEntry]], source: str) -> str:
    """A locator-only work order for a reader who cannot see the worksheets.

    A code is enough to open the committed release. Descriptors and flags are the
    answers being checked, so neither crosses this boundary. ``source`` is accepted
    for symmetry with ``format_report`` but deliberately not printed: run directory
    names can carry a date or site.
    """
    del source
    codes = sorted({item.code for item in for_entry_icd10(per_worksheet)})
    lines = [
        "== a separated second read of ICD-10-CM specificity",
        "",
        "Open every code below in reference/icd10cm-2026.sqlite. Inspect whatever",
        "parents, children, siblings, and tabular notes bear on its specificity.",
        "Do not consult the worksheets or an existing SPECIFICITY reason: this read",
        "is worth what its independence is worth.",
        "",
    ]
    lines.extend(f"  {code}" for code in codes)
    lines += [
        "",
        "Write the result as JSON. Family is EVERY code in the subject's complete",
        "three-character category, with exact release facts. About is the independent",
        "reading in your own words:",
        "",
        '  {"read_on": "<YYYY-MM-DD>",',
        '   "codes": [{"code": "<subject code>",',
        '              "family": [{"code": "<category code>",',
        '                          "descriptor": "<official descriptor>",',
        '                          "billable": <true | false>,',
        '                          "notes": [{"code": "<where written>",',
        '                                     "kind": "<tabular note kind>",',
        '                                     "text": "<exact note text>"}]}],',
        '              "about": "<what the release shows about specificity>"}]}',
        "",
        f"  {SECOND_READ_IS_A_SMOKE_TEST}.",
    ]
    return "\n".join(lines) + "\n"


def _record_problem(record: object, position: str, subject: bool) -> str | None:
    """Return why one subject/evidence record is not structurally gradeable."""
    if not isinstance(record, dict):
        return f"{position} is not an object"
    required = SECOND_READ_CODE_FIELDS if subject else SECOND_READ_FACT_FIELDS
    missing = [name for name in required if name not in record]
    if missing:
        return f"{position} has no {', '.join(missing)}"
    strings = ("code",) + (("about",) if subject else ("descriptor",))
    empty = [name for name in strings if not str(record.get(name, "")).strip()]
    if empty:
        return f"{position} has an empty {', '.join(empty)}"
    if subject:
        family = record.get("family")
        if not isinstance(family, list) or not family:
            return f"{position} family is not a non-empty list"
        seen: set[str] = set()
        for family_position, fact in enumerate(family, start=1):
            problem = _record_problem(
                fact, f"{position} family {family_position}", subject=False
            )
            if problem:
                return problem
            fact_code = normalize(str(fact["code"]))
            if fact_code in seen:
                return f"{position} family repeats {fact['code']}"
            seen.add(fact_code)
        return None
    if not isinstance(record.get("billable"), bool):
        return f"{position} billable is not true or false"
    notes = record.get("notes")
    if not isinstance(notes, list):
        return f"{position} notes is not a list"
    for note_position, note in enumerate(notes, start=1):
        if not isinstance(note, dict):
            return f"{position} note {note_position} is not an object"
        absent = [name for name in ("code", "kind", "text") if not str(note.get(name, "")).strip()]
        if absent:
            return f"{position} note {note_position} has no {', '.join(absent)}"
    return None


def load_second_read_record(loaded: object, path: Path) -> SecondRead:
    """Parse the record's shape. Release facts are checked by ``gate_second_read``."""
    if not isinstance(loaded, dict):
        return SecondRead(path=path, ok=False, why_not="the file is not a JSON object")
    if "codes" not in loaded or not isinstance(loaded.get("codes"), list):
        return SecondRead(path=path, ok=False, why_not="no 'codes' list, so nothing was read")
    read_on = loaded.get("read_on")
    try:
        dt.date.fromisoformat(str(read_on))
    except (TypeError, ValueError):
        return SecondRead(path=path, ok=False, why_not="no ISO 'read_on' date")
    seen: set[str] = set()
    for position, record in enumerate(loaded["codes"], start=1):
        problem = _record_problem(record, f"code {position}", subject=True)
        if problem:
            return SecondRead(path=path, ok=False, why_not=problem)
        code = normalize(str(record["code"]))
        if code in seen:
            return SecondRead(path=path, ok=False, why_not=f"code {record['code']} appears twice")
        seen.add(code)
    return SecondRead(path=path, codes=loaded["codes"], read_on=str(read_on))


def load_second_read(path: Path) -> SecondRead:
    if not path.is_file():
        return SecondRead(path=path, ok=False, why_not=f"no such file: {path.name}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        return SecondRead(
            path=path,
            ok=False,
            why_not=f"unreadable {path.name}: {error.__class__.__name__}",
        )
    except ValueError as error:
        return SecondRead(
            path=path,
            ok=False,
            why_not=f"unreadable {path.name}: invalid JSON at line {error.lineno}",
        )
    return load_second_read_record(loaded, path)


def _note_tuples(record: dict) -> list[tuple[str, str, str]]:
    return sorted(
        (normalize(str(note["code"])), str(note["kind"]), str(note["text"]))
        for note in record["notes"]
    )


def _fact_refusals(
    fact: dict, connection: sqlite3.Connection, label: str
) -> list[str]:
    code = normalize(str(fact["code"]))
    official = describe(connection, code)
    if official is None:
        return [f"{label} {fact['code']} is not in ICD-10-CM FY2026"]
    refusals: list[str] = []
    if fact["descriptor"] != official.long:
        refusals.append(f"{label} {fact['code']} descriptor disagrees with FY2026")
    if fact["billable"] is not official.billable:
        refusals.append(f"{label} {fact['code']} billable disagrees with FY2026")
    official_notes = sorted((note.code, note.kind, note.text) for note in notes_for(connection, code))
    if _note_tuples(fact) != official_notes:
        refusals.append(f"{label} {fact['code']} notes disagree with FY2026")
    return refusals


def _family_refusals(record: dict, connection: sqlite3.Connection, label: str) -> list[str]:
    """Bind a reader's complete category walk to the release that defines it."""
    subject = normalize(str(record["code"]))
    category = subject[:CATEGORY_LENGTH]
    official_codes = {
        row[0]
        for row in connection.execute(
            "SELECT code FROM code WHERE code LIKE ? ORDER BY code", (category + "%",)
        )
    }
    recorded_codes = {normalize(str(fact["code"])) for fact in record["family"]}
    refusals: list[str] = []
    if subject not in official_codes:
        refusals.append(f"{label} {record['code']} is not in ICD-10-CM FY2026")
    if recorded_codes != official_codes:
        refusals.append(f"{label} {record['code']} family coverage disagrees with FY2026")
    for fact in record["family"]:
        refusals.extend(_fact_refusals(fact, connection, f"{label} {record['code']} family"))
    return refusals


def gate_second_read(
    per_worksheet: list[list[Flag]],
    read: SecondRead,
    connection: sqlite3.Connection,
    entries: list[list[WorksheetEntry]] | None = None,
) -> SecondReadGate:
    """Check cited facts and pair, but never grade, the two specificity readings."""
    expected_flags = for_entry_icd10(per_worksheet)
    expected_subjects = for_entry_icd10(entries) if entries is not None else expected_flags
    expected_codes = {normalize(item.code): item.code for item in expected_subjects}
    expected = set(expected_codes)
    records = {normalize(str(record["code"])): record for record in read.codes}
    refusals: list[str] = []
    warnings: list[str] = []
    for code, record in records.items():
        label = "subject" if code in expected else "off-brief subject"
        refusals.extend(_family_refusals(record, connection, label))
        if code not in expected:
            warnings.append(f"{record['code']} was read but no worksheet requested it")
    uncovered = [expected_codes[code] for code in sorted(expected - records.keys())]
    pairings = [
        f"{flag.code}  SPECIFICITY: {flag.value}  <>  SECOND READ: {records[normalize(flag.code)]['about']}"
        for flag in expected_flags
        if normalize(flag.code) in records
    ]
    return SecondReadGate(
        refusals=tuple(refusals),
        warnings=tuple(warnings),
        pairings=tuple(pairings),
        uncovered=tuple(uncovered),
    )


def flag_findings(flag: Flag) -> list[Finding]:
    """C5's enforced test, applied to one flag.

    **A flag on a ``NOT FOR ENTRY`` line is neither graded nor advisory-counted.** A differential is
    coded at the unspecified level *on purpose* -- ``icd10-cpt`` says so and drops
    the specificity part from that shape entirely -- so an entry whose descriptor
    reads ``..., unspecified`` by design is not evidence that anybody failed to
    look. A run that writes a ``SPECIFICITY`` line there has already broken C4,
    which counts parts; firing C5 as well would name the wrong row and point at a
    descriptor the skill asked for.
    """
    found: list[Finding] = []
    if not flag.for_entry:
        return found
    if flag.keyword and not flag.has_substance:
        found.append(Finding(BARE, flag.code, flag.descriptor, flag.value))
    return found


def findings(flags: list[Flag]) -> list[Finding]:
    """Every finding across a set of flags, in flag order."""
    return [finding for flag in flags for finding in flag_findings(flag)]


def advisory_findings(flags: list[Flag]) -> list[Finding]:
    """Every ``complete`` on an unspecified for-entry code."""
    return [
        Finding(UNSPECIFIED_COMPLETE, flag.code, flag.descriptor, flag.value)
        for flag in flags
        if flag.for_entry
        and flag.keyword == "complete"
        and UNSPECIFIED.search(flag.descriptor)
    ]


def survey(per_worksheet: list[list[Flag]]) -> Scan:
    """Count across a run. Takes parsed flags rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift."""
    flags = [flag for sheet in per_worksheet for flag in sheet]
    found = findings(flags)
    advisories = advisory_findings(flags)
    return Scan(
        worksheets=len(per_worksheet),
        flags=len(flags),
        complete_flags=sum(1 for f in flags if f.keyword == "complete"),
        needs_flags=sum(1 for f in flags if f.keyword == "needs"),
        unrecognized_flags=sum(1 for f in flags if not f.keyword),
        not_for_entry_flags=sum(1 for f in flags if not f.for_entry),
        bare_flags=sum(1 for f in found if f.kind == BARE),
        unspecified_complete=len(advisories),
        failing_flags=sum(1 for flag in flags if flag_findings(flag)),
        findings=tuple(found),
        advisories=tuple(advisories),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no code and no descriptor unless ``show``."""
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console, where a middle dot outside cp1252 comes back as a question
    # mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"specificity scan over {source}",
        "",
        f"  worksheets read                  {scan.worksheets}",
        f"  SPECIFICITY flags                {scan.flags}",
        f"    complete                       {scan.complete_flags}",
        f"    needs                          {scan.needs_flags}",
        f"    neither keyword                {scan.unrecognized_flags}",
        f"    on a NOT FOR ENTRY line        {scan.not_for_entry_flags}",
        "",
        f"  C5 - flag carries no reason      {scan.bare_flags}",
        f"  advisory - complete on unspecified {scan.unspecified_complete}",
        f"  C5 - flags at fault              {scan.failing_flags}",
    ]
    if show:
        for heading, details in (
            ("findings", scan.findings),
            ("advisories", scan.advisories),
        ):
            if details:
                lines += ["", f"  {heading} (PHI - read, do not paste):"]
                for finding in details:
                    lines.append(
                        f"    {finding.kind:<22} {finding.code:<9} "
                        f"SPECIFICITY: {finding.value}  [{finding.descriptor}]"
                    )
    return "\n".join(lines)


def read_worksheets(directory: Path) -> list[str]:
    """The text of every worksheet in ``directory``, README excluded.

    A run's README is prose about the run; counting it would put a wrong
    denominator beside every figure below it.
    """
    return [
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and path.stem.lower() != "readme"
    ]


def format_second_read_report(gate: SecondReadGate, show: bool) -> str:
    """Counts by default; the prose pairing is sensitive and requires ``--show``."""
    state = (
        "NOT COMPLETE"
        if gate.uncovered
        else "DEFECT FOUND"
        if gate.refusals
        else "complete"
    )
    lines = [
        "separated specificity read",
        "",
        f"  state                           {state}",
        f"  source fact(s) at fault         {len(gate.refusals)}",
        f"  off-brief code(s)               {len(gate.warnings)}",
        f"  subject code(s) uncovered       {len(gate.uncovered)}",
        f"  prose pairing(s), ungraded      {len(gate.pairings)}",
    ]
    if not gate.uncovered and gate.pairings:
        lines += ["", f"  {SECOND_READ_IS_A_SMOKE_TEST}."]
    if show:
        lines += ["", "  UNGRADED pairings (PHI - read, do not paste):"]
        lines.extend(f"    {pairing}" for pairing in gate.pairings)
        if gate.refusals:
            lines += ["", "  release findings:"]
            lines.extend(f"    {finding}" for finding in gate.refusals)
        if gate.warnings:
            lines += ["", "  warnings:"]
            lines.extend(f"    {warning}" for warning in gate.warnings)
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    directory: Path
    per_worksheet: tuple[tuple[Flag, ...], ...]
    per_worksheet_entries: tuple[tuple[WorksheetEntry, ...], ...]


def _load(parsed: run_grader.Parsed) -> Source:
    directory = Path(parsed.source)
    if not directory.is_dir():
        raise run_grader.SourceError(f"no directory named {directory.name}")
    worksheets = read_worksheets(directory)
    if not worksheets:
        raise run_grader.SourceError(f"no worksheets found in {directory.name}")
    return Source(
        directory,
        tuple(tuple(read_flags(text)) for text in worksheets),
        tuple(tuple(read_entries(text)) for text in worksheets),
    )


def _validate(parsed: run_grader.Parsed) -> str | None:
    if parsed.enabled("--brief") and (parsed.show or parsed.value("--second-read") is not None):
        return "--brief cannot be combined with --show or --second-read"
    return None


def _grade(
    source: Source, parsed: run_grader.Parsed
) -> run_grader.Grade[Scan] | run_grader.EarlyExit:
    per_worksheet = [list(flags) for flags in source.per_worksheet]
    per_worksheet_entries = [list(entries) for entries in source.per_worksheet_entries]
    if parsed.enabled("--brief"):
        return run_grader.EarlyExit(
            status=0,
            stdout=(brief(per_worksheet_entries, source=source.directory.name),),
            stderr=(
                "brief output contains diagnosis codes and is PHI - redirect it into scratch/; "
                "do not paste it",
            ),
        )

    scan = survey(per_worksheet)
    diagnostics: list[str] = []
    reports: list[str] = []
    second_gate: SecondReadGate | None = None
    second_read = parsed.value("--second-read")
    coverage_failed = False
    if second_read is not None:
        second_read_path = Path(second_read)
        read = load_second_read(second_read_path)
        if not read.ok:
            diagnostics.append(f"\nseparated read not graded: {read.why_not}")
            coverage_failed = True
        else:
            try:
                connection = open_database()
            except FileNotFoundError:
                diagnostics.append(
                    "\nseparated read not graded: the committed ICD-10-CM database is missing"
                )
                coverage_failed = True
            else:
                try:
                    second_gate = gate_second_read(
                        per_worksheet,
                        read,
                        connection,
                        entries=per_worksheet_entries,
                    )
                finally:
                    connection.close()
                reports.append("\n" + format_second_read_report(second_gate, show=parsed.show))

    findings_failed = bool(scan.failing_flags)
    if scan.failing_flags:
        findings_count = len(scan.findings)
        detail = "" if findings_count == scan.failing_flags else f" ({findings_count} findings)"
        diagnostics.append(
            f"\n{scan.failing_flags} flag(s) fail fixtures/filled-anchor C5{detail}."
            " Re-run with --show to see which, and do not paste that output."
        )
    if second_gate and second_gate.refusals:
        findings_failed = True
        diagnostics.append(
            f"\n{len(second_gate.refusals)} source fact(s) fail the separated read. "
            "Re-run with --show to see which, and do not paste that output."
        )
    if second_gate and second_gate.uncovered:
        coverage_failed = True
    aar_failed, aar_report = aar_scan.completion_gate(
        source.directory, parsed.value("--submission")
    )
    return run_grader.Grade(
        scan=scan,
        source=source.directory.name,
        findings_failed=findings_failed or aar_failed,
        coverage_failed=coverage_failed,
        diagnostics=tuple(diagnostics),
        reports=tuple(reports) + (aar_report,),
    )


GRADER = run_grader.Grader(
    usage=(
        "usage: specificity_scan.py <a run directory> "
        "[--show | --brief | --second-read <record.json>] [--submission <key>]"
    ),
    options=(
        run_grader.Option("--show"),
        run_grader.Option("--brief"),
        run_grader.Option(
            "--second-read",
            takes_value=True,
            missing_value="--second-read needs a JSON path",
            repeatable=False,
        ),
        run_grader.Option("--submission", takes_value=True, missing_value="--submission needs a key", repeatable=False),
    ),
    load=_load,
    grade=_grade,
    format_report=format_report,
    validate=_validate,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    return run_grader.run(GRADER, argv)
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
