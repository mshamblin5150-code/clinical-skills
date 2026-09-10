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
    posts/
    claims.md
    critique.md
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

Parallel readers or researchers each receive a new run-unique private path. They return findings to
the orchestrating context and never append to `board-<date>.md`, `spec-<date>.md`, `claims.md`,
`reread.md`, or `critique.md`. The orchestrator is the sole writer of those artifacts, including
`voice-status.md`. Apply standing rule 6's independent-checker and cleanup sequence to the temporary
per-agent paths.

## 1. Read the spec, the classmate, and the clinician's own post

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

**The clinician's own post is a comparison, not a standard.** Where the classmate did something
better, that goes in the critique and it goes in early. Where the clinician's own post shares a gap,
say so rather than charging it to the classmate alone.

## 2. Find what is clinically at stake before writing anything

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

Create `claims.md` with a `DATE:` header and one `## CLAIM:` heading per claim before research
begins. Fan out one research agent per claim, then send every sourced record to a **different**
agent briefed to refute it. Every research and refutation brief first reads
[sourcing.md](../_shared/reference/sourcing.md) and applies it to every returned claim or negative.
The orchestrator alone writes the records.

Each record uses the full research-ledger shape:

```text
## CLAIM: <the claim, including any number the critique will state>
STATUS: sourced | unsourced | unreadable - <what was searched or what prevented the read>
SOURCE: society guideline | peer-reviewed | government | tertiary reference
REFERENCE: <full APA 7 entry>
RESTATEMENT: <what the source says, including the critique's exact numeric token where applicable>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled | unreadable - <reason>
SECOND-ROUTE: <research route> -> <refutation route>
INSTRUMENTS: <first instrument> -> <second instrument>
STATED-EXPIRY: none stated | <ISO date> - <where the document states it> | <ISO date>, superseded cited deliberately - <reason>
```

`INSTRUMENTS` is required for `REFUTATION: unreadable` and forbidden elsewhere. Transcribe only an
expiry the document states; do not infer one from a publication cadence.

If the profile records the **Authenticated route** as available, a research agent must attempt it
before giving up on the sought source, choosing an open substitute, or returning
`STATUS: unsourced` because of the wall.

**A citation the critique leans on is opened, not recalled.** A guideline quoted against the
classmate is quoted from the page, and the record names the URL opened and the read date. Where the
claim is that the classmate's own source contradicts them, the refuting agent opens that source
independently and confirms the passage exists where the record says it does.

**A publisher's web rendering and its journal of record can disagree.** Where both exist, name which
one the critique cites and quote that one; do not attribute a web page's wording to the article.

After all records and refutations are gathered, a fresh non-authoring context runs:

```bash
python tools/research_ledger.py scratch/runs/<run-key>/claims.md
```

Its exit must be 0 before a sourced claim is drafted. The grader's coverage boundaries are
inventoried in `research_ledger.DECLARED_LIMITS`; this skill points there without copying its rows.

## 4. Draft the critique

Read `scratch/voice-model.md`. Before drafting, run:

```bash
python tools/voice_model_scan.py
```

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

After the drafting context returns the critique, a fresh non-authoring context runs:

```bash
python tools/peer_critique_scan.py scratch/runs/<run-key>
```

The default report is counts only; `--show` prints classmate names and finding detail, so its output
is private working material and must not be pasted. Exit 0 means every mechanical row passes, 1 means
a finding, and 2 means the run was not completely scannable.

It reads the roster from `posts/*.md`, then grades eleven rows, every one of which is written out
here so a reader who cannot run the command walks the same checks:

| Row | A clean run means |
| --- | --- |
| `missing-heading` | every required heading appears in the critique |
| `empty-heading` | every required heading carries prose beneath it |
| `heading-order` | the headings appear in the order the spec lists them |
| `addressed-name` | the addressed first name is on the run roster |
| `word-floor` | the critique contains at least 500 words |
| `reference-minimum` | the critique carries at least 2 references |
| `unresolved-citation` | every in-text citation resolves to the critique's own list |
| `untraced-number` | every body numeral traces to a believed claim record |
| `missing-posted-reading` | the posted critique has been reread and recorded |
| `unknown-verdict` | every posted reading carries a recognized verdict |
| `bare-verdict` | every posted reading verdict carries substantive text |

The word count excludes the reference list. The 750-word expectation is **reported and never
graded**, on the no-stated-maximum rule in step 4, and the count of literal ampersands is reported
for the reason in step 6.

Then run the reference list through the shared APA grader:

```bash
python tools/reference_scan.py scratch/runs/<run-key>/critique.md --as-of <the sitting's ISO date>
```

Its exit must be 0. Walk `peer_critique_scan.NOT_REACHED` after a clean scan; it is the single
inventory of what the command cannot decide. **A clean scan is not a checked critique.** Whether the
missed diagnosis is really missed, whether an absent item was ever in the case, and whether the
tone is one the clinician will sign are all readings, and the clinician answers them.

## 6. Show, then post to both surfaces

Show the clean critique to the clinician with the word count, the grader exits, and a short list of
what the critique credits the classmate for. Ask whether the substance is right and whether the
register is his. Only an explicit go-ahead authorizes posting.

**There are two surfaces and they are not the same artifact.** The spec calls the critique a
discussion board reply, so **the board is the graded surface**. Where the LMS has also assigned a
peer review, its comment box is bookkeeping that must carry at least one comment before the review
registers as finished.

**Both surfaces can damage what is typed into them, and neither is cleared.** The submission comment
box renders a literal `&` as a visible `&amp;`, which lands in the APA reference list, where the
ampersand is mandatory; that is
[#991](https://github.com/mshamblin5150-code/clinical-skills/issues/991) and its remedy is unsettled.
Whether the board's reply box shares the defect is unmeasured, which is
[#948](https://github.com/mshamblin5150-code/clinical-skills/issues/948)'s open question. The
escaping `tools/post_html.py` applies governs an initial post's raw HTML editor, not a reply box.
Until #991 is ruled, ask the clinician which surface carries the reference list rather than choosing
one. On whichever surfaces are used, re-read the exact content in the box immediately before
posting, then read the rendered DOM after posting, and report every damaged character.

**Nothing on the LMS is edited after it is posted.** A defect found in a posted artifact is recorded
and filed, not repaired in place.

## 7. Reread, record, and review

Reread the posted version and append this record to the run's one `reread.md`:

```text
## REREAD: critique.md
POST-URL: <the posted critique's own deep link>
POSTED: <the board's posted timestamp>
READ: <ISO date of this reading>
VERDICT: matches - <what the reading found>
```

Replace `matches` with `diverges` when the board and artifact differ; both verdicts require
substantive text after the keyword. Record a divergence without changing the already graded
artifact. Rerun `peer_critique_scan.py` after writing the record; its exit must now be 0.

That posted critique is one submission. Invoke `/AAR` with `critique.md` as the submission key, then
rerun `python tools/peer_critique_scan.py <run-directory> --submission critique.md`. The report must
include `the after-action review: clean`.

## Completion

Do not report completion until the terminal submission-keyed grader exits 0 and reports
`the after-action review: clean`. Report the posted addressee, the word count against the spec's
range, the pre-post and post-reading grader exits, the posted-reading verdict, and every place the
critique credited the classmate. Keep `board-<date>.md`, `spec-<date>.md`, `posts/`, `claims.md`,
`critique.md`, and `reread.md`, plus `voice-status.md` when present, together under the run key as
the private provenance record. Remove every temporary per-agent path after the independent checks;
if cleanup fails, report the exact remaining path.
