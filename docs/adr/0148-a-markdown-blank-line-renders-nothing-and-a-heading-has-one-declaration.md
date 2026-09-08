# A Markdown blank line renders nothing, and a heading has one declaration

Out of [#828](https://github.com/mshamblin5150-code/clinical-skills/issues/828) and
[#826](https://github.com/mshamblin5150-code/clinical-skills/issues/826), grilled together on the
clinician's ruling of 2026-09-08 that they are one surface. Measured at `70ca6c9`.

`tools/docx_write.py` emitted one empty `<w:p/>` for every blank line in the Markdown, on top of
body styles that already carry `w:after="0"` with `w:line="480"`. Separately, `--bold-headings`
dropped the heading's `pStyle` and re-applied four of its properties by hand, so the style-borne
`<w:keepNext/>` became unreachable. Both defects sit in the same function, and after the first is
fixed the second's fix has no visible effect without it.

## What was measured before ruling, on 2026-09-08

**Word 16.0, through COM, one APA-shaped source rendered by the tree and by the four-line patch.**
Paragraph vertical position on the page:

| | tree | patch |
| --- | ---: | ---: |
| line to line inside a paragraph | 27.6 pt | 27.6 pt |
| paragraph to paragraph | 55.2 pt | 27.6 pt |
| heading to the first line under it | 55.2 pt | 27.6 pt |
| `References` to the first entry | 27.6 pt | 27.6 pt |
| entry to entry | 27.6 pt | 27.6 pt |

Exactly 2x at every body junction, and the patched body becomes numerically identical to the
reference list. `w:after="0" w:line="480" w:lineRule="auto"` is already continuous double spacing,
which `word-renderer-calibration.json`'s `body-defaults` row confirmed on 2026-08-22; the empty
paragraph is pure addition.

**A synthetic 42-paragraph, 5-heading, 7-entry document sets in 13 pages by the tree and 11 by the
patch**, Word reporting 104 paragraph elements against 56. That reproduces the ticket's own
104/56/48 split on a source anyone can rebuild, which the uncommitted post behind those figures
cannot do.

**`<w:keepNext/>` is inert on the case-study path today.** It binds a heading to the paragraph that
follows it, and the paragraph that follows a heading is the empty one, which carries no `keepNext`
of its own. With the heading tuned to a page foot, Word put the heading on page 2 and its text on
page 3 in the tree, and both on page 2 under the patch. So the property is defeated on the flagged
path by #826's missing `pStyle` and on the unflagged path by the empty paragraph, and a heading in
this repository has orphan protection on neither.

**Two tables in a row and a table at the end of the body were rendered both ways.** Neither produces
adjacent `<w:tbl>` elements or a table-last body, because `table()` at `:641` already appends its own
`<w:p/>`. The obvious structural objection to removing the emission does not exist.

**The archaeology answers #828 decision 3, and answers it differently than the ticket assumes.**
`git log -S '<w:p/>' --follow -- tools/docx_write.py` returns exactly one commit, `bb4a7ed` of
2026-08-18, which created the file; the emission and the `if not in_references` exemption were
written as one clause in it. The only other commit to touch those lines is `ad13b34` (#277), whose
message says *"No rendered output moved."* No ADR, no ticket and no commit message anywhere states a
reason for the exemption. `bb4a7ed`'s own message says *"the round trip is the test ... there is no
Word here."* The ticket's *"the reference-list exemption is deliberate"* overstates the record: it
was authored by someone with no way to look at the page, not decided by someone who had.

**apastyle.apa.org, read in Chrome on 2026-09-08.** `curl` and the fetch tool both received an
Incapsula block page carrying HTTP 200, which is a fact about those tools rather than about the
page. Line spacing, which APA's page attributes to *Publication Manual* section 2.21:

> In general, double-space all parts of an APA Style paper, including the abstract; text; block
> quotations; table and figure numbers, titles, and notes; and reference list (including between and
> within entries). Do not add extra space before or after paragraphs.

Headings, attributed to sections 2.26 and 2.27:

> Do not add blank lines above or below headings, even if a heading falls at the end of a page.

So this is not an internal-consistency repair. It is a published rule the renderer has broken on
every document it has produced, plus a second published rule about headings that the same fix
happens to satisfy. The line-spacing sentence also names block quotations, which independently
corroborates [ADR 0143](0143-the-block-quotation-is-authored-markup-the-renderer-obeys-and-its-citation-keyed-grader-lives-where-the-docx-is-submitted.md)
ruling 5.

**The heading sentence settles `keepNext` against the intuition.** APA contemplates a heading falling
at the end of a page and forbids only the blank-line remedy, so APA does not require keep-with-next.
The same page tells writers to *"use the Styles menu to format headings"*, and Word's built-in
heading styles carry `keepNext`, so retaining it is consistent with APA's own recommended workflow.
It is not an APA rule and must not be filed as one.

**The four `paste_rows` in `word-renderer-calibration.json`, measured 2026-08-22, already rule out
restoring the style under the flag.** A named heading style reaches the clipboard as `<h1>`/`<h3>`/
`<h4>`, which is [#418](https://github.com/mshamblin5150-code/clinical-skills/issues/418); a renamed
style leaves bold only in the embedded stylesheet; a nameless style loses the bold entirely. Only
direct formatting carries `<p><b>` inline.

**Nothing in the suite can see the thing.** Zero of 108 test modules match the self-closing
paragraph form. Of 18 places `tools/test_docx.py` mentions `<w:p`, 16 assert properties and are
sound; exactly two isolate a paragraph by splitting text, at `:509` and `:514`.

## Ruling 1. The body emits nothing for a blank line, on every path

The `if not in_references` guard is removed rather than inverted. The reference list and the body
take one branch for the first time in the file's life, and the branch is merged with the separator
branch — `if block.kind in ("blank", "separator"): continue` — which is byte for byte what
`reference_scan` and `case_study_scan` already write.

**The merge is not cosmetic.** Left alone, `if block.kind == "blank": continue` reads as dead code,
and deleting it as a tidy-up would let a blank fall through to the paragraph branch and render an
empty paragraph carrying a first-line indent, which is worse than the defect being repaired.

**What it costs is named rather than absorbed.** Every document this renderer has produced would
re-render differently. Nothing re-renders on its own, `output/` is untracked, and the destination
guard refuses an overwrite of a hand-edited file, so the cost lands only where a run deliberately
re-renders an old draft. The one grader that compares an archive with a fresh parse,
`discussion_post_scan`'s `rendered-text` row, is reported and not graded — and its declared limit at
`:184` names a blank-paragraph delta as the false alarm that made it so.

**A hard-wrapped body paragraph becomes invisible.** Today a wrap is faintly legible as a missing
gap; afterwards it is indistinguishable from a real paragraph break. That is the `one paragraph`
`NOT_APPLIED` row's defect arriving in the body, it has no catcher there, and it is accepted rather
than absorbed.

**What could not be measured** is whether the LMS paste box needs the empty paragraph to keep
paragraph boundaries visible once it discards the double spacing. Canvas is closed to this
repository. The graded artifact is the case study's `.docx`; if the paste turns out to need visible
separation that is a fact about the paste route, which is
[#817](https://github.com/mshamblin5150-code/clinical-skills/issues/817)'s.

## Ruling 2. The parser keeps the blank block

Over deleting it, which is what #828 decision 2 proposed.

Deleting it changes zero verdicts: `render_body` now discards it, `markdown_tables` never looked,
and `reference_scan.read_document` at `:1064` and `case_study_scan.read_sections` at `:485` and
`:617` each skip it. That is the whole case for deleting, and it is not enough to justify destroying
the only record of where the author put their blank lines.

Two ratified records stand in front of it — ADR 0143 ruling 2 hardened the line-is-a-paragraph
contract, and [ADR 0084](0084-an-own-line-html-comment-is-markup-and-the-renderer-drops-it.md)
ruling 3 refused general blank collapsing as a change to this contract *"wearing a comment fix as a
disguise"*. That refusal reserved the contract for a ticket whose subject it is, which this is; it
does not license deleting the record.

And [ADR 0147](0147-the-post-loads-as-html-through-the-raw-editor-and-the-submit-gate-moves-to-the-rendered-box.md)
queues `tools/post_html.py` as a fourth consumer of this parser, emitting into a box with no double
spacing. Deleting the blank record immediately before that arrives is the wrong order.

**The ticket's framing is satisfied without the deletion.** *The paragraph break should be carried by
the paragraph boundary itself* is already true — consecutive `<w:p>` elements are the boundary — so
the blank block is now purely informational, and keeping informational parse output is cheap.

## Ruling 3. `#826` is ruled here, and both tickets stay open

They are the same function and, after ruling 1, the same property. Neither is closed as a duplicate
of the other.

The reason is an ordering dependency neither ticket records: build #826 alone and nothing changes on
the page, because the heading still keeps with an empty paragraph, so a builder would apply a
correct fix, look at the render, and reasonably conclude the diagnosis was wrong.

## Ruling 4. A heading has one declaration, and both paths read it

Over adding the single forgotten property.

A heading has six properties. Centering, italic and indent are declared once in `HEADING_LEVELS` at
`:379` and read by both paths. Bold and `keepNext` are declared only on the style side — bold inside
the style XML, `keepNext` hardcoded at `:397` — and the flagged path at `:1063-1080` re-supplies the
first from memory and forgot the second. `para()` has no `keep_next` parameter at all, so this is a
missing capability rather than a missed keyword.

#826 is therefore not *somebody forgot `keepNext`*; it is *there are two hand-maintained answers to
what a heading is, and they disagree*. Bold and keep-with-next join the three already in
`HEADING_LEVELS`, `_heading_style` and the flagged path build from that one object, and a test
asserts the two paths produce the same property set. Restoring the style under the flag is refused
on the 2026-08-22 clipboard measurements above.

**What is not established** is whether adding keep-with-next changes what the paste box receives. It
is a pagination property with no HTML equivalent, so nothing is expected, but that is an expectation
and not an observation; the paste rows need re-observing before it is claimed.

## Ruling 5. A check of paragraph structure parses the archive rather than matching its text

Over the discriminating regex the ticket proposes, and over prose.

**The ticket's own suggested guard is wrong after ruling 1.** It asks for a test asserting a
known-good document contains at least one `<w:p/>`; a table-free document now contains zero, so that
assertion fails on correct output. The correct assertion inverts: no empty paragraph anywhere except
the one `table()` emits after each table.

Parsing removes the class of error rather than patching an instance, because a parsed element does
not know whether it was serialized `<w:p></w:p>` or `<w:p/>`. `discussion_post_scan._paragraph_texts`
at `:477` already does this and is immune by construction. The two text-splitting sites at
`test_docx.py:509` and `:514` are converted, and a walk over `tools/` refuses a new reader of
paragraph structure that matches an archive's text instead of parsing it.

Prose was refused on [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s ground: an edit to a
docstring fails nothing.

**The walk's ceiling is declared rather than closed.** A matcher assembled at run time is invisible
to it, so the claim is a floor on the shapes in the tree and never *a third blind reader cannot
arrive*. `test_ls_files_coverage.py` and `test_case_study_scan.py` both already carry that ceiling.

## Ruling 6. Two sourced APA rows, and `keepNext` is measured without becoming an APA rule

`apa7.md` has 30 sections and none states a body-format rule, which is why the renderer had nothing
to be measured against. Section 6 gains two rows, both carrying the 2026-09-08 reading above:

- No extra space before or after paragraphs, section 2.21.
- No blank lines above or below headings, even at the end of a page, sections 2.26 and 2.27.

Each takes its own calibration identity, because `NOT_APPLIED` and its tests bind rows one-to-one by
a distinctive phrase and these are two rules on two APA pages.

Heading property parity between the styled and flagged paths takes a calibration identity and **no**
section 6 row. Section 6's left column is APA rules; APA publishes none here, and this sheet exists
to stop a recalled rule being written down as a looked-up one.

**`NOT_APPLIED` gains nothing from either ticket.** Both fixes make a rule applied, which answers the
sweeps' recommendation to rule that object once.

**Two costs the builder inherits.** `tools/docx_word_probe.py` contains the words `blank` and `empty`
zero times and has no limb that counts paragraphs, so one must be written before either row can be
measured; ADR 0008's price is that a new section 6 row fails until it has a distinct calibration
identity and record. And section 6 sits under a single blanket sentence dating sections 1 through 7
to 2026-08-18, so rows verified on 2026-09-08 require that sentence to carry both dates or move to
per-row dating.

## Ruling 7. ADR 0084 ruling 3 keeps its mechanism on a new reason, recorded here rather than there

That ruling made a dropped own-line comment take one adjacent blank line with it, so that
`para / blank / comment / blank / para` would not leave two consecutive empty paragraphs. Ruling 1
removes the empty paragraphs, so its stated reason is discharged and the mechanism at `:949-958`
now changes nothing observable.

It is retained anyway, on ruling 2's ground: it keeps the parser's record faithful to what the source
would have looked like with the comment removed, which is what ADR 0147's HTML emitter will read.
ADR 0084 is not edited — records here are frozen, as the sweeps established for five ADRs carrying a
dead `apa7.md` path — so this record carries the note that its `:50` sentence about one `<w:p/>` per
blank source line is now historical.

## What this record does not settle

Whether the LMS paste box needs a visible paragraph separator once it discards the double spacing.
Canvas cannot be reached from this repository, and the observation belongs to
[#817](https://github.com/mshamblin5150-code/clinical-skills/issues/817)'s route.

Whether adding keep-with-next under `--bold-headings` changes the clipboard payload. The four paste
rows were measured before the property existed on that path.

Whether a hard-wrapped body paragraph should be caught. Ruling 1 makes one invisible on the page and
supplies no catcher, on the same terms as the `one paragraph` row it inherits from.

Whether the walk in ruling 5 can see a paragraph reader assembled at run time. It cannot, and the
claim is stated as a floor.

Whether the two APA rows' section numbers are correct in the *Publication Manual*. They are what
apastyle.apa.org attributed on 2026-09-08, which is the only claim this sheet ever makes about a
manual it does not hold.

## Ordering constraint

This record clears the `EXTERNAL-GATE` on `issue:828` that packet P815 carries, so ADR 0143's block
quotation build can proceed once the build behind this record lands. Until it does, a correctly
formed block quotation still ships with the quadruple gap, in the case study, where the `.docx` is
the graded artifact.
