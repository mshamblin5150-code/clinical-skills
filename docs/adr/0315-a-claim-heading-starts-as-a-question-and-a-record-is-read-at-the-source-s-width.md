# A claim heading starts as a question and a record is read at the source's width

**Measured at:** 6017d522c512525d59aab7a2da633ee3b54f9375

[#1480](https://github.com/mshamblin5150-code/clinical-skills/issues/1480) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 9) on 2026-10-01: independent
refuters corrected research records five times and narrowed the orchestrator's working headings four
more. Five comments recorded the same drift on later runs of `discussion-post`, `discussion-reply`
(twice), `course-assignment` (twice) and `practicum-case-study`.
[#1578](https://github.com/mshamblin5150-code/clinical-skills/issues/1578) proposed overlapping brief
rules from a `practicum-case-study` review. Grilled 2026-10-09 against `main`, where the freshness
gate read `FRESH` after a rebase; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**No skill hands its brief to the shared sheet.** All five coursework skills tell every research and
refutation worker to read `skills/_shared/reference/sourcing.md` first, and each states its own
record shape and return list. The sheet holds rules and no brief, so a rule written there reaches all
five without a new pointer.

**`discussion-post` drafts from recall by design.** Its step 3 writes the whole post, citations and
numbers included, before any research, then derives the claim set from that draft. The other four
skills write claim headings before research.

**The page-year row reads the first plausible year anywhere in the field.** Driven through
`research_ledger.read_records` and `_citation_findings` with an `n.d.` reference:

| `PAGE-YEAR` | finding |
| --- | --- |
| `the page states no year; it discusses the 1918 pandemic` | `page-year-disagrees`: 1918 on the page, no year in REFERENCE |
| `none stated on the page` | none |
| `2009 - stated on the masthead` | `page-year-disagrees`: 2009 on the page, no year in REFERENCE |

The third row is a true disagreement and the first is a false one, so the instrument discriminates
between a page that states a year and a field that merely mentions one only when the year opens the
field. The module already declares the limit as `page-year-first-plausible-token`.

**`discussion-post`'s refutation brief lists three verdicts.** Its record shape and the shared sheet
also allow `unreadable`; the other four skills list all four.

## Ruling 1 — the rules live once, in the shared sourcing sheet, and this ticket absorbs #1578's sourcing items

Every rule below is written in `skills/_shared/reference/sourcing.md`, which all five coursework
skills already read first. Writing it into `discussion-post` alone was declined because the
recurrences span every skill that keeps a claim ledger; five copies were declined as five prose
copies of one rule. #1578's sections 2 through 6 and the three items in its 2026-10-07 comment are
this rule set and are ruled here. #1578 keeps its two `practicum-case-study`-only items, the live
UpToDate pull offer and the chrome-only duplicate topic in a Titled copy, and stays open on them.

## Ruling 2 — a claim heading is a question before research and a claim in the source's words after

Before any source is opened, a `## CLAIM:` heading states the question the research must answer.
When the record returns, the orchestrator rewrites the heading as the claim the document will make,
in the source's own words and carrying every limiting qualifier the `PASSAGE` carries. Only that
rewritten heading is refuted, has its `TESTED-HEADING` printed, is cited, or is drafted from. A
question-form heading never reaches refutation or drafting. This holds for every claim-ledger skill,
drug-dose headings included: the question names the drug and indication, and the rewritten claim
states the dose. Recall may choose what to look up; it never supplies a heading's words.

A stripped claim, with every unread number, modality and qualifier removed, was declined because the
recorded drift was also framing: an equivalence the source does not draw, and an effect between two
practices no source measures. Leaving the working statement to the refuter was declined because it
is the recorded rework.

ADR 0208 rejected question headings on three grounds, and none reaches this form. Its measurement
showed a certifier taking a number from a question heading; here no question carries a refutation,
so no certifier believes one. It objected that practicum would carry two heading grammars; here every
heading follows one sequence. It objected that a question never becomes the document's sentence;
here the refuted heading is that sentence.

## Ruling 3 — `discussion-post` drafts a blind argument outline, not blind prose

`discussion-post` step 3 replaces the blind prose draft with an outline of the points the post will
argue, in the clinician's voice and reasoning, carrying no citation, number or source fact. Claim
questions are derived from the outline's factual points; the prose is written from the returned
records. The heading read's `unrecorded` finding and the `untraced-number` row remain the
completeness backstop for a factual sentence the outline did not anticipate. Keeping the blind prose
and rewriting its cited sentences afterward was declined because it moves the defend-the-recall
pattern from the heading to the sentence. Dropping the blind stage was declined because it is where
the clinician's argument is laid down before sources steer it.

## Ruling 4 — record rules are three principles, each with its recorded cases

The sheet states three principles and names the recorded cases under each as examples:

- **Every field is copied from the work as a reader sees it rendered.** A web title is the rendered
  page heading, never the browser tab text or a backing dataset's record. A year or date comes from
  visible text, never an HTML comment. An online reference entry is dated by the publisher's citation
  form or its last content revision, never by a link-only history row. `PAGE-YEAR` holds only the
  page's own year or says the page states none. A redirect or login-wall claim records the final
  address observed. A book or report accession must open the work the entry names: a chapter does
  not verify a whole-book entry, and a report verifies only values it assessed.
- **A locator lets a refuter land on the sentence in one read.** `PASSAGE` names the paragraph by its
  own opening words, then its page, section or table, and quotes from the start of the supporting
  sentence with its qualifiers. A heading joining several outcomes gives a locator for each.
- **A record states what the source states, in its words and at its width.** `STATUS` and
  `RESTATEMENT` use the source's descriptors. A record adds no purpose link, equivalence or exception
  the page does not state. A heading keeps the population, comparator, setting, adjustment, device,
  eligibility and tense its passage carries; a recommendation is cited for its own population, in
  the source's words; a finding is credited to the body that made it, in the section where it sits.

A flat list was declined because it grows with every review and is skimmed; principles alone were
declined because the named cases are what let a worker recognize the trap.

## Ruling 5 — a refuter refutes a broadening and lets a narrowing stand

A heading or restatement broader than its source is `refuted`. Broadening includes a dropped
qualifier on the subject, a wider population, an added exception, purpose link or equivalence, and a
stronger modality. A narrower claim is still true and `stands`. The refuter checks the restatement as
well as the heading. A correction the refuter proposes quotes the source's own conditions rather than
paraphrasing them, and an adopted correction is a changed heading that needs a fresh refutation under
ADR 0208 ruling 3. Refuting every width difference was declined because it buys no accuracy on a
true narrower claim.

## Ruling 6 — the page-year row enforces the documented field form

A `PAGE-YEAR` carrying a year must open with it and carry no second, different year; a field saying
the page states none carries no year. A year written after `p.`, `pp.` or `page` is a locator and is
exempt. A field outside that form gets its own named finding instead of a false `page-year-disagrees`,
and the `page-year-first-plausible-token` declared limit is retired. A brief rule alone was declined
because it leaves the false finding in place; reading phrases such as "states no year" was declined
as a natural-language guess that misses the next phrasing.

## Ruling 7 — `discussion-post`'s refutation brief names `unreadable`

The brief lists `stands`, `refuted`, `paywalled` and `unreadable`, matching its record shape and the
other four skills. It is in the paragraph rulings 2, 3 and 5 already rewrite.

## Supersedes

- [ADR 0208](0208-a-claim-heading-is-the-claim-the-document-makes-and-the-refuter-tests-it.md)
  ruling 1, its sentence "Before research the heading is a working statement, including any number
  the document will state." Rulings 2 through 6 of that record stand.

## What this record does not reach

- **Whether a heading was ever a question.** The ledger keeps only the rewritten heading, so ruling 2
  is prose a grader cannot observe.
- **Whether a record is at its source's width.** Rulings 4 and 5 are readings for the researcher and
  refuter; no row compares a restatement with a page.
- **Whether an outline carried a source fact.** Ruling 3's outline is private working material, and
  the backstop reads only the final draft.
