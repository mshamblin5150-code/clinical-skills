# A draft-backed citation is caught per row by the parser the module already shares and the class set is draft alone

[ADR 0061](0061-a-declared-non-source-is-an-enumerated-class-and-it-earns-a-fourth-sweep-state.md)
ruling 6 deferred rather than refused the coupling of `differential_scan` to a threshold sheet's
`## Sources` table, and filed it as
[#641](https://github.com/mshamblin5150-code/clinical-skills/issues/641). Grilled 2026-08-29 against
`origin/main` at `5342b99`. **Eight decisions, all the clinician's, all on that date.** Nothing is
built here.

The ticket poses three decisions. Two of them rest on statements about `differential_scan` that are
false of the module, and the third is answered by a document nobody had opened. Those three
re-derivations are most of this record.

## What is ruled

1. **The class is read from the sheet's `## Sources` table, joined per row.** *Sole source* leaves
   the rule entirely: a threshold citation names one source key, that key resolves to one `##
   Sources` row, and that row carries one class. How many sources the sheet declares stops
   mattering.
2. **`differential_scan` imports `threshold_sheet.parse` and `_threshold_index` is retired.** One
   parser over the sheet, `Sheet.sources` for the class and `Sheet.rows` for the citation join.
3. **The class set is `{draft}`, held as a named module constant.** Not a predicate over *not a
   guideline*.
4. **A source row carrying no `source class` cell is unread, not clean**, and prints a denominator.
   **A sheet `parse` returns `ok=False` for is a not-scanned limb**, exit 2, carrying `why_not`,
   suppressed per sheet rather than per run.
5. **The candidate gets its own count line and its own declared floors**, and does not join the
   row-24 applicability bucket. It does not retire ruling 6's reader row.
6. **It is built behind #587 items 1 and 2, which are independent of #483.** A draft-backed sheet is
   a tripwire in `NOT_VALIDATED_AGAINST`, not a blocker.
7. **The validation residue goes in `NOT_VALIDATED_AGAINST` and the behavioral residues are the
   report's declared floors.** No second limit object is added to this module.
8. **This record is written and ADR 0061 is corrected in place** on
   [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
   terms, its deciding paragraph untouched.

## The ticket's own premise is false, and it is false in the module's own file

#641 states, in bold, *"It never opens a sheet."* `tools/differential_scan.py:1004` builds
`THRESHOLD_ROOT / f"{topic}.md"` and `:1013` calls `_threshold_index(sheet)`, which parses that
file's `## Thresholds` table. The module reads three artifacts — the coverage registry, the shipped
threshold sheets, and `reference/guidelines-uspstf.md` — not the two the ticket counts. It reached
the claim from `_threshold_artifact_topics` at `:810-817`, which is one of them.

Two decisions rest on that sentence and both change when it goes.

**Decision 1 prices a coupling that already exists.** It offers *"opening the sheet is a new coupling
from a run scanner to `threshold-sheet/2`'s internals"* against *"a fourth column on `coverage.md`"*.
Neither half survives contact: the coupling is present and deep, and `coverage.md` carries four
columns today (`topic | state | artifact | record`), so the registry option is a **fifth** and moves
the `threshold-coverage/2` marker. What the registry can carry is a class per *topic*, which
forecloses decision 3 in the one direction that matters — a sheet holding one draft source among
in-force ones would read as wholly draft or wholly clean, and both are wrong.

**Decision 3's stated blocker is already paid for.** It says the per-row question is answerable
*"only if the scanner reads the row's `source` cell, which is a deeper read than the class check
itself."* `_threshold_index` already keeps `cells[4]` as `ThresholdRow.source`, `:1040` reads the cited key off
`THRESHOLD_CITATION` group 1 and `:1047` matches the two. The per-row read is what the module already does.

This is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape arriving in
a ticket's premise sentence: a generalization made from the one function the filing pass had open.

## The ACIP captures are the warrant, not the disclaimer

Decision 2 widens the class set on this ground: *"the ACIP captures recite a court order staying
their own schedule."* All three do carry that order, on line 1. It does not say that. Verbatim, from
the corpus text of `ACIP/Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC`:

> Pursuant to the preliminary order issued on March 16, 2026, in *American Academy of Pediatrics et
> al. v. Kennedy et al.*, No. 1:25-cv-11916 (D. Mass.), which stayed all votes taken by the ACIP
> during its June, September and December 2025 meetings, and further stayed the Acting CDC
> Director's [date elided] Decision Memo revising the CDC's childhood immunization schedule, the
> July 2, 2025 immunization schedule (as amended on April 27, 2026 to add the ACIP's April 2025 RSV
> recommendation for vaccination of high risk adults 50 - 59 as adopted by HHS) posted here is the
> current CDC Adult Immunization Schedule by Age for Consumers.

**One date inside that quotation is elided and nothing else is.** It collides with a date in
the clinician's shorthand corpus, and standing rule 1's corpus layer is the one thing in this
tree no file may exempt itself from — `phi_scan` refused the commit carrying it. The elided
value is the Decision Memo's own date and it is not what the passage turns on; the operative
clause is the last one, and it is verbatim.

The stay is of the **revisions**. The page served is the schedule that is in force *because* of the
order, and it says so in its own first sentence. A `web-capture` here is not a document that may
never take effect; it is the one that has.

That is what decides ruling 3, because the property `draft` has is not *not a guideline* — it is
**not in force**:

| class | topics | in force |
| --- | ---: | --- |
| `draft` | 1 | No. A public review draft; its numbers may not survive review. |
| `web-capture` | 3 | Yes, and the first sentence of each says so. |
| `errata` | 1 | Yes. A correction is in force by definition, and after #640 the topic is not sole-source. |
| `scope-of-work` | 1 | Moot. ADR 0061 ruling 4 gives it a null-sheet artifact, and a sheet with no rows cannot back a citation. |

So the wide predicate would flag three current immunization-schedule topics in order to catch one
document that is not in force — a false alarm on a correct citation, on the preventive-care topics a
case study is likeliest to touch. ADR 0061 ruling 1 refused a predicate over *not a guideline* for
this reason one artifact earlier; the same objection lands here unchanged. The set is enumerated so
that a later class — a withdrawn guideline, a retracted statement — is added by naming it rather
than inherited.

## Why the module ends with one parser

`_threshold_index` reads positionally: `if len(cells) != 8: continue`, then `cells[4]` and
`cells[7]`. That is the hazard ADR 0061 ruling 5 retired one file over, in that record's own words —
*"appending a column to this table would silently redefine the cell that decides
refuse-versus-warn."* Here the failure is quieter and larger. Append a ninth column to `ROW_COLUMNS`
and this matcher takes **zero** rows, so every threshold citation in every note reports *"threshold
source, strength, population, and value do not match a shipped row"* — a wall of findings on a
correct run, exit 1, with nothing naming the cause. `ROW_COLUMNS` has gained columns before.

Writing a second hand parser for `## Sources`, in the ticket that cites the record retiring the
first one, is refused on that ground alone.

The import costs nothing that is not already spent. `threshold_sheet.parse(text, path)` is a pure
text reader that opens no PDF and never raises — an unreadable sheet returns `ok=False` with a
`why_not` string. `threshold_coverage.py:111` already calls it, and `differential_scan` already
imports `threshold_coverage`, so the module is in the process before this change. `Sheet.rows`
carries every field `_threshold_index` derives: its `strength` is `cells[7]`, which is `Row.klass`,
and its `context` is `cells[0]` and `cells[3]`, which are `quantity` and `snippet`.

[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) states this tree's test for
whether a helper may be shared — *a helper two modules happen to have written the same way is not one
that exists to be depended on, and a test pinning the agreement would forbid the divergence the copy
exists to permit.* Divergence is not the point here. A run scanner holding its own answer about a
source's class could pass a citation the sheet grader flags, which is the one failure the check
exists to catch, and it is `reference_scan.py` importing `docx_write.REFERENCE_HEADING` exactly.

## Why a missing cell prints a denominator and an unreadable sheet is exit 2

ADR 0061's Consequences keeps both schema markers where they are — *"`threshold-sheet/2` gains a
column and `threshold-coverage/2` gains a state."* So no version distinguishes a pre-#587 sheet from
a post-#587 one, and `parse` returns `ok=True` for both. Two ways of not getting a class follow, and
they are not the same failure.

**A source row with no `source class` cell.** True of all four shipped sheets today and of any sheet
written before #587 forever. Skipping those silently prints `draft-backed citations 0`, which is
indistinguishable from a run whose every citation checked out — the defect this ticket is about,
rebuilt inside its own fix. So the report carries the population beside it, on
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling and on the shape
this module already has in `guideline tails checked against shipped sheets`.

**A sheet `parse` refuses.** Only two ways — no schema marker, or a `FORBIDDEN_IN_RAW_TEXT`
mis-encoded comparison operator. Under ruling 2 that empties `.rows` as well, so every citation to
that sheet would report as a definite mismatch about a comparison the scanner never performed. That
is partial coverage reading as complete with the sign reversed: a not-scanned condition filed under
the strongest heading the module has. It is exit 2 with `why_not` reported, on this module's own
documented arrangement, and `1 wins` is preserved. **Suppressed per sheet, not per run**, so a run
citing one good sheet and one damaged one still grades the good one — otherwise a single damaged
artifact hides a real row-24 violation elsewhere.

Both states are refused by `threshold_sheet --all` in the pre-commit hook and in CI, so neither
reaches `main`. They are reachable in a worktree mid-edit, which is where a run happens.

## Why the candidate does not join the row-24 bucket

`row 24 candidates - dependency needs a reader` means one thing: the subject could not be joined
mechanically, so a reader decides applicability. A draft-backed citation is its opposite — the join
**succeeded**, and what the reader is told is a fact about the source. Merging them makes the count
answer two questions, and the `declared floor` sentence beneath it false of half its members. This
module's reporting discipline is that a count means one thing and states its own floor; the
row-13, row-22 and row-23 split is that discipline already applied.

Ruling 6 of ADR 0061 stands. The command reports the label and the step 9 reader rules on whether
the number should stand, which is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *both* arrangement, and
the reader row is the half that fails when nobody looks.

## Why the AKI sheet is a tripwire

ADR 0061 says the coupling *"cannot be built until a draft-backed sheet exists, which is the last
item in the reading order."* That sentence rests on the premise the first section falsifies, and the
work splits by what each half needs:

| half | needs | real material today |
| --- | --- | --- |
| retire `_threshold_index`; the denominator; the `ok=False` limb | #587 items 1 and 2 | Four shipped sheets, graded by the hook and CI on every commit |
| reading `guideline` and `recommendation-statement` | #587 items 1 and 2 | The same four |
| the `{draft}` candidate firing | a draft-backed sheet | No, and not until the reading order's last item |

The lesson the ticket cites — that `block_scan` and `threshold_sheet` parser bugs were found by
pointing the tool at real material and neither by a fixture — is about **parser** bugs. Ruling 2 is
the decision that no parser is written here. `threshold_sheet.parse` is the one already run against
all four real sheets every commit, so the lesson has little left to bite on.

Waiting leaves the ninth-column trap live for the length of the corpus sweep — 165 of 169 topics are
`unread`, the KDIGO block is the reading order's last, and the AKI draft is the largest document in
the corpus. The firing path instead takes a `NOT_VALIDATED_AGAINST` row re-derived by its test, so
the day a committed sheet carries a `draft` source class the suite goes red with the instruction in
its own message. This tree has seen that instrument collect exactly once: the row-1 test fired on the
day `fixtures/slot-form-run` was committed, with its own words rather than a reader noticing.

## Where the residues go

`differential_scan` carries one limit object, `NOT_VALIDATED_AGAINST`, and its docstring draws the
line deliberately — *"What this scanner's validation set does not reach is `NOT_VALIDATED_AGAINST`
below, not this paragraph"* — leaving behavioral limits in prose. Three residues arrive and they are
not one kind.

The **validation** residue is that the firing path has never run against a committed sheet. It is
the tripwire above and belongs in that object by its own definition.

The two **behavioral** residues are permanent: whether a draft's number should stand is a reading,
and the class is read per row so no sheet-level claim is made. Filing those in
`NOT_VALIDATED_AGAINST` would put a permanent limit under a heading promising it goes away when
better material arrives, which sends the next session looking for a fixture that closes it. Adding a
second limit object instead would add a shape to this module while
[#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550) is open complaining that
`threshold_sheet` states its unreachable limits in three shapes with ADR 0046 adding a fourth. So
they are the report's `declared floor:` lines, printing on every run beside the count they qualify,
asserted by tests — which is the half [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)
says a docstring cannot have, since a prose edit to a docstring fails nothing and an edit to an
asserted report line fails.

## Consequences

**#587 items 1 and 2 become this ticket's only blockers.** Its body states that items 1, 2 and 6 are
independent of [#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483), so the cell
this reads is the near half of that ticket rather than the far half.

**#587 item 6's check-table row changes before it lands.** That item gives step 9's table a draft row
with `no` in the command column. This ticket makes that cell false and must flip it to the command in
the same commit — the row's reader is unchanged.

**A second measurement is recorded and not acted on here.** Across all 169 catalog topics there are
**zero mixed-class topics** — every topic's documents share a class — so the multi-source scenario
decision 3 was filed over is empty in today's corpus, and the first mixed-class topic that appears is
#640's babesiosis, whose second class is `errata` and is not in `{draft}`. Separately, **nothing
binds a sheet's `## Sources` documents to its own topic's catalog documents**: `threshold_coverage`
binds registry topics to catalog topics and `load_catalog_page_counts` requires a source to be in the
catalog, but a sheet for one topic may declare a source whose catalog topic is another. A
draft-backed row under an in-force topic is therefore reachable, and only the per-row read sees it.
That is a finding about `threshold_coverage`'s bindings rather than about this check, and it is
[#645](https://github.com/mshamblin5150-code/clinical-skills/issues/645) rather than folded in.
**#641's per-row class check does not close it**: that check catches a cited row whose source class is
`draft`, and the general form is a row whose source is a real, in-force guideline about a different
condition, which every gate in the sheet directory passes.

**ADR 0061 gains a dated correction line** on ADR 0016's terms. One sentence of its deferral
paragraph is falsified; ruling 6 and the decision to defer rather than refuse are untouched, and the
deferral is discharged by this record rather than reversed.

## Rejected

- **A fifth column on `coverage.md`.** Buys nothing the sheet does not, moves a schema marker three
  consumers read, and can only carry a class per topic — which destroys the per-row resolution that
  is the only honest answer to decision 3.
- **A second hand parser for `## Sources` inside `differential_scan`.** Smallest diff, and it plants
  the hazard ADR 0061 retired into the module that already carries one, in the ticket citing that
  record.
- **Importing `parse` for the class read while `_threshold_index` stays.** Pays the import cost, keeps
  the ninth-column trap, and puts two parsers over one file inside one function.
- **The predicate *not `guideline` and not `recommendation-statement`*.** Four classes; three of them
  fire on documents that are in force, and the loudest false alarm is on the schedule a court has
  ordered kept in force.
- **Treating a draft-backed citation as a finding.** Refusing it is closed by measurement — the
  public review draft is the sole acute kidney injury source in the corpus, so a refusal refuses the
  whole holding, which is ADR 0057's rejected *drop the draft* option arriving through the consumer.
- **Silence when the class cannot be read.** A zero with no denominator is the defect this ticket is
  about.
- **Failing a run for a missing `source class` cell.** Makes `differential_scan` a second grader of an
  artifact it does not own, and fails a run for a defect in `reference/`.
- **Joining the existing row-24 candidate bucket.** One line saved, at the cost of a count that
  answers two questions and a declared floor that is false of half of it.
- **A second limit object in this module.** The house pattern elsewhere, and a fifth shape here while
  #550 is open about shape proliferation.
- **Waiting for the acute kidney injury sheet.** Leaves the ninth-column trap live for the length of
  the corpus sweep and decays this design in a record nobody re-reads.
- **Splitting the retirement and the candidate into two tickets.** Honest, and it costs the second
  ticket a fresh grilling of decisions settled here.
- **A `status` column.** [#107](https://github.com/mshamblin5150-code/clinical-skills/issues/107)
  refused one and ADR 0061 forbids reopening it. Nothing here reopens it: `draft` is a form, and
  whether a guideline is current or superseded is still answered nowhere in this tree.
