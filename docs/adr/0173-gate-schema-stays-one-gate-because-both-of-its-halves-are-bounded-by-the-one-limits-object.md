# `gate_schema` stays one gate because both of its halves are bounded by the one limits object

Out of [#1005](https://github.com/mshamblin5150-code/clinical-skills/issues/1005), grilled on
2026-09-11 to an empty frontier. Measured at `b55963e` with the freshness gate `FRESH` before
reading.

#1005 was filed from
[ADR 0159](0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md)'s
*What this record does not settle*. Its charge is that `gate_schema` in `tools/threshold_sheet.py`
answers two questions -- is the sheet structurally valid, and does the scope summary agree with the
span table -- and that the second half is what kept the first out of `tools/threshold_grammar.py`.
Its payoff was the move: split the gate, send the structural half to the grammar, and leave the
scope rows with the code they bound.

**Row counts of `threshold_sheet.DECLARED_LIMITS` are not stated anywhere in this record**, on
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)'s
closing instruction. Rows are named by key.

## What was measured before ruling, on 2026-09-11

**The gate does answer two questions, and the halves are very unequal.** The comparison between the
first `Not read:` sentence and the span labels is one block at the end of `gate_schema`, before the
conflict rule, plus the `_not_read_scope_items` helper beside it: thirteen and twenty-two lines at
`b55963e`. Everything else in the function is structural.

**The premise the payoff rests on is false, and was false when #1005 was filed.** The ticket says
every row in the `SCOPE_SUMMARY_NOT_REACHED` view bounds the scope-summary half *"and none bounds
the first."* The first clause holds. The second does not: three rows of the same object, outside
that view, bound the structural half, and each sentence names SCHEMA as the gate it limits.

- `population-key-correctness-unverified` -- *SCHEMA checks that a population key is declared, never
  that the key describes the right patients.*
- `download-address-reachability-unverified` -- *SCHEMA checks that a Download address is an
  HTTP(S) address but never opens it.*
- `download-basis-evidence-not-replayed` -- *SCHEMA validates the Download basis vocabulary and date
  shape but does not replay a fetch.*

All three are behavior-disposition rows whose handlers in `tools/test_threshold_sheet.py` drive the
structural half (`SchemaGate`, `ConflictRule`, `TheDownloadAddressIsGraded`). All three were present
at `9bb259e`, the commit #1005 and ADR 0159 were measured at; they entered the object on 2026-08-30.
*Had the structural half carried no limits of its own, a reading of `DECLARED_LIMITS` outside the
view would find no row whose sentence names SCHEMA; it finds these three.*

**The view is not a pure scope-summary population either.** Its last row, `misdrawn span
boundaries`, carries `PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES` -- *page coverage catches an
omitted span, not a misdrawn one* -- which limits the page-coverage gate. The view is ADR 0046's
rows kept contiguous, not a partition of `gate_schema`.

## Ruling 1. `gate_schema` stays one gate

**The move #1005 was filed to unlock is closed by the same ground that closed it the first time.**
ADR 0159 ruling 1 kept `gate_schema` in `threshold_sheet` because moving it would leave limit rows in
`threshold_sheet.DECLARED_LIMITS` describing code in another module. That ground applies to the
structural half too, through the three rows above.

The two routes that would free it are both closed:

- **Split `DECLARED_LIMITS` so the rows travel with the code.** ADR 0074 ruling 2 rules one
  module-wide object, and #1005's own *What must not come out of this* makes this the condition
  under which the answer is no.
- **Give `threshold_grammar` a limits object.** ADR 0159 ruling 8 rules that it carries none, and
  `tools/test_declared_limits.py` records its no-limits reason under ADR 0167 ruling 3.

With no move available, a split buys no module boundary, and the ticket's only reason to split was
the boundary.

## Ruling 2. #1005's decisions 2 through 4 have no subject, and `threshold_coverage` refuses on what it refuses on today

`tools/threshold_coverage.py` keeps calling `threshold_sheet.gate_schema(sheet, source_classes)`
and refusing on its findings. Nothing it refuses on moves, so decision 2's question -- call both
gates, or narrow to one -- does not arise. Decision 3 has no destination, and decision 4 has no
second gate to type.

**The baseline [#1064](https://github.com/mshamblin5150-code/clinical-skills/issues/1064) rules
against is therefore unaffected by this record.** #1005's *Done when* froze `threshold_coverage`'s
refusal set only on the branch where the gate split.

## Considered options

- **Split inside `threshold_sheet`.** Pull the comparison block into its own function beside
  `_not_read_scope_items`, still counted under `SCHEMA`, so output stays byte-identical and
  `threshold_coverage` is untouched. Not ruled for or against: it is a private refactor with no
  second caller and needs no ruling. It would give the view's rows a named home and change nothing
  a reader or a command can observe.
- **Rule that a limit describes a command's run contract, not where its code lives.** The structural
  half could then move while every row stayed behind. Refused: it overturns ADR 0159 ruling 1 to
  rescue a payoff the measurement removed, and that ruling's ground now holds for both halves.

## What would reopen this

**The structural half ceasing to carry limits of its own.** If the three rows named above were
retired or re-keyed onto the scope-summary half, the move #1005 describes would become available
again and decisions 2 through 4 would regain their subject, including the behavior change in
`threshold_coverage`. A measurement that `gate_schema` answers two questions, or that it is long,
does not reopen it: both are true today and neither moves where its limits live.
