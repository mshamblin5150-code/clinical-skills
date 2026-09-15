# VitalSource reads bind every browser agent, and a Codex patch copies a recorded Claude lifecycle

[#1261](https://github.com/mshamblin5150-code/clinical-skills/issues/1261) asked to route Codex
coursework reads of authenticated VitalSource through `vitalsource-chrome`, and was widened to land
the only working copy of the Codex Chrome patcher. Grilled 2026-09-15 against `dc038b5a`; the
clinician ruled every point below on the same day. Nothing is built here; this is the record the
build reads.

## Measured before ruling

### The working patcher is not on `main`

`main`'s `skills/vitalsource-chrome/scripts/patch_codex_chrome.py` refuses the clinician's installed
Codex Chrome bundle. Snapshot commit `1a20d9215cfe6cee1c324b15ad4e4a90b6f80f40`, reachable only from a
local `refs/codex/snapshots/` ref, reports that bundle `already-patched`, and its output from the
preserved `.vitalsource-original` equals the installed bundle. #1261's body carries that table. No
commit after `39d1bece` touches the skill, its patcher test, `sourcing.md`, or the AGENTS.md
dependency paragraph, so the measurement still describes `main`.

### The personal plugin is a second, already divergent copy

`~/.codex/config.toml` enables `vitalsource-chrome@personal`. That plugin registers a skill and a
scripts folder and no hook, so it runs nothing unprompted. Its patcher differs from the snapshot's
only in the quoting of two string literals. Its skill differs structurally: unnumbered steps, no
`sourcing.md` link, and a patcher path relative to the plugin. A Codex session therefore loads two
skills named `vitalsource-chrome`; which one it follows on the collision was not measured.

### The Claude lifecycle the patch copies was read, never watched

The Codex session that wrote the patch read the installed Claude in Chrome extension, id
`fcoeoabgfenejglbffodgkkbkcdhcgfn`, version `1.0.93`, and Claude Code transcripts that record tool
calls but no debugger events. It never observed Claude's debugger while Claude read VitalSource, and
its own request for a live Claude run went unanswered. Re-counted against the installed `1.0.93`
bundles: `chrome.debugger.attach` 2, an `idle-20s` detach guard present, `setAutoAttach` 0,
`Page.navigate` 0, `Fetch.enable` 0.

So the copied facts are of two kinds. One top-level attachment per tool run and ordinary tab
navigation are **backed by code**. Frame auto-attachment left off and XHTML left a document response
are **inferred from absence**. The XHTML defect itself was observed only in Codex's browser.

`main`'s skill says the patch "releases the debugger before each discrete VitalSource action and
reacquires it", matching Claude. That description was inferred from tool-call order seconds before
the code read that contradicts it, and no observation ever supported it. It is the drift this record
exists to stop recurring.

### Only step 1 is Codex-specific

Steps 2 through 5 of `vitalsource-chrome` are the reading standard: a visible page with its printed
number and title, search as a locator, complete printed-page traversal, and recovery. `icd10-cpt`
already routes every agent to the skill for partial-set CPT and HCPCS misses, while the AGENTS.md
index row and the skill's description say "through Codex Chrome".

## Ruled 2026-09-15

### 1. A refused patcher starts an ordered route, not a stop

When the patcher refuses, a Codex consumer first attempts the read under step 2's verification,
because a refusal means the bundle changed and the change may be an upstream fix; a blocked page
fails step 2 visibly and cannot yield a false read. A page that passes is a read, and the record
states the patcher refused. If step 2 fails, the consumer repairs the patcher inside the run: on a
branch, applied to the clinician's installed Codex only after his go-ahead, with the change landing
through a pull request and a ticket filed either way. If the repair fails or is declined, the chapter
is handed to a Claude session reading through Claude in Chrome. With no such session, the chapter is
an **unreadable source** naming every instrument tried.

**Stopping at the refusal** was declined: it needs an exception to
[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md)'s second-instrument
rule. **Handing off at once** was declined: Codex cannot launch Claude, and the week Codex is used is
often the week Claude's usage is spent. **Repairing without a read until the pull request merges**
was declined: the read's evidence is the verified page, not the patch's review state, and the
clinician's go-ahead stands in for review of what touches his installation. The AGENTS.md sentence
the ticket dropped returns in that form.

### 2. The skill binds every browser agent

Steps 2 through 5 bind any agent reading an authenticated VitalSource chapter. Step 1 is Codex's
preparation and carries ruling 1's route. The AGENTS.md index row and the skill's description stop
saying "through Codex Chrome", and `sourcing.md` points every consumer at the skill, with the patcher
applying only to Codex. **Keeping the skill Codex-only** was declined: a handoff preserves the
standard only if the receiving session reads by the same written rules, and a second statement of
the standard in `sourcing.md` would drift from the skill.

### 3. Page verification gates a read; a recorded Claude lifecycle guides a repair

Step 2's verification is the only gate on a read. A dated **reference lifecycle** records each
Claude in Chrome fact the patcher copies, with the extension version, the instrument, and whether
the fact is backed by code, inferred from absence, or observed live. Each patcher seam names the
fact it copies, and a test asserts the seam set and the record agree. The false "releases the
debugger" description on `main` is corrected. **Dropping the parity claim** was declined: a repair
needs a dated reference, and an unrecorded "the way Claude does it" is how the false description
arose. **Letting the record gate a read** was declined: a stale record would refuse a page that
visibly passes.

### 4. The personal plugin stays, as a derived copy

The repository copy is the source. The plugin is derived from it for use outside the repository,
differing only by declared transforms: the patcher path is plugin-relative, and there is no
`sourcing.md`. The clinician authorized Codex to rewrite the plugin's skill and patcher files; that
authorization does not reach `~/.codex/config.toml`. **Retiring the plugin** was declined because
the clinician will use the skill outside this repository. **A thin pointer** was not taken: the
plugin must work where the repository is absent.

### 5. Codex refreshes the plugin at every step 1, keyed on the patchers' statuses

Each time a Codex session prepares Codex Chrome in the repository, it runs both patchers against the
live bundle. When the repository patcher reports `already-patched`, the plugin is refreshed from the
repository. When only the plugin's patcher does, the plugin holds a fix the repository lacks and is
not overwritten; the fix lands through ruling 1's repair path first. When both refuse, ruling 1's
repair runs, and the refresh follows it. **Refreshing only as a build's last step** was declined: a
fix merged from a Claude session has no Codex builder to refresh the plugin, and nothing would check
between builds. The plugin is current only once a Codex session has prepared Chrome in the
repository after a merge.

### 6. The record starts as a code read and gains one live observation

The record opens as the `1.0.93` code read, with its two inferred facts marked and a declared limit
that Claude's live lifecycle was never observed. One maintainer-run calibration then watches the
extension's attach and detach calls while a Claude session reads a VitalSource chapter, settling or
overturning the inferred facts, on
[ADR 0008](0008-word-is-a-one-time-calibration-instrument.md)'s one-time-instrument pattern. After
it, a changed extension version prompts a code re-read, and a live retake happens only when the
re-read disagrees with the record. Step 1 reports an installed extension version that differs from
the record's and refuses nothing. **A code read alone** was declined: an inferred fact recorded as
Claude's behavior is the defect this record answers. **A live retake at every version** was declined
as a standing cost on the clinician's browser that a disagreeing code read already triggers.

### 7. Two pull requests under #1261

The first lands the snapshot's patcher, test, skill and AGENTS.md changes re-derived against `main`,
rulings 1 through 5, and the code-read record with its declared limit. The second adds the live
calibration and removes the limit. The ticket stays open between them. **Holding the patcher for the
calibration** was declined: the working patcher exists only in a local ref and a plugin folder, and
the calibration needs the clinician's browser at a time of his choosing. **Filing the calibration
separately** was declined because the record is not correct without it.

## Taken as conventions, not ruled

- The record's path, file format and field names are the build's.
- The repair's ticket is filed by the session that attempted the repair.
- The step 1 comparison, the repair's live verification and the Claude handoff each open their own
  tab, under [ADR 0235](0235-a-browser-tab-is-a-private-output-location-and-a-page-action-naming-none-is-refused.md)
  ruling 6; none reuses a tab another pass opened.
- Reporting the XHTML block to OpenAI is worth doing and changes nothing here.

## Consequences

- `skills/vitalsource-chrome/SKILL.md` gains the ruling 1 route and ruling 5 refresh in step 1,
  states that steps 2 through 5 bind every browser agent, and names the reference lifecycle.
- `skills/_shared/reference/sourcing.md` gains a pointer section for every consumer.
- `AGENTS.md`'s index row and dependency paragraph are rewritten to rulings 1 and 2.
- `tools/test_vitalsource_chrome_patch.py` gains the seam-to-record agreement.
- `CONTEXT.md` gains **Reference lifecycle**.
- After the first merge, #1261 moves to `ready-for-human` for the calibration, and the builder
  restores `in flight`, which a `Part of` binding removes.

## What this does not reach

**Which duplicate skill a Codex session follows.** Unmeasured; ruling 5 makes the two copies agree
rather than deciding the collision.

**A plugin used before any Codex session prepares Chrome in the repository after a merge**, which
still holds the previous fix.

**The safety of an unmerged repair.** The patcher's tests drive synthetic seam strings, so nothing
mechanical shows that a patch against a new real bundle leaves full CDP and raw `Target.*` commands
disabled; the clinician's go-ahead is the only gate until review.

**Claude's lifecycle between version changes**, where a change to its code without a new version
folder would pass unnoticed.
