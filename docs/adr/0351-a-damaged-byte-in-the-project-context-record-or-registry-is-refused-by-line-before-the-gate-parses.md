# A damaged byte in the project-context record or registry is refused by line before the gate parses

**Measured at:** 9cf60f4168ef78666c9505d17def3e2d3df6792f

[#1563](https://github.com/mshamblin5150-code/clinical-skills/issues/1563) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 11) on 2026-10-04. It said a shell
heredoc turned backslash sequences in Windows paths into control characters in the run's
`project-context.md`, that the project-context gate accepted the damaged declaration, and that the
run noticed only when a later read could not open those paths. It proposed refusing a control
character in an `OPENED` or registry path line, and left open whether that refusal belongs in
`tools/project_context.py` or in the shared heredoc write guard. Grilled 2026-10-12 against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The gate did not accept the damaged record.** The run's own transcript shows the damage came from a
Python script fed through a heredoc that wrote Windows paths in ordinary rather than raw strings, so
`\a`, `\0`, and `\f` became a bell, a NUL, and a form feed inside five `OPENED` lines. When the run
then ran `python tools/project_context.py <run> --write`, the command printed
`project context NOT WRITTEN - submission or record input is unreadable` and exited 2. Nothing was
written or confirmed. The run found the cause only by dumping the file with `cat -v`. The ticket's
"accepted" is the claim this record corrects.

**Every control character tried in a path is already refused, and neither refusal names the
cause.** Synthetic records driven through the public `write_record` and `main` seams gave three
outcomes:

| Damage | Exit | What the gate said |
| --- | ---: | --- |
| A bell or tab inside an `OPENED` file path | 1 | `an OPENED file could not be read`, naming the place but not the cause |
| A NUL, form feed, or vertical tab inside an `OPENED` file path | 2 | the generic `input is unreadable` |
| A bell inside the free-text `TERMS` field | 0 | nothing; the damaged value was written into the confirmed record |

`str.splitlines` breaks a line at a form feed or vertical tab, so the parser reads half a line as an
unrecognized line; a NUL makes the path itself invalid. Both escape to the command's catch-all. So the real defect is the diagnosis, and the one route that is open is a free-text
field.

**The existing heredoc guard could not have seen this write.** The heredoc wrote into the session
scratchpad, and the file entered `scratch/runs/` by `cp`. That is outside the `scratch/` and
`output/` targets `tools/heredoc_write_hook.py` reads, and a shell-command hook cannot see a copy
of bytes that were already damaged.

**The existing records carry Windows line endings and nothing else.** All nine `project-context.md`
records under the owning checkout's and its worktrees' `scratch/` roots end every line with a carriage return before the newline.
None carries a tab or any other control character, and neither does the account registry.

## Ruling 1 — the check reads the whole record before parsing and names the line

Before it parses anything, `project_context.py --write` checks every line of the run's
`project-context.md` for damage, not only path lines. On damage it names each line number and the
character, and gives the Write tool as the remedy. This replaces the generic `input is unreadable`
for this cause and covers the free-text fields.

Closing the ticket as already handled was declined because the next run would meet the same
unexplained refusal, and a control character in `TERMS` or `DETAIL` would still be confirmed.
Building it as filed, path lines only, was declined because most of that work would test a rule
that already holds while leaving the free-text gap open.

## Ruling 2 — damage is exit 1, and no other check runs

A damaged record is a finding: the file opened and decoded, and the gate established a defect in
it. The command exits 1 and reports only the damaged lines. No other check runs, because the
damage can split a line and the parser's reading of what remains cannot be trusted.

Exit 2 was declined because it would keep saying the gate could not read a file it read completely,
which is the misstatement the old message made. Running every other check beside the damage was
declined because the findings the damage itself causes, a split line read as unrecognized or a path
that cannot open, would bury the cause. A run fixing the damage may then meet an ordinary finding
it could not have seen the first time; that costs one rerun.

## Ruling 3 — the record and the account registry are checked, and nothing fingerprinted is

The check reads the two files the gate parses as text: the run's record and the account's
**Project registry** (`scratch/project-registry.md`, located by `repo_root.project_registry`). Both
are hand-written, both hold Windows paths, and a damaged registry path silently changes which places
a project owes. The files a run opened and the text a service returned are fingerprinted, not
parsed, and are left alone; an opened `.docx` is full of control characters by nature.

A damaged registry stops every coursework run until it is fixed. That is accepted, because a
registry that misstates what is owed has no safe partial reading. Checking the record alone was
declined because it would leave registry damage failing the way the record did on 2026-10-04, as an
unexplained absent or unreadable place.

## Ruling 4 — damage is any C0 control character except a line ending

A line may end in a newline or in a carriage return directly before a newline. Every other C0
control character is damage, including the tab and a carriage return anywhere else.

This set is deliberately narrower than the tracker-body row #723 added to `tools/tracker_bodies.py`,
which accepts tab, line feed, and carriage return because tracker prose can carry them. Nothing
documented in either of these files uses a tab, and `\t` is the likeliest way a heredoc damages a
Windows path, which is full of `\t` pairs such as `\temp` and `\tools`. Copying #723's set would
miss the commonest damage. Refusing every C0 character including the carriage return was declined
because it refuses all nine existing records and every record saved on this Windows machine. A
record or registry written with deliberate tabs is refused, and its remedy is spaces.

## Ruling 5 — the refusal lives in the gate, independent of the heredoc guard

The open placement decision is settled for this ticket: the check belongs in `project_context.py`.
It reads file contents, so it catches damage from any write route, including the one that happened.
[#1581](https://github.com/mshamblin5150-code/clinical-skills/issues/1581), which proposes a
body-backslash limb for `tools/heredoc_write_hook.py`, keeps its own open decisions and is neither a
prerequisite of this build nor settled by it.

The same weakness in the other hand-written run records that graders parse, such as a research
ledger's `claims.md` or a `heading-read.md`, is filed as its own ticket. Widening this one was
declined because it would turn one gate's fix into a survey of every grader that parses an
agent-written file, with that population still to be derived. Holding this ticket for #1581 was
declined because that ruling concerns a mechanism that cannot cover this write route.

## Build checklist

- `tools/project_context.py`: before `read_record` and `read_registry` run on the `--write` path,
  read each file's text and report every damaged line by number and character under ruling 4's set.
  On any damage, exit 1 with only those lines and the Write-tool remedy; run no other check. Name
  the file each line came from, since the registry is outside the run.
- The character set and its divergence from #723's row are stated beside the check, with the reason.
- `DECLARED_LIMITS` gains the limits below that a clean check does not reach.
- Tests that drive the public `--write` command with a planted tab, bell, NUL, form feed, vertical
  tab, and bare carriage return in a path line, in a free-text field, and in the registry. Each
  expects exit 1 naming the line. A control record with Windows line endings and none of those
  characters exits 0.

## What this record does not reach

- **Damage that produces printable characters.** A heredoc can also eat a backslash outright, so
  `C:\Users` becomes `C:Users`. That is ordinary text; it fails later only if the path cannot open.
- **The go-ahead and completion re-reads.** They read a record `--write` has already checked and
  canonicalized. A hand edit after the last `--write` reaches them unchecked.
- **The other hand-written run records.** Ruling 5's new ticket owns them.
- **The heredoc itself.** #1581 owns whether a shell-command hook refuses or warns on the write.
