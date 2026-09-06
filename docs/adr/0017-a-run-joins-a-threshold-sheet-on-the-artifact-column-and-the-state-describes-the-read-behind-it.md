# A run joins a threshold sheet on the artifact column, and the state describes the read behind it
<!-- no-numbered-rulings -->

[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md) settled the **producer**: how a topic is swept, what [`reference/thresholds/coverage.md`](../../reference/thresholds/coverage.md) records, why `none` and `unread` are separate, and that an artifact does not promote a topic's state. It is silent on the **consumer** end to end.

[#455](https://github.com/mshamblin5150-code/clinical-skills/issues/455) is what that silence cost. [`skills/clinical-note/SKILL.md`](../../skills/clinical-note/SKILL.md) told a generating run that `reference/thresholds/` covers *the topics in state `sheet`*, and `0dc6ddb` moved every shipped sheet to `unread` for a stated and correct reason. The obligation fired into an empty set.

The clinician ruled the consumer on 2026-08-23.

## What was measured before anything was ruled

**The claim re-derives.** `python tools/threshold_coverage.py` reports `sheet 0` against 169 topics, and all four shipped sheets appear only in the optional `artifact` column against `unread`.

**`AGENTS.md` never had the defect.** [`AGENTS.md`](../../AGENTS.md) says *"an artifact on an `unread` row is partial and does not claim a completed topic sweep"* and then *"Where a sheet covers what a Plan item asserts, the skill consults it."* That is already an artifact-keyed join. So this is two documents moved apart, and the copy a consumer reads first is the copy that still worked.

**The empty join is not silent.** `SKILL.md`'s *When nothing ships* already declares a verdict for it, so a hypertension note does not fall through a hole — it writes `recalled, no shipped sheet`, a declared and checkable false claim, into the tier block.

**And that verdict is the one nothing checks.** `tools/differential_scan.py` disproves `uspstf: no row` against shipped topics and `sheet does not settle it` against the shipped sheet. The third verdict is `continue`. So the broken join emits exactly the verdict the row 24 floor waves through, and the two defects compose into a clean scan over a note asserting this repo ships no hypertension sheet.

**The skill already carries the partial-read caveat.** Its *two silences* section rules that a threshold sheet is not complete, and its third silence is *the section it would be in was never read*. Every sheet's `## Scope` carries a `Not read:` limb naming that gap per topic, which is strictly more informative than the registry's state word. Consulting a sheet under `unread` therefore introduces no hazard the skill was not already carrying.

**No shipped snippet was truncated.** [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) reports a 160-character mid-sentence cut in bound extraction, which is why `diabetes.md` sits under `unread`. Measured 2026-08-23 across all four sheets, the longest verbatim cell anywhere is 127 characters and `diabetes.md`'s longest is 87, with none in 155 to 170. #436's damage to that sheet is confined to **coverage** — which records the sweep saw — and did not reach the rows that made it in.

**Rebuild cost is asymmetric.** From [`reference/guidelines-catalog.md`](../../reference/guidelines-catalog.md): ADA Standards of Care 2026 is 377 pages and blocked on #436; AHA/ACC 2025 is 105 pages; the two USPSTF sources are 13, and 8 plus 5.

**Sheet stems are lossy against their registry topics**, and one is a synonym rather than an abbreviation: `high blood pressure` ships as `hypertension.md`, `diabetes mellitus` as `diabetes.md`, `cervical cancer screening` as `cervical-cancer.md`.

## What is ruled

**A run joins on the `artifact` column, whatever the row's state.** The state describes the read behind a sheet; it is not permission to open one. An artifact under `unread` is a real sheet whose full-document read is pending, and each sheet's own `## Scope` says what it did not read.

**There is no fourth silence.** A missing row in a partial sheet earns `sheet does not settle it`, exactly as in a complete one. The verdict already asserts nothing about the guideline, so there is nothing left to weaken, and a second wording would leave the rule *the three silences are not interchangeable* policing four.

**`recalled, no shipped sheet` becomes a graded finding.** Where a shipped artifact covers the item's subject, that verdict is refused. It is not a judgment call: the correct verdict there is `sheet does not settle it`, and choosing the widest negative of three declared options is a rule violation rather than a close reading.

**The scanner matches registry topic names, read from the artifact column.** Filename stems would leave `Blood pressure recheck in 4 weeks` sharing no word with `hypertension` — a silent miss on the highest-value topic in the directory, produced by the repair for a silent miss on the highest-value topic in the directory. Reading the same column the skill joins on also makes the two agree by construction rather than by two globs happening to match.

**A subject that names the condition in neither vocabulary stays a candidate.** `Continue lisinopril 20 mg daily` joins nothing. Drug name to topic is the synonym-shaped miss `_uspstf_subject_topics` already declines to guess at, and it is not widened here.

**The prose is bound and reachability is not re-implemented.** A test asserts `SKILL.md` and `AGENTS.md` name the artifact column as the join. `tools/threshold_coverage.py` already refuses a shipped sheet absent from that column, in the pre-commit hook and in CI, so reachability holds by construction: registration is the join. A second check in the suite would be the weaker copy of an invariant one tool owns, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

**The registry auditor prints an artifact count beside every state row**, whether or not it fired, keyed on `STATES` so the partition sums and a fourth state cannot arrive without a column. [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258): the reachable set is what a consumer depends on, and it was invisible in the tool's own output.

**Completing a sheet is a separate decision from fixing the rule.** Promoting a topic to `sheet` is a clinical read under ADR 0009's first point, not a code change, and it does not retire this ruling: the artifact column exists to name partial work, 165 topics remain, and a state-keyed join breaks again the first time the next partial sheet lands.

## Why the state is not the permission

The registry answers *how completely was this topic read*. A run asks *is there a sheet I must consult rather than recall*. Those are different questions, and ADR 0009 built a separate column for the second one precisely so the first could stay honest. Keying the consumer on the state forces one word to answer both, and the failure direction is the expensive one: the run is told, correctly per the rule as written, that no topic has a sheet. It reads as a settled negative.

## Considered options

**Key the join on state `sheet` alone, and wait.** Rejected. It makes *consulted rather than recalled* false for the directory's most-used sheet, on the most common thing this skill writes up, for as long as a 105-page full-document read and an open #436 take.

**Add a third state, such as `partial`.** Rejected. ADR 0009 is one day old and explicitly ruled that an artifact does not change a topic's state. A new state says the artifact column was the wrong mechanism, and nothing measured here shows that.

**Distinguish a partial sheet in the verdict tail.** Rejected. The tail would qualify a verdict that already concedes everything, and the sheet's `## Scope` states the same gap per topic and more precisely. One jump, and the jump is what the citation exists to enable.

**Remove the four sheets and rebuild them to `sheet` state.** Rejected on measurement. ADA cannot be rebuilt while #436 is open, and removing the top two leaves `clinical-note` with no hypertension and no diabetes sheet — strictly worse than the defect this record repairs. Removing `diabetes.md` alone forfeits verified ADA decision points to avoid a coverage defect the `sheet does not settle it` verdict already neutralizes, and would make every diabetes item read `recalled, no shipped sheet`, which is false in exactly the direction now graded.

**Evaluate the join in a test.** Rejected as a second implementation of an invariant `tools/threshold_coverage.py` already owns, and the weaker one: the tool refuses a commit, a test only reddens the suite.

**Match subjects against filename stems.** Rejected on the stem table above.

**Fold the two cheap USPSTF promotions into this work.** Rejected as mixing a clinical reading into a ticket whose subject is a mechanism, where the reading is the half no command can review. Filed separately.
