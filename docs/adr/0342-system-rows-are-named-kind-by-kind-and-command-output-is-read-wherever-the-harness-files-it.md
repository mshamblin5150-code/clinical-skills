# System rows are named kind by kind and command output is read wherever the harness files it

**Measured at:** 5857d147ba83dc0ff59caa2b471b91bb049470c8

[#1535](https://github.com/mshamblin5150-code/clinical-skills/issues/1535) was filed from
[#1256](https://github.com/mshamblin5150-code/clinical-skills/issues/1256)'s grilling. ADR 0285
ruling 1 requires every Claude row type the after-action review leaves unread to carry a written
reason. `aar_scan.NAMED_UNREAD_TYPES` gives `file-history-snapshot` and `progress` reasons, but its
entry for `system` only points back to this ticket. Grilled 2026-10-11; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

The population was every top-level `*.jsonl` directly inside the project folders under
`~/.claude/projects` on the clinician's machine: 616 main transcripts, `subagents/` excluded, read
with `aar_scan.read_transcript`. 589 carry at least one `system` row, and there are 6,868 such rows
in all. No file failed to read or to reduce. A counts-only helper printed harness key names and
integers and never a value. The measurement ran on 2026-10-11 against `b0baede0`, and
`tools/aar_scan.py` is byte-identical at the commit declared above. These figures are that day's
reading of live files, not constants.

**Seven kinds, read off each row's `subtype` key.**

| subtype | rows | transcripts |
| --- | ---: | ---: |
| `stop_hook_summary` | 6,683 | 584 |
| `api_error` | 121 | 24 |
| `local_command` | 26 | 13 |
| `compact_boundary` | 17 | 13 |
| `model_refusal_fallback` | 15 | 4 |
| `informational` | 3 | 3 |
| `turn_duration` | 3 | 2 |

**The test asked by the ticket.** Each nonempty string leaf of each `system` row, with identifier,
timestamp, path and version keys excluded, was compared as a substring against the concatenated text
of every entry `reduce_transcript` makes from the same transcript.

**Command output moved out of the population with a harness release.** Older releases filed the
reply to a local slash command inside a `user` row. 19 such rows exist, and the review reads them
under the `local-command-stdout` entry kind. Newer releases file it as a `system` row of subtype
`local_command`. Of those 26 rows, 16 carry the same `<local-command-stdout>` envelope, 3 carry the
`<command-name>` echo of the typed command, and 7 carry no envelope. All 26 carry `isMeta`. In 21 of
them the `content` text occurs in no reduced entry, and 20 of those 21 are 40 characters or longer.
The typed arguments in `commandRun.args` all occur elsewhere already.

**A refusal fallback withdraws replies the transcript does not keep.** The 15 `model_refusal_fallback`
rows all carry `trigger` `refusal` and `isMeta`. Between them they list 19 `retractedMessageUuids`,
and none of those 19 identifiers belongs to any row in its transcript. The refused user message is
present in all 15 transcripts and is already read. In all 15 rows, the notice text in `content`
occurs in no reduced entry.

**The other kinds.** The 3 `informational` rows are flagged plain notices whose text occurs in no
entry. Of the 6,683 stop-hook summaries, 96 carry `hookErrors`, and every one of those strings occurs
in a reduced entry. No summary had `preventedContinuation` true or a nonempty `stopReason`. Most
`hookInfos[].command` strings occur nowhere else; they are hook command lines. The 121 `api_error`
rows hold connection and retry text found in no entry, and none carries `isMeta`. Each of the 17
`compact_boundary` rows holds a short marker and identifier lists, and the summary it bounds is
already read as a `compaction-summary` entry. The 3 `turn_duration` rows hold a duration and a
message count.

**The version line reads every row.** `extract_diagnostics` builds `HARNESS-VERSIONS` from
`row.get("version")` across all rows, before any reduction by type, and
[ADR 0333](0333-a-bold-references-label-is-read-off-the-word-path-and-an-oversized-memory-index-fails-the-review.md)
ruling 4 compares that line with the release on which the memory-index limits were measured.

## Ruling 1 — Command output filed as a system row is read under its existing label

A `system` row of subtype `local_command` is read, on the same footing as the user-row form that is
already in the population. The harness release that wrote a transcript does not decide whether the
review reads its command output. Ruling 4 settles the label.

Naming these rows as unread was declined. It would make the population depend on which release wrote
the transcript, which ADR 0285 refused in a neighboring form. It would also drop output that an
earlier ruling already put in the population. A new label for the same envelope was declined under
[ADR 0193](0193-an-extract-entry-s-kind-names-its-envelope-and-a-matcher-may-label-where-it-may-not-reduce.md)
ruling 2, under which a kind names the envelope, never the origin.

## Ruling 2 — Each system subtype is named, and an unnamed one is unread material

The single `system` entry in `NAMED_UNREAD_TYPES` is replaced by a per-subtype declaration. Every
subtype is either read (rulings 1, 3 and 5) or named unread with a one-line reason (ruling 5). A
`system` row whose subtype is neither, including a row with no subtype, adds to the extract's
unread remainder. This is ADR 0285 rulings 1 and 2 applied one level down: the extract is still
written, the shared `unread remainder N` line prints, and the extract and the grade exit 2 while N is
nonzero. A finding established on the same run still exits 1. The remedy is naming the subtype with
its reason.

Naming `system` once under a blanket reason was declined, because that arrangement let the
command-output relocation go unseen. Counting unnamed subtypes without changing the status was
declined for the reason ADR 0285 gave: a number nobody has to act on goes unread.

## Ruling 3 — A refusal-fallback notice is read as `harness-meta`

A `model_refusal_fallback` row's `content` notice is read as an entry of the existing `harness-meta`
kind: a flagged harness row with no recognized envelope. The withdrawn replies are not stored, so
their text is a stated limit of the review.

A dedicated kind was declined: it would add a vocabulary word for 15 rows across all history and
tell the reader nothing the notice does not already say. Naming the notice unread was declined
because the clinician saw it, and a reply that appeared and was withdrawn would otherwise leave no
trace.

## Ruling 4 — A read system row is labeled by the envelope it carries

Read `system` rows take the envelope matching user rows already get. A recognized envelope names the
kind: `<local-command-stdout>` is `local-command-stdout` and `<command-name>` is `command-name`. A
flagged row with no recognized envelope is `harness-meta`. Of today's 26 command rows, that gives 16
output entries, 3 command-name entries and 7 `harness-meta` entries.

Labeling every command row `local-command-stdout` was declined, because it labels by origin and would
call 3 echoes output. Reading only the 16 output-wrapped rows was declined, because the 7 unwrapped
rows hold text found in no other entry.

## Ruling 5 — Informational is read and four subtypes are named unread

An `informational` row is read as `harness-meta`, on ruling 3's footing: it is a flagged notice the
session displayed. The other four are named unread with these reasons:

- `stop_hook_summary`: hook bookkeeping; any hook feedback the session saw is read where it was
  delivered.
- `api_error`: a failed request and its retry; nothing said was reversed.
- `compact_boundary`: a compaction marker; the summary it bounds is read.
- `turn_duration`: timing.

The test throughout is whether a row holds text displayed for the clinician to see and react to, or
only bookkeeping, telemetry or text the review already reads elsewhere. The stop-hook reason rests
on the measurement above: all 96 error strings occur in read entries. Naming informational unread
was declined as inconsistent with ruling 3. Reading API errors was declined: those rows are not
flagged, so `harness-meta` would stretch to unflagged rows, and a retry reverses nothing.

## Ruling 6 — An extract written before the build is graded under a dated cutoff

Ruling 2 adds a count and rulings 1, 3, 4 and 5 add entries. An extract whose `EXTRACTED-AT`
precedes the build's cutoff is graded as before, and the report says the system-subtype count was not
measured because the extract predates it. It never prints `0` for such an extract. This follows
ADR 0285 ruling 6 and the module's other dated cutoffs.

Treating such an extract as unread until re-extracted was declined, because it fails completed
reviews under a rule that did not exist when they were written. Grading it with a count of `0` was
declined because the count was never measured.

## Ruling 7 — The harness-version read keeps covering every row

`HARNESS-VERSIONS` continues to read `version` from every transcript row, `system` rows included,
whatever any ruling here does about reduction. ADR 0333 ruling 4 depends on it.

## For the build

- **The `clinician` label is never reached from a `system` row.** That kind means a user row with no
  harness flag and no recognized envelope. A read `system` row that has no envelope therefore falls to
  `harness-meta`, whether or not it carries `isMeta`. None does today.
- **The build edits the same files as #1504's build.** Both touch `tools/aar_scan.py` and
  `skills/aar/SKILL.md`, so whichever of the two lands second rebases onto the first.
- **`ENTRY_KIND_DESCRIPTIONS["harness-meta"]` and the generated extract legend** must describe a
  flagged harness row of either type rather than only a user row, wherever their wording implies the
  narrower reading.

## Stated limits

- A withdrawn reply's text is not stored by the harness and cannot enter the population.
- The comparison above was a substring test against reduced entry text. It establishes that a value
  occurs in an entry, not that the occurrence is the same event.
- A subtype is identified only by the `subtype` key. A row that changes meaning while keeping its
  subtype is not detected.
