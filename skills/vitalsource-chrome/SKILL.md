---
name: vitalsource-chrome
description: Navigate and completely read authenticated VitalSource Bookshelf chapters. Use when a task mentions VitalSource, Bookshelf, a live eText, or a textbook chapter available only in the authenticated reader.
---

# VitalSource Chrome

`vitalsource-chrome` steps 2 through 5 bind every browser agent reading an authenticated VitalSource
chapter. Step 1 is Codex-specific preparation. Codex keeps one ordinary top-level debugger attachment, leaves OOPIF
auto-attachment disabled, uses ordinary navigation and command dispatch, lets Jigsaw XHTML remain
a document response, and treats screenshots as the reading surface. The dated
[reference lifecycle](reference/claude-in-chrome-lifecycle.json) records which Claude in Chrome
facts this patch copies; that record guides repairs and never decides whether a page was read.

## 1. Prepare Codex Chrome

Run `python skills/vitalsource-chrome/scripts/patch_codex_chrome.py` from the repository root after
installation and after a Codex Chrome update. It patches both installed locations when present:

- the bundled Chrome plugin cache under `.codex/plugins/cache/`;
- the active desktop browser runtime under `OpenAI/Codex/runtimes/cua_node/`.

The patch is fail-closed. It changes only reviewed browser-service seams, preserves the first
pre-patch bundle beside each target as `.vitalsource-original`, and rejects an unknown or partial
bundle. It does not enable full CDP or authorize raw `Target.*` commands. If the installed Claude in
Chrome extension version differs from the reference lifecycle, report the difference and continue;
the version is not a read gate.

Run the repository patcher, then run the personal plugin's patcher at
`~/.codex/plugins/cache/personal/vitalsource-chrome/scripts/patch_codex_chrome.py` against the same
live bundle, and record both statuses. Treat the result as an ordered comparison:

1. When the repository patcher reports `patched` or `already-patched`, refresh the personal plugin's
   `SKILL.md` and patcher from the repository. Keep only its declared transforms: the command path is
   plugin-relative and it has no repository `sourcing.md` link. Run the refreshed personal patcher
   again so any mutation from its former copy converges to the repository lifecycle.
2. When the repository patcher refuses and only the personal plugin's patcher reports
   `already-patched`, do not overwrite it: it holds a repair the repository lacks. Follow the repair
   route below so that fix lands first.
3. When both patchers refuse, follow the repair route below.

Restart Codex after either patcher reports `patched`. A running browser service cannot load changed
code in place. A personal installation and a prior successful session are insufficient evidence
that the current bundle works.

A refused repository patcher starts this route in order:

1. Attempt the read under `vitalsource-chrome` step 2's verification and record that the patcher refused. A changed
   bundle may contain an upstream fix, and the visible page is the only read gate.
2. If the page fails step 2, repair the patcher on a branch during this run. File a ticket whether
   the repair succeeds or fails, land a successful repair through a pull request, and obtain the
   clinician's go-ahead before applying it to the clinician's installed Codex. Verify the repair
   under step 2.
3. If repair fails or the clinician declines it, hand the chapter to a Claude session that follows
   steps 2 through 5.
4. If no Claude session is available, report an `unreadable source` and name every instrument tried.

## 2. Open and verify the reader

1. Start a fresh Chrome task and navigate directly to the authenticated VitalSource reader URL.
2. Allow four seconds for the reader to initialize before the first screenshot.
3. Require visible book content, a printed page number, and the expected title. A shell plus five-dot spinner is not a readable page.
4. Read the pane from screenshots. Do not use extracted page text, accessibility trees, DOM snapshots, or frame locators as evidence; VitalSource may expose the shell while omitting or breaking the Jigsaw pane.
5. Use ordinary screenshot-grounded click, type, and scroll actions. In Codex, the patch keeps the
   top-level debugger attachment stable, never enables OOPIF auto-attachment at the tab boundary,
   and classifies `application/xhtml+xml` as a document instead of a download so Jigsaw can load the
   chapter frame.

Coordinates expire after every scroll, resize, panel change, or navigation. Take a new screenshot before choosing the next target.

## 3. Find material without mistaking search for reading

Use the toolbar's **Search across book** control when a term can locate the relevant section:

1. open the search panel from a fresh screenshot;
2. enter one focused term or phrase and submit it;
3. wait four seconds and screenshot the result list;
4. click one result, wait for the destination, and require rendered page text plus its printed page number;
5. close or leave the panel only after the destination is stable.

A search count, snippet, contents entry, highlighted hit, or outer CFI is a locator. None is evidence that the destination page or chapter was read.

Use [sourcing.md](../_shared/reference/sourcing.md) to distinguish locators and discovery surfaces from readable primary material that can carry a claim.

## 4. Read a complete chapter

Treat a chapter as unread until every printed page from its first page through the page before the next chapter has been visibly traversed.

1. Establish the chapter's first printed page and the next chapter's first printed page from the live table of contents.
2. Screenshot the first page and record its heading and printed page number.
3. Move through the reading pane in measured increments. Wait two to three seconds after each scroll or page action, then screenshot the resulting viewport.
4. Preserve continuity by checking overlapping text, headings, printed page markers, and the outer CFI together. The CFI can change without advancing the printed page.
5. Continue until the next chapter marker is visibly reached. Record any unreadable or untraversed page explicitly; do not call the chapter complete.

For each requested chapter, retain the edition and ISBN when known, verified printed page range, every subsection encountered, page-bounded paraphrases relevant to the task, and any claim the chapter narrows or refutes. Do not retain long copyrighted extracts. Quote only the shortest decisive fragment.

**Two-reader code-set rebuild exception.** For a complete code-set rebuild under the maintainer's written AMA permission for internal database storage, a structural extraction may serve as one of two independent readers, but it is never evidence on its own. The other reader transcribes rendered-page screenshots, including printed-page layout; every disagreement is settled on that rendered destination page. The retained full transcription is authorized only by that written permission. Everywhere else, the screenshot-only evidence rule in step 2 and the no-long-extract rule above remain in force.

## 5. Recover without inventing a read

Stop immediately if the pane returns to a five-dot spinner, disappears, or shows `chrome-error://chromewebdata`.

1. Record the outer URL and last verified printed page.
2. Open a new reader tab at the canonical book URL.
3. Wait four seconds and require one stable rendered page.
4. Resume from the last verified page, repeating its screenshot to restore overlap.

Do not use a stuck tab as evidence, repeatedly click while it loads, or substitute a publisher preview, search fragment, contents entry, or opening page for the authenticated chapter.
