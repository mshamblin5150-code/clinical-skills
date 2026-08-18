# APA 7 — the rules this document actually uses

**Distilled, not downloaded.** The *Publication Manual* is copyrighted and cannot live in this
repo. What is freely published is APA Style's own rule pages, and this sheet is the handful of
rules a practicum case study rests on, each carrying the manual section it comes from so a reader
can go to the source rather than trust this file.

**Verified against apastyle.apa.org on 2026-08-18.** Every rule below was read from that site on
that date, not recalled. A rule this sheet does not cover is looked up the same way — **an APA rule
is looked up, never recalled**, which is [SKILL.md](../SKILL.md)'s anchor discipline arriving at
the reference list.

**What this sheet is for.** *APA Format and Scholarly Writing* is 5 of the 100 points, and
[SKILL.md](../SKILL.md) requires the reference walk in step 6 to run on every document. That
instruction needs a written rule behind it, or *"fix the reference list"* is a wish rather than a
check. **Ruled 2026-08-18**, and the words that settled it were the clinician's: *ordering the
differential is very important, but that shouldn't take the place of tidiness.*

---

## 1. The reference list, mechanically

*Publication Manual* §2.12 and §9.43 to §9.49.

- Starts on **a new page** after the text.
- The label is **`References`**, **bold and centered**. Never `Works Cited`, `Bibliography` or
  `Reference List`. Where the list holds exactly one entry the singular **`Reference`** is
  permitted — which the corpus needs, since one submission scored full marks on a single source.
- Each entry is **one paragraph, flush left**, with a **0.5 inch hanging indent applied to the
  whole list**.
- **Double spaced throughout, with no extra space between entries.**
- Page numbers sit in the **top right corner of every page**, the reference list included.
- **Alphabetized by the first word of the entry** — normally the first author's surname. Where a
  work has no author, the title moves to the front and the entry alphabetizes by the title.

**`Roughly alphabetical` is not the rule, and this sheet retires that phrase.**
[style.md](style.md) §10 described the corpus as roughly alphabetical, which was an accurate
description of ten submitted documents and was never a statement of the standard. Sorted is sorted.

## 2. UpToDate — nine in ten of the corpus's references

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
- **A retrieval date is required**, because the content is designed to change and versions of it
  are not archived. See §4.

## 3. Same author, same year — the `a`/`b` rule

*Publication Manual* §8.19, with the ordering rule at §9.47.

**The letters are assigned by placing the entries in the reference list alphabetically by title,
then lettering them in that order.** They are not assigned by which one was cited first, by page
order, or by which one was found first.

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

- **UpToDate always takes one** — APA says so on the page quoted in §2.
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

`tools/docx_write.py` is what turns the Markdown into the submitted `.docx`. **It applies some of
§1 and not all of it**, and the gap is written down rather than assumed away:

| §1 rule | `docx_write.py` |
| --- | --- |
| Times New Roman 12 pt, double spaced, 1 inch margins | applied |
| 0.5 inch hanging indent on the whole reference list | applied |
| No extra space between entries | applied |
| `References` heading **bold** | applied |
| `References` heading **centered** | **not applied** — it renders flush left |
| Reference list **starts on a new page** | **not applied** — no page break is emitted |
| **Page numbers**, top right of every page | **not applied** — the document carries no header part |

**Those three are worth a point between them at most, and they are still real.** They are recorded
here and filed rather than fixed, because they are renderer behavior rather than a rule about what
this skill writes — [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217).
**A rendered `.docx` is not an APA-formatted document**, which is [SKILL.md](../SKILL.md) step 8's
sentence arriving one level down.
