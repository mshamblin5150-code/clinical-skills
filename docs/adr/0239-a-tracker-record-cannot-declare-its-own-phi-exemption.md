# A tracker record cannot declare its own phi exemption

[#1145](https://github.com/mshamblin5150-code/clinical-skills/issues/1145) found that
`tracker_publish_hook.analyze` grades a publication's title and body with `phi_scan.scan_text`,
which reads `phi-scan: synthetic` out of the text it is scanning, while `tracker_scan` passes
`scan_lines(..., True)` for every record that is not a file. Grilled 2026-09-15 against `8b4e44fa`;
the clinician ruled every point below on 2026-09-15. Nothing is built here; this is the record the
build reads.

## Measured before ruling

### The finding holds at this base

Re-derived in process at `8b4e44fa` with an empty corpus index. A body opening with the declaration on
its own line and carrying a date of birth, a Social Security number shape and a short date: `scan_text`
returned no rule, and `scan_lines(..., True)` returned `dob-with-date`, `ssn` and `us-short-date`. The
same body without the declaration returned those three rules from both. The control is what makes the
first result a finding rather than an artifact of the probe.

### The hook advises and does not prevent

#1145 calls the hook the only limb that prevents. It is not: every `phi:` finding the hook emits
carries the `advise` posture, and only a `deny` finding refuses a publication.
[ADR 0077](0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md)
ruling 5 made that posture deliberately, and names what advisory buys: a value goes up with a decision
recorded rather than unnoticed. **So the declaration does not unlock a block.** It turns a recorded
decision back into an unnoticed one. The defect stands on that smaller ground, and it is still standing
rule 1's own mechanism.

### The declaration is read near the top, not only on the first line

`declares_synthetic` searches the opening `PRAGMA_SEARCH_CHARS` window for the declaration alone on a
line. The ticket's title names the first line, which is one instance of the window.

### One caller reads the declaration from text nobody reviewed as a file

Outside tests, four sites decide the shape layer from the text itself: `phi_scan`'s tracked-file walk
through `scan_text`, its staged scan through `declares_synthetic`, `tracker_scan`'s branch for a record
that is a file, and `tracker_publish_hook.analyze`. The first three read committed or staged files. Only
the hook reads tracker titles and bodies. This answers #1145's third question by derivation rather than
by ruling.

## Ruled 2026-09-15

### 1. The publish hook never reads the declaration from tracker text

`analyze` grades every title and body with `phi_scan.scan_lines(text, field, index, True)`, matching
`tracker_scan` for a record that is not a file. PHI findings keep the `advise` posture, and ADR 0077
ruling 5 is unchanged. **Declaring the behavior as a limit was declined**: `scan_lines`'s own docstring
already states that an issue body may not declare the exemption, and under `CONTEXT.md`'s **Declared
limit** a mechanism doing the opposite of its own documentation is a defect and not a boundary.

### 2. A declaration inside a tracker record is not itself a finding

No row reports its presence and nothing refuses on it. After ruling 1 the declaration switches nothing
off on this route, so the shape rows already report everything a body carries. **Refusing it was
declined**: the records most likely to carry it are the ones that discuss it, #1145 and this record
among them, and the own-line rule matches a line inside a fenced block, so a refuser blocks correct
records and protects nothing. **An advisory row was declined**: it reports the presence of a string
that does nothing. `declares_synthetic`'s own docstring guards against accidents rather than
adversaries, and an evasion reading was the only case for either stronger form.

### 3. `scan_text` is renamed `scan_file_text`, and a hook test pins ruling 1

The name carries the unit the exemption belongs to, so the author of the next caller reads the
contract where the call is written. The remaining production callers are `phi_scan`'s tracked-file
walk and `tracker_scan`'s file branch; test callers move with them. A regression test drives the hook
with a body and the same body plus the declaration on its own line, and asserts the PHI rows are
identical: #1145's own control, kept. **A walk asserting the function is called only from a hand-kept
list of file walkers was declined**: it is another hand-kept list, it is blind to a call reached by
indirection, and it is a floor on the shapes in the tree rather than a guarantee.
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
records the same trap on another function, `grade_text`, as what a rebuild reaches for first because it
exists and takes a string.

## What this changes in earlier records

[ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
names this finding under *What none of this reaches* as filed for a ruling. It gains a dated correction
in place pointing here. ADRs 0104 and 0188 cite `scan_text` by its old name; they record what was true
when they were written and are not renamed. `CLAUDE.md`'s *Tracker scan* section says `scan_lines` was
split out of `scan_text`; that sentence moves with the rename.

## Taken as conventions, not ruled

The test's name and whether it drives `analyze` or the hook boundary are the builder's. The wording of
the renamed function's docstring, and whether `scan_lines`'s docstring gains a sentence naming the hook
as a caller, are the builder's, on ADR 0138's assignment of wording to the build.

## What this does not reach

**The direct-writer entry point.** `authorize_issue_body` grades no PHI at all. That is already declared
in `implementation_map.DECLARED_LIMITS`, and the declaration plays no part in it.

**A commit message before it is pushed.** No local check reads one for PHI; `tracker_scan --commits`
grades it afterwards with the shape layer on.

**A publication that never reaches the hook**, and GitHub's retained pre-edit revisions: the routes ADR
0083 already named.

**Correction, 2026-09-15:** the direct-writer paragraph above was written against `8b4e44fa` and was
overtaken the same day by
[ADR 0240](0240-the-map-s-direct-writer-grades-through-analyze-and-runs-no-readback.md) on
[#1148](https://github.com/mshamblin5150-code/clinical-skills/issues/1148), which rules that
`authorize_issue_body` grades through `analyze`. Once both builds land, the direct writer grades PHI
and inherits ruling 1, so it ignores the declaration too, and neither build waits on the other. The
narrowing of `implementation_map.DECLARED_LIMITS` belongs to #1148's build. The rulings above are
unchanged.
