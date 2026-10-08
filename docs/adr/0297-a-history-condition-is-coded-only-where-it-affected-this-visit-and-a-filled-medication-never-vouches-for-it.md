# A history condition is coded only where it affected this visit, and a filled medication never vouches for it

**Measured at:** 5e7a622a55683ece10199e2b3fe34e40db9c8487

[#1447](https://github.com/mshamblin5150-code/clinical-skills/issues/1447) was filed from the
after-action review of a `batch-shift` run. The per-encounter writers put history-only chronic
conditions on each note's `Preexisting diagnoses` line as for-entry codes. In most notes of the
shift the blind descriptor-agreement read then found several of those conditions neither shown
unresolved nor addressed in the encounter; their only sign of activity was a filled home
medication. Four repair agents removed or replaced them after the notes were done. Grilled
2026-10-08 against `main`, where the freshness gate read `FRESH`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

Its sibling [ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md),
from [#1448](https://github.com/mshamblin5150-code/clinical-skills/issues/1448), is the write-time
mechanism; its ruling 6 left the clinical rule, the filled-medication corollary and their writer-side
statement to this record.

## Measured before ruling

**The committed rule was narrower than the official guideline.** ADR 0243 ruling 6 lets a history
agree with a present descriptor only while the note documents it "unresolved and addressed" in the
encounter. The FY2027 Official Guidelines, Section IV.J (printed page 114 of the CDC PDF the
`reference/icd10cm-guidelines-fy2027-coding-read.md` reading cites), read: *"Code all documented
conditions that coexist at the time of the encounter/visit and that require or affect patient care,
treatment or management. Do not code conditions that were previously treated and no longer exist.
However, history codes (categories Z80-Z87) may be used as secondary codes if the historical
condition or family history has an impact on current care or influences treatment."* Section IV.I
on the same page: *"Chronic diseases treated on an ongoing basis may be coded and reported as many
times as the patient receives treatment and care for the condition(s)."*

**The filled home medication is produced by the condition it was then read as proving.**
`skills/clinical-note/SOAP.md` rules that home medications are never deferred: a past-history
condition that ordinarily receives maintenance pharmacotherapy gets a compatible plausible regimen
when the shorthand is silent, declared under `FILLED·asserted`. The shift's evidence of activity was
exactly that line.

**Long-term drug codes reached filled lines.** `skills/icd10-cpt/SKILL.md`'s `Z79` section, which
carries ADR 0292 rulings 5 and 6, codes a drug the patient arrived on and states that a filled
medication line retains the ordinary `SOURCE: filled` disclosure. A filled anticoagulant therefore
earned `Z79.01` whether or not its indication was coded.

**Nothing grades open-status evidence.** `tools/anchor_scan.py`'s agreement read requires
`open_status_evidence` to be a nonempty string and reads nothing else in it. ADR 0296 ruling 1
names the consequence for a writer's self-grade: shared-reader blindness, so a writer that coded a
condition because of its filled medication will cite that medication and pass itself.

**The committed notes list the history on the line.** Each of the six `fixtures/slot-form-run`
notes carries between three and eleven codes on `Preexisting diagnoses`, counted as ` - ` followed
by a code on that line. Whether each would clear ruling 1 was not read. They are run records and are
not edited.

## Ruling 1 — a history condition is coded where it coexists and required or affected this visit's care

A condition from the patient's history takes a code naming it as present only when the note shows it
coexists at this encounter and required or affected this visit's care, treatment or management: it
changed a drug choice, was monitored, was treated, or its treatment was continued with a reason.
This is Section IV.J's wording. The same sentence governs personal-history and status codes, which
are coded only where the history or status affects current care. A condition closed in the past
agrees with a personal-history code only on that condition, or with nothing.

Keeping "active and addressed today" was declined because it is narrower than the official guideline
without a stated reason and could refuse a condition that visibly shaped a decision, such as chronic
kidney disease steering an analgesic away from an NSAID. Coding every condition the patient still
carries was declined because it contradicts IV.J's "require or affect" clause and is the defect the
ticket was filed over.

## Ruling 2 — filled reasoning earns a code only when it changes something concrete in this visit

Where the only evidence that a condition affected care is filled content, the condition is coded
only when that filled reasoning changes something concrete in this visit: a drug chosen or avoided
because of the condition, a dose adjusted, or a test or monitoring ordered for it. Such a code is
marked `SOURCE: filled`, as a code resting on a filled value already is. A filled home medication,
or a "continue home medication" line resting on one, never earns its condition a code.

Refusing all filled evidence was declined because it discards management the clinician performed and
did not write down, against his ruling that shorthand silence is not absence. Accepting any filled
Assessment or Plan line was declined because a writer can always add one, so ruling 1 would bite only
where a writer chose to let it. Whether filled reasoning is concrete rather than token is a reading.

## Ruling 3 — a filled drug earns its long-term-use code on the same terms

A long-term drug named in the shorthand keeps its `Z79` code under ADR 0292 rulings 5 and 6. A filled
drug earns one only when filled reasoning changes something concrete in this visit, under ruling 2;
for example, an anticoagulant held before a procedure. Leaving the `Z79` rule untouched was declined
because a code asserting long-term anticoagulant use would then rest on a drug the writer supplied,
the same loop ruling 2 closes, landing on a different code. Requiring the drug's condition to be
coded was declined because it joins two guideline rules on a link the guidelines do not make and
would strip a code a shorthand-named drug legitimately earns.

## Ruling 4 — the agreement grader refuses open-status evidence that lies only in a filled medication

When a history condition is claimed open, the agreement record's `open_status_evidence` is the
note's exact words, as `agreeing_words` already is. `tools/anchor_scan.py` reads the note's tier
block, and evidence lying wholly inside a filled home-medication item, or a "continue" of one, is a
finding. The check runs at ADR 0296's writer self-grade and at the batch blind read alike. Whether
filled reasoning that does lie outside such an item is concrete stays a reading.

Rule text with ADR 0296's self-grade and a by-eye line alone was declined because the self-grade's
blindness passes exactly this loop. A separate fresh reader at write time was declined because it
overlaps both existing reads and is still a reading that can be talked into the loop.

## Ruling 5 — the Preexisting line carries only qualifying codes

`Preexisting diagnoses (ICD10)` carries only codes that clear ruling 1. Every other past-history
condition stays in the past-medical-history narrative, uncoded. When nothing qualifies, the line
reads `None affecting this visit`.

Listing the non-qualifying conditions by name without a code was declined because it breaks the
line's every-item-carries-a-code shape and invites the next run to code them. A bare `None` was
declined because it reads as no preexisting conditions and contradicts the history above it.

## Ruling 6 — the rule is written once, in icd10-cpt

The rule is stated in `skills/icd10-cpt/SKILL.md`'s descriptor-agreement section, beside ADR 0296's
self-grade. `skills/clinical-note/SOAP.md` and `skills/clinical-note/HP.md` carry a pointer at the
`Preexisting diagnoses` heading and at the home-medication fill rule, and
`skills/batch-shift/SKILL.md`'s pass brief carries a pointer. None carries a second copy.

## Supersedes

- [ADR 0243](0243-descriptor-agreement-is-read-blind-against-the-note-and-the-index.md) ruling 6,
  its test "unresolved and addressed" for a history agreeing with a present descriptor, and its
  sentence that a closed history agrees with any personal-history code the index reaches. Rulings 1
  and 2 replace the test; a personal-history code now also needs the history to affect current care.
  The guard against agreeing a history with an acute code stands.
- [ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
  ruling 5, its reach to "A medication the patient takes long term" where that medication is filled.
  Ruling 3 narrows it; a shorthand-named drug is unchanged, and so is ruling 6's short-course rule.

## Consequences recorded as derived rather than ruled

- `tools/anchor_scan.py` requires `open_status_evidence` to be verbatim note text unless it is
  `none`, and joins it against the note's `FILLED·asserted` home-medication items. The agreement
  brief tells both the writer and the blind reader to quote it.
- `skills/icd10-cpt/SKILL.md`'s `Z79` section's sentence that a filled medication line retains
  `SOURCE: filled` is rewritten to ruling 3.
- `CONTEXT.md` gains **Coexisting condition**, and **Descriptor agreement**'s history sentence
  follows ruling 1.
- #1447's *Done when* is a synthetic note whose only open-status evidence is a filled home medication,
  failing the agreement read at a writer's self-grade.

## What this does not reach

Whether a non-medication filled line is a concrete change or a token one is a reading at both the
self-grade and the blind read. A condition the writer coded on given evidence that does not in fact
show it affected care is ruling 1's reading, not ruling 4's check. Whether the course rubric grades
`Preexisting diagnoses` as a comorbidity list was not established; the clinician ruled ruling 5 with
that fact unknown.
