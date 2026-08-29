# A null sheet's re-derivable clause is re-derived and the gate keys on the zero-row condition

[ADR 0035](0035-a-none-topic-is-a-null-threshold-sheet-and-the-state-is-derived-from-its-span-table.md)
ruled that a `none` topic carries a threshold sheet whose `## Thresholds` holds no row, and that the
sheet declares itself. It fixed the declaration's **literal** and never ruled how strongly that
literal is graded. [ADR 0046](0046-the-scope-summary-is-graded-in-one-direction-and-the-unread-list-is-the-span-table.md)
ruling 8 corrected the wording and said so from the other side — *"which is why ruling 8 leaves the
declaration's own gate with #483."*

[#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483)'s body then carried the
question in its own words — *"Whether that presence test is enough, or whether the declaration must
be re-derived against the span table, is this ticket's to rule"* — while the ticket was labeled
`ready-for-agent`. Two sweeps found that independently and the label was corrected to `grilling` on
2026-08-27. The declaration is what lifts the zero-row refusal, and that refusal is the only thing
standing between a populated sheet and silently losing a column, so an agent picking the weak side
was picking the weak side of a safety gate.

Grilled on 2026-08-29 against `origin/main` at `a92a271`. The clinician ruled all five points below
on that date. **Nothing is built here; this is the record the build reads.**

## The measurement that reframed it

ADR 0035:17 states, under the heading *"The null sheet's shape is already closed by the existing
grammar"*:

> A zero-row sheet therefore cannot carry a `yes` span at all: every span is forced to
> `read YYYY-MM-DD` or `exempt:`.

**That sentence enumerates two values and drops the third.** `no` is a legal `read` cell, nothing in
the grammar forces it out of a zero-row sheet, and the record offers the claim as its reason for
building no further mechanism.

Re-derived by construction rather than by reading: build a zero-row sheet carrying the ratified
declaration and a span whose `read` cell is `no`, call `threshold_sheet.parse` and then
`threshold_sheet.gate_schema` on the result. **The SCHEMA finding count is zero**, identical to the
same sheet with every span retired. ADR 0046's own gate cannot fire either — its `Not read:` limb on
a null sheet names no span, which that record declares as its vacuity. So the artifact carrying the
registry's strongest claim would ship a sentence its own span table falsifies two headings up, and
nothing in the tree would see it.

**And the spec required that artifact to exist.** #483's *Tests* section asks for *"a null sheet with
an unread span audits `unread`"*, while its build item 1 requires the declaration for any zero-row
sheet to parse at all. The two together mandate a committed sheet asserting every span has left the
unread list beside a span table saying one has not.

## What is ruled

**1. The declaration's two clauses are graded differently, and the split is what makes the question
answerable.** *"Every span in `## Scope` has left the unread list"* is **re-derived against the span
table**. *"this source states no quantity that changes what is done to a patient"* is a reading,
stays declared, and is graded by nothing — the floor ADR 0025 point 7 states for the dated marker and
the one `specificity_scan`'s reason test lives with.

The consequence is the ruling's substance rather than a side effect: **a zero-row sheet is legal only
at `none` or `non-source`, never at `unread`.** #483's test above is deleted, and a null sheet with
an unread span refuses instead.

The third option — deleting the re-derivable clause so the prose claims only the reading — was
weighed and refused. It has a ratified argument behind it, ADR 0035 ruling 3's *"The declaration
carries no figures; the arithmetic stays in the span table"*, and clause A is arithmetic written as
prose. It fails on the harder half: deleting the clause does not stop the sheet claiming
**No decision point.** It only stops the sheet saying which spans back the claim, leaving an
unqualified assertion about a source on a sheet that has not finished reading it.

**2. The gate keys on the zero-row condition, never on the declaration literal.** Any sheet with no
threshold row refuses if any span's `read` cell is `no`, whatever declaration it carries.

Keying it on the `none` literal would bind one string. [ADR 0061](0061-a-declared-non-source-is-an-enumerated-class-and-it-earns-a-fourth-sweep-state.md)
ruling 4 requires a `non-source` sheet to carry a **different** declaration, whose literal is not yet
written and belongs to [#587](https://github.com/mshamblin5150-code/clinical-skills/issues/587)'s
build — so until that author copied the rule across, a `scope-of-work` sheet with half its pages
unread would ship. Nothing else would catch it: #587 build item 4 runs the class fork *before* the
derivation, so the row derives `non-source` and the `no` cell is never looked at. That is ADR 0061's
own stated tripwire — *"The read is the tripwire on the declaration"* — disarmed on the row that
record calls the one whose whole purpose is to prevent a false negative.

Keyed on the condition, the rule sits where the property lives. *No rows* is what makes an unread
span incoherent; *which sentence is present* is not. A third zero-row kind arrives already covered,
and **#587 inherits the gate without authoring anything**.

The standing warning against assuming a rule's twin is its mirror — `filled_vitals_census`'s block
boundaries, *"the safe direction of a rule is a property of the rule and not of the pair it belongs
to"* — was checked and does not bite. These are not mirrored boundaries but two declarations resting
on one structural fact, and ADR 0061 forecloses the case that would separate them: without the full
read, *holds no clinical quantity by design* is a claim about a class name and never about a
document.

**3. The gate lives in `gate_schema` and returns 1, not in `parse` at 2.** The two zero-row cases
fall on opposite sides of this repository's own status line.

*No rows and no declaration* is **did not scan**: the parser genuinely cannot tell a null sheet from
a `## Thresholds` table that lost a column, and `threshold_sheet.py:857-859` parses a row only when
`len(cells) >= len(ROW_COLUMNS)`, so a short row is silently skipped. That refusal stays in `parse`
at 2, unchanged.

*No rows, a declaration, and a span reading `no`* is **scanned and found something**: the span table
was read, the declaration was read, zero rows were counted, and the three contradict. Filing it at 2
would put the strongest thing known about the sheet under the weakest heading, which is
`differential_scan.py`'s recorded ordering. It also suppresses every other gate — a non-`ok` parse
returns `NOT GRADED` and *"Nothing was checked"*, so a missing source `url` and a duplicate span stay
invisible until the span cell is fixed.

Placement follows from that and is not merely tidy: every other span rule is already in
`gate_schema` — `span_problems`, duplicate spans, an undeclared span source, an invalid `read` value,
*"read span has neither rows nor a dated marker"*, and ADR 0046's `Not read:` cross-check. This one
in `parse` would be the only span rule outside the function that owns them. `Span.is_unread` is
already the exact predicate.

**4. A null sheet earns its own `differential_scan` finding message.** A Plan item citing a specific
threshold against a null sheet is a **finding** at exit 1 today and stays one — a run that cites a
threshold from a sheet declaring there is none has fabricated it. What changes is the sentence.

The shipped message is *"threshold source, strength, population, and value do not match a shipped
row"*, which sends the run to check its source key, strength letter and population against rows that
do not exist. The correct action is the opposite one: stop citing a threshold here. **Two opposite
remedies out of one message**, which is `guidelines_search.py`'s reason for keeping a genuine zero
apart from a failed scan, arriving on a message rather than a status.

The other spelling is untouched and already correct: `sheet does not settle it` returns a
**candidate** on a null sheet, because `contradicts` is vacuously false with no rows. That is ADR
0035 ruling 4's verdict behaving as ruled.

**The `guideline tails checked against shipped sheets` count line is not qualified.** The tail was
checked against a shipped sheet, and against the strongest thing that sheet asserts. A qualifier
there is ADR 0028 ruling 6's second mechanism for one trigger, and the residue [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)
exists for is already carried by #483's `none` qualifier line one artifact over.

**5. The four gates that go vacuous on a null sheet say `NO ROWS`, and deliberately not `NOT RUN`.**
`CITATION tier 1`, `CITATION tier 2`, `RANGE` and `WATERMARK` are `for row in sheet.rows` loops and
print a bare `0` on a null sheet. `SCHEMA` and `PAGE COVERAGE` are span-keyed and still work.

`NOT RUN` already means one thing in this module — *the evidence was unavailable, so the check could
not happen*: no recommendation record, no PDF root, no `--second-read`. A null sheet's tier-1 gate is
the opposite situation, with the evidence entirely present and nothing to check **because that is the
sheet's claim rather than a gap in it**. One word for a gap and an assertion is ruling 4's defect one
level down, and it would make CI's job summary report a null sheet as missing evidence it does not
miss.

## The omission gate moves the other way, and that belongs beside the markers

The intuition the `NO ROWS` markers invite is that a null sheet is checked less. On an `exact` source
it is checked **more**. `gate_coverage` computes `unaccounted = known - {row.rec} - scoped_out`, so
with no rows it collapses to `known - scoped_out` and every identifier in the record must be scoped
out by name with a written reason or the gate refuses. ADR 0035 ruling 6 records the direction and
that `none` is therefore harder to reach on `exact` than on `bound`.

`gate_second_read` moves the same way: every span of a null sheet is a null retirement, so ADR 0025
point 2's blind independent read applies to **all** of them, and any value that reader finds refuses.

That is what stops `none` being the cheap state, and it is why the vacuity markers are a report
change rather than a confession.

## Declared limits

**Clause B is graded by nothing and this record does not pretend otherwise.** A lazy reader writes
*this source states no quantity that changes what is done to a patient* as easily as a careful one.
What backs it is the per-span blind second read, which is out-of-repo evidence the hook never runs —
ADR 0035's own declared limit, narrowed here rather than closed.

**The gate is a floor on the `read` cell and not a reading of the span table.** A null sheet whose
spans all carry dated markers written without the read having happened passes it. `read YYYY-MM-DD`
records that a read happened, never that it was careful, which is ADR 0025 point 7.

**One direction of the scope summary stays ungraded.** Under this ruling every span in a legal null
sheet has left the unread list, so ADR 0046's gate refuses a null sheet naming any **span** under
`Not read:` — but a limb naming a string that is not a span label still fires nothing. That is ADR
0046's declared one-directional grading, unchanged.

## Two ratified records are corrected in place

On [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, with the correction noted inline at each site.

- **ADR 0035:17** — the sentence quoted above, which asserts the grammar already closes the shape.
  It does not, and it was offered as the reason no gate was needed.
- **ADR 0035:142** — *"A null sheet's claim is declared and page-checkable, not re-derivable."* Half
  of it is re-derivable now.
- **ADR 0035:53** — *"No rows **and** a declaration parses"*, which is true at `parse` and no longer
  the whole story.
- **ADR 0035:45** — the third limb of ruling 2's derivation, *"Any span `read: no` → `unread`"*,
  which stays live for a populated sheet and is unreachable for a zero-row one.
- **ADR 0046:78** — its note that the check is vacuous on a null sheet. Ruling 2 makes it
  non-vacuous there.

**Ruling 3's own heading in ADR 0035 — *"the declaration is what lifts the zero-row refusal"* — is
correct and is not corrected.** The declaration still lifts the refusal in `parse`; ruling 2 above
says only that the span gate is not keyed on it. A sweep agent reported it as a collision and it is
not one, which is this repository's own rule that a subagent's conclusion is a claim and not a fact.

## What this does not close

**#505.** *The USPSTF looked and found no evidence for an interval* still reaches a note as
`sheet does not settle it`, the same words as an unstated absence. Ruling 4 changes only the message
on the citation path.

**The first `none` reading.** No topic is promoted here and none is promoted by #483's build.
[#519](https://github.com/mshamblin5150-code/clinical-skills/issues/519) is the first reading and it
waits on the mechanism, on ADR 0035 ruling 7.

**#587's own build.** Ruling 2 hands it the span gate; its declaration literal, its `source class`
cell and its fourth state remain its own.
