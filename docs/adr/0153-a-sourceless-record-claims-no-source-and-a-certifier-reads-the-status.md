# A sourceless record claims no source and a certifier reads the status

Out of [#963](https://github.com/mshamblin5150-code/clinical-skills/issues/963), grilled on
2026-09-08. Measured at `86161b5`.

A claim record whose `STATUS` says a search found no source could carry a source class, a recency
disposition, and a full restatement of what a source says, and grade clean. It is a settled negative
wearing a source class, inside the grader that exists to catch settled negatives.

The grilling found the defect is larger than the ticket stated in two directions at once. The
restatement on such a record is read by two *other* graders as evidence that a number in a graded
submission came from research, and neither of them can see `STATUS` at all. And the field vocabulary
was never decided by anybody: it grew one ticket at a time, each ticket adding the fields it was
itself inventing.

## What was measured before ruling, on 2026-09-08

**Nobody decided the current set.** `git show 60686c4` — the [#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231)
commit — introduces `CITATION_FIELDS` under a comment that is still in the file word for word:

> Every field that is a claim about a source. An `unsourced` record says there is no source, so
> carrying any one of them is the contradiction `UNSOURCED_WITH_CITATION_FIELD` was written for --
> widened by #231 from the one field to the four

**"The four" are the four fields #231 was inventing.** At that same commit `REQUIRED_WHEN_SOURCED`
already held `SOURCE`, `RESTATEMENT` and `RECENCY`, three lines above, and they were not swept in.
[#500](https://github.com/mshamblin5150-code/clinical-skills/issues/500) then added `SECOND-ROUTE`
and [#498](https://github.com/mshamblin5150-code/clinical-skills/issues/498) added `STATED-EXPIRY`,
each adding its own new fields and neither re-reading the ones already there. **The comment has
stated the rule below since the day it was written and the tuple has never implemented it** — the
prose right and the population short, which is this repository's own recurring shape.

**The briefs never agreed either.** Four skills carry the rule in two phrasings that were never
reconciled: `skills/discussion-post/SKILL.md` and `skills/discussion-reply/SKILL.md` say *omit the
other fields*, entering on [#416](https://github.com/mshamblin5150-code/clinical-skills/issues/416)
and [#399](https://github.com/mshamblin5150-code/clinical-skills/issues/399);
`skills/course-assignment/SKILL.md` says *omit every source field*; and
`skills/practicum-case-study/SKILL.md` carries no omit clause for `unsourced` in its prose at all,
only a defect-table row reading *carrying a source field*.

**The live corpus, across 40 registered checkouts and 12 ledger files, 1,436 claim records.** 1,303
`sourced`, 133 `unsourced`, 0 `unreadable`. Of the 133 sourceless records: **0** carry `SOURCE`,
**89** carry `RECENCY` and every one of the 89 is the single word `current`, and **90** carry
`RESTATEMENT`. All 133 carry a substantive `STATUS` remainder. They sit in three ledgers — two
`course-assignment` runs and one `case-study` run — and in the larger `course-assignment` ledger the
restatement rate on sourceless records is **43 of 43**. That ledger has no `DATE:` header, so
`research_ledger.py` exits 2 on it: it did not grade clean, it was never graded at all.

**A restatement on a sourceless record is of nothing, and that was measured rather than assumed.**
Of the 90, **2** name a location in a document, **10** carry a four-digit year, **0** match a
`sourced` record's restatement in the same ledger, and **26** are two eleven-word sentences pasted
thirteen times each inside one run. The attribution grammar is present and the attribution content
is not. **4 carry a URL or DOI** — `RESOLVED`'s content wearing `RESTATEMENT`'s name, on records
where `RESOLVED` has been forbidden since #231, which is that rule being routed around through the
one field it forgot to close.

**Two other graders read the field to certify a number, and cannot see `STATUS`.**
`discussion_post_scan._claim_records` and `discussion_reply_scan._number_findings` each build
`trace_text` from the claim heading plus `RESTATEMENT`, harvest every number from it, and refuse a
body number absent from that set on `UNTRACED_NUMBER`. A count of `STATUS` over
`discussion_post_scan.py`, `discussion_reply_scan.py` and their shared `discussion_artifact.py`
returns **0, 0, 0**: the status is not ignored, it is unreachable.

**Field hygiene alone cannot close that, because the claim heading is half the trace text.** **92 of
the 133** sourceless records contribute traced numbers today, **159 distinct tokens**, and only 60 of
those needed a restatement to do it. The remainder come from the heading, which no field rule
removes.

**The live neighbors of that hole are not the ones the ticket predicted.** By status and refutation:
1,254 `sourced`/`stands`, 133 `unsourced`, **48 `sourced` carrying no `REFUTATION` field at all**
contributing 264 distinct tokens, 1 `sourced`/`paywalled`, and **0** `refuted`.

## Ruling 1. The rule is that a sourceless record makes no claim about a source, decided field by field

Two rules were available. *Omit the other fields* is a format convention and states no reason. *Make
no claim about a source* states one, and the reason is what decides a field the tree does not yet
have: **does this field assert something about a document the record says it does not have?**

The second is chosen. A rule with no reason is one the next agent argues with, which is how
`RECENCY: current` came to be written 89 times, and *omit the other fields* cannot refuse the same
content moved into the `STATUS` remainder while this rule can.

## Ruling 2. `SOURCE`, `RECENCY` and `RESTATEMENT` join, and the set becomes every field but `STATUS` and `INSTRUMENTS`

A source class and a recency disposition are assertions about a document, on ruling 1's test, and
neither is arguable. `RESTATEMENT` is defined as a source claim by every brief that names it —
*what the source says* in three, and *the whole point is the source's own terms* in the fourth — so
it joins on its own definition rather than on an interpretation.

`FIELD` recognizes eleven names. Removing `STATUS`, which carries the status, and `INSTRUMENTS`,
which is graded on its own two branches by `UNEXPECTED_INSTRUMENTS`, leaves nine. **The set is all
nine**, and #963's *what must not come out of this* forbids arriving there **without asking what an
honest sourceless record is entitled to record**. It was asked, field by field, and the answer is
that the honest record is entitled to its `STATUS` remainder. The prohibition was on the shortcut and
not on the destination.

**The counter-argument dissolves under ruling 1 rather than surviving it.** A search that read a
document and found it insufficient did read a document; putting that document's content on a record
asserting no source was found is the contradiction itself, and it is what makes the number available
to a certifier.

**Predicate unchanged.** `SUBSTANCE.search`, not key presence. An empty `SOURCE:` line is a template
artifact and not a claim, and `UNEXPECTED_INSTRUMENTS`' key-presence rule is not adopted here.

**Renamed, because the current names are wrong twice over.** The row fires on `unreadable` as well as
`unsourced` and now on fields that are not citations, so `UNSOURCED_WITH_CITATION_FIELD` becomes
`SOURCELESS_WITH_SOURCE_FIELD` and `CITATION_FIELDS` becomes `SOURCE_FIELDS`, matching
`_sourceless_findings`, which #818 had already renamed. `ROWS` keeps its `#214` pointer.

## Ruling 3. The number certifier reads `STATUS` and `REFUTATION`, and disbelieves three states

`discussion_post_scan.py` and `discussion_reply_scan.py` read both fields, imported from
`research_ledger` on `reference_scan.py`'s `REFERENCE_HEADING` precedent rather than restated. A
record whose `STATUS` is `unsourced` or `unreadable`, or whose `REFUTATION` is `refuted`, **contributes
no traced numbers**.

**This is in #963 rather than its own ticket, by the clinician's decision on 2026-09-08**, against a
recommendation to split it. The measurement supports the decision: field hygiene closes 60 of the 92
laundering records and the claim heading keeps the rest, so the two halves are not separable into two
merges without shipping a fix that does not fix it.

**Three states and not every refusable record.** Making the certifier disbelieve anything
`research_ledger` would refuse means importing the bar, the `as_of` date and most of
`record_findings` into two scanners. The three chosen are the states whose whole meaning is *this
record has no usable source*; they are two closed vocabularies with no dates and no bar. The 48 live
records missing a `REFUTATION` are a field-completeness defect that the ledger grader already owns,
and having a certifier re-derive it is the rejected option through a side door.

**`refuted` has zero live instances**, so it costs nothing today and is shut before the first one
arrives.

**No new finding kind.** A disbelieved record contributes nothing, so a body number falls through to
the existing `UNTRACED_NUMBER`, which is already the correct refusal.

## Ruling 4. The certifier still believes a disbelieved record's reference key, and the asymmetry is deliberate

`reference_key_set` exists only to **recognize** narrative citations: `read_citations` walks back
from a year and accepts an unparenthesized `Author (2024)` as a citation because that key is in the
set. Removing a key therefore stops the sentence being seen as a citation at all.

**That is the wrong direction.** A reader that stops recognizing a citation reports a cleaner body,
not a dirtier one — a search that could not have worked answering like a settled negative, rebuilt
inside the fix for it. So ruling 3 applies to `record.numbers` and never to `record.references`, and
the asymmetry is stated in the code rather than left looking like an oversight.

## Ruling 5. The rule is written once, in `skills/_shared/reference/sourcing.md`

[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md) ruling 4 already
puts the sourcing rules in one file with the briefing surfaces pointing at it. This rule follows that
arrangement. **That is also what retires *omit the other fields* against *omit every source field*
without picking a winner** — two hand-kept copies of one rule, each editable without failing
anything, is the shape [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
ruled insufficient, and the reconciliation is to have one copy rather than to choose.

## Ruling 6. The live records are not repaired

90 records across three preserved run directories begin failing. **They stay as they are.** A
preserved run record is evidence of what a run produced, and this repository does not edit one so a
tool passes; the rows are additive refusals and a later run of any of those artifacts writes the
compliant shape.

**The larger of the two `course-assignment` ledgers was never graded**, having no `DATE:` header, so
its 43-of-43 restatement rate is not a grader that passed it — it is the interval in which nothing
looked.

## What this record does not settle

**Whether the `STATUS` remainder is true.** All 133 sourceless records carry a substantive one and
nothing verifies it. The rule above moves the recheck record into that field and grades it for
substance only, which is a declared limit rather than a closed hole.

**Whether a rejected source can be named well enough to recheck.** `RESOLVED` has been forbidden on a
sourceless record since #231, so the tree permits *content with no provenance* and forbids
*provenance with no content*. This record removes the first half and deliberately does not reopen the
second: giving a settled negative a locator is the shape #231 built the row to refuse.

**Whether a believed record's restatement supports the number traced from it.** Ruling 3 decides
which records a certifier reads and asserts nothing about whether their content is true.

**Whether the 48 `sourced` records carrying no `REFUTATION` are reaching drafts.** Ruling 3 leaves
them to the ledger grader and this record does not measure their draft join.

**What the 44 sourceless restatements containing the bare word `figure` are.** The text was not read,
being working material under `scratch/`; the confound is named and nothing above rests on it.
