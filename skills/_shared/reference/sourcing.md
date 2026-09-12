# Sourcing

## A pointer is not a source

Derived material may carry a sentence in a graded artifact only when its primary material is
retained and gradeable against it, or when the primary material is resolvable and was independently
re-opened. This includes material recalled from a memory store, summary, index, or prior run.
Anything else is a pointer: it may direct a search and may not carry a sentence.

## A failed read is not a negative

A search that ran and found nothing reports the corpus it read and what it did not open. A search
that did not run is not a negative. When an instrument refuses the read, retry with a second
independent instrument. If that also fails, report the source as unreadable rather than reporting
that the sought material is absent.

## A sourceless record makes no claim about a source

An `unsourced` or `unreadable` record states its substantive search or failure on `STATUS` and
omits every field required of a sourced record: `SOURCE`, `REFERENCE`, `RESTATEMENT`, `RECENCY`,
`RESOLVED`, `PAGE-YEAR`, `REFUTATION`, `SECOND-ROUTE`, and `STATED-EXPIRY`. An unreadable record
retains `INSTRUMENTS`, whose two substantive halves name the distinct failed routes. A clean
sourceless record does not establish that a rejected source was named well enough to recheck.

A sourced claim record may certify a value only when both `REFUTATION` and `SECOND-ROUTE` carry
substance. If either is absent or empty, the record does not establish that the second agent's
refutation pass ran and cannot certify a value.
