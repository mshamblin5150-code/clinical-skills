# A patient FAQ takes no retrieval date and five reference shapes are refused where APA makes them certain

**Measured at:** 9320467c5ca26286264ed5583da680a19c7366f7

[#1580](https://github.com/mshamblin5150-code/clinical-skills/issues/1580) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4) in October 2026. References
readers caught APA form defects in the reference list across many rounds, and `tools/reference_scan.py`
reported none of them. The ticket proposed four rows and asked for one ruling, on whether a patient
FAQ page takes a retrieval date. The clinician ruled every point below on 2026-10-16, against `main`
at the commit above, where the freshness gate read `FRESH`. **Nothing is built here; this is the
record the build reads.**

## Measured before ruling

**The scanner passes every proposed shape today, and the scanner could have failed.** Synthetic
three-entry drafts were run through `python tools/reference_scan.py <draft> --as-of 2026-10-12 --show`.
A drug-label entry with no bracketed description, a report with no element after its title, a
report number in square brackets, and a page range joined by a hyphen each reported no finding, the
same as their correct twins. Each run exited 2 only because the drafts declared no paper language.
A control replacing the report number with `[PDF]` reported `format-bracket 1` and exited 1.

**What the Module 4 run shipped differs from the ticket's descriptions.** The run's retained round
drafts and reader records were read for shape classes only:

| Ticket shape | What the record shows |
| --- | --- |
| Drug-information form | Every drug entry carried a bracket: two DailyMed entries began with `[Drug label]` or `[Package insert]` and a site element of `DailyMed, U.S. National Library of Medicine`, and three FDA package-insert PDFs kept `[Package insert]` throughout without a flag. The round-2 reader flagged the DailyMed descriptors against `apa7.md` §21. A later round took dates from DailyMed's data feed rather than the page. |
| Missing parent agency | No parent was missing. One CDC page carried the name of a larger CDC guidance document in the parent's place, and two Office of Dietary Supplements entries wrote the author parent-first, `National Institutes of Health, Office of Dietary Supplements.`, with nothing after the title, for three rounds. |
| Report number in brackets | No report number appears in any round. The one bracketed number was `[Committee statement No. 26]`, written in round 13 and fixed in round 14. |
| Hyphen in a numeric range | Ten page ranges, one of them `e212-e316`, and one four-digit year range in a vaccine title. The correct final list still holds five hyphenated digit pairs, all inside DailyMed `setid` addresses. |
| FAQ retrieval date | Three ACOG patient FAQs carried retrieval dates in rounds 1 to 3 and none from round 4. The round-1 reader accepted them; the round-3 reader removed them because each page displays its own last-updated date. |

Running the scanner over all 22 rounds and the final with `--paper-language English` exits 0 on
every one.

**What APA publishes, read from archived apastyle.apa.org pages** because the live site returns a bot
challenge to scripted reads:

- The elements page says "Include a retrieval date only if the work is unarchived and designed to
  change over time. Most references do not include retrieval dates," and "Do not include a date of
  last review in a reference because content that has been reviewed has not necessarily been
  changed."
- APA's own patient-education and fact-sheet examples carry no retrieval date: the NIMH *Anxiety
  disorders* health-topic page, a WHO fact sheet, and the ATSDR fact sheet on the Nursing Student
  References page. Its retrieval-date examples are a population clock, Worldometer, UpToDate,
  StatPearls, and an OER Commons resource. APA publishes nothing that names FAQ pages.
- Nursing Student References item 15 gives `[Drug information]` "(or other wording as appropriate)"
  and omits the site name when it equals the author. The elements page says to include a bracketed
  description for works outside the peer-reviewed literature and permits altering its wording.
- "The specific agency responsible for the report appears as the author. The names of parent
  agencies not present in the group author name appear in the source element as the publisher."
- "If the report has a report number, include it in parentheses without italics after the report
  title." Square brackets carry only descriptions of the kind of work.
- APA's examples set page and date ranges with an en dash and keep the ASCII hyphen inside
  identifiers: `NIH Publication No. 18-2059`, `NIH Publication No. 15-NR-8018`, and
  `NASA/CR-2018-220043`.

The standing rule from #816 governs: where APA states a rule in writing, a scanner that cannot match
it has a defect. Each row below refuses only the shapes APA's text makes certain and declares the rest.

**One predicate was priced before it was ruled.** The agency-author predicate in ruling 4 fired on
none of the 21 `Synthesized example` paragraphs in `skills/_shared/reference/apa7.md` and matched no
reference-shaped line in tracked Markdown. That was a throwaway measurement of false-fire risk, not
the build.

## Ruling 1. A patient FAQ or patient-education page takes no retrieval date

`apa7.md` §4 states the answer for this genre: a patient FAQ or patient-education page is a webpage
on a website and takes no retrieval date. It takes the page's last-updated date when that date is
clearly attributable to the cited content, never a last-reviewed date, and `n.d.` when it shows
neither. A reader who believes a particular page is unarchived and rewritten continually argues it
out of the default for that entry.

Always adding a retrieval date was declined because APA's own examples of the genre omit it and the
sheet's webpage class takes none. Leaving the sheet silent was declined because that silence is the
disagreement the ticket recorded.

## Ruling 2. The scanner refuses a retrieval date on a recognizable patient FAQ

An entry is recognized as a patient FAQ when its URL path has a segment equal to `faq` or `faqs`,
ignoring case, or when its title contains the word `FAQ` or the phrase `Frequently asked questions`.
A recognized entry is graded as `Webpage on a website`, so the existing
`retrieval-date-on-archived` row refuses a retrieval date on it. A site name is never consulted.
FAQs not recognized this way remain a reading.

Leaving it to readers was declined because two readers given the same written test split. A
report-only line was declined on ADR 0357 ruling 5's ground that a line which never fails is skipped.

## Ruling 3. A DailyMed entry with no bracketed description is refused, whatever its wording

An entry whose URL host is `dailymed.nlm.nih.gov` must carry a square-bracketed description after its
title. Any wording is accepted. `apa7.md` §21 is corrected to `[Drug information]` "or other wording as
appropriate", so `[Drug label]` and `[Package insert]` stop being read as defects.

DailyMed publishes only drug labels, so its address is certain evidence of the source class. Keying on
a site such as Drugs.com was declined because those sites also publish news and patient articles.
Requiring the literal `[Drug information]` was declined because APA permits other wording. Drug
information from any other host, a year-only date, the layered site element
`DailyMed, U.S. National Library of Medicine`, and dates taken from the data feed rather than the
page remain declared readings.

## Ruling 4. A parent-first group author is refused

For an author element that contains no personal initials, the scanner refuses when a comma is followed
by one of `Office`, `Division`, `Bureau`, `Center`, `National Center`, `Institute`,
`National Institute`, `Branch`, or `Program`. The remedy states APA's form: the specific agency as
author and the parent agency after the title. The word list is closed, declared, and grows on
evidence.

Whether a parent agency is missing, or whether something other than a parent agency stands in that
place, remains a reading. A group author that is its own publisher correctly has nothing there, and
the scanner holds no map of agency hierarchy, so a missing-parent row would refuse correct work.

## Ruling 5. A document number inside square brackets is refused

The scanner refuses a square bracket containing `No.` or `Nos.` followed by a number or code. The
remedy shows the parenthesized form after the title, for example `(Committee Statement No. 26)`,
with any needed description kept in its own bracket. A bare bracketed code without `No.`, such as
`[NG136]`, passes and is declared. Refusing every bracket holding a digit was declined because it
could refuse a correct description that contains a number.

## Ruling 6. A hyphen is refused in a page range and in a four-digit year range

The scanner refuses a hyphen joining two numbers in two positions. The first is the locator: a page
range after a journal's volume and issue or after `pp.`, including letter-prefixed pages like
`e212-e316`. The second is two four-digit years joined by a hyphen, anywhere in the entry. URLs,
DOIs, and parentheticals containing `No.` are excluded. Every other hyphen between digits passes and
is declared, including a dose or age span inside a title.

Refusing every hyphen between digits was declined because APA's own examples keep the hyphen in
identifiers, and identifiers inside titles cannot be enumerated. On the Module 4 record the two
shapes reach all eleven defects and none of the five address fragments in the correct final list.

## Ruling 7. Every new row refuses

Rulings 2 through 6 add or extend rows that set exit 1 like the scanner's existing rows, on ADR 0357
ruling 5's reasoning. None is report-only.

## Supersedes

- [ADR 0357](0357-reference-scan-refuses-four-mechanical-apa-form-defects-and-the-word-grader-carries-reference-italics.md) ruling 7,
  its words "Nothing here moves it." Ruling 2 here moves the retrieval-date direction for a
  recognizable patient FAQ, whose answer ruling 1 settles in the sheet. Whether any other work is
  designed to change stays the declared reading.

## Build checklist

- `tools/reference_scan.py`: a patient-FAQ recognizer mapped to `Webpage on a website` so
  `retrieval-date-on-archived` reaches it; and one kind each for rulings 3, 4, 5, and 6, traced to
  #1580. Each declared limit above goes into `NOT_REACHED`.
- `skills/_shared/reference/apa7.md`: §4 gains ruling 1's sentence; §21 gains "or other wording as
  appropriate"; §7 names every new declared limit, which its two-way bind with `NOT_REACHED`
  requires. Every coverage row grounding a changed section is re-confirmed and its digest refreshed,
  so `python tools/apa7_coverage.py --quiet` reads `gone-stale 0`.
- `skills/practicum-case-study/SKILL.md` step 7's defect table gains a sentence per new kind, which
  the existing `ROW_PHRASES` binding requires.
- `reference/completion-check-starts.tsv`: a row for each new kind at the build's landing time,
  compared with approval, under
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md).
- Tests driving the public command with synthetic drafts: a positive per kind built from the Module 4
  shape (three ACOG-shaped FAQ URLs with retrieval dates, a DailyMed entry with no bracket,
  `National Institutes of Health, Office of Dietary Supplements` as author,
  `[Committee statement No. 26]`, `e212-e316` and a hyphenated `2025-2026` title season) and a
  negative per kind, including `[Drug label]` and `[Package insert]` on DailyMed entries, a WHO entry
  with nothing after the title, a DailyMed `setid` URL, `(NIH Publication No. 18-2059)`,
  `(Report No. NASA/CR-2018-220043)`, and a non-FAQ CDC page with no retrieval date. The scanner's
  every-kind-fires draft is extended to the new kinds.

## What this record does not reach

- **Whether a page other than a recognizable patient FAQ is designed to change.** It stays a reading.
- **Drug information from any host but DailyMed**, and the date and site-element problems in ruling 3.
- **A missing or substituted parent agency.** Ruling 4.
- **Bare bracketed codes and title ranges outside ruling 6's two shapes.** Each is a declared miss.
- **Deck reference slides.** [#1771](https://github.com/mshamblin5150-code/clinical-skills/issues/1771).
