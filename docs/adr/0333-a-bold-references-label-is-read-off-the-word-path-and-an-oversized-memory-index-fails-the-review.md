# A bold References label is read off the Word path and an oversized memory index fails the review

**Measured at:** f20dd5b9718c6b0e6401a5fa3ceabeaa0c26d44d

[#1504](https://github.com/mshamblin5150-code/clinical-skills/issues/1504) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 2) on 2026-10-01. It lists four tool
defects that run could not get past. Item 3, the shared posted-reading reader refusing the
`LEGACY-DISPLAY` line, was ruled by ADR 0288 ruling 3 and built by #1330. This record settles the
other three. Grilled 2026-10-11 against `main` at `85a56763`, where the freshness gate read `FRESH`.
`main` then advanced to `00c787da` with the #1502 and #1503 rulings, and every claim below was
checked against that tree. The clinician ruled each point below in that session.
The tracker sweep closing the session found that ruling 3, as first merged, would re-read the live
index on every later re-grade; the clinician added ruling 7 the same day, and this record was
re-measured against `main` at `f20dd5b9` when it was amended.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The terminal grade still crashes, and the cause is wiring rather than design.**
`tools/peer_critique_scan.py` declares `EXIT_2_LIMBS`, so `run_grader` requires every coverage
failure to name one. The grader passes `coverage_limb` to `voice_model_identity.apply_completion_gate`
and to no other gate. `voice_read.apply_completion_gate` and `project_context.apply_completion_gate`
already accept a `coverage_limb` keyword; the grader leaves it at `None`. When either of those rows
reports incomplete coverage, `run_grader` raises `ValueError: coverage failure names no exit-2 limb`
and the process exits 1, the grader's finding status. The 2026-10-03 sweep on #1504 drove both cases
through `main` and saw the error raised each time. `approval_record.apply_completion_gate` stopped
being a path to this crash when #1474's build gave it the `REPLY_UNREADABLE` limb, which the grader
declares.

**The shared APA checker cannot find the reference list `peer-critique` prescribes.**
`skills/peer-critique/SKILL.md` step 4 ends the critique with the bold label `**References**`. Step
5 then requires `python tools/reference_scan.py <run>/critique.md --as-of <date>` to exit 0.
`reference_scan.read_document` opens a list only at a block that `docx_write.blocks` classes as a
heading. Driven on 2026-10-11 on a two-paragraph draft with one citation and one entry, the bold-label
copy printed `no reference list found`, read 0 entries, reported every in-text citation as
`unlisted-citation`, and exited 1. The same draft with `## References` read the entry and exited 0.
So the skill cannot be satisfied as written.

**The heading-only rule is deliberate.** `docx_write.blocks` classes a bold-only `**References**`
line as an ordinary paragraph, so the Word renderer sets no hanging indent, centering, or page break
under it. `reference_scan` reads the list "the way the renderer will", so a Word-bound draft whose
label is not a real heading is caught before Word sets the list wrong. Accepting the bold line
everywhere would grade such a draft clean.

**The critique never reaches Word.** It reaches a Canvas Peer-review comment as plain text. ADR 0331
ruling 4 builds that text from `critique.md` by one command, which strips the markers. So
`critique.md` remains Markdown source carrying `**References**`, and that file is what step 5
grades. The clinician's standing preference, recorded on #495 for discussion replies, is to bold the
literal References label.

**The memory-index limit, read out of the installed release.** Claude Code loads the auto-memory
index `MEMORY.md` into every session. The installed release, 2.1.284, cuts it at 200 lines or 25,000
characters, whichever comes first. The character figure is a string length after trimming, not a
byte count. When it cuts, it appends a warning to the loaded text, which the next session's agent
reads and no tool sees. Releases 2.1.282 and 2.1.283 carry the same two values. Nothing in
Anthropic's documentation states them, and the release updates itself. On 2026-10-11 the index held
146 lines and about 18,500 characters. In the filing sitting, two memory writes landed by the
after-action review pushed it over, and entries at its end stopped loading.

**The review already knows where the index is and which release ran.** `aar_scan --extract` takes
`--memory-index` and writes `MEMORY-INDEX: <path>` and `HARNESS-VERSIONS:` into the extract. The
second is the set of `version` values on the sitting's Claude transcript rows. The grading run,
`aar_scan <run> --submission <key>`, takes no `--memory-index` and runs after the review's memory
writes have landed.

## Ruling 1 — the grader's gates name their limbs

`tools/peer_critique_scan.py` passes a declared `coverage_limb` to
`voice_read.apply_completion_gate` and `project_context.apply_completion_gate`, and lists both limbs
in `EXIT_2_LIMBS`. A voice-read or project-context coverage failure then exits 2, naming its limb.
This follows the precedent #1474 set for the approval gate, so it needed no new ruling from the
clinician. It is recorded here so the build does not treat it as optional.

Making `run_grader` turn an unnamed coverage failure into a generic exit 2 was not taken. The guard
exists so that a grader that declares exact coverage cannot report an unclassified one.

## Ruling 2 — the APA checker reads a bold label only when told the document is not bound for Word

`tools/reference_scan.py` gains an opt-in switch. With it, a line consisting only of a bold
References label (`**References**`, or the singular) opens the reference list the same way a heading
does. Without it, the checker stays heading-only. `peer-critique` step 5 runs the checker with the
switch. `discussion-post`, `practicum-case-study`, and the `course-assignment` DOCX branch, whose skills
prescribe a heading, run it without the switch, so a bold label in a Word-bound draft is still
caught.

Changing the critique's label to `## References` was declined. It breaks the clinician's
bold-label preference, makes the one heading unlike the critique's eight bold section labels, and
would give ADR 0331's plain-text builder a second marker shape on that line. Accepting the bold
label everywhere was declined because a Word-bound draft with a bold label would grade clean while
its list renders flush, with no hanging indent. That is the failure the heading rule exists to
catch. Moving the APA rows into `peer_critique_scan` was declined because the same checks would then
run behind two command entry points that could drift apart.

## Ruling 3 — the after-action review fails an oversized memory index

The after-action review measures the memory index named by the extract's `MEMORY-INDEX:` line,
and its grading run refuses, with exit 1, a measurement over either limit. Ruling 7 says when the
measurement is taken and where it is kept. The check sits at the review because its step 4 comes
after the sitting's memory writes and before any later session loads the index. So a failure arrives before anything has been cut off. A memory written outside a scoped
skill's review is left to the harness's own warning in the next session.

A hook on every write to `MEMORY.md` was declined. It is a second mechanism to register and
maintain for one limit, and a write made through a shell command would bypass it. A report line
that never fails was declined because a number someone has to notice is the same quiet that let the
filing sitting overflow.

## Ruling 4 — the limits carry the release they were measured on

`aar_scan` holds the two limits, 200 lines and 25,000 characters, in one declared object, beside the
Claude Code release they were read from (2.1.284). When the extract's `HARNESS-VERSIONS:` names a
Claude Code release other than the measured one, the grading run prints one line naming both
releases and saying the limits should be re-measured. That line never changes the exit status.

Reading the limits out of the installed program on every run was declined. It would depend on
internal names that change in any release, and a failed read would leave the clinician's terminal
grade unable to finish. Writing the figures in with no release beside them was declined because
nothing would notice an update that changed them.

## Ruling 5 — the headroom is always printed, and there is no early cut point

Every grading run prints the index's lines and characters against both limits, whether or not they
are exceeded. It warns and fails at no fraction short of the limit.

A warning at a fraction such as 90%, and a failure at that fraction, were both declined. The figure
would be invented, with nothing behind it, and ruling 3's failure already lands before any harm.

## Ruling 6 — a two-level index is its own question

The clinician asked whether the index could live somewhere unlimited behind a pointer. Only the
auto-loaded file is guaranteed to be seen, so a pointer to a second list leaves every memory one
skipped read from going unread. `scratch/` was also ruled out as the home, because it is the
patient-record zone and memory is account knowledge that already lives outside the checkout. The
shape left open is a two-level index, with one line per subject in `MEMORY.md` pointing to a subject
index. It is routed to its own grilling on
[#1707](https://github.com/mshamblin5150-code/clinical-skills/issues/1707).

Folding it into this record was declined so that rulings 1 to 5 can be built without waiting on a
memory redesign.

## Ruling 7 — a re-grade reads the sitting's recorded measurement, never the live index

The after-action check runs twice for a scoped skill: once as the review's own grading run, and
again inside every completion grader, through `aar_scan.completion_gate`, each time a finished run
is graded. `MEMORY.md` is one account-level file that any later session can grow. So the
measurement ruling 3 grades is taken once, in the review's step 4, after that sitting's memory
writes have landed, and written into the run beside the review record: lines, characters, the
limits and release it was compared with, and the verdict. Every grading run reads that recorded
measurement and never the live index. A round extracted before the build lands has no record and
reports the row as `not graded`.

Reading the live index on every grade was declined because a finished, posted run would flip to
failing over a later session's writes, with the failure pointing at a run that did nothing wrong.
Leaving the question to #1558's general ruling on late gates was declined because it would hold
this row's build behind that grilling for no gain: the recorded measurement settles this row
whatever #1558 rules for the others.

## What the build changes

- `tools/peer_critique_scan.py`: two limb constants, passed to the voice-read and project-context
  gates and listed in `EXIT_2_LIMBS`.
- `tools/reference_scan.py`: the opt-in bold-label switch in `read_document` and the command line,
  with its boundary stated in the module's `NOT_REACHED` object.
- `skills/peer-critique/SKILL.md` step 5: the `reference_scan` command carries the switch.
- `tools/aar_scan.py`: a command, run in step 4 after the review's memory writes have landed,
  measures the index at the extract's `MEMORY-INDEX:` path and writes the round's measurement
  record beside the review record. The grading run reads that record and never the live index:
  it prints the headroom, refuses a record over either limit, refuses a missing record for a round
  extracted after the build lands, reports `not graded` for an earlier round, and prints the
  re-measure line on a release mismatch. The limits and their measured release sit in one
  declared object.
- `skills/aar/SKILL.md`: step 4 runs the measuring command before the grade, and the grading step
  names the new row, its failure, and the remedy, which is to compact the index, measure again, and
  re-run the grade.
- Tests that drive each change through the public command seams: both gate limbs through `main`
  with `--submission`, a bold-label draft with and without the switch, and an index over each limit,
  at it, under it, and under a mismatched release. One test grows the live index past a limit after
  the measurement is recorded and asserts that re-grading the finished run still passes.

## What this does not reach

- **A memory written outside a scoped skill's review.** Ruling 3 grades the index at the review only.
- **A later overflow, on a re-grade of a finished run.** Ruling 7 reads the recorded measurement, so
  growth after a sitting is caught at the next sitting's review, not on the old run.
- **A Claude Code update that changes the limits without changing the release string.** Ruling 4
  compares release names, not values.
- **Codex's memory.** The figures are Claude Code's. Codex loads its own instructions by another
  mechanism, which this record does not measure.
- **Whether a bold label stands where the list really starts.** The switch moves the boundary to
  the bold line; it cannot tell a misplaced label from a correct one.
