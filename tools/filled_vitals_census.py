"""Measure which values a run of ``clinical-note`` chose for its filled vitals.

    python tools/filled_vitals_census.py <directory of finished notes> [--show]

``fixtures/day-b`` B1 forces a filled vital to exist and B3 forces an abnormal one
to be worked up. Neither asks **which value was chosen**, which is the license's
actual instruction -- *the value this patient most plausibly had* -- and issue #67
is what happens in the gap: filled heights collapsing onto one value per sex, two
patients thirty-two years apart handed the same body, filled pressures landing on
one side of a line the corpus splits about evenly. **None of that is visible in a
single note**, each of which fills a perfectly ordinary patient. This script is
what makes the pattern countable. The figures for the two runs measured so far
live in ``fixtures/day-b/assertions.md`` and are deliberately not restated here.

It reads finished notes -- the note body and its tier block -- and counts only what
the tier block **declares filled**. A value the block merely mentions is not one
this skill generated, which is what keeps the given-vitals controls out of the
numbers. The discriminator is ``clinical-note``'s own mandated form, *not "blood
pressure filled" -- "BP 142/88 filled"*, so a run that stops writing the value into
the block reads here as having filled nothing rather than as having passed.

**It prints counts only by default and never a measured value**, so its output is
safe to paste into a ticket. A run directory lives under ``scratch/`` or
``output/`` and is a patient record; a height is not an identifier and a weight in
a small county is closer to one than this script can judge, so neither is printed
unless ``--show`` asks. ``--show`` output is PHI on the same terms as
``harvest_review.py``: read it, do not paste it.

**Exit status is the answer to B13.** Zero when no two notes in the directory share
an identical filled height-and-weight pair, non-zero when any two do, so a grading
pass cannot report a pass by printing something reassuring. Every other figure it
prints is counted rather than enforced -- the corpus splits about evenly at 130/80
and nothing licenses turning that into a bar over nine samples.

Extractor limits worth knowing before quoting a number:

- A tier block opens on a key at **column 0**. The phrase "listed in
  FILLED·asserted" appears in note prose -- ``case-03`` writes it -- and a matcher
  that opened a block there would read a whole note body as declared content,
  which is exactly how a given value becomes a filled one.
- A declaration is a **labeled** value with ``filled`` after it and no sentence
  end in between. So ``HEIGHT 5'10" (70 in) filled`` counts, the threshold
  disclosure's adjacent ``5'5" gives 29.1`` does not, and neither does a given
  value the block names to explain a BMI. A declaration that wraps across a line
  break still counts; one interrupted by a period or a semicolon does not, and
  reads here as absent.
- **That window is 80 characters and it cuts both ways**, which is the cost of
  the line above rather than a separate limit. A clause naming a *given* value
  and reaching ``filled`` about a **different** value within one sentence would
  read the given one as declared -- ``BMI from the given Ht 6'2" and Wt 200 lb
  filled`` is the shape. A ``given`` anywhere in the span is therefore rejected,
  which is a guard against one wording and not against every one. **Read the
  block yourself before quoting a figure off a run that writes it unusually.**
- A height is caught in the ``5'10"`` form and in bare ``70 in``. A run writing
  it any other way reads as having declared no height, which is a floor on the
  height figures -- and **not** a floor on ``repeated_bodies``, which needs both
  values and so misses such a pair entirely rather than reporting it. A set whose
  ``notes read`` far exceeds its ``declaring a filled height`` is the shape to
  look at; the exit status will not tell you.
- Not-normal is ``not corpus_census.is_normal_bp`` -- systolic 130 or above **or**
  diastolic 80 or above, which is `day-b` B2's own wording. The predicate is
  imported rather than restated, because two definitions of the line are how a
  skill file and a grader come to disagree about the same reading.
- Every count is over notes, not over patients. Two encounters for one patient in
  a directory are two notes here, and a shared body between them is a repeat this
  script cannot excuse. Read a non-zero exit before acting on it.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from corpus_census import Reading, is_normal_bp

# A tier key at column 0 opens the block; the next key at column 0 closes it.
# The separator between FILLED and asserted is the middle dot in every note this
# repo has produced, and the alternatives cost nothing to accept.
BLOCK_START = re.compile(r"(?m)^FILLED[·.\- ]?asserted\b")
BLOCK_END = re.compile(r"(?m)^(?:DERIVED|FILLED|FLAG|GAPS|UNKNOWN|PROPOSED)\b")

# A declaration is a label, a value, and ``filled`` -- with no sentence end
# between the value and the word. ``{0,80}`` is what lets a declaration wrap
# across a line break while stopping the match running into the next item.
_TO_FILLED = r"[^.;]{0,80}?\bfilled\b"
HEIGHT_DECL = re.compile(
    r"(?i)\b(?:ht|height)\b[\s.:]*(\d)\s*'\s*(\d{1,2})\s*\"?" + _TO_FILLED
)
# The bare-inches form, tried only where the feet form found nothing. Without it
# a run writing ``HEIGHT 70 in filled`` declares no height, shares no body with
# anyone, and exits zero -- a row evaded by formatting, which is #70's defect.
HEIGHT_IN_DECL = re.compile(
    r"(?i)\b(?:ht|height)\b[\s.:]*(\d{2,3})\s*(?:in\b|inches\b|\")" + _TO_FILLED
)
WEIGHT_DECL = re.compile(
    r"(?i)\b(?:wt|weight)\b[\s.:]*(\d{2,3})\s*(?:lbs?|pounds)\b" + _TO_FILLED
)
BP_DECL = re.compile(
    r"(?i)\b(?:bp|blood pressure)\b[\s.:]*(\d{2,3})\s*/\s*(\d{2,3})\b" + _TO_FILLED
)
# ``the given Ht 6'2"`` -- a given value the block names to explain a derived one,
# in a sentence that goes on to reach the word ``filled`` about something else.
# The guard is deliberately narrow: it looks at the words immediately before the
# label and nowhere else, because a *correct* filled line now names the givens it
# was reasoned from -- ``BP 138/86 filled, from the given pulse of 112`` -- and a
# guard scanning the whole clause would reject exactly the lines the rule wants.
PRECEDING_GIVEN = re.compile(r"(?i)\bgiven\s*$")
_LOOKBACK = 12


def _declaration(pattern: re.Pattern[str], block: str) -> re.Match[str] | None:
    """The first match whose label is not introduced as a given value."""
    for match in pattern.finditer(block):
        before = block[max(0, match.start() - _LOOKBACK) : match.start()]
        if not PRECEDING_GIVEN.search(before):
            return match
    return None


@dataclass(frozen=True)
class Fill:
    """One note's declared-filled body values."""

    height_in: int | None = None
    weight_lb: int | None = None
    pressure: Reading | None = None

    @property
    def body(self) -> tuple[int, int] | None:
        """The height-and-weight pair, where the note declared both filled."""
        if self.height_in is None or self.weight_lb is None:
            return None
        return (self.height_in, self.weight_lb)


@dataclass(frozen=True)
class Census:
    """Counts over a set of notes. Holds no note text and no filename."""

    notes: int
    heights: int
    distinct_heights: int
    largest_height_group: int
    weights: int
    distinct_weights: int
    pressures: int
    distinct_pressures: int
    largest_pressure_group: int
    abnormal_pressures: int
    bodies: int
    repeated_bodies: int
    # Kept for ``--show`` alone, and never read by ``format_report`` without it.
    height_counts: tuple[tuple[int, int], ...] = ()
    body_counts: tuple[tuple[tuple[int, int], int], ...] = ()


def filled_block(text: str) -> str:
    """The ``FILLED·asserted`` region of a tier block, or ``""``."""
    start = BLOCK_START.search(text)
    if start is None:
        return ""
    rest = text[start.end() :]
    end = BLOCK_END.search(rest)
    return rest[: end.start()] if end else rest


def read_fill(text: str) -> Fill:
    """What a note's tier block declares it filled.

    A note with no block declares nothing. There is deliberately no fallback to
    scanning the body: the body is written so given and filled content read
    identically, which is the whole reason the block exists.
    """
    block = filled_block(text)
    height = _declaration(HEIGHT_DECL, block)
    inches = None if height else _declaration(HEIGHT_IN_DECL, block)
    weight = _declaration(WEIGHT_DECL, block)
    pressure = _declaration(BP_DECL, block)
    if height:
        height_in = int(height.group(1)) * 12 + int(height.group(2))
    elif inches:
        height_in = int(inches.group(1))
    else:
        height_in = None
    return Fill(
        height_in=height_in,
        weight_lb=int(weight.group(1)) if weight else None,
        pressure=(int(pressure.group(1)), int(pressure.group(2))) if pressure else None,
    )


def survey(texts: list[str]) -> Census:
    """Count the filled bodies across a set of note texts.

    Takes texts rather than files: a ``Census`` never learns a filename, so it
    cannot put a patient record's path into output this script promises is safe
    to paste.
    """
    fills = [read_fill(text) for text in texts]
    heights = Counter(f.height_in for f in fills if f.height_in is not None)
    weights = Counter(f.weight_lb for f in fills if f.weight_lb is not None)
    bodies = Counter(f.body for f in fills if f.body is not None)
    pressures = Counter(f.pressure for f in fills if f.pressure is not None)
    return Census(
        notes=len(texts),
        heights=sum(heights.values()),
        distinct_heights=len(heights),
        largest_height_group=max(heights.values(), default=0),
        weights=sum(weights.values()),
        distinct_weights=len(weights),
        pressures=sum(pressures.values()),
        distinct_pressures=len(pressures),
        largest_pressure_group=max(pressures.values(), default=0),
        abnormal_pressures=sum(n for p, n in pressures.items() if not is_normal_bp(p)),
        bodies=sum(bodies.values()),
        repeated_bodies=sum(n - 1 for n in bodies.values() if n > 1),
        height_counts=tuple(sorted(heights.items())),
        body_counts=tuple(sorted(bodies.items())),
    )


def _inches(value: int) -> str:
    return f"{value // 12}'{value % 12}\""


def format_report(census: Census, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no measured value unless ``show``."""
    lines = [
        f"filled-vitals census over {source}",
        "",
        f"  notes read                      {census.notes}",
        f"  declaring a filled height       {census.heights}",
        f"    distinct values               {census.distinct_heights}",
        f"    largest group at one value    {census.largest_height_group}",
        f"  declaring a filled weight       {census.weights}",
        f"    distinct values               {census.distinct_weights}",
        f"  declaring a filled pressure     {census.pressures}",
        f"    distinct values               {census.distinct_pressures}",
        f"    largest group at one value    {census.largest_pressure_group}",
        f"    not normal (130+ or 80+)      {census.abnormal_pressures}",
        f"  declaring a filled height and weight   {census.bodies}",
        f"    sharing a body with another note     {census.repeated_bodies}",
    ]
    if show:
        lines += ["", "  heights, most repeated first:"]
        for value, count in sorted(census.height_counts, key=lambda p: -p[1]):
            lines.append(f"    {_inches(value):>8}  x{count}")
        repeated = [(b, n) for b, n in census.body_counts if n > 1]
        if repeated:
            lines += ["", "  bodies shared by more than one note:"]
            for (height, weight), count in repeated:
                lines.append(f"    {_inches(height):>8} / {weight} lb  x{count}")
    return "\n".join(lines)


def read_notes(directory: Path) -> list[str]:
    """The text of every note in ``directory``, README excluded.

    A set's README is prose about the set, and counting it as a note read would
    put a wrong denominator beside every figure below it.
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
        print("usage: filled_vitals_census.py <directory> [--show]", file=sys.stderr)
        return 1
    directory = Path(args[0])
    # The directory name, never the path: a run directory sits under ``scratch/``
    # or ``output/``, and its path names the shift and often the site.
    if not directory.is_dir():
        print(f"no directory named {directory.name}", file=sys.stderr)
        return 1
    notes = read_notes(directory)
    if not notes:
        print(f"no notes found in {directory.name}", file=sys.stderr)
        return 1
    census = survey(notes)
    print(format_report(census, source=directory.name, show=show))
    if census.repeated_bodies:
        print(
            f"\n{census.repeated_bodies} note(s) share a filled body with another."
            " fixtures/day-b B13 fails. Re-run with --show to see which values,"
            " and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
