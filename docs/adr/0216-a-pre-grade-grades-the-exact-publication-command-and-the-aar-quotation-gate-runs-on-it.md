# A pre-grade grades the exact publication command and the AAR quotation gate runs on it

[#1026](https://github.com/mshamblin5150-code/clinical-skills/issues/1026) was filed from one
`practicum-case-study` run's after-action review: fourteen AAR-sourced bodies under
`aar/publications/` pre-graded clean with `python tools/tracker_publish_hook.py --text <path>`, and
one of them was refused when it was published, by the AAR quotation gate. The manual mode had never
run that gate and its report did not say so.

Grilled 2026-09-13 to an empty frontier. **Ten rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. The ticket was widened twice during the session: once
to type `Publication`'s source, and once to give the manual mode the route and record it lacked.
The tracker sweep that normally closes a grilling was **limited to the tickets this record moves**, by
the clinician's word for that day only; it is not a precedent.

## Measured before ruling, at `8b633be`

**The gap is the discarded path.** `main` in `tools/tracker_publish_hook.py` builds the manual
publication as `Publication("body", text, "body-file")`. Its source is the literal label, so
`_aar_run_directory` never sees `aar/publications/`, and `aar_quotation_analysis` is called only from
`handle`. `shell_reader.candidate_file` resolves a path against the working directory, and a manual
run is started by the shell, so the run directory was always recoverable there.

**`body-file` is stored as a source value in exactly one place**, that manual constructor. Hook-route
body files already carry their real path; `inline` and `inline heredoc` name publications that have
no file; `_source_label` maps any path back to the word `body-file` for the report.

**The hook route's quotation line reads `0` for publications the gate never compared.** With no
finding, `aar_quotation_analysis` prints `AAR quotation gate: 0 copied private-run spans` whether the
publication was an AAR body with nothing copied or not an AAR body at all.

**Two more rules depend on what `--text` cannot know.** `analyze` grades the Filed-from rule against a
route and a current body, and branch scope's in-flight trigger against the record's labels. The manual
mode passes neither, and prints both as not graded or context-blind.

**Every remedy naming `--text` follows a command-shape refusal.** The seven pointers in
`UNREADABLE_REMEDIES` follow a missing file, an unrooted path, or an inline value exposed to
expansion; a mode that reads a file and not a command reproduces none of them.

**How a command can reach a manual check, measured with `extract` and `_loose_publish_route`.** Four
transports were classified, with a real `gh issue create --title 'T' --body-file /c/x/body.md` as the
control. *Had either classifier failed to recognize a publication, the control would have come back
unrecognized; it came back `('issue', 'create')` from both.*

| transport | Bash route | PowerShell loose classifier |
| --- | --- | --- |
| `--command '<cmd>'` with nested `'\''` escapes | not a publication | not a publication |
| `--command "<cmd>"` | not a publication | not a publication |
| `--command -` with a heredoc on stdin | not a publication | **refused as a publication** |
| `--command-file <path>` | not a publication | not a publication |

**The hook writes its marker on every run of `handle`**, and the bare `phi_scan.py` commit path states
that marker's age as the evidence the hook fires in this checkout.

## Ruling 1. The AAR quotation gate runs on a pre-grade

A **pre-grade** runs `aar_quotation_analysis` over the same publications the hook route does, so a
body under `<run>/aar/publications/` is compared with its run whichever route grades it.

**Declaring the gap instead is declined.** The clinician's standing preference is to declare coverage
rather than widen an instrument, and it binds where the instrument cannot see. This one could: the
path was on the command line and was thrown away. A declaration would also leave every refusal remedy
sending its reader to a check that says in writing it cannot grade what refused them.

## Ruling 2. The quotation line states its population on both routes

`aar_quotation_analysis` counts the publications it compared. It prints
`AAR quotation gate: <n> copied private-run span(s) across <m> AAR publication(s)` when at least one
publication is an AAR body, and `AAR quotation gate: not applicable -- no publication under
aar/publications/` when none is. The deny finding and its count are unchanged. One function prints
the line for both routes.

**Changing the manual route alone is declined.** Two routes printing different lines about the same
file is [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s shape: one
implementation, two answers.

## Ruling 3. A copied span exits 1 on a pre-grade

The gate's finding keeps its `deny` posture, so a pre-grade that finds one exits 1 with no special
case. `not applicable` is not a finding.

**An advisory exit 0 is declined.** A pre-grade that exits 0 on a body the publish refuses is the
defect #1026 was filed over.

## Ruling 4. `Publication` holds an origin and a path, never a label standing for a path

`Publication.source` is replaced by two fields. `origin` is one of `inline`, `inline heredoc` and
`body-file`. `path` is a resolved `Path` exactly when `origin` is `body-file`, and `None` otherwise,
including for a `gh api --input` publication read from a file, whose origin is `body-file`.
Construction refuses a value outside the vocabulary and any origin-and-path mismatch, raising
`ValueError` naming the field. `_aar_run_directory` reads `path`; the report label reads `origin`, so
no path reaches hook output. `_source_label` is deleted. `resolved_against` and `reconstructed_path`
are unchanged.

This is [ADR 0180](0180-a-threshold-root-is-always-a-path-and-a-missing-root-is-one-that-does-not-exist.md)
one module over: a field standing for a real thing holds the real thing, and the object refuses
anything else when it is built.

**Fixing only the manual constructor is declined**, and so is filing the split apart. The defect is
the path-or-label shape itself, and a minimal fix leaves the next path-consuming caller open to it.
`Unreadable.source` is outside this ruling: no gate consumes it as a path.

## Ruling 5. The ticket widens to the route and the record

The pre-grade grades the route-dependent and record-dependent rules too: the Filed-from rule on issue
create and edit, and branch scope's in-flight trigger.

**Leaving them declared is declined.** Both already printed that they did not run, which is honest;
the clinician chose parity over a declared remainder.

## Ruling 6. `--command-file` grades the exact command through the hook's own analysis

`python tools/tracker_publish_hook.py --command-file <path>` reads the file as UTF-8 and grades its
text as a Bash tool command. The body of `handle` that follows its tool check is lifted into one
function both routes call: `extract`, the tracker readback, every `analyze` gate, the missing-body
analysis on issue create, and the AAR quotation gate. The hook route wraps that result in its marker
write and JSON response; the pre-grade prints the report lines and never the command's text.

Exit status: **0** when no refusing finding exists; **1** when one does; **2** for every way of not
having scanned — an unreadable command file, a publication the hook would refuse as unreadable, and an
analysis failure the hook would report as a hook failure.

**The network is the hook's.** A pre-grade fetches `origin/main` and makes the one batched readback,
and a failed fetch prints the same context-blind line with the same advisory posture, not a refusal.

**Separate `--route` and `--issue` flags are declined.** They would be a second reading of what the
command does, beside the one `extract` makes of the real command, and could disagree with it; that is
#1026's defect one level up.

## Ruling 7. A pre-grade writes no marker

Only the hook route writes `scratch/runs/tracker-publish-hook.json`. The marker keeps one meaning:
Claude Code invoked the hook on a publication.

**Writing it from a pre-grade is declined.** A checkout whose hook never registered — which
`NOT_REACHED` names under workspace trust — would show a fresh marker from a hand-run check, hiding the
one failure the marker exists to expose.

## Ruling 8. The command arrives by file only

There is no inline `--command`. The file holds the bytes that will be run.

**The inline forms are declined** because a publication command already contains single quotes, so
wrapping it in one needs `'\''` escapes, and a wrong escape grades a different string and passes.
**The stdin heredoc is declined** on the measurement above: the loose classifier refuses it as a
publication.

## Ruling 9. `--text` is retired

`--command-file` is the only manual mode. Every pointer in `UNREADABLE_REMEDIES` names
`python tools/tracker_publish_hook.py --command-file <path>`, and `NOT_REACHED`'s
`manual text mode has no issue publication route` row is removed, since no manual mode lacks a route.

**Keeping `--text` beside `--command-file` is declined.** Two manual checks, one of which always passes
what the hook refuses, is #218's shape again, and it is
[#781](https://github.com/mshamblin5150-code/clinical-skills/issues/781)'s *advice to use the weaker
pre-flight* sitting next to the stronger one.

This supersedes [ADR 0179](0179-a-body-file-absent-when-the-hook-ran-is-one-condition-and-its-remedy-names-both-causes.md)
ruling 2's retained `--text <path>` pointer, and the `--text` working-directory bullet in
[ADR 0137](0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md)'s
*What the build must not trip over*. Each carries a dated note pointing here.

## Ruling 10. A command file naming no publication route exits 2

Where `extract` recognizes no publication route, the pre-grade prints
`tracker pre-publish: NOT SCANNED -- no publication route recognized in the command file` and exits 2.
The hook route's silent allow for such a command is unchanged.

**Exit 0 with a note is declined.** A typo in `gh issue create`, an empty file or the wrong file would
otherwise read as a clean check of a publication nobody read.

## What the build corrects in place

Descriptions of the manual mode that are facts about behavior this record changes are corrected where
they stand, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, in the same change that changes the behavior:
[ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md)'s two descriptions of the
manual mode grading no route, [ADR 0177](0177-both-publish-routes-grade-a-body-through-one-grader-and-a-lost-body-refuses.md)'s
sentence that `--text` reaches the same body grader, and CLAUDE.md's *Tracker publish hook* section.

## What the build verifies

- A body under a synthetic `<run>/aar/publications/` that copies an 80-character run span, published
  by a command in a command file, exits 1 from `--command-file` and is denied through `handle`, with
  the same quotation line from both. *Had the pre-grade not run the gate, it would exit 0 and print no
  quotation line.*
- The same command with the body moved outside `aar/publications/` prints `not applicable` on both
  routes and exits 0.
- A command file carrying `gh issue creat` exits 2 with the ruling 10 line; an empty file exits 2.
- A command file carrying a relative `--body-file` with no `cd` exits 2 and names the same unreadable
  kind the hook route names.
- An issue-create command whose body lacks a required Filed-from line exits 1 from `--command-file`
  and is denied through `handle`.
- A pre-grade leaves the marker file's bytes and modification time unchanged.
- Building a `Publication` with `origin="body-file"` and no path, or with a path and another origin,
  or with an origin outside the vocabulary, raises `ValueError` naming the field.
- `--text` exits 2 as unsupported arguments, and no remedy string contains `--text`.
- The suite, run through `python tools/suite.py`, is green.

## What this record does not settle

**Chained publications in one command** stay
[#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107)'s. A pre-grade inherits
whatever the hook route grades of such a command, and adds no divergence of its own.

**A paraphrase of run material** still passes the quotation gate, on `NOT_REACHED`'s existing row.

**Whether a file `gh` reads is the file the pre-grade read** is the existing rewritten-after-scan row
and is unchanged; a pre-grade is one more moment before publication at which the file can change.
