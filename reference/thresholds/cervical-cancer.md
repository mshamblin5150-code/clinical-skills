# Cervical cancer screening — threshold sheet

<!-- schema: threshold-sheet/1 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

Every `snippet` cell is the shortest verbatim USPSTF fragment that carries the
decision point. Method-dependent intervals name the method in the quantity key, as
ruled in [ADR 0009](../../docs/adr/0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md).

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/cervical-cancer-final-rec-statement | 2018 | 2018 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/cervical-cancer-screening | exact |

## Scope

**Read:** all five recommendation statements in the USPSTF recommendation table.

**Not read:** the rationale, clinical considerations, evidence review, and references.

citations resolved against C:/codeing/guidelines-src on 2026-08-22

## Populations

| key | verbatim |
| --- | --- |
| women-21-29 | women aged 21 to 29 years |
| women-30-65 | women aged 30 to 65 years |
| women-over65-adequately-screened-average-risk | women older than 65 years who have had adequate prior screening and are not otherwise at high risk for cervical cancer |
| women-under21 | women younger than 21 years |

## Quantities

| key | verbatim |
| --- | --- |
| screening-interval-cervical-cytology-alone | every 3 years with cervical cytology alone |
| screening-interval-hrhpv-alone | every 5 years with hrHPV testing alone |
| screening-interval-hrhpv-cytology-cotesting | every 5 years with hrHPV testing in combination with cytology (cotesting) |
| screening-upper-age-cutoff | women older than 65 years |
| screening-lower-age-cutoff | women younger than 21 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| screening-interval-cervical-cytology-alone | women-21-29 | every 3 years | "every 3 years with cervical cytology alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/1 | A |
| screening-interval-cervical-cytology-alone | women-30-65 | every 3 years | "every 3 years with cervical cytology alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| screening-interval-hrhpv-alone | women-30-65 | every 5 years | "every 5 years with hrHPV testing alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| screening-interval-hrhpv-cytology-cotesting | women-30-65 | every 5 years | "every 5 years with hrHPV testing in combination with cytology (cotesting)" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| screening-upper-age-cutoff | women-over65-adequately-screened-average-risk | >65 years | "women older than 65 years" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/3 | D |
| screening-lower-age-cutoff | women-under21 | <21 years | "women younger than 21 years" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/5 | D |

## Conflicts

None. The different screening intervals are method-dependent alternatives, and the
method is part of each quantity key.

## Coverage

- `p1/screening-for-cervical-cancer/4` - no numeric decision point
