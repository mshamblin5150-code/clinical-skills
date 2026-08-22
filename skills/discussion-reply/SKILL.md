---
name: discussion-reply
description: Read one LMS discussion topic live, rank classmates the clinician can substantively answer, and draft and post short evidence-backed replies in the clinician's confirmed voice. Use for conversational discussion-board replies, not an initial post or the practicum peer-critique deliverable.
---

# Discussion reply

Write a short conversational answer to a classmate's discussion post. This is not the initial
discussion post and not the eight-heading peer critique in
[practicum-case-study/reference/rubric.md](../practicum-case-study/reference/rubric.md). A reply has
no Markdown heading at any level, opens with the classmate's exact first name, contains at least
100 words, and carries at least one source in its own reference list.

The clinician reads every draft and makes the final call. Draft, show, and post only after an
explicit go-ahead for that reply. Authorization to read the board or draft a reply is not posting
authorization.

## Inputs and private run state

The input is one discussion-topic URL. Open it in the clinician's signed-in browser and read the
page live: its breadcrumbs, prompt, the clinician's initial post, every classmate post, and every
nested reply. The live board is authoritative, including edits. Do not ask for pasted posts and do
not use a draft under `output/` as the left-hand side.

Derive a lowercase run key from the page's course and module breadcrumbs, with no date in it. A
run is keyed to the board rather than to the sitting, as recorded in
[ADR 0005](../../docs/adr/0005-a-run-is-keyed-to-the-board.md). Do not configure course names or
module names elsewhere. Write only under the gitignored working directory:

```text
scratch/runs/<course>-<module>/
    board-<date>.md
    posts/
    claims.md
    post.md
    response-<name>.md
```

`board-<date>.md` is the complete snapshot as read on this sitting; never overwrite an earlier
snapshot. `post.md`, when present, is the clinician's initial-post working record and is not a
reply. Under `posts/`, write one file per classmate and start each with these fields before the post
and its nested replies:

```text
AUTHOR: Maren Quill
REPLIES: 2
POST-URL: <permalink where the LMS exposes one>
```

`AUTHOR:` is the run roster used by the grader. Name each response for the selected author's first
name, or full name when first names collide: `response-maren.md` or
`response-maren-quill.md`. Classmate posts are manufactured teaching material and get no PHI
detection layer, count, or report. They remain gitignored working material.

Parallel readers or researchers each receive a new run-unique private path. They return findings
to the orchestrating context and never append to `board-<date>.md`, `claims.md`, or a reply file.
The orchestrator is the sole writer of those artifacts. The canonical `scratch/runs/<run-key>/`
directory is the orchestrator-owned provenance record, not a writer's private path. Apply standing
rule 6's independent-checker and cleanup sequence to the temporary per-agent paths.

## 1. Read and rank the whole board

Read all classmate posts before recommending any. Return one numbered ranking covering every
classmate, with:

1. the exact roster name;
2. the current nested-reply count, prominently flagging two or more;
3. what the clinician can agree with; and
4. what new substance the clinician can add.

Rank for the strongest opportunity to add useful substance, not randomly and not merely for the
shortest post. Ask the clinician to answer with two ranking numbers. Do not draft until the two
targets are chosen.

Where a classmate's claim contradicts a reputable source, flag the contradiction every time. Do
not draft an admonition or switch to an adversarial register unless the clinician asks for it; that
is a social judgment about a named classmate.

## 2. Build and verify the claim ledger

List every new factual claim the replies may add. A paraphrase of the classmate's post, a statement
of agreement, and the clinician's own argument need no record. A number, threshold, factual
comparison, or empirical assertion does. A source already verified in this board's `claims.md`
may discharge another page-level read, but the new claim does not inherit the earlier claim's
verification. Give it a new `RESTATEMENT` and a new `REFUTATION`; it inherits `REFERENCE`,
`RESOLVED` and `PAGE-YEAR`, which are facts about the page already opened. `respent-source` remains
reply against reply and never compares a reply file with `post.md`, so a course-required initial-post
source does not become unavailable to every reply.

Create `claims.md` with a `DATE:` header and one `## CLAIM:` heading per claim before research
begins. Start the heading with the response filename's target slug, for example
`## CLAIM: [REPLY: maren] The combined program reported a 12% improvement.` This is the join that
keeps the same number in another reply's record from tracing the wrong assertion. Fan out one
research agent per claim. Each returns a reputable source from one of
four classes, `society guideline`, `peer-reviewed`, `government`, or `tertiary reference`, plus a
full APA 7 reference, a restatement in the source's own terms, the URL or DOI actually opened and
the read date, and the page's stated year and where it appears. The orchestrator alone writes the
records.

Then send every sourced record to a different agent briefed to refute it. The second agent tries to
prove the reference, locator, year, bibliographic details, or restatement wrong and returns
`stands`, `refuted`, or `paywalled` with a substantive reason. A refuted record is repaired or made
honestly unsourced before drafting; it is never cited.

Each record uses the full research-ledger shape:

```text
## CLAIM: [REPLY: <response filename target>] <the claim, including any number the reply will state>
STATUS: sourced | unsourced - <what was searched>
SOURCE: society guideline | peer-reviewed | government | tertiary reference
REFERENCE: <full APA 7 entry>
RESTATEMENT: <what the source says, including the reply's exact numeric token where applicable>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled - <reason>
```

For `unsourced`, put what was searched on the `STATUS` line and omit the other fields. Within two
years is the target, within five is ordinarily expected, and an older source may stand only when
nothing newer exists and the record says what was searched. No tool here touches the network; the
research and refutation agents open the sources.

After all records and refutations are gathered, a fresh non-authoring context runs:

```bash
python tools/research_ledger.py scratch/runs/<run-key>/claims.md
```

Its exit must be 0 before a sourced claim is drafted. The record vocabulary, recency rules, and
all failure rows are also written in
[practicum-case-study](../practicum-case-study/SKILL.md) step 3 for a reader who cannot run the
command.

## 3. Draft reply one

Read `scratch/voice-model.md`, especially the confirmed reflective and argumentative register. Use
its discriminating pairs and confirmed constructions. Do not reproduce chat typos or lowercase
message openings. Where the model says craft metaphors or named philosophers intensify in
citation-bearing writing, preserve that option; it licenses adding none and never licenses adding
a second instance because the first sounded good.

Open with the selected classmate's exact roster first name and a comma. Concede what is right in
full, then add or refuse on a genuinely different axis when the argument calls for it. A hedge
attaches to a fact; it does not suspend the reply's commitment. Keep the reply conversational and
substantive. Do not add a heading. End with a plain `References` label, not a Markdown heading, and
put each APA entry in its own paragraph separated by a blank line.

Before the `References` label, mark each consciously added craft metaphor or named-philosopher move
on its own invisible working line:

```html
<!-- AMPLIFICATION: craft metaphor -->
```

Use one marker per instance and say which kind it is. These are working annotations: do not type
them into the LMS. The grader strips them from the word count, prints their count, and never grades
the count.

## 4. Independently grade, show, and post reply one

After the drafting context returns the response, a fresh non-authoring context runs:

```bash
python tools/discussion_reply_scan.py scratch/runs/<run-key>
```

The default report is counts only. It reports how many `posts/*.md` files supplied an `AUTHOR:` and
refuses partial roster coverage, then verifies the response filename and addressed first name
against that roster, the 100-word floor, one APA author-year reference backed by the corresponding
tagged claim record, every recognized APA narrative or parenthetical author-year citation resolving
to that response's own list, every Arabic numeral in the body tracing to an exact token in that
response's tagged `CLAIM` heading or `RESTATEMENT`, and no source appearing in more than one
response. Citation years and page locators, and the reference list, are excluded from the
numeric-claim walk. Reference entries must be separated by blank lines and copied from the ledger's
`REFERENCE` field. `--show` prints names and finding detail, so its output is private working
material and must not be pasted.

Exit 0 means every scanned reply passes, 1 means a finding, and 2 means the run was not completely
scannable. Fix any finding through the original drafting context, preserve the first checker
result, and have another fresh context grade the correction.

Show the clean reply to the clinician. Only an explicit go-ahead for this reply authorizes posting.
In the browser, type the reply into the LMS rather than pasting it, preserving the authored line
breaks and omitting the `AMPLIFICATION` comments. Submit it, then reread the posted board version.

## 5. Draft and post reply two sequentially

Only after reply one is posted, draft reply two. Read the posted first reply and its reference list
before writing. Do not reuse its source or figure. The clinician's review is the pacing; add no
artificial delay.

Run the same independent ledger and discussion-reply checks over the completed run. The grader
compares every response file, so a repeated source now fails. Show reply two and wait for a new,
explicit posting go-ahead. Then type, submit, and reread it on the board on the same terms as reply
one.

## Completion

Report the two posted addressees, the two grader exits, and the amplification count for each reply.
Keep every `board-<date>.md`, `posts/`, `post.md` when present, `claims.md`, and both replies
together under the run key as the private provenance record. Remove every temporary per-agent path
after the independent checks; if cleanup fails, report the exact remaining path.
