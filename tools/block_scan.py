"""Grade the block-structure rows on a run of ``clinical-note``.

    python tools/block_scan.py <a run directory> [--show]

``fixtures/day-a`` **F1, F2 and F3** are this. They are the three rows in that
set's block-structure table a string test can settle, and [#120]'s own comment
asks for it by name -- *put any grader in ``tools/``* -- because the four graders
that scored ``filled-anchor`` run 1 were written into the run directory and went
with it when the worktree was removed.

**Three tests, and none needs a reader.**

- **F1** -- ``Primary Payment Method`` never opens a ``GAPS`` entry. It carries a
  **declared rule** in ``reference/medatrax-fields.md``, so it is filled from that
  rule rather than reported missing, and a GAPS entry for it is the block teaching
  the clinician to skim.
- **F2** -- start and end times never open a ``GAPS`` entry. They are estimated by
  design and say so where they appear; *estimated* is a property of the value, not
  the absence of one.
- **F3** -- ``Race/Ethnicity`` appears under ``FILLED·asserted`` and never opens a
  ``GAPS`` entry. **Two limbs**, and the second is why the row is not simply F1's
  twin: a declared administrative value is a claim about the patient, so a block
  naming it nowhere has dropped it rather than passed by omission.

**A row fires on what opens an entry, never on a mention inside one**, and that is
the whole reason this is safe to run unattended. A GAPS entry reading *"Site and
preceptor. Not in the source. The site also decides the payment method above."* is
**compliant** -- its subject is the site, the payment method was filled, and the
sentence is explaining the dependency. An earlier draft of this file matched any
mention and called three such sentences failures. Every violation these rows
describe opens an entry; nothing that opens an entry is prose about the rule.

**What it does not test, and cannot.** F4 -- whether every ``FLAG`` names both the
finding and what was not done with it. ``BP 151/93 undiscussed`` passes and
``vitals not addressed`` fails, and telling those apart is reading a sentence for
whether it names a thing, not matching a string. F5, F6 and F7 turn on one case's
age and sex and are questions about an input this cannot see. All four stay
counted by a reader.

**The entry boundary is a reading, and [#127] is why it has to be.** An entry
opens at a label line or a bullet; every other indented line is a **wrap** of the
entry above it. That is right for a run repeating the label per entry, which is
what ``day-a`` run 2 does, and it is a **floor** on a run using the canonical
aligned-continuation form, where several entries share one label and only the
first opens the item this grades. So the wrap count is printed beside the
findings, and an aligned line that *would* have opened a matching entry is
reported as a **candidate** rather than a failure -- counted, ``--show``-able, and
not touching the exit status, on the arrangement ``specificity_scan.py`` uses for
a flag on a ``NOT FOR ENTRY`` line. A non-zero there is worth going to look at.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record. A
GAPS entry names what an encounter did not supply about a person, so nothing but
integers is printed unless ``--show`` asks; **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, on
``specificity_scan.py``'s and ``differential_scan.py``'s arrangement: 0 clean, 1
for an F1-F3 violation, and **2 for every way of not having scanned** -- no
directory, no notes in it, no argument, and **no tier block in any note read**.
That last limb is the one that matters here: a run writing its block in a shape
this parser does not read would otherwise report zero violations and look like a
pass, which is exactly what ``differential_scan.py`` found when it met the twelve
committed ``day-b`` notes.

One more extractor limit worth knowing before quoting a number: ``FILLED-asserted``
and ``FILLED.asserted`` are read as ``FILLED·asserted``, because a run that lost
the middle dot to an encoding is a formatting matter and not one of these rows.
And **F3's second limb matches anywhere under ``FILLED·asserted``**, wraps
included, so an entry merely mentioning race satisfies it -- judging whether the
value is the declared one takes the reference file and a reader.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ASSERTED = "FILLED·asserted"
PROPOSED = "FILLED·proposed"
GAPS = "GAPS"
LABELS = ("DERIVED", ASSERTED, PROPOSED, "FLAG", GAPS, "UNKNOWN")

# ``FLAG  BP 141/93 undiscussed``, ``**GAPS**  Marital status``, ``- GAPS``.
# The separator in the two FILLED labels is the skill's middle dot; a hyphen or a
# period is read as the same label rather than as a different one.
#
# **Two restrictions here are load-bearing, and both were found by a review after
# each had already produced a wrong number.**
#
# **Case-sensitive.** An earlier version carried ``re.IGNORECASE``, which made
# ordinary prose open a section -- ``Unknown whether the patient smokes.`` and
# ``Gaps in the history remain.`` both matched, so any note containing such a
# sentence read as carrying a block and the exit-2 limb below could not fire. The
# skill writes all six labels in capitals; only the suffix of the two FILLED
# labels varies in case, and only that is matched loosely.
#
# **At the left margin.** An earlier version allowed leading whitespace, so a
# *wrapped* line beginning with a label word re-opened that section and captured
# everything after it. ``fixtures/filled-anchor`` case 11 wraps a sentence onto
# ``DERIVED line. Lands in the overweight band``, which hijacked the rest of the
# block -- including the ``Race/Ethnicity`` line 32 lines below -- and produced two
# F3 failures on a set that has none. The canonical block writes every label at
# column 0 and indents every continuation, which is the whole distinction this
# parser runs on; a note that indents its entire block reads as no block, and the
# exit status says so rather than scoring it.
LABEL = re.compile(
    r"^(?:>[ \t]*)*(?:[-*+][ \t]+)?\*{0,2}"
    r"(DERIVED|FILLED[·.\-](?i:ASSERTED)|FILLED[·.\-](?i:PROPOSED)|FLAG|GAPS|UNKNOWN)"
    r"\*{0,2}[ \t]*:?[ \t]*(.*)$"
)
# A line that ends a section without opening one.
CLOSER = re.compile(r"^[ \t>]*(?:```|~~~|#{1,6}[ \t]|(?:[-*_][ \t]*){3,}$)")
# An indented line, or a bullet at the margin. The bullet opens a new entry; the
# plain indented line wraps the entry above it -- see the module docstring.
BULLET = re.compile(r"^[ \t>]*[-*+][ \t]+(\S.*)$")
INDENTED = re.compile(r"^[ \t]+(\S.*)$")

# Leading markup an entry may open with, stripped before a row is anchored to it.
MARKUP = re.compile(r"^[\s>*_`\[\](){}#|-]+")

# Each row's subject, anchored: it must *open* the entry, never merely appear in
# one. ``Shift start time and shift length not supplied`` opens with ``Shift`` and
# is a real absent input, not the note's own start and end.
ROW_PATTERNS = {
    "F1": re.compile(r"(?i)^(?:primary[ \t]+)?payment[ \t]+method\b"),
    "F2": re.compile(
        r"(?i)^(?:visit[ \t]+|encounter[ \t]+|patient[ \t]+)?"
        r"(?:start[ \t]*(?:/|,|&|-|–|and|to)[ \t]*end\b"
        r"|end[ \t]*(?:/|,|&|-|–|and|to)[ \t]*start\b"
        r"|start[ \t]+and[ \t]+end\b"
        r"|(?:start|end)[ \t]+times?\b"
        r"|times?[ \t]+\(start\b)"
    ),
    "F3": re.compile(r"(?i)^race\b|^ethnicit(?:y|ies)\b|^race[ \t]*/[ \t]*ethnicity\b"),
}
# F3's second limb: a mention anywhere under FILLED-asserted satisfies it.
RACE_ANYWHERE = re.compile(r"(?i)\brace\b|\bethnicit(?:y|ies)\b")

F1, F2, F3 = "F1", "F2", "F3"

WHY = {
    F1: "payment method opens GAPS",
    F2: "start/end times open GAPS",
    F3: "Race/Ethnicity misplaced",
}

# The second limb has no entry to point at, and this string is not note text.
ABSENT = "(no Race/Ethnicity under FILLED-asserted)"


@dataclass(frozen=True)
class Entry:
    """One entry in one tier-block section, with the lines that wrap it."""

    head: str
    wraps: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        """The entry as one line -- what a reader would see unwrapped."""
        return " ".join((self.head, *self.wraps)).strip()

    @property
    def subject(self) -> str:
        """What the entry opens with, markup stripped, for an anchored match."""
        return MARKUP.sub("", self.head)


@dataclass(frozen=True)
class Finding:
    """One block-structure row failing on one entry of one note."""

    row: str
    label: str
    line: str


@dataclass(frozen=True)
class Scan:
    """Counts over a run's notes, plus what ``--show`` prints."""

    notes_read: int
    notes_with_block: int
    notes_with_gaps: int
    gaps_entries: int
    gaps_wrapped_lines: int
    f1_failures: int
    f2_failures: int
    f3_failures: int
    failing_notes: int = 0
    findings: tuple[Finding, ...] = ()
    # An aligned continuation line that would have opened a matching entry. Not a
    # failure and not in the exit status -- see the module docstring on #127.
    candidates: tuple[Finding, ...] = field(default=())


def _canonical(label: str) -> str:
    """``filled-asserted`` and ``FILLED.ASSERTED`` are both ``FILLED·asserted``."""
    upper = label.upper()
    if upper.startswith("FILLED"):
        return ASSERTED if upper.endswith("ASSERTED") else PROPOSED
    return upper


def read_block(text: str) -> dict[str, list[Entry]]:
    """The tier block of one note, label -> its entries.

    Returns an empty mapping when the note carries no block this can read, which
    the caller must distinguish from a block that carried nothing -- see the exit
    status note in the module docstring.
    """
    # Built as ``[head, [wrap, ...]]`` pairs and frozen into ``Entry`` at the end,
    # because an entry's wraps are not known until the next entry opens.
    block: dict[str, list[list]] = {}
    current: str | None = None
    for raw in text.splitlines():
        match = LABEL.match(raw)
        if match:
            current = _canonical(match.group(1))
            block.setdefault(current, []).append([match.group(2).strip(), []])
            continue
        if current is None or not raw.strip():
            continue
        if CLOSER.match(raw):
            current = None
            continue
        bullet = BULLET.match(raw)
        if bullet:
            block[current].append([bullet.group(1).strip(), []])
            continue
        indented = INDENTED.match(raw)
        if not indented:
            current = None
            continue
        if block[current]:
            block[current][-1][1].append(indented.group(1).strip())
        else:
            block[current].append([indented.group(1).strip(), []])
    return {
        label: [Entry(head, tuple(wraps)) for head, wraps in entries]
        for label, entries in block.items()
    }


def block_findings(
    block: dict[str, list[Entry]]
) -> tuple[list[Finding], list[Finding]]:
    """F1, F2 and F3 applied to one note's block.

    Returns ``(findings, candidates)``. A finding is an entry whose **subject**
    matches a row. A candidate is a wrapped line that would have matched had it
    opened an entry -- #127's ambiguity, reported and not scored.
    """
    if not block:
        return [], []
    found: list[Finding] = []
    candidates: list[Finding] = []
    for entry in block.get(GAPS, []):
        for row, pattern in ROW_PATTERNS.items():
            if pattern.search(entry.subject):
                found.append(Finding(row, GAPS, entry.head))
            for wrap in entry.wraps:
                if pattern.search(MARKUP.sub("", wrap)):
                    candidates.append(Finding(row, GAPS, wrap))
    asserted = block.get(ASSERTED, [])
    if not any(RACE_ANYWHERE.search(entry.text) for entry in asserted):
        found.append(Finding(F3, ASSERTED, ABSENT))
    return found, candidates


def survey(blocks: list[dict[str, list[Entry]]]) -> Scan:
    """Count across a run. Takes parsed blocks rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift."""
    per_note = [block_findings(block) for block in blocks]
    found = [f for note, _ in per_note for f in note]
    candidates = [c for _, note in per_note for c in note]
    return Scan(
        notes_read=len(blocks),
        notes_with_block=sum(1 for block in blocks if block),
        notes_with_gaps=sum(1 for block in blocks if block.get(GAPS)),
        gaps_entries=sum(len(block.get(GAPS, [])) for block in blocks),
        gaps_wrapped_lines=sum(
            len(entry.wraps) for block in blocks for entry in block.get(GAPS, [])
        ),
        f1_failures=sum(1 for f in found if f.row == F1),
        f2_failures=sum(1 for f in found if f.row == F2),
        f3_failures=sum(1 for f in found if f.row == F3),
        failing_notes=sum(1 for note, _ in per_note if note),
        findings=tuple(found),
        candidates=tuple(candidates),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no note text unless ``show``."""
    # Plain ASCII throughout, on ``specificity_scan.py``'s reasoning: this prints
    # to a Windows console, where a middle dot outside cp1252 comes back as a
    # question mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"block scan over {source}",
        "",
        f"  notes read                       {scan.notes_read}",
        f"  notes carrying a tier block      {scan.notes_with_block}",
        f"  notes carrying a GAPS section    {scan.notes_with_gaps}",
        f"  GAPS entries                     {scan.gaps_entries}",
        f"  GAPS wrapped lines               {scan.gaps_wrapped_lines}",
        "",
        f"  F1 - {WHY[F1]:<28}{scan.f1_failures}",
        f"  F2 - {WHY[F2]:<28}{scan.f2_failures}",
        f"  F3 - {WHY[F3]:<28}{scan.f3_failures}",
        f"  notes at fault                   {scan.failing_notes}",
        f"  wrapped-line candidates          {len(scan.candidates)}",
    ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            label = finding.label.replace("·", "-")
            lines.append(f"    {finding.row}  {label:<16} {finding.line}")
        lines += ["", "  candidates - wrapped lines, not scored:"]
        for candidate in scan.candidates:
            lines.append(f"    {candidate.row}  {'wrap':<16} {candidate.line}")
    return "\n".join(lines)


def read_notes(directory: Path) -> list[str]:
    """The text of every note in ``directory``, README excluded.

    A run's README is prose about the run; counting it would put a wrong
    denominator beside every figure below it.
    """
    return [
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and path.stem.lower() != "readme"
    ]


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    args = [a for a in argv if not a.startswith("--")]
    show = "--show" in argv
    if not args:
        print("usage: block_scan.py <a run directory> [--show]", file=sys.stderr)
        return 2
    directory = Path(args[0])
    # The directory name, never the path: a run directory sits under ``scratch/``
    # or ``output/``, and its path names the shift and often the site.
    if not directory.is_dir():
        print(f"no directory named {directory.name}", file=sys.stderr)
        return 2
    notes = read_notes(directory)
    if not notes:
        print(f"no notes found in {directory.name}", file=sys.stderr)
        return 2
    scan = survey([read_block(text) for text in notes])
    print(format_report(scan, source=directory.name, show=show))
    if not scan.notes_with_block:
        print(
            f"\nNothing was scanned: none of the {scan.notes_read} note(s) in"
            f" {directory.name} carries a tier block this can read."
            " F1-F3 have no value against this run.",
            file=sys.stderr,
        )
        return 2
    if scan.findings:
        print(
            f"\n{scan.failing_notes} note(s) fail fixtures/day-a F1-F3"
            f" ({len(scan.findings)} finding(s))."
            " Re-run with --show to see which, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
