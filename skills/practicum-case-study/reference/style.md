# House style for a practicum case study

Derived from **ten graded and returned submissions**, all from one FNP practicum course. This is
the authority [SKILL.md](../SKILL.md) points at for voice and for section shapes.

**Scrubbed.** The working file this was distilled from is gitignored: it names the clinician, quotes
his submitted work in full, and links his drive. What survives here is the *shape* — no name, no
dates finer than a year, no links. Standing rule 1 in [AGENTS.md](../../../AGENTS.md).

**All ten passed and the ceiling is high**, so this is a description of work that is already
working. What follows is not a repair list. It is the pattern to match, plus the handful of things
that drift between submissions and should be picked once.

---

## 1. Sanity Check

Always first, always before any clinical content. Four confirmations, one per line, then a closer:

```
Sanity Check:
Module 3 - confirmed
Video: Case III - confirmed
Video hyperlink - <url> - confirmed
Rashes - confirmed
Sanity Check completed - proceed
```

The four are **module or case number**, **which video**, **the hyperlink**, and **a one-line
description of the case**. Label and capitalization both drift across the set. Normalize to the
form above.

## 1a. Intake block — defined fields, never a table

**Ruled 2026-08-19, reversing *"the intake block is a table"*.** The clinician read the first
rendered submission and the demographics, the Review of Systems and the Physical Examination had all
been set as two-column tables. His words: *"for the patient demographics I would not make a
field/value table for that, I would define those fields and append the value"*, and for the Review of
Systems, *"I would not write a table, I would simply write the system and the findings"*.

So every intake section is **a field name, a colon, the value, as running text**:

> Age: 26 years. Sex: Female. Race/Ethnicity: African American. Occupation: Elementary school
> teacher.

**A table is still right for data that arrives as a table** — given laboratory results, given
diagnostic studies, a vital sign set. The distinction is that those are a *result set* with a shared
unit of meaning, and demographics, a Review of Systems and a Physical Examination are a *narrative*
that a table chops into cells. The Rx block in §8 stays a table because a prescription is a form.

### The Review of Systems and the Physical Examination

Same shape, one line per system, with the positives and the negatives signed:

> General: + fatigue and fever, - chills and weight loss.
> Gastrointestinal: + lower abdominal pain and mild nausea, - vomiting and diarrhea.

**The Review of Systems closes with a disclaimer and the Physical Examination does not.** His
instruction: *"I would put at the bottom of that ROS a disclaimer that all other systems reviewed and
are negative."* A Review of Systems is a question set and the closer is what makes the unlisted
systems *asked*; an examination is a set of maneuvers actually performed, and the same sentence there
would claim work that was not done.

### Never bullets, anywhere in the document

§ the skeleton rule in [SKILL.md](../SKILL.md) already forbids bullets in the differential, the MDM,
the Plan and the Patient Education. **It is the whole document, ruled 2026-08-19** — *"remember I
abhor bullet points"* — and the run that prompted this had set the HPI's OLDCARTS breakdown as a
bulleted list. Write the fields as running text on the pattern above.

### No scaffolding language in the finished document

Three forms the first submission carried, none of which he writes:

| Written | Write instead |
| --- | --- |
| `Using OLDCARTS:` before the HPI fields | nothing — just write `Onset: ...` and continue |
| `Ordered, not assumed` after an absent datum | say what is absent: `Not quantified in the case study` |
| `No known drug allergies` | `NKDA` |

**`Ordered, not assumed` is the sharpest of the three because it is this repo's idiom leaking into a
graded document.** It appears nowhere in any skill file — the run invented it — and it narrates the
skill's discipline to a reader who is grading a clinical note. The discipline is right and stays; what
goes is saying so out loud. Where a datum is missing, name the datum and put the order in the Plan.

### Most Likely Clinical Diagnosis is not bold

§4's exemplar sets it in italics and the run set the whole statement in bold. *"I don't do that."*
Ruled 2026-08-19. Italicize the organism names and leave the sentence in body face.

### The signature is one line

`Signed by: <name>, RN, CEN, TCRN` and the date sit on **one** line, separated as a sentence is. The
first submission put the date on its own line beneath, which renders as a stray orphan paragraph.

### These rules are graded by a command, and that is why they are written this precisely

**`tools/case_study_scan.py`, ruled 2026-08-19 on
[#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277).** Most of this section
and the prescription table in §8 are read by a scanner
[SKILL.md](../SKILL.md) step 9 runs over the draft, so a rule here is a rule that fails rather than
a rule that is remembered — [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s
*a prose edit to a rule fails nothing*, answered.

**Some behavior in this file is deliberately outside its graded rows.** The **em dash** is
counted and never graded, because it is a preference with a stated exception and a row keyed on one
would refuse a document he would have written himself. **Authored numbering surprises are counted
and never graded.** A section may intentionally continue a prior list above `1.`. And
anything that takes a **reading** — whether a stop criterion's endpoint is the right endpoint,
whether a wrapper instruction applies to this patient at all — stays a reader's, and
[SKILL.md](../SKILL.md) step 9 names each one. **A clean scan is not a checked draft.**

## 2. Assessment — an optional body under a required heading

The heading is always written. Its body is empty in three of the ten, and `Differential Diagnoses`
follows immediately. When there is a body it holds reasoning that belongs to no single diagnosis:

- **Teaching points on what the exam must include and why** — a carotid bruit, the diabetic foot
  exam, an ankle-brachial index, monofilament testing, each cited.
- **Arithmetic the case data permit.** Back-calculating body weight from a long-acting insulin dose
  through the total daily insulin requirement, then the insulin sensitivity factor, then the
  correction dose. Absolute lymphocyte and neutrophil counts from the white count and the
  differential percentages. The formula is written on the page.
- **Conflicts in the source data, named out loud.** One submission records that the video's
  description of a urinalysis contradicts the slide's, states both, and orders the test that would
  settle it. **That is the model.** Never reconcile a conflict silently.

  **The slides are inside the video — there is no separate deck to go and find. Ruled 2026-08-18.**
  That mattered because the rule as written left it ambiguous, and a run reading it could go
  hunting for a handout that does not exist and then treat the material as incomplete when it
  failed to turn one up. **So the rule is not about slides.** It fires wherever the material
  carries two accounts of the same finding — narration against what is shown on screen, the video
  against the graded wrapper, the wrapper against the case title. The wrappers are known to carry
  copy-paste damage, which makes the last of those the common one rather than the exotic one; see
  *The wrappers carry copy-paste damage* in [rubric.md](rubric.md).

## 3. Differential Diagnoses

- One diagnosis per line, **numbered and ranked**, `1.` favored.
- **ICD-10 pinned to the diagnosis with a hyphen** — `Hypokalemia - E87.6`. Present in half the
  set and absent in the rest; the spec marks it optional. Write it.
- Ordering carries weight. See §9.
- Never mix numbered and bulleted markers in one list — one submission does, and it reads as a
  defect.

## 4. Most Likely Clinical Diagnosis

One line, or a short list when several are genuinely co-primary. Two forms appear, and **the second
is the better one and shows up in the stronger work**: the diagnosis with its discriminator
attached.

> *Acute sigmoid diverticulitis with SIRS, due to the patient's left lower quadrant pain, axial CT
> confirmation, and two SIRS criteria: fever and heart rate.*

A bare list of diagnosis names is the weaker form.

## 5. MDM — one entry per differential, each stating the discriminator

Not a textbook summary of the disease. Each entry says **what in this case puts the diagnosis in or
out**:

> *Acute epididymitis: pain was of sudden onset and not gradual over several days, nor was there
> maximal tenderness on the posterior aspect of the testis on exam, nor any complaint of dysuria or
> discharge, making this less likely.*

Ruled-out entries end on the verdict — `making this less likely`, `is not a strong fit`,
`unlikely`, `must exclude`, `poor fit`. **In the strongest submissions the verdict is promoted to
the entry's own header line** — `- Cholecystitis - unlikely.` — with the reasoning underneath. Use
that form.

Every clinical claim carries a citation. Density runs one to three citations per entry.

## 6. Plan — orders, not prose

Bulleted imperatives. Drug lines carry dose, route, frequency, duration and indication. The
recurring items, in the order they usually appear:

1. **Disposition first when it is time-critical** — and the role transition is announced in line:
   `Refer to ED immediately (will treat as ED provider from this point forward)`.
2. **`Update allergies, height, weight, social hx, PMH, past surgical hx, family medical hx`** —
   in nearly every submission. This is the inverted fill default made concrete.
3. Labs, as one comma-separated line.
4. Imaging.
5. **Start / Stop / Hold / Continue**, one drug per line, each verb explicit.
6. Consults.
7. Education and monitoring — a blood pressure log, accuchecks, intake and output.
8. `F/u with PCP in 3 days after DC` — the standard closer.

**Conditional orders are written as conditionals, not deferred.** *"If the Padua prediction score
is 4 or greater, enoxaparin 40 mg subcutaneous daily, adjusted for creatinine clearance. If under
4, or bleeding risk is elevated, early ambulation with or without intermittent pneumatic
compression."* One submission goes further and writes a **timed** conditional with the procedure
spelled out — manual detorsion if urology is unavailable by a stated hour.

## 7. Patient Education — spoken, second person

The most distinctive voice in the document. It reads as a transcript of what he would say, not as a
handout:

> *"You need to be on a high-intensity statin given that your LDL is elevated, and you're a
> diabetic with high blood pressure. The statin will lower your LDL. But you need to watch out for
> a condition known as rhabdomyolysis. If you start cramping in your legs, or notice brown urine,
> get to the hospital immediately."*

Rules the corpus follows without exception:

- First and second person. Contractions. `I'm going to`, `I want you to`, `we'll`.
- **Every jargon term is named and translated in the same breath.**
- One bullet per plan item, in roughly plan order.
- The reasoning is given, not just the instruction — *why* the drug is changing.
- **Warning signs are concrete and actionable.** Never "seek care if symptoms worsen."
- Ends on the follow-up interval.
- Where knowledge is genuinely absent it is admitted to the patient rather than papered over.
- **No abbreviations at all**, though they are used freely in the Plan and MDM.

## 8. Rx — a fixed six-row table, three columns wide

One table per drug, including home medications continued unchanged.

| | | |
| --- | --- | --- |
| `<patient placeholder>` | `DOB x-x-xxx` | `NPI # <number>` |
| `<drug> <dose> <route> <frequency> [x duration]` |
| `Disp: <quantity, "QS", or "N week supply">` |
| `Sig: <spoken-out instruction> for <indication>` |
| `<name> FNP-C, CEN, TCRN` |
| `Refill: <none, or 0-3>` | `DEA number on file with pharmacy` |

**The table is three columns and most of its rows are merged, which is what makes it look like a
prescription pad rather than a list.** Row 1 carries three cells. The drug, the `Disp:`, the `Sig:`
and the signature each declare **one** cell and span the full width. The last row declares **two**,
so the refill sits on the left and the DEA line on the right. `docx_write.table` merges a short row
onto its last cell and right-aligns that cell when the row has more than one — the layout is a
consequence of how many cells a row declares, and nothing else.

**This shape is ruled 2026-08-19 and it replaces a one-column table whose row 1 separated its three
items with `&#124;`.** That spelling rendered as literal text, and a run copying the idea wrote
`\|` instead, which rendered as a stray backslash — *"the patient carries a `\` and so does the end
of my titles"*. Worse, the one-column header made the grid as wide as its widest row while every
other row held a single cell, so the drug, the `Disp:`, the `Sig:` and the signature all sat in
column 1 with two empty columns beside them. **Both defects came from faking columns inside one
cell. The table has real columns now, and no row needs an escaped pipe.**

- **The patient cell is always a placeholder and the date of birth is literally `x-x-xxx`.** A case
  study prescription carries no identifiers.
- **Sig spells the numbers out** — `Take one tablet daily`, `Infuse 500 mg three times a day` — and
  always ends `for <indication>`.
- **Held orders are labeled in the drug row**: `Delayed order: metformin 500 mg PO BID, hold until
  the acute kidney injury resolves`.
- **A home medication continued unchanged is labeled in the drug row too**: `Continued home
  medication: prenatal vitamin one tablet PO daily`. Ruled 2026-08-19 on
  [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289), and it is the label that
  does the work rather than the fact. A record in the step 3 ledger is required for every drug the
  run **chose a number for**; a dose the patient arrived on is not one, and this is how the row says
  so. **The exemption is declared and never inferred** — an unlabeled row is graded, so a run that
  forgets the label is asked for a record rather than let through. `Delayed order:` exempts nothing:
  a dose that has not started yet is still a dose the run chose. `tools/research_ledger.py --draft`
  reads both labels off this table.
- **One table per drug means one drug per drug row, and a welded pair is how that rule gets
  broken.** A row reading `doxycycline 100 mg PO BID x 7 days and metronidazole 500 mg PO TID x 7
  days` is two prescriptions in one table, and the second drug's dose is then sourced by nothing:
  `tools/research_ledger.py --draft` takes the leading token as the drug, so the expected set comes
  out right by formatting, and `tools/case_study_scan.py`'s stop-criterion row reads the cell as one
  order, so the first drug's `x 7 days` discharges it for the second. **Neither command reaches it
  and neither will** — telling two drugs apart needs a drug vocabulary, which is the artifact
  [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289) prohibits in as many
  words, and every form that avoids one fires on correct orders instead — a titration, a repeat
  dose, an infusion rate, and a taper too once the form is broad enough. **So a
  run that welds a second drug into one row is caught by a reader and by nothing else**, and
  [SKILL.md](../SKILL.md) step 9's `the Rx blocks` row asks for it by name. Ruled 2026-08-20 on
  [#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300), where the measurement
  that declined the parser row is a test rather than a figure here.
- **A drug held because it is contraindicated gets no table at all.** Ruled 2026-08-18 against a run
  that wrote one for doxycycline in pregnancy. A delayed order is for a drug that is coming later
  once a condition clears. A contraindicated drug is never coming, and a prescription block for it is
  a prescription for a drug that must not be given. The decision not to use it belongs in the Plan
  and the MDM, as reasoning.
- Acute, one-time and intravenous drugs take `Refill: none`. Maintenance takes `Refill: 3`.
- **A drug that continues carries its stop criterion in the drug row. Ruled 2026-08-19.** An order
  reading `Ceftriaxone 1 g IV every 24 hours` says when to start and never says when to stop, and
  the reader supplies *until discharge* out of their own head. The clinician's words: *"the rocephin
  did not have a stop criteria on it, I assume that it is continued every day until discharge but
  assumption is the mother of all fuckups, so that needs addressed."* A one-time dose already
  states its own endpoint and needs nothing added.
- **A stop criterion is a clinical claim and takes a source like any other. Ruled 2026-08-19, the
  same day and out of the same reading.** The first attempt at the row above supplied the endpoint
  from recall — *"then stepped down to oral therapy to complete 14 days total"* — inside a
  **ceftriaxone** order. **Ceftriaxone has no oral form**, and the oral agent that would have
  completed that course was contraindicated in the patient it was written for. Both errors were
  invisible to every gate in `tools/`, because a dose nobody entered as a research record is a
  claim `research_ledger.py` cannot see. [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289).
- **So where the duration is not sourced, write the endpoint you can defend and say what sets the
  rest** — *"continued for the admission and reassessed daily against the fever curve"* — rather
  than a number recalled. **A route change is a different drug unless the drug has that route**, and
  saying so in the order is cheaper than a reader assuming it does.

**The credential in this block is `FNP-C, CEN, TCRN`** — the prescribing role the case study puts
him in. The `Signed by:` line at the foot of the document takes `RN, CEN, TCRN`, which is what
every real clinical note takes. Two strings in one document is correct.

### The prose block under each table — ruled 2026-08-18

The table stays six rows. Underneath it, one short paragraph carries the five fields the spec's
Pharmacologic Therapy component asks for and the table has never held: **drug class,
contraindications, monitoring, adverse effects, and the guideline supporting the choice.**

> Third-generation cephalosporin. Contraindicated in anaphylaxis to cephalosporins or a severe
> penicillin reaction. Monitor the injection site and observe for hypersensitivity over the
> following 30 minutes. Adverse effects are injection-site pain, diarrhea and rash. First-line for
> this indication in `<the guideline the step 3 record for this drug sourced>`
> `(<Author> et al., <year>)`.

**The guideline sentence carries a placeholder rather than a citation, and that is the one thing in
this example that is not a style choice.** It named a specific CDC guideline until
[#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289), and the companion evidence
does not carry that topic — it cross-references it repeatedly and carries none of its body — so the
worked example was teaching a run to cite a source it had never read. **How many times is measured
on #289 and deliberately not restated here**: it is a count over a dump under `scratch/`, so nothing
committed re-derives it, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143). **The citation here comes
off the ledger record for this drug or it does not go in**: [SKILL.md](../SKILL.md) step 3 requires
one for every drug the run chose a number for, and `tools/research_ledger.py --draft` fails a
document whose prescriptions do not reach one.

**Prose and not a second table, and not eleven rows in the first one.** The six-row table is a
prescription and reads as one; the five added fields are graded reasoning, and graded reasoning
belongs in prose. **Omitting them has never cost a point across ten submissions**, which is
evidence that the omission is survivable rather than that it is right — the same finding the mode
ruling rests on. See [SKILL.md](../SKILL.md) step 6.

## 9. Ordering is the graded axis

The three deductions across the ten submissions were **all clinical decisions**. Not one was
formatting, citation or completeness:

| What was docked |
| --- |
| Sent a patient to hospital where referral to nephrology and cardiology would have done; should have held the metformin |
| Missed a 30 mL/kg normal saline sepsis bolus; chose the wrong antibiotic for the source |
| *"Ectopic pregnancy needs to be your number one differential, not appendicitis"* |

**The third is the sharpest lesson in the set.** Ectopic pregnancy was on the differential, was
labeled `must exclude`, and was worked up with a pregnancy test in the plan. It still cost five
points, because it was listed eleventh of thirteen and appendicitis was named most likely.
**Ordering is graded, not just membership.**

Against that: one submission scored full marks with a single reference, no plan, no prescriptions,
no differential list and no signature. It answered the four questions the faculty asked and nothing
else.

**The conclusion drawn from that here used to be *"Completeness is not what is being rewarded.
Judgment is."* It is withdrawn, and the sentence it justified is reversed.** Ruled 2026-08-18 —
every skeleton section is written every time, and faculty questions are answered in addition to it
rather than instead of it. **What the submission proves is that the omission was survivable on one
occasion, not that it was rewarded**; the rubric scores ten criteria and four faculty questions
need not touch all ten, so the sections it dropped were points nobody checked rather than points
nobody wanted. See *Three modes, and none of them subtracts a section* in [SKILL.md](../SKILL.md),
and the rulings block at the foot of this file.

**Judgment being what earns the marks is still true, and it was never the same claim.** It is why
the three deductions are all clinical and why ordering is graded — it is not a reason to hand in
fewer sections.

## 9a. Faculty Questions — the section the mode ruling created

**New 2026-08-18 and it has no corpus precedent, which is the point.** The two submissions that
answered faculty questions did so *instead of* the workup; this section is what answering them
*alongside* it looks like, so there is no submitted example to derive a shape from and the shape
below is a ruling rather than a description.

- **Sits after `Signed by:` is wrong — it sits before it**, at skeleton position 10, so the
  signature stays the last thing before the references.
- **Present only where the faculty material poses explicit questions.** No questions, no heading.
- **Each question is restated verbatim, then answered underneath in prose.** Restated because a
  grader reading for *"did they answer what was asked"* should not have to hold the question sheet
  beside the paper.
- **Numbered, matching the faculty's own numbering** where they numbered them.
- **An answer may point at a section rather than repeat it** — *"Covered in the differential above;
  the short answer is ectopic pregnancy first, for the reason in MDM entry 1."* The sections are
  already written, and restating them wholesale is what made the replacement mode attractive in the
  first place.

**A question the skeleton already answers still gets an entry here.** The section exists so that
every item on the faculty's own list can be pointed at, which is [SKILL.md](../SKILL.md) step 9's
first check.

## 10. References — APA 7

**[apa7.md](apa7.md) is the authority here and this section is the corpus description beside it.**
Where the two disagree, APA wins — this section describes ten submitted documents, and those
documents are not the standard.

- **UpToDate dominates** — roughly nine in ten across the set:
  `Author, A., & Author, B. (Year). Title in sentence case. UpToDate. Retrieved Month D, YYYY, from
  https://...`
  **Two corrections to that form, from APA's own UpToDate page** — the database name is
  *italicized* in the entry and not in running text, and the year is the topic's **last update**
  year rather than the year it was read. See [apa7.md](apa7.md) §2. The corpus does neither.
- The set includes a university teaching page, a badge reference card, and a state administrative
  code — the last cited properly with its section number and pulled through into the argument,
  which is the right way to use a non-clinical source.
- **`Non-UpToDate entries are formatted the same way` was wrong and is withdrawn.** A retrieval
  date belongs only where the work is designed to change *and* the version cited is unarchived —
  so UpToDate takes one and a society guideline, a journal article, a USPSTF statement and a
  textbook do not. Copying the UpToDate form across the whole list puts a retrieval date on most
  of the entries that must not carry one, which is a defect in the opposite direction from the one
  the table below catches. [apa7.md](apa7.md) §4.
- **`Roughly alphabetical` is what the corpus is, not what the rule is.** Alphabetize by the first
  word of the entry. [apa7.md](apa7.md) §1.

### The defects to fix every time

| Defect | Fix |
| --- | --- |
| `Links to an external site.` welded to the end of a URL | strip it — a Canvas paste artifact, confirmed |
| Retrieval year one behind the exam year | the retrieval date must be on or after the exam date |
| In-text year not matching the reference-list year | reconcile both |
| Two entries, same author and year, no `a`/`b` | disambiguate in the list *and* in the text |
| A missing space in a date, or a misspelled month | check every one |

**A citation year or edition is looked up, never recalled.** UpToDate revises continuously, and the
same topic appears in this corpus under three different years.

## 11. Voice — the things that are his and must survive

**These are the mechanics, and a run can satisfy every one of them and still read as a competent
stranger.** That happened, and it is what
[#213](https://github.com/mshamblin5150-code/clinical-skills/issues/213) was filed on. The list
below was written by reading finished documents for *what they do*; the **register** — how it
sounds — is [voice.md](voice.md), which is the method for modeling it from writing samples. Neither
file replaces the other: these bullets bind whether or not a model exists, and a model that
contradicted one of them would be a model of the wrong thing.

- **First person and decisive.** `I would`, `I will`, `I'm going to stop`. Never *the provider
  should consider*.
- **Missing data becomes an order, not an assumption.** The inversion from
  [clinical-note](../../clinical-note/SKILL.md), and the single most important rule here.
- **Show the arithmetic.** eGFR, anion gap, ten-year ASCVD risk, insulin sensitivity factor,
  absolute neutrophil count, an estimated date of confinement by Naegele's rule and by adding 280
  days. Both methods, when both exist.
- **Name the inconsistency instead of resolving it silently.** State both hypotheses, pick one, say
  why, and order the test that would settle it.
- **Reason on physiology, not on lists.** *"The body obeys physics: intravascular volume rises,
  edema expands, and blood pressure climbs."*
- **Dry, occasionally funny, never at the patient's expense.**
- **Rarity gets argued down, not ignored.** A low-probability diagnosis stays on the list with an
  explicit reason for staying and an explicit trigger that would promote it.

## 12. Mechanical defects seen in the corpus — never reproduce

Word-joining damage from a bad paste (`isvery commonand`, `patienthas`, `OrderCBC with diff`). A
year typed a decade wrong, in a passage whose entire point was that accurate dating matters. A
stray `±` alone on its own line. **A transcription defect in a document about precision reads as
carelessness about the precision.**

## Ruled 2026-08-18 — the four this file carried open, plus one

Settled with the clinician on
[#211](https://github.com/mshamblin5150-code/clinical-skills/issues/211). Recorded here because
this is where they were left open, and a reader who knew to look here should find the answer rather
than the question.

**1. Q&A mode does not replace the full workup.** Every skeleton section is written every time,
and faculty questions are answered in addition to it. **This reverses what
[SKILL.md](../SKILL.md) shipped saying.** The evidence for replacing was two full-marks submissions
that did it — real, and not enough, because the rubric scores ten criteria and a set of faculty
questions need not touch all ten. The reasoning is in [SKILL.md](../SKILL.md) under *Three modes,
and none of them subtracts a section*.

**2. The `a`/`b` disambiguation, the retrieval dates and the rest of the reference walk are not
optional, and their findings are not handed back.** His words: *ordering the differential is very
important, but that shouldn't take the place of tidiness.* The sentence in
[SKILL.md](../SKILL.md) that read *the ordering of a differential matters more than the tidiness of
a citation* is gone, because a run could read it as permission to skip the walk. The rubric's
70-of-100 weighting still decides where the **length** goes; it never decided what may be left
broken. **[apa7.md](apa7.md) exists because of this ruling** — an instruction to fix the reference
list needs a written rule behind it.

**3. The slides are inside the video.** No separate deck to hunt for, and the conflict rule
generalizes to any two accounts of the same finding in the material. See §2 above.

**4. `Case ID:` is a stray. Never write it.** One submission in ten, no deduction anywhere for its
absence, and nothing in the spec asks for it. **The risk ran the other way**: a run that derived a
case number from the module number would be writing a wrong identifier onto a graded paper.

**5. The Pharmacologic Therapy fields go in a prose block under the Rx table**, not into the table
and not nowhere. See *The prose block under each table* in §8.

## Still open

**Nothing from the original four.** What remains is tracked rather than listed here:
[#213](https://github.com/mshamblin5150-code/clinical-skills/issues/213) the voice model — whose
**method** is built and lives in [voice.md](voice.md), leaving one clinician's actual model as a
thing that only samples can produce —
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) the research fan-out and
the recency rule,
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) the two APA gaps the
renderer has left, and
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218) checkers over the finished
draft. [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217) is settled — it
was filed as the renderer's three APA gaps and closed five, two of them found after it was
written.
