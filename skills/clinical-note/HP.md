# FNP H&P — template

The long-form branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

**The italicized instructions under each heading are the school's rubric, not commentary.** Obey them literally and keep them out of the finished note.

```
Chief Complaint
<one line>

Allergies (with reaction)
<Drug - allergen - reaction, or NKDA;
 Food - allergen - reaction, or none reported;
 Environmental - allergen - reaction, or none reported;
 one category per line>

History of Present Illness (OLDCARTS)
<all eight carry a value; none is left blank or "not documented">
<Onset and Duration take a value naming more than one symptom's timeline where
the shorthand dates symptoms differently. Each is written duration-first as
"<duration> for <symptoms>", clauses separated by a semicolon — see SKILL.md>
Onset:
Location:
Duration:
Character:
Aggravating:
Relieving:
Timing:
Severity: <N/10, and the complaint it belongs to>

<then a short narrative paragraph: age, sex, who brought them, the course,
prior treatment and testing>

Past Medical History including Medications (with reason for taking)
PMH:
<condition - ICD-10 code where the rubric's examples carry one>

Surgical history:

Medications:
<drug name as written in shorthand, dose, route, frequency, ongoing status or duration - reason for taking;
 infer a compatible complete regimen when PMH is present and the shorthand is silent>

Family History (3 generations)
Patient:
Mother:
Father:
Maternal grandparents:
Paternal grandparents:
Siblings:

Social History:
Occupation, education, marital status, tobacco, alcohol, recreational drugs,
spiritual, cultural, environmental, nutrition, fitness, sleep
<one line each, in that order; every line carries a value and none is left blank
 or "not documented">

Subjective:
Review of Systems (systems pertinent to the chief complaint), Use short succinct
statements, and do not use sentences. Do not use reviewed and negative on an
individual system line.
<one system per line: fragment; fragment>
All other systems reviewed and are negative.

Objective:
Vital signs
BP / HR / Temp / O2 Sat / Height / Weight / BMI

Physical Exam (pertinent to the differential)
Use short succinct statements, do not use sentences
<system: fragment; fragment>
Cardiovascular: Regular rate and rhythm; no murmurs, gallops, or friction rubs; radial pulses 2+ bilaterally; posterior tibial pulses 2+ bilaterally
Respiratory: Clear to auscultation bilaterally
GI: Bowel sounds are positive in all quadrants; no tenderness, guarding, masses, or organomegaly noted
Neurologic: Alert and oriented x 4

Lab, x-ray, other tests
<given results; given orders carrying no result, marked as ordered;
 "No new testing today" only where the encounter ordered nothing>

Assessment
Give 3 differential diagnoses with rationale of how you excluded each to arrive at
the final diagnoses/diagnoses. Pre-existing diagnoses with ICD-9 codes, Actual
diagnosis/diagnoses with ICD-9 codes, Screenings appropriate for age, list them
even if you did not do any.

Pre-existing diagnoses with ICD-10 codes:
<condition - code>

Differential diagnoses:
1. <diagnosis - code>
2. <diagnosis - code>
3. <diagnosis - code>

Final diagnosis:
1. <selected condition - code: decisive patient-specific discriminator>
2. <second selected condition - code: decisive discriminator, when present>

Medical Decision Making:
1. <same diagnosis - code as differential item 1> — <favored, less likely, or must exclude>.
   <patient-specific evidence and why it leads to the resulting decision>
2. <same diagnosis - code as differential item 2> — <favored, less likely, or must exclude>.
   <patient-specific evidence and why it leads to the resulting decision>
3. <same diagnosis - code as differential item 3> — <favored, less likely, or must exclude>.
   <patient-specific evidence and why it leads to the resulting decision>

E/M: <supported complexity> complexity — <concise patient-specific problems/data/risk reason>; <code>, <new|established> patient.

Screenings appropriate for age:
<list>

Plan
Non-pharmacologic:
Pharmacologic:
<drug concentration; dose route frequency duration>
Health Promotion/Patient Education:
Referral/Follow-up:

Discussion
<short paragraph: why this presentation fits the chosen diagnosis, and the
significance of any genetic or chronic condition that is not driving the acute
illness but matters for counseling and future care>

Coding worksheet
Patient status: <new|established> — <identity map|Medatrax>
ICD-10-CM: <final for-entry code - descriptor; one line per code>
E/M: <final code - descriptor>
Problems: <level and concise patient-specific support>
Data: <level and concise patient-specific support>
Risk: <level and concise patient-specific support>
MDM: <supported complexity> — <the two of three elements met>
CPT: <code - short descriptor; one line per supported procedure, or None>
HCPCS: <code and units - short descriptor; one line per supported supply or drug, or None>
Coding freshness: PASS
```

## Section notes

**The four Plan labels above are exhaustive.** Oxygen belongs under `Pharmacologic:`. Monitoring, positioning, and laboratory and imaging orders belong under `Non-pharmacologic:`; orders also remain on Objective's `Labs/Tests today` line. Health promotion belongs under `Health Promotion/Patient Education:`, and referrals under `Referral/Follow-up:`. Write no fifth label.

**No OLDCARTS element is ever blank.** Eight headings, eight values — `not documented` beside any of them is a defect, not a disclosure. Where the shorthand supplies none, infer one that follows from the presenting complaint; that is the same act as the exam of a system the shorthand never mentions, which [SKILL.md](SKILL.md) lists as grounded and expected. Each filled element is declared in `FILLED·asserted` carrying its value.

**Severity is a numeric pain scale.** `6/10 facial pressure`, never a word and never blank. It is the one OLDCARTS element that is not ordinary filled content — it takes the filled-vital treatment, and the reasoning, the 0/10 boundary and the two forms in which the score is a *given* are all in [SKILL.md](SKILL.md) under *Filled vitals, body measurements and the pain score*. Do not restate them here; do apply them.

**The HPI is patient history.** Its narrative advances the symptom chronology, context, prior evaluation, attempted treatment, and response. Current examination findings, current results, medication administered today, orders, referral, transfer, and disposition begin in their owning later sections and are not replayed here. Apply [SKILL.md](SKILL.md)'s *HPI is history, not a replay of the visit* ownership pass before finishing.

**The finalized coding worksheet is separated from both the clinical note and the Medatrax fields.** Run [icd10-cpt](../icd10-cpt/SKILL.md) against the note plus tier block and complete the required coding-freshness gate. Render the final code populations, account-backed status, patient-specific problems/data/risk support, two-of-three conclusion, and compact pass line. Keep technical receipts, anchors, specificity, confidence, provenance, and source locators private.

**ROS and Physical Exam** — individual lines use fragments: `Respiratory: No wheeze; no increased work of breathing`, never `Respiratory reviewed and negative`. Write one ROS system per line, then end the ROS with the single global closer `All other systems reviewed and are negative.`

**Family History** is filled almost entirely. Where no family disease is supplied, phrase each line as a report of absence — `No chronic illness reported` — never as an examined finding. Where the shorthand supplies a family disease bundle without relatives, distribute every disease plausibly across the three generations under [SKILL.md](SKILL.md)'s rule and permit the same disease in more than one relative. Each relative's multi-disease list in this section joins the last disease with `and`, never `or`.

**Social History is no longer that**, and it used to be governed by the same sentence. Every one of the twelve lines carries a value, **and none of them is a hedge**: `tobacco not documented this visit` is a sentence defending the note rather than reporting on the patient, which drift row 12 has forbidden since issue #28. Which value each line takes is [SKILL.md](SKILL.md)'s business under *Which way a social or allergy slot reads* — tobacco is settled by a count over the corpus and every other social line by the grounding rule — and drift row 17 checks it. Do not restate those rules here; do apply them, and declare every filled line in `FILLED·asserted` carrying its value. Issue #29.

**Allergies (with reaction)** is the same class and takes the same treatment. Its three ordered lines are always present: `Drug - NKDA`, `Food - none reported`, and `Environmental - none reported` where the shorthand is silent. A stated item replaces only its category's negative; it is a given and survives unchanged. Where a drug the Plan proposes rests on an inferred `NKDA`, that FILLED line says so.

**It survives *in this field*, on the line for its kind** — drug, food, or environmental. The branches now carry the same three-line instruction. Which kind an allergen is, and what a food intolerance takes, are [SKILL.md](SKILL.md)'s business under *Which way a social or allergy slot reads*: do not restate them here, do apply them. Issues #96 and #168.
**This heading is the rubric's own and it asks for the reaction, so the reaction is written.** Where the shorthand names an allergen and stops, the reaction is inferred and declared in the tier block, and **the heading's line carries no marker of it**: `Penicillin - rash`, never `reaction not documented`. After obvious misspellings are corrected, **each distinct allergen gets its own declaration**, naming what the reaction was **reasoned from for that allergen**; one rationale for the list is not several reasoned reactions. **An inferred reaction never licenses a drug the allergen would otherwise bar**, which is the limb that keeps a generated `rash` from making a cephalosporin look safe. The rest, including why the disclosure floor is drawn at drug and food, is [SKILL.md](SKILL.md)'s under *The reaction beside a given allergen*. **The template's separation of the drug status from the other kinds is load-bearing under that floor** rather than presentational — it is the split the ICD-10-CM code set makes between `Z88` and `Z91.0-`. Issues #94 and #205.

**The historical placeholder changed twice.** [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96) first aligned the branches around one field with every stated allergen named by kind. [#168](https://github.com/mshamblin5150-code/clinical-skills/issues/168) then made the three category lines explicit and supplied their silent values. The separation survives both changes; quoting either retired placeholder as the live instruction would recreate the stale-string defect [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) records for figures.

**`Lab, x-ray, other tests` is not a results-only line**, and its placeholder here said it was. A test the encounter ordered goes on it as an order carrying no result, because a given order is a given and having no value to report is not a reason to drop it. `No new testing today` is reserved for an encounter that ordered nothing — writing it over a plan line that names a test is a false statement about the visit, not a cautious one. [SKILL.md](SKILL.md)'s *A given order is a given* is the rule; drift row 18 counts it. Issue #66.

**ICD-9 vs ICD-10** — the rubric headings say ICD-9. That text is stale; supply ICD-10-CM codes under the heading as written. Codes follow [icd10-cpt](../icd10-cpt/SKILL.md): anchored to documented findings, and flagged for verification. Give it the tier assignment along with the text — it marks a code resting on a filled value `SOURCE: filled`, and the note body alone cannot say which values those are.

**Differential rationale** is the graded core, and it belongs in Medical Decision Making rather than beneath the Differential heading. Each excluded diagnosis needs the specific finding that excludes it — `no facial swelling, no focal sinus tenderness` — drawn from the exam, whether that exam line is given or filled.

**Every final diagnosis already exists in the differential with the same code.** Add entries when the conclusion contains more than the rubric's three-item floor; never introduce a diagnosis only under `Final diagnosis`. Attach the decisive patient-specific discriminator to each selected diagnosis, using a short numbered list when several are final.

**Medical Decision Making is required on every H&P.** Keep the differential itself as a clean numbered, likelihood-ranked list. Then number MDM one-for-one in the same order: a diagnosis-and-code header with `favored`, `less likely`, or `must exclude`, followed by the case-specific evidence and why it leads to the decision carried into the Plan. This copies the clinician's case-study Assessment shape without scholarly citations.

**The list is numbered and ranked most likely first, and `1.` is the most-likely entry.** The rule is [SKILL.md](SKILL.md)'s under *The shape of the differential* and binds both branches; on this branch **the numbered differential item is one clean diagnosis-and-code line**. Its matching numbered MDM item carries the likelihood verdict, case-specific evidence, exclusion reasoning, and resulting decision. **A diagnosis argued down inside a paragraph is a defect rather than an entry**, so three diagnoses rejected in prose are three numbered differential items with three matching MDM items. The rubric asks for *"3 differential diagnoses with rationale"* and numbering them is its own instruction read plainly, not a departure from it. Drift row 23 walks it. Issue [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70).

**And the count does not stop at this heading.** A diagnosis-shaped line written anywhere else in the Assessment — under a `problems addressed today` block or any heading a run invents — is an entry and carries a code, because a rule escapable by moving a line one heading down is not a rule. A **measurement of the patient's own body** is a diagnosis here and carries its code; a **line of reasoning** is not, and belongs in the rationale of the entry it concerns. Drift row 13 counts it.

**Every diagnosis code stays in the note form.** Preexisting, differential, and final-diagnosis codes are note content; none travel to Medatrax Add Visit Data. [SOAP.md](SOAP.md) carries the same requirement. **The codes and the clean differential layout match across the branches; H&P adds the separate numbered MDM section.** Issue #19.

**No diagnosis the encounter did not establish gets a code that overstates it**, and that reaches the `Final diagnosis` line as readily as the differential — a hedge is most often on the conclusion. [icd10-cpt](../icd10-cpt/SKILL.md) declines a descriptor naming a confirmed organism or disease where nothing established either: a suspected COVID-19 with no swab takes `Z20.822 Contact with and (suspected) exposure to COVID-19`, not `U07.1`. Drift row 13 in [SKILL.md](SKILL.md) checks it.

**Once a code is declined, the entry is named for the one that survives.** The rule is [SKILL.md](SKILL.md)'s under *Naming a differential entry*. The Differential line stays `<diagnosis - code>` and carries nothing else. The matching MDM item carries the refusal with its reasoning, written as the welded `NOT CODED: <code> <descriptor>, <reason>` pair [SKILL.md](SKILL.md) requires:

```
Differential diagnoses:
2. Pain in left elbow - M25.522

Medical Decision Making:
2. Pain in left elbow - M25.522 — less likely.
   The 5/10 pain followed a fall and the elbow radiographs ordered today have no result. NOT CODED: S52.125A Nondisplaced fracture of head of left radius, initial encounter for closed fracture, nothing established it.
```

**The `Final diagnosis` line keeps the hedge instead**, the way [SOAP.md](SOAP.md)'s does. The clean Differential line keeps the supported code, and the matching MDM item holds any declined code and its reason:

```
Differential diagnoses:
1. Community-acquired pneumonia, pneumococcal organism suspected - J18.9

Final diagnosis:
1. Community-acquired pneumonia, pneumococcal organism suspected - J18.9: five days of fever and focal crackles make this most likely.

Medical Decision Making:
1. Community-acquired pneumonia, pneumococcal organism suspected - J18.9 — favored.
   Five days of fever and focal crackles fit, so treatment and the ordered chest film proceed; the film has no result. NOT CODED: J13 Pneumonia due to Streptococcus pneumoniae, nothing tested for the organism.
```

**This branch's conclusion is `Final diagnosis`, and that is a deliberate departure from the rubric.** The rubric's Assessment instruction — quoted verbatim in the template above — names *"Actual diagnosis/diagnoses with ICD-9 codes"*, and this file's opening rule says obey those instructions literally. **The clinician overruled it on 2026-08-16**, having been shown that the heading is the school's rather than this repo's: both branches now write `Final diagnosis`, so one encounter's conclusion reads the same whichever template it is written in, and drift row 22 has one heading to name instead of two.

**What that costs is written here rather than discovered by a grader.** A reader marking against the rubric's own wording will not find an `Actual diagnosis/diagnoses` heading in an H&P. The content is unchanged and sits under a heading the rubric's *narrative* also uses — *"to arrive at the final diagnoses/diagnoses"* — but the section label no longer matches the list. **The plural survives**: the rubric permits more than one conclusion, so the template's placeholder carries a semicolon-separated second pair, which `SOAP.md`'s own `Final diagnosis` line has never had to.

**The `ICD-9` heading above is a different case and is not precedent for this one.** There the rubric text is *stale* and the fix is to supply the right codes under the heading as written; here the heading itself changed. One keeps the rubric's words and corrects its content, the other does the reverse.

**Both branches now keep the Differential itself clean.** The H&P's separate MDM section is where the reasoning continues, one item for every Differential entry and in the same order. `python tools/differential_scan.py <a run directory>` reads this branch's current shape as well as the historical one and checks the mechanical limb of row 22. **It still reads the retired `Actual diagnosis/diagnoses` heading too**, because every H&P written before today opens its conclusion that way and a scanner that stopped reading them would report exit 2 on a real run. Issues #68 and [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

**Screenings** is a filled list keyed to the patient's age. The rubric wants it present even when nothing was done.

**Pharmacologic** carries doses. Concentration and volume are givens; the milligram equivalent is **derived** and its arithmetic goes in the tier block — in the block, never beside the drug. **A parenthetical on a Pharmacologic line, where there is one, holds the trade name and nothing else**: the tier of each part of the sig belongs in the tier block, and `Medications (with reason for taking)` is the heading where a reason lives. The rule itself is drift row 12 in [SKILL.md](SKILL.md).

**Started cetirizine becomes a daily ongoing medication.** Unless the shorthand supplies a different regimen, write `cetirizine 10 mg PO daily, ongoing`; do not turn a new Zyrtec instruction into a short nightly course. A clinic-administered dose does not by itself complete the outpatient pharmacologic plan when the diagnosed condition still needs treatment after discharge.

**Historical medications are complete too.** The Medications list never defers with `unavailable` or `reconcile`. Infer a compatible regimen for PMH conditions that ordinarily receive maintenance pharmacotherapy, and complete any named drug's dose, route, frequency, and ongoing status or duration. Declare every generated component in `FILLED·asserted`.

**Completeness is PMH coverage, not a minimum count.** In the private `FILLED·asserted` accounting, map every PMH condition to its medication, a shared medication, or no routine maintenance pharmacotherapy on the available facts. Keep the mapping out of the finished note and do not pad a short list merely to make it look substantial.
