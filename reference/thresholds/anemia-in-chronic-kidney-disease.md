# Anemia in chronic kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2026 | KDIGO | KDIGO/KDIGO-2026-Anemia-in-CKD-Guideline | guideline | 2026 guideline | 2026-01 | https://doi.org/10.1016/j.kint.2025.06.006 | stated | bound |

## Scope

**Read:** all 99 source pages: cover, contents, reference keys, nomenclature,
conversion tables, notice, foreword, membership, abstract, introduction, the complete
summary of recommendations and practice points, all four clinical chapters and every
table and figure, guideline-development methods, biographic and disclosure material,
acknowledgments, references, and all five population-based appendix algorithms. The
rows retain numbers that define, classify, dose, time, monitor, refer, start, stop, or
otherwise change an action for a patient. Prevalence estimates, effect estimates,
trial-only protocols, study inclusion criteria, publication years, and bibliography
numbers were read but do not produce rows.

Table 10 on p60 was retained because the guideline directs readers evaluating ESA
hyporesponsiveness to its numeric definitions; each organization's method is named
in the quantity key. Pages 40, 41, 47, 55, 58, and 60 were also rendered and read to
resolve table columns, microgram units, comparison operators, and the reaction
algorithm.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| front matter, contents, and reference keys | 1-8 | read 2026-08-31; blind 2026-08-31 |
| CKD definition, classification, and conversion tables | 9-10 | yes |
| notice, foreword, membership, abstract, and introduction | 11-17 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendation statements and practice points | 18-28 | yes |
| chapter 1: diagnosis and evaluation | 29-36 | yes |
| chapter 2: iron therapy | 37-48 | yes |
| chapter 3: ESAs, HIF-PHIs, and other agents | 49-62 | yes |
| chapter 4: red blood cell transfusions | 63-69 | yes |
| guideline-development methods | 70-76 | read 2026-08-31; blind 2026-08-31 |
| biographic information, disclosures, and acknowledgments | 77-86 | read 2026-08-31; blind 2026-08-31 |
| references | 87-94 | exempt: citation list has no clinical prose |
| population-based management algorithms | 95-99 | yes |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adult-men-ckd | males age >=15 years with CKD |
| adult-women-ckd | females age >=15 years with CKD |
| people-ckd | people with CKD |
| ckd-g1 | CKD G1 |
| ckd-g2 | CKD G2 |
| ckd-g3a | CKD G3a |
| ckd-g3b | CKD G3b |
| ckd-a1 | CKD A1 |
| ckd-a2 | CKD A2 |
| ckd-a3 | CKD A3 |
| children-0.5-4-ckd | children 0.5-4 years with CKD |
| children-5-11-ckd | children 5-11 years with CKD |
| children-12-14-ckd | children 12-14 years with CKD |
| ckd-g3 | CKD G3 |
| ckd-g4 | CKD G4 |
| ckd-g5-g5d | CKD G5 or G5D |
| anemia-ckd | people with anemia and CKD |
| anemia-ckd-g5hd | people with anemia and CKD G5 receiving hemodialysis |
| anemia-ckd-not-dialysis-g5pd | people with anemia and CKD not receiving dialysis or CKD G5 receiving peritoneal dialysis |
| ckd-not-dialysis | people with CKD not receiving dialysis |
| ckd-g5d | people with CKD G5D |
| ckd-g5pd | people with CKD G5PD |
| ckd-g5hd | people with CKD G5HD |
| ckd-iron-treated | people with CKD treated with iron |
| ckd-oral-iron | people with CKD treated with oral iron |
| ckd-iv-iron | people with CKD treated with i.v. iron |
| ckd-iron-after-blood-loss | people with CKD treated with iron after accidental blood loss |
| ckd-profound-iron-no-anemia | people with CKD and profound iron deficiency but no anemia |
| iv-iron-nonspecific-reaction | people with nonspecific reactions to i.v. iron |
| iv-iron-mild-reaction | people with mild infusion reactions to i.v. iron |
| iv-iron-moderate-reaction | people with moderate reactions to i.v. iron |
| iv-iron-severe-reaction | people with severe reactions to i.v. iron |
| adults-children-anemia-ckd-g5d | adults and children with anemia and CKD G5D |
| adults-children-anemia-ckd-not-dialysis | adults and children with anemia and CKD not receiving dialysis |
| adults-anemia-ckd-esa | adults with anemia and CKD treated with ESAs |
| children-anemia-ckd-esa | children with anemia and CKD treated with ESAs |
| anemia-ckd-esa | people with anemia and CKD treated with ESAs |
| anemia-ckd-hif-phi | people with anemia and CKD treated with HIF-PHIs |
| anemia-ckd-roxadustat | people with anemia and CKD treated with roxadustat |
| anemia-ckd-esa-hyporesponsive | people with anemia, CKD, and ESA hyporesponsiveness |
| hif-phi-high-risk | people with anemia and CKD at increased risk for adverse events with HIF-PHIs |
| esa-hyporesponsiveness-reference | people being evaluated for ESA hyporesponsiveness |
| stable-adult-inpatients | hemodynamically stable adult inpatients |
| adult-cardiac-surgery | adults undergoing cardiac surgery |
| adult-orthopedic-or-cvd | adults undergoing orthopedic surgery or with clinically significant cardiovascular disease |
| chronically-transfused-ckd | people with CKD receiving numerous RBC transfusions for chronic anemia |
| anemia-ckd-g5hd-algorithm | people with anemia and CKD G5 receiving hemodialysis |
| anemia-ckd-nondialysis-algorithm | people with anemia and CKD not receiving dialysis |
| anemia-ckd-g5pd-algorithm | people with anemia and CKD G5 receiving peritoneal dialysis |
| anemia-ckd-ktr-algorithm | kidney transplant recipients with anemia and CKD |
| children-anemia-ckd-algorithm | children with anemia and CKD |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-minimum-duration | minimum duration defining CKD |
| ckd-gfr-category | GFR category threshold |
| ckd-albuminuria-category | albuminuria category threshold |
| adult-male-anemia-definition | hemoglobin threshold for anemia in men |
| adult-female-anemia-definition | hemoglobin threshold for anemia in women |
| pediatric-anemia-definition-0.5-4 | hemoglobin threshold for anemia at 0.5-4 years |
| pediatric-anemia-definition-5-11 | hemoglobin threshold for anemia at 5-11 years |
| pediatric-anemia-definition-12-14 | hemoglobin threshold for anemia at 12-14 years |
| systemic-iron-deficiency-nondialysis | systemic iron deficiency in CKD not receiving dialysis |
| systemic-iron-deficiency-g5hd | systemic iron deficiency in CKD G5HD |
| iron-restricted-erythropoiesis | iron-restricted erythropoiesis |
| anemia-testing-g3 | suggested testing frequency for anemia in CKD G3 |
| anemia-testing-g4 | suggested testing frequency for anemia in CKD G4 |
| anemia-testing-g5-g5d | suggested testing frequency for anemia in CKD G5 or G5D |
| blood-loss-evaluation-ferritin | ferritin threshold for clinical evaluation for blood loss |
| blood-loss-evaluation-mcv | mean corpuscular volume threshold for clinical evaluation for blood loss |
| selected-severe-iron-deficiency | ferritin example for severe iron deficiency in select cases |
| g5hd-iron-initiation-summary-ferritin | summary ferritin threshold for initiating iron therapy |
| g5hd-iron-initiation | ferritin and TSAT thresholds for initiating iron therapy |
| nondialysis-pd-iron-initiation-low-ferritin | low-ferritin iron-initiation thresholds |
| nondialysis-pd-iron-initiation-mid-ferritin | midrange-ferritin iron-initiation thresholds |
| ferric-citrate-starting-dose | ferric citrate starting dose |
| ferric-maltol-starting-dose | ferric maltol starting dose |
| ferrous-sulfate-starting-dose | ferrous sulfate starting dose |
| ferrous-fumarate-starting-dose | ferrous fumarate starting dose |
| ferrous-gluconate-starting-dose | ferrous gluconate starting dose |
| liposomal-iron-starting-dose | liposomal iron starting dose |
| heme-iron-polypeptide-starting-dose | heme iron polypeptide starting dose |
| iron-dextran-maximum-and-time | low-molecular-weight iron dextran maximum single dose and administration time |
| iron-dextran-concentration | low-molecular-weight iron dextran concentration |
| iron-sucrose-concentration | iron sucrose concentration |
| ferric-gluconate-concentration | ferric gluconate concentration |
| ferric-carboxymaltose-concentration | ferric carboxymaltose concentration |
| ferric-derisomaltose-concentration | ferric derisomaltose concentration |
| ferumoxytol-concentration | ferumoxytol concentration |
| iron-sucrose-ckd-regimen | iron sucrose regimen for CKD not receiving hemodialysis |
| iron-sucrose-pd-regimen | iron sucrose regimen for peritoneal dialysis |
| ferric-gluconate-regimen | ferric gluconate regimen |
| ferric-carboxymaltose-regimen | ferric carboxymaltose regimen |
| ferric-derisomaltose-regimen | ferric derisomaltose/iron isomaltoside regimen |
| ferumoxytol-regimen | ferumoxytol regimen |
| routine-iron-withhold-ferritin | ferritin threshold for withholding routine iron |
| routine-iron-withhold-tsat | TSAT threshold for withholding routine iron |
| iron-monitoring-nondialysis-pd | hemoglobin, ferritin, and TSAT testing frequency |
| iron-monitoring-g5hd | hemoglobin, ferritin, and TSAT testing frequency |
| post-iv-iron-tsat-delay | delay before TSAT testing after i.v. iron |
| post-blood-loss-iron-retest | iron-status retesting after accidental blood loss |
| oral-to-iv-switch | time to switch from oral to i.v. iron after insufficient effect |
| oral-elemental-iron-daily | typical elemental iron daily dose |
| oral-iron-frequency-reduction | oral iron dosing reduction for gastrointestinal side effects |
| iv-iron-sucrose-narrative-maximum | i.v. iron sucrose maximum per administration |
| iv-iron-gluconate-narrative-maximum | i.v. iron gluconate maximum per administration |
| nonspecific-reaction-observation | observation after stopping infusion for a nonspecific reaction |
| post-infusion-routine-observation | routine observation after an i.v. iron infusion |
| reaction-restart-rate | restart rate after an i.v. iron reaction |
| mild-reaction-retrial-time | retrial time after treatment of a mild infusion reaction |
| moderate-reaction-hydrocortisone | hydrocortisone dose for a moderate reaction |
| severe-reaction-oxygen | oxygen for a severe i.v. iron reaction |
| severe-reaction-epinephrine | intramuscular epinephrine dose and repeat interval |
| severe-reaction-crystalloid | crystalloid volume loading for severe anaphylaxis |
| profound-iron-deficiency-no-anemia | profound iron deficiency thresholds without anemia |
| hif-phi-cancer-remission-window | cancer-remission window for HIF-PHI avoidance consideration |
| hif-phi-us-dialysis-eligibility | U.S. dialysis-duration eligibility for HIF-PHIs |
| esa-initiation-hb-measurements | hemoglobin measurements and trend used for ESA initiation |
| esa-initiation-g5d | hemoglobin concentration for ESA initiation in CKD G5D |
| esa-initiation-nondialysis | hemoglobin concentration for ESA initiation in CKD not receiving dialysis |
| adult-esa-maintenance-target | upper hemoglobin target for ESA maintenance |
| child-esa-maintenance-consideration | adult upper target considered during pediatric individualization |
| epoetin-nondialysis-initial | epoetin alfa and beta initial dose in CKD not receiving dialysis |
| epoetin-g5d-initial | epoetin alfa and beta initial dose in CKD G5D |
| epoetin-g5d-adjustment | epoetin alfa and beta dose adjustment in CKD G5D |
| darbepoetin-nondialysis-initial | darbepoetin initial dose in CKD not receiving dialysis |
| darbepoetin-g5d-initial | darbepoetin initial dose in CKD G5D |
| darbepoetin-g5d-adjustment | darbepoetin dose adjustment in CKD G5D |
| methyl-peg-epoetin-nondialysis-initial | methyl polyethylene glycol-epoetin beta initial dose in CKD not receiving dialysis |
| methyl-peg-epoetin-g5d-initial | methyl polyethylene glycol-epoetin beta initial dose in CKD G5D |
| methyl-peg-epoetin-g5d-adjustment | methyl polyethylene glycol-epoetin beta dose adjustment in CKD G5D |
| epoetin-convenient-dose | convenient epoetin dose |
| darbepoetin-convenient-dose | convenient darbepoetin dose |
| epoetin-darbepoetin-adjustment-frequency | epoetin and darbepoetin dose-adjustment frequency |
| methyl-peg-epoetin-adjustment-frequency | methyl polyethylene glycol-epoetin beta dose-adjustment frequency |
| esa-initial-monthly-rise | intended initial monthly hemoglobin rise |
| cancer-chemotherapy-esa-threshold | hemoglobin threshold for ESA consideration with cancer chemotherapy |
| esa-adjustment-frequency-and-exception | ESA dose-adjustment frequency and rapid-rise exception |
| esa-rise-to-avoid | hemoglobin rise to avoid during ESA initiation |
| esa-initiation-monitoring | hemoglobin monitoring after ESA initiation or dose change |
| esa-maintenance-monitoring | hemoglobin monitoring during ESA maintenance |
| daprodustat-dose | daprodustat recommended initiation and maximum dose |
| desidustat-dose | desidustat recommended initiation and maximum dose |
| enarodustat-dose-nondialysis-pd | enarodustat dose in CKD not receiving dialysis and CKD G5PD |
| enarodustat-dose-hd | enarodustat dose in CKD G5HD |
| molidustat-dose-nondialysis | molidustat dose in CKD not receiving dialysis |
| molidustat-dose-g5d | molidustat dose in CKD G5D |
| roxadustat-dose-naive | roxadustat dose for ESA-naive patients |
| roxadustat-dose-switch | roxadustat dose when switching from ESA |
| vadadustat-dose | vadadustat recommended initiation and maximum dose |
| hif-phi-hb-monitoring | hemoglobin monitoring with HIF-PHIs |
| roxadustat-thyroid-monitoring | thyroid-function monitoring with roxadustat |
| hif-phi-nonresponse-stop | HIF-PHI discontinuation after insufficient response |
| chronic-esa-hyporesponsiveness | chronic ESA hyporesponsiveness duration |
| nkf-iv-epo-hyporesponsiveness | NKF-KDOQI i.v. EPO hyporesponsiveness definition |
| nkf-sc-epo-hyporesponsiveness | NKF-KDOQI subcutaneous EPO hyporesponsiveness definition |
| ebpg-hyporesponsiveness | revised EBPG hyporesponsiveness definition |
| kdigo-initial-hyporesponsiveness | KDIGO 2012 initial ESA hyporesponsiveness definition |
| kdigo-initial-escalation-limit | KDIGO 2012 initial hyporesponsiveness escalation limit |
| kdigo-acquired-hyporesponsiveness | KDIGO 2012 acquired ESA hyporesponsiveness definition |
| kdigo-acquired-escalation-limit | KDIGO 2012 acquired hyporesponsiveness escalation limit |
| riscavid-resistance-index | RISCAVID ESA resistance index threshold |
| uk-iv-epo-hyporesponsiveness | UK Kidney Association i.v. EPO hyporesponsiveness definition |
| uk-sc-epo-hyporesponsiveness | UK Kidney Association subcutaneous EPO hyporesponsiveness definition |
| uk-darbepoetin-hyporesponsiveness | UK Kidney Association darbepoetin hyporesponsiveness definition |
| jsdt-hd-hyporesponsiveness | Japanese Society for Dialysis Therapy HD hyporesponsiveness definition |
| jsdt-pd-hyporesponsiveness | Japanese Society for Dialysis Therapy PD hyporesponsiveness definition |
| jsdt-nondialysis-hyporesponsiveness | Japanese Society for Dialysis Therapy nondialysis hyporesponsiveness definition |
| transfusional-iron-overload | transfused iron amount associated with organ damage |
| rbc-unit-iron | iron delivered by one RBC unit |
| stable-inpatient-transfusion | restrictive RBC transfusion threshold for stable adult inpatients |
| cardiac-surgery-transfusion | restrictive RBC transfusion threshold for cardiac surgery |
| orthopedic-cvd-transfusion | restrictive RBC transfusion threshold for orthopedic surgery or cardiovascular disease |
| g5hd-algorithm-esa-start | ESA initiation threshold in the CKD G5HD algorithm |
| g5hd-algorithm-monthly-monitoring | monthly tests in the CKD G5HD algorithm |
| nondialysis-algorithm-esa-start | ESA initiation threshold in the nondialysis algorithm |
| g5pd-algorithm-esa-start | ESA initiation threshold in the CKD G5PD algorithm |
| ktr-algorithm-esa-start | ESA initiation threshold in the kidney-transplant algorithm |
| pediatric-algorithm-severe-iron | severe iron deficiency threshold in the pediatric algorithm |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-minimum-duration | people-ckd | abnormalities of kidney structure or function present for >=3 months | RENDERED: CKD is defined as abnormalities of kidney structure or function, present for a minimum of 3 months | kdigo-2026 | p9 | p9/narrative/ckd-definition | narrative |
| ckd-gfr-category | ckd-g1 | GFR >=90 ml/min/1.73 m2 | RENDERED: GFR category G1: ≥90 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g1 | narrative |
| ckd-gfr-category | ckd-g2 | GFR 60-89 ml/min/1.73 m2 | RENDERED: GFR category G2: 60–89 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g2 | narrative |
| ckd-gfr-category | ckd-g3a | GFR 45-59 ml/min/1.73 m2 | RENDERED: GFR category G3a: 45–59 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g3a | narrative |
| ckd-gfr-category | ckd-g3b | GFR 30-44 ml/min/1.73 m2 | RENDERED: GFR category G3b: 30–44 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g3b | narrative |
| ckd-gfr-category | ckd-g4 | GFR 15-29 ml/min/1.73 m2 | RENDERED: GFR category G4: 15–29 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g4 | narrative |
| ckd-gfr-category | ckd-g5-g5d | GFR <15 ml/min/1.73 m2 | RENDERED: GFR category G5: <15 ml/min/1.73 m2 | kdigo-2026 | p9 | p9/narrative/gfr-g5 | narrative |
| ckd-albuminuria-category | ckd-a1 | AER <30 mg/24 h and ACR <30 mg/g (<3 mg/mmol) | RENDERED: Albuminuria category A1: AER <30 mg/24 h and ACR <30 mg/g (<3 mg/mmol) | kdigo-2026 | p9 | p9/narrative/albuminuria-a1 | narrative |
| ckd-albuminuria-category | ckd-a2 | AER 30-300 mg/24 h and ACR 30-300 mg/g (3-30 mg/mmol) | RENDERED: Albuminuria category A2: AER 30–300 mg/24 h and ACR 30–300 mg/g (3–30 mg/mmol) | kdigo-2026 | p9 | p9/narrative/albuminuria-a2 | narrative |
| ckd-albuminuria-category | ckd-a3 | AER >300 mg/24 h and ACR >300 mg/g (>30 mg/mmol) | RENDERED: Albuminuria category A3: AER >300 mg/24 h and ACR >300 mg/g (>30 mg/mmol) | kdigo-2026 | p9 | p9/narrative/albuminuria-a3 | narrative |
| adult-male-anemia-definition | adult-men-ckd | Hb <13 g/dl (<130 g/l) | RENDERED: hemoglobin (Hb) <13 g/dl (<130 g/l) for males age ≥15 years | kdigo-2026 | p30 | p30/narrative/adult-anemia-definition | narrative |
| adult-female-anemia-definition | adult-women-ckd | Hb <12 g/dl (<120 g/l) | RENDERED: hemoglobin (Hb) <12 g/dl (<120 g/l) for females age ≥15 years | kdigo-2026 | p30 | p30/narrative/adult-anemia-definition-female | narrative |
| pediatric-anemia-definition-0.5-4 | children-0.5-4-ckd | Hb <11 g/dl (<110 g/l) | RENDERED: for 0.5–4 years, Hb <11 g/dl (<110 g/l) | kdigo-2026 | p30 | p30/narrative/pediatric-anemia-0.5-4 | narrative |
| pediatric-anemia-definition-5-11 | children-5-11-ckd | Hb <11.5 g/dl (<115 g/l) | RENDERED: for 5–11 years, Hb <11.5 g/dl (<115 g/l) | kdigo-2026 | p30 | p30/narrative/pediatric-anemia-5-11 | narrative |
| pediatric-anemia-definition-12-14 | children-12-14-ckd | Hb <12 g/dl (<120 g/l) | for 12-14 years, Hb <12 g/dl (<120 g/l) | kdigo-2026 | p30 | p30/narrative/pediatric-anemia-12-14 | narrative |
| systemic-iron-deficiency-nondialysis | ckd-not-dialysis | TSAT <20% and ferritin <100 ng/ml (<100 µg/l) | TSAT <20% and ferritin <100 ng/ml | kdigo-2026 | p32 | p32/narrative/systemic-iron-deficiency-nondialysis | narrative |
| systemic-iron-deficiency-g5hd | ckd-g5hd | TSAT <20% and ferritin <200 ng/ml (<200 µg/l) | RENDERED: CKD G5HD: ferritin <200 ng/ml (<200 µg/l) and TSAT <20% | kdigo-2026 | p32 | p32/narrative/systemic-iron-deficiency-g5hd | narrative |
| iron-restricted-erythropoiesis | anemia-ckd | TSAT <20% with ferritin >100-200 ng/ml (>100-200 µg/l) | RENDERED: ferritin >100–200 ng/ml (>100–200 µg/l) with TSAT <20% | kdigo-2026 | p32 | p32/narrative/iron-restricted-erythropoiesis | narrative |
| anemia-testing-g3 | ckd-g3 | at least annually | RENDERED: Population CKD G3 — Frequency (at least) Annually | kdigo-2026 | p34 | p34/practice-point/1 | Practice Point |
| anemia-testing-g4 | ckd-g4 | at least twice a year | RENDERED: Population CKD G4 — Frequency (at least) Twice a year | kdigo-2026 | p34 | p34/practice-point/1 | Practice Point |
| anemia-testing-g5-g5d | ckd-g5-g5d | at least every 3 months | RENDERED: Population CKD G5 or G5D — Frequency (at least) Every 3 months | kdigo-2026 | p34 | p34/practice-point/1 | Practice Point |
| blood-loss-evaluation-ferritin | anemia-ckd | if the cause of iron deficiency is uncertain and ferritin <45 ng/ml (<45 µg/l), consider clinical evaluation for blood loss | RENDERED: ferritin <45 ng/ml (<45 µg/l), and where the cause of iron deficiency is uncertain, consider clinical evaluation for blood loss | kdigo-2026 | p36 | p36/practice-point/1 | Practice Point |
| blood-loss-evaluation-mcv | anemia-ckd | if the cause of iron deficiency is uncertain, MCV <80 fl without measured ferritin or known genetic cause: consider clinical evaluation for blood loss | RENDERED: microcytic anemia (mean corpuscular volume <80 fl) in the absence of measured ferritin or known genetic cause, and where the cause of iron deficiency is uncertain, consider clinical evaluation for blood loss | kdigo-2026 | p36 | p36/practice-point/1 | Practice Point |
| selected-severe-iron-deficiency | anemia-ckd | ferritin <100 ng/ml (<100 µg/l) in select cases | ferritin <100 ng/ml | kdigo-2026 | p35 | p35/narrative/select-case-severe-iron-deficiency | narrative |
| g5hd-iron-initiation-summary-ferritin | anemia-ckd-g5hd | initiate only if ferritin <=500 ng/ml (<=500 µg/l) and TSAT <=30% | RENDERED: ferritin ≤500 ng/ml (≤500 µg/l) and TSAT ≤30% | kdigo-2026 | p20 | p20/recommendation/2.1 | 2D |
| g5hd-iron-initiation | anemia-ckd-g5hd | initiate if ferritin <=500 ng/ml (<=500 µg/l) and TSAT <=30% | RENDERED: ferritin ≤500 ng/ml (≤500 µg/l) and TSAT ≤30% | kdigo-2026 | p37 | p37/recommendation/2.1 | 2D |
| nondialysis-pd-iron-initiation-low-ferritin | anemia-ckd-not-dialysis-g5pd | initiate if ferritin <100 ng/ml (<100 µg/l) and TSAT <40% | RENDERED: Ferritin <100 ng/ml (<100 µg/l) and TSAT <40% | kdigo-2026 | p41 | p41/recommendation/2.3 | 2D |
| nondialysis-pd-iron-initiation-mid-ferritin | anemia-ckd-not-dialysis-g5pd | initiate if ferritin >=100 and <300 ng/ml (>=100 and <300 µg/l), and TSAT <25% | RENDERED: Ferritin ≥100 ng/ml (≥100 µg/l) and <300 ng/ml (<300 µg/l), and TSAT <25% | kdigo-2026 | p41 | p41/recommendation/2.3 | 2D |
| ferric-citrate-starting-dose | ckd-not-dialysis | 1 g tablet (210 mg elemental iron), 1 tablet 3 times daily | RENDERED: Ferric citrate — 1 g — 210 mg — CKD not receiving dialysis: 1 tablet, 3 times daily | kdigo-2026 | p40 | p40/narrative/ferric-citrate-nondialysis | narrative |
| ferric-citrate-starting-dose | ckd-g5d | 1 g tablet (210 mg elemental iron), 2 tablets 3 times daily | RENDERED: Ferric citrate — 1 g — 210 mg — CKD G5D: 2 tablets, 3 times daily | kdigo-2026 | p40 | p40/narrative/ferric-citrate-g5d | narrative |
| ferric-maltol-starting-dose | anemia-ckd | 30 mg tablet, 1 tablet 2 times daily | RENDERED: Ferric maltol — 30 mg — 30 mg — 1 tablet, 2 times daily | kdigo-2026 | p40 | p40/narrative/ferric-maltol | narrative |
| ferrous-sulfate-starting-dose | anemia-ckd | 325 mg tablet (65 mg elemental iron), 1 tablet 3 times daily | RENDERED: Ferrous sulfate — 325 mg — 65 mg — 1 tablet, 3 times daily | kdigo-2026 | p40 | p40/narrative/ferrous-sulfate | narrative |
| ferrous-fumarate-starting-dose | anemia-ckd | 325 mg tablet (106 mg elemental iron), 1 tablet 2 times daily | RENDERED: Ferrous fumarate — 325 mg — 106 mg — 1 tablet, 2 times daily | kdigo-2026 | p40 | p40/narrative/ferrous-fumarate | narrative |
| ferrous-gluconate-starting-dose | anemia-ckd | 300 mg tablet (35 mg elemental iron), 4-6 tablets daily | RENDERED: Ferrous gluconate — 300 mg — 35 mg — 4–6 tablets, daily | kdigo-2026 | p40 | p40/narrative/ferrous-gluconate | narrative |
| liposomal-iron-starting-dose | anemia-ckd | 30 mg tablet, 1 tablet daily | RENDERED: Liposomal iron — 30 mg — 30 mg — 1 tablet, daily | kdigo-2026 | p40 | p40/narrative/liposomal-iron | narrative |
| heme-iron-polypeptide-starting-dose | anemia-ckd | 12 mg tablet, 1 tablet 3-4 times daily | RENDERED: Heme iron polypeptide — 12 mg — 12 mg — 1 tablet, 3–4 times daily | kdigo-2026 | p40 | p40/narrative/heme-iron-polypeptide | narrative |
| iron-dextran-maximum-and-time | ckd-iv-iron | maximum 20 mg/kg; minimum infusion 15 minutes for 50 mg or 100 mg/min over 4-6 hours; minimum injection >60 minutes | RENDERED: Low-molecular-weight iron dextran — maximum single dose 20 mg/kg — minimum infusion time 15 min for 50 mg, 100 mg/min 4–6 h — minimum injection time >60 min | kdigo-2026 | p41 | p41/narrative/iron-dextran-regimen | narrative |
| iron-dextran-concentration | ckd-iv-iron | 50 mg/ml | RENDERED: Low-molecular-weight iron dextran — 50 mg/ml | kdigo-2026 | p41 | p41/narrative/iron-dextran-concentration | narrative |
| iron-sucrose-concentration | ckd-iv-iron | 20 mg/ml | RENDERED: Iron sucrose — 20 mg/ml | kdigo-2026 | p41 | p41/narrative/iron-sucrose-concentration | narrative |
| ferric-gluconate-concentration | ckd-iv-iron | 12.5 mg/ml | RENDERED: Ferric gluconate — 12.5 mg/ml | kdigo-2026 | p41 | p41/narrative/ferric-gluconate-concentration | narrative |
| ferric-carboxymaltose-concentration | ckd-iv-iron | 50 mg/ml | RENDERED: Ferric carboxymaltose — 50 mg/ml | kdigo-2026 | p41 | p41/narrative/ferric-carboxymaltose-concentration | narrative |
| ferric-derisomaltose-concentration | ckd-iv-iron | 100 mg/ml | RENDERED: Ferric derisomaltose/iron isomaltoside — 100 mg/ml | kdigo-2026 | p41 | p41/narrative/ferric-derisomaltose-concentration | narrative |
| ferumoxytol-concentration | ckd-iv-iron | 30 mg/ml | RENDERED: Ferumoxytol — 30 mg/ml | kdigo-2026 | p41 | p41/narrative/ferumoxytol-concentration | narrative |
| iron-sucrose-ckd-regimen | ckd-not-dialysis | maximum 200 mg; 5 doses of 200 mg over 5 weeks; minimum infusion 15 minutes; minimum injection 5 minutes | RENDERED: Iron sucrose — CKD: 200 mg — 15 min — 5 min — CKD: 5 doses of 200 mg over 5 wk | kdigo-2026 | p41 | p41/narrative/iron-sucrose-ckd | narrative |
| iron-sucrose-pd-regimen | ckd-g5pd | maximum 400 mg; 300 mg over 1.5 hours twice 14 days apart, then 400 mg over 2.5 hours 14 days later | RENDERED: PD: 2 infusions of 300 mg over 1.5 h 14 d apart followed by one 400 mg infusion over 2.5 h 14 d later | kdigo-2026 | p41 | p41/narrative/iron-sucrose-pd | narrative |
| ferric-gluconate-regimen | ckd-iv-iron | maximum 125 mg; minimum infusion 60 minutes; minimum injection 10 minutes; sucrose complex 250 mg weekly for 4 doses | RENDERED: Ferric gluconate — 125 mg — 60 min — 10 min — Ferric gluconate in sucrose complex (250 mg 4 doses weekly) | kdigo-2026 | p41 | p41/narrative/ferric-gluconate-regimen | narrative |
| ferric-carboxymaltose-regimen | ckd-iv-iron | FDA maximum 750 mg and 7.5-minute injection; EMA maximum 1000 mg and 15-minute injection; 15-minute infusion; 750 mg twice 1 week apart | RENDERED: Ferric carboxymaltose — 750 mg (FDA), 1000 mg (EMA) — 15 min — 7.5 min (FDA), 15 min (EMA) — 750 mg 2 doses 1 wk apart | kdigo-2026 | p41 | p41/narrative/ferric-carboxymaltose-regimen | narrative |
| ferric-derisomaltose-regimen | ckd-iv-iron | FDA maximum 1000 mg with 20-minute infusion; EMA maximum 20 mg/kg, >15 minutes if <=1000 mg or >30 minutes if >1000 mg, injection 250 mg/min to 500 mg | RENDERED: Ferric derisomaltose/iron isomaltoside — 1000 mg (FDA), 20 mg/kg (EMA) — 20 min (FDA), >15 min if ≤1000 mg; >30 min if >1000 mg (EMA) — 250 mg/min (maximum 500 mg) | kdigo-2026 | p41 | p41/narrative/ferric-derisomaltose-regimen | narrative |
| ferumoxytol-regimen | ckd-iv-iron | maximum 510 mg; minimum infusion and injection 15 minutes | RENDERED: Ferumoxytol — 510 mg — 15 min — 15 min | kdigo-2026 | p41 | p41/narrative/ferumoxytol-regimen | narrative |
| routine-iron-withhold-ferritin | ckd-iron-treated | withhold routine iron if ferritin >700 ng/ml (>700 µg/l) | ferritin >700 ng/ml | kdigo-2026 | p44 | p44/practice-point/1 | Practice Point |
| routine-iron-withhold-tsat | ckd-iron-treated | withhold routine iron if TSAT >=40% | TSAT ≥40% | kdigo-2026 | p44 | p44/practice-point/1 | Practice Point |
| iron-monitoring-nondialysis-pd | ckd-not-dialysis | every 3 months | test hemoglobin (Hb), ferritin, and TSAT every 3 months for those with CKD not receiving dialysis or CKD G5PD | kdigo-2026 | p45 | p45/practice-point/3 | Practice Point |
| iron-monitoring-nondialysis-pd | ckd-g5pd | every 3 months | test hemoglobin (Hb), ferritin, and TSAT every 3 months for those with CKD not receiving dialysis or CKD G5PD | kdigo-2026 | p45 | p45/practice-point/3 | Practice Point |
| iron-monitoring-g5hd | ckd-g5hd | every 1-3 months | every 1-3 months for those with CKD G5HD | kdigo-2026 | p45 | p45/practice-point/3 | Practice Point |
| post-iv-iron-tsat-delay | ckd-iv-iron | delay TSAT testing 2-4 weeks after administration | healthcare providers should delay TSAT testing for 2-4 weeks after i.v. iron administration | kdigo-2026 | p45 | p45/narrative/post-iv-iron-tsat-delay | narrative |
| post-blood-loss-iron-retest | ckd-iron-after-blood-loss | retest immediately and 1 week after the event | RENDERED: retest iron status immediately and 1 week after the event | kdigo-2026 | p46 | p46/narrative/post-blood-loss-iron-retest | narrative |
| oral-to-iv-switch | ckd-oral-iron | switch after insufficient effect at 1-3 months or poor tolerability | RENDERED: Switch from oral to i.v. iron if there is an insufficient effect of an optimal oral regimen after 1–3 months or if tolerability is poor | kdigo-2026 | p46 | p46/practice-point/1 | Practice Point |
| oral-elemental-iron-daily | ckd-oral-iron | approximately 200 mg elemental iron daily | Oral iron is typically prescribed to provide w200 mg of elemental iron daily | kdigo-2026 | p46 | p46/narrative/oral-elemental-iron-dose | narrative |
| oral-iron-frequency-reduction | ckd-oral-iron | if 2 or 3 times daily causes gastrointestinal effects, reduce to once daily | If 2 or 3 times daily dosing causes gastrointestinal side effects, then reducing dosing to once daily may be reasonable | kdigo-2026 | p45 | p45/narrative/oral-iron-frequency-reduction | narrative |
| iv-iron-sucrose-narrative-maximum | ckd-iv-iron | do not exceed 200-400 mg per administration | doses of i.v. iron sucrose should not exceed 200-400 mg per administration | kdigo-2026 | p46 | p46/narrative/iron-sucrose-maximum | narrative |
| iv-iron-gluconate-narrative-maximum | ckd-iv-iron | do not exceed 125-250 mg per administration | RENDERED: i.v. iron gluconate should not exceed 125–250 mg per administration | kdigo-2026 | p46 | p46/narrative/iron-gluconate-maximum | narrative |
| post-infusion-routine-observation | ckd-iv-iron | no physiological basis for routine 30-minute observation after infusion | RENDERED: There is no physiological basis to routinely observe patients for 30 minutes after the infusion | kdigo-2026 | p46 | p46/narrative/no-routine-observation | narrative |
| nonspecific-reaction-observation | iv-iron-nonspecific-reaction | stop infusion and observe at least 15 minutes | stopping the infusion for at least 15 minutes and monitoring the response | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| reaction-restart-rate | iv-iron-nonspecific-reaction | if improved, restart at 25%-50% of initial rate | resumed at 25%-50% of the initial infusion rate with monitoring | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| mild-reaction-retrial-time | iv-iron-mild-reaction | retrial 1 hour after steroid or oral H1 blocker | RENDERED: Retrial after steroid or oral H1 blocker (1 hr after treatment) | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| moderate-reaction-hydrocortisone | iv-iron-moderate-reaction | i.v. hydrocortisone 100 mg | RENDERED: i.v. steroid 100 mg hydrocortisone | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| severe-reaction-oxygen | iv-iron-severe-reaction | 15 l oxygen | RENDERED: 15 l oxygen | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| severe-reaction-oxygen | iv-iron-severe-reaction | oxygen >15 l/min by face mask | supportive oxygen should be given at a high rate (>15 l/min) by a face mask | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| severe-reaction-epinephrine | iv-iron-severe-reaction | 0.5 mg of 1:1000 intramuscular epinephrine; repeat after 5-10 minutes if needed | RENDERED: intramuscular injection of 0.5 mg epinephrine in 1:1000 solution; repeat after 5–10 minutes if needed | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| severe-reaction-crystalloid | iv-iron-severe-reaction | 1 l crystalloid solution | Volume loading should be given using 1 l of crystalloid solution | kdigo-2026 | p47 | p47/practice-point/1 | Practice Point |
| profound-iron-deficiency-no-anemia | ckd-profound-iron-no-anemia | ferritin <30 ng/ml (<30 µg/l) and TSAT <20%: consider oral or i.v. iron | RENDERED: ferritin <30 ng/ml (<30 µg/l) and TSAT <20%, but no anemia, consider treatment with oral or i.v. iron | kdigo-2026 | p47 | p47/practice-point/2 | Practice Point |
| hif-phi-cancer-remission-window | hif-phi-high-risk | avoid HIF-PHIs with active cancer or cancer not in complete remission for at least 2-5 years | RENDERED: Active cancer or a history of cancer not in complete remission for at least 2–5 years | kdigo-2026 | p51 | p51/narrative/hif-phi-cancer-remission | narrative |
| hif-phi-us-dialysis-eligibility | ckd-g5d | in the U.S., vadadustat or daprodustat eligibility after 3 or 4 months on dialysis | RENDERED: U.S. approval for people with CKD G5D after receiving dialysis for at least 3 or 4 months | kdigo-2026 | p50 | p50/narrative/us-dialysis-eligibility | narrative |
| esa-initiation-hb-measurements | anemia-ckd | use >1 Hb measurement and the Hb trend to guide initiation | RENDERED: more than 1 Hb measurement and the Hb trend should be considered to guide initiation | kdigo-2026 | p52 | p52/narrative/esa-initiation-hb-trend | narrative |
| esa-initiation-g5d | adults-children-anemia-ckd-g5d | initiate ESA when Hb <=9.0-10.0 g/dl (<=90-100 g/l) | initiation of ESA therapy when the Hb concentration is ≤9.0-10.0 g/dl (≤90-100 g/l) | kdigo-2026 | p51 | p51/recommendation/3.2.1 | 2D |
| esa-initiation-nondialysis | adults-children-anemia-ckd-not-dialysis | generally Hb 8.5-10.0 g/dl (85-100 g/l) | for most people, it should be 8.5-10.0 g/dl (85-100 g/l) | kdigo-2026 | p53 | p53/narrative/esa-initiation-nondialysis | narrative |
| adult-esa-maintenance-target | adults-anemia-ckd-esa | target Hb <11.5 g/dl (115 g/l) | targeting the Hb level to below 11.5 g/dl (115 g/l) | kdigo-2026 | p54 | p54/recommendation/3.3.1 | 1D |
| child-esa-maintenance-consideration | children-anemia-ckd-esa | consider the adult upper target of 11.5 g/dl (115 g/l) with individualization | consider both the rationale for the recommended adult upper target of 11.5 g/dl (115 g/l) and individualization to the child | kdigo-2026 | p55 | p55/narrative/child-esa-maintenance-consideration | narrative |
| epoetin-nondialysis-initial | adults-children-anemia-ckd-not-dialysis | approximately 50 U/kg once or twice weekly; some use up to 100 U/kg once every 2 weeks | RENDERED: CKD not receiving dialysis: ~50 U/kg once or twice weekly (some use up to 100 U/kg once every 2 wk) | kdigo-2026 | p55 | p55/narrative/epoetin-nondialysis-initial | narrative |
| epoetin-convenient-dose | adults-children-anemia-ckd-not-dialysis | convenient doses 4000 or 10,000 U | RENDERED: Convenient doses may be 4000 or 10,000 U | kdigo-2026 | p55 | p55/narrative/epoetin-convenient-dose | narrative |
| epoetin-g5d-initial | adults-children-anemia-ckd-g5d | 50-100 U/kg 3 times weekly | RENDERED: CKD G5D: 50–100 U/kg 3 times weekly | kdigo-2026 | p55 | p55/narrative/epoetin-g5d-initial | narrative |
| epoetin-g5d-adjustment | adults-children-anemia-ckd-g5d | if Hb rise <1.0 g/dl after 4 weeks, increase 25 U/kg/dose; if rise >2 g/dl in 4 weeks, decrease 10-25 U/kg/dose | RENDERED: Increase the dose by 25 U/kg/dose if Hb rise is <1.0 g/dl (<10 g/l) after 4 wk. Decrease the dose by 10–25 U/kg/dose if Hb rise is >2 g/dl (>20 g/l) in 4 wk | kdigo-2026 | p55 | p55/narrative/epoetin-g5d-adjustment | narrative |
| darbepoetin-nondialysis-initial | adults-children-anemia-ckd-not-dialysis | 0.45 µg/kg weekly or 40-100 µg every 2-4 weeks | RENDERED: CKD not receiving dialysis: 0.45 µg/kg weekly or 40–100 µg every 2–4 wk | kdigo-2026 | p55 | p55/narrative/darbepoetin-nondialysis-initial | narrative |
| darbepoetin-convenient-dose | adults-children-anemia-ckd-not-dialysis | convenient doses 25, 40, 60, 100, 150, or 200 µg; 300 and 500 µg also available | RENDERED: Convenient doses may be 25, 40, 60, 100, 150, or 200 µg; 300 and 500 µg are also available | kdigo-2026 | p55 | p55/narrative/darbepoetin-convenient-dose | narrative |
| darbepoetin-g5d-initial | adults-children-anemia-ckd-g5d | 0.45 µg/kg weekly or 0.75 µg/kg every 2 weeks | RENDERED: CKD G5D: 0.45 µg/kg weekly or 0.75 µg/kg every 2 wk | kdigo-2026 | p55 | p55/narrative/darbepoetin-g5d-initial | narrative |
| darbepoetin-g5d-adjustment | adults-children-anemia-ckd-g5d | if Hb rise <1.0 g/dl after 4 weeks, increase 25%; if rise >2 g/dl in 4 weeks, decrease 25% | RENDERED: Increase the dose by 25% if Hb rise is <1.0 g/dl (<10 g/l) after 4 wk. Decrease the dose by 25% if Hb rise is >2 g/dl (>20 g/l) in 4 wk | kdigo-2026 | p55 | p55/narrative/darbepoetin-g5d-adjustment | narrative |
| methyl-peg-epoetin-nondialysis-initial | adults-children-anemia-ckd-not-dialysis | 0.6 µg/kg or 50-120 µg every 2 weeks, or 1.5 µg/kg or 120-200 µg/kg every month | RENDERED: Methyl polyethylene glycol-epoetin beta — CKD not receiving dialysis: 0.6 µg/kg or 50–120 µg every 2 wk, or 1.5 µg/kg or 120–200 µg/kg every month | kdigo-2026 | p55 | p55/narrative/methyl-peg-epoetin-nondialysis | narrative |
| methyl-peg-epoetin-g5d-initial | adults-children-anemia-ckd-g5d | 0.6 µg/kg every 2 weeks | RENDERED: CKD G5D: 0.6 µg/kg every 2 wk | kdigo-2026 | p55 | p55/narrative/methyl-peg-epoetin-g5d | narrative |
| methyl-peg-epoetin-g5d-adjustment | adults-children-anemia-ckd-g5d | if Hb rise <1.0 g/dl in 4 weeks, increase 30-50 µg/dose; if rise >2 g/dl in 4 weeks, decrease 30-50 µg/dose | RENDERED: Increase the dose by 30–50 µg/dose if Hb rise is <1.0 g/dl (<10 g/l) in 4 wk. Decrease the dose by 30–50 µg/dose if Hb rise is >2 g/dl (>20 g/l) in 4 wk | kdigo-2026 | p55 | p55/narrative/methyl-peg-epoetin-g5d-adjustment | narrative |
| epoetin-darbepoetin-adjustment-frequency | anemia-ckd-esa | generally do not adjust more than once weekly | RENDERED: Dose adjustment should generally not occur more frequently than once weekly | kdigo-2026 | p55 | p55/narrative/epoetin-darbepoetin-adjustment-frequency | narrative |
| methyl-peg-epoetin-adjustment-frequency | anemia-ckd-esa | generally do not adjust more than once every 2 weeks | RENDERED: Dose adjustment should generally not occur more frequently than once every 2 weeks | kdigo-2026 | p55 | p55/narrative/methyl-peg-epoetin-adjustment-frequency | narrative |
| esa-adjustment-frequency-and-exception | anemia-ckd-esa | avoid adjustment more often than every 4 weeks; if Hb rises >1.0 g/dl in 2-4 weeks, reduce dose 25%-50% | avoid adjusting the dose of the ESA more frequently than once every 4 weeks. The exception is when Hb increases by >1.0 g/dl (>10 g/l) in 2-4 weeks after the initiation of therapy, at which time the dose should be reduced by 25%-50% | kdigo-2026 | p56 | p56/practice-point/1 | Practice Point |
| esa-rise-to-avoid | anemia-ckd-esa | avoid Hb rise >2.0 g/dl (>20 g/l) over 4 weeks | a rise in Hb of >2.0 g/dl (>20 g/l) over a period of 4 weeks should be avoided | kdigo-2026 | p56 | p56/narrative/esa-rise-to-avoid | narrative |
| esa-initial-monthly-rise | anemia-ckd-esa | aim for Hb rise 1.0 g/dl (10 g/l) per month during initial therapy | RENDERED: aim for a Hb increase of 1.0 g/dl (10 g/l) per month during the initial phase of ESA therapy | kdigo-2026 | p56 | p56/narrative/esa-initial-monthly-rise | narrative |
| esa-initiation-monitoring | anemia-ckd-esa | monitor Hb every 2-4 weeks after initiation or dose change; avoid rise >1.0 g/dl (>10 g/l) in that interval | RENDERED: monitor Hb every 2–4 weeks and avoid a rapid rise of >1.0 g/dl (>10 g/l) during that interval | kdigo-2026 | p56 | p56/practice-point/6 | Practice Point |
| esa-maintenance-monitoring | anemia-ckd-esa | monitor Hb at least once every 3 months | during the maintenance phase of ESA therapy, monitor Hb at least once every 3 months | kdigo-2026 | p56 | p56/practice-point/7 | Practice Point |
| cancer-chemotherapy-esa-threshold | adults-anemia-ckd-esa | with chemotherapy-associated anemia and noncurative intent, consider ESA if Hb <10 g/dl (<100 g/l) | RENDERED: chemotherapy-associated anemia, treatment is not curative in intent, and Hb has declined to <10 g/dl (<100 g/l) | kdigo-2026 | p57 | p57/narrative/cancer-esa-threshold | narrative |
| daprodustat-dose | anemia-ckd-hif-phi | nondialysis: 2 to approximately 4 mg ESA-naive or 4 mg after ESA; G5D: Japan 4 mg, United States 1 to approximately 4 mg ESA-naive or 4-12 mg after ESA; maximum 24 mg daily | RENDERED: Daprodustat — CKD not receiving dialysis: 2–~4 mg (ESA-naive), 4 mg (switch from ESA); CKD G5D: Japan, 4 mg; the United States, 1–~4 mg (ESA-naive), 4–12 mg (switch from ESA) — 24 mg — Daily | kdigo-2026 | p58 | p58/narrative/daprodustat-dose | narrative |
| desidustat-dose | anemia-ckd-hif-phi | 100 mg ESA-naive or 100, 125, or 150 mg after ESA; maximum 150 mg 3 times weekly | RENDERED: Desidustat — 100 mg (ESA-naive), 100, 125, or 150 mg (switch from ESA) — 150 mg — 3 times weekly | kdigo-2026 | p58 | p58/narrative/desidustat-dose | narrative |
| enarodustat-dose-nondialysis-pd | ckd-not-dialysis | 2 mg daily; maximum 8 mg daily | RENDERED: CKD not receiving dialysis and CKD G5PD: 2 mg (ESA-naive and switch from ESA) — 8 mg — Daily | kdigo-2026 | p58 | p58/narrative/enarodustat-nondialysis | narrative |
| enarodustat-dose-nondialysis-pd | ckd-g5pd | 2 mg daily; maximum 8 mg daily | RENDERED: CKD not receiving dialysis and CKD G5PD: 2 mg (ESA-naive and switch from ESA) — 8 mg — Daily | kdigo-2026 | p58 | p58/narrative/enarodustat-pd | narrative |
| enarodustat-dose-hd | ckd-g5hd | 4 mg daily; maximum 8 mg daily | RENDERED: CKD G5HD: 4 mg (ESA-naive and switch from ESA) — 8 mg — Daily | kdigo-2026 | p58 | p58/narrative/enarodustat-hd | narrative |
| molidustat-dose-nondialysis | ckd-not-dialysis | 25 mg ESA-naive or 25 to approximately 50 mg after ESA; maximum 200 mg daily | RENDERED: CKD not receiving dialysis: 25 mg (ESA-naive), 25–~50 mg (switch from ESA) — 200 mg — Daily | kdigo-2026 | p58 | p58/narrative/molidustat-nondialysis | narrative |
| molidustat-dose-g5d | ckd-g5d | 75 mg daily; maximum 200 mg daily | RENDERED: CKD G5D: 75 mg (ESA-naive and switch from ESA) — 200 mg — Daily | kdigo-2026 | p58 | p58/narrative/molidustat-g5d | narrative |
| roxadustat-dose-naive | anemia-ckd-hif-phi | European Union: 70 mg if weight <100 kg or 100 mg if weight >=100 kg; Japan: 50 mg; maximum 3.0 mg/kg 3 times weekly | RENDERED: European Union, 70 mg for body weight <100 kg, 100 mg for body weight ≥100 kg; Japan, 50 mg — 3.0 mg/kg body weight — 3 times weekly | kdigo-2026 | p58 | p58/narrative/roxadustat-naive | narrative |
| roxadustat-dose-switch | ckd-not-dialysis | European Union 70-200 mg or Japan 70-100 mg; maximum 3.0 mg/kg 3 times weekly | RENDERED: CKD not receiving dialysis (switch from ESA): European Union, 70–200 mg; Japan, 70–100 mg — 3.0 mg/kg body weight — 3 times weekly | kdigo-2026 | p58 | p58/narrative/roxadustat-switch | narrative |
| vadadustat-dose | anemia-ckd-hif-phi | 300 mg daily; maximum 600 mg daily | RENDERED: Vadadustat — 300 mg (ESA-naive and switch from ESA) — 600 mg — Daily | kdigo-2026 | p58 | p58/narrative/vadadustat-dose | narrative |
| hif-phi-hb-monitoring | anemia-ckd-hif-phi | monitor Hb 2-4 weeks after initiation or dose adjustment, then every 4 weeks | monitor Hb levels 2-4 weeks after initiation or dose adjustments and subsequently every 4 weeks during therapy | kdigo-2026 | p58 | p58/practice-point/3 | Practice Point |
| roxadustat-thyroid-monitoring | anemia-ckd-roxadustat | periodically during first 3 months, then as clinically indicated | RENDERED: periodic monitoring of thyroid function during the first 3 months of treatment and as clinically indicated subsequently | kdigo-2026 | p58 | p58/practice-point/4 | Practice Point |
| hif-phi-nonresponse-stop | anemia-ckd-hif-phi | discontinue after 3-4 months without desired erythropoietic response | RENDERED: discontinue HIF-PHI after 3–4 months if a desired erythropoietic response has not been achieved | kdigo-2026 | p58 | p58/practice-point/5 | Practice Point |
| chronic-esa-hyporesponsiveness | anemia-ckd-esa-hyporesponsive | chronic if >4 months | ESA hyporesponsiveness can be acute or chronic (>4 months) | kdigo-2026 | p59 | p59/narrative/chronic-esa-hyporesponsiveness | narrative |
| nkf-iv-epo-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at i.v. EPO >450 IU/kg/week | RENDERED: Failure to achieve target Hb levels with epoetin doses greater than: i.v. EPO: 450 IU/kg/wk | kdigo-2026 | p60 | p60/narrative/nkf-iv-epo | narrative |
| nkf-sc-epo-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at subcutaneous EPO >300 IU/kg/week | RENDERED: Failure to achieve target Hb levels with epoetin doses greater than: s.c. EPO: 300 IU/kg/wk | kdigo-2026 | p60 | p60/narrative/nkf-sc-epo | narrative |
| ebpg-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at epoetin >300 IU/kg/week (20,000 IU/week) or darbepoetin 1.5 µg/kg (100 µg/week) | RENDERED: Failure to attain the target Hb concentration while receiving >300 IU/kg/wk (20,000 IU/wk) of epoetin or 1.5 µg/kg of darbepoetin alfa (100 µg/wk) | kdigo-2026 | p60 | p60/narrative/ebpg-hyporesponsiveness | narrative |
| kdigo-initial-hyporesponsiveness | esa-hyporesponsiveness-reference | no Hb increase after first month on appropriate weight-based dosing | RENDERED: If no increase in Hb concentration from baseline after the first month of ESA treatment on appropriate weight-based dosing | kdigo-2026 | p60 | p60/narrative/kdigo-initial-hyporesponsiveness | narrative |
| kdigo-initial-escalation-limit | esa-hyporesponsiveness-reference | avoid repeated escalation beyond double the initial weight-based dose | RENDERED: avoid repeated escalations in ESA dose beyond double the initial weight-based dose | kdigo-2026 | p60 | p60/narrative/kdigo-initial-escalation | narrative |
| kdigo-acquired-hyporesponsiveness | esa-hyporesponsiveness-reference | after stable dosing, 2 increases up to 50% above the stable dose to maintain Hb | RENDERED: they require 2 increases in ESA doses up to 50% beyond the dose at which they had been stable in an effort to maintain a stable Hb concentration | kdigo-2026 | p60 | p60/narrative/kdigo-acquired-hyporesponsiveness | narrative |
| kdigo-acquired-escalation-limit | esa-hyporesponsiveness-reference | avoid repeated escalation beyond double the stable dose | RENDERED: avoid repeated escalations in ESA dose beyond double the dose at which they had been stable | kdigo-2026 | p60 | p60/narrative/kdigo-acquired-escalation | narrative |
| riscavid-resistance-index | esa-hyporesponsiveness-reference | weight-adjusted ESA resistance index >15.4 IU/kg x g/dl | RENDERED: Weight-adjusted ESA resistance index (weekly ESA dose/[body weight × Hb]) > 15.4 IU/kg × g/dl | kdigo-2026 | p60 | p60/narrative/riscavid-resistance-index | narrative |
| uk-iv-epo-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at i.v. EPO >450 IU/kg/week | RENDERED: Failure to achieve target Hb levels with epoetin doses greater than: i.v. EPO 450 IU/kg/wk | kdigo-2026 | p60 | p60/narrative/uk-iv-epo | narrative |
| uk-sc-epo-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at subcutaneous EPO >300 IU/kg/week | RENDERED: Failure to achieve target Hb levels with epoetin doses greater than: s.c. EPO: 300 IU/kg/wk | kdigo-2026 | p60 | p60/narrative/uk-sc-epo | narrative |
| uk-darbepoetin-hyporesponsiveness | esa-hyporesponsiveness-reference | failure at darbepoetin >1.5 µg/kg/week | RENDERED: Darbepoetin dose >1.5 µg/kg/wk | kdigo-2026 | p60 | p60/narrative/uk-darbepoetin | narrative |
| jsdt-hd-hyporesponsiveness | ckd-g5hd | failure despite i.v. rHuEPO 3000 IU/dose 3 times weekly (9000 IU/week) or i.v. darbepoetin 60 µg weekly | RENDERED: People receiving HD: Despite 3000 IU/dose of i.v. rHuEPO 3 times weekly (9000 IU/wk) or 60 µg/wk of i.v. darbepoetin alfa once weekly | kdigo-2026 | p60 | p60/narrative/jsdt-hd-hyporesponsiveness | narrative |
| jsdt-pd-hyporesponsiveness | ckd-g5pd | failure despite subcutaneous rHuEPO 6000 IU weekly or i.v. darbepoetin 60 µg weekly | RENDERED: People receiving PD: Despite 6000 IU/dose of s.c. rHuEPO once weekly (6000 IU/wk) or 60 µg/wk of i.v. darbepoetin alfa once weekly | kdigo-2026 | p60 | p60/narrative/jsdt-pd-hyporesponsiveness | narrative |
| jsdt-nondialysis-hyporesponsiveness | ckd-not-dialysis | failure despite subcutaneous rHuEPO 6000 IU weekly | RENDERED: People with CKD not receiving dialysis: Despite 6000 IU/dose of s.c. rHuEPO once weekly (6000 IU/wk) | kdigo-2026 | p60 | p60/narrative/jsdt-nondialysis-hyporesponsiveness | narrative |
| hif-phi-nonresponse-stop | anemia-ckd-esa-hyporesponsive | discontinue after 3-4 months without desired erythropoietic response | RENDERED: if a desired erythropoietic response has not been achieved after 3–4 months of initiating HIF-PHIs, discontinue treatment | kdigo-2026 | p62 | p62/practice-point/1 | Practice Point |
| transfusional-iron-overload | chronically-transfused-ckd | organ damage concern near 15-20 g total iron, about 75-100 RBC units | hemosiderosis can produce organ damage when the total dose of iron delivered approaches 15-20 g, the amount of iron in 75-100 U of RBCs | kdigo-2026 | p64 | p64/narrative/transfusional-iron-overload | narrative |
| rbc-unit-iron | chronically-transfused-ckd | each RBC unit delivers 200-250 mg iron | RENDERED: Each unit of RBCs contains approximately 200–250 mg of iron | kdigo-2026 | p64 | p64/narrative/rbc-unit-iron | narrative |
| stable-inpatient-transfusion | stable-adult-inpatients | consider restrictive transfusion at Hb <7 g/dl (<70 g/l) | a restrictive transfusion strategy can be used when Hb is <7 g/dl (<70 g/l) | kdigo-2026 | p67 | p67/narrative/stable-inpatient-transfusion | narrative |
| cardiac-surgery-transfusion | adult-cardiac-surgery | consider restrictive transfusion at Hb <7.5 g/dl (<75 g/l) | <7.5 g/dl (<75 g/l) for patients undergoing cardiac surgery | kdigo-2026 | p67 | p67/narrative/cardiac-surgery-transfusion | narrative |
| orthopedic-cvd-transfusion | adult-orthopedic-or-cvd | consider restrictive transfusion at Hb <8 g/dl (<80 g/l) | RENDERED: <8 g/dl (<80 g/l) for those undergoing orthopedic surgery or those with clinically significant cardiovascular disease | kdigo-2026 | p67 | p67/narrative/orthopedic-cvd-transfusion | narrative |
| g5hd-algorithm-monthly-monitoring | anemia-ckd-g5hd-algorithm | check Hb, ferritin, and TSAT every month | Check Hb, ferritin, and TSAT every month | kdigo-2026 | p95 | p95/narrative/g5hd-algorithm-monthly-monitoring | narrative |
| g5hd-algorithm-esa-start | anemia-ckd-g5hd-algorithm | consider ESA when Hb <=9-10 g/dl | consider benefits and risks of starting ESA therapy as first-line therapy when Hb ≤9-10 g/dl | kdigo-2026 | p95 | p95/narrative/g5hd-algorithm-esa-start | narrative |
| nondialysis-algorithm-esa-start | anemia-ckd-nondialysis-algorithm | generally Hb <=8.5-10 g/dl | generally at Hb ≤8.5-10 g/dl | kdigo-2026 | p96 | p96/narrative/nondialysis-algorithm-esa-start | narrative |
| g5pd-algorithm-esa-start | anemia-ckd-g5pd-algorithm | consider ESA when Hb <=9-10 g/dl | consider benefits and risks of starting ESA therapy as first-line therapy when Hb ≤9-10 g/dl | kdigo-2026 | p97 | p97/narrative/g5pd-algorithm-esa-start | narrative |
| ktr-algorithm-esa-start | anemia-ckd-ktr-algorithm | generally Hb <=8.5-10 g/dl | generally at Hb ≤8.5-10 g/dl | kdigo-2026 | p98 | p98/narrative/ktr-algorithm-esa-start | narrative |
| pediatric-algorithm-severe-iron | children-anemia-ckd-algorithm | ferritin <45 ng/ml (<45 µg/l) | RENDERED: Severe iron deficiency, i.e., ferritin <45 ng/ml (µg/l)? | kdigo-2026 | p99 | p99/narrative/pediatric-algorithm-severe-iron | narrative |

## Conflicts

CONFLICT: severe-reaction-oxygen — `oxygen >15 l/min by face mask`; `15 l oxygen`. Figure 7 gives `15 l oxygen`, while its supporting prose specifies `oxygen >15 l/min by face mask`. The sheet preserves both
source statements rather than silently converting the figure's amount into the
prose's flow threshold.

## Coverage

The source is `bound`: marker records delimit recommendation-shaped text but do not
prove a complete recommendation denominator. Every marker occurrence not discharged
by a recommendation-backed threshold row is listed below. The bound artifact contains
118 marker records under 118 distinct locators. Threshold rows cite 19 locators; the
remaining 99 locators were read and contain no additional numeric patient-action
decision point beyond rows represented from source tables, figures, narrative, or a
duplicate summary/body occurrence.

- `p18/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/recommendation/2.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/recommendation/2.3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/recommendation/2.4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p20/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p21/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p21/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p21/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p21/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p22/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p22/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p22/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p23/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p23/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p23/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p24/recommendation/3.2.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p24/recommendation/3.2.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p24/recommendation/3.3.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p24/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p24/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p25/practice-point/11` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p26/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p27/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p35/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p39/recommendation/2.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p41/recommendation/2.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p41/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p43/recommendation/2.4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p44/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p45/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p45/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p45/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p45/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p46/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p46/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p49/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p49/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p50/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p51/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p52/recommendation/3.2.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p55/recommendation/3.3.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p55/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p55/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p56/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p56/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p56/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p56/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p58/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p58/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p59/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p59/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p61/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p61/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p62/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p62/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p63/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p64/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p66/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p67/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p67/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p68/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
