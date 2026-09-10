# Tests list git paths through git_paths and no shared tree reader is built

[#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875) was filed on 2026-09-03
out of an architecture review. It found that the modules asserting prose against code each walk the
tree themselves, and proposed one module, `tree_snapshot`, read once per process behind four names:
`sources()`, `parsed(path)`, `tracked()` and `claude_md()`. It left two decisions open: whether the
work was worth doing at all, and how long such a cache should live when several tests build
throwaway trees and want a fresh read. Its third decision, how it relates to #835, was settled by
[ADR 0158](0158-the-prose-bind-is-one-instrument-and-its-rule-carries-an-identity.md) ruling 5:
an answer that depends on which files exist belongs here, and one that depends on what a document
says belongs to the shared prose instrument.

Grilled 2026-09-10. The session began at `origin/main` `7904c62`, freshness gate `FRESH` before
reading, and was brought forward to `5ea8e66` before this record was committed. **Six
questions were ruled by the clinician one at a time on that date**, and two defaults put in the
closing summary were confirmed with it; they are rulings 7 and 8. The answers took the ticket's
proposal apart rather than refining it: no cache, no new module, and none of the four names is
built. What survives is a byte-safety repair to eight test listings and a ratchet that keeps the
next one from arriving in text mode. Nothing is built here; this is the record the build reads.
Every count and every `file:line` coordinate below was measured at `7904c62` and re-derived
unchanged at `5ea8e66`; each is a dated measurement, not a current property of the tree, and the
build this record orders will move several of the coordinates by construction. The session's own
tracker sweep ran an adversarial reader over this record before it merged; the corrections it forced
are folded in rather than listed.

## Measured before ruling

### The population

`tools/` holds 208 Python modules, 117 of them test modules. Two read-only readers built a census
with AST scripts and grep; the parent re-derived every figure this record states, and a figure only
a reader produced is left out.

### Two sets of files, not one

The walks over `tools/*.py` do not look at the same set. **17 call sites spell `glob("*.py")` over
`tools/`**, in 14 modules, one of them `run_grader.py`; two narrower globs, `test_*.py` in
`test_declared_limits.py` and `tracker_*.py` in `test_tracker_workflow.py`, enumerate subsets on the
same terms. The two functions named `repository_survivors`, in `tools/test_prose_bind.py` and
`tools/test_constant_prose_counts.py`, **ask git's index instead**. A module written and not yet
staged is seen by the first kind and not by the second. That gap is
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s subject, which ruled to
leave the window alone and make each index walk state what it misses.

### The index walks in tests are not byte-safe, and one arrived after the reader existed

The adoption rule in `tools/test_git_paths.py`, `SharedReaderAdoption`, refuses a path-listing git
call in a non-test module unless it is spelled `git_paths.<function>`. Test modules are exempt. Run
over the test modules with the exemption removed, it flags **12** calls:

- **8 real listings, all reading the real repository**: `test_artifact_provenance.py:206`,
  `test_constant_prose_counts.py:46`, `test_prose_bind.py:436`, `test_run_record_claim.py:166`,
  `test_scratch_work.py:102`, and `test_skill_agreement.py:425`, `:1087` and `:2603`. Each decodes
  text with `errors="replace"`. Seven omit `-z`, so git hands back its C-quoted rendering of a
  non-ASCII path rather than the path; the eighth passes `-z`, keeps valid UTF-8 names intact, and
  loses only bytes that do not decode.
- **4 false alarms, each a different shape**: a mock's `run.assert_called_once_with([...])` in
  `test_git_paths.py:29`, a mock's `read.assert_called_once_with(...)` in
  `test_tracker_branch_scope.py:375`, the rule's own set of forbidden words at
  `test_git_paths.py:157`, and `test_python_floor.py:70`, which does go through `git_paths` but
  imports `read_path_records` by bare name.

`git log -L` dates the eight to 2026-08-19 (two of them), 08-21, 08-23, 08-28, 08-30, 09-01 and
09-09. `tools/git_paths.py` was added on **2026-09-03**
([ADR 0123](0123-a-git-path-read-is-bytes-through-z-and-the-staged-walk-is-the-headline-because-a-quoted-path-reaches-no-layer.md)).
So `test_skill_agreement.tracked_repository_paths`, the README walk from #772, was written in text
mode six days after the byte-safe reader existed; it is the one of the eight that postdates it.

### The disk walks are correct

Every file read those 17 sites lead to names `encoding="utf-8"`; two of the sites only list paths
and their callers do the reading. Eleven filter out test modules by hand. Only
`test_pdf_engine.tree_sources` reports a file it could not read; the others would raise, which fails
rather than passing. Two functions share the name `tree_sources` and return different shapes:
`test_ls_files_coverage.py`'s returns every module as a dict, `test_pdf_engine.py`'s returns
non-test modules and a tuple of unread names. The two `repository_survivors` likewise return
`set[tuple[str, str, str]]` and `tuple[set[tuple[str, str]], int]`.

### What sharing would hide from two existing checks

- **#254's check.** `test_ls_files_coverage.walks` finds an index walk by the literal `"ls-files"`
  in a call and requires the **innermost enclosing function's** docstring to state both that a
  clean result covers tracked files and that untracked ones are invisible. A call to a wrapper
  carries no such literal, so its callers leave the check, and the wrapper's single docstring would
  vouch for all of them. The module refuses the nearest case in its own words, a module docstring
  vouching for every walk in its file.
- **`test_prose_bind`'s resolver.** It follows a "must not contain" assertion only when the text was
  read in the same module, from a `Path(__file__)` chain or inside a `glob("*.md")` or
  `glob("*.py")` loop. Driven over the tree it resolves **23** reads against
  `RESOLVED_READ_FLOOR = 20`. With the glob-loop recognition switched off it resolves **21**; both
  lost reads are in `test_artifact_provenance.py`. A read moved behind an imported function drops
  out, and the floor refuses only once more than three are lost.

### What a cache would meet

No test writes into the real `tools/` or `CLAUDE.md`, checked statically and not by a live run.
The hazard is a poisoned first read rather than a stale one: 35 calls in 10 test modules patch
`subprocess.run`, counted by an AST walk that is a floor over the spellings it reads, and a lazily
built snapshot first read inside one of them would hold a fabricated listing for the rest of its
process. Tests rebind `phi_scan.REPO_ROOT` to a temporary tree.
[ADR 0127](0127-a-consumer-asks-the-checkout-for-its-commit-and-a-provenance-check-asks-git-only-when-the-answer-is-still-open.md)
decision 7 refused a process-lifetime cache of a git answer on this kind of reasoning, and
[ADR 0128](0128-a-read-once-cache-of-a-committed-reference-file-gets-a-public-reset-and-a-declared-limit-and-the-pattern-is-not-generalized.md)
ruling 3 refused to generalize its one cache.
[ADR 0164](0164-the-suite-runs-through-one-module-that-accounts-for-every-discovered-test.md)
runs the suite's `TestCase` classes in separate worker processes, so a process-lifetime snapshot
would be built once per worker, and its ruling 5 runs `--jobs 1` in the calling process, where one
snapshot would span the whole run. The ticket itself says the family runs in about 8 seconds and is
not a speed fix.

### `CLAUDE.md`

36 test modules name `CLAUDE.md`. No read of it traced by an AST walk omits `encoding=`, so a
shared read carries no correctness payoff. The reason so many tests read it is to cut out one
section, which ADR 0158 ruling 5 assigns to `prose_bind.section`.

### Duplicate names across the tree

Across the 208 modules, 109 top-level function names are defined more than once, and nearly all
are conventions: `main` 64 times, `format_report` 26, `survey` 22.

## Ruled 2026-09-10

### 1. Nothing is kept for the life of a process

The code that reads the tree may be shared; what it read is not remembered. A test that wants the
repository under test and a test that wants a throwaway tree differ only in the root they pass.
This is what the ticket's second decision turns into once nothing is cached.

### 2. A walk keeps its population, and the population is named where it is used

An **index walk** stays an index walk and a **disk walk** stays a disk walk. No consolidation may
move a walk from one to the other, because the two differ exactly while a new module is being
written, and #254 declined to widen the index walks.

### 3. `CLAUDE.md` is read where it is read today, and `parsed()` is not built

Moving the read behind a function saves a spelling and hides the read from `test_prose_bind`'s
resolver. With nothing cached, `parsed(path)` is `ast.parse`.

### 4. An index walk in a test calls `git_paths` directly

A test lists tracked paths by calling `git_paths.read_path_records` itself, with its git arguments,
`"ls-files"` and `-z` among them, written at the call. No `tracked()` wrapper is built, so every
index walk keeps its literal `"ls-files"` and its own docstring statement where #254's check reads
them.

### 5. No shared disk reader is built, and the two same-name pairs are renamed

The 17 disk sites stay as written. The two `repository_survivors` and the two `tree_sources` are
renamed so that a name predicts what it returns. The new names are the builder's to choose.
[ADR 0021](0021-prose-binds-share-one-normalizer-and-a-raw-assertion-declares-its-reason.md) and
[ADR 0023](0023-a-prose-bind-is-graded-on-its-haystack-and-the-walk-declares-what-it-could-not-resolve.md) cite
`test_prose_bind.repository_survivors` by name as a record of what was measured, and stay as written.

### 6. The `git_paths` adoption rule reaches test modules

`SharedReaderAdoption` drops its test-module exemption and corrects the three shapes that would
otherwise raise false alarms:

- a mock's expected-argument assertion is not a listing, in any of mock's assertion spellings,
  including a `mock.call(...)` passed to `assert_has_calls`;
- `test_git_paths.py` is exempt on the same footing as `git_paths.py`, since it tests the owner and
  holds the rule's own vocabulary;
- a call through a name imported from `git_paths`, or through the module under an alias, counts as
  going through it, as `git_paths.<function>` does.

This extends ADR 0123 ruling 10's adoption walk from non-test modules to test modules; that
ruling's population, and ADR 0158's description of the rule as covering every non-test module,
describe it as it stood. The eight listings above move to `git_paths` in the same change, so the
ratchet lands green. Each keeps its docstring's statement of what an index walk cannot see.

### 7. No general check on duplicate function names

A rule refusing a top-level name defined in two modules would fire on 109 names that are mostly
conventions. Ruling 5 renames the two pairs whose shapes mislead; nothing else is enforced.

### 8. `CONTEXT.md` gains **Index walk** and **Disk walk** under Checks

The pair names the distinction ruling 2 keeps. It carries no module names.

## Rejected options

- **The ticket's process-lifetime snapshot.** It buys no measured time, is built once per worker
  under ADR 0164, and can be poisoned by a first read inside a patched `subprocess.run`.
- **Closing the ticket with nothing done.** The eight text-mode listings are a defect and one
  arrived after the byte-safe reader existed.
- **One population for every walk.** Disk for everyone widens the index walks #254 kept narrow;
  the index for everyone blinds 17 checks to a module until it is staged.
- **A `tracked()` wrapper.** It removes its callers from #254's check and lets one docstring vouch
  for all of them.
- **A shared `claude_md()`, with or without teaching `test_prose_bind` to follow it.** The first
  hides reads from the resolver for a spelling; the second widens a checker for no correctness gain.
- **A shared disk reader, or one that skips loops carrying a prose assertion.** The disk walks are
  correct; the first loses two resolved reads without a failure, and the second leaves a mix held
  together by a rule about which is which.
- **A one-time migration without the ratchet.** The dates above show a cleanup already went stale
  once.
- **A ratchet on the defect instead of the owner**, refusing any listing that decodes text or omits
  `-z`. It is a second rule for what routing through `git_paths` already guarantees.

## What this does not reach

**The document layer.** `module_prose_without_inventory` is defined in `test_checks_ledger.py` and
`test_research_ledger.py` and the two differ by one cut: the first also removes the
`NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)` line, which carries no row text.
`test_differential_scan.py`'s class carrying `SHINGLE = 8` is recorded by ADR 0158 as a stated
divergence. Both depend on what a document says, so ADR 0158 ruling 5 places them outside this
ticket.

**Whether a limits walk is keyed on a name or on a shape.** ADR 0135 ruling 5 and ADR 0145 ruling 9
deferred that question to #867 and #875. Neither ruled it; #867 closed without it and this record
does not take it up, so [#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921)
owns it.

**A walk that changes population.** Ruling 2 is held by no check. A walk moved from the index to the
disk leaves #254's check without anything failing, and one moved the other way joins it.

**Git reads outside the adoption rule's vocabulary.** The rule covers `ls-files`, `ls-tree`,
`diff --name-only` or `--numstat`, and `rev-list --objects`. A `check-ignore` or
`status --porcelain` read is unchecked, as at `test_build_artifacts_ignored.py:95`,
`test_skill_agreement.py:391` and `artifact_provenance.py:332`; none loses a path today.

**A listing built by indirection.** The adoption rule and #254's check both read literal arguments
at the call, so a subcommand assembled at run time or passed through a variable is invisible to
each. Both already declare that ceiling.

**A new disk walk.** Nothing grades how a future disk walk reads its files; ruling 7's measurement
is why no shape check was built.

**Whether a walk points at the repository or at a throwaway tree.** Ruling 1 makes that the root a
caller passes, and nothing checks which root a test chose.
