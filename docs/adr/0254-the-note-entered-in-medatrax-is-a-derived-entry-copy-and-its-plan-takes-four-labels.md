# The note entered in Medatrax is a derived entry copy and its plan takes four labels

Ticket [#1342](https://github.com/mshamblin5150-code/clinical-skills/issues/1342) was filed after
the clinician read several `clinical-note` notes already posted to Medatrax and found two defects.
Refused codes with their official descriptors sat under the Differential, and the Plan carried
headings beyond the four he uses, such as `Oxygenation/bedside` and `Laboratory/imaging`. The
clinician ruled both in a grilling on 2026-09-17.

The first defect is the SOAP template working as written.
`skills/clinical-note/SOAP.md` places the welded `NOT CODED: <code> <descriptor>, <reason>` clause
inside the differential entry's rationale, and its worked example does so. `skills/clinical-note/HP.md`
keeps the Differential line bare and carries the refusal in Medical Decision Making. Both shapes
were entered in the portal. The second defect is a gap in both templates: each lists four Plan
headings, the two lists are spelled differently, and neither says its four are the only ones.

## Ruling 1 — the finished note keeps every refused-code clause

The welded clause stays in the finished note on both branches and in every section that carries it
today. `tools/differential_scan.py` reads it for drift row 22's slot limb, and the clinician's reason
for keeping it is that it helps the machine. Drift row 22 and that scanner do not change.

## Ruling 2 — the text entered in Medatrax is a derived Entry copy with every clause removed

What is entered in the portal is the **Entry copy**: the finished note with every
`NOT CODED: <code> <descriptor>, <reason>` clause removed, wherever it sits (a differential entry,
a Medical Decision Making item, or the `Final diagnosis` block), on both branches. The sentence
around the clause stays. The SOAP entry
`2. Pain in left elbow - M25.522: 5/10 pain after a fall, elbow radiographs ordered today to rule out a radial head fracture, no result. NOT CODED: S52.125A Nondisplaced fracture of head of left radius, initial encounter for closed fracture, nothing established it. Less likely.`
is entered as
`2. Pain in left elbow - M25.522: 5/10 pain after a fall, elbow radiographs ordered today to rule out a radial head fracture, no result. Less likely.`

Scoping the removal to the Differential alone was declined. The clinician's reason, that the clause
serves the machine and not a reader in the portal, holds wherever the clause is written, and a
Differential-only rule would leave the same clause in every H&P's Medical Decision Making.

## Ruling 3 — a committed command derives the Entry copy and refuses a surviving clause

The Entry copy is produced by a committed command from the finished note, never written by a run.
Two hand-kept copies of one note are how the copies come to disagree. The clause is cut at its own
bounds, which the welded form and its semicolon separator already fix. If any `NOT CODED` mark
survives in the output, the command writes no copy and exits non-zero. The portal readback in
`skills/clinical-note/SKILL.md` compares the saved note against the Entry copy.

## Ruling 4 — both branches use the H&P's four Plan labels and nothing else

Every Plan, SOAP and H&P alike, is organized under exactly these **Plan labels**:

```
Non-pharmacologic:
Pharmacologic:
Health Promotion/Patient Education:
Referral/Follow-up:
```

SOAP's `Nonpharm:`, `Pharm:`, `Education:` and `Follow up:` are retired. The H&P's opening sentence,
`Plan is decided upon by the preceptor, Non-pharmacologic, Pharmacologic, Health Promotion/Patient Education, Referral/follow-up`,
is removed from both templates because the labels themselves already say it.

No fifth label is written. Oxygen is placed under `Pharmacologic:`, because it is ordered and dosed
as a drug. Monitoring, positioning, and laboratory and imaging orders are placed under
`Non-pharmacologic:`; an order also stays on the Objective's `Labs/Tests today` line, which drift
row 18 already requires. Health promotion is placed under the education label and a referral under
`Referral/Follow-up:`. Keeping orders only in the Objective was declined because a reader of the
Plan alone could then not see that a workup was ordered.

## Ruling 5 — the Entry copy command refuses a label shape outside the four

The command from Ruling 3 refuses, writing no copy, when a Plan lacks one of the four labels or
carries a label shape that is not one of them. A label shape is a line in the Plan whose text
before its first colon is four words or fewer. A line with more words before its colon is read as a
sentence and passes. A short line that is not a Plan label is refused unless it is a declared
exception; the initial exceptions are `Sig`, `Dispense`, and `Refills`. The exception list grows
only when a real run is refused on a correct line.

Three designs were weighed. An exception list alone refuses ordinary sentences that end in a
colon, and no list can enumerate those. A length rule alone passes a sig-style line only by
accident of its length. The combination refuses short invented headings, lets sentences through,
and names its exceptions. The four-word cut was chosen so that the longer invented headings seen in
committed Plans, such as `Screening offered and reviewed today`, are still read as labels.

A read of the committed Plans under `fixtures/` and `skills/` informed the choice: extra headings
such as `Diagnostics`, `Orders`, `Return precautions` and `Immunizations`, sentences ending in a
colon such as `If the urine culture grows a pathogen`, and no line opening with `Sig`. That read used
a one-time matcher written during the grilling and is a floor, not a census; no figure from it is
load-bearing here, and the build's tests must measure the rule against the committed notes
themselves. A drift-matrix row is appended so a reader also walks the rule.

## Ruling 6 — the fix is forward only

Notes already posted are not corrected in bulk. When the clinician returns a finished note to the
run that produced it, that run relabels the finished note's Plan and derives a fresh Entry copy
with the command, which therefore has to accept a finished note from an existing run and not only
from a new one.

## Consequences

- The build touches `skills/clinical-note/SOAP.md`, `skills/clinical-note/HP.md`,
  `skills/clinical-note/SKILL.md` (the entry and readback steps and an appended drift row), and
  `skills/batch-shift/SKILL.md` where it follows the same entry procedure.
- The Entry copy is written where `tools/medatrax_posting.py`'s note populations do not read it.
  A standalone run's fingerprint requires exactly one top-level Markdown note, so a second top-level
  `.md` beside it would break completion.
- `SUBMISSION-SHA256` continues to bind the finished note's bytes; the Entry copy is a deterministic
  function of them.
