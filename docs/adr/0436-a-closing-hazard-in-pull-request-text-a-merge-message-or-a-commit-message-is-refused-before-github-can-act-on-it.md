# A closing hazard in pull request text, a merge message, or a commit message is refused before GitHub can act on it

**Measured at:** 0ee4d850268bd7276b40e6d9cac0c76ea630c8ea

[#1916](https://github.com/mshamblin5150-code/clinical-skills/issues/1916) was filed from the
grilling of [#1879](https://github.com/mshamblin5150-code/clinical-skills/issues/1879), 2026-10-19.
PR #1915's body carried a closing keyword inside a sentence about #1879's grilling, GitHub read it as
an instruction, and the merge closed #1879 while it still carried the `grilling` label. It was
reopened by hand. Grilled 2026-10-19 against `main` at the commit above, where the freshness gate
read `FRESH`. The clinician ruled every point below in that session, one question at a time.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The instrument exists and recognizes the shape.** `tools/closing_keyword_scan.py`, given a body
whose sentence puts a closing keyword directly before a ticket reference, exits 1 and names the
line; given `Closes #N` alone on its line, it exits 0. Re-derived on synthetic text at the commit
above. Its grammar is [ADR 0073](0073-the-closing-scan-grades-the-measured-github-grammar-plus-a-declared-margin.md)'s
live measurement of what GitHub acts on.

**The pre-publication hook never calls it.** Neither `tools/tracker_publish_hook.py` nor
`tools/command_reader.py` names `closing_keyword_scan`. The hook graded the `gh pr create` that
opened PR #1915 and reported no finding.

**The hook does not model a merge.** `command_reader.PUBLISH_ROUTES` holds issue create, comment,
edit and close, pull-request create, comment, edit and review, and `api`. `gh pr merge` is not among
them: driven through the hook's `--command-file` mode, `gh pr merge 5 --merge --body x` reports no
publication route recognized. `gh pr merge` sets the merge commit's subject with `-t`/`--subject`
and its body with `-b`/`--body` or `-F`/`--body-file`, and that commit lands on `main`, which is a
surface GitHub scans. The REST merge endpoint, `PUT repos/{owner}/{repo}/pulls/{n}/merge`, is today
an unclassified API endpoint that the reader does not grade.

**The commit-message check warns by inheritance.** `tools/hooks/commit-msg` runs the closing scan
with `|| true`, and its comment says it does so "on the existing commit-msg ruling". That ruling was
made for spelling, where a misspelling was judged not worth refusing a commit over. No ruling
weighed it for a closing hazard, although the recorded instance behind the scanner,
[#183](https://github.com/mshamblin5150-code/clinical-skills/issues/183), was a commit message.

**CI could not have saved it.** PR #1915 was created at 16:24:45Z and merged at 16:24:55Z; #1879's
close event is 16:24:57Z and its reopen 16:25:56Z. `gh pr view 1915 --json closingIssuesReferences`
prints `[1879]`. The pull request's CI ran about fifteen minutes, so every check reported after the
merge, and its suite job failed. The pull-request closing-keyword step carries no
`continue-on-error`, but red after the merge prevents nothing. No mechanism makes a merge wait for
CI; a memory note describes how to poll for it.

**The neighbor rule does not overlap.** [ADR 0382](0382-a-whole-ticket-binding-on-a-grilling-ticket-is-a-premature-close-refused-at-the-publish-hook-and-red-in-ci.md)
(#1602, ready to build, not built) refuses a **premature close**: a whole-ticket binding, `Closes #N`
owning its line, naming a ticket labeled `grilling`. The closing scan passes exactly that line, and
ADR 0382's rule reads nothing else, so no line can trip both rules.

## Ruling 1. The pre-publication hook refuses a closing hazard

The hook runs the existing scanner, in process and unchanged, over each graded field, and any
**closing hazard** is a refusing finding. The refusal carries the scanner's own finding message,
which already names the line and the remedy: reword the sentence, or bind a finished ticket with
`Closes #N` alone on its line. This is a rule of its own, independent of ADR 0382's.

Advising was declined: the defect was text written past a documented rule, and a warning is one
more written rule, which is ADR 0382 ruling 3's reason for refusing. Folding the rule into #1602's
build was declined because that build's ADR says a closing hazard is not graded again there, so its
builder would be working against its own record. The cost of refusing is one reword; the scanner
matches only the grammar GitHub was measured to act on, so a refusal is almost always a real close
stopped.

## Ruling 2. It grades pull-request text and the merge message, and no other tracker text

The rule grades the title and body of a pull-request create or edit, by `gh pr create`,
`gh pr edit` or the REST route the reader already classifies as either. It also grades the merge
commit's subject and body: the command reader gains a merge route for `gh pr merge`, reading
`-t`/`--subject`, `-b`/`--body` and `-F`/`--body-file`, and classifies the REST merge endpoint as the
same route by the same either-route principle. Only this rule runs on the merge route. It adds no
readback request, and a merge gains no refusal from any other hook rule. A merge that supplies
neither a subject nor a body has nothing to grade.

Issue bodies, issue comments, pull-request comments and reviews stay out. GitHub does not close from
them (ADR 0073, probe 17 for issue comments), and refusing there would refuse ordinary discussion of
tickets that can close nothing, which teaches agents to route around the check. Pull-request text
alone was declined because the merge message is the last text to reach `main` before GitHub acts,
and on that route CI runs only after the merge.

## Ruling 3. The local commit-message hook refuses a closing hazard

`tools/hooks/commit-msg` refuses the commit when the closing scan finds a closing hazard. The
spelling check in the same hook stays advisory, because its own reason, that a spelling is not worth
refusing a commit over, still holds for spelling. The deliberate whole-ticket form, `Closes #N` alone
on its line, passes as it always has. Like every hook here, it acts only in a clone with
`core.hooksPath` set.

Keeping the warning was declined because on a merge that does not wait for CI, the warning is the
only check on this surface and it stops nothing. A refusing pre-push hook was declined because it is
a new hook to build and install and catches the text one step later than the moment it was written.

## Ruling 4. A check that cannot run follows its hook's standing posture

At the publication hook, an exception in any rule already denies the publication, and this rule
inherits that. A merge-route subject or body the reader cannot reproduce is refused on
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)'s
terms, because ruling 2 makes the merge route a graded publication and ADR 0096 refuses an
unreadable graded publication. A hook that cannot read its own payload is
[#1728](https://github.com/mshamblin5150-code/clinical-skills/issues/1728)'s open question and is not
ruled here.

At the commit-message hook, the closing scan follows the strictest local check, the PHI pre-commit
scan: any nonzero exit refuses the commit, so a scan that could not read the message is not read as
clean. With no Python on the PATH the hook prints a loud `SKIPPED` line and allows the commit, as the
PHI check does.

## Ruling 5. Merging before CI reports is a separate ticket

PR #1915's merge landed before every check, including a failing suite, so the gap is wider than
closing hazards. Rulings 1 to 3 close the closing-hazard path without depending on CI. Whether a merge
must wait for CI touches [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md)'s advisory posture and the
time cost of every merge, so it goes to its own ticket labeled `grilling`, with its own measurement.
Ruling it here was declined because it would settle that posture on evidence gathered for a
different question.

**Correction, 2026-10-19:** this record says twice that #1915's suite failed. Its `suite + PHI shape
layer` job failed on the `Closing keyword scan, pull request` step alone; the `Test suite` step
passed, read from the job's step conclusions, and the push run on the merge commit `7020e852`
succeeded. The tree that landed was green, and the closing hazard was the only harm. The rulings
are unchanged. Found by #1926's grilling, whose answer to ruling 5 is
[ADR 0437](0437-a-merge-does-not-wait-for-ci-and-a-red-main-is-handled-by-its-ticket.md). The
`Measured at` line moved to that grilling's base; no file under `tools/` or `.github/` changed
between the two.

## Ruling 6. This build and #1602's are independent

The two rules grade disjoint lines and neither changes the other's verdict, so neither build waits
on the other. Both add a refusing rule and a limit row to `tracker_publish_hook.py`; whichever lands
second keeps both, which is the coordination note #1602 already carries for #1896. Sequencing #1916
behind #1602 was declined because it delays a fix that needs nothing from that build, and one
combined build was declined because it reopens a brief already ready to build for no change in
behavior.

## What this does not reach

The hook never sees text written in the browser: a pull request opened or edited there, or a merge
performed from the merge button with an edited message. GitHub's default merge message carries the
pull request's title, which the hook graded only if it was published through a graded route. A
local merge and push to `main` runs no pull-request step and no publication hook; its merge commit
reaches `main` with only the commit-message hook between it and GitHub, and git does not run
`commit-msg` for a merge it completes automatically. A clone without `core.hooksPath` runs neither
local hook. The scanner is a dated measurement of an unversioned parser, which
`closing_keyword_scan.DECLARED_LIMITS` already states; this record copies none of its rows.

## Build checklist

- `tools/tracker_publish_hook.py`: a refusing closing-hazard rule over each pull-request title and
  body and each merge-route subject and body, calling `closing_keyword_scan` in process, with its
  limit added to `tracker_publish_hook.NOT_REACHED`.
- `tools/command_reader.py`: a merge route for `gh pr merge` reading `-t`/`--subject`, `-b`/`--body`
  and `-F`/`--body-file`, the REST merge endpoint classified as that route, and the route carrying
  only the closing-hazard rule, with its limit added to `command_reader.NOT_REACHED`.
- `tools/hooks/commit-msg`: the closing scan's nonzero exit refuses; spelling keeps `|| true`; the
  no-Python branch keeps its `SKIPPED` lines and exit 0.
- `tools/test_closing_keyword_scan.py`'s `CommitMessageHook` pins the advisory status today and moves
  to the refusing one.
- `CLAUDE.md` **Closing keyword scan** and **Tracker publish hook** sections, and
  `docs/agents/issue-tracker.md` **Check closing keywords before merge**: name the two refusals and
  the merge route without copying either module's limits.
- Tests: a prose closing hazard in a pull-request title, a body, and a merge subject and body is
  refused at the hook; `Closes #N` alone on its line passes there; issue comments and bodies carrying
  the same text are not refused by this rule; a merge route with no subject or body is allowed; an
  unreproducible merge body is refused; the commit-message hook exits nonzero on a hazard and zero on
  `Closes #N` alone; a spelling finding alone still leaves the commit status zero.
