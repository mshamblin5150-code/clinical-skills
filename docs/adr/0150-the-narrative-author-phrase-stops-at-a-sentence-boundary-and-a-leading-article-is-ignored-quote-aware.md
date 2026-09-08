# The narrative author phrase stops at a sentence boundary, and a leading article is ignored quote-aware

[#913](https://github.com/mshamblin5150-code/clinical-skills/issues/913) reports that `reference_scan` keys a narrative group author on the phrase's **last** word and its reference entry on the **first**, so one correct APA citation raises `uncited-entry` and `unlisted-citation` together. Grilled on 2026-09-08. Every measurement below was taken in process at `ba2fe5b` with the freshness gate `FRESH`, over the 80-document population — `output/` plus `scratch/`, which is exactly the ticket's own 80. **Nothing is built here; this is the record the build reads.**

## The clinician's standing ruling, made in this session

Minimum necessary, buildable today. **No new tickets were filed from this grilling.** Findings outside this ticket's root are recorded as comments on tickets already queued, never as new work.

## APA's own page settled two questions the tree had been guessing at

ADR 0145 ruling 2 already records that `apastyle.apa.org` is reachable and that ADR 0039's Imperva caveat is a fact about the fetch tool. That holds and is not re-ruled here. It was re-confirmed the hard way: WebFetch returned empty bodies, `curl` — plain and with full browser headers — got an Incapsula interstitial at HTTP 200, and a real browser loaded the page. **A 200 of 212 bytes is worse than a 403**, and only the browser distinguishes them.

The page is [How to alphabetize "a," "an," and "the" in APA Style references](https://apastyle.apa.org/blog/alphabetize-nonsignificant-words) (McAdoo, 2022). Its reader question is the group-author case *by name* — whether `The Smithsonian Institution` files under T or S — and APA answers **"We ignore the three nonsignificant words … at the beginning of an author name."** It is not an inference from the title rule; APA states the two separately on the same page and they agree.

Two facts fall out, and the second is the trap:

| | reference entry | parenthetical | narrative |
| --- | --- | --- | --- |
| group author | `The Smithsonian Institution.` filed under **S** | `(… The Smithsonian Institution, n.d.; …)` | `The Smithsonian Institution (n.d.)` |
| title in author position | `The Beatles.` filed under **B** | `("The Beatles," 2022)` | `"The Beatles" (2022)` |

The article is **retained everywhere it is printed** and ignored **only for sort position**. And a title in the author position takes **quotation marks** where a group author stays bare — which is what makes the article strip quote-aware rather than naive.

## Ruling 1 — the phrase boundary moves, and neither key moves

`read_citations.add` already routes through `citation_key`, which reduces to the first word. The defect is entirely that `NARRATIVE`'s `\b` starts the match at the **last** capitalized word. Widening the capture to the whole phrase makes the narrative key equal `Entry.key` with **no change to `Entry.key`, no change to `resolution_keys`, and no new key vocabulary** — so ADR 0039's prohibition on keying the `a`/`b` rows on a resolution key is untouched by construction rather than by care.

**The boundary rule is a measurement, not a judgment.** Three candidates over the 80 documents:

| rule | matches | crossings | lost | keys moved |
| --- | ---: | ---: | ---: | ---: |
| current | 236 | 0 | 0 | 0 |
| `discussion_artifact`'s `AUTHOR_PHRASE`, transplanted | 236 | **1** | 0 | 3 |
| restrict `NAME` to non-sentence-ending tokens | 224 | 0 | **12** | 15 |
| **adopted** — refuse a *continuation* across a lowercase-letter-then-period | **236** | **0** | **0** | **3** |

The adopted rule leaves `NAME` untouched and refuses only the continuation step, so `Virginia.` stops the phrase and `U.S.` does not, and a lone `Epictetus.` still matches because nothing continues it — which is why the third candidate lost 12 and this loses none. The three keys that move are the three that were wrong.

**The patterns the measurements were taken with are recorded here rather than in the ticket**, because a ticket is maintained and a dated record is not — so a second live copy of a rule is what [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) refuses, while a measurement stated once beside what it measured is what this file is for. The ticket carries the property and points here.

```python
NOT_SENTENCE_END = r"(?!(?<=[a-z’']\.)\s)"
CONNECTORS       = ("of", "for", "the", "and", "&", "on", "in", "at")   # never "to"
PHRASE           = NAME + r"(?:" + NOT_SENTENCE_END + r"\s+(?:" + NAME + r"|" + "|".join(CONNECTORS) + r")){0,10}"
ARTICLE          = re.compile(r"^(\s*[*_\"'“‘]*\s*)(?:a|an|the)\s+", re.I)
```

**Where `sort_key` strips is immaterial and is stated so no one agonizes over it.** Stripping the assembled key and stripping the head element before assembly give identical results across all 80 documents — 0 entries differing, 0 verdicts differing.

**The transplant was measured rather than assumed, and it is the reason the sibling module was not imported.** Its one crossing is this ticket's own live instance: `West Virginia. The Health Resources and Services Administration` in submitted work, where the phrase runs backwards across a sentence boundary because `NAME` admits a trailing period.

## Ruling 2 — a leading `a`/`an`/`the` is ignored in `first_word`, `citation_key` and `sort_key`, keeping any opening quote

One uniform rule across all three, per APA's "first significant word". **Partial application was refused**, and both partial forms were driven before the ruling:

**Citation side only** newly breaks a currently-clean submitted document. `output/nur5042-m5-discussion-2026-09-02.md` lists `The Elite Nurse Practitioner.` and cites it parenthetically; both key `the` today and resolve. Stripping on one side splits them — the repair manufacturing its own defect, in the same corpus.

**Leaving `sort_key` alone** makes one module hold two answers to what the first word is, which is this ticket's root shape. Not severable.

**The strip keeps an opening quote or emphasis mark and drops only the article.** A naive strip reproduces this ticket's exact defect on APA's own published Beatles example: `"The Beatles,"` keys `the` against an entry keyed `beatles`, raising `uncited-entry` and `unlisted-citation` on a correct list. Both directions are asserted.

## Ruling 2a — the connector set is the sibling's five plus `on`, `in` and `at`, and never `to`

**Added 2026-09-08, later the same session, before any build began.** The first recommendation was to freeze at `discussion_artifact`'s five and declare the gap, argued from a constructed shape — `Mortality in Heart Failure (2024)` keying `mortality` — that **nobody had measured**. The clinician refused the ruling until it was. Measuring reversed it.

Each candidate driven separately over the 80 documents, full findings plus every citation key:

| set | findings delta | citation keys moved |
| --- | --- | ---: |
| five (baseline) | — | — |
| `+on` | none | **0** |
| `+in` | none | **0** |
| `+at` | none | **0** |
| `+to` | none | **2** |

`on`, `in` and `at` are free. **`to` breaks a live case**: `According to Averkamp (2026)` becomes one phrase keyed `according`, because `SIGNAL_PHRASE` strips ten leading forms and *According to* is not among them. That is the measured reason `to` is excluded, and it is a gap in `SIGNAL_PHRASE` rather than a property of connectors — worth the next reader knowing, because widening that vocabulary would change the answer.

**With both costs measured at zero on this corpus, the corpus does not break the tie and failure direction does.** Excluding `on` leaves `National Institute on Aging` — and `on Drug Abuse`, `on Alcohol Abuse and Alcoholism` — firing the exact false pair this ADR exists to remove, on an author class nursing references genuinely carry. Including it risks a capitalized noun phrase joined by a connector sitting immediately before a year-parens, which 80 documents do not contain and which had to be invented to be discussed. The first is a recorded defect class; the second is a hypothesis.

**The adopted configuration was then re-measured whole rather than inferred from the variant run**, because the `Done when` delta had been taken with five connectors and the build ships eight. It is unchanged, and `National Institute on Aging` joins the four opening shapes as clean, while `According to Averkamp` keys `averkamp` and `Smith et al.` keys `smith`.

## Ruling 3 — APA's worked example is quoted into `apa7.md` §1 and the scanner is run over it

`apa7.md` §1 reads *"Alphabetized by the first word of the entry"*, which APA's page makes wrong — it is the first **significant** word. `style.md` §10 restates it **and points at §1**, so correcting §1 alone leaves §10 asserting the retired rule. `CONTEXT.md`'s **Grouping key** is sharpened the same way. §3's existing article rule for the a/b title order is **already implemented** — `Entry.title` reads `irishman film` — and needs no change.

**Nothing binds any of this today.** `test_the_apa_sheet_still_owns_the_rules` asserts three phrases in the sheet and none is the alphabetization rule, so the sheet and `first_word` can disagree with nothing failing — which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

**APA's Smithsonian example is the control, and it discriminates.** Correct by construction, it fails **three rows** today and is clean under the repair:

```text
today        citation keys ['institution','raskin','steinbeck']  entries ['raskin','the','steinbeck']
             findings: list-not-sorted, uncited-entry, unlisted-citation
repaired     citation keys ['raskin','smithsonian','steinbeck']  entries ['raskin','smithsonian','steinbeck']
             findings: none
```

The narrative key today is `institution` — this ticket's root, on APA's own worked example. One fixture covers all three moved rows and states what it would print if the claim were false, which is CLAUDE.md's discrimination rule rather than only its liveness rule.

**A substring tripwire is kept beside it**, because the example cannot notice §10 pointing at a §1 that no longer says what §10 claims. That is prose-to-prose and only a substring check reaches it; the two mechanisms catch different failures rather than being belt and braces.

## Ruling 4 — the new `list-not-sorted` finding on submitted work is taken

Measured whole, all eleven rows, all 80 documents:

```text
list-not-sorted    28 -> 29   (+1)
uncited-entry       4 ->  3   (-1)
unlisted-citation 173 -> 172  (-1)
every other row               (+0)
```

Two documents move, both under `output/`. The `+1` is `The Elite Nurse Practitioner` filed under **T** where APA's Smithsonian example puts it under **E** — a **true** finding the scanner has never been able to see. Taking it records a shape; it does not edit the document, which is the distinction this ticket's own *"not a repair order"* line draws.

**So the build must not reorder that reference list, and that prohibition is stated rather than assumed.** `output/` is submitted, graded work. The obvious way for a builder to make the delta come out at `+0` on that row is to sort the list — which would be editing a document already handed in, to make a scanner quiet. The expected delta is `+1` **because** the defect stays where it is.

## Ruling 5 — the partition of the corpus figure, re-derived

The ticket's *"6 across 80 documents"* is **4 today**; the corpus moved since 2026-09-06 and the population is exactly its 80. Of the four: **1 is this root** — HRSA, in submitted work, with its `unlisted-citation` pair — **2 are genuine** (`Landess, M., Christman, M., & Mikes, B. A.` and `Sobel, J.`, each surname occurring exactly once in its file, in the entry itself), and 1 is a synthetic scratch fixture. **The row's live precision on graded work is 2 genuine to 1 false**, and the false one is the pair. That is the ticket's decision 3, which it named as the first thing the build should produce.

## Ruling 6 — decision 2's published answer was wrong, and decision 4's answer is yes

Two sweep comments on this ticket concluded `discussion_artifact` *"returns `()` for the parenthetical form"* and that the two parsers are *"wrong in complementary directions."* **Both ran `reference_keys` — an entry parser — on a citation string.** Driven correctly through `read_citations` and `citation_occurrence_keys`, that module resolves narrative **and** parenthetical alike on all seven group-author shapes. It is not complementary; it is right where this module is wrong, and wrong only at the sentence boundary ruling 1 measured.

Decision 4 asked whether a whole-phrase author key is available. **It is, and this repair supplies it**: ADR 0039 ruling 5's mandatory named legal entry, cited narratively by name, keys `services` today and `payment` after — resolving against `Entry.key`.

## Ruling 7 — the legal exclusion stays, and its falsified reason is corrected in place

`NOT_REACHED`'s `whether a legal entry is cited` gives its reason as *"the canonical narrative name citation needs a whole-phrase key this module does not have."* **Ruling 6 makes that clause false.** Lifting the exclusion was measured — 18 legal entries move from ungraded to graded with **zero** new findings, 13 resolving on the section key and 5 on `entry.key` — and is **not** done here: it amends ADR 0088, and this session's standing ruling is minimum necessary.

**The replacement reason is a measurement, not a hedge, and it is stated here so a builder does not invent one.** After ruling 1 the exclusion still has a true justification, and it is a different one: `uncited-entry` tests `entry.key` alone, while a legal entry cited **by its section** — the ordinary form — resolves on a `resolution_keys` entry that row never consults. Measured: **13 of 18 legal entries would fire falsely** if the exclusion were lifted without also making the row read `resolution_keys`. So the corrected reason reads that a legal entry is outside `uncited-entry` because that row keys on the entry's first significant word alone, and a section-form citation resolves on a key it does not read — and a clean result therefore cannot prove a legal entry is cited anywhere in the draft.

So the row is retained and its reason corrected, in three one-line edits in the same commit: `reference_scan.py:112`, `reference_scan.py:686`, and `apa7.md` §7's row. **ADR 0088 and ADR 0100 carry the same clause and are not edited** — a ratified record states what was true when it was ratified. The tests bind `NOT_REACHED`'s keys rather than its reasons, so no test moves.

A limit falsified by the commit that falsifies it is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape, and correcting it is not reopening [#678](https://github.com/mshamblin5150-code/clinical-skills/issues/678).

## Ruling 8 — three findings are severed, and none becomes a new ticket

Recorded as comments on [#942](https://github.com/mshamblin5150-code/clinical-skills/issues/942), which is already queued and is already the ticket about citation shapes neither reader can read:

**`discussion_artifact.AUTHOR_PHRASE` crosses a sentence boundary** — 1 of 236 narrative citations, and it is this ticket's live instance. Its `NAME` admits a trailing period, so the phrase runs backwards into the previous sentence. Not repaired here; ruling 1 declines to import that module for exactly this reason.

**The narrative multi-year form reads as zero citations.** `Scorsese (2019a, 2019b)` — APA's own published narrative spelling — matches neither path, because `NARRATIVE` admits a year and at most a locator while the parenthetical path has `EXTRA_YEAR`. Both entries then report `uncited-entry`. **Zero corpus instances**, so it is latent, and it is a worked instance for #942's open question 1 rather than a coverage-reporting change.

**A non-ASCII surname is untouched.** `Kübler-Ross (2014)` still keys `ross`; `NAME` is ASCII-only and this repair does not change the character class. Recorded so a builder does not expect [#943](https://github.com/mshamblin5150-code/clinical-skills/issues/943) to fall out of this one. The King James Bible narrative half **does** fall out — `Bible` becomes `King James Bible`, keying `king`.

## What none of this reaches

**Whether a cited work exists or says what the draft claims.** Unchanged; the research and refutation passes own it.

**A sentence ending in an uppercase-before-period abbreviation followed by a group author.** Ruling 1's boundary continues across it — `…in the U.S. The World Health Organization (2024)` would key `u`. The corpus contains none. Declared rather than closed, because narrowing it means deciding when a period ends a sentence, which is a reading.

**Whether the two modules' boundary rules agree.** They now hold two different ones deliberately, and nothing binds them. That is the residue ruling 1 accepts in exchange for not importing a measured defect.

**A capitalized common noun before a parenthesis.** `PARTICLES`' recorded residue is unchanged — the key is still the first significant word, so a wider phrase does not widen what counts as an author, but it does not narrow it either.
