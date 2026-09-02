# The after-action review's signal is an observed correction and its findings land or the run is not done

[#814](https://github.com/mshamblin5150-code/clinical-skills/issues/814) records that a skill run's
findings die with the session: the next invocation starts from the same instructions with none of
them, so the same defect is available to be rediscovered indefinitely. One `discussion-post` run on
2026-09-01 produced seven corrections and **four of them landed nowhere**.

Grilled 2026-09-02. **Fourteen rulings, made by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling

**Every transcript figure below was measured against real session files under
`~/.claude/projects/`, which are the harness's state and not this repository's.** Nothing committed
re-derives one, and none is restated anywhere else in this tree.

**1. The ticket's proposed mechanism cannot do the job it is proposed for.** A `Stop` hook fires
**once per turn**, after the model finishes responding and before the next user input. It cannot
distinguish a skill that has finished from one that is mid-run and waiting. The ticket names a `Stop`
hook as the thing that makes the review mandatory, and the ticket's own *What must not come out of
this* forbids a per-turn review. **They are the same hook.** `SessionEnd` exists and fires at
teardown, when the model is already gone — it can run a script and cannot make anything review
anything.

**2. The transcript's schema is undocumented and was read directly.** A 2,199-line session carries
`type`, `sessionId`, `timestamp`, `isSidechain`, `userType`, `message`, `toolUseResult` and
`attributionSkill`. That last field names the invoked skill, so *did a skill run in this session* has
a mechanical answer rather than needing a convention.

**3. A human turn is separable from tool output, with one contamination.** Of 385 `user` entries in
that session, **356 were tool results and 26 were plain strings** — but skill-invocation boilerplate
is injected in **exactly the shape of a human turn**, so a type check alone reads the `<command-message>`
block as the clinician speaking.

**4. The clinician's corrections are short.** Two of his turns in that session were the single word
`agree`. A detector assuming a push-back is a paragraph misses them, silently.

**5. Six of the seven tracked clinical skills already write a run directory** — `batch-shift`,
`clinical-note`, `discussion-post`, `discussion-reply`, `icd10-cpt`, `practicum-case-study`. Only
`setup-clinical-skills` does not.

**6. The conversation is 3–4% of the transcript.** Reduction by entry shape — keeping every user turn
and every assistant text block, dropping tool-call payloads and tool-result bodies — took 4.0 MB to
**175 KB** and 6.1 MB to **223 KB**. All conversation text alone is **132 KB and 190 KB**.

**7. The cheaper cuts are barely cheaper and cost a whole corrector class.** User turns alone are
**49 KB and 100 KB**; user turns plus the reply to each are **87 KB and 130 KB**. The narrow cut saves
roughly 15k tokens against all conversation text and loses every correction that did not arrive
adjacent to one of the clinician's turns.

**8. Subagent material rivals the main transcript, and its useful part does not.** Five sessions
carried **6 to 14 subagent transcripts totalling 1.9 to 9.6 MB** — sometimes larger than the main
file. But the **subagent *result* bodies, which are what reach the orchestrator, are 7 KB and 22 KB.**
All tool-result bodies together are 0.30 MB and 1.49 MB.

**9. The ticket's own worked table is an after-action review performed by the context that erred, and
it exculpates itself.** Four of its seven rows are dispositioned a version of *"nothing durable."*
Row three — *recommended a word count without checking his own precedent* — is classified
**"nothing durable; contradicted a standing preference already recorded in memory."** The preference
already existed: `length-serves-clarity-never-a-target` is in the memory store today. **The failure
was not a missing artifact; it was that an existing artifact went unread**, and the classification
leaves the identical error available next session with the memory sitting right there.

**10. All seven rows of that table describe conduct, and not one contains patient data.** This is not
luck. A correction is a statement about the agent's conduct; the patient is in the material the agent
was working on, not in the error it made.

**11. The record's home is a patient record and the existing net has a hole shaped like the
material.** Run directories live under `scratch/`, which this repository's own rule makes a patient
record without exception. `phi_scan`'s corpus layer reaches patient names and dates; it does **not**
reach a classmate, a preceptor or a site, which
[#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50) and
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) both ruled open rather than
closed — and `discussion-post` and `discussion-reply` are exactly where that exposure lives.

**12. `CONTEXT.md` already forbids the ticket's vocabulary.** **Session** is defined as one agent's
working pass over this repo and its `_Avoid_` rejects `run` and `pass` outright; **Run directory**
*"carries no date and outlives every sitting"*; **Submission** is *"one per sitting, named by its run
key and the date it was written."* The ticket says "skill run" throughout, which is ambiguous between
a session and a graded artifact's whole provenance.

## Ruled 2026-09-02

**1. A correction is an observed reversal, and the corrector is a field on it.**

A claim was asserted, later contradicted, and the contradiction stood. It is an **event that
happened**, which is what lets it be read off a record rather than introspected about — and it is why
the review's question is *where was I corrected* rather than the ticket body's *what would have failed
silently*. That second framing asks a model to reason about counterfactuals it never observed, which
is the class of judgment a model is least reliable at and most inclined to flatter itself on.

Three correctors are recognized because the fix's destination differs by each: **the clinician**, **an
agent or tool**, and **the orchestrator catching itself**. Which party was *in error* is a **further
field and not the same one** — a correction whose corrector was wrong is a supported outcome, and
finding 9's Stop the Bleed case is the recorded instance.

**A preference stated for the first time is not a correction.** It reverses nothing, and counting one
inflates the record with things nothing was wrong about.

**2. Detection is mechanical; classification and landing are adversarial and read the memory index.**

The ticket's constraint puts the review inside the running skill, which makes the erring context its
own grader — and this repository's standing rule is that *a report by the pass that produced it is a
baseline, not a verification*.

**Half that objection dissolves and half does not.** By ruling 1 the review never finds new errors; it
harvests ones somebody already caught, and detection is honest self-work. **Classification is not.**
Finding 9 is the evidence: the erring context marked four of its own seven errors as needing no
durable fix.

So `tools/aar_scan.py` extracts the population and **a fresh subagent disposes of it**, briefed
adversarially and reading the extract **plus the memory index**. That last input is not a convenience:
it is the only artifact that can distinguish *we never knew this* from *we knew this and did not
look*, and finding 9 is precisely the second.

**3. The disposition set is closed and *nothing durable* is not a member.**

A skill-file edit, a tracker ticket, a memory write, or a check. **A correction dispositioned nowhere
is indistinguishable from a review that did no work**, and it is the disposition a tired context
reaches for first. *"A habit visible only in a review"* is either a skill-file step that was missing
or it is a ticket.

**Apply what records; propose what rules.** A memory write and a ticket are recording and are applied
unattended, on the finishing sweep's existing authority — `docs/agents/issue-tracker.md`'s
*changing a ruling needs the clinician, recording what you found does not*. **A skill file is a
ruling**, so the review writes the exact proposed diff onto the ticket and stops. The conceded cost is
latency on the class that most needs to land: finding 9's skill-file gap waits on the clinician.

**4. The grader is the mechanism. The `Stop` hook is refused.**

Finding 1 disqualifies it. What replaces it is three layers, each doing only what it can:

- **Model-invoked at the terminal step**, `/AAR` model-invocable, written into each skill's final step.
- **An expected row in the run's completion grader**, on `checks_ledger.EXPECTED_CHECKS`'s precedent —
  **the layer that fails**, and unskippable because the grader is what declares the run done.
- **A `SessionEnd` pointer** for the sitting that never reaches a terminal step, per ruling 14.

**An advisory hook was refused rather than kept as a belt.** A nag on a hot path is a check that gets
learned around, and this repository has already paid for one: `spelling_scan` crashed inside the
pre-commit hook, its status was OR-ed away, and *an advisory check that crashed is indistinguishable
from one that passed* cost a real finding.

**5. Scope is six skills, and the boundary is named rather than inferred.**

`batch-shift`, `clinical-note`, `discussion-post`, `discussion-reply`, `icd10-cpt`,
`practicum-case-study`. **Not** the Matt Pocock plugin skills, **not** the maintainer's engineering
skills, and **not** `setup-clinical-skills`.

Finding 5 is why this costs nothing: every one of the six already has somewhere to put the record, so
no terminal artifact is invented, no commit is gated and no fourth refuser is created. **The
declared cost is that the error class which produced the ticket's own finding 1 — an orchestrator
reporting derived memory as the clinician's own words — is not clinical and happens in any skill.**
Under this scope it is caught only inside the six.

**6. The unit is the submission, not the run and not the session.**

Finding 12 makes this mechanical rather than terminological. A `practicum-case-study` run directory is
written into across several sittings; **one `<run directory>/aar.md` is overwritten by the next
sitting and the grader passes on whatever survived.** That is the silent pass this ticket exists to
close, rebuilt inside the fix for it.

A submission is already one per sitting and already dated, so the record is keyed to it. **A resumed
run accumulates records and that is correct** — a reader can see that Monday's skill-file proposal was
never acted on by Thursday, which one overwritten file destroys.

**7. Subagent transcripts are read on demand, and a subagent-invoked skill gets no review of its own.**

Finding 8 rules out reading them speculatively. It is also unnecessary: **corrections are visible
where they are resolved, and they are resolved in the main transcript.** The ticket's Stop the Bleed
finding erred inside a subagent and was corrected in front of the orchestrator.

One subagent transcript is read **only when a disposition requires it** — which is exactly the case
where the fix is an edit to a fan-out brief, since *the brief must require a second corpus* cannot be
written without knowing the subagent searched one.

**A subagent submits nothing**, so by ruling 6 it has no unit and is covered by the submitting run.

**The residue is declared rather than closed: a subagent that erred and was never contradicted is
invisible.** Nothing corrected it, so no correction occurred. That is the boundary of using observed
reversals as the signal and it is the price of ruling 1.

**8. The orchestrator may overrule the classifier, never silently.**

The clinician's rule is that a subagent's result is a claim verified by the agent that spawned it —
and here **the spawning agent is the one that erred**, so taken literally the protection in ruling 2
is undone by the rule governing it. The veto still has to exist: finding 9's Stop the Bleed subagent
was confidently wrong, and an unappealable classifier would file the clinician's correction as a
defect in his own account.

Three mechanisms, each closing a different escape:

- **The population is not the orchestrator's to touch.** `aar_scan` fixes it. Nobody decides what
  counted as a correction, because that is the one place a veto would be invisible.
- **A disagreement is written down with both verdicts** and who overruled whom.
- **The grader refuses a correction with no disposition and cannot refuse a wrong one**, declared in
  the tool so a clean scan never reads as *the dispositions were right*.

**The ceiling is named and not a to-do: an orchestrator that overrules every unflattering verdict
produces a record that passes every check.** The mechanism makes self-exculpation legible, not
impossible, and the only party who can catch it is the clinician reading a short list of
disagreements.

**9. The reduction is by entry shape, and what it drops is declared.**

Reduction by shape is safe; reduction by content is a matcher, and **a matcher never turns a partial
read into a clean whole.** `aar_scan` keeps every user turn, every assistant text block, every
subagent result, and each tool call's **name and exit status** — finding 8 makes the subagent results
free.

Finding 7 rules out the narrower cuts: they save little and lose corrector class two entirely.
Finding 6 rules out keeping everything.

**Tool output bodies are dropped and the ceiling is stated** — *a correction that lived only in a
tool's output and was silently acted on is not extractable*. The reason is not cost: **exit status is
the honest signal and an output body is not.** A 1.5 MB stream of directory listings and `git` output
is where a classifier finds pattern in noise. The status lets it see *a check failed here and
something changed after* and go read that one result, on ruling 7's targeted rule.

**10. The drain is a watermark, not a move of bytes.**

Without one, a third sitting's review re-reads and re-disposes the first two sittings' corrections,
and a correction already ruled on Monday gets a fresh verdict on Tuesday from a context that never saw
Monday's reasoning.

The raw transcripts are the harness's files, not this repository's; **moving one would leave a
resuming session with its own history gone.** So each record ends with the identifier of the last
entry it dispositioned and the next review starts there. It is a move in the sense that matters — the
material leaves the unreviewed set — and never a delete.

**A late correction about early work is still caught**, because the correction *event* is after the
watermark. **A missing watermark is exit 2**, because a scan reading from an unknown start reports a
clean set it never measured.

**11. The diff is the landing check and never the detector.**

A diff shows end state, not the reversal that produced it. Finding 9 is decisive: **four of the seven
rows changed no file at all**, so a diff-based detector reports zero corrections on the very session
that produced this ticket, and reports it as clean.

But it answers the half a transcript cannot: **did the fix land.** A `memory write` that produced no
new file under the memory directory is a finding; a `ticket` disposition with no `gh` call in the
transcript is a finding. That converts the ticket's own completion condition — *a written review that
landed nothing is the silent pass this ticket exists to close* — from the model's say-so into a check.

**12. The record's disclosure class is private working material.**

Read it, never paste it. Declared in `aar_scan`'s module docstring and nowhere else, on the roster
`CONTEXT.md`'s **Disclosure class** already fixes.

**13. A published finding describes conduct and does not reproduce material, and a quotation gate
holds it.**

The first draft of this ruling bounded a filed ticket to a disposition name, a corrector class and a
file path. **The clinician refused it: it needs to know what went wrong otherwise it is wind.** He is
right — that is a work order with the finding removed.

Finding 10 is why both are available. The boundary is **describe the conduct, do not reproduce the
material**, and it is enforced rather than stated: `tracker_publish_hook.py` already intercepts every
`gh` command, and for an AAR-sourced publication it additionally refuses **any span of the run
directory's own text reappearing in the ticket body.**

**It is a quotation scan and not a PHI scan**, which is what makes it reach where finding 11 says the
shape layer does not: it needs no notion of a patient, a classmate or a site, only of what the source
was. *"Reported material recalled from a memory store as the clinician's own authored words"* copies
nothing and publishes.

**The span length is measured before a number is written**, ruled explicitly. `SPACE_ADVANCE_FRACTION`
is this repository's recorded instance of a constant named at an edge, where the chosen value was
worse than making no change at all. **And the gate is a floor: a paraphrase walks through it**,
declared in the tool rather than closed.

**14. A sitting that never submits leaves a pointer.**

By ruling 6 no submission means no review and no grader; and the next sitting's review reads the next
sitting's transcript, so **an abandoned sitting is permanently invisible** — which is where the
expensive corrections cluster, because work is parked when something has gone wrong.

`SessionEnd` writes the orphaned transcript's path and the run key under `scratch/runs/`, and the next
review on that run **reads it, drains it, and disposes of its corrections alongside its own.**

**It is a pointer and not a log** — two fields, no findings, no prose. The ticket's prohibition is
against *an accreting prose log nothing reads*, and this is consumed and cleared. **A marker left
unconsumed across sittings is visible**, which is a run whose parked work was never reviewed.

## Consequences

**#814 is respecified to these fourteen rulings and moves to `ready-for-agent`.** Its open questions 1
through 5 are settled by rulings 5, 3, 1, 7 and 9 respectively; its proposed `Stop` hook is refused by
ruling 4.

**`CONTEXT.md` gains a `### Review` section** carrying **Correction**, **Disposition**, **After-action
review** and **Quotation gate**. The ticket's own "skill run" vocabulary is not adopted, per finding
12.

**The quotation gate is a change to `tools/tracker_publish_hook.py`'s contract** and is the one part
of this that touches an existing refuser. It fires only on an AAR-sourced publication.

**The span-length measurement is a prerequisite of the build and not part of it** — ruling 13 forbids
writing a number before it is taken.

## What none of it reaches

**Whether a disposition was the right one.** Ruling 8's grader refuses a correction with no
disposition and cannot refuse a wrong one.

**A correction nobody made.** Ruling 1's signal is an observed reversal, so an error that went
unchallenged is not in the population — ruling 7's residue, and permanent by construction.

**A correction living only in a tool's output** — ruling 9, declared rather than closed.

**A paraphrase of the working material** — ruling 13's floor.

**Any skill outside the six** — ruling 5, including this session's own.

**And an orchestrator that overrules every unflattering verdict**, which produces a record passing
every check — ruling 8's ceiling, catchable only by the clinician reading the disagreements.
