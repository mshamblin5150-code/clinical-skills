# A measurement instrument becomes a `tools/` module when its question reopens

[#404](https://github.com/mshamblin5150-code/clinical-skills/issues/404) was filed
about one false sentence in `CLAUDE.md`. Grilling it on 2026-08-23 found that this
repo had ruled on the disposition of a measurement script **three times with no
general rule written down**, and that the third ruling was argued from a fabricated
account of the first two.

#404's body asserts *"this repo has ruled twice that a one-off measurement stays
out."* There are **zero** such rulings. `reader_compare.py`'s docstring is a script
describing itself; [#178](https://github.com/mshamblin5150-code/clinical-skills/issues/178)
records placement as a fact and rules nothing. The record is 0–2 the other way:
[#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388) decision 1
ruled a throwaway extractor into `tools/voice_corpus.py` *over its own no-move
argument, stated in #404's exact terms*, and [ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md)
rejected the no-move branch using a figure — *all seven scripts together are 48 KB* —
that already covered the six scripts #404 is about.

**An ADR is what stops the fourth ruling being argued from an invented account of
the third.** Three instances is thin for a general rule; the third instance being
fabricated is what makes the rule necessary rather than premature.

The clinician ruled, 2026-08-23:

1. **The disposition test is: does the question the instrument answers go live again
   when the rule or the corpus moves?** If it does, the instrument becomes a `tools/`
   module. If it does not, it is deleted — not preserved.
2. **Owning a published figure is a *separate* test, asked separately.** An
   instrument may fail the first test and still own a figure the repo publishes.
   That does not rescue the instrument; it obliges the figure.
3. **A figure whose producer is deleted becomes an orphaned figure**, and takes the
   declared-limit treatment — one named object, `CLAUDE.md` pointing at it and
   copying no row.
4. **A moved instrument may not hold its own copy of the rule it measures.** The rule
   is extracted so both the production path and the instrument consume one
   implementation.

## What was measured

Every claim below was re-derived on the merged tree before the ruling.

**The scripts run, and that is worse than not running.** All four import cleanly and
two workers execute against a corpus PDF. `split_shapes.py` and `true_split.py`
reimplement the pre-#178 single-bar gap rule, so they print a confident table under
a rule this repo retired, with nothing in the output saying so. That is
[#403](https://github.com/mshamblin5150-code/clinical-skills/issues/403)'s live-hazard
finding one level over — there the generator silently regressed a committed sheet,
here the instrument silently measures a superseded rule.

**Two rows of the published table re-derive and three do not.** 13,685 occurrences
over 10,731 distinct shapes re-derive exactly from `split-shapes.json`; the
`digit-break` 390 re-derives from 135 shapes in `digit-context.json` summed against
it. `9,622 / 3,179 / 306 / 188` re-derive from nothing — their producer really was
never saved. `tools/guidelines_extract.py` already stated that exact partition and
was the only correct copy in the repo.

**The safety claim read under 7% of its own population.** `split_shapes.py` marks a
split as a digit-break only where a piece ends in a digit and the next begins with
one — 390 occurrences, against 5,755 digit-adjacent boundaries corpus-wide.
`digit|digit` is the shape a year, a page range and a reference marker take, which is
why the conclusion came back *every distinct run was citation apparatus*: **the
matcher could not have found anything else.** 362 boundaries sit next to a decimal
point or comma against a digit, which is the shape a dose breaks in, and that class
was never examined.

## Considered options

**Leave all six outside and repair the sentence** — #404's own recommendation.
Rejected because the sentence it proposed is also false: after this ruling
`split_census.py` re-derives three of the figures from this tree. More importantly it
leaves the hazard standing — the next session finds the scripts, runs them, and
publishes a pre-#178 measurement as current, which is exactly how this ticket was
generated.

**Move all six.** Rejected. `reader_compare.py` and `split_measure.py` argue a closed
decision — which PDF reader — and `threshold_sweep.py` and `adaptive_test.py` cannot
sweep #178's second bar, so as instruments they are already *wrong* rather than
merely dated. Moving one puts a tool in `tools/` that cannot answer the question it
is named for.

**Delete all six and let the figures go with them**, on
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) option 5.
Rejected, and the precedent misreads itself: option 5 was applied to figures nothing
rested on — a directory size, a worktree count — whereas `CLAUDE.md` says of this
argument that *the conclusion drawn from it was wrong, which is worth keeping visible
rather than quietly deleting.* Delete the figures and the argument stops being
checkable.

**Commit `reader-compare.json`** — 60 KB of per-document counts, no guideline text —
so the reader table stays re-derivable from a committed artifact. The most tempting
option, and rejected because committing a file out of the gitignored build directory
is precisely what [#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176)
and [#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223)'s net
exists to stop; `TheNetDoesNotSwallowWhatIsCommitted` would need a carve-out for it.

**Keep the lexicon cache with a provenance stamp**, on #184's arrangement. Rejected:
`true_split.py` caches a 444 KB lexicon and reloads it *if present, without checking
what rule built it*, and that artifact is on disk today built under the retired rule.
Building the #184 apparatus in miniature to save one corpus pass on a command run
once per refresh is instrumenting the hazard rather than removing it. The lexicon is
rebuilt every run and nothing is written.

## The cost this accepts

**Three of the five bucket rows are permanently unrepeatable.** The rewrite carries
#178's second bar and #172's operator repair, so its output is a *different* table
rather than a re-derivation — and the extractor already records that reasonable
bucket rules put `letter-spaced word` anywhere from 128 to 466. Republishing them off
a rewritten classifier would repeat #83's recorded failure of publishing a table from
an instrument that had moved. They stay declared rather than re-measured.

**The extractor's hot path is refactored to serve an instrument.** `rebuild_text`'s
per-line walk becomes a generator both it and the census consume. That is a real risk
to the function every guideline figure rests on, accepted because the alternative —
a second implementation pinned by a test — is the arrangement this repo has already
ruled against: *a second mechanism that cannot fail is not a belt and braces; it is a
line that costs a test.* The precedent is `docx_write.render_body` → `docx_write.blocks`,
**including its verification method**: compare output across the whole population
rather than reading the diff.

**The safety judgment is narrower than the safety count.** All five boundary classes
are counted so the denominator is on the page; the judgment covers the 752
quantity-shaped occurrences. `alpha|digit` and `digit|alpha` are dominated by correct
fixes — `5mg` → `5 mg` — so judging them drowns the signal. That is
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s *declare
the coverage rather than widen the instrument*, and it means a clinical unit broken
in an unjudged class is still reachable by nothing but a reader.
