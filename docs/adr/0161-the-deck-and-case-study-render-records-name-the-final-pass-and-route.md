# The deck and case study render records name the final pass and route

[#866](https://github.com/mshamblin5150-code/clinical-skills/issues/866) was filed out of
[#864](https://github.com/mshamblin5150-code/clinical-skills/issues/864)'s grilling, 2026-09-03, and
declared rather than fixed there:
[ADR 0125](0125-render-coverage-and-the-render-record-are-two-properties-and-each-artifact-wires-them-its-own-way.md)
ruling 3 found that skipping `render_scan` produces no signal in either skill that runs it, and that
the deck has render coverage with no record half at all.
[ADR 0142](0142-the-word-export-route-is-shared-by-stem-and-a-reached-bound-ends-it.md) ruling 2 then
handed it a second question: which route produced a pass.

Grilled 2026-09-10. The session began at `origin/main` `ffbe5c6` and was fast-forwarded to `6b12a85`
mid-session to pick up the `peer-critique` skill, then to `8e3744e`, which carried ADR 0160 ruling 9
and its conforming edits. **Fifteen questions were ruled by the clinician on that date.** Twelve were
asked before this record was drafted; two more — the field predicate and the conflict with
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
— were raised by an adversarial check of the draft, and a fifteenth, on a repeated field, by a probe
run after the record was first committed. All three amended it. They are grouped into the eleven
rulings below. Nothing is built here; this is the record the build reads. A figure counted under
`scratch/` below is a dated floor that nothing committed re-derives.

## Measured before ruling

### The ticket's substance re-derives, and two completion conditions are read by nothing

`tools/checks_ledger.py` names `render_scan` nowhere, and its `FIELD` pattern reads `VERDICT` and
`FINDINGS` only. `deck_scan.ROWS` holds five rows and no render row, `deck_scan` takes no
`--submission`, and it declares no `EXPECTED_COMPLETION_CHECKS`. So no completion grader joins
`skills/course-assignment/SKILL.md` step 6's conditions, and two of them — the visual comparison and
`the after-action review: clean` — are read by nothing at all, although `aar_scan.SCOPED_SKILLS`
names `course-assignment`.

### The completion-grader test reads a hand-typed list, and a second skill passed it mid-session

`test_aar_scan.EveryScopedCompletionGraderExpectsTheReview` asserts the review row over six modules
typed into the test, so `course-assignment` having no grader fails nothing. While this session ran,
`peer-critique` joined `SCOPED_SKILLS` with `peer_critique_scan` declaring the row correctly, and the
list was not updated. A correct arrival went unseen by the same list that
[#942](https://github.com/mshamblin5150-code/clinical-skills/issues/942)'s sweep had found letting an
incorrect one through two days earlier.

### Both producers compute the route and keep it nowhere

`tools/deck_render.py` prints `SOURCE: powerpoint-pdf` or `SOURCE: clinician`, and
`tools/case_study_render.py` prints `word-pdf`, `word-xps` or `clinician`. Neither writes the value to
any file.

### `checks_ledger` silently absorbs any other field line

Driven on a synthetic checks file carrying every expected check, with `SOURCE: word-pdf` placed three
ways on `the rendered document`:

| placement | parsed as | exit |
| --- | --- | --- |
| above `VERDICT` | dropped | 0 |
| between `VERDICT` and `FINDINGS` | `VERDICT: clean SOURCE: word-pdf`, still a clean verdict | 0 |
| below `FINDINGS` | appended to `FINDINGS` | 0 |

`read_records` appends any line that is not a recognized field to the field above it, so this holds
for every name and not only `SOURCE`. Its `FIELD` pattern is case-insensitive, so `verdict:` reads as a
field and `source:` would be absorbed like `SOURCE:`.

A repeated known field is worse, because `read_records` replaces the earlier value. Driven after this
record was first committed: a record whose substantiated `FINDINGS` is followed by `FINDINGS: short`
keeps `short`, and a findings sentence wrapped onto a line opening `findings:` keeps only the words
after it. Both grade clean.

No field-shaped line other than `VERDICT` or `FINDINGS` appears in the three worked check records in
`skills/practicum-case-study/SKILL.md` or in either retained case-study checks file, so a finding on a
misplaced known field costs nothing measured.

### The producers already enforce what `render_scan` grades, on a pass nobody touched

`deck_render.render` raises when the exported page count differs from the slide count, and retains a
pass only after `render_pass.images_cover_exported_pages` holds and the build returns.
`case_study_render.render` applies the same coverage check before `render_pass.retain_staged_pass`
keeps anything. A pass written that way and left alone grades clean under `render_scan`. What only
`render_scan` reaches is a pass the producer did not write, or one altered after retention — an image
replaced or deleted, a second export added — and a missing PDF engine at grading time, which is its
exit 2 whatever the pass holds.

### An in-flight deck run holds many passes and no record

The live [#823](https://github.com/mshamblin5150-code/clinical-skills/issues/823) deck run held 27
retained passes on 2026-09-10 and no render record; the two retained case-study runs held 10 between
them. A rule requiring a record for every pass would demand, beyond the final pass's record the run
must write anyway, 26 records reconstructed for passes nobody recorded.

### A missing PDF engine failed the post's record row, and that posture is ruled elsewhere

[#837](https://github.com/mshamblin5150-code/clinical-skills/issues/837)'s tracker sweep, 2026-09-10,
recorded on #866 that blocking the engine import turns clean fixtures in
`test_discussion_post_scan.CanvasSubmissionRows` into `rendered-pages` findings, because
`discussion_post_scan` appends *"PyMuPDF is unavailable"* to a pass's detail.
[ADR 0160](0160-the-pdf-engine-is-reached-through-one-seam-the-page-questions-are-four-and-the-availability-verdict-is-the-caller-role.md)
ruling 9, ruled the same day, makes that row report `not graded` at exit 2 instead. It bears here only
because no row ruled below opens a PDF or decodes an image, so a missing engine can neither fail one
nor leave one ungraded.

### ADR 0098 had already refused the case study's new fields

Found by the adversarial check of this record's first draft, after the case-study fields were ruled.
ADR 0098 ruling 2 rules that `the rendered document` record *"keeps `VERDICT` and `FINDINGS` and gains
nothing"*: `PAGES:` because the denominator is on disk, `SOURCE:` because *"the kept file is that —
`.pdf` or `.xps` by extension"*, and it refuses extending a grammar thirteen rows share for one row.
Its ruling 3 refuses `checks_ledger` for counting a sibling directory, *"a filesystem contract it has
never had."* That record's uniformity objection is the one ADR 0142 ruling 2 attributed, wrongly, to
`checks_ledger`'s docstring.

Two of its premises no longer hold. ADR 0142 found a bounded-route pass and a hand-exported pass
indistinguishable, and both are `.pdf`, so the extension does not name the route. And `checks_ledger`
already reads beyond its argument: at `--submission`, `aar_scan.completion_gate` reads the review
record in the run directory. Its objection to a self-reported page count still holds.

## Ruled 2026-09-10

### 1. The deck gets a render record, graded by `deck_scan` only at the terminal run

The record is written to the run's `rendered.md`, by the orchestrator from the non-authoring visual
reader's result, the way `adversarial.md` is written. `deck_scan` grades it when invoked with
`--submission`; without that flag the terminal requirements print `not graded`.

**No record was refused** because `skills/course-assignment/SKILL.md` step 5 already requires the
comparison and step 6 already lists it as a completion condition; the record gives work the run must
do a place to be written. **A checks ledger for `course-assignment` was refused**: it is the
two-command arrangement ADR 0125 measured as the weaker one, and a larger build.

**ADR 0124 ruling 4 is answered rather than routed around.** Its timing objection was a row that fails
at `skills/course-assignment/SKILL.md` step 4, before the render exists; a row graded only at
`--submission` cannot. This is `aar_scan.completion_gate`'s shape, already shipped in every other
scoped skill's completion grader.

### 2. #866 widens to give `course-assignment` its completion grader, and stays one ticket

`deck_scan` gains `--submission`, declares `EXPECTED_COMPLETION_CHECKS = (aar_scan.EXPECTED_ROW,)`,
and calls `completion_gate`, in the same build as the render record. The flag without the review row
would make `deck_scan` a completion grader that skips the review, and the review row cannot exist
without the flag.

**Filing it separately was refused** because the two cannot ship apart correctly. The ticket's own
decision 3 — whether its halves are one ticket — is answered by the ruling above leaving them joined.

### 3. The deck's row joins the record to the slide count and the pass's file list, and opens no export

A record reads:

```text
## RENDERED: <course>-<module>-course-assignment-<date>.pptx
PASS: 27
SLIDES: 12 of 12 read
SOURCE: powerpoint-pdf
UNSEEN: none
READ: every pass-27 slide image against the deck and bar.md
VERDICT: clean - no clipping, overflow, overlap or uncaptioned conceptual image on any slide
```

At `--submission` the row takes the record naming the highest retained pass — which pass that must be,
and what happens when there is none, is the next ruling — and requires that it names the submitted
deck; that its `m` equals the deck's slide count, which `deck_scan` already counts for `slide-count`;
that its `n` equals the PNG files in that pass; that `n` equals `m`; that `UNSEEN` is `none`; and that
its verdict is a substantiated `clean -`. Passes are read through `render_pass.read_passes`. The run's
`render/` is new to `deck_scan`, which reads nothing there today; the row lists that directory's files
and opens none of them.

**It opens no export and decodes no image**, so `deck_scan` gains no PyMuPDF dependency, and the
export's page count and image readability stay `render_scan`'s. **The post's full weld was refused**
for exactly that reason, and **a shape-only row was refused** because it passes a record claiming
more slides than its pass holds.

**The overlap with coverage is stated rather than denied.** Comparing the record's count with the
slide count and the PNG files is a coverage-shaped comparison made from the record's side. It was
accepted because a reader's count must be checked against something, and these files are all the row
can read without becoming a second coverage grader.

**The deck keeps its count where the case study's record does not.** The deck states its own slide
count, so `SLIDES` is checked against a number the reader did not write, and it catches a pass rendered
from an earlier version of the deck whose slide count has since changed. A `.docx` states no page
count, so a case-study `PAGES` could be checked only against the images it describes, which is the
self-reported count ADR 0098 refused and ruling 7 keeps refused.

### 4. Only the final pass must carry a record, and a run with no pass fails

Each record names its pass with `PASS: N`. The row requires a record naming the highest retained
pass. An earlier record, if present, must name a pass that exists and the submitted deck; a pass with
no record is counted, reported, and never graded.

**A run with no retained pass at `--submission` fails the row as a finding, not as a coverage limb.**
What the row grades is the run's obligation to have rendered, and an empty `render/` is that obligation
unmet — the skipped render the first ruling exists to catch — rather than evidence the grader could not
read. This is the empty-population question
[#922](https://github.com/mshamblin5150-code/clinical-skills/issues/922) asks of `deck_scan`, answered
for this row only; the case study's row takes the same answer.

**One record per retained pass was refused**, amending the form first put to the clinician. ADR 0124
ruling 1 found that an earlier pass carries no evidentiary obligation, the case study's row checks
only its final pass, and the in-flight deck run above would otherwise need records reconstructed for
passes nobody recorded — exactly the unsubstantiated record this ticket exists to catch.
**Grandfathering older runs was refused**: it needs a date cutoff and leaves the live run on the weaker
arrangement.

### 5. The deck's record declares its route, and nothing proves it

`SOURCE` is `powerpoint-pdf` or `clinician`, the two values `deck_render.py` prints, and any other
value is a finding. The value is the run naming its route, which #803's grilling, commenting on #866
on 2026-09-07, found to be the post's existing posture rather than an invented proof.

**Keeping the route in the pass directory was refused**: it changes what a render pass holds, the
passes already retained lack it, ADR 0124 ruling 3 leaves the files inside a pass to its producer
behind one shared shape, and it approaches the ticket's prohibition on inventing a mechanism to prove a
command ran while still proving nothing. **Not recording it was refused**: it discards a value the
producer already computes, and with it what ADR 0087 ruling 7 cares about — whether a run fell back to
the clinician's export.

### 6. The case study's record gains `SOURCE` and `PASS`, and a misplaced known field is a finding

On `the rendered document` only, `checks_ledger` recognizes `SOURCE` — `word-pdf`, `word-xps` or
`clinician` — and `PASS`, a positive integer, beside `VERDICT` and `FINDINGS`. A clean record on that
check must carry both.

```text
## CHECK: the rendered document
VERDICT: clean
SOURCE: word-pdf
PASS: 10
FINDINGS: compared all 14 pass-10 page images with the Markdown; margins, page numbers and reference hang intact
```

**A line that opens, in any case, with a known field name on a row that does not take it is a
finding.** The known names are `VERDICT`, `FINDINGS`, `SOURCE` and `PASS`, and the two names
ADR 0087 used and ADR 0098 retired, `PAGES` and `UNSEEN`. So `SOURCE:` under `differential ordering`,
`source:` anywhere it is not taken, and `PAGES:` on any row are findings, while `ROS:`, `MDM:` or
`General:` wrapped into findings prose never are. A misspelled `SOUCRE:` on `the rendered document` is
still caught, because a clean record without `SOURCE` fails.

**So is a known field name that opens more than one line in the same record**, on any row. Today the
later line silently replaces the earlier value, which can shrink a substantiated clean to a stub that
still passes. **The cost of both findings is stated, not denied**: a findings sentence wrapped onto a
line that happens to open with one of the six names — `Source:`, `Pass:`, `Findings:` — fires. Today
that same line is silently misfiled or truncates the finding, so each finding replaces a silent loss
with a visible one. **Declaring the overwrite was refused**: once `the rendered document` takes
`SOURCE` and `PASS`, a second `SOURCE:` line there would silently replace the first on the one row
these fields are added to.

**This supersedes ADR 0098 ruling 2 in part, for these two fields on this one check.** Its reason for
retiring `SOURCE` rested on the extension naming the route, which ADR 0142 found false. `PASS` answers
a failure that record did not weigh: #1020 records visual reads filed against a superseded pass and
against an earlier pass while later ones existed. **`PAGES` stays retired on ADR 0098's own ground**:
it is a self-reported count beside the countable one, and with `PASS` it answers nothing further.

**Naming the route inside `FINDINGS` was refused**: it needs a keyword picked out of free text, which
is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s prefix-read-as-a-word
hole. **Leaving the route unrecorded was refused**: the case study would be the one artifact of three
whose record cannot name it. **Any all-caps name as the finding was refused**: it fires on clinical
abbreviations wrapped onto a new line, and a warning that fires on correct prose is one readers learn
to skip; restricting it to unindented lines rests on an indentation nothing requires. **The finding
belongs to this ruling rather than to a separate ticket** because a `SOURCE` line the grader does not
recognize is absorbed in silence today — in one placement, into the verdict itself — so the field
cannot be built correctly without it.

### 7. The case study's terminal run requires `PASS` to name the highest retained pass

At `--submission`, `checks_ledger` lists `render/` in the directory it already treats as the run — the
checks file's parent, where `completion_gate` reads the review — and requires a retained pass to exist
and a clean `the rendered document` to name the highest one in `PASS`. A run with no retained pass
fails as a finding, as the deck's does. It opens no file in `render/`.

**This supersedes ADR 0098 ruling 3 in part: `checks_ledger` gains a directory listing.** That record
refused the grader for *counting* a sibling directory; the count stays `render_scan`'s, and this row
only asks which pass is highest. `checks_ledger` already reads past its argument through
`completion_gate`.

**It settles #1020's decision 2 for both render records**, the case study here and the deck in
ruling 4. A repair rarely changes pagination, so a check on counts alone would pass a verdict against pass 8
whenever pass 10 has the same number of pages; naming the pass does not. **#1020's decisions 1 and 3,
binding a pass and a check record to the document's bytes, were left there**: they concern whether a
pass shows the submitted document at all, a different root that needs a producer change.

**Existence alone was refused**: it passes a verdict filed against any retained pass. **Declaring it
was refused**: the case study would stay the weaker arrangement while the deck no longer is.

### 8. A skipped `render_scan` is declared, for both artifacts

`deck_scan.DECLARED_LIMITS` and `checks_ledger.DECLARED_LIMITS` each gain a limit: the render record
row reads neither the export nor the images' content, and nothing notices that `render_scan` was not
run. On a pass the producer wrote and nobody touched, the producer has already enforced what
`render_scan` grades; the residue is a pass the producer did not write, one altered after retention,
and a grading machine missing the PDF engine. Both skills keep running `render_scan`. The route being
declared rather than proven is stated as a limit in the same two objects.

**Grading the export and images inside `deck_scan` was refused** as a reversal of the no-engine join
above. **A marker written by `render_scan` was refused**: the ticket prohibits it, it is trivially
forged, and it proves one run of the command rather than a run against the final pass. **Dropping
`render_scan` from the deck skill was refused**: nothing would then check a hand-placed or altered
pass.

**What would reverse this is one fact.** If hand-placed or edited passes become normal work, grading
the export at the terminal run is the option to revisit. This is a choice with its reason written
down, not a finding that the gap cannot be closed.

### 9. Format is checked on every invocation; the requirement and the joins wait for `--submission`

Whenever a record is present, its format is graded: `SOURCE` within its values, `PASS` a positive
integer, `SLIDES` well formed on the deck, a substantiated verdict, a clean case-study
`the rendered document` carrying `SOURCE` and `PASS`, and the known-field finding. Only at
`--submission` is a record required, a pass required to exist, the record joined to the deck and the
pass files, and the final pass required.

**Everything at `--submission` was refused**: a misspelled `SOURCE` would ride through every
`skills/practicum-case-study/SKILL.md` step 9 run and fail at the most expensive moment. **Everything
always was refused**: `skills/course-assignment/SKILL.md` requires clean final scans in step 6 after
the repairs of step 5, and nothing orders a `deck_scan` run after the last re-render, so a join checked
on every invocation would fail a correct run that precedes it — ADR 0124 ruling 4's timing objection
again. Every field is written by one reader at one moment after the render, so a format check never
fails a correct run; only the join can go stale between runs.

### 10. `aar_scan.COMPLETION_GRADERS` pairs every scoped skill with its grader

`aar_scan` gains a mapping from each skill in `SCOPED_SKILLS` to its completion grader's module name.
The test asserts that the mapping's keys equal `SCOPED_SKILLS`, that each named module declares
`EXPECTED_COMPLETION_CHECKS == (aar_scan.EXPECTED_ROW,)`, and that each skill's `SKILL.md` contains its
module's name and the `--submission` flag — a file-level search, not a parse of a command line. On the
tree this record was ruled against it fails naming `course-assignment`; after the build it holds eight
pairs, `peer-critique` to `peer_critique_scan` and `course-assignment` to `deck_scan` among them.

**Reading the pairing from a command line in skill prose was refused**: of the seven skills that write
a terminal call today, three write it inside a sentence rather than as a fenced command —
discussion-post with `...` elided, discussion-reply, and peer-critique — and the
[extractor-coverage rule](../../CLAUDE.md#extractor-coverage) forbids a matcher that turns a partial
read into a clean one. **Collecting graders from `tools/` was refused**: it finds only graders that
exist, so it cannot see the defect it is for.

### 11. Three earlier records are superseded in part or corrected

- **ADR 0124 ruling 4's *"`deck_scan` gains no render row"* is superseded for the one terminal record
  row above and nothing else.** The refusal of a coverage row that reads the retained export stands,
  as does the declared placement divergence.
- **ADR 0098 ruling 2 is superseded for `SOURCE` and `PASS` on `the rendered document`, and its
  ruling 3 for a directory listing at `--submission`.** Its other rulings, and `PAGES`'s retirement,
  stand.
- **ADR 0142 ruling 2's clause attributing a uniformity argument to `checks_ledger`'s docstring is
  corrected in place** under
  [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md):
  the argument is ADR 0098 ruling 2's. Its decision is untouched, and this record answers the question
  it handed on.

ADR 0124, ADR 0125 and ADR 0098 each carry a dated pointer, in the form ADR 0033 carries for
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md).

**No supersession was refused**: a reader who opens only ADR 0124 or ADR 0098 would meet an unqualified
refusal and refuse this build. **Full supersession was refused**: nothing here ruled on a coverage row
that reads the export, on a self-reported page count, or on `checks_ledger` counting files.

`CONTEXT.md`'s **Render record** gains the declared route. No module is named there, on ADR 0125
ruling 2's precedent.

## What this does not reach

**Whether the retained images are the pages a reader read.** Unchanged from ADR 0098, whose ruling 3
keeps the two claims apart and whose own *What this does not reach* declares it. A record joined to
the files is still a reader's claim.

**Which route actually produced a pass.** The route is declared. A clinician export placed by hand and
labeled `powerpoint-pdf` passes both rows.

**A pass the producer did not write or that was altered after retention**, for either artifact, unless
`render_scan` is run. That is the declared limit above.

**Readings of earlier passes.** A pass without a record is reported and never graded.

**Whether a pass shows the submitted document.** Both records name a pass and the deck record names a
file, and neither binds either to the document's bytes. A pass rendered from a document since replaced
still passes both rows, unless the deck's slide count changed. That is #1020's decisions 1 and 3.

**Whether `--submission` means the run really is at its terminal step.** Both rows take the flag as
the terminal moment, as every completion grader does.
[#1015](https://github.com/mshamblin5150-code/clinical-skills/issues/1015) records that `aar_scan`
grades a review taken before submission as terminal; this record carries that assumption into one more
grader and does not repair it.

**The post.** Its `rendered-pages` row, its `--html` gate, and its behavior without a PDF engine are
unchanged here; the last belongs to ADR 0160 ruling 9 and #837.

**`peer-critique`.** It keeps no render pass, so by `CONTEXT.md`'s definition it has no render record
to lack. It enters this record only through the completion-grader pairing.

**`deck_scan`'s coverage limb and `render_scan`'s limits object.** #922 is answered here only for the
render record row, and [#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867) is
untouched.
