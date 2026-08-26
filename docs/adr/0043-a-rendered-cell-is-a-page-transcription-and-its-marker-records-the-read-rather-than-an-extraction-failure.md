# A rendered cell is a page transcription and its marker records the read rather than an extraction failure

[#501](https://github.com/mshamblin5150-code/clinical-skills/issues/501) was filed over two rows in
`reference/thresholds/diabetes.md` that declare `RENDERED:` while their snippet bodies sit verbatim
on their cited page — so the ordinary page check would have passed them, and the marker bought them
out of a gate they did not need. The ticket read that as a **denominator** defect: the run prints how
many rows declared the marker, and a reader takes that figure for a measurement of how badly the
corpus extracts.

Grilled 2026-08-26 against `e55e22f`, with the corpus and PyMuPDF present so every figure below was
re-derived rather than inherited from the ticket's four sweep comments. **Six decisions, ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

## Measured before ruling, at `e55e22f`

Every figure in this section is counted against `ADA/standards-of-care-2026.pdf`, which lives outside
this repo. **Nothing committed re-derives one.** They are stated here once and nowhere else.

- **The ticket's finding reproduces exactly.** `diabetes.md` parses to 357 rows, 36 carry the marker,
  and exactly 2 have bodies verbatim on their cited page — the two the ticket names, at `:674`
  `p109/narrative/088` and `:736` `p204/narrative/143`.
- **Both flagged rows sit beside a genuinely unreadable one from the same table**, and other rows of
  that same table are on-page and carry no marker:

  | line | rec | marker | body on cited page |
  | ---: | --- | --- | --- |
  | 673 | `p109/narrative/087` | `RENDERED:` | no |
  | 674 | `p109/narrative/088` | `RENDERED:` | **yes** |
  | 675 | `p109/narrative/089a` | — | yes |
  | 676 | `p109/narrative/089b` | — | yes |
  | 734 | `p204/narrative/141` | `RENDERED:` | no |
  | 735 | `p204/narrative/142` | — | yes |
  | 736 | `p204/narrative/143` | `RENDERED:` | **yes** |

  So the page really was rendered — `087` and `141` prove that read happened — and the marker
  travels with the page read rather than with the cell.

- **The 2-against-34 split has a mechanism, and it is not extraction.** The 36 cells are two kinds of
  writing. Most are **reconstructions** carrying editorial scaffolding that is nowhere on the page as
  a phrase — `"Table 16.1 DKA diagnostic criteria; all three criteria required; Ketosis; …"` — and
  cannot resolve by construction. The two are **linear transcriptions** of one run of page text. What
  the ticket's proposed check would measure is whether a drafter's cell happened to linearize.
- **The marker buys out of one gate, not three.** Disabling it and grading all 36 rows normally moves
  `CITATION tier 2` from `0` to `36` and leaves `WATERMARK 0 refusing` **unchanged**. Not one of the
  36 would have been refused by gate 4, so every interleave refusal the marker is credited with
  skipping is one that would never have fired.
- **The tier-0 skip note is unreachable on the only sheet that has markers.** `rendered` is
  incremented at `tools/threshold_sheet.py:1171`, inside the per-source loop and past the `continue`
  at `:1152` that drops an ungraded source. `diabetes.md`'s only source is `bound`, so the counter
  stays `0` and that line has never printed on any committed sheet.
- **`CONTEXT.md` has no entry for the marker at all**, and its **Snippet** entry at `:278` requires
  *verbatim*, which most of the 36 cells are not.

## Ruling 1 — the marker names an audit claim, and an extraction failure is a common cause of one and never its definition

[#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296) ruled `RENDERED:` an audit
claim: an agent rendered the cited page and confirmed the label and value belong together. That is
what the marker means. That extraction also garbled the cell is the usual **reason** somebody did the
read, and it is not part of the claim.

**Both named rows stand, untouched.** The measurement above says each sits one line from a row whose
table genuinely defeated the reader, so the page was on screen and the claim is true. A passing page
check is not grounds to delete a true record of work performed.

### Rejected: the marker means extraction failed, so a cleanly extracting row must drop it

This is machine-checkable, which is its whole appeal, and it is why the ticket leans toward it. It
would delete a true audit claim in order to make a printed count read more cleanly — which is the
thing the ticket's own *What must not come out of this* forbids in as many words.

### Rejected: split into two markers, one for the read and one for the extraction failure

It buys a sharper denominator at the price of a choice every future drafter must make correctly, with
no gate able to catch a wrong one. A new silent failure mode in exchange for a number.

## Ruling 2 — a `RENDERED:` cell is a **page transcription**, and the term is filed in `CONTEXT.md` against **Snippet**

`CONTEXT.md:278` defines a **snippet** as the shortest *verbatim* fragment of a guideline, and says
in the entry itself that verbatim is what makes a fabricated citation detectable. Most `RENDERED:`
cells fail that test. They sit in the snippet column and are not snippets.

The clause the build files, against **Snippet**, on [ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)'s rule:

> **Page transcription**:
> What a reader saw on a rendered guideline page, reassembled into one cell — faithful to the page's
> layout and meaning rather than to its text stream, so a table's columns may be joined and a
> figure's branch named. It is what a cell marked `RENDERED:` holds, and it is not a **snippet**: no
> verbatim test applies to it, which is why the page check skips such a row rather than failing it.
> The marker is the audit claim that a page was rendered and read, and that claim is what licenses
> the cell.
> _Avoid_: snippet, quote, paraphrase, reconstruction

**This is the ruling the other four fall out of.** The reason the page check skips a marked row stops
being an assertion and becomes a consequence of what the cell *is*; the reason a marked row passing
that check is uninterpretable is that a transcription passing is a coincidence of layout; and the
reason the printed count was never an extraction measurement is that it counts transcriptions, which
are made by hand for whatever reason.

### Rejected: widen **Snippet** from *verbatim* to *faithful*

*Verbatim* is load-bearing across four sheets and the whole citation ladder rests on it. Weakening
the term that makes a fabricated citation detectable, in order to describe cells already exempt from
the check that uses it, trades the strong property for the convenience of one column.

## Ruling 3 — no gate detects a marked row that would have passed the page check

The ticket's decision 2 asks for one. Under ruling 1 it detects no defect, and under ruling 2 what it
measures is whether a drafter joined cells with semicolons or read a line straight across. **A figure
whose movement has no interpretation is not worth printing** — `guidelines_recs`'s bound-of-one, *a
true statement about markers and a poor description of the document*.

What replaces it is a sentence in `reference/thresholds/README.md` saying plainly that a marked row
may extract cleanly and that this is not a defect. **Declare the coverage rather than widen the
instrument**, which is [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s
ruling arriving at a marker.

### Rejected: report it as a tier-2 coverage figure

Tier 2's blind spot on a sheet is every skipped row, because a skipped row is skipped whether or not
it would have passed. Printing the counterfactual beside the real number is how a reader learns to
read the smaller one.

### Rejected: report it as a drafting hint, so a drafter can drop the marker and gain page grading

It rewards a drafter for **not** doing the read, since dropping the marker is what buys the grading.
#296 put the read first deliberately.

## Ruling 4 — the skip notes stay conditional, and [ADR 0035](0035-a-none-topic-is-a-null-threshold-sheet-and-the-state-is-derived-from-its-span-table.md) ruling 5 does not transfer

Two sweeps read ruling 5 as a settled precedent for printing the qualifier on every run. **The
analogy breaks on what the silence stands for.** There, `none 0` printing nothing stood for *nothing
was checked about `none`*, and the reader could not tell an absent claim from a zero one. Here
`rendered == 0` is a parse result over every row: no row carried the marker, so the bare count above
it genuinely is over all of them and the stronger claim a reader takes from the absence is **true**.

Ruling 5's own wording is careful about exactly this — it argues from *"a categorical difference a
reader seeing `sheet 1 / none 2` cannot otherwise infer."* There is no such difference here; `0` and
silence carry identical information.

**Ruling the two the same because they look the same is what would be the accident.** `block_scan`'s
boundary lesson: the safe direction of a rule is a property of the rule and not of the pair it
belongs to.

## Ruling 5 — the tier-0 counter is deliberately per-graded-source, and a tripwire holds the case that would break it

Tier 0 grades a row against its recommendation record. An ungraded source has no record, so **no** row
of it is graded — marker or not. Printing a marker skip beside `NOT RUN` would attribute the
non-coverage to the marker when the source caused it, and would report the same rows as uncovered
twice under two headings. The scope is right and the code does not change.

**What it does have is a latent denominator hazard.** The day a sheet carries one graded and one
ungraded source with markers on both, tier 0 prints a subset of the sheet's markers with nothing
naming the remainder, three lines from the sheet-wide figures the other two gates print. Two numbers
under one marker name, differing silently — the extractor-coverage rule's own shape, *a matcher never
gets to turn a partial read into a clean whole*. `prediabetes-type-2-diabetes-screening.md` already
carries two sources, so the case is reachable rather than hypothetical.

So the scope is declared at the counter **and** a test asserts no committed sheet mixes a graded and
an ungraded source while carrying markers, with the message telling whoever trips it to re-examine
the line. `differential_scan.NOT_VALIDATED_AGAINST`'s arrangement, which has collected here before —
its row-1 tripwire fired on its own words the day `fixtures/slot-form-run` was committed, rather than
a reader noticing.

### Rejected: give the line a denominator now

It writes a figure into a line that has never printed and cannot print on any committed sheet, so
nothing in the tree drives it. That is the positive-control problem, and a limit that schedules its
own review is cheaper and fires on the day the hazard becomes real.

### Rejected: a comment alone

[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) both ruled that a prose edit
to a limit fails nothing and goes stale in the direction nobody notices.

## Ruling 6 — the format sheet names both routes to the marker, and no marker is added to any row

`reference/thresholds/README.md:541` describes only a **reactive** route: gate 4 refuses, an agent
renders the page, and records the check. The measurement says **all 36 markers in the tree came from a
prophylactic route instead** — a drafter hand-reassembling a table said so on the way past, with no
gate having demanded anything. The documented procedure has never been walked.

Both are legitimate under ruling 1, because each asserts a page was rendered and read. The sheet
names both, and says the prophylactic one is the ordinary case.

**No marker is added anywhere, and the asymmetry is recorded as unrecoverable rather than tidied.**
`089a`, `089b` and `142` are reassembled like their marked neighbors and carry none. Under ruling 1
they arguably should — but nothing establishes that anyone rendered those pages *for those rows*, and
adding an unsubstantiated marker fabricates the audit claim #296 exists to make trustworthy.

**A consequence worth stating, because it is the last nail in the denominator reading:** the count
will drift **up** on future sheets, not down. A drafter following this ruling marks every
hand-reassembled row, where `diabetes.md`'s marked some.

### Rejected: reactive only, with the 36 grandfathered

A rule written against its entire evidence base, and it leaves a drafter reassembling `Table 16.1`
with no way to record the read most worth recording.

### Rejected: prophylactic only

Gate 4 refusing is exactly when a read is most needed. Its zero here is a fact about ADA's
typesetting, not about the gate.

## What the build reads

Nothing in `diabetes.md` changes. No gate is built. No skip note changes.

- `CONTEXT.md` — **Page transcription**, ruling 2's clause verbatim, filed against **Snippet**.
- `reference/thresholds/README.md:387` — drop *"because extraction garbles that table"*; the marker
  declares a page transcription and records the read, whatever prompted it.
- `reference/thresholds/README.md:541` — name both routes; the prophylactic one is ordinary.
- `reference/thresholds/README.md` — a marked row may extract cleanly, and that is not a defect.
- `CLAUDE.md:1347` — drop *"nothing detecting that a row needed it"*; need was never the criterion.
- `tools/threshold_sheet.py:1171` — declare the per-graded-source scope.
- A tripwire for ruling 5's mixed-source case.
- A `tools/test_ruling_cohort.py`-shaped test binding this record, both README paragraphs and the
  `CONTEXT.md` term, because every item above except the tripwire is prose and *a policy with no
  runnable test is one a tidy can delete without failing anything*.

**That last test is not optional here.** This record's central claim is that a marker on a
machine-clean row is correct, which is precisely the thing a future tidy will try to "fix."

## What stays a reading

Whether a page transcription is *faithful* — whether the drafter's reassembly says what the typeset
page says — is not reachable by any gate here and is not made reachable by this record. The marker
asserts the read happened. **A clean scan is still not a checked transcription.**
