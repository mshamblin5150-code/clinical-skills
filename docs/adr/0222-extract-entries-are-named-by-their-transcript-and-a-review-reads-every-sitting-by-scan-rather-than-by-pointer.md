# Extract entries are named by their transcript and a review reads every sitting by scan rather than by pointer

**Measured at:** 43b901efb469c3c5935aff90f9ad272ef93e491e

[#1042](https://github.com/mshamblin5150-code/clinical-skills/issues/1042) was filed after a
2026-09-10 after-action review whose classifier named entries by extract line numbers and shortened
prefixes. Its proposed fix was one sentence in `skills/aar/SKILL.md`, narrowed twice by sweeps
because `aar_scan.reduce_transcript` names a row that carries no `uuid` `line-{ordinal}`. Grilled
2026-09-13; the clinician widened the ticket from how an entry is named to which transcripts a review
reads, so a Claude drone and a Codex drone are served by one mechanism. Freshness gate `FRESH` at
`43b901ef`, after a rebase. Nothing is built here; this is the record the build reads.

## Read before ruling

These were driven or counted, not only read.

- **Two Codex transcripts collide.** Two synthetic Codex rollouts with no payload `id` each reduced
  to `line-2` and `line-3`. `collect_population` concatenates transcripts without qualifying an
  identifier, and `_extract_metadata` refuses the resulting extract with `extract entry identifier is
  absent or duplicated`; the same extract with distinct identifiers reads. *Had identifiers been
  unique across transcripts, the duplicate case would read like the control.* Not observed in a real
  run.
- **Claude and Codex already share one reader.** A Claude and a Codex transcript of one exchange
  reduced to `u-1`, `a-1#text-1` and `line-1`, `line-2` with correct kinds and no collision.
  `locate_transcript` searches `~/.claude/projects` and `~/.codex/sessions`.
- **Selection reads one transcript.** `--transcript` takes one path and `locate_transcript` stops at
  the newest match; an earlier sitting reaches the population only through an orphan pointer, and
  only `.claude/settings.json` registers `--session-end`.
- **Most Codex rollouts are drones, and today's selection accepts them.** Of 1,199 rollouts under
  `~/.codex/sessions` on the clinician's machine, 872 carry `session_meta.source.subagent`; nothing in
  a rollout's filename or directory marks it. `_is_codex_transcript` accepts any of them.
  [#1166](https://github.com/mshamblin5150-code/clinical-skills/issues/1166) records the attribution
  half of that seam.
- **The haystack is about 17 GB.** `~/.claude/projects` 2,336 files, 2,274,761,190 bytes (1,898 in
  `subagents` directories); `~/.codex/sessions` 1,199 files, 1,365,948,208 bytes;
  `~/.codex/archived_sessions` 3,072 files, 13,336,961,889 bytes. `archived_sessions` is not searched
  today.
- **Codex has a `SessionEnd` hook, read from source and not run.** A research agent read
  `openai/codex` at `a505c714`: `SessionEnd` exists from `rust-v0.153.4`, is skipped for subagents, and
  passes `session_id` and `transcript_path`; project hooks require per-hook trust. The clinician's
  `~/.codex/hooks.json` configures none. Ruling 7 makes this moot.
- **`CONTEXT.md` said a sitting always submits.** [ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
  ruling 14 is about a sitting that never submits.

## Ruled 2026-09-13

### 1. A row with no identifier is named by its transcript

The fallback identifier is `<transcript-stem>#row-<ordinal>`, replacing `line-<ordinal>`. It uses the
`#` suffix the extract already uses for a part of a source, it matches the entry's own `TRANSCRIPT:`
line, and it cannot collide across transcripts. The old `line-<ordinal>` is carried as an alias so a
prior round's `WATERMARK` and `CLASSIFIER-ENTRY` still resolve. A colon separator was declined because
`## ENTRY:` and every record field already use one; an unqualified `row-N` still collides.

### 2. A correction names the entry holding the contradiction

A correction names the entry where the reversal was observed, which is the entry its `CORRECTOR`
describes; a sustain names the entry where the right thing was settled. The asserting entry was
declined because a claim can be contradicted more than once and carries no corrector. A second
`CLAIM-ENTRY` field was declined as template weight with no grader use.

### 3. A correction cannot rest on an entry whose text the extractor wrote

The grader refuses, exit 1, a correction resting on a `tool-call`, `subagent-launch` or
`inter-agent-metadata` entry, held as one constant in `aar_scan.py`: their text is a tool name, a
fixed acknowledgment or a constant marker, so none can hold a contradiction. It prints a
corrector-by-kind count table for corrections and sustains that never changes the status. A strict
pairing of corrector and kind was declined: a message typed while an agent works arrives as a queued
row labeled `harness-meta`, and a loaded skill prompt can contradict an agent's claim. **Declared
limit:** a misplacement onto a `tool-status` or `skill-prompt` entry, the 2026-09-10 shape, is shown
in the table and not refused. Sustains are not refused, because a sustain can rest on a tool call.

### 4. A review reads every sitting by scan

Extraction reads every main transcript under `~/.claude/projects`, `~/.codex/sessions` and
`~/.codex/archived_sessions` whose tool calls name the run directory and that carries entries past
its own watermark, plus any `--transcript` path. Pointers for both harnesses were declined because a
sitting that crashes before its hook runs is lost and a Codex hook needs trust on the clinician's
machine; an orchestrator-named list was declined because it depends on remembering which sittings
touched the submission.

### 5. No scoped-skill filter; drones are excluded

A main session in either harness counts as a sitting when its tool calls name the run directory,
whether or not a scoped skill ran. A plain session that corrects a draft is otherwise lost, and an
extra transcript costs reading while a dropped one loses a correction silently. Codex rollouts whose
`session_meta.source` is `subagent` and Claude transcripts under a `subagents` directory are never read
as sittings; a drone's result reaches the extract through the main transcript that launched it.

This departs from #1166's *What must not come out of this*, which forbade widening the Claude side to
match the Codex side. The clinician ruled that direction on the ground above: the failure being
prevented is a lost correction, and requiring attribution is what loses one.

### 6. The scan is bounded by creation time and a byte search

A transcript last modified more than 24 hours before the run directory's creation is skipped without
being opened. Creation time is the platform's own birth time where it reports one; where it does not,
the time filter is dropped, because POSIX `ctime` is later than creation and would skip real sittings.
Of what remains, only a file whose raw bytes contain the run key is parsed. Both filters only exclude,
the margin's error direction is more reading, and the report prints transcripts found, skipped by
time, skipped by byte search, and read. Scanning everything was declined as minutes per extraction.

### 7. Orphan pointers are retired

The `--session-end` mode, its `.claude/settings.json` registration, pointer reading and the
`orphaned sittings` report row are removed; the scan's report replaces the row. Existing
`orphaned-*.json` files are moved aside under the run's `aar/` directory, never deleted. **This
supersedes ADR 0109 ruling 14's mechanism and the third bullet of its ruling 4**; ruling 14's purpose,
that an abandoned sitting's corrections are reviewed, stands and is served by ruling 4.

### 8. Grading counts later sittings and does not fail on them

The grading run re-scans and prints how many sittings began after the extract. The status is
unchanged; the next round's extraction takes them. Failing was declined because any later work on a
run, including the reviewing session's own entries, would reopen a closed review.

### 9. The skill text

`skills/aar/SKILL.md` step 1 replaces its selection and orphan-pointer sentences with the scan; step
2 adds *Name every correction and sustain by one entry, using the identifier exactly as it follows
`## ENTRY:`, including any `#` suffix. A correction names the entry holding the contradiction; a
sustain names the entry where the right thing was settled. An extract line number or a shortened
prefix is never an identifier.*; step 4 adds that the grader refuses a correction resting on an entry
whose text the extractor wrote rather than copied, and counts corrector against kind without grading
the count. The skill names no entry kind, because `aar_scan.ENTRY_KINDS` owns that vocabulary.

### 10. Each harness's side is measured by a builder that runs it

The Codex builder confirms rollout shape, the drone marker and scan hits in a live Codex session; the
Claude side is supplied from a structure-only read of real Claude transcripts on #1042.

## Consequences

`CONTEXT.md` **Sitting** and **Review round** now say a sitting produces at most one submission.
#1042 is respecified to these rulings and moves to `ready-for-agent`; #1166 is settled by rulings 4
and 5 and folds into it.

**Not reached here:** eight top-level Claude row types observed in real transcripts are absent from
`CLAUDE_ROW_TYPES`, and the undeclared-row count is taken only when a Codex row is present, so a pure
Claude extract reports 0. Filed separately rather than widened into this record.
