# The session law is one grammar limb the loose spelling is refused and the legal reader states its composition

[#771](https://github.com/mshamblin5150-code/clinical-skills/issues/771) reports that a session law is unread by every legal reader and that its visible symptom has a different root. Grilled 2026-09-06. Every measurement below was taken in process at `0d3d008` with the freshness gate `FRESH`, against the artifact itself rather than against the citation string the ticket body quotes. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement falsified the ticket's headline before the first decision

**The entry is read as legal today, and not by anything that reads the session law.** #771 and [ADR 0100](0100-the-legal-source-is-a-measured-shape-plus-a-closed-vocabulary-and-the-shared-section-grammar-admits-a-state-codification.md) ruling 6 both quote the citation truncated at its listed year. The artifact's entry continues past it:

```text
Consolidated Appropriations Act, 2023, Pub. L. No. 117-328, § 1263, 136 Stat. 4459,
5683-5684 (2022) (the Medication Access and Training Expansion Act, ...; codified as
amended at 21 U.S.C. § 823(m)). https://...
```

```text
is_legal              True                       <- not False
won on                21 U.S.C. § 823(m)
resolution_keys       ('consolidated', '2022')
                      ('21 u s c 823 m', '2022')
                      ('21 u s c 823 m', '')
```

Strip the codification parenthetical and `is_legal` flips to `False`. So the reader matched a **different statute**, named in an explanatory aside, that the entry does not cite. Two consequences neither record could know: the entry's exemption from `uncited-entry` is unearned, and `resolution_keys` **manufactures two keys for a statute nobody cited**, so a body writing `21 U.S.C. § 823(m)` would resolve to this entry. That is ADR 0100 ruling 5's `('w', 2021)` mis-key with the sign flipped, and it is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape a further time: a figure measured on a partial population, reading exactly like one measured on the whole.

**The symptom row has two roots and the ticket names one.** Corpus-wide, across 80 documents with a readable reference list and 263 entries, `intext-year-mismatch` fires exactly twice, both in the M2 artifact, and **both are false alarms on correct APA**:

| finding | root |
| --- | --- |
| `consolidated cited as 2023, listed as 2022` | a year inside the statute's name |
| `new cited as 1978, listed as 2011` | APA's republished-work `1978/2011` in-text form |

The second is `(New International Version Bible, 1978/2011, Psalm 147:3)` against an entry dated `(2011)` carrying `(Original work published 1978)` — APA's documented form, verbatim, and nothing legal about it. **The row's live precision is 0 of 2.**

## Ruling 1 — the symptom leaves this ticket, because one equality is one ticket

[#816](https://github.com/mshamblin5150-code/clinical-skills/issues/816) already owns the second root and names it in its title: *APA puts two dates in text and one in the entry.* The two mechanisms differ — one puts the extra year in the entry's name, the other in the in-text citation — but **the rule that has to change is the same one**, the single-year equality between `citation.year` and `entry.year` in `_citation_findings`.

Splitting one equality across two tickets is the move ADR 0085 records as sending a builder at the wrong root. The symptom is #816's; #771 keeps *read the session law*, which is what ADR 0100 ruling 6 filed it as before the second root was known.

**The evidence transfers with it.** #816 records the symptom as `uncited-entry`; the same root also produces `intext-year-mismatch` when the in-text year parses, which is a second symptom row it does not know about. The form recurs: 13 parenthetical slash-year spans across 4 corpus documents, including `(Benner, 1984/2001)` in three drafts, beside `(4.8 percent in the 2013/2014 data)` — a non-citation parenthetical of the same shape that any candidate rule must clear.

## Ruling 2 — the session law is a grammar limb and never a Source-vocabulary row

#771 decision 3 asks *what the Source rule would be*. There is no Source rule. ADR 0100's vocabulary feeds a slot that must sit adjacent to `§`, and the session-law form puts the public-law number in between:

```text
W. Va. Code § 30-7-15a          ->  matches
Pub. L. No. 117-328, § 1263     ->  None
Pub. L. No. 117-328 § 1263      ->  None      not the comma either
136 Stat. 4459                  ->  None      no § follows it at all
```

Adding `Pub. L. No.` to `LEGAL_SOURCE_VOCABULARY` and re-running changes nothing: `is_legal` stays `False` under a windowed reader and the keys do not move. The ruled shape is a new `LEGAL_AUTHOR` alternative, `Pub. L. No. <number>-<number>, § <section>`, consuming the shared `LEGAL_SECTION_NUMBER` tail ADR 0100 ruling 3 widened.

**One written instance is the bar, and it is ADR 0100 ruling 1's own.** *It grows on a form somebody wrote, never on a family.* `W. Va. Code` entered the vocabulary on this same corpus's single evidence.

## Ruling 3 — the loose spelling and the parallel cite are both refused, and both refusals are recorded

Measured over corpus Markdown plus every tracked `.md`, ADR 0100's own population — **1,012 files, this record and this ticket's own draft excluded**:

| candidate | occurrences | real citations | false matches on prose |
| --- | ---: | ---: | ---: |
| `Pub. L. No. N-N, § N` | 2 | 1 use + 1 record mention | **0** |
| `Pub. L. No. N-N` alone | 2 | 1 use + 1 record mention | **0** |
| `Public Law` / `Pub. L.` spellings | 84 | 1 | **82** |
| `N Stat. N` | 2 | 1 use + 1 record mention | **0** |

**The exclusion is load-bearing and was found by the figure moving under its own author.** Re-derived after `main` advanced mid-session, the same three counts read 7, 93 and 8 — because a record that quotes the forms it rules on is inside the population it measures. A ratified ADR arguing from a false-match count is therefore a false match, and the next refresh of this table inflates by however many times the tree has since discussed it. The honest population is *every tracked `.md` except the records stating this measurement*, and it is named here so a later re-derivation that comes back higher is read as this shape rather than as a corpus that moved.

**The 82 are the clinician's own voice corpus**, across six files, and they take the citation shape exactly: `...amendment of 1986 (Public Law 99-457).` sits in ordinary narrative inside a parenthetical. A rule firing there manufactures a citation on correct prose, which is what #771's *What must not come out of this* forbids and what ADR 0085 measured as the danger. **Refused.**

**`136 Stat. 4459` is refused although it measures clean**, and the reason is structural rather than statistical. It is a **parallel citation** — the same enactment located in the Statutes at Large — not the authority. Admitting it would put a second legal span inside the one entry this record is about, reintroducing the multi-match condition ruling 4 declares.

**A refusal whose object has no name is one the next session re-proposes**, so both are named in the glossary and both are rows of the object ruling 5 renames.

## Ruling 4 — there is no span window, and the leftmost ordering is declared rather than guarded

The obvious repair is to window the legal search to the text before the entry's listed year. Measured, it is a rule with no case:

```text
entries examined, table rows excluded                129   (110 carry a bare (Year))

                                            without limb A     with limb A
is_legal, searching the whole entry                     18              --
is_legal, windowed to before the listed year            17              --
entries whose ONLY legal match sits after the year       1               0
entries carrying more than one legal match               0               1
```

**The two columns are one entry moving between them, and stating a single column would misread the window's value in either direction.** Without limb A the M2 entry's only legal match *is* the codification aside, so the window looks decisive — it is the one verdict of 129 that changes. With limb A the act's own cite appears before the aside, so the entry becomes the corpus's only multi-match and leftmost already resolves it. **A table mixing the two says the window fixes an entry that limb A has already fixed.** A first draft of this record did exactly that, and it was caught by re-deriving after `main` moved rather than by reading.

`re.search` returns the leftmost match and the act's own cite is written before the codification aside, so **limb A alone flips the entry to the right span and the right keys with no change to the span logic at all**. The window would then change zero entries.

This repository has already ruled on that shape: *a second mechanism that cannot fail is not a belt and braces; it is a line that costs a test.* So no window is built, and `LEGAL_READER_NOT_REACHED` states instead that the reader takes the leftmost legal span and cannot distinguish an entry's authority from a **codification cross-reference**.

**The two-window disagreement is declared latent rather than repaired.** `_legal_match` reads the whole entry and `reference_keys` reads only the text before the listed year — two readers of *is this legal* over different substrings, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape. Because no corpus entry has its only legal match after the year, they agree everywhere today. That is ADR 0128's arrangement whole: a latent join, declared and kept read that way, checked on the day it is revisited rather than guarded against a shape nobody writes.

## Ruling 5 — the declared-limit object is renamed, and it holds the span row beside the Source row

`LEGAL_SOURCE_NOT_REACHED` becomes **`LEGAL_READER_NOT_REACHED`** and gains the two rows above: the refused Source forms, and the leftmost-span ordering. A span row filed under a name about *Sources* is a row nobody looks for, and this repository's recorded failure is a declared limit whose name lets a reader stop reading it.

**The rename does not touch ADR 0100 ruling 7's argument**, which was never about the word *Source*: it was that the limit moves into code beside the grammar it describes, because that grammar has three consumers and a per-consumer copy is #220. The object is one merge old and carries one row, so the rename is at the cheapest it will ever be. This record supersedes ruling 7's sentence naming it, which is the same move ruling 7 itself made to [#751](https://github.com/mshamblin5150-code/clinical-skills/issues/751)'s §8 label.

`apa7.md` §8 points at the new name and enumerates no row of it, both directions bound by a test, unchanged in arrangement from ruling 7.

**The rename moves four places and no fewer, and this record proved that by getting it wrong.** The name is written in `discussion_artifact.py`, in `apa7.md` §8, twice in `tools/test_reference_scan.py`, and in `CONTEXT.md`. The commit that ruled the rename applied it **to `CONTEXT.md` alone** — so the glossary named a symbol that does not exist, `hasattr` returned `False`, and **297 tests passed**. #220's shape, arriving inside the change that ruled the rename, in the one direction nothing checks: a prose pointer at a code object fails nothing when the object is not there. The glossary is reverted to the name that exists and the rename is the build's, all four at once.

**And the rename does not put the object inside the repository's limits walk.** `test_declared_limits.declarers()` is keyed on the literal module-level name `DECLARED_LIMITS` and enumerates 18 modules; `discussion_artifact` is not one of them, before the rename or after it. **So this is a third naming convention for a declared-limits object and it is the one convention no walk sees.** That is declared here rather than repaired: bringing it inside the walk is a decision about the walk's population — whether it is `DECLARED_LIMITS`-named or limits-*shaped* — which belongs to [#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867) and [#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875) rather than being settled in passing by a ticket about a session law.

## Ruling 6 — the coverage line states a derived composition, because a third mechanism makes a typed one false

Both graders print, each from its own copy of the sentence:

```text
legal Source vocabulary: closed at 2 listed mixed-case forms; title-number uppercase
codes are read by shape.
```

The **figure** is derived from `len(LEGAL_SOURCE_VOCABULARY)`; the **composition** is typed. Limb A is neither a listed mixed-case form nor a title-number uppercase code, so that sentence goes from true to false the moment the limb lands, silently, in two modules — and a typed third clause would force the word *shape* onto a fixed structural form that is not one.

The mechanisms become a declared tuple the grammar is built from, and both the count and the mechanism names are read off it:

```text
legal reader coverage: 3 mechanisms -- title-number uppercase codes by shape,
2 listed mixed-case Source forms, 1 fixed session-law form.
```

That is `spelling_scan.vocabulary_covered`'s arrangement whole, **including its recorded correction**: that scanner printed a total the table a reader counts disagreed with, and the repair was to name the composition from the same structures the matcher iterates. ADR 0100 ruling 7's split survives — each grader keeps its own copy of the sentence, both read the composition off the one object — because a mechanism list is a figure wearing a sentence's clothes.

**The reconciliation test is an AST walk and never a substring search**, on `test_console_codec.py`'s instrument and for its reason: the substring form is what that module records passing on a docstring.

**The walk must reconcile the two copies with each other, and not only each copy with the shared object.** The two functions are **byte-identical today** — 312 characters including the docstring, `tools/reference_scan.py:1304` and `tools/discussion_post_scan.py:1014` — and **nothing binds them**: neither test module imports the other's, and each asserts only its own report. Ruling 6 orders the same edit to both. Two byte-identical blocks edited on two branches is this repository's recorded [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) trap verbatim — *the two `**24**`s were byte-identical, so git merged that one silently and the count was wrong in a tree neither branch had ever produced.* A walk that checks each copy against the mechanism tuple passes both halves of that merge. **Only a copy-to-copy assertion closes it**, and it is cheap because ruling 7 of ADR 0100 already ruled the two sentences are deliberate copies rather than an accident to be extracted.

**Whether the function should be one object rather than two copies is deliberately not ruled here.** Both copies import `LEGAL_SOURCE_VOCABULARY` from `discussion_artifact`, so the placement answer looks obvious — but ADR 0100 ruling 7 ruled the *sentence* copied on purpose, and reversing that is a decision about the two graders' independence rather than about a session law. It belongs to [#835](https://github.com/mshamblin5150-code/clinical-skills/issues/835), where the duplicate-helper decision is already open and where this pair is now recorded as its strongest instance: two **production** functions with the same name and the same bytes, held in step by nothing.

## Ruling 7 — the glossary widens to enacted law, and both asides are named

`CONTEXT.md` defines **Legal reference entry** as *a reference for codified law* and **Legal citation** as *an in-text reference to codified law*. **A session law is not codified law** — that is the whole distinction between the Statutes at Large and the U.S. Code — so the glossary as written excludes the thing this record rules on.

Both widen to *enacted or codified law*. The alternative, a `Session law` term standing as a peer, was refused because the code holds a single concept: one `is_legal`, one `LEGAL_READER_NOT_REACHED`, one §8 form, one `legal` reference bucket. A glossary with two peers would describe a distinction the tree does not make.

Two terms are added because both are now ruled on:

- **Codification cross-reference** — a legal citation inside a reference entry that is not that entry's authority. Its limit is ruling 4's, so the glossary points at `LEGAL_READER_NOT_REACHED` and keeps no second copy.
- **Parallel citation** — a second locator for the same enactment. Ruling 3 refuses it.

## Ruling 8 — ADR 0100 ruling 6's verdict holds and its table is superseded, and the two are not the same act

Ruling 6's measurement:

```text
session-law limb absent    is_legal=False   findings ['intext-year-mismatch']
session-law limb present   is_legal=True    findings ['intext-year-mismatch']
```

Re-derived against the artifact:

| row | verdict |
| --- | --- |
| `is_legal=False` | **false about the artifact.** True only of the truncated string both records quote. |
| `is_legal=True` | true, but not by the mechanism pictured — ruling 2 measures that a vocabulary widening cannot match the form at all. |
| *does not cure the symptom* | **holds**, independently re-derived, now with a second root and a second symptom row behind it. |

**A right conclusion resting on wrong evidence is a different failure from a conclusion overtaken by later work**, and this repository already has a sentence for the second one — ADR 0100 ruling 3's *a later reader comparing ADR 0085's* What none of this reaches *against a grammar that reaches it should read neither record as wrong.* Filing this under that sentence would launder a measurement error into a supersession and teach the next reader the wrong lesson. So ruling 6's verdict is preserved and re-derived, its table is replaced, and the reason they differ is stated here rather than left to be discovered.

The earlier record is not edited. That is this repository's practice — ADR 0100 ruling 3 and [ADR 0134](0134-the-guideline-currency-check-is-per-society-reads-what-its-publisher-lists-and-refuses-to-repoint-a-sheet.md) both supersede prose rather than rewriting the record they correct, and editing a ratified ADR would make its merge receipt point at text that no longer exists.

## What none of this reaches

**Whether an in-text year must equal its entry's year.** Ruling 1 hands that to #816, with two roots and two symptom rows attached. Nothing here changes `_citation_findings`, and the M2 artifact still reports both findings after every ruling above.

**A session law written in any other form.** One instance grounds limb A, and a second spelling is invisible until somebody writes one. That is the standing price of ADR 0100 ruling 1's second limb arriving at a third mechanism, declared in code under ruling 5.

**An entry whose authority is written after a cross-reference.** Ruling 4 declares the leftmost ordering rather than guarding it, so `Amendments to 42 C.F.R. § 482.23, W. Va. Code § 30-7-15a (2024)` would key on the cross-reference. Nothing in 129 corpus entries writes that shape.

**Whether the cited section says what the draft claims.** The refutation pass owns it, with no carve-out for legal primary sources. Nothing here reads a statute.

**Whether the entry is correct APA.** It is submitted, graded work. Every finding recorded here is a record of what the reader cannot see, never an instruction to edit it.
