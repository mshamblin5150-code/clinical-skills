# day-a — assertion set

Ten encounters from a single twelve-hour family-practice shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

## Status — both halves built

**The inputs are in.** All ten encounters are transcribed from the scan into [shorthand/](shorthand/), one file per case, de-identified. Every DRIFT and REPORTED row has a source line in the scan.

**The reference is read.** All ten submitted notes were opened in the portal on 2026-08-09 and are kept, un-de-identified, in `scratch/day-a-reference/` — gitignored, because they carry the visit date, the site and the clinician's own social-history detail. Every row below now records what the submitted note actually did.

**Inputs must come from the scan, never from the generated notes.** That output already contains the skill's reading of the shorthand — defects included — so a set derived from it would pass forever, on exactly the cases it exists to fail. The same trap applied to the reference half, and reading it changed four of the six DRIFT rows.

**Run 1, 2026-08-09: `DRIFT 10/10` · `REPORTED 14/14` · block 6/6 tested.** Output in `scratch/day-a-run-1/`.

That number carries a caveat worth more than the number. **The run and the grading were done by the same pass**, which is the arrangement [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) rejected for the drift matrix. Checking against output text rather than a self-report is the safeguard the ADR chose and it holds here, but a first run graded by its own author is a **baseline recorded, not a bar cleared.** The value of run 1 is that run 2 now has something to differ from.

**Eight of the twenty-four rows came back *neither*, not *better*** — D3, D5, R6 and R8 among them. Before the reference was read the set implied every row was a catch.

**Run 2, 2026-08-16, against base commit `184462d`: `DRIFT 10/10` · `REPORTED 13/14` · `block 6/7` — 31 of 31 rows.** [#120](https://github.com/mshamblin5150-code/clinical-skills/issues/120).

**Output is in the main checkout's `scratch/day-a-run-2/`, not a worktree's**, which is what [#122](https://github.com/mshamblin5150-code/clinical-skills/issues/122) cost two earlier runs and what this ticket's fifth comment asked for before the run was graded. It was generated in a worktree and copied across, verified identical. `notes/` holds the eleven scored notes; `notes-branch-unstated/` holds four discarded drafts, kept because they are the evidence for the branch paragraph below.

**Twelve notes, eleven scored.** `notes/` contains the ten cases plus the F7 demographics variant. **F1 through F4 are reported over all eleven**, the variant included, because they are block-structure rows that every note answers. **F5 and F6 are scored on `case-10.md` alone** and F7 on the variant alone, which is the separation the ticket required — the two are different runs of one encounter and neither may answer for the other.

**The bar is clean and the two short rows are in counted classes**, which is a distinction this file has to keep making. DRIFT is the only binary class here, and it is 10 of 10. R10 and F5 are counted rather than enforced, so **this run does not fail its bar** — and neither row is worth less for that, because a counted row is where a defect gets seen before anybody decides whether to enforce it.

**Separated, which is the whole reason it exists.** Eleven generating passes with `assertions.md`, `fixtures/README.md` and `shorthand/README.md` withheld and the shorthand pasted inline; eight grading passes split by class, none of which saw a generation; and an orchestrating pass that authored no note and re-derived every row from the output text. `fixtures/` was closed to every generating pass for any purpose.

**The two rows that did not come back clean are R10 and F5, and neither is the skill regressing.** R10 is half-met on the case it names, and **F5 fails because the row and the skill now contradict each other** — see *What run 2 found* below. **No DRIFT row regressed**, which was the most consequential thing this run could have found: D7 through D10 are one repeating defect and all four pass.

**The run had to state the branch, and that is worth knowing before the next one.** This set is `clinical-note` on the comprehensive SOAP branch, and the first eleven passes were given the shorthand without being told which branch to take. **Four of them chose the FNP H&P**, reasoning from the program's first-six-encounters rule with no course context to check it against. Those four were discarded and regenerated on SOAP; the run scored here is eleven SOAP notes. Nothing was wrong with the four — the skill routed sensibly on what it had — but **a mixed-branch run cannot be scored against D6, which names the SOAP branch's `Final diagnosis` field.** *Running a set* step 1 already says *on the stated branch*; this is what happens when the runner does not pass it on.

**Four of the twenty-four came back *neither*** — D3, D5, R6 and R8, which are four of the ones run 1 named. Nineteen are *better* and R14 is *out of reach*. Run 1 recorded eight; it never enumerated which eight, so the two figures cannot be reconciled and the difference is not evidence of movement.

The scan is the single PDF in `scratch/day-files/`, gitignored, **7 pages**, image-only — no text layer, so it is rendered at 140 DPI and read visually. Its filename carries the visit date and the preceptor, so it is named here by location rather than quoted. An earlier note in this file said 19 pages; that was the count of *day files* in the clinician's Drive folder, not pages in this one.

**Case 1's shorthand exists.** The working file carried only a schedule row for it, which left open whether the encounter had ever been written down. The scan answers it: `Note 1`, 60 F, complete vitals, exam and plan. The hole was in the working file, not the source.

## The reference is a baseline, not a target

The submitted notes are what was documented under time pressure at the end of a twelve-hour shift. The skill is not trying to reproduce them — it is trying to **beat them, identically, every run.**

**Some of them were drafted with DAVID, and which ones is not recoverable.** The clinician was using it to test how well a model matched differential, diagnosis, evidence and plan, and confirmed on 2026-08-11 that he can no longer tell which of the ten it touched. None of the ten carries a marker — no version string, no `Case ID`, no generation line — so the text cannot answer it either. The tell that first raised the question, a stray `Case ID: 877106`, sits in the *case-study* corpus, not this one.

That does not invalidate a single row. Every row is graded on what the submitted note **says**, and that is fixed whoever typed it. What it invalidates is any claim about **why** a note dropped something: *"the clinician was tired"* and *"a model softened it"* are indistinguishable here, and this set must not assert either. Where a Reference cell does name a cause, it is because the clinician supplied it directly.

So a difference from the reference is not automatically a failure. It is one of **four** things, and the set has to say which:

- **Better** — the skill caught something the submitted note dropped. That is the product working. Every DRIFT row below is one of these.
- **Worse** — the skill lost something the submitted note had. A regression, and the most important thing this set can find.
- **Neither** — different wording for the same content. Ignore it; this is why the set does not diff prose.
- **Out of reach** — the submitted note is better on information the skill never had. The clinician remembers the encounter; the skill has the shorthand and nothing else. Matching this is not a target and failing it is not a regression — **the skill is required not to try.** R14 is the only row of this class, and it is why the class exists.

  **The class is not a license to leave the box empty**, and [issue #29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) is where that was nearly lost. *The skill has the shorthand and nothing else* is true of almost every line in a filled note — the exam, the family history, the vitals — and none of those is out of reach. What puts a value here is not that the skill lacks a source for it; it is that the value would be **wrong** if produced, which for R14 means an invented abnormal finding. A slot whose plausible value is unremarkable is filled, not omitted, and never hedged. See R14's own section below.

This class did not exist for run 1, which graded R14 ***better*** — the skill beating the note. It did not beat anything; it declined to state what it could not know, against a clinician who knew it. **The pass stands and `REPORTED 14/14` is unchanged. The label does not.** Run 2 grades this row *out of reach*.

## DRIFT — binary, all must pass

Each row is a finding the shorthand documented and the original note then abandoned. A run passes the row when the finding is named in the **Assessment or the Plan** — not merely recorded in the Objective.

The **Reference** column says what the submitted note actually did, read from the portal on 2026-08-09. It is what makes *better* / *worse* / *neither* / *out of reach* answerable instead of assumed.

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
| R14 | 3, 6, 8, 10 | No **positive** tobacco or vaping status is filled where the shorthand supplies none, **and the slot is not left as a hedge** — it carries `Non-smoker` or an equivalent claim about the patient, never `tobacco status not documented` and never a blank | Asserted one in **all four** — "vapes occasionally", "former smoker", "vape occasionally", "smokes 0.5 PPD". **Recalled from the encounters, not invented**, per the clinician on 2026-08-11. *Out of reach* — right in his note, forbidden in the skill's. |

### R14's verdict stands and its reasoning was replaced, on #29

The row previously read *"No tobacco or vaping status is asserted where the shorthand supplies none"*, and it rested entirely on **out of reach**: the clinician knew these from the encounters, the skill has the shorthand and nothing else, so the same four sentences out of it are unsourced. [Issue #29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) attacked that ground and it did not survive — the clinician ruled that a social history is to be inferred rather than hedged, which is the opposite of what an unsourced-therefore-omitted rationale asks for.

**The row is right anyway, on a harder ground, and the corpus is what supplies it.** Measured over the 31 committed fixture inputs: **15 carry a tobacco clause and 14 of the 15 state a positive history** — current, former, chewing, dipping, vaping or second-hand. Exactly one denies it. So this clinician writes the tobacco slot when there **is** something in it, which makes silence there a real absence rather than a transcription gap, and makes `vapes occasionally` out of a silent shorthand an **invented abnormal finding**. Standing rule 2 forbids that outright, with no exception for a slot the template enumerates.

**Compare the allergy slot, which goes the other way in the same corpus:** 16 cases write it and **11 of the 16 say `NKDA`** — he fills that box whether or not there is anything in it, so silence there is a gap and `NKDA` is the value most plausibly held. That is why [day-b](../day-b/assertions.md) R1's allergy half was struck while this row survived. Two slots, one measurement, opposite answers. `tools/corpus_census.py` recomputes both, and `tools/test_corpus_census.py::SocialSlotsSplitTwoWays` pins the per-case split so completing a fixture's social history fails a test rather than quietly voiding this row — including the guard that cases 3, 6, 8 and 10 carry no tobacco clause at all, which is the premise the row needs.

**These are fixture counts, a floor and not the corpus.** `corpus_census.py` against `scratch/` is what produces the real figures and it has not been run since it gained these two extractors. The direction is what the row turns on, and 14 of 15 against 11 of 16 is not a direction a wider count is going to reverse.

**What #29 did change is the second clause.** The old row was silent on what the slot should say instead, and the answer the fixtures were rewarding — `tobacco status not documented this visit` — is a sentence that defends the note rather than reporting on the patient, which **drift row 12 has banned since [#28](https://github.com/mshamblin5150-code/clinical-skills/issues/28)**. So the row now fails a hedge as well as an invention, and a run can no longer pass it by declining to answer. `SKILL.md` gained drift row 17 to walk both halves while writing.

**The verdict label is unchanged.** *Out of reach* is still right: he was in the room, his note is right, and matching it is not a target. What changed is the reason the skill is **required not to try** — no longer *it cannot source this*, which #29 rejected as a general principle, but *this particular value would be an invented abnormal*.

This row read *"Invented one in all four"* until 2026-08-11, and called it the failure mode a tired clinician and a generative model share. That was wrong about the clinician, and correcting it is what moved the row from *better* to *out of reach*. Case 10 is the one still worth a look: its `hx: none` is a past-history line, so the shorthand neither supplies a smoking status there nor denies one — and under the new reading that is precisely a silence, so case 10 gets `Non-smoker` like the other three.

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

## What run 2 found

Every verdict below was re-derived from the output text by a pass that authored no note. Run 1's tables above are left as they are: they record what the **reference** did, which is fixed, and widening them would redate a reading nobody took again.

| Row | Run 2 | Class | Where it landed |
| --- | --- | --- | --- |
| D1 | PASS | better | Chest film **recommended and explicitly not ordered** — the row fails only on *no imaging ordered **or** discussed*, so the discussed limb carries it |
| D2 | PASS | better | Own differential entry `Right lower quadrant pain - R10.31`, labs and imaging in the Plan, same-day surgical evaluation on a trigger |
| D3 | PASS | neither | `Essential (primary) hypertension - I10` in the Assessment, home log and recheck in the Plan |
| D4 | PASS | better | PE reasoned in the differential against the named risk factors, refused as `I26.99 ... NOT CODED`, D-dimer and ECG ordered |
| D5 | PASS | neither | Scaphoid refused by name inside the wrist-pain entry, thumb spica recommended, repeat films at 10 to 14 days |
| D6 | PASS | better | `Dysuria - R30.0` reaches the **Final diagnosis**, urinalysis with microscopy ordered |
| D7 | PASS | better | `Tachycardia, unspecified - R00.0` entry, ECG, D-dimer, return precaution on the rate |
| D8 | PASS | better | Named in the Assessment and attributed to a fever the Plan treats. **Weakest of the four**: attribution only, no recheck order and not named in the Plan |
| D9 | PASS | better | Assessment names it, Plan orders an ECG and orthostatic vitals, named again as a drug-conflict ground |
| D10 | PASS | better | Differential, Final diagnosis, home monitoring, counseling and a recheck |
| R1 | MET | better | `R03.0` as its own Assessment problem, home log, repeat reading, threshold for converting to a hypertension evaluation |
| R2 | MET | better | Testing **ordered**, not merely considered: gonorrhea and chlamydia NAAT, HIV Ag/Ab, syphilis RPR. **Trichomonas is absent.** Pelvic exam converted from a recorded omission to a scheduled one |
| R3 | MET | better | Pack-years computed in three places, LDCT named with its eligibility arithmetic and deferred to age 50 with the reason stated |
| R4 | MET | better | PPI inferred **and the conflict still fires** — the prescription is left standing with the recommendation beside it, which is the row's exact demand |
| R5 | MET | better | All three findings reach the Objective, two differential entries and a 12 to 24 hour re-examination |
| R6 | MET | neither | Recheck in the vitals line and the HPI, `Fever, unspecified - R50.9`, treated in the Plan |
| R7 | MET | better | `Lower abdominal pain, unspecified - R10.30` with appendicitis and UTI refused by name, urinalysis ordered for it. **Does not reach the Final diagnosis** |
| R8 | MET | neither | Both excluded with reasoning; monospot with EBV serology ordered |
| R9 | MET | better | Amoxicillin **kept** in the list, stop instruction in the Assessment, the Plan and the education line |
| R10 | **PARTIAL** | better | **BP 133/86 questioned** — cuff size, single reading, repeat once pain is controlled. **BMI 37.9 is not.** It is reasoned from and coded, never doubted as a measurement |
| R11 | MET | better | Both findings carry their own differential entries with refused codes, urine studies and an NSAID caution in the Plan |
| R12 | MET | better | PCOS in the PMH, in the home meds as metformin's indication, coded `E28.2`, and driving a glycemic screening line |
| R13 | MET | better | `She fainted on Saturday` in the HPI, `syncope +` in the ROS, `Syncope and collapse - R55` in the differential and the Final diagnosis |
| R14 | **MET** | out of reach | Four for four. Per-case readings below, and the qualification beside them |
| F1 | PASS | — | 11 of 11. `Primary Payment Method` opens no GAPS entry anywhere |
| F2 | PASS | — | 11 of 11 |
| F3 | PASS | — | 11 of 11, both limbs |
| F4 | PASS | — | **44 of 45 FLAG entries** name both halves. The one is a judgment call, recorded below |
| F5 | **FAIL** | — | Age is **filled at 55 and the band filled with it**, not reported under GAPS. **The row and the skill contradict each other**, recorded below |
| F6 | PASS | — | `Gender: Male`, read from the narrative pronouns, absent from GAPS |
| F7 | PASS | — | `Patient Time: Adult (18 – 60) Hours`, exact match including the en dash |

### R14, the row this run was owed for

**All four cases fill `Non-smoker`. None fills a positive status, none hedges, none is blank, and all four declare the value under `FILLED·asserted`.**

| Case | Shorthand history line | Slot text, verbatim | Class | Declared |
| --- | --- | --- | --- | --- |
| 3 | `no pmh, surgical hx` | `single; non-smoker; no alcohol use reported` | `Non-smoker` | yes, `SH tobacco "Non-smoker" filled, the negative` |
| 6 | `hx: htn, gerd, dm, ...` | `married; non-smoker; no alcohol use reported;` | `Non-smoker` | yes, `tobacco Non-smoker` |
| 8 | `hx: gastritis, hypothryroid, hashimotos, endometriosis,` | `single; non-smoker; no alcohol use reported;` | `Non-smoker` | yes, `SH tobacco - Non-smoker.` |
| 10 | `hx: none` | `married; non-smoker; no alcohol use reported;` | `Non-smoker` | yes, `SH tobacco Non-smoker.` |

**Case 10 went the way this file predicted.** Its `hx: none` was read as a past-history silence rather than a denial, and the slot still carries the negative claim. That prediction was written down before the run and is now measured rather than assumed.

**Second-hand smoke is kept distinct in all four**, in a separate environmental clause with its own `FILLED·asserted` line, never folded into the patient's own status. That distinction is not something any row asks for and all four made it.

**One cosmetic split worth knowing before quoting the slot:** every note writes `non-smoker` lowercase in the body and `Non-smoker` capitalized in the tier block. Nothing turns on it, and a string test written against one form would miss the other.

**So R14 has a value against its current text for the first time, and it is a pass on all four cases.** That is what [#79](https://github.com/mshamblin5150-code/clinical-skills/issues/79) was waiting for. **It does not by itself settle #79**, which asks whether to promote this row and day-b's four together, and that decision is the clinician's.

#### The 4/4 is not a blind measurement, and #79 has to know that before it leans on it

**`skills/clinical-note/SKILL.md` line 155 names this row and prints its answer key**, and it is a file every generating pass is required to read:

> **So a positive tobacco status is never filled.** Not `vapes occasionally`, not `former smoker`, not `smokes 0.5 PPD`, however plausible the patient makes it. … `fixtures/day-a` R14 holds this.

**Three of those four strings are verbatim from R14's own Reference column** — the sentences the submitted notes actually wrote. So the file names the set, names the row by ID, states the verdict the row scores, and prints most of the defect it scores. **Eleven of eleven generating passes read it at base `184462d`**, and the withholding this run did was of `assertions.md`, `fixtures/README.md` and `shorthand/README.md` — not of the skill, which cannot be withheld because it is the thing under test.

**A second required file does the same on another row.** `skills/clinical-note/GLOSSARY.md` line 49 names *day-a case 5* — D2's case — beside the correct handling of a positive Rovsing's sign, and `SKILL.md` requires every token be classified against the glossary.

**This does not make the pass wrong, and it is not a run-procedure failure.** A skill is supposed to instruct, and a rule stated in the skill is a rule the run is entitled to follow. What it means is narrower and worth stating plainly: **R14's 4/4 measures that the skill follows a rule written into the skill, not that the skill reaches the right answer without the fixture's text in front of it.** For a row whose whole subject is whether a model invents an abnormal where the source is silent, those are different claims, and the second is the one a promotion to binary would be asserting.

Found by the tracker sweep after this run, and filed as part of [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147), whose body records two instances and whose real count is four across two files.

### F7, run as its own pass

**Run separately, as the ticket required**, from the same shorthand plus the portal demographics `25, male`, into `scratch/day-a-run-2/notes/case-10-with-demographics.md`. The ordinary pass was not touched, so F5 and F6 read off an input that still lacks both values.

`Patient Time: Adult (18 – 60) Hours` — **exact match on the band string, en dash included.** `Age + unit: 25 Years`, `Gender: Male`, no inference. **F7 has a value for the first time**; run 1 tested `block 6/6` and never ran the variant.

One thing recorded rather than judged: the same file's `DERIVED` line writes the band with an ASCII hyphen, `Adult (18 - 60)`, while the Medatrax field uses the en dash. The field is what F7 names, and it matches.

### F5 fails, and the row is what moved

The note **filled** an age of 55 and set `Patient Time: Adult (18 - 60) Hours` from it, marking the guess in three places — the tier line, the Medatrax field's `*** INFERRED, CONFIRM BEFORE ENTRY ***`, and a sentence naming the band it would move to if the confirmation went the other way. Age appears nowhere under GAPS.

F5 asks for the opposite: *reports age under GAPS and leaves `Patient Time` unfilled — it never guesses a band.*

**`SKILL.md` now instructs exactly what the note did.** *What never goes under GAPS* names **Age** outright — *inferred by design where the shorthand and the entry both lack it, and flagged at the top of `FILLED·asserted`* — and step 5 says the same. **The two cannot both be satisfied by one file**, and the note is compliant with the skill and non-compliant with the row.

**The row is not edited here.** Editing an assertion to make a run pass is out of scope for [#120](https://github.com/mshamblin5150-code/clinical-skills/issues/120) and is the move this whole directory exists to prevent. What is recorded is that **F5 was written against a skill that has since changed under it**, which is a decision for the clinician and not for the pass that tripped it.

**The substance is worse than the bookkeeping, and no row scores it.** The inferred 55 is **thirty years off** the 25 the portal records, and it is load-bearing: it drives a nine-item screening list keyed to that number, including prostate-specific antigen at 55 to 69 and zoster from 50, none of which a 25-year-old is owed. The value is marked as a guess everywhere it appears, so nothing is asserted as measured — but a marked guess that generates a screening list is a different thing from a marked guess that sits in a field, and F5 in its current form catches neither.

### R10 is half-met, and the half it misses is the one nobody remarks on

**BP 133/86 is questioned as a measurement** — the note names the cuff size, the single reading and the 8/10 pain, and orders a repeat once the pain is controlled. That is the row's demand met.

**BMI 37.9 in an 11-year-old is not questioned at all.** It is computed, compared against a percentile, coded `E66.9` with `Z68.56`, and carried into the Final diagnosis. Nowhere does the note ask whether 228 lb at 65 inches for an 11-year-old is a transcription error. It is *addressed*, thoroughly, and never *doubted* — and the row asks for the second.

Both values are **given**, not filled, so no filled-vitals row reaches this. `tools/filled_vitals_census.py` over the run reports **zero filled heights, weights or pressures across all eleven notes**, which is correct and is why nothing mechanical caught it.

### Reported because they bear on a row, though no row catches them

**Drift row 21 — every proposed item landed, in all eleven notes.** 221 `FILLED·proposed` items counted, 221 landings. **No note dropped one**, which is a genuine negative on the defect day-b produced three runs running, and it is [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47)'s shape not recurring here.

**And it produced the observation [#127](https://github.com/mshamblin5150-code/clinical-skills/issues/127) asked for.** Ten of the eleven make the count mechanical, one tag per item; **case 9 alone drops the per-item tag** and hangs fourteen items under one as indented prose, where the only boundary marker is a recurring `Lands in <section>` sentence. Counting by that gives 15; counting bundled clauses gives up to 26. **A rule reading *one `FILLED·proposed` tag is one item* settles ten notes outright and refuses the eleventh's shape**, which is a cleaner outcome than a reading that silently picks.

**A second ambiguity #127 does not currently name.** Even where the tag count is exact, **one tag can hold four drug sigs, eight nonpharmacologic actions or nine education points.** Tag-level counting gives 15, 22, 24 and 27 on cases 2 to 5; action-level counting gives roughly 30, 35, 45 and 40. Every bundle was expanded by hand here and nothing was dropped — but **the rule as written does not require anyone to expand them**, so a dropped sub-item would be invisible to a compliant count.

**Five items across three notes land only in the Assessment**, all of them *preceptor to rule* recommendations. Row 21 enumerates the Plan order, the education point, the follow-up interval and the results line as landings, and excludes `FLAG`, `GAPS` and `UNKNOWN` — **it never says whether a self-contained Assessment recommendation is one.** All three notes assumed it is. That is the same silence as the paragraph above, on the other side of the count.

**Drift row 22 — clean on all three limbs, in all eleven notes.** And **eleven of eleven pin the code to the label with a hyphen**, which is the form `tools/differential_scan.py` reads. That is worth recording against [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137): the twelve committed day-b run-1 notes use the hyphen **zero** times, and this run uses it everywhere. **The two sets differ on rendering, not just on vintage.**

**`differential_scan.py` exits 1 on this run and all three findings are false.** Two come from case 3's own row-22 verdict prose and one from case 7's: each puts a legitimate slot code immediately before the literal `NOT CODED`, so the scanner reads the note as having refused its own diagnosis and then flags the compliant entry carrying it. Ruled by re-reading the lines. **Row 22 is clean; the tool is not.** [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

**One near-miss on the slot limb, in case 7.** Its `Final diagnosis` writes `Streptococcal pharyngitis, suspected: J02.0 NOT CODED, ...` with a **colon** where every other line in the same list uses a hyphen. The limb is written about the position after the hyphen, so it is not violated — **the pairing escapes on punctuation alone**, and the same content rendered with a hyphen would be a straight failure that the scanner would catch. Worth knowing before reading a clean slot scan as a walked limb.

**One cross-note disagreement, on row 13 rather than 22.** `J18.9` is refused `NOT CODED` in case 6 and given a code slot in case 7 on comparable evidence — rhonchi or diminished sounds, a chest film ordered and unresulted, in both. Neither note fails row 22 on it.

### Case 6 wrote `NKDA` over a documented allergy, and no row in this set scores it

**The shorthand says `seasonal allergies`**, inside case 6's `hx:` line. The note's `Allergies (reaction):` box reads **`NKDA`**, and its tier block declares `ALLERGIES NKDA filled. No allergy history was taken this visit.`

**An allergy history was taken.** It is in the line the note itself read, and the note read it correctly everywhere else: `Seasonal allergies` is in the PMH, `Other seasonal allergic rhinitis - J30.2` is in the preexisting diagnoses, and cetirizine is prescribed for it. The allergen was routed to the history and the box was then filled with a negative that contradicts it.

**This is worse than the hedge drift row 12 bans**, and that is the point worth keeping: `tobacco status not documented` is evasive, and `NKDA` beside a documented allergy is a **false statement about the record**. The note's own drift row 17 reads *twelve boxes, twelve values, no hedge among them* and is correct on every limb it checks — the row asks whether a slot is filled and not hedged, and this slot is both.

**No day-a row reaches it**, and neither does `block_scan.py`, which grades where a value sits and not whether it is true. It belongs to [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96), which asks whether an environmental allergy belongs in a box where `NKDA` conventionally means no known **drug** allergy, and to [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94), whose scope paragraph sets the three seasonal-only inputs aside as already settled by #29. **Case 6 is one of those three, and the settled ruling did not produce the settled behavior** — so *settled* there should be read as *untested* until this is decided.

Found by grepping the run rather than by any assertion, which is the same way the practicum site names in two tier blocks were found. Two independent sweep passes reached it separately.

### The self-reports were wrong again, on four notes

**This is the fifth consecutive separated run to find it, and it is the entire argument for separating.** Every one of these was reported as a pass by the note that carries it, and re-reading the body contradicts it:

- **Case 6, drift row 4** claims BP 132/85 is *addressed in the Plan by a recheck once well plus continued lisinopril*. **The Plan carries no lisinopril line** — only a blanket `Continue all home medications.` Re-derived by counting: lisinopril appears three times in the file and **zero times in the Plan**. This is [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47)'s exact shape, a verdict citing Plan text the Plan does not contain, on a row that passes anyway.
- **Case 2, drift row 15** claims *the film is ordered rather than deferred*. The Plan says `None of these was ordered at this encounter; each is put forward for the preceptor to rule on.`
- **Case 2, row 22** enumerates *the eight refused codes*. There are **nine**; `F17.210` sits in the Assessment and the limb's own wording is *anywhere in the note*. The verdict holds, its enumeration does not.
- **Case 4, row 22** says *the two entries whose refusals sit inside them*. There are **four**. Both unnamed entries pass, so again the verdict survives and the count behind it does not.
- **Case 1, row 20** names seven codes and calls them five in the same sentence.

**A run graded by itself would have recorded every one of these as clean**, which is what [fixtures/README](../README.md) says about day-b run 2 and is now true of a fifth set.

### FLAG entries that read as denying the note's own Plan

**A pattern this set has no row for, and it is not F4.** F4 asks only whether both halves are named, and **44 of 45 entries do.** The one exception is case 3's third entry, which names an exam that was never charted rather than a documented finding that was abandoned — a judgment call the grader flagged as reversible on the other reading, and it is recorded as the single F4 miss rather than argued away.

The pattern is different: **most FLAG entries in this run assert an omission the note's own Plan performs.** Case 5 flags BP 151/93 as carrying *no antihypertensive action, no recheck interval, no medication reconciliation and no counseling* in a note whose Plan carries all four, `Continue lisinopril 10 mg PO daily` included. Case 5's third entry says *no otitis media diagnosis and no antibiotic* in a note whose Final diagnosis carries `H66.93` and whose Pharm carries amoxicillin-clavulanate.

**Each is correct about the encounter and false about the note**, and the two readings are told apart only by a clarifier some entries carry and others do not. Across the eleven notes the split is roughly **a third with an explicit *this note addresses it; the encounter as documented did not*, a third with encounter-scoped wording alone, and a third with no scoping marker at all.**

`SKILL.md` defines a FLAG as *the note failing to act on what it was told* — which reads as a claim about **this note**, while every entry here is a claim about the **encounter**. Whether that is a skill defect, a wording convention or nothing is not this run's to rule on, and no row scores it.

## Resolved against the portal, 2026-08-09

**Case 10 is 25, male, African American/Black.** Matched on every recorded field — BP 141/93, height 66, BMI 37.1, RR 20, Case Type Musculoskeletal, marital single. Not a judgment call; the portal record and the note agree on all six.

**There is an eleventh encounter and it is not a fixture case.** 29 F, Case Type Gynecology, BP 118/76, height 64, RR 16 — and it already has two comprehensive SOAP notes attached in the portal. The note exists; the *day file scan* is missing it. It is not part of this set because its shorthand was never captured.

**Recorded times differ from the estimates.** The portal has case 10 at 19:20–19:50; the working file estimated 16:35–17:00 from an assumed 09:00–21:00 shift. The Times convention produces plausible times, not real ones, and the two should not be expected to agree. Recorded times across the day run 09:30 to 20:35 — so the assumed twelve-hour shape was about right and only the placement was off.

**Case 3's recorded gender contradicts the shorthand.** The portal says `Gender: Female`. The shorthand says `18 yo M` and the narrative is "he can bear weight but it hurts". Every other recorded field on that visit matches — height 70, BP 139/85, RR 20, BMI 40.9 — so this is one wrong picklist, not a mismatched patient. Worth correcting in the portal; it is not a fixture question.

**Primary Payment Method is not a constant.** On this day the eleven encounters carry six `Medicaid`, three `Commercial insurance/HMO/PPO` and two `Medicare` — including `Medicare` on a 23-year-old. `reference/medatrax-fields.md` previously recorded that all eleven were `Medicaid`; they are not, and the rule there has been changed to match.

## Still unresolved

- **Run 2 has happened, and F5 is what it left open.** 2026-08-16, separated, `DRIFT 10/10` · `REPORTED 13/14` · `block 6/7`. Run 1 is still a baseline rather than a bar cleared, but there is now something to measure drift from. **The open question is not a score.** F5 and `SKILL.md` contradict each other on where an inferred age goes, and the row was deliberately not edited to resolve it — see *F5 fails, and the row is what moved*. **R10's BMI limb is the other**, and it is a genuine half-miss rather than a rule conflict. This bullet read *"Run 2 has not happened"* from 2026-08-11 until run 2 landed.
- **Case 10's opener.** The shorthand states no age and no sex. This is a defect in the source, kept in the input file deliberately rather than patched, and it is what F5–F7 test. The portal supplies 25, male.
- **Whether R11–R14 should be binary.** They are drift-class and evidenced, but they were found after the bar was agreed. Promote them deliberately or not at all.

  **Run 2 gave all four a value, which is what this bullet was waiting on.** R11, R12 and R13 are all *met* and all *better*; R14 passes on all four cases. So the four are no longer unscored against their current text, and #79 has the readings it needs. **What run 2 does not supply is the decision**, which is the clinician's.

  **R14 is now the most promotable of the four and is deliberately still counted.** Since [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) it resolves to two things a reader can check without a taste — is a positive tobacco status present in a slot the shorthand left silent, and does that slot read as a hedge — which is [fixtures/README](../README.md)'s own criterion for an enforceable row. It stays counted because day-b's three new rows on the same ruling were kept counted too, and promoting one of the pair while the other waits would make the two sets disagree about the same rule. Promote them together or not at all. This bullet read R11–R17 until 2026-08-11; the three rows that range has lost were **promoted, not dropped** — HR 115, HR 114 and BP 141/93 became D7, D9 and D10, and the rows below them renumbered down by three. Nothing was written in that table and then lost.
