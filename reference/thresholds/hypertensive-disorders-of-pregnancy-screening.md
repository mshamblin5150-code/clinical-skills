# Hypertensive disorders of pregnancy screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2023 | USPSTF | USPSTF/hypertensive-disorders-pregnancy-final-recommendation | recommendation-statement | 2023 | 2023 | https://doi.org/10.1001/jama.2023.16991 | stated | exact |

## Scope

**Read:** the complete recommendation statement, including the recommendation,
condition definitions, risk assessment, screening tests and interval, treatment,
implementation, supporting evidence, response, research needs, and recommendations
of others on pp. 1-7. The reference list on pp. 8-9 is retired by class because it
contains citations rather than clinical prose.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's numeric decision-point rule:** the complete read also
found qualitative positions to screen with blood pressure throughout pregnancy; repeat
an elevated reading; perform further diagnostic evaluation and clinical monitoring
after multiple elevated readings; avoid routine point-of-care urine screening; obtain
blood pressure at each prenatal visit; counsel about preeclampsia at discharge; and
obtain subsequent postpartum blood pressure checks. The recommendations-of-others
section likewise states qualitative baseline-testing, Canadian measurement-method,
and testing-at-each-antenatal-visit positions. All were read, but none states a number
that changes patient action, so none produces a threshold row. `## Coverage` separately
accounts for the source's exact recommendation record; it does not enumerate document
prose outside that index.

| span | pages | read |
| --- | --- | --- |
| complete recommendation-statement narrative | 1-7 | yes |
| references | 8-9 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| pregnant-without-known-hdp-or-chronic-htn | pregnant persons without a known diagnosis of a hypertensive disorder of pregnancy or chronic hypertension |
| pregnant-new-onset-hypertension | pregnant persons with new-onset hypertension during pregnancy |
| high-risk-preeclampsia | persons at high risk for preeclampsia |
| black-pregnant-additional-moderate-risk | pregnant Black individuals with at least 1 additional moderate risk factor |
| pregnant-age-35-or-older | the pregnant individual being 35 years or older |
| diagnosed-hdp-postpartum | women with a diagnosed hypertensive disorder of pregnancy |
| severe-hypertension-postpartum | women with severe hypertension |

## Quantities

| key | verbatim |
| --- | --- |
| chronic-hypertension-timing | timing used to define chronic hypertension |
| preeclampsia-onset | gestational timing used to define preeclampsia |
| severe-feature-blood-pressure | blood pressure indicating preeclampsia with severe features |
| gestational-hypertension-onset | gestational timing used to define gestational hypertension |
| positive-screen-blood-pressure | positive screening result for new-onset hypertension during pregnancy |
| aspirin-prevention | low-dose aspirin preventive medication |
| maternal-age-risk | age associated with increased risk of preeclampsia and gestational hypertension |
| acog-postpartum-evaluation | ACOG postpartum blood pressure evaluation interval |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chronic-hypertension-timing | pregnant-without-known-hdp-or-chronic-htn | before pregnancy or within first 20 weeks of gestation | diagnosed before pregnancy or within the first 20 weeks of gestation | uspstf-2023 | p3 | p3/narrative/chronic-hypertension-timing | narrative |
| preeclampsia-onset | pregnant-without-known-hdp-or-chronic-htn | new-onset hypertension most often after week 20 | after the 20th week of gestation | uspstf-2023 | p3 | p3/narrative/preeclampsia-onset | narrative |
| severe-feature-blood-pressure | pregnant-without-known-hdp-or-chronic-htn | SBP >=160 mm Hg or DBP >=110 mm Hg | systolic blood pressure ≥160 mm Hg or diastolic blood pressure ≥110 mm Hg | uspstf-2023 | p3 | p3/narrative/severe-feature-blood-pressure | narrative |
| gestational-hypertension-onset | pregnant-without-known-hdp-or-chronic-htn | new-onset hypertension after week 20 | after the 20th week of gestation | uspstf-2023 | p3 | p3/narrative/gestational-hypertension-onset | narrative |
| maternal-age-risk | pregnant-age-35-or-older | age >=35 years: increased risk factor | the pregnant individual being 35 years or older | uspstf-2023 | p4 | p4/narrative/maternal-age-risk | narrative |
| positive-screen-blood-pressure | pregnant-new-onset-hypertension | SBP >=140 mm Hg or DBP >=90 mm Hg twice at least 4 hours apart | systolic blood pressure ≥140 mm Hg or diastolic blood pressure ≥90 mm Hg in the absence of chronic hyperten- sion) measured twice at least 4 hours apart | uspstf-2023 | p4 | p4/narrative/positive-screen-blood-pressure | narrative |
| aspirin-prevention | high-risk-preeclampsia | 81 mg/day after 12 weeks gestation | low-dose aspirin (81 mg/d) as preventive medication after 12 weeks of gestation | uspstf-2023 | p5 | p5/narrative/aspirin-high-risk | narrative |
| aspirin-prevention | black-pregnant-additional-moderate-risk | recommend aspirin when at least 1 additional moderate risk factor | aspirin use recommended for those with at least 1 additional moderate risk factor | uspstf-2023 | p4 | p4/narrative/aspirin-black-additional-risk | narrative |
| acog-postpartum-evaluation | diagnosed-hdp-postpartum | no later than 7 to 10 days postpartum | no later than 7 to 10 days postpartum | uspstf-2023 | p7 | p7/narrative/acog-postpartum-evaluation | narrative |
| acog-postpartum-evaluation | severe-hypertension-postpartum | within 72 hours | women with severe hypertension should be seen within 72 hours | uspstf-2023 | p7 | p7/narrative/acog-severe-postpartum-evaluation | narrative |

## Conflicts

CONFLICT: acog-postpartum-evaluation — no later than 7 to 10 days postpartum applies
to a diagnosed hypertensive disorder of pregnancy; within 72 hours applies to severe
hypertension.

CONFLICT: aspirin-prevention — 81 mg/day after 12 weeks states the dose and timing for
high-risk patients; the at-least-1-additional-moderate-risk row states the eligibility
rule specifically attributed to pregnant Black patients.

## Coverage

- `p1/screening-for-hypertensive-disorders-of-pregnanc/1` - qualitative screening
  recommendation; it states blood pressure measurement throughout pregnancy but no
  numeric dose, period, cutoff, or target
