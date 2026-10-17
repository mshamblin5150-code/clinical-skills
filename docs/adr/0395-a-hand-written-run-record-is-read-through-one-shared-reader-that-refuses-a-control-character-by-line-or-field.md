# A hand-written run record is read through one shared reader that refuses a control character by line or field

**Measured at:** c86b4e03b30b91ac7b2d2be1f0c68e811efc8e1f

[#1755](https://github.com/mshamblin5150-code/clinical-skills/issues/1755) was filed from the
grilling of #1563 under [ADR 0351](0351-a-damaged-byte-in-the-project-context-record-or-registry-is-refused-by-line-before-the-gate-parses.md)
ruling 5. ADR 0351 made `project_context.py --write` refuse a C0 control character in the run's
`project-context.md` and the account registry. #1755 asked whether the same damage reaching the
other hand-written run records that graders parse should be refused, and how. Grilled 2026-10-17
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The population was derived by walking the readers in `tools/`, not by grepping skill prose.**
Five read-only passes walked every non-test module that opens a file inside a run directory and
drove each reader through its public function on synthetic records built in a temporary directory.
Nothing under `scratch/` or `output/` was opened for content. The passes found four kinds of file
with control-character exposure: run records an agent writes by hand, records a committed tool
writes as JSON, deliverables, and committed reference sheets. Only the first kind is this record's
subject.

**No reader of a hand-written run record checks for a control character except one.**
`project_context._damaged_lines` runs only on the `--write` path, and the module's own
`DECLARED_LIMITS` carries `later-control-damage-unchecked`: the go-ahead and completion re-reads do
not check. `tracker_bodies.has_c0_control_character` is the only other C0 predicate over parsed
text, and it allows tab where ADR 0351 refuses it.

**Undetected damage fails in three ways, and the worst passes clean.** `Path.read_text` turns a bare
carriage return into a line break, and `str.splitlines` also splits on a form feed and a vertical
tab, so those three cut a field in half. A bell or NUL inside a vocabulary value becomes a generic
malformed finding with no line number. A bell or NUL after a keyword or inside free text passes:
`research_ledger.keyword_of("sourced\x00", ...)` returns `sourced` with the byte as its remainder,
and `checks_ledger.keyword_of("clean\x07", ...)` returns `clean`, both driven here. The walk also
drove a reread verdict of `matches - ` followed by a bell clearing the bare-verdict check in
`discussion_artifact`, and a bare carriage return inside a signed bar's `SLIDE-MAX` value being
read as its first digit by the graders while `assignment_bar.sign` refuses the same bytes.

**A JSON record carries the commonest damage as an escape, not a byte.** Strict `json.loads`
refuses a raw control character inside a string, but `json.loads(r'"C:\temp"')` returns a real tab
followed by `emp`, driven here. A check over the raw text sees a clean backslash.

**No real record carries the damage, and only copied classmate text carries a tab.** Counted across
the five registered checkouts that own a `scratch/` root: 249 files of the in-scope record kinds
and classmate post copies. No file holds any C0 character other than a line ending, except that 2
of the 41 classmate post copies under `posts/` carry tabs in the copied post body. No file under
`skills/`, `docs/agents/`, `AGENTS.md` or `reference/*.md` documents a record format with a literal
tab.

## Ruling 1 — a check is built rather than the gap only declared

The readers of hand-written run records refuse a damaged control character. Declaring the gap in
each reader's limits was declined: no real record has carried the damage, but the route that
produced it is still open. [ADR 0368](0368-a-doubled-backslash-in-a-bash-command-is-refused-because-the-bash-tool-halves-it.md)'s
hook refuses a doubled backslash typed into a shell command; a script written with the Write tool
and then run still turns `\t` in an ordinary Python string into a tab. The worst outcome, a damaged
value confirmed silently, is what ADR 0351 already refused for one record, and leaving it open
elsewhere would make one rule depend on which file the damage reached. Building only for records
likely to carry Windows paths was declined because a free-text field elsewhere still passes a bell
silently.

## Ruling 2 — one shared reader reads and checks together

One shared function opens a hand-written run record, checks it, and returns either its text or its
damaged lines. Every grader that reads an in-scope record reads it through that function, the
project-context gate included, so its go-ahead and completion re-reads gain the check its declared
limit names as missing. A suite test asserts that no non-test module reads an in-scope record by
another route; it is a floor on the read shapes it recognizes and says so.

Sharing only the character test was declined because a new grader could read a record and forget
to call it, with nothing to notice. A copy in each grader was declined because the two predicates
that already exist disagree about tab, which is what copies do.

## Ruling 3 — damage is any C0 character except a line ending, with one named exception for copied text

ADR 0351 ruling 4's set holds: a line may end in a line feed or in a carriage return directly before
a line feed, and every other C0 character is damage, tab included. The shared reader carries one
named list of record kinds whose body is text copied from outside the run, where a tab is allowed,
with the reason beside the list. Today that list is the classmate post copies under `posts/`.

Refusing tab everywhere was declined because it refuses two faithful copies of what a classmate
wrote, and its remedy alters their words. Allowing tab everywhere was declined because a `\t` in a
Windows path is the commonest damage. A copied post body holds no paths, so the exception costs
nothing that matters.

## Ruling 4 — a JSON record is also checked after decoding

For a record that is JSON, or that carries a JSON body, the reader also walks every decoded key and
string value under ruling 3's set and names each damaged one by its field path, for example
`images[2].path: U+0009`. A raw-text check alone was declined because the likeliest JSON damage, a
hand-typed `"C:\temp"`, is an escape the raw check cannot see. Refusing escape spellings in the raw
text was declined because it judges spelling rather than meaning and would need its own escape
parser to tell `\\temp` from `\temp`.

## Ruling 5 — damage is exit 1, and only the damaged record's checks are withheld

A damaged record is a finding: the grader read the file and established a defect in it. The grader
exits 1, names each damaged line or field with its character, and prints `not graded — damaged
text` for that record's own checks. Every other record in the run is still graded. Where the
reader also rewrites a record, such as `refutation_apply.py` or `assignment_bar.py sign`, the check
runs before any rewrite, on ADR 0351 ruling 1's reason.

Stopping the whole grader on the first damaged record was declined: ADR 0351's reason, that a
damaged parse cannot be trusted, covers that record and not its neighbors, and a stray byte in one
would hide real findings in the rest. Exit 2 was declined because it says the grader could not read
a file it read completely.

At completion the check is a new completion check under
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md)
ruling 4. It gets one row in `reference/completion-check-starts.tsv`, compared with `approval`, so
an item approved before it lands reports `not graded` for it and a frozen item is never regraded.

## Ruling 6 — the scope is run records an agent writes by hand

The shared reader covers the run records an agent writes by hand that a grader parses as text or
JSON. The three other kinds the walk found are filed as their own tickets, because each has a
different writer and remedy:

- **Deliverables**, including notes, worksheets, posts, replies, the critique and its plain-text
  comment. `entry_copy` refuses only non-ASCII in the Medatrax Entry copy, so C0 passes into it, and
  `post_text.render` copies a bell and a NUL into the Canvas comment unchanged, driven here. The
  remedy is a refusal before anything leaves, at a different moment.
- **Records a committed tool writes as JSON.** Their writers escape every control character, and
  their observed defects are fail-open handling of any unreadable JSON: `frozen_grade._read`
  returns an empty object, so the next freeze rewrites the file with only the new item, and
  `run_status_stop_hook._read_object` returns nothing, so the Stop hook demands no status line.
- **Committed reference sheets.** `reference/thresholds/sepsis-and-septic-shock.md` carries 474 bell
  characters on 167 rows, all from the two Surviving Sepsis Campaign sources, and the sheet gate does
  not refuse them. The source PDF stores the bell in its text layer between a recommendation number
  and its text, and the rendered page shows nothing there, so no threshold was lost.

Widening this record to all four was declined because the tool-written fixes are not a control
character question and the deliverable fix is a different gate.

## What this record does not reach

- **Damage that produces printable characters**, such as a lost backslash. ADR 0351 names the same
  limit.
- **A record read by a route the read-shape test does not recognize.** Ruling 2's test is a floor.
- **The deliverables, tool-written records and reference sheets.** Ruling 6's tickets own them.
- **Damage outside the parsed text of a hashed record.** Where a reader compares only a digest, as
  `voice_read` does for the planted copy, the digest already refuses a changed byte; the reader adds
  nothing there.

## Build checklist

- A new shared module in `tools/` exposing the reader: it takes a run-record path and its record
  kind, reads with `newline=""` so a bare carriage return stays visible, splits on `"\n"` only, and
  returns the text or the damaged lines as `path: line N: U+XXXX`. `project_context._damaged_lines`
  is the reference behavior and moves into this module; its tracker-body divergence comment moves
  with it. JSON kinds also return a decoded walk naming `field.path: U+XXXX`.
- The copied-text exception list lives in that module beside its reason, keyed by record kind.
- Every reader of an in-scope record switches to it. The walk named these at the time of grilling;
  re-derive the population from the readers before building rather than trusting this list:
  `research_ledger`, `claim_ledger_census`, `refutation_apply` (and its refuter returns),
  `checks_ledger` (CHECK records, its HEADING-READ records and the walk JSON files),
  `heading_read`, `discussion_artifact.read_posted_readings`, the bar readers in `assignment_bar`,
  `deck_scan`, `assignment_docx_scan`, `discussion_post_scan`, `research_ledger` and
  `checks_ledger`, the rendered, intent and adversarial readers in `deck_scan` and
  `assignment_docx_scan`, `canvas_readback`, the `AUTHOR` readers in `discussion_reply_scan` and
  `peer_critique_scan`, the posting fields in `discussion_post_scan`, `shift_summary`,
  `delegated_answers`, `aar_scan.read_review`, `imagery_proposals`, `voice_read`,
  `coursework_mechanics`, `lms_attachments`, the scope JSON in `artifact_repairs`, and
  `project_context` at write, go-ahead and completion.
- On damage, each grader exits 1, names the damaged lines or fields, prints `not graded — damaged
  text` for that record's checks and grades the rest. A rewriting command refuses before rewriting.
- One row in `reference/completion-check-starts.tsv` for the completion check, compared with
  `approval`.
- `project_context.DECLARED_LIMITS` drops `later-control-damage-unchecked` and
  `other-record-damage-unchecked` once the shared reader covers those paths.
- The read-shape test from ruling 2, with its floor stated.
- Tests driving each switched reader's public seam with a planted tab, bell, NUL, form feed,
  vertical tab and bare carriage return in a key, a vocabulary value, a free-text value and a
  heading, and a JSON escape `\t` and `\u0000` in a JSON kind. Each expects exit 1 naming the line or
  field. A Windows-line-ending control record exits clean, and a classmate post copy with a tab in
  its body grades clean.
- Name these walk findings as controls, because each is a symptom the shared reader must prevent:
  a damaged `delegated-answers.md` record vanishing before the first `## QUESTION`, a damaged claim
  marker dropping a record from `claim_ledger_census` with no unread count, an escaped NUL in an
  attachment record's `local_path` raising an uncaught `ValueError` out of
  `lms_attachments.completion_gate`, and a form feed in `project-context.md` raising an uncaught
  `ValueError` from `project_context.go_ahead` at `approval_record.prepare` and
  `assignment_submission.prepare`.
