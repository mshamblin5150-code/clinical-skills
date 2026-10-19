# Every recursive walk in tools adopts the shared walk or is a named exception and each walk's verdict fails closed on a folder it could not read

**Measured at:** a595ac98d7df59a35f92bff9dffc5874c380e48d

[#1896](https://github.com/mshamblin5150-code/clinical-skills/issues/1896) was filed from the
tracker sweep closing [#1841](https://github.com/mshamblin5150-code/clinical-skills/issues/1841)'s
grilling. [ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md)
ruled on the walks #1841 named, and its own *What this does not reach* says that list came from the
ticket rather than from a census of `tools/`. A census of the code then found thirteen more
functions with the same two gaps: each enters a Windows junction, and each skips a subdirectory it
cannot list with no error and no count. Grilled 2026-10-19 against `main` at `a4bceb36`, where the
freshness gate read `FRESH`. The commit above is `main` after it, which adds only ADRs 0429 to 0431
and their glossary entries and touches no file under `tools/` or `skills/`, so every code reading
below holds there. The clinician ruled every point below in that session, one question
at a time. **Nothing is built here; this is the record the build reads.**

## Supersedes

- [ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md)
  ruling 4, the words "`checks_ledger.DECLARED_LIMITS` states that its submission lookup refuses
  on both junction shapes, does not terminate on an ancestor junction, and accepts the one visible
  document when a second same-name document sits beneath a folder it cannot list." The submission
  lookup now adopts the shared walk and refuses over a folder it could not open (ruling 2 here), so
  the limit row is retired whole. `aar_scan`'s adoption and the `skills_mirror` comparison rows
  stand.

- [ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md)
  ruling 4, the words "`run_relevant_paths` needs no limit". The function adopts the shared walk
  (ruling 10 here).

That second decision rested on a ground that was false when written: ADR 0416 says the function
walks a tracked tree, and at its measured commit it already walked `skills/` on disk. Under
[ADR 0390](0390-an-overturned-passage-with-no-ruling-number-is-located-by-its-exact-quote-and-a-repair-s-mislabeled-opening-is-restored.md)
ruling 3 the false ground is an [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
correction. It is recorded here and not in ADR 0416: a correction line there is not
supersession-only maintenance under [ADR 0334](0334-supersession-only-adr-edits-preserve-the-historical-measurement-base.md),
so the staged measurement check refuses it against ADR 0416's historical base. ADR 0416's sentence
and its measured table row keep the false words.

## Measured before ruling

**The population was re-derived from the code at the commit above**, first by a subagent and then
by a direct search for `.rglob(`, `os.walk(` and `**` glob patterns in non-test `tools/*.py`. There
are 23 walk sites. ADR 0416 rules on eight of them. The other fifteen are the thirteen functions
#1896 lists, which hold fourteen sites because `coursework_run.draft_files` holds two walks, plus
`spelling_scan.markdown_under`, which #1896 names as having no caller. No `glob.glob(recursive=True)`
and no hand-written directory recursion exists. The shared walk module of ADR 0416 ruling 3 is not
built, and `skills_mirror._is_link` is still the only link test in `tools/`.

**What each account-tree walk's silent drop changes, read from the code:**

| Walk | What its result decides | What an unlisted folder does today |
|---|---|---|
| `run_status_stop_hook._changed_after` | whether a named run is touched, and so whether a reply owes its `Run status:` line | the run reads untouched and the hook lets the turn end; the `except OSError` also returns untouched |
| `tracker_publish_hook._quotes_run_material` | the AAR quotation gate's deny | the gate allows a body it never compared; a file whose read raises is also skipped uncounted |
| `coursework_run.draft_files` | the first draft observation, kept forever, which the completion grade fails on | a draft beneath it is never observed, so the grade passes |
| `reference_class_census.read_root` | its counts and an exit 2 on an unreadable root or document | uncounted; neither existing unreadable line moves |
| `spelling_scan.files_under` | the folder-mode clean line and exit status | uncounted, so the clean line claims the whole folder |
| `skills_mirror.run_relevant_paths` | which cited tools the session-start **Base distance** line counts | the line undercounts with nothing printed |

`spelling_scan.read_file` lets an `OSError` escape on a file it cannot open, so folder mode exits 1,
the scanner's status for a finding, through a traceback. `run_relevant_paths` walks `skills/` on
disk, not Git's index, so ADR 0416's ground for leaving it alone ("a tracked tree; Git holds no
junction") does not hold of the code. Its read failure already prints
`NOT ESTABLISHED: run-relevant path-set read failed` on the session-start base line.

**Only tests call `markdown_under`.** Both callers are in `tools/test_spelling_scan.py`, so those two
tests grade a walk the command never runs.

## Ruling 1 — one rule for the whole population, enforced by a suite test

Every recursive walk in non-test `tools/` goes through ADR 0416's shared walk, unless it is named in
an exception list with its reason. The list lives as one object in the shared walk module, beside its
`DECLARED_LIMITS`. A suite test reads the code and fails on any recursive walk outside the module
that is not on the list. Its docstring states that the test is a floor on the walk shapes it
recognizes: a walk assembled by indirection is invisible to it.

**Ruling on each walk one at a time, with no test, was declined**, because the next walk would arrive
the way these thirteen did, by being missed from a list written from a ticket. **Declaring all of
them as limits was declined**, because two of them feed refusers.

## Ruling 2 — the submission lookup adopts the walk and refuses over a folder it could not open

`checks_ledger._submission_document` walks `output_root()` through the shared walk. When any
subdirectory could not be listed, it refuses with its existing `SourceError` (exit 2), naming the
count and never a folder. A link is not entered, so a document reachable only through one reads as
no match. This retires the wrong-document limit row ADR 0416 ruling 4 placed in
`checks_ledger.DECLARED_LIMITS`.

The accepted cost is that one unopenable folder anywhere in `output/` blocks the posted-reading
check for every submission until it is fixed. **Refusing only when exactly one match was found was
declined** as the same outcome in more words, since zero and two matches already refuse. **Keeping
the declared limit was declined** because the lookup exists to prove exactly one document, and it
cannot prove that over folders it did not read.

## Ruling 3 — the eight guideline-corpus walks adopt the walk on ADR 0416 ruling 2's terms

`guidelines_build._files`, `guidelines_extract._run` and `orphaned_outputs`,
`guidelines_index._sources`, `guidelines_manifest._read_locked`, `guidelines_recs.build_sweep` and
`compare_reader_corpus`, and `split_census._pdfs` use the shared walk. An unopenable subdirectory
makes the command exit 2. A link not entered is printed as a count on every run, zero included, and
never changes the status. A society folder reachable only through a link stops being read.

**An exception for all eight was declined**: the build identity is a fingerprint over the files
found, so a corpus missing a folder gets its own clean fingerprint and publishes as complete, and
every threshold sheet and search reads it. **Adopting the walk only in the producers was declined**,
because a diagnostic would then report figures disagreeing with the build's with nothing printed to
say why.

## Ruling 4 — `markdown_under` is deleted

`spelling_scan.markdown_under` is removed. Its two tests are rewritten to drive the command's folder
mode, which walks through `files_under`. The first test's claim that nothing but Markdown is collected
changes to what the command does: it reads every file. The #321 behavior those tests protect, a run
folder never being read as the preserved run record, belongs to `run_record_for` and stays tested.

**Adopting the walk in it was declined** as giving a walk that grades nothing its own tests, while
the tests kept certifying a path the command does not take. **An exception entry was declined**
because the list would then excuse dead code rather than a walk with a reason to differ.

## Ruling 5 — the Stop hook counts a run it could not fully walk as touched

When `_changed_after` cannot establish that nothing under a named run changed, the run is touched:
an unopenable subdirectory, or any read error during the walk, makes it touched. The usual
`Run status:` rules then apply, including the `stopped` line that
[ADR 0422](0422-an-unreadable-tool-written-run-record-is-never-read-as-empty-and-a-damaged-freeze-record-is-left-untouched.md)
ruling 2 requires for a damaged approval record. A link is not entered and changes nothing, and the
hook's limits object declares that, because a Stop hook has no report to print a count in.

The accepted cost is that a run with a permanently unopenable subdirectory demands a status line on
every turn that names it. The demand can always be met, since `stopped - <reason>` is a true
statement about any run. **Keeping "untouched unless a visible file changed" was declined** because
that is the case the hook exists to catch. **A system note only was declined** on ADR 0422 ruling 2's
ground: the reply would carry no status line and the agent could treat the run as finished.

## Ruling 6 — the AAR quotation gate refuses over run material it could not read

`tracker_publish_hook._quotes_run_material` walks the AAR run through the shared walk. When any
subdirectory could not be listed, or any file it would compare could not be read, the gate denies the
publication. The refusal names how many subdirectories and files were unread, never their names, and
says to restore read access and retry. A link is not entered; its count goes on the gate's existing
report line and does not deny.

This applies [ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)'s
rule for this hook, that what it cannot read it refuses, to the material it compares against as well
as to the publication itself. **Allowing with the counts printed was declined**, and so was a declared
limit, because a published tracker body cannot be withdrawn: GitHub keeps every revision.

## Ruling 7 — the draft walk refuses before it records an incomplete first observation

When `coursework_run.draft_files` could not list a subdirectory, the command that takes the first
draft observation exits 2 and stores no observation. Those commands are `project_context.py --write`
and the voice-model identity write. Its message gives the count and says to restore access and rerun.
A link is not entered; its count is printed at write time and not stored, so the observation's
recorded shape is unchanged and older observations need no legacy reading. Both walk sites in the
function, the run-directory glob and the session-folder walk, follow this ruling.

**Recording the observation with an unread count and grading it `not graded` was declined**, because
the first observation is never retaken, so the run could never grade clean even after the folder was
fixed. **A declared limit was declined** because a run that drafted before the gate would pass.

## Ruling 8 — the reference-class census counts unreadable subdirectories on their own line

`reference_class_census.read_root` uses the shared walk. A `subfolders unreadable` line prints beside
the existing `roots unreadable` and `candidate documents unreadable` lines, and a nonzero count exits
2 on the same terms. A finding still exits 1. Links are not entered, so a document beside a live
junction to its own folder is counted once, and a `links not entered` line prints on every run, zero
included, without changing the status.

**Following links with deduplication by resolved location was declined**, as ADR 0416 ruling 1
declined it for the sweep. **Folding the count into `roots unreadable` was declined** because one
figure would then mean two things.

## Ruling 9 — the spelling scan's folder mode counts what it could not read and exits 2

In folder mode, an unopenable subdirectory and a file `read_file` cannot open enter one printed
unread count, and a nonzero count exits 2. A finding still exits 1, with the count beside it. A link
is not entered, and a `links not entered` count prints on every folder-mode run without changing the
status. The staged, `--all`, `--record` and commit-message modes are unchanged. This also ends the
traceback that exits 1 on an unreadable file.

**Counting but keeping exit 0 because spelling is advisory was declined.** Advisory describes what
the hooks do with the status, not a license for the status to overclaim, and the hooks use other
modes.

## Ruling 10 — `run_relevant_paths` adopts the walk and either gap leaves the base line not established

`skills_mirror.run_relevant_paths` walks `skills/` through the shared walk. An unopenable
subdirectory **or** a link not entered makes the session-start base line read `NOT ESTABLISHED`, with
the reason wording the line already uses for a failed read. A link counts here, unlike in every other
consumer, because an instruction file behind one is a cited tool the line would otherwise silently
omit, so the line would understate how far behind the checkout is.

**Making only an unopenable folder count was declined** for that reason. **An exception entry was
declined** because its reason, that the walk reads a tracked tree, is false of the code.

**This ruling governs the walk while it is a disk walk.** [#1914](https://github.com/mshamblin5150-code/clinical-skills/issues/1914),
open as this was recorded, decides which population the path-set read covers: the tracked files
under `skills/` or every file on disk. If it chooses the tracked files, the recursive walk leaves
`tools/` and this ruling has nothing to govern; that record then marks it. Per-file decode failures
are #1914's, not this record's.

*Superseded 2026-10-19.* The words "`skills_mirror.run_relevant_paths` walks `skills/` through the shared walk." are superseded by [ADR 0435](0435-the-base-line-reads-the-files-git-lists-under-skills-and-a-file-that-is-not-clean-utf-8-is-read-with-replacement-and-counted.md) ruling 1. The function reads the files Git lists under `skills/`, tracked or new but not ignored, and holds no recursive walk, so this ruling's link and unopenable-folder postures have nothing to govern. Every other ruling here stands, and #1896's build no longer converts the function.

## Ruling 11 — the exception list holds only the mirror comparisons

The exception list starts with `skills_mirror`'s copy-stale comparison over the canonical skills and
the mirror. It enters junctions on purpose, because the mirror is made of them, and ADR 0416 ruling 4
already declares it in `skills_mirror.NOT_REACHED`. The session-start comparison, ordered by ADR 0407
and re-premised by [ADR 0426](0426-a-desktop-worktree-session-is-served-the-main-checkout-s-skills-so-the-main-checkout-is-fast-forwarded-at-a-worktree-session-s-start.md)
ruling 3 (built under #1806 and #1879), joins the list in whichever of that build and this one lands
second, with its reason. Every other walk adopts the
shared walk under ADR 0416 or the rulings above.

## Ruling 12 — this is its own build, after ADR 0416's

This build imports the module ADR 0416's build creates and waits for it. #1896 is blocked on #1841
until that lands. The population test and the exception list land here, in the change that moves the
last walks, so the test is green the day it arrives.

**Folding this into ADR 0416's build was declined** as a review holding about twenty walks in nine
modules, the size ADR 0422 ruling 8 refused for its writers. **Letting whichever build lands first
create the module was declined**: two concurrent builds could each write it, and if this one landed
first, ADR 0416's three walks would need temporary exception entries whose reasons were false.

## Coordination the rulings fix without a further choice

ADR 0416's build adds the submission-lookup row to `checks_ledger.DECLARED_LIMITS` that ruling 2
retires, with a test pinning the wrong-document case, so this build removes both.

These unbuilt records share a file with this build, and whichever of each pair lands second keeps
both changes: ADR 0422 (#1860) and #1728 edit `run_status_stop_hook` and its limits; #1728 and
#1602 edit `tracker_publish_hook` and its `NOT_REACHED`; ADR 0395 (#1755), #1600 and #1905 edit
`project_context.py --write` or the voice-model identity write, where a damaged-record refusal
(exit 1) still wins over ruling 7's exit 2; #1806 and #1879 edit `skills_mirror`'s session-start
path beside ruling 10; #1914 edits `run_relevant_paths`; and #1588's posted-reading check goes
through the lookup ruling 2 changes.

## What this does not reach

- A walk the population test does not recognize, such as one assembled by indirection. Ruling 1's
  test is a floor.
- Material reachable only through a link, in every consumer except `run_relevant_paths`, appears in
  no count but the links-not-entered figure.
- ADR 0416's own limits, which this record inherits unchanged: a subdirectory deleted during a walk
  counts as unreadable, and a file the walk could list but misreads is outside the walk.
- Each consumer's handling of files it could list but could not read, except where a ruling above
  names it: rulings 6 and 9.

## Build checklist

- Prerequisite: ADR 0416's build has landed and the shared walk module exists.
- Shared walk module: add the exception list of ruling 11, with each entry's reason.
- Suite test of ruling 1: an AST walk over non-test `tools/*.py` that fails on a recursive walk
  outside the module and off the list, with its floor in its docstring and a planted raw `rglob`
  as a live control.
- `tools/checks_ledger.py`: ruling 2; remove the wrong-document limit row and its pinning test, and
  add a test that the planted case now refuses.
- The eight corpus walks: ruling 3. Drive an unreadable society folder (exit 2) and a live junction
  (counted, not read) through each command that prints a status.
- `tools/spelling_scan.py`: rulings 4 and 9.
- `tools/run_status_stop_hook.py`: ruling 5; add the link row to its limits object.
- `tools/tracker_publish_hook.py`: ruling 6; add the link row to `NOT_REACHED`.
- `tools/coursework_run.py`, `tools/project_context.py`, `tools/voice_model_identity.py`: ruling 7.
- `tools/reference_class_census.py`: ruling 8.
- `tools/skills_mirror.py`: ruling 10.
- `CLAUDE.md` sections for each changed command (**Reference-class census**, **Spelling scan**,
  **Tracker publish hook**, **Approved run status guard**, **Coursework project context**,
  **Guideline text extraction** and its siblings): name the new counts without copying any limits
  object.
- Re-check whether any posture change is a new completion check needing a row in
  `reference/completion-check-starts.tsv`; ruling 7 changes when the draft-order check can be
  observed.
- Tests: for each refuser and each exit-2 posture, drive an `icacls`-denied subdirectory and a live,
  a dangling and an ancestor junction through the public command, skipping the junction cases off
  Windows and running a symbolic-link mutant everywhere.
