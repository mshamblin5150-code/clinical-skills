# A topic is swept on what the guideline states, and the sweep records its own coverage

Issue [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)
used *has decision points* without defining how that conclusion is reached. The
clinician ruled the term and the sweep on 2026-08-22.

1. **A topic has a decision point when the guideline states a number that changes
   what is done to a patient** — a dose, a period, a cutoff, or a target. The test is
   read from the guideline, never inferred from a catalog or recommendation index.
2. **The document is the population and a recommendation record is only an index into
   it.** A sweep names what it read and what it did not read; an extractor's matches
   cannot establish that the rest of the document says nothing.
3. **The sweep records its denominator.**
   [`reference/thresholds/coverage.md`](../../reference/thresholds/coverage.md) has one
   row for every distinct topic derived from
   [`reference/guidelines-catalog.md`](../../reference/guidelines-catalog.md). Each row
   is in state `sheet`, `none`, or `unread`, and the registry auditor re-derives both
   the population and the state counts. A separate optional artifact column can name
   partial work; an artifact does not change an `unread` topic's state.
4. **A method-dependent value names the method in its quantity key.** Quantity keys
   are declared under `## Quantities` on the same terms that population keys are
   declared under `## Populations`. This represents alternatives without pretending
   the method is a patient population or a disagreement.
5. **A topic whose only records are `bound` remains `unread` while #436 is open.** A
   fixed marker window that can end before the decision point is not a document read.

## Why the USPSTF table is not the sweep

`reference/guidelines-uspstf.md` remains the recommendation artifact for the federal
documents, but it does not decide whether a topic needs a threshold sheet. Its columns
cannot represent every kind of decision point: the aspirin recommendation for
preeclampsia states a dose and start week, while the table has no dose column; the
cervical-cancer recommendation states modality-dependent intervals. Society and
recommendation grade therefore do not sort topics into sheet and no-sheet groups. The
guideline does.

**Extended by issue [#432](https://github.com/mshamblin5150-code/clinical-skills/issues/432)
on 2026-08-22:** the recommendation artifact's `interval` cell now carries every
distinct period its statement sentence names, in source order. The modality that
distinguishes those alternatives remains in the paired statement. This reopens only the
earlier single-value representation. The artifact remains an index rather than the topic
sweep: it still has no general decision-point schema, and its recommendation rows cannot
establish what the rest of a document does not state.

## Why `none` and `unread` are separate

An empty sheet is refused. It would make silence look like a clinical negative finding
and would weaken [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85)'s
rule that a missing row means `sheet does not settle it`. The registry records two
different reasons for an absent sheet instead:

- `none`: the named source documents were read and state no decision point;
- `unread`: the source documents have not been read completely enough to decide.

That distinction preserves `sheet does not settle it`. A missing row inside a sheet
still makes no claim about the guideline, and an `unread` registry row establishes
nothing.

## Order and accepted cost

Cervical cancer moves the format first because it exposes the method-dependent quantity
case. Exact multi-document topics follow so `CONFLICT` and per-source `COVERAGE` run
before single-source work can hide defects in those gates. Remaining exact topics follow,
then sources with no recommendation record. Bound-only topics wait on #436.

The registry is an additional maintained artifact, and `none` is a substantive reading
that a later source revision can invalidate. The auditor therefore derives its topic
column from the catalog, requires every disposition to carry a record, and refuses a
sheet that is absent from the artifact column or a `sheet` row with no artifact.

## Rejected

- **Exclude USPSTF.** A screening grade is not itself a threshold, but a USPSTF
  recommendation can state a dose, start week, cutoff, or modality-dependent interval.
- **Classify from recommendation records.** They are an index and can omit decision
  points elsewhere in a document; `bound` records can also end before the number.
- **Commit an empty sheet for a topic with none.** Directory silence would become
  indistinguishable from a clinical negative finding.
- **Put screening method in `population`.** Method does not describe the patient and
  would corrupt the key the applicability and conflict rules depend on.
- **Treat alternatives as conflicts.** Different methods can support different correct
  values for the same patients without disagreeing.
