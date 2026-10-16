# The entry copy check never writes or deletes a copy

**Measured at:** a1c440906ee7d1594dd7bcb6e66a21d7d6e54f1b

[#1657](https://github.com/mshamblin5150-code/clinical-skills/issues/1657) was filed from the
independent Spec review and tracker sweep of #1477's implementation, 2026-10-09.
[ADR 0313](0313-a-leftover-refusal-mark-is-refused-only-in-the-entered-sections-and-an-estimated-input-is-disclosed-in-plain-words.md)
ruling 1 says a leftover-mark refusal removes any prior derived copy in the derive and `--check`
routes alike; #1477 was told to keep the existing lifecycle, and under `--check` that lifecycle
keeps the copy. Grilled 2026-10-16 against `main` at the commit above, where the freshness gate
read `FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this
is the record the build reads.**

## Measured before ruling

**The check treats the copy two ways.** Driven at the commit above, with a stale file already at
`entry-copies/<note>`: under `--check`, a clause that does not open its own sentence is refused and
the stale file is deleted; a `NOT CODED` mark typed bare in the Assessment is refused and the stale
file stays; a note the check passes leaves the stale file in place. The writing route deletes the
stale file on every refusal and overwrites it on success.

**Only one refusal was ever given the deletion.** `tools/entry_copy.py`'s `main` deletes the copy
under `--check` only for `RefusalGrammarError`, the class #1472 added for
[ADR 0307](0307-a-refused-code-clause-opens-its-own-sentence-and-its-semicolon-only-joins-two-clauses.md)'s
two rules. ADR 0307 says those refusals write no copy in both routes; it says nothing about deleting
one under `--check`. The Plan-label, leftover-mark, clinician-instruction, portal-character and
section-split refusals all keep it. `CLAUDE.md`'s **Medatrax Entry copy** section and
`skills/clinical-note/SKILL.md`'s welded-form paragraph describe the grammar deletion and credit it
to ADR 0307.

**The check was ruled to write nothing.** [ADR 0300](0300-the-entry-copy-refusals-run-before-the-go-ahead-and-a-changed-note-needs-a-new-word.md)
ruling 1 created the check-only mode as one that "runs every refusal it can raise and writes
nothing", and `skills/batch-shift/SKILL.md` step 7 and `skills/clinical-note/SKILL.md` still say
"This check writes nothing". [ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
ruling 1 ordered step 7 reworded to name the grammar deletion; on `main` that rewording is not yet
built. `approval_record.approve` calls `entry_copy.check`, which has never written or deleted a
file, so the approval backstop is untouched by all of this.

## Ruling 1 — the check-only mode never writes, replaces or deletes an Entry copy

`tools/entry_copy.py --check` leaves any file at `entry-copies/<note>` exactly as it found it,
whatever it refuses and whether or not it passes. The writing route is unchanged: it writes the
copy on success and, on every refusal, writes none and removes any prior derived copy. Every
refusal still exits nonzero in both routes and names its rule without quoting note text.

A stale copy is the risk any deletion would guard, and the check cannot guard it: once a note is
edited after its copy was derived, the copy is out of date whether the check passes or refuses.
The guard is the writing run required before entry, which already treats every refusal alike.
Keeping today's split, with only the grammar refusal deleting, was declined because two refusals
from one check would treat the file differently and every description of the check would have to
carry the difference. Deleting on the leftover-mark refusal too, as ADR 0313 wrote, was declined
because it moves the split rather than ending it. Deleting on every check refusal was declined
because it makes the check able to delete files while guaranteeing nothing a passing check does
not.

## Supersedes

- [ADR 0313](0313-a-leftover-refusal-mark-is-refused-only-in-the-entered-sections-and-an-estimated-input-is-disclosed-in-plain-words.md)
  ruling 1, its statement that the leftover-mark refusal removes any prior derived copy in the
  `--check` route. The narrowing to the four Note sections, the section-naming refusal, the
  whole-copy fallback and the removal in the derive route stand.
- [ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
  ruling 1, its instruction to reword batch-shift step 7's "This check writes nothing" to name a
  grammar-failure deletion. Under ruling 1 here the sentence is true as written and stays. A note
  pass running the check on its own note, and the orchestrating context's non-authoring run, stand.

## What this does not reach

Nothing here warns that a copy on disk predates the note's current bytes; the writing run before
entry stays the only step that brings the copy in line with the note. The refusals themselves, what
each reads and what each names, are unchanged. Preserved run records are not edited, and notes
already posted to Medatrax are not corrected.

## Build checklist

- `tools/entry_copy.py`: under `--check`, remove no file on any refusal.
- `tools/test_entry_copy.py`: the internal-semicolon and lead-in grammar refusals under `--check`
  keep a stale copy byte for byte; under the writing route they still remove it; the leftover-mark
  refusal under `--check` keeps it, as today.
- `CLAUDE.md` **Medatrax Entry copy** and `skills/clinical-note/SKILL.md`'s welded-form paragraph:
  say the writing route removes a prior copy on every refusal and the check removes none, and stop
  crediting a check-mode deletion to ADR 0307.
- `skills/batch-shift/SKILL.md` step 7: no change; #1596's build drops ADR 0380 ruling 1's
  step-7 rewording.
