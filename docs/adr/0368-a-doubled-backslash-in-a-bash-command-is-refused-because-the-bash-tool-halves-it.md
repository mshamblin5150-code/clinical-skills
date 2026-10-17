# A doubled backslash in a bash command is refused because the bash tool halves it

**Measured at:** 84418797c3451c4f6d5076e0d93ad83958308832

[#1581](https://github.com/mshamblin5150-code/clinical-skills/issues/1581) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). The run wrote a file
through a Bash heredoc whose body carried backslash escapes, and the file arrived with real line
breaks where escaped ones were meant. A memory note about heredocs already existed and was heeded
once in the same sitting before it failed. A later comment recorded a third instance, a batch-shift
orchestrator writing a Review-sheet builder script. The ticket proposed a heredoc-body limb in
`tools/heredoc_write_hook.py`. Grilled 2026-10-16 against `main`, where the freshness gate read
`FRESH`; one session began the grilling and froze, and a second took it over from that session's
transcript. The clinician ruled every point below. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

### The damage is the Bash tool's, not the heredoc's

On this machine, with Claude Code 2.1.284, the Bash tool halves every run of backslashes before Git
Bash reads the command: two become one, four become two, three become two. A lone backslash
survives. The halving happens inside single quotes, in a quoted `<<'EOF'` heredoc, in unquoted text
and in `python -c`, so a heredoc is one place it lands rather than its cause. The Monitor tool halves
the same way. The PowerShell tool and the Write tool keep both backslashes; the bytes were read
back. The session transcript records the tool input with both backslashes, so the halving happens
when the tool executes, after the input that a `PreToolUse` hook is given is formed. The upstream
tracker already carries this defect several times, among them
[anthropics/claude-code#85856](https://github.com/anthropics/claude-code/issues/85856),
[#97409](https://github.com/anthropics/claude-code/issues/97409) and
[#100063](https://github.com/anthropics/claude-code/issues/100063).

### Double quotes sometimes undo the damage

Inside double quotes Git Bash itself turns `\\` into `\`, so when the next character is not `$`, a
backtick, `"`, `\` or a line break, the halved command produces the same text the unhalved one would
have. `"a\\b"` and `python -c "...'x\\ny'..."` run as intended today. Single-quoted, heredoc and
unquoted doubled backslashes, and doubled backslashes before those special characters, are damaged.
The first grilling session stated that no command containing `\\` runs as written; that was false
for this case, and the clinician re-ruled with it corrected.

### The guard the ticket proposed extending could not have reached the recorded instances

The batch-shift instance was `python - "$S" "$D" <<'PYEOF'` writing through `Path(sys.argv[2])`.
`heredoc_write_hook` could not resolve that target and attached only its unread note; the command
carried six doubled backslashes, and the written script held a real backspace and a real tab inside
a Windows path. In #1563's instance the damaged text was built in a Python variable before the write,
and the body's own doubled escaping was itself halved in transit. A limb keyed on a heredoc body that
becomes file content, or on a resolved target, misses both.

## Ruling 1. The check fires on any doubled backslash in a Bash or Monitor command

The trigger is two consecutive backslashes anywhere in the command text, whether or not the command
writes a file, uses a heredoc, or lands in `scratch/` or `output/`. That is exactly the text the tool
changes. The ticket's three open questions, which bodies count, target scope and whether only file
content counts, are answered by this trigger rather than separately.

## Ruling 2. A match is refused, and a correct double-quoted command is a declared cost

The hook denies the call and names the remedy: put the content in a file with the Write tool and run
that file, or write a single backslash where the shell keeps it literal. A warning was declined
because it arrives after the damage and repeats the memory note's failure mode three times recorded.
Limiting the refusal to the contexts where the result changes was declined because it needs a shell
quote parser, and a command that parser cannot read would pass unread, which is how every recorded
instance escaped. So a correct double-quoted `\\` is refused. Its fix, one backslash, is correct
whether or not the harness defect is present. The refusal message and the hook's limits state this
false-refusal case rather than claiming none.

## Ruling 3. The check is its own hook, not a limb of the heredoc guard

The build adds `tools/backslash_pair_hook.py`, registered in `.claude/settings.json` as a
`PreToolUse` hook for `Bash|Monitor`. It reads the command field of the payload and does no shell
parsing. Placing it inside `heredoc_write_hook` was declined: a refusal of a `python -c` command
would come from a module documented as a heredoc and private-root guard, and the limb would sit
behind that module's parser and its blanket exception handler, so an unrelated parse failure could
switch it off. ADR 0291's guard is unchanged and keeps its own subject.

## Ruling 4. An unreadable payload is allowed with a visible note, and #1728 governs it

When the payload is not readable JSON, or its command field is absent or not text, the hook allows
the call and attaches a visible `backslash check: unread` note, the shape `heredoc_write_hook`
already uses for an unresolvable target. Blocking was declined because it would pre-empt
[#1728](https://github.com/mshamblin5150-code/clinical-skills/issues/1728), which is open on exactly
this question for the existing guards. Silent allowing was declined because it is the defect #1728
was filed over. This hook joins #1728's population, and whatever that ruling decides binds it too.

*Superseded 2026-10-17.* The words "the hook allows the call and attaches a visible `backslash check: unread` note" are superseded by [ADR 0392](0392-a-guard-that-cannot-read-its-payload-refuses-only-on-its-own-trigger-in-the-raw-text.md) ruling 1. The hook refuses an unreadable payload whose raw text carries four consecutive backslashes and allows the rest with the note. Placing this hook under #1728's ruling, and declining a silent allow, still stand.

## Ruling 5. One exact probe command is exempt so the block can be retired

The hook allows exactly `printf '%s\n' 'backslash-probe: a\\b'` and nothing else. Its output shows
one backslash while the defect stands and two once it is fixed; two means the hook's reason is gone
and a ticket retires it. No hook or test runs a command through the tool's execution path, so the
probe cannot be automated. The refusal message and the hook's limits name the probe. The limits also
record the measurement this ruling rests on: 2026-10-16, Claude Code 2.1.284, and the upstream
reports above. No new upstream report is filed.

## Ruling 6. Registration is repo settings only

The hook is registered in the tracked `.claude/settings.json`, like every other guard, so the copy
under test is the copy that runs. Sessions in a checkout older than the build, in other repositories,
and in Codex are outside its reach, and its limits say so. A user-level installer was declined:
it would run the check twice in a current checkout and let an installed copy drift from the tested
one.

## Ruling 7. The build is believed on a planted payload and the live probe

Tests drive the hook's public command with payloads carrying a heredoc body with `\\n`, a
single-quoted `\\b`, a `python -c` argument with `\\n`, a double-quoted `"a\\b"` (refused, the
declared cost), a lone backslash (allowed), the exact probe (allowed), the probe with one extra
character (refused), a Monitor payload, and malformed and non-object payloads (allowed with the note).
Before merge the builder runs one real Bash call carrying `\\` in the session and confirms the hook
saw both backslashes and refused it. That confirms the payload is formed before the halving, which
the transcript shows but no test can.

*Superseded 2026-10-17.* The words "and malformed and non-object payloads (allowed with the note)" are superseded by [ADR 0392](0392-a-guard-that-cannot-read-its-payload-refuses-only-on-its-own-trigger-in-the-raw-text.md) ruling 6. Malformed and non-object payloads are tested both with and without the trigger. The other planted payloads and the live probe before merge still stand.
