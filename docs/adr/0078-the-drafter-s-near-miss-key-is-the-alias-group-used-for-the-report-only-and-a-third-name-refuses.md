# The drafter's near-miss key is the alias group, used for the report only, and a third name refuses

[#648](https://github.com/mshamblin5150-code/clinical-skills/issues/648) was filed out of
[ADR 0064](0064-a-threshold-sheet-s-sources-are-not-joined-to-its-topic-because-the-catalog-cell-is-the-guideline-s-wording.md)
ruling 3, which left the mechanism unruled: `tools/threshold_draft.py`'s near-miss report is keyed on
the string the author typed, so which sibling documents surface depends on which of a subject's names
was used. Grilled 2026-08-30 against `origin/main` at `7e22a19`. **Seven decisions, all the
clinician's, all on that date.** Nothing is built here; this is the record the build reads.

**`main` advanced three times mid-grilling -- to `bb0d223`, `7699af0` and `36ae148` -- and every
figure below was re-derived at each.** `tools/threshold_draft.py`, `reference/guidelines-catalog.md`,
`reference/thresholds/` and ADR 0064 were untouched by all three and all four measurements reproduce
identically. What those merges did change is two things decided here and not by the ticket: a premise,
recorded under *What was closed rather than decided*, and ruling 6, which
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
made askable by landing.

The ticket poses three decisions. The measurement retires the middle option of the first outright,
two rulings here are forks that ship green either way and had to be asked because of that, two more
were forced by `main` moving under the grilling, and the ticket's third decision is closed as already
ruled.

## Measured before ruling, at `7e22a19`, corpus-free

**A word-overlap key over catalog topic cells cannot reach the document the ticket was filed over,
at any threshold.** The USPSTF adult statement's catalog row carries
`topic = 'hypertension screening'`, `title = 'Screening for Hypertension in Adults: US Preventive
Services Task Force Reaffirmation Recommendation Statement'` and
`filename = 'hypertension-screening-adults-final-rec-statement.pdf'`. **The string `blood pressure`
appears nowhere in it.** `reference/thresholds/hypertension.md` is registered under `high blood
pressure`, so the name the sheet is actually drafted under shares **zero** significant words with its
most likely second source. No cut point above zero surfaces it.

**And at zero the report is noise.** Reporting every catalog row sharing one significant word with the
seeded row's topic gives `cervical cancer screening` 16 near-misses — every cancer in the catalog —
and `chronic obstructive pulmonary disease` **34**, including `Lyme disease` and `congenital heart
disease`. Over the 169 distinct topics, 1,143 topic pairs share at least one significant word and one
topic has 65 neighbours.

**So this is a synonym gap and not an overlap gap.** `hypertension` and `high blood pressure` share
no word, and nothing inferred from society-written wording bridges them. That corroborates
ADR 0064's *"a derived grouping of catalog cells"* prohibition rather than reopening it, and it means
the option was not refused on [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
ungroundable-cut-point objection alone — it fails on the ticket's own material in both directions at
once.

**The one existing alias entry, used in both directions, closes the measured table.** `TOPIC_ALIASES`
is `{"hypertension": "high blood pressure"}`, one entry, one-way. Keying the report on every name in
the group rather than on the typed one:

| drafted as | near-miss reported today | with the group as key |
| --- | --- | --- |
| `hypertension` | hypertension screening | **both** USPSTF rows |
| `high blood pressure` | high blood pressure screening | **both** USPSTF rows |
| `chronic obstructive pulmonary disease` | COPD screening | COPD screening |
| `diabetes mellitus` | — | — |

Symmetric by construction, and it changes nothing for the other three shipped sheets.

**A two-way group would not change the seed set today, and that is a coincidence of this catalog.**
No catalog row's `topic` cell is exactly `hypertension`, so the alias's left-hand side matches no row
and a one-way `_topic` and a two-way one produce the identical single-row seed for both drafting
names.

**Blast radius is zero.** `TOPIC_ALIASES` and `_topic` are private to `threshold_draft.py`; the only
reference outside it is `test_threshold_draft.py` importing the module. Neither
`tools/threshold_coverage.py` nor the 169-row registry reads either.

**The near-miss list is written into the drafted sheet, not to stderr.** `source_rejections` flows
into `render`'s `## Rejected candidates` table on stdout; only `source_errors + row_rejections` reach
the `REJECTED:` stderr lines and the exit-2 path. **`## Rejected candidates` and `## Candidate set`
are draft-only** — none of the four committed sheets carries either heading.

## What is ruled

1. **The report is keyed on every name in the drafted topic's alias group, not on the typed string.**
   The measurement leaves this as the only candidate that reaches the document the ticket names, and
   it invents no similarity judgment. **Its cost is stated rather than papered over: it reaches one
   clinical subject out of the catalog's 169 topics, and for the other 168 the key is still the name
   that was typed.** Keying on the seeded rows' own topic instead was refused — it kills typed-string
   dependence, which is the ticket's title, and leaves the ticket's worst case standing, because
   neither hypertension name reaches a row carrying no `blood pressure` string.
2. **The report states that bound unconditionally, in the draft, and the figures are derived.** A
   sentence under `## Rejected candidates` above the table, printed on every run and not only when
   the list fires, on [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
   terms and because the shape being guarded against is a one-source sheet with an empty rejected
   list reading as a complete topic join. The count of named subjects is read off `TOPIC_ALIASES` and
   the topic count off the parsed catalog rather than typed, on
   [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. **stderr was
   refused** — the author curates the draft file, not the console they walked away from — and **both
   was refused** as [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two
   editable copies of one claim. **This floor is not ADR 0064 ruling 2's sixth bullet and is not
   bound to it**: that one says no gate checks source membership, this one says this report's key is
   narrow, so this ticket does not wait on
   [#645](https://github.com/mshamblin5150-code/clinical-skills/issues/645)'s merge.
3. **The group governs the report key only. `_topic` stays one-way and canonical.** Today the two
   answers are unobservable — the seed is identical under both — which is why it is ruled rather than
   left to the build. The day a catalog refresh lands a row whose topic cell is `hypertension`, a
   two-way `_topic` seeds it beside `high blood pressure` into one sheet, which is what the
   constant's own comment forbids in as many words: *"a request for hypertension must not silently
   absorb the separate 'hypertension screening' topic."* **Pinned by a test against a synthetic
   catalog carrying such a row, asserting it is reported and not seeded** — the assertion is pointed
   at a shape the tree does not contain, on `test_skill_agreement.py`'s reasoning that asserting the
   catalog is clean today proves only that the walk found nothing.
4. **`nearby` excludes documents the seeded sheet already cites.** Ruling 1 makes the report start
   firing on correct sources: the moment `hypertension.md` gains the USPSTF adult statement — the
   exact document ruling 1 exists to surface — every later re-draft reports that accepted source back
   as a rejected candidate, forever. **The noise arrives with the fix**, since the list never fires
   for `high blood pressure` today, and a report that fires on the normal case is what ADR 0064
   ruling 1 refuses a report for. The exclusion uses the document-name match `resolve_sources`
   already makes to carry a seeded key forward. The list then means *documents this subject has that
   this sheet has not taken*, and it empties as the author accepts them, which is also what makes
   ruling 2's floor sentence true in the stronger sense — an empty list means nothing further to
   consider rather than nothing found.
5. **A third name in `TOPIC_ALIASES` refuses rather than working.** The group is derived from the
   existing one-way dict rather than from a second constant, so there is one authored object and
   nothing to drift. A one-way dict can express a three-name subject as two entries, and at today's
   single entry a transitive derivation and a pairwise one are indistinguishable. The derivation is
   **pairwise, and any name appearing in more than one pair is exit 2 naming the grouping ticket.**
   The stakes are not the arithmetic: a transitive derivation is what lets `TOPIC_ALIASES` become the
   hand-kept synonym list this repo refuses, one entry at a time, with the authored grouping never
   built — and each single addition looks like the cheapest correct move. **Pinned by a test on a
   synthetic three-name alias set**, since one real entry cannot distinguish the two.

6. **The floor sentence is a module-level constant that `render` prints, and no limits object is
   started here.**
   [ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
   ruling 3's membership criterion -- *a limit tells a reader that a clean result covers less than it
   appears to* -- is exactly what ruling 2's sentence is, so it is a declared limit in the ratified
   sense rather than incidental prose.
   [ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
   ruling 2 -- merged from #550 while this record was being written -- settles how such a sentence is
   held: *"the object does not print; every printed line the module has stays exactly where it is as
   the run-scoped face of its limit, and a row for a printed limit points at the constant that
   prints."* A constant costs one name and makes that arrangement already true; the sentence is built
   from derived figures at run time, so it is a template rather than a fixed string and wants a name
   regardless. **ADR 0074's *"more names is the disease"* does not reach it** -- that refusal was of
   per-gate sibling objects competing with one inventory inside one module, and `threshold_draft.py`
   has no inventory to compete with: `DECLARED_LIMITS`, `NOT_REACHED` and `NOT_GUARDED` are all
   absent from it. **And none is started here.** ADR 0074 is scoped to `tools/threshold_sheet.py`, no
   ticket owns this module's inventory shape, and starting one in passing is exactly what ADR 0064
   ruling 2 declined to do to #550 -- which is why #550 got to rule it properly.

## What was closed rather than decided

**#648's decision 3 — a source added to a sheet after drafting — is already ruled and nothing is
filed for it.** It is the third limb of ADR 0064's declared limit, which #645 is building as the
sixth bullet. The only mechanism that would reach it is a report keyed on the catalog topic column
against a committed sheet's sources, and ADR 0064 ruling 1 refuses exactly that on the measurement
that 160 of 169 topics own one document, so it would fire on nearly every correct second source any
sheet ever gains. **Ruling 4 is the part of that limb that is reachable**, because it is scoped to a
re-draft the author is running anyway rather than to a sheet nobody is looking at.

**The authored grouping is a separate ticket, and it is a one-party ticket — which it was not when
this grilling opened.** ADR 0064's Consequences record that *nothing in this repo derives which
catalog cells are one clinical topic* and that the honest form of such a grouping is authored and
committed. It is the prerequisite nobody owns, and building it inside a near-miss-report repair
would decide a cross-cutting artifact in passing.

**Decision 7 was forced by the merge rather than raised by the ticket.** This grilling opened with
[#584](https://github.com/mshamblin5150-code/clinical-skills/issues/584) named as the second party
needing the same artifact for a cross-sheet `CONFLICT`, which is what ADR 0064 records. **`main`
retired that premise while the record was being written**:
[ADR 0076](0076-the-cross-sheet-reading-is-a-substantiated-row-and-the-reader-derives-the-join-per-patient.md)
ruling 2 makes #584 a substantiated reader row whose grouping is *per patient, made by the reader
from the patient in front of it*, states in as many words that this *"answers ADR 0064's named
prerequisite without building it"*, and puts **a committed clinical-topic grouping built for this
row** on its own list of what must not come out of it — while leaving the artifact open for a future
mechanical gate *"on its own ticket."* **The ticket is filed anyway**, because the durable part is
the measurement above rather than the demand: it is the third recorded time this repo has priced this
join, and not filing leaves it discoverable only by reading this record. Its trigger is now exactly
one hypothetical — someone wanting a third alias name — and ruling 5 is what converts that
hypothetical into a refusal that names the ticket.

## Consequences

`TOPIC_ALIASES` stays at one entry and is now load-bearing in two directions rather than one. The
near-miss report reaches one clinical subject of 169 and says so on every run; the other 168 are as
blind as they are today, and ruling 2's sentence is the only thing standing between that and a reader
reading a short list as a checked topic join.

**Rulings 3 and 5 are both pinned against shapes the tree does not contain**, because at one alias
entry and this catalog neither fork is observable. Those two tests are the whole of what keeps the
build from being decided silently, and a later author who deletes them as testing nothing has removed
the reason they exist.

The refused grouping remains refused and remains unowned. Ruling 5 converts the day it is genuinely
needed from a keystroke into a refusal that names the ticket, which is the price being declared
rather than a defect.

## What must not come out of this

**A similarity threshold.** Not deferred — measured and dead. The document this ticket was filed over
is unreachable at every cut point above zero, and zero reports 34 near-misses for one topic. There is
no plateau to take the midpoint of, which is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection and
`SPACE_ADVANCE_FRACTION`'s recorded failure both landing on the same option.

**A gate.** ADR 0064 ruling 1 refused one and this does not reopen it. This is a report to an author
at draft time and it must not acquire an exit status that refuses a sheet. **The one exit status
ruling 5 adds is about the alias constant's own shape and never about a sheet's sources.**

**Growing `TOPIC_ALIASES` into the grouping.** Ruling 5 exists to make that fail rather than to make
it awkward.

**Reading the widened report as coverage.** ADR 0064's Consequences stand: nothing in this repo
derives which catalog cells are one clinical topic, and widening a string match to a second authored
name changes that for one subject and for nothing else.
