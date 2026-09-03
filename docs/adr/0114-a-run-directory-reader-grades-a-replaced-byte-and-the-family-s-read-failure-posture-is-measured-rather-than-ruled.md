# A run-directory reader grades a replaced byte and the family's read-failure posture is measured rather than ruled

Found while grilling [#838](https://github.com/mshamblin5150-code/clinical-skills/issues/838),
2026-09-02, at `origin/main` `398193d`, freshness gate `FRESH` at both checkpoints. **Ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

## Measured before ruling, at `398193d`

Every figure was re-derived by running the code rather than by reading it, and three of them
disagree with the ticket that prompted the grilling.

**Both of #838's limbs reproduce exactly as filed.**

```
python tools/refusal_scan.py <dir with one 0xFF byte>   -> UnicodeDecodeError, EXIT=1
python tools/refusal_scan.py <dir containing notes.md/> -> PermissionError,    EXIT=1
```

**The residue #838 attributes to `refusal_scan` belongs to the whole family.** One worksheet was
denied read with `icacls` and `anchor_scan` -- a sibling carrying *both* of the guards #838 asks
for -- was pointed at the directory:

```
PermissionError: [Errno 13] Permission denied: ...case-02.md
EXIT=1
```

The two guards close two members of the crash class. Every reader leaves the rest.

**#838's own `Done when` cannot be met by the repair it prescribes.** Byte 400 of a committed note
was set to `0xFF` and a sibling carrying `errors="replace"` was run over the directory:

```
block_scan  clean directory    EXIT=0
block_scan  corrupted directory EXIT=0   (notes at fault 0)
```

`errors="replace"` does not make a bad byte an unreadable artifact. It makes it `U+FFFD` and grades
the note. #838 asks for **exit 2** on that input; the guards give **exit 0**.

**The six readers are two bodies, not four shapes.** #839's table hashes body and docstring
together. Hashing the body alone, with the function name normalized away:

```
929346c7  anchor_scan  block_scan  differential_scan  filled_vitals_census  specificity_scan
39cc9511  refusal_scan
```

The other three "shapes" are entirely the docstring's `worksheet`/`note` and `run`/`set` nouns,
which is #839's decision 3 and a naming question rather than a body question.

**`refusal_scan`'s third divergence is equivalent rather than merely benign.** Every candidate name
the `*.md` glob admits was generated and both spellings evaluated:

```
globbed name           name!=readme.md  stem!=readme   agree
.md / a.md / case-01.md / notreadme.md / readme .md / readme.md.md   True   True   True
README.md                             False            False          True
DISAGREEMENTS: 0
```

**Fifteen members hold three verdicts on one question, and the split is date-correlated.** Taken by
walking each member's load path for an `errors=` argument and for a handler naming `UnicodeError`:

```
GRADE it (8)        anchor_scan  block_scan  case_study_scan  checks_ledger
                    differential_scan  reference_scan  research_ledger  specificity_scan
REFUSE, exit 2 (4)  deck_scan  discussion_post_scan  discussion_reply_scan  voice_model_scan
CRASH,  exit 1 (3)  aar_scan  refusal_scan  render_scan
```

Every module landing 2026-08-15 through 08-19 grades; every module landing 08-22 onward refuses.
**#838 as filed was following the newer convention and its five siblings follow the older one.**
Nothing ruled either. `filled_vitals_census`, the sixth run-directory reader and a
`NOT_MEMBERS` deferral, carries body `929346c7` and therefore grades a byte and crashes on the
residue like the five.

**The classifier over-matched once and was corrected by opening the file.** It reported
`reference_scan` as holding both verdicts; its `ValueError` handler is the `--as-of` date parse at
`tools/reference_scan.py:1391` and not a read, so it grades. The distribution above is the
corrected one.

**`refusal_scan` declares no exit-2 vocabulary and neither do 11 other members.** The
`exit_2_limbs` / `invalid_invocation_limb` pair is passed by `differential_scan`, `render_scan` and
`voice_model_scan` alone.

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. They move the day
a grader lands or a reader is extracted.

## Ruled 2026-09-02

### 1. A run-directory reader grades a replaced byte, and the ruling is scoped to that reader

A reader over the `.md` artifacts of one run directory treats an undecodable byte as **readable**:
it decodes with `errors="replace"` and grades what comes back, and the exit status is whatever the
artifacts say. It is not an [unreadable source](../../CONTEXT.md).

**The ground is that it reads a set.** `errors="replace"` is
[#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150)'s ruling read onto an input
stream -- *a legible line with a `?` in it rather than raise, because the thing being protected is
the exit status and not the glyph* -- and a set reader that refused would lose the other artifacts
in the run to one byte in one of them. The denominator is what the whole family's reports are
about, so destroying it is the more expensive error.

**The scope is the ruling and not a hedge on it.** Four members take the opposite verdict today and
none of them was in this grilling. Writing this family-wide in either direction would rule on
behalf of modules nobody read, which is the objection this session sustained four separate times,
and writing it the newer way would additionally reverse the ground ruling 2 rests on.

### 2. #838's repair is convergence and not improvement, and it includes the equivalent divergence

`refusal_scan.read_worksheets` adopts all three of the five's answers -- `errors="replace"`,
`path.is_file()`, and `path.stem.lower() != "readme"` -- and fills the docstring absence, so the
whole function becomes byte-identical to `anchor_scan.read_worksheets` and
`specificity_scan.read_worksheets`, whose `worksheet` and `run` nouns are both correct here.

**The README spelling is in because it is measured equivalent, not despite being benign.** Zero
disagreements means the `Done when`'s *stdout byte-identical on every committed directory* is
untouched and no existing test moves. Landing only the two behavioral guards would leave the body
still its own, and the *one correct body to converge on* that both #838 and #839 cite as the reason
for this ordering would not be delivered -- #838 landing first would then have bought nothing over
landing second.

**The residue is out of scope and the ticket's title says so.** A real file `open()` refuses still
exits 1 here after this lands, as it does in nine other members. The title and `Done when` are
amended to claim only what the repair delivers, because a closed ticket claiming a class was
cleared is worse than an open one.

### 3. The family's read-failure posture is measured and deliberately left unruled

Sixteen readers disagree three ways on the byte and two ways on the file `open()` refuses. That
question goes to its own ticket, and **it is ruled with or before #839 decision 1** rather than
after it.

**The coupling is conditional, which is why it is a dependency and not a merge.** #839 decision 1
is where the shared reader lives. A ruling of *grade the byte, and each caller's `_load` converts
the residue* leaves the shared reader with no failure channel and decision 1 untouched; a ruling of
*the shared reader itself refuses* binds it, because `SourceError` lives in `run_grader` and
`filled_vitals_census` is a non-member that cannot import the runner to raise one. Neither record
may be ruled in ignorance of the other, and the dependency is written on both.

**It is not folded into #839 and the reason is the populations.** #839 touches six readers and its
`Done when` is *each member's stdout byte-identical before and after*; a behavior ruling over
sixteen readers inside it contradicts its own landing terms and puts that ticket in the position
#838 was just taken out of.

### 4. `refusal_scan` gains no exit-2 vocabulary, and that is ruled rather than skipped

#838's decision 2 was conditional on the repair raising `SourceError`. Ruling 1 means it raises
none, so the antecedent is gone and adopting the vocabulary would be a seam change arriving inside
a bug ticket.

[ADR 0113](0113-the-per-grader-report-frame-is-affirmed-a-second-time-and-the-shared-report-value-is-declined-on-measurement.md)
affirmed per-grader divergence where the divergence reflects a ruling, and measured this exact pair
as three of fifteen, born in the #405 migration. The module's docstring does carry an informal
two-limb vocabulary in prose that nothing holds, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape; it goes on the
read-failure ticket, where it can be ruled against the family rather than against one module.

## What this does not reach, declared rather than left to be found

**The residue, in ten members including this one.** A real file `open()` refuses still exits 1 --
the status this family reserves for a finding -- in `aar_scan`, `anchor_scan`, `block_scan`,
`checks_ledger`, `differential_scan`, `reference_scan`, `refusal_scan`, `render_scan`,
`research_ledger` and `specificity_scan`. #838 closing does not clear that class and its amended
title is what stops the closed ticket reading as though it had.

**The four members that refuse a byte.** `deck_scan`, `discussion_post_scan`,
`discussion_reply_scan` and `voice_model_scan` take ruling 1's opposite, and `voice_model_scan`
declares a `MODEL_ABSENT` exit-2 limb for it. Ruling 1 is scoped away from all four and says
nothing about whether they are right.

**Whether the date correlation is a policy that drifted or a coincidence.** It is a fact about
sixteen landing dates and this record does not read a cause into it. The read-failure ticket is
where that is argued.

**Whether the convergence stays converged.** Ruling 2 makes six bodies agree and nothing holds the
agreement. A test pinning two modules' agreement forbids the divergence a copy exists to permit,
which is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s rule, and
whether this agreement may be forbidden is #839's premise rather than #838's. The ratchet arrives
with the extraction that makes it meaningful, and until then the body is correct and unheld --
which is the status quo for all six today.

**The `SourceError` docstring's second sense of *tier*.** It reads *a tier-1 failure* while
`CONTEXT.md` owns *tier* for note content, and `test_glossary_collisions` cannot see it: its
declared limit is that only `CONTEXT.md` is inspected, and this sense lives in code prose. The
glossary's new **Unreadable source** entry carries `tier-1 failure` in its `_Avoid_` row, which
gives the next author a word to reach for instead; rewording the docstring is a source edit and
goes on the read-failure ticket.
