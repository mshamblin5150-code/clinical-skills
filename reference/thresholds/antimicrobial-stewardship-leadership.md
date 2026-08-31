# Antimicrobial stewardship leadership — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guidance** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shea-idsa-pids-sidp-2026 | IDSA | IDSA/guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america | guideline | 2026 guidance update | 2026 | https://doi.org/10.1017/ash.2026.10344 | stated |  |

## Scope

**Read:** the complete 13-page guidance, page by page, including the title material,
abstract, introduction, purpose and skill-level framework, all of Tables 1-3 and their
notes, the narrative on key partnerships and barriers, conclusion, supplementary-
material notice, acknowledgments, disclosures, review statement, and references. No
figure appears in the source PDF. The separate supplementary gap-assessment file was
not part of this source PDF. The recommendation artifact declares `nothing-found` and
holds no recommendation identifiers; that extractor result is not treated as proof
that the rest of the document contains no decision point, so the full-page and table
read accounts for the source itself.

**Not read:** nothing in the source page range. The separately hosted supplementary
gap-assessment file is outside the cataloged source document and this sheet makes no
claim about its contents.

**Scoped out under ADR 0009's numeric patient-action rule:** publication and access
dates, author affiliations, tables and reference numbers, journal volumes and pages,
the basic/intermediate/advanced competency labels, examples that name no numeric
cutoff or interval, and study and administrative figures were read but do not change a
numeric patient action. The annual antibiogram, initial focus on up to two guidelines,
annual staff education, annual formulary assessment, 1-year and 3-5-year strategic-goal
horizons, annual goal review, quarterly microbiology-leadership meeting, monthly
antibiotic-use report, and annual institutional report are administrative or program
metrics rather than patient-action thresholds. The 30-day pneumonia readmission window
is likewise an outcome measure for aligning program goals rather than a patient-action
threshold. Qualitative knowledge and skill statements without a numeric dose,
duration, target, cutoff, or follow-up interval are outside this sheet.

**Source: `shea-idsa-pids-sidp-2026`**

| span | pages | read |
| --- | --- | --- |
| title material, abstract, introduction, purpose, and skill-level framework | 1-2 | read 2026-08-31; blind 2026-08-31 |
| Table 1 clinical infectious-disease and microbiology competencies before the antibiogram interval | 3-5 | read 2026-08-31; blind 2026-08-31 |
| Table 1 concluding diagnostic competencies | 6 | read 2026-08-31; blind 2026-08-31 |
| Table 2 preauthorization intervention carrying the patient-action threshold | 7 | yes |
| remaining Table 2 antimicrobial-stewardship interventions | 8 | read 2026-08-31; blind 2026-08-31 |
| conclusion of Table 2 and all of Table 3: program building, leadership, measurement, analysis, public health, and advocacy | 9-11 | read 2026-08-31; blind 2026-08-31 |
| partnerships, implementation barriers, conclusion, and administrative material | 12 | read 2026-08-31; blind 2026-08-31 |
| disclosures, review statement, and references | 13 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asp-leaders | ASP leaders |

## Quantities

| key | verbatim |
| --- | --- |
| preauthorization-first-review-window | Implement preauthorization of select broad spectrum, new, or expensive antimicrobials within the first 24 hours of therapy |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| preauthorization-first-review-window | asp-leaders | implement preauthorization within the first 24 hours of therapy, or after a locally specified number of days based on staffing | Implement preauthorization of select broad spectrum, new, or expensive antimicrobials within the first 24 hours of therapy or after a specified number of days | shea-idsa-pids-sidp-2026 | p7 | p7/narrative/preauthorization-first-review-window | narrative |

## Conflicts

## Coverage

The recommendation artifact for this source declares `nothing-found` and contains no
recommendation identifiers to cite or scope out. That empty index does not establish
document completeness; the page and table spans under `## Scope` are the coverage
instrument. The administrative and program metrics named in `## Scope` were read and
expressly dispositioned there rather than silently omitted.
