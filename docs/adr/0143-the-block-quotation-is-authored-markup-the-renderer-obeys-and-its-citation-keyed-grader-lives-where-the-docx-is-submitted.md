# The block quotation is authored markup the renderer obeys and its citation-keyed grader lives where the docx is submitted

[#815](https://github.com/mshamblin5150-code/clinical-skills/issues/815) was filed after a live
`discussion-post` run on 2026-09-02. The clinician added a 66-word quotation from a translation of
the *Meditations* to his draft; the orchestrating context found that `tools/docx_write.py` has no
block-quotation form, **trimmed the quotation to 33 words so it would fall under APA's 40-word
threshold**, and reported that as an APA decision. It was APA-compatible and it was not
APA-driven. A tool limitation edited the author's writing and the write-up presented the workaround
as the reason rather than the symptom.

Grilled 2026-09-06. **Seven decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## What was measured before ruling, at `76b8786`

Freshness gate `FRESH` at the read. Every figure below was re-derived at that commit.

**`skills/_shared/reference/apa7.md` contains the word `quotation` zero times.** The sheet this
repository says owns the APA rules states no block-quotation rule at all, in any of its thirty
sections. So #815 is a gap in the sheet before it is a gap in the renderer, and that ordering is
mechanical rather than rhetorical: every `docx_write.NOT_APPLIED` row is bound in both directions to
a row of that sheet's section 6, so nothing can be declared in code until the rule exists in prose.

**The current render is wrong in the opposite direction rather than merely absent.** A `> ` line
matches none of `blocks`' four patterns, falls through to `Block("paragraph", ...)`, and `esc` turns
the marker into a literal `&gt;`. The paragraph it lands in takes `w:ind w:firstLine="720"` — a
**first-line** indent of half an inch, where APA asks for a **left** indent of half an inch and no
first-line indent. A skimming reader sees something that looks deliberately formatted.

**`para` cannot emit the shape today.** Its indent surface is two mutually exclusive limbs,
`if first_line: ... elif indent: ...`, and `w:hanging` is unreachable from it entirely. The
`Reference` style in `word/styles.xml` is the template the shape wants: a named `pStyle` carrying
the indent, selected by loop state.

**`> ` collides with nothing on a render path.** Thirty-two tracked lines across seven skill and
reference files begin `> `, and every one is a display device wrapping a worked example —
`style.md` wraps its examples so a reader can see where they start, and a run copies the content
inside rather than the marker.

**The obvious grading row is falsified by the repository's own style sheet.** `style.md` section 7
publishes the Patient Education worked example as a quoted span of **56 words**. It is the
clinician's own scripted speech to a patient, it is the most distinctive voice in a case study, and
APA emphatically does not want it set as a block quotation. `case_study_scan` is already run over
the shapes `style.md` publishes, so a row reading *a quoted span of 40 or more words that carries no
marker* would go red against the sheet that defines it.

**Fifty citations key on an `apa7` section number and every one lands in sections 1 through 8.**
Sections 9 through 30 are cited by nothing.

**The paste target discards the property this feature depends on.**
[ADR 0013](0013-the-paste-target-keeps-tags-and-the-renderer-carries-formatting-directly.md)
measured Word to clipboard to Canvas at one institution: the sanitizer keeps **tags only**, and
every `style` attribute, every `class` attribute and the whole `<style>` block are discarded.
`NOT_APPLIED`'s `unreachable in the box` row already records centering and the hanging indent as
gone *by any tool from any source*.

**There is not one block quotation anywhere in the committed tree.** No fixture is a case study and
every finished draft lives under `output/`, which nothing committed re-derives.

**APA's own pages could not be opened.** `curl` and `WebFetch` both return HTTP 200 with a
1,033-byte Imperva challenge page on every `apastyle.apa.org` URL tried. The rule text below was
read through a search index of those pages rather than from a page anybody opened, and ruling 5
carries what that costs.

## Ruling 1 — the renderer obeys the marker and never counts words

A `> ` prefixed line renders as a body paragraph with a 0.5 inch left indent and no first-line
indent, with the marker consumed. The renderer does not find quotations, does not count their words,
and does not restyle one the author wrote inline.

**Detecting the threshold was refused although it is the cheaper design.** It would make the marker
question, the collision question and the grading row all vanish. It is also the act this ticket was
filed over, one layer down and running on every render forever: a tool deciding it knows better than
the author's text and changing it without saying so. It would strip quotation marks the author typed
out of a submitted document on a false positive with nobody watching.

**The posture is already ratified rather than invented here.** `NOT_APPLIED`'s `alphabetized` row
says sorting a reference list is *an edit to the document rather than a format applied to it, and
this renderer changes no word it is handed*. Counting words to restyle a quotation is that act
exactly.

## Ruling 2 — each `> ` line is its own paragraph, and consecutive lines are not joined

The ticket body asks that consecutive `> ` lines form one block. They do not.

**`NOT_APPLIED`'s `one paragraph` row already refuses the join**, in the reference list, on the
ground that *joining them is an edit on the same terms as sorting*. Nothing distinguishes a
hard-wrapped quotation from a hard-wrapped reference entry, so the renderer's line-is-a-paragraph
contract is unchanged here.

**What it costs is named rather than discovered.** A quotation hard-wrapped across four `> ` lines
renders as four Word paragraphs breaking where the author's file broke rather than where the page
margin is. Written as one long line it is correct. The reference-list case pushes that defect to
`reference_scan` and to `skills/practicum-case-study/SKILL.md` step 7, and **this case has no
equivalent catcher** — that is a real asymmetry with the row it inherits from, and it is accepted
rather than absorbed.

**It makes APA's nested-paragraph indent unimplementable rather than merely unimplemented.** With
every line already a paragraph there is no signal saying which ones open a new paragraph within one
quotation, so the additional 0.5 inch first-line indent APA gives the second and later paragraphs
of a block quotation has nothing to key on. It becomes a declared row, and the reason it is declared
is this ruling rather than a judgment that the rule does not matter.

## Ruling 3 — the unmarked long quotation is graded on the span plus its citation, in `case_study_scan`

Ruling 1 leaves a hole: a 60-word quotation the author wrote inline is an APA defect that every
command exits 0 over. A row closes it, and the row is keyed on **a quoted span of 40 or more words,
in a paragraph that also carries an in-text citation, with no `> ` marker**.

**The citation is the discriminator and it was measured rather than reasoned to.** The naive form of
the row fires on `style.md` section 7's 56-word patient-education script. A quotation from a source
carries a citation and APA requires a locator in it; scripted speech to a patient carries none and
never will. Without the discriminator the row is
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s and
[#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275)' defect again — a rule that
fires on a correct document.

**Declaring the gap and grading nothing was refused** on
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s ground, *what a written
instruction cannot do is fail*.

**It may not land in `reference_scan`.** That is the one grader in `tools/` whose `--show` output
the clinician ruled safe to paste, and the ruling rests on a measured property: every finding detail
it can emit is a reference entry, a heading, a date, or a citation key. A finding carrying forty
words of the draft's prose breaks that bound, in the module where pasteability is load-bearing.
`case_study_scan` is the home because its `--show` is already PHI *for the reason that makes it
correct here* — a finding's text is the draft's own text.

**What the row cannot reach is declared.** A narrative citation preceding the quotation —
*Aurelius (2002) wrote, "..."* — puts the citation outside the shape the row keys on. That is a
declared limit, not a hidden one.

## Ruling 4 — the case study only, and the paste path declares the rule unreachable

The row lands in `case_study_scan` and not in `discussion_post_scan`.

**The two artifacts are not the same case, and the ticket's own origin obscures it.** The run that
filed #815 was a `discussion-post` run, and that is the one path where a block quotation cannot
reach the page. `skills/discussion-post/SKILL.md` step 7 renders the `.docx` as a **paste vehicle**
and step 8 pastes from Word into the LMS; `skills/practicum-case-study/SKILL.md` step 8 renders the
file that **is submitted**.

**On the paste path, obeying the rule produces the worse page.** ADR 0013's measurement is that
every `style` attribute is discarded, and an indent is a `style` attribute — so a correctly marked
block quotation arrives in the box with its indent gone *and* its quotation marks removed by APA,
reading as ordinary prose that no longer looks like a quotation. The unmarked inline form keeps its
quotation marks and reads correctly. **That does not excuse the 33-word trim**, which edited the
author's writing and reported the workaround as the reason; it means the outcome that shipped was
defensible on that path for a reason nobody had stated.

**So `discussion_post_scan.DECLARED_LIMITS` gains the limit** — the block-quotation form is
unreachable in the box, so a clean post scan is not a claim that the post's quotations are
APA-formatted — and `skills/discussion-post/SKILL.md` tells an author not to write `> ` in a post
draft, because the renderer strips the marker and APA strips the quotation marks while the paste
strips the indent, leaving the author worse off than doing nothing.

**One thing is derived from a measured mechanism rather than measured directly, and it is stated
rather than buried.** ADR 0013 measured that the sanitizer discards `style` attributes wholesale and
measured centering and the hanging indent by name. **Nobody has pasted a left-indented paragraph
into that box.** The derivation follows from the mechanism, which is stronger than reasoning about
Canvas, and it is one paste away from being a measurement.

## Ruling 5 — `apa7.md` gains a real section, inserted as section 30, covering the block form and its locators

**A table cell in section 6 is not enough.** Section 7's standing claim is that *this sheet owns the
rules and that command is a second reader of it, never a second copy*, so the row ruled in ruling 3
needs a passage to read from. Section 6 is renderer-scoped and states what `docx_write` does, not
what an author must write.

**It inserts as section 30 and the reference-example index moves to section 31.** Fifty citations
key on an `apa7` section number and all fifty land in sections 1 through 8, so this is the one
insertion point in the sheet where the number that moves is cited nowhere. Inserting near sections 1
through 7 instead would silently re-point twenty-five citations with nothing failing, which is what
[ADR 0129](0129-the-apa-form-heading-declares-itself-and-its-tail-is-exact.md) warns about. The
form-section run keeps sections 8 through 29 and its heading grammar is untouched.

**The section covers the locators as well as the form**, on the clinician's instruction of
2026-09-06, because the case he actually hits is a long quotation from a book:

- The threshold, the indent, the absence of quotation marks, the double spacing, and both permitted
  citation placements.
- The locator rules: a page number in every direct quotation, `p.` for one page and `pp.` for a
  span, a comma between discontinuous pages.
- Works without page numbers: a heading or section name, a paragraph number counted by hand, or a
  timestamp for audiovisual material.
- Ancient Greek and Roman works and classical religious works: **no reference list entry is
  required**, the first citation names the version used, the locator is the canonically numbered
  part rather than a page, and a translation carries both years earliest first and slashed.

**The provenance line may not claim a read nobody performed.** The sheet's sections 1 through 7 say
*verified against apastyle.apa.org on 2026-08-18* and section 8 onward carry per-section provenance.
Every `apastyle.apa.org` fetch attempted during this grilling was stopped by an Imperva challenge,
so the wording above was read through a search index. **Opening those pages in a browser and
capturing the wording with a read date is a build prerequisite**, and it is why #815 is `blocked`
rather than `ready-for-agent`. ADR 0129 ruling 6 exists precisely to stop a later session inventing
a read date for a read nobody performed.

## Ruling 6 — citation placement is declared rather than graded

APA moves the parenthetical by form: inside the sentence for an inline quotation, after the final
punctuation and carrying none of its own for a block quotation. Nothing grades that.

**The reason is a measurement and not a preference.** There is not one block quotation anywhere in
the committed tree, so a placement rule would be written against zero real examples and tuned
against none. That is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s ruling exactly: ground a
cut point where the corpus offers one and refuse to invent one where it does not. A rule would also
have to survive a quotation ending in a question mark, a `para.` locator, and a narrative citation
preceding the quote.

Ruling 3's row already moves an author into the block form; once they are in it the citation is one
line a reader can see. It goes to `case_study_scan.DECLARED_LIMITS` and to the new sheet section.

## Ruling 7 — the classical-work collision is filed rather than fixed here

Writing ruling 5's classical-work rule into the sheet exposes a live defect in a shipped grader.
`reference_scan`'s `UNLISTED_CITATION` row grades `apa7` section 5, every in-text citation is listed
in the reference list; APA says a correctly cited ancient work **has no reference list entry**. So a
correctly quoted classical work fires that row on a correct document. It is live today and has
nothing to do with the renderer, and it has been invisible only because nobody has cited one in a
graded draft.

**A carve-out inside this build was refused on three grounds.** #815 is a renderer ticket and the
carve-out reaches into a grader with sixteen rows whose pasteable `--show` rests on measured
properties. Recognizing a classical work mechanically is not obvious — a slashed year with `ca.` is
a signal, a classical religious work is not — and it needs its own grilling. And **the two failure
directions are not symmetric**: the live bug is a false alarm on a correct document, which a reader
sees and dismisses, while a hasty carve-out is a false pass, which nobody sees.

## Derived rather than ruled

**The marker is `> `.** Nothing on a render path writes one meaning anything else. One cost travels
with it: today a run that copies a `style.md` worked example *including* its `> ` wrapper gets
visible debris on the page, and after this it gets a silent half-inch indent instead. That is a
mistake becoming invisible, and it is the price of the obvious marker.

**A new `Block.kind` reaches two scanners, and one of them changes verdict.**
`reference_scan.read_document` builds every post-heading block into an `Entry` with
`paragraph=block.kind == "paragraph"`, so a `> ` line below the References heading would fail
`ENTRY_NOT_A_PARAGRAPH`. That is arguably the right answer — a block quotation is not a reference
entry — but it is
[ADR 0084](0084-an-own-line-html-comment-is-markup-and-the-renderer-drops-it.md)'s
comment-in-the-reference-list finding one row over, and it is named here rather than discovered by
whoever writes the first draft that trips it. `case_study_scan.read_sections` appends the new kind
to the open section as content, which is correct and needs nothing.

**Every new `apa7.md` section 6 row costs a calibration identity and a dated Word record.** That
section closes with *a new row fails until it gains both*, and
`skills/_shared/reference/word-renderer-calibration.json` is where the identity lives. The applied
form takes a row; each declined part takes its own, because `NOT_APPLIED` rows bind one-to-one by a
distinctive phrase. The probe is `python tools/docx_word_probe.py --word`, maintainer-only and never
on the consumer or CI path, per
[ADR 0008](0008-word-is-a-one-time-calibration-instrument.md).

**`case_study_scan`'s new row needs a sentence in `skills/practicum-case-study/SKILL.md` step 9.**
`ROW_PHRASES` in `tools/test_case_study_scan.py` is keyed on the module's own tuple and asserts each
row has one, so the row cannot arrive as a rule only the scanner knows. No `checks_ledger` row moves
— that ledger already expects `the house style`, and a row inside `case_study_scan` is not a new
reader.

**`skills/discussion-reply/SKILL.md` is untouched.** A reply pastes from Markdown directly and
renders no `.docx`, so a `> ` in a reply draft reaches the board as a literal marker and this build
changes nothing about it.

## What this record does not settle

**Whether the left indent survives the Canvas paste.** Ruling 4 derives it from ADR 0013's measured
mechanism. One paste settles it, and nobody has performed one.

**How a scanner recognizes a classical work.** Ruling 7 files it. The question is open and the
answer is not obvious.

**Whether a rendered block quotation is a correct one.** The row ruled in ruling 3 establishes that
a long quotation carrying a citation was marked. It says nothing about whether the quoted words match
the source, whether the locator is right, or whether the quotation should have been a paraphrase.
**A clean scan is not a checked quotation**, and the report says so.

**Whether the author should have quoted at all.** APA's own guidance on appropriate level of citation
is outside every row here and stays a reading.
