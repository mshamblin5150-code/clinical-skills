# A render reader counts blind and the case-study graders rerun as handoffs before every reader round

**Measured at:** ac4bfe0f2866eb172b84c7bb591259387df193c6

[#1577](https://github.com/mshamblin5150-code/clinical-skills/issues/1577) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). It proposed nine changes to
`skills/practicum-case-study/SKILL.md` step 9, `skills/_shared/reference/voice-read.md` and
`skills/_shared/reference/sourcing.md`, each learned from a reader or orchestration correction made
one round at a time. It is the third ticket from that review, after
[#1575](https://github.com/mshamblin5150-code/clinical-skills/issues/1575) and
[#1576](https://github.com/mshamblin5150-code/clinical-skills/issues/1576). Grilled 2026-10-12
against `main`; the clinician ruled every point below in that session. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**All nine hunks still apply to `main`.** Each diff's context lines were found in its file at the
commit above. The step 9 reader-brief paragraph section 3 edits is unchanged by the
[ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md) build, which
added `REMARK:` lines to the record templates below it, so the coordination the ticket asked for is
no longer needed.

**ADR 0330 already settles two halves of the ticket.** A problem outside a reader's question goes on
a `REMARK:` line and is shown at the go-ahead, which replaces section 5's *notes beside the verdict*.
Its ruling 4 has the approval step run the paired grader before the ask, which covers section 9's run
of `tools/checks_ledger.py` before the go-ahead.

**The three graders section 9 names are already Grader handoffs.** `tools/research_ledger.py`
with `--draft` hands off at step 6, `tools/reference_scan.py` at step 7, and
`tools/case_study_scan.py` before step 8 renders and after every repair. The run's gap was that
repairs prompted by step 9 readers were placed for the next round without the ledger and reference
graders running again.

**Standing rule 6 already gives section 8's staging route.** It creates the private staging folder
"in the scratch root of the checkout the pass runs in" and moves the file into the run by copy and
rename. The run's agent read neither that rule nor the memory entry recording the refusal.

**Section 7's sentence contradicts both the record and the gate.** `sourcing.md` says flatly that
the memory index and every registered project place are owed.
[ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md) ruling 3
owes the memory index only on a run whose declaration is not `none`. `tools/project_context.py`
refuses a `PROJECT-SEARCH`, `PROJECT-WAIVE` or `## PLACE:` entry on a `none` run that declares no
classmate or `COURSE-HISTORY` retrieval, and the paragraph above the sentence already owns the
declared-retrieval branch.

## Ruling 1 — sections 1, 2, 3 and 6 are adopted as written

A reader recommendation that reverses a fix an earlier round required is reconciled against the
source both findings rest on before it is applied; the run directory records which stands and why,
and an unsettled pair goes to `PROPOSED` (section 1). For a pregnant patient, a row an opened
threshold sheet gives for every pregnancy that the Plan omits is a `defect`, never an observation
(section 2). The step 9 reader brief names the `Rx:` block's FNP credential string and the
`Signed by:` line's RN string as settled under *Credentials* (section 3). `voice-read.md` gains the
synthetic `pair_id` example that shows which text of a model pair heading the grader reads
(section 6). Each writes down a call the orchestrator or the clinician already made correctly
during the run.

## Ruling 2 — a render reader counts reference entries and prescription pads blind

Section 4's problem is adopted and its mechanism is not. The render reader records its own counts
of reference entries and prescription pads from the retained page images without being told the
expected numbers. The orchestrator compares them with the counts in the Markdown. A disagreement
sends the reader back to recount the named pages; the orchestrator never settles it by asserting
its own count. Stating the expected counts in the brief, as written, was declined: a reader handed
the number it is meant to verify can confirm it by default, and a miscount that matches the stated
number goes unseen. Dropping the change was declined because `render_scan.py` grades page coverage
and not what the pages hold.

## Ruling 3 — the stakes standard binds the clinical-decisions reader only

Section 5 is adopted for the clinical-decisions row, reworded onto ADR 0330. From round one, a
`defect` there is only what a faculty grader or a clinician acting on the document would catch as
an error; anything else goes on a `REMARK:` line. Applying the standard to every step 9 reader was
declined. The other rows grade a named rule, which already draws the line between a defect and a
preference, and a stakes test on top of it would let a reader downgrade a real violation of that
rule. The decisions row is the one whose questions have no rule behind them, and its audit widened
across about twenty rounds before the orchestrator imposed this standard.

## Ruling 4 — `sourcing.md` scopes the owed places to a run that names a project

Section 7 is adopted in ADR 0272's terms rather than as an exception clause. The sentence becomes:
on a run that names a project, the memory index and every registered project place are owed. A
second sentence says a `none` run owes neither; with no declared retrieval its record carries no
`PROJECT-SEARCH`, `PROJECT-WAIVE` or `## PLACE:` entry, and `tools/project_context.py` refuses one
that does. The paragraph above it stays the only statement of the classmate and course-history
branch. The ticket's corrected diff was declined because its exception restated half of that
paragraph. Reopening ADR 0272 to owe the memory index on `none` runs was declined: the run failed by
listing places it did not owe, not by missing a memory.

## Ruling 5 — the Write tool's refusal is stated in standing rule 6, not in a skill

Section 8's open decision is settled for `AGENTS.md`. Standing rule 6's staging sentence gains the
reason the shortcut fails: when the run directory is in another checkout, the Write tool refuses
that checkout's `scratch/`, so the pass stages in its own checkout and the copy step crosses.
Placing the sentence in `practicum-case-study`, as proposed, was declined because the refusal
belongs to the harness and binds every skill that writes from a worktree, and because rule 6 says
no skill file copies the route. Changing nothing was declined: the rule gave the route without the
reason, and the run tried the shortcut.

## Ruling 6 — before every reader round the three graders rerun as Grader handoffs

Section 9 is adopted for the reader rounds through the handoffs the skill already has. Before a
draft is placed for any step 9 reader round, the `research_ledger.py --draft`, `case_study_scan.py`
and `reference_scan.py` Grader handoffs run again over the draft as placed, under
[standing rule 6](../../AGENTS.md). Their raw output is kept in the run directory, a finding is
repaired and its grader rerun before readers see the draft, and the results are not check records
and replace no row. The ticket's *private preflight* was declined. Rule 6 forbids an author
checking its own draft except through a handoff whose raw result is preserved, and a preflight that
leaves no output cannot be told apart from one that was skipped. The run of `checks_ledger.py`
before the go-ahead is dropped from this change because ADR 0330 ruling 4 already requires it.
