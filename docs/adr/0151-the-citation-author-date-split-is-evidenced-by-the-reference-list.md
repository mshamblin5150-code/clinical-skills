# The citation author-date split is evidenced by the reference list

[#942](https://github.com/mshamblin5150-code/clinical-skills/issues/942) reports that neither citation reader states a denominator, so a shape the parser cannot read surfaces as a finding two rows from its cause. Grilled on 2026-09-08. **Nothing is built here; this is the record the build reads.**

**`main` advanced twice mid-session and the gate caught it at the publication attempt.** Every measurement was first taken at `4693353`; [#913](https://github.com/mshamblin5150-code/clinical-skills/issues/913)'s build then merged as `8108af3`, changing `reference_scan.py` by 73 lines, and #815's landed after it. The branch was brought forward through both and **every driven case below was re-derived on the merged base**, twice — once after each. Three figures moved on the first and none on the second; each is marked where it appears, and the rulings did not move. ADR 0150 ruling 4's expected delta re-derives exactly on the merged base — `list-not-sorted` 28 to **29**, `uncited-entry` 4 to **3**, `unlisted-citation` 173 to **172** — so #913's build is correct and this record's baseline is the post-merge one.

**Two measurement sets in this record were taken at `4693353` and are not re-derived here**: the five key disagreements in ruling 1, and the three `normalize` variant deltas in ruling 7. Both were computed against the pre-#913 reader. **The build re-derives both before relying on either**; ruling 1's disagreement count is expected to fall, because #913 repaired one of the two failure modes that produced it.

## The clinician's standing rulings, made in this session

> "assumption is the mother of all fuck ups"

Made twice, and it moved two rulings. The first version of ruling 4 below invented a repository convention for a rule APA publishes; the first version of ruling 7 declared a gap that the primary source could have closed. Both were re-taken against the authority.

**Scope is wide on purpose.** The clinician's instruction was to fold in whatever would otherwise become a follow-up ticket, because the build is queued for the same day and chasing successors costs more than the wider diff. [#943](https://github.com/mshamblin5150-code/clinical-skills/issues/943) and [#941](https://github.com/mshamblin5150-code/clinical-skills/issues/941) are folded into #942 and will not be opened separately. [#963](https://github.com/mshamblin5150-code/clinical-skills/issues/963) stays its own ticket behind #818's build, because it is a different module and its own body sequences it there.

## The Publication Manual is readable now, and that retires a standing dead end

The clinician owns the *Publication Manual of the American Psychological Association* (7th ed.) in VitalSource. `apastyle.apa.org` publishes Chapters 8 and 10; **Chapter 9 (reference list order, §9.43–9.48) and Chapter 11 (legal references) are manual-only**, and several records in this tree — [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md) ruling 5 among them — treat those as unreachable. They are not.

**Three routes were exhausted before the manual was opened**, and recording that is the point rather than the conclusion. APA's own examples index carries no legal category. Its in-text index carries no legal section. A site-restricted index search for `U.S.C.`, `bluebook` and `court decision` returns zero, and one for `diacritic`, `accent`, `umlaut` and `letter by letter` returns zero. Purdue OWL's *Reference List: Basic Rules*, *Reference List: Author/Authors* and *In-Text Citations: Author/Authors* were read in full and carry no diacritic rule either. **Every one of those searches was a true negative about the web and a false negative about APA.**

The reader is a JavaScript application: `get_page_text` returns nothing on the reading pane, so it is read by screenshot, and its figures carry a collapsed **Full Description** block whose per-example explanations are not in the body text. That block is where the alphabetization rule ruling 7 turns on actually lives.

`apa7.md`'s caveat that the manual's section numbers are pointers rather than checked claims **was true when written and is now narrower than the tree's reach.** Correcting it is the build's, not this record's.

## Ruling 1 — an unread-span count is not the instrument, because it does not discriminate

The ticket's own instrument is a count of candidate spans the reader declined. **Measured, it prints zero.**

| measured at `4693353`, pre-#913 | `reference_scan` | `discussion_artifact` |
| --- | ---: | ---: |
| unread remainder, reference-evidenced candidates | **0** | **0** |
| unread remainder, strict containment rule | **0** | **0** |
| key **disagreement** | **2** (1 degenerate) | **3** |

All five disagreements are key disagreements, none a year disagreement, and all five sit in `output/` documents. A second, independent measurement using a loose year-anchored recogniser reaches the same verdict from the other side: 20,537 candidates over 1,212 Markdown files, ~3,200 unread across the corpus, and **`766 / 766` on graded material** — a clean row that would not have distinguished a defective reader from a correct one on any graded artifact in the tree.

This is `CLAUDE.md`'s discrimination rule applied to the ticket that cites it: if the claim *both readers key every reference-evidenced citation correctly* were false, an unread-span count would print exactly what it prints when the claim is true. It settles nothing. **The measurement that settles it is disagreement, not absence.**

**The reason is structural rather than a property of this corpus.** Three of the four known wrong-key producers are reads that *succeeded*:

```text
re-derived on the merged base a8be735
Scorsese (2019a, 2019b) directed both.          ref []              disc []
Both were directed (Scorsese, 2019a, 2019b).    ref correct         disc ('Scorsese, 2019a', '2019b')
Hooton et al. (2025a, 2025b) reports.           ref []              disc []
...West Virginia. The HRSA (n.d.) designates.   ref ('health','nd') disc 55-char key
```

Only the first and third are unread spans. The second and fourth produce a citation with a wrong key, and no count of declined spans can see either.

**The fourth row moved when #913 merged, and the movement is worth keeping rather than editing away.** At `4693353` `reference_scan` returned `('administration', 'nd')` — the last word of the phrase — and #913's widening repaired it to the entry's key. **The disagreement survives on the other reader**, whose over-read still crosses the sentence boundary, so the row remains ruling 1's evidence with one side repaired rather than both. That is ADR 0150's own declared residue — the two modules hold two different boundary rules and nothing binds them — arriving as a measurement inside this record's own window.

## Ruling 2 — the independent denominator is the reference list, not a candidate grammar

The ticket's open question 1 warns that a candidate rule built from the same matcher agrees with itself while both omit a member. **The answer is not a looser grammar; it is a different source of evidence.** A reference entry's author and year are authored independently of every citation grammar in the tree, and [ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md) ruling 3 already ratified a reader consulting them, on the ground that a key drawn from the reference source can only produce a citation that resolves.

`discussion_artifact.read_citations` already ships that walk behind `REFERENCE_YEAR`. What it lacks is reach: its trigger is a parenthetical holding a year *alone*, and it is gated on spans no citation already covers — which is exactly why it misses the HRSA case, where the correct span falls **inside** an over-greedy narrative match.

**The prohibition ADR 0150 ruling 1 preserves is on the entry side** — `Entry.key`, `resolution_keys`, and new key vocabulary. Consulting the reference set from the citation reader is not that prohibition and never was.

## Ruling 3 — the two readers keep two numbers, and they mean different things

The ticket's open question 2 asks whether the remainder is one number or two. It is two, and the divergence is by design rather than drift: `reference_scan` keys on `citation_key`, the first word, while `discussion_artifact` keys on `author_key`, the whole normalized phrase. Measured, the same entry yields a six-character key for one and a forty-character key for the other.

A shared candidate recogniser would be a third grammar to keep in step, which is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s refusal. The recogniser's *rule* is shared; its key function is each module's own.

## Ruling 4 — a legal in-text citation is the entry's first element and the entry's publication year

**#941's title claim — that no APA rule exists to settle the repair — is false, and the manual says so directly.** §11.5 gives the template `(Name of Act, Year)` and states that the year in both the reference entry and the in-text citation is the year the statute was published in the source being cited, and that this date may differ from the year in the name of the act. §11.3 states that most legal in-text citations consist of the title and the year. Purdue OWL restates both independently, and APA Chapter 8's general rule — the in-text year matches the reference entry's year — applies with no legal carve-out.

So the two library conventions #941 could not choose between are not equal. **The Franklin convention — shortened name plus the statute's own year — is non-conforming under APA's own general rule**, because its date element can never join the entry's. Driven at `4693353`:

```text
(Family & Medical Leave Act of 1993, 2006)     entry (2006)   -> clean
(No Child Left Behind Act, 2001)               entry (2008)   -> intext-year-mismatch
```

**The repair is not a heuristic, and the earlier recommendation was falsified before it was ruled.** That recommendation was *the last of two comma-separated years is the date element*, which would read APA §8.12's own `(Department of Veterans Affairs, n.d., 2017a, 2017b, 2019)` as one work dated 2019 and lose three citations. The reverse rule loses the statute. **Both fail on a published example, because the two shapes are grammatically identical** — and APA resolves them by definition rather than by grammar: the author element *is* the entry's first element. `Consolidated Appropriations Act, 2023` is one string because that is the entry's first element; `Department of Veterans Affairs` is where that entry's first element stops.

The mechanism is therefore ruling 2's, not a second one.

**The consequence for submitted work is stated rather than left to be found.** Under this ruling the live artifact's `(Consolidated Appropriations Act, 2023)` is missing its date element and becomes a **true** finding. It is graded, handed-in work under `output/`. This is ADR 0150 ruling 4's position exactly: the record stays as it is, the finding is what a reader cannot see, and **the document is not edited to quiet a scanner.**

## Ruling 5 — evidence-first, gated by five measured noise predicates

The reference-evidenced walk is the reader's **primary** author/date split wherever an entry's first element matches; the existing grammar is the fallback where none does. Under grammar-first the five measured disagreements would be *reported* and left wrong; under evidence-first they become correct reads.

**The risk runs against this repo's usual safety direction and is priced rather than waved through.** ADR 0039's *safe by construction* argument covers emitting a citation that resolves. Overriding a grammar read is a different act: a wrong evidenced match manufactures a resolving citation and **silences a true `unlisted-citation`** — a finding disappearing, which is worse than a false one appearing.

So an evidenced match is refused when its author span crosses a sentence boundary, crosses a line break, starts lowercase, sits inside a code span or fence, or its key is under three characters. Each predicate is mechanical, was measured over the corpus, and has a recorded instance; one of the five measured disagreements was itself a one-character key matching almost any phrase.

**The fallback's answer is what `unlisted-citation` grades**, and it must be, because a genuinely unlisted citation has no entry to be evidenced by. The report says which path answered.

## Ruling 6 — the coverage row prints keys, never spans

`reference_scan`'s `--show` is the one pasteable `--show` in `tools/`, and that ruling rests on a measured property: `BODY_ROWS` bounds the rows reading the draft's prose, and the only aperture is a citation key.

Keys only. The evidenced walk reaches back several words of preceding prose and **that span never reaches the report** — a draft is written about a patient. `reference_scan`'s keys remain single words, so a disagreement detail of *evidenced key against reader key* stays inside the blessed class, and the salted-draft measurement is re-run to prove the pasteable ruling still holds with the new row in `BODY_ROWS`.

**`discussion_artifact`'s keys are whole phrases and are explicitly not covered by that ruling.** Its measured over-read keys run to fifty-five characters, which is draft prose wearing a key's name; its rows print counts by default and detail only behind its existing private `--show`.

The narrower ground, which the 2026-08-19 pasteable ruling did not contemplate: **an evidenced key comes out of the reference list rather than the body**, so this arguably narrows the aperture rather than widening it.

## Ruling 7 — `normalize` folds, and preserve is not what "letter by letter" means

APA publishes no diacritic rule. That is now a checked negative rather than an unread section: §9.44's three bullets, and each of the twelve per-example explanations in Figure 9.2's Full Description, give the complete rule — alphabetize letter by letter **including any prefix**, disregarding **capitalization, spaces and punctuation** such as apostrophes and hyphens. Diacritics appear in none of them, nor in the index outside §2.20 on manuscript special characters.

**Preserve does not implement that rule.** Under it `ö` sorts after `z`, which is Unicode code-point order and is a principle APA states nowhere; the figure files `de Onís` and `López` in ordinary alphabetical position. Folding is what letter-by-letter comparison means.

Three variants were built and run over the whole corpus, **at `4693353`, against the pre-#913 baseline**. The base column is that reader's; on the merged base the same rows read 29, 3 and 172. **The build re-derives the deltas rather than carrying this table forward:**

| measured at `4693353` | pop80 base | V1 preserve | V2 fold | V3 fold-equality, preserve-order |
| --- | ---: | --- | --- | --- |
| every one of 16 rows | | `+0` | `+0` | `+0` |
| `list-not-sorted` | 28 | `+0` | `+0` | `+0` |
| `uncited-entry` | 4 | `+0` | `+0` | `+0` |
| `unlisted-citation` | 173 | `+0` | `+0` | `+0` |
| documents under `output/` whose findings change | | 0 | 0 | 0 |

**The `+0` result is expected to survive the re-derivation and is not assumed to.** #913 changed the narrative phrase boundary and the article strip; it added no non-ASCII handling, and the single corpus entry these variants touch is unchanged. But that is an argument, and the whole point of the table is that it is a measurement.

**V1 is eliminated by measurement, not by preference.** On a leading-`Ö` entry cited with the ASCII spelling it *adds* a false `uncited-entry` to the existing `unlisted-citation`: widening the character class without folding is worse than the bug.

**V2 and V3 are indistinguishable on this corpus and genuinely diverge in principle** — synthetic controls separate them on `list-not-sorted` — so the decision rests on APA's rule rather than on a measurement, which is why the paragraph above had to be taken from the manual.

**#943's three modes have zero live instances**, confirmed as a real zero by controls that fire every counter. The corpus holds one entry with a non-ASCII author letter; its truncation is symmetric, it is last in its list, and its finding set is empty before and after under all three variants.

**The cost is real and is accepted:** folding makes `Kübler` and `Kubler` one author, a false-negative risk on `missing-ab`. It is distinguished from `docx_read.py`'s deliberately narrow homoglyph map on the ground that the map crosses scripts while NFKD-then-strip-marks stays inside one and undoes a decomposition Unicode itself defines. That is an argument and not a measurement, and the corpus cannot settle it.

## Ruling 8 — `in press` is a date value everywhere `n.d.` is, and its letter form is published

`n.d.` is fully supported on both sides of both readers and `in press` on neither, though APA names them together. Driven at `4693353`, a **fully correct** in-press pair — two entries, two citations — yields zero citations and two `entry-has-no-year` findings. That is this ticket's thesis verbatim: a correct document reports a defect **in the entry** because the reader lacks a token.

§9.4 states that an in-press work uses `in press` for the date in both the entry and the in-text citation, in the sentence beside the identical `n.d.` rule. §9.46 orders no-date first, then dates, with in-press last. §8.12 and Purdue OWL both write the multi-date parenthetical with `in press` as a member.

**§9.47 publishes the letter form explicitly** — years take `2020a`, no-date takes `n.d.-a`, and in-press takes `in press-a`. So it is **read and graded**, and the earlier plan to read it without grading it, on the ground that grading would be an invention, is retired. Nothing is invented; the manual states it.

The corpus contains **0 instances**, entry or body. The form is latent and rests on the authority alone, which is ADR 0145 ruling 2's footing for the narrative republished form.

**The letter suffix is generic over the date vocabulary rather than a second hardcoded alternative**, so `n.d.-a` and `in press-a` fall out of one rule.

## What none of this reaches

**Whether a cited work exists or says what the draft claims.** Unchanged; the research and refutation passes own it.

**A wrong key produced by a fallback grammar read where no entry evidences the span.** Evidence-first only reaches spans the reference list can vouch for. A citation of a source that is genuinely unlisted is read by the grammar, and its key is whatever the grammar makes of it — which is what `unlisted-citation` grades and cannot itself audit.

**Whether the five noise predicates are the right five.** They are mechanical, measured and each has an instance, but they are a floor on implausibility rather than a definition of it. A wrong evidenced match that trips none of them still overrides a grammar read.

**The nine-document evidence base.** The 80-document grader-reachable population is weak: 65 of the 80 produce zero candidates, 63 have a body under 500 characters and 64 have exactly two reference entries, because the gate fires on small non-APA structures whose `Reference`-prefixed heading truncates the body. **The substantive corpus is 9 documents**, holding 766 of the 790 candidates. Every coverage claim in this record is evidenced by those nine. It does not falsify ADR 0150 ruling 4's baselines, which re-derived cell for cell in two independent processes, but no reader should infer 80.

**`v.` as a connector.** ADR 0150 ruling 2a's connector set omits it because the corpus carries no case citation. **#913 has now landed and the case citation is still broken, differently** — re-derived on the merged base, `Brown v. Board of Education (1954)` keys `board` where it keyed `education` before, against an entry keyed `brown`. The widening moved the phrase start left as far as `v.` and stopped, which is the boundary rule working exactly as ruled. Recorded on that ticket while it was in flight, with the pre-merge figure; the repair is #942's.

**Whether the two modules' boundary rules agree.** ADR 0150 accepted that residue deliberately. This record closes it by repairing `discussion_artifact`'s side, and states no rule binding them mechanically thereafter.

**A case name's italics.** §11.3 requires italic in-text and standard in the entry. `discussion_artifact.PAREN_PAIR` anchors on an uppercase class, so an italicised in-text legal citation is invisible to it; the build repairs the reading and grades nothing about whether the italics are present.
