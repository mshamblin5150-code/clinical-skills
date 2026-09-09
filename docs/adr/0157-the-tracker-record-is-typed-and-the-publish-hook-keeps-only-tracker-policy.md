# The tracker record is typed and the publish hook keeps only tracker policy

Grilling of [#834](https://github.com/mshamblin5150-code/clinical-skills/issues/834), ruled by the
clinician on 2026-09-09. Seven rulings. The build is a separate session.

## What was measured before ruling, on 2026-09-09

Measured at `origin/main` `08499d6667a3e973ae290a280abbfab2b610581c`. `main` moved mid-session; the
branch was brought forward and **every figure below was re-derived at that base**. The one exception
is named where it appears: the redaction mutation table was taken at `0de8fc8`, and the intervening
commit touched only `authorize_issue_body`, which is not on the `analyze` path.

**Corrected 2026-09-09, hours after ratification, by this ticket's own sweep.** The sentence above
claimed every figure was re-derived at `08499d6`, and it was false for **five** of them. All five
were carried forward from `0de8fc8` without being re-measured, while `main` moved
underneath them:

| published | actual at `08499d6` |
| --- | --- |
| `implementation_map.GitHub.issues:284` | `:289` |
| `get_issue:331` | `:336` |
| `_hook_response:1393` | `:1409` |
| `handle:1538` | `:1554` |
| 46 of 83 zero-importer modules, 55% | **45 of 83**, 54% |

Nothing rests on any of them: every coordinate points at a claim that holds, and 45 makes the
majority argument no weaker than 46. Every other coordinate and importer count in this record was
re-derived and does hold. But the defect is [#928](https://github.com/mshamblin5150-code/clinical-skills/issues/928)'s exact subject, *a
coordinate copied forward through a pass that did not re-measure it*, arriving inside the record that
documents it and under a sentence asserting the opposite. **The re-derivation was scoped to the
figures the session had been thinking about**, which is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s generalization-from-open-files
one level up: a pass re-measures what it remembers measuring. The same sweep also found the
eight-member population unstated while ruling 6 makes that denominator a reported figure; the members
are named above now.

**The report is a wire format at three sites, not one.** #834's body names `_branch_rule` alone.
Two further sites read the same prose: `tracker_publish_hook.py:1224` matches
`"ancestry could not be verified"` to set `positive_unverified`, and `:1238` matches
`"citation path resolution NOT GRADED"` to decide whether the callee's whole report is appended to
the hook's. Rewording either sentence in `tracker_branch_scope` silently stops the hook declaring a
limit.

**`branch:scope` is not a fallback for an unforeseen tail.** Every reachable status-1 shape was put
through `grade` and then through `_branch_rule` — driven, not read:

| report shape | rule recovered |
| --- | --- |
| repo-relative Markdown link | `branch:repo-relative-link` |
| unresolved path, no near miss | `branch:unresolved-path` |
| self-declares completion | `branch:self-declares-completion` |
| `in flight` label | `branch:in-flight` |
| missing body while in flight | `branch:in-flight` |
| Branch state blockquote missing, not-on-`main` form | **`branch:scope`** |
| Branch state blockquote missing, rests-on-`main` form | **`branch:scope`** |
| positive Branch state refused, ancestry unverified | **`branch:scope`** |

Eight shapes onto six names, and the generic name carries three of them — two distinct defects with
different remedies. *Fix your blockquote marker* and *the commit you claim is not an ancestor of
`origin/main`* reach the agent under one rule name, and the rule name is what selects the posture:
`remote_rule = rule in ("branch:unresolved-path", "branch:near-miss")`. An ancestry verdict is
remote-dependent by definition and is structurally unable to join the remote-dependent posture group
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4's table defines. **No live posture defect was demonstrated** — when the fetch fails, `grade`
returns 0 for the ancestry case before the matcher sees it. What is demonstrated is that
`_branch_rule` cannot express the distinction if anyone wants it to.

**Those six names are declared nowhere.** No `ROWS`, no `KINDS`, no enumerating test; one test names
`branch:in-flight`. Every other grader in `tools/` declares its vocabulary.

**`event_name` is semantic, not serialization.** #834 reads the if/elif ladder as pure envelope
overhead. Driven, the event name alone flips verdicts:

| document | event | status |
| --- | --- | --- |
| completion body, no labels | `issues` | 0 |
| *same body* | `issue_comment` | 1 |
| `in flight` label, prose body | `issues` | 1 |
| *same* | `pull_request_target` | 0 |
| `in flight` label, `pull_request` key present | `issue_comment` | 0 |

So `container["pull_request"] = {}` at `:1204` is not *"planted purely so a membership test in the
callee will see it"* — it carries a semantic field in sentinel clothing, and deleting the plant is a
wrong repair. What the ladder encodes is two orthogonal axes: **container** (issue \| pull request)
× **surface** (the record's own body \| a comment on it \| a review on it). `grade` reads exactly six
values — body, url, number, labels, and those two axes. Everything else in the envelope is packaging.

**The callee already impersonates a webhook against itself.** `tracker_branch_scope.grade_text:395`
fabricates `{"issue": {"number": 0, "labels": []}, "comment": {...}}`. The fabrication is the
subsystem's idiom in two places, not one module's hack.

**The hook's own subject is a minority of its own body.** Classified by AST at this base — 1,611
lines, 1,261 in definitions:

| subject | lines | share |
| --- | ---: | ---: |
| generic shell reading — quote-aware splitting, command position, `$VAR` expansion, MSYS spellings, literal `cd` | 221 | 17.5% |
| `gh` route table and field extraction — `PUBLISH_ROUTES`, `INLINE_FLAGS`, `_record_number`, `_api_grade_route`, `extract` | 362 | 28.7% |
| CommonMark block reader — `ordinary_comment_prose:924` and the seven predicates under it | 148 | 11.7% |
| tracker policy, GraphQL readback, AAR gate, hook protocol | 530 | 42.0% |

#834's *"roughly half"* re-derives at 46.2% for rows 1 and 2 together, so the figure holds and its
line coordinates and 1,108-line module size are stale. **The subject claim does not hold across
both rows.** Across the 221 lines: `gh` 0, `issue` 0, `tracker` 0, `title` 0, `route` 0,
`Publication` 0. The 362 encode `PUBLISH_ROUTES`, which ADR 0083 ruling 2 ratified as belonging in a
tested module in `tools/`.

**The 148 CommonMark lines are generic including the one with a tracker name on it.** Across all
eight definitions the count of `tracker`, `verdict`, `comment`, `publish`, `gh`, `issue` and
`Publication` is **zero**; `ordinary_comment_prose` is the only tracker flavour and its body has
none. The actual policy is 15 lines at `:1134-1149` and stays in the hook either way. The seam is
in the wrong place by a countable margin: the hook reaches into `tracker_bodies` **six** times for
`prose_outside_code`, `QUOTE_PREFIX` and `LIST_PREFIX` to build the layer above them.

**A shell reader would have one importer, except it already has two.**
`aar_scan._successful_gh_call:589` finds the `gh` call in a Bash transcript with
`re.search(r"(?:^|[;&|]\s*)gh\s+", command)` — the leading fragment of
`tracker_publish_hook.RAW_PUBLISH_ROUTE`, hand-rolled a second time and **not quote-aware**, where
the hook's is. That divergence is **latent and undriven**, and is recorded as such. For contrast,
every existing member of that infrastructure class has real reuse: `console_codec` 49 non-test
importers, `repo_root` 20, `run_grader` 17, `git_paths` 6.

**`grader_conformance.for_module` demands six things; the tracker family satisfies at most two, in
different modules.** Across the eight members -- `tracker_scan`, `tracker_bodies`,
`tracker_branch_scope`, `tracker_publish_hook`, `tracker_readback`,
`tracker_merge_receipt`, `tracker_freshness` and `map_scan`, which is a tracker gate by
function rather than by name:

| requirement | modules that have it |
| --- | --- |
| `main` delegates to `run_grader.run` | 0 of 8 |
| `Finding` subclasses `run_grader.Finding` | 0 of 8 |
| `ROWS`/`KINDS` | 1 — `tracker_bodies` |
| `Scan` is a dataclass | 1 — `tracker_scan` |
| `format_report` | 2 |
| `--show` | 1 — `tracker_scan`, whose output is PHI |

The last row settles it. The probe asserts a **two-sided** property: `assertNotIn(MARKER, default)`
*and* `assertIn(MARKER, shown)`. Seven of eight have no `--show`, so the second limb is not merely
unsatisfied but unsatisfiable, and adopting `for_module` would mean building a reveal path on seven
modules whose contract is that they have none.

**Four of seven finding apertures can echo the publication's text with nothing failing.** Each
`Finding(...)` site in `analyze` was given a text-carrying field appended to its report line, and
all 5,078 tests were run per group. That report reaches `additionalContext` — `_hook_response:1393`
and `handle:1538` — so an echo publishes the text into the agent's transcript, and the PHI aperture
is one of the seven.

| aperture | tests that failed anywhere in the suite |
| --- | --- |
| `phi:*` | 2, both named, both deliberate |
| `branch:*` | 1, **incidental** — a test whose subject is the unreadable-body remedy |
| `body:c0-control-character` | 1, **incidental** — the fixture happened to carry the excluded word |
| `body:carriage-return-flanked` | 0 |
| `body:literal-newline-escape` | 0 |
| `body:doubled-path-separator` | 0 |
| `verdict:missing-discriminator` | 0 |

All five body and verdict apertures were live in one run, so a test guarding any silent one would
have failed beside the one that did. **#834's claim that *nothing* in the suite fails is false for
three of seven apertures and true for four**, and the sharper finding is that two of the three
catches are accidental. Taken at `0de8fc8`, per the note above.

**Two duplication claims in #834's *Measured* section do not survive, and one it does not make
does.** `tracker_scan.EVENT_RECORD_KEYS` and `tracker_bodies.EVENT_RECORD_KEYS` are equal
five-entry dicts at distinct addresses — one fact about GitHub's webhook schema held twice. The
three `_label` URL precedences are genuinely different: `html_url`→number; `html_url`→`url`→number,
documented as added because `gh issue view --json url` writes that key; and record-`html_url`→
container-`html_url`. And `implementation_map.GitHub.issues:289` and `get_issue:336` build
`{number, title, state, labels, assignees, body}` — more of #834's claimed record shape than any of
the eight parsers it names, in a module it never mentions.

**`tracker_freshness` is not orphaned and the hook is not discarding its split.** 45 of 83 non-test
modules in `tools/` — **54%** — have zero non-test importers, so that condition is the majority and
not evidence. Its consumer is a documented procedure: `CLAUDE.md` mandates it at two checkpoints of
every sweep and `docs/agents/issue-tracker.md` names it. The two commands ask different questions:
`refresh_default_branch:1294` runs `git fetch origin main` and returns `returncode == 0`, asking
*is the remote-tracking ref current enough to compare against*; `tracker_freshness` fetches into
`REMOTE_REF` and then asks *does `HEAD` contain `origin/main`*. A branch legitimately behind `main`
must still publish. **The real duplication is one module over**:
`tracker_branch_scope._main_ancestry:178` and `tracker_freshness` both implement tri-state
`merge-base --is-ancestor`, differing only in operand order, and `tracker_freshness.run_git` and
`git` are already public and consumed by nobody.

## Ruling 1. `Result` carries a verdict, the rule vocabulary is declared and walked, and `branch:scope` splits

`tracker_branch_scope.Result` gains a verdict carrying the rule identity **and** the two facts the
hook currently recovers from prose — whether ancestry was verified, whether the default-branch tree
was read. `report` becomes display-only: nothing outside the module reads its text, and all three
string matches go.

**A rule field alone was refused.** The argument for the field is that a rule identity should not be
recovered from prose; a field shipping the same lossy name the prose search produced removes the
coupling and keeps the defect the coupling caused. So `branch:scope` splits into
`branch:blockquote-missing` and `branch:ancestry-refused`, and the vocabulary becomes a module tuple
with a walk asserting every status-1 path is constructible from it. Without the walk a seventh
return arrives mapping to a generic name in silence, which is the only way this stays fixed.
`tools/test_git_paths.py:149` is the precedent: a shared seam plus an AST walk that stops anyone
re-implementing it.

The cost is one row in ADR 0083's posture table — the ancestry row that table already implies and
the code cannot currently express. **This is not a posture change**: the new names inherit exactly
today's postures until a separate decision moves one.

## Ruling 2. There is a `TrackerRecord`, it carries six values on two axes, and it sits beside the existing types

One type carrying exactly what `grade` reads — body, url, number, labels, **container** and
**surface** as two separate fields. Three adapters: the `gh` command line, the Actions event, the
GraphQL reply. `grade` gains a record-taking entry point; the if/elif ladder, the sentinel
`html_url` values at `:1157` and `:1176`, the `pull_request` plant at `:1204` and `grade_text`'s own
envelope all go.

**The two axes are load-bearing rather than tidy.** ADR 0083 ruling 1 records that a body-only check
reports clean on more than two thirds of what the published workflow fails, and names `grade_text` as
*"what a rebuild reaches for first because it exists and takes a string."* A record carrying text and
not the axes rebuilds a defect already ruled against, and the five driven verdict flips above are
what a text-only record cannot express.

**The maximal form was refused.** `tracker_scan.Record`, `tracker_bodies.Record` and `Publication`
keep their private axes and *hold* a `TrackerRecord` rather than being replaced by it. `is_file` is
the `phi-scan: synthetic` pragma question, `harvest` is which file it came from, and `source`,
`resolved_against` and `reconstructed_path` are lexer provenance. None is a property of a GitHub
record, and folding them in makes a bag whose fields are meaningful to one caller each —
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s rule, that a helper two
modules happen to have written the same way is not one that exists to be depended on.

## Ruling 3. The event key table shares and the three URL precedences do not

The two `EVENT_RECORD_KEYS` copies collapse into the one Actions-event adapter. Which JSON key holds
the record for a given event name is a fact about GitHub's webhook schema that neither module owns,
which is `repo_root`'s case exactly.

The three `_label` URL rules are left alone. They differ because their inputs differ, one of them
documents why, and forcing a share would forbid the divergence #253 says a copy exists to permit.
**Sharing the object is necessary and not sufficient**, per
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218): the collapse is proved by
driving both former call sites to the same verdict, not by an identity assertion.

## Ruling 4. Only the generic shell reader leaves, and converting `aar_scan` is what proves the seam

The 221 generic lines become a `tools/` module in `console_codec`/`repo_root`/`git_paths`'s class,
and `aar_scan._successful_gh_call` is converted to consume it — which makes it two real importers on
day one rather than one, and is what makes the extraction falsifiable. **If `aar_scan` cannot be
converted, the seam was the wrong shape.**

The 362-line `gh` half stays tracker-side as ruling 2's command-line adapter. Moving it would put
`PUBLISH_ROUTES` in a module whose stated subject is shell syntax, against ADR 0083 ruling 2.

On today's importer count alone, deferring was the defensible answer. It was not taken because
`aar_scan` already carries a hand-rolled copy of the leading rule that is narrower than the original
in a way nobody has measured. **Whether the two disagree in practice is undriven**, and the
conversion is what settles it.

Decision 3's justification also loses its citation:
[#745](https://github.com/mshamblin5150-code/clinical-skills/issues/745) is closed, and
[ADR 0137](0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md) is the
live record entirely about that same reading half.

## Ruling 5. The CommonMark reader moves to `tracker_bodies` and is renamed

All 148 lines move beside the base layer they already call, and `ordinary_comment_prose` is renamed
to something its body earns — it has no comment-specific logic. The hook goes from six
module-attribute reach-ins to one named import.

On consumer count this would have stayed put. It moves because the reach-in is ruling 4's
*"the seam is in the wrong place"* signal in a different currency, and it costs nothing while the
file is open.

**A `markdown_blocks.py` is the more principled destination and is declined here**, because it
re-homes `prose_outside_code` — a predicate `tracker_branch_scope:145` already imports — for a
benefit nobody has measured. It is named so a later ticket reopens it rather than re-deriving that
it was considered. **Seven non-test modules outside the tracker family also do Markdown block
reasoning and none was read**, so whether a fourth consumer exists is unmeasured and this ruling
does not claim there is none.

## Ruling 6. The tracker redaction walk is one-sided, per kind, and carries a denominator

The family gets its own walk rather than joining `for_module`, and the reason is stronger than shape:
its guarantee is one-sided where the kit's probe is two-sided.

Per member: a declared set of finding kinds, one fixture per kind that actually triggers it, a salted
marker driven in as the publication text, and the marker asserted absent from the default report. **A
declared kind with no triggering fixture fails the walk rather than passing silently**, and the walk
reports its denominator and unread remainder every run. That last clause is the extractor-coverage
rule: a probe that cannot recognize a kind cannot count it unread, and *four of seven apertures
silent* is what a coverage-free probe produces.

**An AST walk over `Finding(...)` construction was refused.** It would have caught the exact mutation
run here and is blind to the likelier arrival — a report line interpolating the text without going
through `Finding` — and `analyze` already interpolates `branch.report` into its lines at `:1239`, so
that shape is live in the module today.

Ruling 1's declared branch-rule vocabulary is this walk's first member and `tracker_bodies` already
has `ROWS`/`KINDS`, so the population is two-thirds declared before this ruling spends anything.
**`tracker_scan` stays outside and keeps a named test**: it is the one member with a `--show` and the
one whose output is PHI by contract, a genuinely two-sided property that a one-sided walk would
assert something false about.

## Ruling 7. `tracker_freshness` keeps its standing, the ancestry primitive is shared, and the hook must not call the gate

Procedure-invoked commands are a legitimate class here and `tracker_freshness` is one. The bool the
hook keeps is the complete answer to a narrower question, not a discarded split —
[#744](https://github.com/mshamblin5150-code/clinical-skills/issues/744) is closed and that split
exists.

**The hook calling the gate is refused by name.** A branch legitimately behind `main` must still
publish, so reading `STALE` into the publish path would refuse or degrade a publication for a reason
with nothing to do with branch-scope grading. This is recorded so the next session finds the answer
rather than re-deriving the premise.

What is shared is the tri-state `merge-base --is-ancestor` predicate, consumed by both
`_main_ancestry` and `tracker_freshness`. **The fetches stay separate** — different refspecs for
different purposes, and forcing them together is the mistake #834 makes one level down. Ruling 1's
new `branch:ancestry-refused` now depends on that tri-state being right in one place rather than two.

## What this record does not settle

**Whether a plain `git fetch origin main` reliably updates `refs/remotes/origin/main`.** The gate
fetches with an explicit refspec precisely so it trusts no cached ref; the hook does not. If the
plain form does not, `_main_ancestry` compares against a stale ref while `remote_fresh` is `True`,
which would be a live hole in ADR 0105's mechanism. **Undriven**, decided by an experiment rather
than by reading, and its own ticket.

**Whether `aar_scan`'s non-quote-aware `gh` matcher disagrees with the hook's in practice.**
Undriven. Ruling 4's conversion settles it.

**Whether any module outside the tracker family is a fourth consumer of the CommonMark layer.**
Seven do Markdown block reasoning and none was read.

**The eight-parser and three-kind-notion censuses.** `implementation_map` alone puts the first
figure at a floor rather than a count, and it is out of scope here by ruling 2's boundary.

**Any posture.** ADR 0083 rules what refuses and what advises, per trigger. Ruling 1 adds names and
inherits the postures those names had.
