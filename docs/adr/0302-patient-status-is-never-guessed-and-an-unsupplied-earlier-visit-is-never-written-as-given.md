# Patient status is never guessed and an unsupplied earlier visit is never written as given

**Measured at:** 32ce8f5905148ac85f4db41231a4fd40b338e9eb

[#1462](https://github.com/mshamblin5150-code/clinical-skills/issues/1462) was filed from the
after-action review of a NUR5144 `batch-shift` run. The clinician delegated
the run's open questions. The orchestrator called one patient established because the shorthand
mentioned an earlier visit, and a later pass wrote that visit's location into the history as fact,
although the clinician never supplied it. `tools/coding_freshness.py` refused the status because it
carried no identity-map or Medatrax evidence, and the status was reverted. Grilled 2026-10-08
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in
that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The status half was already ruled, and one skill sentence still contradicts the ruling.**
[ADR 0250](0250-a-review-sheet-carries-final-coding-only-after-the-batch-is-fresh.md) ruling 4 makes
status account-backed and says a shift-relative inference is not evidence. `skills/icd10-cpt/SKILL.md`
step 5 and `skills/batch-shift/SKILL.md` follow it. `skills/clinical-note/SKILL.md` step 5 still
reads *"Read status from the shorthand when it states it. Otherwise use the private identity map"*,
which is [ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)
ruling 12's wording from before ADR 0250 narrowed it. That sentence invites the inference this run
made.

**The account evidence cannot see a group's earlier visit.** The CPT definition counts a patient as
established when a clinician of the same specialty in the same group saw them within three years.
The identity map and Medatrax record only the clinician's own visits, so a patient his practice saw
before he did reads as new on the account evidence.

**An unknown status has no route to the clinician.** It blocks the whole Review sheet, and status is
not one of the `PRE-APPROVAL PATIENT QUESTIONS` kinds.

**No rule addresses an unsupplied fact about an earlier visit.** The asserted tier permits declared,
grounded inferences about the patient's past, and nothing excludes an earlier encounter from it.
No skill file defines what a delegated answer may decide.

## Ruling 1 — the stale shorthand sentence is corrected to account-backed status

`clinical-note` step 5 states status from the identity map or Medatrax, as ADR 0250 ruling 4 and
`icd10-cpt` step 5 already do, and never from the shorthand. No delegation-specific status clause is
added: nobody decides status by judgment, delegated or not, so such a clause would restate a rule
that binds every pass. Adding only the ticket's proposed `batch-shift` paragraph was declined because
it leaves the sentence that caused the inference standing. Doing both was declined because it writes
one rule in two places.

## Ruling 2 — a shorthand-mentioned earlier visit the records lack is the clinician's question

Where the shorthand mentions an earlier visit and neither the identity map nor Medatrax records the
patient, the run adds a status item to `PRE-APPROVAL PATIENT QUESTIONS`: the shorthand mentions an
earlier visit, the records show none, and the question is whether it was the clinician's practice
within three years. The clinician's recorded answer is accepted status evidence beside the identity
map and Medatrax, and `coding_freshness.py` accepts it as a third evidence kind with the same
fingerprint requirement. The question fires only on that conflict; a patient whose records settle
the status is never asked about. Letting the account evidence decide silently was declined because it
codes a group's established patient as new with nothing telling the clinician. Leaving the status
unknown was declined because the run stalls without a question, which is how this run came to guess.

## Ruling 3 — the note states only what the clinician supplied about an earlier visit

The note says only what the shorthand supplies about an earlier visit. Any unsupplied detail of that
visit, including where, when, who, and what was done, goes to `GAPS` and never into the note, not
even as a declared `FILLED·asserted` inference. An earlier visit is an event with a place, a date and
a clinician, and writing one creates a documented encounter under the clinician's name; the asserted
tier is for plausible patient history, not for creating encounters. Permitting a declared inference
was declined because it depends on the clinician catching an invented event at review, and this run
showed a pass can skip the declaration. Asking about every unsupplied detail was declined because
most returning-patient notes would carry questions about details they rarely need.

## Ruling 4 — under delegation the status question falls back to the records and is named at the go-ahead

A delegate never answers ruling 2's question. When the clinician has delegated the pre-approval
questions, the run codes the status from the account evidence, so no record reads as new, and the
go-ahead message names that patient: coded new, the shorthand mentions an earlier visit, and saying
`established` changes it. A change re-renders the affected note under the existing approval rules.
Holding the Review sheet until the clinician answers was declined because it makes delegation
unreliable. Letting the delegate answer was declined because nothing in its view settles whether the
visit was the practice's; that is the guess this run made.

## Ruling 5 — a general bound on delegation is not decided here

No list of what a delegated answer may never decide is ruled here, because rulings 1 through 4 no
longer depend on one. This run's status guess is recorded on
[#1461](https://github.com/mshamblin5150-code/clinical-skills/issues/1461), where a delegated answer
dropped skill-required BMI codes, as a second instance of a delegated answer overriding a written
rule.

## Supersedes

- [ADR 0250](0250-a-review-sheet-carries-final-coding-only-after-the-batch-is-fresh.md) ruling 4,
  its sentence that status comes from the identity map or Medatrax evidence. Ruling 2 adds the
  clinician's recorded answer as evidence where the shorthand mentions an earlier visit the records
  lack; a shift-relative inference is still not evidence, and an unknown status still blocks.

## What this does not reach

Ruling 2's question depends on a pass noticing that the shorthand mentions an earlier visit; no
check reads the shorthand for that mention, so a missed mention codes from the account evidence
without a question. `coding_freshness.py` checks the shape of the evidence, not whether the
recorded answer supports the status. Whether the clinician's practice and the CPT group are the
same is his reading, not the run's.
