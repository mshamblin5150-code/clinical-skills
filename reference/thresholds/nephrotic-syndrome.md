# Nephrotic syndrome in children - threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in the
threshold-sheet README.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2025-pediatric-ns | KDIGO | KDIGO/KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children | guideline | 2025 Clinical Practice Guideline | 2025-05 | https://doi.org/10.1016/j.kint.2024.11.007 | stated | bound |

## Scope

**Read:** all 50 source pages. This included cover matter, contents and supplementary-table
index, reference keys, CKD nomenclature and proteinuria tables, abbreviations, notice,
foreword, membership, abstract, every summary recommendation and practice point, the complete
clinical chapter and rendered Figures 1-5, methods, disclosures, acknowledgments, and the
reference list. Rows retain definitions, applicability boundaries, diagnostic branches,
regimens, doses, durations, tapers, monitoring, stop rules, adverse-effect boundaries, and
other actions that can change care.

**Not read:** nothing in the source page range. Pages marked `blind` were read to confirm they
contain no patient-changing clinical prose; reference pages were checked as citation lists and
are exempt from clinical extraction.

| span | pages | read |
| --- | --- | --- |
| covers | 1-2 | read 2026-09-01; blind 2026-09-01 |
| contents and supplementary-material index | 3-7 | read 2026-09-01; blind 2026-09-01 |
| executive committee and reference keys | 8-9 | read 2026-09-01; blind 2026-09-01 |
| CKD and proteinuria classification tables | 10-11 | yes |
| abbreviations, notice, foreword, membership, and abstract | 12-16 | read 2026-09-01; blind 2026-09-01 |
| summary recommendations and practice points, all action-accounted below as duplicate or fragment occurrences | 17-21 | read 2026-09-01; blind 2026-09-01 |
| complete clinical chapter, including rendered Figures 1-5 | 22-36 | yes |
| guideline-development methods | 37-42 | read 2026-09-01; blind 2026-09-01 |
| biographic disclosures and acknowledgments | 43-47 | read 2026-09-01; blind 2026-09-01 |
| references | 48-50 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| children-age-1-to-18 | children with nephrotic syndrome aged 1-18 years |
| children-under-1 | children younger than 1 year fulfilling the definition of nephrotic syndrome |
| children-assessed-for-ckd | children being assessed for CKD duration and GFR category |
| children-assessed-for-proteinuria | children being assessed for albuminuria or proteinuria category |
| suspected-pediatric-ns | children aged 1-18 years being assessed for nephrotic syndrome |
| pediatric-ns-remission-assessment | children with nephrotic syndrome being assessed for remission |
| pediatric-ns-relapse-assessment | children previously in complete remission being assessed for relapse |
| pediatric-ns-course-classification | children with nephrotic syndrome being classified by response or relapse course |
| new-onset-pediatric-ns | children aged 1-18 years with new-onset nephrotic syndrome |
| new-onset-under-12-typical | children younger than 12 years with new-onset nephrotic syndrome and no syndromic features or family history |
| new-onset-over-12-or-atypical | children older than 12 years or with syndromic features or family history at nephrotic-syndrome onset |
| new-onset-at-least-12-or-atypical | children at least 12 years old or with atypical features being considered for kidney biopsy |
| new-onset-no-response | children with new-onset nephrotic syndrome who do not respond to the initial daily glucocorticoid course |
| atypical-pediatric-ns | children with atypical nephrotic-syndrome features or course |
| pediatric-ns-family-or-syndromic | children with nephrotic syndrome and a family history or syndromic features |
| ssns-initial-treatment | children with steroid-sensitive nephrotic syndrome receiving initial glucocorticoid treatment |
| young-delayed-responder | children aged 1-6 years with remission 10-15 days after starting prednisolone |
| rapid-initial-responder | children with remission within 7 days of starting prednisolone |
| frns-or-sdns | children with frequently relapsing or steroid-dependent nephrotic syndrome |
| frns-sdns-selected-infection | children with FRNS or SDNS already taking low-dose alternate-day prednisolone and repeated infection-associated relapse or significant glucocorticoid morbidity |
| ssns-relapse | children with steroid-sensitive nephrotic syndrome being treated for relapse |
| frns-no-serious-steroid-toxicity | children with frequently relapsing nephrotic syndrome without serious glucocorticoid adverse effects |
| frns-serious-toxicity-or-sdns | children with FRNS and serious glucocorticoid adverse effects or any child with SDNS |
| steroid-sparing-initiation | children starting a glucocorticoid-sparing agent for FRNS or SDNS |
| frns-agent-selection | children with frequently relapsing nephrotic syndrome selecting a glucocorticoid-sparing agent |
| sdns-agent-selection | children with steroid-dependent nephrotic syndrome selecting a glucocorticoid-sparing agent |
| ssns-on-cni | children with steroid-sensitive nephrotic syndrome receiving a calcineurin inhibitor |
| ssns-on-cyclosporine | children with steroid-sensitive nephrotic syndrome receiving cyclosporine |
| ssns-on-tacrolimus | children with steroid-sensitive nephrotic syndrome receiving tacrolimus |
| ssns-on-cyclophosphamide | children with steroid-sensitive nephrotic syndrome receiving oral cyclophosphamide |
| ssns-on-levamisole | children with steroid-sensitive nephrotic syndrome receiving levamisole |
| ssns-on-mmf | children with steroid-sensitive nephrotic syndrome receiving mycophenolate mofetil |
| difficult-frns-sdns-rituximab | children with continuing frequent relapses despite optimal oral therapy or serious treatment adverse effects being considered for rituximab |
| complicated-frns-sdns-post-rituximab | children with complicated FRNS or SDNS after rituximab |
| srns-confirmation | children without complete remission after 4 weeks of standard daily prednisone or prednisolone |
| srns-all | children with steroid-resistant nephrotic syndrome |
| srns-genetic | children with a genetic cause of steroid-resistant nephrotic syndrome |
| srns-no-genetic-cause | children with steroid-resistant nephrotic syndrome without an identified genetic cause |
| srns-cni-treatment | children with steroid-resistant nephrotic syndrome receiving a calcineurin inhibitor |
| srns-cni-nonresponse | children with steroid-resistant nephrotic syndrome without at least partial response to a calcineurin inhibitor |
| srns-stable-cni-remission | children with steroid-resistant nephrotic syndrome in stable remission on a calcineurin inhibitor |
| srns-low-egfr-or-after-cni-remission | children with SRNS and eGFR below 30 ml/min/1.73 m2 or stable remission for more than 1 year on a calcineurin inhibitor |
| srns-nephrotic-rituximab | children with SRNS and nephrotic-range proteinuria receiving rituximab |
| srns-identified-coq-pathway | children with steroid-resistant nephrotic syndrome and an identified COQ2, COQ6, or ADCK4 mutation |
| cni-resistant-srns | children with calcineurin-inhibitor-resistant steroid-resistant nephrotic syndrome |
| congenital-infantile-ns | children with congenital or infantile nephrotic syndrome younger than 1 year |
| pediatric-ns-biopsy-consideration | children with nephrotic syndrome being considered for kidney biopsy |
| pediatric-ns-genetic-testing | children with nephrotic syndrome being considered for genetic testing |
| ssns-normal-vitamin-d | children with steroid-sensitive nephrotic syndrome and normal vitamin D levels |
| frns-sdns-or-vitamin-d-deficiency | children with FRNS, SDNS, or known vitamin D deficiency |
| pediatric-ns-no-gastro-risk | children with nephrotic syndrome without gastrotoxicity risk factors or gastric symptoms |
| untreated-or-unresponsive-ns | children with nephrotic syndrome who are untreated or fail to respond to treatment |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-duration | minimum duration defining CKD |
| gfr-category | GFR category cutoffs |
| aer-category | albumin excretion rate category cutoffs |
| per-category | protein excretion rate category cutoffs |
| acr-category | albumin-to-creatinine ratio category cutoffs |
| pcr-category | protein-to-creatinine ratio category cutoffs |
| protein-strip-category | protein reagent-strip categories |
| guideline-age-scope | age applicability of this guideline |
| diagnosis-definition-reference | practice-point direction to use the clinical definitions in Figure 1 |
| nephrotic-range-proteinuria | urine protein thresholds defining nephrotic-range proteinuria |
| nephrotic-syndrome-definition | proteinuria plus albumin or edema definition |
| complete-remission-definition | urine protein threshold and consecutive-day duration for complete remission |
| partial-remission-definition | urine protein and albumin range for partial remission |
| relapse-dipstick-definition | dipstick threshold and duration commonly defining relapse |
| dipstick-semiquantitation | typical protein dipstick concentration bands |
| ssns-definition | glucocorticoid-response interval defining steroid sensitivity |
| infrequent-relapse-definition | relapse-count windows defining infrequently relapsing disease |
| frequent-relapse-definition | relapse-count windows defining frequently relapsing disease |
| steroid-dependent-definition | relapse timing defining steroid dependence |
| srns-definition | glucocorticoid-response interval defining steroid resistance |
| confirmation-period | timing and actions for partial response at 4 weeks |
| ssns-late-responder-definition | complete-remission interval defining a late responder |
| cni-responsive-srns-definition | CNI partial- and complete-response intervals |
| cni-resistant-srns-definition | CNI nonresponse interval |
| multidrug-resistant-srns-definition | duration and number of mechanistically distinct agents defining multidrug resistance |
| secondary-srns-definition | relapse nonresponse interval defining secondary resistance |
| initial-biopsy-strategy | initial biopsy action by response and atypical course |
| new-onset-treatment-routing | treatment and diagnostic routing from new-onset nephrotic syndrome |
| onset-biopsy-indications | atypical onset features prompting biopsy |
| later-biopsy-indications | later response, kidney-function, and exposure triggers for biopsy |
| initial-treatment-duration | 8-week versus 12-week initial glucocorticoid courses |
| initial-daily-prednisone-dose | initial daily prednisone or prednisolone dose and maximum |
| initial-alternate-day-dose | initial alternate-day prednisone or prednisolone dose and maximum |
| prolonged-initial-course-boundary | patient subgroup and interval where a 16-24-week course may be beneficial |
| rapid-response-standard-course | initial-course duration favored after rapid remission |
| infection-prophylactic-steroid-routine | routine daily glucocorticoid action during infections |
| selected-infection-extra-doses | selected infection-triggered extra prednisone or prednisolone doses |
| selected-infection-daily-course-evidence | narrative selected-case daily prednisone or prednisolone duration during infection |
| relapse-daily-prednisone | relapse daily dose, maximum, and remission endpoint |
| relapse-alternate-day-prednisone | post-remission relapse dose, maximum, and duration |
| relapse-toxicity-adjustment | taper and steroid-sparing adjustment for glucocorticoid toxicity |
| low-dose-relapse-prevention | alternate-day prednisone or prednisolone ceiling for relapse prevention |
| steroid-sparing-indication | indication for glucocorticoid-sparing therapy |
| steroid-sparing-overlap | remission prerequisite and glucocorticoid overlap duration |
| steroid-sparing-choice | preferred agent families by FRNS versus SDNS |
| cni-ssns-duration | minimum CNI duration in steroid-sensitive disease |
| cni-creatinine-stop-rule | creatinine rise threshold, dose reduction, and stop action |
| cni-formulation-frequency | formulation-dependent once-daily CNI option |
| cni-target-evidence-boundary | provenance and uncertainty of CNI trough targets in nephrotic syndrome |
| cni-proteinuria-titration | individualized CNI titration against proteinuria and creatinine |
| cni-agent-preference | cyclosporine and tacrolimus preference boundaries based on adverse-effect risk |
| cyclosporine-ssns-dose | cyclosporine starting dose and dosing frequency |
| cyclosporine-ssns-trough | cyclosporine 12-hour trough target |
| tacrolimus-ssns-dose | tacrolimus starting dose and dosing frequency |
| tacrolimus-ssns-trough | tacrolimus 12-hour trough target |
| young-child-cyclosporine-frequency | cyclosporine dosing option for children younger than 6 years |
| cyclophosphamide-ssns-course | oral cyclophosphamide dose, duration, and cumulative maximum |
| cyclophosphamide-monitoring | CBC monitoring and second-course boundary |
| levamisole-dose | levamisole dose, frequency, and maximum |
| levamisole-duration | minimum levamisole duration |
| levamisole-monitoring | CBC, liver enzyme, and ANCA monitoring intervals and stop triggers |
| mmf-ssns-dose | MMF starting dose and divided frequency |
| mmf-ssns-duration | minimum MMF duration |
| mmf-auc-target | mycophenolic-acid area-under-curve target |
| mycophenolate-equivalence | sodium mycophenolate to MMF equivalent dose |
| rituximab-ssns-dose | rituximab dose and dose-count range |
| rituximab-screening-monitoring | pre-rituximab infection screening and immune monitoring |
| post-rituximab-mmf | MMF action after rituximab in complicated FRNS or SDNS |
| srns-confirmation-treatment | treatment during weeks 4-6 before confirming SRNS |
| srns-genetic-testing-action | genetic testing action and immunosuppression boundary |
| srns-comprehensive-gene-panel | comprehensive gene-panel method for all children with SRNS |
| genetic-ubiquinone-action | genotype-specific ubiquinone supplementation evidence |
| prolonged-proteinuria-supportive-care | conservative kidney-protection and pediatric kidney-replacement boundary |
| srns-initial-second-line | initial second-line therapy choice |
| srns-cni-dose-trough | cyclosporine and tacrolimus starting doses and trough targets |
| srns-cni-response-stop | partial-response deadline and discontinuation action |
| srns-cni-duration | minimum CNI duration after response |
| srns-glucocorticoid-regimen | methylprednisolone pulses and oral taper used with a CNI |
| srns-low-dose-prednisone | low-dose alternate-day prednisone used with a CNI |
| srns-cyclophosphamide-boundary | cyclophosphamide treatment boundary |
| srns-mmf-regimen | MMF dose and duration after stable CNI remission |
| srns-rituximab-regimen | rituximab dose and two-infusion option |
| srns-rituximab-screening-monitoring | hepatitis B screening and IgG-replacement monitoring for SRNS rituximab |
| srns-low-egfr-mmf | eGFR and remission-duration boundaries for MMF consideration |
| cni-resistant-trial-referral | trial referral action for CNI-resistant SRNS |
| biopsy-age-trigger | age trigger for kidney biopsy |
| biopsy-cni-exposure | CNI exposure duration prompting biopsy consideration |
| genetic-testing-indications | disease and family-history indications for genetic testing |
| vitamin-d-calcium-action | supplementation action by disease and vitamin D status |
| gastroprotection-boundary | proton-pump-inhibitor prophylaxis boundary |
| vaccination-evidence-boundary | vaccination action stated without a product or schedule |
| untreated-ns-complication-risk | untreated disease risks informing treatment choice |
| glucocorticoid-harms | glucocorticoid adverse-effect profile |
| steroid-sparing-harms | major adverse-effect profile of glucocorticoid-sparing agents |
| cni-comparative-harms | cyclosporine versus tacrolimus adverse-effect differences |
| rituximab-long-term-harm-uncertainty | pediatric age and repeat-course long-term safety boundary |
| special-situations-principles | practice-point direction to apply Figure 5 principles |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-duration | children-assessed-for-ckd | abnormalities of kidney structure or function for at least 3 months | "RENDERED: CKD is defined as abnormalities of kidney structure or function, present for a minimum of 3 months" | kdigo-2025-pediatric-ns | p10 | p10/figure/ckd-duration | figure |
| gfr-category | children-assessed-for-ckd | G1 >=90; G2 60-89; G3a 45-59; G3b 30-44; G4 15-29; G5 <15 ml/min/1.73 m2 | "RENDERED: GFR categories (ml/min/1.73 m2): G1 >=90; G2 60-89; G3a 45-59; G3b 30-44; G4 15-29; G5 <15" | kdigo-2025-pediatric-ns | p10 | p10/figure/gfr-categories | figure |
| aer-category | children-assessed-for-proteinuria | A1 <30 mg/d; A2 30-300 mg/d; A3 >300 mg/d | "RENDERED: AER (mg/d): A1 <30; A2 30-300; A3 >300" | kdigo-2025-pediatric-ns | p11 | p11/table/aer-categories | table |
| per-category | children-assessed-for-proteinuria | A1 <150 mg/d; A2 150-500 mg/d; A3 >500 mg/d | "RENDERED: PER (mg/d): A1 <150; A2 150-500; A3 >500" | kdigo-2025-pediatric-ns | p11 | p11/table/per-categories | table |
| acr-category | children-assessed-for-proteinuria | A1 <3 mg/mmol and <30 mg/g; A2 3-30 mg/mmol and 30-300 mg/g; A3 >30 mg/mmol and >300 mg/g | "RENDERED: ACR: A1 <3 mg/mmol, <30 mg/g; A2 3-30 mg/mmol, 30-300 mg/g; A3 >30 mg/mmol, >300 mg/g" | kdigo-2025-pediatric-ns | p11 | p11/table/acr-categories | table |
| pcr-category | children-assessed-for-proteinuria | A1 <15 mg/mmol and <150 mg/g; A2 15-50 mg/mmol and 150-500 mg/g; A3 >50 mg/mmol and >500 mg/g | "RENDERED: PCR: A1 <15 mg/mmol, <150 mg/g; A2 15-50 mg/mmol, 150-500 mg/g; A3 >50 mg/mmol, >500 mg/g" | kdigo-2025-pediatric-ns | p11 | p11/table/pcr-categories | table |
| protein-strip-category | children-assessed-for-proteinuria | A1 negative to trace; A2 trace to positive; A3 positive or greater | "RENDERED: Protein reagent strip: A1 Negative to trace; A2 Trace to positive; A3 Positive or greater" | kdigo-2025-pediatric-ns | p11 | p11/table/protein-strip-categories | table |
| guideline-age-scope | children-age-1-to-18 | treatment recommendations apply at age 1-18 years; below 1 year refer to a pediatric-nephrology specialist because treatment is outside scope | "RENDERED: This guideline makes treatment recommendations for children with nephrotic syndrome aged 1-18 years. Below the age of 1 year, all children fulfilling the definition of nephrotic syndrome should be referred to a specialist in pediatric nephrology" | kdigo-2025-pediatric-ns | p22 | p22/narrative/age-scope | narrative |
| diagnosis-definition-reference | children-age-1-to-18 | apply the clinical characteristics and definitions in the referenced figure | "RENDERED: Practice Point 1.1.1: The clinical characteristics of and definitions for nephrotic syndrome in children are outlined in Figure 1" | kdigo-2025-pediatric-ns | p22 | p22/practice-point/1 | practice-point |
| nephrotic-range-proteinuria | suspected-pediatric-ns | spot uPCR >=200 mg/mmol (2 g/g), or 24-hour protein >=1000 mg/m2/day, corresponding to dipstick 3+ (300-1000 mg/dl) or 4+ (>=1000 mg/dl) | "RENDERED: uPCR >=200 mg/mmol (2 g/g) in a spot urine, or proteinuria >=1000 mg/m2 per day in a 24-h urine sample corresponding to 3+ (300-1000 mg/dl) or 4+ (>=1000 mg/dl)" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-nephrotic-proteinuria | figure |
| nephrotic-syndrome-definition | suspected-pediatric-ns | nephrotic-range proteinuria plus serum albumin <30 g/l (3 g/dl), or edema when albumin is unavailable | "RENDERED: NS: Nephrotic-range proteinuria and either hypoalbuminemia (serum albumin <30 g/l (3 g/dl)) or edema when albumin level is not available" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-ns-definition | figure |
| complete-remission-definition | pediatric-ns-remission-assessment | first-morning or 24-hour uPCR <=200 mg/g (0.2 g/g or 20 mg/mmol), negative or trace dipstick, or protein <100 mg/m2/day, on at least three consecutive days | "RENDERED: Complete remission: First morning urine or 24-h uPCR <=200 mg/g (0.2 g/g or 20 mg/mmol or negative or trace dipstick or <100 mg/m2 per day) on three or more consecutive days" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-complete-remission | figure |
| partial-remission-definition | pediatric-ns-remission-assessment | first-morning or 24-hour uPCR >200 mg/g (0.2 g/g) but <2 g/g, or >20 and <200 mg/mmol, with serum albumin >=30 g/l (3 g/dl) if available | "RENDERED: Partial remission: First morning urine or 24-h uPCR >200 mg/g (0.2 g/g) but <2 g/g (or >20 and <200 mg/mmol) and, if available, serum albumin >=30 g/l (3 g/dl)" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-partial-remission | figure |
| relapse-dipstick-definition | pediatric-ns-relapse-assessment | recurrence of nephrotic-range proteinuria after complete remission; commonly dipstick >=3+ for 3 consecutive days | "RENDERED: Relapse: Recurrence of nephrotic-range proteinuria in a child who had previously achieved complete remission. In children, relapse is commonly assessed by urine dipstick and is thus defined as dipstick >=3+ for 3 consecutive days" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-relapse | figure |
| dipstick-semiquantitation | suspected-pediatric-ns | negative <15 mg/dl; trace 15 to <30; 1+ 30 to <100; 2+ 100 to <300; 3+ 300 to <1000; 4+ >=1000 mg/dl | "RENDERED: Negative: less than 15 mg/dl; Trace: 15 to <30 mg/dl; 1+: 30 to <100 mg/dl; 2+: 100 to <300 mg/dl; 3+: 300 to <1000 mg/dl; 4+: >=1000 mg/dl" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-dipstick | figure |
| ssns-definition | pediatric-ns-course-classification | complete remission within 4 weeks of standard-dose prednisone or prednisolone | "RENDERED: SSNS: Complete remission within 4 weeks of prednisone or prednisolone at standard dose" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-ssns | figure |
| infrequent-relapse-definition | pediatric-ns-course-classification | <2 relapses in first 6 months after initial remission or <3 relapses in any subsequent 12-month period | "RENDERED: Infrequently relapsing NS: <2 relapses in the 6 months following remission of the initial episode or <3 relapses in any subsequent 12-month period" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-infrequent | figure |
| frequent-relapse-definition | pediatric-ns-course-classification | >=2 relapses in first 6 months after initial remission or >=3 relapses per 12 months in a subsequent 12-month period | "RENDERED: Frequently relapsing NS: >=2 relapses in the first 6 months following remission of the initial episode or >=3 relapses per 12 months in any subsequent 12-month period" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-frequent | figure |
| steroid-dependent-definition | pediatric-ns-course-classification | 2 consecutive relapses during recommended prednisone or prednisolone therapy or within 14 days after discontinuation | "RENDERED: Steroid-dependent NS: 2 consecutive relapses during recommended prednisone or prednisolone therapy for first presentation or relapse or within 14 days of prednisone or prednisolone discontinuation" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-steroid-dependent | figure |
| srns-definition | pediatric-ns-course-classification | no complete remission within 4 weeks of standard-dose daily prednisone or prednisolone | "RENDERED: SRNS: Lack of complete remission within 4 weeks of therapy with daily prednisone or prednisolone at standard dose" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-srns | figure |
| confirmation-period | srns-confirmation | weeks 4-6: after partial remission at week 4, continue oral prednisone or prednisolone and/or IV methylprednisolone pulses plus RAS inhibition to determine response; no complete remission at week 6 confirms SRNS | "RENDERED: Confirmation period: Time period between 4 and 6 weeks from prednisone or prednisolone initiation during which response to further oral prednisone or prednisolone and/or pulses of i.v. methylprednisolone and RASi are ascertained in patients achieving only partial remission at 4 weeks. A patient not achieving complete remission at 6 weeks is defined as SRNS" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-confirmation | figure |
| ssns-late-responder-definition | srns-confirmation | complete remission during weeks 4-6 defines a late responder | "RENDERED: SSNS late responder: A patient with new-onset NS achieving complete remission during the confirmation period (between 4 and 6 weeks)" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-late-responder | figure |
| cni-responsive-srns-definition | srns-cni-treatment | partial remission within 6 months and/or complete remission within 12 months at adequate CNI dose or level | "RENDERED: Calcineurin inhibitor-responsive SRNS: Partial remission with 6 months of treatment and/or complete remission with 12 months of treatment with a calcineurin inhibitor at adequate doses and/or levels" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-cni-responsive | figure |
| cni-resistant-srns-definition | srns-cni-treatment | no partial remission after at least 6 months at adequate CNI dose or level | "RENDERED: Calcineurin inhibitor-resistant SRNS: Absence of partial remission with at least 6 months of treatment with a calcineurin inhibitor at adequate doses and/or levels" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-cni-resistant | figure |
| multidrug-resistant-srns-definition | srns-all | no complete remission after 12 months with 2 mechanistically distinct steroid-sparing agents at standard doses | "RENDERED: Multi-drug resistant SRNS: Absence of complete remission with 12 months of treatment with 2 mechanistically distinct glucocorticoid-sparing agents at standard doses" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-multidrug-resistant | figure |
| secondary-srns-definition | pediatric-ns-course-classification | initially steroid-sensitive disease followed by a relapse without remission after 4 weeks of standard-dose daily prednisone or prednisolone | "RENDERED: Secondary SRNS: A SSNS patient at disease onset who at a subsequent relapse fails to achieve remission within 4 weeks of therapy with daily prednisone or prednisolone at standard dose" | kdigo-2025-pediatric-ns | p23 | p23/figure/figure-1-secondary | figure |
| initial-biopsy-strategy | children-age-1-to-18 | prognosis is best predicted by initial response and first-year relapse frequency; kidney biopsy is not usually needed initially and is reserved for resistance or atypical course | "RENDERED: Practice Point 1.2.1: The prognosis for children with nephrotic syndrome is best predicted by the response to initial treatment and frequency of relapse during the first year; kidney biopsy is usually not needed at initial presentation and is reserved for resistance or an atypical course" | kdigo-2025-pediatric-ns | p23 | p23/practice-point/1 | practice-point |
| onset-biopsy-indications | atypical-pediatric-ns | biopsy at onset for macroscopic hematuria, low C3, acute kidney injury not caused by hypovolemia, sustained hypertension, arthritis, or rash | "RENDERED: At-onset kidney-biopsy indications include macroscopic hematuria, low C3, acute kidney injury not related to hypovolemia, sustained hypertension, arthritis, or rash" | kdigo-2025-pediatric-ns | p24 | p24/narrative/onset-biopsy | narrative |
| prolonged-proteinuria-supportive-care | srns-all | use optimal conservative therapy to minimize kidney-disease progression during prolonged proteinuria; dialysis and transplantation must be provided in centers with pediatric-nephrology expertise | "RENDERED: Employ optimal conservative therapy to minimize progression of kidney disease in children with prolonged proteinuria; dialysis and transplantation must be performed in centers with specific expertise in pediatric nephrology" | kdigo-2025-pediatric-ns | p24 | p24/narrative/prolonged-proteinuria-supportive-care | narrative |
| new-onset-treatment-routing | new-onset-under-12-typical | begin daily oral glucocorticoids for 4 or 6 weeks; after response, continue alternate-day glucocorticoids for another 4 or 6 weeks, for a total of 8 or 12 weeks | "RENDERED: Figure 2 routes new-onset nephrotic syndrome below age 12 without syndromic features or family history to daily glucocorticoids for 4 or 6 weeks and, after response, alternate-day glucocorticoids for another 4 or 6 weeks, total 8 or 12 weeks" | kdigo-2025-pediatric-ns | p25 | p25/figure/figure-2-typical-new-onset | figure |
| new-onset-treatment-routing | new-onset-over-12-or-atypical | perform kidney biopsy and/or genetic testing and refer to a specialty center | "RENDERED: Figure 2 routes new-onset nephrotic syndrome above age 12 or with syndromic features or family history to biopsy and/or genetic testing plus referral to a specialty center" | kdigo-2025-pediatric-ns | p25 | p25/figure/figure-2-atypical-new-onset | figure |
| new-onset-treatment-routing | new-onset-no-response | perform genetic testing and kidney biopsy; use a calcineurin inhibitor and renin-angiotensin-aldosterone-system blockade; refer to a specialty center | "RENDERED: Figure 2 routes no response to genetic testing, kidney biopsy, a calcineurin inhibitor, renin-angiotensin-aldosterone-system blockade, and referral to a specialty center" | kdigo-2025-pediatric-ns | p25 | p25/figure/figure-2-no-response | figure |
| later-biopsy-indications | pediatric-ns-biopsy-consideration | biopsy for steroid resistance at 4-6 weeks or secondary steroid resistance | "Biopsy is subsequently indicated for all children with steroid resistance at 4-6 weeks from onset" | kdigo-2025-pediatric-ns | p24 | p24/narrative/later-biopsy | narrative |
| initial-treatment-duration | ssns-initial-treatment | oral glucocorticoids for 8 weeks (4 daily then 4 alternate-day) or 12 weeks (6 daily then 6 alternate-day) | "We recommend that oral glucocorticoids be given for 8 weeks (4 weeks of daily glucocorticoids followed by 4 weeks of alternate-day glucocorticoids) or 12 weeks (6 weeks of daily glucocorticoids followed by 6 weeks of alternate-day glucocorticoids)" | kdigo-2025-pediatric-ns | p24 | p24/recommendation/1.3.1.1 | recommendation |
| initial-daily-prednisone-dose | ssns-initial-treatment | 60 mg/m2/day or 2 mg/kg/day, maximum 60 mg/day, for 4 or 6 weeks | "RENDERED: daily oral prednisone/prednisolone 60 mg/m2 per day or 2 mg/kg per day (maximum 60 mg/d) for 4 weeks; alternatively the same dose for 6 weeks" | kdigo-2025-pediatric-ns | p26 | p26/practice-point/1 | practice-point |
| initial-alternate-day-dose | ssns-initial-treatment | 40 mg/m2 or 1.5 mg/kg, maximum 40 mg, on alternate days for 4 or 6 weeks | "RENDERED: alternate-day prednisone/prednisolone 40 mg/m2 or 1.5 mg/kg (maximum 40 mg) for another 4 weeks; alternatively the same dose for another 6 weeks" | kdigo-2025-pediatric-ns | p26 | p26/narrative/initial-alternate-day-dose | narrative |
| prolonged-initial-course-boundary | young-delayed-responder | age 1-6 years with remission in 10-15 days: a 16-24-week initial course may be beneficial | "RENDERED: age 1-6 years; remission in 10-15 days; prolonging initial treatment to 16-24 weeks may be beneficial" | kdigo-2025-pediatric-ns | p26 | p26/narrative/young-delayed-response | narrative |
| rapid-response-standard-course | rapid-initial-responder | remission in <7 days favors the standard 8-12-week prednisolone course | "RENDERED: standard 8- to 12-week prednisolone course may be preferable with rapid response in <7 days" | kdigo-2025-pediatric-ns | p26 | p26/narrative/rapid-response-course | narrative |
| infection-prophylactic-steroid-routine | frns-or-sdns | do not routinely give daily glucocorticoids during upper respiratory or other infections solely to reduce relapse risk | "RENDERED: Recommendation 1.3.2.1: Daily glucocorticoids should not be routinely given during upper respiratory tract or other infections to reduce relapse risk" | kdigo-2025-pediatric-ns | p27 | p27/recommendation/1.3.2.1 | recommendation |
| selected-infection-extra-doses | frns-sdns-selected-infection | at upper-respiratory-infection onset, consider three extra daily doses of prednisone or prednisolone 0.5 mg/kg/day | "RENDERED: Practice Point 1.3.2.1: A short course of three extra daily doses of prednisone or prednisolone 0.5 mg/kg/day at onset of an upper respiratory tract infection can be considered in selected children" | kdigo-2025-pediatric-ns | p27 | p27/practice-point/1 | practice-point |
| selected-infection-daily-course-evidence | frns-sdns-selected-infection | in selected cases, daily prednisone or prednisolone for 5-7 days at infection onset may be reasonable | "RENDERED: In select cases, daily prednisone or prednisolone for 5-7 days at the onset of an infection may still be reasonable, including children already on alternate-day treatment who regularly relapse with upper respiratory infection or have significant treatment-related morbidity" | kdigo-2025-pediatric-ns | p28 | p28/narrative/selected-infection-course | narrative |
| relapse-daily-prednisone | ssns-relapse | single daily prednisone or prednisolone 60 mg/m2/day or 2 mg/kg/day, maximum 60 mg/day, until complete remission for at least 3 days | "The initial approach to relapse should include oral prednisone or prednisolone as a single daily dose of 60 mg/m2 per day or 2 mg/kg per day (maximum 60 mg/d) until the child remits completely for ≥3 days" | kdigo-2025-pediatric-ns | p28 | p28/practice-point/1 | practice-point |
| relapse-alternate-day-prednisone | ssns-relapse | after complete remission, prednisone or prednisolone 40 mg/m2 or 1.5 mg/kg, maximum 40 mg, on alternate days for 4 weeks | "reduce oral prednisone/prednisolone to 40 mg/m2 or 1.5 mg/kg (maximum 40 mg) on alternate days for 4 weeks" | kdigo-2025-pediatric-ns | p28 | p28/practice-point/2 | practice-point |
| relapse-toxicity-adjustment | frns-or-sdns | without glucocorticoid toxicity use the same regimen; with toxicity consider a shorter taper and/or stronger steroid-sparing approach | "a shorter taper and/or more robust steroid-sparing approaches should be considered in children with signs of glucocorticoid toxicity" | kdigo-2025-pediatric-ns | p28 | p28/practice-point/3 | practice-point |
| low-dose-relapse-prevention | frns-no-serious-steroid-toxicity | alternate-day prednisone or prednisolone, optimally <=0.5 mg/kg per dose, may prevent relapse | "RENDERED: Practice Point 1.3.3.4: Low-dose alternate-day oral prednisone or prednisolone, optimally no more than 0.5 mg/kg per dose, can be prescribed to prevent relapse" | kdigo-2025-pediatric-ns | p28 | p28/practice-point/4 | practice-point |
| steroid-sparing-indication | frns-serious-toxicity-or-sdns | prescribe a glucocorticoid-sparing agent rather than no treatment or glucocorticoids alone | "RENDERED: Recommendation 1.3.3.1: Glucocorticoid-sparing agents should be prescribed to prevent relapses rather than no treatment or continuation with glucocorticoids alone" | kdigo-2025-pediatric-ns | p28 | p28/recommendation/1.3.3.1 | recommendation |
| steroid-sparing-overlap | steroid-sparing-initiation | ideally achieve remission before starting; coadminister glucocorticoids for at least 2 weeks after steroid-sparing initiation | "Coadministration of glucocorticoids is recommended for ≥2 weeks following the initiation of glucocorticoid-sparing treatment" | kdigo-2025-pediatric-ns | p30 | p30/practice-point/1 | practice-point |
| steroid-sparing-choice | frns-agent-selection | oral cyclophosphamide or levamisole may be preferable | "Oral cyclophosphamide and levamisole may be preferable glucocorticoid-sparing therapies in frequently relapsing nephrotic syndrome" | kdigo-2025-pediatric-ns | p30 | p30/practice-point/2 | practice-point |
| steroid-sparing-choice | sdns-agent-selection | MMF, rituximab, CNIs, and to a lesser extent oral cyclophosphamide may be preferable | "MMF, rituximab, CNIs, and, to a lesser extent, oral cyclophosphamide may be preferable glucocorticoid-sparing therapies in children with steroid-dependent nephrotic syndrome" | kdigo-2025-pediatric-ns | p30 | p30/narrative/sdns-agent-choice | narrative |
| cyclosporine-ssns-dose | ssns-on-cyclosporine | start 4-5 mg/kg/day in two divided doses | "RENDERED: Cyclosporine: 4 to 5 mg/kg/d (starting dose) in two divided doses" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cyclosporine-dose | figure |
| cyclosporine-ssns-trough | ssns-on-cyclosporine | target 12-hour trough 60-150 ng/ml (50-125 nmol/l), using the lowest level maintaining remission | "RENDERED: Target 12 hour trough level of 60-150 ng/ml (50-125 nmol/l) aiming for lowest levels to maintain remission and avoid toxicity" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cyclosporine-trough | figure |
| tacrolimus-ssns-dose | ssns-on-tacrolimus | start 0.1 mg/kg/day in two divided doses | "RENDERED: Tacrolimus: 0.1 mg/kg/d (starting dose) given in two divided doses" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-tacrolimus-dose | figure |
| tacrolimus-ssns-trough | ssns-on-tacrolimus | target 12-hour trough 5-10 ng/ml (6-12 nmol/l), using the lowest level maintaining remission | "RENDERED: Target 12 hour trough level of 5-10 ng/ml (6-12 nmol/l) aiming for lowest levels to maintain remission" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-tacrolimus-trough | figure |
| cni-ssns-duration | ssns-on-cni | continue for at least 12 months; most children relapse after discontinuation; monitor levels for toxicity | "RENDERED: CNI should be continued for at least 12 months as most children will relapse upon discontinuation. Monitor CNI levels during therapy to limit toxicity" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cni-duration | figure |
| young-child-cyclosporine-frequency | ssns-on-cyclosporine | age <6 years: daily cyclosporine may be split into 3 doses every 8 hours | "RENDERED: In younger children (<6 years of age), the daily dose of cyclosporine can be divided into 3 doses (every 8 hours)" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-young-cyclosporine | figure |
| cni-creatinine-stop-rule | ssns-on-cni | reduce dose if creatinine rises without plateau or >30% above baseline; discontinue if creatinine does not fall after reduction | "RENDERED: reducing the dose if serum creatinine increases but does not plateau or increases over 30% of baseline. If the serum creatinine level does not fall after dose reduction, the CNI should be discontinued" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cni-creatinine | figure |
| cni-formulation-frequency | ssns-on-cni | although commonly dosed twice daily, a CNI may be dosed once daily when permitted by the individual formulation | "RENDERED: The calcineurin inhibitor, while often used twice daily, may be dosed once a day depending on the individual formulation" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cni-formulation-frequency | figure |
| cni-target-evidence-boundary | ssns-on-cni | trough targets derive from transplant literature; nephrotic-syndrome target ranges are unknown; levels are commonly checked for adherence and toxicity | "RENDERED: CNI target ranges are based on transplant literature, target ranges for nephrotic syndrome are not known, and clinicians commonly check levels to verify adherence and avoid toxicity" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cni-target-boundary | figure |
| cni-proteinuria-titration | ssns-on-cni | titrate to the desired proteinuria effect while balancing dose escalation against serum creatinine; reduce if creatinine rises without plateau or >30% above baseline and stop if it does not fall | "RENDERED: Titrate the individual CNI dose to the desired effect on proteinuria while balancing escalation against serum creatinine; reduce the dose if creatinine rises without plateau or more than 30% above baseline, and discontinue if it does not fall after reduction" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cni-proteinuria-titration | figure |
| cni-agent-preference | ssns-on-cyclosporine | cyclosporine may be preferable when diabetic complications are a concern | "RENDERED: Cyclosporine may be preferable in patients at risk for diabetic complications" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cyclosporine-preference | figure |
| cni-agent-preference | ssns-on-tacrolimus | tacrolimus may be preferred when cyclosporine-associated cosmetic adverse effects are unacceptable | "RENDERED: Tacrolimus may be preferred over cyclosporine when cosmetic side effects are unacceptable" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-tacrolimus-preference | figure |
| cyclophosphamide-ssns-course | ssns-on-cyclophosphamide | oral 2 mg/kg/day for 12 weeks; maximum cumulative 168 mg/kg | "RENDERED: Oral cyclophosphamide: 2 mg/kg/d for 12 weeks (maximum cumulative dose 168 mg/kg)" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cyclophosphamide-dose | figure |
| cyclophosphamide-monitoring | ssns-on-cyclophosphamide | start only after steroid-induced remission; no second alkylator course; CBC weekly and reduce or stop for severe leukopenia or marrow suppression | "RENDERED: second courses of alkylating agents should not be given. Weekly CBCs are recommended during the treatment course" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-cyclophosphamide-monitoring | figure |
| levamisole-dose | ssns-on-levamisole | 2.5 mg/kg on alternate days, maximum 150 mg | "RENDERED: Oral levamisole: 2.5 mg/kg on alternate days, with a maximum dose of 150 mg" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-levamisole-dose | figure |
| levamisole-duration | ssns-on-levamisole | continue for at least 12 months | "RENDERED: Levamisole should be continued for at least 12 months" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-levamisole-duration | figure |
| levamisole-monitoring | ssns-on-levamisole | CBC every 2-3 months; ALT/AST every 3-6 months; ANCA every 6 months if possible; interrupt for ANCA positivity, rash, or agranulocytosis | "RENDERED: Monitor CBC every 2-3 months and alanine and aspartate aminotransferases every 3-6 months. Check ANCA titers every 6 months, if possible, and interrupt treatment in case of ANCA positivity, skin rash, or agranulocytosis" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-levamisole-monitoring | figure |
| mmf-ssns-dose | ssns-on-mmf | start 1200 mg/m2/day in 2 divided doses | "RENDERED: Mycophenolate mofetil: Starting dose of 1200 mg/m2/d (given in two divided doses)" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-mmf-dose | figure |
| mmf-ssns-duration | ssns-on-mmf | continue at least 12 months because most children relapse when it stops | "RENDERED: Mycophenolate mofetil should be continued for at least 12 months, as most children will relapse when it is stopped" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-mmf-duration | figure |
| mmf-auc-target | ssns-on-mmf | target mycophenolic-acid AUC >50 micrograms-hour/ml | "RENDERED: Target area under the curve >50 micrograms-hour/ml" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-mmf-auc | figure |
| mycophenolate-equivalence | ssns-on-mmf | 360 mg sodium mycophenolate corresponds to 500 mg MMF | "RENDERED: 360 mg of sodium mycophenolate corresponds to 500 mg of mycophenolate mofetil" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-mycophenolate-equivalence | figure |
| rituximab-ssns-dose | difficult-frns-sdns-rituximab | 375 mg/m2 IV for 1-4 doses; evidence does not define the needed number | "RENDERED: Rituximab: 375 mg/m2 i.v. x 1-4 doses. There are insufficient data to make a recommendation for specific number of needed doses" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-rituximab-dose | figure |
| rituximab-screening-monitoring | difficult-frns-sdns-rituximab | before treatment check hepatitis B surface antigen, hepatitis B core antibody, and QuantiFERON TB; monitor IgG before and after, and monitor CD20 when available | "RENDERED: Before rituximab, check hepatitis B surface antigen, hepatitis B core antibody, and QuantiFERON tuberculosis; monitor IgG before and after treatment and CD20 when available" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-rituximab-screening | figure |
| post-rituximab-mmf | complicated-frns-sdns-post-rituximab | MMF after rituximab can reduce treatment failure | "RENDERED: In children with complicated forms of FRNS or SDNS, the use of mycophenolate mofetil after rituximab can decrease the risk of treatment failure" | kdigo-2025-pediatric-ns | p31 | p31/figure/figure-3-post-rituximab-mmf | figure |
| srns-confirmation-treatment | srns-confirmation | weeks 4-6: begin RAS inhibition and continue daily or alternate-day oral prednisolone; three daily IV methylprednisolone pulses may be added | "RENDERED: Between weeks 4 and 6, use a renin-angiotensin-system inhibitor and continue daily or alternate-day oral prednisolone; three daily IV methylprednisolone pulses may be added" | kdigo-2025-pediatric-ns | p32 | p32/narrative/srns-confirmation-treatment | narrative |
| srns-genetic-testing-action | srns-all | rapidly pursue expert genetic testing; an identified genetic cause generally favors conservative rather than immunosuppressive therapy | "RENDERED: As soon as SRNS is established, consider a genetic cause for which immunosuppression may not be useful and pursue expert genetic testing rapidly" | kdigo-2025-pediatric-ns | p33 | p33/narrative/srns-genetic-action | narrative |
| srns-initial-second-line | srns-no-genetic-cause | use cyclosporine or tacrolimus as initial second-line therapy | "We recommend using cyclosporine or tacrolimus as initial second-line therapy for children with steroid-resistant nephrotic syndrome" | kdigo-2025-pediatric-ns | p33 | p33/recommendation/1.4.1.1 | recommendation |
| srns-low-egfr-mmf | srns-low-egfr-or-after-cni-remission | consider MMF when eGFR <30 ml/min/1.73 m2 or as a CNI alternative after remission >1 year | "MMF may also be considered in patients presenting with eGFR < 30 ml/min per 1.73 m2 or used as an alternative to a CNI after remission has been maintained for >1 year" | kdigo-2025-pediatric-ns | p33 | p33/narrative/srns-mmf-boundary | narrative |
| cni-resistant-trial-referral | cni-resistant-srns | strongly consider enrollment in a clinical trial; rituximab has only a limited role where trials are unavailable | "RENDERED: For children with CNI-resistant SRNS, strongly consider entry into a clinical trial evaluating a novel therapy; rituximab has a limited role when a trial is unavailable" | kdigo-2025-pediatric-ns | p33 | p33/narrative/cni-resistant-trial | narrative |
| srns-comprehensive-gene-panel | srns-all | use comprehensive next-generation sequencing that includes all currently known SRNS genes | "RENDERED: Genetic testing is recommended for all patients with SRNS; comprehensive next-generation sequencing of all currently known SRNS genes is usually the most cost-effective method" | kdigo-2025-pediatric-ns | p34 | p34/narrative/srns-comprehensive-panel | narrative |
| genetic-ubiquinone-action | srns-identified-coq-pathway | ubiquinone supplementation has mitigated proteinuric disease with identified COQ2, COQ6, or ADCK4 mutations | "RENDERED: Proteinuric disease has been mitigated with ubiquinone supplementation in patients with identified COQ2, COQ6, and ADCK4 mutations" | kdigo-2025-pediatric-ns | p34 | p34/narrative/coq-ubiquinone | narrative |
| srns-cni-dose-trough | srns-cni-treatment | cyclosporine 5 mg/kg/day in two doses, target 12-hour trough 60-150 ng/ml (50-125 nmol/l); or tacrolimus 0.1 mg/kg/day in two doses for at least 6 months, target 5-10 ng/ml (6-12 nmol/l) | "RENDERED: Oral cyclosporine 5 mg/kg/day in two divided doses, target 12-hour trough 60-150 ng/ml (50-125 nmol/l); or oral tacrolimus 0.1 mg/kg/day in two divided doses for a minimum of 6 months, target 12-hour trough 5-10 ng/ml (6-12 nmol/l)" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-cni-regimens | figure |
| srns-cni-response-stop | srns-cni-nonresponse | discontinue if no partial response by 6 months | "RENDERED: They should be discontinued in those without at least a partial response by 6 months" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-cni-stop | figure |
| srns-cni-duration | srns-cni-treatment | continue at least 12 months after response; about 70% of responders relapse after discontinuation | "RENDERED: CNIs should be continued for at least 12 months as 70% of those who achieve a complete response or partial response will relapse upon discontinuation" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-cni-duration | figure |
| srns-glucocorticoid-regimen | srns-cni-treatment | IV methylprednisolone 500 mg/m2/day for 3 days before CNI, then alternate-day oral prednisolone tapered over 6 months | "RENDERED: i.v. methylprednisolone bolus of 500 mg/m2/d for 3 days prior to starting CNI. Followed by taper: alternate-day oral prednisolone to be tapered gradually over 6 months" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-glucocorticoid-regimen | figure |
| srns-low-dose-prednisone | srns-cni-treatment | prednisone <0.25 mg/kg/day on alternate days | "RENDERED: Low-dose prednisone (<0.25 mg/kg/d alternate day dosing)" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-low-dose-prednisone | figure |
| srns-cyclophosphamide-boundary | srns-all | cyclophosphamide is not recommended; only consider where CNIs are unavailable because of limited resources | "RENDERED: Cyclophosphamide: Not recommended. However, in countries with limited resources where CNIs are not available, this approach may be considered" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-cyclophosphamide | figure |
| srns-mmf-regimen | srns-stable-cni-remission | MMF 1200 mg/m2/day in 2 divided doses for 1 year to maintain remission without further CNI nephrotoxicity | "RENDERED: Mycophenolate mofetil: Starting dose of 1200 mg/m2/d (given in two divided doses) for 1 year" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-mmf | figure |
| srns-rituximab-regimen | srns-nephrotic-rituximab | rituximab 375 mg/m2 IV; two infusions on days 1 and 8 may be preferable with nephrotic-range proteinuria | "RENDERED: Rituximab: 375 mg/m2 i.v. Giving two infusions (day 1 and day 8) at this dose may be preferable in the presence of nephrotic-range proteinuria" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-rituximab | figure |
| srns-rituximab-screening-monitoring | srns-nephrotic-rituximab | check a hepatitis B panel before rituximab; monitor IgG before and after treatment to identify patients who may benefit from immunoglobulin replacement | "RENDERED: Check a hepatitis B panel before rituximab. Monitor IgG before and after rituximab therapy to identify patients who may benefit from immunoglobulin replacement" | kdigo-2025-pediatric-ns | p35 | p35/figure/figure-4-rituximab-screening | figure |
| biopsy-age-trigger | new-onset-at-least-12-or-atypical | age >=12 years is an indication for kidney biopsy | "RENDERED: Indication for kidney biopsy: Children presenting with nephrotic syndrome >=12 years of age" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-biopsy-age | figure |
| biopsy-cni-exposure | pediatric-ns-biopsy-consideration | biopsy for falling kidney function on CNI or prolonged CNI exposure of 2-3 years | "RENDERED: decreasing kidney function in children receiving calcineurin inhibitors or prolonged exposure to calcineurin inhibitors (2 to 3 years)" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-biopsy-cni | figure |
| genetic-testing-indications | pediatric-ns-genetic-testing | test for SRNS, congenital or infantile NS at age <1 year, syndromic features, or family history of SRNS or focal segmental glomerulosclerosis | "RENDERED: Genetic testing: Steroid-resistant nephrotic syndrome; Congenital and infantile forms of nephrotic syndrome (<1 year of age); Nephrotic syndrome associated with syndromic features; Family history of steroid-resistant nephrotic syndrome or focal segmental glomerulosclerosis" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-genetic-testing | figure |
| vitamin-d-calcium-action | ssns-normal-vitamin-d | no supplementation required | "RENDERED: In patients with steroid-sensitive nephrotic syndrome and normal vitamin D levels, supplementation is not required" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-vitamin-d-normal | figure |
| vitamin-d-calcium-action | frns-sdns-or-vitamin-d-deficiency | oral calcium plus vitamin D may prevent reduced bone-mineral content | "RENDERED: in frequently relapsing nephrotic syndrome or steroid-dependent nephrotic syndrome in children or in the presence of a known vitamin D deficiency, a reduction in bone mineral content can be prevented by oral supplementation with oral calcium and vitamin D" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-vitamin-d-supplement | figure |
| gastroprotection-boundary | pediatric-ns-no-gastro-risk | insufficient evidence to recommend prophylactic proton-pump inhibitors | "RENDERED: insufficient evidence of benefit to recommend prophylactic use of proton-pump inhibitors in children with nephrotic syndrome in the absence of risk factors for gastrotoxicity or of gastric symptoms" | kdigo-2025-pediatric-ns | p36 | p36/figure/figure-5-gastroprotection | figure |
| special-situations-principles | children-age-1-to-18 | apply the Figure 5 biopsy, genetic, vitamin D/calcium, and gastroprotection principles | "RENDERED: Practice Point 1.5.1: Figure 5 outlines the general principles for children with nephrotic syndrome" | kdigo-2025-pediatric-ns | p36 | p36/practice-point/1 | practice-point |
| vaccination-evidence-boundary | children-age-1-to-18 | an appropriate vaccination strategy is important, but this source gives no vaccine product, schedule, or disease-specific threshold | "RENDERED: An appropriate vaccination strategy is important to minimize morbidity; this source states no vaccine product, schedule, or disease-specific threshold" | kdigo-2025-pediatric-ns | p24 | p24/narrative/vaccination-boundary | narrative |
| untreated-ns-complication-risk | untreated-or-unresponsive-ns | untreated or unresponsive disease carries high risk from infection, acute kidney injury, edema, and thromboembolism; this source gives no thromboprophylaxis regimen or threshold | "the risk of mortality from infections, acute kidney injury, and complications from edema and thromboembolism is high in children with NS who are not treated or fail to respond" | kdigo-2025-pediatric-ns | p29 | p29/narrative/untreated-complications | narrative |
| glucocorticoid-harms | frns-or-sdns | impaired linear growth, obesity, hypertension, eye disease, behavioral changes, altered bone metabolism, impaired glucose tolerance, acne, and Cushingoid physical changes | "RENDERED: Long-term glucocorticoid harms include impaired linear growth, obesity, hypertension, ophthalmologic pathology, behavioral changes, altered bone metabolism, impaired glucose tolerance, acne, and physical changes related to Cushing syndrome" | kdigo-2025-pediatric-ns | p27 | p27/narrative/glucocorticoid-harms | narrative |
| steroid-sparing-harms | steroid-sparing-initiation | reduced fertility with alkylators; kidney dysfunction and hypertension with CNIs; leukopenia and serious infection risk across second-line options | "RENDERED: Adverse effects include reduced fertility with alkylating agents, kidney dysfunction and hypertension with CNIs, leukopenia, and increased risk of serious infections" | kdigo-2025-pediatric-ns | p29 | p29/narrative/steroid-sparing-harms | narrative |
| cni-comparative-harms | srns-cni-treatment | similar nephrotoxicity; cyclosporine causes more gingival hyperplasia and hypertrichosis, while tacrolimus causes more glucose intolerance | "RENDERED: Cyclosporine and tacrolimus have similar nephrotoxicity; gingival hyperplasia and hypertrichosis are more prevalent with cyclosporine, and glucose intolerance is more frequent with tacrolimus" | kdigo-2025-pediatric-ns | p34 | p34/narrative/cni-comparative-harms | narrative |
| rituximab-long-term-harm-uncertainty | difficult-frns-sdns-rituximab | long-term pediatric safety is uncertain, especially below age 7 years and with repeated courses | "RENDERED: Long-term rituximab safety in children is highly uncertain, particularly below age 7 years and with repeated courses" | kdigo-2025-pediatric-ns | p32 | p32/narrative/rituximab-long-term-safety | narrative |

## Conflicts

No same-quantity, same-population action conflict was found. Apparent differences are
scope-dependent. Routine infection-triggered daily glucocorticoids are discouraged for all
FRNS/SDNS. The formal practice point permits three extra low-dose daily doses only for selected
children already receiving alternate-day therapy with repeated infection-associated relapses or
significant steroid morbidity, while the adjacent evidence discussion says a 5-7-day daily course
may still be reasonable in the same selected circumstances; both source statements are retained,
with the practice-point regimen identified as the formal action. The 8- or 12-week standard initial
course and possible 16-24-week course apply to different response-defined populations. Figure 2
prints younger than 12 versus older than 12 routing, whereas Figure 5 identifies age at least 12 as
a kidney-biopsy indication; each value remains attached to its source-specific action. CNI trough
targets derive from transplant experience, and the source says nephrotic-syndrome target ranges
are unknown; they are therefore retained as monitoring targets, not validated disease-specific
thresholds. Cyclosporine's diabetes-risk preference and tacrolimus's cosmetic-adverse-effect
preference are complementary agent-selection branches.

## Coverage

The bound recommendation record contains **33 marker occurrences = 15 cited + 18 scoped
out**. The cited detailed occurrences are `p22/practice-point/1`,
`p23/practice-point/1`, `p24/recommendation/1.3.1.1`, `p26/practice-point/1`,
`p27/recommendation/1.3.2.1`, `p27/practice-point/1`,
`p28/recommendation/1.3.3.1`, `p28/practice-point/1`, `p28/practice-point/2`,
`p28/practice-point/3`, `p28/practice-point/4`, `p30/practice-point/1`,
`p30/practice-point/2`, `p33/recommendation/1.4.1.1`, and
`p36/practice-point/1`. Every remaining occurrence is individually disposed below.

- `p17/practice-point/1` - summary duplicate of the diagnosis definitions retained from rendered Figure 1 on page 23
- `p18/recommendation/1.3.1.1` - summary duplicate of the complete page 24 initial-treatment recommendation
- `p18/practice-point/1` - summary duplicate of the complete page 23 prognosis practice point
- `p18/practice-point/2` - extraction fragment from the Figure 2 caption, with no independent recommendation action
- `p19/recommendation/1.3.2.1` - summary duplicate of the complete page 27 infection recommendation
- `p19/recommendation/1.3.3.1` - summary duplicate of the complete page 28 steroid-sparing recommendation
- `p19/practice-point/1` - summary duplicate of the complete page 26 initial dosing practice point
- `p19/practice-point/2` - summary duplicate of the complete page 27 selected infection-dose practice point
- `p19/practice-point/3` - summary duplicate of the complete page 28 relapse-induction practice point
- `p19/practice-point/4` - summary duplicate of the complete page 28 post-remission relapse practice point
- `p19/practice-point/5` - summary duplicate of the complete page 28 toxicity-adjusted relapse practice point
- `p19/practice-point/6` - summary duplicate of the complete page 28 low-dose relapse-prevention practice point
- `p19/practice-point/7` - summary duplicate of the complete page 30 steroid-sparing overlap practice point
- `p19/practice-point/8` - summary duplicate of the complete page 30 steroid-sparing selection practice point
- `p21/recommendation/1.4.1.1` - summary duplicate of the complete page 33 SRNS second-line recommendation
- `p21/practice-point/1` - summary duplicate of the complete page 36 special-situations practice point and rendered Figure 5
- `p25/practice-point/1` - extraction fragment from the Figure 2 caption, with no independent recommendation action
- `p28/recommendation/1.3.2.1` - narrative cross-reference to the page 27 infection recommendation, not a new occurrence of its action

ADR 0009 disposition: retained all patient-changing definitions, applicability limits,
classification cutoffs, diagnostic and referral branches, doses, maxima, durations, tapers,
monitoring intervals, stop rules, treatment-selection boundaries, harms, and explicit evidence
limits from the 50-page document. Retained the clinical values in rendered Figures 1-5 and the
front-matter CKD/proteinuria classifications. Figure 2 routing is retained by onset population and
response; Figure 3 retains formulation-dependent dosing, transplant-derived target uncertainty,
proteinuria-versus-creatinine titration, and agent preferences; Figure 4 retains the tacrolimus
minimum course and rituximab screening and IgG-replacement boundary. Narrative retention includes
the formal-versus-evidence infection-course distinction, conservative care during prolonged
proteinuria, pediatric-center dialysis/transplantation, comprehensive SRNS gene testing, and
COQ2/COQ6/ADCK4-specific ubiquinone evidence. The page 17-21 summary occurrences are individually
action-accounted below and are not treated as independent clinical actions. Scoped out contents-only supplementary-study
regimens, trial sample sizes and effect estimates, publication years, research recommendations,
evidence-review mechanics, generic unit conversions, disclosure prose, acknowledgments, and
bibliography entries. Vaccination and thromboembolism are retained only to the extent the source
states them; the document supplies no vaccine schedule or thromboprophylaxis dose, duration, or
threshold.
