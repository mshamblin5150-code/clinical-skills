# The run-directory reader is extracted into the runner and refuses a source it cannot open

Found while grilling [#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839) and
[#843](https://github.com/mshamblin5150-code/clinical-skills/issues/843), 2026-09-02, at
`origin/main` `c024551`, freshness gate `FRESH` at both checkpoints. **Ruled by the clinician on
that date.** Nothing is built here; this is the record the build reads.

This is [#405](https://github.com/mshamblin5150-code/clinical-skills/issues/405)'s unfinished
migration step.
[ADR 0116](0116-the-read-failure-posture-is-keyed-on-the-input-s-role-and-only-the-crash-is-ruled-family-wide.md)
ruling 2 was ruled with this and constrains ruling 1 below, which is the dependency
[ADR 0114](0114-a-run-directory-reader-grades-a-replaced-byte-and-the-family-s-read-failure-posture-is-measured-rather-than-ruled.md)
ruling 3 wrote on both.

## Measured before ruling, at `c024551`

**#839's headline table does not survive re-derivation, and ADR 0114 already said so.** Hashing each
function body with the name normalized away and the docstring held separately:

```
body efb1bb8d  anchor_scan  block_scan  differential_scan  filled_vitals_census  specificity_scan
body 29d9e215  refusal_scan
```

Two bodies. The four "shapes" are four *docstrings* -- the `worksheet`/`note` and `run`/`set` nouns
plus `refusal_scan`'s absence -- which is #839's own decision 3 and a naming question.

**Re-derived at `eac8d7b`, after the rulings and before this record was published.**
[#838](https://github.com/mshamblin5150-code/clinical-skills/issues/838) landed mid-session and its
convergence is exactly what ADR 0114 ruling 2 specified, so there is **one** body now:

```
body efb1bb8d  anchor_scan  block_scan  differential_scan  filled_vitals_census
               refusal_scan  specificity_scan
```

`refusal_scan`'s docstring is `anchor_scan`'s and `specificity_scan`'s. **No ruling below moves** --
the ordering ruling 5's neighbor worried about is discharged rather than reversed, and the
extraction now has the one correct body to converge on that both tickets asked for. The freshness
gate caught this at the publication checkpoint, which is what that second checkpoint is for.

**#839's `NOT_MEMBERS` is a stale name.** #830 landed between filing and grilling: `MEMBERS` is 14,
`REFUSED` and `DEFERRED` split what `NOT_MEMBERS` held, and `filled_vitals_census`'s migration has a
ticket -- [#842](https://github.com/mshamblin5150-code/clinical-skills/issues/842).

**Both deferrals hand-roll `main()` and neither reaches `run_grader.run`.**

```
tools/filled_vitals_census.py   notes = read_notes(directory)     # top level, no try
tools/aar_scan.py               except (OSError, ValueError, ...) -> print + return 2
```

So a non-member gets no `except SourceError -> exit 2` for free.

**The glossary had already named the concept before the ticket was filed.**

```
CONTEXT.md:582  **Run-directory reader**:
                _Avoid_: note reader, worksheet loader, directory walk
```

Both spellings in the tree are on that row. `worksheet` is not a defined term anywhere in
`CONTEXT.md`; its only occurrence in the file is that row.

**Stubbing the shared reader into two members and running the real runner:**

```
anchor_scan        declares_limbs=False  status=2
differential_scan  declares_limbs=True   UNCAUGHT ValueError: an exit-2 path names no exit-2 limb
```

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

## Ruled 2026-09-02

### 1. The shared reader lives in `run_grader`

#839 decision 1 argues for a separate module because *importing the runner into a non-member to get
a file reader inverts the dependency*. ADR 0116 ruling 2 refutes that as a fact -- both deferrals
already depend on `run_grader`, one directly -- and ruling 3 below makes it moot, since
`filled_vitals_census` imports `SourceError` and catches it in its own `main` whatever this answers.

**The precedent is one commit old and was ruled deliberately.** #830 put `NOT_GRADED` in
`run_grader` and had `aar_scan` -- a deferral, a non-member -- import it, on exactly the reasoning
that a shared policy belongs in the runner and a non-member may reach for it.

**And the widening cost is smaller than #839 assumes, because `run_grader` is already not what its
docstring says it is.** It is 313 lines holding `Finding`, `Option`, `Parsed`, `Grade`, `EarlyExit`,
`Grader`, `parse`, `run`, `NOT_GRADED`, *and* the population walk `walk_grader_modules` /
`_has_main_guard`, under an opening line reading *Shared command tail for graders over run
artifacts*. The population walk is not a command tail either. So this adds one more thing to a
module whose stated subject is already behind its contents, and **the docstring is repaired to say
what it holds** as part of this.

**A source-layer module holding `SourceError` and the reader, with `run_grader` re-exporting, is the
defensible alternative and its trigger is written down.** The layering is right -- `SourceError`'s
own docstring is a statement about a source and `run_grader.run` mapping it to exit 2 is the command
tail consuming it. It buys nothing measurable today, because the module is imported either way. If a
future non-member needs the source layer without the runner, that is when this is re-opened, and the
cost is one module plus a re-export line.

### 2. The reader refuses a source it cannot open, and #839 stops being a pure extraction

Under ADR 0116 ruling 2 the reader raises `SourceError`, which `run_grader.run` converts to exit 2
with no widening of its `except` -- the thing ADR 0114 forbids touching.

**#843's guard applies and is answered rather than dodged.** *Converting members silently -- a
member changing its verdict is a behavior change with a before-and-after, not a tidy.* Here the
extraction and the conversion are the same commit for six members, so **#839 may no longer describe
itself as behavior-preserving** and its build owes an explicit before-and-after on the deny-ACL
input ADR 0116 records.

**Its literal `Done when` survives and is not weakened.** *Stdout byte-identical against every
committed directory* still holds, because no committed directory crashes. The ticket is respec'd to
say what it now does rather than to lower its bar.

### 3. `filled_vitals_census` adopts now, with a hand-rolled catch in its own `main`

#839 decision 2 frames this as free -- *a defensible reading is now, since the reader is orthogonal
to the `Finding` shape* -- and under ruling 2 it is not. Adopting the reader without a
`try/except run_grader.SourceError: return 2` in `main` would raise straight out of `main`,
uncaught, at **exit 1**: the defect the ticket exists to remove, wearing the fix.

So it adopts the reader **and** the catch. Three lines in a non-member duplicating the runner's own
limb, with a known deletion date when #842 makes it a member.

**Deferring to #842 was declined on what it would have to lean on.** #843's `Done when` permits a
reader to be *named with a reason in a declared-limits object*, and `DEFERRED` is that object -- but
the reason sitting in it is **migration in #842 requires the `Finding` rewrite**. That is a reason
for not adopting the *runner*. It is not a reason for exiting 1 on a file `open()` refuses, and the
read posture does not depend on the `Finding` shape in any measurable way. Using it would be a
declared limit whose stated reason does not reach the claim it is asked to support, which is the
failure this repository has recorded against itself more than any other.

**Stdout is unaffected either way.** The shared body is byte-identical to what `filled_vitals_census`
runs today and the empty-directory limb stays in `main`.

### 4. One name, and it is neither of the two in the tree

`CONTEXT.md`'s **Run-directory reader** entry names the concept and its `_Avoid_` row names exactly
the two spellings the tree uses: `read_notes` is the note reader and `read_worksheets` is the
worksheet loader. The function takes the concept's name -- `read_run_directory`, though the exact
spelling is the builder's as long as it is not on that row.

**Two module-level aliases were declined because the domain model had already refused both words.**
#839 decision 3 calls this *a naming question and not a behavioral one*, which is right, and it
stopped being an open one when the glossary entry was written. The *each call site reads in its own
domain vocabulary* argument has one real term behind it and one word that was never one:
`worksheet` is undefined in `CONTEXT.md` outside that `_Avoid_` row.

### 5. Two glossary entries are corrected by this session rather than left standing

**`Run-directory reader` overstates its own ground.** It reads *That it reads a set is what fixes its
failure posture* -- true of the byte, and false as written of the `open()`, which ADR 0116 ruling 1
keys on the input's role. `discussion_reply_scan` refuses a set, which the sentence as it stands
calls wrong. It is amended to say the artifact class fixes the byte verdict and the role fixes the
read verdict.

**`Unreadable source` closes with a sentence this session retires.** *Which inputs qualify is
measured and unruled -- the members disagree three ways -- so the term names the outcome and not yet
its boundary.* ADR 0116 rulings 1, 3 and 4 rule the crash, declare grade-versus-refuse, and give the
declaration an address. Leaving it would point the next reader at a question that is closed.

## What this does not reach, declared rather than left to be found

**Whether the convergence stays converged, one level up.** ADR 0114 left this open on the ground
that a test pinning two modules' agreement forbids the divergence a copy exists to permit, and asked
whether this ticket's premise answers it. It does for the six: after this there is one body, so
there is no agreement left to hold. It answers nothing about the ten readers outside the run
directory.

**The reader's role parameter.** Ruling 2 forecloses the shared reader serving a **secondary** input
without a flag. Every use today is primary, so this is speculative -- and under ADR 0116 ruling 1 it
is the exact distinction the role unit exists to draw, so if it ever happens the reader needs a
parameter rather than a caller's judgment.

**`aar_scan`.** It is a run-directory reader by ADR 0114's population and it is **not** one by body:
it holds no copy of the extracted function, so nothing here reaches it. Its migration is
[#840](https://github.com/mshamblin5150-code/clinical-skills/issues/840).

**The `refusal_scan` ordering, discharged rather than standing.** This was written while #838 was
`ready-for-agent` and unbuilt, saying the extraction must wait or lose the before-and-after ADR 0114
ruling 2 built it for. #838 landed at `eac8d7b` during this session, so the condition is met and the
extraction has one body to converge on. It is kept rather than deleted because the reasoning is what
a later reordering would have to answer.
