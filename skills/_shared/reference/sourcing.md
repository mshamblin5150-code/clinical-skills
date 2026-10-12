# Sourcing

## A pointer is not a source

Derived material may carry a sentence in a graded artifact only when its primary material is
retained and gradeable against it, or when the primary material is resolvable and was independently
re-opened. This includes material recalled from a memory store, summary, index, or prior run.
Anything else is a pointer: it may direct a search and may not carry a sentence.

For all five coursework skills, research and refutation returns refer to the clinician's compilation
as his **Case research** or to the **Evidence store**, and never state who wrote, compiled, or supplied
a document unless their brief says so.

## Search the evidence store and guideline index first

For every research claim in the five coursework skills, first search the **Evidence store** with
`python tools/uptodate_store.py search "<query>"` and the guideline index with
`python tools/guidelines_search.py "<query>"`. Record the literal query and hit count for each,
including zero:

```text
SEARCHED-FIRST: store "<query>" -> <hits>; guidelines "<query>" -> <hits>
```

Where neither covers the claim, search the clinician's UpToDate account through the
[Authenticated route](#a-wall-counts-only-after-the-authenticated-route-is-tried), without asking.
Use his one signed-in Chrome one pull at a time. File each topic used as a supplement dump with
`uptodate_store.py ingest` before drafting, so later runs find it. Extend the same record:

```text
SEARCHED-FIRST: store "<query>" -> <hits>; guidelines "<query>" -> <hits>; account "<query>" -> <hits>; filed <dump id>
```

Outside sources follow those searches. An unavailable index or account is a failed read under
[A failed read is not a negative](#a-failed-read-is-not-a-negative); report the failed attempt
rather than writing a zero-hit search that never ran. A failed first-stop search records
`store "<query>" -> unreadable - <failure>` or `guidelines "<query>" -> unreadable - <failure>`
in its slot. That record remains a finding: restore retrieval and replace the failed slot with
the actual hit count before drafting. An account failure follows the failed-read route above.
`research_ledger.py` refuses a missing
`SEARCHED-FIRST` or either missing first-stop query and hit count. Its shape-check ceiling belongs
to `research_ledger.DECLARED_LIMITS`.

The orchestrating context pastes each research return's `REFERENCE` and `RESTATEMENT` exactly as
returned into the ledger. The refutation leg remains the backstop; no character comparison grades
this copying rule.

## A resolving locator is not verification

Verifying a locator means opening it and confirming that it is the work's own address. A successful
response status is not verification: a near-miss address and a login form can both return one. A
sourced claim record's `RESOLVED` field therefore names the address confirmed as the work's own,
never a bare status.

## The clinician's own unpublished work

`clinician's own work` is admitted only by the assignment's signed `SOURCE-CLASSES`.
No bar template includes it by default. Add it only when the clinician allows it for that
assignment, at signing or by amending and re-signing `bar.md` when he asks mid-run. His request
authorizes that re-signing; retain it with the bar. Where no bar exists, write one with `SIGNED`,
the assignment's permitted `SOURCE-CLASSES`, and `RECENCY-WINDOW-YEARS` before using the class.
A record outside the signed classes fails `unknown-source-class`; stop to ask the clinician.
Keep a full sourced claim record and independent refutation. Use APA's unpublished-manuscript
form in [apa7.md](apa7.md) §42. The ordinary recency window still applies: older work needs
`nothing newer` or `guideline in force` with a reason.

```text
RESOLVED: <absolute document path> | SHA256: <lowercase SHA-256 of the bytes read> - read <ISO date>
PAGE-YEAR: <year> - document statement: <where the document dates itself>
PAGE-YEAR: <year> - internal metadata last-modified: <Word core properties or PDF modification date>
PAGE-YEAR: <year> - clinician's answer: <recorded answer>
SECOND-ROUTE: <author's reading route> -> refuter opened <same absolute document path> | SHA256: <digest the refuter read>
```

Choose one `PAGE-YEAR` line, taking the first available source in the order shown. Never use the
file-system modified date. The refuter opens that exact path, hashes the bytes it read, and tests
the heading and restatement against the document. Its digest must agree with `RESOLVED`.
Every other class retains the URL-or-DOI locator. The ledger rehashes local bytes at grading;
an absent or changed file is shared unread remainder, exit 2, while a finding still wins.
The existing `unresolvable-locator` row also refuses a malformed local locator or a refuter path
or digest that differs; `page-year-form` refuses an own-work year without one of these sources.

## A record is read at the source's width

**QUALIFIERS** lists every limiting qualifier the `PASSAGE` carries: population, setting,
comparator, condition, eligibility, device, adjustment and tense; a requirement, a quantifier
and an exclusivity the passage states (for example "all three are required", "most", "only").
Quote each word for word,
using double-quoted strings separated by ` | `, or write `QUALIFIERS: none` when none exist.
Escape an embedded double quote with `\"`. An absent field never means `none`.
The researcher returns the field with the passage; the refuter checks the list is complete.
The heading and restatement retain every named qualifier. Matching ignores case and runs
of whitespace and otherwise keeps the exact words.

Ledgers dated on or after 2026-10-11 require this field on sourced, non-`DROPPED` records.
Earlier ledgers report the qualifier rows as `not graded` with the unread record count;
they are not backfilled. Sourceless and `DROPPED` records owe no qualifier field.

- **Every field is copied from the work as a reader sees it rendered.** A web title is the rendered
  page heading, never the browser tab text or a backing dataset's record. For the clinician's own
  unpublished work, use the ordered year sources above; for online works a year or date comes from
  visible text, never an HTML comment. An online reference entry is dated by the publisher's citation
  form or its last content revision, never by a link-only history row. `PAGE-YEAR` holds only the
  page's own year or says the page states none. A year in 1900–2099 opens the field; no second,
  different year in that range appears, except a locator after `p.`, `pp.` or `page`. A field saying
  the page states none carries no year. A redirect or login-wall claim records the final address
  observed. A book or report accession must open the work the entry names: a chapter does not verify
  a whole-book entry, and a report verifies only values it assessed.
- **A locator lets a refuter land on the sentence in one read.** `PASSAGE` names the paragraph by
  its own opening words, then its page, section or table, and quotes from the start of the supporting
  sentence with its qualifiers. A heading joining several outcomes gives a locator for each.
- **A record states what the source states, in its words and at its width.** `STATUS` and
  `RESTATEMENT` use the source's descriptors. A record adds no purpose link, equivalence or exception
  the page does not state. A heading keeps the population, comparator, setting, adjustment, device,
  eligibility and tense its passage carries; a recommendation is cited for its own population, in
  the source's words; a finding is credited to the body that made it, in the section where it sits.

## A failed read is not a negative

A search that ran and found nothing reports the corpus it read and what it did not open. A search
that did not run is not a negative. When an instrument refuses the read, retry with a second
independent instrument. If that also fails, report the source as unreadable rather than reporting
that the sought material is absent.

## A wall counts only after the Authenticated route is tried

The **Authenticated route** is the clinician's signed-in Chrome through
`mcp__claude-in-chrome__*`. The in-app Browser pane is not that route. A research agent must try it
before giving up on the sought source, choosing an open substitute, or writing `STATUS: unsourced`
because of a wall.

A refuter writes `paywalled` only when the source body remains inaccessible through the
Authenticated route; an anonymous or in-app login wall does not establish the disposition.
[ADR 0042](../../../docs/adr/0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
ruled the refuter's required attempt.

Where the route cannot be reached in the run, the attempt is a failed read: `STATUS: unreadable`
or `REFUTATION: unreadable`, with `INSTRUMENTS` naming the attempts. An unreachable route never
yields `paywalled` and never yields `STATUS: unsourced` on the ground of a wall.

## Authenticated VitalSource chapters use one reading standard

When a source is an authenticated VitalSource Bookshelf chapter, every browser agent reads and
follows [`vitalsource-chrome`](../../vitalsource-chrome/SKILL.md) before opening the book.
`vitalsource-chrome` steps 2 through 5 are the shared visible-page and complete-traversal standard.
Only Codex runs its compatibility patcher in `vitalsource-chrome` step 1. A personal installation and a prior successful session are
insufficient evidence that the current consumer path works.

## An absence-based refutation reads and quotes the passage

A refutation that reports a record's supporting language absent reads the record's `PASSAGE` and
quotes what the source says there. A string search may lead the refuter to that place; it never
settles the question. A return reporting the language absent without that quote is a defective
return, not a verdict. The orchestrator does not write it to the ledger and re-briefs the refutation
leg.

A claim record whose `PASSAGE` does not hold the supporting language receives `REFUTATION: refuted`.
Correcting `PASSAGE` or `RESTATEMENT` changes the claim record's evidence and requires a fresh
`REFUTATION` and `SECOND-ROUTE` before the record can certify a value.

The orchestrator writes a researcher's returned `RESTATEMENT` and `PASSAGE` into the ledger verbatim.
Wording the orchestrator adds is a change to the record's evidence and returns through refutation
before the record can certify a value.

## A refuted record fails the citation, not the claim

A `refuted` verdict fails the citation; it establishes nothing about whether the claim is true.
Give the claim exactly one fresh research round using a source other than the refuted one and
a fresh refuter. The claim comes out with a sound record or as `unsourced`. If that record also
fails, the claim is `unsourced`; apply its disposition rather than starting another round.
After its fresh round, rewrite the refuted record in place as the sound record the round produced,
or as an `unsourced` record whose search text names each source tried and why each failed,
including the refuted source and the refuter's reason. The claim's provenance stays in `claims.md`,
in the record later readers grade. `DROPPED` stays on a sourced record whose claim the draft no
longer makes. A cut `unsourced` claim carries no `DROPPED`.

When an `unsourced` claim would be cut, and it is a **Clinician-supplied claim**, ask the clinician
before cutting it and before the draft is final. Name each source tried and why it failed.
Ask whether the clinician will supply a source, rule that the claim stays, or agree to the cut.
A claim the run introduced is cut and reported to the clinician.

A claim is clinician-supplied by where it came from: an invoked source in the clinician's reasoning,
the brief or notes the clinician supplied, a paper the clinician already approved, or a domain
the canonical voice model records as the clinician's. State that provenance in the question;
an invoked-source marker alone does not define the population.
[ADR 0316](../../../docs/adr/0316-a-refuted-record-fails-the-citation-and-a-clinician-supplied-claim-is-asked-about-before-a-cut.md)
records the ruling.

## Invoked attributions

An **Invoked attribution** is a person, school, or work named in the canonical voice model's
stated principles or invoked sources. The test is where the name came from, whether it names a
philosopher, a school, a historical figure, or a fictional character. An attribution introduced
by the run's own research keeps the ordinary research-or-cut choice.

When deriving research questions, read those parts of the canonical model beside the planned
outline or deck and open the **Attribution library**, `scratch/attributions.md`, first.
`repo_root.attribution_library()` resolves it through the owning checkout, like the canonical model,
so a worktree reads the same file. If it is absent, research directly and create it when an entry
is ready. Put each attribution the piece is likely to use into the first research round as a
claim question. The heading read remains the backstop for an attribution the look-ahead missed.

The library is an **ungraded pointer**, saving the search rather than the check. Each paper
reopens the source, confirms the passage, and runs its own refutation; an entry never carries a
sentence. Keep one entry per attribution with:

- the name and idea or line as the clinician uses it;
- the source address and section;
- the APA reference and source class;
- the date last checked and the paper that checked it;
- any dated ruling of the clinician's.

Add or refresh an entry only after the paper's claim record passes `research_ledger.py` and
refutation. Record a clinician ruling when he gives it. Retain a ruling about the same line for
later papers so they do not ask it again; they still reopen and refute their own source.

An unrecorded invoked attribution receives a full researched and refuted record; it is never cut
unresearched or recast as the clinician's own principle to remove the name. If research fails,
apply the [refuted-record disposition](#a-refuted-record-fails-the-citation-not-the-claim): one
fresh round with a different source, then ask the clinician before any cut. If research succeeds
and shows the attribution itself is wrong, stop before the draft is final and show what was
attributed, what the sources say, and which sources say it. The clinician corrects it, supplies a
source, or keeps it as written; record his ruling in the library.

Use a reference work documenting the attribution first. The signed bar's source classes stay
unchanged. When none of its admitted classes can carry the attribution, ask whether to amend and
re-sign this paper's bar, supply a source, or drop the line; record the answer in the library.
[ADR 0329](../../../docs/adr/0329-an-invoked-attribution-is-researched-before-drafting-and-never-cut-or-changed-without-asking.md)
records the ruling.

## A sourceless record makes no claim about a source

An `unsourced` or `unreadable` record states its substantive search or failure on `STATUS` and
omits every field required of a sourced record: `SOURCE`, `REFERENCE`, `RESTATEMENT`, `PASSAGE`, `QUALIFIERS`, `RECENCY`,
`RESOLVED`, `PAGE-YEAR`, `REFUTATION`, `TESTED-HEADING`, `SECOND-ROUTE`, and `STATED-EXPIRY`. An unreadable record
retains `INSTRUMENTS`, whose two substantive halves name the distinct failed routes. A clean
sourceless record does not establish that a rejected source was named well enough to recheck.

A sourced claim record may certify a value only when `REFUTATION`, `TESTED-HEADING`, and
`SECOND-ROUTE` carry substance and `TESTED-HEADING` matches the current claim heading. If any is
absent, empty, malformed, or stale, the record cannot certify a value.

A claim record carrying `DROPPED` certifies no value. The field says the document no longer makes
the claim, so the record cannot support a figure the document still states.

## A claim heading is the claim the document will make

The heading is the claim the finished document will make, including any number the document will
state. Before research it states the question the research must answer. Recall may choose what to
look up but never supplies the heading's words. When the record returns, the orchestrator rewrites
the heading as the claim in the source's own words, carrying every limiting qualifier the `PASSAGE`
carries. Only the rewritten heading is refuted, has its `TESTED-HEADING` printed, is cited or is
drafted from. For a drug-dose heading, the question names the drug and indication, and the rewritten
claim states the dose. A heading the source does not support is corrected before drafting, or marked
`refuted` by the refuter.

### Refutation checks the heading and restatement at the source's width

A heading or restatement broader than its source is `refuted`. Broadening includes a dropped
qualifier on the subject, a wider population, an added exception, purpose link or equivalence, or a
stronger modality. A narrower claim `stands`. The refuter checks the restatement as well as the
heading. A proposed correction quotes the source's conditions; an adopted correction is a changed
heading that needs a fresh refutation.
The refuter checks `QUALIFIERS` against the complete supporting passage and returns any missing
limitation for correction before the heading is refuted again.

A heading changed after its refutation is a new claim. `TESTED-HEADING` is the lowercase SHA-256 of
the `## CLAIM:` heading text after runs of whitespace collapse to one space and the ends are
trimmed; case and punctuation remain significant. Before every refutation dispatch, the parent runs
`python tools/research_ledger.py <claims.md> --heading-digests`, copies the printed digest for that
heading into the refuter's brief, and writes it beside the returned `REFUTATION` and `SECOND-ROUTE`.
The command reads the file and never accepts heading text as an argument. A changed heading needs a
fresh refutation and a newly printed `TESTED-HEADING` before anything cites it or takes a number
from it.

## A heading read binds the final draft to the ledger

Before the first prose in a coursework run, write the purpose-named
`<run-directory>/project-context.md`. Its confirmed header declares either the project or `none`
with a reason. The account registry resolved by `repo_root.project_registry()` states one
`MEMORY-INDEX:` and each `PROJECT:` with its absolute `LOCATION:` paths and named `SERVICE:` MCP
servers. Never write a service URL. An unregistered project stops for the clinician's ruling.

```text
PROJECT-CONTEXT: <project> | none - <reason>
OWN-SUBMISSION: <path> | none - <reason>
CASE-MATERIAL: <path> | none - <reason>
CASE-RESEARCH: <dump id> | none - <reason>
CLASSMATE-POST: <submission key> -> <absolute path to the selected classmate's post>
CLASSMATE-BOARD: <submission key> -> <absolute path to the board snapshot>
CLASSMATE-ATTACHMENT: <submission key> -> <absolute path to a retained attachment copy> | <submission key> -> none - <reason>
PROJECT-SEARCH: <location or service> - "<terms>"
PROJECT-WAIVE: <location or service> - <what failed and when>; proceed without, per the clinician
CONFIRMED: <ISO date>

## PLACE: <owed location or service>
STATE: read | searched | unreadable | absent
ROOT: <absolute searched path root>
TERMS: <searched path terms>
EXAMINED: <nonnegative count>
UNREADABLE: <nonnegative count>
CORPUS-SIZE: <nonnegative service count>
QUERY: <terms> | THRESHOLD: <value> | LIMIT: <count> | HITS: <count>
DETAIL: <why an unreadable or absent place failed>
OPENED: <file path or service item identifier> | none
```

`OWN-SUBMISSION` declares the clinician's submission already handed in on the same board or
case, or `none` with a reason. The absolute file path holds the handed-in text or the run's
capture of the posted entry. Open it as an item in a `read` place; add its location through
`PROJECT-SEARCH` if needed. Confirm this line with the rest of the header. The gate refuses
a missing or duplicated line, reasonless `none`, or a path not opened in a read place.

`CASE-MATERIAL` declares the case-material file, or `none` with a reason. Open its absolute path
as an item of a `read` place, adding its location through `PROJECT-SEARCH` when needed.
`CASE-RESEARCH` declares the dump id of the clinician's case research in the Evidence store,
or `none` with a reason. File an existing compilation with `python tools/uptodate_store.py ingest`
before drafting; open the filed `source.txt` as an item of a `read` place. The declaration names the
dump, rather than the original Word file. Confirm both lines with the rest of the header in all
five coursework skills. The gate requires each line exactly once, refuses a reasonless `none` or
an unopened declared item, and refuses a research dump without a manifest or with a filed-copy
fingerprint that disagrees with its manifest. The go-ahead recheck covers both declared items,
including the research manifest and filed-copy identity.

In `discussion-reply` and `peer-critique`, confirm the three `CLASSMATE-` lines for each
submission key with the header. Declare exactly one post and board snapshot per key. Repeat
the attachment line for every file the selected classmate attached, or write one `none` with
a reason. Open every declared absolute path as an item of a `read` place, adding its location
through `PROJECT-SEARCH` when needed. The gate refuses missing or duplicated post or board
lines, missing attachments, reasonless `none`, `none` beside a path, and unopened paths for
the gated key. Another key's declarations cannot satisfy it. Both replies' lines are confirmed
before reply one's first prose; their board lines may name the same snapshot. Records confirmed
before 2026-10-11 report this check as `not graded` with a pre-cutoff record count.
A sentence stating what the classmate wrote, found, or planned is an **Item description** under
**Draft order**. Its `ITEM:` may name its own key's classmate files or other opened items;
naming a classmate file declared only under another submission key is a finding, on the
heading read's existing Item-description cutoff.
When `PROJECT-CONTEXT` is `none`, these declarations still owe their opened files: add
their read locations through `PROJECT-SEARCH`. No registered project places are owed in
that branch; file hashing and the go-ahead recheck apply to the declared retrieval.

The memory index and every registered project place are owed. Each `PROJECT-SEARCH` adds or
constrains one owed place; a direction given later amends and re-confirms the header before drafting.
Every owed place has exactly one entry. A searched path carries `ROOT`, `TERMS`, `EXAMINED`,
`UNREADABLE`, and `OPENED`; a searched service carries `CORPUS-SIZE`, one `QUERY` per query, and
opened identifiers only. `OPENED: none` records a bounded miss, never a settled negative.
`unreadable` or `absent` blocks unless the confirmed header waives that exact place.

Run `python tools/project_context.py <run-directory> --write --submission <submission-key>` after retrieval and before drafting.
When service items were opened, pass a `place -> item identifier -> returned text` JSON object on
standard input with `--service-payloads -`; the command hashes the returned text without storing it.
The command hashes opened file bytes, writes every item hash and a context digest binding the
`OWN-SUBMISSION`, `CASE-MATERIAL`, and `CASE-RESEARCH` header lines and sorted place/item/hash triples,
and exits 0 only when the gate passes. Exit 1 is a finding. Exit 2 means the owed population was not
established, including an unavailable registry or unregistered project. The completion grader
rehashes file items; drift is exit-2 coverage, while a finding still wins. It does not retrieve
service items again.

### Draft order

An **Item description** states what an item opened for `project-context.md` says, such as a
classmate's plan or a prior submission. Compare that sentence with the opened item claim by
claim while drafting and again before the heading reader writes `CONTEXT-VERDICT`.
An omission is `narrows` only when the omitted part bears on the sentence's point. Stating
something otherwise, dropping a qualifier the item carries, or asserting an absence the item
does not state is `contradicts`. Both are findings and block the go-ahead.

While drafting, every statement the draft makes about the clinician, his history, or his own
projects agrees with the opened project-context items: it neither narrows nor contradicts them.
Check each such sentence against those items as it is written, not after the draft is final.
Where opened items disagree with each other, stop before writing that sentence and ask the
clinician, naming both sources and what differs; his ruling lands as a memory write. The heading
read's context verdict re-checks this agreement and remains the backstop; nothing grades the
drafting-time check.

Read a document of the clinician's whole before writing any first-person factual sentence that
rests on it, rather than reading only matching lines. Its self-description is not evidence of
who wrote it, for whom, or what organization or program it covers. When a sentence states any of
those facts, ask the clinician separately whether he wrote the document and for which organization
or scope: ask one single question, wait for the answer, then ask the other. A compound question
that one "yes" could answer is not asked. Use his answers immediately; write the memory recording
the document's author and scope at the after-action review, not mid-draft, because a mid-run write
moves the gate-hashed memory index. Nothing grades the whole read or these questions; see
`project_context.DECLARED_LIMITS`, row `agreement-inherits-item-errors`.

Capture `voice-reads/<submission-key>/supplied-voice.json` before the gates. The identity gate
requires that file before writing its record. Use the terminal submission key for both commands;
when staging a coursework draft under standing rule 6, use that key as the pass folder's name.
The gates retain their first observation for each key across reruns. Keep their machine-written
observations when amending and re-confirming the project-context header; reruns refresh retrieval
and model identity without replacing the historical observation.

A draft present before the first gate is a finding even though the gate writes its record and
hashes. Stop for the clinician's ruling. If cleared, add a line to the confirmed header and rerun
with the same key:

```text
ORDER-WAIVE: <absolute draft path> - <what was drafted before the gate>; proceed, per the clinician
```

Each observed path needs its own matching waiver; a different path clears nothing. Before the
go-ahead, read `project_context.completion_gate(run, submission)` and
`voice_model_identity.completion_gate(run, submission)`. Present and unwaived blocks approval.
Show any late observation and its waiver to the clinician, including the waived-observation count
reported by both records' existing completion rows.

Before any go-ahead, a fresh context receives only the final draft, `claims.md`, and the headings
with digests printed by `research_ledger.py --heading-digests`, plus every item pointer recorded in
`project-context.md`. It opens those items itself; it is not given summaries. It pairs every factual sentence
with the first eight hex characters of the current heading digest and judges only whether the
sentence claims more than that heading. A paraphrase claiming no more is a match; an absent claim is
`unrecorded`, and a broader population or subject, changed number, added entity or condition, or
dropped limitation is `drifted`. A requirement, quantifier, or exclusivity the draft attributes to
the source is an added condition unless the heading itself states it, even when the record's
restatement does. The clinician's own reasoning and experience are counted but need
no claim-heading pair; they remain subject to the project-context verdict. Item descriptions form
a third sentence class, each with an `ITEM` line naming the opened item identifier exactly as
`project-context.md` records it. The reader opens and compares that item itself, claim by claim.
A sentence stating who wrote, compiled, or supplied a document agrees only when a confirmed
project-context header line, a memory entry, or the clinician's recorded answer states it, never on
the document's own contents; where none does, write `CONTEXT-VERDICT: contradicts` and name the sentence.
For every pair whose claim carries `QUALIFIERS`, the reader counts the named qualifiers retained
in the sentence as `qualifiers N of M`. The total equals the record's list length, including
`0 of 0` for `none`. A shortfall has a `FINDINGS: drifted - <same location>, <difference>` line;
that finding does not count as a second sentence. The count records coverage, not correctness.
This is a **Second reader** under [standing rule 6](../../../AGENTS.md). With no second context,
the read does not complete: write no record, give no go-ahead, and submit no artifact.
The reader writes each problem outside its assigned question on a `REMARK: <problem>` line,
repeated for each remark, and nowhere else in the record.

```text
## HEADING-READ: <draft file>
DRAFT: <SHA-256 of the draft's raw bytes>
ROUTE: separate context
SENTENCES: <n> factual, <n> clinician's own, <n> item
PAIR: <location> -> <first 8 hex of the heading digest> | qualifiers <n> of <total>
ITEM: <location> -> <opened item identifier>
CONTEXT-DIGEST: <the project-context digest when this read was taken>
CONTEXT-VERDICT: agrees
CONTEXT-VERDICT: none
CONTEXT-VERDICT: narrows - <location>, <what differs>
CONTEXT-VERDICT: contradicts - <location>, <what differs>
CONTEXT-VERDICT: sources-conflict - <source A> and <source B>, <what differs>
VERDICT: clean
VERDICT: defect - <substance>
FINDINGS: unrecorded - <location>, <what differs>
FINDINGS: drifted - <location>, <what differs>
REMARK: <problem outside the assigned question; repeat as needed>
```

Keep the digest from the read's sitting. `project_context` retains that context
under the run's `private/heading-contexts/`. A later grade compares the items it
held: edits, removals, or an added place or opened item break the read. Appended
memory-index lines preserve it under ADR 0328's line comparison. A posted item's
read is not rebound. ADR 0346 governs its frozen terminal grade, and
`completion_checks.DECLARED_LIMITS` owns the dated-check derivation boundary.

Choose exactly one `CONTEXT-VERDICT` line and one `VERDICT` line from these forms.
`VERDICT: clean` is legal only beside `CONTEXT-VERDICT: agrees`, or beside `none` on a legacy `none` run.
`agrees`, `none`, and `clean` take nothing after them. A `FINDINGS:` line appears once
per sentence that failed and never on a clean record. This differs from the `## RENDERED:`
record's `VERDICT: clean - <what was compared>` and from the practicum `## CHECK:` record,
where a clean record's `FINDINGS:` supplies its substance.

A clean record has one `PAIR` per factual sentence and one `ITEM` per item-description sentence.
The three-class sentence line is required for ledgers dated on or after 2026-10-11; earlier
ledgers report item comparisons as `not graded` with unread heading-read records. A pair owes
the qualifier suffix whenever its record carries the field, including on earlier ledgers.
Pairs plus findings at unpaired locations equal the factual count;
every prefix names a current, non-`DROPPED` heading; and `DRAFT` matches the final artifact. A
context digest names the retained project context from the read, and only `agrees` is
clean. Even a run declaring no project binds all three declaration reasons in that digest. `narrows`, `contradicts`, and
`sources-conflict` are findings; the last names both sources and only the clinician resolves it,
with that ruling written to memory. A finding blocks the go-ahead. Repair a drifted sentence toward the correct side: return it to its
heading, or change and refute the heading again. Give an unrecorded sentence a full researched and
refuted record or cut it, except an [invoked attribution](#invoked-attributions), which is
researched and follows that section's clinician-decision route. Every repair changes the draft, so a fresh heading read replaces the old
one before the go-ahead.

The `none` context verdict is retained for legacy records whose context digest is `none`;
both fields must be `none` there. New runs use the bound digest and the `agrees` verdict.


## Reader remarks at the go-ahead

Refutation records use the same outside-problem line:

```text
REFUTATION: <the assigned verdict and its reason>
TESTED-HEADING: <the current claim-heading SHA-256>
REMARK: <problem outside the refutation question; repeat as needed>
```

Every coursework reader's verdict answers only its assigned question. Put a problem noticed
outside that question on its own `REMARK: <problem>` line, repeated for each remark, and nowhere
else. A remark preserves the verdict. This also applies to refutation records and visual reads.
The voice reader writes a `remarks` list of nonempty strings in `voice-read.json`, empty when
there are none. Retain remarks when replacing a record after a repair so they still reach the
go-ahead. A skipped, unrecognized line inside a bound reader record counts as unread; folded
prose and substance-only reasons have the declared limits in their reader modules.

Before asking for approval, call `approval_record.prepare` with the same `run`, `skill`,
`submission`, `sources`, and `grader_args` that the approval call will receive. For
`course-assignment`, call `assignment_submission.prepare(run, artifact)` instead. A finding
stops the ask. The returned `Prepared` holds the paired grader report, remarks, and coverage
lines. Read the report; give each remark a `reader_remarks.Outcome("fixed", "<what changed>")`
or `reader_remarks.Outcome("leave", "<proposal and reason>")`, in returned order. Show
`reader_remarks.surface(prepared, outcomes)` in the chat before the question: it numbers every
remark with its outcome and prints every coverage qualifier word for word. Coverage lines are
shown for reading and carry no waiver. The complete draft and references still follow their
skill's existing approval rule.

Pass the same tuple as `remark_outcomes=outcomes` to `approve` or `stage`, along with the whole
`clinician_reply`. Approval accepts the fixes; leaving one needs the clinician's explicit word
by number (such as "leave 2") or covering all remarks (such as "leave all of them"). A bare
"go", "fire", or "send it" accepts fixed outcomes but leaves leave proposals unanswered.
The refusal names the open numbers. The transcript check requires the numbered list and exact
coverage lines after preparation and the last artifact change, before the reply. Any changed
artifact or grader report requires preparation and a new ask. The durable approval keeps each
remark and its accepted outcome. `reader_remarks.DECLARED_LIMITS` owns this gate's ceiling.
[ADR 0330](../../../docs/adr/0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md)
is the authority.
