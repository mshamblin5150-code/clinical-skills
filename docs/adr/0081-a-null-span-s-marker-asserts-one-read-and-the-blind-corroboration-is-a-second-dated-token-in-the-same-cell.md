# A null span's marker asserts one read and the blind corroboration is a second dated token in the same cell

[ADR 0025](0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md)
ruling 2 requires a span retired **having found nothing** to take a blind independent read, and
ruling 7 requires such a span to carry a dated marker in the sheet. Nothing asks for the first.
[#662](https://github.com/mshamblin5150-code/clinical-skills/issues/662) is that hole. Grilled
2026-08-30 against `origin/main` at `2abb8fa`, freshness gate `FRESH` at both checkpoints.
**Seven decisions, all the clinician's, all on that date.** Nothing is built here; this is the
record the build reads.

## What is ruled

1. **A span's dated marker asserts one read.** `read 2026-08-23` means somebody read that span and
   found nothing. It is not the blind read's trace, and it never was.
2. **A null span with no committed blind-read token refuses.** Not a warning, not a declared limit.
3. **The refusable unit is the span, never the sheet.** The `**Second read:**` prose block stays as
   the human summary and stays ungraded, on [ADR 0046](0046-the-scope-summary-is-graded-in-one-direction-and-the-unread-list-is-the-span-table.md)'s
   arrangement.
4. **The token is a suffix on the `read` cell**, `read <date>; blind <date>`, where `exempt:`'s
   reason already sits. The span table stays three columns and `threshold-sheet/2` does not move.
   The two dates may be equal.
5. **The refusal is its own reported gate line, `NULL SPAN`, and states its denominator on every
   run.** It is not a `SCHEMA` failure and it does not re-grade the marker's existence, which
   `gate_schema` already does correctly and keeps.
6. **All eight shipped null spans owe a token in one commit.** Five are discharged by transcribing
   prose that already names the span and its date; three take a real blind read.
7. **`CONTEXT.md` gains two terms, `Null span` and `Blind read`**, and they land with the build
   rather than ahead of it.

## Measured before anything was ruled, at `2abb8fa`

**Every gate is green on every sheet and no sheet supplies a read.** All five exit **0** with
`SECOND READ NOT RUN -- no --second-read given`.

**`**Second read:**` is graded by nothing.** `Read:` and `Not read:` are parsed; the string
`Second read` appears nowhere in `tools/threshold_sheet.py`. Three sheets carry the block and no
check reads a character of it.

**A null span is `has_dated_marker`, full stop.** `gate_second_read` sets
`null_span = span.has_dated_marker or span.exemption_reason is not None` and its own comment says
page overlap means a row can sit inside a null span without turning it positive. So a span with a
marker *and* rows cited in its range is still a null claim, which
`prediabetes`'s `recommendation statement and assessment | 1-2` demonstrates: four rows fall in its
range and belong to the overlapping `practice considerations | 2-3`.

**The ticket's evidence table is stale in every row and short by a sheet.** Re-derived with
`_rows_cited_within_span` over all five sheets:

| sheet | null spans | rows | `**Second read:**` |
| --- | ---: | ---: | --- |
| cervical-cancer | 0 | 15 | yes, 2026-08-29 |
| diabetes | 2 | 357 | yes, 2026-08-23 |
| prediabetes-type-2-diabetes-screening | 4 | 13 | yes, 2026-08-29 |
| hypertension | 1 | 316 | **none** |
| heart-failure-in-chronic-kidney-disease | 1 | **0** | **none** |

**The population is eight null spans across five sheets, and three are unbacked by any attestation
in their own sheet** — not the one the ticket names:

| # | sheet / span | marker | attested by |
| --- | --- | --- | --- |
| 1 | diabetes / disclosures | 08-23 | *"the disclosures and index were independently confirmed as null spans"* |
| 2 | diabetes / index | 08-23 | same sentence |
| 3 | prediabetes / 2021 supporting evidence | 08-29 | *"its separate read of the 2021 supporting-evidence span found no additional row"* |
| 4 | **prediabetes / 2022 recommendation statement and assessment** | **08-22** | **nothing** |
| 5 | prediabetes / 2022 supporting evidence | 08-29 | *"its separate read of the 2022 supporting-evidence span found no current USPSTF decision point"* |
| 6 | prediabetes / 2022 article information and references | 08-23 | *"independently confirmed as a null read on 2026-08-23"* |
| 7 | **hypertension / appendices** | **08-23** | **nothing** |
| 8 | **heart-failure-in-CKD / complete scope of work** | **08-29** | **nothing** |

`2026-08-22` occurs exactly once in that sheet — in the span row itself. Its block covers *"all five
newly retired spans"* as of `2026-08-29`, and that span was retired seven days earlier, so the block
does not reach it.

**The registry holds 169 topics, 164 of them `unread`**, which is the cost denominator for anything
enforced here.

**A column would be additive and a suffix costs less.** ADR 0061 added `source class` to
`## Sources` and kept the marker at `threshold-sheet/2` — *"gains a column"* — so a fourth span
column needs no version bump. But the span header is checked strictly against
`["span", "pages", "read"]`, so it costs a migration of every row of every sheet, and it would be
blank on **11 of the 19** span rows shipped today.

**`heart-failure-in-chronic-kidney-disease` is registry state `non-source`, which is not an escape.**
ADR 0061 ruling 4: *"A `non-source` topic is read like any other and carries a null-sheet artifact."*

**Nothing binds the two proposed glossary terms to code.**
`test_glossary_vocabulary.CODE_VOCABULARIES` holds **Source mode** and **Sweep state** and nothing
else, so ADR 0061's glossary-and-code-in-one-commit trap does not fire here.

## Why the marker asserts one read

The two records can be read against each other, which is how this survived. Ruling 2 says a null
span *takes a blind independent second read*; ruling 7 says it *carries a dated marker in the sheet
itself*, and its rationale explains the marker exists **because** the second-read JSON lives outside
the repo. Read together, one plausible reading is that the marker is the blind read's committed
trace — under which `hypertension.md` is compliant and this ticket closes as prose.

It is not, for two reasons.

`RENDERED:`'s precedent, which ruling 7 invokes by name, is an audit claim by **one** reader about
**one** act. Stretching a single date token to assert that two readers found the same nothing asks
one cell to carry the independence claim, and independence is the one claim this repo does not let a
single side make.

And the sheets already read it the other way. Three of five wrote a separate prose block to say a
blind read happened, which nobody writes if the cell already said it. `diabetes.md` dates its
markers `2026-08-23` **and** dates its blind reads `2026-08-23`, in two different places, because
they are two different claims that happened on one day.

## Why it refuses rather than warns or declares

ADR 0025 established the constraint that makes the ticket's own decision 1 unanswerable as written:
the hook runs `threshold_sheet.py` with no `--second-read`, so `SECOND READ` reads `NOT RUN` on
every commit and in CI, permanently. *Refuse* therefore cannot mean *refuse unless a record is
handed to the gate*; it can only mean **refuse unless the sheet carries a committed token**, which
is a gate over a sentence rather than over a read.

That is the posture `RENDERED:` already holds in this module. [#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296)
ruled that a gate-4 finding refuses until an agent renders the cited page and records the marker,
and the marker is an audit claim rather than a re-runnable check. **The claim here is weaker than
that one**: a page transcription at least ships the cell it licensed, and a null span ships nothing
at all.

*Warn* is the option this repo has repeatedly found worthless, and the proof is in the tree — the
`**Second read:**` block has been sitting in three sheets being read by nothing.

*Declare* inverts the effort ADR 0025 weighed explicitly. It would declare away the half with **no**
evidence while the half that already carries a verbatim snippet on a real page keeps two citation
tiers on it. The 164-topic cost is the cost of the rule ruling 2 already made; if that is too
expensive the honest move is to reopen ruling 2, not to leave it shipped and unscored.

## Why the unit is the span

Ruling 2 says the span, and both existing instruments are span-driven already: `gate_second_read`
takes one span and `brief()` prints a work order for one span name. But every sheet that volunteered
evidence wrote it as a per-sheet sentence, so the practice in the tree was sheet-level and the
question was live.

**The sheet unit's failure mode is not hypothetical; it is shipped.** `prediabetes` has four null
spans, its per-sheet block names three of them, and the fourth has no attestation anywhere in the
file. A sheet-level token would have passed that sheet, and did — the ticket's own table credits it
as compliant. Partial coverage reading as complete, arriving on the artifact built to stop it.

The prose block is not displaced. ADR 0046 already fixed this arrangement for `Read:` and
`Not read:`: **the prose is the human summary and the table carries the arithmetic.** That also
leaves the three volunteering sheets' narrative intact rather than rewriting it into cells.

## Why the token is a suffix and not a column

The blind read is meaningful only when `read` is a dated marker. It is not an independent axis of a
span; it is a qualification of one of the four things that cell can say — and the `read` cell
**already carries a qualifier for one of its own forms**, since `exempt:`'s reason lives inside the
cell rather than in a `reason` column, for exactly this reason.

A `yes` span, a `no` span and an `exempt:` span have nothing to put in a `blind` column. Blank would
have to mean both *not applicable* and *missing* unless the format demanded an explicit `n/a`, which
is ceremony on 164 topics' worth of rows. The suffix also keeps the two claims adjacent, so a reader
sees *read on X, corroborated on Y* as one sentence.

Two dates rather than one: the first is read #1's audit claim, which ruling 7 already ships and
which nothing here retires. Same-day is legal — an agent may discharge both in one session, and
`diabetes.md` already dates both `2026-08-23`.

A per-span line under the table was considered and refused: it joins by span name, needs its own
parser, and is what the ungraded `**Second read:**` block already is.

## Why it is its own gate line

Folded into `gate_schema`, a clean `cervical-cancer.md` and a clean `hypertension.md` both print
`SCHEMA 0`. One has no null span at all and the other has one, corroborated, and **the report cannot
tell them apart** — [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
ruling exactly, and the same indistinguishability this ticket was filed over, reproduced one level
down inside its own fix.

It is also a different kind of question. `read span '<name>' has neither rows nor a dated marker` is
well-formedness — does this cell say a legal thing. This one is an evidence claim about whether a
positive assertion has a second reader behind it, which puts it in `SECOND READ`'s family.

The line is named for the **population** rather than for the token, so it stays legible on a sheet
whose count is zero and does not read as a second `SECOND READ`. It fires only on markers
`gate_schema` has already accepted, so #662's *what must not come out of this* — a second grader for
the marker's existence — is respected.

## Why all eight, in one commit, with five transcribed

Landing a refusing gate against three unbacked spans turns `main` red and refuses any commit
staging those three sheets, so *gate now, readings later* is not available as written.

**Grandfathering by date was refused.** It is the declared-limit option re-entering through the back
door, aimed precisely at the three instances that motivated the ticket. Exempting the only spans
anybody has ever failed to corroborate makes the gate vacuous on arrival.

**Shipping the gate unenforced was refused** because it is this ticket's own subject, done
knowingly.

**Transcription adds no claim.** The prose was written by whoever performed the read, names the span
and carries the date; moving a figure the summary already states into the graded slot is ADR 0046's
ruling applied, not a new assertion. The three that need real reads are hypertension pp. 98-105,
heart-failure pp. 1-9 and prediabetes 2022 pp. 1-2 — **19 pages**, briefed cold through
`--brief --span`, by a reader that has not seen the sheet.

**ADR 0025 ruling 6's separation is not breached.** That ruling scopes *reading tickets* — the ones
that add rows and narrow the unread list. A blind corroboration of an already-retired span adds no
row and narrows nothing; it discharges the evidence for a retirement that already happened, which is
mechanism work by ruling 2's own placement.

## Why two glossary terms

The fuzz Q1 found was in the glossary and not only in the code, which is why the two records could be
read against each other for a week. `blind` appears three times in `CONTEXT.md` as an undefined
adjective — *"the blind second read of the catalog"*, *"the unit a blind second reader is briefed
on"*, *"when a blind independent read agrees it holds none"* — and the population the new gate counts
has been called four different things across the tree.

**Amending the existing terms was refused for the reason this session exists.** `Section read`
already carried the correct clause — *"when a blind independent read agrees it holds none"* — and it
did not prevent any of this, because a clause inside another term's body is not a thing a reader
looks up.

`Blind read` is also where ADR 0042's limit belongs: independence is **declared and unreachable**, so
the token is an audit claim and no check can confirm the second reader was a second reader. A limit
stated in a glossary term is read by everyone who looks the term up, which is an audience a
`NOT_REACHED` row does not have.

## Considered options

**Read the marker as asserting both reads.** Rejected in ruling 1. It closes the ticket for free and
buys the closure by letting one date token carry an independence claim.

**Warn and stay green.** Rejected. The tree already contains the experiment: three sheets volunteer
the evidence in prose and nothing has ever read it.

**Declare the limit.** Rejected. It declares away the only half of a section read that carries no
evidence.

**A sheet-level token.** Rejected on a live instance rather than on principle — `prediabetes` would
pass with one of four spans unbacked.

**A fourth `blind` column.** Rejected. Additive without a version bump on ADR 0061's precedent, but
blank on 11 of 19 shipped rows, ambiguous between *not applicable* and *missing*, and a migration of
every row of every sheet.

**A keyed per-span line beneath the table.** Rejected. It joins by span name, needs a second parser,
and duplicates the prose block.

**Fold the refusal into `gate_schema`.** Rejected. It loses the denominator, which is the defect one
level down from the ticket's own.

**Grandfather the eight by date.** Rejected. Vacuous on arrival.

**Ship the gate reporting-only, flip it later.** Rejected. A rule shipped unenforced is the subject.

**Require the blind date to differ from the read date.** Rejected without being filed. Two reads on
one day is ordinary agent work and `diabetes.md` already records it; a difference rule would invent
a constraint nobody ruled and refuse a correct sheet, which is
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect this repo has now
produced five times.

## Declared limits

**The gate grades a sentence and never a read.** `NULL SPAN 0 refusing` means every null span
carries a token claiming corroboration, not that anybody was corroborated. This is `RENDERED:`'s
posture and it is no stronger here.

**Independence is unreachable.** ADR 0042 already rules it. Nothing checks that the blind reader was
a second reader, that it was briefed cold, or that it did not open the sheet.

**A blind read is a smoke test in the clean direction.** `SECOND_READ_IS_A_SMOKE_TEST` says so for
gate 5 and ADR 0025 restates it for this. Two readers missing the same number agree.

**`exempt:` spans are outside the denominator and stay outside it.** ADR 0025 ruling 9 retires a
reference list by class and its declared limit says *"a span retired by class is not a span that was
read."* The three shipped `exempt:` spans are corroborated by nothing, by design, and the gate's
wording says *retired on a marker* rather than *null* so the line does not over-claim.

**The refusal does not reach `threshold_coverage.py`.** That module reports
`fails threshold-sheet/2 schema` off `gate_schema`'s findings, and `NULL SPAN` is a separate gate, so
a sheet failing only this passes the registry auditor. It is caught anyway — a staged sheet fires
`threshold_sheet.py --all` in the hook and in CI — but the registry auditor's report is not a
statement about it.

**Transcription inherits the prose's accuracy.** The five transcribed tokens are only as true as the
sentence they were copied from, and that sentence was written by the reader whose work it attests.

**Page coverage catches an omitted span, not a misdrawn one**, and this changes nothing about that:
a null span whose page range is drawn wrong is corroborated over the wrong pages by both readers.
