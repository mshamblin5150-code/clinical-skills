# A scanner's status read through a pipe is refused before the command runs

**Measured at:** dae512ff969c4eb8b3eaf44f211c11990eae910b

[#1457](https://github.com/mshamblin5150-code/clinical-skills/issues/1457) was filed from the
after-action review of a `batch-shift` run. A shell loop printed `exit=$?` after a pipe, so every
exit it reported belonged to the last pipe stage and not to the scanner. The orchestrator noticed
only on reading its own output, after the approval record had been written, and re-ran six
scanners, the agreement read, the manifest and the freshness gate, re-rendered the Review sheet and
re-recorded approval. The rule against it was already written in the clinician's agent memory and
had failed repeatedly. Grilled 2026-10-08 against `main`, where the freshness gate read `FRESH`;
the clinician ruled every point below in that session. **Nothing is built here; this is the record
the build reads.**

## Measured before ruling

### The recorded instances take three shapes, and the ticket's proposal named one

The written rule in the clinician's agent memory records its own failures. They fall into three
shapes, each a status that passed through a second process before anything read it:

- **A pipe followed by a `$?` read.** A publish-hook pre-grade piped through `tail` and followed by
  `echo EXIT=$?` printed 0; the hook had exited 2. #1457's own instance is this shape inside a loop.
- **A pipe that ends the command, so the harness reports the last stage's status.** The complete
  suite piped through `tail` was reported as exit 0 twice while its output read `FAILED`.
- **A pipe followed by `&&`.** The freshness gate piped through `head`, `tail` or `cut` and joined
  to a publication by `&&` printed `STALE` four times, and each time the publication went out.

#1457 proposed refusing the first shape only. That would leave every recorded instance of the
second and third outside the guard.

### Hidden status is the common case

#1457's comment of 2026-10-03, from the grilling of
[#1206](https://github.com/mshamblin5150-code/clinical-skills/issues/1206), measured the
clinician's retained Claude Code transcripts in the spans before each compaction: of 292 graded
runs of a `tools/` script, the agent never saw the script's own status in 166. 104 were piped and
106 were chained behind `;`, with heavy overlap. Those figures are private, nothing committed
re-derives them, and that comment is their only record. No ruling below rests on their exact
values; they price how often a guard of each width would fire.

### PowerShell keeps the status through its own filters

Measured live 2026-10-08 in PowerShell 7.6.6 on the clinician's machine, with a command that exits
1 and prints one line:

- **Piped into a PowerShell command** (`Select-Object -Last 1`, `Select-String`): `$LASTEXITCODE`
  stayed 1, `$?` read False, a following `&&` did not run, and Claude Code's PowerShell tool
  reported exit code 1.
- **Piped into a separate program** (`findstr`): `$LASTEXITCODE` read 0 and the tool reported
  success.
- `tail`, `head`, `grep` and `cut` do not resolve in that shell.

**What the instrument would have printed if the claim were false:** a `$LASTEXITCODE` of 0 and an
`&&` branch that ran, after the cmdlet filter. It printed 1 and the branch did not run, while the
same command into `findstr` printed 0, so the measurement separates the two cases.

### Codex registers no pre-command hook today

The clinician's `~/.codex/hooks.json` registers `Stop` and `PreCompact` hooks only. Whether the
installed Codex offers a hook that runs before a shell command and can refuse it was not
established by reading its files, the same unknown
[ADR 0281](0281-a-command-result-stated-after-a-compaction-is-re-observed-or-labeled-and-a-compaction-hook-says-so.md)
ruling 6 met at the compaction boundary.

## Ruling 1 — the defect is a piped scanner status that something reads

A command is matched when a `tools/` script feeds a pipe and the pipe's status is then read by any
of: a `$?` expansion, `&&`, `||`, an `if`, `while` or `until` test, or the end of the command,
where the harness reports the pipe's status as the command's. A pipe inside a loop body is read the
same way, and #1457's loop is a required positive control.

A plain `;` chain is not matched. It hides a status rather than printing a wrong one, and
[standing rule 7](../../AGENTS.md) already declines to count such a run as an observation after a
compaction.

## Ruling 2 — a match is refused before the command runs

The hook denies the command and names the remedy. It does not rewrite the command and does not
merely advise. The written rule failed repeatedly as an instruction, and a rewrite to `pipefail`
would misreport in the other direction, ruling 6.

The refusal names the redirect form first, because nothing added to the line later can break it:

```bash
python tools/<name>.py > <file> 2>&1; echo "exit=$?"
```

followed by a `grep` of the file for the finding lines.

## Ruling 3 — the examined commands are the scripts in `tools/`

A pipe stage is examined when it runs `python tools/<name>.py` and that file exists in the
checkout the hook runs from when the hook runs. Nothing is a hand-kept list, so a new scanner is
covered on arrival. `git`, `gh` and a direct `python -m unittest` are outside it; the complete
suite has one documented interface, `tools/suite.py`, which is inside it. The spellings of the
interpreter and of the path that the reader recognizes are its declared limits.

## Ruling 4 — Codex is covered, and a live test decides how

The build first tests live whether Codex can run a hook before a shell command and act on its
refusal.

- **If it can,** the installer registers the guard in `~/.codex/hooks.json` beside existing hooks,
  on the pattern of `tools/install_grilling_guard.py` and `tools/install_run_status_guard.py`, and
  a repeat run replaces only its own registration.
- **If it cannot,** the installer writes the rule into a marked block in the user-level
  `~/.codex/AGENTS.md` and reports that Codex received the written rule only.

## Ruling 5 — PowerShell is unread, and the measurement is the declared reason

Claude Code's Bash and Monitor tools are read through the shared command reader, as the heredoc
guard of [ADR 0291](0291-a-writing-pass-stages-patient-text-in-a-scratch-root-and-a-hook-refuses-heredoc-writes-there.md)
ruling 5 reads them. The PowerShell tool is not read and not refused. The guard's declared limits
state why, with the measurement above and its date: PowerShell's own filters preserve the status,
and only a pipe into a separate program loses it. A recorded PowerShell instance is the evidence
that reopens this.

## Ruling 6 — two status-reading forms pass

A piped `tools/` script passes when either holds:

- **No second process reads its output**: the redirect form of ruling 2.
- **`${PIPESTATUS[N]}` is read in the very next command**, where `N` is the script's own stage in
  that pipeline. Anything between the pipeline and the read, or the wrong index, is refused. A
  pipeline that ends the command has no next command to read it and is refused.

A preceding `set -o pipefail` does not pass. It makes a clean scan piped into a `grep` that matches
nothing report 1, which this repository's exit vocabulary reads as a finding, and it can report a
broken pipe from `head` as a failure that never happened.

## Ruling 7 — #1457 carries the whole build

The hook, its registration beside the existing `PreToolUse` hooks in `.claude/settings.json`, the
Codex live test and installer, the declared limits and the tests are one build on #1457.

## Rejected options

**The ticket's narrow trigger, a pipe followed by `$?` only.** It misses every recorded instance of
the other two shapes, including all of the freshness-gate publications.

**Adding plain `;` chains.** It roughly doubles the firings for a shape that prints no wrong number.

**Advising instead of refusing.** The wrong number still arrives in the same run, and the advice is
the written rule that already failed.

**Rewriting the command to `pipefail`.** Ruling 6.

**Every command rather than `tools/` scripts.** It refuses the many `git log | head` and
`gh … | python` reads whose status is rarely the point.

**Only the graders with the 0/1/2 contract.** Membership has no mechanical test in the tree, so it
would need a hand-kept list that a new scanner arrives outside of.

**A PowerShell parser, or refusing every PowerShell pipe unread.** The first builds a reader for a
narrow measured hole; the second refuses the common cmdlet filter the measurement shows is safe.

**Codex as its own ticket.** The measurement found the shape most often there.

## Consequences

**A piped `tools/` status can no longer be read by the shell or the harness in Claude Code's Bash
and Monitor tools** without passing ruling 6.

**`.claude/settings.json` gains a third command-shape `PreToolUse` refusal**, beside the publish
hook and the heredoc guard.

**The Codex installer branch records which form Codex received.**

## What this does not reach

**A status hidden behind a plain `;` chain.** Ruling 1 leaves it to standing rule 7 and to the
reader.

**A piped status in Claude Code's PowerShell tool**, through a pipe into a separate program.
Ruling 5.

**A command the shared reader cannot parse, or a script invoked by an unrecognized spelling.**
Those are the build's declared limits, not findings.

**Whether a status that was seen is reported truthfully.** The guard ensures the status read is
the script's own; what an agent then says about it is
[ADR 0281](0281-a-command-result-stated-after-a-compaction-is-re-observed-or-labeled-and-a-compaction-hook-says-so.md)'s
subject.
