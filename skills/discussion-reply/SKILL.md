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

Derive a lowercase run key from the page's course and module breadcrumbs, then append the fixed
artifact word `discussion`. The key has no date in it. A
run is keyed to the board rather than to the sitting, as recorded in
[ADR 0005](../../docs/adr/0005-a-run-is-keyed-to-the-board.md). Do not configure course names or
module names elsewhere. Write only under the gitignored working directory:

```text
scratch/runs/<course>-<module>-discussion/
    board-<date>.md
    posts/
    claims.md
    post.md
    response-<name>.md
    reread.md
    voice-status.md
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
to the orchestrating context and never append to `board-<date>.md`, `claims.md`, `reread.md`, or a
reply file. The orchestrator is the sole writer of those artifacts, including `voice-status.md`.
The canonical
`scratch/runs/<run-key>/` directory is the orchestrator-owned provenance record, not a writer's
private path. Apply standing rule 6's independent-checker and cleanup sequence to the temporary
per-agent paths.

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
message openings. Where the model says invoked sources intensify in citation-bearing writing,
preserve that option; it licenses adding none and never licenses adding a second instance because
the first sounded good.

Before drafting, run:

```bash
python tools/voice_model_scan.py
```

Exit 0 is required to draft against the model. Exit 1 refuses the draft until the model's shape is
repaired. Exit 2 takes the absent-model door below explicitly: preserve the command's `voice
unmodeled` banner in `scratch/runs/<run-key>/voice-status.md`, then follow §8 rather than treating an
unscanned model as clean. The default report is counts only. `--show` is private working material
and must not be pasted. A clean scan grades shape, not whether the model is true of the clinician.

If `scratch/voice-model.md` is absent, follow [voice.md](../practicum-case-study/reference/voice.md)
§8's no-model rule in full. Write the declaration it requires to
`scratch/runs/<run-key>/voice-status.md`. Keep `voice-status.md` in the private run record; it is
not part of the reply typed into the LMS.

Open with the selected classmate's exact roster first name and a comma. Concede what is right in
full, then add or refuse on a genuinely different axis when the argument calls for it. A hedge
attaches to a fact; it does not suspend the reply's commitment. Keep the reply conversational and
substantive. Do not add a heading. End with the bold Markdown label `**References**`; the reply is
typed into the LMS without a renderer, so this source form is what preserves the clinician's bold
label. Put each APA entry in its own paragraph separated by a blank line.

Before the `References` label, mark every invoked source that is present, whether inherited,
deliberate, or arrived at, on its own invisible working line:

```html
<!-- INVOKED: <domain> | <property> -->
```

Use one marker per instance. Name the domain the invoked source draws on and state the property as
a predicate-bearing clause describing the real behavior the argument spends. A retained invoked source carries the argument, and its payoff sentence states
what that behavior does; do not enlarge the noun or increase the rate. An invoked source with no
property is decorative and must be cut. The domain stays open: do not create a list of permitted domains. These are working
annotations and never reach the LMS. The grader strips them from the word count and refuses an
empty property or one that merely restates the domain noun. It still strips and separately reports
a retired `AMPLIFICATION` marker as a pre-#496 marker that is not graded.

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

Exit 0 means every scanned reply and posted reading passes, 1 means a finding, and 2 means the run
was not completely scannable. Before a new reply is submitted, its one expected finding is
`missing-posted-reading`; every other row must be clean. Fix any other finding through the original
drafting context, preserve the first checker result, and have another fresh context grade the
correction. After submission, the board-side record below must clear that final finding.

Walk `discussion_reply_scan.NOT_REACHED` after a clean scan; it is the single inventory of what the
command cannot decide. A clean scan grades only the mechanically visible set and is not a checked
voice or a checked board. The clinician answers the substance questions from the table below.

Show the clean reply and an invoked-source table to the clinician. For every retained invoked
source, the table shows the invoked source, its domain, and the property it spends. Ask separately whether the substance is
right and whether each invoked source sounds like the clinician; this is one approval with two named
questions, not two gates. When `voice-status.md` exists, show its unmodeled-voice declaration
alongside the reply. Only an explicit go-ahead for this reply authorizes posting.
In the browser, type the reply into the LMS rather than pasting it, preserving the authored line
breaks and omitting the `INVOKED` comments. Submit it, then reread the posted board version. Use the
entry's Copy Link control to read its own `?entry_id=` deep link; do not copy a classmate's locator
from `posts/`. Append this record to the run's one `reread.md`:

```text
## REREAD: response-<name>.md
POST-URL: <the posted reply's own deep link>
POSTED: <the board's posted timestamp>
READ: <ISO date of this reading>
VERDICT: matches - <what the reading found>
```

Replace `matches` with `diverges` when the board and artifact differ. Both verdicts require
substantive text after the keyword. Record a divergence without changing
the already graded response artifact. A board repair is available only when the clinician directs
that live coursework edit; no repair is automatic. Do not capture or diff the board against the
artifact. Rerun `discussion_reply_scan.py` after writing the record; its exit must now be 0.

## 5. Draft and post reply two sequentially

Only after reply one is posted, draft reply two. Read the posted first reply and its reference list
before writing. Do not reuse its source or invoked source. The clinician's review is the pacing; add no
artificial delay.

Run the same independent ledger and discussion-reply checks over the completed run. The grader
compares every response file, so a repeated source now fails. Show reply two and wait for a new,
explicit posting go-ahead. Then type, submit, record, and grade its posted reading on the same terms
as reply one.

## Completion

Report the two posted addressees, the pre-post and post-reading grader exits, each posted-reading
verdict, the invoked-source count for each reply, and any pre-#496 marker count.
Keep every `board-<date>.md`, `posts/`, `post.md` when present, `claims.md`, both replies, and
`reread.md`, plus `voice-status.md` when present, together under the run key as the private
provenance record. Remove
every temporary per-agent path after the independent checks; if cleanup fails, report the exact
remaining path.
