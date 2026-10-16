# A causal link the clinician never stated is never written and a complication code rests on the index or his words

**Measured at:** a22d9c58db035a2e5a2e4e17cd584c4189927079

[#1597](https://github.com/mshamblin5150-code/clinical-skills/issues/1597) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift. The clinician ruled every
point below on 2026-10-16, against `main` at the commit above, where the freshness gate read
`FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The recorded encounter was a paronychia in a patient with type 2 diabetes.** The note pass wrote
that the infection was a complication of the diabetes while coding the diabetes `E11.9`. The blind
agreement reader offered `E11.628` as a possible fit, the orchestrator ordered that recode, and the
author refused it on the ground that the only support for the link was the sentence the pass had
written. The author removed the sentence and kept `E11.9`. The repaired note then stated that the
two were not linked, which the clinician had not said either.

**The refusal was right, and the index shows why.** `python tools/icd10_lookup.py --index` reaches
no `Diabetes ... > with >` path from `paronychia` or from `cellulitis`, so no complication code was
available without the clinician's own words. The same trace does reach one for other acute
findings: `osteomyelitis` gives `E11.69` and `gangrene` gives `E11.52` under type 2 diabetes.

**The ticket's proposed batch-shift text conflicts with ADR 0292.** It read "never recode to the
complication the unsupported link implies". [ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
ruling 4 and the FY2027 Official Guidelines Section I.A.15, read in
[the committed source reading](../../reference/icd10cm-guidelines-fy2027-coding-read.md), presume
the link wherever the index joins two documented conditions with `with`, unless the note states they
are unrelated. Adopted as written, the proposed text would have required `E11.9` plus a separate
code for documented diabetes and osteomyelitis.

**The blind agreement reader runs in three skills and its findings are acted on in one.**
`clinical-note`, `batch-shift` and `icd10-cpt` all run the read. The instructions for acting on its
findings live in `icd10-cpt`'s *Descriptor agreement is a separate blind read*, which the other two
point to. The `with` combination rule already lives in `icd10-cpt` under *Linked conditions take the
`with` combination code*.

**An invented link coded consistently passes every current check.** The writer self-grade
([ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md))
and the blind read both test whether a code agrees with the note. Neither reads the clinician's
shorthand, so a pass that wrote the link and also coded `E11.628` would have agreed with itself.

**The case-study rule has the same conflict on its code clause.**
[ADR 0361](0361-a-case-study-s-differential-ranks-by-three-defined-standings-and-its-pre-review-walks-are-written-records-a-grader-shapes.md)
ruling 1 requires a step 3 claim record and a `### DEPARTURE:` entry for a causal link between two
listed diagnoses "or a code for the combined condition", with no exception for an index `with` path.

## Ruling 1 — the code follows the index, and a flagged link is removed before any recode

Where the index joins two documented conditions with `with`, the combination code is used whether or
not anyone wrote a link. Where it does not, the conditions keep separate codes unless the clinician
stated the link. When the agreement reader finds a code in conflict with a causal link the note
asserts, the pass first asks whether the clinician stated it. If he did not, it removes the
sentence, then recodes to the combination only where an index `with` path exists, and records that
path as the anchor. A complication code is never justified by prose the pass wrote.

The ticket's "never recode" was declined because it contradicts ADR 0292 ruling 4 and the guideline
on every presumed pair. The case-study wording was declined for notes because a real note has no
departure outlet and the wording still ignores the presumption.

## Ruling 2 — the note's prose never states a relationship the clinician did not state

A note never writes that one condition caused, complicated, or is unrelated to another unless the
clinician's shorthand or recorded answer says so. It lists the conditions side by side. A link the
index presumes is carried only by the code and by the worksheet's recorded index path. The
assessment entry's label may use the code's own official descriptor, because that wording is the
code's, not the pass's.

Allowing the combined name, such as "diabetic osteomyelitis", wherever the index presumes the link
was declined because it turns a coding convention into a clinical claim the clinician never made.
Forbidding only invented causation was declined because an invented "unrelated" defeats the
presumption under Section I.A.15 and would remove a correct combination code without anyone seeing
it.

## Ruling 3 — each half sits where its subject is already owned

Ruling 2 sits in `skills/clinical-note/SKILL.md`, beside its rules on what the encounter
establishes; `batch-shift` note passes already write notes by that skill. Ruling 1's remediation sits
in `skills/icd10-cpt/SKILL.md` *Descriptor agreement is a separate blind read*, which `clinical-note`
and `batch-shift` already defer to, cross-linked with *Linked conditions take the `with` combination
code*. `batch-shift` gets no new text.

The ticket's placement, `clinical-note` plus `batch-shift` step 6, was declined because a standalone
`icd10-cpt` run and a single-encounter `clinical-note` run act on the same reader. Copying both
halves into all three skills was declined as three hand-kept copies of one rule.

## Ruling 4 — a complication code records the source of its link

A code that joins two conditions records, in the worksheet's specificity reason, one of two link
sources: the index `with` path, which ADR 0292 ruling 4 already requires, or `clinician:` followed
by the shorthand's or recorded answer's own words stating the link. A code with neither source is
not proposed, and the conditions keep separate codes. Before the blind brief the orchestrator, the
one party holding the shorthand, compares every `clinician:` quote with the encounter's shorthand
or recorded answer.

A checklist item in the note pass's own pre-hand-back check was declined because the pass that
invented the link is the weakest reader of it. A grader over relationship phrases in the note was
declined because phrases such as "due to" are common in correct notes and no committed check reads
the shorthand beside the note.

## Ruling 5 — a case study's presumed combination code needs no claim record or departure

In `practicum-case-study`, a combination code the index presumes through `with` between two of the
clinician's listed diagnoses needs no step 3 claim record and no `### DEPARTURE:` entry; its source
is the index path, as in a note. A causal sentence between listed diagnoses still needs both, and a
combination code with no index path still needs both, exactly as ADR 0361 ruling 1 rules.

Leaving case studies as ruled was declined because every presumed combination would carry a
departure for ordinary coding, and a run that skipped the departure would submit the uncomplicated
code in a graded document. Deferring it to a separate ticket was declined because the contradiction
would stay on `main` until then.

## Supersedes

- [ADR 0361](0361-a-case-study-s-differential-ranks-by-three-defined-standings-and-its-pre-review-walks-are-written-records-a-grader-shapes.md) ruling 1,
  its words "or a code for the combined condition". Ruling 5 here exempts a combination code the
  index presumes through `with`. The causal-link clause and a combination code with no index path
  still need the claim record and departure.

## Consequences recorded as derived rather than ruled

- `skills/clinical-note/SKILL.md` carries ruling 2 with the paronychia and osteomyelitis cases as
  its worked contrast.
- `skills/icd10-cpt/SKILL.md` carries ruling 1's remediation and ruling 4's coordinator quote
  check in its blind-read section, which `batch-shift` and `clinical-note` already follow, and
  ruling 4's `clinician:` source beside *Linked conditions take the `with` combination code*.
- `skills/practicum-case-study/SKILL.md` narrows its causal-link paragraph by ruling 5.

## What this does not reach

Whether the clinician's words state a link, and whether a recorded index path applies to the
documented conditions, remain readings. No grader is claimed for an invented relationship sentence
or for a `clinician:` quote's fidelity; whether a grader can recognize the two link-source forms is
left to the build to measure. Preserved run records are not edited.
