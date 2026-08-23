# An ADR number is claimed when it is handed out, and a ratified record's facts may be corrected in place

[#452](https://github.com/mshamblin5150-code/clinical-skills/issues/452) recorded three files named `docs/adr/0010-*.md` on `main` at once, written by three sessions that never saw each other. [#459](https://github.com/mshamblin5150-code/clinical-skills/issues/459) recorded [ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md) stating the guideline corpus as `392 MB`, which is its MiB figure carrying an MB label, after [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) ruled bytes-only for that artifact.

**They are one decision and #459 said so first**: *"it should be settled once and applied to both rather than twice and differently."* The correction rule is what makes renumbering a legitimate repair, and renumbering is the repair the allocation mechanism falls back on. Splitting them would leave each ruling resting on the other.

The clinician ruled both on 2026-08-23.

## What was measured before anything was ruled

**Every defect either ticket lists is already repaired by hand.** `main` carries `0001` through `0015`, each stem unique, and no unmerged ref holds a duplicate. `CLAUDE.md`'s `[ADR 0009]`-labeled link to an `0010-` target is gone, and `tools/artifact_provenance.py`'s two bare `docs/adr/0010` citations resolve correctly, because `0010` on `main` is #406's own record. So the tickets' decisions 1, 2 and 4 were settled by events, and what remained open was the mechanism alone.

**The citation surface is 134 references across 45 files** — 81 bare `ADR NNNN` and 53 by path. `ADR 0001` alone is cited 49 times by number and 31 by path.

**One ticket already produces more than one ADR.** `0014` and `0015` are both #417. `0001` names no ticket at all.

**Sixteen worktrees share one object store.** `C:/codeing/clinical_skills/.git/worktrees/` holds fifteen registrations plus the main checkout, including two Codex worktrees living under `C:/Users/msham/.codex/` that git registers here because they were created from this clone. Zero were prunable when this was measured.

## The failure is when the number is chosen, not how

A session reads `docs/adr/`, sees `0009` as the highest, and takes `0010`. It is correct at that moment. `main` moves during the session; the freshness gate catches the move and is re-run; the merge produces no conflict **because the filenames differ**. The number was picked against a tree that had ceased to exist, and every gate downstream passed — freshness `FRESH`, the suite `OK`, spelling clean, `phi_scan` clean.

It fired four times in two days across five tickets, and twice it fired on the **repair**: two sessions renumbering *because of #452* both read the same tree, both saw the same first free number, and both took it. Careful re-checking at authoring time does not converge, because a long session's start is not its merge.

**Parallel grilling worktrees are the standing way of working here**, so this is a permanent property of the workflow rather than a two-day anomaly.

## What is ruled

**A ratified record's facts may be corrected in place, and a dated line at the bottom records what they said and why they changed.** The paragraph that does the *deciding* stays untouchable. **The filename is an index rather than the ruling, so a record may be renamed with `git mv`** — never delete-and-re-add, which loses `git log --follow`.

**A number is claimed at the moment it is handed out.** `tools/adr_next.py` takes a title, reads every worktree's `docs/adr/` — the working tree and not only what is committed — writes the file with its heading already in it, and prints the path. The claim and the check are the same act.

**A test asserts no two files in `docs/adr/` share a four-digit stem.** It lives in `tools/`, so `python -m unittest discover -s tools -t tools` runs it and CI runs it at every merge with no workflow edit.

**The pre-commit hook warns, and never refuses.** When an ADR is staged it reads all worktrees and prints which other one claims the same number. Advisory, on the same terms as the skills-mirror and spelling checks already there, and it costs nothing on a commit that does not touch `docs/adr/`.

**ADR 0007's `392 MB` becomes `410,197,235 bytes`, and its `8000:1` becomes *four orders of magnitude*.**

## Considered options

**Rename every record to its originating ticket number.** Rejected on a measurement rather than on cost. It is not collision-proof by construction — `0014` and `0015` are both #417 today, so it moves the collision from between sessions to inside one — and `0001` names no ticket to be renamed to. Its cost was also the largest: fifteen filenames and 134 citations.

**Defer the number to the merge.** Rejected. `docs/adr/draft-452-*.md` numbered by whoever merges, with a test forbidding a `draft-` file on `main`, never collides. But every citation the session writes into `CLAUDE.md` points at a filename that changes at merge, so it needs a rename-and-rewrite tool on the critical path, and it trades a sometimes-problem for an always-chore.

**The merge-time test alone.** Rejected as insufficient rather than wrong; it is adopted as one half. With parallel grilling standing, a red `main` is most batches rather than a rare event, and the cheap avoidance sits unused at the moment the mistake is made.

**A number-picker reading remote branches.** Rejected as the wrong instrument, and #452 reasoned its way to this conclusion on evidence that does not hold. `git ls-remote` cannot see an unpushed branch, and all four collisions were drafted on unpushed branches — but they were not on separate clones. The local worktree registry would have seen every one of them, and nobody looked locally.

**A fourth refusing check in the hook.** Rejected. It can only honestly refuse on the tree it stands in, which reaches the one collision of four that lived in a single tree and lets the other three past — a check that reads as coverage while missing what it is named for. It would also mean a refusal fired by a draft sitting uncommitted in another agent's worktree, which nothing here does.

**Correcting ADR 0007 by annotation only.** Rejected. A reader opens the file, reads the figure at `:40`, copies it, and never scrolls to the footnote — which is the failure this repo keeps recording. The correction is visible either way; only one of the two options fixes what the reader sees.

**Correcting `392 MB` to `410 MB` and stopping.** Rejected by #459 in advance, and rightly: #87's ruling was about the convention rather than the digits, and a corrected MB figure is the same unre-derivable number one factor over.

## What this does not reach, declared rather than left to be found

**A separate clone.** A fresh `git clone` elsewhere on the disk, or the same repository on another machine, has its own `.git` and is not in this registry. Not how the work is done today; it is the honest edge and the reason the test stays behind the picker.

**A worktree that exists but has not written its ADR yet.** This is the residual window, and shrinking it from a whole session to an instant is the entire value of the picker writing the file rather than printing a number. Two sessions asking within the same instant still collide, which is what the test is for.

**An abandoned worktree still on disk.** Its draft keeps its number claimed and the sequence skips one. Harmless: the number is an index and not a count, so a gap costs nothing.

**Whether the correction rule was applied honestly.** Nothing checks that an in-place edit to a ratified record left the dated line, or that what was edited was a fact rather than a ruling. That is a reading, and it stays one.

Correction, 2026-08-23: this sentence formerly read "its heading and status lines".
No ratified record has ever carried a status line and none was ever committed; the
clause described a house convention that did not exist. [#472]. The ruling itself is
unchanged.
