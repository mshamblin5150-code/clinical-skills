# The case study scan grades layout, citations, cross-references and required sections

[#1019](https://github.com/mshamblin5150-code/clinical-skills/issues/1019) was filed on 2026-09-10
out of the after-action review of one `practicum-case-study` run. It named four shapes that reached a
graded document while `tools/case_study_scan.py` exited 0 — intake review sections set as run-on
paragraphs, a care-setting change left unrepaired in some sections, cross-references that no longer
landed, and a numbered MDM entry with no citation — and four decisions behind them.

Grilled 2026-09-13 to an empty frontier. **Eight rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. [ADR 0207](0207-a-case-study-reader-is-handed-the-house-rules-and-a-departure-is-ruled-at-the-go-ahead.md)
ruling 4 had already put a non-authoring re-read over every change after the first draft, so every
ruling below is weighed against a reader that exists rather than against none.

## What was measured before ruling

Every figure here was taken by a sweep reader and re-derived by running its script before it was put
to the clinician. Counts only; the drafts are private working material.

- **The population is five submitted case study drafts**, three of one Module 1 submission and one
  each for Modules 2 and 3. No working draft under a run directory was a case study.
- **Intake layout.** 72 field labels across the Review of Systems, Physical Examination and a
  developmental section, 19 distinct. Two paragraphs held more than one label, both in one Module 1
  draft, and both listed separate systems back to back (5 and 6 labels). No paragraph paired a
  system with a sub-label of itself.
- **MDM citations.** 46 numbered MDM entries, each a single block. 44 carry at least one in-text
  citation as `reference_scan.read_citations` reads it; 2 carry none and hold no parenthesized year,
  so the reader did not miss them. All 62 citation keys in MDM entries match a reference entry; with
  every year shifted by one, 8 of the body's 91 still match, so the match discriminates.
- **Cross-references.** 19 in the five drafts. 10 name their section (`Plan item N`,
  `Plan items N .. N`, `Patient Education item N`, `differential N`) and all 10 land in range. 9 name
  none (`... as entry N`, `... in item N`), and one of those runs past the end of the section it sits
  in. No `#N` or `No. N` form occurs.
- **Care setting.** The Module 2 run retained the draft carrying all five recorded leftovers. Counting
  a closed setting vocabulary in each leftover item before and after its repair: one entry carried the
  same terms both times, two carried no setting term either time, one lost a single term, and one
  swapped one term for another. The terms that changed remain correct elsewhere in the final draft,
  and the Assessment legitimately names the rejected setting.
- **Developmental headings.** The two pediatric drafts titled that material four ways. Only
  `Developmental History` holds a domain list, already one domain per line; `Growth Assessment` is one
  line of measurements, and the two growth-and-development examination or assessment sections are
  prose.
- **A misspelled heading.** Measured on 2026-09-11 and recorded on #1019: the ROS closer removed exits
  1 under `## Review of Systems` and 0 with no finding under `## Reveiw of Systems`, because the only
  coverage failure fires when no section is recognized at all.

## Ruling 1. The Review of Systems, the Physical Examination and Developmental History are one field per line

`skills/_shared/reference/style.md` §1a already rules the Review of Systems and the Physical
Examination one line per system. **Developmental History joins them**, one domain per line —
`Gross motor:`, `Fine motor:`, `Language:`, `Social:` — and is added to §1a and to the scanner's
intake section set. **Demographics stays a running line**, as §1a's own example writes it.

**Every labeled intake section was refused** because it reverses the 2026-08-19 demographics example
without a reason; demographics is short identifying data, where the review sections are a set of
systems or domains each carrying findings.

## Ruling 2. A system's line carries one label, and sub-findings are written in words

In those three sections, a paragraph holding two or more `Label: ` fields — a capitalized word or short
phrase and a colon followed by a space, at the start of the paragraph or after sentence punctuation —
fails. §1a gains the sentence that a system's line carries one label and its sub-findings are written
in running words: `Neurologic: Alert and oriented x3, strength 5/5 in all extremities, reflexes 2+ and
symmetric`.

**The strength assessment is not in question.** The clinician's correction, 2026-09-13: *"a strength
assessment is how we determine any neurological damage."* What is ruled is only the colon: `Strength: 5/5`
as a second label inside the neurologic line is written `strength 5/5`.

**A closed system vocabulary was refused.** Allowing colon sub-labels would make a neurologic line
with sub-fields indistinguishable from a run-on to a label count, so the row would need a list of
system names — which misses a run-on written with a synonym and has to be kept. With the colon ruled,
a label count carries no vocabulary and no false alarm on the house form.

## Ruling 3. Developmental History is the one recognized name, and growth material is left alone

The section is found by the exact name `Developmental History`, which §1a publishes. **Growth
measurements stay a running line** like demographics, and a growth-and-development examination or
assessment stays prose; the row reads neither. A variant title is invisible to the row, which is a
declared limit because ruling 7 makes this section optional.

**Recognizing the variants was refused** because it would read `Growth Assessment` and fail a correct
measurement line. **One measurement per line** was refused as a style rule nobody asked for.

## Ruling 4. Every numbered MDM entry carries at least one in-text citation

A numbered MDM entry with no in-text citation, as `reference_scan.read_citations` reads the entry's
text, fails. Whether a citation matches a reference entry stays `reference_scan`'s row, which already
refuses an unmatched citation across the whole document. `style.md` §5 gains the per-entry floor
beside *"Every clinical claim carries a citation."* **The two historical uncited entries were
defects.** The row reads the MDM only; the Assessment's teaching points are not in it.

**Choosing a citation reader was not a decision.** `discussion_artifact.reference_keys`, which
#1019's comments weighed against `reference_scan`, is the discussion-post reader; the case study's
reference list has always been read by `reference_scan`. **A marked exception** for an entry arguing
only from case data was refused, because such an entry still rests on a claim about how the disease
presents, and a marker is something a run learns to reach for. **Count and report** was refused
because §5 already states the rule.

## Ruling 5. An out-of-range cross-reference fails, and every cross-reference is listed beside its target

A **cross-reference** — the glossary term, added to `CONTEXT.md` with this record — whose number runs
past the end of the section it names fails. Under `--show`, every cross-reference prints beside the text
of the item it currently lands on, as a checklist for ADR 0207 ruling 4's re-reader. The default
report prints counts only.

**What the refusing half cannot reach is recorded beside it.** Insert a Plan item above item 3 and a
cross-reference to `Plan item 3` still resolves, now to the wrong order. A resolver fails only a list
that shrank past the number, so a clean run never means the cross-references land on the right items.
**Fail on a miss alone** was refused because it leaves the insertion case to a reader re-deriving each
by hand, which is what caught Module 2's. **Print only** and **no row** were refused because a
number past the end of its list is never correct.

## Ruling 6. The row reads a cross-reference that names its section, and counts the rest

The row resolves `Plan item N`, `MDM entry N`, `Patient Education item N` and `differential N`,
ranges included, against the section named. A cross-reference that names no section is counted on
every run, listed under `--show`, and never fails. `style.md` gains the sentence that a cross-reference
names its section.

**Resolving an unnamed cross-reference against the section it sits in was refused** on the measurement:
one of the nine already written would have resolved against the wrong section. **Failing an unnamed
cross-reference** was refused because `item 4` or `entry 4` that is not a cross-reference at all
would fail too, and the measurement could not say how often that happens.

## Ruling 7. Six sections are required, and a row whose section is missing is not graded

The Review of Systems, Physical Examination, Differential Diagnoses, MDM, Plan and Patient Education
must each be recognized. A draft missing any of them exits 2; a finding still exits 1. A row that
reads a missing section prints `not graded` rather than `0`. Every run prints the count of headings
the scanner did not recognize. Developmental History and Faculty Questions are optional, and a
misspelled optional heading is a declared limit.

**It is widened into this record rather than left to [#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066)**
because each row that rulings 2, 4 and 6 add reads one named section, so a misspelled heading turns that
row into a clean pass over nothing — the defect is in these rows' correctness, not only in the family.
#1066 keeps the lead for every other `run_grader` member and for this module's rows outside those six
sections. **The whole skeleton** was refused as reaching rows this ticket did not ask about.

## Ruling 8. Care-setting agreement across sections is a reading, and no row reads it

No row is built. `case_study_scan.DECLARED_LIMITS` gains a declared-reading entry: agreement of the
care setting across sections is a reading, owned by ADR 0207 ruling 4's re-read row.

**A declared disposition field with a closed vocabulary was refused on the Module 2 measurement.**
*Had a vocabulary match separated a leftover from its repair, the counts would have differed at every
leftover*; they differed at two of five, and the words that changed stay correct elsewhere in the
final draft. The leftovers that mattered argued from the old setting without naming a setting word.
**A per-section count report** was refused because it would have pointed the re-reader at the wrong
places.

## What this record does not settle

- **Whether a cross-reference lands on the right item.** Ruling 5's listing puts it in front of a
  reader; nothing mechanical decides it.
- **Whether an MDM citation supports its claim.** Ruling 4 establishes that a citation is present.
- **A table inside the Physical Examination.** `style.md` §1a allows a vital sign set as a table while
  the existing `intake-table` row fails any table in that section. Noticed during this grilling, not
  driven, and not ruled here.
