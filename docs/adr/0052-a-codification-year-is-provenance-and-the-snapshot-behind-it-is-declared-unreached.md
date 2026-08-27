# A codification year is provenance and the snapshot behind it is declared unreached

[#534](https://github.com/mshamblin5150-code/clinical-skills/issues/534) was separated out of
[#498](https://github.com/mshamblin5150-code/clinical-skills/issues/498) by
[ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
ruling 1 and ruling 10: a cited source with a published reissue schedule has a replacement date
nothing records, and `STATED-EXPIRY` is ruled not to carry it.

Grilled 2026-08-27. **Six decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

**Corrected in place 2026-08-27, hours after merging and before anything was built against it.**
The exhaustive tracker sweep this record's own session ran found **six** defects in it, and one
reverses a ratified ruling. ADR 0038's, ADR 0042's and ADR 0050's correction headers are the
precedent. Ruling 1, 2, 4, 5 and 6 are untouched; **ruling 3's first limb is replaced.**

- **Ruling 3 ordered `research_ledger.NOT_REACHED` built for one row, which three ratified
  records refuse by name.**
  [ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
  ruling 9 *declined that object as its change and filed it* as
  [#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535);
  [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
  ruling 9 landed its own limit as prose and left `#535` the owner;
  [ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
  ruling 11 built one for `discussion_reply_scan` **because that module holds one prose ceiling**
  and said in as many words that for `research_ledger` *"an object with one row genuinely would
  have been a numerator with no denominator."* This record cited ADR 0040 rulings 1, 2 and 3, never
  ruling 9, and asserted in its correction header on that file that *every ruling below stands* —
  reversing a ruling in the act of declaring it intact. Ruling 3's first limb now takes ADR 0042
  ruling 9's arrangement instead.
- **"The only ledger grader in `tools/` without a limits object" was false.** Re-derived at
  `9e08a23`: `research_ledger.py`, `checks_ledger.py` and `discussion_reply_scan.py` all hold
  none. Three, not one — and `#535`'s own population question is live, so the number is a floor.
- **"The established arrangement" is a hybrid of two, and neither module writes it.**
  `reference_scan.NOT_REACHED` *is* a `(key, sentence)` tuple; `case_study_scan.NOT_REACHED` is
  **derived** from a `(text, disposition)` tuple. This record specified the first one's payload
  with the second one's derivation and called it established. That is
  [#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550)'s subject, and the
  shape is `#535`'s to rule.
- **`SECOND-ROUTE (#542)` named a merged pull request.** The ticket is
  [#500](https://github.com/mshamblin5150-code/clinical-skills/issues/500). No source supplied
  `542`; it was invented, which is
  [#554](https://github.com/mshamblin5150-code/clinical-skills/issues/554)'s class arriving in a
  record written hours after this session corrected an instance of it on `#534`.
- **"Whether a run will fill in a field it is given. #541's subject."** It is not.
  [#541](https://github.com/mshamblin5150-code/clinical-skills/issues/541) is the
  authenticated-route asymmetry between researcher and refuter; the phrase appears once in it,
  inside *What must not come out of this*. Promoting one clause of a prohibition into a ticket's
  subject would make `#541` the de-facto owner of the ledger's whole field budget, which nothing
  has ruled. Corrected below.
- **The sixth is in ADR 0040 rather than here** and is recorded on that file: ruling 10's
  *"ADR 0039 ruling 6"* miscitation survived the in-place correction this session made to the
  same file.

## Measured before ruling, at `f9a501c`

Re-derived in this session by command, not carried from the ticket.

| | |
| ---: | --- |
| claim ledgers in the tree | **4** |
| claim records | **23** |
| citations (`REFERENCE:` fields) | **22** |
| citations on a published reissue cadence | **1** |
| distinct publishers in that bucket | **1** (GPO / C.F.R.) |
| citations with an expiry printed on the document | **1** (#498's case, not this one) |

Counts only. The ledgers live under `scratch/` and no record text was read into this record
beyond the one bibliographic citation the ticket is filed over.

**`research_ledger.py` holds no declared-limits object**, which ADR 0040 measured and which still
holds. ~~Every sibling ledger grader does.~~ **Corrected 2026-08-27: three ledger graders hold
none** — `research_ledger.py`, `checks_ledger.py` and `discussion_reply_scan.py`, re-derived at
`9e08a23`. Four other modules do carry one — `reference_scan.NOT_REACHED`,
`case_study_scan.DECLARED_LIMITS`, `discussion_post_scan.NOT_REACHED`,
`differential_scan.NOT_VALIDATED_AGAINST` — and they do not write one shape between them. **What
counts as a limits object, and what shape one takes, are
[#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535)'s and
[#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550)'s open questions, so
every count here is a floor rather than a census.**

`STATED-EXPIRY` and `SECOND-ROUTE` are both unbuilt tree-wide.

## ADR 0040's denominator is wrong, and this ticket turned on it

ADR 0040's *Measured before ruling* reads **"Every claim ledger in the tree is 9 records across
2 runs"** and names the two `discussion` runs. It missed
`scratch/runs/nur5144-m1-case-study/claims-2026-08-19.md` and `claims-2026-08-20.md` — 14
records, 13 citations, both last written **2026-08-20**, six days before that ADR was ruled.

A matcher scoped to one run type, reported as *every ledger in the tree*. That is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape arriving inside
a ratified record, on the exact figure the separated ticket's *Done when* asks for.

**It moves the rate ADR 0040 wrote a paragraph about.** That record corrected #498's figure from
*two of five records in one run* to *one of nine across the tree* and treated the movement as
load-bearing. The true figure is **one of twenty-two**, less than half its own corrected number.
The correction is applied in place on ADR 0040 under the ADR 0038, ADR 0042 and ADR 0050
precedent, and carried to #498 under ruling 5 below.

## The ruling

**1. The defect is the snapshot, not the year, and two of the ticket's four options die on the
merits.**

`(2025)` in `42 C.F.R. § 414.56 (2025)` is the **edition of the code the writer consulted**. It
is provenance. It was accurate the day it was written and it is accurate in 2031; it never
becomes false. What can become false is the unstated claim riding underneath it — *the text I
quoted is still the text in force.*

Every option the ticket lists treats the year as a number that goes stale. Measured against this
ruling:

- **A per-publisher cadence table is refused.** The annual C.F.R. recodification reissues the
  whole title on schedule, but the overwhelming majority of individual sections are unchanged
  between editions. A row keyed on the cadence therefore fires on *every* C.F.R. citation
  *every* year, and is right about the edition and wrong about the section's content almost
  every time. That is a row that false-alarms on correct records —
  [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect, which the
  ticket cites three separate times as the thing to avoid, arriving inside its own leading
  option. It is refused on this ground and not on the cost of maintaining the table.
- **Reaching it from the citation side is refused.** The ticket concedes a draft citing `(2025)`
  against a `(2025)` entry agrees perfectly. ADR 0039's *What none of this reaches* adds the
  harder half: an APA legal entry yields an **empty-year key by design**, and *no branch
  considered here can* make the year enforceable while the bare form must resolve. There is
  nothing on the entry side to compare against. This is not an unbuilt gap someone could close.

**2. The limit is declared, and the strongest build is recorded as rejected rather than
unmentioned.**

The build that survives ruling 1 is not in the ticket. It is a per-section **last amended** date
transcribed off the eCFR section page — a fact the document states about itself, so it clears
ADR 0040 ruling 1's transcription-not-inference line — joined against the edition year already
in the citation:

```text
REFERENCE:  42 C.F.R. § 414.56 (2025). ...
SECTION-AMENDED: 2026-03-14, stated on the eCFR section page under "Source"
                 -> edition cited 2025, section amended after it - SUPERSEDED

SECTION-AMENDED: 2019-11-12, stated on the eCFR section page under "Source"
                 -> edition cited 2025, section unchanged since 2019 - clean
```

One row, two transcribed strings, no cadence, no inference, no network at grading time. It
cannot false-alarm on a correct record, and unlike the cadence row it fires only on the
citations whose text actually moved. It is ADR 0040 ruling 2's accruing-rather-than-decaying
property, on the half ruling 1 excluded.

**It is refused on rate and on field contention, not on soundness.** It is a third new required
field arriving into a slot `STATED-EXPIRY` (#498) and `SECOND-ROUTE` ([#500](https://github.com/mshamblin5150-code/clinical-skills/issues/500)) already contend for,
and [#541](https://github.com/mshamblin5150-code/clinical-skills/issues/541) names field count as
a cost nobody has priced against a run's willingness to fill fields in honestly. It buys a row
that can fire on **one citation in twenty-two, from one publisher**.

### Rejected: a record field naming the cadence rule relied on

The ticket's option 2. It costs an unfalsifiable field (R2), does not fire on a record that never
mentions a cadence, and after ruling 1 it is a field for an inference this record has just
refused to let any field carry.

### Rejected: a weaker form of ruling 2's build

A `SECTION-AMENDED` field with no join to the edition year buys no row at all. The last-amended
date is always at or before the day the agent read the page, so the comparison is vacuous on the
day it is written and nothing ever re-reads it. A field that fires never is the R2 defect with
extra steps. If this is ever built it is built with the join.

**3. The limit lives in three places: one that fails, and two that are records.**

*(This heading read "and none of them is only prose" until 2026-08-27. That was true of the
version ordering a `NOT_REACHED` object and false the moment the correction above replaced it with
prose — the fix honored ADR 0040 ruling 9 and dissolved the mechanism this ruling existed to
create, leaving ruling 6's declined-row test as the only limb that fails. Restated on the re-grill;
see the addendum.)*

- **Prose beside the row it belongs to, and [#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535)
  is told this row's text.** `research_ledger.py` holds its limits in prose and `#535` owns the
  migration of all of them into one object; a row added here goes into that ticket, not into a
  new object built for one row. This is
  [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
  ruling 9's arrangement taken whole — *"the narrowed limit lands as prose here; `#535` stays the
  object's owner and is told the new text"* — and it is what
  [ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
  ruling 9 and
  [ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
  ruling 11 both require. **A comment on `#535` carrying this row's text is part of this ticket's
  close, not something that follows it.**
- **A named re-open trigger inside that row** (ruling 4).
- **A rider on #498.** When `STATED-EXPIRY` lands, the agent filling it in on the C.F.R. record
  reaches `none stated` — correct under ADR 0040 ruling 1, and one inch from re-deriving this
  whole ticket as a fresh finding. The skill's field documentation names the C.F.R. case as *the
  known instance where `none stated` is the right answer*. ~~**#534 does not block on #498**; this
  is a rider carried on that ticket, and the other two land alone.~~ **Reversed by ruling 7 on the
  re-grill of 2026-08-27: the prose limb is unwritable until `STATED-EXPIRY` exists, so it and this
  rider are one blocked piece. Ruling 6's test is the piece that lands alone. See the addendum.**

**4. The trigger is the baseline and never an invented threshold.**

```text
re-open the day a tree-wide count returns a SECOND citation on a published reissue
cadence, or a SECOND distinct publisher in that bucket.
measured 1 and 1 on 2026-08-27, at f9a501c, over 22 citations in 4 claim ledgers.
```

A drafted `3 sources or 2 publishers` was refused as **a value named at an edge** —
`SPACE_ADVANCE_FRACTION`'s recorded failure, and
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s rule: ground a cut point
where the corpus offers one, refuse to invent one where it does not. The corpus offers 1 and 1.
The baseline is arithmetic on what is there; a `3` would be a guess at what rate the clinician
would care at.

Its cost is named rather than discovered: it is more sensitive, so the next C.F.R. citation
anywhere re-opens the question and may be shrugged at. That is the right direction to be wrong
in — a re-open costing one re-read beats a limit that silently outlives its evidence.

**This limit is declared and structurally cannot fire, and that is said out loud.** The praised
form in this repo is the limit that schedules its own review — `differential_scan`'s tripwire
fired on its own words the day a committed run falsified its row. **That form is unavailable
here**, for two independent reasons: a test cannot re-derive the count, because the denominator
lives in `scratch/` which never reaches CI and never will; and a command-side count would have to
decide which reference strings name a source on a published cadence, which is the heuristic over
reference strings the ticket's *What must not come out of this* forbids in as many words. So the
re-open trigger is a person, and ruling 3 is about putting it where the right person trips over
it.

**5. The corrected denominator is carried to #498 as a recorded finding, and ruling 3 of ADR 0040
stands.**

#498's record must carry the true figure, because the next session to grill field contention
will reach for it and ADR 0040 is where it will look. Leaving a live ticket resting on a figure
this session proved wrong is the shape `CLAUDE.md` names as the one a sweep most often misses.

**ADR 0040 ruling 3 was re-examined against 1-in-22 and survives on its argument rather than on
its rate.** An optional field leaves the filed defect where it is, and that is true at any rate —
at 1-in-22 an optional field is *more* likely to be skipped, not less, so the corrected figure
strengthens mandatory rather than weakening it. What follows from the correction is that **21 of
22 sourced records will write `none stated`**, and that sentinel-dominant shape is a real cost
for #541 to weigh; it is recorded here, not ruled on.

**Recording a correction is not changing a ruling.** The distinction is the clinician's standing
one and it is why this is ruling 5 rather than a re-opening of ADR 0040.

**6. The refused cadence table is recorded as a failing test, not as a paragraph.**

**A prose edit to a rejected alternative fails nothing** —
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s lesson. The cadence
table is the option the next session re-proposes, because it looks obvious the moment somebody
sees `(2025)` in a citation and knows Title 42 recodifies each October. An ADR paragraph saying
*we weighed it and it false-alarms* is an argument, and arguments lose to fresh intuition.

`tools/test_research_ledger.py`'s `TheDeclinedParserRowsFireOnCorrectOrders` is the precedent and
it is named by `CLAUDE.md` as the transferable half of
[#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300)'s ruling: implement the
declined row and run it, so re-proposing costs a failing test rather than an argument.

So the build implements the cadence row — *edition year in the citation is behind the current
annual edition, therefore a finding* — and runs it over correct C.F.R. citations written in the
test whose sections are unchanged across editions. Every one fires; the test asserts they fire;
its name says why. It lands in the same module gaining `NOT_REACHED`, so the row and its
demonstration sit together.

**Its ceiling is declared and is the precedent's own.** The citations are written in the test and
measured against no corpus, because a finished ledger lives under `scratch/` and cannot be a
fixture. **The claim is a floor on the false-alarm shape and never a rate.**

## What none of this reaches

**Whether the cited section still says what the draft claims it says.** That is the refutation
pass, and ADR 0042 ruling 5's authenticated-route attempt is where it is answered, not here.
Nothing in this record reads a regulation.

**A legal citation's year against its entry's year.** ADR 0039's declared limit stands untouched;
ruling 1 above explains why closing it would not have reached this ticket anyway.

**Any source class the corpus does not yet cite.** The measurement is 22 citations in 4 ledgers
on one day. Ruling 4 is the whole of the arrangement for that.

**Whether a run will fill in a field it is given.** Ruling 5 records the sentinel-dominant
shape `STATED-EXPIRY` acquires under the corrected denominator and rules nothing about it.
**It has no ticket**, and it is deliberately not filed under
[#541](https://github.com/mshamblin5150-code/clinical-skills/issues/541), whose subject is the
authenticated-route asymmetry rather than the ledger's field budget. The field-count datum is
#541's; the fill-rate question is not.

## Addendum, 2026-08-27 — the re-grill after the correction

The correction above was itself grilled, because replacing an object with prose is not a neutral
edit: it changes what holds the limit. **Two decisions, ruled by the clinician on that date.**

**7. The prose limb is blocked on [#498](https://github.com/mshamblin5150-code/clinical-skills/issues/498),
and ruling 3's "does not block on #498" is reversed.**

The limit's content is *`STATED-EXPIRY` does not carry a cadence-derived date*, and
`grep -c "STATED-EXPIRY" tools/research_ledger.py` returns **0** — the field is unbuilt tree-wide.
So limb 1 is not merely unenforced today, it is **unwritable** today: a prose limit about a field
the module does not have cannot be read in context and cannot be checked in any context. The
rider on #498 was always going to land there; the prose now lands with it, in one change rather
than two.

**Nothing is lost by waiting**, which is the whole reason this is cheap. #535 already carries the
row's text and its measured trigger, delivered as part of this ticket's close under ruling 3, so
the finding is on the tracker whether or not the prose ever lands.

The declined option was to **bind the docstring without building the object** — a test asserting
`research_ledger.__doc__` names this limit. It is refused: it is half of #535's mechanism arriving
through a side door, and binding one prose limit among the module's many is *these are the limits*
in a different hat, which is the objection ADR 0040 ruling 9 raised against the object itself.

**8. It splits, and the test lands first.**

- **A** — ruling 6's declined-cadence test. Depends on nothing #498 builds: no field, no ledger, no
  corpus, only citations typed into `tools/test_research_ledger.py`. **Buildable now.**
- **B** — the prose limb and the #498 rider. Blocked by ruling 7.

**#534 does not close until B lands**, on
[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
ruling 7's arrangement for the same shape.

**A goes first because it has the shortest half-life.** Re-proposing the per-publisher cadence
table costs nothing today and costs a failing test once A lands, and the whole argument of ruling 6
is that a rejected alternative recorded only in prose loses to fresh intuition. Holding A until
#498 ships would leave the table re-proposable for exactly as long as that takes.

**The declined option was to close #534 and move the prose limb to #498 outright.** Refused: this
record is *why the cadence table is refused*, and a later session asking that question would find
the expiry-field ticket instead of this one.

## Second addendum, 2026-08-27 — ruling 7's ground expired the same day, and piece B's limit is a row

**Ruled by the clinician on 2026-08-27**, during the exhaustive tracker sweep from
[#538](https://github.com/mshamblin5150-code/clinical-skills/issues/538)'s grilling. **Ruling 7
stands as ruled and is not rewritten.** What follows is what changed underneath it.

### The finding is that one ground carried three refusals, and it is spent

Piece B1 forbade `research_ledger.NOT_REACHED` on the stated ground that *three ratified records
refuse a one-row object in this module by name*. That is true, and it is not what those records say.
All three refuse the same narrower thing, in the same words:

- [ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
  ruling 9 — *"Introducing the object with one row **while five stay in prose** is ruling 7's
  numerator-without-denominator one level up."*
- [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
  ruling 9 — *"introducing the object with one row **while the others stay in prose** reads as* these
  are the limits *— a numerator with no denominator."*
- [ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
  ruling 11 — *"the reason is specific to this module. It was made about `research_ledger`, **which
  holds five prose limits**"* — and it then **built** the object for `discussion_reply_scan`, on the
  ground that one row there is the whole population.

**None of them refuses a row in a populated object.** ADR 0050 ruling 11 is the proof, because it
went the other way on the same question for a different module. Ruling 7's own declined option
inherits the identical ground — *binding one prose limit among the module's many is* these are the
limits *in a different hat*.

[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 1 builds `research_ledger.DECLARED_LIMITS` **whole**, over a population derived by reading the
module end to end. After it, appending one row is not a numerator without a denominator, and the
ground every one of these refusals rests on no longer describes the module.

### What is ruled

**1. Piece B's limit lands as a row in `research_ledger.DECLARED_LIMITS`, not as prose.**

ADR 0053 ruling 1 had already ruled this and named the ticket — *"#498, #500 and **#534's piece B**
each own a limit that is not true yet [...] each ticket appends its row when it lands [...] piece B
stops being prose no test binds and becomes one row appended to a bound object, which is what ruling
7 wanted and could not have. **#534 is told**."* **#534 was not told**; its B1 still said prose for
the whole of that day, and this addendum is what tells it.

**A one-row object is still refused.** The prohibition survives exactly as written and only its
scope was ever in question: do not create the object *for this row*. Appending to one built for the
module's whole population is the thing the three records were distinguishing all along.

**2. The row is unconditional, and #534 gains `blocked_by #535`.**

The declined option was to make it conditional — a row if
[#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535) has landed, prose if not.
Both #535 and #498 carry **zero** blockers and either can land first, so a conditional instruction
makes the build outcome depend on merge order: **one specification, two different trees**, and the
prose branch is what ADR 0053 ruling 1 calls *prose no test binds*. This repository has [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)
for a result that depends on which branch merged first.

**It deepens no chain and costs no waiting.** Piece B cannot start until #498 lands whatever
happens; #535 is buildable today with nothing in front of it. The edge records an ordering that was
already the likely one.

**This does not reopen what ADR 0053 ruling 1 declined.** That ruling refused to block **#535** on
the three tickets queuing rows, calling it *a deadlock dressed as thoroughness*. This is the
opposite direction — #534 waiting on #535 — and closes no cycle.

**3. The two-direction bind returns, and that is a consequence rather than a new requirement.**

The `Done when` had required it, was rewritten hours earlier to drop it as the honest price of a
prose limit, and gets it back because the row is in an object again. It is ADR 0053 ruling 10's
point-at-and-copy-no-row bind, not a new mechanism. Under ADR 0053 ruling 8 the row is a `key`, a
`limit` and an `evidence` disposition; under ruling 7 this one is a **declared reading**, because
ruling 7 of *this* record already established the trigger cannot be re-derived by any test — the
denominator is under `scratch/`, which never reaches CI — so no handler and no positive control is
constructible for it, and the row says so.

### What this does not reach

**Whether ruling 7's blocking of piece B on #498 still holds.** It does, untouched: the limit's
content names a field the module does not have, and that is unchanged by where the limit is stored.

**Whether the other two queued rows — #498's and #500's — take the same correction.** Both are named
by ADR 0053 ruling 1 in the same sentence as #534, so the same reasoning appears to reach them, and
neither was examined here. Not asserted, and not filed as a finding, because a claim about two
tickets nobody read is the shape this sweep spent the day removing.

*(Ruling 7 is not rewritten. This addendum records that its stated ground became false on the day it
was written, and what the clinician ruled in its place. On
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms.)*
