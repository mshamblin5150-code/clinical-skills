# An orchestrator's per-note claims and every repair pass are derived from the record

[#1420](https://github.com/mshamblin5150-code/clinical-skills/issues/1420) was filed from the
after-action review of one `batch-shift` run. Two of its three defects are about an
orchestrator vouching for work it did not re-read. The shift summary said one note "invented
nothing" while that note's Plan proposed an antibiotic the clinician never gave. A fix agent briefed
for coding-anchor fixes also changed a differential verdict and made a symptom code for-entry. The
orchestrator caught and reverted the second; nothing would have caught the first. Grilled
2026-10-08. The facts below were read from `main` at `1b8ffa93`, and none of the files they rest on
changed before this record was written on `main` at `472632e4`. The clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

[ADR 0295](0295-medatrax-note-entry-is-a-verified-scripted-fill-and-a-form-is-finished-only-when-date-finished-says-so.md)
records the same grilling's third defect, Medatrax entry.

## Measured before ruling

**The shift summary template carries no generation claim.** `skills/batch-shift/SKILL.md` step 6
writes `Notes clean (no flags, no gaps)` and `Notes needing attention`. "Invented nothing" was the
orchestrator's own addition, written from memory of the pass. Step 7 keeps the schedule table and
shift summary "for the chat", so neither reaches the run directory and no grader reads either.

**A proposed order is always in `FILLED·proposed`.** `clinical-note` defines that block as the
forward actions the skill contributes, and a Plan order the givens call for is written there. Almost
every note also fills vitals, allergies or social history under `FILLED·asserted`, so a note with
both blocks empty is rare.

**No skill file spawns a repair pass.** No passage in any skill names a fix agent, a repair pass or
a fix pass. The incident's fix agent was improvised mid-shift. `CONTEXT.md` divides every
**Briefing surface** into a **Fan-out brief**, a **Second reader** and a **Grader handoff**; a
context sent to change an artifact another context wrote is none of the three.

**No existing grader would have caught the fix agent.** `differential_scan.py` grades slot form, not
a verdict's value. `anchor_scan.py`'s agreement read grades the note and worksheet against each other,
so a pass that changes both consistently still agrees. Every command on the run would have exited
clean on the incident.

## Ruling 1 — each note's generation line is printed by the completion grader

The shift summary carries one fixed line per note giving its `FILLED·asserted` and `FILLED·proposed`
counts. The completion grader for `batch-shift` prints those counts from each note's tier block,
names the proposed items only under `--show`, and the summary line copies them. A free-form claim
about what a note generated, such as "invented nothing", is not written.

## Ruling 2 — the shift summary is a run-directory file the completion grader checks

The roll-up writes the shift summary into the run directory by standing rule 6's write route, and
the chat shows that file. The completion grader compares each note's summary line with the counts it
reads from that note. A mismatched or missing line is exit 1. An absent summary at the terminal
invocation is incomplete coverage, and a finding still wins over it.

## Ruling 3 — a repair pass is bounded by a clause the orchestrator states in its brief

Standing rule 6 gains an obligation the orchestrator states in every brief that sends a context to
change an artifact another context wrote. No skill file copies it, on the owned-tab rule's
precedent. The brief names the fields the pass may change. The pass never changes a differential
verdict, a for-entry or not-for-entry status, a code population, or clinical content outside them,
and it reports a change it believes is needed outside them rather than making it. The orchestrator
diffs the pass against its brief before accepting it. `CONTEXT.md` names this a **Repair pass**,
distinct from the three briefing kinds. A fourth briefing-surface kind was refused, because no skill
file contains a repair passage and its check would grade an empty population while missing the
improvised pass this record exists for.

## Ruling 4 — a repair pass is checked by comparing protected populations

Before the pass, the orchestrator saves a copy of each note and worksheet the pass may touch and
writes a scope record naming, from a closed vocabulary, what the pass may change. After the pass a
command compares, through the parsers the graders already share, the code set and each code's
for-entry or not-for-entry status, the differential items and their verdicts, and the note's code
populations. A change to any of them that the scope record does not name is exit 1, wherever in the
file it sits. A section-level line diff was refused as the check: the incident's for-entry change
sat inside the worksheet entry the brief allowed, so a section diff would have printed clean.

## Ruling 5 — every change since placement is chained through a recorded, passing repair

When a writer places `note-N.md` or `worksheets/note-N.md` by standing rule 6's copy and rename, it
records the file's SHA-256 in the run. Each repair record carries the before and after hashes and
its comparison result. At the terminal step the completion grader requires each final file's hash
to end an unbroken chain from placement through zero or more recorded, passing repairs. A broken
chain, a failed comparison or a comparison never run is exit 1. This binds every skill that places
notes or worksheets, not only `batch-shift`.

## Ruling 6 — the go-ahead shows every repair pass and the sections it changed

Beside the `PRE-APPROVAL PATIENT QUESTIONS` block, and never inside the Review sheet, the run shows
one `REPAIRS` line per repair pass: the note, the scope its brief named, the comparison verdict, and
the sections whose lines changed, derived from the before and after copies. A changed section
outside the named scope is marked and does not block; the clinician rules on it in the reading the
go-ahead already requires.

## Consequences

- `skills/batch-shift/SKILL.md` step 6 gains the per-note generation line and writes the summary
  into the run directory; step 7's table no longer calls the summary chat-only, and the go-ahead
  gains the `REPAIRS` block.
- `tools/filled_vitals_census.py`, the `batch-shift` completion grader, gains the generation counts,
  the summary comparison and the chain row.
- `AGENTS.md` standing rule 6 gains ruling 3's clause; a committed command performs ruling 4's
  comparison; placement records ruling 5's hash; every completion grader whose run holds notes or
  worksheets gains the chain row.
- `CONTEXT.md` gains **Repair pass**.

## What none of this reaches

Whether a rewritten clinical sentence outside the protected populations stayed within its brief is
a reading, which ruling 6 points at rather than settles. A repair to an artifact other than a note
or a worksheet is bound by ruling 3's clause alone. A scope record and a summary line are graded in
shape and against the notes; neither proves the orchestrator's brief said what the record says.
