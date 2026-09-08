# A pointer is not a source and a failed read is not a negative

Out of [#818](https://github.com/mshamblin5150-code/clinical-skills/issues/818), grilled on
2026-09-08. Measured at `43e0a45`.

Two failures on one `discussion-post` run of 2026-09-02, both caught by the clinician rather than by
anything in the toolchain. An orchestrating context read a memory store, reported a seven-value
leadership doctrine to him as **his own written doctrine**, and proposed building a section of a
graded post on it; six of the seven phrases appear zero times in his 62,488-message export in any
role. A verification context briefed to cross-reference those entries searched one corpus, found
nothing, and reported the claim **false**; the speech text was on disk the whole time.

A third arrived on 2026-09-05, in a session grilling a different ticket. A research sub-agent
returned HTTP 403 on eight `kdigo.org` URLs and the session published `UNKNOWN` for KDIGO; plain
`curl` returns 200 and 84 KB for the same URL.

The three are one subject: **a claim asserted more widely than the thing that was actually opened.**

## What was measured before ruling, on 2026-09-08

**The briefs carry neither requirement.** A tree-wide search of `skills/` for the requirement's own
phrasings returns one hit, in `skills/practicum-case-study/SKILL.md`, and it is about UpToDate
homoglyphs defeating `docx_read.py`. The nearest approach to a bounded negative is
`skills/discussion-post/SKILL.md:168`, `STATUS: sourced | unsourced - <what was searched>`. The
nearest approach to requirement 1 is `skills/practicum-case-study/SKILL.md:291`, *"Not a content
farm and not a summary of a summary"* — which constrains what class of **source** is acceptable and
says nothing about material recalled from a store carrying a sentence.

**The graders have no vocabulary for either.** `tools/research_ledger.py` and
`tools/checks_ledger.py` contain **zero** occurrences of *memory*, *summary*, *instrument* or
*negative*. The only two hits for *provenance* in either file are denials —
`checks_ledger.DECLARED_LIMITS` reads *"CHECK/VERDICT/FINDINGS carries no provenance about which
artifact the reader opened."*

**`STATUS: unsourced` is weaker than the ticket thread assumed.** `_unsourced_findings` fires two
rows: the remainder after the keyword must carry an alphanumeric, and no citation field may be
populated. `research_ledger.DECLARED_LIMITS`'s `reason-substance-unverified` states the rest —
*"Alphanumeric substance cannot prove that a stated search or reason happened."* The string
`not found` satisfies the row.

**The closed vocabularies, at `tools/research_ledger.py`.** `STATUSES = (SOURCED, UNSOURCED)` at
`:195`, two values. `REFUTATION_VALUES = (REFUTATION_STANDS, REFUTATION_REFUTED,
REFUTATION_PAYWALLED)` at `:177`, three values.

**The surface is nine briefs across seven skill files, not the two the ticket names.**
`discussion-post`'s research and refutation fan-outs, its differentiation reader and its vision
render reader; `discussion-reply`'s research and refutation; `course-assignment`'s refutation and
its adversarial investor read; `practicum-case-study` step 3's research-with-refutation and step 9's
eleven-reader fan-out; `icd10-cpt`'s blinded specificity verifier; and `aar`'s classifier.

**No shared brief document exists.** `skills/_shared/reference/` holds six files — `apa7.md`,
`rubric.md`, `style.md`, `voice.md`, `voice-corpus.md` and `word-renderer-calibration.json`. None is
a brief. Two mention a fan-out in passing.

**All nine surfaces already restate the same four structural rules in their own words**: prewrite
the headings before spawning, one writer to the ledger and it is the spawning context, the second
reader is never the one that wrote the record, and serial fallback where the harness has no subagent
tool. Four rules, nine copies, no check between any of them.

**And the nine are a family rather than nine spellings of one rule.** `icd10-cpt/SKILL.md:178`
briefs its verifier **blinded** — given the code numbers and forbidden the worksheet, descriptor,
anchor and specificity line. `practicum-case-study` step 9's readers are handed the whole draft. At
least one member is deliberately stricter than the rule a shared copy would state.

**The existing second-instrument requirement does not reach the failure, and the two briefs fail
differently.** `skills/discussion-post/SKILL.md:203` requires the clinician's Authenticated route
*"before … writing `STATUS: unsourced` because an **access wall** stopped the search"*; the KDIGO 403
was not an access wall but a public static PDF, so that trigger never fires.
`skills/practicum-case-study/SKILL.md:607-609` writes the same rule with the broader trigger *"because
the body was inaccessible"*, which **does** fire on a 403.

**Neither helps, because both name one specific second instrument and it is the wrong one.** The
Authenticated route is the clinician's signed-in Chrome — a subscription remedy. A public document
that returns 403 to one fetch tool and 200 to `curl` is not reached by it, so an agent that takes the
prescribed route and still fails writes `unsourced` compliantly. Rule (ii) is therefore not a
widening of this rule's trigger; it is a different rule about instruments rather than about walls.

**Rule (i) has already been invented three times locally.** `STATUS: unsourced - <what was
searched>`; the vision reader's `UNSEEN:` block for pages it could not open; and
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255)'s substantiated `clean` on
seven of step 9's thirteen rows.

**A refuter with a broken instrument deletes a correct claim.** `REFUTATION_VALUES` covers a wall
with `paywalled` and covers nothing for a 403 on a public document, so the available word is
`refuted` — and `REFUTED_CITATION` is a failure row. A false `unsourced` loses a claim nobody had; a
false `refuted` removes one that was sourced, verified and right. `SECOND-ROUTE` does not reach it:
it compares the *research* route with the *refutation* route, not a first instrument with a second
after a failure.

**`CONTEXT.md` already holds half the vocabulary and none of the other half.** **Established empty**,
**Second route** and **Authenticated route** are filed. There is no entry for *pointer*,
*provenance*, *negative*, *memory* or *recall*.

**Not re-derived**: the 62,488-message export evidence, which is external and lives outside every
checkout. Four prior sweeps on this thread recorded the same boundary.

## Ruling 1. The subject splits by surface, and this record takes the fan-out half

[#771](https://github.com/mshamblin5150-code/clinical-skills/issues/771)'s sweep measured four
published false figures in one session and **four of four were written by the orchestrating session
directly**, into an ADR ruling, a ticket body and a tracker comment. None is a fan-out. None is even
a skill run, so no brief in `skills/` could have fired on any of them.

The ticket's title asserts the opposite and its own evidence falsifies it. So the fan-out binding is
ruled here, and **publication-time binding across ADRs, ticket bodies and tracker comments is a
separate ticket** — a different file, a different reviewer, and a different gate.

Keeping them together is why this ticket has stood through five sweeps.

## Ruling 2. A pointer is not a source, and the discriminator is retention rather than recorded provenance

Anything recalled from a memory store, a summary, an index or a prior run's notes is evidence that
something may exist. Before it may carry a sentence in a graded artifact it must sit in one of two
arrangements:

- its primary material is **retained** and the artifact is gradeable against it; or
- its primary material is **resolvable and was independently re-opened** by a second pass.

Anything in neither is a **pointer**. It may direct a search. It may not carry a sentence.

**The thread's standing repair is superseded.** Four sweeps converged on *the distinguishing
property has to be a recorded provenance chain rather than the word summary*, because requirement 1
as drafted would forbid citing a `reference/uptodate/` sheet, which
[ADR 0132](0132-the-uptodate-store-is-scratch-rooted-and-its-published-topic-sheets-carry-the-entitlement.md)
ruling 4 makes citable. That repair fails its own worked example. Had the memory entry recorded
`summary of the 2026-08-14 conversation on leadership`, it would carry a recorded provenance chain
and its doctrine would **still** be an AI composition, six of seven phrases appearing zero times in
any role. A chain says where a thing came from. It does not say the thing is what it says it is.

**What actually makes a topic sheet safe is retention plus grading**, and ADR 0132 ruling 8 lists it:
*"required fields present, the year matching the topic's own last-updated line, a parseable currency
stamp, a retrieval date on or after the dump date, a `uptodate.com`-shaped URL, and the verbatim
share inside a declared cap."* The dump is kept, with a digest, and the sheet is re-checkable against
it at any moment. The memory entry never was. Ruling 10 of the same record refuses a constructed slug
on the ground that `RESOLVED` means the URL the agent actually opened, which is the same
distinction one field down.

**Both limbs already exist in the tree.** This invents no mechanism; it names which of two existing
arrangements a derived artifact sits in.

## Ruling 3. A negative is two rules with different triggers, not one clause

The 2026-09-06 sweep proposed that the requirement *"absorb a second clause about instruments"* and
warned in the same comment that absorbing failures one clause at a time is how a requirement ends up
describing the last failure rather than the class. Both halves of that are right, and the resolution
is that these are two rules:

1. **A search that ran and found nothing** reports the corpus it read and what it did not open.
   Fires on every negative and costs one clause.
2. **A search that did not run is not a negative.** An instrument that refused — a 403, a timeout, a
   login wall, or ADR 0134 ruling 7's *"200 over a page with no content"* — has produced no evidence
   about the subject. It is retried with a second independent instrument, and where that also fails
   the record says the source could not be read, never that the thing is not there.

**One clause cannot carry both.** Under a widened rule 1 the KDIGO subagent writes *"not found;
corpus = kdigo.org, instrument = WebFetch"*, which is compliant and still false. Labeling a 403 does
not repair it. Rule 2 fires only on failure, so it adds no boilerplate to the ordinary case, and it
is the only one of the two that would have caught the run.

**Most of the sweep's other species leave with ruling 1.** Truncated input, self-inclusion and mixed
populations were all published by an orchestrator into an ADR ruling and a ticket body. They belong
to the spawned ticket, not here.

## Ruling 4. The rules are written once, in `skills/_shared/reference/sourcing.md`, and nine surfaces point at it

The home must be consumer-reachable, because a fan-out brief runs inside a skill, and
`skills/_shared/reference/` is the only shared directory that ships. None of its six files fits.
`evidence.md` collides with **Evidence store** and **Evidence dump**; `claims.md` collides with the
ledger filename.

**Duplication is refused on [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s
recorded ground** — two copies of one rule where a prose edit to either fails nothing, and the reader
misled is whichever checked the file nearer to hand. With two tickets and nine briefing surfaces, the
duplicated form is up to eleven copies rather than the two the ticket imagines.

**All nine point at it**, one line each, deleting nothing. The evidence that this is a general rule
rather than a fan-out rule is that rule (i) has already been invented three times independently, in
three different local dialects, by three different parts of the tree.

**`aar`'s classifier is the non-obvious member and is deliberately included.**
[ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 2 briefs it to read the memory index by design — *"the only artifact that can distinguish we
never knew this from we knew this and did not look."* It is the one fan-out in the tree whose brief
requires it to handle derived material, so requirement 1 is load-bearing there rather than
precautionary.

## Ruling 5. Requirement 1 and rule (i) are declared; rule (ii) is graded

**Requirement 1 is not gradeable.** A record built on a pointer fills every field convincingly. It
takes a `research_ledger.DECLARED_LIMITS` row.

**Rule (i) is not gradeable either, and refusing to try is the load-bearing half.** The only place to
put it is the `unsourced` remainder, and grading it means hunting for corpus-shaped wording.
[ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md) ruling 2
already refused exactly that for route-shaped wording — *"which has no honest general text pattern"*
— and `discussion_post_scan.NOT_REACHED` declares the shape. It takes a declared-limit row.

**Rule (ii) is graded, and not by a text matcher.** See ruling 6.

A matcher over the remainder was available and is refused, on the extractor-coverage rule and on
`guidelines_catalog.py --draft`'s standing position that a guessed answer is worse than a blank one.

## Ruling 6. `STATUS` gains a third value, `unreadable`, and the branch owes both instruments

`STATUSES` is a closed two-word vocabulary. A claim whose search was refused by its instrument is
neither member: it is not sourced, and `unsourced` asserts that a search ran and came back empty.
**There is no word for the state, so the agent writes the nearest one** — which is the 2026-09-05
failure exactly.

That is a ratified pattern rather than an invention here.
[ADR 0138](0138-an-absent-committing-scratch-root-is-nothing-to-grade-and-the-empty-population-rule-is-not-generalized.md)
ruling 8 filed a glossary term for the identical gap: *"**Unreadable source** and **Unreadable body**
both name the subject could not be obtained; nothing named there is no subject. That gap is the most
likely reason the census conflated them — there was no word for the state it was in."*

**The word is `unreadable`**, reusing `CONTEXT.md`'s existing **Unreadable source** with the actor
widened from a grader to a research agent. One concept, two subjects.

**No instrument in the tree fires on that widening, and the first draft of this ruling said one
does.** It claimed the sense collision goes to `test_glossary_collisions.DECLARED_CANDIDATES` for a
verdict. Re-derived by running the detector rather than reading it: `candidate_headings` fires only
on a **bare single-word** heading whose word also appears inside a compound heading. Thirteen fire at
`43e0a45` and all thirteen are declared. **`Unreadable source` and `Unreadable body` are both
compound, so neither can ever be among them**, and `Pointer` does not fire either because no compound
heading uses the word. Widening one entry's scope is invisible to that walk by construction.

So the verdict on this sense is the clinician's, taken on 2026-09-08 and recorded here, and **nothing
will fail if it stops being right.** That is this record's own subject arriving inside it — a
mechanism asserted to cover something it cannot reach — and it was caught by running the tool.

**The green suite could not have caught it, and naming why is the transferable part.** A passing
`test_glossary_collisions` is what a declared collision produces *and* what an invisible one
produces, so the instrument prints the same thing under the claim and its negation. That is
`CLAUDE.md`'s discrimination rule, which reached `main` at `b2b1881` hours after this defect was
made and after it was found: a measurement settles a claim only where the instrument would report
differently if the claim were false. The discriminating read was not the test run but
`candidate_headings`'s own predicate, which requires a bare single-word heading.

**`unreachable` is refused.** ADR 0134 ruling 8 records that exact word being written into the tree
as a settled property and withdrawn. `unread` is the coverage registry's sweep state, `blocked` is a
triage label, and `paywalled` is already a `REFUTATION` value meaning something narrower.

**The record is clean at record level.** It obtained no source, so it carries no `REFERENCE` and
behaves downstream exactly as `unsourced` does — the claim survives only as uncited reasoning. The
one thing that can fail on the branch is the second-instrument declaration, graded on ADR 0042
ruling 3's shape: two substantive halves that must differ after normalization.

**Where a second instrument genuinely was not available, the truthful entry is the identical pair and
the row firing is correct.** That is ADR 0042 ruling 4 taken whole rather than answered a second way.

## Ruling 7. `REFUTATION` gains `unreadable` too; it passes and is counted on its own line

Without it a refuter with a broken instrument has only `refuted` available, and `REFUTED_CITATION` is
a failure row that deletes a sourced, verified, correct claim on the strength of an instrument
artifact.

**Widening `paywalled` to cover it is refused.** ADR 0042 ruling 4 warns that *"blessing a
`paywalled` escape sentence rebuilds the hatch: one sentence, satisfying every substance test,
available verbatim to the self-clearer,"* and ruling 5 ties `paywalled` to the Authenticated route
having been attempted, which has nothing to do with a 403 on a public PDF.

**It passes**, on `paywalled`'s treatment, and the completion report counts it on its own line so a
clean exit never stands for such records silently. The state justifies it: the research agent opened
the page and recorded `RESOLVED` with a read date, so one instrument reached the document and a
second did not. That is an unverified claim, not a disproved one.

**Failing it was available and is refused**, because it re-creates the defect through a different
row — a broken instrument again destroying a correct claim, with a different word on the tombstone.

## Ruling 8. ADR 0134 ruling 9 is generalized beyond the currency registry

That ruling reads *"a fetch tool's refusal is a fact about the tool until a second instrument
agrees,"* and it is scoped to `guidelines_currency.py`. Rule (ii) is that sentence applied to a
research fan-out.

**These records do not generalize themselves, and 0134 is the proof.** Its own *not settled* section
declines to stretch ADR 0132 ruling 10's Chrome authorization one inch past `uptodate.com`. Without a
numbered ruling here, the next sweep is entitled to read rule (ii) as an unratified extension of
another record's scope.

## Ruling 9. The four structural rules are not centralized here

`sourcing.md` holds these two rules and nothing else. Absorbing the four rules already duplicated
across all nine surfaces is a separate ticket **with a measurement as its precondition**.

[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) refused this move for
`keyword_of` on the ground that *"a test pinning the agreement would forbid the divergence the copy
exists to permit"*, and the divergence here is already visible: `icd10-cpt`'s verifier is not merely
a different context from the writer, it is blinded. Centralizing before anyone measures whether the
nine are one rule is how a correct local tightening gets flattened.

Pointing nine files at a new file adds a line and deletes nothing. Absorbing four rules deletes local
text and reconciles divergence. They are different changes and only the first is ruled here.

## Ruling 10. The two instruments get their own field, on both `unreadable` branches

Added 2026-09-08, hours after the first nine, because the clinician asked when #818 could be
labeled `ready-for-agent` and the answer was **not yet**: rulings 6 and 7 require the branch to name
both instruments tried, this record's *does not settle* section conceded no slot was chosen, and the
build list nonetheless asked for the row. An agent could reasonably have picked three different
answers, which is the `ready-for-agent` bar failing on a gap this record created.

**`INSTRUMENTS: <first> -> <second>`.** Required on a `STATUS: unreadable` record and on a
`REFUTATION: unreadable` record, forbidden elsewhere, and graded on `SECOND-ROUTE`'s existing shape:
two substantive halves that must differ after normalization.

**Reusing `SECOND-ROUTE` was the cheap option and is refused.** `CONTEXT.md` already gives that term
the instrument sense — *"The access path **or instrument** a refuting pass used that the pass it is
checking did not"* — so the reuse is closer than it looks. What stops it is the rest of that
definition: it is a comparison between **two passes**, and a `STATUS: unreadable` record has no
refutation to compare against. The two halves would mean *how the research and refutation passes
differed* on a sourced record and *what one failed read tried* on an unreadable one. That is one
field answering two questions, which is the defect this repository has paid for most often.

**Putting it in the `STATUS` remainder is refused too.** The reason and the instruments would share
one string, so the substance test and the pair test fight over it, and grading a `->` pair inside a
prose reason is the text-matching ruling 5 declined for rule (i).

**On an `unreadable` refutation both fields are present and say different things, and that is the
honest shape rather than a collision.** `SECOND-ROUTE` says how the two passes differed;
`INSTRUMENTS` says what the failed read tried.

**Where a second instrument genuinely was not available, the truthful entry is the identical pair and
the row firing is correct** — ADR 0042 ruling 4, applied here as it is in ruling 6.

**`CONTEXT.md` gains `Instrument`**, because this ruling turns on a word the glossary does not
define, and **Second route** and **Authenticated route** are both filed while the thing they are
made of is not.

## What this record does not settle

**Whether any check can catch a record built on a pointer.** Ruling 5 declares it unreachable and
nothing here narrows that.

**Whether the nine briefing surfaces are one rule or a family.** Ruling 9 names the measurement and
does not take it.

**What binds a claim published outside a skill run** — an ADR ruling, a ticket body, a tracker
comment. Ruling 1 sends it to its own ticket with four measured instances behind it.

**Whether `unreadable` is the right glossary sense or a collision to be split**, and **nothing checks
it**. Ruling 6 records why the existing detector cannot reach a widened compound heading. Whether
that walk should reach within-entry sense widening at all is a separate question and is not opened
here.

**Whether a `STATUS: unreadable` record should record the locator it failed to open.** `RESOLVED`
means a URL that was opened and read, so it cannot carry one. Ruling 10 settles where the
**instruments** go and deliberately does not settle the **locator**: `INSTRUMENTS` names what was
tried, not what was aimed at.

**The export evidence behind failure one**, which is external to every checkout and re-derivable by
nothing committed.
