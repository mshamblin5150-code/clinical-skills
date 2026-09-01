# Native vertebral osteomyelitis — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2015 | IDSA | IDSA/civ482 | guideline | 2015 guideline | 2015-07-29 | https://doi.org/10.1093/cid/civ482 | stated | bound |

## Scope

**Read:** all 21 pages, including the executive summary and recommendation list;
population, exclusions, definitions, methods, diagnostic and therapeutic evidence;
SPEP, tuberculosis and Brucella specimen handling, intravesical-BCG history, both
antimicrobial tables, operative biopsy and surgical branches, false-failure and premature-
imaging harms, follow-up and treatment-failure sections, research needs, article
information, disclosures, and references. The bound record contains 76 marker
occurrences. Its marker omissions warn rather than establish a complete recommendation
index, so the page read—not the marker record—defines this sweep.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's patient-action rule:** incidence and prevalence,
diagnostic-accuracy statistics, cohort enrollment and outcome rates, publication dates,
research questions, author metadata, and reference-list numbers unless the source uses a
value to change diagnostic testing, biopsy handling, antimicrobial choice or duration,
surgery, monitoring, or treatment-failure assessment.

| span | pages | read |
| --- | --- | --- |
| executive summary, 38 recommendations, population, exclusions, definitions | 1-5 | yes |
| methods, endorsement, and development process | 6 | read 2026-09-01; blind 2026-09-01 |
| diagnostic triggers, examination, cultures, laboratory tests, and imaging | 7-8 | yes |
| biopsy indications, withholding antibiotics, and specialized testing | 9-12 | yes |
| empiric therapy and parenteral organism-specific treatment table | 12-13 | yes |
| duration, oral treatment table, and surgical branches | 14-15 | yes |
| monitoring, failure definition, repeat imaging, sampling, and consultation | 15-17 | yes |
| research needs | 17-18 | read 2026-09-01; blind 2026-09-01 |
| article information and disclosures | 18 | read 2026-09-01; blind 2026-09-01 |
| references | 18-21 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-native-nvo | adults with native vertebral osteomyelitis |
| excluded-spinal-implant | patients with spinal implant-associated infection |
| excluded-postprocedure | patients with postprocedure spinal infection |
| excluded-epidural-only | patients with epidural abscess without associated native vertebral osteomyelitis |
| suspected-nvo | adults with suspected native vertebral osteomyelitis |
| new-back-neck-fever | patients with new or worsening back or neck pain and fever |
| new-back-neck-markers | patients with new or worsening back or neck pain and elevated ESR or CRP |
| new-back-neck-bloodstream | patients with new or worsening back or neck pain and bloodstream infection or infective endocarditis |
| fever-neurologic | patients with fever and new neurologic symptoms with or without back pain |
| recent-s-aureus-pain | patients with new localized neck or back pain after recent Staphylococcus aureus bloodstream infection |
| suspected-nvo-mri-unavailable | patients with suspected NVO when MRI cannot be obtained |
| subacute-brucella-risk | patients with subacute NVO residing in a brucellosis-endemic area |
| fungal-risk | patients with suspected NVO and epidemiologic or host risk for fungal infection |
| tuberculosis-risk | patients with subacute NVO originating or residing in a tuberculosis-endemic region or otherwise at risk |
| high-tuberculosis-suspicion | patients with NVO and high clinical suspicion for tuberculous infection despite PPD or interferon-gamma release assay results |
| significant-immunity-impairment | patients with significant impairment of immunity and clinical and radiographic evidence of NVO |
| biopsy-no-known-organism | patients with suspected NVO without S. aureus, S. lugdunensis, or Brucella established by blood culture or serology |
| known-associated-organism | patients with suspected NVO and S. aureus, S. lugdunensis, or Brucella bloodstream infection |
| endemic-positive-brucella | patients with suspected subacute NVO in a high-endemicity setting with strongly positive Brucella serology |
| low-endemic-brucella-serology | patients with suspected Brucella NVO in a low-endemicity setting such as the United States |
| other-organism-bloodstream | patients with suspected NVO and bloodstream infection due to an organism outside the named biopsy exceptions |
| sustained-skin-flora-bloodstream | chronic hemodialysis or intravascular-device patients with sustained coagulase-negative staphylococcal bloodstream infection |
| neuro-sepsis-urgent | patients with neurologic compromise with or without impending sepsis or hemodynamic instability |
| biopsy-special-risk | patients whose epidemiology, host factors, or radiologic clues suggest fungal, mycobacterial, or brucellar NVO |
| suspected-brucellar-nvo | patients with suspected brucellar NVO |
| culture-negative-specimen | patients whose aerobic and anaerobic biopsy cultures show no growth |
| insufficient-biopsy-specimen | patients whose biopsy specimen is insufficient for all contemplated studies |
| adequate-biopsy-tissue | patients from whom adequate tissue can be safely obtained |
| inconclusive-workup-biopsy | patients whose original NVO workup, including image-guided biopsy, remains inconclusive |
| first-biopsy-contaminant | patients without bloodstream infection whose first biopsy grew a skin contaminant |
| nondiagnostic-first-biopsy | patients with suspected NVO and a nondiagnostic first image-guided biopsy |
| decompression-surgery-indicated | patients requiring decompression for an epidural abscess or another neurologic complication |
| stable-neurologic-hemodynamic | patients with a normal stable neurologic examination and stable hemodynamics |
| unstable-or-progressive | patients with hemodynamic instability, sepsis, septic shock, or severe or progressive neurologic symptoms |
| bacterial-nvo | most patients with bacterial NVO |
| brucellar-nvo | most patients with NVO due to Brucella species |
| high-failure-risk | patients perceived to have high risk of failure, such as MRSA or extensive infection |
| surgical-neurologic-instability | patients with progressive neurologic deficits, progressive deformity, or spinal instability despite adequate antimicrobials |
| surgical-bloodstream-pain | patients with persistent or recurrent bloodstream infection without another source or worsening pain despite therapy |
| possible-cohort-surgical-indication | patients with neurologic compromise, significant vertebral destruction with instability, large epidural abscess formation, intractable back pain, or failure of medical treatment |
| intractable-back-pain | patients with intractable back pain |
| improving-worse-bone-image | patients with worsening bony imaging at 4-6 weeks but improving symptoms, examination, and inflammatory markers |
| treated-nvo | treated patients with NVO |
| favorable-response | patients with favorable clinical and laboratory response to antimicrobial therapy |
| poor-response | patients with poor clinical response to therapy |
| suspected-treatment-failure | patients with suspected NVO treatment failure |
| clinical-radiographic-failure | patients with clinical and radiographic evidence of treatment failure |
| oxacillin-susceptible-staphylococci | NVO caused by oxacillin-susceptible staphylococci |
| oxacillin-resistant-staphylococci | NVO caused by oxacillin-resistant staphylococci |
| penicillin-susceptible-enterococcus | NVO caused by penicillin-susceptible Enterococcus species |
| penicillin-resistant-enterococcus | NVO caused by penicillin-resistant Enterococcus species |
| vancomycin-resistant-enterococcus | NVO caused by vancomycin-resistant Enterococcus species |
| pseudomonas-nvo | NVO caused by Pseudomonas aeruginosa |
| enterobacteriaceae-nvo | NVO caused by Enterobacteriaceae |
| beta-hemolytic-streptococci | NVO caused by beta-hemolytic streptococci |
| propionibacterium-nvo | NVO caused by Propionibacterium acnes |
| salmonella-nvo | NVO caused by Salmonella species |
| bacteroides-anaerobic-nvo | NVO caused by Bacteroides or another susceptible anaerobe |
| oral-gram-negative-nvo | NVO caused by susceptible Enterobacteriaceae or another aerobic gram-negative organism |
| oral-resistant-staphylococci | oxacillin-resistant staphylococcal NVO when first-line agents cannot be used |
| brucella-oral-regimen | patients treated orally for brucellar NVO |

## Quantities

| key | verbatim |
| --- | --- |
| population-boundary | adult native-NVO population and excluded infection forms |
| diagnostic-trigger | clinical circumstance that should trigger suspicion for NVO |
| s-aureus-history-window | S. aureus bloodstream-infection history and aspiration boundary |
| diagnostic-examination | pertinent medical, motor, and sensory neurologic examination |
| initial-blood-labs | blood-culture set count and baseline inflammatory markers |
| initial-imaging | first-choice and alternate imaging |
| repeat-mri-window | repeat MRI after initially atypical imaging |
| radiograph-delay | delay before bone destruction appears on plain radiographs |
| imaging-interpretation | imaging modality use and result boundaries |
| tuberculosis-radiographic-trigger-pattern | radiographic patterns that should raise suspicion for tuberculous NVO |
| tuberculosis-comparative-mri-pattern | comparative MRI patterns of tuberculous NVO |
| brucella-blood-serology-testing | Brucella blood-culture and serologic testing action |
| brucella-incubation-titer | Brucella incubation and serologic-titer boundary |
| brucella-laboratory-alert | extended incubation and laboratory-safety alert |
| fungal-testing | fungal blood-culture action |
| tuberculosis-testing | PPD or interferon-gamma release assay action |
| tuberculosis-tissue-culture | mycobacterial tissue-culture action despite screening-test results |
| intravesical-bcg-history | intravesical BCG history elicitation |
| specialist-evaluation | infectious disease and spine-surgeon evaluation |
| spep-screening | serum protein electrophoresis after an inconclusive workup |
| initial-biopsy | initial image-guided aspiration-biopsy indication or exception |
| prebiopsy-antibiotic-hold | antibiotic-withholding duration and urgent exception |
| biopsy-special-cultures | specialized culture and nucleic-acid testing |
| repeat-biopsy-panel | tests to send on a repeat biopsy |
| insufficient-specimen-prioritization | epidemiologic prioritization when tissue is insufficient |
| biopsy-volume-evidence | aspirated-fluid volume associated with highest culture yield |
| biopsy-harms | image-guided aspiration-biopsy harm boundary |
| pathology-specimen | pathologic examination action |
| contaminant-repeat-biopsy | repeat biopsy after a skin-contaminant result |
| nondiagnostic-organism-exclusion | difficult-to-grow organism exclusion after a nondiagnostic biopsy |
| nondiagnostic-procedure-next-step | repeat-biopsy, PEDD, or open-biopsy branch |
| decompression-excisional-biopsy | excisional biopsy during indicated decompression |
| empiric-timing | timing of empiric antimicrobial therapy |
| empiric-coverage | organisms and example empiric regimens |
| empiric-avoidance | organism groups not routinely covered empirically |
| bacterial-duration | total therapy duration for bacterial NVO |
| brucella-duration | total therapy duration for Brucella NVO |
| high-risk-duration | evidence-limited extended-treatment practice |
| oral-switch-boundary | evidence-only early oral switch conditions |
| oral-beta-lactam-boundary | oral beta-lactam initial-treatment restriction |
| surgery-indication | operative and nonoperative decision branches |
| cohort-surgical-indication | cohort-derived surgical-indication context |
| failure-definition | findings that do or do not define treatment failure |
| false-failure-assignment-harm | harms of assigning failure without microbiologic evidence |
| inflammatory-monitoring-timing | ESR and CRP monitoring timing |
| inflammatory-marker-interpretation | ESR and CRP response and failure-risk interpretation |
| follow-up-imaging | routine or response-triggered follow-up MRI |
| premature-follow-up-imaging-harm | harms of premature follow-up imaging |
| failure-tissue-sampling | failure tissue-sampling action |
| failure-specialist-consultation | failure specialist-consultation action |
| oxacillin-susceptible-regimen | Table 2 regimen for oxacillin-susceptible staphylococci |
| oxacillin-resistant-regimen | Table 2 regimen for oxacillin-resistant staphylococci |
| penicillin-susceptible-enterococcus-regimen | Table 2 regimen for penicillin-susceptible Enterococcus |
| penicillin-resistant-enterococcus-regimen | Table 2 regimen for penicillin-resistant Enterococcus |
| vancomycin-resistant-enterococcus-options | Table 2 footnote options for vancomycin-resistant Enterococcus |
| pseudomonas-regimen | Table 2 regimen for Pseudomonas aeruginosa |
| enterobacteriaceae-regimen | Table 2 regimen for Enterobacteriaceae |
| beta-streptococci-regimen | Table 2 regimen for beta-hemolytic streptococci |
| propionibacterium-regimen | Table 2 regimen for Propionibacterium acnes |
| salmonella-regimen | Table 2 regimen for Salmonella species |
| antimicrobial-adjustment | renal, hepatic, susceptibility, allergy, interaction, and monitoring boundary |
| flucloxacillin-option | European oxacillin-susceptible staphylococcal option |
| vancomycin-allergy-boundary | beta-lactam allergy boundary for vancomycin use |
| metronidazole-oral | Table 3 metronidazole dose and use |
| moxifloxacin-oral | Table 3 moxifloxacin dose and use |
| linezolid-oral | Table 3 linezolid dose and use |
| levofloxacin-oral | Table 3 levofloxacin dose and use |
| ciprofloxacin-oral | Table 3 ciprofloxacin dose and use |
| tmp-smx-oral | Table 3 trimethoprim-sulfamethoxazole dose and use |
| clindamycin-oral | Table 3 clindamycin dose and use |
| doxycycline-rifampin-oral | Table 3 brucellar regimen |
| prolonged-treatment-harms | resistance and C. difficile harm boundary |
| treatment-failure-risk-profile | clinical findings that raise concern for treatment failure or relapse |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| population-boundary | adults-native-nvo | applies to adults with native vertebral osteomyelitis | RENDERED: 2015 ... Guidelines for the Diagnosis and Treatment of Native Vertebral Osteomyelitis in Adults | idsa-2015 | 1 | p1/narrative/adult-native-population | narrative |
| population-boundary | excluded-spinal-implant | does not address spinal implant-associated infections | RENDERED: The panel elected not to address patients with spinal implant-associated infections | idsa-2015 | 5 | p5/narrative/excluded-spinal-implant | narrative |
| population-boundary | excluded-postprocedure | does not address postprocedure infections | RENDERED: patients with postprocedure infections | idsa-2015 | 5 | p5/narrative/excluded-postprocedure | narrative |
| population-boundary | excluded-epidural-only | does not address epidural abscess without associated NVO | RENDERED: patients with epidural abscess without associated NVO | idsa-2015 | 5 | p5/narrative/excluded-epidural-only | narrative |
| diagnostic-trigger | new-back-neck-fever | suspect NVO | Clinicians should suspect the diagnosis of NVO in patients with new or worsening back or neck pain and fever | idsa-2015 | 7 | p7/grade-terse/1 | strong, low |
| diagnostic-trigger | new-back-neck-markers | suspect NVO | Clinicians should suspect the diagnosis of NVO in patients with new or worsening back or neck pain and elevated ESR or CRP | idsa-2015 | 7 | p7/grade-terse/2 | strong, low |
| diagnostic-trigger | new-back-neck-bloodstream | suspect NVO | Clinicians should suspect the diagnosis of NVO in patients with new or worsening back or neck pain and bloodstream infection or infective endocarditis | idsa-2015 | 7 | p7/grade-terse/3 | strong, low |
| diagnostic-trigger | fever-neurologic | consider NVO even without back pain | Clinicians may consider the diagnosis of NVO in patients who present with fever and new neurologic symptoms with or without back pain | idsa-2015 | 7 | p7/grade-terse/4 | weak, low |
| diagnostic-trigger | recent-s-aureus-pain | consider NVO after recent S. aureus bloodstream infection | RENDERED: Clinicians may consider the diagnosis of NVO in patients who present with new localized neck or back pain, following a recent episode of Staphylococcus aureus bloodstream infection | idsa-2015 | 7 | p7/grade-terse/5 | weak, low |
| s-aureus-history-window | recent-s-aureus-pain | obtain history for bloodstream infection within the previous year; preceding 3 months with compatible MRI usually precludes aspiration | RENDERED: history of or concomitant Staphylococcus aureus bloodstream infection in the previous year ... presence of S. aureus bloodstream infection within the preceding 3 months and compatible spine MRI changes preclude the need for a disc space aspiration in most patients | idsa-2015 | 1 | p1/narrative/s-aureus-time-boundaries | narrative |
| diagnostic-examination | suspected-nvo | perform pertinent medical and motor/sensory neurologic examination, including bowel and bladder continence and endocarditis signs | RENDERED: We recommend performing a pertinent medical and motor/sensory neurologic examination in patients with suspected NVO | idsa-2015 | 7 | p7/grade-terse/6 | strong, low |
| spep-screening | inconclusive-workup-biopsy | screen for multiple myeloma with serum protein electrophoresis when the original workup, including image-guided biopsy, remains inconclusive | RENDERED: Screening for multiple myeloma with an serum protein electrophoresis may be warranted, if the original workup including an image-guided biopsy remains inconclusive. | idsa-2015 | 7 | p7/narrative/spep-inconclusive-workup | narrative |
| initial-blood-labs | suspected-nvo | obtain 2 sets of aerobic and anaerobic blood cultures plus baseline ESR and CRP | bacterial (aerobic and anaerobic) blood cultures (2 sets) and baseline ESR and CRP | idsa-2015 | 7 | p7/grade-terse/7 | strong, low |
| initial-imaging | suspected-nvo | obtain spine MRI | We recommend a spine MRI in patients with suspected NVO | idsa-2015 | 7 | p7/grade-terse/8 | strong, low |
| initial-imaging | suspected-nvo-mri-unavailable | use combined gallium/Tc99 bone scan, CT, or PET when MRI cannot be obtained | RENDERED: combination spine gallium /Tc99 bone scan, or computed tomography scan or a positron emission tomography scan ... when MRI cannot be obtained | idsa-2015 | 7 | p7/grade-terse/9 | weak, low |
| repeat-mri-window | suspected-nvo | EVIDENCE ONLY: repeat MRI within 1-3 weeks if initial imaging lacks typical NVO features | RENDERED: A repeat examination may be warranted within 1-3 weeks if the initial imaging study fails to show typical features of NVO. | idsa-2015 | 8 | p8/narrative/repeat-mri-window | narrative |
| radiograph-delay | suspected-nvo | EVIDENCE ONLY: bone destruction becomes evident on plain radiography after 3-6 weeks of symptoms | RENDERED: It takes 3-6 weeks after the onset of symptoms for bone destruction to be evident on plain roentgenography. | idsa-2015 | 8 | p8/narrative/radiograph-delay | narrative |
| imaging-interpretation | suspected-nvo | do not primarily use indium-tagged WBC scanning because sensitivity is inadequate | RENDERED: Indium-tagged WBC scanning lacks sensitivity in the diagnosis of NVO and should not be primarily used in establishing the diagnosis of NVO. | idsa-2015 | 8 | p8/narrative/indium-wbc-boundary | narrative |
| imaging-interpretation | suspected-nvo-mri-unavailable | CT assesses bony and soft-tissue involvement and guides percutaneous biopsy; a negative PET scan excludes osteomyelitis including NVO | RENDERED: CT scanning is useful to assess the degree of bony and soft tissue involvement and is a very useful test to guide the percutaneous needle aspiration biopsy ... A negative PET scan excludes the diagnosis of osteomyelitis, including NVO | idsa-2015 | 8 | p8/narrative/ct-pet-interpretation | narrative |
| tuberculosis-radiographic-trigger-pattern | tuberculosis-risk | raise suspicion for tuberculosis with destruction of >=2 contiguous vertebrae and opposed endplates, anterior-longitudinal-ligament spread, disc infection with or without a paraspinal mass or mixed soft-tissue fluid collection, or less commonly spondylitis without disc involvement | RENDERED: findings that should raise suspicion for Mycobacterium tuberculosis NVO infection include (1) destruction of 2 or more contiguous vertebrae and their opposed endplates, (2) spread along the anterior longitudinal ligament, (3) disc infection with or without a paraspinal mass or mixed soft tissue fluid collection, or, less commonly, (4) spondylitis without disc involvement | idsa-2015 | 8 | p8/narrative/tuberculosis-radiographic-suspicion | narrative |
| tuberculosis-comparative-mri-pattern | tuberculosis-risk | EVIDENCE ONLY: compared with bacterial NVO, tuberculosis more commonly involves >=3 vertebral bodies and MRI more typically shows >1 level, larger paravertebral abscesses, heterogeneous vertebral-body signal, increased rim enhancement, and thoracic involvement | RENDERED: tuberculosis more commonly involves 3 or more vertebral bodies ... MRI ... typically have >1 level involvement, larger paravertebral abscesses, heterogeneous magnetic resonance intensity ... increased rim enhancement ... and are more likely to have a thoracic level of involvement | idsa-2015 | 10 | p10/narrative/tuberculosis-comparative-imaging | narrative |
| brucella-blood-serology-testing | subacute-brucella-risk | obtain Brucella blood cultures and serology | RENDERED: blood cultures and serologic tests for Brucella species in patients with subacute cases of NVO residing in endemic areas | idsa-2015 | 7 | p7/grade-terse/10 | strong, low |
| brucella-incubation-titer | subacute-brucella-risk | incubate blood cultures up to 2 weeks; a serum agglutination or Coombs titer >=1:160 supports the source-described endemic-setting boundary | RENDERED: blood cultures should be incubated for up to 2 weeks ... For serum agglutination and Coombs titers, the cutoff point is >=1:160. | idsa-2015 | 9 | p9/narrative/brucella-incubation-titer | narrative |
| fungal-testing | fungal-risk | obtain fungal blood cultures | obtaining fungal blood cultures in patients with suspected NVO and at risk for fungal infection | idsa-2015 | 8 | p8/grade-terse/1 | weak, low |
| tuberculosis-testing | tuberculosis-risk | perform PPD or obtain an interferon-gamma release assay | RENDERED: performing a PPD test or obtaining an interferon-gamma release assay in patients with subacute NVO and at risk for Mycobacterium tuberculosis NVO | idsa-2015 | 8 | p8/grade-terse/2 | weak, low |
| tuberculosis-tissue-culture | high-tuberculosis-suspicion | submit image-guided aspiration-biopsy specimens for mycobacterial tissue culture regardless of PPD or interferon-gamma release assay results | RENDERED: in a scenario of high clinical suspicion, we recommend submission of aspiration specimens from an image-guided aspiration biopsy for mycobacterial tissue cultures regardless of the results of these tests. | idsa-2015 | 8 | p8/narrative/high-suspicion-tb-tissue-culture | narrative |
| specialist-evaluation | suspected-nvo | consider infectious disease and spine-surgeon evaluation | RENDERED: evaluation by an infectious disease specialist and a spine surgeon may be considered | idsa-2015 | 8 | p8/grade-terse/3 | weak, low |
| initial-biopsy | biopsy-no-known-organism | perform image-guided aspiration biopsy | RENDERED: image-guided aspiration biopsy in all patients with suspected NVO ... when a microbiologic diagnosis ... has not been established | idsa-2015 | 9 | p9/grade-terse/1 | strong, low |
| initial-biopsy | known-associated-organism | do not perform image-guided aspiration biopsy when S. aureus, S. lugdunensis, or Brucella bloodstream infection establishes the microbiology | RENDERED: advise against performing an image-guided aspiration biopsy in patients with S. aureus, S. lugdunensis, or Brucella species bloodstream infection | idsa-2015 | 9 | p9/grade-terse/2 | strong, low |
| initial-biopsy | endemic-positive-brucella | do not perform image-guided aspiration biopsy in a high-endemicity setting with strongly positive Brucella serology | RENDERED: advise against performing an image-guided aspiration biopsy ... high endemic setting ... strongly positive Brucella serology | idsa-2015 | 9 | p9/grade-terse/3 | strong, low |
| initial-biopsy | low-endemic-brucella-serology | because false-positive serology is more likely in a low-endemicity setting, image-guided biopsy may be warranted | RENDERED: In the United States, a low-endemicity country ... a false-positive test for Brucella serology is more likely and an image-guided aspiration biopsy may be warranted. | idsa-2015 | 9 | p9/narrative/low-endemic-brucella-biopsy | narrative |
| initial-biopsy | other-organism-bloodstream | biopsy need is left to treating-physician discretion for bloodstream infection with organisms outside the named exceptions | RENDERED: bloodstream infection with other microorganisms (ie, Candida species, Enterobacteriaceae, streptococci, Pseudomonas species) is left to the discretion of the treating physicians. | idsa-2015 | 9 | p9/narrative/other-bsi-biopsy | narrative |
| initial-biopsy | sustained-skin-flora-bloodstream | sustained bloodstream infection with other coagulase-negative staphylococci may obviate biopsy in chronic hemodialysis or infected intravascular-device patients | RENDERED: sustained bloodstream infection with other coagulase-negative staphylococci ... receiving chronic hemodialysis or ... infected intravascular devices may also obviate the need for image-guided aspiration biopsy. | idsa-2015 | 9 | p9/narrative/sustained-skin-flora-biopsy | narrative |
| brucella-laboratory-alert | suspected-brucellar-nvo | alert microbiology laboratory personnel to use extended incubation and mitigate laboratory-acquired Brucella infection risk | RENDERED: When brucellar NVO is suspected, the physician is advised to alert the microbiology laboratory personnel to use extended incubation techniques and to mitigate the risk of laboratory-acquired Brucella infection. | idsa-2015 | 10 | p10/narrative/brucella-laboratory-alert | narrative |
| intravesical-bcg-history | intractable-back-pain | elicit a history of bladder cancer treated with intravesical BCG instillation | RENDERED: In patients with intractable back pain, a history of bladder cancer treated with intravesical BCG instillation should be elucidated. | idsa-2015 | 11 | p11/narrative/intravesical-bcg-history | narrative |
| prebiopsy-antibiotic-hold | neuro-sepsis-urgent | immediate surgery and empiric antimicrobials; do not withhold for biopsy | immediate surgical intervention and initiation of empiric antimicrobial therapy | idsa-2015 | 9 | p9/grade-terse/4 | strong, low |
| prebiopsy-antibiotic-hold | stable-neurologic-hemodynamic | when feasible, hold antibiotics for 1-2 weeks before image-guided biopsy | RENDERED: holding antibiotics when feasible for 1-2 weeks is reasonable. | idsa-2015 | 10 | p10/narrative/prebiopsy-antibiotic-hold | narrative |
| biopsy-special-cultures | biopsy-special-risk | add fungal, mycobacterial, or brucellar cultures when epidemiologic, host, or radiologic clues are present | RENDERED: addition of fungal, mycobacterial, or brucellar cultures on image-guided biopsy and aspiration specimens | idsa-2015 | 10 | p10/grade-terse/1 | weak, low |
| biopsy-special-cultures | significant-immunity-impairment | send biopsy material for bacterial, mycobacterial, and fungal stains and cultures | RENDERED: patients with significant impairment of their immunity and clinical and radiographic evidence of NVO to have biopsy material sent for bacterial, mycobacterial, and fungal stains and cultures | idsa-2015 | 11 | p11/narrative/impaired-immunity-biopsy-panel | narrative |
| biopsy-special-cultures | culture-negative-specimen | add fungal and mycobacterial cultures and bacterial nucleic-acid amplification testing to stored specimens | RENDERED: addition of fungal and mycobacterial cultures, and bacterial nucleic acid amplification testing ... if aerobic and anaerobic bacterial cultures reveal no growth | idsa-2015 | 10 | p10/grade-terse/2 | weak, low |
| repeat-biopsy-panel | nondiagnostic-first-biopsy | if repeated, send Gram stain/aerobic culture, mycobacterial stain/culture plus nucleic-acid amplification if available, Brucella culture, fungal stain/culture, and pathology | RENDERED: material should be sent for (1) Gram stain and aerobic culture, (2) mycobacterial stain and culture (and nucleic acid amplification testing if available), (3) brucellar culture, (4) fungal stain and culture, and (5) pathology. | idsa-2015 | 11 | p11/narrative/repeat-biopsy-panel | narrative |
| insufficient-specimen-prioritization | insufficient-biopsy-specimen | use epidemiologic considerations to determine which tests to prioritize when the specimen is insufficient for all studies | RENDERED: Epidemiologic considerations will need to be made when determining what to test for if specimen is insufficient for all studies. | idsa-2015 | 11 | p11/narrative/insufficient-specimen-prioritization | narrative |
| biopsy-volume-evidence | adequate-biopsy-tissue | EVIDENCE ONLY: >2 mL aspirated fluid had the highest positive-culture rate; needle size 11-18 gauge did not significantly change yield | RENDERED: highest rate of positive cultures was associated with obtaining >2 mL of fluid. The size of the needle used (range, 11-18 gauge) ... did not have a significant impact on the yield. | idsa-2015 | 11 | p11/narrative/biopsy-volume | narrative |
| biopsy-harms | biopsy-no-known-organism | image-guided biopsy can cause aortic or vascular injury, psoas puncture, nerve damage, hematoma, or wrong-level biopsy; severe complications are exceedingly rare with a trained operator | RENDERED: complications ... include aortic and vascular injuries, psoas muscle puncture or nerve damage, hematoma formation, and biopsy of incorrect level ... exceedingly rare when this procedure is performed by a trained operator. | idsa-2015 | 9 | p9/narrative/biopsy-harms | narrative |
| pathology-specimen | adequate-biopsy-tissue | send pathology specimens, especially with negative cultures | RENDERED: pathology specimens should be sent from all patients to help confirm a diagnosis of NVO ... especially in the setting of negative cultures | idsa-2015 | 11 | p11/grade-terse/1 | strong, low |
| contaminant-repeat-biopsy | first-biopsy-contaminant | obtain a second aspiration biopsy | RENDERED: obtaining a second aspiration biopsy ... original image-guided aspiration biopsy grew a skin contaminant | idsa-2015 | 12 | p12/grade-terse/1 | strong, low |
| nondiagnostic-organism-exclusion | nondiagnostic-first-biopsy | exclude anaerobes, fungi, Brucella, and mycobacteria | RENDERED: further testing should be done to exclude difficult-to-grow organisms | idsa-2015 | 12 | p12/grade-terse/2 | strong, low |
| nondiagnostic-procedure-next-step | nondiagnostic-first-biopsy | repeat image-guided biopsy, perform PEDD, or proceed to open excisional biopsy | RENDERED: repeating an image-guided aspiration biopsy, performing percutaneous endoscopic discectomy and drainage, or proceeding with an open excisional biopsy | idsa-2015 | 12 | p12/grade-terse/3 | weak, low |
| decompression-excisional-biopsy | decompression-surgery-indicated | perform excisional biopsy during indicated decompression without a preceding image-guided aspiration biopsy | RENDERED: When surgical intervention is indicated for decompression because of an epidural abscess or other neurologic complications, excisional biopsy should be done without the need for a preceding image-guided aspiration biopsy. | idsa-2015 | 12 | p12/narrative/decompression-excisional-biopsy | narrative |
| empiric-timing | stable-neurologic-hemodynamic | hold empiric therapy until a microbiologic diagnosis is established | RENDERED: holding empiric antimicrobial therapy until a microbiologic diagnosis is established | idsa-2015 | 12 | p12/grade-terse/4 | weak, low |
| empiric-timing | unstable-or-progressive | start empiric therapy while attempting microbiologic diagnosis | RENDERED: initiation of empiric antimicrobial therapy in conjunction with an attempt at establishing a microbiologic diagnosis | idsa-2015 | 12 | p12/grade-terse/5 | weak, low |
| empiric-coverage | unstable-or-progressive | cover MRSA and other staphylococci, streptococci, and aerobic gram-negative bacilli; examples are vancomycin plus cefepime, ciprofloxacin, or a carbapenem; allergy alternative is daptomycin plus a quinolone | RENDERED: include coverage against staphylococci, including methicillin-resistant S. aureus (MRSA), streptococci, and gram-negative bacilli ... vancomycin in combination with ciprofloxacin ... cefepime ... or ... a carbapenem ... daptomycin and a quinolone. | idsa-2015 | 12 | p12/narrative/empiric-coverage | narrative |
| empiric-avoidance | unstable-or-progressive | do not routinely add anaerobic, fungal, brucellar, or mycobacterial coverage | RENDERED: not in favor of routine use of empiric regimens that include coverage against anaerobes or fungal, brucellar, or mycobacterial organisms. | idsa-2015 | 13 | p13/narrative/empiric-avoidance | narrative |
| bacterial-duration | bacterial-nvo | 6 weeks of parenteral or highly bioavailable oral therapy | total duration of 6 weeks of parenteral or highly bioavailable oral antimicrobial therapy | idsa-2015 | 14 | p14/grade-terse/1 | strong, low |
| brucella-duration | brucellar-nvo | 3 months total antimicrobial therapy | RENDERED: total duration of 3 months of antimicrobial therapy for most patients with NVO due to Brucella species | idsa-2015 | 14 | p14/grade-terse/2 | strong, moderate |
| oral-switch-boundary | bacterial-nvo | EVIDENCE ONLY: early oral switch after median 2.7 weeks IV may be safe when CRP decreased and significant epidural or paravertebral abscesses were drained | RENDERED: switch to an oral antimicrobial therapy ... after a median intravenous therapy of 2.7 weeks ... may be safe, provided that CRP has decreased and epidural or paravertebral abscesses of significant size have been drained. | idsa-2015 | 14 | p14/narrative/oral-switch-boundary | narrative |
| high-risk-duration | high-failure-risk | EXPERT PRACTICE, LIMITED EVIDENCE: >6 weeks followed by oral therapy for >=3 months; weigh adverse-reaction risk and lack of efficacy data | RENDERED: longer treatment duration for >6 weeks followed by a course of oral therapy for 3 months or longer ... high risk for failure ... weighed against the lack of data ... and the potential for adverse reactions | idsa-2015 | 14 | p14/narrative/high-risk-duration | narrative |
| oral-beta-lactam-boundary | bacterial-nvo | do not use oral beta-lactams for initial NVO treatment because bioavailability is low | RENDERED: Oral beta-lactams should not be prescribed for the initial treatment of NVO given their low bioavailability. | idsa-2015 | 14 | p14/narrative/oral-beta-lactam | narrative |
| prolonged-treatment-harms | high-failure-risk | prolonged therapy can cause adverse reactions, resistant pathogens, and Clostridium difficile colitis | RENDERED: potential for adverse reactions associated with prolonged use of antimicrobial therapy, including emergence of resistant pathogens and Clostridium difficile colitis | idsa-2015 | 14 | p14/narrative/prolonged-treatment-harms | narrative |
| surgery-indication | surgical-neurologic-instability | perform surgery for progressive neurologic deficits, progressive deformity, or spinal instability with or without pain despite adequate antimicrobials | RENDERED: surgical intervention in patients with progressive neurologic deficits, progressive deformity, and spinal instability with or without pain despite adequate antimicrobial therapy | idsa-2015 | 14 | p14/grade-terse/3 | strong, low |
| surgery-indication | surgical-bloodstream-pain | consider debridement with or without stabilization | RENDERED: surgical debridement with or without stabilization in patients with persistent or recurrent bloodstream infection ... or worsening pain | idsa-2015 | 14 | p14/grade-terse/4 | weak, low |
| surgery-indication | improving-worse-bone-image | do not operate solely for worsening bony imaging at 4-6 weeks when clinical and laboratory response is improving | RENDERED: worsening bony imaging findings at 4-6 weeks in the setting of improvement in clinical symptoms, physical examination, and inflammatory markers | idsa-2015 | 14 | p14/grade-terse/5 | weak, low |
| cohort-surgical-indication | possible-cohort-surgical-indication | EVIDENCE ONLY: cohort-derived indications may include neurologic compromise, significant vertebral destruction with instability, large epidural abscess formation, intractable back pain, or failure of medical treatment | RENDERED: The indications for surgery may include the presence of neurologic compromise, significant vertebral destruction with instability, large epidural abscess formation, intractable back pain, or failure of medical treatment. | idsa-2015 | 15 | p15/narrative/cohort-surgical-indications | narrative |
| failure-definition | treated-nvo | persistent pain, residual neurologic deficits, elevated inflammatory markers, or radiographic findings alone do not necessarily mean failure | RENDERED: persistent pain, residual neurologic deficits, elevated markers of systemic inflammation, or radiographic findings alone do not necessarily signify treatment failure | idsa-2015 | 15 | p15/grade-terse/1 | weak, low |
| failure-definition | suspected-treatment-failure | the most specific failure measure is microbiologically confirmed persistent infection despite targeted therapy for an appropriate duration | RENDERED: The most specific measure of treatment failure is microbiologically confirmed persistent infection despite receipt of targeted antimicrobial therapy for an appropriate duration. | idsa-2015 | 16 | p16/narrative/failure-definition | narrative |
| false-failure-assignment-harm | treated-nvo | assigning failure without microbiologic evidence may overestimate failure and expose patients to potentially unnecessary medical and surgical interventions | RENDERED: Ascribing treatment failure to NVO patients in the absence of microbiologic evidence may lead to overestimation of treatment failure ... and predispose patients to potentially unnecessary medical and surgical interventions. | idsa-2015 | 16 | p16/narrative/false-failure-assignment-harm | narrative |
| inflammatory-monitoring-timing | treated-nvo | monitor ESR and/or CRP after approximately 4 weeks with clinical assessment | RENDERED: monitoring systemic inflammatory markers ... after approximately 4 weeks of antimicrobial therapy, in conjunction with a clinical assessment | idsa-2015 | 16 | p16/grade-terse/1 | weak, low |
| inflammatory-marker-interpretation | treated-nvo | EVIDENCE ONLY: after about 4 weeks, 25%-33% marker reduction lowers risk; 50% ESR reduction rarely precedes failure; ESR >50 mm/h or CRP >2.75 mg/dL increases risk, but interpret with clinical status | RENDERED: at least a 25%-33% reduction ... after ... approximately 4 weeks ... 50% reduction in ESR after 4 weeks rarely develop treatment failure ... ESR values >50 mm/hour and CRP values >2.75 mg/dL may confer a significantly higher risk ... values should be interpreted in concert with the clinical status | idsa-2015 | 16 | p16/narrative/inflammatory-marker-evidence | narrative |
| follow-up-imaging | favorable-response | do not routinely order follow-up MRI | RENDERED: recommend against routinely ordering follow-up MRI ... favorable clinical and laboratory response | idsa-2015 | 16 | p16/grade-terse/2 | strong, low |
| follow-up-imaging | poor-response | obtain follow-up MRI focused on epidural and paraspinal soft-tissue evolution | RENDERED: performing a follow-up MRI to assess evolutionary changes of the epidural and paraspinal soft tissues | idsa-2015 | 16 | p16/grade-terse/3 | weak, low |
| follow-up-imaging | treated-nvo | EVIDENCE ONLY: imaging <4 weeks can falsely suggest progression; worsened soft tissue at 4-8 weeks is the more relevant failure signal | RENDERED: Follow-up imaging performed <4 weeks ... may falsely suggest progressive infection ... worsened soft tissue findings on MRI 4-8 weeks after diagnosis | idsa-2015 | 16 | p16/narrative/follow-up-mri-timing | narrative |
| premature-follow-up-imaging-harm | treated-nvo | imaging before 4 weeks may falsely suggest progression and lead to unnecessary surgical debridement or prolonged antibiotic therapy | RENDERED: Follow-up imaging performed <4 weeks ... may falsely suggest progressive infection ... may influence clinicians to perform unnecessary surgical debridement or prolongation of antibiotic therapy. | idsa-2015 | 16 | p16/narrative/premature-follow-up-imaging-harm | narrative |
| inflammatory-marker-interpretation | suspected-treatment-failure | unchanged or increasing ESR or CRP after 4 weeks increases suspicion for failure | RENDERED: Unchanged or increasing values after 4 weeks of treatment should increase suspicion for treatment failure | idsa-2015 | 16 | p16/grade-terse/4 | weak, low |
| follow-up-imaging | suspected-treatment-failure | obtain follow-up MRI emphasizing paraspinal and epidural soft-tissue changes | RENDERED: obtaining a follow-up MRI with emphasis on evolutionary changes in the paraspinal and epidural soft tissue findings | idsa-2015 | 17 | p17/narrative/failure-follow-up-mri | narrative |
| failure-tissue-sampling | clinical-radiographic-failure | obtain additional bacterial, fungal, and mycobacterial tissue plus histopathology by image-guided or surgical sampling | RENDERED: obtaining additional tissue samples for microbiologic ... and histopathologic examination | idsa-2015 | 17 | p17/grade-terse/2 | weak, very low |
| failure-specialist-consultation | clinical-radiographic-failure | consult a spine surgeon and infectious disease physician | RENDERED: consultation with a spine surgeon and an infectious disease physician | idsa-2015 | 17 | p17/grade-terse/3 | weak, very low |
| treatment-failure-risk-profile | suspected-treatment-failure | highest-risk findings include persistent or progressive pain, systemic infection symptoms, undrained or partly drained large epidural abscess, persistently elevated inflammatory markers, diabetes, intravenous drug use, recurrent bloodstream infection, new neurologic deficits, or sinus tract | RENDERED: persistent or progressive pain, systemic symptoms of infection, undrained or partially drained large epidural abscess, or persistently elevated systemic inflammatory markers may be at highest risk ... diabetes mellitus, intravenous drug use, recurrent bloodstream infection, new-onset neurologic deficits, and sinus tract formation | idsa-2015 | 17 | p17/narrative/failure-risk-profile | narrative |

| oxacillin-susceptible-regimen | oxacillin-susceptible-staphylococci | nafcillin or oxacillin 1.5-2 g IV every 4-6 hours or continuous; cefazolin 1-2 g IV every 8 hours; or ceftriaxone 2 g IV every 24 hours; alternatives vancomycin 15-20 mg/kg IV every 12 hours, daptomycin 6-8 mg/kg IV every 24 hours, linezolid 600 mg PO/IV every 12 hours, levofloxacin 500-750 mg PO every 24 hours plus rifampin 600 mg PO daily, or clindamycin 600-900 mg IV every 8 hours; duration 6 weeks | RENDERED: Nafcillin sodium or oxacillin 1.5-2 g IV q4-6 h ... Cefazolin 1-2 g IV q8 h ... Ceftriaxone 2 g IV q24 h ... Vancomycin IV 15-20 mg/kg q12 h ... daptomycin 6-8 mg/kg IV q24 h ... linezolid 600 mg PO/IV q12 h ... levofloxacin 500-750 mg PO q24 h and rifampin PO 600 mg daily ... clindamycin IV 600-900 mg q8 h ... 6 wk duration | idsa-2015 | 13 | p13/narrative/table2-oxacillin-susceptible | narrative |
| oxacillin-resistant-regimen | oxacillin-resistant-staphylococci | vancomycin 15-20 mg/kg IV every 12 hours with loading-dose/level consideration; alternatives daptomycin 6-8 mg/kg IV every 24 hours, linezolid 600 mg PO/IV every 12 hours, or levofloxacin 500-750 mg PO every 24 hours plus rifampin 600 mg PO daily; duration 6 weeks | RENDERED: Vancomycin IV 15-20 mg/kg q12 h (consider loading dose, monitor serum levels) ... Daptomycin 6-8 mg/kg IV q24 h or linezolid 600 mg PO/IV q12 h or levofloxacin PO 500-750 mg PO q24 h and rifampin PO 600 mg daily ... 6 wk duration | idsa-2015 | 13 | p13/narrative/table2-oxacillin-resistant | narrative |
| penicillin-susceptible-enterococcus-regimen | penicillin-susceptible-enterococcus | penicillin G 20-24 million units IV every 24 hours continuously or in 6 doses, or ampicillin 12 g IV every 24 hours continuously or in 6 doses; alternatives are vancomycin 15-20 mg/kg every 12 hours with loading-dose consideration and serum-level monitoring, daptomycin 6 mg/kg every 24 hours, or linezolid 600 mg every 12 hours, but use vancomycin only for penicillin allergy; add aminoglycoside 4-6 weeks for endocarditis, shorter may be chosen for bloodstream infection, optional otherwise | RENDERED: Penicillin G 20-24 million units IV q24 h continuously or in 6 divided doses; or ampicillin sodium 12 g IV q24 h ... Vancomycin 15-20 mg/kg IV q12 h (consider loading dose, monitor serum levels) or daptomycin 6 mg/kg IV q24 h or linezolid 600 mg PO or IV q12 h ... addition of 4-6 wk of aminoglycoside therapy in patients with infective endocarditis ... shorter duration ... BSI ... Optional for other patients ... Vancomycin should be used only in case of penicillin allergy. | idsa-2015 | 13 | p13/narrative/table2-enterococcus-penicillin-susceptible | narrative |
| penicillin-resistant-enterococcus-regimen | penicillin-resistant-enterococcus | vancomycin 15-20 mg/kg IV every 12 hours with loading-dose consideration and serum-level monitoring; alternatives daptomycin 6 mg/kg IV every 24 hours or linezolid 600 mg PO/IV every 12 hours; add aminoglycoside 4-6 weeks for endocarditis, shorter may be chosen for bloodstream infection, optional otherwise | RENDERED: Vancomycin IV 15-20 mg/kg q12 h (consider loading dose, monitor serum levels) ... Daptomycin 6 mg/kg IV q24 h or linezolid 600 mg PO or IV q12 h ... addition of 4-6 wk of aminoglycoside therapy in patients with infective endocarditis ... shorter duration ... BSI ... optional for other patients | idsa-2015 | 13 | p13/narrative/table2-enterococcus-penicillin-resistant | narrative |
| vancomycin-resistant-enterococcus-options | vancomycin-resistant-enterococcus | daptomycin, linezolid, or Synercid may be used; the table footnote states no dose | RENDERED: Daptomycin, linezolid, or Synercid may be used for vancomycin-resistant enterococci. | idsa-2015 | 13 | p13/narrative/table2-vre-options | narrative |
| pseudomonas-regimen | pseudomonas-nvo | cefepime 2 g IV every 8-12 hours, meropenem 1 g IV every 8 hours, or doripenem 500 mg IV every 8 hours; alternatives ciprofloxacin 750 mg PO every 12 hours or 400 mg IV every 8 hours, aztreonam 2 g IV every 8 hours for severe penicillin allergy and quinolone resistance, or ceftazidime 2 g IV every 8 hours; duration 6 weeks; double coverage may be a beta-lactam plus ciprofloxacin or a beta-lactam plus an aminoglycoside | RENDERED: Cefepime 2 g IV q8-12 h or meropenem 1 g IV q8 h or doripenem 500 mg IV q8 h ... Ciprofloxacin 750 mg PO q12 h (or 400 mg IV q8 h) or aztreonam 2 g IV q8 h ... ceftazidime 2 g IV q8 h ... 6 wk duration ... Double coverage may be considered (ie, beta-lactam and ciprofloxacin or beta-lactam and an aminoglycoside). | idsa-2015 | 13 | p13/narrative/table2-pseudomonas | narrative |
| enterobacteriaceae-regimen | enterobacteriaceae-nvo | cefepime 2 g IV every 12 hours or ertapenem 1 g IV every 24 hours; alternative ciprofloxacin 500-750 mg PO every 12 hours or 400 mg IV every 12 hours; duration 6 weeks | RENDERED: Cefepime 2 g IV q12 h or ertapenem 1 g IV q24 h ... Ciprofloxacin 500-750 mg PO q12 h or 400 mg IV q12 hours ... 6 wk duration | idsa-2015 | 13 | p13/narrative/table2-enterobacteriaceae | narrative |
| beta-streptococci-regimen | beta-hemolytic-streptococci | penicillin G 20-24 million units IV every 24 hours continuously or in 6 doses, or ceftriaxone 2 g IV every 24 hours; allergy alternative vancomycin 15-20 mg/kg IV every 12 hours; duration 6 weeks | RENDERED: Penicillin G 20-24 million units IV q24 h continuously or in 6 divided doses or ceftriaxone 2 g IV q24 h ... Vancomycin IV 15-20 mg/kg q12 h ... 6 wk duration ... Vancomycin only in case of allergy. | idsa-2015 | 13 | p13/narrative/table2-beta-streptococci | narrative |
| propionibacterium-regimen | propionibacterium-nvo | penicillin G 20 million units IV every 24 hours continuously or in 6 doses, or ceftriaxone 2 g IV every 24 hours; alternatives clindamycin 600-900 mg IV every 8 hours or allergy-only vancomycin 15-20 mg/kg IV every 12 hours; duration 6 weeks | RENDERED: Penicillin G 20 million units IV q24 h continuously or in 6 divided doses or ceftriaxone 2 g IV q24 h ... Clindamycin 600-900 mg IV q8 h or vancomycin IV 15-20 mg/kg q12 h ... 6 wk duration ... Vancomycin only in case of allergy. | idsa-2015 | 13 | p13/narrative/table2-propionibacterium | narrative |
| salmonella-regimen | salmonella-nvo | ciprofloxacin 500 mg PO every 12 hours or 400 mg IV every 12 hours; alternative ceftriaxone 2 g IV every 24 hours if nalidixic-acid resistant; duration 6-8 weeks | RENDERED: Ciprofloxacin PO 500 mg q12 h or IV 400 mg q12 h ... Ceftriaxone 2 g IV q24 h (if nalidixic acid resistant) ... 6-8 wk duration | idsa-2015 | 13 | p13/narrative/table2-salmonella | narrative |
| antimicrobial-adjustment | adults-native-nvo | adjust doses for renal and hepatic function; select by susceptibility, allergies, intolerance, interactions, and contraindications; monitor toxicity and levels | RENDERED: Antimicrobial dosage needs to be adjusted based on patients' renal and hepatic function ... chosen based on in vitro susceptibility as well as patient allergies, intolerances, and potential drug interactions or contraindications ... monitoring of antimicrobial toxicity and levels | idsa-2015 | 13 | p13/narrative/table2-adjustment | narrative |
| flucloxacillin-option | oxacillin-susceptible-staphylococci | flucloxacillin may be used in Europe; the table footnote states no dose | RENDERED: Flucloxacillin may be used in Europe. | idsa-2015 | 13 | p13/narrative/table2-flucloxacillin | narrative |
| vancomycin-allergy-boundary | oxacillin-susceptible-staphylococci | restrict vancomycin to type I or documented delayed beta-lactam allergy | RENDERED: Vancomycin should be restricted to patients with type I or documented delayed allergy to beta-lactams. | idsa-2015 | 13 | p13/narrative/table2-vancomycin-allergy | narrative |

| metronidazole-oral | bacteroides-anaerobic-nvo | metronidazole 500 mg PO three or four times daily; may be used initially for susceptible anaerobes | RENDERED: Metronidazole 500 mg PO tid to qid ... initial course of NVO due to Bacteroides species and other susceptible anaerobes. | idsa-2015 | 15 | p15/narrative/table3-metronidazole | narrative |
| moxifloxacin-oral | oral-gram-negative-nvo | moxifloxacin 400 mg PO once daily; not for staphylococcal NVO, may be used for susceptible aerobic gram-negative organisms | RENDERED: Moxifloxacin 400 mg PO once daily ... not recommended ... staphylococcal NVO ... may be used ... Enterobacteriaceae and other susceptible aerobic gram-negative organisms. | idsa-2015 | 15 | p15/narrative/table3-moxifloxacin | narrative |
| linezolid-oral | oral-resistant-staphylococci | linezolid 600 mg PO twice daily; may be used initially when first-line agents cannot be used | RENDERED: Linezolid 600 mg PO bid ... initial course of NVO due to oxacillin-resistant staphylococci when first-line agents cannot be used. | idsa-2015 | 15 | p15/narrative/table3-linezolid | narrative |
| levofloxacin-oral | oral-gram-negative-nvo | levofloxacin 500-750 mg PO once daily; do not use as monotherapy for staphylococcal NVO; may use for susceptible aerobic gram-negative organisms | RENDERED: Levofloxacin 500-750 mg PO once daily ... not recommended ... staphylococcal NVO as monotherapy ... may be used ... Enterobacteriaceae and other susceptible aerobic gram-negative organisms. | idsa-2015 | 15 | p15/narrative/table3-levofloxacin | narrative |
| ciprofloxacin-oral | oral-gram-negative-nvo | ciprofloxacin 500-750 mg PO twice daily; do not use for staphylococcal NVO; may use for susceptible Enterobacteriaceae, Pseudomonas, and Salmonella | RENDERED: Ciprofloxacin 500-750 mg PO bid ... not recommended ... staphylococcal NVO ... may be used ... Enterobacteriaceae ... Pseudomonas aeruginosa and Salmonella species. | idsa-2015 | 15 | p15/narrative/table3-ciprofloxacin | narrative |
| tmp-smx-oral | oral-gram-negative-nvo | trimethoprim-sulfamethoxazole 1-2 double-strength tablets PO twice daily; not for staphylococcal NVO; second-line for susceptible aerobic gram-negative organisms; may monitor sulfamethoxazole levels | RENDERED: TMP-SMX 1-2 double strength tabs PO bid ... not recommended ... staphylococcal NVO ... second-line agent ... Enterobacteriaceae and other susceptible aerobic gram-negative organisms. May need to monitor sulfamethoxazole levels. | idsa-2015 | 15 | p15/narrative/table3-tmp-smx | narrative |
| clindamycin-oral | oxacillin-susceptible-staphylococci | clindamycin 300-450 mg PO four times daily; second-line for susceptible staphylococcal NVO | RENDERED: Clindamycin 300-450 mg PO qid ... second-line choice for sensitive staphylococcal NVO. | idsa-2015 | 15 | p15/narrative/table3-clindamycin | narrative |
| doxycycline-rifampin-oral | brucella-oral-regimen | doxycycline plus rifampin is mostly used for brucellar NVO; source cohort used both for 3 months, or streptomycin 2-3 weeks plus doxycycline 3 months | RENDERED: Doxycycline and rifampin ... Mostly used in patients with brucellar NVO ... streptomycin for 2-3 weeks and doxycycline for 3 months, or doxycycline and rifampin (both for 3 months). | idsa-2015 | 15 | p15/narrative/table3-brucella | narrative |

## Conflicts

No within-population conflict was identified. The stable-patient instruction to hold
empiric therapy and the urgent instruction to begin therapy with immediate surgery apply
to different neurologic and hemodynamic states. Six weeks is the general bacterial-NVO
duration; the 3-month Brucella course, 6-8-week Salmonella course, organism-specific
aminoglycoside adjuncts, and evidence-limited high-risk extension are separate organism
or risk branches rather than interchangeable alternatives.

The Brucella blood/serology action and incubation/titer interpretation are complementary;
the tuberculosis radiographic trigger pattern and comparative MRI evidence describe
different imaging functions. Repeat-biopsy contaminant handling, difficult-organism
exclusion, and procedural escalation are distinct steps. Failure sampling and specialist
consultation are cumulative actions, while inflammatory-marker timing and interpretation
are distinct quantities. None of those source statements is represented as a conflict.

## Coverage

The source is `bound`. Its 76 marker occurrences are reconciled as **76 = 37 cited +
39 disposed** without claiming that marker extraction found every recommendation. The
37 detailed, intact occurrences are cited in threshold rows above. The 38 summary
occurrences below duplicate the detailed recommendations, and the final p17 occurrence
is a split fragment represented by a rendered full recommendation row.

- `p2/grade-terse/1` - summary duplicate of cited `p7/grade-terse/1`
- `p2/grade-terse/2` - summary duplicate of cited `p7/grade-terse/2`
- `p2/grade-terse/3` - summary duplicate of cited `p7/grade-terse/3`
- `p2/grade-terse/4` - summary duplicate of cited `p7/grade-terse/4`
- `p2/grade-terse/5` - summary duplicate of cited `p7/grade-terse/5`
- `p2/grade-terse/6` - summary duplicate of cited `p7/grade-terse/6`
- `p2/grade-terse/7` - summary duplicate of cited `p7/grade-terse/7`
- `p2/grade-terse/8` - summary duplicate of cited `p7/grade-terse/8`
- `p2/grade-terse/9` - summary duplicate of cited `p7/grade-terse/9`
- `p2/grade-terse/10` - summary duplicate of cited `p7/grade-terse/10`
- `p2/grade-terse/11` - summary duplicate of cited `p8/grade-terse/1`
- `p2/grade-terse/12` - summary duplicate of cited `p8/grade-terse/2`
- `p2/grade-terse/13` - summary duplicate of cited `p8/grade-terse/3`
- `p2/grade-terse/14` - summary duplicate of cited `p9/grade-terse/1`
- `p2/grade-terse/15` - summary duplicate of cited `p9/grade-terse/2`
- `p2/grade-terse/16` - summary duplicate of cited `p9/grade-terse/3`
- `p2/grade-terse/17` - summary duplicate of cited `p9/grade-terse/4`
- `p3/grade-terse/1` - summary duplicate of cited `p10/grade-terse/1`
- `p3/grade-terse/2` - summary duplicate of cited `p10/grade-terse/2`
- `p4/grade-terse/1` - summary duplicate of cited `p11/grade-terse/1`
- `p4/grade-terse/2` - summary duplicate of cited `p12/grade-terse/1`
- `p4/grade-terse/3` - summary duplicate of cited `p12/grade-terse/2`
- `p4/grade-terse/4` - summary duplicate of cited `p12/grade-terse/3`
- `p4/grade-terse/5` - summary duplicate of cited `p12/grade-terse/4`
- `p4/grade-terse/6` - summary duplicate of cited `p12/grade-terse/5`
- `p4/grade-terse/7` - summary duplicate of cited `p14/grade-terse/1`
- `p4/grade-terse/8` - summary duplicate of cited `p14/grade-terse/2`
- `p4/grade-terse/9` - summary duplicate of cited `p14/grade-terse/3`
- `p4/grade-terse/10` - summary duplicate of cited `p14/grade-terse/4`
- `p4/grade-terse/11` - summary duplicate of cited `p14/grade-terse/5`
- `p4/grade-terse/12` - summary duplicate of cited `p15/grade-terse/1`
- `p4/grade-terse/13` - summary duplicate of cited `p16/grade-terse/1`
- `p4/grade-terse/14` - summary duplicate of cited `p16/grade-terse/2`
- `p4/grade-terse/15` - summary duplicate of cited `p16/grade-terse/3`
- `p4/grade-terse/16` - summary duplicate of cited `p16/grade-terse/4`
- `p5/grade-terse/1` - split summary fragment of the rendered failure follow-up MRI action
- `p5/grade-terse/2` - summary duplicate of cited `p17/grade-terse/2`
- `p5/grade-terse/3` - summary duplicate of cited `p17/grade-terse/3`
- `p17/grade-terse/1` - split detailed fragment represented by `p17/narrative/failure-follow-up-mri`

ADR 0009 disposition:

- Retained every diagnostic trigger and examination, culture/laboratory count, imaging
  choice and repeat interval, biopsy indication and exception, prebiopsy antibiotic hold,
  specialized specimen test, nondiagnostic-biopsy branch, pathology action, indium-WBC
  restriction, CT/PET interpretation, tuberculosis imaging-suspicion patterns,
  high-suspicion tuberculosis tissue culture regardless of PPD/IGRA, SPEP after an
  inconclusive workup, low-endemicity Brucella branch, microbiology-laboratory incubation
  and safety alert, intravesical-BCG history, epidemiology-based test prioritization for
  insufficient tissue, other-organism bloodstream discretion, immunocompromised-host
  biopsy panel, decompression-time excisional biopsy, and biopsy-harm boundary.
- Retained the stable-versus-urgent empiric-treatment branches, coverage targets and
  example regimens, and the routine exclusions for anaerobic, fungal, brucellar, and
  mycobacterial empiric coverage.
- Read both complete antimicrobial tables and retained every listed organism, drug,
  dose, route, frequency, duration, allergy boundary, adjunct rule, oral-use restriction,
  and renal/hepatic/susceptibility/interaction adjustment. Table footnotes and European
  flucloxacillin, vancomycin allergy, and vancomycin-resistant-enterococcus alternatives
  are retained even where the source footnote states a selection without a dose. Both
  Enterococcus rows retain vancomycin loading-dose and serum-level monitoring, the
  susceptible row limits vancomycin to penicillin allergy, and Pseudomonas double coverage
  preserves both beta-lactam-plus-ciprofloxacin and beta-lactam-plus-aminoglycoside options.
- Retained the 6-week bacterial and 3-month Brucella recommendations, Salmonella and
  endocarditis adjunct durations, early oral-switch evidence conditions, high-risk
  expert-practice limitation, oral beta-lactam restriction, and prolonged-treatment
  harms without converting cohort response rates into clinical targets.
- Retained all surgical, neurologic, bloodstream-infection, pain, monitoring, imaging,
  failure-definition, repeat-sampling, and specialist-consultation branches, including
  surgery for instability with or without pain, the cohort-derived large-epidural-abscess
  and intractable-pain indications, the 4-week and 4-8-week interpretation thresholds,
  the warning against treating isolated symptoms, markers, or imaging as failure, harms
  from false failure assignment and premature imaging, and the source-listed clinical
  profile that heightens concern for persistent or recurrent infection.
- Incidence, test sensitivity/specificity, biopsy yield percentages, cohort sizes,
  surgical outcome rates, research questions, administrative dates, disclosures, and
  reference-list numbers were read and scoped out unless a value directly changed the
  patient action represented above.
