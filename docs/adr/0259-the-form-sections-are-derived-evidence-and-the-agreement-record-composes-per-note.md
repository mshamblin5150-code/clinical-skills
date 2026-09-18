# The form sections are derived evidence and the agreement record composes per note

Ticket [#1356](https://github.com/mshamblin5150-code/clinical-skills/issues/1356) was filed after the
2026-09-17 entry of six unsubmitted NUR 5144 shifts into Medatrax, where two throwaway scripts each
did work no committed command reaches. The clinician ruled that both belonged in `tools/` and left
the shape open: the command names, whether the two are one module or two, whether the sections
deriver refuses or merely reports when the stored copy differs, and whether the agreement
split-and-merge sits beside `anchor_scan` or stands alone. He ruled all of it in a grilling on
2026-09-17.

## Measured before ruling

Every figure below was taken during the grilling, over the committed fixtures and the account's own
`scratch/runs/` tree. The `scratch/` half is not re-derivable from anything committed, so it is
dated here and nothing downstream rests on it.

### The staleness the ticket reports is a floor

The ticket reports three stale notes against 44 untouched ones. Rebuilding the four sections from
each `entry-copies/note-N.md` and comparing with the stored `private/form-sections/note-N.json`
across all seven shifts: 64 notes, 48 byte-identical, **16 differing**. Every one of the 16 differs
in `A`; 11 of those also differ in `P`; **none differs in `S` or `O`**. That is where ADR 0254's Plan
relabeling and welded-clause removal land, so the divergences are that ADR arriving after the
sections had been pulled rather than an independent defect.

### The heading population is wider than the ticket's two forms

| | `S:` | `## S` | `## S:` | `P:` | `## P:` |
| --- | ---: | ---: | ---: | ---: | ---: |
| live Entry copies | 47 | 17 | 0 | 47 | 17 |
| committed fixture notes | 13 | 0 | 15 | 13 | 15 |

The ticket names a bare `S:` and a `## S` with no colon. Both corpora also write `## P:` **with** a
colon, and the committed fixtures write `## S:` with one where the live notes do not. So the colon is
independently optional per letter, and a reader keyed on either dialect returns four sections for one
corpus and three for the other.

### The Plan terminator population divides by corpus

Over the 64 live Entry copies the Plan always ends at `Coding worksheet`, bare in 47 and
`##`-prefixed in 17. Over the 28 committed fixture notes it never does: it ends at a `---` rule
followed by `## Medatrax entry`, `## Medatrax entry block`, `## Medatrax entry fields`, an
em-dash-suffixed `## Medatrax entry` variant, `## Tier block`, or a bare fence opening an unheaded
tier block, and one note carries no rule at all. The ticket's own list re-derives only once both
corpora are read; each corpus alone is a partial account of it.

### Every note has a preamble, and no note's Plan reaches end of file

Across all 92 committed and live notes, every one carries content before its `S` heading — up to 16
lines in the fixtures and 5 live — and not one carries a Plan that runs to the end of the file. Every
note has a tail.

### Five non-ASCII characters reach the pasted boxes, and the ticket names one

Scoped to the four sections that are actually typed into the portal, across the 64 live Entry copies:

| character | occurrences | notes |
| --- | ---: | ---: |
| `–` en dash | 567 | 28 |
| `∴` therefore | 64 | 64 |
| `µ` micro sign | 52 | 23 |
| `—` em dash | 14 | 14 |
| `²` superscript two | 2 | 2 |

The middle dot appears 4,016 times in those files and never inside a pasted section, because it is
all `FILLED·asserted` in the tier block; `≥` likewise stays outside. Only `∴` has a measured portal
verdict.

### The ticket's test instruction cannot run as written

`entry_copy.derive()` refuses **all 28** committed fixture notes, every one for `Plan labels
invalid`: they carry `Nonpharm:`, `Pharm:`, `Education:` and `Follow up:`, which ADR 0254 ruling 4
retired. No committed note can produce an Entry copy, so "read the committed notes for the heading
forms" cannot run through the Entry copy pipeline.

### The agreement modes skip the console codec entirely

`anchor_scan.main` dispatches to `_run_agreement` before reaching `run_grader.run`, and
`console_codec` is imported nowhere in that module. So on `--agreement-brief` and `--agreement-read`
neither `use_utf8()` nor `require_python_floor()` executes. The brief mitigates the encoding half
with `ensure_ascii=True`; the interpreter floor check simply does not run.

## Ruling 1 — the stored form sections are evidence of what was pasted

The per-note file is not a second copy of the note. It is the only record of what was actually typed
into Medatrax, and it is what answers *what does the portal hold today*. A difference between it and
a freshly derived read is therefore **reported and never graded**: the command counts it, names the
notes, and its exit status is untouched.

Grading it was declined because ADR 0254 ruling 6 already ruled the fix forward only — notes already
posted are not corrected in bulk — and a committed command that exited non-zero on 16 of 64 notes
would put itself in contradiction with a ratified ruling. `medatrax_posting.completion_gate` already
grades the same fact one level up, returning a finding when the current note bytes stop matching the
recorded `SUBMISSION-SHA256`; nothing here duplicates that.

Deleting the artifact and deriving on demand was also declined. ADR 0254 ruling 3's reasoning that
two hand-kept copies of one note are how the copies come to disagree does not reach it, because this
is not a copy of the note; overwriting it is what would erase the evidence that found the ticket's
three stale notes in the first place.

## Ruling 2 — one module owns the note grammar and the existing readers are left alone

The reader that finds `S`, `O`, `A` and `P` and the Plan's end lives in `tools/note_grammar.py`, a
module with no command line and therefore no console-codec call, on `tools/worksheet_grammar.py`'s
arrangement exactly. Three partial readers of note structure already exist —
`entry_copy._plan_labels`, which locates `P` alone; `anchor_scan._section_codes`, whose closing-label
list is the closest thing in the tree to a correct boundary registry; and `differential_scan`'s
heading and tier patterns — and a fourth written into a new command would be a fifth copy to keep in
step.

Extending `entry_copy.py` to write both artifacts was declined on a lifetime collision rather than on
taste. That command overwrites its destination freely and unlinks it on any failure, and ruling 1
makes the sections file one that is never silently overwritten. One write path owning both is how the
wrong one gets destroyed, and `scratch/` has no history.

**This build does not refactor `entry_copy.py`, `anchor_scan.py` or `differential_scan.py` onto the
new module.** Each is a behavior-preserving change needing its own evidence, and folding three of
them into a build whose subject is elsewhere is how a green suite stops meaning anything. A test
binds `note_grammar`'s Plan boundary to `entry_copy._plan_labels`' over every committed fixture note
and every live Entry copy, which is the arrangement `PIPE_ESCAPES` and `split_row` already use: two
implementations permitted to differ, one test that says when they have.

## Ruling 3 — one command, writing when the file is absent and reporting when it is present

`tools/form_sections.py` is a single direct command. When no stored file exists it derives and
writes, because there is no evidence to destroy. When one exists it compares, reports, and writes
nothing; replacing it takes an explicit flag, which is the case where the clinician knows he is
discarding a record. The report says which of the two happened on every run.

Splitting it into a producer and a separate scanner, on `case_study_render.py` and `render_scan.py`'s
precedent, was declined: honoring ruling 1 means the producer must run the comparison before it
decides whether to write, so the split would put the identical comparison in two modules — the
duplication ruling 2 refuses one step earlier. That precedent earns its keep where the halves
genuinely differ, and here they do not.

The command branches on filesystem state and so does two things under one name. `day_file_text.py`
already lives with that, and the mitigation is the same one: the report names which branch ran.

## Ruling 4 — the reader accounts for every line and a Plan must close

An unknown **heading** form makes a section go missing and the refusal fires. An unknown
**terminator** is silent: the Plan runs past its end and swallows the coding worksheet, the tier
block, the Medatrax entry block or the drift matrix, the note still yields four non-empty sections,
and that apparatus is what gets pasted into a graded academic record. Refusing on *not exactly four
non-empty sections* cannot see it. This is `differential_scan`'s recorded lesson that a block end
matching too reluctantly never closes and reads what follows as content.

So a Plan that reaches end of file without a recognized closer is a **refusal**, not a section. The
measurement above makes that rule free: it refuses zero of the 92 committed and live notes, and fires
exactly when the corpus grows a closer nobody taught the reader.

And the reader assigns **every line** of the Entry copy to exactly one of preamble, `S`, `O`, `A`,
`P` and tail, printing all six counts on every run. A numerator and a denominator built from one
matcher can agree while both omit a form; a partition cannot, because the lines have to go somewhere.
It also reaches what neither weaker rule does — a second `S:` further down, or a heading-shaped line
inside a fence — which would move a boundary while leaving four non-empty sections and a clean tail.
The preamble is a named bucket rather than something skipped, because all 92 notes have one.

The command opts into ADR 0230's seam, printing `unread remainder N` through
`run_grader.format_unread_remainder` and exiting 2 when it is non-zero.

**The coverage claim is not believed until a mutant fails it.** The reader is fed at least one note
carrying an unrecognized terminator and one that has lost a heading, and both must fail before the
claim stands. A rule that refuses nothing on today's corpus is indistinguishable from a rule that is
never evaluated.

## Ruling 5 — the portal substitution belongs in the Entry copy and is keyed on a measurement

ADR 0254 ruling 2 defines the Entry copy as what is entered in the portal, and ruling 3 has the
readback compare the saved note against it. Today the Entry copy carries `∴`, what is typed is `;`,
and what Medatrax stores is `?` — three characters in one position across all 64 notes — so
`SKILL.md`'s instruction to correct an ordinary mismatch to the approved value names a value that
cannot be typed. The step is unsatisfiable as written.

`entry_copy.py` therefore applies the substitution, and the Entry copy literally is what is typed.
The form sections inherit it. The finished note keeps `∴` and every grader reading the finished note
is untouched. This extends ADR 0254 rulings 2 and 3 rather than superseding them; the artifact's
definition is unchanged and its content now matches it.

The substitution is keyed on a **measured table**, and a non-ASCII character in a pasted section with
no measured verdict is a **refusal** rather than a pass-through. Converting `∴` alone was declined:
the en dash outnumbers it nine to one across 28 notes and nobody has measured what the editor stores
for it, and passing an unmeasured character through is what put 567 of them into the portal with
nothing looking. A refusal costs one measurement; a pass-through costs a mangled graded record that
the readback then compares against the wrong bytes.

**The five characters are measured in the live portal before the build ships**, by entering a probe
carrying all of them into one scratch note form and reading back what was stored. That is the
clinician's experiment, not a committed command's: no scanner here fetches or writes a third-party
system.

## Ruling 6 — there is no split-and-merge command; the brief narrows and the read composes

`anchor_scan --agreement-brief` gains a `--stem` filter, and `--agreement-read` accepts several
record paths, composing them in memory and grading the union. Both of the ticket's operations
disappear, and **nothing ever writes a merged record**.

The ticket asks a merge to leave every other note's verdict exactly as its reader left it. Under this
ruling that is not a promise a test has to check: re-reading one note writes that note's record, and
no other record is opened for writing. The property holds because nothing can violate it. *Preserves
stem order* stops being a requirement too, since separate files have no order.

It is also less code than the standalone pair — one filter in `_pair_agreement_sources`, one loop
where there is now a single path — and the existing coverage accounting works unchanged over the
union.

This changes a contract ADR 0243 ruling 13 states, that `anchor_scan` writes the brief and grades the
record. The read keeps accepting a single file, so the committed control records and the three
`SKILL.md` call sites are unaffected. A narrowed brief **declares its bound**: it names the stems
requested and the shift's full pair count beside them, because a one-note brief reporting a clean
whole would claim coverage of a shift it never read. That is ADR 0230's rule that a deliberately
partial report keeps its ordinary status only when its contract names the bound beside the result.

The same change imports `console_codec` and calls `use_utf8()` then `require_python_floor()` on the
agreement dispatch branch, closing the gap measured above rather than filing it.

## Ruling 7 — `form_sections.py` is a Required command and a refusal blocks posting

It is a Required command for `clinical-note` and `batch-shift`, run before pasting, and AGENTS.md
gains an entry beside `entry_copy.py`'s. A **refusal blocks posting** on `entry_copy.py`'s terms,
because an unknown heading, an unknown terminator, an empty section or an unmeasured non-ASCII
character each mean the four strings are wrong. A **divergence never blocks**, on ruling 1.

Leaving it a tool the run may use was declined on this repository's own recurring finding, that what
a written instruction cannot do is fail. The failure it catches is silent: a stale stored copy is
well-formed, the right length, and parses.

Drift row 36 is **extended** rather than joined by a row 37. It is already the entry-procedure row
and already names the command that blocks posting; a second row covering the next step of one
procedure is how two rows come to disagree about one rule. `entry_copy.py`'s AGENTS.md entry changes
with it, since ruling 5 gives that command a third job.

## Ruling 8 — the names distinguish a reading from an artifact

`tools/note_grammar.py` takes the name `tools/worksheet_grammar.py` established. `tools/form_sections.py`
is named for the artifact it writes, on `entry_copy.py` and `entry-copies/`'s precedent, and it adopts
the existing `<run>/private/form-sections/note-N.json` path and its `{"S", "O", "A", "P"}` shape rather
than inventing one that orphans seven shifts of evidence.

`note_sections.py` was declined for the grammar module. It differs from `form_sections.py` by one word
while naming a different thing, and the distinction the pair now carries is real: **note sections** are
a reading of a note's structure, and **form sections** are the four strings typed into the portal,
frozen as evidence. They are the same content in two roles with two lifetimes, and conflating them is
how the overwrite ruling 1 forbids would have happened. `CONTEXT.md` carries both terms.

## Consequences

- New: `tools/note_grammar.py`, `tools/form_sections.py`, and their tests.
- Changed: `tools/entry_copy.py` gains the measured substitution; `tools/anchor_scan.py` gains
  `--stem`, multi-path record composition, and its console-codec calls.
- Changed: `AGENTS.md` gains a Required-command entry and amends `entry_copy.py`'s;
  `skills/clinical-note/SKILL.md` drift row 36 and its entry step, and `skills/batch-shift/SKILL.md`
  where it follows the same procedure.
- Changed: `CLAUDE.md` gains a section pointing at each new module's `DECLARED_LIMITS` without
  copying its rows, and its most-recent-direct-command correction moves to `form_sections.py`.
- Changed: `CONTEXT.md` gains **Form sections** and **Note section**, each with its `_Avoid_` line.
- The grammar is testable against all 28 committed fixture notes as a pure function over note text.
  The command wrapper is not, because `entry_copy.derive()` refuses every one of them; only the
  wrapper needs a real Entry copy, and its tests build synthetic ones.

## What none of this reaches

**Whether the four derived strings are the right four strings.** The grammar establishes that every
line is accounted for and that the Plan closes. Whether the content under `A` belongs under `A` is
the note's problem and remains a reading.

**Whether Medatrax stored what was pasted.** The form sections record what was typed. Only the
readback in `skills/clinical-note/SKILL.md` reads the portal, and ruling 5 repairs its comparison
without extending its reach.

**The 16 divergent notes.** Ruling 1 makes them reported and never graded; their disposition is the
clinician's, per note, and nothing here decides it.

**What the portal stores for `–`, `µ`, `—` and `²`.** Ruling 5 requires the measurement and refuses
until it exists; it does not supply it.

**Whether a narrowed agreement read was read by a second reader.** Ruling 6 changes the population a
record may cover and nothing else. ADR 0243's declared and unreachable independence is untouched.

**Measured at:** 53c2514544ed554a5bee129c9676f39dbc546860
