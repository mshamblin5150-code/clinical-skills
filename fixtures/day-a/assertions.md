# day-a — assertion set

Ten encounters from a single twelve-hour family-practice shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

## Status — documented, not yet runnable

The shorthand inputs are **not in this repo**. They exist in a scanned day file that has not been located. Until it is placed in `day-a/shorthand/`, this set records what a correct run must produce but cannot be executed.

**The inputs must come from the original scan.** They must never be reconstructed from the previously generated notes. That output already contains the skill's own reading of the shorthand — including every defect below — so a set derived from it would pass forever, on exactly the cases it exists to fail.

One further hole: **case 1 has no note body** in the working file, only a schedule row. Nine of ten encounters are documented. Whether case 1's shorthand exists is unresolved.

## DRIFT — binary, all must pass

Each row is a finding the shorthand documented and the original note then abandoned. A run passes the row when the finding is named in the **Assessment or the Plan** — not merely recorded in the Objective.

| # | Case | The finding | Fails when |
| --- | --- | --- | --- |
| D1 | 2 — 40 F | Hemoptysis in a smoker | The note diagnoses without addressing imaging. No CXR was ordered in the original. |
| D2 | 5 — 45 F | Positive Rovsing's sign | Diagnosed as URI with no abdominal workup. Rovsing's is an appendicitis sign; it is either a real finding that went unaddressed or a token meaning something else in this shorthand. |
| D3 | 5 — 45 F | BP 151/93 | Recorded and never discussed. Stage 2 hypertension. |
| D4 | 6 — 37 M | HR 115 with fever to 103, pleuritic pain, diminished breath sounds, BMI 43.9, family history of DVT/PE | Diagnosed as URI alone. The differential must reach beyond it. |
| D5 | 9 — 11 F | Anatomical snuff box tenderness after a fall | Diagnosed as sprain alone. Scaphoid must appear in the Assessment — scaphoid fractures are commonly occult on initial x-ray, so a normal film does not clear the row. |
| D6 | 10 — 25 M | Months of dysuria with right CVA tenderness | Only the ankles are diagnosed. Two problems presented; the note must address both. |

Issue #1 named five defects. These are six, because its fifth bullet — "BP 151/93, HR 115, never mentioned" — bundles two findings from two different patients.

## REPORTED — counted, not enforced

| # | Case | Claim |
| --- | --- | --- |
| R1 | 3 — 18 M | BP 139/85 in an 18-year-old is elevated and gets addressed |
| R2 | 4 — 48 F | Unprotected intercourse × 2 days documented → STI testing considered |
| R3 | 4 — 48 F | 32 pack-years → LDCT screening discussed |
| R4 | 6 — 37 M | Motrin 800 TID against documented GERD on no acid suppression is called out |
| R5 | 6 — 37 M | Second positive Rovsing's, with RUQ and LLQ tenderness, is not left undiagnosed |
| R6 | 7 — 10 F | Temperature rising 99.2 → 102 during the visit with HR 119 is addressed |
| R7 | 7 — 10 F | Diffuse lower abdominal tenderness is not left undiagnosed |
| R8 | 8 — 23 F | Unilateral exudate failing amoxicillin, plus syncope → peritonsillar abscess and mono explicitly excluded |
| R9 | 8 — 23 F | Amoxil listed as current while clindamycin is added → a stop instruction appears |
| R10 | 9 — 11 F | Implausible vitals are questioned rather than transcribed silently |

Several of these are drift-class and could be promoted to binary once the set actually runs. They start here because the agreed bar was the defects named in issue #1, and a bar is only worth having if it was set deliberately.

## Block-structure assertions

Deterministic checks on the shape of the output rather than its clinical content. They lock in the block rules settled alongside this set, and they are counted with REPORTED rather than enforced — promote them once the set has run often enough to show they hold steadily.

| # | Claim |
| --- | --- |
| F1 | `Primary Payment Method` never appears under GAPS — it is filled from the declared rule |
| F2 | `Start/End estimated` never appears under GAPS |
| F3 | `Race/Ethnicity` appears under `FILLED·asserted`, never under GAPS |
| F4 | Every `FLAG` names both the finding and what was not done with it — never a bare category like "vitals not addressed" |
| F5 | Case 10's Patient Time band is `Adult (18 – 60)` |

## Resolved against the portal, 2026-08-09

**Case 10 is 25, male, African American/Black.** Matched on every recorded field — BP 141/93, height 66, BMI 37.1, RR 20, Case Type Musculoskeletal, marital single. Not a judgement call; the portal record and the note agree on all six.

**There is an eleventh encounter and it is not a fixture case.** 29 F, Case Type Gynecology, BP 118/76, height 64, RR 16 — and it already has two comprehensive SOAP notes attached in the portal. The note exists; the *day file scan* is missing it. It is not part of this set because its shorthand was never captured.

**Recorded times differ from the estimates.** The portal has case 10 at 19:20–19:50; the working file estimated 16:35–17:00 from an assumed 09:00–21:00 shift. The Times convention produces plausible times, not real ones, and the two should not be expected to agree.

## Still unresolved

- **The shorthand inputs.** Nothing here runs without them.
- **Case 1 has no note body** in the working file — only a schedule row.
