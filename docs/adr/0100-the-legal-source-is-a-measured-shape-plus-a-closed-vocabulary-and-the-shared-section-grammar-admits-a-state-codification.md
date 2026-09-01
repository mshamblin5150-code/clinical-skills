# The legal Source is a measured shape plus a closed vocabulary, and the shared section grammar admits a state codification

[#716](https://github.com/mshamblin5150-code/clinical-skills/issues/716) reports that `discussion_artifact.LEGAL_AUTHOR` is hardcoded to `C.F.R.`, so APA's own worked legal example — a state nursing practice act, on the page written for nurses — is mis-keyed and unflagged. Grilled 2026-09-01. Every measurement below was re-derived in process at `ce83ea4` after `main` moved mid-session; the freshness gate read `FRESH` at the first checkpoint, `STALE` at the second, and the branch was brought forward and every load-bearing figure re-taken before anything was published. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement reshaped the ticket three times before the first decision

**The ticket's three candidate Source rules all miss the codification this corpus actually writes.** Decision 1 offered a closed vocabulary of code abbreviations, a shape `<digits> <UPPERCASE letters> §`, or a per-jurisdiction table. The state citations live here are West Virginia:

```
Prescriptive authority for prescription drugs, W. Va. Code § 30-7-15a (2024).
Advanced practice registered nurse licensure requirements (W. Va. Code R. § 19-7, ...).
```

`W. Va. Code` carries **no title number** and is **mixed case**, so no candidate reaches it. APA's `16 CCR § 1481` appears in this tree only where ADR 0088 and #716 quote it. The ticket generalized from APA's one published example and the corpus holds a different shape, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) arriving on a ticket filed by a sweep.

**The state gap is a false alarm and not a silence, and it is live on submitted work.** Driven through `reference_scan` on drafts that are APA-correct throughout, one entry, both spellings ADR 0039 ruling 1 blesses:

| in-text spelling | state entry | federal entry |
| --- | --- | --- |
| name-first `(Name, 2024)` | exit 0 | exit 0 |
| section `(<Source> § <n>, 2024)` | **exit 1** `uncited-entry` + `unlisted-citation` | exit 0 |

The section spelling is the one ADR 0039 ruling 2 promises resolves. On a state code it manufactures findings on correct prose — the outcome #716's own *What must not come out of this* forbids, already shipped. Confirmed at scale rather than on a synthetic draft: across every corpus document with a readable reference list, the widening removes **four** `uncited-entry` findings, all four in `output/discussions/nur5042-m2-discussion-2026-08-20.md`, an artifact whose eight legal entries are all APA-correct.

**The reader is narrower than `C.F.R.`-only.** `42 CFR` without periods is written 27 times in this corpus and is invisible too, so the honest statement is `C.F.R.`-with-periods-only.

## Ruling 1 — the Source is a measured shape plus a closed mixed-case vocabulary

Two limbs, and the split is forced by the corpus rather than chosen for symmetry.

**Limb one is a shape**: a leading title number and an uppercase code. Measured over all corpus Markdown plus every tracked `.md`, the shape and a closed vocabulary of `C.F.R.`/`U.S.C.`/`CCR` spellings return the **identical** set — 130 occurrences, 21 distinct spans at `ce83ea4`, **zero non-legal**. Dropping either requirement breaks immediately:

| rule | fires on |
| --- | --- |
| digits + uppercase code + `§` | nothing but real citations |
| code optional, lowercase admitted | `3 of the plan sets § 5`, `23 sections on §8`, `0 is the silent pass §8` |

**Limb two is a closed vocabulary of mixed-case source names**, seeded from evidence in this tree and nothing else — today `W. Va. Code` and `W. Va. Code R.` A rule keyed on a listed name cannot fire on an unlisted one, so `The Code § 5` stays prose by construction rather than by a measurement that has to keep being retaken.

**It grows on a form somebody wrote, never on a family.** That is `spelling_scan`'s table rule adopted whole, and it is the reason limb two can be admitted at all: the generic form of it — capitalized words ending in `Code` before a `§` — buys the unwritten states for free and has no measurement saying it stays off correct prose, which is the bar #716's `Done when` sets.

**In scope: `42 CFR` without periods, `29 U.S.C.`, `16 CCR`, `W. Va. Code`, `W. Va. Code R.` Out of scope: any bare `§ n`.**

## Ruling 2 — the Source slot follows the shared half, and both readers change

ADR 0085 ruling 2 ruled `LEGAL_SECTION_NUMBER` one shared constant *because a run writing `(b)(1)(v)` must be read the same way by both readers*, while the outer citation-versus-statute shapes stay two. The Source slot is the same kind of piece. It is exported from `discussion_artifact` and imported by `discussion_post_scan`, at the width of the piece that must agree.

**`STATUTE` stays the looser reader** — optional `§`, its bare-`§` branch, and the comment saying why. `§ 5` is untouched in both directions, because the shared constant is a *prefix* vocabulary and neither limb can match an empty prefix.

**Both readers change, because ADR 0085 ruling 3's table repeats here with `W. Va. Code` in place of `(c)(3)-1`.** Measured on `STATUTE` as it stands:

```
Under W. Va. Code § 30-7-15a (2024).    strips '§ 30-7'      leaks '2024'
Under 42 C.F.R. § 414.56 (2023).        strips whole         leaks nothing
The schedule at 42 CFR § 482.23 (2024)  strips '§ 482.23'    leaks '42', '2024'
Section 3 of the plan sets § 5.         strips '§ 5'         leaks '3'   <- correct
```

Widening the citation reader alone leaves those `untraced-number` requirements standing on correct state prose.

## Ruling 3 — the shared section grammar widens, and ADR 0085's range residue is retired for being free

Ruling 1 is unbuildable without this: the shared constant cannot express a West Virginia section number. It allows one hyphen group and no letter, and these carry two or three groups, letter suffixes, and letters in the head.

```
fullmatch '30-7-15b'  -> None      fullmatch '60A-9-5a' -> None      fullmatch '19-8-3.7' -> None
```

The ruled tail admits a head letter, repeated hyphen groups each with an optional letter suffix, and a decimal group after each. Measured over all corpus Markdown plus every tracked `.md`:

| tail | real sections read whole | spans differing from today |
| --- | --- | --- |
| today | 13 of 21 | 0 |
| head letter, repeated groups | 19 of 21 | 30, all real sections |
| **ruled** | **21 of 21** | 35 — 33 real, 2 over-strips |
| permissive `-\w+` | 21 of 21 | and eats `§ 5-year` |

**The two over-strips are `§1a` and `§2b`, this repository's own sheet references.** They are reachable only through `STATUTE`'s bare-`§` branch — `LEGAL_CITATION` requires a Source, so no tail can turn `§1a` or `§ 5` into a citation — and ADR 0085 ruling 2 ruled over-stripping safe in exactly that reader.

**The conservative tail was rejected on a federal case, not a state one.** Its single miss is `42 U.S.C. § 1395dd`, EMTALA, which today's rule also truncates to `1395`. This is not a state-only repair.

**ADR 0085's declared range residue is closed rather than inherited, and it is closed for being free.** That record declared `§§ 414.56-414.60` losing `-414.60` on the ground that *"nothing in the tree writes one, and it costs a character in a span nothing keys on."* The reason still holds; the cost is now zero, because the ruled tail consumes the range whole at no measured price. **A later reader comparing ADR 0085's *What none of this reaches* against a grammar that reaches it should read neither record as wrong.**

**The tail was found by a blast-radius measurement, not by reasoning.** The conservative tail left `.7` dangling on `§ 19-8-3.7`, a real West Virginia rule section live in a claims ledger, and that surfaced only when the numeric walk was re-measured across the corpus. `block_scan.py`'s and `threshold_sheet.py`'s lesson a further time: both of those parsers' bugs were caught by pointing them at real material and neither by a fixture.

**The blast radius is stated because it reaches every post rather than only legal reading.** 13 documents change, 93 numbers stop requiring a claim record, every one in the over-stripping direction.

## Ruling 4 — `legal_reference_lacks_name` transfers unchanged, and its one refusal is accepted

#716 decision 3 said ADR 0039 ruling 5 *looks like* it applies but had never been checked against a second state's codification. It is checked now, against the one this corpus uses.

```
reference entries read                     239 at ce83ea4
legal-reference-lacks-name   before 0   after 2

  W. Va. Code § 30-7-15b (2016). https://code.wvlegislature.gov/30-7-15b/
    output/discussions/nur5042-m3-discussion-2026-08-29.md   submitted
    scratch/runs/nur5042-m3-discussion/post.md               its draft
```

The predicate needs no edit — widening the grammar it already consumes is what makes it reach a state entry — so it earns its own named test rather than its own ticket, on ADR 0085 ruling 4's *a behavior that arrives for free is a behavior nothing pins*.

**The M2 artifact's eight legal entries, six of them state, all pass**, so the row does not fire on a correct second-state entry. The one that fires carries no regulation name in any slot.

**The refusal is a record and not a repair order.** That discussion is submitted and graded. Whether the draft is corrected is the clinician's.

**One residue was measured rather than assumed.** The paren-embedded form `...requirements (W. Va. Code R. § 19-7, effective May 2, 2024).` keys **nothing** today and keys two keys after, becoming visible to `uncited-entry` for the first time. Driven across the corpus, it produces **no** new finding.

## Ruling 5 — the second citation walk is folded in, and the shared width is the span set

`discussion_artifact.read_citations` excludes legal spans before reading ordinary parentheticals. `reference_scan.read_citations` is an independent walk that does not.

```
today        ('w', 2021)                                    one wrong key
widened      ('w va code 60a 9 5a', 2021) AND ('w', 2021)   right key, wrong key kept
widened+fix  ('w va code 60a 9 5a', 2021)                   one right key
```

**The federal form escapes by accident** — `42 C.F.R.` starts with a digit, so the ordinary parenthetical reader never matches it. Only a **capitalized** legal author is double-read, which is exactly the vocabulary ruling 1 admits. So this is not a pre-existing bug that may be left alone: without it, limb two emits the correct key *and* a junk one, and the junk one fires `unlisted-citation` on submitted work.

**The `('w', 2021)` mis-key is live today**, so #716's *mis-keyed rather than unkeyed* thesis holds on the in-text side, where the ticket measured only the entry side.

**The width that must agree is the span set, not the walk.** Two hand-written copies of *a span already read as a legal citation is not re-read as an ordinary parenthetical* is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) with nothing between them; unifying two walks with different dedup and different key types wholesale is the move ADR 0085 ruling 2 warns against. The span set is exported and both walks consume it. That is `LEGAL_SECTION_NUMBER`'s argument at a third width.

## Ruling 6 — the session-law form is filed, not folded, and the negative measurement travels with it

`Consolidated Appropriations Act, 2023, Pub. L. No. 117-328, § 1263, 136 Stat. 4459, 5683-5684 (2022)` is live in the M2 submitted artifact, unread as legal today and unread under everything ruled above.

**Adding a session-law limb does not cure its symptom**, which is the whole argument for filing rather than folding:

```
session-law limb absent    is_legal=False   findings ['intext-year-mismatch']
session-law limb present   is_legal=True    findings ['intext-year-mismatch']
```

The root is that the statute's *title* contains a year, cited against a listed `(2022)`. A builder who folded this in would widen the Source vocabulary, watch the finding survive, and be editing the wrong function — ADR 0085's own recorded failure, where a ticket body sent a builder at the wrong root.

It also fails #716's `Done when`: `Pub. L. No.` has had one form driven through it and `Stat.` none, and putting an unmeasured grammar in the same commit as a measured one is what that clause forbids.

## Ruling 7 — the limit moves into code, the sheet points at it, and both graders state it every run

After this lands the true limit is *an unlisted code reads as non-legal* — narrower than the law and not knowable from the output. The only statement of narrowness today is `apa7.md` §8's prose, which is the arrangement [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) ruled insufficient, because a prose edit to it fails nothing.

`discussion_artifact` gains its first declared-limit object, beside the grammar it describes, because that grammar has three consumers and a per-consumer copy is #220 with no test between the copies. **§8 names the object rather than enumerating it** — #241's repair adopted at the outset rather than after two copies drift — with a test binding the sheet to the object in both directions, the way `reference_scan.NOT_REACHED` is already bound.

**Both graders print the coverage, each holding its own copy of the sentence and both reading the figure off the one constant.** The precedent is `spelling_scan.vocabulary_covered` and the analogy is tight rather than decorative: that scanner prints its coverage because **it holds a table rather than the language**, and this reader holds a vocabulary rather than the law. It prints on clean runs too, because a reader who learns to read a qualifier reads its absence as the stronger claim — and a reader who learns to read it in one grader reads its absence in the other the same way.

**[#751](https://github.com/mshamblin5150-code/clinical-skills/issues/751) landed during this session** and repaired §8's `Federal-only` label and the second copy of it in `skills/discussion-post/SKILL.md`. This record **supersedes** those sentences rather than reverting them. **§8's closing clause still enumerates the excluded set as *state or foreign*, which omits every other federal code**; that half of #751's defect survives its own fix and is retired here with the paragraph.

## Ruling 8 — one branch, staged edits, and the remediation row widens with the row it describes

The work is five pieces with real dependencies: the section grammar, the Source vocabulary, the span suppression, the declared limit with the sheet pointer, and the report line. The first is independently correct and independently measured; the second and third cannot be separated.

**One ticket, one branch, staged in that order**, and the argument is this repository's record rather than tidiness: the first two pieces edit the same two constants in the same two modules, and [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) and [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86) are both about two branches meeting on one artifact. Two branches over `LEGAL_SECTION_NUMBER` and `LEGAL_AUTHOR` in one window is that shape volunteered for.

**A full-corpus re-measurement after the grammar and again after the suppression**, so the two blast radii stay attributable — the first reaches every post's numeric walk through `STATUTE`, the second reaches only legal reading, and a single measurement at the end cannot tell them apart.

**`skills/practicum-case-study/SKILL.md`'s remediation row becomes *a legal entry carrying only its section*.** It reads *"A federal-regulation entry carrying only its C.F.R. section"* and it is the reader-facing half of ruling 4, whose one real instance is a state entry — so leaving it ships a grader that flags a defect the remediation table does not describe.

**§8 gains a worked instance of the codification this corpus writes**, presented as an instance of APA's pattern with APA's `16 CCR` example kept as the authority, never as a second rule. The argument is ruling 4's measurement rather than symmetry: the single new refusal is a state entry written section-only, in submitted work, by a run that had §8 in front of it, and §8's only example is a code this corpus never writes.

## What none of this reaches

**A state whose code is not in the vocabulary.** That is the standing price of ruling 1's second limb, and it is declared in code under ruling 7 rather than left to be discovered. A second state's citation is invisible until somebody writes one and adds the row.

**A session law.** Ruling 6, filed with its negative measurement attached.

**Whether the cited section says what the draft claims.** The refutation pass owns it, with no carve-out for legal primary sources. Nothing here reads a regulation.

**Whether a year in a statute's title is read correctly.** Measured as unfixed by anything ruled here, and its root may reach non-legal sources too, which nothing has measured.

**Whether faculty mark the in-text spelling.** Unchanged from ADR 0039 ruling 2 — declined on the absence of evidence, not on evidence of absence.

**Whether a clean legal row means a legal entry is cited.** Unchanged from `reference_scan.NOT_REACHED`: a legal entry is outside `uncited-entry` because the canonical narrative name citation needs a whole-phrase key that module does not have.
