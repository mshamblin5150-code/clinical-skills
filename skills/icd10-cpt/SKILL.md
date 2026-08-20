---
name: icd10-cpt
description: Propose ICD-10-CM diagnosis codes and CPT procedure codes from a documented encounter, each anchored to the note text supporting it. Use when the user asks for codes, needs to code an encounter, or mentions ICD-10, CPT, or E/M level.
---

Codes are **proposed**, never asserted. A code you supply is a suggestion the clinician verifies before it is entered anywhere — this skill's output is a worksheet, not a coding decision.

Three disciplines make that verification fast:

- **Anchor** — every code quotes the note text that documents it. A code with no anchor is not a code, it is a guess about the patient.
- **Descriptor** — every code carries its official descriptor next to its number. When the number and the descriptor disagree, the clinician sees it instantly. This is the defense against a fluent, plausible, wrong code number, and it is the reason the descriptor is never omitted to save space.
- **Source** — every code says whether its anchor was **recorded** or **filled**. A note carries filled content by design, and filled content reads exactly like recorded content, so a worksheet that does not say which is which has destroyed the distinction rather than merely omitted it. A code resting on filled content is still proposed. It is proposed **marked**.

The third one is invisible and is the reason for *The input* below.

**Source used to refuse rather than mark, and the change is [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46).** [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10)'s rule sent a filled-anchored code to step 4 uncoded. That left this skill and [clinical-note](../clinical-note/SKILL.md) applying **different rules to the same value** — the note writing `E66.3` into a submitted diagnosis field while this worksheet refused it — and the clinician holding two documents that disagreed with nothing saying which was right. Two skills disagreeing about one number is a defect whichever of them is correct, so the disagreement was removed rather than adjudicated: both code it, and this skill marks it.

## The input

**The input to this skill is the whole `clinical-note` output — the note body and the tier block beneath it — not the note body alone.**

That is a hard requirement, not a convenience. Every line of a finished note is **given**, **derived**, or **filled** ([clinical-note](../clinical-note/SKILL.md)), and the finished note is written so those three read identically. `BMI 36.4` in the Objective is the same eleven characters whether it was measured or generated. The tier block is the only place the difference is recorded, so a note arriving without one has had its source information stripped.

**Where the tier block is missing, say so and treat every vital, body measurement and BMI in the note as filled.** Not as a punishment — as the accurate reading. Measured 2026-08-11 with `tools/corpus_census.py` across 551 encounters, 46% carry no vital at all and only 41% carry a height — so **59% have no height to write down**. An unmarked measurement in a note from this pipeline is more likely to have been filled than recorded. Being wrong in that direction costs a code that had to be earned by measuring; being wrong in the other direction puts a number nobody measured onto a claim.

## The code set

This repo ships the ICD-10-CM code set at `reference/icd10cm-2026.sqlite`, so a code can be **looked up rather than recalled**:

```bash
python tools/icd10_lookup.py Z68.36 E66.811
```

```bash
python tools/icd10_lookup.py --find "body mass index" --billable
```

It answers four things: does the code exist, what is its official descriptor, is it billable, and what notes govern it. Use it for every code you propose. Three things it changes:

- **The descriptor stops being recalled.** Paste the official one.
- **`CONFIDENCE` means something narrower.** `verify this number` is for a code you did not look up. A code you did look up is verified against a named release and says so.
- **Billability is checked, and it is the quiet one.** `Z68.2` is a real code with a real descriptor that cannot be submitted — it is a header, and only its children are billable. A proposal carrying a header code reads as correct right up to the rejection.

**What the lookup cannot do.** There is no alphabetic index in the database, so it verifies a candidate rather than finding one from a diagnosis phrase. `--find` is a substring match over descriptors, which is weaker: a miss is not evidence that no code exists. And nothing in it encodes the official coding guidelines. It answers *does this code exist and what governs it*, never *is this the right code*.

### Pediatric BMI-for-age

This repo also ships CDC's 2022 Extended BMI-for-Age table at `reference/cdc-bmi-for-age-2022.csv`. Ages 2–19 take `Z68.5-`, whose bands are percentiles rather than adult BMI intervals, so run the committed calculator for every pediatric BMI:

```bash
python tools/cdc_percentile.py male 198 21.6
python tools/cdc_percentile.py female 16 21.6 --age-years
```

It returns the extended percentile, percent of the 95th percentile, the exact `Z68.5-` band and the corresponding `E66.-` code where the child is overweight or has class 1, 2 or 3 obesity. The `E66` pairing is not inferred from adult cutoffs: CDC pairs `Z68.53` with `E66.3`, `Z68.54` with `E66.811`, `Z68.55` with `E66.812` and `Z68.56` with `E66.813`. `Z68.51` and `Z68.52` produce no BMI-derived `E66` code.

**Use the age the encounter can support.** A date of birth and encounter date produce completed months. Where the shorthand gives only whole years, use `--age-years`: the tool fills the midpoint month deterministically and says so. That filled month joins height and weight on `SOURCE: filled` and in step 4's `CODED, ANCHOR WAS FILLED` block; a guessed month never becomes a documented birth date. The clinician submitting the encounter confirms it during the ordinary filled-content review; nobody is an implementation-time approval gate.

The confidence line names both checks: `verified against ICD-10-CM FY2026 and CDC 2022 Extended BMI-for-Age`. A filled height, weight or age month still carries its provenance disclosure, but the band itself is computed rather than recalled.

## Steps

### 1. Read the FILLED and DERIVED lines first

Before reading the note body, list every value the tier block gives as filled — every filled vital, every filled body measurement.

**Then read `DERIVED` as well, because that is where the BMI lives.** A BMI computed from a filled height is *derived* under [clinical-note](../clinical-note/SKILL.md)'s tiers — the arithmetic has one right answer — so it is written on the `DERIVED` line, not a `FILLED` one. A step that read only the FILLED lines would miss the single value this whole rule was written for. **A derived value is treated as filled here whenever any input to it was filled**, and its FILLED line names those inputs.

That combined list is the set of numbers whose codes carry a **`SOURCE: filled`** line in step 3 and are listed again in step 4. Hold it while doing step 2.

Completion: every entry under `DERIVED`, `FILLED·asserted` and `FILLED·proposed` has been read; every filled vital and measurement is written down with its value; and every derived value has been checked for a filled input.

### 2. Extract codable elements

Read the note and list what is documented — not what is implied. For each, capture the exact supporting text.

- **Diagnoses** — from the Assessment. A symptom is codable as a symptom; it does not become a disease.
- **Procedures** — from the Plan and Objective: laceration repair, splinting, incision and drainage, ECG interpretation, foreign body removal, and so on.

**Every occurrence of spirometry in the worksheet identifies which intervention it means.**
`Office spirometry`, `diagnostic spirometry`, `spirometry with bronchodilator response` and
`incentive spirometry` are qualified; the bare term is not. A qualifier on the source note's Plan
does not carry into an Assessment anchor, procedure list or CPT entry, because each worksheet line
is designed to survive being copied by itself.

**A bare source occurrence cannot be copied into an affected worksheet entry.** If that source text
supports an extracted procedure, ask the clinician for a qualified restatement before writing that
entry, treat the response as added source text and quote it verbatim. Continue extracting unrelated
elements; the ambiguity in one procedure does not block the rest of the worksheet. Do not infer the
answer from whether the procedure was performed or deferred, and do not insert an editorial
qualifier inside an `ANCHOR`: anchors remain verbatim. This is the same human-read,
spirometry-specific convention as [clinical-note](../clinical-note/SKILL.md), not a general
ambiguous-procedure table. Ruled by the clinician 2026-08-20, issue
[#166](https://github.com/mshamblin5150-code/clinical-skills/issues/166).

Then mark every element whose only support is a value from step 1. Those are coded like any other — they carry their mark into step 3 and are listed **again** in step 4.

Completion: every Assessment problem and every Plan procedure appears in the list, marked codable or filled-anchored.

### 3. Propose codes

For each codable element:

```
ICD-10  <code>  <official descriptor>
  ANCHOR: "<verbatim note text>"
  SOURCE: filled — <which inputs were filled>; confirm before submitting
  SPECIFICITY: <complete — why nothing further applies | needs: laterality / episode / site / severity / a billable child>
  CONFIDENCE: <verified against ICD-10-CM FY2026 | verify this number>
```

**`SOURCE` appears only where the anchor was filled**, so an ordinary code keeps its five parts and a filled-anchored one carries six. It is a line on the code itself and not only a step-4 heading, for the reason step 4 gives about `NOT CODED`: **a block heading does not survive being copied one line at a time**, and the proposed-code list is exactly the block a clinician scans for things to enter.

CPT entries take the same shape, plus the note text documenting anything the code's requirements hinge on — repair length, wound complexity, time.

Rules:

- Code to the specificity the documentation supports and no further. If the note says "wrist fracture" with no side, the laterality is `needs: laterality`, not a coin flip between left and right.
- **Every `SPECIFICITY` flag carries substance beyond its keyword — a bare `complete` and a bare `needs:` both fail.** A code whose descriptor says `unspecified` normally reads `needs:`, but may read `complete` when its reason explains why nothing the bedside can supply would move the code. Below.
- Say `verify this number` whenever you are working from recall rather than the code set. An honest flag costs the clinician ten seconds; a confident wrong code costs a rejected claim or a bad log entry.
- Never invent a documented finding to justify a code. If a code needs an element the note lacks, that goes in step 4.
- **A code whose only anchor is a filled value is proposed, and carries `SOURCE: filled`.** The rule and its reasoning are below.
- **A hedged diagnosis is coded, and the documented symptoms are coded with it** — with one limit, on the code rather than the hedge. Below.
- **Every differential entry carries a code, and none of those codes is for entry.** Below.

#### `complete` is a claim, and it carries its reason

**A flag reading `complete` says the encounter documented every axis the code has.** That is a finding about the code, and it takes a reason the way `needs:` already takes an axis.

```
SPECIFICITY: complete                                  <- not compliant
SPECIFICITY: complete — I10 has no further axis        <- compliant
SPECIFICITY: complete — laterality documented as left  <- compliant
```

**The reason is the evidence that the check happened, and a bare word cannot be.** Nobody writes *"`Z98.51` has no further axis"* without having looked at `Z98.51`'s axes. Anybody can write `complete` without having opened the code at all, and the two outputs are indistinguishable on the page. A pediatric `Z68.5-` now supplies the same evidence by naming the committed CDC table and calculator rather than merely asserting a percentile.

**The same holds on the other branch, and it is the same defect wearing the other keyword.**

```
SPECIFICITY: needs:        <- not compliant
SPECIFICITY: needs: site   <- compliant
```

A bare `needs:` names a gap and then does not say what the gap is, which leaves a step-4 `UNDOCUMENTED` entry that cannot be written — so the clinician is told something is missing and not told what to document at the bedside. **The rule is therefore one rule, not two**: a flag carries substance beyond its keyword, whichever keyword it took.

**A code whose own official descriptor says `unspecified` demands an explanation, not an automatic `needs:`.** Usually the descriptor is the code set stating that an axis exists and that this code declines to name it, so `complete` would contradict the line directly above it:

```
ICD-10  M19.90  Unspecified osteoarthritis, unspecified site
  SPECIFICITY: complete — no further axis    <- contradicts its own descriptor, twice
  SPECIFICITY: needs: site                   <- and this earns a step-4 bedside line
```

**But the word is not proof that the encounter left an axis open.** `R00.1 Bradycardia, unspecified` is the only bradycardia code in its sibling set, so this is compliant:

```
ICD-10  R00.1  Bradycardia, unspecified
  SPECIFICITY: complete — R00.1 is the only bradycardia code; nothing documented at the bedside would move it
```

**A substantive reason discharges the specificity flag rule.** `tools/specificity_scan.py` enforces that the reason exists and counts every `complete` on `unspecified` or `not specified` as an advisory review surface; it does not fail that shape merely because of the descriptor. Deciding whether the reason names a real exhausted axis or disguises a documentation gap takes a reader.

**Measured rather than assumed, and re-derivable rather than quoted.** [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) established the rule by checking committed diagnosis lists against `reference/icd10cm-2026.sqlite`. The audit, counts and record identity remain in the withheld fixture files, where `tools/test_specificity_scan.py` pins them against the committed notes.

**Many descriptors name a detail the bedside could supply** — a lipid panel for `E78.5`, a rapid strep for `J02.9`, the joint for `M19.90`, an orthostatic component for `R51.9`, the duration for `R05.9 Cough, unspecified`.

**The descriptor has known false positives.** For example, `R00.1 Bradycardia, unspecified` and `R19.7 Diarrhea, unspecified` have no sibling naming a more specific form of the same condition — `R00.1`'s neighbors are tachycardia and palpitations, `R19.7`'s are abdominal swelling and bowel sounds. The word is part of the condition's own name there, and **nothing at the bedside would move either code**. [#135](https://github.com/mshamblin5150-code/clinical-skills/issues/135) therefore made the descriptor shape advisory and let a substantive reason carry the distinction. These code-set examples are synthetic rather than extracted from a fixture audit.

**Two more distinctions matter.** A code that is already a billable leaf does not need a child merely because its descriptor is broad; verify the hierarchy rather than assuming one exists. And an `Other ...` residual is **not** an `unspecified` one: `R06.89 Other abnormalities of breathing` says the finding does not fit a named code, not that the documentation is thin. Those read `complete` with a reason like anything else. Exact audit counts remain in the withheld fixture record.

**What the command cannot reach is whether a reason is a real check or a stock phrase.** `L85.3` has five siblings and `Z98.51` has one, and ruling that those are different conditions rather than axes of one thing takes a reader — so `complete — L85.3 has no further axis` can be true, and no string test confirms it. A withheld counted row carries that residue rather than pretending to enforce it.

**What the worksheet's own pass cannot settle is whether its reason is true.** A reason can be specific, checkable, and false while every descriptor is official and every string test passes. The worksheet that wrote the reason is not its verifier; preserved run evidence and its verdict stay withheld under [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147). [#154](https://github.com/mshamblin5150-code/clinical-skills/issues/154).

#### A fresh reader checks every ICD-10 specificity reason

After every worksheet in a run is written, give a **fresh reader in a separate context** the for-entry ICD-10 code numbers and nothing else. The fresh reader **must not see the worksheet**, its descriptor, its anchor, or its `SPECIFICITY` line. Parallelism is only a speed property; a serial harness may run the reader later, provided its context contains the brief and not the worksheet.

The reader is briefed to **try to break each reason**, not to confirm it. For each subject code, open `reference/icd10cm-2026.sqlite`; inspect whatever parents, children, siblings, and inherited tabular notes bear on specificity; and record:

```json
{
  "read_on": "YYYY-MM-DD",
  "codes": [{
    "code": "I10",
    "family": [{
      "code": "I10",
      "descriptor": "Essential (primary) hypertension",
      "billable": true,
      "notes": [{
      "code": "I10",
      "kind": "excludes1",
      "text": "hypertensive disease complicating pregnancy, childbirth and the puerperium (O10-O11, O13-O16)"
    }, {
      "code": "I10",
      "kind": "excludes2",
      "text": "essential (primary) hypertension involving vessels of brain (I60-I69)"
      }, {
        "code": "I10",
        "kind": "excludes2",
        "text": "essential (primary) hypertension involving vessels of eye (H35.0-)"
      }]
    }],
    "about": "what the release shows about this code's specificity, in the fresh reader's own words"
  }]
}
```

`"family"` is every code whose normalized number begins with the subject's three-character category — `I10` for `I10`, all of `Z90...` for `Z90.49` — each with its exact descriptor, billability, and **complete inherited note set**. The scanner recomputes that set from SQLite, so an omitted sibling, invented sibling, or empty family refuses rather than reading as a completed lookup. `"about"` states what the whole category means for the subject's specificity without copying the worksheet's reason.

The committed scanner creates the answer-free brief and grades the record:

```bash
python tools/specificity_scan.py <run directory> --brief > scratch/specificity-brief.txt
python tools/specificity_scan.py <run directory> --second-read scratch/specificity-second-read.json
```

The brief contains diagnosis codes and is PHI; keep it in `scratch/` and do not paste it. The second command checks every category member, descriptor, billability value, and complete inherited-note set against `reference/icd10cm-2026.sqlite`. Exit 1 means a family/source fact or specificity flag failed. Exit 2 means the second read was absent, malformed, or did not cover every for-entry ICD-10 code. `--show` places the original reason beside the fresh reader's `"about"` prose for the final eye check; that output is PHI too.

Without the scanner, do the same walk by eye: list each distinct for-entry ICD-10 code without copying its reason; hand that list alone to the fresh reader; require every field above; compare every source field to `tools/icd10_lookup.py` and the committed database; then place the original reason beside `"about"`. The command saves that mechanical comparison; it does not replace the reader.

**`about` is never machine-graded.** It is free prose beside free prose, so judging whether the two agree is itself a reading. A source-field disagreement is a hard failure; a clean source comparison plus a human agreement is a **smoke test and never proof**. Two readers can misread the same code family the same way. This is separation as an instrument, not a claim that a second reason cannot also be wrong.

The brief excludes CPT and HCPCS entries because this repo ships no corresponding code set to bind their family walks against. Their specificity reasons keep the ordinary human verification posture; a clean ICD-10 second read says nothing about them.

#### A filled value is coded, and it is marked

**A code whose only anchor is a filled value is proposed like any other, carries `SOURCE: filled`, and is listed again in step 4.** The code is derived from the note's own stated value and looked up, not withheld and not recalled.

**Withholding it was the previous rule and it was wrong for a reason that has nothing to do with whether the code is earned.** [clinical-note](../clinical-note/SKILL.md) writes codes into the Medatrax `Preexisting diagnoses` and `Final diagnosis` fields, because those are fields and something goes in them. So a rule that refused those same codes here produced two documents, from one pipeline, disagreeing about one number — with nothing in either saying which was right. **The clinician cannot adjudicate that and should not be asked to.** Marking gives the same protection without the contradiction: the code is present, so the two agree, and the mark says what the note alone cannot.

**The mark is not a formality, and this is what it buys.** The note is written so given and filled content read identically — that is deliberate, and it is why the tier block exists at all. Once a code leaves this worksheet, nothing downstream can recover whether anybody measured the patient. `SOURCE: filled` is the last point in the pipeline where that fact is still knowable.

The rule is general. It is not a rule about `Z68`, which is only its sharpest instance.

**Why the general form.** These four all code directly off a single number with no clinical judgment in between, and every one of them is a value `clinical-note` is *required* to generate when the shorthand omits it:

```
Z68.-    Body mass index, banded to 1.0 BMI units through the 30s
E66.-    Overweight and obesity
R03.0    Elevated blood-pressure reading, without diagnosis of hypertension
R06.82   Tachypnea, not elsewhere classified
```

An enumerated list would be a snapshot of what was thought of once. The test is structural: *does this code rest on a number the encounter recorded?*

**Two of those four say it themselves, in CMS's words.** `E66` carries the instruction

> code to identify body mass index (BMI), if known

and `R03.0` carries

> This category is to be used to record an episode of elevated blood pressure

**`if known`** and **`an episode`** are the tabular's own language. A filled BMI is not known — it is the value the patient most plausibly had. A filled blood pressure records no episode; read `R03.0`'s descriptor and the noun is *reading*, which is an act somebody performed.

**So the tabular's own conditions are unmet, and the code is still proposed.** That is not the tabular being overridden — it is the division of labor this skill opens with. Codes here are **proposed, never asserted**; the worksheet is a document the clinician verifies, not a coding decision. `SOURCE: filled` is how an unmet condition reaches the person who can settle it, and *"confirm before submitting"* is the instruction the tabular's `if known` becomes when the answer is *not yet*.

**`Z68` and `R06.82` carry no such instruction, and the rule still covers them.** Check for yourself — `Z68`'s only notes are its age boundaries and the growth-chart provenance, and `R06.82` carries an inclusion term and a list of exclusions. So the rule is not *derived* from the tabular; it is **confirmed** by it where the tabular happens to speak. What the rule actually rests on is the structural test in the paragraph above: does this code turn on a number the encounter recorded? Citing `E66` where it helps is not the same as claiming the code set decides every case, and a rule that needed a supporting note per family would fail on two of its own four examples.

**Why one filled value is enough to matter.** `Z68` is banded to 1.0 BMI units through the 30s, and a height is invented in well over half of this corpus. From a real encounter — 48 F, weight 212, no height recorded:

```
5'4"  ->  BMI 36.4  ->  Z68.36
5'5"  ->  BMI 35.3  ->  Z68.35
```

One invented inch, a different code. Nothing in the finished note distinguishes the two, and nothing downstream can tell that an inch was chosen rather than measured.

**And a filled inch may substantially reflect the generating skill's default rather than a measurement.** A `Z68` off a filled body therefore needs its `SOURCE: filled` mark; without it the derived band looks measured when it was not. The evidence and counts remain in the withheld fixture record. That is [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67) rather than this skill's defect to fix — but it is why the mark is not decoration.

**The band code and the diagnosis code are not equally exposed to that, and the difference is checkable.** At a filled weight of 185 lb, *every* height from 5'6" to 6'0" lands in the overweight band, so `E66.3` holds across the whole plausible range and the invented inch is not what produced it. Those same seven heights produce **five different `Z68` codes**. A diagnosis code names a state that survives the invention; a band code encodes the invention to one decimal place. Both are proposed and both are marked — the mark simply matters more on one than the other, and a clinician confirming the pair should know which one the inch decided.

**Age matters here too, and the pediatric branch is computed separately.** `Z68` adult codes are for persons 20 years and older; ages 2–19 take `Z68.5-`, which is a **CDC growth-chart percentile**, not a BMI band. Run `tools/cdc_percentile.py` rather than applying adult cutoffs. A filled height, weight or midpoint age month still makes the proposal filled-anchored, and `SOURCE` names each filled input; the percentile and code band themselves are verified against the committed chart.

**What codes without a mark, and this is most of it.** The mark reaches the value, not the patient.

- A **documented** diagnosis of obesity, hypertension or asthma codes from the Assessment however the vitals got there, and codes **unmarked** where the source documented it. `E66.9` off a charted diagnosis is a given anchored to given text.

  **"Charted" means charted by the clinician, not written into the Assessment by the upstream skill.** The note arriving here is generated, so its Assessment can name a diagnosis resting on nothing but a filled measurement. That entry is the measurement wearing a diagnosis — it still codes, and it carries `SOURCE: filled` naming the measurement underneath. **Reading this bullet as license to code such an entry *unmarked* launders a filled height in two moves, and the output reads perfectly well.** The mark is the whole of the difference between the two bullets.
- A **given** vital codes unmarked. Only the filled ones carry `SOURCE`.
- A **derived** value whose inputs were all given is given for this purpose — a BMI computed from a recorded height and a recorded weight is a measurement, not an invention, and it codes unmarked.

**One limit is clinical rather than provenance, and it is not lifted by any of the above.** `I10` requires hypertension the clinician documented, because **no single reading diagnoses hypertension** — real or filled. That limit holds against a *given* 138/86 exactly as it holds against a filled one, so it is not a `SOURCE` question at all and marking does not reach it. What a filled pressure supports is `R03.0`, marked. What it never supports is `I10`. A withheld fixture row pins that diagnosis rule.

#### A hedged diagnosis is a given, and it is coded

`probable viral URI` is something the clinician wrote. [clinical-note](../clinical-note/SKILL.md) preserves the hedge on purpose — *"Never … soften a hedge — `prob viral` becomes `probable viral`, not `viral`"* — so it reaches this skill intact, and it reaches it as a **given**.

**So it is coded, and the documented symptoms are coded alongside it.** Both, not one instead of the other. A suspected diagnosis is usually the reason the encounter happened and the reason codes were asked for at all; a worksheet that refused it would be missing the thing it was opened for.

**Both rules now code, and the difference is which one carries a mark.** A filled BMI is a number *nobody recorded* — the note reads identically whether it was measured or generated — so its code carries `SOURCE: filled`. `probable viral URI` was recorded, hedge and all. The uncertainty there is **documented rather than manufactured**, so `J06.9` is anchored to something the encounter actually says and takes no `SOURCE` line. Uncertainty is not the same defect as invention, and the mark is reserved for the second.

**The limit is on the code, not on the hedge.** Where the code's own descriptor names a **confirmed organism or a confirmed disease** and the encounter established neither, that code is not proposed. Propose what the encounter does document, and send the specific code to step 4 naming what would earn it:

```
COVID-19 — documented household contact, congruent symptoms, no test obtained

  propose:  Z20.822  Contact with and (suspected) exposure to COVID-19
  not:      U07.1    COVID-19 — the descriptor asserts the disease, and nothing tested for it
```

**The test is the descriptor, read against the note.** `Acute upper respiratory infection, unspecified` says *unspecified* and asserts nothing the note lacks, so `probable viral URI` codes to `J06.9` and the hedge costs nothing. `COVID-19` names the organism, and a note saying nobody swabbed cannot support it. The limit is narrow by construction — it fires on organism-specific and disease-specific descriptors, not on every hedge.

**A pending test refuses only what its result would establish.** Run the same descriptor test in the other direction: ask what the missing result would add, then ask whether the proposed descriptor asserts that thing. A culture can establish bacteria in blood or name an organism, so an unresulted culture can gate `R78.81 Bacteremia` and an organism-specific code such as `A41.50 Gram-negative sepsis, unspecified`. It cannot by itself gate `A41.9 Sepsis, unspecified organism`, `J18.9 Pneumonia, unspecified organism`, `L03.-` cellulitis or `N39.0 Urinary tract infection, site not specified`; none of those descriptors names the organism the culture would supply. Where the encounter clinically establishes one of those diagnoses, propose its code and route only the organism-specific code aside.

**A pending test is not a finding.** If the code names nothing the unresulted test would establish, either the note's documented findings establish the diagnosis and it is coded, or documented findings reject it and those findings are named. *Culture pending*, *no culture drawn* and *no result yet* are not substitutes for that clinical reading. Sepsis may therefore be rejected on the documented bedside findings — for example, vitals meeting no SIRS criterion with no white count or organ dysfunction documented — but never merely because the culture that would name its organism is pending. This is the converse of the over-claiming limit above, not an instruction to code every suspected diagnosis.

**Imaging is different because its result may establish the disease itself.** A film does not merely name pneumonia's organism; an infiltrate can establish pneumonia. A pending film may therefore leave a disease-specific descriptor unsupported where the note documents only a suspicion. It still is not a negative finding: when the note already establishes the diagnosis clinically, the pending film does not erase it; when documented findings argue against it, name those findings rather than the absent result. A resulted negative film is a finding and may reject the disease. The same test governs both branches: what would this result establish, and does the descriptor assert it? Issue [#149](https://github.com/mshamblin5150-code/clinical-skills/issues/149).

**Submission coding for a claim is generally taught the other way, and this differs from it deliberately.** Outpatient claim coding is taught to code the signs and symptoms rather than a `probable`, `suspected` or `rule out` diagnosis. **That is recalled, and nothing in this repo verifies it** — the official guidelines are prose in a PDF, they are not shipped here, and `reference/icd10cm-2026.sqlite` holds the tabular alone. Say it as recall if it comes up; do not cite a section number this repo cannot check. The difference stands either way, because this worksheet feeds an academic clinical-hours record rather than a claim, and the differential codes below are documentation of reasoning rather than candidates for submission.

**Guideline sheets now ship and this is not one of the things they cover, which is a stronger statement than the one it replaces.** Two do — `reference/guidelines-uspstf.md` and `reference/thresholds/` — and neither reaches coding. The ICD-10-CM Official Guidelines for Coding and Reporting are a CMS and NCHS document, and **no CMS or NCHS coding document is among the nine societies in the corpus** those sheets are distilled from. So the absence is now checkable rather than taken: open `reference/guidelines-catalog.md` and there is nothing to find. The ruling is unchanged and the reason got better. [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85).

**`Z03.-` is not proposed here**: it carries `excludes1: signs or symptoms under study- code to signs or symptoms`, every encounter in this corpus arrives with a complaint, and coding the symptoms is what the rule above already does.

#### The differential is coded, and none of it is for entry

Both branches of [clinical-note](../clinical-note/SKILL.md) carry a differential and both put a code on every entry — [SOAP.md](../clinical-note/SOAP.md) and [HP.md](../clinical-note/HP.md). Those codes **document medical decision-making**; they are not candidates for entry anywhere. Step 5 says what they document.

They get their own section, and **three parts rather than five**:

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---
ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**`NOT FOR ENTRY` is on the code's own line, and the heading is not enough by itself.** That is step 4's reasoning applied to a second block, for the same reason: a block heading does not survive being copied one line at a time. A note runs its differential five to seven deep, so this is five to seven code numbers sitting above the ones the clinician is actually there to enter.

**Two of the five parts drop, and two do not.**

- **Anchor** is the differential entry itself, named rather than re-quoted. The entry is in the Assessment with its rationale attached, which is more than a quoted fragment would carry.
- **Specificity** drops. A differential is coded at the unspecified level on purpose, so `needs: laterality` on a diagnosis the note is arguing against is noise in a block that already runs long.
- **Descriptor and confidence stay.** They are the two defenses against a fluent, plausible, wrong code number, and a differential code is exactly as easy to invent as any other. Look each one up.

**Where they must not go.** `reference/medatrax-fields.md` names `ICD-10-CM` as an Add Visit Data category, and that category takes the **preexisting diagnoses and the final diagnoses only** — what the patient had. `reports/diagnosisstatistics.aspx` reports across a whole rotation, and loading it with five to seven entries per encounter, most of them diagnoses the note argues *against*, would make it describe a caseload nobody saw.

**The uncertainty rule above applies inside the differential too, and this is where it bites hardest.** The entries most worth coding are the ones the encounter could not establish — a suspected pneumonia, an untested influenza — and those are exactly the entries where an organism-specific descriptor would assert what the note denies. `Z20.822` over `U07.1` is that rule, on a differential line.

### 4. Report what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
<element the code set wants — laterality, wound length, time spent, episode of care,
 the axis an "unspecified" descriptor leaves open>
  affects: <which proposed code>

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
<code> — <the value, and which inputs were filled>
  needs: <the measurement that would settle it>

--- NOT CODED, NOTHING ESTABLISHED IT ---
<the suspected diagnosis, and what documents the suspicion>
  NOT CODED: <code and official descriptor>
  needs: <the result that would establish it>
  proposed instead: <the code the encounter does document>
```

This is the section with the most value in it. It tells the clinician what to document *at the bedside next time* so the encounter codes cleanly, which is worth more over a rotation than any single code proposal.

The three blocks are the same statement about different causes. `laterality not documented`, `height not measured` and `nobody swabbed` are all *this encounter did not record the thing the code needs*, and all three are fixed the same way — at the bedside, next time. **The second differs from the other two in outcome only**: its code was proposed rather than withheld. What it needs is the same as theirs — the measurement nobody took — and the difference is that a code is already sitting on the guess in the meantime. Write them so the clinician can act on them:

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
Z68.36 — BMI 36.4 derived from a filled height (5'4") and a given weight (212 lb)
  needs: a measured height. One inch moves this to Z68.35

--- NOT CODED, NOTHING ESTABLISHED IT ---
COVID-19, suspected from a documented household contact and a congruent presentation
  NOT CODED: U07.1  COVID-19
  needs: a positive test. The contact alone does not establish the disease
  proposed instead: Z20.822  Contact with and (suspected) exposure to COVID-19
```

**The third block is not the hedge rule refusing a diagnosis.** A hedged diagnosis is coded — that is settled above. What lands here is the narrower thing: a code whose **descriptor** asserts a confirmed organism or disease that the encounter never established. The diagnosis is still coded, by the code the encounter does support, and this block records what the specific one was waiting on.

**Its first line names the suspicion, and that is now visibly not what the note's own entry is called.** Nothing here changed — the `COVID-19, suspected from a documented household contact` line above has always named the suspicion, and this paragraph records a contrast rather than deciding one. What changed is on the other side: [clinical-note](../clinical-note/SKILL.md) ruled in #68 that a differential entry is named **for the code it carries**, so the entry now reads `Pain in right leg - M79.604` with the disease in the rationale beside it. **The two documents therefore name one refusal two ways, and a reader moving between them should know it is intended:**

```
--- NOT CODED, NOTHING ESTABLISHED IT ---
Contiguous osteomyelitis of the right tibia or fibula, suspected on a chronic wound with
overlying pain; tib/fib film ordered, no result
  NOT CODED: M86.9  Osteomyelitis, unspecified
  needs: a film that resulted, or a bone biopsy
  proposed instead: M79.604  Pain in right leg
```

**The reason the two differ is what each document is for.** A note is read by a grader and by whoever treats the patient next, so a label that names an unestablished disease is a claim sitting where a claim is not earned. **This worksheet is read by the clinician looking for what to chase**, and *"the film that would settle the osteomyelitis"* is the whole content of the entry — filing it under `Pain in right leg` would bury the one thing the block exists to surface. `proposed instead` is where the two documents meet, and it holds the note's label. Issue #68.

**What the two documents now agree on is the mark itself, and this skill's form is the one that won.** `NOT CODED: <code>  <descriptor>` has been step 4's since it was written. Until 2026-08-16 [clinical-note](../clinical-note/SKILL.md) wrote the code *first* — `M86.9 Osteomyelitis, unspecified NOT CODED, …` — so one pipeline rendered one mark two ways. [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) made the note adopt this one, because a mark welded to its code by a colon can be found without guessing which code it refers to and the other order cannot. **Nothing on this side changed**, which is worth stating plainly: a worksheet written before that date is still compliant, and the rule that changed is the note's.

**Every line that withholds a code carries `NOT CODED` inline, on the same line as the number** — the first and third blocks. The code has to be named, because the clinician who gets the swab back tomorrow needs to know what it would have earned, so the defense cannot be hiding it. It is that the number never appears without its refusal attached, and never in the proposed-codes list where a reader is scanning for things to enter.

**The second block works the same way and cannot use the same device**, because its code *is* proposed and *does* belong in that list. The equivalent is `SOURCE: filled` on the code itself in step 3 — the mark travels with the line rather than living in a heading. **The principle is identical in both: a block heading does not survive being copied one line at a time.** A worksheet that named the filled anchor only here, and left the proposed code bare, would lose the disclosure to a copy-paste — which is exactly the silent failure [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) opened for, arriving by a different route.

### 5. E/M level — only if asked

Offer the supporting elements (problems addressed, data reviewed, risk) and let the clinician assign the level. Do not select an E/M level unprompted.

**The differential is where the first element is documented, and that is the job those codes do.** A differential entry with its rationale is a problem addressed. A suspected diagnosis that drove an order — a swab sent, a film taken — is what *data reviewed* is reviewing. And an entry the encounter could not exclude is the one that carries the most weight in that column, because an undiagnosed new problem with an uncertain prognosis is not a low-complexity problem however ordinary the visit felt.

So the codes on the differential are required, and none of them is for entry. They are not a claim in miniature; they are the written form of the reasoning, and the reasoning is the element.

**The MDM phrasing here is recalled, and nothing in this repo verifies it** — the same posture as the outpatient rule in step 3, and now for its corrected reason rather than the one both paragraphs used to give. Guideline sheets ship and neither covers this: the medical decision making table is an **AMA CPT** document, and no AMA document is among the nine societies the corpus holds. Offer the elements, name that they are recalled, and let the clinician map them to a level.

**No lookup is added to this skill by [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85), and that is a ruling rather than an omission.** [clinical-note](../clinical-note/SKILL.md) is obliged to consult a sheet where one covers what a Plan item asserts; this worksheet is not, on any encounter. **A code is anchored to what the note documents, never to whether the number should have met a target** — a coder who declined `I10` because a pressure sat under a threshold sheet's cutoff, or who withheld a screening `Z` code because the patient fell outside a USPSTF population, would be re-deciding the clinical question from the worksheet with the note as its only input. That is the anchor rule running backwards, and step 3's *filled value is coded, and it is marked* already settled the general form of it: mark what a code rests on, never withhold on a ground the note does not carry.

## Completion

Every proposed code has a code number, a descriptor, an anchor, a specificity flag, and a confidence flag — five parts, no exceptions. **A code whose anchor was filled carries a sixth, `SOURCE`.** A code missing any of the five, or a filled-anchored code missing its sixth, is not ready to hand over.

**Every specificity flag carries substance beyond its keyword — a bare `complete` and a bare `needs:` both fail.** Present-but-bare is the one way a part can be there and still fail, which is why it is said here as well as in step 3. A descriptor saying `unspecified` or `not specified` may read `complete` only when the reason explains why nothing the bedside can supply would move the code; `python tools/specificity_scan.py <run directory>` enforces the reason and reports that shape as advisory for a reader.

**Every for-entry ICD-10 code has a separated second read by a fresh reader who did not see the worksheet.** Every subject code is covered; every source fact agrees with the committed FY2026 release; and the original reason has been read beside the independent `"about"` account. A missing, partial, or self-authored read is not completion. Agreement is a smoke test and never proof.

**A differential code is the one shape with fewer, and it is not an exception to that sentence** — it is a different thing being written down. Number, descriptor, confidence, three parts, plus `NOT FOR ENTRY` on the line. Anything with five parts or six is a code proposed for entry; anything with three is documentation of reasoning. **The count is still how the two are told apart** — the gap is five-or-six against three, and nothing lands between — which is why neither shape may borrow from the other.

And every value the FILLED block declared has been accounted for: either it supports no code, or every code it supports carries `SOURCE: filled` **and** appears under `CODED, ANCHOR WAS FILLED`. **Both, not one instead of the other** — the block is the summary a clinician reads once, the `SOURCE` line is what survives the code being copied out of the list. A filled value that quietly supports an unmarked proposed code is the defect this skill was rewritten to catch, and marking rather than refusing did not retire it.

Every hedged diagnosis in the Assessment has been accounted for the same way: coded, or sent to `NOT CODED, NOTHING ESTABLISHED IT` with the code the encounter does support proposed in its place. A hedge that produced no code and no refusal is a diagnosis this worksheet silently dropped.

**Every refusal resting on a pending test names what that result would establish.** A culture-pending refusal is limited to bacteremia or an organism-specific descriptor; a pending culture alone never withholds an unspecified-organism diagnosis. An imaging-pending refusal says that the image would establish the disease itself, and where documented findings reject the disease those findings are the reason. A `needs:` line that merely says a test is pending has not completed the descriptor check in step 3.

And every occurrence of spirometry identifies the intervention. An affected entry waited for a
qualified clinician restatement while unrelated extraction continued; no worksheet line relies on
a qualifier written somewhere else.
