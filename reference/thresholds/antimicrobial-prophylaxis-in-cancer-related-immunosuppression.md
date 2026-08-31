# Antimicrobial Prophylaxis in Cancer-Related Immunosuppression — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete guideline summary below. **Not a
substitute for the guideline** and not a clinical instruction: every row is a fact
this repo restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| asco-idsa-2018 | IDSA | IDSA/taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa | guideline | 2018 guideline update summary | 2018-09-04 | https://doi.org/10.1200/JOP.18.00366 | stated | bound |

## Scope

**Read:** the complete 5-page guideline update summary, page by page, including the
clinical background and rationale; target population and audience; methods; all ten
bound recommendation-record occurrences; qualifying statements; additional resources;
guideline limitations; acknowledgments; author contributions; references; and author
disclosures. Page 2 was also read from the rendered page because its comparison
operators are encoded through a symbol font and are not preserved correctly in the
extracted text. The bound record is a marker inventory rather than proof that every
recommendation was extracted, so `## Coverage` accounts for all ten entries while the
full-page read accounts for the source itself.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's numeric decision-point rule:** publication dates,
study and reference numbers, complication and mortality rates, descriptive risk
statistics, evidence grades, and qualitative recommendations without a numeric dose,
duration, target, cutoff, or follow-up interval were read but do not change a numeric
patient-action point in this summary.

**Source: `asco-idsa-2018`**

| span | pages | read |
| --- | --- | --- |
| clinical background, infection-risk rationale, and prior-guideline context | 1 | read 2026-08-31; blind 2026-08-31 |
| target population, methods, and all key recommendations | 2-3 | yes |
| limitations, acknowledgments, contributions, and references | 4 | read 2026-08-31; blind 2026-08-31 |
| author conflict-of-interest disclosures | 5 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| chemotherapy-regimens-pjp-risk | patients receiving chemotherapy regimens associated with > 3.5% risk for pneumonia from Pneumocystis jirovecii |
| prednisone-pjp-risk-example | those with ≥ 20 mg prednisone equivalents daily for ≥ 1 month |
| chemotherapy-patients-contacts-and-providers | all patients receiving chemotherapy for malignancy, for all family and household contacts, and for health care providers |

## Quantities

| key | verbatim |
| --- | --- |
| pjp-prophylaxis-risk-threshold | chemotherapy regimens associated with > 3.5% risk for pneumonia from Pneumocystis jirovecii |
| pjp-prophylaxis-prednisone-example | ≥ 20 mg prednisone equivalents daily for ≥ 1 month |
| inactivated-influenza-vaccination-interval | Yearly influenza vaccination with inactivated vaccine |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pjp-prophylaxis-risk-threshold | chemotherapy-regimens-pjp-risk | risk >3.5%: provide prophylaxis such as TMP-SMX | RENDERED: chemotherapy regimens associated with > 3.5% risk for pneumonia from Pneumocystis jirovecii | asco-idsa-2018 | p2 | p2/recommendation/2.2 |  |
| pjp-prophylaxis-prednisone-example | prednisone-pjp-risk-example | prednisone equivalent >=20 mg daily for >=1 month: example regimen warranting prophylaxis | RENDERED: those with ≥ 20 mg prednisone equivalents daily for ≥ 1 month | asco-idsa-2018 | p2 | p2/recommendation/2.2 |  |
| inactivated-influenza-vaccination-interval | chemotherapy-patients-contacts-and-providers | yearly | Yearly influenza vaccination with inactivated vaccine is recommended | asco-idsa-2018 | p3 | p3/recommendation/3.3 |  |

## Conflicts

## Coverage

- `p2/recommendation/1.1` - scoped out: qualitative systematic risk-assessment recommendation states no numeric patient-action point.
- `p2/recommendation/1.2` - scoped out: qualitative fluoroquinolone-prophylaxis recommendation does not quantify high risk or profound, protracted neutropenia in this summary.
- `p2/recommendation/2.1` - scoped out: qualitative antifungal-prophylaxis recommendation does not quantify profound, protracted neutropenia in this summary.
- `p3/recommendation/3.1` - scoped out: qualitative HSV prophylaxis recommendation states no numeric dose, duration, target, cutoff, or interval.
- `p3/recommendation/3.2` - scoped out: qualitative hepatitis B reactivation prophylaxis recommendation states no numeric patient-action point.
- `p3/recommendation/3.4` - scoped out: referral to a separate immunosuppressed-host vaccination guideline states no numeric patient-action point in this source.
- `p3/recommendation/4.1` - scoped out: qualitative hand-hygiene and respiratory-hygiene recommendation states no numeric patient-action point.
- `p3/recommendation/4.2` - scoped out: qualitative environmental-exposure avoidance recommendation does not quantify prolonged contact or airborne fungal-spore concentration.
