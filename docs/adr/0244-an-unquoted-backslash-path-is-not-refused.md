# An unquoted backslash path is not refused, because the hook grades the file the shell opens

[#1150](https://github.com/mshamblin5150-code/clinical-skills/issues/1150) was filed on 2026-09-12
from [ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)'s
*What none of this reaches*, which listed *"a latent wrong read of a bare backslash path whose mangled
spelling names a real file"*. Two sweep comments on the same day falsified its headline, and its
title was narrowed to a mixed-separator path that respells to a different real file.

Grilled 2026-09-15 to an empty frontier. **Three rulings, by the clinician, on that date.** The build
is #1150 itself, respecified to ruling 2.

## Measured before ruling, at `39d1bece`

Freshness gate `FRESH` at `39d1bece` before any reading.

**The reader and the shell agree on an unquoted backslash.** An unquoted `<temp>/m1150/a\xbody.md`
comes back as `<temp>/m1150/axbody.md` from both `shlex.split` and `bash -c "printf '%s\n' …"`. The
two sweep comments on #1150 found the same for a bare `C:\tmp\x.md`. The one shell that keeps the
backslash is PowerShell, and ADR 0188 ruling 1 refuses a publication written in it unread.

**The hook grades the file the shell opens, driven through `tracker_publish_hook.py --command-file`
rather than read off the parser.** The respelled file held the two characters `@-`; the file the
author meant held plain text:

| value typed | file the hook graded | verdict |
| --- | --- | --- |
| unquoted `…/m1150/a\xbody.md` | `…/m1150/axbody.md`, the file Bash opens | deny `body:lost-at-dash` |
| double-quoted, same characters | `…/m1150/a/xbody.md` | 0 findings |

**The instrument discriminates.** Had the hook read the file the author meant while the shell opened
the respelled one, the unquoted row would have reported 0 findings, as the quoted row does. It refused
on the respelled file's text.

**The population, reported for context and grounding no ruling.** A subagent counted this account's
Claude Code transcripts: 2,332 files, 0 unreadable, 2026-08 through 2026-09, read while still being
appended, so every figure is a dated floor. Of 4,052 file-naming flag values on `Bash` `gh`
publications, 252 were single-quoted, 1,277 double-quoted, 1,394 unquoted and 1,129 a variable or
another form. **6** unquoted values carry a backslash, 1 of them mixed with `/`, and **0** of the 6
name an existing file once the backslash is removed; that zero is weak for relative paths, which were
resolved against a different folder than the originating session's. These figures were not
re-derived, nothing committed re-derives them, and they are stated here once.

## Ruling 1 — an unquoted backslash in a file-naming value is not refused

[ADR 0183](0183-the-publish-hook-reads-only-an-inline-value-it-can-reproduce.md) ruling 1 refuses an
inline value the hook cannot reproduce, because there the text graded differs from the text
delivered and the miss is a silent pass. **No such miss exists here.** The respelled path opens a
different file, but the shell performs that respelling with or without a hook, and the hook grades
the file the shell will open. The published text is the graded text. A path that names the wrong
file is an authorship error, not a fidelity defect.

**A refusal was priced and declined.** Refusing any unquoted value carrying a backslash is cheap and
its remedy is one pair of quotes, exactly as under ADR 0183. What it would buy is a guard against a
typo that happens to name a real file, and the measured instances of that are zero. ADR 0183's
refused alternatives already decline applying the quoting rule to `--body-file` paths and place a
path's fidelity under
[ADR 0137](0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md) and
[ADR 0179](0179-a-body-file-absent-when-the-hook-ran-is-one-condition-and-its-remedy-names-both-causes.md);
this record adds that the fidelity question has no divergence to answer on the modeled path.

## Ruling 2 — the limit is declared in the hook rather than left to this record

`tracker_publish_hook.NOT_REACHED` gains one row, titled *which file an author meant is not
established*, stating that the hook reads the file the shell will open, that on the modeled path an
unquoted backslash is removed by the shell and by this reader alike, and that a path spelled with one
publishes whatever file that spelling opens, which need not be the file the author intended.

ADR 0183 ruling 5 is the precedent: it closed #916 with one tuple row and no other build, because
closing without the row leaves the next session re-deriving the ticket. #1150 was itself filed from a
record's list of what it does not reach; removing that entry with nothing in the code standing in its
place would make the limit silent again.

## Ruling 3 — ADR 0188's carried claim is corrected in place, and its measurement is left standing

The entry in ADR 0188's *What none of this reaches* is a carried claim and is corrected where it
stands, with a dated line beneath it, on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
and [ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md) ruling 3.
It is false once ADR 0188 ruling 1 lands: PowerShell never reaches the reader, and on the modeled
path the reader and the shell agree.

**The paragraph in ADR 0188's measurement reading *"And there are no wrong reads, for a reason that
is luck rather than a property of the reader"* is not corrected.** It describes the PowerShell
population as read with `Bash` rules against what PowerShell delivers, which keeps the backslash, so
it was true when written. It is a dated reading, and ADR 0191 ruling 2 supersedes a reading rather
than correcting it. The grilling first proposed correcting both; re-reading the paragraph's table
header before writing found the second was a reading of the other shell.

## Alternatives refused

- **Refuse an unquoted file-naming value carrying a backslash.** Refused under ruling 1.
- **Key a rule on the divergence between `shlex`'s answer and the raw source span.** Refused: on the
  modeled path there is no divergence for it to detect, so it would be a second reader that cannot
  fire.
- **Close #1150 with no declared limit.** Refused under ruling 2.
- **Correct ADR 0188's measurement paragraph as well.** Refused under ruling 3.

## What none of this reaches

- **Which file an author meant**, per ruling 2. Declared, never graded.
- **A relative or partial path**, whose resolution is ADR 0137's and ADR 0179's subject.
- **A shell other than `bash`**, which ADR 0188 ruling 1 refuses unread rather than reads.
