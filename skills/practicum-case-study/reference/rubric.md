# What a practicum case study is graded by

The course spec, distilled. Captured from the program's learning management system for an FNP
primary-care-across-the-lifespan practicum. **Read this before drafting** —
[SKILL.md](../SKILL.md) points here for the required components, the point weighting and the
guideline roster.

**Course numbers, module numbers and due dates are deliberately not in this file.** They change
every term and they are per-account; they live in `scratch/medatrax-profile.md` with everything
else about *which* clinician. What is here is the part that does not change.

---

## Where the spec lives, and the trap in it

The graded topics are **not** where the instructions are. In the term this was captured from, the
master spec sat in a separate ungraded topic — one that still carried the title *Discussion
Introductions*, because the faculty reused it — while the five graded topics each carried a thin
wrapper worth the actual points.

**So there is one spec to read and several thin per-case wrappers**, and a wrapper's header may say
*no due date, 0 points possible* while being the only place the requirements are written. Find the
master topic before concluding the assignment is underspecified.

### The wrappers carry copy-paste damage, and the case title is the authority

The wrappers were cloned from one another and the population word was not always swapped. Observed
in a single term:

- A geriatric case opening *"To successfully complete this **adolescent** clinical case scenario"*.
- An obstetric case asking the student to *"Conduct a comprehensive **adult** assessment"*.
- *"Evaluate growth, development."* surviving into four cases where it means nothing.
- *"weight-based prescribing principles"* in **all five**, including the geriatric and obstetric
  ones.

**Treat the population word in a graded wrapper as unreliable. The case title and the faculty
material are the authority.**

---

## Required Components

Demographics · chief complaint · HPI in OLDCARTS or OPQRST · comprehensive history · review of
systems · physical examination · diagnostic studies · differential diagnoses · working diagnosis ·
medical decision making · comprehensive treatment plan · follow-up.

The treatment plan is itself enumerated: **pharmacologic, nonpharmacologic, preventive, health
promotion, patient education, referrals.**

**Two places the corpus's habitual intake block falls short of this list**, both worth closing:

**Demographics asks for more than age and sex.** The spec names **occupation or school status,
marital status, insurance, social determinants of health, and cultural considerations**. The
habitual block carries age, sex, race and source. [clinical-note](../../clinical-note/SKILL.md)
already infers marital status from age and fills payment method and race from declared rules — the
same machinery serves here, except that in a case study an unknown is **ordered rather than
filled**. See the tier rule in [SKILL.md](../SKILL.md).

**Pharmacologic therapy asks for more than the Rx table carries.** For every medication: generic
name, **drug class**, dose, route, frequency, duration, **contraindications**, **monitoring**,
**adverse effects**, patient education, **guideline support**. The habitual table carries drug,
dose, route, frequency, duration, sig and indication. The bolded five land in the patient-education
prose when they land at all, which is unstructured and case-dependent.

**Write them, in a prose block under each Rx table. Ruled 2026-08-18** — the table keeps its six
rows, and the five go underneath it as one paragraph rather than into the table or into nothing.
The shape and the worked example are in [style.md](style.md) §8; the reasoning is in
[SKILL.md](../SKILL.md) step 6. **Omitting them has never cost a point**, which the ruling treats
as survivable rather than as safe.

## Two explicit limits

**Three to five prioritized differential diagnoses.** The rubric line repeats it. The corpus
exceeds it constantly — nine, eleven, thirteen — and **has never once been docked for count**.
`Prioritized` is the word that is actually graded; see *Ordering is the graded axis* in
[style.md](style.md).

**ICD-10 is optional.** The working-diagnosis component marks it so. That explains why the corpus
carries codes in some submissions and not others — it was never required. Writing them is a
strength.

---

## The rubric — 100 points, ten criteria

| Criterion | Points |
| --- | --- |
| Comprehensive Treatment Plan | **20** |
| Comprehensive History and Physical Examination | **15** |
| Differential Diagnoses and Clinical Reasoning | **15** |
| Review of Systems and Physical Examination | 10 |
| Diagnostic Studies and Interpretation | 10 |
| Medical Decision Making | 10 |
| Preventive Care and Health Promotion | 5 |
| Integration of Evidence-Based Guidelines | 5 |
| APA Format and Scholarly Writing | 5 |
| Peer Clinical Critique | 5 |

**Clinical judgment carries 70 of the 100 points.** APA format and guideline integration carry 10
between them, and that is why [SKILL.md](../SKILL.md) spends its length on the differential and its
ordering rather than on citation hygiene.

**It is a claim about where the length goes and not about what may be left broken.** This paragraph
used to add that *a grader who docks only clinical decisions and never formatting is not deviating
from the rubric*, which was true of every deduction the corpus records and was being read as a
license to skip the reference walk. **Ruled 2026-08-18 on
[#211](https://github.com/mshamblin5150-code/clinical-skills/issues/211)** — the walk runs on every
document and its findings get fixed rather than handed back. [apa7.md](apa7.md) is the rule it runs
against. **That evidence is also a thin basis for a claim about the grader** — it is three data points,
counted once in [style.md](style.md) §9 and deliberately not restated here — **and the published
weighting above supports the same emphasis without needing it.**

**Preventive Care and Health Promotion is 5 points that a focused acute case makes easy to
forget.** `reference/guidelines-uspstf.md` in this repo holds 143 USPSTF recommendation statements
and is the cheapest way to earn it — age-appropriate screening, immunization status, counseling.

---

## The required guideline roster — 21 bodies

The spec's *Required Evidence-Based Clinical Guidelines* section, with the instruction:
*"Students should integrate only those guidelines that are applicable to their selected case."* So
this is a menu, not a checklist — but **Integration of Evidence-Based Guidelines is a scored line**,
and a case study that cites no society at all forfeits it.

| Group | Bodies |
| --- | --- |
| Primary care | USPSTF, CDC Immunization Schedule, CDC STI Treatment Guidelines |
| Chronic disease | ADA Standards of Care, ACC/AHA, KDIGO, GOLD, GINA, ACR, AACE, AGA, ACG |
| Pediatrics | American Academy of Pediatrics, Bright Futures, CDC Childhood Immunization Schedule |
| Women's health | ACOG, Society for Maternal-Fetal Medicine |
| Mental health | American Psychiatric Association, American Academy of Sleep Medicine |
| Pain management | CDC Clinical Practice Guideline for Prescribing Opioids for Pain |

That is 20. **IDSA is the twenty-first**, and it is easy to miss: it appears only in the section's
closing supplementary list and not in the grouped table above.

**The roster names bodies, not documents.** A body is not a citation. Resolving one to a current
document title, year and URL is a lookup, never a recall — and this repo's own corpus covers nine
societies of the twenty-one:

```bash
python tools/guidelines_search.py "<the clinical question>"
```

`reference/guidelines-catalog.md` lists what is indexed. **A body absent from that catalog is not a
body with no guideline** — it means this repo has not indexed it, and the document has to be found
and cited from the source. The distinction matters: an empty search result here is a fact about the
index, never about the society.

## Foundational references the spec supplies

Cite these where they apply; the spec lists them itself, so they need no defense.

AACN Essentials · AANP FNP Certification Examination Blueprint · ANCC FNP Certification Examination
Content Outline · Buttaro, Trybulski, Polgar-Bailey & Sandberg-Cook, *Primary care:
Interprofessional collaborative practice*, Elsevier · CDC immunization schedules, current · NONPF
Nurse Practitioner Role Core Competencies · NTF Standards for Quality Nurse Practitioner Education ·
USPSTF A and B recommendations, current.

**Years and editions are deliberately omitted here** and are looked up at write time. A textbook
edition and a competency-document year both roll, and a reference list is the one place in the
document where a stale number is visible to the grader.

---

## Out of scope: the peer critique

Captured so it is not mistaken for part of the case study. It is a **separate deliverable**, one per
case study, **500 to 750 words**, under eight headings:

Clinical Assessment · Clinical Reasoning · Diagnostic Interpretation · Pharmacotherapeutics ·
Evidence-Based Practice · Preventive Care · Patient Education · Professional Practice.

**Minimum two scholarly references, within the last five years where possible.**

In the term this was captured from it was worth 5 points as a rubric line. **In at least one other
course it is a 100-point assignment of its own**, which is why it is named here rather than folded
in. Check which before assuming the weight.
