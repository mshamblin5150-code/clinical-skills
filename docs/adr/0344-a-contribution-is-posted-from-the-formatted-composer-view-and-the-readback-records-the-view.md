# A contribution is posted from the formatted Composer view and the readback records the view

**Measured at:** ca94d9fe823db4fc2fda2bbb4e9e2a8e829f9290

[#1555](https://github.com/mshamblin5150-code/clinical-skills/issues/1555) was filed from the
after-action review of a NUR 5042 Module 9 `discussion-reply` run on 2026-10-04. The run loaded a
Reply into Canvas's plain raw-HTML textarea, graded the readback clean, and clicked submit in the
same step. The clinician stopped it before anything posted. On the retry the Composer showed the
reply in Canvas's pretty HTML Editor, he looked, and it posted with rendered formatting. The ticket
named two defects. [ADR 0331](0331-every-canvas-save-waits-at-the-loaded-box-for-a-recorded-go-ahead-and-plain-text-is-built-by-one-command.md)
settled the first, the missing stop at the loaded box, and its build has landed. It left the second
to this ticket: the readback cannot see which view the Composer is in.

Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the clinician ruled
everything below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**A clean readback cannot separate the state the clinician refused from the state he approved.**
`skills/_shared/reference/canvas-editor.md` reads back "the raw textarea value while the raw editor
is active", and `discussion_reply_scan`'s `editor-readback` row compares that serialized HTML with
the built `.html` by paragraph text, anchor destinations, and anchor count. The raw textarea, the
pretty HTML Editor, and the rich editor can all hold HTML that passes that comparison, so the
comparison says nothing about which of them the Composer is showing.

**ADR 0147 already ruled the switch back for the Initial post, and the shared sheet lost it.**
[ADR 0147](0147-the-post-loads-as-html-through-the-raw-editor-and-the-submit-gate-moves-to-the-rendered-box.md)
ruling 1 has the post load "through the raw HTML editor, and toggles back to the rich editor", and
its ruling 6 repeats the step. [ADR 0190](0190-the-canvas-editor-surface-is-one-shared-route-and-the-reply-prefers-the-raw-editor.md)
ruling 4 moved the load route into the shared sheet, whose route 1 now ends at "Load the built HTML
into that textarea." `skills/discussion-post/SKILL.md` says to "inspect the rendered Composer" and
never says to switch back. No graded row records the view at the post's click.

**The switch from the raw editor to the rich editor has been exercised once, and not on a Reply.**
`skills/_shared/reference/canvas-editor-calibration.json` records a 2026-09-08 NUR 5144 M2 reading
in which a `<blockquote>` "survived the raw-editor-to-rich-editor toggle and rendered visibly
indented", with the Composer surface unresolved. Its 2026-09-12 entry exercised the threaded
Composer's toggle into the raw editor only: the rich toolbar disappeared, a plain visible textarea
appeared with zero CodeMirror instances, and the status control offered *Switch to pretty HTML
Editor*. Those three page facts are what separate the views.

**Whether the raw textarea would have posted literal markup is unmeasured.** Measuring it means
submitting, and a Canvas board entry cannot be withdrawn. Both the raw textarea and the pretty HTML
Editor show markup rather than formatted text; the clinician accepted the second and refused the
first. The rulings below rest on the view he will accept at his look and at the click, not on what
Canvas would have stored.

## Ruling 1 — a contribution is looked at and posted only in the formatted view

Whenever a Composer holds a contribution at the loaded-box stop and at the click that posts it, the
Composer is in its formatted view: the rich editor, where the contribution appears as the board will
show it. It is never submitted from the raw textarea or from the pretty HTML Editor.

The pretty HTML Editor, which the 2026-10-04 retry used and the clinician approved there, was
declined as the required view. It still shows markup rather than the contribution, so it cannot
answer the concern he stopped the run over, and reading text back out of a CodeMirror instance is an
operation no run has performed or measured. Allowing either code view as long as the run recorded
which one was declined as the most permissive answer: it keeps a second path to test and still asks
him to check tags.

## Ruling 2 — the raw-HTML route is a loading step that ends in the formatted view

`canvas-editor.md` route 1 keeps its place as the first route. The run confirms it landed in the raw
textarea, loads the built HTML there, switches the Composer back to the formatted view, and only then
reads back and stops. The switch back is part of the route rather than an optional extra step.

Retiring the route in favor of the content interface was declined. That route needs a keystroke to
register the change, and that keystroke can autolink the token before it; #1039's surviving board
entry is that cost. Typing every contribution was declined as the slowest route with the most
chances for a formatting slip. The raw textarea remains the only way into the Composer with no
parser between the built bytes and the editor. The rich editor parses those bytes on the switch
back, and the readback comparison already tolerates serialization differences.

## Ruling 3 — one fixed page script reads the view and the contribution together

`canvas-editor.md` carries one fixed page script, used verbatim. In a single read of the identified
Composer it reports which view is showing and the serialized contribution. The view comes from the
page facts the 2026-09-12 measurement found: whether the plain textarea is visible, whether a
CodeMirror instance is present, whether the rich toolbar is visible, and what the status control
offers. The script reports the formatted view only when the textarea is hidden, no CodeMirror
instance is present, and the toolbar is visible. Any other combination reports the code view it
matches, or reports the view as unidentified. The serialized contribution comes from `getContent` on
the identified TinyMCE instance, or from the rich-editor body's serialized `innerHTML` when
`getContent` is unavailable.

The script's output is retained unedited as the readback. A grader refuses a readback whose view is
not the formatted view, and refuses a readback with no view or in any other shape. A readback whose
text equals the build is not clean when the view is a code view.

A line written by the run naming the view it saw was declined: the 2026-10-04 run did not misreport
the view, it never checked it, and a separate line can be written without the check. Reading the view
in the same step as the text means a clean readback carries the view. A screenshot read by a second
reader was declined on ADR 0331 ruling 3's ground. The script is still run by the agent, so a clean
row is a floor and not proof that the click happened in that view.

## Ruling 4 — the rule and its check cover the Initial post and the Reply

Rulings 1 to 3 live in the shared sheet and apply to every Composer. `discussion_reply_scan`'s
`editor-readback` row refuses a code-view readback. `discussion_post_scan` gains the same refusing
check over a readback taken at the loaded-box stop, which it does not retain today. The post's
retained captures and its independent box reading are unchanged; they are taken before the stop,
and only the readback speaks for the view at the click.

Covering the post by the written rule alone was declined, because nothing graded would catch the
Composer left in a code view between the captures and the click. Leaving the post's route 1 wording
as it is was declined, because the shared sheet would then give two instructions for one route.

## Ruling 5 — the loaded-box message names the view

ADR 0331 ruling 3's message at the loaded box reports the view in its readback line, for example
"loaded in the formatted view, unsubmitted, in tab '<tab title>'; readback matches." The grader's
refusal already implies the view on a clean readback. Naming it costs a few words and makes a
mismatch between the message and what the clinician sees in the box immediately visible.

## Ruling 6 — `CONTEXT.md` gains Composer view

The face a Composer shows is named **Composer view** in the glossary, beside **Composer** and
**Load route**. It replaces the drifting words "raw editor", "HTML mode", "editor mode", and "mode"
in new prose.

## Supersedes

- [ADR 0190](0190-the-canvas-editor-surface-is-one-shared-route-and-the-reply-prefers-the-raw-editor.md)
  ruling 3, the words "so it carries no parser and nothing live between the bytes and the box". They
  remain true of the load. The Composer at the stop and at the click holds the rich editor's parse of
  those bytes, because route 1 now ends in the formatted view. The route order, the confirmation of
  the landed editor by reading it, and the rule against switching routes after a bad comparison stand.

## Build checklist

- `skills/_shared/reference/canvas-editor.md`: route 1 ends with the switch back to the formatted
  view; the readback section names the fixed page script, replaces "the raw textarea value while the
  raw editor is active", and states that a code-view readback is not clean; the loaded-box paragraph
  names the view in its readback line.
- `tools/discussion_reply_scan.py`: the `editor-readback` row reads the script's retained output and
  refuses a code view, an unidentified view, or a missing one. Its test shows a code-view readback
  whose text equals the build is refused, and a formatted-view readback with matching text is clean.
- `tools/discussion_post_scan.py`: a readback taken at the loaded-box stop is retained in the newest
  render pass and graded by the same view rule, with the same pair of tests.
- `skills/discussion-reply/SKILL.md` step 4 and `skills/discussion-post/SKILL.md` step 8: the
  readback paragraphs point at the script and its retained file; `discussion-post`'s load sentence
  states the switch back.
- `skills/_shared/reference/canvas-editor-calibration.json`: the first agent run under this record
  adds a dated observation of the threaded Composer's switch back to the rich editor, with the editor
  id, rather than relying on the 2026-09-08 entry's unresolved surface.

The build edits the same `canvas-editor.md` paragraphs that ADR 0331's build edited; read the
landed text rather than this record's quotations of it.

## What this record does not reach

- **What Canvas stores from a raw-textarea submit.** No run will submit to find out.
- **That the click happened in the formatted view.** The readback is taken at the stop; the run
  changes nothing in the Composer between it and the click, and a later change means a new readback.
- **The switch back on the threaded Composer.** It has been exercised only on a Composer whose
  surface was not recorded.
- **Peer-review comments and file uploads.** They are not Composers and keep their own routes under
  ADR 0204 and ADR 0331.
