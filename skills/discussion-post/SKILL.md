---
name: discussion-post
description: Read one LMS board and its course syllabus live, derive and confirm the graded bar, then research, draft, verify, render, and submit an evidence-backed initial post. Use for a nonpatient initial post whose shape comes from its prompt; route a worked clinical case to practicum-case-study.
---

# Initial post

Write the clinician's initial post for one board. Its skeleton comes from that board's prompt and
may change from one board to the next. Do not configure a skeleton or a course-specific bar.

If the prompt asks for a worked clinical case, this is not the skill. Hand the board URL
to [practicum-case-study](../practicum-case-study/SKILL.md), whose clinical reasoning, coding, and
patient safeguards are required. This routing line is also the PHI line: `discussion-post` never
accepts patient material. A prompt asking for policy analysis, professional reflection, ethics,
leadership, or another nonpatient academic argument remains here.

The clinician signs the bar before drafting, reads the finished post, and gives an explicit
go-ahead before it is loaded into the LMS. After an independent reading of the rendered Canvas
box, the clinician gives a second explicit go-ahead before submission. Authorization to read,
research, draft, render, or load is not submission authorization.

## Inputs, outputs, and one board-keyed run

The input is one board URL in the clinician's signed-in browser. A Canvas-style URL of
`/courses/<id>/discussion_topics/<id>` supplies the course identifier needed to derive
`/courses/<id>/assignments/syllabus`; do not ask for a second URL when that derivation works.

Derive a lowercase run key from the live course and module breadcrumbs, then append this skill's
fixed artifact word, `discussion`. The key has no date in it. A run
is keyed to the board, not to the sitting, as recorded in
[ADR 0005](../../docs/adr/0005-a-run-is-keyed-to-the-board.md). Write private state only under:

```text
scratch/runs/<course>-<module>-discussion/
    board-<date>.md
    posts/
    bar.md
    claims.md
    post.md
    differentiation.md
    reread.md
    voice-status.md
    render/pass-N/
```

Each sitting writes a new `board-<date>.md`; never overwrite an earlier snapshot. `posts/` holds
one file per classmate for provenance. `post.md` is the private working draft, not the handed-over
artifact. Write the finished submission and its renders only to:

```text
output/discussions/<course>-<module>-discussion-<date>.md
output/discussions/<course>-<module>-discussion-<date>.html
output/discussions/<course>-<module>-discussion-<date>.docx
```

The `.html` is the submission loaded into Canvas. The Markdown is its source of record, and the
`.docx` is its archival paper-shaped rendering. `output/` holds the submission and its renders;
provenance stays in the run directory.

For this skill, the canonical artifacts governed by [standing rule 6](../../AGENTS.md) are
`board-<date>.md`, `bar.md`, `claims.md`, `post.md`, `differentiation.md`, `reread.md`, and
`voice-status.md`; each worker's temporary path is separate and run-unique.

## 1. Route from the prompt, then snapshot the nonpatient board

Open the topic live and first read only its breadcrumbs and prompt. **If the prompt asks for a
worked clinical case, stop this skill now.** Hand the board URL to `practicum-case-study`; do not
create a discussion run directory, read the classmate contributions, write a snapshot, derive a
bar, or accept any patient material here. The clinical skill derives the `case-study` run key and
owns those patient-bearing reads and writes.

For a nonpatient prompt, continue in this skill. Read the point value, due dates, the clinician's
existing contribution if any, every classmate initial post, and every nested reply. The live board
is authoritative, including edits. Write the complete state to `board-<date>.md` and split the
classmate contributions under `posts/` for provenance.

The drafting context does not see the classmate posts. Give it only the prompt, the signed bar,
and `scratch/voice-model.md`. Neighboring posts demonstrate what normal looks like; showing them
before drafting quietly normalizes the clinician's argument toward the board.

Open the derived syllabus page. Read the initial-post bar there: word floor and ceiling, reference
minimum, source recency, required textbook or ISBN, and every other stated element. The topic page
overrides the syllabus when both state the same bar element; the syllabus fills the topic's
silence. This precedence is declared and has not been observed in a live conflict, so report the
conflict rather than silently choosing when a new shape makes the rule ambiguous.

## 2. Write and sign `bar.md`

Transcribe the relevant topic and syllabus language verbatim as block quotes, each with the page
it came from. Above the quotes write the mechanical fields exactly once:

```text
TOPIC: <the board URL>
SYLLABUS: <the derived syllabus URL>
SIGNED: <ISO date after clinician approval>
WORD-FLOOR: <integer, or 0 when none is stated>
WORD-CEILING: <integer, or none>
REFERENCE-MINIMUM: <integer, or 0 when none is stated>
SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference
RECENCY-WINDOW-YEARS: 5

## Topic bar

> <verbatim topic language>

## Syllabus bar

> <verbatim syllabus language>
```

Show `bar.md` to the clinician and wait for an explicit confirmation that the transcription and
precedence are right. Only then write `SIGNED:` and begin drafting. A run that reads, transcribes,
and grades its own transcription without this checkpoint is grading its own interpretation.

The word floor is graded. The ceiling is counted and never graded: the clinician deliberately
exceeds stated maxima. A clean mechanical scan therefore never means the post obeyed the ceiling.
The reply skill's ceiling rule also binds this artifact; quoted verbatim, it reads: No stated
maximum is honored. Never trim a drafted reply to fit a word ceiling: the clauses a
ceiling removes first are the ones that bound a claim, because those are the clauses that read as
optional. Where a reply genuinely runs long, cut a whole point rather than the qualifiers on a
point you are keeping. The artifact governed by that rule in this skill is the initial post.
Every prose bar element remains a reader's check; `discussion_post_scan.NOT_REACHED` is the single
inventory of what that command cannot decide.

## 3. Draft blind, then derive the claim set from the document

Read `scratch/voice-model.md` and use register 3 throughout. Preserve confirmed sentence shapes,
hedges attached to facts, and the clinician's argumentative posture. Do not copy chat typos or
lowercase message openings. An invoked source already present in the clinician's reasoning may
stay; the skill is licensed to add none.

If `scratch/voice-model.md` is absent, follow [voice.md](../_shared/reference/voice.md)
§8's no-model rule in full. Write the declaration it requires to
`scratch/runs/<course>-<module>-discussion/voice-status.md`. Keep `voice-status.md` in the private
run record; do not copy it into the finished post or the LMS.

Mark every retained invoked source on its own working line:

```html
<!-- INVOKED: <domain> | <property> -->
```

Name the domain the invoked source draws on and state the property as a predicate-bearing clause
describing the real behavior the argument spends. A retained
invoked source carries the argument, and its payoff sentence states what that behavior does; do not enlarge the
noun or increase the rate. The domain stays open: do not create a list of permitted domains. The
scanner counts an empty property or a lexical restatement of the domain noun for clinician review
without failing; it does not parse English or prove that other words state the real behavior, because
every retained invoked source here is the clinician's. It still strips and separately reports a retired
`AMPLIFICATION` marker as a pre-#496 marker that is not graded. Keep these own-line comments in the
Markdown; `docx_write.py` drops own-line HTML comments when it renders the Word document.

Write the prompt-shaped working draft to `post.md`, including its in-text citations and reference
list. This is not the finished artifact. Now derive the required claim set from the document
rather than from the run's account of what it intended to claim:

1. every in-text citation; and
2. every Arabic numeral in the body that is not a citation year, page locator, or statute section
   number.

A factual claim without a citation still receives a record when it is new rather than the
clinician's own reasoning. The mechanical `untraced-number` row is a floor, not permission to leave
uncited prose unresearched.

Create `claims.md` with a `DATE:` header and one `## CLAIM:` heading per derived claim. Write each
reference entry from the applicable form in
[apa7.md](../_shared/reference/apa7.md), including its legal-entry form and declared
`C.F.R.`-only limit; do not recall a form the sheet does not cover. Use the full record shape:

```text
## CLAIM: <the drafted claim, including its exact numeric token where applicable>
STATUS: sourced | unsourced | unreadable - <what was searched or what prevented the read>
SOURCE: society guideline | peer-reviewed | government | tertiary reference
REFERENCE: <full APA 7 entry>
RESTATEMENT: <what the source says, including the draft's exact numeric token where applicable>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled | unreadable - <reason>
SECOND-ROUTE: <research route> -> <refutation route>
INSTRUMENTS: <first instrument> -> <second instrument>
STATED-EXPIRY: none stated | <ISO date> - <where the document states it> | <ISO date>, superseded cited deliberately - <reason>
```

Apply the shared sourcing rules below to `unsourced` and `unreadable` records. `INSTRUMENTS` is
also required for `REFUTATION: unreadable` and is forbidden on every other record. The source
classes and recency dispositions are the same ones in `practicum-case-study` step 3: within two
years is the target, within five is ordinarily expected, and `nothing newer` names what was
searched. `guideline in force` applies only when the cited guideline is presently in force and the
record says why; membership in a catalog does not establish standing.

Every research and refutation brief first reads the rules in
[sourcing.md](../_shared/reference/sourcing.md) and applies them to every returned claim or negative.
This **Fan-out brief** applies [standing rule 6](../../AGENTS.md). Each research worker takes one
claim and returns the source class, full APA 7 reference,
restatement, opened URL or DOI and read date, the page's stated year and locator, and the source's
stated expiry or `none stated`. Transcribe only an expiry the document states; do not infer one from
a publication cadence. `42 C.F.R. § 414.56 (2025)` is the known case where `none stated` is correct:
the codification year is provenance, and the annual reissue schedule is not a stated expiry. Each
`sourced` record gets a refutation leg. It returns
`stands`, `refuted`, or `paywalled` with a substantive reason. There is no carve-out for legal
primary sources: a refuter checks whether the cited section says what the draft claims. It also
returns `SECOND-ROUTE: <research route> -> <refutation route>`; both halves must have substance and
must differ after normalization. Before `paywalled`, it attempts the clinician's authenticated
Chrome route through `mcp__claude-in-chrome__*`, not the separate in-app Browser pane. Refuter
independence remains orchestrator-owned; see `research_ledger.DECLARED_LIMITS`. A source is
`paywalled` only when its body remains inaccessible through that **Authenticated route**; an
anonymous or in-app login wall does not establish the disposition.
When the account profile records that the **Authenticated route** is available, the research
context must try it before giving up on a preferred source, settling for a reachable substitute,
or writing `STATUS: unsourced` because an access wall stopped the search.

A source already verified elsewhere in this board's ledger may discharge a second page-level
read. The new claim still gets its own record, a new `RESTATEMENT`, and a new `REFUTATION`; only
`REFERENCE`, `RESOLVED`, `PAGE-YEAR`, and `STATED-EXPIRY` may be inherited because those describe
the page already opened. `SECOND-ROUTE` belongs to the new refutation and is never inherited. A
claim is never inherited from another sentence.

After every research and refutation result is gathered, this **Grader handoff** under
[standing rule 6](../../AGENTS.md) runs:

```bash
python tools/research_ledger.py scratch/runs/<course>-<module>-discussion/claims.md
```

The grader's coverage boundaries are inventoried in
`research_ledger.DECLARED_LIMITS`; this skill points there without copying its rows.

Exit 0 means the records are mechanically complete, 1 means a finding, and 2 means the ledger was
not scanned. The refutation pass and the draft-to-ledger read own the source-support judgment.

## 4. Resolve dead claims before the draft is final

Apply every ledger disposition before promoting `post.md` to the finished artifact:

- `refuted`: the sentence is cut, not softened or hedged;
- `unsourced`: the sentence may survive only as clearly uncited clinician reasoning, and the
  unearned reference is removed; and
- `paywalled`: the claim may ship on the recorded terms, and it is counted in the completion report on
  its own line.

Report every cut to the clinician before the draft is final because removing a sentence changes
the argument. Repair the reference list after the cuts. A source supporting no surviving sentence
is deleted rather than left as decoration.

## 5. Differentiate only after the clinician's draft exists

Give this **Second reader** under [standing rule 6](../../AGENTS.md) `posts/` and the completed
working draft. Have it report where the classmate
posts converge and where the clinician's already differs. Write that report to
`differentiation.md` and show it to the clinician. This is a differentiation read, not permission
to import classmates' claims or normalize the draft toward their median.

That differentiation reader first reads and applies
[sourcing.md](../_shared/reference/sourcing.md); a remembered or indexed classmate claim remains a
pointer until the retained post is graded against it, and a failed read reports unreadable rather
than absent.

Any substantive change made after this read reopens the affected claim records and reference
walk. A new factual sentence is researched and independently refuted on the same terms as step 3.

## 6. Write and independently grade the finished Markdown

Copy the approved working text to `output/discussions/<course>-<module>-discussion-<date>.md`. Keep the
`INVOKED` comments in the Markdown working artifact so the count remains auditable. End with the Markdown heading `## References`.
This is the source of record that the post grader and reference
scanner both read. Both renderers consume `docx_write.blocks`, so own-line comments leave both
renders without a second omission rule. `discussion-reply` builds its reply submission with the
same HTML renderer.

Each source grader is a **Grader handoff** under [standing rule 6](../../AGENTS.md):

```bash
python tools/research_ledger.py scratch/runs/<course>-<module>-discussion/claims.md
python tools/reference_scan.py output/discussions/<course>-<module>-discussion-<date>.md --as-of <submission date>
python tools/discussion_post_scan.py scratch/runs/<course>-<module>-discussion --draft output/discussions/<course>-<module>-discussion-<date>.md
```

`reference_scan.py` walks the APA list and citation resolution unchanged. Its exit must be 0.
`discussion_post_scan.py` grades the signed word floor and reference minimum. Its
`untraced-number` row requires every distinct body-number value to appear in a claim record;
repeating a value does not spend another record. Its `untraced-citation` row requires every
in-text citation to have a claim record for its source, while `respent-record` requires each
citation to carry its own record. One record may therefore trace a number and carry the citation
beside it, but two citations may not spend that record. The report counts distinct numeric values
and claim records, along with the word ceiling, invoked sources, and unfilled invoked properties;
the latter fields remain counted without grading. Its default output is counts only; `--show`
includes private finding detail and must not be pasted.

The `bold-headings`, `rendered-comments`, `submission-text`, `rendered-text`, and
`rendered-pages` rows report `not graded` at this stage because neither render has been supplied.
Step 7 writes both renders; step 8 supplies the Canvas-box evidence and runs the artifact rows.

Exit 0 means the scanner's source rows pass, 1 means a finding, and 2 means it did not completely
scan. Preserve the original checker result, fix findings through the drafting context, and repeat
the declared grading surface on the correction. Then walk `discussion_post_scan.NOT_REACHED` item
by item against the live pages, signed bar, draft, and ledger. In particular, read whether an ISBN
or other prose bar element is present and whether a reference supports the proposition the bar
requires; do not substitute a reference count for either judgment.

## 7. Generate the HTML submission and archival `.docx`

Generate both renderings from the checked Markdown:

```bash
python tools/post_html.py output/discussions/<course>-<module>-discussion-<date>.md output/discussions/<course>-<module>-discussion-<date>.html
python tools/docx_write.py output/discussions/<course>-<module>-discussion-<date>.md output/discussions/<course>-<module>-discussion-<date>.docx
```

`post_html.py` writes the exact bytes the agent will load into Canvas's raw editor. Every URL
outside a code span becomes a link whose text is the URL itself, so each reference can be followed
from the board. Every Markdown heading becomes `<p><strong>`; paragraph and inline text come from
the same block and inline parsers as the Word renderer. An authored `> ` line becomes a semantic
`<blockquote>` with the
marker consumed. A Bluefield NUR 5144 M2 measurement on 2026-09-08 found that the tag survived and
its text rendered 19.8 pixels right of ordinary paragraph text, not at APA's 0.5-inch left indent;
the dated geometry is in
[_shared/reference/canvas-editor-calibration.json](../_shared/reference/canvas-editor-calibration.json).
A clean scan does not claim
exact APA indentation, and the pixel-backed box reading still verifies the current form before
Gate 2. Own-line comments are absent. A mid-line or multi-line HTML comment
remains a real delimiter so `rendered-comments` can refuse it rather than hiding it in the box.

The `.docx` is archival and uses proper named heading styles. ADR 0013's direct-formatting
`--bold-headings` route is historical: its Word-to-Canvas measurement remains the reason the HTML
route uses `<strong>`, but no discussion-post document is destined for a Word paste now.
The archive is graded only through `rendered-text`, a reported paragraph-text parity count that
does not change exit status. It is not rasterized or visually graded, because it is not the
submission.

The Markdown is the authoritative artifact. If the Word renderer refuses an existing document, the refusal
can mean Word or a person owns changes Git cannot restore. Read the document and recover the edit
into the Markdown and its claim ledger, and only then ask the clinician before passing `--force`.
The flag is available after recovery; it is never a substitute for recovery.

## 8. Gate 1, load, independently read the box, Gate 2, and submit

Before the retained captures are decoded, run:

```bash
python tools/pdf_engine.py
```

On exit 1, ask the clinician for permission to run the install line the check printed and run the
check again after an attempted install. If permission is declined or the install fails, walk the
rendered-page rules in this step by eye and retain that result for the completion report. Exit 2
from the check does not establish that the engine is missing and stops this step for investigation.

Before Gate 1, inspect the topic-level Canvas Composer and read
[canvas-editor.md](../_shared/reference/canvas-editor.md). Choose its first supported **Load route**
before loading, and declare the route and its cost to the clinician at Gate 1. This trigger applies
because the live assignment accepts the initial post through the topic-level Composer.

Show the final post and clean source-check summary to the clinician. **Gate 1** is the clinician's
explicit approval of the post and authorizes loading it into the box, not submission. That approval
also confirms that every edit implicated by a destination-guard refusal was recovered into the
authoritative Markdown and, where it changes a factual claim, the claim ledger.

Load the exact `.html` contents by the route declared at Gate 1, following `canvas-editor.md`, and
inspect the rendered Composer before doing anything else.

Create the next retained `render/pass-N/`. Copy the exact output `.html` into that pass as
`post.html`, and retain enough PNG captures of the scrolling Canvas box to make every rendered
block visible. The destination is the rasterizer: a text-only reread does not replace these pixels.
A vision reader first reads and applies [sourcing.md](../_shared/reference/sourcing.md) before it
reports anything from the retained render.
This vision-capable **Second reader** under [standing rule 6](../../AGENTS.md) compares the captures
with the Markdown and accounts for every
nonblank block derived through `docx_write.blocks`. The denominator comes from the submitted HTML
render, never from the record and never from the capture count. Append this exact shape to the
private `post.md`:

```text
## RENDERED: post.md
BLOCKS: 13 of 13 read
SOURCE: canvas-box
UNSEEN: none
READ: 2026-09-08
VERDICT: clean - all 13 blocks compared; headings bold, paragraphs and references present
```

Replace `13` with the derived block count. Re-renders append: never replace an earlier record or
overwrite its evidence. Every record must parse, each pass must keep exactly one `.html` export
whose bytes equal the submitted HTML and at least one readable PNG capture, and the expected block
count must equal the export's count. An earlier pass may stop after a defect; only the last pass
must account for every block, name `UNSEEN: none`, and carry a clean verdict with substantive
reading detail.

Run the artifact grader:

```bash
python tools/discussion_post_scan.py scratch/runs/<course>-<module>-discussion --draft output/discussions/<course>-<module>-discussion-<date>.md --html output/discussions/<course>-<module>-discussion-<date>.html --docx output/discussions/<course>-<module>-discussion-<date>.docx
```

The HTML submission owns the graded `bold-headings`, `rendered-comments`, `submission-text`,
and `rendered-pages` rows. The archival Word document owns only the reported `rendered-text`
count. A missing or malformed record, an unreadable capture, a nonidentical retained HTML export, a
false block denominator, an incomplete final reading, or a non-clean final verdict makes the scan
exit 1.

Show the captures to the clinician and say explicitly that the Canvas box is loaded and unsubmitted.
A non-clean reading stops here and returns to the clinician; the agent does not
adjudicate its own load, switch routes, or retry. **Gate 2** is the clinician's explicit
authorization to submit. Gate 2 authorizes submit and nothing else does. After Gate 2, submit and reread
the posted board version.

The graders read the Markdown, HTML, Word archive, and ledger; the reread owns any change between
the inspected box and the posted entry.

After submission, read the initial entry's Copy Link and the board's posted timestamp. Add
`POST-URL:` and `POSTED:` fields to the private `post.md`; this working record is not the graded
output artifact. Append this record to the run's one `reread.md`, preserving any reply records:

```text
## REREAD: post.md
POST-URL: <the initial post's own deep link>
POSTED: <the board's posted timestamp>
READ: <ISO date of this reading>
VERDICT: matches - <what the reading found>
```

Replace `matches` with `diverges` when the board and artifact differ, including when a reference URL
on the board is not a link. Both verdicts require
substantive text after the keyword. Record a divergence without changing
the already graded output artifact. A board repair is available only when the clinician directs
that live coursework edit; no repair is automatic. Do not capture or diff the board against the
artifact. Rerun `discussion_post_scan.py` with the same `--draft`, `--html`, and `--docx`; its exit
must be 0.
Then walk `discussion_post_scan.NOT_REACHED`, whose posted-reading row declares that reply records
belong to the sibling grader.

Now invoke `/AAR` with the output Markdown stem as the submission key. After it exits clean, rerun
the same grader one final time with the same `--draft`, `--html`, and `--docx` plus
`--submission <output-Markdown-stem>`. Its report must include `the after-action review: clean`;
the earlier pre-post and rendered passes deliberately report that row as not graded.

## Completion

Do not report completion until the final `discussion_post_scan.py ... --submission <output-Markdown-stem>` exits 0, except that its exit 2 is accepted when this run's engine check reported the engine missing and the install did not happen. In that case report that the run is not mechanically verified and that the rendered-page rows were walked by eye. A finding still stops the run. Report the board key, signed-bar date, research-ledger exit, reference-scan exit,
discussion-post-scan exit, body word count, stated ceiling and whether it was exceeded, reference
count, claim-record count, invoked-source count, unfilled-property count, pre-#496 marker count,
paywalled-claim count, unreadable-status count, unreadable-refutation count,
rendered-box verdict, and the recorded posted-reading verdict.
Keep `board-<date>.md`, `posts/`, `bar.md`, `claims.md`, `post.md`, `differentiation.md`,
`reread.md`, and `render/`, plus `voice-status.md` when present, together under the board-keyed run. Remove every
temporary per-agent
path after the independent checks; if cleanup fails, report the exact remaining path.
