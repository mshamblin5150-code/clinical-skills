# Threshold-sheet subject ledger

<!-- schema: threshold-subjects/1 -->

This is the committed evidence ledger for clinical-subject groups authored in
[`coverage.md`](coverage.md)'s `subject` column. A `?` there is unruled and has no
record here. A subject with more than one member has exactly one record in this
shape:

```markdown
## SUBJECT: <the elected catalog topic>
DATE: <YYYY-MM-DD>
ELECTED: <the same catalog topic>
ELECTION: <why this member name was elected>
REFUTATION: <what the independent agent tried and found>

### MEMBERS
- <catalog topic>
- <catalog topic>

### EVIDENCE
- <catalog topic>: <the evidence from this member's guideline>
- <catalog topic>: <the evidence from this member's guideline>
```

Membership is not transitive. One catalog topic may appear in several records,
which represents overlapping maximal cliques rather than a connected component.

No subject records have been authored. Every registry subject is currently `?`.
