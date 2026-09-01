# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues on the public `mshamblin5150-code/clinical-skills` repository. Use the `gh` CLI for all operations.

**Maintainer tooling.** This file configures Matt Pocock's engineering skills for whoever maintains the repo. It is not a dependency of the clinical skills — anyone consuming `skills/` via [AGENTS.md](../../AGENTS.md) needs none of it.

## Conventions

### Multi-line bodies: always `--body-file -`

**`--body` takes a string and cannot read a heredoc.** `--body-file` (`-F`) is the flag that reads standard input, and only when given `-`. Get this wrong and the failure is silent — see *The `@-` trap* below.

```bash
gh issue create --title "..." --body-file - <<'EOF'
Body text, as many lines as you like.
Single-quoted 'EOF' so $vars and `backticks` stay literal.
EOF
```

The same `--body-file -` works for `gh issue comment` and `gh issue edit`. Single-line bodies may use `--body "..."`.

### The rest

- **Read an issue**: `gh issue view <number> --comments`. Add `--json body --jq '.body'` when the rendered view truncates.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment**: `gh issue comment <number> --body-file - <<'EOF' … EOF`
- **Edit a body**: `gh issue edit <number> --body-file - <<'EOF' … EOF`
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

`gh` infers the repo from `git remote -v` when run inside the clone.

### The `@-` trap

**Never write `--body @-`.** The `@-` and `-F body=@file` forms belong to `gh api`, which is a different command with different flags. On `gh issue create`, `--body` is a plain string, so `--body @- <<'EOF'` sets the body to the two literal characters `@-`, discards the heredoc, **and exits 0**. The issue is created, the command reports success, and the body is gone.

This ate the bodies of #7 and #8 before it was spotted; both had to be reconstructed from `scratch/rule-amendments.md`, and #7's grilling ran off its title alone.

**The same trap has a second door, and it cost four comment bodies on 2026-08-19.** `gh api`'s `-f` takes a **literal** value and never resolves `@`; only `-F` does. So `-f body=@-` is not a stdin read that failed, it is a successful write of the two characters `@-`, and `gh` exits 0. Use `-F body=@-`, or `--input -` with a JSON document, which cannot be misread as a literal at all.

**Verify after creating anything with a long body:**

```bash
gh issue view <number> --json body --jq '.body' | head -5
```

A body of `@-`, or an empty body, means it was eaten. Fix it with `gh issue edit <number> --body-file -`.

### And a command that grades it

**The rule above was written down on 2026-08-11 and bodies kept being lost anyway** — which is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written instruction cannot do is fail*, arriving at the tracker. So `tools/tracker_bodies.py` grades a harvest for five shapes: the literal `@-`, an empty or whitespace-only body, a body that is one bare `@token` — what `--body @notes.md` writes — [#155](https://github.com/mshamblin5150-code/clinical-skills/issues/155)'s double-encoded body, and [#723](https://github.com/mshamblin5150-code/clinical-skills/issues/723)'s raw C0 control character other than tab, line feed, or carriage return.

```bash
: "${TICKET_NUMBER:?set TICKET_NUMBER to the current ticket number}"
H=$(python tools/scratch_work.py ticket "$TICKET_NUMBER")
mkdir -p "$H"
gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" > "$H/tracker-issues.json"
gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" > "$H/tracker-comments.json"
gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" > "$H/tracker-reviews.json"
python tools/tracker_bodies.py "$H"/tracker-*.json
```

**All three surfaces, which is `tools/tracker_scan.py`'s set.** The review-comment endpoint is the one easiest to leave out; a harvest that omits it reports that as a clean scan of it rather than as not having read it.

**New and edited tracker text is scanned at publication.** The `tracker.yml`
workflow gives `tracker_scan.py` the one changed GitHub event record and runs
the shape layer with the corpus absence stated in its job name and report. It
does not replace the full-harvest command above: the runner can never hold
`scratch/`, so patient names remain a maintainer-clone layer. Incremental input
is deliberate -- a whole-tracker run on every comment would replay #264's
historical findings rather than attach a result to the record that changed.
Issue #260.

**It opens no socket**, on `tracker_scan.py`'s terms — the fetch is a documented `gh` command whose output is a file. Into `scratch/` for that tool's reason too: the harvest is the tracker's entire text, and `scratch/` is the PHI firewall's own directory. **Its report names a URL and a row name and never a body**, so its output is safe to paste, and there is no `--show` to widen it. The fourth row catches both known encoding mechanisms: UTF-8 decoded through cp1252, and a literal `\uXXXX` escape left undecoded. It counts affected records rather than raw sequences. A shape inside inline or fenced code is a mention and does not fire on that row. **The fifth row instead reads the raw body**, including code spans and leading or trailing Python whitespace, because a raw control character cannot be a mention.

**It is also the read-back**, because it takes a single JSON object as well as a list — one command, and it catches the shape `--jq '.body | length'` does not, since a lost body has a length of 2 and reads as a number rather than as a failure:

```bash
gh issue view <number> --json number,body,url | python tools/tracker_bodies.py -
```

**`-` and not a path to a device.** This line first read `/dev/stdin`, which is not a file on the platform every commit here is made from — the command exited 2 saying *no harvest file named dev/stdin*, so a documented step could not run while reading as a checked one.

**Nothing runs any of this, and saying so is the point.** `tools/hooks/` holds `pre-commit` and `commit-msg`, and neither owns a filing — the tracker is not in the tree, so no local hook can reach it. The gap this closes is *there was no check*; the gap it leaves is *a check exists and somebody has to run it*, and a command nobody runs is a written instruction with extra steps.

**Do not grade this with `gh issue list`, and that is #130's own finding rather than a preference.** That command **`gh issue list` excludes pull requests**. Two of the eight lost bodies in this repo are pull requests — #98 and #71 — so every sweep that ran #130's reproduce command re-derived *six, not eight* and concluded the ticket's title was stale. **Its count was right** — its *three are still open* half really had gone stale, which is what made the whole title easy to dismiss — and the instrument could not see two of its members and had no way to say so. The `issues` REST endpoint returns both, and a `pull_request` key is which.

**A clean scan is not a body worth reading.** The first three rows ask whether text landed; the fourth reads only the two bounded encoding shapes above; the fifth reads only its bounded C0 set. A body truncated at a shell metacharacter, or the right words about the wrong ticket, can have text, match no row, and pass. The complete boundary belongs to `tracker_bodies.NOT_REACHED`.

### Commit finding rulings

**Commit findings already ruled by a person live in
`reference/tracker-scan-rulings.json`.** `tracker_scan.py --commits` reports how
many exact findings that ledger removed. Each row holds the full commit id,
line, rule and a SHA-256 match digest, never the match itself; changing any limb
leaves the finding live. Add a row only after reading `--show` locally and
deciding its `verdict` and `reason`. A malformed ledger is not an empty ledger:
the run says the rulings were not applied and cannot exit clean on the commit
surface.

## Pull requests as a triage surface

### Branch truth gets a dated scope, then a merge receipt

Before branch work produces tracker prose, label its issue `in flight`. Any
issue body or comment published or edited while that label is present starts
with a scope block above the claim, in this exact, unambiguous form:

> **Branch state:** `branch-name` at `full commit SHA` is not on `main` as of `YYYY-MM-DD`.

Naming a branch, saying it was *merged with main*, or adding `in flight` is not
the same statement. The first can outlive a deleted ref, the second does not say
which direction the merge ran, and the label scopes a ticket rather than an
individual claim. Keep the label as a useful queue signal; do not use it as the
claim's provenance.

Cite a repository file from tracker text with an absolute `blob/main` URL.
Relative Markdown destinations resolve against the issue URL and are broken;
they are not a weaker repository citation. When the cited path is not yet on
`main`, start the record with either the Branch state line above or this
path-specific form:

> **Cited record state:** `<path>` is not on `main` as of `YYYY-MM-DD`.

The date makes the statement remain true after the path lands. Do not rewrite
or delete it on merge. A bare `ADR NNNN` is under-specified; prefer the link,
though bare numbers are deliberately not graded. The check's blind spots have
one owner in `tracker_branch_scope.NOT_REACHED`; this document copies none of
those rows.

This is mechanically checked at the publication event. `tracker.yml` runs
`tools/tracker_branch_scope.py` for issue bodies, issue comments, pull request
bodies, reviews, and review comments. Adding `in flight` therefore grades the
issue body already present; later records are graded as they are published.
An issue comment on a pull request remains outside the older in-flight trigger,
but every surface is checked for unresolved or relative path citations. The
check is prospective: it does not reinterpret historical comments when a label
is added, and says so rather than claiming a semantic backfill.

The label is not the only trigger. A newly published comment whose opening
sentence says `Ruled and built`, `Implemented locally`, `Built on`, or `Landed
on` has declared a state transition itself. It must start with the same Branch
state block, or with the workflow's exact `Merged into main` receipt. This is a
bounded fallback for a missed `in flight` label, not a claim that the checker can
infer assertions from arbitrary prose. It catches the fresh premature closure
recorded on #283 while leaving historical discussion outside its vocabulary.

Every pull request body names each ticket whose state it changes with a binding
that owns its line: `Closes #N` for the whole ticket, `Part of #N`, or
`Implements #N's decision 1` for a partial. The partial-unit noun vocabulary is
`decision`, `decisions`, `option`, `options`, `lead`, and `leads`; a number,
range, or list follows it. Terminal punctuation, matched Markdown emphasis,
ordered or unordered list decoration, blockquote decoration, and a
comma-separated list of further references do not stop a binding from owning
the line. Prose before or after it does. A pull request body or commit message
that intentionally binds nothing writes `Binds no ticket: <reason>` on its own
line. The pull request body is one authored message, and each commit is one
authored message whose headline and body are grouped together. A declaration
may sit in a pull request that has bindings elsewhere; it conflicts only with a
binding in the same authored message.
When that pull request merges into `main`, `tracker.yml` runs
`tools/tracker_merge_receipt.py` over the PR body and commit messages and posts
one merge receipt for each explicitly named whole ticket or partial lead. The
receipt preserves that bounded relation, plus the PR, full merge SHA and date,
so two branches settling two leads on one ticket do not collapse into one state.
It does not pretend a symbol kept its name or that every other claim on the
ticket is current. The pre-merge receipt-plan check is advisory and reports an
empty plan or declined reference-shaped line; a clean result does not establish
that the binding names the right ticket.

**Do not rewrite or delete the dated branch-state record after merge.** A
comment is evidence of what was true when written. The later merge receipt is
the state transition, and its immutable commit anchor remains useful after a
branch is deleted. Historical tracker records predating this mechanism remain
historical; there is no semantic backfill that can distinguish an assertion
from a proposal reliably. Issue #290.

### Check closing keywords before merge

GitHub scans a pull request's title, body, and commit messages for closing keywords. The repository scanner follows the dated measured grammar and declared margins named in `closing_keyword_scan.DECLARED_LIMITS`; prose intent does not make a matching form safe. Run it over all three fields before merging:

```bash
gh pr view <number> --json title,body,commits |
  python tools/closing_keyword_scan.py --github-json -
```

The only allowed binding is `Closes #N` alone on its own line, when the whole ticket is done. Use `Implements #N's lead 1` or `Part of #N` for partial work. The local `commit-msg` hook checks commit messages; the pull-request CI check treats the scanner's exit status as its verdict, while the post-action push check stays advisory. In both CI steps the scanner runs last, nothing consumes its output, and its exit status is the verdict. The command above is the pre-merge check that reaches the whole PR artifact. Issues #183 and #574.

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Search before you file

**One command, before `gh issue create`, every time:**

```bash
gh issue list --state all --search "phi_scan --all"
```

`--state all` is the part that earns its keep. A closed ticket answers the question as often as an open one does — either the thing is already fixed, or it was already argued about and rejected, and the reasoning is sitting on the issue.

Search the **artifact**, not your framing of the problem: the command you ran, the file path, the symbol, the error string. Whoever filed first described the problem their way, not yours. The results are ranked rather than filtered, so unrelated tickets appear below the real hits — read the top few and ignore the tail.

**This is not hypothetical.** #20 and #21 are one bug, filed 25 minutes apart by two sessions that never saw each other. Both titles open with `phi_scan --all exits 1 on CLAUDE.md's own`, so either session searching `phi_scan` would have found the other instantly.

What made them collide is worth knowing, because it recurs. Neither session was working on phi_scan — one was implementing #18, the other running the audit before committing #11 — and each filed within a minute of finishing that unrelated work. #18 was itself the cause: it took `--all` from 130s to 0.48s, which turned a failure nobody ever saw into the first thing every session meets. **Fixing something that hid a defect makes every concurrent session discover that defect at once**, and an incidental finding at a task boundary is exactly when this step feels skippable.

Labeling does not cover this. Labeling at creation makes a ticket findable *after* it exists; searching first is what stops the second copy being written. Both duplicates were labeled correctly.

**Finding a match does not always mean staying quiet.** If an existing ticket covers part of what you hit, comment there instead of opening a second. If yours is genuinely a different problem, file it and link the other one by number in the body — a stated relationship beats a backlog that merely looks tidy.

## Every issue you create gets a label

**A ticket filed with no label is a ticket nobody can find.** `--label` takes a comma-separated list and works on `gh issue create` as well as `gh issue edit`:

```bash
gh issue create --title "..." --label "needs-triage,grilling" --body-file - <<'EOF'
...
EOF
```

The vocabulary and how to choose between the labels is in [triage-labels.md](triage-labels.md). Two rules worth repeating here, because both have already been broken in this repo:

- **A ticket with an open decision gets `grilling`, never `ready-for-agent`.** `ready-for-agent` is a promise that an unattended agent can build it without guessing.
- **Record dependencies rather than describing them in prose.** `gh issue edit <n> --add-blocked-by <m>` and `--add-blocking <m>` are supported, and they show up in `gh issue view`.

The sweep also holds the `blocked` invariant: every open ticket carrying `blocked` has an open
`blocked_by` edge, or its body names a gate that no edge can record. If every gate has cleared and
the body names none, remove `blocked` and re-triage the ticket. If a recordable gate lives only in
prose, add the dependency edge instead.

Label at creation time. Coming back to label later is the step that gets skipped.

## Finishing a ticket means sweeping the tracker, and you are authorized to do it

**A merged PR is half of finishing.** The other half is that the work found things, and those things belong on the tracker before the session ends. **Do it without asking** — updating an existing ticket and filing a new one are both standing authorization here, on the same footing as spawning subagents. What needs permission is changing a *ruling*; recording what you found does not.

**The reason is the one #59 was filed about, arriving one level up.** That ticket exists because a decision got resolved inside an implementation and shipped, discoverable only by reading a merged diff. A finding that stays in the diff is the same defect in a cheaper form: the next session re-derives it, or does not, and nothing says which.

### Establish the current base twice

**Before reading any ticket**, fetch and grade the base with the repository gate:

```bash
python tools/tracker_freshness.py
```

The command exits **0** for `FRESH`, **1** for `STALE` — `HEAD` does not contain the fetched `origin/main` — and **2** for `DID NOT CHECK`, which is every way of reaching no verdict about the base at all: a failed fetch, an unrunnable `git`, or an ancestry question git declines to answer. It does not merge or rebase. Bring the branch forward, resolve any conflicts, rerun the work's checks, and repeat the gate until it reports `FRESH`.

**Read 1 and 2 differently.** A 1 is the gate working: the base is behind and you know it. A 2 is the gate having established nothing, so anything you were about to publish rests on an unmeasured base — treat it exactly as you would a stale one, and do not read it as permission to proceed with a banner. Both non-zero limbs were 2 until [#744](https://github.com/mshamblin5150-code/clinical-skills/issues/744).

**Immediately before posting** a sweep finding, run it again:

```bash
python tools/tracker_freshness.py
```

An exhaustive sweep takes long enough for `main` to move underneath it. If the second gate stops, publish nothing from the pending sweep until the branch contains the new base and the affected evidence has been checked again. Per-file comparisons do not replace this: a claim that the tree lacks a repair cites no file to compare. This is [#320](https://github.com/mshamblin5150-code/clinical-skills/issues/320)'s ruling.

### Every open ticket, not the ones that look relevant

**The sweep is exhaustive. Read every open ticket, one at a time, and record a verdict for each.** Not the ones whose titles look related — *all* of them. Ruled 2026-08-15.

This is the rule most likely to be quietly narrowed, because narrowing it feels like judgment rather than like skipping. A session settling [#63](https://github.com/mshamblin5150-code/clinical-skills/issues/63) swept 9 of 39 open tickets, picked by which titles sounded connected, and reported that as the sweep. Everything it picked was genuinely connected — and the two findings that mattered most were both outside the selection:

- **A latent defect in the code that session had just merged.** Its new guard sweeps `fixtures/` with a bare three-digit match and had no exemption for `fixtures/filled-anchor/notes/`, the preserved run record [ADR 0001](../adr/0001-fixture-asserts-on-named-findings.md) forbids editing. Surfaced only by reading [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137), which is about that directory and has nothing to do with catalog denominators.
- **A stale figure restated in many files at once.** "The 31 committed fixture inputs" became 34 when `hedged-dx` landed, and `test_thirty_one_committed_cases` still passed because `all_cases()` enumerated four fixture directories and not the fifth. Surfaced by reading [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94) and [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96), which are about the allergy box; the ticket is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

  **Today it is 37 across six sets** — `git ls-files 'fixtures/*/shorthand/case-*.md' | wc -l` — and `duration-span` and `hedged-dx` were the two the enumerator could not see. **The example is left standing with its original numbers and its retired symbol names *and* the current figure beside it on purpose**: a worked example of a figure going stale is worth little if the example is quietly kept current, and this one had gone stale twice while sitting in the paragraph warning about exactly that.

  **#143 is closed**, ruled 2026-08-19: the enumerator is a glob and the classification stays explicit per case. **Two assertions hold it and neither is enough alone** — `test_the_denominator_is_every_committed_shorthand_input` says who is counted, and `test_no_other_committed_case_writes_either_slot` says the classification covers them. A seventh set writing neither slot in any of its cases clears the second one in silence, which is why the first exists; a seventh set whose cases nobody classifies clears nothing. **What is worth carrying forward is not the arithmetic.** Nothing in the repair depended on knowing the right number — what the four-directory list cost was that the one assertion whose job was to notice read as though it had.

**Neither would ever be reached by asking "which tickets does my work move."** The connection runs the other way: the ticket knows something about the repo that your work does not know it needed. A relevance filter can only select on what you already understand, which is exactly the wrong instrument for finding what you have missed.

**The expected verdict is "untouched", and most of them will be.** Of the 38 swept afterwards, 26 were untouched and saying so plainly is the correct output — a sweep that finds something in every ticket is not being skeptical enough. Fan the reading out across subagents if the tracker is long; that is what they are for, and this repo already authorizes them. Take each verdict as a claim and re-derive any figure before writing it anywhere.

### What a sweep looks for

Not "is there a ticket about this file." **Take what the work actually established and ask which tickets it moves — then read the rest anyway.** Four shapes recur, and the last two are the ones that get missed:

1. **A new gap** — a rule shipped with nothing scoring it, a limb no fixture reaches. File it.
2. **Live evidence for an open ticket** — you hit the thing it describes. Comment with the date, the command, and what it cost you. A `grilling` ticket with dated instances is easier to rule on than one with an argument.
3. **A claim in an open ticket that your work proved wrong.** This is the highest-value shape and the least likely to be looked for, because it means reading tickets you were not working on. #130 said #69 and #97 had no recoverable anchor; both had one, in the fixture prose that filed them, and finding that turned two dead tickets into two answerable ones.
4. **A cross-reference that has gone stale** — a ticket pointing at a sibling that has since closed, a paragraph naming a case that a later ruling removed. #65 pointed at #49 as the other encounter to search for in one pass; #49 closed, and the pairing sat there reading as live.

### The commands

```bash
gh issue list --state open --limit 100 --json number,title,labels \
  --jq '.[] | "\(.number)\t[\(.labels|map(.name)|join(","))]\t\(.title)"'
```

That list is the **work list**, not a menu — every number on it gets read and gets a verdict. Reading the titles first is fine for deciding what order to go in, and it is not a filter. **Search the artifact for anything you are about to file** — that section is above and it is not weakened by this one; a sweep files *more* tickets, so it is exactly when duplicates get written.

**That command hides pull requests, and it is the right command anyway — as long as you know which.** `gh issue list` excludes them by design, so the work list above is issues only. That is correct for a sweep of open *tickets*, and it is wrong the moment you use the same command to reason about *every record on the tracker*: #130's own reproduce command did exactly that, and sweep after sweep re-derived a population two members short without one of them being able to notice. When the question is about all records, use the REST endpoint, which returns both and marks pull requests with a `pull_request` key:

```bash
gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100"
```

**When a ticket names a fixture row or a skill passage, grep the repo for its number before believing it is unrecoverable:**

```bash
grep -rn "issues/69)" --include="*.md" fixtures/ skills/ docs/
```

The paragraph that filed a ticket usually cites it, and that paragraph is a specification the ticket body may no longer hold.

### What not to do

- **Do not file a ticket for every observation.** A finding earns one when someone could act on it — a decision to make, a gap to close, a claim to check. An observation with no such handle belongs in a comment on the ticket it bears on, or nowhere.
- **Do not re-file something already ruled acceptable.** #50 ruled the account-profile hole out of scope deliberately; `CLAUDE.md` says so by name precisely so it does not come back. `--state all` in the search is what catches this.
- **Do not close a ticket your work did not settle.** Narrowing one is a comment, not a closure.
- **Do not restate a ruling you made up.** A reconstructed body says it is a reconstruction, names the lines it was rebuilt from, and marks which parts are inference — #69 and #97 both carry that header.

### Ticket text takes standing rule 4

**Everything the repo emits, which includes ticket bodies, comments, PR bodies and commit messages.** Since [#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104), the local `commit-msg` hook checks a commit message against the listed forms, advisory; ticket bodies, comments and PR bodies remain the clinician's explicit manual surface because no local hook owns them. **A clean `spelling_scan` run says nothing about a ticket you just filed**, and the table it holds is narrower than the language. **Do not quote its width here** — derive it, because the figure in this sentence went stale twice on 2026-08-18 alone:

```bash
python -c "import sys; sys.path.insert(0,'tools'); import spelling_scan as s; print('TABLE', len(s.TABLE), 'FORMS', len(s.FORMS), 'ALL_FORMS', len(s.ALL_FORMS))"
```

**It prints three numbers on purpose, because there are three and picking the wrong one is how this went wrong twice.** `FORMS` is `TABLE` plus the stem changes; `ALL_FORMS` is `FORMS` plus the drug names. **The first repair of this paragraph shipped `len(FORMS) + len(STEM_CHANGES)`**, which double-counts the stem changes and prints a number the table has never held — a command that exits clean and returns a wrong answer, which is [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s own failure mode reproduced inside the fix for it. Caught by a sweep subagent before it merged.

**The worked case is this sentence's own history and it is worth keeping.** It read *the table is 28 entries wide: `judgement` and `neighbouring` are both British, both absent from it, and both shipped in ticket text on 2026-08-15 before being caught by hand.* **The number was wrong when written and the examples were true.** `TABLE` was 25 at the commit that wrote it, 26 on `origin/main`, 28 today — so `28` has matched a quantity for none of its life until it accidentally matched `FORMS` this week. Two sweep agents derived the original figure as two different quantities and neither could settle which was meant, which is the tell. Then both forms were added to the table on 2026-08-18 — and the sentence had **named them as invisible without anyone checking where else they were sitting.** Both were in the committed run record at `fixtures/filled-anchor/notes/`: `neighbour` twice, `judgement` three times, uncounted since the run because the table did not hold either form.

**Naming a form in prose is not adding it to the table.** A warning about ticket text is worth writing; it is not a substitute for the one-line change that makes the scanner see the form everywhere else.

**Read the body back after posting**, which the `@-` trap section already asks for and which costs one command:

```bash
gh issue view <number> --json body --jq '.body | length'
```
