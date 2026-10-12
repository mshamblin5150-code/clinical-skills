# Coursework body mechanics are graded on four APA rules and an uncertain hit blocks until the run records its disposition

**Measured at:** c0cbd997a1eef1e9752da4085fc1a3fc83a82765

[#1572](https://github.com/mshamblin5150-code/clinical-skills/issues/1572) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. Independent page
reads found APA mechanics defects in the body that no grader reported: abbreviations used before
being spelled out, `US` mixed with `U.S.` and `healthcare` with `health care`, counts under ten
written as numerals, one `cancelled`, the `pre-`, `post-` and `non-` prefixes hyphenated, title
included, and the title not repeated at the start of the text. PR #1698 repaired the last of
these. The ticket left one decision open: which of the proposed rows refuse and which report.
Grilled 2026-10-12; the clinician ruled every point below in that session, one question at a time.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**No grader checks any of the four rules today.** The coursework body graders are
`assignment_docx_scan`, `deck_scan`, `discussion_post_scan`, `discussion_reply_scan`,
`peer_critique_scan`, and `case_study_scan`, which `practicum-case-study` step 9 runs and
`checks_ledger` expects. None reports an undefined abbreviation, a mixed spelling variant, a
hyphenated closed prefix, or a count written as a numeral. The nearest checks are the
untraced-number rows, which trace body digits to claim headings, and
`discussion_artifact.group_abbreviation_definitions`, which covers group-author abbreviations in
citations only ([ADR 0263](0263-reference-scan-resolves-a-no-surname-entry-by-title-proper-prefix-and-reads-apa-8-21-group-abbreviations-through-one-shared-recognizer.md)).

**The rules are already written; only enforcement is missing.** `skills/_shared/reference/apa7.md`
section 34 states every one: one accepted spelling variant used consistently (§6.11), the
dictionary's hyphenation with most prefixes closed (§6.12, Tables 6.1–6.3), definition at first
use outside the manual's standard set (§§6.24–6.31), and zero through nine as words outside the
listed numeric exceptions, with no numeral opening a sentence or heading (§§6.32–6.39).

**A shared body module already exists.** `tools/coursework_style.py` reads Markdown through
`docx_write.blocks`, projects a Word body into the same grammar, and is imported by
`assignment_docx_scan`, `discussion_post_scan`, `discussion_reply_scan`, and
`peer_critique_scan`. `case_study_scan` reads its draft through `docx_write.blocks` directly.

**House style already departs from strict APA on clinical abbreviations.**
`skills/_shared/reference/style.md` tells a case study to write `HEENT`, `T`, `HR`, `RR`, `BP`,
and `SpO2` undefined and to use abbreviations freely in the Plan and MDM.

**The spelling table does not reach a draft.** `tools/spelling_scan.py`'s `TABLE` does not hold
`cancelled`, and the scanner reads tracked files, filenames, commit messages, and the preserved
run records. No coursework draft enters it, so adding the word alone would not have caught this
paper.

**APA's position on the ticket's two variant pairs was not confirmed from the Manual.** University
writing guides (Purdue OWL, Walden, Langara) state that `U.S.` takes periods and is used only as
an adjective, with `United States` spelled out as a noun; the session did not read the Manual
itself. No APA ruling on `health care` against `healthcare` was found; a library FAQ says the
sixth-edition Manual did not address it, and AP's 2026 move to `healthcare` is not APA.

**ADR 0358 changed the numeral picture mid-session.** It merged while this grilling was open:
a number in the clinician's own sentence is excused from tracing once the heading reader lists it,
and the writer is told to keep such figures in APA numerals. That removed the trap that would have
caught a run between the trace check and a words-to-numerals rule. Its build, which excuses reader-listed own figures in the
five number graders, landed on `main` before this record did.

## Ruling 1 — the check reads every coursework artifact written as APA prose, and decks are declared unread

The mechanics check reads Word course assignments, practicum case studies, discussion posts,
discussion replies, and peer critiques, through one shared module each body grader imports.
PowerPoint decks are not read, and each report that covers a deck says so. Slide text is written
in fragments and leans on abbreviations, so stretching paragraph rules over it would mean
inventing a slide rulebook nobody asked for. Reading only the Word assignment where the defects
were found was declined: the same undefined abbreviation in a case study or post would pass
silently.

## Ruling 2 — only APA's standard set and the house clinical abbreviations go undefined

One committed list holds what may appear without a definition at first use: the manual's standard
set (abbreviations the dictionary treats as words, such as `HIV`, `AIDS`, and `IQ`, and statistical
symbols) and the house clinical abbreviations `style.md` already prescribes (`HEENT`, `T`, `HR`,
`RR`, `BP`, `SpO2`). Every other abbreviation is defined at first use, everywhere, the Plan and MDM
of a case study included. That narrows `style.md`'s "used freely": an abbreviation like `CBC` is
spelled out once in the paper. Exempting the Plan and MDM wholesale was declined because an
abbreviation first used there would go undefined in the whole paper, which is the defect the page
reader found. Strict APA, defining the vital-sign labels too, was declined as overturning a
standing house rule.

The check recognizes capitalized abbreviation shapes. Lowercase and mixed-case forms, such as
`mL`, are declared unread, not graded.

## Ruling 3 — an undefined abbreviation blocks

An abbreviation outside the list that is used before its definition is a finding and the grader
exits 1. Every false alarm has a fix that is correct APA, because defining any abbreviation is
always permitted, and a genuinely standard abbreviation the list missed is added in one line.
Report-only was declined because it would leave the defect for a later page read again, which is
what this ticket recorded.

## Ruling 4 — spelling variants come from a committed table that grows only on evidence

A committed table lists the variant forms of one term, seeded with `US`/`U.S.` and
`healthcare`/`health care`/`health-care`. A row grows only when a run or a page read catches a
variant, the same way the American-spelling table grows. Automatic detection of any word appearing
both closed and open was declined: it fires on correct pairs such as the verb `follow up` beside
the noun `follow-up`, or `every day` beside `everyday`, and a run "fixing" one writes an error.
A mixed term not yet in the table passes, and that limit is declared.

## Ruling 5 — a row names a required form only where the signed-in Manual names one

Every row requires consistency. A row additionally names a required form only where the
*Publication Manual* itself names one, read in the signed-in VitalSource copy before the build and
cited on the row. The `U.S.` rule is read first: if the Manual states that `U.S.` is an adjective
and `United States` the noun, that row requires those forms; otherwise it requires consistency
only. A house-chosen form on every row was declined as inventing rules APA does not make.

## Ruling 6 — a mixed or wrong variant blocks, and a cited group author's name is exempt

A draft using two forms of one row, or a form the row's Manual rule forbids, is a finding and the
grader exits 1. Quotations and the titles of cited works are excluded, because APA reproduces both
as published. A table form inside a group-author name that appears in the paper's own reference
list is exempt wherever that name appears in the text, so `US Preventive Services Task Force
(2024)` passes in a paper that otherwise writes `U.S.` A proper name that is not a cited group
author can still be refused; each such case is added to the table as an exemption. Blocking only on
mixing, with the noun-or-adjective rule reported, was declined; if the noun-or-adjective reading
misfires on real papers, that limb comes back for a ruling.

## Ruling 7 — prefix hyphens are read as two populations

The first population is a committed table of prefixed words the dictionary closes, seeded with the
words this paper hyphenated and grown on evidence. The second is every other hyphen after one of
APA's listed prefixes, minus the structural exceptions APA keeps hyphenated (before a capital,
before a numeral, before an abbreviation, `self-`, and a closed form that would change the meaning)
and minus a committed list of dictionary-hyphenated words. That list is seeded with known cases
such as `anti-inflammatory`, `co-occur`, and `meta-analysis`, each confirmed against
Merriam-Webster at the build. A table alone was declined because it catches only words already
seen, while the ticket's defect was a habit. A blanket rule alone was declined because the
dictionary keeps some prefixed words hyphenated by word, not by pattern.

## Ruling 8 — a table hit blocks, and a wider hit blocks until the run records its disposition

A first-population hit is a finding and the grader exits 1. A second-population hit is also a
finding until the run records a disposition for it in a run record: either the word was closed, or
the dictionary keeps the hyphen, with the Merriam-Webster entry named. The grader checks that each
wider hit has a disposition of a recognized shape; it cannot verify the dictionary claim, and that
limit is declared. Words a run confirms as dictionary-hyphenated are proposed for the committed list
at the after-action review. Report-only was declined because nothing would make a run look; plain
blocking was declined because an unlisted dictionary-hyphenated word would stop a correct paper
with no correct edit.

## Ruling 9 — a digit zero through nine is read as two populations the same way

A digit zero through nine followed by a noun on a committed count-noun list (`patients`,
`participants`, `studies`, `visits`, `factors`, `criteria`, grown on evidence) is a finding and the
grader exits 1. Every other bare digit zero through nine, after mechanical exclusions (a following
unit or time word, a percent sign, a decimal, a date, a preceding series word such as `Table`,
`Step`, `Stage`, or `Grade`), is a finding until the run records a disposition: the one APA
exception that keeps the numeral (measurement, statistic, percentage, ratio, date, age, time,
score, money, or series position), or "changed to words". The disposition vocabulary is APA's own
exception list, so the run classifies and does not invent. A count-noun list alone was declined
because counts of unlisted nouns would pass. Bare-digit blocking was declined because a run
guessing wrong writes "two mg".

## Ruling 10 — a number word of ten or above blocks

A number word for ten or above (`ten`, `twelve`, `thirty`, `ninety`, `hundred`, and the rest),
outside quotations and the start of a sentence or heading, is a finding and the grader exits 1.
APA writes these as numerals whatever they count, so no meaning has to be guessed. This catches the
M11 slip, `ninety-day` and `thirty-day`, which ADR 0358 now tells the writer not to make. Number
words under ten in an exception context (`five days`) are not graded. Leaving the rule
one-directional was declined because the exact M11 slip would pass every grader.

## Ruling 11 — a sentence or heading that opens with a numeral blocks

A sentence or heading whose first token is a numeral is a finding and the grader exits 1. A
numbered list marker is a list item, not a sentence start, and the shared reader already tells them
apart. A false alarm after an abbreviation's period is cleared by rewording, which is always
correct. The rule was not in the ticket; it was added because the numeral rules already walk every
digit and APA section 34 states it.

## Ruling 12 — a paper not written in English is not graded on mechanics

Every rule above is an English rule. The check takes the paper's language the way
[ADR 0356](0356-the-paper-language-picks-the-filing-alphabet-and-english-files-a-special-letter-as-its-plain-letter.md)
ruling 4 does, from the paper's override and otherwise the account profile. Any language other
than English, and an unread language, makes every mechanics row report `not graded` with the
language named, and the command takes its did-not-scan status. A finding established on the same
run still wins. A clean status for an ungraded paper was declined as a silent gap. Running the
English rules anyway was declined as false findings throughout.

## Ruling 13 — `cancelled` joins the American-spelling table, and the mechanics check reads that table

`cancelled` is added to `spelling_scan`'s table, with its row in `clinical-note`'s conventions
table. The mechanics check imports that same table and refuses any of its British forms in a draft
body, outside quotations and the titles of cited works. A finding blocks. One table serves the
repository and the coursework, so every past catch protects a paper. A separate coursework list was
declined as two copies of one rule. Adding the word alone was declined because no draft enters the
spelling scanner.

## What the build does

- Read `U.S.` in the signed-in Manual before writing the variant table, and cite each row's source.
- Add the mechanics rows to `tools/coursework_style.py`, or a module beside it that imports its
  reader, and call them from `assignment_docx_scan`, `discussion_post_scan`,
  `discussion_reply_scan`, `peer_critique_scan`, and `case_study_scan`. Decks get a declared
  `not read` line.
- Hold the committed lists in one module (the abbreviation exemptions, the variant table, the
  closed-prefix table, the dictionary-hyphenated list, and the count nouns), each grown on evidence.
- Add one purpose-named run record for the prefix and digit dispositions, and grade its shape.
- Exclude quotations, the reference list, and the titles of cited works from every row.
- Enter each new finding in `reference/completion-check-starts.tsv`; nothing is backfilled, and
  posted items keep their frozen grades under
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md).
- Name the rules the check enforces beside `apa7.md` section 34, and add the after-action-review
  step that proposes confirmed dictionary-hyphenated words and new variant pairs for the lists.
- Test each row through each grader's public command seam with a defect, its correct twin, and the
  exclusions, including the USPSTF group-author case, `anti-inflammatory`, `2 tablets` with and
  without a disposition, `ninety-day`, a sentence opening with a year, a non-English paper, and
  `cancelled` in a body against a quoted title that keeps it.

## What this record does not settle

**Whether a wider hit's recorded disposition is true.** The grader checks its shape, not the
dictionary or the APA category it names.

**Lowercase and mixed-case abbreviations**, and mixed terms or count nouns no list holds yet. They
are declared limits, not graded.

**Deck mechanics.** Slides are declared unread until someone asks for a slide rulebook.

**Whether the noun-or-adjective `U.S.` reading misfires on real papers.** The build measures it
against committed material; a misfire returns it for a ruling.
