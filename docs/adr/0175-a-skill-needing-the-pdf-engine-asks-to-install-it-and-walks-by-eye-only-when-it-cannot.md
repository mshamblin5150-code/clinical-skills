# A skill needing the pdf engine asks to install it and walks by eye only when it cannot

[#1009](https://github.com/mshamblin5150-code/clinical-skills/issues/1009) was filed during
[#837](https://github.com/mshamblin5150-code/clinical-skills/issues/837)'s grilling: `AGENTS.md`, the
whole of what a consumer reads, names commands that need PyMuPDF at run time and says so of none,
beside a paragraph that says *there is still nothing to install*. The ticket asked whether the file
states the dependency and where, whether that sentence gets scoped, whether a consumer without the
package is in scope at all, and whether anything is checkable.

Grilled 2026-09-11 to an empty frontier. **Ten rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.
[ADR 0160](0160-the-pdf-engine-is-reached-through-one-seam-the-page-questions-are-four-and-the-availability-verdict-is-the-caller-role.md)
stands unchanged: its detection, its one remedy sentence and its roles are what these rulings point
at, and its `consumer-contract` limit is what they discharge.

**The ticket widened twice, under the standing rule that a subject entangled with a ticket's
correctness widens it.** `batch-shift` uses the engine too, so a contract naming only the coursework
skills would be wrong in the direction the ticket is about; and the Office applications the two
render producers drive are an install of the same kind. **Two findings were filed rather than
folded**, because nothing ruled here depends on them:
[#1086](https://github.com/mshamblin5150-code/clinical-skills/issues/1086), batch-shift's inline
snippet reaching the engine outside the seam, and
[#1087](https://github.com/mshamblin5150-code/clinical-skills/issues/1087), a second typed copy of the
engine-absence reason.

## Measured before ruling, at `9f3d018`

Freshness gate `FRESH` before reading, and again after rebasing onto `origin/main` `5dae592`, where
every figure below was re-derived.

**`AGENTS.md` names no PDF engine.** A case-insensitive count of `pymupdf`, `pdf_engine` and `pdf
engine` over the file returns 0. *Had the file stated the dependency by any of those names, the count
would be at least 1.*

**Twelve non-test modules in `tools/` import `pdf_engine`, and five of them are named in `AGENTS.md`
as `<name>.py`**: `case_study_render`, `deck_render`, `discussion_post_scan`, `render_scan` and
`threshold_sheet`. The last is named as a pre-commit refuser, not as a skill step.

**The file and the skills already answered the ticket's scope question in opposite directions.**
`AGENTS.md`'s paragraphs for `practicum-case-study`, `discussion-post` and `course-assignment` each say
a consumer without the command can walk the same rows by eye and cannot call the run mechanically
verified. The skills' own completion lines say otherwise: `discussion-post` will not report completion
until `discussion_post_scan.py ... --submission` exits 0, the case study's final checklist asks whether
`render_scan.py` exited 0, and course-assignment's render step grades final-pass coverage. Only
`practicum-case-study` step 9 grants a by-eye route, and only where the render producer cannot run.

**A missing engine and a real coverage gap exit the same way.** `render_scan.py` driven over a run
holding one pass, with `pymupdf` blocked from import, exits 2 and prints
`pass-1: PyMuPDF is unavailable`; the same run with the engine present, whose export is not a readable
PDF, exits 2 and prints `pass-1: could not read the retained export`. *Had the status distinguished
the two, the exit numbers would differ; they are both 2, and only a printed line tells them apart.*
`discussion_post_scan.py`'s rendered-pages row was read rather than driven: it prints
`not graded - PyMuPDF is unavailable` and the run exits 2, on ADR 0160 ruling 9.

**Among `aar_scan.COMPLETION_GRADERS`, only discussion-post's reaches the engine.** No module in
`tools/` imports an engine-reaching module other than `pdf_engine` itself, so none reaches it
transitively. The AAR's terminal gate reads `aar_scan`'s own status and returns to the invoking
skill's completion grader, so a completion line owns what that grader's status means. A real AAR
finding still outranks the missing engine, because `discussion_post_scan`'s findings status includes
the AAR result.

**`batch-shift` step 2 uses the engine directly**, in a fenced Python block opening `import fitz`. The
seam's walks read `tools/*.py` only, and ADR 0160's importer census was taken over the same files, so
this use was in neither.

**The Office applications are already optional on the agent's machine.** Both render producers
export through `powershell.exe`; on failure they exit 2 and the skill routes to a file the clinician
exports by hand. A submission with no page-faithful export stops. `case_study_render.py` checks for
the engine before trying either route, so the clinician's export needs the package too.

**The engine-dependent skills can be derived, and the derivation discriminates.** Taking every skill
directory whose Markdown names a `pdf_engine.ROLES` key as `<key>.py`, together with every skill
directory holding a fenced Python block that imports `fitz` or `pymupdf`, returns exactly
`batch-shift`, `course-assignment`, `discussion-post` and `practicum-case-study`. *`threshold_sheet` is
a `ROLES` key used only by maintainers; had any skill named it, that skill would have been returned
too, and none was.* Both matchers returned the members they should, so neither was dead.

**One test reads `AGENTS.md` on an install question**, `TheIndexTellsAConsumerWhatToInstall` in
`tools/test_guideline_sheets.py`. It pins the guideline-sheets sentence only, not the ICD sentence;
its docstring says the answer is still nothing.

## Ruling 1. A missing engine is installed first, and a step falls back only when it cannot be

When a step that needs the PDF engine finds it absent, the skill asks for the install before
anything else. Only when the install cannot happen does the run fall back: a check is walked by eye
against the rules the skill already writes out, and the run is complete but never **mechanically
verified**, which its completion report states.

Declined: stopping outright, which blocks a finished artifact on a property of the grading machine
rather than of the artifact, the ground ADR 0160 ruling 9 already gives; and falling back without
trying, which skips a one-command remedy that would have produced a real check. The fallback is the
house arrangement already: an agent that cannot run the ICD lookup proceeds from recall and marks
every code.

## Ruling 2. A skill checks for the engine before the step and never reads an exit 2's printed reason

A skill runs the engine check before each step that needs the engine. An exit 2 from that step is
accepted as the engine's absence only when that check reported the engine missing and the install did
not happen. The skill never keys on the text a grader prints, and no new exit status is added.

**The residue is named rather than left to be found.** When the engine is missing and the run also
has a genuine coverage gap, the gap's exit 2 is accepted with the engine's. The by-eye walk
re-examines the same retention and coverage rules, so a reader still meets it.

Declined: reading the printed reason, which ties skill instructions to output wording and to the two
copies #1087 records; and a distinct exit status, which breaks the 0, 1 and 2 meanings every grader
here states in order to serve three skills.

## Ruling 3. The clinician grants the install and the agent runs it

The skill asks the clinician's permission. On a yes, the agent runs the install itself, reads any
failure, and runs the check again. On a no, or on an install that fails, Ruling 1's fallback applies.

Declined: the agent installing without asking, which changes the clinician's machine without consent;
and handing the command to the clinician to type, which gives up the agent reading the failure and
re-checking at once.

## Ruling 4. Setup asks once, and each needing step checks again quietly

`setup-clinical-skills` step 0, which already arms the hooks and checks for Python, runs the engine
check and makes Ruling 3's ask, so the one interruption normally lands on the first day. Each step
that needs the engine runs the check again and asks only when the engine is missing there. The steps
are:

- `batch-shift` step 2, where a day file's text is got out
- `practicum-case-study` step 9, the render and its coverage grade
- `discussion-post` step 8, where retained captures are decoded
- `course-assignment` step 5, the render and its coverage grade

After setup has run on a machine the check prints and asks nothing. A setup check alone was declined
because it misses a new machine or a different agent, which is what Ruling 2 needs the check for.

## Ruling 5. batch-shift reads the day file with the agent's own PDF reader and says so

When the engine cannot be installed, `batch-shift` step 2 opens the day file with the agent's own PDF
reader and reads every page as an image rather than trusting an extracted text layer, because the
step's own rule that a zero-length extraction is a scan still holds. It stops only when the agent
cannot open a PDF at all.

`batch-shift` step 4's confirmation block gains a line naming the route:

```
Day file read with: <PyMuPDF | the agent's own PDF reader>
```

That is the stop where the clinician checks every boundary against quoted first and last lines, which
is where a misread shows. A second ask before using the other reader was declined as a question
already answered by the declined install.

## Ruling 6. `tools/pdf_engine.py` gets a command line, and its statuses are 0, 1 and 2

The engine check is `python tools/pdf_engine.py`:

- **0** when the engine imports, printing that it is installed and its version
- **1** when the check ran and found the engine missing, printing `pdf_engine.REMEDY`
- **2** when the check could not reach a verdict, which is an acquisition that fails any way other than
  the engine's absence

A missing engine is 1 and not 2 on
[#744](https://github.com/mshamblin5150-code/clinical-skills/issues/744)'s ground: the check found
the one thing it exists to find. The command calls `use_utf8` on its command path and joins the
console-codec record in `CLAUDE.md` like every direct command. It copies no string: detection,
version and remedy are already the module's.

Declined: a separate small tool importing the seam, which adds a file whose whole job the seam already
does; and no command, where a skill would run a bare import and then have to type the install line,
the second copy ADR 0160 ruling 2 forbids.

## Ruling 7. `AGENTS.md` states the contract once, near the top

One paragraph, placed beside the instruction to run `/setup-clinical-skills` before the others,
carries:

- the four skills of Ruling 4 by name, as needing the PDF engine, PyMuPDF, on the machine that runs them
- that no other skill needs a Python package, which is narrower than the repository: maintainer
  commands that open the guideline corpus need the engine too, and a consumer runs none of them
- `python tools/pdf_engine.py` as the check that says whether it is present and prints the install
  line when it is not
- that `setup-clinical-skills` step 0 runs it and asks before installing, and that each of those
  skills runs it again before the step that needs it
- Ruling 1's fallback and Ruling 5's, in a sentence each

The install line itself never appears in `AGENTS.md`. The three existing sentences offering a by-eye
route for `practicum-case-study`, `discussion-post` and `course-assignment` each gain that the route
applies after the install has been tried. The skills' completion lines are changed to match Rulings 1
and 2, so the file and the skills stop giving opposite answers.

Declined: one sentence in each skill's dependency paragraph, which leaves the reader to finish four
paragraphs before learning that Python is not enough and scatters the list.

## Ruling 8. Word and PowerPoint are named in that paragraph, with their fallback

The same paragraph says that `practicum-case-study` and `course-assignment` use Microsoft Word or
PowerPoint on Windows for the automatic page export; that without them the clinician exports the file
by hand; and that a submission with no page-faithful export stops. Its summary sentence is scoped to
Python packages so that it stays true. Leaving the applications out was declined, because it makes
the paragraph a reader consults to decide *can my machine run this* wrong in the direction this
ticket was filed about.

## Ruling 9. The ICD sentence is scoped to the lookup

`AGENTS.md`'s *There is still nothing to install* becomes *The lookup still needs nothing installed*,
keeping its reason beside it. Deleting it was declined because the ICD path's freedom from any install
is worth a reader knowing. Leaving it was declined because it depends on reading order. The docstring
of `TheIndexTellsAConsumerWhatToInstall` is reworded in the same build, since *the answer is still
nothing* stops being true of the file.

## Ruling 10. A test derives the engine skills and binds the paragraph in both directions

A test in `tools/` derives the set of engine-dependent skills the way the measurement above did, and
compares it with the skills Ruling 7's paragraph names, in both directions. The same test asserts:

- that `AGENTS.md` names `python tools/pdf_engine.py` and copies none of `pdf_engine.REMEDY`, through
  the prose-bind instrument of
  [ADR 0158](0158-the-prose-bind-is-one-instrument-and-its-rule-carries-an-identity.md)
- that `setup-clinical-skills` step 0 and each derived skill name that command

It states its ceiling beside the derivation: it sees a command only when written as `<name>.py` and
an import only inside a fenced Python block, so a skill reaching the engine any other way escapes it.
The same build retires `pdf_engine.DECLARED_LIMITS`' `consumer-contract` row, because this build is
the change to the consumer contract that row says was not made.

Declined: asserting only that the paragraph mentions the package and the command, which stays green
when a fifth skill starts rendering pages and nobody edits `AGENTS.md`; and no test, which leaves a
hand-kept list that fails nothing when it goes stale.

## What the build verifies

- **The command's three statuses are driven, not read**: with the engine present, with its import
  blocked, and with an acquisition made to fail another way.
- **The derivation's liveness in both directions**: a skill fixture naming an engine command turns
  the test red, and removing one skill's name from the paragraph turns it red.
- **Each changed completion line is walked against its grader**: a discussion-post run with the engine
  blocked reaches the completion report as not mechanically verified, and a run with a genuine finding
  still stops on exit 1.
- **Nothing in `AGENTS.md` carries the install line**, through the copy detector, and the existing
  `AGENTS.md` tests still pass.

## What this record does not settle

**The route to the engine for `batch-shift`.** Whether step 2 calls a command or keeps a snippet is
#1086's, and Ruling 10's snippet source exists only until that is ruled.

**The second copy of the engine-absence reason** in `discussion_post_scan.py` is #1087's.

**A consumer with no Python at all.** The by-eye routes `AGENTS.md` already describes for that
harness are unchanged, and nothing here measures one.

**The consumer path's Python version floor** is
[#927](https://github.com/mshamblin5150-code/clinical-skills/issues/927)'s, and macOS, where
`powershell.exe` does not exist, is
[#773](https://github.com/mshamblin5150-code/clinical-skills/issues/773)'s.

**Whether a derived test fits the other install-shaped facts** `AGENTS.md` states, such as the ICD
database being committed. Only the engine's list is bound here.
