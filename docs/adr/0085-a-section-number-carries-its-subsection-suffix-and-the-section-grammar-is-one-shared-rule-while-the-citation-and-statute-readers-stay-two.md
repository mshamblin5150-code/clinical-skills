# A section number carries its subsection suffix, and the section grammar is one shared rule while the citation and statute readers stay two

[#674](https://github.com/mshamblin5150-code/clinical-skills/issues/674) reports that a C.F.R. section carrying a subsection suffix defeats every limb of [#497](https://github.com/mshamblin5150-code/clinical-skills/issues/497)'s fix, so APA form and a resolving citation are mutually exclusive again. Grilled on 2026-08-30. Every measurement below was taken in process at `0d26b95`, with the freshness gate `FRESH` at both checkpoints. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement retired the ticket's headline and kept every one of its defects

The ticket's own title says the two are mutually exclusive again. They are not. Measured on a subsectioned regulation with a **full APA regulation name in the entry**, with nothing fixed:

| in-text form | `reference_scan` | `discussion_post_scan` |
| --- | --- | --- |
| `(26 C.F.R. § 1.501(c)(3)-1, 2026)` — what the live run wrote | **exit 1** `uncited-entry` | **exit 1** `untraced-number: 3` |
| `(Organizations organized and operated…, 2026)` — [ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md) ruling 1's canonical parenthetical | **exit 0** | **exit 0** |
| `Organizations organized and operated… (2026)` — ruling 1's canonical narrative | **exit 1** `uncited-entry` | — |

**Row 2 is a form that is both APA-correct and clean through both graders today, with nothing built.** It is not a workaround: it is the exact form ADR 0039 ruling 1 already declares canonical. So *"a run must choose between an APA-correct reference list and a clean grader"* is false, and the ticket's *"what the live run had to do — truncate the regulation's name"* is false with it. **A compliant path existed and the run did not take it.** It wrote ruling 1's *declined* branch, the Bluebook-flavoured section form, and hit the wall ruling 1 exists to steer around.

**That retires the framing and none of the defects.** Ruling 2 is an explicit promise that a section-form citation resolves against its own entry — *"the section **is** in the reference list"* — and the promise is broken for every subsectioned regulation. The fix below is owed because a shipped ruling does not hold, not because a run is blocked.

## The root, and the fourth consequence the ticket does not name

`LEGAL_AUTHOR`'s section pattern is `\d+(?:\.\d+)*`, which stops at `1.501` and leaves `(c)(3)-1` outside the span. Driven in process:

```
in-text  (26 C.F.R. § 1.501(c)(3)-1, 2026)
  span    '26 C.F.R. § 1.501'
  key     ('26cfr1501', '')
  leaked  '3', '1', '2026'  ->  _numeric_values
```

**The ticket's account of its own third consequence is wrong, and a builder reading the body edits the wrong function.** The body says the entry and the citation *"still fail to pair"*. They pair — the entry truncates to `26cfr1501` too, so both sides produce the same key. What fails is **record allocation**: the three leaked digits become three extra `untraced-number` requirements, and `_maximum_record_matching` allocates claim records to requirements in list order with every number built before every citation. Reproduced in both directions — with a claim record whose text does not carry those digits the result is `untraced-number: 3, untraced-citation: 0`; make the record carry them, which is what a real record about `1.501(c)(3)-1` does, and it becomes `untraced-number: 2, untraced-citation: 1`, **reporting a correctly-sourced citation as untraced**.

**The fourth consequence is a silent false negative on a defect row.** ADR 0039 ruling 5 detects a nameless legal entry by `LEGAL_CITATION.fullmatch(author_text)` — the author slot is the section and nothing else. Truncate the span and the leftover `(c)(3)-1` defeats the `fullmatch`, so on `26 C.F.R. § 1.501(c)(3)-1 (2026).` with no regulation name the predicate returns **False** and the row prints `legal-reference-name: 0`. **The row #497 built to catch a nameless legal entry has been blind to every subsectioned one since it shipped**, and the blindness reads as checked.

## Ruling 1 — the section grammar admits a subsection suffix, and the range case is declared rather than guarded

The tail is `(?:\([\w]+\))*(?:-\d+)?`.

I expected it to swallow the APA year in `42 C.F.R. § 414.56 (2025)` and it does not: **the space is the discriminator**, because a subsection is welded to its number and an APA year never is. So the guarded variant — a `(?!(?:19|20)\d{2})` lookahead — buys nothing and costs a rule that has to stay right. Measured:

| written in the post | today | with the tail |
| --- | --- | --- |
| `26 C.F.R. § 1.501(c)(3)-1` | `…§ 1.501` | **whole** |
| `45 C.F.R. § 164.512(b)(1)(v)` | `…§ 164.512` | **whole** |
| `42 C.F.R. § 414.56 (2025)` | `…§ 414.56` | `…§ 414.56` — year untouched |
| `42 C.F.R. § 414.56` | unchanged | unchanged |

With the tail in both readers, the **full suite runs 4,163 tests with 0 failures and 0 errors**, 3 skipped. The ticket's stated risk — a wider span eating surrounding text — appeared in no shape that could be constructed against the tree.

**The declared residue is a section range.** `§§ 414.56-414.60` has `-414` taken by the `(?:-\d+)?` limb. Nothing in the tree writes one, and it costs a character in a span nothing keys on. Declared rather than guarded, because a guard for a shape nobody writes is a rule that can only be wrong.

## Ruling 2 — the section grammar is one shared constant; the citation and statute readers stay two

`discussion_artifact.LEGAL_AUTHOR` and `discussion_post_scan.STATUTE` went wrong here in the same way, which is the ticket's argument for merging them. **They are not the same rule and the difference is deliberate.** `LEGAL_AUTHOR` requires both `C.F.R.` and the `§`, and decides *this is a citation*. `STATUTE` makes the `§` optional and carries a second branch for a bare `§ 482.13`, and decides *these digits are a section number, do not ask for a claim record*.

The second is deliberately looser because being loose is **safe** there: over-stripping a number costs a missed `untraced-number`, while over-matching a citation manufactures a finding on correct prose. Measured, wholesale unification does exactly that:

| prose | the ruled narrow reader | wholesale unification |
| --- | --- | --- |
| `The rule at § 1.501(c)(3)-1 is the operative one.` | no citation | **citation** `§ 1.501(c)(3)-1` |
| `Section 3 of the plan sets § 5 as the floor.` | no citation | **citation** `§ 5` |
| `The 42 C.F.R. 414.56 schedule was reissued.` | no citation | **citation** `42 C.F.R. 414.56` |

A citation keyed `5` resolves against nothing, so unification manufactures a finding on correct prose — the direction ADR 0039 rejected twice.

**What genuinely is one rule is the section-number grammar**, and [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test splits the two halves cleanly. A run writing `(b)(1)(v)` must be read the same way by both readers, so that piece exists to be depended on; the outer citation-versus-statute shapes must be allowed to diverge, and a shared object over the whole pattern would forbid the very divergence that keeps `§ 5` out of the citation set. The constant is exported from `discussion_artifact` and imported by `discussion_post_scan`, at the width of the piece that must agree — `reference_scan` importing `docx_write.REFERENCE_HEADING`, rather than at the width of the whole rule. **The reason `STATUTE` is the looser of the two is written down beside it**, because the next reader's instinct will be to tighten it.

## Ruling 3 — both readers change, because neither subsumes the other

The ticket asks whether the year capture and the numeral leak are one fix or two. They are one grammar and two edits, and the shapes they cover are disjoint:

| body form | widen `LEGAL_CITATION` only | widen `STATUTE` only | both |
| --- | --- | --- | --- |
| `(26 C.F.R. § 1.501(c)(3)-1, 2026)` | clean | **leaks `3`,`1`,`2026`** | clean |
| `Under 26 C.F.R. § 1.501(c)(3)-1 (2026)` | clean | **leaks** | clean |
| `Under § 1.501(c)(3)-1` (no `C.F.R.`) | **leaks `3`,`1`** | clean | clean |

Row 3 is the one that forces the second edit: the bare-sign form is reachable only through `STATUTE`'s second branch, and no widening of the citation reader touches it.

## Ruling 4 — the nameless-entry false negative is folded in, not filed

It costs no edit beyond ruling 1 — the predicate is already written and already correct, and was being handed a short string. **The in-flight cost measures zero**: across 221 Markdown files under `scratch/` and `output/`, 66 lines mention `C.F.R.`, 15 carry a subsection, and the count flagged nameless is 2 before the widening and 2 after, with none ceasing to be flagged. So nothing already written acquires a new refusal.

Filing it separately would produce a ticket carrying no code, `ready-for-agent` for a change that had already landed. It gets its own named test and its own line in the build spec, because a behavior that arrives for free is a behavior nothing pins.

## Ruling 5 — the misattributed `untraced-citation` is its own ticket

Ruling 1 removes the trigger: no legal shape leaks digits, so nothing in #674's report survives the fix. **What survives is the mechanism.** The loser of a contended allocation is decided by list position, and every number requirement is built before every citation, so a genuine shortfall of claim records is reported against a citation, systematically, saying *"citation occurrence 2 has no source-matched claim record"* when the honest sentence is *"this post is one claim record short."*

```
two number requirements + one citation, all pointing at one claim record
  matched:   [0]        the first number
  unmatched: [1, 2]     the second number, and the citation
```

It is a different root — an allocation and reporting policy, not a grammar — it has no live trigger once ruling 1 lands, and the repair is a decision about what the report *says* rather than a mechanical fix. Folding it in would mean building against a symptom this ticket has already removed.

## Ruling 6 — #674 is not gated on #678, and the asymmetry belongs there

[#678](https://github.com/mshamblin5150-code/clinical-skills/issues/678) reports `reference_scan` blind to legal entries and exiting 0. Both accounts are true of different entry shapes: a **nameless** entry parses with an empty key and is guarded out, exit 0, which is #678's measurement; a **named** entry — the one ADR 0039 rulings 1 and 5 make mandatory — keys fine, is cited by a legal citation the scanner cannot read, and exits **1** on `uncited-entry`.

The table at the head of this record is the consequence: ruling 1's two blessed spellings are **not equally usable**. The parenthetical is clean through `reference_scan`; the narrative is refused. That is a real constraint on a shipped ruling and it is `reference_scan`'s to fix, so it is recorded on #678 rather than here. Because the parenthetical path is green, #674 has a compliant route today and is `ready-for-agent` rather than `blocked`.

## What none of this reaches

**Whether the cited subsection says what the draft claims.** The refutation pass in `skills/discussion-post/SKILL.md` owns that, and it has no carve-out for legal primary sources. Nothing here reads a regulation.

**Whether ruling 1's narrative spelling is usable.** Measured as refused by `reference_scan` and handed to #678. Until that lands, the parenthetical is the only spelling clean through the whole chain, and no ruling here says so in the skill.

**A section range.** Declared under ruling 1, guarded by nothing, written by nobody in the tree today.

**Whether faculty mark the in-text spelling.** Unchanged from ADR 0039 ruling 2 — declined on the absence of evidence, not on evidence of absence.

**Why the live run chose the declined branch.** The run wrote a form ruling 1 had already declined, and nothing in the skill or in either grader stopped it or said so. Whether that is a skill-text gap is not settled here.
