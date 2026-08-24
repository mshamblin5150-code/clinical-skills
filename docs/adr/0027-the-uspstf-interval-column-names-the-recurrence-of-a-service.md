# The uspstf interval column names the recurrence of a service

[#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434) was filed over one
cell — `rhrs.pdf` deriving an interval of `repeated`, a word naming no period — and asks
three questions that all turn out to hang off one nobody had asked: what the column is a
column of.

Grilled 2026-08-24. **Seven decisions, ruled by the clinician on that date.** Nothing is
built here; this is the record the build reads.

## Two contracts were already live and they disagree

`tools/uspstf_table.py`'s module docstring calls the column *"often a screening interval"*.
The artifact header at `reference/guidelines-uspstf.md:5` — written deliberately by
[#432](https://github.com/mshamblin5150-code/clinical-skills/issues/432), days earlier —
says *"`interval` names every period its statement names"*. Those are different columns, and
the tree contained rows that are correct under one and wrong under the other with nothing
recording which was meant.

`interval` appeared in no glossary. It does now, beside `Decision point`, which had already
drawn the distinction the whole ruling rests on: *"a dose, a period, a cutoff, or a target"*.

## The ticket's own measurement was wrong in two directions

**`repeated` is not the only cell naming no period.** `periodic` names none either — it
asserts regular recurrence without saying how often. #434 lists it among the eleven
neighbors it clears, citing #432 as having checked it; #432 checked whether the cell
faithfully repeats its statement, which it does, and that is a different test.

**Four cells name a real period belonging to something that is not a service.** All four
`daily` rows are a drug or supplement dose frequency:

| row | what `daily` modifies |
| --- | --- |
| `aspirin-use-cvd-prevention-final-rec`, C | *willing to take low-dose aspirin **daily*** |
| `folic-acid-supplementation-final-rec-statement`, A | *take a **daily** supplement containing 0.4 to 0.8 mg* |
| `vitamind-calcium-fracture-prevention-final-rec-statement`, D | *against **daily** supplementation with 400 IU or less* |
| `vitamind-calcium-fracture-prevention-final-rec-statement`, I | *__daily__ supplementation with doses greater than 400 IU* |

A reader taking `annual` on the lung row as *re-image in a year* and `daily` on the folic
acid row as the same kind of fact has been misled, and that is four instances against
`repeated`'s one. **So the ruling inverts the ticket**: the cell it was filed over is kept,
and cells it never named are what move.

## The ruling

**1. The column answers *how often does the recommended service recur*.** Not *every period
the statement names*, which is the shipped header's claim and is what admits a dose. Not
*the frequency of the recommended action whatever form it takes*, which keeps all twelve
cells and closes the ticket as a no-change.

The two rejected contracts are recorded because the first is the one a future reader will
reach for: it is mechanical, judgment-free, and the rule a lexical vocabulary naturally
implies. Under it `repeated`, `periodic`, `1-time` and `at least once` all come out and the
four `daily` stay — the exact inverse of this ruling, arrived at honestly. **Anyone
restoring it should know it was weighed, and what it costs.**

**2. It is enforced by choosing the vocabulary, not by reading each derivation.**
`\bdaily\b` leaves `INTERVAL_PHRASE`. A preventive *service* that recurs is measured in
months and years; a thing done daily in a USPSTF statement is a dose. The list stops being
*phrases naming a period* and becomes *phrases naming the recurrence of a service* — the
reading happens once, when the list is chosen, which is what a closed vocabulary is for.

Gating `daily` on what it modifies was declined: there is no daily service in this corpus,
so the gate protects nothing and can only ever fire wrong, which is `SPACE_ADVANCE_FRACTION`
named at an edge and `case_study_scan`'s `ENDPOINT` failing correct orders, both already
recorded in this tree.

Classifying the service per row — screening against medication against counseling — is the
honest form of the contract and is **a different ticket**. It invents a column,
reclassifies 143 rows, and
[#435](https://github.com/mshamblin5150-code/clinical-skills/issues/435) already owns
widening this derivation. #434's own body warns that two evidence bars in one commit is how
the weaker one rides in on the stronger one's credibility.

**3. The argument holds at the day scale and nowhere finer, and that ceiling is declared
rather than left to be found.** `every 2 weeks` or `every 3 months` is a dose frequency for
a long-acting injectable exactly as `daily` is for a tablet, and the vocabulary admits both
patterns today with nothing firing on them. So this ruling buys a correct table now and
carries a known reopening condition, which is what rulings 4 and 5 below exist for.

**4. The reason is held by an object and a tripwire, because prose fails nothing.** A
declared exclusion beside `INTERVAL_PHRASE` naming what is deliberately outside it and why,
a test asserting each named phrase is genuinely unmatched, and a check that **fails when a
sub-yearly period reaches a committed statement** — telling the next reader the granularity
argument no longer decides the case.

A docstring alone is the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) have already ruled
insufficient and [ADR 0020](0020-a-count-inside-a-declared-limit-is-derived-or-dropped-and-the-check-walks-constants-rather-than-prose.md)
states as *the check walks constants rather than prose*. Here the failure is concrete:
`daily` is a common enough word that the next person to read the vocabulary will notice it
missing and put it back, and nothing would go red.

**5. The tripwire walks any sub-yearly period, on a pattern independent of the vocabulary.**
Not only what `INTERVAL_PHRASE` can see. Under the narrower reading a statement saying
`twice weekly` is invisible to the tripwire *and* to the derivation at once, so the column
reads `not stated`, the suite stays green, and this ruling goes untested against the one
corpus change that would falsify it — a check that could not have found the thing it is
named for.

**The price is named rather than discovered**: a genuine `monthly` self-examination
recommendation will turn the suite red for a row nobody needs to change, and whoever
refreshes the corpus pays for a review they did not cause.

**6. `not stated` absorbs the four rows, and the header discloses the exclusion by name.**
That sentinel now carries three distinct situations — the statement is silent, the statement
is silent *in this sentence* (#435's subject), and the statement names a period that is a
dose. The header is the only place a consumer meets this column, so it says that a dose or
supplement frequency is not a recurrence and is deliberately outside the column.

A distinct sentinel for the four was declined on a measurement: after the change **all 43
non-screening rows read `not stated` uniformly**, the four joining 39 that already did.
Telling them apart requires the service classification deferred in ruling 2, and marking
only the four would separate them from 39 rows identical in kind.

Nothing is lost from the file. `## Statements` carries every statement verbatim, so *daily
supplement containing 0.4 to 0.8 mg* stays in the row where a dose belongs.

**7. `repeated`, `periodic`, `1-time` and `at least once` are all kept, as one class.** Each
answers *how often does this recur* in the right currency — `repeated` and `periodic` assert
recurrence without naming a period, `1-time` and `at least once` name a count. #434's
decision 2 asks whether the last two travel with the first; under this contract they are the
same class and need no separate ruling.

## What this costs, stated rather than implied

The contract is now written in four places — the artifact header, `derive_interval`'s
docstring, the declared exclusion object, and `CONTEXT.md` — and this record is a fifth.
This tree has recorded a prose copy going stale in the direction nobody notices more often
than any other failure it has. **What justifies the fifth is that it is the only one
carrying the rejected alternatives**; the other four state what the column is and none
records that the mechanical contract was considered. This record states the contract only as
far as it must to make those alternatives legible.

## Measured before ruling, at `16011c5`

- 143 rows, 12 carrying a derived interval; 8 after the change.
- The rebuild is **content-identical** to the committed artifact today — 323 lines, zero
  hunks — so the diff will be exactly the ruled cells. `core.autocrlf=true` over an LF
  index, so the builder's LF output normalizes clean.
- The tripwire is **zero** on the current corpus under both candidate patterns.
- The vocabulary exists **twice**: `tools/uspstf_table.py` and the deliberate independent
  copy in `tools/test_uspstf_derived_cells.py` that #432 added and justified. That is not a
  #220 hazard — the test joins against the committed artifact, so every mutation direction
  fails loudly — but both move together or the suite goes red for the right reason at the
  wrong moment.
