# Outpatient parenteral antimicrobial therapy — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2018 | IDSA | IDSA/ciy745 | guideline | 2018 guideline | 2018-11-13 | https://doi.org/10.1093/cid/ciy745 | stated | bound |

## Scope

**Read:** all 35 pages, including the definition and care models; executive and full
recommendations; adult, pediatric, neonatal, elderly, PWID, home, infusion-center,
SNF, and dialysis branches; antibacterial, antifungal, and antiviral tables; vascular
access, laboratory and drug-level monitoring, follow-up, stewardship, benefits, harms,
methods, disclosures, and references. The bound record has 23 marker occurrences, but
its omissions include five explicitly numbered no-recommendation actions; the full-page
read, not the marker record, defines the clinical sweep.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's patient-action rule:** epidemiology, study enrollment,
effect estimates, cost estimates, evidence-grading methods, research questions, author
metadata, and reference-list numbers unless the source uses a value to change eligibility,
site or device choice, administration, surveillance, drug monitoring, or stewardship.

| span | pages | read |
| --- | --- | --- |
| title, definition, executive recommendations, care models | 1-5 | yes |
| antibacterial administration and monitoring table | 6-8 | yes |
| therapeutic, safety, administration, team, antiviral and antifungal table | 9-11 | yes |
| methods, grading, and conflicts process | 11-13 | read 2026-09-01; blind 2026-09-01 |
| self-administration, unsupported home care, PWID, elderly, and neonates | 14-20 | yes |
| first dose and vascular-access decisions | 20-27 | yes |
| laboratory/drug monitoring, follow-up, stewardship | 27-31 | yes |
| stewardship rationale and pediatric oral-transition boundary | 31 | yes |
| future directions, article information, and disclosures | 32 | read 2026-09-01; blind 2026-09-01 |
| references | 32-35 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| opat-patients | patients receiving parenteral antimicrobial therapy in at least 2 doses on different days without intervening hospitalization |
| trained-patient-caregiver | patients or caregivers trained and competent to self-administer OPAT |
| home-no-nurse | patients or caregivers self-administering OPAT at home without visiting-nurse support |
| home-candidates | OPAT candidates considered for home infusion |
| infusion-center-candidates | patients physically unable or unwilling to self-infuse who can travel reliably to an infusion center |
| snf-candidates | patients requiring nursing, rehabilitation, wound care, or other skilled services |
| dialysis-patients | patients receiving OPAT during dialysis sessions |
| pwid | people who inject drugs considered for home OPAT |
| elderly | elderly patients considered for home OPAT |
| neonates | infants aged less than 1 month considered for home OPAT |
| new-agent-no-class-allergy | patients with no prior allergy to an antimicrobial in the same class receiving the first dose of a new parenteral antimicrobial at home |
| adults-short-opat | adults needing an OPAT course shorter than 14 days |
| pediatric-midline | pediatric patients needing OPAT for whom a midline is considered |
| vancomycin-opat | OPAT patients receiving vancomycin |
| other-vesicant-opat | OPAT patients receiving a vesicant other than vancomycin, including nafcillin or acyclovir |
| advanced-ckd | patients with advanced chronic kidney disease requiring OPAT |
| frequent-opat | patients requiring frequent OPAT courses |
| ca-vte | OPAT patients who develop symptomatic catheter-associated venous thromboembolism |
| prior-ca-vte | OPAT patients with a history of catheter-associated venous thromboembolism |
| most-children | most children requiring OPAT without an already appropriate long-term central catheter |
| monitored-opat | patients receiving OPAT whose tests and results are available to the overseeing team |
| stable-renal-vancomycin | vancomycin OPAT patients with stable renal function |
| aminoglycoside-opat | OPAT patients receiving aminoglycosides |
| all-opat-before-start | all patients before initiation of OPAT |
| normal-organ-function | OPAT patients with normal renal and hepatic function |
| pediatric-assisted | pediatric OPAT patients requiring adult assistance for every infusion |
| oral-switch-candidate | OPAT candidates for whom an effective, absorbable oral regimen may substitute |

## Quantities

| key | verbatim |
| --- | --- |
| opat-definition | number and timing of parenteral doses defining OPAT |
| home-eligibility | minimum patient, caregiver, and home-system requirements |
| site-selection | practical boundary among home, infusion center, SNF, and dialysis delivery |
| self-administration | whether a patient or caregiver may administer OPAT |
| home-no-nurse-eligibility | monitoring condition for home OPAT without visiting nursing |
| home-no-nurse-competency | competency and clinic-follow-up implementation for teach-and-train OPAT |
| pwid-home | home-OPAT disposition for people who inject drugs |
| elderly-home | home-OPAT disposition and functional conditions for elderly patients |
| neonatal-home | home-OPAT disposition for infants younger than 1 month |
| first-dose-home | allergy and supervision boundary for first administration at home |
| first-dose-observation | usual observation time after a first dose |
| midline-duration | duration boundary for adult midline rather than central access |
| midline-extension | action when a functioning midline course extends beyond its anticipated duration |
| vesicant-access | central-access requirements for vancomycin and other vesicants |
| ckd-idsa-access | IDSA device choice in advanced CKD |
| ckd-magic-access | MAGIC device choice by CKD stage and renal replacement status |
| ckd-external-threshold | external vascular-access assessment and vein-preservation thresholds |
| frequent-course-access | whether a long-term central catheter should remain between courses |
| ca-vte-retention | catheter-retention conditions after catheter-associated thrombosis |
| ca-vte-retention-context | continued-access, function, and bleeding considerations |
| ca-vte-prophylaxis | prophylaxis after prior catheter-associated thrombosis |
| pediatric-access | PICC versus long-term central catheter for children |
| serial-laboratory-recommendation | requirement and evidence limits for laboratory monitoring |
| serial-laboratory-implementation | result availability and short-course implementation boundary |
| adverse-event-surveillance | treatment-duration and drug-profile boundary for surveillance |
| vancomycin-levels | serum-level monitoring frequency and duration |
| aminoglycoside-levels | serum-level monitoring and toxicity-surveillance boundary |
| follow-up-individualization | physician-determined follow-up variables |
| follow-up-home-cadence | home nursing cadence |
| follow-up-infusion-cadence | infusion-center nursing and physician cadence |
| follow-up-program-cadence | reported program cadence |
| id-review-recommendation | infectious-diseases expert review before OPAT |
| id-review-model | forms of infectious-diseases expert review |
| oral-switch-stewardship | oral-transition decision boundary |
| opat-diagnosis-source-control | diagnosis and source-control boundary before OPAT |
| opat-agent-selection | antimicrobial efficacy and patient-factor boundary |
| opat-necessity | OPAT only when equivalent oral therapy is unavailable |
| delivery-selection | delivery-device and administration constraints |
| amikacin-table | amikacin administration, monitoring, and harms |
| gentamicin-table | gentamicin administration, monitoring, and harms |
| tobramycin-table | tobramycin administration, monitoring, and harms |
| aminopenicillin-table | ampicillin and ampicillin-sulbactam administration, monitoring, and harms |
| azithromycin-table | azithromycin administration, oral transition, and QT harm |
| beta-lactam-table | aztreonam and cephalosporin administration, monitoring, and harms |
| ciprofloxacin-table | ciprofloxacin administration, oral transition, and harms |
| levofloxacin-table | levofloxacin administration, oral transition, and harms |
| clindamycin-metronidazole-table | clindamycin and metronidazole administration, monitoring, and harms |
| daptomycin-table | daptomycin administration, CK monitoring, and stop thresholds |
| carbapenem-table | carbapenem administration, monitoring, and harms |
| oxazolidinone-table | linezolid and tedizolid administration, monitoring, and harms |
| antistaphylococcal-penicillin-table | nafcillin and oxacillin administration, monitoring, and harms |
| penicillin-g-table | penicillin G administration, monitoring, and oral-substitution boundary |
| piperacillin-tazobactam-table | piperacillin-tazobactam administration, monitoring, and harms |
| polymyxin-table | colistin and polymyxin B administration, monitoring, and harms |
| rifampin-table | rifampin administration, monitoring, interactions, and oral transition |
| long-acting-lipoglycopeptide-table | dalbavancin and oritavancin administration and monitoring limits |
| vancomycin-table | vancomycin administration, monitoring, and harms |
| telavancin-table | telavancin administration, monitoring, and harms |
| tmp-smx-table | trimethoprim/sulfamethoxazole administration, monitoring, and harms |
| tigecycline-table | tigecycline administration, monitoring, and harms |
| amphotericin-table | amphotericin B administration, monitoring, and harms |
| echinocandin-azole-table | echinocandin and selected azole administration and monitoring |
| voriconazole-table | voriconazole administration, monitoring, and renal boundary |
| acyclovir-table | acyclovir administration, hydration, oral transition, and harms |
| cidofovir-table | cidofovir administration, hydration, monitoring, and harms |
| foscarnet-table | foscarnet administration, hydration, monitoring, and harms |
| ganciclovir-table | ganciclovir administration, monitoring, oral transition, and harms |
| benefit-harm | benefits and harms that govern OPAT selection |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| opat-definition | opat-patients | at least 2 parenteral doses on different days without intervening hospitalization | RENDERED: provision of parenteral antimicrobial therapy in at least 2 doses on different days without intervening hospitalization | idsa-2018 | 1 | p1/narrative/opat-definition | narrative |
| home-eligibility | home-candidates | require a competent, adherent patient or caregiver; adequate refrigeration and storage; at least 1 adult able to learn sterile infusion technique and communicate with the team | RENDERED: Critical to the success of home-based OPAT is the presence of a competent and adherent patient and/or caregiver ... adequate refrigeration and storage ... At least 1 adult who can reliably learn and perform sterile infusion technique and communicate with the treatment team | idsa-2018 | 4 | p4/narrative/home-minimum-features | narrative |
| site-selection | infusion-center-candidates | infusion-center delivery requires reliable travel and provides daily in-person nursing oversight | RENDERED: Infusion centers are well suited for patients who are physically incapable or unwilling to infuse themselves ... requires reliable transportation ... offers additional oversight with daily in-person visits | idsa-2018 | 4 | p4/narrative/infusion-center | narrative |
| delivery-selection | infusion-center-candidates | dosing more often than once daily is typically impractical in an infusion center | RENDERED: Dosing more frequently than once daily is typically not practical for patients who receive care in infusion centers. | idsa-2018 | 8 | p8/table-2/infusion-center-frequency | table |
| site-selection | snf-candidates | SNF permits on-site nursing plus rehabilitation or wound care but increases exposure to resistant organisms including Clostridioides difficile and is the most expensive overall model | RENDERED: skilled nursing facility (SNF), where on-site nurses perform all infusion functions ... patients are more likely to encounter resistant organisms, including Clostridium difficile ... significantly more expensive | idsa-2018 | 4 | p4/narrative/snf | narrative |
| site-selection | dialysis-patients | dialysis delivery can avoid a separate access device but may restrict drugs to those the center provides; vancomycin, cefazolin, or aminoglycosides may be the only available choices | RENDERED: patients who receive their parenteral antimicrobials during dialysis sessions may be limited to a choice of vancomycin, cefazolin, or aminoglycosides only | idsa-2018 | 9 | p9/narrative/dialysis-delivery | narrative |
| self-administration | trained-patient-caregiver | allow patient or caregiver self-administration | RENDERED: Patients (or their caregivers) should be allowed to self-administer OPAT | idsa-2018 | 14 | p14/grade-spelled-out/1 | strong recommendation, low-quality evidence |
| home-no-nurse-eligibility | home-no-nurse | may self-administer without visiting nurse only with an effective system monitoring vascular-access complications and antimicrobial adverse events | RENDERED: Patients (or their caregivers) may be allowed to self-administer OPAT at home without visiting nurse support as long as there is a system in place for effective monitoring for vascular access complications and antimicrobial adverse events | idsa-2018 | 15 | p15/grade-spelled-out/1 | weak recommendation, low-quality evidence |
| home-no-nurse-competency | home-no-nurse | establish administration competency before discharge; clinic follow-up provides vascular-access care, laboratory monitoring, and physician follow-up | RENDERED: competency was established before discharge through a standardized protocol ... followed at designated intervals in clinic for IV access care, laboratory monitoring, and physician follow-up | idsa-2018 | 15 | p15/narrative/teach-train-competency | narrative |
| pwid-home | pwid | no recommendation; decisions should be made case by case | RENDERED: No recommendation can be made about whether PWID may be treated with OPAT at home (no recommendation, low-quality evidence). Decisions should be made on a case-by-case basis. | idsa-2018 | 16 | p16/narrative/pwid-home | narrative |
| benefit-harm | pwid | observed association with vascular-access complications: IRR 3.32 (95% CI 1.16-7.46); theoretical harms include device misuse, nonadherence, lower cure, and overdose, while SNF misuse risk is not known to be lower | IDU was found to be a risk factor for vascular access complications (incidence rate ratio [IRR] 3.32, 95% CI 1.16–7.46, P = .01) | idsa-2018 | 16 | p16/narrative/pwid-risk | narrative |
| elderly-home | elderly | allow home OPAT only after cognition, mobility, and dexterity are considered and the patient or caregiver can communicate with the treatment team | RENDERED: Elderly patients should be allowed to be treated with OPAT at home ... This recommendation assumes that potential challenges to OPAT in the elderly, such as cognition, mobility, and dexterity, have been duly considered and that the patient or caregiver is able to communicate with the treatment team if necessary. | idsa-2018 | 17 | p17/grade-spelled-out/1 | strong recommendation, low-quality evidence |
| benefit-harm | elderly | older patients may need more support; one study found lower self-administration (20% vs 41%) and higher urgent-care visits, calls, social-work use, and nephrotoxicity, but overall evidence did not show more readmissions or adverse events | RENDERED: Older patients had lower rates of ability to self-administer (20% vs 41%) ... higher rates of urgent care visits ... calls ... social work intervention | idsa-2018 | 18 | p18/narrative/elderly-resources | narrative |
| neonatal-home | neonates | no recommendation; decisions should be made case by case | RENDERED: No recommendation can be made regarding whether infants aged <1 month may be treated with OPAT at home (no recommendation, very low-quality evidence). Decisions should be made on a case-by-case basis. | idsa-2018 | 18 | p18/narrative/neonate-home | narrative |
| first-dose-home | new-agent-no-class-allergy | may give the first dose at home only under healthcare personnel qualified and equipped to respond to anaphylaxis | RENDERED: In patients with no prior history of allergy to antimicrobials in the same class, the first dose of a new parenteral antimicrobial may be administered at home under the supervision of healthcare personnel who are qualified and equipped to respond to anaphylactic reactions | idsa-2018 | 20 | p20/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| adverse-event-surveillance | new-agent-no-class-allergy | tolerating a first dose does not exclude a serious adverse event on a later administration | RENDERED: It is recognized that serious adverse events from antimicrobials may occur on subsequent administrations after the first dose has been tolerated. | idsa-2018 | 20 | p20/narrative/later-allergy | narrative |
| first-dose-observation | new-agent-no-class-allergy | no clear guideline; usual practice is 30 minutes | RENDERED: There are no clear guidelines about how long a patient should be observed after administration of the first dose of a new antimicrobial. The usual practice is 30 minutes. | idsa-2018 | 20 | p20/narrative/first-dose-observation | narrative |
| midline-duration | adults-short-opat | IDSA: a midline may replace central access when the planned OPAT course is less than 14 days | In adult patients needing short courses of OPAT (less than 14 days), a MC may be used rather than a central catheter | idsa-2018 | 21 | p21/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| midline-duration | adults-short-opat | MAGIC external criteria: use a midline for anticipated infusions lasting 14 or fewer days and prefer a PICC for 15 or more days | RENDERED: recommended the use of a MC for infusions anticipated to last 14 or fewer days and preferential use of a PICC for infusions anticipated to last 15 or more days | idsa-2018 | 21 | p21/narrative/magic-midline-duration | narrative |
| midline-duration | pediatric-midline | no recommendation can be made regarding midlines in pediatric patients | RENDERED: No recommendations can be made regarding the use of MCs in pediatric patients. | idsa-2018 | 21 | p21/narrative/pediatric-midline | narrative |
| midline-extension | adults-short-opat | when an anticipated short course is unexpectedly extended, do not automatically exchange a well-functioning midline for a PICC | RENDERED: In the setting of a well-functioning catheter, there is no compelling argument to exchange a MC for a PICC if an anticipated short OPAT course requires extension. | idsa-2018 | 21 | p21/narrative/midline-extension | narrative |
| vesicant-access | vancomycin-opat | do not mandate a central catheter solely for vancomycin | Mandatory use of a central catheter over a noncentral catheter for OPAT with vancomycin is not necessary | idsa-2018 | 22 | p22/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| vesicant-access | other-vesicant-opat | no recommendation for nafcillin, acyclovir, or other vesicants; evidence does not support one blanket catheter rule | No recommendation can be made for choice of vascular catheter for OPAT with other vesicant antimicrobials such as nafcillin and acyclovir | idsa-2018 | 22 | p22/narrative/other-vesicants | narrative |
| ckd-idsa-access | advanced-ckd | use a tunneled central venous catheter rather than a PICC | For patients with advanced CKD requiring OPAT, a t-CVC is recommended rather than a PICC | idsa-2018 | 23 | p23/grade-spelled-out/1 | strong recommendation, low-quality evidence |
| ckd-external-threshold | advanced-ckd | ASDIN/AVA: obtain expert vascular-access assessment before any vascular-access device when eGFR is below 60 mL/min/1.73 m2 or serum creatinine is at least 2.0 mg/dL | RENDERED: patients with an estimated glomerular filtration rate (eGFR) of <60 mL/min/1.73 m2 or a serum creatinine level ≥2.0 mg/dL should undergo an expert vascular access assessment prior to placement of any VAD | idsa-2018 | 24 | p24/narrative/asdin-ava-assessment | narrative |
| ckd-magic-access | advanced-ckd | MAGIC: prefer a CVC over a PICC or midline to preserve upper-extremity veins at CKD stage 3b, eGFR below 45 mL/min/1.73 m2, or renal replacement therapy | RENDERED: For patients with CKD stage 3b (eGFR of <45 mL/min/1.73 m2) or greater or receiving renal replacement therapy, panelists recommended CVCs over PICCs and MCs to maximize upper extremity vein preservation. | idsa-2018 | 24 | p24/narrative/magic-ckd-device | narrative |
| frequent-course-access | frequent-opat | no recommendation can be made about leaving a long-term central catheter in place between frequent OPAT courses | RENDERED: No recommendation can be made about whether patients who require frequent courses of OPAT should have a LTCC left in place between courses (no recommendation, no evidence). | idsa-2018 | 24 | p24/narrative/frequent-opat-access | narrative |
| ca-vte-retention | ca-vte | catheter need not be removed if it remains well positioned and arm pain and swelling decrease with anticoagulation | RENDERED: It is not necessary to remove a vascular access device if CA-VTE develops during OPAT, as long as the catheter remains well positioned and arm pain and swelling decrease with anticoagulation | idsa-2018 | 25 | p25/grade-spelled-out/1 | weak recommendation, very low-quality evidence |
| ca-vte-retention-context | ca-vte | catheter retention is considered when continued vascular access is needed and the catheter remains functional; factor major-bleeding potential into the decision | RENDERED: if there is continued need for a vascular catheter ... as long as the catheter is functional ... The potential for major bleeding must be factored into a decision regarding catheter retention and anticoagulation. | idsa-2018 | 25 | p25/narrative/ca-vte-continued-access-bleeding | narrative |
| ca-vte-prophylaxis | prior-ca-vte | no recommendation can be made about prophylactic oral anticoagulation during OPAT | RENDERED: No recommendation can be made regarding the need to treat patients with a history of prior CA-VTE with prophylactic oral anticoagulation while on OPAT (no recommendation, no evidence). | idsa-2018 | 26 | p26/narrative/ca-vte-prophylaxis | narrative |
| pediatric-access | most-children | place a PICC rather than a long-term central catheter | For most children requiring OPAT, a PICC should be placed rather than a LTCC | idsa-2018 | 26 | p26/grade-spelled-out/1 | strong recommendation, very low-quality evidence |
| serial-laboratory-recommendation | monitored-opat | monitor serial laboratory tests; evidence does not establish specific tests or frequencies for individual OPAT antimicrobials | RENDERED: Serial laboratory testing should be monitored in patients receiving OPAT ... Data are insufficient to make evidence-based recommendations about specific tests and specific frequencies of monitoring for individual antimicrobials used in OPAT. | idsa-2018 | 27 | p27/grade-spelled-out/1 | strong recommendation, high-quality evidence |
| serial-laboratory-implementation | monitored-opat | effective monitoring includes performing the tests and making results available to the physician or team overseeing OPAT; short courses may not require laboratory monitoring | RENDERED: Effective laboratory test monitoring entails the performance of laboratory tests and the availability of results to the physician or team overseeing the OPAT course ... Short courses of OPAT may not require laboratory monitoring. | idsa-2018 | 27 | p27/narrative/effective-monitoring | narrative |
| adverse-event-surveillance | monitored-opat | surveillance depends on the drug's adverse-event profile, comorbidities, baseline tests, and anticipated duration; adverse-event incidence rises as therapy lengthens and reactions are common (reported 11.8%-63.2%) | RENDERED: adverse reactions while on OPAT are common, occurring at a reported rate of 11.8% to 63.2% | idsa-2018 | 28 | p28/narrative/adverse-event-surveillance | narrative |
| vancomycin-levels | vancomycin-opat | monitor blood levels regularly throughout the OPAT course, not only initially | Vancomycin blood levels should be measured regularly throughout the course of OPAT treatment | idsa-2018 | 28 | p28/grade-spelled-out/1 | strong recommendation, very low-quality evidence |
| adverse-event-surveillance | vancomycin-opat | nephrotoxicity may begin after 14 days despite previously stable renal function; 64 of 154 nephrotoxicity cases occurred after day 14 | RENDERED: of the 154 patients who developed nephrotoxicity, 64 (42%) did so after 14 days ... even with previously stable renal function | idsa-2018 | 28 | p28/narrative/vancomycin-late-nephrotoxicity | narrative |
| vancomycin-levels | stable-renal-vancomycin | optimal frequency undefined; general practice with stable renal function is once weekly and additionally with dose changes | The optimal frequency of measurement is undefined, but the general practice in the setting of stable renal function is once weekly | idsa-2018 | 28 | p28/narrative/vancomycin-weekly | narrative |
| aminoglycoside-levels | aminoglycoside-opat | careful renal and otovestibular surveillance and dose adjustment by serum level are warranted; concentrations at least weekly, with trough target depending on drug, infection, and strategy; evidence cannot define the optimal schedule | RENDERED: monitor concentrations minimum weekly. Goal aminoglycoside trough values differ according to the drug, infection, and dosing strategy | idsa-2018 | 8 | p8/table-2/aminoglycoside-monitoring | table |
| follow-up-individualization | opat-patients | no generalized office-visit frequency; clinician weighs patient characteristics, infection, tolerance, response, and individual social factors | RENDERED: No generalized recommendation on frequency of outpatient follow-up can be made for patients treated with OPAT (no recommendation, no evidence). The treating physician should dictate the frequency of office visits, giving consideration to patient characteristics, the nature of the infection, the patient’s tolerance of and response to therapy, and individual patient social factors. | idsa-2018 | 29 | p29/narrative/follow-up-frequency | narrative |
| follow-up-home-cadence | home-candidates | home OPAT usually includes at least weekly nursing visits | RENDERED: patients usually have at least weekly nursing visits. | idsa-2018 | 29 | p29/narrative/home-nursing-cadence | narrative |
| follow-up-infusion-cadence | infusion-center-candidates | infusion-center patients are seen daily by nurses administering therapy; weekly physician visits are a typical program component | RENDERED: Patients who receive OPAT at an infusion center are physically seen daily by nurses who administer their antimicrobial therapy ... weekly physician visits are a typical component of the oversight program. | idsa-2018 | 29 | p29/narrative/infusion-center-cadence | narrative |
| follow-up-program-cadence | opat-patients | reported programs may evaluate patients every 1-2 weeks, or after therapy with more frequent visits when clinically needed | RENDERED: Some programs report physician evaluation as frequently as every 1–2 weeks ... Other programs see patients after therapy, with more frequent visits as clinical needs dictate. | idsa-2018 | 29 | p29/narrative/program-cadence | narrative |
| id-review-recommendation | all-opat-before-start | obtain infectious-diseases expert review before OPAT | RENDERED: All patients should have ID expert review prior to initiation of OPAT | idsa-2018 | 29 | p29/grade-spelled-out/1 | strong recommendation, very low-quality evidence |
| id-review-model | all-opat-before-start | expert review may be traditional consultation, a care-transition or stewardship team, or an ID-pharmacist-managed program collaborating with an ID physician | RENDERED: ID expert review may take different forms ... traditional ID consultation ... ID care transition team ... OPAT stewardship team ... or an ID pharmacist–managed program in collaboration with an ID physician. | idsa-2018 | 31 | p31/narrative/id-review-forms | narrative |
| oral-switch-stewardship | oral-switch-candidate | consider oral transition when the oral drug is appropriate for the infection, with food/drug interactions, concomitant illness, and possible impaired gut absorption included in the decision | RENDERED: changing to oral medications when possible is part of good antimicrobial stewardship ... appropriateness of oral antimicrobials for the condition being treated ... interaction with foods and other medications ... concomitant illnesses ... potential for impaired gut absorption | idsa-2018 | 8 | p8/table-2/oral-stewardship | table |
| opat-diagnosis-source-control | opat-patients | before treatment, identify the infection site and extent and obtain early source control when possible | RENDERED: Correct treatment begins with the correct diagnosis ... identify the infection being treated ... primary site ... extent ... distant sites ... source control ... should be addressed appropriately early in treatment. | idsa-2018 | 9 | p9/narrative/diagnosis-source-control | narrative |
| opat-agent-selection | opat-patients | choose an agent active against the pathogen, distributed to the infection site, and proven effective, considering comorbidities, concomitant therapies, age, and organ function | RENDERED: should have activity against the identified or presumptive causative pathogen(s), known distribution to the site of infection, and proven therapeutic efficacy ... comorbidities, concomitant therapies ... patient age, and organ function. | idsa-2018 | 9 | p9/narrative/agent-selection | narrative |
| delivery-selection | normal-organ-function | table dose frequencies assume normal renal/hepatic function; infusion-center dosing more than once daily is usually impractical; efficacy must not be sacrificed merely for convenient infrequent dosing | RENDERED: Doses per day: assumes normal renal and hepatic function ... Dosing more frequently than once daily is typically not practical for patients who receive care in infusion centers | idsa-2018 | 8 | p8/table-2/dose-assumptions | table |
| delivery-selection | pediatric-assisted | more than 2-3 administrations daily may be impractical when an adult must assist every pediatric dose | More than 2–3 doses per day may be impractical for pediatric outpatient parenteral antimicrobial therapy (OPAT) that requires adult infusion assistance for every dose | idsa-2018 | 8 | p8/table-2/pediatric-frequency | table |
| delivery-selection | home-candidates | select device by patient capability/preferences, drug concentration/stability/infusion time, access device, and coverage; electronic pumps permit multiple doses but mean near-continuous connection, elastomerics are simple, gravity is cheaper but slower/complex, and IV push is rapid but needs dexterity | RENDERED: should be selected based upon patient preferences and capabilities, drug characteristics ... VAD, and cost/insurance coverage | idsa-2018 | 9 | p9/narrative/delivery-selection | narrative |
| amikacin-table | normal-organ-function | amikacin 1-3/day over 30-60 minutes; CBC weekly and BMP twice weekly; nephrotoxicity and ototoxicity; monitor concentrations at least weekly | RENDERED: Amikacin ... 1–3 ... 30–60 min depending on dose ... 1 2 ... Nephrotoxicity; ototoxicity ... monitor concentrations minimum weekly | idsa-2018 | 6 | p6/table-2/amikacin | table |
| gentamicin-table | normal-organ-function | gentamicin 1-3/day over 30-120 minutes; CBC weekly and BMP twice weekly; nephrotoxicity and ototoxicity; monitor concentrations at least weekly | RENDERED: Gentamicin ... 1–3 ... 30–120 min depending on dose ... 1 2 ... Nephrotoxicity; ototoxicity ... monitor concentrations minimum weekly | idsa-2018 | 7 | p7/table-2/gentamicin | table |
| tobramycin-table | normal-organ-function | tobramycin 1-3/day over 30-120 minutes; CBC weekly and BMP twice weekly; nephrotoxicity and ototoxicity; monitor concentrations at least weekly | RENDERED: Tobramycin ... 1–3 ... 30–120 min depending on dose ... 1 2 ... Nephrotoxicity; ototoxicity ... monitor concentrations minimum weekly | idsa-2018 | 8 | p8/table-2/tobramycin | table |
| aminopenicillin-table | normal-organ-function | ampicillin 4-6/day by 3-5-minute push or 10-15-minute infusion; ampicillin-sulbactam 3-4/day by 10-15-minute push or 15-30-minute infusion; weekly CBC/BMP/liver profile; hypersensitivity including anaphylaxis; both remain stable only 3 days after reconstitution | RENDERED: Ampicillin ... 4–6 ... 3–5 min push or 10–15 min infusion ... 1 1 1 ... Hypersensitivity including anaphylaxis ... Ampicillin-sulbactam ... 3–4 ... 10–15 min push or 15–30 min infusion ... 1 1 1 ... Hypersensitivity including anaphylaxis ... Stable once reconstituted for only 3 days | idsa-2018 | 6 | p6/table-2/ampicillin | table |
| azithromycin-table | normal-organ-function | azithromycin daily over 60 minutes; monitor CBC weekly; known torsades de pointes risk; consider oral change | RENDERED: Azithromycin ... 1 ... 60 min ... 1 ... Known ... Consider change to po | idsa-2018 | 6 | p6/table-2/azithromycin | table |
| beta-lactam-table | normal-organ-function | aztreonam 2-4/day by 3-5-minute push or 20-60-minute infusion with weekly CBC/BMP/liver profile and rare cross-allergenicity with other beta-lactams; cefazolin 3-4/day by 3-5-minute push or 30-60-minute infusion, cefepime 2-3/day by 5-minute push or 30-minute infusion, and ceftazidime 3/day by 3-5-minute push or 15-30-minute infusion, each with a dialysis-only dosing option; cefoxitin 3-4/day by 3-5-minute push or 20-30-minute infusion; ceftaroline 2-3/day by 5-minute push or 5-60-minute infusion; ceftazidime-avibactam 3/day over 120 minutes; ceftolozane-tazobactam 3/day over 60 minutes; ceftriaxone 1-2/day by 1-4-minute push or 30-minute infusion; generally monitor CBC/BMP weekly, with weekly liver profile for ceftriaxone; cephalosporins carry hypersensitivity including anaphylaxis | RENDERED: Aztreonam ... 2–4 ... 3–5 min push or 20–60 min infusion ... 1 1 1 ... Rare cross-allergenicity with other beta-lactams ... Cefazolin ... 3–4 ... 3–5 min push or 30–60 min infusion ... Dialysis-only dosing possible ... Cefepime ... 2–3 ... 5 min push or 30 min infusion ... Dialysis-only dosing possible ... Cefoxitin ... 3–4 ... 3–5 min push or 20–30 min infusion ... Ceftaroline ... 2–3 ... 5 min push or 5–60 min ... Ceftazidime ... 3 ... 3–5 min push or 15–30 min infusion ... Dialysis-only dosing possible ... Ceftazidime-avibactam ... 3 ... 120 min ... Ceftolozane-tazobactam ... 3 ... 60 min ... Ceftriaxone ... 1–2 ... 1–4 min push or 30 min infusion ... 1 1 1 ... Hypersensitivity including anaphylaxis | idsa-2018 | 6 | p6/table-2/beta-lactams | table |
| ciprofloxacin-table | normal-organ-function | ciprofloxacin 2-3/day over 60 minutes; tendon rupture and peripheral neuropathy; consider oral change | RENDERED: Ciprofloxacin ... 2–3 ... 60 min ... Tendonitis/tendon rupture; peripheral neuropathy ... Consider change to po | idsa-2018 | 6 | p6/table-2/ciprofloxacin | table |
| levofloxacin-table | normal-organ-function | levofloxacin daily over 60-90 minutes; tendon rupture, cardiac arrhythmias, and peripheral neuropathy; consider oral change | RENDERED: Levofloxacin ... 1 ... 60–90 min depending on dose ... Tendonitis/tendon rupture; cardiac arrhythmias; peripheral neuropathy ... Consider change to po | idsa-2018 | 7 | p7/table-2/levofloxacin | table |
| clindamycin-metronidazole-table | normal-organ-function | clindamycin 3-4/day over 10-60 minutes, not exceeding 30 mg/min, with weekly CBC/BMP/liver profile; metronidazole 2-4/day over 30-60 minutes with weekly CBC and peripheral-neuropathy risk; consider oral change | RENDERED: Clindamycin ... 3–4 ... 10–60 min (not to exceed 30 mg/min) ... 1 1 1 ... Consider change to po ... Metronidazole ... 2–4 ... 30–60 min ... 1 ... Peripheral neuropathy ... Consider change to po | idsa-2018 | 7 | p7/table-2/clindamycin-metronidazole | table |
| daptomycin-table | normal-organ-function | daptomycin daily by 2-minute push or 30-minute infusion; weekly CBC/BMP and baseline/weekly CK; stop if symptomatic CK >1000 U/L (about 5 times ULN) or asymptomatic CK >2000 U/L (about 10 times ULN) | RENDERED: Daptomycin ... 1 ... 2 min push or 30 min infusion ... 1 1 ... Myopathy; rhabdomyolysis ... Baseline and weekly CK, discontinue if symptomatic and CK >1000 U/L (~5× ULN) or asymptomatic and CK >2000 U/L (~10× ULN) | idsa-2018 | 6 | p6/table-2/daptomycin | table |
| carbapenem-table | normal-organ-function | ertapenem daily over 30 minutes; imipenem 3-4/day over 20-60 minutes depending on dose; meropenem 3-4/day over 30 minutes; each has weekly CBC/BMP/liver profile and hypersensitivity including anaphylaxis, while imipenem also carries seizure risk; limited stability can require delivery more often than weekly | RENDERED: Ertapenem ... 1 ... 30 min ... 1 1 1 ... Hypersensitivity including anaphylaxis ... Imipenem ... 3–4 ... 20–60 min depending on dose ... 1 1 1 ... Hypersensitivity including anaphylaxis; seizures ... Meropenem ... 3–4 ... 30 min ... 1 1 1 ... Hypersensitivity including anaphylaxis | idsa-2018 | 7 | p7/table-2/carbapenems | table |
| oxazolidinone-table | normal-organ-function | linezolid twice daily over 30-120 minutes and tedizolid daily over 60 minutes; weekly CBC and liver profile; thrombocytopenia, leukopenia, anemia, peripheral neuropathy, and optic neuritis; monitor neuropathy/optic neuritis with prolonged use, consider interactions and oral change | RENDERED: Linezolid ... 2 ... 30–120 min ... 1 ... 1 ... Thrombocytopenia; leukopenia; anemia; peripheral neuropathy; optic neuritis ... Consider change to po; monitor for neuropathy, optic neuritis in prolonged use ... Tedizolid ... 1 ... 60 min ... 1 ... 1 ... Thrombocytopenia; leukopenia; anemia; peripheral neuropathy; optic neuritis | idsa-2018 | 7 | p7/table-2/oxazolidinones | table |
| antistaphylococcal-penicillin-table | normal-organ-function | nafcillin 4-6/day over 30-60 minutes and oxacillin 4-6/day over 10-30 minutes; weekly CBC/BMP/liver profile; hypersensitivity including anaphylaxis and oxacillin hepatotoxicity; central access is commonly used because of phlebitis concern, not mandated by evidence | RENDERED: Nafcillin ... 4–6 ... 30–60 min ... 1 1 1 ... Hypersensitivity including anaphylaxis ... Oxacillin ... 4–6 ... 10–30 min ... 1 1 1 ... Hypersensitivity including anaphylaxis; hepatotoxicity ... Central line commonly used because of concern for phlebitis risk | idsa-2018 | 7 | p7/table-2/antistaphylococcal-penicillins | table |
| penicillin-g-table | normal-organ-function | penicillin G 4-6/day over 15-30 minutes; weekly CBC/BMP/liver profile; hypersensitivity including anaphylaxis; oral penicillin V potassium is not a substitute for most conditions requiring IV penicillin | RENDERED: Penicillin G ... 4–6 ... 15–30 min ... 1 1 1 ... Hypersensitivity including anaphylaxis ... Oral penicillin V K is not a substitute for IV treatment of most clinical conditions requiring IV penicillin | idsa-2018 | 7 | p7/table-2/penicillin-g | table |
| piperacillin-tazobactam-table | normal-organ-function | piperacillin-tazobactam 3-4/day over 30-240 minutes as an extended infusion; weekly CBC/BMP/liver profile; hypersensitivity including anaphylaxis | RENDERED: Piperacillin-tazobactam ... 3–4 ... 30–240 min (extended infusion) ... 1 1 1 ... Hypersensitivity including anaphylaxis | idsa-2018 | 7 | p7/table-2/piperacillin-tazobactam | table |
| polymyxin-table | normal-organ-function | colistin 2-4/day by 3-5-minute push or 30-minute infusion and polymyxin B daily over 60-90 minutes; weekly CBC and twice-weekly BMP; nephrotoxicity and neurotoxicity | RENDERED: Colistin ... 2–4 ... 3–5 min IVP; 30 min for infusion ... 1 2 ... Nephro- and neurotoxicity ... Polymyxin B ... 1 ... 60–90 min ... 1 2 ... Nephro- and neurotoxicity | idsa-2018 | 7 | p7/table-2/polymyxins | table |
| rifampin-table | normal-organ-function | rifampin 1-3/day over 30 minutes; weekly CBC/BMP/liver profile; hepatitis and hypersensitivity; evaluate drug interactions and consider oral change | RENDERED: Rifampin ... 1–3 ... 30 min ... 1 1 1 ... Hepatitis; hypersensitivity ... Potential for drug-drug interactions; consider change to po | idsa-2018 | 7 | p7/table-2/rifampin | table |
| long-acting-lipoglycopeptide-table | normal-organ-function | dalbavancin once weekly over 30 minutes, with red-man reaction more likely below 30 minutes; oritavancin once over 180 minutes, with red-man reaction more likely below 60 minutes; both carry hypersensitivity including anaphylaxis/infusion reactions; monitoring beyond 2 weeks or beyond the single dose is unknown | RENDERED: Dalbavancin ... Once per week ... 30 min ... Red man syndrome more likely if infusion <30 min ... monitoring requirements unknown for treatment duration greater than 2 weeks ... Oritavancin ... Once ... 180 min ... Red man syndrome more likely if infusion <60 min ... monitoring requirements unknown for treatment duration greater than a single dose | idsa-2018 | 6 | p6/table-2/long-acting-lipoglycopeptides | table |
| vancomycin-table | normal-organ-function | vancomycin 1-2/day over 60-120 minutes; weekly CBC/BMP and trough or AUC/MIC with dose changes; nephrotoxicity and infusion reactions; red-man reaction is more likely if infusion is shorter than 60 minutes | RENDERED: Vancomycin ... 1–2 ... 60–120 min ... trough levels or area under the curve/minimum inhibitory concentration weekly and with dose changes | idsa-2018 | 8 | p8/table-2/vancomycin | table |
| telavancin-table | normal-organ-function | telavancin daily over 60 minutes with weekly CBC and twice-weekly BMP; renal injury, anaphylaxis, infusion reaction, and QTc prolongation; renal injury risk is high above age 65, with renal impairment, or other nephrotoxins | RENDERED: Telavancin ... 1 ... 60 min ... 1 2 ... Nephrotoxicity; hypersensitivity including anaphylaxis; infusion-related prolongation of QTc ... High rate of renal injury in patients aged >65 years, with preexisting renal impairment or other nephrotoxins | idsa-2018 | 8 | p8/table-2/telavancin | table |
| tmp-smx-table | normal-organ-function | trimethoprim/sulfamethoxazole 2-4/day over 60-90 minutes with weekly CBC/BMP/liver profile; hyperkalemia, rash, nephrotoxicity, Stevens-Johnson syndrome, high fluid need and drug interactions; consider oral change | RENDERED: Trimethoprim/sulfamethoxazole ... 2–4 ... 60–90 min ... 1 1 1 ... Hyperkalemia; rash; nephrotoxicity; Stevens Johnson syndrome ... Consider change to po | idsa-2018 | 8 | p8/table-2/tmp-smx | table |
| tigecycline-table | normal-organ-function | tigecycline twice daily over 30-60 minutes; weekly CBC/BMP/liver profile; nausea and vomiting | RENDERED: Tigecycline ... 2 ... 30–60 min ... 1 1 1 ... Nausea/vomiting | idsa-2018 | 8 | p8/table-2/tigecycline | table |
| amphotericin-table | normal-organ-function | amphotericin B daily: liposomal over 2 hours or deoxycholate over 2-4 hours; weekly CBC/liver profile and twice-weekly BMP; sodium loading and chemistry 10 preferred; renal failure, electrolyte, infusion, hematologic, and hepatic harms | RENDERED: Amphotericin B ... 1 ... Liposomal: 2 hours Deoxycholate: 2–4 hours ... 1 2 1 ... renal failure ... electrolyte abnormalities ... Sodium loading recommended; chemistry 10 preferred | idsa-2018 | 10 | p10/table-3/amphotericin | table |
| echinocandin-azole-table | normal-organ-function | anidulafungin daily over 1.5 hours, caspofungin and micafungin daily over 1 hour, each with weekly CBC/BMP/liver profile; fluconazole daily over 1-2 hours not exceeding 200 mg/hour with weekly liver profile; isavuconazole 1-3/day over at least 1 hour with weekly liver profile; posaconazole 1-2/day over 90 minutes through an inline filter with weekly CBC/BMP/liver profile; consider oral azoles and drug interactions | RENDERED: Anidulafungin ... 1 ... 1.5 hours ... 1 1 1 ... Caspofungin ... 1 ... 1 hour ... 1 1 1 ... Fluconazole ... 1 ... 1–2 hours (not to exceed 200 mg/h) ... Isavuconazole ... 1–3 ... ≥1 hour ... Micafungin ... 1 ... 1 hour ... 1 1 1 ... Posaconazole ... 1–2 ... 90 min with in-line filter ... 1 1 1 | idsa-2018 | 10 | p10/table-3/echinocandins-azoles | table |
| voriconazole-table | normal-organ-function | voriconazole twice daily over 1-2 hours with weekly CBC/BMP/liver profile and plasma levels; hallucinations, sensory/skin/fluorosis harms and interactions; avoid IV formulation at CrCl below 50 unless benefit clearly outweighs cyclodextrin risk | RENDERED: Voriconazole ... 2 ... 1–2 hours ... 1 1 1 ... Hallucinations; auditory/visual disturbances; skin changes; fluorosis with prolonged use ... monitor plasma concentrations; avoid intravenous formulations if CrCl <50 unless benefits clearly outweigh risks | idsa-2018 | 10 | p10/table-3/voriconazole | table |
| acyclovir-table | normal-organ-function | acyclovir 3/day over 1 hour with weekly CBC/BMP; hydration is critical against crystalluria/acute renal injury and oral valacyclovir, famciclovir, or acyclovir should be considered | RENDERED: Acyclovir ... 3 ... 1 hour ... 1 1 ... Crystalluria; acute renal injury ... Hydration critical in preventing nephrotoxicity; consider change to po valacyclovir, famciclovir, or acyclovir | idsa-2018 | 10 | p10/table-3/acyclovir | table |
| cidofovir-table | normal-organ-function | cidofovir daily over 1 hour with weekly CBC/liver profile and twice-weekly BMP; normal saline before/after, consider probenecid, weekly urinalysis and chemistry 10; renal, metabolic, ocular, hematologic, and rash harms | RENDERED: Cidofovir ... 1 ... 1 hour ... 1 2 1 ... nephrotoxicity; metabolic acidosis ... Hydrate with NS before and after dose; consider probenecid; urinalysis weekly; chemistry 10 preferred | idsa-2018 | 10 | p10/table-3/cidofovir | table |
| foscarnet-table | normal-organ-function | foscarnet 1-3/day over 1-2 hours, not exceeding 1 mg/kg/min; weekly CBC/liver profile and twice-weekly BMP; hydrate before first dose and prefer chemistry 10; renal, neurologic, hematologic, and electrolyte harms | RENDERED: Foscarnet ... 1–3 ... 1–2 hours (not to exceed 1 mg/kg/min) ... 1 2 1 ... Nephro- and neurotoxicity ... electrolyte disturbances ... Hydrate ... prior to first dose; chemistry 10 preferred | idsa-2018 | 10 | p10/table-3/foscarnet | table |
| ganciclovir-table | normal-organ-function | ganciclovir 1-2/day over 1 hour with twice-weekly CBC and weekly BMP; dose-dependent myelosuppression; consider oral valganciclovir | RENDERED: Ganciclovir ... 1–2 ... 1 hour ... 2 1 ... Dose-dependent myelosuppression ... Consider change to po valganciclovir | idsa-2018 | 11 | p11/table-3/ganciclovir | table |
| benefit-harm | opat-patients | OPAT can reduce inpatient cost and permit earlier return to usual home activities | RENDERED: The advantages of OPAT relative to prolonged hospitalization are substantial. These include decreased medical costs and an earlier return to usual daily activities at home both for patients and caregivers. | idsa-2018 | 31 | p31/narrative/opat-benefit | narrative |
| benefit-harm | oral-switch-candidate | avoiding OPAT and central access improves safety when effective oral therapy can substitute without compromising cure | RENDERED: oral therapy can be substituted for OPAT without compromising cure rates. Safety is enhanced by avoiding OPAT-related complications | idsa-2018 | 31 | p31/narrative/oral-transition-harm-avoidance | narrative |
| opat-necessity | oral-switch-candidate | prescribe OPAT only when equivalent oral therapy is unavailable | RENDERED: ensuring that OPAT is only prescribed for patients where an equivalent oral therapy is not available is a high priority | idsa-2018 | 31 | p31/narrative/opat-only-if-needed | narrative |

## Conflicts

CONFLICT: midline-duration | adults-short-opat | `IDSA: a midline may replace central access when the planned OPAT course is less than 14 days` versus `MAGIC external criteria: use a midline for anticipated infusions lasting 14 or fewer days and prefer a PICC for 15 or more days` | IDSA's graded recommendation and the external MAGIC criteria place exactly day 14 on different sides of their verbal boundary. A functioning midline selected for an anticipated short course is not automatically exchanged if the course is unexpectedly extended.

No other exact within-population conflict was identified. IDSA's advanced-CKD tunneled-catheter action
and external eGFR/creatinine thresholds express the same vein-preservation goal at different
levels of specificity. The no-routine-prophylaxis statements apply to cancer cohorts and do
not resolve the IDSA no-recommendation boundary for prior CA-VTE in general OPAT. The 2004
first-dose healthcare-setting rule and weekly physician-visit practice are historical context;
the 2018 recommendation permits qualified home supervision and makes follow-up frequency
individual. Vancomycin's table language describes trough or AUC/MIC monitoring while the
2018 discussion notes that AUC/MIC use was emerging and not widespread; neither supplies a
target value in this source.

## Coverage

The bound record contains **23 = 12 cited + 11 disposed** marker occurrences. The 12
detailed occurrences are cited once each in rows above: p14 recommendation 1; p15
recommendation 2; p17 recommendation 4; p20 recommendation 6; p21 recommendation 7;
p22 recommendation 8; p23 recommendation 9; p25 recommendation 11; p26 recommendation
13; p27 recommendation 14; p28 recommendation 15; and p29 recommendation 17. The 11
summary occurrences are duplicates disposed individually below. Numbered actions 3, 5,
10, 12, and 16 explicitly state that no recommendation can be made and are retained as
narrative decision points; they are not marker occurrences in the bound record. Thus
marker silence is not used as evidence of clinical silence.

- `p1/grade-spelled-out/1` - duplicate summary occurrence.
- `p2/grade-spelled-out/1` - duplicate summary occurrence.
- `p2/grade-spelled-out/2` - duplicate summary occurrence.
- `p3/grade-spelled-out/1` - duplicate summary occurrence.
- `p3/grade-spelled-out/2` - duplicate summary occurrence.
- `p3/grade-spelled-out/3` - duplicate summary occurrence.
- `p3/grade-spelled-out/4` - duplicate summary occurrence.
- `p3/grade-spelled-out/5` - duplicate summary occurrence.
- `p3/grade-spelled-out/6` - duplicate summary occurrence.
- `p3/grade-spelled-out/7` - duplicate summary occurrence.
- `p3/grade-spelled-out/8` - duplicate summary occurrence.

## ADR 0009 disposition

- **Retained:** the OPAT definition; all 17 numbered actions, including all five
  no-recommendation/case-by-case branches; eligibility and care-setting requirements;
  Table 1 care-model differences; Tables 2-3 patient-changing administration,
  monitoring, oral-transition, adverse-event, and device constraints; first-dose,
  vascular-access, thrombosis, laboratory, drug-level, follow-up, and ID-review actions;
  pediatric, neonatal, elderly, PWID, CKD, dialysis, home, infusion-center, and SNF
  branches; benefits, harms, stewardship, and external decision thresholds.
- **Blinded after reading:** methods and evidence-grading mechanics, conflicts process,
  future-research agenda, acknowledgments, funding, and disclosures because they do not
  direct patient care.
- **Disposed:** Table 4 risk-of-bias machinery; Tables 5-8 and 10-17 study-design and
  comparative-effect detail except patient-changing harms or boundary evidence retained
  above; cohort sizes, P values, costs, and program-performance figures; author and
  reference metadata.
- **References:** pages 32-35 were read as part of the cold sweep and are exempt from
  patient-action extraction; externally attributed thresholds or recommendations used by
  the guideline are preserved at their clinical discussion pages, with organization
  provenance in the row or conflict text.
