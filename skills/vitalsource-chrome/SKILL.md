---
name: vitalsource-chrome
description: Navigate and completely read authenticated VitalSource Bookshelf chapters through Codex Chrome. Use when a task mentions VitalSource, Bookshelf, a live eText, or a textbook chapter available only in the authenticated reader.
---

# VitalSource Chrome

Read VitalSource the way Claude in Chrome does: navigate before the debugger remains attached, let the Jigsaw reader settle, and treat screenshots as the reading surface. The installer makes Codex release and reacquire its debugger at those boundaries automatically.

## 1. Prepare Codex Chrome

Run `python skills/vitalsource-chrome/scripts/patch_codex_chrome.py` from the repository root after installation and after a Codex Chrome update. It patches both installed locations when present:

- the bundled Chrome plugin cache under `.codex/plugins/cache/`;
- the active desktop browser runtime under `OpenAI/Codex/runtimes/cua_node/`.

The patch is fail-closed. It changes only reviewed browser-service seams, preserves the first pre-patch bundle beside each target as `.vitalsource-original`, and rejects an unknown or partial bundle. It does not enable full CDP or authorize raw `Target.*` commands.

Restart Codex after the script reports `patched`. A running browser service cannot load changed code in place.

## 2. Open and verify the reader

1. Start a fresh Chrome task and navigate directly to the authenticated VitalSource reader URL.
2. Allow four seconds for the reader to initialize before the first screenshot.
3. Require visible book content, a printed page number, and the expected title. A shell plus five-dot spinner is not a readable page.
4. Read the pane from screenshots. Do not use extracted page text, accessibility trees, DOM snapshots, or frame locators as evidence; VitalSource may expose the shell while omitting or breaking the Jigsaw pane.
5. Use ordinary screenshot-grounded click, type, and scroll actions. The patch releases the debugger before each discrete VitalSource action and reacquires it only for that action, matching Claude's working lifecycle.

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

## 5. Recover without inventing a read

Stop immediately if the pane returns to a five-dot spinner, disappears, or shows `chrome-error://chromewebdata`.

1. Record the outer URL and last verified printed page.
2. Open a new reader tab at the canonical book URL.
3. Wait four seconds and require one stable rendered page.
4. Resume from the last verified page, repeating its screenshot to restore overlap.

Do not use a stuck tab as evidence, repeatedly click while it loads, or substitute a publisher preview, search fragment, contents entry, or opening page for the authenticated chapter.
