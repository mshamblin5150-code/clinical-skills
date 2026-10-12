---
name: peer-critique
description: Read one classmate's clinical case study live and write the graded eight-heading peer clinical critique against it, sourced, verified, and posted only after the clinician's go-ahead. Use for the peer critique that accompanies a case study, not a conversational discussion reply and not the case study itself.
---

# Peer critique

Write the **peer clinical critique** that accompanies a practicum case study: one scholarly response
to one classmate, under eight fixed headings, sourced and graded. The bar lives in
[_shared/reference/rubric.md](../_shared/reference/rubric.md).

This is not the conversational reply in [discussion-reply](../discussion-reply/SKILL.md), which has
no headings and answers a classmate in a paragraph or two. It is not the case study itself, which
[practicum-case-study](../practicum-case-study/SKILL.md) writes and which stops before the board.
Those two skills each name this deliverable as outside their scope; this is the skill that owns it.
The Reply to the same classmate is a separate artifact, not a substitute for the Peer critique.

The clinician reads every draft and makes the final call. Draft, show, and post only after an
explicit go-ahead. Authorization to read the board or draft the critique is not posting
authorization.

## The bar is not on the graded topic, and that is the first trap

The graded case-study topic carries a thin wrapper. **The peer critique's requirements are in a
separate, ungraded topic**, and that topic's title is frequently a reused name with nothing about
critiques in it. Find it before concluding the assignment is underspecified;
[_shared/reference/rubric.md](../_shared/reference/rubric.md) records the trap and the wrappers'
copy-paste damage.

Read the spec live and sign what it says on this sitting. Do not assume the distilled sheet is
current for this course: it records that the same deliverable is a small rubric line in one course
and a hundred-point assignment in another, and the weight changes what the clinician wants spent on
it. Where the live spec and the sheet disagree, the live spec wins and the disagreement is reported
to the clinician.

At this spec-signing stop, before researching any claim, write `bar.md` with these lines,
taking the source classes and recency window from the live spec where it states them and
using these defaults otherwise:

```text
SIGNED: <leave blank until the clinician answers>
SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference
RECENCY-WINDOW-YEARS: 5
```

Show these lines beside the spec reading. The clinician's answer signs the bar; only then
replace the blank `SIGNED:` value with the ISO date and begin research.

When the clinician asks to cite his own unpublished work, apply
[sourcing.md's own-work bar admission](../_shared/reference/sourcing.md#the-clinicians-own-unpublished-work)
at signing or by mid-run re-signing. `clinician's own work` is never a default template class.

## Inputs and private run state

The inputs are one case-study discussion-topic URL and, where the LMS has assigned one, the peer
review URL. Open them in the clinician's signed-in browser and read live: breadcrumbs, the wrapper
prompt, the master spec topic, the clinician's own case study post, the classmate's post, and every
nested reply. The live board is authoritative, including edits.

Derive a lowercase run key from the page's course and module breadcrumbs, then append the fixed
artifact word `peer-critique`. The key has no date in it; a run is keyed to the board rather than to
the sitting, as recorded in [ADR 0005](../../docs/adr/0005-a-run-is-keyed-to-the-board.md). Do not
configure course names or module names elsewhere. Write only under the gitignored working directory:

```text
scratch/runs/<course>-<module>-peer-critique/
    board-<date>.md
    spec-<date>.md
    bar.md
    posts/
    claims.md
    critique.md
    critique.txt
    critique-stored-comment-readback.txt
    reread.md
    voice-status.md
```

`board-<date>.md` is the complete snapshot as read on this sitting and `spec-<date>.md` is the
master spec topic as read on this sitting; never overwrite an earlier snapshot. Under `posts/`,
write one file per classmate and start each with these fields before the post and its nested
replies:

```text
AUTHOR: Maren Quill
REPLIES: 2
POST-URL: <permalink where the LMS exposes one>
```

`AUTHOR:` is the run roster used by the grader. Classmate posts are manufactured teaching material
and get no PHI detection layer, count, or report. They remain gitignored working material, and a
classmate's name is private working material that is never pasted into a ticket.

For this skill, the canonical artifacts governed by [standing rule 6](../../AGENTS.md) are
`board-<date>.md`, `spec-<date>.md`, `bar.md`, `claims.md`, `reread.md`, `critique.md`, and
`critique.txt`, `critique-stored-comment-readback.txt`, and `voice-status.md`; each worker's
temporary path is separate and run-unique.

## 1. Read the spec, the classmate, and the clinician's own post

Before searching for or reading a Faculty file or Classmate file, follow [LMS attachments](../_shared/reference/lms-attachments.md) and record the sitting's attachment appendix, including when no files are linked.

Read the master spec topic first and write `spec-<date>.md`. Report to the clinician, before
drafting: the eight headings and their sub-questions as the live spec states them, the word range,
the reference floor, and the point weight. Where the LMS has assigned a specific classmate for peer
review, that classmate is the target and there is no ranking step. Where it has not, rank every
classmate on where the clinician can add the most clinical substance and ask him to choose.

Then read three documents side by side and keep them side by side for the whole run: the **case
material** the assignment supplied, the **classmate's post**, and the **clinician's own post** on
the same case.

**Only what the case supplied is in scope.** A case study hands every student one fixed data set. An
item absent from that data set — a family history nobody was given, an insurance field the case
never stated — is not the classmate's omission, and a finding against them for it is a finding
against the assignment. Grade the reasoning applied to what was given. This rule is the one most
easily broken by a reader working from a required-components list rather than from the case.

Read [The clinician's own position](../_shared/reference/rubric.md#the-clinicians-own-position)
before deciding which points to fault; resolve a disagreement with his submission before drafting.

## 2. Find what is clinically at stake before writing anything

Read the classmate's orders under
[Applicable orders](../_shared/reference/rubric.md#applicable-orders).

Before the headings, answer one question in the run record: **is there a missed diagnosis that can
kill, and is the evidence for it inside the classmate's own document?**

A finding the classmate recorded and never carried forward is the highest-value thing this critique
can contain, and it outranks every stylistic observation. Where one exists, the critique's
Clinical Reasoning heading carries it, and it is stated plainly rather than softened.

Two rules govern how a differential is graded, and both cut against reflexive criticism:

- **An entry named and then argued away by the tests is correct practice**, not a defect. A
  differential exists to be narrowed on the record.
- **An entry never made is the failure.** An entry argued off is a decision; an entry that never
  appears leaves nothing to check, and every downstream section — the regimen, the disposition, the
  follow-up — can read as complete while resting on it.

Where the classmate cited a guideline, **read the guideline they cited**. A critique that shows the
answer was inside their own reference is worth more than one that introduces a new source, and it
cannot be dismissed as a difference of reading.

## 3. Build and verify the claim ledger

Every factual claim the critique adds needs a record. A paraphrase of the classmate's post, a
statement of agreement, and the clinician's own clinical argument need none. A number, threshold,
guideline requirement, drug regimen, screening grade, or empirical assertion does.

This **Fan-out brief** applies [standing rule 6](../../AGENTS.md). Create `claims.md` with a `DATE:`
header and one question-form `## CLAIM:` heading per factual point to research; read the canonical voice model's stated principles and invoked sources
for the [invoked-attribution look-ahead](../_shared/reference/sourcing.md#invoked-attributions).
Each research worker
takes one question. When its record returns, rewrite the heading as the source-backed claim under
[sourcing.md](../_shared/reference/sourcing.md), before each sourced record gets its refutation leg.
Every research and refutation brief first reads
[sourcing.md](../_shared/reference/sourcing.md) and applies it to every returned claim or negative.
Immediately before each refutation dispatch, run `python tools/research_ledger.py
scratch/runs/<run-key>/claims.md --heading-digests`, name that claim's printed digest in the brief,
then [save and apply the refuter return](../_shared/reference/sourcing.md#save-and-apply-a-refuter-return)
with the Required command `tools/refutation_apply.py`.

Each record uses the full research-ledger shape:

```text
## CLAIM: <the claim, including any number the critique will state>
STATUS: sourced | unsourced | unreadable - <what was searched or what prevented the read>
SEARCHED-FIRST: store "<clinical question>" -> 0; guidelines "<clinical question>" -> 0
SOURCE: society guideline | peer-reviewed | government | tertiary reference
REFERENCE: <full APA 7 entry>
RESTATEMENT: <what the source says, including the critique's exact numeric token where applicable>
PASSAGE: <where in the source the supporting language sits>
QUALIFIERS: "<limiting qualifier quoted from PASSAGE>" | "<next qualifier>"
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>; an n.d. reference: see [An undated source needs a reasoned excuse](../_shared/reference/sourcing.md#an-undated-source-needs-a-reasoned-excuse)
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled | unreadable - <reason>
TESTED-HEADING: <SHA-256 printed for this heading at refuter dispatch>
SECOND-ROUTE: <research route> -> <refutation route>
INSTRUMENTS: <first instrument> -> <second instrument>
STATED-EXPIRY: none stated | <ISO date> - <where the document states it> | <ISO date>, superseded cited deliberately - <reason>
REMARK: <problem outside the assigned question; repeat as needed>
```

When the passage has no limiting qualifiers, write `QUALIFIERS: none` instead of the list.

`INSTRUMENTS` is required for `REFUTATION: unreadable` and forbidden elsewhere. Transcribe only an
expiry the document states; do not infer one from a publication cadence.
For `refuted` records and clinician-supplied `unsourced` claims, apply the
[shared refuted-record disposition](../_shared/reference/sourcing.md#a-refuted-record-fails-the-citation-not-the-claim).

**A citation the critique leans on is opened, not recalled.** A guideline quoted against the
classmate is quoted from the page, and the record names the URL opened and the read date. Where the
claim is that the classmate's own source contradicts them, the refuting agent opens that source
independently and confirms the passage exists where the record says it does.

**A publisher's web rendering and its journal of record can disagree.** Where both exist, name which
one the critique cites and quote that one; do not attribute a web page's wording to the article.

After all records and refutations are gathered, this **Grader handoff** under
[standing rule 6](../../AGENTS.md) runs:

```bash
python tools/research_ledger.py scratch/runs/<run-key>/claims.md
```

Its exit must be 0 before a sourced claim is drafted. The grader's coverage boundaries are
inventoried in `research_ledger.DECLARED_LIMITS`; this skill points there without copying its rows.

## 4. Draft the critique

Before that first prose, write `voice-reads/<key-stem>/supplied-voice.json` by
[voice-read.md](../_shared/reference/voice-read.md) step 1: quote every image or reasoning ground the
clinician authored in this run's input, exclude faculty, classmate, and source language, or record
explicit `none`.

First write and confirm `project-context.md`, then retrieve every place owed by
[sourcing.md](../_shared/reference/sourcing.md).
Show the declared project's registered assets with the header being confirmed; a `none` run shows none.
Write the selected classmate's keyed declarations under `critique.md`, following that
reference's header rules. Compare descriptions of the classmate's work under
[Draft order](../_shared/reference/sourcing.md#draft-order).
The research return includes `QUALIFIERS`; the refutation brief checks its completeness
under that shared rule. The project-context command must exit 0. An
unregistered project stops for the clinician's answer; an unreachable place stops until it is
readable or the clinician confirms its waiver. A later direction amends and re-confirms the record
before prose resumes.

Immediately before drafting the first prose, run:

```bash
python tools/project_context.py scratch/runs/<run-key> --write --submission <submission-key>
python tools/voice_model_identity.py scratch/runs/<run-key> --write --submission <submission-key>
python tools/voice_model_scan.py
```

Use the terminal submission key: `critique.md`.
Use the [shared draft-order procedure](../_shared/reference/sourcing.md#draft-order)
for applying retrieved context while drafting, keyed staging, retained observations,
clinician waivers, and the pre-approval reading.
At the go-ahead, show any late gate and its waived-observation count.

Read only the canonical path the identity command reports.

Reuse a recorded image whole where it fits. Where none fits, follow
[imagery-proposals.md](../_shared/reference/imagery-proposals.md); only a new image from a recorded
domain may be proposed, and one that works never licenses a second instance.

Exit 0 is required to draft against the model. Exit 2 refuses drafting unless the banner explicitly
says the model is absent; only that limb opens
[voice.md](../_shared/reference/voice.md) §8's no-model rule, whose declaration is written to
`scratch/runs/<run-key>/voice-status.md`. Any other exit is repaired and rerun.

Open with the classmate's exact roster first name and a comma. Then write **every one of the eight
headings**, in the spec's order, each answering the sub-questions the spec states under it.

**Lead each heading with what is true before what is wrong.** Credit is not decoration here: a
critique that opens every section with a defect is one the reader stops reading, and the
rubric asks for constructive feedback in as many words. Where the classmate beat the clinician, say
which and say it without hedging.

**No stated maximum is honored.** The spec's range is a floor of 500 and an expectation of 750. Never
trim a drafted critique to fit the ceiling: the clauses a ceiling removes first are the ones that
bound a claim, because those are the clauses that read as optional. Where the critique runs long,
cut a whole point rather than the qualifiers on a point being kept, and tell the clinician the count
so the choice is his.

End with the bold Markdown label `**References**` and put each APA 7 entry in its own paragraph
separated by a blank line. [apa7.md](../_shared/reference/apa7.md) is the authority; a tertiary
database entry italicizes the database name and not the topic title, which is the form the corpus
most often gets wrong.

## 5. Independently grade

After the drafting context returns the critique, this **Grader handoff** under
[standing rule 6](../../AGENTS.md) runs:

```bash
python tools/peer_critique_scan.py scratch/runs/<run-key>
```

The default report is counts only; `--show` prints classmate names and finding detail, so its output
is private working material and must not be pasted. Exit 0 means every mechanical row passes, 1 means
a finding, and 2 means the run was not completely scannable.

It reads the roster from `posts/*.md`, then grades the rows below, every one of which is written out
here so a reader who cannot run the command walks the same checks:

| Row | A clean run means |
| --- | --- |
| `missing-heading` | every required heading appears in the critique |
| `empty-heading` | every required heading carries prose beneath it |
| `heading-order` | the headings appear in the order the spec lists them |
| `addressed-name` | the addressed first name is on the run roster |
| `word-floor` | the critique contains at least 500 words |
| `narrative-body` | the shared house-style body row is clean |
| `reference-minimum` | the critique carries at least 2 references |
| `unresolved-citation` | every in-text citation resolves to the critique's own list |
| `untraced-number` | every body numeral traces to a believed claim record |
| `missing-posted-reading` | the posted critique has been reread and recorded |
| `unknown-verdict` | every posted reading carries a recognized verdict |
| `bare-verdict` | every posted reading verdict carries substantive text |
| `submission-fingerprint` | the terminal posted-reading fingerprint matches `critique.md` |

The final-draft reading adds `missing-heading-read`, `duplicate-heading-read`,
`unread-heading-read`, `unknown-heading-read-route`,
`heading-read-sentence-count`, `heading-read-unknown-heading`, `heading-read-dropped-heading`,
`heading-read-draft-mismatch`, `heading-read-defect`, `heading-read-verdict-shape`
(a malformed verdict line), `heading-read-finding`,
`heading-read-context-digest`, `heading-read-context-verdict-shape`, and
`heading-read-context-defect`, plus `heading-read-qualifier-count`,
`heading-read-item-count`, and `heading-read-unopened-item` under the shared sourcing rule.

The word count excludes the reference list. The 750-word expectation is **reported and never
graded**, on the no-stated-maximum rule in step 4, and the count of literal ampersands is reported
for the reason in step 6.

If the command is unavailable, walk its named `narrative-body` row against the same body boundary
and [style.md](../_shared/reference/style.md); do not restate a second list rule in this skill.

Then run the reference list through the shared APA grader:

```bash
python tools/reference_scan.py scratch/runs/<run-key>/critique.md --as-of <the sitting's ISO date> --bold-references
```

Its exit must be 0. Walk `peer_critique_scan.NOT_REACHED` after a clean scan; it is the single
inventory of what the command cannot decide. **A clean scan is not a checked critique.** Whether the
missed diagnosis is really missed, whether an absent item was ever in the case, and whether the
tone is one the clinician will sign are all readings, and the clinician answers them.

After `critique.md` is final and before the go-ahead, run the **Planter** and separate fresh **Voice
reader** in [voice-read.md](../_shared/reference/voice-read.md). A real sentence placed on a generic
half returns the critique to its author, then both contexts rerun on a fresh plant. With no subagent
tool, write the two not-run records exactly as the shared sheet requires. The completion grader
enforces both the voice read and the model-owned profanity row. Its complete ceiling is
`voice_read.DECLARED_LIMITS`; this skill copies no row.

Before the go-ahead, this fresh **Second reader** under [standing rule 6](../../AGENTS.md) receives only `critique.md`, `claims.md`, the printed
heading digests, and every item pointer recorded in `project-context.md`. It opens those items
itself. Do not give it research sources. It writes the shared `## HEADING-READ: critique.md` record
from [sourcing.md](../_shared/reference/sourcing.md) to `<run-directory>/heading-read.md`. Repair
every `unrecorded` or `drifted` finding and repeat the read after any repair. The reader writes each
problem outside its assigned question on a `REMARK: <problem>` line, repeated for each remark,
and nowhere else in the record. With no second context, the read does not complete: write no record,
give no go-ahead, and submit no artifact. Rerun `peer_critique_scan.py`, which refuses a missing or stale
record before the go-ahead.

## 6. Show, then post to the peer-review comment

Show the clean critique to the clinician with the word count, the grader exits, and a short list of
what the critique credits the classmate for. Every approval ask, including one repeated after a revision,
shows the complete final text with its full reference list before the approval question. If the run proposed imagery, also show this table from
`imagery-proposals.json`:

| Proposed image | Recorded domain | Real behavior it spends | Approve this image? |
| --- | --- | --- | --- |
| `<exact image>` | `<domain>` | `<behavior>` | yes / no |

Ask whether the substance is right, whether the register is his, and, separately, whether each
proposed image is approved. Apply the record and draft changes in
[imagery-proposals.md](../_shared/reference/imagery-proposals.md) and rerun the grader. Only an
explicit content go-ahead authorizes loading.
Before each draft showing at the go-ahead, follow [Revisions](../_shared/reference/revisions.md) to retain the shown copy and include the computed change list after the first showing.
Apply [Reader remarks at the go-ahead](../_shared/reference/sourcing.md#reader-remarks-at-the-go-ahead) before each approval question: prepare the paired grade, show its numbered remarks with proposed outcomes and every coverage line verbatim, then pass `remark_outcomes=outcomes` with the whole reply.

Before asking for the go-ahead, run `python tools/project_context.py <run-directory>
--go-ahead critique.md`. Show its moved places and every added memory-index line. A moved item is
incomplete coverage the clinician may approve over; a finding stops approval. Approval repeats
and records the check; show any changed notice and renew approval if it differs from the notice
the clinician saw. Completion carries that result forward after recorded posting.
Set `clinician_reply` to the clinician's whole approval message, including any conditions.
Before posting, the posted-reading rows are not graded and the go-ahead grade is expected to
pass. Once the approval record carries an `agent` or `clinician` posting route, a missing or
failing reading is a finding; a reading without recorded posting is incomplete coverage.
Leave the historical runs filed in #1495 as they stand. When touching one that posted without
an approval record, report `stopped - posted before the approval recorder could record it (#1495)`.
At that go-ahead call `approval_record.approve(run, skill="peer-critique",
submission="critique.md", sources=(run / "critique.md",), grader_args=(str(run),),
content_approved=True, clinician_reply=clinician_reply, remark_outcomes=outcomes)`. Compare its `pregrade_report` with the report shown before the ask; incomplete coverage does not block, while a
finding refuses the record. From this record onward every reply touching the run ends with
`Run status: <run-key> — <awaiting posting|awaiting posted reading|awaiting AAR|complete|stopped -
reason>`. Several touched runs each receive their own keyed line, and no classmate name enters it.

**There are two artifacts on two surfaces.** The Reply goes on the board and is written and posted
by [discussion-reply](../discussion-reply/SKILL.md). The Peer critique goes in the peer-review
comment on the classmate's submission. Both carry references, and the critique is not also posted
to the board. Where a course assigns no peer review, this ruling names no surface; ask the clinician
where the Peer critique belongs before loading it anywhere.

Build `critique.txt` from `critique.md` with:

```bash
python tools/post_text.py <run-directory>/critique.md <run-directory>/critique.txt
```

A refusal stops loading. Keep a real `&` wherever APA 7 requires one. Load the build into the
peer-review comment and compare the textarea value with `critique.txt`. The peer-review comment
is not a Composer, so only the loaded-box stop in
[canvas-editor.md](../_shared/reference/canvas-editor.md) applies, not its Composer load routes.
Follow that stop, then record the **Posting go-ahead** with a second
`approval_record.approve(run, skill="peer-critique", submission="critique.md",
sources=(run / "critique.md",), grader_args=(str(run),), content_approved=True,
clinician_reply=clinician_reply, approval_kind="posting")` call. Use the clinician's whole reply.
On unchanged text this carries forward the content approval's reader-remark outcomes; the
remark-list and coverage-line windows retain the content approval display, and approved leave
proposals need no repeated naming. Show any changed project-context notice and renew approval
before the **Save** click. A changed draft needs a new content approval, shown in full, before
loading and taking the stop again. Save only after the Posting go-ahead is recorded.

This route implements [ADR 0204](../../docs/adr/0204-a-peer-critique-posts-to-the-peer-review-comment-and-its-ampersand-is-typed-literally.md)
and closes [#991](https://github.com/mshamblin5150-code/clinical-skills/issues/991). The 2026-09-12
Bluefield observation found the comment stored the literal character correctly while the legacy
peer-review submission page displayed the stored `&` as a visible `&amp;`.

**Nothing on the LMS is edited after it is posted.** A defect found in a posted artifact is recorded
and filed, not repaired in place.

## 7. Read the stored comment, record, and review

After the run posts, call `approval_record.record_agent_posting(run, skill="peer-critique",
submission="critique.md")`. If the clinician says he posted the approved critique himself, call
`approval_record.record_clinician_posting(...)` instead. That clinician-posting route skips the
run's final read of the loaded Peer-review comment textarea before Submit, so an error is found only
after Canvas stores it and must be recorded rather than repaired in place; the posted reading
remains required.
Then read Canvas's stored comment text and retain it exactly as
`critique-stored-comment-readback.txt`. Compare it with `critique.txt` character for character and
compare at minimum the ampersand count. A disagreement is a defect: record it and file it without
changing the posted comment. ADR 0204 classifies the legacy peer-review page's visible `&amp;`, when
present, as expected display behavior; it is not filed when the stored comment still matches.
This posted reading compares Canvas's stored comment text with the plain-text build.
Read the legacy page too and record what it displays; its dated `&amp;` behavior is expected and is
not filed again.

Append this record to the run's one `reread.md`:

```text
## REREAD: critique.md
POST-URL: <the reviewed submission's page>
POSTED: <the comment's posted timestamp>
READ: <ISO date of this reading>
SUBMISSION-SHA256: <SHA-256 of critique.md>
VERDICT: matches - <character comparison and source/stored ampersand counts>
LEGACY-DISPLAY: expected - <visible &amp; count> | differs - <what the page showed> | unreadable - <reason>
```

`POST-URL` names the reviewed submission's page because ADR 0204's dated observation exposed no
deep link for the comment itself.
Replace `matches` with `diverges` when the stored comment and plain-text build differ; both verdicts
require substantive text after the keyword. Rerun `peer_critique_scan.py` after writing the record;
its exit must now be 0. The grader requires `POSTED`, `READ`, the current fingerprint, and a
recognized verdict with substantive detail. It checks the `LEGACY-DISPLAY` keyword and reason,
while the display observation remains outside grading. An unreadable record exits 2.

Compute the fingerprint with `python tools/file_digest.py "<critique.md>"` and write it before `/AAR`
extracts the record; adding or changing the line afterwards makes that review stale because
`aar_scan` fingerprints the whole block. That posted
critique is one submission. Invoke `/AAR` with `critique.md` as the submission key, then
rerun `python tools/peer_critique_scan.py <run-directory> --submission critique.md`. The report must
include `the after-action review: clean`.

## Completion

Do not report completion until the terminal submission-keyed grader exits 0 and reports
`the after-action review: clean`. Report the posted addressee, the word count against the spec's
range, the pre-post and post-reading grader exits, the posted-reading verdict, and every place the
critique credited the classmate. Keep `board-<date>.md`, `spec-<date>.md`, `posts/`, `claims.md`,
`critique.md`, `critique.txt`, `critique-stored-comment-readback.txt`, and `reread.md`, plus
`voice-status.md` when present, together under the run key as the private provenance record. Remove
every temporary per-agent path after the independent checks; if cleanup fails, report the exact
remaining path.
