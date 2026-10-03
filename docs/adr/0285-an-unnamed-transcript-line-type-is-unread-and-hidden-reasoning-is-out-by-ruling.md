# An unnamed transcript line type is unread, and hidden reasoning is out by ruling

**Measured at:** a2749102df08d8af544cd27da3dd4e296eae1aa1

[#1256](https://github.com/mshamblin5150-code/clinical-skills/issues/1256) was filed from
[#1042](https://github.com/mshamblin5150-code/clinical-skills/issues/1042)'s grilling. It found
that `aar_scan.CLAUDE_ROW_TYPES` names seven top-level Claude transcript row types, that real
transcripts carry more, and that a pure Claude extract reports `0` undeclared rows beside them.
[ADR 0222](0222-extract-entries-are-named-by-their-transcript-and-a-review-reads-every-sitting-by-scan-rather-than-by-pointer.md)
declared the same gap as not reached. Grilled 2026-10-03 against `main`, where the freshness gate
read `FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this
is the record the build reads.**

## Measured before ruling

### The code

`extract_diagnostics` computes its undeclared-row count only when some row carries a Codex type,
and prints it as `UNDECLARED-CODEX-ROW-TYPES`. On a transcript holding no Codex row the count is
`0` whatever the rows are. `UNDECLARED-CODEX-PAYLOAD-TYPES` counts `response_item` payload kinds
outside `CODEX_RESPONSE_TYPES`. No grader reads either field: both are header text, and neither
changes an exit status. `reduce_transcript` makes entries from `user`, `assistant`, `attachment` and
`queue-operation` rows and from five Codex shapes; a row of any other type contributes nothing.
`CODEX_RESPONSE_TYPES` already names `reasoning`, and `reduce_transcript` reads no reasoning item,
so Codex reasoning is declared and unread with no written reason.

### The population

Population: every top-level `*.jsonl` directly inside the 244 project folders under
`~/.claude/projects` on the clinician's machine, 571 main transcripts, `subagents/` excluded. The
matcher is the top-level `type` key of each JSON row; no file failed to read and no line failed to
parse. Counted 2026-10-03 by a counts-only helper over live files, so the figures drift by a few
rows between passes and are stated as that day's reading, not as constants.

**Fourteen row types are outside the seven, not the ticket's eight.** The ticket counted 11
transcripts in one project folder. The wider population adds `ai-title`, `cost-state`,
`permission-mode`, `frame-link`, `artifact-autoreact-ledger` and `artifact-comment-monitor` to the
ticket's `bridge-session`, `atis-latch`, `last-prompt`, `pr-link`, `custom-title`,
`file-history-delta`, `mode` and `agent-name`. Had the seven covered every row, the count of rows
outside them would have printed zero; it printed about 80,000.

**`last-prompt` is a truncated echo.** Its `lastPrompt` string never exceeds 201 characters, and
2,500 of the 2,521 values at 200 characters or longer end in an ellipsis. Of 22,403 nonempty
values, 19 occur in no other row of their own transcript after the ellipsis is trimmed, and 18 of
those occur in no transcript at all. Sixteen of the 19 are cut-off long prompts. What the 18 hold
was not read, because reading them is reading the clinician's text; an unsent or edited prompt is
the likely cause and is unverified.

**Titles and agent names are mostly generated.** About 14% of `customTitle`, 5% of `aiTitle` and
34% of `agentName` values occur inside the same transcript's user rows.

**Thinking text is mostly not stored.** 41,077 assistant `thinking` blocks carry a signature, and
10,791 carry any text. Across 5,325 Codex rollouts, 70,659 of 408,979 `reasoning` items carry
summary text; the rest hold only encrypted content.

## Ruling 1. Every row type is either named with a reason or counted

Each Claude row type observed above is named in the module as deliberately unread, with a one-line
reason beside it. Every row type outside the named Claude and Codex sets is counted on every
extract, whether or not a Codex row is present. A clean extract therefore reads `0`, and a new type
reads nonzero the first day it appears.

## Ruling 2. An unnamed row type is unread material

The extract is still written, because everything it could read is good. The extract command and
the grade both print the shared `unread remainder N` line through
`run_grader.format_unread_remainder` and exit 2 when N is nonzero; a finding established on the same
run still exits 1. The remedy is naming the new type with its reason.

## Ruling 3. Hidden reasoning is outside the population on both harnesses

Claude `thinking` blocks and Codex `reasoning` items are named as deliberately unread. The reason is
[ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 1: a correction is an observed reversal, and a thought revised before anything was said
reversed nothing anyone saw. A self-catch that appears only in reasoning is a stated limit.

## Ruling 4. `last-prompt` is named as unread

Its reason is that it is a 200-character echo of a turn the review already reads. The residue
measured above, text held nowhere else, is a stated limit.

## Ruling 5. Unrecognized Codex payload kinds join the same remainder

A `response_item` payload kind outside the named set is unread material on the same terms as an
unnamed row type, and adds to the same N.

## Ruling 6. An extract written before the build is graded under a dated cutoff

An extract whose `EXTRACTED-AT` precedes the build's cutoff is graded as before, and the report
says the count was not measured because the extract predates it. It never prints `0` for such an
extract. This follows the module's existing classifier-entry and posted-reading-fingerprint
cutoffs.

## Rejected options

**Name the eight and add no Claude count.** A ninth type would still read `0`, which is the
ticket's defect deferred by one release.

**Count without naming.** The ticket's 11 transcripts alone held about two thousand such rows,
and a new type would be buried in a number nobody reads.

**Report the count without changing the status.** Nothing would make anyone look, which is how the
gap went unseen.

**Exit 2 at extract time only.** A session that passes the warning would still finish with a clean
grade over rows it never read.

**Read reasoning as an entry kind.** The population would depend on whether the harness stored the
text, which it mostly did not, and the review would grade thoughts rather than events.

**Read `last-prompt` where it matches nothing else.** That test compares text with text, the
content matcher ADR 0109 ruling 9 refused, to recover about one truncated line across the whole
history.

**Read every `last-prompt`.** Nearly every value repeats a turn already read, so corrections would
appear twice, the second time cut off.

**Treat an extract without the count as unread, or recount it at grading time.** The first fails
every completed review after the fact under a rule that did not exist when it was written. The
second counts transcripts that may have moved or grown since the review read them.

## Consequences

**A pure Claude extract states its true unread count.** A harness update that adds a row type stops
a clean finish until the type is named, and the message names that remedy.

**The two harnesses share one rule for reasoning**, and the Codex `reasoning` name gains the reason
it never had.

## What this does not reach

**A type named for the wrong reason.** Naming a type removes it from the count, so a type later
found to carry clinician text stays unread until someone revisits its reason.

**Nested content inside a named type.** The count is over top-level types and payload kinds, and a
named type's nested objects are not walked.

**Self-catches in reasoning and text held only in `last-prompt`**, both by ruling.
