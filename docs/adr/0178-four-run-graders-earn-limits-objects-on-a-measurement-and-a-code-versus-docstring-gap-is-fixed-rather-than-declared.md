# Four run graders earn limits objects on a measurement and a code-versus-docstring gap is fixed rather than declared

[#1038](https://github.com/mshamblin5150-code/clinical-skills/issues/1038) was filed out of
[#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867)'s grilling under
[ADR 0162](0162-render-scan-earns-its-limits-object-on-a-measurement-and-counts-exactly-one-image-per-page.md)
ruling 6. Four of the 17 `run_grader.MEMBERS` held no limits object under any recognized name and
stated their limits only in unbound prose: `anchor_scan`, `block_scan`, `filled_vitals_census` and
`specificity_scan`. The ticket applies ADR 0162's method to each (shapes built from the command's own
input chain, one link broken at a time, a stated negation, and one verdict per module) and inherits
[ADR 0125](0125-render-coverage-and-the-render-record-are-two-properties-and-each-artifact-wires-them-its-own-way.md)
ruling 2's refusal of an object added for symmetry.

Grilled 2026-09-11. The session began at `origin/main` `8c0437e`, where every measurement below was
taken, and was merged forward to `b24aada` before this record was written. That merge changed none of
the four modules, `run_grader.read_run_directory` or `tools/test_declared_limits.py`. **Eleven
questions were ruled by the clinician on that date**, one at a time. The closing summary, including
the conventions it applied without a question, was confirmed; the eleventh question re-put one line of
that summary after drafting showed it untrue of the fix it named. Nothing is built here; this is the
record the build reads.

## Measured before ruling

### How the shapes were built

One read-only agent per module built shapes in a temporary directory outside every checkout and drove
the real command over each, with a clean, a finding and a not-scanned control. Those reports are
claims. The grilling session then rebuilt every row a ruling below rests on with its own mutations of
committed fixtures (`fixtures/filled-anchor/notes/case-01.md` and `case-06.md`, and
`fixtures/filled-anchor/run-2/case-01.md` and `case-06.md`). Rows it rebuilt sit in the tables below;
counts attributed to "the agent" were not rebuilt.

In every rebuilt table the finding control was made the same way as the shapes, by changing one line,
so it cannot discriminate between them. **Each shape's twin is the discriminator**: it differs only in
the link the shape breaks, and prints what the shape would have printed had that link been read. The
driver scripts were throwaway. What re-derives a behavior entry afterwards is its control under
ruling 7.

### `block_scan`

The module docstring states F4 as a sentence reading, F5 to F7 as questions about an input the command
never sees, #127's aligned-continuation candidates, #297's label-line candidates, a hyphen or period
read in place of the middle dot, and F3's second limb matching race anywhere under
`FILLED·asserted`. The `CLAUDE.md` section states the first three and the exit-2 limb, and none of the
last three.

Rebuilt on `notes/case-01.md`; `VIOL` is `Primary Payment Method — not in the source.`, which F1
forbids as a GAPS entry.

| shape | exit | counts |
| --- | --- | --- |
| unchanged | 0 | carrying a tier block 1, F1 0 |
| `GAPS` + aligned spaces + `VIOL` added | 1 | F1 1 |
| the fenced tier block cut | 2 | carrying a tier block 0 |
| `GAPS` + aligned spaces + `1. ` + `VIOL` | 0 | F1 0 |
| `GAPS` + aligned spaces + `"Primary Payment Method" — not in the source.` | 0 | F1 0 |
| `#### GAPS` then `- ` + `VIOL` after the fence | 0 | F1 0 |
| `GAPS` + one space + `VIOL` | 0 | label-line candidates 1 |
| the race line replaced by `Race not supplied; see GAPS.` | 0 | F3 0 |
| the race line removed | 1 | F3 1 |
| the unchanged note beside the `VIOL` note with its block indented four spaces | 0 | notes read 2, carrying a tier block 1 |
| that indented note alone | 2 | carrying a tier block 0 |
| the unchanged note beside a copy with no tier block | 0 | notes read 2, carrying a tier block 1 |
| the unchanged note, with the `VIOL` note in `sub/` | 0 | notes read 1 |
| the unchanged note, with the `VIOL` note saved as `.txt` | 0 | notes read 1 |
| the `VIOL` note's directory passed as a second argument | 0 | notes read 1 |
| `FILLED·asserted` written `FILLEDÂ·asserted` | 1 | F3 1 |

**Under the negation, that the prose is complete, no clean row would carry an unnamed violation.** The
agent counted 17 clean violation shapes. The docstring's literal words name 2; read generously, 5
escape it: the list numeral, the quotation mark, the subfolder, the other extension and the second
argument. The `CLAUDE.md` section names 1 literally and misses 9 generously. The last three of the
five are the shared reader's and #1085's (ruling 9); the numeral and the quotation mark remain
`block_scan`'s own. Every row is readable by a person who opens the note.

The last row is a defect and not a limit: the docstring gives the hyphen and period reading because
*"a run that lost the middle dot to an encoding is a formatting matter and not one of these rows"*,
and a two-character garbled dot fails F3 on a note carrying race exactly where it belongs.

### `anchor_scan`

Both surfaces state that what the command cannot reach is the rest (docstring) or most
(`CLAUDE.md`) of ANCHOR, because a note is not in the run directory. Only the docstring carries the
entry-opening and pairing rule, the `NOT FOR ENTRY` rule and the `SOURCE` value rule; only
`CLAUDE.md` carries the listing's line format and the pre-#46 heading.

Rebuilt on `run-2/case-01.md`:

| shape | exit | counts |
| --- | --- | --- |
| unchanged | 0 | marked 3, listed 3 |
| the Z68.26 listing removed | 1 | marked, not listed 1 |
| that, with Z68.26's mark written `**SOURCE:** filled` | 0 | marked 2, listed 2 |
| Z68.26's `SOURCE:` written `NOTE:`, listing kept | 1 | listed, not marked 1 |
| that, with `### Adult BMI band` inserted above the listing | 0 | marked 2, listed 2 |
| the listing removed and restated as `Z68.26 - …` below the Accounting table row that names the block heading | 0 | marked 3, listed 3 |

The agent also drove, and the session did not rebuild:

- Z68.26's label written `**ICD-10**` with its listing turned to prose: exit 0. This is #1066's lead.
- A synthetic Z68.54 carrying BMI 23.0, age 17, male and the exact CDC sentence: exit 0, while
  `tools/cdc_percentile.py male 17 23.0 --age-years` gives Z68.52.
- A second worksheet whose every mark and listing is unreadable, beside a clean one: exit 0; alone,
  exit 2.

The agent counted 15 clean shapes. The docstring names 2 literally and misses 7 generously, 3 of them
this module's own (the bold mark, the subheading and the restated listing); `CLAUDE.md` names none
literally and misses 12 generously. Committed run-2 exits 1 under this command deliberately:
`tools/test_anchor_scan.py`'s `TheCommittedRunsFiguresArePinned` pins its two pre-#123 Z68.52 bands as
findings.

### `filled_vitals_census`

The docstring lists most of its reading limits: other height spellings, a key line it does not
recognize being invisible to parse and count, a period or semicolon interrupting a declaration, the
80-character window, the clause scope, a spelled sex, counts over notes rather than patients, and the
pain score as the loosest pattern. It states five vital classes counted and not graded. `CLAUDE.md`
shares the five classes, #204's unread-key refusal and the heads-a-line rule, and carries none of the
docstring's reading bullets.

Rebuilt:

| shape | exit | counts |
| --- | --- | --- |
| `notes/case-01.md` unchanged | 1 | filled height 1, naming no age and sex 1 |
| a column-0 `DERIVED at D2 the reading above stands.` inserted after its pressure line | 0 | filled height 0, naming no age and sex 0, filled pressure 1 |
| `notes/case-06.md` unchanged | 0 | filled pressure 1, not normal 0 |
| its pressure item written `BP 152/94 given, HR 88 filled.` | 0 | filled pressure 1, not normal 1 |
| the same with `given.` | 0 | filled pressure 0 |

The agent also drove: a shared body whose height is written in centimeters, exit 0 against a twin at 1
(#1066's first lead, reproduced on committed text as well); a key written `FILLED·asserted:` on a
violating note, exit 0 with `scanned 2 of 2` over three notes (#1066's second lead; `7 of 7` over
twelve committed notes); and a violating note in a subfolder or saved as `.txt`, exit 0.

The agent counted 23 clean shapes. The docstring misses 4 even generously: the early close, the
subfolder, the other extension and the `given` window; `CLAUDE.md` misses 16. After rulings 9 and 10
the early close is the one case outside the docstring that belongs to this module.

The `given` row is a defect. The docstring says *"A `given` anywhere in the span is therefore
rejected"*; `PRECEDING_GIVEN` reads only the twelve characters before the label. Two repairs were
swapped into `_declaration` and compared:

| input | unmodified | A: the window stops at the next vital's label | B: a `given` between value and `filled` rejects |
| --- | --- | --- | --- |
| every census figure over the twelve committed notes | baseline | unchanged | unchanged |
| `BP 152/94 given, HR 88 filled.` | filled pressure | none | none |
| `BP 152/94, HR 88 filled.` | filled pressure | none | filled pressure |
| `BP 138/86 filled, from the given pulse of 112.` | filled pressure | filled pressure | filled pressure |
| `BP 138/86 filled. HR 92 filled.` | filled pressure | filled pressure | filled pressure |

Of the 63 first declarations in the twelve committed blocks, none carries another vital's label or
the word `given` between its value and its `filled`, which is why neither repair moves a figure.

### `specificity_scan`

The docstring states that a substantive reason's truth is not tested, that the advisory does not fail
C5 because no string test separates the cases, the entry-opening and pairing rule, the
`NOT FOR ENTRY` exemption, and that a flag starting with neither keyword fails nothing. It never names
C2: `grep -c C2 tools/specificity_scan.py` prints 0. `CLAUDE.md` states that the advisory is not a
failure and that the advisory count rests on C2.

Rebuilt on `run-2/case-01.md`, with an entry added above `### Differential`:

| shape | exit | counts |
| --- | --- | --- |
| unchanged | 0 | for-entry codes read 13, flags at fault 0 |
| `ICD-10  J02.9  Acute pharyngitis, unspecified` with `SPECIFICITY: complete` | 1 | for-entry codes read 14, flags at fault 1 |
| the same entry as `- ICD-10  J02.9 …` with `- **SPECIFICITY:** complete` | 0 | for-entry codes read 13, flags at fault 0 |
| the same entry as the table row `\| ICD-10 \| J02.9 \| … \| complete \|` | 0 | for-entry codes read 13, flags at fault 0 |
| the plain entry with `SPECIFICITY: completed` | 0 | flags at fault 0 |
| the plain entry with `SPECIFICITY: complete.` | 1 | flags at fault 1 |

The docstring says a worksheet written another way *"reads here as having flagged nothing, which is a
floor on every count and **not** on the exit status"*. Since ADR 0170 ruling 10's build, the dashed
entry beside recognized ones exits 0, and the agent measured a worksheet written wholly that way
exiting 2, so the sentence is false in both directions. ADR 0170's rejected option said the next
unrecognized spelling *"is caught the same way"*; the remainder is computed over the entries `ENTRY`
recognizes, so a code line spelled another way is not. ADR 0170 carries a dated correction.

The agent also drove: a stock `complete - nothing more to add`, exit 0; a paraphrased descriptor
without `unspecified`, advisory 0 against its twin's 1; `SPECIFICITY: n/a`, exit 0; and a for-entry
code mismarked `NOT FOR ENTRY` with a bare flag, exit 0. It counted 21 clean shapes: the docstring
misses 10 generously and `CLAUDE.md` 16; 8 escape both, four of them this module's own.

Committed run-2 exits 2 under this command, with 10 codes unpaired: 4 in `case-03.md`, 2 in
`case-05.md`, 3 in `case-06.md` and 1 in `case-08.md`. That goes to #1104.

### The shared reader

`run_grader.read_run_directory` reads `sorted(directory.glob("*.md"))`, keeps files whose stem is not
`readme`, and decodes them as UTF-8 with replacement. Its whole docstring is *"Read a run directory's
Markdown artifacts in name order, excluding README."* `run_grader.DECLARED_LIMITS` holds grader-family
discovery and direct text-read classification, and neither covers this. The subfolder and `.txt`
shapes exit 0 in all four modules. `allow_extra_positionals` defaults to `True`, which drops a second
source; [#1085](https://github.com/mshamblin5150-code/clinical-skills/issues/1085) already owns it.

### Correct input that fails

Beyond the three defects above, the measurement reproduced graders failing correct worksheets and
notes: `anchor_scan` on a wrapped or extended CDC sentence, `recorded, not filled`, a subheading in the
step-4 block and a bold label that blames the entry above; `filled_vitals_census` on `36 y.o.`,
`age: 36` and a spelled-out age; `specificity_scan` on run-2's four worksheets and a wrapped reason; and
run-2's README and `assertions.md` claiming exit statuses the commands no longer return. Each is
tabled on #1104. A `block_scan` bullet list after an unfenced block was reported to fail F1 and
exited 0 on the session's rebuild, so it is unconfirmed and filed nowhere.

## Ruled 2026-09-11

### 1. `block_scan` earns `DECLARED_LIMITS`

A list numeral or a quotation mark opening a GAPS entry exits 0 on a real F1 violation and prints the
counts of a correct note, and neither surface names either shape on any reading. The ticket's rule is
that a clean shape outside the prose earns the object. The argument against, that a person reading the
note catches every shape, was weighed and did not carry.

### 2. `anchor_scan` earns `DECLARED_LIMITS`

A bold `SOURCE` mark, a subheading above the listing, and a listing restated below a mention of the
block heading each exit 0 with an anchor unlisted, and neither surface names them on any reading.

### 3. `filled_vitals_census` earns `DECLARED_LIMITS`

The early close exits 0 on a height that names no age and sex and is outside the docstring on any
reading. The docstring is otherwise close to complete; the object is earned on that one shape, on
`CLAUDE.md` missing most of the rest, and on the two surfaces already stating different limit sets.

### 4. `specificity_scan` earns `DECLARED_LIMITS`, and neither prose surface keeps a limit

A code line behind a list marker or written as a table row exits 0 with its bare flag unread, and
neither surface names it. The ticket asked which limit each surface keeps. Neither keeps one: the
docstring's limit paragraphs and `CLAUDE.md`'s C2 paragraph become entries, and both surfaces point at
the object.

### 5. What each object holds

- Every limit either prose surface states today, its reason kept in the surface's existing words,
  the docstring's first. A sentence that is not a **Declared limit** in `CONTEXT.md`'s sense stays
  prose.
- Every measured clean shape the prose missed, grouped into one entry per link it breaks.
- Nothing the shared reader owns (ruling 9), nothing #1085 owns, and no defect (rulings 10 and 11).
- Entries are `(subject, reason, run_grader.EvidenceDisposition)` triples, as in
  `render_scan.DECLARED_LIMITS`.

### 6. The entries

Subjects and dispositions are fixed here; reasons come from the surfaces under ruling 5, and a
builder whose control shows a subject untrue reports it rather than writing it.

`block_scan.DECLARED_LIMITS`:

- whether every `FLAG` names both the finding and what was not done with it (F4); declared reading.
- F5, F6 and F7, which turn on one case's age and sex, an input the command never sees; declared
  reading.
- the entry boundary: an aligned continuation line is a wrap, and one that would have opened a
  matching entry is a candidate outside the exit status (#127); behavior, controlled by an aligned
  continuation `VIOL` exiting 0 with one wrapped-line candidate.
- a label-like line that does not head a line (one space, a tab, `**GAPS:**`) opens no section and is
  only counted (#297); behavior, controlled by `GAPS` + one space + `VIOL` exiting 0 with one
  label-line candidate.
- which openings a row matches: a closed set of spellings anchored at the entry's start after markup
  is stripped, so a list numeral, quotation mark, negation or synonym opener, or a section under a
  Markdown heading, is neither graded nor a candidate; behavior, controlled by the numeral and
  `#### GAPS` shapes each exiting 0.
- F3's second limb matches race anywhere under `FILLED·asserted`, so an entry merely mentioning race
  satisfies it; behavior, controlled by `Race not supplied; see GAPS.` exiting 0.
- a note whose tier block is unreadable or absent, beside notes whose blocks read, is graded on
  nothing, F3's absence limb included; behavior, under ruling 8.
- a note whose `FILLED·asserted` key is not recognized is not graded on F3's absence limb; behavior,
  under ruling 10.

`anchor_scan.DECLARED_LIMITS`:

- the rest of ANCHOR: each such question compares a worksheet to a note, a note is not in the run
  directory, and a clean run says nothing about whether the right codes were marked; declared reading.
- a `NOT FOR ENTRY` entry is not a proposed code and is graded on nothing; behavior.
- an entry opens only on a line beginning `ICD-10`, `CPT` or `HCPCS`, so a `SOURCE` or `CONFIDENCE`
  line under any other code line pairs with the entry above it or with none; behavior, under ruling 8.
- a listing is `<code> - <value>` on its own line, and one in a table or prose is not read; behavior.
- only a line opening `SOURCE:` whose first value line says `filled` marks a code, so a bold label or
  another value leaves the code unmarked; behavior, controlled by `**SOURCE:** filled` with its
  listing removed exiting 0.
- the step-4 block ends at any `---` or Markdown heading line; behavior, controlled by the subheading
  shape exiting 0.
- any line naming the block heading opens collection, so a code-dash line below a mention of it is
  read as a listing; behavior, controlled by the restated-listing shape exiting 0.
- a pediatric band is taken from the `CONFIDENCE` sentence and never recomputed from the worksheet's
  BMI and age; behavior.
- coverage is per run, so a worksheet carrying no mark, listing or pediatric band beside worksheets
  that do adds nothing; behavior, under ruling 8.

`filled_vitals_census.DECLARED_LIMITS`:

- the five counted vital classes are counted and not graded, because the corpus supplies no even
  split; declared reading.
- a height is read only as feet-and-inches or bare inches and a weight only in pounds, so another
  spelling reads as no declaration; behavior, under ruling 8.
- a key line the rule does not recognize is invisible to the parse and to the count, so the coverage
  figure is a floor; behavior, under ruling 8.
- a declaration interrupted by a period or semicolon reads as absent; behavior.
- any column-0 tier word closes the block, which is the permissive end chosen on purpose; behavior,
  controlled by the column-0 `DERIVED` shape exiting 0.
- a height's clause runs to the next declaration read or the end of the block, so an age and sex in a
  later item satisfy it; behavior.
- a declaration's window stops at the next vital's label, so `BP 152/94, HR 88 filled.` declares no
  filled pressure; behavior, under ruling 10.
- whatever else the docstring's limits list states that is a limit under ruling 5.

`specificity_scan.DECLARED_LIMITS`:

- whether a substantive reason is true; declared reading.
- whether a `complete` on an unspecified descriptor names an exhausted axis, which no string test
  separates; declared reading.
- the substance test accepts any letter or digit after the keyword, so a stock phrase passes;
  behavior, controlled by `complete - nothing more to add` exiting 0.
- the advisory count reads the descriptor on the entry line alone and rests on C2: a paraphrase
  without the word counts 0, and so does a verbatim descriptor wrapped before it; behavior.
- an entry opens only on a line beginning `ICD-10`, `CPT` or `HCPCS`, so a code line behind a list
  marker, in bold or as a table row, beside recognized entries, is invisible with its flag, and the
  unread remainder cannot see it; behavior, under ruling 8.
- a flag pairs with the nearest entry above it, with no lower bound; behavior.
- a flag on a `NOT FOR ENTRY` entry is exempt, so a for-entry code mismarked is graded on nothing;
  behavior.
- a flag whose value starts with a word that is neither keyword fails nothing; behavior, controlled by
  `SPECIFICITY: n/a` exiting 0.

### 7. Each surface points once, each behavior entry has a control, and each no-limits entry leaves

- Each module docstring's limit prose and its `CLAUDE.md` section's limit prose become one sentence
  naming the object, asserted exactly once per surface, with
  `prose_bind.bind(<object>, surface, mode=NAMING)` returning nothing for each, as ADR 0162 ruling 4
  arranged for `render_scan`.
- Each module's test gains a partition test in
  `test_case_study_scan.EveryDeclaredLimitHasAnEvidenceDisposition`'s form.
- Each behavior entry has a control asserting today's result, so a change that closes the boundary
  fails the control and retires the entry in the same change.
- Each module's entry in `tools/test_declared_limits.NO_LIMITS` is removed in the same change.
- `specificity_scan`'s docstring and `CLAUDE.md` exit-2 lists gain ADR 0170 ruling 10's
  unread-remainder limb, and the docstring's *"not on the exit status"* sentence goes.

### 8. A partial read is an entry naming #1066 as the owner of its repair

A form that goes unread beside forms that are read is declared, with
[#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066) named in the entry as the
open owner and a control asserting today's result. The clinician ruled it for `block_scan`'s unreadable
tier block. The closing summary applied it to `anchor_scan`'s per-run coverage and its unrecognized
code labels, to `filled_vitals_census`'s two #1066 leads, and to `specificity_scan`'s unrecognized code
lines, which #1066 did not list and gains as a measured lead. Gating any of them here was declined:
it would decide #1066's family question inside one module.

### 9. The shared reader's blind spot is one entry in `run_grader.DECLARED_LIMITS`

The entry says which run-directory artifacts a member reads: `read_run_directory` opens only top-level
`*.md` files whose stem is not `readme`, so a subfolder, another extension or a file named README is
never read. It is behavior, with a control in `tools/test_run_grader.py` showing an artifact in `sub/`
and a `.txt` artifact unread. The four module objects do not repeat it. The dropped second positional
stays #1085's.

### 10. Three contradictions between code and docstring are fixed here

A place where a grader does the opposite of its own documentation is not a declared limit, as
`CONTEXT.md`'s **Declared limit** now says; declaring one would record the disagreement rather than a
boundary. ADR 0162's rejected option applied the same reasoning to `render_scan`'s comparator.

- **`filled_vitals_census`:** a declaration's window stops at the next vital's label, so a `filled`
  counts only for the nearest labeled value before it, and the docstring's *"anywhere in the span"*
  sentence is rewritten to the guard the code has plus this stop. Its controls: `BP 152/94 given, HR 88
  filled.` and `BP 152/94, HR 88 filled.` each declare no filled pressure, and
  `BP 138/86 filled, from the given pulse of 112.` declares one. Every figure pinned over the twelve
  committed notes stays as it is, which the comparison above measured.
- **`block_scan`:** a left-margin line shaped like `FILLED`…`asserted` that `LABEL` does not recognize
  is counted as a label-line candidate, and for that note F3's absence limb reports `not graded` rather
  than failing. The pattern is the builder's, and it must at least recognize the two-character
  `FILLEDÂ·asserted` and a replacement character in place of the dot. The docstring's formatting-matter
  sentence is rewritten to say so. Its control: `FILLEDÂ·asserted` on the unchanged note reports one
  label-line candidate and F3 not graded, and fails nothing.
- **`specificity_scan`:** a value whose first word is `complete` or `needs` with further letters
  welded on (`completed`, `completely`) is its own finding and exits 1, whatever follows. The
  neither-keyword rule is untouched for a genuinely different word such as `n/a`, and an empty value
  stays on that rule too. Its controls: `SPECIFICITY: completed` and
  `SPECIFICITY: completely specified — laterality documented` each exit 1, and `SPECIFICITY: n/a`
  exits 0.

### 11. The remaining defects go to #1104

Correct input that fails, and prose about run-2's exit statuses, go to one `grilling` ticket split by
grader: [#1104](https://github.com/mshamblin5150-code/clinical-skills/issues/1104). They do not bear
on whether an object is earned or on what it holds. Several turn on a reading the clinician has not
made, such as which age spellings name an age and whether `ALSO PROPOSED ABOVE` is a legitimate
differential marker.

## Rejected options

- **Prose as the honest home for any of the four.** Each has a clean shape outside its prose on every
  reading.
- **One verdict for all four.** The ticket forbids it, and each ruling above rests on its own module's
  shapes.
- **Only the measured shapes in each object, with the existing prose limits left in place.** That
  leaves two unbound copies beside each object, which is #867's shape.
- **The shared reader's entry in each module's object.** Four copies of one function's behavior is
  [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s drift, and every other
  member inherits the same reader.
- **Filing the shared reader separately.** Where it is declared decides what the four objects hold.
- **Gating `block_scan`'s partial read here.** It would decide #1066's family question in one module.
- **Reading a garbled `FILLED·asserted` key as the key.** It widens a matcher, which #1066 names as the
  repair not to make, and the next garbling may be a spelling it still misses.
- **Rejecting a `given` between a value and its `filled`, as the docstring says.** It leaves
  `BP 152/94, HR 88 filled.` counting a pressure the note never declared filled.
- **Leaving `completed` to the neither-keyword rule.** It stays exit 0, so a flag with no reason still
  passes the gate.
- **Failing every neither-keyword flag.** It overturns the extra-branch rule `CLAUDE.md` records as
  deliberate.
- **Declaring the three contradictions.** A declared limit records a boundary, not a disagreement
  between a module and its own documentation.
- **Fixing every defect in #1038, or filing the three contradictions with the rest.** The first
  enlarges the build with readings the clinician has not made; the second leaves entries that would
  have to be written in words the code contradicts.

## What this does not reach

**Whether a declared-reading entry stays true.** Only behavior entries have controls.

**The defects on #1104,** and the `block_scan` bullet-list report that did not reproduce.

**Whether every `run_grader` member must report an unread remainder.** That is #1066's.

**The dropped second positional.** That is #1085's.

**The other thirteen members.** Nothing here measures them.
