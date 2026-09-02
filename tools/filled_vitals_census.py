"""Measure which values a run of ``clinical-note`` chose for its filled vitals.

    python tools/filled_vitals_census.py <directory of finished notes> [--show] [--submission <key>]

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

**Exit status answers three rows now, and the last two are issue #97's ruling.**
0 clean, 1 for a violation, **2 for every way of not having scanned** -- no
directory, no notes in it, **a ``FILLED·asserted`` key outside the block that
was read**, or no note declaring a filled height or a filled pressure. **That
last limb has a real instance rather than a hypothetical one**:
a full separated run over ``day-a`` declared nothing filled at all, because every
one of that set's inputs gives a pressure. The figures are in issue #97's own
comments and are **deliberately not restated here**, having been measured against
a directory under ``scratch/`` that nothing committed can re-derive --
``differential_scan.py``'s rule, and #143's shape. **Where a violation and an
ungraded set both hold, 1 wins**, on that tool's ordering and for its reason. The
three graded rows:

- **B13** -- no two notes share an identical filled height-and-weight pair.
- **The tilt bar** -- filled pressures may not land not-normal so much more often
  than a fair split that chance would produce it less than ``CHANCE_FLOOR`` of the
  time. See ``tilt_beyond_chance`` for why that number is not an invented one.
- **The person rule** -- every filled height's own clause names an age and a sex.

Everything else is counted rather than enforced, which is ``fixtures/day-b`` R5.
**That now includes the five vital classes this tool could not previously see at
all** -- temperature, heart rate, respiratory rate, oxygen saturation and pain
score. Issue #69 was ruled entirely on a filled temperature and two filled
saturations while this module read none of them, and a bar written over three of
five classes with nothing recording which three is what that ticket objected to.
They are counted and not graded because the corpus supplies no even split for a
temperature or a saturation to ground a cutoff on, the way it does at 130/80 for
a pressure.

**The fifth was nearly left out, and the near-miss is the reusable part.** The
first pass here added four and wrote this paragraph enumerating them as though
the gap were closed; review caught it against #69's own list. The pain score is
the one with no label of its own -- it is written ``7/10 itching filled`` -- and
the only one already carrying a clinician's ruling, #59's carve-out barring a
filled ``0/10`` from drift row 19's *no anchor* exit. **Counting it is not that
rule**, which is about a disclosure's wording and stays with a reader.
``COUNTED_CLASSES`` is one tuple for exactly this reason: a sixth class is one
entry, not six edits.

**Run it against ``fixtures/filled-anchor/notes`` and it exits 1**, which is
correct and worth knowing before reading it as breakage. **5 of its 9 heights
name no age and sex; the other 4 already write the compliant form**, two of them
with a percentile. Its pressures clear the tilt bar, so the exit status is the
heights and nothing else. Measured 2026-08-17 and pinned by a test.

**The obvious explanation for that is wrong and was published wrong first.**
Those twelve notes are day-b **run 1** byte for byte apart from two redacted
site names, written before drift row 19 existed, so the prediction was that
every height fails. Four do not. The prediction was made from two notes during
this ticket's grilling and corrected by
running the scanner over all twelve -- issue #137's subject, and the reason the
compliant form is worth naming: **the rule asks for something this skill has
already produced unprompted**, which is a much better argument for it than the
one it was ruled on. **The counts over the set are untouched** and stay #67's
evidence.

Extractor limits worth knowing before quoting a number:

- A tier block opens on a key that **heads a line** -- at column 0, and followed
  by the end of the line or by an aligned column of two or more spaces. The
  phrase "listed in FILLED·asserted" appears in note prose -- ``case-03`` writes
  it -- and a matcher that opened a block there would read a whole note body as
  declared content, which is exactly how a given value becomes a filled one.
  **Column 0 alone was not enough and this was not hypothetical**: note prose is
  hard-wrapped, ``case-04`` lands ``FILLED·asserted.`` at column 0 far above its
  tier block, and the parser took it -- so that note's
  real block was never read at all. ``case-06`` writes ``FILLED·asserted item
  11.`` below its own, harmlessly. Issue #204.
- **Three block forms are live and this reads all three**: one key with its items
  aligned under it, one key alone on a line with its items beneath (``case-07``
  and ``case-08``), and **one key per item**, which is how
  ``skills/clinical-note/SKILL.md``'s own worked examples write a multi-item
  block. The third used to end the block at its own **second** declaration, so
  the first swallowed nothing and every one after it read as a block that ended
  where it began -- and a shrunken denominator makes a graded row *less* likely
  to fail rather than more. **How many declarations one run lost is #204's to
  state and is deliberately not restated here**: it was measured against a
  directory under ``scratch/``, nothing committed re-derives it, and this module
  carried two different numbers for it before review caught them. Issue #204.
- **A key the read block does not contain is reported and refused**, which is
  what stops a fourth form doing quietly what the third one did. See
  ``key_coverage`` for what that count reaches and what it does not: a key line
  this rule does not recognize as a key is invisible to the parse and to the
  count alike, so the coverage figure is a floor rather than a proof.
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
- **The person rule reads a height's own clause, never the whole block**, and the
  clause runs from the height's label to the next declared value or the end of the
  block. A block-wide test would pass a height on an age read for a *different*
  value -- ``clinical-note``'s own canonical example names ``age 68`` on the
  pressure line and nothing on the height line -- which is the 17-year-old
  surviving his own fix. The cost of the narrow scope is that a run declaring its
  height last has the rest of the block in scope.
- **A sex has to be spelled.** A bare ``M`` or ``F`` is not accepted, because
  ``T 98.4 F filled`` sits in these blocks and a Fahrenheit mark would otherwise
  satisfy the rule for a neighboring height.
- The counted classes are matched on the same labeled-value-then-``filled`` form
  as the three graded ones, and are subject to every limit in this list. Nothing
  about them reaches the exit status. **The pain score has no label**, so it is
  matched on the ``N/10`` shape alone and is the loosest pattern here.
- **A usage error exits 2 as well, and that changed** -- no argument, no such
  directory and no notes in it all returned 1 before #97, which is the status a
  B13 violation returns. Nothing asked for that; it is the sibling scanners'
  arrangement and the reason is theirs, that a run reporting *nothing found*
  and a run reporting *nothing read* must not share a status. Declared here
  because a caller checking ``== 1`` for a violation would otherwise change
  meaning silently.
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
from math import comb
from pathlib import Path

from console_codec import use_utf8
from corpus_census import Reading, is_normal_bp
import aar_scan

EXPECTED_COMPLETION_CHECKS = (aar_scan.EXPECTED_ROW,)

# A tier key at column 0 opens the block; the next key at column 0 closes it.
# The separator between FILLED and asserted is the middle dot in every note this
# repo has produced, and the alternatives cost nothing to accept.
#
# **Column 0 is not sufficient**, and a tier key therefore **heads** a line --
# end of line, or an aligned column of two or more spaces before its content.
# A sentence does neither. Which committed notes forced that and what it cost
# are in the module docstring's limits list rather than restated here.
_HEADS_A_LINE = r"(?=[ \t]*$|[ \t]{2,}\S)"
BLOCK_START = re.compile(r"(?m)^FILLED[·.\- ]?asserted" + _HEADS_A_LINE)
# ``FILLED·asserted`` is deliberately **not** an end: one key per item is a live
# form of this block, and ending there read the first declaration and none of
# the rest while reporting a number that looked complete. Issue #204, and the
# limits list above is where the three live forms are named.
#
# **``_HEADS_A_LINE`` is deliberately not applied here, and the asymmetry is the
# point rather than an oversight.** The two boundaries fail in opposite
# directions. A start that matches too readily opens a block on prose and reads
# a note body as declared content; an end that matches too *reluctantly* fails
# to close the block and reads the tiers below it as declared content. So the
# start is strict and the end is permissive, and each is loose in its own safe
# direction. A single-space ``FLAG BP 151/93 undiscussed`` closes the block --
# without that, a given pressure the note flagged reads as filled.
BLOCK_END = re.compile(
    r"(?m)^(?:DERIVED|FLAG|GAPS|UNKNOWN|PROPOSED|FILLED(?![·.\- ]?asserted\b))\b"
)

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

# Counted, never graded -- see the module docstring. These are the four classes
# issue #69 was ruled on while this module could not see any of them.
TEMP_DECL = re.compile(
    r"(?i)\b(?:t|temp|temperature)\b[\s.:]*(\d{2,3}(?:\.\d)?)\s*°?\s*[FC]\b" + _TO_FILLED
)
HR_DECL = re.compile(r"(?i)\b(?:hr|heart rate|pulse)\b[\s.:]*(\d{2,3})\b" + _TO_FILLED)
RR_DECL = re.compile(
    r"(?i)\b(?:rr|resp(?:iratory)? rate)\b[\s.:]*(\d{1,2})\b" + _TO_FILLED
)
SPO2_DECL = re.compile(
    r"(?i)\b(?:spo2|sao2|o2 sat(?:uration)?|oxygen saturation)\b[\s.:]*(\d{2,3})\s*%?"
    + _TO_FILLED
)
# A severity, which is the fifth of the five classes #69's comment on #97 named
# and the one most easily left out: it has no label of its own, being written as
# ``7/10 itching filled``. It is also the only counted class already carrying a
# clinician's ruling -- a filled ``0/10`` may not take drift row 19's *no anchor*
# exit, issue #59 -- so leaving it uncounted would have been the worst of the
# five to leave uncounted. **Counting is not that rule**, which is about a
# disclosure's wording and stays with a reader.
PAIN_DECL = re.compile(r"(\d{1,2})\s*/\s*10\b" + _TO_FILLED)

# One entry per counted class, and **adding a class is one entry and nothing
# else** -- the report, the census and the extractor all read this tuple. It was
# four parallel fields and a fifth had to be added the day after; that is the
# shotgun-surgery smell arriving on schedule, and this is the fix.
COUNTED_CLASSES: tuple[tuple[str, str, "re.Pattern[str]"], ...] = (
    ("temperature", "temperature", TEMP_DECL),
    ("heart rate", "heart_rate", HR_DECL),
    ("respiratory rate", "resp_rate", RR_DECL),
    ("saturation", "saturation", SPO2_DECL),
    ("pain score", "pain_score", PAIN_DECL),
)

# The two halves of #97's person rule. An age is spelled in any of the corpus's
# forms; a sex is **spelled**, never a bare ``M`` or ``F`` -- ``T 98.4 F filled``
# is in these blocks and would otherwise satisfy a neighboring height.
NAMES_AGE = re.compile(
    r"(?i)\b(?:age[ds]?\s*\d{1,3}"
    r"|\d{1,3}\s*[-‐‑‒– ]?\s*(?:year|yr|y/o|yo)s?\b"
    r"|\d{1,2}\s*[-‐‑‒– ]?\s*(?:month|week|day)s?[-– ]?old)"
)
NAMES_SEX = re.compile(
    r"(?i)\b(?:male|female|man|men|woman|women|boy|girl|gentleman|lady|"
    r"transgender|nonbinary)\b"
)

# How often a bar is willing to fail an honestly reasoned run for nothing. Ruled
# by the clinician on 2026-08-17 at 2%, which puts the cut at 8 of 9 -- see
# ``tilt_beyond_chance``. It is the false-alarm rate that was chosen and not the
# count, so the bar follows a set of any size without being re-decided.
CHANCE_FLOOR = 0.02


# The report and the refusal both name this, so it is one string rather than
# two: a reword of either alone would leave the run's own two sentences about
# coverage disagreeing about what was counted.
KEY_NOUN = "FILLED·asserted key(s)"


def _declaration(pattern: re.Pattern[str], block: str) -> re.Match[str] | None:
    """The first match whose label is not introduced as a given value."""
    for match in pattern.finditer(block):
        before = block[max(0, match.start() - _LOOKBACK) : match.start()]
        if not PRECEDING_GIVEN.search(before):
            return match
    return None


def _clause(block: str, declaration: re.Match[str], others: list[re.Match[str]]) -> str:
    """One declaration's own span: from its label to wherever the next one starts.

    The boundary is a **declaration** and not a sentence, because a disclosure is
    several sentences and a value is one label -- ``clinical-note``'s canonical
    block runs three sentences of reasoning under one pressure. Reading to the
    next label is what stops a height borrowing the age named for the pressure
    above it, which is the whole point of scoping this at all.
    """
    starts = [m.start() for m in others if m.start() > declaration.start()]
    return block[declaration.start() : min(starts, default=len(block))]


def tilt_beyond_chance(not_normal: int, total: int, floor: float = CHANCE_FLOOR) -> bool:
    """Is this many not-normal filled pressures more than a fair split explains?

    Issue #97's objection to its own option 1 was that *a row saying no more than
    N needs an N that nothing grounds*. **It is groundable.** ``clinical-note``
    measures 249 transcribed pressures splitting about evenly at 130/80, so a set
    of honestly reasoned filled pressures should land like that many coin flips.
    What is left to choose is not a count but **how often an honest run may be
    failed for nothing**, which is a judgment a clinician can make and did:

    ======================  ==============================
    fail a set of 9 at      an honest run wrongly fails
    ======================  ==============================
    5 or more               50%
    6 or more               25%
    7 or more               9%
    **8 or more**           **2%**  <- ruled 2026-08-17
    ======================  ==============================

    **The run that filed the ticket passes, and that was ruled knowingly.**
    ``fixtures/filled-anchor``'s six of nine is a coin-flip outcome one time in
    four; a bar failing it would fire on an honest set a quarter of the time,
    which is the rate at which a warning stops being read. Its defect is graded
    by the person rule on its heights instead.

    **One-sided on purpose.** Filled pressures clustering *normal* is the bland
    normal, a different defect that ``clinical-note`` guards upstream, and a
    two-sided test here would fail a run for the opposite of what #97 is about.

    **The 50% null is generous to the machine.** Encounters whose shorthand omits
    vitals are plausibly the simpler ones, so an honest run arguably ought to land
    below half rather than at it. Nothing measures that, so the assumption that
    favors the run is the one used.

    A set too small to distinguish is not failed: five of five is 1 in 32 and
    passes, six of six is 1 in 64 and does not. **Six is the smallest set this can
    fail**, and only by failing every pressure in it.
    """
    if total <= 0 or not_normal <= total / 2:
        return False
    tail = sum(comb(total, k) for k in range(not_normal, total + 1)) / 2**total
    return tail < floor


def names_person(scope: str) -> bool:
    """Does this clause name both an age and a sex?

    Issue #97's second ruling. Age and sex are given on **36 of the 37 committed
    inputs**, so a filled height is almost never truly unanchored however little
    the encounter says about the body.

    **The ruling was made on the stronger claim and the stronger claim is false.**
    ``fixtures/day-a/shorthand/case-10.md`` carries no age line -- the only one of
    the 37, and issue #158's own case. On such an input this rule can be satisfied
    only by naming an *inferred* age, so the height comes to lean on the same guess
    #158 is about. That is a real cost of the rule and it is recorded rather than
    smoothed over; it does not change the rule, which the clinician ruled.

    **Repetition itself is not graded**, and that is the ruling rather than a gap:
    ``clinical-note`` says outright that where the encounter supplies no habitus
    datum *the repetition across a set is that honesty's consequence*, so a bar on
    repeated values would leave a compliant run no way out but inventing a
    distinguishing one -- which standing rule 2 forbids in the same words.

    **A sex must be spelled.** A bare ``M`` or ``F`` is refused because
    ``T 98.4 F filled`` is in these blocks and its Fahrenheit mark would otherwise
    satisfy the rule for whatever height sits beside it.
    """
    return bool(NAMES_AGE.search(scope)) and bool(NAMES_SEX.search(scope))


@dataclass(frozen=True)
class Fill:
    """One note's declared-filled body values."""

    height_in: int | None = None
    weight_lb: int | None = None
    pressure: Reading | None = None
    # Which of ``COUNTED_CLASSES`` this note declared, by key. Presence only --
    # nothing here is graded, so the value is never needed and storing one would
    # be a measured value kept for no reason.
    counted: frozenset[str] = frozenset()
    # ``None`` where the note declared no filled height, so a control with
    # nothing to fail is never counted as having failed.
    height_names_person: bool | None = None

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
    # #204's coverage. ``FILLED·asserted`` keys across the set, and how many of
    # them sat inside a block that was read. Every figure above is a floor where
    # these disagree, because each graded row is a fraction whose denominator is
    # whatever the parser found. **Required rather than defaulted**: a coverage
    # field defaulting to 0 and 0 reports *nothing missed*, which is the silent
    # pass this whole row exists to refuse, and the neighbors below default to
    # *nothing found* instead.
    asserted_keys: int
    asserted_keys_read: int
    # #97's person rule. Over notes declaring a filled height, never over notes.
    heights_missing_person: int = 0
    # Counted, never graded -- #69's five classes, keyed as ``COUNTED_CLASSES``.
    counted: tuple[tuple[str, int], ...] = ()
    # Kept for ``--show`` alone, and never read by ``format_report`` without it.
    height_counts: tuple[tuple[int, int], ...] = ()
    body_counts: tuple[tuple[tuple[int, int], int], ...] = ()

    def count_of(self, key: str) -> int:
        """How many notes declared one counted class, by its ``COUNTED_CLASSES`` key."""
        return dict(self.counted).get(key, 0)

    @property
    def counted_total(self) -> int:
        """Every declaration in the counted classes, across the set."""
        return sum(n for _, n in self.counted)

    @property
    def asserted_keys_unread(self) -> int:
        """``FILLED·asserted`` keys no block this read contains."""
        return self.asserted_keys - self.asserted_keys_read

    @property
    def tilted(self) -> bool:
        """#97's pressure bar over this set."""
        return tilt_beyond_chance(self.abnormal_pressures, self.pressures)

    @property
    def gradeable(self) -> bool:
        """Was there anything here for either graded row to read?

        A set declaring no filled height and no filled pressure has not passed
        them; it has not been measured by them, and the exit status says which.
        """
        return bool(self.heights or self.pressures)


def _block_span(text: str) -> tuple[int, int] | None:
    """Where the ``FILLED·asserted`` region starts and stops, or ``None``.

    Offsets into ``text``, so ``filled_block`` and ``key_coverage`` read the same
    boundary rather than each deriving one. Two answers to *what was scanned*
    would be worse than none: the count and the coverage line beside it would
    disagree, and the coverage line is the one nobody would check.
    """
    start = BLOCK_START.search(text)
    if start is None:
        return None
    end = BLOCK_END.search(text, start.end())
    return (start.end(), end.start() if end else len(text))


def filled_block(text: str) -> str:
    """The ``FILLED·asserted`` region of a tier block, or ``""``.

    A repeated key is replaced by a sentence end rather than kept, because that
    is what it means: each key opens its own item. Without one the declaration
    window -- which crosses a line break on purpose, so an aligned entry may wrap
    -- runs from the tail of one item into the ``filled`` on the line below, and
    reads a **given** value as declared by a word belonging to something else.
    """
    span = _block_span(text)
    if span is None:
        return ""
    return BLOCK_START.sub(". ", text[span[0] : span[1]])


def key_coverage(text: str) -> tuple[int, int]:
    """``FILLED·asserted`` keys in this note, and how many the read block holds.

    Issue #204's ruling. Reading a second block form leaves the tool silently
    tolerant of a third nobody has written, so the signal is derived from the
    **member list** -- the keys the note carries -- rather than from whether a
    block was found at all. That second arithmetic is what let *one declaration
    of N* report exactly what a note declaring one reports. #177's fix, one tool
    over, is the same move.

    **What it cannot reach is a key line the rule does not recognize as a key**,
    which is invisible to the parse and to this count alike. The coverage figure
    is therefore a floor on what was read, not a proof that a block was found.
    """
    keys = [m.start() for m in BLOCK_START.finditer(text)]
    span = _block_span(text)
    if span is None:
        return (len(keys), 0)
    return (len(keys), sum(1 for start in keys if start < span[1]))


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
    counted = {key: _declaration(pattern, block) for _, key, pattern in COUNTED_CLASSES}
    anchor = height or inches
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
        counted=frozenset(key for key, match in counted.items() if match),
        height_names_person=(
            None
            if anchor is None
            else names_person(
                _clause(
                    block,
                    anchor,
                    [m for m in [weight, pressure, *counted.values()] if m is not None],
                )
            )
        ),
    )


def survey(texts: list[str]) -> Census:
    """Count the filled bodies across a set of note texts.

    Takes texts rather than files: a ``Census`` never learns a filename, so it
    cannot put a patient record's path into output this script promises is safe
    to paste.
    """
    fills = [read_fill(text) for text in texts]
    coverage = [key_coverage(text) for text in texts]
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
        asserted_keys=sum(present for present, _ in coverage),
        asserted_keys_read=sum(read for _, read in coverage),
        heights_missing_person=sum(1 for f in fills if f.height_names_person is False),
        counted=tuple(
            (key, sum(1 for f in fills if key in f.counted))
            for _, key, _ in COUNTED_CLASSES
        ),
        height_counts=tuple(sorted(heights.items())),
        body_counts=tuple(sorted(bodies.items())),
    )


def _inches(value: int) -> str:
    return f"{value // 12}'{value % 12}\""


def _tilt_verdict(census: Census) -> str:
    """The tilt line, which never reads as a pass where nothing was measured."""
    if not census.pressures:
        return "not graded — no filled pressure declared"
    return "YES" if census.tilted else "no"


def format_report(census: Census, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no measured value unless ``show``."""
    lines = [
        f"filled-vitals census over {source}",
        "",
        # First, and on every run rather than only a degraded one -- #258's
        # ruling and #177's ordering. A count printed ahead of the caveat is
        # read as the verdict, and a caveat printed only when it fires teaches
        # a reader that its absence is a stronger claim than it is.
        f"  {'scanned':<32}{census.asserted_keys_read} of"
        f" {census.asserted_keys} {KEY_NOUN}",
        f"  notes read                      {census.notes}",
        f"  declaring a filled height       {census.heights}",
        f"    distinct values               {census.distinct_heights}",
        f"    largest group at one value    {census.largest_height_group}",
        f"    naming no age and sex         {census.heights_missing_person}",
        f"  declaring a filled weight       {census.weights}",
        f"    distinct values               {census.distinct_weights}",
        f"  declaring a filled pressure     {census.pressures}",
        f"    distinct values               {census.distinct_pressures}",
        f"    largest group at one value    {census.largest_pressure_group}",
        f"    not normal (130+ or 80+)      {census.abnormal_pressures}",
        f"    {f'beyond a fair split at {CHANCE_FLOOR:.0%}?':<30}{_tilt_verdict(census)}",
        f"  declaring a filled height and weight   {census.bodies}",
        f"    sharing a body with another note     {census.repeated_bodies}",
        "",
        "  counted, not graded — no corpus split grounds a bar on these:",
    ]
    lines += [
        f"    {f'declaring a filled {label}':<37}{census.count_of(key)}"
        for label, key, _ in COUNTED_CLASSES
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
    args: list[str] = []
    submission: str | None = None
    index = 0
    while index < len(argv):
        if argv[index] == "--submission":
            if index + 1 >= len(argv):
                print("--submission needs a key", file=sys.stderr)
                return 2
            submission = argv[index + 1]
            index += 2
            continue
        if not argv[index].startswith("--"):
            args.append(argv[index])
        index += 1
    show = "--show" in argv
    if not args:
        print("usage: filled_vitals_census.py <directory> [--show]", file=sys.stderr)
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
    census = survey(notes)
    print(format_report(census, source=directory.name, show=show))
    aar_failed, aar_report = aar_scan.completion_gate(directory, submission)
    print(aar_report)

    findings = []
    if census.repeated_bodies:
        findings.append(
            f"{census.repeated_bodies} note(s) share a filled body with another."
            " fixtures/day-b B13 fails."
        )
    if census.tilted:
        findings.append(
            f"{census.abnormal_pressures} of {census.pressures} filled pressures land"
            " not normal, which a fair split produces less than"
            f" {CHANCE_FLOOR:.0%} of the time. The anchors were in the notes."
            " fixtures/day-b B17 fails."
        )
    if census.heights_missing_person:
        findings.append(
            f"{census.heights_missing_person} filled height(s) name no age and sex."
            " Both are given on all but one committed input, so a height almost"
            " always has two anchors already in the encounter."
            " fixtures/day-b B18 fails."
        )
    # #204. Every figure above is a fraction whose denominator is whatever the
    # parser found, so a key it did not read shrinks a graded row rather than
    # failing it -- which makes a violation less likely, not more.
    unread = (
        f"{census.asserted_keys_unread} of {census.asserted_keys} {KEY_NOUN} sit"
        " outside the block that was read, so every count here is a floor.\n"
        if census.asserted_keys_unread
        else ""
    )
    if findings or aar_failed:
        # 1 outranks 2 deliberately: returning 2 where something was graded and
        # failed would file the strongest thing known about the run under the
        # heading that means nothing was measured.
        #
        # The floor note goes **first**, ahead of the findings, on #177's
        # ordering: a count printed ahead of its caveat is read as the verdict,
        # and every finding below is a count.
        print(
            "\n" + unread + "\n".join(findings) + ("\n" if findings else "") + "Re-run with --show to see"
            " which values, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    if unread:
        print(
            "\n" + unread.rstrip("\n") + f" No graded row was measured over the whole of"
            f" {directory.name}. This is not a pass.",
            file=sys.stderr,
        )
        return 2
    if not census.gradeable:
        print(
            f"\nno note in {directory.name} declares a filled height or a filled"
            " pressure, so neither graded row read anything. This is not a pass.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
