# An own-line HTML comment is markup and the renderer drops it

[#673](https://github.com/mshamblin5150-code/clinical-skills/issues/673) was filed after a live
`discussion-post` run against NUR_5042 M3 put three `INVOKED` working comments on a graded page —
eleven lines across pages 1 and 2 of a three-page submission, one of them split across the page
boundary. `docx_write` had no rule for an HTML comment, so `blocks` handed the line through as an
ordinary paragraph and `body_xml` wrote it as visible text. Every command in the toolchain exited 0;
the only thing that caught it was a vision-capable reader looking at the pages.

Grilled 2026-08-30. **Nine decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `0d26b95`

Freshness gate `FRESH` at both checkpoints. `main` moved from `7a4b5fc` to `0d26b95` during the
session and **every measurement below was re-derived at the fresh base**, which is how the ninth
decision came to exist at all.

**The defect is live at `HEAD` and it is not visibly foreign.** `body_xml` emits the comment as an
escaped text run, and the branch it falls to is the ordinary paragraph branch — so it takes APA's
0.5 inch first-line indent and renders as an indented body paragraph rather than as something a
skimming reader would read as debris.

**`blocks` has three production consumers, not the two the ticket names.** `render_body`,
`case_study_scan.py:488`, and `reference_scan.py:793`. The third is the one that moves decision 1:
`read_document` turns every non-blank block after the References heading into an `Entry` and grades
it, so a comment written below `## References` is graded **as a malformed APA reference** today — a
false finding one draft away, in the scanner whose whole subject is the reference list.

**Nothing in `case_study_scan` reads a comment.** It parses as a `paragraph` block, `normalize` of
its text matches no `KNOWN_SECTIONS` key so it opens no section, and no finding keys on it. The
ticket's *the scanner stops seeing a shape that is in the file* is true and costs nothing findable.

**The workaround the live run shipped destroys visible prose.** Its pattern is
`(?m)^\s*<!--.*?-->\s*$\n?`, measured over four forms:

| source line | result |
| --- | --- |
| `<!-- INVOKED: a \| b -->` | dropped, as intended |
| `<!-- INVOKED: a \| b --> and the argument spends it here.` | unchanged, renders |
| `<!-- a --> the sentence a reader needs <!-- b -->` | **deleted entirely** |
| `<!-- INVOKED: a` … `\| b -->` across two lines | unchanged, renders |

Row 3 is the finding. Non-greedy backtracks to the **last** `-->` on the line, and the sentence
between the two comments goes with it. Silent content loss on a graded page is a worse defect than
the one being repaired, and it is the pattern the run that found #673 rendered its own submission
through. Row 4 says the multi-line form is *under-read* rather than partly read: it survives whole,
so no partial strip exists today to be preserved.

**Dropping the comment block alone leaves a double gap.** `render_body` emits one `<w:p/>` per blank
source line, so `para / blank / comment / blank / para` becomes two consecutive empty paragraphs. The
workaround did not have this problem only because its `re.sub` consumed the trailing newline and it
then collapsed `\n{3,}` back to `\n\n`.

**The renderer is the outlier, and the rest of the toolchain already treats these comments as
invisible.** `discussion_artifact.strip_discussion_markers` — *"Remove current and retired invisible
working annotations"* — keeps them out of the graded word count, and `discussion_reply_scan.py:255`
excludes an own-line comment from the reply body. `artifact_provenance` carries a full comment-span
walk, so a wider rule would be an adoption rather than an invention.

**The one live mid-line comment in the tree is not on a rendered path.**
`skills/practicum-case-study/reference/voice.md:183` carries
`<!-- voice-model-scan: invoked-source -->` welded into a numbered item, read by
`voice_model_scan.py:70`. Nothing renders that sheet.

## Ruled 2026-08-30

### 1. The strip lands in `docx_write.blocks`

Over `render_body` and over the skill.

`blocks` is the only home where the comment stops being a shape in **three** readings at once. It
keeps the identity `case_study_scan` has rested on since
[#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277) — *a line the scanner calls
a bullet is a `ListParagraph` in the document* — true, because both sides agree the comment is not a
block. And it closes the latent `reference_scan` false positive measured above, which
`render_body` leaves standing.

The skill was refused on
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s ground: promoting the
present workaround to an instruction is *what a written instruction cannot do is fail*, and it leaves
every other skill that renders holding the same hole.

### 2. The rule matches an own-line comment only, and the line must carry nothing but comments

The second half is not a refinement of the first, it is what stops the repair being worse than the
defect. *Opens with `<!--` and ends with `-->`* is the workaround's rule and it deletes row 3's
sentence. The predicate is that the line has no visible content outside its comments.

Mid-line and multi-line forms are declared rather than stripped. `docx_write`'s stated posture is
that it changes no word it is handed — `NOT_APPLIED`'s `alphabetized` and `one paragraph` rows both
refuse to edit an author's text and push the defect to a scanner instead. Removing a whole line of
markup removes no word from a paragraph; reaching inside a sentence does, and it would then have to
decide what happens to the whitespace left behind. The coverage it buys is against a form nobody
writes on this path.

**This is *declare the coverage rather than widen the instrument*** —
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s and
[#278](https://github.com/mshamblin5150-code/clinical-skills/issues/278)'s ruling arriving at a
renderer — and it is honest only because of decisions 4 and 5, which report and gate the residue. A
narrow rule with a silent remainder would be the partial read this repository's extractor-coverage
rule forbids.

### 3. The dropped line takes one adjacent blank with it

Over leaving the blanks, and over collapsing runs of blanks generally.

It is the narrowest rule that produces a correct page: `para / blank / comment / blank / para`
renders as `para / blank / para`. It changes the rendering of no document that carries no comment,
and its target is measured rather than invented — byte-for-byte the shape the live run already
shipped and the clinician already accepted.

**General blank collapsing was refused** as a change to the renderer's blank-line contract wearing a
comment fix as a disguise: a draft deliberately carrying two blank lines would silently gain one
paragraph less, in documents this ticket has nothing to do with.

### 4. The command states what it did and warns about what it left, and never refuses

Two limbs. stdout gains one line beside `wrote`, printed only when the count is non-zero, saying how
many comment lines the `.docx` does not carry. stderr warns when a form the rule does not cover will
be drawn on the page.

Both bounded to **a count and a fixed form name, never a line of the run's text**, on
[#280](https://github.com/mshamblin5150-code/clinical-skills/issues/280)'s reasoning and at its
width: this renderer does not branch on whether the draft it was handed is about a patient.

**Warn, never refuse** — #280's ruling, unchanged and for its reason. This command is on the
consumer's critical path and a blocked submission is a worse outcome than a comment on the page.

The stdout limb exists because the rule deletes lines from an author's file, and a renderer that
silently deletes content would be #673's own shape one layer down. It is not a warning on every clean
run: a case study drops nothing and prints nothing extra.

### 5. `discussion_post_scan --docx` gates the correspondence

The ticket's decision 3 says that if the strip lands in the renderer the question disappears. It does
not.

The rule ruled in decision 2 is deliberately narrow, so the residue it declares reaches the page with
nothing but a stderr warning from a command whose exit stays 0. And the gate reads the **artifact**
rather than the renderer: a `.docx` rendered from a checkout predating the fix, rendered by something
else, or hand-saved out of Word, all reach faculty the same way.

The precedent is one row over. `BOLD_HEADINGS` grades that no paragraph carries a named `Heading{N}`
style, which is exactly what `--bold-headings` guarantees — so this repository already accepts
grading the artifact for a property the renderer promises.

**The row keys on both delimiters**, `<!--` and `-->`, not the opener alone. A multi-line comment's
closing line renders carrying no opener at all, so an opener-only row would count one occurrence
where two lines are affected. Without `--docx` the row reports `not graded`, on `BOLD_HEADINGS`'
arrangement; with it, a hit is exit 1. Default output stays a count.

`_docx_heading_styles` already opens the archive and parses `word/document.xml`, so the row costs one
more pass over a tree already in memory.

### 6. The skill prose states the mechanism, and `discussion-reply` is deliberately untouched

Three `discussion-post` sentences go vacuous the moment the renderer strips: step 3's *"The comments
never reach the LMS"*, step 6's *"omit them from the LMS"*, and step 8's *"omit every `INVOKED`
comment"* at paste time. All three were true only because a human was doing the omitting, and a step
asking for an action a reader can never perform is one they learn to skim — which then costs the
paste-box inspection sitting beside it in step 8.

Step 6 keeps *keep them in the Markdown, the count stays auditable*, which is the ticket's
**what must not come out of this** and is untouched. Step 7 gains the decision 5 row beside the
bold-headings row it already names.

**`discussion-reply` line 243 does not move.** The reply pastes from the Markdown directly — nothing
in that skill renders a `.docx` — so its human-omission instruction is the only thing standing
between a working comment and the board. After this change the two skills say what looks like the
same thing for opposite reasons, so the post's prose says why they differ: a later author
harmonizing them would silently delete the reply's only protection.

**No separate ticket for that asymmetry.** It is a ruled and declared state rather than a defect, and
a ticket would read as an open question when it is a closed one.

### 7. The residue is `docx_write.NOT_STRIPPED`, and it is not `NOT_APPLIED`

A third declared-limits object in the module, on `NOT_GUARDED`'s precedent and with
`TheGuardsDeclaredLimits`' treatment: the module docstring names the object, `CLAUDE.md` names the
object, keys are unique, and **no row is copied into either prose surface**.

**`NOT_APPLIED` is the wrong object although it looks like the right one.** Every row in it is bound
by `TheTwoCopiesOfWhatTheRendererApplies` to a row of `apa7.md` section 6, in both directions. A
comment rule is not an APA rule, so a row there would force an APA sheet to carry a row about HTML
and the bind would assert a correspondence that is not one.

**The docstring subset table is where the rule goes and not the residue.** It already carries the row
this one is shaped like — `---  ignored -- a Markdown rule is not a Word construct` — and a comment
is the same claim about markup that is not content. It gains one row for the rule and points at
`NOT_STRIPPED` for what the rule does not cover.
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) and
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) are why the residue may not
live there: a prose edit to a limit fails nothing, so a limit written as prose goes stale in the
direction nobody notices.

Each row takes [#323](https://github.com/mshamblin5150-code/clinical-skills/issues/323)'s treatment —
a positive control rendering the form and asserting it still reaches the page — so a row that stops
being true fails the suite rather than standing as a claim nobody re-derives.

### 8. The fenced-block cost is a declared rationale and never a `NOT_STRIPPED` row

**This decision exists because the base moved mid-session.** The fence cost was ruled *into* the
tuple one round before
[ADR 0082](0082-the-declared-limit-criterion-is-a-glossary-pair-and-membership-is-decided-on-the-sentence.md)
and `tools/test_declared_limit_glossary_pair.py` merged, and that record forbids it: what may enter a
limits object is *a sentence telling a reader that a clean result covers less than it appears to*,
and a **declared rationale** is *the same shape and never a member of one*. Membership *is decided on
the sentence and never on the constant's name*.

`blocks` opens nothing on a fence, deliberately — which is the ground on which `case_study_scan`
grants no mention-versus-use exemption for one where `spelling_scan` reading a skill file does. So a
fenced comment is dropped exactly like an unfenced one, and a draft meaning to **show** the `INVOKED`
form on the page cannot. That states a *why the boundary sits where it does*, not an unreached what,
so it is a rationale.

It takes its own constant on `WHY_NO_WRITE_GUARD`'s precedent — passed to nothing, read only by a
test. ADR 0082 measured that constant as the one true *rationale for a declined option* of the three
it examined, and this is that shape exactly: the fence exemption is available and is declined.
**A code-point comment was refused** as the form ADR 0082's own constants were moved out of, and
because the fence exemption is precisely what a later session will re-propose — `spelling_scan`'s
backtick rule is close enough to be persuasive. Recording it should cost a diff against a named
object rather than an argument.

`NOT_STRIPPED` therefore holds **two** rows, both coverage sentences.

### 9. Nothing is built here

The build is a separate context's: the `blocks` rule and its blank consumption, the two console
limbs, the `discussion_post_scan --docx` row, `NOT_STRIPPED` and the rationale constant with their
controls, the `discussion-post` prose, and the `CLAUDE.md` paragraph.

The bind for decision 6 exists rather than needing inventing:
`test_discussion_post_skill.TheWorkflowCarriesEveryRatifiedGate` is a `ProseBind` over those steps,
and `test_the_post_label_runs_clean_through_every_post_command_and_renders_bold` already calls
`docx_write.main` on a real label and reads the result — so the assertion that the rendered document
carries no comment lands in a test that already renders.

## What this does not reach

**A case-study `.docx` gets no comment gate.** `discussion_post_scan --docx` is the only command in
the repository that opens a rendered archive, and no `practicum-case-study` shape mandates a comment
today. Declared rather than closed.

**Decision 5's row proves the document carries no comment, never that the Markdown beside it was the
source of it.** `--draft` and `--docx` name files whose bodies now deliberately differ, and nothing
asserts the second was rendered from the first. That is the ticket's own observation about the
workaround, surviving the fix.

**A rendered page is still read by a reader.** Step 7's visual check found this defect and no row
ruled here would have found it before that reader did; what changes is that the same shape cannot
recur silently. A clean render is not a checked page.
