# The topic section names the declared-field route alone and the filename route is guarded by a corpus-free tripwire

`reference/guidelines-uspstf.md` derives its `Topic` column three ways and marks none.
`uspstf_table.derive_topic` reads page 1's title, falls back to the PDF's own declared title
field, and falls back again to the filename slug.
[#656](https://github.com/mshamblin5150-code/clinical-skills/issues/656) is that residue, filed
out of [#545](https://github.com/mshamblin5150-code/clinical-skills/issues/545)'s grilling
because its remedy has to answer a question #545's did not.

Grilled 2026-08-30 against `origin/main` at `ac6f48a`, freshness gate `FRESH` at both
checkpoints. The clinician ruled all nine points below. **Nothing is built here; this is the
record the build reads.**

## The measurement, re-derived twice in this session

Corpus-bound, against `C:/codeing/guidelines-text` under `--allow-untrusted-provenance`,
re-running the branches of `derive_topic` per document and asserting each reconstruction
equals what the function returns:

```
USPSTF documents read: 90
  route page     : 87
  route metadata :  3   Thyroid Cancer (JAMA capture), autismfinalrs.pdf, rhrs.pdf
  route filename :  0
```

Corpus-free, against the committed artifact alone, computing the filename route from the `File`
cell:

```
rows read 143   distinct files 90   distinct topics 90
rows whose Topic equals the filename derivation of its File   1
  of those, page-route documents      0  (of 87)
  of those, metadata-route documents  1  (Thyroid Cancer)
  of those, filename-route documents  0
nearest non-identical Topic/slug similarity   0.75
```

**The corpus figure is not re-derivable from anything committed** and the method is stated here
rather than a number being trusted. The corpus-free figure is re-derivable in any clone and is
what ruling 4 rests on.

## Findings this grilling produced

**These are numbered `Finding N` and the rulings below are numbered `N`, deliberately** —
[ADR 0069](0069-a-field-quotation-is-listed-as-a-population-and-document-pair-and-the-disclosure-collapses-to-one-consumer-facing-site.md)'s
arrangement, adopted for its reason: a record numbering both `**N.**` makes *"ruling 3"* resolve
to two real items under a bold-shape extractor.

**Finding 1. `Topic` is one value per document, and `Population`'s hardest complication has no
analogue here.** 90 files, 90 distinct topics, no file carrying two, no two files sharing one, no
empty cell. ADR 0069 needed a `(Population, File, Page)` key and two rendered counts because a
population varies within a file and two files can share one; here an entry is a topic and its
file, the three documents contribute 4 rows, and the *"15 rows form 13 pairs"* two-figure problem
that ruling 3 and ruling 4 exist to solve cannot arise.

**Finding 2. The ticket's impossibility claim is wider than what it measures.** Its body reads
*"no instrument in a clone can tell which route produced a `Topic` cell."* That is true of the
page-title-versus-declared-field distinction, whose inputs the artifact ships neither of. It is
**false of the filename route**, whose only input is the `File` cell. The filename route's output
is computable in a clone, and a document that took that route produces, by construction, exactly
the string the computation returns — so the detector has **no false-negative direction at all**.

**Finding 3. Routes 2 and 3 produce the same string for the Thyroid Cancer capture, which is why
the corpus-free signal has one collision rather than zero.** The browser named the file after the
page title, and `TITLE_STOP` cuts both at the Task Force masthead:

```
metadata -> 'Screening for Thyroid Cancer'
filename -> 'Screening for Thyroid Cancer'
```

`autismfinalrs.pdf` and `rhrs.pdf` do not collide — their filename routes would return
`autismfinalrs` and `rhrs`. The collision is a property of one web capture's naming, not of the
rule.

**Finding 4. The ground the ticket rests on is not the ground ADR 0069 ruled on.** That record's
ruling 1 says the impossibility motivation *"was withdrawn"* and what survived was **a derivation
is not a record** — differencing runs the *current* function against a table built by a *possibly
different* version of it, and nothing announces when the two stop agreeing. That argument never
mentions recoverability, so it transfers to `Topic` untouched and the impossibility question does
not decide whether the section exists.

**Finding 5. The disclosure shape is the opposite of `Population`'s, and ruling 5 there does not
transfer.** The topic rule is written in three places and **none of them is consumer-facing**:
`derive_topic`'s docstring, `uspstf_table`'s module docstring, and `CLAUDE.md`'s #108 paragraph.
The artifact header says nothing about how `Topic` is derived and neither does
`skills/clinical-note/SKILL.md`. ADR 0069 ruling 5 collapsed six sites and two consumer-facing
statements; here the problem is a **gap**, not duplication — and separately, two of the three
sites carry the count `three` in prose that nothing re-derives.

**Finding 6. #656's decision 2 offers an option that is not one.** It proposes *"emitting the
route into the artifact at build time so a check has something to read."* A check that reads back
a route label the build wrote has established that the build wrote what the build wrote. ADR 0069
ruling 7 already named the weaker form of this — tier 1 there shares `derive_population` with the
producer — but tier 1 there still recomputes from the **statement**, which the artifact ships.
Here there is no independent input, so writing the route down relocates an unchecked claim rather
than making it checkable.

## The ruling

**1. The `Topic` column gets a generated section, on ADR 0069 ruling 1's ground and not on
#656's.** The deciding argument is *a derivation is not a record*: a generated section is stamped
at build time and cannot drift from the table it ships in, while a re-derivation checks today's
function against yesterday's artifact. **Recoverability is not the reason** — Finding 4 — which
matters because #656's framing would have made the section's justification collapse the moment
Finding 2 landed.

The counter was weighed and rejected: this is 3 of 90 where `Population` was 15 of 143, and a
`Topic` never reaches a note, since `guidelines_recs.CuratedRow` hands `population` to a run and
does not hand `topic` to one. A wrong topic is a navigation error. That lowers the stakes and does
not touch the drift argument.

**2. The section names the declared-field route alone, and the filename route is excluded in
writing.** Heading `## Topic cells quoted from the declared field`. Three entries today.

**The wider class was refused because it fails in the direction that matters.** A class reading
*topic not read from the document's own page* would cover both fallbacks and would let a future
web capture — `Topic` reading `some print job 2019 final` — join the list looking exactly like a
quotation from the document. **The route that most deserves to be loud is the one the wider class
makes quietest.** A declared title field is the document's own words; a filename slug is whatever
a browser or a curator named the file, and those are different strengths of evidence.

**A per-entry route column was refused too.** It would publish a column that is constant across
every row today, which is a column a reader learns to skip, and it would coin vocabulary for a
route with no members.

**3. The exclusion is written now, while it is a no-op.** ADR 0069 ruling 8's arrangement and its
reason: the distinction is currently untestable against the artifact, and the next corpus refresh
is what would publish a false claim in a public-domain artifact. It is a code-level guard and a
preamble sentence, **not a published column** — which is exactly what ruling 8 did for
`not stated` and is why that ruling is the precedent rather than a column-shaped one.

**4. The filename route is guarded by a corpus-free tripwire instead of by a list entry, and that
is what makes ruling 2 safe.** No unlisted row's `Topic` may equal the filename derivation of its
`File`.

**It cannot miss a member.** A document that took the filename route produces precisely the string
the tripwire computes, so the check has no false-negative direction — Finding 2. Its only failure
mode is a false alarm from a coincidental collision, measured at **0 among the 87 page-route
documents**, 1 among the metadata-route three, and that one is Thyroid Cancer, which the section
lists and which is therefore excluded. The nearest non-identical pair sits at 0.75 similarity.

**So #656's decision 3 is answered by not marking.** The filename route is not marked, is not
invisible, and needs no second term. ADR 0069 ruling 9's *"decision 3 still needs a second term if
route 3 is ever marked"* is satisfied by the antecedent being false.

**The cost is declared rather than hidden**: a future page-route document whose real title happens
to equal its own cleaned filename fires the tripwire with nowhere to be listed. That is not zero
in principle. It is zero over today's corpus and the nearest approach is not close.

**5. The section is graded in two tiers, and the tier boundary is *not* ADR 0069's.**

**Tier 1, corpus-free, in CI.** Every named file appears in `## Recommendations`; every named
topic equals that file's `Topic` cell; entries are unique; the preamble's count is rendered from
`len()` and never typed; and **no unlisted row's `Topic` equals the filename derivation of its
`File`** — ruling 4's tripwire, the one limb here that grades a claim rather than bookkeeping.

**Tier 2, where the corpus is, skipping with a banner that survives `--quiet`.** Membership is
re-derived — the listed set is exactly the documents whose page-1 title fails
`_looks_like_a_title` and whose declared title passes — and each listed topic equals
`derive_topic`'s return verbatim.

**6. The downgrade against ADR 0069 is declared, and it is the narrow true form of #656's
impossibility claim.** For `Population`, tier 1 established **membership** exactly, at zero error
over 143 rows, so the central claim ran in CI. **Here it cannot.** Membership moves entirely to
tier 2, so on a machine with no corpus the section's central assertion — *these three documents
took the declared-field route* — is not graded at all.

The impossibility therefore blocks **corpus-free membership grading, specifically.** It does not
block the section, and it does not block checking:
[threshold_sheet.py](../../tools/threshold_sheet.py)'s *there is no machine on which checking
drops to zero*, which ADR 0069 ruling 6 adopted in this module, still holds, because ruling 4's
limb is real and corpus-free.

**7. Two positive controls, because a check nobody has driven red is measuring nothing.** ADR 0069
ruling 7 required a named mutant for this reason and its own mutant does not transfer, there being
no withdrawn figure here to reproduce.

- **Tier 1 liveness.** A synthetic unlisted row whose `Topic` equals its filename derivation must
  turn tier 1 red. Free, needs no corpus, and it is the control for the limb the whole of ruling 2
  rests on.
- **Tier 2 liveness.** Substituting a page-route document for a listed entry must turn tier 2 red,
  so membership re-derivation is not vacuous.

**8. Four dispositions across the disclosure sites, one per site.**

- **`derive_topic`'s docstring — untouched, and named as the owner.** ADR 0069 ruling 5's
  treatment of `derive_population` verbatim: the only site where the rule and the code applying it
  cannot drift apart. **Its *"twelve of the ninety"* stays and must not be reconciled with three**
  — it counts how often the manifest title field is missing or reads `JAMA`, which is a different
  question from how often that field was used.
- **The artifact header's pointing clause, generated in `render_markdown`, gains `Topic`.** That
  sentence already names two sections and a third joins it rather than earning its own. A section
  nothing points at is one a reader does not know to look for, which is most of why it exists.
- **Both prose copies of `three` collapse to the rendered count, each site keeping its own local
  work.** The module docstring's point is that the manifest title field is a required part of the
  handoff and not decoration; that stays, without a numeral, pointing at `derive_topic`, because a
  docstring points at the function that decides. `CLAUDE.md`'s #108 paragraph states *why* —
  browser chrome, a page opening with the recommendation, a page extracted without space glyphs —
  and those three causes are not in the section and are worth keeping; only the numeral goes. The
  count becomes the section's, rendered from `len()`, on ADR 0069 ruling 4's rule.
- **`skills/clinical-note/SKILL.md` gains nothing, deliberately.** ADR 0069 ruling 5 kept the
  population sentence there as a *second* consumer-facing statement because its work is a clinical
  caution: a population decides care and a run copies that cell verbatim in front of a preceptor.
  `Topic` decides navigation and no run copies it. **The symmetry is the trap, so it is named here
  rather than left for someone to complete.**

**9. No new glossary term is coined, and that is ADR 0069 ruling 9 working as designed.** That
ruling wrote **`Field quotation`** *"general to the artifact so the `Topic` ticket inherits
vocabulary instead of coining a rival"*, and its `CONTEXT.md` entry — *"a cell quoted from a
structured field the document declares, where the column's rule primarily reads a passage of its
prose"* — covers the declared-title route unchanged. Ruling 2 means the filename route is never
marked, so the second term that ruling contemplated is not needed. **`CONTEXT.md` takes no edit.**

## Consequences

**The rebuild is paid alone, and there is nothing left to co-land with.** `reference/guidelines-uspstf.md`
sits in `artifact_provenance.CACHE_IDENTITY["recs"]`, so any byte change refuses every
`curated-table` recommendation record until re-produced —
[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md)
ruling 2, priced by
[ADR 0045](0045-the-recommendation-sweep-is-a-third-cache-stage-its-records-are-keyed-on-doc-id-and-a-document-that-yields-nothing-declares-itself.md)
at **56 minutes of CPU for 179 byte-identical records**. ADR 0069 ruling 10's co-lander is gone:
#545 and #505 both closed at `061002f`, and the only open ticket naming this artifact,
[#512](https://github.com/mshamblin5150-code/clinical-skills/issues/512), **reads** the table to
ask whether a URL can be reconstructed from `filename` and `page` rather than writing to it.
Ruling 10 there already framed co-landing as *"a saving and not a sequencing constraint"*, so its
absence is not a reason to hold a ruled ticket on an unfiled one. **If #512 later adds a column,
the sweep runs twice**; that was weighed and accepted.

**The section is two cells wide and is safe from `differential_scan._uspstf_index` by width.**
That parser walks the whole artifact anchored to no section and mints a citation row from any
**nine**-cell row whose third cell is a grade and fifth a four-digit year. This section carries a
topic and a file and **no `Page`** — the topic is one value per document and the declared-field
route reads no page at all. ADR 0069 ruling 11 asked in as many words that the next author of a
generated section in this file *meet* that hazard rather than discover it; this is that author
doing so. The fix belongs to
[#641](https://github.com/mshamblin5150-code/clinical-skills/issues/641) and this build only
records the encounter.

**Nothing downstream changes.** `parse_curated_table` and `CuratedRow` are untouched, the
`## Recommendations` table stays nine columns wide, and no character enters any string a note
copies.

## What no limb reaches

**Whether a listed topic is the *right* name for the document.** Tier 2 establishes that the cell
is the document's declared title verbatim; whether that title describes the recommendation a
reader is hunting for is a reading. **A listed entry is a provenance claim, never a naming
judgment.**

**Whether an unlisted topic came from page 1 or from the declared field.** Only tier 2 separates
those, so on a corpus-free machine the section's membership is asserted and not graded — ruling 6.

**A page-route document whose title coincidentally equals its cleaned filename.** Ruling 4's
tripwire would fire on it with nowhere to list it. Zero today, and the honest form of the guard is
that its false-alarm direction is open while its false-negative direction is closed.
