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
`RESOLVED`, `PAGE-YEAR`, `REFUTATION`, `SECOND-ROUTE`, and `STATED-EXPIRY`. An unreadable record
retains `INSTRUMENTS`, whose two substantive halves name the distinct failed routes. A clean
sourceless record does not establish that a rejected source was named well enough to recheck.

A sourced claim record may certify a value only when both `REFUTATION` and `SECOND-ROUTE` carry
substance. If either is absent or empty, the record does not establish that the second agent's
refutation pass ran and cannot certify a value.

## A claim heading is the claim the document will make

The heading is the claim the finished document will make, including any number the document will
state. Before research it is a working statement. A heading the source does not support is corrected
before drafting, or marked `refuted` by the refuter.

A heading changed after its refutation is a new claim. It needs a fresh `REFUTATION` and
`SECOND-ROUTE` before anything cites it or takes a number from it.
