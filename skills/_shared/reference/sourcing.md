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

## A failed read is not a negative

A search that ran and found nothing reports the corpus it read and what it did not open. A search
that did not run is not a negative. When an instrument refuses the read, retry with a second
independent instrument. If that also fails, report the source as unreadable rather than reporting
that the sought material is absent.

## An absence-based refutation reads and quotes the passage

A refutation that reports a record's supporting language absent reads the record's `PASSAGE` and
quotes what the source says there. A string search may lead the refuter to that place; it never
settles the question. A return reporting the language absent without that quote is a defective
return, not a verdict. The orchestrator does not write it to the ledger and re-briefs the refutation
leg.

A claim record whose `PASSAGE` does not hold the supporting language receives `REFUTATION: refuted`.
Correcting `PASSAGE` changes the claim record's evidence and requires a fresh `REFUTATION` and
`SECOND-ROUTE` before the record can certify a value.

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
state. Before research it is a working statement. A heading the source does not support is corrected
before drafting, or marked `refuted` by the refuter.

A heading changed after its refutation is a new claim. `TESTED-HEADING` is the lowercase SHA-256 of
the `## CLAIM:` heading text after runs of whitespace collapse to one space and the ends are
trimmed; case and punctuation remain significant. Before every refutation dispatch, the parent runs
`python tools/research_ledger.py <claims.md> --heading-digests`, copies the printed digest for that
heading into the refuter's brief, and writes it beside the returned `REFUTATION` and `SECOND-ROUTE`.
The command reads the file and never accepts heading text as an argument. A changed heading needs a
fresh refutation and a newly printed `TESTED-HEADING` before anything cites it or takes a number
from it.

## A heading read binds the final draft to the ledger

Before any go-ahead, a fresh context receives only the final draft, `claims.md`, and the headings
with digests printed by the command above. It is not given sources. It pairs every factual sentence
with the first eight hex characters of the current heading digest and judges only whether the
sentence claims more than that heading. A paraphrase claiming no more is a match; an absent claim is
`unrecorded`, and a broader population or subject, changed number, added entity or condition, or
dropped limitation is `drifted`. The clinician's own reasoning and experience are counted but need
no pair. A harness without a second context performs the same written walk and records `ROUTE:
orchestrator walk`.

```text
## HEADING-READ: <draft file>
DRAFT: <SHA-256 of the draft's raw bytes>
ROUTE: separate context | orchestrator walk
SENTENCES: <n> factual, <n> clinician's own
PAIR: <location> -> <first 8 hex of the heading digest>
VERDICT: clean | defect - <substance>
FINDINGS: unrecorded | drifted - <location>, <what differs>
```

A clean record has one `PAIR` per factual sentence. Pairs plus findings equal the factual count;
every prefix names a current, non-`DROPPED` heading; and `DRAFT` matches the final artifact. A
finding blocks the go-ahead. Repair a drifted sentence toward the correct side: return it to its
heading, or change and refute the heading again. Give an unrecorded sentence a full researched and
refuted record or cut it. Every repair changes the draft, so a fresh heading read replaces the old
one before the go-ahead.
