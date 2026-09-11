# A body file absent when the hook ran is one condition and its remedy names both causes

Ruled by the clinician on 2026-09-11, in the grilling of
[#897](https://github.com/mshamblin5150-code/clinical-skills/issues/897). Freshness gate `FRESH`
before reading; `main` moved once during the session, from `d096104` to `b9565ae`, the branch was
brought forward, and every row below was driven again on the new base. Nothing is built here; this
is the record the build reads.

**The subject.** `tools/tracker_publish_hook.py` refuses a body file it cannot open under one of two
kinds. `written-before-publish` is chosen by `_written_before_publish`, a regular expression for a
`>` redirect to the typed path in the text before the first `gh ` substring; every other absent file
is `missing-file`, whose remedy is *create the file first*. The hook is `PreToolUse`, so it runs
before any part of the command. A body written by `python`, `cp` or `tee` earlier in the same
command is therefore refused with advice its author had already followed.

## Measured before ruling, at `b9565ae`

Each command below was driven through `tracker_publish_hook.extract()` from a script file, with `P`
an absolute forward-slash path in a fresh temporary directory and the file never created:

| command shape | kind |
| --- | --- |
| `echo hi > P && gh … --body-file P` | `written-before-publish` |
| `echo hi >> P && gh … --body-file P` | `written-before-publish` |
| `cat > P <<EOF` … then `gh … --body-file P` | `written-before-publish` |
| `python tools/mk.py P && gh … --body-file P` | `missing-file` |
| `cp a.md P && gh … --body-file P` | `missing-file` |
| `echo hi \| tee P && gh … --body-file P` | `missing-file` |
| `python - <<PY` writing the literal `P`, then `gh … --body-file P` | `missing-file` |
| `python - <<PY` building `P` with `os.path.join`, then `gh … --body-file P` | `missing-file` |
| `gh … --body-file P` alone | `missing-file` |
| `python tools/tracker_freshness.py && gh … --body-file P` | `missing-file` |
| `cd "<folder>" && python mk.py body.md && gh … --body-file body.md` | `missing-file` |
| `python mk.py body.md && gh … --body-file body.md` | `unrooted-path` |
| `echo hi > P.bak && gh … --body-file P` | **`written-before-publish`** |
| `echo "high " > P.x && cp P.x P && gh … --body-file P` | **`missing-file`** |

The last two rows are the recognizer mislabeling in both directions. The redirect pattern has no end
anchor, so a write to `P.bak` reads as a write to `P`; and `command.find("gh ")` stops inside the
word `high`, so the prefix it searches ends before the redirect it was looking for.

**What the refusals have actually been.** Session transcripts on this machine, 2,162 files, read for
the hook's refusal text. Two instruments, counted against live working material outside this
repository, so every figure is a dated floor on a matcher and nothing committed re-derives one; they
are stated here once, on [ADR 0137](0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md)
ruling 5's terms.

- **The parent's**, joining each `hook_additional_context` attachment carrying a refusal to its Bash
  command by tool-use id: 41 refused calls, of which 30 `missing-file`, 8 `invalid-command` and 3
  `written-before-publish`. Of the 30 `missing-file` refusals, 9 name the typed path in an earlier
  stage of the same command, 18 do not, 3 escaped its publish-token matcher, and 0 begin with `gh`.
- **A subagent's**, also counting deny reasons recorded without an attachment: 43 refusals, of which
  31 `missing-file`, 8 `invalid-command`, 3 `written-before-publish` and 1 `external-variable`; of
  the 31, 10 name the path earlier, 21 do not, 0 begin with `gh`.

*Had recognizing the path's text been the route to the right remedy for most absent files, the first
of those bins would hold most of the `missing-file` refusals; it holds 9 of 30 on one instrument and
10 of 31 on the other.* The zero is not evidence against the retry case #897's 2026-09-05 comment
recorded: a retry that keeps its `cd` prefix lands in the second bin, which neither instrument
subdivides.

## Ruling 1 — a body file absent when the hook ran is one condition, keyed `missing-file`

For every creation route above, the file genuinely does not exist when the hook looks, because the
hook runs before the command does. **Whether an earlier stage of the same command will write it
cannot be decided from the text.** A redirect or a `cp` names the path; a program can build it; and a
retry after a refused command carries no trace at all of the write that refusal prevented, because
the evidence is in an earlier tool call. So the two kinds merge. `written-before-publish` leaves
`UNREADABLE_REMEDIES`, and `_written_before_publish` is deleted with both of its call sites. The key
stays `missing-file` because it remains literally true.

**This is consistent with ADR 0137 ruling 4 rather than a departure from it.** That ruling made
`unrooted-path` a kind of its own, on the precedent of `external-variable`, because each names a
condition the hook decides from the command it holds. A kind is for a distinguishable condition, and
*written by this command* is not one the hook can distinguish.

## Ruling 2 — the remedy says why the file is absent and names both repairs

The `missing-file` entry in `UNREADABLE_REMEDIES` reads, in full:

```text
no file was at this path when the hook ran, which is before any part of this command runs, and a refused command runs none of its stages; if this command writes the file, write it in a separate command first, otherwise create it, then run `python tools/tracker_publish_hook.py --text <path>` before retrying
```

The shared line ADR 0137 ruling 3 added beneath every refusal, naming the folder resolved against and
the reconstructed path, is unchanged, so the author sees which path was absent.

**The clause about a refused command is load-bearing.** After `printf … > P && gh …` is refused, the
natural retry is `gh … P`, and the file is absent *because the hook stopped the write*. Nothing in
the retried command can show that, so the only place the fact can reach the author is the remedy
printed on every absent file.

## Ruling 3 — an unrooted path keeps precedence over absence

A partial path with no folder readable from the command is `unrooted-path`, whatever else the command
writes. The hook never looked for a file, because it had no folder to look in, so *no file was at
this path* would claim something it did not check. The build note in ADR 0137 that ordered
resolution after `_written_before_publish` is corrected in place in that record. The test
`test_the_typed_write_is_classified_before_path_resolution` changes to expect `unrooted-path` and is
renamed for what it then asserts.

## Ruling 4 — the refusal is unchanged and nothing new is declared

[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
rulings 1 and 5 stand: every command in the table is still refused as `NOT SCANNED`, and only the
advice printed changes. No row is added to `NOT_REACHED`. The refusal cannot tell a mistyped path
from a same-command write, but the remedy names both on every refusal, so that limit is on the page
rather than waiting to be discovered. `CONTEXT.md` is unchanged: its **Unreadable body** entry
already lists *written by an earlier stage of the same command* among the causes.

## Considered options

- **Enumerate creation routes** — add `cp`, `tee`, `mv`, `python … P` and program-fed heredocs to the
  redirect pattern. Refused. The set is open, which is the partial-instrument shape
  [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) names; a built path is
  unreachable by construction; and the retry case is outside any reading of the command.
- **Recognize the typed path's text anywhere in an earlier stage.** Refused. On the census it reaches
  9 of 30 absent-file refusals at most; it mislabels a stage that only tests or reads the path; and it
  shares the enumeration's blindness to a built path and to a retry.
- **One condition with a remedy naming both causes.** Chosen, above.

## What this does not reach

**A publication inside a nested shell.** The 2026-09-10 comments on #897 record a read-only Python
heredoc refused as `invalid-command`, and this grilling measured the neighboring defect: a
publication inside `bash <<SH` or `sh -c "…"` passes unscanned. Both concern which commands are
publications, not what an absent file's refusal says, and both are
[#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107), filed from this grilling.

**Whether the file `gh` reads is the file the hook read.** A file rewritten between the two is
already a `NOT_REACHED` row and is unchanged.

**What the `--text` pre-grade in the remedy establishes.** Ruling 2 keeps the pointer to
`python tools/tracker_publish_hook.py --text <path>` that most remedies in `UNREADABLE_REMEDIES`
carry, and the manual mode runs no AAR quotation gate. So a body under an AAR run's
`aar/publications/` directory can pre-grade clean and still be refused when it is published. That gap
is [#1026](https://github.com/mshamblin5150-code/clinical-skills/issues/1026)'s, and this record
widens its reach by exactly the refusals that used to print the `written-before-publish` remedy,
which did not name `--text`.

**Skill prose that says to write a body and then publish it.** `skills/aar/SKILL.md` directs a run to
write every AAR-sourced ticket body under its publication directory first and then publish it with
`gh --body-file`, without saying the two must be separate commands. This record leaves that text as
it is; ruling 2's remedy is what reaches an author who does both in one command.

## What the build must not trip over

- **Deleting the helper removes the early branch in `_read_file_field`**, so `_resolve_file_source`
  runs first: a partial path with no readable `cd` returns `unrooted-path` before any read, and a
  resolvable path that does not open returns `missing-file`.
- **`test_each_ruled_residue_has_its_own_class` lists `written-before-publish` among its commands**;
  that entry leaves with the kind, and the remaining four still map to themselves.
- **New coverage is every row of the measured table** asserting `missing-file`, or `unrooted-path` for
  the row without a `cd`, driven through `handle` so the printed remedy text of ruling 2 is asserted
  and not only the kind. The `P.bak` and `high` rows pin that neither mislabel survives, and a bare
  `gh … --body-file P` row stands for the retry after a refusal.
- **`docs/agents/issue-tracker.md` names neither kind**, so no manual edit is owed.
