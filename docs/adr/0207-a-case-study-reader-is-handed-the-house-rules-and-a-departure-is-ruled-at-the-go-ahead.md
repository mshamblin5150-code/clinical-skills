# A case study reader is handed the house rules and a departure is ruled at the go-ahead

[#1017](https://github.com/mshamblin5150-code/clinical-skills/issues/1017) was filed on 2026-09-10
out of the after-action review of one `practicum-case-study` run. It named three gaps in step 9 of
`skills/practicum-case-study/SKILL.md`, all about what a reader is given or asked to look for, and
three decisions behind a proposed diff.

Grilled 2026-09-13 to an empty frontier. **Five rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.

## What moved before the grilling

[#962](https://github.com/mshamblin5150-code/clinical-skills/issues/962), ruled by
[ADR 0194](0194-a-briefing-surface-declares-its-kind-and-points-at-standing-rule-6.md), replaced
the reader-brief paragraph the ticket's second hunk edited. Step 9's readers are **Second reader**
surfaces: with no second context the row stays incomplete and the document is not submitted. The
main-context serial fallback that hunk would have extended no longer exists, so its addition is
re-anchored against the current paragraph rather than applied.

The mechanical half of the propagation gap is
[#1019](https://github.com/mshamblin5150-code/clinical-skills/issues/1019), still open on its own
decisions. Nothing here settles whether a command can catch a leftover.

## Two claims the ticket carried that did not hold

**The 48-hour cap was ruled, and nothing recorded it.** The ticket says the orchestrator narrowed the
clinician's *"a few days"* of observation to 48 hours, *"disclosed that to the clinician, never
obtained a ruling, and submitted with it."* The clinician read the disclosure before allowing the
submission and agreed with it. What was missing was a record that the go-ahead covered the item,
which is why the review read an approved departure as an unruled one. Ruling 2 is shaped by that
correction: a separate stop was proposed and declined because the existing gate had worked.

**The two review passes are not two confirmations.** The #1014 sweep already recorded that the pass-2
extract carried the pass-1 dispositions as one entry, so *found by both passes* is one finding
re-read, not two independent ones.

## Ruling 1. Every step 9 reader is handed the house rules as settled context

Each step 9 reader receives the part of the skill above *Steps* — the skeleton, *Three modes*, the
wrapper-instruction rule, *Ordering*, *Tiers*, *Credentials*, *Voice* and *Conventions* — marked as
settled and never reportable as a defect. It still grades only the rule its row names; the settled
context tells it what not to report, and adds nothing for it to grade.

The recorded misreads were three: two credential strings reported as a contradiction, skeleton
heading punctuation reported as a style defect, and a severity axis proposed as a differential entry.

**The named minimum was refused on the evidence it was proposed from.** *Credentials* for the `Rx:`
and signature readers plus the skeleton and *Conventions* for layout readers covers the first two
misreads and not the third, so a list built from observed misreads misses the next one by
construction. **The whole file was refused** because the steps describe how the draft was produced,
and a reader holding the author's process is less independent than the Second reader kind requires.
The house-rules part is bounded by the file's own layout rather than by a list that has to be kept.

**Under ADR 0194 ruling 6 this is the surface's narrowing** — an addition to what the reader
receives, stated once at the surface, copying no shared rule.

**And *Credentials* gains the reason a reader cannot infer from the page.** The clinician, 2026-09-13:
*"I cannot prescribe as an RN I can as an FNP and I am currently in my last semester the reason the
FNP block exists are for the case study where I write that out in a table."* The section says the
prescription is written in the prescribing role the case study assigns, and never says that an RN
cannot prescribe. That sentence is what stops a reader from "fixing" the `Rx:` string toward the
signature string.

## Ruling 2. A departure is listed for the go-ahead, and the go-ahead rules on it

When a run narrows or departs from the clinician's instruction, the departure is listed on its own,
in plain words — what was instructed, what the draft says, and why — in a section of
`<run-directory>/proposed-<date>.md`, which the clinician already reads before submission. His
go-ahead after reading that list is recorded as his ruling on each item listed. There is no separate
stop and no mid-draft question.

The clinical-decisions reader reports every departure the run did not list, so that it reaches the
list rather than being repaired silently.

**Two stronger options were refused.** A per-item stop that a general go-ahead does not discharge,
and asking before narrowing at all, were both priced on Module 2's evidence — and the correction
above removed that evidence: the gate the clinician actually uses is reading before the go-ahead,
and it worked. What failed was the record, so the ruling repairs the record.

## Ruling 3. A choice may not meet the reason the draft used to reject an alternative

For every alternative the draft rejects and names a reason for — a care setting, a drug, a test or a
procedure — the clinical-decisions reader checks whether the option the draft chose meets that same
reason. It never judges whether the rejection was clinically right, which keeps the row inside its
existing prohibition on judging a dose.

**Care setting alone was refused.** The recorded instance is an observation stay planned long enough
to meet the length-of-stay criterion the draft used against inpatient admission. The same reading
applies to a drug rejected for renal function beside a chosen drug the same renal function excludes,
or a study rejected for radiation in pregnancy beside a chosen study with the same concern. A reader
told "care setting" skips those, while the evidence and the reading are identical.

**It joins the existing row rather than taking its own reader**, because it reads the same evidence
— the faculty material and the whole draft — and the skill separates readers only where the evidence
differs (#306's decision 2). That row's substantiated `clean` names the rejections and departures it
walked, beside the orders and wrapper instructions it already names.

## Ruling 4. Every change after the first draft is carried everywhere and re-read by a non-author

Every change after the first draft — a reader's repair or the clinician's own revision — is carried
to every section that restates the instruction, figure, pointer, care setting or other content it
changed. Then a context that did not make the change is told what changed and reads the whole draft
for leftovers of the old version before the check is recorded `clean`. One read covers one round of
changes, not one change.

**Step 9 repairs alone was refused**, because most of Module 2's leftovers came from the clinician's
mid-run care-setting change rather than from a reader's repair: an MDM entry still arguing from the
old setting, an education item contradicting the two after it, and three smaller ones. **The run's
own "carried through every section" was refused as the check**, because it was reported twice in one
sitting and was wrong both times. This is standing rule 6's *a fresh non-authoring context checks
the correction again*, applied to propagation.

**The re-read is its own fixed row of step 9's check table**, so a round that never received it
leaves a prewritten heading with no verdict. It substantiates its `clean` by naming the changes it
walked, and on a run with no change after the first draft the `clean` says so. The row name is the
build's to fix in `checks_ledger.EXPECTED_CHECKS`, `SUBSTANTIATED_CLEAN` and the table together.

## Ruling 5. A care-setting or disposition change is restated and confirmed before it is propagated

When the clinician changes a care setting or disposition, the run restates it in one sentence in
exact terms — for example *"hospital outpatient observation status, not inpatient admission, for a
few days"* — and waits for his yes before carrying it into any section.

In Module 2 *observation* was read first as an inpatient admission and then as daily office
follow-up, and each wrong reading cost a full propagation pass that left stale copies of the reading
it replaced. **It does not contradict ruling 2**: ruling 2 is about the run changing his
instruction, and this is the run confirming it understood his instruction before rewriting around
it. **Every change was refused as the scope** because it would ask for confirmation of a typo fix.

## What this record does not settle

- **Whether a reader read the settled context.** A well-formed verdict cannot show which inputs a
  reader used; `checks_ledger.NOT_REACHED` already declares that ceiling for the draft itself.
- **Whether a leftover is mechanically detectable.** That is #1019's.
- **Whether other skills' Second readers need the same settled context.** Their readers were not
  measured here, and the ruling is scoped to `practicum-case-study` step 9.
