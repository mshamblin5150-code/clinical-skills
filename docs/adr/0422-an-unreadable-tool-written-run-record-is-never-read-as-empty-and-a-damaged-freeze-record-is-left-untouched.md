# An unreadable tool-written run record is never read as empty and a damaged freeze record is left untouched

**Measured at:** 72133a636d1678814c7701bbbe9a2c569bd2fd09

[#1860](https://github.com/mshamblin5150-code/clinical-skills/issues/1860) found two readers that
treat a damaged record written by a committed tool as an empty one: the freeze in `frozen_grade`,
which then writes the file back holding only its new entry, and the `run_status_stop_hook` approval
read, which then demands no `Run status:` line. [ADR 0395](0395-a-hand-written-run-record-is-read-through-one-shared-reader-that-refuses-a-control-character-by-line-or-field.md)
ruling 6 filed the ticket and left this class outside its own scope, because these writers escape
every control character and the defect is fail-open handling of any unreadable JSON. Grilled
2026-10-19 against `main` at `04154959`, where the freshness gate read `FRESH`. Rulings 1 to 11
were first recorded at `a65ac5ce`, on `main` at `6bcd6249`, which adds only ADR 0421 and its glossary
entry to that base; every measurement here was taken again there. The tracker sweep closing the
grilling then reopened four points, which the clinician ruled the same day as rulings 12 to 15, and
corrected one sentence in ruling 7. The commit above is that first record merged to `main`; nothing
between it and `04154959` touches a module named here. The clinician ruled every point below.

This record overturns nothing. It adds a second reader to the module ADR 0395 ordered, and it
distinguishes its Stop-hook posture from [ADR 0392](0392-a-guard-that-cannot-read-its-payload-refuses-only-on-its-own-trigger-in-the-raw-text.md)
ruling 4 rather than reversing it.

## Measured before ruling

Each row was driven at the commit above through the named function, in a temporary run directory,
with the damage planted by truncating a record a committed writer had produced:

| reader | planted damage | observed |
| --- | --- | --- |
| `frozen_grade.freeze` | `frozen-grades.json` holding two frozen items, truncated | the rewritten file holds only the new item; both earlier items are gone |
| `run_status_stop_hook.approvals` | `posting-approvals.json` truncated | returns no approvals, so the run is skipped |
| `approval_record._read` | the same file | refuses with `ApprovalRecordError` |
| `medatrax_posting._approved_standalone_note` | the same file | returns nothing, so posting falls back to the run's only note |
| `assignment_submission._next_approval_revision` | `submission-gates.json` at revision 4, truncated | returns revision 1 |
| `frozen_grade.freeze` | `frozen-grades.json` whose `items` is a list | raises an uncaught `AttributeError` |

Had these readers failed closed, the first, second, fourth and fifth rows would each have printed a
refusal instead of a value. The approval read and the Stop hook read one file and disagree about it.

**The revision restart is the most serious route and its downstream effect is read, not driven.**
Frozen grades and the run-status record are both keyed by approval revision. A restart at 1 can
therefore match a revision-1 row recorded for an earlier approval of the same submission, and the
code reads that row as the new approval's frozen grade. No run was driven through that collision.

**The population was counted from the code.** A read of every non-test module in `tools/` found 29
reader sites for records a committed tool writes into a run directory. Sixteen fail closed. Twelve
degrade to a default: five loosen a check, four default in the strict direction, two fail closed at
their caller anyway, and one gates nothing. One more lets a decode error escape uncaught into six
scanners. That census is a subagent's read, re-derived here only for the six rows above; the build
re-derives the whole population before switching it.

**No writer of a run record holds a lock**, apart from the two already ruled: the repair ledger
under [ADR 0405](0405-a-repair-scope-is-recorded-before-the-file-changes-and-only-the-clinician-supersedes-a-failed-comparison.md)
ruling 5, and the freeze below. Two writers overwrite the file in place rather than writing a
temporary file and replacing it.

**Correction, 2026-10-19:** "Two writers" undercounted. The tracker sweep found `aar_scan` writing
three more records in place, read here in code: `measure_memory` writes the memory measurement with
`write_text`, and `write_extract` writes the extract with `open("w")` and the baseline with
`write_text`. The census above came from one reading pass, so the build's re-derivation is the
count, not this paragraph.

**The sweep drove two more facts the rulings below rest on**, at the commit above:

| subject | planted input | observed |
| --- | --- | --- |
| `outbound_search.completion_gate` | `outbound-searches.jsonl` truncated | `(True, 'Outbound searches: finding - private record unreadable')`; the same run with no record read clean |
| `reader_remarks.coverage_lines` | a report holding ruling 11's `unreadable` line and `unread remainder 1` | keeps only `unread remainder 1` |

The first shows a site that already fails closed reporting damage as a finding rather than as a
failure to establish. Had the selector matched `unreadable`, the second would have kept both lines.

## Ruling 1 — a damaged record is never read as empty

A tool-written run record that exists and cannot be read is reported as unreadable by every reader.
It is never treated as a record holding nothing. A **missing** record keeps its present meaning in
each reader, which for most is that nothing has been recorded yet; a first write starts there.

**Fixing only the two named readers was declined**: any other reader that degrades the same way
would stay silent, and each later find would need its own ticket. **Reading damage as empty with a
warning was declined**: for frozen grades the damage is lost data, and a warning reports the loss
after the rewrite has made it.

## Ruling 2 — the Stop hook demands a `stopped` line for a run whose approval record is damaged

When a touched run's durable approval record is present and unreadable, the Stop hook treats the run
as open and requires its keyed `Run status:` line. It accepts only `stopped - <reason>`; `complete`
is refused because the hook cannot confirm it. The line is keyed by the run directory's name, which
the hook has without reading the damaged record.

**ADR 0392 ruling 4 does not govern this case.** That ruling lets an end-of-turn check end the turn
on an unreadable *harness payload*, because nothing a reply says repairs a harness fault and a
refusal would ask for a retry that cannot succeed. Here the record on disk is damaged and the reply
can state a true thing about the run, so the one retry the hook asks for always succeeds. **A system
note only was declined**: the reply would carry no status line and the agent could treat the run as
finished. **Refusing until the file reads was declined**: it could hold the turn open indefinitely,
and repairing an approval record is the clinician's call, not one an agent makes to clear a check.

## Ruling 3 — the freeze refuses a damaged record and leaves it untouched

When `frozen-grades.json` is present and unreadable, the freeze writes nothing, leaves the file
byte for byte as it found it, and prints the line under ruling 11. This applies at every point the
freeze runs: after a terminal grader passes, inside the Stop hook's completion test, and during
historical adoption, which also rewrites the file to mark adoption done.

Until the file is repaired nothing new freezes in that run, and items frozen earlier cannot be read
either, so each is graded fresh at completion and can fail on a check added after its approval.
Restoring the one file restores every earlier freeze. **Moving the damaged file aside and starting a
fresh record was declined**: the active record loses every earlier freeze all the same, a repair
becomes a merge of two files, and the fresh file loses the adoption-done mark so adoption reruns.
**Recovering the entries that still parse was declined** as guessing where a damaged entry begins.

## Ruling 4 — a clean grade whose freeze was refused exits 2

The shared runner prints the passing grader's clean report, then the freeze refusal, and exits 2.
A run in that state cannot be marked `complete`; the Stop hook falls to ruling 2's `stopped` line
until the record is repaired. The Stop hook's own freeze after its completion test follows the same
rule and refuses `complete` rather than raising.

**Exit 0 with a warning was declined**: the run would be marked complete over a damaged record,
nothing would force a repair, and earlier frozen items would keep being graded fresh for the life of
the run. **Exit 1 was declined**: it would call the submission defective when the damage is in its
bookkeeping.

## Ruling 5 — the freeze holds the exclusive artifact lock

The freeze reads, changes and replaces `frozen-grades.json` while holding `artifact_lock`'s
exclusive lock for that file. A busy lock is retried for about one second and then refused under
ruling 4, naming the holder. The operating system releases a crashed holder's lock. **No lock was
declined** because a lost freeze is silent, the loss this ticket was filed over by another route.
**A re-read-and-compare before the replace was declined** because it narrows the race without
closing it.

## Ruling 6 — one shared reader, in ADR 0395's module

Every reader of a tool-written run record reads it through one shared function. The function returns
the decoded record, returns a distinct missing outcome, or raises one unreadable error naming the
file and the cause. It lives in the run-record reader module ADR 0395 ordered, beside that record's
hand-written reader; whichever build lands first creates the module. The two functions stay separate
because their damage tests differ: this one asks whether the bytes decode into the declared shape,
and ADR 0395's asks for a control character.

A suite test asserts that no non-test module reads an in-scope record by another route, and states
that it is a floor on the read shapes it recognizes. The drug-page read-date record that ADR 0409
adds to `uptodate_store` has no reader yet; when it gains one, it reads through this function.

**A fix in each module was declined**: the approval read and the Stop hook already reach opposite
answers about one file because each carries its own handling. **A module of its own was declined**:
two modules for reading a run record would leave a later author choosing between them for no gain.

## Ruling 7 — all 29 reader sites move in one build

The build re-derives the population and switches every reader site to the shared function. The five
that loosen a check fail closed. The four that default in the strict direction report the record as
unreadable instead of defaulting silently. The site that lets a decode error escape raises the
shared error. The sixteen that already fail closed change only their read route.

**Correction, 2026-10-19:** the last sentence is wrong for any site that fails closed by reporting
the damage as a finding. `outbound_search.completion_gate` does, as driven above, and the sweep
read the same posture in the `artifact_repairs` and `assignment_submission` completion gates and in
`aar_scan`'s memory-measurement grade. Under ruling 10 those sites also change their status, from a
finding to exit 2. Ruling 10 already settled this; the sentence described the census wrongly. The
callers of a switched reader, such as `completion_checks.approval_moment`, take the raise rather
than reading it as a missing value.

**Switching only the degrading sites was declined**, and so was switching only the five that loosen
a check: either would leave sixteen reads outside the shared route, so ruling 6's test could not
assert one route over the population, and the next reader would copy whichever pattern sat nearer.

## Ruling 8 — every rewriter takes the lock and an atomic write, built under its own ticket

Every committed tool that rewrites a tool-written run record holds the exclusive artifact lock for
the read, change and write, and writes a temporary file it then replaces. An append-only record
appends under the same lock. The shared module provides that locked read-change-write as one
function, so writing a run record has one answer as reading does. The freeze is built under this
record; the repair ledger is already ruled under ADR 0405; every other rewriter is built under a
separate ticket filed from this grilling, so that this record's build stays a reader change.

**Fixing only the two in-place overwrites was declined**: the lost-update race would stay open on
the approval and gate records, whose loss matters most. **Building the writers here was declined**
because one review would then have to hold every reader and every writer at once.

## Ruling 9 — a record of the wrong shape is unreadable

A record that decodes but violates its kind's minimal shape is unreadable under rulings 1 through
4, exactly like one that does not decode. Each record kind declares that shape to the shared
function: a top-level object, its items as the declared list or mapping, and a revision that is a
positive whole number where the kind carries one. The approval tool therefore refuses a record
holding a non-object item, rather than dropping that item when it rewrites, and refuses a revision
that is not a positive whole number, rather than restarting at 1. The Stop hook's present reading,
in which one malformed item hides every approval in the run, becomes ruling 2's `stopped` line.

**Leaving shape faults to each reader was declined**: the approval tool would keep erasing a bad
item and restarting revisions, and the readers would keep disagreeing about one file.

## Ruling 10 — an unreadable record exits 2 and the rest is still graded

A grader that cannot read a tool-written record it needs exits 2, grades every check that does not
need that record, and prints the line under ruling 11. A finding established on the same run still
exits 1. **This departs from ADR 0395 ruling 5 on purpose**: a damaged hand-written record is
defective content an agent wrote, which is a finding, while a damaged tool-written record is a crash,
a hand edit or a race in bookkeeping the submission did not author, which is a failure to establish.
**Exit 1 was declined** for that reason and because it would split the freeze's status from the
graders' for one file. **Grading nothing else was declined** because it would hide real findings
behind a bookkeeping fault.

## Ruling 11 — one fixed message, safe to paste

Every unreadable outcome prints `<record filename>: unreadable — <cause>`. The cause comes from a
closed list owned by the shared function: `does not decode at line L column C`,
`wrong shape: <which declared rule>`, `could not be opened`, and `held by another task: <holder>`.
The filename passes through the checked-label rule the graders already use for pasteable output.
The message never carries any of the record's contents, because these records sit under `scratch/`
and can carry PHI. The Stop hook's `stopped` reason and the freeze refusal use the same cause
wording. **Printing each site's raw error message was declined**: a shape error built from a value
could print that value, and 29 sites would word one fault 29 ways.

## Ruling 12 — item rules are declared once, at the strictest current reader

Ruling 9's declared shape reaches each item, not only the top level. Each record kind declares its
item rules once to the shared function, set to the rules of its strictest current reader: which
fields an item must carry, which values they may take, and that no submission key appears twice.
An item that fails them makes the record unreadable. The sweep drove two approval records that pass
ruling 9's top-level test and still get two answers: with one submission listed twice, the Stop hook
returns no approvals while the approval tool skips the duplicate and returns the other item; with an
item missing a field the Stop hook requires, the Stop hook returns no approvals while the approval
tool reads both items.

**Keeping ruling 9 at the top level was declined**: those two answers would stay, and the Stop hook
would keep going silent on one malformed item. **Item rules for the approval record alone were
declined**: the same gap would remain in every other record that carries items. The cost accepted
is that a record whose items an older tool wrote in a looser form is refused until it is repaired.

## Ruling 13 — the dependent checks print `not graded` and the record counts in the remainder

When a grader cannot read a tool-written record it needs, every check that depends on that record
prints `not graded`, and the record counts as one member of the run's `unread remainder` under
[ADR 0393](0393-the-unread-remainder-is-one-line-per-report-that-counts-each-member-once-and-names-a-nonzero-population.md).
A nonzero remainder names that population, as ADR 0393 requires. Ruling 10's exit 2 is therefore the
shared seam's own exit on a nonzero remainder, and the go-ahead's coverage lines carry the fault,
because `reader_remarks.coverage_lines` already keeps both a `not graded` row and the remainder line.
Ruling 11's message still prints beside them.

**Adding `unreadable` to the selector was declined**: it would amend the list [ADR 0417](0417-the-clinical-go-ahead-shows-its-paired-grader-s-coverage-lines-before-the-ask-and-refuses-an-approval-that-did-not.md)
ruling 4 ruled, and a run could still exit 2 while printing `unread remainder 0`, the shape
[#1740](https://github.com/mshamblin5150-code/clinical-skills/issues/1740) was filed over. **Doing
both was declined** as two signals for one fault and an amendment this ruling shows is unneeded.

## Ruling 14 — a tool-written record kept in Markdown is in scope

The rule reaches a record by who writes it, not by its format. A tool-written record kept in
Markdown, such as the `aar_scan` extract and, once [ADR 0408](0408-the-go-ahead-uptodate-block-and-the-medatrax-posted-reading-are-written-by-committed-tools-and-checked-before-they-are-relied-on.md)'s
writer exists, `reread.md`, declares its required header fields to the shared function. For such a
record, `does not decode` means its bytes are not valid UTF-8 and its cause names the byte offset,
and `wrong shape` means a required field is missing or does not parse. A field that older records
legitimately lack is declared optional: the extract's `UNREAD-REMAINDER` is one, because
[ADR 0420](0420-the-extract-and-rebuild-output-is-one-report-whose-remainder-figure-is-the-rebuilt-grade-s.md)
ruling 2 reads its absence as a legacy round that was not measured, not as damage.

**JSON records only was declined**: the glossary's definition and this record would disagree about
what is covered, and the extract's reader would keep its own posture outside ruling 6's one route.
**A separate ticket was declined** because the build would stop at a boundary its own definition
crosses.

## Ruling 15 — a record an agent writes and a tool rewrites keeps both meanings

An agent writes `project-context.md` and `project_context.py --write` then re-renders the whole file
and writes it back, so the file belongs to both populations. Each kind of damage keeps the meaning
its own ruling gave it. A control character is ADR 0395's finding, exit 1, because it is content an
agent wrote, including when the tool's rewrite carried it. A decode failure or a broken
tool-rendered field is unreadable here, exit 2. The control-character check runs first and the
decode and shape check second, and the record kind is declared to both functions.

**Treating it as hand-written only was declined**: a torn rewrite by the tool would be reported as
the agent's defect, which ruling 10 refused. **Treating it as tool-written once rewritten was
declined**: a control character the agent typed would stop being a finding, reopening the route
ADR 0395 closed.

## What this record does not reach

- **Hand-written run records.** ADR 0395 owns them.
- **A reader by a route the read-shape test does not recognize.** Ruling 6's test is a floor.
- **A missing record's meaning.** Each reader keeps its own; this record changes only a present
  record that cannot be read.
- **Damage that still decodes into the declared shape.** A wrong value in a well-formed record is
  outside every check here.
- **The rewriters other than the freeze.** Ruling 8's ticket builds them, and until it lands their
  lost-update race and in-place overwrites remain.

## Build checklist

- Before building, count damaged tool-written records across every registered scratch root with a
  command that prints integers only, so the build knows whether any real run is already in the
  state rulings 2 to 4 describe.
- Add the shared function and each record kind's shape declaration to the run-record reader module
  ADR 0395 ordered, creating the module if that build has not landed.
- Re-derive the reader population from the code rather than trusting the census above, and switch
  every site under ruling 7.
- Change the freeze under rulings 3 to 5, including adoption's final rewrite, and the shared runner
  and the Stop hook's completion test under ruling 4.
- Change the Stop hook under rulings 2 and 9.
- Re-check whether any posture change is a new completion check needing a row in
  `reference/completion-check-starts.tsv`.
- Update each switched module's `DECLARED_LIMITS` with its unreadable-record posture.
- Drive each switched reader's public command with a truncated record, a wrong-shape record and an
  unopenable path, and each rewriter with the same three, asserting the refusal, the untouched file,
  the exit status and the exact message. Name as controls the six rows under *Measured before
  ruling*, and the revision restart driven through to its frozen-grade collision.
- Add the read-shape test under ruling 6, with its floor stated.
- Move every fail-closed site that reports damage as a finding to exit 2 under ruling 7's
  correction, and give each caller of a switched reader the raise.
- Declare each record kind's item rules under ruling 12 from its strictest current reader, and drive
  a duplicated submission key and an item missing a required field as controls.
- Under ruling 13, print `not graded` on every dependent check and count the record in the shared
  remainder; drive `reader_remarks.coverage_lines` over the result and assert it keeps the fault.
- Declare the Markdown kinds under ruling 14, including the extract's optional `UNREAD-REMAINDER`,
  and drive a legacy round without it as a control that stays `not measured`.
- Run both checks on `project-context.md` under ruling 15, and drive a planted control character
  (exit 1) and a broken tool-rendered field (exit 2) as separate controls.
