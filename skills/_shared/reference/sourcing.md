# Sourcing

## A pointer is not a source

Derived material may carry a sentence in a graded artifact only when its primary material is
retained and gradeable against it, or when the primary material is resolvable and was independently
re-opened. This includes material recalled from a memory store, summary, index, or prior run.
Anything else is a pointer: it may direct a search and may not carry a sentence.

## A resolving locator is not verification

Verifying a locator means opening it and confirming that it is the work's own address. A successful
response status is not verification: a near-miss address and a login form can both return one. A
sourced claim record's `RESOLVED` field therefore names the address confirmed as the work's own,
never a bare status.

## A record is read at the source's width

- **Every field is copied from the work as a reader sees it rendered.** A web title is the rendered
  page heading, never the browser tab text or a backing dataset's record. A year or date comes from
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
Correcting `PASSAGE` changes the claim record's evidence and requires a fresh `REFUTATION` and
`SECOND-ROUTE` before the record can certify a value.

## A refuted record fails the citation, not the claim

A `refuted` verdict fails the citation; it establishes nothing about whether the claim is true.
Give the claim exactly one fresh research round using a source other than the refuted one and
a fresh refuter. The claim comes out with a sound record or as `unsourced`. If that record also
fails, the claim is `unsourced`; apply its disposition rather than starting another round.
The refuted record itself certifies no value and is never cited.

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

## A sourceless record makes no claim about a source

An `unsourced` or `unreadable` record states its substantive search or failure on `STATUS` and
omits every field required of a sourced record: `SOURCE`, `REFERENCE`, `RESTATEMENT`, `PASSAGE`, `RECENCY`,
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

The memory index and every registered project place are owed. Each `PROJECT-SEARCH` adds or
constrains one owed place; a direction given later amends and re-confirms the header before drafting.
Every owed place has exactly one entry. A searched path carries `ROOT`, `TERMS`, `EXAMINED`,
`UNREADABLE`, and `OPENED`; a searched service carries `CORPUS-SIZE`, one `QUERY` per query, and
opened identifiers only. `OPENED: none` records a bounded miss, never a settled negative.
`unreadable` or `absent` blocks unless the confirmed header waives that exact place.

Run `python tools/project_context.py <run-directory> --write --submission <submission-key>` after retrieval and before drafting.
When service items were opened, pass a `place -> item identifier -> returned text` JSON object on
standard input with `--service-payloads -`; the command hashes the returned text without storing it.
The command hashes opened file bytes, writes every item hash and the sorted-triple context digest,
and exits 0 only when the gate passes. Exit 1 is a finding. Exit 2 means the owed population was not
established, including an unavailable registry or unregistered project. The completion grader
rehashes file items; drift is exit-2 coverage, while a finding still wins. It does not retrieve
service items again.

### Draft order

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
dropped limitation is `drifted`. The clinician's own reasoning and experience are counted but need
no claim-heading pair; they remain subject to the project-context verdict. A harness without a second context performs the same written walk and records `ROUTE:
orchestrator walk`.

```text
## HEADING-READ: <draft file>
DRAFT: <SHA-256 of the draft's raw bytes>
ROUTE: separate context | orchestrator walk
SENTENCES: <n> factual, <n> clinician's own
PAIR: <location> -> <first 8 hex of the heading digest>
CONTEXT-DIGEST: <the project-context record's digest> | none
CONTEXT-VERDICT: agrees
CONTEXT-VERDICT: none
CONTEXT-VERDICT: narrows - <location>, <what differs>
CONTEXT-VERDICT: contradicts - <location>, <what differs>
CONTEXT-VERDICT: sources-conflict - <source A> and <source B>, <what differs>
VERDICT: clean
VERDICT: defect - <substance>
FINDINGS: unrecorded - <location>, <what differs>
FINDINGS: drifted - <location>, <what differs>
```

Choose exactly one `CONTEXT-VERDICT` line and one `VERDICT` line from these forms.
`agrees`, `none`, and `clean` take nothing after them. A `FINDINGS:` line appears once
per sentence that failed and never on a clean record. This differs from the `## RENDERED:`
record's `VERDICT: clean - <what was compared>` and from the practicum `## CHECK:` record,
where a clean record's `FINDINGS:` supplies its substance.

A clean record has one `PAIR` per factual sentence. Pairs plus findings equal the factual count;
every prefix names a current, non-`DROPPED` heading; and `DRAFT` matches the final artifact. A
non-`none` context digest matches the machine-written project-context digest and only `agrees` is
clean. On a `none` run both context fields are `none`. `narrows`, `contradicts`, and
`sources-conflict` are findings; the last names both sources and only the clinician resolves it,
with that ruling written to memory. A finding blocks the go-ahead. Repair a drifted sentence toward the correct side: return it to its
heading, or change and refute the heading again. Give an unrecorded sentence a full researched and
refuted record or cut it. Every repair changes the draft, so a fresh heading read replaces the old
one before the go-ahead.
