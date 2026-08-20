# Diabetes — threshold sheet

<!-- schema: threshold-sheet/1 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

**Every `snippet` cell is the shortest verbatim ADA fragment that carries the
decision point.** It is what the citation gates check against — paraphrase it and a
fabricated citation stops being detectable. The quotation quantity for this sheet is
measured independently in [README.md](README.md#the-quoting-posture-ruled-against-a-public-repo)
and re-derived by a test.


## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| ada-2026 | ADA | ADA/standards-of-care-2026 | 2026 | 2026 | https://diabetesjournals.org/care/issue/49/Supplement_1 | bound |

## Scope

**Read:** every record emitted by `tools/guidelines_recs.py` from the source's
`Recommendation` markers — **126 records carrying 116 distinct identifiers**. The
marker-bound extraction includes 98 change-summary records from pages 12–18 rather
than recommendation statements; their 88 distinct identifiers are named under
[Coverage](#coverage). Of the 28 remaining records, 14 identifiers produce the 25
decision-point rows below and 14 are scoped out by identifier.

**Not read:** narrative statements, evidence tables, appendices, and decision points
outside those extracted markers. A number stated only in those places is not here,
so **absent from this sheet does not mean absent from the guideline.** The source is
`bound`, so even an omission from the marker set warns rather than refuses.

citations resolved against C:/codeing/guidelines-src on 2026-08-20


## Populations

| key | verbatim |
| --- | --- |
| post-acute-pancreatitis | Screen people for diabetes within 3–6 months following an episode of acute pancreatitis |
| chronic-pancreatitis | people with chronic pancreatitis |
| stage2-t1d-age8plus | selected individuals aged ≥8 years with stage 2 type 1 diabetes |
| diabetes-household | people with diabetes, caregivers, and family members |
| adults-t1d-obesity | adults with type 1 diabetes who have obesity |
| asian-adults-t1d-obesity | Asian American individuals |
| people-diabetes | people with diabetes |
| people-diabetes-htn | Individuals with hypertension |
| people-ckd-albuminuria300 | people with CKD and albuminuria ≥300 mg/g |
| people-ckd-g3plus | people with CKD stage G3 or higher |
| people-dialysis | individuals on dialysis |
| people-ckd-albuminuria | people with CKD and albuminuria |
| adults-t2d-uacr100-egfr30-90 | adults with type 2 diabetes and UACR ≥100 mg/g with eGFR 30–90 mL/min/1.73 m2 |
| people-egfr-under20-nondialysis | individuals with eGFR <20 mL/min/1.73 m2 and not on dialysis |
| adults-diabetes-age65plus | adults 65 years of age or older |
| pediatric-diabetes | children and adolescents with diabetes and their parents or caregivers |
| pregnancy-t1d-t2d | pregnant individuals with type 1 or type 2 diabetes |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| post-pancreatitis-initial-screening-interval | post-acute-pancreatitis | 3-6 months | "within 3–6 months following an episode of acute pancreatitis" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| post-pancreatitis-ongoing-screening-interval | post-acute-pancreatitis | annually | "RENDERED: and annually thereafter" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| chronic-pancreatitis-screening-interval | chronic-pancreatitis | annually | "annually for people with chronic pancreatitis" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| teplizumab-discussion-age-threshold | stage2-t1d-age8plus | >=8 years | "selected individuals aged ≥8 years with stage 2 type 1 diabetes" | ada-2026 | p62 | p62/recommendation/3.17 | B |
| diabetes-distress-screening-interval | diabetes-household | at least annually | "at least annually in people with diabetes, caregivers, and family members" | ada-2026 | p116 | p116/recommendation/5.45 | B |
| obesity-bmi-threshold | adults-t1d-obesity | >=30.0 kg/m2 | "obesity (BMI ≥30.0 kg/m2" | ada-2026 | p183 | p183/recommendation/8.29 | B/C |
| obesity-bmi-threshold | asian-adults-t1d-obesity | >=27.5 kg/m2 | "or ≥27.5 kg/m2 in Asian American" | ada-2026 | p183 | p183/recommendation/8.29 | B/C |
| lifestyle-counseling-bp-threshold | people-diabetes | >120/80 mmHg | "For people with diabetes and blood pressure >120/80 mmHg" | ada-2026 | p227 | p227/recommendation/10.5 | A |
| mra-consideration-medication-threshold | people-diabetes-htn | three antihypertensive classes including a diuretic | "not meeting blood pressure goals on three classes" | ada-2026 | p228 | p228/recommendation/10.13 | A |
| albuminuria-reduction-target | people-ckd-albuminuria300 | >=30% | "reduce urinary albumin by ≥30%" | ada-2026 | p255 | p255/recommendation/11.2 | B |
| albuminuria-eligibility-threshold | people-ckd-albuminuria300 | >=300 mg/g | "≥300 mg/g to slow CKD progression" | ada-2026 | p255 | p255/recommendation/11.2 | B |
| nondialysis-ckd-stage-threshold | people-ckd-g3plus | G3 or higher | "For people with CKD stage G3 or higher, protein intake should be 0.8 g/kg body weight per day" | ada-2026 | p256 | p256/recommendation/11.3 | A |
| nondialysis-protein-intake | people-ckd-g3plus | 0.8 g/kg/day | "For people with CKD stage G3 or higher, protein intake should be 0.8 g/kg body weight per day" | ada-2026 | p256 | p256/recommendation/11.3 | A |
| dialysis-protein-intake | people-dialysis | 1.0-1.2 g/kg/day | "protein intake of 1.0–1.2 g/kg/day" | ada-2026 | p256 | p256/recommendation/11.3 | B |
| nsmra-egfr-threshold | people-ckd-albuminuria | >=25 mL/min/1.73 m2 | "if eGFR is ≥25 mL/min/1.73 m2" | ada-2026 | p261 | p261/recommendation/11.8 | A |
| nsmra-potassium-follow-up | people-ckd-albuminuria | 1 month | "monitored 1 month after initiation" | ada-2026 | p261 | p261/recommendation/11.8 | A |
| sglt2-nsmra-uacr-threshold | adults-t2d-uacr100-egfr30-90 | >=100 mg/g | "UACR ≥100 mg/g with eGFR 30–90 mL/min/1.73 m2" | ada-2026 | p261 | p261/recommendation/11.9 | B |
| sglt2-nsmra-egfr-range | adults-t2d-uacr100-egfr30-90 | 30-90 mL/min/1.73 m2 | "UACR ≥100 mg/g with eGFR 30–90 mL/min/1.73 m2" | ada-2026 | p261 | p261/recommendation/11.9 | B |
| sglt2-continuation-egfr-threshold | people-egfr-under20-nondialysis | <20 mL/min/1.73 m2 | "Individuals with eGFR <20 mL/min/1.73 m2 and not on dialysis" | ada-2026 | p262 | p262/recommendation/11.11 | B/C |
| cognitive-screening-age-threshold | adults-diabetes-age65plus | >=65 years | "adults 65 years of age or older at the initial visit, annually, and as appropriate" | ada-2026 | p284 | p284/recommendation/13.3 | B |
| cognitive-screening-interval | adults-diabetes-age65plus | annually | "adults 65 years of age or older at the initial visit, annually, and as appropriate" | ada-2026 | p284 | p284/recommendation/13.3 | B |
| caregiver-dsmes-age-threshold | pediatric-diabetes | <18 years | "for individuals aged <18 years" | ada-2026 | p304 | p304/recommendation/14.1 | B |
| pregnancy-aspirin-dose | pregnancy-t1d-t2d | 100-150 mg/day | "low-dose aspirin 100–150 mg/day" | ada-2026 | p336 | p336/recommendation/15.23 | E |
| pregnancy-aspirin-start | pregnancy-t1d-t2d | 12-16 weeks gestation | "12–16 weeks of gestation" | ada-2026 | p336 | p336/recommendation/15.23 | E |
| pregnancy-aspirin-alternative-dose | pregnancy-t1d-t2d | 162 mg/day | "A dosage of 162 mg/day may be acceptable" | ada-2026 | p336 | p336/recommendation/15.23 | E |

## Conflicts

No duplicate `(quantity, population)` pair carries different values in this sheet.


## Coverage

Every distinct recommendation identifier in the bound extraction that is not cited
by a row above, with why. The 126 extracted records carry 116 distinct identifiers;
25 rows cite 14 of them and the 102 identifiers below account for the rest. Because
the source is `bound`, an identifier absent from both places warns rather than
refuses.

- `p12/recommendation/1.1` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.5` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.8` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.9` - change-summary entry, not a recommendation statement
- `p12/recommendation/2.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.18` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.19` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.20` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.21` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.22` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.24` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.31` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.9` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.1` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.2` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.3` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.4` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.6` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.9` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.13` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.26` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.27` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.3` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.5` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.12` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.23` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.4` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.5` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.32` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.34` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.40` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.45` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.46` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.47` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.56` - change-summary entry, not a recommendation statement
- `p14/recommendation/6.17` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.15` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.17` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.25` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.3` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.6` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.7` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.8` - change-summary entry, not a recommendation statement
- `p14/recommendation/8.2` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.10` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.4` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.6` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.14` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.15` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.20` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.21` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.29` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.5` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.8` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.11` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.12` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.13` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.24` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.25` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.27` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.33` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.36` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.37` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.38` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.9` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.11` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.32` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.40` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.44` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.1` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.10` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.11` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.5` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.6` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.8` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.9` - change-summary entry, not a recommendation statement
- `p16/recommendation/12.22` - change-summary entry, not a recommendation statement
- `p16/recommendation/13.9` - change-summary entry, not a recommendation statement
- `p166/recommendation/7.27` - no numeric decision point in the recommendation
- `p166/recommendation/7.28` - no numeric decision point in the recommendation
- `p17/recommendation/13.11` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.1` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.2` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.3` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.24` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.25` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.3` - change-summary entry, not a recommendation statement
- `p18/recommendation/16.14` - change-summary entry, not a recommendation statement
- `p256/recommendation/11.4` - no numeric decision point in the recommendation
- `p262/recommendation/11.10` - no numeric decision point in the recommendation
- `p287/recommendation/13.3` - narrative cross-reference, not a recommendation statement
- `p331/recommendation/2.32` - narrative cross-reference, not a recommendation statement
- `p346/recommendation/16.3` - no numeric decision point in the recommendation
- `p348/recommendation/16.7` - no numeric decision point in the recommendation
- `p349/recommendation/16.11` - no numeric decision point in the recommendation
- `p355/recommendation/16.18` - no numeric decision point in the recommendation
- `p36/recommendation/2.5` - no numeric decision point in the recommendation
- `p70/recommendation/4.5` - no numeric decision point in the recommendation
- `p78/recommendation/4.14` - no numeric decision point in the recommendation
- `p79/recommendation/4.17` - no numeric decision point in the recommendation
