# Canvas composer load route

Read this sheet after a skill has established that authored bytes must enter a Canvas rich content
**Composer**. The calling skill owns whether its graded artifact uses a Composer; this sheet owns
how the finished contribution reaches it and how the loaded result is read back.

## Name the non-Composer surface

ADR 0204 classifies the peer-review comment as a non-Composer surface. Its 2026-09-12 Bluefield
observation found that surface accepted plain text rather than the HTML build and load routes below.
A Peer critique therefore loads an exact plain-text build with every character literal, then its
posted reading compares Canvas's stored comment text with that build.
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
   is not confirmation because Canvas remembers the account's last-used HTML mode. Load the built
   HTML into that textarea.
2. **Content interface:** use `tinymce.get(<editor-id>).setContent(...)` only when the identified
   live instance exposes callable `setContent` and `getContent`. After `setContent`, make the editor
   register the change with one keystroke at the end of the opening line, never after a URL; that
   keystroke can autolink the token immediately before it.
3. **Typing:** type into the rich editor. Omit working comments, apply the authored formatting with
   the editor controls, and make every reference URL a link with the link control.

A non-clean readback stops at the clinician. It never causes the agent to switch routes or retry
the load on its own.

## Read back the loaded contribution

Before posting, read the Composer's serialized HTML: the raw textarea value while the raw editor is
active; `getContent` from the identified TinyMCE instance on the content-interface route; or the
identified rich-editor body's serialized `innerHTML` on the typing route when `getContent` is
unavailable. Compare it with the built HTML by paragraph and other visible block text, and by the
ordered anchor destinations and anchor count. Attribute order, insignificant whitespace, and other
serialization differences do not make the readback diverge.

The calling skill owns where that serialized HTML is retained and which independent check grades
it. A clean pre-posting readback establishes neither that the correct Composer was chosen nor that
Canvas preserved the same content after posting; the posted reading remains the account
of the board state.

## Initial-post attachment fallback (only when the calling skill opts in)

After the calling skill's existing explicit submit authorization, click **Reply** with the full
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

Attach the finished `.docx`. Read back the pointer's body text and the Composer's displayed
attachment filename and size. Show those readings and the visually checked document to the
clinician and wait for a **fresh explicit authorization** to submit this attached entry. The
authorization for the earlier full-body click does not cover it. After posting, use the posted
entry's **own attachment link** to download the file into `<run-directory>/posted/<filename>`.
Keep that copy for the terminal grader's SHA-256 comparison with the local `.docx`; a copy from
the general files area does not establish what this entry carries. Write
`COMPOSER-OUTCOME: attachment`, `HTML-BYTES:`, `REFUSAL: <ISO date> - <observed wording>`, and
`ATTACHMENT: posted/<filename>` in the posted reading before `/AAR` extracts it. An accepted
full-body entry instead records `COMPOSER-OUTCOME: inline` and `HTML-BYTES:`.

The dated observations behind the surface discriminator, route, and known limits are in
[`canvas-editor-calibration.json`](canvas-editor-calibration.json). They cover one institution,
Canvas instance, theme, account, and measurement date; they do not establish a stable Canvas-wide
contract.
