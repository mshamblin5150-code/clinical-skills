# An overturned passage with no ruling number is located by its exact quote and a repair's mislabeled opening is restored

**Measured at:** 9e1916f1d6e47081127f7979b732b4241cfd6578

*Re-declared from `66aaf05b1bcf7ee185f7f7010af35d1e66ac5eff` on 2026-10-19, for the correction-note population correction alone. The other measurements below remain dated observations of the 2026-10-17 base and were not re-derived at this one.*

[#1706](https://github.com/mshamblin5150-code/clinical-skills/issues/1706) was filed under
[ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
ruling 10 by [#1518](https://github.com/mshamblin5150-code/clinical-skills/issues/1518)'s repair. It
holds the pairs that repair could not classify and the old-form markers it could not attribute.
Grilled 2026-10-17 against `main`, where the freshness gate read `FRESH`; the clinician ruled every
point below in that session, one question at a time. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**Every unsure pair hit the same wall.** At the commit above, `docs/adr/supersession-classification-1518.json`
held 29 pairs classified `unsure` and 8 `unresolved_legacy_markers`. In all 29 the overturned words sit
outside any numbered ruling: either the earlier record has none (ADR 0002, 0005, 0013, 0015 and 0037),
or the words sit in a section such as *Rejected options* or *What must not come out of this*. The
binding in `tools/test_adr_supersession.py` reads only `ruling N` declarations and markers beneath a
recognized ruling, so no classification of those pairs could become a marker.

**Two independent readings were taken before any pair was ruled.** Five blind readers, each given only
the two records and ADR 0280 ruling 2's definitions, re-read every pair without seeing #1706's
recommendations. Where the blind reading and #1706's agreed and no structural problem was present, the
clinician ruled the pairs as one table. He ruled every disagreement on its own.

**The repair that filed this ticket also damaged the records it touched.** Commit `2f109057`
(#1518) prefixed the counted opening `*Superseded YYYY-MM-DD.*` onto every old-form note. It checked
neither each note's class nor its layout:

- In ADR 0107 line 67, ADR 0137 line 215 and ADR 0179 line 93, the opening or the reworded marker
  absorbed a `## Superseded in part by …` heading, which no longer renders.
- Thirteen correction notes across twelve records were given the counted opening. The nine counted
  by line-opening `*Corrected` omitted ADR 0030's mid-line correction and ADR 0035, 0152 and 0155's
  bold correction labels. Three are ruled below; one of the three was not a supersession at all.
- ADR 0002 carries two counted markers for one overturning.
- ADR 0201 gained a `## Supersedes` section that declares a pair this record classifies as neither.

**Two overturned passages no longer exist where they were ratified.** The #927 build deleted ADR
0002's "What the floor actually is…" paragraph on 2026-09-12; its words survive at `562787b3^`. ADR
0076 ruling 3's quoted reader contract was rewritten in place on the day ADR 0102 was ratified; its
ratified words survive at `96f2e99d`. Both edits predate ADR 0280 ruling 1's never-rewrite rule.

## Ruling 1 — where the overturned words have no ruling number, their exact quote is the coordinate

A declaration whose target words sit outside any numbered ruling reads
`- [ADR NNNN](NNNN-slug.md) the words "…", what still stands`, with no ruling number. Its marker sits
directly beneath the paragraph that holds those words. The binding keys the pair on the target record,
the declaring record and the exact quote, and the quote must occur exactly once in the target outside
any marker.

**A ruling number is still used wherever one exists.** The quote form exists because inventing an
ordinal for unnumbered text would point a reader at a ruling that says something else, which is the
error ADR 0280 ruling 4's quoting requirement was written against.

## Ruling 2 — a record with no numbered rulings is linked bare

A marker names its overturning record with a link and that record's ruling number. Where the
overturning record has **no** numbered rulings, the marker links the record alone. The check confirms
the condition mechanically, so a bare link to a record that has rulings is a finding. ADR 0014 is the
only overturning record this applies to today.

## Ruling 3 — a decision later changed is a supersession, and a fact false when written is not

A later record's verb does not decide the class. A ruling about what the repository will do, true or
open when made and later replaced by a different choice, is overturned even where the later record
says *corrects*. A fact that was false on the day it was written stays an ADR 0016 correction even
where the later record says *supersedes*, as ADR 0280 ruling 2 already provides.

Two further shapes owe no marker:

- **A fact that was true when written and moved later**, where no decision rests on it, such as a
  corpus description or the module that hosts a named symbol.
- **A declared gap later filled or a declared limit later built past.** Filling an open question or
  building the detector a limit said was missing completes the record and withdraws nothing.

## Ruling 4 — a pair whose words lie under an ADR 0343 banner is discharged by the banner

Where the overturned words sit in a record that
[ADR 0343](0343-the-implementation-map-is-retired-and-a-wholly-withdrawn-record-carries-one-supersession-banner.md)
withdrew whole, or in a ruling that ADR 0343's banner withdraws, the pair is recorded as overturned
and no pair marker is written. The classification report gains a disposition naming the banner as
what tells the reader, so the binding does not read the pair as a missing declaration. ADR 0343 ruling
5 already says such a record carries one banner instead of per-ruling markers.

## Ruling 5 — a counted opening a repair added to a non-supersession is removed

Where a note is classified as no supersession, any counted `*Superseded YYYY-MM-DD.*` opening that a
later repair added or substituted is taken off, and the opening the note's author wrote is restored
word for word. The note stays as a pointer or an ADR 0016 correction and no longer counts. The word
*Superseded* may remain in its prose; only the fixed opening is counted.

## Ruling 6 — overturned words rewritten away before ADR 0280 are restored from git

Where the words a later record overturned were deleted or rewritten in place before ADR 0280 ruled,
the ratified words are restored from the commit that holds them, and the ordinary marker goes directly
beneath them stating what replaced them. ADR 0280 ruling 1's ground is that the merge receipt points
at every word it ratified, and today it points at words that are gone.

## Ruling 7 — one overturning carries one counted marker, and a marker holds no heading

Where two counted markers record one overturning, the one beneath the overturned words stays counted
and the other's added opening is removed, leaving its author's words. A test refuses any marker
paragraph that contains a `##` heading, and each heading the #1518 repair absorbed is restored to its
own line word for word.

## Ruling 8 — the pairs are classified as follows

Pairs are written *later → earlier*. "Ground" means the ruling stands and only its stated ground fell.

| Class | Pairs |
| --- | --- |
| Overturned | 0014→0005, 0029→0007, 0035→0009, 0056→0040, 0056→0042, 0057→0009, 0060→0051, 0089→0037, 0102→0076, 0147→0013, 0147→0015, 0179→0137, 0187→0002, 0216→0137, 0223→0206, 0237→0185 |
| Overturned limb the #1518 repair left unmarked | 0151→0039, 0167→0119 |
| Ground falsified | 0034→0030, 0053→0052, 0062→0061, 0067→0047, 0150→0100 |
| Overturned, discharged by the ADR 0343 banner | 0090→0089, 0144→0107, 0279→0168 |
| Neither | 0056→0052, 0062→0057, 0065→0030, 0088→0039, 0092→0037, 0099→0048, 0119→0053, 0152→0131, 0201→0039, 0201→0145 |

0179→0137, 0053→0052 and 0088→0039 were classified by the #1518 report and are reclassified here on
the fifth reader's dispute. The quoted words, overturning ruling and surviving account for each pair
are #1706's build specification, which this record does not restate.

**The application to individual records:**

- ADR 0052 loses the opening the repair added to 0056's note (ruling 5).
- ADR 0039's grounding note regains its opening *"Superseded grounding marked 2026-09-12."* (ruling 5).
- ADR 0145's note regains *"Corrected 2026-09-12."*, and the `## Supersedes` section the repair added
  to ADR 0201 is removed (ruling 5).
- ADR 0002's deleted paragraph is restored and its line-31 marker sits beneath it; its line-92 note
  loses its added opening (rulings 6 and 7).
- ADR 0076 ruling 3's ratified contract is restored and the marker beneath it carries ADR 0102's
  wording, which keeps every phrase `tools/test_checks_ledger.py` asserts (ruling 6).
- ADR 0005's note moves directly beneath its key sentence, with "below" corrected to "above" under
  ADR 0016 (rulings 1 and 2).
- ADR 0131 ruling 5's closure claim gains a dated `*Corrected*` note under ADR 0016 recording that the
  desktop application's worktrees bypassed the hook from the day it was ruled (ruling 3).
- ADR 0053 ruling 1 falsifies the ground of ADR 0052 ruling 7, and the marker sits beneath ruling 7.

## Ruling 9 — what the repair found outside this population is filed, not widened in

The six `*Corrected*` openings the #1518 repair swapped that this record does not rule, in ADR 0036,
0078, 0147, 0169 (two) and 0243, go to their own `grilling` ticket, which applies ruling 3 and ruling 5.
The #976 build's reversal of ADR 0039 ruling 2 with no ADR declaring it is filed as a finding; an
overturning recorded outside an ADR is outside ADR 0280's binding by that record's own declared limit.

*Population clarified 2026-10-19, under [ADR 0418](0418-the-corrections-the-1518-repair-relabeled-are-classified-and-a-banner-record-keeps-its-existing-pair-markers.md) rulings 1 and 7: the six named above were part of a larger set. That record rules the ten relabeled notes not ruled here, plus ADR 0076's purpose clause. Ruling 9's decision stands.*

## Supersedes

- [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
  ruling 4, the words "names the overturning record with a link and its ruling number,". A record with
  no numbered rulings is linked bare. The fixed opening, the quote and the account of what stands
  still stand.
- [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
  ruling 5, the words "naming each target and its ruling". A target outside any numbered ruling is
  named by its exact quote. The binding in both directions and its floor still stand.

## Rejected options

**Name an unnumbered target by its section heading.** A section can hold several passages of which
only one fell, so a heading coordinate reintroduces the wrong-sentence error ADR 0280 ruling 4's quote
was written against, and some records repeat a heading.

**Leave unnumbered targets as a permanent declared limit.** A reader reaching ADR 0005 or 0037 by an
old link would see nothing, which is the failure ADR 0280 exists to close, and the unread remainder
would never reach zero.

**Accept the repair's recommendations wholesale.** They were one unchecked reading, and one of them
recommended *overturned* for a pair whose later record says in so many words that the earlier record
is not superseded.

**Rule all 29 pairs one at a time.** Most agreed pairs are settled by the records' own words, so that
would have spent the clinician's attention where no reading conflicted.

**Write pair markers into records ADR 0343 withdrew whole.** It contradicts ADR 0343 ruling 5's one
banner instead of per-ruling markers, and writes markers into records that are themselves history.

**Leave pre-0280 rewrites in place and quote the lost words from a commit.** The binding would need a
commit-resolved quote form, and a reader arriving by an old link would still see text no ruling
produced.

**Widen this ticket to the six unexamined `*Corrected*` swaps.** They were inherited from #1518's
confirmed set rather than entangled with these pairs, and this record gives their ticket a test it can
apply directly.

## Consequences

**Once built, the historical unsure and unattributed-legacy remainders both read zero**, and the
binding covers every pair the #1518 population derived.

**The supersession count stops including corrections**, because ruling 5 removes the counted opening
wherever a repair placed it on a note that records no overturning.

**Two ratified records gain back text they lost.** ADR 0002 and ADR 0076 read again as they were
ratified, with markers saying what replaced the words.

## What this does not reach

**Whether a marker's account of what survives is right.** That stays a reading at review.

**The six unexamined swaps and the #976 reversal**, which ruling 9 files.

**An overturning nobody recognized.** The blind readings covered the pairs the #1518 population
derived; a later record that overturns an earlier one while naming it in neither form remains below
that population's floor, as ADR 0280 states.

*Corrected 2026-10-19, under [ADR 0418](0418-the-corrections-the-1518-repair-relabeled-are-classified-and-a-banner-record-keeps-its-existing-pair-markers.md) ruling 7: the measured sentence read "Nine notes across eight records that opened `*Corrected`". Reading commit `2f109057` with the wider matcher recorded there gives thirteen correction notes in twelve records, including the mid-line and bold labels omitted by that count.*
