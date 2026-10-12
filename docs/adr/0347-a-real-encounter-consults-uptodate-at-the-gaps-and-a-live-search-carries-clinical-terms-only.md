# A real encounter consults UpToDate at the gaps and a live search carries clinical terms only

**Measured at:** d5284f5aa707bec163d8c66bf8c30f054377bfa3

[#1704](https://github.com/mshamblin5150-code/clinical-skills/issues/1704) was split off the
grilling of [#1503](https://github.com/mshamblin5150-code/clinical-skills/issues/1503) on
2026-10-11. [ADR 0332](0332-case-material-and-case-research-are-declared-context-places-and-both-libraries-come-first.md)
ruling 8 left the real-encounter skills out because a live search of the clinician's UpToDate
account types its terms into a third-party service, and a real encounter carries protected health
information where a classmate's teaching case does not. Grilled 2026-10-12 against `main`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**`clinical-note` reaches no UpToDate source.** Its *Guideline sheets* section routes every active
diagnosis through `reference/guidelines-catalog.md` and `reference/thresholds/coverage.md` before
diagnosis-directed testing, treatment, medication continuation or hold, monitoring, referral, or
disposition is written. Where no sheet settles the decision, the `FILLED·proposed` line's tail reads
`recalled, no shipped sheet` or `sheet does not settle it`: the decision came from memory. Ordinary
symptom relief and generic return precautions need no route. `batch-shift` writes its notes through
the same skill.

**The ticket's table was wrong about `icd10-cpt`.** It said that skill uses the catalog and the
threshold sheets. `skills/icd10-cpt/SKILL.md` records the opposite as a ruling of
[#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85): a code is anchored to what
the note documents, and a coder who withheld a code because a value missed a sheet's cutoff would
be re-deciding the clinical question from the worksheet.

**The pieces a search check needs already exist.** `phi_scan.corpus_identifiers` returns every
patient name and date literal in the corpus, and the per-account site picklist lives in
`scratch/medatrax-profile.md`. `tools/uptodate_store.py` has `ingest` and `search`, and ADR 0332
ruling 4 already files a topic a coursework run pulls live into the **Evidence store** as a
supplement dump. `tools/differential_scan.py` grades row 24's tails and knows only today's forms.

## Ruling 1 — a real-encounter note consults the store first and then the live account

`clinical-note`, and `batch-shift` through it, consult the **Evidence store** first and the
clinician's live UpToDate account second, through the **Authenticated route**. Every topic pulled
live is filed into the store through its ordinary ingest, so a later shift finds it locally.

Store only was refused because the store holds the clinician's coursework topics, so most shift
diagnoses would match nothing. Live only was refused because it gives up private local hits and
keeps the exposure. Neither was refused because the clinician asked for UpToDate across every
clinical skill.

## Ruling 2 — an encounter search carries clinical terms, one population word and one sex word

An **Outbound search** carries clinical terms (diagnosis, drug, test or procedure words), at most
one population word from `adult`, `child`, `infant`, `adolescent`, `pregnancy`, `older adult`, and
at most one sex word from `male`, `female`. It carries nothing else the encounter supplied: no exact
age, date, site, or free text from the shorthand.

Clinical terms alone were refused because UpToDate files many topics separately by population, so a
search without one opens the wrong topic. The clinician added sex because it changes the answer
often enough to need. Anything short of the HIPAA identifiers was refused because an exact age,
a rare diagnosis and the timing of a search together begin to point at a person, and that line is a
judgment made in the moment that nothing can check afterward. Exact age adds nothing to finding a
topic; the dosing table is read once the topic is open.

## Ruling 3 — every encounter search is checked before it is typed

A new command checks each **Outbound search** before it is typed and refuses digits, date shapes,
any patient name or date literal from the PHI corpus, any site string from the account profile, and
more than one population word or more than one sex word. A refused search is never typed. A passed
search is written to the run's record, and the completion grader refuses a live pull whose search
has no record line. The command cannot prove that the remaining words are clinical vocabulary; that
limit is declared beside it.

Recording and grading afterward was refused because a check after typing can only report a leak
that has already reached the third party. A written rule alone was refused because a skipped rule
looks the same as a followed one. The declared gap is a search typed with no check and no record
line, which leaves the grader nothing to find.

## Ruling 4 — the store joins every routed decision and the live account joins only the gaps

The store is searched at every routed Plan decision, beside the guideline sheets. The live account
is searched only where the guideline route would otherwise end in `recalled, no shipped sheet` or
`sheet does not settle it`. Symptom relief and generic return precautions stay exempt.

Both sources only at the gaps was refused because a store search is free and private, so a sheet
that has fallen behind current evidence should have a chance to be caught. Both at every decision
was refused because it multiplies live pulls through one signed-in browser across a shift. Asking at
the go-ahead was refused because the recalled item would stay the default.

## Ruling 5 — UpToDate wins a conflict, as it stands today

When UpToDate and a threshold sheet disagree, UpToDate wins. A conflict found in a store copy is
settled by a fresh live pull of that topic, through ruling 3's check, and the live version is what
wins; it is filed into the store and replaces the stale copy for later runs.

Letting the store copy win unconditionally was refused because a copy filed before UpToDate absorbed
a newer society guideline would put the older position into the note, the opposite of the rule's
purpose. Comparing the copy's last-updated date with the sheet's guideline year was refused because
it compares a month against a year and lets the sheet win against a copy a fresh pull might show had
already changed.

## Ruling 6 — a conflict UpToDate wins is shown and the sheet row is ticketed

A conflict UpToDate wins is shown at the go-ahead. The run's after-action review files a ticket to
re-read that sheet row, after searching for an open one so one conflict is filed once. The ticket
names only the sheet file, the row, the UpToDate topic title with its last-updated date, and what
differs; nothing from the encounter.

Leaving the sheet alone was refused because every later shift would pay a live pull for the same
conflict and the coursework skills would keep reading the outdated row. Showing it only at the
go-ahead was refused because the next shift rediscovers it.

## Ruling 7 — an UpToDate-backed decision is a tier-block tail

An item UpToDate backs carries a bracketed tail on its own `FILLED·proposed` line, in one of two
forms:

```text
[uptodate: <topic title>, updated <month year>, <dump id>]
[uptodate over thresholds/<sheet> <row>: <topic title>, updated <month year>, <dump id>]
```

The first replaces a `recalled` verdict where UpToDate filled the gap; the second records a sheet
conflict UpToDate won. No citation appears in the note body. The dump id names the store copy that
was read, so the claim can be reopened. Row 24 and `tools/differential_scan.py` learn both forms.

A reference list was refused because a note has never carried one, the Medatrax form has no place
for it, and it separates a source from the Plan line it supports. The run record alone was refused
because the clinician confirms generated Plan items from the tier block at the go-ahead, and an
UpToDate item would be indistinguishable there from a recalled one.

## Ruling 8 — a failed live pull keeps the run going and says so

When a live pull cannot be made (signed out, service unavailable, no topic found), a gap keeps its
existing `recalled` or `sheet does not settle it` verdict, and a conflict falls back to the sheet
with a tail ending `; uptodate pull failed`. The failure is listed at the go-ahead with the
instrument tried, and the run finishes.

Stopping the run was refused because one signed-out browser would hold a whole shift over one topic.
Falling back to the store copy on a conflict was refused because it undoes ruling 5's protection.

## Ruling 9 — `icd10-cpt` is outside this record

Codes rest on the note and the code sets. UpToDate's clinical position reaches a code only through
the note `clinical-note` already wrote. Admitting it as a reference for clinical definitions while
coding was refused because it reopens #85's ruling and lets the worksheet second-guess the note.

## Build checklist

- A new search-check command: refuse digits, date shapes, corpus names and date literals from
  `phi_scan.corpus_identifiers`, account-profile site strings, and a second population or sex word;
  write a passed search to the run record; a `DECLARED_LIMITS` object naming the unprovable
  clinical-vocabulary limit and the unchecked-and-unrecorded gap; tests through the public command
  for each refusal and a clean search.
- `skills/clinical-note/SKILL.md` *Guideline sheets*: the store search at every routed decision, the
  live search at the gaps, the conflict rule with its fresh pull, the failed-pull fallback, the two
  tail forms, and the go-ahead lines for conflicts and failed pulls; drift row 24 widened to match.
- `skills/batch-shift/SKILL.md`: pulls run one at a time through the signed-in browser across the
  shift, and the go-ahead review sheet carries the conflict and failed-pull lines.
- `tools/differential_scan.py`: read and grade both `uptodate` tail forms and the
  `uptodate pull failed` suffix; tests through the public command.
- The completion graders for `clinical-note` and `batch-shift`: refuse a live pull with no
  search-record line.
- The after-action review path: file the sheet-row ticket of ruling 6, search before filing, PHI-free
  content only.
- Store ingest of a live pull reuses `tools/uptodate_store.py ingest`, and a fresh pull after a
  conflict replaces the stale copy's topic for later searches.
- `CONTEXT.md`: **Outbound search**, written with this record.

## What this record does not reach

- **Whether a search's remaining words are clinical.** The check refuses known identifiers and
  shapes; a free-text word outside them passes.
- **A search typed without the check.** It leaves no record line, so no grader can see it.
- **Whether the UpToDate position applies to this patient.** That remains the clinician's reading at
  the go-ahead, as it is for a sheet row.
