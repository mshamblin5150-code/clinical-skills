# The staged ADR check accepts the tip or its parent and a post-commit report gives the exact verdict

**Measured at:** aa5d6d302a3ad9639a4f19c12280908de6877446

[#1875](https://github.com/mshamblin5150-code/clinical-skills/issues/1875) reports that
`python tools/tracker_measurements.py --staged-adrs` refuses every `**Measured at:**` value during
`git commit --amend`. Grilled 2026-10-19 against `main`. The clinician ruled every point below in
that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Two checks read the same declaration against different commits.** `grade_staged_adrs` runs in
the pre-commit hook and compares a staged ADR's declaration with `current_head`, the branch tip
before the commit. `grade_adrs` is the committed audit that CI runs; it compares each eligible ADR
with the first parent of the commit that last touched it. On an ordinary commit those are one
commit. During an amend the tip is the commit being replaced, and the new commit's parent is the
commit below it, so no declaration passes both checks.

**It has cost four records.** ADRs 0404, 0407, 0416 and 0421 each met the refusal, and the sweep
comments on #1875 record each one. 0407 shows that a rebase is not needed: one edited sentence
was refused. Two workarounds landed them: `git reset --soft` onto the base followed by a fresh
commit, or a follow-up commit whose declaration names its own parent. The second leaves a
declaration that names a commit already holding a draft of the record, and 0416 had to reword
its opening paragraph to say so.

**No hook signal names an amend.** The triage probe on 2026-10-18, run in a throwaway repository
under Git for Windows, logged what `pre-commit` and `prepare-commit-msg` received on two plain
commits and two amends. `pre-commit` received the same `GIT_*` environment every time.
`prepare-commit-msg` received source `commit` and object `HEAD` on `git commit --amend
--no-edit`, and on `git commit --amend -m ...` it received exactly what a plain `git commit -m`
gives. The ticket's first option, comparing with `HEAD^` once an amend is detected, has no
signal to detect with.

**The exact check is cheap only when narrowed.** On this record's base the full committed audit
read 422 ADRs, 331 at or after the cutoff and 186 declarations, with `findings 0`, and took 65
seconds. Most of that time is one `git log` per tracked ADR. Restricted to the ADRs a single
commit touched, the audit reads only those few.

## Ruling 1 — the commit-time check accepts the tip or its first parent

`grade_staged_adrs` accepts a declaration naming either the pre-commit `HEAD` or `HEAD`'s first
parent. No staged ADR declaration is refused for naming the second of the two.

Keeping the exact tip and declaring the amend case next to the existing limit was declined.
Every later rebase or one-sentence edit would keep paying for an extra commit or a soft reset,
and the follow-up-commit route keeps producing records whose base holds a draft of themselves.
Skipping the check when `prepare-commit-msg` reports an amend was declined, because it covers only
`--amend --no-edit` and makes the rule depend on which flags were typed. The cost of the ruling is
stated, not hidden: on an ordinary commit, a declaration naming the commit one too far back now
passes locally. Ruling 2 and CI catch that exactly.

## Ruling 2 — a post-commit hook reports the exact verdict

A new `tools/hooks/post-commit` runs the committed audit over only the ADRs the new commit
touched, against that commit's first parent. It prints any finding and never changes Git's
status. CI's full committed audit remains the backstop that nothing local can skip.

A pre-push refusal was declined. The hook policy adds refusing checks deliberately to protect
clinical guidance a consumer may rely on, and an ADR's measurement base is not that; it would also
be the first refusal that fires at push. Relying on CI alone was declined because the gap from
ruling 1 would surface only on the pull request page, after the push. The post-commit report
reaches the author in the same command output, while the fix, an amend that ruling 1 now admits,
is still at hand.

## Ruling 3 — the annotation exemption tries the same two commits

The [ADR 0334](0334-supersession-only-adr-edits-preserve-the-historical-measurement-base.md)
annotation-only exemption, at commit time, proves preservation against the tip and against its
first parent, and exempts the staged ADR if either proof holds.

Keeping the tip alone was declined. It reasons about the same unknown commit underneath, and
amending a commit that annotated an old ADR would compare against the commit being replaced. That
would likely bring back this ticket's refusal in a narrower case; it was not driven. What the
ruling opens is narrow: on an ordinary commit, a staged text that is annotation-only relative to
the commit one further back, which means one that undoes the tip's own change to that ADR and
adds annotations. Ruling 2 and CI grade that exactly.

## What this record does not reach

- **Which of the two commits is correct, at commit time.** Nothing a hook receives tells an amend
  apart from an ordinary commit, so the pre-commit verdict is a two-value floor. The exact
  verdict exists only after the commit, from ruling 2's report or CI.
- **Whether `post-commit` runs during a rebase's replayed commits.** Not established. A rebase
  that leaves a stale declaration is still caught by CI's full audit.
- **Branch drift.** The staged check still compares with the branch tip, not with `main`, so the
  existing limit stands.
- **A fresh re-derivation.** `DECLARED_LIMITS` already states that the gate cannot tell a
  re-derived figure from a copied SHA; accepting a second value does not change that.

## Build checklist

- `tracker_measurements.grade_staged_adrs`: read `HEAD` and, when it exists, `HEAD^`, and pass both
  to the grade. A declaration matching either passes. A root commit, with no `HEAD^`, keeps the
  single tip. A stale finding reports both accepted values.
- `_grade_adr` and `_annotation_only_proof`: at commit time, try the annotation proof against each
  accepted base and exempt the ADR if either proves preservation. The committed audit keeps its
  single last-touch parent.
- Replace the `DECLARED_LIMITS` row "The staged-ADR reader compares with branch HEAD and therefore
  fires on branch drift." with one stating that the staged reader accepts the pre-commit `HEAD` or
  its first parent because no hook signal distinguishes an amend, still fires on branch drift, and
  leaves which value is correct to the post-commit and committed-ADR audits. Add a row for the
  post-commit mode: it reads only the ADRs the new commit touched, and running during a rebase is
  not established.
- A command mode, for example `--commit HEAD`, that runs the committed grade over the ADRs a named
  commit touched, against that commit's first parent, printing the shared report. Exit statuses
  follow the module: 0 clean, 1 finding, 2 not scanned.
- `tools/hooks/post-commit` calls that mode only when the new commit touched `docs/adr/*.md`, and
  exits 0 whatever it prints. The `pre-commit` comment for the staged check and `CLAUDE.md`'s
  **Tracker measurements** section move with the two rulings, and the hook inventory names the
  post-commit report as advisory.
- Tests drive the public command in throwaway repositories: an ADR added at the tip's declaration
  passes; a `git commit --amend` that re-declares at the amended commit's parent passes the staged
  check and the committed audit; an ordinary commit declaring `HEAD^` passes the staged check and
  is reported by the post-commit mode with exit 1; a declaration naming neither commit is refused.
  An annotation-only amend of an old ADR passes. Name as a control today's refusal: on the
  unpatched module the amend case exits 1.
