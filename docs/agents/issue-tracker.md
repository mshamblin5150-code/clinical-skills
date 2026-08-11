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
