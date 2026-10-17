# A repair scope is recorded before the file changes and only the clinician supersedes a failed comparison

**Measured at:** eee1fb8b97455bb1792c0476b5eaa1a01fdbf993

[#1804](https://github.com/mshamblin5150-code/clinical-skills/issues/1804) was filed from the
after-action review of a `batch-shift` run on 2026-10-14. On one shift, repair passes went out with
no permitted scope, two comparisons failed on correct content and could not be superseded, and
parallel passes were briefed inconsistently onto the run's one repair ledger. Its comments record
the same failed-comparison shape on each of the next two shifts, the second filed separately
as [#1815](https://github.com/mshamblin5150-code/clinical-skills/issues/1815). Grilled 2026-10-17
against `main` at `4dbf0795`, where the freshness gate read `FRESH`; the only change between that
commit and the one above is an unrelated ADR and glossary entry, so the measurements hold at both. The clinician ruled every
point below in that session, one question at a time. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The scope reaches the tool only after the pass.** `compare` takes `--scope` as an argument at the
moment it runs, which is after the pass has changed the file. [ADR 0294](0294-an-orchestrator-s-per-note-claims-and-every-repair-pass-are-derived-from-the-record.md)
ruling 4 and standing rule 6 already say the scope record is written before the pass, but nothing
the command receives distinguishes a scope written then from one chosen after the change was seen.

**A failed comparison has no way out.** `record_repair` appends every comparison before its verdict
is graded, and `completion_gate` counts every non-`pass` verdict as a broken chain. A later
comparison must start from the last recorded `after` digest, so it can record only a no-op, and
`place` refuses an already placed file. The only remaining route is editing `chain.json` by hand,
which the permission classifier refused on 2026-10-14 as audit tampering.

**`differential-verdicts` compares text, not verdicts.** For a note it retains the complete text of
each differential item; for a worksheet, `worksheet_grammar.differential_prose` retains the
differential region's clinical prose. The code says this is deliberate, because a closed verdict
vocabulary would miss an unknown verdict or its removal. Two of the three recurrences were edits that
changed no verdict, a one-character punctuation repair and a relabel, recorded under scopes that
omitted the population because its name says verdicts.

**The ledger is an unlocked read-modify-write file.** `place` and `record_repair` read
`chain.json`, change it and replace it whole. Two concurrent writers lose one update silently, and
the loss surfaces only as a broken chain at the terminal grade. On the next shift two passes attempted
`place`; they wrote nothing only because they gave relative paths and the command exited 2.

**An open pull request implemented the opposite of Ruling 2.** PR #1842, opened 2026-10-17 to close
#1815, adds `compare --rescope`, which lets the orchestrator re-record a failed pair under an equal
or wider scope and supersede the failure on its own judgment.

## Ruling 1 — the scope is recorded before the file changes, by the tool

A new `artifact_repairs.py begin <run> <file> --scope <scope.json>` runs before the orchestrator
sends a repair pass. It refuses unless the file's current SHA-256 ends its recorded chain, then
retains the before copy and records the scope. `compare` takes no `--scope`: it compares against
the copy and scope `begin` recorded, and with no open `begin` for the file it refuses with exit 2.
Standing rule 6 gains a sentence saying why `begin` comes first. The file snapshot is what makes the
order provable: once a pass has changed the file, `begin` can no longer succeed for it. A brief
template line alone was declined because the written rule already existed and failed on three
consecutive shifts. **This proves the scope preceded the change; it cannot prove the scope was wide
enough.**

## Ruling 2 — only the clinician's recorded acceptance supersedes a failed comparison

A failed comparison appears in the go-ahead's `REPAIRS` block, which ADR 0294 ruling 6 already puts
before the clinician. If the clinician accepts the change, a re-scope record cites the clinician's
reply, verified through `approval_record.verify_clinician_reply` as a bar signature is, names the
failed record it supersedes, and keeps both in the chain. `completion_gate` keeps re-measuring the
superseded record's retained evidence but no longer counts its verdict. Without that reply the
failure stands. The orchestrator's own wider re-scope, as PR #1842 built it, was declined: whoever
widens the scope has already seen what changed, so its judgment is the post-hoc scope Ruling 1
exists to stop. Leaving no route was declined because correct content would then block submission
or force a full rewrite, which is the trap that produced the hand-edit attempt.

## Ruling 3 — no preview; every comparison is recorded

`compare` gains no preview mode. #1815 and #1804's first comment asked for one so a
coordinator could test a scope before committing it; after Ruling 1 the scope is fixed before the
pass, so that use is gone. What a preview would still allow is seeing a pass's overreach, restoring
the snapshot and re-running the pass with nothing recorded, which erases the evidence ADR 0294 exists
to keep. A pass that changes something outside its scope therefore always leaves a failed record.
The clinician accepts it under Ruling 2, or the orchestrator restores the snapshot and starts a new
`begin`; the failed record stays in the chain either way. **How the gate reads a chain that returns
to an earlier file state is the build's to establish and test.** A logged non-grading preview was
declined as a third record kind for what this route already covers.

## Ruling 4 — the population is renamed for what it compares

`differential-verdicts` is renamed `differential-text`, and the measurement is unchanged for both
artifact kinds. `differential-item-text` was the name offered in the grilling; the worksheet branch
compares the differential region's prose rather than one item at a time, so the record takes the
name true of both. A ledger record written under the old name is still read under it, so runs in
progress keep grading. Documenting the old name was declined because the name is what the
orchestrator reads when writing the scope, and it misled two coordinators the same way. Narrowing
the measurement to verdict words was declined because it reopens the unknown-verdict gap the code
comment closes.

## Ruling 5 — passes never write the ledger, and every ledger write is locked

Standing rule 6's repair section says passes never run `artifact_repairs.py`; the orchestrator
places, begins and compares every returned file. `place`, `begin` and `compare` each hold the
existing `artifact_lock` exclusive lock across their read-modify-write, and a second writer is
refused with exit 2 and told to retry. The tool cannot tell a pass from the orchestrator, so the
lock does not enforce the brief line; it turns a pass that breaks it from a silent lost update into
an immediate refusal. The relative-path refusal stays, because it is the guard that stopped the
next shift's passes.

## Ruling 6 — PR #1842 closes unmerged and #1815 folds into this ticket

PR #1842 is closed unmerged with a comment citing this record, because its `Closes #1815` line would
close that ticket on the declined design. #1815 is closed as a duplicate of #1804, so one ticket
carries the build. The reproduction script in #1842's description becomes the build's first failing
test.

## Supersedes

- [ADR 0294](0294-an-orchestrator-s-per-note-claims-and-every-repair-pass-are-derived-from-the-record.md) ruling 5, the words "A broken chain, a failed comparison or a comparison never run is exit 1". A failed comparison superseded by a re-scope record carrying the clinician's verified acceptance no longer breaks the chain; an unsuperseded failed comparison, a broken chain and a comparison never run remain exit 1.

## Build checklist

- `tools/artifact_repairs.py`: the `begin` route; `compare` without `--scope`, reading the open
  `begin`; the clinician-accepted re-scope record and its gate handling; `differential-text` with
  the old name accepted only when reading existing records; `artifact_lock` around every ledger
  write; `DECLARED_LIMITS` rows for a scope recorded too narrow and for the brief line the lock
  does not enforce.
- `AGENTS.md` standing rule 6: the `begin` step and why it comes first, the renamed population, and
  the sentence that passes never run `artifact_repairs.py`.
- `skills/batch-shift/SKILL.md` and every other skill text that names the repair route or the
  population, and the go-ahead's `REPAIRS` block showing a failed comparison as awaiting the
  clinician's ruling.
- `CLAUDE.md`'s **Artifact repair chain** section, rewritten for the new route rather than copied.
- Tests drive, through the public command: #1842's reproduction; `begin` refusing a changed file;
  `compare` refusing with no open `begin`; a supersession with and without a verified reply; a
  restored snapshot followed by a new `begin`; a ledger under the old population name; and a second
  writer refused while the lock is held.

## What this record does not reach

- **A scope recorded too narrow.** Ruling 1 orders the scope before the change; it does not size it.
- **Whether a pass followed its brief.** The lock refuses a concurrent writer; it does not identify
  one, so a pass that runs `artifact_repairs.py` alone is not detected.
- **Whether the clinician's acceptance was informed.** The record proves the reply; the reading
  behind it is the clinician's.
