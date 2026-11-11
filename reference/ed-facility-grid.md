# ED Facility Level — Intervention Grid

**Version:** v0.6.5, tested 2026-11-10. Adopted by
[ADR 0444](../docs/adr/0444-the-repository-carries-a-tested-ed-facility-grid-and-office-mdm-check-sheet.md),
which records the clinician's decisions, the panel results and the limits.

Hospital facility level for a Type A emergency department: 99281–99285 on the
hospital claim (Type B: G0380–G0384). **Not the clinician's professional level**,
which the CPT MDM table sets (see [office-mdm-check.md](office-mdm-check.md) and
`icd10-cpt` step 5). Item placement follows the published BCBS Texas CPCP003 grid
(2023; the Oct 6, 2025 version has the same items) except where a departure is
marked [D] and explained at the end. A hospital uses one method only. Why a grid
and not a point sheet, and the CMS framework behind it, are in
[em-point-systems.md](em-point-systems.md).

## How to assign the level
1. **What counts.** The nursing and ED record for the ED portion of the visit
   only. The ED portion ends at the first of: the observation order, the
   inpatient admission order, or the patient's departure from the ED
   (discharge, leaving, or departure on transfer). Boarding (time after an
   observation or admission order) does not count. A patient waiting for
   transfer is still in the ED portion until departure. Exception: the Level 5
   coordination item counts the ED staff's bed or ICU request or
   accepting-unit call for an admission decided during the ED portion, even
   when documented after the admission order. Coordination after an
   observation order, including an inpatient request when observation
   converts to admission, does not count.
2. **Highest item wins.** The level is the highest level with at least one
   listed item documented as performed. Do not add levels together. Anything
   not listed below does not raise the level.
3. **Staff work.** Count hospital staff work. The clinician's decisions,
   prescriptions and procedures belong on the professional claim, except
   that an item naming the service itself (for example epistaxis packing,
   NG or gastrostomy tube placement, urinary catheter placement) counts
   whoever performs it, because the hospital supplies the room, supplies and
   support either way; an item reading "preparation or assist" counts only
   the staff work (clinician ruling, 2026-11-10).
4. **Packaged versus separately paid** (status indicators from the October
   2026 OPPS Addendum B).
   - Listed items for services packaged into the ED visit can set the level:
     status N (for example IV start or saline lock, moderate sedation
     monitoring), Q4 (laboratory tests) and Q1 (for example EKG tracing,
     nebulizer, IM/SC injection, simple repair, some splints such as 29125,
     catheter, NG tube, epistaxis packing, gastric lavage). A packaged service
     this grid does not list, such as pulse oximetry, does not set the level
     (rule 2; see Not placed). Addendum B lists the ED visit codes as status J2;
     CMS's public outpatient code editor specification (v17.1) processes an ED
     visit without comprehensive observation as status V, which packages Q1
     services; the current release is AHA-licensed and was not read.
   - **This grid's choice** under 72 FR 66806 (hospitals may decide): services
     Medicare pays separately (status S or T, for example IV pushes and
     infusions, transfusion, lumbar puncture, paracentesis, intubation,
     cardioversion, CPR, abscess drainage, joint aspiration, intermediate
     repair, closed fracture treatment, bladder irrigation), and the staff
     preparation and assistance that belong to them, do not set the level.
     Staff work not paid by those codes, named in the items below, does.
     **One exception: imaging** (below). Whatever an imaging study's status
     (S, Q3 or other), the ED staff's preparation for it counts, and the study
     is the proxy for that preparation.
   - Except for the imaging items, a listed item does not count when the
     service it describes meets the description of an S or T code; report that
     code instead (for example a splint or cast that is part of fracture
     treatment; a long-arm, long-leg or short-leg splint application such as
     29105 or 29515, which is status T whether or not a fracture is treated;
     or cast removal), so the same work is never both a level item and a
     separately paid line.
   - Moderate sedation (status N) monitoring counts even when the sedated
     procedure is S or T, because sedation is not paid separately [D].
   - A status J1 procedure (for example a central line or chest tube)
     packages the whole claim, including the visit, into one comprehensive
     payment; still report the level from the other items.
   - **Imaging.** The imaging items count the ED staff's preparation for a
     study (processing the clinician's order and arranging the study with
     imaging, safety screening, readying and sending the patient), as the BCBS
     Texas items do ("Preparation for plain X-rays"; "Prep for one special
     imaging study"), not the study itself, which is reported on its own line.
     Under the same 72 FR 66806 option, this grid uses the study as the proxy
     for that staff work, as the one exception to the separately paid rule. A
     study ordered by the ED clinician and performed by hospital technical
     staff (the imaging department, or the echocardiography or vascular lab)
     during the ED portion is the evidence of that preparation; no separate
     preparation note is required [D: hospital choice]. A study with an
     imaging-department result during the ED portion counts as ordered by the
     ED clinician and performed by hospital technical staff unless the record
     shows otherwise. A study the clinician performs at the bedside, or one
     not performed during the ED portion, does not count.
     - **Advanced imaging** means CT (including CT angiography), MRI,
       ultrasound (including echocardiography and vascular duplex) or a V/Q
       scan. A plain X-ray is the Level 3 item. Other nuclear medicine studies,
       fluoroscopy and any other modality are not listed (rule 2).
     - **Counting studies:** each distinct CPT-coded study is one study. The
       same code reported for both sides or more than once in one trip
       (RT/LT, -50, multiple units) is one study; a separately ordered repeat
       study is another.
5. **Orders and indications.** (order): an order is in the record.
   (indication): a documented abnormal finding for this patient (vital sign,
   examination, rhythm or test result). For continuous cardiac monitoring,
   serial vital signs and serial cardiac studies only, the indication may
   instead be a reason the clinician documents in the order or the note as
   one of: suspected acute coronary syndrome; suspected arrhythmia; syncope or
   near-syncope (a documented loss or near-loss of consciousness, not
   dizziness or weakness alone); suspected stroke; ingestion or overdose of a
   cardiotoxic or respiratory-depressant substance. A triage complaint, a
   standing or nursing protocol, or arrival mode does not supply an
   indication. Automated monitor readings count toward a vital-sign set only
   while the patient is roomed in the ED portion and only when staff have
   validated them in the record.
6. **Counting nebulizers.** A continuous nebulizer counts one treatment for
   each completed 20 minutes of documented run time (start and stop times or
   a documented duration). A remainder under 20 minutes adds nothing, except
   that a whole run shorter than 20 minutes counts one treatment. A
   continuous nebulizer with no documented run time counts one treatment;
   query for the times. Add these to any intermittent treatments (15 min = 1,
   45 min = 2, 60 min = 3) [D: BCBS does not say how to count a partial
   period].
7. **Left before being seen.** Medicare: no visit charge when the patient
   leaves before being seen by a physician or other practitioner, roomed or
   not (CMS FAQ 2297, as quoted by AAPC; services must be "furnished under
   the order of a physician or other practitioner," Medicare Benefit Policy
   Manual ch. 6 §20.5.2, continued under §20.5.3). For Medicare, a service
   given only under a standing order or triage protocol before any
   practitioner contact is not billed; a test a practitioner ordered for this
   patient may be billed on its own line and never raises the level. (Whether
   a physician-signed protocol meets Medicare's order requirement was not
   verified; check before use.) Other payers: follow the contract; where it
   allows a charge (for example BCBS Texas, which lists elopement before
   evaluation under 99281), the level is Level 1, whatever other items were
   done (clinician ruling, 2026-11-10). When the record does not name the
   payer, report no visit and query the payer; report Level 1 only once the
   payer is confirmed to allow a charge.
8. **Critical care.** Critical illness or injury "acutely impairs one or more
   vital organ systems" with a high probability of imminent or
   life-threatening deterioration (the CPT definition as quoted in Kaiser
   Permanente Washington's policy and CorroHealth, Dec 2023). With 30 or more documented minutes of
   active face-to-face critical care, report 99291 (and 99292 when provided)
   and report no level from this grid for the same encounter (whether a
   separate, earlier ED visit may also be billed was not verified). Count
   physician and staff time once when they overlap. Report ancillary services
   separately; the outpatient code editor conditionally packages them (Claims
   Processing Manual ch. 4 §160.1). Under 30 minutes, use this grid. Before
   use, check this rule and the 99292 threshold against the CPT 2026
   critical-care guidelines in the book; the definition above is a secondhand
   quotation.
9. **Trauma activation.** Revenue code 68x only at a state- or
   locally-designated or ACS-verified trauma center, for a patient with
   prehospital notification meeting field triage criteria or delivered by
   inter-hospital transfer, given the team response. Report one unit of G0390
   per day, with 68x and 99291 on the same date. Under 30 minutes of critical
   care, 68x may be reported but G0390 may not (§160.1; CorroHealth Dec 2023).
10. **Observation.** One comprehensive Medicare payment (C-APC 8011) when the
   claim has G0378 of 8 or more hours, an ED visit (Type A or B) or critical
   care the same day or the day before, and no status T or J1 procedure (90 FR
   53460). Still report the level from the ED portion. **Direct referral:** a
   patient referred directly to observation or admitted by a community
   physician who has already seen the patient, with no associated ED visit,
   clinic visit or critical care on the day observation begins, gets no ED
   level, even when the patient passes through the ED or ED staff carry out
   the referring physician's orders; report those services separately. For
   observation, report G0379 with G0378 on the same date (Claims Processing
   Manual ch. 4 §290.5.2) [D].
11. **Audit.** At a set interval, compare the hospital's level distribution
   and how often each item sets the level with its own baseline. CMS states it
   reevaluates visit-level patterns (72 FR 66805) and does not expect a normal
   distribution at a single hospital (72 FR 66807), so a national mix is not a
   target. Each interval, a second coder independently re-levels a sample of
   charts; disagreements are resolved and recorded. Track how often the IV/IO
   reassessment item, the cardiac-monitoring item, the advanced-imaging items
   and the serial-cardiac item set the level.

## Level 1 — 99281
- Nursing assessment with no other item on this grid
- Visit only for a medication refill or a work or school excuse
- Simple wound recheck; uncomplicated dressing change
- Uncomplicated suture or staple removal
- Booster or follow-up immunization only (an immunization given during any
  visit never counts as a parenteral item)
- Left before being seen, where the payer allows a charge (rule 7)

## Level 2 — 99282
- Bedside point-of-care test by ED staff, waived or not (dipstick, glucose,
  rapid strep, urine pregnancy, stool occult blood) [D]
- Visual acuity
- Skin-adhesive closure (tissue adhesive or adhesive strips) applied by ED
  staff; a closure the clinician performs is the assist item below
- Over-the-counter medication given (classify by the product given: a drug
  sold over the counter at the dose given is over-the-counter unless the
  record shows a prescription product was dispensed; a discharge prescription
  does not classify the ED dose; if the record does not show which, code it
  here and query)
- Preparation or assist for a simple laceration repair, a clinician's
  skin-adhesive closure, or skin foreign body removal (staff setup,
  irrigation, or a dressing staff apply after the clinician's repair)
- Ear irrigation; prefabricated splint, sling or immobilizer applied by ED
  staff, where the application meets no S or T code (rule 4) and the device
  is not reported on its own line [D]
- Crutch or walker teaching [D]
- Discharge teaching for a new prescription [D]

## Level 3 — 99283
- Arrival by EMS or ambulance
- IV start or saline lock (with or without medication) [D]
- IM or SC injection given (not an immunization or local anesthetic) [D]
- One nebulizer treatment
- Laboratory tests: a specimen sent to and accessioned by the hospital
  laboratory for an ordered, billable test, shown by an accession or specimen
  number, a laboratory collection or receipt time, or a result from a
  laboratory analyzer (a urinalysis result reporting microscopy, such as cells
  per high-power field, is a laboratory analyzer result and shows laboratory
  performance without an accession number or time).
  A test performed at the bedside by ED staff is the Level 2 item however its
  result is labeled or filed. When the record does not show whether the
  laboratory or ED staff performed the test, code the Level 2 item and query.
  Hold or extra tubes never count [D]
- Plain X-ray of one or more body areas (rule 4, Imaging) [D]
- Prescription medication given by a non-parenteral route (oral, sublingual,
  rectal, inhaled by metered-dose inhaler, topical, ophthalmic, otic or
  nasal). Oxygen is not a medication here; it counts only under the oxygen
  items. A topical or local anesthetic applied for a procedure counts only as
  preparation for that procedure. Contrast counts only through the imaging
  items.
- Urinary catheter placement, or in-and-out catheterization
- Cervical spine immobilization device in place
- Staff fluorescein instillation or slit-lamp setup for a corneal exam [D]
- Epistaxis packing
- Oxygen by nasal cannula (not high-flow) or simple face mask (indication;
  not counted as a prescription medication) [D]
- Emesis or incontinence care
- Anxiety with a documented staff calming intervention or simple treatment
  [D]
- Psychiatric medical clearance with staff safety screening [D]
- Post-mortem care

## Level 4 — 99284
- One advanced imaging study (rule 4, Imaging)
- Two nebulizer treatments
- Port access
- IM or SC therapeutic medication with documented reassessment of its effect
  (tied to the drug, for example a pain score after an analgesic; routine
  vital signs or a feeding trial afterward do not count; not an immunization
  or local anesthetic)
- IV or IO medication or fluids with documented reassessment of its effect
  and two or more repeat vital-sign sets after it, where (a) the drug is an
  IV opioid, benzodiazepine or other sedative, antihypertensive or vasoactive
  agent, or antiarrhythmic, or (b) an abnormal vital sign was documented
  before it (rule 5). A policy requiring vital signs after every IV
  medication does not meet (a) [D: the drug classes are this grid's choice]
- Nasogastric or gastrostomy tube placement or replacement, or two or more
  documented staff reassessments of such a tube
- Preparation or assist for eye irrigation with a lens, or a pelvic exam
  without forensic collection (a documented staff chaperone counts as the
  assist; clinician ruling, 2026-11-10)
- Sexual assault exam without specimen collection
- Psychotic patient with documented environmental safety precautions and
  observation checks [D: BCBS lists the patient state]
- EKG
- Continuous cardiac monitoring (order, indication) with documented start and
  end times at least 60 minutes apart within the ED portion [D: duration is
  a hospital choice]
- Serial vital signs (indication): five or more complete sets, no more than
  30 minutes between consecutive sets, at least 120 minutes from first to
  last, within the ED portion [D]

## Level 5 — 99285
- Two or more advanced imaging studies (rule 4, Imaging), combined with
  either (a) two or more other unique tests, or (b) either Level 4
  medication item (IM or SC with reassessment, or IV or IO with reassessment
  and repeat vital signs). Other unique tests: each distinct CPT-coded test or
  study beyond the two advanced studies is one (a lab panel, a separately
  coded lab test, an EKG, a plain film, a third advanced study). Bedside
  point-of-care tests do not count; port access, an IV start and a Level 3
  injection are not medication items [D]
- Oxygen by non-rebreather, high-flow nasal cannula, or non-invasive
  ventilation, with documented hypoxia or respiratory distress, not meeting
  critical care [D: BCBS lists non-invasive ventilation as critical care]
- Three or more nebulizer treatments
- Moderate (procedural) sedation monitoring by ED staff before, during and
  after, meaning only this (no separate pre-dose staff entry is needed): a
  staff member other than the proceduralist monitors the patient,
  with continuous physiologic monitoring from the sedating dose to a
  documented return to baseline; an unattributed nursing-record entry counts
  as staff [D]
- Gastric lavage
- Temperature instability: documented core temperature below 95.0 °F or at
  or above 104.0 °F treated with an active warming or cooling device
  (forced-air warmer, cooling blanket, ice packs, cooled or warmed IV fluids;
  not warmed blankets for comfort or an antipyretic alone) [D: BCBS sets no
  thresholds; these are the clinical definitions of hypothermia and
  heat-stroke-range temperature, the clinician's choice, 2026-11-10]
- Specialized resources initiated by ED staff: a report of suspected abuse,
  neglect or assault to a protective agency with documented staff contact, or
  a crisis-team or social-work consult for a safety plan or for a new
  placement because the patient cannot safely go home (transport, insurance
  and pharmacy help, reportable-disease, animal-bite and administrative
  reports, and arrival by police do not count) [D]
- Sexual assault exam with forensic specimen collection by ED staff
- Coordination by ED staff of inpatient or ICU admission, or of transfer to a
  higher level of care (inpatient, ICU, specialty or psychiatric facility);
  observation placement is not a higher level of care; timing under rule 1.
  The record must attribute the bed or ICU request, the call to the
  accepting unit, or the transfer arrangement to ED staff; an accepting
  physician's acceptance alone, an unattributed admission disposition, or
  the ED physician's consult does not count [D]
- Physical restraints, or chemical restraint given under the restraint policy
  with restraint monitoring [D]
- 1:1 sitter for 60 or more continuous documented minutes (order;
  indication: suicide, elopement or violence risk) [D]
- Serial cardiac studies (order, indication; rule 5): two or more repeat EKGs
  or cardiac enzymes, in any combination, resulted during the ED portion. A
  chest-pain or triage order set applied by complaint alone is not an
  indication. Repeats for artifact, hemolysis or a redrawn specimen do not
  count [D: BCBS sets no count; two or more is the clinician's choice,
  2026-11-10, following sources that place a single repeat at Level 4]

## Separately paid; do not set the level (rule 4)
IV pushes and infusions; transfusion; lumbar puncture; paracentesis;
intubation; cardioversion; CPR; abscess incision and drainage; joint
aspiration or injection; intermediate or complex repair; closed fracture
treatment; bladder irrigation. Code them on their own lines.

## Not placed (no level until the hospital places them)
Interpreter use; isolation precautions; delivery of a newborn and fetal
monitoring; burn care by degree; continuous pulse oximetry.

## Departures from BCBS Texas [D]
- **Separately paid procedures and their staff assistance removed** (BCBS
  places their preparation or assistance at Levels 2–5): this grid takes the
  CMS option (72 FR 66806) not to use separately paid services as a proxy for
  hospital resources, except imaging studies (see the imaging departure), so
  their resources are not counted twice (72 FR 66800).
- **IV start, IM/SC injection and the IV/IO reassessment item:** the IV start
  and IM/SC injection are packaged, so they set Level 3 on their own; the IV
  administration is separately paid, so Level 4 needs the staff reassessment
  and vital signs that the administration code does not pay for.
- **Point-of-care tests at Level 2 and the narrowed laboratory item:** BCBS
  puts lab tests (CPT 80048–87999) at Level 3; bedside tests use far less
  staff and specimen handling than accessioned laboratory work.
- **Discharge prescription teaching at Level 2** (BCBS: discharge with a
  prescription at Level 3), so the clinician's prescription does not set the
  facility level (principle 2).
- **Simple face mask at Level 3** (BCBS: Level 5), so one device sits at one
  level; Level 5 oxygen requires a high-intensity device and documented
  hypoxia or distress. Non-invasive ventilation not meeting critical care is
  placed at Level 5.
- **Ear irrigation, splint and crutch teaching at Level 2; cardiac monitoring
  and serial vital signs at Level 4:** brief nursing tasks and monitoring
  BCBS does not list, each with an indication requirement.
- **Direct admission via the ED removed** (BCBS: Level 3): a direct
  admission is not an ED visit (rule 10).
- **Laboratory specimen collection** (BCBS: Level 2) counts only through the
  Level 3 laboratory item.
- **Items narrowed by added conditions** (order, indication, staff
  documentation, duration or count): every item marked [D] above without its
  own departure line here.
- **Imaging counted by the study as proxy** (BCBS: "preparation for" the
  study): an ordered-and-performed study is taken as the evidence of the
  preparation (rule 4); 72 FR 66806 permits the proxy.
- **Serial cardiac studies limited to the ED portion and a clinical serial
  protocol** (BCBS also counts studies done in observation).

## Sources
CMS CY 2008 OPPS rule, 72 FR 66800, 66805–66807; CY 2026 OPPS rule, 90 FR
53460; Claims Processing Manual ch. 4 §§10.4, 160, 160.1; Medicare Benefit
Policy Manual ch. 6 §20.5.2; I/OCE specification v17.1; October 2026 OPPS
Addendum B; BCBS Texas CPCP003 (2023); Kaiser Permanente Washington ED
facility policy; CorroHealth ED Charge Process (Dec 2023); AAPC reproduction of
CMS FAQ 2297.
