# The corrections the #1518 repair relabeled are classified and a banner record keeps its existing pair markers

**Measured at:** 90877cef78cd9cbacec1c867dfe1926b23fe8f07

[#1849](https://github.com/mshamblin5150-code/clinical-skills/issues/1849) was filed under
[ADR 0390](0390-an-overturned-passage-with-no-ruling-number-is-located-by-its-exact-quote-and-a-repair-s-mislabeled-opening-is-restored.md)
ruling 9 for the `*Corrected*` notes that commit `2f109057` (#1518) gave the counted opening
`*Superseded YYYY-MM-DD.*` and that ADR 0390 did not rule, plus one unruled passage of ADR 0076.
Grilled 2026-10-19 against `main` at the commit above, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session, one question at a time. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**The population is wider than the ticket's six, and wider than ADR 0390's nine.** Every hunk of
`git show 2f109057 -- docs/adr/` was read, the classification report excluded. The matcher is a
case-insensitive `correct` in a hunk's removed lines, with a second pass over hunks that add a
`*Superseded` line and carry `correct` only in context. It reads 14 such hunks across 13 records.
One is a false positive: ADR 0039's removed line is a supersession marker that says *correctly*. The
other 13 are **13 correction notes in 12 records** that now carry the counted opening:

- ADR 0076, 0137 and 0145, already ruled by ADR 0390;
- ADR 0036, 0078, 0147, 0169 (two notes) and 0243, the six #1849 names;
- ADR 0030 ruling 3, whose correction sat mid-line, and ADR 0152 and 0155, whose correction opened
  in bold `**Correction,`, the three the ticket's sweep comment found;
- ADR 0035 ruling 2, whose bold `**Corrected in place on …:**` label the repair moved behind a
  counted opening. The sweep comment left it out because its text survives, but the text of ADR 0036,
  0078 and 0147 survives in exactly the same way.

The matcher reads only the `correct` stem, so a correction worded *Amended* or *Revised* is below its
floor. ADR 0153's moved paragraph sits in a `## Correction` section but opens as a supersession
statement, and is not in the population. Commit `2f109057` is immutable, so these figures cannot
move.

**Every note was read blind, then read again.** Five readers, each given the two records a note
joins and ADR 0390 ruling 3's test, classified the notes without seeing the ticket, ADR 0390 or the
#1518 report. The session then read each note against its later record. **The reader brief named
three classes and omitted ADR 0280 ruling 2's *ground falsified***, so the reader who returned *no
marker* for ADR 0147 had no class for a ruling that stands on a reason that fell; that disagreement
was put to the clinician on its own. Where both readings agreed with high confidence the clinician
ruled the notes as one table; he ruled every split reading on its own. **Every class below matches
the one `docs/adr/supersession-classification-1518.json` already gives its pair**; the report was
consulted only after the readings.

**ADR 0343's banner covers twelve records**, eleven withdrawn whole and ADR 0089 withdrawn except
ruling 9. Counting paragraphs that open `*Superseded YYYY-MM-DD.*` other than the banner, **14 pair
markers sit in 5 of them**: ADR 0089 (3, beneath withdrawn rulings 1, 3 and 5), 0106 (2), 0107 (4),
0108 (3) and 0155 (2). Each records one map ruling replacing another while the map existed, and each
was written before the banner. The grilling put this question with a count of eleven in four
records, which missed ADR 0089; ruling 4 does not depend on the count.

**The binding reads the repair's added sentences.** `tools/test_adr_supersession.py` requires a
marker to carry a quoted span and the overturning record's link followed by `ruling N`. ADR 0169
ruling 3's own note names "ADR 0228 rulings 1 to 3", so the sentence the repair appended, "…
superseded by ADR 0228 ruling 1", is what satisfies it.

## Ruling 1 — the population is every correction note the repair relabeled

This record rules ten notes: the six #1849 names, ADR 0030 ruling 3, ADR 0152, ADR 0155, and ADR
0035 ruling 2. It also rules the ADR 0076 passage in ruling 3. A note of the same shape that a wider
matcher later finds is ruled by the same test and is not a new ticket by default.

## Ruling 2 — the ten notes are classified as follows

Every note below keeps its counted opening, because each records a supersession under ADR 0280
ruling 2.

| Class | Note | What replaced it |
| --- | --- | --- |
| Overturned | ADR 0030 ruling 3 | ADR 0045 ruling 1 made recommendation records a third cache stage once a batch producer existed |
| Overturned | ADR 0078 ruling 1, with rulings 2 and 5 | ADR 0102 ruling 11 moved the report key to the `subject` column and retired the alias dictionary |
| Overturned | ADR 0169 ruling 3 | ADR 0228 refused the adjacent line the build had graded clean |
| Overturned | ADR 0169 ruling 7, its third sentence | ADR 0191 ruling 3 withdrew the permission to correct anywhere below the line |
| Overturned | ADR 0243 ruling 2, its second sentence | ADR 0248 ruling 5 shipped all three index parts |
| Overturned, narrowed | ADR 0035 ruling 2, "Any span `read: no` → `unread`" | ADR 0066 ruling 1 made a zero-row sheet legal only at `none` or `non-source`, deleting a behavior #483 had specified and tested |
| Overturned, narrowed | ADR 0152 ruling 7, the refusal to fold a currency check into the hook | ADR 0200 ruling 1 put a non-fetching currency report in that hook; the cost objection to a fetch, the advisory posture and the consistent-never-current boundary stand |
| Overturned | ADR 0155 ruling 5, "**Folding the diff into `check` was refused.**" | ADR 0224 ruling 1; the note also records that the refusal's cost premise was false on its day, since `check` already paid the tracker read |
| Ground falsified | ADR 0036 ruling 1, "Nothing renders a reply" | ADR 0190 ruling 8; the reply grader is unchanged and now rests on the skill's "Do not add a heading" |
| Ground falsified | ADR 0147 ruling 6, "A reply is short and typed" | ADR 0190 ruling 2; the reply stopped being typed, and the one-gate ruling stands on length after the clinician declined a second gate |

**A refusal whose only ground was false on its day is still a supersession when a later record
chooses differently.** ADR 0155 ruling 5 refused a fold on a cost that measurement disproved, and
ADR 0224 replaced the refusal with new options. ADR 0016 replaces words; ADR 0280 ruling 1 forbids
rewriting a ruling, so the false premise is recorded inside the marker rather than corrected away.

**ADR 0066 lists ADR 0035's third limb among sites "corrected in place" on ADR 0016's terms.** That
label is the author's classification and ruling 5 below governs it: the counted opening stands and
ADR 0066's wording is left as written.

## Ruling 3 — ADR 0076's purpose clause is overturned in part, by its exact quote

ADR 0076's *What must not come out of this* bullet reads "A committed clinical-topic grouping built
for this row. Ruling 2 needs none. If one is ever built it is for a mechanical cross-sheet gate, on
its own ticket, and this record does not foreclose it." ADR 0102 ruling 1 built that grouping on its
own ticket with "ADR 0076's shipped reader, not a future gate" as its consumer, and never declared
the bullet.

**Only the words "If one is ever built it is for a mechanical cross-sheet gate" fell.** "Ruling 2
needs none" still holds, because the reader still derives the join per patient, and ADR 0102 keeps a
mechanical replacement for that judgment on its own prohibited list. The bullet's first sentence was
#584's build scope and expired with that build rather than being overturned.

The marker sits directly beneath the bullet in ADR 0390 ruling 1's exact-quote form and names ADR
0102 ruling 1. ADR 0102's `## Supersedes` gains the matching declaration.

## Ruling 4 — ADR 0390 ruling 4 stops new pair markers in a banner record and removes none

ADR 0390 ruling 4 discharges a pair whose words lie under ADR 0343's banner: no pair marker is
written. **It does not remove a pair marker already there.** The 14 existing markers stay.

The banner and an earlier pair marker record different events. The banner says every ruling fell to
ADR 0343 when the map was retired; a pair marker says, for example, that ADR 0224 replaced ADR 0155
ruling 5 while the map was still live. ADR 0390 refused writing markers into withdrawn records because those records are
themselves history, and a marker already in one is part of that history. Removing it would be the
rewrite ADR 0280 ruling 1 forbids.

So banner records stay uneven: these 14 overturnings carry markers, and ADR 0390's three discharged
pairs (0090→0089, 0144→0107 and 0279→0168) do not. The difference is when the overturning was
recognized, not what it was.

## Ruling 5 — an author's correction label inside a counted note stays word for word

Where a note is a supersession, its counted opening is its classification. An author's label that
called it a correction, such as `*(Corrected in place …, on ADR 0016's terms …)*` retained after
"The original dated account is retained:", stays exactly as written and is overruled by this record.
This is ADR 0390 ruling 5 in the other direction: there the word *Superseded* may remain in the prose
of a non-supersession because only the fixed opening is counted, and here the word *Corrected* may
remain in the prose of a supersession for the same reason.

The labels this governs today are in ADR 0035, 0036, 0078, 0147, 0152 and 0155. Where the repair
replaced the author's `*Corrected YYYY-MM-DD.*` opening outright (ADR 0169's two notes and ADR 0243)
or deleted the label (ADR 0030), the counted opening is the right class and nothing is restored.

## Ruling 6 — the build repairs what the reader sees and keeps what the binding reads

The repair moved several notes and left four reading defects. The build:

- returns ADR 0030 ruling 3's note into its numbered list so the list is no longer split;
- moves ADR 0147 ruling 6's note from between its gate-list items 4 and 5 to directly beneath the
  paragraph holding "A reply is short and typed", rejoining that list;
- re-anchors ADR 0152's dated "Figure corrected … the paragraph above" note beneath the paragraph
  that now holds the figure, and removes the stray blank lines the move left.

Each move keeps the marker attributable to the same ruling under `adr_read`'s grammar, and the
binding is re-run before the commit. **The repair's sentences that restate an author's note stay**,
in ADR 0155 and ADR 0169 ruling 3, because the binding reads them; removing ADR 0169's would leave
its marker without the `ruling N` link, and the author's words may not be rewritten to supply it.

## Ruling 7 — ADR 0390's figure and ADR 0190's claim are corrected under ADR 0016

**ADR 0390's measured sentence "Nine notes across eight records that opened `*Corrected`" is
corrected in place** to the 13 notes in 12 records measured above, naming the forms the nine
omitted, with a dated line recording what it said. Its `**Measured at:**` line is re-declared for
that correction alone, on ADR 0200's precedent, so the staged-ADR check grades it.

**ADR 0390 ruling 9's "six" stays as written.** It sits in a deciding paragraph, which ADR 0016 keeps
untouchable, and the decision it carries stands: this record extends it and withdraws nothing, so
under ADR 0280 ruling 2 no marker is owed. A dated note directly beneath ruling 9 says the population
was larger and links this record.

**ADR 0190 ruling 8's statement that the reply's no-heading ground is one "ADR 0036 could not have
stated because it predates the renderer" is corrected in place.** `skills/discussion-reply/SKILL.md`
already said "Do not add a heading." at `da4fee25`, the commit that recorded ADR 0036. The ruling's
outcome is unaffected.

## Build checklist

- [ ] Ruling 3: the exact-quote marker beneath ADR 0076's bullet and the declaration in ADR 0102's
      `## Supersedes`. This needs ADR 0390 ruling 1's quote-keyed binding, which #1706's build adds.
- [ ] Ruling 6: the moves in ADR 0030, 0147 and 0152, with the binding green afterwards.
- [ ] Ruling 7: the in-place correction and re-declared `**Measured at:**` in ADR 0390, the dated
      note beneath its ruling 9, and the in-place correction in ADR 0190 ruling 8.
- [ ] No counted opening in the ten notes is removed, and no correction label is edited.

## Rejected options

**Rule only the six the ticket names.** The other four are the same repair, the same test and the same
commit. They were missed because the literal opening that defined the first count also defined the
population, and splitting them off would repeat that narrow search.

**Remove existing pair markers from banner records.** Fourteen edits across five records, deleting
dated history the banner does not carry.

**Delete the authors' correction labels, or add a correction note beneath each.** Deleting rewrites
dated author text; a note on each corrects a classification rather than a fact, which is not ADR
0016's subject.

**Delete the repair's duplicate sentences.** ADR 0169 ruling 3's marker would fail the binding.

**Treat ADR 0155 ruling 5 as an ADR 0016 correction.** It would invite rewriting a ruled refusal.

**Mark the whole ADR 0076 bullet.** It would mark as withdrawn a sentence that still holds and a
build scope that merely expired.

**Record these rulings in ADR 0390 or only on the ticket.** The first reopens a ratified record for a
different ticket's rulings; the second leaves the banner and label readings outside `docs/adr/`.

## What this record does not reach

**Whether each marker's account of what survives is right.** That stays a reading at review.

**A correction note worded without the `correct` stem.** It is below this record's matcher.

**Any later record that overturns one of these rulings while naming it in neither form**, which
remains below the #1518 population's floor, as ADR 0280 states.
