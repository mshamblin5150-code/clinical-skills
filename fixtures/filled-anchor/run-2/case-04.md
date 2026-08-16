# case-04

Codes below are **proposed, not asserted.** Verify before entering anything.

---

## Step 1 — the FILLED and DERIVED lines, read first

**`DERIVED`, in full:**

| Value | Inputs | Any input filled? |
| --- | --- | --- |
| Height 74 in = 6 ft × 12 + 2 in | Ht 6'2", given | no |
| BMI 25.7 = 703 × 200 ÷ 74² = 140,600 ÷ 5,476 | Ht 74 in given, Wt 200 lb given | no |
| BMI band Z68.25 (25.0–25.9, adult) from BMI 25.7, and E66.3 overweight | BMI 25.7, age 45 given | no |
| Pack-years 51 = 1.5 ppd × 34 years | 1.5 ppd × 34 y, given | no |
| Patient Time = Adult (18 – 60) Hours, from age 45 | age 45, given | no |

**`FILLED·asserted`** declares, verbatim:

> NO VITAL OR BODY MEASUREMENT WAS FILLED. BP, HR, T, RR, SpO2, height and weight are all given;
> the BMI is derived from two given inputs, so the near-threshold disclosure rule does not apply
> to it even though 25.7 sits 0.7 above a band edge

Every other `FILLED·asserted` entry is home medications, allergy status, family history, social
history, ROS negatives, normal exam findings, or an administrative declaration. **None of them is a
vital, a body measurement, or a value any code below rests on** — a normal exam finding anchors no
code, and no medication or administrative field is coded here.

**So the set of numbers carrying `SOURCE: filled` in step 3 is empty**, and the step-4 block
`CODED, ANCHOR WAS FILLED` is empty for this encounter. That is a finding about this note, not an
omission: BMI 25.7 and its band code are derived from a **given** height and a **given** weight, and
[clinical-note](../../../skills/clinical-note/SKILL.md)'s tiers make that a measurement rather than
an invention. `E66.3` and `Z68.25` therefore code **unmarked**.

Completion: every `DERIVED`, `FILLED·asserted` and `FILLED·proposed` entry read; no filled vital or
body measurement exists to write down; all five derived values checked for a filled input, none has
one.

---

## Step 2 — codable elements

**Diagnoses, from the Assessment** (all anchored to given text):

acute upper respiratory infection · bilateral otitis media · acute pharyngitis · fever by history ×
5 days · acute productive cough · pleuritic chest pain · chest tightness 5/10 · diarrhea ×
5 days · epigastric tenderness · diffuse lower abdominal tenderness · right flank discomfort ·
right costovertebral angle tenderness · headache · generalized myalgia · overweight with BMI band ·
GERD · cigarette dependence · underimmunization · bilateral knee pain · post-cholecystectomy and
post-appendectomy absence · healed prior fractures and prior traumatic pneumothorax.

**Procedures, from the Objective and Plan:** 12-lead ECG obtained today (given, from the source
plan). Nothing else was performed — the COVID-19 test, troponin, chest radiograph, urinalysis,
urine culture, CBC, CMP, lipase, CRP, influenza/RSV PCR, stool studies and CT are ordered or
proposed, and the note records that no result exists for any of them.

**Filled-anchored elements:** none. See step 1.

---

## Step 3 — proposed codes

```
ICD-10  J06.9  Acute upper respiratory infection, unspecified
  ANCHOR: "5 days of fever, headache, myalgia, sore throat with pharyngeal erythema,
           productive cough, diarrhea, and a household contact with the same illness"
  SPECIFICITY: needs: the infectious agent — J06 carries "code (B95-B97) to identify
               infectious agent, if known"; the COVID-19, influenza and RSV results are
               all outstanding
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H66.93  Otitis media, unspecified, bilateral
  ANCHOR: "Both tympanic membranes bulging; the left is also erythematous."
  SPECIFICITY: needs: whether suppuration is present, and acute versus chronic — the
               exam records bulging and erythema and no purulence, so H66.003 is not
               earned
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: H66 carries "use additional code ... tobacco dependence (F17.-)"; F17.210 below
        satisfies it

ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "Pharyngeal erythema present"
  SPECIFICITY: needs: the organism — J02 splits streptococcal (J02.0) from unspecified,
               and no rapid strep or culture was obtained
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R50.9  Fever, unspecified
  ANCHOR: "Fever is by history over 5 days; he is afebrile at 97.4 °F today."
  SPECIFICITY: needs: a measured temperature and a pattern — GAPS records that no home
               value and no stated pattern exist
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R05.1  Acute cough
  ANCHOR: "productive cough"; "Duration 5 days, continuous and not improving"
  SPECIFICITY: complete — R05 is split on duration alone, and 5 days documents acute
               rather than subacute (R05.2) or chronic (R05.3)
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R07.81  Pleurodynia
  ANCHOR: "the chest pain specifically worse on deep inspiration"
  SPECIFICITY: complete — R07.81 has no further axis; laterality and severity are not
               axes of this code
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R07.89  Other chest pain
  ANCHOR: "Severity chest tightness 5/10"
  SPECIFICITY: complete — an "Other" residual rather than an unspecified one; the chest
               tightness does not fit a named R07 code, and R07.81 above carries the
               pleuritic component separately
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R19.7  Diarrhea, unspecified
  ANCHOR: "watery diarrhea"; "the diarrhea specifically worse after eating"
  SPECIFICITY: needs: nothing the bedside can supply — R19.7's neighbors are abdominal
               swelling and bowel sounds, not more specific diarrheas, so the word is
               part of the condition's own name. This is one of the two known false
               positives of the unspecified rule (skill's #135 note), recorded rather
               than treated as a documentation gap
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R10.13  Epigastric pain
  ANCHOR: "Tenderness across the entire lower abdomen and in the epigastrium."
  SPECIFICITY: complete — site documented as epigastric, which is the axis R10.1 splits on
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R10.30  Lower abdominal pain, unspecified
  ANCHOR: "Tenderness across the entire lower abdomen and in the epigastrium."
  SPECIFICITY: needs: a quadrant — R10.31 right lower, R10.32 left lower, R10.33
               periumbilical. The exam documents tenderness across the entire lower
               abdomen, so no quadrant code applies today; a localization on recheck
               would move this
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R10.A1  Flank pain, right side
  ANCHOR: "right flank discomfort +"
  SPECIFICITY: complete — laterality documented as right
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R39.851  Costovertebral (angle) tenderness, right side
  ANCHOR: "Right costovertebral angle tenderness."
  SPECIFICITY: complete — laterality documented as right, and left CVA tenderness is
               documented absent
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: the note's own Final diagnosis field carries R10.8A1 Right flank tenderness for
        this finding. R10 carries "excludes2: costovertebral (angle) tenderness (R39.85)",
        which sends an elicited CVA sign to R39.85- rather than to R10.8A-, so R39.851 is
        proposed for the exam finding and R10.A1 above for the reported symptom. R39.85
        itself is NOT BILLABLE — a header — so a proposal naming it would be rejected.
        Two codes rather than the note's one; confirm which the clinician wants entered.

ICD-10  R51.9  Headache, unspecified
  ANCHOR: "I've had a headache, a sore throat, body aches, stomach pain and fever for
           five days."
  SPECIFICITY: needs: an orthostatic component — R51.0 is headache with orthostatic
               component, and nothing positional is documented either way
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.10  Myalgia, unspecified site
  ANCHOR: "generalized myalgia +"
  SPECIFICITY: needs: site — M79.1 splits to mastication muscle, auxiliary muscles and
               other site; "generalized body aches" names no site and there is no
               generalized-myalgia code
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  E66.3  Overweight
  ANCHOR: "Ht 6'2" (74 in) · Wt 200 lb → BMI 25.7"; "It is overweight and it is
           addressed below."
  SPECIFICITY: complete — E66.3 has no further axis; the BMI axis is carried by Z68.25
               below, per E66's own "use additional code to identify body mass index"
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: unmarked deliberately. Both inputs are given, so this is a measurement and not a
        filled value.

ICD-10  Z68.25  Body mass index [BMI] 25.0-25.9, adult
  ANCHOR: "BMI 25.7"; tier block DERIVED — "BMI band Z68.25 (25.0–25.9, adult) from
           BMI 25.7"
  SPECIFICITY: complete — the band is fixed by BMI 25.7, and age 45 selects the adult
               series (Z68's own note: adult codes are for persons 20 years and older)
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: unmarked deliberately, and this is the code the mark usually lands on. 25.7 sits
        0.7 above the band edge and one inch of height would move it — but the height was
        transcribed, not invented, so nothing here rests on a chosen inch.

ICD-10  K21.9  Gastro-esophageal reflux disease without esophagitis
  ANCHOR: "PMH/PSH: Gastro-esophageal reflux disease."
  SPECIFICITY: complete — K21's only axis is the presence of esophagitis, and none is
               documented; no endoscopy is on record to document one
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  F17.210  Nicotine dependence, cigarettes, uncomplicated
  ANCHOR: "Current cigarette smoker, 1.5 packs per day for 34 years."
  SPECIFICITY: complete — product documented as cigarettes, and no withdrawal or other
               nicotine-induced disorder is documented, which is the complication axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z28.39  Other underimmunization status
  ANCHOR: "Not up to date with vaccinations."
  SPECIFICITY: complete — an "Other" residual rather than an unspecified one. Z28.3's
               axes are delinquent versus other underimmunization status, and the source
               records the gap without naming a reason, which is what Z28.39 says
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M25.561  Pain in right knee
  ANCHOR: "Bilateral knee pain."
  SPECIFICITY: complete — laterality documented as right, half of the documented bilateral
               pair
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M25.562  Pain in left knee
  ANCHOR: "Bilateral knee pain."
  SPECIFICITY: complete — laterality documented as left, the other half of the pair
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z90.49  Acquired absence of other specified parts of digestive tract
  ANCHOR: "Past surgical: cholecystectomy, appendectomy."
  SPECIFICITY: complete — Z90.4 names stomach, pancreas and large intestine separately;
               gallbladder and appendix fall to the "other specified parts" child, which
               is a residual and not an unspecified one
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z87.828  Personal history of other (healed) physical injury and trauma
  ANCHOR: "Prior right upper extremity fractures. Prior left shoulder fracture. Prior
           punctured lung — traumatic pneumothorax, healed."
  SPECIFICITY: complete — an "other" residual under Z87.82, whose inclusion term is
               "Conditions classifiable to S00-T88, except traumatic fractures". The
               fractures are healed and no laterality axis exists on this code
  CONFIDENCE: verified against ICD-10-CM FY2026
```

### CPT

```
CPT  93005  Electrocardiogram, routine ECG with at least 12 leads; tracing only,
            without interpretation and report
  ANCHOR: "COVID-19 test, 12-lead ECG and troponin obtained; abdominal workup initiated.
           No results are recorded in the source, so none are reported here."
  SPECIFICITY: needs: a documented interpretation and report — the component split is the
               only axis here, and the note records the tracing as obtained with no
               interpretation written. A documented interpretation earns 93010, or 93000
               if the practice owns the equipment and the interpretation both
  CONFIDENCE: verify this number — no CPT code set ships in this repo, so this descriptor
              and number are recalled, not looked up
```

**No other CPT is proposed.** The COVID-19 test, troponin, chest radiograph, urinalysis, urine
culture, CBC, CMP, lipase, CRP, influenza/RSV PCR, stool studies and CT are ordered or proposed and
have no documented result, and nothing states whether any was performed in-house or sent out — the
technical and professional components belong to whoever performed them. No venipuncture or
specimen collection is documented. **No E/M code is selected**, per step 5; the elements are offered
below.

---

### --- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

**Two of the note's differential entries resolved into codes proposed above and are not repeated
here**, because a code cannot be both proposed for entry and marked not for entry: the favored
*acute febrile viral syndrome* is carried by `J06.9`, and *acute otitis media, bilateral* by
`H66.93`. The organisms named inside the favored entry are refused in step 4.

**The `FILLED·proposed` block declares that eleven of these entries were not stated by the
clinician.** They are documentation of this note's reasoning, which is what a differential code is
for; the mark is recorded here once rather than on each line, because a differential code takes
three parts and may not borrow a `SOURCE` line from the proposed shape.

```
ICD-10  J18.9  Pneumonia, unspecified organism   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J93.9  Pneumothorax, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N10  Acute pyelonephritis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N39.0  Urinary tract infection, site not specified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N20.0  Calculus of kidney   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  A09  Infectious gastroenteritis and colitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K91.5  Postcholecystectomy syndrome   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K27.9  Peptic ulcer, site unspecified, unspecified as acute or chronic, without
               hemorrhage or perforation   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I30.9  Acute pericarditis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I40.9  Acute myocarditis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I24.9  Acute ischemic heart disease, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I26.99  Other pulmonary embolism without acute cor pulmonale   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**One excludes1 collision is worth seeing before any of these is copied anywhere.** `A09` carries
`excludes1: diarrhea NOS (R19.7)`, and `R19.7` is proposed for entry above. The two cannot be
submitted together. Nothing is wrong here — `A09` is not for entry — but it is exactly the pair a
copy-paste out of this block would create.

The *GERD flare* limb of the GERD-or-PUD entry is `K21.9`, proposed for entry above as a
preexisting diagnosis; only the peptic ulcer limb is coded here. The *streptococcal pharyngitis*
entry is refused rather than coded — see step 4.

---

## Step 4 — what documentation is missing

### --- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

```
The infectious agent — COVID-19, influenza and RSV results are all outstanding, and J06
carries "code (B95-B97) to identify infectious agent, if known"
  affects: J06.9

Whether suppuration is present, and acute versus chronic otitis media. The exam records
bulging and erythema; purulence or a documented acute suppurative course earns H66.003
Acute suppurative otitis media without spontaneous rupture of ear drum, bilateral
  affects: H66.93

The pharyngeal organism. No rapid strep and no throat culture were obtained; a result
either way settles J02.0 against J02.9
  affects: J02.9

A measured temperature at home and a fever pattern. Fever is reported over five days with
no value and no pattern recorded, and he is afebrile at the visit
  affects: R50.9

A quadrant for the lower abdominal tenderness. Today's exam documents tenderness across
the entire lower abdomen; a localization on recheck earns R10.31, R10.32 or R10.33
  affects: R10.30

Whether the headache has an orthostatic component. Nothing positional is documented, and
R51.0 is the code that would carry it
  affects: R51.9

A muscle group for the myalgia. "Generalized body aches" names no site, and M79.1 splits
to mastication muscle, auxiliary muscles and other site
  affects: M79.10

A documented ECG interpretation and report. The tracing was obtained and no reading is
written, which is the whole of the component split
  affects: CPT 93005

Nothing at the bedside would move R19.7 Diarrhea, unspecified — recorded here for
completeness because the flag reads "needs:", not because a documentation gap exists.
R19.7 has no sibling naming a more specific diarrhea
  affects: R19.7
```

### --- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

```
None. The tier block states "NO VITAL OR BODY MEASUREMENT WAS FILLED", and every derived
value — height in inches, BMI 25.7, the Z68.25 band, 51 pack-years, the Patient Time band
— has given inputs only. E66.3 and Z68.25 are therefore proposed unmarked, which is the
one place in this worksheet where the absence of a mark is itself the finding.
```

### --- NOT CODED, NOTHING ESTABLISHED IT ---

```
COVID-19, named inside the favored acute febrile viral syndrome entry — five days of fever,
myalgia, sore throat, cough and diarrhea, with a symptomatic household contact; the test is
ordered and no result exists
  NOT CODED: U07.1  COVID-19
  needs: the COVID-19 result. The descriptor asserts the disease and nothing has tested for it
  proposed instead: J06.9  Acute upper respiratory infection, unspecified, with the documented
    symptoms coded alongside it
  and Z20.822 Contact with and (suspected) exposure to COVID-19 is NOT proposed either — the
    source states no known exposure to anyone who tested positive, and the wife is symptomatic
    and untested. Testing her is what would earn it, and the Plan already asks for that

Influenza, named inside the same entry — five days of a febrile respiratory illness, not up to
date with vaccinations, influenza PCR added by this note and not yet resulted
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory
    manifestations
  needs: a positive influenza test. "Unidentified influenza virus" still asserts influenza, and
    J06.9 carries an explicit excludes1 against it
  proposed instead: J06.9  Acute upper respiratory infection, unspecified

Streptococcal pharyngitis, suspected only far enough to be argued against — sore throat with
pharyngeal erythema, but no cervical lymphadenopathy (a given), no tonsillar exudate, afebrile
today and a prominent cough, Centor 0-1, no rapid strep indicated
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: a positive rapid strep or throat culture. The descriptor names the organism, and none
    was tested for
  proposed instead: J02.9  Acute pharyngitis, unspecified
```

---

## Step 5 — E/M supporting elements, offered only

No level is selected. **The MDM phrasing below is recalled — no coding guidelines ship in this
repo — so treat the mapping as a starting point the clinician confirms.**

**Problems addressed.** One acute illness with systemic symptoms plus a treated acute bacterial
focus (bilateral otitis media, antibiotic prescribed), on a background of four documented chronic
problems (GERD, nicotine dependence, bilateral knee pain, underimmunization). Twelve differential
entries carry rationale, and three of them — pyelonephritis, pneumonia and recurrent pneumothorax —
are **undiagnosed new problems with uncertain prognosis** rather than excluded ones. The right CVA
tenderness is the entry that carries the most weight in this column: it is documented, unexplained,
and the study that would settle it has not resulted.

**Data reviewed or ordered.** Ordered and outstanding: COVID-19 test, 12-lead ECG, troponin,
urinalysis with microscopy, urine culture, CBC with differential, CMP with LFTs, lipase, CRP,
chest radiograph two views, influenza and RSV PCR. Conditional: stool studies with GI pathogen
panel, CT abdomen and pelvis with contrast, *H. pylori* testing. **No result is available for any
of them**, so nothing in this encounter is documented as reviewed — that is a distinction the
clinician should carry into the level, and the recheck at 48-72 hours is where the review lands.

**Risk.** Prescription drug management on four agents (amoxicillin-clavulanate, acetaminophen with
a stated 3 g ceiling, benzonatate, omeprazole continued), plus two documented withholding
decisions with reasons — loperamide held against five days of fever with undifferentiated
abdominal pain and CVA tenderness, and NSAIDs avoided against documented GERD with epigastric
tenderness. Conditional oseltamivir on a positive influenza test. Named return precautions and a
48-72 hour recheck.

---

## Completion check

- 23 codes proposed for entry, plus 1 CPT. Each carries a number, an official descriptor pasted
  from `tools/icd10_lookup.py`, an anchor, a specificity flag with substance beyond its keyword,
  and a confidence flag. **No code carries a sixth `SOURCE` part, because no anchor was filled.**
- Every code whose official descriptor contains `unspecified` or `not specified` reads `needs:`,
  never `complete` — J06.9, H66.93, J02.9, R50.9, R19.7, R10.30, R51.9, M79.10.
- Billability checked on every proposal. One header was found and avoided: `R39.85` is not
  billable, so `R39.851` is proposed in its place.
- 12 differential codes, three parts each, `NOT FOR ENTRY` on every line, none of them borrowing a
  fourth part.
- Every filled value in the tier block accounted for: none supports a code.
- Every hedged diagnosis accounted for: the favored viral syndrome is coded as `J06.9`; COVID-19,
  influenza and streptococcal pharyngitis are refused with the code named inline and the code the
  encounter does support proposed in its place.
- ICD-10-CM release: FY2026, from `reference/icd10cm-2026.sqlite`. CPT is recalled, not verified.
