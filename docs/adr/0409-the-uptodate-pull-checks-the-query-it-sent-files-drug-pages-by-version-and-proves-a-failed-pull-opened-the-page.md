# The UpToDate pull checks the query it sent, files drug pages by version, and proves a failed pull opened the page

**Measured at:** 806ebbe6373a14433ea79381b60cc9fdf56e3800

[#1809](https://github.com/mshamblin5150-code/clinical-skills/issues/1809) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift) on 2026-10-14. The UpToDate
puller's own report named two defects. A key chord meant to submit or clear the search box was
typed as literal text, so one query reached UpToDate carrying a character the pretyping check never
saw. And two drug-dosing pages were recorded as failed reads because they were expected to carry no
clinical-topic masthead, without either page being opened. Grilled 2026-10-18 against `main` at
`91f234ebd4b9e41839f5938784f10819449159b9`, where the freshness gate read `FRESH`; the declared
commit above adds only this record's own first draft to that base. The clinician ruled every point below in that
session, one question at a time, and asked for the drug page to be measured live before ruling on
it. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The check sees the planned words, never the sent ones.** `tools/outbound_search.py check` grades
the string the agent intends to type and writes it as a passed search. Nothing compares that string
with what the browser submitted. Its `DECLARED_LIMITS` held three rows and none for this.

**The results page states the query it received, three ways.** Measured live through the
**Authenticated route** on 2026-10-18 with a non-encounter query: the address bar's `search=`
parameter, the search box's value, and the page's `Showing results for` line all carry the received
query, signed in or out.

**A drug page is a different kind of page, and the store is right to refuse it.** Signed in, the
results page shows a drug-information panel beside the topic list. Its full page, measured on
`Amoxicillin: Drug information`, is headed `UpToDate Lexidrug` with a copyright year, a Contributor
Disclosures link, and links to the patient and pediatric drug pages. It carries no `Authors:` line,
no literature-review currency line and no last-updated line. Read whole with every section
expanded, every month-and-year date on the page and every use of "update" sits inside a reference
citation, apart from a statement that pricing data is updated monthly. The only page-level marker
is a closing `Topic <N> Version <N.N>` line. `tools/uptodate_store.py ingest` refuses a file with no
authored topic body, so neither failed pull could have been filed even had it been read. A second
page, `Lisinopril: Drug information`, showed the same header and a version line; it was not read
through, so the build measures several drug pages before its filing check is written.

**A drug page's doses are folded shut until expanded.** The adult and pediatric dosing areas list
each indication as a collapsed heading. The amoxicillin page has four separate Expand All controls.
Folded, its visible text read 143,733 characters and the indication-specific doses were absent from
a plain text read; with all four expanded it read 169,265 characters and the doses were present, and
no block carrying content remained hidden. The first reading of this page during the grilling read
only the first 50,000 characters of the folded text and was corrected when the clinician questioned
it; the figures here are the whole-page reading.

**The coursework grader already reads a drug-page citation as an UpToDate citation.**
`research_ledger.UPTODATE_TITLE` matches an APA entry whose parenthesized date or `n.d.` and title
are followed by `UpToDate.`, with or without a URL after it, so a drug-page reference in the APA
sheet's drug-information form enters the store-membership join and fails it today only because no drug page has ever been filed.
Its currency check reads a topic's literature-review month against the bar's UpToDate window, which
a drug page cannot supply.

## Ruling 1 — the query read off the results page is checked against the query that passed

The live-pull and failed-pull commands each take the query read back off the results page. The tool
compares it with the passed query, ignoring spacing and letter case, and refuses to record the pull
when they differ. `outbound_search.DECLARED_LIMITS` gains the limit that the readback is copied by
the agent, the same honest-agent trust every check on this route already carries. A declared limit
alone was declined because nothing would catch the next mismatch. A written readback step with no
tool behind it was declined because a skipped comparison is indistinguishable from a passed one.

## Ruling 2 — a mismatched search is its own recorded outcome, checked and shown at the go-ahead

A search whose readback differs is recorded as a **Mismatched search**. The tool runs the same
identifier check over the sent words and records whether they would have passed. The go-ahead
UpToDate block gains `UPTODATE MISMATCHED SEARCHES`, each entry with that result, or `none`. The
agent then searches again under a new checked search id. A quiet retry was declined because the
clinician would never learn that unchecked words left the machine. Showing only a mismatch whose
sent words fail the check was declined because it hides the mechanical fault until it finally sends
something that matters.

## Ruling 3 — a drug page is a filed source, identified by version and read date

The **Evidence store** gains a second kind of filed page, the **Drug page**, identified by its title,
its version line and the date it was read. The puller clicks every Expand All on the page before
reading, and the filing check refuses a drug page under which any indication heading carries no
dosing text, so the check does not depend on the agent remembering. Keeping drug pages out of the
route was declined because they carry the site's indication-specific and kidney-adjusted dosing.
Recording every drug pull as a failed pull and moving the build to its own ticket was declined
because the version line removed the unknown that made deferral the cautious choice, and a puller
that reaches a drug page today can come back with no doses and nothing would catch it.

## Ruling 4 — a drug page is cited with its own tail

An item a drug page settles carries the same-line `FILLED·proposed` tail
`[uptodate drug: <page title>, version <N>, <dump id>]`. The read date lives in the filed copy's
record, which the dump id resolves. Adding the read date to the tail was declined because it would
be a second copy of a fact the record holds and could drift from it. Reusing the topic tail with the
read date in its `updated` slot was declined because it would state that the publisher updated the
page on the day it was read.

## Ruling 5 — a drug page fills gaps and never overrides a threshold sheet

A drug page may settle a gap. When it disagrees with a threshold sheet, the puller pulls the clinical
topic. If the topic settles the disagreement, the existing topic override applies; if no topic
settles it, the sheet stands and `UPTODATE CONFLICTS` lists the disagreement as `sheet kept`. A drug
page overriding a sheet as a topic does was declined because it summarizes labeling and expert
opinion rather than weighing the guidelines a sheet distills, which is the ground the topic override
rests on. Dropping the disagreement silently was declined because the clinician would never learn
that the drug reference and the guideline differed.

## Ruling 6 — coursework may cite a filed drug page

The coursework graders accept a citation to a filed drug page through the same store-membership
join, with the reference written in the APA sheet's drug-information form. The clinician has cited
the drug database in coursework before for its treatment recommendations and the conditions each
drug treats. Refusing drug-page citations in coursework was declined on that ground.

## Ruling 7 — a drug page is current for one year from its read date, refreshed on use

In both clinical notes and coursework, a filed drug page is current for one year from the date it
was read. A grader refuses a use of an older copy, and the agent pulls a fresh copy before using it.
The store's report states how many drug pages are past that year, so the clinician can refresh them
in a batch when he chooses. Reusing the bar's date window on the read date was declined because these
pages are revised often enough that a copy inside the window can be many versions behind. A fresh
pull for every paper was declined in favor of the one-year term the clinician set. A scheduled
refresh alone was declined because a pull needs the clinician's signed-in browser, so nothing
unattended can perform it and nothing would enforce it.

## Ruling 8 — a drug page is filed by its own section headings

A filed drug page is split at its own headings, down to each indication under a dosing heading, so
a store search returns the matching section with the page's title, version and read date rather
than the whole monograph. The clinician asked for the monographs to be quick for agents to use; the
whole page runs well past a hundred thousand characters.

## Ruling 9 — a failed pull carries one of four reasons and the evidence that reason needs

The failed-pull command from [ADR 0408](0408-the-go-ahead-uptodate-block-and-the-medatrax-posted-reading-are-written-by-committed-tools-and-checked-before-they-are-relied-on.md)
ruling 1 takes one of four reasons, and the grader refuses a record missing that reason's evidence:

- **signed out** — the sign-in page reached, and whether its own Sign In button was tried under the
  permission in `skills/_shared/reference/sourcing.md`;
- **service unavailable** — the error page's address;
- **no match** — the query read back off the results page and how many results were read;
- **page unreadable** — the address of the page actually opened, and a second method also tried.

A page never opened is not a **Failed pull**. Free text graded for substance was declined because
this shift's own reason would have passed it. A retained screenshot per failure was declined because
the recorded defect is an attempt never made, which the required page address already refuses.

## Ruling 10 — one shared puller brief, handed over word for word

`skills/_shared/reference/uptodate-pull.md` is the brief every UpToDate puller receives, verbatim,
from both the clinical and the coursework routes. It states the readback, every Expand All, opening
a page before calling it failed, the four reasons and their evidence, and the Sign In permission
that `sourcing.md` says every brief through the Authenticated route must state. A test asserts the
file still states each of these. A rule inline in `clinical-note` was declined because the
coordinator's paraphrase of it is where this shift's defect entered. A command printing a filled
brief was declined because it proves nothing about what the coordinator pastes.

## Supersedes

- [ADR 0408](0408-the-go-ahead-uptodate-block-and-the-medatrax-posted-reading-are-written-by-committed-tools-and-checked-before-they-are-relied-on.md) ruling 1, the words "Every passed search must end in either a recorded live pull or a recorded failed pull". A passed search may also end as a recorded mismatched search under ruling 2; a passed search with no recorded outcome remains a finding, and the failed-pull command stands.

## Build checklist

- `tools/outbound_search.py`: the readback argument on the live-pull and failed-pull commands and
  the mismatch refusal (ruling 1); the mismatched-search record with its identifier result
  (ruling 2); the four failed-pull reasons and their required evidence (ruling 9); the completion
  gate counting three outcomes; `DECLARED_LIMITS` gains the readback limit.
- The go-ahead block command from ADR 0408 ruling 3: the `UPTODATE MISMATCHED SEARCHES` line and the
  `sheet kept` conflict entry. The `sheet kept` entry is derived from the drug page's own live pull,
  which carries ADR 0408 ruling 4's sheet, row and what-differs arguments marked as kept rather than
  won, because no pull settled that conflict.
- `tools/uptodate_store.py`: drug-page ingest identified by title, version and read date; refusal of
  a page with a folded indication; filing by section; search returning sections; the report's count
  of drug pages past one year; the unfiled-material sweep counting a drug page by its version line,
  since it has none of the three topic markers the sweep counts today. Measure several drug pages
  before writing the filing check.
- The note tail grader, `tools/differential_scan.py` row 24, which today reads every `uptodate` tail
  against the topic form: the `[uptodate drug: ...]` form, and refusal of a drug page past one year.
- `tools/research_ledger.py`: drug-page citations join the filed drug pages, and the one-year term
  replaces the review-month check for them. A filed drug page inside its year stands for the
  undated-reference row's reason, since `n.d.` is its correct APA date.
- `skills/_shared/reference/uptodate-pull.md`, and a test binding its required statements;
  `skills/clinical-note/SKILL.md`, `skills/batch-shift/SKILL.md` and the coursework research steps
  point at it.
- `CLAUDE.md` maintainer tooling: name the new commands and point to their limits objects.
- Tests through each public command: a mismatched readback is refused and recorded; a mismatch whose
  sent words fail the identifier check is shown as failing; a failed pull missing its reason's
  evidence is refused; a drug page with a folded indication is refused at ingest; a drug page past a
  year is refused at use; a coursework drug-page citation passes membership; a clean shift passes.

## What this record does not reach

- **Whether the readback was copied from the browser.** The tool compares what it is given.
- **Whether a drug page's dose applies to this patient.** Filing proves the page was read whole, not
  that its dose fits the indication, weight, or kidney function in front of the clinician.
- **A drug page's revisions between reads.** The version line identifies the copy that was read; a
  copy within its year can still be behind the live page.
- **The per-run scripts and the CPT receipt**, which stay on
  [#1882](https://github.com/mshamblin5150-code/clinical-skills/issues/1882), filed from #1808's
  grilling, and [#1811](https://github.com/mshamblin5150-code/clinical-skills/issues/1811), filed
  from the ED-shift review of the same day.
- **Which indication section a cited dose came from.** The drug tail names the page, not the
  section, so whether the dose matches the entered diagnosis stays a reading.
