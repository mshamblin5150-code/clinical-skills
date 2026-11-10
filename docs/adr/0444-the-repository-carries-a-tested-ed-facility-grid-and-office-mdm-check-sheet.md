# The repository carries a tested ED facility grid and office MDM check sheet

**Measured at:** 3fae242d94968af871734a2eab4357a4866bf67e

On 2026-11-10 the clinician asked for an E/M check sheet a human coder could use, for a hospital
emergency department and for an independent office, built from research and tested by coders. The
session drafted three sheets, tested them through several versions, ran a research pass on each
open question, and put each decision that was the clinician's to him one at a time. He chose the
intervention grid for the hospital, retired the point sheet, and asked that the repository carry
the result. The freshness gate read `FRESH` against `main` before this record was written.

## Measured before ruling

**The panels.** Two synthetic panels of 65 encounters each (40 emergency department, 25 office),
both drawn to the national visit mix estimated from NCHS public-use microdata (NHAMCS 2022 and
NAMCS 2019). The second panel was written by an agent that could not see the sheets, with no
scenario repeated from the first. Every case is synthetic; no patient record was used.

**The test.** On every run three coder models coded every case independently from the sheet
alone, and an adjudicator ruled on every case where they disagreed, naming the cause as the
sheet's wording, a missing rule, the record, or the coder. Separate adversarial reviewers read
three of the versions, and a skeptic checked each review finding before it was applied.

**The result on the adopted versions.** All three coders agreed on the ED level in 95% of the
original panel and 97.5% of the fresh panel, and no disagreement on either panel was blamed on
the grid's wording. All three agreed on the office code in 92% of both panels; every coder
matched the reference on 24 or 25 of 25. One run of 40 or 25 cases varies by about five points by
chance, and the office sheet's last runs each surfaced a different interpretive edge of the CPT
definitions rather than a repeated one.

**The research.** Six open questions were researched against saved sources, each answer checked
by a skeptic. CMS leaves ED facility leveling to each hospital's written guidelines and lets a
hospital use separately payable services "as a proxy to measure hospital resource use that is not
associated with those separately payable services" (CY 2008 OPPS final rule, 72 FR 66806). The
BCBS Texas facility policy CPCP003 is the grid's item source. Its October 2025 version carries
the same items as its 2023 version.

## Ruling 1 — the repository carries the ED facility grid, and the point sheet is not adopted

`reference/ed-facility-grid.md` is the hospital facility-level tool. It sets the hospital's level
(99281–99285, or G0380–G0384), never the clinician's professional level. Each departure from BCBS
Texas is marked in the grid. The clinician's choices on 2026-11-10 are:

- a study ordered from the ED and performed during the ED portion is the evidence of the staff's
  imaging preparation;
- serial cardiac studies need two or more repeats for Level 5;
- temperature instability means a core temperature below 95.0 °F or at or above 104.0 °F, treated
  with an active warming or cooling device;
- an item naming a service, such as epistaxis packing or tube placement, counts whoever performs
  it;
- a documented staff chaperone counts as the assist for a pelvic examination.

The point sheet was declined because its bands were never measured against staff time and it
scored services its own packaging rule excluded.

## Ruling 2 — the office check sheet's house rules govern the office E/M level

`reference/office-mdm-check.md` applies the committed CPT 2026 entries to an office or other
outpatient visit, citing them by id. Its house rules are the clinician's rulings:

- **Refills.** A renewal, or a decision to continue a prescription drug, counts as prescription
  drug management when his shorthand or recorded answer shows he addressed the problem the drug
  treats. A continuation only the note pass wrote is a proposed drug under
  [ADR 0308](0308-the-e-m-level-rests-on-what-the-clinician-did.md) ruling 3.
- **Hospitalization.** A decision regarding hospitalization, including one considered and not
  selected or a transfer from the office to the ED, counts only when his own record shows the
  decision and that the condition approaches the threshold for hospital-level care.
- **Device renewal.** Renewing his order for a prescribed device or its supplies, such as CPAP,
  supports low risk.

Its counting notes and documentation checks apply as written. They interpret the CPT text and may
require more documentation or a lower level, but never support a level the CPT text does not.

## Ruling 3 — `icd10-cpt` applies the office check sheet when it selects an office level

When `icd10-cpt` step 5 selects an office or other outpatient E/M level, it applies
`reference/office-mdm-check.md` alongside the passing CPT sheet. Where the check sheet asks the
clinician a level-changing question, the question goes into the run's existing pre-approval
questions under ADR 0308 ruling 2. The emergency department grid is never used for the
clinician's professional level.

## Consequences

- `reference/em-point-systems.md` points to both sheets and records the research findings.
- `skills/icd10-cpt/SKILL.md` step 5 names the office check sheet.
- Every tested version, the decision log and the panels stay in the clinician's private working
  material; only the adopted versions are committed.

## What none of this reaches

The panels are synthetic, so the results show the wording is clear to independent coders; they
do not show the sheets hold on real charts. A pilot audit of real charts by a human coder is the
next measurement. The ED grid's choices are one hospital-guideline design among those CMS
permits; a hospital adopting it owns its written guideline. Three office edges found on the last
run are not yet written into the sheet: counseling about the condition a same-day procedure
treats, when an injury counts as acute and complicated, and when a new problem counts as
undiagnosed with uncertain prognosis.
