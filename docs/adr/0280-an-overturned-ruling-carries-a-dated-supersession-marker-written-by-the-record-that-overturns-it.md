# An overturned ruling carries a dated supersession marker written by the record that overturns it

**Measured at:** adb97bfa66f79690ded7879ac87d35907eba7872

[#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201) recorded that a reader
arriving at a ratified ADR by an old link has no way to know one of its rulings has been overturned.
[ADR 0201](0201-a-grounding-claim-names-what-was-read-and-a-falsified-record-is-marked.md) ruling 7
filed the class there rather than repairing the one instance that session had open. Grilled
2026-10-03 against `main`, where the freshness gate read `FRESH`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

### Two ratified practices disagree, and less than they appear to

**Leave the earlier record alone.** [ADR 0135](0135-the-session-law-is-one-grammar-limb-the-loose-spelling-is-refused-and-the-legal-reader-states-its-composition.md)
ruling 8 states it as house practice — *"The earlier record is not edited. That is this repository's
practice"* — on the ground that *"editing a ratified ADR would make its merge receipt point at text
that no longer exists."* [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md)
follows it by name. [ADR 0219](0219-a-refutation-fingerprints-its-heading-and-a-reader-pairs-the-draft.md),
[ADR 0225](0225-a-refused-reference-label-voids-only-its-declared-kinds-and-a-partial-gate-keeps-what-it-read.md),
[ADR 0231](0231-an-unreproduced-publication-is-refused-unread-and-every-gh-command-reaches-the-hook.md)
and [ADR 0246](0246-the-publish-marker-records-a-hook-run-per-checkout.md) each name the targets they
overturn and leave them unedited on purpose, pending this ruling.

**Add a dated note and leave the words.** [ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md)
ruling 6 marked ADR 0169, on the reason that *"a reader arriving at ADR 0169 by an old link must not
be standing on a falsified ground with no marker on it."* ADR 0201 ruling 5 marked ADR 0145 the same
way, and [ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)
carries the terser ancestor.

**The objection behind the first practice is to rewriting.** A note added beneath a ruling leaves
every ratified word where the merge receipt pointed, so the two practices conflict only if a marker
is read as an edit of the decision. ADR 0145, which states the first practice, now carries an
instance of the second.

### The population is derivable, and #1201's count is not it

#1201's body names 15 unmarked targets of 31, and its comments add more. **That count came from a
matcher that paired a supersession verb with an ADR number, and it missed the instance it was sent
after**: ADR 0131 answers ADR 0097 ruling 7 with *"This is that question, answered,"* and carries no
verb at all.

Every overturning that names its target is a pair in which a later record cites an earlier one. At
the commit declared above, **279 records carry 932 distinct later-cites-earlier pairs**, read as the
union of `ADR NNNN` text and a `NNNN-` record path. Reading each pair reaches the verb-free form. Its
floor is a later record that overturns an earlier one while naming it in neither form.

### The failure it exists for recurred during the grilling

[ADR 0279](0279-the-map-check-fails-only-on-new-debt-and-the-debt-it-inherited-is-frozen-and-drained.md)
merged on 2026-10-03 while this record was being grilled. It narrows
[ADR 0168](0168-a-map-obligation-belongs-to-whoever-incurred-it-and-the-producer-stamp-hashes-the-emitter.md)'s
sentence *"`map_scan` keeps failing on both rows"*, and ADR 0168 carries no marker. It is a member of
the population ruling 7 repairs.

## Ruling 1 — a ruling a later ADR overturns carries a dated supersession marker

Overturning a ruling in whole or in part obliges a **supersession marker** beneath it. The
overturned words are never rewritten: a superseded ruling was the true record of what was decided
on its date, so the marker adds text and replaces none. That keeps the merge receipt pointing at
every word it ratified, which is the whole of ADR 0135 ruling 8's stated objection.

**This retires the practice of leaving the earlier record alone**, stated by ADR 0135 ruling 8 and
followed by ADR 0145, and both records carry markers saying so.

## Ruling 2 — the trigger is a withdrawn or narrowed ruling, or a falsified ground

A marker is owed when a later ADR withdraws, changes or narrows what a ruling decided, and when it
falsifies the ground stated for a ruling that still stands. In the second case the marker says the
ruling stands and names what fell. A ground is carried away and reused as often as the ruling it
supports, and ADR 0201 ruling 3 already marked one.

**A later record that completes or extends a ruling and withdraws nothing owes none.** A fact that
was false on the day it was written remains an ADR 0016 correction, because its words are replaced
rather than preserved. A sentence that expires on its own stated condition — *"until #N lands"*,
then #N closes — is outside this rule: it tells its reader what to check, and nothing overturned it.

## Ruling 3 — the change that adds the overturning ADR writes the marker

The marker lands in the same branch and the same merge as the record that overturns. The author is
the one party who knows which words fell and what survives, at the moment of writing, and one review
then sees the overturning and the marker side by side. No window exists in which the earlier record
stands unmarked.

## Ruling 4 — the marker has a fixed opening and four parts

The marker sits directly beneath the overturned ruling or ground. It opens with the literal
`*Superseded YYYY-MM-DD.*`, and that opening is used for nothing else, so a superseded ruling stays
distinguishable from a corrected fact everywhere in the log. It then:

- quotes the overturned words rather than citing them by ordinal,
- names the overturning record with a link and its ruling number,
- states what still stands.

**Quoting is load-bearing**: ADR 0191 ruling 6 records a draft that called a third sentence the
second, which would have withdrawn the exception that record grants.

## Ruling 5 — the overturning ADR declares its targets, and a suite test binds both directions

A record that overturns anything carries an optional `## Supersedes` section naming each target and
its ruling. A test in `tools/` asserts that every declared target carries a `*Superseded*` marker
naming the declaring record, and that every such marker names a record that declares it. The second
direction catches a marker pointing at nothing, which is the live-link-to-the-wrong-thing failure
ADR 0191 repaired.

**It is a floor.** An overturning the author never recognizes is never declared, and the test cannot
see it; its declared limits say so beside the implementation. A matcher on supersession wording was
refused because it misses the verb-free form and fires on a record saying it *completes* a ruling.

**This record's own `## Supersedes` section is the first instance**, and the build either parses it
as written or reconciles it in the same change.

## Ruling 6 — a missing marker fails the suite and refuses no commit

The test runs under `python tools/suite.py` and in CI, as the ADR-number uniqueness test does, and
CI stays advisory under [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md). A refusing pre-commit
check was declined: the refusing roster is reserved for findings that protect clinical guidance a
consumer may rely on, and an unmarked ADR is a defect in the maintainer's decision log.

## Ruling 7 — the repair reads the whole derived population

Every later-cites-earlier pair is read and classified as overturned, ground falsified, neither, or
unsure. Each confirmed pair gains its marker and its declaration; nothing is decided by a reading the
clinician has not ruled. **The denominator is derived from the records rather than inherited from a
partial matcher**, and its floor is the one stated under *Measured before ruling*.

[ADR 0139](0139-a-floor-is-cited-by-api-and-symbol-and-coordinates-are-ratcheted-to-zero.md) ruling 2
declined a mass rewrite of the decision log and drew the line that a pointer is not a decision. A
marker rewrites no word and records a decision, so that refusal does not reach it.

## Ruling 8 — the rule and the repair are two tickets, joined by a cutoff

#1201 builds the rule: the marker form, the `## Supersedes` section and the test, binding this
record and every later one. A second ticket performs the repair and then lowers the cutoff so the
test binds the whole log. The rule protects new records from the day it lands, and a session that
dies inside the repair's long tail leaves the cutoff recording exactly how far the binding reaches,
which is ADR 0191 ruling 9's reason for the same split.

## Ruling 9 — existing markers in the old form are reworded, not duplicated

Markers written before this record open with *Corrected* or with no fixed phrase. The repair rewords
each opening to `*Superseded YYYY-MM-DD.*`, keeps its original date and words, and supplies any of
the four parts it lacks. A second marker beside each would leave a reader deciding whether one
ruling was overturned twice, and teaching the test the old wording would restore the ambiguity the
fixed opening removes.

## Ruling 10 — an unsure pair becomes a question, and its count is stated

The repair's agent marks only confirmed pairs. It files the unsure set as one `grilling` ticket that
quotes both records for each pair and recommends a classification, and the clinician rules them one
at a time. Until then the unsure count stands in the test's declared limits as an unread remainder,
so a clean run never reads as a whole log. This keeps the repair ticket buildable unattended, which
is what `ready-for-agent` promises.

## Supersedes

- [ADR 0135](0135-the-session-law-is-one-grammar-limb-the-loose-spelling-is-refused-and-the-legal-reader-states-its-composition.md)
  ruling 8, its stated practice *"The earlier record is not edited."* The ruling's verdict stands.
- [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md)
  ruling 5, its ground *"The earlier record is not edited, on the practice ADR 0135 ruling 8 states
  for itself."* The ruling stands.

## Rejected options

**Leave each marker to the author's judgment.** It is the state that produced the population: five
consecutive overturning records chose to leave their targets unedited.

**A central list of overturned rulings instead of markers.** One file and easy to check, but the
reader standing in the earlier record still sees nothing there, and that reader is the failure.

**A separate follow-up writes the markers after the overturning record merges.** It rebuilds the
unmarked window this record exists to close, one follow-up ticket per overturning record.

**A tool writes the marker from a declaration.** It spends machinery on the mechanical part and still
leaves what survives to the author.

**Mark completions and extensions too.** Markers announcing that nothing changed would train readers
to skip the ones that matter.

**Repair forward only, or repair only the targets already found.** The first leaves every existing
reader where #1201 found them; the second repairs whatever a partial matcher happened to surface,
which is the relevance filter the tracker-sweep rule refuses.

**Put the unsure pairs to the clinician inside the repair.** The repair ticket would stall waiting
for a person, and a ticket that does is not `ready-for-agent`.

## Consequences

**A reader arriving by an old link sees whether the ruling in front of them still stands.**

**Every overturning record now touches a second file**, and the test makes skipping it visible at
the merge.

**The decision log gains one marker form**, distinct from ADR 0016's fact corrections in its opening,
so counting markers counts supersessions.

## What this does not reach

**An overturning nobody recognizes.** The declaration is the author's, and the test binds what was
declared.

**Whether a marker's account of what survives is right.** That is a reading at review.

**An overturning recorded somewhere other than an ADR**, such as a ticket comment or a merged pull
request with no record. ADR 0201 ruling 7 placed ADR 0145 ruling 5's falsification by a manual read
outside the 31; whether such a falsification is a ground a later ADR overturned is a classification
for the repair's reading, not a ruling here.
