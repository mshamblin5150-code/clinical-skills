# An ambiguous answer is read back and earlier-care status is asked at the first stop

**Measured at:** cabc2146d99ad76f1e9b93d3ad471c5f9d02fbde

[#1803](https://github.com/mshamblin5150-code/clinical-skills/issues/1803) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift) on 2026-10-14. It proposed two
step 4 changes. A comment added a third, about where a practice rule the clinician states during a
run is written. A second comment proposed a mechanical check against a rapid screen written as
pending. Grilled 2026-10-17 against `main` at `d366ac2f`, where the freshness gate read `FRESH`;
the merge to the commit above changed none of the measured files. The clinician ruled every point below in that session, one question at a time. **Nothing
is built here; this is the record the build reads.**

## Measured before ruling

**The identity map is read after the step 4 stop, and Medatrax later still.**
`skills/batch-shift/SKILL.md` step 5 reads every identity-map row for an encounter's name. Step 7
opens Patient Detail before the Review sheet. The earlier-visit status question fires in step 7,
only when the shorthand mentions an earlier visit and neither record holds the patient. A step 4
question therefore needs the identity-map read moved before that stop.

**ADR 0384 ruling 4 names step 7's block.** A `clinician-answer` status carries "the clinician's
whole reply to the pre-approval questions block, verbatim", which `coding_freshness.py` checks with
`approval_record.verify_clinician_reply` and requires to follow the day file or shorthand. #1648
builds it; it is open and `coding_freshness.py` does not yet read a reply.

**A note pass reads the per-account shorthand file and its brief, not memory.**
`skills/clinical-note/SKILL.md` tells a pass to read `scratch/shorthand.md` first.
[ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
ruling 3 builds each brief from the current skill, standing rules and memory, but a brief already
sent carries nothing written after it. All three practice rules the clinician stated in the
recorded sitting are rules for reading his shorthand.

**A profile-keyed note check has a precedent.** `tools/exam_scheme.py` grades quadrant wording only
where the account profile saves a nine-region abdominal scheme.

## Ruling 1 — an answer that parses more than one way is read back before step 5

Where an answer to the step 4 stop can be parsed more than one way — a run-together number, a
dropped word, or an answer that could belong to two encounters — the orchestrator restates the
parsed value per encounter and waits for the clinician's confirmation before any note pass starts.
Reading back every answer was declined because it charges every shift a reply for a guess that
happened once. Always reading back a supplied age or sex was declined for the same reason; the
recorded orchestrator knew it was guessing, so the ambiguity trigger reaches the recorded failure.

## Ruling 2 — the same read-back binds the pre-approval patient questions block

The rule is written once in `skills/clinical-note/SKILL.md` beside its `PRE-APPROVAL PATIENT
QUESTIONS` block, which `batch-shift` step 7 already says binds its own block. An answer there sets
patient status, an age or sex correction, or an E/M level, and a guessed parse forces a re-render.
A standing rule for every skill was declined: coursework stops show the exact text at the go-ahead,
and no recorded failure reaches them.

## Ruling 3 — earlier-care status is asked at the step 4 stop

Before the step 4 stop, the orchestrator reads the identity map by name. An encounter whose
shorthand mentions earlier care at the practice, with no identity-map row, is listed on a new
output line, `Earlier care mentioned, no identity-map row: <which encounters, or "none">`, and the
clinician is asked once whether he saw the patient within three years. The answer is the status
evidence step 7 retains, so the step 7 question does not fire again for that encounter. A delegate
never answers it. Step 7 is unchanged for an encounter step 4 did not settle.

Checking Medatrax before the stop as well was declined: a signed-in portal lookup before the first
stop costs more than the occasional unneeded one-word answer it saves. Leaving the question to
step 7 alone was declined because a late `established` moves the E/M family and re-renders a
finished note.

## Ruling 4 — a status reply at either stop is the recorded reply

A `clinician-answer` status carries the clinician's whole reply, verbatim, to whichever stop asked
the earlier-visit question: the step 4 stop or the pre-approval questions block. The check is
unchanged: the reply must be his own message and follow the day file or shorthand it answers.
Re-asking a step 4 answer in the step 7 block was declined because it asks him twice for the
rule's wording rather than its purpose. A separate evidence value for a step 4 answer was declined
as code for no clinical gain.

## Ruling 5 — a practice rule stated during a run goes to the shorthand file and every later brief

A practice rule the clinician states during a run is written to `scratch/shorthand.md` in his own
words, with the date. Every later note-pass and repair brief that run sends carries it as a binding
line. Memory keeps at most a one-line pointer to the file. The orchestrator never tells him a
future pass will follow a rule held only in memory. A full memory copy beside the file was
declined as two copies of one rule that can drift. Memory alone was declined because a pass reads
only its brief and the shorthand file.

## Ruling 6 — notes written before the rule are rechecked and repaired

When a practice rule arrives mid-run, the orchestrator rechecks that run's unapproved notes against
it. Each note that reads the shorthand against the rule gets a **Repair pass** bounded to what the
rule touches, and the go-ahead names those notes. An approved or posted note is never changed
silently; it is named to the clinician with the conflict and he decides. Applying the rule forward
only was declined because it leaves a known error for review. Asking before each repair was
declined because the rule he just stated already settles the answer.

## Ruling 7 — a rapid screen written as pending is refused where the profile declares the rule

A check refuses a finished note that writes a rapid strep, influenza, COVID-19 or RSV screen as
pending or awaiting a result, only where the account profile declares that rapid screens are
negative unless stated. It runs for `batch-shift` and standalone `clinical-note`. A rapid screen
written as not performed or declined passes, and a send-out culture or PCR is outside it. An
account without the declaration is not graded. An unconditional check was declined because it
writes one clinician's practice into every account's tooling. No check was declined because a pass
that ignores its brief reaches review, as one did on the next recorded shift.

## Supersedes

- [ADR 0384](0384-course-assignment-s-gate-2-and-a-recorded-patient-status-answer-carry-the-clinician-s-whole-reply.md)
  ruling 4, the words "the clinician's whole reply to the pre-approval questions block, verbatim".
  The recorded reply is his whole reply, verbatim, to whichever stop asked the earlier-visit
  question, the `batch-shift` step 4 stop or the pre-approval questions block. The check through
  `approval_record.verify_clinician_reply`, the requirement to follow the day file or shorthand,
  the refusal of an unheld reply, and the delegated fallback still stand.

## Build checklist

- `skills/batch-shift/SKILL.md` step 4: the read-back paragraph (ruling 1) placed before `Resume
  only on the clinician's confirmation or correction.`; the identity-map read moved before the stop,
  the `Earlier care mentioned, no identity-map row` output line and its paragraph (ruling 3).
- `skills/batch-shift/SKILL.md` step 5: the practice-rule paragraph (rulings 5 and 6).
- `skills/batch-shift/SKILL.md` step 7: the status paragraph says the question fires only for an
  encounter step 4 did not settle.
- `skills/clinical-note/SKILL.md`: the read-back sentence beside the `PRE-APPROVAL PATIENT
  QUESTIONS` block (ruling 2); the practice-rule home beside the instruction to read
  `scratch/shorthand.md` first (ruling 5).
- #1648's build of ADR 0384 ruling 4 accepts a reply to either stop (ruling 4).
- The rapid-screen check (ruling 7): a profile declaration in `scratch/medatrax-profile.md`, a
  grader row run by both note skills, `DECLARED_LIMITS` naming the recognized wordings, and tests
  through the public command for a pending screen, a not-performed screen, a pending send-out
  culture, and an account without the declaration.

## What this record does not reach

- **An ambiguity the orchestrator does not notice.** Ruling 1 fires on a parse it recognizes as
  ambiguous; a confident misreading passes.
- **Whether a rule stated mid-run was written down.** Nothing grades that the orchestrator wrote it
  to the shorthand file or carried it into later briefs.
- **Rapid-screen wording the check does not recognize.** Ruling 7 refuses the forms it names and
  declares the rest.
