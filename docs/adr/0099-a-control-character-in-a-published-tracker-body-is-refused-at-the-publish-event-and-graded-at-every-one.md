# A control character in a published tracker body is refused at the publish event and graded at every one

[#723](https://github.com/mshamblin5150-code/clinical-skills/issues/723), filed by the exhaustive
tracker sweep of #678's grilling on 2026-08-31 and corroborated independently by the sweeps from
#689's and #713's. Grilled 2026-09-01 and ruled by the clinician on that date at `origin/main`
`643077a`, freshness gate `FRESH`. The ticket carried four open decisions, a fifth added by #689's
sweep, and the label `grilling`. **Nothing is built here; this is the record the build reads.**

## What the grilling found that the ticket did not

Every figure below was measured against the live tracker on 2026-09-01 by harvesting every issue,
pull request and issue comment through `gh api --paginate` into `scratch/`. **The instruments are
throwaway scripts under `scratch/`, so nothing committed re-derives these figures** and each is a
dated floor. Counts only; no body text is quoted except the two forms named as evidence.

**The ticket's central claim re-derives exactly.** `tools/tracker_bodies.py` over the three cited
harvests reports `records read 33`, every row `0`, `bodies failed 0`, **exit 0**. The comment counts
in the body have drifted again — #9 is 3, #519 is 22 then 24, #689 is 4 then 6 — which is harvest
drift on a dated table and not a wrong finding.

**1. The population carrying a control character is four, not three.** Swept over **3,809 records**,
the set of bodies holding a C0 character other than tab, line feed or carriage return is:

| record | body | in a code span |
| --- | --- | --- |
| [#9 comment 5256998963](https://github.com/mshamblin5150-code/clinical-skills/issues/9#issuecomment-5256998963) | 84 backticks, 0 backslashes | yes |
| [#429 comment 5471066342](https://github.com/mshamblin5150-code/clinical-skills/issues/429#issuecomment-5471066342) | 0 backticks, 16 backslashes | no |
| [#519 comment 5471067862](https://github.com/mshamblin5150-code/clinical-skills/issues/519#issuecomment-5471067862) | 0 backticks, 22 backslashes | no |
| [#689 comment 5471077562](https://github.com/mshamblin5150-code/clinical-skills/issues/689#issuecomment-5471077562) | 0 backticks, 18 backslashes | no |

Every one is `U+0008`. **#429's is the record the ticket and both later sweeps missed**, and it is on
the same batch as two of the three the ticket names.

**2. The damage class those four belong to is fourteen records over three days, and a control
character is present in four of them.** The unit is a body whose escaping was interpreted rather than
preserved:

| shape | records | carry a C0 character |
| --- | ---: | ---: |
| every backtick became a backslash; `\b` collapsed to backspace and `\r` to carriage return (2026-08-30) | 6 | 3 |
| a literal `\n` on the page in place of a newline (2026-08-20 and 08-21); one of the five also shows the backtick loss | 5 | 0 |
| a doubled `C:\\codeing\\` path (2026-08-20, 2026-08-29); one of the two also carries `U+FFFD` | 2 | 0 |
| a regex `\b` collapsed inside a code span, backticks intact (#9) | 1 | 1 |
| **total** | **14** | **4** |

**So the row the ticket asks for reaches 4 of 14.** That is not an argument against building it; it is
the coverage the build has to declare rather than discover.

**3. The wider rule the sweeps implied fires on legitimate text, measured.** Keying on *no backticks
and at least one backslash* selects **15** of the 3,809 records, and **two of them are correct**:
[pull/368](https://github.com/mshamblin5150-code/clinical-skills/pull/368) and
[pull/631](https://github.com/mshamblin5150-code/clinical-skills/pull/631) contain real Windows paths
of the form `C:\codeing\guidelines-text\manifest.json` and nothing wrong. The ticket's own *What must
not come out of this* names firing on legitimate text as the thing to refuse, and this is the rule
that would.

**4. Decision 2's proposed character set is wrong in one direction and incomplete in the other.** The
body proposes *C0 minus tab, newline and carriage return*, and the #689 sweep argued carriage return
back in on the strength of two bare carriage returns in the #519 record. Measured: **20 records carry
a bare carriage return, and 16 of them have intact backticks and no backslash at all** — an unrelated
line-ending population. Including it turns a rule with no false alarms into one with sixteen.

In the other direction the ticket's note on the normalization trap names too few characters. It says
`str.strip()` treats `U+001C`–`U+001F` as whitespace and `str.splitlines()` breaks on `U+001E`.
Measured: **six** C0 characters are Python whitespace — `U+000B` and `U+000C` as well as
`U+001C`–`U+001F` — and **five** of them break lines. `tracker_bodies.grade` opens with
`text = (record.body or "").strip()`, so any of those six at a body's edge is gone before matching.

**5. Two published sweep claims on this ticket are false and one earlier correction was itself
incomplete.** #689's sweep reported *"Every `U+0008` sits immediately after a backslash"*; #713's
sweep corrected that to 2 of 3. Measured over the true population of four it is **3 of 4**, and #9 is
a separate cause rather than a stray — its body holds 84 intact backticks and no backslash anywhere.
Separately, #689's sweep reported the same route producing `\e` collapsed to escape in the #519
record. **That record's comments carry zero escape characters.** What is there is the literal two
characters `^[`, which is a *rendering* of escape and not the byte. The only collapses that landed
anywhere are `\b` to backspace and `\r` to carriage return.

**6. The pre-publish hook could not have caught a single one of the fourteen, and the reason is not
the date.** `tools/tracker_publish_hook.py` is registered in `.claude/settings.json`, a Claude Code
`PreToolUse` hook. This repository has **84 `codex/*` branches on the remote**, and every damaged
record measured was published from one — `codex/tickets-550-645` for the 2026-08-30 batch. A second
agent harness publishes to this tracker routinely and does not read that file. The hook was
registered at `e430e33` on 2026-08-31, after the damage; **had it existed on 2026-08-30 it would
still have graded none of it.**

**7. A third host exists that no account of this ticket names.**
[`.github/workflows/tracker.yml`](../../.github/workflows/tracker.yml) already fires on `issues`,
`issue_comment`, `pull_request_target`, `pull_request_review` and `pull_request_review_comment`, and
runs `tracker_scan.py --github-event` and `tracker_branch_scope.py --github-event` against
`$GITHUB_EVENT_PATH`. It is harness-independent by construction: it grades whatever published the
record, including Codex. `tracker_bodies` is not on it and has no `--github-event` mode.

**8. [ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
retired the cost [ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4 named.** That ruling conceded *"a refuser cannot refuse what it cannot read"* against a
measured residue of roughly one publish in five. Since #745 an unreadable publication is refused
outright, so every publication reaching the hook's graders has been read. A refusing check added
today has complete coverage of the Claude Code publish path rather than four fifths of it.

**9. #212's retained-revision claim re-derives, for the first time.** #689's sweep reported it *not
verifiable here*. GraphQL `userContentEdits` serves the full prior text of every edit to anyone with
read access — probed against an edited comment on #8, two revisions, `diff` lengths 4,554 and 4,561,
`deletedAt` null on both. **873 records on this tracker have been edited.** The `deletedAt` field
exists, so a revision can be deleted, but by the web interface rather than by any public mutation.
The claim stands as the ticket states it.

**10. ADR 0048 ruling 14 does not reach this ticket, and both of its reasons invert.** Its argument
for *nothing is repaired* is that *"editing them makes each comment disagree with the state it was
posted in"* — a reason about a **dated claim** that was true when posted. A collapsed escape was
never a state anything was posted in; it is not a claim but a rendering fault, so repairing it makes
the comment agree with what its author asserted. Its second reason, the retained revision, bites when
the original holds something that should never have been public. Here the original holds corruption
that is already public, so an edit publishes nothing that is not already served.

## Ruled 2026-09-01

**1. This ticket is a control character and not a family, and the coverage is declared rather than
widened.**

Finding 2 is the whole argument for stating it: the row reaches 4 of 14 measured damaged bodies, and
a build that does not say so ships a check that reads as covering the class it was filed over. The
other three shapes have different causes, different homes and — in the `U+FFFD` case — an unsolved
ambiguity, and they are a separate ticket with a separate measurement.

The wider rule was priced and refused on finding 3 rather than on taste. This is the repository's
standing preference on exactly this shape — **declare the coverage rather than widen the
instrument** — and it is `spelling_scan`'s refused suffix rules arriving on a tracker body.

**2. The row matches the raw body, and a control character inside a code span counts.**

`#155 - double-encoded` matches against `prose`, after `grade` strips fenced blocks and code spans, on
this repository's mention-versus-use rule: *a shape inside inline or fenced code is a mention and does
not fire*. **That rule does not transfer, because a control character cannot be mentioned.** The rule
protects a *spelling* — a backticked British form is the word being named, and the backticks are what
distinguish naming it from using it. There is no spelling of `U+0008` that is the byte itself: writing
about a backspace puts `U+0008` or `\b` or `BS` on the page, never the character. A code span holding
the raw byte is therefore always damage that landed inside backticks, which is exactly what #9 is —
a reader copying that regex out of the page gets a pattern that does not compile.

**This answers the ticket's decision 1 on measurement rather than on taste.** Matching prose catches
3 of 4 and could be a widening of `#155`; matching the body catches 4 of 4 and **must be a new row**,
because it grades a different string from every row above it.

**3. The set is C0 minus tab, line feed and carriage return, matched against `record.body` and never
against the stripped `text`.**

Three parts, each on a measurement:

- **The set.** Zero false alarms over 3,809 records, and the reason is structural rather than lucky:
  there is no correct Markdown body containing `U+0007`. `spelling_scan`'s evidence-only discipline
  does not transfer — it refuses `-ise` and `-our` because those fire on `seizure` and `figure`, and
  nothing in this set is a word. `U+0008` alone would be a rule that knows one instance while
  `\a`, `\v`, `\f` and `\e` sit on the same escape table that produced it.
- **Carriage return stays out**, on finding 4's sixteen legitimate records.
- **The unstripped body.** Six of the set are Python whitespace, so matching `text` silently drops
  them at a body's edges. This is `differential_scan`'s recorded trap, and the fix is to not normalize
  before matching.

**`U+007F` stays out and is declared**: it is not C0, no escape sequence in the collapsing table
produces it, and it is unmeasured here.

**`U+FFFD` stays out for a reason stronger than scope, and it constrains the separate ticket.**
`tracker_bodies.load_harvest` reads with `errors="replace"`, so a `U+FFFD` in the scanned string may
be **the scanner's own substitution** for an undecodable byte in the harvest file rather than damage
in the published record. The row could not tell those apart. Whoever takes the `U+FFFD` shape has to
solve that ambiguity before grading it.

**4. The predicate lives in `tools/tracker_bodies.py`, the workflow is what closes the ticket, and the
hook is what prevents.**

Three hosts, none redundant, and the division follows findings 6 and 7:

- **`tools/tracker_bodies.py` owns the row** — one predicate, one implementation, one place a test
  points at. It gains a `--github-event` mode on its two siblings' pattern, because a GitHub event
  payload is a shape its single-object `-` limb cannot read.
- **`.github/workflows/tracker.yml` gains a step calling it**, and that step is what answers this
  ticket. It is the only host that reaches every publisher. **Advisory**, on ADR 0002's standing CI
  ruling and matching the two steps beside it.
- **`tracker_publish_hook.py` gains the same check**, because it is the only limb that stops a record
  ever landing and the hook already extracts the text.

**The honest declaration ships with it: the hook covers one of two publishers, and the workflow covers
both one minute after the fact.** Nothing here is prevention for Codex, and nothing in this repository
can be — that needs a check inside a harness this repository does not control. A build that leaves
that unsaid rebuilds this ticket's own subject.

**5. The hook refuses on this row, and it clears ADR 0083 ruling 4's bar more cleanly than
branch-scope does.**

That ruling's test is no PHI, no one-for-one false block, and a remedy that is a line of text rather
than a ruling about a patient. All three hold, and two hold more strongly here:

- Branch-scope refuses on triggers measured at 348 of 353 firings correct. This row has **zero** false
  alarms over 3,809 records, structurally.
- **The remedy is one the agent applies alone** — rewrite the body without the character. This is
  precisely the distinction ADR 0083 drew when it kept the PHI half advisory: *the PHI half has no
  remedy the agent can apply alone.* This half does, which is why a third refuser in a hook whose PHI
  check advises is right rather than backwards.
- `tracker_branch_scope.NOT_REACHED` row 1 — *publication precedes the check … it is a backstop and
  cannot intercept the original write* — is what a refusing hook retires. The cost of a backstop for a
  wrong branch-state block is an editable claim; for a control character it is a revision retained
  under finding 9, because the workflow step fires **after** publication.

**The row grades the title as well as the body.** ADR 0083 ruling 2 makes a title a publish surface,
the hook already extracts both, and that record measured 32 publishes carrying a title and no body
flag.

**The workflow step stays advisory and the asymmetry is deliberate**: the hook refuses because it can
still prevent, the workflow reports because it cannot.

**6. Six of the fourteen are repaired, eight are not, and the repair happens after this record and the
ticket cite them.**

The default is ADR 0048 ruling 14 — *nothing is repaired* — so the burden is on the case for
repairing, and finding 10 is why that default can be met rather than merely overridden. It is met
exactly where the damage falsifies something a reader copies or a rule grades:

- **The five malformed `**Branch state:**` blocks** on #471, #429, #519, #689 and #662. That block is
  specified by `docs/agents/issue-tracker.md` in an *"exact, unambiguous form"* and is graded by
  `tracker_branch_scope`; published with every backtick turned into a backslash, five times, it
  teaches the next sweep the wrong form. That is this repository's recurring shape — *a documented
  shape the grader would refuse teaches the next run to write one that fails*.
- **#9's corrupted regex.** A code span is the one construct a reader copies out verbatim, and a
  pattern that does not compile is worse than prose that reads oddly.

**The eight pull request bodies stay.** Nothing reads them as a form, nothing is copied out of them,
and each describes work already merged.

**The ordering is part of the ruling rather than advice about it.** Those six records are this
ticket's evidence. Repairing before this record and the ticket cite them by URL and date leaves an ADR
asserting a defect the live tracker no longer shows — retained in a revision, but only for a reader
who knows to ask GraphQL for it. So: record first, repair second, and each repair carries a dated line
saying what was corrected and why, since every repair is itself a publication the workflow grades.

## Consequences

**One build, on #723, and none of it is built here.** The ticket is respecified against these six
rulings; its decision 1 is answered by ruling 2, its decision 2 by ruling 3, its decision 3 by
ruling 1, its decision 4 by ruling 6, and the fifth decision #689's sweep added by rulings 4 and 5.
Its `records read` figures are corrected on finding 1 and its population on finding 2.

**Two of this ticket's own sweep comments carry false sentences** and are left standing rather than
edited, on ruling 6's boundary: they are dated claims about what a measurement showed, and finding 5
corrects them here where a reader arrives with the record. The `\e` claim and the *every `U+0008`
sits after a backslash* claim are both wrong; neither changes a ruling either sweep reached.

**The three non-control-character shapes are their own ticket**, because none is about a control
character and one of the three is not gradable until the `errors="replace"` ambiguity in ruling 3 is
solved.

**Ruling 4 is the one to read before touching any of it.** A build that adds the row to
`tracker_bodies.py` alone satisfies the ticket's letter and catches nothing at publication time,
which is that module's own recorded limit — *a command nobody runs is a written instruction with
extra steps* — and #214's thesis pointed back at the module that quotes it.
