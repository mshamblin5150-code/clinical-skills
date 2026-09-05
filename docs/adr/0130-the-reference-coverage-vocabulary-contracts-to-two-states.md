# The reference coverage vocabulary contracts to two states

[#893](https://github.com/mshamblin5150-code/clinical-skills/issues/893) recorded that
[ADR 0097](0097-the-apa-sheet-s-class-vocabulary-is-apa-s-nursing-set-and-coverage-is-decided-per-bucket-while-the-gate-is-a-bind-test.md)
ruling 6's three-state coverage machine expires when
[#757](https://github.com/mshamblin5150-code/clinical-skills/issues/757) lands: `COVERAGE_FINDING`
becomes unreachable and `CONTEXT.md` names a state nothing can produce. The ticket recorded the
finding and ruled nothing, because #804's scope forbade widening.
[ADR 0129](0129-the-apa-form-heading-declares-itself-and-its-tail-is-exact.md)'s *whether the bucket
state machine survives its own success* files the same question and defers it for the same reason.
This record is its answer. Grilled and ruled 2026-09-04.

## Measured before ruling, at `1730f7a`, re-derived after merging `92ac70b`

`main` advanced mid-session and the freshness gate went `STALE` between the read and the
publication, which is what [#320](https://github.com/mshamblin5150-code/clinical-skills/issues/320)'s
second checkpoint exists to catch. The merge is #894, ADR 0129 — **a record and no code** — so every
derivation below was re-run against the rebased tree and reproduces unchanged rather than being
carried forward.

**The ticket's derivation reproduces.** Evaluating every declared bucket with `has_form` forced true
on every class leaves `COVERAGE_CLEAN` and `COVERAGE_UNDECIDABLE` reachable and
`COVERAGE_FINDING` reachable from nothing. The per-bucket table is #893's and is not copied here;
one command over `reference_scan.REFERENCE_BUCKETS` re-derives it.

**A fourth consequence the ticket does not name, and it is the sharpest.**
`tools/reference_class_census.py`'s `main` ends `return 1 if result.uncovered else 0`, and
`Census.uncovered` sums the populations of finding-state buckets alone. That command therefore loses
its exit 1 outright — 0 and 2 remain — while its own module docstring continues to document a status
no run can produce.

**The decision cannot be deferred past #757 by accident.**
`tools/test_reference_scan.py`'s `ReferenceCoverageIsClassifiedByDeclaredBuckets` asserts in as many
words that the StatPearls and Cochrane buckets report `COVERAGE_FINDING`. Both assertions go red the
moment the sheet covers those classes, so #757's builder edits this machinery either way.

**Correction, 2026-09-04, hours after this record merged: the breakage is four assertions and not
two, and ruling 4 is reopened by it.** The sentence above was measured by reading the two subtests
rather than by simulating the build. Simulated — every `APA_SOURCE_CLASS` flipped to `has_form=True`
with `dataclasses.replace`, both suites run in process — 177 tests give five red, of which
`test_has_form_is_bound_to_the_sheet_headings_in_both_directions` is an artifact of flipping the
column without adding the sheet sections and stays green in the real build. The four that are real
are the two named above plus:

* `tools/test_reference_scan.py:1603` `test_uncovered_class_is_advisory_and_not_a_body_or_graded_row`,
  which asserts `len(result.coverage_findings) == 1` at `:1614` over a Cochrane entry. Covering
  Cochrane empties that list, and the assertion is that a coverage finding **exists at all**, so no
  expected-state edit repairs it.
* `tools/test_reference_class_census.py:157`
  `test_finding_is_exit_one_and_report_names_no_corpus_text`, which fails `AssertionError: 0 != 1` at
  `:170` — the exit-1 loss this section describes, arriving at **#757's** merge rather than at #893's
  build.

**Those two are rulings 1 and 2's own subjects**, so neither can be repaired without doing part of
what ruling 4 assigns to the separate build. Ruling 4's *minimal repair … and nothing else*
instruction is therefore unsatisfiable as written, and the split as ruled leaves a red window: #757
cannot merge green under it, and #893 cannot land first while the coverage finding is still
reachable and correct. **That cost was not priced and the clinician was not shown it.** Ruling 4
stands as ratified until he rules again; the candidate resolutions are recorded on #893 and none is
adopted here.

**The method is the transferable part.** The original figure came from reading the two assertions
that name `COVERAGE_FINDING`; the honest instrument was to force the column and run the suites,
which is `block_scan.py`'s and `threshold_sheet.py`'s recorded lesson — both of their parser bugs
were found by pointing the tool at real material and neither by a fixture — arriving on a record's
own measurement rather than on a parser. It was caught by the tracker sweep this record's session
was obliged to run, which is
[#320](https://github.com/mshamblin5150-code/clinical-skills/issues/320)'s and the sweep rule's
whole argument.

**The keeping argument was checked against the tree and does not hold.** #893's option 1 rests on
detecting a future class arriving uncovered. The class vocabulary is a hand-written module object and
`TheNursingSourceClassTableIsBoundToTheSheet` compares it against a second hand-written copy in the
test module, so adding a class turns the suite red and forces a person to look before the coverage
state could speak. A section removed from the sheet fails the same class's bidirectional bind. In
every path found, something else fails first.

**That bind is itself under repair, and this record assumes the repaired form.** ADR 0129 rules the
heading identity a canonical grammar because the substring filter cannot represent a class name
nested inside another, and #757 is blocked on it. The repair does not change the direction relied on
here — `has_form` stays bound to the sheet's headings both ways — but a reader arriving before it
lands should not read the sentence above as a description of the code in front of them.

**Where an ordinary reference actually lands.** `classify_entry` sends a work carrying a DOI to
`doi-work`, an unmatched web signal to `identified-web` and anything with no decisive signal to
`unresolved`. All three declare `spans_outside_set`, so all three are permanently
`COVERAGE_UNDECIDABLE`. The undecidable remainder is therefore where the bulk of any real reference
list sits, not an exceptional tail.

**The census has no caller.** No skill, no CI step and no hook invokes
`tools/reference_class_census.py`; `CLAUDE.md` documents it and nothing else runs it. ADR 0097 ruling
6's protection of the exit status is about the per-run row, which
`skills/discussion-post/SKILL.md` requires to exit 0. It does not reach this command, whose non-zero
status is free.

## Ruled 2026-09-04

### 1. The coverage finding is retired rather than kept as a tripwire against a future class

`COVERAGE_FINDING`, `UNCOVERED_CLASS`, the `CoverageFinding` record, `Scan.coverage_findings` and
both report lines that print them come out. The two live states remain.

The machinery's stated job is discharged earlier by tests that refuse the commit, so what survives is
a report line that can only read zero — the settled-negative shape this repository catches itself on
by name, and the weakness ADR 0097 already admits about ruling 6 in *an advisory line on a report
nobody reads*.

**This is not tuning the corpus until the instrument fires.** #893's prohibition stands: no class
leaves the vocabulary and no section is withheld from #757 to keep a bucket reporting a finding. The
gate was genuinely exercised before it was satisfied, which is what ADR 0097 ruling 10's split
bought, and it is retired because it ran out of subject rather than because it was inconvenient.

### 2. The census keeps no finding status

`reference_class_census.py` returns 0 for a completed count and 2 for every way of not having
completed one, with a docstring sentence saying there is no 1 and why — on `threshold_draft.py`'s
precedent, whose own reason is that a draft has no *found nothing* to report. A census counts; it
does not grade.

**Re-pointing the 1 at the undecidable remainder was refused on the measurement above.** That
remainder is where an everyday journal article lands, so binding a failure to it makes the command
permanently red over a corpus that has done nothing wrong — the false-alarm-on-correct-work shape
refused by ADR 0089 ruling 5 and by ADR 0097 ruling 6 itself.

**Deleting the command was refused as too far.** Counting which source shapes the account's
coursework actually cites is a live question, and ADR 0097 ruling 2's second reader exists to make it
askable.

### 3. The coverage calculation keeps consulting the per-class column, with a positive control

`ReferenceBucket.state` keeps reading `has_form` after the finding limb comes out. It does not
collapse to a direct read of `spans_outside_set`, even though the two agree on every bucket the tree
can hold once the sheet is complete.

**The collapse reports a wrongly reassuring `clean`, and that is what decides it.** Give a future
class no section and a dedicated bucket, and the collapsed form calls it covered while the retained
calculation calls it undecidable. A false `clean` is the worst outcome available here and it costs
one comparison to avoid.

**The countervailing rule is named rather than ignored.** `docx_write.py`'s *a second mechanism that
cannot fail is not a belt and braces; it is a line that costs a test* is aimed at exactly this shape.
It does not carry, because this limb can fail — in the one case where deleting it lies. A test drives
it by declaring a class with no form, so it is a proven-live branch rather than one nobody exercises.

**`COVERAGE_UNDECIDABLE` keeps its name.** For a work carrying a DOI the reader genuinely cannot tell
whether the source is a class the sheet covers or one outside the set, so the word stays accurate and
a rename to something naming the outside-set case alone would make it less so.

### 4. The build is separate, gated on #757, and its premise is conditional on a page nobody has read

#757 makes the minimal repair its own change forces — the two bucket assertions become
`COVERAGE_CLEAN` — and nothing else. The retirement is #893's own build, which starts by re-deriving
the state table against what actually landed.

**Folding it into #757 was refused on that ticket's own terms.** Its *what must not come out of this*
list ends with **any change to #715's mechanism**, and this is such a change; folding would mean
amending a prohibition #757 placed deliberately. #757 is also blocked on a public-repository
copyright question about its synthesized strings and is a large content fill, so coupling a
state-machine change to it joins two unrelated risks.

**The premise is not established.** #757's finish line permits an item to be *accounted for by the
general-index section with a reason* rather than receiving its own section, and it instructs its
builder to check the inherited claims about APA's page at the read rather than inherit them, because
no session in this repository has been able to open that host. If a class lands without a form,
`COVERAGE_FINDING` stays reachable and this ruling does not fire. **The build's first step is the
derivation, and a class without a form returns #893 to the clinician rather than proceeding.**

#893 therefore carries `blocked` rather than `ready-for-agent`. The test that flips it: #757 on
`main`, and the derivation still showing the finding state unreachable.

## What this record does not settle

**Whether APA's *Nursing Student References* page holds what ADR 0097 inherited about it.** That
record already declares the three claims as unchecked and #757 owns the read. Ruling 4 is written so
this record fails safe if the read comes back otherwise.

**`CONTEXT.md` is deliberately not edited by the session that wrote this.**
`test_context_names_the_bucket_vocabulary_and_all_three_states` asserts the literal `**finding**`
appears in the glossary, so removing it now turns the suite red on a tree where the state still fires
correctly. The replacement sentence is carried in #893's body for the builder to land with the code,
and the test contracts to the two surviving states in the same change.

**ADR 0097 ruling 6 is superseded in part rather than reversed.** Its posture ruling — that a
repository gap must never reach a student's coursework — is untouched and is why the row was never
graded. What expires is the row's subject. The bucket populations and the undecidable remainder
continue to print on every run on
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling.

**Whether `has_form` remains worth carrying per class once the sheet is complete.** It is all-true on
a covered sheet and survives as the bind test's anchor and as ruling 3's input. Whether a column that
is constant on every shippable tree earns its place is a question about the bind test rather than
about coverage, and it is not asked here.

**No count of covered classes, sections or buckets appears in this record.**
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143); those figures belong to
`reference_scan.APA_SOURCE_CLASSES`, `reference_scan.REFERENCE_BUCKETS` and the commands that read
them.
