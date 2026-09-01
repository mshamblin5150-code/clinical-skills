# Cardiovascular disease prevention, diet and physical activity counseling — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2022 | USPSTF | USPSTF/behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs | recommendation-statement | 2022 | 2022 | https://doi.org/10.1001/jama.2022.10951 | stated | exact |
| uspstf-2020 | USPSTF | USPSTF/healthy-diet-phys-activity-high-risk-final-rec | recommendation-statement | 2020 | 2020 | https://doi.org/10.1001/jama.2020.21749 | stated | exact |

## Scope

**Read:** both complete recommendation statements. For the 2022 source this includes
the recommendation and rationale on pp. 1-2, practice considerations on pp. 2-4,
supporting evidence on pp. 5-6, and the response, research needs, and recommendations
of others on p. 6. For the 2020 source this includes the recommendation and practice
considerations on pp. 1-3, supporting evidence on pp. 4-5, and the response, research
needs, and recommendations of others on pp. 5-6. The reference lists are retired by
class because they contain citations rather than clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and rationale | 1-2 | yes |
| practice considerations and implementation | 2-4 | yes |
| supporting evidence | 5-6 | read 2026-08-30; blind 2026-08-30 |
| response, research needs, and recommendations of others | 6 | read 2026-08-30; blind 2026-08-30 |
| article information | 7 | read 2026-08-30; blind 2026-08-30 |
| references | 7-8 | read 2026-08-30; blind 2026-08-30 |

**Source: `uspstf-2020`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and practice considerations | 1-3 | yes |
| practice descriptors and supporting evidence | 4 | yes |
| supporting evidence, response, and research needs | 5-6 | read 2026-08-30; blind 2026-08-30 |
| recommendations of others and article information | 6 | read 2026-08-30; blind 2026-08-30 |
| references | 6-7 | read 2026-08-30; blind 2026-08-30 |

**Second read:** a blind independent read dated 2026-08-30 corroborated that the
marked null spans contain no additional current USPSTF decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-no-known-cvd-risk-factors | adults 18 years or older without known CVD risk factors |
| adults-with-cvd-risk-factors | adults 18 years or older with known hypertension or elevated blood pressure, dyslipidemia, or mixed or multiple risk factors |
| adults-18-or-older | adults 18 years or older |

## Quantities

| key | verbatim |
| --- | --- |
| counseling-offer | offer or refer adults to behavioral counseling interventions to promote a healthy diet and physical activity |
| cvd-risk-boundary | estimated 10-year CVD risk of 7.5% or greater |
| physical-activity-guideline-moderate | moderate-intensity aerobic physical activity |
| physical-activity-guideline-vigorous | vigorous-intensity aerobic physical activity |
| physical-activity-guideline-strengthening | strengthening activities |
| physical-activity-counseling-goal | gradually increase aerobic activity |
| counseling-interaction-time | interaction time with a clinician |
| counseling-contacts | contacts and contact time over the intervention period |
| counseling-contact-time | total contact time over the intervention period |
| counseling-intervention-duration | intervention period |
| cvd-risk-factor-count | number of listed CVD risk factors |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| counseling-offer | adults-no-known-cvd-risk-factors | individualize the decision to offer or refer | The USPSTF recommends that clinicians individualize the decision to offer or refer adults without CVD risk factors to behavioral counseling interventions to promote a healthy diet and physical activity. | uspstf-2022 | p1 | p1/behavioral-counseling-interventions-to-promote-a/1 | C |
| cvd-risk-boundary | adults-no-known-cvd-risk-factors | 10-year CVD risk <7.5% and no listed risk factor | mixed or multiple risk factors such as metabolic syndrome or an estimated 10-year CVD risk of 7.5% or greater. | uspstf-2022 | p1 | p1/narrative/cvd-risk-boundary | narrative |
| physical-activity-guideline-moderate | adults-18-or-older | >=150 minutes per week | at least 150 minutes | uspstf-2022 | p2 | p2/narrative/physical-activity-guideline-moderate | narrative |
| physical-activity-guideline-vigorous | adults-18-or-older | >=75 minutes per week | 75 minutes | uspstf-2022 | p2 | p2/narrative/physical-activity-guideline-vigorous | narrative |
| physical-activity-guideline-strengthening | adults-18-or-older | at least twice per week | strengthening activities at least twice per week | uspstf-2022 | p2 | p2/narrative/physical-activity-guideline-strengthening | narrative |
| physical-activity-counseling-goal | adults-no-known-cvd-risk-factors | gradually increase to >=150 minutes per week | at least 150 minutes | uspstf-2022 | p3 | p3/narrative/physical-activity-counseling-goal | narrative |
| counseling-interaction-time | adults-no-known-cvd-risk-factors | 30 minutes to 6 hours over >=6 months | Interaction time with a clinician may range from 30 minutes to 6 hours over 6 months or longer. | uspstf-2022 | p3 | p3/narrative/counseling-interaction-time | narrative |
| counseling-offer | adults-with-cvd-risk-factors | offer or refer | The USPSTF recommends offering or referring adults with CVD risk factors to behavioral counseling interventions to promote a healthy diet and physical activity. | uspstf-2020 | p1 | p1/behavioral-counseling-interventions-to-promote-a/1 | B |
| cvd-risk-factor-count | adults-with-cvd-risk-factors | >=1 listed risk factor | 1 or more of the following | uspstf-2020 | p2 | p2/narrative/cvd-risk-factor-count | narrative |
| cvd-risk-boundary | adults-with-cvd-risk-factors | 10-year CVD risk >=7.5% | estimated 10-year CVD risk of ≥7.5% | uspstf-2020 | p2 | p2/narrative/cvd-risk-boundary | narrative |
| physical-activity-counseling-goal | adults-with-cvd-risk-factors | 90 to 180 minutes per week of moderate to vigorous activity | Physical activity counseling typically advised 90 to 180 min/wk of moderate to vigorous activity. | uspstf-2020 | p4 | p4/narrative/physical-activity-counseling-goal | narrative |
| counseling-contacts | adults-with-cvd-risk-factors | median 12 contacts | median of 12 contacts | uspstf-2020 | p3 | p3/narrative/counseling-contacts | narrative |
| counseling-contact-time | adults-with-cvd-risk-factors | about 6 hours | estimated 6 hours | uspstf-2020 | p3 | p3/narrative/counseling-contact-time | narrative |
| counseling-intervention-duration | adults-with-cvd-risk-factors | 6 to 18 months | 6 to 18 months | uspstf-2020 | p3 | p3/narrative/counseling-intervention-duration | narrative |

## Conflicts

## Coverage
