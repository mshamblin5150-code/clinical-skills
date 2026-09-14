# A shift is entered into Medatrax after one go-ahead and confirmed by one posted reading

[#1205](https://github.com/mshamblin5150-code/clinical-skills/issues/1205) was filed from
[#1015](https://github.com/mshamblin5150-code/clinical-skills/issues/1015)'s grilling.
[ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
ruled that `clinical-note`, `icd10-cpt` and `batch-shift` hand off by posting to Medatrax and granted
no exception while none of them does. [ADR 0221](0221-a-posted-reading-carries-the-fingerprint-of-the-source-it-read.md)
then required every posted reading to carry `SUBMISSION-SHA256`. The ticket asked for the posting
step itself: the go-ahead, who enters what, what the record's locator and time mean in the portal,
the unit of the record, the coding skill's hand-off, and the fingerprint's source.

Grilled 2026-09-14 across two sessions to an empty frontier. **Fifteen rulings, by the clinician, on
that date.** Nothing is built here; this is the record the build reads.

## Measured before ruling

Two delegated readers opened the live portal on 2026-09-14, view only, and changed no record. Each
reported labels and shapes and no patient value. The facts below are their reports and were not
re-derived by a second pass; the supervised entry in ruling 15 is where they are next exercised.

**1. The Time Log holds no clock times.** Its saved-entry list has `Date`, `Hours` as a duration and
`Confirmed`; its entry form takes hours and minutes only. The detail report adds `Created` as a date
with no time.

**2. Patient Detail shows each visit's clock times and no saved time.** The visit block reads
`Time: HH:MM - HH:MM`. Its Forms table carries `Finished` as a checkmark and `Date` as a date only.

**3. Both locators reopen directly.** A `patientdetail.aspx?patid=<id>&visitid=<id>` address pasted
into a new tab loads the same visit, and a `forms/ComprehensiveSoapNoteV2.aspx?resultid=<id>`
address loads the same form. The form's id is a short sequential number, so a guessed one plausibly
opens another student's note; it is only ever copied from the View link.

**4. The note is a separate form from the visit.** The View page holds the note text in six
textareas (Subjective Data, Objective Data, Assessment/Analysis, Plan, Intervention, Evaluation) and
repeats course, date, patient, location and preceptor. It holds no start or end time, case type or
patient time.

**5. The only time of day is the Patient Visit List's `Created` column**, shaped
`M/D/YYYY H:MM AM/PM`. Whether it shows a returning patient's new visit or the patient's first
creation was not measured.

**6. The reference already records that no existing visit carries Add Visit Data**, under its
*Still to confirm* list: *"Do the new courses require structured visit data (ICD-10 / Clinical
Experience Check), given none exists today?"*

## Ruled 2026-09-14

### 1. One go-ahead per shift

The clinician reviews every note in the shift, the patient list showing each patient as matched to
a Patient Reference or as a new patient, the preceptor, and every E/M line, and then says go once.
A standalone `clinical-note` run is a one-encounter batch under the same rule. **A go-ahead per
encounter was refused**: the shift is what he reviews, so it is what he approves.

### 2. The agent enters the batch one patient at a time

After the go-ahead the agent enters each patient in turn: the patient, the visit, then its note form.
The clinician reports that Medatrax has no batch upload, so the batch is the unit of approval and of
the record, never of the portal operation.

### 3. A new patient's Patient Reference reaches the identity map at once

Immediately after Medatrax generates a Patient Reference for a new patient, the agent writes it into
the identity map, so a returning patient is matched rather than created a second time.

### 4. Every visit falls inside the shift

A visit's start and end both fall between the shift's start and its end. The agent asks the shift's
start time once per batch; the end is that start plus the hours the Time Log holds for that date.
Where the Time Log has no row for the date yet, the agent asks the start and the hours together.
On a shift ending at 2100, a 20-minute visit starts no later than 2040. **Reading the shift's hours
from the Time Log alone was refused on measurement 1**, and **re-reading the Time Log before entry
was refused** as a check the clinician makes at review, where every visit's times are shown.

### 5. The preceptor comes from the day file's title and the private profile

The agent reads the preceptor named in the day file's title and resolves it through the tables in
the clinician's private profile. A name in neither table is asked once and added. The resolved
preceptor is shown at the go-ahead review. Because the shipped skills are clinician-agnostic,
`setup-clinical-skills` asks each clinician, per course, who the primary preceptor is and what goes
in the Preceptor box when a day file names someone not on the picklist: the primary preceptor, or a
question each time. **Shipping one clinician's substitution as the default was refused**: it was a
workaround the picklist forced, not a program rule. **Asking every shift was refused** where the
title and the tables already answer.

### 6. Every saved visit is read back

After entry the agent reopens every saved visit and its note form and compares each with its note
and field block. The reading states `N of N read` and names any mismatch by patient number and field.
**A sample, and no read-back, were both refused.**

### 7. A mismatch is corrected to what was approved and read again

Where a saved field differs from what the clinician approved, the agent corrects that field, reopens
the visit, and the reading records the correction. Anything beyond making a saved field match the
approved batch stops for the clinician, including a change to a note and a saved value that may be
the right one. **Stopping on every mismatch, and reporting without correcting, were both refused.**

### 8. Interrupted entry is checked before it resumes

When entry stops partway, the agent signs back in, reads back every visit already saved, and
searches the Patient Visit List for a record created during the interruption. With none, it resumes
at the first unsaved patient. With a partial record, it stops and tells the clinician, because a
retry would make a duplicate and the agent deletes no record. **Stopping on every interruption, and
an immediate retry, were both refused.**

### 9. Diagnosis codes are entered nowhere but the note

The preexisting and final diagnosis codes stay in the note. Nothing is entered under Add Visit Data,
matching the clinician's own practice. **Entering ICD-10-CM codes, and entering them only when a
course requires it, were both refused.**

### 10. The coding skill rides on the note

`icd10-cpt` records no posted reading of its own. Its codes are confirmed in the read-back of the note
that carries them, and its review uses that note's submission key: the shift key where `batch-shift`
owns the run, and the note's own key otherwise. This corrects ADR 0206 ruling 2's inclusion of
`icd10-cpt` among the skills that post. **A separate record for the same visit was refused** as the
same check written twice, and **an exception was refused** on ADR 0206 ruling 3.

### 11. Every note carries a proposed full E/M code

Each note carries an office E/M line naming the full code, whether the patient is new or established,
and the three elements that set the level: problems addressed, data reviewed and risk. The clinician
verifies it at the go-ahead review, which keeps codes proposed rather than asserted. This reverses
`icd10-cpt`'s *"Do not select an E/M level unprompted."* for the note. **Proposing only the
new-or-established family, and a code only on request, were both refused.**

### 12. New or established follows CPT, read from the shorthand

A patient is established when the clinician, or another clinician of the same specialty in the same
group, provided professional services within three years; otherwise new. The agent reads that from
the shorthand. Where the shorthand does not say, it falls back to the identity map, with an identity
map match reading as established, and marks the line `new/established assumed from Medatrax`.
**The identity map alone was refused** because it disagrees with CPT when a preceptor saw the patient
first or when a patient from an earlier site arrives at another group. **Asking at review for every
unsettled patient was refused.**

### 13. One posted reading per shift, with a line per visit

The record stays `## REREAD: <submission key>`, so ADR 0206 ruling 6 holds. `POST-URL` is the Patient
Visit List and `POSTED` is the `Created` time of the last visit entered, as the portal displays it.
Beneath them each visit has one line carrying its patient number, its Patient Reference marked
matched or new, its Patient Detail address, its note form's View address, its `Created` time and its
verdict. Every locator and time is copied from Medatrax. Where `Created` proves to show a returning
patient's first creation rather than the visit, that line carries the visit date instead.
**A record per visit was refused** because the shift's key would then name no single record and no
line would state `N of N`. **A time written by the agent was refused** as not read off the portal.

### 14. The fingerprint covers every note in the shift together

`SUBMISSION-SHA256` is one digest over the shift's note files in note order; a standalone note's is
the digest of its one note file. The completion grader that already grades the skill refuses a
missing or stale value: `filled_vitals_census` for a shift and `differential_scan` for a standalone
note. **A digest per note was refused** as format the record does not need, and **fingerprinting the
review packet was refused** because the identity map writes of ruling 3 change it during entry.

### 15. The build is gated on one supervised entry

Before the build, an attended session runs a real shift from the new course's shorthand, which the
clinician names, through the notes and his go-ahead, and enters the first patient with him through
the read-back. He shows the steps a person takes; that session records them as the entry procedure in
the Medatrax reference. An unattended agent then builds everything else from that record. The ticket
carries `ready-for-agent` and `blocked`, and the gate clears when the reference holds that procedure
and #1205 carries a comment saying the supervised entry ran. **One attended session for the whole
build was refused** as spending the clinician's time on work that does not need him, and **building
without the entry step was refused** because it leaves the skills unable to post while their reviews
keep failing.

## Taken as conventions, not ruled

- `clinical-note` writes the E/M line, since `batch-shift` never invokes `icd10-cpt`. The agent
  stated this to the clinician and he did not object.
- A shift's digest is the SHA-256 of the note files' bytes concatenated in ascending note number,
  computed with `file_digest` before `/AAR` extracts, per ADR 0221's convention.
- The per-visit line is one `VISIT:` field per visit, and the record parser accepts it for the
  portal record alone.

## Consequences

- `skills/batch-shift/SKILL.md`, `skills/clinical-note/SKILL.md` and `skills/icd10-cpt/SKILL.md` gain
  the go-ahead, entry, read-back, correction, interruption and record steps, the visit-time bound, the
  E/M line, and the posted-reading hand-off.
- `skills/setup-clinical-skills/SKILL.md` asks ruling 5's two per-course questions.
- `reference/medatrax-fields.md` retires *"Entering encounters through the portal is out of scope for
  this pass"* and gains ruling 15's procedure and the Add Visit Data rule of ruling 9.
- `skills/clinical-note/SKILL.md`'s *"`Preexisting diagnoses (ICD10)` and `Final diagnosis` are
  Medatrax fields"* is corrected: they are note headings, and ruling 9 enters their codes nowhere else.
- `skills/batch-shift/SKILL.md`'s claim that `clinical-note` *"never writes a document"* is corrected,
  since a standalone note is written to `output/notes/`.
- `discussion_artifact`'s record parser, `aar_scan`'s posted-reading block and the two graders of
  ruling 14 move with rulings 13 and 14; `specificity_scan` reads the note's key per ruling 10.
- The clinician's private profile no longer says to ask the preceptor on every shift not yet entered.
  That file is gitignored and nothing about it is committed.
- `CONTEXT.md` widens **Posted reading** to a shift's visits.

## What this does not reach

**Whether a matched patient is the right person.** The identity map is the only join between a name
and a Patient Reference, and a wrong row enters a real visit under the wrong patient with nothing
in the portal to catch it.

**Duplicates made before this step.** A read-back confirms what was entered, not the patient list it
was entered into.

**The supervised shift's own final grade.** It runs before the build, so its review is graded by the
tree as it stands that day.

**Whether the program credits the visit.** A read-back that matches says the portal holds what was
approved, not that the course counts it.
