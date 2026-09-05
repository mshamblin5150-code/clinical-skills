# The shared sheet directory moves whole and the mirror gains a non skill rule

Ruled by the clinician on 2026-09-05, in the grilling of
[#758](https://github.com/mshamblin5150-code/clinical-skills/issues/758). Freshness gate `FRESH` at
both checkpoints. Nothing is built here; this is the record the build reads.

[ADR 0097](0097-the-apa-sheet-s-class-vocabulary-is-apa-s-nursing-set-and-coverage-is-decided-per-bucket-while-the-gate-is-a-bind-test.md)
ruling 7 refused to move `apa7.md` alone and declared the set a separate question. This is that
question, answered.

## Measured before ruling, at `b26ea2a`

**The reader table re-derived, and #758's headline is wrong in a third way.** Nine skills exist.
`voice.md` is read by five others — `clinical-note`, `course-assignment`, `discussion-post`,
`discussion-reply`, `setup-clinical-skills`; `rubric.md` by `discussion-reply`; `apa7.md` by
`discussion-post`; `voice-corpus.md` by `setup-clinical-skills`; `style.md` by none. The title's
*four of five skills* is **five of the eight others**.

**The clinician supplied the cause, and it is not design.** `practicum-case-study` was the first
skill written, so every later skill reached into the only `reference/` that existed. The directory
never carried an ownership claim; it carried a chronology.

**The directory is one cluster and `style.md` is its hub.** Ten sibling links, all written as bare
same-directory targets such as `[apa7.md](apa7.md)`:

| from | to | links |
| --- | --- | ---: |
| `style.md` | `apa7.md`, `voice.md`, `rubric.md` | 5, 2, 1 |
| `voice.md` | `style.md`, `voice-corpus.md`, `rubric.md` | 4, 2, 1 |
| `rubric.md` | `style.md`, `apa7.md` | 3, 1 |
| `apa7.md` | `style.md` | 2 |
| `voice-corpus.md` | `voice.md` | 1 |

So the sheet with **no** external reader is the one nine sibling links point at. *Practicum-only* is
true of `style.md` at the skill level and false at the sheet level.

**How the six files are cited, classified by whether a check can see the mention.** Counts are
occurrences of the six basenames over tracked files:

| area | Markdown links, graded by `EveryRelativeLinkResolvesToAnIndexedPath` | inline-code and prose, graded by nothing |
| --- | ---: | ---: |
| `skills/` | 69 | 71 |
| `tools/` | 5 | 125 |
| `docs/adr/` | **0** | **39** |
| `CLAUDE.md` | 8 | 18 |

**#758's third *what must not come out of this* rests on a false premise.** Its *"a dead relative
link in a skill file fails nothing today"* stopped being true on 2026-08-27, when
[ADR 0054](0054-a-relative-link-resolves-against-the-index-and-the-fixture-exclusion-is-shared-rather-than-copied.md)
landed the resolver over every tracked `.md` outside `fixtures/` — five days before the ticket was
filed.

**What each destination costs, in populations lost with nothing firing.** The four skills-rooted
walks are `test_skill_agreement.instruction_files()`, `test_blind_fixture_instructions.REQUIRED_INSTRUCTIONS`,
`test_docx.py`'s phantom-table walk and `test_corpus_census.py`'s figure sweep. All four are rooted
at `skills/`, not at `skills/<a skill>/`:

| destination | populations lost silently | note |
| --- | ---: | --- |
| `reference/` (repo root) | 4 | no `*.md` walk exists there; only named-file constants |
| `docs/` | 4 | same |
| **`skills/_shared/reference/`** | **0** | stays inside `SKILLS_DIR.rglob("*.md")` |
| `reference/thresholds/` | — | refused on sight: `SHEET_ROOT.glob("*.md")` would parse them as threshold sheets |

**The step citations, re-derived by running this repository's own `step_citations` over each sheet
twice** — once with `owner="practicum-case-study"` and once with `owner=None`:

| sheet | citations | lost if it leaves a skill directory |
| --- | ---: | ---: |
| `style.md` | 8 | **8** |
| `apa7.md` | 5 | **5** |
| `voice.md` | 6 | **2** |
| `rubric.md` | 1 | **1** |
| `voice-corpus.md` | 0 | 0 |

Every lost one is written `[SKILL.md](../SKILL.md) step N`, so the link text names a filename rather
than a skill and the `beside` limb never fires. `owning_skill` returns `None` outside a named skill
directory, and `test_the_unresolved_limb_is_reported_and_never_floored` **permits** an unresolved
`owner`-limb citation, so nothing fails and nothing ever would.

**What breaks loudly, which is what makes the move safe.** `test_docx.py`'s sheet-table walk is
rooted at the practicum `reference/` directory with `FLOOR = 9`, and the five sheets hold twelve
tables — `apa7.md` 3, `rubric.md` 2, `style.md` 4, `voice.md` 3, `voice-corpus.md` 0. Six path
constants open the sheets directly. The relative-link resolver reads every cross-skill citation.

**The mirror.** `skills_mirror.py` treats a directory under `skills/` as a skill when it holds a
`SKILL.md` and mirrors nothing else, so today `../practicum-case-study/reference/voice.md` resolves
through the mirror only because that skill is itself junctioned. `.claude/` is gitignored, so no
check reads the mirror.

**`git worktree add` fires `post-checkout`, measured rather than assumed.** A throwaway repository
with a `post-checkout` hook logged `FIRED args=0000000000000000000000000000000000000000 <sha> 1` on
`git worktree add`. The null first argument is the discriminator between a worktree or clone
checkout and an ordinary branch switch, and `core.hooksPath` is already an absolute path in shared
config, so a new worktree inherits the hook with no setup.

## Ruled 2026-09-05

### 1. The whole directory moves to `skills/_shared/reference/`

All five sheets and `word-renderer-calibration.json`, as one unit. `practicum-case-study` keeps no
`reference/`.

**Moving the whole directory is cheaper per unit of churn than moving the shared four**, which is
the finding that decided it. The four cost eight prose repairs *plus* rewriting ten intra-cluster
links in both directions, and strand the hub. The five cost sixteen prose repairs and **zero link
rewrites**, because every sibling link is a bare same-directory target that stays correct when the
directory moves as a unit.

**`style.md` having one reader is not a residual anomaly.** What was anomalous is a directory
*named for one skill* holding four other skills' sheets. A neutrally named directory holding a sheet
with one reader is an ordinary fact about that sheet.

### 2. `skills/_shared/` over the repo-root `reference/`, decided on populations rather than on category

Root `reference/` is the intuitive destination and it is the expensive one: four walks lose the
sheets with nothing firing. `skills/_shared/reference/` keeps every one, because those walks are
rooted at `skills/` and not at a named skill.

**This is not a ruling that authored prose belongs under `skills/`.** It is a ruling that these
files should stay inside the population that already grades them.
[ADR 0132](0132-the-uptodate-store-is-scratch-rooted-and-its-published-topic-sheets-carry-the-entitlement.md)
ruling 3 sends a different artifact class the other way for the opposite reason, and the two
together are the distinction #758 decision 2 was reaching for: **instruction stays in `skills/`,
data about the literature goes under `reference/`.**

### 3. The sixteen citations are repaired in prose and the resolver is not touched

Rewrite each `[SKILL.md](../SKILL.md) step N` so the link text names the skill, which moves every
one to the `beside` limb.
[#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238) solved the identical
problem in `tools/` this way at no cost to the resolver, and that precedent transfers exactly.

**A parser change was refused.** Teaching `owning_skill` about a shared directory would invent an
owner for a file that has none, which is the inverse of the honesty the third limb exists for.

### 4. The mirror gains a rule for a directory under `skills/` that carries no `SKILL.md`

`skills/_shared/` must be junctioned into `.claude/skills/`, or every cross-skill link is dead when
a skill loads natively and **nothing reports it**, because `.claude/` is gitignored.

The rule is the builder's to shape — an allowlist or a widening to every directory — but the
comment at `skills_mirror.py`'s `SKILL_FILE` states today's rule deliberately, so whichever is
chosen replaces that sentence rather than sitting beside it.

### 5. `post-checkout` repairs a new worktree's mirror, and it lands whether or not the move does

`tools/hooks/post-checkout`, gated on the null first argument, running `skills_mirror.py --repair`.

**It closes a standing defect that predates this ticket.** `CLAUDE.md` ends its mirror section with
*"Every worktree still needs its own `--repair`, and nothing will ask."* This is the thing that
asks, and the mirror is graded by nothing else.

### 6. The repoint's completion is a grep, and ratified records are left alone

After the move, `git grep -c "practicum-case-study/reference/"` outside `docs/adr/` and `fixtures/`
reads **zero**. That turns 125 `tools/` prose mentions and 18 in `CLAUDE.md` — none of which any
check can see — into one criterion a reviewer can run.

**The 39 mentions in ratified ADRs stay.** They are all inline code and none is a Markdown link, so
no resolver breaks, and a path in a ratified record is a dated statement about the tree at
ratification. Editing one to keep it true would falsify the record, which is the rule this
repository already applies to a preserved run record.

### 7. #758's body carries five measured errors and they are corrected rather than left in comments

The dead-link premise above; *four of five skills* when it is five of the eight others;
`tools/test_skill_agreement.py:3258`, which is `:3349`; the **81 references** figure, which
re-derives at no scoping — `apa7.md` is 110 occurrences across 25 tracked files at `b26ea2a`; and
ADR 0097 ruling 7's *"`rubric.md` by two"*, measured as one.

**A sixth finding is not an error but retires the ticket's framing.**
`skills/discussion-post/reference/canvas-paste-calibration.json` is a second skill-owned
`reference/`, so a skill having one is an established pattern and was never the anomaly.

## What this record does not settle

**Whether `skills/_shared/` is the right name.** `_shared`, `shared`, or `reference` under `skills/`
are all inside the population that matters; the leading underscore is the builder's call and no
check reads it.

**Whether the mirror rule is an allowlist or a widening.** Ruling 4 requires the outcome and not the
mechanism.

**Whether a second non-skill directory under `skills/` should ever exist.** This ruling creates one
and says nothing about the next.
