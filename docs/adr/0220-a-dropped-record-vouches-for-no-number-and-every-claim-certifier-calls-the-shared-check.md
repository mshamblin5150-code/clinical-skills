# A dropped record vouches for no number and every claim certifier calls the shared check

**Measured at:** ab981a27fd4b594e62ab6a6743f7cee34b03d26e

Out of [#1056](https://github.com/mshamblin5150-code/clinical-skills/issues/1056), grilled on
2026-09-13. `peer_critique_scan` is the fourth number certifier and the only one that never calls
`discussion_artifact.claim_record_can_certify_values`: its `_believed_tokens` harvests every number
from every claim heading and restatement and reads no field that decides belief. Nothing is built
here; this is the record the build reads.

## What was measured before ruling, on 2026-09-13

- **Four modules import `CLAIM_BLOCK` from `discussion_artifact`**: `deck_scan`,
  `discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan`. The first three call the
  shared predicate and `peer_critique_scan` does not. `reference_scan` imports only citation helpers
  from that module, and `uptodate_sheet`'s `RESTATEMENT` is a topic-sheet heading, not a claim record.
- **`DROPPED` is read by no certifier.** It entered on
  [ADR 0211](0211-an-uptodate-entry-is-checked-against-its-masthead-and-a-sourced-record-is-cited-or-dropped.md)
  ruling 4 and releases only the reference-list obligation; the predicate names neither the field nor
  the state.
- **The live cost of both rulings below is zero.** Across the 54 registered worktrees, the 8 files
  named `claims.md` — the only name any certifier loads, per ADR 0198 — hold 784 claim records and
  none carries `DROPPED`. No run directory under any `scratch/runs/` carries a `critique.md`, so no
  peer critique run exists to begin failing. *Had either population been nonzero, the two counts
  would have printed it; they print zero, so these rulings close holes before any record uses them.*

## Ruling 1. `peer_critique_scan` routes its trace through the shared predicate

This applies a settled rule and was not a new decision. ADR 0153 ruling 3 made a certifier read the
states that decide belief, its 2026-09-08 correction brought `deck_scan` in the same way, and
[ADR 0198](0198-a-number-is-certified-only-by-a-record-whose-refutation-pass-ran.md) ruling 3 names
this module as the one that adopts the predicate under #1056. A record the predicate refuses
contributes no numbers. When
[ADR 0219](0219-a-refutation-fingerprints-its-heading-and-a-reader-pairs-the-draft.md) ruling 5 is
built, this module disbelieves a heading changed after its refutation with no further change.

The applications that follow from the same records: a body number found only in a disbelieved
record gets the *appears only in a disbelieved claim record* detail and a number in no record keeps
*absent from claims.md*, with no new finding kind (ADR 0198 ruling 3); and `DECLARED_LIMITS` gains
the field-completeness row derived from `research_ledger.REFUTATION_EVIDENCE_COMPLEMENT`, as its three
siblings carry (ADR 0198 ruling 2). ADR 0153 ruling 4's reference-key asymmetry has nothing to act on
here, because this module reads reference keys from the critique's own list rather than from claim
records.

## Ruling 2. A dropped record is never believed, and the shared predicate says so

`claim_record_can_certify_values` returns false for a record carrying `DROPPED`, so the rule reaches
all four certifiers at once. **The reason is the field's own meaning**: a record saying the document
no longer makes its claim cannot be the evidence for a figure the document still states. The rule is
written once, in `skills/_shared/reference/sourcing.md`, on ADR 0198 ruling 6's arrangement.

**Rejected:** leaving the predicate unchanged and declaring the gap in each certifier, which keeps a
hole whose only cost to close is zero; and disbelieving `DROPPED` in `peer_critique_scan` alone, which
is the per-caller copy ADR 0219 already refused as three copies of one rule.

## Ruling 3. The report prints `numeric claims` and `claim records`, as `discussion_post_scan` does

`claim records:` today prints the size of the believed number set, so two records carrying the same
figure print `1`. It becomes two lines: `numeric claims:` counts the distinct body numerals the
certifier checks, and `claim records:` counts the `## CLAIM:` records read from `claims.md`.

**Rejected:** a believed count beside the record count, which would make this certifier print a
figure its three siblings do not, and belongs to all four under one ticket if it is wanted; and a
single renamed line counting numbers, which keeps the record population off the page.

## Ruling 4. A test requires every importer of the claim-record parser to call the shared predicate

Every non-test module in `tools/` that imports `CLAIM_BLOCK` from `discussion_artifact` must call
`claim_record_can_certify_values`, read by AST rather than by text. **It is chosen over a typed list
of certifiers because the typed list is the defect this record follows**: ADR 0153 named two
certifiers while three existed, its correction added the third, and this fourth was missed by that
correction and by ADR 0198, each set named from the modules its session had open. *Run against the
tree measured above, the test fails on `peer_critique_scan` alone and passes the other three.*

Its ceiling is stated beside it: a module that writes its own `## CLAIM:` pattern instead of
importing the shared one is invisible to it, so a clean run is a floor on the shapes in the tree.

## What this record does not settle

- Whether a number may be certified from the restatement or only the heading. That is
  [#1245](https://github.com/mshamblin5150-code/clinical-skills/issues/1245)'s, and this build keeps
  the heading and restatement its siblings read today.
- Whether a `DROPPED` reason is true, or whether the draft in fact still makes the claim. ADR 0211's
  limit is unchanged.
- A marker on ADR 0219's declared limit naming this module. Whether a ratified record is edited to
  carry one is [#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201)'s open
  question, so ADR 0219 is not edited here.
