# A stated expiry is read off the document and a publication cadence is not one

[#498](https://github.com/mshamblin5150-code/clinical-skills/issues/498) was filed over two
records in one `discussion-reply` claim ledger, both reading `RECENCY: current`, both graded
clean by `tools/research_ledger.py` at exit 0, and both citing a document that says on its own
face when it stops being current.

Grilled 2026-08-26. **Ten decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## The ticket's two instances are two different things, and its own prohibition says so

The body's *What must not come out of this* opens **do not infer an expiry a source does not
state**. Measured against that, the two instances part company.

| | what the document prints | where the expiry comes from |
| --- | --- | --- |
| `W. Va. Code R. § 19-7` | `termination date: August 01, 2034`, on the cover sheet | the page |
| `42 C.F.R. § 414.56 (2025)` | a codification stamp, the day the annual snapshot was taken | the reader, who knows Title 42 recodifies each October |

The C.F.R. artifact states no expiry. `DATE` and `ORIGINALDATE` in the govinfo XML are an
*as-of* stamp; the replacement date is a fact about the publisher that a reader supplies. The
ticket gives this away twice in its own sentences — *"has a **known** replacement date"* and
*"no 2026 edition exists **yet**"*. So the ticket's first instance is the thing its own
prohibition refuses, and the second is transcription.

**This moves the number the ticket was filed on.** *"Two of five records in one run, which is a
higher rate than I would have guessed"* is the stated reason it was filed rather than shrugged
at. Under this ruling it is one of five in that run and one of nine across the tree.

## Measured before ruling, at `87526a5`

- **Every claim ledger in the tree is 9 records across 2 runs** — `nur5042-m2-discussion` 5,
  `nur5144-m1-discussion` 4. Legal-shaped references: 2, both in the first run; the second has
  none. Counts only; the ledgers live under `scratch/` and no record text was read or is
  restated here.
- `RECENCY_VALUES` holds exactly the four dispositions and `FIELD` names exactly eight fields,
  verbatim as the ticket describes.
- **`TheSkillSaysWhatThisChecks` binds `research_ledger` to one skill file.**
  `skills/discussion-post/SKILL.md` and `skills/discussion-reply/SKILL.md` publish the same
  nine-line field block a run copies, and no test compares either against
  `REQUIRED_WHEN_SOURCED`, `RECENCY_VALUES`, `SOURCE_CLASSES` or `REFUTATION_VALUES`.
- `checks_ledger.EXPECTED_CHECKS` is `practicum-case-study` step 9 and nothing else. **Neither
  discussion skill has a check ledger at all**, and both of this ticket's live instances came
  from a `discussion-reply` run.
- `research_ledger.py` holds **no declared-limits object**; its limits are prose.
- The test fixtures descend from one `CLEAN` constant in `tools/test_research_ledger.py`, plus a
  handful of literal records in the two discussion scan test modules and three skill templates.

## The ruling

**1. Two kinds, and only the stated sunset is in scope.** A stated expiry is a date the document
prints about itself. A publication cadence is a schedule the reader knows, and folding it into
the same field makes the field carry an inference — `#215`'s defect, which this ticket's own
prohibition exists to refuse and which that ticket has already produced three times.

The cadence half is not dismissed, it is **separated and filed** (ruling 10). It also does not
narrow to a safe case on inspection: `42 C.F.R.` recodifying each October is true until the OFR
or Congress changes it, so the "sourced inference" is itself unversioned and has no expiry of
its own.

**2. It is recorded *and* graded, and the ticket's argument against grading is backwards.**
Bullet 3 declines a row on the ground that *"a row firing on a future date is a row that fires
on correct records for years before it matters."* A row reading *this record's stated expiry is
at or before the ledger's `DATE:`* is **silent** every day until the stated date and fires on
the day after it, correctly, on a record that has quietly become wrong. It cannot false-alarm,
because after ruling 1 every value in the field is a string transcribed off a cover sheet and
there is no judgment left for the row to get wrong.

**It is the only row in this module that accrues rather than decays.** `STALE_UNEXCUSED`,
`READ_AFTER_DATE` and the five-year window all get less informative as a ledger ages; this one
gets more. That answers the ticket's own *"nothing decays, there is no signal"* at the root: a
transcribed sunset **is** the signal, and it arrives on schedule with no network and no reread.

**3. A mandatory ninth field with an explicit sentinel, because an optional one leaves the filed
defect exactly where it is.** Every sourced record answers the question: a date and where the
document states it, or `none stated`. Omission is `MISSING_FIELD` — the existing row, no new
machinery, and an eighth entry in `REQUIRED_WHEN_SOURCED`.

The sentinel is ADR 0027 ruling 6's move, one artifact over: `not stated` absorbed the excluded
rows there **so that an absence would be legible rather than silent**, and the artifact header
disclosed the exclusion by name.

**4. A ledger carrying the field nowhere is exit 2, and `none stated` counts as carrying it.**
The discriminator is per ledger, not per record: some records carrying it and one not is a
genuine `MISSING_FIELD`; none carrying it anywhere is a ledger written before the question
existed. That is `differential_scan.py`'s retired-refusal-form limb, one module over, and it
joins `research_ledger.py`'s existing not-scanned family — no argument, no file, no `## CLAIM:`
record, no `DATE:` header. Existing ordering holds: where a finding and a not-scanned limb both
hold, **1 wins**, with the banner beside it so the finding reads as a floor.

**It is not an escape hatch**, which is the objection to reach for first. A new run whose agent
never writes the field anywhere gets exit 2 rather than exit 1 — still refused, still non-zero,
and with a message more accurate about what went wrong than one field missing repeated five
times.

Backfilling `none stated` into the two ledgers already in the tree was declined: a run record is
evidence, and editing one to satisfy a later rule is the repair `fixtures/filled-anchor` refuses
in as many words. A grandfather keyed on the `DATE:` header was declined too — that is a rule
about the calendar rather than about the document, and it re-opens silently the moment somebody
writes an old date into a new ledger.

**5. Three dispositions, and the escape hatch carries a reason.**

```text
STATED-EXPIRY: none stated
STATED-EXPIRY: <ISO date> - <where the document states it>
STATED-EXPIRY: <ISO date>, superseded cited deliberately - <reason>
```

The third exists because **the row as specified refuses a correct record**: a policy-history or
timeline claim cites a superseded rule *on purpose*, and its expiry being past is the point of
the citation rather than a defect in it. That is `#215`'s own shape — a bare age rule cutting a
correct 2018 refutation — and the repair is `#215`'s own: not to drop the rule but to give it a
stated escape, *the run must have looked, and must say so*. An unrecognized disposition is a
failure on `STATUS`'s reasoning, because it gates the row below it.

The value's grammar is `PAGE-YEAR`'s — a transcription plus its provenance, so a reader checks
it in one jump.

**The comparison is against the ledger's `DATE:` header and never the clock**, so a ledger
graded twice a year apart grades the same both times; a dateless ledger loses this row the way
it already loses two others. **A date equal to `DATE:` fires.** W. Va.'s cover sheet says the
rule terminates *on* a date without saying whether it is in force through that day, so the
ambiguity is one day wide on an eight-year window and the ruling fails toward *expired*,
declared here rather than left to be found.

**6. The field is `STATED-EXPIRY`, and the name does ruling 1's work.** The failure to design
against is a research agent looking at the C.F.R. entry, knowing Title 42 recodifies each
October, and writing that date into the field. A bare `EXPIRES` invites it. `PAGE-YEAR` is the
precedent worth copying: its own name says the year comes from **the page** rather than from the
reference, which is why that field is hard to fill wrong. The one ruling most likely to be
forgotten goes into the one place every author of a record has to look.

`SUNSET` was declined as jargon and as wrong for any non-legal source that prints a validity
date; `TERMINATES` as a verb breaking the field pattern.

**`CONTEXT.md` gains one term**, `Stated expiry`, carrying the exclusion inside its own
definition. A second term for the kind this repo deliberately does not model was declined:
`CONTEXT.md` is a glossary of terms **in use**, and naming a ruled-out kind sends the next
reader looking for where it is handled.

**7. Two report lines, both on every run.**

```text
stated expiry                     <n> of <m> sourced records name a date
superseded cited deliberately     <n>
```

*Done when* asks for the first count alone, and a numerator with no denominator reads as
coverage — `#258`, and a shape this module has already been corrected on once, when
`evidence topics carried` had to be printed beside `UpToDate citations read`. The second line is
`REFUTATION_PAYWALLED`'s arrangement in this same module and for its reason: it is the weakest
disposition that passes, and a run resting on it should not read as a run whose sources are all
live. Both print whether or not they fire, on `#258`'s ruling.

A third `none stated` line was declined as always reconciling, and a row a reader stops checking
is worse than no row.

The counts stay in the **default** report — they are integers — and the finding details stay
behind `--show` with no carve-out. `reference_scan.py` is this directory's one `--show`
exception and it was earned by measurement rather than by argument.

**The docstring's *"Two rows need that date since #231, not one"* becomes three** in the same
change, rather than being left to a sweep.

**8. The vocabulary binds widen to every skill that publishes a ledger template, with the
population derived.** Adding the field fails the practicum bind automatically, because that
class loops the tuple, and would leave the two discussion templates publishing an eight-field
block against a nine-field parser **silently** — every run of those two skills then failing
`MISSING_FIELD` on every record, for a field its own instructions never mention. That is
`#220`'s two copies of a rule, with three copies, and it is live in the tree today rather than
created by this change.

The population is **derived** — the skill files whose text carries a `## CLAIM:` block — rather
than hand-listed, so a fourth skill that starts writing ledgers is covered on arrival.
Hand-listing is the matcher that turns a partial read into a clean whole,
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137).

**`ROW_PHRASES` deliberately does not widen.** Writing out every row is `practicum-case-study`
step 9's defect table, and requiring a discussion skill to carry it would be inventing a rule
nobody made.

This fixes a defect #498 did not file, and that was weighed against `#434`'s warning that two
evidence bars in one commit is how the weaker one rides in on the stronger one's credibility.
Here they are one bar: the widening is not a separate improvement, it is what stops this change
breaking two skills.

**9. The sentinel's unfalsifiability is R2 inherited, declared in prose beside the row.**
`none stated` written by an agent that never opened the cover sheet is indistinguishable from
one that looked. No version of this closes it.

**A reader row was declined on a measurement rather than on cost.** `#255` and `#299`'s
`SUBSTANTIATED_CLEAN` requires a `clean` to say what it walked on, and it lives in
`checks_ledger.EXPECTED_CHECKS`, which is `practicum-case-study` step 9 and nothing else. Both
of this ticket's live instances came from a `discussion-reply` run, and that skill has no check
ledger. **A reader row would be built in the one skill where this has never happened and absent
from the one where it did.**

And it is not a new limit. `BARE_STATUS`, `BARE_EXCUSE` and `BARE_REFUTATION` all sit on exactly
this — `specificity_scan.py`'s R2, *the reason is the evidence the check happened* — so the
sentinel inherits a class limit already declared across this directory rather than opening one.

**A `research_ledger.NOT_REACHED` object was declined as this change and filed as its own.** The
module has no such object and five limits in prose: the numbers are never compared,
`UNRESOLVABLE_LOCATOR`'s DOI shape, `DOSE_NOT_CLAIMED` asking for *a* number rather than *the*
number, no expected count of records, and now this. Introducing the object with one row while
five stay in prose is ruling 7's numerator-without-denominator one level up — it would read as
*these are the limits*.

**10. The publication-cadence case is filed rather than buried.** Recording it only as a
rejected alternative here leaves it in a record nobody greps, and the next session re-derives it
as a fresh finding — which is the shape #498's own third comment was written to prevent. It is a
real property of a real citation in a real run, and
[#497](https://github.com/mshamblin5150-code/clinical-skills/issues/497)'s
[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
ruling 6 has independently declared that **a legal citation's year is checked against its
entry's year by nothing, anywhere in the tree**, before or after that work — so the cadence case
sits beside a second blind spot on the same citation.

## The two rejected contracts

Recorded because a future reader will reach for both, and neither is refuted by anything in the
tree unless it is written down here.

### A fifth `RECENCY` value

The ticket's own first bullet — *something like `expires <ISO date> - <reason>`, which keeps one
field and makes the vocabulary two-directional*. The #434 sweep argued against it from ADR 0027
ruling 1 by analogy, *a column answers one question*. **It dies mechanically, which is
stronger.**

`_recency_findings` splits the field once with `keyword_of(recency, RECENCY_VALUES)`, and
`STALE_UNEXCUSED` reads that same split. So a fifth value has to be in `EXCUSES` or not, and
both are wrong:

- **In `EXCUSES`** it stands the five-year window down. A 1990 rule with a 2034 termination date
  is thirty-six years old *and* in force, and the record would have no way left to say the first
  thing.
- **Not in `EXCUSES`** the window fires, and the record needs a second recency claim with
  nowhere to put it.

The field answers one question honestly today. A sunset is a different question.

### An optional field

The obvious cheap shape, and it **changes nothing about the failure that generated this
ticket**. The W. Va. record was written by an agent that did not think to open the cover sheet.
Give it an optional `STATED-EXPIRY:` and that same agent writes the same record, omits the same
field, and `research_ledger.py` exits 0 exactly as it did — with a field standing beside it that
makes the ledger *look* covered.

The variant that rescues it — an optional field plus an independent classifier over `REFERENCE`,
flagging records that cite a class of source which *ought* to publish a sunset — is refused by
ruling 1. Deciding which sources ought to have one is inferring one, and it fires on correct
records.

## What this costs, stated rather than implied

**Every claim ledger written before this exits 2 rather than grading**, and that is the intended
behavior rather than a side effect. Two ledgers in the tree today; both are historical run
records and neither is edited.

**A legitimate ledger in which no source states a sunset, and every record honestly reads
`none stated`, is not the exit-2 case** — the sentinel counts as carrying the field. That
distinction is the whole difference between the sentinel doing its job and being a no-op, and it
is the first thing to check in the implementation.

**The contract is now written in five places** — the field block in three skill templates,
`research_ledger.py`'s docstring, and this record. This tree has recorded a prose copy going
stale in the direction nobody notices more often than any other failure it has. What justifies
the count is ruling 8: the three templates are **bound to the module by a derived test**, so
four of the five cannot drift silently. This record is the fifth and is the only one carrying
the rejected contracts.

**The tripwire this ruling does not have.** ADR 0027 ruling 5 required a check walking a pattern
*independent of the vocabulary*, because a check keyed only on what the vocabulary can see
cannot find the thing it is named for. Ruling 3 answers that requirement structurally rather
than with a second pattern: the field is mandatory, so a record that never asked the question
fails `MISSING_FIELD` without any classifier having to guess which sources ought to carry one.
That is the *only* independent instrument available after ruling 1, and its cost is ruling 9's
R2 residue.
