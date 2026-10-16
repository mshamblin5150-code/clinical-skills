# A filled sig fits the entered diagnosis and the E/M reasoning says not documented rather than not done

**Measured at:** 43ef7bf3f285b58a0567d9373ab311c7840b9a73

[#1594](https://github.com/mshamblin5150-code/clinical-skills/issues/1594) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift. Its Filed-from line names the
shift after the one the two corrections actually came from; the run record, not the line, is what
was read here. The clinician ruled every point below on 2026-10-16, against `main` at the commit
above, where the freshness gate read `FRESH`. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**Both corrections came from one encounter.** Its shorthand named no drug. The note pass coded the
symptoms, refused acute pyelonephritis and acute cystitis among others, and wrote the E/M risk
reason as *"Risk low: he directed no drug."* At the pre-approval questions the clinician said he had
given ceftriaxone 1 g in the office and started trimethoprim-sulfamethoxazole for a urinary
infection. The rewrite entered a urinary infection with no site and filled a 14-day course, the
length used when the kidney is involved, beside the note's own refusal of pyelonephritis. The
clinician then supplied the actual course: three days.

**The level did not move on that encounter.** Problems and data already met moderate, so two of
three elements held 99204 whatever risk read. The false sentence was a claim about the clinician's
actions, not a coding error, and no existing question would have been asked about it.

**[ADR 0308](0308-the-e-m-level-rests-on-what-the-clinician-did.md) asks about problems and threat to
life, never about a drug.** Its ruling 2 puts one question to the clinician when leaving a condition
out lowers the level, and its ruling 5 does the same for a threat-to-life reading. Its ruling 3 counts
a drug the pass proposes on a problem he addressed, with the filled risk mark. Nothing asks whether he
gave a drug the shorthand omits. One note pass on an earlier shift asked exactly that on its own
initiative, naming both levels; no rule required it.

**The ticket's placement names the wrong paragraph.** It proposed inserting the course-length rule
after the paragraph that begins *"Every historical medication is complete enough to administer as
written"*, which governs the patient's home medications. The defect was in a Plan order, which
`clinical-note`'s *What may be inferred* list governs through its bullet *"Route, frequency, and
duration for a drug the shorthand names"*.

## Ruling 1 — every filled part of a Plan drug's sig fits the diagnosis the note enters

Where the shorthand, or the clinician's recorded answer, names a Plan drug and omits part of its sig,
every part the writer fills (dose, frequency and length) fits the diagnosis the note enters for
entry, and never a diagnosis the same note refuses. Where the entered code leaves severity open, as
a site-unspecified urinary infection does, the writer sizes the drug for the least severe reading
the note's own findings support. A writer whose findings support the more serious reading enters
that diagnosis rather than sizing the drug for it under a lesser code. The rule sits in
`clinical-note`'s *What may be inferred*, beside the route, frequency and duration bullet.

On the recorded encounter the tiebreak gives the clinician's own answer: the note refused
pyelonephritis, so the least severe reading is cystitis, and its course is three days.

Length alone, as the ticket drafted it, was declined because a filled dose can contradict the
note's coding the same way a filled length did, and because it left the site-unspecified case to
the writer's judgment, which is where the 14 days came from. Putting every diagnosis-dependent
antibiotic length to the clinician was declined on ADR 0308's ground for declining an every-drug
question: most infection encounters would carry one and the list would stop being read.

## Ruling 2 — the E/M reasoning states what is documented, never what the clinician did not do

The problems, data and risk reasons on the E/M line describe what the note documents. None of them
states that the clinician did not do something. An element graded low because the shorthand is
silent says the thing is not documented, never that it was not done: *no prescription drug
management documented*, not *he directed no drug*. The rule sits in `skills/icd10-cpt/SKILL.md`
step 5, which the note pass follows for the coding worksheet and the note's E/M paragraph alike, and
`clinical-note` points to it.

Ruling only the drug wording, as the ticket drafted it, was declined because the defect is a claim
about the clinician's actions drawn from silence, and the data and problems reasons can make it the
same way. The ruling changes only the wording of a reason and never the level.

## Ruling 3 — an undocumented drug is asked about when moderate risk would raise the level

When risk is graded below moderate only because no drug management is documented, and moderate risk
would raise the E/M level, the pass selects the lower level and puts one question in the run's
existing pre-approval questions: whether the clinician gave or prescribed a drug at this visit,
naming both levels. A yes, with the drug he names, enters the note as his order and counts toward
risk. No question is asked when moderate risk would not change the level. Where pre-approval
questions are delegated, the lower level stands, because a delegate cannot supply his answer. This
extends ADR 0308 ruling 2 to the risk element in the same shape and sits beside that ruling's text
in `skills/icd10-cpt/SKILL.md` step 5.

Letting the documented level stand silently was declined on ADR 0308 ruling 2's own ground: a drug
he gave and did not write down would stay undercoded unless he noticed its absence, and his recorded
practice is to leave drugs out of the shorthand when he is moving fast. Asking whenever no drug is
documented was declined because the question would sit on most encounters without changing a code.

## Consequences recorded as derived rather than ruled

- `skills/clinical-note/SKILL.md` *What may be inferred* carries ruling 1 beside its route,
  frequency and duration bullet, with the site-unspecified urinary infection as the worked example.
- `skills/icd10-cpt/SKILL.md` step 5 carries ruling 2 beside its E/M element reasoning and ruling 3
  beside the *Problems addressed* question, naming both as extensions of ADR 0308.
- The pre-approval question lists in `skills/batch-shift/SKILL.md` and `clinical-note`'s standalone
  block already link `icd10-cpt` step 5 for ADR 0308's question shape; that link carries ruling 3
  without a second copy.

## What this does not reach

Which reading of an open-severity code is least severe, and whether the note's findings support the
more serious one, remain clinical readings. No grader derives an E/M level or reads a reason's
wording: `anchor_scan.py` excludes E/M lines and `coding_freshness.py` verifies code identity,
edition and date status, so every ruling here is a required reading with no new gate claim. Preserved
run records are not edited.
