# Clostridioides difficile infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the source** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-shea-2021 | IDSA/SHEA | IDSA/ciab549 | guideline | 2021 focused update | 2021 | https://doi.org/10.1093/cid/ciab549 | stated | bound |

## Scope

**Read:** all 16 pages, including every figure, table, disclosure, and reference page. The page spans below account for the entire document.

**Not read:** nothing. Two spans yielded no patient-action numeric decision point and carry completed first-read and blind markers. The reference page is exempt from decision-point extraction.

| span | pages | read |
| --- | --- | --- |
| title, abstract, executive summary, recommendations, and treatment table | 1-3 | yes |
| methods, evidence profiles, and fidaxomicin evidence figures | 4-6 | read 2026-08-31; blind 2026-08-31 |
| fidaxomicin regimens, recurrence options, and supporting evidence | 7-10 | read 2026-08-31; blind 2026-08-31 |
| bezlotoxumab recommendation, dose, rationale, and implementation considerations | 11-14 | yes |
| acknowledgments and disclosures | 15 | read 2026-08-31; blind 2026-08-31 |
| references | 16 | exempt: reference list; no first-read or blind marker required |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-initial-cdi | adult patients with an initial CDI episode |
| adults-nonsevere-initial-cdi | adult patients with an initial nonsevere CDI episode when fidaxomicin and vancomycin are unavailable |
| adults-first-cdi-recurrence | adult patients with a first CDI recurrence |
| adults-second-or-later-cdi-recurrence | adult patients with a second or subsequent CDI recurrence |
| adults-multiple-cdi-recurrences | adult patients with multiple CDI recurrences |
| adults-fulminant-cdi | adult patients with fulminant CDI |
| adults-recurrent-cdi-six-months | adult patients with a recurrent CDI episode within the last 6 months |
| adults-primary-cdi-recurrence-risk | adult patients with primary CDI and risk factors for recurrence |
| adults-cdi-bezlotoxumab | adult patients with CDI receiving bezlotoxumab with standard-of-care antibiotics |

## Quantities

| key | verbatim |
| --- | --- |
| initial-fidaxomicin-regimen | fidaxomicin regimen for an initial CDI episode |
| initial-vancomycin-regimen | vancomycin alternative regimen for an initial CDI episode |
| initial-metronidazole-regimen | metronidazole alternative regimen when preferred agents are unavailable |
| nonsevere-definition | laboratory definition of nonsevere CDI |
| recurrence-fidaxomicin-standard | standard fidaxomicin regimen for recurrence |
| recurrence-fidaxomicin-extended | extended-pulsed fidaxomicin regimen for recurrence |
| recurrence-vancomycin-taper | vancomycin tapered and pulsed regimen example |
| first-recurrence-vancomycin | standard vancomycin regimen for a first recurrence |
| recurrence-vancomycin-rifaximin | vancomycin followed by rifaximin for a second or subsequent recurrence |
| fmt-recurrence-floor | recurrence floor before fecal microbiota transplantation |
| fulminant-vancomycin | vancomycin regimen for fulminant CDI |
| fulminant-metronidazole | intravenous metronidazole regimen for fulminant CDI |
| bezlotoxumab-dose-infusion | bezlotoxumab dose and infusion duration |
| bezlotoxumab-recurrence-window | recurrence window for adding bezlotoxumab |
| bezlotoxumab-age-risk-threshold | age risk factor for considering bezlotoxumab in primary CDI |
| bezlotoxumab-risk-factor-count | risk-factor count supporting bezlotoxumab in primary CDI |
| bezlotoxumab-administration-window | timing of bezlotoxumab during standard-of-care antibiotics |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initial-fidaxomicin-regimen | adults-initial-cdi | fidaxomicin 200 mg by mouth twice daily for 10 days | RENDERED: "Fidaxomicin 200 mg given twice daily for 10 days" | idsa-shea-2021 | p3 | p3/narrative/initial-fidaxomicin-regimen | narrative |
| initial-vancomycin-regimen | adults-initial-cdi | vancomycin 125 mg by mouth four times daily for 10 days | RENDERED: "Vancomycin 125 mg given 4 times daily by mouth for 10 days" | idsa-shea-2021 | p3 | p3/narrative/initial-vancomycin-regimen | narrative |
| initial-metronidazole-regimen | adults-nonsevere-initial-cdi | metronidazole 500 mg by mouth three times daily for 10-14 days only if fidaxomicin and vancomycin are unavailable | RENDERED: "Metronidazole, 500 mg 3 times daily by mouth for 10-14 days" | idsa-shea-2021 | p3 | p3/narrative/initial-metronidazole-regimen | narrative |
| nonsevere-definition | adults-initial-cdi | white blood cell count <=15 000 cells/microliter and serum creatinine <1.5 mg/dL | RENDERED: "White blood cell count of 15 000 cells/µL or lower and a serum creatinine level <1.5 mg/dL" | idsa-shea-2021 | p3 | p3/narrative/nonsevere-definition | narrative |
| recurrence-fidaxomicin-standard | adults-first-cdi-recurrence | fidaxomicin 200 mg by mouth twice daily for 10 days | RENDERED: "Fidaxomicin 200 mg given twice daily for 10 days" | idsa-shea-2021 | p3 | p3/narrative/recurrence-fidaxomicin-standard | narrative |
| recurrence-fidaxomicin-extended | adults-first-cdi-recurrence | fidaxomicin 200 mg by mouth twice daily for 5 days, then once every other day for 20 days | RENDERED: "Fidaxomicin 200 mg given twice daily for 5 days followed by once every other day for 20 days" | idsa-shea-2021 | p3 | p3/narrative/recurrence-fidaxomicin-extended | narrative |
| recurrence-fidaxomicin-standard | adults-second-or-later-cdi-recurrence | fidaxomicin 200 mg by mouth twice daily for 10 days | RENDERED: "Fidaxomicin 200 mg given twice daily for 10 days" | idsa-shea-2021 | p3 | p3/narrative/multiple-recurrence-fidaxomicin-standard | narrative |
| recurrence-fidaxomicin-extended | adults-second-or-later-cdi-recurrence | fidaxomicin 200 mg by mouth twice daily for 5 days, then once every other day for 20 days | RENDERED: "Fidaxomicin 200 mg given twice daily for 5 days followed by once every other day for 20 days" | idsa-shea-2021 | p3 | p3/narrative/multiple-recurrence-fidaxomicin-extended | narrative |
| recurrence-vancomycin-taper | adults-first-cdi-recurrence | example: vancomycin 125 mg by mouth four times daily for 10-14 days, twice daily for 7 days, once daily for 7 days, then every 2 or 3 days for 2-8 weeks | RENDERED: "125 mg 4 times daily for 10-14 days, 2 times daily for 7 days, once daily for 7 days, and then every 2 or 3 days for 2-8 weeks" | idsa-shea-2021 | p3 | p3/narrative/recurrence-vancomycin-taper | narrative |
| first-recurrence-vancomycin | adults-first-cdi-recurrence | vancomycin 125 mg by mouth four times daily for 10 days; consider when metronidazole was used for the initial episode | RENDERED: "Vancomycin 125 mg given 4 times daily by mouth for 10 days" | idsa-shea-2021 | p3 | p3/narrative/first-recurrence-vancomycin | narrative |
| recurrence-vancomycin-rifaximin | adults-second-or-later-cdi-recurrence | vancomycin 125 mg by mouth four times daily for 10 days followed by rifaximin 400 mg three times daily for 20 days | RENDERED: "Vancomycin 125 mg 4 times daily by mouth for 10 days followed by rifaximin 400 mg 3 times daily for 20 days" | idsa-shea-2021 | p3 | p3/narrative/recurrence-vancomycin-rifaximin | narrative |
| fmt-recurrence-floor | adults-multiple-cdi-recurrences | use after appropriate antibiotic treatments for at least 2 recurrences, meaning 3 CDI episodes | RENDERED: "appropriate antibiotic treatments for at least 2 recurrences (ie, 3 CDI episodes)" | idsa-shea-2021 | p3 | p3/narrative/fmt-recurrence-floor | narrative |
| fulminant-vancomycin | adults-fulminant-cdi | vancomycin 500 mg by mouth or nasogastric tube four times daily; if ileus, consider rectal instillation | RENDERED: "Vancomycin 500 mg 4 times daily by mouth or by nasogastric tube. If ileus, consider adding rectal instillation of vancomycin." | idsa-shea-2021 | p3 | p3/narrative/fulminant-vancomycin | narrative |
| fulminant-metronidazole | adults-fulminant-cdi | metronidazole 500 mg intravenously every 8 hours together with oral or rectal vancomycin, particularly if ileus is present | RENDERED: "Intravenously administered metronidazole (500 mg every 8 hours) should be administered together with oral or rectal vancomycin, particularly if ileus is present." | idsa-shea-2021 | p3 | p3/narrative/fulminant-metronidazole | narrative |
| bezlotoxumab-dose-infusion | adults-cdi-bezlotoxumab | bezlotoxumab 10 mg/kg intravenously once over 60 minutes during standard-of-care antibiotics | "Bezlotoxumab is given as a one-time infusion at a recommended dose of 10 mg/kg over 60 minutes." | idsa-shea-2021 | p11 | p11/narrative/bezlotoxumab-dose-infusion | narrative |
| bezlotoxumab-recurrence-window | adults-recurrent-cdi-six-months | add bezlotoxumab as a cointervention with standard-of-care antibiotics when recurrence occurred within the last 6 months | "For patients with a recurrent CDI episode within the last 6 months, we suggest using bezlotoxumab as a co-intervention along with SOC antibiotics rather than SOC antibiotics alone" | idsa-shea-2021 | p11 | p11/grade-spelled-out/1 | conditional, very low certainty |
| bezlotoxumab-age-risk-threshold | adults-primary-cdi-recurrence-risk | age >=65 years is a risk factor for recurrence | "patients with a primary CDI episode and other risk factors for CDI recurrence (such as age ≥65 years" | idsa-shea-2021 | p2 | p2/narrative/bezlotoxumab-age-risk | narrative |
| bezlotoxumab-age-risk-threshold | adults-primary-cdi-recurrence-risk | age >65 years is a risk factor for recurrence | RENDERED: "age >65 years" | idsa-shea-2021 | p3 | p3/narrative/bezlotoxumab-age-risk | narrative |
| bezlotoxumab-risk-factor-count | adults-primary-cdi-recurrence-risk | at least 1 risk factor supports adding bezlotoxumab; benefit appears more favorable with multiple risk factors | "favors adding bezlotoxumab to SOC antibiotics for patients with a CDI episode and at least 1 risk factor for recurrence" | idsa-shea-2021 | p13 | p13/narrative/bezlotoxumab-risk-factor-count | narrative |
| bezlotoxumab-administration-window | adults-cdi-bezlotoxumab | administer while the patient receives standard-of-care antibiotics and at any time before antibacterial treatment ends | "The infusion of bezlotoxumab should be performed while a patient is receiving SOC antibiotics and has been shown to be effective in preventing CDI if administered at any time before ending antibacterial treatment" | idsa-shea-2021 | p14 | p14/narrative/bezlotoxumab-administration-window | narrative |

## Conflicts

CONFLICT: bezlotoxumab-age-risk-threshold — `age >=65 years is a risk factor for recurrence; age >65 years is a risk factor for recurrence`. The executive-summary recommendation comment includes patients aged exactly 65 years, while the treatment-table footnote does not.

## Coverage

The bound recommendation file contains exactly 5 recommendation records: 1 is cited above and 4 are scoped below.

- `p1/grade-spelled-out/1` - scoped out because the recommendation to prefer fidaxomicin over a standard vancomycin course for an initial CDI episode is nonnumeric; the numeric regimens are captured from the rendered treatment table.
- `p1/grade-spelled-out/2` - scoped out because the recommendation to prefer standard or extended-pulsed fidaxomicin over a standard vancomycin course for recurrent CDI is nonnumeric; the numeric regimens are captured from the rendered treatment table and page 7 narrative.
- `p2/grade-spelled-out/1` - scoped out because extraction captured a malformed continuation of the bezlotoxumab recommendation rather than an independent recommendation record; its numeric age-risk statement is captured through the page-bound narrative locator.
- `p9/grade-spelled-out/1` - scoped out because it repeats the nonnumeric recurrent-CDI fidaxomicin recommendation; page 9's numeric definition of multiple recurrences is represented by the rendered treatment-table floor of at least 2 recurrences (3 CDI episodes).

ADR 0009 disposition: Table 1 is the guideline's patient-action treatment algorithm and was read from the rendered page; all of its numeric doses, durations, laboratory cutoffs, and recurrence floors are represented above. Tables 2-4 and Figures 1-5 report evidence selection, study flow, and effect estimates rather than additional patient-action thresholds and are scoped out.

ADR 0009 disposition: the 18-day bezlotoxumab elimination half-life, measurable concentrations through 3 months, trial response percentages, confidence intervals, follow-up periods, and other study-design or outcome figures are pharmacology or evidence descriptors, not instructions, and are scoped out.

ADR 0009 disposition: page 7's extended-fidaxomicin study schedule of 200 mg twice daily for 5 days followed by once daily on alternate days on days 7-25 is a trial-regimen description, not an additional guideline action. The rendered treatment-table regimen is retained instead.

ADR 0009 disposition: the FDA warning for patients with congestive heart failure contains no numeric threshold; it remains source guidance and is outside this decision-point-only sheet.

Source: `C:/codeing/guidelines-recs/IDSA/ciab549.json` (mode `bound`, counted from text markers). Source PDF SHA-256: `0bf8f3483969496aff9ab80d2b94ab3958c68ade8c815416e114d9b9215fd4b1`.
