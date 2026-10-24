# A course assignment reaches Gate 1 only after an element coverage read

**Measured at:** 63d7137cdfaf50836bbf3f02d5b6d8b44663fbad

[#2037](https://github.com/mshamblin5150-code/clinical-skills/issues/2037) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M6), 2026-10-23. The DOCX draft left out
two elements that the faculty clinical-hours document required. Nothing was asked to catch that: the
gap surfaced only as an out-of-scope remark in a heading read. After submission, the paper was read
against the course rubric at the clinician's request, and descriptors it covered thinly or not at
all were visible only then. Grilled 2026-10-24 against `main` at the commit above, where the
freshness gate read `FRESH`; the clinician ruled every point below. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**No `course-assignment` reader is asked whether each required element is answered.** The skill's
readers are the visual read, the deck's presentation-intent and adversarial reads, the heading read,
and the voice read. The heading read is deliberately given no research sources, so it cannot compare
a draft with the faculty material.

**`practicum-case-study` already carries the shape.** Its check table has a row named `the faculty's
own to-do list`: a reader receives the faculty material, the draft's headings and, on a routed run,
`bar.md`, and confirms that every faculty item has a section answering it. That row is not in
`checks_ledger.SUBSTANTIATED_CLEAN`, so a bare `clean` passes it, and it has no copied rubric to read.

**ADR 0355 ruling 1 already declined one form of this.** It refused a structured required-elements
field in `bar.md`, because a list the drafting agent transcribes grades only what that agent noticed.
An element it missed escapes the check the same way it escaped the draft.

**No snapshot holds the rubric.** Step 1 tells a run to read the rubric, but only the assignment
page's wording is written to `assignment-<date>.md`. The NUR 5042 M5, M6, M11 and M12 snapshots were
counted for rubric criteria, rating descriptors and table rows; all four have none. The M6 rubric
gap was therefore not a reading failure. The rubric was never on disk for any reader to be given.

## Ruling 1 — a fresh reader lists the required elements from the original documents

Before Gate 1, a fresh **Second reader** under standing rule 6 receives the captured assignment
page, every linked faculty document retained under the LMS attachments route, the copied rubric
(ruling 5), the signed `bar.md`, and the built artifact. It writes its own list of required elements
from those documents and maps each element to the paragraph, caption, figure note, slide bullet, or
speaker-note sentence that answers it. It writes a record, and the grader refuses Gate 1 without a
current one.

Widening the heading read was declined: that reader is source-blind by design and is shared by five
coursework skills, so handing it the faculty documents would mix two jobs and change a contract the
other four rely on. A signed required-elements field was declined on ADR 0355 ruling 1's ground.
Changing nothing was declined because the M6 omission stays possible on every run.

## Ruling 2 — an element answered nowhere is a finding; a thin answer is a remark

An element with no answering place is a finding and refuses Gate 1, whether it came from the
prompt, a faculty document, or a rubric full-credit descriptor. An element answered thinly is a
`REMARK:` line and never changes the verdict.

The ticket's own split, under which every rubric descriptor was only a remark, was declined: a
full-credit descriptor answered nowhere loses points as surely as a missing prompt element, and the
M6 paper had descriptors covered not at all. Refusing on thin coverage was declined because
thinness is the reader's judgment, and a refusal resting on judgment gets learned around. Making
everything a remark was declined because it fails the ticket's own done-when line.

## Ruling 3 — a deliberate omission is cleared only by the signed bar

An element the clinician agrees to leave out is recorded in `bar.md` and signed, through ADR 0355
ruling 1's omission route and ruling 5's changed-line re-signing. The coverage reader marks that
element `omitted` and quotes the bar line; the grader confirms the quoted text is in the latest
signed bar. The grader proves the line exists, never that it concerns this element; that join is
the reader's.

Approving over a missing element at Gate 1 was declined because it undoes ruling 2: the run would
reach the ask with a known gap. Having no omission route was declined because an element that does
not apply, or that the producer cannot make, would be padded or would stall the run.

## Ruling 4 — the drafting agent's list is reconciled by the reader

Before drafting, the drafting agent writes its own list of required elements to `elements.md`, one
identified item per element. The coverage reader builds its list without seeing that file, then
receives it and accounts for every item, mapping it to one of its own elements or adding it. The
grader refuses a record that does not account for every `elements.md` item identifier.

Two lists drawn from the same documents by different readers expose an element either one missed.
They do not expose one both missed, and the record says so rather than claiming completeness.
Comparing the two lists by command was declined: matching free text either misfires on paraphrase or
loosens until it matches anything, so the comparison is a reading and the grader checks only the
identifiers. Relying on the reader's list alone was declined because its list is then its own
unchecked denominator.

## Ruling 5 — the rubric is copied and its points must sum

Step 1 copies the rubric verbatim into its own fixed-shape run file, one row per criterion carrying
the criterion, its full-credit descriptor, and its points, or writes one explicit line stating that
the assignment has no rubric. The grader checks that the rows' points sum to the assignment's point
value and refuses a coverage record that does not account for every rubric row. A rubric whose
points legitimately do not sum to that value, such as one with an unscored criterion, needs a stated
exception; the build defines its form.

The sum is the one check here that does not depend on whoever did the copying: a dropped row leaves
the total short. Copying the rubric as prose into the existing snapshot was declined because the
descriptor count would again come only from a reader. Leaving the capture unchanged was declined
because the coverage reader would never be given the rubric.

## Ruling 6 — Gate 1 shows counts, thin remarks and omissions

The record reaches the clinician through the existing
[reader remarks at the go-ahead](../../skills/_shared/reference/sourcing.md#reader-remarks-at-the-go-ahead)
route: one coverage line giving the elements listed, answered, and omitted per the signed bar; each
thin-coverage remark as a numbered remark with a proposed outcome; and each omitted element named on
one line. The full element-to-location map stays in the run file and is shown on request.

Showing the full map at Gate 1 was declined because most of its rows read as answered, and a long
list skimmed at the moment of decision is where real items get missed. Showing nothing beyond the
grade was declined because thin rubric coverage would again reach the clinician only after
submission.

## Ruling 7 — the read comes first and is bound to the artifact fingerprint

The coverage read is the first reader taken on the built artifact, before the render and its
visual read, the heading read, and the voice read. Its record carries the artifact's SHA-256; the
grader refuses a record whose digest no longer matches, so any later change to the file, including
a layout-only repair, takes a new coverage read. That is the rule the heading read already follows.

Placing it last was declined because a missing element found there forces every earlier read to be
retaken. Reading the draft text without a fingerprint was declined because a later repair could
remove the paragraph that answered an element without anything noticing.

## Ruling 8 — deck and DOCX alike

Rulings 1 through 7 apply to both branches. Locations use the heading read's vocabulary: slide
bullets and speaker-note sentences for a deck; body paragraphs, captions, and figure notes for a
DOCX. Both branch graders enforce the record through `course_assignment_scan.py`. A run approved
before the check starts reports `not graded` through `reference/completion-check-starts.tsv`.

Limiting the read to DOCX was declined: a deck missing a rubric row loses points as a paper does,
and the deck's presentation-intent reader grades against the signed audience purpose and talk style,
not against the prompt's required elements.

## Ruling 9 — course-assignment only; the siblings are a separate ticket

This record governs `course-assignment` alone. Whether `practicum-case-study` and `discussion-post`
adopt the same read is filed as a separate ticket carrying `grilling`, which names `peer-critique`
and `discussion-reply` as probably outside it because each answers one classmate's post rather than
a faculty assignment. This follows ADR 0355 ruling 4's handling of the same choice.

Applying the read to every coursework skill now was declined: five skills with different bar
grammars and record shapes, on the evidence of one Word paper. Filing nothing was declined because
the case study's weaker row would then live only in this session.

## Done when

- `course-assignment` step 1 writes the rubric file or its no-rubric line, and the grader refuses a
  rubric whose points do not sum to the assignment's value without the stated exception.
- The drafting agent writes `elements.md` before drafting.
- A course-assignment run cannot reach Gate 1 without a current coverage record bound to the
  artifact's SHA-256 and accounting for every rubric row and every `elements.md` item.
- A planted draft missing one required element is refused; the same draft with that element's
  omission recorded in a signed bar line passes; and an omission quoting text absent from the
  signed bar is refused.
- A thin-coverage remark reaches Gate 1 through the reader-remarks route without changing the
  verdict.
- Both the deck and DOCX graders enforce the record.
