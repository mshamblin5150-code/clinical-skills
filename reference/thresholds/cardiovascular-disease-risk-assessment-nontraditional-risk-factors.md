# Cardiovascular disease risk assessment, nontraditional risk factors — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/cvd-nontraditional-risk-factors-final-rec-statement | recommendation-statement | 2018 | 2018 | https://doi.org/10.1001/jama.2018.8359 | stated | exact |

## Scope

**Read:** pages 1-8, including the recommendation, clinical considerations, supporting evidence, recommendations of others, and article information; the reference list was retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendation through supporting-evidence text | 1-7 | yes |
| article information | 8 | read 2026-08-30; blind 2026-08-30 |
| references | 8-9 | exempt: citation list has no clinical prose |

**Second read:** blind source-only corroboration completed 2026-08-30 for the dated null span.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults | asymptomatic adults without a history of CVD |

## Quantities

| key | verbatim |
| --- | --- |
| framingham-risk-band | 10-year CVD event risk using the Framingham Risk Score |
| pooled-cohort-risk-band | 10-year CVD event risk using the Pooled Cohort Equations |
| abi-peripheral-artery-disease-cutoff | ankle-brachial index indicating peripheral artery disease |
| hscrp-increased-risk-cutoff | high-sensitivity C-reactive protein level indicating increased cardiovascular risk |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| framingham-risk-band | asymptomatic-adults | <10% low; 10% to 20% intermediate; >20% high | Persons with a 10-year CVD event risk greater than 20% are generally considered at high risk, those with a 10-year risk less than 10% are considered at low risk, and those in the 10% to 20% range are considered at intermediate risk. | uspstf-2018 | p4 | p4/narrative/framingham-risk-band | narrative |
| pooled-cohort-risk-band | asymptomatic-adults | <7.5% low; >=7.5% high | Persons with a 10-year CVD event risk less than 7.5% are considered at low risk, and those with a 10-year risk of 7.5% or greater are considered at high risk. | uspstf-2018 | p4 | p4/narrative/pooled-cohort-risk-band | narrative |
| abi-peripheral-artery-disease-cutoff | asymptomatic-adults | <0.9 indicates peripheral artery disease | A value <0.9 indicates peripheral artery disease. | uspstf-2018 | p4 | p4/narrative/abi-threshold | narrative |
| hscrp-increased-risk-cutoff | asymptomatic-adults | >2 or 3 mg/L indicates increased cardiovascular risk | A threshold of >2 or 3 mg/L indicates increased cardiovascular risk. | uspstf-2018 | p4 | p4/narrative/hscrp-threshold | narrative |

## Conflicts

## Coverage

- `p1/risk-assessment-for-cardiovascular-disease-with/1` - scoped out: the recommendation states no numeric dose, period, cutoff, or target; the numeric risk-assessment definitions are cited from narrative above.
