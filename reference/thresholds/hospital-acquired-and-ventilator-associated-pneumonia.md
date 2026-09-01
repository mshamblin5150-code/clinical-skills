# Hospital-acquired and ventilator-associated pneumonia — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the guideline** and not a clinical instruction: every row is a fact this repo restates, and choosing among them is the clinician's.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-hap-vap-2016 | IDSA/ATS | IDSA/ciw353 | guideline | 2016 | 2016 | https://doi.org/10.1093/cid/ciw353 | chosen | bound |

The source is bound: `IDSA/ciw353`.

## Scope

**Read:** all 51 pages, including 89 bound recommendation manifestations, Tables 1-4, diagnostic evidence, treatment evidence, administrative matter, and references.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| title, abstract, and executive recommendations | 1-8 | yes |
| scope, methods, resistance risks, and definitions | 9-12 | read 2026-09-01; blind 2026-09-01 |
| microbiologic diagnosis and cultures | 13-16 | yes |
| biomarker, CPIS, and VAT evidence | 16-20 | read 2026-09-01; blind 2026-09-01 |
| VAP empiric therapy and Table 3 | 21-25 | yes |
| HAP empiric therapy, Table 4, and PK/PD | 26-30 | read 2026-09-01; blind 2026-09-01 |
| inhaled and pathogen-specific therapy | 30-39 | read 2026-09-01; blind 2026-09-01 |
| duration, de-escalation, and discontinuation | 39-43 | read 2026-09-01; blind 2026-09-01 |
| references | 44-51 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| guideline-adults | nonimmunocompromised adults with hospital-acquired pneumonia or ventilator-associated pneumonia |
| suspected-vap | adults with suspected ventilator-associated pneumonia |
| suspected-hap | adults with suspected hospital-acquired pneumonia that is not ventilator-associated |
| suspected-hap-vap | adults with suspected HAP/VAP |
| all-suspected-vap | all adults with suspected VAP |
| suspected-hap-culture-results | adults with suspected HAP for whom blood-culture results are available |
| vat | adults with ventilator-associated tracheobronchitis |
| vap-mrsa-risk | suspected VAP with an antimicrobial-resistance risk, ICU MRSA prevalence >10%-20%, or unknown MRSA prevalence |
| vap-low-mrsa-risk | suspected VAP without antimicrobial-resistance risks in an ICU with MRSA prevalence <10%-20% |
| vap-double-pseudomonas | suspected VAP with an antimicrobial-resistance risk, >10% gram-negative resistance to contemplated monotherapy, unknown local susceptibility, or structural lung disease such as bronchiectasis or cystic fibrosis |
| vap-mrsa-double-pseudomonas | suspected VAP requiring both empiric MRSA coverage and double antipseudomonal or gram-negative coverage |
| vap-single-pseudomonas | suspected VAP without antimicrobial-resistance risks in an ICU where <=10% of gram-negative isolates resist the contemplated monotherapy agent |
| hap-empiric-all | all adults treated empirically for HAP |
| proven-mssa-hap | adults with microbiologically proven MSSA HAP |
| hap-not-high-no-mrsa | empirically treated HAP not at high mortality risk and without factors increasing MRSA likelihood |
| hap-not-high-with-mrsa | empirically treated HAP not at high mortality risk but with factors increasing MRSA likelihood |
| hap-high-or-prior-iv | empirically treated HAP with high mortality risk or IV antibiotics during the prior 90 days |
| hap-severe-penicillin-allergy | empirically treated HAP with severe penicillin allergy in whom aztreonam replaces every beta-lactam |
| hap-mrsa-risk | empirically treated HAP with IV antibiotics in the prior 90 days, unit MRSA prevalence >20% or unknown, ventilatory support due to HAP, or septic shock |
| hap-double-pseudomonas | empirically treated HAP with IV antibiotics in the prior 90 days, high mortality risk, bronchiectasis, or cystic fibrosis |
| pseudomonas-stable | proven P. aeruginosa HAP/VAP, susceptibility known, without septic shock or high mortality risk |
| pseudomonas-high-risk | proven P. aeruginosa HAP/VAP with persistent septic shock or high mortality risk when susceptibility is known |
| only-polymyxin-susceptible | HAP/VAP caused by Acinetobacter or another carbapenem-resistant pathogen susceptible only to polymyxins |
| severe-organ-dysfunction | patients whose hepatic or renal dysfunction requires individualized initial dose or interval modification |

## Quantities

| key | meaning |
| --- | --- |
| applicability | source population and exclusions |
| diagnostic-sampling | respiratory sampling method |
| culture-threshold-action | action below quantitative culture threshold |
| initiation-pct | PCT boundary for antibiotic initiation |
| initiation-strem1 | BAL-fluid sTREM-1 boundary for antibiotic initiation |
| initiation-crp | CRP boundary for antibiotic initiation |
| initiation-cpis | CPIS boundary for antibiotic initiation |
| empiric-coverage | organisms and drug classes covered initially |
| hap-universal-coverage | universal empiric HAP organism coverage |
| hap-penicillin-allergy | severe-penicillin-allergy MSSA safeguard |
| vap-antibiogram | VAP-specific antibiogram action |
| hap-antibiogram | HAP-specific antibiogram action |
| vap-blood-culture | universal VAP blood-culture action |
| hap-blood-culture-use | HAP blood-culture evidence and result use |
| resistance-risk | resistance and mortality risk boundary |
| table3-mrsa-dose | Table 3 MRSA-column dose and interval |
| table3-beta-lactam-dose | Table 3 beta-lactam-column dose and interval |
| table3-non-beta-dose | Table 3 non-beta-lactam-column dose and interval |
| colistin-dose | colistin loading and maintenance dose |
| polymyxin-equivalence | colistin and polymyxin unit equivalence |
| table4-low-no-mrsa-dose | Table 4 not-high/no-MRSA branch dose |
| table4-low-with-mrsa-dose | Table 4 not-high/with-MRSA branch dose |
| table4-high-risk-dose | Table 4 high-mortality/prior-IV branch dose |
| antibiotic-dose | other antimicrobial dose and interval |
| definitive-mrsa | definitive MRSA therapy |
| definitive-pseudomonas | definitive Pseudomonas therapy |
| definitive-esbl | definitive ESBL therapy |
| definitive-acinetobacter | definitive Acinetobacter therapy |
| treatment-duration | antimicrobial course length |
| de-escalation | narrowing an empiric regimen |
| pct-discontinuation | PCT-guided stopping decision |
| cpis-discontinuation | CPIS stopping boundary |
| harm-safeguard | avoidance or monitoring safeguard |

## Thresholds

| quantity | population | value | snippet | source | page | source locator | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| applicability | guideline-adults | applies to nonimmunocompromised adults with HAP/VAP; immunosuppressed patients at risk for opportunistic pulmonary infection may require an alternative approach | RENDERED: guidance on the most effective diagnosis and management of nonimmunocompromised patients with HAP/VAP ... Patients with immunosuppression ... often requires an alternative approach | idsa-hap-vap-2016 | p8 | p8/narrative/scope-and-purpose | narrative |
| diagnostic-sampling | suspected-vap | prefer noninvasive endotracheal aspiration with semiquantitative culture over invasive quantitative or noninvasive quantitative culture | We suggest noninvasive sampling with semiquantitative cultures to diagnose VAP | idsa-hap-vap-2016 | p2 | p2/narrative/recommendation-i | narrative |
| culture-threshold-action | suspected-vap | if invasive quantitative culture was performed and PSB is <10^3 CFU/mL or BAL is <10^4 CFU/mL, withhold rather than continue antibiotics, while considering alternative infection source, prior antibiotics, clinical suspicion, severe sepsis, and improvement | RENDERED: PSB With <10^3 ... CFU/mL, BAL With <10^4 CFU/mL ... antibiotics be withheld rather than continued | idsa-hap-vap-2016 | p2 | p2/narrative/recommendation-ii | narrative |
| diagnostic-sampling | suspected-hap | guide treatment by microbiologic studies on noninvasively obtained respiratory samples rather than treating empirically; methods include expectoration, induced sputum, nasotracheal suction, and endotracheal aspiration | RENDERED: We suggest that patients with suspected HAP (non-VAP) be treated according to the results of microbiologic studies performed on respiratory samples obtained noninvasively | idsa-hap-vap-2016 | p2 | p2/narrative/recommendation-iii | narrative |
| vap-blood-culture | all-suspected-vap | obtain blood cultures; use results to identify nonpulmonary infection and to target therapy | RENDERED: remain in favor of blood cultures for all patients with suspected VAP ... blood cultures results might provide evidence of a nonpulmonary source of infection | idsa-hap-vap-2016 | p13 | p13/narrative/vap-blood-cultures | narrative |
| hap-blood-culture-use | suspected-hap-culture-results | direct evidence for obtaining blood cultures in all HAP is limited; available results may guide treatment and de-escalation | RENDERED: no studies were identified that specifically evaluated blood cultures in patients with HAP ... blood culture data can be used to guide antibiotic treatment ... de-escalation | idsa-hap-vap-2016 | p13 | p13/narrative/hap-blood-culture-use | narrative |
| initiation-pct | suspected-hap-vap | use clinical criteria alone, not serum PCT plus clinical criteria | RENDERED: recommend using clinical criteria alone, rather than using serum PCT plus clinical criteria | idsa-hap-vap-2016 | p2 | p2/narrative/recommendation-iv | narrative |
| initiation-strem1 | suspected-hap-vap | use clinical criteria alone, not BAL-fluid sTREM-1 plus clinical criteria | RENDERED: using clinical criteria alone, rather than using bronchoalveolar lavage fluid (BALF) sTREM-1 plus clinical criteria | idsa-hap-vap-2016 | p2 | p2/narrative/recommendation-v | narrative |
| initiation-crp | suspected-hap-vap | use clinical criteria alone, not CRP plus clinical criteria | RENDERED: recommend using clinical criteria alone rather than using CRP plus clinical criteria | idsa-hap-vap-2016 | p3 | p3/narrative/recommendation-vi | narrative |
| initiation-cpis | suspected-hap-vap | use clinical criteria alone, not CPIS plus clinical criteria | RENDERED: suggest using clinical criteria alone, rather than using CPIS plus clinical criteria | idsa-hap-vap-2016 | p3 | p3/narrative/recommendation-vii | narrative |
| empiric-coverage | vat | do not provide antibiotics routinely; mucus plugging and weaning difficulty may justify treatment in selected cases | In patients with VAT, we suggest not providing antibiotic therapy | idsa-hap-vap-2016 | p3 | p3/narrative/recommendation-viii | narrative |
| vap-antibiogram | suspected-vap | hospitals regularly generate and disseminate a local antibiogram, ideally ICU-specific; base empiric VAP regimens on local pathogen distribution and susceptibility, with update frequency set by change rate, resources, and data volume | RENDERED: all hospitals regularly generate and disseminate a local antibiogram, ideally one that is specific to their intensive care population ... empiric treatment regimens be informed by the local distribution of pathogens associated with VAP and their antimicrobial susceptibilities | idsa-hap-vap-2016 | p3 | p3/narrative/recommendation-ix | narrative |
| empiric-coverage | suspected-vap | every empiric regimen covers S. aureus, P. aeruginosa, and other gram-negative bacilli | RENDERED: recommend including coverage for S. aureus, P. aeruginosa, and other gram-negative bacilli in all empiric regimens | idsa-hap-vap-2016 | p3 | p3/narrative/recommendation-x | narrative |
| resistance-risk | vap-mrsa-risk | include MRSA coverage when unit MRSA prevalence is >10%-20%, unknown, or another resistance risk exists | units where >10%-20% of S. aureus isolates are methicillin resistant, and patients in units where the prevalence of MRSA is not known | idsa-hap-vap-2016 | p3 | p3/narrative/vap-mrsa-threshold | narrative |
| resistance-risk | vap-low-mrsa-risk | use MSSA rather than MRSA coverage when unit MRSA prevalence is <10%-20% and no resistance risk exists | RENDERED: ICUs where <10%-20% of S. aureus isolates are methicillin resistant | idsa-hap-vap-2016 | p3 | p3/narrative/vap-mssa-threshold | narrative |
| empiric-coverage | vap-mrsa-risk | vancomycin or linezolid | If empiric coverage for MRSA is indicated, we recommend either vancomycin or linezolid | idsa-hap-vap-2016 | p3 | p3/narrative/vap-mrsa-agents | narrative |
| empiric-coverage | vap-low-mrsa-risk | for MSSA-only empiric coverage use piperacillin-tazobactam, cefepime, levofloxacin, imipenem, or meropenem; reserve oxacillin, nafcillin, or cefazolin for proven MSSA | RENDERED: regimen including piperacillin-tazobactam, cefepime, levofloxacin, imipenem, or meropenem ... Oxacillin, nafcillin, or cefazolin are preferred agents for treatment of proven MSSA | idsa-hap-vap-2016 | p21 | p21/narrative/vap-mssa-agents | narrative |
| resistance-risk | vap-double-pseudomonas | use 2 antipseudomonal drugs from different classes for prior IV antibiotics within 90 days, septic shock at VAP, ARDS preceding VAP, five or more hospital days before VAP, acute renal replacement therapy before VAP, >10% resistance, unknown susceptibility, bronchiectasis, or cystic fibrosis | RENDERED: Table 2 ... Prior intravenous antibiotic use within 90 d ... Septic shock at time of VAP ... ARDS preceding VAP ... Five or more days of hospitalization ... Acute renal replacement therapy prior to VAP onset ... >10% ... 2 antipseudomonal agents | idsa-hap-vap-2016 | p3 | p3/table2/vap-mdr-risk | table |
| resistance-risk | vap-single-pseudomonas | use one antipseudomonal agent when no resistance risk exists and <=10% of gram-negative isolates resist the contemplated monotherapy agent | RENDERED: one antibiotic active against P. aeruginosa ... without risk factors ... ICUs where <=10% of gram-negative isolates are resistant | idsa-hap-vap-2016 | p4 | p4/narrative/vap-one-agent | narrative |
| harm-safeguard | suspected-vap | avoid aminoglycosides and colistin when adequate alternatives exist because superfluous treatment can cause adverse drug effects, C. difficile infection, resistance, cost, and agent toxicity | RENDERED: avoiding aminoglycosides ... avoiding colistin ... adverse drug effects, Clostridium difficile infections, antibiotic resistance, and increased cost | idsa-hap-vap-2016 | p4 | p4/narrative/vap-agent-avoidance | narrative |
| table3-mrsa-dose | vap-mrsa-double-pseudomonas | MRSA column: vancomycin 15 mg/kg IV q8-12h, with 25-30 mg/kg once loading dose for severe illness; or linezolid 600 mg IV q12h | RENDERED: Vancomycin 15 mg/kg IV q8-12h (consider a loading dose of 25-30 mg/kg x 1 for severe illness) ... Linezolid 600 mg IV q12h | idsa-hap-vap-2016 | p4 | p4/table3/mrsa-column | table |
| table3-beta-lactam-dose | vap-mrsa-double-pseudomonas | beta-lactam column: piperacillin-tazobactam 4.5 g IV q6h; cefepime or ceftazidime 2 g IV q8h; imipenem 500 mg IV q6h; meropenem 1 g IV q8h; aztreonam 2 g IV q8h | RENDERED: Piperacillin-tazobactam 4.5 g IV q6h ... Cefepime 2 g IV q8h ... Ceftazidime 2 g IV q8h ... Imipenem 500 mg IV q6h ... Meropenem 1 g IV q8h ... Aztreonam 2 g IV q8h | idsa-hap-vap-2016 | p4 | p4/table3/beta-lactam-column | table |
| table3-non-beta-dose | vap-mrsa-double-pseudomonas | non-beta-lactam column: ciprofloxacin 400 mg IV q8h; levofloxacin 750 mg IV q24h; amikacin 15-20 mg/kg IV q24h; gentamicin or tobramycin 5-7 mg/kg IV q24h; polymyxin B 2.5-3.0 mg/kg/day divided in 2 IV doses | RENDERED: Ciprofloxacin 400 mg IV q8h ... Levofloxacin 750 mg IV q24h ... Amikacin 15-20 mg/kg IV q24h ... Gentamicin 5-7 mg/kg IV q24h ... Tobramycin 5-7 mg/kg IV q24h ... Polymyxin B 2.5-3.0 mg/kg/d divided in 2 daily IV doses | idsa-hap-vap-2016 | p4 | p4/table3/non-beta-lactam-column | table |
| colistin-dose | only-polymyxin-susceptible | colistin loading 5 mg/kg IV once, then 2.5 mg x (1.5 x CrCl + 30) IV q12h; drug levels and renal/hepatic adjustment are required where applicable | RENDERED: Colistin 5 mg/kg IV x 1 (loading dose) followed by 2.5 mg x (1.5 x CrCl + 30) IV q12h | idsa-hap-vap-2016 | p4 | p4/table3/colistin-dose | table |
| harm-safeguard | severe-organ-dysfunction | modify initial doses for hepatic or renal dysfunction; obtain drug levels and adjust doses or intervals for vancomycin, aminoglycosides, and polymyxins; imipenem may need reduction below 70 kg to prevent seizures; extended beta-lactam infusions may be appropriate | RENDERED: initial doses ... may need to be modified for patients with hepatic or renal dysfunction ... Drug levels and adjustment of doses and/or intervals required ... dose may need to be lowered in patients weighing <70 kg to prevent seizures ... Extended infusions may be appropriate | idsa-hap-vap-2016 | p4 | p4/table3/dose-footnotes | table |
| empiric-coverage | vap-double-pseudomonas | aztreonam may be combined with another beta-lactam only when other options are absent because it has different bacterial-cell-wall targets; polymyxins are reserved for high-MDR settings with local expertise | RENDERED: In the absence of other options, it is acceptable to use aztreonam as an adjunctive agent with another beta-lactam-based agent because it has different targets ... Polymyxins should be reserved for settings where there is a high prevalence of multidrug resistance and local expertise | idsa-hap-vap-2016 | p4 | p4/table3/agent-footnotes | table |
| polymyxin-equivalence | only-polymyxin-susceptible | source equivalences: 1 million IU colistin is about 30 mg colistin-base activity and about 80 mg colistimethate; polymyxin B 1 mg = 10 000 units | RENDERED: One million IU of colistin is equivalent to about 30 mg of CBA, which corresponds to about 80 mg of the prodrug colistimethate. Polymyxin B (1 mg = 10 000 units) | idsa-hap-vap-2016 | p4 | p4/table3/polymyxin-equivalence | table |
| hap-antibiogram | suspected-hap | hospitals regularly generate and disseminate a local antibiogram tailored to HAP when possible; base empiric regimens on local HAP pathogen distribution and susceptibility | RENDERED: all hospitals regularly generate and disseminate a local antibiogram, ideally one that is tailored to their HAP population ... empiric antibiotic regimens be based upon the local distribution of pathogens associated with HAP and their antimicrobial susceptibilities | idsa-hap-vap-2016 | p4 | p4/narrative/recommendation-xi | narrative |
| hap-universal-coverage | hap-empiric-all | every empiric HAP regimen covers S. aureus and P. aeruginosa plus other gram-negative bacilli | RENDERED: patients being treated empirically for HAP ... antibiotic with activity against S. aureus ... antibiotics with activity against P. aeruginosa and other gram-negative bacilli | idsa-hap-vap-2016 | p5 | p5/narrative/hap-universal-coverage | narrative |
| resistance-risk | hap-mrsa-risk | include MRSA therapy for prior IV antibiotic use within 90 days, unit MRSA prevalence >20% or unknown, ventilatory support due to HAP, or septic shock | RENDERED: prior intravenous antibiotic use within 90 days ... >20% ... prevalence ... not known ... ventilatory support due to HAP and septic shock | idsa-hap-vap-2016 | p5 | p5/narrative/hap-mrsa-threshold | narrative |
| resistance-risk | hap-double-pseudomonas | use 2 antipseudomonal classes for prior IV antibiotics within 90 days, high mortality risk, bronchiectasis, or cystic fibrosis; do not use 2 beta-lactams | RENDERED: antibiotics from 2 different classes ... prior intravenous antibiotic use within 90 days ... bronchiectasis or cystic fibrosis ... avoid 2 beta-lactams | idsa-hap-vap-2016 | p5 | p5/table4/hap-double-coverage | table |
| table4-low-no-mrsa-dose | hap-not-high-no-mrsa | use one of: piperacillin-tazobactam 4.5 g IV q6h; cefepime 2 g IV q8h; levofloxacin 750 mg IV daily; imipenem 500 mg IV q6h; or meropenem 1 g IV q8h; ensure MSSA coverage | RENDERED: Not at High Risk of Mortality and no Factors Increasing the Likelihood of MRSA ... One of the following ... Piperacillin-tazobactam 4.5 g IV q6h ... Cefepime 2 g IV q8h ... Levofloxacin 750 mg IV daily ... Imipenem 500 mg IV q6h ... Meropenem 1 g IV q8h | idsa-hap-vap-2016 | p5 | p5/table4/not-high-no-mrsa | table |
| table4-low-with-mrsa-dose | hap-not-high-with-mrsa | use one gram-negative agent from the source column plus vancomycin 15 mg/kg IV q8-12h targeting source-era trough 15-20 mg/mL with 25-30 mg/kg once loading for severe illness, or linezolid 600 mg IV q12h | RENDERED: Not at High Risk of Mortality but With Factors Increasing the Likelihood of MRSA ... One of the following ... Plus: Vancomycin 15 mg/kg IV q8-12h ... 15-20 mg/mL trough ... 25-30 mg/kg IV x 1 ... OR Linezolid 600 mg IV q12h | idsa-hap-vap-2016 | p5 | p5/table4/not-high-with-mrsa | table |
| table4-high-risk-dose | hap-high-or-prior-iv | use 2 gram-negative agents from different classes, avoiding 2 beta-lactams, plus vancomycin or linezolid at the source doses | RENDERED: High Risk of Mortality or Receipt of Intravenous Antibiotics During the Prior 90 d ... Two of the following, avoid 2 beta-lactams ... Plus: Vancomycin 15 mg/kg IV q8-12h ... OR Linezolid 600 mg IV q12h | idsa-hap-vap-2016 | p5 | p5/table4/high-risk-or-prior-iv | table |
| hap-penicillin-allergy | hap-severe-penicillin-allergy | if aztreonam replaces every beta-lactam, add MSSA coverage | RENDERED: If patient has severe penicillin allergy and aztreonam is going to be used instead of any beta-lactam-based antibiotic, include coverage for MSSA | idsa-hap-vap-2016 | p5 | p5/table4/severe-penicillin-allergy | table |
| empiric-coverage | proven-mssa-hap | use oxacillin, nafcillin, or cefazolin for proven MSSA; these are not required empirically if an MSSA-active broad agent is already used | RENDERED: Oxacillin, nafcillin, or cefazolin are preferred for the treatment of proven MSSA, but are not necessary for empiric coverage of HAP | idsa-hap-vap-2016 | p6 | p6/narrative/proven-mssa | narrative |
| harm-safeguard | hap-empiric-all | do not use an aminoglycoside as the sole antipseudomonal agent | RENDERED: recommend not using an aminoglycoside as the sole antipseudomonal agent | idsa-hap-vap-2016 | p6 | p6/narrative/hap-aminoglycoside-monotherapy | narrative |
| antibiotic-dose | guideline-adults | use PK/PD data, blood concentrations, extended or continuous infusions, and weight-based dosing rather than relying only on manufacturer prescribing information | RENDERED: PK/PD-optimized dosing refers to the use of antibiotic blood concentrations, extended and continuous infusions, and weight-based dosing | idsa-hap-vap-2016 | p6 | p6/narrative/pk-pd | narrative |
| definitive-pseudomonas | only-polymyxin-susceptible | for VAP gram-negative bacilli susceptible only to aminoglycosides or polymyxins, use inhaled plus systemic therapy; adjunctive inhaled therapy may be a last resort for IV nonresponse | RENDERED: susceptible to only aminoglycosides or polymyxins ... both inhaled and systemic antibiotics | idsa-hap-vap-2016 | p6 | p6/narrative/inhaled-antibiotic | narrative |
| definitive-mrsa | guideline-adults | MRSA HAP/VAP: vancomycin or linezolid; choose with blood counts, serotonergic drugs, renal function, and cost | RENDERED: choice between vancomycin and linezolid may be guided by ... blood cell counts ... serotonin-reuptake inhibitors, renal function, and cost | idsa-hap-vap-2016 | p6 | p6/narrative/mrsa-definitive | narrative |
| definitive-pseudomonas | pseudomonas-stable | select a susceptible single agent; do not use aminoglycoside monotherapy | RENDERED: recommend monotherapy using an antibiotic to which the isolate is susceptible rather than combination therapy | idsa-hap-vap-2016 | p7 | p7/narrative/pseudomonas-monotherapy | narrative |
| definitive-pseudomonas | pseudomonas-high-risk | use 2 susceptible agents while septic shock or high mortality risk persists; high risk was >25% mortality and low risk <15%; stop combination when shock resolves | RENDERED: combination therapy using 2 antibiotics ... High risk of death ... >25%; low risk ... <15% ... septic shock resolves ... continued combination therapy is not recommended | idsa-hap-vap-2016 | p7 | p7/narrative/pseudomonas-combination | narrative |
| definitive-esbl | guideline-adults | ESBL-producing gram-negative HAP/VAP: select definitive therapy by susceptibility, allergies, and comorbidities | RENDERED: based upon the results of antimicrobial susceptibility testing and patient-specific factors | idsa-hap-vap-2016 | p7 | p7/narrative/esbl-definitive | narrative |
| definitive-acinetobacter | guideline-adults | susceptible Acinetobacter: carbapenem or ampicillin/sulbactam; only-polymyxin-susceptible: IV colistin or polymyxin B plus optional inhaled colistin; do not add rifampin when only colistin-sensitive; do not use tigecycline | RENDERED: carbapenem or ampicillin/sulbactam if the isolate is susceptible ... intravenous polymyxin ... adjunctive inhaled colistin ... not using adjunctive rifampicin ... against the use of tigecycline | idsa-hap-vap-2016 | p7 | p7/narrative/acinetobacter-therapy | narrative |
| harm-safeguard | only-polymyxin-susceptible | mix inhaled colistin with sterile water and administer promptly; do not use premixed inhaled colistin | Colistin for inhalation should be administered promptly after being mixed with sterile water | idsa-hap-vap-2016 | p7 | p7/narrative/inhaled-colistin-safety | narrative |
| treatment-duration | suspected-vap | 7 days rather than 8-15 days, with shorter or longer treatment according to clinical, radiologic, and laboratory improvement | RENDERED: 7 Days or 8-15 Days ... recommend a 7-day course ... shorter or longer duration ... depending upon the rate of improvement | idsa-hap-vap-2016 | p7 | p7/narrative/vap-duration | narrative |
| treatment-duration | suspected-hap | 7 days, with shorter or longer treatment according to clinical, radiologic, and laboratory improvement | For patients with HAP, we recommend a 7-day course of antimicrobial therapy | idsa-hap-vap-2016 | p8 | p8/narrative/hap-duration | narrative |
| de-escalation | guideline-adults | de-escalate from broad empiric therapy by narrowing agents or moving from combination therapy to monotherapy rather than keeping a fixed broad regimen | RENDERED: De-escalation refers to changing an empiric broad-spectrum antibiotic regimen to a narrower antibiotic regimen | idsa-hap-vap-2016 | p8 | p8/narrative/de-escalation | narrative |
| pct-discontinuation | guideline-adults | PCT plus clinical criteria may guide discontinuation; benefit is unknown where standard VAP therapy is already <=7 days | RENDERED: using PCT levels plus clinical criteria to guide the discontinuation ... not known ... where standard antimicrobial therapy for VAP is already 7 days or less | idsa-hap-vap-2016 | p8 | p8/narrative/pct-discontinuation | narrative |
| cpis-discontinuation | suspected-hap-vap | do not use CPIS to guide discontinuation | RENDERED: suggest not using the CPIS to guide the discontinuation of antibiotic therapy | idsa-hap-vap-2016 | p8 | p8/narrative/cpis-discontinuation | narrative |

## Conflicts

No same-quantity, same-population source conflict was retained. The MRSA, antipseudomonal, mono-versus-combination, and 7-day-duration branches apply to different risk strata or stages of care.

## Coverage

Stored recommendation records: 89. Cited recommendation records: 0. Scoped-out recommendation records: 89. Accounting: 89 = 0 + 89.

ADR 0009 disposition: all 89 bound grade-marker manifestations are individually disposed below because the same actions are retained in page-bound narrative/table rows; evidence-only epidemiology, comparative trial outcomes, methods, administrative prose, and references do not create additional patient-action rows.

- `p2/grade-spelled-out/1` - represented by page-bound narrative row.
- `p2/grade-spelled-out/2` - represented by page-bound narrative row.
- `p2/grade-spelled-out/3` - represented by page-bound narrative row.
- `p2/grade-spelled-out/4` - represented by page-bound narrative row.
- `p3/grade-spelled-out/1` - continuation fragment represented by page-bound narrative row.
- `p3/grade-spelled-out/2` - represented by page-bound narrative row.
- `p3/grade-spelled-out/3` - represented by page-bound narrative row.
- `p3/grade-spelled-out/4` - represented by page-bound narrative row.
- `p3/grade-spelled-out/5` - represented by page-bound narrative row.
- `p3/grade-spelled-out/6` - represented by page-bound narrative row.
- `p3/grade-spelled-out/7` - represented by page-bound narrative row.
- `p3/grade-spelled-out/8` - represented by page-bound narrative row.
- `p4/grade-spelled-out/1` - continuation fragment represented by page-bound narrative row.
- `p4/grade-spelled-out/2` - represented by page-bound narrative row.
- `p4/grade-spelled-out/3` - represented by page-bound narrative row.
- `p4/grade-spelled-out/4` - represented by page-bound narrative row.
- `p5/grade-spelled-out/1` - represented by page-bound narrative row.
- `p5/grade-spelled-out/2` - represented by page-bound narrative row.
- `p5/grade-spelled-out/3` - represented by page-bound narrative row.
- `p6/grade-spelled-out/1` - continuation represented by page-bound narrative row.
- `p6/grade-spelled-out/2` - represented by page-bound narrative row.
- `p6/grade-spelled-out/3` - represented by page-bound narrative row.
- `p6/grade-spelled-out/4` - represented by page-bound narrative row.
- `p6/grade-spelled-out/5` - represented by page-bound narrative row.
- `p6/grade-spelled-out/6` - represented by page-bound narrative row.
- `p6/grade-spelled-out/7` - represented by page-bound narrative row.
- `p6/grade-spelled-out/8` - represented by page-bound narrative row.
- `p6/grade-spelled-out/9` - represented by page-bound narrative row.
- `p7/grade-spelled-out/1` - represented by page-bound narrative row.
- `p7/grade-spelled-out/2` - represented by page-bound narrative row.
- `p7/grade-spelled-out/3` - duplicate action represented by page-bound narrative row.
- `p7/grade-spelled-out/4` - represented by page-bound narrative row.
- `p7/grade-spelled-out/5` - represented by page-bound narrative row.
- `p7/grade-spelled-out/6` - partial manifestation represented by page-bound narrative row.
- `p7/grade-spelled-out/7` - complete manifestation represented by page-bound narrative row.
- `p7/grade-spelled-out/8` - represented by page-bound narrative row.
- `p7/grade-spelled-out/9` - represented by page-bound narrative row.
- `p7/grade-spelled-out/10` - partial manifestation represented by page-bound narrative row.
- `p7/grade-spelled-out/11` - complete manifestation represented by page-bound narrative row.
- `p7/grade-spelled-out/12` - represented by page-bound narrative row.
- `p8/grade-spelled-out/1` - represented by page-bound narrative row.
- `p8/grade-spelled-out/2` - represented by page-bound narrative row.
- `p8/grade-spelled-out/3` - represented by page-bound narrative row.
- `p8/grade-spelled-out/4` - represented by page-bound narrative row.
- `p13/grade-spelled-out/1` - detailed duplicate represented by p2 row.
- `p14/grade-spelled-out/1` - detailed duplicate represented by p2 row.
- `p15/grade-spelled-out/1` - detailed duplicate represented by p2 row.
- `p16/grade-spelled-out/1` - detailed duplicate represented by p2 row.
- `p17/grade-spelled-out/1` - detailed duplicate represented by p2 row.
- `p18/grade-spelled-out/1` - detailed duplicate represented by p3 row.
- `p18/grade-spelled-out/2` - detailed duplicate represented by p3 row.
- `p19/grade-spelled-out/1` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/1` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/2` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/3` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/4` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/5` - detailed duplicate represented by p3 row.
- `p21/grade-spelled-out/6` - detailed duplicate represented by p4 row.
- `p21/grade-spelled-out/7` - detailed duplicate represented by p4 row.
- `p21/grade-spelled-out/8` - detailed duplicate represented by p4 row.
- `p21/grade-spelled-out/9` - detailed duplicate represented by p4 row.
- `p26/grade-spelled-out/1` - detailed duplicate represented by p5 row.
- `p26/grade-spelled-out/2` - detailed duplicate represented by p5 row.
- `p26/grade-spelled-out/3` - detailed duplicate represented by p5 row.
- `p26/grade-spelled-out/4` - detailed duplicate represented by p6 row.
- `p26/grade-spelled-out/5` - detailed duplicate represented by p6 row.
- `p26/grade-spelled-out/6` - detailed duplicate represented by p6 row.
- `p26/grade-spelled-out/7` - detailed duplicate represented by p6 row.
- `p29/grade-spelled-out/1` - detailed duplicate represented by p6 row.
- `p30/grade-spelled-out/1` - detailed duplicate represented by p6 row.
- `p31/grade-spelled-out/1` - detailed duplicate represented by p6 row.
- `p33/grade-spelled-out/1` - continuation fragment represented by p6 definitive-therapy row.
- `p33/grade-spelled-out/2` - detailed duplicate represented by p6 row.
- `p34/grade-spelled-out/1` - detailed duplicate represented by p7 row.
- `p34/grade-spelled-out/2` - detailed duplicate represented by p7 row.
- `p34/grade-spelled-out/3` - duplicate action represented by p7 row.
- `p36/grade-spelled-out/1` - detailed duplicate represented by p7 row.
- `p37/grade-spelled-out/1` - detailed duplicate represented by p7 row.
- `p37/grade-spelled-out/2` - partial manifestation represented by p7 row.
- `p37/grade-spelled-out/3` - complete manifestation represented by p7 row.
- `p37/grade-spelled-out/4` - detailed duplicate represented by p7 row.
- `p37/grade-spelled-out/5` - detailed duplicate represented by p7 row.
- `p38/grade-spelled-out/1` - partial manifestation represented by p7 row.
- `p38/grade-spelled-out/2` - complete manifestation represented by p7 row.
- `p39/grade-spelled-out/1` - detailed duplicate represented by p7 row.
- `p40/grade-spelled-out/1` - detailed duplicate represented by p8 row.
- `p41/grade-spelled-out/1` - detailed duplicate represented by p8 row.
- `p42/grade-spelled-out/1` - detailed duplicate represented by p8 row.
- `p42/grade-spelled-out/2` - detailed duplicate represented by p8 row.
