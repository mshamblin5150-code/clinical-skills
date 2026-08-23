# A section read is the unit and a sheet's page coverage is what the state asserts

[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md) settled how a topic is swept and what [`reference/thresholds/coverage.md`](../../reference/thresholds/coverage.md) records. [ADR 0017](0017-a-run-joins-a-threshold-sheet-on-the-artifact-column-and-the-state-describes-the-read-behind-it.md) settled the consumer, and closed by saying that **completing a sheet is a separate decision** — a clinical read rather than a code change.

[#471](https://github.com/mshamblin5150-code/clinical-skills/issues/471) is that decision. Four sheets ship as partial artifacts under `unread`, and the ticket asked who reads them, in what order, and on how many tickets.

Grilled on 2026-08-23. The clinician ruled every point below on the same day.

## What is ruled

1. **The unit of work is one section of a source document, never a whole-document promotion.** A section read's deliverable is the rows that section holds plus a narrowed unread list. The row's `state` moves to `sheet` only when the last span falls, and is bookkeeping rather than the deliverable.
2. **An agent performs the read. The two halves of it are discharged differently.** Rows added ride the citation gates that already exist. A span retired **having found nothing** takes a blind independent second read of that named span, and a disagreement in that direction refuses.
3. **A section is a named span with a page range, and the union of read and unread ranges must cover every page of the source.** The denominator is `page_count` from [`reference/guidelines-catalog.md`](../../reference/guidelines-catalog.md), derived by a different instrument than the span list. Overlap between ranges is permitted; the check is coverage, never partition.
4. **The span list is a required table inside `## Scope`, and the sheet schema moves to `threshold-sheet/2`.** The existing `Read:` and `Not read:` prose limbs stay as the human summary and keep their grader rule; the table carries the arithmetic.
5. **ADR 0009 point 5 no longer blocks `diabetes.md`.** Its reason names an instrument this record replaces. #436 continues to own that sheet's `## Coverage` recommendation accounting, which is marked in the sheet and is not what the state asserts.
6. **The mechanism and the readings are separate tickets.** #471 becomes the parent of one reading ticket per sheet, each blocked on one mechanism ticket, in ADR 0009's order. Hypertension does not wait.
7. **A second read's record names what it was briefed on**, and a span retired on a null carries a dated marker in the sheet itself. A span retired with no rows and no marker is refused.
8. **The registry auditor checks the state against the artifact's page arithmetic, in both directions.** A `sheet` row whose artifact still lists an unread span is refused, and so is a non-`sheet` row whose artifact shows every page read.
9. **A reference list may be retired by class, and nothing else may.** The exemption is written in the table with its reason, so a sheet that reached `sheet` with spans exempted says so on its face.
10. **A reading ticket may retire spans that hold nothing before [#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464) lands, and may not record a narrative row until it does.** The three exact-source sheets are sequenced behind that ticket for their positive half only. ADR 0009's order is unchanged.

## The premise #471 was filed on does not hold

#471 calls the two USPSTF sheets *the cheap pair* and says each is *blocked on reading effort only*. That is false, and the grilling found it in the tracker rather than in the ticket.

[#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464) establishes that an `exact` source cannot carry a decision point stated in narrative without a fabricated `rec` identifier, and enumerates the four escapes that do not work: an invented identifier is refused by the exact record, attaching the value to a real identifier falsely claims it came from that recommendation, `RENDERED:` does not make the identifier true, and scoping it out leaves the topic unpromotable. Its worked case is a USPSTF recommendation statement whose *Practice Considerations* defines an ever smoker as 100 or more cigarettes, which decides whether grade B or grade C applies.

Three of the four sheets are exact-source — cervical cancer, both prediabetes statements, and AHA/ACC 2025. Only `diabetes.md` is `bound`. **And the span this record used as its own worked example of a valuable read — USPSTF's clinical considerations — is precisely the narrative location #464 says the format cannot represent.**

None of points 1 through 9 depends on that. What moves is only sequencing, which is point 10. The half of a section read that #464 blocks is the half that already carries evidence; the half it does not block is the null retirement, which is the half with none and the half point 2's second read exists for. So the mechanism is exercised on live work rather than on a fixture while #464 is settled.

Reordering to put the 377-page `bound` source first was rejected: it routes around a blocker rather than settling it, and #464 carries the `grilling` label, so it needs a ruling and not merely a build.

## What was measured before anything was ruled

**Nothing reads the `state` word.** After ADR 0017 the consumer joins on the `artifact` column. `tools/threshold_coverage.py` reads `state` only to count it and to refuse a `sheet` row with no artifact. So promoting a row changes the registry's own count line and nothing a run consumes — the rows are what a run consumes, and they are consumed today.

**The grader requires a `Not read:` limb.** `tools/threshold_sheet.py:784` refuses a sheet whose `## Scope` never says what was not read. A sheet promoted to `sheet` must still write one, saying nothing is unread. Under the old arrangement that sentence was unbacked, so the honesty clause went vacuous on exactly the sheets claiming completeness.

**The independence instrument cannot reach an unread section.** `brief()` builds its work order from `cited_citations(sheet)` — the pages a row already names. `gate_second_read` is row-driven and citation-keyed throughout. An empty `values: []` record parses, produces zero pairings, and reports every row as *uncovered*: a floor, not a refusal. With zero values it names zero documents, so a null record for one span is byte-identical to a null record for any other and to one where nobody opened anything.

**One unread limb is not a work list.** `hypertension.md`'s reads *"the narrative sections, the evidence tables, the appendices and the reference list"* of a 105-page document. *The narrative sections* is plural and unenumerated.

**The denominator exists and is independently derived.** `reference/guidelines-catalog.md` carries a `page_count` column that `tools/guidelines_catalog.py` re-derives from the extracted corpus and refuses when wrong: 13 for the cervical statement, 8 and 5 for the two prediabetes statements, 105 for AHA/ACC 2025, 377 for ADA 2026.

**Page is a locator and not an atom.** `cervical-cancer.md` cites p1 for all six of its rows while its rationale also sits on p1. A strict partition is therefore unavailable, which is why the rule is coverage.

**Three different things in this repo are called coverage**: `## Coverage` inside a sheet, which recommendation identifiers were accounted for; `reference/thresholds/coverage.md`, the per-topic registry; and now the per-page document read. The third takes no new heading and no reuse of the word.

**#436 bears on one limb of `diabetes.md` and not the other.** That ticket measured a 160-character mid-sentence cut across 48 bound documents and found ADA's 126 records to be 98 front-matter changelog entries. ADR 0017 measured the shipped snippets separately and found none truncated. So the damage is confined to the sheet's recommendation accounting, which is an index, and does not reach a page-coverage claim, which is a document read.

## Why point 5 of ADR 0009 is discharged rather than overruled

Point 5 reads *"A topic whose only records are `bound` remains `unread` while #436 is open. A fixed marker window that can end before the decision point is not a document read."*

The second sentence is the whole reason. It exists to stop a recommendation index masquerading as a document read. Point 3 above replaces that instrument entirely: a read is a named span with a page range, checked against a page count a different tool derives, and it never opens a recommendation record. A marker window ending before a decision point cannot make the claim in the first place.

Point 5 is therefore correct about the instrument it names and inapplicable to the one that replaces it. ADR 0009 keeps its text with a forward pointer rather than being amended, on [ADR 0014](0014-a-run-is-keyed-to-the-graded-artifact.md)'s arrangement and for its stated reason: the collision was not known on the day it was ruled, and rewriting the sentence would make the ruling look wider than it was.

## Why the two halves of a read are gated differently

Rows added carry evidence a machine checks: tier 1 requires the value's number inside the verbatim snippet, tier 2 requires that snippet on the cited page of the real PDF. A span retired having yielded nothing carries **no evidence at all**, and a careless read produces a byte-identical result to a careful one.

So the second read is spent where it is worth something. Reader B finding a decision point in a span A declared null **refuses**: A's claim has no evidence and B's has a page and a value. Reader B finding nothing in a span where A added rows **warns**: A's rows are already gated on a verbatim snippet located on that page, and refusing there would fail a correct row for a reader's miss — [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect, which this repo has now produced four times.

That asymmetry is the same shape as [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83)'s own caveat on gate 5: correlated error makes two readers agreeing cheap and does not make two readers disagreeing cheap, because correlation does not manufacture a disagreement.

## Why the committed trace is a marker rather than the record

The second-read JSON lives outside the repo and the pre-commit hook runs `threshold_sheet.py` with no `--second-read`, so that gate reads `NOT RUN` on every commit and in CI. A span retired on a null would otherwise land committed with nothing having checked it.

The dated marker in the `read` cell is what the committed sheet asserts, on `RENDERED:`'s precedent from [#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296) — an audit claim that a read happened, present-and-dated rather than re-runnable. The JSON stays out-of-repo evidence. What pre-commit can enforce without the corpus is that no span is retired with neither rows nor a marker, and that is what it enforces.

## Considered options

**Atomic promotion — the whole document or nothing**, which is how #471 was written. Rejected. It prices the valuable read at the cost of the worthless one: nobody could add the rows in USPSTF's *Clinical Considerations* until somebody had also read the reference list of the same 13-page statement, and ADR 0009 point 1 already guarantees a bibliography holds nothing. ADR 0009 point 3 — *an artifact does not change an `unread` topic's state* — is precisely the license to grow an artifact under `unread`.

**Agent reads and the clinician ratifies rows only.** Rejected. The negative half is the one with no evidence, so ratifying the evidenced half and waving the other through inverts the effort.

**A section may never be retired on a null result.** Rejected. It needs no second read and makes `sheet` permanently unreachable for every sheet whose unread list names a reference list, while discarding the information that a section was read and holds nothing.

**The clinician reads all four himself.** Rejected on arithmetic. There are 169 topics behind these four.

**Enumerate named sections with no page ranges.** Rejected. An omitted section is then invisible, and reaching an empty unread list without having listed a chapter that exists is partial coverage reading as complete, arriving on the state word.

**Per-section tickets.** Rejected as unwritable: the span list does not exist until the mechanism's first step derives it, so the tickets cannot be written before the thing they would decompose is built.

**Put the span list in `coverage.md`.** Rejected on inspection. That file's population is derived from the catalog's topic column and `tools/threshold_coverage.py` refuses any row that is not a catalog topic. Per-section rows break the derivation the registry's honesty rests on.

**A new top-level section in the sheet.** Rejected. It needs a name that is not *coverage*, and it adds an eighth heading to a format whose seven are a production interface the draft scaffolder imports from `SECTION_HEADINGS`.

**Make the span table optional.** Rejected. Silence never means full coverage, and an optional table means a sheet that ships without one makes no page claim while reading exactly like one that reconciles.

**Narrow ADR 0009 point 5 to forbid `sheet` while `## Coverage` rests on a broken index.** Rejected. Under point 3 the state asserts *pages read*; hanging it on the recommendation index makes one word assert two unrelated things, one of which no longer has a reader. What that option reaches for is satisfied by marking the limb inside the sheet, where the wrong number is.

**Extend the class exemption to evidence reviews as well as reference lists.** Rejected. USPSTF evidence reviews state numbers, and *does this number change what is done to a patient* is ADR 0009 point 1's reading rather than a property of a section's name. A class exemption that reached it would swallow a reading.

## Declared limits

**Page coverage catches an omitted span, not a misdrawn one.** A span written as `references pp. 12-13` where the references begin on p11 leaves p11 covered by a wrong claim — a page assigned to a span nobody read. Nothing here reaches that. It belongs beside the check in `tools/threshold_sheet.py` on `NOT_REACHED`'s arrangement, not only in this record.

**A blind second read is a smoke test in the clean direction.** `SECOND_READ_IS_A_SMOKE_TEST` already says so for gate 5 and it is no truer here. Two agents reading one span and both missing the same number agree.

**The marker records that a read happened, never that it was careful.** It is an audit claim in the sense `RENDERED:` is one.

**A span retired by class is not a span that was read.** The exemption is marked and countable for exactly that reason.

**The sequencing in point 10 is #464's to retire, not this record's.** When that ticket lands, the exact-source reading tickets stop being half-blocked and nothing here needs rewriting.

**Nothing here says anything about `none`.** A `none` topic has no artifact, so it has nowhere to carry a page-coverage table, which leaves the registry's most substantive claim its least checkable one. That is the symmetric hole and it is filed rather than ruled here.
