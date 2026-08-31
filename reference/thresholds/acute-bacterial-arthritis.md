# Acute bacterial arthritis — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2023 | IDSA | IDSA/piad089 | guideline | 2024 | 2024 | https://doi.org/10.1093/jpids/piad089 | stated | bound |

## Scope

**Read:** the complete 59-page guideline, including the executive summary,
introduction and definitions, methods, all 15 clinical-question sections and their
recommendations, comments, evidence summaries, rationales, research needs, diagnostic
and treatment tables, figures, supplementary-material notice, disclosures, disclaimer,
and reference list. Tables 2, 4, and 5 were read as rendered tables because their cell
structure carries clinical decision points. The bound recommendation record contains
28 extracted occurrences; it is not a complete inventory of the source's recommendations,
so `## Coverage` accounts only for those 28 record entries while the full-page read
accounts for the guideline itself.

**Not read:** nothing in the source page range. The reference list was inspected for
scope and retired by class because it contains citations rather than clinical prose.

**Scoped out under ADR 0009's numeric decision-point rule:** study sizes, dates,
prevalence and positivity rates, confidence intervals, sensitivity and specificity,
risk estimates, outcome rates, trial doses not adopted by the panel, historical
practice, and research-method numbers were read but do not change what is done to a
patient. Qualitative recommendations and good-practice statements are accounted for
under `## Coverage` when they contain no numeric dose, duration, target, cutoff, or
follow-up interval.

**Source: `idsa-2023`**

| span | pages | read |
| --- | --- | --- |
| executive summary, introduction, definitions, and guideline scope | 1-7 | yes |
| guideline-development methods | 7-8 | read 2026-08-31; blind 2026-08-31 |
| diagnostic laboratory testing and evidence | 8-14 | yes |
| imaging recommendations and evidence | 14-19 | yes |
| invasive diagnosis and timing of empiric therapy | 19-25 | yes |
| empiric antimicrobial therapy | 25-28 | yes |
| repeat imaging and invasive source-control procedures | 28-29 | yes |
| intra-articular antimicrobial therapy and adjunctive corticosteroids | 29-32 | read 2026-08-31; blind 2026-08-31 |
| definitive therapy, pathogen table, and dosing table | 32-38 | yes |
| clinical and CRP response monitoring | 39-40 | yes |
| transition to oral therapy or OPAT | 40-44 | yes |
| total antimicrobial treatment duration | 44-48 | yes |
| follow-up imaging after primary ABA | 48-49 | read 2026-08-31; blind 2026-08-31 |
| treatment failure and recurrence | 49-51 | yes |
| clinical follow-up for sequelae | 51-52 | yes |
| disclosures and disclaimer | 52-53 | read 2026-08-31; blind 2026-08-31 |
| references | 53-59 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| otherwise-healthy-children-with-aba | otherwise healthy children 1 month to 17 years old in North America with acute bacterial arthritis |
| suspected-aba | children with suspected ABA |
| suspected-aba-age-6-to-48-months | infants and preschool aged children (6 to 48 months of age) with suspected ABA |
| suspected-aba-persistent-after-negative-ultrasound | children with a negative ultrasound result for effusion and persistent clinical suspicion for ABA |
| suspected-aba-high-risk-adjacent-osteomyelitis | children with ABA at high risk of adjacent osteomyelitis |
| aba-with-lyme-compatible-knee-arthritis | a weight bearing child with arthritis of the knee in a Lyme disease-endemic area |
| knee-aba-aspiration-candidates | children with ABA of the knee managed with aspiration alone |
| presumed-or-confirmed-aba-poor-response | children with presumed or confirmed ABA with poor clinical and laboratory response after initial invasive procedures and appropriate antimicrobial therapy |
| mild-moderate-aba-low-mrsa-region | children with mild to moderate ABA in regions with low rates of CA-MRSA arthritis |
| aba-region-mrsa-at-least-10-percent | children with ABA in regions where methicillin resistance is at least 10% to 20% |
| aba-mrsa-vancomycin-mic-at-least-2 | children with MRSA ABA caused by strains with vancomycin MIC at least 2 mcg/mL |
| confirmed-primary-aba-rapid-response | children with confirmed primary ABA without adjacent osteomyelitis with rapid clinical improvement and progressive CRP decrease by the end of the first week |
| primary-aba-slow-response | children with primary ABA with slower clinical response, inadequate source control, or persistently elevated CRP |
| presumed-primary-aba-rapid-response | children with presumed primary ABA without adjacent osteomyelitis with rapid clinical improvement and progressive CRP decrease by the end of the first week |
| aba-salmonella | children with ABA caused by Salmonella species |
| aba-brucella-older-than-7 | children older than 7 years with brucellar ABA |
| aba-brucella-age-7-or-younger | children age 7 years or younger with brucellar ABA |
| aba-gonococcal | sexually active adolescents with gonococcal ABA |
| aba-meningococcal | children with meningococcal ABA |
| aba-group-a-streptococcus | children with ABA caused by group A Streptococcus |
| aba-kingella | children with ABA caused by K. kingae |
| aba-mssa | children with ABA caused by methicillin-susceptible S. aureus |
| aba-mrsa | children with ABA caused by methicillin-resistant S. aureus |
| aba-mrsa-clindamycin-susceptible | children with ABA caused by methicillin-resistant S. aureus susceptible to clindamycin |
| aba-mrsa-clindamycin-resistant | children with ABA caused by methicillin-resistant S. aureus resistant to clindamycin |
| aba-pneumococcus-penicillin-mic-under-2 | children with pneumococcal ABA and penicillin MIC under 2 mcg/mL |
| aba-pneumococcus-penicillin-mic-at-least-2 | children with pneumococcal ABA and penicillin MIC at least 2 mcg/mL |
| aba-negative-cultures | children with suspected ABA and negative cultures and molecular tests |
| aba-on-prolonged-beta-lactam | children receiving prolonged high-dose beta-lactam therapy for ABA |
| aba-on-linezolid-over-2-weeks | children receiving linezolid for more than 2 weeks |
| aba-on-fluoroquinolone | children receiving fluoroquinolone therapy for ABA |
| aba-on-therapy | children receiving treatment for presumed or confirmed ABA |
| primary-aba-rapid-recovery | children with primary ABA that responds promptly to treatment |
| aba-treatment-failure | children with primary or secondary treatment failure |
| aba-persistent-bacteremia | children whose bacteremia persists during antimicrobial therapy, particularly with poor clinical response |
| children-with-aba-assessed-for-adjacent-infection | children with ABA being assessed for adjacent musculoskeletal infection |
| aba-repeat-procedure-risk | children with ABA being assessed for a repeat invasive procedure |
| aba-repeat-aspiration | children with ABA managed by repeated aspiration |
| aba-improving-for-oral-transition | children with ABA improving on initial parenteral therapy and being assessed for oral transition |
| culture-proven-common-pathogen-aba-over-3-months | previously healthy children older than 3 months with culture-proven ABA caused by common pathogens |
| complicated-primary-aba | children with more severe or complicated primary ABA |
| presumed-aba-response-guided-duration | children with presumed ABA and no identified pathogen whose duration is guided by clinical and laboratory response |
| aba-higher-sequela-risk | children with ABA at higher risk of long-term joint or growth complications |
| aba-h-influenzae-beta-lactamase-negative | children with ABA caused by beta-lactamase-negative H. influenzae |
| aba-h-influenzae-beta-lactamase-positive | children with ABA caused by beta-lactamase-producing H. influenzae |
| aba-antibiotic-dose-adjustment | children with ABA and renal or hepatic failure |
| aba-receiving-doxycycline-or-minocycline | children receiving doxycycline or minocycline for ABA |
| aba-receiving-fluoroquinolone | children or adolescents receiving a fluoroquinolone for ABA |
| aba-linezolid-over-4-weeks | children receiving linezolid for more than 4 weeks |
| pneumococcal-aba-severe-beta-lactam-allergy | children with pneumococcal ABA who are allergic to beta-lactams and intolerant of vancomycin or clindamycin |

## Quantities

| key | verbatim |
| --- | --- |
| guideline-age-scope | age range addressed by this guideline |
| kingella-empiric-coverage-age | empiric therapy to include activity against K. kingae |
| adjacent-osteomyelitis-risk-symptom-duration | symptom duration that increases risk of adjacent osteomyelitis |
| repeat-imaging-after-negative-ultrasound | repeat ultrasound or MRI when suspicion persists |
| follow-up-plain-film-interval | follow-up plain films to detect adjacent osteomyelitis |
| lyme-compatible-knee-low-aba-risk | peripheral WBC and ESR values indicating very low ABA risk |
| aspiration-alone-success-predictors | predictors of successful outcome with aspiration alone |
| aba-synovial-wbc-range | synovial fluid WBC count typical of ABA |
| transient-nonbacterial-synovitis-wbc-range | synovial fluid WBC count typical of transient nonbacterial synovitis |
| jia-synovial-wbc-range | synovial fluid WBC count typical of juvenile idiopathic arthritis |
| repeat-mri-window | time to MRI after poor response |
| repeat-source-control-window | time to additional invasive source control after poor response |
| low-region-mrsa-empiric-threshold | local CA-MRSA rate supporting MSSA-active empiric therapy |
| mrsa-active-empiric-threshold | local methicillin-resistance rate supporting MRSA-active empiric therapy |
| vancomycin-alternative-mic-threshold | vancomycin MIC prompting consideration of an alternative |
| crp-monitoring-interval | serial CRP monitoring interval |
| negative-culture-reassessment-window | time to reconsider the diagnosis after negative cultures |
| beta-lactam-cbc-monitoring | CBC monitoring during prolonged beta-lactam therapy |
| linezolid-cbc-monitoring | CBC monitoring during prolonged linezolid therapy |
| fluoroquinolone-return-threshold | persistent arthropathy or tendinopathy prompting evaluation |
| confirmed-primary-aba-duration | total antimicrobial duration for confirmed primary ABA |
| presumed-primary-aba-duration | total antimicrobial duration for presumed primary ABA |
| slow-response-aba-duration | total antimicrobial duration for slower-response primary ABA |
| group-a-streptococcus-duration | total antimicrobial duration for group A streptococcal ABA |
| kingella-duration | total antimicrobial duration for K. kingae ABA |
| meningococcal-duration | total antimicrobial duration for meningococcal ABA |
| gonococcal-duration | total antimicrobial duration for gonococcal ABA |
| pneumococcus-susceptible-duration | total duration for pneumococcal ABA with penicillin MIC under 2 mcg/mL |
| pneumococcus-resistant-duration | total duration for pneumococcal ABA with penicillin MIC at least 2 mcg/mL |
| salmonella-duration | total antimicrobial duration for Salmonella ABA |
| brucella-duration-and-gentamicin | brucellosis regimen duration and initial gentamicin duration |
| primary-treatment-failure-window | time defining lack of response to initial therapy |
| persistent-bacteremia-mri-window | time to MRI when bacteremia persists |
| prompt-response-follow-up-duration | specialist follow-up duration after prompt response |
| parenteral-ampicillin-dose | parenteral ampicillin dose |
| parenteral-cefazolin-dose | parenteral cefazolin dose |
| parenteral-ceftaroline-dose | parenteral ceftaroline dose |
| parenteral-ceftriaxone-dose | parenteral ceftriaxone dose |
| parenteral-ciprofloxacin-dose | parenteral ciprofloxacin dose |
| parenteral-clindamycin-dose | parenteral clindamycin dose |
| parenteral-daptomycin-dose | parenteral daptomycin dose by age |
| parenteral-levofloxacin-dose | parenteral levofloxacin dose by age |
| parenteral-linezolid-dose | parenteral linezolid dose by age |
| parenteral-moxifloxacin-dose | parenteral moxifloxacin dose by age |
| parenteral-nafcillin-dose | parenteral nafcillin dose |
| parenteral-oxacillin-dose | parenteral oxacillin dose |
| parenteral-penicillin-g-dose | parenteral penicillin G dose |
| parenteral-vancomycin-dose-and-target | parenteral vancomycin dose and exposure target |
| oral-amoxicillin-dose | oral amoxicillin dose |
| oral-cephalexin-dose | oral cephalexin dose |
| oral-clindamycin-dose | oral clindamycin dose |
| oral-levofloxacin-dose | oral levofloxacin dose by age |
| oral-ciprofloxacin-dose | oral ciprofloxacin dose |
| oral-linezolid-dose | oral linezolid dose by age |
| oral-doxycycline-minocycline-dose | oral doxycycline or minocycline dose |
| oral-trimethoprim-sulfamethoxazole-dose | oral trimethoprim-sulfamethoxazole dose |
| mssa-definitive-agents | definitive parenteral and oral agents for MSSA ABA |
| mrsa-clindamycin-susceptible-agents | definitive parenteral and oral agents for clindamycin-susceptible MRSA ABA |
| mrsa-clindamycin-resistant-agents | definitive parenteral and oral agents for clindamycin-resistant MRSA ABA |
| group-a-streptococcus-definitive-agents | definitive parenteral and oral agents for group A streptococcal ABA |
| kingella-definitive-agents | definitive parenteral and oral agents for K. kingae ABA |
| meningococcal-definitive-agents | definitive parenteral and oral agents for meningococcal ABA |
| gonococcal-definitive-agents | definitive parenteral and oral agents for gonococcal ABA |
| gonococcal-oral-agents | susceptibility-qualified oral agents for gonococcal ABA |
| pneumococcus-susceptible-definitive-agents | definitive parenteral and oral agents for penicillin-susceptible pneumococcal ABA |
| pneumococcus-resistant-definitive-agents | definitive parenteral and oral agents for relatively penicillin-resistant pneumococcal ABA |
| second-procedure-crp-predictor | CRP value above which a second procedure was likely in the cited study |
| adjacent-infection-prediction-rule | factors predicting adjacent musculoskeletal infection in a derived algorithm |
| repeat-procedure-inflammatory-risks | presenting inflammatory-marker risks for a repeat procedure |
| repeat-aspiration-age-risk | age associated with higher failure of repeated aspiration |
| oral-transition-crp-decline | CRP decline used with clinical improvement for oral transition |
| oral-transition-french-criteria | IV duration, afebrile period, and CRP criterion used for oral transition |
| oral-transition-crp-level | CRP value used with clinical improvement for oral transition |
| common-pathogen-short-course | shortest supported course and initial parenteral period for culture-proven common-pathogen ABA |
| complicated-aba-duration | reasonable total duration for more severe or complicated ABA |
| presumed-aba-short-course | shortest response-guided total duration for presumed ABA |
| sequela-risk-age-and-delay | age and treatment-delay factors associated with higher complication risk |
| h-influenzae-definitive-agents | definitive agents selected by beta-lactamase status for H. influenzae ABA |
| table5-dose-adjustment | Table 5 dose-adjustment qualification |
| tetracycline-age-caution | age qualification for doxycycline or minocycline use |
| fluoroquinolone-age-caution | age qualification for fluoroquinolone use |
| linezolid-neuropathy-duration | duration associated with optic and peripheral neuropathies |
| aspiration-failure-age-risk | age associated with aspiration treatment failure |
| aspiration-failure-crp-risk | CRP associated with aspiration treatment failure |
| crp-normalization-time | expected CRP normalization interval with appropriate therapy |
| vancomycin-trough-renal-toxicity | trough target associated with high doses and kidney injury |
| pneumococcal-severe-allergy-agents | fluoroquinolone options for defined severe beta-lactam allergy and intolerance |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guideline-age-scope | otherwise-healthy-children-with-aba | age 1 month to 17 years | "otherwise healthy children 1 month to 17 years old in North America" | idsa-2023 | p6 | p6/narrative/guideline-age-scope | narrative |
| kingella-empiric-coverage-age | suspected-aba-age-6-to-48-months | age 6-48 months: select empiric therapy that includes K. kingae activity rather than only S. aureus activity | "RENDERED: In infants and preschool aged children (6 to 48 months of age) with suspected ABA, we suggest selecting empiric therapy to include activity against K. kingae rather than only targeting S. aureus" | idsa-2023 | p25 | p25/grade-spelled-out/2 |  |
| adjacent-osteomyelitis-risk-symptom-duration | suspected-aba-high-risk-adjacent-osteomyelitis | symptoms >3 or 4 days before presentation increase risk and support MRI consideration | "more than 3 or 4 days of symptoms prior to presentation" | idsa-2023 | p15 | p15/narrative/adjacent-osteomyelitis-risk-symptom-duration | narrative |
| repeat-imaging-after-negative-ultrasound | suspected-aba-persistent-after-negative-ultrasound | if initial negative ultrasound occurred in first 24 hours and suspicion persists: repeat ultrasound or obtain MRI | "false negative ultrasound examinations were performed in the first 24 hours of illness; thus, children with a negative ultrasound result for effusion should have a repeat ultrasound examination or MRI if clinical suspicion for ABA persists" | idsa-2023 | p16 | p16/narrative/repeat-imaging-after-negative-ultrasound | narrative |
| follow-up-plain-film-interval | suspected-aba-high-risk-adjacent-osteomyelitis | consider plain films at 2 weeks into therapy | "obtain follow-up plain films at 2 weeks into therapy" | idsa-2023 | p19 | p19/narrative/follow-up-plain-film-interval | narrative |
| lyme-compatible-knee-low-aba-risk | aba-with-lyme-compatible-knee-arthritis | peripheral WBC <10,000 cells/microliter and ESR <40 mm/hr: very low ABA risk | "A peripheral WBC < 10,000 cells/microliter and ESR < 40 mm/hr in a weight bearing child with arthritis of the knee indicates a very low risk for ABA" | idsa-2023 | p14 | p14/narrative/lyme-compatible-knee-low-aba-risk | narrative |
| aspiration-alone-success-predictors | knee-aba-aspiration-candidates | age <3 years and CRP <20 mg/L predict success with aspiration alone | "age < 3 years and CRP < 20 mg/L were predictive of successful outcome with aspiration alone" | idsa-2023 | p20 | p20/narrative/aspiration-alone-success-predictors | narrative |
| aba-synovial-wbc-range | suspected-aba | usually >50,000/microliter and often >100,000/microliter | "RENDERED: In ABA, the joint fluid WBC count is usually greater than 50,000/µl and often exceeds 100,000/µl" | idsa-2023 | p20 | p20/narrative/aba-synovial-wbc-range | narrative |
| transient-nonbacterial-synovitis-wbc-range | suspected-aba | commonly 5,000-15,000/microliter | "RENDERED: in transient nonbacterial synovitis the WBC count is commonly 5,000 to 15,000/µl" | idsa-2023 | p20 | p20/narrative/transient-nonbacterial-synovitis-wbc-range | narrative |
| jia-synovial-wbc-range | suspected-aba | typically <50,000/microliter | "RENDERED: In JIA it is typically <50,000/µl" | idsa-2023 | p20 | p20/narrative/jia-synovial-wbc-range | narrative |
| repeat-mri-window | presumed-or-confirmed-aba-poor-response | poor response within 48-96 hours: perform MRI if not previously obtained | "RENDERED: In children with presumed or confirmed ABA who demonstrate a poor clinical and laboratory response within 48-96 hours (continued fever, persistent bacteremia and/or rising CRP) after initial invasive procedures (open or arthroscopic) and initiation of appropriate antimicrobial therapy, we suggest performing MRI if not previously obtained" | idsa-2023 | p28 | p28/narrative/repeat-mri-window | narrative |
| repeat-source-control-window | presumed-or-confirmed-aba-poor-response | poor response within 48-96 hours with persisting foci: perform additional invasive source-control procedures | "RENDERED: poor clinical and laboratory response within 48-96 hours (continued fever, persistent bacteremia and/or rising CRP) after initial invasive procedures, and evidence to suggest persisting foci of infection (ineffective source control), we suggest additional invasive procedures to ensure adequate source control" | idsa-2023 | p28 | p28/narrative/repeat-source-control-window | narrative |
| low-region-mrsa-empiric-threshold | mild-moderate-aba-low-mrsa-region | local CA-MRSA arthritis <about 10%: some experts begin oxacillin/nafcillin or cefazolin | "low rates of CA-MRSA arthritis (less than ~10%)" | idsa-2023 | p26 | p26/narrative/low-region-mrsa-empiric-threshold | narrative |
| mrsa-active-empiric-threshold | aba-region-mrsa-at-least-10-percent | methicillin resistance 10%-20% or greater: consider empiric MRSA-active therapy | "resistance to methicillin is estimated to be 10-20% or greater" | idsa-2023 | p26 | p26/narrative/mrsa-active-empiric-threshold | narrative |
| vancomycin-alternative-mic-threshold | aba-mrsa-vancomycin-mic-at-least-2 | MIC >=2 micrograms/mL: consider an alternative to vancomycin | "RENDERED: alternatives to vancomycin should be considered for MRSA infections caused by relatively vancomycin-non-susceptible strains (MIC ≥2 µg/mL)" | idsa-2023 | p27 | p27/narrative/vancomycin-alternative-mic-threshold | narrative |
| negative-culture-reassessment-window | aba-negative-cultures | at 48–72 hours: reconsider diagnosis and evaluate alternatives | "RENDERED: In children with suspected ABA and negative results of cultures after 48–72 hours of incubation (and negative results of any molecular microbial tests obtained), reconsideration of the diagnosis with re-evaluation for historical and physical examination findings that may support alternative etiologies is warranted." | idsa-2023 | p38 | p38/narrative/negative-culture-reassessment-window | narrative |
| beta-lactam-cbc-monitoring | aba-on-prolonged-beta-lactam | weekly or every 2 weeks CBC may help, particularly if course is more than three weeks | "RENDERED: weekly or biweekly (every 2 weeks) assessments of marrow function (e.g., a complete blood count with differential) have not been studied prospectively, but may be helpful, particularly for courses of therapy of more than three weeks" | idsa-2023 | p38 | p38/narrative/beta-lactam-cbc-monitoring | narrative |
| linezolid-cbc-monitoring | aba-on-linezolid-over-2-weeks | >2 weeks: CBC weekly | "For children receiving linezolid for more than 2 weeks, weekly screening for thrombocytopenia and neutropenia is recommended" | idsa-2023 | p36 | p36/narrative/linezolid-cbc-monitoring | narrative |
| fluoroquinolone-return-threshold | aba-on-fluoroquinolone | arthropathy or tendinopathy persisting >2-3 days: return for evaluation | "This potential adverse event should be discussed with families, with instructions for the family to return for evaluation should symptoms consistent with a persistent arthropathy or tendinopathy occur for more than 2-3 days during therapy" | idsa-2023 | p38 | p38/narrative/fluoroquinolone-return-threshold | narrative |
| crp-monitoring-interval | aba-on-therapy | every 2-3 days early, then weekly or periodically until a clear normalization trend | "RENDERED: Measurement every 2 to 3 days during the early therapeutic course, rather than daily, followed by weekly or other periodic measurement until a clear trend towards normalization is evident" | idsa-2023 | p40 | p40/narrative/crp-monitoring-interval | narrative |
| confirmed-primary-aba-duration | confirmed-primary-aba-rapid-response | 10-14 days total | "as short as 10 to 14 days for common pathogens" | idsa-2023 | p44 | p44/narrative/confirmed-primary-aba-duration | narrative |
| presumed-primary-aba-duration | presumed-primary-aba-rapid-response | 10-14 days total | "as short as 10 to 14 days rather than for longer courses" | idsa-2023 | p45 | p45/narrative/presumed-primary-aba-duration | narrative |
| slow-response-aba-duration | primary-aba-slow-response | 21-28 days may be preferred | "courses of therapy of 21 to 28 days may be preferred" | idsa-2023 | p45 | p45/narrative/slow-response-aba-duration | narrative |
| group-a-streptococcus-duration | aba-group-a-streptococcus | 10-14 days | "RENDERED: Group A streptococcus; 10-14 days" | idsa-2023 | p33 | p33/narrative/group-a-streptococcus-duration | narrative |
| kingella-duration | aba-kingella | 10-14 days | "RENDERED: K. kingae; 10-14 days" | idsa-2023 | p33 | p33/narrative/kingella-duration | narrative |
| meningococcal-duration | aba-meningococcal | 10-14 days | "RENDERED: N. meningitidis; 10-14 days" | idsa-2023 | p33 | p33/narrative/meningococcal-duration | narrative |
| gonococcal-duration | aba-gonococcal | 7-14 days | "RENDERED: N. gonorrhea; 7-14 days" | idsa-2023 | p33 | p33/narrative/gonococcal-duration | narrative |
| pneumococcus-susceptible-duration | aba-pneumococcus-penicillin-mic-under-2 | 10-14 days | "RENDERED: S. pneumoniae susceptible strains with MIC values to penicillin < 2.0 mcg/mL; 10-14 days" | idsa-2023 | p33 | p33/narrative/pneumococcus-susceptible-duration | narrative |
| pneumococcus-resistant-duration | aba-pneumococcus-penicillin-mic-at-least-2 | 14-21 days | "RENDERED: S. pneumoniae relatively resistant to penicillin with MIC values ≥ 2.0 mcg/mL; 14-21 days" | idsa-2023 | p34 | p34/narrative/pneumococcus-resistant-duration | narrative |
| salmonella-duration | aba-salmonella | limited evidence suggests 4-6 weeks may be needed, particularly with associated osteomyelitis | "These very limited data suggest these infections may need to be treated for 4-6 weeks." | idsa-2023 | p47 | p47/narrative/salmonella-duration | narrative |
| meningococcal-duration | aba-meningococcal | 4-day parenteral penicillin or ceftriaxone was successful in 8 mostly adult primary-ABA cases; limited pediatric evidence | "RENDERED: Administration of a 4-day course of parenteral penicillin or ceftriaxone was successful for treatment of 8 patients (mostly adults) with primary meningococcal ABA without meningitis" | idsa-2023 | p47 | p47/narrative/meningococcal-four-day-duration | narrative |
| gonococcal-duration | aba-gonococcal | fully susceptible strains: total 7-10 days, with oral cefixime or fluoroquinolone completion | "For fully susceptible strains, treatment may be completed with oral antibiotics, usually cefixime or fluoroquinolones, for a total course of 7 to 10 days." | idsa-2023 | p47 | p47/narrative/gonococcal-seven-to-ten-duration | narrative |
| brucella-duration-and-gentamicin | aba-brucella-older-than-7 | doxycycline plus rifampin for Six-to-12 weeks; often add gentamicin for first 1-2 weeks | "RENDERED: usually doxycycline with rifampin for children older than 7 years, and TMP/SMX with rifampin for children ≤7 years. Six-to-12-week minimum courses are recommended, often with the addition of gentamicin for the first 1-2 weeks of therapy" | idsa-2023 | p37 | p37/narrative/brucella-duration-and-gentamicin-older | narrative |
| brucella-duration-and-gentamicin | aba-brucella-age-7-or-younger | TMP/SMX plus rifampin for Six-to-12 weeks; often add gentamicin for first 1-2 weeks | "RENDERED: usually doxycycline with rifampin for children older than 7 years, and TMP/SMX with rifampin for children ≤7 years. Six-to-12-week minimum courses are recommended, often with the addition of gentamicin for the first 1-2 weeks of therapy" | idsa-2023 | p37 | p37/narrative/brucella-duration-and-gentamicin-younger | narrative |
| brucella-duration-and-gentamicin | aba-brucella-older-than-7 | treatment for at least 45 days | "RENDERED: Treatment for at least 45 days is recommended for pediatric brucellosis" | idsa-2023 | p47 | p47/narrative/brucella-at-least-45-days-older | narrative |
| brucella-duration-and-gentamicin | aba-brucella-age-7-or-younger | treatment for at least 45 days | "RENDERED: Treatment for at least 45 days is recommended for pediatric brucellosis" | idsa-2023 | p47 | p47/narrative/brucella-at-least-45-days-younger | narrative |
| primary-treatment-failure-window | aba-treatment-failure | lack of improvement two to four days after adequate therapy defines primary failure | "two to four days after initiation of presumed adequate antimicrobial therapy" | idsa-2023 | p49 | p49/narrative/primary-treatment-failure-window | narrative |
| persistent-bacteremia-mri-window | aba-persistent-bacteremia | bacteremia persisting 48-72 hours: obtain MRI of infection sites | "When bacteremia persists 48 to 72 hours into the course of antimicrobial therapy (particularly in the child with poor clinical response), the panel suggests obtaining MRI of the site(s) of infection" | idsa-2023 | p50 | p50/narrative/persistent-bacteremia-mri-window | narrative |
| prompt-response-follow-up-duration | primary-aba-rapid-recovery | follow-up not routinely required beyond 2-3 weeks from treatment start | "follow-up is not routinely required beyond 2-3 weeks from the start of treatment" | idsa-2023 | p51 | p51/narrative/prompt-response-follow-up-duration | narrative |
| second-procedure-crp-predictor | suspected-aba | CRP 150 mg/L: level above which a second surgery was likely in the cited study | "RENDERED: The authors concluded that a CRP of 150 mg/L was the level above which a second surgery would likely be needed." | idsa-2023 | p12 | p12/narrative/second-procedure-crp-predictor | narrative |
| adjacent-infection-prediction-rule | children-with-aba-assessed-for-adjacent-infection | age >3.6 years, CRP >13.8 mg/L, symptoms >3 days, platelets <314 x 10^3/microliter, and ANC >8.6 x 10^3/microliter predicted adjacent infection in the derived algorithm | "RENDERED: older age (above 3.6 years), higher CRP (>13.8 mg/L), longer duration of symptoms (more than 3 days), lower platelets (<314 X10(3) cells/µL), and higher ANC (>8.6 X 10(3) cells/µL)" | idsa-2023 | p17 | p17/narrative/adjacent-infection-prediction-rule | narrative |
| repeat-procedure-inflammatory-risks | aba-repeat-procedure-risk | presenting CRP >100 mg/L and ESR >40 mm/hour: risks for requiring a repeat procedure | "RENDERED: presenting CRP >100 mg/L (normal <10), presenting ESR >40 mm/hour, adjacent AHO, and intraoperative cultures positive for MRSA as risks for requiring a repeat procedure" | idsa-2023 | p29 | p29/narrative/repeat-procedure-inflammatory-risks | narrative |
| repeat-aspiration-age-risk | aba-repeat-aspiration | age >10 years: repeated-aspiration failure may be higher | "failure rate with repeated aspirations may be higher among children older than 10 years" | idsa-2023 | p29 | p29/narrative/repeat-aspiration-age-risk | narrative |
| oral-transition-crp-decline | aba-improving-for-oral-transition | CRP decline >=50% plus clinical improvement used to support oral transition | "Successful transition to oral therapy after good clinical response plus CRP decline by 50% or more has been described" | idsa-2023 | p39 | p39/narrative/oral-transition-crp-decline | narrative |
| oral-transition-french-criteria | aba-improving-for-oral-transition | 48 hours IV therapy, 24 hours afebrile, clinical improvement, and CRP <20 mg/L | "Criteria for transition to oral therapy were receipt of 48 hours of IV therapy, 24 hours without fever, improvement of clinical findings, and significant decrease in inflammatory markers, which included CRP < 20 mg/L." | idsa-2023 | p41 | p41/narrative/oral-transition-french-criteria | narrative |
| oral-transition-crp-level | aba-improving-for-oral-transition | CRP 20-30 mg/L plus clinical improvement used for oral transition | "RENDERED: using clinical improvement plus CRP values having fallen to 20 to 30 mg/L (normal ≤9 mg/L) as criteria for transition to oral therapy" | idsa-2023 | p41 | p41/narrative/oral-transition-crp-level | narrative |
| oral-transition-crp-decline | aba-improving-for-oral-transition | 50% CRP decline plus clinical improvement used for oral transition in another cohort | "RENDERED: used a 50% decline in CRP values plus clinical improvement to transition to oral therapy" | idsa-2023 | p43 | p43/narrative/oral-transition-crp-decline-repeat | narrative |
| common-pathogen-short-course | culture-proven-common-pathogen-aba-over-3-months | total 10 days after 2-4 days initial parenteral therapy when clinical and CRP improvement is documented | "previously healthy children older than 3 months of age with culture proven ABA due to common pathogens treated for a total duration of 10 days is not different to those treated for 30 days, if clinical and CRP improvement is documented. This is typically accomplished by 2 to 4 days of initial parenteral antibiotic therapy" | idsa-2023 | p48 | p48/narrative/common-pathogen-short-course | narrative |
| complicated-aba-duration | complicated-primary-aba | at least 3-4 weeks, individualized | "RENDERED: For more severe infections (e.g., \"complicated ABA\") as determined based on initial clinical and laboratory parameters and on the clinical course on therapy, a total duration of at least 3 to 4 weeks, determined on a case-by-case basis, is reasonable" | idsa-2023 | p48 | p48/narrative/complicated-aba-duration | narrative |
| presumed-aba-short-course | presumed-aba-response-guided-duration | as short as 10 days based on clinical and laboratory response | "total duration of therapy may be based on the observed response from clinical and laboratory data, with treatment durations as short as 10 days" | idsa-2023 | p48 | p48/narrative/presumed-aba-short-course | narrative |
| sequela-risk-age-and-delay | aba-higher-sequela-risk | age less than 6 months or delay of diagnosis/definitive surgical management beyond 4 days: higher complication risk | "RENDERED: infants less than 6 months of age, as well as those with ABA of the hip or shoulder, and those with delay of diagnosis or definitive surgical management beyond 4 days into treatment" | idsa-2023 | p51 | p51/narrative/sequela-risk-age-and-delay | narrative |
| h-influenzae-definitive-agents | aba-h-influenzae-beta-lactamase-negative | parenteral ampicillin; oral amoxicillin | "RENDERED: Parenteral ampicillin may be used for beta-lactamase negative strains. Parenteral second (cefuroxime) or third generation cephalosporins (cefotaxime/ceftriaxone/ceftazidime) may be used as alternatives or for beta-lactamase producing isolates. For oral convalescent therapy for beta-lactamase negative strains, amoxicillin should be used." | idsa-2023 | p36 | p36/narrative/h-influenzae-beta-lactamase-negative | narrative |
| h-influenzae-definitive-agents | aba-h-influenzae-beta-lactamase-positive | parenteral cefuroxime, cefotaxime, ceftriaxone, or ceftazidime; oral cefuroxime, cefdinir, cefpodoxime, ceftibuten, or amoxicillin/clavulanate | "RENDERED: Parenteral second (cefuroxime) or third generation cephalosporins (cefotaxime/ceftriaxone/ceftazidime) may be used as alternatives or for beta-lactamase producing isolates. Oral second (cefuroxime) and third generation cephalosporins (cefdinir, cefpodoxime, ceftibuten) or beta-lactam/beta-lactamase inhibitor combinations (e.g., amoxicillin-clavulanate) should provide effective" | idsa-2023 | p36 | p36/narrative/h-influenzae-beta-lactamase-positive | narrative |
| table5-dose-adjustment | aba-antibiotic-dose-adjustment | dose adjustment may be needed with renal or hepatic failure | "RENDERED: Dose Adjustment may be Needed in Children with Renal or Hepatic Failure" | idsa-2023 | p35 | p35/narrative/table5-dose-adjustment | narrative |
| tetracycline-age-caution | aba-receiving-doxycycline-or-minocycline | traditionally not used routinely at age <8 years; prohibition is evolving | "Traditionally have not been used routinely in children < 8 years old, but evidence and thoughts on this prohibition are evolving." | idsa-2023 | p36 | p36/narrative/tetracycline-age-caution | narrative |
| fluoroquinolone-age-caution | aba-receiving-fluoroquinolone | age <18 years: use caution because of potential cartilage toxicity | "RENDERED: Caution must be observed when using fluoroquinolones in children and adolescents <18 years old due to potential for cartilage toxicity" | idsa-2023 | p36 | p36/narrative/fluoroquinolone-age-caution | narrative |
| linezolid-neuropathy-duration | aba-linezolid-over-4-weeks | more than 4 weeks: optic and peripheral neuropathies have been described | "optic and peripheral neuropathies, have been described in both adults and children receiving more than 4 weeks of linezolid" | idsa-2023 | p38 | p38/narrative/linezolid-neuropathy-duration | narrative |
| aspiration-failure-age-risk | knee-aba-aspiration-candidates | age >3 years: higher aspiration-treatment failure | "RENDERED: Risk of treatment failure in a series of 74 children with ABA of the knee treated with antibiotics and needle aspiration alone was higher in children > 3 years old" | idsa-2023 | p49 | p49/narrative/aspiration-failure-age-risk | narrative |
| aspiration-failure-crp-risk | knee-aba-aspiration-candidates | CRP >20 mg/L at any age: higher aspiration-treatment failure | "children of any age with serum CRP concentration > 20 mg/L" | idsa-2023 | p50 | p50/narrative/aspiration-failure-crp-risk | narrative |
| salmonella-duration | aba-salmonella | longer than 10-14 days according to clinical and laboratory response, up to 4-6 weeks particularly with associated osteomyelitis | "RENDERED: Courses longer than 10 to 14 days may be required, depending on the clinical and laboratory response of an individual child, with treatment up to 4 to 6 weeks, particularly in those with associated osteomyelitis." | idsa-2023 | p37 | p37/narrative/salmonella-response-guided-duration | narrative |
| confirmed-primary-aba-duration | confirmed-primary-aba-rapid-response | 10-14 days when rapid improvement and CRP decline, for example CRP <20 mcg/L, are evident | "ABA caused by S. aureus, S. pyogenes, S. pneumoniae or Hib may be treated for 10 to 14 days if rapid clinical improvement and CRP decline (e.g., <20 mcg/L) are evident" | idsa-2023 | p47 | p47/narrative/confirmed-duration-crp-support | narrative |
| crp-normalization-time | aba-on-therapy | typically returns to normal in about 9-12 days with appropriate therapy | "With appropriate therapy, this is followed by a progressive decline, and the CRP typically returns to the normal range in about 9 to 12 days" | idsa-2023 | p39 | p39/narrative/crp-normalization-time | narrative |
| vancomycin-trough-renal-toxicity | aba-mrsa | target trough >15 micrograms/mL required high doses associated with acute kidney injury and no improved osteomyelitis outcomes | "RENDERED: Initial guidelines by IDSA for vancomycin dosing in severe CA-MRSA infections recommended target serum trough levels > 15 micrograms/ml. The high doses required to achieve this goal were associated with acute kidney injury and were not associated with improved outcomes in children with osteomyelitis when compared with lower doses." | idsa-2023 | p34 | p34/narrative/vancomycin-trough-renal-toxicity | narrative |
| pneumococcal-severe-allergy-agents | pneumococcal-aba-severe-beta-lactam-allergy | levofloxacin or moxifloxacin | "For children infected by S. pneumonia, but allergic to beta-lactams and intolerant of vancomycin or clindamycin, levofloxacin or moxifloxacin are effective options." | idsa-2023 | p34 | p34/narrative/pneumococcal-severe-allergy-agents | narrative |
| mssa-definitive-agents | aba-mssa | parenteral preferred cefazolin or oxacillin/nafcillin; alternatives clindamycin or vancomycin; oral preferred cephalexin, alternative clindamycin | "RENDERED: S. aureus, methicillin susceptible (MSSA): parenteral preferred cefazolin or semisynthetic penicillin, e.g., oxacillin, nafcillin; alternatives clindamycin, vancomycin; oral preferred cephalexin; alternative clindamycin" | idsa-2023 | p33 | p33/narrative/mssa-definitive-agents | narrative |
| mrsa-clindamycin-susceptible-agents | aba-mrsa-clindamycin-susceptible | parenteral and oral preferred clindamycin; parenteral alternatives ceftaroline, vancomycin, or linezolid; oral alternatives linezolid, doxycycline/minocycline, or TMP/SMX | "RENDERED: S. aureus, methicillin-resistant (MRSA), susceptible to clindamycin: preferred clindamycin; parenteral alternatives ceftaroline, vancomycin, linezolid; oral alternatives linezolid, doxycycline/minocycline, trimethoprim-sulfamethoxazole" | idsa-2023 | p33 | p33/narrative/mrsa-clindamycin-susceptible-agents | narrative |
| mrsa-clindamycin-resistant-agents | aba-mrsa-clindamycin-resistant | parenteral preferred ceftaroline or vancomycin, alternatives linezolid or daptomycin; oral preferred linezolid, alternatives doxycycline/minocycline or TMP/SMX; some children require full parenteral therapy | "RENDERED: S. aureus methicillin-resistant (MRSA), resistant to clindamycin: parenteral preferred ceftaroline or vancomycin; alternatives linezolid, daptomycin; oral preferred linezolid; alternatives doxycycline/minocycline, trimethoprim-sulfamethoxazole; some children may require the entire treatment course with parenteral therapy" | idsa-2023 | p33 | p33/narrative/mrsa-clindamycin-resistant-agents | narrative |
| group-a-streptococcus-definitive-agents | aba-group-a-streptococcus | parenteral preferred penicillin G or ampicillin; alternatives cefazolin, ceftriaxone, or clindamycin; oral preferred amoxicillin; alternatives penicillin V, clindamycin, or cephalexin | "RENDERED: Group A streptococcus: parenteral preferred penicillin G or ampicillin; alternatives cefazolin, ceftriaxone, clindamycin; oral preferred amoxicillin; alternatives penicillin V, clindamycin, cephalexin" | idsa-2023 | p33 | p33/narrative/group-a-streptococcus-definitive-agents | narrative |
| kingella-definitive-agents | aba-kingella | parenteral preferred ampicillin; alternatives cefazolin, ceftriaxone, ceftaroline, or ciprofloxacin; oral preferred amoxicillin; alternatives amoxicillin/clavulanate, cephalexin, ciprofloxacin, or TMP/SMX | "RENDERED: K. kingae: parenteral preferred ampicillin; alternatives cefazolin, ceftriaxone, ceftaroline, ciprofloxacin; oral preferred amoxicillin; alternatives amoxicillin/clavulanate, cephalexin, ciprofloxacin, trimethoprim-sulfamethoxazole" | idsa-2023 | p33 | p33/narrative/kingella-definitive-agents | narrative |
| meningococcal-definitive-agents | aba-meningococcal | parenteral preferred penicillin G or ampicillin, alternative ceftriaxone; oral preferred amoxicillin, alternative penicillin V | "RENDERED: N. meningitidis: parenteral preferred penicillin G or ampicillin; alternative ceftriaxone; oral preferred amoxicillin; alternative penicillin V" | idsa-2023 | p33 | p33/narrative/meningococcal-definitive-agents | narrative |
| gonococcal-definitive-agents | aba-gonococcal | start parenteral ceftriaxone | "RENDERED: Parenteral therapy with a third-generation cephalosporin, typically ceftriaxone, should be started." | idsa-2023 | p37 | p37/narrative/gonococcal-definitive-agents | narrative |
| gonococcal-oral-agents | aba-gonococcal | consider oral therapy only after susceptibility data, using high-dose cefixime or a fluoroquinolone if susceptible | "RENDERED: Oral therapy generally should be considered only after antibiotic susceptibility data are available. Due to increasing resistance to azithromycin, combination therapy of azithromycin with ceftriaxone is no longer routinely recommended. Oral options may include high dose oral cefixime or a fluoroquinolone if susceptibility has been documented." | idsa-2023 | p37 | p37/narrative/gonococcal-oral-agents | narrative |
| pneumococcus-susceptible-definitive-agents | aba-pneumococcus-penicillin-mic-under-2 | parenteral preferred penicillin G or ampicillin; alternatives ceftriaxone, levofloxacin, linezolid, or clindamycin if susceptible; oral preferred amoxicillin or penicillin V; alternatives cephalexin, levofloxacin, linezolid, or clindamycin if susceptible | "RENDERED: S. pneumoniae susceptible strains with MIC values to penicillin <2.0 mcg/mL. Parenteral preferred: Penicillin G or Ampicillin. Alternatives: Ceftriaxone, Levofloxacin, Linezolid, Clindamycin (if susceptible). Oral preferred: Amoxicillin or Penicillin V. Alternatives: Cephalexin, Levofloxacin, Linezolid, Clindamycin (if susceptible)." | idsa-2023 | p33 | p33/narrative/pneumococcus-susceptible-definitive-agents | narrative |
| pneumococcus-resistant-definitive-agents | aba-pneumococcus-penicillin-mic-at-least-2 | if ceftriaxone MIC <=1 mcg/mL, parenteral preferred ceftriaxone; alternatives clindamycin if susceptible, levofloxacin, or linezolid; oral preferred clindamycin if susceptible or levofloxacin, alternative linezolid | "RENDERED: S. pneumoniae relatively resistant to penicillin with MIC values ≥2.0 mcg/mL. Parenteral preferred: Ceftriaxone (if ceftriaxone MIC ≤1 mcg/ml). Alternatives: Clindamycin (if susceptible), Levofloxacin, Linezolid. Oral preferred: Clindamycin (if susceptible), Levofloxacin. Alternative: Linezolid." | idsa-2023 | p34 | p34/narrative/pneumococcus-resistant-definitive-agents | narrative |
| parenteral-ampicillin-dose | otherwise-healthy-children-with-aba | 200 mg/kg/day divided every 6 hours; maximum 8 g/day | "RENDERED: Ampicillin; 200 mg/kg/day in divided doses every 6 h; 8 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-ampicillin-dose | narrative |
| parenteral-cefazolin-dose | otherwise-healthy-children-with-aba | 100-150 mg/kg/day divided every 8 hours; maximum 12 g/day; use higher end for more invasive staphylococcal infection with inadequate debridement | "RENDERED: Cefazolin; 100-150 mg/kg/day in divided doses every 8 h; 12 g/day; higher end of dosing range for more invasive staphylococcal infection with inadequate debridement" | idsa-2023 | p35 | p35/narrative/parenteral-cefazolin-dose | narrative |
| parenteral-ceftaroline-dose | otherwise-healthy-children-with-aba | 45 mg/kg/day divided every 8 hours, each dose infused over 1-2 hours; maximum 1.8 g/day | "RENDERED: Ceftaroline; 45 mg/kg/day in divided doses every 8 h, each dose infused over 1-2 h; 1.8 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-ceftaroline-dose | narrative |
| parenteral-ceftriaxone-dose | otherwise-healthy-children-with-aba | 50-100 mg/kg/day once daily or divided every 12 hours; maximum 4 g/day | "RENDERED: Ceftriaxone; 50-100 mg/kg/day once daily or in two divided doses every 12 h; 4 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-ceftriaxone-dose | narrative |
| parenteral-ciprofloxacin-dose | otherwise-healthy-children-with-aba | 16-20 mg/kg/day divided every 12 hours; maximum 800 mg/day | "RENDERED: Ciprofloxacin; 16-20 mg/kg/day in divided doses every 12 h; 800 mg/day" | idsa-2023 | p35 | p35/narrative/parenteral-ciprofloxacin-dose | narrative |
| parenteral-clindamycin-dose | otherwise-healthy-children-with-aba | 30-40 mg/kg/day divided every 6-8 hours; maximum 2.7 g/day | "RENDERED: Clindamycin; 30-40 mg/kg/day in divided doses every 6 to 8 h; 2.7 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-clindamycin-dose | narrative |
| parenteral-daptomycin-dose | otherwise-healthy-children-with-aba | once daily: age 12-17 years 7 mg/kg; age 7-11 years 9 mg/kg; age 1-6 years 12 mg/kg; not recommended under age 1 year | "RENDERED: Daptomycin; 12-17 years: 7 mg/kg; 7-11 years: 9 mg/kg; 1-6 years: 12 mg/kg; not recommended for children under one year of age" | idsa-2023 | p35 | p35/narrative/parenteral-daptomycin-dose | narrative |
| parenteral-levofloxacin-dose | otherwise-healthy-children-with-aba | age >=5 years 10 mg/kg/day once daily; age 6 months to <5 years 20 mg/kg/day divided every 12 hours; maximum 750 mg/day | "RENDERED: Levofloxacin; ≥ 5 years: 10 mg/kg/day once daily; 6 months - < 5 years: 20 mg/kg/day in divided doses every 12 h; 750 mg/day" | idsa-2023 | p35 | p35/narrative/parenteral-levofloxacin-dose | narrative |
| parenteral-linezolid-dose | otherwise-healthy-children-with-aba | age >=12 years 20 mg/kg/day every 12 hours; age >=5 to <12 years 30 mg/kg/day every 8 hours; birth to <5 years 30 mg/kg/day every 8 hours; maximum 1200 mg/day | "RENDERED: Linezolid; ≥12 years: 20 mg/kg/day in divided doses every 12 h; ≥ 5 years - < 12 years: 30 mg/kg/day in divided doses every 8 h; Birth - < 5 years: 30 mg/kg/day in divided doses every 8 hours; 1200 mg" | idsa-2023 | p35 | p35/narrative/parenteral-linezolid-dose | narrative |
| parenteral-moxifloxacin-dose | otherwise-healthy-children-with-aba | divided every 12 hours: age >=12 to <18 years 8 mg/kg/day; >=6 to <12 years 8 mg/kg/day; >=2 to <6 years 10 mg/kg/day; source-defective youngest band printed "3 - <2 years" at 12 mg/kg/day; maximum 400 mg/day | "RENDERED: Moxifloxacin; ≥ 12- < 18 years: 8 mg/kg/day; ≥ 6 - <12 years: 8 mg/kg/day; ≥ 2- < 6 years: 10 mg/kg/day; 3 - < 2 years: 12 mg/kg/day; 400 mg/day" | idsa-2023 | p35 | p35/narrative/parenteral-moxifloxacin-dose | narrative |
| parenteral-nafcillin-dose | otherwise-healthy-children-with-aba | 100-200 mg/kg/day divided every 6 hours; maximum 12 g/day | "RENDERED: Nafcillin; 100-200 mg/kg/day in divided doses every 6 h; 12 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-nafcillin-dose | narrative |
| parenteral-oxacillin-dose | otherwise-healthy-children-with-aba | 100-200 mg/kg/day divided every 6 hours; maximum 12 g/day | "RENDERED: Oxacillin; 100-200 mg/kg/day in divided doses every 6 h; 12 g/day" | idsa-2023 | p35 | p35/narrative/parenteral-oxacillin-dose | narrative |
| parenteral-penicillin-g-dose | otherwise-healthy-children-with-aba | 200 000-300 000 IU/kg/day divided every 4-6 hours; maximum 20 000 000 U/day | "RENDERED: Penicillin G crystalline; 200 000 - 300 000 IU/kg/day in divided doses every 4 to 6 h; 20 000 000 U/day" | idsa-2023 | p35 | p35/narrative/parenteral-penicillin-g-dose | narrative |
| parenteral-vancomycin-dose-and-target | aba-mrsa | 40-60 mg/kg/day divided every 6-8 hours; no mg/kg maximum; target AUC/MIC >400; monitor serum concentrations and renal function; less renal toxicity than trough 15-20 mcg/mL exposure | "RENDERED: Vancomycin; 40-60 mg/kg/day in divided doses every 6 to 8 h; no mg/kg maximum, but follow for renal toxicity; dosing to achieve an AUC/MIC of >400; associated with the same antibiotic exposure, but less renal toxicity than trough concentrations of 15-20 mcg/mL; monitor serum concentrations and renal function" | idsa-2023 | p35 | p35/narrative/parenteral-vancomycin-dose-and-target | narrative |
| oral-amoxicillin-dose | otherwise-healthy-children-with-aba | 50-100 mg/kg/day divided every 8 hours; maximum 4 g/day | "RENDERED: Amoxicillin; 50-100 mg/kg/day in divided doses every 8 h; 4 g/day" | idsa-2023 | p35 | p35/narrative/oral-amoxicillin-dose | narrative |
| oral-cephalexin-dose | otherwise-healthy-children-with-aba | 75-100 mg/kg/day divided three or four times daily; maximum 4 g/day, with some experts using up to 6 g/day | "RENDERED: Cephalexin; 75-100 mg/kg/day in divided doses three or four times per day; 4 g/day; some experts recommend up to 6 g/day" | idsa-2023 | p35 | p35/narrative/oral-cephalexin-dose | narrative |
| oral-clindamycin-dose | otherwise-healthy-children-with-aba | 30-40 mg/kg/day divided three or four times daily; maximum 1.8 g/day, with some experts using up to 2.7 g/day | "RENDERED: Clindamycin; 30-40 mg/kg/day in divided doses three or four times per day; 1.8 g/day; some experts recommend up to 2.7 g/day" | idsa-2023 | p35 | p35/narrative/oral-clindamycin-dose | narrative |
| oral-levofloxacin-dose | otherwise-healthy-children-with-aba | age >=5 years 10 mg/kg/day once daily; age 6 months to <5 years 20 mg/kg/day divided every 12 hours; maximum 750 mg/day | "RENDERED: Levofloxacin; ≥ 5 years: 10 mg/kg/day once daily; 6 months - < 5 years: 20 mg/kg/day in divided doses every 12 h; 750 mg/day" | idsa-2023 | p36 | p36/narrative/oral-levofloxacin-dose | narrative |
| oral-ciprofloxacin-dose | otherwise-healthy-children-with-aba | 30 mg/kg/day divided every 12 hours; maximum 1.5 g/day | "RENDERED: Ciprofloxacin; 30 mg/kg/day in divided doses every 12 h; 1.5 g/day" | idsa-2023 | p36 | p36/narrative/oral-ciprofloxacin-dose | narrative |
| oral-linezolid-dose | otherwise-healthy-children-with-aba | age >=12 years 20 mg/kg/day every 12 hours; age >=5 to <12 years 30 mg/kg/day every 8 hours; birth to <5 years 30 mg/kg/day every 8 hours; maximum 1200 mg/day | "RENDERED: Linezolid; ≥12 years: 20 mg/kg/day in divided doses every 12 h; ≥ 5 years - < 12 years: 30 mg/kg/day in divided doses every 8 h; Birth - < 5 years: 30 mg/kg/day in divided doses every 8 hours; 1200 mg/day" | idsa-2023 | p36 | p36/narrative/oral-linezolid-dose | narrative |
| oral-doxycycline-minocycline-dose | aba-receiving-doxycycline-or-minocycline | 4 mg/kg/day divided every 12 hours; maximum 200 mg/day; traditionally not routine at age <8 years | "RENDERED: Doxycycline/minocycline; 4 mg/kg/day in divided doses every 12 h; 200 mg/day; traditionally have not been used routinely in children < 8 years old, but evidence and thoughts on this prohibition are evolving." | idsa-2023 | p36 | p36/narrative/oral-doxycycline-minocycline-dose | narrative |
| oral-trimethoprim-sulfamethoxazole-dose | otherwise-healthy-children-with-aba | 12 mg/kg/day trimethoprim component divided every 12 hours | "RENDERED: Trimethoprim-sulfamethoxazole; 12 mg/kg/day (trimethoprim component) in divided doses every 12 h" | idsa-2023 | p36 | p36/narrative/oral-trimethoprim-sulfamethoxazole-dose | narrative |

## Conflicts

CONFLICT: meningococcal-duration — for `aba-meningococcal`, Table 4 gives `10-14 days`, while the narrative gives `4-day parenteral penicillin or ceftriaxone was successful in 8 mostly adult primary-ABA cases; limited pediatric evidence`; the table range remains the direct pediatric selection.

CONFLICT: gonococcal-duration — for `aba-gonococcal`, Table 4 gives `7-14 days`, while the susceptibility-qualified narrative gives `fully susceptible strains: total 7-10 days, with oral cefixime or fluoroquinolone completion`; susceptibility and oral-completion eligibility explain the narrower alternative.

CONFLICT: brucella-duration-and-gentamicin — for `aba-brucella-older-than-7`, the pathogen discussion gives `doxycycline plus rifampin for Six-to-12 weeks; often add gentamicin for first 1-2 weeks`, while the duration section gives `treatment for at least 45 days`; for `aba-brucella-age-7-or-younger`, the pathogen discussion gives `TMP/SMX plus rifampin for Six-to-12 weeks; often add gentamicin for first 1-2 weeks`, while the duration section gives `treatment for at least 45 days`. These are compatible minimum formulations, not evidence for shortening either regimen.

CONFLICT: presumed-primary-aba-duration — the formal recommendation gives 10-14 days for rapidly improving presumed primary ABA without adjacent osteomyelitis, while the later rationale says response-guided treatment may be as short as 10 days; the latter is the lower endpoint, not a separate routine range.

CONFLICT: salmonella-duration — for `aba-salmonella`, the response-guided discussion gives `longer than 10-14 days according to clinical and laboratory response, up to 4-6 weeks particularly with associated osteomyelitis`, while the duration section gives `limited evidence suggests 4-6 weeks may be needed, particularly with associated osteomyelitis`; clinical response and adjacent osteomyelitis qualify the longer alternative.

CONFLICT: oral-transition-crp-decline — for `aba-improving-for-oral-transition`, one cohort used `CRP decline >=50% plus clinical improvement used to support oral transition`, while another used `50% CRP decline plus clinical improvement used for oral transition in another cohort`; these are study criteria rather than a validated universal cutoff.

CONFLICT: confirmed-primary-aba-duration — for `confirmed-primary-aba-rapid-response`, the general duration discussion gives `10-14 days total`, while the pathogen-specific rationale gives `10-14 days when rapid improvement and CRP decline, for example CRP <20 mcg/L, are evident`; the latter states the response qualification supporting the same range.

## Coverage

- `p1/grade-spelled-out/1` - scoped out: qualitative blood-culture recommendation; its timing is before antimicrobial therapy, not a numeric dose, duration, target, cutoff, or interval.
- `p1/grade-spelled-out/2` - scoped out: recommendation against procalcitonin measurement states no numeric patient-action point.
- `p1/grade-spelled-out/3` - scoped out: qualitative plain-radiography recommendation states no numeric patient-action point.
- `p2/grade-spelled-out/1` - scoped out: qualitative ultrasonography-first recommendation states no numeric patient-action point.
- `p2/grade-spelled-out/2` - scoped out: qualitative MRI preference states no numeric patient-action point; the high-risk symptom-duration threshold is cited from narrative.
- `p2/grade-spelled-out/3` - scoped out: arthrocentesis-before-therapy recommendation states no numeric patient-action point.
- `p2/grade-spelled-out/4` - scoped out: qualitative joint-fluid testing recommendation states no numeric patient-action point.
- `p2/grade-spelled-out/5` - scoped out: immediate empiric-therapy recommendation states no numeric dose or clock time.
- `p2/grade-spelled-out/6` - scoped out: qualitative S. aureus coverage recommendation states no numeric patient-action point.
- `p2/grade-spelled-out/7` - duplicate executive-summary occurrence of the age 6-48-month K. kingae threshold cited from `p25/grade-spelled-out/2` above.
- `p3/grade-spelled-out/1` - scoped out: recommendation against routine intra-articular antimicrobials states no numeric patient-action point.
- `p3/grade-spelled-out/2` - scoped out: qualitative serial-CRP recommendation; its numeric monitoring interval is cited from narrative above.
- `p4/grade-spelled-out/1` - malformed bound extraction of the qualitative oral-transition recommendation; it states no numeric patient-action point.
- `p5/grade-spelled-out/1` - malformed bound extraction of the follow-up recommendation; its numeric 2-3-week interval is cited from narrative above.
- `p8/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative blood-culture recommendation.
- `p9/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative recommendation against procalcitonin measurement.
- `p14/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative plain-radiography recommendation.
- `p15/grade-spelled-out/1` - malformed bound extraction of the qualitative ultrasonography-first recommendation.
- `p15/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative MRI preference; the high-risk symptom-duration threshold is cited from narrative.
- `p19/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative arthrocentesis-before-therapy recommendation.
- `p19/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative joint-fluid testing recommendation.
- `p22/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative immediate empiric-therapy recommendation.
- `p25/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative S. aureus coverage recommendation.
- `p29/grade-spelled-out/1` - duplicate full-text occurrence of the recommendation against routine intra-articular antimicrobials.
- `p39/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative serial-CRP recommendation; the numeric monitoring interval is cited from narrative.
- `p40/grade-spelled-out/1` - qualitative oral-transition recommendation states no numeric patient-action point.
- `p45/grade-spelled-out/1` - malformed bound extraction of the duration recommendation; the complete 10-14-day and 21-28-day decision points are cited from the page's narrative text above.
