# Both publish routes grade a body through one grader and a lost body refuses

Out of [#1028](https://github.com/mshamblin5150-code/clinical-skills/issues/1028), grilled on
2026-09-11 to an empty frontier. Measured at `5dae592` with the freshness gate `FRESH` before
reading.

#1028 was filed after a session blanked #866's body on 2026-09-10: a script truncated its draft
files, and `gh issue edit 866 --body-file <empty draft>` passed the pre-publish hook and left the
body at length 0 until the same session restored it. Two `gh issue comment` calls on the same empty
files were also allowed by the hook and refused only by GitHub (`Body cannot be blank`); an edit has
no such server-side refusal. The ticket asked two things: whether the hook's command path applies
`tracker_bodies.grade` whole or only
[#130](https://github.com/mshamblin5150-code/clinical-skills/issues/130)'s three rows, and whether a
whitespace-only body counts as empty.

## What was measured before ruling, on 2026-09-11

**The hook has two routes, and they grade different row sets.** `tracker_publish_hook.analyze`,
which every `gh` command reaches through `handle`, calls four `tracker_bodies` predicates by name:
`has_c0_control_character`, `has_carriage_return_flanked`, `has_literal_newline_escape` and
`has_doubled_path_separator`. `authorize_issue_body`, the direct-writer route, calls
`tracker_bodies.grade`, which grades every row in `tracker_bodies.KINDS`, and raises on any finding.
Its only production callers are the two sites in `tools/implementation_map.py` that publish the map.

**The gap on the command route is wider than the ticket names.** Empty, whitespace-only, `@-` and
double-encoded sample body files were driven through `extract` and `analyze` on `gh pr edit`,
`gh issue comment` and `gh issue edit`. Each was extracted as one readable body publication and each
returned **0 findings** on all three routes. `@-` is #130's own documented trap, and the
double-encoded shape is
[#155](https://github.com/mshamblin5150-code/clinical-skills/issues/155)'s. *Had `analyze` applied
`grade`, each of those twelve runs would have carried a deny finding.*

**The whole tracker, harvested 2026-09-11.** 5,350 records: 491 issues, 597 pull requests and 4,262
comments, with review comments read and empty. The documented `gh api .../issues?state=all` fetch was
refused by the hook at `5dae592`, a routing defect
[#1084](https://github.com/mshamblin5150-code/clinical-skills/issues/1084) has since fixed, so the harvest used `gh issue list --json` and `gh pr list --json`.
The harvesting subagent reported each surface's total matching a GraphQL count at harvest time; that
match was not re-derived, because records created after the harvest have since moved the live totals.
`tools/tracker_bodies.py` over that harvest reports:

| row | findings |
| --- | ---: |
| `lost-at-dash` | 8 |
| `empty-body` | 0 |
| `literal-at-path` | 0 |
| `double-encoded` | 9 |
| `c0-control-character` | 0 |
| `carriage-return-flanked` | 0 |
| `literal-newline-escape` | 5 |
| `doubled-path-separator` | 2 |

`empty-body` reads 0 because #866 was restored; the instance is the ticket's, not the harvest's.

**All nine `double-encoded` firings are damage, and none refuses correct text.** Each of the nine
carries 4 to 13 matches in its prose, decoding to dashes, section signs, middots, mathematical signs
and emoji. *A record that named the defect in prose rather than carrying it would show one or two
matches; none does.* Sixteen further records carry the shape only inside code spans or fenced
blocks, all of them correct discussions of the defect, and the row does not fire on them. The row's
one blind spot runs in the permissive direction: #190 and #97 each carry one more damaged sequence
inside a code span. The harvest was taken by a subagent; its record count, per-row counts and the
sixteen were re-derived from its files, and the damage classification was checked by the match count
above rather than taken on its word.

**No title fires on any row.** `grade` run over the 1,088 harvested titles returns no finding of any
kind. `gh issue` and `gh pr` accept a title only inline, through `--title` or `-t`; a title reaches
the tracker from a file only through `gh api -F title=@path` or an `--input` document.

**The harvest lives under `scratch/`, so nothing committed re-derives these figures**, and each is a
dated floor. Re-derive by harvesting the tracker and running
`python tools/tracker_bodies.py <harvest files>`.

## Ruling 1 — both routes grade a body through `tracker_bodies.grade`

The command route grades a body publication with the same `tracker_bodies.grade` call the direct
writer makes. The four body predicates `analyze` names by hand leave the body path; a title keeps
the two rows ADR 0099 ruling 5 and
[ADR 0136](0136-each-escape-collapse-shape-gets-its-own-refusing-row-and-a-record-may-fail-more-than-one.md)
already grade on it, because `grade` reads bodies only. Every row in `tracker_bodies.KINDS` then
reaches both routes under one posture, and a row added to `tracker_bodies` reaches both with no edit
to the hook.

**The defect is the divergence, not the three missing rows.** Adding #130's rows to `analyze` by name
would close this ticket's instance and leave two hand-kept row sets in one hook, so the next row
would arrive at one route and miss the other exactly as #1028's did. ADR 0136 ruling 5 had already
recorded the coupling: `authorize_issue_body` refuses every row, so any row the command route treats
differently is a split posture inside one module.

## Ruling 2 — a lost body is refused, and a whitespace-only body is lost

A body the checker read whose text did not land -- nothing but whitespace, the two characters `@-`,
or a single `@`-token -- is a **lost body**, now defined in `CONTEXT.md`. It is a finding and refuses.
It is not an **unreadable body**, which the checker could not obtain, and not a route carrying no body
flag at all, which is silent on every route except an issue create.

**Whitespace-only is lost on the ground #130 already ruled**: a body is never legitimately empty, and
`grade` strips before testing. A hook that tested for zero length instead would disagree with the
post-publication workflow grading the same body, and a body of two line breaks publishes exactly
what an empty one does. This answers #1028's decision 2.

## Ruling 3 — a rule on the body's text holds on both routes, and a rule on the command's form holds on the command route only

Rules on the text of a body are shared by both routes under Ruling 1. Rules on how the command was
typed -- the Filed-from refusal on issue create and edit, the unreadable-body refusal, and any check
on whether a body arrived inline -- have nothing to read on the direct writer, which holds bytes and
no command. The direct writer answers such a rule with an exemption keyed on something it already
stamps, which is
[ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md) ruling 10's arrangement, or
with a declared limit.

**This constrains [#916](https://github.com/mshamblin5150-code/clinical-skills/issues/916) and does
not absorb it.** That ticket's decision 4 counts *"the two hook entry points would enforce different
rules"* as a cost of a cause-side check on inline bodies. Under this ruling a rule on the command's
form is command-route-only by definition, so decision 4 is answered. Its decisions 1 to 3 -- whether
the check is worth building, what it refuses, and whether titles are in scope -- are not ruled here.
#1028's repair is correct whether or not #916 is ever built.

## Ruling 4 — `double-encoded` refuses on both routes

The direct writer already refuses #155's row; the command route now refuses it too, and the
post-publication workflow stays advisory under
[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md). It clears
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4's bar on measurement rather than argument: no PHI, nine damaged bodies of nine firings with
no refusal of correct text, and a remedy the agent applies alone.

**The refusal names two remedies, and the difference between them is the part a message can get
wrong.** A body that came through a cp1252 path is rewritten as UTF-8. A body that deliberately names
the sequence puts it in backticks. Backticks also clear real damage, so the message says the second
remedy is for a genuine mention only.

**Advising was priced and refused.** It would make `authorize_issue_body` filter by row to stay
consistent, which is the split ADR 0136 ruling 5 refused, and it would leave
[ADR 0141](0141-a-collapsed-escape-is-repaired-by-mechanical-inverse-and-the-residual-red-needs-no-register.md)
ruling 5's ground false for #155's population permanently.

## Ruling 5 — titles stay outside the lost-body rows and #155's row, and the gap is declared

`grade` stays a body grader. The declaration goes into `tracker_bodies.NOT_REACHED`: an empty, `@-`
or double-encoded title is outside those rows; none of 1,088 titles fired on 2026-09-11; and
`gh issue` and `gh pr` have no title-file flag, so the file-backed ways bodies were lost do not
reach a title on those routes. The `literal-at-path` precedent admits a row with zero instances only
for a documented trap, and no title trap is documented.

## Correction to ADR 0141 ruling 5

That ruling declines a register on the ground that *"the command path refuses a damaged title or
body, so no row's population can grow through the Claude Code publisher."* When it was written the
command route graded four of `tracker_bodies`' eight rows, so `lost-at-dash`, `empty-body`,
`literal-at-path` and `double-encoded` could grow through that publisher, and #866's body was blanked
through it. The no-register conclusion stands; its ground holds for every row once Ruling 1 is built.
A dated correction line is appended to ADR 0141.

## Considered options

- **Add #130's three rows to `analyze` by name.** Refused under Ruling 1: it fixes the instance and
  keeps the divergence.
- **Advise on `double-encoded` at the command route.** Refused under Ruling 4.
- **Test for zero length at the hook.** Refused under Ruling 2: it disagrees with the workflow over
  the same body.
- **Rule #916 together with this ticket.** Refused under Ruling 3: the two are related and neither
  repair depends on the other.
- **Grade titles on the lost-body rows and #155's row.** Refused under Ruling 5.

## Consequences for the build

- `analyze` grades a body publication through `tracker_bodies.grade`; each finding is a
  `body:<kind>` deny finding carrying its row's remedy. A title keeps its two predicates.
- `python tools/tracker_publish_hook.py --text` reaches the same grader, because it grades through
  `analyze`.
- A test derived from `tracker_bodies.KINDS` drives every row through both `handle` and
  `authorize_issue_body` and asserts both refuse, so a new row that reaches one route and not the
  other fails it.
- A blank body edit on a ticket that already carries a Filed-from line now draws two deny findings,
  one from each rule; both stand.
- An explicit empty review body, as in `gh pr review 12 --approve --body ""`, is refused. An approval
  needs no body, and the remedy is to omit the flag.
- `CLAUDE.md`'s *Tracker bodies* section and the *Both publication hosts* paragraph of
  `docs/agents/issue-tracker.md` describe the command route's row set; the build updates them in the
  same change that moves the behavior.

## What this does not reach

**The other publisher.** The refusing hook covers the Claude Code publisher only, which is a row of
`tracker_publish_hook.NOT_REACHED`; the workflow reaches both publishers after publication and
reports.

**A body that landed with a defect no row grades**, which is `tracker_bodies.NOT_REACHED`'s, and a
body rewritten between the scan and the publication, which is `tracker_publish_hook.NOT_REACHED`'s.

**The historical records.** The eight `lost-at-dash` and nine `double-encoded` records above are
unchanged; no route grades a historical record, and ADR 0141 ruling 5's no-register conclusion stands.
