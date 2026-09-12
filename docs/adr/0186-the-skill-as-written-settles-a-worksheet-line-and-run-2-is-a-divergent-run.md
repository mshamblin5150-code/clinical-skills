# The skill as written settles a worksheet line and run-2 is a divergent run

[#1104](https://github.com/mshamblin5150-code/clinical-skills/issues/1104) was filed out of
[#1038](https://github.com/mshamblin5150-code/clinical-skills/issues/1038)'s grilling under
[ADR 0178](0178-four-run-graders-earn-limits-objects-on-a-measurement-and-a-code-versus-docstring-gap-is-fixed-rather-than-declared.md)
ruling 11, which sent the remaining defects to one `grilling` ticket split by grader: a grader
failing input somebody called correct, and prose claiming an exit status a command no longer
returns. Its tables hold nine such rows across `anchor_scan`, `filled_vitals_census` and
`specificity_scan`, and three prose claims about `fixtures/filled-anchor/run-2`.

Grilled 2026-09-11. The session began at `0fdb4ba`, was carried forward to `origin/main`
`82092fc` when the freshness gate reported `STALE` mid-session, and every figure below was
re-derived at `82092fc` after that merge. That merge changed none of the three modules and none of
the `CLAUDE.md` sections this record corrects. **Fourteen questions were ruled by the clinician on
that date**, one at a time. The closing summary, including the conventions applied without a
question, was confirmed.

**The ticket's framing did not survive the measurement.** It presents every row as a grader failing
correct input. Nine rows were driven against the committed set one at a time, and most of them are
a grader reporting a correct verdict about a worksheet that departed from the skill. One row is a
pure scanner defect, three are settled by a single format rule the skill never wrote down, and the
run's own written rationale for the sharpest row is falsified twenty-eight times by the same run.

## Measured before ruling

Every figure here is re-derivable by a command over a committed directory. Exit statuses were read
from `$?` and never through a pipe.

### run-2's exits

| command | exit | report line |
| --- | --- | --- |
| `anchor_scan` | 1 | `A1 - pediatric not computed 2` |
| `specificity_scan` | 2 | `without a paired flag 10` |
| `refusal_scan` | 0 | `findings 0` |

So run-2's README's *"All three exit 0 on this directory"* and `assertions.md`'s *"Run 2 scored C5
and it passes"* are both false today, and `CLAUDE.md`'s **Specificity scan** claim that C5's figure
*"is re-derivable rather than cited — one command over a directory a reader can open"* is false
while that command exits 2 there.

### The ten unpaired codes partition exactly

Exactly one of the ten fails a real code shape. `specificity_scan.ENTRY` captures the code as
`([A-Z0-9][A-Z0-9.]*)` under `(?i)` and applies no code-shape test, while `anchor_scan.CODE` in the
same repository already carries one. The hard-wrapped prose line at `case-08.md:381` therefore
parses with `or` as its code. The other nine are real code numbers on lines that should not open an
entry: four `ALSO PROPOSED ABOVE` markers in `case-03.md`, two `NOT FOR ENTRY` tails in
`case-05.md`, three system-prefixed step-4 listing lines in `case-06.md`.

### The step-4 block re-lists only codes proposed above

Across run-2, `marked` is 29, `listed` is 29 and the symmetric difference is 0. A line inside the
`CODED, ANCHOR WAS FILLED` block is never a new code. `specificity_scan` has no notion of that
block and is immune today only because 26 of its 29 listing lines omit the system token `ENTRY`
requires.

### Holding `LISTING` to the skill's template

`skills/icd10-cpt/SKILL.md` writes the listing as a bare code, a dash and a value.
`anchor_scan.LISTING` makes a bullet, bold and the system token all optional. Driven over run-2:

```
as shipped                                      findings=2
no system prefix                                findings=5
skill template only (no bullet, bold or token)  findings=5
```

The whole cost is `case-06.md`'s three prefixed lines; no run-2 listing uses a bullet or bold.

### The same situation, six worksheets, two answers

A code both proposed for entry and named on a differential line occurs in six of run-2's twelve
worksheets. **Twenty-eight instances write `NOT FOR ENTRY`. Four write `ALSO PROPOSED ABOVE`, all
in `case-03.md`**, whose own prose states the reason: writing `NOT FOR ENTRY` on `B86` *"would
refuse this encounter's final diagnosis."* `case-07.md` proposes `U07.1` for entry anchored to a
positive test and writes the same code on its differential line as a plain `NOT FOR ENTRY`, with
nothing refused.

### Detail-line pairing has no lower bound

`anchor_scan.owner()` and `specificity_scan`'s flag loop both walk to the nearest recognized entry
above with no bound at all. Over run-2's 524 recognized detail lines: every one is indented exactly
two spaces, and 522 sit with no blank line between themselves and their owner. The two that do not
are `CONFIDENCE:` lines inside step 4's `NOT CODED, NOTHING ESTABLISHED IT` records in
`case-01.md`, paired 129 and 140 lines upward across 23 and 24 blank lines. **That is a live
mis-pairing in the committed set**, silent only because `anchor_scan` reads `CONFIDENCE` for
pediatric bands alone.

A contiguity bound — every line between the detail line and its owner is non-blank and indented —
keeps all 522 and drops exactly those 2.

Driven against the ticket's two false-finding rows:

```
anchor_scan, E66.3's label bolded
  as shipped        marked-not-listed R06.89  +  listed-not-marked E66.3
  contiguity bound                               listed-not-marked E66.3
  contiguity bound, unchanged worksheet          (nothing)

specificity_scan, a dashed code label with a plain flag under it
  as shipped        bare-flag M79.675 [Pain in left toe(s)]
```

In both, the named code did nothing wrong. Placed where no entry precedes it, the same shape emits
`bare-flag` with an empty code, so a bound alone would trade a false accusation for a codeless one.

### B18's age vocabulary

`skills/clinical-note/SKILL.md` states the person rule entirely by example.
`filled_vitals_census.NAMES_AGE` accepts three families the skill never lists and refuses three it
never excludes. Driven:

| clause | reads | |
| --- | --- | --- |
| `36-year-old male` | passes | the form all four compliant fixture heights use |
| `36 y/o male` | passes | |
| `36 y.o. male` | fails | the same abbreviation, different punctuation |
| `age 36, male` | passes | |
| `age: 36, male` | fails | the same construction, a colon |
| `thirty-six-year-old male` | fails | a different form |
| `36M` | fails | correct and already ruled: a spelled sex is required |

`tools/test_filled_vitals_census.py` pins four accepting cases and not one rejecting case, so the
boundary is held only from the side that passes.

### `SOURCE` values

`anchor_scan.FILLED` is a word search applied anywhere in the value, so
`SOURCE: recorded, not filled` marks the code as filled. All 29 `SOURCE` values in run-2 **begin**
with the word `filled`, which is the form `skills/icd10-cpt/SKILL.md` documents, and none carries
`filled` anywhere but first.

### One grammar, written twice

`anchor_scan.ENTRY` and `specificity_scan.ENTRY` are byte-identical modulo one capturing group;
their `FIELD` and `NOT_FOR_ENTRY` patterns are byte-identical. `refusal_scan` holds a different
`NOT_FOR_ENTRY` and grades a different block.

### The README's reconciliation is two offsetting errors

run-2's README states *"The two halves reconcile exactly and that is the check, not decoration: 297
entry lines less the 87 ending in `NOT FOR ENTRY` is 210."* Both 297s are computed over different
sets of the same size, and the difference is exactly one line in each direction, both hard-wrapped
prose: `case-08.md:381` is matched by `ENTRY` and not by the published grep, and `case-06.md:133`
is matched by the grep and not by `ENTRY`.

### What opens the filled-anchor block

`anchor_scan.BLOCK_HEADING` searches anywhere in a line. Seventeen lines open the block across
run-2 and seven are not the documented delimited form: five genuine prose mentions, and **two
worksheets that write the heading as `### --- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING
---`**, which opens only because `BLOCK_HEADING` is tested before `OTHER_HEADING` would close on
the `###`. Driven:

```
as shipped                      findings=2   blocks read 12 of 12
delimited only                  findings=5   blocks read 10 of 12
delimited, optional ### prefix  findings=2   blocks read 12 of 12
```

The five prose mentions cost nothing today because nothing they collect matches `LISTING`.
`case-04.md`'s block is genuinely empty, so only `case-08.md` pays.

### Two rows re-derived and discharged

`block_scan`'s "Not filed" lead — a bullet list after an unfenced tier block — was rebuilt on
`notes/case-01.md` and exits 0 with every row 0. The call to file it nowhere stands.

The absent `exit_2_limbs` on thirteen of seventeen `run_grader` members is **a ruled design and not
a gap**. ADR 0114 ruling 4, ADR 0116 rulings 5 and 6, ADR 0117 ruling 3 and
[ADR 0118](0118-the-conformance-kit-shapes-a-migrating-grader-s-value-and-vocabulary-and-the-fixture-row-is-the-finding-kind.md)
ruling 3 all decline it, the last by name for `filled_vitals_census`, and ADR 0170's rejected
options list a family-wide requirement. It was raised in this session as a finding and it is not
one.

## Ruled 2026-09-11

### 1. The skill as written is the referent for whether a line is correct input

`skills/icd10-cpt/SKILL.md` and `skills/clinical-note/SKILL.md` settle whether a worksheet or note
line is correct. A line in a form the skill documents must be read, and a grader that misses it is
the defect. A line in a form the skill documents nowhere is unruled, and the repair is to rule it in
the skill and then move the grader — never to widen the matcher first. run-2 is evidence of what the
skill produced on one day; it is not the referent.

This sorts three rows out of contention immediately. `case-08.md`'s prose line is a scanner defect,
because no skill makes `or` a code. `SOURCE: recorded, not filled` is a divergence, because the
skill says a `SOURCE` line appears only where the anchor was filled. A subheading inside the step-4
block is a divergence, and is already a declared limit.

### 2. A field value owns one physical line, and a fixed phrase owns its line

Every worksheet field value is a single physical line. Where the skill specifies a fixed phrase —
`NOT FOR ENTRY` at the end of a code line, the affirmative CDC `CONFIDENCE` sentence — that phrase
runs to end of line with nothing after it. Open-ended values carry whatever they carry, still on one
line. The skill already distinguishes the two kinds: its `SOURCE` template documents a trailing
clause and a semicolon, and its `CONFIDENCE` template documents a choice between two fixed phrases
with nothing after.

All three graders already read this way, so the work is a sentence in the skill and controls. Four
rows fall to it: a wrapped CDC sentence, a CDC sentence with a trailing clause, a wrapped
`SPECIFICITY` reason, and a `NOT FOR ENTRY` carrying a tail. The committed cost is two lines in
`case-05.md`, the second of which also wraps.

### 3. A step-4 listing line carries no code-system token

`anchor_scan.LISTING` narrows to the skill's template on all three axes — no bullet, no bold, no
system token — including the two axes with no committed instance. `case-06.md`'s three prefixed
lines become a divergence that both graders report, and `anchor_scan` over run-2 goes from two
findings to five.

The token is redundant in that block by construction: it re-lists codes already proposed above, each
carrying its system on its own entry line, so the token restates something one screen up while being
the exact character sequence that makes the line look like a new entry to the other grader.

**`specificity_scan`'s blindness to the step-4 block becomes a latent shape rather than a defect.**
A compliant listing line can never match `ENTRY`, so the consequence is unreachable. It is recorded
with its join named — a listing line that matches `ENTRY` — on `CONTEXT.md`'s **Latent shape** and
**Join** terms.

### 4. No second differential marker, and the differential template gains its prose line

`NOT FOR ENTRY` refuses the **line** and not the code, so a differential line naming a code proposed
for entry above still reads `NOT FOR ENTRY`. The skill gains that sentence. `case-03.md`'s four
`ALSO PROPOSED ABOVE` markers are a divergence and `specificity_scan`'s four findings there are
correct verdicts.

The run's written rationale is false and its own output disproves it twenty-eight times to four,
one worksheet against five. A second fixed phrase would mean every consumer must know both while the
next run invents a third; `NOT FOR ENTRY` being one phrase is most of what makes it checkable.

**Folded in on the clinician's word rather than filed:** the differential template shows no prose
line above the code line while every run writes one, and rulings 2 and 4 together remove
`case-05.md`'s tail idiom for saying *why*. The skill's differential template gains the prose line,
so the next run has somewhere to put the reason instead of inventing a tail or a marker.

### 5. Detail-line pairing is bounded by contiguity, and an orphan is counted

A detail line pairs with the entry above only when every line between them is non-blank and
indented. A detail line that pairs with nothing is **counted and printed on every run**, and is
never a finding — including the codeless `bare-flag` shape a bound alone would otherwise produce.
The count is reported and does not gate the exit status.

The bound is exact on the committed set, costs nothing on correct input, and stops a grader
accusing a code of a defect on a line belonging to a different code, which is the most expensive
false finding this repository produces because the named code looks fine when a reader opens it. It
is a narrowing, so #1066's must-not never fires. The count is what keeps it honest: dropping an
orphan silently trades a loud false finding for a quiet true miss.

Gating it was declined. Exit 2 means *not having scanned*, and an orphan is something the command
did read and could not attribute.

### 6. The absent exit-2 vocabulary is not folded in, and nothing is filed

ADR 0118 ruling 3 stands. Its reason holds today — prose with no code copy has nothing to diverge
from — and none of this ticket's rows needs the vocabulary, because ruling 5 reports rather than
gates. *Don't file* is satisfied by that ruling already holding the record and naming the shape of
the ticket that closes it: one ticket over every member, not a clause in another ticket.

### 7. Both modules declare the pairing bound

Ruling 5 makes `specificity_scan`'s `"nearest-entry flag pairing"` entry false, so under ADR 0178
ruling 7 its control fails and the entry is rewritten in the same change. `anchor_scan` gains the
matching entry it never had. Both get controls asserting today's result.

The asymmetry is the defect rather than the wording: two modules running the same walk, one
declaring it and one silent, is how a reader comes to believe `anchor_scan` bounds something it does
not. Retiring the entry was declined — the bound moves the boundary rather than closing it, since a
detail line can still pair with nothing, which is why ruling 5 counts them.

### 8. Naming an age is digits and a unit, and punctuation is not graded

The clause names the age in digits, followed by a year, month, week or day unit however abbreviated,
or after the word `age`. Punctuation between the parts is not graded, so `NAMES_AGE` tolerates a
period, a colon and a slash. A number spelled as a word is not an age, and the skill says to write
digits. The residue is declared with rejecting controls, which the module's tests have none of
today.

`y/o` passing while `y.o.` fails is not a rule anyone made; it is what the alternation happened to
list, and a grader that accepts one and refuses the other fails a correct note while teaching a run
nothing. The spelled-out number is different in kind: every other value in that block is a digit,
and B18 exists to show the anchor was read.

**Narrowing the skill to the single committed form was declined on the blast radius rather than on
the merits.** Rulings 3 and 4 narrowed against populations measured in full. The notes this would
newly fail live under `scratch/` and `output/` and cannot be counted, and the failure would fall on
correct notes rather than defective ones.

### 9. A `SOURCE` line marks only when its value begins with `filled`

The predicate anchors to the documented form. A recognized `SOURCE` line whose value does not affirm
is counted alongside ruling 5's orphans rather than dropped.

`anchor_scan`'s own declared limit says only a value that *says filled* marks its code, and
`recorded, not filled` says the reverse, so this is `CONTEXT.md`'s **Declared limit** exclusion — a
mechanism doing the opposite of its own documentation — and ADR 0178 ruling 10's class. A negation
vocabulary was declined: `not filled`, `never filled`, `no longer filled` is a closed set nobody
has, and its miss is a code marked as filled that the document says was not.

### 10. One module owns the `icd10-cpt` worksheet grammar

A shared module holds `ENTRY` — gaining the code-shape test that stops `or` parsing as a code —
`CODE`, `FIELD`, `NOT_FOR_ENTRY` and the pairing bound. `anchor_scan` and `specificity_scan` import
it. `refusal_scan` keeps its own `NOT_FOR_ENTRY`, declared rather than drifted, because it grades a
different block and this ticket has no measurement on it.

[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test is whether the
divergence is legitimate, and here it is the defect: the two read the same file and must agree about
what a code entry is, or they grade different populations of one document and nothing reports it.
That is `reference_scan` importing `docx_write.REFERENCE_HEADING`, and ruling 3 records the live
instance. One grader owning it was declined because neither is the producer; the producer is a
Markdown file.

### 11. run-2's verdicts stand qualified, and six prose sites are corrected

C5's zero faults are a true statement about the 200 flags graded, over a population the command
reports as incomplete. Withdrawal was right for run 1's `ANCHOR 5/5` because
[#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) reversed the rule; nothing
here reverses C5. Retracting a true finding because its denominator was overstated throws the
evidence away with the error.

The qualification is not optional: a clean number over an incomplete read is what the
extractor-coverage rule forbids. Corrected are run-2's README exit claim, `assertions.md`'s C5
sentence, `CLAUDE.md`'s **Specificity scan** re-derivability claim, the README's published `grep 1`,
its reconciliation paragraph, and its `case-04` paragraph — which credits `anchor_scan` with reading
the block's line format when under ruling 14 it reports none because it never finds the block.

run-2's README gains a divergence section naming four classes and each command's exit.

### 12. A `NOT CODED` record may carry a `CONFIDENCE` line, and step-4 blocks are outside the pairing population

The skill's `NOT CODED` record gains the line. No grader attributes it to anything and it is not
counted as an orphan, because the step-4 blocks leave the pairing population.

A refused CPT code appears only in its `NOT CODED:` line and has no entry to carry the disclosure
the skill mandates elsewhere, so refusing the line would delete real information with nowhere to put
it. Pairing it to the `NOT CODED:` anchor was declined: no grader reads `CONFIDENCE` outside a
pediatric band, so it buys machinery for a line nothing grades. The exclusion also keeps ruling 5's
orphan count usable, since a count whose floor is *two, always* is one nobody reads.

### 13. A fresh one-case `icd10-cpt` run is the positive control

After the skill edits land, one case is run over an existing committed note and the output is
committed as it is.

Four rulings narrow a matcher, and a narrowing's characteristic failure is refusing correct input.
After this build the only committed `icd10-cpt` material is run-2, which these rulings establish is
divergent on four counts, so every other control would be synthetic. Five rulings **edit a skill**,
and a skill edit is only as good as what a run does with it; a synthetic control checks the graders
against material written by whoever wrote the graders. This repository has recorded four times that
real material catches parser bugs its fixtures do not — `block_scan`'s two, `threshold_sheet`'s gate
3, `reference_scan`'s author key, `voice_corpus`'s one-hop walk.

**If the fresh run itself diverges, that is a finding about the skill edits** — the rulings were
written but not clearly enough to follow — and it returns the skill edits for another pass. It is
not edited until it passes.

### 14. The filled-anchor block opens only on the strict delimited heading

`BLOCK_HEADING` requires the documented `--- … ---` form anchored at line start. The five prose
mentions stop opening the block, which costs nothing today. `case-04.md` and `case-08.md` report no
step-4 block, so block coverage reads 10 of 12, `case-08.md` gains three `marked-not-listed`, and
run-2 gains a fourth divergence class.

Tolerating the `###` prefix was declined on ruling 3's precedent taken consistently: it is the same
shape ruling 3 rejected, and taking it here after taking the narrow side there would make the rule
*narrow unless it costs findings*, which is not a rule. Coverage falling to 10 of 12 is the correct
outcome, because two worksheets wrote the heading in a form the skill does not document and a reader
should see it.

## What run-2 is

**Four divergence classes**, not the three #1104 implies: `case-03.md`'s invented marker, four
lines; `case-05.md`'s `NOT FOR ENTRY` tails, two lines, one of which also wraps; `case-06.md`'s
system-prefixed step-4 listings, three lines; `case-04.md` and `case-08.md`'s `###`-prefixed step-4
heading, two lines. `case-01.md`'s two `CONFIDENCE` lines inside `NOT CODED` records are not a
class, because ruling 12 makes them compliant.

After the build, run-2 exits `anchor_scan` 1 with five findings, `specificity_scan` 2 with nine
unpaired codes, `refusal_scan` 0.

**`CONTEXT.md` gains a term for it.** This repository has had no name for a committed run record
whose output departs from the skill as written, where a grader's finding is a correct verdict rather
than a defect, and four classes in one twelve-worksheet run is when it earns one.

## Corrections to the tracker

**#1104's comment of 2026-09-11 claims one ruling here settles #1066 as well. It does not.** Both
#1066 controls use a shape where the code label and its detail line are unrecognized, so there is no
recognized detail line for ruling 5's bound to bound and no orphan for its count to count. #1104's
row is label-unrecognized with a recognized detail line; #1066's is both unrecognized. After ruling
5 the second is exactly where it was, and #1066's rows for these modules are unchanged.

## Rejected options

- **run-2 as the referent.** It makes every row a matcher to widen, which is #1104's own must-not
  stated as a policy, and it hides the eleventh invented marker the way it hides this one.
- **Row by row with no referent.** It leaves nothing for the tenth row, which is how nine rows became
  one ticket.
- **Allowing a value to wrap, or a fixed phrase to carry a tail.** Continuation logic in three
  modules to accommodate two committed lines.
- **A separator vocabulary after `NOT FOR ENTRY`.** A closed set nobody has, and it still fails
  `case-05.md`'s second tail, so it does not buy the thing it costs for.
- **Blessing `ALSO PROPOSED ABOVE`.** Ruling a marker into the vocabulary on a premise the same run
  falsified.
- **Deleting the differential line for a code proposed above.** It removes the MDM documentation the
  block exists to hold.
- **Gating an orphaned detail line at exit 2.** It says the wrong thing about whose fault a
  divergence is.
- **Folding the exit-2 vocabulary into this ticket, for three modules or for thirteen.** The first is
  the clause in a migration ADR 0118 ruling 3 refused; the second turns a bug ticket into a family
  seam change.
- **Narrowing B18 to the one committed spelling.** Its blast radius is unmeasurable and falls on
  correct notes.
- **A negation vocabulary for `SOURCE`.** See ruling 9.
- **Keeping two copies of the worksheet grammar**, or giving one grader ownership of a grammar
  neither produces.
- **Withdrawing run-2's C5 verdict.** The rule was not reversed; the population was overstated.
- **A hand-authored compliant worksheet as the positive control.** A synthetic control wearing a
  fixture's clothes.
- **Tolerating a `###` prefix on the step-4 heading.** Ruling 3's rejected shape, one block over.

## What this does not reach

**Whether run-2's four divergence classes mean the skill under-specifies.** Three of the four are
formatting choices a careful run made deliberately, and one of them came with a written rationale.
That is a reading about the skill's clarity, and ruling 13's fresh run is the measurement that would
inform it rather than a substitute for it.

**Whether any worksheet's codes are right.** Every ruling here is about what a line *is*, never about
whether the code on it fits the encounter. `fixtures/filled-anchor/run-2/README.md` already records
that C1 through C4 were not re-run and that its descriptors are checked against the release by
nothing.
