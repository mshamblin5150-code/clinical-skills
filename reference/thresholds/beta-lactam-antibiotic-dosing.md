# Beta-lactam antibiotic dosing — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guidance** and not a clinical instruction: the panel expressly describes
several exposure-toxicity cutoffs as uncertain or less established rather than as
recommended safety targets.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsac-2026 | IDSA | IDSA/Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill | guideline | 2026 consensus guidance | 2026 | https://doi.org/10.1002/phar.70181 | stated |  |

## Scope

**Read:** the complete 27-page consensus guidance, page by page, including title
material, abstract, introduction, Tables 1-4, all thirteen questions and their
recommendations or best-practice statements, rationales, both figures, special
considerations, conclusion, disclosures, references, and the supporting-information
inventory. The recommendation artifact declares `nothing-found` and contains no
recommendation identifiers; that extractor result is not treated as proof that the
document contains no decision point, so this full-document read is the coverage
instrument.

**Not read:** nothing in the cataloged source PDF. Separately hosted supporting
information named on page 27 is outside the cataloged source and this sheet makes no
claim about it.

**Scoped out under ADR 0009's numeric patient-action rule:** publication and access
dates, author affiliations, literature-search dates, panel and voting counts,
reference numbers, journal volumes and pages, study sample sizes, odds ratios,
confidence intervals, posterior probabilities, follow-up periods, and other evidence
results were read but do not themselves define a patient action. This includes the
piperacillin mortality associations, cefepime neurotoxicity associations, very-high-
concentration neurotoxicity reports, and Cmin/MIC neurological-deterioration study on
page 11: the panel did not adopt any of them as a safety target. Administrative
program metrics, implementation cadence, laboratory turnaround goals, and assay-
development criteria that do not change an individual patient's dose, specimen
timing, or monitoring action are likewise outside the sheet.

**Source: `idsac-2026`**

| span | pages | read |
| --- | --- | --- |
| title material, abstract, introduction, and question summary before the quantitative definition table | 1-4 | read 2026-08-31; blind 2026-08-31 |
| quantitative definitions, methods, evidence process, and recommendation-strength framework | 5-7 | yes |
| clinical-impact recommendations, PK/PD targets, safety thresholds, and patient selection | 8-12 | yes |
| implementation stakeholders, workflow, specimen choice, and laboratory reporting | 13-16 | read 2026-08-31; blind 2026-08-31 |
| MIPD discordance, assay tolerances, sampling, MIC selection, and free-concentration guidance | 17-20 | yes |
| conclusion, administrative material, references, and supporting-information inventory | 21-27 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| acutely-ill-beta-lactam | acutely ill patients treated with beta-lactam therapy |
| decreased-distribution-infection | infections at sites with decreased drug distribution (e.g., meningitis) |
| traditional-tdm | patients undergoing traditional therapeutic drug monitoring |
| prolonged-infusion | patients receiving prolonged infusion beta-lactam therapy |
| continuous-infusion | patients receiving continuous infusion beta-lactam therapy |
| augmented-renal-clearance | patients with augmented renal clearance |
| mipd-discordance | patients whose observed beta-lactam concentration differs from the model-predicted concentration |
| continuous-infusion-nonmodel | patients receiving continuous infusion therapy when accurate model predictions are not achieved |
| resistant-no-safe-alternative | patients whose isolate exceeds the susceptibility breakpoint or ECV/ECOFF and for whom no other safe susceptible antibiotic exists |
| pseudomonas-meropenem-example | a patient with a P. aeruginosa bloodstream infection and a laboratory-reported meropenem MIC of 0.25 µg/mL |

## Quantities

| key | verbatim |
| --- | --- |
| minimum-pkpd-target | minimum PK/PD target for beta-lactam dose individualization |
| decreased-distribution-pkpd-target | higher plasma PK/PD target for an infection at a site with decreased drug distribution |
| traditional-tdm-start | usual timing of measured concentrations in traditional TDM |
| prolonged-infusion-duration | duration defining prolonged infusion beta-lactam therapy |
| continuous-infusion-duration | duration defining continuous infusion beta-lactam therapy |
| augmented-renal-clearance-cutoff | creatinine-clearance value typically defining augmented renal clearance in adults |
| discordance-concern | absolute prediction error from the observed concentration that represents a threshold of concern |
| assay-accuracy-precision | allowable assay accuracy and precision around expected concentrations |
| nonmodel-continuous-sampling | time after steady state at which a continuous-infusion concentration can be measured |
| no-alternative-mic-target | MIC multiple that may be considered when no other safe susceptible antibiotic exists |
| worked-meropenem-target | beta-lactam concentration target selected from the higher meropenem ECV/ECOFF or susceptibility breakpoint in the worked example |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| minimum-pkpd-target | acutely-ill-beta-lactam | at least 100% fT>MIC | RENDERED: pursue a minimum PK/PD target of 100% fT>MIC | idsac-2026 | p8 | p8/narrative/minimum-pkpd-target | narrative |
| decreased-distribution-pkpd-target | decreased-distribution-infection | 100% fT>4×MIC may be appropriate | RENDERED: a higher plasma PK/PD target such as 100% fT>4×MIC may be appropriate | idsac-2026 | p8 | p8/narrative/decreased-distribution-pkpd-target | narrative |
| traditional-tdm-start | traditional-tdm | typically day 1-3 of therapy or after | Typically occurs on day 1-3 of therapy or after | idsac-2026 | p5 | p5/narrative/traditional-tdm-start | narrative |
| prolonged-infusion-duration | prolonged-infusion | at least 2 hours | Drug delivery over at least 2 h | idsac-2026 | p5 | p5/narrative/prolonged-infusion-duration | narrative |
| continuous-infusion-duration | continuous-infusion | over 24 hours | continuous infusion (over 24 h) therapy | idsac-2026 | p5 | p5/narrative/continuous-infusion-duration | narrative |
| augmented-renal-clearance-cutoff | augmented-renal-clearance | creatinine clearance >130 mL/min/1.73 m² | RENDERED: creatinine clearance >130 mL/min/1.73 m² | idsac-2026 | p11 | p11/narrative/augmented-renal-clearance-cutoff | narrative |
| discordance-concern | mipd-discordance | absolute prediction error >20% from the observation is a threshold of concern | RENDERED: an absolute value of >20% prediction error from the observation represents a threshold of concern | idsac-2026 | p17 | p17/narrative/discordance-concern | narrative |
| assay-accuracy-precision | mipd-discordance | allowable accuracy and precision ±15% of expected concentration, or ±20% at the lower limit of quantification | RENDERED: an allowable range for assay accuracy and precision of ±15% of the expected concentrations (±20% at the lower limit of quantification) | idsac-2026 | p17 | p17/narrative/assay-accuracy-precision | narrative |
| nonmodel-continuous-sampling | continuous-infusion-nonmodel | measure after steady state, typically within 4-5 half-lives | RENDERED: after steady state is achieved, typically within 4-5 half-lives | idsac-2026 | p17 | p17/narrative/nonmodel-continuous-sampling | narrative |
| no-alternative-mic-target | resistant-no-safe-alternative | consider one doubling dilution above the isolate MIC if the required dose is safe in humans | RENDERED: consideration could be given to the use of one doubling dilution above the isolate MIC | idsac-2026 | p17 | p17/narrative/no-alternative-mic-target | narrative |
| worked-meropenem-target | pseudomonas-meropenem-example | target 2 µg/mL for 100% of the dosing interval despite reported MIC 0.25 µg/mL | RENDERED: despite documented laboratory reporting of an MIC of 0.25 μg/mL, the clinical team would target a beta-lactam concentration of 2 μg/mL for 100% of the dosing interval | idsac-2026 | p19 | p19/narrative/worked-meropenem-target | narrative |

## Conflicts

## Coverage

The recommendation artifact for this source declares `nothing-found` and contains no
recommendation identifiers to cite or scope out. That empty index does not establish
document completeness; the 27-page span table under `## Scope` and the explicit
disposition of study, administrative, and reference figures are the coverage
instrument. Tables 1 and 2 supplied multiple retained decision points; Tables 3 and 4
describe evidence grading and stakeholder roles without an additional numeric
patient-action threshold. Figures 1 and 2 were read with their captions and add no
numeric patient-action threshold beyond the discordance and MIC-selection rows above.
