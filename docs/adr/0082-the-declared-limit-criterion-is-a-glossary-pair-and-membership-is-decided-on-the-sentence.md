# The declared-limit criterion is a glossary pair and membership is decided on the sentence

[#667](https://github.com/mshamblin5150-code/clinical-skills/issues/667) was filed over
`CONTEXT.md`'s **Declared limit** entry stating what the shape *is* and nothing about what may go
in one, while the inclusion criterion lived in three ratified records and no glossary term:
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 3 states it,
[ADR 0070](0070-a-four-row-limits-object-takes-the-enumerated-skill-bind-the-sibling-s-size-refused.md)
applies it to derive a module's population, and
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 1 had to sharpen it a third time.

Grilled 2026-08-30. **Seven decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `a724f0b`

Freshness gate `FRESH` at both checkpoints. Four measurements, each of which moved a decision, and
three of them falsify something the ticket or a ratified record states.

**The ticket's option 2 names a mechanism this file does not use.** It proposes a sibling filed
*"with each `_Avoid_` naming the other"*. Across **123 terms**, exactly **one** `_Avoid_` line names
a sibling term — the one under **Sitting**, `session (in the agent sense — see **Session**)`. The file's
convention for a defined-against pair is a **body-level** `Distinct from a **X**` clause: **12** of
them, one of which is `Second route` pointing at `Declared limit` today.

**The excluded set is two shapes, not one.** ADR 0053 ruling 3 names `WHY_NO_WRITE_GUARD`,
`WHY_OUTSIDE`, `WHY_NO_PUBLISH` and `WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED` as one class,
*"declared rationale for a declined option"*. ADR 0074 ruling 1 has already moved the fourth in as a
limit. Of the three that remain:

| constant | sites | what it is |
| --- | --- | --- |
| `WHY_NO_WRITE_GUARD` | `adr_next`, `split_census`, `threshold_sheet` | passed to nothing; read only by tests. Rationale for an option that **was** declined. |
| `WHY_OUTSIDE` | `guidelines_build` ×3, `guidelines_extract`, `guidelines_index`, `guidelines_recs` | `ensure_outside_checkout(..., detail=WHY_OUTSIDE)` — the refusal's own printed message, naming the remedy |
| `WHY_NO_PUBLISH` | `artifact_provenance` | the same, asserted in stderr by three tests |

So *rationale for a declined option* is true of one of the three. The other two explain a decision
that **was** taken and are runtime refusal text. A sibling named for the declined-option case would
leave two of the three constants outside both terms — the pair failing its own worked calls.

**A dangling-cross-reference walk over this file cannot be built.** `CONTEXT.md` spends `**bold**`
on two jobs: **19** cross-references (23 occurrences, every one resolving) and **6** occurrences of
plain emphasis — `**not**`, `**There is one per checkout that has one, not one per repository**`,
and four further clauses. A broken cross-reference and an emphasized clause are byte-identical in
kind, so the only mechanical discriminator available is *does it resolve*, which makes the check
circular: whatever fails is declared emphasis and nothing can ever dangle. A word-count heuristic
does not rescue it, because the live emphasis set contains a **one-word** span.

**A latent sense collision predates this ticket.** The term **Declared**, in `### Tiers`, is a **tier** term — *a
value fixed by a stated rule rather than observed* — a different sense from the one in
`Declared limit`, `Declared no-binding` and `Declared non-source`. Ruling 3 adds a fourth term in the
second sense. The collision is filed rather than resolved here; it is ADR 0037's kind and #667's
*what must not come out of this* forbids widening into it.

**Three ratified quotations of the entry exist and the ruled draft breaks none.** ADR 0028 and
ADR 0053 ruling 3 both quote *a boundary of what a mechanism reaches*, and
ADR 0053 ruling 6 quotes *"points at the object and copies no row of it"*. All three clauses survive
verbatim.

**`Declared limit` is cited by name nowhere in `CLAUDE.md` or `AGENTS.md`.** Those files name
`WHY_NO_WRITE_GUARD` and several `DECLARED_LIMITS` objects and have never cited the glossary term.

## Ruled 2026-08-30

### 1. The repair is a pair, and the pair is written on the file's own convention

#667's option 2 — a sibling term filed against `Declared limit` — over option 1 (one entry gaining
the criterion) and option 3 (neither, leaving it record-held).

On this file's anatomy option 2 **contains** option 1: a defined-against pair is two bodies plus a
`Distinct from` clause, so `Declared limit` gains the criterion as a contrast and the sibling carries
the exclusion. Option 1 alone leaves a reader holding `WHY_NO_WRITE_GUARD` with nothing to look up,
which is how the mistake is actually made and is why ADR 0074 ruling 1 had to state the criterion a
third time.

**Option 3's #143 argument is real and misapplied.** #143's subject is a **figure** copied where
nothing re-derives it. The three records state the criterion *with* its reasoning and its worked
calls; a glossary entry states the boundary alone, which is the register none of them occupies and
the surface [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s arrangement
has the others point at rather than restate.

**The ticket's stated mechanism is corrected rather than adopted**, on the measurement above: the
pointer is a body-level `Distinct from` clause, not an `_Avoid_` line naming the sibling.

### 2. The sibling is named for the criterion's axis, not for one instance of it

Not `Declined-option rationale`. The term covers **any** named object beside a mechanism holding a
*why* rather than an unreached *what*, with declined-option rationale as one case.

The pair exists to answer one question — *may this sentence enter a limits object?* — and the answer
for `WHY_OUTSIDE` is no for identically the reason it is no for `WHY_NO_WRITE_GUARD`. Under the
narrow name, a reader holding `WHY_OUTSIDE` looks the sibling up, finds it does not fit, and is back
where ADR 0074 ruling 1 found them.

**Splitting the exclusion in two was refused.** A second term separating documentation-rationale from
printed refusal text would be keyed on a **delivery mechanism** — printed at refusal versus not —
which cuts across the membership question instead of answering it, and #667's *what must not come out
of this* forbids that widening.

**This is wider than ADR 0053 ruling 3's phrasing and does not contradict it.** That ruling's
operative content is that the four constants stay out. *Rationale for a declined option* was a
sufficient condition stated over the cases in front of it, not the boundary — the same
partial-instrument shape ADR 0074's *Measured before ruling* section records of this thread's own
sweeps, which published five different figures for one tree from unstated matchers.

### 3. The term is `Declared rationale`

The parallel with `Declared limit` is load-bearing rather than decorative, and it is the half most
easily got wrong: **both shapes are the same thing structurally** — a named object holding a
sentence, sitting beside the mechanism it is about. That shared structure is exactly why
`WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED` looked like it belonged outside and `WHY_NO_WRITE_GUARD`
looked like it belonged inside. So the shared word carries the shared structure and the differing
word carries the whole distinction, in the one line a reader hitting either entry sees.

`rationale` appears **nowhere** in `CONTEXT.md`'s prose, so this coins no
[#496](https://github.com/mshamblin5150-code/clinical-skills/issues/496)-third-kind
heading-against-prose collision.

**A bare `Rationale` was refused** for coining one deliberately: the word is common in the ADR
corpus, so a bare term makes every ordinary use read as the term — the class ADR 0041's *what this
does not reach* names. **A mechanism-keyed name** (`Mechanism rationale`, `Build rationale`) was
refused because the constants sit beside checks, commands and refusals alike and no mechanism word
covers the set.

### 4. What each body says, and the criterion lands in both halves

The two entries, ruled as drafted:

> **Declared limit**:
> A boundary of what a mechanism reaches, held as a named object beside that mechanism rather than as prose about it. What may go in one is a sentence telling a reader that a clean result covers less than it appears to. Prose points at the object and copies no row of it, so a limit that stops being true fails a check instead of standing as a claim nobody re-derives. Distinct from a **declared rationale**, which is the same shape holding a different sentence.
> _Avoid_: caveat, known issue, disclaimer, rationale
>
> **Declared rationale**:
> A named object beside a mechanism holding why it is built as it is — why an option was declined, or why a refusal refuses. The same shape as a **declared limit** and never a member of one, because it states a why rather than an unreached what. Which it is, is decided on the sentence and never on the constant's name: a `WHY_`-named constant carrying a coverage sentence is a limit, and a plainly-named one carrying reasoning is not.
> _Avoid_: declared limit, caveat, note, comment

**The criterion goes in `Declared limit` rather than only in the sibling.** Leaving it in the sibling
alone means a reader arriving at the entry three ADRs already cite by name still finds no inclusion
test — #667's headline defect surviving its own repair.

**ADR 0074 ruling 1's sentences-never-names rule is boundary, not argument, and it sits in the
sibling.** It says what the criterion is applied to; without it the pair is re-derivable wrong in
precisely the direction ADR 0074 was written to fix. It belongs on the **excluded** side because the
mistake is made while holding a `WHY_`-named constant and reaching for that entry.

**Nothing here restates ADR 0053 ruling 3's reasoning.** The worked calls, the `WHY_` census argument
and the four named constants stay at the records, on ruling 6's anatomy. The `_Avoid_` additions use
the `Sitting` → `**Session**` precedent — rejecting the sibling's word as a *name for this concept*,
which is what `_Avoid_` is for.

### 5. It is filed in `### Guidelines`, immediately after **Declared limit**

ADR 0041 ruling 1 applies unchanged: *a term is filed with the term it is defined against, and
section coherence loses to that.*

**The declared cost deepens by one and is restated rather than left to be re-found.** ADR 0041 ruling
1 accepted three figure-discipline terms under a section otherwise about the guideline corpus —
**Orphaned figure**, **Declared limit**, **Underived count** — *"accepted, not unnoticed."* This
makes it four.

`### Checks` was refused because it separates a term from the term it is defined against and puts the
two halves of one distinction in two sections — the failure #667 is filed over, rebuilt in the file
meant to fix it. **Coining a `### Figures` section was refused** on ADR 0041 ruling 2, which is
untouched by anything here, and on #667's *do not widen*.

Insertion between `Declared limit` and `Underived count` breaks nothing: ADR 0041 ruling 1
established that a `CONTEXT.md` cross-reference resolves **by term name within one file, never by
section or position**, and `Underived count`'s pointer at `Orphaned figure` already crosses two
entries.

### 6. A pair bind holds it, in a new module

Both terms present, each half carrying its pointer at the other, and `Declared limit` carrying the
criterion clause — through `ProseBind`, so hard wrapping and emphasis cannot decide the outcome. This
is `test_ruling_cohort.py`'s precedent: *assert the rule is still written where a reader will find
it.*

**It does not trip ADR 0053 ruling 6.** That ruling refused a second prose **copy of one sentence**
under a bind, on the ground that *a bind proves two strings match, never that either is true, so it
buys synchronized staleness.* These two halves say different things, so this is a presence bind
rather than a copy bind.

**Home is a new module, not `tools/test_glossary_terms.py`.** That file declares its subject as one
sentence — *every term in `CONTEXT.md` is defined exactly once* — and ADR 0041 ruling 4 refused
widening a module past its stated ceiling for exactly this reason, when it declined
`test_glossary_vocabulary.py` on its own `CODE_VOCABULARIES` ceiling.

**The general walk was refused on the measurement above**, not on taste: it is undecidable against
this file's markup.

**Two limits are declared with it.** It cannot tell whether either definition is **right** — ADR
0041's own residue, that nothing compares a body to the ADR that contributed it, unchanged. And a
body reworded to keep the phrase and lose the meaning passes.

### 7. It ripples no further than `CONTEXT.md` and the new module

**No addenda on ADRs 0053, 0070 or 0074.** An addendum that changes no ruling is three more
statements of one fact in the three records #667 was filed over for already holding it — #143
arriving inside the repair for #667, a shape this repo has recorded repeatedly. Those records rule
the criterion, the glossary now holds the boundary, and ADR 0041 measured that a record citing a term
**by name** survives any filing decision.

**No `CLAUDE.md` pointer.** Measured: there is no existing `CLAUDE.md` citation of any glossary term,
so this would coin that convention in the one file whose own record is that claims rot in it
unnoticed. The lookup path being built is the term name itself, reached from the constant or from the
record.

## What this does not reach

**Whether either definition is right.** One heading, one body and a pointer at the other half is all
the bind reaches; nothing compares a body to the record that contributed it. ADR 0041 already
declared this and it is unchanged.

**A body reworded to keep the phrase and lose the meaning.** The bind is a presence check.

**Every other cross-reference in the file.** The 19 live cross-references outside this pair remain
held by nothing, and the measurement above records why a general walk cannot be built against this
file's markup rather than leaving it to be re-proposed.

**The `Declared` tier-sense collision in `CONTEXT.md`'s `### Tiers` section.** Filed rather than
resolved; it is an ADR 0037 question and a clinician decision.

**A limits object built after this ruling that classifies by name anyway.** The criterion is prose a
reader applies. Nothing walks `tools/` deciding whether a given constant is on the correct side, and
ADR 0074 ruling 1 is the record of why a name-keyed instrument for that question is refused.
