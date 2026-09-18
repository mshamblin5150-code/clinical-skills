# The CPT descriptor set is rebuilt by two readers and a verified flag gates it

**Measured at:** 6ede4b5f6b6cd4e7882dc4914fbc7471518c2394

[#1348](https://github.com/mshamblin5150-code/clinical-skills/issues/1348) found CPT descriptors in
`reference/procedure-codes-2026.sqlite` that name a sibling code's analyte: 87804 returns the
immunoassay stem followed by both the group B streptococcus term and its own influenza term. Grilled
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

Read from the committed database's `code` table, CPT rows only.

| Shape | Rows | What it is |
| --- | ---: | --- |
| text before the final `; ` equals another CPT code's complete descriptor | 3,927 | the ticket's own predicate |
| of those, the matched parent carries its own `; ` | 3,617 | the figure #1348 published |
| of those, the matched parent carries no `; ` | 310 | mostly a parent ending in a bare `;`, giving `;;` |
| any `;;` | 304 | the doubled separator those produce |
| descriptor ending at a colon | 37 | a bulleted element list that was never carried |

*Under the stacking being legitimate three-level nesting, some matched parents would themselves be
children of a further parent, and some candidates would carry more than one stacked term.* Neither
occurs. Every matched parent has at most one semicolon, no matched parent is itself a candidate, and
no row outside the 3,927 has two or more `; `. In 3,876 of the 3,927 the parent's locator sequence
precedes the child's.

`tools/procedure_codes_build.py` copies the CSV `description` column verbatim, so the join did not
make these. The fault is in the normalized licensed CSV recorded in the `source` table as
`licensed-cpt-2026.csv`. That file is not on disk anywhere searched and no producer for it is in the
tree, so the input cannot be audited.

**The predicate is a floor, and one case proves it.** 86486 is stored under the unlisted hematology
stem of 85999, the code before it in the extracted order; the book prints it in the skin-test
family. It was found only because 85999's descriptor happens to be a complete descriptor. A wrong
stem that matches no other code's descriptor is invisible to every check over the database, so the
wrong-parent population cannot be counted from the database.

## Ruling 1 — the CPT set is re-extracted from the rendered book, not repaired in place

The whole CPT code set is extracted again from the maintainer's authenticated VitalSource copy of
CPT Professional 2026 and the database rebuilt from it. A mechanical rewrite of the 3,927 stacked
rows was refused: it is exact for that shape alone, cannot reach the wrong-parent shape, and cannot
restore the 37 dropped lists. A database repaired that way would present a partial correction as a
clean one. A mechanical stopgap followed by the rebuild was refused for the same reason.

## Ruling 2 — a separate descriptor flag carries the interim state

The database's `meta` table gains `cpt_descriptors`, whose values are `verified` and `unverified`,
and the committed database is set to `unverified` until the rebuild lands. While it is
`unverified`, `tools/procedure_codes_lookup.py` prints its own warning beside every CPT result, and
`icd10-cpt` takes every CPT descriptor from the rendered destination page rather than from the
lookup.

**`cpt_complete` keeps its single meaning.** Setting it to `no` would have routed every code to the
same read with no code change, and was refused: completeness says whether a miss is evidence of
absence, and this defect is whether a hit's text is right. A flag meaning both leaves the reader
who clears it unable to say which one was certified. HCPCS rows are untouched; they come from the
CMS machine file.

## Ruling 3 — `verified` is earned by two independent extractions agreeing exactly

The rebuild produces two extractions of every CPT code by different methods. A code's descriptor is
accepted where the two agree exactly. Every disagreement is resolved by reading the code's rendered
destination page, and the resolution is recorded. A disagreement not yet resolved is an unread
remainder and never clean. The rebuild must reproduce four named controls exactly: 87804 with
influenza as its only analyte, 86486 in the skin-test family, 97169 with its element list, and 45825
with no doubled separator.

This is [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md)'s
two-reader rule extended from the MDM sheet to the code set. One extraction with fixed controls was
refused because a single pass cannot see its own systematic error; that is how the first CSV was
wrong for thousands of rows without anything reporting it. A random rendered-page sample was refused
because it finds only the defect shapes that happen to land in the sample.

## Ruling 4 — the rebuild inputs are kept in the owning checkout's scratch root

Both extractions, the disagreement record, and the agreed CSV are written under `scratch/cpt-2026/`
resolved through `repo_root.scratch_root()`, never through the worktree the rebuild runs in. The
`source` table records each file's SHA-256, and the build refuses when any recorded input is absent
or its digest disagrees.

Committing the transcriptions was refused: that places further copies of licensed CPT text in a
public repository, which the procedure-code reference already rules against for the CSV. Keeping
only the agreed CSV was refused because it discards the evidence that the two readers were
independent and how each disagreement was settled.

## Ruling 5 — reader 1 is structural and reader 2 is screenshot transcription

Reader 1 parses the reader's page structure. Reader 2 transcribes the rendered pages from
screenshots. Two screenshot readers were refused: they share a method, so a misreading both make
reads as agreement. The pairing is chosen because it differs in kind. The first CSV's fault follows
markup order, and a reader following the printed layout disagrees with it wherever the two part.

**`vitalsource-chrome` gains a declared exception.** Its step 4 forbids extracted page text, DOM
snapshots, and accessibility trees as evidence, and it forbids retaining long copyrighted extracts.
The exception is scoped to a two-reader code-set rebuild: a structural extraction may serve as one
of two readers and is never evidence on its own, and the retained full transcription rests on the
maintainer's written AMA permission for internal database storage. Outside that scope both rules
stand unchanged.

## Ruling 6 — the build refuses three recognizable shapes and alone sets `verified`

`tools/procedure_codes_build.py` refuses, naming the codes, a CPT input carrying any of: a
descriptor whose text before its final `; ` equals another CPT code's complete descriptor; a `;;`;
or a descriptor ending at a colon. It writes `cpt_descriptors: verified` only when the input comes
with an agreement record whose digest matches, and `unverified` otherwise, so the flag cannot be
set by hand through the build.

A wrong-parent check was refused because family membership needs the printed layout, which the CSV
does not carry; reader 2 covers that shape.

## Ruling 7 — a bulleted descriptor joins its elements with the book's bullet

A descriptor printed as a lead-in and a bulleted list is stored as the lead-in followed by each
element, each introduced by the book's own `•` glyph, in one `description` string. The `; `
separator keeps its single role as the stem boundary, so ruling 6's stacking check stays
unambiguous, and a colon-terminated descriptor with no following bullet remains a refusal.

Joining the elements with `; ` was refused because it collides with the stem separator. A separate
column for the elements was refused because it changes the schema and every reader for a few dozen
rows.

## Ruling 8 — produced output is corrected now for the codes found, then censused again

Runs that copied a defective descriptor verbatim are corrected now: each affected code is read on
its rendered page, and each unsubmitted run's worksheet line and descriptor agreement for that code
are redone. A submitted artifact is recorded, never edited. When the rebuilt database lands, the
verbatim-copy census runs again against the corrected descriptors to catch what the first pass
could not see, including wrong-parent codes. The census and its figures are measured against
gitignored run material and are reported on the tracker, never in this record.

## Ruling 9 — one build ticket and one immediate ticket

#1348 is widened to rulings 1 through 7 and the post-rebuild census. The immediate correction in
ruling 8 is filed separately because it touches run worksheets rather than the database or tools,
has an earlier deadline, and would otherwise wait behind the rebuild.

## What this record does not settle

**The reading capacity the rebuild needs.** The code set spans several hundred rendered pages, and
the screenshot reader is the slow half. This record fixes what earns `verified`, not a schedule.

**Whether HCPCS descriptors need the same treatment.** They come from the CMS machine file and no
defect has been found in them; nothing here was measured against them.
