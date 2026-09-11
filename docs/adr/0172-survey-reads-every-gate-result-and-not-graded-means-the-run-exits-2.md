# Survey reads every gate result and not graded means the run exits 2

[#1004](https://github.com/mshamblin5150-code/clinical-skills/issues/1004) was filed during
[#836](https://github.com/mshamblin5150-code/clinical-skills/issues/836)'s grilling as a shape defect:
`survey` in `tools/threshold_sheet.py` assembles its failure list by naming gates one at a time, and
`gate_edition_currency` is not among them. The grilling found the same assembly three more times in the
same function, and found that one of the four lists is narrow on purpose.

Grilled 2026-09-11 to an empty frontier. **Six rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. It leaves
[ADR 0134](0134-the-guideline-currency-check-is-per-society-reads-what-its-publisher-lists-and-refuses-to-repoint-a-sheet.md)
ruling 5 unchanged, applies
[ADR 0159](0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md)
ruling 3's rule for a field with no production reader to citation tier 0's `not_graded`, and closes
the reporting hole that record's ruling 6 left to #1004.

**Row counts of this module's limit population are not stated anywhere in this record**, on
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)'s
closing instruction.

## Measured before ruling, at `d148087`

Freshness gate `FRESH` at `d148087` before any reading. Every construction of a gate result was read
by AST, and `survey` was driven over the committed sheets by wrapping it and calling `main` with
`--all --quiet`.

**The hole is latent.** `results` holds twelve gate results; the failure list concatenates the
findings of eleven, without edition currency. Both of `gate_edition_currency`'s constructions pass
`lines` and nothing else, and over the 169 committed sheets its findings and warnings were empty on
every one.

**Deriving the failure list moves nothing, and the cost #1004 recorded against it does not exist.**
The 2026-09-10 sweep comment on #1004 said a comprehension over `results` cannot reproduce the
hand-written order. It can: the hand-written order is `results` order with edition currency removed,
which is read off the two sequences. Over the 169 sheets the derived and hand-written lists compared
equal on every one. *That comparison would also have printed equal had the orders differed on a sheet
carrying findings from fewer than two gates, so it establishes no output change, and the order claim
rests on the reading.*

**Warnings are the same shape with the same answer.** Extraction identity, coverage and second read are
the only gates whose constructions set a warning, and they are the three `survey` names, in `results`
order.

**`not_graded` is the third hand-written list, and its omission is policy.** Five gates can set the
flag: page coverage, citation tier 0, coverage, watermark and second read. `survey` reads four; tier 0
is absent. Tier 0 sets the flag whenever a source is `bound` or its recommendation record is absent.
Driven on `reference/thresholds/diabetes.md` — one source, `ada-2026`, `bound` — with its record
supplied in memory, tier 0's flag was set and coverage's was not; the same held with the record absent
and listed as missing. So reading tier 0 would move that sheet from exit 0 to exit 2, which
[ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md)'s
refuse/warn line and
[#181](https://github.com/mshamblin5150-code/clinical-skills/issues/181)'s ruling that a missing record
does not refuse both rule out.

**Nothing on this machine could have caught that change.** The one test pinning the sheet's exit 0,
`TheDiabetesSheetPassesTheExternalCliSeam`, skips here for want of an external second-read record. And
the 169-sheet survey cannot discriminate it: coverage's flag is set on all 169 here, because no
recommendation record is built on this machine, so a derived and a hand-written `not_graded` agree on
every sheet whatever tier 0 does.

**Tier 0's flag has no production reader.** Five assertions in `tools/test_threshold_sheet.py` read it;
nothing in `tools/threshold_sheet.py` does.

**The floor note disagrees with its own condition in both directions.** The note names page coverage,
citation tier 0, coverage and second read; the condition that prints it reads page coverage, coverage,
watermark and second read. Tier 0 entered the sentence without entering the condition in the same
commit, `5a3ddee` on #403. The note fired on none of the 169 sheets.

**Diagnostics is the fourth list, and its order is designed.** Five gates set diagnostics — page
coverage through `survey`'s own replacement, extraction identity, watermark, second read and coverage
— and `survey` reads all five, interleaving them with the `FAIL`, `WARN` and `NOT DIFFED` lines and
splitting watermark's first line from the rest. The other seven set none.

**ADR 0134 ruling 5 already has a test, at the gate rather than the run.** `EditionCurrencyReport`
asserts a `superseded` verdict yields no findings from the gate. Its name says *without changing sheet
status*, and it never calls `survey`.

**ADR 0159 ruling 3's split kept the channel.** Every per-gate type inherits `findings` and `warnings`;
`EditionCurrencyResult("X", findings=["y"])` constructs. #1004's decision 2 would therefore be a type
change #836's build did not make.

## Ruling 1. The failure list is derived from `results`

`survey`'s failure list becomes the findings of every member of `results`, in `results` order. No gate
can be left out, and a gate added to `results` is read without anyone adding it to a second list.

**Removing the failure channel from edition currency's type is declined.** It guards one gate, keeps
the hand-written list that dropped it, and needs a report-only base type for a single member.

**Edition currency still refuses nothing.** ADR 0134 ruling 5 is untouched: the derivation makes the
channel work, and ruling 6's run-level test is what holds ruling 5 in place.

## Ruling 2. The warning list is derived the same way

`survey`'s warnings become the warnings of every member of `results`, in `results` order. A warning
never changes the exit status, so the only effect is that a gate's warning prints rather than
disappearing; keeping three names by hand would leave #1004's trap on the channel where a lost line is
least likely to be noticed.

## Ruling 3. `not_graded` means the run is not graded, and `survey` derives it

A gate sets `not_graded` only when its incompleteness should make the whole run exit 2, and the field
carries that definition. `survey` derives the run's flag from every member of `results`.

**Citation tier 0 stops setting it.** Its `CITATION tier 0 NOT RUN` line already carries the gap and
its row counts, and the exit status the flag would produce is the one ADR 0007 and #181 rule out. Its
five flag assertions move to the emitted line, which is ADR 0159 ruling 3's rule for a field no
production code reads.

**Keeping four names by hand beside a comment is declined.** Tier 0's result would go on saying *not
graded* about a run that deliberately is graded — a field that reads as a verdict and is not one,
which is #1004's own shape.

## Ruling 4. The floor note names the gates that set the flag

When a run has findings and is not completely graded, the note is built from the members of `results`
whose `not_graded` is set on that run, rather than from a fixed sentence. Correcting the fixed sentence
is declined: a fixed list of names beside a computed condition is what drifted, and naming only the
gates that fired tells the reader which line to read.

## Ruling 5. Diagnostics keeps its designed order and gains a remainder

The named interleaving stays. After it, `survey` appends the diagnostics of every member of `results`
the named assembly does not read, in `results` order. Nothing prints differently today, because no
unnamed member sets any.

**A plain derivation is declined** because it would reorder stderr on real runs, and the defect #1004
names is a dropped line, not a misplaced one.

## Ruling 6. The planted test runs through every gate, and the gate population is read from the module

For each gate, a test wraps the real gate so it returns its own result with a planted finding, warning,
not-graded flag and diagnostic line added, runs `survey` over a sheet that otherwise grades clean, and
asserts each reaches the run: status 1
for the finding and status 2 for the flag alone, the planted `FAIL` and `WARN` lines, the gate named in
the floor note, and the planted diagnostic line. The population is the module's `gate_` functions, read
rather than typed, so a new gate is covered without editing the test.

**Against today's code the plant fails** on edition currency for every channel, and on each gate
`survey` does not read for warnings, flags and diagnostics. That is what makes it discriminate rather
than confirm.

Two companions:

- `EditionCurrencyReport` runs through `survey`: a `superseded` verdict leaves the run's status where
  it was without the registry.
- A sheet with one `bound` source, its record built in memory, exits 0 and prints
  `CITATION tier 0 NOT RUN`. It needs no external input and cannot skip.

## What the build verifies

`python tools/threshold_sheet.py --all` and `--all --quiet` produce byte-identical output and the same
exit status before and after, against the committed sheets. Rulings 1 to 5 change no committed output
on the measurements above; a difference is a defect in the build, not a consequence of these rulings.
The suite, run through `python tools/suite.py`, is green with ruling 6's tests included.

## What this record does not settle

**`skip_reason` is a core field read for one gate only.** Production code reads citation tier 2's value
and no other gate's, at `d148087` and at ADR 0159's `9bb259e` alike. Filed as
[#1078](https://github.com/mshamblin5150-code/clinical-skills/issues/1078) rather than
ruled here, because it changes the result core rather than `survey`'s assembly.

**Which lines survive `--quiet`** is [#986](https://github.com/mshamblin5150-code/clinical-skills/issues/986)'s,
and **whether `gate_schema` is two gates** is
[#1005](https://github.com/mshamblin5150-code/clinical-skills/issues/1005)'s. Neither is moved.

**The local list's name.** `survey` calls its failure list `refusals`, and `CONTEXT.md`'s **Refusal**
is a `run_grader.REFUSED` entry. This record says *failure list* and *findings*; the collision is
recorded and the name is not ruled.

**Whether the emitted output is right.** A byte-identical comparison proves the build preserved
behavior, not that the preserved behavior is wanted.
