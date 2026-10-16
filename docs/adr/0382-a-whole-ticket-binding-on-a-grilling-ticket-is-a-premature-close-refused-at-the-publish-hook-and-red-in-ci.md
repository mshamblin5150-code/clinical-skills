# A whole-ticket binding on a grilling ticket is a premature close, refused at the publish hook and red in CI

**Measured at:** cf590bcb8f3c95db12d240f1a06755c2f44ff5f5

[#1602](https://github.com/mshamblin5150-code/clinical-skills/issues/1602) was filed from the
after-action review of a `discussion-reply` run (NUR 5042 Module 10), 2026-10-07. During a sitting
that touched that run, PR #1554 merged bound as `Closes #1499` and auto-closed a ticket the
clinician had said he meant to grill and modify later; it was reopened by hand. The conduct fix was
a memory note, and a memory note works only when it is read. The ticket proposed a warning keyed on
the `grilling` label. The clinician ruled every point below on 2026-10-16. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**The approved form is the one that closed it.** `tools/closing_keyword_scan.py` reports every
closing hazard except `Closes #N` alone on its line, which the repository treats as a deliberate
whole-ticket **binding**. So the scanner has no finding for the #1499 shape, and by the glossary's
terms it should not: a **closing hazard** is accidental text, and this was authored.

**The pre-publication hook already holds the label.** `tools/tracker_publish_hook.py` reads the
current state and labels of every record in a publication's **citation set** in one batched
request, on `gh pr create` and `gh pr edit` among its routes. A `Closes #N` line cites `#N`, so the
label this ticket needs is already fetched before the pull request exists. When that read fails, a
rule that needs the record's labels or body reports `NOT GRADED` and does not deny on that ground
alone; the Filed-from body-edit rule is the standing example. The hook sees the title and body it
publishes and never a commit message.

**The two CI steps differ in posture.** In `.github/workflows/checks.yml`, the pull-request
closing-keyword step has no `continue-on-error`, so a finding turns the run red. The
`tracker_merge_receipt.py --check-plan` step that follows does carry `continue-on-error`, so a
finding there leaves the run green and appears only in its log. Both read the same
`gh pr view --json title,body,commits` file, which carries the title, the body and every commit
message. Nothing in the workflow is a required check
([ADR 0002](0002-ci-runs-the-suite-at-the-merge.md)), so red is the strongest verdict CI has. A
pre-merge poll that requires every check to succeed stops on a red run, and passes a run whose only
finding sat in a `continue-on-error` step.

**The binding grammar already has one home.** `tracker_merge_receipt.py` parses the owned-line
`Closes #N`, `Part of #N` and `Implements #N's decision N` forms, and is the reader the merge-time
receipt job already trusts. GitHub closes a ticket from the title, the body and every commit
message, so a binding in any of the three closes it.

## Ruling 1 — a whole-ticket binding on a grilling ticket is a premature close

A **premature close** is a whole-ticket binding, `Closes #N`, naming a ticket that currently carries
the `grilling` label. The term enters `CONTEXT.md` beside **binding** and **closing hazard**. It is
a binding rather than a hazard, because it was written on purpose; what is wrong is its timing,
since the merge closes a ticket whose ruling the clinician has not yet made. `Part of #N` and
`Implements #N's decision N` are never premature closes.

## Ruling 2 — two seams, one binding parse

The check runs at two seams. The pre-publication hook grades the title and body of `gh pr create`
and `gh pr edit`, using the labels its batched readback already fetched, so it adds no request. A
CI step on every pull request grades the title, the body and every commit message, with one label
read per whole-ticket binding. Both seams take the set of whole-ticket bindings from the parse in
`tracker_merge_receipt.py` rather than from a second grammar.

`tools/closing_keyword_scan.py` itself was declined as a seam. It is an offline text grader that
also runs in the local `commit-msg` hook; a label read would put a network call on every commit and
give nothing the CI step does not. The hook alone was declined because it never sees a commit
message, and the binding convention writes the same line there. The CI step alone was declined
because it fires only after the pull request exists, which is later than the moment the agent wrote
the line.

## Ruling 3 — the hook refuses and CI turns red

A premature close is a refusing finding at the hook: the publication is denied with the remedy in
ruling 6. In CI it runs as a step of its own with no `continue-on-error`, so it turns the run red. It
is not folded into the advisory `--check-plan` step, where a finding leaves the run green. The CI
command exits 0 when no whole-ticket binding names a `grilling` ticket, 1 on a premature close, and
2 when a label could not be read, by ruling 5.

Warning at both seams, the ticket's proposal, was declined because the defect was an agent reading
past a written rule, and a warning is one more written rule. Advising at the hook and turning red in
CI was declined because it gives up the cheapest moment to fix it. A deliberate close of a ticket
under grilling costs taking the `grilling` label off first, which is also what makes the tracker
true.

## Ruling 4 — only the grilling label counts

The check fires on `grilling` and on no other label. It is the only label in
`docs/agents/triage-labels.md` whose meaning is that the clinician still has to rule, which is what
a close forecloses. `needs-triage`, `needs-info`, `blocked` and `ready-for-human` each describe a
state a finishing pull request can legitimately end, and `in flight` is normally closed by the
building session's own pull request. A wider set was declined because it would refuse ordinary
work, and a check that refuses ordinary work teaches agents to strip labels to get past it.

## Ruling 5 — an unread label is not graded at the hook and red in CI

When the hook's batched readback fails, the premature-close rule reports `NOT GRADED` and allows the
publication, consistent with its other label-dependent rules. When the CI step cannot read a
binding's labels, it exits 2, and a step without `continue-on-error` turns the run red. A re-run
after the lookup recovers clears it. So a publication may go out ungraded during an outage, but a
pull request cannot reach a green run, and so cannot clear the merge poll, until a label was really
read.

Refusing at the hook as well was declined because an outage would then block every pull-request
publication carrying a whole-ticket binding, and a failed read has never by itself denied a
publication there. Passing with a note at both seams was declined because a green run that never
read the label presents a partial read as clean.

## Ruling 6 — the remedy is Part of, after checking in flight

The refusal and the CI finding both name the remedy: bind the ticket with `Part of #N` on its own
line instead, and check whether another session holds `in flight` on it first, because the
merge-receipt job removes that label from every ticket a merged pull request binds. `Part of #N`
leaves a **merge receipt** on the ticket, which is the record of what merged that the clinician
asked for on #1499. `Binds no ticket: <reason>` was declined as the suggestion because it leaves
nothing on the ticket. The message also says that a ticket whose grill is really over takes its
`grilling` label off first.

## What this does not reach

The label is read when the hook or the CI step runs, not at the merge: a ticket labeled `grilling`
after the last CI run, or a merge that does not wait for a fresh run, is outside both seams. A local
merge and push never runs the pull-request step; `tracker_merge_receipt.NOT_REACHED` already names
that route. The hook never sees a pull request opened or edited in the browser, or a commit message;
the CI step covers both only once a pull request exists. A closing keyword outside the owned-line
binding grammar is a **closing hazard**, which the existing scanner already reports, and is not
graded again here. Nothing here decides whether the clinician's ruling on a ticket is in fact
finished; the check reads the label he and the grilling workflow maintain.

## Build checklist

- `tools/tracker_merge_receipt.py`: expose the whole-ticket binding set from its existing parse,
  and add the CI command of ruling 3 with the exit statuses of rulings 3 and 5 and the remedy of
  ruling 6.
- `.github/workflows/checks.yml`: a new pull-request step, with no `continue-on-error`, that reads
  the existing `pull-request.json` and supplies `GH_TOKEN` for the label reads.
- `tools/tracker_publish_hook.py`: a refusing premature-close rule over title and body, fed by the
  existing readback, reporting `NOT GRADED` when that read failed, with its limit added to
  `tracker_publish_hook.NOT_REACHED`.
- `CLAUDE.md` **Closing keyword scan** and **Tracker publish hook** sections, and
  `docs/agents/issue-tracker.md`: name the new rule and step without copying either module's limits.
- Tests: a `Closes #N` binding on a `grilling` ticket is refused at the hook and exits 1 in CI; the
  same binding on an unlabeled ticket is clean at both; a `Part of #N` binding on a `grilling` ticket
  is clean; a failed label read is `NOT GRADED` and allowed at the hook and exits 2 in CI; a
  commit-message binding is reached by the CI command and not by the hook.
