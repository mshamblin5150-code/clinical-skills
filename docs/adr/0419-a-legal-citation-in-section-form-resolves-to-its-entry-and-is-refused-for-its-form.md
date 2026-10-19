# A legal citation in section form resolves to its entry and is refused for its form

**Measured at:** db02f093a2c6bb5df72c0ce3a54c64b4e8f54e18

[#1850](https://github.com/mshamblin5150-code/clinical-skills/issues/1850) was filed from
[#1706](https://github.com/mshamblin5150-code/clinical-skills/issues/1706)'s grilling under
[ADR 0390](0390-an-overturned-passage-with-no-ruling-number-is-located-by-its-exact-quote-and-a-repair-s-mislabeled-opening-is-restored.md)
ruling 9. It reports that commit `6c75ba62`, the #976 build, removed the section key
[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
ruling 2 requires, and that no record says so. Grilled 2026-10-19 against `main` at `972ebf8d`,
where the freshness gate read `FRESH` and the measurements below were taken. The commit above
adds only the first draft of this record, its markers and its glossary edit to `main` at
`7821ce1f`, which differs from that base only by ADR 0417; ADR 0417 touches no module or record
measured here. The clinician ruled every point below in that
session, one question at a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The ticket's account is right and is half the removal.** In `tools/discussion_artifact.py`,
`reference_keys('Patient rights, 42 C.F.R. § 482.13 (2024).')` returns only
`(('patientrights', '2024'),)`. The same commit deleted the empty-year duplicate and flipped the
2 entry forms × 5 in-text forms matrix in `tools/test_discussion_post_scan.py`: a named entry now
resolves only the two name spellings, and a section-first entry resolves nothing. Read from
`discussion_reply_scan.py`, the reply grader then reports a section citation whose entry is in
the reply's own list as `<section>, <year> has no matching reference`, which names a missing
source where the source is present.

**The same commit made the same change to the draft grader, and no record says that either.**
`reference_scan.py`'s docstring changed from *"A legal entry resolves on its Source and section,
with or without a citation year"* to *"A supported statute or regulation resolves on its title and
publication year"*, and from excluding legal entries to *"A supported named statute or regulation
participates in `uncited-entry`."* That reverses
[ADR 0088](0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md)
ruling 1's section key and its rulings 2 and 5's exclusion. Driven through
`python tools/reference_scan.py <draft> --as-of 2026-10-19 --show` over a draft whose only entry
is `Patient rights, 42 C.F.R. § 482.13 (2024).`:

| body | `uncited-entry` | `unlisted-citation` |
| --- | ---: | ---: |
| `Patient rights (2024) sets the rule.` | 0 | 0 |
| `The rule is set (Patient rights, 2024).` | 0 | 0 |
| `The rule is set (42 C.F.R. § 482.13, 2024).` | **1, false** | **1, false** |
| `Under 42 C.F.R. § 482.13 the rule is set.` | **1, false** | **1, false** |
| `The rule is set elsewhere.` | **1, true** | 0 |

All five runs exit 2 as well, for a reason outside this record: no paper language was supplied, so
reference order was not graded. Every legal row in them is as tabled.

**Why the removal happened is legible, and why it is a finding.** The #976 build read the
*Publication Manual*'s legal chapter, and
[ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) ruling 4,
ruled the same day, holds that a legal in-text citation is the entry's first element and its
publication year. `skills/_shared/reference/apa7.md` now teaches that form. Neither that record
nor any other names ADR 0039 ruling 2 or ADR 0088's rulings as withdrawn, so a reader of either is
told the section form resolves when the code no longer lets it.

## Ruling 1 — a section-form legal citation resolves to its entry, in every grader

The section key comes back. A named legal entry yields its name key, its section key with the
publication year, and its section key with an empty year, as ADR 0039 ruling 2 rules;
`reference_scan`'s `Entry.resolution_keys` derives the section key in its own key space, as ADR
0088 ruling 1 rules. So `(42 C.F.R. § 482.13, 2024)`, `42 C.F.R. § 482.13 (2024)` and a bare
`42 C.F.R. § 482.13` all match `Patient rights, 42 C.F.R. § 482.13 (2024).` in the reply,
peer-critique, post and draft graders.

**The removal is reversed, not ratified.** The declined branch kept it and recorded it: no code,
but the citation stays reported as having no matching reference while its source sits in the
list. A finding that names a missing source where none is missing is the misattributed shape this
repository has ruled against repeatedly. Restoring the key without ruling 2 below was also
declined, because it would leave `apa7.md` teaching a form the graders no longer enforce.

ADR 0039 ruling 2 and ADR 0088 ruling 1 therefore stand as written, and the build restores what
they rule. The section-first entry, which names no regulation, stays ADR 0039 ruling 5's and ADR
0088 ruling 3's defect.

## Ruling 2 — a section-form legal citation is refused for its form

A legal citation that resolves through a section key, rather than the entry's name, is a
`legal-citation-section-form` finding. It fails the artifact (exit 1), on the reply,
peer-critique, post and draft graders under the one shared name, and its detail names the
citation and says to write the legal source's name and the entry's year.

**This overturns ADR 0039 ruling 2's refusal to police the in-text form.** That ruling rested on
there being no evidence faculty mark the in-text spelling. The *Publication Manual* now grounds
the sheet directly: ADR 0151 ruling 4 reads §11.3 and §11.5 as making the title and year the
legal in-text form, and the same reading already refuses a legal citation whose year disagrees
with its entry. A report-only row was declined: section citations have been failing since
`6c75ba62` under the wrong name, so a row that never fails would lower enforcement below what has
run for six weeks, on a ground the manual has since outweighed.

**A section citation with no year takes the same finding.** It resolves through the empty-year key
and is refused for its form; it is never reported as missing a source.

## Ruling 3 — a named legal entry takes part in the draft grader's `uncited-entry`

The #976 build's reversal of ADR 0088 rulings 2 and 5 stands, and this record is its declaration.
ADR 0088 ruling 2 excluded legal entries because the draft grader could not see a citation written
in the regulation's name, so it could never honestly prove one uncited. Rows 1 and 2 of the table
above show that blindness is gone, and row 5 shows the row now catches a regulation listed and
never cited, which the exclusion let pass. Rows 3 and 4 are false only through the removed section
key, which ruling 1 restores.

Restoring the exclusion was declined: it would silence a true finding for a reason that no longer
holds. ADR 0088 ruling 5's every-run statement survives with its sense reversed, and the report
already prints *"A supported named statute or regulation participates in uncited-entry by title and
year."* An entry with no name stays outside the row, because it has no key to be cited by.

## Ruling 4 — one record and one build cover both modules

`discussion_artifact` and `reference_scan` lost the section key in one commit, for one reason, and
both now misname the same citation. Filing the draft grader separately was declined: until the
second ticket landed, the reply grader would name the real defect while the draft grader blamed a
missing source for the same citation, and the next session would re-derive this measurement.

## Coordination the rulings fix without a further choice

- **Posted work is not re-graded.** Approved items keep their frozen grades under
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md), so
  the new finding reaches only work graded after the build lands.
- **The name is shared.** `legal-citation-section-form` is one constant, defined once beside the
  shared legal grammar and imported by each grader, so the four cannot drift apart.
- **The glossary entry for a legal citation** said the section *may stand in the same slot*. It now
  says a citation spelled with the section alone resolves and is refused for its form.

## What this does not reach

- **Whether the cited section says what the artifact claims.** That stays the refutation pass's.
- **Whether a legal citation's year is the year of the edition consulted.** ADR 0039's *What none
  of this reaches* still holds for a section citation with no year: the empty-year key resolves
  regardless of the entry's year.
- **Whether faculty mark the section spelling.** Ruling 2 rests on the manual, not on evidence of
  faculty marking, and none was measured here.
- **Legal forms outside the recognized statute and regulation subset**, which
  `discussion_artifact.LEGAL_READER_NOT_REACHED` owns.

## Build checklist

1. Restore the section key and its empty-year duplicate in `discussion_artifact.reference_keys`,
   and the section key in `reference_scan.Entry.resolution_keys`.
2. Add `legal-citation-section-form` beside the shared legal grammar, fire it where a legal
   citation resolves only through a section key, and add it to each grader's rows and to
   `apa7.md`'s rule.
3. Re-derive the 2 × 5 matrix in `tools/test_discussion_post_scan.py`: every named-entry cell
   resolves, the three section cells carry the new finding, and the section-first entry stays a
   `legal-reference-name` defect. Drive the five-row table above through `reference_scan` with
   rows 3 and 4 moving to the new finding and row 5 unchanged.
4. Rename the two tests whose names state the removal as a rule.

## Supersedes

- [ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
  ruling 2, the paragraph beginning "The in-text form is deliberately not policed". The section key
  stands and is restored by ruling 1; the in-text form is now refused under ruling 2.
- [ADR 0088](0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md)
  ruling 2, the exclusion of legal entries from `uncited-entry`, under ruling 3.
- [ADR 0088](0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md)
  ruling 5, the sentence saying a legal entry is outside `uncited-entry`, under ruling 3. The
  legal count and the every-run statement stand.
