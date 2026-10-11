# Case material and case research are declared context places and both libraries come first

**Measured at:** 85a56763aa5b22cd2419de5c3da24f90aa3408e9

[#1503](https://github.com/mshamblin5150-code/clinical-skills/issues/1503) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 2) on 2026-10-01. Two drafts were
written before the case material was opened, one draft faulted the classmate with a threshold the
clinician's own paper did not use, and one reference was retyped and lost a parenthetical. Grilled
2026-10-11 against `main`; the clinician ruled every point below in that session. **Nothing is built
here; this is the record the build reads.**

## Measured before ruling

**Half of the ticket's open decision had already been ruled.** The ticket asked whether the
clinician's own post and the case material should become places a run owes. [ADR
0325](0325-a-classmate-s-order-counts-only-for-the-patient-the-case-presents-and-the-clinician-s-own-submission-is-a-declared-context-place.md)
ruling 4, built on #1493, already makes every coursework run declare its **Own submission** in the
project-context record and refuses a declared file the record does not show opened. Since
[ADR 0290](0290-the-pre-draft-gates-observe-that-the-draft-does-not-yet-exist-and-a-late-gate-is-a-finding-the-clinician-clears.md)
was built on #1404, the same record observes whether the draft already existed when it was written.
Nothing names the case material.

**The Module 2 case material was the clinician's own file, not a course attachment.** His per-case
OneDrive file carries the module video's case data verbatim plus his own sanity-check, differential
and first-plan lines. [ADR 0324](0324-a-faculty-or-classmate-file-is-identified-on-the-live-page-and-matched-by-fingerprint-before-a-run-reads-it.md)
identifies and fingerprints files linked on the live course page, so it does not reach a case
delivered by video.

**The run did read the file, late, and nothing recorded when.** The Module 2 run's project-context
record lists six opened items, one of them the case-study file. The approved draft was rebuilt after
it was added. A final draft reads the same whether the file was opened first or brought in to repair
earlier drafts, which is why the clinician believed the run had read it.

**Only one coursework skill reaches the clinician's research.** Measured from the skill files: the
guideline index is a required routing step in `clinical-note`, is used by `icd10-cpt` and
`practicum-case-study`, and reaches `peer-critique` and `discussion-reply` only through a roster
paragraph in `skills/_shared/reference/rubric.md`; `discussion-post` and `course-assignment` never
name it. The **Evidence store** is searched only by `practicum-case-study`. `peer-critique` step 3
sends each claim to outside sources directly.

**The store's copy is a separate object from the clinician's Word file.** `uptodate_store.py ingest`
files a text copy beneath `scratch/uptodate/` with a **Dump manifest** carrying its fingerprint and
topics, and `uptodate_store.py search` reads only filed copies. A run that opened only the Word file
could leave the case's topics unsearchable.

**A research return is not kept as a file.** Under standing rule 6 each research worker returns its
record and the orchestrating context alone writes `claims.md`, so the retyping that dropped the
parenthetical happens in the parent of every coursework fan-out.

## Ruling 1 — the case material is a declared, opened context place

The project-context record gains one confirmed header line in all five coursework skills
(`course-assignment`, `discussion-post`, `discussion-reply`, `peer-critique`,
`practicum-case-study`):

```text
CASE-MATERIAL: <path> | none - <reason>
```

It declares the **Case material**, or that none exists and why. `tools/project_context.py` refuses a
record without exactly one such line, refuses `none` without a reason, and refuses a declared path
that the record does not show opened as an item of a read place. The tool locates nothing: the run
names the file and the clinician confirms it with the rest of the header, as for the own-submission
line. The line is part of the confirmed header the context digest covers.

A written instruction alone was declined because the recorded failure was a skipped written step,
and a skipped step looks the same as a run with nothing to read. Widening the own-submission line
to several files was declined because the gate could no longer say which declared file was missing.
Scoping the line to the skills that answer a case was declined because it needs a per-skill table
the own-submission line avoided, and never asks a post or assignment that turns out to rest on a
case.

## Ruling 2 — the case research is a declared, filed and opened store entry

The same header gains, in the same five skills:

```text
CASE-RESEARCH: <dump id> | none - <reason>
```

It names the **Dump manifest** entry of the clinician's **Case research**, never his original Word
file. Where a compilation exists it is filed into the **Evidence store** before drafting. The gate
refuses a missing line, a reasonless `none`, a dump id with no manifest, a filed copy whose
fingerprint no longer matches its manifest, and a filed copy the record does not show opened in a
read place.

Naming the Word file was declined because a run could open it and pass while the case's topics were
never filed, so the per-claim search in ruling 3 would miss them. Naming both was declined because
it doubles what the clinician confirms and needs a new comparison between the two. Requiring the
line only where `CASE-MATERIAL` names a file was declined because research can exist without a case.

## Ruling 3 — the Evidence store and the guideline index are every claim's first stop

In all five coursework skills, each research claim first searches the **Evidence store** and the
guideline index, before any outside source. Every claim record carries one line naming both, the
literal queries, and each hit count, zero included:

```text
SEARCHED-FIRST: store "<query>" -> <hits>; guidelines "<query>" -> <hits>
```

`tools/research_ledger.py` refuses a record missing the line or missing either search. It checks
shape only, and `research_ledger.DECLARED_LIMITS` states that a line written without the search
having run passes. The session's working name for the field was `LIBRARY-SEARCH`; it is renamed
because `CONTEXT.md` lists *library* as a term to avoid for the **Evidence store**.

Advice beside the guideline roster was declined because an unrecorded search looks the same as one
that found nothing. Leaving the store to the per-case line was declined because research from the
clinician's other cases would never reach a critique whose topic overlaps it. Having the grader
re-run the queries was declined because both collections grow, so honest records would go red as
counts drift, and the guideline index lives outside the checkout and is not always present.

## Ruling 4 — the clinician's UpToDate account is the standing second stop

Where neither search covers a claim, the research step searches the clinician's UpToDate account
through the **Authenticated route** before any outside source, without asking him first. Any topic
it uses is filed into the **Evidence store** as a supplement dump through the store's ordinary
ingest, so later runs find it. The same `SEARCHED-FIRST` line records the account search and the
dump it filed. Pulls go through his one signed-in Chrome one at a time.

This settles section 1 of [#1578](https://github.com/mshamblin5150-code/clinical-skills/issues/1578)
and widens it from `practicum-case-study` to all five coursework skills. Asking once per run, as
#1578 proposed, was declined because the clinician has given the same answer on Module 4 and here.
Leaving live pulls to #1578 was declined because critiques and replies would go from an empty search
straight to outside sources, the route he corrected on Module 4.

## Ruling 5 — a classmate is never faulted against the clinician's own position unasked

Where a critique or reply would fault a classmate on a point where the clinician's **Own submission**
took a different position, the run stops before drafting and asks him, naming both positions; he
may decide his own paper was wrong. A point his submission never reached is open to correction and
is judged against the evidence: his **Case research** first, because his final submission records
where that research led him, then the searches in rulings 3 and 4. A first-plan line in his own copy
of the **Case material** is his reasoning before research, not his position.

Barring a point automatically was declined because a real error of the classmate's would go unsaid
and the clinician would never see the disagreement. Barring every standard his submission did not
apply was declined because it removes the sourced corrections his ruling to lean into correction
asks for, most of them in the clinical reasoning and plan.

## Ruling 6 — the rule lives once beside applicable orders

Ruling 5 is one short section of `skills/_shared/reference/rubric.md`, beside the applicable-order
section ADR 0325 placed there, labeled as this repository's reading rule rather than the course's
words. `peer-critique` step 1 and `discussion-reply` step 1 each point to it. `peer-critique` step
1's existing sentence calling the clinician's post a comparison, not a standard, is folded into that
section rather than left as a second copy.

`peer-critique` alone was declined because a reply judges a classmate's work against the clinician's
with the same exposure. `skills/_shared/reference/sourcing.md` was declined because posts,
assignments and case studies have no classmate to fault.

## Ruling 7 — a research return's reference and restatement are pasted, never retyped

`skills/_shared/reference/sourcing.md` states once, for all five skills, that the orchestrating
context pastes each research return's `REFERENCE` and `RESTATEMENT` exactly as returned. The
refutation leg remains the backstop, and no grader checks this.

`peer-critique` alone was declined because every coursework fan-out writes its ledger the same way.
Keeping each return as a file for a character comparison was declined for now: it adds a file per
claim, and the comparison would have to exempt the heading rewrite ADR 0315 requires. Retyping that
keeps escaping the refuter is the evidence for building it later.

## Ruling 8 — the real-encounter skills are a separate question

This record covers the five coursework skills. Whether `clinical-note` and `batch-shift` consult the
**Evidence store** or the clinician's UpToDate account is
[#1704](https://github.com/mshamblin5150-code/clinical-skills/issues/1704). A live account search
from a real encounter types its terms into a third-party service, and that protected-health-information
question needs its own ruling. Widening this record to every clinical skill was declined because the
real-encounter half shares only the collections with it.

## Build checklist

- `tools/project_context.py`: parse, require and canonicalize `CASE-MATERIAL` and `CASE-RESEARCH`,
  bind both into the context digest, refuse an unopened declared path, and refuse a dump id with no
  manifest or a fingerprint mismatch; tests through the public command for each refusal and a clean
  record, and the go-ahead recheck of ADR 0328 covering both items.
- `skills/_shared/reference/sourcing.md`: the two header lines and what the gate refuses; the
  first-stop and second-stop order with the `SEARCHED-FIRST` line; the paste-never-retype rule.
- `tools/research_ledger.py`: require `SEARCHED-FIRST` with both searches on every record, with a
  `DECLARED_LIMITS` row for an unsearched line; the skill worked records updated so the suite's
  worked-example runs still pass.
- `skills/_shared/reference/rubric.md`: the section for ruling 5, beside applicable orders.
- `skills/peer-critique/SKILL.md` step 1 and `skills/discussion-reply/SKILL.md` step 1: pointers to
  that section; step 1's comparison sentence folded into it.
- `skills/practicum-case-study/SKILL.md`: the live-pull route of ruling 4 replaces any instruction
  to source a missing topic elsewhere first.
- `CONTEXT.md`: **Case material** and **Case research**, written with this record.
