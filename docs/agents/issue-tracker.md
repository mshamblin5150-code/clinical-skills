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
