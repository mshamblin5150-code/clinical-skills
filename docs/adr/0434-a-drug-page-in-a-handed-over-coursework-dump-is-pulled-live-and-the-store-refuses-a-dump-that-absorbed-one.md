# A drug page in a handed-over coursework dump is pulled live and the store refuses a dump that absorbed one

**Measured at:** 0bd3d566198a63206267fffbaa01ae4155dfe008

[#1809](https://github.com/mshamblin5150-code/clinical-skills/issues/1809) was ruled on
2026-10-18 in [ADR 0409](0409-the-uptodate-pull-checks-the-query-it-sent-files-drug-pages-by-version-and-proves-a-failed-pull-opened-the-page.md),
which made a **Drug page** a filed source identified by its title, its version line and the date it
was read. That record covered a drug page the puller reaches through the **Authenticated route**.
Its ruling comment left one question for the clinician: a **Titled copy** writes one title above
each author masthead, a drug page has none, so a drug page inside a handed-over coursework dump had
no stated titling route. The sweep closing #1896's grilling flagged that the ticket carried
`ready-for-agent` with that question open, and the clinician moved it back to `grilling`. Grilled
2026-10-19 against `main` at the commit above, where the freshness gate read `FRESH`. The clinician
ruled both points below in that session, one question at a time. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**No handed-over dump has held a drug page.** Every evidence dump in the owning checkout's scratch
root, filed and in run directories, was read for the drug-page header `UpToDate Lexidrug` and for a
closing version line in a block with no author masthead above it. None carried either. The only
file naming `Lexidrug` is a run's working text, with no author masthead and no version line.

**A clinical topic carries the same closing version line.** In every filed dump whose topics kept
their endings, the count of `Topic <N> Version <N.N>` lines equals the count of author mastheads.
One filed dump carries 107 mastheads and 31 version lines, so many topics are pasted with the ending
cut off. ADR 0409's build checklist has the unfiled-material sweep count a drug page "by its version
line"; that count would include every topic that kept its ending.

**A drug page in a handover would be filed as part of a topic, silently.**
`uptodate_store._topic_blocks` splits a dump at author mastheads, and a drug page has none. Its text
lands inside the block of the topic before it, or before the first masthead where no block reads it.
It adds no author, review or update line, so `parse_topics`'s population check still balances.

**The words `Drug information` appear in topics only inside quoted cross-references.** One filed
dump carries the phrase on five lines, each a sentence ending `(See "<name>: Drug information".)`.
No filed line is the phrase alone in the title form `<name>: Drug information`.

**A handover cannot show two facts ADR 0409 ruling 3 requires of a drug page:** the date the agent
read it, since the clinician copied it at a time the run never saw, and that every Expand All was
clicked before the copy.

## Ruling 1 — a drug page in a handover is dropped from the filed copy and pulled live

When a handed-over coursework dump holds a drug page, the run leaves it out of the copy it files and
writes the drop into the block-to-title mapping, naming the page and why it was left out. If the case
needs that drug, the run pulls the drug page live through the shared puller brief from ADR 0409
ruling 10, which coursework research already does without asking under
[ADR 0332](0332-case-material-and-case-research-are-declared-context-places-and-both-libraries-come-first.md)
ruling 4. Removing a drug page means the filed file differs from the handover, so the run files a
**Titled copy** even when the handover already carries its topic titles. A Titled copy may now
differ from the handover in a third way: a drug page left out.

**Filing it from the handover was declined.** Its read date would be the handover date, a stand-in
that starts the one-year term from the wrong day, and a page copied with its doses folded is refused
by ADR 0409 ruling 3 anyway. **Refusing the whole dump until the clinician removes the page was
declined**, because the run would stop and wait on him for a page the agent can fetch itself. A live
pull is the only route on which the agent sees every fact the store requires of a drug page.

## Ruling 2 — the store refuses a dump showing either sign of an absorbed drug page

`uptodate_store.py ingest` refuses a dump in which:

- one topic block holds more than one closing version line;
- a closing version line sits above the first author masthead; or
- a line carries the drug-page header: `UpToDate Lexidrug`, or the title form
  `<name>: Drug information` as the whole line.

Before the header check is written, the build pastes at least one real drug page through the same
copy route the clinician uses and confirms which header lines survive the paste. If neither survives,
that signal is dropped and the declared limit below widens to say so. `tools/uptodate_store.py`
carries no limits object today, so the build creates `uptodate_store.DECLARED_LIMITS` and names the
miss there: a drug page following a topic whose ending was cut off, when its header did not survive
the paste.

**The version-line signal alone was declined** because many topics are pasted without their ending,
and a drug page after one of them adds the topic's only version line. **The header signal alone was
declined** because whether it survives a paste is unmeasured. **No store check was declined**
because a missed drug page is filed silently as a topic's text, and a grader can then read a drug
monograph as that topic's evidence. The store stays the strict backstop under the run's reading, the
arrangement [ADR 0365](0365-a-duplicate-topic-differing-only-in-page-chrome-is-dropped-by-the-run-and-the-store-stays-strict.md)
kept for chrome-only duplicates.

## Correction to ADR 0409's build checklist

The `tools/uptodate_store.py` item reads "the unfiled-material sweep counting a drug page by its
version line, since it has none of the three topic markers the sweep counts today." A clinical topic
carries the same version line, so that count would include every topic that kept its ending. The
sweep counts a drug page by ruling 2's signals instead: a version line in material with no author
masthead above it, or the drug-page header. This corrects a build instruction, not a ruling.
[ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md)'s
section *Coordination the rulings fix without a further choice* repeats the same instruction when
it tells its build to keep ADR 0409's sweep change; the change to keep is the count stated here.
Neither earlier record is edited, and #1841 and #1685, which carry ADR 0416's build, are told on
the tracker.

## Build checklist

- `tools/uptodate_store.py`: ruling 2's three refusals at ingest, each naming the block and the
  remedy (file a Titled copy without the drug page); the sweep count above; a new
  `DECLARED_LIMITS` object naming the miss, pointed to from `CLAUDE.md`'s **UpToDate evidence
  store** section. Measure a real pasted drug page before writing the header
  check.
- `skills/practicum-case-study/SKILL.md` step 3, the paragraph opening "An untitled dump takes the
  Titled copy route", and `skills/_shared/reference/sourcing.md`'s `CASE-RESEARCH` paragraph, which
  files the clinician's case-research compilation for all five coursework skills: ruling 1's drop,
  its mapping entry, and the live pull. The step 3 paragraph is also the build site of
  [#1578](https://github.com/mshamblin5150-code/clinical-skills/issues/1578)'s chrome-only drop;
  whichever build lands second keeps the other's text.
- `CONTEXT.md`'s **Titled copy** entry names the drug-page drop and that a titled handover holding a
  drug page is also filed as a Titled copy. That edit lands with this record.
- Tests through the public ingest command: a topic block holding two version lines is refused; a
  version line above the first masthead is refused; a whole-line drug-page header is refused; a
  topic whose prose quotes `"<name>: Drug information"` is accepted; a clean dump whose topics all
  keep their version lines is accepted.

## What this record does not reach

- **A drug page following a topic cut off at its end, whose header did not survive the paste.** It
  adds one version line where the topic had none, and nothing in the text marks it. The run's
  reading is the only catch, and the limit is declared.
- **Whether a drug page's paste keeps its header at all.** Unmeasured until the build pastes one.
- **Drug pages in clinical-note or batch-shift runs.** Those routes pull live under ADR 0409 and take
  no handed-over dump, so ruling 1 does not reach them.
