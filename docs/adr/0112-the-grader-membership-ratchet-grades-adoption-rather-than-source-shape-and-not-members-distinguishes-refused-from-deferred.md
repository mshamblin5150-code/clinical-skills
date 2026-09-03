# The grader membership ratchet grades adoption rather than source shape and not-members distinguishes refused from deferred

Found while grilling [#830](https://github.com/mshamblin5150-code/clinical-skills/issues/830),
2026-09-02, at `origin/main` `7ad784e`, freshness gate `FRESH` at both checkpoints. **Ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

## Measured before ruling, at `7ad784e`

Every figure was re-derived by running the code rather than by reading it, and each disagrees with
the ticket that prompted the grilling.

**`run_grader.MEMBERS` holds a name that does not use the runner.** Taken from executing
`walk_grader_modules()` and reading each member's source:

```
walk population size:      19
aar_scan in walk population: True
aar_scan in MEMBERS:         True
aar_scan top-level survey:   True | format_report: True
MEMBERS that do NOT import run_grader:
    aar_scan
```

`aar_scan.py` carries a hand-rolled `main()` — its own usage string, its own flag parsing, its own
`print(format_report(...))`, its own return codes. It imports nothing from `run_grader`.

**The ratchet that was supposed to prevent this graded something else.** `test_run_grader.py`
asserts `walk_grader_modules() == MEMBERS | NOT_MEMBERS`, and that walk's predicate is *top-level
`survey`, top-level `format_report`, and a `__main__` guard* — **source shape**. `aar_scan`
satisfies the shape, so the walk went red on its landing branch, and the commit turned it green by
appending one line: `"aar_scan",`.

**The conformance kit is adopted by 12 of 15 members.** `aar_scan`, `deck_scan` and
`voice_model_scan` do not call `grader_conformance.for_module`, and none of their test modules
contains a marker, a salt, a redaction assertion, or a `show=True`/`show=False` pair. All ten
members migrated on [#405](https://github.com/mshamblin5150-code/clinical-skills/issues/405) adopt
it; all three non-adopters arrived after 2026-08-28.

**Both defects passed the same green walk**, which is the finding rather than either one alone.

**The frame itself has been stable.** Seven commits touched `run_grader.py` after the migration;
six changed exactly one line, appending a name. Only
[#475](https://github.com/mshamblin5150-code/clinical-skills/issues/475) on 2026-08-23 changed its
shape. Four members have joined since and needed no field.

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. They move the day
a grader lands, and ruling 1 is what stops them mattering.

## What is ruled

**Ruling 1. Membership is delegation, and the ratchet grades delegation.** A name in
`run_grader.MEMBERS` asserts that the module runs on the shared runner. A walk over `MEMBERS`
requires each member to import `run_grader` and each member's test module to adopt
`grader_conformance.for_module`. The existing shape walk stays; it answers a different question and
is a floor on visibility, never a claim about adoption.

**The two walks are not redundant and the reason is the direction each fails in.** The shape walk
catches a grader arriving that nobody declared — #405's landing case, where a member could otherwise
merge silently. The adoption walk catches a name declared that nobody wired up. Neither sees the
other's case, and `aar_scan` is the recorded instance of the second passing through the first.

**Ruling 2. `NOT_MEMBERS` distinguishes a refusal from a deferral, and the two are separate
mappings.** A **refused** module is a permanent verdict: the runner cannot express what it does.
A **deferred** module is open work with a named owner. Today `corpus_census`, `threshold_sheet` and
`tracker_bodies` are refusals and `filled_vitals_census` is a deferral.

**One mapping could not tell them apart, and that is the same defect one level up.** The single
assertion `all(NOT_MEMBERS.values())` proves a reason was written, never which kind of reason it is
— so a deferral reads as a settled exclusion and nothing schedules its review. That is a declared
limit going stale in the direction nobody notices, which is
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s subject, arriving on a
membership roster.

**Ruling 3. `aar_scan` is deferred, not refused, and its entry must say what migration would take.**
Its graded path fits the runner. What does not fit is a second entry point and a side effect:
`--session-end` takes no positional source and `run_grader.parse` raises on `if not positionals`,
and `consume_orphans` unlinks files only on a clean grade, after the report, where `run()` returns
`0` with no hook.

**It is not `threshold_sheet` and its entry may not read as though it were.** That module is refused
because its *graded* path cannot work under the runner — no quiet suppression, no worst-of-N status,
which is [#410](https://github.com/mshamblin5150-code/clinical-skills/issues/410) decision 3.
`aar_scan`'s obstacles are both outside its graded path and both are soluble, so writing
*structurally excluded* there would ship the same overclaim this record exists to correct.

**Ruling 4. The guard is a walk in the shared test kit and never structure in the runner.**
[ADR 0094](0094-a-tool-s-show-output-is-unpasteable-by-default-and-its-own-docstring-is-the-only-authority.md)
declares that **`run_grader` does not speak for its members** — a verdict on the runner would be a
claim about every grader that delegates to it. A structural redaction gate inside `run_grader.run`
is exactly that claim, so it is foreclosed here rather than left to be re-proposed.

**The walk is not the same act and that is why it survives the same ADR.** It asserts a behavioral
property of each member's own `format_report` — a salted marker reaches `--show` and does not reach
the default — and makes no claim about any module's disclosure posture, which stays that module's
docstring's under ADR 0094 ruling 2. Ruling 4 of that record blesses precisely this distribution,
calling a guarded aperture beside a silent default *the correct distribution*.

## What this does not reach, declared rather than left to be found

**Whether a member's report is correct.** The walk proves a marker is redacted and a member is
wired to the runner. It says nothing about whether the report says a true thing, which is every
member's own tests' subject.

**A grader that assembles its parts under other names.** The shape walk's ceiling is already
declared in `run_grader.WALK_CEILING` and the adoption walk inherits it: it iterates `MEMBERS`, so a
module that is neither declared nor shaped like a grader is invisible to both walks.

**Whether a deferral is being worked on.** Ruling 2 makes the state visible and nothing schedules
it. A deferred entry can sit for as long as a refused one; what changes is only that a reader can
tell which they are looking at.

**The three non-adopting members' redaction posture is not thereby reviewed.** The walk will fail
until each adopts, and adoption proves the marker property from that day. Neither this record nor
the walk says anything about what those three modules' `--show` output has been until now.
