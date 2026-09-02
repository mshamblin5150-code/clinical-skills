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

The clinician signs the bar before drafting, reads the finished post, and gives the explicit
go-ahead before anything is pasted into the LMS. Authorization to read, research, draft, or render
is not submission authorization.

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
artifact. Write the finished pair only to:

```text
output/discussions/<course>-<module>-discussion-<date>.md
output/discussions/<course>-<module>-discussion-<date>.docx
```

Parallel readers and researchers each receive a new run-unique private path that no sibling reads
or writes. They return findings to the orchestrating context and never append to the canonical run
files. The orchestrator is the sole writer of `board-<date>.md`, `bar.md`, `claims.md`, `post.md`,
`differentiation.md`, `reread.md`, and `voice-status.md`. Apply standing rule 6's independent-checker and
cleanup sequence to every temporary path.

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

If `scratch/voice-model.md` is absent, follow [voice.md](../practicum-case-study/reference/voice.md)
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
[apa7.md](../practicum-case-study/reference/apa7.md), including its legal-entry form and declared
`C.F.R.`-only limit; do not recall a form the sheet does not cover. Use the full record shape:

```text
## CLAIM: <the drafted claim, including its exact numeric token where applicable>
STATUS: sourced | unsourced - <what was searched>
SOURCE: society guideline | peer-reviewed | government | tertiary reference
REFERENCE: <full APA 7 entry>
RESTATEMENT: <what the source says, including the draft's exact numeric token where applicable>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled - <reason>
SECOND-ROUTE: <research route> -> <refutation route>
STATED-EXPIRY: none stated | <ISO date> - <where the document states it> | <ISO date>, superseded cited deliberately - <reason>
```

For `unsourced`, put what was searched on the `STATUS` line and omit the other fields. The source
classes and recency dispositions are the same ones in `practicum-case-study` step 3: within two
years is the target, within five is ordinarily expected, and `nothing newer` names what was
searched. `guideline in force` applies only when the cited guideline is presently in force and the
record says why; membership in a catalog does not establish standing.

Fan out one research context per claim. Each returns the source class, full APA 7 reference,
restatement, opened URL or DOI and read date, the page's stated year and locator, and the source's
stated expiry or `none stated`. Transcribe only an expiry the document states; do not infer one from
a publication cadence. `42 C.F.R. § 414.56 (2025)` is the known case where `none stated` is correct:
the codification year is provenance, and the annual reissue schedule is not a stated expiry. The
orchestrator alone writes the records. Then send every `sourced` record to a different context
briefed to disprove the reference, locator, year, bibliographic details, or restatement. It returns
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

After every research and refutation result is gathered, a fresh non-authoring context runs:

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

Give a fresh reader `posts/` and the completed working draft. Have it report where the classmate
posts converge and where the clinician's already differs. Write that report to
`differentiation.md` and show it to the clinician. This is a differentiation read, not permission
to import classmates' claims or normalize the draft toward their median.

Any substantive change made after this read reopens the affected claim records and reference
walk. A new factual sentence is researched and independently refuted on the same terms as step 3.

## 6. Write and independently grade the finished Markdown

Copy the approved working text to `output/discussions/<course>-<module>-discussion-<date>.md`. Keep the
`INVOKED` comments in the Markdown working artifact so the count remains auditable. End with the Markdown heading `## References`. This is the form the post grader and reference scanner both read.
`docx_write.py --bold-headings` drops the own-line comments and renders the heading as direct bold
formatting without a named heading style before the document is pasted into the LMS. This differs
from `discussion-reply`, which pastes from Markdown directly and therefore still requires a person
to omit its working comments.

Fresh, non-authoring contexts run each artifact grader. One context never grades an artifact it
authored, and a repair is checked by another fresh context:

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
The `bold-headings`, `rendered-comments`, `rendered-text`, and `rendered-pages` rows report `not graded` at this
stage because the document does not exist yet; step 7 renders it and reruns this grader with
`--docx`.

Exit 0 means the scanner's rows pass, 1 means a finding, and 2 means it did not completely scan.
Preserve the original checker result, fix findings through the drafting context, and have a new
non-authoring context check the correction. Then walk `discussion_post_scan.NOT_REACHED` item by
item against the live pages, signed bar, draft, and ledger. In particular, read whether an ISBN or
other prose bar element is present and whether a reference supports the proposition the bar
requires; do not substitute a reference count for either judgment.

## 7. Render and inspect the `.docx`

Render the checked Markdown:

```bash
python tools/docx_write.py output/discussions/<course>-<module>-discussion-<date>.md output/discussions/<course>-<module>-discussion-<date>.docx --bold-headings
python tools/discussion_post_render.py scratch/runs/<course>-<module>-discussion --docx output/discussions/<course>-<module>-discussion-<date>.docx
```

`discussion_post_render.py` creates a new retained `render/pass-N/`, keeps Word's page-faithful PDF
or XPS there, and writes one 120-dpi PNG per page beside it. It asks a freshly spawned
`Word.Application` to open the document read-only with conversion
confirmation disabled, without touching `Application.Visible`. Its first route is
`ExportAsFixedFormat2(path, 17)` followed by PyMuPDF; if Word's PDF route fails, it uses
`SaveAs2(path, wdFormatXPS)` followed by the same reader. PyMuPDF opened directly on the `.docx`
is not a route: it reflows the document and cannot supply Word's pagination. The command prints the
source, exported page count, and retained pass directory. An exit of 2 means no complete pass was
retained and the document was not visually checked.

The `rendered-comments` row must be 0. It reads the Word artifact for either HTML-comment
delimiter, so residue from a mid-line or multi-line form fails even though the renderer warns and
continues. The Markdown keeps the own-line audit comments; the document does not.

The `rendered-text` row reports whether the draft and document paragraph text differ. It is
reported, not graded: a nonzero result must be read and reconciled, but does not change the
scanner's exit status because list markers, fields, and other document structure can make the
paragraph streams differ without losing prose.

The Markdown is the authoritative artifact. If the renderer refuses an existing document, the
refusal can mean Word or a person owns changes that Git cannot restore. Read the document and
recover the edit into the Markdown and its claim ledger, and only then ask the clinician before passing
`--force`. The flag is available after recovery; it is never a substitute for recovery.

A vision-capable, non-authoring context compares every retained page image with the Markdown and
reports clipping, overlap, missing text, broken references, bad page breaks, or misplaced
headings. A text-only reread does not substitute for the visual check. Each pass is one
rasterization: if the PDF route cannot image every page, its pixels are discarded before the XPS
route begins, so the retained images always come from the retained export. If both Word exports
fail, ask the clinician to export the document as PDF or XPS and rerun with
`--clinician-export <PDF-or-XPS>`; this records `SOURCE: clinician` while the agent still
rasterizes and compares every page. Name any page the reader did not compare under `UNSEEN:`. The
clinician is an escalation, not an equal first route.

After the comparison, append this exact record to the private `post.md`:

```text
## RENDERED: post.md
PAGES: 3 of 3 imaged
SOURCE: word-pdf
UNSEEN: none
READ: 2026-08-30
VERDICT: clean - three pages compared; headings bold, references hang, nothing clipped
```

`SOURCE:` is `word-pdf`, `word-xps`, or `clinician`. Re-renders append: never replace an earlier
record or overwrite its evidence. Each new comparison writes the next `render/pass-N/` and appends
one matching record. Every record must parse, its expected count must equal the retained export's
page count, and its imaged count must equal the PNG count in its own pass. An earlier pass may stop
short after finding a defect; only the last pass must image and compare every page, name
`UNSEEN: none`, and carry a `clean` verdict with substantive reading detail.

Now rerun the grader:

```bash
python tools/discussion_post_scan.py scratch/runs/<course>-<module>-discussion --draft output/discussions/<course>-<module>-discussion-<date>.md --docx output/discussions/<course>-<module>-discussion-<date>.docx
```

The `rendered-pages` row must be 0. A missing or malformed record, an unrecognized source, a
record-to-pass count mismatch, or a missing or unreadable retained export is a finding. A partial
page count or anything other than `none` under `UNSEEN:` is a finding on the last pass; it remains
visible without failing an earlier pass abandoned after a defect. A last verdict that is not clean
is also a finding. Any finding makes the scan exit 1. The retained render directory is run evidence
and survives cleanup.

The clinician pastes from Word because direct bold on each heading survives as inline bold in the
LMS. The paste discards the hanging indent, centering, page break, and first-line indent; those
properties remain in the document because the visual check above still needs a paper-shaped file.

## 8. Approve, paste, and reread

Show the final post and the clean-check summary to the clinician. Wait for an explicit go-ahead.
That approval includes confirming that every edit implicated by a destination-guard refusal was
recovered into the authoritative Markdown and, where it changes a factual claim, the claim ledger
before any forced render.
Paste from Word into the LMS and inspect the paste box before submitting. Submit only after that
inspection, then reread the posted board version.

The graders read the Markdown and ledger, not the LMS editor. A clean pre-post scan is not a
checked post in the box. The reread owns lost headings, broken paragraphs, missing references, and
any change introduced by paste.

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

Replace `matches` with `diverges` when the board and artifact differ. Both verdicts require
substantive text after the keyword. Record a divergence without changing
the already graded output artifact. A board repair is available only when the clinician directs
that live coursework edit; no repair is automatic. Do not capture or diff the board against the
artifact. Rerun `discussion_post_scan.py` with the same `--draft` and `--docx`; its exit must be 0.
Then walk `discussion_post_scan.NOT_REACHED`, whose posted-reading row declares that reply records
belong to the sibling grader.

## Completion

Report the board key, signed-bar date, research-ledger exit, reference-scan exit,
discussion-post-scan exit, body word count, stated ceiling and whether it was exceeded, reference
count, claim-record count, invoked-source count, unfilled-property count, pre-#496 marker count,
paywalled-claim count,
rendered-page verdict, and the recorded posted-reading verdict.
Keep `board-<date>.md`, `posts/`, `bar.md`, `claims.md`, `post.md`, `differentiation.md`,
`reread.md`, and `render/`, plus `voice-status.md` when present, together under the board-keyed run. Remove every
temporary per-agent
path after the independent checks; if cleanup fails, report the exact remaining path.
