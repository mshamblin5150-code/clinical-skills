# A legal reference is read by its section and never refused for its name, and the sheet's authority is APA's own page

[#678](https://github.com/mshamblin5150-code/clinical-skills/issues/678) reports a legal reference entry invisible to every citation row `reference_scan.py` has, exiting 0. Grilled 2026-08-30. Every measurement below was taken at `0d26b95`, the freshness gate read `FRESH` at both checkpoints, and `main` did not move during the session. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

**ADR 0085 is in flight and is not on `main` as of 2026-08-30**, so it is named by number without a link or a ruling coordinate throughout: its numbering is not final until it merges, and a coordinate into an unmerged record is a claim that may be false on arrival. Every measurement it is credited with below was re-derived here independently.

## The measurement widened the defect and inverted its direction

The ticket reports silence. On the entry shape [ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md) ruling 5 makes mandatory, it is a **refusal**. Driven in process over both entry forms and all five in-text spellings:

| entry | `(§, 2026)` | `§ (2026)` | bare `§` | `(Name, 2026)` | `Name (2026)` |
| --- | --- | --- | --- | --- | --- |
| nameless `42 C.F.R. § 414.56 (2026).` | 0 silent | 0 silent | 0 silent | 1 `unlisted-citation` | 0 silent |
| named, ADR 0039's mandatory form | **1 `uncited-entry`** | **1 `uncited-entry`** | **1 `uncited-entry`** | 0 clean | **1 `uncited-entry`** |

**Four of five in-text spellings falsely refuse a correct entry**, including all three section forms that ADR 0039 ruling 2 blessed as resolving. ADR 0085 reported only the narrative cell and handed the asymmetry here; the section cells are three more of the same defect.

**It is live rather than hypothetical.** Across 245 Markdown files under `scratch/` and `output/`, 34 hold a readable reference list, 159 entries in total, of which **5 are legal entries across 3 documents — and all 3 take a false `uncited-entry`**. None of the three is blocked by that alone, so no run has yet been stopped by it. All 5 carry a regulation name; **none is nameless**.

### The two modules grade the same draft under different rules

`skills/discussion-post/SKILL.md` step 6 runs `reference_scan.py` on the finished draft and requires exit 0. So the module blind to legal citations and the module ADR 0039 taught to read them grade one artifact in one step. ADR 0039 ruling 4 named the draft's own `References` block as "left untouched and pre-existing"; `reference_scan` is the module that keys it.

### The key spaces are different, which is what bounds the fix

`reference_scan.Entry.key` is `first_word` — a single normalized word. `discussion_artifact.author_key` is the whole phrase. Importing ADR 0039's key space wholesale would replace the key that `missing-ab` and the `a`/`b` rows group on, which is #678's own prohibition and a direction this module has already failed in once.

## Ruling 1 — the legal grammar is imported and the key space is not

`reference_scan` takes `discussion_artifact`'s legal citation pattern and derives a section key inside its own key space. `Entry` gains resolution keys for the citation-pairing block; `Entry.key` is untouched, so the author-grouping rows are unmoved.

Prototyped in a throwaway script with `tools/` unmodified: **nine of the ten cells above go correct**, and three ordinary author-year controls — a single surname, a two-author `&` pair, and a narrative citation — stay clean.

This is ADR 0085's own precedent taken at the same width: the constant is exported from `discussion_artifact` and imported at the width of the piece that must agree, which that record states as *"`reference_scan` importing `docx_write.REFERENCE_HEADING`."*

### Rejected: import ADR 0039's key space whole

All ten cells correct, and it changes what every non-legal entry groups on. #678's *What must not come out of this* forbids it by name, and `reference_scan.py` carries a recorded defect from keying those rows on the wrong half of the author string — a defect whose cost was refusing a correct list **and** teaching the next run to write a wrong one.

### Rejected: declare the class unreached and change nothing

[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s *declare the coverage, do not widen the instrument* is this repository's standing preference and it is a ruling about **silence**. It cannot repair a wrong exit 1, and six of the ten cells are gradeable by one imported constant.

## Ruling 2 — a legal entry is never refused by `uncited-entry`

The one cell ruling 1 cannot reach is the named entry cited narratively — ADR 0039 ruling 1's canonical narrative spelling. Resolving it needs ADR 0039's reverse key walk, which requires a whole-phrase key this module does not have.

So `reference_scan` cannot see that spelling and therefore can never honestly prove a legal entry uncited. The entry is excluded from the row, and the exclusion is declared in `NOT_REACHED`.

**This is what makes ADR 0039 ruling 1's two blessed spellings equally usable**, which ADR 0085 records they are not. It is the constraint that record handed to this ticket.

## Ruling 3 — a legal entry with no regulation name is a reported defect here too

`discussion_artifact.legal_reference_lacks_name` is imported, not reinvented. The predicate exists, is ruled under ADR 0039 ruling 5, and is already correct.

**Measured cost on work in flight: zero.** 0 of the 5 legal entries in `scratch/` and `output/` is nameless, so nothing already written acquires a refusal. It is an entry row, so `BODY_ROWS` is untouched.

Without it, ruling 2's exclusion converts a partial blindness into a complete one: the nameless entry would be excluded from `uncited-entry`, unreadable by the other two citation rows, and reported by nothing — which is the ticket's own headline left standing after its own fix.

## Ruling 4 — the rule is written in `apa7.md` §8, and `discussion-post` gains the pointer

Ruling 3 is a graded row, and `reference_scan.py`'s stated architecture is that it is *"a second reader of `apa7.md`, never a second copy of it."* The legal rule presently exists only in ADR 0039 — a record a maintainer reads, not a sheet a run reads. Nothing tells a drafting run what a legal reference entry looks like, which is how the nameless form came to be written.

`ROWS` points `"apa7 8"`. The table already carries a non-`apa7` pointer, and `tools/test_reference_scan.py`'s section-7 reader already brackets on the next `## ` heading, its docstring naming an eighth section as the trap it was fixed for.

**`skills/discussion-post/SKILL.md` gains a pointer to the sheet**, because that path writes the legal entries and currently points at no APA sheet at all while requiring `reference_scan` to exit 0. Cross-skill sheet references are the existing pattern: that skill already cites `../practicum-case-study/reference/voice.md`, and `discussion-reply` cites `../practicum-case-study/reference/rubric.md`.

Ruling 2's exclusion is a `NOT_REACHED` row, and a test binds that object to `apa7.md` §7 in both directions, so §7 gains a row as well.

## Ruling 5 — the report states the legal count and the exclusion on every run

A sub-count beside the two already there, and one sentence saying a legal entry is outside `uncited-entry`. Both print whether or not the draft holds a legal entry.

[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258) ruled the conditional form out in as many words: a reader who learns to read a qualifier reads its absence as the stronger claim. The house pattern is already uniform — `phi_scan`'s scope row, `checks_ledger`'s graded-row names, `differential_scan`'s coverage line, and the `UpToDate entries` and `entries carrying a DOI` sub-counts this one sits beside.

## Ruling 6 — the sheet's authority is APA's own page, and the library-guide caveat is retired

ADR 0039 recorded `apastyle.apa.org` behind Imperva, returning an incident ID rather than a document, and grounded its legal rulings in seven university library guides. **That block is on the tooling, not on the account.** Re-derived 2026-08-30 with a screenshot and a network trace showing the `_Incapsula_Resource` call and the interstitial; the same URL opened in the maintainer's own browser with **no check at all**.

Passing a bot check is not an action available to an agent here, so the route is the maintainer's browser and that is a standing fact about how this repository reads APA.

**APA's free site publishes 52 reference-example pages** across textual works, data and assessments, audiovisual media and online media, last updated June 2026 — **and no legal-references section**. Neither the References hub nor the sitemap carries one; Chapter 11 is manual-only.

**The legal form is published, on a page nobody had looked at.** *Nursing Student References*, last updated April 2026, item 14, a state nursing practice act:

```
Professional and Vocational Regulations, 16 CCR § 1481 (2023). https://...
    parenthetical  (Professional and Vocational Regulations, 2023)
    narrative      Professional and Vocational Regulations (2023)

    "Name of the Statute, Title number Source § Section number(s) (Year)"
```

**The name is the first element of APA's own pattern**, so ADR 0039 ruling 1 and ruling 5 are confirmed from the source rather than from guide consensus. §8 is written from this page.

### §8 declares the federal-only limit

APA's pattern takes any code as its Source, and its chosen nursing example is `16 CCR` — a **state** code. `discussion_artifact.LEGAL_AUTHOR` is hardcoded to `C.F.R.`, so a state nursing practice act is invisible to every legal reader in this repository. Widening that grammar is a change to a module with three consumers and carries its own false-match risk — ADR 0085 measured `§ 5` and `Section 3 of the plan` as the danger — so it is [#716](https://github.com/mshamblin5150-code/clinical-skills/issues/716), and §8 states the limit rather than documenting a form nothing here can read.

## Ruling 7 — the sheet's coverage is a separate ticket, and it is gated rather than promised

Measured over the same 161 entries in flight: **six source classes, and `apa7.md` gives an entry form for exactly one of them.**

| entries | class | form in the sheet |
| ---: | --- | --- |
| 50 (31%) | journal article with a DOI | no |
| 42 (26%) | no locator — book, print, other | no |
| 38 (23%) | UpToDate | **yes, §2** |
| 16 (9%) | government web page | no |
| 9 (5%) | other web source | no |
| 6 (3%) | legal | no |

So 77% of every entry written is written from recall, against a sheet whose own opening forbids it: *an APA rule is looked up, never recalled.* The sheet's other six sections are rules *about* a list rather than forms for an entry.

**The widening is scoped to APA's whole published set, not to the classes already written** — scoping the sheet to what has been written is scoping it to the assumption. And it is **gated**: the sheet declares which classes it carries a form for, and a census reports any class appearing in a run's reference list that the sheet names no form for. A prose declaration alone is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s finding — a prose edit to a claim fails nothing.

**[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223) is not an obstacle and was checked rather than assumed.** It forbids reproducing APA's prose in a public repository. Covering APA's classes in this repository's own words is what §2 already does.

**Not built here.** The widening, its census and its gate are [#715](https://github.com/mshamblin5150-code/clinical-skills/issues/715), with the table above as its evidence.

## What none of this reaches

**Whether a legal entry is cited anywhere at all.** Ruling 2 removes the only row that could have said so, and ruling 1 cannot restore it for the narrative name spelling. A legal entry cited nowhere passes — as it always has.

**A state or foreign code.** Declared in §8 under ruling 6 and filed as [#716](https://github.com/mshamblin5150-code/clinical-skills/issues/716); `C.F.R.` is the whole vocabulary until it lands.

**Whether the cited section says what the draft claims.** The refutation pass in `skills/discussion-post/SKILL.md`, which states it has no carve-out for legal primary sources. Nothing here reads a regulation.

**Whether faculty mark the in-text legal spelling.** ADR 0039 ruling 2 declined to police it on the absence of evidence, and nothing measured here supplies any.

**The retrieval-date source-class mapping.** APA's nursing page supplies the class-to-retrieval-date rule that [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) declined its option for lack of — UpToDate and StatPearls take one, guidelines and reports do not. That reopens a ruling on new evidence and is [#717](https://github.com/mshamblin5150-code/clinical-skills/issues/717) rather than folded in.
