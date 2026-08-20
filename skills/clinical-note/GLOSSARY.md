# Shorthand glossary

Expansions [clinical-note](SKILL.md) applies at step 2. Anything absent here is an **unknown token** — carried forward verbatim and surfaced in the tier block.

> **Keep this file current.** Every unknown token that comes back from a note belongs here. The skill gets more deterministic with each line you add, and the shift-level roll-up in [batch-shift](../batch-shift/SKILL.md) exists to feed it.

## Two glossaries, and this is the one that travels

**A clinician's shorthand is theirs.** `hx`, `wnl`, `spo2` and `q6h` are the field's and every ER writes them; `rec 4 days`, `36in 33lb` and a typo confirmed as a token are one person's hand. **The second kind belongs in `scratch/shorthand.md`, not here** — [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects it, on the same terms as the voice model in step 8 and for [#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212)'s reason: the reference is the file a second clinician inherits, and an expansion that resolves against one person's habits is wrong for them rather than merely unhelpful.

**A wrong expansion is not a vague note — it is a fabricated finding.** That is why this split matters more here than it did for a picklist. Reading a stranger's `dm` by this clinician's rule gives their patient a disease or deletes one, and the *Ambiguous* section below is the worked case: it keeps every token and the tell that separates its readings, and states **no** resolution. A resolution there would be a count over one person's notes wearing the authority of a reference.

**Where the two disagree, `scratch/shorthand.md` wins**, which is the rule [setup-clinical-skills](../setup-clinical-skills/SKILL.md) already states for the profile against the reference.

**The tables below were swept on [#228](https://github.com/mshamblin5150-code/clinical-skills/issues/228), so the rule now has a tree behind it.** The rule landed a ticket earlier on purpose — a rule with no tree behind it can still stop the next entry landing in the wrong file, and a tree cleaned with no rule written down fills back up.

**`tools/test_glossary_split.py` is the gate, and it states its own limit.** It reads the first cell of every row and refuses the forms that sweep moved, and it reads a row as a row so the paragraph above may go on naming two of them. **What it cannot reach is a per-account form nobody has listed** — a new row in one clinician's hand lands unflagged — which is why the rule above is what a reader follows and the test is only what catches a repeat.

### Collecting one

**Ask for the tokens rather than a glossary.** Nobody has a list; everybody has a shift's worth of scratch. The cheapest source is the clinician's own day files — run a few encounters through and let the `unknown token` lines in the tier block, or `batch-shift`'s `NEW GLOSSARY CANDIDATES` roll-up, produce the ask. **A token that appeared twice is worth a question; one that appeared once is worth carrying verbatim.**

**Get the expansion in their words and record it verbatim.** An expansion is not a definition — `rec 4 days` is *recheck in four days* because that is what he means by it, and a nearby-sounding gloss is the same class of error as a guessed preceptor surname.

**Ambiguity is collected, never resolved by the collector.** Where a token has two standard readings, ask which contexts take which, and write the *tell* down beside them the way the section below does. **A per-account glossary with no tells is more dangerous than none**, because it converts a token that would have been flagged into one that is silently expanded.

**A confirmed typo is an entry, not a correction.** `2/2j` earns a row in the per-account file because he types it, and a glossary that tidied it would fail to read the next one.

## Common shorthand

**The field's forms.** Every expansion below is one any ER writes; a form that resolves against one person's habits belongs in `scratch/shorthand.md` instead, on the rule above.

| Shorthand | Expansion |
| --- | --- |
| `hx` | history |
| `cc` | chief complaint |
| `dx` | diagnosis |
| `rtc` | return to clinic |
| `us` | ultrasound |
| `t 97.3` | temperature 97.3 °F |
| `spo2 96` | oxygen saturation 96% |
| `vaccs utd` | vaccinations up to date |
| `OP` | oropharynx |
| `L` / `R` | left / right |
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
| `duoneb` | ipratropium-albuterol nebulizer solution |

**A named peritoneal sign is never a throwaway.** Rovsing's, psoas, obturator, Murphy's and McBurney's all appear below, and a positive one recorded in a note whose abdomen is otherwise normal is a contradiction the note has to resolve out loud, not a token to expand and move past. **The spellings a given clinician reaches for are theirs** and live in `scratch/shorthand.md`; the sign is the field's.

### Conditions and history

**The forms below are the field's; the evidence that they are the field's is one account's.** They were confirmed against a sweep of one clinician's full day-file catalog — 49 files (48 unique; one is duplicated on disk), 340 pages, **551 encounters** — the 32 text-layer files extracted, the 17 image-only scans rendered and read. **That is a provenance note rather than a warrant**: a form recurring two hundred times in one hand is still that hand's evidence, so a row here earns its place by being what the field writes and not by how often it appeared.

This said **548 encounters** until 2026-08-15, which was three short: the pages were all read and three encounters were not counted. [batch-shift](../batch-shift/SKILL.md) step 3 carries the reconciliation and is the only place it is written down; issue [#63](https://github.com/mshamblin5150-code/clinical-skills/issues/63). **Nothing in this file is a share of that figure**, and since #228 moved the occurrence tallies to `scratch/shorthand.md` there is no rate here at all, so the correction moves nothing.

| Shorthand | Expansion |
| --- | --- |
| `dm` | diabetes mellitus |
| `htn` | hypertension |
| `cad` | coronary artery disease |
| `copd` | chronic obstructive pulmonary disease |
| `gerd` | gastroesophageal reflux disease |
| `afib` | atrial fibrillation |
| `dvt` | deep vein thrombosis |
| `sud` | substance use disorder |
| `bv` | bacterial vaginosis |
| `hep b`, `hep c` | hepatitis B, hepatitis C |
| `mrsa` | methicillin-resistant *Staphylococcus aureus* |
| `cap` | community-acquired pneumonia |
| `pna` | pneumonia |
| `chole` | cholecystectomy — a past surgery, in a PMH or PSH list |
| `appy` | in a past surgical history, appendectomy — see the ambiguity note below |
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
| `feso4` | ferrous sulfate |
| `b12` | vitamin B12 |
| `vits`, `prenatal vits` | vitamins, prenatal vitamins |
| `gtt` | drops — `ciprodex 4 gtt BID` is four drops twice daily |
| `odt` | orally disintegrating tablet |
| `tx` | treatment, or treated — `nebulizer tx`, `was recently tx with amoxicillin` |
| `qhs` | at bedtime |
| `q4-6h`, `q6-8h` | every 4 to 6 hours, every 6 to 8 hours |
| `mcg` | micrograms |
| `mg/5ml` | milligrams per 5 milliliters — a suspension concentration |

### Tests and findings

| Shorthand | Expansion |
| --- | --- |
| `a1c` | hemoglobin A1c |
| `micro urine` | microscopic urinalysis, ordered alongside `ua` |
| `c/s` | culture and sensitivity — `urine c/s`, `pharyngeal c/s` |
| `rsv` | respiratory syncytial virus |
| `rpr` | rapid plasma reagin — syphilis screening |
| `abg` | arterial blood gas |
| `trop` | troponin |
| `egd` | esophagogastroduodenoscopy |
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
| `fundus measures 39.5 cm` | fundal height in centimeters |
| `g5p4a0`, `g3p1a1` | gravida, para, abortus — the same pattern as `g2p2a0` |
| `iud` | intrauterine device |
| `depo` | depot medroxyprogesterone injection |
| `sud` | substance use disorder — usually with the substance appended (`sud-marijuana`, `SUD - heroin`) |
| `dips`, `chews` | smokeless tobacco — quantified as a duration or an amount, never as a `ppd` rate |
| `oe` / `aom` / `om` | otitis externa / acute otitis media / otitis media |
| `pad` | peripheral artery disease |

### Exam and procedure

| Shorthand | Expansion |
| --- | --- |
| `s1,s2` | first and second heart sounds, normal |
| `2/2` | peripheral pulses 2+ and equal, in an exam — the *Symbols* table below carries the other reading |
| `clear x 4`, `dm x 4` | clear / diminished in all four lung fields |
| `exw`, `iew` | expiratory wheezing / inspiratory and expiratory wheezing |
| `ckls` | crackles |
| `i&d` | incision and drainage |
| `d&c` | dilation and curettage |
| `t&a` | tonsillectomy and adenoidectomy |
| `lac` | laceration |
| `ble` / `rle` / `lle` / `rue` / `lue` | bilateral / right lower / left lower / right upper / left upper extremity |
| `ac space`, `AC area` | antecubital fossa |
| `xerosis` | abnormally dry skin |
| `rovsing`, `psoas`, `obturator`, `murphys`, `mcburneys` | the named abdominal signs. **A positive one is never a throwaway** |
| `kub` | kidneys-ureters-bladder film |
| `flat plate` | plain supine abdominal film |
| `micro urine` | microscopic urinalysis |
| `c/s` | culture and sensitivity — see the ambiguity note below |
| `amy`, `lip` | amylase, lipase |
| `trop` | troponin |
| `uds` | urine drug screen |
| `spot mono` | monospot |
| `gtt` | drops (`cortisporin gtt 4 tid`) |
| `zpac`, `z-pack` | azithromycin course |
| `solu 125`, `solumedrol 125` | methylprednisolone 125 mg |
| `decadron` | dexamethasone |
| `tessalon perle` | benzonatate |
| `macrobid` | nitrofurantoin — **does not reach the renal parenchyma; check it against any flank or CVA finding in the same note** |
| `fht` | fetal heart tones |
| `edd` | estimated date of delivery |

## Ambiguous — resolve from context, never by default

These carry more than one standard expansion and the wrong one invents a diagnosis. Treat them the way `d/c` is treated: read the context, and where the context does not settle it, **flag rather than guess.**

**The tells below are the field's; the resolutions are not.** Which reading a given clinician actually writes is a fact about that clinician's notes, and it lives in `scratch/shorthand.md` — [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects it, and asks for the tell alongside the expansion for exactly this reason. **Where that file is absent, flag; do not fall back on a default**, because no default here is anything but somebody's habit.

**`CVA` — costovertebral angle, or cerebrovascular accident.** Both are ordinary and they can appear in one note:

- `Left CVA tenderness` — costovertebral angle. A physical exam finding.
- `family hx: Mother - CAD, DM, CVA` — cerebrovascular accident. A stroke.

The tell is the neighboring word. `CVA tenderness` is anatomical; `CVA` in a history or problem list is a stroke. Expanding a family history's `CVA` as costovertebral angle loses a stroke from the family history; expanding an exam finding as a stroke invents one. **Neither is recoverable downstream, because both read perfectly well.**

**`dm` — diabetes mellitus, or diminished.** The worst of the set, because both readings are plausible in the same note:

- `hx: dm, htn, hyperlipidemia` — diabetes mellitus. A chronic condition.
- `lungs clear/dm` · `DM on right` · `lung sounds are dm in all fields` — **diminished breath sounds.** A physical exam finding.

The tell is the section. In a history, problem list or family history it is diabetes; **attached to lung sounds it is diminished.** The failure runs both ways and neither is visible downstream: reading the exam's `dm` as diabetes gives a patient a disease they do not have, and reading the history's `dm` as diminished quietly deletes one they do.

**`PPD` — packs per day, or purified protein derivative.** The tell is what it is attached to: a rate carrying a duration — `3 ppd smoker`, `smokes 0.5 ppd x 1 year` — is a smoking history, and a test placed and read is the TB screen.

**`c/s` — culture and sensitivity, or cesarean section.** The tell is the specimen. `urine c/s` and `pharyngeal c/s` are cultures; in an obstetric or surgical history it is the operation, and any catalog carrying obstetric encounters will hold both.

**`hs` — at bedtime, or a typo for "has".** Position decides: attached to a dose, `10 mg PO HS` is bedtime; loose in a sentence — `states hs fever` — it is not an abbreviation at all but a slip for an ordinary word, and a note that dosed on it would have invented an order.

**`appy` — appendectomy, or appendicitis.** The tell is the section: in a past surgical history it is the operation; in an assessment or an active problem it may be the disease. **A note that reads a history's `appy` as an active diagnosis has invented an acute abdomen out of a scar**, which is why this one is worth flagging even when the section looks obvious.

**`WIC` — a walk-in clinic, or the federal nutrition program.** The tell is what the sentence is doing: a place of care or a referral destination is the clinic; a benefits, coverage or nutrition context is the program. Both are ordinary in primary care, and the reading decides what the note says the patient was sent to.

**Local facility abbreviations** — a catalog refers to hospitals and imaging centers by initials for referral destinations. They are per-clinician and are collected by [`/setup-clinical-skills`](../setup-clinical-skills/SKILL.md), not hardcoded here.

### Misspellings

Corrected silently as transcription noise, per the skill's Given rules.

**The forms themselves are one person's and are not listed here.** A misspelling is a token like any other, so the ones a clinician actually types belong in `scratch/shorthand.md` — [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects them and [batch-shift](../batch-shift/SKILL.md)'s `NEW GLOSSARY CANDIDATES` roll-up is where they surface. **A form that recurs is a habit rather than a slip**, so it will be in the next day file too, which is what makes recording it worth the line.

**A drug misspelling is the one that matters most.** A word typo produces an odd-looking note; a drug typo produces a prescription. Correct it, and treat any unrecognized drug spelling as a candidate for the same treatment rather than passing it through as written — the rule against "correcting" a number does not extend to a misspelled drug.

**A misspelling can land on a token the glossary already expands, and that is not hypothetical.** *Diminished* is misspelled commonly enough to collide with `dm` above, which is already ambiguous. Where a slip lands on a live form, the ambiguity rule wins and the token gets flagged rather than expanded twice over.

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
