# A recursive walk never enters a link and one shared walk serves the census the sweep and the after-action review

**Measured at:** dda02009b178dee0f6dcfea4f2e067aab3c30682

[#1841](https://github.com/mshamblin5150-code/clinical-skills/issues/1841) was filed from the
tracker sweep closing #1685's grilling on 2026-10-16. Grilled 2026-10-18 against `main` at
`31b048a1`, where the measurements below were taken. The commit above adds only drafts of this
record to `main` at `1b98c073`, which differs from that base only by ADRs 0413 to 0415 and their
glossary entries, and the freshness gate read `FRESH` there. The clinician ruled every point below in that session, one question at a time. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**No link sits under the owning scratch root today.** A count-only walk of `repo_root.scratch_root()`
that stops at every symbolic link and junction found zero, live or dangling. The rulings fix the
next instance rather than a current miscount.

**`Path.rglob` drops an unreadable subdirectory without a trace.** Under Python 3.14.4, a temporary
tree holding one readable file and one subdirectory denied to the current user by `icacls` returned
only the readable file, raised nothing, and gave no count of what it skipped. So
`uptodate_store.sweep_unfiled` has a second silent shortfall beside the junction ones #1841 records:
its `unread` count covers files it opened and failed to read, never directories it could not list.

**The junction shapes in each candidate walk, read from the code:**

| Walk | Live junction | Dangling junction | Junction to an ancestor |
|---|---|---|---|
| `aar_scan.discover_transcripts` | read once; paths are deduplicated by resolved location | dropped from a graded population, uncounted | does not terminate |
| `aar_scan._memory_files` | read once; hashes are keyed by resolved location | the file is absent, so landing evidence fails visibly | does not terminate |
| `checks_ledger._submission_document` over `output_root()` | a second match, so it refuses | no match, so it refuses | does not terminate |
| `skills_mirror` copy-stale comparison and ADR 0407's session-start walk | entered on purpose; the mirror is made of junctions | surfaces as a difference | not reached by a served skill tree |
| `skills_mirror.run_relevant_paths` over `skills/` | a tracked tree; Git holds no junction | none | none |

**The `checks_ledger` row is narrower than it reads, and the sweep closing this grilling found it.**
An unreadable folder is not a junction shape. Planted on 2026-10-19 under Python 3.14.4, with one
`stem.md` in a readable folder and a second one level beneath a folder denied to the current user,
`rglob("stem.md")` returned 1 match, so the exactly-one lookup accepts the visible document without a
word. A second document directly inside the denied folder was still found, because a literal name is
checked without listing that folder. The clinician ruled that this record keeps ruling 4 and states
the case in the limit, and that whether the lookup should adopt the shared walk belongs to
[#1896](https://github.com/mshamblin5150-code/clinical-skills/issues/1896).

**Link detection has a floor trap.** `os.path.isjunction` and `DirEntry.is_junction` exist only on
Python 3.12 and later, against a consumer and tooling floor of 3.10. `skills_mirror._is_link` already
answers correctly on every supported version: symbolic link, then `isjunction` where it exists, then
the Windows reparse-point attribute. It is the only correct copy in `tools/`.

## Ruling 1 — the sweep adopts ADR 0386's rule as written

`uptodate_store sweep` never enters a symbolic link or junction below a sweep root, live or
dangling, and counts each one once as a link not entered. A link is not counted in `files examined`.
Topic-shaped material reachable only through a live link is not read; the report states how many
links were not entered rather than what lay behind them. The two refused options were following live
links with deduplication by resolved location and an ancestor guard, which reads outside the root it
was given and makes the census and the sweep disagree about one junction, and refusing the run when
any link sits below the root, which ADR 0386 already refused because naming the link prints a
scratch filename.

## Ruling 2 — an unreadable subdirectory is a failed read, and a link not entered is a reported boundary

A subdirectory below a sweep root that cannot be listed joins the sweep's unread count and makes the
command exit 2, as an unreadable file already does. A link not entered is printed as a count on every
run, zero included, and never changes the exit status: it is the boundary ruling 1 declares, not a
failed read. The census
keeps ADR 0386 ruling 2 and ruling 3, under which neither count changes its status, because its file
figure is printed for context and its grade rests on the top level; the sweep's figures are its whole
output.

## Ruling 3 — one shared module holds the link test and the walk

The link test moves out of `skills_mirror._is_link` into one new module, with its 3.10 fallback
intact, and `skills_mirror` imports it. The same module holds the walk: it descends from a root
without entering any link, keeps walking past a subdirectory it cannot list, and returns the files it
reached, the count of subdirectories it could not list, and the count of links not entered. It never
raises below the root and never returns an entry's name in a count. `scratch_census`,
`uptodate_store` and `aar_scan` import it; each composes its own figures from those three results, so
the census can count a link toward a root's file total as ADR 0386 ruling 1 requires while the sweep
keeps links out of `files examined`. A local walk per consumer was refused because the policy is one
policy, so a divergence between copies would be the defect itself.

## Ruling 4 — `aar_scan`'s two walks adopt it; the other candidates are declared limits

`aar_scan.discover_transcripts` and `aar_scan._memory_files` adopt the shared walk on ruling 2's
terms: an unreadable subdirectory joins the extract's existing unread remainder, and links not
entered are printed as a count beside its found, time-skipped, byte-skipped and read counts. A
transcript reachable only through a live link stops being read, which closes the silent drop of a
dangling one and the ancestor loop.

The remaining candidates are declared rather than rebuilt, each in its own limits object with the
reason from the table above. `checks_ledger.DECLARED_LIMITS` states that its submission lookup refuses
on both junction shapes, does not terminate on an ancestor junction, and accepts the one visible
document when a second same-name document sits beneath a folder it cannot list. `skills_mirror.NOT_REACHED`
states that the copy-stale comparison and ADR 0407's session-start walk enter junctions deliberately
and surface a dangling one as a difference. `run_relevant_paths` needs no limit: it walks a tracked
tree.

*Superseded 2026-10-19.* The words "`checks_ledger.DECLARED_LIMITS` states that its submission lookup refuses on both junction shapes, does not terminate on an ancestor junction, and accepts the one visible document when a second same-name document sits beneath a folder it cannot list." are superseded by [ADR 0432](0432-every-recursive-walk-in-tools-adopts-the-shared-walk-or-is-a-named-exception-and-each-walk-s-verdict-fails-closed-on-a-folder-it-could-not-read.md) ruling 2. The submission lookup adopts the shared walk and refuses over a folder it could not open, so the limit row is retired whole. `aar_scan`'s adoption and the `skills_mirror` comparison rows stand.

*Superseded 2026-10-19.* The words "`run_relevant_paths` needs no limit" are superseded by [ADR 0432](0432-every-recursive-walk-in-tools-adopts-the-shared-walk-or-is-a-named-exception-and-each-walk-s-verdict-fails-closed-on-a-folder-it-could-not-read.md) ruling 10. The function walks `skills/` on disk rather than a tracked tree, so it adopts the shared walk, and an unopenable folder or a link not entered leaves the session-start base line not established. The `skills_mirror` comparison rows stand.

## Ruling 5 — #1685 and #1841 are one build

The shared module is built in the same change as ADR 0386's census repair, with the census as its
first consumer. This record supersedes the location in ADR 0386's build checklist: its first item's
walk is written in the shared module of ruling 3, and `scratch_census.count_files` is replaced by a
call to it. Every ADR 0386 ruling, consequence and test stands. ADR 0386 is not edited, because its
checklist is not a ruling and its measurement declaration must stay at the commit it was measured
against; #1685 carries a comment pointing here.

## Coordination the rulings fix without a further choice

[ADR 0409](0409-the-uptodate-pull-checks-the-query-it-sent-files-drug-pages-by-version-and-proves-a-failed-pull-opened-the-page.md)
has the sweep count a drug page by its `Topic <N> Version <N.N>` line. That build and this one edit
`sweep_unfiled`; whichever lands second keeps both changes.

The same rule holds for the other unbuilt records the sweep found sharing a file with this build:
ADR 0387 (#1693) and ADR 0396 (#1759) edit `aar_scan`'s
extract report, as do the open builds on #1601 and #1855; #1588's build edits `checks_ledger`'s
posted-reading path beside `_submission_document`; and [ADR 0407](0407-a-worktree-session-that-started-without-its-skill-mirror-is-told-its-skills-came-from-the-owning-checkout.md)
adds the session-start comparison to `skills_mirror`. If this build lands before ADR 0407's, the
session-start row of ruling 4 is written by whichever of the two lands second, because a limit row for
a walk that does not exist yet would describe nothing. That comparison must not adopt the shared
walk: it reaches every served file through the owning mirror's junction, so the shared walk would
read none of them.

**`aar_scan`'s remainder is an equality, so ruling 4 needs a named part.** The extract writes
`UNREAD-REMAINDER` as the sum of named component fields, and the grade refuses `coverage-mismatch`
unless the remainder equals that sum. Unreadable subdirectories therefore enter as a new named
component field in both the extract and the equality, or every extract with one would fail its own
grade. `discover_transcripts` already counts transcripts it failed to `stat` or read in
`TranscriptDiscovery.unread`, and the extract never prints that count. On ruling 2's terms an
unreadable transcript is a failed read, so it joins the remainder as its own named component in the
same build.

## What this does not reach

A file the walk could list but whose type or name it misreads is outside this record, as it is
outside ADR 0386. Material reachable only through a live link appears in no count. A subdirectory
deleted during a walk is counted as unreadable and not distinguished from a permission failure.
`checks_ledger` and the deliberate `skills_mirror` walks keep their ancestor-junction exposure as a
declared limit. The candidate walks came from #1841's list, not from a census of `tools/`. The sweep
closing this grilling counted every recursive walk in non-test `tools/` and found thirteen more with
the same two gaps, over account trees and the guideline corpus; they are filed as
[#1896](https://github.com/mshamblin5150-code/clinical-skills/issues/1896), and this record rules on
none of them.

## Build checklist

- New shared module in `tools/`: the link test moved from `skills_mirror._is_link`, and the walk of
  ruling 3, built on `os.scandir` with the link test applied to every entry before descending. Its
  module docstring states the boundary in a `DECLARED_LIMITS` object.
- `tools/skills_mirror.py`: import the link test; add the copy-stale and session-start rows to
  `NOT_REACHED`.
- `tools/scratch_census.py`: ADR 0386's checklist in full, with `count_files` replaced by the shared
  walk.
- `tools/uptodate_store.py` `sweep_unfiled`: use the shared walk; add unreadable subdirectories to
  `unread`; add a links-not-entered count to `SweepReport` and print it on every run; keep links out
  of `examined`.
- `tools/aar_scan.py`: `discover_transcripts` and `_memory_files` use the shared walk; the extract
  report prints links not entered; unreadable subdirectories and `TranscriptDiscovery.unread` each
  enter the unread remainder as a named component field, and the `coverage-mismatch` equality adds
  both.
- `tools/checks_ledger.py`: add the submission-lookup row to `DECLARED_LIMITS`.
- `CLAUDE.md` **Scratch census**, **UpToDate evidence store** and **After-action review**, and
  `docs/agents/scratch.md`: name the new counts without copying any limits object.
- Coordination: whichever of this build and each record named under *Coordination* lands second
  keeps both changes.
- Tests: ADR 0386's list is split by subject. The walk's own behavior (a live junction not entered,
  a dangling one counted, an ancestor junction terminating, an unreadable subdirectory counted) is
  tested in the shared module's tests; the census consequences (the `files beneath` line, the
  hold-back of a worktree, the exit-2 remedy, peer-root classing) stay in `test_scratch_census.py`. The sweep: a live junction to a sibling is counted
  once as a link and its target's files are not examined; a dangling junction is counted as a link
  rather than dropped; an ancestor junction terminates; an unreadable
  subdirectory makes the sweep exit 2; the links-not-entered count prints at zero. `aar_scan`: a
  dangling junction under a transcript root is counted, an ancestor junction terminates, and an
  extract with one unreadable subdirectory grades without `coverage-mismatch`. `checks_ledger`: a
  test pins the documented wrong-document case so the limit row stays true. A
  symbolic-link mutant runs everywhere and junction tests skip off Windows. The link test passes on
  3.10, where `isjunction` is absent, through the reparse-point limb.
