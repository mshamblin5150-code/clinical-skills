# Chronic kidney disease in HIV infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2014 | IDSA | IDSA/ciu617 | guideline | 2014 update | 2014 | https://doi.org/10.1093/cid/ciu617 | stated | bound |

## Scope

**Read:** all 43 source pages, including the executive summary, methods, CKD
definitions and classifications, kidney-function and damage markers, epidemiology,
pathogenesis, antiretroviral nephrotoxicity, all recommendation sections and evidence
summaries, all eight tables, pediatric material, future directions, disclosures, and
references. The bound recommendation artifact contains 48 marker occurrences; its
omissions warn rather than refuse and do not establish a complete recommendation index.
Numeric narrative accounting includes the page-13 Stribild initiation/discontinuation
boundaries, page-15 dipstick-proteinuria quantification rule, page-16 referral timing and
risk strata, pages 18-24 renal-dose branches and source defects, and pages 28-31
corticosteroid, transplant, pediatric, and drug-interaction thresholds.

**Not read:** nothing in the source page range. The source itself excludes screening,
evaluation, and management in resource-constrained settings.

**Scoped out under ADR 0009's numeric patient-action rule:** author dates and
affiliations, study eligibility and outcome numbers, epidemiologic rates and risk
ratios, trial sample sizes and statistical results, formula coefficients, citation
numbers, reference publication data, grant numbers, and recommendation-grade
definitions were read but do not themselves change an action for a patient. Qualitative
recommendations without a dose, period, cutoff, target, or staging boundary are
accounted for under `## Coverage` but are not threshold rows.

**Source defects preserved rather than silently repaired:** Table 7 prints the
hemodialysis/peritoneal-dialysis levofloxacin loading range as `750-500 mg`, in
descending order; omits `mg` after ciprofloxacin's `400` IV doses and after
famciclovir's `500` VZV dose; prints pentamidine as `q-48h`; prints valganciclovir
as `450 mg qod I)` without an opening parenthesis; and prints the CrCl 10-20 mL/min
valacyclovir dose as `500-1 g mg`. The corresponding rows retain and disclose
those source strings rather than silently normalizing them.

| span | pages | read |
| --- | --- | --- |
| executive summary and recommendations | 1-4 | yes |
| methods | 5 | read 2026-08-31; blind 2026-08-31 |
| CKD definitions, classifications, markers, epidemiology, pathogenesis, and antiretroviral toxicity | 6-13 | yes |
| transplantation background, screening, evaluation, referral, and ART management | 14-17 | yes |
| antiretroviral and antimicrobial renal-dose tables | 18-24 | yes |
| tenofovir, renoprotective therapy, blood pressure, corticosteroids, transplantation, pediatrics, and interaction table | 25-31 | yes |
| future directions, acknowledgments, disclosures, and beginning of references | 32 | read 2026-08-31; blind 2026-08-31 |
| references | 33-43 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| hiv-adults-children-us | HIV-infected adults and children in the United States |
| stable-hiv | stable HIV-infected patients |
| hiv-kidney-disease | HIV-infected patients with kidney disease |
| hiv-ckd | HIV-infected patients who have CKD |
| tenofovir-treated-decline | tenofovir-treated patients who experience a confirmed GFR decline |
| diabetic-albuminuria | diabetic patients |
| nondiabetic-albuminuria | nondiabetic patients |
| pre-esrd-ckd | HIV-infected individuals with pre-ESRD CKD |
| ckd-low-albuminuria | HIV-infected patients who have CKD with normal or mildly increased albuminuria |
| ckd-higher-albuminuria | HIV-infected patients who have CKD with moderately to severely increased albuminuria |
| biopsy-hivan | patients with biopsy-confirmed HIVAN |
| children-adolescents-stable | children and adolescents with stable kidney function |
| prepubertal-children | prepubertal children (Tanner stages 1-3) |
| children-adolescents-no-kidney-disease | children and adolescents with HIV who are without evidence of existing kidney disease |
| children-under-2 | children <2 years of age |
| pediatric-tanner-1-3 | children with Tanner stages 1-3 |
| adults | adults |
| men | men |
| women | women |
| normal-kidney-function | normal kidney function |
| impaired-kidney-function | impaired kidney function |
| all-crcl | All CrCl |
| hiv-adults-ckd-esrd | HIV-infected adults with chronic kidney disease or end-stage renal disease |
| hiv-ckd-esrd | HIV-infected patients with chronic kidney disease or end-stage renal disease |
| transplant-candidates | transplantation candidates |
| upcr-over-200 | individuals with urine protein-to-creatinine ratio >200 mg/g |
| crcl-ge70 | CrCl >=70 mL/min |
| crcl-lt70 | CrCl <70 mL/min |
| crcl-ge60 | CrCl >=60 mL/min |
| crcl-ge50 | CrCl >=50 mL/min |
| crcl-30-59 | CrCl 30-59 mL/min |
| crcl-40-59 | CrCl 40-59 mL/min |
| crcl-30-50 | CrCl 30-50 mL/min |
| crcl-30-49 | CrCl 30-49 mL/min |
| crcl-26-50 | CrCl 26-50 mL/min |
| crcl-25-50 | CrCl 25-50 mL/min |
| crcl-25-49 | CrCl 25-49 mL/min |
| crcl-25-39 | CrCl 25-39 mL/min |
| crcl-20-49 | CrCl 20-49 mL/min |
| crcl-20-40 | 20-40 mL/min |
| crcl-20-39 | CrCl 20-39 mL/min |
| crcl-15-30 | CrCl 15-30 mL/min |
| crcl-15-29 | CrCl 15-29 mL/min |
| crcl-10-50 | CrCl 10-50 mL/min |
| crcl-10-30 | CrCl 10-30 mL/min |
| crcl-10-29 | CrCl 10-29 mL/min |
| crcl-10-24 | CrCl 10-24 mL/min |
| crcl-10-20 | 10-20 mL/min |
| crcl-10-19 | CrCl 10-19 mL/min |
| crcl-5-14 | CrCl 5-14 mL/min |
| crcl-lt50 | CrCl <50 mL/min |
| crcl-lt50-nondialysis | CrCl <50 mL/min and not receiving hemodialysis |
| crcl-lt30 | CrCl <30 mL/min |
| crcl-lt20 | CrCl <20 mL/min |
| crcl-lt15 | CrCl <15 mL/min |
| crcl-ge15 | CrCl >=15 mL/min |
| crcl-lt15-dialysis | CrCl <15 mL/min, hemodialysis, or peritoneal dialysis |
| crcl-lt10 | CrCl <10 mL/min |
| crcl-lt5-dialysis | CrCl <5 mL/min, hemodialysis, or peritoneal dialysis |
| crcl-lt10-dialysis | CrCl <10 mL/min, hemodialysis, or peritoneal dialysis |
| crcl-le25 | CrCl <=25 mL/min |
| crcl-gt50 | CrCl >50 mL/min |
| crcl-gt30 | CrCl >30 mL/min |
| crcl-lt30-hd | CrCl <30 mL/min or hemodialysis |
| crcl-10-29-hd | CrCl 10-29 mL/min or hemodialysis |
| dialysis | hemodialysis or peritoneal dialysis |
| hemodialysis | receiving hemodialysis |
| pi-experienced-hemodialysis | protease-inhibitor-experienced patients receiving hemodialysis |
| peritoneal-dialysis | receiving peritoneal dialysis |
| body-ge60 | Body weight >=60 kg |
| body-lt60 | Body weight <60 kg |
| renal-transplant-hiv | patients infected with HIV after kidney transplantation |
| children-young | young children (<10 years old) |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-duration | present for >3 months |
| ckd-gfr-definition | GFR that persists below 60 mL/minute/1.73 m2 for >3 months |
| gfr-monitoring | at least twice yearly |
| kidney-damage-monitoring | at least annually |
| nephrology-referral | clinically significant decline in GFR |
| tenofovir-avoidance-gfr | GFR <60 mL/minute/1.73 m2 |
| tenofovir-substitution | GFR decline by >25% from baseline and to a level <60 mL/minute/1.73 m2 |
| tenofovir-discontinuation-evidence | tenofovir should be discontinued in patients who develop reduced GFR |
| ace-arb-albuminuria | clinically significant albuminuria |
| statin-cvd-risk | >7.5% 10-year risk of cardiovascular disease |
| aspirin-dose | aspirin (75-100 mg/day) |
| bp-target-low-albuminuria | target blood pressure of <140/90 mm Hg |
| bp-target-higher-albuminuria | target blood pressure of <130/80 mm Hg |
| pediatric-screening | at least twice yearly |
| albuminuria-a1-stage | normal to mildly increased albuminuria (A1) |
| albuminuria-a2-stage | moderately increased albuminuria (A2) |
| albuminuria-a3-stage | severely increased albuminuria (A3) |
| proteinuria-a1-stage | normal to mildly increased proteinuria (A1) |
| proteinuria-a2-stage | moderately increased proteinuria (A2) |
| proteinuria-a3-stage | severely increased proteinuria (A3) |
| reagent-strip-a1-stage | normal to mildly increased protein reagent strip result (A1) |
| reagent-strip-a2-stage | moderately increased protein reagent strip result (A2) |
| reagent-strip-a3-stage | severely increased protein reagent strip result (A3) |
| gfr-strata | GFR level (6 strata) |
| urine-collection-adequacy-men | expected 24-hour urine creatinine in men |
| urine-collection-adequacy-women | expected 24-hour urine creatinine in women |
| proximal-phosphate-fe | Fractional excretion of phosphate |
| proximal-phosphate-tmp-gfr | Tubular maximum for phosphate corrected for GFR |
| proximal-uric-acid-fe | Fractional excretion of uric acid |
| urine-albumin-protein-ratio | Urine albumin-to-protein ratio |
| urine-albumin-protein-ratio-tenofovir | urinary albumin-total protein ratio in tenofovir-treated patients |
| proteinuria-dipstick-quantification | Proteinuria >=1+ on urinalysis |
| biopsy-observation | 24-hour postbiopsy observation period |
| referral-before-dialysis | at least 1 year prior to the initiation of dialysis |
| gfr-method-near-60 | GFR values near 60 mL/minute/1.73 m2 |
| nephrology-referral-risk | consider referral in patients with GFR 30-59 mL/minute/1.73 m2 and ESRD risk factors |
| ace-arb-monitoring | measured within 1 week of starting, or following any dose escalation |
| prednisone-hivan | prednisone 60 mg/day or the equivalent of 1 mg/kg of prednisone per day |
| prednisone-response | after 1-4 weeks |
| prednisone-continuation | continued at that dose for 2-11 weeks |
| prednisone-taper | tapered off over 2-26 weeks |
| transplant-cd4 | CD4 count >200 cells/µL |
| transplant-pi-immunosuppressant-dose | immunosuppressant dose with protease inhibitor coadministration |
| tacrolimus-trough | Target trough: 5-15 ng/mL |
| cyclosporine-trough | Target trough: 150-450 ng/mL |
| sirolimus-trough | Target trough: 3-12 ng/mL |
| pediatric-tenofovir-age | children <2 years of age |
| antiretroviral-renal-dose | Dosing of Antiretroviral Drugs for HIV-Infected Adults With Chronic Kidney Disease or End-Stage Renal Disease |
| antimicrobial-renal-dose | Dosing of Antimicrobial Agents for HIV-Infected Patients With Chronic Kidney Disease or End-Stage Renal Disease |
| zidovudine-renal-dose | Zidovudine dosage for patients with CKD or ESRD |
| lamivudine-renal-dose | Lamivudine dosage for patients with CKD or ESRD |
| stavudine-ge60-renal-dose | Stavudine body weight >=60 kg dosage for patients with CKD or ESRD |
| stavudine-lt60-renal-dose | Stavudine body weight <60 kg dosage for patients with CKD or ESRD |
| didanosine-ge60-renal-dose | Didanosine delayed-release capsules body weight >=60 kg dosage for patients with CKD or ESRD |
| didanosine-lt60-renal-dose | Didanosine delayed-release capsules body weight <60 kg dosage for patients with CKD or ESRD |
| emtricitabine-renal-dose | Emtricitabine dosage for patients with CKD or ESRD |
| tenofovir-renal-dose | Tenofovir disoproxil fumarate dosage for patients with CKD or ESRD |
| emtricitabine-tenofovir-renal-dose | Emtricitabine/tenofovir disoproxil fumarate dosage for patients with CKD or ESRD |
| stribild-renal-dose | Elvitegravir, cobicistat, tenofovir disoproxil fumarate, emtricitabine dosage |
| dolutegravir-renal-dose | Dolutegravir dosage by CrCl |
| maraviroc-renal-dose | Maraviroc dosage for patients with CKD or ESRD |
| maraviroc-potent-cyp3a | Maraviroc with a potent CYP3A inhibitor |
| acyclovir-renal-dose | Acyclovir dosage for patients with CKD or ESRD |
| adefovir-renal-dose | Adefovir dosage for patients with CKD or ESRD |
| cidofovir-renal-dose | Cidofovir dosage for patients with CKD or ESRD |
| ciprofloxacin-renal-dose | Ciprofloxacin dosage for patients with CKD or ESRD |
| clarithromycin-renal-dose | Clarithromycin dosage for patients with CKD or ESRD |
| ethambutol-renal-dose | Ethambutol dosage for patients with CKD or ESRD |
| famciclovir-renal-dose | Famciclovir dosage for patients with CKD or ESRD |
| fluconazole-renal-dose | Fluconazole dosage for patients with CKD or ESRD |
| flucytosine-renal-dose | Flucytosine dosage by renal function |
| foscarnet-renal-dose | Foscarnet CMV induction and maintenance dosage by CrCl |
| ganciclovir-renal-dose | Ganciclovir induction and maintenance dosage by renal function |
| levofloxacin-renal-dose | Levofloxacin dosage for patients with CKD or ESRD |
| pentamidine-renal-dose | Pentamidine dosage for patients with CKD or ESRD |
| pyrazinamide-renal-dose | Pyrazinamide dosage for patients with CKD or ESRD |
| peginterferon-a2a-renal-dose | Peginterferon alfa-2a dosage by renal function |
| peginterferon-a2b-renal-dose | Peginterferon alfa-2b dosage by renal function |
| ribavirin-renal-dose | Ribavirin dosage for patients with CKD or ESRD |
| rifabutin-renal-dose | Rifabutin dosage by renal function |
| rifampin-renal-dose | Rifampin dosage for patients with CKD or ESRD |
| sulfadiazine-renal-dose | Sulfadiazine dosage by renal function |
| tmp-smx-prophylaxis-renal-dose | Trimethoprim-sulfamethoxazole prophylaxis dosage for patients with CKD or ESRD |
| tmp-smx-treatment-renal-dose | Trimethoprim-sulfamethoxazole treatment dosage for patients with CKD or ESRD |
| valacyclovir-renal-dose | Valacyclovir dosage for patients with CKD or ESRD |
| valganciclovir-renal-dose | Valganciclovir induction and maintenance dosage for patients with CKD or ESRD |
| abacavir-dose | Abacavir dosage for patients with CKD or ESRD |
| nonnucleoside-dose | No dose adjustment needed with CKD or ESRD for all NNRTIs |
| protease-inhibitor-dose | No dose adjustment needed with CKD or ESRD for all PIs |
| atazanavir-hemodialysis | Atazanavir use in patients receiving hemodialysis |
| lopinavir-ritonavir-hemodialysis | Lopinavir/ritonavir use in protease-inhibitor-experienced patients receiving hemodialysis |
| entry-inhibitor-dose | No dose adjustment needed with CKD or ESRD |
| raltegravir-dose | Raltegravir no dose adjustment needed with CKD or ESRD |
| amphotericin-deoxycholate-dose | Amphotericin B deoxycholate dosage for patients with CKD or ESRD |
| amphotericin-colloidal-dose | Amphotericin B colloidal dispersion dosage for patients with CKD or ESRD |
| amphotericin-lipid-dose | Amphotericin B lipid complex dosage for patients with CKD or ESRD |
| amphotericin-liposomal-dose | Amphotericin B liposomal dosage for patients with CKD or ESRD |
| isoniazid-dose | Isoniazid dosage for patients with CKD or ESRD |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-duration | hiv-adults-children-us | >3 months | RENDERED: present for >3 months | idsa-2014 | 1 | p1/narrative/ckd-duration | narrative |
| gfr-monitoring | stable-hiv | when ART starts or changes and at least twice yearly | when antiretroviral therapy (ART) is initiated or changed, and at least twice yearly in stable HIV-infected patients | idsa-2014 | 2 | p2/grade-terse/1 | strong, low |
| kidney-damage-monitoring | stable-hiv | baseline, when ART starts or changes, and at least annually | at baseline, when ART is initiated or changed, and at least annually in stable | idsa-2014 | 2 | p2/narrative/kidney-damage-monitoring | narrative |
| nephrology-referral | hiv-kidney-disease | GFR decline >25% from baseline and to <60 mL/minute/1.73 m2 that does not resolve after nephrotoxin removal | GFR decline by >25% from baseline and to a level <60 mL/minute/ 1.73 m2 | idsa-2014 | 3 | p3/grade-terse/3 | strong, low |
| nephrology-referral | hiv-kidney-disease | albuminuria >300 mg/day | albuminuria in excess of 300 mg per day | idsa-2014 | 3 | p3/grade-terse/3 | strong, low |
| nephrology-referral | hiv-kidney-disease | advanced CKD with GFR <30 mL/minute/1.73 m2 | advanced CKD management (GFR < 30 mL/minute/1.73 m2) | idsa-2014 | 3 | p3/grade-terse/3 | strong, low |
| tenofovir-avoidance-gfr | hiv-ckd | <60 mL/minute/1.73 m2 | GFR <60 mL/ minute/1.73 m2, we recommend avoiding tenofovir | idsa-2014 | 3 | p3/grade-terse/9 | strong, low |
| tenofovir-substitution | tenofovir-treated-decline | >25% decline from baseline and <60 mL/minute/1.73 m2 | RENDERED: GFR decline by >25% from baseline and to a level <60 mL/minute/1.73 m2 | idsa-2014 | 3 | p3/grade-terse/10 | strong, low |
| ace-arb-albuminuria | diabetic-albuminuria | >30 mg/day | >30 mg/day in diabetic patients | idsa-2014 | 3 | p3/grade-terse/11 | strong, high |
| ace-arb-albuminuria | nondiabetic-albuminuria | >300 mg/day | >300 mg/day in nondiabetic patients | idsa-2014 | 3 | p3/grade-terse/11 | strong, high |
| statin-cvd-risk | pre-esrd-ckd | >7.5% 10-year risk | >7.5% 10-year risk of cardiovascular disease | idsa-2014 | 3 | p3/grade-terse/12 | strong, high |
| aspirin-dose | hiv-ckd | 75-100 mg/day | aspirin (75-100 mg/day) | idsa-2014 | 3 | p3/grade-terse/13 | weak, high |
| bp-target-low-albuminuria | ckd-low-albuminuria | <140/90 mm Hg when albuminuria <30 mg/day | RENDERED: target blood pressure of <140/90 mm Hg in HIV-infected patients who have CKD with normal to mildly increased albuminuria (eg, <30 mg/day or equivalent) | idsa-2014 | 4 | p4/grade-terse/1 | strong, moderate |
| bp-target-higher-albuminuria | ckd-higher-albuminuria | <130/80 mm Hg when albuminuria >30-300 mg/day | RENDERED: target blood pressure of <130/80 mm Hg ... (eg, >30-300 mg/day or equivalent) | idsa-2014 | 4 | p4/grade-terse/2 | weak, low |
| pediatric-screening | children-adolescents-no-kidney-disease | estimated GFR when ART starts or changes and at least twice yearly | when ART is initiated or changed and at least twice yearly | idsa-2014 | 4 | p4/grade-terse/6 | strong, low |
| kidney-damage-monitoring | children-adolescents-stable | urinalysis or quantitative proteinuria when ART starts or changes and at least annually | when ART is initiated or changed, and at least annually in children and adolescents with stable kidney function | idsa-2014 | 4 | p4/narrative/pediatric-kidney-damage | narrative |
| ckd-gfr-definition | hiv-adults-children-us | <60 mL/minute/1.73 m2 for >3 months | RENDERED: GFR that persists below 60 mL/minute/1.73 m2 for >3 months | idsa-2014 | 6 | p6/narrative/ckd-gfr-definition | narrative |
| gfr-strata | hiv-adults-children-us | G1 >=90; G2 60-89; G3a 45-59; G3b 30-44; G4 15-29; G5 <15 mL/minute/1.73 m2 | RENDERED: GFR (mL/minute/1.73 m2): G1 (>=90); G2 (60-89); G3a (45-59); G3b (30-44); G4 (15-29); G5 (<15) | idsa-2014 | 6 | p6/narrative/gfr-strata | narrative |
| urine-collection-adequacy-men | men | 20-25 mg/kg/day creatinine | 20-25 and 15-20 mg/kg/day of creatinine in men and women | idsa-2014 | 7 | p7/narrative/urine-adequacy-men | narrative |
| urine-collection-adequacy-women | women | 15-20 mg/kg/day creatinine | 20-25 and 15-20 mg/kg/day of creatinine in men and women | idsa-2014 | 7 | p7/narrative/urine-adequacy-women | narrative |
| albuminuria-a1-stage | hiv-adults-children-us | AER <30 mg/24 h; ACR <3 mg/mmol or <30 mg/g | RENDERED: Normal to Mildly Increased (A1): AER, mg/24 h <30; ACR mg/mmol <3; mg/g <30 | idsa-2014 | 10 | p10/narrative/albuminuria-a1 | narrative |
| albuminuria-a2-stage | hiv-adults-children-us | AER 30-300 mg/24 h; ACR 3-30 mg/mmol or 30-300 mg/g | RENDERED: Moderately Increased (A2): AER, mg/24 h 30-300; ACR mg/mmol 3-30; mg/g 30-300 | idsa-2014 | 10 | p10/narrative/albuminuria-a2 | narrative |
| albuminuria-a3-stage | hiv-adults-children-us | AER >300 mg/24 h; ACR >30 mg/mmol or >300 mg/g | RENDERED: Severely Increased (A3): AER, mg/24 h >300; ACR mg/mmol >30; mg/g >300 | idsa-2014 | 10 | p10/narrative/albuminuria-a3 | narrative |
| proteinuria-a1-stage | hiv-adults-children-us | PER <150 mg/24 h; PCR <15 mg/mmol or <150 mg/g | RENDERED: Normal to Mildly Increased (A1): PER, mg/24 h <150; PCR mg/mmol <15; mg/g <150 | idsa-2014 | 10 | p10/narrative/proteinuria-a1 | narrative |
| proteinuria-a2-stage | hiv-adults-children-us | PER 150-500 mg/24 h; PCR 15-50 mg/mmol or 150-500 mg/g | RENDERED: Moderately Increased (A2): PER, mg/24 h 150-500; PCR mg/mmol 15-50; mg/g 150-500 | idsa-2014 | 10 | p10/narrative/proteinuria-a2 | narrative |
| proteinuria-a3-stage | hiv-adults-children-us | PER >500 mg/24 h; PCR >50 mg/mmol or >500 mg/g | RENDERED: Severely Increased (A3): PER, mg/24 h >500; PCR mg/mmol >50; mg/g >500 | idsa-2014 | 10 | p10/narrative/proteinuria-a3 | narrative |
| reagent-strip-a1-stage | hiv-adults-children-us | negative or trace | RENDERED: Protein reagent strip Negative or trace | idsa-2014 | 10 | p10/narrative/reagent-a1 | narrative |
| reagent-strip-a2-stage | hiv-adults-children-us | trace to 1+ | RENDERED: Protein reagent strip Trace to 1+ | idsa-2014 | 10 | p10/narrative/reagent-a2 | narrative |
| reagent-strip-a3-stage | hiv-adults-children-us | 1+ or greater | RENDERED: Protein reagent strip 1+ or greater | idsa-2014 | 10 | p10/narrative/reagent-a3 | narrative |
| proximal-phosphate-fe | hiv-adults-children-us | <10% normal; >20% abnormal | <10% is normal and >20% is abnormal | idsa-2014 | 12 | p12/narrative/phosphate-fe | narrative |
| proximal-phosphate-tmp-gfr | hiv-adults-children-us | normal 2.8-4.4 mg/dL; lower is abnormal | Lower than reference value (normal, 2.8-4.4 mg/dL) | idsa-2014 | 12 | p12/narrative/tmp-gfr | narrative |
| proximal-uric-acid-fe | hiv-adults-children-us | <15% normal; >20% abnormal | <15% is normal and >20% is abnormal | idsa-2014 | 12 | p12/narrative/uric-acid-fe | narrative |
| urine-albumin-protein-ratio | upcr-over-200 | <0.4 suggests tubulointerstitial; >0.4 suggests glomerular | uAPR <0.4 suggests predominantly tubulointerstitial disease, whereas uAPR >0.4 suggests predominantly glomerular disease | idsa-2014 | 12 | p12/narrative/uapr | narrative |
| stribild-renal-dose | crcl-lt70 | do not initiate when CrCl <70 mL/minute | estimated creatinine clear- ance <70 mL/minute | idsa-2014 | 13 | p13/narrative/stribild-initiation | narrative |
| stribild-renal-dose | crcl-lt50 | discontinue when CrCl <50 mL/minute | should be discontinued if estimated creatinine clearance falls below 50 mL/min | idsa-2014 | 13 | p13/narrative/stribild-discontinuation | narrative |
| proteinuria-dipstick-quantification | hiv-adults-children-us | proteinuria >=1+: quantify with albumin-to-creatinine ratio or protein-to-creatinine ratio | RENDERED: Proteinuria >=1+ on urinalysis should be quantified with either albumin-to-creatinine ratio ... or a protein-to-creatinine ratio | idsa-2014 | 15 | p15/narrative/proteinuria-quantification | narrative |
| gfr-method-near-60 | hiv-adults-children-us | near 60 mL/minute/1.73 m2: consider combined-biomarker CKD-EPI or exogenous GFR when greater accuracy would change management | RENDERED: estimated GFR-creatinine is near 60 mL/minute/1.73 m2, and a more accurate or precise GFR estimate would directly affect clinical management | idsa-2014 | 15 | p15/narrative/gfr-near-60 | narrative |
| biopsy-observation | hiv-kidney-disease | 24 hours | 24-hour postbiopsy observation period | idsa-2014 | 16 | p16/narrative/biopsy-observation | narrative |
| referral-before-dialysis | hiv-kidney-disease | >=1 year before dialysis | RENDERED: nephrology referral at least 1 year prior to the initiation of dialysis | idsa-2014 | 16 | p16/narrative/referral-before-dialysis | narrative |
| nephrology-referral-risk | hiv-kidney-disease | consider referral at GFR 30-59 mL/minute/1.73 m2 with ESRD risk factors | RENDERED: patients with GFR 30-59 mL/minute/1.73 m2 and ESRD risk factors | idsa-2014 | 16 | p16/narrative/referral-risk | narrative |
| maraviroc-potent-cyp3a | crcl-lt30 | contraindicated when CrCl <30 mL/minute with a potent CYP3A inhibitor | creatinine clearance <30 mL/ minute when combined with a potent CYP3A inhibitor | idsa-2014 | 17 | p17/narrative/maraviroc-potent-cyp3a | narrative |
| zidovudine-renal-dose | hiv-adults-ckd-esrd | usual 300 mg twice daily | RENDERED: Zidovudine Usual dosage 300 mg po bid | idsa-2014 | 18 | p18/narrative/zidovudine-usual | narrative |
| zidovudine-renal-dose | crcl-ge15 | no adjustment | RENDERED: CrCl >=15 mL/min No adjustment | idsa-2014 | 18 | p18/narrative/zidovudine-ge15 | narrative |
| zidovudine-renal-dose | crcl-lt15-dialysis | 100 mg every 6-8 hours or 300 mg daily; give after hemodialysis on dialysis days | RENDERED: CrCl <15 mL/min, hemodialysis, or peritoneal dialysis 100 mg po q6-8h or 300 mg qd; administer dose after hemodialysis | idsa-2014 | 18 | p18/narrative/zidovudine-lt15 | narrative |
| lamivudine-renal-dose | hiv-adults-ckd-esrd | usual 150 mg twice daily or 300 mg daily | RENDERED: Lamivudine Usual dosage 150 mg po bid/300 mg po qd | idsa-2014 | 18 | p18/narrative/lamivudine-usual | narrative |
| lamivudine-renal-dose | crcl-ge50 | no adjustment | RENDERED: CrCl >=50 mL/min No adjustment | idsa-2014 | 18 | p18/narrative/lamivudine-ge50 | narrative |
| lamivudine-renal-dose | crcl-30-49 | 150 mg daily | RENDERED: CrCl 30-49 mL/min 150 mg po qd | idsa-2014 | 18 | p18/narrative/lamivudine-30-49 | narrative |
| lamivudine-renal-dose | crcl-15-29 | 150 mg first dose, then 100 mg daily | RENDERED: CrCl 15-29 mL/min 150 mg po first dose, then 100 mg po qd | idsa-2014 | 18 | p18/narrative/lamivudine-15-29 | narrative |
| lamivudine-renal-dose | crcl-5-14 | 150 mg first dose, then 50 mg daily; some recommend 100 mg or 150 mg tablet daily in advanced renal disease | RENDERED: CrCl 5-14 mL/min 150 mg po first dose, then 50 mg po qd; some recommend 100 mg or 150 mg daily in advanced renal disease | idsa-2014 | 18 | p18/narrative/lamivudine-5-14 | narrative |
| lamivudine-renal-dose | crcl-lt5-dialysis | 50 mg first dose, then 25 mg daily; administer after hemodialysis on dialysis days | RENDERED: CrCl <5 mL/min, hemodialysis, or peritoneal dialysis 50 mg po first dose, then 25 mg po qd; administer dose after hemodialysis on days when hemodialysis performed | idsa-2014 | 18 | p18/narrative/lamivudine-lt5 | narrative |
| abacavir-dose | hiv-adults-ckd-esrd | usual 300 mg twice daily or 600 mg daily | RENDERED: Abacavir Usual dosage 300 mg po bid/600 mg po qd | idsa-2014 | 18 | p18/narrative/abacavir-usual | narrative |
| abacavir-dose | all-crcl | no adjustment; with hemodialysis, no adjustment and administer after hemodialysis on dialysis days | RENDERED: All CrCl No adjustment; Receiving hemodialysis No adjustment; administer dose after hemodialysis on days when hemodialysis performed | idsa-2014 | 18 | p18/narrative/abacavir-all | narrative |
| abacavir-dose | peritoneal-dialysis | unknown; use with caution | RENDERED: Receiving peritoneal dialysis Unknown, use with caution | idsa-2014 | 18 | p18/narrative/abacavir-pd | narrative |
| stavudine-ge60-renal-dose | body-ge60 | usual 40 mg twice daily; WHO recommends 30 mg twice daily | RENDERED: Body weight >=60 kg Usual dosage 40 mg po bid (WHO recommends 30 mg po bid) | idsa-2014 | 18 | p18/narrative/stavudine-ge60-usual | narrative |
| stavudine-ge60-renal-dose | crcl-gt50 | no adjustment | RENDERED: CrCl >50 mL/min No adjustment | idsa-2014 | 18 | p18/narrative/stavudine-ge60-gt50 | narrative |
| stavudine-ge60-renal-dose | crcl-26-50 | 20 mg twice daily | RENDERED: CrCl 26-50 mL/min 20 mg po bid | idsa-2014 | 18 | p18/narrative/stavudine-ge60-26-50 | narrative |
| stavudine-ge60-renal-dose | crcl-le25 | 20 mg daily | RENDERED: CrCl <=25 mL/min 20 mg po qd | idsa-2014 | 18 | p18/narrative/stavudine-ge60-le25 | narrative |
| stavudine-ge60-renal-dose | hemodialysis | 20 mg daily after hemodialysis | RENDERED: Receiving hemodialysis 20 mg po qd; give post-HD | idsa-2014 | 18 | p18/narrative/stavudine-ge60-hd | narrative |
| stavudine-ge60-renal-dose | peritoneal-dialysis | unknown; use with caution; dose reduction needed | RENDERED: Receiving peritoneal dialysis Unknown, use with caution (dose reduction needed) | idsa-2014 | 18 | p18/narrative/stavudine-ge60-pd | narrative |
| stavudine-lt60-renal-dose | body-lt60 | usual 30 mg twice daily | RENDERED: Body weight <60 kg Usual dosage 30 mg po bid | idsa-2014 | 18 | p18/narrative/stavudine-lt60-usual | narrative |
| stavudine-lt60-renal-dose | crcl-gt50 | no adjustment | RENDERED: CrCl >50 mL/min No adjustment | idsa-2014 | 18 | p18/narrative/stavudine-lt60-gt50 | narrative |
| stavudine-lt60-renal-dose | crcl-26-50 | 15 mg twice daily | RENDERED: CrCl 26-50 mL/min 15 mg po bid | idsa-2014 | 18 | p18/narrative/stavudine-lt60-26-50 | narrative |
| stavudine-lt60-renal-dose | crcl-le25 | 15 mg daily | RENDERED: CrCl <=25 mL/min 15 mg po qd | idsa-2014 | 18 | p18/narrative/stavudine-lt60-le25 | narrative |
| stavudine-lt60-renal-dose | hemodialysis | 15 mg daily after hemodialysis | RENDERED: Receiving hemodialysis 15 mg po qd; give post-HD | idsa-2014 | 18 | p18/narrative/stavudine-lt60-hd | narrative |
| stavudine-lt60-renal-dose | peritoneal-dialysis | unknown; use with caution; dose reduction needed | RENDERED: Receiving peritoneal dialysis Unknown, use with caution (dose reduction needed) | idsa-2014 | 18 | p18/narrative/stavudine-lt60-pd | narrative |
| didanosine-ge60-renal-dose | body-ge60 | usual 400 mg daily | RENDERED: Body weight >=60 kg Usual dosage 400 mg po qd | idsa-2014 | 18 | p18/narrative/didanosine-ge60-usual | narrative |
| didanosine-ge60-renal-dose | crcl-ge60 | no adjustment | RENDERED: CrCl >=60 mL/min No adjustment | idsa-2014 | 19 | p19/narrative/didanosine-ge60-ge60 | narrative |
| didanosine-ge60-renal-dose | crcl-30-59 | 200 mg daily | RENDERED: CrCl 30-59 mL/min 200 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-ge60-30-59 | narrative |
| didanosine-ge60-renal-dose | crcl-10-29 | 125 mg daily | RENDERED: CrCl 10-29 mL/min 125 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-ge60-10-29 | narrative |
| didanosine-ge60-renal-dose | crcl-lt10 | 125 mg daily | RENDERED: CrCl <10 mL/min 125 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-ge60-lt10 | narrative |
| didanosine-ge60-renal-dose | dialysis | 125 mg daily; after hemodialysis on dialysis days | RENDERED: Receiving hemodialysis 125 mg po qd; Receiving peritoneal dialysis 125 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-ge60-dialysis | narrative |
| didanosine-lt60-renal-dose | body-lt60 | usual 250 mg daily | RENDERED: Body weight <60 kg Usual dosage 250 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-lt60-usual | narrative |
| didanosine-lt60-renal-dose | crcl-ge60 | no adjustment | RENDERED: CrCl >=60 mL/min No adjustment | idsa-2014 | 19 | p19/narrative/didanosine-lt60-ge60 | narrative |
| didanosine-lt60-renal-dose | crcl-30-59 | 125 mg daily | RENDERED: CrCl 30-59 mL/min 125 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-lt60-30-59 | narrative |
| didanosine-lt60-renal-dose | crcl-10-29 | 125 mg daily | RENDERED: CrCl 10-29 mL/min 125 mg po qd | idsa-2014 | 19 | p19/narrative/didanosine-lt60-10-29 | narrative |
| didanosine-lt60-renal-dose | crcl-lt10-dialysis | do not use delayed-release capsules; use 75 mg pediatric powder daily | RENDERED: CrCl <10 mL/min, hemodialysis, or peritoneal dialysis Do not use didanosine delayed-release capsules; use 75 mg pediatric powder for suspension qd | idsa-2014 | 19 | p19/narrative/didanosine-lt60-lt10 | narrative |
| emtricitabine-renal-dose | hiv-adults-ckd-esrd | usual 200 mg daily | RENDERED: Emtricitabine Usual dosage 200 mg po qd | idsa-2014 | 19 | p19/narrative/emtricitabine-usual | narrative |
| emtricitabine-renal-dose | crcl-ge50 | no adjustment | RENDERED: CrCl >=50 mL/min No adjustment | idsa-2014 | 19 | p19/narrative/emtricitabine-ge50 | narrative |
| emtricitabine-renal-dose | crcl-30-49 | 200 mg every 48 hours | RENDERED: CrCl 30-49 mL/min 200 mg po q48h | idsa-2014 | 19 | p19/narrative/emtricitabine-30-49 | narrative |
| emtricitabine-renal-dose | crcl-15-29 | 200 mg every 72 hours | RENDERED: CrCl 15-29 mL/min 200 mg po q72h | idsa-2014 | 19 | p19/narrative/emtricitabine-15-29 | narrative |
| emtricitabine-renal-dose | crcl-lt15 | 200 mg every 96 hours | RENDERED: CrCl <15 mL/min 200 mg po q96h | idsa-2014 | 19 | p19/narrative/emtricitabine-lt15 | narrative |
| emtricitabine-renal-dose | hemodialysis | 200 mg every 96 hours after hemodialysis | RENDERED: Receiving hemodialysis 200 mg po q96h; administer dose after hemodialysis | idsa-2014 | 19 | p19/narrative/emtricitabine-hd | narrative |
| emtricitabine-renal-dose | peritoneal-dialysis | unknown; use with caution; dose reduction needed | RENDERED: Receiving peritoneal dialysis Unknown, use with caution (dose reduction needed) | idsa-2014 | 19 | p19/narrative/emtricitabine-pd | narrative |
| tenofovir-renal-dose | hiv-adults-ckd-esrd | usual 300 mg daily | RENDERED: Tenofovir disoproxil fumarate Usual dosage 300 mg po qd | idsa-2014 | 19 | p19/narrative/tenofovir-usual | narrative |
| tenofovir-renal-dose | crcl-ge50 | no adjustment | RENDERED: CrCl >=50 mL/min No adjustment | idsa-2014 | 19 | p19/narrative/tenofovir-ge50 | narrative |
| tenofovir-renal-dose | crcl-30-49 | 300 mg every 48 hours | RENDERED: CrCl 30-49 mL/min 300 mg po q48h | idsa-2014 | 19 | p19/narrative/tenofovir-30-49 | narrative |
| tenofovir-renal-dose | crcl-lt50-nondialysis | guideline recommends avoiding tenofovir | RENDERED: guideline recommends avoiding tenofovir in patients with CrCl <50 mL/min who are not on hemodialysis | idsa-2014 | 19 | p19/narrative/tenofovir-avoidance-nondialysis | narrative |
| tenofovir-renal-dose | crcl-10-29 | 300 mg every 72-96 hours | RENDERED: CrCl 10-29 mL/min 300 mg po q72-96h | idsa-2014 | 19 | p19/narrative/tenofovir-10-29 | narrative |
| tenofovir-renal-dose | hemodialysis | 300 mg every 7 days after hemodialysis on dialysis days; additional dose may be needed if >12 hours hemodialysis weekly | RENDERED: Receiving hemodialysis 300 mg po every 7 d (an additional dose may be needed if >12 h HD per week); administer dose after hemodialysis on days when hemodialysis performed | idsa-2014 | 19 | p19/narrative/tenofovir-hd | narrative |
| tenofovir-renal-dose | peritoneal-dialysis | unknown; use with caution; dose reduction needed | RENDERED: Receiving peritoneal dialysis Unknown, use with caution (dose reduction needed) | idsa-2014 | 19 | p19/narrative/tenofovir-pd | narrative |
| emtricitabine-tenofovir-renal-dose | hiv-adults-ckd-esrd | usual 200 mg/300 mg daily | RENDERED: Emtricitabine/tenofovir disoproxil fumarate Usual dosage 200 mg/300 mg po qd | idsa-2014 | 19 | p19/narrative/ftc-tdf-usual | narrative |
| emtricitabine-tenofovir-renal-dose | crcl-ge50 | no adjustment | RENDERED: CrCl >=50 mL/min No adjustment | idsa-2014 | 19 | p19/narrative/ftc-tdf-ge50 | narrative |
| emtricitabine-tenofovir-renal-dose | crcl-30-49 | one tablet every 48 hours | RENDERED: CrCl 30-49 mL/min One tablet po q48h | idsa-2014 | 19 | p19/narrative/ftc-tdf-30-49 | narrative |
| emtricitabine-tenofovir-renal-dose | crcl-lt30 | do not use combination tablet | RENDERED: CrCl <30 mL/min Should not use combination tablet | idsa-2014 | 19 | p19/narrative/ftc-tdf-lt30 | narrative |
| nonnucleoside-dose | hiv-adults-ckd-esrd | nevirapine 200 mg twice daily after 2 weeks at 200 mg daily; efavirenz 600 mg nightly; delavirdine 400 mg three times daily; etravirine 200 mg twice daily; rilpivirine 25 mg daily; no renal adjustment | RENDERED: No dose adjustment needed with CKD or ESRD for all NNRTIs; Nevirapine 200 mg po bid (after 2 wks of 200 mg po qd); Efavirenz 600 mg po qhs; Delavirdine 400 mg po tid; Etravirine 200 mg po bid; Rilpivirine 25 mg po qd | idsa-2014 | 20 | p20/narrative/nnrti | narrative |
| protease-inhibitor-dose | hiv-adults-ckd-esrd | indinavir 800 mg twice daily with ritonavir 100 mg twice daily; saquinavir 1000 mg twice daily with ritonavir 100 mg twice daily; nelfinavir 1250 mg twice daily or 750 mg three times daily; fosamprenavir 1400 mg daily with ritonavir 100-200 mg daily or 700 mg twice daily with ritonavir 100 mg twice daily; ritonavir 100-400 mg/day; lopinavir/ritonavir 400/100 mg twice daily or 800/200 mg daily; atazanavir 400 mg daily or 300 mg with ritonavir 100 mg daily; darunavir 800 mg with ritonavir 100 mg daily or 600 mg with ritonavir 100 mg twice daily; no renal adjustment | RENDERED: No dose adjustment needed with CKD or ESRD for all PIs; Indinavir 800 mg po bid with ritonavir 100 mg bid; Saquinavir 1000 mg po bid with ritonavir 100 mg bid; Nelfinavir 1250 mg po bid or 750 mg tid; Fosamprenavir 1400 mg po qd with ritonavir 100-200 mg qd OR 700 mg po bid with ritonavir 100 mg bid; Ritonavir 100-400 mg per day; Lopinavir/ritonavir 400 mg/100 mg po bid OR 800 mg/200 mg po qd; Atazanavir 400 mg po qd OR 300 mg po qd with ritonavir 100 mg po qd; Darunavir 800 mg po qd with ritonavir 100 mg po qd OR 600 mg po bid with ritonavir 100 mg bid | idsa-2014 | 20 | p20/narrative/protease-inhibitors | narrative |
| atazanavir-hemodialysis | hemodialysis | avoid unboosted atazanavir; do not initiate ritonavir-boosted atazanavir in ART-experienced patients | RENDERED: Avoid unboosted ATV in HD. Avoid boosted ATV in treatment-experienced patients on HD | idsa-2014 | 20 | p20/narrative/atazanavir-hemodialysis | narrative |
| lopinavir-ritonavir-hemodialysis | pi-experienced-hemodialysis | trough concentrations are lower; use with caution and monitor antiviral efficacy closely | RENDERED: LPV trough lower in HD; use with caution in PI-experienced patients | idsa-2014 | 20 | p20/narrative/lopinavir-hemodialysis | narrative |
| entry-inhibitor-dose | hiv-adults-ckd-esrd | enfuvirtide 90 mg subcutaneous twice daily; no renal adjustment | RENDERED: No dose adjustment needed with CKD or ESRD; Enfuvirtide 90 mg subcutaneous bid | idsa-2014 | 20 | p20/narrative/enfuvirtide | narrative |
| raltegravir-dose | hiv-adults-ckd-esrd | 400 mg twice daily; no renal adjustment | RENDERED: Raltegravir No dose adjustment needed with CKD or ESRD; Usual dosage 400 mg po bid | idsa-2014 | 20 | p20/narrative/raltegravir | narrative |
| stribild-renal-dose | crcl-ge70 | one tablet containing elvitegravir 150 mg, cobicistat 150 mg, emtricitabine 200 mg, and tenofovir disoproxil fumarate 300 mg daily with food | RENDERED: Usual dosage if CrCl >=70 mL/min 1 tablet (150 mg elvitegravir, 150 mg cobicistat, 200 mg emtricitabine, 300 mg tenofovir disoproxil fumarate) po qd with food | idsa-2014 | 20 | p20/narrative/stribild-ge70 | narrative |
| stribild-renal-dose | crcl-lt50 | discontinue when CrCl <50 mL/minute | RENDERED: CrCl <50 mL/min Discontinue | idsa-2014 | 20 | p20/narrative/stribild-lt50 | narrative |
| dolutegravir-renal-dose | hiv-adults-ckd-esrd | usual 50 mg once daily when ARV- or INSTI-naive; 50 mg twice daily when INSTI-experienced with certain INSTI mutations | RENDERED: Usual dose 50 mg once daily (ARV- or INSTI-naive patients); 50 mg twice daily (INSTI-experienced with certain INSTI mutations) | idsa-2014 | 20 | p20/narrative/dolutegravir-usual | narrative |
| dolutegravir-renal-dose | crcl-gt30 | usual dose | RENDERED: CrCl >30 mL/min Usual dose | idsa-2014 | 20 | p20/narrative/dolutegravir-gt30 | narrative |
| dolutegravir-renal-dose | crcl-lt30 | use with close monitoring; concentrations decrease 40%; INSTI-experienced patients with INSTI mutations may be at increased risk for virologic breakthrough | RENDERED: CrCl <30 mL/min Use with close monitoring; Dolutegravir concentrations decreased by 40%. Clinical significance unknown, but INSTI-experienced patients with INSTI mutations may be at increased risk for virologic breakthrough. | idsa-2014 | 21 | p21/narrative/dolutegravir-lt30 | narrative |
| maraviroc-renal-dose | hiv-adults-ckd-esrd | usual 300 mg twice daily, adjusted for most PI and NNRTI coadministration | RENDERED: Usual dosage 300 mg po bid (adjustment needed with most PI and NNRTI coadministration) | idsa-2014 | 21 | p21/narrative/maraviroc-usual | narrative |
| maraviroc-renal-dose | crcl-gt30 | no adjustment | RENDERED: CrCl >30 mL/min No dose adjustment | idsa-2014 | 21 | p21/narrative/maraviroc-gt30 | narrative |
| maraviroc-renal-dose | crcl-lt30 | 300 mg twice daily; reduce to 150 mg twice daily if orthostatic hypotension; avoid with CYP3A4 inhibitor | RENDERED: CrCl <30 mL/min 300 mg po bid. Reduce dose to 150 mg po bid if orthostatic hypotension occurs. Avoid maraviroc with CYP3A4 inhibitor | idsa-2014 | 21 | p21/narrative/maraviroc-lt30 | narrative |
| acyclovir-renal-dose | hiv-ckd-esrd | usual 200-800 mg oral 3-5 times/day or 5-10 mg/kg ideal body weight IV every 8 hours | RENDERED: Acyclovir Usual dosage 200-800 mg po 3-5 times per day; 5-10 mg/kg of ideal body weight IV q8h | idsa-2014 | 22 | p22/narrative/acyclovir-usual | narrative |
| acyclovir-renal-dose | crcl-25-50 | 200-800 mg oral 3-5 times/day or 5-10 mg/kg IV every 12 hours | RENDERED: CrCl 25-50 mL/min 200-800 mg po 3-5 times per day; 5-10 mg/kg of ideal body weight IV q12h | idsa-2014 | 22 | p22/narrative/acyclovir-25-50 | narrative |
| acyclovir-renal-dose | crcl-10-24 | 200-800 mg oral every 8 hours or 5-10 mg/kg IV every 24 hours | RENDERED: CrCl 10-24 mL/min 200-800 mg po q8h; 5-10 mg/kg of ideal body weight IV q24h | idsa-2014 | 22 | p22/narrative/acyclovir-10-24 | narrative |
| acyclovir-renal-dose | crcl-lt10 | 200-800 mg oral every 12 hours or 2.5-5 mg/kg IV every 24 hours | RENDERED: CrCl <10 mL/min 200-800 mg q12h; 2.5-5 mg/kg of ideal body weight IV q24h | idsa-2014 | 22 | p22/narrative/acyclovir-lt10 | narrative |
| acyclovir-renal-dose | hemodialysis | 2.5-5 mg/kg IV every 24 hours after hemodialysis | RENDERED: CrCl <10 mL/min receiving hemodialysis 2.5-5 mg/kg of ideal body weight IV q24h; on days of HD, dose post-HD | idsa-2014 | 22 | p22/narrative/acyclovir-hd | narrative |
| adefovir-renal-dose | hiv-ckd-esrd | usual 10 mg every 24 hours | RENDERED: Adefovir Usual dosage 10 mg po q24h | idsa-2014 | 22 | p22/narrative/adefovir-usual | narrative |
| adefovir-renal-dose | crcl-30-49 | 10 mg every 48 hours | RENDERED: CrCl 30-49 mL/min 10 mg q48h | idsa-2014 | 22 | p22/narrative/adefovir-30-49 | narrative |
| adefovir-renal-dose | crcl-10-29 | 10 mg every 72 hours | RENDERED: CrCl 10-29 mL/min 10 mg q72h | idsa-2014 | 22 | p22/narrative/adefovir-10-29 | narrative |
| adefovir-renal-dose | hemodialysis | 10 mg every 7 days after dialysis | RENDERED: Receiving hemodialysis 10 mg every 7 d following dialysis | idsa-2014 | 22 | p22/narrative/adefovir-hd | narrative |
| amphotericin-deoxycholate-dose | hiv-ckd-esrd | 0.7-1.0 mg/kg IV every 24 hours; no renal adjustment; consider lipid amphotericin formulations, azoles, or echinocandins | RENDERED: Amphotericin B deoxycholate 0.7-1.0 mg/kg IV q24h; No dose adjustment (but consider lipid amphotericin formulations, azoles, or echinocandins) | idsa-2014 | 22 | p22/narrative/amphotericin-deoxycholate | narrative |
| amphotericin-colloidal-dose | hiv-ckd-esrd | 3.0-6.0 mg/kg actual body weight IV every 24 hours; no renal adjustment | RENDERED: Amphotericin B colloidal dispersion 3.0-6.0 mg/kg of actual body weight IV q24h; No dose adjustment | idsa-2014 | 22 | p22/narrative/amphotericin-colloidal | narrative |
| amphotericin-lipid-dose | hiv-ckd-esrd | 5 mg/kg actual body weight IV every 24 hours; no renal adjustment | RENDERED: Amphotericin B lipid complex 5 mg/kg of actual body weight IV q24h; No dose adjustment | idsa-2014 | 22 | p22/narrative/amphotericin-lipid | narrative |
| amphotericin-liposomal-dose | hiv-ckd-esrd | 4.0-6.0 mg/kg actual body weight IV every 24 hours; no renal adjustment | RENDERED: Amphotericin B liposomal 4.0-6.0 mg/kg of actual body weight IV q24h; No dose adjustment | idsa-2014 | 22 | p22/narrative/amphotericin-liposomal | narrative |
| cidofovir-renal-dose | hiv-ckd-esrd | usual 5 mg/kg IV weekly x 2 weeks, then every other week with probenecid and hydration | RENDERED: Cidofovir Usual dosage 5 mg/kg IV q week x 2 wk, then every other week (with probenecid and hydration) | idsa-2014 | 22 | p22/narrative/cidofovir-usual | narrative |
| cidofovir-renal-dose | impaired-kidney-function | creatinine increase 0.3-0.4: 3 mg/kg every other week; increase >=0.5 or grade 3+ proteinuria: discontinue; baseline creatinine >1.5, CrCl <=55, or grade >=2+ proteinuria: not recommended | RENDERED: Increase in serum creatinine level to 0.3-0.4 above baseline 3 mg/kg every other week; increase >=0.5 above baseline or grade 3+ proteinuria Discontinue; baseline serum creatinine >1.5, CrCl <=55 mL/min, or grade >=2+ proteinuria Not recommended | idsa-2014 | 22 | p22/narrative/cidofovir-adjust | narrative |
| ciprofloxacin-renal-dose | hiv-ckd-esrd | usual 500-750 mg oral every 12 hours or source prints `400 IV` every 8-12 hours, omitting mg | RENDERED: Ciprofloxacin Usual dosage 500-750 mg po q12h OR 400 IV q8h-12h | idsa-2014 | 22 | p22/narrative/ciprofloxacin-usual | narrative |
| ciprofloxacin-renal-dose | crcl-30-50 | 500-750 mg oral every 12 hours or source prints `400 IV` every 12 hours, omitting mg | RENDERED: CrCl 30-50 mL/min 500-750 mg q12h OR 400 IV q12h | idsa-2014 | 22 | p22/narrative/ciprofloxacin-30-50 | narrative |
| ciprofloxacin-renal-dose | crcl-lt30 | 250-500 mg oral every 18-24 hours or source prints `400 IV` every 24 hours, omitting mg | RENDERED: CrCl <30 mL/min 250-500 mg q18-24h OR 400 IV q24h | idsa-2014 | 22 | p22/narrative/ciprofloxacin-lt30 | narrative |
| ciprofloxacin-renal-dose | hemodialysis | 250-500 mg oral every 24 hours or source prints `200-400 IV` every 24 hours after hemodialysis, omitting mg | RENDERED: Receiving hemodialysis 250-500 mg q24h OR 200-400 IV q24h (days of HD dose post-HD) | idsa-2014 | 22 | p22/narrative/ciprofloxacin-hd | narrative |
| clarithromycin-renal-dose | hiv-ckd-esrd | usual 500 mg every 12 hours | RENDERED: Clarithromycin Usual dosage 500 mg po q12h | idsa-2014 | 22 | p22/narrative/clarithromycin-usual | narrative |
| clarithromycin-renal-dose | impaired-kidney-function | CrCl <30: reduce by 50%; with PI, reduce 50% at CrCl 30-60 and 75% at CrCl <30 | RENDERED: Reduce dose by one-half if CrCl <30 mL/min. With PI coadministration, dose reduction by 50% with CrCl 30-60 mL/min and 75% reduction with CrCl <30 mL/min | idsa-2014 | 22 | p22/narrative/clarithromycin-adjust | narrative |
| ethambutol-renal-dose | hiv-ckd-esrd | usual 15-25 mg/kg every 24 hours | RENDERED: Ethambutol Usual dosage 15-25 mg/kg of body weight po q24h | idsa-2014 | 22 | p22/narrative/ethambutol-usual | narrative |
| ethambutol-renal-dose | crcl-10-50 | 15-25 mg/kg every 24-36 hours | RENDERED: CrCl 10-50 mL/min 15-25 mg/kg of body weight po q24-36h | idsa-2014 | 22 | p22/narrative/ethambutol-10-50 | narrative |
| ethambutol-renal-dose | crcl-lt10 | 15-25 mg/kg every 48 hours | RENDERED: CrCl <10 mL/min 15-25 mg/kg of body weight po q48h | idsa-2014 | 22 | p22/narrative/ethambutol-lt10 | narrative |
| famciclovir-renal-dose | hiv-ckd-esrd | usual 500 mg every 12 hours for HSV or source prints `500 q8h` for VZV, omitting mg | RENDERED: Famciclovir Usual dosage 500 mg po q12h (HSV) or 500 q8h (VZV) | idsa-2014 | 22 | p22/narrative/famciclovir-usual | narrative |
| famciclovir-renal-dose | crcl-20-39 | 500 mg every 24 hours | RENDERED: CrCl 20-39 mL/min 500 mg q24h | idsa-2014 | 22 | p22/narrative/famciclovir-20-39 | narrative |
| famciclovir-renal-dose | crcl-lt20 | 250 mg every 24 hours | RENDERED: CrCl <20 mL/min 250 mg q24h | idsa-2014 | 22 | p22/narrative/famciclovir-lt20 | narrative |
| famciclovir-renal-dose | hemodialysis | 250 mg after each dialysis | RENDERED: Receiving hemodialysis 250 mg after each dialysis | idsa-2014 | 22 | p22/narrative/famciclovir-hd | narrative |
| fluconazole-renal-dose | hiv-ckd-esrd | usual 200-1200 mg every 24 hours; CrCl <=50: half-dose; hemodialysis: full dose after dialysis | RENDERED: Usual dosage 200-1200 mg po q24h; CrCl <=50 mL/min Half-dose; Receiving hemodialysis Full dose after dialysis | idsa-2014 | 23 | p23/narrative/fluconazole | narrative |
| flucytosine-renal-dose | hiv-ckd-esrd | target 30-80 mcg/mL 2 hours postdose; usual 25 mg/kg every 6 hours; CrCl 20-40: every 12 hours; 10-20: every 24 hours; <10: every 48 hours | RENDERED: target 30-80 mcg/mL (2 h postdose); Usual dosage 25 mg/kg q6h; 20-40 mL/min 25 mg/kg q12h; 10-20 mL/min 25 mg/kg q24h; <10 mL/min 25 mg/kg q48h | idsa-2014 | 23 | p23/narrative/flucytosine | narrative |
| foscarnet-renal-dose | impaired-kidney-function | CrCl >1.4 mL/min/kg: 90 mg/kg every 12 hours induction and every 24 hours maintenance; 1.0-1.4: 70 mg/kg on those schedules; 0.8-1.0: 50 mg/kg; 0.6-0.8: 80 mg/kg every 24/48 hours; 0.5-0.6: 60 mg/kg every 24/48 hours; 0.4-0.5: 50 mg/kg every 24/48 hours; <0.4: not recommended | RENDERED: >1.4 90 mg/kg q12h 90 mg/kg q24h; 1.0-1.4 70 mg/kg q12h 70 mg/kg q24h; 0.8-1.0 50 mg/kg q12h 50 mg/kg q24h; 0.6-0.8 80 mg/kg q24h 80 mg/kg q48h; 0.5-0.6 60 mg/kg q24h 60 mg/kg q48h; 0.4-0.5 50 mg/kg q24h 50 mg/kg q48h; <0.4 Not recommended | idsa-2014 | 23 | p23/narrative/foscarnet | narrative |
| ganciclovir-renal-dose | hiv-ckd-esrd | usual 5 mg/kg every 12 hours induction and every 24 hours maintenance; CrCl 50-69: 2.5 mg/kg every 12/24 hours; 25-49: 2.5/1.25 mg/kg every 24 hours; 10-24: 1.25/0.625 mg/kg every 24 hours; <10 or hemodialysis: 1.25/0.625 mg/kg three times weekly after dialysis | RENDERED: Usual dosage 5 mg/kg q12h (I); 5 mg/kg q24h (M); 50-69 mL/min 2.5 mg/kg q12h (I); 2.5 mg/kg q24h (M); 25-49 mL/min 2.5 mg/kg q24h (I); 1.25 mg/kg q24h (M); 10-24 mL/min 1.25 mg/kg q24h (I); 0.625 mg/kg q24h (M); <10 mL/min; HD 1.25 mg/kg TIW (I) post-HD; 0.625 mg/kg TIW (M) post-HD | idsa-2014 | 23 | p23/narrative/ganciclovir | narrative |
| isoniazid-dose | hiv-ckd-esrd | 300 mg every 24 hours; after hemodialysis on dialysis days | RENDERED: Isoniazid 300 mg q24h (on days of HD, dose post-HD) | idsa-2014 | 23 | p23/narrative/isoniazid | narrative |
| levofloxacin-renal-dose | hiv-ckd-esrd | usual 250-750 mg every 24 hours; for 500 mg daily regimen, CrCl 20-49: 500 mg load then 250 mg daily; 10-19: 500 mg load then 250 mg every 48 hours; dialysis: source prints 750-500 mg load then 250-500 mg every 48 hours, dose post-HD on dialysis days | RENDERED: Usual dosage 250-750 mg po q24h; CrCl 20-49 mL/min 500 mg loading dose, then 250 mg q24h; CrCl 10-19 mL/min 500 mg loading dose, then 250 mg q48h; Receiving hemodialysis or PD 750-500 mg loading dose, then 250-500 mg q48h (dose post-HD on days of dialysis) | idsa-2014 | 23 | p23/narrative/levofloxacin | narrative |
| pentamidine-renal-dose | hiv-ckd-esrd | usual 4.0 mg/kg IV every 24 hours; CrCl 10-50: 3.0 mg/kg every 24 hours, use with caution; <10: source prints 4.0 mg/kg every `q-48h` | RENDERED: Usual dosage 4.0 mg/kg IV q24h; CrCl 10-50 mL/min 3.0 mg/kg IV q24h (use with caution); CrCl <10 mL/min 4.0 mg/kg IV q-48h | idsa-2014 | 23 | p23/narrative/pentamidine | narrative |
| pyrazinamide-renal-dose | hiv-ckd-esrd | usual 20-25 mg/kg every 24 hours; CrCl <10: 15-20 mg/kg every 24 hours; hemodialysis: 20 mg/kg every 24 hours after dialysis | RENDERED: Usual dosage 20-25 mg/kg q24h; CrCl <10 mL/min 15-20 mg/kg q24h; Receiving hemodialysis 20 mg/kg q24h (dose post-HD) | idsa-2014 | 23 | p23/narrative/pyrazinamide | narrative |
| peginterferon-a2a-renal-dose | hiv-ckd-esrd | usual 180 mcg/kg weekly; CrCl <30 or hemodialysis: 135 mcg/kg weekly | RENDERED: Usual dosage 180 mcg/kg weekly; <30 mL/min; HD 135 mcg/kg weekly | idsa-2014 | 23 | p23/narrative/peginterferon-a2a | narrative |
| peginterferon-a2b-renal-dose | hiv-ckd-esrd | usual 1.5 mcg/kg weekly; CrCl 30-50: reduce 25%; 10-29 or hemodialysis: reduce 50% | RENDERED: Usual dosage 1.5 mcg/kg q wk; 30-50 mL/min Decrease dose by 25%; 10-29 mL/min; HD Decrease dose by 50% | idsa-2014 | 23 | p23/narrative/peginterferon-a2b | narrative |
| ribavirin-renal-dose | hiv-ckd-esrd | usual 800-1200 mg/day in 2 doses; CrCl 30-50: alternate 200 and 400 mg every other day; <30 or hemodialysis: 200 mg daily | RENDERED: Usual dosage 800-1200 mg/day in 2 divided doses; CrCl 30-50 mL/min Alternate 200 mg and 400 mg qod; CrCl <30 mL/min 200 mg qd; CrCl <10 mL/min on HD 200 mg/d | idsa-2014 | 24 | p24/narrative/ribavirin | narrative |
| rifabutin-renal-dose | hiv-ckd-esrd | usual 300 mg every 24 hours with dose adjustment for PI/r coadministration; CrCl <30: consider 50% dose reduction | RENDERED: Usual dosage 300 mg po q24h (dose adjustment needed with PI/r coadministration); <30 mL/min Consider 50% dose reduction | idsa-2014 | 24 | p24/narrative/rifabutin | narrative |
| rifampin-renal-dose | hiv-ckd-esrd | usual 600 mg every 24 hours; CrCl 10-50: 100% dose; <10: 50%-100%; hemodialysis: 50%-100%, no supplement; peritoneal dialysis: 50%-100% plus another 50%-100% after dialysis, therapeutic drug monitoring recommended | RENDERED: Usual dosage 600 mg po q24h; CrCl 10-50 mL/min 100% of full dose; CrCl <10 mL/min 50%-100% of full dose; Receiving hemodialysis 50%-100% of full dose; no supplement; Receiving peritoneal dialysis 50%-100% of full dose; extra 50%-100% of full dose after receipt of peritoneal dialysis. Therapeutic drug monitoring recommended | idsa-2014 | 24 | p24/narrative/rifampin | narrative |
| sulfadiazine-renal-dose | hiv-ckd-esrd | usual 1-1.5 g every 6 hours, 1.5 g when >60 kg; CrCl 10-50: 1-1.5 g every 12 hours; <10 or hemodialysis: 1-1.5 g every 24 hours | RENDERED: Usual dosage 1-1.5 g po q6h (1.5 g for >60 kg); 10-50 mL/min 1-1.5 g po q12h; <10 mL/min; HD 1-1.5 g po q24h | idsa-2014 | 24 | p24/narrative/sulfadiazine | narrative |
| tmp-smx-prophylaxis-renal-dose | hiv-ckd-esrd | usual one double-strength dose daily, one double-strength dose 3 times/week, or one single-strength dose daily; CrCl 15-30: half-dose; <15: half-dose or alternative agent | RENDERED: Usual dosage 1 double-strength dose po q24h; 1 double-strength dose po 3 times per week; 1 single-strength dose po q24h; CrCl 15-30 mL/min Half-dose; CrCl <15 mL/min Half-dose or use alternative agent | idsa-2014 | 24 | p24/narrative/tmp-smx-prophylaxis | narrative |
| tmp-smx-treatment-renal-dose | hiv-ckd-esrd | usual trimethoprim 5 mg/kg every 6-8 hours; CrCl 10-30: every 12 hours; <10: every 24 hours | RENDERED: Usual dosage 5 mg/kg (as trimethoprim component) IV or po q6-8h; CrCl 10-30 mL/min 5 mg per kg q12h; CrCl <10 mL/min 5 mg per kg q24h | idsa-2014 | 24 | p24/narrative/tmp-smx-treatment | narrative |
| valacyclovir-renal-dose | hiv-ckd-esrd | usual 500 mg-1 g every 8 hours; CrCl 30-49: 500 mg-1 g every 12 hours; 10-20: source prints 500-1 g mg every 24 hours; <10: 500 mg every 24 hours | RENDERED: Usual dosage 500 mg-1 g po q8h; CrCl 30-49 mL/min 500 mg-1 g po q12h; CrCl 10-20 mL/min 500-1 g mg po q24h; CrCl <10 mL/min 500 mg po q24h | idsa-2014 | 24 | p24/narrative/valacyclovir | narrative |
| valganciclovir-renal-dose | hiv-ckd-esrd | usual 900 mg every 12 hours induction and 900 mg every 24 hours maintenance; CrCl 40-59: 450 mg every 12/24 hours; 25-39: 450 mg daily/every other day; 10-24: source prints `450 mg qod I)` induction and 450 mg twice weekly maintenance; <10: manufacturer does not recommend, use IV ganciclovir or consider 200/100 mg suspension three times weekly; hemodialysis: consider 200/100 mg three times weekly | RENDERED: Usual dosage 900 mg po q12h (I); 900 mg po q24h (M); CrCl 40-59 mL/min 450 mg q12h (I); 450 mg qd (M); CrCl 25-39 mL/min 450 mg qd (I); 450 mg qod (M); CrCl 10-24 mL/min 450 mg qod I); 450 mg twice per wk (M); CrCl <10 mL/min Not recommended by US manufacturer. Use IV ganciclovir or consider 200 mg suspension tiw (I)/100 mg suspension tiw (M); Receiving hemodialysis Consider 200 mg oral powder formulation tiw (I); 100 mg tiw (M) | idsa-2014 | 24 | p24/narrative/valganciclovir | narrative |
| tenofovir-discontinuation-evidence | tenofovir-treated-decline | >25% decline from baseline and <60 mL/minute/1.73 m2, especially with proximal tubular dysfunction | reduced GFR (ie, by >25% from baseline and to a level <60 mL/minute/1.73 m2) | idsa-2014 | 25 | p25/narrative/tenofovir-discontinue | narrative |
| urine-albumin-protein-ratio-tenofovir | impaired-kidney-function | <0.4 may distinguish predominantly proximal tubular from glomerular proteinuria | urinary albumin-total protein ratio <0.4 | idsa-2014 | 25 | p25/narrative/uapr-tenofovir | narrative |
| ace-arb-monitoring | hiv-ckd | when GFR <45 mL/minute/1.73 m2, check GFR and potassium within 1 week after start or dose escalation | GFR <45 mL/minute/1.73 m2, in whom GFR and potassium should be measured within 1 week of starting | idsa-2014 | 27 | p27/narrative/ace-arb-monitoring | narrative |
| prednisone-hivan | biopsy-hivan | 60 mg/day or 1 mg/kg/day | prednisone 60 mg/day or the equivalent of 1 mg/kg of prednisone per day | idsa-2014 | 28 | p28/narrative/prednisone-dose | narrative |
| prednisone-response | biopsy-hivan | assess response after 1-4 weeks; rapidly taper nonresponders | patients who do not respond after 1-4 weeks of prednisone should be rapidly tapered | idsa-2014 | 28 | p28/narrative/prednisone-response | narrative |
| prednisone-continuation | biopsy-hivan | responders: continue dose 2-11 weeks | RENDERED: responders were continued at that dose for 2-11 weeks then tapered off over 2-26 weeks | idsa-2014 | 28 | p28/narrative/prednisone-continuation | narrative |
| prednisone-taper | biopsy-hivan | taper over 2-26 weeks | RENDERED: responders were continued at that dose for 2-11 weeks then tapered off over 2-26 weeks | idsa-2014 | 28 | p28/narrative/prednisone-taper | narrative |
| transplant-cd4 | transplant-candidates | >200 cells/mcL and undetectable HIV RNA on stable ART | RENDERED: CD4 count >200 cells/µL ... undetectable plasma HIV RNA on a stable ART regimen | idsa-2014 | 29 | p29/narrative/transplant-cd4 | narrative |
| transplant-pi-immunosuppressant-dose | transplant-candidates | some patients require only 1%-2% of a typical immunosuppressant dose with protease inhibitors | some patients require only 1%-2% of a typical dose of the immunosuppressive drug | idsa-2014 | 29 | p29/narrative/pi-immunosuppressant-dose | narrative |
| pediatric-tenofovir-age | children-under-2 | not recommended <2 years; FDA approved for >=2 years | RENDERED: tenofovir is not recommended for children <2 years of age ... approved tenofovir for use in children aged >=2 years | idsa-2014 | 30 | p30/narrative/pediatric-tenofovir-under2 | narrative |
| pediatric-tenofovir-age | pediatric-tanner-1-3 | avoid as first-line treatment at Tanner stages 1-3 | RENDERED: not recommended as part of first-line treatment in children with Tanner stages 1-3 | idsa-2014 | 30 | p30/narrative/pediatric-tenofovir-tanner | narrative |
| tacrolimus-trough | renal-transplant-hiv | 5-15 ng/mL | RENDERED: Target trough: 5-15 ng/mL | idsa-2014 | 31 | p31/narrative/tacrolimus-trough | narrative |
| cyclosporine-trough | renal-transplant-hiv | 150-450 ng/mL | RENDERED: Target trough: 150-450 ng/mL | idsa-2014 | 31 | p31/narrative/cyclosporine-trough | narrative |
| sirolimus-trough | renal-transplant-hiv | 3-12 ng/mL | RENDERED: Target trough: 3-12 ng/mL | idsa-2014 | 31 | p31/narrative/sirolimus-trough | narrative |

## Conflicts

The tenofovir dosing table supplies reduced-frequency schedules below CrCl 50 mL/min,
while its own comment says this guideline recommends avoiding tenofovir below that
threshold in patients not receiving hemodialysis. The narrative likewise permits
carefully monitored, renally adjusted use when treatment options are limited or
tenofovir is needed for hepatitis B. These are conditional fallback dosing instructions
beside a preferred avoidance recommendation, not two incompatible cutoffs. The source
also advises avoiding concurrent nephrotoxic drugs when feasible and describes greater
GFR declines with tenofovir plus atazanavir, amprenavir, or a ritonavir-boosted protease
inhibitor; those context statements do not create a different numeric cutoff.

CONFLICT: nephrology-referral uses `GFR decline >25% from baseline and to <60 mL/minute/1.73 m2 that does not resolve after nephrotoxin removal`, `albuminuria >300 mg/day`, and `advanced CKD with GFR <30 mL/minute/1.73 m2` as complementary referral triggers, not competing thresholds.

## Coverage

The source recommendation record is `bound`. Its 48 marker occurrences are fully
accounted for below without claiming that its running-text marker found every
recommendation. Ten occurrences are cited and 38 are dispositioned. Rows above cite the numeric occurrences on pages 2-4; the detailed
restatements and word-only recommendations are dispositioned here.

- `p3/grade-terse/2` - the 24-hour urine collection is represented by the referral/evaluation material but the remaining checklist is word-only
- `p3/grade-terse/1` - page-break continuation of the annual kidney-damage monitoring recommendation represented by the page-2 narrative row
- `p3/grade-terse/4` - word-only permanent-access recommendation
- `p3/grade-terse/5` - word-only catheter-avoidance recommendation
- `p3/grade-terse/6` - word-only ART recommendation
- `p3/grade-terse/7` - word-only equation-choice recommendation; formula coefficients are scoped out
- `p3/grade-terse/8` - word-only ART recommendation
- `p4/grade-terse/3` - word-only corticosteroid recommendation; dose and durations are represented from page 28
- `p4/grade-terse/4` - word-only transplant-assessment recommendation
- `p4/grade-terse/5` - word-only interaction-minimization recommendation; numeric troughs are represented from page 31
- `p4/grade-terse/7` - Tanner stages 1-3 boundary is represented from the detailed pediatric discussion on page 30
- `p4/grade-terse/8` - word-only pediatric ART and referral recommendation
- `p4/grade-terse/9` - word-only ACE inhibitor/ARB caution
- `p4/grade-terse/10` - word-only pediatric corticosteroid recommendation
- `p14/grade-terse/1` - detailed duplicate of the twice-yearly monitoring recommendation represented from page 2
- `p14/grade-terse/2` - detailed duplicate of the annual kidney-damage monitoring recommendation represented from page 3
- `p15/grade-terse/1` - detailed duplicate of the evaluation recommendation; the 24-hour collection is represented in the page-3 summary material
- `p16/grade-terse/1` - detailed duplicate of the nephrology-referral thresholds represented from page 3
- `p16/grade-terse/2` - detailed duplicate of the word-only permanent-access recommendation
- `p16/grade-terse/3` - detailed duplicate of the word-only catheter-avoidance recommendation
- `p17/grade-terse/1` - detailed duplicate of the word-only ART recommendation
- `p17/grade-terse/2` - detailed duplicate of the word-only equation-choice recommendation
- `p17/grade-terse/3` - detailed duplicate of the word-only HIVAN ART recommendation
- `p17/grade-terse/4` - detailed duplicate of the tenofovir-avoidance threshold represented from page 3
- `p17/grade-terse/5` - detailed duplicate of the tenofovir-substitution threshold represented from pages 3 and 25
- `p26/grade-terse/1` - detailed duplicate of the diabetic and nondiabetic albuminuria thresholds represented from page 3
- `p26/grade-terse/2` - detailed duplicate of the statin cardiovascular-risk threshold represented from page 3
- `p26/grade-terse/3` - detailed duplicate of the aspirin dose represented from page 3
- `p28/grade-terse/1` - detailed duplicate of the <140/90 mm Hg target represented from page 3
- `p28/grade-terse/2` - detailed duplicate of the <130/80 mm Hg target represented from page 4
- `p28/grade-terse/3` - word-only corticosteroid recommendation; dose and duration are represented from page 28 narrative
- `p29/grade-terse/1` - truncated word-only transplant-assessment recommendation; CD4 eligibility is represented from page 29 narrative
- `p29/grade-terse/2` - word-only interaction-minimization recommendation; trough targets are represented from page 31
- `p30/grade-terse/1` - detailed duplicate of pediatric monitoring frequencies represented from page 4
- `p30/grade-terse/2` - detailed duplicate of Tanner stages 1-3 avoidance represented from page 30 narrative
- `p30/grade-terse/3` - word-only pediatric ART and referral recommendation
- `p30/grade-terse/4` - word-only ACE inhibitor/ARB caution
- `p30/grade-terse/5` - word-only pediatric corticosteroid recommendation

The cited recommendation identifiers not listed above are `p2/grade-terse/1`,
`p3/grade-terse/3`, `p3/grade-terse/9`,
`p3/grade-terse/10`, `p3/grade-terse/11`, `p3/grade-terse/12`,
`p3/grade-terse/13`, `p4/grade-terse/1`, `p4/grade-terse/2`, and
`p4/grade-terse/6`.
