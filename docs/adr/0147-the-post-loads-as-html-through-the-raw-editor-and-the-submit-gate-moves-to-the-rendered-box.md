# The post loads as HTML through the raw editor and the submit gate moves to the rendered box

[#817](https://github.com/mshamblin5150-code/clinical-skills/issues/817) was filed after a live
`discussion-post` run on 2026-09-02. The skill hands the LMS paste to the clinician and gives a
sound reason for it — direct bold on each heading survives as inline bold in the LMS — but Canvas
exposes a raw HTML editor, and `<strong>` reaches the posted entry through it exactly as a Word
paste does. The run posted through that editor and verified the result against the live board: the
stored entry was byte-for-byte the length of the submitted HTML, all five section headings and the
References label survived as inline bold, and no comment residue reached the board. The clinician's
words when the step handed the work back to him were *"why am i the bottle neck again"*.

Grilled 2026-09-07. **Nine decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## What was measured before ruling, at `43b93c8`

Freshness gate `FRESH` at the read and again before publication. Every figure below was re-derived
at that commit rather than taken from a subagent's report.

**The ticket's own anchor is wrong, and the fix spans four places rather than one.** The reason
sentence is at `skills/discussion-post/SKILL.md:360-362`, inside **step 7**. `## 8. Approve, paste,
and reread` begins at `:364` and step 8's own paste imperative is a separate line at `:370`. The
reason and the assignment live in different steps, so a change that edits "step 8" moves one and
leaves the other standing. The front matter at `:18` carries a third copy of the assignment, and
the cross-reference discussed below is a fourth.

**`discussion-post` is the outlier among the board-posting skills, not the pioneer.** The ticket's
open question 3 asks whether this change propagates to `discussion-reply`; the direction is the
reverse. `skills/discussion-reply/SKILL.md:252-253` already assigns the write to the agent — *"In
the browser, type the reply into the LMS rather than pasting it, preserving the authored line breaks
and omitting the `INVOKED` comments. Submit it, then reread the posted board version."*
`skills/course-assignment/SKILL.md:196` does the same for an upload — *"Wait for the explicit
go-ahead. Upload the `.pptx`, inspect the LMS submission page before committing the action,
submit."* `practicum-case-study` has no submission step at all. So the house already runs an
agent-submits pattern behind one gate, and this skill is the one board-posting skill outside it.

**Nothing in this repository generates HTML.** The only HTML-aware module in `tools/` is
`guidelines_currency.py`, which *parses* remote publisher index pages. There is no emitter of any
kind, so the conversion used in the 2026-09-02 run exists nowhere and the next run writes it again.

**The block seam is ready and the inline seam is not.** `docx_write.blocks` at `:927` is the one
Markdown block parser and already has three consumers outside its own module —
`reference_scan.py:252`, `case_study_scan.py:483`, and `discussion_post_scan.py` through
`document_xml`. ADR 0013 blessed exactly this shape when it called `--bold-headings` *"a third
consumer of `blocks` rather than a second parser."* But `runs` at `:513` returns Word XML, and the
pattern it is built on, `_INLINE` at `:510`, is private. There is no format-neutral inline
tokenizer, so a second renderer either reaches past the underscore or writes the second inline
parser this module's docstrings spend three paragraphs refusing.

**`--docx` gates three rows and one count.** `discussion_post_scan.GATED_ROW_SETS["docx_graded"]` is
`(BOLD_HEADINGS, RENDERED_COMMENTS, RENDERED_PAGES)` plus `rendered_text_mismatches`. Every one of
them describes a property of a document that, after ruling 1, is submitted nowhere and pasted from
nowhere.

**The paste target already has a fielded calibration record.** `skills/discussion-post/reference/canvas-paste-calibration.json`
carries ADR 0013's observation with its date, institution, course, board, theme, instrument, source
shape, sanitizer behavior, rendered type scale and the surfaces it was observed in. It is a single
JSON object rather than a list, so a second observation is a shape change and not an append.

**ADR 0015's rule has never had a literal application on this path.** Its ruling is a biconditional
— *"A file goes under `output/` if and only if it was handed in"* — and its closing section names
this exact case in advance: *"A companion file this record did not anticipate still needs a
judgment. The rule reaches it — was it handed in? — but somebody has to ask the question."* On a
paste-target path **nothing is handed in as a file at all**, which is why
`output/discussions/<stem>.md` has sat there without satisfying the rule since before this ticket,
read in place by `reference_scan`.

**The cross-reference to the sibling skill is false in both halves.**
`skills/discussion-post/SKILL.md:253-254` reads *"This differs from `discussion-reply`, which pastes
from Markdown directly and therefore still requires a person to omit its working comments."* That
skill **types** rather than pastes, and the omission belongs to whoever is typing, which is the
agent. ADR 0036 and ADR 0084 both lean on that framing, so it has propagated.

## Ruling 1 — the route is HTML through the raw editor, typing is the fallback, and the Word paste is retired

The ticket frames the change as who performs the paste. It is a change of **route**, and the two are
not separable: the browser tool types text and clicks, and cannot place rich content on a clipboard
the way Word does. Agent-performed paste therefore selects a route, and the route decides what
survives.

The measured route is primary. The agent generates HTML from the finished Markdown, loads it through
the raw HTML editor, and toggles back to the rich editor. **Typing is the declared fallback**, which
is what `discussion-reply` already does and is available on any board whatever its configuration.
**The Word paste is retired.**

A third route was named and refused. Placing `CF_HTML` on the Windows clipboard and sending `ctrl+v`
would reproduce the exact sanitizer path ADR 0013 measured and would need no raw editor — and nobody
has ever run it here. Adopting it would be reasoning about Canvas rather than measuring it, which is
the move ruling 4 of ADR 0143 was caught making. It is refused rather than deferred, and the ground
is that typing already covers the case it was proposed for.

**Typing is a real fallback rather than a formality, and its cost is stated.** It carries no
formatting, so bold headings require interleaving `ctrl+b` around each heading's text — six times
for five headings and the References label. `discussion-reply` already does this for one label, so
the mechanism is established rather than new.

**Why the primary route is easier is a fact about the instrument rather than a preference.** The raw
editor is a plain `textarea`: nothing intercepts a keystroke, nothing auto-formats, nothing
transforms. The rich editor's input pipeline does all three — smart quotes, a typed `1.` opening an
ordered list that renumbers itself, a typed URL becoming a link. Those are silent edits to the
author's text, which is the failure [#815](https://github.com/mshamblin5150-code/clinical-skills/issues/815)
was filed over arriving from the other end.

## Ruling 2 — both artifacts are kept, and each is graded for what it now is

The `.docx` is kept. The clinician's reason is preservation and it stands on its own: the board keeps
no copy anyone can open, and the Markdown is source rather than shape, so a paper-shaped file is the
only artifact that shows the post as a document.

**Grading both artifacts on one row set is refused.** When two renderings of one source disagree, a
run fails — and the artifact that fails it is the one that did not ship. That is a false alarm on a
correct submission, which is the failure direction this repository refuses everywhere else. The case
is not hypothetical: `docx_write.NOT_STRIPPED` declares that mid-line and multi-line HTML comments
survive the renderer, and a mid-line `<!--` reaches the `.docx` as literal visible text in a `w:t`
node while reaching the HTML as a real comment delimiter. Same source, two consequences, one row
name.

So each artifact is graded for what it is. The `.html` is the submission and takes the comment
residue row, the heading row restated as *every heading is `<p><strong>`*, and paragraph-text parity
against the Markdown. The `.docx` is the archival render and takes **text parity only** — the one
property an archive must have — which is already a reported count rather than an exit-status row and
therefore cannot fail a run over a file nobody handed in.

## Ruling 3 — the archival `.docx` renders proper headings, and ADR 0013's ruling becomes historical

`--bold-headings` exists because ADR 0013 ruled that *"a document destined for a paste box carries
its heading formatting as direct run properties."* After ruling 1 no document is destined for a
paste box on this path, so the flag's reason is spent and the file it produces is a document whose
headings are cosmetic bold carrying no `outlineLvl` — invisible to Word's navigation pane and to
anything that reads structure. A file kept in order to preserve it is preserved in the shape a
document should be in.

`discussion-post` is the only caller of `--bold-headings`. **ADR 0013's ruling therefore becomes a
historical record while its measurement stays load-bearing forever** — *"the sanitizer keeps tags
only"* is precisely why route A works and why ruling 8 below is answerable at all. This is stated
rather than left to be discovered, because a builder who found the flag orphaned without this
sentence would put it back.

**One consequence is sharper than the flag's retirement.** With the `.docx` carrying proper heading
styles, ADR 0013's measurement says those headings arrive through the clipboard **unbolded** — *"No
heading level renders bold at any level."* The Word paste is therefore not a dormant third rung that
could be reached for in an emergency; it is a route that now produces a visibly wrong post. Ruling 7
names no third mechanism for that reason.

## Ruling 4 — `output/` holds the submission and its renders, and ADR 0015 is amended rather than excepted

The `.docx` stays in `output/`. ADR 0015 as written sends it to the run directory, and priced this
objection deliberately: *"The clinician's reading copy and the submitted document are now two files
... That is the price of `output/` meaning exactly one thing."*

**That price was set on an upload path and this is not one.** The rule is amended rather than
excepted: **`output/` holds the submission and its renders — the source of record, the bytes handed
in, and any archival rendering of the same content. Provenance stays in the run directory.** The
skill states which file was handed in; nothing infers it from a filename.

The defect ADR 0015 existed to kill was `-PROPOSED` and `-SUBMIT` — two files with **different
content** and nothing saying which shipped. Three files carrying the **same** content in three
formats reproduce none of it: the extensions are distinct, no two are near-identical, and the
submission is named rather than guessed. Amending keeps `output/` meaning one thing everywhere
instead of one thing here and another there, and it retires the sharpest edge of that rule on
purpose rather than leaving a builder to find a `.docx` in `output/` beside a ruling that forbids it.

## Ruling 5 — the box reading is pixel-backed, independently read, and its denominator comes from the export

The required visual check retargets from the Word page images to the **rendered Canvas box**. What
can mangle text on the new route is the HTML generation and Canvas, not Word, so comparing Word's
pages checks a pipeline nobody uses.

The check it replaces had two deliberate properties, and the retarget inherits both. A **fresh,
non-authoring context** does the looking, as step 7 already requires. And it is **backed by kept
pixels**, which is ADR 0087 ruling 1 — *"A page with no picture is a page not checked."* Downgrading
either would be a downgrade wearing a rename.

**The denominator is the submitted HTML's block count, derived through `blocks` and never taken from
the record.** ADR 0087's denominator is un-fakeable because Word states the page count and the
`.docx` carries none; a scrolling box has no page count, and a screenshot count is whatever the
agent says it is. *Every block accounted for in the reading* is the exact analogue of *every page
imaged*, and it makes this check sharper than the one it replaces: a block Canvas silently dropped
shows as a short reading rather than as a clean one.

**The captures live in `render/pass-N/`, and the pass's export is the `.html`.** That satisfies
ADR 0124's invariant literally rather than by exception — one page-faithful export, N images of it,
the denominator derived from the export. One export, one row, one record shape; `SOURCE:` gains
`canvas-box` beside `word-pdf`, `word-xps` and `clinician`, so `rendered-pages` grades the box read
rather than reporting `not graded`. The one genuinely new thing is declared: **the rasterizer is the
destination itself**, which is why this check is worth more than the Word one it replaces — it
images the actual renderer under test rather than a stand-in.

It holds on the typing fallback too. Under ruling 4 the `.html` exists as a render of the submission
whether or not it was the vehicle, so the denominator is the same either way.

## Ruling 6 — two gates, and the second is the only reader the pipeline does not produce

The house pattern is one gate. This skill takes two, and the divergence is declared rather than left
looking like an oversight.

1. Show the finished post. **Gate 1** approves it and authorizes loading it into the box.
2. The agent generates the HTML, loads it through the raw editor, and toggles back.
3. A fresh non-authoring context reads the rendered box against the Markdown and retains the
   captures.
4. The clinician is shown the captures **and told the box is loaded and unsubmitted**, so he can
   look at the live page rather than at an image the agent produced.
5. **Gate 2** authorizes submit, and nothing else does.

The clinician's ground, in his words: *"i need to see what i am asking you to do before i ever agree
for you to post it."* The mechanical reason is that **every record in this pipeline is agent-written
and self-attesting** — `RENDERED`, `REREAD`, and the box reading alike. ADR 0050 already says what
that is worth: a posted reading *"does not establish that the reading was careful, or that the
reader compared anything."* The fresh context is independent of the authoring context and is still
the agent's. **Gate 2 is the only reader in the chain whose eyes are not produced by the thing being
checked**, which is why it cannot be folded into gate 1 for convenience.

**A non-clean box reading stops and returns to the clinician.** The agent never adjudicates its own
paste.

The split this settles is the ticket's real subject: **the bottleneck was the mechanical paste, not
the inspection.** Looking at a post before it ships is the approval the clinician already gives;
fifteen thousand characters of clipboard work is not.

`discussion-reply` and `course-assignment` keep one gate. A reply is short and typed, and a deck
upload shows a filename; neither loads fifteen kilobytes of markup into a box where a silent drop is
invisible.

*(Corrected in place 2026-09-12, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, by [#948](https://github.com/mshamblin5150-code/clinical-skills/issues/948) and
[ADR 0190](0190-the-canvas-editor-surface-is-one-shared-route-and-the-reply-prefers-the-raw-editor.md)
ruling 2. `discussion-reply` no longer types, so **and typed** describes the route at the time of
ruling and not the current one. The exemption stands on length alone. ADR 0190 ruling 2 put the
second gate to the clinician on that changed premise and he declined it, ruling instead that the
reply's pre-submit readback becomes a graded comparison of the editor's serialized HTML against the
built `.html`, with a non-clean comparison returning to him. The residue — that no reader who is not
the author sees the loaded box before submit — is declared in that record rather than closed.)*

## Ruling 7 — the fallback is declared at gate 1, the route never switches after a bad reading, and there is no third rung

The raw editor is an **instance and not a Canvas guarantee** — one board, one date. Its absence is
detected by looking for the toggle control and is **reported at gate 1**, before anything is loaded,
with what the fallback costs. That is not a new gate; gate 1 already exists, and this is information
the clinician needs in order to give it. **The fallback is never taken silently**, because typing and
pasting produce materially different artifacts and one of them is what ships.

**The route is chosen before the paste and is never switched after a bad reading.** A non-clean box
reading returns to the clinician under ruling 6; it does not silently re-route to typing and try
again. Retrying a failed publication unsupervised is the one act neither gate can see.

**Typing keeps the bold via the interleave**, and the box reading is what verifies it landed. That
is the case where a pixel-backed independent read earns its cost: a missed `ctrl+b` toggle is
invisible in the source and obvious on the page.

**There is no third rung.** If typing also fails the skill stops and asks. Ruling 3 is why: the Word
paste would now produce a visibly wrong post rather than a degraded one.

## Ruling 8 — the block quotation is measured on this route rather than derived

ADR 0143 ruling 4 declares APA's block-quotation form unreachable in the Canvas box and, on that
ground, gives `discussion_post_scan` a declared limit and tells an author never to write a `> `
marker in a post draft. It is derived from ADR 0013's **Word-clipboard** measurement, and that
record admits it: *"Nobody has pasted a left-indented paragraph into that box."* ADR 0013's own
finding is that the sanitizer keeps **tags**, and `<blockquote>` is a tag rather than a `style`
attribute, so nothing has been measured against it either way.

**It is measured here rather than ruled stale on the mechanism**, because deriving twice does not
make a measurement. The route this record adopts is what makes it cheap and safe: load HTML carrying
a `<blockquote>` into the raw editor, toggle to the rich editor, read whether it renders indented,
and **discard without submitting**. No board write and no publication — the capture machinery of
ruling 5 pointed at a question instead of at a draft. The measurement leaves a draft in the box that
wants clearing, and that is its whole cost.

**The observation is recorded, not remembered.** It goes into
`skills/discussion-post/reference/canvas-paste-calibration.json` as a second entry with its own
instrument, date, board and surface. That file is a single object today, so the build restructures
it to carry observations as a list without editing ADR 0013's row. The disclosure stays what ADR 0013
disclosed about itself: one institution, one course, one board, one theme, one date.

This settles ADR 0143's ordering constraint and unblocks
[#815](https://github.com/mshamblin5150-code/clinical-skills/issues/815) whichever way the
measurement falls.

## Ruling 9 — `discussion-reply` is untouched and the reply route is filed

The ticket's premise does not reach it. There is no bottleneck there: the agent already types and
submits behind one gate, and has since ADR 0050. Nothing hands work back to the clinician.

What does reach it is a **reliability** argument rather than a bottleneck one — the reply's bold
`References` label depends on a `ctrl+b` interleave in a live editor, which ruling 7 treats as the
degraded path. Adopting route A there is filed as its own ticket, whose first item is a measurement
nobody has taken: **does the reply box expose a raw editor at all?** Folding it in here would carry a
skill with no renderer and no output artifact into a pipeline built around both, on an unmeasured
assumption about a different box, inside a ticket whose subject is a bottleneck that skill does not
have.

*(Corrected in place 2026-09-10, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, by [#1039](https://github.com/mshamblin5150-code/clinical-skills/issues/1039). `discussion-reply`
no longer types. A typed reply reached the board with a reference URL that was not a link, so the
skill now builds its submission with `tools/post_html.py` and loads it through the editor's content
interface. That interface is not the raw-editor toggle this ruling filed a measurement for, so
[#948](https://github.com/mshamblin5150-code/clinical-skills/issues/948)'s toggle question stays
open. The ruling's scope for #817 is unchanged.)*

*(Corrected in place 2026-09-12, same terms, by #948. **The filed measurement is taken and the answer
is yes.** A threaded reply composer on Bluefield NUR 5144 M2 Discussion carries the same
`data-btn-id="rce-edit-btn"` toggle as the topic-level composer, and toggling it exposes a plain
`<textarea>` with no CodeMirror — Canvas's raw editor. This ruling's *"a skill with no renderer and
no output artifact"* is also spent on its first limb: the reply has rendered through
`tools/post_html.py` since #1039. It has no output artifact still, and ADR 0190 ruling 6 keeps it
that way. Measurement, discriminator and limits are in ADR 0190.)*

**One correction to `discussion-post` about its sibling lands in this ticket's diff**, because it is
false in the file this change is already editing. `skills/discussion-post/SKILL.md:253-254` claims
the reply *"pastes from Markdown directly"* and *"still requires a person to omit its working
comments."* It types, and the omitter is the agent.

## Derived rather than ruled

**The HTML emitter is a module rather than a flag.** Every other function in `docx_write.py` emits
Word XML and writes a zip. `tools/post_html.py` importing `docx_write.blocks` is the shape
`reference_scan` and `case_study_scan` already use.

**`_INLINE` is promoted to a public, format-neutral inline splitter** consumed by both renderers, so
there is one home for what Markdown this repository speaks. This is not
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s refused extraction: that
one was two modules that happened to write a helper the same way, and this is one policy with two
consumers.

**`esc` is reusable for HTML text nodes and not for attribute values.** It escapes `&`, `<` and `>`
only. The emitter writes no attributes, so the boundary holds; a future attribute needs its own
escaping.

*(Corrected in place 2026-09-10, by [#1039](https://github.com/mshamblin5150-code/clinical-skills/issues/1039).
The emitter now writes one attribute: an anchor's `href`, in double quotes. `esc` still covers it,
because `post_html.URL` cannot match a double quote and the value therefore cannot close its own
quoting. Any other attribute still needs its own escaping.)*

**Own-line comments are dropped for free** — `post_html` consuming `blocks` inherits ADR 0084's drop.
`NOT_STRIPPED`'s mid-line and multi-line forms survive, which is why ruling 2 keeps the residue row
on the HTML and why it matters more there than it did on the `.docx`: a comment inside a `textarea`
paste is invisible in the rich editor and lands on the board.

**`--html` joins the grader's flags on the established terms.** Absent, its rows report `not graded`
rather than `0`, on [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
ruling.

**ADR 0036's outcome is unchanged and its post-path mechanism sentence goes stale.** `## References`
becomes `<p><strong>References</strong></p>` either way; the sentence explaining that the clinician
pastes from Word to get there does not survive ruling 1.

**Nothing about the clinician's authorization is removed.** It is doubled. Authorization to draft,
render, or load is still not authorization to submit.

## What this record does not settle

**Whether the raw editor exists on any other board.** One board, one theme, one date, disclosed in
the calibration record the way ADR 0013 disclosed its own. Ruling 7's fallback exists because this
is an instance rather than a guarantee.

**Whether the box reading was careful.** Ruling 5 establishes that a located, pixel-backed reading
accounting for every block was recorded. It does not establish that the reader compared anything,
which is ADR 0050's limit arriving at a new surface. Gate 2 is the mitigation and not a proof.

**Whether a retained export is an export of the submission.** ADR 0124's hole carries over unchanged:
the shape establishes that a pass keeps exactly one export, never that it is of the artifact that
was submitted.

**Whether Canvas's rendering of the box is faithful to what it will render on the board.** The
2026-09-02 run compared a stored entry length rather than a rendering, and ruling 5 images the box
before submission rather than the posted body. The reread at step 8 remains the only reading of the
posted entry, and it is text.

**What the block-quotation measurement will find.** Ruling 8 orders the measurement and rules nothing
about its outcome. If `<blockquote>` survives, ADR 0143 ruling 4's declared limit is stale and its
instruction never to write a `> ` marker is wrong; if it does not, ruling 4 stands on a measurement
instead of on a derivation. Either result is worth more than the current state.
