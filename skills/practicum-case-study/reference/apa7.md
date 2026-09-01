# APA 7 — the rules this document actually uses

**Distilled, not downloaded.** The *Publication Manual* is copyrighted and cannot live in this
repo. What is freely published is APA Style's own rule pages, and this sheet is the handful of
rules a practicum case study rests on, each carrying the manual section it comes from so a reader
can go to the source rather than trust this file.

**Sections 1 through 7 were verified against apastyle.apa.org on 2026-08-18.** Every rule in those
sections was read from that site on that date, not recalled. A rule this sheet does not cover is
looked up the same way — **an APA rule is looked up, never recalled**, which is
[SKILL.md](../SKILL.md)'s anchor discipline arriving at the reference list.

**The two fenced examples are APA's own, and they stay.** Ruled 2026-08-18 on
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223), against a public
repo rather than a private one. This sheet reproduces **no APA prose at all** — the only
verbatim third-party strings in it are the 22-word UpToDate reference in §2 and the
19-word `2019a`/`2019b` pair in §3, both from the free rule pages, both with their
publishers already elided, and both *format demonstrations*: a reference format described
in a sentence is not a reference format. Everything else here is this repo's own wording
with a section pointer beside it.

**The *Publication Manual* section numbers are what those pages cite, and are not themselves
checked here** — the manual is not in this repo and cannot be. They are a pointer for anyone who
holds a copy, and the claim being made is only that the site said so on the date above. Treating
them as verified would be the thing this sheet exists to stop.

**What this sheet is for.** *APA Format and Scholarly Writing* is 5 of the 100 points, and
[SKILL.md](../SKILL.md) requires the reference walk in step 7 to run on every document. That
instruction needs a written rule behind it, or *"fix the reference list"* is a wish rather than a
check. **Ruled 2026-08-18**, and the words that settled it were the clinician's: *ordering the
differential is very important, but that shouldn't take the place of tidiness.*

**Readers:** the `practicum-case-study` and `discussion-post` skills. The former links this sheet
directly; the latter links it from its own workflow because the reference scanner is shared.

---

## 1. The reference list, mechanically

*Publication Manual* §2.12 and §9.43 to §9.49.

- Starts on **a new page** after the text.
- The label is **`References`**, **bold and centered**. Never `Works Cited`, `Bibliography` or
  `Reference List`. Where the list holds exactly one entry the singular **`Reference`** is
  permitted — which the corpus needs, since one submission scored full marks on a single source.
  **Take that permission freely**: since
  [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217) the renderer matches
  both spellings and the whole of §1 applies to either. This bullet told a run to write the plural
  regardless until that landed; the workaround is gone. **Write the label and nothing else** —
  the singular is matched only as a complete heading, because `Reference Ranges` is a heading a
  clinical document really writes and a match there would center it and break the page.
- Each entry is **one paragraph, flush left**, with a **0.5 inch hanging indent applied to the
  whole list**.
- **Double spaced throughout, with no extra space between entries.**
- Page numbers sit in the **top right corner of every page**, the reference list included.
- **Alphabetized by the first word of the entry** — normally the first author's surname. Where a
  work has no author, the title moves to the front and the entry alphabetizes by the title.

**`Roughly alphabetical` is not the rule, and this sheet retires that phrase.**
[style.md](style.md) §10 described the corpus as roughly alphabetical, which was an accurate
description of ten submitted documents and was never a statement of the standard. Sorted is sorted.

## 2. UpToDate article reference form

APA publishes a reference example for this database specifically, which is worth knowing before
inventing a form for it. *Publication Manual* §10.1.

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

**The letters are assigned by placing the entries in the reference list alphabetically by title,
then lettering them in that order.** They are not assigned by which one was cited first, by page
order, or by which one was found first.

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
- **Use only the year with its letter in text**, even where the reference list entry carries a
  fuller date.
- Undated works by one author take **`n.d.-a`, `n.d.-b`** — with the hyphen.

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

*Publication Manual* §10.16.

**Most references do not take one.** A retrieval date belongs only where **both** hold: the work is
inherently designed to change over time, **and** an unarchived version of it is what is being
cited.

- **The per-class answer lives only in `reference_scan.APA_SOURCE_CLASSES`'s
  `takes_retrieval_date` column.** A class section points to that column rather than restating a
  second mapping here.
- A society guideline PDF, a journal article, a USPSTF statement and a textbook **do not**. Adding
  one there is a defect in the other direction, and a run that puts retrieval dates on everything
  is wrong on most of the list.
- **The retrieval date must be on or after the exam date.** A date in the past relative to the
  document is the corpus's recurring defect, and it is the one the clinician named himself:
  *"I more than likely wrote the retrieved by wrong."*

## 5. Every entry is cited, and every citation is listed

*Publication Manual* §2.12, and it runs in both directions:

- **Every work cited in the text appears in the reference list.**
- **Every work in the reference list is cited in the text.** Where one is not, APA's instruction is
  to *either* cite it in the body *or* delete the entry — and this skill's ruling is **delete**,
  because a reference list is what the argument rests on and the rubric scores *Integration* rather
  than reading. That ruling predates this sheet; what the sheet adds is that APA agrees with it.

The exceptions APA names do not arise here: personal communications, which are cited in text only,
and the references of a meta-analysis.

## 6. What the renderer applies, and what it does not

`tools/docx_write.py` is what turns the Markdown into the submitted `.docx`. **It applies every
§1 rule that is a matter of *format*** — plus the two rules from elsewhere in the manual that a
renderer can reach — and what it does not is written down rather than assumed away:

| APA rule | `docx_write.py` | Word calibration and tripwire |
| --- | --- | --- |
| Times New Roman 12 pt, double spaced, 1 inch margins | applied | `body-defaults` |
| 0.5 inch hanging indent on the whole reference list | applied | `reference-hanging-indent` |
| No extra space between entries | applied | `reference-no-extra-space` |
| `References` heading **bold** | applied | `reference-heading-bold` |
| `References` heading **centered** | applied | `reference-heading-centered` |
| `References` heading at **body size**, 12 pt | applied — every heading level is 12 pt | `reference-heading-body-size` |
| Reference list **starts on a new page** | applied | `reference-page-break` |
| **Page numbers**, top right of every page | applied | `page-number-header` |
| The singular **`Reference`** heading gets the hanging indent | applied | `singular-reference-hanging-indent` |
| Every body paragraph takes a **0.5 inch first-line indent** (§2.24) | applied — and *only* a body paragraph: a heading, a list item, a reference entry and a table cell each take none | `body-first-line-indent` |
| A table carries **horizontal rules only**, no grid (§7.8) | applied — three rules and no more: above the header row, below the header row, below the last row | `table-horizontal-rules` |

**Word is the evidence for every verdict in both tables.** The dated observation and the
semantic XML shape it covered are in
[`word-renderer-calibration.json`](word-renderer-calibration.json). Re-derive them with
`python tools/docx_word_probe.py --word`, the maintainer-only command that opens the probes
through Word COM and prints what Word reports. Word is not on the consumer or CI path. The
permanent test opens no Office process: it compares the current shapes with all calibration keys
and says the affected row must be retaken when one leaves the measured set. This is
[ADR 0008](../../../docs/adr/0008-word-is-a-one-time-calibration-instrument.md).

**The last two rows are [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220),
landed 2026-08-19, and they were first checked the same way the nine above them were** — a document
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

**The nine rows above those two were first checked the same way, on a different day** — by rendering
a document and reading `word/document.xml`, `word/styles.xml` and `word/header1.xml`, not inferred
from the source. 2026-08-18, on
[#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217)'s branch. **Those XML
reads were renderer-shape checks, not Word measurements.** Five of those
nine read *not applied* earlier the same day, and the other four were already green — the table
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
clinician ruled it on 2026-08-18, and the answer was wider than the row — **every heading level
now renders the way APA distinguishes them**, level 1 bold centered, level 2 bold flush left,
level 3 bold italic flush left, level 4 bold indented.

**What is still not applied**, so the list above does not read as the whole of APA:

| APA rule | `docx_write.py` | Word calibration and tripwire |
| --- | --- | --- |
| A **title page** — title, author, affiliation, course, instructor, due date | **not applied**, and not mechanical: none of those six values is in the Markdown | `title-page` |
| APA level 4 and 5 headings are **run-in** | **not applied** — Markdown gives a heading its own line, so level 4 renders as the indented bold paragraph it otherwise is, and level 5 is not in the subset | `run-in-headings` |
| The list is **alphabetized** (§1) | **not applied**, and declined rather than pending — sorting is an *edit to the document*, not a format applied to it, and this renderer changes no word it is handed. `tools/reference_scan.py` grades the order instead, its `list-not-sorted` row | `reference-alphabetization` |
| Each entry is **one paragraph** (§1) | **not applied** — every non-blank line becomes its own paragraph, so a hard-wrapped entry renders as two and the second hangs on nothing. Joining them is an edit on the same terms as sorting; [SKILL.md](../SKILL.md) step 7 catches it as an author defect | `reference-single-paragraph` |

**The last two rows are not #220's, and they were on neither table before it** — they are a gap
that ticket's repair surfaced. This paragraph used to say the renderer applied *most of* §1, which
was true and vague; rewriting it into a claim a reader can check is what showed that two of §1's
bullets had never been recorded in either direction. **The lesson is the one #220 is about**: an
unfalsifiable summary hides a gap exactly as well as a wrong list does, and nothing had to go
stale for it to happen.

**Each of the four is a statement about what this renderer is *for*** rather than a fix somebody
has not got to. The title page is a `practicum-case-study` question about where six course values
come from before it is a renderer question; the run-in heading is a limit of Markdown; and the
last two are the same ruling twice — **a renderer formats, it does not rewrite**. All four are
recorded here rather than filed.

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
**A rendered `.docx` is not an APA-formatted document**, which is [SKILL.md](../SKILL.md) step 9's
sentence arriving one level down — and it is no less true for the rows that went green above,
because what a renderer cannot check is whether the entry it indented so carefully is a real
source.

---

## 7. What a command reads off this sheet, and what stays a reading

`tools/reference_scan.py` grades a finished draft's reference list against most of the sections
above — the label in §1, the sorting in §1, the `a`/`b` ordering in §3, where a retrieval date
belongs and where it is a defect in §4, the italics in §2, and both directions of §5. **This sheet
owns the rules and that command is a second *reader* of it, never a second copy**, which is why a
row it applies is written out in [SKILL.md](../SKILL.md) step 7 as well: a harness with no Python
walks the table by eye and reaches the same verdict.

**What stays a reading, and it is a list rather than a paragraph now.** Each row is a rule this
sheet states that no command grades, so a run walks it by eye — and since
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) the walk is not left to
memory either: [SKILL.md](../SKILL.md) step 9 names the row `the reference list, the part no command
reaches` and `tools/checks_ledger.py` expects it, so a run that returns no verdict on that row fails. **One row and one verdict for all three**, which is the honest width of it — a run that read only the UpToDate years and wrote `clean` discharges the row, and no command can tell. What the grader catches is a run that never looked at all.

| What stays a reading | Why no command reaches it |
| --- | --- |
| An **unwarranted retrieval date** on a guideline, a statement or a textbook | §4 says those take none. The command refuses one only where the entry carries a **DOI** — the work stating an archived version of itself exists, which is §4's own test failing. Nothing in a URL distinguishes a stable PDF from a page designed to change |
| **The UpToDate last update year** | §2's date element is the topic's own last update year, not the year it was read, and the same topic appears in one corpus under three years. Which is which is in the companion evidence document, which the command never sees |
| **Whether the source exists and says so** | Whether an entry is a real source saying what the sentence citing it says. That is [#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231), answered **before the draft exists**: `tools/research_ledger.py` grades a year an agent read off the page and a refutation a second agent returned |
| A check of **whether a legal entry is cited** | A legal entry is outside `uncited-entry`: the canonical narrative name needs a whole-phrase key the command does not have, so a clean result cannot prove the entry is cited anywhere |

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
count beside it on #143's terms and then stated this one. A test asserts that mapping's keys are
exactly `research_ledger.SOURCE_CLASSES`, so a fifth class fails rather than leaving a ruling made
over four standing unqualified.

**This was the third copy of that claim and the one the correction missed.** `reference_scan.py` and
`CLAUDE.md` were both fixed when #218 and #231 met; a sheet under `skills/` was outside what that
sweep had open, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)
again. Found by the merge rather than by either branch.

## 8. Legal reference entries — State nursing practice act (NPA)

**Provenance:** APA Style's *Nursing Student References* page, item 14, read 2026-08-30.

APA's published example is a state nursing regulation:

```text
Professional and Vocational Regulations, 16 CCR § 1481 (2023). https://...
```

Its parenthetical citation is `(Professional and Vocational Regulations, 2023)`, and its
narrative citation is `Professional and Vocational Regulations (2023)`. The entry form is:

```text
Name of the Statute, Title number Source § Section number(s) (Year)
```

The legal source name is required; a section-only entry is not this form.

A corpus instance follows APA's pattern with West Virginia's codification:

```text
Eligibility for prescriptive authority, W. Va. Code § 30-7-15b (2016). https://...
```

**Configured reader boundary.** The implemented limit is owned by
`discussion_artifact.LEGAL_SOURCE_NOT_REACHED`; this sheet points to that object and does not
restate its entries.
