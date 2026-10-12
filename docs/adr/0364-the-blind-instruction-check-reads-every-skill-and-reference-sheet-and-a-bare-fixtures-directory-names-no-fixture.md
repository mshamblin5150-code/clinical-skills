# The blind-instruction check reads every skill and reference sheet, and a bare fixtures directory names no fixture

**Measured at:** ac4bfe0f2866eb172b84c7bb591259387df193c6

[#776](https://github.com/mshamblin5150-code/clinical-skills/issues/776) asked to bring the root
`README.md` under `tools/test_blind_fixture_instructions.py`, the check that refuses a required
instruction naming a concrete fixture set, path, numbered case or run, or assertion row. The ticket
found that adding the file first would fail the suite on correct prose, because the check's path
pattern fires on a bare `fixtures/` that names nothing. Grilled 2026-10-12 against `main`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

Every figure was taken by importing the test module at the commit above and calling its own
`REQUIRED_INSTRUCTIONS` and `findings()`, never by reading the pattern source.

**The checked population is 204 files.** It is `AGENTS.md`, two named `reference/` sheets, every
Markdown file under `skills/`, and the threshold-sheet directory. `README.md` returns exactly one
finding, the bare `fixtures/` row of its Layout block, which names no set, case, run, row or score.
The checked population returns none.

**The bare shape is wider than the README.** It also stands three times in `CLAUDE.md` and in eight
decision records, one of them eleven times. None of those files is checked, so nothing has failed.

**Twenty-six tracked `reference/` Markdown files sit outside the check and return zero findings.**
They include the UpToDate topic sheets, the CPT E/M sheet, the procedure-code and ICD-10-CM coding
reads and the guideline catalog. `icd10-cpt`, `clinical-note`, `practicum-case-study` and
`vitalsource-chrome` point at several of them, so by the rule's own ground they are required
instructions the check never read.

**`CLAUDE.md` is part of every fixture-generating pass's prompt.** Claude Code's subagent
documentation states that every built-in and custom subagent loads the project `CLAUDE.md` unless
its definition opts out; only the built-in Explore and Plan agents skip it. `fixtures/README.md`
runs generating passes as ordinary subagents in the repository. The ticket body assumed the
opposite. `CLAUDE.md` returns 38 findings, many of them concrete fixture sets and assertion rows.

**The remaining candidates were priced.** `CONTEXT.md` returns zero findings and is edited by
nearly every grilling session. `docs/adr/` holds 361 records, 54 of them with findings, 240 in
all. `docs/agents/issue-tracker.md` returns five.

## Ruling 1 — a bare `fixtures/` with nothing after the slash passes

`CONCRETE_FIXTURE_PATH` is narrowed so that `fixtures/` followed by whitespace, a backtick, a
closing bracket or parenthesis, sentence punctuation or the end of the line does not match. Any
character that begins a path segment after the slash still matches, so `fixtures/day-a/...`, a
wildcard form such as `fixtures/*/assertions.md` and a placeholder form such as `fixtures/<set>/`
all stay refused. The existing exemption for the general policy link to `fixtures/README.md` is
unchanged. Tests drive strings through the compiled pattern in both directions, so the narrowing
cannot widen until a named set passes.

Keeping the bare shape as a warning sign was declined: it names nothing a generating pass does not
already know, the set-name limb of the same check refuses any committed set name on the line, and
the remedy would be rewording correct prose to dodge the checker, which teaches authors to evade
the rule rather than obey it. Exempting only the README's Layout line was declined because it
leaves the over-match for every later file and makes the exemption a hand-kept list.

## Ruling 2 — `README.md` and `CONTEXT.md` join; `CLAUDE.md` takes its own ticket

Both files join because authors open and edit them constantly, which makes them the widest path by
which a fixture quotation enters the tree; neither is read by a generating pass, and the module
says so beside them. Both are clean once Ruling 1 lands.

`CLAUDE.md` is not added here. Its finding is an existing gap the rule's own ground already reaches,
not a part of the README change, and the likely remedy is to run fixture-generating passes as a
subagent that does not load `CLAUDE.md`, rather than rewording 38 lines whose job is to describe
the checkers. That is the mention-versus-use problem
[#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246) ruled the two root
documents apart over. It is filed as its own ticket under `grilling`.

Decision records and `docs/agents/` are declared outside the check, with the reason written in the
module: decision records are history no generating pass loads, and the tracker documents are read
only for tracker work. Because decision records stay outside, the run-number and scanner-row false
alarms the tracker recorded against them are not priced here; a proposal to check them answers
those first.

## Ruling 3 — the checked population is derived by directory, and root documents are named

`REQUIRED_INSTRUCTIONS` becomes every Markdown file under `skills/`, every Markdown file under
`reference/` (absorbing the two named sheets and the threshold directory), and `AGENTS.md`,
`README.md` and `CONTEXT.md` named one by one. One sentence in the module states why the root
documents are a named list rather than a glob: each has been ruled on individually, and `CLAUDE.md`
is out pending its own ticket. The population test asserts that a file in a `reference/`
subdirectory is a member, so the walk is shown live.

A hand list with a boundary sentence was declined because every new reference sheet would start
unguarded, the gap the tracker kept finding as sheets arrived. Deriving the set by following links
out of the skills was declined: it needs a link parser that misses a file a skill reaches by
command, which is a matcher reading part of the tree as though it were the whole.

## Ruling 4 — **Required instruction** is defined in `CONTEXT.md`

The term names a file a fixture-generating pass reads as part of its prompt, which is the ground
`fixtures/README.md` gives for the blindness rule. It is defined because Ruling 2 deliberately makes
the checked population wider than the required instructions, and because the `CLAUDE.md` finding
rests on the distinction.

## What this does not establish

A clean run still means only that no checked file names a concrete fixture identity by pattern. It
does not recognize a paraphrased fixture input or a disguised answer, which `fixtures/README.md`
leaves to review, and adding files does not change what the check can see.
