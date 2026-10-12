# A case study's differential ranks by three defined standings, and its pre-review walks are written records a grader shapes

**Measured at:** b6dc5d408fc3b56f22cfac505b331fcea65c5c5e

[#1575](https://github.com/mshamblin5150-code/clinical-skills/issues/1575) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). It proposed
ten drafting rules for the differential, the MDM and the Assessment, each learned from a reader
correction made one round at a time. Grilled 2026-10-12 against `main`; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Every hunk still applies to `main`.** Each of the ticket's ten diffs was compared with
`skills/practicum-case-study/SKILL.md` at the commit above; every context line is present and no
two hunks change the same line. No sibling ticket from the same review (#1576 through #1578) and no
ADR rules on any of the ten subjects.

**The skill names standings loosely and in three words.** It says a rare diagnosis is "argued down
in the MDM", that "Ruled-out entries end on the verdict", and that pregnancy emergencies rank first
"until imaging or a test excludes them". Nothing defines which evidence moves an entry from one to
another.

**The signed bar is checked only after drafting.** In this skill the faculty to-do reader compares
every signed bar element with the finished draft on a routed board run. The departure entry and the
wrapper-instruction clause, the two sanctioned ways to say an element does not apply, exist only in
this skill. `discussion-post`, `discussion-reply`, `peer-critique` and `course-assignment` also sign
a bar and have neither.

**The completion grader is `checks_ledger`.** `aar_scan.COMPLETION_GRADERS` pairs
`practicum-case-study` with it.

## Ruling 1 — five of the ten rules are adopted as the ticket writes them

Sections 1, 2, 5, 7 and 8 of #1575 land as their diffs read, subject only to Ruling 3's wording.
A diagnosis the documented history makes anatomically impossible takes no differential entry, no MDM
entry and no promotion trigger, and one Assessment sentence names the history line that excludes it;
the worked MDM completeness record's "the prior appendectomy" becomes "the afebrile course". A
causal link drawn between two of the clinician's listed diagnoses, or a code for the combined
condition, needs its own step 3 claim record and its own `### DEPARTURE:` entry. The promotion
trigger sits in the MDM entry of the diagnosis it promotes. A clinician ruling is restated in its
own scope words. A visit-date assumption is written into `proposed-<date>.md` before drafting
whenever a recommendation depends on the date.

## Ruling 2 — the cited source's emergency list is walked before the first reader round, and the walk is written down

Section 3 is adopted with a record. Before the first reader round the run writes, in the run
directory and outside the graded document, the source it walked for the presenting complaint and
every emergency that source lists for this complaint in this population, each with its outcome:
ranked at a named position, or excluded by a named faculty-material line or test. Where the run
cites more than one source for the complaint, the record names each source walked. Adopting the
rule as an unrecorded instruction was declined, because the defect was a list that came out
incomplete one round at a time and an unrecorded walk leaves a reader unable to tell a complete one
from a skipped one. Keeping only the existing pregnancy-first bullet was declined as leaving that
defect open for every other complaint.

## Ruling 3 — three standings are defined and the skill's ranking and verdict language uses them

`CONTEXT.md` defines **Ruled out**, **Argued down** and **Impossible on the history**, and the
skill's rules from this ticket and its existing ranking text use those words and no synonym.
Ruled out means a test, imaging, or every observation the criterion requires excludes the
diagnosis. A criterion defined by change over time requires two observations, so one examination
never rules a diagnosis out on that criterion; where such a criterion carries weight, the Plan
orders the repeat observation and the MDM says argued down until it is back (section 6). Leaving
the words undefined was declined: under Ruling 4's order an entry one examination "excluded" would
sink below the untested emergencies, while section 6 says that examination ruled nothing out.

## Ruling 4 — the full differential order is one sentence

The diagnosis the patient meets most of the published criteria for is number 1. Every emergency
not ruled out comes next, ordered by what would kill or maim first, even where the history argues
it down. The other diagnoses not ruled out follow by likelihood. Ruled-out entries come last.
Section 4's rule is this order's third and fourth clauses. Ranking an untested emergency above a
criteria-met diagnosis was declined, because it partly reverses the earlier criteria-lead
ruling, which a grader also enforced; the emergency at number 2 stays visible and worked up.
Adopting section 4 without placing it against the criteria-lead rule was declined as leaving the
next run to reconstruct the order from three paragraphs.

## Ruling 5 — the signed bar is walked before the first reader round, in this skill only

Section 9 is adopted with a record. Before the first reader round the run writes each element
`bar.md` carries with its outcome: met in a named section, or inapplicable with its one clause
under the wrapper-instruction rule and a `### DEPARTURE:` entry. The faculty to-do reader confirms
the walk; it does not replace it. Extending the walk to the four other skills that sign a bar was
declined: the defect is recorded only here, and only this skill has the departure outlet an
inapplicable element needs. A dropped element in another skill's run is filed from that run's
review with its own evidence.

## Ruling 6 — every stated negative and descriptor is traced and the trace is written down

Section 10 is adopted with a full record. Before a draft is placed for a reader round, the run
writes every absent symptom, normal finding, examination descriptor, negative history item and
qualifier on a result the draft states, each beside the faculty-material line it came from; one
that names no line is marked cut or ordered and the draft is changed to match. The same rule binds
what the run tells the clinician in chat. An unrecorded trace was declined because the defect
recurred after its first repair. Recording only the negatives stated outside the transcribed
intake sections was declined, because the run's own recorded instances include an examination
descriptor added where transcription belongs.

## Ruling 7 — the completion grader refuses a missing or outcome-less record

`checks_ledger`, the paired completion grader, gains a shape check over the three records Rulings 2,
5 and 6 create. A record that is absent, or that carries an entry with no outcome from its closed
vocabulary, is a finding. The check reads shape only. Whether the right emergencies, elements and
source lines were recorded stays a reader's judgment, and the step 9 reader briefs that read the
records belong to #1577. Leaving the records to readers alone was declined: a skipped record would
look exactly like a completed walk. The new check enters `reference/completion-check-starts.tsv`
like every later check, so runs drafted before it are not graded on it.
