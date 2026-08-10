# Shorthand glossary

Expansions [clinical-note](SKILL.md) applies at step 2. Anything absent here is an **unknown token** — carried forward verbatim and surfaced in the tier block.

> **Keep this file current.** Every unknown token that comes back from a note belongs here. The skill gets more deterministic with each line you add, and the shift-level roll-up in [batch-shift](../batch-shift/SKILL.md) exists to feed it.

## Personal shorthand

Observed in real notes. Expansions confirmed against the finished versions.

| Shorthand | Expansion |
| --- | --- |
| `hx` | history |
| `cc` | chief complaint |
| `dx` | diagnosis |
| `rtc` | return to clinic |
| `rec 4 days` | recheck in four days |
| `us` | ultrasound |
| `t 97.3` | temperature 97.3 °F |
| `spo2 96` | oxygen saturation 96% |
| `vaccs utd` | vaccinations up to date |
| `OP` | oropharynx |
| `L` / `R` | left / right |
| `36in 33lb` | height 36 inches, weight 33 pounds |
| `2/2j` | peripheral pulses 2+ and equal — a typo, confirmed |
| `wnl` | within normal limits |
| `emb` | endometrial biopsy |
| `aub` | abnormal uterine bleeding |
| `BTL` | bilateral tubal ligation |
| `cocs` | combined oral contraceptives |
| `TM` | tympanic membrane |
| `RA` | room air |
| `mamo` | mammogram |
| `rtn` | return |
| `fe` | iron |
| `rx` | prescribe |
| `MDI` | metered dose inhaler |
| `TIA` | transient ischemic attack |
| `#` (in `7# 10 oz`) | pounds — birth weight |
| `lmp` | last menstrual period |
| `pcos` | polycystic ovary syndrome |
| `g2p2a0` | gravida 2, para 2, abortus 0 |
| `pna` | pneumonia |
| `adhd` | attention-deficit hyperactivity disorder |
| `hfa` | hydrofluoroalkane — a metered-dose inhaler propellant, so `albuterol hfa` is the inhaler |
| `duoneb` | ipratropium-albuterol nebuliser solution |
| `rosvig`, `rovsig` | **Rovsing's sign** — confirmed by the clinician 2026-08-10 |

**`rosvig` is a peritoneal sign, so it is never a throwaway.** A positive Rovsing's recorded in a note whose abdomen is otherwise normal — as in day-a case 5 — is a contradiction the note has to resolve out loud, not a token to expand and move past.

### Conditions and history

Drawn from a sweep of the clinician's full day-file catalog — 49 files, 340 pages, 32 of them carrying a text layer.

| Shorthand | Expansion |
| --- | --- |
| `dm` | diabetes mellitus |
| `htn` | hypertension |
| `cad` | coronary artery disease |
| `copd` | chronic obstructive pulmonary disease |
| `gerd` | gastro-oesophageal reflux disease |
| `afib` | atrial fibrillation |
| `dvt` | deep vein thrombosis |
| `sud` | substance use disorder |
| `bv` | bacterial vaginosis |
| `hep b`, `hep c` | hepatitis B, hepatitis C |
| `mrsa` | methicillin-resistant *Staphylococcus aureus* |
| `cap` | community-acquired pneumonia |
| `pna` | pneumonia |
| `chole` | cholecystectomy — a past surgery, in a PMH or PSH list |
| `appy` | appendectomy — also a past surgery, **not** appendicitis |
| `t&a` | tonsillectomy and adenoidectomy |
| `d&c` | dilation and curettage |
| `full hyster` | total hysterectomy |
| `fx` | fracture |
| `polyp` | polyp |

### Drugs, doses and orders

| Shorthand | Expansion |
| --- | --- |
| `otc` | over the counter |
| `asa` | aspirin — expands the same way in a medication list and an allergy list |
| `pcn` | penicillin |
| `hctz` | hydrochlorothiazide |
| `feso4` | ferrous sulphate |
| `b12` | vitamin B12 |
| `vits`, `prenatal vits` | vitamins, prenatal vitamins |
| `gtt` | drops — `ciprodex 4 gtt BID` is four drops twice daily |
| `odt` | orally disintegrating tablet |
| `tx` | treatment, or treated — `nebulizer tx`, `was recently tx with amoxicillin` |
| `qhs` | at bedtime |
| `q4-6h`, `q6-8h` | every 4 to 6 hours, every 6 to 8 hours |
| `mcg` | micrograms |
| `mg/5ml` | milligrams per 5 millilitres — a suspension concentration |

### Tests and findings

| Shorthand | Expansion |
| --- | --- |
| `a1c` | haemoglobin A1c |
| `micro urine` | microscopic urinalysis, ordered alongside `ua` |
| `c/s` | culture and sensitivity — `urine c/s`, `pharyngeal c/s` |
| `rsv` | respiratory syncytial virus |
| `rpr` | rapid plasma reagin — syphilis screening |
| `abg` | arterial blood gas |
| `trop` | troponin |
| `egd` | oesophagogastroduodenoscopy |
| `dexa` | dual-energy x-ray absorptiometry — bone density |
| `pap` | Papanicolaou smear |
| `tms` | tympanic membranes — the plural of `TM` |
| `heent` | head, eyes, ears, nose and throat |
| `sob` | shortness of breath |
| `llq`, `rll`, `rle`, `ble` | left lower quadrant · right lower lobe · right lower extremity · bilateral lower extremities |
| `preop` | preoperative |

### Obstetric

The catalog carries obstetric encounters, and they feed a separate hours bucket — see [medatrax-fields.md](../../reference/medatrax-fields.md).

| Shorthand | Expansion |
| --- | --- |
| `fht` | **fetal heart tones**, reported as a rate — `FHT 145 bpm` |
| `fundus measures 39.5 cm` | fundal height in centimetres |
| `g5p4a0`, `g3p1a1` | gravida, para, abortus — the same pattern as `g2p2a0` |
| `iud` | intrauterine device |
| `depo` | depot medroxyprogesterone injection |

## Ambiguous — resolve from context, never by default

These carry more than one standard expansion and the wrong one invents a diagnosis. Treat them the way `d/c` is treated: read the context, and where the context does not settle it, **flag rather than guess.**

**`CVA` — costovertebral angle, or cerebrovascular accident.** Both appear in this catalog, sometimes in the same note:

- `Left CVA tenderness` — costovertebral angle. A physical exam finding.
- `family hx: Mother - CAD, DM, CVA` — cerebrovascular accident. A stroke.

The tell is the neighbouring word. `CVA tenderness` is anatomical; `CVA` in a history or problem list is a stroke. Expanding a family history's `CVA` as costovertebral angle loses a stroke from the family history; expanding an exam finding as a stroke invents one. **Neither is recoverable downstream, because both read perfectly well.**

**`PPD` — packs per day, or purified protein derivative.** Every instance in this catalog is packs per day: `3 ppd smoker`, `smokes 0.5 ppd x 1 year`. The TB skin test meaning has not appeared here, so read it as packs per day and flag anything that reads otherwise.

**`c/s` — culture and sensitivity, or caesarean section.** Every instance here is culture and sensitivity, always attached to a specimen: `urine c/s`, `pharyngeal c/s`. In an obstetric note it would mean the other thing, and this catalog contains obstetric notes.

**`hs` — at bedtime, or a typo for "has".** `cetrazine 10 mg PO HS` is bedtime dosing. `states hs fever` is a mistyped "has". Position decides: attached to a dose it is bedtime, in a sentence it is not.

**`appy` — appendectomy, not appendicitis.** It appears only in surgical histories here. A note that turns it into an active diagnosis has invented an acute abdomen out of a scar.

**Local facility abbreviations** — the catalog refers to hospitals and imaging centres by initials for referral destinations. They are per-clinician and are collected by [`/setup-clinical-skills`](../setup-clinical-skills/SKILL.md), not hardcoded here.

### Typos seen in the wild

Corrected silently as transcription noise, per the skill's Given rules.

`triglycerieds` → triglycerides · `oorphectomy` → oophorectomy · `endometroises` → endometriosis · `labido` → libido · `dryiness` → dryness · `sicnce` → since · `draininge` → drainage · `eart tympansotomy` → ear tympanostomy · `prednisolono` → prednisolone · `claritian` → Claritin · `zithromax` → Zithromax (azithromycin) · `brom fed` → Bromfed

**Recurring across the catalog**, with counts from the 32 text-layer files. These are habits rather than slips, so they will be in the next day file too:

`buldging` → bulging (50) · `exm` → exam (14) · `cetrazine` → cetirizine (13) · `apces` → apices (8) · `vist` → visit (6) · `clinc` → clinic (6) · `brith` → birth (5) · `obsucred` → obscured (5) · `insurence` → insurance (5) · `erythma` → erythema (4) · `diminised` → diminished (3) · `migranes` → migraines (3) · `hypothryroid` → hypothyroid (3) · `difuse` → diffuse (2) · `urinatin` → urination (2) · `proceedure` → procedure (2)

Seen once each, listed because the pattern is the same: `famliy`, `diminisnished`, `occiptial`, `tonsuilar`, `pharngeal`, `comited`, `neuorpathy`, `palpatiations`, `anitomical`, `poping`, `rinoplasy`, `anerysim`, `syphallis`, `nostiril`, `opthalmic`, `strated`, `abck` → back, `bowl sounds` → bowel sounds, `lymph note` → lymph node, `netti pot` → neti pot.

**`cetrazine` is the one that matters.** It is a drug name, it appears thirteen times, and cetirizine is what it means. A word typo produces an odd-looking note; a drug typo produces a prescription. Correct it, and treat any unrecognised drug spelling as a candidate for the same treatment rather than passing it through as written — the rule against "correcting" a number does not extend to a misspelled drug.

`apces` deserves a note too: it appears only inside one stock phrase — *"lungs are clear in the apces, diminished in the bases"* — which is this clinician's habitual way of recording that finding.

## Dose conversions — derived, show the arithmetic

| Shorthand | Conversion |
| --- | --- |
| `1 t`, `1 tsp` | 5 mL |
| `3/4 t` | 3.75 mL |
| `1/2 t` | 2.5 mL |
| `1 T`, `1 tbsp` | 15 mL |
| `200/5ml, 3/4 t` | azithromycin 200 mg/5 mL, 3.75 mL = 150 mg per dose |

## Symbols

| Shorthand | Expansion |
| --- | --- |
| `c/o` | complains of |
| `s/p` | status post |
| `w/`, `w/o` | with, without |
| `2/2` | secondary to |
| `r/o` | rule out |
| `+` / `-` | positive for / negative for |
| `↑` / `↓` | increased / decreased |
| `→` | leading to, progressing to |
| `x` | for (duration) — `x3d` = for three days |
| `q`, `qd`, `bid`, `tid`, `qid` | every, daily, twice daily, three times daily, four times daily |
| `prn` | as needed |
| `NKDA` | no known drug allergies |

## History and exam

| Shorthand | Expansion |
| --- | --- |
| `HPI` | history of present illness |
| `PMH` / `PSH` | past medical history / past surgical history |
| `FH` / `SH` | family history / social history |
| `ROS` | review of systems |
| `NAD` | no acute distress |
| `AAOx3` / `AAOx4` | alert and oriented to person, place, time (and situation) |
| `RRR` | regular rate and rhythm |
| `CTAB` | clear to auscultation bilaterally |
| `S1, S2` | first and second heart sounds normal |
| `S/NT/ND` | soft, non-tender, non-distended |
| `EOMI` | extraocular movements intact |
| `PERRL` | pupils equal, round, reactive to light |
| `CN II-XII` | cranial nerves two through twelve |
| `MAEW` | moves all extremities well |
| `LOC` | loss of consciousness |
| `LAD` | lymphadenopathy |

## Vitals and diagnostics

| Shorthand | Expansion |
| --- | --- |
| `VSS` | vital signs stable |
| `BP` / `HR` / `RR` / `T` | blood pressure / heart rate / respiratory rate / temperature |
| `CBC` / `BMP` / `CMP` | complete blood count / basic metabolic panel / comprehensive metabolic panel |
| `LFTs` | liver function tests |
| `UA` | urinalysis |
| `CXR` / `KUB` | chest x-ray / kidneys-ureters-bladder x-ray |
| `CTA` / `CTH` | CT angiogram / CT head |
| `ECG`, `EKG` | electrocardiogram |
| `POC` | point of care |
| `hCG` | human chorionic gonadotropin |
| `FSH` | follicle-stimulating hormone |
| `TSH` | thyroid-stimulating hormone |

## Treatment and disposition

| Shorthand | Expansion |
| --- | --- |
| `IV` / `IM` / `PO` / `SL` / `SQ` | intravenous / intramuscular / by mouth / sublingual / subcutaneous |
| `NS` / `LR` | normal saline / lactated Ringer's |
| `abx` | antibiotics |
| `f/u` | follow up |
| `d/c` | **ambiguous** — discharge or discontinue. Flag as unknown unless context is unmistakable |
| `DC'd home` | discharged home |
| `AMA` | against medical advice |
| `PCP` | primary care provider |
| `ED` / `ER` | emergency department |
| `OBS` | observation |
| `RTED` | return to emergency department |
