# The conformance kit shapes a migrating grader's value and vocabulary and the fixture row is the finding kind

Found while grilling [#842](https://github.com/mshamblin5150-code/clinical-skills/issues/842) and
[#840](https://github.com/mshamblin5150-code/clinical-skills/issues/840), 2026-09-03. Opened at
`origin/main` `6cd340a`; `main` moved mid-session when
[#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839) and
[#843](https://github.com/mshamblin5150-code/clinical-skills/issues/843) landed as one commit, and
every figure below was re-derived at `3af546c` before ruling. Freshness gate `FRESH` at both
checkpoints. **Ruled by the clinician on that date.** Nothing is built here; this is the record the
build reads. [ADR 0117](0117-a-member-s-obligations-outside-the-graded-path-stay-in-main-and-the-crash-posture-gains-a-finding-sibling.md)
is the other half of the same session.

## The thesis both records share, and neither ticket saw it

[ADR 0112](0112-the-grader-membership-ratchet-grades-adoption-rather-than-source-shape-and-not-members-distinguishes-refused-from-deferred.md)
recorded that membership grades **adoption**. **Nobody has recorded that adoption reshapes the
module.** Three of the six decisions #840 and #842 put to a person were settled by the conformance
kit's own mechanics before anyone reached them:

- `grader_conformance._salted_report_input` calls `dataclasses.fields(module.Scan)` and
  `module.Scan(**values)`, so a class **literally named `Scan` carrying a `findings` field** is not
  optional — which answers #842 decision 3 before it is asked.
- `for_module` asserts `tuple(module.ROWS) == module.KINDS` and
  `set(module.ROWS) == constructed_kinds(module)`, so a migrating module must declare a vocabulary
  it may never have had.
- `test_the_modules_own_report_redacts_until_show` reaches a finding through an attribute other than
  `kind`, so `format_report` **must** print finding detail under `--show` — which is a report change
  no ruling can decline.
- `test_run_grader.py`'s ratchet requires every name in `MEMBERS` to import the runner, delegate in
  `main`, **and** have its test module call `for_module`. #842's decision 3 asks whether adoption
  lands in the same commit; the ratchet forbids any other answer.

The kit is a design constraint on a migration and not only a check on one. That is the sentence this
record exists to add.

## Measured before ruling

**`_empty_value` decides each `Scan` field from its annotation** — `bool` to `False`, a container
word to `()`, `str` to `""`, and **everything else to `0`**. A `Scan` holding a nested
`census: Census` therefore receives `0`, and `format_report` doing `scan.census.notes` raises
`AttributeError` inside the conformance probe. The wrapper shape is available only if that field
carries a default `Census` instance: an all-zero sentinel existing to satisfy a test.

**Fourteen of fourteen members construct zero `Finding`s inside their grade function.** Every one
builds findings in `survey` or its helpers; `grade` turns a populated `Scan` into status,
diagnostics and reports. #842 decision 3's second half is settled by that unanimity.

**Thirteen of fourteen use hyphenated descriptions as kinds.** `block_scan` is the exception and it
is this module's twin: its kinds are `F1`, `F2`, `F3` — the row identifiers from
`fixtures/day-a/assertions.md` — with `ROWS` carrying the description. `refusal_scan` is the other
outlier, using spaced phrases.

**Six of fourteen default reports name their declared rows; eight name none.** `block_scan` names
all three of its, from dedicated `f1_failures`/`f2_failures`/`f3_failures` counters rather than from
`findings`. It is a choice and not a house rule.

**That figure was taken twice and the first take measured the wrong property.** A grep for a
findings count line returned six as well, by coincidence and for the wrong reason: ten of fourteen
default reports change when a finding is added, and four do not. Neither of those numbers is the one
ruling 4 rests on, which is whether the report *names a row*.

**`Census` is constructed zero times in `tools/test_filled_vitals_census.py`**, and one test class
name mentions the word. **`Census` names three unrelated things in `tools/`** —
`filled_vitals_census`, `reference_class_census`, `split_census` — while `Scan` is this
repository's word for the value a grader's `survey` returns and its `format_report` reads.

**This report's count lines already are its row outcomes.** `sharing a body with another note` is
B13, `beyond a fair split at 2%?` is B17, `naming no age and sex` is B18 — each stated as a
measurement rather than as a row.

**Measured invocation shapes.** `--show <dir>` already works, because flags are filtered before
`args[0]`; `--submission` with no value already exits 2 with `--submission needs a key`. An unknown
flag is **silently ignored** and exits 1. `--submission --show` grades a submission whose key is the
string `--show` — the same defect [ADR 0117](0117-a-member-s-obligations-outside-the-graded-path-stay-in-main-and-the-crash-posture-gains-a-finding-sibling.md)
records in `aar_scan`.

**#839 landed mid-session and the baseline moved as its own comment predicted.** `read_notes` is
deleted from this module and replaced by `run_grader.read_run_directory` with a hand-rolled
`try/except run_grader.SourceError: return 2`. `run_grader.UNREADABLE_RUN_ARTIFACT` now exists as a
limb constant.

## Ruled 2026-09-03

### 1. `survey` returns a flat `Scan`, and `Census` is renamed rather than wrapped or aliased

Every existing field keeps its name, its comment and its meaning; `findings: tuple[Finding, ...] =
()` is added. The wrapper shape is refused on the measurement above — it buys the word `Census` and
pays with a sentinel census that exists for a test probe. An alias keeping both names gives the
module two words for one thing.

**The rename is a glossary correction rather than a preference**, which is why it is worth doing on
its own terms: it moves one of three unrelated `Census` classes onto the family's word and reduces a
live collision instead of creating one.

Findings are derived in `survey` on the fourteen-of-fourteen measurement. `Census.tilted` and
`Census.gradeable`, which already grade, survive as properties.

### 2. The finding kind is the fixture row identifier, and `detail` carries the count and denominator

`B13`, `B17`, `B18`, with `ROWS` giving the description, on `block_scan`'s precedent.

**`block_scan` did not choose `F1` for brevity.** A row's authoritative definition, its scoring
history and its withheld-verdict status all live in one cell of `assertions.md`, and a paraphrase in
the code becomes a second copy of a rule the fixture owns. **B17 in particular is a false-alarm
rate rather than a count**, and any short hyphenated name for it will be wrong in a way `B17` cannot
be. That the stderr sentences already end `fixtures/day-b B13 fails.` is corroboration, not the
ground.

**`detail` carries counts rather than values**, because the values are already in the `--show`
height and body blocks and a second rendering of the same measurements is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) at close range. It also
keeps the finding line itself non-PHI, so what makes that block private is its neighbors — which is
the honest position and not a weakening of the disclosure class.

**The AAR gate is not a kind.** `differential_scan._grade` folds `aar_failed` into `findings_failed`
with `or` and puts `aar_report` in `reports`, which is what this module's `main` already does. The
vocabulary is three, not four.

### 3. This module declares no exit-2 vocabulary

[ADR 0116](0116-the-read-failure-posture-is-keyed-on-the-input-s-role-and-only-the-crash-is-ruled-family-wide.md)
ruling 6 answered this for a migrating module and said no: prose with no code copy has nothing to
diverge from, and adopting a vocabulary to hold it is a seam change with no ticket behind it. #842 is
a migration.

**ADR 0117 ruling 3 reaches the same answer by a different argument and the two must not be
collapsed.** There the surface is not wholly inside the runner, so a vocabulary would be incomplete
by construction. Here it would be complete; the reason to decline is precedent and scope.

**Declining has a second effect worth naming.** ADR 0116 ruling 5 records that #839's shared reader
raises an uncaught `ValueError: an exit-2 path names no exit-2 limb` in a member that declares a
vocabulary whose limbs do not name it. Declaring here would couple this ticket to importing
`UNREADABLE_RUN_ARTIFACT`; declining leaves the runner supplying the 2 with nothing to import.

**The residue is real and is not closed.** `CLAUDE.md` enumerates this module's limbs in prose and
nothing holds that. It is the same gap `refusal_scan` was ruled to keep, and closing it is one
ticket over all eleven members rather than a clause in a migration.

### 4. The default report is unchanged, and `--show` gains the join

`block_scan` needs its `F` lines because its count block states no row outcome. **This report's
count lines already are its row outcomes**, so adding per-row lines would put each of three
measurements on the page twice under two names.

That leaves the `--show` findings block as the only place a row identifier appears beside its
measurement — **which is the honest thing for it to be.** It is not redundant with the default
report; it is the join between a number a reader can see and the `fixtures/day-b` row that rules on
it, and that join exists nowhere today. The reason a reader comparing this module to `block_scan`
will want is written in the module rather than left to be re-derived.

### 5. The declared list, and what belongs to #839 rather than here

**Byte-identical, and achievable:** the whole report block; the AAR gate line after it, via
`reports=(aar_report,)`; the three finding sentences with the floor note and the
`Re-run with --show` trailer as **one** diagnostics string, since today they are one `print`; both
exit-2 banners; `no directory named X` and `no notes found in X` via `SourceError` with
`source_error_to_stdout=False`; and `--submission needs a key` via `Option(missing_value=...)`.
The runner emits report, then reports, then diagnostics, which is today's order.

**Forced changes:** `--show` gains a findings block; an unrecognized flag exits 2 rather than being
ignored; `--submission --show` exits 2 rather than grading a submission named `--show`.

**Not this ticket's, but on its baseline:** #839's move from an uncaught 1 to a 2 on an unopenable
run artifact. **This ticket deletes the hand-rolled `try/except run_grader.SourceError`**, which
exists only because the module is outside `MEMBERS`; leaving both it and the runner's limb would be
two copies of one policy in a module that had just stopped needing either.

**When both deferrals clear, `run_grader.DEFERRED` becomes an empty mapping and no tree either
branch produced contains it.** Each ticket deletes its own named deferral test;
`test_every_nonmember_verdict_carries_a_reason` then passes vacuously and nothing fails. **Keep the
empty mapping and assert nothing new about it**: removing it is a frame change to a distinction ADR
0112 made deliberately, and a test that it *is* empty asserts today's tree, which this repository
refuses on the ground that a walk finding nothing proves only that. The second ticket to land says
so in its write-up.

## What this does not reach, declared rather than left to be found

**Whether the three rows are the right rows.** B13, B17 and B18 are `fixtures/day-b`'s and this
record moves none of them. B17's 2% false-alarm floor and B18's person rule are the clinician's from
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97) and are untouched.

**The five counted vital classes stay counted and ungraded.** No corpus split grounds a bar on them,
which is #97's own objection holding where it was not answered.

**Ruling 1's rename is not a glossary sweep.** `reference_class_census` and `split_census` keep the
word, correctly — they are counts over a corpus rather than grader values. The collision narrows by
one and is not resolved.

**The thesis is a description and not a check.** Nothing walks `tools/` and reports that the kit
constrained a migration; a future migration discovers it the way this one did, by running
`for_module` and reading what fails.

**Ruling 4 leaves the default report without a findings count**, so a reader who takes the report
alone still learns the outcome from three measurement lines rather than from a verdict. That is
today's behavior preserved and it is a floor, not a claim that the report is complete.
