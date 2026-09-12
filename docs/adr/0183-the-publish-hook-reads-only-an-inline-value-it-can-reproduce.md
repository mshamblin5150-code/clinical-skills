# The publish hook reads only an inline value it can reproduce

[#916](https://github.com/mshamblin5150-code/clinical-skills/issues/916) was filed on 2026-09-06 by
[ADR 0136](0136-each-escape-collapse-shape-gets-its-own-refusing-row-and-a-record-may-fail-more-than-one.md)
ruling 7, which priced a cause-side route check at the pre-publish hook and ruled it **filed rather
than built**. Eight sweep comments followed. The ticket asked four things: whether such a check is
worth its cost at all, what it refuses, whether titles are in scope, and what it costs the
direct-writer path. The fourth was answered by
[ADR 0177](0177-both-publish-routes-grade-a-body-through-one-grader-and-a-lost-body-refuses.md)
ruling 3 before this grilling opened.

Grilled 2026-09-11 to an empty frontier. **Seven rulings, by the clinician, on that date.** Nothing
is built here; this is the record the build reads. The build is
[#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123); #916 closes on ruling 5
and carries no build of its own.

## Measured before ruling, at `6db417e` and re-derived at `45a0a5b` and `8e0b754`

Freshness gate `FRESH` at `6db417e` before any reading. **It reported `STALE` twice and every
comparison below was re-driven on each new base rather than carried over.** The first merge, to
`45a0a5b`, touched `docs/adr/` and `tools/day_file_text.py`; the second, to `8e0b754`, touched
`docs/adr/` alone. Neither touched `tools/tracker_publish_hook.py`, `tools/tracker_bodies.py`,
`tools/shell_reader.py` or `.claude/settings.json`, which is where every comparison below reads. Gate
`FRESH` at `8e0b754` immediately before publication.

Two kinds of figure appear here and they are not equally durable.

**The hook-versus-shell comparisons are re-derivable from committed code.** They ask one question —
does `tracker_publish_hook.extract()` return the bytes a real shell puts in `argv` — by running both
over the same command text. A reader re-derives any row by calling `extract()` on a command and
`bash -c "printf '%s' <the same value>"` beside it. Nothing here was reasoned from reading the
parser.

**The population figures come from this account's Claude Code transcripts, which nothing committed
re-derives.** 173 project directories, 376 JSONL files, 262,887 lines, 2026-08-09 to 2026-09-11.
They are floors over a population that moves while it is read — one transcript was being appended
during the measurement, and the totals drifted across passes. **They are stated here once and are
deliberately not restated in `tools/`, in `CLAUDE.md` or on the tracker**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

### The divergence, by form

`extract()` strips quotes without reproducing what the quotes mean. Driven at `45a0a5b`:

| an inline value written as | the hook reads | a real shell delivers | |
| --- | --- | --- | --- |
| `'plain text'` | `plain text` | `plain text` | agree |
| `"plain text"` | `plain text` | `plain text` | agree |
| `'it'\''s'` | `it's` | `it's` | agree |
| `"a\$b"` | `a\$b` | `a$b` | **diverges** |
| <code>"a\\`b"</code> | <code>a\\`b</code> | <code>a\`b</code> | **diverges** |
| `'a'"$T"'c'` | `a$Tc` | `asetc` | **diverges** |
| `"$(cat f.md)"` | `$(cat f.md)` | the file's contents | **diverges** |
| `"$(cat <<'EOF' … EOF)"` | the operator text, heredoc body deleted | the heredoc body | **diverges** |

The last two are the ones with a population. A substitution **behind a variable** is already refused
as `command-substitution`; a substitution written **directly as the flag value** is not refused at
all, and the hook grades the operator text instead of the body.

### What that costs in both directions

**A silent pass.** The same body text is refused through `--body-file` and allowed through
`--body "$(cat bad.md)"`, which reports `scanned body: 0 findings`:

| body text | via `--body-file <abs path>` | via `--body "$(cat bad.md)"` |
| --- | --- | --- |
| the two characters `@-` | deny `body:lost-at-dash` | **allowed** |
| a C0 control character | deny `body:c0-control-character` | **allowed** |
| a literal newline escape | deny `body:literal-newline-escape` | **allowed** |

Three refusing rows bypassed, including the row #130 exists for and the row #777 had just built. The
two reports are otherwise byte-identical: both say `body read from inline` and `scanned body: 0
findings`, so a reader cannot tell a grade of the body from a grade of fourteen characters of command
line.

**A false refusal.** Because the hook keeps the backslash that bash removes, a code span stops being
a code span in the text that gets graded:

| | text | verdict |
| --- | --- | --- |
| the published body | <code>the row matches \`\n\` in prose</code> | CLEAN, the escape is in a code span |
| what the hook grades | <code>the row matches \\\`\n\\\` in prose</code> | **refused** `literal-newline-escape` |

That is the exact false-positive class ADR 0136 ruling 4 says the code-span exclusion protects. The
exclusion is defeated because the backslashes survive into the graded text.

### The population

Inline **body** publications, by how the value was written — 364 of 4,155 body-carrying publications:

| class | all time | September |
| --- | ---: | ---: |
| `$(cat <<'DELIM' … DELIM)`, inner delimiter quoted | 192 | 0 |
| `$(cat <<DELIM … DELIM)`, inner delimiter unquoted | 0 | 0 |
| other command substitution | 3 | 1 |
| typed literal, double-quoted | 127 | 3 |
| typed literal, single-quoted | 5 | 0 |
| typed literal, unquoted | 0 | 0 |
| concatenated segments | 24 | 3 |
| the `@-` form | 13 | 0 |

Inline **titles** — 960 on title-bearing surfaces, with 3,611 invocations supplying no title:

| class | all time | September |
| --- | ---: | ---: |
| wholly single-quoted | 18 | 11 |
| wholly double-quoted | 942 | 346 |
| unquoted, concatenated, or a whole-value substitution | 0 | 0 |

No title spans more than one line. Of the 942 double-quoted titles, **3** carry a live parameter
expansion and **none** carries a live command substitution; 5 carry an escaped backtick and 13 a
backslash sequence, which is the de-escaping divergence above. `gh issue close --comment` supplies 33
bodies, **none** wholly single-quoted.

**The instrument found two defects in itself and the correction ran in the unsafe direction both
times.** Its lexer opened a single-quote context on an apostrophe inside a double-quoted string, and
it matched a flag name inside a quoted argument. Repairing them moved wholly-single-quoted bodies
from 22 to **5** and mixed titles from 194 to **0** — so the first pass **over-reported the safe
class**, which is the direction that would have made this ruling look cheaper than it is. The figures
above are the corrected ones.

**Named blind spots, each sized.** 45 publish uses came through the `PowerShell` tool, which the
`PreToolUse` matcher does not reach; 41 through argv-list `"gh", "issue", "comment"` shapes carrying
no `gh` token; and 235 blocks ran `implementation_map.py`, whose `gh` call appears in no command
string. None is in the 364 or the 960. A heredoc delimiter assembled from a variable is not
recognized, and a matcher that cannot recognize a form cannot count it as unread.

## Ruling 1 — an inline value is readable only if no segment of it is exposed to expansion

The hook may grade an inline value only where it can reproduce what the shell will deliver. That is a
property of **quoting**, not of the characters the value happens to contain: nothing is interpreted
inside single quotes, which is a fact about the shell rather than a catalog, so a construct nobody has
seen yet cannot arrive past it. Every other inline value is an **unreadable body** and is refused
under
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
ruling 1.

**Per segment, not per argument, and the argument form is why.** A title carrying an apostrophe is
ordinary English and cannot be written as one single-quoted string; its only spelling splices an
escaped quote, `'the run'\''s own record'`, which **agrees with the shell exactly**. A rule reading
*wholly single-quoted* refuses a value that has no compliant form at all, which is not a gate but a
wall. So the safe class is *no segment exposed to expansion*: an escaped-quote splice passes, and
`'a'"$T"'c'` is refused because its one double-quoted splice is exactly the live expansion the rule
exists to catch — driven, hook `a$Tc` against shell `asetc`.

**The alternative was a construct-keyed predicate** refusing only a live expansion or a de-escaping
sequence. It is more precise and it is refused, because it asks the hook to decide escaped-from-live
correctly — the precise capability measured failing twice above — and **its miss is a silent pass**,
which is this defect rebuilt one layer in. The quoting rule's miss is a false refusal whose remedy is
one pair of quotes.

## Ruling 2 — the rule holds over titles as well as bodies, at its measured price

A title is a publish surface on ADR 0083 ruling 2, it is always argument-supplied because `gh issue`
and `gh pr` have no title-file flag, and the divergence on it is identical and driveable. The
precedents for keeping titles out of a row do not transfer: ADR 0136 ruling 4 excluded
`literal-newline-escape` because a title can never carry a real line break, and ADR 0177 ruling 5
excluded the lost-body rows because no title-file route exists through which the measured loss
occurred. Neither ground is present here — this is not a text predicate and it does not degrade on a
title.

**The price is named rather than discovered: 942 of 960 titles are refused, 98.1%, and 346 of 357 in
September.** Against a divergence population of roughly 5 to 13. That is the worst ratio in this
record and it was ruled anyway, on two grounds. It is a **one-time change of habit** rather than a
recurring cost — a title is written in single quotes from now on, which is what the body rule already
demands, so the two surfaces stop having different spellings. And the alternative for titles alone was
the construct-keyed predicate ruling 1 refuses, which fails toward publishing; a mangled title is a
smaller harm than a mangled body, but it is not a harm worth buying a silent pass for.

Under ruling 1's per-segment form every title has a compliant spelling, so the 98% is a cost and not
a dead end.

## Ruling 3 — the refusal is the whole verdict, and text predicates do not run on a refused value

Where a value is refused on quoting, nothing grades the string the hook happens to hold. The
measured case is the 13 `--body @-` calls: their text is also a `lost-at-dash` finding, and reporting
it beside the refusal looks like more information.

It is not. On a double-quoted body the hook un-spans code spans, so a text finding reported beside a
quoting refusal is a finding **about a string the tracker will never hold**, and some fraction of
those findings are false — the table above is one. Printing them teaches an author to act on a
diagnosis of text that does not exist, which is the same error as the silent pass wearing a helpful
face. The author requotes and then receives `lost-at-dash` with its real remedy: a correct diagnosis
one round later instead of a possibly-false one now. The remedy text carries that reason, so the
delay reads as deliberate.

## Ruling 4 — the hook's declared limit on expansion is false and is repaired rather than appended to

`tracker_publish_hook.NOT_REACHED` carries *"anything a subshell computes … Each is refused rather
than guessed at, so the floor does not become a silent pass."* A substitution written directly as a
flag value **is** guessed at, and the floor **is** a silent pass — 195 measured calls. The row is
true of the case it was written about, a substitution behind a variable, and false as written.

A false declared limit is its own defect and the worse half of this one: the silent pass is a gap, and
the row is a **claim that the gap does not exist**. It is repaired in place to say what it covers, not
appended to, because a limit is read by whoever is deciding whether to look further and a correction
below it is not a correction for anyone who acts on it — [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436)'s
ruling, arriving on a tuple instead of on a ticket body.

## Ruling 5 — #916's cause-side route check is refused, and the refusal is declared rather than silent

Once ruling 1 lands, the only inline form still allowed is one the hook reproduces exactly, and #916's
proposed form rule — refuse a multi-line inline body, require `--body-file` — has no population left
worth refusing. Its residue is a **partial** literal-newline collapse, an escape present with a real
line break surviving, which `literal-newline-escape`'s second clause excludes by design and which
measures zero.

It is unreachable from both sides and each side already has a ruling. **From the text side**, ADR 0136
ruling 4 requires both clauses *"and not as belt and braces: each guards a different false-positive
class"*; dropping the line-break clause fires on any multi-line body that mentions the escape in
prose, which includes #916's own body and ADR 0136's. **From the form side**, `literal-at-path` is the
precedent #916 was kept open for — a documented trap with zero instances earning a row — and it does
not transfer: that row earned its place because its predicate *cannot* fire on correct prose, whereas
a multi-line rule fires on every remaining single-quoted inline body measured. ADR 0136 ruling 1 drew
exactly that line when it required a zero to have a structural cause rather than a dated one, and
honoring it closes this ticket rather than building it.

**So one tuple row is added, and that row is the whole of #916's output.** `tracker_bodies.NOT_REACHED`
already declares why the *row* does not reach a partial collapse. Nothing anywhere declares that **no
route rule covers it either**, and that silence is what #916 was filed into. Closing without the row
leaves the next session re-deriving the ticket from scratch.

## Ruling 6 — two tickets and one ADR, and #916 closes on this record

Ruling 5's row is only *true* once ruling 1 lands — before the refusal exists the cause side is not
merely uncovered, it is open in a larger way — so the row and the refusal are one packet by sequence
rather than two packets in a collision group. [#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123) carries rulings 1 through 5. #916 closes with no
commit binding it.

**That shape has a recorded failure mode and this record is written against it.** ADR 0136 ruling 7
said *filed* and named no number, so a reader of the ratified record could not reach #916 — the sweep
of 2026-09-06 found exactly that. Both ticket numbers are therefore named in this record's own
rulings, and [#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123)'s body cites #916, or ruling 6 rebuilds the defect it is guarding.

## Ruling 7 — two surfaces are handed off rather than covered, and both are named

**The `PowerShell` tool is a second command surface the hook never sees.** The `PreToolUse` matcher is
`Bash`, and 45 publish uses came through PowerShell. That is not a form the hook misreads, it is a
tool it is not registered for, and its fix carries a question this grilling did not ask — whether
`tracker_publish_hook` must learn PowerShell quoting, whose rules differ. It is
[#1124](https://github.com/mshamblin5150-code/clinical-skills/issues/1124) and not part of [#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123).

**[#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107) is inherited unchanged.**
A quoting-keyed refusal runs only where `route` is recognized, and a publication inside `bash <<'SH'`
or `sh -c "…"` classifies as `None` and returns an empty response before any rule runs. So ruling 1
prevents nothing nested, exactly as the body grader prevents nothing nested today.

**And ADR 0099 ruling 4's declaration stands.** This hook is one of two publishers. Nothing here is
prevention for the harness that published every measured damaged record.

## Alternatives refused

- **Build #916's form rule as filed** — refuse a multi-line inline body. Refused under ruling 5: it
  fires on every remaining inline body measured, to prevent zero.
- **Refuse any inline body, single-line included.** Refused: it contradicts
  `docs/agents/issue-tracker.md`'s own *"Single-line bodies may use `--body \"...\"`"* and #916's
  prohibition on refusing a correct short publication. Ruling 1 refuses on reproducibility instead, so
  a single-quoted one-liner still passes.
- **Refuse an inline body carrying the two characters of the escape.** Refused: `literal-newline-escape`
  already grades that text on both routes, so the rule would be a second symptom row wearing a route
  check's name, which #916's own *what must not come out of this* forbids.
- **A construct-keyed predicate.** Refused under ruling 1, for bodies and again under ruling 2 for
  titles.
- **Repair the `` \` `` and `\$` de-escaping and keep reading double-quoted values.** Refused as
  unnecessary: under ruling 1 a double-quoted value never reaches a text predicate, so the path is
  unreachable and a second mechanism that cannot fail is a line that costs a test.
- **Apply the quoting rule to `--body-file` path arguments.** Refused: a path's fidelity is
  [ADR 0137](0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md)'s and
  [ADR 0179](0179-a-body-file-absent-when-the-hook-ran-is-one-condition-and-its-remedy-names-both-causes.md)'s
  subject, the body text comes from the file rather than from the argument, and the rule's subject is
  the fidelity of text the hook will grade.
- **Report text findings beside a quoting refusal.** Refused under ruling 3.
- **Append the expansion limit's correction below it.** Refused under ruling 4.
- **Correct ADR 0096 in place rather than write this record.** Refused: its ruling 1 is not wrong, it
  has a door it never measured, and a correction appended there leaves the new refusal discoverable
  only from a record whose headline is about something else.
- **Fold the PowerShell surface into [#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123).** Refused under ruling 7.
- **Auto-repair, and reporting the mechanism upstream.** Both were refused by ADR 0136 ruling 7 and
  are not reopened.

## What none of this reaches

- **A nested publication**, per ruling 7. #1107 owns it.
- **The argv-list and `implementation_map` routes**, which supply no command string the hook reads.
- **The `PowerShell` tool**, which is a separate cause and is
  [#1124](https://github.com/mshamblin5150-code/clinical-skills/issues/1124).

  **Corrected in place 2026-09-12, after merging and before anything was built against it.** These
  were one bullet reading *"The `PowerShell` tool and the argv-list and `implementation_map` routes,
  which supply no command string the hook reads."* **That reason is true of two of the three and
  false of the first**: the `PowerShell` tool's `tool_input` is field-identical to `Bash`'s and
  carries a `command` string the hook could read — it is a tool the matcher does not name, which is
  what ruling 7 says eleven lines above. Folding three routes under one reason hid that they have two
  causes and therefore two remedies. Found by #1124's grilling, 2026-09-12;
  [ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
  carries the split. ADR 0038's correction header is the precedent.
- **A partial literal-newline collapse**, per ruling 5 — declared, not graded, from either side.
- **Backtick loss with no other symptom**, which ADR 0136 already leaves ungraded with a dated
  residue. Ruling 1 prevents the *form* that produces it from this publisher and grades no published
  instance.
- **Whether a reproducible inline body says something true.** Ruling 1 establishes that the text the
  hook graded is the text the tracker will hold. It establishes nothing about that text beyond the rows
  that ran on it.
- **A value the shell would transform in a way `extract()` happens to reproduce.** The comparison
  above is a floor over the forms driven, not a proof that the two agree everywhere they are permitted
  to.
