# Codex scanner pipe hook probe

ADR 0299 ruling 4 required a live pre-command refusal test. On 2026-10-08,
`codex-cli 0.162.0-alpha.2` ran a disposable project under
`scratch/sessions/issue-1457-probe/` with `codex exec --ephemeral
--skip-git-repo-check --dangerously-bypass-hook-trust --json`.

The project-local `.codex/hooks.json` probe did not block the command. The
user-level `~/.codex/hooks.json` probe registered a temporary `PreToolUse`
command with matcher `.*`. The hook returned:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"ISSUE1457_LIVE_DENY"}}
```

The requested command was `Write-Output ISSUE1457_EXECUTED`. The command did
not execute; the live router reported `Command blocked by PreToolUse hook:
ISSUE1457_LIVE_DENY`. A second user-level probe captured stdin before denying.
It supplied `tool_name: Bash`, `tool_input.command` and the disposable project's
`cwd`, matching the shared command reader's input contract. The CLI normalized
this shell call to Bash even though its host shell was PowerShell; the guard's
shell boundary remains the tool name supplied by the runtime.

The temporary user hook file was restored byte for byte in a `finally` block
after each probe. The bypass flag admitted only the deliberately authored probe
hooks for those invocations; the installer does not enable bypass or modify trust.

A final integration probe registered `tools/scanner_pipe_hook.py` itself with
matcher `Bash|Monitor`, requested `python tools/spelling_scan.py | tail -5` from
the checkout, and received `Scanner pipe refused` before command execution.
It stopped without retrying or rewriting the command. This tested the actual
guard and matcher, in addition to the generic deny response above.

**Selected branch: mechanical PreToolUse hook.**
`tools/install_scanner_pipe_guard.py` registers the guard beside existing
user-level hooks and refreshes only its own handler on a repeat run. Codex
hook trust is managed through `/hooks`. The written-rule fallback was not selected.
This establishes refusal in the measured CLI with admitted hooks, not that every
desktop session automatically reloads or trusts a newly registered hook.
