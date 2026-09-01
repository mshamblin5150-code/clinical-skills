# Skin and soft tissue infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2014 | IDSA | IDSA/ciu296 | guideline | 2014 update | 2014-07-15 | https://doi.org/10.1093/cid/ciu296 | stated | bound |

## Scope

**Read:** all 43 source pages. The complete cold read covered the executive summary,
Figures 1-2, Tables 1-7, definitions, methods, all 25 recommendation questions and
their evidence summaries, future directions, article information, disclosures, and
references. The bound record contains 212 marker occurrences; it is an index into the
read, not the denominator of clinical content.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| title, executive summary, Figures 1-2, and recommendation summary | 1-10 | yes |
| introduction, methods, guideline development, and impetigo evidence | 10-13 | yes |
| purulent infection, recurrent abscess, cellulitis, and recurrent cellulitis | 13-17 | yes |
| surgical-site and necrotizing infection, including Tables 3-4 | 17-22 | yes |
| pyomyositis, gas gangrene, bites, anthrax, and uncommon zoonotic infections | 22-29 | yes |
| immunocompromised hosts, neutropenia, Tables 6-7, and cellular immune defects | 29-36 | yes |
| future directions | 36-37 | yes |
| acknowledgments, article information, and disclosures | 37 | read 2026-09-01; blind 2026-09-01 |
| references | 37-43 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| all-ssti-hosts | otherwise healthy hosts and compromised hosts of all age groups |
| limited-impetigo | patients with limited number of lesions |
| numerous-impetigo | patients with numerous lesions or in outbreaks affecting several people |
| purulent-moderate | patients with purulent infection with systemic signs of infection |
| purulent-severe | patients who have failed incision and drainage plus oral antibiotics or those with systemic signs of infection, or immunocompromised patients |
| recurrent-abscess | recurrent abscess |
| typical-cellulitis | typical cases of cellulitis without systemic signs of infection |
| severe-cellulitis | severe nonpurulent infection |
| nondiabetic-adult-cellulitis | nondiabetic adult patients with cellulitis |
| recurrent-cellulitis | patients who have 3-4 episodes of cellulitis per year despite attempts to treat or control predisposing factors |
| systemic-ssi | surgical site infections associated with a significant systemic response |
| intestinal-gu-ssi | Surgery of Intestinal or Genitourinary Tract |
| trunk-extremity-ssi | Surgery of trunk or extremity away from axilla or perineum |
| axilla-perineum-ssi | Surgery of axilla or perineum |
| necrotizing-infection | necrotizing infection of the skin, fascia, and muscle |
| documented-gas | documented group A streptococcal necrotizing fasciitis or clostridial myonecrosis |
| pyomyositis | patients with pyomyositis |
| animal-bite-high-risk | patients who are immunocompromised, asplenic, have advanced liver disease or edema, have moderate to severe hand or face injury, or possible periosteal or joint penetration |
| animal-human-bite | infections following animal or human bites |
| no-recent-tetanus | patients without toxoid vaccination within 10 years |
| natural-anthrax | naturally acquired cutaneous anthrax |
| bioterror-anthrax | bioterrorism cases because of presumed aerosol exposure |
| cat-scratch-heavy | patients with cat scratch disease weighing >45 kg |
| cat-scratch-light | patients with cat scratch disease weighing <45 kg |
| bacillary-angiomatosis | patients with bacillary angiomatosis |
| erysipeloid | patients with erysipeloid |
| bubonic-plague | patients with bubonic plague |
| severe-tularemia | severe cases of tularemia |
| mild-tularemia | mild cases of tularemia |
| fever-neutropenia | patients with fever and neutropenia |
| high-risk-neutropenia | anticipated prolonged and profound neutropenia or MASCC score <21 |
| low-risk-neutropenia | anticipated brief neutropenia and few comorbidities or MASCC score >=21 |
| initial-neutropenic-ssti | patients with SSTIs during the initial episode of fever and neutropenia |
| persistent-neutropenic-ssti | patients with SSTIs during persistent or recurrent episodes of fever and neutropenia |
| candida-ssti | Candida species SSTIs |
| aspergillus-ssti | Aspergillus SSTIs |
| mucor-rhizopus-ssti | Mucor/Rhizopus infections |
| resistant-ssti | multidrug-resistant organisms |
| cellular-immunodeficiency | patients with cellular immune defects |
| ntm-ssti | nontuberculous mycobacterial infections of the skin and soft tissues |
| nocardia-ssti | severe or disseminated Nocardia infection in cellular immune deficiency |
| disseminated-histoplasmosis | acute life-threatening progressive disseminated histoplasmosis |
| transplant-vzv-hsv | recipients of allogeneic blood and bone marrow transplants |
| table2-impetigo | impetigo caused by Staphylococcus and Streptococcus |
| table2-mssa | methicillin-susceptible Staphylococcus aureus skin and soft tissue infection |
| table2-mrsa | methicillin-resistant Staphylococcus aureus skin and soft tissue infection |
| table2-streptococcal | streptococcal skin infection |
| table4-mixed | mixed necrotizing infections |
| table4-strep | streptococcal necrotizing infection |
| table4-staph | staphylococcal necrotizing infection |
| table4-aeromonas-vibrio | Aeromonas hydrophila or Vibrio vulnificus necrotizing infection |

| dirty-major-wound | all other wounds, especially contaminated wounds |
| clean-minor-wound | clean and minor wounds |
| cat-scratch-evidence-heavy | patients weighing >=45.5 kg (100 lb) |
| cat-scratch-evidence-light | patients weighing <45.5 kg |
| tularemia-adult | adults with tularemia |
| tularemia-child | children with tularemia |
| cutaneous-anthrax-diagnostic | patients with suspected cutaneous anthrax |
| low-risk-neutropenic-oral | low-risk patients with fever and neutropenia who are candidates for oral empiric therapy |
| fluoroquinolone-prophylaxis | patients with fever and neutropenia already receiving fluoroquinolone prophylaxis |
| cutaneous-mold | immunocompromised patients with a single or localized cutaneous mold lesion |
| cryptococcal-ssti | patients with cryptococcal skin or soft tissue infection |
| hsv-ssti | immunocompromised patients with cutaneous HSV infection |
| vzv-ssti | immunocompromised patients with cutaneous VZV infection |
## Quantities

| key | verbatim |
| --- | --- |
| figure1-severity | purulent and nonpurulent severity thresholds |
| impetigo-topical | topical impetigo regimen |
| impetigo-oral | oral impetigo regimen |
| table2-impetigo-doses | Table 2 impetigo doses |
| table2-mssa-doses | Table 2 MSSA doses |
| table2-mrsa-doses | Table 2 MRSA doses |
| table2-strep-doses | Table 2 streptococcal doses |
| abscess-sirs | SIRS thresholds for adjunctive antibiotics |
| recurrent-abscess-course | recurrent abscess antibiotic course |
| recurrent-decolonization | recurrent S. aureus decolonization |
| cellulitis-course | cellulitis treatment duration |
| cellulitis-steroid | adjunctive prednisone regimen |
| cellulitis-ibuprofen | studied adjunctive ibuprofen regimen |
| recurrent-prophylaxis | recurrent cellulitis prophylaxis |
| recurrent-penicillin-evidence | phenoxymethyl-penicillin evidence regimen |
| ssi-systemic | systemic-response thresholds for SSI antibiotics |
| ssi-surveillance | SSI surveillance windows |
| table3-intestinal-gu | Table 3 intestinal or genitourinary SSI doses |
| table3-trunk-extremity | Table 3 trunk or extremity SSI doses |
| table3-axilla-perineum | Table 3 axilla or perineum SSI doses |
| necrotizing-reoperation | repeat debridement timing |
| necrotizing-stop | antimicrobial stopping boundary |
| table4-mixed-doses | Table 4 mixed-infection doses |
| table4-strep-doses | Table 4 streptococcal doses |
| table4-staph-doses | Table 4 staphylococcal doses |
| table4-water-doses | Table 4 Aeromonas and Vibrio doses |
| pyomyositis-course | pyomyositis duration |
| bite-preemption | bite prophylaxis duration |
| table5-animal-bite | Table 5 animal-bite doses |
| table5-human-bite | Table 5 human-bite doses |
| tetanus-window | tetanus booster window |
| anthrax-natural | naturally acquired anthrax regimen |
| anthrax-bioterror | bioterrorism anthrax regimen |
| cat-scratch-dose | cat scratch azithromycin |
| bacillary-course | bacillary angiomatosis regimen |
| erysipeloid-course | erysipeloid regimen |
| plague-dose | bubonic plague regimen |
| plague-course | bubonic plague narrative duration and isolation |
| tularemia-severe-dose | severe tularemia regimen |
| tularemia-mild-dose | mild tularemia regimen |
| tularemia-course | tularemia narrative duration |
| persistent-fever-window | persistent fever definition |
| neutropenia-definition | neutropenia definition |
| neutropenia-high | high-risk neutropenia thresholds |
| neutropenia-low | low-risk neutropenia thresholds |
| neutropenic-bacterial-course | bacterial SSTI duration |
| candida-course | Candida duration |
| aspergillus-course | Aspergillus duration |
| table6-antifungal | standard antifungal doses |
| table7-resistant | multidrug-resistant organism doses |
| ntm-course | NTM regimen and duration |
| nocardia-course | Nocardia duration |
| histoplasma-course | histoplasmosis transition and total duration |
| transplant-antiviral | transplant VZV/HSV prophylaxis |
| vzv-lesion-course | VZV lesion evolution in compromised hosts |
| cellulitis-yield | culture and pathogen-isolation yields |
| abscess-aspiration | needle aspiration success |
| necrotizing-mortality | group A streptococcal necrotizing-fasciitis mortality |
| candida-skin-frequency | candidiasis skin-lesion frequency |
| aspergillus-frequency | Aspergillus frequency in profound neutropenia |
| fusarium-frequency | Fusarium skin lesion and blood-culture frequency |

| figure1-wbc-print | Figure 1 printed WBC severity value |
| rec6-wbc-threshold | recommendation 6 WBC SIRS value |
| table2-pediatric-doses | Table 2 pediatric doses and age restrictions |
| table2-qualifiers | Table 2 drug-selection and toxicity qualifiers |
| table2-neonatal-boundary | Table 2 neonatal dose nonapplicability |
| table2-impetigo-footnote | Table 2 impetigo duration footnote |
| table2-erythromycin | Table 2 erythromycin dose and resistance qualifier |
| table2-strep-allergy | Table 2 severe-penicillin-hypersensitivity alternatives |
| table3-combination-doses | Table 3 intestinal/GU combination regimens |
| table3-mrsa-footnote | Table 3 axilla/perineum MRSA add-on |
| table4-pediatric-doses | Table 4 pediatric doses |
| table4-clostridial-doses | Table 4 clostridial adult and pediatric doses |
| table4-pediatric-water-boundary | Table 4 pediatric water-pathogen treatment boundary |
| table4-mixed-severe-allergy | Table 4 mixed-infection severe-penicillin-hypersensitivity alternatives |
| table4-strep-staph-allergy | Table 4 streptococcal and staphylococcal severe-allergy alternatives |
| table4-mrsa-footnote | Table 4 suspected-MRSA pediatric vancomycin footnote |
| table5-coverage-qualifiers | Table 5 spectrum and resistance qualifiers |
| table5-complete-animal | complete Table 5 animal-bite regimens |
| table5-complete-human | complete Table 5 human-bite alternatives |
| table6-qualifiers | Table 6 resistance, renal, spectrum, and PK qualifiers |
| table7-qualifiers | Table 7 spectrum, toxicity, and oral-bioavailability qualifiers |
| tetanus-dirty-window | contaminated-wound tetanus booster boundary |
| tetanus-clean-window | clean-minor-wound tetanus booster boundary |
| anthrax-diagnostic-action | anthrax vesicle/ulcer specimen and biopsy action |
| tularemia-adult-dose | adult tularemia aminoglycoside dosing and maximum |
| tularemia-child-dose | pediatric tularemia aminoglycoside dosing |
| cat-scratch-evidence-dose | narrative cat-scratch weight threshold |
| action-p12-1 | detailed recommendation fragment p12/grade-terse/1 action |
| action-p12-2 | detailed recommendation fragment p12/grade-terse/2 action |
| action-p12-3 | detailed recommendation fragment p12/grade-terse/3 action |
| action-p12-4 | detailed recommendation fragment p12/grade-terse/4 action |
| action-p12-5 | detailed recommendation fragment p12/grade-terse/5 action |
| action-p12-6 | detailed recommendation fragment p12/grade-terse/6 action |
| action-p13-1 | detailed recommendation fragment p13/grade-terse/1 action |
| action-p13-2 | detailed recommendation fragment p13/grade-terse/2 action |
| action-p13-3 | detailed recommendation fragment p13/grade-terse/3 action |
| action-p13-4 | detailed recommendation fragment p13/grade-terse/4 action |
| action-p13-5 | detailed recommendation fragment p13/grade-terse/5 action |
| action-p14-1 | detailed recommendation fragment p14/grade-terse/1 action |
| action-p14-2 | detailed recommendation fragment p14/grade-terse/2 action |
| action-p14-3 | detailed recommendation fragment p14/grade-terse/3 action |
| action-p14-4 | detailed recommendation fragment p14/grade-terse/4 action |
| action-p14-5 | detailed recommendation fragment p14/grade-terse/5 action |
| action-p14-6 | detailed recommendation fragment p14/grade-terse/6 action |
| action-p14-7 | detailed recommendation fragment p14/grade-terse/7 action |
| action-p14-8 | detailed recommendation fragment p14/grade-terse/8 action |
| action-p14-9 | detailed recommendation fragment p14/grade-terse/9 action |
| action-p14-10 | detailed recommendation fragment p14/grade-terse/10 action |
| action-p14-11 | detailed recommendation fragment p14/grade-terse/11 action |
| action-p14-12 | detailed recommendation fragment p14/grade-terse/12 action |
| action-p14-13 | detailed recommendation fragment p14/grade-terse/13 action |
| action-p14-14 | detailed recommendation fragment p14/grade-terse/14 action |
| action-p14-15 | detailed recommendation fragment p14/grade-terse/15 action |
| action-p14-16 | detailed recommendation fragment p14/grade-terse/16 action |
| action-p15-1 | detailed recommendation fragment p15/grade-terse/1 action |
| action-p16-1 | detailed recommendation fragment p16/grade-terse/1 action |
| action-p16-2 | detailed recommendation fragment p16/grade-terse/2 action |
| action-p16-3 | detailed recommendation fragment p16/grade-terse/3 action |
| action-p16-4 | detailed recommendation fragment p16/grade-terse/4 action |
| action-p17-1 | detailed recommendation fragment p17/grade-terse/1 action |
| action-p17-2 | detailed recommendation fragment p17/grade-terse/2 action |
| action-p17-3 | detailed recommendation fragment p17/grade-terse/3 action |
| action-p17-4 | detailed recommendation fragment p17/grade-terse/4 action |
| action-p17-5 | detailed recommendation fragment p17/grade-terse/5 action |
| action-p18-1 | detailed recommendation fragment p18/grade-terse/1 action |
| action-p18-2 | detailed recommendation fragment p18/grade-terse/2 action |
| action-p18-3 | detailed recommendation fragment p18/grade-terse/3 action |
| action-p22-1 | detailed recommendation fragment p22/grade-terse/1 action |
| action-p22-2 | detailed recommendation fragment p22/grade-terse/2 action |
| action-p22-3 | detailed recommendation fragment p22/grade-terse/3 action |
| action-p22-4 | detailed recommendation fragment p22/grade-terse/4 action |
| action-p22-5 | detailed recommendation fragment p22/grade-terse/5 action |
| action-p22-6 | detailed recommendation fragment p22/grade-terse/6 action |
| action-p22-7 | detailed recommendation fragment p22/grade-terse/7 action |
| action-p23-1 | detailed recommendation fragment p23/grade-terse/1 action |
| action-p23-2 | detailed recommendation fragment p23/grade-terse/2 action |
| action-p23-3 | detailed recommendation fragment p23/grade-terse/3 action |
| action-p23-4 | detailed recommendation fragment p23/grade-terse/4 action |
| action-p24-1 | detailed recommendation fragment p24/grade-terse/1 action |
| action-p24-2 | detailed recommendation fragment p24/grade-terse/2 action |
| action-p24-3 | detailed recommendation fragment p24/grade-terse/3 action |
| action-p25-1 | detailed recommendation fragment p25/grade-terse/1 action |
| action-p26-1 | detailed recommendation fragment p26/grade-terse/1 action |
| action-p26-2 | detailed recommendation fragment p26/grade-terse/2 action |
| action-p26-3 | detailed recommendation fragment p26/grade-terse/3 action |
| action-p26-4 | detailed recommendation fragment p26/grade-terse/4 action |
| action-p27-1 | detailed recommendation fragment p27/grade-terse/1 action |
| action-p27-2 | detailed recommendation fragment p27/grade-terse/2 action |
| action-p27-3 | detailed recommendation fragment p27/grade-terse/3 action |
| action-p27-4 | detailed recommendation fragment p27/grade-terse/4 action |
| action-p27-5 | detailed recommendation fragment p27/grade-terse/5 action |
| action-p27-6 | detailed recommendation fragment p27/grade-terse/6 action |
| action-p28-1 | detailed recommendation fragment p28/grade-terse/1 action |
| action-p28-2 | detailed recommendation fragment p28/grade-terse/2 action |
| action-p28-3 | detailed recommendation fragment p28/grade-terse/3 action |
| action-p28-4 | detailed recommendation fragment p28/grade-terse/4 action |
| action-p28-5 | detailed recommendation fragment p28/grade-terse/5 action |
| action-p28-6 | detailed recommendation fragment p28/grade-terse/6 action |
| action-p28-7 | detailed recommendation fragment p28/grade-terse/7 action |
| action-p29-1 | detailed recommendation fragment p29/grade-terse/1 action |
| action-p29-2 | detailed recommendation fragment p29/grade-terse/2 action |
| action-p29-3 | detailed recommendation fragment p29/grade-terse/3 action |
| action-p30-1 | detailed recommendation fragment p30/grade-terse/1 action |
| action-p30-2 | detailed recommendation fragment p30/grade-terse/2 action |
| action-p30-3 | detailed recommendation fragment p30/grade-terse/3 action |
| action-p30-4 | detailed recommendation fragment p30/grade-terse/4 action |
| action-p30-5 | detailed recommendation fragment p30/grade-terse/5 action |
| action-p31-1 | detailed recommendation fragment p31/grade-terse/1 action |
| action-p32-1 | detailed recommendation fragment p32/grade-terse/1 action |
| action-p32-2 | detailed recommendation fragment p32/grade-terse/2 action |
| action-p32-3 | detailed recommendation fragment p32/grade-terse/3 action |
| action-p32-4 | detailed recommendation fragment p32/grade-terse/4 action |
| action-p32-5 | detailed recommendation fragment p32/grade-terse/5 action |
| action-p32-6 | detailed recommendation fragment p32/grade-terse/6 action |
| action-p32-7 | detailed recommendation fragment p32/grade-terse/7 action |
| action-p32-8 | detailed recommendation fragment p32/grade-terse/8 action |
| action-p32-9 | detailed recommendation fragment p32/grade-terse/9 action |
| action-p32-10 | detailed recommendation fragment p32/grade-terse/10 action |
| action-p33-1 | detailed recommendation fragment p33/grade-terse/1 action |
| action-p33-2 | detailed recommendation fragment p33/grade-terse/2 action |
| action-p33-3 | detailed recommendation fragment p33/grade-terse/3 action |
| action-p33-4 | detailed recommendation fragment p33/grade-terse/4 action |
| action-p33-5 | detailed recommendation fragment p33/grade-terse/5 action |
| action-p33-6 | detailed recommendation fragment p33/grade-terse/6 action |
| action-p33-7 | detailed recommendation fragment p33/grade-terse/7 action |
| action-p33-8 | detailed recommendation fragment p33/grade-terse/8 action |
| action-p33-9 | detailed recommendation fragment p33/grade-terse/9 action |
| action-p33-10 | detailed recommendation fragment p33/grade-terse/10 action |
| action-p33-11 | detailed recommendation fragment p33/grade-terse/11 action |
| action-p34-1 | detailed recommendation fragment p34/grade-terse/1 action |
| action-p34-2 | detailed recommendation fragment p34/grade-terse/2 action |
| action-p34-3 | detailed recommendation fragment p34/grade-terse/3 action |
| action-p34-4 | detailed recommendation fragment p34/grade-terse/4 action |
| figure2-routing | Figure 2 surgical-site infection routing qualifiers |
| neutropenic-blood-cultures | blood-culture collection in fever and neutropenia |
| low-risk-neutropenic-oral-regimen | oral regimen for low-risk fever and neutropenia |
| fluoroquinolone-prophylaxis-boundary | empiric-therapy boundary after fluoroquinolone prophylaxis |
| linezolid-neutropenia-harm | linezolid harm in neutropenia |
| ntm-debridement | NTM culture, susceptibility, and healing debridement |
| nocardia-treatment | Nocardia antimicrobial and surgical management |
| cutaneous-mold-management | biopsy, resection, and antifungal choices for cutaneous mold |
| cryptococcal-management | medical treatment and surgery boundary for cryptococcal SSTI |
| histoplasma-suppression | long-term suppression after disseminated histoplasmosis treatment |
| vzv-treatment | VZV antiviral route and resistance action |
| hsv-treatment | HSV antiviral, resistance, duration, and surgery action |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| figure1-severity | purulent-severe | temperature >38 C, heart rate >90/min, respiratory rate >24/min, WBC <12 000 or <400 cells/uL; failed drainage plus oral antibiotics or immunocompromised | RENDERED: temperature >38°C, tachycardia (heart rate >90 beats per minute), tachypnea (respiratory rate >24 breaths per minute) or abnormal white blood cell count (<12 000 or <400 cells/µL), or immunocompromised patients | idsa-2014 | 2 | p2/figure1/1 | figure |
| impetigo-topical | limited-impetigo | mupirocin or retapamulin twice daily for 5 days | RENDERED: mupirocin or retapamulin twice daily (bid) for 5 days | idsa-2014 | 2 | p2/narrative/1 | narrative |
| impetigo-oral | numerous-impetigo | oral therapy for 7 days | RENDERED: Oral therapy for ecthyma or impetigo should be a 7-day regimen | idsa-2014 | 2 | p2/narrative/2 | narrative |
| table2-impetigo-doses | table2-impetigo | dicloxacillin 250 mg four times daily; cephalexin 250 mg four times daily; erythromycin 250 mg four times daily; clindamycin 300-400 mg four times daily; amoxicillin-clavulanate 875/125 mg twice daily | RENDERED: Dicloxacillin 250 mg qid po; Cephalexin 250 mg qid po; Erythromycin 250 mg qid po; Clindamycin 300-400 mg qid po; Amoxicillin-clavulanate 875/125 mg bid po | idsa-2014 | 5 | p5/table2/1 | table |
| table2-mssa-doses | table2-mssa | nafcillin or oxacillin 1-2 g every 4 hours IV; cefazolin 1 g every 8 hours IV; clindamycin 600 mg every 8 hours IV or 300-450 mg four times daily oral; dicloxacillin 500 mg four times daily; cephalexin 500 mg four times daily | RENDERED: Nafcillin or oxacillin 1-2 g every 4 h IV; Cefazolin 1 g every 8 h IV; Clindamycin 600 mg every 8 h IV or 300-450 mg qid po; Dicloxacillin 500 mg qid po; Cephalexin 500 mg qid po | idsa-2014 | 5 | p5/table2/2 | table |
| table2-mrsa-doses | table2-mrsa | vancomycin 30 mg/kg/day in 2 divided IV doses; linezolid 600 mg every 12 hours IV or twice daily oral; clindamycin 600 mg every 8 hours IV or 300-450 mg four times daily oral; daptomycin 4 mg/kg every 24 hours IV; ceftaroline 600 mg twice daily IV; doxycycline or minocycline 100 mg twice daily oral; SMX-TMP 1-2 double-strength tablets twice daily oral | RENDERED: Vancomycin 30 mg/kg/d in 2 divided doses IV; Linezolid 600 mg every 12 h IV or 600 mg bid po; Clindamycin 600 mg every 8 h IV or 300-450 mg qid po; Daptomycin 4 mg/kg every 24 h IV; Ceftaroline 600 mg bid IV; Doxycycline, minocycline 100 mg bid po; Trimethoprim-sulfamethoxazole 1-2 double-strength tablets bid po | idsa-2014 | 5 | p5/table2/3 | table |
| table2-strep-doses | table2-streptococcal | penicillin 2-4 million units every 4-6 hours IV; clindamycin 600-900 mg every 8 hours IV; nafcillin 1-2 g every 4-6 hours IV; cefazolin 1 g every 8 hours IV; penicillin VK 250-500 mg every 6 hours oral; cephalexin 500 mg every 6 hours oral | RENDERED: Penicillin 2-4 million units every 4-6 h IV; Clindamycin 600-900 mg every 8 h IV; Nafcillin 1-2 g every 4-6 h IV; Cefazolin 1 g every 8 h IV; Penicillin VK 250-500 mg every 6 h po; Cephalexin 500 mg every 6 h po | idsa-2014 | 6 | p6/table2/1 | table |
| abscess-sirs | purulent-moderate | temperature >38 C or <36 C, respiratory rate >24/min, heart rate >90/min, or WBC >12 000 or <400 cells/uL | RENDERED: temperature >38°C or <36°C, tachypnea >24 breaths per minute, tachycardia >90 beats per minute, or white blood cell count >12 000 or <400 cells/µL | idsa-2014 | 13 | p13/narrative/1 | narrative |
| recurrent-abscess-course | recurrent-abscess | 5-10 days active against isolated pathogen | RENDERED: treat with a 5- to 10-day course of an antibiotic active against the pathogen isolated | idsa-2014 | 14 | p14/narrative/1 | narrative |
| recurrent-decolonization | recurrent-abscess | 5 days; intranasal mupirocin twice daily, chlorhexidine wash daily, personal-item decontamination daily | RENDERED: 5-day decolonization regimen twice daily of intranasal mupirocin, daily chlorhexidine washes, and daily decontamination of personal items | idsa-2014 | 14 | p14/narrative/2 | narrative |
| cellulitis-course | typical-cellulitis | 5 days; extend if not improved | RENDERED: recommended duration of antimicrobial therapy is 5 days, but treatment should be extended if the infection has not improved | idsa-2014 | 14 | p14/narrative/3 | narrative |
| cellulitis-steroid | nondiabetic-adult-cellulitis | prednisone 40 mg daily for 7 days | RENDERED: prednisone 40 mg daily for 7 days | idsa-2014 | 16 | p16/narrative/1 | narrative |
| cellulitis-ibuprofen | nondiabetic-adult-cellulitis | ibuprofen 400 mg four times daily for 5 days was studied as an adjunct | RENDERED: ibuprofen 400 mg 4 times daily (qid) for 5 days | idsa-2014 | 16 | p16/narrative/2 | narrative |
| recurrent-prophylaxis | recurrent-cellulitis | oral penicillin or erythromycin twice daily for 4-52 weeks, or benzathine penicillin IM every 2-4 weeks; continue while risk factors persist | RENDERED: oral penicillin or erythromycin bid for 4-52 weeks, or intramuscular benzathine penicillin every 2-4 weeks | idsa-2014 | 16 | p16/narrative/3 | narrative |
| recurrent-penicillin-evidence | recurrent-cellulitis | phenoxymethyl-penicillin 250 mg twice daily for 12 months; recurrence 37% to 22%, median recurrence 532 to 626 days | RENDERED: phenoxymethyl-penicillin given as 250 mg twice daily for 12 months increased the time to recurrence to 626 days compared with 532 days and decreased recurrence from 37% to 22% | idsa-2014 | 17 | p17/narrative/1 | narrative |
| ssi-systemic | systemic-ssi | erythema and induration >5 cm, temperature >38.5 C, heart rate >110/min, or WBC >12 000/uL | RENDERED: erythema and induration extending >5 cm from the wound edge, temperature >38.5°C, heart rate >110 beats/minute, or white blood cell count >12 000/µL | idsa-2014 | 17 | p17/narrative/2 | narrative |
| ssi-surveillance | systemic-ssi | 30 days without prosthesis; 1 year with prosthesis | RENDERED: 30 days of follow-up for operations without placement of prosthetic material and for 1 year for operations where a prosthesis was inserted | idsa-2014 | 18 | p18/narrative/1 | narrative |
| table3-intestinal-gu | intestinal-gu-ssi | ticarcillin-clavulanate 3.1 g every 6 hours IV; piperacillin-tazobactam 3.375 g every 6 hours or 4.5 g every 8 hours IV; imipenem-cilastatin 500 mg every 6 hours; meropenem 1 g every 8 hours; ertapenem 1 g every 24 hours | RENDERED: Ticarcillin-clavulanate 3.1 g every 6 h IV; Piperacillin-tazobactam 3.375 g every 6 h or 4.5 g every 8 h IV; Imipenem-cilastatin 500 mg every 6 h IV; Meropenem 1 g every 8 h IV; Ertapenem 1 g every 24 h IV | idsa-2014 | 19 | p19/table3/1 | table |
| table3-trunk-extremity | trunk-extremity-ssi | oxacillin or nafcillin 2 g every 6 hours IV; cefazolin 0.5-1 g every 8 hours IV; cephalexin 500 mg every 6 hours oral; SMX-TMP 160-800 mg every 6 hours oral; vancomycin 15 mg/kg every 12 hours IV | RENDERED: Oxacillin or nafcillin 2 g every 6 h IV; Cefazolin 0.5-1 g every 8 h IV; Cephalexin 500 mg every 6 h po; SMX-TMP 160-800 mg po every 6 h; Vancomycin 15 mg/kg every 12 h IV | idsa-2014 | 19 | p19/table3/2 | table |
| table3-axilla-perineum | axilla-perineum-ssi | metronidazole 500 mg every 8 hours plus ciprofloxacin 400 mg IV or 750 mg oral every 12 hours, levofloxacin 750 mg every 24 hours, or ceftriaxone 1 g every 24 hours | RENDERED: Metronidazole 500 mg every 8 h IV plus Ciprofloxacin 400 mg IV every 12 h or 750 mg po every 12 h; Levofloxacin 750 mg every 24 h; Ceftriaxone 1 g every 24 h | idsa-2014 | 19 | p19/table3/3 | table |
| necrotizing-reoperation | necrotizing-infection | return to operating room 24-36 hours after first debridement and daily thereafter until no further debridement needed | RENDERED: return to the operating room 24-36 hours after the first debridement and daily thereafter until the surgical team finds no further need for debridement | idsa-2014 | 21 | p21/narrative/1 | narrative |
| necrotizing-stop | necrotizing-infection | continue until no further debridement, clinical improvement, and afebrile 48-72 hours | RENDERED: until further debridement is no longer necessary, the patient has improved clinically, and fever has been absent for 48-72 hours | idsa-2014 | 21 | p21/narrative/2 | narrative |
| table4-mixed-doses | table4-mixed | piperacillin-tazobactam 3.37 g every 6-8 hours IV plus vancomycin 30 mg/kg/day in 2 doses; or imipenem-cilastatin 1 g every 6-8 hours, meropenem 1 g every 8 hours, ertapenem 1 g daily | RENDERED: Piperacillin-tazobactam 3.37 g every 6-8 h IV plus vancomycin 30 mg/kg/d in 2 divided doses; Imipenem-cilastatin 1 g every 6-8 h IV; Meropenem 1 g every 8 h IV; Ertapenem 1 g daily IV | idsa-2014 | 20 | p20/table4/1 | table |
| table4-strep-doses | table4-strep | penicillin 2-4 million units every 4-6 hours IV plus clindamycin 600-900 mg every 8 hours IV | RENDERED: Penicillin 2-4 million units every 4-6 h IV plus clindamycin 600-900 mg every 8 h IV | idsa-2014 | 20 | p20/table4/2 | table |
| table4-staph-doses | table4-staph | nafcillin or oxacillin 1-2 g every 4 hours IV; cefazolin 1 g every 8 hours IV; resistant strains vancomycin 30 mg/kg/day in 2 IV doses | RENDERED: Nafcillin 1-2 g every 4 h IV; Oxacillin 1-2 g every 4 h IV; Cefazolin 1 g every 8 h IV; Vancomycin for resistant strains 30 mg/kg/d in 2 divided doses IV | idsa-2014 | 20 | p20/table4/3 | table |
| table4-water-doses | table4-aeromonas-vibrio | Aeromonas: doxycycline 100 mg every 12 hours IV plus ciprofloxacin 500 mg every 12 hours IV or ceftriaxone 1-2 g every 24 hours; Vibrio: doxycycline 100 mg every 12 hours IV plus ceftriaxone 1 g four times daily or cefotaxime 2 g three times daily | RENDERED: Aeromonas hydrophila Doxycycline 100 mg every 12 h IV plus ciprofloxacin 500 mg every 12 h IV or ceftriaxone 1 to 2 g every 24 h IV; Vibrio vulnificus Doxycycline 100 mg every 12 h IV plus ceftriaxone 1 g qid IV or cefotaxime 2 g tid IV | idsa-2014 | 20 | p20/table4/4 | table |
| pyomyositis-course | pyomyositis | IV initially, oral after clinical improvement, promptly cleared bacteremia, and no endocarditis or metastatic abscess; total Two to 3 weeks | RENDERED: Antibiotics should be administered intravenously initially, but once the patient is clinically improved, oral antibiotics are appropriate for patients in whom bacteremia cleared promptly and there is no evidence of endocarditis or metastatic abscess. Two to 3 weeks of therapy is recommended | idsa-2014 | 22 | p22/narrative/1 | narrative |
| bite-preemption | animal-bite-high-risk | preemptive therapy 3-5 days | RENDERED: Preemptive early antimicrobial therapy for 3-5 days | idsa-2014 | 24 | p24/narrative/1 | narrative |
| table5-animal-bite | animal-human-bite | amoxicillin-clavulanate 875/125 mg twice daily oral; ampicillin-sulbactam 1.5-3.0 g every 6-8 hours IV; doxycycline 100 mg twice daily oral or every 12 hours IV; cefuroxime 500 mg twice daily oral or 1 g every 12 hours IV | RENDERED: Animal bite Amoxicillin-clavulanate 875/125 mg bid; Ampicillin-sulbactam 1.5-3.0 g every 6-8 h; Doxycycline 100 mg bid oral or 100 mg every 12 h IV; Cefuroxime 500 mg bid oral or 1 g every 12 h IV | idsa-2014 | 25 | p25/table5/1 | table |
| table5-human-bite | animal-human-bite | amoxicillin-clavulanate 875/125 mg twice daily oral; ampicillin-sulbactam 1.5-3.0 g every 6 hours IV; doxycycline 100 mg twice daily oral | RENDERED: Human bite Amoxicillin-clavulanate 875/125 mg bid; Ampicillin-sulbactam 1.5-3.0 g every 6 h; Doxycycline 100 mg bid | idsa-2014 | 25 | p25/table5/2 | table |
| tetanus-window | no-recent-tetanus | give toxoid if no vaccination within 10 years; prefer Tdap if never given | RENDERED: Tetanus toxoid should be administered to patients without toxoid vaccination within 10 years | idsa-2014 | 25 | p25/narrative/1 | narrative |
| anthrax-natural | natural-anthrax | penicillin V 500 mg four times daily for 7-10 days | RENDERED: Oral penicillin V 500 mg qid for 7-10 days | idsa-2014 | 26 | p26/narrative/1 | narrative |
| anthrax-bioterror | bioterror-anthrax | ciprofloxacin 500 mg oral twice daily or levofloxacin 500 mg IV/oral every 24 hours for 60 days | RENDERED: Ciprofloxacin 500 mg by mouth bid or levofloxacin 500 mg intravenously or by mouth every 24 hours for 60 days | idsa-2014 | 26 | p26/narrative/2 | narrative |
| cat-scratch-dose | cat-scratch-heavy | azithromycin 500 mg day 1, then 250 mg daily for 4 more days | RENDERED: Patients >45 kg: 500 mg on day 1 followed by 250 mg for 4 additional days | idsa-2014 | 27 | p27/narrative/1 | narrative |
| cat-scratch-dose | cat-scratch-light | azithromycin 10 mg/kg day 1, then 5 mg/kg daily for 4 more days | RENDERED: Patients <45 kg: 10 mg/kg on day 1 and 5 mg/kg for 4 more days | idsa-2014 | 27 | p27/narrative/2 | narrative |
| bacillary-course | bacillary-angiomatosis | erythromycin 500 mg four times daily or doxycycline 100 mg twice daily for 2 weeks-2 months | RENDERED: Erythromycin 500 mg qid or doxycycline 100 mg bid for 2 weeks to 2 months | idsa-2014 | 27 | p27/narrative/3 | narrative |
| erysipeloid-course | erysipeloid | penicillin 500 mg four times daily or amoxicillin 500 mg three times daily for 7-10 days | RENDERED: Penicillin 500 mg qid or amoxicillin 500 mg 3 times daily for 7-10 days | idsa-2014 | 27 | p27/narrative/4 | narrative |
| plague-dose | bubonic-plague | streptomycin 15 mg/kg IM every 12 hours or doxycycline 100 mg twice daily oral | RENDERED: Streptomycin 15 mg/kg intramuscularly every 12 hours or doxycycline 100 mg bid po | idsa-2014 | 28 | p28/narrative/1 | narrative |
| plague-course | bubonic-plague | 10-14 days probably adequate; respiratory isolation until after 48 hours effective therapy if pneumonic risk | RENDERED: 10-14 days is probably adequate; respiratory isolation until after 48 hours of effective drug therapy | idsa-2014 | 28 | p28/narrative/2 | narrative |
| tularemia-severe-dose | severe-tularemia | streptomycin 15 mg/kg IM every 12 hours or gentamicin 1.5 mg/kg IV every 8 hours | RENDERED: Streptomycin 15 mg/kg every 12 hours IM or gentamicin 1.5 mg/kg every 8 hours IV | idsa-2014 | 28 | p28/narrative/3 | narrative |
| tularemia-mild-dose | mild-tularemia | tetracycline 500 mg four times daily or doxycycline 100 mg twice daily oral | RENDERED: Tetracycline 500 mg qid or doxycycline 100 mg bid given by mouth | idsa-2014 | 28 | p28/narrative/4 | narrative |
| tularemia-course | severe-tularemia | parenteral until acute illness controlled; 7-10 days total, extend severe cases to 14 days | RENDERED: duration of 7-10 days. Treatment of severe cases should be extended to 14 days | idsa-2014 | 29 | p29/narrative/1 | narrative |
| tularemia-course | mild-tularemia | oral regimens at least 14 days | RENDERED: For oral regimens, patients should receive at least 14 days of therapy | idsa-2014 | 29 | p29/narrative/2 | narrative |
| persistent-fever-window | fever-neutropenia | persistent episode after 4-7 days | RENDERED: persistent unexplained fever of their initial episode after 4-7 days | idsa-2014 | 30 | p30/narrative/1 | narrative |
| neutropenia-definition | fever-neutropenia | ANC <500 cells/uL or expected <500 within 48 hours | RENDERED: Neutropenia is defined as an ANC <500 cells/µL, or a neutrophil count that is expected to decrease to <500 cells/µL within 48 hours | idsa-2014 | 30 | p30/narrative/2 | narrative |
| neutropenia-high | high-risk-neutropenia | anticipated >7 days and ANC <100 cells/uL, or MASCC <21 | RENDERED: anticipated prolonged (>7 days) and profound neutropenia (absolute neutrophil count <100 cells/µL) or with a MASCC score of <21 | idsa-2014 | 30 | p30/narrative/3 | narrative |
| neutropenia-low | low-risk-neutropenia | anticipated <7 days with few comorbidities, or MASCC >=21 | RENDERED: anticipated brief (<7 days) periods of neutropenia and few comorbidities or with a MASCC score of ≥21 | idsa-2014 | 30 | p30/narrative/4 | narrative |
| neutropenic-bacterial-course | initial-neutropenic-ssti | 7-14 days for most bacterial SSTIs | RENDERED: treatment duration for most bacterial SSTIs should be 7-14 days | idsa-2014 | 32 | p32/narrative/1 | narrative |
| candida-course | candida-ssti | 2 weeks after bloodstream clearance or skin-lesion resolution | RENDERED: Treatment should be for 2 weeks after clearance of bloodstream infection or resolution of skin lesions | idsa-2014 | 32 | p32/narrative/2 | narrative |
| aspergillus-course | aspergillus-ssti | voriconazole; alternatives lipid amphotericin B, posaconazole, or echinocandin for 6-12 weeks | RENDERED: Aspergillus SSTIs should be treated with voriconazole, or alternatively lipid formulations of amphotericin B, posaconazole, or echinocandin for 6-12 weeks | idsa-2014 | 33 | p33/narrative/1 | narrative |
| table6-antifungal | persistent-neutropenic-ssti | fluconazole 100-400 mg every 24 hours oral or 800 mg IV load then 400 mg daily; voriconazole 400 mg twice daily for 2 doses then 200 mg every 12 hours oral or 6 mg/kg IV every 12 hours for 2 doses then 4 mg/kg every 12 hours; posaconazole 400 mg twice daily with meals; lipid-complex amphotericin B 5 mg/kg/day; liposomal amphotericin B 3-5 mg/kg/day | RENDERED: Fluconazole 100-400 mg every 24 h; 800 mg loading dose then 400 mg daily. Voriconazole 400 mg bid for 2 doses then 200 mg every 12 h; 6 mg/kg IV every 12 h for 2 doses followed by 4 mg/kg IV every 12 h. Posaconazole 400 mg bid with meals. Lipid complex amphotericin B 5 mg/kg/d. Liposomal amphotericin B 3-5 mg/kg/d | idsa-2014 | 32 | p32/table6/1 | table |
| table7-resistant | resistant-ssti | vancomycin 30-60 mg/kg/day in 2-4 doses with trough 15-20 mcg/mL; daptomycin 4-6 mg/kg/day; linezolid 600 mg every 12 hours; colistin 5 mg/kg load then 2.5 mg/kg every 12 hours | RENDERED: Vancomycin 30-60 mg/kg/d in 2-4 divided doses, target serum trough concentrations of 15-20 µg/mL; Daptomycin 4-6 mg/kg/d; Linezolid 600 mg every 12 h; Colistin 5 mg/kg load, then 2.5 mg/kg every 12 h | idsa-2014 | 33 | p33/table7/1 | table |
| ntm-course | ntm-ssti | combination therapy 6-12 weeks: macrolide plus second susceptible agent | RENDERED: prolonged combination therapy (duration, 6-12 weeks) that should consist of a macrolide antibiotic and a second agent to which the isolate is susceptible | idsa-2014 | 34 | p34/narrative/1 | narrative |
| nocardia-course | nocardia-ssti | combination therapy for severe infection; total 6-24 months based on dissemination and immunosuppression | RENDERED: duration of treatment (6-24 months) should take into account the presence of disseminated disease and the extent of immunosuppression | idsa-2014 | 35 | p35/narrative/1 | narrative |
| histoplasma-course | disseminated-histoplasmosis | amphotericin B until improvement in 1-2 weeks, then itraconazole to complete at least 6-12 months | RENDERED: rapid clinical improvement within 1-2 weeks, and itraconazole can then replace amphotericin B to complete at least 6-12 months | idsa-2014 | 35 | p35/narrative/2 | narrative |
| transplant-antiviral | transplant-vzv-hsv | acyclovir 800 mg twice daily or valacyclovir 500 mg twice daily during first year after transplant | RENDERED: acyclovir (800 mg bid) or valacyclovir (500 mg bid) during the first year following transplant | idsa-2014 | 36 | p36/narrative/1 | narrative |
| vzv-lesion-course | cellular-immunodeficiency | lesions may develop 7-14 days and heal more slowly | RENDERED: among immunocompromised hosts, skin lesions may continue to develop over a longer period (7-14 days) | idsa-2014 | 36 | p36/narrative/2 | narrative |
| cellulitis-yield | typical-cellulitis | blood cultures <=5%; needle aspiration <=5%-about 40%; punch biopsy 20%-30%; clinical pathogen isolation <20% | RENDERED: Blood cultures are generally positive in ≤5% of cases; needle aspiration ranges from ≤5% to approximately 40%; punch biopsy specimens yield an organism in 20%-30%; clinical isolation rate is <20% | idsa-2014 | 15 | p15/narrative/1 | narrative |
| abscess-aspiration | recurrent-abscess | ultrasound-guided aspiration successful 25% overall and <10% with MRSA | RENDERED: aspiration was successful in only 25% of cases overall and <10% with MRSA infections | idsa-2014 | 13 | p13/narrative/2 | narrative |
| necrotizing-mortality | necrotizing-infection | group A streptococcal infection with hypotension/organ failure mortality 30%-70% | RENDERED: mortality in patients with group A streptococcal necrotizing fasciitis, hypotension, and organ failure is high, ranging from 30% to 70% | idsa-2014 | 19 | p19/narrative/4 | narrative |
| candida-skin-frequency | persistent-neutropenic-ssti | up to 13% develop skin lesions measuring 0.5-1.0 cm | RENDERED: up to 13% of patients with invasive disseminated candidiasis develop skin lesions; papules (0.5-1.0 cm) | idsa-2014 | 33 | p33/narrative/2 | narrative |
| aspergillus-frequency | persistent-neutropenic-ssti | 10%-14% with profound prolonged neutropenia | RENDERED: Aspergillus species infections occur in 10%-14% of patients with profound and prolonged neutropenia | idsa-2014 | 34 | p34/narrative/2 | narrative |
| fusarium-frequency | persistent-neutropenic-ssti | skin lesions 60%-80%; blood cultures positive 40%-50% | RENDERED: Skin lesions are very common (60%-80% of infections); Blood cultures are frequently positive (40%-50%) | idsa-2014 | 34 | p34/narrative/3 | narrative |

| rec6-wbc-threshold | purulent-moderate | WBC >12 000 or <400 cells/uL | white blood cell count >12 000 or <400 cells/µL | idsa-2014 | 13 | p13/grade-terse/4 | strong recommendation, low-quality evidence |
| table2-pediatric-doses | table2-impetigo | cephalexin 25-50 mg/kg/day in 3-4 oral doses; erythromycin 40 mg/kg/day in 3-4 oral doses; clindamycin 20 mg/kg/day in 3 oral doses; amoxicillin-clavulanate 25 mg/kg/day amoxicillin component in 2 oral doses | RENDERED: Cephalexin 25-50 mg/kg/d in 3-4 divided doses po; Erythromycin 40 mg/kg/d in 3-4 divided doses po; Clindamycin 20 mg/kg/d in 3 divided doses po; Amoxicillin-clavulanate 25 mg/kg/d of the amoxicillin component in 2 divided doses po | idsa-2014 | 5 | p5/table2/pediatric-impetigo | table |
| table2-pediatric-doses | table2-mssa | nafcillin/oxacillin 100-150 mg/kg/day in 4 doses; cefazolin 50 mg/kg/day in 3 doses; clindamycin 25-40 mg/kg/day IV or 25-30 mg/kg/day oral in 3 doses; dicloxacillin 25-50 mg/kg/day in 4 oral doses; cephalexin 25-50 mg/kg/day in 4 oral doses; doxycycline/minocycline not recommended age <8 years; TMP-SMX 8-12 mg/kg/day TMP component in 4 IV or 2 oral doses | RENDERED: Nafcillin or oxacillin 100-150 mg/kg/d in 4 divided doses; Cefazolin 50 mg/kg/d in 3 divided doses; Clindamycin 25-40 mg/kg/d in 3 divided doses IV or 25-30 mg/kg/d in 3 divided doses po; Dicloxacillin 25-50 mg/kg/d in 4 divided doses po; Cephalexin 25-50 mg/kg/d in 4 divided doses po; Doxycycline, minocycline not recommended for age <8 y; TMP-SMX 8-12 mg/kg/d based on trimethoprim component in 4 divided doses IV or 2 divided doses po | idsa-2014 | 5 | p5/table2/pediatric-mssa | table |
| table2-pediatric-doses | table2-mrsa | vancomycin 40 mg/kg/day in 4 IV doses; linezolid 10 mg/kg every 12 hours IV/oral if <12 years; clindamycin 25-40 mg/kg/day IV or 30-40 mg/kg/day oral in 3 doses; doxycycline/minocycline not recommended age <8; TMP-SMX 8-12 mg/kg/day TMP component in 4 IV or 2 oral doses | RENDERED: Vancomycin 40 mg/kg/d in 4 divided doses IV; Linezolid 10 mg/kg every 12 h IV or po for children <12 y; Clindamycin 25-40 mg/kg/d in 3 divided doses IV or 30-40 mg/kg/d in 3 divided doses po; Doxycycline, minocycline not recommended for age <8 y; TMP-SMX 8-12 mg/kg/d based on trimethoprim component in 4 divided doses IV or 2 divided doses po | idsa-2014 | 5 | p5/table2/pediatric-mrsa | table |
| table2-pediatric-doses | table2-streptococcal | penicillin 60 000-100 000 units/kg/dose every 6 hours IV; clindamycin 10-13 mg/kg/dose every 8 hours IV; nafcillin 50 mg/kg/dose every 6 hours IV; cefazolin 33 mg/kg/dose every 8 hours IV | RENDERED: Penicillin 60-100 000 units/kg/dose every 6 h IV; Clindamycin 10-13 mg/kg dose every 8 h IV; Nafcillin 50 mg/kg/dose every 6 h; Cefazolin 33 mg/kg/dose every 8 h IV | idsa-2014 | 6 | p6/table2/pediatric-streptococcal | table |
| table2-neonatal-boundary | table2-impetigo | listed pediatric doses are not appropriate for neonates; use the AAP neonatal-dose source | RENDERED: Doses listed are not appropriate for neonates. Refer to the report by the Committee on Infectious Diseases, American Academy of Pediatrics, for neonatal doses | idsa-2014 | 6 | p6/table2/footnote-a | table |
| table2-impetigo-footnote | table2-impetigo | treat for 7 days depending on clinical response | RENDERED: Infection due to Staphylococcus and Streptococcus species. Duration of therapy is 7 days, depending on the clinical response | idsa-2014 | 6 | p6/table2/footnote-b | table |
| table2-erythromycin | table2-impetigo | erythromycin ethylsuccinate adult dose is 400 mg four times daily oral; some S. aureus and S. pyogenes strains may be resistant | RENDERED: Adult dosage of erythromycin ethylsuccinate is 400 mg 4 times/d po; Some strains of Staphylococcus aureus and Streptococcus pyogenes may be resistant | idsa-2014 | 5 | p5/table2/erythromycin | table |
| table2-strep-allergy | table2-streptococcal | for severe penicillin hypersensitivity select clindamycin, vancomycin, linezolid, daptomycin, or telavancin; clindamycin resistance is below 1% but may be increasing in Asia | RENDERED: antimicrobial agents for patients with severe penicillin hypersensitivity: Clindamycin, vancomycin, linezolid, daptomycin, or telavancin. Clindamycin resistance is <1% but may be increasing in Asia | idsa-2014 | 6 | p6/table2/severe-penicillin-hypersensitivity | table |
| table2-qualifiers | table2-mssa | nafcillin/oxacillin is the parenteral drug of choice and inactive against MRSA; cefazolin is more convenient than nafcillin with less bone-marrow suppression and, like cephalexin, is for penicillin allergy except immediate hypersensitivity; dicloxacillin is the adult oral MSSA choice but is not used much in pediatrics; clindamycin has cross-resistance and inducible-resistance risk; doxycycline/minocycline is not recommended below age 8; TMP-SMX efficacy is poorly documented; daptomycin can cause myopathy | RENDERED: Parenteral drug of choice; inactive against MRSA; For penicillin-allergic patients except those with immediate hypersensitivity reactions; More convenient than nafcillin with less bone marrow suppression; Oral agent of choice for methicillin-susceptible strains in adults. Not used much in pediatrics; potential of cross-resistance and emergence of resistance in erythromycin-resistant strains; inducible resistance in MRSA; Not recommended for age <8 y; efficacy poorly documented; possible myopathy | idsa-2014 | 5 | p5/table2/mssa-selection-qualifiers | table |
| table2-qualifiers | table2-mrsa | vancomycin is the parenteral drug of choice for MRSA in penicillin-allergic patients; linezolid has no cross-resistance with other antibiotic classes; clindamycin has cross-resistance and inducible-resistance risk; daptomycin can cause myopathy | RENDERED: For penicillin allergic patients; parenteral drug of choice for treatment of infections caused by MRSA; Linezolid no cross-resistance with other antibiotic classes; Clindamycin potential of cross-resistance and emergence of resistance in erythromycin-resistant strains, inducible resistance in MRSA; Daptomycin possible myopathy | idsa-2014 | 5 | p5/table2/mrsa-selection-qualifiers | table |
| table3-combination-doses | intestinal-gu-ssi | ceftriaxone 1 g every 24 hours plus metronidazole 500 mg every 8 hours IV; ciprofloxacin 400 mg IV or 750 mg oral every 12 hours plus metronidazole 500 mg every 8 hours; levofloxacin 750 mg every 24 hours plus metronidazole 500 mg every 8 hours; ampicillin-sulbactam 3 g every 6 hours plus gentamicin or tobramycin 5 mg/kg every 24 hours IV | RENDERED: Ceftriaxone 1 g every 24 h plus metronidazole 500 mg every 8 h IV; Ciprofloxacin 400 mg IV every 12 h or 750 mg po every 12 h plus metronidazole 500 mg every 8 h IV; Levofloxacin 750 mg IV every 24 h plus metronidazole 500 mg every 8 h IV; Ampicillin-sulbactam 3 g every 6 h plus gentamicin or tobramycin 5 mg/kg every 24 h IV | idsa-2014 | 19 | p19/table3/combinations | table |
| table3-mrsa-footnote | axilla-perineum-ssi | if MRSA present or suspected, add vancomycin 15 mg/kg every 12 hours | RENDERED: May also need to cover for methicillin-resistant Staphylococcus aureus with vancomycin 15 mg/kg every 12 h | idsa-2014 | 19 | p19/table3/footnote-a | table |
| table4-pediatric-doses | table4-mixed | piperacillin 60-75 mg/kg/dose every 6 hours plus vancomycin 10-13 mg/kg/dose every 8 hours; meropenem 20 mg/kg/dose every 8 hours; ertapenem 15 mg/kg/dose every 12 hours age 3 months-12 years; cefotaxime 50 mg/kg/dose every 6 hours plus metronidazole 7.5 mg/kg/dose every 6 hours or clindamycin 10-13 mg/kg/dose every 8 hours | RENDERED: 60-75 mg/kg/dose of the piperacillin component every 6 h IV; vancomycin 10-13 mg/kg/dose every 8 h IV; meropenem 20 mg/kg/dose every 8 h IV; ertapenem 15 mg/kg/dose every 12 h IV for children 3 mo-12 y; cefotaxime 50 mg/kg/dose every 6 h IV plus metronidazole 7.5 mg/kg/dose every 6 h IV or clindamycin 10-13 mg/kg/dose every 8 h IV | idsa-2014 | 20 | p20/table4/pediatric-mixed | table |
| table4-pediatric-doses | table4-strep | penicillin 60 000-100 000 units/kg/dose every 6 hours IV plus clindamycin 10-13 mg/kg/dose every 8 hours IV | RENDERED: 60 000-100 000 units/kg/dose every 6 h IV; 10-13 mg/kg/dose every 8 h IV | idsa-2014 | 20 | p20/table4/pediatric-strep | table |
| table4-pediatric-doses | table4-staph | nafcillin or oxacillin 50 mg/kg/dose every 6 hours IV; cefazolin 33 mg/kg/dose every 8 hours IV; resistant strains vancomycin 15 mg/kg/dose every 6 hours IV; clindamycin 10-13 mg/kg/dose every 8 hours IV | RENDERED: Nafcillin 50 mg/kg/dose every 6 h IV; Oxacillin 50 mg/kg/dose every 6 h IV; Cefazolin 33 mg/kg/dose every 8 h IV; Vancomycin for resistant strains 15 mg/kg/dose every 6 h IV; Clindamycin 10-13 mg/kg/dose every 8 h IV | idsa-2014 | 20 | p20/table4/pediatric-staph | table |
| table4-pediatric-water-boundary | table4-aeromonas-vibrio | doxycycline-containing Aeromonas and Vibrio regimens are not recommended for children but may be needed in life-threatening situations | RENDERED: Not recommended for children but may need to use in life-threatening situations | idsa-2014 | 20 | p20/table4/pediatric-water-boundary | table |
| table4-clostridial-doses | documented-gas | clindamycin 600-900 mg every 8 hours IV plus penicillin 2-4 million units every 4-6 hours IV; pediatric clindamycin 10-13 mg/kg/dose every 8 hours plus penicillin 60 000-100 000 units/kg/dose every 6 hours | RENDERED: Clostridium species Clindamycin 600-900 mg every 8 h IV plus penicillin 2-4 million units every 4-6 h IV; 10-13 mg/kg/dose every 8 h IV plus 60 000-100 000 units/kg/dose every 6 h IV | idsa-2014 | 20 | p20/table4/clostridial-doses | table |
| table4-mixed-severe-allergy | table4-mixed | with severe penicillin hypersensitivity use clindamycin or metronidazole plus an aminoglycoside or fluoroquinolone; add appropriate antistaphylococcal therapy when staphylococci are present or suspected | RENDERED: severe penicillin hypersensitivity: clindamycin or metronidazole with an aminoglycoside or fluoroquinolone; If staphylococcus present or suspected, add an appropriate agent | idsa-2014 | 20 | p20/table4/mixed-severe-penicillin-hypersensitivity | table |
| table4-strep-staph-allergy | table4-strep | severe-allergy alternatives are vancomycin, linezolid, quinupristin-dalfopristin, or daptomycin | RENDERED: Vancomycin, linezolid, quinupristin/dalfopristin, daptomycin | idsa-2014 | 20 | p20/table4/streptococcal-allergy | table |
| table4-strep-staph-allergy | table4-staph | severe-allergy or resistant-staphylococcal alternatives are vancomycin, linezolid, quinupristin-dalfopristin, or daptomycin | RENDERED: Vancomycin, linezolid, quinupristin/dalfopristin, daptomycin | idsa-2014 | 20 | p20/table4/staphylococcal-allergy | table |
| table4-mrsa-footnote | table4-staph | if MRSA is present or suspected, add vancomycin without exceeding the maximum adult daily dose | RENDERED: If MRSA is present or suspected, add vancomycin not to exceed the maximum adult daily dose | idsa-2014 | 20 | p20/table4/footnote-b | table |
| table5-complete-animal | animal-human-bite | animal bite: piperacillin-tazobactam 3.37 g every 6-8 hours; carbapenem per individual information; doxycycline 100 mg twice daily oral or every 12 hours IV; penicillin plus dicloxacillin 500 mg/500 mg four times daily; TMP-SMX 160-800 mg twice daily oral or 5-10 mg/kg/day TMP IV; metronidazole 250-500 mg three times daily oral or 500 mg every 8 hours IV; clindamycin 300 mg three times daily oral or 600 mg every 6-8 hours IV; cefoxitin 1 g every 6-8 hours; ceftriaxone 1 g every 12 hours; cefotaxime 1-2 g every 6-8 hours; ciprofloxacin 500-750 mg twice daily oral or 400 mg every 12 hours IV; levofloxacin 750 mg daily; moxifloxacin 400 mg daily | RENDERED: Animal bite piperacillin-tazobactam 3.37 g every 6-8 h; carbapenems see individual information; doxycycline 100 mg bid or every 12 h; penicillin plus dicloxacillin 500 mg qid/500 mg qid; TMP-SMX 160-800 mg bid or 5-10 mg/kg/day TMP; metronidazole 250-500 mg tid or 500 mg every 8 h; clindamycin 300 mg tid or 600 mg every 6-8 h; cefoxitin 1 g every 6-8 h; ceftriaxone 1 g every 12 h; cefotaxime 1-2 g every 6-8 h; ciprofloxacin 500-750 mg bid or 400 mg every 12 h; levofloxacin 750 mg daily; moxifloxacin 400 mg daily | idsa-2014 | 25 | p25/table5/animal-complete | table |
| table5-complete-human | animal-human-bite | human bite: amoxicillin-clavulanate or ampicillin-sulbactam; ertapenem; beta-lactam allergy ciprofloxacin or levofloxacin plus metronidazole, or moxifloxacin alone; doxycycline 100 mg twice daily | RENDERED: Human bite Amoxicillin-clavulanate 875/125 mg bid; Ampicillin-sulbactam 1.5-3.0 g every 6 h; Carbapenems; Doxycycline 100 mg bid; fluoroquinolone such as ciprofloxacin or levofloxacin plus metronidazole, or moxifloxacin as a single agent; ertapenem | idsa-2014 | 25 | p25/table5/human-complete | table |
| table5-coverage-qualifiers | animal-human-bite | amoxicillin-clavulanate and ampicillin-sulbactam have some resistant gram-negative rods and miss MRSA; piperacillin-tazobactam and carbapenems miss MRSA; doxycycline is excellent for Pasteurella but some streptococci resist it; TMP-SMX misses anaerobes; metronidazole misses aerobes; clindamycin misses Pasteurella; cefuroxime misses anaerobes; fluoroquinolones miss MRSA and some anaerobes, while moxifloxacin also covers anaerobes; human-bite doxycycline covers Eikenella, staphylococci, and anaerobes but some streptococci resist it | RENDERED: Some gram-negative rods are resistant; misses MRSA; Excellent activity against Pasteurella multocida; some streptococci are resistant; Good activity against aerobes; poor activity against anaerobes; Good activity against anaerobes; no activity against aerobes; misses P. multocida; misses anaerobes; misses MRSA and some anaerobes; Monotherapy; good for anaerobes also; Good activity against Eikenella species, staphylococci, and anaerobes; some streptococci are resistant | idsa-2014 | 25 | p25/table5/coverage-qualifiers | table |
| table6-qualifiers | persistent-neutropenic-ssti | fluconazole misses C. krusei and C. glabrata; IV voriconazole cyclodextrin accumulates with renal insufficiency and patient-specific PK is recommended; posaconazole covers Mucorales; lipid-complex and liposomal amphotericin B are not active against Fusarium | RENDERED: Candida krusei and Candida glabrata are resistant; Accumulation of cyclodextrin vehicle with IV formulation with renal insufficiency; Covers Mucorales; Not active against fusaria; patient-specific pharmacokinetics is recommended | idsa-2014 | 32 | p32/table6/qualifiers | table |
| table7-qualifiers | resistant-ssti | daptomycin covers VRE but vancomycin-nonsusceptible strains may be cross-resistant; linezolid has 100% oral bioavailability and covers VRE/MRSA; colistin is nephrotoxic and misses gram-positive bacteria, anaerobes, Proteus, Serratia, and Burkholderia | RENDERED: Daptomycin covers VRE, strains nonsusceptible to vancomycin may be cross-resistant to daptomycin; Linezolid 100% oral bioavailability, oral dose same as IV dose, covers VRE and MRSA; Colistin nephrotoxic, does not cover gram-positives or anaerobes, Proteus, Serratia, Burkholderia | idsa-2014 | 33 | p33/table7/qualifiers | table |
| tetanus-dirty-window | dirty-major-wound | booster if >5 years since last dose | RENDERED: booster dose of tetanus toxoid vaccine should be administered for dirty wounds if >5 years has elapsed since the last dose | idsa-2014 | 25 | p25/narrative/tetanus-dirty | narrative |
| tetanus-clean-window | clean-minor-wound | booster if >10 years since last dose | RENDERED: For clean, minor wounds, vaccination is recommended only if >10 years have elapsed since the last dose | idsa-2014 | 25 | p25/narrative/tetanus-clean | narrative |
| anthrax-diagnostic-action | cutaneous-anthrax-diagnostic | collect vesicle fluid by sterile swab or material beneath eschar edge for Gram stain and culture; punch biopsy may be submitted for culture and histopathology | RENDERED: vesicle may be unroofed and 2 dry swabs soaked in the fluid; in the ulcer stage, the lesion should be sampled with a moist swab rotated beneath the edge of the eschar; a full-thickness punch biopsy specimen should be obtained for culture and histopathology | idsa-2014 | 26 | p26/narrative/anthrax-diagnosis | narrative |
| tularemia-adult-dose | tularemia-adult | streptomycin 30 mg/kg/day in 2 doses, max 2 g/day, or gentamicin 1.5 mg/kg every 8 hours with renal adjustment | RENDERED: For adults, the regimen for streptomycin is 30 mg/kg/day in 2 divided doses (no more than 2 g daily) or gentamicin 1.5 mg/kg every 8 hours | idsa-2014 | 28 | p28/narrative/tularemia-adult | narrative |
| tularemia-child-dose | tularemia-child | streptomycin 30 mg/kg/day in 2 doses or gentamicin 6 mg/kg/day in 3 doses | RENDERED: For children, streptomycin should be administered at 30 mg/kg/day in 2 divided doses or gentamicin at 6 mg/kg/day in 3 divided doses | idsa-2014 | 29 | p29/narrative/tularemia-child | narrative |
| cat-scratch-evidence-dose | cat-scratch-evidence-heavy | azithromycin 500 mg day 1 then 250 mg daily for 4 additional days | RENDERED: recommended dose of azithromycin for patients weighing ≥45.5 kg (100 lb) is 500 mg on day 1, then 250 mg once daily for 4 additional days | idsa-2014 | 27 | p27/narrative/cat-scratch-evidence-heavy | narrative |
| cat-scratch-evidence-dose | cat-scratch-evidence-light | azithromycin 10 mg/kg day 1 then 5 mg/kg days 2-5 | RENDERED: those weighing <45.5 kg, the dose is 10 mg/kg orally on day 1, then 5 mg/kg on days 2-5 | idsa-2014 | 27 | p27/narrative/cat-scratch-evidence-light | narrative |
| figure2-routing | systemic-ssi | for anaphylaxis or hives from beta-lactams use the printed surgical-site-algorithm allergy route; if Gram stain is unavailable, open and debride when purulent drainage is present; where MRSA rates are high, consider vancomycin, daptomycin, or linezolid pending culture and susceptibility | RENDERED: For patients with type 1 (anaphylaxis or hives) allergy to beta-lactam antibiotics. If Gram stain not available, open and debride if purulent drainage present. Where the rate of infection with MRSA is high, consider vancomycin, daptomycin, or linezolid, pending results of culture and susceptibility tests | idsa-2014 | 3 | p3/figure2/footnote | figure |
| neutropenic-blood-cultures | fever-neutropenia | obtain at least 2 sets of blood cultures | RENDERED: Blood cultures are critical, and at least 2 sets should be obtained | idsa-2014 | 30 | p30/narrative/blood-culture-sets | narrative |
| low-risk-neutropenic-oral-regimen | low-risk-neutropenic-oral | prefer oral ciprofloxacin plus amoxicillin-clavulanate | RENDERED: The combination of ciprofloxacin and amoxicillin-clavulanate is the preferred oral antibiotic regimen for low-risk patients | idsa-2014 | 32 | p32/narrative/low-risk-oral | narrative |
| fluoroquinolone-prophylaxis-boundary | fluoroquinolone-prophylaxis | do not use a fluoroquinolone for empiric therapy; consider a broad-spectrum beta-lactam instead | RENDERED: Fluoroquinolone prophylaxis should preclude the use of fluoroquinolones for empiric therapy, and instead broad-spectrum beta-lactam antibiotics should be considered | idsa-2014 | 32 | p32/narrative/fluoroquinolone-prophylaxis | narrative |
| linezolid-neutropenia-harm | fever-neutropenia | linezolid has been associated with delayed ANC recovery | RENDERED: The use of linezolid in this patient population has been associated with delayed ANC recovery | idsa-2014 | 32 | p32/narrative/linezolid-anc | narrative |
| ntm-debridement | ntm-ssti | debride to obtain cultures and susceptibilities, remove devitalized tissue, and promote healing, in addition to prolonged combination therapy | RENDERED: Surgical debridement is crucial for cultures and sensitivities and in addition is necessary to remove devitalized tissue and to promote skin and soft tissue healing | idsa-2014 | 34 | p34/narrative/ntm-debridement | narrative |
| nocardia-treatment | nocardia-ssti | use SMX-TMP as treatment of choice; consider combination therapy for severe infection or profound lasting immunodeficiency; debride necrotic nodules or large subcutaneous abscesses; treat 6-24 months according to dissemination and immunosuppression | RENDERED: SMX-TMP remains the treatment of choice; Combination therapy with other agents should be considered in patients with severe infections or profound and lasting immunodeficiency; duration of treatment 6-24 months; Surgical debridement is recommended for necrotic nodules or large subcutaneous abscesses | idsa-2014 | 35 | p35/narrative/nocardia-treatment | narrative |
| cutaneous-mold-management | cutaneous-mold | perform skin biopsy; consider complete resection or debulking for a single or localized lesion; use voriconazole for Aspergillus, Scedosporium apiospermum, or Fusarium, with amphotericin B as an alternative and posaconazole with amphotericin B or as oral transition | RENDERED: Skin biopsy should be performed for diagnostic purposes and resection of the entire lesion or debulking procedures should be considered in cases where there is either a single lesion or localized disease; voriconazole is the best therapeutic option; Amphotericin B is an excellent alternative; Posaconazole is also a reasonable alternative in combination with amphotericin B or as a transition to oral therapy | idsa-2014 | 35 | p35/narrative/cutaneous-mold | narrative |
| cryptococcal-management | cryptococcal-ssti | use fluconazole for mild infection or after amphotericin B plus flucytosine induction improvement; do not use surgical debridement or drainage | RENDERED: Fluconazole is often used as initial treatment, for patients with mild infections, or to complete treatment after the patient has shown clinical and microbiologic improvement with amphotericin B and 5-flucytosine induction therapy; Surgical debridement and/or drainage are not helpful | idsa-2014 | 35 | p35/narrative/cryptococcal-management | narrative |
| histoplasma-suppression | disseminated-histoplasmosis | after completing the initial amphotericin B-to-itraconazole treatment course, continue long-term itraconazole suppression when immunosuppression is profound and prolonged | RENDERED: Patients with illnesses that result in profound and prolonged immune suppression should receive long-term suppressive therapy with itraconazole after the initial treatment course is complete | idsa-2014 | 35 | p35/narrative/histoplasma-suppression | narrative |
| vzv-treatment | vzv-ssti | use high-dose IV acyclovir in compromised hosts; reserve oral acyclovir, famciclovir, or valacyclovir for mild disease with transient immunosuppression or completion after IV response; investigate resistance if lesions develop during prophylaxis | RENDERED: High-dose IV acyclovir remains the treatment of choice for VZV infections in compromised hosts; oral therapy should be reserved for mild cases of VZV disease in patients with transient immune suppression or as treatment to complete therapy once the patient has shown a clinical response to IV acyclovir; antiviral resistance should be investigated | idsa-2014 | 36 | p36/narrative/vzv-treatment | narrative |
| hsv-treatment | hsv-ssti | use acyclovir; famciclovir and valacyclovir are alternatives; suppress reactivation or continue until lesions heal; use prolonged IV foscarnet for acyclovir resistance, with continuous high-dose acyclovir reported in HSCT; avoid surgery unless a bacterial or fungal abscess is documented | RENDERED: Acyclovir is the treatment of choice for HSV infections, although famciclovir and valacyclovir are also highly effective; Suppression of HSV reactivation or continued treatment until the ulcerated skin or mucosal lesions have totally healed; acyclovir-resistant HSV isolates requires a prolonged course of intravenous foscarnet; continuous infusion of high-doses of acyclovir has been reported to be successful in HSCT patients; Surgery should be avoided unless a documented bacterial or fungal abscess is identified | idsa-2014 | 36 | p36/narrative/hsv-treatment | narrative |
| action-p12-1 | table2-impetigo | Gram stain and culture of pus or exudate is recommended to identify S. aureus and/or beta-hemolytic Streptococcus | RENDERED: Gram stain and culture of the pus or exudates from skin lesions of impetigo and ecthyma are recommended to help identify whether Staphylococcus aureus and/or a beta-hemolytic Streptococcus is the cause | idsa-2014 | 12 | p12/grade-terse/1 | recommendation |
| action-p12-2 | table2-impetigo | Gram stain and culture is recommended, but treatment without these studies is reasonable in typical cases | RENDERED: Gram stain and culture of the pus or exudates from skin lesions of impetigo and ecthyma are recommended, but treatment without these studies is reasonable in typical cases | idsa-2014 | 12 | p12/grade-terse/2 | recommendation |
| action-p12-3 | table2-impetigo | Treatment for ecthyma should be an oral antimicrobial. (a) Treatment of bullous and nonbullous impetigo should be with either topical mupirocin or retapamulin twice daily (bid) for 5 days (strong, high) | Treatment for ecthyma should be an oral antimicrobial. (a) Treatment of bullous and nonbullous impetigo should be with either topical mupirocin or retapamulin twice daily (bid) for 5 days (strong, high) | idsa-2014 | 12 | p12/grade-terse/3 | recommendation |
| action-p12-4 | table2-impetigo | use oral therapy for numerous lesions, outbreaks, and ecthyma; topical mupirocin or retapamulin twice daily for 5 days for limited impetigo; use 7 days of an agent active against S. aureus, or penicillin if streptococci alone; prefer dicloxacillin or cephalexin for usual MSSA | RENDERED: Bullous and nonbullous impetigo can be treated with oral or topical antimicrobials, but oral therapy is recommended for patients with numerous lesions or in outbreaks; Treatment for ecthyma should be an oral antimicrobial; mupirocin or retapamulin twice daily for 5 days; Oral therapy for ecthyma or impetigo should be a 7-day regimen with an agent active against S. aureus unless cultures yield streptococci alone; dicloxacillin or cephalexin is recommended | idsa-2014 | 12 | p12/grade-terse/4 | recommendation |
| action-p12-5 | table2-impetigo | When MRSA is suspected or conﬁrmed, doxycycline, clindamycin, or sulfamethoxazole-trimethoprim (SMX-TMP) is recom- mended (strong, moderate) | When MRSA is suspected or conﬁrmed, doxycycline, clindamycin, or sulfamethoxazole-trimethoprim (SMX-TMP) is recom- mended (strong, moderate) | idsa-2014 | 12 | p12/grade-terse/5 | recommendation |
| action-p12-6 | table2-impetigo | when MRSA is suspected or confirmed use doxycycline, clindamycin, or SMX-TMP; use systemic antimicrobials during poststreptococcal-glomerulonephritis outbreaks to eliminate nephritogenic S. pyogenes strains | RENDERED: When MRSA is suspected or confirmed, doxycycline, clindamycin, or SMX-TMP is recommended; Systemic antimicrobials should be used for infections during outbreaks of poststreptococcal glomerulonephritis to help eliminate nephritogenic strains of S. pyogenes from the community | idsa-2014 | 12 | p12/grade-terse/6 | recommendation |
| action-p13-1 | purulent-moderate | Gram stain and culture of pus from carbuncles and ab- scesses are recommended, but treatment without these studies is reasonable in typical cases (strong, moderate) | Gram stain and culture of pus from carbuncles and ab- scesses are recommended, but treatment without these studies is reasonable in typical cases (strong, moderate) | idsa-2014 | 13 | p13/grade-terse/1 | recommendation |
| action-p13-2 | purulent-moderate | Gram stain and culture of pus from inﬂamed epidermoid cysts are not recommended (strong, moderate) | Gram stain and culture of pus from inﬂamed epidermoid cysts are not recommended (strong, moderate) | idsa-2014 | 13 | p13/grade-terse/2 | recommendation |
| action-p13-3 | purulent-moderate | Incision and drainage is the recommended treatment for inﬂamed epidermoid cysts, carbuncles, abscesses, and large fu- runcles (strong, high) | Incision and drainage is the recommended treatment for inﬂamed epidermoid cysts, carbuncles, abscesses, and large fu- runcles (strong, high) | idsa-2014 | 13 | p13/grade-terse/3 | recommendation |
| action-p13-4 | purulent-moderate | The decision to administer antibiotics directed against S. aureus as an adjunct to incision and drainage should be made based on the presence or absence of systemic inﬂam- matory response syndrome (SIRS) | The decision to administer antibiotics directed against S. aureus as an adjunct to incision and drainage should be made based on the presence or absence of systemic inﬂam- matory response syndrome (SIRS) | idsa-2014 | 13 | p13/grade-terse/4 | recommendation |
| action-p13-5 | purulent-severe | use an MRSA-active antibiotic after failed initial antibiotic treatment, with markedly impaired defenses, or with SIRS and hypotension | RENDERED: An antibiotic active against MRSA is recommended for patients with carbuncles or abscesses who have failed initial antibiotic treatment or have markedly impaired host defenses or in patients with SIRS and hypotension | idsa-2014 | 13 | p13/grade-terse/5 | recommendation |
| action-p14-1 | all-ssti-hosts | A recurrent abscess at a site of previous infection should prompt a search for local causes such as a pilonidal cyst, hidra- denitis suppurativa, or foreign material (strong, moderate) | A recurrent abscess at a site of previous infection should prompt a search for local causes such as a pilonidal cyst, hidra- denitis suppurativa, or foreign material (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/1 | recommendation |
| action-p14-2 | all-ssti-hosts | Recurrent abscesses should be drained and cultured early in the course of infection (strong, moderate) | Recurrent abscesses should be drained and cultured early in the course of infection (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/2 | recommendation |
| action-p14-3 | all-ssti-hosts | Culture recurrent abscess and treat with a 5- to 10-day course of an antibiotic active against the pathogen isolated (weak, low) | Culture recurrent abscess and treat with a 5- to 10-day course of an antibiotic active against the pathogen isolated (weak, low) | idsa-2014 | 14 | p14/grade-terse/3 | recommendation |
| action-p14-4 | recurrent-abscess | consider 5-day decolonization with intranasal mupirocin twice daily, daily chlorhexidine washes, and daily decontamination of towels, sheets, and clothes for recurrent S. aureus | RENDERED: Consider a 5-day decolonization regimen twice daily of intranasal mupirocin, daily chlorhexidine washes, and daily decontamination of personal items such as towels, sheets, and clothes for recurrent S. aureus infection | idsa-2014 | 14 | p14/grade-terse/4 | recommendation |
| action-p14-5 | all-ssti-hosts | Adult patients should be evaluated for neutrophil disor- ders if recurrent abscesses began in early childhood (strong, moderate) | Adult patients should be evaluated for neutrophil disor- ders if recurrent abscesses began in early childhood (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/5 | recommendation |
| action-p14-6 | all-ssti-hosts | Cultures of blood or cutaneous aspirates, biopsies, or swabs are not routinely recommended (strong, moderate) | Cultures of blood or cutaneous aspirates, biopsies, or swabs are not routinely recommended (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/6 | recommendation |
| action-p14-7 | all-ssti-hosts | Cultures of blood are recommended (strong, moderate) | Cultures of blood are recommended (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/7 | recommendation |
| action-p14-8 | cellular-immunodeficiency | obtain blood cultures and consider cultures plus microscopic examination of cutaneous aspirates, biopsies, or swabs with malignancy on chemotherapy, neutropenia, severe cell-mediated immunodeficiency, immersion injury, or animal bite | RENDERED: Cultures of blood are recommended, and cultures and microscopic examination of cutaneous aspirates, biopsies, or swabs should be considered in patients with malignancy on chemotherapy, neutropenia, severe cell-mediated immunodeficiency, immersion injuries, and animal bites | idsa-2014 | 14 | p14/grade-terse/8 | recommendation |
| action-p14-9 | all-ssti-hosts | Typical cases of cellulitis without systemic signs of infec- tion should receive an antimicrobial agent that is active against streptococci (mild; Figure 1) (strong, moderate) | Typical cases of cellulitis without systemic signs of infec- tion should receive an antimicrobial agent that is active against streptococci (mild; Figure 1) (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/9 | recommendation |
| action-p14-10 | typical-cellulitis | for systemic signs use systemic antibiotics and optionally cover MSSA; with penetrating trauma, MRSA elsewhere, nasal MRSA colonization, injection drug use, or SIRS, use vancomycin or another agent active against MRSA and streptococci | RENDERED: For cellulitis with systemic signs of infection, systemic antibiotics are indicated. Many clinicians could include coverage against MSSA. For cellulitis associated with penetrating trauma, evidence of MRSA infection elsewhere, nasal colonization with MRSA, injection drug use, or SIRS, vancomycin or another antimicrobial effective against both MRSA and streptococci is recommended | idsa-2014 | 14 | p14/grade-terse/10 | recommendation |
| action-p14-11 | all-ssti-hosts | In severely compromised patients (as deﬁned in question 13), broad-spectrum antimicrobial coverage may be considered (weak, moderate) | In severely compromised patients (as deﬁned in question 13), broad-spectrum antimicrobial coverage may be considered (weak, moderate) | idsa-2014 | 14 | p14/grade-terse/11 | recommendation |
| action-p14-12 | all-ssti-hosts | Vancomycin plus either piperacillin-tazobac- tam or imipenem-meropenem is recommended as a reasonable empiric regimen for severe infection (strong, moderate) | Vancomycin plus either piperacillin-tazobac- tam or imipenem-meropenem is recommended as a reasonable empiric regimen for severe infection (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/12 | recommendation |
| action-p14-13 | all-ssti-hosts | The recommended duration of antimicrobial therapy is 5 days, but treatment should be extended if the infection has not improved within this time period (strong, high) | The recommended duration of antimicrobial therapy is 5 days, but treatment should be extended if the infection has not improved within this time period (strong, high) | idsa-2014 | 14 | p14/grade-terse/13 | recommendation |
| action-p14-14 | all-ssti-hosts | Elevation of the affected area and treatment of predispos- ing factors, such as edema or underlying cutaneous disorders, are recommended (strong, moderate) | Elevation of the affected area and treatment of predispos- ing factors, such as edema or underlying cutaneous disorders, are recommended (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/14 | recommendation |
| action-p14-15 | typical-cellulitis | examine interdigital toe spaces in lower-extremity cellulitis and treat fissuring, scaling, or maceration to reduce colonization and recurrence | RENDERED: In lower-extremity cellulitis, clinicians should carefully examine the interdigital toe spaces because treating fissuring, scaling, or maceration may eradicate colonization with pathogens and reduce the incidence of recurrent infection | idsa-2014 | 14 | p14/grade-terse/15 | recommendation |
| action-p14-16 | all-ssti-hosts | Outpatient therapy is recommended for patients who do not have SIRS, altered mental status, or hemodynamic instabil- ity (mild nonpurulent; Figure 1) (strong, moderate) | Outpatient therapy is recommended for patients who do not have SIRS, altered mental status, or hemodynamic instabil- ity (mild nonpurulent; Figure 1) (strong, moderate) | idsa-2014 | 14 | p14/grade-terse/16 | recommendation |
| action-p15-1 | severe-cellulitis | hospitalize for concern for deeper or necrotizing infection, poor adherence, severe immunocompromise, or failed outpatient treatment | RENDERED: Hospitalization is recommended if there is concern for a deeper or necrotizing infection, for patients with poor adherence to therapy, for infection in a severely immunocompromised patient, or if outpatient treatment is failing | idsa-2014 | 15 | p15/grade-terse/1 | recommendation |
| action-p16-1 | recurrent-cellulitis | Systemic corticosteroids (eg, prednisone 40 mg daily for 7 days) could be considered in nondiabetic adult patients with cellulitis (weak, moderate) | Systemic corticosteroids (eg, prednisone 40 mg daily for 7 days) could be considered in nondiabetic adult patients with cellulitis (weak, moderate) | idsa-2014 | 16 | p16/grade-terse/1 | recommendation |
| action-p16-2 | recurrent-cellulitis | Identify and treat predisposing conditions such as edema, obesity, eczema, venous insufﬁciency, and toe web ab- normalities (strong, moderate) | Identify and treat predisposing conditions such as edema, obesity, eczema, venous insufﬁciency, and toe web ab- normalities (strong, moderate) | idsa-2014 | 16 | p16/grade-terse/2 | recommendation |
| action-p16-3 | recurrent-cellulitis | These practices should be per- formed as part of routine patient care and certainly during the acute stage of cellulitis (strong, moderate) | These practices should be per- formed as part of routine patient care and certainly during the acute stage of cellulitis (strong, moderate) | idsa-2014 | 16 | p16/grade-terse/3 | recommendation |
| action-p16-4 | recurrent-cellulitis | after 3-4 episodes yearly despite risk-factor control, consider oral penicillin or erythromycin twice daily for 4-52 weeks or benzathine penicillin IM every 2-4 weeks; continue while predisposing factors persist | RENDERED: Administration of prophylactic antibiotics, such as oral penicillin or erythromycin bid for 4-52 weeks, or intramuscular benzathine penicillin every 2-4 weeks, should be considered in patients who have 3-4 episodes of cellulitis per year despite attempts to treat or control predisposing factors; This program should be continued so long as the predisposing factors persist | idsa-2014 | 16 | p16/grade-terse/4 | recommendation |
| action-p17-1 | systemic-ssi | Suture removal plus incision and drainage should be per- formed for surgical site infections (strong, low) | Suture removal plus incision and drainage should be per- formed for surgical site infections (strong, low) | idsa-2014 | 17 | p17/grade-terse/1 | recommendation |
| action-p17-2 | systemic-ssi | Adjunctive systemic antimicrobial therapy is not routine- ly indicated, but in conjunction with incision and drainage may be beneﬁcial for surgical site infections associated with a signiﬁ- cant systemic response (Figure 2) | Adjunctive systemic antimicrobial therapy is not routine- ly indicated, but in conjunction with incision and drainage may be beneﬁcial for surgical site infections associated with a signiﬁ- cant systemic response (Figure 2) | idsa-2014 | 17 | p17/grade-terse/2 | recommendation |
| action-p17-3 | systemic-ssi | give a brief systemic antimicrobial course after clean trunk, head/neck, or extremity operations when systemic signs are present | RENDERED: A brief course of systemic antimicrobial therapy is indicated in patients with surgical site infections following clean operations on the trunk, head and neck, or extremities that also have systemic signs of infection | idsa-2014 | 17 | p17/grade-terse/3 | recommendation |
| action-p17-4 | systemic-ssi | use a first-generation cephalosporin or antistaphylococcal penicillin for MSSA; when MRSA risk is high from colonization, prior infection, recent hospitalization, or recent antibiotics, use vancomycin, linezolid, daptomycin, telavancin, or ceftaroline | RENDERED: A first-generation cephalosporin or an antistaphylococcal penicillin for MSSA or vancomycin, linezolid, daptomycin, telavancin, or ceftaroline where risk factors for MRSA are high, including nasal colonization, prior MRSA infection, recent hospitalization, or recent antibiotics | idsa-2014 | 17 | p17/grade-terse/4 | recommendation |
| action-p17-5 | axilla-perineum-ssi | use gram-negative and anaerobic coverage, such as a cephalosporin or fluoroquinolone plus metronidazole, after axilla, GI, perineal, or female-genital-tract operations | RENDERED: Agents active against gram-negative bacteria and anaerobes, such as a cephalosporin or fluoroquinolone in combination with metronidazole are recommended for infections following operations on the axilla, gastrointestinal tract, perineum, or female genital tract | idsa-2014 | 17 | p17/grade-terse/5 | recommendation |
| action-p18-1 | necrotizing-infection | Prompt surgical consultation is recommended for pa- tients with aggressive infections associated with signs of system- ic toxicity or suspicion of necrotizing fasciitis or gas gangrene (severe nonpurulent; Figure 1) (strong, low) | Prompt surgical consultation is recommended for pa- tients with aggressive infections associated with signs of system- ic toxicity or suspicion of necrotizing fasciitis or gas gangrene (severe nonpurulent; Figure 1) (strong, low) | idsa-2014 | 18 | p18/grade-terse/1 | recommendation |
| action-p18-2 | necrotizing-infection | Empiric antibiotic treatment should be broad (eg, vanco- mycin or linezolid plus piperacillin-tazobactam or plus a carba- penem, or plus ceftriaxone and metronidazole), as the etiology can be polymicrobial (mixed aerobic-anaerobic microbes) | Empiric antibiotic treatment should be broad (eg, vanco- mycin or linezolid plus piperacillin-tazobactam or plus a carba- penem, or plus ceftriaxone and metronidazole), as the etiology can be polymicrobial (mixed aerobic-anaerobic microbes) | idsa-2014 | 18 | p18/grade-terse/2 | recommendation |
| action-p18-3 | necrotizing-infection | Penicillin plus clindamycin is recommended for treat- ment of documented group A streptococcal necrotizing fasciitis (strong, low) | Penicillin plus clindamycin is recommended for treat- ment of documented group A streptococcal necrotizing fasciitis (strong, low) | idsa-2014 | 18 | p18/grade-terse/3 | recommendation |
| action-p22-1 | pyomyositis | use MRI to establish pyomyositis; CT and ultrasound are also useful | RENDERED: Magnetic resonance imaging is the recommended imaging modality for establishing the diagnosis of pyomyositis. Computed tomography scan and ultrasound studies are also useful | idsa-2014 | 22 | p22/grade-terse/1 | recommendation |
| action-p22-2 | pyomyositis | Cultures of blood and abscess material should be ob- tained (strong, moderate) | Cultures of blood and abscess material should be ob- tained (strong, moderate) | idsa-2014 | 22 | p22/grade-terse/2 | recommendation |
| action-p22-3 | pyomyositis | use vancomycin initially; add enteric gram-negative coverage for immunocompromise or open muscle trauma | RENDERED: Vancomycin is recommended for initial empirical therapy. An agent active against enteric gram-negative bacilli should be added for infection in immunocompromised patients or following open trauma to the muscles | idsa-2014 | 22 | p22/grade-terse/3 | recommendation |
| action-p22-4 | pyomyositis | Cefazolin or antistaphylococcal penicillin (eg, nafcillin or oxacillin) is recommended for treatment of pyomyositis caused by MSSA (strong, moderate) | Cefazolin or antistaphylococcal penicillin (eg, nafcillin or oxacillin) is recommended for treatment of pyomyositis caused by MSSA (strong, moderate) | idsa-2014 | 22 | p22/grade-terse/4 | recommendation |
| action-p22-5 | pyomyositis | Early drainage of purulent material should be performed (strong, high) | Early drainage of purulent material should be performed (strong, high) | idsa-2014 | 22 | p22/grade-terse/5 | recommendation |
| action-p22-6 | pyomyositis | Repeat imaging studies should be performed in the pa- tient with persistent bacteremia to identify undrained foci of in- fection (strong, low) | Repeat imaging studies should be performed in the pa- tient with persistent bacteremia to identify undrained foci of in- fection (strong, low) | idsa-2014 | 22 | p22/grade-terse/6 | recommendation |
| action-p22-7 | pyomyositis | Two to 3 weeks of therapy is recommended (strong, low) | Two to 3 weeks of therapy is recommended (strong, low) | idsa-2014 | 22 | p22/grade-terse/7 | recommendation |
| action-p23-1 | documented-gas | Urgent surgical exploration of the suspected gas gangrene site and surgical debridement of involved tissue should be per- formed (severe nonpurulent; Figure 1) (strong, moderate) | Urgent surgical exploration of the suspected gas gangrene site and surgical debridement of involved tissue should be per- formed (severe nonpurulent; Figure 1) (strong, moderate) | idsa-2014 | 23 | p23/grade-terse/1 | recommendation |
| action-p23-2 | documented-gas | In the absence of a deﬁnitive etiologic diagnosis, broad- spectrum treatment with vancomycin plus either piperacillin- tazobactam, ampicillin-sulbactam, or a carbapenem antimicro- bial is recommended (strong, low) | In the absence of a deﬁnitive etiologic diagnosis, broad- spectrum treatment with vancomycin plus either piperacillin- tazobactam, ampicillin-sulbactam, or a carbapenem antimicro- bial is recommended (strong, low) | idsa-2014 | 23 | p23/grade-terse/2 | recommendation |
| action-p23-3 | documented-gas | Deﬁnitive antimicrobial therapy along with penicillin and clindamycin is recommended for treatment of clostridial myonecrosis (strong, low) | Deﬁnitive antimicrobial therapy along with penicillin and clindamycin is recommended for treatment of clostridial myonecrosis (strong, low) | idsa-2014 | 23 | p23/grade-terse/3 | recommendation |
| action-p23-4 | documented-gas | Hyperbaric oxygen (HBO) therapy is not recommended because it has not been proven as a beneﬁt to the patient and may delay resuscitation and surgical debridement (strong, low) | Hyperbaric oxygen (HBO) therapy is not recommended because it has not been proven as a beneﬁt to the patient and may delay resuscitation and surgical debridement (strong, low) | idsa-2014 | 23 | p23/grade-terse/4 | recommendation |
| action-p24-1 | animal-bite-high-risk | give preemptive antimicrobials for 3-5 days with immunocompromise, asplenia, advanced liver disease, local edema, moderate-severe hand or face injury, or possible periosteal or joint-capsule penetration | RENDERED: Preemptive early antimicrobial therapy for 3-5 days is recommended for patients who are immunocompromised, are asplenic, have advanced liver disease, have preexisting or resultant edema, have moderate to severe injuries especially to the hand or face, or have injuries that may have penetrated the periosteum or joint capsule | idsa-2014 | 24 | p24/grade-terse/1 | recommendation |
| action-p24-2 | animal-bite-high-risk | Postexposure prophylaxis for rabies may be indicated; consultation with local health ofﬁcials is recommended to de- termine if vaccination should be initiated (strong, low) | Postexposure prophylaxis for rabies may be indicated; consultation with local health ofﬁcials is recommended to de- termine if vaccination should be initiated (strong, low) | idsa-2014 | 24 | p24/grade-terse/2 | recommendation |
| action-p24-3 | animal-bite-high-risk | An antimicrobial agent or agents active against both aer- obic and anaerobic bacteria such as amoxicillin-clavulanate (Table 5) should be used (strong, moderate) | An antimicrobial agent or agents active against both aer- obic and anaerobic bacteria such as amoxicillin-clavulanate (Table 5) should be used (strong, moderate) | idsa-2014 | 24 | p24/grade-terse/3 | recommendation |
| action-p25-1 | no-recent-tetanus | administer tetanus toxoid when no toxoid vaccination occurred within 10 years; prefer Tdap over Td if Tdap was never given | RENDERED: Tetanus toxoid should be administered to patients without toxoid vaccination within 10 years. Tdap is preferred over Td if the former has not been previously given | idsa-2014 | 25 | p25/grade-terse/1 | recommendation |
| action-p26-1 | all-ssti-hosts | Primary wound closure is not recommended for wounds with the exception of those to the face, which should be man- aged with copious irrigation, cautious debridement, and pre- emptive antibiotics (strong, low) | Primary wound closure is not recommended for wounds with the exception of those to the face, which should be man- aged with copious irrigation, cautious debridement, and pre- emptive antibiotics (strong, low) | idsa-2014 | 26 | p26/grade-terse/1 | recommendation |
| action-p26-2 | all-ssti-hosts | Other wounds may be approximated (weak, low) | Other wounds may be approximated (weak, low) | idsa-2014 | 26 | p26/grade-terse/2 | recommendation |
| action-p26-3 | all-ssti-hosts | Oral penicillin V 500 mg qid for 7–10 days is the recom- mended treatment for naturally acquired cutaneous anthrax (strong, high) | Oral penicillin V 500 mg qid for 7–10 days is the recom- mended treatment for naturally acquired cutaneous anthrax (strong, high) | idsa-2014 | 26 | p26/grade-terse/3 | recommendation |
| action-p26-4 | all-ssti-hosts | Ciproﬂoxacin 500 mg po bid or levoﬂoxacin 500 mg IV/ po every 24 hours × 60 days is recommended for bioterrorism cases because of presumed aerosol exposure (strong, low) | Ciproﬂoxacin 500 mg po bid or levoﬂoxacin 500 mg IV/ po every 24 hours × 60 days is recommended for bioterrorism cases because of presumed aerosol exposure (strong, low) | idsa-2014 | 26 | p26/grade-terse/4 | recommendation |
| action-p27-1 | all-ssti-hosts | Azithromycin is recommended for cat scratch disease (strong, moderate) | Azithromycin is recommended for cat scratch disease (strong, moderate) | idsa-2014 | 27 | p27/grade-terse/1 | recommendation |
| action-p27-2 | cat-scratch-heavy | use azithromycin; above 45 kg give 500 mg on day 1 then 250 mg for 4 additional days | RENDERED: Azithromycin is recommended for cat scratch disease. Patients >45 kg: 500 mg on day 1 followed by 250 mg for 4 additional days | idsa-2014 | 27 | p27/grade-terse/2 | recommendation |
| action-p27-3 | cat-scratch-light | use azithromycin; below 45 kg give 10 mg/kg day 1 then 5 mg/kg for 4 more days | RENDERED: Azithromycin is recommended for cat scratch disease. Patients <45 kg: 10 mg/kg on day 1 and 5 mg/kg for 4 more days | idsa-2014 | 27 | p27/grade-terse/3 | recommendation |
| action-p27-4 | all-ssti-hosts | Erythromycin 500 mg qid or doxycycline 100 mg bid for 2 weeks to 2 months is recommended for treatment of bacillary angiomatosis (strong, moderate) | Erythromycin 500 mg qid or doxycycline 100 mg bid for 2 weeks to 2 months is recommended for treatment of bacillary angiomatosis (strong, moderate) | idsa-2014 | 27 | p27/grade-terse/4 | recommendation |
| action-p27-5 | all-ssti-hosts | Penicillin (500 mg qid) or amoxicillin (500 mg 3 times daily [tid]) for 7–10 days is recommended for treatment of er- ysipeloid (strong, high) | Penicillin (500 mg qid) or amoxicillin (500 mg 3 times daily [tid]) for 7–10 days is recommended for treatment of er- ysipeloid (strong, high) | idsa-2014 | 27 | p27/grade-terse/5 | recommendation |
| action-p27-6 | all-ssti-hosts | Ceftazidime, gentamicin, imipenem, doxycycline, or cip- roﬂoxacin is recommended based on in vitro susceptibility (strong, low) | Ceftazidime, gentamicin, imipenem, doxycycline, or cip- roﬂoxacin is recommended based on in vitro susceptibility (strong, low) | idsa-2014 | 27 | p27/grade-terse/6 | recommendation |
| action-p28-1 | all-ssti-hosts | Bubonic plague should be diagnosed by Gram stain and culture of aspirated material from a suppurative lymph node (strong, moderate) | Bubonic plague should be diagnosed by Gram stain and culture of aspirated material from a suppurative lymph node (strong, moderate) | idsa-2014 | 28 | p28/grade-terse/1 | recommendation |
| action-p28-2 | all-ssti-hosts | Streptomycin (15 mg/kg intramuscularly [IM] every 12 hours) or doxycycline (100 mg bid po) is recom- mended for treatment of bubonic plague (strong, low) | Streptomycin (15 mg/kg intramuscularly [IM] every 12 hours) or doxycycline (100 mg bid po) is recom- mended for treatment of bubonic plague (strong, low) | idsa-2014 | 28 | p28/grade-terse/2 | recommendation |
| action-p28-3 | all-ssti-hosts | Genta- micin could be substituted for streptomycin (strong, low) | Genta- micin could be substituted for streptomycin (strong, low) | idsa-2014 | 28 | p28/grade-terse/3 | recommendation |
| action-p28-4 | all-ssti-hosts | Serologic tests are the preferred method of diagnosing tu- laremia (weak, low) | Serologic tests are the preferred method of diagnosing tu- laremia (weak, low) | idsa-2014 | 28 | p28/grade-terse/4 | recommendation |
| action-p28-5 | all-ssti-hosts | Streptomycin (15 mg/kg every 12 hours IM) or gentami- cin (1.5 mg/kg every 8 hours IV) is recommended for treatment of severe cases of tularemia (strong, low) | Streptomycin (15 mg/kg every 12 hours IM) or gentami- cin (1.5 mg/kg every 8 hours IV) is recommended for treatment of severe cases of tularemia (strong, low) | idsa-2014 | 28 | p28/grade-terse/5 | recommendation |
| action-p28-6 | all-ssti-hosts | Tetracycline (500 mg qid) or doxycycline (100 mg bid given by mouth) is recommended for treatment of mild cases of tularemia (strong, low) | Tetracycline (500 mg qid) or doxycycline (100 mg bid given by mouth) is recommended for treatment of mild cases of tularemia (strong, low) | idsa-2014 | 28 | p28/grade-terse/6 | recommendation |
| action-p28-7 | all-ssti-hosts | Notify the microbiology laboratory if tularemia is sus- pected (strong, high) | Notify the microbiology laboratory if tularemia is sus- pected (strong, high) | idsa-2014 | 28 | p28/grade-terse/7 | recommendation |
| action-p29-1 | cellular-immunodeficiency | include drug eruption, malignant infiltration, chemotherapy/radiation reactions, Sweet syndrome, erythema multiforme, leukocytoclastic vasculitis, and graft-versus-host disease in the differential besides infection | RENDERED: In addition to infection, differential diagnosis of skin lesions should include drug eruption, cutaneous infiltration with the underlying malignancy, chemotherapy- or radiation-induced reactions, Sweet syndrome, erythema multiforme, leukocytoclastic vasculitis, and graft-vs-host disease among allogeneic transplant recipients | idsa-2014 | 29 | p29/grade-terse/1 | recommendation |
| action-p29-2 | cellular-immunodeficiency | Differential diagnosis for infection of skin lesions should include bacterial, fungal, viral, and parasitic agents (strong, high) | Differential diagnosis for infection of skin lesions should include bacterial, fungal, viral, and parasitic agents (strong, high) | idsa-2014 | 29 | p29/grade-terse/2 | recommendation |
| action-p29-3 | cellular-immunodeficiency | Biopsy or aspiration of the lesion to obtain material for histological and microbiological evaluation should always be implemented as an early diagnostic step (strong, high) | Biopsy or aspiration of the lesion to obtain material for histological and microbiological evaluation should always be implemented as an early diagnostic step (strong, high) | idsa-2014 | 29 | p29/grade-terse/3 | recommendation |
| action-p30-1 | fever-neutropenia | classify the presentation as initial fever/neutropenia, persistent unexplained fever after 4-7 days of the initial episode, or recurrent fever/neutropenia | RENDERED: Determine whether the current presentation of fever and neutropenia is the patient's initial episode, persistent unexplained fever of the initial episode after 4-7 days, or a subsequent recurrent episode | idsa-2014 | 30 | p30/grade-terse/1 | recommendation |
| action-p30-2 | fever-neutropenia | Aggressively determine the etiology of the SSTI by aspi- ration and/or biopsy of skin and soft tissue lesions and submit these for thorough cytological/histological assessments, micro- bial staining, and cultures (strong, low) | Aggressively determine the etiology of the SSTI by aspi- ration and/or biopsy of skin and soft tissue lesions and submit these for thorough cytological/histological assessments, micro- bial staining, and cultures (strong, low) | idsa-2014 | 30 | p30/grade-terse/2 | recommendation |
| action-p30-3 | fever-neutropenia | classify high risk as anticipated >7 days with ANC <100 cells/uL or MASCC <21 | RENDERED: Risk-stratify patients with fever and neutropenia; high-risk patients are those with anticipated prolonged >7 days and profound neutropenia, ANC <100 cells/uL, or with a MASCC score of <21 | idsa-2014 | 30 | p30/grade-terse/3 | recommendation |
| action-p30-4 | fever-neutropenia | classify low risk as anticipated <7 days with few comorbidities or MASCC >=21 | RENDERED: low-risk patients are those with anticipated brief <7 days periods of neutropenia and few comorbidities or with a MASCC score of >=21 | idsa-2014 | 30 | p30/grade-terse/4 | recommendation |
| action-p30-5 | fever-neutropenia | Determine the extent of infection through a thorough physical examination, blood cultures, chest radiograph, and ad- ditional imaging (including chest CT) as indicated by clinical signs and symptoms (strong, low) | Determine the extent of infection through a thorough physical examination, blood cultures, chest radiograph, and ad- ditional imaging (including chest CT) as indicated by clinical signs and symptoms (strong, low) | idsa-2014 | 30 | p30/grade-terse/5 | recommendation |
| action-p31-1 | initial-neutropenic-ssti | Hospitalization and empiric antibacterial therapy with vancomycin plus antipseudomonal antibiotics such as cefe- pime, a carbapenem (imipenem-cilastatin or meropenem or doripenem), or piperacillin-tazobactam are recommended (strong, high) | Hospitalization and empiric antibacterial therapy with vancomycin plus antipseudomonal antibiotics such as cefe- pime, a carbapenem (imipenem-cilastatin or meropenem or doripenem), or piperacillin-tazobactam are recommended (strong, high) | idsa-2014 | 31 | p31/grade-terse/1 | recommendation |
| action-p32-1 | initial-neutropenic-ssti | treat documented clinical and microbiologic SSTIs according to isolate susceptibilities | RENDERED: Documented clinical and microbiologic SSTIs should be treated based on antimicrobial susceptibilities of isolated organisms | idsa-2014 | 32 | p32/grade-terse/1 | recommendation |
| action-p32-2 | initial-neutropenic-ssti | treat most bacterial SSTIs for 7-14 days | RENDERED: duration of treatment for most bacterial SSTIs should be for 7-14 days | idsa-2014 | 32 | p32/grade-terse/2 | recommendation |
| action-p32-3 | initial-neutropenic-ssti | drain soft-tissue abscess after marrow recovery and operate for progressive polymicrobial necrotizing fasciitis or myonecrosis | RENDERED: Surgical intervention is recommended for drainage of soft tissue abscess after marrow recovery or for a progressive polymicrobial necrotizing fasciitis or myonecrosis | idsa-2014 | 32 | p32/grade-terse/3 | recommendation |
| action-p32-4 | initial-neutropenic-ssti | do not routinely use G-CSF, GM-CSF, or granulocyte transfusions as adjuncts | RENDERED: Adjunct colony-stimulating factor therapy, G-CSF, GM-CSF, or granulocyte transfusions are not routinely recommended | idsa-2014 | 32 | p32/grade-terse/4 | recommendation |
| action-p32-5 | initial-neutropenic-ssti | administer acyclovir for suspected or confirmed cutaneous or disseminated HSV or VZV | RENDERED: Acyclovir should be administered to patients suspected or confirmed to have cutaneous or disseminated HSV or VZV infection | idsa-2014 | 32 | p32/grade-terse/5 | recommendation |
| action-p32-6 | persistent-neutropenic-ssti | Yeasts and molds remain the primary cause of infection- associated with persistent or recurrent fever and neutropenia; therefore, empiric antifungal therapy (Table 6) should be added to the antibacterial regimen (strong, high) | Yeasts and molds remain the primary cause of infection- associated with persistent or recurrent fever and neutropenia; therefore, empiric antifungal therapy (Table 6) should be added to the antibacterial regimen (strong, high) | idsa-2014 | 32 | p32/grade-terse/6 | recommendation |
| action-p32-7 | persistent-neutropenic-ssti | add vancomycin or another gram-positive agent such as linezolid, daptomycin, or ceftaroline if not already given | RENDERED: Empiric administration of vancomycin or other agents with gram-positive activity, linezolid, daptomycin, or ceftaroline, should be added if not already being administered | idsa-2014 | 32 | p32/grade-terse/7 | recommendation |
| action-p32-8 | candida-ssti | treat Candida SSTI with an echinocandin; for C. parapsilosis use lipid amphotericin B | RENDERED: Candida species SSTIs should be treated with an echinocandin or, if Candida parapsilosis has been isolated, lipid formulation amphotericin B | idsa-2014 | 32 | p32/grade-terse/8 | recommendation |
| action-p32-9 | candida-ssti | treat Candida SSTI with an echinocandin or C. parapsilosis with lipid amphotericin B; fluconazole is an acceptable alternative | RENDERED: Candida species SSTIs should be treated with an echinocandin or, if Candida parapsilosis has been isolated, lipid formulation amphotericin B with fluconazole as an acceptable alternative | idsa-2014 | 32 | p32/grade-terse/9 | recommendation |
| action-p32-10 | persistent-neutropenic-ssti | Treatment should be for 2 weeks after clearance of bloodstream infection or resolution of skin lesions (strong, moderate) | Treatment should be for 2 weeks after clearance of bloodstream infection or resolution of skin lesions (strong, moderate) | idsa-2014 | 32 | p32/grade-terse/10 | recommendation |
| action-p33-1 | persistent-neutropenic-ssti | (c) Aspergillus SSTIs should be treated with voriconazole (strong, high) | (c) Aspergillus SSTIs should be treated with voriconazole (strong, high) | idsa-2014 | 33 | p33/grade-terse/1 | recommendation |
| action-p33-2 | persistent-neutropenic-ssti | (c) Aspergillus SSTIs should be treated with voriconazole (strong, high), or, alternatively, lipid formulations of ampho- tericin B, posaconazole, or echinocandin for 6–12 weeks (strong, low) | (c) Aspergillus SSTIs should be treated with voriconazole (strong, high), or, alternatively, lipid formulations of ampho- tericin B, posaconazole, or echinocandin for 6–12 weeks (strong, low) | idsa-2014 | 33 | p33/grade-terse/2 | recommendation |
| action-p33-3 | persistent-neutropenic-ssti | Mucor/Rhizopus infections should be treated with lipid formulation amphotericin B (strong, moderate) | Mucor/Rhizopus infections should be treated with lipid formulation amphotericin B (strong, moderate) | idsa-2014 | 33 | p33/grade-terse/3 | recommendation |
| action-p33-4 | persistent-neutropenic-ssti | Mucor/Rhizopus infections should be treated with lipid formulation amphotericin B (strong, moderate) or posaconazole (strong, low) | Mucor/Rhizopus infections should be treated with lipid formulation amphotericin B (strong, moderate) or posaconazole (strong, low) | idsa-2014 | 33 | p33/grade-terse/4 | recommendation |
| action-p33-5 | persistent-neutropenic-ssti | The addition of an echi- nocandin could be considered based on synergy in murine models of mucormycosis and observational clinical data (weak, low) | The addition of an echi- nocandin could be considered based on synergy in murine models of mucormycosis and observational clinical data (weak, low) | idsa-2014 | 33 | p33/grade-terse/5 | recommendation |
| action-p33-6 | persistent-neutropenic-ssti | treat Fusarium with high-dose IV voriconazole or posaconazole | RENDERED: Fusarium species infections should be treated with high-dose IV voriconazole or posaconazole | idsa-2014 | 33 | p33/grade-terse/6 | recommendation |
| action-p33-7 | resistant-ssti | begin treatment for antibiotic-resistant bacteria in patients currently receiving antibiotics | RENDERED: Begin treatment for antibiotic-resistant bacterial organisms in patients currently on antibiotics | idsa-2014 | 33 | p33/grade-terse/7 | recommendation |
| action-p33-8 | persistent-neutropenic-ssti | add IV acyclovir for suspected or confirmed cutaneous or disseminated HSV or VZV | RENDERED: Intravenous acyclovir should be added to the patient's antimicrobial regimen for suspected or confirmed cutaneous or disseminated HSV or VZV infections | idsa-2014 | 33 | p33/grade-terse/8 | recommendation |
| action-p33-9 | persistent-neutropenic-ssti | obtain blood cultures and aggressively evaluate skin lesions by culture aspiration, biopsy, or surgical excision because resistant microbes, yeasts, or molds may cause them | RENDERED: Blood cultures should be obtained, and skin lesions should be aggressively evaluated by culture aspiration, biopsy, or surgical excision as they may be caused by resistant microbes, yeast, or molds | idsa-2014 | 33 | p33/grade-terse/9 | recommendation |
| action-p33-10 | persistent-neutropenic-ssti | recognize low sensitivity of a single beta-D-glucan or galactomannan test, especially during antifungals, and inconsistent benefit from fungal antigen or DNA testing | RENDERED: The sensitivity of a single serum fungal antigen test, 1,3-beta-D-glucan or galactomannan, is low particularly in patients receiving antifungal agents, and benefits from laboratory tests for fungal antigen or DNA detection remain inconsistent | idsa-2014 | 33 | p33/grade-terse/10 | recommendation |
| action-p33-11 | persistent-neutropenic-ssti | PCR in peripheral blood for HSV and VZV might be helpful in establishing a diagnosis of disseminated infection in patients with unexplained skin lesions (weak, moderate) | PCR in peripheral blood for HSV and VZV might be helpful in establishing a diagnosis of disseminated infection in patients with unexplained skin lesions (weak, moderate) | idsa-2014 | 33 | p33/grade-terse/11 | recommendation |
| action-p34-1 | cellular-immunodeficiency | immediately consider dermatology consultation familiar with infection in lymphoma, lymphocytic leukemia, organ transplant, or immunosuppressive-drug cellular immune defects | RENDERED: Consider immediate consultation with a dermatologist familiar with cutaneous manifestations of infection in patients with cellular immune defects, including lymphoma, lymphocytic leukemia, organ transplant recipients, or those receiving immunosuppressive drugs such as anti-TNF or certain monoclonal antibodies | idsa-2014 | 34 | p34/grade-terse/1 | recommendation |
| action-p34-2 | cellular-immunodeficiency | Consider biopsy and surgical debridement early in the management of these patients (weak, low) | Consider biopsy and surgical debridement early in the management of these patients (weak, low) | idsa-2014 | 34 | p34/grade-terse/2 | recommendation |
| action-p34-3 | cellular-immunodeficiency | in life-threatening situations consider empiric antibacterial, antifungal, and/or antiviral therapy, selecting agents with the primary, dermatology, infectious disease, and other consulting teams | RENDERED: Empiric antibiotics, antifungals, and/or antivirals should be considered in life-threatening situations. The use of specific agents should be decided with the input of the primary team, dermatology, infectious disease, and other consulting teams | idsa-2014 | 34 | p34/grade-terse/3 | recommendation |
| action-p34-4 | cellular-immunodeficiency | select specific empiric agents collaboratively with the primary team, dermatology, infectious disease, and other consultants | RENDERED: The use of specific agents should be decided with the input of the primary team, dermatology, infectious disease, and other consulting teams | idsa-2014 | 34 | p34/grade-terse/4 | recommendation |

## Conflicts

CONFLICT: figure1-severity uses WBC <12 000 or <400 cells/uL in the printed Figure 1 caption, while rec6-wbc-threshold uses WBC >12 000 or <400 cells/uL in recommendation 6 and its detailed text. The recommendation threshold is the internally coherent SIRS value; the figure's first comparator is retained as printed rather than silently corrected.

CONFLICT: cat-scratch-dose uses recommendation cutoffs >45 kg and <45 kg, while cat-scratch-evidence-dose uses the narrative evidence cutoffs >=45.5 kg (100 lb) and <45.5 kg. Both source values are retained with distinct populations and provenance.

No same-population, same-quantity conflict was found. Different drug regimens in Tables
2-7 are alternatives or pathogen-, site-, severity-, allergy-, and host-specific branches,
not contradictions. The 5-day cellulitis course and longer 7-14-day neutropenic-host
course apply to different populations. Tularemia's 7-10-day parenteral/severe framework
and at-least-14-day oral framework are distinct route and severity branches.

## Coverage

The bound record contains 212 marker occurrences representing 75 numbered recommendations. All 106 detailed-location fragment IDs on pages 12-34 are cited in the Thresholds table, including word-only clinical actions. The 106 executive-summary duplicates on pages 2-10 are individually disposed below. Exact accounting: **212 = 106 detailed fragment IDs cited + 106 executive duplicates scoped out**.

- `p2/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p2/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p2/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p2/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p2/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p3/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p3/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p3/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p4/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p4/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/6` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/7` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/8` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/9` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/10` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/11` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/12` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/13` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p6/grade-terse/14` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/6` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/7` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/8` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/9` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/10` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/11` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/12` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/13` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/14` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/15` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/16` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/17` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/18` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/19` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p7/grade-terse/20` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/6` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/7` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/8` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/9` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/10` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/11` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/12` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/13` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/14` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/15` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/16` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/17` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/18` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/19` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/20` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p8/grade-terse/21` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/6` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/7` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/8` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/9` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/10` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/11` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/12` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/13` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/14` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/15` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/16` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/17` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/18` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/19` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/20` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/21` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/22` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p9/grade-terse/23` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/1` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/2` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/3` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/4` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/5` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/6` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/7` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/8` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/9` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/10` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/11` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/12` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/13` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/14` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/15` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/16` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/17` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table
- `p10/grade-terse/18` - executive-summary duplicate of the corresponding detailed fragment cited in the Thresholds table

## ADR 0009 disposition

The complete source-page sweep retained every number and word-only action that changes patient management:
purulent/nonpurulent severity, culture and drainage boundaries, empiric and directed
regimens, adult and pediatric doses in Tables 2-7, treatment durations, prophylaxis,
repeat surgery, escalation, monitoring, immunocompromise, and quantified benefit or
harm evidence. All 75 numbered recommendations are retained as complete actions while
all 106 detailed fragment identifiers remain individually cited; extractor-fragmented
sentences were restored from the rendered recommendation text without inventing thresholds.

Figures 1-2 were read for severity and SSI routing. Tables 1-7 were read; Table 1 is the
GRADE definitions table and contains no patient-action threshold, while Tables 2-7 supply
drug/dose branches retained above. Introduction and methods add no patient-changing
thresholds beyond the scope/applicability statements. Future directions are research
priorities rather than current patient actions. Article administration and disclosures
were read with a dated blind; references are exempt as a citation list.

Exact recommendation accounting for the bound marker record: **106 cited detailed marker
IDs + 106 scoped-out executive-summary duplicate marker IDs = 212 total marker
occurrences**. The sheet's clinical denominator is the full 43-page read, not that marker
count.
