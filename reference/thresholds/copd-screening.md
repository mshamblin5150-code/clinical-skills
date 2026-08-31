# COPD screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2022 | USPSTF | USPSTF/copd-screening-final-recommendation | recommendation-statement | 2022 | 2022 | https://doi.org/10.1001/jama.2022.5692 | stated | exact |

## Scope

**Read:** all 6 pages, including the recommendation, practice considerations, supporting evidence, recommendations of others, article information, and references.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| complete recommendation statement, including interleaved references | 1-6 | yes |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| symptomatic-or-exposed-persons | persons with appropriate symptoms and significant exposures to noxious stimuli |

## Quantities

| key | verbatim |
| --- | --- |
| postbronchodilator-fev1-fvc-ratio | postbronchodilator spirometry ratio of forced expiratory volume in 1 second to forced vital capacity (FEV1/FVC) |
| postbronchodilator-fev1-percent-predicted-severity | Airflow obstruction is classified by the postbronchodilator FEV1% predicted |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| postbronchodilator-fev1-fvc-ratio | symptomatic-or-exposed-persons | <0.70: confirms persistent airway obstruction and COPD diagnosis | RENDERED: A postbronchodilator spirometry ratio of forced expiratory volume in 1 second to forced vital capacity (FEV1/FVC) of less than 0.70 confirms the presence of persistent airway obstruction and a diagnosis of COPD | uspstf-2022 | p2 | p2/narrative/postbronchodilator-fev1-fvc-ratio | narrative |
| postbronchodilator-fev1-percent-predicted-severity | symptomatic-or-exposed-persons | >=80% predicted: mild | RENDERED: 80% or more is mild | uspstf-2022 | p2 | p2/narrative/fev1-mild | narrative |
| postbronchodilator-fev1-percent-predicted-severity | symptomatic-or-exposed-persons | 50% to 79% predicted: moderate | RENDERED: 50% to 79% is moderate | uspstf-2022 | p2 | p2/narrative/fev1-moderate | narrative |
| postbronchodilator-fev1-percent-predicted-severity | symptomatic-or-exposed-persons | 30% to 49% predicted: severe | RENDERED: 30% to 49% is severe | uspstf-2022 | p2 | p2/narrative/fev1-severe | narrative |
| postbronchodilator-fev1-percent-predicted-severity | symptomatic-or-exposed-persons | <30% predicted: very severe | RENDERED: less than 30% is very severe | uspstf-2022 | p2 | p2/narrative/fev1-very-severe | narrative |

## Conflicts

CONFLICT: postbronchodilator-fev1-percent-predicted-severity — `>=80% predicted: mild`, `50% to 79% predicted: moderate`, `30% to 49% predicted: severe`, and `<30% predicted: very severe` are mutually exclusive airflow-obstruction severity bands, not competing thresholds.

## Coverage

- `p1/screening-for-chronic-obstructive-pulmonary-dise/1` - the recommendation against screening asymptomatic adults contains no numeric patient-action decision point; the source's numeric diagnostic and staging cutoffs are recorded from its practice considerations.
