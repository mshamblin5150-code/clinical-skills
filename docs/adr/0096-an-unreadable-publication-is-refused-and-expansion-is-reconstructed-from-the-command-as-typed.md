# An unreadable publication is refused and expansion is reconstructed from the command as typed

[#745](https://github.com/mshamblin5150-code/clinical-skills/issues/745), filed by the exhaustive
tracker sweep of #702's grilling and corroborated independently from #708's, 2026-09-01. Ruled by
the clinician on that date at `origin/main` `4608019`, freshness gate `FRESH`. The ticket carried
three open decisions and was labeled `grilling`; this is the record its build reads.

## What this adds to ADR 0083

**[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
is untouched.** Its scope — the hook grades the record rather than the body — and its per-trigger
branch-scope refusal both stand as written. What that record does not say is what happens when the
hook cannot read the text at all, and the answer in the code was **allow**.

## Measured before ruling, at `4608019`

Every form driven through `tracker_publish_hook.extract` with the variable assigned in the same
command, before any change:

| body-file argument | outcome |
| --- | --- |
| a bare variable that is the whole path | graded |
| `$VAR/name.md` | **escaped**, reported `missing-file` |
| `${VAR}/name.md` | **escaped**, reported `missing-file` |
| a literal Windows-spelled path | graded |
| a literal Git Bash `/c/...` path | **escaped**, reported `missing-file` |
| a variable never assigned, with a suffix | **escaped**, reported `missing-file` |

**Three findings, and the ticket names one of them.** The variable-with-suffix rows are #745's own.
The Git Bash row was found from #708's session and posted there; MSYS rewrites that spelling when it
launches a native executable, so the argument the shell used opens and the hook's copy — taken
before that rewrite — does not. **The last row is a misclassification nobody had named**: the module
already carries an `external-variable` kind with its own remedy, and the suffix form could not reach
it, so the advice printed was *create the file first* for a path the hook could never have built.

**What it cost is recorded on two tickets and is not hypothetical.** #745 carries a non-conforming
branch-state block reaching the tracker on a record the gate refuses. #708's session published four
times, one of which had a real `unresolved-path` refusal waiting, and a dead citation shipped and
had to be corrected. In both cases the by-hand run is what caught it, and nothing required one.

## What is ruled

**Ruling 1. A publication whose text cannot be read is refused.** Every kind in
`UNREADABLE_REMEDIES` denies, and the reason states that the publication was not scanned.

**The argument is that the alternative is not a gate.** The branch-scope limb refuses; a refusal
that evaporates whenever the hook cannot parse its own input is strongest exactly when the text is
known and absent exactly when it is not. That is the inverse of what a gate is for, and it is the
same shape this repository keeps recording — a check that could not have worked, answering in a
register that reads as a settled result.

**Ruling 2. The refusal is bounded by `PUBLISH_ROUTES` and by nothing wider.** A command that is not
a recognized publication returns an empty response and is untouched, which is what keeps ruling 1
from becoming a general veto over `gh`. A test drives both an unrelated command and a read-only `gh`
call and asserts each is left alone.

**Ruling 3. Expansion is reconstructed from the command as typed, because there is nothing else to
read.** The hook receives `tool_input.command` — the text before the shell runs — so #745's
decision 2, *resolve the argument rather than parse the command*, describes something that does not
exist at hook time. **The decision is answered by the fact rather than chosen against.** What is
available is the assignments made in the same command, which the module already tracked; a variable
naming a path *prefix* now expands as the shell would expand it, and a Git Bash path is also tried
in its Windows spelling.

**Ruling 4. What remains unresolvable is unresolvable by construction and is refused, not
declared.** A variable from the environment, a command substitution, a pipe: the hook cannot know
these and no amount of parsing changes that. #745's decision 3 offered declaring the limit instead,
on [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s terms. **Declaring is
the remedy for a limit that cannot be closed, and this one is closed by ruling 1** — the text is not
scanned, so the publication does not happen, and the remedy line names the by-hand command that
grades the file.

**Ruling 5. The report says `NOT SCANNED` rather than naming a missing file.** The prior message was
advice to an author about their own next step, and nothing in it distinguished a typo'd path from a
gate that did not run — which is why four publications in a row read as a harmless nudge. The
remedy sentences are kept; the register in front of them is not.

## What this does not reach

**Two rows are added to `tracker_publish_hook.NOT_REACHED` and are deliberately not restated here.**
That object and its rule — a limit is owned by it rather than copied into the module docstring or
`CLAUDE.md` — arrived on [ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
while this branch was open, and it is adopted here rather than worked around. Its existing four rows
are ways the hook never runs at all; these two are what a run it *did* perform does not establish,
so they belong in the same object and are distinguishable by nothing else. A test asserts the whole
population in both directions and names which ruling owns which rows.

**Why the second of them is safe is this record's to say, and it is the reason the floor was
acceptable at all**: an unreconstructed form is *refused* rather than guessed at, so a gap in
reconstruction cannot become a silent publication. Ruling 1 is what buys that, and without it a
reconstruction floor would be the same defect one layer down.

**The Git Bash spelling is tried, not detected.** Both candidates are offered to the reader and the
first that opens wins, so a platform where `/c/...` is a real path is served by the first candidate
and is unaffected. It is not a claim to have modeled MSYS's rewriting rules.

**Nothing here changes what is graded.** `phi_scan` findings stay advisory and the branch-scope
triggers keep the per-trigger refusal ADR 0083 ruled. This record is about publications the hook
never got to grade at all.
