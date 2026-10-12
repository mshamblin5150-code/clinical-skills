# Canvas composer load route

Read this sheet before every Canvas save, submit, or reply click, including a plain Peer-review
comment and a file-upload submission. The calling skill owns the artifact and surface; this sheet
owns the loaded-box stop and the Composer load route when that surface is a Composer.

## File upload access

A worktree session can read only folders it has been granted. If the browser upload tool refuses
the approved file's folder (the owning checkout's `output/`), ask the clinician to run
`/add-dir <that folder>`, then retry the approved path. Never copy the approved file anywhere else
to upload it.

## Stop at the loaded box

Load the contribution, read it back, and leave it loaded and unsubmitted. Name the Chrome tab,
say the box is loaded and unsubmitted, and name the **Composer view** in the readback verdict:
"loaded in the formatted view, unsubmitted, in tab '<tab title>'; readback matches", or the exact
view and difference. A non-Composer surface keeps its own readback verdict. Take a screenshot only when the clinician asks. Click only on his **Posting go-ahead**
given after he has looked. The content go-ahead authorizes loading and never covers the click.
Record the Posting go-ahead before recording the posting route. If recording it reports a changed
project-context notice, show that notice here and renew approval under ADR 0328 before clicking.
A requested text change creates a new fingerprint: show the complete changed text and obtain a
new content go-ahead before reloading and taking this stop again.

## Name the non-Composer surface

ADR 0204 classifies the peer-review comment as a non-Composer surface. Its 2026-09-12 Bluefield
observation found that surface accepted plain text rather than the HTML build and load routes below.
Build the plain contribution with `python tools/post_text.py <source.md> <plain.txt>`; a Peer
critique uses `critique.md` and `critique.txt`. Load that build, then its posted reading compares
Canvas's stored comment text with the build.
The 2026-09-12 Bluefield observation found the legacy peer-review page's visible `&amp;` was display
behavior rather than evidence that the stored comment differed. That four-instrument observation
and its limits are in the calibration record; it does not establish current behavior elsewhere.

## Identify the composer

Read the live TinyMCE editor id before loading anything:

- `message-body-root` identifies the topic-level Composer for an **Initial post**.
- `message-body-<digits>` identifies a threaded Composer for a **Reply**. The numeric value's
  relationship to the entry id is unmeasured and is not part of the discriminator.

Canvas labels both controls *Reply*. Record the surface by editor id; a generic reading of a
*reply box* does not distinguish them. If the id matches neither form, report that the Composer
could not be identified rather than assigning it to either surface.

## Choose one load route before loading

Choose the first route the live Composer supports, declare that route and its cost at the calling
skill's existing clinician gate, and keep it for this load:

1. **Raw HTML:** use the `data-btn-id="rce-edit-btn"` control, then confirm the resulting editor is
   the plain textarea whose status control offers *Switch to pretty HTML Editor*. The click alone
   is not confirmation because Canvas remembers the account's last-used Composer view. Load the built
   HTML into that textarea, then switch back to the formatted view before reading back or stopping.
2. **Content interface:** use `tinymce.get(<editor-id>).setContent(...)` only when the identified
   live instance exposes callable `setContent` and `getContent`. After `setContent`, make the editor
   register the change with one keystroke at the end of the opening line, never after a URL; that
   keystroke can autolink the token immediately before it.
3. **Typing:** type into the rich editor. Omit working comments, apply the authored formatting with
   the editor controls, and make every reference URL a link with the link control.

A non-clean readback stops at the clinician. It never causes the agent to switch routes or retry
the load on its own.

## Read back the loaded contribution

Run this fixed page script verbatim after the switch back. Supply the identified editor id and a
live selector for its enclosing Composer: exactly one element containing that editor's source
textarea, rich editor, and status control, with no other Composer inside it. These are page inputs,
not edits to the script. Retain the returned JSON string unedited in the calling skill's readback
file. It reads the Composer view and serialized contribution together; a code-view, unidentified,
missing-view, or differently shaped readback is not clean even when its text equals the build.

```javascript
(editorId, composerSelector) => {
  const result = {editor_id: editorId, view: "unidentified", html: ""};
  const roots = document.querySelectorAll(composerSelector);
  if (roots.length !== 1 || !/^message-body-(root|\d+)$/.test(editorId))
    return JSON.stringify(result);
  const root = roots[0];
  const source = document.getElementById(editorId);
  const sources = root.querySelectorAll('textarea[id^="message-body-"]');
  if (!source || !root.contains(source) || sources.length !== 1)
    return JSON.stringify(result);
  const visible = element => {
    if (!element || !element.getClientRects().length) return false;
    for (let node = element; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden" || node.hidden)
        return false;
    }
    return true;
  };
  const textareaVisible = [...root.querySelectorAll("textarea")].some(visible);
  const codeMirrorPresent = !!root.querySelector(".CodeMirror, .cm-editor");
  const toolbarVisible = [...root.querySelectorAll(".tox-toolbar, .tox-toolbar__primary, .mce-toolbar")].some(visible);
  const status = [...root.querySelectorAll("button, [role=button]")]
    .filter(visible).map(node => [node.textContent, node.getAttribute("aria-label"), node.getAttribute("title")].filter(Boolean).join(" "))
    .join(" ");
  if (!textareaVisible && !codeMirrorPresent && toolbarVisible)
    result.view = "formatted";
  else if (textareaVisible && !codeMirrorPresent && !toolbarVisible && /Switch to pretty HTML Editor/i.test(status))
    result.view = "raw";
  else if (codeMirrorPresent && !toolbarVisible)
    result.view = "pretty";
  const editor = window.tinymce?.get(editorId);
  const frame = document.getElementById(editorId + "_ifr");
  const body = typeof editor?.getBody === "function" ? editor.getBody()
    : (frame && root.contains(frame) ? frame.contentDocument?.body : null);
  result.html = typeof editor?.getContent === "function" ? editor.getContent()
    : (body ? body.innerHTML : "");
  if (typeof result.html !== "string" || (!editor && !body)) {
    result.view = "unidentified";
    result.html = "";
  }
  return JSON.stringify(result);
}
```

The graders require exactly the string fields `editor_id`, `view`, and `html`, with `view` equal
to `formatted`. They compare the serialized HTML with the build by paragraph and other visible
block text, ordered anchor destinations, and anchor count. Attribute order, insignificant
whitespace, and other serialization differences do not make the readback diverge.

The calling skill owns the retained file and the check. A clean pre-posting readback establishes
neither that the correct board's Composer was chosen nor that Canvas preserved the content after
posting; the posted reading remains the account of the board state. Change nothing in the Composer
between this readback and the click; a later change requires a new readback and loaded-box stop.
The first live run under ADR 0344 adds a dated observation of the threaded Composer's switch back,
with its editor id, to the calibration record below; the build alone supplies no such observation.

## Initial-post attachment fallback (only when the calling skill opts in)

After the recorded Posting go-ahead at the loaded-box stop, click **Reply** with the full
body loaded. Record the built HTML's byte count beside the observed outcome; the count never
predicts or chooses a route. Read the result on the page. Only a visible message-size refusal
triggers this fallback. Record the refusal's exact observed wording and ISO date. For acceptance,
an unfamiliar error, no response, or uncertainty, read the board for a created entry, report
what is there, and stop at the clinician. Do not retry or create a second entry on an uncertain
result. Do not match the refusal against a fixed string or a byte threshold.

If the signed bar requires substantive content in the post body itself, stop at the clinician:
an attached document under a pointer cannot satisfy that bar. Otherwise replace the refused
body with this fixed pointer, substituting only the artifact title and attached filename:

```text
<artifact title>

Canvas refused the full text inline for message size. The complete submission is attached as <attachment filename>.
```

Attach the finished `.docx`. Run the same page script on the formatted pointer and retain its output in the newest render pass.
Read back the pointer's body text and the Composer's displayed
attachment filename and size. Show those readings and the visually checked document to the
clinician at the loaded-box stop and record a fresh **Posting go-ahead** before submitting this attached entry. The
authorization for the earlier full-body click does not cover it. After posting, apply
[Posted files](lms-attachments.md#posted-files) to identify and read the attachment. Write
`COMPOSER-OUTCOME: attachment`, `HTML-BYTES:`, `REFUSAL: <ISO date> - <observed wording>`, and
the shared section's `POSTED-FILE:` line in the posted reading before `/AAR` extracts it. An accepted
full-body entry instead records `COMPOSER-OUTCOME: inline` and `HTML-BYTES:`.

The dated observations behind the surface discriminator, route, and known limits are in
[`canvas-editor-calibration.json`](canvas-editor-calibration.json). They cover one institution,
Canvas instance, theme, account, and measurement date; they do not establish a stable Canvas-wide
contract.
