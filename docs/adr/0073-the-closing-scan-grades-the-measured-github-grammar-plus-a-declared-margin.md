# The closing scan grades the measured GitHub grammar plus a declared margin

[#574](https://github.com/mshamblin5150-code/clinical-skills/issues/574) found two defects in
`tools/closing_keyword_scan.py`'s `BINDING`: no word boundary after the keyword, so `fixtures`
matched as a keyword, and a `between` window of anything-but-sentence-punctuation across newlines,
so a keyword in a heading bound a reference deep in the body. The first was ruled at filing; the
second was the posture question this grilling existed for — *report every binding* against
*report what GitHub would act on*.

Grilled 2026-08-29. The rulings below were put to the clinician one at a time and each agreed.
Nothing is built here; this is the record the build reads.

## The measurement came first, because both sides of the thread rested on unmeasured claims

In [#183](https://github.com/mshamblin5150-code/clinical-skills/issues/183)'s record, every
close GitHub actually performed is keyword-adjacent. Every *GitHub did not act* datum on #574's thread was taken on an
issue comment or a committed record — and those are surfaces GitHub never scans, so the non-close
half of the ledger had measured nothing at all. The wide window itself traces to a reasoned claim
on #183 that a list item under a keyword-and-colon sentence would close, which no recorded GitHub
action ever supported.

So the grammar was measured live, with the clinician's authorization, in
`mshamblin5150-code/closing-keyword-probe` — private, synthetic, kept. Fourteen probes, both
positive controls live, every shape written byte-exact from files. `N` below is a placeholder,
because a probe shape quoted with a real number is armed the moment it is pasted onto a live
surface:

| probe | surface | shape | closed? |
| --- | --- | --- | --- |
| 1 | commit on default branch | `fix #N` adjacent — control | **yes** |
| 2 | commit | keyword, then prose, then the reference, one sentence | no |
| 3 | commit | keyword ends a line; the reference opens the next | **yes** |
| 4 | commit | keyword and colon, a blank line, then the reference | **yes** |
| 5 | commit | keyword and colon, a blank line, then a `- ` list item | no |
| 6 | commit | triple-backtick fence around an adjacent form | **yes** |
| 7 | commit | keyword welded into a hyphenated compound | no |
| 8 | merged PR body | adjacent form — control | **yes** |
| 9 | merged PR body | triple-backtick fence around an adjacent form | no |
| 10 | merged PR title | adjacent form, body inert | **yes** |
| 14 | commit | keyword, then a parenthesized reference | no |
| 15 | commit | keyword, then a bold-wrapped reference | no |
| 16 | commit | keyword and colon, a blank line, then a `> ` quote line | no |
| 17 | issue comment | adjacent form | no |

**The grammar, as measured on 2026-08-29:** a whole-word keyword — a hyphen weld is not one — an
optional colon, then any run of whitespace including newlines and blank lines, then the
reference. Nothing else survives between: prose, a list marker, a quote marker, a parenthesis and
bold wrapping are all inert, at any distance.

Four load-bearing claims fell to the table. The list-boundary close that justified the wide
window does not happen (probe 5). Fencing buys nothing in a commit message (probe 6) **and buys
everything in a PR body** (probe 9), so the thread's *backticks buy nothing* was half right and
the half was surface-shaped. The two prose-distance non-closes on the thread were taken on
non-surfaces and measured nothing (probes 2 and 17 are the real data). And a PR **title** alone
closes (probe 10), which the module's docstring claimed and its author doubted.

## Rulings

1. **Limb 2 moves, from stance to measurement.** `BINDING` becomes
   `\b(close[sd]?|fix(?:e[sd])?|resolve[sd]?)(?!-)[\s:]*#[0-9]+\b` (case-insensitive). The
   `between` of `[\s:]*` is the measured grammar plus the cheapest conservative slack — it
   over-reports only on unmeasured colon-and-whitespace mixes nobody writes, and under-reports on
   nothing measured. The sentence-boundary concept, and the comment describing it, are deleted
   with the window.
2. **Limb 1 rides inside it.** Adjacency supplies the trailing boundary, and `(?!-)` refuses the
   hyphen weld, which probe 7 shows agrees with GitHub. Every word in the ticket's table goes
   clean, including the hyphenated one a bare trailing boundary could not clear.
3. **Fences fire uniformly on every surface, and probe 9 is declared margin rather than honored.**
   The argument is migration: this repo's recorded failure shape is quoted text moving between
   surfaces, and a fenced form in a PR body is one paste from a commit message, where fences are
   measured live. One grammar, no field-dependent branch.
4. **The declaration is a `DECLARED_LIMITS`-style module object, and this record is the table's
   one home.** The object names the grammar rows, the margins (the colon-whitespace slack and the
   fence posture), the non-surfaces (issue comments — measured, probe 17 — and repository files),
   and the standing limit that GitHub's parser is unversioned and can drift; it cites this ADR
   and the probe repo for the per-probe evidence and copies no row of the table. The docstring
   points at the object.
5. **Callers.** One sentence in `docs/agents/issue-tracker.md`: the scanner runs last, nothing
   consumes its output, its exit status is the verdict — the four recorded drops were all
   pipelines that read some other command's status. And `continue-on-error` comes **off** the
   pull-request CI step: under the measured grammar a finding is almost always a shape GitHub
   would act on, so a red X at the one pre-merge moment somebody looks is signal. The
   push-to-`main` step stays advisory — it fires after GitHub has already acted, so blocking
   there buys nothing. No required status check; ADR 0002's posture is untouched.
6. **The probe repo is kept**, private, as the measurement's re-derivation — a suspected parser
   drift re-runs against the same issues in minutes instead of being rebuilt from prose.
7. **The vocabulary splits.** `CONTEXT.md` gains **Closing hazard** — text on a graded surface
   that GitHub's measured closing grammar would act on, accidental by nature — distinct from a
   **Binding**, which is deliberate and owns its line. The finding message says *would close*
   rather than *binds*, which is also simply truer now that the pattern is the measured grammar.

## Consequences

Three pinned tests flip, each on a named probe rather than a stance: prose-between (probe 2),
same-clause (probe 2), and the list boundary (probe 5). The ticket's third *Done when* stands
whole: every cleared word is driven through the scanner and asserted clean, and the same word
with the keyword standing alone is asserted to fire, so a pass is caused by the boundary and not
by a dead matcher. What no probe reaches stays with the object per ruling 4 — the sharpest limb
is that a measurement of an unversioned parser is dated evidence, not a contract, which is why
the margin leans wide and the probe repo stays alive.
