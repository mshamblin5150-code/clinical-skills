# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues on `mshamblin5150-code/clinical-skills` (private). Use the `gh` CLI for all operations.

**Maintainer tooling.** This file configures Matt Pocock's engineering skills for whoever maintains the repo. It is not a dependency of the clinical skills — anyone consuming `skills/` via [AGENTS.md](../../AGENTS.md) needs none of it.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment**: `gh issue comment <number> --body "..."`
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

`gh` infers the repo from `git remote -v` when run inside the clone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Note on triage labels

The `triage` skill is not installed in this environment, so no label vocabulary is configured. If it is installed later, run the setup again to add `docs/agents/triage-labels.md`.
