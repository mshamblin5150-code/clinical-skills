# day-a — assertion set

Ten encounters from a single twelve-hour family-practice shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

## Status — both halves built

**The inputs are in.** All ten encounters are transcribed from the scan into [shorthand/](shorthand/), one file per case, de-identified. Every DRIFT and REPORTED row has a source line in the scan.

**The reference is read.** All ten submitted notes were opened in the portal on 2026-08-09 and are kept, un-de-identified, in `scratch/day-a-reference/` — gitignored, because they carry the visit date, the site and the clinician's own social-history detail. Every row below now records what the submitted note actually did.

**Inputs must come from the scan, never from the generated notes.** That output already contains the skill's reading of the shorthand — defects included — so a set derived from it would pass forever, on exactly the cases it exists to fail. The same trap applied to the reference half, and reading it changed four of the six DRIFT rows.

**Run 1, 2026-08-09: `DRIFT 10/10` · `REPORTED 14/14` · block 6/6 tested.** Output in `scratch/day-a-run-1/`.

That number carries a caveat worth more than the number. **The run and the grading were done by the same pass**, which is the arrangement [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) rejected for the drift matrix. Checking against output text rather than a self-report is the safeguard the ADR chose and it holds here, but a first run graded by its own author is a **baseline recorded, not a bar cleared.** The value of run 1 is that run 2 now has something to differ from.

**Eight of the twenty-four rows came back *neither*, not *better*** — D3, D5, R6 and R8 among them. Before the reference was read the set implied every row was a catch.

The scan is the single PDF in `scratch/day-files/`, gitignored, **7 pages**, image-only — no text layer, so it is rendered at 140 DPI and read visually. Its filename carries the visit date and the preceptor, so it is named here by location rather than quoted. An earlier note in this file said 19 pages; that was the count of *day files* in the clinician's Drive folder, not pages in this one.

**Case 1's shorthand exists.** The working file carried only a schedule row for it, which left open whether the encounter had ever been written down. The scan answers it: `Note 1`, 60 F, complete vitals, exam and plan. The hole was in the working file, not the source.

## The reference is a baseline, not a target

The submitted notes are what was documented under time pressure at the end of a twelve-hour shift. The skill is not trying to reproduce them — it is trying to **beat them, identically, every run.**

So a difference from the reference is not automatically a failure. It is one of three things, and the set has to say which:

- **Better** — the skill caught something the submitted note dropped. That is the product working. Every DRIFT row below is one of these.
- **Worse** — the skill lost something the submitted note had. A regression, and the most important thing this set can find.
- **Neither** — different wording for the same content. Ignore it; this is why the set does not diff prose.

## DRIFT — binary, all must pass

Each row is a finding the shorthand documented and the original note then abandoned. A run passes the row when the finding is named in the **Assessment or the Plan** — not merely recorded in the Objective.

The **Reference** column says what the submitted note actually did, read from the portal on 2026-08-09. It is what makes *better* / *worse* / *neither* answerable instead of assumed.

| # | Case | The finding | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 2 — 40 F | Hemoptysis in a smoker | No imaging is ordered or discussed | Named hemoptysis, listed pneumonia as "Unlikely" on auscultation alone, **ordered no film**. Imaging is *better*. |
| D2 | 5 — 45 F | Positive Rovsing's sign | Not named in the Assessment or the Plan | Carried `+ Rosvig` into the Objective and stopped. Pure drift. Naming it is *better*. |
| D3 | 5 — 45 F | BP 151/93 | Not named in the Assessment or the Plan | **Addressed it** — `Essential HTN I10 (elevated BP today)` in the Assessment, home BP log and PCP review in the Plan. Matching this is *neither*; losing it is *worse*. |
| D4 | 6 — 37 M | Pulmonary embolism, against family history of DVT/PE, HR 115, pleuritic pain, BMI 43.9 and diminished breath sounds | PE is absent from the differential | Ran URI / CAP / sinusitis and **ordered a CXR** — the differential does reach past URI. **PE never appears.** Considering it is *better*. |
| D5 | 9 — 11 F | Anatomical snuff box tenderness after a fall | Scaphoid is absent from the Assessment | **Named it first** — "Scaphoid fracture (occult) … must exclude" — and immobilized in a **thumb spica**. Only the coded diagnosis is sprain. Matching this is *neither*. |
| D6 | 10 — 25 M | Months of dysuria with right CVA tenderness | The GU problem is absent from the **final diagnosis** | Built a GU differential and ordered UA + culture, then coded only the ankles — the Final line reads `Bilateral ankle pain-M25.571 & M25.572;` and stops mid-line. Coding it is *better*. |
| D7 | 6 — 37 M | HR 115 | Not named in the Assessment or the Plan | Recorded, never addressed. |
| D8 | 7 — 10 F | HR 119 | Not named in the Assessment or the Plan | Recorded, never addressed. The temperature beside it *was* addressed. |
| D9 | 8 — 23 F | HR 114, with palpitations documented in the ROS | Not named in the Assessment or the Plan | Recorded, never addressed. |
| D10 | 10 — 25 M | BP 141/93 in a 25-year-old | Not named in the Assessment or the Plan | Recorded, never addressed. |

D7–D10 were promoted from REPORTED after the reference read. They are one defect — **a vital recorded and abandoned** — occurring four times across four patients, which is the pattern a shift roll-up is supposed to make visible and a single note never does.

Issue #1 named five defects. These are six, because its fifth bullet — "BP 151/93, HR 115, never mentioned" — bundles two findings from two different patients.

**Two of these six were wrong before the reference was read.** D3 and D5 both asserted the original had abandoned a finding it had in fact carried into the Assessment and the Plan. Both were written from the skill's own prior output, which is exactly the failure `fixtures/README` warns about — and the reason it is worth saying plainly is that a set claiming credit for catching what the clinician already caught is not measuring anything. D4 and D6 needed narrowing for the same reason. Only D1 and D2 survived unchanged.

## REPORTED — counted, not enforced

| # | Case | Claim | Reference did |
| --- | --- | --- | --- |
| R1 | 3 — 18 | BP 139/85 in an 18-year-old is elevated and gets addressed | Recorded it; never addressed. BMI 40.9 appears only as a recovery-biomechanics aside. |
| R2 | 4 — 48 F | Unprotected intercourse × 2 days documented → STI testing considered | Wrote "STI risk with recent unprotected intercourse" and ordered nothing for it; recorded that no pelvic exam was done. |
| R3 | 4 — 48 F | 32 pack-years → LDCT screening discussed | No screening section at all. Tobacco appears only as an ICD-10 code. |
| R4 | 6 — 37 M | Motrin 800 TID against documented GERD is called out — **and the flag fires whatever the inferred home regimen contains** | **Asserted omeprazole 20 mg QD** as a home med, then let that silence the conflict. Inferring a PPI is not itself the defect: `clinical-note` instructs that an absent `meds:` line with documented conditions be inferred. Suppressing the flag because of the inference is. |
| R5 | 6 — 37 M | Second positive Rovsing's, with RUQ and LLQ tenderness, is not left undiagnosed | Worse than undiagnosed — **the Objective has no abdominal exam at all**. All three findings vanished between shorthand and note. |
| R6 | 7 — 10 F | Temperature rising 99.2 → 102 during the visit is addressed | Addressed — recorded as a recheck, called out in the general appearance, coded `Fever-R50.9`. *Neither.* (The HR 119 half of the original row is now D8.) |
| R7 | 7 — 10 F | Diffuse lower abdominal tenderness is not left undiagnosed | Reached the Objective; three diagnoses made, none abdominal. |
| R8 | 8 — 23 F | Unilateral exudate plus syncope → peritonsillar abscess and mono explicitly excluded | **Did both**, with the reasoning for each. *Neither* — and losing either is *worse*. |
| R9 | 8 — 23 F | Amoxil listed as current while clindamycin is added → a stop instruction appears | Dropped amoxil from the med list entirely, so no conflict appeared to resolve. |
| R10 | 9 — 11 F | Implausible vitals are questioned rather than transcribed silently | BP 133/86 and BMI 37.9 in an 11-year-old, both transcribed without comment. |

### Found by reading the reference

These came out of the submitted notes, not from issue #1. All are drift-class.

| # | Case | Claim | Reference did |
| --- | --- | --- | --- |
| R11 | 1 — 60 F | Left CVA tenderness and epigastric tenderness are not left undiagnosed | Both reached the Objective; the Assessment is respiratory only. |
| R12 | 2 — 40 F | PCOS from the history reaches the note | Dropped. PMH lists only PE tubes and tonsillectomy. |
| R13 | 8 — 23 F | `fainted on saturday` is carried as syncope, not softened | Downgraded to "lightheaded" and "dizziness". |
| R14 | 3, 6, 8, 10 | No tobacco or vaping status is asserted where the shorthand supplies none | Invented one in **all four** — "vapes occasionally", "former smoker", "vape occasionally", "smokes 0.5 PPD". Case 10's shorthand says `hx: none`. |

R14 is the one to watch. Four inventions across ten notes, all in the same field, all plausible — this is what *every filled finding is normal, absent, or not reported* is for (`no smoke exposure reported`), and it is the failure mode a tired clinician and a generative model share. Standing rule 2's list names no category that reaches it.

The rest stay counted rather than enforced. The four vitals rows were promoted to D7–D10 because they are one repeating defect with unambiguous pass conditions; these are not, and a bar is only worth having if it was set deliberately.

## Block-structure assertions

Deterministic checks on the shape of the output rather than its clinical content. They lock in the block rules settled alongside this set, and they are counted with REPORTED rather than enforced — promote them once the set has run often enough to show they hold steadily.

| # | Claim |
| --- | --- |
| F1 | `Primary Payment Method` never appears under GAPS — it is filled from the declared rule |
| F2 | `Start/End estimated` never appears under GAPS |
| F3 | `Race/Ethnicity` appears under `FILLED·asserted`, never under GAPS |
| F4 | Every `FLAG` names both the finding and what was not done with it — never a bare category like "vitals not addressed" |
| F5 | Case 10's shorthand states no age, so the run reports age under GAPS and leaves `Patient Time` unfilled — it never guesses a band |
| F6 | Case 10's sex is read as male from the narrative pronouns and is not reported missing |
| F7 | Fed the portal demographics alongside the shorthand — 25, male — case 10's Patient Time band is `Adult (18 – 60)` |

F5 replaced a row that asserted the band outright. That row was written before the shorthand had been read, on the assumption the age was in it. It is not, so asserting the band would have graded the skill on filling a value it has no source for.

## Resolved against the portal, 2026-08-09

**Case 10 is 25, male, African American/Black.** Matched on every recorded field — BP 141/93, height 66, BMI 37.1, RR 20, Case Type Musculoskeletal, marital single. Not a judgment call; the portal record and the note agree on all six.

**There is an eleventh encounter and it is not a fixture case.** 29 F, Case Type Gynecology, BP 118/76, height 64, RR 16 — and it already has two comprehensive SOAP notes attached in the portal. The note exists; the *day file scan* is missing it. It is not part of this set because its shorthand was never captured.

**Recorded times differ from the estimates.** The portal has case 10 at 19:20–19:50; the working file estimated 16:35–17:00 from an assumed 09:00–21:00 shift. The Times convention produces plausible times, not real ones, and the two should not be expected to agree. Recorded times across the day run 09:30 to 20:35 — so the assumed twelve-hour shape was about right and only the placement was off.

**Case 3's recorded gender contradicts the shorthand.** The portal says `Gender: Female`. The shorthand says `18 yo M` and the narrative is "he can bear weight but it hurts". Every other recorded field on that visit matches — height 70, BP 139/85, RR 20, BMI 40.9 — so this is one wrong picklist, not a mismatched patient. Worth correcting in the portal; it is not a fixture question.

**Primary Payment Method is not a constant.** On this day the eleven encounters carry six `Medicaid`, three `Commercial insurance/HMO/PPO` and two `Medicare` — including `Medicare` on a 23-year-old. `reference/medatrax-fields.md` previously recorded that all eleven were `Medicaid`; they are not, and the rule there has been changed to match.

## Still unresolved

- **The set has never been run.** Both halves exist; no `clinical-note` output has been checked against them. Until it is, `DRIFT n/n` and `REPORTED n/m` have no first value to measure drift from.
- **Case 10's opener.** The shorthand states no age and no sex. This is a defect in the source, kept in the input file deliberately rather than patched, and it is what F5–F7 test. The portal supplies 25, male.
- **Whether R11–R17 should be binary.** They are drift-class and evidenced, but they were found after the bar was agreed. Promote them deliberately or not at all.
