# The entry copy refusals run before the go-ahead and a changed note needs a new word

**Measured at:** dae512ff969c4eb8b3eaf44f211c11990eae910b

[#1458](https://github.com/mshamblin5150-code/clinical-skills/issues/1458) was filed from the
after-action review of a `batch-shift` run, and carries the duplicate #1451 from the same shift.
The shift's go-ahead was recorded through `approval_record.approve`, whose pre-post grader passed.
`tools/entry_copy.py` then refused one note because its Assessment carried a clinician-directed
instruction. Removing the clause changed the note bytes, which voided the approval fingerprint, so
the downstream gates, the Review sheet and the approval were run again, and the second approval was
recorded under the standing go-ahead without a new word from the clinician. Grilled 2026-10-08
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in
that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Both skills approve before the Entry copy exists.** `skills/batch-shift/SKILL.md` calls
`approval_record.approve` at the Review-sheet go-ahead and runs `entry_copy.py` afterward;
`skills/clinical-note/SKILL.md` has the same order. No pre-approval grader imports `entry_copy`.

**Every refusal the Entry copy can raise is computed by one function that writes nothing.**
`entry_copy.derive` raises on an invalid Plan label set, a surviving `NOT CODED` mark, a
clinician-directed instruction, and an unmeasured portal character. Only `main` writes the copy.

**The Entry copy passes a note that form sections then refuses.** `_portal_characters` accepts a
plain-ASCII copy that `note_grammar.parse` cannot split, on the ground that form sections refuses
that shape later. Driven on `main` with a plain-ASCII note carrying only Assessment and Plan,
`entry_copy.py` exited 0 and `form_sections.py` on the derived copy exited 2.

**The approval step is shared by every posting skill.** `approval_record.approve` serves the
coursework skills as well as the two note skills, and reads its approved notes from `sources`.

## Ruling 1 — a check-only mode runs before the Review sheet, outside the writing pass

`entry_copy.py` gains a mode that runs every refusal it can raise and writes nothing. After every
note is final and before the Review sheet is built, the orchestrating context runs it over every
note; a refusal is corrected before the Review sheet exists. The writing pass never runs it on its
own output, by `AGENTS.md`'s rule that authors do not check their own generated artifacts. The
writing run after approval is unchanged. Running the writing command early was declined because it
puts derived patient text on disk before approval, where a later note change leaves it stale.
Folding the check into the approval grader alone was declined because the refusal would still
arrive after the clinician has read the whole Review sheet. Having the note writer avoid the shapes
was declined because nothing would check.

## Ruling 2 — the check-only mode also requires the four-section split

In that mode the note must also split through `note_grammar.parse`, the parser form sections uses,
so a plain-ASCII note that cannot be split is refused rather than passed. `form_sections.py` and
its private record stay after approval. Running form sections before the Review sheet was declined
because it needs the derived copy on disk and writes its record before the content is approved.
Leaving the split to form sections alone was declined because it keeps this ticket's defect for one
class of shapes.

## Ruling 3 — standalone `clinical-note` takes the same check before its go-ahead

[ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)
ruling 1 makes a standalone `clinical-note` run a one-encounter batch under the same go-ahead, and
its skill has the same order, so it runs the check-only mode before the note is shown for approval.

## Ruling 4 — a change to an approved note needs a new explicit word

Once a note has been approved, any change to its text is shown to the clinician as the exact change
and is re-approved only on the clinician's new explicit word. The standing go-ahead never covers a
re-approval. This extends ADR 0223 ruling 7's stop on a change to a note to the interval before
entry. Allowing a deletion of text the Entry copy would refuse or strip was declined because the
agent making the edit would also be classifying it. Letting the standing go-ahead cover any
re-approval was declined because the approval would stop meaning these exact notes.

## Ruling 5 — the approval step runs the same check as a backstop

For `batch-shift` and `clinical-note`, `approval_record.approve` runs the check-only mode over every
note in `sources` and refuses to record the approval when any note fails. A skipped early step
therefore refuses before anything is recorded or entered, rather than voiding an approval. Relying
on the written step alone was declined because a skipped step reproduces the recorded run.

## What this does not reach

Ruling 4 is not mechanical: `approve` cannot tell a new word from the clinician from an agent
calling it again, so the rule binds the skill text and the run that follows it. The backstop checks
only what the Entry copy and the four-section split can refuse; a form-sections refusal about its
own stored record still arrives after approval, by ruling 2. Whether the note's content is
clinically right remains the clinician's reading at the go-ahead.
