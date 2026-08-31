# ANCA-associated vasculitis — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2024-anca | KDIGO | KDIGO/KDIGO-2024-ANCA-Vasculitis-Guideline-Update | guideline | 2024 Clinical Practice Guideline | 2024-03 | https://doi.org/10.1016/j.kint.2023.10.008 | chosen | bound |

## Scope

**Read:** all 47 source pages, including front matter, the complete summary of
recommendation statements and practice points, every clinical section and its tables
and figures, guideline-development methods, disclosures, acknowledgments, and the
reference list. The rows retain numbers that define, classify, dose, time, monitor,
start, stop, or otherwise change an action for a patient. Trial effect estimates,
cohort characteristics, publication years, bibliography numbers, unit-conversion
factors, and evidence-review methods were read but do not produce rows.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| front matter, contents, and reference keys | 1-7 | read 2026-08-31; blind 2026-08-31 |
| CKD GFR and albuminuria/proteinuria classifications | 8-9 | yes |
| abbreviations, notice, foreword, membership, and abstract | 10-14 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendation statements and practice points | 15-20 | yes |
| diagnosis, prognosis, induction, maintenance, relapse, refractory disease, and transplantation | 21-35 | yes |
| guideline-development methods | 36-41 | read 2026-08-31; blind 2026-08-31 |
| biographic disclosures and acknowledgments | 42-45 | read 2026-08-31; blind 2026-08-31 |
| references | 46-47 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| older-adults-active-aav | older adults older than 75 years with active systemic AAV |
| people-assessed-for-ckd | people being assessed for CKD duration and GFR category |
| people-assessed-for-albuminuria-proteinuria | people being assessed for persistent albuminuria or proteinuria category |
| aav-remission-assessment | patients with AAV being assessed for remission |
| aav-kidney-biopsies | kidney biopsies from patients with ANCA-associated glomerulonephritis |
| new-onset-aav-severe-kidney | patients with new-onset AAV and markedly reduced or rapidly declining GFR |
| aav-under-50kg-induction | patients with AAV weighing less than 50 kg receiving induction therapy |
| aav-50-75kg-induction | patients with AAV weighing 50-75 kg receiving induction therapy |
| aav-over-75kg-induction | patients with AAV weighing more than 75 kg receiving induction therapy |
| aav-oral-cyclophosphamide | patients with AAV receiving oral cyclophosphamide induction |
| aav-iv-cyclophosphamide | patients with AAV receiving intravenous cyclophosphamide induction |
| aav-rituximab-induction | patients with AAV receiving rituximab induction |
| aav-combination-induction | patients with AAV receiving rituximab plus intravenous cyclophosphamide induction |
| aav-mmf-induction | patients with AAV receiving MMF induction |
| aav-avacopan-induction | patients with AAV receiving avacopan with rituximab or cyclophosphamide induction |
| aav-lovas-induction | patients with AAV receiving reduced-dose or high-dose prednisolone plus rituximab in the LoVAS trial |
| aav-lower-kidney-function-avacopan | patients with AAV and lower kidney function receiving avacopan |
| aav-dialysis-no-extrarenal | patients with AAV who remain on dialysis and have no extrarenal manifestations |
| aav-after-cyclophosphamide-induction | patients with AAV after cyclophosphamide induction |
| aav-after-rituximab-induction | patients with AAV after rituximab induction |
| aav-cyclophosphamide-or-rituximab | patients with AAV receiving cyclophosphamide or rituximab |
| aav-rituximab | patients with AAV treated with rituximab |
| aav-severe-kidney-plex | patients with AAV and severe kidney disease receiving plasma exchange |
| aav-plex-consideration | patients with AAV being considered for plasma exchange because of severe kidney disease, dialysis, rapidly increasing SCr, or diffuse alveolar hemorrhage with hypoxemia |
| aav-pulmonary-hemorrhage-plex | patients with AAV and diffuse pulmonary hemorrhage receiving plasma exchange |
| aav-anti-gbm-overlap-plex | patients with AAV and anti-GBM antibodies receiving plasma exchange |
| aav-maintenance | patients with AAV after induction of remission |
| aav-azathioprine-maintenance | patients with AAV receiving azathioprine maintenance |
| aav-mmf-maintenance | patients with AAV receiving MMF maintenance |
| aav-rituximab-maintenance | patients with AAV receiving scheduled rituximab maintenance |
| aav-maintenance-agent-selection | patients with AAV being considered for rituximab versus azathioprine maintenance |
| aav-methotrexate-candidate | patients with AAV being considered for methotrexate maintenance |
| aav-maintenance-eular-comparison | patients with AAV after induction of remission, as reported for EULAR guidance |
| aav-cumulative-cyclophosphamide | patients with AAV previously exposed to cyclophosphamide |
| aav-transplant-candidate | patients with AAV being considered for kidney transplantation |

## Quantities

| key | verbatim |
| --- | --- |
| older-adult-immunosuppression-age | age group in which immunosuppressive treatment was associated with improved survival |
| ckd-duration-definition | duration required for CKD definition |
| ckd-gfr-category | GFR category cutoffs |
| persistent-albuminuria-category | persistent albuminuria A1-A3 cutoffs |
| aer-category | albumin excretion rate A1-A3 cutoffs |
| per-category | protein excretion rate A1-A3 cutoffs |
| acr-category | albumin-to-creatinine ratio A1-A3 cutoffs |
| pcr-category | protein-to-creatinine ratio A1-A3 cutoffs |
| protein-reagent-strip-category | protein reagent-strip A1-A3 categories |
| aav-remission-bvas | Birmingham Vasculitis Activity Score criterion for remission |
| focal-histologic-class | normal-glomeruli cutoff for focal histopathologic class |
| sclerotic-histologic-class | globally-sclerotic-glomeruli cutoff for sclerotic histopathologic class |
| crescentic-histologic-class | cellular-crescents cutoff for crescentic histopathologic class |
| mixed-histologic-class | histopathologic class when no predominant glomerular phenotype reaches its cutoff |
| favorable-kidney-risk-normal-glomeruli | normal-glomeruli cutoff associated with favorable kidney outcomes in the Brix kidney risk score |
| severe-kidney-induction-scr | serum-creatinine cutoff for limited rituximab-plus-glucocorticoid data and alternative induction regimens |
| prednisolone-pexivas-taper | reduced-dose PEXIVAS prednisolone taper by weight and week |
| oral-cyclophosphamide-induction | oral cyclophosphamide induction dose, duration, and age/GFR reductions |
| iv-cyclophosphamide-induction | intravenous cyclophosphamide induction dose, schedule, and age/GFR reductions |
| rituximab-induction | rituximab induction alternatives |
| rituximab-cyclophosphamide-induction | rituximab plus intravenous cyclophosphamide induction alternatives |
| mmf-induction | MMF induction dose and escalation |
| avacopan-induction | avacopan induction dose and frequency |
| lovas-prednisolone-comparison | reduced-dose versus high-dose prednisolone regimens in LoVAS |
| avacopan-recovery-egfr-subgroup | eGFR cutoff for the subgroup observed to have increased kidney-function recovery with avacopan |
| dialysis-immunosuppression-stop | time after which discontinuation of immunosuppression may be considered |
| prednisolone-after-cyclophosphamide | prednisolone target after cyclophosphamide induction |
| prednisolone-after-rituximab | prednisolone withdrawal target after rituximab induction |
| initial-oral-prednisolone | initial oral prednisolone dose and duration |
| initial-iv-methylprednisolone | total initial intravenous methylprednisolone dose used for severe presentations |
| pneumocystis-prophylaxis-duration | duration of low-dose TMP-SMX or alternative prophylaxis |
| rituximab-igg-monitoring | IgG monitoring interval during rituximab treatment |
| rituximab-low-baseline-igg | baseline IgG level predicting greater secondary-immunodeficiency risk |
| maintenance-agent-low-baseline-igg | baseline IgG cutoff favoring azathioprine over rituximab maintenance |
| plasma-exchange-consideration-scr | serum-creatinine threshold for considering plasma exchange |
| severe-kidney-plasma-exchange | plasma-exchange schedule and replacement volume for severe kidney disease |
| pulmonary-hemorrhage-plasma-exchange | plasma-exchange schedule for diffuse pulmonary hemorrhage |
| anti-gbm-overlap-plasma-exchange | plasma-exchange schedule and stopping condition for anti-GBM overlap |
| maintenance-duration | optimal duration of remission-maintenance therapy |
| methotrexate-minimum-gfr | GFR below which methotrexate should not be used |
| rituximab-mainritsan-maintenance | MAINRITSAN scheduled rituximab maintenance protocol |
| rituximab-ritazarem-maintenance | RITAZAREM scheduled rituximab maintenance protocol |
| azathioprine-standard-maintenance | standard azathioprine dose, duration, and taper |
| azathioprine-extended-maintenance | extended azathioprine and glucocorticoid maintenance regimen |
| mmf-maintenance | MMF maintenance dose and duration |
| eular-maintenance-duration | EULAR maintenance-duration comparison reported by KDIGO |
| cumulative-cyclophosphamide-malignancy | cumulative cyclophosphamide exposure associated with malignancy |
| transplant-remission-delay | complete-clinical-remission interval before transplantation |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-duration-definition | people-assessed-for-ckd | abnormalities of kidney structure or function for >3 months | "RENDERED: CKD is defined as abnormalities of kidney structure or function, present for >3 months, with implications for health" | kdigo-2024-anca | p8 | p8/narrative/ckd-duration | narrative |
| ckd-gfr-category | people-assessed-for-ckd | G1 >=90; G2 60-89; G3a 45-59; G3b 30-44; G4 15-29; G5 <15 ml/min/1.73 m2 | "RENDERED: GFR categories (ml/min/1.73 m²); G1 ≥90; G2 60–89; G3a 45–59; G3b 30–44; G4 15–29; G5 <15" | kdigo-2024-anca | p8 | p8/narrative/gfr-categories | narrative |
| persistent-albuminuria-category | people-assessed-for-albuminuria-proteinuria | A1 <30 mg/g and <3 mg/mmol; A2 30-300 mg/g and 3-30 mg/mmol; A3 >300 mg/g and >30 mg/mmol | "RENDERED: Persistent albuminuria categories; A1 <30 mg/g, <3 mg/mmol; A2 30–300 mg/g, 3–30 mg/mmol; A3 >300 mg/g, >30 mg/mmol" | kdigo-2024-anca | p8 | p8/narrative/persistent-albuminuria | narrative |
| aer-category | people-assessed-for-albuminuria-proteinuria | A1 <30 mg/d; A2 30-300 mg/d; A3 >300 mg/d | "RENDERED: Relationship among categories for albuminuria and proteinuria; AER (mg/d); A1 <30; A2 30–300; A3 >300" | kdigo-2024-anca | p9 | p9/narrative/aer-categories | narrative |
| per-category | people-assessed-for-albuminuria-proteinuria | A1 <150 mg/d; A2 150-500 mg/d; A3 >500 mg/d | "RENDERED: Relationship among categories for albuminuria and proteinuria; PER (mg/d); A1 <150; A2 150–500; A3 >500" | kdigo-2024-anca | p9 | p9/narrative/per-categories | narrative |
| acr-category | people-assessed-for-albuminuria-proteinuria | A1 <3 mg/mmol and <30 mg/g; A2 3-30 mg/mmol and 30-300 mg/g; A3 >30 mg/mmol and >300 mg/g | "RENDERED: Relationship among categories for albuminuria and proteinuria; ACR; A1 <3 mg/mmol, <30 mg/g; A2 3–30 mg/mmol, 30–300 mg/g; A3 >30 mg/mmol, >300 mg/g" | kdigo-2024-anca | p9 | p9/narrative/acr-categories | narrative |
| pcr-category | people-assessed-for-albuminuria-proteinuria | A1 <15 mg/mmol and <150 mg/g; A2 15-50 mg/mmol and 150-500 mg/g; A3 >50 mg/mmol and >500 mg/g | "RENDERED: Relationship among categories for albuminuria and proteinuria; PCR; A1 <15 mg/mmol, <150 mg/g; A2 15–50 mg/mmol, 150–500 mg/g; A3 >50 mg/mmol, >500 mg/g" | kdigo-2024-anca | p9 | p9/narrative/pcr-categories | narrative |
| protein-reagent-strip-category | people-assessed-for-albuminuria-proteinuria | A1 negative to trace; A2 trace to +; A3 + or greater | "RENDERED: Relationship among categories for albuminuria and proteinuria; Protein reagent strip; A1 Negative to trace; A2 Trace to +; A3 + or greater" | kdigo-2024-anca | p9 | p9/narrative/reagent-strip-categories | narrative |
| older-adult-immunosuppression-age | older-adults-active-aav | >75 years | "older adults (>75 years of age) for whom immunosuppressive treatment has been associated with improved survival" | kdigo-2024-anca | p22 | p22/narrative/older-adult-treatment | narrative |
| aav-remission-bvas | aav-remission-assessment | BVAS = 0 | "Remission is defined as the absence of manifestations of vasculitis and GN (BVAS=0)" | kdigo-2024-anca | p22 | p22/narrative/remission-bvas | narrative |
| focal-histologic-class | aav-kidney-biopsies | >=50% normal glomeruli | "RENDERED: Figure 5; Focal class; ≥50% normal glomeruli" | kdigo-2024-anca | p24 | p24/narrative/figure-5-focal | narrative |
| sclerotic-histologic-class | aav-kidney-biopsies | >=50% globally sclerotic glomeruli | "RENDERED: Figure 5; Sclerotic class; ≥50% globally sclerotic glomeruli" | kdigo-2024-anca | p24 | p24/narrative/figure-5-sclerotic | narrative |
| crescentic-histologic-class | aav-kidney-biopsies | >=50% cellular crescents | "RENDERED: Figure 5; Crescentic class; ≥50% cellular crescents" | kdigo-2024-anca | p24 | p24/narrative/figure-5-crescentic | narrative |
| mixed-histologic-class | aav-kidney-biopsies | globally sclerotic glomeruli <50%, normal glomeruli <50%, and cellular crescents <50% | "RENDERED: Figure 5; score globally sclerotic glomeruli, normal glomeruli, then cellular crescents; when none is ≥50%, Mixed class" | kdigo-2024-anca | p24 | p24/narrative/figure-5-mixed | narrative |
| favorable-kidney-risk-normal-glomeruli | aav-kidney-biopsies | >25% normal glomeruli | "a higher percentage of normal glomeruli (>25%) was associated with favorable kidney outcomes" | kdigo-2024-anca | p23 | p23/narrative/brix-normal-glomeruli | narrative |
| severe-kidney-induction-scr | new-onset-aav-severe-kidney | SCr >4 mg/dl (>354 µmol/l) | "RENDERED: Practice Point 9.3.1.2; markedly reduced or rapidly declining GFR; serum creatinine [SCr] >4 mg/dl [>354 µmol/l]" | kdigo-2024-anca | p17 | p17/practice-point/1 | practice-point |
| prednisolone-pexivas-taper | aav-under-50kg-induction | week 1: 50 mg/d; week 2: 25 mg/d; weeks 3-4: 20 mg/d; weeks 5-6: 15 mg/d; weeks 7-8: 12.5 mg/d; weeks 9-10: 10 mg/d; weeks 11-12: 7.5 mg/d; weeks 13-14: 6 mg/d; weeks 15-52: 5 mg/d; after week 52: local practice | "RENDERED: Figure 9; <50 kg; weeks 1, 2, 3–4, 5–6, 7–8, 9–10, 11–12, 13–14, 15–16, 17–18, 19–20, 21–22, 23–52: 50, 25, 20, 15, 12.5, 10, 7.5, 6, 5, 5, 5, 5, 5 mg; >52: investigators' local practice" | kdigo-2024-anca | p18 | p18/narrative/figure-9-under-50 | narrative |
| prednisolone-pexivas-taper | aav-50-75kg-induction | week 1: 60 mg/d; week 2: 30 mg/d; weeks 3-4: 25 mg/d; weeks 5-6: 20 mg/d; weeks 7-8: 15 mg/d; weeks 9-10: 12.5 mg/d; weeks 11-12: 10 mg/d; weeks 13-14: 7.5 mg/d; weeks 15-52: 5 mg/d; after week 52: local practice | "RENDERED: Figure 9; 50–75 kg; weeks 1, 2, 3–4, 5–6, 7–8, 9–10, 11–12, 13–14, 15–16, 17–18, 19–20, 21–22, 23–52: 60, 30, 25, 20, 15, 12.5, 10, 7.5, 5, 5, 5, 5, 5 mg; >52: investigators' local practice" | kdigo-2024-anca | p18 | p18/narrative/figure-9-weight-50-to-75 | narrative |
| prednisolone-pexivas-taper | aav-over-75kg-induction | week 1: 75 mg/d; week 2: 40 mg/d; weeks 3-4: 30 mg/d; weeks 5-6: 25 mg/d; weeks 7-8: 20 mg/d; weeks 9-10: 15 mg/d; weeks 11-12: 12.5 mg/d; weeks 13-14: 10 mg/d; weeks 15-18: 7.5 mg/d; weeks 19-52: 5 mg/d; after week 52: local practice | "RENDERED: Figure 9; >75 kg; weeks 1, 2, 3–4, 5–6, 7–8, 9–10, 11–12, 13–14, 15–16, 17–18, 19–20, 21–22, 23–52: 75, 40, 30, 25, 20, 15, 12.5, 10, 7.5, 7.5, 5, 5, 5 mg; >52: investigators' local practice" | kdigo-2024-anca | p18 | p18/narrative/figure-9-over-75 | narrative |
| oral-cyclophosphamide-induction | aav-oral-cyclophosphamide | 2 mg/kg/d for 3 months, up to 6 months for ongoing activity; age 60: 1.5 mg/kg/d; age 70: 1.0 mg/kg/d; reduce by 0.5 mg/kg/d for GFR <30 ml/min/1.73 m2 | "RENDERED: Figure 10; Oral cyclophosphamide; 2 mg/kg/d for 3 months, continue for ongoing activity to a maximum of 6 months; age 60 yr 1.5 mg/kg/d; age 70 yr 1.0 mg/kg/d; reduce by 0.5 mg/kg/day for GFR <30 ml/min/1.73 m²" | kdigo-2024-anca | p30 | p30/narrative/figure-10-oral-cyclophosphamide | narrative |
| iv-cyclophosphamide-induction | aav-iv-cyclophosphamide | 15 mg/kg at weeks 0, 2, 4, 7, 10, and 13, with weeks 16, 19, 21, and 24 if required; age 60: 12.5 mg/kg; age 70: 10 mg/kg; reduce by 2.5 mg/kg for GFR <30 ml/min/1.73 m2 | "RENDERED: Figure 10; Intravenous cyclophosphamide; 15 mg/kg at weeks 0, 2, 4, 7, 10, 13 (16, 19, 21, 24 if required); age 60 yr 12.5 mg/kg; age 70 yr 10 mg/kg; reduce by 2.5 mg/kg for GFR <30 ml/min/1.73 m²" | kdigo-2024-anca | p30 | p30/narrative/figure-10-iv-cyclophosphamide | narrative |
| rituximab-induction | aav-rituximab-induction | 375 mg/m2 weekly for 4 weeks or 1 g at weeks 0 and 2 | "RENDERED: Figure 10; Rituximab; 375 mg/m²/week × 4 weeks OR 1 g at weeks 0 and 2" | kdigo-2024-anca | p30 | p30/narrative/figure-10-rituximab | narrative |
| rituximab-cyclophosphamide-induction | aav-combination-induction | rituximab 375 mg/m2 weekly for 4 weeks plus IV cyclophosphamide 15 mg/kg at weeks 0 and 2; or rituximab 1 g at weeks 0 and 2 plus IV cyclophosphamide 500 mg every 2 weeks for 6 doses | "RENDERED: Figure 10; Rituximab and i.v. cyclophosphamide; rituximab 375 mg/m²/week × 4 weeks with i.v. cyclophosphamide 15 mg/kg at weeks 0 and 2 OR rituximab 1 g at 0 and 2 weeks with i.v. cyclophosphamide 500 mg/2 weeks × 6" | kdigo-2024-anca | p30 | p30/narrative/figure-10-combination | narrative |
| mmf-induction | aav-mmf-induction | 2000 mg/d in divided doses; may increase to 3000 mg/d for poor response | "RENDERED: Figure 10; MMF; 2000 mg/d (divided doses), may be increased to 3000 mg/d for poor treatment response" | kdigo-2024-anca | p30 | p30/narrative/figure-10-mmf | narrative |
| avacopan-induction | aav-avacopan-induction | 30 mg twice daily | "RENDERED: Figure 10; Avacopan; 30 mg twice daily as alternative to glucocorticoids, in combination with rituximab or cyclophosphamide induction" | kdigo-2024-anca | p30 | p30/narrative/figure-10-avacopan | narrative |
| lovas-prednisolone-comparison | aav-lovas-induction | reduced dose 0.5 mg/kg/d versus high dose 1 mg/kg/d, each with rituximab 375 mg/m² weekly for 4 doses | "RENDERED: LoVAS; reduced-dose prednisolone 0.5 mg/kg/d or high-dose prednisolone 1 mg/kg/d plus 4 doses of rituximab 375 mg/m² per week" | kdigo-2024-anca | p25 | p25/narrative/lovas-doses | narrative |
| avacopan-recovery-egfr-subgroup | aav-lower-kidney-function-avacopan | eGFR <20 ml/min/1.73 m² | "RENDERED: Patients with lower kidney function (eGFR <20 ml/min per 1.73 m²) also might benefit, as an increased recovery of kidney function was observed" | kdigo-2024-anca | p27 | p27/narrative/avacopan-egfr-subgroup | narrative |
| dialysis-immunosuppression-stop | aav-dialysis-no-extrarenal | consider discontinuation after 3 months | "RENDERED: Practice Point 9.3.1.5; Consider discontinuation of immunosuppressive therapy after 3 months in patients who remain on dialysis and who do not have any extrarenal manifestations of disease" | kdigo-2024-anca | p29 | p29/practice-point/2 | practice-point |
| prednisolone-after-cyclophosphamide | aav-after-cyclophosphamide-induction | reduce to 5 mg/d by 6 months | "Following cyclophosphamide induction, oral prednisolone should be reduced to a dose of 5 mg/d by 6 months" | kdigo-2024-anca | p29 | p29/narrative/prednisolone-cyclophosphamide | narrative |
| prednisolone-after-rituximab | aav-after-rituximab-induction | withdraw by 6 months | "RENDERED: Following rituximab induction, prednisolone can be withdrawn by 6 months" | kdigo-2024-anca | p29 | p29/narrative/prednisolone-rituximab | narrative |
| initial-oral-prednisolone | aav-cyclophosphamide-or-rituximab | 1 mg/kg/d for the first week | "RENDERED: The dose of oral prednisolone is 1 mg/kg/d for the first week" | kdigo-2024-anca | p29 | p29/narrative/initial-oral-prednisolone | narrative |
| initial-iv-methylprednisolone | aav-cyclophosphamide-or-rituximab | 1-3 g total for more severe presentations | "Intravenous methylprednisolone is widely used initially for patients with more severe presentations, at a dose of 1–3 g in total" | kdigo-2024-anca | p29 | p29/narrative/initial-iv-methylprednisolone | narrative |
| pneumocystis-prophylaxis-duration | aav-cyclophosphamide-or-rituximab | through the cyclophosphamide course or for 6 months after rituximab induction | "RENDERED: Low-dose TMP-SMX, or alternative, is advised for pneumocystis pneumonia prophylaxis for the duration of the cyclophosphamide course or for 6 months following rituximab induction" | kdigo-2024-anca | p27 | p27/narrative/pneumocystis-prophylaxis | narrative |
| rituximab-igg-monitoring | aav-rituximab | baseline and every 6 months | "IgG levels should be measured at baseline and every 6 months for patients treated with rituximab" | kdigo-2024-anca | p27 | p27/narrative/igg-monitoring | narrative |
| rituximab-low-baseline-igg | aav-rituximab | IgG <3 g/l | "RENDERED: A low level at baseline (defined as IgG <3 g/l) may predict a greater risk of secondary immunodeficiency with rituximab" | kdigo-2024-anca | p27 | p27/narrative/low-baseline-igg | narrative |
| maintenance-agent-low-baseline-igg | aav-maintenance-agent-selection | baseline IgG <300 mg/dl favors azathioprine over rituximab | "RENDERED: Figure 13; Azathioprine preferred; Low baseline IgG (<300 mg/dl)" | kdigo-2024-anca | p34 | p34/narrative/figure-13-low-igg | narrative |
| plasma-exchange-consideration-scr | aav-plex-consideration | consider when SCr >3.4 mg/dl (>300 µmol/l), dialysis is required, SCr is rapidly increasing, or diffuse alveolar hemorrhage causes hypoxemia | "RENDERED: Practice Point 9.3.1.9; Consider plasma exchange for patients with SCr >3.4 mg/dl (>300 µmol/l), patients requiring dialysis or with rapidly increasing SCr, or patients with diffuse alveolar hemorrhage who have hypoxemia" | kdigo-2024-anca | p30 | p30/practice-point/2 | practice-point |
| severe-kidney-plasma-exchange | aav-severe-kidney-plex | 7 treatments over no more than 14 days; 60 ml/kg replacement with albumin | "RENDERED: Figure 11; ANCA vasculitis with severe kidney disease; 7 treatments over a maximum of 14 days, 60 ml/kg volume replacement, albumin substitution" | kdigo-2024-anca | p30 | p30/narrative/figure-11-severe-kidney | narrative |
| pulmonary-hemorrhage-plasma-exchange | aav-pulmonary-hemorrhage-plex | daily until bleeding stops; replace albumin with fresh frozen plasma | "RENDERED: Figure 11; Vasculitis with diffuse pulmonary hemorrhage; Daily until bleeding stops, replace albumin with fresh, frozen plasma" | kdigo-2024-anca | p30 | p30/narrative/figure-11-pulmonary-hemorrhage | narrative |
| anti-gbm-overlap-plasma-exchange | aav-anti-gbm-overlap-plex | daily for 14 days or until anti-GBM antibodies are undetectable | "RENDERED: Figure 11; Vasculitis in association with anti-GBM antibodies; Daily for 14 days or until anti-GBM antibodies are undetectable" | kdigo-2024-anca | p30 | p30/narrative/figure-11-anti-gbm | narrative |
| maintenance-duration | aav-maintenance | 18 months to 4 years after induction of remission | "The optimal duration of remission therapy is between 18 months and 4 years after induction of remission" | kdigo-2024-anca | p33 | p33/practice-point/2 | practice-point |
| methotrexate-minimum-gfr | aav-methotrexate-candidate | do not use when GFR <60 ml/min/1.73 m2 | "Methotrexate should not be used for patients with a GFR <60 ml/min per 1.73 m2" | kdigo-2024-anca | p33 | p33/practice-point/4 | practice-point |
| rituximab-mainritsan-maintenance | aav-rituximab-maintenance | 500 mg twice at complete remission, then 500 mg at months 6, 12, and 18 | "RENDERED: Figure 14; MAINRITSAN scheme; 500 mg × 2 at complete remission, and 500 mg at mo 6, 12, and 18 thereafter" | kdigo-2024-anca | p34 | p34/narrative/figure-14-mainritsan | narrative |
| rituximab-ritazarem-maintenance | aav-rituximab-maintenance | 1000 mg after induction of remission and at months 4, 8, 12, and 16 after the first infusion | "RENDERED: Figure 14; RITAZAREM scheme; 1000 mg infusion after induction of remission, and at mo 4, 8, 12, and 16 after the first infusion" | kdigo-2024-anca | p34 | p34/narrative/figure-14-ritazarem | narrative |
| azathioprine-standard-maintenance | aav-azathioprine-maintenance | 1.5-2 mg/kg/d at complete remission until 1 year after diagnosis, then decrease by 25 mg every 3 months | "RENDERED: Figure 14; Azathioprine; 1.5–2 mg/kg/d at complete remission until 1 yr after diagnosis then decrease by 25 mg every 3 mo" | kdigo-2024-anca | p34 | p34/narrative/figure-14-azathioprine-standard | narrative |
| azathioprine-extended-maintenance | aav-azathioprine-maintenance | 1.5-2 mg/kg/d for 18-24 months, then 1 mg/kg/d until 4 years, then reduce 25 mg every 3 months; glucocorticoids 5-7.5 mg/d for 2 years, then reduce 1 mg every 2 months | "RENDERED: Figure 14; Extend azathioprine until 4 yr; 1.5–2 mg/kg/d for 18–24 mo, then 1 mg/kg/d until 4 yr, then taper by 25 mg every 3 mo; glucocorticoids 5–7.5 mg/d for 2 yr then reduced by 1 mg every 2 mo" | kdigo-2024-anca | p34 | p34/narrative/figure-14-azathioprine-extended | narrative |
| mmf-maintenance | aav-mmf-maintenance | 2000 mg/d in divided doses for 2 years | "RENDERED: Figure 14; MMF; 2000 mg/d (divided doses) at complete remission for 2 yr" | kdigo-2024-anca | p34 | p34/narrative/figure-14-mmf | narrative |
| eular-maintenance-duration | aav-maintenance-eular-comparison | at least 24-48 months after induction | "The EULAR guideline advises maintenance therapy for at least 24–48 months following induction" | kdigo-2024-anca | p33 | p33/narrative/eular-maintenance-duration | narrative |
| cumulative-cyclophosphamide-malignancy | aav-cumulative-cyclophosphamide | above 36 g | "Cumulative dosages above 36 g have been associated with the occurrence of malignancies" | kdigo-2024-anca | p34 | p34/narrative/cumulative-cyclophosphamide | narrative |
| transplant-remission-delay | aav-transplant-candidate | complete clinical remission for >=6 months | "Delay transplantation until patients are in complete clinical remission for ≥6 months" | kdigo-2024-anca | p35 | p35/practice-point/3 | practice-point |

## Conflicts

No duplicate `(quantity, population)` pair carries different values in this sheet.
The KDIGO maintenance-duration row and the EULAR comparison row use distinct quantity
and population keys so that the secondary report of another society's interval cannot
be mistaken for KDIGO's own interval.

## Coverage

The bound extraction contains 53 marker occurrences. Its windows duplicate the summary
and body and frequently stop before the numeric decision point. Every marker not cited
directly above is accounted for here; the complete-document narrative and figure read,
not the marker count, bounds this sheet.

- `p15/practice-point/1` - diagnosis statement has no numeric patient-action point
- `p15/practice-point/2` - experienced-center statement has no numeric patient-action point
- `p15/practice-point/3` - relapse-prediction statement has no numeric patient-action point
- `p16/recommendation/9.3.1.1` - initial-treatment statement has no numeric patient-action point
- `p16/practice-point/1` - algorithm pointer has no numeric patient-action point
- `p16/practice-point/2` - truncated cross-reference marker has no numeric patient-action point
- `p17/practice-point/2` - treatment-selection figure pointer has no additional numeric patient-action point
- `p17/practice-point/3` - route-selection figure pointer has no numeric patient-action point
- `p17/practice-point/4` - dialysis threshold is represented by `dialysis-immunosuppression-stop`
- `p18/practice-point/1` - glucocorticoid taper values are represented by the three `prednisolone-pexivas-taper` rows
- `p18/practice-point/2` - avacopan preference statement adds no numeric point beyond `avacopan-induction`
- `p18/practice-point/3` - immunosuppressive dosing pointer is represented by the Figure 10 rows
- `p18/practice-point/4` - plasma-exchange threshold is represented by `plasma-exchange-consideration-scr`
- `p19/recommendation/9.3.2.1` - maintenance-agent recommendation has no numeric patient-action point
- `p19/practice-point/1` - anti-GBM overlap statement is represented by `anti-gbm-overlap-plasma-exchange`
- `p19/practice-point/2` - maintenance-after-rituximab statement has no numeric patient-action point
- `p19/practice-point/3` - duration is represented by `maintenance-duration`
- `p19/practice-point/4` - withdrawal-risk statement has no numeric patient-action point
- `p19/practice-point/5` - methotrexate cutoff is represented by `methotrexate-minimum-gfr`
- `p19/practice-point/6` - maintenance-agent selection pointer has no additional numeric patient-action point
- `p20/recommendation/9.3.1.1` - cross-reference occurrence has no additional numeric patient-action point
- `p20/practice-point/1` - maintenance dosing pointer is represented by the Figure 14 rows
- `p20/practice-point/2` - relapse treatment statement has no numeric patient-action point
- `p20/practice-point/3` - refractory-disease statement has no numeric patient-action point
- `p20/practice-point/4` - alveolar-bleeding statement has no numeric threshold beyond the plasma-exchange rows
- `p20/practice-point/5` - transplantation interval is represented by `transplant-remission-delay`
- `p22/practice-point/1` - repeated diagnosis statement has no numeric patient-action point
- `p24/recommendation/9.3.1.1` - repeated initial-treatment statement has no numeric patient-action point
- `p24/practice-point/1` - repeated relapse-prediction statement has no numeric patient-action point
- `p27/practice-point/1` - practical-treatment-algorithm pointer has no numeric patient-action point
- `p28/practice-point/1` - repeated severe-kidney threshold is represented by `severe-kidney-induction-scr`
- `p28/practice-point/2` - treatment-selection figure pointer has no additional numeric patient-action point
- `p28/practice-point/3` - truncated cross-reference marker has no numeric patient-action point
- `p29/practice-point/1` - route-selection figure pointer has no numeric patient-action point
- `p29/practice-point/3` - taper pointer is represented by the prednisolone taper rows
- `p29/practice-point/4` - avacopan preference statement adds no numeric point beyond `avacopan-induction`
- `p30/practice-point/1` - dosing pointer is represented by the Figure 10 rows
- `p30/practice-point/3` - anti-GBM overlap is represented by `anti-gbm-overlap-plasma-exchange`
- `p31/recommendation/9.3.2.1` - repeated maintenance-agent recommendation has no numeric patient-action point
- `p33/practice-point/1` - maintenance-after-rituximab statement has no numeric patient-action point
- `p33/practice-point/3` - withdrawal-risk statement has no numeric patient-action point
- `p34/recommendation/9.3.1.1` - narrative cross-reference marker has no numeric patient-action point
- `p34/practice-point/1` - maintenance-agent selection pointer has no additional numeric patient-action point
- `p34/practice-point/2` - maintenance dosing pointer is represented by the Figure 14 rows
- `p34/practice-point/3` - relapse treatment statement has no numeric patient-action point
- `p35/practice-point/1` - refractory-disease statement has no numeric patient-action point
- `p35/practice-point/2` - alveolar-bleeding statement adds no numeric point beyond the plasma-exchange rows
