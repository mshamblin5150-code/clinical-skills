"""Check the mechanical limb of ``clinical-note``'s drift row 22.

    python tools/differential_scan.py <a run directory> [--show]

[#68] asked what a differential entry is *called* once its organism-specific code
is refused, and the answer -- **the entry is named for the code it carries** --
closed a hole that had nothing to do with naming. One run produced three
renderings of one rule, and **all three happened to keep the refused code out of
the code slot with nothing requiring them to.** A fourth putting ``M86.9`` after
the hyphen and the refusal in a footnote would have satisfied every row this repo
had, while a reader, a grader and every later copy of that line read a disease
nobody established.

**One test, and it needs no reader.** No code marked ``NOT CODED`` anywhere in a
note may appear in any entry's code slot -- the position after the hyphen that
``SKILL.md``'s punctuation rule reserves for the code pinned to a label.

**What it cannot reach is row 22 itself.** Deciding whether ``Pain in right leg``
is what ``M79.604`` says takes a reader, and paraphrase is permitted:
``Shortness of breath - R06.02`` and ``Mild dyspnea - R06.02`` are both correct.
So a clean scan is **not** a walked row, and row 22 says so beside the command.
This is ``filled-anchor``'s R2 residue arriving on a different rule.

**It fails ``fixtures/hedged-dx`` run 1's case 2, and that is the rule being new
rather than the run being newly wrong.** That note wrote
``Contiguous osteomyelitis of the right tibia or fibula - M86.9 NOT CODED, ...;
coded as pain in right leg - M79.604``, which was compliant with everything
written down at the time and is the exact shape #68 was filed over.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record; an
entry label is a diagnosis attached to an encounter. Nothing but integers is
printed unless ``--show`` asks, and **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, on
``specificity_scan.py``'s arrangement and ``guidelines_search.py``'s before it: 0
when every slot is clean, 1 on a violation, and **2 for every way of not having
scanned** -- no argument, no directory, no notes in it, **and no differential
entry in any note read.** That last one matters most: a run whose differential was
written in some shape this parser does not read would otherwise report zero
violations and look like a pass.

Extractor limits worth knowing before quoting a number:

- **A slot is a ``<label> - <CODE>`` pair**, the form ``SKILL.md`` requires under
  *Punctuation* -- the hyphen pins a value to its label. Both branches are read:
  [SOAP.md](../skills/clinical-note/SOAP.md) puts the pair and the rationale on
  one line, [HP.md](../skills/clinical-note/HP.md) puts the pair on its own line
  with the rationale beneath. **The ``Final diagnosis`` and
  ``Actual diagnosis/diagnoses`` lines are slots too**, deliberately: row 22
  exempts them from the naming limb and not from this one.
- **A refusal is a code adjacent to the literal ``NOT CODED``** -- the last code
  before the mark on that line, and the first code after it where the mark is
  followed by a colon, which is ``icd10-cpt`` step 4's own
  ``NOT CODED: <code>  <descriptor>`` form. A run that withholds a code some other
  way reads here as having refused nothing, which is a floor on the count and on
  the exit status both. ``icd10-cpt`` requires the literal mark inline, so this is
  a limit on non-compliant output rather than on compliant output.
- **The last code before the mark, not every code on the line.** A compliant entry
  puts its own slot code and its refusals on one line, so a parser treating every
  code on a ``NOT CODED`` line as refused would flag the slot and fail the skill's
  own worked example. ``test_differential_scan.py`` pins that case.
- A code is ``[A-Z][0-9][0-9A-Z]`` with an optional dotted extension, so ``97.3``,
  ``4/10`` and ``s1,s2`` are not codes. ``B12`` is code-shaped and would be read as
  one; it fails nothing unless it sits in a slot and carries the mark.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ``M86.9``, ``R06.02``, ``A41.9``. Letter, digit, alphanumeric, optional dotted
# extension -- which is what keeps ``97.3`` and ``4/10`` out.
CODE = r"[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?"
CODE_TOKEN = re.compile(rf"\b{CODE}\b")

# ``Pain in right leg - M79.604``. The label runs back to the start of the line or
# to the nearest ``;`` or ``:``, so ``Final diagnosis: <label> - <code>`` yields
# the label and not the heading, and ``; coded as <label> - <code>`` yields the
# second pinned pair rather than swallowing the first.
SLOT = re.compile(rf"([^;:\n]{{2,120}}?)[ \t]+-[ \t]+({CODE})\b")

# ``icd10-cpt`` step 4 requires this literal, inline, on the same line as the
# number. Case-sensitive on purpose: the skill specifies the uppercase form, and
# matching ``not coded`` in prose would sweep up sentences discussing the rule.
MARK = re.compile(r"NOT CODED")
MARK_WITH_COLON = re.compile(r"NOT CODED[ \t]*:")


@dataclass(frozen=True)
class Entry:
    """One ``<label> - <CODE>`` pair, and the line it came from."""

    label: str
    code: str
    line: int


@dataclass(frozen=True)
class Note:
    """One note's slots and the set of codes it marked ``NOT CODED``."""

    entries: tuple[Entry, ...]
    refused: frozenset[str]


@dataclass(frozen=True)
class Finding:
    """One entry whose slot holds a code the same note refused."""

    code: str
    label: str
    line: int


@dataclass(frozen=True)
class Scan:
    """Counts over a run, plus the findings ``--show`` prints."""

    notes: int
    entries: int
    refused_codes: int
    findings: tuple[Finding, ...] = ()


def _refused_on_line(line: str) -> set[str]:
    """Every code the marks on one line refuse.

    The last code **before** each mark, which is the inline form
    ``M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it``, plus
    the first code **after** a mark that carries a colon, which is step 4's
    ``NOT CODED: M86.9  Osteomyelitis, unspecified``.
    """
    refused: set[str] = set()
    for mark in MARK.finditer(line):
        before = CODE_TOKEN.findall(line[: mark.start()])
        if before:
            refused.add(before[-1])
        if MARK_WITH_COLON.match(line, mark.start()):
            after = CODE_TOKEN.search(line, mark.end())
            if after:
                refused.add(after.group(0))
    return refused


def read_note(text: str) -> Note:
    """Parse one note into its slots and its refusals.

    Refusals are collected **note-wide** rather than per entry, because the H&P
    branch puts the code on one line and the refusal on the next -- so an entry
    line frequently carries no mark at all and the two cannot be paired
    positionally the way ``specificity_scan.py`` pairs a flag to its code.
    """
    entries: list[Entry] = []
    refused: set[str] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        for match in SLOT.finditer(line):
            entries.append(
                Entry(label=match.group(1).strip(), code=match.group(2), line=number)
            )
        refused |= _refused_on_line(line)
    return Note(entries=tuple(entries), refused=frozenset(refused))


def note_findings(note: Note) -> list[Finding]:
    """Row 22's slot limb, applied to one note."""
    return [
        Finding(code=entry.code, label=entry.label, line=entry.line)
        for entry in note.entries
        if entry.code in note.refused
    ]


def survey(notes: list[Note]) -> Scan:
    """Count across a run. Takes parsed notes rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift."""
    found = [finding for note in notes for finding in note_findings(note)]
    return Scan(
        notes=len(notes),
        entries=sum(len(note.entries) for note in notes),
        refused_codes=sum(len(note.refused) for note in notes),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no code and no label unless ``show``."""
    # Plain ASCII throughout, on ``specificity_scan.py``'s reasoning: this prints
    # to a Windows console, where anything outside cp1252 comes back as a question
    # mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"differential scan over {source}",
        "",
        f"  notes read                       {scan.notes}",
        f"  differential entries             {scan.entries}",
        f"  codes marked NOT CODED           {scan.refused_codes}",
        "",
        f"  row 22 - refused code in a slot  {len(scan.findings)}",
    ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    line {finding.line:<5} {finding.code:<9} {finding.label}")
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
        print("usage: differential_scan.py <a run directory> [--show]", file=sys.stderr)
        return 2
    directory = Path(args[0])
    # The directory name, never the path: a run directory sits under ``scratch/``
    # or ``output/``, and its path names the shift and often the site.
    if not directory.is_dir():
        print(f"no directory named {directory.name}", file=sys.stderr)
        return 2
    texts = read_notes(directory)
    if not texts:
        print(f"no notes found in {directory.name}", file=sys.stderr)
        return 2
    scan = survey([read_note(text) for text in texts])
    if not scan.entries:
        print(
            f"no differential entry found in {scan.notes} note(s) in {directory.name}."
            " Nothing was scanned -- this is not a clean run.",
            file=sys.stderr,
        )
        return 2
    print(format_report(scan, source=directory.name, show=show))
    if scan.findings:
        print(
            f"\n{len(scan.findings)} entry/entries hold a code the note refused,"
            " failing clinical-note drift row 22."
            " Re-run with --show to see which, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
