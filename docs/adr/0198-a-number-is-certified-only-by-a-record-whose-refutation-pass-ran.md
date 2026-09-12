# A number is certified only by a record whose refutation pass ran

Out of [#981](https://github.com/mshamblin5150-code/clinical-skills/issues/981), grilled on
2026-09-12. Supersedes part of
[ADR 0153](0153-a-sourceless-record-claims-no-source-and-a-certifier-reads-the-status.md) ruling 3.

**Measured at:** 7c555b7e8e579991c74f1a06a9329d72a472a2a5

A claim record whose second agent never ran could certify a figure in a graded submission. ADR 0153
ruling 3 taught the number certifiers to disbelieve three sourceless states and left field
completeness to the ledger grader by name, so a record carrying a recognizable `sourced` status and
no refutation at all was fully believed.

The grilling found the ticket's ground had moved in one direction and its reasoning was wrong in
another. The population the ticket measured is not the population any certifier reads, so the
defect's live instance count is zero rather than 48 — and the reason ADR 0153 gave for refusing a
field test is not what a field test costs.

## What was measured before ruling, on 2026-09-12

**Every certifier loads one file, by exact name.** `deck_scan.py:298`, `discussion_post_scan.py:768`,
`discussion_reply_scan.py:577` and `peer_critique_scan.py:412` each resolve `claims.md` against the
run directory:

```
bar_path, claims_path, rendered_path = root / "bar.md", root / "claims.md", root / "rendered.md"
claims_path = root / "claims.md"
```

**So the ticket's population is wider than the certified one, and the whole defect sits in the
remainder.** Across every registered checkout:

| population | files | sourced records | sourced carrying no substantive `REFUTATION` |
| --- | ---: | ---: | ---: |
| `claims*.md` anywhere under a scratch root | 12 | 1,329 | **48** |
| `claims.md`, the name every certifier loads | 8 | 696 | **0** |

All 48 are in `scratch/runs/nur5042-m5-course-assignment/claims-pre-refutation.md`, a snapshot taken
before the refutation pass, whose name appears nowhere in `skills/`, `docs/` or `tools/`. The
`claims.md` beside it holds 701 records and none without a refutation.

**One glob produced three premises in ADR 0153, and all three are measured over files no command
loads.** Per file rather than per glob, in that one run directory:

| file | records | `DATE:` | loaded by |
| --- | ---: | --- | --- |
| `claims.md` | 701 | `2026-09-03` | every certifier |
| `claims-staged-2026-09-03.md` | 615 | absent | nothing |
| `claims-pre-refutation.md` | 49 | `2026` | nothing |
| `claims-arithmetic-2026-09-03.md` | 0 | — | nothing |

So ADR 0153's *48 live records*, its ruling 6 sentence that *the larger of the two `course-assignment`
ledgers was never graded, having no `DATE:` header*, and its 1,436-record denominator are each true of
a snapshot and false of the run's ledger. That record gains an in-place correction and the
measurement defect behind it is filed separately, because *which file is the ledger* has a different
answer per artifact family: `scratch/runs/nur5144-m1-case-study/` carries no `claims.md` at all, only
the two dated ledgers ADR 0040 and ADR 0052 both cite.

**ADR 0153's stated cost of a field test is not what a field test costs.** Its refusal reads
*"importing the bar, the `as_of` date and most of `record_findings`"*. An AST walk over
`_contract_findings` with its docstring stripped reports the names its body reads, and neither `as_of`
nor `recency_window_years` is among them; taint-propagated across assignments, **24 of the 28
record-level rows are dateless and bar-free**, and only `READ_AFTER_DATE`, `STALE_UNEXCUSED`,
`STATED_EXPIRY_REACHED` and `UNKNOWN_SOURCE_CLASS` are not. The refusal is therefore sound for rows
and unsound for fields.

**What a row-based predicate would actually import is a bar decision nobody named.** Driven on one
record differing only in its source class, under `record_findings(record, None)`:

```
SOURCE: market source      default bar -> unknown-source-class   full vocabulary -> clean
SOURCE: society guideline  default bar -> clean
```

The default is `SOURCE_CLASS_VOCABULARY[:-1]`, which excludes the class ADR 0110 added for deck runs.
A row-based predicate would therefore make `deck_scan` disbelieve exactly the market-source records a
business-plan deck exists to use, and the clinical control shows the difference is the class rather
than the record. ADR 0153's refusal survives on this measurement rather than on its stated one.

**The live cost of each candidate, per ledger — the unit a certifier builds a believed set from.**

| predicate | records disqualified | tokens a certifier stops believing | heading-only certifier |
| --- | ---: | ---: | ---: |
| as shipped | 0 | 0 | 0 |
| refutation verdict present | 0 | 0 | 0 |
| verdict and second route present | 9 | 26 | 8 |
| all nine required sourced fields present | 9 | 26 | 8 |

The last two are identical, so the choice between them is about the rule's reason and not about what
breaks. All 9 are in two ledgers dated `2026-08-23`; both fields entered the module on `2026-08-28` in
`dca159bb`, so they are five-day vintage rather than a run that skipped a required field.

**The 48 name the pair rather than anybody choosing it.** Their absent-field profile is exactly
`('REFUTATION', 'SECOND-ROUTE')` — the two fields a refutation pass writes — because the file is the
snapshot taken before that pass. The other live profile is `('SECOND-ROUTE', 'STATED-EXPIRY')`, which
is the vintage above.

**ADR 0153 ruling 3's *no new finding kind* left a false message behind, and it is live on `main`.**
Driven through `_claim_records` on one record differing only in the fields that decide belief:

```
sourced / stands       traced numbers=['42']
unsourced              traced numbers=[]
sourced / refuted      traced numbers=[]
```

`42` is on the page of `claims.md` in all three, and the message a reader gets is the literal at
`discussion_post_scan.py:1122`:

```
f"{value} is absent from claims.md"
```

`deck_scan.py:487` says `$<amount> has no claim record`, equally false. The `sourced / stands` control
traces the token, so the instrument discriminates: the difference is the disbelief and not the parse.
The row texts carry the same defect, and the module that does not call the predicate at all has the
honest one — `peer_critique_scan.py:88` reads *"every body numeral traces to a believed claim
record"*, while the three callers promise a trace to `claims.md`.

## Ruling 1. The disqualifying incompleteness is the refutation pair, and nothing wider

A record certifies a figure only when it carries **both** halves of the second agent's evidence: the
refutation verdict, and the differing route that verdict was reached by. Either absent, and the
record certifies nothing.

**The rule is chosen for its reason, on ADR 0153 ruling 1's own pattern.** That ruling refused *omit
the other fields* as a format convention stating no reason and took *make no claim about a source*
because it states one. The reason here is **no figure is certified by a record the refutation pass has
not been through**, and the test for a field is *does its absence mean the second agent's check is
unrecorded?* It admits the verdict and the route and excludes the other seven.

**The verdict alone is half the rule.** A record reading `REFUTATION: stands` with no route still
certifies a figure whose check may have been the first agent re-reading its own page, which is
`REFUTATION_ECHOES_RESTATEMENT`'s defect one field over. The route is written as two halves precisely
so independence can be compared, and a record that never wrote it has not recorded one.

**Requiring all nine is refused at equal live cost.** It disqualifies the same 9 records and loses the
same 26 tokens, so it buys nothing measurable, states no reason, and is the formulation that later
grows toward rows — which the measurement above shows is where a bar decision enters unannounced.
`STATED-EXPIRY` is the plain case: its absence is #498's row and says nothing about whether the source
supports the figure.

**The pair is named by the corpus and not by the ruling.** It is the absent-field profile of the
pre-refutation snapshot, so the population that exposed the defect is also what bounds the fix.

## Ruling 2. The pair lives in `research_ledger` and its complement is derived from it

`REFUTATION_EVIDENCE_FIELDS` sits beside `REQUIRED_WHEN_SOURCED`, and
`claim_record_can_certify_values` imports it on the local import the module already makes. ADR 0153
ruled `research_ledger` the one owner of both vocabularies and their keyword parser; the pair is
vocabulary, so it goes there and the predicate imports rather than restates, on `reference_scan.py`'s
`REFERENCE_HEADING` precedent that this predicate was built on.

**A test asserts the pair and its complement partition `REQUIRED_WHEN_SOURCED`.** That is the answer
to creep: a field cannot join the pair without leaving the complement, so a reviewer sees seven become
six rather than a tuple quietly gaining a line. It is `skills_mirror.py`'s two-way reason property —
a third category makes the summary stop adding up, and that is the one thing a reader checks it
against.

**The three declared-limit rows derive their residue text from the complement rather than naming it.**
They read *"whether a sourced record missing required fields is still believed"* today, in
`discussion_post_scan.py:158`, `discussion_reply_scan.py:133` and `deck_scan.py:89`:

```
"whether a sourced record missing required fields is still believed",
"A sourced record missing required fields is still believed by the cost certifier; field completeness belongs to research_ledger.",
```

This ruling makes all three false at once for two of the nine, and they are three hand-kept prose
copies of one claim where an edit to any copy fails nothing. Deriving them closes
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape before it arrives
rather than after the copies drift. `peer_critique_scan` declares no such row and is not touched here;
that is [#1056](https://github.com/mshamblin5150-code/clinical-skills/issues/1056).

## Ruling 3. The refusal keeps its kind and gains a second detail

`UNTRACED_NUMBER` and `UNTRACED_COST` keep their kinds. ADR 0153's reasoning for adding none survives
and is not reopened: the refusal is identical, the exit status is identical, and the remedy is
identical — the run repairs the record or drops the figure.

**What does not survive is the detail.** It is chosen by whether the token appears in *any* claim
block, believed or not. Absent from every block keeps `is absent from claims.md`; present in a block
the certifier disbelieved gets a detail saying so. Every certifier already walks every block, so the
second set is accumulated in the existing walk and the predicate keeps its `-> bool` signature
untouched — which is what lets `peer_critique_scan` adopt it under #1056 without inheriting a reason
parameter.

**A new kind was refused on two grounds.** It buys a reader nothing the detail does not, and it would
make the two refusals separately suppressible, which is the one property a gate here should not gain.

**The row texts adopt the honest form.** The three that promise a trace to `claims.md` say what
`peer_critique_scan.py:88` already says — *every body numeral traces to a believed claim record* — and
that wording is now what the code means rather than what one module happened to write.

## Ruling 4. ADR 0153 ruling 3 stands for rows and is superseded for the pair

That ruling's refusal of *anything `research_ledger` would refuse* is upheld, on the `market source`
measurement rather than on the bar-and-date reason it gave. What is superseded is the narrower clause
placing the pair outside the certifier: *the 48 live records missing a `REFUTATION` are a
field-completeness defect that the ledger grader already owns, and having a certifier re-derive it is
the rejected option through a side door*. The pair is not re-derivation of the ledger grader's
judgment — it is the certifier reading the one thing that says its evidence exists.

**`refuted` and the two sourceless states are untouched**, and so is `paywalled`, which remains the
weakest disposition that certifies. **Ruling 4 of ADR 0153 is untouched**: this applies to a record's
figures and never to its reference keys, because removing a key stops a narrative citation being
recognized and reports a cleaner body rather than a dirtier one.

## Ruling 5. The live records are not repaired

The 9 records in `scratch/runs/nur5042-m2-discussion/claims.md` and
`scratch/runs/nur5144-m1-discussion/claims.md` begin failing and stay as they are, on ADR 0153
ruling 6. Both ledgers predate the two fields by five days, the refusals are additive, and a preserved
run record is not edited so a tool passes. A later run of either artifact writes the compliant shape.

## Ruling 6. The rule is written once, in the shared sourcing reference

`skills/_shared/reference/sourcing.md` gains the sentence, on ADR 0153 ruling 5 and
[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md) ruling 4's
arrangement. The briefing surfaces point at it and carry no copy, so the four skills cannot come to
state it two ways — which is the defect ADR 0153 found in the omit clause and is why that ruling put
the rule in one file rather than choosing between two phrasings.

## What this record does not settle

**Whether a believed record's restatement supports the figure traced from it.** Unchanged from
ADR 0153: this decides which records a certifier reads and asserts nothing about whether their content
is true.

**Whether the recorded refutation is a real second agent's.** The pair is graded for presence and
substance. A verdict and a route written by the first agent satisfy both, and
`REFUTATION_ECHOES_RESTATEMENT` and `SECOND_ROUTE_UNCHANGED` reach only the echo and the identical
pair. The ledger grader owns that reading and this record does not widen it.

**Whether a figure in a graded submission is certified by `peer_critique_scan`.** That module calls no
predicate and is #1056's, not this record's. Its row text promises a believed record and its code does
not read one, which is the one place the promise and the behavior still disagree after this lands.

**Which file is the ledger, per artifact family.** A certifier resolves `claims.md` by name while
`practicum-case-study` points the ledger grader at a path, and a case-study run in the live corpus
carries two dated ledgers and no `claims.md`. The glob that produced three false premises is filed
rather than fixed here.

**Whether the seven fields outside the pair ever matter to a certifier.** They are excluded by ruling
1's reason, not deferred. Reopening one means showing its absence leaves the second agent's check
unrecorded, which is a different argument from showing it is required.
