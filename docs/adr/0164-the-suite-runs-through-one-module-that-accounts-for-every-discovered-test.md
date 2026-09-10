# The suite runs through one module that accounts for every discovered test

[#874](https://github.com/mshamblin5150-code/clinical-skills/issues/874) was filed out of an
architecture review of what it called the repo-wide gate, 2026-09-04. The suite's interface was a
command string, `python -m unittest discover -s tools -t tools`, copied into five files, and it ran
in one process on a 22-core machine. Nothing could hold parallelism, a cost report or a re-run
line. [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) rules the suite's posture: advisory, at
the merge, one job on `windows-latest`, Python 3.14, nothing installed. This record rules how the
suite is invoked inside that job and leaves the posture untouched.
[ADR 0163](0163-a-generated-conformance-class-takes-its-test-module-and-a-fixed-name-so-its-id-re-runs.md)
made every discovered test id re-runnable and was this record's prerequisite. It landed during the
session as PR #1048.

Grilled 2026-09-10. The session began at `origin/main` `75861e0` and was brought forward to
`e27ee54`, which carries #873's build. **Fifteen questions were ruled by the clinician one at a
time on that date**, and two defaults put in the closing summary were confirmed with it; they are
rulings 15 and 16. The fifteenth question corrected ruling 10's spelling after the session's own
tracker sweep found the first spelling raised the tree's Python floor. Nothing is built here; this is the record the build reads. Every count below is
a dated measurement, not a current property of the suite.

## Measured before ruling

### The command is written in five files and bound in two

At `e27ee54`, `git grep -- "unittest discover"` finds the command in exactly five files:
`.github/workflows/checks.yml`, `CLAUDE.md`,
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md),
`tools/test_ci_workflow.py` as `SUITE_COMMAND`, and a `Run with::` docstring in
`tools/test_uspstf_table.py`. `test_ci_workflow` asserts `SUITE_COMMAND` at three sites, but two
of them read the same workflow file, once as text and once as parsed YAML, so it binds two files.
`reference/thresholds/README.md` and a docstring in `tools/test_threshold_sheet.py` carry
single-module commands, which are not suite commands.

A test id is re-runnable only from `tools/`. From the repository root,
`python -m unittest test_class_vocabulary` fails to import; from `tools/` it passes.

### Today's runner cannot tell a failure from a module that never loaded

On Python 3.14.4, `python -m unittest discover` over a directory holding no tests exits 5, over a
module that raises on import exits 1, and over a failing test exits 1.

### The CI runner

GitHub's hosted-runner reference, read 2026-09-10, gives `windows-latest` on a public repository 4
vCPUs and 16 GB. The `Test suite` step took between 6 min 28 s and 7 min 15 s across the four
`push` runs of `checks.yml` on `main` that day. The job sets no `timeout-minutes`.

### Timing with spread

A read-only measurement agent ran a throwaway runner on the maintainer's machine: Intel Core Ultra
9 185H, 16 physical and 22 logical cores, Python 3.14.4, tree `75861e0` plus this session's
uncommitted `CONTEXT.md` entry. The population was 5,238 tests in 116 modules and 950 classes,
packed as 689 class units with the 17 modules holding generated classes kept whole, or as 116
module units. Workers ran as separate processes from `tools/`. Configurations alternated, three
runs each. **The parent re-derived every figure in the table below from the run's raw per-run
records with its own script; it did not re-run the measurement.**

Two serial runs: 363.1 s and 338.8 s wall, each 5,238 tests, 0 failures, 0 errors, 4 skips.

| configuration | wall, s (min / median / max) | second-slowest worker, s | summed test time vs serial |
| --- | --- | --- | --- |
| weighted class units, 4 jobs | 109.1 / 131.0 / 144.6 | 80.9 / 88.1 / 89.3 | ×1.09 |
| weighted, 8 jobs | 121.5 / 124.5 / 135.6 | 42.5 / 43.1 / 43.7 | ×1.15 |
| weighted, 12 jobs | 130.2 / 131.2 / 139.8 | 32.2 / 34.1 / 34.6 | ×1.37 |
| weighted, 16 jobs | 122.9 / 128.0 / 137.5 | 29.7 / 29.7 / 30.3 | ×1.50 |
| weighted, 20 jobs | 121.6 / 131.5 / 133.7 | 32.2 / 33.3 / 33.6 | ×1.73 |
| equal weights, 12 jobs | 138.7 / 143.2 / 165.3 | 46.7 / 50.2 / 53.6 | ×1.21 |
| weighted module units, 12 jobs | 131.6 / 131.9 / 132.8 | 45.7 / 45.9 / 46.2 | ×1.34 |
| weighted, 12 jobs, one shared lock root | 130.2 / 131.9 / 134.9 | 34.4 / 34.7 / 34.8 | ×1.37 |

**Wall clock discriminates nothing here.** In every weighted and module run the slowest worker held
one test method alone, so wall equals that worker, and that method's own time in parallel runs
ranged 108.8 to 150.5 s. *Had job count mattered to wall clock, the medians would separate by more
than that range; they sit between 124.5 and 131.9 s.*

**The second-slowest worker does discriminate**, because its range is about 2 s. Sixteen jobs beat
twelve by more than the range, and twenty is no better than twelve and worse than sixteen. Summed
test time rises with job count, which is contention. Equal weights and module units are each worse
than weighted class units by more than any range. *Had weights not mattered, the equal-weight row
would overlap the weighted one; its minimum exceeds the weighted maximum by 12 s.*

**No test behaved differently in parallel.** All 24 runs ran 5,238 tests with 4 skips, no failure,
no error, no loader failure and no unaccounted result, across 21 distinct packings. Three runs per
configuration cannot see an interaction rarer than about one run in 24. The shared lock root changed
neither correctness nor time within the range.

### The critical path is one defect

The method is `test_reference_class_census.TheExtractorCoverageHasAnIndependentPopulation.test_one_real_committed_member_is_read`:
112.7 s and 111.9 s of the two serial runs. The parent re-derived its cause at `e27ee54`:
`reference_scan.read_document` on `skills/practicum-case-study/SKILL.md` took 106.9 s in one
uninstrumented run, and under `cProfile` all of it is `_evidenced_narratives` re-normalizing a
growing suffix for every whitespace token before each date parenthetical, per entry. Filed as
[#1049](https://github.com/mshamblin5150-code/clinical-skills/issues/1049). No job count and no
unit size can split one method.

### Facts the rulings rest on

- No test module under `tools/` defines `setUpModule`, `tearDownModule` or `addModuleCleanup`.
- `tools/artifact_lock_test_support.py` gives each lock-bearing test process a private temporary
  lock root when `CLINICAL_SKILLS_LOCK_ROOT` is not inherited, and its docstring promises exactly
  that. The locks do not wait; a process that finds one held exits 2.
- The CPU count is 22 on the maintainer's machine, from both `os.cpu_count()` and
  `os.process_cpu_count()`; three quarters of it is 16, and of the runner's 4 it is 3. Python's
  documentation gives `os.process_cpu_count()` as added in 3.13 and returning `None` when
  undetermined. `README.md` states a 3.10 floor, and `tools/guidelines_extract.py` already sizes its
  pool with `os.cpu_count() or 1`.
- `runs` is in `scratch_census.STANDING_ARTIFACTS`, and `phi_scan.TRACKER_PUBLISH_MARKER` already
  writes under `scratch/runs/`. `repo_root.scratch_root()` returns the owning checkout's path
  whether or not it exists.
- `run_grader.WALK_CEILING` recognizes a grader by a top-level `survey()`, a top-level
  `format_report()` and a `__main__` guard.
- The word *gate* already names the threshold-sheet gates, the tracker freshness gate, the
  glossary's **Quotation gate** and **Gated row set**, and `grader_conformance.gate_conformance`.

## Ruled 2026-09-10

### 1. `tools/suite.py` is the suite's one command

`.github/workflows/checks.yml`'s `Test suite` step and `CLAUDE.md` both invoke
`python tools/suite.py`. `unittest` discovery is invoked only inside the module. With no arguments
it runs every discovered test, so ADR 0002's guarantee that the detection ran is unchanged.

### 2. The run accounts for every discovered id

The parent discovers once, with the start and top-level directories both set to the directory
holding the module, so the population does not depend on the working directory. That list of ids
is the denominator. Each worker reports the id and outcome of every test it ran, and the parent
requires every discovered id to come back exactly once as pass, failure, error or skip. A missing,
duplicated or unexpected id makes the run incomplete. Every run, including an in-process one,
prints the discovered count and the number never accounted for. Ids are compared as strings, so
the accounting never loads a test by name.

### 3. The module is `suite.py` and the term is Suite run

**Suite run** enters `CONTEXT.md` under Checks. *Gate* stays with the checks that refuse. ADRs 0126,
0127 and 0163 keep "the repo-wide gate", because they record the review as it happened.

### 4. Exit 0 is complete and passing, 1 is a failure, 2 is incomplete

Exit 1 means at least one discovered test failed or errored. Exit 2 covers every way the run was
not complete: discovery found nothing, a module could not be imported, a worker ended without
reporting, or an id went missing, came back twice or came back unexpected. Where a failure and an
incomplete run both hold, 1 wins and the report still names each module that did not load and the
unaccounted count. A module that raises on import therefore moves from `unittest`'s 1 to 2.

### 5. `--jobs 1` runs in the calling process

It starts no worker, runs tests in discovery order, and prints `unittest`'s own traceback output,
so `breakpoint()` and `pdb` work. The accounting of ruling 2 and the statuses of ruling 4 are the
same. The module documents it as the mode for reproducing a failure.

### 6. Two surfaces are bound and the history is left alone

`test_ci_workflow.SUITE_COMMAND` becomes `python tools/suite.py`, and its existing assertions keep
binding the workflow and `CLAUDE.md`. ADR 0016's sentence naming the old command is corrected in
place with a dated line, under ADR 0016's own rule. `test_uspstf_table.py`'s `Run with::` docstring
is deleted. Nothing asserts the old command's absence elsewhere, and the single-module commands
stay.

### 7. No time bound on a worker

A hung worker hangs the run, as a hung test does today. Nothing reports clean. The hang is a
declared limit under ruling 15.

### 8. No hand-picked subset, and every failure prints its re-run line

`suite.py` takes no test names. For each failing or erroring test its report prints
`re-run (from tools/): python -m unittest <id>`, which stock `unittest` runs.
`tools/test_suite_ids.py` keeps every such id resolvable.

### 9. No `--shard`

The suite is never split across CI jobs; within its job it parallelizes with `--jobs`. Every
`suite.py` run is a suite run. This rules how the suite runs inside a job and nothing about how
many jobs `checks.yml` holds: whether the workflow gains a job on another platform stays with ADR
0002 and [#773](https://github.com/mshamblin5150-code/clinical-skills/issues/773), and a job
added there would run the same `python tools/suite.py`.

### 10. `--jobs` defaults to three quarters of the CPU count

The default is `max(1, (os.cpu_count() or 1) * 3 // 4)`. `checks.yml` and `CLAUDE.md` both run the
plain command, so the runner uses 3. The report prints the job count and how it was derived, and the
module states the fraction as this record's one-machine measurement, not as a rule.

This was first ruled as `os.process_cpu_count()`. The session's tracker sweep found that function
postdates the 3.10 floor and returns `None` when the count is undetermined, which would raise the
floor with no check noticing and crash on `None * 3`. The clinician ruled the spelling above the same
day. It gives the same count on both machines measured and does not follow CPU affinity, which
nothing in this repository sets.

### 11. Weights live in the owning checkout's `scratch/runs/`

After each run in which every discovered id came back, `suite.py` atomically replaces
`scratch/runs/suite-weights.json` under `repo_root.scratch_root()` with each unit's measured time.
It never creates the scratch root, so a fresh clone and the CI runner write nothing. With no file
it packs by equal weights; a unit absent from the file takes the mean of the recorded units. The
report says whether it packed by recorded or equal weights. The accounting of ruling 2 never reads
the weights.

### 12. The parent does not set a lock root

`suite.py` neither sets nor removes `CLINICAL_SKILLS_LOCK_ROOT`, so each worker keeps the private
root `artifact_lock_test_support` gives it and tests in different workers cannot collide on a lock.
The 2026-09-04 advice on #874 that a parent should set one root is withdrawn.

### 13. A unit is a `TestCase` class

A class goes to one worker whole, so its class fixtures run once. Classes of one module may go to
different workers.

### 14. Every run prints its critical path

One line names the slowest unit, its elapsed time, the run's wall time and the next-slowest
worker's time, labeled as one run's elapsed time. It carries no threshold, is never a finding and
never changes the status. `--slowest N` lists that run's N slowest units.

### 15. `suite.DECLARED_LIMITS` holds the module's boundary

It is a tuple of `(subject, reason, run_grader.EvidenceDisposition)` triples, as
`grader_conformance.DECLARED_LIMITS` holds, with two rows:

- **whether a worker that never finishes is reported**; ruling 7 sets no bound, so the run waits;
  `DECLARED_READING`, because a live control would hang.
- **whether a test outside discovery's population ran**; the population is `test*.py` under
  `tools/` and nothing else; `BEHAVIOR`, with a control that builds a temporary tree holding a
  test file discovery does not match and shows the run reporting complete without it.

A test module names the object where `test_declared_limits.named_by_tests` can see it. `CLAUDE.md`
points at the object and copies no row. `suite.py` is not a `run_grader` member and does not take
`run_grader.WALK_CEILING`'s grader shape.

### 16. CI puts the suite report on the job page

The `Test suite` step writes `suite.py`'s report into `$GITHUB_STEP_SUMMARY` and preserves its exit
status, as the PHI and threshold-sheet steps do.

## Rejected options

- **A local accelerator beside the unchanged command, or both commands documented.** The first
  adds a sixth description of the suite and leaves the finding open; the second makes a second
  population somebody has to keep equal to the first.
- **Comparing summed worker totals, or trusting worker reports.** A lost test and a duplicated one
  cancel in a total, and trusting reports is the partial read passing as complete that the
  repository's extractor-coverage rule forbids.
- **Naming the module `gate.py`, or a generic name.** The first collides with five existing uses of
  the word; the second names nothing the tree already calls this.
- **`unittest`'s statuses, or only 0 and 1.** Both leave a module that never loaded reading as a
  failing test.
- **`--jobs 1` as one worker process.** One code path for every count, at the cost of the only mode
  where a debugger attaches.
- **An absence check for the old command.** It cannot tell a mention from a use and would fire on
  this record and on ADR 0016's correction line.
- **A per-worker time bound, or `timeout-minutes` on the job.** The bound is a number nobody can
  calibrate, and its realistic failure is a false incomplete on the slower runner; the job timeout
  leaves a local run unbounded.
- **Accepting test ids as arguments.** It gives `suite.py` a mode where exit 0 means a subset
  passed, which ADR 0002 and #874's own warning against letting a shard become the gate both refuse.
- **`--shard` with a CI matrix and a combining job.** No split across machines beats the one slow
  method, and it would amend ADR 0002's one job and re-implement ruling 2 across machines.
- **Default 1, every CPU, or a fixed 16.** Default 1 needs a flag for every fast run and splits CI's
  command from the documented one; every CPU measured worse than 16 here; a fixed 16 is four times
  the runner's CPUs.
- **`os.process_cpu_count()`, or it with an `os.cpu_count()` fallback.** The first raises the Python
  floor to 3.13 through a ruling about job counts, which is #927's decision to make; the fallback is
  two code paths for an affinity difference nothing here exercises.
- **A committed timings file, no weights, or a CI cache step.** The file is a figure nothing
  re-derives and a merge-conflict source; no weights costs the measured difference on every run; a
  cache step adds a service to a job ADR 0002 keeps to checkout, setup and commands.
- **One shared lock root set by the parent.** It adds nothing measured and admits a cross-worker
  collision rarer than three runs can see.
- **Module or method units.** Module units measured 12 s slower on the rest of the suite; method
  units cannot shorten a run pinned to one method and repeat class fixtures.
- **A cost report only on request.** That is how a 113-second method went unnoticed.

## What this does not reach

**Whether three quarters is right on another machine.** It is fitted to one machine, and nothing
was measured on the runner. The report's job count and CI's step duration are what would show it.

**An interaction between tests rarer than about one run in 24.** None was seen in 24 parallel runs.

**The one slow method.** #1049 owns it. Until it lands, no job count finishes a run faster than that
method.

**A worker that hangs, and tests outside discovery's population.** Both are declared by ruling 15.

**How many jobs `checks.yml` holds.** Ruling 9 keeps the suite in one job; a job on another
platform is #773's question.
