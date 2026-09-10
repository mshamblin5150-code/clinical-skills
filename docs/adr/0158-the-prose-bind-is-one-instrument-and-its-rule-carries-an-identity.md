# The prose bind is one instrument and its rule carries an identity

[#835](https://github.com/mshamblin5150-code/clinical-skills/issues/835) was filed because the claim
*this prose names every row of that object and copies none of them* had no shared implementation. It
sat open for a week and was swept eight times, and every sweep read its second decision as a choice
between shingle widths 8 and 9.

**The width is inert and the sensitivity split is not the defect.** What the measurements below
establish is that the instrument the repository needs already exists, fully general, inside a test
module named after one document; that a pure shingle is blind to half the rows it is pointed at
whatever number it carries; and that one of the twenty-five sites is a copy the tree does not catch
today.

It also rules a consequence [ADR 0154](0154-the-apa-sheet-rests-on-the-manual-and-its-coverage-is-a-digest-bound-registry.md)
created and could not have foreseen: `tools/prose_bind.py` now backs a committed artifact, so its
normalization is no longer a test convenience.

This record supersedes nothing. [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s
refusal is still the standing rule and ruling 1 answers it rather than setting it aside.

## What was measured before ruling, on 2026-09-09

Freshness gate `FRESH` at `f67e1cd` before reading. `main` advanced twice mid-session and the branch
was brought forward each time; every figure below was re-derived at `7bea9b5`, whose merge brought
three new modules and two new test modules, neither of which adds a no-copy bind. Matchers are named.
Every count over the tree is a floor.

**The no-copy population is four sensitivities, not two.** Derived structurally by AST over `tools/test_*.py`, 112 modules, not by a name grep:

| sensitivity of the no-copy half | sites |
| --- | ---: |
| `exact` — raw `assertNotIn(row, text)`, blind to a hard wrap | 13 |
| normalized substring | 4 |
| shingle | 6 |
| other | 2 |
| **total** | **25**, over 22 modules |

Eight of the 22 import `prose_bind`. The majority class is the blind one.

**The width is inert and the short row is not.** Finding counts over the `CLAUDE.md` sections that
name a limits object are flat at 1 from width 8 through 16; over each module's own docstring they are
flat at 4 from width 6 through 11. Nothing in the tree distinguishes 8 from 9. But **246 of the 506
row strings in those objects are shorter than a nine-word window**, and a shingle computes no windows
for a short row, so the comparison is empty by construction. 34 of the 246 are not row keys, so the
key-substring check the shingle sites also carry does not reach them either.

**One of the twenty-five is a copy that passes.** `voice_corpus.NOT_REACHED` carries
`whether a reply is a rewrite of the same content is a reading, not a match`, and
`tools/voice_corpus.py`'s docstring line 99 reads
`assistant message with text below it. Whether that reply is a *rewrite of the same` / `content is a
reading, and 388 measured the gap`. A hard wrap, an emphasis mark and one changed word defeat
`assertNotIn` at once. `tools/test_voice_corpus.py:710` is green and its own docstring cites #241.

**The rule now backs a committed artifact.** `tools/apa7_coverage.py` stores
`sha256(prose_bind.normalized(section))` for 345 manual items. Mutating `PROSE_MARK` by one character
and reverting: adding `_` staled 46 rows, removing `*` staled all 345 and took `read-to-root` to 0.
The suite goes red, so it is not silent. The registry's only identity is its schema marker, which
describes the table's structure, and `apa7_coverage.DECLARED_LIMITS` has four rows, none about the
normalization.

**Section extraction is a second silent-pass axis.** Five implementations of *given a document and a
heading, return that heading's section*, under three closing rules — next `###` only
(`test_glossary_collisions.py:227`, `test_refusal_scan.py:344`, `test_tracker_freshness.py:266`),
`##` or `###` (`subject_ledger.py:41`), any `#` (`test_allergy_reaction_reasoning.py:32`). Over
`CLAUDE.md`'s 68 `###` sections they disagree materially on four. `### Tracker scan` is 12,577
characters under the first rule and 1,670 under the third, which cuts at a hard-wrapped line
beginning `#264's already-triaged findings`. That rule reads 13% of the section and reports clean
about the rest.

**Code masking exists three times and two of them claim the same thing.**
`test_skill_agreement._markdown_prose` masks with spaces and preserves offsets;
`tracker_bodies.prose_outside_code` deletes and does not; `test_python_floor.prose_outside_fences` is
fences-only and says so in its name. They disagree on 404 of 476 tracked Markdown files; on
`CLAUDE.md` the surviving non-space characters are 319,835, 319,554 and 357,374. And 32
heading-shaped lines sit inside code fences in tracked Markdown, three of them `###`, all in
`skills/_shared/reference/voice.md`.

**The walk that polices the declared-limits population sees 19 of 33.** Thirty-three non-test modules
hold an authored limits object, 35 objects in all;
`test_declared_limits.declarers()` is keyed on the literal name `DECLARED_LIMITS` and returns 19.
Fifteen authored declarers are outside it.

**One reasoned finding was falsified by driving the code, and it is recorded because the method is the
point.** `tracker_branch_scope`'s single-regex link matcher looked like a weak copy of
`test_skill_agreement.dead_links`. Driven, `_citation_prose` already calls `prose_outside_code`, the
two agree on every tracked file, and there is no defect. The apparent one was an artifact of running
the regex without the masking step that production already performs.

## Ruling 1. The shared instrument is built, and #253's refusal does not reach it

#253 refused an extraction on the ground that *a helper two modules happen to have written the same
way is not one that exists to be depended on, and a test pinning the agreement would forbid the
divergence the copy exists to permit*. That test is whether the copies were converging by accident.
These were not: every one encodes the same policy about the same repository, and the sensitivity
differences are unchosen rather than argued.

The deciding fact is that `prose_bind` now backs a committed artifact. A rule with a committed
consumer is `console_codec`'s and `repo_root`'s class by construction — infrastructure rather than a
coincidence — and infrastructure gets one implementation.

**One site keeps a stated divergence.** `test_differential_scan.py:1593` carries a written argument
for its window and a different mark set. It becomes a declared exception rather than a silent orphan;
its rows are all 60 words or longer, so nothing about its own floor moves.

## Ruling 2. The detector is the hybrid, and it already exists

`test_claude_pointers.copied_leaves` shingles a row of nine or more normalized words and compares a
shorter row by normalized substring. It walks into dataclass, dict and tuple rows so a row's parts are
each read, and raises when an object yields no strings at all, so an unreadable object cannot pass as
clean. It is already green over every limits pointer in `CLAUDE.md`.

It moves to `prose_bind` with `shingles` and `string_leaves`, and every no-copy site is pointed at it.
`test_claude_pointers` keeps only what is genuinely about that one document: finding the pointers.

A pure shingle at any width is refused, because it is blind to 246 of 506 rows. The exact form is
refused, because it is blind to the wrap that `prose_bind` exists for and a live instance is recorded
above.

## Ruling 3. The caller supplies the mode, because two contracts share one population

A surface that **points at** an object must copy no row. A surface that **enumerates** it must
reproduce every row in order — `apa7.md` §6 and §7 against `docx_write.NOT_APPLIED` and
`reference_scan.NOT_REACHED`, bound by `test_docx.py:1152` and `test_reference_scan.py:1989`, and the
step inventories bound by `test_checks_ledger.py:326` and `test_case_study_scan.py:938`.

Running the no-copy rule across the 21 non-`CLAUDE.md` surfaces that name a limits object returns nine copies, and every
one is an enumeration contract behaving correctly. A shared helper that assumed the first mode would
fail two sheets that are right. **The mode is passed in and never inferred**, which is #253's warning
arriving in the one form where it is real.

## Ruling 4. The normalization carries an identity, and a moved rule refuses rather than reports

ADR 0154 ruling 8 rules that structural drift refuses and staleness reports, on the ground that *no
tool here can tell a re-read from a recompute*. That is right when the sheet section moved. It is
backwards when the rule moved: the text a human ruled on did not change, so a recompute is provably
correct and a re-read buys nothing. The two are indistinguishable only because nothing records which
rule produced the digests.

**A digest of `tools/prose_bind.py` is recorded in the coverage registry beside its schema marker.** A
mismatch is structural drift, which ADR 0154 ruling 8 already refuses, and its remedy is a recompute
rather than 345 signed-in re-reads of a paywalled manual. The mechanism is
`guidelines_build._code_inputs`, which already hashes producing-file contents into an artifact
identity with the file list owned by `artifact_provenance.CACHE_IDENTITY`.

ADR 0154 ruling 8 is not overturned. A moved **section** still reports staleness exactly as it does
now.

## Ruling 5. The line with #875 is what the answer depends on

[#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875) asks in its own body that
this boundary be settled before either ticket starts.

**If a function's answer depends on what a document says, it belongs to #835. If it depends on which
files exist, it belongs to #875.** So `prose_bind` gains the copy detector, a `section(text, heading)`
with one declared closing rule, the enumeration mode, and the code masking a section reader needs.
Nothing about globbing, AST parsing or `ls-files` crosses into it; `git_paths` already owns tracked
paths and `test_git_paths.py:149` already enforces that for every non-test module.

**The declared closing rule is `subject_ledger.py:41`'s** — a `##` closes a `###`, and a `#` inside a
fence or at a hard wrap does not. The other two are converted rather than kept as exceptions.

**The masking implementation is the offset-preserving one**, because a bind that cannot report where
it fired is worth less than one that can. `tracker_bodies.prose_outside_code` is converted to it;
`test_python_floor.prose_outside_fences` is left alone as a declared narrower reader, which is exactly
the divergence #253 protects.

## Ruling 6. The four Markdown parsers leave, on their own ticket

`tools/test_skill_agreement.py` is 3,882 lines and holds four general-purpose Markdown parsers, not
the three #835 names: a step-citation resolver, a link resolver, an ADR ruling-ordinal parser, and an
ADR ruling-citation resolver. All four have their own liveness classes and none is about skills.

They are in #835's layer by ruling 5's test and they are **inherited rather than entangled** — the
copy detector never calls one. On the standing rule that entangled work widens a ticket and inherited
work is filed, they file, carrying this ruling and their liveness classes with them.

## Ruling 7. The bind population is graded as a bijection over objects, on #921

Nothing today catches a declared object with **no** bind, because the walk that enumerates the
population sees 19 of 33. `test_prose_bind`'s existing walk grades the silent direction of the sites
that exist, at a declared floor, with a raw positive assertion deliberately outside it; it catches a
bind written wrongly and never a missing one.

**Every authored limits object carries exactly one no-copy bind, through the shared detector.** That
is a bijection over objects rather than a pattern over calls, and it is the half that closes the
population hole. The seven-name vocabulary it needs already exists as
`test_claude_pointers.LIMIT_CONSTANTS` and travels with ruling 2's lift.

It is not entangled with #835's correctness — the shared detector works whether or not every object
has a bind — so it lands on
[#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921), which is already open on
precisely this blindness, with ruling 2's lift as its prerequisite. `test_prose_bind`'s walk stays
untouched: it grades a wider population than the limits objects.

## What none of this reaches

A bind assembled at run time, or a needle built by concatenation, is invisible to any walk here, which
is `test_ls_files_coverage.py`'s declared ceiling inherited rather than closed. A copy reworded past
the window is invisible at every width. And a clean detector says nothing about whether the prose it
read is *true* — a surface that points at the right object and copies no row of it can still describe
it wrongly, and no instrument in this repository reaches that.
