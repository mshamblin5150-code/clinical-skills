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

**What the same ruling puts out of reach is C1's own count**, and that is a
consequence rather than a gap. Telling ``Body mass index 28.6, in the overweight
range`` -- a diagnosis, which takes a ``Z68`` -- from ``Drug and condition
conflict: ...`` -- reasoning, which takes no code and no line of its own -- is a
reader's judgment, and so is finding a diagnosis-shaped line under a heading a run
invented. **A scanner reading the labeled block would be checking the narrow
reading the ruling rejected**, reporting clean on precisely the note that moved a
line down one heading. [#164] holds what a partial one could still be worth.

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
without it.** A run where *no* note carries a differential entry never reaches
``format_report`` -- the exit-2 limb fires first -- so the most uncovered run of
all prints no coverage row. It is louder rather than quieter, which is why the
ordering stands: it exits 2 with its own message. What the row makes visible is
the interval **between** those two, where the old report said nothing at all.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record; an
entry label is a diagnosis attached to an encounter. Nothing but integers is
printed unless ``--show`` asks, and **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, on
``specificity_scan.py``'s arrangement and ``guidelines_search.py``'s before it: 0
when every slot is clean, 1 on a violation, and **2 for every way of not having
scanned** -- no argument, no directory, no notes in it, **no differential entry in
any note read, and any bare ``NOT CODED`` mark.** The last two matter most: a run
whose differential was written in some shape this parser does not read, or whose
refusals are written in the form row 22 retired, would otherwise report zero
violations and look like a pass.

**Where a violation and an incomplete scan both hold, 1 wins, and that ordering
is a decision.** A run carrying a real row-22 failure *and* a bare mark is
definitely not clean, so returning 2 would file the strongest thing known about
it under the weakest heading. Nothing is hidden by the choice: the unwelded count
prints above either message, and the exit-1 message names it, so a 1 still says
the finding is a floor rather than the whole count.

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

from console_codec import use_utf8

# ``M86.9``, ``R06.02``, ``A41.9``. Letter, digit, alphanumeric, optional dotted
# extension -- which is what keeps ``97.3`` and ``4/10`` out.
CODE = r"[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?"
CODE_TOKEN = re.compile(rf"\b{CODE}\b")

# ``Pain in right leg - M79.604``. The label runs back to the start of the line or
# to the nearest ``;`` or ``:``, so ``Final diagnosis: <label> - <code>`` yields
# the label and not the heading, and ``; coded as <label> - <code>`` yields the
# second pinned pair rather than swallowing the first.
SLOT = re.compile(rf"([^;:\n]{{2,120}}?)[ \t]+-[ \t]+({CODE})\b")

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
        "The exit-1 path fires on nothing committed and never will. A run directory "
        "is a patient record under gitignored ``scratch/`` or ``output/``, so no run "
        "can be committed and CI can never see one -- every test of the violation "
        "path builds a synthetic note. ``research_ledger.py`` and "
        "``reference_scan.py`` have the same property for the same reason, so it is "
        "a class of three rather than a fixture that went stale. What the tests "
        "below can still do is re-derive that no committed set reaches it, which is "
        "the honest half of the claim.",
    ),
    (
        "the aggregate of the exit-2 limbs",
        "Each of the four ways of not having scanned is separately correct and "
        "separately documented above, and none of them says what they come to "
        "together: both committed sets are refused, so a reader who checks one limb "
        "at a time infers a coverage this tool does not have. "
        "``fixtures/filled-anchor/run-2`` is the sharp case -- the one committed "
        "artifact written in the mandated welded form is an ``icd10-cpt`` worksheet "
        "set, which this scanner is pointed away from by design.",
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
    notes_with_differential: int
    differential_entries: int
    conclusion_entries: int
    refused_codes: int
    unwelded_marks: int
    malformed_pins: int
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


def read_note(text: str) -> Note:
    """Parse one note into its slots, its refusals and its bare marks.

    Refusals are collected **note-wide** rather than per entry, because the H&P
    branch puts the code on one line and the refusal on the next -- so an entry
    line frequently carries no mark at all and the two cannot be paired
    positionally the way ``specificity_scan.py`` pairs a flag to its code.
    """
    lines = [_readable(line) for line in text.splitlines()]
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
                Entry(label=match.group(1).strip(), code=match.group(2), line=number)
            )
    return Note(
        entries=tuple(entries), refused=frozenset(refused), unwelded_marks=unwelded
    )


def note_findings(note: Note) -> list[Finding]:
    """Row 22's slot limb, applied to one note."""
    return [
        Finding(code=entry.code, label=entry.label, line=entry.line)
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
        f"  row 22 - refused code in a slot  {len(scan.findings)}",
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
    if not scan.differential_entries:
        print(
            f"no differential entry found in {scan.notes} note(s) in {directory.name}."
            " Nothing was scanned -- this is not a clean run.",
            file=sys.stderr,
        )
        return 2
    print(format_report(scan, source=directory.name, show=show))
    # **A confirmed violation outranks an incomplete scan, and the ordering is a
    # decision rather than an accident.** Both conditions can hold at once, and a
    # status can carry one. A run holding a real row-22 failure *and* a bare mark
    # is definitely not clean, so reporting it as *not scanned* would file the
    # strongest thing known about it under the weakest heading. Nothing is hidden
    # either way -- ``unwelded NOT CODED marks`` is printed above both messages,
    # so an exit 1 still shows how much went unread.
    if scan.findings:
        print(
            f"\n{len(scan.findings)} entry/entries hold a code the note refused,"
            " failing clinical-note drift row 22."
            " Re-run with --show to see which, and do not paste that output."
            + (
                f" {scan.unwelded_marks} further mark(s) are unwelded and were not"
                " read, so this is a floor rather than the whole count."
                if scan.unwelded_marks
                else ""
            ),
            file=sys.stderr,
        )
        return 1
    if scan.unwelded_marks:
        # **Any** bare mark, not only a run with no welded refusal at all. The
        # weaker test was written first and a real run refuted it, clearing the
        # guard on a handful of welded refusals while the rest went unread. A run
        # is either written in the form row 22 reads or it is not scanned, and
        # there is no useful middle. Counts in fixtures/day-a/assertions.md.
        print(
            f"\n{scan.unwelded_marks} NOT CODED mark(s) in {directory.name} are not"
            " welded to a code, so no rule could pair them with one."
            " Refusals here are written in the form row 22 retired."
            " The slot limb was not evaluated -- this is not a clean run.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
