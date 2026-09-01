# New fever in the intensive care unit — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sccm-idsa-2023 | SCCM/IDSA | IDSA/society-of-critical-care-medicine-and-the-infectious | guideline | 2023 update | 2023-11 | https://doi.org/10.1097/CCM.0000000000006022 | stated | bound |

## Scope

**Read:** all 17 pages, including the abstract, population and exclusion boundaries,
methods, full 24-item consensus table, fever definitions, temperature measurement,
device calibration and route-specific feasibility, antipyretic treatment, imaging and
POCUS, catheter and peripheral blood cultures and catheter-hub safeguards, urine culture,
viral testing and panel/specimen limitations, SARS-CoV-2 testing, rapid biomarkers,
sepsis/septic-shock provenance, antimicrobial-start and discontinuation safeguards,
conclusions, disclosures, and references.

**Not read:** nothing in the source page range. The reference-only pages are exempt
from decision-point extraction as recorded below.

**Scoped out under ADR 0009's decision-point rule:** epidemiologic prevalence,
diagnostic sensitivity and specificity, pooled effect estimates, confidence intervals,
study sizes, evidence-search dates, recommendation-development voting thresholds,
device engineering details, author metadata, funding identifiers, and reference-list
numbers that do not change an evaluation, test, treatment, or observation decision.
Study assay performance and trial timing are not patient-care cutoffs unless the
guideline separately adopts them as an action boundary.

| span | pages | read |
| --- | --- | --- |
| abstract, rationale, scope, populations, and noninfectious differential | 1-2 | yes |
| methods and GRADE process | 3 | read 2026-09-01; blind 2026-09-01 |
| consensus recommendations and fever definition | 4-5 | yes |
| temperature measurement, antipyretics, and imaging | 6-8 | yes |
| blood cultures, urine cultures, and respiratory testing | 9-10 | yes |
| viral testing, SARS-CoV-2 testing, biomarkers, and antimicrobial boundaries | 11-13 | yes |
| article information and disclosures | 13 | read 2026-09-01; blind 2026-09-01 |
| references | 13-17 | exempt: reference list has no additional patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adult-icu-new-fever | adult ICU patients with new-onset fever without severe immunocompromise |
| adult-icu-suspected-infection | ICU patients with suspected infection regardless of the presence of temperature elevation |
| obvious-noninfectious-fever | ICU patients whose fever has an obvious noninfectious etiology, such as fever immediately after surgery |
| severely-immunocompromised-icu | organ transplant recipients, patients with severe neutropenia, and other severely immunocompromised ICU patients |
| adult-icu-fever | critically ill adult ICU patients with fever |
| adult-icu-fever-comfort-priority | critically ill patients with fever who value comfort from reducing temperature |
| neuroinjury-or-post-cardiac-arrest-fever | febrile patients with neurologic injury or after cardiac arrest |
| central-temperature-device-or-critical-accuracy | ICU patients with a pulmonary artery catheter, bladder catheter, or esophageal balloon thermistor in place, or for whom accurate temperature measurement is critical to diagnosis and management |
| no-central-temperature-device | ICU patients without a pulmonary artery catheter, bladder catheter, or esophageal balloon thermistor in place |
| alert-cooperative-temperature-patient | alert and cooperative ICU patients in whom oral temperature measurement is feasible |
| hospital-acquired-infection-fever-definition | patients assessed under the source-printed CDC hospital-acquired-infection fever definition |
| older-long-term-care-fever-definition | persons older than 65 years residing in long-term care facilities under the source-printed IDSA definition |
| chemotherapy-neutropenia-fever-definition | patients with neutropenia due to chemotherapy under the source-printed IDSA and NCCN definition |
| fever-during-icu-stay | patients who develop fever during an ICU stay |
| fever-clear-alternative-source-or-better-chest-imaging | febrile ICU patients with a clear alternative source or with higher-quality chest imaging available |
| recent-thoracic-abdominal-pelvic-surgery-fever | febrile patients who recently underwent thoracic, abdominal, or pelvic surgery and whose initial workup has not readily identified an etiology |
| postoperative-fever-several-days | surgical ICU patients whose fever first occurs several days after surgery without an alternative cause |
| fever-workup-negative-transport-acceptable | critically ill patients with fever whose other diagnostic tests failed to establish an etiology and whose transport risk is acceptable |
| fever-no-established-etiology | febrile ICU patients without an established etiology |
| fever-no-abdominal-findings-or-recent-surgery | critically ill patients with fever, no abdominal signs or symptoms, no liver-function abnormalities, and no recent abdominal surgery |
| fever-abdominal-source-risk | patients with fever and recent abdominal surgery, abdominal symptoms, or suspicion of an abdominal source |
| fever-abnormal-chest-radiograph-expertise | critically ill patients with fever, an abnormal chest radiograph, and available thoracic-ultrasound expertise |
| fever-no-chest-radiograph-abnormality | patients with fever without chest-radiograph abnormalities |
| immunocompromised-pulmonary-disease-concern | immunocompromised patients in whom pulmonary parenchymal disease must be excluded |
| fever-no-source-central-catheter | ICU patients with fever without an obvious source who have a central venous catheter |
| central-catheter-cultures-indicated | febrile ICU patients in whom central venous catheter cultures are indicated |
| new-fever-unclear-origin-rapid-blood-test | critically ill patients with new fever of unclear origin for whom a rapid molecular blood test is performed |
| adult-icu-blood-culture | adult ICU patients in whom blood cultures are performed |
| sepsis-antimicrobials-indicated | febrile ICU patients with sepsis for whom antimicrobial therapy is indicated |
| febrile-pyuria-suspected-uti | febrile ICU patients with pyuria and suspected urinary tract infection |
| catheterized-unable-report-urinary-symptoms | catheterized ICU patients unable to report urinary symptoms, without another obvious source, and with suspicion of infection |
| asymptomatic-bacteriuria-context | ICU patients with asymptomatic bacteriuria |
| new-fever-pneumonia-or-upper-respiratory-symptoms | critically ill patients with new fever and suspected pneumonia or new upper respiratory symptoms such as cough |
| pneumonia-respiratory-sampling | critically ill patients being evaluated for pneumonia |
| immunocompetent-icu-routine-blood-virus-testing | immunocompetent ICU patients considered for routine blood testing for viral pathogens such as herpesviruses or adenovirus |
| new-fever-community-sars-cov-2-risk | critically ill patients with new fever whose SARS-CoV-2 testing decision is informed by community transmission |
| negative-upper-sars-cov-2-lower-infection-suspected | patients with a negative upper respiratory SARS-CoV-2 NAAT and suspected lower respiratory tract COVID-19 |
| low-intermediate-bacterial-probability-no-focus | critically ill patients with new fever, no clear infection focus, and low-to-intermediate probability of bacterial infection |
| high-bacterial-probability-no-focus | critically ill patients with new fever, no clear infection focus, and high probability of bacterial infection |
| stable-icu-suspected-sepsis-on-antibiotics | stabilized ICU patients with suspected sepsis who are receiving antibiotics |
| biomarker-guided-antimicrobial-decision | critically ill patients whose antimicrobial initiation, alteration, or discontinuation is being considered with PCT or CRP results |
| any-icu-temperature-measurement | ICU patients whose temperature is measured with any device |
| rectal-temperature-considered | ICU patients without central temperature monitoring in whom rectal measurement is considered |
| critically-ill-oral-temperature | critically ill patients in whom oral temperature measurement is considered |
| febrile-icu-immunocompromised-ct-context | febrile ICU patients whose immunocompromised state may support CT imaging |
| febrile-icu-plain-radiograph-followup | febrile ICU patients with a plain-radiography abnormality requiring specific follow-up |
| critically-ill-pocus-available | critically ill patients when point-of-care ultrasound is available |
| central-catheter-blood-culture-collection | ICU patients undergoing blood-culture collection through a central venous catheter |
| nosocomial-viral-acquisition-concern | hospitalized ICU patients with concern for nosocomial viral acquisition based on local epidemiology |
| nosocomial-covid-acquisition-concern | hospitalized ICU patients with concern for nosocomial COVID-19 acquisition |
| respiratory-viral-panel-result-context | febrile ICU patients whose respiratory viral NAAT panel is being selected or interpreted |
| immunocompetent-icu-asymptomatic-cmv-reactivation | immunocompetent ICU patients with asymptomatic CMV reactivation |
| bacterial-exposure-context | patients after bacterial exposure whose PCT kinetics are being interpreted |
| healthy-persons-pct-reference | healthy persons whose normal PCT reference is being described |
| acute-inflammatory-or-infectious-insult | patients after an acute inflammatory or infectious insult whose CRP kinetics are being interpreted |
| healthy-or-reference-crp-context | persons whose typical CRP reference values are being described |
| severe-viral-illness | patients with severe viral illness, including influenza or COVID-19 |
| crp-altering-host-or-medication | patients with neutropenia or immunodeficiency or who use nonsteroidal anti-inflammatory drugs |
| sepsis-or-septic-shock | patients with sepsis or septic shock addressed by source-described major guidelines |
| icu-suspected-sepsis | ICU patients with suspected sepsis before initial antimicrobial therapy |

## Quantities

| key | verbatim |
| --- | --- |
| guideline-population | population directly addressed by the guideline |
| investigation-necessity | when new fever requires investigation |
| diagnostic-study-targeting | source-directed rather than reflex diagnostic testing |
| legacy-guideline-boundary | status of 2008 recommendations not specifically updated |
| icu-fever-definition | SCCM/IDSA fever threshold used by this guideline |
| cdc-hai-fever-definition | source-printed CDC hospital-acquired-infection fever threshold |
| idsa-long-term-care-fever-definition | source-printed IDSA fever thresholds for older long-term-care residents |
| idsa-nccn-neutropenia-fever-definition | source-printed IDSA and NCCN fever thresholds for chemotherapy-associated neutropenia |
| infection-without-fever-boundary | application when suspected infection is afebrile |
| temperature-measurement-selection | temperature method chosen by device status and required accuracy |
| oral-temperature-feasibility | oral measurement feasibility limitations |
| routine-antipyretic-use | routine fever reduction with antipyretic medication |
| comfort-directed-fever-reduction | fever-reduction method when comfort is prioritized |
| neurocritical-antipyretic-boundary | antipyretic evidence boundary for neurologic injury or post-cardiac-arrest fever |
| initial-chest-imaging | chest imaging during ICU-acquired fever |
| postoperative-ct-escalation | CT escalation after recent thoracic, abdominal, or pelvic surgery |
| postoperative-ct-timing | timing and collaboration boundary for postoperative CT |
| fdg-pet-ct-escalation | nuclear imaging after unrevealing diagnostic testing |
| wbc-scan-position | WBC scan evidence boundary |
| abdominal-ultrasound-initial-use | abdominal ultrasound selection by abdominal findings and surgery |
| thoracic-ultrasound-use | bedside thoracic ultrasound selection by radiograph and expertise |
| immunocompromised-thoracic-imaging | preferred thoracic imaging in immunocompromised patients |
| catheter-peripheral-blood-culture-pairing | paired catheter and peripheral blood-culture collection |
| differential-time-to-positivity | differential time supporting catheter-associated bacteremia |
| catheter-lumen-minimum | minimum catheter lumens sampled |
| catheter-all-lumen-sampling | separate culture of all catheter lumens |
| rapid-blood-molecular-test | relationship between rapid molecular blood testing and cultures |
| blood-culture-set-count | minimum number and sequence of blood-culture sets |
| blood-culture-total-volume | ideal total blood volume |
| blood-culture-bottle-volume | proper fill volume per blood-culture bottle |
| blood-culture-bottle-composition | minimum bottle composition per set |
| blood-culture-site | preferred anatomical collection approach |
| sepsis-culture-delay | maximum culture-related antimicrobial delay |
| single-set-contaminant-interpretation | interpretation of a common contaminant in one set |
| uti-pyuria-definition | urine WBC threshold used to justify culture |
| catheterized-uti-culture | catheter replacement and urine-culture sequence |
| asymptomatic-bacteriuria-harm | antibiotic-overuse and misdiagnosis boundary |
| respiratory-viral-naat | viral test selection for pneumonia or upper respiratory symptoms |
| pneumonia-bacterial-sampling | bacterial sampling assumed during pneumonia evaluation |
| respiratory-viral-specimen | upper versus lower respiratory viral specimen selection |
| routine-blood-viral-testing | routine blood viral-testing position in immunocompetent ICU patients |
| immunocompetent-cmv-treatment | CMV-treatment evidence boundary in immunocompetent ICU patients |
| sars-cov-2-testing | SARS-CoV-2 PCR selection by community transmission |
| sars-cov-2-lower-respiratory-escalation | lower respiratory specimen after a negative upper specimen |
| sars-cov-2-upper-respiratory-specimen | upper respiratory NAAT specimen choices for SARS-CoV-2 |
| pct-adjunctive-diagnosis | PCT use by bacterial-infection probability |
| crp-adjunctive-diagnosis | CRP use by bacterial-infection probability |
| biomarker-ruleout-selection | PCT or CRP use to help rule out bacterial infection |
| pct-kinetics | PCT rise and peak timing after bacterial exposure |
| pct-healthy-reference | PCT value in healthy persons |
| crp-kinetics | CRP rise and peak timing after an inflammatory or infectious insult |
| crp-reference-cutoff | CRP reference value and typical cutoff |
| pct-viral-limitation | severe viral illness limitation on PCT interpretation |
| crp-host-medication-limitation | neutropenia, immunodeficiency, and NSAID limitations on CRP interpretation |
| initial-antimicrobial-withholding | whether PCT may justify withholding initial antibiotics |
| pct-antibiotic-discontinuation | stabilized-patient PCT discontinuation criteria |
| biomarker-only-antimicrobial-decision | prohibition on biomarker-only antimicrobial decisions |
| culture-contamination-harm | harms of catheter-drawn or contaminated blood cultures |
| imaging-transport-harm | transport risk during advanced imaging |
| temperature-device-calibration-maintenance | calibration and maintenance prerequisite for temperature devices |
| rectal-temperature-practicality | ICU practicality limitation of rectal measurement |
| oral-temperature-critical-illness-limitations | intubation, cooperation, mouth-breathing, fluid, and gas limitations of oral measurement |
| ct-host-followup-indications | evidence-qualified CT host-factor and plain-radiography follow-up indications |
| pocus-adjunct-availability | POCUS as an available adjunct to physical examination |
| catheter-hub-antiseptic-cap | antiseptic barrier-cap contamination safeguard |
| catheter-connector-safeguard | old-connector removal or new-connector contamination safeguard |
| nosocomial-viral-testing-timing | viral-testing timing when local epidemiology suggests nosocomial acquisition |
| nosocomial-covid-testing-timing | COVID-19-testing timing when nosocomial acquisition is a concern |
| respiratory-viral-panel-boundaries | organisms omitted from panels and noncontributory detections |
| sepsis-biomarker-routine-use | major-guideline position on routine biomarkers in sepsis and septic shock |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| guideline-population | adult-icu-new-fever | applies to adult ICU patients with new-onset fever without severe immunocompromise | new-onset fever in adult ICU patients without severe immunocompromise | sccm-idsa-2023 | 1 | p1/narrative/guideline-population | narrative |
| guideline-population | severely-immunocompromised-icu | not directly addressed; recommendations may sometimes apply but the guideline does not establish that applicability | these populations are not directly addressed here | sccm-idsa-2023 | 2 | p2/narrative/severe-immunocompromise-exclusion | narrative |
| investigation-necessity | obvious-noninfectious-fever | investigation is not required for every febrile episode when a noninfectious cause is obvious | not all febrile episodes dictate a need for investigation | sccm-idsa-2023 | 2 | p2/narrative/obvious-noninfectious-fever | narrative |
| diagnostic-study-targeting | adult-icu-new-fever | use history and physical examination to identify potential sources, then target diagnostic studies rather than reflexively culturing all possible sources | RENDERED: Diagnostic studies should then be sent with those potential sources in focus rather than reflexively sending cultures for all possible sources. | sccm-idsa-2023 | 2 | p2/narrative/targeted-diagnostic-studies | narrative |
| legacy-guideline-boundary | adult-icu-new-fever | SOURCE-PRINTED RELATED: any 2008 recommendation not specifically addressed in this update remains in place; this sheet does not import unstated legacy thresholds | RENDERED: Any recommendation from the 2008 guideline not specifically addressed in this update remains in place. | sccm-idsa-2023 | 2 | p2/narrative/legacy-2008-boundary | narrative |
| icu-fever-definition | adult-icu-new-fever | a single temperature >=38.3 degrees C defines fever for this guideline | a single temperature measurement greater than or equal to 38.3°C | sccm-idsa-2023 | 5 | p5/narrative/icu-fever-definition | narrative |
| cdc-hai-fever-definition | hospital-acquired-infection-fever-definition | SOURCE-PRINTED EXTERNAL CDC: measured temperature >38 degrees C | a measured temperature of greater than 38°C | sccm-idsa-2023 | 5 | p5/narrative/cdc-hai-fever-definition | narrative |
| idsa-long-term-care-fever-definition | older-long-term-care-fever-definition | SOURCE-PRINTED EXTERNAL IDSA: single oral >37.8 degrees C, repeated oral >37.2 degrees C, repeated rectal >37.5 degrees C, or rise from baseline >1.1 degrees C | RENDERED: a single oral temperature greater than 37.8°C, repeated temperature measurements greater than 37.2°C (oral) or greater than 37.5°C (rectal), or an increase from baseline greater than 1.1°C | sccm-idsa-2023 | 5 | p5/narrative/idsa-long-term-care-fever-definition | narrative |
| idsa-nccn-neutropenia-fever-definition | chemotherapy-neutropenia-fever-definition | SOURCE-PRINTED EXTERNAL IDSA/NCCN: single oral >=38.3 degrees C or oral >38.0 degrees C sustained for >=1 hour | a single oral temperature measurement greater than or equal to 38.3°C or greater than 38.0°C sustained over at least 1 hour | sccm-idsa-2023 | 5 | p5/narrative/idsa-nccn-neutropenia-fever-definition | narrative |
| infection-without-fever-boundary | adult-icu-suspected-infection | evaluation recommendations may apply when infection is suspected even without temperature elevation | RENDERED: suspected infection regardless of the presence of temperature elevation | sccm-idsa-2023 | 5 | p5/narrative/infection-without-fever | narrative |
| temperature-measurement-selection | central-temperature-device-or-critical-accuracy | prefer pulmonary-artery, bladder-catheter, or esophageal-balloon thermistors | RENDERED: Central temperature monitoring methods, including thermistors for pulmonary artery catheters, bladder catheters, or esophageal balloon thermistors, are preferred | sccm-idsa-2023 | 5 | p5/narrative/central-temperature-preferred | narrative |
| temperature-measurement-selection | no-central-temperature-device | prefer oral or rectal measurement over axillary, tympanic-membrane, temporal-artery, or chemical-dot methods | we suggest using oral or rectal temperatures over other temperature measurement methods that are less reliable | sccm-idsa-2023 | 5 | p5/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| temperature-device-calibration-maintenance | any-icu-temperature-measurement | calibrate and maintain every temperature device according to the manufacturer's specifications | RENDERED: all devices are calibrated and maintained according to manufacturers' specifications | sccm-idsa-2023 | 5 | p5/narrative/temperature-device-calibration | narrative |
| rectal-temperature-practicality | rectal-temperature-considered | EVIDENCE ONLY: rectal measurement can be used but is often impractical in the ICU | RENDERED: A rectal thermometer could be used but is often impractical in the ICU setting. | sccm-idsa-2023 | 6 | p6/narrative/rectal-temperature-practicality | narrative |
| oral-temperature-feasibility | alert-cooperative-temperature-patient | oral measurement is safe and convenient when the patient is alert and cooperative | RENDERED: Oral measurements are safe and convenient for alert and cooperative patients | sccm-idsa-2023 | 6 | p6/narrative/oral-temperature-feasibility | narrative |
| oral-temperature-critical-illness-limitations | critically-ill-oral-temperature | EVIDENCE ONLY: oral readings can be distorted by mouth breathing or hot or cold fluids or gases in or near the mouth and are often impractical with endotracheal intubation or inability to cooperate | RENDERED: distorted by mouth breathing or hot or cold fluids or gases in or near the mouth ... often impractical due to endotracheal intubation or the inability of the patient to cooperate | sccm-idsa-2023 | 6 | p6/narrative/oral-temperature-limitations | narrative |
| routine-antipyretic-use | adult-icu-fever | avoid routine antipyretic medication solely to reduce temperature | RENDERED: avoiding the routine use of antipyretic medications for the specific purpose of reducing the temperature | sccm-idsa-2023 | 6 | p6/grade-spelled-out/1 | weak recommendation, moderate-quality evidence |
| comfort-directed-fever-reduction | adult-icu-fever-comfort-priority | use antipyretic medication rather than nonpharmacologic temperature reduction | RENDERED: using antipyretic medications over nonpharmacologic methods to reduce body temperature | sccm-idsa-2023 | 6 | p6/grade-spelled-out/2 | weak recommendation, low-quality evidence |
| neurocritical-antipyretic-boundary | neuroinjury-or-post-cardiac-arrest-fever | EVIDENCE ONLY: theoretical benefit may exceed risk, but evidence does not support routine antipyretic use | RENDERED: the theoretical benefit of antipyretic therapy may outweigh the risk, but there is little evidence to support a recommendation for routine use of antipyretic medications in these populations. | sccm-idsa-2023 | 7 | p7/narrative/neurocritical-antipyretic-boundary | narrative |
| initial-chest-imaging | fever-during-icu-stay | perform a chest radiograph | RENDERED: For patients who develop fever during ICU stay, we recommend performing a chest radiograph. | sccm-idsa-2023 | 4 | p4/grade-spelled-out/4 | best-practice statement |
| initial-chest-imaging | fever-clear-alternative-source-or-better-chest-imaging | bedside chest radiography may be unnecessary when an alternative source is clear or higher-quality imaging is available | might not be indicated include those with a clear alternative source for fever, and those for whom higher quality chest imaging | sccm-idsa-2023 | 7 | p7/narrative/chest-radiograph-exception | narrative |
| postoperative-ct-escalation | recent-thoracic-abdominal-pelvic-surgery-fever | perform CT with the surgical service when initial workup does not readily identify an etiology | RENDERED: For patients who have recently undergone thoracic, abdominal, or pelvic surgery, we recommend performing CT (in collaboration with the surgical service) as part of a fever workup if an etiology is not readily identified by initial workup. | sccm-idsa-2023 | 4 | p4/grade-spelled-out/4 | best-practice statement |
| postoperative-ct-timing | postoperative-fever-several-days | consider CT of the operative area when fever first occurs several days after surgery and no alternative cause is readily identified; immediate-postoperative timing has insufficient data and the decision should be made with the surgical service | RENDERED: reasonable for surgical patients to undergo CT imaging of the operative area when fever first occurs several days after surgery and an alternative cause is not readily identified ... insufficient data regarding the timing ... in the immediate postoperative setting; this decision should be made in collaboration with the surgical services. | sccm-idsa-2023 | 7 | p7/narrative/postoperative-ct-timing | narrative |
| imaging-transport-harm | recent-thoracic-abdominal-pelvic-surgery-fever | consider patient stability and transport adverse-event risk before CT | Stability of the patient and risk of adverse events during transportation should be taken into consideration. | sccm-idsa-2023 | 7 | p7/narrative/ct-transport-risk | narrative |
| ct-host-followup-indications | febrile-icu-immunocompromised-ct-context | EVIDENCE ONLY: immunocompromised state may be a host-factor indication for CT in a febrile ICU patient | RENDERED: indications for CT imaging in febrile ICU patients may include host factors such as immunocompromised state | sccm-idsa-2023 | 7 | p7/narrative/ct-immunocompromised-host-factor | narrative |
| ct-host-followup-indications | febrile-icu-plain-radiograph-followup | EVIDENCE ONLY: specific follow-up of abnormalities on plain radiography may indicate CT | RENDERED: indications for CT imaging in febrile ICU patients may include ... specific follow-up of abnormalities on plain radiography | sccm-idsa-2023 | 7 | p7/narrative/ct-plain-radiography-followup | narrative |
| fdg-pet-ct-escalation | fever-workup-negative-transport-acceptable | suggest performing 18F-FDG PET/CT after other diagnostic testing fails, only when transport risk is acceptable | RENDERED: we suggest performing an 18F-fluorodeoxyglucose (18F-FDG) positron emission tomography (PET)/CT if the risk of transport is deemed acceptable | sccm-idsa-2023 | 7 | p7/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| wbc-scan-position | fever-no-established-etiology | insufficient evidence to recommend WBC scanning | RENDERED: The panel found insufficient evidence to issue a recommendation regarding the use of WBC scans for patients with fever without an established etiology. | sccm-idsa-2023 | 7 | p7/narrative/wbc-scan-insufficient | narrative |
| abdominal-ultrasound-initial-use | fever-no-abdominal-findings-or-recent-surgery | do not routinely use formal abdominal ultrasound or POCUS as the initial investigation | RENDERED: recommend against the routine use of a formal abdominal ultrasound or point-of-care ultrasound (POCUS) as an initial investigation | sccm-idsa-2023 | 4 | p4/grade-spelled-out/5 | best-practice statement |
| abdominal-ultrasound-initial-use | fever-abdominal-source-risk | perform formal bedside diagnostic abdominal ultrasound | RENDERED: recommend performing a formal bedside diagnostic ultrasound of the abdomen | sccm-idsa-2023 | 4 | p4/grade-spelled-out/5 | best-practice statement |
| pocus-adjunct-availability | critically-ill-pocus-available | use POCUS when available to complement the physical examination | RENDERED: POCUS in critical care settings is a useful tool to further complement the physical examination, and its use is recommended when available. | sccm-idsa-2023 | 7 | p7/narrative/pocus-adjunct | narrative |
| thoracic-ultrasound-use | fever-abnormal-chest-radiograph-expertise | perform bedside thoracic ultrasound to identify pleural effusions and parenchymal or interstitial pathology | RENDERED: performing a thoracic bedside ultrasound when sufficient expertise is available | sccm-idsa-2023 | 8 | p8/grade-spelled-out/1 | weak recommendation, low-quality evidence |
| thoracic-ultrasound-use | fever-no-chest-radiograph-abnormality | insufficient evidence for a recommendation; use may be considered only case by case | RENDERED: Insufficient evidence was found to issue a recommendation regarding the use of thoracic bedside ultrasound for patients with fever without chest radiograph abnormalities ... its use could be considered on case-by-case basis. | sccm-idsa-2023 | 4 | p4/grade-spelled-out/6 | insufficient evidence; no recommendation |
| immunocompromised-thoracic-imaging | immunocompromised-pulmonary-disease-concern | lung ultrasound may not exclude parenchymal disease; prefer CT | LUS may be insufficient to rule out pulmonary parenchymal disease, and CT imaging is preferable. | sccm-idsa-2023 | 8 | p8/narrative/immunocompromised-thoracic-imaging | narrative |
| catheter-peripheral-blood-culture-pairing | fever-no-source-central-catheter | collect catheter and peripheral blood cultures simultaneously to calculate differential time to positivity | RENDERED: simultaneous collection of central venous catheter and peripherally drawn blood cultures | sccm-idsa-2023 | 4 | p4/grade-spelled-out/6 | best-practice statement |
| differential-time-to-positivity | fever-no-source-central-catheter | catheter culture positive at least two hours before the same organism in the peripheral culture supports catheter-associated bacteremia | positive two or more hours earlier than the peripheral specimen | sccm-idsa-2023 | 9 | p9/narrative/differential-time-positivity | narrative |
| catheter-lumen-minimum | central-catheter-cultures-indicated | sample at least two lumens | RENDERED: recommend sampling at least two lumens | sccm-idsa-2023 | 4 | p4/grade-spelled-out/6 | best-practice statement |
| catheter-all-lumen-sampling | central-catheter-cultures-indicated | EVIDENCE ONLY: collect separately through every lumen to reduce missed bacteremia | RENDERED: blood cultures should be collected through all catheter lumens ... failure to separately collect blood from each lumen may lead to missed detection of bacteremia | sccm-idsa-2023 | 9 | p9/narrative/catheter-all-lumens | narrative |
| culture-contamination-harm | fever-no-source-central-catheter | avoid routine catheter-drawn cultures except for the paired diagnostic strategy because catheter cultures contaminate more often and contaminated results may drive unnecessary antibiotics and divert attention from the actual fever source | RENDERED: collection of blood cultures through central venous catheters should be avoided ... higher rates of contamination ... potentially leading to overuse of antibiotics and drawing healthcare teams' attention away from actual causes of fever | sccm-idsa-2023 | 9 | p9/narrative/catheter-culture-contamination | narrative |
| catheter-hub-antiseptic-cap | central-catheter-blood-culture-collection | use antiseptic barrier caps on central venous catheter hubs to reduce contamination | RENDERED: Strategies to reduce the higher contamination rates from catheter blood cultures include use of antiseptic barrier caps on central venous catheter hubs | sccm-idsa-2023 | 9 | p9/narrative/catheter-antiseptic-caps | narrative |
| catheter-connector-safeguard | central-catheter-blood-culture-collection | obtain cultures only after removing the old needleless connector or through a new connector | RENDERED: only obtaining cultures after the removal of the old needleless connector or through a new connector | sccm-idsa-2023 | 9 | p9/narrative/catheter-connector-safeguard | narrative |
| rapid-blood-molecular-test | new-fever-unclear-origin-rapid-blood-test | use rapid molecular blood tests only together with blood cultures | they should only be used with concomitant blood cultures | sccm-idsa-2023 | 9 | p9/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| blood-culture-set-count | adult-icu-blood-culture | collect at least two sets sequentially from different anatomical sites without a purposeful interval | RENDERED: collecting at least two sets of blood cultures (ideally 60 mL of blood total), from different anatomical sites, without a time interval between them | sccm-idsa-2023 | 4 | p4/grade-spelled-out/7 | best-practice statement |
| blood-culture-total-volume | adult-icu-blood-culture | ideally collect 60 mL total | ideally 60 mL of blood total | sccm-idsa-2023 | 9 | p9/narrative/blood-culture-total-volume | narrative |
| blood-culture-bottle-volume | adult-icu-blood-culture | fill each bottle with 10 mL | Proper filling of blood culture bottles (10 mL per bottle) is important | sccm-idsa-2023 | 10 | p10/narrative/blood-culture-bottle-volume | narrative |
| blood-culture-bottle-composition | adult-icu-blood-culture | include at least one aerobic and one anaerobic bottle per set | At a minimum, an aerobic and anaerobic bottle should be included in each set | sccm-idsa-2023 | 10 | p10/narrative/blood-culture-bottles | narrative |
| blood-culture-site | adult-icu-blood-culture | prefer peripheral venipuncture with appropriate skin preparation; a dedicated venipuncture team may reduce contamination | RENDERED: properly collected, ideally via peripheral venipuncture, with appropriate skin preparation and preferably by a dedicated venipuncture team | sccm-idsa-2023 | 10 | p10/narrative/blood-culture-site | narrative |
| sepsis-culture-delay | sepsis-antimicrobials-indicated | blood-culture collection should not substantially delay indicated antimicrobials; keep the delay <45 minutes in patients with sepsis | RENDERED: should not substantially delay (i.e., < 45 min in patients with sepsis) the start of antimicrobial therapy | sccm-idsa-2023 | 10 | p10/narrative/sepsis-culture-delay | narrative |
| single-set-contaminant-interpretation | adult-icu-blood-culture | contamination is likely when only a single set grows a common contaminant such as S. epidermidis | RENDERED: Contamination is likely if only a single blood culture set is positive for a microorganism that is a common contaminant (e.g., Staphylococcus epidermidis). | sccm-idsa-2023 | 10 | p10/narrative/single-set-contaminant | narrative |
| uti-pyuria-definition | febrile-pyuria-suspected-uti | pyuria means 5-10 WBC/hpf and, with suspected UTI, justifies urine culture | RENDERED: pyuria (defined as 5-10 WBC/hpf) on urinalysis should be used to justify urine culture | sccm-idsa-2023 | 10 | p10/narrative/uti-pyuria-definition | narrative |
| catheterized-uti-culture | febrile-pyuria-suspected-uti | replace the urinary catheter and culture urine from the newly placed catheter | RENDERED: replacing the urinary catheter and obtaining urine cultures from the newly placed catheter | sccm-idsa-2023 | 4 | p4/grade-spelled-out/7 | best-practice statement |
| catheterized-uti-culture | catheterized-unable-report-urinary-symptoms | replace the catheter, send urinalysis from the new catheter, and culture only if WBCs are present | A urinalysis should be sent from a newly placed catheter and if WBCs are present, a urine culture should then be obtained | sccm-idsa-2023 | 10 | p10/narrative/catheterized-unable-symptoms | narrative |
| asymptomatic-bacteriuria-harm | asymptomatic-bacteriuria-context | a positive culture may drive antibiotic overuse, distract from the true fever source, and create a false CAUTI diagnosis | RENDERED: positive urine cultures may lead to overuse of antibiotics and draw healthcare teams away from actual causes of fever ... asymptomatic bacteriuria may result in false diagnoses of catheter-associated urinary tract infection (CAUTI) | sccm-idsa-2023 | 10 | p10/narrative/asymptomatic-bacteriuria-harm | narrative |
| respiratory-viral-naat | new-fever-pneumonia-or-upper-respiratory-symptoms | test with a viral NAAT panel | testing for viral pathogens using viral NAAT panels | sccm-idsa-2023 | 10 | p10/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| nosocomial-viral-testing-timing | nosocomial-viral-acquisition-concern | viral testing should be considered at any time during hospitalization when local epidemiology raises concern for nosocomial acquisition | RENDERED: If there is concern about nosocomial acquisition based on local epidemiology, viral testing should be considered at any time during a patient's hospitalization. | sccm-idsa-2023 | 10 | p10/narrative/nosocomial-viral-testing | narrative |
| pneumonia-bacterial-sampling | pneumonia-respiratory-sampling | EVIDENCE ONLY: in patients with pneumonia, the guideline assumes deep tracheal aspirates will be sent for bacterial stains and culture | RENDERED: In patients with pneumonia, it is assumed that deep tracheal aspirates will be sent for bacterial stains and culture. | sccm-idsa-2023 | 10 | p10/narrative/pneumonia-bacterial-sampling | narrative |
| respiratory-viral-specimen | pneumonia-respiratory-sampling | EVIDENCE ONLY: upper respiratory sampling is sufficient for most cases, but influenza or SARS-CoV-2 may sometimes be detected only in lower respiratory samples such as bronchoalveolar lavage or endotracheal-tube aspirate | RENDERED: Upper respiratory tract sampling is sufficient for most cases, but in some instances, viruses such as influenza viruses and SARS-CoV-2 may only be detected in lower respiratory tract samples, such as those obtained by bronchoalveolar lavage or endotracheal tube aspirate. | sccm-idsa-2023 | 10 | p10/narrative/respiratory-viral-specimen | narrative |
| respiratory-viral-panel-boundaries | respiratory-viral-panel-result-context | panel composition varies; not every potential pneumonia cause is included, and a detected virus may be present but noncontributory to the illness | RENDERED: specific panel compositions vary ... not all potential causes of pneumonia are encompassed by such panels ... possible to detect viruses in a febrile ICU patient that are present but are noncontributory to patient's illness | sccm-idsa-2023 | 11 | p11/narrative/respiratory-panel-boundaries | narrative |
| routine-blood-viral-testing | immunocompetent-icu-routine-blood-virus-testing | insufficient evidence; no recommendation for routine blood viral testing | RENDERED: There was insufficient evidence to allow a recommendation on performing routine blood testing for viral pathogens in immunocompetent patients in the ICU. | sccm-idsa-2023 | 5 | p5/grade-spelled-out/2 | insufficient evidence; no recommendation |
| routine-blood-viral-testing | immunocompetent-icu-routine-blood-virus-testing | do not routinely test blood by NAAT for herpesviruses or adenovirus because testing is generally not indicated | blood testing for these viruses with NAATs is not indicated | sccm-idsa-2023 | 11 | p11/narrative/routine-blood-virus-not-indicated | narrative |
| immunocompetent-cmv-treatment | immunocompetent-icu-asymptomatic-cmv-reactivation | EVIDENCE ONLY: asymptomatic CMV reactivation is increasingly recognized, but treatment for CMV in this population does not improve outcomes | RENDERED: although asymptomatic CMV reactivation in immunocompetent ICU patients is increasingly recognized, treatment for CMV in this population does not improve outcomes. | sccm-idsa-2023 | 11 | p11/narrative/immunocompetent-cmv-treatment | narrative |
| sars-cov-2-testing | new-fever-community-sars-cov-2-risk | test for SARS-CoV-2 by PCR based on community-transmission levels | RENDERED: For critically ill patients with a new fever, we recommend testing for severe acute respiratory syndrome coronavirus 2 by PCR based on levels of community transmission. | sccm-idsa-2023 | 5 | p5/grade-spelled-out/2 | best-practice statement |
| nosocomial-covid-testing-timing | nosocomial-covid-acquisition-concern | COVID-19 testing should be considered at any time during hospitalization because of nosocomial-acquisition concern | RENDERED: Because of the concern of nosocomial acquisition, COVID-19 testing should be considered at any time during a patient's hospitalization. | sccm-idsa-2023 | 11 | p11/narrative/nosocomial-covid-testing | narrative |
| sars-cov-2-upper-respiratory-specimen | new-fever-community-sars-cov-2-risk | upper-respiratory NAAT specimen options include nasopharyngeal, mid-turbinate, anterior nasal, saliva, or combined anterior nasal/oropharyngeal sampling | RENDERED: using a NAAT on a nasopharyngeal swab, mid-turbinate swab, anterior nasal swab, saliva, or a combined anterior nasal/oropharyngeal swab | sccm-idsa-2023 | 11 | p11/narrative/sars-cov-2-upper-options | narrative |
| sars-cov-2-lower-respiratory-escalation | negative-upper-sars-cov-2-lower-infection-suspected | lower respiratory secretions such as sputum, tracheal aspirate, or bronchoalveolar lavage fluid should be considered after a negative upper respiratory NAAT when lower respiratory COVID-19 remains suspected | RENDERED: if negative and a COVID-19 lower respiratory tract infection is suspected, lower respiratory secretions (e.g., sputum, tracheal aspirate, bronchoalveolar lavage fluid) should be considered | sccm-idsa-2023 | 11 | p11/narrative/sars-cov-2-lower-respiratory | narrative |
| pct-adjunctive-diagnosis | low-intermediate-bacterial-probability-no-focus | measure PCT in addition to bedside clinical evaluation | RENDERED: measuring procalcitonin (PCT) in addition to bedside clinical evaluation | sccm-idsa-2023 | 11 | p11/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| pct-adjunctive-diagnosis | high-bacterial-probability-no-focus | do not measure PCT to rule out bacterial infection | RENDERED: not measuring PCT to rule out bacterial infection | sccm-idsa-2023 | 11 | p11/grade-spelled-out/2 | weak recommendation, very low-quality evidence |
| crp-adjunctive-diagnosis | low-intermediate-bacterial-probability-no-focus | measure CRP in addition to bedside clinical evaluation | RENDERED: measuring C-reactive protein (CRP) in addition to bedside clinical evaluation | sccm-idsa-2023 | 11 | p11/grade-spelled-out/3 | weak recommendation, very low-quality evidence |
| crp-adjunctive-diagnosis | high-bacterial-probability-no-focus | do not measure CRP to rule out bacterial infection | RENDERED: not measuring CRP to rule out bacterial infection | sccm-idsa-2023 | 11 | p11/grade-spelled-out/4 | weak recommendation, very low-quality evidence |
| biomarker-ruleout-selection | low-intermediate-bacterial-probability-no-focus | measure either serum PCT or CRP to help rule out bacterial infection, always with clinical evaluation | RENDERED: measuring either serum PCT or CRP to rule out bacterial infection ... biomarkers ... used as adjuncts ... When used in conjunction with clinical assessment | sccm-idsa-2023 | 11 | p11/grade-spelled-out/5 | weak recommendation, very low-quality evidence |
| sepsis-biomarker-routine-use | sepsis-or-septic-shock | SOURCE-PRINTED RELATED: major guidelines recommend against routine biomarker use in sepsis and septic shock because benefit is uncertain and cost and availability are concerns | RENDERED: major guidelines recommend against routine use of biomarkers in the setting of sepsis and septic shock, out of respect for uncertain benefit and cost and availability issues | sccm-idsa-2023 | 12 | p12/narrative/major-guidelines-sepsis-biomarkers | narrative |
| pct-kinetics | bacterial-exposure-context | EVIDENCE ONLY: PCT begins rising about four hours after bacterial exposure and peaks after six to eight hours | RENDERED: PCT begins to rise four hours after exposure to bacteria, reaching a maximum level after six to eight hours | sccm-idsa-2023 | 12 | p12/narrative/pct-kinetics | narrative |
| pct-healthy-reference | healthy-persons-pct-reference | EVIDENCE ONLY: PCT is normally <0.05 ng/mL in healthy persons | RENDERED: PCT values in healthy individuals are less than 0.05 ng/mL. | sccm-idsa-2023 | 12 | p12/narrative/pct-healthy-reference | narrative |
| crp-kinetics | acute-inflammatory-or-infectious-insult | EVIDENCE ONLY: CRP rises 12-24 hours after an inflammatory or infectious insult and peaks after 48 hours | RENDERED: CRP levels start to rise 12-24 hours after an acute inflammatory or infectious insult, reaching a maximum value after 48 hours. | sccm-idsa-2023 | 12 | p12/narrative/crp-kinetics | narrative |
| crp-reference-cutoff | healthy-or-reference-crp-context | EVIDENCE ONLY: CRP is typically <5 mg/L and the typical cutoff is 10 mg/L | RENDERED: Levels of CRP are typically below 5 mg/L and the typical cutoff for CRP is 10 mg/L. | sccm-idsa-2023 | 12 | p12/narrative/crp-cutoff | narrative |
| pct-viral-limitation | severe-viral-illness | severe viral illness, including influenza and COVID-19, may elevate PCT and weaken bacterial discrimination | RENDERED: PCT may be elevated during severe viral illness including influenza and COVID-19, potentially making the discriminating power for predicting the causative microorganisms less useful | sccm-idsa-2023 | 12 | p12/narrative/pct-viral-limitation | narrative |
| crp-host-medication-limitation | crp-altering-host-or-medication | neutropenia, immunodeficiency, and NSAID use can affect CRP concentration | RENDERED: CRP concentrations can be affected by neutropenia, immunodeficiency, and the use of nonsteroidal anti-inflammatory drugs. | sccm-idsa-2023 | 12 | p12/narrative/crp-host-medication-limitation | narrative |
| initial-antimicrobial-withholding | icu-suspected-sepsis | do not initially withhold antibiotics based on PCT | RENDERED: In ICU patients with suspected sepsis, clinicians should not initially withhold antibiotics | sccm-idsa-2023 | 12 | p12/narrative/initial-antibiotic-withholding | narrative |
| pct-antibiotic-discontinuation | stable-icu-suspected-sepsis-on-antibiotics | PCT <0.5 micrograms/L or a decrease >=80% from peak may guide antibiotic discontinuation after stabilization | PCT levels of less than 0.5 µg/L or levels that decrease by greater than or equal to 80% from peak levels may guide antibiotic discontinuation once patients stabilize | sccm-idsa-2023 | 12 | p12/narrative/pct-antibiotic-discontinuation | narrative |
| biomarker-only-antimicrobial-decision | biomarker-guided-antimicrobial-decision | do not initiate, alter, or discontinue antimicrobial therapy solely from PCT or CRP changes | RENDERED: Decisions on initiating, altering, or discontinuing antimicrobial therapy should not be made solely based on changes in PCT or CRP levels. | sccm-idsa-2023 | 13 | p13/narrative/biomarker-only-decision | narrative |

## Conflicts

CONFLICT: routine-blood-viral-testing | immunocompetent-icu-routine-blood-virus-testing | `insufficient evidence; no recommendation for routine blood viral testing` versus `do not routinely test blood by NAAT for herpesviruses or adenovirus because testing is generally not indicated`; recommendation 18 says the evidence is insufficient to issue a recommendation, while its rationale gives a practical negative action for the same population. The sheet preserves both statements rather than converting the evidence gap into an unqualified recommendation.

The ICU fever threshold, CDC hospital-acquired-infection threshold, IDSA long-term-care
thresholds, and IDSA/NCCN neutropenia thresholds differ but apply to different defined
populations and settings; they are related provenance, not same-population conflicts.

The formal catheter recommendation requires sampling at least two lumens, while the
rationale describes separate sampling of all lumens as evidence to reduce missed
bacteremia. These are recorded under distinct minimum and complete-sampling quantities,
not treated as contradictory values.

The negative initial-investigation value for formal abdominal ultrasound or POCUS in
patients without abdominal findings or recent abdominal surgery is complementary to the
general use of available POCUS as an adjunct to physical examination; the latter does not
convert POCUS into a routine abdominal fever investigation. The abnormal-chest-radiograph
thoracic branch and no-abnormality case-by-case branch are likewise separately
population-keyed rather than conflicting.

The source-described major-guideline position against routine biomarkers in sepsis or
septic shock differs from this guideline's low-to-intermediate-probability, new-fever,
no-clear-focus adjunct branches. These are different populations and provenance, not a
license to use a healthy-person reference cutoff as an infection diagnosis.

## Coverage

The bound recommendation record contains **24 marker records**. It is an overinclusive
index rather than an exact recommendation denominator: several records concatenate
multiple Table 2 recommendations, several later records duplicate full-text occurrences,
and recommendations 7, 11, and 18 are insufficiency statements without clean standalone
marker records. The complete 17-page read therefore accounts against the document's
24-item consensus table, not against a claim that the bound record is exact. All 24
marker records are accounted as **17 cited + 7 disposed**; a concatenated marker may
support more than one source-faithful row.

Bound-record disposition:

- Cited directly from clean full-text occurrences: `p5/grade-spelled-out/1`,
  `p6/grade-spelled-out/1`, `p6/grade-spelled-out/2`, `p7/grade-spelled-out/1`,
  `p8/grade-spelled-out/1`, `p9/grade-spelled-out/1`,
  `p10/grade-spelled-out/1`, and `p11/grade-spelled-out/1` through
  `p11/grade-spelled-out/5`.
- Cited from source-rendered consensus-table occurrences to preserve best-practice or
  insufficiency provenance and class: `p4/grade-spelled-out/4` through
  `p4/grade-spelled-out/7` and `p5/grade-spelled-out/2`.
- `p4/grade-spelled-out/1` - summary-table marker window; the temperature action is cited from its clean full-text occurrence on page 5.
- `p4/grade-spelled-out/2` - concatenated summary-table window for recommendations 1 and 2; recommendation 2 is cited from page 6.
- `p4/grade-spelled-out/3` - concatenated summary-table window for recommendations 1 through 3; recommendations 2 and 3 are cited from page 6.
- `p5/grade-spelled-out/3` - concatenated summary-table window for recommendations 18 through 21; the same actions are retained or cited from page 11.
- `p5/grade-spelled-out/4` - concatenated summary-table window for recommendations 20 through 22; the three actions are cited from page 11.
- `p5/grade-spelled-out/5` - concatenated summary-table window for recommendations 21 through 23; the three actions are cited from page 11.
- `p5/grade-spelled-out/6` - concatenated summary-table window for recommendations 22 through 24; the three actions are cited from page 11.

ADR 0009 disposition:

- Retained all 24 consensus actions or insufficiency boundaries: temperature method;
  antipyretic use; chest radiograph; postoperative CT; FDG PET/CT; WBC-scan uncertainty;
  abdominal and thoracic ultrasound branches; catheter/peripheral cultures; catheter
  lumen sampling; rapid blood testing; blood-culture collection; catheterized urine
  culture; respiratory viral NAAT; routine blood-virus uncertainty; SARS-CoV-2 PCR;
  and probability-dependent PCT and CRP actions.
- Retained numeric patient-changing thresholds outside the recommendation list:
  setting-specific fever definitions, differential time to positivity >=2 hours,
  at least 2 blood-culture sets, ideal 60 mL total and 10 mL per bottle, at least one
  aerobic and one anaerobic bottle per set, sepsis culture delay <45 minutes, pyuria
  5-10 WBC/hpf, and stabilized-patient PCT discontinuation at <0.5 micrograms/L or a
  decrease >=80% from peak.
- Retained host, device, procedure, and observation branches: severe immunocompromise
  is outside direct scope; suspected infection may require evaluation without fever;
  obvious noninfectious fever need not trigger investigation; central devices govern
  temperature method, with calibration/maintenance and rectal/oral feasibility limits;
  recent surgery, abdominal findings, chest-radiograph findings,
  transport stability, catheter presence, urinary-catheter status, respiratory
  symptoms, community transmission, and bacterial-infection probability govern the
  next action.
- Retained evidence-qualified CT host and plain-radiography follow-up contexts, POCUS as
  an available examination adjunct, immediate-postoperative CT uncertainty with surgical
  collaboration, thoracic ultrasound case-by-case use, and catheter-hub antiseptic-cap
  and old/new connector safeguards.
- Retained nosocomial viral-testing timing, upper-respiratory SARS-CoV-2 NAAT specimen
  options and lower-respiratory escalation, the lower-respiratory influenza/SARS-CoV-2
  branch, respiratory-panel omissions and noncontributory detections, and the source's
  evidence-only assumptions for deep-tracheal bacterial sampling and asymptomatic CMV
  reactivation.
- Retained treatment safeguards and harms: routine antipyretics are discouraged unless
  comfort is prioritized; cultures must not materially delay indicated sepsis therapy;
  antibiotics are not initially withheld on PCT; PCT or CRP never acts alone; catheter
  contamination and asymptomatic bacteriuria can cause unnecessary antibiotics; and
  advanced imaging requires transport-risk assessment.
- Fever prevalence, normal-temperature drift, temperature-device agreement estimates,
  imaging and molecular-test accuracy, biomarker diagnostic performance, study drug
  effects, trial sizes and follow-up, publication years, author/funding data, and
  reference-list values were read but are evidence descriptors rather than additional
  patient-action thresholds. PCT/CRP kinetics and reference cutoffs are retained only
  as `EVIDENCE ONLY` interpretation context and not as stand-alone infection diagnoses.
  Their populations are source-faithful exposure, healthy-reference, acute-insult,
  severe-viral-illness, and host/medication contexts rather than the low-to-intermediate
  bacterial-probability action population. The source-described major-guideline position
  against routine biomarkers in sepsis and septic shock is retained as related provenance.
