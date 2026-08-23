"""Grade the research ledger a ``practicum-case-study`` run writes before it drafts.

    python tools/research_ledger.py <a ledger file> [--draft <a draft .md>]
        [--evidence <the evidence dump>] [--show]

[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) is this.
The skill used to write an unsourced claim into the body and list it in the
``PROPOSED`` block with **verify this** against it; the clinician's ruling of
2026-08-18 is that such a claim gets **researched** instead, one agent per claim,
in parallel. **The ticket asks for a mechanism rather than an instruction**, and
the mechanism is a written record with a grader in front of it: the fan-out
produces one ledger record per claim, and this refuses the ones that did not
answer the question they were sent to answer.

**The ledger is the mechanism, not the parallelism.** A harness with no subagent
tool works the same briefs serially into the same file, and the grader cannot tell
the difference -- which is the point. ``SKILL.md`` says so where it names this
command, and a test here asserts that sentence is still there.

**One writer, and the claim list goes in before the agents go out.** N agents
appending to one Markdown file lose records to each other, and this tool has no
expected count to measure a short ledger against -- so three records where eight
claims were sent out would grade clean and the run would draft.
[#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s
shared-artifact channel, with lost writes where that ticket has leaked reads.
**Writing the headings first is what closes it rather than a new row**: a heading
whose answer never arrived carries no ``STATUS``, and a record with no ``STATUS``
already fails. ``skills/practicum-case-study/SKILL.md`` step 3 orders it that way
and a test below pins the consequence.

**The record shape**, one per claim, in a Markdown file under ``scratch/``::

    DATE: 2026-08-19

    ## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.
    STATUS: sourced
    SOURCE: peer-reviewed
    REFERENCE: Abbassi-Ghanavati, M., Greer, L. G., & Cunningham, F. G. (2009).
        Pregnancy and laboratory studies. Obstetrics and Gynecology, 114(6), 1326-1331.
    RESTATEMENT: The table gives a third-trimester white cell range of 5.6 to
        16.9 x 10^9/L in normal pregnancy.
    RECENCY: nothing newer - searched 2026-08-19; no later reference-range table
        for pregnancy exists, and obstetric texts still cite this one.
    RESOLVED: https://doi.org/10.1097/AOG.0b013e3181c2bde8 - read 2026-08-19
    PAGE-YEAR: 2009 - stated on the article's masthead and in the journal citation.
    REFUTATION: stands - the volume, issue and pages match the publisher's landing
        page, and the third-trimester row is on page 1327.

A field's value runs to the next field line or the next claim, so an APA entry may
wrap the way an APA entry wraps.

**What it checks, and which ruling each row belongs to.**

*#214, the fan-out's own contract:*

- **Every field is present and carries something.** A record missing its
  ``RESTATEMENT`` is a citation nobody checked against the claim.
- **``STATUS`` is one of two branches**, and an unrecognized one is a **failure**
  rather than a counted curiosity. This departs from ``specificity_scan.py``'s
  third-branch rule deliberately: there the keyword selects a message, here it
  selects **which tests run**, so a record reading ``STATUS: pending`` is graded on
  nothing at all and reports as clean.
- **``STATUS: unsourced`` carries a reason.** That is ``specificity_scan.py``'s
  substance test and it is here for its reason -- nobody writes *"searched PubMed,
  IDSA and UpToDate, nothing addresses this"* without having looked, and anybody
  can write ``unsourced``. An unsourced record is **not a failure**: the skill
  routes it to ``PROPOSED``, and out of the document entirely where it is a number.
  The count is printed so the run knows how many did.
- **An unsourced record may not carry a ``REFERENCE``.** The two statements
  contradict each other and nothing else in the file can tell which was meant.
- **The restatement is not the claim again.** Normalized equality only, because
  anything looser is a guess about paraphrase. This is the cheap half of the limb
  the ticket calls the one that matters most.
- **A claim carrying a number gets a restatement carrying a number.** ``A white
  count of 15,000 ...`` answered by *"the source discusses leukocytosis in
  pregnancy"* is the wrong-citation-survives-review failure at its most expensive,
  and it is the one form of it a string test can reach.

*#215, the recency rule as amended:*

- **``RECENCY`` is one of four dispositions**, and an unrecognized one is a failure
  for ``STATUS``'s reason rather than ``SOURCE``'s: it gates the row below it, so a
  record reading ``RECENCY: probably fine`` is never measured against the window at
  all. **This row was missing from the first version of this module** and was found
  by review, which is the same argument arriving at the field it was first written
  for and not at the field beside it.
- **Past five years, the record says why it stands.** ``nothing newer`` or
  ``guideline in force``, and nothing else excuses it. The first version of this
  rule cut a correct 2018 refutation and left a 1932 teaching standing by default;
  what the rule refuses is a claim that is old **and superseded**.
- **The excuse carries a reason**, on the same footing as the status. *The run must
  have looked, and must say so* is #215's own wording, and a bare ``nothing newer``
  is the assertion without the looking.
- **A reference states a year, unless an excuse stands in for one.** ``n.d.`` is
  legitimate APA, and the recency rule cannot be applied to it -- a row that could
  not be graded reads exactly like a row that passed. **Refusing it outright would
  be a rule the clinician never made**, so the escape hatch is the one he did make:
  an undated source carrying ``nothing newer`` or ``guideline in force`` with a
  reason stands, and one carrying neither is refused.

*#231, the citation's truth half:*

- **``RESOLVED`` is a URL or a bare DOI, and it says when it was opened.** The field
  exists to put a specific in front of a reader; *"on the society website"* is not
  one, and neither is a locator with no date beside it. The date is read off the
  word ``read`` or ``retrieved`` rather than off any digits in the value, because a
  URL is full of digits and one being date-shaped is not the agent saying when it
  looked.
- **A source cannot be read after the paper was written.** That is the second row
  measured against ``DATE``, and the second one a dateless ledger loses.
- **``PAGE-YEAR`` and ``REFERENCE`` agree about the year.** One rule in three rows:
  a page year that states none against an entry that states one, a page year that is
  a year and nothing else, and a page year that is not the entry's. **An ``n.d.``
  entry beside a page carrying no date is the agreeing case and passes** -- refusing
  it would refuse legitimate APA, which is the mistake ``UNDATED_REFERENCE`` was
  corrected for once already.
- **``REFUTATION`` is one of three dispositions with a reason after it**, and an
  unrecognized one is a failure for ``STATUS``'s reason: it gates the row below.
- **``refuted`` is a failure and not an outcome.** Unlike ``unsourced``, which the
  skill routes to ``PROPOSED`` honestly, a refuted record is a **false citation
  sitting in the ledger**: the run rewrites it or writes ``unsourced``, and never
  drafts from it.
- **``paywalled`` passes, and it is the clinician's ruling of 2026-08-19 on the
  ticket's decision 4.** A locator that 404s or names a document search cannot find
  is ``refuted``; a live page whose title and authors match, body behind a
  subscription, is ``paywalled`` -- the URL resolving to the right document is
  itself evidence it exists, which is most of what a fabricated citation cannot do.
  **It is the weakest disposition that passes**, so ``survey`` counts it on its own
  line: a set of citations all behind a wall has been checked far less than exit 0
  suggests. Failing them instead would refuse every UpToDate record, which is nine
  in ten of this corpus and the reason no resolver was built here at all.
- **A refutation that is the restatement pasted back** is the first agent
  re-asserting rather than a second one checking -- ``RESTATEMENT_ECHOES_CLAIM``'s
  trick one level up, and the only part of the pass's independence a row can reach.
- **An unsourced record carries none of the four citation fields.** That is
  ``UNSOURCED_WITH_CITATION_FIELD`` widened from one field to four: a locator on a record
  that says it found nothing is the same contradiction, and it was passing.

**#289, and it was the only thing here that read anything but the ledger until
#298 put ``--evidence`` beside it.**

- **Every drug the run chose a number for has a claim record.** The rows above
  grade the records that exist, and this module has **no expected count of its
  own and says so** -- so a dose nobody entered as a claim is invisible to every
  one of them. That is exactly what happened: a run recorded in its own
  ``REFUTATION`` field that the treatment topic was unavailable, wrote specific
  doses citing it anyway, and ``research_ledger``, ``reference_scan`` and
  ``checks_ledger`` all exited 0. **A prescription is a dose**, which makes it
  the highest-stakes claim in the document and the one nothing reached.
- **The set comes from the draft rather than from a table in here**, which is
  the one way ``checks_ledger.py``'s expected-set arrangement transfers: there
  ``skills/practicum-case-study/SKILL.md`` step 9's table fixes the checks, and
  here the run's own Rx blocks fix the drugs. ``--draft`` is what supplies it.
- **A record is required for every drug the run chose a number for**, ruled by
  the clinician on 2026-08-19 against the alternative of every drug with a table.
  A home medication continued unchanged at the patient's own dose is a number the
  patient arrived on, and a row **declaring** itself ``Continued home
  medication:`` is exempt. **Declared and never inferred**: an unlabeled row is
  graded, so the direction the rule fails in is toward asking for a record.
- **An order stating a dose is answered by a claim stating a number**, and that
  is a chain rather than a second check: where the claim carries a number,
  ``NUMERIC_CLAIM_UNQUANTIFIED`` above already forces the restatement to answer
  with one. So the two rows compose into *the table's dose reaches a source*.
- **A prescription table with no readable drug row is a finding**, not a table
  subtracted from the set in silence.

**It never compares the numbers, and that is #289's own closing prohibition.** A
dose depends on indication, weight, renal function, pregnancy and route, so a row
refusing a correct dose for the wrong reason is #215's defect a fourth time --
and #215 has already produced three. The reachable property is whether the dose
was **sourced**, never whether it is right: a record carrying a *different*
number passes these rows. There is no drug table here and there will not be one.

**Without ``--draft`` those rows do not run, and the report prints ``not
graded`` against them rather than ``0``.** That is
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling
arriving at the one grader here that reads two files, and it is why
``Scan.prescriptions`` is ``int | None`` rather than an ``int`` starting at zero:
a zero beside a row that never ran is indistinguishable from a row that passed,
which is the shape the whole ticket is about.

**``DOSE_NOT_CLAIMED`` asks for a number and cannot ask for *the* number**, and
that limit is documented rather than tightened, on ``UNRESOLVABLE_LOCATOR``'s
terms. Any digit in the claim heading satisfies it, so a heading carrying a year
and no dose passes -- and narrowing it is not available, because the heading is
written in the source's own terms by design and this module's own
``NUMERIC_CLAIM_UNQUANTIFIED`` exists because a claim about 15,000 cells is
rightly answered in ``10^9/L``. **It only ever weakens the weaker half of a
pair**: the row says *this claim was not asked numerically*, never *this dose is
sourced*, and it is one row of three. Pinned by a test so it is a known behavior
rather than an accident.

**One drug row is one drug, and nothing here makes that true.** ``_drug_of``
takes the leading token, so a row welding two orders together --
``doxycycline 100 mg PO BID x 7 days and metronidazole 500 mg PO TID x 7 days``
-- is one drug to this parser, and the second drug's dose is invisible to all
three rows. ``style.md`` section 8 says *one table per drug* and this grades
nothing about that, so **the run picks the denominator**, which is
[#127](https://github.com/mshamblin5150-code/clinical-skills/issues/127)'s shape
arriving in a set built to be an expected one. **It is not narrowable here**:
splitting a drug row on ``and`` would cut ``normal saline and potassium
chloride``, and telling two drugs apart needs a drug vocabulary, which is
exactly the table #289 forbids. Written down and pinned by a test rather than
guessed at, on ``UNRESOLVABLE_LOCATOR``'s terms, and filed --
[#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300).

**Ruled a reading rather than a row on 2026-08-20, and the row stays exactly as
declared above.** #300 offered three answers and the clinician took the third:
``skills/practicum-case-study/SKILL.md`` step 9's ``the Rx blocks`` row asks its
reader for the welded row by name. **That row was already the right reader and
was simply not told** -- its brief has always asked whether every drug in the Plan
has a table, and a welded pair is precisely a drug in the Plan without one. **No
parser moved**, which is the durable half; where the wording landed is those
files' to say rather than this docstring's.

**The declined parser row is refused on a measurement, and the measurement is a
test rather than a figure here.** Both forms the ticket priced fire on correct
orders, and they do not fire on the same ones: *a second unit-bearing token after
the first dose* takes a taper and an infusion rate as well as a titration and a
repeat dose, and narrowing to a conjunction between the two doses drops the taper
and keeps the rest. **The narrowing helps and does not close it**, which is the
finding rather than the count. Narrowing past what is left needs a closed set of
continuation
verbs, and a verb missing from that set is a false alarm on a correct order,
which is **the same failure direction as the drug table #289 prohibits**.
``test_research_ledger.TheDeclinedParserRowsFireOnCorrectOrders`` implements both
forms and runs them, so re-proposing one costs a failing test rather than an
argument.

**What that buys is a brief and not a gate**, which is the standing price of the
option and is named rather than left to be found: that row's ``clean`` is not one
``checks_ledger`` requires to say what it walked --
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255) ruled
which rows do and this is not one -- so a bare ``clean`` from a reader that
skimmed still passes.

**What it cannot reach, and the sharpest limb is a claim about coverage rather
than about a dose.** Whether the dose is right for this patient, whether the
record that names the drug sourced its *dose* rather than its indication --
record 1 of the run that produced #289 sourced the **disposition**, and would
have failed these rows only because it named no drug at all -- and whether the
drug row and the ``Sig`` agree.

**A reader is looking at the number since
[#299](https://github.com/mshamblin5150-code/clinical-skills/issues/299), and it
is not this module.** This paragraph said ``skills/practicum-case-study/SKILL.md``
step 9 sends a reader at the Rx blocks *for exactly that reason*, and that was
false: that row briefs a reader on whether every drug has a table -- including,
since [#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300),
whether a drug row welds a second drug into it -- whether every ``Sig`` ends in
an indication and whether the prose block is there, and on no number at all -- and ``checks_ledger.SUBSTANTIATED_CLEAN`` leaves it out, so a
bare ``clean`` on it passes. So the residue was declared covered and covered
nowhere -- this
ticket's own shape arriving in the fix for it, found by the spec axis of
``/code-review``. It is ``the dose against the record that sourced it``, its own
row of step 9's table and of ``checks_ledger.EXPECTED_CHECKS``, and one of the
rows ``checks_ledger.SUBSTANTIATED_CLEAN`` names -- so a bare ``clean`` on it
fails.

**A reader and not a row, ruled by the clinician on 2026-08-20, and the ground is
that the false-alarm rate could not be grounded rather than that it would be
high.** A string test can reach *the table's number appears in the record naming
that drug* and nothing further, so it fires on ``1 g`` against *1000 mg* and on
``q24h`` against *once daily* -- the unit problem ``NUMERIC_CLAIM_UNQUANTIFIED``
above already refuses to touch, arriving one level down. And when it was ruled
there was **no pair in the tree to measure it on**: the only ``practicum-case-study``
run **with a claim ledger** predated these rows, so every one of its
prescriptions reached no claim
record at all and not one drug-row-and-record pair existed anywhere. **How
many that was is deliberately not stated**, here or in the two other places
this paragraph is written: it counts a run under ``scratch/`` that nothing
committed re-derives, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143), and
the three copies disagreed about it the day they were written.
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
precedent is that a cut point is grounded where the corpus offers one and refused
where it does not. **The prohibition is unchanged either way**: the question is
whether the document's number and the record's number are the *same* number,
never whether either is right. **A clean scan is not a checked prescription.**

**``--evidence`` grades what the run says it read against what it was handed**
-- [#298](https://github.com/mshamblin5150-code/clinical-skills/issues/298),
ruled by the clinician 2026-08-20. A run recorded in its own ``REFUTATION`` field
that the treatment topic was missing from the companion evidence and cited it
anyway; ``--draft`` closes that only where the missing topic is a **drug**, and
this closes it wherever the topic is **cited**.

- **The grounding is #231's and it is what scopes the row to UpToDate.** That
  ticket ruled the database subscription-gated -- a fetch reaches a login wall
  rather than the topic page -- so an UpToDate topic the dump does not carry is
  one **nobody could have opened**. The clinician hands topics over wholesale, so
  the dump is the whole of what was read. A journal article, a society guideline
  or a government page the dump lacks is ``skills/practicum-case-study/SKILL.md``
  step 3's ordinary case: a claim record exists *because* the evidence did not
  cover the claim, and a row firing on those would be #215's defect again.
- **The topics the dump merely refers to are not graded, and that is the ruling
  rather than an omission.** A rendered dump cross-references far more topics than
  it carries -- by more than an order of magnitude in the one this was measured on
  -- which is the ordinary case #298's own *What must not come out of this*
  forbids firing on. Ranking them does not rescue it either: the reference counts
  decay smoothly with **no plateau anywhere**, so any cut is a value named at an
  edge, which is ``guidelines_extract.SPACE_ADVANCE_FRACTION``'s recorded failure
  and #97's objection. **No threshold is built and none is available.** What is
  graded is the join. **Every figure behind that is counted against a file under
  ``scratch/``, so nothing committed re-derives one and the next article the
  clinician pastes moves them all; they are stated on #298 and nowhere in this
  tree**, on #143's terms.
- **A body is recognized by its ``Authors:`` masthead and never by a heading.**
  #298 decision 2 proposed reading a title as a heading and that is not
  implementable against the artifact it describes -- the rendered dump carries no
  headings of any kind. **Measured before it was believed**: nearly every body the
  real dump carries joins a ``See "..."`` cross-reference exactly under this rule,
  and the count is #298's to state.
- **No escape hatch, and it was asked rather than assumed.** If an UpToDate topic
  is worth citing it goes in the dump, and the remedy for a finding is one paste.
- **The draft's reference list is parsed by ``reference_scan`` and not by a second
  reading in here**, on ``REFERENCE_HEADING``'s precedent and #108's.
- **An entry this cannot read is a finding, and for a row with no escape hatch
  that limb *is* the hatch.** ``uptodate_topic`` recognizes a topic only from the
  database element, so an entry dropping ``UpToDate.`` was invisible to the row
  **and** to the population row -- and ``reference_scan`` reports nothing on it
  either, so four characters removed from an entry took the topic out of the join
  with nothing red anywhere. ``UNREADABLE_UPTODATE_ENTRY`` keys on the
  **locator's host** and is ``UNREADABLE_DRUG_ROW``'s argument one row over: a
  citation this cannot read is never one subtracted from the set in silence.
  Found by a tracker-sweep subagent and re-derived in both directions.

**What that leaves is an entry naming neither the database element nor an
UpToDate locator**, which is invisible to both rows and to the population count,
so the report cannot tell *cited none* from *cited one unreadably*. It is not
narrowable: with neither element there is nothing distinguishing such an entry
from a journal article, and guessing would fail a correct one -- #215's defect,
which the scope limb above exists to avoid. Documented rather than tightened, on
``UNRESOLVABLE_LOCATOR``'s terms, and it only ever weakens the weaker half: the
rows say *this citation did not reach the dump*, never *this citation is good*.

**What ``--evidence`` cannot reach is a claim that rested on a missing topic
without citing it.** The join is on a citation, so a threshold, a screening
interval or a discriminator taken from a topic nobody read and written with no
reference is invisible to this row and to every other one -- which is the residue
#298 names and does not close. **A clean scan is not a sourced document.**

**#215's first limb reaches no row here, and that is deliberate.** *Within two years
is the target* is a target: a ``current`` disposition on a three-year-old reference
is not a defect, and grading it would refuse what the ruling merely prefers.

**The rows sit in four helpers, and the branching sits in ``record_findings``.**
[#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242), which filed
one 129-line grader against the four scanners that keep one -- and did not check
``reference_scan.py``, the only sibling with a comparable row count, which had
already split five ways. What could not move is the control flow: a record with no
recognized ``STATUS`` is graded on nothing below it, and an ``unsourced`` one on a
different set entirely. **A record's findings are sorted by ``KINDS`` now** rather
than appended in call order, so which helper a row lives in is invisible and the
seam can move again without ``--show`` changing shape. **Within a record**, which is
the honest width: ``survey`` concatenates one sorted list per record, so a ledger's
findings are grouped by record rather than globally sorted -- and should be, since a
reader wants one record's rows together.

**What the split makes visible is which rows need the date.** Two helpers take
``as_of`` and each spends it on one row -- ``STALE_UNEXCUSED`` and
``READ_AFTER_DATE`` -- so the exit-2 banner's claim about a dateless ledger is
readable off two signatures instead of off the whole grader. A test drives one ledger
both ways and asserts the difference is exactly those two.

**``UNRESOLVABLE_LOCATOR``'s own limit, since #242.** A DOI is a registrant prefix
and a free-form suffix, so ``pp. 10.1327/1400`` is a page range wearing the shape
and passes the row. It is not narrowable -- a real bare DOI arrives with no scheme
and no ``doi:`` prefix to key on -- and it only ever weakens the weaker half of a
pair: the row says *this is not a locator*, never *this locator is good*, and
``UNDATED_READ`` and ``REFUTATION`` still ask when the page was opened and what was
found there. Documented rather than tightened, and pinned by a test, because every
other limit in this module is written down and this one was not.

**What it cannot reach, and this is most of the ticket.** Whether the source is
reputable, whether it says what the restatement says it says, and whether the
numbers agree. **The last one is not an oversight**: the restatement is written in
the source's own terms *by design*, so a claim about 15,000 cells is rightly
answered with a range in ``10^9/L``, and a test comparing the digits would refuse
the correct answer. Judging a restatement against its source is a reading, and a
clean scan here is not a walked claim.

**Nor does it reach the document.** *A claim that survives the fan-out still
unsourced does not go in the body* is #214's rule and it is about the draft, which
this never sees -- so a ledger of nothing but well-formed ``unsourced`` records
exits 0, and that 0 means the records are honest rather than that the paper is. The
count is printed for exactly that reason, and
``skills/practicum-case-study/SKILL.md`` step 9 walks it.

**#214's open question 2 is answered on
[#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231), and the
answer is that nothing here fetches anything.** The format half already had a written
standard from #211 -- ``skills/practicum-case-study/reference/apa7.md``, walked by
``skills/practicum-case-study/SKILL.md`` step 7 and by
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218).
For the truth half the ticket proposed ``threshold_sheet.py``'s two-tier arrangement,
a resolver opting into the network and skipping with a banner. **Two findings killed
it.** UpToDate **dominates** this corpus's references and is subscription-gated, so a
fetch reaches a login wall rather than the topic page ``apa7.md`` section 2 takes the
date element from -- every such entry would fail outright, or pass on a 200 from a
login form, which is the silent-pass shape this whole directory exists to refuse.
**The size of that dominance is stated once, in ``reference/style.md`` section 10,
hedged and against a gitignored set that nothing committed re-derives.** And
**the clinician hands the topics over wholesale**, so wherever a source is in the
evidence dump there was never anything to resolve.

**So the checking moved to where the reading already happens.** The agent that
researched a claim was on the page: it records what it opened and when
(``RESOLVED``), and the year the page itself carries and where (``PAGE-YEAR``). A
second agent, briefed to **refute** rather than to confirm -- because an agent asked
*is this right?* says yes -- records what the attempt found (``REFUTATION``). All
three are graded here, offline. **No tool in this repo touches the network**, which is
the ticket's decision 1 settled by making it unnecessary rather than by opting out of
it.

**What that buys, and what it does not.** ``RESOLVED`` and ``PAGE-YEAR`` narrow the
hole rather than closing it -- an agent can write a URL it never opened -- but they
force a commitment to specifics a reader can be caught on in one click, where a
correctly formatted APA entry is checkable only by going and looking. The refutation
pass is the only **verification** in the arrangement -- **and it does not happen
here.** The pass is a second agent; this module refuses a record where the pass did
not answer, answered in a third word, or answered by pasting the restatement back.
**No row here can see that the refuter was a different agent**, or that it opened
anything: that is an instruction, and *what a written instruction cannot do is fail*
binds its own successor as squarely as it bound #214.

**Per record, when the source was read is ``RESOLVED``'s own date; what there is
deliberately no second date for is the ledger.** #231 admired ``threshold_sheet.py`` recording *the date tier 2 last really
ran*, and the difference is that tier 2 there is skippable and months stale by
design, while the fan-out and the refutation both run in one sitting before a word
is drafted. ``RESOLVED``'s date is the **research** agent's, and it is bounded above
by ``DATE`` and **not below** -- a read date years before the paper is incoherent and
passes. Bounding it below would need a window nothing here grounds, which is
``filled_vitals_census.py``'s reason for grading three rows and counting five.

**This module states no opinion about whether a source is reputable or whether it
says what the restatement says it says.** What it checks is that a year is *stated*,
that two records *agree* about it, and that the pass sent to knock the citation down
came back and said something. It opens nothing.

**Counts only by default**, on ``specificity_scan.py``'s and ``block_scan.py``'s
terms and for their reason: the ledger lives under ``scratch/`` and a claim is
transcribed from faculty material about a patient. **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** -- 0
clean, 1 for a violation, **2 for every way of not having scanned**: no argument,
no file, no ``## CLAIM:`` record in it, **no ``DATE:`` header**, a ``--draft``
naming a file that is not there, a draft carrying **no readable prescription
table**, an ``--evidence`` naming a file that is not there, and an evidence file
carrying **no topic body at all**.

**Two of those limbs are the ones that matter, and they are the two where a row
would otherwise print a zero it never earned.** The window is measured against
the day the paper is written, so a ledger with no ``DATE`` was never measured by
#215's rule at all and a clean report would read as though it had been -- **two
rows need that date**, #215's window and #231's read date, both comparing to
``DATE``. And a draft whose prescriptions are written in a shape
``read_prescriptions`` does not read would report #289's rows as zeros and look
like a document whose every dose reaches a record, which is
``differential_scan.py``'s reasoning arriving at a second file.

**The evidence limb inverts that and is the sharpest of the three.** A dump
``carried_topics`` cannot read carries **no** topic to join against, so every
UpToDate citation in the ledger would fire at once -- a mass false finding rather
than a silent pass, and the one not-scanned limb here whose failure is loud rather
than quiet. So the row is left **ungraded** and prints *not graded*, and the exit
2 is deferred to the tail like its two siblings.

**Returning it early is the defect this module was built having already read
about**, and it shipped anyway: it suppressed every other row's findings and
printed no report at all, which is ``tracker_scan.py``'s recorded corpus-limb
inversion -- *returning 2 before scanning, so a real hit was reported as did not
scan* -- arriving in the one function whose own docstring, in the paragraph below,
states the ordering it broke. Caught by the spec axis of ``/code-review``, and
pinned by a test that drives ``main`` rather than the report, because every test
that had been written for this limb asserted the status and none asserted that
the other rows survived it.

**Where a violation and any not-scanned limb both hold, 1 wins**, on
``differential_scan.py``'s and ``filled_vitals_census.py``'s ordering and for their
reason: returning 2 would file the strongest thing known about the ledger under the
weakest heading. The banner prints either way, so an exit 1 over a dateless ledger
reads as a floor rather than the whole. **The first version of this module returned
2 there**, which is the one place it departed from both siblings without saying so.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import run_grader
import coursework_run
from docx_write import markdown_tables, split_row

# **The draft's reference list is parsed once, by the module that grades it.**
# ``reference_scan`` importing ``docx_write.REFERENCE_HEADING`` is the
# precedent and this is the same argument at the width of the whole list: a
# second reading in here could put an entry where the grader does not, which
# is #108's duplication and the failure ``reference_scan`` records against
# itself. A test asserts the two are one object *and* drives both.
from reference_scan import read_document

# A record opens on a heading. The heading level is free, so the ledger can sit
# under a document heading without the parser caring.
CLAIM = re.compile(r"(?mi)^[ \t]*#+[ \t]*CLAIM[ \t]*:[ \t]*(.*?)[ \t]*$")
FIELD = re.compile(
    r"(?mi)^[ \t]*(STATUS|SOURCE|REFERENCE|RESTATEMENT|RECENCY"
    r"|RESOLVED|PAGE-YEAR|REFUTATION)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
# The day the paper is written. Recency is measured against it and never against
# the clock -- a ledger graded twice a year apart has to grade the same both times.
DATE_HEADER = re.compile(r"(?mi)^[ \t]*DATE[ \t]*:[ \t]*(\d{4})-(\d{2})-(\d{2})[ \t]*$")

# An APA entry states its year in parentheses. ``2019a`` is the a/b disambiguation
# form ``reference/apa7.md`` section 3 requires, so the letter is allowed and dropped.
YEAR = re.compile(r"\((\d{4})[a-z]?(?:,[^)]*)?\)")

# The four source classes #214 names, and nothing else. A fixed vocabulary is
# ``threshold_sheet.py``'s population key for the same reason: a machine can only
# compare strings, and a mis-keyed value is a wrong *word* a reader can see.
SOURCE_CLASSES = ("society guideline", "peer-reviewed", "government", "tertiary reference")

# #215's four dispositions. The last two are the ones that excuse an old source,
# and both have to say why.
RECENCY_CURRENT = "current"
RECENCY_WITHIN_FIVE = "within five"
RECENCY_NOTHING_NEWER = "nothing newer"
RECENCY_IN_FORCE = "guideline in force"
RECENCY_VALUES = (RECENCY_CURRENT, RECENCY_WITHIN_FIVE, RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)
EXCUSES = (RECENCY_NOTHING_NEWER, RECENCY_IN_FORCE)

# #231. A locator is a URL or a bare DOI, and nothing else -- the field exists to
# put a specific in front of a reader, and *"on the society website"* is not one.
#
# **The DOI branch matches text that is not a DOI, and that is documented rather
# than tightened** -- [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242).
# A DOI is a registrant prefix and a free-form suffix, so ``pp. 10.1327/1400 vol``
# is a page range wearing the shape and matches. It is not narrowable from here: a
# real bare DOI arrives with no scheme and no ``doi:`` prefix to key on, so refusing
# the coincidence would refuse the field's own documented form.
#
# **It only ever weakens a row that is already the weaker half of a pair.**
# ``UNRESOLVABLE_LOCATOR`` says *this is not a locator*, never *this locator is
# good* -- nothing here opens anything -- and the value has to carry substance
# before the row runs at all. So the cost is a ``RESOLVED`` full of page numbers
# passing one row, while ``UNDATED_READ`` still asks it when the page was opened
# and ``REFUTATION`` still asks what the second agent found there.
LOCATOR = re.compile(r"(?i)\bhttps?://\S+|\b10\.\d{4,9}/\S+")
# Anchored on the word rather than on the shape, because a URL is full of digits
# and one of them being date-shaped is not the agent saying when it looked.
# ``retrieved`` beside ``read`` because ``apa7.md`` section 4 calls it a retrieval
# date, so a run copying that word is writing the field right rather than wrong.
#
# **The anchor word has to be outside the URL, and the first version was not.**
# ``https://site.org/read/2026-01-02/piece`` matched, so an archive path supplied a
# read date the agent never wrote -- a locator grading itself as dated. The
# lookbehind refuses a word joined to what precedes it, and the separator between
# the word and the date may not be a slash.
READ_DATE = re.compile(
    r"(?i)(?<![/\-\w])(?:read|retrieved)\b[ \t]*[:\-]?[ \t]*(\d{4})-(\d{2})-(\d{2})"
)
# The year a page states, which is not written in parentheses the way an APA
# entry's is -- so this is the bare form and ``YEAR`` is deliberately not reused.
#
# **Restricted to plausible years, and the first version was not.** A bare
# ``\d{4}`` takes the first four-digit token, and ``PAGE-YEAR`` is documented as the
# year *and where the page says so* -- so ``on page 1327, dated 2009`` read as the
# year 1327 and reported a false disagreement against a correct record. A page
# number is not in 1900-2099; a page number that is remains order-dependent, and
# that limit is the reason the field's documented form puts the year first.
BARE_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")

# #231's three dispositions. The brief is to *refute*, so ``stands`` is the outcome
# of a failed attempt rather than the default.
#
# **``paywalled`` is the clinician's ruling of 2026-08-19 on decision 4**, and the
# split it makes is between *could not reach* and *is not there*. A locator that
# 404s, or that names a document search cannot find, is ``refuted`` and fails. A
# live page whose title and authors match, whose body sits behind a subscription,
# **passes** -- the URL resolving to the right document is itself evidence the
# document exists, which is most of what a fabricated citation fails to do.
#
# **It is a weaker check wearing a passing disposition, and that was priced rather
# than missed.** The alternative failed every UpToDate record, and UpToDate dominates
# this corpus -- which is the reason no resolver was built in the first place. What
# the report does about it is count them: a run whose citations are all ``paywalled``
# says so on its own face rather than reading as fully checked.
REFUTATION_STANDS = "stands"
REFUTATION_REFUTED = "refuted"
REFUTATION_PAYWALLED = "paywalled"
REFUTATION_VALUES = (REFUTATION_STANDS, REFUTATION_REFUTED, REFUTATION_PAYWALLED)

SOURCED = "sourced"
UNSOURCED = "unsourced"
STATUSES = (SOURCED, UNSOURCED)

# #215's "ordinarily expected" window. Past it a record has to say why it stands.
ORDINARY_WINDOW_YEARS = 5

# Anything alphanumeric after a keyword is substance. Judging whether the reason is
# a real search or a stock phrase takes a reader -- ``specificity_scan.py``'s R2.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")
DIGIT = re.compile(r"[0-9]")
NOT_ALNUM = re.compile(r"[^0-9a-z]+")

# #253. What may follow a vocabulary keyword, so a prefix is not read as a word.
# The hyphen is excluded deliberately -- see ``keyword_of``.
BOUNDARY = re.compile(r"[^0-9A-Za-z-]|$")

MISSING_FIELD = "missing-field"
UNKNOWN_STATUS = "unknown-status"
BARE_STATUS = "bare-status"
UNSOURCED_WITH_CITATION_FIELD = "unsourced-with-citation-field"
UNKNOWN_SOURCE_CLASS = "unknown-source-class"
UNKNOWN_RECENCY = "unknown-recency"
RESTATEMENT_ECHOES_CLAIM = "restatement-echoes-claim"
NUMERIC_CLAIM_UNQUANTIFIED = "numeric-claim-unquantified"
UNDATED_REFERENCE = "undated-reference"
STALE_UNEXCUSED = "stale-unexcused"
BARE_EXCUSE = "bare-excuse"
UNRESOLVABLE_LOCATOR = "unresolvable-locator"
UNDATED_READ = "undated-read"
READ_AFTER_DATE = "read-after-date"
PAGE_YEAR_UNSTATED = "page-year-unstated"
BARE_PAGE_YEAR = "bare-page-year"
PAGE_YEAR_DISAGREES = "page-year-disagrees"
UNKNOWN_REFUTATION = "unknown-refutation"
BARE_REFUTATION = "bare-refutation"
REFUTED_CITATION = "refuted-citation"
REFUTATION_ECHOES_RESTATEMENT = "refutation-echoes-restatement"

# #289's three, and they are the only rows here that read anything but the
# ledger. They grade the draft's prescriptions against it, so they run only
# where ``--draft`` named one -- and ``format_report`` prints them as *not
# graded* rather than as zeros where it did not, on
# [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
# ruling: a zero beside a row that never ran is the silent pass this whole
# directory refuses.
# #298's one row, ruled by the clinician 2026-08-20. It reads the evidence
# dump, so it runs only where ``--evidence`` named one, on the arrangement
# directly below.
CITED_TOPIC_NOT_IN_EVIDENCE = "cited-topic-not-in-evidence"

# The sibling that keeps the row above from being escapable. An entry whose
# locator is an UpToDate topic but whose title element this cannot read is a
# finding, never a citation subtracted from the set in silence --
# ``UNREADABLE_DRUG_ROW``'s argument one row over.
UNREADABLE_UPTODATE_ENTRY = "unreadable-uptodate-entry"

UNRESEARCHED_PRESCRIPTION = "unresearched-prescription"
DOSE_NOT_CLAIMED = "dose-not-claimed"
UNREADABLE_DRUG_ROW = "unreadable-drug-row"

# Which ruling each row belongs to, so a reader knows which ticket to go and read.
ROWS = {
    CITED_TOPIC_NOT_IN_EVIDENCE: "#298",
    UNREADABLE_UPTODATE_ENTRY: "#298",
    UNRESEARCHED_PRESCRIPTION: "#289",
    DOSE_NOT_CLAIMED: "#289",
    UNREADABLE_DRUG_ROW: "#289",
    MISSING_FIELD: "#214",
    UNKNOWN_STATUS: "#214",
    BARE_STATUS: "#214",
    UNSOURCED_WITH_CITATION_FIELD: "#214",
    UNKNOWN_SOURCE_CLASS: "#214",
    UNKNOWN_RECENCY: "#215",
    RESTATEMENT_ECHOES_CLAIM: "#214",
    NUMERIC_CLAIM_UNQUANTIFIED: "#214",
    UNDATED_REFERENCE: "#215",
    STALE_UNEXCUSED: "#215",
    BARE_EXCUSE: "#215",
    UNRESOLVABLE_LOCATOR: "#231",
    UNDATED_READ: "#231",
    READ_AFTER_DATE: "#231",
    PAGE_YEAR_UNSTATED: "#231",
    BARE_PAGE_YEAR: "#231",
    PAGE_YEAR_DISAGREES: "#231",
    UNKNOWN_REFUTATION: "#231",
    BARE_REFUTATION: "#231",
    REFUTED_CITATION: "#231",
    REFUTATION_ECHOES_RESTATEMENT: "#231",
}
KINDS = tuple(ROWS)

# Report order as a lookup, built from ``KINDS`` rather than typed beside it. Every
# helper appends in whatever order its own rules read best, and ``record_findings``
# sorts once -- so which helper a row lives in is not something the report can see.
_KIND_ORDER = {kind: index for index, kind in enumerate(KINDS)}

REQUIRED_WHEN_SOURCED = (
    "SOURCE",
    "REFERENCE",
    "RESTATEMENT",
    "RECENCY",
    "RESOLVED",
    "PAGE-YEAR",
    "REFUTATION",
)

# Every field that is a claim about a source. An ``unsourced`` record says there
# is no source, so carrying any one of them is the contradiction
# ``UNSOURCED_WITH_CITATION_FIELD`` was written for -- widened by #231 from the one
# field to the four, because a locator on a record that found nothing is the same
# defect and was passing.
CITATION_FIELDS = ("REFERENCE", "RESOLVED", "PAGE-YEAR", "REFUTATION")

# The rows #289 added, so ``format_report`` can tell a zero apart from a row
# that never ran. **One tuple, and how many is its own to say** -- a second
# list of the same rows is #220's drift, and a count of them in prose is
# [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143),
# which this module published in five places before a review re-derived it.
DRAFT_ROWS = (UNRESEARCHED_PRESCRIPTION, DOSE_NOT_CLAIMED, UNREADABLE_DRUG_ROW)

# #298's row, on ``DRAFT_ROWS``' arrangement and for its reason: a zero beside
# a row that never ran reads exactly like a row that passed, which is #258's
# ruling. **One tuple, and how many is its own to say.**
EVIDENCE_ROWS = (CITED_TOPIC_NOT_IN_EVIDENCE, UNREADABLE_UPTODATE_ENTRY)

# A prescription table is the one table in a case study carrying both of
# these, and the drug row is the row above ``Disp:``. **A welded pair and a
# position read off an anchor**, never a row counted from the top of the
# table: ``differential_scan.py``'s first version read a refusal by position
# and failed in both directions at once, and #153's repair was exactly this.
# A run that omits either anchor has not written a prescription table, and
# ``main``'s exit-2 limb is what says so rather than a clean zero.
DISP = re.compile(r"(?i)^disp\b[ \t]*:")
SIG = re.compile(r"(?i)^sig\b[ \t]*:")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")

# The drug name is the leading token of the drug row and nothing cleverer.
# ``ceftriaxone 1 g IV q24h`` gives ``ceftriaxone``; ``magnesium sulfate 4 g``
# gives ``magnesium``, which still matches a claim naming the salt. **It errs
# toward matching**, so what it costs is a missed finding rather than a
# refused correct record -- the direction #215's three false alarms say to
# take. A first token that is not a word is no drug at all, which is
# ``UNREADABLE_DRUG_ROW`` rather than a guess.
#
# **The cost it names is a missed drug and not only a missed match**, and the
# module docstring says which: a row welding two orders together is one drug
# here, so the second one's dose is graded by no command in this repo. #300 ruled
# it a reading on 2026-08-20 -- ``skills/practicum-case-study/SKILL.md`` step 9's
# ``the Rx blocks`` row asks a reader for it -- and this parser is untouched by
# that, which is the point of taking the option that needed no parser change.
DRUG_NAME = re.compile(r"[A-Za-z][A-Za-z'-]*")

# What a drug row may declare about itself. **The exemption is declared and
# never inferred**, so the rule fails closed: a row saying nothing is graded.
# ``continued home medication`` is the clinician's ruling of 2026-08-19 on
# #289's decision 1 -- a home medication continued unchanged at the patient's
# own dose is a number the run did not choose. ``delayed order`` is
# ``style.md`` section 8's existing declaration and exempts nothing: a dose
# that has not started yet is still a dose the run chose.
CONTINUED_HOME = "continued home medication"
DELAYED_ORDER = "delayed order"
DRUG_ROW_DECLARATIONS = (CONTINUED_HOME, DELAYED_ORDER)
EXEMPT_DECLARATIONS = (CONTINUED_HOME,)


def normalize(text: str) -> str:
    """Lowercase alphanumerics only, single-spaced.

    Used for equality and never for similarity -- anything looser would be a guess
    about paraphrase, and paraphrase is exactly what the restatement is for.
    """
    return " ".join(NOT_ALNUM.sub(" ", text.lower()).split())


# Built from ``normalize`` rather than typed, so the lookup and the comparison it
# stands in for cannot come to disagree about what a mis-keyed value looks like.
# Built once rather than per record. ``SOURCE`` can afford this and ``RECENCY``
# cannot: there the whole value is the keyword, here the keyword is a prefix with a
# reason after it, and normalizing destroys the boundary between them.
_CLASS_KEYS = frozenset(normalize(name) for name in SOURCE_CLASSES)


def keyword_of(value: str, vocabulary: tuple[str, ...]) -> tuple[str, str]:
    """Split a field value into its vocabulary keyword and the remainder.

    Longest first, so ``guideline in force`` is not read as an unrecognized value
    that happens to begin with a shorter one.

    **A prefix is not a word**, and this limb is
    [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253).
    Matching on ``startswith`` alone read any value whose first token merely
    *began with* a vocabulary word as that word, and absorbed the rest of the token
    into the remainder -- which is the field the substance rows then read as a
    reason.

    **The values that graded *clean* are the ones that matter, and they are not the
    one #253's title names.** ``STATUS: unsourced-but-see-below`` produced **no
    findings at all**: the substance row was satisfied by ``-but-see-below``, the
    residue of the very keyword it was keyed on, so a record saying nothing about
    what was searched passed the row that exists to make it say so. ``RECENCY:
    nothing newerish`` and ``RECENCY: guideline in forceful terms`` did the same
    one field over, and there the excuse is what the **window** reads -- so an old
    reference with no excuse and no reason passed with nothing reported.

    **``RECENCY: currently under review`` is a weaker case than the ticket, this
    docstring and the commit that landed them all said, and the correction is the
    finding.** ``current`` is not in ``EXCUSES``, so the window fired on that value
    before the fix and fires now; ``BARE_EXCUSE`` can never fire on it at all. What
    the prefix bug suppressed there is ``UNKNOWN_RECENCY`` alone. The wrong
    consequence was copied out of #253's table while only its *keyword* column was
    re-derived -- the same failure this work caught in that table's second row,
    committed in the fix for it, and caught by the tracker sweep afterwards.
    ``REFUTATION: standstill on the publisher's side`` is the defect on the one
    verification row.

    **The hyphen is excluded from the boundary, and that was ruled rather than
    copied from the sibling.** ``RECENCY: nothing newer - searched 2026-08-19`` is
    the documented form, so a **spaced** hyphen is a separator; a **welded** one is
    part of the word. No legitimate value of the vocabularies this helper serves
    opens with a welded hyphenated form -- checked against the tree, not assumed,
    and ``test_research_ledger`` reads which vocabularies those are off this
    module rather than listing them. ``SOURCE`` is outside this helper, matched by
    normalized equality against ``_CLASS_KEYS``, which is also where the corpus's
    only hyphen *inside* a vocabulary word lives: ``peer-reviewed``.

    **This adopted the sibling's rule rather than sharing its code.**
    ``checks_ledger.py`` ruled the boundary first and keeps its own **copy**, which
    the two modules' docstrings both argue for. **Whether the two agree today is
    deliberately not asserted anywhere** -- a claim of present identity is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) the
    moment either module moves, and pinning it in a test would forbid the very
    divergence the copy exists to permit. ``console_codec.py`` is this directory's
    only module that exists to be depended on.
    """
    stripped = value.strip()
    lowered = stripped.lower()
    for word in sorted(vocabulary, key=len, reverse=True):
        if lowered.startswith(word) and BOUNDARY.match(lowered[len(word) :]):
            return word, stripped[len(word) :]
    return "", stripped


@dataclass(frozen=True)
class Record:
    """One claim and the fields the fan-out returned for it."""

    claim: str
    fields: dict[str, str] = field(default_factory=dict)

    def value(self, name: str) -> str:
        return self.fields.get(name, "")

    @property
    def status(self) -> str:
        return keyword_of(self.value("STATUS"), STATUSES)[0]

    @property
    def reference_year(self) -> int | None:
        match = YEAR.search(self.value("REFERENCE"))
        return int(match.group(1)) if match else None

    @property
    def page_year(self) -> int | None:
        """The year the page itself states, per #231's ``PAGE-YEAR``.

        Bare rather than parenthesized: this is what a reader copied off a cover
        page, not an APA date element.
        """
        match = BARE_YEAR.search(self.value("PAGE-YEAR"))
        return int(match.group(1)) if match else None

    @property
    def read_date(self) -> date | None:
        """The day the agent says it opened the source, or ``None``.

        A date that does not exist reads as no date at all -- the field failed to
        say when it was read, which is the finding either way.
        """
        match = READ_DATE.search(self.value("RESOLVED"))
        if not match:
            return None
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None


@dataclass(frozen=True)
class Prescription:
    """One drug row of one prescription table in the draft.

    ``drug`` is empty where the row could not be read, which is a finding
    rather than a table quietly dropped. ``order`` is the row with its
    declaration stripped, so the dose test reads what was prescribed and not
    a digit inside the words ``Continued home medication``.
    """

    drug: str
    order: str
    declaration: str = ""

    @property
    def exempt(self) -> bool:
        return self.declaration in EXEMPT_DECLARATIONS

    @property
    def states_a_dose(self) -> bool:
        """Whether the run chose a number here.

        ``prenatal vitamin one tablet PO daily`` spells its number out and is
        not asked for a quantified claim, which is
        ``NUMERIC_CLAIM_UNQUANTIFIED``'s *a claim with no number is not asked
        for one* arriving one artifact over.
        """
        return bool(DIGIT.search(self.order))


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One record failing one row."""

    claim: str
    detail: str


@dataclass(frozen=True)
class Scan:
    """Counts over one ledger, plus the findings ``--show`` prints.

    ``as_of`` is ``None`` where the ledger carried no ``DATE:`` header. Nine of the
    ten rows still grade; the window does not, and the report says so.
    """

    as_of: date | None
    records: int
    sourced: int
    unsourced: int
    unrecognized_status: int
    by_class: tuple[tuple[str, int], ...]
    outside_vocabulary: int
    standing_past_five: int
    # Counted rather than graded, because ``paywalled`` passes. A run whose
    # citations are all behind a wall has been checked much less than a clean
    # exit suggests, and this line is the only place that shows.
    behind_a_paywall: int
    counts: tuple[tuple[str, int], ...]
    failing_records: int
    # ``None`` where no ``--draft`` was given, which is the whole reason it is
    # not an ``int`` starting at zero: #289's rows did not run, and a
    # zero beside a row that never ran reads exactly like a row that passed.
    # ``format_report`` prints *not graded* off this, on #258's ruling.
    prescriptions: int | None
    continued_home: int
    # Table runs carrying one anchor and not the other -- a partial read,
    # counted and reported and outside the exit status. See
    # ``half_anchored_tables``.
    half_anchored: int
    prescriptions_at_fault: int
    # ``None`` where no ``--evidence`` was given, for the reason
    # ``prescriptions`` is not an ``int``: a zero beside a row that never ran
    # is indistinguishable from a row that passed, which is #258's ruling.
    evidence_topics: int | None
    # What the row **read**, where ``evidence_topics`` is what it read
    # *against*. #258 one level down: a ledger citing no UpToDate topic at all
    # reported a clean row, which is indistinguishable from one whose every
    # citation checked out. Found by pointing the command at the real ledger.
    uptodate_citations: int | None
    evidence_at_fault: int
    findings: tuple[Finding, ...]


# A topic body is present when its masthead is. **#298 decision 2 proposed
# reading a title as a *heading* and that is not implementable against the
# artifact it describes** -- the rendered dump carries no headings of any kind,
# only prose, bullets and short all-caps section labels. The masthead is what
# marks a body, and the title is the line above it. Measured before it was
# believed: nearly every body the real dump carries joins a ``See "..."``
# cross-reference exactly under this rule. **The count is #298's to state and is
# deliberately nowhere in this tree** -- it is measured against a file under
# ``scratch/``, so nothing here re-derives it and the next paste moves it.
TOPIC_MASTHEAD = re.compile(r"(?i)^[ \t]*authors?[ \t]*:")

# The title element of [apa7.md](skills/practicum-case-study/reference/apa7.md)
# section 2's published form, taken between the year element and the database
# element. **The database name is matched as a word and never as a hostname**,
# which is ``reference_scan``'s recorded defect adopted rather than
# rediscovered: without the lookahead an entry that drops the database element
# has its title read out of ``www.uptodate.com`` and a garbage string is then
# compared against the dump. Both spellings of the name are live -- section 2
# requires it italicized and records that the corpus italicizes it nowhere.
UPTODATE_TITLE = re.compile(
    r"\(\s*(?:n\.d\.|\d{4}[a-z]?)\s*\)\s*\.\s*"
    r"(?P<title>.+?)"
    r"\s*\.\s*[*_]{0,2}UpToDate[*_]{0,2}\s*\.(?=\s|$)",
    re.S | re.I,
)

# **A locator pointing at an UpToDate topic**, which is what tells this an entry
# was meant to be one when ``UPTODATE_TITLE`` could not read it. Matched as a
# **host** and never as a word -- the mirror of ``UPTODATE_TITLE``'s guard, and
# for the mirror reason: there the name in a URL must not be read as the database
# element, and here the name in a *title* must not be read as a locator. So it
# requires the scheme-or-``www`` run and the path that a real topic URL carries.
UPTODATE_LOCATOR = re.compile(r"(?i)\b(?:https?://|www\.)[\w.-]*\buptodate\.com/")

# What a finding names where the citation came from the draft rather than from a
# record. ``UNREADABLE_DRUG_ROW``'s ``a prescription table`` precedent: the
# ``claim`` slot is a record heading everywhere else, and a draft entry has none.
DRAFT_LIST = "the draft's reference list"


def carried_topics(text: str) -> set[str]:
    """Every topic whose **body** the dump carries.

    A cross-reference is not a body and that distinction is the whole row: the
    real dump refers to more than an order of magnitude more topics than it
    carries, so reading a reference as a body would report a clean join over a
    dump carrying almost nothing. The two figures are #298's to state.
    """
    lines = text.splitlines()
    carried: set[str] = set()
    for index, line in enumerate(lines):
        if not TOPIC_MASTHEAD.match(line):
            continue
        above = index - 1
        while above >= 0 and not lines[above].strip():
            above -= 1
        # A masthead with nothing above it names no topic, and the empty string
        # must not go in: it would match every entry whose title failed to parse,
        # which is a silent pass on the one row here that can refuse.
        if above >= 0:
            carried.add(lines[above].strip())
    return carried


def uptodate_topic(entry: str) -> str:
    """The topic an UpToDate reference entry names, or ``""`` if it is not one.

    **Scoped to UpToDate, and that scope is the grounding rather than a
    narrowing.** #231 ruled the database subscription-gated -- a fetch reaches a
    login wall -- so a topic the dump does not carry is one nobody could have
    opened. A journal article the dump lacks is
    ``skills/practicum-case-study/SKILL.md`` step 3's ordinary case, and a row
    firing on one would be #215's defect again.
    """
    match = UPTODATE_TITLE.search(entry)
    return " ".join(match.group("title").split()) if match else ""


def read_records(text: str) -> list[Record]:
    """Every claim record in one ledger.

    A field's value runs to the next field line or the next claim heading, so an
    APA entry may wrap onto a hanging-indent continuation the way APA sets one. A
    line before the first claim heading belongs to no record and is dropped --
    the ``DATE:`` header lives there.
    """
    records: list[Record] = []
    claim: str | None = None
    fields: dict[str, str] = {}
    current: str | None = None

    def close() -> None:
        if claim is not None:
            records.append(Record(claim=claim, fields=dict(fields)))

    for line in text.splitlines():
        heading = CLAIM.match(line)
        if heading:
            close()
            claim, fields, current = heading.group(1), {}, None
            continue
        if claim is None:
            continue
        named = FIELD.match(line)
        if named:
            current = named.group(1).upper()
            fields[current] = named.group(2)
            continue
        if current and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    close()
    return records


def _unsourced_findings(record: Record) -> list[Finding]:
    """#214's unsourced branch: the reason, and the four fields it may not carry.

    An ``unsourced`` record is not a failure -- ``skills/practicum-case-study/SKILL.md``
    step 3 routes it to ``PROPOSED``. What is refused is one that says it found
    nothing while carrying a claim about a source.
    """
    claim = record.claim
    found: list[Finding] = []
    if not SUBSTANCE.search(keyword_of(record.value("STATUS"), STATUSES)[1]):
        found.append(Finding(BARE_STATUS, claim, record.value("STATUS")))
    for name in CITATION_FIELDS:
        if SUBSTANCE.search(record.value(name)):
            found.append(Finding(UNSOURCED_WITH_CITATION_FIELD, claim, f"{name}: {record.value(name)}"))
    return found


def _contract_findings(record: Record) -> list[Finding]:
    """#214's rows for a sourced record: the fields, the class, the restatement.

    Takes no ``as_of``. Nothing #214 asks of a record is measured against a date,
    and the signature is where that is visible.
    """
    claim = record.claim
    found: list[Finding] = []

    for name in REQUIRED_WHEN_SOURCED:
        if not SUBSTANCE.search(record.value(name)):
            found.append(Finding(MISSING_FIELD, claim, name))

    source = normalize(record.value("SOURCE"))
    if source and source not in _CLASS_KEYS:
        found.append(Finding(UNKNOWN_SOURCE_CLASS, claim, record.value("SOURCE")))

    restatement = record.value("RESTATEMENT")
    if SUBSTANCE.search(restatement):
        if normalize(restatement) == normalize(claim):
            found.append(Finding(RESTATEMENT_ECHOES_CLAIM, claim, restatement))
        if DIGIT.search(claim) and not DIGIT.search(restatement):
            found.append(Finding(NUMERIC_CLAIM_UNQUANTIFIED, claim, restatement))
    return found


def _recency_findings(record: Record, as_of: date | None) -> list[Finding]:
    """#215's four rows: the disposition, the excuse, the year, the window.

    **The two blocks are one helper because they are one rule read twice.** The
    vocabulary keyword and its remainder are computed here and read by both -- the
    window row asks whether an excuse stands, which is the same ``keyword_of`` split
    the disposition row grades. Cutting between them would hand the second block a
    value it did not derive, which is the sharing
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242) found
    and the reason the seam is here rather than at the six blocks it counted.

    One row here reads ``as_of``: ``STALE_UNEXCUSED``. ``None`` means the ledger
    stated no date, so the window is skipped and the other three still run.
    """
    claim = record.claim
    found: list[Finding] = []

    recency = record.value("RECENCY")
    excuse, remainder = keyword_of(recency, RECENCY_VALUES)
    if SUBSTANCE.search(recency) and not excuse:
        # ``STATUS``'s reasoning and not ``SOURCE``'s: this field gates the window
        # row below it, so a fifth disposition is a record the window never read.
        found.append(Finding(UNKNOWN_RECENCY, claim, recency))
    if excuse in EXCUSES and not SUBSTANCE.search(remainder):
        found.append(Finding(BARE_EXCUSE, claim, recency))

    if SUBSTANCE.search(record.value("REFERENCE")):
        year = record.reference_year
        excused = excuse in EXCUSES and SUBSTANCE.search(remainder)
        if year is None:
            # ``n.d.`` is legitimate APA. What is refused is an undated source with
            # nothing said about why it stands -- the clinician's own escape hatch,
            # rather than a blanket rule he never made.
            if not excused:
                found.append(Finding(UNDATED_REFERENCE, claim, record.value("REFERENCE")))
        elif as_of is not None and as_of.year - year > ORDINARY_WINDOW_YEARS and excuse not in EXCUSES:
            detail = f"{year}, RECENCY: {recency}"
            found.append(Finding(STALE_UNEXCUSED, claim, detail))
    return found


def _citation_findings(record: Record, as_of: date | None) -> list[Finding]:
    """#231's ten rows: the locator, the page year, the refutation.

    **Self-contained, which is what made the seam worth cutting on
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242).** These
    rows share nothing with #214's and #215's but the record itself -- the echo row
    re-reads ``RESTATEMENT`` off the record rather than being handed it, so no value
    crosses the boundary.

    One row here reads ``as_of``: ``READ_AFTER_DATE``. With ``_recency_findings``'s
    window that is **every** row in the module measured against a date, and the two
    signatures are where a reader sees it.

    Nothing here fetches anything. What the rows buy is a commitment to specifics a
    reader can be caught on in one click, which an APA entry alone is not.
    """
    claim = record.claim
    found: list[Finding] = []

    # #231's first half: the agent was on the page, so it writes down where it was
    # and when.
    resolved = record.value("RESOLVED")
    if SUBSTANCE.search(resolved):
        if not LOCATOR.search(resolved):
            found.append(Finding(UNRESOLVABLE_LOCATOR, claim, resolved))
        read = record.read_date
        if read is None:
            found.append(Finding(UNDATED_READ, claim, resolved))
        elif as_of is not None and read > as_of:
            # The second row measured against ``DATE``, and the second one a
            # dateless ledger loses. Reading a source after the paper was written
            # is a record describing something that had not happened yet.
            found.append(Finding(READ_AFTER_DATE, claim, f"read {read.isoformat()}, DATE {as_of}"))

    # **One rule in three rows: the page and the entry agree about the year.** An
    # ``n.d.`` entry beside a page that states no year is the agreeing case and
    # passes -- refusing it would refuse legitimate APA, which is the mistake
    # ``UNDATED_REFERENCE`` was already corrected for once.
    stated = record.value("PAGE-YEAR")
    if SUBSTANCE.search(stated):
        page_year = record.page_year
        entry_year = record.reference_year
        cited = bool(SUBSTANCE.search(record.value("REFERENCE")))
        if page_year is None:
            if cited and entry_year is not None:
                found.append(Finding(PAGE_YEAR_UNSTATED, claim, stated))
        else:
            # Two things rather than one, on ``BARE_EXCUSE``'s reasoning: a year
            # alone is an assertion, a year with where it was found is a place a
            # reader can go and look.
            if not SUBSTANCE.search(BARE_YEAR.sub(" ", stated, count=1)):
                found.append(Finding(BARE_PAGE_YEAR, claim, stated))
            if cited and page_year != entry_year:
                entry = entry_year if entry_year is not None else "no year"
                found.append(
                    Finding(PAGE_YEAR_DISAGREES, claim, f"{page_year} on the page, {entry} in REFERENCE")
                )

    # #231's second half, and the only row here that is verification rather than a
    # better-shaped promise. **That the refuter was a different agent is not
    # reachable from the record** -- ``skills/practicum-case-study/SKILL.md`` step 3
    # states it, this grades the shape.
    refutation = record.value("REFUTATION")
    if SUBSTANCE.search(refutation):
        verdict, reason = keyword_of(refutation, REFUTATION_VALUES)
        if not verdict:
            # ``STATUS``'s reasoning again: it gates the row below, so a third
            # word is a record the refutation row never read.
            found.append(Finding(UNKNOWN_REFUTATION, claim, refutation))
        else:
            if not SUBSTANCE.search(reason):
                found.append(Finding(BARE_REFUTATION, claim, refutation))
            elif normalize(reason) == normalize(record.value("RESTATEMENT")):
                # The first agent re-asserting rather than a second one checking.
                # ``RESTATEMENT_ECHOES_CLAIM``'s trick, one level up.
                found.append(Finding(REFUTATION_ECHOES_RESTATEMENT, claim, refutation))
            if verdict == REFUTATION_REFUTED:
                # A **failure**, unlike ``unsourced``, which the skill routes to
                # ``PROPOSED`` honestly. This is a false citation sitting in the
                # ledger: the run rewrites the record or writes ``unsourced``.
                found.append(Finding(REFUTED_CITATION, claim, refutation))
    return found


def record_findings(record: Record, as_of: date | None) -> list[Finding]:
    """Every row this record fails, in ``KINDS`` order. A record can fail several.

    ``as_of`` of ``None`` means the ledger stated no date, so the window row and the
    read-date row are skipped and every other row still runs --
    ``differential_scan.py``'s ordering, where a finding outranks an incomplete scan.

    **The rows live in four helpers and the branching lives here**, on
    ``reference_scan.py``'s arrangement -- the sibling with a comparable row count,
    and the one
    [#242](https://github.com/mshamblin5150-code/clinical-skills/issues/242) did not
    check when it wrote that every other scanner keeps one grader. What stays here is
    the control flow the helpers cannot be written without: a record with no
    recognized ``STATUS`` is graded on nothing below it, and an ``unsourced`` one is
    graded on a different set entirely.

    **Sorted by ``KINDS`` rather than by append order**, so where a helper is called
    is not something a reader of this record's findings can see. The counts were
    already ordered that way and the finding list was not, and this is what lets a
    seam move again without a report changing shape.

    **Per record, and ``survey`` does not re-sort across them.** A ledger's findings
    stay grouped by the record that raised them, which is what ``--show`` should
    print; the guarantee here is about one record's rows and no wider.
    """
    found: list[Finding] = []
    claim = record.claim

    if not SUBSTANCE.search(claim):
        found.append(Finding(MISSING_FIELD, claim, "CLAIM"))

    status = record.status
    if not status:
        # Unlike an unrecognized ``SPECIFICITY`` keyword, this one is a failure:
        # the branch decides which tests below run, so a record wearing a third
        # word is graded on nothing at all and prints as clean.
        found.append(Finding(UNKNOWN_STATUS, claim, record.value("STATUS")))
    elif status == UNSOURCED:
        found += _unsourced_findings(record)
    else:
        found += _contract_findings(record)
        found += _recency_findings(record, as_of)
        found += _citation_findings(record, as_of)

    # Stable, so two findings of one kind keep the order their helper appended them in.
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind])


def _cells(line: str) -> list[str]:
    r"""The cells of one Markdown table row, unwrapped from their backticks.

    **The split is the renderer's own**, imported rather than restated, on
    ``reference_scan.py``'s ``REFERENCE_HEADING`` precedent and for its reason:
    ``docx_write.split_row`` is what decides where a cell ends in the document
    a grader actually reads, and a second reading of one table can put the
    ``Disp:`` anchor in a different row than the one that renders. It honors an
    escaped ``\|`` as a literal pipe; a copy here would not, and #215's follow-up
    is the recorded instance of that exact divergence costing a rendered cell.

    **A row's cell count varies by design and nothing here reads it.** Since
    #293 that table is three columns wide: row 1 declares three cells, the drug,
    ``Disp:``, ``Sig:`` and signature rows declare one and span, and the last
    declares two.

    The backticks are this module's own business -- ``style.md`` sets every cell
    of that table as code, and the renderer keeps them because they are content.
    """
    return [cell.strip("`").strip() for cell in split_row(line)]


def _declaration_of(order: str) -> tuple[str, str]:
    """Split a drug row into what it declares about itself and the order.

    **The boundary is #253's**, arriving at the declarations: a value merely
    *opening* with a vocabulary word is not that word, so ``Continued home
    medications reviewed:`` does not exempt the row it opens. The separator is a
    colon, which is what ``style.md`` section 8 writes.
    """
    lowered = order.lower()
    for name in sorted(DRUG_ROW_DECLARATIONS, key=len, reverse=True):
        if not lowered.startswith(name):
            continue
        rest = order[len(name) :].lstrip()
        if rest.startswith(":"):
            return name, rest[1:].strip()
    return "", order


def _drug_of(order: str) -> str:
    """The leading token of a drug row, or ``""`` where it is not a word.

    Deliberately the first token and nothing cleverer -- see ``DRUG_NAME``.
    """
    tokens = order.split()
    if not tokens:
        return ""
    token = tokens[0].strip(",;.:()")
    return token if DRUG_NAME.fullmatch(token) else ""


def _table_runs(text: str) -> list[list[list[str]]]:
    """Every Markdown table in ``text``, as rows of cells.

    **The blocks are the renderer's own**, imported rather than walked here, on
    ``_cells``'s reasoning one level up: ``docx_write.markdown_tables`` is what
    decides where a table begins and ends in the document a grader reads, and its
    own docstring refuses a second copy of the loop in as many words. This module
    had one -- written a day before that function existed, on a branch that could
    not see it -- and the two disagreed about what a table *is*: this required
    only consecutive rows and that requires a separator rule under the header, so
    a block the renderer would set as paragraphs was a prescription table here.
    Caught at the merge and by nothing either suite ran.
    """
    return [
        [_cells(line) for line in block.splitlines() if line.strip()]
        for block in markdown_tables(text)
    ]


def read_prescriptions(text: str) -> list[Prescription]:
    """Every drug row in every prescription table of a draft.

    A prescription table is a run of consecutive Markdown table lines carrying
    both a ``Disp:`` cell and a ``Sig:`` cell, and the drug row is the row above
    ``Disp:``. Any other table in the document -- the differential, the MDM, the
    faculty's questions -- carries neither and is not read.

    **A table carrying the pair with nothing readable above ``Disp:`` comes back
    with an empty ``drug``** rather than being dropped, so a table this parser
    cannot read is a finding instead of a silent subtraction from the set.
    """
    return [rx for rows in _table_runs(text) for rx in _prescriptions_in(rows)]


def half_anchored_tables(text: str) -> int:
    """Table runs carrying one of the two anchors and not the other.

    **A partial read is what this exists to make visible**, and total absence is
    not the only way to get one. A draft whose Rx tables are mixed -- one
    canonical, one writing ``Dispense:``, which the word boundary in ``DISP``
    rightly refuses -- yields a smaller set, and all three rows then grade a
    subset while the report prints the shrunken count with nothing beside it.
    ``main``'s exit-2 limb covers *no* prescription table and never a short one,
    which is
    [#204](https://github.com/mshamblin5150-code/clinical-skills/issues/204)'s
    complaint -- a parser reading one declaration of eight and printing nothing
    to say so -- arriving in a second tool. Found by the tracker sweep on #289's
    own branch.

    **Counted and reported, and deliberately outside the exit status**, which is
    ``block_scan.py``'s arrangement for a reading rather than a violation: a
    table carrying one anchor is *probably* a malformed prescription and this
    cannot know it is one, and #204's own question -- whether a short read may
    refuse -- is unruled. What the run gets is the number, on the same page as
    its exit.
    """
    return sum(
        1
        for rows in _table_runs(text)
        if any(DISP.match(c) for cells in rows for c in cells)
        != any(SIG.match(c) for cells in rows for c in cells)
    )


def _prescriptions_in(rows: list[list[str]]) -> list[Prescription]:
    """The drug rows of one run of table lines, empty where it is not a table of
    prescriptions."""
    opened = [index for index, cells in enumerate(rows) if any(DISP.match(c) for c in cells)]
    if not opened or not any(SIG.match(c) for cells in rows for c in cells):
        return []
    found: list[Prescription] = []
    for index in opened:
        above = rows[index - 1] if index else []
        order = next(
            (
                cell
                for cell in above
                if cell and not SEPARATOR_CELL.match(cell) and not DISP.match(cell)
            ),
            "",
        )
        declaration, order = _declaration_of(order)
        found.append(Prescription(_drug_of(order), order, declaration))
    return found


def _records_naming(drug: str, records: list[Record]) -> list[Record]:
    """Every claim heading naming this drug, as a word rather than as a prefix."""
    word = re.compile(rf"(?i)(?<![0-9A-Za-z]){re.escape(drug)}(?![0-9A-Za-z])")
    return [record for record in records if word.search(record.claim)]


def prescription_findings(
    prescriptions: list[Prescription], records: list[Record]
) -> list[Finding]:
    """#289's rows: the draft's prescriptions against the ledger.

    One of the two graders here that read anything but the ledger -- #298's
    ``evidence_findings`` is the other -- and **the only one with an expected
    set** -- which is the gap the ticket is about.
    ``research_ledger`` has no expected count of its own and says so, so a dose
    nobody entered as a claim is invisible to every other row in this module.
    ``checks_ledger.py``'s arrangement, with the set derived from the document
    the run wrote rather than from a table in here.

    **It never compares the numbers**, which is the ticket's own closing
    prohibition: a dose depends on indication, weight, renal function, pregnancy
    and route, and a row refusing a correct dose for the wrong reason is #215's
    defect a fourth time. What is reachable is whether the dose was *sourced*.
    """
    found: list[Finding] = []
    for rx in prescriptions:
        if rx.exempt:
            continue
        if not rx.drug:
            found.append(
                Finding(
                    UNREADABLE_DRUG_ROW,
                    "a prescription table",
                    "carries Disp: and Sig: with no readable drug row above Disp:",
                )
            )
            continue
        naming = _records_naming(rx.drug, records)
        if not naming:
            found.append(
                Finding(
                    UNRESEARCHED_PRESCRIPTION,
                    rx.drug,
                    "prescribed in the draft, and no claim record names it",
                )
            )
            continue
        if rx.states_a_dose and not any(DIGIT.search(record.claim) for record in naming):
            found.append(
                Finding(
                    DOSE_NOT_CLAIMED,
                    rx.drug,
                    "the order states a dose and no claim record naming the drug states a number",
                )
            )
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind])


def evidence_findings(
    records: list[Record],
    entries: tuple[str, ...],
    carried: set[str],
) -> tuple[list[Finding], int]:
    """#298's row: an UpToDate topic the run cites that the dump does not carry.

    **The topics the dump merely refers to and does not carry are not graded**,
    and that is the ruling rather than an omission. The overwhelming majority of
    the real dump's cross-references are exactly that, which is the ordinary case
    the ticket's own *What must not come out of this* forbids firing on, and their
    reference counts decay smoothly with no plateau -- so any cut is a value named
    at an edge, which is ``SPACE_ADVANCE_FRACTION``'s recorded failure and #97's
    objection. **The figures are #298's to state**, being counted against a file
    under ``scratch/`` that nothing committed re-derives. What is graded is the
    **join**: the dump is the whole of what the clinician handed over, so an
    UpToDate topic cited and absent from it is one nobody read.

    **No escape hatch, ruled 2026-08-20.** If an UpToDate topic is worth citing
    it goes in the dump, and the remedy is one paste.

    Reads the ledger's ``REFERENCE`` fields and the draft's entries where
    ``--draft`` named one. **One finding per topic and not per citation** -- the
    row is about a topic nobody read, so two records naming the same missing one
    is one thing wrong.
    """
    keys = {normalize(title) for title in carried}
    found: list[Finding] = []
    seen: set[str] = set()
    read = 0
    cited = [(record.claim, record.value("REFERENCE")) for record in records]
    cited += [(DRAFT_LIST, entry) for entry in entries]
    for claim, entry in cited:
        title = uptodate_topic(entry)
        key = normalize(title)
        if not key:
            # An entry this cannot read but whose locator says it was meant to be
            # an UpToDate topic. It is counted and reported rather than dropped:
            # dropping it took the topic out of the join **and** out of the
            # population row, so four characters removed from an entry walked
            # around a row that has no escape hatch, with nothing red anywhere --
            # ``reference_scan`` does not reach it either.
            if UPTODATE_LOCATOR.search(entry):
                read += 1
                found.append(
                    Finding(
                        UNREADABLE_UPTODATE_ENTRY,
                        claim,
                        "the locator names an UpToDate topic and the entry states"
                        " no database element, so no title could be read",
                    )
                )
            continue
        # Counted before the join and before the de-duplication, because this is
        # the row's **population**: what it read, not what it failed. Derived from
        # the one walk rather than counted a second time, so the figure and the
        # findings cannot come to disagree about what was scanned.
        read += 1
        if key in keys or key in seen:
            continue
        seen.add(key)
        found.append(Finding(CITED_TOPIC_NOT_IN_EVIDENCE, claim, title))
    return sorted(found, key=lambda f: _KIND_ORDER[f.kind]), read


def survey(
    records: list[Record],
    as_of: date | None,
    prescriptions: list[Prescription] | None = None,
    half_anchored: int = 0,
    carried: set[str] | None = None,
    entries: tuple[str, ...] = (),
) -> Scan:
    """Count across one ledger.

    Takes parsed records rather than paths, so the counts carry no provenance of
    their own. The ledger's **name** is printed by ``format_report`` the way every
    sibling prints a run directory's -- the name, never the path.
    """
    graded = [(record, record_findings(record, as_of)) for record in records]
    # The prescription rows lead, in the findings as well as in the counts:
    # they are their own group rather than one more row of a record, and
    # ``--show`` and the count column have to agree about the order.
    on_the_draft = prescription_findings(prescriptions or [], records)
    # The evidence row leads, on the prescription rows' reasoning: it is its
    # own group rather than one more row of a record, and ``--show`` and the
    # count column have to agree about the order.
    on_the_evidence, uptodate_read = (
        ([], None)
        if carried is None
        else evidence_findings(records, entries, carried)
    )
    found = (
        on_the_evidence
        + on_the_draft
        + [f for _, per_record in graded for f in per_record]
    )
    sourced = [r for r in records if r.status == SOURCED]
    return Scan(
        as_of=as_of,
        records=len(records),
        sourced=len(sourced),
        unsourced=sum(1 for r in records if r.status == UNSOURCED),
        unrecognized_status=sum(1 for r in records if not r.status),
        by_class=tuple(
            (name, sum(1 for r in sourced if normalize(r.value("SOURCE")) == normalize(name)))
            for name in SOURCE_CLASSES
        ),
        outside_vocabulary=sum(1 for r in sourced if normalize(r.value("SOURCE")) not in _CLASS_KEYS),
        standing_past_five=sum(
            1 for r in sourced if keyword_of(r.value("RECENCY"), RECENCY_VALUES)[0] in EXCUSES
        ),
        behind_a_paywall=sum(
            1
            for r in sourced
            if keyword_of(r.value("REFUTATION"), REFUTATION_VALUES)[0] == REFUTATION_PAYWALLED
        ),
        counts=tuple((kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS),
        failing_records=sum(1 for _, per_record in graded if per_record),
        prescriptions=None if prescriptions is None else len(prescriptions),
        continued_home=sum(1 for rx in prescriptions or [] if rx.exempt),
        half_anchored=half_anchored,
        prescriptions_at_fault=len(on_the_draft),
        evidence_topics=None if carried is None else len(carried),
        uptodate_citations=uptodate_read,
        evidence_at_fault=len(on_the_evidence),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no claim text unless ``show``."""
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console where anything outside cp1252 reads like corruption in the
    # one output meant to be pasted.
    lines = [
        f"research ledger over {source}, as of {scan.as_of.isoformat()}"
        if scan.as_of
        else f"research ledger over {source}, NO DATE HEADER - the window was not graded",
        "",
        f"  claim records read               {scan.records}",
        f"    sourced                        {scan.sourced}",
        f"    unsourced - go to PROPOSED     {scan.unsourced}",
        f"    neither status                 {scan.unrecognized_status}",
        "",
    ]
    for name, count in scan.by_class:
        lines.append(f"    {name:<30} {count}")
    lines.append(f"    {'outside the vocabulary':<30} {scan.outside_vocabulary}")
    lines.append("")
    lines.append(f"  standing past five years         {scan.standing_past_five}")
    lines.append(f"  citations behind a paywall       {scan.behind_a_paywall}")
    lines.append("")
    # **The coverage line, and it prints on every run rather than only a short
    # one.** #258's ruling: a reader who has learned to read the qualifier
    # takes its absence as the stronger claim, so the run that graded no
    # prescriptions says so on the same page as its clean exit.
    if scan.prescriptions is None:
        lines.append(
            f"  {'prescription drug rows':<32} not graded - no --draft was given"
        )
    else:
        lines.append(f"  prescription drug rows           {scan.prescriptions}")
        lines.append(
            f"    continued unchanged, exempt    {scan.continued_home}"
        )
        lines.append(
            f"    needing a claim record         {scan.prescriptions - scan.continued_home}"
        )
        # Printed on every graded run rather than only a short one, on #258's
        # reasoning: a reader who has learned to read the qualifier takes its
        # absence as the stronger claim.
        lines.append(
            f"    tables read with one anchor    {scan.half_anchored}  (not graded)"
        )
    # The population this row joined against, on #258's ruling and for its
    # reason: a reader who has learned to read the qualifier takes its absence as
    # the stronger claim, so the run that graded no citation says so on the same
    # page as its clean exit.
    if scan.evidence_topics is None:
        lines.append(
            f"  {'evidence topics carried':<32} not graded - no --evidence was given"
        )
        lines.append(
            f"  {'UpToDate citations read':<32} not graded - no --evidence was given"
        )
    else:
        lines.append(f"  {'evidence topics carried':<32} {scan.evidence_topics}")
        # What the row read, beside what it read against. Both, because either
        # alone reads as the stronger claim: a count of topics carried says
        # nothing about whether a single citation was joined to them.
        lines.append(f"  {'UpToDate citations read':<32} {scan.uptodate_citations}")
    lines.append("")
    for kind, count in scan.counts:
        # Wide enough for the longest kind, so the count column stays a column.
        # ``refutation-echoes-restatement`` is 29 and overflowed 28 on the day it
        # was added, which is the report going ragged in the one output meant to
        # be pasted into a ticket.
        # A #289 row that did not run prints as such rather than as a zero,
        # for the reason ``Scan.prescriptions`` is not an ``int``.
        shown = count
        if scan.prescriptions is None and kind in DRAFT_ROWS:
            shown = "not graded"
        if scan.evidence_topics is None and kind in EVIDENCE_ROWS:
            shown = "not graded"
        lines.append(f"  {ROWS[kind]} - {kind:<31} {shown}")
    lines.append("")
    lines.append(f"  records at fault                 {scan.failing_records}")
    if scan.prescriptions is not None:
        lines.append(
            f"  prescriptions at fault           {scan.prescriptions_at_fault}"
        )
    if scan.evidence_topics is not None:
        lines.append(
            f"  cited topics not handed over     {scan.evidence_at_fault}"
        )
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<26} {finding.claim}")
            lines.append(f"      {finding.detail}")
    return "\n".join(lines)


# One string, so the usage line and the flags cannot drift apart.
USAGE = (
    "usage: research_ledger.py <a ledger file> [--draft <a draft .md>]"
    " [--evidence <the evidence dump>] [--show]"
)


@dataclass(frozen=True)
class Source:
    path: Path
    records: tuple[Record, ...]
    as_of: date | None
    prescriptions: tuple[Prescription, ...] | None
    half_anchored: int
    carried: set[str] | None
    entries: tuple[str, ...]
    evidence_unreadable: bool
    draft_name: str | None
    evidence_name: str | None


def _load(parsed: run_grader.Parsed) -> Source:
    path = Path(parsed.source)
    if not path.is_file():
        raise run_grader.SourceError(f"no ledger file named {path.name}")
    text = path.read_text(encoding="utf-8", errors="replace")
    records = tuple(read_records(text))
    if not records:
        raise run_grader.SourceError(f"no claim records found in {path.name}")

    draft = parsed.value("--draft")
    prescriptions: tuple[Prescription, ...] | None = None
    half_anchored = 0
    draft_text = ""
    draft_name: str | None = None
    if draft is not None:
        draft_path = Path(draft)
        draft_name = draft_path.name
        if not draft_path.is_file():
            raise run_grader.SourceError(f"no draft file named {draft_path.name}")
        if (
            coursework_run.is_submission(draft_path)
            and coursework_run.is_run_directory(path.parent)
            and not draft_path.stem.startswith(path.parent.name)
        ):
            raise run_grader.SourceError(
                f"submission {draft_path.name} does not belong to run directory {path.parent.name}"
            )
        draft_text = draft_path.read_text(encoding="utf-8", errors="replace")
        prescriptions = tuple(read_prescriptions(draft_text))
        half_anchored = half_anchored_tables(draft_text)

    evidence = parsed.value("--evidence")
    carried: set[str] | None = None
    entries: tuple[str, ...] = ()
    evidence_unreadable = False
    evidence_name: str | None = None
    if evidence is not None:
        evidence_path = Path(evidence)
        evidence_name = evidence_path.name
        if not evidence_path.is_file():
            raise run_grader.SourceError(f"no evidence file named {evidence_path.name}")
        found = carried_topics(evidence_path.read_text(encoding="utf-8", errors="replace"))
        evidence_unreadable = not found
        if found:
            carried = found
        if carried is not None and draft is not None:
            entries = tuple(entry.text for entry in read_document(draft_text).entries)

    stamp = DATE_HEADER.search(text)
    as_of = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3))) if stamp else None
    return Source(
        path,
        records,
        as_of,
        prescriptions,
        half_anchored,
        carried,
        entries,
        evidence_unreadable,
        draft_name,
        evidence_name,
    )


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(
        list(source.records),
        source.as_of,
        list(source.prescriptions) if source.prescriptions is not None else None,
        source.half_anchored,
        source.carried,
        source.entries,
    )
    diagnostics: list[str] = []
    if source.evidence_unreadable:
        diagnostics.append(
            f"no topic body found in {source.evidence_name} - a body is read by its"
            " Authors: masthead, so #298's row was applied to nothing. Every other row still ran."
        )
    if source.as_of is None:
        diagnostics.append(
            f"{source.path.name} carries no DATE: <YYYY-MM-DD> header, so neither the"
            " five-year window nor the read-date check was applied to any record in it."
        )
    if source.prescriptions is not None and not source.prescriptions:
        diagnostics.append(
            f"no prescription table found in {source.draft_name} - a table is read by its"
            " Disp: and Sig: rows, so none of #289's rows was applied to it."
        )
    if scan.failing_records:
        diagnostics.append(
            f"{scan.failing_records} record(s) fail the #214 fan-out contract."
            " Re-run with --show to see which, and do not paste that output."
        )
    if scan.prescriptions_at_fault:
        diagnostics.append(
            f"{scan.prescriptions_at_fault} prescription(s) in {source.draft_name} reach"
            " no claim record. Re-run with --show to see which, and do not paste that output."
        )
    if scan.evidence_at_fault:
        diagnostics.append(
            f"{scan.evidence_at_fault} UpToDate topic(s) cited here are not in the"
            " evidence dump, so nobody read them. Paste the topic in and re-run,"
            " or drop the citation. Re-run with --show to see which, and do not paste that output."
        )
    findings_failed = bool(
        scan.failing_records or scan.prescriptions_at_fault or scan.evidence_at_fault
    )
    coverage_failed = bool(
        source.as_of is None
        or source.evidence_unreadable
        or (source.prescriptions is not None and not source.prescriptions)
    )
    return run_grader.Grade(
        scan=scan,
        source=source.path.name,
        findings_failed=findings_failed,
        coverage_failed=coverage_failed,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage=USAGE,
    options=(
        run_grader.Option("--show"),
        run_grader.Option("--draft", takes_value=True, missing_value=USAGE),
        run_grader.Option("--evidence", takes_value=True, missing_value=USAGE),
    ),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    return run_grader.run(GRADER, argv)
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
