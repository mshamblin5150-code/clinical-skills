# The read failure posture is keyed on the input's role and only the crash is ruled family wide

Found while grilling [#843](https://github.com/mshamblin5150-code/clinical-skills/issues/843) and
[#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839), 2026-09-02, at
`origin/main` `c024551`, freshness gate `FRESH` at both checkpoints. **Ruled by the clinician on
that date.** Nothing is built here; this is the record the build reads.

[ADR 0114](0114-a-run-directory-reader-grades-a-replaced-byte-and-the-family-s-read-failure-posture-is-measured-rather-than-ruled.md)
ruling 3 sent this question to its own ticket and required it to be ruled with or before #839
decision 1. It is, and the two records were ruled in one session for that reason;
[ADR 0115](0115-the-run-directory-reader-is-extracted-into-the-runner-and-refuses-a-source-it-cannot-open.md)
is the other half and depends on ruling 2 below.

## Measured before ruling, at `c024551`

Every figure was re-derived by running the code rather than by reading it, and four of them
disagree with the ticket that prompted the grilling.

**The population moved under both tickets and neither says so.** #830 landed between filing and
grilling: `NOT_MEMBERS` no longer exists, `MEMBERS` is 14, and `REFUSED` and `DEFERRED` split what
it held. `aar_scan` and `filled_vitals_census` are the two deferrals, so the population is still 16.

**#843's axis 2 counts two verdicts on a file `open()` refuses. There are four.**

| posture | status | who |
| --- | --- | --- |
| `SourceError` on the load path | 2 | `case_study_scan` `deck_scan` `discussion_post_scan` `discussion_reply_scan` `voice_model_scan` |
| degrade into the report and state the narrowing | what the artifacts say | `specificity_scan.load_second_read`, `case_study_scan`'s `skill_text = None`, `render_scan`'s retained-export read |
| a deliberate **finding** | 1 | `aar_scan` -- `Finding("unscannable-review", ...)` |
| no handler | 1, uncaught | the ten ADR 0114 names |

The third is the one that matters, because #843's `Done when` reads *no reader in the population
exits 1 for a reason that is not a finding* and `aar_scan` exits 1 for a reason that **is** one.

**The residue reproduces on every run-directory reader.** A deny ACL on one worksheet of a copy of
`fixtures/filled-anchor/run-2`:

```
anchor_scan  specificity_scan  refusal_scan  block_scan  differential_scan  filled_vitals_census
    -> PermissionError, EXIT=1   (all six)
case_study_scan -> EXIT=2, "cannot read ...: Permission denied"
```

**The two axes are orthogonal and `case_study_scan` is the proof.** #843 decision 1 names it as the
case refuting the set-versus-single boundary, measuring axis 1 alone. On axis 2 it is the model:
`SourceError` for the draft it was pointed at, and `skill_text = None` for `SKILL.md` with a comment
saying *it says so rather than reporting a check that did not run as one that passed.* One module,
two postures, and what separates them is not the artifact class.

**The set-versus-single boundary is refuted in both directions, not one.** `discussion_reply_scan`
reads a set -- `posts/*.md`, `board-*.md`, `response-*.md` -- and refuses at
`tools/discussion_reply_scan.py:457`. `checks_ledger`, `reference_scan` and `research_ledger` each
read a single artifact and grade. The landing date still predicts everything the class does not.

**ADR 0114's classifier over-matched a second time, and this one was not caught.** That record
reports correcting one over-match by opening `reference_scan` and finding its `ValueError` was an
`--as-of` parse. `render_scan` is the second: it has **zero** builtin text reads, both `open(` sites
are `pymupdf.open`, and each sits inside `except Exception` returning a stated read error. It has no
undecodable-byte path at all and is not a crasher.

Corrected axis-1 distribution on the load path:

```
GRADE (9)   anchor_scan block_scan case_study_scan checks_ledger differential_scan
            filled_vitals_census reference_scan research_ledger specificity_scan
REFUSE (4)  deck_scan discussion_post_scan discussion_reply_scan voice_model_scan
CRASH (2)   aar_scan refusal_scan
NO TEXT (1) render_scan
```

**Re-derived at `eac8d7b`, after the rulings and before this record was published.**
[#838](https://github.com/mshamblin5150-code/clinical-skills/issues/838) landed mid-session, so
`refusal_scan` now reads with `errors="replace"` and leaves the crash row:

```
CRASH (1)   aar_scan
GRADE (10)  the nine above, plus refusal_scan
```

It gained no `OSError` handler, so it stays in the axis-2 residue and the deny-ACL reproduction
above is unchanged. **No ruling below moves**; ruling 3's closing paragraph is now true at `main`
rather than after ADR 0115.

**Five of the sixteen carry no limits object at all** -- `anchor_scan`, `block_scan`, `render_scan`,
`specificity_scan`, `filled_vitals_census` -- and four of those five are run-directory readers.

**Three live senses of `tier`, not two.** `CONTEXT.md` §Tiers owns note content;
`threshold_sheet` uses citation resolution tiers in 62 places and `CLAUDE.md` documents them;
`run_grader.py:141` is the third and the one #843 decision 4 names. The second sense appears in no
glossary entry and `test_glossary_collisions` cannot see it -- its declared limit is that only
`CONTEXT.md` is inspected.

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. They move the day
a grader lands or a reader is extracted.

## Ruled 2026-09-02

### 1. The read-failure posture is a property of the input's role, not of the module and not of the artifact class

Three roles, each with its own posture. A **primary source** is the artifact named on the command
line, whose absence leaves no denominator: refuse, exit 2. An **optional secondary** narrows
coverage when absent: degrade into the report and state the narrowing, never silently pass. A
**tracked reference artifact** shipped in the checkout means a broken checkout rather than a bad run.

**The ground is that it describes the code that is already correct rather than overwriting it.**
`case_study_scan` is not an exception to a role-keyed rule, it is the worked example of one, and
`specificity_scan`'s second read and `render_scan`'s retained export are the other two instances
already in the tree. A module-keyed rule cannot express a module holding two postures at once, and
the artifact class was measured above to predict neither axis.

**ADR 0114 ruling 1 is untouched and this is not a side door onto it.** The byte verdict stays a
property of the artifact class -- a set reader grades a replaced byte -- and the `open()` verdict
becomes a property of the role. The two axes stop being asked as one question, which is what let
#843's own decision 1 read `case_study_scan` as a refutation when it is a demonstration.

**The cost is named rather than left to be found.** Role is not a mechanical property. Nothing can
walk `tools/` and tell you a given `read_text` serves a secondary rather than a primary, so a
role-keyed ruling is enforced by declaration per module and never by a conformance walk. That is
weaker than a module-keyed rule and it is the trade taken deliberately.

### 2. The shared reader raises `SourceError`, and #843's stated impossibility does not survive measurement

#843 decision 2 holds that the shared reader **cannot** raise `SourceError` because that class lives
in `run_grader` and `filled_vitals_census` is a non-member. As an import-graph fact that is refuted:

```
tools/aar_scan.py:37              from run_grader import NOT_GRADED     # aar_scan is DEFERRED
tools/filled_vitals_census.py:173 import aar_scan
tools/filled_vitals_census.py:698 aar_scan.completion_gate(...)
```

`run_grader` is already in `sys.modules` when `filled_vitals_census` loads, verified by importing
it. Both deferrals already depend on the runner and one of them directly, on **#830's own
`NOT_GRADED` constant** -- landed the day before, on the reasoning that a shared policy belongs in
the runner and a non-member may import it. Ruling the opposite here, one ticket later, for the same
class of thing, needs a reason that distinguishes a constant from an exception class and none was
found.

**A new typed failure the callers convert was refused for a reason, not skipped.** It is the option
#843 names, and under this ruling it is a module that depends on `run_grader` in order to avoid
depending on `run_grader`: a second exception class plus six conversion blocks that do nothing but
rename it. Each caller's own `_load` converting was refused on the same measurement -- it leaves six
`except OSError` blocks in six modules, which is the copied-policy shape #839 exists to remove,
relocated one function up.

**This constrains [#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839) decision 1
and it is why the two records are one session.** ADR 0114 ruling 3 wrote the dependency as
conditional: a ruling of *each caller converts* would have left #839 decision 1 untouched. It went
the other way, so ADR 0115 is bound by this.

### 3. There is no family-wide verdict on an undecodable byte, and only the crash is ruled

ADR 0114 ruling 1 stands scoped to the run-directory reader. Every other module's grade-or-refuse
choice is declared with its reason. The one family-wide rule is the crash: **no reader exits 1 for a
reason that is not a finding.**

**#843's own `Done when` already says this.** *No reader in the population exits 1 for a reason that
is not a finding* is a rule about the crash and says nothing about grade versus refuse; the title
bundles the two because they were taken in one walk, not because one answer governs both.

**The distinction is that the crash is a defect and grade-versus-refuse is a design choice.** The
crash is [#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150)'s shape on an
input stream -- a dead process presenting in the status this family reserves for a real finding --
and no module chose it; it is what writing no handler produces.
[ADR 0113](0113-the-per-grader-report-frame-is-affirmed-a-second-time-and-the-shared-report-value-is-declined-on-measurement.md)
ruling 1 measured this exact class and affirmed that divergence reflecting a ruling stays
per-grader.

**Generalizing ADR 0114's own ground was priced and declined.** Its reason was the denominator, and
stated generally that is *grade where the read is one member of a graded population, refuse where
the read is the whole grade.* It is principled, and it moves five modules nobody read --
`case_study_scan`, `checks_ledger`, `reference_scan` and `research_ledger` from grade to refuse, and
`discussion_reply_scan` the other way. ADR 0114 refused rulings over unread modules four separate
times and nothing measured here reverses that.

**The axis-1 crash population is one module.** This was written as a prediction -- *`refusal_scan`
closes under #838 plus the shared reader; `render_scan` was never in it* -- and #838 landed at
`eac8d7b` before publication, so it is now a measurement. `aar_scan` is the whole residue, it is a
deferral with its own migration ticket, and its unreadable-review path already converts to a
finding.

### 4. The declaration is a family-wide map in `run_grader`, held by a behavioral probe and a declared floor

The map is name to reason, on `REFUSED` and `DEFERRED`'s shape and covering non-members as those two
already do. Per-module `DECLARED_LIMITS` is refused on the measurement above: it would mean
inventing a limits object in five modules to hold one line, and it leaves the split invisible, which
is the condition that let #843 exist.

**It is at least three-valued.** `render_scan` reads no text at all, and a two-valued map would
force it into a verdict it cannot hold.

**One behavioral probe settles six of the sixteen, and the extraction is what pays for it.** ADR
0115 makes the six run-directory readers one body, so a single test against the shared reader
establishes the byte verdict for all six with real evidence and no per-member fixture. That moves
the population needing the weaker instrument from sixteen to ten.

**For the remaining ten the matcher is a floor and must say so**, on this repository's
extractor-coverage rule -- *a matcher never gets to turn a partial read into a clean whole.* Given
it has produced two false classifications inside ADR 0114's own measurement, its acceptance is
conditional: it is fed a zero-match and a partial-match mutant and driven red before its coverage
claim is believed, and its ceiling is written beside it.

### 5. Only a member that already declares an exit-2 vocabulary gains a limb, and the limb is one object

Under ruling 2 the shared reader raises, and a member declaring `exit_2_limbs` must name a limb for
every exit-2 path. **The fix reintroduces the defect in one of the six without this.** Stubbing the
shared reader into two members and running the real runner:

```
anchor_scan        declares_limbs=False  status=2
differential_scan  declares_limbs=True   UNCAUGHT ValueError: an exit-2 path names no exit-2 limb
```

`differential_scan` is the only run-directory reader among the three members with a vocabulary, and
its limbs name no *a run artifact could not be opened*. `render_scan` reads no text and
`voice_model_scan` reads a single model, so neither takes the shared reader.

**The limb constant lives beside the reader and is imported**, on `NOT_GRADED`'s precedent: the
reader raises the string and the member declares it, so a constant in each is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two copies with an
uncaught `ValueError` standing in for the second.

**All fourteen members adopting a vocabulary was declined.** ADR 0113 measured the pair as three of
fifteen, born in the #405 migration, and affirmed per-grader divergence; universal adoption is a
seam change with no ticket behind it.

### 6. `refusal_scan` gains no exit-2 vocabulary, ruled fresh rather than inherited

ADR 0114 ruling 4 answered *no* on the ground that *ruling 1 means it raises none, so the antecedent
is gone.* Ruling 2 restores that antecedent, so the question genuinely reopens.

The answer is still no. Its docstring's informal *2 means no worksheet refusal was scanned or the
input could not be read* is a **false** claim today -- the second limb exits 1 -- and ruling 2 makes
it **true**. What was #220's shape becomes an accurate but unheld docstring: one copy in prose and
no code copy to diverge from. Adopting a vocabulary to hold it is the seam change ADR 0114 ruling 4
refused, arriving by a different route into the same ticket.

### 7. `SourceError`'s docstring drops *tier-1 failure*, and the second live sense of *tier* gains a glossary entry

The reword is dictated by the glossary: **Unreadable source**'s `_Avoid_` row already names
`tier-1 failure`.

**Widening `test_glossary_collisions` to code prose was refused on measurement.** It would fire
immediately on `threshold_sheet`'s 62 occurrences of a sense the repository uses deliberately and
documents, and that module is *an inventory, never a gate*, so the fires would accumulate unruled.

**So the citation-resolution sense gains an entry with a distinction clause**, on `CONTEXT.md`'s own
`Section number` against `Section read` precedent -- *these are two senses of the word and neither
term is a narrowing of the other*. Rewording the one occurrence and leaving the sixty-two inverts
the priority, and leaves the second sense in exactly the condition that produced #843 decision 4.

## What this does not reach, declared rather than left to be found

**Whether the date correlation is a policy that drifted or a coincidence.** Ruling 3 leaves a module
landing after 2026-08-22 with a different answer from one landing before it, separated by a declared
reason and nothing else. ADR 0114 declined to read a cause into it and so does this; what changed is
that the split now has an address, so re-filing it is answerable rather than a re-derivation from
the same `grep`.

**The vocabulary's coverage under ruling 5.** It reaches *whoever already declared one*, a
population of three chosen by the #405 migration and by no rule. That is not a defect today and it
is the thing that will look arbitrary to whoever reads ruling 4's map.

**Ruling 1's enforcement.** Role is declared, not walked. A `read_text` serving a secondary role
that is written as a primary is caught by a reader and by nothing else.

**Ruling 7 does not make the detector see the second sense.** Its declared limit stands, and a
fourth sense arriving in code prose tomorrow is as invisible as the citation sense was this morning.
The entry gives the next author a word to reach for, which is what `_Avoid_` rows are for; it is not
detection.

**`aar_scan`'s residue.** It is the whole of the axis-1 crash population after ADR 0115 and it is
outside both tickets, being a deferral whose migration is
[#840](https://github.com/mshamblin5150-code/clinical-skills/issues/840). Ruling 3 says what it owes;
nothing here schedules it.
