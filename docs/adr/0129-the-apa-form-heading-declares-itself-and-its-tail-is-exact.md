# The apa form heading declares itself and its tail is exact

[#804](https://github.com/mshamblin5150-code/clinical-skills/issues/804) found that
`TheNursingSourceClassTableIsBoundToTheSheet.assert_form_headings_bind` cannot represent APA's
published vocabulary. It filters `##` headings by the substring `reference form` or
`reference entries`, then requires the raw heading to contain exactly one
`APA_SOURCE_CLASSES.name` substring. A heading containing `Journal article with an article number`
necessarily also contains `Journal article`, so `len(names) == 1` is false and the bind fails on a
correct heading.

The state is latent only because both nested pairs currently carry `has_form` false.
[#757](https://github.com/mshamblin5150-code/clinical-skills/issues/757) flips every class to true,
so this blocks it. #757's own body forbids widening the mechanism inside that build and sends the
finding here, which is why this record exists rather than a repair inside #757.

## Measured before ruling, at `1730f7a`

Freshness gate `FRESH` at the read. Every figure below was re-derived at that commit.

**The two nested pairs are the whole collision set.** `Journal article` is inside
`Journal article with an article number`; `Medical dictionary` is inside
`Entry in a medical dictionary` under the casefolded comparison. Nothing else in the twenty-three
contains anything else. The two clinical practice guideline names share twenty-eight characters of
prefix and neither contains the other, so they are not a third case.

**Nothing outside the test reads a heading's text.** Every citation into this sheet across
`tools/`, `skills/` and `docs/adr/` is by section *number*. Heading prose is free to change.

**The vocabulary is punctuation-poor.** All twenty-three names are pure ASCII, none carries an
apostrophe or a quote, and the only punctuation anywhere in the set is `(`, `)` and one comma. The
drift that normally motivates a normalized comparison cannot occur here.

**`checks_ledger.normalize` maps the twenty-three to twenty-three distinct keys**, so a normalized
comparison was available and was declined on the ground in ruling 3 rather than on a collision.

**Two properties of the existing bind that are not the reported defect.** Its final assertion
compares `classes_claiming_a_form` against a **set** of matched names, so two headings naming one
class pass — inert at two form sections and live at twenty-three. And `ApaSourceClass.item` is
positional, asserted as `enumerate(EXPECTED_CLASSES, 1)`, so a bind keyed on the item number would
pass while two names were swapped.

**Sixty-two citations key on an `apa7` section number**, across eighteen files including
`reference_scan.py`, `skills/practicum-case-study/SKILL.md`, `style.md`, `docx_write.py`, six test
modules and four ratified records. No test binds a section number to that section's content.

## Ruled 2026-09-04

### 1. The identity is a canonical heading grammar rather than a substring search

A form section's heading is `## <n>. Reference form: <class name>`. The marker bounds the name on
the left and end-of-line bounds it on the right, so the nested pairs cannot collide: the comparison
is equality on the delimited tail and has no reach past either delimiter.

**Three alternatives were priced and declined.** A repaired containment rule — matches must form a
containment chain, take the longest — keeps the headings as they are and is roughly five lines, but
it remains a substring test, and this repository's recorded failures are a run of them:
`spelling_scan`'s mention-versus-use, `differential_scan`'s
[#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153),
`test_run_record_claim`'s hard-wrapped grep, `phi_scan`'s two self-exempting files. A bind on the
item number carried in each section's provenance line reuses a fact #757 mandates anyway, but that
key is positional and would pass across a rename. Declaring each heading string in full is exact
and puts twenty-three heading strings into Python, where every prose tweak becomes a code edit.

**The grammar is exact and intrinsic at once**, which is the pair no other candidate holds. Ending
with the class name would not have been enough: `Entry in a medical dictionary` ends with
`medical dictionary` casefolded, so a suffix rule collides on the second pair. The left delimiter
is what does the work.

### 2. The marker detects, and the tail is an obligation rather than a qualification

Carrying `Reference form: ` is what makes a heading a form heading. A heading carrying the marker
whose tail names no class in the table **fails**.

The alternative — qualify a heading only when its tail already matches a class — is a cleaner parse
with no error state, and it is the way to land a section without joining the table. A misspelled or
renamed class would drop out of the population in silence and the class it was written for would
read as having no section.
[ADR 0097](0097-the-apa-sheet-s-class-vocabulary-is-apa-s-nursing-set-and-coverage-is-decided-per-bucket-while-the-gate-is-a-bind-test.md)
ruling 6 already requires that a section landing without joining the table fails, and that is the
option which quietly removes it.

**This retires a second unruled substring test in the same function.** `"reference form" in
heading` was the detector; the marker replaces it, so the sheet has one rule where it had two and
the surviving one is exact.

### 3. The tail is compared raw, and the departure from `checks_ledger` is deliberate

Equality on the stripped tail against `ApaSourceClass.name`. No case folding, no punctuation
folding.

The house precedent for a marker-plus-payload heading is `checks_ledger`'s `## CHECK: <name>`,
whose declaration comment states the anti-nesting rule this record reaches independently — *a
prefix test would read either one as satisfying both* — and which then compares on a normalized
string. **This record follows its structure and declines its comparison**, because the two payloads
are different kinds of thing.

`checks_ledger`'s tail is a **description** an agent writes under time pressure, where punctuation
carries no meaning. This tail is a **published vocabulary term**, already declared byte-exact in
`APA_SOURCE_CLASSES` and already asserted byte-exact by
`test_the_table_is_the_published_nursing_source_class_vocabulary`. The sheet is where a human reads
that vocabulary, so a heading permitted to spell it differently is a second spelling of one
published term, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
one artifact over.

Normalization absorbs drift that does not matter. In a set with no apostrophes and no non-ASCII,
every drift available is a drift in APA's own name, and that is the thing worth failing on. The
failure is a one-character edit against an expected string the assertion prints.

### 4. The control is synthetic, and it carries a tripwire against its own vacuity

Under ruling 1 the reported defect is **structurally impossible**, because equality has no reach
past the delimiters. That is the condition under which this repository has repeatedly shipped a
regression test that passes for the wrong reason.

It is also dormant against the committed sheet. The control can only fire on a sheet carrying
headings for both members of a nested pair, and `apa7.md` carries neither, which is #804's own
closing line.

**So three things run.** A **synthetic** sheet built in the test file, carrying both members of a
nested pair and asserting they resolve to two different classes — red the moment anyone reinstates
containment, and red today rather than after #757. The **committed** sheet's bind, for the state.
And `checks_ledger`'s tripwire: assert that a nested pair still exists in `APA_SOURCE_CLASSES`
before using one.

**The tripwire is the half that schedules its own review.** #757 checks three inherited claims
about APA's page at the read, none of them re-derived here. If that read returns names which no
longer nest, this grammar's whole justification has evaporated and the suite says so rather than
standing green over a ruling nobody rereads. `differential_scan`'s row-1 tripwire is the recorded
precedent for a declared limit firing in its own words.

`test_an_unknown_form_heading_breaks_the_bind` is retired by ruling 2 and replaced. Its mutant,
`## 24. Unknown reference form`, carries no marker under the new grammar, so it is no longer a form
heading and the bind passes — the control goes vacuous. The replacement is a heading with a good
marker and an unknown tail, which fails **inside** the population rather than outside it.

### 5. The sheet states its own grammar, bound to section 7's span

The marker is a module constant. `apa7.md` section 7 states the grammar in prose and carries the
marker string **literally**, because an author writing twenty-one more headings needs to copy it.

This is the one place the sheet departs from its own point-at-the-object habit, and the bind is
what pays for it: the assertion is scoped to section 7's **bracketed span**, not to the file. An
`assertIn` over the whole sheet would be satisfied by the form headings themselves and would prove
nothing about the prose. `test_reference_scan.py:1224` already brackets that section, and its
docstring records that the earlier open-ended slice was a latent widening caught by review.

**The usual argument runs the other way and does not apply.** *What a written instruction cannot do
is fail* is an argument against prose standing alone; here the gate exists and the prose is what
makes the rule followable. The live failure is the inverse — an unwritten rule cannot be followed,
and the author who must follow it twenty-one times has the sheet open rather than the test.

### 6. Section 2 declares why it carries no provenance line

After #757, twenty-two of twenty-three form sections open with a provenance line naming the page,
the item and the read date. Section 2 will not, because its form was read off the *Publication
Manual* rather than off that page, and its new heading now claims the class while only its body
says where the form came from.

One declared sentence, in the section. The failure it forecloses is specific: a later session sees
twenty-two provenance lines and one gap, reads it as an oversight, and **invents a read date for a
read nobody performed** — which is what ADR 0097 ruling 9 refuses when it forbids hoisting the
line. *An absent guard is easy to read as an oversight when it is a choice.*

## Derived rather than ruled

**#757 appends its sections and does not interleave them.** The bind ignores the heading's leading
number, which is what makes appending safe. Sixty-two citations key on a section number and nothing
binds a number to its content, so inserting sections in APA item order re-points every one of them
and **nothing fails**. This follows from ruling 1 and needed no separate decision; it is recorded on
#757 and in its body.

**The class table is untouched.** Section 2 and section 8 already carry `has_form`, so this build
changes `reference_scan.py`'s constant and parser, `test_reference_scan.py`'s bind and controls, and
three parts of `apa7.md`. No column moves.

**This record refines ADR 0097 ruling 6 and does not supersede it.** That ruling's *the class
table's `has_form` column is bound to the sheet's own `##` headings in both directions* stays true
in every word. What is settled here is how a heading names a class, which ruling 6 left open.

**Section 8 loses `Legal reference entries` from its heading and keeps the signal.** Nothing binds
that string; `skills/discussion-post/SKILL.md` links the sheet without citing the section by number;
the section's body still requires the legal source name; and `reference_scan.py:106`'s
`*Legal reference entries, section 8:*` is a docstring paraphrase that survives the rewrite.

## What this record does not settle

**Whether the bucket state machine survives its own success.** With every class carrying a form,
`COVERAGE_FINDING` becomes unreachable: `statpearls`, `cochrane` and `identified-media` all move
from `finding` to `clean`, only `clean` and `undecidable` remain reachable, ADR 0097 ruling 6's
`uncovered-class` row never fires again, and `CONTEXT.md` names a third state nothing can produce.
That is the goal state rather than a defect, and nobody has ruled what the row and the third state
become once it is reached. It is filed rather than answered here, because #804's scope forbids
widening and because an open decision is a question rather than a comment.

**The three inherited claims about APA's page.** That it carries twenty-three items, that StatPearls
is among them and takes a required retrieval date, and which classes take none. ADR 0097 declared
them unre-derived and #757 checks them at the read. Nothing here re-derives one, and ruling 4's
tripwire is what makes a change to them visible instead of silent.

**Whether a section's content is right.** The grammar binds a heading to a class name. It says
nothing about whether the form beneath the heading is APA's form, and ADR 0097's limit stands
unchanged: a synthesized example that has drifted from APA's slot order looks exactly like one that
has not.

**Whether a heading's leading number is correct.** The bind ignores it entirely, which is what
buys the append property above and is also the reason nothing here can catch a misnumbered section.
