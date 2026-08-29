# A declared non-source is an enumerated class and it earns a fourth sweep state

[ADR 0057](0057-the-corpus-sweep-is-comprehensive-and-every-ruling-it-needs-is-already-ruled.md)
ruling 8 was ratified with no ticket owning its build, which its own tracker sweep found and filed
as [#587](https://github.com/mshamblin5150-code/clinical-skills/issues/587). Grilled 2026-08-29
against `origin/main` at `923ad0f`. **Six decisions, all the clinician's, all on that date.**
Nothing is built here; this is the record the build reads.

**The freshness gate refused mid-session.** `main` advanced from `1face6f` to `923ad0f` between the
last ruling and this record being written, so every figure below was re-derived at the new base
rather than carried across. What landed ([#629](https://github.com/mshamblin5150-code/clinical-skills/issues/629),
ADR 0060) touches receipt bindings and no threshold artifact, and no figure moved — but that is a
result of the re-derivation rather than a reason to have skipped it.

## What is ruled

1. **A declared non-source is an enumerated set of source classes, never a predicate over
   *not a guideline*.** The set is `{scope-of-work}`.
2. **Nothing joins the set.** `errata` and `web-capture` are ordinary sources that carry their cell
   and nothing more.
3. **The coverage registry gains a fourth sweep state, `non-source`.** The class fork runs *before*
   the zero-row fork, so a declared non-source never reaches the `none`/`sheet` decision at all.
4. **A `non-source` topic is read like any other and carries a null-sheet artifact**, with a
   declaration of its own. The `none` declaration and the `non-source` declaration are mutually
   refusing.
5. **The sheet's cell is `source class`, placed beside `document`**, and the positional fallback in
   the `## Sources` parser is retired.
6. **`draft` surfaces through a named row of [practicum-case-study](../../skills/practicum-case-study/SKILL.md)
   step 9's check table**, bound by `checks_ledger.EXPECTED_CHECKS`. `differential_scan` is not
   coupled to the `## Sources` table here.

## Why the rule is a set and not a predicate

ADR 0057 states its own ruling twice and the two are not the same rule. Ruling 8 names one class:
*"A source whose class is `scope-of-work` is a declared non-source."* Its **Consequences** paragraph
widens that to *"a source that is not a guideline cannot produce one"* — and it is the wider form
that was copied into `CONTEXT.md`'s **Sweep state** term.

The difference is 90 documents. Re-derived at `923ad0f`:

```
recommendation-statement  90   guideline  83   web-capture  3   errata  1   draft  1   scope-of-work  1
```

**The wider form forbids the first `none` its own sibling ticket schedules.**
[#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483)'s *Out of scope* names
`latent tuberculosis infection screening` (USPSTF 2023, `page_count 8`) as the first reading ticket
for a `none` topic. Its catalog class is `recommendation-statement`. So the sentence shipped in
`CONTEXT.md` today rules out the topic #483 already picked, and rules out the corpus's largest
class — the class where a USPSTF I statement makes a legitimate `none` most likely to be earned.

The third option, keying on whether a document *holds no clinical quantity by design*, is
unbuildable: that is a reading and not a cell, and #587 build item 1 requires the value be fed from
the guideline catalog rather than typed.

An enumerated set also makes each further class an explicit decision rather than something that
falls out of a predicate, which is what turned the next two into findings instead of presumptions.

## Why nothing joins the set

**ADR 0057's errata sentence is falsified in both halves, by reading the document.** The record says
*"The errata needs none of this. Its topic is named (corrections) and nobody will lean on it."*
`IDSA/ciab275.pdf` is two pages. One half is an author-affiliation correction. The other half is a
**revised babesiosis treatment table** — atovaquone 750 mg orally Q12h, azithromycin 500 mg then
250 mg Q24h for 7 to 10 days, clindamycin 600 mg, quinine sulfate 650 mg, a full pediatric mg/kg
column — plus a changed clinical rule stated in prose: where IV azithromycin 1000 mg is given,
*"subsequent doses should be reduced to 500 mg daily,"* and the clindamycin and quinine dosing
intervals are revised. It is not empty and it is exactly the kind of thing somebody leans on.

**And the document it corrects is not in the corpus.** The parent is `ciaa1216`, IDSA's 2020
babesiosis guideline; the catalog holds `ciaa1215` (Lyme) and no babesiosis guideline. So this
two-page corrigendum is the corpus's entire babesiosis holding — a correction with no corrected
document behind it.

That is a strong argument for calling it a non-source and it is the wrong argument. **The orphaned
parent is a fact about corpus membership, not about document form.** Keying it on `class` would
declare every future errata a non-source on evidence drawn from one, which is the generalization
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) is about. It is filed
separately instead.

**`web-capture` was never considered by ADR 0057 or by #587, and it is three documents and three
sole-source topics** — `adult immunization schedule`, `childhood and adolescent immunization
schedule`, `childhood immunization schedule`. The ACIP captures open by reciting a court order:
the schedule is *"stayed"* pending `American Academy of Pediatrics et al. v. Kennedy et al.`, the
posted schedule is July 2 2025 *"as amended on April 27, 2026"*, and the page calls itself a
*"Guide for individuals."* The catalog `year` is `?` for all three. They hold clinical content, so
they are sources; they are the class whose cell earns its place most obviously.

So the affected-topic list is **six** rather than the three ADR 0057 names, and it is derived from
the catalog rather than typed.

## Why a fourth state, and why `unread` is closed rather than merely worse

#587 decision 3 asks for a fourth state to be argued for rather than defaulted into, on the ground
that it is the expensive answer. Measured at `923ad0f`, **the `state` column has exactly one
consumer in the tree**: `tools/threshold_coverage.py` itself. Nothing else in `tools/` reads it.
`differential_scan` keys on the **artifact** column, which #483 established and which re-derives at
`differential_scan.py:810-817`. So the code cost is one tuple at `threshold_coverage.py:22`, one
branch in #483's derivation, and one count line that `:219` prints automatically. The expense is a
fourth word in the registry's vocabulary, not a change to a consumer.

**Parking the row at `unread` is not available.** ADR 0057 ruling 4 sets #429's completion condition
as *"the ticket closes when `python tools/threshold_coverage.py` reports `unread 0`."* A row parked
at `unread` by design never leaves it, so that option converts the sweep into a thing that cannot
finish, silently. Ruling 1 says the same from the other side: *"`unread` is a defect to be burned
down and not a resting state."* A declared non-source is a resting state by construction.

`none` is closed by ruling 8. Dropping the topic from the denominator was rejected by ADR 0057, and
its stated reason argues only about the draft's 499 pages — but it fails independently: the topic
population is derived from the catalog, so an exception would be a hand-kept list beside a derived
population, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) at the
place this directory is most careful about.

The word is `non-source` because it names what the row asserts about the **document**, which is the
distinction that separates it from `none` — a claim about a completed **read**.

## Why a declared non-source is still read

The cheap option is that the catalog cell is the whole evidence: no read, no artifact, nine pages
saved. It is refused on three grounds.

**The read is the tripwire on the declaration.** This session measured
`KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work` at **zero quantity-shaped tokens across all
nine pages** — no comparison-and-number, no `mg`, `mmHg`, `mL/min`, `kg/m2`, `%`, `mmol`, `g/dL`.
That measurement is what makes ADR 0057's premise true, and it was not in the tree. Without the
read, *holds no clinical quantity by design* is a claim about a **class name** and never about a
document, and the next scope of work KDIGO publishes inherits the verdict unopened. That is this
repository's most-recorded failure shape — a check that could not have worked, answering like a
settled negative — arriving on the one row whose whole purpose is to prevent a false negative.

**Every other sweep state is backed by a span table.** A state resting on a catalog cell alone would
be the sole row where page coverage does not apply, with nothing saying so.

**And it would leave the original defect standing.** `differential_scan` joins on the artifact
column, so a `non-source` row with no artifact joins nothing and a Plan item on heart failure in
chronic kidney disease writes `recalled, no shipped sheet` uncontradicted — the hole #483 was filed
over, reproduced one state along. A null sheet is what lets a run be told that KDIGO has not
published this guideline, which is the true and useful answer.

**The two declarations must refuse each other.** #483 mandates the null sheet's `## Thresholds`
declaration verbatim: *"**No decision point.** Every span in `## Scope` has left the unread list and
this source states no quantity that changes what is done to a patient."* On a `non-source` sheet
that sentence is true and says the wrong thing — it reads as **read and found empty**, which is the
`none` claim ruling 8 forbids, written on the artifact's own face. So a `non-source` sheet carries
its own declaration naming the form, and `threshold_sheet.py` refuses each wording on the other's
state. Otherwise the two are distinguishable in the registry and indistinguishable in the artifact a
reader opens.

## Why the cell is `source class` and why the fallback goes

**The word is already taken inside the same file.** `ROW_COLUMNS` at `threshold_sheet.py:379` is
`(quantity, population, value, snippet, source, page, rec, class)`, and that `class` is the **class
of recommendation**, graded against `record["cor"]` at `:2680` — the one gate that catches a row
pinned to the wrong recommendation. Two columns spelled `class` meaning two unrelated things, in one
artifact a clinician opens, is the two-answers-one-word failure this tree names repeatedly.

`CONTEXT.md` has already had this collision and settled it by naming: the term is **Source class**,
and the **Source mode** entry's `_Avoid_` line already reads *"also avoid source class, which
answers a different question."* So the disambiguating name is the tree's own, not an invention.

Renaming the `## Thresholds` column instead was rejected: it touches `ROW_COLUMNS`, the `cor`
grading and every row of four shipped sheets, and it costs the sheet the word AHA/ACC itself uses.

**Adding the fifth column is what makes a documented hazard live.** `threshold_sheet.py:966-975`
reads the Sources table by name against its header row with a positional fallback,
`"mode": named.get("mode", cells[-1])`, and the comment beside it states the reason: *"`mode` was
`cells[-1]`, so appending a column to this table would silently redefine the cell that decides
refuse-versus-warn."* The fallback fires whenever the header's first cell is not exactly lowercase
`key`, in which case the header row is itself parsed as a source row. Append the new column last and
that fallback makes a source's **mode** read `guideline`, and nothing validates `mode` against a
vocabulary unless a recommendation record is loaded — which more than twenty affected topics do not
have. The fallback is retired and an unreadable `## Sources` header refuses.

## Why `draft` gets a reader and not a consumer change

ADR 0057 rules that a draft's numbers ship **labeled rather than suppressed**. The chain after that
is: an agent reads 499 pages, rows land in a sheet, a Plan item cites `[thresholds/<sheet>:...]`,
`differential_scan` confirms the citation joins a shipped topic, and the paper carries a number from
a public review draft as guidance in force. Nothing in that chain says *draft* except the cell.

Refusing such a citation is closed by measurement: **the KDIGO public review draft is the sole AKI
source in the corpus**, so a refusal would refuse the whole holding — ADR 0057's rejected
*drop the draft* option arriving through the consumer instead of the denominator.

Leaving it at the cell reproduces the defect ADR 0057 indicts in its own words — *"nothing therefore
says a draft's numbers may not ship as thresholds"* — one artifact along, on a cell nobody is
required to read. ADR 0057 ruling 9 already establishes the remedy for exactly this shape: assign
the reading to a **named row** of step 9's check table, where `checks_ledger.EXPECTED_CHECKS` makes
a run that returns no verdict fail. That is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail*.

Coupling `differential_scan` to the sheet's `## Sources` table — reporting a **candidate**, never a
finding, where a cited topic's sole source is a non-`guideline` class — is attractive and mechanical,
and it is deferred rather than refused. It changes a consumer in a ticket whose subject is a format,
which ADR 0057's own Consequences already separates; and it cannot be built until a draft-backed
sheet exists, which is the last item in the reading order. Filed separately.

## Consequences

`threshold-sheet/2` gains a column and `threshold-coverage/2` gains a state, so both schema markers'
owners have work that is not #429's. A fourth sweep state means every reader of the registry learns
a fourth word, and the registry's report gains a fourth count line and its qualifier.

**The fourth state and the glossary move in one commit or the suite goes red**, and that was found
by running it rather than by reading. `tools/test_glossary_vocabulary.py`'s `CODE_VOCABULARIES`
binds the backticked list in `CONTEXT.md`'s **Sweep state** term to `threshold_coverage.STATES`, in
both directions, and it reads *every* backticked token in that term's body. So the word cannot be
written into the glossary ahead of the code even as an aside. This record's own session tried it,
on the precedent that the **Source class** term already describes ruling 8 ahead of its build --
which holds, because that term states prose and this one declares a vocabulary. The glossary carries
the ruling in prose and a link, and the list gains its fourth value when `STATES` does.

**The vocabulary is published in four places and one of them is bound**, which the same run
surfaced. `CONTEXT.md`'s term is bound; `AGENTS.md`, and the directory README twice — once as the
bulleted definition and once as prose — are not. `AGENTS.md` is the file a consumer reads and needs
no tool for, so it is the copy whose staleness is least checkable by whoever is misled by it.
[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md)
names the three as well and is history rather than a fifth copy: it is superseded here, not
falsified.

`none` is bounded on two sides, and the second side is narrower than ADR 0057 said: it is a claim
about the **named source documents** and never about the topic, and a source whose class is in the
declared-non-source set cannot produce one. It is not the case that only a `guideline` can.

#483's build item 2 gains a branch that runs before its three-way fork, and the branch is where its
two zero-row cases are told apart. Its first reading ticket is unaffected and was never at risk from
ruling 8 itself — only from the wider sentence.

Two records are corrected in place on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms: ADR 0057's Consequences sentence, which over-reached its own ruling 8, and ADR 0057's errata
sentence, which is a factual claim this session falsified by reading the document. No ruling of ADR
0057 changes.

## Rejected

- **Keying the rule on *not a guideline*.** Forbids the corpus's largest class and #483's own first
  `none` topic.
- **Keying it on whether a document holds no clinical quantity by design.** A reading, not a cell;
  not derivable from the catalog, which build item 1 requires.
- **`errata` as a declared non-source.** It carries a full revised dose table; the orphaned parent
  that tempts the ruling is a corpus-membership fact rather than a form fact.
- **`web-capture` as a declared non-source.** Holds a schedule; suppressing it would drop three
  topics' only material.
- **Parking the row at `unread`.** Makes ADR 0057 ruling 4's completion condition permanently
  unreachable.
- **Dropping the topic from the registry denominator.** A hand-kept exception beside a derived
  population.
- **Naming the cell `class`.** Collides with the class of recommendation in the same file, and
  appending it last walks into the parser hazard the source file documents in a comment.
- **Refusing a citation to a draft-backed topic.** Refuses the corpus's only AKI material.
