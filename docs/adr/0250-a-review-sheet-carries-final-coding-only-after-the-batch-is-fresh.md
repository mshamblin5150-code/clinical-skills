# A Review sheet carries final coding only after the batch is fresh

Ticket [#1205](https://github.com/mshamblin5150-code/clinical-skills/issues/1205) needs a
clinician-review surface before its separately gated Medatrax posting step. ADR 0223 made the
shift the approval unit but called its E/M code proposed; ADR 0243 later reduced the visible coding
worksheet to terse procedure lines and excluded E/M from agreement. The clinician ruled the
replacement surface before this build.

## Ruling 1 — the approval artifact is the Review sheet

A **Review sheet** is one batch-atomic Word document containing every finished note and that note's
finalized coding worksheet, in encounter order. It is generated only after ruling 8's supervised
handoff has been incorporated. It replaces *shift document* and *batch document* for this artifact.
Working tier blocks, portal-entry fields, schedules, summaries, and technical receipts remain private.

## Ruling 2 — the note carries one final E/M sentence

Each note carries one logical paragraph that may wrap naturally. It states the supported MDM
complexity, a concise patient-specific reason, the final E/M code, and new-or-established status.
It is placed at the end of an H&P's Medical Decision Making block and after SOAP's Final diagnosis,
before preventive screening. The skill selects the level supported by the encounter; moderate is
not a default.

## Ruling 3 — the visible worksheet is final and explanatory

The heading is `Coding worksheet`, not `Proposed coding worksheet`. It carries final ICD-10-CM,
E/M, CPT, and HCPCS selections; account-backed patient status; the problems, data, and risk
elements with concise patient-specific support; the two-of-three MDM conclusion; and
`Coding freshness: PASS`. The clinician's Review-sheet reading is quality control, not the step
that turns a proposal into a selection.

This supersedes ADR 0223 ruling 11's proposed posture and ADR 0243 rulings 16 and 17's terse,
excluded E/M surface. ADR 0243's private anchored worksheet and descriptor-agreement obligations
remain: the final surface does not erase its evidence.

## Ruling 4 — patient status is account-backed

New or established comes from the private identity map or Medatrax evidence. A shift-relative
inference is not evidence. An unknown status blocks finalization and therefore blocks the whole
Review sheet. This narrows ADR 0223 ruling 12: shorthand alone no longer settles the status.

## Ruling 5 — coding freshness has two independent limbs

Final coding requires both current authoritative sources and validity on the encounter's service
date. ICD-10-CM and HCPCS are checked against their live CDC and CMS release pages on every batch.
CPT uses a durable private receipt naming the licensed edition, source fingerprint, and next
edition boundary; it expires when that boundary passes or the fingerprint changes. Every selected
code is then checked in the committed databases for identity, completeness, billability where
applicable, and service-date activity. An unread, stale, incomplete, unsupported, or date-invalid
limb blocks finalization.

`tools/coding_freshness.py` is the public gate. Its private manifest names every encounter in exact
order, binds the normalized note-and-worksheet content by SHA-256, carries one account-backed status
record with a SHA-256 fingerprint of its private identity-map or Medatrax evidence and the final code
populations for each encounter, and refuses a missing or duplicate member.
The normalization uses UTF-8 text, LF line endings, trailing whitespace removed from every line,
and exactly one terminal newline; it covers the clinical note plus visible coding worksheet and
excludes tier blocks, Medatrax fields, and technical receipts. A successful private JSON receipt
retains those encounter records, URLs, fingerprints, and database hashes; the Review sheet renders
only `Coding freshness: PASS`.

## Ruling 6 — one blocked encounter blocks the batch

The Review sheet is batch-atomic. Every confirmed encounter appears exactly once and every
encounter must be finalizable before the document can be called ready for approval. A partial
document may be diagnostic working output, never a Review sheet.

## Ruling 7 — approval binds normalized clinical and coding content

The approval identity covers normalized note and worksheet content, account-backed status evidence,
batch membership and order, and freshness receipts. A substantive change invalidates approval for
the entire batch. A layout-only regeneration from unchanged normalized content does not.

## Ruling 8 — the supervised handoff precedes Review-sheet generation

After this skill change merges and before any Review sheet is generated, invoke `handoff` for the
supervised human Medatrax route. The clinician teaches the actual portal procedure; the resumed run
incorporates any field, status-evidence, or layout consequence before it freezes the normalized
Review-sheet content. The walkthrough does not authorize later unattended entry, and Review-sheet
approval does not enlarge that authority. ADR 0223 ruling 15's unattended-entry gate stays closed
until the procedure and the ticket's supervised-entry record both exist.

## Consequences

- `clinical-note`, its two templates, `icd10-cpt`, and `batch-shift` use one final coding contract.
- `coding_freshness.py` is required before a Review sheet is rendered.
- The #1205 build stops after merge for the handoff route and generates no Review sheet before that walkthrough is incorporated.
- No broader tracker reconciliation or ticket sweep is part of this ruling.

---

**Superseded in part 2026-09-16 by
[ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md), and left as
written.** Ruling 5's CPT receipt expiry, *"it expires when that boundary passes"*, is judged by the
encounter's service date rather than the day the gate runs. A fingerprint change still invalidates the
receipt, and every other ruling here stands.
