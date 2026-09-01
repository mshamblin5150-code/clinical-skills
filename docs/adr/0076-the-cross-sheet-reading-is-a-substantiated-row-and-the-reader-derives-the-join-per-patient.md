# The cross-sheet reading is a substantiated row and the reader derives the join per patient

[#584](https://github.com/mshamblin5150-code/clinical-skills/issues/584) is the boundary
[ADR 0057](0057-the-corpus-sweep-is-comprehensive-and-every-ruling-it-needs-is-already-ruled.md)
ruling 9 declared and did not close: population and quantity keys are sheet-local, `CONFLICT` is
within-sheet, `--all` iterates sheets independently, and **nothing compares two sheets** — so the
KDIGO/AHA pair the population-in-the-key ruling was made about is the pair the mechanism never
sees. [ADR 0064](0064-a-threshold-sheet-s-sources-are-not-joined-to-its-topic-because-the-catalog-cell-is-the-guideline-s-wording.md)
sharpened it: the sheet unit is the **catalog topic** cell, so one clinical subject is several
sheets by design, and its Consequences named the prerequisite — nothing in this repo derives which
catalog cells are one clinical topic, so a cross-sheet gate has no committed grouping to iterate
over.

Grilled 2026-08-30. **Four rulings, made by the clinician on that date.** Nothing is built here;
this is the record the build reads. The ticket's two standing rejections — a directory-wide
population vocabulary, and a similarity threshold — were not re-opened and stay rejected on
ADR 0057's and ADR 0064's grounds.

## Ruled 2026-08-30

**1. The cross-sheet reading joins `SUBSTANTIATED_CLEAN`.**

The ticket's argument against was that no run in the tree has ever joined two sheets, so there is
no false-alarm rate to ground the requirement on. That objection is answered rather than
overridden: it belongs to **graded thresholds**, where a firing bar refuses an honest run —
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s territory — and this is
not a bar. The cost of requiring substantiation is one sentence a reader writes.

And the measurement that does exist cuts the other way. The zero-or-one-sheet run is the **common
case**, so a bare `clean` on this row would be a stock pass on nearly every run — the
unfalsifiable shape [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255)
exists to refuse, arriving as the row's ordinary state rather than its failure. Substantiation is
what makes the common case honest: *"walked coverage.md; the draft rests on hypertension.md alone
— no second sheet joined"* is checkable by eye, and distinguishes a run where no join happened
from a run where nobody looked. Without it the two are one string.

The marginal cost is one tuple member:
[ADR 0070](0070-a-four-row-limits-object-takes-the-enumerated-skill-bind-the-sibling-s-size-refused.md)
records that the report already prints the `SUBSTANTIATED_CLEAN` list and the `not graded for it`
count on every run.

**2. The reader derives the join itself, and a run-recorded strike list is refused.**

The reader is handed the Markdown draft, the faculty material's patient, and
`reference/thresholds/` via `coverage.md` — it identifies which sheets' topics this patient's
problems touch, opens them, and reads whether every sheet the draft rests on applies to this
patient. This is step 9's own qualification — *a fresh reader given the draft and the rule and
nothing else* — applied to the one reading nothing else reaches.

The refused alternative was step 3 bookkeeping: the run records which sheets covered struck
claims, and the reader grades against that list. Refused on
[ADR 0001](0001-fixture-asserts-on-named-findings.md)'s grounds — the run grading its own record
is a baseline, not a verification. A run that silently drew from a sheet it should not have
writes a list that omits it, and a reader graded against that list never opens the sheet that
would catch it. Independent derivation **is** the verification. The claims ledger was not a
candidate at all: it holds the researched residue, so the sheet-backed thresholds — the row's
whole subject — are exactly what it does not contain.

This also answers ADR 0064's named prerequisite without building it: the grouping this row needs
is **per patient**, made by the reader from the patient in front of it, so no committed
clinical-topic grouping is required. **That refusal is scoped to this row.** A future mechanical
cross-sheet `CONFLICT` would need the committed grouping ADR 0064 says does not exist, and
nothing here forecloses building one; what is ruled is only that this reading does not wait for
it.

**3. The row is `the threshold sheets against this patient`.**

Named on `the dose against the record that sourced it`'s pattern — what is read and what it is
read against — and deliberately not in this ticket's own vocabulary: *cross-sheet* and *join* are
the mechanism's words, not a reader's. The step 9 table row:

> **What it reads:** the whole draft, the faculty material's patient, and `reference/thresholds/`
> via `coverage.md`, including its `subject` column.
> **How:** a reader: group the registry's rows by subject, and where the patient's problems touch
> any cell in a subject, open every sheet in that subject; `?` means nobody has ruled whether that
> cell has siblings, never that it has none. Where the draft rests on rows from more than one sheet,
> decide whether each sheet's own population wording holds for **this** patient — population and
> quantity keys are sheet-local, `CONFLICT` is within-sheet, and no command compares two sheets, so
> this pair is seen by nobody else.
> **A `clean` says what it walked:** yes.

Scope is the join. Single-sheet threshold applicability in general is a different reading and is
not widened into this row.

**4. The README declaration points, never copies, and the test binds three surfaces.**

`reference/thresholds/README.md` states the three required claims — keys are sheet-local,
`CONFLICT` is within-sheet, and a clean `--all` is **not** a claim the directory is internally
consistent — plus one pointer sentence for the why (the sheet unit is the catalog topic cell, so
one clinical subject may be several sheets; see ADR 0064 and `CONTEXT.md`'s **Topic** and
**Catalog topic**), restating neither record. And it **names the row**, because the ticket's own
prohibition — reading the declaration as the fix — is answered by the declaration pointing at the
thing that looks.

Naming the row in a third file is a rename-rot surface, so the end-to-end test binds **three**
surfaces rather than the ticket's two: the README's mention, the step 9 table row, and the
`checks_ledger.EXPECTED_CHECKS` member. The Rx-blocks arrangement — *the chain is asserted end to
end rather than described* — at one more surface. If the row is ever renamed or dropped, the
README's claim that somebody looks fails a test instead of standing false.

### The collision is recorded and no ordering is imposed

**Ruled: no imposed ordering.** Chaining this ticket behind another has no structural need — every
append is name-keyed, and the position lesson is already learned
(`test_the_two_reference_rows_are_not_one_check` finds rows by property after an index broke it).
Each build appends by name, no test keys on count or position, and a textual conflict in the
shared region resolves by union — the loud direction;
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s trap is the silent
merge.

**Corrected in place 2026-08-30, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. The ruling is unchanged; two facts it was
recorded with were wrong, and both were wrong in the direction that under-states the hazard.**

This paragraph first described a **three-way** collision between #584,
[#587](https://github.com/mshamblin5150-code/clinical-skills/issues/587) item 6 *(blocked on
[#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483))*, and
[#565](https://github.com/mshamblin5150-code/clinical-skills/issues/565)/ADR 0070. Re-derived:

1. **#587 item 6 is not blocked.** That ticket's own *Sequencing* reads *"Items 1, 2 and 6 are
   independent of #483"* — only its items 3, 4, 5 and 7 wait. So the colliding item is **live
   today**, not deferred, and the parenthetical was the ground the no-ordering ruling leaned on
   most heavily. The ruling survives on its other ground — name-keyed appends — and the merge-safe
   discipline matters *more* than recorded, not less.
2. **#565 touches neither `EXPECTED_CHECKS` nor the check table.** Its body names `EXPECTED_CHECKS`
   zero times; ADR 0070 names it zero times. Ruling 4's step 9 surface is a **prose enumeration of
   `NOT_REACHED` sentences** in the checks-ledger block, some 230 lines below the check table, and
   its module edits are `DECLARED_LIMITS`, the docstring and the `outside the table` report label.

So the textual collision is **two-way — #584 against #587 item 6 — on both files**, and #565 is a
file-level neighbor with disjoint regions that merges cleanly against either. Checked for a
silent-merge hazard from #565 landing beside them and found none: its row count is over *prose
limits*, which an `EXPECTED_CHECKS` member is not, and `SUBSTANTIATED_CLEAN`'s size is stated in no
prose.

**Both errors were introduced by this record's own author and caught by the finishing sweep the
same day**, which is the argument for the sweep rather than for the ruling: a collision recorded
one claimant too wide and one blocker too many reads as *handled* exactly like one recorded
correctly.

## What must not come out of this

**A directory-wide population vocabulary or a similarity threshold.** Still rejected; the
grilling did not re-open either.

**A committed clinical-topic grouping built for this row.** Ruling 2 needs none. If one is ever
built it is for a mechanical cross-sheet gate, on its own ticket, and this record does not
foreclose it.

**Widening the row to single-sheet applicability.** Ruling 3's scope clause.

## Declared limits

**Ruling 1 buys a shape, never a reading** — a stock substantiation clause satisfies it, which is
`SUBSTANTIATED_CLEAN`'s standing R2 limit inherited whole.

**Ruling 2's reader can be wrong about the join.** Which sheets a patient's problems touch is
itself a reading; a reader that misses a sheet reports a smaller join, and nothing mechanical
counts the true one. That is the ticket's assignment working as designed, not a gap a later
mechanism has been promised for.

**The three-surface bind proves the names agree, never that any verdict is true.**

## Consequences

[#584](https://github.com/mshamblin5150-code/clinical-skills/issues/584) is respecced for a build
drone and moves from `grilling` to `ready-for-agent`: Done-when item 3 is dropped as already
discharged (`CONTEXT.md`'s entries carried the sheet-local wording from ADR 0057's record commit
`66ba77f`), the stale 149/407 figures become the command's to state, and the two moved line
anchors are replaced with symbol-level ones. Cross-reference comments on #587 and #565 record the
collision.

*(Corrected in place 2026-09-01, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. ADR 0102 and #689 added the registry's authored `subject` column after this row was ratified. Ruling 3's quoted reader contract now includes the column, its group-expansion walk, and the meaning of `?`; the row name, reader, population judgment, and other rulings are unchanged.)*
