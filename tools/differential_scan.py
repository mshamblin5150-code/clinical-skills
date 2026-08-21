"""Check declared mechanical floors for ``clinical-note``'s differential.

    python tools/differential_scan.py <a run directory> [--show]

Ticket #192 extends the same run-directory command across the adjacent shapes it
already parses. **Drift row 23's mechanical floor** grades labeled Differential
blocks for a numbered, contiguous sequence beginning at ``1.``, one required
``Name - CODE`` opener per item, and no prose substitute. It never grades whether
the clinical likelihood order is right or discovers diagnosis-shaped prose under
an invented Assessment heading.

**Drift row 24's mechanical floor** reads every physical ``FILLED·proposed``
opener, including an unnumbered one, and checks same-line guideline tails against
the shipped USPSTF and threshold sheets wherever a direct join is mechanical. A
known screening, counseling, immunization, vaccination, target, cutoff or threshold
subject without a tail is a finding. Any other absent tail is a candidate outside
the exit status, because the scanner cannot decide whether that item rests on a
population or threshold. It also cannot decide whether a correctly extracted
recommendation applies to the patient. A clean scan is therefore not a walked row
23 or 24.

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

**A refusal is the welded pair ``NOT CODED: <code> <descriptor>, <reason>``, and
nothing else.** [#153] is why. The first version of this scanner paired a mark
with *the last code before it on the same physical line*, which is a guess, and
it failed in both directions at once: hard-wrapping a rationale so the mark
landed on its own line made the refusal **invisible** and the scan exited 0,
while a note's own drift-row-22 verdict -- *"the slot after the hyphen carries
M79.604, never a code marked NOT CODED"* -- was read as refusing the note's final
diagnosis and exited 1. **Describing the rule is what broke it**, which is
``phi_scan``'s self-exemption problem inverted. Both are gone because the pairing
is now a match rather than an inference: the code follows the mark, welded to it
by a colon, and a sentence writing ``NOT CODED`` without one is not a refusal.

**The form was not invented here.** ``icd10-cpt`` step 4 has always written
``NOT CODED: <code>  <descriptor>``, and all twelve worksheets in
``fixtures/filled-anchor/run-2/`` use it and nothing else. ``clinical-note`` was
the outlier; the clinician's ruling on 2026-08-16 made the two agree.

**A run written in the retired form is reported as unscanned, not as clean**, and
that is the whole point of retiring it. See the exit-status paragraph below.

**Four things carry the fix, and dropping any one of them reopens a symptom:**

- **The welded pair**, above.
- **A pipe table is skipped outright.** In a note a Markdown table is the drift
  matrix or a Medatrax field block, never a differential entry. This is what
  makes a verdict *about* row 22 unreadable as a violation of it, rather than
  merely unlikely to be one.
- **A form inside backticks is a mention, a form in running prose is a use.**
  ``spelling_scan.py``'s rule, adopted whole. The table limb covers a drift
  matrix; #153 also asks that **a README sentence** not read as an entry, and a
  sentence is not a table. Without this limb the verdict prose that filed #153
  stops being a false *finding* and becomes a false *exit 2* -- a quieter way to
  be wrong rather than a fix, and the review that caught it said so. It cuts both
  ways, which is what keeps it a rule: a refusal quoted inside backticks is prose
  about one and is not read either.
- **The conclusion is read by position, not by punctuation.** Inside a
  ``Final diagnosis`` region every code not sitting in a refusal clause is
  slot-held, whatever pins it. ``day-a`` run 2's case 7 wrote
  ``Final diagnosis: Streptococcal pharyngitis, suspected: J02.0`` with a colon
  where every sibling line used a hyphen, and the slot escaped **on punctuation
  alone** -- a real assertion of strep that the hyphen-only rule could not see.
  Non-hyphen pins are counted as ``malformed slot pins`` as well as read, because
  the punctuation rule is a separate rule and a reader should see it slipped.

**It reads no ``Differential`` heading, and since [#70] that is ruled rather than
incidental.** A slot is a ``<label> - <CODE>`` pin anywhere in the note outside a
conclusion region and outside a pipe table, which was true here before anyone had
decided it should be -- the ticket's own complaint was that *nothing but the
parser said so*. The clinician ruled on 2026-08-16 that the count runs to **every
diagnosis-shaped line in the Assessment**, whatever heading sits above it, because
the narrow reading is escapable by moving an uncoded diagnosis one heading down.
So this parser's omission is now the rule, written in ``SKILL.md`` under *The
shape of the differential* and in both templates.

**What the same ruling puts out of reach is C1's wide count**, and that is a
consequence rather than a gap. Telling ``Body mass index 28.6, in the overweight
range`` -- a diagnosis, which takes a ``Z68`` -- from ``Drug and condition
conflict: ...`` -- reasoning, which takes no code and no line of its own -- is a
reader's judgment, and so is finding a diagnosis-shaped line under a heading a run
invented.

**Ticket #164 nevertheless ruled for an additional QA floor.** Inside the two
template-labeled Differential blocks, this command counts numbered items, joins
them to required ``Name - CODE`` slots, and fails row 13 when an item has no slot.
The report prints both populations and states on every run that the wide Assessment
count still needs a reader. No numbered item in any labeled block is NOT RUN
(exit 2), never a clean zero; a confirmed missing code is exit 1 even when the old
slot limb read nothing. See ``NOT_VALIDATED_AGAINST`` for the limits.

**What it cannot reach is row 22 itself.** Deciding whether ``Pain in right leg``
is what ``M79.604`` says takes a reader, and paraphrase is permitted:
``Shortness of breath - R06.02`` and ``Mild dyspnea - R06.02`` are both correct.
So a clean scan is **not** a walked row, and row 22 says so beside the command.
This is ``filled-anchor``'s R2 residue arriving on a different rule.

**It no longer grades ``fixtures/hedged-dx`` run 1's case 2, and that is a
reclassification rather than a lost finding.** That note wrote
``Contiguous osteomyelitis of the right tibia or fibula - M86.9 NOT CODED, ...;
coded as pain in right leg - M79.604``, which is the exact shape #68 was filed
over and which this scanner used to catch. Its refusal is in the retired form, so
the run now reads as **unscanned** -- one bare mark, no refusal read. **N1 is
still failed by that run**; it is failed by a reader now, and
``fixtures/hedged-dx/assertions.md`` records which.

**What this scanner's validation set does not reach is ``NOT_VALIDATED_AGAINST``
below, not this paragraph.** [#162] is why it is an object: option 4 there was
*"say so in the docstring"*, and #241 had already ruled that shape insufficient on
a different module -- a **prose** edit to a limit fails nothing, so a limit written
as prose goes stale in the direction nobody notices. Every row is re-derived by an
assertion in ``test_differential_scan.py`` rather than merely stated, so a limit
that stops being true fails the suite. **The reasons live on the rows**; what
belongs here is the shape of the answer rather than a second copy of it.

**The coverage row is that list's third item arriving in the report.** ``notes with
a differential entry`` prints on every run **this tool reports on at all**, and a
short one carries a line saying what the verdict covers. The **status is
untouched** -- reported, not graded, the clinician's ruling on 2026-08-19, and the
row says why rather than this paragraph saying it again.

**That qualifier is not pedantry, and the first draft of this sentence was wrong
without it.** Every run that contains notes now reaches ``format_report`` before
an exit-2 limb, including a labeled block written as unnumbered prose. The report
therefore prints both zero populations before stderr says the QA floor was NOT
RUN. A missing-code finding still exits 1 first, so incomplete coverage cannot
suppress the defect it was meant to qualify.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record; an
entry label is a diagnosis attached to an encounter. Nothing but integers is
printed unless ``--show`` asks, and **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, on
``specificity_scan.py``'s arrangement and ``guidelines_search.py``'s before it: 0
when every reached floor is clean, 1 on a violation, and **2 for every way of not having
scanned** -- no argument, no directory, no notes in it, **no differential entry in
any note read, no numbered item in a labeled block, and any bare ``NOT CODED``
mark.** The last three matter most: a run
whose differential was written in some shape this parser does not read, or whose
refusals are written in the form row 22 retired, would otherwise report zero
violations and look like a pass.

**Where a violation and an incomplete scan both hold, 1 wins, and that ordering
is a decision.** A run carrying a real row-22 failure *and* a bare mark is
definitely not clean, so returning 2 would file the strongest thing known about
it under the weakest heading. Nothing is hidden by the choice: the unwelded count
prints above either message, and the exit-1 message names it, so a 1 still says
the finding is a floor rather than the whole count. Row 23's definite prose-shape
finding and row 24's definite tail findings use the same ordering; candidate tails
never affect it.

**The bare-mark limb is *any* bare mark, and the weaker version of it was wrong.**
It first fired only where a run had no welded refusal at all, and a real run
cleared that guard while leaving almost every refusal in it unread -- a handful
welded, the rest bare, and a clean row-22 line printed beneath them. That is the
partial-coverage-reading-as-complete shape, not a partial success. **The counts
are in ``fixtures/day-a/assertions.md`` and deliberately not repeated here**: they
were measured against a run under ``scratch/``, so nothing committed can
re-derive them, and a figure like that is kept in one place or it goes stale in
several. What is pinned instead is the behavior --
``test_differential_scan.py`` asserts a run mixing the two forms exits 2.

Extractor limits worth knowing before quoting a number:

- **A slot is a ``<label> - <CODE>`` pair**, the form ``SKILL.md`` requires under
  *Punctuation* -- the hyphen pins a value to its label. Both branches are read:
  [SOAP.md](../skills/clinical-note/SOAP.md) puts the pair and the rationale on
  one line, [HP.md](../skills/clinical-note/HP.md) puts the pair on its own line
  with the rationale beneath. **Inside the conclusion region the hyphen is not
  required**, per the positional rule above.
- **The conclusion region** opens on a ``Final diagnosis`` line and runs to the
  next blank one, which covers the value written on the heading's own line and a
  list written beneath it. ``Actual diagnosis/diagnoses`` opens one too: #153
  retired that heading from ``HP.md`` in favor of ``Final diagnosis`` on both
  branches, and **every H&P run written before then opens its conclusion that
  way**, so a scanner that stopped reading it would report exit 2 on a real run.
- **A refusal clause runs from the mark to the next ``;`` or the end of its
  line**, and the first code in it is the refused one. The semicolon bound is the
  collapse rule's separator, which is what lets one entry carry two refusals. The
  end-of-line bound is load-bearing in the other direction: a clause running to
  the end of the *paragraph* would swallow the entry written on the line below
  and hide a violation on it. ``test_differential_scan.py`` pins that case.
- **The clause continues onto the next line only where its own line yields no
  code**, which is the one split welding cannot prevent -- a wrap falling between
  ``NOT CODED:`` and the code.
- **The refused occurrence is not the slot occurrence.** A conclusion pinning
  ``J02.0`` with ``NOT CODED: J02.0`` on the line beneath is the same string
  twice, and only the one outside the clause is an assertion. Codes are excluded
  from slots **by position**, never by having been refused somewhere -- excluding
  by identity would make that note read as clean, which is precisely the case
  #153 filed.
- A code is ``[A-Z][0-9][0-9A-Z]`` with an optional dotted extension, so ``97.3``,
  ``4/10`` and ``s1,s2`` are not codes. ``B12`` is code-shaped and would be read as
  one; it fails nothing unless it sits in a slot and carries the mark. Inside a
  conclusion region it would read as a slot, which is the one place the positional
  rule costs something.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import run_grader

# ``M86.9``, ``R06.02``, ``A41.9``. Letter, digit, alphanumeric, optional dotted
# extension -- which is what keeps ``97.3`` and ``4/10`` out.
CODE = r"[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?"
CODE_TOKEN = re.compile(rf"\b{CODE}\b")

# ``Pain in right leg - M79.604``. The label runs back to the start of the line or
# to the nearest ``;`` or ``:``, so ``Final diagnosis: <label> - <code>`` yields
# the label and not the heading, and ``; coded as <label> - <code>`` yields the
# second pinned pair rather than swallowing the first.
SLOT = re.compile(rf"([^;:\n]{{2,120}}?)[ \t]+-[ \t]+({CODE})\b")

# The same pair at the opening of a numbered item. A later pair in the rationale
# cannot rescue an uncoded label; row 23 requires ``Name - CODE`` as the item's
# form, not merely as a substring somewhere on its line.
ITEM_SLOT = re.compile(rf"^[^;:\n]{{2,120}}?[ \t]+-[ \t]+{CODE}\b")

# The welded pair row 22 requires, and the only thing read as a refusal.
# Case-sensitive on purpose: the skill specifies the uppercase form, and matching
# ``not coded`` in prose would sweep up sentences discussing the rule.
MARK = re.compile(r"NOT CODED[ \t]*:")

# The retired form, and any other bare mention of the mark. Counted rather than
# read -- see the docstring on why silence would be the wrong report.
BARE_MARK = re.compile(r"NOT CODED(?![ \t]*:)")

# ``icd10-cpt`` step 4's block heading, which is a bare mark and is not a refusal.
# Removed before the bare marks are counted, so a worksheet's own scaffolding does
# not read as a note written in the retired form.
BLOCK_HEADING = re.compile(r"NOT CODED, NOTHING ESTABLISHED IT")

# A pipe table in a note is the drift matrix or a Medatrax field block, never a
# differential entry. Skipping the row outright is what makes a verdict *about*
# row 22 unreadable as a violation of it rather than merely unlikely to be one.
TABLE_ROW = re.compile(r"^[ \t]*\|")

# An inline code span. ``spelling_scan.py``'s distinction, adopted here for its
# reason: **a form inside backticks is a mention, a form in running prose is a
# use.** A table covers a drift matrix and not a sentence, and #153 asks for both
# -- *"a drift matrix row, a verdict table and a README sentence are not
# differential entries."* This is the limb that reaches the sentence.
CODE_SPAN = re.compile(r"`[^`\n]*`")

# Both conclusion openers, built from one alternation. ``Final diagnosis`` is what
# both templates write since #153; ``Actual diagnosis/diagnoses`` is the H&P
# heading it replaced, still read because every H&P run written before then opens
# its conclusion that way. Two literals holding one list is how a heading gets
# added to the reader and not to the labeller.
_HEADINGS = r"(?:Final diagnosis|Actual diagnosis/diagnoses)"
_OPENER = rf"^[ \t]*(?:\*\*|__)?{_HEADINGS}"
CONCLUSION = re.compile(_OPENER)
CONCLUSION_PREFIX = re.compile(rf"{_OPENER}[^:]*:")

# A conclusion code pinned the way the punctuation rule requires.
HYPHEN_PIN = re.compile(r"[ \t]-[ \t]+$")

# The two headings the branch templates render. This deliberately does not try
# to discover synonyms: ticket #164 ruled this check a declared floor over the
# labeled block, never the wide Assessment count that still needs a reader.
DIFFERENTIAL_HEADING = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]+)?(?:\*\*|__)?"
    r"Differential(?: diagnoses with rationale)?[ \t]*:?(?:\*\*|__)?[ \t]*$",
    re.IGNORECASE,
)
ITEM_NUMBER_PREFIX = re.compile(r"^[ \t]*\d+\.[ \t]+")

# A proposed item is opened by the tier label, whether or not the run obeyed row
# 21's numbering rule. Row 24 explicitly reaches an unnumbered screening item, so
# refusing that shape here would make the guideline floor easiest to evade where
# the proposal floor already failed.
PROPOSED_ITEM = re.compile(
    r"^FILLED·proposed[ \t]+(?:(\d+)\.[ \t]+)?(.*)$"
)
TIER_LABEL = re.compile(
    r"^(?:DERIVED|FILLED·asserted|FILLED·proposed|FLAG|GAPS|UNKNOWN)\b"
)
GUIDELINE_TAIL = re.compile(
    r"\[((?:uspstf|thresholds/[^:\]]+):[^\]]+|recalled, no shipped sheet[^\]]*)\]",
    re.IGNORECASE,
)
GUIDELINE_TAIL_START = re.compile(
    r"\[(?:uspstf|thresholds/[^:\]]+):|\[recalled, no shipped sheet",
    re.IGNORECASE,
)
GUIDELINE_TRIGGER = re.compile(
    r"\b(?:screen(?:ing)?|counsel(?:ing)?|immuniz\w*|vaccin\w*|target|cutoff|threshold)\b",
    re.IGNORECASE,
)
NO_GUIDELINE_DEPENDENCY = re.compile(
    r"\b(?:rests?|resting) on no population or threshold\b", re.IGNORECASE
)
USPSTF_CITATION = re.compile(
    r"^(?:grade[ \t]+([ABCDI])[^,]*|([ABCDI])[ \t]+statement),"
    r"[ \t]*(.+),[ \t]*(\d{4})$",
    re.IGNORECASE,
)
THRESHOLD_CITATION = re.compile(
    r"^([a-z0-9-]+)[ \t]+Class[ \t]+([A-Za-z0-9]+),[ \t]*([^,]+),[ \t]*(.+)$",
    re.IGNORECASE,
)
THRESHOLD_SIGNAL = re.compile(
    r"(?:>=|<=|>|<|≥|≤)[ \t]*\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?%?"
    r"|\d+(?:/\d+)(?:\.\d+)?%?"
    r"|\d+(?:\.\d+)?%"
)

REFERENCE_ROOT = Path(__file__).resolve().parent.parent / "reference"
USPSTF_SHEET = REFERENCE_ROOT / "guidelines-uspstf.md"
THRESHOLD_ROOT = REFERENCE_ROOT / "thresholds"


# **What this scanner's validation set does not reach**, declared rather than
# described -- [#162], option 4, and it is an object rather than a sentence for
# [#241]'s reason: a **prose** edit to a limit fails nothing, so a limit written as
# prose goes stale in the direction nobody notices. ``docx_write.NOT_APPLIED`` and
# ``reference_scan.NOT_REACHED`` are the two worked examples this copies.
#
# **Every row is re-derived by an assertion rather than asserted**, which is the
# half that makes it more than a docstring: ``test_differential_scan.py``'s
# ``TheValidationSetsLimitsAreDeclared`` runs the scanner over every committed
# directory it can be pointed at, so a row that stops being true fails the suite
# instead of standing as a claim nobody re-derives.
#
# **The prose surfaces point at this and copy none of it**, in the module docstring
# above and in ``CLAUDE.md``'s *Differential scan* section, and the same class
# asserts both. That is [#143]'s discipline made checkable -- one object, and no
# second place for it to go stale.
NOT_VALIDATED_AGAINST = (
    (
        "the exit-1 path on committed input",
        "**The branch has still never fired on output nobody edited**, and that is "
        "now the whole of this row rather than half of it. What used to be the "
        "other half was that the path could not be reached at all: every committed "
        "directory was turned away before a single entry was parsed, so an empty "
        "``findings`` there said nothing was read rather than nothing violates. "
        "``fixtures/slot-form-run`` retired that -- each of its notes parses slot "
        "entries **and** welded refusals, so one displaced code in any of them "
        "trips the branch, and the merge reads the directory. **What is missing is "
        "a committed run that genuinely violates, and it should stay missing**: a "
        "record edited until the checker complains is material authored to make a "
        "check pass its own examination, and #162's CI comment names the trap. So "
        "the branch is driven by **mutating** that run inside the suite, where the "
        "planted defect is legible in the test instead of baked into the record. "
        "``research_ledger.py`` and ``reference_scan.py`` keep the harder version "
        "of the old claim -- what they read is an assertion and an essay composed "
        "about a person, and neither has a redacted shape anyone could commit.",
    ),
    (
        "the aggregate of the exit-2 limbs",
        "Each of the four ways of not having scanned is separately correct and "
        "separately documented above, and none of them says what they come to "
        "together. **That total used to be *nothing committed is legible here at "
        "all*, and ``fixtures/slot-form-run`` ended it.** The residue is narrower "
        "and still worth declaring: most of the committed directories a reader "
        "would try are turned away, so checking one limb at a time still yields a "
        "coverage figure this tool has not earned. "
        "``fixtures/filled-anchor/run-2`` remains the sharp case -- a committed "
        "artifact composed in the required welded shape that belongs to "
        "``icd10-cpt``, so this scanner is aimed elsewhere deliberately. **It was "
        "*the* one until ``slot-form-run`` landed, and the first rewrite of this "
        "row kept the exclusivity while the same commit falsified it** -- the "
        "declared-limits object overclaiming about the tree it ships in, which is "
        "the defect #162 already records this rule committing once. Caught by the "
        "spec axis; the reason-bind cannot see it, because a word like *sole* is "
        "one the prose surfaces never copy.",
    ),
    (
        "partial coverage inside a run",
        "The *no differential entry* limb hangs on the run rather than on the note, "
        "so a single parsed entry carries a whole run past it and the notes that "
        "contributed nothing are invisible in the verdict. Since #162 the "
        "denominator is printed. Grading it was weighed and refused: a per-note "
        "limb fails any shift where one encounter's assessment carries no ranked "
        "list, which is the common case rather than the defective one, and a gate "
        "that refuses ordinary work is a gate people route around.",
    ),
    (
        "the row-13 labeled-block floor",
        "The additional QA join sees numbered items only inside the two template "
        "headings. A diagnosis-shaped line under another heading, an unnumbered "
        "prose diagnosis, and the clinical distinction between a diagnosis and "
        "reasoning remain outside it. The command therefore prints the narrow "
        "populations and the reader residue on every report; it never promotes "
        "its clean count to the wide Assessment verdict.",
    ),
)


@dataclass(frozen=True)
class Entry:
    """One code held in a slot, and the line it came from.

    ``conclusion`` marks the ones found inside a ``Final diagnosis`` region,
    which are located by position rather than by punctuation and are counted
    apart from the differential for the reason ``survey`` gives.
    """

    label: str
    code: str
    line: int
    conclusion: bool = False
    pinned: bool = True


@dataclass(frozen=True)
class NumberedItem:
    """One numbered item inside a template-labeled Differential block."""

    number: int
    label: str
    line: int
    coded: bool
    slot_count: int


@dataclass(frozen=True)
class RankingFinding:
    """One mechanically certain drift-row-23 shape violation."""

    line: int
    reason: str
    label: str = ""


@dataclass(frozen=True)
class ProposedItem:
    """One physical ``FILLED·proposed`` opener and its wrapped lines."""

    line: int
    text: str
    continuation: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class GuidelineFinding:
    """One mechanically certain drift-row-24 violation."""

    line: int
    reason: str
    label: str = ""


@dataclass(frozen=True)
class GuidelineCandidate:
    """An absent tail whose population-or-threshold dependency needs a reader."""

    line: int
    label: str


@dataclass(frozen=True)
class ThresholdRow:
    """One shipped threshold row, kept intact for citation joins."""

    source: str
    strength: str
    value: str
    context: str


@dataclass(frozen=True)
class Span:
    """Half-open ``[start, end)`` over one line: the text of a refusal clause."""

    start: int
    end: int

    def holds(self, position: int) -> bool:
        return self.start <= position < self.end


@dataclass(frozen=True)
class Note:
    """One note's slots, its refusals, and its bare marks."""

    entries: tuple[Entry, ...]
    refused: frozenset[str]
    unwelded_marks: int = 0
    labeled_differential_blocks: int = 0
    numbered_items: tuple[NumberedItem, ...] = ()
    ranking_findings: tuple[RankingFinding, ...] = ()
    proposed_items: tuple[ProposedItem, ...] = ()
    guideline_tails_checked: int = 0
    guideline_findings: tuple[GuidelineFinding, ...] = ()
    guideline_candidates: tuple[GuidelineCandidate, ...] = ()


REFUSED_CODE = "refused-code-in-differential-slot"
ROWS = {REFUSED_CODE: "clinical-note drift row 22 - refused code in slot"}
KINDS = tuple(ROWS)


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One entry whose slot holds a code the same note refused."""

    code: str
    label: str
    line: int


@dataclass(frozen=True)
class Scan:
    """Counts over a run, plus the findings ``--show`` prints."""

    notes: int
    notes_with_differential: int
    differential_entries: int
    conclusion_entries: int
    refused_codes: int
    unwelded_marks: int
    malformed_pins: int
    labeled_differential_blocks: int
    notes_with_labeled_differential: int
    numbered_items: int
    coded_numbered_items: int
    missing_code_items: tuple[NumberedItem, ...] = ()
    ranking_findings: tuple[RankingFinding, ...] = ()
    proposed_items: int = 0
    guideline_tails_checked: int = 0
    guideline_findings: tuple[GuidelineFinding, ...] = ()
    guideline_candidates: tuple[GuidelineCandidate, ...] = ()
    findings: tuple[Finding, ...] = ()


def _clause_end(line: str, start: int) -> int:
    """Where a refusal clause opened at ``start`` stops.

    At the next ``;`` -- the collapse rule's separator, which is what lets one
    entry carry two refusals -- or at the end of the line. **Never past the end
    of the line**, because a clause running to the end of the paragraph would
    swallow the entry written on the line below and hide a violation on it.
    """
    semicolon = line.find(";", start)
    return len(line) if semicolon == -1 else semicolon


def _refusals(lines: list[str]) -> tuple[set[str], dict[int, list[Span]]]:
    """Every welded refusal in a note, and the clause spans, keyed by line.

    The spans are what keep a refused code from also reading as an assertion:
    ``NOT CODED: J02.0 ...`` beneath a conclusion pinning ``J02.0`` is the same
    string twice, and only the occurrence outside the clause is the slot.
    """
    refused: set[str] = set()
    spans: dict[int, list[Span]] = {}

    def record(index: int, start: int, end: int, code: str) -> None:
        refused.add(code)
        spans.setdefault(index, []).append(Span(start, end))

    for index, line in enumerate(lines):
        for mark in MARK.finditer(line):
            end = _clause_end(line, mark.end())
            code = CODE_TOKEN.search(line, mark.end(), end)
            if code is not None:
                record(index, mark.end(), end, code.group(0))
                continue
            # The one split welding cannot prevent: a wrap between the mark and
            # its code. The clause continues onto the next line, and only when
            # its own line yielded nothing.
            if index + 1 < len(lines):
                following = lines[index + 1]
                end = _clause_end(following, 0)
                code = CODE_TOKEN.search(following, 0, end)
                if code is not None:
                    record(index + 1, 0, end, code.group(0))
    return refused, spans


def _conclusion_lines(lines: list[str]) -> set[int]:
    """The indices inside a conclusion region.

    A region opens on a ``Final diagnosis`` or ``Actual diagnosis/diagnoses``
    line and runs to the next blank one, which covers both layouts: the value on
    the heading's own line, and the list written beneath it.
    """
    inside: set[int] = set()
    index = 0
    while index < len(lines):
        if CONCLUSION.match(lines[index]):
            while index < len(lines) and lines[index].strip():
                inside.add(index)
                index += 1
        else:
            index += 1
    return inside


def _readable(line: str) -> str:
    """One line with everything that is *about* the rule masked out.

    **Blanked rather than dropped, and masked rather than deleted**, so every
    index below still matches the line and column a reader would count to -- and
    so a table following a conclusion closes the region the way a blank line does.

    Two things go. A **pipe table row** is the drift matrix or a Medatrax field
    block. An **inline code span** is a mention rather than a use, which is
    ``spelling_scan.py``'s rule and is what lets a note discuss row 22 in a
    sentence: ``never a code marked `NOT CODED``` is prose about the rule, and
    ``NOT CODED: M86.9 ...`` is a refusal. Without this limb the verdict sentence
    #153 filed over stops being a false *finding* and becomes a false *exit 2*,
    which is a quieter way to be wrong rather than a fix.
    """
    if TABLE_ROW.match(line):
        return ""
    return CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)


def _label_before(line: str, position: int) -> str:
    """The label a conclusion code is pinned to, for ``--show`` only."""
    segment = line[:position].rsplit(";", 1)[-1]
    segment = CONCLUSION_PREFIX.sub("", segment)
    return segment.strip(" \t-:.*_—–")


def _without_item_number(label: str) -> str:
    """Remove the visible ranking numeral from a slot label used by ``--show``."""
    return ITEM_NUMBER_PREFIX.sub("", label).strip()


def _labeled_differential_items(
    lines: list[str],
) -> tuple[int, list[NumberedItem], list[RankingFinding]]:
    """Count template-labeled blocks and their numbered items.

    A block ends at its first blank line, matching both branch templates. Only a
    ``Name - CODE`` slot on the numbered item's opening line satisfies the code
    join. Parentheses and colons are intentionally not accepted: drift row 23
    requires the hyphen-pinned form, and accepting a retired form here would let
    this QA row report a stronger result than the note earned.
    """
    blocks = 0
    items: list[NumberedItem] = []
    findings: list[RankingFinding] = []
    index = 0
    while index < len(lines):
        if not DIFFERENTIAL_HEADING.match(lines[index]):
            index += 1
            continue
        blocks += 1
        index += 1
        block_items: list[NumberedItem] = []
        content_lines: list[int] = []
        unnumbered_entry_lines: list[tuple[int, str]] = []
        while index < len(lines) and lines[index].strip():
            content_lines.append(index + 1)
            prefix = ITEM_NUMBER_PREFIX.match(lines[index])
            if prefix:
                item_text = lines[index][prefix.end() :]
                slots = list(SLOT.finditer(item_text))
                item = NumberedItem(
                    number=int(prefix.group(0).strip().removesuffix(".")),
                    label=item_text,
                    line=index + 1,
                    coded=bool(ITEM_SLOT.search(item_text)),
                    slot_count=len(slots),
                )
                items.append(item)
                block_items.append(item)
            elif ITEM_SLOT.search(lines[index]):
                unnumbered_entry_lines.append((index + 1, lines[index].strip()))
            index += 1
        if content_lines and not block_items:
            findings.append(
                RankingFinding(
                    line=content_lines[0],
                    reason="labeled Differential block is prose, not a numbered list",
                )
            )
            continue
        findings.extend(
            RankingFinding(
                line=line,
                reason="entry-shaped line is not its own numbered item",
                label=label,
            )
            for line, label in unnumbered_entry_lines
        )
        numbers = [item.number for item in block_items]
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            findings.append(
                RankingFinding(
                    line=block_items[0].line,
                    reason="numbering does not start at 1 and remain contiguous",
                )
            )
        for item in block_items:
            if not item.coded:
                findings.append(
                    RankingFinding(
                        line=item.line,
                        reason="numbered item lacks the required Name - CODE opener",
                        label=item.label,
                    )
                )
            elif item.slot_count != 1:
                findings.append(
                    RankingFinding(
                        line=item.line,
                        reason="one numbered item opens more than one pinned entry",
                        label=item.label,
                    )
                )
    return blocks, items, findings


def _pipe_cells(line: str) -> list[str]:
    """Cells from one simple Markdown table row."""
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def _uspstf_index() -> tuple[tuple[str, str, str], ...]:
    """Citation tuples from the shipped USPSTF sheet."""
    rows: list[tuple[str, str, str]] = []
    for line in USPSTF_SHEET.read_text(encoding="utf-8").splitlines():
        cells = _pipe_cells(line) if line.startswith("|") else []
        if len(cells) != 8 or cells[2] not in {"A", "B", "C", "D", "I"}:
            continue
        if not re.fullmatch(r"\d{4}", cells[4]):
            continue
        rows.append((cells[0], cells[2].casefold(), cells[4]))
    return tuple(rows)


USPSTF_ROWS = _uspstf_index()


def _topic_words(text: str) -> set[str]:
    stop = {
        "adult",
        "adults",
        "and",
        "discussed",
        "for",
        "infection",
        "offered",
        "of",
        "review",
        "screening",
        "status",
        "the",
    }
    words = {
        word
        for word in re.findall(r"[a-z0-9]+", text.casefold())
        if word not in stop and len(word) >= 3
    }
    lowered = text.casefold()
    if (
        "blood pressure" in lowered
        or "hypertension" in words
        or words & {"bp", "sbp", "dbp"}
    ):
        words.update(("blood", "pressure", "hypertension"))
    if words & {"target", "threshold", "cutoff"}:
        words.update(("target", "threshold", "cutoff"))
    return words


def _uspstf_subject_topics(item: str) -> list[tuple[str, str, str]]:
    """High-confidence lexical joins only; synonym-shaped misses stay candidates."""
    words = _topic_words(item)
    decisive: list[tuple[str, str, str]] = []
    for row in USPSTF_ROWS:
        shared = words & _topic_words(row[0])
        if not shared:
            continue
        # A one-token subject such as HIV is decisive. Longer subjects need most
        # of their informative words joined; ``blood pressure`` alone must not
        # join an adult screening item to the pediatric sheet row.
        if words <= shared or (len(shared) >= 2 and len(shared) / len(words) >= 0.67):
            decisive.append(row)
    return decisive


def _uspstf_citation_matches(item: str, grade: str, year: str) -> bool | None:
    """Whether a directly joined topic carries the cited grade and year.

    ``None`` means the subject could not be joined mechanically; it is a
    candidate for a reader, never a fabricated clean sheet comparison.
    """
    matches = _uspstf_subject_topics(item)
    if not matches:
        return None
    return any(row[1] == grade.casefold() and row[2] == year for row in matches)


def _normalized_value(text: str) -> str:
    return "".join(
        text.casefold()
        .replace("≥", ">=")
        .replace("≤", "<=")
        .replace(",", "")
        .split()
    )


def _threshold_index(path: Path) -> tuple[ThresholdRow, ...]:
    """Intact citation rows from one shipped threshold sheet."""
    rows: list[ThresholdRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = _pipe_cells(line) if line.startswith("|") else []
        if len(cells) != 8 or cells[0] in {"quantity", "---"}:
            continue
        source, population, value, strength = cells[4], cells[1], cells[2], cells[7]
        if not source or not population or not value or not strength:
            continue
        rows.append(
            ThresholdRow(
                source=source.casefold(),
                strength=strength.casefold(),
                value=_normalized_value(value),
                context=" ".join((cells[0], cells[3])),
            )
        )
    return tuple(rows)


def _threshold_signals(text: str) -> set[str]:
    """Comparator, ratio, and percent values strong enough for a direct join."""
    return {_normalized_value(signal) for signal in THRESHOLD_SIGNAL.findall(text)}


def _threshold_signal_values(text: str) -> set[str]:
    """Numeric cores used to disprove a claim that the sheet has no value."""
    return {signal.lstrip("<>=") for signal in _threshold_signals(text)}


def _read_proposed_items(lines: list[str]) -> list[ProposedItem]:
    """Read physical proposed-item openers and retain their continuation lines."""
    items: list[ProposedItem] = []
    index = 0
    while index < len(lines):
        match = PROPOSED_ITEM.match(lines[index])
        if not match:
            index += 1
            continue
        continuation: list[tuple[int, str]] = []
        following = index + 1
        while following < len(lines) and not TIER_LABEL.match(lines[following]):
            continuation.append((following + 1, lines[following]))
            following += 1
        items.append(
            ProposedItem(
                line=index + 1,
                text=match.group(2).strip(),
                continuation=tuple(continuation),
            )
        )
        index = following
    return items


def _guideline_floor(
    items: list[ProposedItem],
) -> tuple[int, list[GuidelineFinding], list[GuidelineCandidate]]:
    """Validate row 24's mechanical limbs and preserve its clinical ceiling."""
    checked = 0
    findings: list[GuidelineFinding] = []
    candidates: list[GuidelineCandidate] = []

    for item in items:
        opening_tails = list(GUIDELINE_TAIL.finditer(item.text))
        continuation_tails = [
            (line, text)
            for line, text in item.continuation
            if GUIDELINE_TAIL_START.search(text)
        ]
        if continuation_tails:
            findings.append(
                GuidelineFinding(
                    line=continuation_tails[0][0],
                    reason="guideline verdict is on a continuation line",
                    label=item.text,
                )
            )

        if not opening_tails:
            if continuation_tails:
                continue
            if NO_GUIDELINE_DEPENDENCY.search(item.text):
                continue
            if GUIDELINE_TRIGGER.search(item.text):
                findings.append(
                    GuidelineFinding(
                        line=item.line,
                        reason="population-or-threshold subject carries no guideline tail",
                        label=item.text,
                    )
                )
            else:
                candidates.append(GuidelineCandidate(item.line, item.text))
            continue

        for match in opening_tails:
            tail = match.group(1).strip()
            subject = (item.text[: match.start()] + item.text[match.end() :]).strip()
            lowered = tail.casefold()
            if lowered.startswith("recalled, no shipped sheet"):
                continue
            if lowered.startswith("uspstf:"):
                checked += 1
                verdict = tail.split(":", 1)[1].strip()
                if verdict.casefold().startswith("no row"):
                    if _uspstf_subject_topics(subject):
                        findings.append(
                            GuidelineFinding(
                                item.line,
                                "uspstf: no row contradicts a shipped topic",
                                item.text,
                            )
                        )
                    else:
                        candidates.append(GuidelineCandidate(item.line, item.text))
                    continue
                citation = USPSTF_CITATION.fullmatch(verdict)
                if citation is None:
                    findings.append(
                        GuidelineFinding(item.line, "malformed USPSTF verdict", item.text)
                    )
                    continue
                if not citation.group(3).strip():
                    findings.append(
                        GuidelineFinding(
                            item.line, "USPSTF population is empty", item.text
                        )
                    )
                    continue
                grade = citation.group(1) or citation.group(2)
                matched = _uspstf_citation_matches(subject, grade, citation.group(4))
                if matched is None:
                    candidates.append(GuidelineCandidate(item.line, item.text))
                elif not matched:
                    findings.append(
                        GuidelineFinding(
                            item.line,
                            "USPSTF grade, population, and year do not match a shipped row",
                            item.text,
                        )
                    )
                continue

            topic, verdict = tail.split(":", 1)
            topic = topic.split("/", 1)[1].strip()
            sheet = THRESHOLD_ROOT / f"{topic}.md"
            if not sheet.is_file():
                findings.append(
                    GuidelineFinding(
                        item.line, "threshold tail names no shipped topic", item.text
                    )
                )
                continue
            checked += 1
            rows = _threshold_index(sheet)
            verdict = verdict.strip()
            if verdict.casefold().startswith("sheet does not settle it"):
                subject_signals = _threshold_signal_values(subject.replace(",", ""))
                subject_words = _topic_words(subject)
                contradicts = any(
                    subject_signals & _threshold_signal_values(row.value)
                    and subject_words & _topic_words(row.context)
                    for row in rows
                )
                if contradicts:
                    findings.append(
                        GuidelineFinding(
                            item.line,
                            "sheet does not settle it contradicts a value in the shipped sheet",
                            item.text,
                        )
                    )
                else:
                    candidates.append(GuidelineCandidate(item.line, item.text))
                continue
            citation = THRESHOLD_CITATION.fullmatch(verdict)
            if citation is None:
                findings.append(
                    GuidelineFinding(item.line, "malformed threshold verdict", item.text)
                )
                continue
            source = citation.group(1).casefold()
            strength = citation.group(2).casefold()
            population = citation.group(3).strip()
            value = citation.group(4).strip()
            cited_value = _normalized_value(value)
            cited_signals = _threshold_signals(value)
            matching_row = any(
                row.source == source
                and row.strength == strength
                and (
                    cited_signals <= _threshold_signals(row.value)
                    if cited_signals
                    else cited_value in row.value
                )
                for row in rows
            )
            if (
                not population
                or not value
                or not matching_row
            ):
                findings.append(
                    GuidelineFinding(
                        item.line,
                        "threshold source, strength, population, and value do not match a shipped row",
                        item.text,
                    )
                )
    return checked, findings, candidates


def read_note(text: str) -> Note:
    """Parse one note into its slots, its refusals and its bare marks.

    Refusals are collected **note-wide** rather than per entry, because the H&P
    branch puts the code on one line and the refusal on the next -- so an entry
    line frequently carries no mark at all and the two cannot be paired
    positionally the way ``specificity_scan.py`` pairs a flag to its code.
    """
    lines = [_readable(line) for line in text.splitlines()]
    labeled_blocks, numbered_items, ranking_findings = _labeled_differential_items(lines)
    proposed_items = _read_proposed_items(lines)
    guideline_checked, guideline_findings, guideline_candidates = _guideline_floor(
        proposed_items
    )
    refused, spans = _refusals(lines)
    conclusion = _conclusion_lines(lines)
    unwelded = sum(
        len(BARE_MARK.findall(BLOCK_HEADING.sub("", line))) for line in lines
    )

    def in_a_clause(index: int, position: int) -> bool:
        return any(span.holds(position) for span in spans.get(index, ()))

    entries: list[Entry] = []
    for index, line in enumerate(lines):
        number = index + 1
        if index in conclusion:
            # Position, not punctuation. Inside the conclusion every code that is
            # not being refused is being asserted, whatever pins it -- which is
            # what closes the hole a colon opened in day-a run 2's case 7.
            for match in CODE_TOKEN.finditer(line):
                if in_a_clause(index, match.start()):
                    continue
                entries.append(
                    Entry(
                        label=_label_before(line, match.start()),
                        code=match.group(0),
                        line=number,
                        conclusion=True,
                        pinned=bool(HYPHEN_PIN.search(line[: match.start()])),
                    )
                )
            continue
        for match in SLOT.finditer(line):
            if in_a_clause(index, match.start(2)):
                continue
            entries.append(
                Entry(
                    label=_without_item_number(match.group(1)),
                    code=match.group(2),
                    line=number,
                )
            )
    return Note(
        entries=tuple(entries),
        refused=frozenset(refused),
        unwelded_marks=unwelded,
        labeled_differential_blocks=labeled_blocks,
        numbered_items=tuple(numbered_items),
        ranking_findings=tuple(ranking_findings),
        proposed_items=tuple(proposed_items),
        guideline_tails_checked=guideline_checked,
        guideline_findings=tuple(guideline_findings),
        guideline_candidates=tuple(guideline_candidates),
    )


def note_findings(note: Note) -> list[Finding]:
    """Row 22's slot limb, applied to one note."""
    return [
        Finding(kind=REFUSED_CODE, code=entry.code, label=entry.label, line=entry.line)
        for entry in note.entries
        if entry.code in note.refused
    ]


def survey(notes: list[Note]) -> Scan:
    """Count across a run. Takes parsed notes rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift.

    **Differential and conclusion entries are counted apart**, because the
    exit-2 limb hangs on the differential alone. Every note in
    ``fixtures/filled-anchor/notes`` carries a ``Final diagnosis`` list and none
    of them pins a differential code, so a single total would rescue that set
    into looking scanned on the strength of a conclusion nobody graded.

    **``notes_with_differential`` is the coverage denominator**, and the reason it
    is counted at all is ``NOT_VALIDATED_AGAINST``'s third row rather than this
    docstring's to give.

    **Against the differential and never against the note, which was measured
    rather than reasoned.** The two denominators come apart on a recorded run: a
    note carrying a ``Final diagnosis`` and no differential has its conclusion codes
    read by position and graded, so counting notes with *any* entry would report
    such a run as nearly covered when its differential went unread. This is the
    narrower count, and ``format_report`` says beside it what the wider one still
    covers rather than claiming those notes went ungraded. **The figures behind that
    were taken against a run under ``scratch/``, so nothing committed re-derives
    them and none is stated here** -- [#143], and the shape is pinned by
    ``TheCoverageRowSeparatesReadableFromClean`` on notes built in that file.
    """
    found = [finding for note in notes for finding in note_findings(note)]
    entries = [entry for note in notes for entry in note.entries]
    numbered_items = [item for note in notes for item in note.numbered_items]
    ranking_findings = [
        finding for note in notes for finding in note.ranking_findings
    ]
    guideline_findings = [
        finding for note in notes for finding in note.guideline_findings
    ]
    guideline_candidates = [
        candidate for note in notes for candidate in note.guideline_candidates
    ]
    return Scan(
        notes=len(notes),
        notes_with_differential=sum(
            1 for note in notes if any(not entry.conclusion for entry in note.entries)
        ),
        differential_entries=sum(1 for entry in entries if not entry.conclusion),
        conclusion_entries=sum(1 for entry in entries if entry.conclusion),
        refused_codes=sum(len(note.refused) for note in notes),
        unwelded_marks=sum(note.unwelded_marks for note in notes),
        malformed_pins=sum(1 for entry in entries if entry.conclusion and not entry.pinned),
        labeled_differential_blocks=sum(
            note.labeled_differential_blocks for note in notes
        ),
        notes_with_labeled_differential=sum(
            bool(note.labeled_differential_blocks) for note in notes
        ),
        numbered_items=len(numbered_items),
        coded_numbered_items=sum(item.coded for item in numbered_items),
        missing_code_items=tuple(item for item in numbered_items if not item.coded),
        ranking_findings=tuple(ranking_findings),
        proposed_items=sum(len(note.proposed_items) for note in notes),
        guideline_tails_checked=sum(note.guideline_tails_checked for note in notes),
        guideline_findings=tuple(guideline_findings),
        guideline_candidates=tuple(guideline_candidates),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no code and no label unless ``show``.

    **The coverage row prints on every run and not only on a short one**, which is
    [#258]'s ruling on ``phi_scan`` and ``spelling_scan`` borrowed whole: a reader
    who learns to read a qualifier reads its absence as the stronger claim. The
    *qualifier* beneath the verdict is a finding about the run and prints only when
    the run is short, because a caveat printed unconditionally is one nobody reads.
    """
    # A zero is earned only where the limb had a population to inspect. Another
    # limb's finding must not turn absence here into a plausible clean count.
    row_22 = str(len(scan.findings)) if scan.differential_entries else "NOT RUN"
    row_13 = str(len(scan.missing_code_items)) if scan.numbered_items else "NOT RUN"
    row_23 = (
        str(len(scan.ranking_findings))
        if scan.labeled_differential_blocks
        else "NOT RUN"
    )
    row_24 = str(len(scan.guideline_findings))

    # Plain ASCII throughout, on ``specificity_scan.py``'s reasoning: this prints
    # to a Windows console, where anything outside cp1252 comes back as a question
    # mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"differential scan over {source}",
        "",
        f"  notes read                       {scan.notes}",
        f"  notes with a differential entry  {scan.notes_with_differential} of {scan.notes}",
        f"  differential entries             {scan.differential_entries}",
        f"  conclusion entries               {scan.conclusion_entries}",
        f"  codes marked NOT CODED           {scan.refused_codes}",
        f"  unwelded NOT CODED marks         {scan.unwelded_marks}",
        f"  malformed slot pins              {scan.malformed_pins}",
        "",
        f"  labeled Differential blocks read      {scan.labeled_differential_blocks}"
        f" in {scan.notes_with_labeled_differential} of {scan.notes} notes",
        f"  numbered items in labeled blocks     {scan.numbered_items}",
        f"  numbered items carrying a code       {scan.coded_numbered_items}"
        f" of {scan.numbered_items}",
        "  declared floor: these counts cover labeled Differential blocks only;",
        "  the wide Assessment count still needs a reader.",
        "",
        f"  row 22 - refused code in a slot  {row_22}",
        f"  row 13 floor - numbered item without a code  {row_13}",
        f"  row 23 floor - ranking shape violations  {row_23}",
        "  declared floor: clinical likelihood order still needs a reader.",
        "",
        f"  FILLED proposed items read                 {scan.proposed_items}",
        "  guideline tails checked against shipped sheets  "
        f"{scan.guideline_tails_checked}",
        f"  row 24 - guideline tail violations  {row_24}",
        "  row 24 candidates - dependency needs a reader  "
        f"{len(scan.guideline_candidates)}",
        "  declared floor: whether a recommendation applies to the patient still"
        " needs a reader.",
    ]
    ungraded = scan.notes - scan.notes_with_differential
    if ungraded > 0:
        # **Named against the differential and not against the note**, because the
        # two come apart on a real run and the wider claim would be false. A note
        # with a conclusion entry and no differential entry has its conclusion codes
        # read by position and graded. So what went unread is the differential,
        # which is what row 22 is about and what the exit-2 limb above keys on, and
        # the second line says the rest rather than leaving it to be inferred.
        lines += [
            "",
            f"  {ungraded} note(s) carry no differential entry, so the slot limb"
            " read nothing from their differential.",
            "  A conclusion code in such a note is read by position and graded"
            " anyway.",
        ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    line {finding.line:<5} {finding.code:<9} {finding.label}")
        for item in scan.missing_code_items:
            lines.append(f"    line {item.line:<5} NO CODE   {item.label}")
        for finding in scan.ranking_findings:
            lines.append(
                f"    line {finding.line:<5} ROW 23    {finding.reason} {finding.label}".rstrip()
            )
        for finding in scan.guideline_findings:
            lines.append(
                f"    line {finding.line:<5} ROW 24    {finding.reason} {finding.label}".rstrip()
            )
        for candidate in scan.guideline_candidates:
            lines.append(
                f"    line {candidate.line:<5} CANDIDATE {candidate.label}".rstrip()
            )
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


@dataclass(frozen=True)
class Source:
    directory: Path
    texts: tuple[str, ...]


def _load(parsed: run_grader.Parsed) -> Source:
    directory = Path(parsed.source)
    if not directory.is_dir():
        raise run_grader.SourceError(f"no directory named {directory.name}")
    texts = tuple(read_notes(directory))
    if not texts:
        raise run_grader.SourceError(f"no notes found in {directory.name}")
    return Source(directory, texts)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey([read_note(text) for text in source.texts])
    has_findings = bool(
        scan.findings
        or scan.missing_code_items
        or scan.ranking_findings
        or scan.guideline_findings
    )
    diagnostics: list[str] = []
    if has_findings:
        messages = []
        if scan.findings:
            messages.append(
                f"{len(scan.findings)} entry/entries hold a code the note refused,"
                " failing clinical-note drift row 22."
            )
        if scan.missing_code_items:
            messages.append(
                f"{len(scan.missing_code_items)} numbered differential item(s)"
                " carry no code in the required slot, failing clinical-note drift row 13."
            )
        if scan.ranking_findings:
            messages.append(
                f"{len(scan.ranking_findings)} differential ranking shape violation(s),"
                " failing clinical-note drift row 23."
            )
        if scan.guideline_findings:
            messages.append(
                f"{len(scan.guideline_findings)} guideline-tail violation(s),"
                " failing clinical-note drift row 24."
            )
        message = "\n" + " ".join(messages)
        message += " Re-run with --show to see which, and do not paste that output."
        if scan.unwelded_marks:
            message += (
                f" {scan.unwelded_marks} further mark(s) are unwelded and were not"
                " read, so this is a floor rather than the whole count."
            )
        diagnostics.append(message)
    coverage_failed = False
    if not scan.differential_entries:
        row_13 = (
            " row 13 floor was not run: no numbered item was found inside a labeled Differential block."
            if not scan.numbered_items
            else ""
        )
        diagnostics.append(
            f"no differential entry found in {scan.notes} note(s) in {source.directory.name}."
            " The row 22 slot limb was not run."
            + row_13
            + " This is not a clean run."
        )
        coverage_failed = True
    if scan.unwelded_marks and not has_findings:
        diagnostics.append(
            f"\n{scan.unwelded_marks} NOT CODED mark(s) in {source.directory.name} are not"
            " welded to a code, so no rule could pair them with one."
            " Refusals here are written in the form row 22 retired."
            " The slot limb was not evaluated -- this is not a clean run."
        )
        coverage_failed = True
    if not scan.numbered_items and scan.differential_entries:
        diagnostics.append(
            f"\nrow 13 floor was not run in {source.directory.name}: no numbered item"
            " was found inside a labeled Differential block. This is not a clean"
            " QA result; the wide Assessment count still needs a reader."
        )
        coverage_failed = True
    return run_grader.Grade(
        scan=scan,
        source=source.directory.name,
        findings_failed=has_findings,
        coverage_failed=coverage_failed,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage="usage: differential_scan.py <a run directory> [--show]",
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
