# The pre-draft gates observe that the draft does not yet exist and a late gate is a finding the clinician clears

**Measured at:** ef8b5c80d56aa87fc449c3ce0d5597afbce87988

*Re-declared from `b73661b` on 2026-10-03, for the two fact corrections dated at the foot of this record;
between the two commits only this record, its ADR 0272 marker, ADR 0291 and `CONTEXT.md` changed, and
no measured sentence here cites any of them.*

[#1404](https://github.com/mshamblin5150-code/clinical-skills/issues/1404) was filed from the
grilling of [#1395](https://github.com/mshamblin5150-code/clinical-skills/issues/1395), where
[ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md) ruling 8
declared the order *project context retrieved before the draft began* as a limit and filed its
grading separately. Grilled 2026-10-03 against `main`, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The instrument the ticket named cannot see a file write.** `aar_scan --extract` records a
tool-call entry as the tool's name alone, `Write` or `Bash`, never its path or command. The extract
reads tool inputs only during discovery, to decide whether a transcript names the run key; the
`--submission` grade's `_successful_gh_call` also reads Bash and Codex command strings, to find a
successful `gh` call, and reads no file-write path. So *the record was written before the draft* is
not in the extract today, and grading it there needs a new reader of file-write paths across both
harnesses and every writing tool.

**Three records are required before the first prose, and one of them admits its order is
unproven.** Each of the five bound coursework skills writes:

- the project context record, through `tools/project_context.py --write`, whose
  `retrieval-before-draft-unobservable` row declares the order;
- the voice-model identity record, through `tools/voice_model_identity.py --write`, whose limits
  name no ordering row;
- `voice-reads/<submission-key>/supplied-voice.json`, written by hand with no command, whose owning
  module's limits are likewise silent on when the capture happened. The 2026-09-26 sweep comment on
  #1404 found this record neither ordered nor declared.

**The first prose does not always land in the submitted file.** At the declared commit:

| Skill | Where first prose lands | Terminal submission key |
| --- | --- | --- |
| peer-critique | `critique.md` in the run directory | `critique.md` |
| discussion-reply | `response-<name>.md` in the run directory, one per reply | that response filename |
| practicum-case-study | the dated output Markdown under `output/case-studies/` | that file's stem |
| discussion-post | `post.md` in the run directory | the output Markdown stem |
| course-assignment, deck branch | a `.pptx` built in a run-unique private writer path anywhere | the output deck stem |
| course-assignment, DOCX branch | a run-unique private JSON specification for `tools/assignment_docx.py`, anywhere | the output document stem |

**The gates take no submission key today**, while `supplied-voice.json` already lives under one.

**The content of a late draft is already read against the context.** ADR 0272 ruling 10 has a fresh
reader compare the finished draft with the retrieved items and return a verdict. What no instrument
records is whether the run looked before it wrote.

**`tools/coursework_run.py` already owns shared coursework-run policy**: the submission-key parse,
the run-directory join and the output-tree test, imported by three graders.

## Ruling 1 — each gate observes that the draft does not yet exist, and the completion grader checks it

When a pre-draft gate runs, it records whether a file exists at the sitting's mapped first-prose
location. The completion grader checks that observation before the go-ahead, through the row each
record already carries under ADR 0272 ruling 9 and
[ADR 0270](0270-the-canonical-voice-model-is-resolved-by-one-owner-and-identity-is-the-graded-row.md)
ruling 7; no new row is declared.

The observation is a fact the gate function writes, on ADR 0270 ruling 6's machine-written
precedent. It catches the failure this ticket is about, a careless run that drafts first and runs
the gate late, before the post goes out, which is the only point where a finding can still change
the work.

Grading the order from the session transcript at the after-action review was refused here; see
ruling 7. Keeping ruling 8's limit whole was refused because a run that skipped the gate and wrote
the record afterwards stays indistinguishable from an honest one, for all three records.

## Ruling 2 — the observation covers all three pre-draft records

Both gate commands record the observation. **The voice-model identity command also requires
`supplied-voice.json` to exist when it runs**, so a capture present while the draft was absent is
proven to precede it, at the same strength as the two command-written records. The five skills'
instructions move the capture ahead of the two gate commands.

The identity record thereby states a fact about a file it does not own. Its own grader still reads
only its own record, which is what
[ADR 0289](0289-a-record-file-has-one-owning-reader-and-the-currency-command-stops-reading-three-files-it-does-not-own.md)
ruling 1 governs.

Covering the project context record alone was refused because it would leave the supplied-voice
capture, the record most likely to be written late, silently unordered. Declaring a limit for the
capture instead of ordering it was refused because the identity command already runs at the right
moment and costs one existence check.

## Ruling 3 — the gates take the submission key, and one table maps it to the first-prose location

Both gate commands take the sitting's submission key and look up where that sitting's first prose
lands. Discussion-reply runs the gates once per reply, and a record keeps one observation per key.

**Course-assignment's private writer path moves inside the run directory**, so *draft absent* means
that subtree holds no deck and the output deck stem does not exist. Left anywhere, a careless run
drafting in an arbitrary temporary folder passes every gate, which is the exact failure this record
targets.

A keyless check for any draft-shaped file was refused because a legitimate earlier draft — reply one
when reply two starts, an earlier case-study sitting — would fire, and each would need an
exemption. A draft path declared by the run in its own record was refused as the self-certification
ADR 0272 ruling 1 refused: a run that drafted elsewhere names an empty path and passes.

## Ruling 4 — a late gate still writes its record and raises a finding only the clinician clears

A gate that finds the draft already present still performs the retrieval and writes its record and
hashes, so ADR 0272 ruling 10's content check has something to compare against. It records the
draft as present, names its path, and exits nonzero, so drafting stops for a question. At completion
that is a finding, cleared only by the clinician's recorded word under ruling 6. The go-ahead shows
him that the draft came first. A cleared observation is reported as waived and counted, on ADR 0272
ruling 6's terms, so a waived run never reads as one gated in order.

**No tool prints deletion as the remedy.** Deleting or moving the draft and re-running the gate is
the one evasion the observation cannot see; a remedy telling a run to do it would teach the evasion
as the way to pass.

Refusing and sending the run back to redraft was refused for that reason, and because it discards
work the clinician may already have read. Recording a late gate as an exit-2 coverage state was
refused because the skills accept an exit 2 with a banner, so the line could never fail.

## Ruling 5 — `coursework_run` owns the table

The table mapping each bound skill's submission key to its first-prose location lives in
`tools/coursework_run.py`. Where a sitting's working files live is coursework-run layout, which is
that module's stated subject, and it already holds the key parse the table depends on. The module
thereby names the five skills, which it does not today; that widening is accepted.

A new module for a five-row table was refused beside one whose purpose already covers it. Placing
the table in `tools/project_context.py` was refused because the voice code would depend on the
project-context code for something that is not project context.

## Ruling 6 — one confirmed waiver line in the project context header clears both findings

The clinician's word is written once, as a line in the project context record's confirmed header:

```
ORDER-WAIVE: <draft path> - <what was drafted before the gate>; proceed, per the clinician
```

It is confirmed with the rest of the header, as `PROJECT-WAIVE:` lines are. The voice-model
identity grader asks the project-context module, through its public reader, whether the order is
waived for the submission; it never parses `project-context.md` itself. Both records' limits state
that dependency.

A waiver in each record was refused because the identity record is machine-written and has no
confirmation surface: a flag carrying it is a waiver the run can grant itself. A fourth record for a
line that appears only on late-gate runs was refused.

## Ruling 7 — the transcript instrument is declined, and the remaining limit is declared

Grading the order from the session transcript at the after-action review is **declined** and no
ticket is filed for it. It would land after submission, make that review a second grader of each
bound skill, and require a new cross-harness reader of tool inputs for a case with no recorded
instance. **Reconsider it on the first recorded run that deleted, moved, or wrote a draft outside
its mapped location to get past a gate**; that run is the instance this decline waits for.

The observation establishes only that no file existed at the mapped location when each gate ran.
`project_context.DECLARED_LIMITS` narrows `retrieval-before-draft-unobservable` to what it cannot
see, and `voice_model_identity.DECLARED_LIMITS` gains the matching row:

- a draft deleted or moved out of its mapped location before the gate ran;
- prose written at any other location;
- prose composed in the conversation and saved only after the gates.

## Supersedes

- [ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md)
  ruling 8, its holding that the ordering *"is a declared limit, not a graded claim."* The gate
  itself stands; the ordering is now observed by it under ruling 1, and the limit is narrowed under
  ruling 7.

*Corrected 2026-10-03.* The measured paragraph on the transcript instrument formerly said *"Tool inputs
are read only during discovery"* and that grading the order needs *"a new reader of tool inputs"*. The
`--submission` grade already reads Bash and Codex command strings in `_successful_gh_call`, so the
missing reader is narrower: file-write paths. Ruling 7's decline stands on its other grounds, that
the grade lands after submission, makes the review a second grader, and has no recorded instance; its
cost clause is overstated by the same width. The table formerly gave course-assignment one row, the
deck branch, and omitted the DOCX branch, whose first prose lands in a run-unique private JSON
specification read by `tools/assignment_docx.py`. Ruling 3's reason, that a writer path left anywhere
lets a careless run pass every gate, applies to that specification unchanged, so #1404's build maps
it inside the run directory too. Both omissions were found by the tracker sweep after this record
merged.
