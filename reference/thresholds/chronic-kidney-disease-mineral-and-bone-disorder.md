# Chronic kidney disease-mineral and bone disorder — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2017 | KDIGO | KDIGO/KDIGO-2017-CKD-MBD-Guideline | guideline | 2017 guideline update | 2017-07 | https://doi.org/10.1016/j.kisu.2017.04.001 | stated | bound |

## Scope

**Read:** all 60 source pages: cover and title matter; contents and supplementary-
material inventory; executive material; reference key; CKD nomenclature; conversion
factors; abbreviations; notice; foreword; membership; abstract; the full summary of
recommendations; the comparison of the 2017 update with the 2009 guideline; every
clinical chapter; every table and figure; methods; biographies and disclosures;
acknowledgments; and references. The rows retain CKD definitions and stage boundaries,
stage-triggered testing or treatment decisions, monitoring intervals, treatment targets,
therapy-selection thresholds, and transplant timing. Study eligibility and results,
epidemiologic estimates, research recommendations, publication years, bibliography
numbers, and numeric examples the Work Group expressly did not adopt as targets were
read but do not produce rows. Historical 2009 recommendations shown only for comparison
were not treated as current 2017 decision points.

Pages 9, 16-19, 24-25, 28-29, 31-33, and 36-41 were rendered at 180 dpi and read to
preserve classification-table operators, boxed recommendation boundaries, stage ranges,
units, the transplant branching on the summary pages, and clinical qualifiers whose
extracted text was hyphenated or carried ligatures.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| cover, title, contents, tables, supplementary-material inventory, executive material, and reference key | 1-8 | read 2026-08-31; blind 2026-08-31 |
| CKD nomenclature and classification | 9 | yes |
| conversion factors, abbreviations, notice, foreword, membership, and abstract | 10-15 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendations | 16-19 | yes |
| comparison of the 2017 update with the 2009 guideline | 20-22 | yes |
| clinical chapters 3.2, 4.1, 4.2, 4.3, and 5 | 23-41 | yes |
| methodological approach | 42-48 | read 2026-08-31; blind 2026-08-31 |
| biographies, disclosures, and acknowledgments | 49-55 | read 2026-08-31; blind 2026-08-31 |
| references | 56-60 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 9de805834e3d6f009c11af84192e696c5b3b09dc9d1b13d141801f7c421969c9; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| people-ckd | patients with CKD |
| ckd-g1 | CKD G1 |
| ckd-g2 | CKD G2 |
| ckd-g3a | CKD G3a |
| ckd-g3b | CKD G3b |
| ckd-g4 | CKD G4 |
| ckd-g5 | CKD G5 |
| ckd-g5-including-g5d | CKD G5, including G5D |
| adults-ckd | adult patients with CKD |
| children-ckd | children with CKD |
| infants-ckd-g2-g5d | infants with CKD G2-G5D |
| children-ckd-g2-g5d | children with CKD G2-G5D |
| ckd-g3a-g3b | patients with CKD G3a-G3b |
| ckd-g3a-g5d | patients with CKD G3a-G5D |
| ckd-g3a-g5 | patients with CKD G3a-G5 |
| ckd-g3a-g5d-mbd-or-osteoporosis-risk | patients with CKD G3a-G5D with evidence of CKD-MBD and/or risk factors for osteoporosis |
| adults-ckd-g3a-g5d | adult patients with CKD G3a-G5D |
| children-ckd-g3a-g5d | children with CKD G3a-G5D |
| ckd-g4-g5d | patients with CKD G4-G5D |
| ckd-g5d | patients with CKD G5D |
| ckd-g3a-g5-nondialysis | patients with CKD G3a-G5 not on dialysis |
| adults-ckd-g3a-g5-nondialysis | adult patients with CKD G3a-G5 not on dialysis |
| ckd-g4-g5-severe-progressive-hpt | patients with CKD G4-G5 with severe and progressive hyperparathyroidism |
| ckd-g3a-g5d-severe-hpt-treatment-failure | patients with CKD G3a-G5D with severe hyperparathyroidism who fail to respond to medical or pharmacological therapy |
| ckd-g1-g2-osteoporosis | patients with CKD G1-G2 with osteoporosis and/or high risk of fracture |
| ckd-g3a-g3b-normal-pth-osteoporosis | patients with CKD G3a-G3b with PTH in the normal range and osteoporosis and/or high risk of fracture |
| ckd-g3a-g5d-mbd-low-bmd-fracture | patients with CKD G3a-G5D with biochemical abnormalities of CKD-MBD and low BMD and/or fragility fractures |
| children-adolescents-ckd-g2-g5d-height-deficit | children and adolescents with CKD G2-G5D and related height deficits |
| immediate-posttransplant | patients in the immediate post-kidney transplant period |
| post-immediate-transplant | patients after the immediate post-kidney transplant period |
| ckd-g1t-g3bt | CKD G1T-G3bT |
| ckd-g4t | CKD G4T |
| ckd-g5t | CKD G5T |
| ckd-g3at-g5t | CKD G3aT-G5T |
| ckd-g1t-g5t | patients with CKD G1T-G5T |
| ckd-g1t-g5t-osteoporosis-risk | patients with CKD G1T-G5T with risk factors for osteoporosis |
| first-12-months-transplant-low-bmd | patients in the first 12 months after kidney transplant with low BMD |
| ckd-g4t-g5t-low-bmd | patients with CKD G4T-G5T with known low BMD |
| ckd-treatment-or-abnormality | CKD patients receiving treatments for CKD-MBD, or in whom biochemical abnormalities are identified |
| ckd-g3a-g5d-known-calcification | patients with CKD G3a-G5D with known vascular or valvular calcification |
| adults-ckd-significant-symptomatic-hypocalcemia | adults with CKD and significant or symptomatic hypocalcemia |
| adults-ckd-mild-asymptomatic-hypocalcemia | adults with CKD and mild asymptomatic hypocalcemia |
| ckd-g3a-g5d-phosphate-diet | patients with CKD G3a-G5D limiting dietary phosphate |
| ckd-g3a-g5-severe-progressive-shpt | patients with CKD G3a-G5 with severe and progressive SHPT |
| children-pth-lowering-therapy | children receiving PTH-lowering therapies |
| children-short-stature-ckd | children with short stature and CKD |
| kidney-transplant-recipients | kidney transplant recipients |
| de-novo-kidney-transplant-recipients | de novo kidney transplant recipients |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-minimum-duration | duration defining CKD |
| gfr-category | GFR category |
| biochemical-monitoring-start | beginning of monitoring serum calcium, phosphate, PTH, and alkaline phosphatase activity |
| biochemical-monitoring-frequency-basis | basis for biochemical monitoring frequency |
| calcium-phosphate-monitoring | monitoring interval for serum calcium and phosphate |
| pth-monitoring | monitoring interval for PTH |
| alkaline-phosphatase-monitoring | monitoring interval for alkaline phosphatase activity |
| vitamin-d-measurement | CKD stages in which 25(OH)D levels might be measured |
| vitamin-d-retesting | basis for repeated 25(OH)D testing |
| vitamin-d-deficiency-treatment | treatment approach for vitamin D deficiency and insufficiency |
| trend-based-decisions | CKD stages in which therapeutic decisions should be based on trends |
| combined-assessment-context | CKD-MBD assessments considered with laboratory trends |
| calcium-phosphate-joint-use | use of individual calcium and phosphate values rather than calcium-phosphate product |
| laboratory-assay-reporting | laboratory assay and handling information reported to clinicians |
| bmd-testing | CKD stages in which BMD testing may affect treatment decisions |
| bone-biopsy | CKD stages in which bone biopsy may affect treatment decisions |
| bone-turnover-testing | CKD stages in which PTH or bone-specific alkaline phosphatase may evaluate bone disease |
| bone-turnover-prediction | PTH or bone-specific alkaline-phosphatase pattern that predicts bone turnover |
| pediatric-dxa-adjustment | adjustment of pediatric DXA results for short stature |
| collagen-marker-testing | CKD stages in which bone-derived collagen turnover markers should not be routinely measured |
| infant-length-monitoring | minimum infant length-measurement frequency |
| child-growth-monitoring | minimum child linear-growth assessment frequency |
| calcification-imaging | CKD stages in which radiograph and echocardiogram are alternatives to CT-based imaging |
| calcification-risk | CKD stages in which known vascular or valvular calcification indicates highest cardiovascular risk |
| calcification-guided-management | use of calcification risk information in CKD-MBD management |
| serial-mbd-assessment | CKD stages in which CKD-MBD treatment uses serial phosphate, calcium, and PTH assessments |
| phosphate-target | CKD stages in which elevated phosphate is lowered toward normal |
| adult-calcium-target | CKD stages in which adult hypercalcemia is avoided |
| pediatric-calcium-target | CKD stages in which pediatric calcium is kept in the age-appropriate normal range |
| dialysate-calcium | dialysate calcium concentration |
| dialysate-calcium-selection | individualization of dialysate calcium concentration |
| phosphate-treatment-trigger | CKD stages and biochemical trigger for phosphate-lowering treatment |
| calcium-binder-restriction | CKD stages in which calcium-based phosphate-binder dose is restricted |
| calcium-binder-maximum | maximum calcium-based phosphate-binder dose |
| pediatric-phosphate-therapy-selection | CKD stages in which pediatric phosphate-lowering treatment choice is based on serum calcium |
| aluminum-avoidance | CKD stages in which long-term aluminum-containing binders are avoided |
| dialysate-aluminum-avoidance | CKD stage in which dialysate aluminum contamination is avoided |
| dietary-phosphate-treatment | CKD stages in which dietary phosphate is limited for hyperphosphatemia |
| dietary-phosphate-source | phosphate-source categories considered in dietary recommendations |
| hidden-phosphate-sources | dietary supplements and medications as phosphate sources |
| phosphate-food-selection | food-selection counseling based on phosphate bioavailability and additives |
| phosphate-education | education focus for dietary phosphate counseling |
| dietary-phosphate-protein-caveat | protein-intake constraint on dietary phosphate restriction |
| dialytic-phosphate-removal | CKD stage in which dialytic phosphate removal is increased for persistent hyperphosphatemia |
| pth-evaluation-trigger | CKD stages and PTH pattern triggering evaluation of modifiable factors |
| pth-evaluation-factors | modifiable factors evaluated when the PTH trigger is met |
| calcitriol-routine-use | CKD stages in which routine calcitriol or vitamin D analog use is discouraged |
| calcitriol-reserved-use | CKD stages in which calcitriol or vitamin D analogs may be reserved |
| calcitriol-initiation-titration | initiation and titration approach for calcitriol or vitamin D analogs |
| pediatric-calcitriol-use | pediatric CKD stages in which calcitriol or vitamin D analogs may maintain calcium |
| ipth-target | iPTH range relative to the assay upper normal limit |
| ipth-therapy-change | PTH change within the target range prompting therapy initiation or change |
| pth-lowering-therapy | CKD stage in which listed PTH-lowering therapies are options |
| pth-lowering-selection | factors guiding selection among PTH-lowering therapies |
| pediatric-pth-lowering-caution | pediatric safety constraint on PTH-lowering therapies |
| parathyroidectomy | CKD stages in which treatment failure supports parathyroidectomy |
| general-population-bone-management | CKD stages in which osteoporosis or fracture risk is managed as in the general population |
| general-population-bone-criteria | criteria identifying osteoporosis or high fracture risk for general-population management |
| ckd-mbd-bone-treatment | CKD stages in which bone-treatment choices account for biochemical abnormalities and CKD progression |
| ckd-mbd-bone-treatment-factors | factors used to select bone treatment |
| ckd-mbd-bone-treatment-risks | therapy-specific risks considered when selecting bone treatment |
| growth-hormone-treatment | pediatric CKD stages in which growth hormone is recommended after prerequisites |
| growth-hormone-prerequisites | prerequisites before recombinant human growth hormone treatment |
| immediate-posttransplant-monitoring | serum calcium and phosphate monitoring frequency until stable |
| transplant-monitoring-frequency-basis | basis for post-immediate-transplant monitoring frequency |
| transplant-abnormality-management | nondialysis CKD stages used to manage posttransplant abnormalities |
| transplant-vitamin-d-measurement | transplant CKD stages in which 25(OH)D levels might be measured |
| transplant-vitamin-d-retesting | basis for repeated posttransplant 25(OH)D testing |
| transplant-vitamin-d-treatment | transplant CKD stages in which vitamin D deficiency is corrected as in the general population |
| transplant-bmd-testing | transplant CKD stages in which BMD testing may alter therapy |
| posttransplant-bone-treatment-window | posttransplant time and eGFR supporting consideration of bone treatment |
| posttransplant-bone-treatment-options | therapies considered within the posttransplant treatment window |
| posttransplant-bone-treatment-selection | laboratory abnormalities influencing posttransplant treatment choices |
| posttransplant-bone-biopsy | use of bone biopsy to guide posttransplant treatment |
| posttransplant-treatment-evidence-window | posttransplant time after which treatment evidence is insufficient |
| transplant-low-bmd-management | transplant CKD stages managed as corresponding nondialysis CKD stages |
| bone-biopsy-indications | clinical situations supporting bone biopsy |
| bone-biopsy-pth-trend | inconsistent PTH trends supporting bone biopsy |
| bone-biopsy-uncertain-etiology | uncertain symptom or biochemical-abnormality etiology supporting bone biopsy |
| antiresorptive-biopsy-caveat | effect of inability to perform bone biopsy on antiresorptive treatment |
| antiresorptive-prerequisites | renal-osteodystrophy and caution prerequisites for antiresorptive treatment |
| antiresorptive-aki-risk | acute kidney injury risk considered with antiresorptive therapy |
| adult-hypocalcemia-management | adult hypocalcemia severity guiding individualized correction |
| adult-mild-hypocalcemia-tolerance | mild asymptomatic hypocalcemia that may be tolerated to avoid calcium loading |
| bone-phenotype-diagnostic-certainty | weighing treatment risk against accuracy of bone-phenotype diagnosis |
| transplant-cinacalcet-approval | approval status for cinacalcet after transplant |
| transplant-cinacalcet-mineralization | bone-mineralization evidence for cinacalcet after transplant |
| transplant-denosumab-bmd | BMD evidence for denosumab after transplant |
| transplant-denosumab-uti | urinary-tract-infection finding for denosumab after transplant |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-minimum-duration | people-ckd | abnormalities present for >3 months | RENDERED: CKD is defined as abnormalities of kidney structure or function, present for > 3 months | kdigo-2017 | p9 | p9/narrative/ckd-definition | narrative |
| gfr-category | ckd-g1 | GFR >=90 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G1 Normal or high ≥90 | kdigo-2017 | p9 | p9/narrative/gfr-g1 | narrative |
| gfr-category | ckd-g2 | GFR 60-89 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G2 Mildly decreased 60–89 | kdigo-2017 | p9 | p9/narrative/gfr-g2 | narrative |
| gfr-category | ckd-g3a | GFR 45-59 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G3a Mildly to moderately decreased 45–59 | kdigo-2017 | p9 | p9/narrative/gfr-g3a | narrative |
| gfr-category | ckd-g3b | GFR 30-44 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G3b Moderately to severely decreased 30–44 | kdigo-2017 | p9 | p9/narrative/gfr-g3b | narrative |
| gfr-category | ckd-g4 | GFR 15-29 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G4 Severely decreased 15–29 | kdigo-2017 | p9 | p9/narrative/gfr-g4 | narrative |
| gfr-category | ckd-g5 | GFR <15 mL/min/1.73 m² | RENDERED: GFR categories (ml/min/1.73 m²), description and range ... G5 Kidney failure <15 | kdigo-2017 | p9 | p9/narrative/gfr-g5 | narrative |
| biochemical-monitoring-start | adults-ckd | begin at CKD G3a | RENDERED: monitoring serum levels of calcium, phosphate, PTH, and alkaline phosphatase activity beginning in CKD G3a | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.1-adult | narrative |
| biochemical-monitoring-start | children-ckd | begin at CKD G2 | RENDERED: In children, we suggest such monitoring beginning in CKD G2 | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.1-child | narrative |
| biochemical-monitoring-frequency-basis | ckd-g3a-g5d | base frequency on abnormalities and CKD progression in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, it is reasonable to base the frequency of monitoring serum calcium, phosphate, and PTH on the presence and magnitude of abnormalities, and the rate of progression of CKD | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-basis | narrative |
| calcium-phosphate-monitoring | ckd-g3a-g3b | every 6-12 months | RENDERED: In CKD G3a–G3b: for serum calcium and phosphate, every 6–12 months | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g3 | narrative |
| pth-monitoring | ckd-g3a-g3b | by baseline level and CKD progression | RENDERED: and for PTH, based on baseline level and CKD progression | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g3-pth | narrative |
| calcium-phosphate-monitoring | ckd-g4 | every 3-6 months | RENDERED: In CKD G4: for serum calcium and phosphate, every 3–6 months | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g4-ca-p | narrative |
| pth-monitoring | ckd-g4 | every 6-12 months | RENDERED: and for PTH, every 6–12 months | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g4-pth | narrative |
| calcium-phosphate-monitoring | ckd-g5-including-g5d | every 1-3 months | RENDERED: In CKD G5, including G5D: for serum calcium and phosphate, every 1–3 months | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g5-ca-p | narrative |
| pth-monitoring | ckd-g5-including-g5d | every 3-6 months | RENDERED: and for PTH, every 3–6 months | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-g5-pth | narrative |
| alkaline-phosphatase-monitoring | ckd-g4-g5d | every 12 months, or more often with elevated PTH | RENDERED: In CKD G4–G5D: for alkaline phosphatase activity, every 12 months, or more frequently in the presence of elevated PTH | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-alp | narrative |
| biochemical-monitoring-frequency-basis | ckd-treatment-or-abnormality | increase frequency to monitor trends, efficacy, and side effects | RENDERED: In CKD patients receiving treatments for CKD-MBD, or in whom biochemical abnormalities are identified, it is reasonable to increase the frequency of measurements to monitor for trends and treatment efficacy and side effects | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.2-increase | narrative |
| vitamin-d-measurement | ckd-g3a-g5d | 25(OH)D may be measured in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we suggest that 25(OH)D (calcidiol) levels might be measured | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.3 | narrative |
| vitamin-d-retesting | ckd-g3a-g5d | repeat testing by baseline values and therapeutic interventions | RENDERED: repeated testing determined by baseline values and therapeutic interventions | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.3-retest | narrative |
| vitamin-d-deficiency-treatment | ckd-g3a-g5d | correct deficiency and insufficiency using general-population strategies in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D ... vitamin D deficiency and insufficiency be corrected using treatment strategies recommended for the general population | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.3-correct | narrative |
| trend-based-decisions | ckd-g3a-g5d | base decisions on trends rather than a single laboratory value | RENDERED: therapeutic decisions be based on trends rather than on a single laboratory value | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.4 | narrative |
| combined-assessment-context | ckd-g3a-g5d | take all available CKD-MBD assessments into account | RENDERED: taking into account all available CKD-MBD assessments | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.4-context | narrative |
| calcium-phosphate-joint-use | ckd-g3a-g5d | use individual calcium and phosphate values together rather than Ca x P | RENDERED: individual values of serum calcium and phosphate, evaluated together, be used to guide clinical practice rather than the mathematical construct of calcium-phosphate product (Ca × P) | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.5 | narrative |
| laboratory-assay-reporting | ckd-g3a-g5d | report assay method and changes in method, sample source, or handling | RENDERED: clinical laboratories inform clinicians of the actual assay method in use and report any change in methods, sample source (plasma or serum), or handling specifications | kdigo-2017 | p16 | p16/narrative/recommendation-3.1.6 | narrative |
| bmd-testing | ckd-g3a-g5d-mbd-or-osteoporosis-risk | BMD testing if results affect treatment in CKD G3a-G5D with CKD-MBD evidence and/or osteoporosis risk | RENDERED: In patients with CKD G3a–G5D with evidence of CKD-MBD and/or risk factors for osteoporosis, we suggest BMD testing to assess fracture risk if results will impact treatment decisions | kdigo-2017 | p16 | p16/narrative/recommendation-3.2.1 | narrative |
| bone-biopsy | ckd-g3a-g5d | consider bone biopsy in CKD G3a-G5D if type affects treatment | RENDERED: In patients with CKD G3a–G5D, it is reasonable to perform a bone biopsy if knowledge of the type of renal osteodystrophy will impact treatment decisions | kdigo-2017 | p16 | p16/narrative/recommendation-3.2.2 | narrative |
| bone-turnover-testing | ckd-g3a-g5d | use PTH or bone-specific alkaline phosphatase in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we suggest that measurements of serum PTH or bone-specific alkaline phosphatase can be used to evaluate bone disease | kdigo-2017 | p16 | p16/narrative/recommendation-3.2.3 | narrative |
| bone-turnover-prediction | ckd-g3a-g5d | markedly high or low PTH or bone-specific alkaline phosphatase predicts underlying turnover | RENDERED: because markedly high or low values predict underlying bone turnover | kdigo-2017 | p16 | p16/narrative/recommendation-3.2.3-prediction | narrative |
| collagen-marker-testing | ckd-g3a-g5d | do not routinely measure bone-derived collagen turnover markers in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we suggest not to routinely measure bone-derived turnover markers of collagen synthesis | kdigo-2017 | p16 | p16/narrative/recommendation-3.2.4 | narrative |
| infant-length-monitoring | infants-ckd-g2-g5d | at least quarterly | RENDERED: infants with CKD G2–G5D have their length measured at least quarterly | kdigo-2017 | p17 | p17/narrative/recommendation-3.2.5-infant | narrative |
| child-growth-monitoring | children-ckd-g2-g5d | at least annually | RENDERED: children with CKD G2–G5D should be assessed for linear growth at least annually | kdigo-2017 | p17 | p17/narrative/recommendation-3.2.5-child | narrative |
| calcification-imaging | ckd-g3a-g5d | use lateral abdominal radiograph for vascular and echocardiogram for valvular calcification as CT alternatives | RENDERED: a lateral abdominal radiograph can be used to detect the presence or absence of vascular calcification, and an echocardiogram can be used to detect the presence or absence of valvular calcification, as reasonable alternatives to computed tomography-based imaging | kdigo-2017 | p17 | p17/narrative/recommendation-3.3.1 | narrative |
| calcification-risk | ckd-g3a-g5d-known-calcification | known vascular or valvular calcification in CKD G3a-G5D indicates highest cardiovascular risk | RENDERED: patients with CKD G3a–G5D with known vascular or valvular calcification be considered at highest cardiovascular risk | kdigo-2017 | p17 | p17/narrative/recommendation-3.3.2 | narrative |
| calcification-guided-management | ckd-g3a-g5d-known-calcification | use highest-risk information to guide CKD-MBD management | RENDERED: It is reasonable to use this information to guide the management of CKD-MBD | kdigo-2017 | p17 | p17/narrative/recommendation-3.3.2-management | narrative |
| serial-mbd-assessment | ckd-g3a-g5d | base treatment on serial phosphate, calcium, and PTH assessments in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, treatments of CKD-MBD should be based on serial assessments of phosphate, calcium, and PTH levels | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.1 | narrative |
| phosphate-target | ckd-g3a-g5d | lower elevated phosphate toward normal in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we suggest lowering elevated phosphate levels toward the normal range | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.2 | narrative |
| adult-calcium-target | adults-ckd-g3a-g5d | avoid hypercalcemia in CKD G3a-G5D | RENDERED: In adult patients with CKD G3a–G5D, we suggest avoiding hypercalcemia | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.3-adult | narrative |
| pediatric-calcium-target | children-ckd-g3a-g5d | maintain age-appropriate normal calcium in CKD G3a-G5D | RENDERED: In children with CKD G3a–G5D, we suggest maintaining serum calcium in the age-appropriate normal range | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.3-child | narrative |
| dialysate-calcium | ckd-g5d | 1.25-1.50 mmol/L (2.5-3.0 mEq/L) | RENDERED: using a dialysate calcium concentration between 1.25 and 1.50 mmol/l (2.5 and 3.0 mEq/l) | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.4 | narrative |
| phosphate-treatment-trigger | ckd-g3a-g5d | progressively or persistently elevated phosphate in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, decisions about phosphate-lowering treatment should be based on progressively or persistently elevated serum phosphate | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.5 | narrative |
| calcium-binder-restriction | adults-ckd-g3a-g5d | restrict calcium-based phosphate-binder dose in CKD G3a-G5D | RENDERED: In adult patients with CKD G3a–G5D receiving phosphate-lowering treatment, we suggest restricting the dose of calcium-based phosphate binders | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.6-adult | narrative |
| pediatric-phosphate-therapy-selection | children-ckd-g3a-g5d | base treatment choice on serum calcium in CKD G3a-G5D | RENDERED: children with CKD G3a–G5D, it is reasonable to base the choice of phosphate-lowering treatment on serum calcium levels | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.6-child | narrative |
| aluminum-avoidance | ckd-g3a-g5d | avoid long-term aluminum-containing binders in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we recommend avoiding the long-term use of aluminum-containing phosphate binders | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.7-binder | narrative |
| dialysate-aluminum-avoidance | ckd-g5d | avoid dialysate aluminum contamination in CKD G5D | RENDERED: in patients with CKD G5D, avoiding dialysate aluminum contamination | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.7-dialysate | narrative |
| dietary-phosphate-treatment | ckd-g3a-g5d | limit dietary phosphate for hyperphosphatemia in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D, we suggest limiting dietary phosphate intake in the treatment of hyperphosphatemia | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.8 | narrative |
| dietary-phosphate-source | ckd-g3a-g5d-phosphate-diet | consider animal, vegetable, and additive phosphate sources | RENDERED: It is reasonable to consider phosphate source (e.g., animal, vegetable, additives) in making dietary recommendations | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.8-source | narrative |
| dialytic-phosphate-removal | ckd-g5d | increase dialytic phosphate removal for persistent hyperphosphatemia in CKD G5D | RENDERED: In patients with CKD G5D, we suggest increasing dialytic phosphate removal in the treatment of persistent hyperphosphatemia | kdigo-2017 | p17 | p17/narrative/recommendation-4.1.9 | narrative |
| pth-evaluation-trigger | ckd-g3a-g5-nondialysis | progressively rising or persistently above assay upper normal limit in CKD G3a-G5 | RENDERED: In patients with CKD G3a–G5 not on dialysis ... intact PTH progressively rising or persistently above the upper normal limit for the assay | kdigo-2017 | p17 | p17/narrative/recommendation-4.2.1 | narrative |
| pth-evaluation-factors | ckd-g3a-g5-nondialysis | evaluate hyperphosphatemia, hypocalcemia, high phosphate intake, and vitamin D deficiency | RENDERED: be evaluated for modifiable factors, including hyperphosphatemia, hypocalcemia, high phosphate intake, and vitamin D deficiency | kdigo-2017 | p17 | p17/narrative/recommendation-4.2.1-factors | narrative |
| calcitriol-routine-use | adults-ckd-g3a-g5-nondialysis | do not routinely use calcitriol or vitamin D analogs in CKD G3a-G5 | RENDERED: In adult patients with CKD G3a–G5 not on dialysis, we suggest that calcitriol and vitamin D analogs not be routinely used | kdigo-2017 | p17 | p17/narrative/recommendation-4.2.2-routine | narrative |
| calcitriol-reserved-use | ckd-g4-g5-severe-progressive-hpt | reserve calcitriol or vitamin D analogs for CKD G4-G5 with severe progressive HPT | RENDERED: reserve the use of calcitriol and vitamin D analogs for patients with CKD G4–G5 with severe and progressive hyperparathyroidism | kdigo-2017 | p17 | p17/narrative/recommendation-4.2.2-reserve | narrative |
| pediatric-calcitriol-use | children-ckd | consider calcitriol or vitamin D analogs to maintain age-appropriate normal calcium | RENDERED: In children, calcitriol and vitamin D analogs may be considered to maintain serum calcium levels in the age-appropriate normal range | kdigo-2017 | p17 | p17/narrative/recommendation-4.2.2-child | narrative |
| ipth-target | ckd-g5d | approximately 2-9 times the assay upper normal limit | RENDERED: maintaining iPTH levels in the range of approximately 2 to 9 times the upper normal limit for the assay | kdigo-2017 | p18 | p18/narrative/recommendation-4.2.3-target | narrative |
| ipth-therapy-change | ckd-g5d | marked change in either direction within the 2-9 times range prompts therapy initiation or change | RENDERED: maintaining iPTH levels in the range of approximately 2 to 9 times the upper normal limit for the assay. We suggest that marked changes in PTH levels in either direction within this range prompt an initiation or change in therapy | kdigo-2017 | p18 | p18/narrative/recommendation-4.2.3-change | narrative |
| pth-lowering-therapy | ckd-g5d | calcimimetics, calcitriol, vitamin D analogs, or calcimimetic plus calcitriol or vitamin D analog in CKD G5D | RENDERED: In patients with CKD G5D requiring PTH-lowering therapy, we suggest calcimimetics, calcitriol, or vitamin D analogs, or a combination of calcimimetics with calcitriol or vitamin D analogs | kdigo-2017 | p18 | p18/narrative/recommendation-4.2.4 | narrative |
| parathyroidectomy | ckd-g3a-g5d-severe-hpt-treatment-failure | consider parathyroidectomy after treatment failure in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D with severe hyperparathyroidism (HPT) who fail to respond ... we suggest parathyroidectomy | kdigo-2017 | p18 | p18/narrative/recommendation-4.2.5 | narrative |
| general-population-bone-management | ckd-g1-g2-osteoporosis | manage as general population in CKD G1-G2 | RENDERED: In patients with CKD G1–G2 with osteoporosis and/or high risk of fracture ... management as for the general population | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.1 | narrative |
| general-population-bone-criteria | ckd-g1-g2-osteoporosis | osteoporosis and/or high fracture risk identified by WHO criteria in CKD G1-G2 | RENDERED: In patients with CKD G1–G2 with osteoporosis and/or high risk of fracture, as identified by World Health Organization criteria | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.1-criteria | narrative |
| general-population-bone-management | ckd-g3a-g3b-normal-pth-osteoporosis | treat as general population in CKD G3a-G3b with normal PTH | RENDERED: In patients with CKD G3a–G3b with PTH in the normal range ... treatment as for the general population | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.2 | narrative |
| general-population-bone-criteria | ckd-g3a-g3b-normal-pth-osteoporosis | osteoporosis and/or high fracture risk identified by WHO criteria | RENDERED: with PTH in the normal range and osteoporosis and/or high risk of fracture, as identified by World Health Organization criteria | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.2-criteria | narrative |
| ckd-mbd-bone-treatment | ckd-g3a-g5d-mbd-low-bmd-fracture | account for biochemical abnormalities and CKD progression in CKD G3a-G5D | RENDERED: In patients with CKD G3a–G5D with biochemical abnormalities of CKD-MBD and low BMD and/or fragility fractures | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.3 | narrative |
| ckd-mbd-bone-treatment-factors | ckd-g3a-g5d-mbd-low-bmd-fracture | consider magnitude and reversibility of abnormalities, CKD progression, and bone biopsy | RENDERED: treatment choices take into account the magnitude and reversibility of the biochemical abnormalities and the progression of CKD, with consideration of a bone biopsy | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.3-factors | narrative |
| growth-hormone-treatment | children-adolescents-ckd-g2-g5d-height-deficit | use recombinant human growth hormone in CKD G2-G5D after addressing malnutrition and biochemical abnormalities | RENDERED: In children and adolescents with CKD G2–G5D and related height deficits, we recommend treatment with recombinant human growth hormone | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.4 | narrative |
| growth-hormone-prerequisites | children-adolescents-ckd-g2-g5d-height-deficit | additional growth desired after addressing malnutrition and CKD-MBD biochemical abnormalities | RENDERED: when additional growth is desired, after first addressing malnutrition and biochemical abnormalities of CKD-MBD | kdigo-2017 | p18 | p18/narrative/recommendation-4.3.4-prerequisites | narrative |
| immediate-posttransplant-monitoring | immediate-posttransplant | at least weekly until stable | RENDERED: measuring serum calcium and phosphate at least weekly, until stable | kdigo-2017 | p18 | p18/narrative/recommendation-5.1 | narrative |
| transplant-monitoring-frequency-basis | post-immediate-transplant | base calcium, phosphate, and PTH frequency on abnormalities and CKD progression | RENDERED: In patients after the immediate post–kidney transplant period, it is reasonable to base the frequency of monitoring serum calcium, phosphate, and PTH on the presence and magnitude of abnormalities, and the rate of progression of CKD | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-basis | narrative |
| calcium-phosphate-monitoring | ckd-g1t-g3bt | every 6-12 months | RENDERED: In CKD G1T–G3bT, for serum calcium and phosphate, every 6–12 months | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g1t-g3bt-ca-p | narrative |
| pth-monitoring | ckd-g1t-g3bt | once, then by baseline and CKD progression | RENDERED: and for PTH, once, with subsequent intervals depending on baseline level and CKD progression | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g1t-g3bt-pth | narrative |
| calcium-phosphate-monitoring | ckd-g4t | every 3-6 months | RENDERED: In CKD G4T, for serum calcium and phosphate, every 3–6 months | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g4t-ca-p | narrative |
| pth-monitoring | ckd-g4t | every 6-12 months | RENDERED: and for PTH, every 6–12 months | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g4t-pth | narrative |
| calcium-phosphate-monitoring | ckd-g5t | every 1-3 months | RENDERED: In CKD G5T, for serum calcium and phosphate, every 1–3 months | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g5t-ca-p | narrative |
| pth-monitoring | ckd-g5t | every 3-6 months | RENDERED: and for PTH, every 3–6 months | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-g5t-pth | narrative |
| alkaline-phosphatase-monitoring | ckd-g3at-g5t | annually, or more often with elevated PTH | RENDERED: In CKD G3aT–G5T, measurement of alkaline phosphatases annually, or more frequently in the presence of elevated PTH | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-alp | narrative |
| transplant-monitoring-frequency-basis | ckd-treatment-or-abnormality | increase frequency to monitor efficacy and side effects after transplant | RENDERED: In CKD patients receiving treatments for CKD-MBD, or in whom biochemical abnormalities are identified, it is reasonable to increase the frequency of measurements to monitor for efficacy and side effects | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-increase | narrative |
| transplant-abnormality-management | post-immediate-transplant | manage abnormalities as for CKD G3a-G5 | RENDERED: It is reasonable to manage these abnormalities as for patients with CKD G3a–G5 | kdigo-2017 | p18 | p18/narrative/recommendation-5.2-management | narrative |
| transplant-vitamin-d-measurement | ckd-g1t-g5t | 25(OH)D may be measured in CKD G1T-G5T | RENDERED: In patients with CKD G1T–G5T, we suggest that 25(OH)D (calcidiol) levels might be measured | kdigo-2017 | p18 | p18/narrative/recommendation-5.3 | narrative |
| transplant-vitamin-d-retesting | ckd-g1t-g5t | repeat testing by baseline values and interventions | RENDERED: repeated testing determined by baseline values and interventions | kdigo-2017 | p18 | p18/narrative/recommendation-5.3-retest | narrative |
| transplant-vitamin-d-treatment | ckd-g1t-g5t | correct deficiency as in general population in CKD G1T-G5T | RENDERED: In patients with CKD G1T–G5T, we suggest that vitamin D deficiency and insufficiency be corrected using treatment strategies recommended for the general population | kdigo-2017 | p18 | p18/narrative/recommendation-5.4 | narrative |
| transplant-bmd-testing | ckd-g1t-g5t-osteoporosis-risk | BMD testing in CKD G1T-G5T if results alter therapy | RENDERED: In patients with CKD G1T–G5T with risk factors for osteoporosis, we suggest that BMD testing be used to assess fracture risk if results will alter therapy | kdigo-2017 | p19 | p19/narrative/recommendation-5.5 | narrative |
| posttransplant-bone-treatment-window | first-12-months-transplant-low-bmd | first 12 months and eGFR >approximately 30 mL/min/1.73 m² | RENDERED: In patients in the first 12 months after kidney transplant with an estimated glomerular filtration rate greater than approximately 30 ml/min/1.73 m² and low BMD | kdigo-2017 | p19 | p19/narrative/recommendation-5.6-window | narrative |
| posttransplant-bone-treatment-options | first-12-months-transplant-low-bmd | consider vitamin D, calcitriol/alfacalcidol, and/or antiresorptive agents | RENDERED: we suggest that treatment with vitamin D, calcitriol/alfacalcidol, and/or antiresorptive agents be considered | kdigo-2017 | p19 | p19/narrative/recommendation-5.6-options | narrative |
| posttransplant-bone-treatment-selection | first-12-months-transplant-low-bmd | use abnormal calcium, phosphate, PTH, alkaline phosphatase, and 25(OH)D | RENDERED: treatment choices be influenced by the presence of CKD-MBD, as indicated by abnormal levels of calcium, phosphate, PTH, alkaline phosphatases, and 25(OH)D | kdigo-2017 | p19 | p19/narrative/recommendation-5.6-selection | narrative |
| posttransplant-bone-biopsy | first-12-months-transplant-low-bmd | consider bone biopsy to guide treatment | RENDERED: It is reasonable to consider a bone biopsy to guide treatment | kdigo-2017 | p19 | p19/narrative/recommendation-5.6-biopsy | narrative |
| posttransplant-treatment-evidence-window | first-12-months-transplant-low-bmd | insufficient data after first 12 months | RENDERED: There are insufficient data to guide treatment after the first 12 months | kdigo-2017 | p19 | p19/narrative/recommendation-5.6-after | narrative |
| transplant-low-bmd-management | ckd-g4t-g5t-low-bmd | manage CKD G4T-G5T as CKD G4-G5 not on dialysis | RENDERED: In patients with CKD G4T–G5T with known low BMD, we suggest management as for patients with CKD G4–G5 not on dialysis | kdigo-2017 | p19 | p19/narrative/recommendation-5.7 | narrative |
| adult-calcium-target | adults-ckd-g3a-g5d | mild asymptomatic hypocalcemia may be tolerated to avoid inappropriate calcium loading | Mild and asymptomatic hypocalcemia (e.g., in the context of calcimimetic treatment) can be tolerated in order to avoid inappropriate calcium loading in adults | kdigo-2017 | p20 | p20/narrative/adult-mild-hypocalcemia | narrative |
| pediatric-dxa-adjustment | children-short-stature-ckd | adjust DXA results for bone size | RENDERED: Given that DXA measures of areal BMD (g/cm²) underestimate volumetric BMD (g/cm³) in children with short stature, DXA results should be adjusted for bone size | kdigo-2017 | p24 | p24/narrative/pediatric-dxa-adjustment | narrative |
| bone-biopsy-pth-trend | ckd-g3a-g5d | consider bone biopsy when PTH trends are inconsistent | RENDERED: when trends in PTH are inconsistent, a bone biopsy should be considered | kdigo-2017 | p25 | p25/narrative/bone-biopsy-pth-trend | narrative |
| bone-biopsy-indications | ckd-g3a-g5d | consider biopsy for unexplained fractures, refractory hypercalcemia, suspected osteomalacia, atypical PTH-therapy response, or progressive BMD decline | A bone biopsy should also be considered in patients with unexplained fractures, refractory hypercalcemia, suspicion of osteomalacia, an atypical response to standard therapies for elevated PTH, or progressive decreases in BMD despite standard therapy | kdigo-2017 | p25 | p25/narrative/bone-biopsy-indications | narrative |
| antiresorptive-biopsy-caveat | ckd-g3a-g5d-mbd-low-bmd-fracture | inability to perform biopsy may not justify withholding antiresorptive therapy from high-fracture-risk patients | the inability to perform a bone biopsy may not justify withholding antiresorptive therapy to patients at high risk of fracture | kdigo-2017 | p25 | p25/narrative/antiresorptive-biopsy-caveat | narrative |
| antiresorptive-prerequisites | ckd-g3a-g5d-mbd-low-bmd-fracture | use antiresorptives cautiously and address renal osteodystrophy first | RENDERED: it is still prudent that these drugs be used with caution and that the underlying renal osteodystrophy be addressed first | kdigo-2017 | p25 | p25/narrative/antiresorptive-prerequisites | narrative |
| antiresorptive-aki-risk | ckd-g3a-g5 | consider acute kidney injury risk in CKD G3a-G5 | RENDERED: additional side effects such as acute kidney injury may also merit consideration in CKD G3a to G5 | kdigo-2017 | p25 | p25/narrative/antiresorptive-aki-risk | narrative |
| bone-biopsy-uncertain-etiology | ckd-g3a-g5d | consider biopsy when the etiology of symptoms and biochemical abnormalities is uncertain and results may change therapy | RENDERED: In summary, bone biopsy is the gold standard for the assessment of renal osteodystrophy and should be considered in patients in whom the etiology of clinical symptoms and biochemical abnormalities is in question, and the results may lead to changes in therapy | kdigo-2017 | p25 | p25/narrative/bone-biopsy-uncertain-etiology | narrative |
| adult-calcium-target | adults-ckd-g3a-g5d | individualize correction and address significant or symptomatic hypocalcemia | RENDERED: the Work Group emphasizes an individualized approach to the treatment of hypocalcemia rather than recommending the correction of hypocalcemia for all patients. However, significant or symptomatic hypocalcemia should still be addressed | kdigo-2017 | p28 | p28/narrative/adult-hypocalcemia-management | narrative |
| dialysate-calcium-selection | ckd-g5d | individualize dialysate calcium concentration | RENDERED: Their data confirmed the results of previous papers and also support individualization of dialysate calcium concentrations as recommended previously by the Work Group | kdigo-2017 | p29 | p29/narrative/dialysate-calcium-individualization | narrative |
| calcium-binder-maximum | adults-ckd-g3a-g5d | no explicit maximum dose; use individual physician judgment | RENDERED: the Work Group could not make an explicit recommendation about a maximum dose of calcium-based binders, preferring to leave this to the judgment of individual physicians | kdigo-2017 | p31 | p31/narrative/calcium-binder-maximum | narrative |
| hidden-phosphate-sources | ckd-g3a-g5d-phosphate-diet | include dietary supplements and over-the-counter or prescription medications as hidden sources | RENDERED: Dietary supplements and over-the-counter or prescription medications are hidden sources of phosphate. They may contain phosphate salts within their inactive ingredients. | kdigo-2017 | p32 | p32/narrative/hidden-phosphate-sources | narrative |
| phosphate-food-selection | ckd-g3a-g5d-phosphate-diet | teach absorbable-phosphate food choices and favor fresh or homemade over processed foods | RENDERED: include education about the best food choices as they relate to absorbable phosphate. Additionally, it is important for patients to be guided toward fresh and homemade foods rather than processed foods in order to avoid additives. | kdigo-2017 | p32 | p32/narrative/phosphate-food-selection | narrative |
| phosphate-education | ckd-g3a-g5d-phosphate-diet | substantiate phosphate sources and focus education on best choices | RENDERED: phosphate sources should be better substantiated and patient education should focus on best choices | kdigo-2017 | p33 | p33/narrative/phosphate-education | narrative |
| dietary-phosphate-protein-caveat | ckd-g3a-g5d-phosphate-diet | do not compromise adequate protein intake | efforts to restrict dietary phosphate must not compromise adequate protein intake | kdigo-2017 | p33 | p33/narrative/dietary-phosphate-protein | narrative |
| calcitriol-initiation-titration | ckd-g3a-g5-severe-progressive-shpt | start low independent of initial PTH, titrate by PTH response, and avoid hypercalcemia | RENDERED: If initiated for severe and progressive SHPT, calcitriol or vitamin D analogs should be started with low doses, independent of the initial PTH concentration, and then titrated based on the PTH response. Hypercalcemia should be avoided. | kdigo-2017 | p36 | p36/narrative/calcitriol-initiation | narrative |
| pth-lowering-selection | ckd-g5d | guide choice by concomitant therapies, current calcium and phosphate, and dialysate calcium concentration | RENDERED: The individual choice should continue to be guided by considerations about concomitant therapies and the present calcium and phosphate levels. In addition, the choice of dialysate calcium concentrations will impact on serum PTH levels. | kdigo-2017 | p37 | p37/narrative/pth-lowering-selection | narrative |
| pediatric-pth-lowering-caution | children-pth-lowering-therapy | use cautiously to avoid hypocalcemia | RENDERED: PTH-lowering therapies should be used with caution in children to avoid hypocalcemia | kdigo-2017 | p38 | p38/narrative/pediatric-pth-caution | narrative |
| ckd-mbd-bone-treatment-risks | ckd-g3a-g5d-mbd-low-bmd-fracture | consider antiresorptive worsening of low turnover and denosumab-induced hypocalcemia | RENDERED: their specific side effects must also be taken into account (e.g., antiresorptives will exacerbate low bone turnover, denosumab may induce significant hypocalcemia) | kdigo-2017 | p39 | p39/narrative/bone-treatment-risks | narrative |
| bone-phenotype-diagnostic-certainty | ckd-g3a-g5d-mbd-low-bmd-fracture | weigh administration risk against accuracy of the underlying bone-phenotype diagnosis | RENDERED: the risk of their administration must be weighed against the accuracy of the diagnosis of the underlying bone phenotype | kdigo-2017 | p39 | p39/narrative/bone-phenotype-diagnostic-certainty | narrative |
| transplant-cinacalcet-approval | kidney-transplant-recipients | not approved for treatment of hyperparathyroidism | RENDERED: Cinacalcet is not approved for the treatment of hyperparathyroidism in kidney transplant recipients | kdigo-2017 | p41 | p41/narrative/transplant-cinacalcet-approval | narrative |
| transplant-cinacalcet-mineralization | kidney-transplant-recipients | no beneficial impact on bone mineralization shown | RENDERED: cinacalcet so far has failed to show a beneficial impact on bone mineralization in the transplant population | kdigo-2017 | p41 | p41/narrative/transplant-cinacalcet-mineralization | narrative |
| transplant-denosumab-bmd | de-novo-kidney-transplant-recipients | effectively increased BMD | RENDERED: Denosumab was recently shown to effectively increase BMD in de novo kidney transplant recipients | kdigo-2017 | p41 | p41/narrative/transplant-denosumab-bmd | narrative |
| transplant-denosumab-uti | de-novo-kidney-transplant-recipients | increased rate of urinary tract infections | RENDERED: an increased rate of urinary tract infections was observed | kdigo-2017 | p41 | p41/narrative/transplant-denosumab-uti | narrative |

## Conflicts

CONFLICT: adult-calcium-target — `avoid hypercalcemia in CKD G3a-G5D`; `individualize correction and address significant or symptomatic hypocalcemia`; `mild asymptomatic hypocalcemia may be tolerated to avoid inappropriate calcium loading`. The first is the current upper-side target, the second preserves correction for clinically important low calcium, and the third permits a mild asymptomatic low value when correction would create inappropriate calcium loading.

## Coverage

The source is `bound`: marker records delimit recommendation-shaped text but do not
prove a complete recommendation denominator. The artifact contains 55 marker records
under 48 distinct locators. None is discharged by a recommendation-backed threshold
row because the current complete recommendation summary on pages 16-19 is outside the
marker artifact; those current rows therefore use narrative locators. Every bound marker
below was read and is a historical renumbering statement, a superseded comparison-table
statement explicitly labeled as such, a duplicate current statement, a rationale
cross-reference, a duplicate body occurrence, or study discussion with no additional
current patient-action decision point beyond the rows above. Pages 20-22 were treated as
a mixed comparison: current 2017 text and rationale remain current, while the neighboring
2009 comparison statements are superseded where the table says the recommendation was
revised, removed, combined, or renumbered.

- `p19/recommendation/4.1.6` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/4.1.7` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/4.1.8` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/4.1.9` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/4.3.4` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/4.3.5` - historical renumbering statement, not an additional current decision point
- `p19/recommendation/5.7` - historical renumbering statement, not an additional current decision point
- `p20/recommendation/4.1.2` - comparison or rationale cross-reference with no additional current decision point
- `p21/recommendation/4.2.4` - comparison or rationale cross-reference with no additional current decision point
- `p22/recommendation/3.2.2` - comparison or rationale cross-reference with no additional current decision point
- `p22/recommendation/4.1.6` - historical renumbering statement, not an additional current decision point
- `p22/recommendation/4.1.7` - historical renumbering statement, not an additional current decision point
- `p22/recommendation/4.1.8` - historical renumbering statement, not an additional current decision point
- `p22/recommendation/4.1.9` - historical renumbering statement, not an additional current decision point
- `p22/recommendation/4.3.3` - comparison or rationale cross-reference with no additional current decision point
- `p22/recommendation/4.3.4` - superseded 2009 comparison statement, not a current 2017 decision point
- `p22/recommendation/4.3.5` - historical renumbering statement, not an additional current decision point
- `p22/recommendation/5.5` - superseded 2009 comparison statement, not a current 2017 decision point
- `p22/recommendation/5.7` - superseded 2009 comparison statement, not a current 2017 decision point
- `p22/recommendation/5.8` - historical renumbering statement, not an additional current decision point
- `p25/recommendation/3.2.1` - rationale cross-reference with no additional current decision point
- `p26/recommendation/3.1.4` - rationale cross-reference with no additional current decision point
- `p26/recommendation/4.1.1` - rationale cross-reference or duplicate occurrence with no additional current decision point
- `p27/recommendation/4.1.5` - rationale cross-reference with no additional current decision point
- `p27/recommendation/4.1.8` - rationale cross-reference with no additional current decision point
- `p29/recommendation/4.1.4` - rationale cross-reference with no additional current decision point
- `p29/recommendation/4.1.5` - rationale cross-reference with no additional current decision point
- `p30/recommendation/4.1.2` - rationale cross-reference or duplicate occurrence with no additional current decision point
- `p30/recommendation/4.1.4` - rationale cross-reference with no additional current decision point
- `p30/recommendation/4.1.5` - rationale cross-reference or duplicate occurrence with no additional current decision point
- `p30/recommendation/4.1.6` - rationale cross-reference with no additional current decision point
- `p31/recommendation/4.1.3` - rationale cross-reference or duplicate occurrence with no additional current decision point
- `p31/recommendation/4.1.5` - rationale cross-reference with no additional current decision point
- `p31/recommendation/4.1.6` - rationale cross-reference with no additional current decision point
- `p32/recommendation/4.1.7` - historical-number cross-reference with no additional current decision point
- `p34/recommendation/3.1.3` - rationale cross-reference with no additional current decision point
- `p35/recommendation/4.2.2` - rationale cross-reference with no additional current decision point
- `p36/recommendation/4.1.3` - rationale cross-reference with no additional current decision point
- `p37/recommendation/4.2.4` - rationale cross-reference with no additional current decision point
- `p37/recommendation/4.2.5` - rationale cross-reference with no additional current decision point
- `p39/recommendation/3.2.2` - rationale cross-reference with no additional current decision point
- `p39/recommendation/4.3.3` - rationale cross-reference with no additional current decision point
- `p39/recommendation/4.3.4` - removed 2009 recommendation, not a current 2017 decision point
- `p40/recommendation/3.2.1` - rationale cross-reference with no additional current decision point
- `p40/recommendation/3.2.2` - rationale cross-reference with no additional current decision point
- `p40/recommendation/5.5` - rationale cross-reference with no additional current decision point
- `p40/recommendation/5.7` - rationale cross-reference with no additional current decision point
- `p41/recommendation/5.5` - rationale cross-reference with no additional current decision point
