# Cervical cancer screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

Every `snippet` cell is the shortest verbatim USPSTF fragment that carries the
decision point. Method-dependent intervals name the method in the quantity key, as
ruled in [ADR 0009](../../docs/adr/0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/cervical-cancer-final-rec-statement | recommendation-statement | 2018 | 2018 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/cervical-cancer-screening | chosen | exact |

## Scope

**Read:** all five recommendation statements in the USPSTF recommendation table. The
rationale, clinical considerations, and evidence review on pp. 1-11 were read on
2026-08-29. The reference list is retired by class because it is a citation list with
no clinical prose.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| recommendation statements | 1 | yes |
| rationale and clinical considerations | 1-11 | yes |
| references | 11-13 | exempt: citation list has no clinical prose |

**Second read:** a blind independent read dated 2026-08-29 corroborated the
adequate-prior-screening definition, the CIN grade boundary, and the continued-screening
duration, and identified the two over-65 screening branches now recorded below. Its
remaining candidates were recommendation-statement repeats, evidence or model results,
or recommendations the article attributes to other organizations; none was promoted
into a USPSTF decision-point row.

citations resolved against C:/codeing/guidelines-src on 2026-08-29
extraction identity: producer 0cd92f02fc7445ea306901b5427c0912f3960a62; tools/guidelines_extract.py sha256 f8e95baf7e4e74328a752d89e1e7b617217ba1e43c4368fba92f789840e21cf9

## Populations

| key | verbatim |
| --- | --- |
| women-21-29 | women aged 21 to 29 years |
| women-30-65 | women aged 30 to 65 years |
| women-over65-adequately-screened-average-risk | women older than 65 years who have had adequate prior screening and are not otherwise at high risk for cervical cancer |
| women-over65-inadequate-unknown-screening-history | older women with an inadequate or unknown screening history |
| women-over65-otherwise-high-risk | women older than 65 years who are otherwise at high risk |
| women-post-hysterectomy-cervix-removed | women who have had a hysterectomy with removal of the cervix |
| women-after-precancerous-lesion-regression-management | after spontaneous regression or appropriate management of a precancerous lesion |
| women-under21 | women younger than 21 years |

## Quantities

| key | verbatim |
| --- | --- |
| screening-interval-cervical-cytology-alone | every 3 years with cervical cytology alone |
| screening-interval-hrhpv-alone | every 5 years with hrHPV testing alone |
| screening-interval-hrhpv-cytology-cotesting | every 5 years with hrHPV testing in combination with cytology (cotesting) |
| high-grade-precancerous-lesion-cin-grade | cervical intraepithelial neoplasia [CIN] grade 2 or 3 |
| adequate-prior-screening-negative-cytology-count | 3 consecutive negative cytology results |
| adequate-prior-screening-negative-cotesting-count | 2 consecutive negative cotesting results |
| adequate-prior-screening-negative-hpv-count | 2 consecutive negative HPV results |
| adequate-prior-screening-lookback-window | within 10 years before stopping screening |
| adequate-prior-screening-most-recent-test-window | the most recent test occurring within 5 years |
| continued-screening-after-precancer | routine screening should continue for at least 20 years after spontaneous regression or appropriate management of a precancerous lesion |
| screening-upper-age-cutoff | women older than 65 years |
| screening-lower-age-cutoff | women younger than 21 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| screening-interval-cervical-cytology-alone | women-21-29 | every 3 years | "every 3 years with cervical cytology alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/1 | A |
| screening-interval-cervical-cytology-alone | women-30-65 | every 3 years | "every 3 years with cervical cytology alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| screening-interval-hrhpv-alone | women-30-65 | every 5 years | "every 5 years with hrHPV testing alone" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| screening-interval-hrhpv-cytology-cotesting | women-30-65 | every 5 years | "every 5 years with hrHPV testing in combination with cytology (cotesting)" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/2 | A |
| high-grade-precancerous-lesion-cin-grade | women-post-hysterectomy-cervix-removed | CIN grade 2 or 3 | "cervical intraepithelial neoplasia [CIN] grade 2 or 3" | uspstf-2018 | p2 | p2/narrative/1 | narrative |
| adequate-prior-screening-negative-cytology-count | women-over65-adequately-screened-average-risk | 3 consecutive negative cytology results | "3 consecutive negative cytology results" | uspstf-2018 | p4 | p4/narrative/1a | narrative |
| adequate-prior-screening-negative-cotesting-count | women-over65-adequately-screened-average-risk | 2 consecutive negative cotesting results | "2 consecutive negative cotesting results" | uspstf-2018 | p4 | p4/narrative/1b | narrative |
| adequate-prior-screening-lookback-window | women-over65-adequately-screened-average-risk | within 10 years | "within 10 years before stopping screening" | uspstf-2018 | p4 | p4/narrative/1c | narrative |
| adequate-prior-screening-most-recent-test-window | women-over65-adequately-screened-average-risk | within 5 years | "the most recent test occurring within 5 years" | uspstf-2018 | p4 | p4/narrative/1d | narrative |
| continued-screening-after-precancer | women-after-precancerous-lesion-regression-management | at least 20 years | "routine screening should continue for at least 20 years after spontaneous regression or appropriate management of a precancerous lesion" | uspstf-2018 | p4 | p4/narrative/2 | narrative |
| adequate-prior-screening-negative-hpv-count | women-over65-adequately-screened-average-risk | 2 consecutive negative HPV results | "2 consecutive negative HPV results within 10 years before stopping screening, with the most recent test performed within 5 years" | uspstf-2018 | p9 | p9/narrative/1 | narrative |
| screening-upper-age-cutoff | women-over65-adequately-screened-average-risk | >65 years | "women older than 65 years" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/3 | D |
| screening-upper-age-cutoff | women-over65-inadequate-unknown-screening-history | >65 years | "Women Older Than 65 Years Who Have Not Been Adequately Screened Screening may be clinically indicated in older women with an inadequate or unknown screening history" | uspstf-2018 | p4 | p4/narrative/3 | narrative |
| screening-upper-age-cutoff | women-over65-otherwise-high-risk | >65 years | "women older than 65 years" | uspstf-2018 | p4 | p4/narrative/4 | narrative |
| screening-lower-age-cutoff | women-under21 | <21 years | "women younger than 21 years" | uspstf-2018 | p1 | p1/screening-for-cervical-cancer/5 | D |

## Conflicts

The different screening intervals and adequate-prior-screening test counts are
method-dependent alternatives, and the method is part of each quantity key. The
Clinical Considerations passage on p. 4 states 2 consecutive negative cotesting
results; the Discussion passage on p. 9 instead states 2 consecutive negative HPV
results. The sheet preserves both source wordings rather than treating a negative HPV
result and a negative cotest as interchangeable.

## Coverage

- `p1/screening-for-cervical-cancer/4` - no numeric decision point
