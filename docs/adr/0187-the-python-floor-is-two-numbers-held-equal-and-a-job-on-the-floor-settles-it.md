# The Python floor is two numbers held equal and a job on the floor settles it

[#927](https://github.com/mshamblin5150-code/clinical-skills/issues/927) was filed on 2026-09-06 out
of [#791](https://github.com/mshamblin5150-code/clinical-skills/issues/791)'s grilling, by
[ADR 0139](0139-a-floor-is-cited-by-api-and-symbol-and-coordinates-are-ratcheted-to-zero.md)
ruling 4. #791 fixed where the floor's evidence is *stated*; this ticket asks whether the floor is
*right*, which that ticket's scope forbade touching. It asked three things: whether a walk that
derives the minimum interpreter asserts or only reports, what the remedy is if the tree's floor and
the consumer path's turn out to differ, and whether a static walk supersedes
[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md)'s concession that *"only a job that runs on it can
settle it."*

Grilled 2026-09-11 to an empty frontier. **Fourteen rulings, by the clinician, on that date.**
Nothing is built here; this is the record the build reads.

**ADR 0002 is corrected rather than left standing.** Its ruling on the CI job, its `windows-latest`
reasoning and its account of what a suite is a floor on are untouched. Its statement that *"the floor
is 3.10"*, as a single number, is superseded by ruling 1 — see ruling 14. ADR 0139 ruling 3's check
is superseded in scope by ruling 10 and its ruling 4 is discharged by this record.

## Measured before ruling, at `82092fc`

Freshness gate `FRESH` before reading the ticket, `STALE` when the record was opened — `main` had
advanced mid-session — and `FRESH` again after the branch was brought forward, with every figure
below re-derived on the new base. Each figure was taken by running a command.

**The tree-wide floor is 3.11 and the non-test floor is 3.10.** The derivation was an AST walk with
three confidence tiers, driven against a positive control carrying every vocabulary item, a negative
control of 3.7-only code, and a pair of files identical but for `from __future__ import annotations`,
before any of its output was believed.

| | |
| --- | --- |
| tree-wide floor, tests included | **3.11** |
| non-test floor | **3.10** |
| witnesses above 3.10 | **3**, all `contextlib.chdir`, all in `tools/test_tracker_publish_hook.py` |
| non-test `zip(strict=True)` sites | **9**, in six modules |
| `sys.version_info` anywhere in `tools/` | **0** |
| tracked `.py` outside `tools/*.py` | **0** |
| `tools/*.py` | **222**, of which **97** are non-test |
| modules carrying `from __future__ import annotations` | **197** |
| non-test modules with a `__main__` guard | **70** |

`contextlib.chdir` is *"Added in version 3.11"*, fetched from `docs.python.org` rather than recalled,
and it is unguarded — no `sys.version_info`, no `try`/`except ImportError`. It arrived in `14cd092`
on 2026-09-08, two days after #927's body recorded a clean baseline, and was found by a tracker sweep
three days later. *Had it not set the tree-wide floor, replacing it with `contextlib.nullcontext`
would leave that floor unmoved; it moves it to 3.10.*

**The non-test 3.10 verdict is redundantly evidenced.** Deleting every `strict=True` leaves 3.10
through five evaluated PEP 604 annotations in `tools/prose_bind.py`, the only non-test module with no
future import; deleting those as well drops it to 3.9.

**Nothing in the tree is at 3.12 or above**, by the AST walk and by an independent regex sweep for
sixteen high-version names that agreed on every one.

**The instrument's first run reported a false floor of 3.12**, on twelve `.walk(...)` calls that were
all `self.walk(...)` — ordinary test helper methods read as `pathlib.Path.walk`. Caught by the
controls, not by review. That is ruling 9's evidence, taken before ruling 9 existed.

**`AGENTS.md` has three tiers and states no interpreter version at all.** Fifteen modules under
*depends on*, six it says you may *"skip … and the skill still works"*, five repo-hygiene tools. Its
line 82 is a prerequisites paragraph that names PyMuPDF as a required package for four skills and
names no Python version for any skill. *Had a version been stated, a grep of `AGENTS.md` for `3.1`
would return it; it returns nothing.*

**Three populations of consumer roots were derived and they disagree.** The modules `AGENTS.md`
declares, the modules a skill file invokes with a literal `python tools/X.py`, and their symmetric
difference:

| | roots | closure over `tools/` |
| --- | ---: | ---: |
| `AGENTS.md` *depends on* tier | 15 | 29 |
| `AGENTS.md`, all three tiers | 26 | 51 |
| invoked by a skill file | 30 | 54 |

**Nine modules a skill file runs are declared nowhere in `AGENTS.md`** — `aar_scan`,
`case_study_scan`, `docx_read`, `docx_word_probe`, `docx_write`, `guidelines_search`, `name_index`,
`peer_critique_scan`, `voice_model_scan`. A grep of `AGENTS.md` for each stem, with and without the
`tools/` prefix, returns zero for all nine. `peer_critique_scan.py` is the sole grader for a skill
`AGENTS.md` tables by name.

**The largest tier-2 root is one `AGENTS.md` calls skippable.** `tools/differential_scan.py` imports
`threshold_sheet` at module scope, which pulls the whole guideline subtree — twelve further modules,
four of them carrying `zip(strict=)`. *Were the import lazy, as `page_image` and `page_text` wrap the
PDF engine, the match would carry leading whitespace; it is at column 0.*

**CI is one job.** `.github/workflows/checks.yml`, `suite`, `runs-on: windows-latest`,
`python-version: '3.14'`. `tools/suite.py` takes only `--jobs` and `--slowest`, so there is no
existing way to run a subset of the suite.

**`tools/python_floor.py` does not exist**, and three separate tracker sweeps used that absence as
their discrimination check. `tools/test_python_floor.py` does exist and is two things: a `path:NNN`
coordinate ratchet, and `TheStatedFloorHasEvidence`, which asserts that evidence *for* 3.10 is
present and asserts no ceiling whatever.

## Ruling 1. The repository has two floors and states them separately

A **consumer floor** and a **tooling floor**. The consumer floor is the minimum interpreter that runs
every command a skill tells a consumer to type. The tooling floor is the minimum interpreter that
runs the suite. They are two numbers, they are allowed to differ, and each is published where its
reader is.

The single number this repository publishes today is wrong in both directions at once: too low for
the suite, which needs 3.11, and too high for a consumer whose only path is the ICD lookup, which
parses at 3.7. That is #927's title, and one number cannot express it.

The alternative of one number taken as the maximum was declined because it makes a consumer's
install instruction hostage to a test module's import, which is the coupling that let
`contextlib.chdir` land unnoticed. The alternative of declaring only a consumer floor was declined
because `README.md` sends a contributor through the same install and would then tell them nothing.

## Ruling 2. The consumer floor asserts in both directions; the tooling floor ratchets

The consumer floor is an **equality**. A derived value above or below the declared one is a finding.
The tooling floor is a **ratchet**: a derived value above the declared baseline is a finding, and
raising the baseline is a deliberate edit.

The asymmetry is the point rather than a compromise, and it turns on who reads each number. The
consumer number is acted on by a stranger following `README.md` — being wrong in either direction
sends them somewhere. The tooling number is read by the maintainer, who has 3.14 installed and will
not act on it.

**The downward direction is what keeps the walk worth having.** A job pinned at the floor answers
*"does it run at 3.10?"* and can never answer *"is 3.10 more than we need?"*, because it stays green
forever after the last 3.10 feature leaves the tree. `README.md` spends a Homebrew install on that
number; nothing else would ever report that the install had stopped being necessary.

A cleanup that removes the last consumer-side `zip(strict=True)` therefore goes red. That is correct
and it is cheap: the remedy is editing three numbers down.

## Ruling 3. The consumer population is every module a skill file invokes, closed over imports

The roots are the modules named in a literal `python tools/X.py` in any skill file, including the
reference sheets under `skills/_shared/`. The population is their transitive import closure within
`tools/`.

Not the `AGENTS.md` declaration, and not either of its tiers. The floor exists because a consumer
follows an instruction and gets a `TypeError`; that consumer does not care which tier the tool was
filed under, and `AGENTS.md` line 30's *"skip every one of those and the skill still works"* is true
and irrelevant to the consumer who did not skip it.

`skills/_shared/` is in because a reference sheet's command is copied by a run exactly as a
`SKILL.md`'s is. A tool named in prose with no command is out, because nobody types a prose pointer,
and counting one would drag `repo_root` and `prose_bind` in as roots when they are already in the
closure where they belong.

**Making the two populations equal was declined.** ADR 0181 ruling 15 names `day_file_text.py` in
`AGENTS.md` while saying in as many words that *"`batch-shift` is not moved into the
depends-on-a-tool group."* Forcing the declaration to cover every invocation would legislate that
distinction away. The divergence is reported instead, under ruling 11.

## Ruling 4. An interpreter runs, and the floor stops being inferred

ADR 0002 records that *"only a job that runs on it can settle it, and that is a second decision rather
than a correction."* This is that decision: CI gains a job at the floor.

A static walk cannot discharge it. Its largest blind spot is not its vocabulary but its annotation
model — 197 of 222 modules defer their annotations, and `typing.get_type_hints` and `dataclasses`
evaluate those strings at runtime, so a real dependency can sit in an annotation the walk scores as
free. No static instrument closes that. An interpreter closes it on every run, for free.

**This lands here rather than on [#773](https://github.com/mshamblin5150-code/clinical-skills/issues/773).**
That ticket's decision 3 reads *"if a macOS job lands, a 3.10 job is nearly free"*, which has the
dependency backwards: the floor job needs no second platform, only a `python-version` value on the
runner that already exists. #773's genuine subject is the platform and the `os.symlink` branch
nobody has executed, and that stays its.

## Ruling 5. One full-suite job at the consumer floor, and `contextlib.chdir` is repaired

The job runs the **whole suite** at the consumer floor. The three `contextlib.chdir` calls in
`tools/test_tracker_publish_hook.py` are replaced with `os.chdir` in a `try`/`finally`, which returns
the tooling floor to the consumer floor and lets one job measure both.

Three alternatives were weighed and two were refused on measurement.

**An import-only smoke job does not discriminate.** Every consumer-floor witness in the tree is a
runtime API *inside a function* — `zip(strict=True)` at `tools/guidelines_catalog.py:203` is the
worked case — so importing every closure module would be green at 3.10 and green at 3.9 alike. An
instrument that prints the same thing whether the claim is true or false settles nothing.

**A derived subset job — each closure module's own `test_M.py` — discriminates but costs a selection
path the suite does not have**, plus a permanent obligation to report which closure modules have no
test and what that leaves unmeasured, for a number identical to the one the whole suite gives.

**The ratchet survives and stays two-valued.** `TOOLING_FLOOR` may exceed `CONSUMER_FLOOR`; the day
it does, this job splits in two and the subset selection becomes real work. That is the right price.
Three `contextlib.chdir` calls bought a marginally tidier test, and under a one-line ratchet bump
they would have silently bought a second CI job forever.

The job is advisory on ADR 0002's existing posture: not a required status check, and it blocks
nothing.

## Ruling 6. Both numbers live in one declared object and the prose copies are bound to it

`tools/python_floor.py` declares `CONSUMER_FLOOR` and `TOOLING_FLOOR` beside the version-gated
vocabulary and the object's declared limits. A test parses `README.md` and `CLAUDE.md` and fails when
either states a number the object does not hold — `test_spelling_scan.py`'s table-parity arrangement,
at the width of a version.

Bound rather than deleted. A person choosing what to install has not cloned anything yet, so the
number has to be legible in prose; what keeps it true is the bind, not its absence. Three live copies
exist today and one of them is already wrong, which is #220 with a stranger on the other end.

## Ruling 7. `AGENTS.md` states the consumer floor

It goes in the prerequisites paragraph that already exists for PyMuPDF.

`AGENTS.md`'s silence is the sharper half of the gap. It is the contract this repository advertises,
it has a paragraph whose whole job is stating what a machine needs before a skill will run, it names
a package there, and it names no interpreter. An agent reading only `AGENTS.md` gets a `TypeError`
out of `deck_scan` with nothing in the file it read having mentioned a version. It is also the file
that says *"The lookup still needs nothing installed"*, which is true of the database and silent
about the interpreter underneath it.

## Ruling 8. `CLAUDE.md`'s floor paragraph names its floor and its witness

The paragraph currently reading *"The floor is 3.10"* sits in the **Continuous integration** section,
so it states the tooling floor and must say so. Under ruling 5 the number stays 3.10, and the
paragraph must name the `contextlib.chdir` episode as what the repair discharged — otherwise a record
whose own subject is having been wrong about the floor twice carries a third account that omits the
one witness nobody's list contained.

## Ruling 9. Only `syntax` and resolved-`api` witnesses may set a floor

The vocabulary has three tiers and they differ in how much the instrument knows. `syntax` is grammar
and is certain. `api` resolved traces the name through the module's own import bindings, or is a
builtin demonstrably not shadowed. `api-heuristic` is a bare attribute name with the receiver's type
unknown.

The first two grade. The third is **counted and printed on every run, never graded**.

The failure direction decides it. A false positive here does not merely annoy the maintainer, it
propagates outward into an install instruction — the remedy a spurious finding demands is editing
`README.md` to tell a stranger to install a newer interpreter. This repository has ruled the same way
every time: `case_study_scan` counts em dashes and grades none, `differential_scan`'s row-24
candidates never change the exit status, and `research_ledger`'s declined parser row is implemented
and run against correct orders to price its false alarms. The `.walk` episode above is this tier's
recorded instance, and it happened before the tool existed.

Dropping the tier was also declined. A heuristic witness at 3.9 says nothing, but one at 3.12 is the
first sign that something arrived the resolved tier cannot see, and an instrument that finds only what
it can fully resolve reports clean.

## Ruling 10. The deliverable is a command plus assertions in the existing test module

`tools/python_floor.py` is the command; the assertions live in `tools/test_python_floor.py` beside
`TheStatedFloorHasEvidence`, which they supersede in scope — that class asserts a floor exists and
these assert what it is.

**No pre-commit gate.** `CLAUDE.md` argues the conditional refusers are affordable because they
*"cost nothing on a commit that touches none of their artifacts — which is what keeps them from
becoming checks people learn to `--no-verify` around."* A gate keyed on staged `tools/*.py` fires on
nearly every commit here and costs an AST parse of the whole tree each time. The suite and the CI job
hold the line.

**A command rather than a test alone**, because the number is the deliverable: the corrected prose
points at something runnable, and when the equality assert reports that the consumer floor could be
lowered, the next thing anyone does is run it and read the witnesses.

**Not a `run_grader` member**, by that family's own boundary rather than by preference —
`apa7_coverage.py` is deliberately outside it *"because it grades a committed registry rather than a
per-run survey"*, and this grades the tree.

Exit **0** clean, **1** a finding, **2** every way of not having walked. Output is counts, module
paths, line numbers and feature names, which is everything the code can draw on, so there is no
`--show` and the report is pasteable. Both floors and both populations print on every run, including
a clean one.

## Ruling 11. The population is derived from the index, and the undeclared nine are its denominator

The walk derives its population from `git ls-files '*.py'` rather than globbing `tools/`, so a `.py`
arriving elsewhere is counted rather than silently outside the walk. At the measurement above there
are none, and the hooks are `/bin/sh`.

The count and names of the modules a skill file invokes that `AGENTS.md` declares nowhere **print on
every run and are never graded**. That figure is not a second subject; it is this walk's denominator.
Ruling 3 keyed the consumer floor on a population every tracked document describes differently, and a
tool that walks one while the prose describes the other, never saying they differ by nine, is the
partial instrument this repository keeps recording.

Grading it to zero was declined under ruling 3's reasoning. Whether a module belongs in the
*depends on* tier is an editorial judgment about whether the skill works without it, which no walk can
settle, so the nine are filed for a person instead.

## Ruling 12. A consumer below the floor gets one legible line

`console_codec.py` gains a second exported function that refuses an interpreter below
`CONSUMER_FLOOR`, called from the same two shapes `use_utf8` already uses: directly under `__main__`
for the 52 commands that do not import `run_grader`, and once inside `run_grader.run()` for the 18
that do.
`test_console_codec.py`'s existing AST walk extends to assert both.

Nothing else in this record helps the person the floor exists for. The walk proves the tree is
consistent; the job proves the suite runs. A Mac user on Apple's 3.9.6 who runs
`python tools/deck_scan.py` still gets a `TypeError` out of a grader, which #773 records reads
*"as a broken repository rather than as a too-old interpreter."*

**Folding the check into `use_utf8` was declined.** `CLAUDE.md` states that `console_codec.py`
*"holds one line of policy"*, and a function named `use_utf8` that also exits the process on an old
interpreter is a name that no longer describes what it does.

`use_utf8()` is called **first** and the guard second. `sys.stdout.reconfigure` is a 3.7 API, so it
works on the old interpreter, and the message then prints through a fixed codec rather than being
constrained to ASCII. The exit status is **2**, the house code for *did not run*.

## Ruling 13. #773's decisions 2 and 3 are discharged and its other two survive

Ruling 12 is #773's decision 2 and ruling 4 is its decision 3. Its decision 1, a macOS CI job, and
its decision 4, `skills_mirror.py` verifying what it created, are about a platform and a link and are
untouched here. #773 is respecified rather than closed.

## Ruling 14. ADR 0002's single-number floor paragraph is superseded

Both ADR 0002 and ADR 0139 take a dated line at the bottom pointing here. ADR 0002 takes one thing
more: its sentence *"the floor is 3.10"* is not merely dated, it is the wrong shape, and a dated
pointer alone would leave a reader who stops at that record holding one number — which is the failure
this whole ticket is about. So that paragraph is superseded by ruling 1, named the way
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
names ADR 0033 ruling 3. Its CI ruling and its `windows-latest` reasoning stand.

## What the build verifies

The derived consumer floor equals `CONSUMER_FLOOR` in both directions, and the derived tooling floor
does not exceed `TOOLING_FLOOR`. Both are 3.10 at this record's measurement, so the first run lands
clean and the repair under ruling 5 is what makes the second of those true.

`README.md`, `CLAUDE.md` and `AGENTS.md` state no Python version the declared object does not hold,
in both directions, so a number added to prose without the object fails as surely as one that drifts.

Every command path calls the guard, by the AST walk that already proves every command path calls
`use_utf8`, in both its direct and its `run_grader` shape.

The instrument is live before its output is believed: a positive control carrying every vocabulary
item, a negative control of 3.7-only code that yields nothing, and a discrimination pair identical but
for the future import. A tier promoted from `api-heuristic` to grading fails a test.

The walk's population reconciles — every tracked `.py` is read or named as unread, and the consumer
closure plus the undeclared nine are reported whether or not anything fires.

## What this record does not settle

**Whether a pin exists that neither the walk nor the job can see.** The walk is a floor on literal
shapes with a named vocabulary; the job is one interpreter on one platform. A dependency reachable
only on a path no test exercises is outside both.

**The deferred-annotation hole, for anything the job does not execute.** 197 of 222 modules defer
their annotations. The job closes this for every line the suite runs and for nothing else.

**Whether the vocabulary's version assignments are right.** Only `contextlib.chdir` was verified
against primary source, because it was the one that decided an answer. An entry off by a version
moves nothing today and could move something later.

**A module that will not import on the old interpreter.** Ruling 12's guard runs on the command path,
so it cannot help when the failure is at import time of a closure module — `tools/prose_bind.py`
evaluates `FenceOpening | None` at definition time and would raise on 3.9 before any `__main__` block
existed to have guarded it.

**Whether `AGENTS.md` should declare the nine.** Ruling 11 reports them and ruling 3 declines to
legislate the tier. The judgment is a person's and is filed.

**macOS and the `os.symlink` branch**, which stay #773's under ruling 13.

**A consumer with no Python at all.** Unchanged by everything here.
