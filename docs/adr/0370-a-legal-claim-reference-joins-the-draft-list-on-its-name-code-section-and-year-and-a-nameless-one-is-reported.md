# A legal claim reference joins the draft list on its name, code, section and year, and a nameless one is reported

**Measured at:** 84418797c3451c4f6d5076e0d93ad83958308832

[#1583](https://github.com/mshamblin5150-code/clinical-skills/issues/1583) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4) in October 2026. A claim
record cited a regulation in APA's legal reference form, and `python tools/research_ledger.py
--draft` reported it as `sourced-record-not-listed` although the draft's reference list carried the
same entry. The run swapped to a secondary source and dropped the primary one. The clinician ruled
every point below on 2026-10-16, against `main` at the commit above, where the freshness gate read
`FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The defect reproduces, and the probe could have shown it fixed.** At the commit above,
`research_ledger.reference_identity` returned `None` for a named regulation entry of the form
`<Name of regulation>, 42 C.F.R. § 414.56 (2025).` and for its section-only twin
`42 C.F.R. § 414.56 (2025).`, and returned an identity for an ordinary author-year-title entry. Had
the legal form been read, both legal probes would have returned an identity as the ordinary one did.
The shared `discussion_artifact.LEGAL_CITATION` grammar found its legal span in both legal probes,
and `discussion_artifact.legal_reference_lacks_name` was true for the section-only probe alone. The
#1583 triage drove the same entry through `--draft` on `main` at `69316820` and recorded exit 1 with
`sourced-record-not-listed 1` beside a clean ordinary control.

**The join compares two complete entries, not a citation with an entry.**
`draft_reference_findings` compares the identities of each sourced, non-dropped record's
`REFERENCE` field with those of every entry in the draft's reference list. Both sides are
reference entries the run wrote for one source.

**The in-flight population, counts only.** Every registered checkout's `scratch/runs/*/claims.md`
was read through `research_ledger.read_records`: 18 distinct ledgers, all readable. They hold 36
records whose `REFERENCE` carries a span the shared legal grammar recognizes, all `sourced`, one
`DROPPED`. Six of the 36 have no regulation name, in 2 runs, both discussion-post runs. ADR 0088
ruling 3 recorded 0 nameless of 5 legal entries at its own date; that figure was quoted during this
grilling as current and was corrected by this count before ruling 2 was confirmed.

**`research_ledger` is not case-study-only.** `discussion-post`, `discussion-reply`,
`course-assignment`, `peer-critique` and `practicum-case-study` all run it.
`discussion_post_scan` already reports a nameless legal `REFERENCE` in a discussion run's ledger,
under ADR 0039 ruling 5; nothing reports one in the other skills' ledgers.

## Ruling 1 — a legal claim reference and a draft entry are one source only when name, code, section and year all agree

When the text before a reference entry's parenthesized year is recognized by the shared legal
grammar and no title follows the year, its identity is that whole element before the year,
normalized as ordinary identities are, together with the bare year. The regulation's name, its code,
its section and the year all take part in the comparison, so a record and a draft entry differing in
any one of them do not join. This is the legal counterpart of the author, year and title identity an
ordinary entry already takes, and it is no more lenient.

[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
ruling 2 is untouched and does not extend here. It lets a legal entry be found by its name or by its
section so that either in-text spelling resolves. Here both sides are entries, so its reason does
not transfer.

Keying on code, section and year alone was declined because a record naming the wrong regulation, or
none, would join a named draft entry and the disagreement would go unreported. Keying on name and
year alone was declined because a mistyped section would join silently.

## Ruling 2 — `research_ledger` reports a claim record whose legal reference carries no name

A `sourced` claim record whose `REFERENCE` is a legal entry with only its section in the author slot
is a finding, detected by importing `discussion_artifact.legal_reference_lacks_name` and not by a
second predicate. It is a new kind traced to #1583.

Under ruling 1 a nameless record still joins an identical nameless draft entry, where
`reference_scan` reports the draft's missing name. A nameless record beside a named draft entry does
not join, and this row then states the defect the `sourced-record-not-listed` finding beside it
does not. On a discussion-post run the same defect is also reported by `discussion_post_scan`; the
two graders name one defect with one remedy, and that duplication was accepted.

Leaving the record side unchecked was declined because a nameless claim record in a case study, an
assignment or a peer critique would be reported by nothing. Treating a nameless entry as never
joining was declined because its only report would then be a `sourced-record-not-listed` finding
blaming a reference list that does carry the source.

The row starts at the build's landing time, compared with approval, under
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md).
The six nameless records counted above remain real defects; ruling 2 neither drains nor exempts them.

## Ruling 3 — the join reads only the legal forms the shared grammar recognizes

The legal branch of ruling 1 applies only where `discussion_artifact.LEGAL_CITATION` recognizes the
author element: the title-number code-section shape, the listed West Virginia sources, and the fixed
session-law form, as `discussion_artifact.LEGAL_READER_MECHANISMS` declares them. One
`research_ledger.DECLARED_LIMITS` row names what the join does not read: court cases, Federal
Register entries, executive orders, treaties, constitutional provisions, unlisted codes, and the
shared grammar's leftmost-span limit. A claim citing one of those still reads as
`sourced-record-not-listed`.

`reference_scan` also recognizes full-date treaty forms and date-free constitutional locators
structurally. Reading them here was declined because a date-free provision needs a yearless identity
built for forms not cited in this coursework. Matching any entry with nothing after its year on its
exact pre-year text was declined because it is no longer a rule about legal entries and would let an
ordinary entry missing its title join an identical copy of itself. Widening the join is widening the
shared grammar, which moves every grader together.

## Build checklist

- `tools/research_ledger.py`: a legal branch in `reference_identity` (and so in
  `reference_identities`) per rulings 1 and 3; one new kind for ruling 2 with its `ROWS` entry
  tracing to `#1583`; one `DECLARED_LIMITS` row per ruling 3.
- `skills/practicum-case-study/SKILL.md` step 3's row table gains the new kind, which the test keyed
  on the module's tuple requires.
- `reference/completion-check-starts.tsv`: a row for the new kind at the build's landing time,
  compared with approval.
- Tests driving `python tools/research_ledger.py --draft` with synthetic ledgers and drafts:
  - a named regulation record joins its identical draft entry (exit 0);
  - the ordinary author-year-title control still joins;
  - a legal record whose section, year or name differs from the draft entry stays
    `sourced-record-not-listed`;
  - a nameless record is reported by the new kind, both beside an identical nameless draft entry and
    beside a named one;
  - a court-case record stays not-listed, with the `DECLARED_LIMITS` row naming its form;
  - a mutant that drops the legal branch fails the named-entry positive.

## What this record does not reach

- **Whether the cited regulation says what the claim says, or is current law.** Both stay readings.
- **The in-text form of a legal citation.** ADR 0039 rulings 1 to 3 govern it.
- **Legal forms outside the shared grammar.** Ruling 3's declared row.
- **The six existing nameless records.** They are defects for their runs to fix, not for this build.
