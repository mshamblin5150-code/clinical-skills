# Antimicrobial-Resistant Gram-Negative Infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-amr-2026 | IDSA | IDSA/amr-guidance-update | guideline | 2026 guidance | 2026-03-01 | https://www.idsociety.org/practice-guideline/amr-guidance/ | stated | null |

## Scope

**Read:** the complete 140-page guidance, page by page, including title material,
abstract, introduction, general management suggestions, adult dosing Table 1,
susceptibility-breakpoint Table 2 and all footnotes, all six organism/resistance
sections and their 31 question-and-answer discussions, conclusions,
acknowledgments, disclosures, and references. Every table and displayed numeric
example was read in page context. The current PDF-bound recommendation sweep at
`IDSA/amr-guidance-update.json` reported `nothing-found` with 0 recommendations;
the page sweep, not that null marker inventory, is the denominator.

**Not read:** nothing in the source page range. The references were inspected for
scope and retired by class because they contain citations rather than clinical
prose.

**Scoped out under ADR 0009's numeric patient-action rule:** publication and access
dates, study sizes, study-treatment regimens that the panel does not adopt,
percentages, confidence intervals, risk and outcome estimates, prevalence and
surveillance rates, mortality and cure rates, resistance-emergence frequencies,
pharmacodynamic exposure targets used only in models, historical breakpoints,
reference numbers, molecular-mechanism quantities, and development metadata were
read but do not themselves change what is done to a patient. Qualitative treatment
preferences without a numeric dose, duration, target, cutoff, or interval do not
produce threshold rows.

**Source: `idsa-amr-2026`**

| span | pages | read |
| --- | --- | --- |
| title, abstract, introduction, and general management | 1-4 | read 2026-08-31; blind 2026-08-31 |
| empiric lookback periods, duration, and oral-transition considerations | 5-6 | yes |
| adult antibiotic dosing Table 1 | 7-10 | yes |
| susceptibility-breakpoint Table 2 and ESBL-E introduction | 11-12 | yes |
| ESBL-E treatment questions and rationales | 13-30 | yes |
| AmpC-E biology and qualitative selection considerations | 31-34 | read 2026-08-31; blind 2026-08-31 |
| AmpC-E numeric susceptibility decisions and remaining questions | 35-42 | yes |
| CRE introduction and nonnumeric treatment framework | 43-44 | read 2026-08-31; blind 2026-08-31 |
| CRE treatment questions and rationales | 45-60 | yes |
| CRE combination conclusion and MDR Pseudomonas introduction | 61-62 | read 2026-08-31; blind 2026-08-31 |
| MDR and DTR Pseudomonas treatment questions and rationales | 63-75 | yes |
| DTR Pseudomonas nebulized-therapy conclusion | 76 | read 2026-08-31; blind 2026-08-31 |
| CRAB introduction | 77 | read 2026-08-31; blind 2026-08-31 |
| CRAB treatment questions and rationales | 78-87 | yes |
| CRAB nebulized-therapy conclusion and S. maltophilia introduction | 88-89 | read 2026-08-31; blind 2026-08-31 |
| S. maltophilia treatment questions and rationales | 90-98 | yes |
| conclusions, acknowledgments, and disclosures | 99-100 | read 2026-08-31; blind 2026-08-31 |
| references | 101-140 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| empiric-therapy-patients | considerations that should inform empiric therapy |
| adults-normal-function | adults, assuming normal renal and hepatic function |
| adults-uuti | uUTI |
| adults-cuti | cUTI |
| adults-other-infections | All other infections |
| adults-crcl-90 | CrCL ≥90 mL/min |
| adults-crcl-120 | CrCL ≥120 mL/min |
| adults-crcl-130 | CrCL ≥130 mL/min |
| adults-obesity-cns-ecmo-high-crcl | obesity, central nervous system infections, and extracorporeal membrane oxygenation or CrCL ≥130 mL/min |
| adults-hypoalbuminemia-esbl-e | patients who are critically ill and/or have hypoalbuminemia |
| enterobacterales | Enterobacterales |
| enterobacterales-uti | Enterobacterales urinary tract infections |
| ecoli | Escherichia coli |
| ecoli-urinary-isolates | Escherichia coli urinary tract isolates only |
| kpneumoniae | Klebsiella pneumoniae |
| pseudomonas-aeruginosa | Pseudomonas aeruginosa |
| pseudomonas-aeruginosa-uti | Pseudomonas aeruginosa urinary tract infections |
| crab | Carbapenem-Resistant Acinetobacter baumannii |
| stenotrophomonas-maltophilia | Stenotrophomonas maltophilia |
| ecoli-kpneumoniae-koxytoca | E. coli, K. pneumoniae, or K. oxytoca isolates |
| moderate-risk-ampc | organisms at moderate risk of significant AmpC production (i.e., E. cloacae complex, K. aerogenes, C. freundii, H. alvei) |
| non-carbapenemase-cre-phenotype | Enterobacterales isolates that do not produce carbapenemases and demonstrate susceptibility to meropenem and imipenem |
| cre-nonblood-nonutinary | CRE infections that do not involve the bloodstream or urinary tract |
| pseudomonas-carbapenem-nonsusceptible | P. aeruginosa isolates that are not susceptible to carbapenems |
| pseudomonas-multiple-newer-beta-lactam-nonsusceptible | P. aeruginosa isolates not susceptible to any of the newer β-lactams |
| invasive-crab | invasive CRAB infections |
| sulbactam-susceptible-crab | sulbactam-susceptible CRAB isolates |
| invasive-stenotrophomonas | invasive S. maltophilia infections |

## Quantities

| key | verbatim |
| --- | --- |
| prior-microbiology-lookback | organisms and associated AST results within the past 12 months |
| prior-antibiotic-exposure-lookback | antibiotic exposure in the preceding 3 months |
| amikacin-dose | Amikacin |
| ampicillin-sulbactam-dose | Ampicillin-sulbactam |
| aztreonam-avibactam-dose | Aztreonam-avibactam |
| cefepime-dose | Cefepime |
| cefepime-enmetazobactam-dose | Cefepime-enmetazobactam |
| cefiderocol-dose | Cefiderocol |
| ceftazidime-avibactam-dose | Ceftazidime-avibactam |
| ceftazidime-avibactam-aztreonam-dose | Ceftazidime-avibactam PLUS aztreonam |
| ceftolozane-tazobactam-dose | Ceftolozane-tazobactam |
| ciprofloxacin-dose | Ciprofloxacin |
| eravacycline-dose | Eravacycline |
| ertapenem-dose | Ertapenem |
| fosfomycin-dose | Fosfomycin |
| gentamicin-dose | Gentamicin |
| gepotidacin-dose | Gepotidacin |
| imipenem-cilastatin-dose | Imipenem-cilastatin |
| imipenem-relebactam-dose | Imipenem-cilastatin-relebactam |
| levofloxacin-dose | Levofloxacin |
| meropenem-dose | Meropenem |
| meropenem-vaborbactam-dose | Meropenem-vaborbactam |
| minocycline-dose | Minocycline |
| nitrofurantoin-dose | Nitrofurantoin |
| pivmecillinam-dose | Pivmecillinam |
| plazomicin-dose | Plazomicin |
| sulbactam-durlobactam-dose | Sulbactam-durlobactam |
| sulopenem-dose | Sulopenem etzadroxil-probenecid |
| tigecycline-dose | Tigecycline |
| tobramycin-dose | Tobramycin |
| tmp-smx-dose | Trimethoprim-sulfamethoxazole |
| amikacin-breakpoint | Amikacin |
| ampicillin-sulbactam-breakpoint | Ampicillin-sulbactam |
| aztreonam-breakpoint | Aztreonam |
| aztreonam-avibactam-breakpoint | Aztreonam-avibactam |
| cefepime-breakpoint | Cefepime |
| cefepime-enmetazobactam-breakpoint | Cefepime-enmetazobactam |
| cefiderocol-breakpoint | Cefiderocol |
| ceftazidime-breakpoint | Ceftazidime |
| ceftazidime-avibactam-breakpoint | Ceftazidime-avibactam |
| ceftolozane-tazobactam-breakpoint | Ceftolozane-tazobactam |
| ciprofloxacin-breakpoint | Ciprofloxacin |
| ertapenem-breakpoint | Ertapenem |
| fosfomycin-iv-breakpoint | Fosfomycin (intravenous) |
| fosfomycin-oral-breakpoint | Fosfomycin tromethamine (oral) |
| gentamicin-breakpoint | Gentamicin |
| gepotidacin-breakpoint | Gepotidacin |
| imipenem-breakpoint | Imipenem |
| imipenem-relebactam-breakpoint | Imipenem-relebactam |
| levofloxacin-breakpoint | Levofloxacin |
| meropenem-breakpoint | Meropenem |
| meropenem-vaborbactam-breakpoint | Meropenem-vaborbactam |
| minocycline-breakpoint | Minocycline |
| nitrofurantoin-breakpoint | Nitrofurantoin |
| piperacillin-tazobactam-breakpoint | Piperacillin-tazobactam |
| pivmecillinam-breakpoint | Pivmecillinam (mecillinam) |
| plazomicin-breakpoint | Plazomicin |
| polymyxin-breakpoint | Colistin or polymyxin B |
| sulbactam-durlobactam-breakpoint | Sulbactam-durlobactam |
| sulopenem-breakpoint | Sulopenem |
| tigecycline-breakpoint | Tigecycline |
| tmp-smx-breakpoint | Trimethoprim-sulfamethoxazole |
| tobramycin-breakpoint | Tobramycin |
| pivmecillinam-equivalence | 185 mg pivmecillinam is equivalent to 200 mg pivmecillinam hydrochloride |
| esbl-surrogate-ceftriaxone-mic | ceftriaxone minimum inhibitory concentrations |
| pivmecillinam-high-dose | higher dosing |
| tmp-smx-uuti-course | TMP-SMX, as a three-day course |
| esbl-hypoalbuminemia-cutoff | hypoalbuminemia (defined as serum albumin <2.5 g/dL) |
| ampc-cefepime-mic | cefepime MICs are in the susceptible or susceptible dose-dependent range |
| cre-carbapenem-phenotype | susceptibility to meropenem and imipenem but not susceptible to ertapenem |
| tigecycline-poor-outcome-mic | tigecycline MICs associated with poor outcomes in CRE infections |
| pseudomonas-prolonged-infusion | prolonged β-lactam infusions |
| pseudomonas-carbapenem-nonsusceptible-mic | imipenem or meropenem MICs |
| pseudomonas-high-dose-cefepime | high-dose, extended-infusion regimen |
| pseudomonas-combination-selection-mics | β-lactam with an MIC closest to its susceptibility breakpoint |
| sulbactam-durlobactam-resistance-mic | resistance to sulbactam-durlobactam |
| ampicillin-sulbactam-bridge-dose | total daily dose of 9 grams of the sulbactam component |
| ampicillin-sulbactam-standard-dose | standard-dose ampicillin-sulbactam |
| ampicillin-sulbactam-high-dose-preference | high-dose ampicillin-sulbactam administered as a prolonged infusion |
| minocycline-crab-mic | minocycline susceptible breakpoint |
| tigecycline-crab-mic | MICs exceed 1 µg/mL |
| polymyxin-crab-mic | polymyxin MICs |
| cefiderocol-stenotrophomonas-resistance-mic | cefiderocol resistance |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prior-microbiology-lookback | empiric-therapy-patients | review organisms and AST results from the past 12 months | "organisms and associated AST results within the past 12 months" | idsa-amr-2026 | p5 | p5/narrative/prior-microbiology-lookback | narrative |
| prior-antibiotic-exposure-lookback | empiric-therapy-patients | review antibiotic exposure in the preceding 3 months | "antibiotic exposure in the preceding 3 months" | idsa-amr-2026 | p5 | p5/narrative/prior-antibiotic-exposure-lookback | narrative |
| amikacin-dose | adults-uuti | 15 mg/kg IV once | "uUTI: 15 mg/kg IV as a single dose" | idsa-amr-2026 | p7 | p7/narrative/amikacin-uuti-dose | narrative |
| amikacin-dose | adults-cuti | 15 mg/kg IV once; subsequent doses and interval by pharmacokinetic evaluation | "cUTI: 15 mg/kg IV once; subsequent doses and dosing interval based on pharmacokinetic evaluation" | idsa-amr-2026 | p7 | p7/narrative/amikacin-cuti-dose | narrative |
| ampicillin-sulbactam-dose | adults-normal-function | target 9 g sulbactam/day as ampicillin-sulbactam 9 g IV every 8 hours infused over 4 hours | "9 grams of ampicillin-sulbactam (6 grams ampicillin, 3 grams sulbactam) IV every 8 hours, infused over 4 hours" | idsa-amr-2026 | p7 | p7/narrative/ampicillin-sulbactam-intermittent-dose | narrative |
| ampicillin-sulbactam-dose | adults-normal-function | target 9 g sulbactam/day as ampicillin-sulbactam 27 g continuous IV infusion over 24 hours | "27 grams of ampicillin-sulbactam (18 grams ampicillin, 9 grams sulbactam) IV as a continuous infusion over 24 hours" | idsa-amr-2026 | p7 | p7/narrative/ampicillin-sulbactam-continuous-dose | narrative |
| aztreonam-avibactam-dose | adults-normal-function | load 2.67 g IV once over 3 hours, then 2 g IV every 6 hours over 3 hours | RENDERED: "2.67 grams of aztreonam-avibactam (2 grams aztreonam, 0.67 grams avibactam) IV once, infused over 3 hours as a loading dose THEN 2 grams of aztreonam-avibactam (1.5 grams aztreonam, 0.5 grams avibactam) IV every 6 hours, infused over 3 hours as maintenance dosing" | idsa-amr-2026 | p7 | p7/narrative/aztreonam-avibactam-dose | narrative |
| cefepime-dose | adults-uuti | 1 g IV every 8 hours over 30 minutes | "uUTI: 1 gram IV every 8 hours, infused over 30 minutes" | idsa-amr-2026 | p7 | p7/narrative/cefepime-uuti-dose | narrative |
| cefepime-dose | adults-other-infections | load 2 g IV over 30 minutes, then 2 g every 8 hours over 3 hours | RENDERED: "All other infections: 2 grams IV, infused over 30 min as a loading dose THEN 2 grams IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p7 | p7/narrative/cefepime-other-dose | narrative |
| cefepime-enmetazobactam-dose | adults-normal-function | 2.5 g IV every 8 hours over 2 hours | "2.5 grams (2 grams cefepime, 0.5 grams enmetazobactam) IV every 8 hours, infused over 2 hours" | idsa-amr-2026 | p7 | p7/narrative/cefepime-enmetazobactam-dose | narrative |
| cefepime-enmetazobactam-dose | adults-crcl-130 | 2.5 g IV every 8 hours over 4 hours | "CrCL ≥130 mL/min: 2.5 grams IV every 8 hours, infused over 4 hours" | idsa-amr-2026 | p7 | p7/narrative/cefepime-enmetazobactam-high-crcl-dose | narrative |
| cefiderocol-dose | adults-normal-function | 2 g IV every 8 hours over 3 hours | "2 grams IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p8 | p8/narrative/cefiderocol-dose | narrative |
| cefiderocol-dose | adults-crcl-120 | 2 g IV every 6 hours over 3 hours | "CrCL ≥120 mL/min: 2 grams IV every 6 hours, infused over 3 hours" | idsa-amr-2026 | p8 | p8/narrative/cefiderocol-high-crcl-dose | narrative |
| ceftazidime-avibactam-dose | adults-normal-function | 2.5 g IV every 8 hours over 3 hours | "2.5 grams (2 grams ceftazidime, 0.5 grams avibactam) IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p8 | p8/narrative/ceftazidime-avibactam-dose | narrative |
| ceftazidime-avibactam-aztreonam-dose | adults-normal-function | ceftazidime-avibactam 2.5 g plus aztreonam 2 g IV every 8 hours, both over 3 hours and simultaneous by Y-site | RENDERED: "Ceftazidime-avibactam: 2.5 grams (2 grams ceftazidime, 0.5 grams avibactam) IV every 8 hours, infused over 3 hours PLUS (administered simultaneously via Y-site administration) Aztreonam: 2 grams IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p8 | p8/narrative/ceftazidime-avibactam-aztreonam-dose | narrative |
| ceftolozane-tazobactam-dose | adults-uuti | 1.5 g IV every 8 hours over 1 hour | "uUTI: 1.5 grams (1 gram ceftolozane, 0.5 grams tazobactam) IV every 8 hours, infused over 1 hour" | idsa-amr-2026 | p8 | p8/narrative/ceftolozane-tazobactam-uuti-dose | narrative |
| ceftolozane-tazobactam-dose | adults-other-infections | 3 g IV every 8 hours over 3 hours | "All other infections: 3 grams (2 grams ceftolozane, 1 gram tazobactam) IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p8 | p8/narrative/ceftolozane-tazobactam-other-dose | narrative |
| ciprofloxacin-dose | adults-uuti | 400 mg IV every 12 hours or 500 mg orally every 12 hours | "uUTI: 400 mg IV every 12 hours OR 500 mg PO every 12 hours" | idsa-amr-2026 | p8 | p8/narrative/ciprofloxacin-uuti-dose | narrative |
| ciprofloxacin-dose | adults-other-infections | 400 mg IV every 8 hours or 750 mg orally every 12 hours | "All other infections: 400 mg IV every 8 hours OR 750 mg PO every 12 hours" | idsa-amr-2026 | p8 | p8/narrative/ciprofloxacin-other-dose | narrative |
| eravacycline-dose | adults-normal-function | 1 mg/kg IV every 12 hours | "1 mg/kg IV every 12 hours" | idsa-amr-2026 | p8 | p8/narrative/eravacycline-dose | narrative |
| ertapenem-dose | adults-normal-function | 1 g IV every 24 hours over 30 minutes | "1 gram IV every 24 hours, infused over 30 minutes" | idsa-amr-2026 | p8 | p8/narrative/ertapenem-dose | narrative |
| fosfomycin-dose | adults-uuti | 3 g orally once | "uUTI: 3 grams PO as a single dose" | idsa-amr-2026 | p8 | p8/narrative/fosfomycin-uuti-dose | narrative |
| fosfomycin-dose | adults-cuti | 6 g IV every 8 hours over 1 hour | "cUTI: 6 grams IV every 8 hours, infused over 1 hour" | idsa-amr-2026 | p8 | p8/narrative/fosfomycin-cuti-dose | narrative |
| gentamicin-dose | adults-uuti | 5 mg/kg IV once | "uUTI: 5 mg/kg per dose IV as a single dose" | idsa-amr-2026 | p8 | p8/narrative/gentamicin-uuti-dose | narrative |
| gentamicin-dose | adults-cuti | 7 mg/kg IV once; subsequent doses and interval by pharmacokinetic evaluation | "cUTI: 7 mg/kg IV once; subsequent doses and dosing interval based on pharmacokinetic evaluation" | idsa-amr-2026 | p8 | p8/narrative/gentamicin-cuti-dose | narrative |
| gepotidacin-dose | adults-uuti | 1.5 g orally every 12 hours | "uUTI: 1.5 grams PO every 12 hours" | idsa-amr-2026 | p8 | p8/narrative/gepotidacin-dose | narrative |
| imipenem-cilastatin-dose | adults-uuti | imipenem 500 mg IV every 6 hours over 30 minutes | "uUTI: 500 mg imipenem IV every 6 hours, infused over 30 minutes" | idsa-amr-2026 | p8 | p8/narrative/imipenem-uuti-dose | narrative |
| imipenem-cilastatin-dose | adults-other-infections | imipenem 500 mg IV every 6 hours over 3 hours | "All other infections: 500 mg imipenem IV every 6 hours, infused over 3 hours (if feasible)" | idsa-amr-2026 | p8 | p8/narrative/imipenem-other-dose-500 | narrative |
| imipenem-cilastatin-dose | adults-other-infections | imipenem 1,000 mg IV every 8 hours over 1 hour | RENDERED: "OR 1,000 mg imipenem IV every 8 hours, infused over 1 hour" | idsa-amr-2026 | p9 | p9/narrative/imipenem-other-dose-1000 | narrative |
| imipenem-cilastatin-dose | adults-crcl-90 | imipenem 1 g IV every 6 hours over 1 hour | "CrCL ≥90 mL/min: 1 gram imipenem IV every 6 hours, infused over 1 hour" | idsa-amr-2026 | p9 | p9/narrative/imipenem-high-crcl-dose | narrative |
| imipenem-relebactam-dose | adults-normal-function | 1.25 g IV every 6 hours over 30 minutes | "1.25 grams (500 mg imipenem, 500 mg cilastatin, 250 mg relebactam) IV every 6 hours, infused over 30 minutes" | idsa-amr-2026 | p9 | p9/narrative/imipenem-relebactam-dose | narrative |
| levofloxacin-dose | adults-normal-function | 750 mg IV or orally every 24 hours | "750 mg IV/PO every 24 hours" | idsa-amr-2026 | p9 | p9/narrative/levofloxacin-dose | narrative |
| meropenem-dose | adults-uuti | 1 g IV every 8 hours over 30 minutes | "uUTI: 1 grams IV every 8 hours, infused over 30 minutes" | idsa-amr-2026 | p9 | p9/narrative/meropenem-uuti-dose | narrative |
| meropenem-dose | adults-other-infections | 1-2 g IV every 8 hours over 3 hours if feasible | "All other infections: 1-2 gram IV every 8 hours, infused over 3 hours (if feasible)" | idsa-amr-2026 | p9 | p9/narrative/meropenem-other-dose | narrative |
| meropenem-dose | adults-obesity-cns-ecmo-high-crcl | prefer 2 g | "2 g preferred for obesity, central nervous system infections, and extracorporeal membrane oxygenation or CrCL ≥130 mL/min" | idsa-amr-2026 | p9 | p9/narrative/meropenem-special-dose | narrative |
| meropenem-vaborbactam-dose | adults-normal-function | 4 g IV every 8 hours over 3 hours | "4 grams (2 grams meropenem, 2 grams vaborbactam) IV every 8 hours, infused over 3 hours" | idsa-amr-2026 | p9 | p9/narrative/meropenem-vaborbactam-dose | narrative |
| minocycline-dose | adults-normal-function | 200 mg IV or orally every 12 hours | "200 mg IV/PO every 12 hours" | idsa-amr-2026 | p9 | p9/narrative/minocycline-dose | narrative |
| nitrofurantoin-dose | adults-uuti | macrocrystal/monohydrate 100 mg orally every 12 hours | "Macrocrystal/monohydrate (Macrobid®): 100 mg PO every 12 hours" | idsa-amr-2026 | p9 | p9/narrative/nitrofurantoin-macrocrystal-dose | narrative |
| nitrofurantoin-dose | adults-uuti | oral suspension 50 mg every 6 hours | "Oral suspension: 50 mg PO every 6 hours" | idsa-amr-2026 | p9 | p9/narrative/nitrofurantoin-suspension-dose | narrative |
| pivmecillinam-dose | adults-uuti | 370 mg orally every 8 hours | "uUTI: 370 mg pivmecillinam PO every 8 hours" | idsa-amr-2026 | p9 | p9/narrative/pivmecillinam-dose | narrative |
| pivmecillinam-equivalence | adults-uuti | 185 mg pivmecillinam = 200 mg pivmecillinam hydrochloride | "185 mg pivmecillinam is equivalent to 200 mg pivmecillinam hydrochloride" | idsa-amr-2026 | p9 | p9/narrative/pivmecillinam-equivalence | narrative |
| plazomicin-dose | adults-uuti | 15 mg/kg IV once | "uUTI: 15 mg/kg IV as a single dose" | idsa-amr-2026 | p9 | p9/narrative/plazomicin-uuti-dose | narrative |
| plazomicin-dose | adults-cuti | 15 mg/kg IV once; subsequent doses and interval by pharmacokinetic evaluation | "cUTI: 15 mg/kg IV once; subsequent doses and dosing interval based on pharmacokinetic evaluation" | idsa-amr-2026 | p9 | p9/narrative/plazomicin-cuti-dose | narrative |
| sulbactam-durlobactam-dose | adults-normal-function | 2 g IV every 6 hours over 3 hours | "2 grams (1 gram sulbactam, 1 gram durlobactam) IV every 6 hours, infused over 3 hours" | idsa-amr-2026 | p10 | p10/narrative/sulbactam-durlobactam-dose | narrative |
| sulbactam-durlobactam-dose | adults-crcl-130 | 2 g IV every 4 hours over 3 hours | "CrCL ≥130 mL/min: 2 grams (1 gram sulbactam, 1 gram durlobactam) IV every 4 hours, infused over 3 hours" | idsa-amr-2026 | p10 | p10/narrative/sulbactam-durlobactam-high-crcl-dose | narrative |
| sulopenem-dose | adults-normal-function | sulopenem etzadroxil 500 mg plus probenecid 500 mg orally every 12 hours | "500 mg sulopenem etzadroxil-500 mg probenecid PO every 12 hours" | idsa-amr-2026 | p10 | p10/narrative/sulopenem-dose | narrative |
| tigecycline-dose | adults-normal-function | load 200 mg IV once, then 100 mg IV every 12 hours | "200 mg IV once as a loading dose THEN 100 mg IV every 12 hours" | idsa-amr-2026 | p10 | p10/narrative/tigecycline-dose | narrative |
| tobramycin-dose | adults-uuti | 5 mg/kg IV once | "uUTI: 5 mg/kg/dose IV as a single dose" | idsa-amr-2026 | p10 | p10/narrative/tobramycin-uuti-dose | narrative |
| tobramycin-dose | adults-cuti | 7 mg/kg IV once; subsequent doses and interval by pharmacokinetic evaluation | "cUTI: 7 mg/kg IV once; subsequent doses and dosing interval based on pharmacokinetic evaluation" | idsa-amr-2026 | p10 | p10/narrative/tobramycin-cuti-dose | narrative |
| tmp-smx-dose | adults-uuti | trimethoprim 160 mg IV or orally every 12 hours | "uUTI: 160 mg (trimethoprim component) IV/PO every 12 hours" | idsa-amr-2026 | p10 | p10/narrative/tmp-smx-uuti-dose | narrative |
| tmp-smx-dose | adults-other-infections | trimethoprim 8-15 mg/kg/day IV or orally divided every 8-12 hours | "All other infections: 8-15 mg/kg/day (trimethoprim component) IV/PO divided every 8 to 12 hours" | idsa-amr-2026 | p10 | p10/narrative/tmp-smx-other-dose | narrative |
| amikacin-breakpoint | enterobacterales | susceptible at MIC <=4 µg/mL | RENDERED: "Amikacin ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/amikacin-enterobacterales-breakpoint | narrative |
| amikacin-breakpoint | pseudomonas-aeruginosa-uti | susceptible at MIC <=16 µg/mL; breakpoint available only for UTI | RENDERED: "Amikacin ; ≤16" (rendered table shows breakpoint ¹⁶ followed by footnote ²) | idsa-amr-2026 | p11 | p11/narrative/amikacin-pseudomonas-uti-breakpoint | narrative |
| ampicillin-sulbactam-breakpoint | crab | susceptible at MIC <=8/4 µg/mL | RENDERED: "Ampicillin-sulbactam ; ≤8/4" | idsa-amr-2026 | p11 | p11/narrative/ampicillin-sulbactam-crab-breakpoint | narrative |
| aztreonam-breakpoint | enterobacterales | susceptible at MIC <=4 µg/mL | RENDERED: "Aztreonam ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/aztreonam-enterobacterales-breakpoint | narrative |
| aztreonam-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=8 µg/mL | RENDERED: "Aztreonam ; ≤8" | idsa-amr-2026 | p11 | p11/narrative/aztreonam-pseudomonas-breakpoint | narrative |
| aztreonam-avibactam-breakpoint | enterobacterales | susceptible at MIC <=4/4 µg/mL | RENDERED: "Aztreonam-avibactam ; ≤4/4" | idsa-amr-2026 | p11 | p11/narrative/aztreonam-avibactam-enterobacterales-breakpoint | narrative |
| aztreonam-avibactam-breakpoint | stenotrophomonas-maltophilia | no CLSI or FDA breakpoint is available | "Neither CLSI nor FDA breakpoints are available" | idsa-amr-2026 | p12 | p12/narrative/aztreonam-avibactam-stenotrophomonas-no-breakpoint | narrative |
| cefepime-breakpoint | enterobacterales | susceptible at MIC <=2 µg/mL | RENDERED: "Cefepime ; ≤2⁴" | idsa-amr-2026 | p11 | p11/narrative/cefepime-enterobacterales-breakpoint | narrative |
| cefepime-breakpoint | enterobacterales | MIC 4-8 µg/mL is susceptible dose-dependent | "Cefepime MICs of 4-8 µg/mL are susceptible dose-dependent" | idsa-amr-2026 | p12 | p12/narrative/cefepime-enterobacterales-sdd-breakpoint | narrative |
| cefepime-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=8 µg/mL | RENDERED: "Cefepime ; ≤8" | idsa-amr-2026 | p11 | p11/narrative/cefepime-pseudomonas-breakpoint | narrative |
| cefepime-enmetazobactam-breakpoint | enterobacterales | FDA susceptible breakpoint <=8/8 µg/mL; no CLSI breakpoint | RENDERED: "Cefepime-enmetazobactam ; ≤8/8⁵" | idsa-amr-2026 | p11 | p11/narrative/cefepime-enmetazobactam-enterobacterales-breakpoint | narrative |
| cefiderocol-breakpoint | enterobacterales | susceptible at MIC <=4 µg/mL | RENDERED: "Cefiderocol ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/cefiderocol-enterobacterales-breakpoint | narrative |
| cefiderocol-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=4 µg/mL | RENDERED: "Cefiderocol ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/cefiderocol-pseudomonas-breakpoint | narrative |
| cefiderocol-breakpoint | crab | susceptible at MIC <=4 µg/mL | RENDERED: "Cefiderocol ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/cefiderocol-crab-breakpoint | narrative |
| cefiderocol-breakpoint | stenotrophomonas-maltophilia | susceptible at MIC <=1 µg/mL | RENDERED: "Cefiderocol ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/cefiderocol-stenotrophomonas-breakpoint | narrative |
| ceftazidime-breakpoint | enterobacterales | susceptible at MIC <=4 µg/mL | RENDERED: "Ceftazidime ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/ceftazidime-enterobacterales-breakpoint | narrative |
| ceftazidime-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=8 µg/mL | RENDERED: "Ceftazidime ; ≤8" | idsa-amr-2026 | p11 | p11/narrative/ceftazidime-pseudomonas-breakpoint | narrative |
| ceftazidime-avibactam-breakpoint | enterobacterales | susceptible at MIC <=8/4 µg/mL | RENDERED: "Ceftazidime-avibactam ; ≤8/4" | idsa-amr-2026 | p11 | p11/narrative/ceftazidime-avibactam-enterobacterales-breakpoint | narrative |
| ceftazidime-avibactam-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=8/4 µg/mL | RENDERED: "Ceftazidime-avibactam ; ≤8/4" | idsa-amr-2026 | p11 | p11/narrative/ceftazidime-avibactam-pseudomonas-breakpoint | narrative |
| ceftolozane-tazobactam-breakpoint | enterobacterales | susceptible at MIC <=2/4 µg/mL | RENDERED: "Ceftolozane-tazobactam ; ≤2/4" | idsa-amr-2026 | p11 | p11/narrative/ceftolozane-tazobactam-enterobacterales-breakpoint | narrative |
| ceftolozane-tazobactam-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=4/4 µg/mL | RENDERED: "Ceftolozane-tazobactam ; ≤4/4" | idsa-amr-2026 | p11 | p11/narrative/ceftolozane-tazobactam-pseudomonas-breakpoint | narrative |
| ciprofloxacin-breakpoint | enterobacterales | susceptible at MIC <=0.25 µg/mL | RENDERED: "Ciprofloxacin ; ≤0.25" | idsa-amr-2026 | p11 | p11/narrative/ciprofloxacin-enterobacterales-breakpoint | narrative |
| ciprofloxacin-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=0.5 µg/mL | RENDERED: "Ciprofloxacin ; ≤0.5" | idsa-amr-2026 | p11 | p11/narrative/ciprofloxacin-pseudomonas-breakpoint | narrative |
| ertapenem-breakpoint | enterobacterales | susceptible at MIC <=0.5 µg/mL | RENDERED: "Ertapenem ; ≤0.5" | idsa-amr-2026 | p11 | p11/narrative/ertapenem-enterobacterales-breakpoint | narrative |
| fosfomycin-iv-breakpoint | ecoli | FDA susceptible breakpoint <=8 µg/mL; no CLSI breakpoint | "The Escherichia coli breakpoint is ≤8 µg/mL" | idsa-amr-2026 | p12 | p12/narrative/fosfomycin-iv-ecoli-breakpoint | narrative |
| fosfomycin-iv-breakpoint | kpneumoniae | FDA susceptible breakpoint <=32 µg/mL; no CLSI breakpoint | "the Klebsiella pneumoniae breakpoint is ≤32 µg/mL" | idsa-amr-2026 | p12 | p12/narrative/fosfomycin-iv-kpneumoniae-breakpoint | narrative |
| fosfomycin-oral-breakpoint | ecoli-urinary-isolates | susceptible at MIC <=64 µg/mL; applies only to E. coli urinary isolates | RENDERED: "Fosfomycin tromethamine (oral) ; ≤64⁸" | idsa-amr-2026 | p11 | p11/narrative/fosfomycin-oral-ecoli-uti-breakpoint | narrative |
| gentamicin-breakpoint | enterobacterales | susceptible at MIC <=2 µg/mL | RENDERED: "Gentamicin ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/gentamicin-enterobacterales-breakpoint | narrative |
| gepotidacin-breakpoint | enterobacterales-uti | FDA susceptible breakpoint <=16 µg/mL; no CLSI breakpoint and available only for UTI | RENDERED: "Gepotidacin ; ≤16²˒⁵" | idsa-amr-2026 | p11 | p11/narrative/gepotidacin-enterobacterales-uti-breakpoint | narrative |
| imipenem-breakpoint | enterobacterales | susceptible at MIC <=1 µg/mL | RENDERED: "Imipenem ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/imipenem-enterobacterales-breakpoint | narrative |
| imipenem-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=2 µg/mL | RENDERED: "Imipenem ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/imipenem-pseudomonas-breakpoint | narrative |
| imipenem-relebactam-breakpoint | enterobacterales | susceptible at MIC <=1/4 µg/mL | RENDERED: "Imipenem-relebactam ; ≤1/4" | idsa-amr-2026 | p11 | p11/narrative/imipenem-relebactam-enterobacterales-breakpoint | narrative |
| imipenem-relebactam-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=2/4 µg/mL | RENDERED: "Imipenem-relebactam ; ≤2/4" | idsa-amr-2026 | p11 | p11/narrative/imipenem-relebactam-pseudomonas-breakpoint | narrative |
| levofloxacin-breakpoint | enterobacterales | susceptible at MIC <=0.5 µg/mL | RENDERED: "Levofloxacin ; ≤0.5" | idsa-amr-2026 | p11 | p11/narrative/levofloxacin-enterobacterales-breakpoint | narrative |
| levofloxacin-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=1 µg/mL | RENDERED: "Levofloxacin ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/levofloxacin-pseudomonas-breakpoint | narrative |
| levofloxacin-breakpoint | stenotrophomonas-maltophilia | susceptible at MIC <=2 µg/mL | RENDERED: "Levofloxacin ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/levofloxacin-stenotrophomonas-breakpoint | narrative |
| meropenem-breakpoint | enterobacterales | susceptible at MIC <=1 µg/mL | RENDERED: "Meropenem ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/meropenem-enterobacterales-breakpoint | narrative |
| meropenem-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=2 µg/mL | RENDERED: "Meropenem ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/meropenem-pseudomonas-breakpoint | narrative |
| meropenem-vaborbactam-breakpoint | enterobacterales | susceptible at MIC <=4/8 µg/mL | RENDERED: "Meropenem-vaborbactam ; ≤4/8" | idsa-amr-2026 | p11 | p11/narrative/meropenem-vaborbactam-enterobacterales-breakpoint | narrative |
| minocycline-breakpoint | enterobacterales | susceptible at MIC <=4 µg/mL | RENDERED: "Minocycline ; ≤4" | idsa-amr-2026 | p11 | p11/narrative/minocycline-enterobacterales-breakpoint | narrative |
| minocycline-breakpoint | crab | susceptible at MIC <=1 µg/mL | RENDERED: "Minocycline ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/minocycline-crab-breakpoint | narrative |
| minocycline-breakpoint | stenotrophomonas-maltophilia | susceptible at MIC <=1 µg/mL | RENDERED: "Minocycline ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/minocycline-stenotrophomonas-breakpoint | narrative |
| nitrofurantoin-breakpoint | enterobacterales-uti | susceptible at MIC <=32 µg/mL; breakpoint available only for UTI | RENDERED: "Nitrofurantoin ; ≤32²" | idsa-amr-2026 | p11 | p11/narrative/nitrofurantoin-enterobacterales-uti-breakpoint | narrative |
| piperacillin-tazobactam-breakpoint | enterobacterales | susceptible at MIC <=8/4 µg/mL | RENDERED: "Piperacillin-tazobactam ; ≤8/4⁹" | idsa-amr-2026 | p11 | p11/narrative/piperacillin-tazobactam-enterobacterales-breakpoint | narrative |
| piperacillin-tazobactam-breakpoint | enterobacterales | MIC 16/4 µg/mL is susceptible dose-dependent | "Piperacillin-tazobactam MICs of 16/4 µg/mL are susceptible dose-dependent" | idsa-amr-2026 | p12 | p12/narrative/piperacillin-tazobactam-enterobacterales-sdd-breakpoint | narrative |
| piperacillin-tazobactam-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=16/4 µg/mL | RENDERED: "Piperacillin-tazobactam ; ≤16/4" | idsa-amr-2026 | p11 | p11/narrative/piperacillin-tazobactam-pseudomonas-breakpoint | narrative |
| pivmecillinam-breakpoint | enterobacterales-uti | susceptible at MIC <=8 µg/mL; breakpoint available only for UTI | RENDERED: "Pivmecillinam (mecillinam) ; ≤8²" | idsa-amr-2026 | p11 | p11/narrative/pivmecillinam-enterobacterales-uti-breakpoint | narrative |
| plazomicin-breakpoint | enterobacterales | susceptible at MIC <=2 µg/mL | RENDERED: "Plazomicin ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/plazomicin-enterobacterales-breakpoint | narrative |
| polymyxin-breakpoint | enterobacterales | no susceptible category; MIC <=2 µg/mL is intermediate | "No susceptible category for colistin or polymyxin B; MICs ≤2 µg/mL are categorized as intermediate" | idsa-amr-2026 | p12 | p12/narrative/polymyxin-enterobacterales-intermediate-breakpoint | narrative |
| polymyxin-breakpoint | pseudomonas-aeruginosa | no susceptible category; MIC <=2 µg/mL is intermediate | "No susceptible category for colistin or polymyxin B; MICs ≤2 µg/mL are categorized as intermediate" | idsa-amr-2026 | p12 | p12/narrative/polymyxin-pseudomonas-intermediate-breakpoint | narrative |
| polymyxin-breakpoint | crab | no susceptible category; MIC <=2 µg/mL is intermediate | "No susceptible category for colistin or polymyxin B; MICs ≤2 µg/mL are categorized as intermediate" | idsa-amr-2026 | p12 | p12/narrative/polymyxin-crab-intermediate-breakpoint | narrative |
| sulbactam-durlobactam-breakpoint | crab | susceptible at MIC <=4/4 µg/mL | RENDERED: "Sulbactam-durlobactam ; ≤4/4" | idsa-amr-2026 | p11 | p11/narrative/sulbactam-durlobactam-crab-breakpoint | narrative |
| sulopenem-breakpoint | enterobacterales | FDA susceptible breakpoint <=0.25 µg/mL; no CLSI breakpoint | RENDERED: "Sulopenem ; ≤0.25⁵" | idsa-amr-2026 | p11 | p11/narrative/sulopenem-enterobacterales-breakpoint | narrative |
| tigecycline-breakpoint | enterobacterales | FDA susceptible breakpoint <=2 µg/mL; no CLSI breakpoint | RENDERED: "Tigecycline ; ≤2⁵" | idsa-amr-2026 | p11 | p11/narrative/tigecycline-enterobacterales-breakpoint | narrative |
| tmp-smx-breakpoint | enterobacterales | susceptible at MIC <=2/38 µg/mL | RENDERED: "Trimethoprim-sulfamethoxazole ; ≤2/38" | idsa-amr-2026 | p11 | p11/narrative/tmp-smx-enterobacterales-breakpoint | narrative |
| tmp-smx-breakpoint | stenotrophomonas-maltophilia | susceptible at MIC <=2/38 µg/mL | RENDERED: "Trimethoprim-sulfamethoxazole ; ≤2/38" | idsa-amr-2026 | p11 | p11/narrative/tmp-smx-stenotrophomonas-breakpoint | narrative |
| tobramycin-breakpoint | enterobacterales | susceptible at MIC <=2 µg/mL | RENDERED: "Tobramycin ; ≤2" | idsa-amr-2026 | p11 | p11/narrative/tobramycin-enterobacterales-breakpoint | narrative |
| tobramycin-breakpoint | pseudomonas-aeruginosa | susceptible at MIC <=1 µg/mL | RENDERED: "Tobramycin ; ≤1" | idsa-amr-2026 | p11 | p11/narrative/tobramycin-pseudomonas-breakpoint | narrative |
| esbl-surrogate-ceftriaxone-mic | ecoli-kpneumoniae-koxytoca | ceftriaxone MIC >=4 µg/mL is a commonly acknowledged surrogate for ESBL production | "ceftriaxone minimum inhibitory concentrations [MICs] ≥4 µg/mL" | idsa-amr-2026 | p12 | p12/narrative/esbl-surrogate-ceftriaxone-mic | narrative |
| pivmecillinam-high-dose | adults-uuti | 400 mg three times daily | "higher dosing (400 mg three times daily)" | idsa-amr-2026 | p15 | p15/narrative/pivmecillinam-high-dose | narrative |
| tmp-smx-uuti-course | adults-uuti | three-day course | RENDERED: "TMP-SMX, as a three-day course, is effective for ESBL-E uUTI when the infecting isolate is susceptible" | idsa-amr-2026 | p15 | p15/narrative/tmp-smx-uuti-course | narrative |
| esbl-hypoalbuminemia-cutoff | adults-hypoalbuminemia-esbl-e | serum albumin <2.5 g/dL: prefer imipenem or meropenem rather than ertapenem as initial therapy | RENDERED: "For patients who are critically ill and/or have hypoalbuminemia, imipenem or meropenem are preferred over ertapenem"; "hypoalbuminemia (defined as serum albumin <2.5 g/dL)" | idsa-amr-2026 | p21 | p21/narrative/esbl-hypoalbuminemia-cutoff | narrative |
| ampc-cefepime-mic | moderate-risk-ampc | cefepime MIC <=8 µg/mL: cefepime is preferred if no ESBL gene is identified | RENDERED: "the panel suggests cefepime as a preferred treatment option for AmpC-E infections when the cefepime MIC is ≤8 µg/mL, provided an ESBL gene has not been identified" | idsa-amr-2026 | p37 | p37/narrative/ampc-cefepime-mic | narrative |
| cre-carbapenem-phenotype | non-carbapenemase-cre-phenotype | meropenem and imipenem MIC <=1 µg/mL plus ertapenem MIC >=1 µg/mL: use extended-infusion meropenem or imipenem | "susceptibility to meropenem and imipenem (MIC ≤ 1 µg/mL) but are not susceptible to ertapenem (MIC ≥ 1 µg/mL)" | idsa-amr-2026 | p48 | p48/narrative/cre-carbapenem-phenotype | narrative |
| tigecycline-poor-outcome-mic | cre-nonblood-nonutinary | MIC >=0.5 µg/mL is associated with poor outcomes despite FDA susceptibility <=2 µg/mL | RENDERED: "tigecycline MICs ≥0.5 µg/mL are associated with poor outcomes in CRE infections, despite remaining within the FDA susceptible range (≤2 µg/mL)" | idsa-amr-2026 | p59 | p59/narrative/tigecycline-poor-outcome-mic | narrative |
| pseudomonas-prolonged-infusion | pseudomonas-carbapenem-nonsusceptible | use 3-4-hour prolonged infusion rather than 30-minute standard infusion when needed to maximize exposure | "prolonged β-lactam infusions (e.g., 3-4 hours) compared with standard infusions (e.g., 30 minutes)" | idsa-amr-2026 | p64 | p64/narrative/pseudomonas-prolonged-infusion | narrative |
| pseudomonas-carbapenem-nonsusceptible-mic | pseudomonas-carbapenem-nonsusceptible | imipenem or meropenem MIC >=4 µg/mL | "imipenem or meropenem MICs ≥4 µg/mL" | idsa-amr-2026 | p64 | p64/narrative/pseudomonas-carbapenem-nonsusceptible-mic | narrative |
| pseudomonas-high-dose-cefepime | pseudomonas-carbapenem-nonsusceptible | cefepime 2 g IV every 8 hours infused over >=3 hours is the example high-dose extended-infusion regimen | "cefepime 2 g IV every 8 hours infused over ≥3 hours" | idsa-amr-2026 | p64 | p64/narrative/pseudomonas-high-dose-cefepime | narrative |
| pseudomonas-combination-selection-mics | pseudomonas-multiple-newer-beta-lactam-nonsusceptible | when ceftazidime-avibactam and ceftolozane-tazobactam MICs are >128/4 and imipenem-relebactam MIC is 4/4 µg/mL, favor imipenem-relebactam plus tobramycin | RENDERED: "if ceftazidime-avibactam and ceftolozane-tazobactam MICs are >128/4 µg/mL and the imipenem-relebactam MIC is 4/4 µg/mL (intermediate), imipenem-relebactam in combination with tobramycin is favored" | idsa-amr-2026 | p74 | p74/narrative/pseudomonas-combination-selection-mics | narrative |
| sulbactam-durlobactam-resistance-mic | invasive-crab | MIC >=16/4 µg/mL: prefer non-sulbactam-based combinations | "If resistance to sulbactam-durlobactam (MIC ≥16/4 µg/mL)" | idsa-amr-2026 | p79 | p79/narrative/sulbactam-durlobactam-resistance-mic | narrative |
| ampicillin-sulbactam-bridge-dose | invasive-crab | sulbactam 9 g/day in combination with at least one additional agent only as a bridge until sulbactam-durlobactam plus a carbapenem is available | "total daily dose of 9 grams of the sulbactam component" | idsa-amr-2026 | p80 | p80/narrative/ampicillin-sulbactam-bridge-dose | narrative |
| ampicillin-sulbactam-standard-dose | sulbactam-susceptible-crab | 3 g IV every 6 hours over 30 minutes may be sufficient | "standard-dose ampicillin-sulbactam (3 g IV every 6 hours infused over 30 minutes) may be sufficient" | idsa-amr-2026 | p81 | p81/narrative/ampicillin-sulbactam-standard-dose | narrative |
| ampicillin-sulbactam-high-dose-preference | sulbactam-susceptible-crab | favor high-dose ampicillin-sulbactam administered as a prolonged infusion even when reported susceptible | "the panel favors the use of high-dose ampicillin-sulbactam administered as a prolonged infusion even for isolates reported as sulbactam susceptible" | idsa-amr-2026 | p82 | p82/narrative/ampicillin-sulbactam-high-dose-preference | narrative |
| minocycline-crab-mic | invasive-crab | minocycline 200 mg every 12 hours attains stasis targets up to MIC <=1 µg/mL | RENDERED: "Minocycline dosed at 200 mg every 12 hours provides a high probability of attaining targets associated with bacterial stasis for isolates with MICs up to the susceptible breakpoint of ≤1 µg/mL" | idsa-amr-2026 | p84 | p84/narrative/minocycline-crab-mic | narrative |
| tigecycline-crab-mic | invasive-crab | efficacy is reduced when MIC >1 µg/mL | "reduced efficacy when MICs exceed 1 µg/mL" | idsa-amr-2026 | p85 | p85/narrative/tigecycline-crab-mic | narrative |
| polymyxin-crab-mic | invasive-crab | MIC <=2 µg/mL is intermediate; benefit diminishes when MIC >2 µg/mL | "The benefit of polymyxins is diminished when polymyxin MICs are >2 µg/mL" | idsa-amr-2026 | p86 | p86/narrative/polymyxin-crab-mic | narrative |
| cefiderocol-stenotrophomonas-resistance-mic | invasive-stenotrophomonas | MIC >=2 µg/mL is cefiderocol resistance | "cefiderocol resistance (i.e., MICs ≥2 µg/mL)" | idsa-amr-2026 | p90 | p90/narrative/cefiderocol-stenotrophomonas-resistance-mic | narrative |

## Conflicts

CONFLICT: ampicillin-sulbactam-dose — for `adults-normal-function`, the two complete row values are `target 9 g sulbactam/day as ampicillin-sulbactam 9 g IV every 8 hours infused over 4 hours` and `target 9 g sulbactam/day as ampicillin-sulbactam 27 g continuous IV infusion over 24 hours`.

CONFLICT: imipenem-cilastatin-dose — for `adults-other-infections`, the two complete row values are `imipenem 500 mg IV every 6 hours over 3 hours` and `imipenem 1,000 mg IV every 8 hours over 1 hour`.

CONFLICT: nitrofurantoin-dose — for `adults-uuti`, the two complete row values are `macrocrystal/monohydrate 100 mg orally every 12 hours` and `oral suspension 50 mg every 6 hours`.

CONFLICT: cefepime-breakpoint — for `enterobacterales`, the two complete row values are `susceptible at MIC <=2 µg/mL` and `MIC 4-8 µg/mL is susceptible dose-dependent`.

CONFLICT: piperacillin-tazobactam-breakpoint — for `enterobacterales`, the two complete row values are `susceptible at MIC <=8/4 µg/mL` and `MIC 16/4 µg/mL is susceptible dose-dependent`.

## Coverage

The current PDF-bound recommendation sweep at `IDSA/amr-guidance-update.json`
reported `nothing-found` with 0 recommendations. The complete page, table, and
figure sweep recorded under `## Scope` is the source accounting; the null result is
recorded here without treating it as evidence that the rest of the guideline states
no numeric patient-action point.
