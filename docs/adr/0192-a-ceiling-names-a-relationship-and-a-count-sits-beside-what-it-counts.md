# A ceiling names a relationship and a count sits beside what it counts

[#932](https://github.com/mshamblin5150-code/clinical-skills/issues/932) was filed on 2026-09-06
claiming the step-citation hatch was full while `CLAUDE.md` still said a fourth exemption had to be
argued for. Seventeen comments and seven exhaustive sweeps followed. **Every one of them re-derived
the marker count correctly, and not one asked whether the sentence had ever been true.** The body
carries two dated corrections retracting the headline; the sentence it was filed over is still
wrong, for a reason nobody on the thread stated.

Grilled 2026-09-12 to an empty frontier. **Four rulings, by the clinician, on that date.**

## Measured before ruling, at `9c78d3f`

Freshness gate `FRESH` before any reading.

**The hatch has one free slot.** `marker_exemptions(CLAUDE.md, EXEMPT_MARKER)` returns three spans,
declared sum 3, against `EXEMPT_CEILING` of 4, asserted as `assertLessEqual`. *Under the filed
headline being true that reader prints four spans and sum 4; it printed three and 3.*

**Nothing here ever went stale, which retires the frame the whole thread reasoned inside.**
`EXEMPT_CEILING` has been `4` and the declared sum `3` since `f4daa6a0`, 2026-08-19, and every
sentence at issue is byte-identical to that commit. *Had any drifted, a diff against `f4daa6a0`
would show it at that line; all are clean.* So this is neither
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape nor
[#928](https://github.com/mshamblin5150-code/clinical-skills/issues/928)'s. **One authoring error
was made once and written into three places, and the mechanism meant to prevent it — *"The count is
not restated in prose anywhere"* — was declared in the same commit that violated it three times.**

**The defect is arithmetic and not a stale figure.** With a ceiling of `4` and `assertLessEqual`,
the first refused exemption is the **fifth**. `CLAUDE.md` and `EXEMPT_CEILING`'s own comment both
named the *fourth*. **That is wrong at every declared count**, because it names the ceiling's own
digit rather than one past it, so correcting the ordinal to *fifth* would leave a sentence that goes
wrong again the day the ceiling moves.

**The two false sentences are not count restatements, which is why the filed frame indicted the
wrong ones.** Driven through `test_constant_prose_counts.DEFINITE_COUNT`, the predicate matches
`the three exceptions` and `The three citations` — both **correct** at the time — and matches
neither `a fourth has to be argued for` nor `the next one has to be argued for`. *Under the filed
frame being right, the predicate fires on the defects; it fired only on the sound sentences.* So
decision 1 as filed — delete every count from prose — would have removed two true sentences and
left both defects standing.

**A third restatement sits in the module whose comment denies one exists**, twenty-five lines above
it, and **a ratified record inherits the ordinal**: ADR 0059 ruling 6 read *"`EXEMPT_CEILING`'s
comment asks that the next one be argued for in a diff rather than typed."* Neither was named on the
thread.

**The same module holds three ceilings under three disciplines, and a fourth is in
`scratch_census.py`:**

| constant | slack | what its comment says | true? |
| --- | ---: | --- | --- |
| `EXEMPT_CEILING` | 1 | denies any prose restatement; names the wrong ordinal | no, twice |
| `RULING_EXEMPT_CEILING` | 1 | **nothing — a bare constant with no comment at all** | n/a |
| `RULING_UNNUMBERED_CEILING` | 0 | states both digits of its own movement, the ticket, and the reason | **yes** |
| `OWNING_BASELINE` | n/a | states the rule and **no digit at all**, per ADR 0059 ruling 3 | yes |

**The ceiling whose comment states the most digits is the only one whose comment is true**, and it
is the only one genuinely full, so its next addition really must be argued for in a diff. It works
because the count sits two lines above the constant: a change to either lands in one diff.

**The instrument that misled the thread over-counts by exactly one, in both hatches.** A `grep` for
the step marker returns four and the reader returns three; the fourth is the fenced syntax example.
Taking the ruling-hatch measurement for this record I made the identical error — a naive count
returned 20 unnumbered markers against a ceiling of 19, and `unnumbered_ruling_marker_count` returns
19, because the naive count read a fenced specimen. **A file that contains its own syntax example
cannot be counted with a matcher that does not know what a fence is**, and this is
`spelling_scan.py`'s mention-versus-use rule arriving on a count.

**A detector over prose is measured unavailable rather than argued against**, which is
[ADR 0182](0182-the-refusing-check-roster-lives-in-the-hook-and-prose-keeps-only-its-own-claim.md)
ruling 4's method applied to a second object. Every proposed widening of
`test_constant_prose_counts`, driven over the tree:

| widening | findings | declared exemptions would go | reaches this defect? |
| --- | ---: | --- | --- |
| current, constant string literals | 1 | 1 | no |
| **plus tracked Markdown** | **1,206**, in half the corpus | 1 to about 1,206 | **no** |
| plus Python comments, non-test only | 39 | 1 to about 40 | **no** |
| plus Python comments including test modules | 72 | 1 to about 73 | only the sentence deleted here |

*Under a widening being the answer, at least one row reaches a defect this record is about. None
does.* Re-derive with `DEFINITE_COUNT` over the index; the figures move with the tree and are
recorded here as the measurement that declined an option, not as a constant.

## Ruling 1. A ceiling's prose names the relationship and never the ordinal

`CLAUDE.md` and `EXEMPT_CEILING`'s comment both say **an exemption past the ceiling** has to be
argued for in a diff rather than typed. Naming *a fifth* was refused: it is `EXEMPT_CEILING + 1`
spelled as a word, so it repairs today's digit and keeps the generator that produced the defect.
Deleting the clause was refused too — it carries why a ceiling exists at all, which is the half of
the paragraph doing the arguing rather than the counting.

## Ruling 2. A count sits where one diff covers it and what it counts, or nowhere

**The rule.** A count may stand where a change to it and a change to the thing it counts land in the
same diff. It may not stand anywhere else.

`RULING_UNNUMBERED_CEILING`'s *"Raised 18 to 19"* passes: the comment is adjacent to the value.
`CLAUDE.md`'s *"The other three are all in this section"* passes: it enumerates all three in the
same sentence, which is the ground `DECLARED_DEFINITE_COUNTS`' one live entry is already blessed on,
and the *"those three"* pointing at it inherits that. **Both bare restatements fail and are
deleted** — `the three exceptions` and `The three citations` each counted markers in another file
with nothing joining them. **Deleting them makes `EXEMPT_CEILING`'s comment true as written**, so
ADR 0059 ruling 3's quotation of it needed no correction; the exemplar that ruling cites now holds.

**Adjacency is not the same as being immune.** Somebody can still change a value and not its
neighbouring comment. What adjacency buys is that the two sit in one hunk, so the omission is in
front of whoever writes and whoever reviews the diff — which is the whole of what *argued for in a
diff rather than typed* ever meant.

## Ruling 3. The floor is two regression binds, and it is declared as a floor

`ACeilingsProseNamesNoOrdinal` holds that neither retired sentence returns, in `CLAUDE.md` and in
`EXEMPT_CEILING`'s own comment block. **It is a floor**: a reworded ordinal claim escapes it
entirely, no detector is available to reach one, and the module says so beside the bind rather than
leaving a reader to take it for coverage.

**Two things it does not reach were found by driving it rather than by reading it.** Its first
version read the whole module and failed on the `RETIRED` tuple three lines below — a test holding a
phrase in order to refuse it is a mention, and the check written for mention-versus-use fell to it
on its first run. Its second version read the constant's comment block without stripping the marker;
`PROSE_MARK` removes the hash and keeps the colon, so every wrap left a stray `": "` and **no needle
spanning one could match**. That version passed a correct mutation. The liveness control had been
built from an inline string, which does not have the shape the real haystack has, so it could not
discriminate — the control is driven through the reader with a wrapped phrase now.

## Ruling 4. This is a floor and a stricter local rule outranks it

Ruling 2 permits an adjacent count. **ADR 0059 ruling 3 forbids one entirely for `OWNING_BASELINE`**,
on a recorded incident rather than a preference, and **this record does not loosen it.** Where a
local rule is stricter, the local rule governs and says why beside itself, which `scratch_census.py`
already does.

**`Hatch` and `Ceiling` enter `CONTEXT.md`.** The sense collision is real and live in `tools/`: a
`Bar`'s stated maximum is transcribed and never honored per ADR 0103, while a hatch's ceiling is
always graded and refuses. **It is invisible to the collision inventory** — `candidate_headings`
fires only when a single-word heading appears inside another heading, and the course sense lives in
the `Bar` entry's body — so it is declared in the `Ceiling` entry itself, on the precedent the
`Join` entry already set for a sense a heading-derived read cannot see. No `DECLARED_CANDIDATES`
verdict is owed and none is written.

## What this record does not settle

**Why `RULING_EXEMPT_CEILING` is 2.** One exemption is declared against it, it carries no comment at
all, and ADR 0075 and ADR 0133 both cite it as a precedent without stating its reason. Filed
separately: writing that reason is a decision, and inventing a rationale for a number nobody here
chose is what this repository refuses.

**Whether any surviving adjacent count is correct.** Ruling 2 is about where a count may stand, not
about whether it is right. `RULING_UNNUMBERED_CEILING`'s comment is true today because somebody
checked, not because it is adjacent.

**Every ceiling and baseline in `tools/`.** A ceiling caps a declared population; a measured
threshold shares the suffix and is a different object, so the sweep was declined rather than run.
