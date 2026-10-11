# Stdin is put on UTF-8 by the call that moves stdout and a bad byte is replaced

**Measured at:** 44375202245c22ed0c8502727d4cb2de9b0f0771

[#1520](https://github.com/mshamblin5150-code/clinical-skills/issues/1520) was filed from the
triage of #1456 on 2026-10-03. That ticket found `run_status_stop_hook` reading its payload with
`json.load(sys.stdin)`: `console_codec.use_utf8()` moves stdout and stderr onto UTF-8 and leaves
stdin on the Windows locale codec, so a UTF-8 payload's em dash arrived as mojibake and stopped
matching the grammar that required it. The same text-mode read appeared in other command paths.
Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the clinician ruled every
point below in that session. The figures below were re-derived after `main` moved during the session's
tracker sweep, and they held. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The defect reproduces here.** UTF-8 bytes for `a—b` piped into `python -c` on this machine report
`sys.stdin.encoding` as `cp1252` and decode to `a\xe2€”b`. The same bytes after
`sys.stdin.reconfigure(encoding="utf-8")`, called before the read, decode to `a—b`. The stream's
default error handler here is `surrogateescape`, so today a byte cp1252 does not map, such as `0x81`,
arrives as a lone surrogate rather than raising. A byte that is not valid UTF-8 under
`errors="strict"` raises `UnicodeDecodeError` at the read.

**Fourteen command files still read stdin in text mode.** `git grep -n "sys.stdin" -- 'tools/*.py'`
with tests and `stdin.buffer` excluded prints `browser_tab_hook`, `closing_keyword_scan`,
`command_tool_roster`, `grilling_stop_hook`, `heredoc_write_hook`, `implementation_map_post_hook`,
`procedure_codes_build`, `project_context`, `scanner_pipe_hook`, `skills_mirror`,
`tracker_branch_scope`, `tracker_filed_from`, `tracker_merge_receipt` and `tracker_publish_hook`.
The ticket body named eleven; its sweeps added `tracker_filed_from`, which reads
`json.load(sys.stdin if stdin is None else stdin)` and is invisible to a search for the literal
`json.load(sys.stdin)`, and the two guards built after it was filed. A search for `input(`,
`fileinput`, `open(0`, `FileType` and `TextIOWrapper` found no other spelling.

**Four files read raw bytes, with three postures on a bad byte.** `tracker_bodies` decodes with
`errors="replace"`; `compaction_reminder` exits 0; `run_status_stop_hook` grades an empty payload.
`tracker_publish_stub` decodes only a copy, to test for `gh`, and forwards the original bytes
unchanged to the full publish hook.

**Every one of those eighteen files already calls `use_utf8()` under its `__main__` guard**, and
`test_console_codec.EveryToolTakesIt` parses every non-test `tools/*.py` carrying that guard and
fails one that does not make the call.

**What a strict decode would reach.** A raised decode error would land in each site's existing
handler. `heredoc_write_hook` and `scanner_pipe_hook` catch it and exit 0, letting the command run
unread. `browser_tab_hook`, `grilling_stop_hook` and `implementation_map_post_hook` do not catch it
and exit 1 with a traceback. `tracker_publish_hook` catches it and returns a failure note with no
deny. The piped commands without a handler exit 1, which this repository's exit convention reads as
a finding. `command_tool_roster` and `tracker_filed_from` already convert it to exit 2.

**The run-status Stop hook fails open too.** `run_status_stop_hook.main` catches
`(UnicodeError, json.JSONDecodeError, OSError)` and grades an empty payload, and `handle` returns no
response when the payload names no transcript, so the stop proceeds. Its `DECLARED_LIMITS` do not
name this. ADR 0339, ruled on #1519, also edits `tools/run_status_stop_hook.py`, so whichever of the
two builds lands second rebases onto the first.

**A hook payload cannot carry an invalid byte sequence in practice.** The harness serializes the
payload as JSON and sends it as UTF-8, so the hooks the ticket worried about, the publish hook among
them, are not expected to reach the replacement path. A hand-piped file into one of the command-line
readers is the reachable case.

## Ruling 1 — `use_utf8()` moves stdin too

`console_codec.use_utf8()`, called with no arguments, reconfigures `sys.stdin` onto UTF-8 alongside
stdout and stderr. No text-mode read site is edited for the codec. `EveryToolTakesIt` is the guard
against a future unprotected read: a command that reads stdin without calling `use_utf8()` already
fails it, whatever spelling the read takes. The docstring of `use_utf8` and the **Console codec**
section of `CLAUDE.md` state that the input end is now covered and why.

A shared reading function called at every site was declined: it makes the decode visible at each
read, at the price of fourteen edits and a new AST check that is a floor, blind to a read routed
through a variable, which is the spelling the ticket's own search missed. Fixing each site by hand,
as #1456 did, was declined as fourteen copies of one rule with nothing to hang a check on.

## Ruling 2 — an undecodable stdin byte is replaced

Stdin takes `errors="replace"`, the setting stdout and stderr already use. Nothing crashes on input
encoding, and the replacement character stays visible in anything printed.

Strict decoding was declined because the outcome would fall to the handlers measured above: two
guards would let the command run unread, several commands would report a crash as a finding, and the
publish hook would allow. Strict decoding with every handler repaired in this build was declined as
roughly ten hand-written handlers, the per-site copying ruling 1 refused. The publish-hook concern in
the ticket, grading text that differs from what `gh` sends, is not reachable through a harness
payload.

## Ruling 3 — the three byte decoders converge and the stub keeps its bytes

`tracker_bodies`, `run_status_stop_hook` and `compaction_reminder` read plain `sys.stdin`, so every
site that decodes stdin follows one rule. `run_status_stop_hook` and `compaction_reminder` therefore
grade replaced text rather than giving up on a bad byte. `compaction_reminder`'s comment naming this
ticket's helper as not yet landed goes with the edit.

`tracker_publish_stub` keeps reading `sys.stdin.buffer`, with a comment stating that it forwards the
payload unchanged to the full hook. Reading it as text would make the full hook grade a re-encoding
rather than the bytes the harness sent. Leaving all four byte readers alone was declined because two
of them would keep a bad-byte posture different from every other site.

## Ruling 4 — one discriminating drive and a unit test

One subprocess test drives a stdin-reading hook with a raw UTF-8 payload whose output depends on a
non-ASCII character in that payload. #1456's run-status hook is the natural candidate, and the
builder chooses. The child process runs with `PYTHONIOENCODING=cp1252`, so the test reproduces the
Windows default on any platform, and it must fail when the stdin line is removed from `use_utf8()`.
A unit test asserts that `use_utf8()` called with no arguments moves stdin.

Driving every stdin-reading command was declined: seventeen hand-built payloads would mostly re-prove
one function that the call check already shows every site uses. A unit test alone was declined
because nothing would show a real process decoding a real payload, which is how #1456 was found.

## Ruling 5 — the fail-open guards are a separate decision

`heredoc_write_hook` and `scanner_pipe_hook` exit 0, `tracker_publish_hook` allows, and
`run_status_stop_hook` lets the stop proceed when they cannot read their own payload. No ADR,
including ADR 0291 and ADR 0299, and no guard's declared limits rule on that, and the tracker held no
ticket for it. After ruling 2 an encoding error no longer
reaches those handlers; malformed JSON and a failed read still do. The question of whether a guard
may fail open goes to its own ticket for a decision and stays outside #1520.

## Build checklist

- `tools/console_codec.py`: `use_utf8()` with no arguments reconfigures `sys.stdin` with
  `encoding="utf-8"` and `errors="replace"`, falling back to the error handler alone as it does for
  output streams; its docstring covers the input end.
- `tools/tracker_bodies.py`, `tools/run_status_stop_hook.py`, `tools/compaction_reminder.py`: read
  `sys.stdin` rather than `sys.stdin.buffer` with a hand decode.
- `tools/tracker_publish_stub.py`: a comment stating why it keeps reading bytes.
- `CLAUDE.md` **Console codec**: the paragraph on the input end of the boundary states that stdin is
  covered by the same call.
- Tests: the unit test of `use_utf8()` moving stdin; the cp1252-forced subprocess drive, shown red
  with the stdin line removed.

## What this record does not reach

- **A read before `use_utf8()` runs.** A module that reads stdin at import, or anywhere before its
  `__main__` guard calls the helper, gets the locale codec. None does today.
- **A caller that imports `main()`.** Tests that call `main()` in process get no reconfiguration,
  which is already true of stdout.
- **A command outside `tools/`.** `EveryToolTakesIt` walks only that directory.
- **Whether replaced text was meant.** A hand-piped file with a bad byte is graded on the replaced
  text with no separate signal beyond the visible replacement character.
- **Whether a guard should fail open on an unreadable payload.** Ruling 5's ticket owns that.
