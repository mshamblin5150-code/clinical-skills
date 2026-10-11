# Supersession-only ADR edits preserve the historical measurement base

Out of #1518. On 2026-10-11 the clinician selected option A: permit a narrow
exception for supersession-only edits that preserve the original measurement
declaration and findings, rather than rederive historical measurements merely
because their ADR receives an annotation.

## Ruling 1. An unchanged historical measurement stays historical

An ADR edit confined to supersession annotations and their matching declarations
does not owe a fresh measurement base when the original measurement declaration
and findings remain intact. Its historical declaration is preserved, not replaced
with today's revision or represented as a new measurement.

This narrows [ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) ruling 6's branch-drift refusal and ruling 7's
record-level forcing function for this class of edit only. Other changes to the
record keep the existing measurement rule, including changes to a measurement,
its declaration, or the findings that make it mean something.

## Ruling 2. The exception is proved from the actual prior bytes

The staged and committed ADR readers compare the edited record with its prior
Git bytes. They accept only the documented supersession annotation and declaration
forms while preserving the original substantive text. Canonical normalization of
an existing supersession annotation is within the exception only when its original
words and date remain; [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
owns that preservation obligation.

A new ADR, an unrelated body edit, a changed declaration, or an unreadable prior
record earns no exception. The existing grade still runs when the proof fails.
Calling an edit supersession-only does not establish the proof.

## Ruling 3. Tracker publications retain their existing gate

This exception belongs to retrospective ADR maintenance. It does not change the
measurement grade for a tracker publication or certify that an original measurement
was correct. The command's complete mechanical boundary remains in
`tracker_measurements.DECLARED_LIMITS`.

## Supersedes

- [ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) ruling 6, the branch-drift refusal for supersession-only ADR maintenance. Ruling 1 preserves the original declaration and findings; other edits still owe the existing grade.
- [ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) ruling 7, the demand to rederive a preserved historical record merely because supersession annotations change it. Ruling 1 keeps its historical base; new measurements and other changes remain record-level.
