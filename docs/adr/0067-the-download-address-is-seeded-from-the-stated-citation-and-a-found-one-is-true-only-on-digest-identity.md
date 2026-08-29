# The download address is seeded from the stated citation and a found one is true only on digest identity

[#512](https://github.com/mshamblin5150-code/clinical-skills/issues/512) was ruled on 2026-08-27 and
recorded as [ADR 0047](0047-a-corpus-document-s-stated-citation-is-read-off-its-own-page-and-a-link-is-not-one.md).
[ADR 0057](0057-the-corpus-sweep-is-comprehensive-and-every-ruling-it-needs-is-already-ruled.md)
ruling 6 then ordered a second catalog column and deferred the reconciliation in its own words —
*"that record is read before this is built rather than after."* This is that reading.

Grilled 2026-08-29, against `origin/main` `87b2ed9`. The clinician ruled every point below on the
same day. **Nothing is built here; this is the record the build reads.**

It spans two tickets. #512 owns rulings 1 to 4; [#551](https://github.com/mshamblin5150-code/clinical-skills/issues/551)
owns rulings 5 to 11. They stay two tickets and the design lives here, so neither body restates the
other's half.

## The denominator ADR 0057 ruling 6 rests on had already been retired

Ruling 6 priced its column at **33 topics** whose documents print nothing on **page 1**. ADR 0047's
column admits a locator read at **any** page, which rescues most of them. Re-derived 2026-08-29 by
scanning the extracted corpus for the first DOI per document. **These figures are counted against a
corpus outside every checkout and nothing committed re-derives one.**

| | first own-locator | disposition |
| --- | --- | --- |
| KDIGO 16 of 18 | a DOI at pages 10–25, the Foreword publication line | covered by `Stated citation` |
| ACIP 3 of 3 | its own printed capture URL | covered — ruling 2 |
| ADA, CDC, GOLD | page 7 is the *introduction's* DOI, page 30 and page 197 are reference-list DOIs | residue — ADR 0047's recorded trap |
| GINA | none; `www.ginasthma.org` is a masthead | residue |
| KDIGO draft, KDIGO scope-of-work | none; the page-397 hit is a reference | residue, and the scope-of-work is a declared non-source under ADR 0057 ruling 8 |

**Six documents, and each carries exactly one catalog topic** — diabetes mellitus, opioid prescribing
for pain, asthma, chronic obstructive pulmonary disease, acute kidney injury and acute kidney
disease, heart failure in chronic kidney disease. So the hoist saves six lookups and not 33, there is
no repetition across topics for it to prevent, and no risk of two sessions writing two addresses for
one document. **That is the whole ground of ruling 1**, and it was measured rather than argued.

## What is ruled

1. **ADR 0057 ruling 6 is superseded. The catalog gains `Stated citation` and nothing else.** A
   second column was bought to avoid 33 inventions that are six, and the six are precisely the
   documents where a hand-found value is worst — two are registration-gated and one is a 377-page
   compilation. The residue takes `?` with its `## Unsettled cells` reason, which is ADR 0047
   ruling 6 already. A pointer beside ruling 6 in ADR 0057 records the reversal, so a reader
   arriving at that number finds it.
2. **The three ACIP captures' printed URLs are admitted to `Stated citation`, read against the
   rendered PDF page.** They are the only documents in the corpus where ADR 0047 ruling 2's *a URL
   where the document prints one* limb can fire; left out it is a dead letter and three documents
   take a `?` while printing their address on every page. **The audit row states the rendered page**,
   on [ADR 0043](0043-a-rendered-cell-is-a-page-transcription-and-its-marker-records-the-read-rather-than-an-extraction-failure.md)'s
   posture, because the boilerplate strip removes the URL from the extracted text — verified
   2026-08-29, no `http` in any of the three `.txt` files — so a reader auditing from extracted text
   would report it missing.
3. **Link rot earns no stamp and no check.** A dated `last-checked` cell attaches a date to an act
   nobody performed and would read as verification. One keyed sentence joins ruling 12's
   declared-limits object: a printed URL can cease to resolve where a DOI is designed not to, and
   neither has been opened.
4. **This record supersedes rather than corrects.** [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
   permits correcting a ratified record's *facts* in place; reversing a *ruling* is a different edit.
   Folding rulings 5 to 11 into ADR 0047 was refused for a second reason — that record is dated
   2026-08-27, and dating decisions made today to a day they were not made is the record falsifying
   itself.
5. **A drafted sheet's `url` is never a path on the maintainer's machine.** `threshold_draft`'s
   `file:///` limb is deleted. The value is **seeded** from the document's `Stated citation`: a DOI
   becomes `https://doi.org/<doi>`, a printed URL is used verbatim, and a journal citation line
   seeds nothing because it is not an address. `_seed_sources` already calls
   `guidelines_catalog.parse_catalog` and is holding the row at the line the fallback fires, so the
   seed costs no new read.
6. **A seed is not a bind, and this record says so in as many words.** ADR 0047 ruling 11 refuses
   *forcing* a sheet onto the corpus copy's DOI, on `hypertension.md`'s measurement. A default a
   person overwrites is what that sheet's author did by hand. Without this sentence the next session
   reads ruling 5 as violating ruling 11.
7. **Where nothing seeds, the agent goes and finds it.** Refusing would put the clinician back at the
   bottleneck, which is the cost this whole toolchain exists to remove. **No tool gains a socket** —
   ADR 0047's own words are *the honest form is no tool opens a socket, not no route exists*, and
   [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) established the nine corpus
   societies were publicly downloadable. It is six lookups, once.
8. **A found address is a true match only on digest identity.** A title match is not enough. The
   agent fetches and compares against the `sha256` the audit ledger already commits, so the evidence
   it leaves is re-derivable by anyone holding the file. **This reverses ADR 0047's decision-reason 1
   for these rows** — *the repo has no instrument that could ever grade one* is false once the test is
   a digest comparison against a committed value. Three outcomes, not two: matched; reachable and
   different, which is a finding and is ADR 0031's corpus drift arriving from outside; and
   unreachable.
9. **The authenticated route is a required attempt before a wall may be recorded.** GOLD and GINA
   gate downloads. [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
   ruling 5 already makes that route a required attempt rather than an option, so the wall is a
   measured finding rather than an assumption. **This deliberately overrides ADR 0042's `paywalled`
   posture for this artifact**: there a matching title and authors is evidence enough, and here it is
   not. Recorded as deliberate so the two records are not read as contradicting.
10. **Two evidence kinds, matched to two provenances, in a closed vocabulary of four.** `stated` —
    seeded from the document's own printed citation, already audited on the catalog. `digest <date>` —
    fetched, bytes matched. `gated <date>` — authenticated route attempted, download still gated,
    title matched. `chosen` — a person deliberately picked a different-but-correct address. A single
    rule was refused: a seeded DOI resolves to a landing page rather than to the bytes, so demanding a
    digest of it fails a correct value for a property the rule does not care about, which is
    [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s recorded defect. It
    would also make the six documents that cite nothing the best-evidenced rows in the artifact and
    the 163 that print their own DOI the worst.
11. **The concept is `Download address`, the column stays `url`, and the new column is `basis`.**
    `locator` carries a live tested definition in `research_ledger` — *a URL or a bare DOI, and
    nothing else* — and `mode` already holds `exact`/`bound`, so both are taken. The term is the
    clinician's own word for it. #551's decision 2 asked for a glossary term rather than a rename,
    and the `## Sources` parser reads by header name, so renaming would migrate four shipped sheets
    and buy nothing. **The five shipped URLs are back-filled** rather than landing the column reading
    `unverified` five times out of five, which is ADR 0047 ruling 10's objection.

## Appending to `## Sources` is safe, and the catalog is why that had to be checked

ADR 0047 ruling 8's enumeration of the catalog's positional readers was short three times in one day,
so the same question was asked of the table this record adds a column to. `tools/threshold_sheet.py:964-968`
carries a comment recording that `mode` was `cells[-1]` and that appending would have silently
redefined the cell deciding refuse-versus-warn. It reads by **name** against the header row now, with
position only as a fallback, so a named column appends safely and costs one `named.get(...)` line.

That is the opposite of the catalog, where `corpus_census.CATALOG_CELL_COUNT == 10` matches no row at
all once a ninth column lands. **The two tables have opposite tolerances and the difference is not
visible from either one**, which is why it was measured rather than assumed from the sibling.

## What was refused

- **A resolver.** Unchanged from ADR 0047 and #231. Ruling 7 puts the socket in the agent, which is
  where the research fan-out already has one.
- **A `last-checked` stamp.** Ruling 3. A date attached to an act nobody performed.
- **A catalog `url` column.** Ruling 1, on the six-document measurement.
- **One evidence rule for every row.** Ruling 10, on #215's ground.
- **Softening the digest test to tolerate a re-encode.** Bytes differing is not proof content differs
  — a re-encode or an embedded timestamp moves the hash — so byte-identity is sufficient for a true
  match and not necessary. Refusing on bytes anyway, because it is the line that cannot be argued
  with, which is [#198](https://github.com/mshamblin5150-code/clinical-skills/issues/198)'s posture in
  `skills_mirror`. The limit is declared rather than the test weakened.
- **Merging #512 and #551.** They were split on a stated line — different file, different column,
  different question — and #551's body says *"Do not refile it as that."*

## What none of it reaches

**A digest match proves the bytes are the ones audited. It proves nothing about whether the address
will still serve them tomorrow, and nothing at all about the 163 rows that carry `stated`** — for
those, two people will have read the same string off a page and nothing will have opened one, which
is ADR 0047's own closing sentence and is unchanged here.

A `gated` row is the weakest that ships: a title matched behind a wall, with the authenticated route
attempted and no bytes compared. It is recorded as its own value precisely so a reader cannot mistake
it for a `digest`.
