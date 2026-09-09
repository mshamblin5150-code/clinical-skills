# APA 7 — the rules this document actually uses

**Distilled, not downloaded.** The *Publication Manual* is copyrighted and cannot live in this
repo. What is freely published is APA Style's own rule pages, and this sheet is the handful of
rules a practicum case study rests on, each carrying the manual section it comes from so a reader
can go to the source rather than trust this file.

**Sections 1 through 7 were verified against apastyle.apa.org on 2026-08-18; section 6's rules on
paragraph and heading spacing were verified on 2026-09-08.** The manual-side audit and the
independent second read for each item are recorded in [apa7-coverage.md](apa7-coverage.md); a
digest change makes the affected verdict stale. A rule this sheet does not cover is looked up at
the source — **an APA rule is looked up, never recalled**, which is
[practicum-case-study](../../practicum-case-study/SKILL.md)'s anchor discipline arriving at the reference list.

**The fenced examples are APA's own, and they stay.** Ruled 2026-08-18 on
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223), against a public
repo rather than a private one. This sheet reproduces **no APA prose at all** — its
verbatim third-party strings are limited to the reference and citation forms needed for
the format demonstrations, drawn from the free rule pages with publishers elided where
the example supplies one. A reference format described in a sentence is not a reference
format. Everything else here is this repo's own wording with a section pointer beside it.

**The *Publication Manual* is the authority for this sheet.** It remains outside the repository
because it is copyrighted; the coverage registry records which manual material was read, what a
second reader tried to refute, and which exact sheet bytes that verdict governs. Public APA Style
pages remain legitimate supporting sources, but they are no longer the ceiling on this sheet.

**What this sheet is for.** *APA Format and Scholarly Writing* is 5 of the 100 points, and
[practicum-case-study](../../practicum-case-study/SKILL.md) step 7 requires the reference walk to run on every document. That
instruction needs a written rule behind it, or *"fix the reference list"* is a wish rather than a
check. **Ruled 2026-08-18**, and the words that settled it were the clinician's: *ordering the
differential is very important, but that shouldn't take the place of tidiness.*

**Readers:** the `practicum-case-study` and `discussion-post` skills. The former links this sheet
directly; the latter links it from its own workflow because the reference scanner is shared.

---

## 1. The reference list, mechanically

*Publication Manual* §§2.12, 2.18, and 9.43–9.49.

- Starts on **a new page** after the text.
- The label is **`References`**, **bold and centered**, including when the list has one entry.
  Never `Reference`, `Works Cited`, `Bibliography` or `Reference List`. The renderer still styles
  the legacy singular defensively, but `reference_scan.py` reports it as the wrong APA label.
- Each entry is **one paragraph, flush left**, with a **0.5 inch hanging indent applied to the
  whole list**.
- **Double spaced throughout, with no extra space between entries.**
- Page numbers sit in the **top right corner of every page**, the reference list included.
- **Alphabetized letter by letter from the first significant word of the entry** — normally the
  first author's surname, including any surname prefix. Disregard capitalization, spaces, and
  punctuation. Ignore a leading `A`, `An`, or `The` for alphabetizing while retaining it in the
  printed entry. Where a work has no author, the title moves to the front and the entry
  alphabetizes by the title; spell numerals out conceptually for that comparison. For one first
  author, place sole-author works before multiple-author works, order identical author sequences
  by date, and compare the first differing later author when sequences differ. For identical
  surnames, initials distinguish first authors. Generational suffixes follow birth order rather
  than lexical order.

APA's published Smithsonian example applies the same rule to a group author
([McAdoo, 2022](https://apastyle.apa.org/blog/alphabetize-nonsignificant-words)):

```markdown
# In-text citations

Raskin (1978), The Smithsonian Institution (n.d.), and Steinbeck (1939) are cited.

## References

Raskin, E. (1978). *The Westing game*. Avon Books.
The Smithsonian Institution. (n.d.). *Our organization*. https://www.si.edu/about/administration
Steinbeck, J. (1939). *The grapes of wrath*. Penguin Books.
```

**`Roughly alphabetical` is not the rule, and this sheet retires that phrase.**
[style.md](style.md) §10 described the corpus as roughly alphabetical, which was an accurate
description of ten submitted documents and was never a statement of the standard. Sorted is sorted.

## 2. Reference form: UpToDate article

APA publishes a reference example for this database specifically, which is worth knowing before
inventing a form for it. *Publication Manual* §10.1.

**Form provenance:** This form was read from the *Publication Manual*, not APA Style's *Nursing
Student References* page, so it carries no page-item provenance line.

```
Bordeaux, B., & Lieberman, H. R. (2020). Benefits and risks of caffeine and caffeinated
    beverages. UpToDate. Retrieved February 26, 2020, from https://www.uptodate.com/contents/...
```

Parenthetical: `(Bordeaux & Lieberman, 2020)`. Narrative: `Bordeaux and Lieberman (2020)`.

Four rules carry it, and **two of them the corpus does not currently follow**:

- Format the entry **like a periodical article**.
- **Italicize the database name in the reference**, the way a periodical title is italicized — so
  it is *UpToDate*, not plain `UpToDate`. **Do not italicize it in running text.** The corpus
  italicizes it nowhere; this is the first of the two gaps.
- **The date element is the year of the topic's last update.** Not the year it was read, and not
  the year the reference list was assembled. The companion evidence document states each topic's
  own revision date, and that is where this comes from. This is the second gap, and it is the
  mechanism behind [style.md](style.md) §10's observation that one topic appears in the corpus
  under three different years — the topic really was revised three times, and the entries were
  right to differ.
- **Retrieval-date behavior is declared by `reference_scan.APA_SOURCE_CLASSES`'s
  `takes_retrieval_date` column.** This form includes the date because the content is designed to
  change and versions of it are not archived. See §4.

## 3. Same author, same year — the `a`/`b` rule

*Publication Manual* §8.19, with the ordering rule at §9.47.

**The letters are assigned from the reference-list order.** For works by the same authors in the
same order, compare the date elements first: a year-only work precedes a more specific date in that
year, and fuller dates proceed chronologically. Only works with identical dates are ordered by
title, ignoring an initial `A`, `An`, or `The`; explicitly numbered parts in one series retain
series order. They are not lettered by citation order, page order, or discovery order.

- **The same *authors*, not the same first author.** The rule is scoped to an identical author
  string. `Hsu, K. (2026)` and `Hsu, K., & Khosropour, C. (2026)` are two author strings, and
  `(Hsu, 2026)` and `(Hsu & Khosropour, 2026)` already tell them apart in text — so **neither takes
  a letter, and adding one is the defect.** `tools/reference_scan.py` reads the rule this way, and
  it did not at first: it grouped on the first surname alone, which is the right key for matching
  an in-text citation and the wrong one here. It failed a correct list *and* would have taught a
  run to write `2026a`/`2026b` onto two entries APA requires to carry neither.
- **Ignore a leading `A`, `An` or `The` in either title** when alphabetizing.
- The year–letter combination is used in **both** the in-text citation **and** the reference list
  entry. Fixing one and not the other is the defect, not the fix.
- A republished, translated, or reissued work uses both publication years in text and the
  republication year in the entry; §31 owns that two-date rule.
- **Use only the year with its letter in text**, even where the reference list entry carries a
  fuller date.
- Undated works by one author take **`n.d.-a`, `n.d.-b`** — with the hyphen.
- Works accepted for publication use **`in press`** in both the entry and the in-text citation.
  When same-author works need letters, the same suffix rule gives `in press-a` and `in press-b`.
  Within one author's list, §9.46 orders works with no date first, dated works next, and in-press
  works last.

APA's own worked example, which shows the ordering doing something non-obvious:

```
Scorsese, M. (Director). (2019a). The Irishman [Film]. <publishers elided>
Scorsese, M. (Director). (2019b). Rolling thunder revue [Film]. <publishers elided>
```

*The Irishman* is `2019a` because **`Irishman` sorts before `Rolling`** — the leading *The* is not
counted. Cited together: `(Scorsese, 2019a, 2019b)`.

**Two UpToDate topics revised in the same year by the same authors is the shape this fires on
here**, and it is ordinary rather than exotic.

## 4. Retrieval dates

*Publication Manual* §9.16; source-category applications appear throughout Chapter 10.

**Most references do not take one.** A retrieval date belongs only where **both** hold: the work is
inherently designed to change over time, **and** an unarchived version of it is what is being
cited.

Write `Retrieved Month Day, Year, from URL`, immediately before the URL. A DOI is not APA's archive
test: fixed works without DOIs commonly omit retrieval dates, and a changing cited form is not made
fixed merely by carrying a DOI. Decide from the cited version and source category.

- **The per-class answer lives only in `reference_scan.APA_SOURCE_CLASSES`'s
  `takes_retrieval_date` column.** A class section points to that column rather than restating a
  second mapping here.
- A society guideline PDF, a journal article, a USPSTF statement and a textbook **do not**. Adding
  one there is a defect in the other direction, and a run that puts retrieval dates on everything
  is wrong on most of the list.
- **Local submission policy:** the retrieval date must be on or after the exam date. APA does not
  impose this exam-date comparison; it is the corpus's recurring defect and the one the clinician named himself:
  *"I more than likely wrote the retrieved by wrong."*

## 5. Every entry is cited, and every citation is listed

*Publication Manual* §2.12, and it runs in both directions:

- **Every work cited in the text appears in the reference list.**
- **Every work in the reference list is cited in the text.** Where one is not, APA's instruction is
  to *either* cite it in the body *or* delete the entry — and this skill's ruling is **delete**,
  because a reference list is what the argument rests on and the rubric scores *Integration* rather
  than reading. That ruling predates this sheet; what the sheet adds is that APA agrees with it.

Exceptions include personal communications and general mentions of a website or common software,
which can be text-only; the source studies in a meta-analysis, which may be marked in the list
without separate body citations; classical or religious works whose standard parts suffice; and
epigraphs or research-participant quotations handled under the manual's specific rules.

A two-date citation for a republished, translated, or reissued work still resolves to the one entry
for the version used; see §31.

## 6. What the renderer applies, and what it does not

`tools/docx_write.py` is what turns the Markdown into the submitted `.docx`. **It applies every
§1 rule that is a matter of *format*** — plus the two rules from elsewhere in the manual that a
renderer can reach — and what it does not is written down rather than assumed away:

| APA rule | `docx_write.py` | Word calibration and tripwire |
| --- | --- | --- |
| Times New Roman 12 pt, one permitted accessible font, used consistently with double spacing subject to §2.21's exceptions and 1 inch margins | applied | `body-defaults` |
| 0.5 inch hanging indent on the whole reference list | applied | `reference-hanging-indent` |
| No extra space between entries | applied | `reference-no-extra-space` |
| `References` heading **bold** | applied | `reference-heading-bold` |
| `References` heading **centered** | applied | `reference-heading-centered` |
| `References` heading at **body size**, 12 pt | applied — every heading level is 12 pt | `reference-heading-body-size` |
| Reference list **starts on a new page** | applied | `reference-page-break` |
| **Page numbers**, top right of every page | applied | `page-number-header` |
| The legacy singular **`Reference`** heading gets the hanging indent | applied defensively, but the label is not APA-compliant | `singular-reference-hanging-indent` |
| Every body paragraph takes a **0.5 inch first-line indent** (§2.24) | applied — and *only* a body paragraph: a heading, a list item, a reference entry and a table cell each take none | `body-first-line-indent` |
| **No extra space before or after paragraphs** (§2.21) | applied — consecutive body paragraphs remain continuously double spaced without an empty paragraph between them | `body-no-extra-space` |
| **No blank lines above or below headings**, even at the end of a page (§2.21) | applied — a heading is adjacent to the body paragraph that follows it | `heading-no-blank-lines` |
| A marked **block quotation of 40 words or more** starts on a new line, has no quotation marks added, stays double spaced with no extra space, and is indented 0.5 inch from the left | applied — an authored `> ` line becomes one `BlockQuotation` paragraph and the marker is consumed | `block-quotation-format` |
| A table uses **horizontal rules only**, with no grid or vertical dividers (§7.17) | applied as a narrower three-rule subset: above and below the heading row and below the last row; APA also allows a rule above a spanner and an optional rule before a summary | `table-horizontal-rules` |

**Word is the evidence for every verdict in both tables.** The dated observation and the
semantic XML shape it covered are in
[`word-renderer-calibration.json`](word-renderer-calibration.json). Re-derive them with
`python tools/docx_word_probe.py --word`, the maintainer-only command that opens the probes
through Word COM and prints what Word reports. Word is not on the consumer or CI path. The
permanent test opens no Office process: it compares the current shapes with all calibration keys
and says the affected row must be retaken when one leaves the measured set. This is
[ADR 0008](../../../docs/adr/0008-word-is-a-one-time-calibration-instrument.md).

**The body-first-line-indent and table-horizontal-rules rows are
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220), landed 2026-08-19, and
they were first checked the same way the already-present rows were** — a document
rendered and its `word/document.xml` and `word/styles.xml` read, not the renderer's source. What
that read: exactly one paragraph of a document carrying a heading, a body paragraph, two list
items, a three-column table and a reference entry took `w:ind w:firstLine`, and it was the body
one; the table's `tblBorders` came back `single` on top and bottom and `none` on all four of
`left`, `right`, `insideH` and `insideV`, with the rule under the header set on that row's cells,
where `insideH` would have drawn it between every pair of body rows as well.

**The table row was a decision rather than a fix**, on the same footing as the heading-size row
below, and the clinician ruled it on 2026-08-19: **horizontal rules unconditionally**, not a
switch. An APA table is not the only kind of table a Markdown document can hold, but the only
consumer of this renderer is an APA document — and a parameter no caller passes is a branch
nothing honestly tests.

**The rows that preceded #220 were first checked the same way, on a different day** — by rendering
a document and reading `word/document.xml`, `word/styles.xml` and `word/header1.xml`, not inferred
from the source. 2026-08-18, on
[#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217)'s branch. **Those XML
reads were renderer-shape checks, not Word measurements.** Five of those
rows read *not applied* earlier the same day, and the others were already green — the table
was rechecked rather than inherited because a row's verdict expires when the renderer changes,
which here was hours rather than days.

**Both dates have to stay attached to their own rows, and that is not a pedantry.** A single
*"every row above was measured"* sentence is what this paragraph said until #220 added two rows
above it, at which point it silently dated 2026-08-19 measurements to 2026-08-18 and called eleven
rows nine — [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape,
inside the paragraph two lines below that exists to record it happening once already. Caught by
`/code-review` on #220's branch, by both of its axes independently.

**That sentence said *every* row and *the day before*, and both were wrong.** It was caught by
`/code-review` against the previous version of this very table, which is the check working: a
paragraph arguing that figures must be re-derived had itself been written from memory of a table
sitting four lines above it.

**Two of those nine came out differently than the ticket asked, and both are worth knowing.** The
`Reference` singular was not on #217 as filed — it was found by `/code-review` on the branch that
wrote this sheet, and it is a gap **this sheet created**, because §1 above is what blesses the
singular. And the heading-size row was filed as *"worth a decision rather than a fix"*; the
clinician ruled it on 2026-08-18, and the answer was wider than the row — **every supported
heading level receives its available APA styling**, level 1 bold centered, level 2 bold flush
left, level 3 bold italic flush left, and level 4 bold indented. The required Level 4 run-in
behavior and all of Level 5 remain outside the renderer's subset, as the table below states.

**What is still not applied**, so the list above does not read as the whole of APA:

| APA rule | `docx_write.py` | Word calibration and tripwire |
| --- | --- | --- |
| A **title page** — title, author, affiliation, course, instructor, due date | **not applied**, and not mechanical: none of those six values is in the Markdown | `title-page` |
| APA level 4 and 5 headings are **run-in** | **not applied** — Markdown gives a heading its own line, so level 4 renders as the indented bold paragraph it otherwise is, and level 5 is not in the subset | `run-in-headings` |
| The list is **alphabetized** (§1) | **not applied**, and declined rather than pending — sorting is an *edit to the document*, not a format applied to it, and this renderer changes no word it is handed. `tools/reference_scan.py` grades the order instead, its `list-not-sorted` row | `reference-alphabetization` |
| Each entry is **one paragraph** (§1) | **not applied** — every non-blank line becomes its own paragraph, so a hard-wrapped entry renders as two and the second hangs on nothing. Joining them is an edit on the same terms as sorting; [practicum-case-study](../../practicum-case-study/SKILL.md) step 7 catches it as an author defect | `reference-single-paragraph` |
| **Additional paragraphs within one block quotation** take an additional 0.5 inch first-line indent | **not applied** — each `> ` line is its own paragraph and the Markdown carries no signal that groups several lines into one quotation, so the renderer does not guess which line is a later paragraph in the same block | `block-quotation-subsequent-paragraph-indent` |

**The alphabetization and one-paragraph rows are not #220's, and they were on neither table before
it** — they are a gap that ticket's repair surfaced. This paragraph used to say the renderer applied *most of* §1, which
was true and vague; rewriting it into a claim a reader can check is what showed that two of §1's
bullets had never been recorded in either direction. **The lesson is the one #220 is about**: an
unfalsifiable summary hides a gap exactly as well as a wrong list does, and nothing had to go
stale for it to happen.

**Each original row is a statement about what this renderer is *for*** rather than a fix somebody
has not got to. The title page is a `practicum-case-study` question about where six course values
come from before it is a renderer question; the run-in heading is a limit of Markdown; and the
last two are the same ruling twice — **a renderer formats, it does not rewrite**. All four are
recorded here rather than filed. The subsequent-paragraph row is #815's separate declaration that
the authored markup does not expose which consecutive paragraphs belong to one source quotation.

**This table is no longer a second copy of a list, and that is #220's other half.** The same list
sat in `tools/docx_write.py`'s docstring, and a **prose** edit to either failed nothing — a code
regression fails a behavior test, so the direction that was uncovered was the one where the two
files quietly disagree and the reader who is misled is the one who checked the file nearer to hand.
It is `docx_write.NOT_APPLIED` now, one object, on `REFERENCE_HEADING`'s precedent, and
`tools/test_docx.py` asserts this table names the same items in both directions. #323 executes
every declared limit against the rendered archive. **Neither mechanism establishes what Word
draws.** #424 adds that independent measurement and a Word-free shape tripwire for every row;
a new row fails until it gains both a calibration identity and a dated Word record.

**None of these is worth more than a point, and they are still real.**
**A rendered `.docx` is not an APA-formatted document**, which is [practicum-case-study](../../practicum-case-study/SKILL.md) step 9's
sentence arriving one level down — and it is no less true for the rows that went green above,
because what a renderer cannot check is whether the entry it indented so carefully is a real
source.

---

## 7. What a command reads off this sheet, and what stays a reading

`tools/reference_scan.py` grades a finished draft's reference list against most of the sections
above — the label in §1, the sorting in §1, the `a`/`b` ordering in §3, where a retrieval date
belongs and where it is a defect in §4, the italics in §2, and both directions of §5. **This sheet
owns the rules and that command is a second *reader* of it, never a second copy**, which is why a
row it applies is written out in [practicum-case-study](../../practicum-case-study/SKILL.md) step 7 as well: a harness with no Python
walks the table by eye and reaches the same verdict.

A form section's heading uses `## <n>. Reference form: <class name>` exactly; the class-name tail
is the published `APA_SOURCE_CLASSES` vocabulary term rather than a paraphrase.

**What stays a reading, and it is a list rather than a paragraph now.** Each row is a rule this
sheet states that no command grades, so a run walks it by eye — and since
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) the walk is not left to
memory either: [practicum-case-study](../../practicum-case-study/SKILL.md) step 9 names the row `the reference list, the part no command
reaches` and `tools/checks_ledger.py` expects it, so a run that returns no verdict on that row fails. **One row and one verdict for all three**, which is the honest width of it — a run that read only the UpToDate years and wrote `clean` discharges the row, and no command can tell. What the grader catches is a run that never looked at all.

| What stays a reading | Why no command reaches it |
| --- | --- |
| The **republished original publication date** | §31's original date element is parsed and not compared with the entry. APA's own Gilgamesh example reverses the range between its entry and citation, so joining the halves would fail the source that defines the rule |
| An **author-shaped slash span** | Grammar alone recognizes a span such as `(Cohort A, 2013/2014)`, which can raise `unlisted-citation` even when the span is not a citation. The measured corpus supplied no such false positive |
| An **unwarranted retrieval date** on a guideline, a statement or a textbook | §4 says those take none. The command refuses one only when a committed source classifier settles that the cited form is fixed. DOI presence alone is not the archive test, and an unresolved URL cannot distinguish a stable PDF from a page designed to change |
| **The UpToDate last update year** | §2's date element is the topic's own last update year, not the year it was read, and the same topic appears in one corpus under three years. Which is which is in the companion evidence document, which the command never sees |
| **Whether the source exists and says so** | Whether an entry is a real source saying what the sentence citing it says. That is [#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231), answered **before the draft exists**: `tools/research_ledger.py` grades a year an agent read off the page and a refutation a second agent returned |
| **legal form and authority validity** | The command recognizes a narrow statute/regulation subset plus date-free constitutional locators and full-date treaty forms. It does not validate cases, legislative materials, proposed rules, executive orders, patents, parallel reporters, official-version choice, state-specific form, or current legal status |

**That table is `reference_scan.NOT_REACHED` and this is not a second copy of it**, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s repair arriving one
artifact over: the same list sat in this sheet and in the module's docstring, and a **prose** edit
to either failed nothing, so the reader who was misled was the one who checked the file nearer to
hand. `tools/test_reference_scan.py` asserts the two name the same items in both directions. **That
bind still cannot establish whether a row's verdict is true**, so #323 drives a synthetic draft
through the scanner for every current row and makes a new row fail until it gains its own
measurement.

**#241's first row was ruled a reading rather than left open, and the option it declined is worth
recording.** The proposal was to join each entry to its `tools/research_ledger.py` record and read
the `SOURCE` class off it. `peer-reviewed` and `society guideline` map onto §4's list cleanly;
`government` covers a USPSTF statement, which takes no retrieval date, and a public-health page
designed to change, which takes one, and `tertiary reference` covers UpToDate and a textbook, which
take opposite answers. A row keyed on either of those two would fail a **correct** entry, and a
guessed answer here is worse than a blank one.

**How many of the classes settle it is `reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`'s to
say, and is deliberately not counted here.** This paragraph stated the number, and so did
`CLAUDE.md` and the module's own docstring — one figure in three files with nothing re-deriving it,
which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside
the change whose subject is a list that had been copied into two. Caught by `/code-review` and by
the tracker sweep independently; the sharper form is theirs, that the same change withheld the row
count beside it on #143's terms and then stated this one. ADR 0110 deliberately widened the
closed vocabulary for deck runs and moved the equality: a test now asserts that the mapping's keys
are exactly `research_ledger.SOURCE_CLASS_VOCABULARY`. Each signed bar selects its permitted subset,
so the fifth class does not silently loosen a clinical run.

**This was the third copy of that claim and the one the correction missed.** `reference_scan.py` and
`CLAUDE.md` were both fixed when #218 and #231 met; a sheet under `skills/` was outside what that
sweep had open, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)
again. Found by the merge rather than by either branch.

## 8. Reference form: State nursing practice act (NPA)

**Provenance:** APA Style's *Nursing Student References* page, item 14, read 2026-08-30;
*Publication Manual* §§11.3 and 11.5, read 2026-09-08.

APA's published example is a state nursing regulation:

```text
Professional and Vocational Regulations, 16 CCR § 1481 (2023). https://...
```

Its parenthetical citation is `(Professional and Vocational Regulations, 2023)`, and its
narrative citation is `Professional and Vocational Regulations (2023)`. This example's regulation form is:

```text
Name of Regulation, Title number Source § Section number(s) (Year). Optional URL
```

The legal source name is required; a section-only entry is not this form. A statute instead names
the act and cites its official compilation or, when not codified or scattered across titles, its
public-law and session-law source. The year is the publication year of the compilation cited, not
automatically the enactment year or a year embedded in the act's name. A URL may aid retrieval but
does not replace the official legal locator.

The in-text form uses the entry's first element as its author element and the entry's publication
year as its date element. A long title may be shortened only enough to remain an unambiguous pointer
to the entry. A year embedded in the name of an act remains part of that first element;
it does not replace the publication year. For example, an entry beginning `Consolidated
Appropriations Act, 2023` and published in 2022 is cited as `(Consolidated Appropriations Act,
2023, 2022)`.

A corpus instance follows APA's pattern with West Virginia's codification:

```text
Eligibility for prescriptive authority, W. Va. Code § 30-7-15b (2016). https://...
```

Chapter 11's categories do not collapse into this form. Cases retain the first reporter page,
parallel citations, court and history information; case names are roman in the list and italic in
text. Legislative materials, proposed and codified regulations, executive orders, patents,
constitutional provisions, charters, and treaties each have distinct slots. A whole constitution
is ordinarily mentioned only in text, whereas an article or amendment receives its legal form; a
current provision may be date-free and a repealed amendment carries repeal information. Every
authority must be retrievable and checked for current legal status. The scanner can test only its
declared structural subset and cannot certify good law.

**Configured reader boundary.** The implemented limit is owned by
`discussion_artifact.LEGAL_READER_NOT_REACHED`; this sheet points to that object and does not
restate its entries.

---

## 9. Reference form: Journal article

**Provenance:** APA Style's *Nursing Student References* page, item 1, read 2026-09-04.

**Synthesized example:** Rivera, L. M., & Chen, T. P. (2026). Preparing rural clinics for extreme
heat. *Journal of Community Nursing, 18*(2), 41–49. https://doi.org/10.1000/jcn.2026.14

**Abstracted entry form:** Author, A. A., & Author, B. B. (Year). Title of article. *Journal Title,
volume*(issue when available), page range. DOI when present; otherwise retain a URL for a
nondatabase article and omit the ordinary academic-database name and URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the local
sheet records the observed slot order, not a copied APA example or proof that any source exists.

## 10. Reference form: Journal article with an article number

**Provenance:** APA Style's *Nursing Student References* page, item 2, read 2026-09-04.

**Synthesized example:** Morgan, D. R., & Patel, S. N. (2025). Simulation coaching for novice
preceptors. *Clinical Learning Review, 2025*, Article 734921. https://doi.org/10.1000/clr.734921

**Abstracted entry form:** Author, A. A. (Year). Title of article. *Journal Title, volume*(issue when
available), Article number. DOI when present; otherwise retain a URL for a nondatabase article and
omit the ordinary academic-database name and URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the local
sheet records the article-number slot rather than reproducing APA's demonstration.

## 11. Reference form: Cochrane review

**Provenance:** APA Style's *Nursing Student References* page, item 4, read 2026-09-04.

**Synthesized example:** Okafor, I. J., Singh, R., & Bell, M. T. (2026). Telephone follow-up after
same-day procedures. *Cochrane Database of Systematic Reviews*.
https://doi.org/10.1000/14651858.CD010101.pub2

**Abstracted entry form:** Author, A. A. (Year). Title of review. *Cochrane Database of Systematic
Reviews*. https://doi.org/xxxxx

**Declared limit:** The synthesized example is not string-checkable against APA's page; the form
allows version-dependent journal details when the cited copy displays them.

## 12. Reference form: StatPearls

**Provenance:** APA Style's *Nursing Student References* page, item 5, read 2026-09-04.

**Synthesized example:** Ellis, J. K. (2025). Community-acquired skin infection. *StatPearls*.
Retrieved September 4, 2026, from https://www.statpearls.example/point-of-care/24680

**Abstracted entry form:** Author, A. A. (Year). Title of entry. *StatPearls*. Retrieved Month Day,
Year, from URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the live
page established the retrieval-date slot but not this invented author, title, or locator.

## 13. Reference form: Authored or edited book

**Provenance:** APA Style's *Nursing Student References* page, item 6, read 2026-09-04.

**Synthesized example:** Allen, R. P., & Vega, M. L. (Eds.). (2024). *Foundations of ambulatory
nursing* (3rd ed.). North Valley Press.

**Abstracted entry form:** Author, A. A. (Year). *Title of book* (Edition). Publisher. DOI when
present, or a nondatabase ebook URL; omit an ordinary academic-database name and URL. An edited
book places `(Ed.)` or `(Eds.)` after the editor name

**Declared limit:** The synthesized example is not string-checkable against APA's page; the form
does not establish authorship, edition, publisher, or locator for a real book.

## 14. Reference form: Chapter in an edited book

**Provenance:** APA Style's *Nursing Student References* page, item 7, read 2026-09-04.

**Synthesized example:** James, P. R., & Soto, E. L. (2024). Medication reconciliation. In N. K.
Brooks & A. D. Shah (Eds.), *Handbook of transitional care* (2nd ed., pp. 88–109). Harbor Press.

**Abstracted entry form:** Chapter Author, A. A. (Year). Title of chapter. In E. E. Editor (Ed.),
*Title of book* (Edition, pp. xx–xx). Publisher. DOI when present, or a nondatabase ebook URL; omit
an ordinary academic-database name and URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; it records
the chapter-to-container relationship without copying APA's example.

## 15. Reference form: Report by a government agency or other group author

**Provenance:** APA Style's *Nursing Student References* page, item 8, read 2026-09-04.

**Synthesized example:** Mountain State Office of Rural Health. (2026). *Access to primary care in
frontier counties* (Report No. 26-04). Department of Community Health.
https://health.example/reports/frontier-care

**Abstracted entry form:** Group Author. (Year). *Title of report* (Report number). Parent Agency or
Publisher when different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the form
does not prove which agency authored or published a real report.

## 16. Reference form: Clinical practice guideline with a group author

**Provenance:** APA Style's *Nursing Student References* page, item 9, read 2026-09-04.

**Synthesized example:** Society for Community Respiratory Care. (2025). *Clinical practice
guideline for home inhaler teaching*. https://guidelines.example/home-inhaler-teaching

**Abstracted entry form:** Guideline Group. (Year). *Title of clinical practice guideline*. Site
Name when different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the form
does not establish that a named organization issued or updated a guideline.

## 17. Reference form: Clinical practice guideline by individual authors at a government agency, published as part of a series

**Provenance:** APA Style's *Nursing Student References* page, item 10, read 2026-09-04.

**Synthesized example:** Ford, A. L., Nguyen, P. T., & Cole, J. R. (2026). Improving adult vaccine
access in mobile clinics. *Public Health Practice Reports, 12*(4), 201–209.
https://doi.org/10.1000/phpr.2026.204

**Abstracted entry form:** Author, A. A. (Year). Title of report article. *Government Series Title,
volume*(issue), page range. DOI or URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the live
form reflects the series' current journal-article presentation and must follow the cited issue.

## 18. Reference form: Ethics code

**Provenance:** APA Style's *Nursing Student References* page, item 11, read 2026-09-04.

**Synthesized example:** Association of Community Nurse Educators. (2026). *Code of ethics for
community-based teaching*. https://ethics.example/community-nurse-educators

**Abstracted entry form:** Group Author. (Year). *Title of ethics code*. Publisher or site name when
different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; it does not
establish the title, date, publisher relationship, or section language of a real code.

## 19. Reference form: Position statement

**Provenance:** APA Style's *Nursing Student References* page, item 12, read 2026-09-04.

**Synthesized example:** Coalition for Safe Ambulatory Care. (2026, May 14). *Position statement on
plain-language discharge instructions*. https://policy.example/plain-language-discharge

**Abstracted entry form:** Group Author. (Year, Month Day). *Title of position statement*. Publisher
or site name when different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the date
precision and author-publisher relationship must be read from the actual statement.

## 20. Reference form: Fact sheet

**Provenance:** APA Style's *Nursing Student References* page, item 13, read 2026-09-04.

**Synthesized example:** Office of Neighborhood Health. (2025). *Preventing heat illness at outdoor
clinics* [Fact sheet]. Department of Public Health. https://publichealth.example/heat-clinics

**Abstracted entry form:** Specific Agency. (Year or n.d.). *Title* [Fact sheet]. Parent Agency.
URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the actual
document decides the responsible agency, available date, description, and parent source.

## 21. Reference form: Drug information

**Provenance:** APA Style's *Nursing Student References* page, item 15, read 2026-09-04.

**Synthesized example:** Northlake Therapeutics. (2026, February 8). *Glucofen—metformin tablet*
[Drug information]. DailyMed. https://dailymed.example/drug/glucofen

**Abstracted entry form:** Manufacturer or Drug Author. (Year, Month Day or n.d.). *Title of drug
information* [Drug information]. Website Name when different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; it supplies
no evidence about a real product, manufacturer, revision date, or DailyMed record.

## 22. Reference form: Lab or diagnostic manual

**Provenance:** APA Style's *Nursing Student References* page, item 16, read 2026-09-04.

**Synthesized example:** Bennett, H. J., & Flores, M. A. (2025). *Pocket manual of ambulatory
diagnostic tests* (6th ed.). Meridian Health Press.

**Abstracted entry form:** Author, A. A. (Year). *Title of laboratory or diagnostic manual*
(Edition). Publisher. DOI or stable URL when present

**Declared limit:** The synthesized example is not string-checkable against APA's page; it records
the book-form slots without establishing a real manual or edition.

## 23. Reference form: Medical dictionary

**Provenance:** APA Style's *Nursing Student References* page, item 17, read 2026-09-04.

**Synthesized example:** Monroe, K. T. (Ed.). (2025). *Dictionary of outpatient medicine* (5th
ed.). Meridian Health Press. https://dictionary.example/outpatient

**Abstracted entry form:** Author or Editor, A. A. (Role). (Year). *Title of medical dictionary*
(Edition or version) [Format when needed]. Publisher or App Store. URL when available

**Declared limit:** The synthesized example is not string-checkable against APA's page; the cited
dictionary's own medium determines which book, website, or application slots apply.

## 24. Reference form: Entry in a medical dictionary

**Provenance:** APA Style's *Nursing Student References* page, item 18, read 2026-09-04.

**Synthesized example:** Capillary refill. (2025). In K. T. Monroe (Ed.), *Dictionary of outpatient
medicine* (5th ed.). Meridian Health Press. https://dictionary.example/outpatient/capillary-refill

**Abstracted entry form:** Entry Author or Entry Title. (Year). Entry title when not used as author.
In E. E. Editor (Ed.), *Dictionary title* (Edition or version) [Format when needed]. Publisher or
App Store. URL when available

**Declared limit:** The synthesized example is not string-checkable against APA's page; attribution
and container details must be read from the actual entry and dictionary.

## 25. Reference form: YouTube Video

**Provenance:** APA Style's *Nursing Student References* page, item 19, read 2026-09-04.

**Synthesized example:** Clinic Skills Studio. (2026, March 3). *Building a clear medication list*
[Video]. YouTube. https://youtu.be/example-med-list

**Abstracted entry form:** Account Name. (Year, Month Day). *Title of video* [Video]. YouTube. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the actual
upload decides the account name, creation context, upload date, title, and locator.

## 26. Reference form: Podcast or podcast episode

**Provenance:** APA Style's *Nursing Student References* page, item 20, read 2026-09-04.

**Synthesized example:** Torres, M. (Host). (2026, April 18). Teaching with a mobile clinic (No. 12)
[Audio podcast episode]. In *Practice close to home*. Community Audio Network.
https://audio.example/practice-close-to-home/12

**Abstracted entry form:** Host, A. A. (Host). (Year, Month Day). Episode title (No. x) [Audio or
video podcast episode]. In *Podcast title*. Publisher. URL. For a whole podcast, use its year span,
italicized title, podcast description, publisher, and URL.

**Declared limit:** The synthesized example is not string-checkable against APA's page; whether the
work is an episode or whole podcast controls the date, title, and description slots.

## 27. Reference form: Doctor of nursing practice (DNP) project

**Provenance:** APA Style's *Nursing Student References* page, item 21, read 2026-09-04.

**Synthesized example:** Lewis, N. A. (2025). *Improving follow-up after urgent-care discharge*
[Doctor of nursing practice final project, Plains University]. Plains Digital Repository.
https://repository.example/dnp/2025/44

**Abstracted entry form:** Author, A. A. (Year). *Title of project* [Doctor of nursing practice
project description, Degree-Granting University]. Repository Name. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; the actual
repository record supplies the project description, institution, repository, date, and URL.

## 28. Reference form: PowerPoint slides or lecture notes

**Provenance:** APA Style's *Nursing Student References* page, item 22, read 2026-09-04.

**Synthesized example:** Kim, S. H., & Wallace, D. P. (2026, January 22). *Evaluating community
screening events* [PowerPoint slides]. Regional Nursing Education Network.
https://education.example/slides/screening-events

**Abstracted entry form:** Author, A. A. (Year, Month Day). *Title* [PowerPoint slides or lecture
notes]. Hosting Site. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; this public
locator form does not apply to course material unavailable to the reader.

## 29. Reference form: Webpage on a website

**Provenance:** APA Style's *Nursing Student References* page, item 23, read 2026-09-04.

**Synthesized example:** Office of Family Health. (2026, June 9). *Preparing for a telehealth
appointment*. Department of Community Services. https://services.example/telehealth/preparing

**Abstracted entry form:** Author. (Year, Month Day or n.d.). *Title of webpage*. Site Name when
different from the author. URL

**Declared limit:** The synthesized example is not string-checkable against APA's page; use this
form only when the work does not fit a more specific reference category.

## 30. Outside the nursing set: APA reference example index

**Provenance:** APA Style's general [*Reference Examples*
index](https://apastyle.apa.org/style-grammar-guidelines/references/examples), read 2026-09-04.

**Synthesized routing example:** A writer citing an original data set first leaves the nursing set,
selects **Data and Assessments**, and follows the index link for data-set references instead of
forcing the work into the webpage form.

**Abstracted selection form:** Identify the work itself → choose the narrowest applicable index
category → choose that work type → apply the linked example. Use the webpage category only when no
more specific category fits.

**Declared limit:** This index section routes a reader and supplies no citation form of its own; the
synthesized routing example is not string-checkable against APA's page and does not prove the
linked detail page's slots.

## 31. Two dates for republished, translated, reissued, religious, and classical works

**Provenance:** APA Style's [*Book/Ebook References*](https://apastyle.apa.org/style-grammar-guidelines/references/examples/book-references),
[*Religious Work References*](https://apastyle.apa.org/style-grammar-guidelines/references/examples/religious-work-references),
[*Citing classical and religious works*](https://apastyle.apa.org/blog/citing-classical-religious-works),
and [*How to cite translated works*](https://apastyle.apa.org/blog/citing-translated-works), read
2026-09-08.

**APA examples:**

| Reference entry | In-text citation | Matching year | `reference_scan` resolution |
| --- | --- | --- | --- |
| `Watson, J. B., & Rayner, R. (2013). Conditioned emotional reactions: The case of Little Albert (D. Webb, Ed.). CreateSpace Independent Publishing Platform. https://a.co/06Se6Na (Original work published 1920)` | `(Watson & Rayner, 1920/2013)` | `2013` | clean |
| `Watson, J. B., & Rayner, R. (2013). Conditioned emotional reactions: The case of Little Albert (D. Webb, Ed.). CreateSpace Independent Publishing Platform. https://a.co/06Se6Na (Original work published 1920)` | `Watson and Rayner (1920/2013)` | `2013` | clean |
| `Kübler-Ross, E. (with Byock, I.). (2014). On death & dying: What the dying have to teach doctors, nurses, clergy & their own families (50th anniversary ed.). Scribner. (Original work published 1969)` | `(Kübler-Ross, 1969/2014, foreword by Byock, p. xv)` | `2014` | clean |
| `Kübler-Ross, E. (with Byock, I.). (2014). On death & dying: What the dying have to teach doctors, nurses, clergy & their own families (50th anniversary ed.). Scribner. (Original work published 1969)` | `Kübler-Ross (1969/2014)` | `2014` | clean |
| `King James Bible. (2017). King James Bible Online. https://www.kingjamesbibleonline.org/ (Original work published 1769)` | `(King James Bible, 1769/2017, Song of Solomon 8:6)` | `2017` | clean |
| `King James Bible. (2017). King James Bible Online. https://www.kingjamesbibleonline.org/ (Original work published 1769)` | `King James Bible (1769/2017)` | `2017` | clean |
| `Alighieri, D. (2001). The divine comedy (H. F. Cary, Trans.). Bartleby. https://www.bartleby.com/20/ (Original work published 1909)` | `(Alighieri, 1909/2001, Inferno, Canto XIII, Lines 72–74)` | `2001` | clean |
| `The epic of Gilgamesh (M. G. Kovaks, Trans.). (1998). Academy of Ancient Texts. https://www.ancienttexts.org/library/mesopotamian/gilgamesh/ (Original work published ca. 2500–2750 B.C.E.)` | `(The Epic of Gilgamesh, ca. 2750–2500 B.C.E./1998, Tablet II)` | `1998` | clean |

**Abstracted date form:** Put both publication years in the in-text citation, separated by a slash,
with the earlier year first. The original element may carry `ca.`, an en-dash year range, and an era
marker. Match the citation to the reference entry on the second year, which is the republication
year in the entry. Use canonically numbered parts rather than page numbers when quoting classical
or religious works.

**Declared limit:** The original half is parsed but not graded: APA's own Gilgamesh entry gives
`ca. 2500–2750 B.C.E.` while its citation gives `ca. 2750–2500 B.C.E./1998`.

## 32. Block quotations and direct-quotation locators

**Provenance:** APA Style's [*Quotations*](https://apastyle.apa.org/style-grammar-guidelines/citations/quotations),
[*Direct Quotation of Material With Page Numbers*](https://apastyle.apa.org/style-grammar-guidelines/citations/quotations/page-numbers),
and [*Direct Quotation of Material Without Page Numbers*](https://apastyle.apa.org/style-grammar-guidelines/citations/quotations/no-page-numbers),
read in a browser on 2026-09-08.

A quotation of fewer than 40 words stays in the surrounding text and uses quotation marks. A
quotation of 40 words or more is a block quotation: start it on a new line, omit quotation marks,
indent the whole block 0.5 inch from the left margin, double-space it, and add no extra space before
or after it. Additional paragraphs within the same quotation take another 0.5 inch first-line
indent; the renderer's declared limit for that form is in §6.

For a parenthetical citation, put the citation after the quotation's final punctuation and add no
period after the closing parenthesis. For a narrative citation, put the author and year before the
quotation and only the locator in parentheses after the quotation's final punctuation. Citation
placement is a reader-owned check: `case_study_scan` grades that a cited quoted span at the
40-word threshold has authored `> ` markup, not where its citation sits.

Ordinary scholarly direct quotations carry the author, year, and a locator. Epigraphs and
participant quotations follow their own identification rules, and a general website mention is
not automatically a quotation citation. Use `p.` for one page and `pp.` for
multiple pages, an en dash for a continuous range, and a comma between discontinuous pages. When a
work has no page numbers, use the heading or section name, a paragraph number counted by hand, or
both; use a timestamp for audiovisual material. For religious and classical works, use the
canonically numbered book, chapter, verse, line, canto, or comparable part instead of a page. See
§31 for the reference and two-date form for republished, translated, religious, and classical
works; this section does not restate it.

Quote the source exactly, correcting only under the manual's disclosed mechanisms: an inserted or
changed capital letter can be bracketed, omissions take ellipses where needed, and emphasis added
by the writer is identified. Preserve errors with `[sic]` only when necessary to prevent confusion.
Nested quotation marks change with whether the quotation is inline or blocked, and a quotation
embedded in the syntax of the writer's sentence may require only the punctuation demanded by that
sentence.

## 33. Bias-free descriptions of people

*Publication Manual* §§5.1–5.10.

Bias-free language is a decision method, not a frozen substitution list. Describe only attributes
that matter to the question, but use the most specific information the source or participant
supports. Prefer people's current self-designations, make comparison groups parallel rather than
treating one as the default, preserve agency, and report meaningful intersections instead of
silently reducing a person to one axis. Terminology and preferences change, so a person's or
community's stated preference controls when it is known.

- **Age (§5.3):** use an exact age, a bounded range, or informative summary measures when they are
  available. Avoid treating older age as disease or using an age label that does not fit the
  population.
- **Disability (§5.4):** both person-first and identity-first language can be appropriate. Do not
  impose one order universally; follow expressed preference and describe capabilities and
  conditions precisely without confinement metaphors, slurs, euphemisms, or crude functioning
  labels.
- **Sex, gender, and pronouns (§5.5):** distinguish sex assigned at birth, gender identity, gender
  expression, and sexual orientation. Report the construct actually measured, use each person's
  name and pronouns, use singular *they* when gender is unknown or irrelevant, and do not presume a
  binary.
- **Research and clinical roles (§5.6):** choose the noun that matches the setting—participant,
  patient, client, respondent, or another specific role—and do not equate a person with a disease
  occurrence. Name who is at risk and the risk rather than leaving a broad risk label unexplained.
- **Race and ethnicity (§5.7):** treat them as distinct constructs, use self-identified and
  appropriately specific national, regional, racial, or ethnic terms, capitalize group names, keep
  comparisons parallel, and avoid essentializing umbrella labels.
- **Sexual orientation (§5.8):** describe orientation rather than a supposed preference, match any
  umbrella abbreviation to the groups actually discussed, define it when needed, and prefer a
  specific self-identification over a broader label.
- **Socioeconomic status (§5.9):** state the concrete dimensions available—such as education,
  occupation, income, housing, or environment—and their context. Do not use economic wording as an
  unstated proxy for race or ethnicity or frame structural constraints as individual deficits.
- **Intersectionality (§5.10):** report relevant identities together when their combination matters
  to the sample or interpretation; intersectionality is neither an additive score nor permission
  to attribute an outcome to one identity in isolation.

## 34. Mechanics of scholarly prose

*Publication Manual* §§6.1–6.52 and Tables 6.1–6.5.

Use one space after ordinary sentence and reference-element punctuation (§6.1). Apply periods,
commas, semicolons, colons, quotation marks, parentheses, brackets, slashes, and unspaced em and en
dashes according to the relation they express (§§6.2–6.10); a DOI or URL takes no terminal period,
and an en dash rather than a hyphen expresses a numeric range. Use the serial comma. A retrieval
date is punctuated as an exact date. Article and chapter titles are not put in quotation marks in
the reference list, and a bracketed work-form description follows the title when one is needed.

American spelling follows Merriam-Webster, with the APA Dictionary of Psychology controlling its
specialized vocabulary (§6.11). Choose one accepted variant consistently. Hyphenate permanent
compounds as the dictionary directs and temporary pre-noun compounds only when the hyphen prevents
misreading or joins one meaning; most post-noun and `-ly` adverb compounds remain open (§6.12 and
Tables 6.1–6.3).

Capitalize sentence openings, proper names, racial and ethnic group names, exact test names, formal
titles immediately before names, and the major words of headings (§§6.13–6.21). Lowercase generic
drug names, diseases, procedures, theories, variables, generic roles, and ordinary group labels
unless a proper name remains inside them. Reference-entry work titles use sentence case; periodical
titles retain title case.

Italicize standalone works, periodical titles and volume numbers, variables and statistical
symbols that call for italics, scientific taxa, and a newly defined term at first use (§§6.22–6.23).
Do not extend italics to the punctuation separating reference elements, familiar foreign phrases,
Greek letters, or routine emphasis; text that would itself be italic returns to roman when nested
inside an italic span.

Use an abbreviation only when it is familiar or repeated enough to help, define it at first use
unless it belongs to the manual's standard set, and define nonstandard abbreviations independently
inside each table or figure (§§6.24–6.31). Measurement symbols do not pluralize and normally follow
a number after a space; unit names are written out without a number, `L` is the standalone symbol
for liter, and day, week, month, and year remain written out even after numerals. Use `p.` and `pp.`
for page locators. Keep Latin abbreviations mainly inside parentheses, with the stated citation and
legal exceptions; do not use `ibid.`

Write 10 and above as numerals and zero through nine as words unless the value is a measurement,
statistic, percentage, ratio, date, age, time, score, money amount, or numbered series position
(§§6.32–6.39). Spell out a number that begins a sentence or heading. Separate adjacent numeric
modifiers for clarity, apply the same threshold to ordinals, use a leading zero only for quantities
that can exceed 1, and use commas in most values of 1,000 or more but not page numbers or other
identified exceptions. Numeric plurals take no apostrophe. Report justified precision; ordinary
exact *p* values use two or three decimals, and values below .001 use the less-than form.

Choose prose for a small set of values and a table or figure when comparison becomes clearer there;
the numerical bands in §6.40 are starting heuristics, not mandates. Cite uncommon, disputed, or
central statistical methods, display formulas that are novel or difficult to read in line, and
report enough information to understand and reproduce the analysis without duplicating a display
(§§6.40–6.48). State each confidence level, distinguish total *N* from subgroup *n*, use true minus
signs and appropriate operator spacing, and preserve every mathematical symbol and alignment the
work requires.

Lists must be grammatically and conceptually parallel (§§6.49–6.52). An inline series can use
parenthesized lowercase letters; complete ordered steps can use Arabic numerals and sentence
punctuation; unordered items can use bullets with punctuation matched to whether the items are
sentences, fragments, or parts of one continuing sentence. The practicum case study's stricter
prohibition on bullets is a house rule, not an APA prohibition.

## 35. Tables and figures

*Publication Manual* §§7.1–7.36, Tables 7.1–7.24, and Figures 7.1–7.21.

A table or figure must make a comparison, pattern, process, or other information materially easier
to understand; it must not merely repeat the prose or decorate it (§§7.1–7.3). Call out every
display by number and tell the reader what to notice, never by unstable page position such as
“above” (§7.5). Place it after its first callout or in the permitted end matter, according to the
assignment, and keep it self-contained, legible, accessible, and consistent with related displays
(§§7.4–7.6).

Every table has a bold number, an italic concise title, sentence-case column headings including a
stub heading, a real cell-based body, and only the notes needed to understand it (§§7.9–7.14).
Stub entries normally align left; other cells may center or align left for readability. Body cells
may be single, 1.5, or double spaced. Explain a dash used for missing data, use comparable precision,
and order notes as general, specific, then probability notes. Standard statistical and measurement
abbreviations are exempt from definition; define every other abbreviation within that display
(§§7.15–7.16). Use only functional horizontal rules—normally at the top and bottom, beneath column
headings, above spanners, and optionally before a summary—and never a full cell grid or vertical
dividers (§7.17). Repeat headings on later pages of a long table and split a table that remains both
too long and too wide (§7.18).

Every figure has a bold number, an italic concise title, a clear image, a legend only when symbols
need one, and explanatory notes when the image cannot stand alone (§§7.22–7.28). Image text is
normally 8–14 point sans serif. Axes, units, scales, error information, panels, symbols, meaningful
colors or patterns, and alterations must be labeled or explained. Avoid ornamental gridlines and
three-dimensional effects, ensure color is accessible, and keep like figures comparable in size
and scale (§§7.26–7.35). Specialized biological, electrophysiological, radiological, and genetic
figures additionally disclose the orientation, acquisition, processing, scale, coordinate, or
method details a reader needs (§§7.30–7.34).

A reprinted or adapted table or figure needs source credit in its note and a reference-list entry,
plus the copyright holder's permission when required (§7.7). The renderer cannot infer ownership,
permission, missing definitions, callout quality, or whether a display is necessary; those remain
reader-owned checks. The chapter's sample displays illustrate compliant shapes but do not license
copying their study-specific language or values.

## 36. Paper elements and student-paper format

*Publication Manual* §§2.1–2.28, Tables 2.1–2.3, and Figures 2.1–2.5.

The assignment determines whether student or professional elements apply. Every APA paper has a
title page; the student form identifies the title, author, affiliation, course, instructor, and due
date, whereas the professional form adds its own affiliation, author-note, and running-head
requirements. A student paper normally omits a running head, abstract, keywords, and author note
unless the instructor requires them. Repeat the paper title at the start of the text rather than
adding an `Introduction` heading.

Use a concise, informative title in bold title case; preserve authors' chosen names without
credentials and map affiliations unambiguously. Put the automatic page number at top right on every
page. Use one permitted accessible font consistently, 1-inch margins, a ragged right edge, and
ordinary 0.5-inch first-line indents. Do not manually hyphenate line endings or insert breaks into
DOIs and URLs. Double-space except where the manual expressly allows a different display, note, or
title-page treatment, and do not add blank lines around headings.

Headings express a logical hierarchy, proceed top-down without skipped levels, remain parallel,
and do not create a lone subsection. Levels 1–3 are freestanding; Levels 4–5 are indented run-in
headings ending with a period. Do not number or letter headings. References, footnotes, appendices,
tables, figures, and supplemental material each have their own placement, callout, labeling,
accessibility, and numbering requirements; the course's declared artifact form controls which are
used.

## 37. Effective scholarly expression

*Publication Manual* §§4.1–4.30.

Write for a defined audience with continuity, a visible argument, informative headings, and
paragraphs long enough to develop one claim. Put familiar information before new information,
maintain parallel structure, and use transitions that state the relation between ideas. Revise for
economy: remove repetition, empty intensifiers, strings of nouns, and needless circumlocution while
retaining qualifications that affect meaning.

Prefer precise verbs and concrete nouns, but do not turn style guidance into blanket bans. Passive
voice can keep the relevant object or procedure in focus; an inanimate subject can be accurate;
first, second, or third person can be appropriate to the rhetorical job; and contractions or
specialized terms can be proper inside quotations or for a knowledgeable audience. Define an
unfamiliar term where first used and avoid both unexplained jargon and condescending simplification.

Keep verb tense consistent with time: past or present perfect for completed literature and methods,
past for completed results, and present for conclusions or enduring statements. Make pronoun
antecedents unmistakable, keep modifiers beside what they modify, use singular and plural forms
consistently, and reserve comparisons and causal wording for relations the evidence supports.
`Since`, `while`, `would`, and similar words are not universally forbidden; rewrite them only when
their temporal, contrastive, conditional, or habitual meaning is ambiguous.

## 38. Crediting sources in the text

*Publication Manual* §§8.1–8.36, Tables 8.1–8.2, and Figures 8.1–8.7.

Cite ideas, language, data, media, and other contributions where a reader needs to distinguish the
writer's work from another's. Prefer primary sources; use a secondary-source citation only when the
original cannot reasonably be obtained, naming both in text but listing only the source actually
read. Match every ordinary citation to a reference entry and place citations close enough to show
their scope without repeating them mechanically in every sentence when attribution remains clear.

Use author-date parenthetical or narrative form. Apply the one-author, two-author, and three-or-more
author rules consistently; distinguish group authors, define a useful abbreviation on first use,
and disambiguate authors or dates when the normal short form would collide. Multiple citations in
one parenthesis are alphabetized and separated by semicolons; repeated works by one author order by
date. Personal communications appear in text only. A general website or common software mention
may give a version or URL in text without creating a reference entry.

Paraphrase genuinely rather than changing a few words, and still cite the source. Mark exact words
as quotations and follow §32. A citation can be omitted from a subsequent sentence only while its
source remains unambiguous; begin a new paragraph with attribution rather than relying on the prior
paragraph. Cite research participants without turning their confidential statements into ordinary
recoverable references. Epigraphs, classroom or intranet material, and traditional knowledge have
their specific access, permission, and attribution boundaries.

## 39. Reference elements, order, and missing information

*Publication Manual* §§9.1–9.52, Table 9.1, and Figures 9.1–9.4.

Choose a reference by identifying its group, category, and work type; online access or a PDF format
does not turn a report, article, book, or data set into a webpage. Build the entry from author, date,
title, and source, and verify every element against the work itself. Do not invent a missing element:
move the title to author position when authorship cannot be found, use `n.d.` when the date is absent,
add an informative bracketed description when needed, and omit a list entry when no recoverable
source exists. `Anonymous` is used only when the work is actually signed that way.

Preserve individual and group names as published, including diacritics, capitalization, surname
particles, suffixes, usernames, and creator roles. List up to 20 authors; for 21 or more, retain the
first 19 and final author around an ellipsis without an ampersand. Use the most specific responsible
group and omit a publisher identical to that group. Dates identify the cited version and may be a
year, fuller date, span, `n.d.`, or `in press`; retrieval dates follow §4.

Use sentence case for work titles and title case for periodical titles. Italic treatment depends on
whether the work stands alone or sits inside a larger work. Bracket a nonroutine work description
after the title. The source element can be a periodical, publisher, database required for recovery,
social platform, website, event location, DOI, or URL. Include a DOI when one exists, in resolver
form; otherwise include a URL only when the category and access route call for it. Do not prefix an
ordinary locator with “Retrieved from,” and do not add terminal punctuation to a DOI or URL.

Order entries and same-author works as §§1 and 3 specify. An annotation follows its normally
formatted entry in its own indented paragraph. Meta-analysis source studies stay in the main list
and may carry leading asterisks explained beneath the heading. Translated, reprinted, republished,
religious, and classical works retain the version actually used and the original-date or canonical
locator information applicable to that work.

## 40. Selecting the correct reference form

*Publication Manual* §§10.1–10.16 and Examples 1–114.

Apply the narrowest work-type form before deciding what locator belongs. Periodical articles use
periodical source data and an ordinary academic database is omitted; Cochrane and UpToDate retain
database identity because their works are uniquely recoverable there. Books and chapters omit an
ordinary database but may name an exclusive database, repository, or direct nondatabase locator.
Reports, conference work, dissertations, reviews, data, software, tests, audiovisual and audio
works, visual works, social media, and webpages each assign responsibility, date, title, source,
description, and locator according to the work itself.

Database access is not one behavior. Proprietary originals, limited-circulation works, repository
records, and test-database records may name the database; routine aggregator access normally does
not. Likewise, “online” is not a reference category. Use the webpage form only when the work has no
more specific category and no larger publication other than the site. Cite each webpage separately;
a general site mention can remain in text.

Retrieval dates are version decisions, not broad class decorations. Changing profiles, generated
maps, population clocks, and comparable unarchived states take one; fixed posts, articles, books,
and archived versions do not. A data set can be designed to change even when a DOI or URL appears,
so the identifier alone does not settle the question. Credit the creator role appropriate to media,
distinguish a whole work from one component, and include a URL only when it helps recover the cited
form under that category.

## 41. Legal references

*Publication Manual* §§11.1–11.10, Tables 11.1–11.2, and Examples 1–29.

Legal references normally retain legal style: title, legal source, and date, with standardized
abbreviations and the official version of record. Their ordinary in-text key is title and year,
shortened only enough to remain unambiguous. Preserve required parallel reporters and history,
make the authority retrievable, and verify that a decision has not been overturned and that a law
has not been amended or repealed. Formal pattern matching cannot establish current legal status.

Cases, statutes, legislative materials, administrative and executive materials, patents,
constitutions and charters, and treaties use distinct forms. A case retains the first reporter page,
court information, parallel citations, and relevant history; its name is roman in the list and
italic in text. A statute cites the compilation year, or public-law/session source when necessary.
Codified and proposed rules differ, as do bills, hearings, reports, resolutions, and executive
orders. Patent dates are issuance dates. Whole constitutions are generally text mentions, while
articles and amendments take legal locators and current provisions may be date-free. Treaties use
their agreement name and signing or approval date.

The chapter's abbreviation table is illustrative, not an exhaustive legal vocabulary. State rules
can differ, a URL is ordinarily supplemental to the authoritative locator, and the Bluebook or an
appropriate law-library source governs legal questions this distilled sheet does not resolve.
