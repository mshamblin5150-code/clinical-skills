# hedged-dx — inputs

Three encounters, one file each, transcribed from the day-file text. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the day file, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## What the set is for

[Drift row 13](../../skills/clinical-note/SKILL.md) has two halves. The first — *every differential entry carries an ICD-10-CM code* — fires on every note ever generated, and `day-b`'s C1 has held it since [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19). The second half is this set:

> **no diagnosis the encounter did not establish** — differential entry, favored entry or final — carries a code whose descriptor names a confirmed organism or disease

`day-b` can test that on a diagnosis the *skill* generates, which is its C2: a documented COVID contact, no swab, and an entry that must not code `U07.1`. It cannot test it on a hedge the **clinician wrote**, because zero of its twelve inputs carry a hedge token. `day-b`'s own file says so and names the gap as owed. This set is that fixture. [#49](https://github.com/mshamblin5150-code/clinical-skills/issues/49).

## This set is not a shift, and the numbering says so

`day-a` and `day-b` are whole shifts. `peds-bp` is part of one, and keeps that shift's numbering so the gaps show what was left out. **This set is neither.** Its three encounters come from **three different day files**, because a hedge on an organism-specific diagnosis is rare and no single day holds two of them.

So the cases are renumbered `01`–`03` and the `Note <n>` line inside each file is renumbered to match. Which day file each came from is deliberately not recorded: file names carry the visit date and the preceptor.

## It is a pick, not a population, and that is stated rather than hidden

`obesity-bmi` spans three day files too, and clears [fixtures/README](../README.md)'s recomputability bar by being the **whole** of a shape the corpus contains four times. **This set cannot do that.** Measured 2026-08-15 across 551 encounters with `tools/corpus_census.py`:

| | n | share |
| --- | --- | --- |
| hedge token anywhere in the shorthand | 33 | 6% |
| **beside an organism- or disease-specific term** | **17** | **3%** |

Three of those seventeen are here. **They were selected to make the rule fire**, by reading the seventeen and choosing the ones where a code would over-claim hardest — which is exactly the curation [fixtures/README](../README.md) warns can make a set look chosen to pass. Saying so is the defense, not a disclaimer on one.

**What is recomputable is the pool, not the pick.** `tools/corpus_census.py` prints both rows above, so anyone can re-derive the seventeen and ask why these three. Taking all seventeen was the alternative and it would have killed the set: [fixtures/README](../README.md) already records that this repo writes rows faster than it runs them — `day-b` holds thirty-one rows and has scored twenty-four — and a seventeen-case set would never be run at all. **A tighter filter engineered to return exactly these three was considered and refused**: it would read as recomputable and prove nothing, which is worse than an honest pick.

## The three, and what each one is for

**Case 1 is the pure over-claim.** `dx CAP likely mycoplasma`, and nothing in the encounter names an organism. `J15.7 Pneumonia due to Mycoplasma pneumoniae` says one; `J18.9 Pneumonia, unspecified organism` is what the encounter supports.

**Case 2 is the contrast, and it is the only adult and the only non-respiratory case.** Two organism-shaped things in one encounter, with opposite verdicts: a wound culture that **came back** — `reveald klebsiella pneumonea`, `resistant to current abx regimen` — and a film ordered `r/o osteomyelitis` that resulted in nothing. A run that refuses every organism-specific code passes case 1 and fails here.

**Case 3 is the control.** `dx: URI vs mycoplasma` puts both directions on one line: `J06.9 Acute upper respiratory infection, unspecified` asserts nothing and **must be coded**, while the mycoplasma half must not be. Without it, a note that withheld every code in the set would score full marks — which is what `filled-anchor` run 1 did before [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) reversed three rows and voided its `ANCHOR` column.

**The set is narrower than is comfortable.** Two of three are pediatric respiratory, and both hedge the same organism. That is worth knowing when reading a score off it, and it is not fixable from seventeen candidates without taking cases whose codes turn on judgment — see *What was left out* below.

## The hedges are clinical judgments, and the clinician said what they rest on

Ruled 2026-08-15, in conversation, and recorded here because it changes how the rows should be read rather than what they say.

**Case 1's mycoplasma is radiographic.** A pneumonia was seen and the film read the way atypical pneumonia films read. *"You can't diagnose pneumonia just by listening to someone, you need a CXR."* The impression is well-founded and a reader who knows those films would reach it too.

**Case 3's is not, and cannot be** — its own shorthand records the chest film as negative. What it rests on is the course: three weeks of cough and fever, cefdinir already failed, strep, influenza and COVID all tested negative, and azithromycin started. Atypical coverage on a protracted illness that did not respond to a cephalosporin.

**Neither earns the organism-specific code, and that is the point of the set.** A row that only caught careless hedges would be worth very little. These are careful ones.

## Two things the inputs leave out, and this is the one set that can say so

[fixtures/README](../README.md) records that a **reference** note may be missing things and that nobody can ever know what — *"and they could be, I don't know."* That is stated about the portal notes and it is equally true of the day file. **Here it is not unknowable**, because the clinician is available and was asked. Both were volunteered on 2026-08-15:

- **Case 1's chest film is not written down and it happened.** The shorthand runs `decreased air movment in lungs. dx CAP likely mycoplasma. plan zithromax` with no imaging token anywhere. A pneumonia cannot be diagnosed by auscultation, so the diagnosis **presupposes** a film the record omits.
- **Case 2 was offered admission and declined it.** The shorthand records only the outcome — `will follow in clinic on thursday` — and not the deliberation. The patient was willing to do follow-up instead of an admission.
- **Case 2's blood culture is not written down and probably happened.** Volunteered 2026-08-15 while [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68) was being settled: *"that paitent definatly had bacteremia i think i did a lactate and a blood c/s but didn't write it in that note."* **The lactate is in fact written down** — the plan line runs `amy, lip, lactate, ABG, urince c/s, micro scopic urine, cxr` — and it is an order carrying no result like the rest of that panel. The blood culture is not: `urince c/s` is the urine one, and `c/s from [DATE] of wound` is the wound one. Recorded with the hedge the clinician gave it, *"i think"*, rather than promoted to a given.

**None of the three is a license for a run to supply them.** Drift row 3 forbids filling an imaging result outright, and case 1's D1 exists to check that the note refuses to. The record is here so that a later reader knows the absence is a transcription gap rather than a clinical one, and does not read a correct note as having missed something.

**And the third one changes no row, which is worth saying because it looks as though it should.** A blood culture written into the input would not establish bacteremia either — it would be one more order carrying no result, exactly like the lactate beside it. What a note may say about `R78.81` is unchanged, and what rejects **sepsis** on this encounter was never the culture: it is `bp 126/80 hr 77 t 97.3 rr 18`, which meets no SIRS criterion. That distinction is [#149](https://github.com/mshamblin5150-code/clinical-skills/issues/149) and is the one thing run 1 got wrong on this case while reaching the right verdict.

## What was changed on the way across

Everything else is verbatim, typos included. `sistiser`, `2 weeeks`, `movment`, `bettery`, `phayrngeal`, `urince`, `reveald`, `draininge`, `sicnce`, `eart tympansotomy`, `claritian`, `prednisolono`, `s1,s2, 2/2j` and case 2's truncated `Dx chronic right lower extremity` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[DR]` | Case 2's named physician, who was called in and read the culture. Named provider plus age plus a small county narrows the population the way the site name does. What mattered clinically — that a physician evaluated the patient and reviewed the sensitivity report — survives. |
| `[SITE]` | Case 2's named outside facility, a two-month admission for the same wound in 2023. The year stays; a year alone identifies nobody. |
| `[DATE]` | Case 2's prior visit, four days earlier, written twice — `was seen on [DATE]` and `c/s from [DATE]`. **Both tokens are the same date in the source**, and the culture is from that visit. A visit date finer than a year is the identifier that matters here. |
| `[HOLIDAY]` | Case 3's `sicnce [HOLIDAY]`. A fixed calendar day plus `sick for 3 weeks` reconstructs the visit to within days, which is the visit date arriving by the back door. Same reasoning as `peds-bp`'s. The interval survives; only the anchor goes. |
| `3 yo` | Case 3's source gives a **date of birth and no age**. [fixtures/README](../README.md) requires the age be derived before the date is stripped, or the case silently becomes a missing-age test. Derived against the day file's own date: 3 years 4 months. |

**Case 3's sex is not stated in the source and is not supplied here.** The record gives a name and no sex marker — no `M`, no `F`, no pronoun in the exam line, which reads `well appearing child`. Inferring one from the name would be inventing a given, and the name is exactly what standing rule 1 removes. A run that needs a sex will have to fill one, and nothing in this set scores it.

**Case 1's `hr 1238` is preserved and is not a typo to fix here.** A heart rate of 1238 is impossible and the intended value is unrecoverable — 123 and 128 are equally available and nothing in the encounter chooses. No row in this set turns on it. It stays because repairing a source defect inside a fixture is how a fixture stops testing the corpus it came from, and because what a note does with an impossible given is a real question nobody has asked yet.

Line wrapping was removed. The source files wrap mid-sentence at the width they were captured at, and `obesity-bmi` unwrapped for the same reason: the breaks are an artifact of the capture, not the clinician's paragraphing. No word, no punctuation mark and no space inside a line was touched.

## What was left out, and why

**A fourth case was read and rejected on the coding, not the clinical picture.** A 4-year-old whose shorthand carries `cxr - mycoplasma cap vs viral pna. dx: flu a+, mycoplasma CAP` — the same contrast as case 2, in one diagnosis line, with the film actually written down. It would have been the best-documented case in the set.

**`J18.9` carries `codeFirst: if applicable, associated influenza (J09.X1, J10.0-, J11.0-)`**, verified against `reference/icd10cm-2026.sqlite`. So a positive influenza beside a pneumonia is a coding decision — whether the pneumonia belongs to the flu — and a row over it stops being *is `J15.7` present, yes or no* and becomes a judgment about which pneumonia code is right. [fixtures/README](../README.md) is firm that a row turning on judgment cannot be binary, so the case went out and case 2 carries the contrast instead: a wound culture and a leg film do not collapse into one code.

It is named here rather than silently dropped, on `peds-bp`'s terms: a set scoped to part of what it could have covered says what it left out.

## Do not resolve the hedges in these files

An input whose diagnosis has been tidied to `mycoplasma pneumonia` or `viral URI` cannot test what the skill does with a hedge, which is the entire set. `clinical-note` states the rule the other way round — *"Never … soften a hedge — `prob viral` becomes `probable viral`, not `viral`"* — and these three files are the only committed inputs that put it under load.

The same applies to the negatives. Case 2's `strep (was negative)` and case 3's `strep, flu and COVID testing all negative` are **results**, and removing one would turn a documented rule-out into an untested organism and change which row the case anchors.
