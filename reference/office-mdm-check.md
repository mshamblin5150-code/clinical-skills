# Office E/M Level — MDM Check Sheet

**Version:** v0.6.6, tested 2026-11-10. Adopted by
[ADR 0444](../docs/adr/0444-the-repository-carries-a-tested-ed-facility-grid-and-office-mdm-check-sheet.md),
which records the clinician's rulings, the panel results and the limits.

Professional level for an independent office (no facility charge), for
service dates covered by the CPT 2026 edition (ADR 0251 ruling 7). The CPT
text this sheet applies lives only in the repository's committed CPT
Professional 2026 sheet, [cpt-em-mdm-2026.md](cpt-em-mdm-2026.md); this sheet
cites its entries by id (for example `table-moderate`) and does not copy them.
**Order of authority:** the house and repository rules below interpret the CPT
text; they may require more documentation or a lower level, but never support a
level the CPT text does not. Payer policy governs where it differs.

**Scope.** Use this sheet only for office or other outpatient E/M visits
(99202–99215). It does not apply to preventive medicine visits (a visit for
a patient without a presenting illness or complaint whose work is
screening, counseling or risk-factor reduction, for example a preconception
visit), Medicare
annual wellness visits (G0438/G0439), postoperative visits inside a global
surgical period (99024), or antepartum visits inside global obstetric care;
do not level those from this sheet. Whether a separate problem-oriented
office E/M may also be reported on such a day is outside this sheet's
sources; follow CPT and payer policy, and level any such E/M from this sheet
using only the problem-oriented work.

## Codes by MDM level (two of three elements met or exceeded)

| MDM level | New patient | Established patient |
|---|---|---|
| Straightforward | 99202 | 99212 |
| Low | 99203 | 99213 |
| Moderate | 99204 | 99214 |
| High | 99205 | 99215 |

- **99211:** no MDM level applies (entry mdm-selection); see definition-minimal below.
- **Total time:** not available on this sheet. Its thresholds are not in the
  committed sheet; read them live in the rendered CPT book each time, and
  leave the E/M line pending without that read (ADR 0251 ruling 3, ADR 0308
  ruling 7).
- New or established status comes from a verified source, never inferred.

## House rules (clinician rulings of 2026-11-10, checked against published guidance)
1. **Refills.** A renewal, or a decision to continue a prescription drug,
   counts as prescription drug management when the clinician's shorthand or
   recorded answer shows he addressed the problem the drug treats (ADR 0308
   ruling 1). Reviewing a medication list alone does not. A continuation only
   the note pass wrote is a proposed drug under ADR 0308 ruling 3: it counts
   only on a problem he addressed, and when the level rests on it the E/M
   line carries `[SOURCE: filled - risk: <drugs>]`. A prescription drug is
   one not sold without a prescription at the dose continued; a continued
   over-the-counter agent follows house rule 3. (AMA 2023 E/M webinar, an inpatient
   question: "Renewing or changing medication in the medication list through
   an extension or new prescription would represent medication management of
   the prescribed medications for that patient." The extension to a decision
   to continue without a refill is AAFP FPM Jan/Feb 2021 p. 9 alone.)
2. **Decision regarding hospitalization.** Counts, whether hospitalization is
   selected or considered and not selected, only when the clinician's
   shorthand or recorded answer records both the decision and that the
   condition approaches the threshold for hospital-level care; boilerplate
   shared-decision text, or a decision the note pass wrote, does not count
   (AMA 2023 E/M guidelines: "a decision about hospitalization includes
   consideration of alternative levels of care"). No particular phrase is
   required: his offer of admission for a named hospital-level treatment
   (for example IV diuresis), tied to this visit's findings, meets it.
   Sending a patient from the office to the ED counts on the same terms only
   when his record names the suspected condition as the reason (for example
   "?ACS, to ED"); a referral whose only recorded reason is a test the office
   lacks ("to ED for trops") or convenience does not. Where his record meets
   these conditions, the decision counts. Only where it is unclear whether it
   meets them and counting would raise the level, select the lower level and
   ask the ADR 0308 ruling-2 question. The ED-referral part is a house interpretation; no AMA, CMS or
   AAFP text addresses it.
3. **Over-the-counter agents (ADR 0442, which superseded ADR 0292 ruling 1).**
   A directed OTC agent reaches moderate risk only when the clinician's
   shorthand or recorded answer states why it is higher risk for this patient
   (for example an NSAID with kidney disease or anticoagulation); otherwise it
   supports at most low risk, and a prescription written for it does not
   change that. When the moderate reading would raise the level, ask the
   ADR 0442 ruling-2 question. General advice naming an option counts toward
   nothing unless his record gives both a dose and directions for use ("as
   needed" alone is not a dose). An OTC agent the note pass proposed,
   rather than one his shorthand directs, counts only where it treats a
   problem he addressed (ADR 0308 rulings 1 and 3); this rule grades its risk,
   moderate needs his own stated reason, and when the level rests on it the
   E/M line carries `[SOURCE: filled - risk: <agents>]`. (AAFP FPM 2021; AMA
   2022 E/M webinar FAQ.)

## Counting notes (read from the CPT definitions cited below)
- A chronic illness counts as not stable only where the clinician's shorthand
  or recorded answer states it is not at his treatment goal for this patient,
  including "near goal" (definition-stable-chronic), or records it as acutely
  worsening, poorly controlled or progressing (definition-chronic-exacerbation).
  Count it as a chronic
  illness with exacerbation, progression or side effects of treatment, even
  when treatment is unchanged. A status the note pass wrote, such as a filled
  lab value or a pass-written "not at goal," leaves it stable; where the
  not-stable reading would raise the level, ask the ADR 0308 ruling-2
  question. A side effect of treatment is part of the chronic illness whose
  treatment causes it, not a separate problem
  (definition-chronic-exacerbation). It makes that illness not stable only where his
  record shows attention to the side effect (a treatment change, added
  supportive care, or testing for it); a side effect he records as mild or
  tolerated, with treatment unchanged, leaves it stable.
- Minimal versus low risk (proposed; the 2021 CPT table gives no examples, so
  this uses the CMS 1997 Table of Risk as an anchor): lifestyle advice, rest
  or patient self-monitoring with no drug, therapy or test ordered supports
  minimal risk; a home exercise program he directs, physical or occupational
  therapy, an OTC drug, or continuing or renewing his order for a prescribed
  device or its supplies (for example CPAP; clinician ruling, 2026-11-10)
  supports low risk (an OTC drug higher only under house rule 3).
- A recurring order (for example monthly prothrombin times) counts as one
  test ordered and reviewed at the encounter that orders it; each new result
  may be counted in the encounter in which it is analyzed
  (definition-data-analyzed).
- In-office imaging or other in-office tests (not the ECG, which ADR 0443
  governs): when this clinician bills the global code or the professional
  component (-26), the test counts for nothing toward data
  (definition-data-analyzed). When the practice bills only the technical
  component or nothing, the order counts as one test ordered; his own read of
  a test his office performed adds no independent interpretation, for the
  reason ADR 0443 records (the CPT text does not settle it).

## Documentation checks (proposed from the CPT definitions; not yet ruled)
Apply each check. Where applying it lowers the level, select the lower level
and ask the ADR 0308 ruling-2 question naming both levels; where questions
are delegated, the lower level stands. No check may support a higher level
than the CPT text alone.
- An independent historian counts only when the note names who gave the
  history and why: the patient's limitation, or the need for confirmation.
- Social determinants count only when the note names the determinant and the
  diagnostic or treatment option it limited.
- A normally self-limited illness following its expected course (for example
  a viral upper respiratory infection) is a self-limited or minor problem. It
  becomes acute, uncomplicated only when the clinician's shorthand or
  recorded answer shows it is not resolving on that course, or that he
  considered treatment for it (definition-acute-uncomplicated). A Plan line
  or general advice the note pass wrote is not his consideration.
- A same-day procedure or other service (any service with its own CPT code,
  for example 96372, a laceration repair or a lesion destruction): its usual
  pre- and post-service work does not count toward the E/M. Append modifier
  25 only when the E/M is significant and separately identifiable, above and
  beyond that service; a different diagnosis is not required. When every
  problem addressed is the subject of a same-day procedure and the record
  documents no work beyond evaluating the problem the procedure treats, the
  decision to perform it, consent and the procedure's usual aftercare
  instructions, report no E/M. For Medicare, a procedure with a 0- or 10-day
  global period is a minor surgical procedure: "The decision to perform a
  minor surgical procedure is included in the payment for the minor surgical
  procedure," and "a significant and separately identifiable E&M service
  unrelated to the decision to perform the minor surgical procedure is
  separately reportable with modifier 25" (NCCI Policy Manual for Medicare
  2026, ch. 11; ch. 1). Evaluating and managing another problem, or a
  treatment plan for the problem beyond the procedure's usual aftercare (for
  example a directed home exercise program or a new drug), is such separate
  work. CPT says modifier 25 is not used for an E/M that resulted in a
  decision to perform surgery; see modifier 57 (committed entry
  modifier-25); for Medicare that applies to a procedure with a 90-day
  global period. Other payers follow their own global-surgery policy.
- "Over-the-counter agent" means one sold without a prescription at the
  strength and dose directed (for example naproxen 500 mg tablets are
  prescription-only; ibuprofen 400 mg as two 200 mg tablets is not).

## Repository rules (this repository's ADRs)
- **ADR 0308 ruling 1.** A condition counts as addressed only where the
  clinician's shorthand, or his recorded answer, shows he evaluated or treated
  it at this visit; a Plan line the note pass proposed does not make it
  addressed.
- **ADR 0308 ruling 2.** When leaving a condition out lowers the level, select
  the lower level and ask him one pre-approval question naming both levels.
  No question when the condition would not change the level; where questions
  are delegated, the lower level stands.
- **ADR 0308 ruling 3.** A prescription drug the pass proposes counts as
  prescription drug management only where it treats a problem he addressed;
  when the level rests on it, mark the E/M line
  `[SOURCE: filled - risk: <drugs>]`. House rule 1 applies it to
  continuations; for an OTC agent, house rule 3 grades the risk once this
  ruling's addressed-problem condition is met.
- **ADR 0308 ruling 5.** Threat to life or bodily function counts only where
  his own evaluation and treatment (what his shorthand orders, gives or
  decides about disposition) are consistent with that severity. Where they
  are, count it without a question. Only where they are not and the
  threat-to-life reading would raise the level, select the lower level and
  ask the ruling-2 question naming both levels.
- **ADR 0443 ruling 1** (superseding ADR 0308 ruling 6's office limb). When
  his shorthand records his own read of an ECG traced at this office, bill
  93000 and count the ECG toward nothing in the data element. His read must
  be a written interpretation and report, not a bare "normal"; where the
  shorthand records only "normal" or no findings, ask for his findings before
  approval, and until he answers bill 93005 and count the ECG as one test
  ordered. A tracing from elsewhere: bill no ECG code, and his read counts as
  a test ordered and an independent interpretation.
- **ADR 0442 rulings 1 and 2.** See house rule 3.
- **ADR 0292 ruling 7.** A test the note pass proposed and wrote as a Plan
  order counts toward data; when the level rests on it, mark the E/M line
  `[SOURCE: filled - data: <tests>]`. A recommendation left for the preceptor
  never counts.

## Counting notes (from AMA 2023 E/M guidelines; not CPT 2026 sheet text)
- A test ordered at the visit and its result reviewed is one element:
  "Ordering a test is included in the category of test result(s) and the
  review of the test result is part of the encounter and not a subsequent
  encounter." Only an independent interpretation may add a second credit. A
  test counted when ordered at an earlier encounter is not counted again when
  its result is reviewed later, except a recurring order's new results (CPT
  counting note above).
- An interpreter is never an independent historian.

## Worksheet
Problems ______ · Data ______ · Risk ______ → two of three ______ → code ______
New/established (source) ______ · Filled marks ______ · House rule used ______

## The CPT entries this sheet applies

Read each entry in [cpt-em-mdm-2026.md](cpt-em-mdm-2026.md) by its id.

- **The MDM table:** `mdm-two-of-three`, `table-footnote`, `table-straightforward`, `table-low`, `table-moderate`, `table-high`.
- **Problems:** `definition-problem`, `definition-problem-addressed`, `problem-counting-guidance`, `condition-management-risk`, `definition-minimal`, `definition-self-limited`, `definition-stable-chronic`, `definition-acute-uncomplicated`, `definition-stable-acute`, `definition-acute-uncomplicated-hospital`, `definition-chronic-exacerbation`, `definition-undiagnosed-new`, `definition-acute-systemic`, `definition-acute-complicated-injury`, `definition-severe-exacerbation`, `definition-threat-life-function`.
- **Data:** `definition-data-analyzed`, `definition-data-test`, `definition-data-unique`, `definition-combination-data`, `definition-external`, `definition-external-clinician`, `definition-independent-historian`, `definition-independent-interpretation`, `definition-discussion`, `definition-appropriate-source`.
- **Risk:** `definition-risk`, `definition-morbidity`, `definition-social-determinants`, `definition-surgery-minor-major`, `definition-surgery-elective-emergency`, `definition-surgery-risk-factors`, `definition-intensive-monitoring`, `definition-parenteral-controlled`.

## Sources
reference/cpt-em-mdm-2026.md (CPT Professional 2026, two-reader agreement
2026-09-16); docs/adr/0292, 0308, 0251, 0442 and 0443 in this repository; AMA 2023 E/M
descriptors and guidelines; AMA 2023 E/M webinar Q&A; AMA 2022 E/M webinar
FAQ; AAFP Family Practice Management, Jan/Feb 2021, p. 8-9.
