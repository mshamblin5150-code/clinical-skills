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

The dated observations behind the surface discriminator, route, and known limits are in
[`canvas-editor-calibration.json`](canvas-editor-calibration.json). They cover one institution,
Canvas instance, theme, account, and measurement date; they do not establish a stable Canvas-wide
contract.
