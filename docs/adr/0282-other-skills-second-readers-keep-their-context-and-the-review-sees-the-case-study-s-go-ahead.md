# Other skills' Second readers keep their context, and the review sees the case study's go-ahead

**Measured at:** 6f7bf3d3dbfedbb26ed0f5e6f3947e52861f11f4

[#1217](https://github.com/mshamblin5150-code/clinical-skills/issues/1217) was filed from
[#1017](https://github.com/mshamblin5150-code/clinical-skills/issues/1017)'s grilling.
[ADR 0207](0207-a-case-study-reader-is-handed-the-house-rules-and-a-departure-is-ruled-at-the-go-ahead.md)
ruling 1 hands every `practicum-case-study` step 9 reader the part of that skill above *Steps*,
marked settled and never reportable, and its *What this record does not settle* left open whether
any other skill's Second reader needs the same. Grilled 2026-10-03 against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

### The population

**Fourteen Second reader paragraphs sit outside `practicum-case-study`.** The population is the
paragraphs of `skills/*/SKILL.md` that declare the bolded kind, read with
`tools/briefing_surface.py`, whose `surface_findings` returns no finding on the tree measured, so
every spawn-vocabulary line sits inside a declared surface. A separate literal search for the kind's
name over the same files returns the same fourteen. They are about ten reader roles, because the
descriptor-agreement reader appears in `icd10-cpt`, `clinical-note` and `batch-shift`, and the
heading read is one shared protocol:

- `aar`: the after-action classifier;
- `icd10-cpt`: the blinded specificity reader and the descriptor-agreement reader, the second
  inherited by `clinical-note` and `batch-shift`;
- `course-assignment`: the visual, presentation-intent, adversarial investor and heading readers;
- `discussion-post`: the differentiation, heading and Canvas-box visual readers;
- `discussion-reply` and `peer-critique`: one heading reader each.

Nested support files are outside that population by `briefing_surface.DECLARED_LIMITS`. Three
nested readers were read anyway: the DOCX visual reader in `course-assignment/references/docx.md`,
the Planter and Voice reader in `_shared/reference/voice-read.md`, and the heading-read protocol in
`_shared/reference/sourcing.md`.

### No reader outside the case study has misreported settled form

**No tracker record or ADR records a reader outside `practicum-case-study` reporting settled house
form as a defect.** Had one done so, the instrument would have printed an issue or ruling recording
it; the searches ran over the readers' names and over the misread's phrasings. It is a floor: a
misread nobody recorded is invisible to it. The records closest to the shape run other ways. A
reader missing a source it needed reported a false defect
([#1506](https://github.com/mshamblin5150-code/clinical-skills/issues/1506)). A reader missing a
fact recorded only in memory returned a false clean
([#1505](https://github.com/mshamblin5150-code/clinical-skills/issues/1505)). A reader missing
rules it needed placed its quotations wrongly
([#1459](https://github.com/mshamblin5150-code/clinical-skills/issues/1459)).

### The boundary ADR 0207 uses does not exist elsewhere

The part above *Steps* is house rules only in `practicum-case-study`. Elsewhere it holds:

- scope, run identity and paths in `course-assignment`, which has no `## Steps` heading at all;
- the input and the code set in `icd10-cpt`, whose coding rules sit inside its steps;
- nothing in `batch-shift`;
- the bar-location trap in `peer-critique`, whose house form sits inside its steps;
- in `clinical-note`, a thousand lines that include how the note and its coding summary are
  produced. ADR 0207 refused exactly that for a reader, because a reader holding the author's
  process is less independent.

### Two recorded findings a settled marking would have suppressed

**DOCX visual readers reported producer styling as APA defects, and the clinician accepted them as
real** ([#1498](https://github.com/mshamblin5150-code/clinical-skills/issues/1498)), while
`course-assignment/references/docx.md` describes that styling as intended. **The agreement reader
failed seven clinician lay labels that the index does not reach**
([#1475](https://github.com/mshamblin5150-code/clinical-skills/issues/1475)), while
`clinical-note` states that paraphrased labels are correct. Marking either source as settled and
never reportable would have hidden a true finding.

### What is missing is a grading rule, and in four places

- **The after-action classifier** receives only its extract and the memory index. Nothing in
  `skills/aar/SKILL.md` or `tools/aar_scan.py` reads a run's departure list or its `GO-AHEAD:`
  line, which ADR 0207 ruling 2 put in `practicum-case-study`'s `proposed-<date>.md`. The review of
  the run #1017 was filed from called an approved departure unruled. That is the one recorded miss
  outside #1459.
- **The descriptor-agreement reader's** generated brief omits rules the skill states, including the
  hedged-diagnosis rule and the refused role, and says nothing about filled values. #1459 records the
  misses and carries the proposed repair.
- **The Canvas-box visual reader** compares the box with the Markdown without being told the
  renderer's settled mappings: every heading becomes a bold paragraph, and a quotation renders at
  its calibrated offset rather than APA's indent. No miss is recorded.
- **The `discussion-reply` and `peer-critique` heading readers** are not told that a paraphrase of
  the classmate and a statement of agreement need no record, which both skills state.
  `sourcing.md` exempts only the clinician's own reasoning and experience. No miss is recorded.

### Which input lists are blinding whitelists

The specificity reader's list blinds it to the worksheet's answers, and the Voice reader's keeps
house style out on purpose under
[ADR 0275](0275-a-voice-read-compares-a-planted-copy-of-the-draft-with-the-voice-model.md)
ruling 8. House rules would breach both. The heading read's list blinds it to sources, and house
rules are not sources: `practicum-case-study` step 9 already hands its heading reader both. The
`discussion-post` differentiation reader's list is not a blinding whitelist, because the blinding
in that skill is on the drafter.

## Ruling 1. ADR 0207's settled context stays scoped to `practicum-case-study` step 9

No other skill's Second reader is handed house rules marked settled and never reportable. The
evidence that grounded ADR 0207 exists only in that skill, the boundary it uses exists only there,
and the evidence from the other skills shows the same marking suppressing true findings. If a reader
elsewhere later misreports settled form, that skill takes its own ticket on its own evidence.

## Ruling 2. A missing grading rule is built where a miss is recorded and declared where none is

The fix for the after-action classifier is #1217's build, ruled below. The descriptor-agreement
evidence belongs to #1459, which already carries its options, so this record adds no second copy of
that decision. The Canvas-box mappings and the heading-read paraphrase exemption are declared known
and unbuilt; each becomes a ticket on its first recorded miss.

## Ruling 3. The review extract carries each case-study departure list and its go-ahead

In every round, `aar_scan.py --extract` writes one entry for each `proposed-<date>.md` in the run
directory that carries the departure section ADR 0207 ruling 2 defines. The entry holds every
`### DEPARTURE:` block and the section's `GO-AHEAD:` line as written. A section with no go-ahead
line is carried without one, so an unapproved departure stays visible, and a run with no such file
writes no entry.

The entry has its own kind in `aar_scan.ENTRY_KINDS` and is extractor-written, so a correction may
not be placed on it. A sustain may name it. The classifier's input list stays the extract and the
memory index, and `skills/aar/SKILL.md` step 2 says that a listed departure under a go-ahead is
ruled, not unruled.

The population is every departure list a scoped skill records. Today that is only
`practicum-case-study`.

## Rejected options

**Extend ADR 0207 to every Second reader with house rules it could see.** It needs a curated settled
list per skill, the kind of list ADR 0207 refused. It would have hidden both recorded true findings
above, and it breaches ADR 0275 ruling 8.

**Extend it only to the two readers at risk with nothing recorded.** That builds against a risk
nobody has seen happen, and *never reportable* is the wrong tool if the rendering really does break.

**Widen #1217 to all four grading-rule gaps.** Two have no recorded miss, so building them applies
the evidence standard ruling 1 declined.

**Add the departure file to the classifier's input list in prose.** Nothing fails when an
orchestrator forgets to attach it, and the extract is already the reader's whole population.

**Make the orchestrator check the go-ahead before accepting an unruled finding.** The record of
#1017 cannot say whether the classifier or the orchestrator wrote that claim, so this may assign the
duty to the context that erred.

## Consequences

**A review of a case-study run sees what the clinician approved** before it classifies a departure.

**#1217's question has a measured answer**, and the next skill that adds a Second reader inherits
ruling 1's default rather than an open question.

## What this does not reach

**A misread nobody recorded.** The measurement is a floor, and ruling 1's revisit trigger depends on
a miss being written down.

**Whether a classifier read the entry.** A well-formed classification cannot show which entries it
used, the ceiling ADR 0207 already declares for step 9.

**Defects the measurement found outside its question.**
[#1524](https://github.com/mshamblin5150-code/clinical-skills/issues/1524) carries the heading-read
surfaces' input lists, their no-second-context route and the DOCX branch's missing heading-read text.
