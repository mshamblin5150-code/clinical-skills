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

## 8. Rx — a fixed six-row table

One table per drug, including home medications continued unchanged.

| |
| --- |
| `<patient placeholder>` &#124; `DOB x-x-xxx` &#124; `NPI # <number>` |
| `<drug> <dose> <route> <frequency> [x duration]` |
| `Disp: <quantity, "QS", or "N week supply">` |
| `Sig: <spoken-out instruction> for <indication>` |
| `<name> FNP-C, CEN, TCRN` &#124; `DEA number on file with pharmacy` |
| `Refill: <none, or 0-3>` |

- **The patient cell is always a placeholder and the date of birth is literally `x-x-xxx`.** A case
  study prescription carries no identifiers.
- **Sig spells the numbers out** — `Take one tablet daily`, `Infuse 500 mg three times a day` — and
  always ends `for <indication>`.
- **Held orders are labeled in the drug row**: `Delayed order: metformin 500 mg PO BID, hold until
  the acute kidney injury resolves`.
- **A drug held because it is contraindicated gets no table at all.** Ruled 2026-08-18 against a run
  that wrote one for doxycycline in pregnancy. A delayed order is for a drug that is coming later
  once a condition clears. A contraindicated drug is never coming, and a prescription block for it is
  a prescription for a drug that must not be given. The decision not to use it belongs in the Plan
  and the MDM, as reasoning.
- Acute, one-time and intravenous drugs take `Refill: none`. Maintenance takes `Refill: 3`.

**The credential in this block is `FNP-C, CEN, TCRN`** — the prescribing role the case study puts
him in. The `Signed by:` line at the foot of the document takes `RN, CEN, TCRN`, which is what
every real clinical note takes. Two strings in one document is correct.

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
else. **Completeness is not what is being rewarded. Judgment is.**

## 10. References — APA 7

- **UpToDate dominates** — roughly nine in ten across the set:
  `Author, A., & Author, B. (Year). Title in sentence case. UpToDate. Retrieved Month D, YYYY, from
  https://...`
- Non-UpToDate entries are formatted the same way. The set includes a university teaching page, a
  badge reference card, and a state administrative code — the last cited properly with its section
  number and pulled through into the argument, which is the right way to use a non-clinical source.
- Roughly alphabetical.

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

## Still open — needs the clinician

1. **Rubric versus grader.** The evidence says the grader rewards clinical judgment and
   differential ordering, and does not appear to police citation minimums or section completeness.
   That is a reading of three deductions, not a rule.
2. **Where the slide description came from** in the submission that compared the video against
   slides. The video-versus-slides conflict rule is live and its source is unclear.
3. **`Case ID:`** appears above the references in one submission and nowhere else. Required field,
   or a stray?
4. **Q&A mode** — when faculty questions are present, do they replace the full workup or sit
   alongside it? Both submissions that replaced it scored full marks, which is evidence and not a
   ruling.
