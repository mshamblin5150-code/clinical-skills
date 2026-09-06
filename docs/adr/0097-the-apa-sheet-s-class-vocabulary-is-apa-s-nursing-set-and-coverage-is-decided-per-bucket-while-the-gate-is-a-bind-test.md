# The apa sheet's class vocabulary is apa's nursing set and coverage is decided per bucket while the gate is a bind test

Ruled by the clinician on 2026-09-01, in the grilling of
[#715](https://github.com/mshamblin5150-code/clinical-skills/issues/715) and
[#717](https://github.com/mshamblin5150-code/clinical-skills/issues/717) together. Both tickets
were filed by the grilling of [#678](https://github.com/mshamblin5150-code/clinical-skills/issues/678)
on 2026-08-30 and both carry decisions that turn out to be one decision asked twice, which is why
they were worked as one tree rather than in sequence.

**The freshness gate failed between the first checkpoint and the second, and the failure paid for
itself.** `main` moved from `bbb317d` to `1595299` mid-session, and
[ADR 0094](0094-a-tool-s-show-output-is-unpasteable-by-default-and-its-own-docstring-is-the-only-authority.md)
landed in that window and falsified a derivation this session had already published to the
clinician. Ruling 10's second limb is the repair. That is
[#320](https://github.com/mshamblin5150-code/clinical-skills/issues/320)'s second checkpoint
collecting for the first recorded time on a grilling rather than on a sweep.

## Measured before ruling, at `1595299`

Every figure here is dated to that commit and is re-derivable from it. Nothing measured against a
gitignored corpus is stated anywhere in this record, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms — which is the
correction ADR 0088 ruling 7 has already had to take once.

**The sheet.** `skills/practicum-case-study/reference/apa7.md` carries 8 `##` sections. **§2
(UpToDate) and §8 (legal) are the only entry forms**; §1, §3, §4, §5, §6 and §7 are rules *about* a
list — heading and sorting, the `a`/`b` rule, retrieval dates, citation resolution in both
directions, what the renderer applies, and what stays a reading. §8 landed on #678 and moved #715's
headline from *one class in six* to *two*, exactly as that ticket's own 2026-08-31 correction
predicted it would.

**The scanner.** `tools/reference_scan.py` already carries `UPTODATE_NO_RETRIEVAL_DATE`, fired at
`:933` on `entry.is_uptodate and stamp is None`, where `is_uptodate` is `UPTODATE_NAME` or
`UPTODATE_HOST` — a hardcoded one-class rule. `RETRIEVAL_DATE_ON_ARCHIVED` is gated at `:887` on
`DOI.search(entry.text)` alone. `SOURCE_CLASS_SETTLES_RETRIEVAL_DATE` holds four keys bound by test
to `research_ledger.SOURCE_CLASSES`.

**The seam.** `tools/research_ledger.py:42` is `from reference_scan import read_document`, with the
comment above it naming [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108)'s
duplication as what it refuses. This repository has already declined to build a second parser of
this exact list once.

**The sheet's readers.** `apa7.md` is named 81 times across 14 tracked files outside `docs/adr/`.
`skills/discussion-post/SKILL.md:155` is #678's pointer to it and `:253` requires
`reference_scan.py` to exit 0. Four of five skills read into
`skills/practicum-case-study/reference/`: `voice.md` is read by `clinical-note`,
`discussion-post`, `discussion-reply` and `setup-clinical-skills`, and `rubric.md` by
`discussion-reply`. `tools/test_skill_agreement.py:3258` walks `SKILLS_DIR.rglob("*.md")`, so the
step-citation resolver's population is `skills/` and nothing else.

**The roots.** `tools/scratch_census.py:85` `worktree_roots()` walks
`git worktree list --porcelain`; `repo_root.scratch_root()` resolves to the owning checkout alone;
`docx_write.ensure_main_checkout` forces every submission into the main checkout's `output/`.
`tools/adr_next.py` enumerated **50** worktrees, 0 unreadable, allocating this number.

**The access.** `apastyle.apa.org` was navigated in the in-app browser during this session and
returned `navOk: false` — denied. #678 records the same host opening with no check in the
maintainer's own browser, with a screenshot and an `_Incapsula_Resource` network trace. **The block
is on tooling and not on the account**, re-derived here in the one direction this session could
reach.

**The corpus, which was not measured.** This worktree holds **no `output/` at all and 6 files under
`scratch/`**, so no `scratch/`-plus-`output/` figure in either ticket is re-derivable from this
base. Every reliability claim below is a **shape** argument and none is a rate. The #689 sweep of
2026-09-01 recorded the same bound about the same body.

## The rulings

### 1. The class vocabulary is APA's *Nursing Student References* page, and this overrides ADR 0088 ruling 7

The sheet grows one `##` section per item of that page — 23 items, last updated April 2026 — with
anything outside it covered by one section pointing at APA's general example index. The census's
denominator is that same set.

**This is an override of a ratified record and is written as one rather than drifted past.**
[ADR 0088](0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md)
ruling 7 says *"the widening is scoped to APA's whole published set, not to the classes already
written"* — 52 reference-example pages. **Ruling 7's reasoning survives intact and its scope does
not.** Its ground is that *scoping the sheet to what has been written is scoping it to the
assumption*, and the nursing page is **a published APA set**, not this repository's measured set, so
the ground is met. What changes is which published set.

**The three candidates were priced against what the gate can then do, which is the axis ruling 7
did not consider.** All 52 pages makes the census's finding state **unreachable by construction** —
there is no class outside the set for it to report — which is
[#182](https://github.com/mshamblin5150-code/clinical-skills/issues/182)'s *a block satisfies the
gate by existing* arriving on the gate ruling 7 asked for in the same paragraph. Deriving the
vocabulary from what the classifier can distinguish inverts the dependency ruling 7 exists to
prevent and is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s numerator
and denominator built from one matcher.

**And the nursing page is already half-adopted.** §8 is item 14 of it, built and landed on #678, so
the shape is proven against something in the tree rather than argued in the abstract. The page's
own item list — UpToDate, Cochrane review, StatPearls, clinical practice guideline, DailyMed drug
information, lab or diagnostic manual, state nursing practice act, ethics code, position statement,
fact sheet — is very nearly the exact class set this repository's work is made of, which is the
observation #715 makes and does not act on.

### 2. The census is two readers of one classifier, because the two findings have different readers

#715 decision 2 asks about the census as one instrument. It is two, and ADR 0088 asks for both in
two different sentences written thirteen days apart.

**A per-run row inside `reference_scan`** reaches whoever can still act on the entry, and its
remedy is the sheet's own opening line — *an APA rule is looked up, never recalled*. This is what
ruling 7 means by *"a census reports any class appearing in a run's reference list."*

**A corpus census command** reaches the maintainer, who is the only party who can widen the sheet,
and it is what discharges ruling 7's 2026-08-31 correction: *"#715 carries the re-measurement and
owns the census that makes it re-derivable."* Building only the row leaves that ratified assignment
permanently unmet and ADR 0088's class split permanently un-re-derivable.

**One classifier object, two readers, on `research_ledger.py:42`'s precedent.** Two implementations
of one vocabulary is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) with
nothing between them; sharing the object means no second implementation survives to disagree.

### 3. Recognition is per **bucket**, with a declared many-to-one mapping and three states

**The sheet's vocabulary and the recognizable vocabulary cannot be the same set, and that is a
structural fact rather than a limitation of any matcher.** An entry string carries a DOI, a host, a
`§`, a database name. It does not carry *this is a Cochrane review rather than a journal article*
or *this is a position statement rather than a fact sheet*. Several of the 23 items are
indistinguishable from one another in an entry string by construction.

So the classifier recognizes **buckets** — what an entry string can actually carry — and each
bucket **declares which sheet classes it spans**. Coverage is decided on the bucket:

* every spanned class has a form — **clean**;
* no spanned class has a form — **finding**, and the remedy is unambiguous;
* some do and some do not — **`undecidable`**, counted and printed on every run, never a finding.

**Classifying to the 23 directly is the option [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)
declined and #717 forbids by name**: where two classes share every signal the rule must pick one,
and a wrong class **fails a correct entry**. `guidelines_catalog.py --draft`'s *a guessed answer
here is worse than a blank one*, arriving at a reference list.

**`undecidable` is not a hole, it is the extractor-coverage rule applied.** *A matcher never gets to
turn a partial read into a clean whole*, so the unread remainder prints beside the denominator on
every run. It also makes the widening **measurable without a hand-kept list**: a bucket moves
`finding` → `undecidable` → `clean` as sections land, so the gate's own output tracks its own
closure.

### 4. #241's join reopens in one direction, and its closure is **confirmed** in the other

This is the ruling the two tickets were worked together to reach, and it is not either verdict #717
decision 1 offered.

**The refusing direction does not widen, and #241 was right.** That ticket declined the join because
`research_ledger`'s `government` spans a USPSTF statement (no retrieval date) and a public-health
page designed to change (one), and `tertiary reference` spans UpToDate (one) and a textbook (none).
In ruling 3's vocabulary those are `undecidable` buckets, and **APA's nursing page does not rescue
them**: it answers per *class*, while *designed to change and unarchived* is a property of **the
work**. A static agency fact sheet and an agency page revised quarterly are one bucket, one class,
and opposite answers. `RETRIEVAL_DATE_ON_ARCHIVED` stays keyed on the DOI and
`reference_scan.NOT_REACHED`'s first row survives untouched.

**What moves is the opposite direction, and it is decidable.** APA's page states a retrieval date
**required** for exactly two classes, UpToDate and StatPearls, and both are recognizable from an
entry string by host with no ambiguity. `UPTODATE_NO_RETRIEVAL_DATE` is that rule already built for
one of the two and hardcoded to it. It generalizes into a `requires-retrieval-date` row over a
declared class set, and StatPearls joins it.

**So #717's premise is true and its conclusion is smaller than it reads.** The mapping #241 was
declined for lack of does exist and is published, and #717's reading that #241 *joined on the wrong
vocabulary* is correct — but the right vocabulary reopens **one** direction and **confirms** the
closure of the other. That is a stronger outcome than either bare verdict, because it explains #241
rather than overturning it, and #241 stays closed on its own reasoning.

### 5. The retrieval-date answer is a column on the class table, never a second object

The *requires-one* set is a property of a sheet class, so it lives on the table ruling 3 already
requires: `has_form` and `takes_retrieval_date` beside each class, with the sheet's per-class
sections **pointing at it rather than restating it**. That is #717's *no second copy of the mapping*
satisfied by construction rather than by discipline, and it is
`reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`'s existing arrangement — a mapping in code
whose count `apa7.md` §7 already refuses to restate, on #143's terms, after that figure had stood
in three files.

### 6. The coverage finding is **reported and not graded**, and the thing that fails is the bind test

**The two rows this work produces are not the same kind of finding, and #715 decision 2 asks about
posture as though they were.**

The `requires-retrieval-date` row grades **the draft**. A missing retrieval date on an unarchived
database entry is a defect in the document in front of the scanner, fixable in one edit. It enters
`KINDS` at exit 1 like every row beside it and needs no ruling.

The `uncovered-class` row's subject is **this repository's sheet**. A run citing a Cochrane review
before that section lands has behaved **correctly** — it looked the form up on APA's page, which is
what the sheet instructs. Failing it is the false-alarm-on-correct-work shape refused by
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
ruling 5, by `spelling_scan`'s suffix rules, by `case_study_scan`'s stop-criterion row and by
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) — and here it **blocks a
graded submission**, because `skills/discussion-post/SKILL.md:253` requires exit 0. A repository gap
would land on a student's coursework.

**So the row prints and never touches the exit status**, with bucket populations, states and the
`undecidable` remainder reported on every run rather than only when something fires, on
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling.

**What fails is `tools/test_reference_scan.py`.** The class table's `has_form` column is bound to
the sheet's own `##` headings **in both directions**: a class claiming a form the sheet has no
section for fails, and a section landing without joining the table fails. That is ruling 7's own
#220 objection answered exactly — its complaint is against *a prose declaration alone*, and the
bind is what stops the sheet's coverage claim being prose.

**ADR 0089 ruling 5's flag is worse than the report here, and the difference is where the finding
lands.** That flag exists where a finding still reaches a human who owed the work. Here **every
caller would pass it**, so the flag would record nothing while the row never fired and the
machinery was still paid for.

### 7. The sheet stays at `skills/practicum-case-study/reference/apa7.md`

#715 decision 4 asks whether the sheet moves. Measuring it shows **the sheet is not the anomaly, the
directory is**: `voice.md` is read by four skills and `rubric.md` by two, so `apa7.md` is the
third-most-shared file in one skill's `reference/` directory rather than the first.

**Moving `apa7.md` alone is the worst of the three options.** It repoints 81 references, fixes the
least-shared of the three sheets, leaves the real anomaly standing, and **removes the sheet from
`SKILLS_DIR.rglob("*.md")`**, so its step citations into `SKILL.md` stop being graded — a file
leaving a walk's population fails nothing, which is
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s subject arriving on a
move rather than on a new file.

The sheet gains a statement of its readers, bound by a test in both directions — which skills link
it against which skills it names. **Moving the whole shared set is a real question and is filed
separately**; nothing in #715's finding depends on it.

### 8. The census reads `scratch/` across every registered checkout and `output/` from the main checkout

**A census resolving through `repo_root.scratch_root()` returns a fraction and prints it as the
corpus.** [ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 1 is that there is one scratch root **per checkout that has one**, and that record states
that most of this repository's scratch material has lived in worktree roots. That failure on the
instrument whose whole purpose is making #715's own table re-derivable would be #143 rebuilt inside
#143's repair.

**The asymmetry between the two roots is derived, not a convenience.** `scratch/` is genuinely
per-checkout by ADR 0059; `output/` is single-homed **by policy**, enforced by
`docx_write.ensure_main_checkout`. Each half is read where its own governing rule says it lives.

The report prints checkouts enumerated, roots read and roots unreadable on every run, on
`adr_next.py`'s and `scratch_census.py`'s shape. **`scratch_census.py`'s two limits are inherited
unchanged and are stated rather than closed**: a separate clone has its own worktree registry and is
invisible, and material written outside every checkout is outside the walk.

### 9. A section carries a **synthesized** example and its own provenance line

§8's four parts generalize: a provenance line naming page, item number and read date; a worked
example; the abstracted entry form; a declared limit. **Part 2 does not generalize as written**, and
it is the one part of this build that touches a ruling made against a public repository.

[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223) ruled on 2026-08-18 that
this sheet reproduces **no APA prose at all**, and blessed its verbatim strings on a stated basis:
22 words and 19 words, publishers elided, *format demonstrations* rather than expression. §8 added a
third on the same footing. **Filling 23 sections on §8's shape makes that roughly 23 verbatim
strings, and #223's ruling was made about two.** A ruling about a public repository is not extended
on a quantity argument nobody has re-derived.

So part 2 is **this repository's own invented author, title and locator poured into APA's slot
order**. The form is a fact about a format; the string is this repo's. **The three existing verbatim
strings stay** — they are ruled, and they are not the question.

**The provenance line is not hoisted, and that is refused rather than merely not chosen.** It is
three facts that differ per section — which page, which item, read when — and hoisting them makes
one header sentence stand for 23 independent reads. That is the shape where the header stays true
while an individual section's read never happened and nothing says so. §8 got this right and it is
not tidied.

### 10. The mechanism ships before the sections, and the census carries no `--show`

**Everything in rulings 2 through 8 needs no APA page.** The classifier, the mapping, the class
table, the bind test, the census and ruling 4's row are buildable today with the table declaring a
form for **§2 and §8 alone**, which is true of the tree. So the mechanism is one ticket and the 22
sections are another.

**The split is what makes the gate prove itself.** The bind test and the census land **before** the
sections, so the mechanism is exercised against a sheet that genuinely covers two classes of
twenty-three, and each section landing is a state change something observes. Shipping both halves in
one change would ship the gate and its satisfied state together, which is #182 again — nothing would
ever have watched it fire.

**The census carries no `--show`, and this limb is ADR 0094's.** This session had already published
to the clinician that the census's output would *inherit* `reference_scan`'s 2026-08-19 pasteable
exception. ADR 0094 inverts the default — *a tool's `--show` output is unpasteable by default* —
and rules that *the module's own docstring is the only authority, and no second copy is kept
anywhere*. So inheriting a blessing is the precise thing that record forbids, and its own
measurement is that the derived copy of that roster had already drifted short by 2026-09-01.

**Its rulings are cited by their own words here rather than by number, and the reason is a defect
this record found.** That record writes each one as a bold `Ruling` **word** before the numeral,
where `declared_rulings` in `tools/test_skill_agreement.py` reads a bold numeral opening the line —
so it declares **none**, and a coordinate naming any of its six resolves to nothing. This is the
first record to cite it, which is how the defect surfaced. It is filed rather than repaired here,
on [#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246)'s de-citing precedent,
because correcting another session's ratified record is not this grilling's to do.

**And describing it reproduced it.** The first draft of this paragraph wrote the resolvable
coordinate inside backticks to name what fails, and the resolver has no mention-versus-use rule the
way `spelling_scan.py` does — so the sentence explaining the defect **was** an instance of it, and
the suite stayed red on the paragraph reporting why. That is
[#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153)'s *describing the rule
broke the tool that checks the rule*, arriving on the citation resolver.

The remedy is not a second guarded aperture. The census's finding is *this bucket has no covered
class*, and the bucket name **is** the remedy; the entries themselves are the per-run row's
business, inside `reference_scan`, where the blessing and its guard already exist. So the census
prints bucket names, states and integers — every one drawn from the class vocabulary, a module
constant, and never from the corpus — and needs no flag at all, on `tracker_bodies.py`'s precedent.
**ADR 0094's default then applies to nothing, because there is nothing to bless.**

## Derived from precedent rather than ruled

* **The house exit convention.** 0 clean, 1 finding, 2 for every way of not having scanned, in both
  the row and the census. Stated in a dozen modules identically and not re-decided here.
* **The census is a separate `tools/` module** importing `reference_scan.read_document` and the
  classifier, on `research_ledger.py:42`'s precedent. A different population, a different reader and
  a different meaning of a non-zero status.
* **The `uncovered-class` row is declared *not* in `reference_scan.BODY_ROWS`, in the diff that
  introduces it.** ADR 0094's *the one claim here that is load-bearing already carries a check*
  records #678's row doing exactly that hours before that record,
  and calls a blessing that survives a change written by somebody who had never read the record the
  only kind worth resting a ruling on.
* **The bucket vocabulary is `CONTEXT.md`'s.** ADR 0094's *the class vocabulary is `CONTEXT.md`'s
  and is named there rather than here* rules that the record of *what the
  classes are* belongs in the glossary while the record of *what the rule is* belongs in the ADR,
  and that neither restates the other.

## What none of this reaches, declared rather than left to be found

**Three claims about APA's page are inherited from #715 and #717 and were not re-derived here**,
because the in-app browser is denied the host: that the *Nursing Student References* page carries
**23 items**; that **StatPearls** is among them and takes a required retrieval date; and that
guidelines, agency reports, ethics codes, position statements, fact sheets and DailyMed drug
information take none. **Ruling 4's whole reopening rests on the StatPearls limb.** If the page says
otherwise at the read, #717 closes with #241 and nothing else in this record moves. The build checks
each at the read rather than inheriting it.

**`undecidable` buckets are permanent, not transitional.** A bucket spanning a covered class and one
outside the 23 stays undecidable however many sections land. The state is reported and is never a
finding, so nothing here ever says whether such an entry was right.

**A synthesized example is not checkable against APA's page by string comparison.** One that has
drifted from APA's slot order looks exactly like one that has not. §2 and §8 remain the only
anchored strings in the sheet, and every synthesized section's declared limit says so.

**The path still reads as `practicum-case-study`'s** to anyone who has not opened the file. Ruling
7's bind makes the *sheet* say otherwise; it does not make the *directory* say otherwise, and that
residue is the separate ticket's to close.

**An advisory line on a report nobody reads is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) one level up**, which is
the weakness ADR 0089 ruling 5 names about itself and which ruling 6 inherits whole. The corpus
census is the answer only to the extent somebody runs it.

**No corpus figure.** Neither the class split nor the recall share is stated in this record, and
neither is re-derivable from the base it was written on. They belong to the command on the day it is
run, which is what ruling 2's second reader exists to make possible.

**2026-09-05 correction.** [#759](https://github.com/mshamblin5150-code/clinical-skills/issues/759)
and [ADR 0133](0133-a-ruling-is-identified-by-its-ordinal-and-an-empty-parse-is-declared-rather-than-guessed-at.md)
record the widened ruling declaration grammar and why the quotations above remain unchanged.
