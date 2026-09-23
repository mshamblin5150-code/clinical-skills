# The canonical voice model is resolved by one owner and identity is the graded row

**Measured at:** 4edf4d470d7affcf3bbe3b1afda823fdb45bb04f

[#1393](https://github.com/mshamblin5150-code/clinical-skills/issues/1393) was filed from the
after-action review of a course-assignment run, 2026-09-22: a draft began from a secondary voice
reference while the canonical working model was available. Grilled against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**Two voice models exist.** The canonical one is the account-owned model under the owning
checkout's `scratch/`. The second is a dated snapshot held **outside every checkout**, in the
clinician's cloud-synced documents. Its absolute path is deliberately not published in this record:
it contains a personal account name and this repository is public.

| | lines | dated | `voice_model_scan` |
| --- | ---: | --- | --- |
| the canonical account model | 1021 | 2026-08-28 | exit 0, 0 findings |
| the snapshot outside every checkout | 1013 | 2026-08-21 | exit 1, 2 findings |

**The word *condensed* in the ticket is wrong.** The snapshot is 99.2% the size of the canonical
model. It is not a summary; it is a faithful copy seven days stale, and its faithfulness is why it
was plausible.

**What the staleness costs is a purchased correction.** The diff is 18 lines and it is exactly
[#496](https://github.com/mshamblin5150-code/clinical-skills/issues/496)'s payload — ADR 0038's
invoked-source rewrite, and one discriminating pair:

> *Generic (machine draft)*: "What worries me"
> *His (clinician correction)*: "What concerns me"

That pair was bought with a reply already irreversibly posted to a board. A draft taken from the
snapshot spends the purchase.

**The location has no owner.** The filename is spelled twice in code and twenty-one times in skill
prose, and nothing binds any spelling to any other. The scanner builds the default by joining the
scratch root to the bare filename:

> `arguments.insert(0, str(repo_root.scratch_root() / "voice-model.md"))`

and the scratch census carries the same bare string in its standing-artifact set:

> `"voice-model.md",`

**The twenty-one prose spellings are three classes, not one.** Some are mentions describing the
artifact. Some are uses instructing a run to open a path. Seven are existence tests.

**The existence tests carry a second live defect, and it is the quieter one.** A worktree has no
`scratch/`, so a run obeying the prose literally finds the path absent and takes
[#528](https://github.com/mshamblin5150-code/clinical-skills/issues/528)'s no-model branch —
declaring the voice unmodeled, in writing, while the model resolves successfully through the
scratch root. Demonstrated in a worktree during the grilling. It has **no recorded instance**; it is
grounded in a demonstrated mechanism rather than a measurement.

**The instrument that missed the second model is the one the run used, and the grilling reproduced
the error before correcting it.** A walk of registered git worktrees reports the canonical model as
the only copy, because the snapshot lies outside every checkout. The run stated that conclusion; so
did the first round of this grilling. The clinician supplied the discriminator in his own words —
the canonical model is the expansive one.

**The store an agent is trained to search first is not a corrective here.** Five memory entries
send an agent to the clinician's cloud documents first for his files, which is right for every
artifact but this one. The separate captured-thought store carries voice-register statements dated
two months before the 2026-08-18 damping reversal and carries no capture of that reversal, so it
would have supplied the superseded position with nothing marking it superseded.

## Ruling 1 — the defect is resolution and identity, and the precedence half stands

The ticket's original framing was that a secondary copy must not silently outrank the canonical
model. That framing was provisionally dropped during the grilling on a false fact — an assurance
that no second copy existed — and is **restored**. Two models exist, the wrong one is reachable and
plausible, and a rule that only required correct resolution would be satisfied by a run that
resolved correctly and then read the snapshot anyway. The graded claim is **identity**: the
declared model is the resolved canonical model, or it is a finding.

## Ruling 2 — the five coursework readers are in scope and the note skill is not

`course-assignment`, `discussion-post`, `practicum-case-study`, `discussion-reply` and
`peer-critique` are bound. Each produces graded coursework prose from the model, each has a run
directory, and each is already paired to a completion grader.

`clinical-note` reads the model and is deliberately **out of scope**: its consumer is a chart and a
portal entry rather than a graded paper, and the register it draws is a different one. That is a
ruling and not an omission. It is not an exemption from any submission rule.

An earlier point in the grilling held scope at three skills on the reasoning that two of the five
had no signed bar to carry a field. Ruling 6 moved the record out of the bar, which dissolved that
reasoning, and the scope was widened in the same session rather than left standing on it.

## Ruling 3 — there are two states and no override

A run either resolves the canonical model and records it, or declares absence under the existing
no-model rule. **There is no deliberate-override state.** Every candidate case put to the grilling
was either already covered — a rebuild belongs to the setup skill with the clinician present, a
test is the scanner's own positional argument, a second clinician is the absence declaration — or
was not a coursework run at all. An override state would be a named, legal field shaped exactly
like the defect. Anything that is neither state is a finding.

## Ruling 4 — a wrong path refuses and a moved digest reports

The declared path and the declared digest prove different things and are graded differently.

A declared path that is not the resolved canonical path is the defect verbatim and is **exit 1**. A
declared path that matches, with a digest that has since moved, is staleness rather than
substitution: it is **reported, with an exit-2 coverage state**, on the same terms the evidence-dump
join already uses. Where a finding and the coverage state both hold, **1 wins**.

Refusing on any digest mismatch was refused: the model is stable in practice and the branch would
fire on an honest run whose model was saved mid-draft. Reporting both without grading either was
refused as the written instruction this ticket exists because instructions cannot fail.

**The staleness branch has no recorded instance.** Across the runs examined the model did not move.
It is grounded in a trap rather than a measurement, and this record says so rather than implying a
count.

## Ruling 5 — one owner holds the location and one function produces the resolution

`repo_root` owns the canonical location. It already holds the resolvers for shared gitignored
account state, and a location spelled in many places with no owner is the shape this repository has
repeatedly ruled against.

**The object is one artifact wide.** The standing-artifact set names several account files; only
this one has a recorded failure and a live negative control. The others are deliberately not
resolved, and that is recorded here so the next session finds a ruling. A general resolver over all
of them was refused: it generalizes from no instance and lowers the cost of adding an unowned next
one.

**One function produces the resolution** — the path, its digest and its existence state — and both
the run's record and the grader's check call it. Two call sites deriving the same value
independently is the two-answers failure the shared-object precedents exist to stop, and ruling 4's
whole design rests on the two strings being the same string derived the same way.

## Ruling 6 — the record is machine-written in the run directory at draft time

The resolution is recorded in a **purpose-named record in the run directory**, written by the
resolution function immediately before the first prose is drafted.

**It is not a signed-bar field.** Every field of that bar is transcribed from the live assignment
page or syllabus, and the clinician signs having confirmed the transcription is right. A path and a
digest are facts about the run's environment, not elements of the assignment, and a signature over
an unverifiable value devalues the fields that are verifiable.

**The timing is draft time and not bar time.** The bar is signed before research. A digest taken
then is already stale when prose is written, which would fire ruling 4's coverage state on ordinary
correct runs.

**The record is named for its purpose rather than claiming a generic pre-draft slot**, because
[#1395](https://github.com/mshamblin5150-code/clinical-skills/issues/1395) comes from the same
review and needs its own. Neither may silently take the other's.

## Ruling 7 — each completion grader declares the same row

The five skills' completion graders each declare the same expected row and enable it the same way,
on the precedent of the after-action-review row those graders already share. The skill-to-grader
pairing already exists and is not re-invented here, and no new grader is created.

## Ruling 8 — uses and existence tests name the resolver, mentions keep the name

The prose spellings are repaired by the mention-versus-use rule this repository already applies at
the span rather than the file.

A **use** — an instruction to open or write the model — names the resolver. An **existence test**
names the resolver, so that absence is decided by the resolver and never by the working directory.
A **mention** describing the artifact keeps its canonical relative name, because a reader needs it.

**The existence tests are repaired first.** They produce a well-formed, documented, graded-clean
declaration of absence with nothing firing anywhere, which makes them the more expensive defect
despite having no recorded instance.

Leaving the prose and relying on the grader was refused: the grader fires at the terminal step, so
the remedy would be a full re-draft, and it does not reach the false-absence case at all, because a
declared absence recorded against the wrong path is internally consistent.

## Ruling 9 — the snapshot is marked, never deleted, and its path is not published

The dated snapshot outside every checkout is **marked in place** — a first line stating that it is a
dated snapshot, that it is not canonical, and naming the resolver. That is the only remedy that
reaches an agent which finds it by hunting, and it needs no repository change.

**It is not deleted and no work list may schedule that.** It is the clinician's file and it reads as
a deliberate backup; disposal is his word, per file, on the scratch rule's own terms.

**Its absolute path is not written into any tracked file.** The path carries a personal account name
and this repository is public. Where a tracked record must describe the control it says *a dated
snapshot of the voice model held outside every checkout*.

## Ruling 10 — one limits object carries both ceiling limbs

The ceiling is declared in **one object**, owned by the module that owns the row, named by the five
graders and by `CLAUDE.md`, with no row copied. Five per-grader copies of one limit is the
duplicated-limit defect, and a limit written only as prose fails nothing.

**Resolution is not use.** A run that resolves the canonical model, records a true path and digest,
and then drafts from something else produces a record that is true about the resolver and false
about the draft. The instrument prints the same thing either way. This mechanism removes the
**accident** that caused the observed failure; it does not reach a run that reads elsewhere on
purpose.

**Use is not voice.** A run with the model correctly in hand still produced a draft the clinician
disowned, 2026-09-09.
[#1394](https://github.com/mshamblin5150-code/clinical-skills/issues/1394) covers that for
course-assignment decks against the signed talk style; the other four skills and the model's own
discriminating pairs are uncovered. That residue is **filed separately** rather than folded in,
because this record is complete without it.

## What this record does not settle

**Whether a draft came from the model it names.** Ruling 10 states this as the mechanism's ceiling.
No check here compares drafted prose with the resolved model.

**Whether a resolved model sounds like its clinician.** The scanner grades shape, and the
confirmation named in the voice reference remains the verification of the model's truth.

**The captured-thought store's superseded voice statements.** They are measured above and no ruling
here changes, marks or retires them. Reconciling that store with the current damping ruling is
outside this record.

**Whether the five memory entries that send an agent to cloud documents first need a carve-out.**
The mechanism is measured above as the cause; whether the remedy belongs in those entries is not
ruled here.
