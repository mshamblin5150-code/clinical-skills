# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues on `mshamblin5150-code/clinical-skills` (private). Use the `gh` CLI for all operations.

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

**Verify after creating anything with a long body:**

```bash
gh issue view <number> --json body --jq '.body' | head -5
```

A body of `@-`, or an empty body, means it was eaten. Fix it with `gh issue edit <number> --body-file -`.

## Pull requests as a triage surface

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

Label at creation time. Coming back to label later is the step that gets skipped.

## Finishing a ticket means sweeping the tracker, and you are authorized to do it

**A merged PR is half of finishing.** The other half is that the work found things, and those things belong on the tracker before the session ends. **Do it without asking** — updating an existing ticket and filing a new one are both standing authorization here, on the same footing as spawning subagents. What needs permission is changing a *ruling*; recording what you found does not.

**The reason is the one #59 was filed about, arriving one level up.** That ticket exists because a decision got resolved inside an implementation and shipped, discoverable only by reading a merged diff. A finding that stays in the diff is the same defect in a cheaper form: the next session re-derives it, or does not, and nothing says which.

### Every open ticket, not the ones that look relevant

**The sweep is exhaustive. Read every open ticket, one at a time, and record a verdict for each.** Not the ones whose titles look related — *all* of them. Ruled 2026-08-15.

This is the rule most likely to be quietly narrowed, because narrowing it feels like judgment rather than like skipping. A session settling [#63](https://github.com/mshamblin5150-code/clinical-skills/issues/63) swept 9 of 39 open tickets, picked by which titles sounded connected, and reported that as the sweep. Everything it picked was genuinely connected — and the two findings that mattered most were both outside the selection:

- **A latent defect in the code that session had just merged.** Its new guard sweeps `fixtures/` with a bare three-digit match and had no exemption for `fixtures/filled-anchor/notes/`, the preserved run record [ADR 0001](../adr/0001-fixture-asserts-on-named-findings.md) forbids editing. Surfaced only by reading [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137), which is about that directory and has nothing to do with catalog denominators.
- **A stale figure restated in many files at once.** "The 31 committed fixture inputs" became 34 when `hedged-dx` landed, and `test_thirty_one_committed_cases` still passed because `all_cases()` enumerated four fixture directories and not the fifth. Surfaced by reading [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94) and [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96), which are about the allergy box; the ticket is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

  **Today it is 37 across six sets** — `git ls-files 'fixtures/*/shorthand/case-*.md' | wc -l` — with `duration-span` and `hedged-dx` the two the enumerator cannot see, and the gap is now pinned by a test rather than latent. **The example is left standing with its original numbers *and* the current one beside it on purpose**: a worked example of a figure going stale is worth little if the example is quietly kept current, and this one has now gone stale twice while sitting in the paragraph warning about exactly that.

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

**Everything the repo emits, which includes ticket bodies, comments, PR bodies and commit messages.** Nothing checks any of them — `tools/spelling_scan.py` reads tracked Markdown, and an issue body is neither — so this one is on you, and [#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104) is where the gap is tracked. **A clean `spelling_scan` run says nothing about a ticket you just filed**, and the table it holds is narrower than the language. **Do not quote its width here** — derive it, because the figure in this sentence went stale twice on 2026-08-18 alone:

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
