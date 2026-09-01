# Cardiovascular disease risk screening, electrocardiography — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/cvd-screening-with-ecg-final-rec-statement | recommendation-statement | 2018 | 2018 | https://doi.org/10.1001/jama.2018.6848 | stated | exact |

## Scope

**Read:** pages 1-6, including the recommendations, rationale, clinical considerations, supporting evidence, recommendations of others, and article information; the reference list was retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendation through supporting-evidence text | 1-6 | yes |
| references | 7 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults | adults without symptoms or a diagnosis of cardiovascular disease |

## Quantities

| key | verbatim |
| --- | --- |
| framingham-risk-band | 10-year CVD event risk using the Framingham Risk Score |
| pooled-cohort-risk-band | 10-year CVD event risk using the Pooled Cohort Equations |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| framingham-risk-band | asymptomatic-adults | <10% low; 10% to 20% intermediate; >20% high | RENDERED: "Persons with a 10-year CVD event risk greater than 20% are generally considered high risk, those with a 10-year CVD event risk less than 10% are considered low risk, and those with a 10-year CVD event risk of 10% to 20% are considered intermediate risk." | uspstf-2018 | p4 | p4/narrative/framingham-risk-band | narrative |
| pooled-cohort-risk-band | asymptomatic-adults | <7.5% low; >=7.5% elevated | RENDERED: "Persons with a 10-year CVD event risk less than 7.5% are considered at low risk, and those with a 10-year CVD event risk of 7.5% or greater are considered at elevated risk." | uspstf-2018 | p4 | p4/narrative/pooled-cohort-risk-band | narrative |

## Conflicts

## Coverage

- `p1/screening-for-cardiovascular-disease-risk-with-e/1` - scoped out: the recommendation states no numeric dose, period, cutoff, or target; the numeric low-risk definition is cited from narrative above.
- `p1/screening-for-cardiovascular-disease-risk-with-e/2` - scoped out: the recommendation states no numeric dose, period, cutoff, or target; the numeric intermediate- and high-risk definitions are cited from narrative above.
