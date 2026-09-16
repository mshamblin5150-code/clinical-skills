# A guideline verdict takes one wording and a near miss is a finding

**Measured at:** ae681aecdecb1efea1c987aa7aabdae49f7bdfa6

Ticket [#1337](https://github.com/mshamblin5150-code/clinical-skills/issues/1337) was filed from the
grilling that produced [ADR 0252](0252-the-threshold-tail-class-is-the-sheet-cell-and-the-sheet-decides-where-it-ends.md).
`python tools/differential_scan.py fixtures/descriptor-agreement-note-path-control/notes` exits 1
with 8 drift row 24 findings, all `malformed threshold verdict`, over one note that ADR 0252 leaves
failing. The clinician ruled the shapes in a grilling on 2026-09-16.

Read line by line, the 8 tails take four shapes: 4 are a `sheet does not settle` verdict naming a
source and a subject, 2 name a subject with no source, 1 writes `grade` where the threshold tail
takes `Class`, and 1 cites a narrative row with no `Class` and with a page. The grilling found a
ninth nonconforming tail the ticket did not count. Line 132 ends
`[recalled, no single shipped sheet governs the combined interval]`, which no tail pattern opens,
so the scanner reads that item as carrying no tail and lists it among the candidates outside the
exit status. The grilling also found that `skills/clinical-note/SKILL.md` documents a verdict no
tool recognizes: *if the source page cannot be read, the tail says `recalled, source page unread`*.

## Ruling 1 — the sheet verdict is `sheet does not settle it` and nothing else

A threshold sheet that holds no row for an item earns exactly
`[thresholds/<topic>: sheet does not settle it]`. The verdict names no subject and no source. The
scanner matches the verdict whole rather than by prefix, so
`sheet does not settle offloading`, `idsa-2014, sheet does not settle it`, and
`sheet does not settle it, offloading` are each `malformed threshold verdict`.

"It" is the item on the same line, and the scanner already disproves the verdict against that
item's text. A subject written into the tail is a second statement of the same claim that can
disagree with the first, as the fixture's `Keep the toe clean and covered` beside
`routine wound-care wording` does, and agreement between the two is a reading. A source narrows a
verdict about the whole sheet to one of its sources, which leaves unsaid whether the others were
consulted and adds nothing where the sheet has one source. This is
[ADR 0017](0017-a-run-joins-a-threshold-sheet-on-the-artifact-column-and-the-state-describes-the-read-behind-it.md)'s
refusal to qualify the verdict in its tail, applied to a subject and a source.

Accepting a subject, with or without a leading source, and grading only its shape was declined: it
gives one verdict three documented wordings and grades none of the words that differ.

## Ruling 2 — `grade` and a paged narrative tail are refused, with no alternative form

A threshold tail takes `<source> Class <class>, <population>, <value>`, and under ADR 0252 the class
is the sheet's cell. `uspstf-2021-tobacco grade A, ...` is refused; the documented form is
`uspstf-2021-tobacco Class A, ...`. `grade` belongs to the `uspstf:` tail, and admitting it as a
synonym in the threshold tail admits the next borrowed word on the same argument.

`gold-2026 narrative, <population>, <value>, p45` is refused; the documented form is
`gold-2026 Class narrative, <population>, <value>`. A note never writes a page for a sheet row,
because the row carries the page. A page belongs only in the `guideline/` tail, for a
recommendation the sheet scoped out.

## Ruling 3 — a tail keyword that opens no documented form is a finding

A bracketed segment on a `FILLED·proposed` line that opens with one of the tail keywords `uspstf`,
`thresholds/`, `guideline/`, or `recalled`, and that no documented tail form reads, is a row 24
finding, `malformed guideline tail`, with exit 1. Line 132's
`[recalled, no single shipped sheet governs the combined interval]` is such a segment. Its wording
is also a new name for a silence, which ADR 0017's *no fourth silence* already refuses.

The finding is exit 1 rather than an [ADR 0230](0230-a-measured-partial-read-prints-an-admissible-unread-remainder-that-exits-not-scanned-and-is-declared-only-where-no-candidate-count-is-admissible.md)
unread remainder because the scanner read the segment and established that it does not follow the
documented grammar; that is a defect in the note, not input the tool could not read. The keyword
prefix is the bound. A bracket on a plan line may be ordinary prose, and one opening with a keyword
is an attempt at a verdict.

What this cannot reach is a verdict attempt opening with some other word, such as `[no sheet ...]`,
which stays read as no tail. That limit is declared in `differential_scan.NOT_VALIDATED_AGAINST` rather
than in prose.

## Ruling 4 — `recalled, source page unread` is a recognized verdict and grades as a candidate

The scanner reads `[recalled, source page unread]` as a documented verdict. Nothing shipped can
disprove that a page could not be read, so the item is a candidate outside the exit status, the
treatment `recalled, no shipped sheet` already receives where its subject joins no topic. The
wording is matched whole on the terms of ruling 1. The documented `recalled` wordings are therefore
exactly `recalled, no shipped sheet`, with its optional `; catalog lists <document>` limb, and
`recalled, source page unread`, and ruling 3 tests against that set.

Retiring the form in favor of the `guideline/` tail was declined, because that tail requires the
page the verdict says could not be read.

`skills/clinical-note/SKILL.md` gains one worked line in this form, so the existing test that runs
the scanner over the skill's worked examples grades it.

## Ruling 5 — the fixture is a divergent run and says so

`fixtures/descriptor-agreement-note-path-control/notes/case-01.md` is not edited. It is #1139's
retained blind path run, and `tools/test_anchor_scan.py` depends on it for descriptor agreement.
Under rulings 1 through 3 its row 24 findings are correct verdicts, which makes it a **Divergent
run** for row 24.

The fixture's `README.md` gains a section declaring that, naming the four refused classes: a sheet
verdict naming a subject or a source, `grade` written for `Class`, a narrative tail with no `Class`
and with a page, and a `recalled` wording outside the documented set. It says that
`differential_scan` exits 1 over the directory and that the exit is correct. It states no count a
command re-derives.

A test runs the scanner over the directory and asserts the set of finding reasons, not their
number, so a later grammar change that begins accepting one of these shapes fails the test rather
than leaving the README describing a divergence that no longer holds.

## Ruling 6 — the skill states the one wording

`skills/clinical-note/SKILL.md` states beside the three silences that `sheet does not settle it` is
written whole with no subject and no source, and that the `recalled` verdicts are the two wordings
of ruling 4.

## Consequences

- `tools/differential_scan.py`, its tests, `skills/clinical-note/SKILL.md`, and the fixture's
  `README.md` change together.
- A run in flight is graded under this record by rerunning `differential_scan`. No other committed
  record is known to carry these shapes; the build reruns the scanner over every committed
  `clinical-note` notes directory before claiming none does.
