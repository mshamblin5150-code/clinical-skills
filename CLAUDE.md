See [AGENTS.md](AGENTS.md) for the skill index and the standing rules that bind every skill in this repo.

## Agent skills

Configuration for the maintainer's engineering skills. **None of this is required to use the clinical skills** — consumers read [AGENTS.md](AGENTS.md) and need nothing else, with no plugin to install.

### Subagents

**Spawning subagents is allowed in this repo, without asking first.** Fan out for anything that means reading widely — sweeping the corpus, checking a claim across many files, reviewing a diff along several axes at once. `/code-review` runs its two axes in parallel subagents and is the normal way to review work here.

Two constraints that are not about permission:

- **A subagent must not paste PHI back.** Everything under `scratch/` and `output/` is a patient record. A subagent reading them reports counts, file paths and findings — never note text, names or dates. `tools/corpus_census.py` is the worked example: it reads the corpus and can only emit integers.
- **Take a subagent's result as a claim, not a fact.** Its conclusions get checked the same as anyone's, and figures it reports get re-derived before they are written into a skill file. This is [ADR 0001](docs/adr/0001-fixture-asserts-on-named-findings.md)'s reasoning applied to agents: a report by the pass that produced it is a baseline, not a verification.

### Issue tracker

GitHub issues on `mshamblin5150-code/clinical-skills`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

**Search before you file** — `gh issue list --state all --search "..."`, on the command or file or symbol rather than your own framing. #20 and #21 are one bug filed 25 minutes apart by two sessions that never saw each other, both labeled correctly: labeling makes a ticket findable once it exists, and only searching stops the second copy being written.

**Finishing a ticket means sweeping the tracker, and that is authorized without asking.** A merged PR is half of finishing; the work found things, and those belong on the tracker before the session ends. Update the tickets your findings move and file the ones they raise — **changing a ruling needs the clinician, recording what you found does not.** The reason is #59's own defect one level up: a finding left in a merged diff is discoverable only by reading that diff, so the next session re-derives it or does not. The shape most often missed is **a claim in an open ticket your work proved wrong** — #130 said #69 and #97 had no recoverable anchor and both had one, in the fixture prose that filed them.

**The sweep is every open ticket, one at a time, each getting a verdict — not the ones whose titles look related.** Ruled 2026-08-15, because the session settling #63 swept 9 of 39 by relevance and both findings that mattered were outside its selection: a latent defect in the code it had just merged, found in #137, and a figure stale in ten places across four files, found in #94 and #96. Neither ticket has anything to do with what that session was working on. **A relevance filter selects on what you already understand, which is the wrong instrument for finding what you missed.** Expect "untouched" — 26 of 38 were — and fan the reading out across subagents. See `docs/agents/issue-tracker.md` for what a sweep looks for and what not to file.

### Triage labels

The five canonical roles, kept at their default strings, plus a local `grilling`. See `docs/agents/triage-labels.md`.

**Label every issue at creation time** — `gh issue create --label "..."`. An unlabeled ticket is one nobody can find. And a ticket with a decision still open gets `grilling`, **never** `ready-for-agent`: that label promises an unattended agent can build the thing without guessing, and #8 carried it while being unbuildable as written.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root, created lazily by `/domain-modeling` rather than scaffolded upfront. See `docs/agents/domain.md`.

## Maintainer tooling

Also not required to use the clinical skills, and deliberately not cited from [AGENTS.md](AGENTS.md) — a consumer needs the Markdown and nothing else.

### Console codec

`tools/console_codec.py` is **the only module every command line in `tools/` imports**, and it holds one line of policy: **each of them puts stdout and stderr on UTF-8 with `errors="replace"` before printing anything.**

It is *not* the directory's first shared module, and #150's *"there is no shared module in `tools/` today to put one in"* is false as written — `guidelines_search` imports `guidelines_index`, `icd10_lookup` imports `icd10_build`, `harvest_review` imports `phi_scan`, `filled_vitals_census` imports `corpus_census`. What it is first at is being **infrastructure rather than a tool another tool happens to need**. This paragraph originally said "the only shared module in `tools/`" and was caught in review, which is the #137 shape again: the generalization was made from the four files the work had open.

```python
from console_codec import use_utf8

if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
```

**The defect it exists for is an exit status, not a mangled character** — [#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150). On Windows the default stdout codec is cp1252, and guideline text is full of characters it has no code point for: the greater-or-equal sign a threshold is written with, an en dash, a typographic quote, a mu. The `print` raised `UnicodeEncodeError`, the traceback escaped `main`, and the process exited **1** — which `guidelines_search.py`'s own contract reads as *a genuine zero*. So the one failure those statuses exist to make visible was reachable by accident, and **the queries likeliest to hit it were the clinical-threshold ones**, because a cut point is written with exactly the character that dies. Output was partial and looked complete: the `== query` header printed, some hits printed, then it stopped mid-list.

**`errors="replace"` carries as much of the fix as the encoding does.** A console that genuinely will not move off its codec still has to print a legible line with a `?` in it rather than raise, because the thing being protected is the exit status and not the glyph.

**Called from `__main__`, never at import, and that is the shape rather than a habit.** Reconfiguring `sys.stdout` is a decision about a process; a module that made it on import would make it for every test importing it and for every tool importing another. `tools/test_console_codec.py` **parses every module in `tools/` and asserts the ones with a command line call it** — **26** of them today, and the paragraph below says which one is newest. *(This sentence read 22 while the one below read 23, for the length of one review: two figures for one count, in the same section, one updated and its neighbor left. [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape at the shortest range it has yet been caught at.)* The check is an AST walk and not a substring search, because the first version was a substring search and `console_codec.py` passed it on the usage example in its own docstring: a module with no command line at all, graded as having one. That is `spelling_scan`'s mention-versus-use distinction arriving uninvited, and it is why a sixteenth tool cannot quietly skip the line.

**It reads 26 today, and `tracker_bodies.py` is the most recent — written on #130's branch against a base that already carried this rule. It read 25, and `tracker_scan.py` and `checks_ledger.py` were the two before it — written on separate branches, on the same day, against a base that already carried this rule, so neither could arrive the way the sixteenth and seventeenth did. It read 23, and `reference_scan.py` was the one before them, on the same terms. It read 22, and `research_ledger.py` was the one before that. It read 21, and `docx_read.py` and `docx_write.py` were the two before it, on one branch against a base that already carried the rule too. It read 19, and it read 17, and #83 added two at once — `guidelines_recs.py` and `threshold_sheet.py`, on one branch, so neither could arrive the way the fifteenth and sixteenth did.** **Those two branches are why the sentence above passed through 25 rather than 24, and the way that was nearly missed is worth more than the number.** Each branch moved 23 to 24 and named its own tool as the most recent. The *naming* halves differed, so git conflicted and a person had to look; the two `**24**`s were **byte-identical**, so git merged that one silently and the count was wrong in a tree neither branch had ever produced. [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s subject, and [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the merge is the unguarded moment* arriving on a **figure** rather than on an import — where no suite can catch it, because `test_console_codec.py` asserts a floor. It was caught only because the neighbor sentence forced the look, which is the argument for keeping the pair in one paragraph and is the second time this exact sentence has recorded it.

**It read 15, and the sixteenth arrived the same day from the other direction.** `tools/anchor_scan.py` was written on [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124)'s branch while this rule was being written on #150's, and the two merged an hour apart. **Neither branch's suite failed; the merged tree's did** — the new tool did not import a helper that did not exist when it was written, and nothing either side ran could have seen it. That is [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the merge is the unguarded moment*, arriving on the mechanism built to make a fifteenth tool impossible to miss and catching the sixteenth one commit late.

**#150 fixed the process's *output* codec, and the *input* end of the same boundary was wrong in three places until 2026-08-18.** `subprocess.run(..., text=True)` with no `encoding` decodes with the **locale** codec, which here is cp1252 -- so a tool reading `git` output dies on any byte cp1252 has no mapping for. `phi_scan._git` named `encoding="utf-8", errors="replace"`; `spelling_scan._git` and both of `skills_mirror.py`'s call sites did not.

**What tripped it is the part worth keeping.** A paragraph in this file documenting `docx_read.py`'s homoglyph map -- which has to contain the homoglyphs in order to describe them -- was staged, and `spelling_scan`'s pre-commit run died inside `staged_additions` with `'NoneType' object has no attribute 'splitlines'`, on a `_git` that had already raised `UnicodeDecodeError` in a reader thread. **The commit went through**, because `spelling_scan` is advisory and the hook ORs its status away: **an advisory check that crashed is indistinguishable from one that passed.** Describing the rule broke the tool that checks the rule, which is `differential_scan`'s [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) arriving on a different module.

**It cost a real finding, which is the argument for the test rather than for the fix.** With the scan dead, `licence` landed in `skills/practicum-case-study/SKILL.md` -- a form already on standing rule 4's table, and the same one [#73](https://github.com/mshamblin5150-code/clinical-skills/issues/73) recorded as its thirteenth instance. **Neither net caught it**: the staged scan crashed, and `--all` walks `git ls-files`, so it cannot see a file until the commit that makes it tracked. `TheOtherEndOfTheSameBoundary` in `tools/test_console_codec.py` now walks every `subprocess` call in `tools/` by AST and asserts each one that decodes names both its encoding and its `errors`, so a fourth site cannot arrive quietly.

**Two things it does not reach, and both follow from the placement rather than being oversights.** A tool that printed *before* `main` would print through the old codec — nothing here does, checked by AST, and an `argparse` error is written by `argparse` to a stream already reconfigured. And **a caller that imports `main()` rather than running the script gets no protection at all**, which is every command-line test in `tools/`; that is why they still redirect into a `StringIO` happily and why #150's end-to-end case had to be a subprocess.

**`icd10_lookup.py` was safe, and not for the reason #150 assumed** — it prints tabular notes as well as descriptors, and only the descriptors are ASCII. The counts, the date and the nine code points are in that module's own docstring and **deliberately not restated here**, on `spelling_scan --record`'s terms: [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is one figure that went stale across many files at once, and a number is cheapest to keep true where the code that produces it lives. **The count of places is deliberately not restated here**, because #143's own headline figures have since gone stale twice over — 31 became 34, and 34 is 37 today across six fixture sets — which is the ticket demonstrating its own thesis on itself.

### Corpus census

Several claims in [clinical-note](skills/clinical-note/SKILL.md) are counts over the clinician's shorthand corpus, and rulings have turned on them. `tools/corpus_census.py` recomputes all of them:

```bash
python tools/corpus_census.py
```

It reads `scratch/day-file-text/` — gitignored PHI — and **prints counts only, never matched text**, so its output is safe to paste into a ticket. Run it before relying on a figure again, and whenever the corpus grows.

**Since #93 that path resolves through the checkout that owns this tree, so the command above works from a worktree with no argument.** It used to resolve from the module's own location, which in a worktree is a `scratch/` that has never existed — #78 was blocked on exactly that and got its figures by typing the main checkout's path. See *Corpus resolution* under the PHI hook.

Its extractors are covered by `tools/test_corpus_census.py`, which runs against the committed PHI-free fixtures and never touches `scratch/`:

```bash
python -m unittest discover -s tools -t tools
```

Stdlib only — no package manager and no lockfile, and the census is not worth introducing either.

**That sentence used to bundle a third thing, and the three were never coupled.** It read *"no package manager, no lockfile, no CI in this repo"*, and the reason written down was about dependency machinery — which CI here carries none of. [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86) reversed the CI clause and left the other two standing; see *Continuous integration* below and [ADR 0002](docs/adr/0002-ci-runs-the-suite-at-the-merge.md).

**Five tools are now exceptions, and they are the five that open a PDF.** `tools/guidelines_extract.py`, `tools/uspstf_table.py`, `tools/guidelines_recs.py` and `tools/threshold_sheet.py`'s citation tier 2 all need PyMuPDF; `tools/guidelines_catalog.py` prefers PyMuPDF and falls back to `pypdf`. Reading a PDF is not something the standard library does, so `tools/icd10_build.py`'s *"Stdlib only, like everything in `tools/`"* is no longer true of the directory.

**It read three, and #83 changed both halves of that sentence.** It added two tools, and it moved `guidelines_extract.py` off `pypdf` — so `pypdf` is now a fallback in exactly one place and no tool requires it. The count going up is not the finding; **the finding is still that three of the five extract text from the same 179 files**, and two of those exist only because #80 had not landed when they were written. [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) is where that gets reconciled down to one, and it is now cheaper than it was: they no longer disagree about which library reads a page. Each import sits inside the function that opens the file rather than at module scope, so the test suite needs nothing installed — and **nothing a consumer runs imports any of them.**

**That sentence was false for one class, and the first CI run is what found it.** `tools/test_threshold_sheet.py`'s `TheRenderedPageEscapeHatch` calls `gate_citation_tier2`, which returns early with `pymupdf is not installed` — so on a clean machine one test failed outright and **two others passed for the wrong reason**, asserting `rendered == 0` against a gate that short-circuited before it could count anything. The maintainer's machine has PyMuPDF, so no local run could ever have shown it; #86's very first run on a bare Windows runner did, at 1,126 tests. The class now skips as a whole rather than in part, because a partial run here reads as a pass. **The honest form of the claim is that the suite runs with nothing installed and four tests skip when it is absent**, not that it needs nothing.

### Filled-vitals census

The corpus census reads the clinician's shorthand. This one reads **a run's finished notes**, and it exists because [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67) is a defect no single note contains: nine notes each filling a plausible vital set, and one patient described nine times.

```bash
python tools/filled_vitals_census.py <a run directory>
python tools/filled_vitals_census.py fixtures/filled-anchor/notes   # the committed evidence
```

It counts only what a tier block **declares filled** — `clinical-note`'s own `BP 142/88 filled` form — so given vitals stay out of the numbers, and a run that stops writing values into the block reads as having filled nothing rather than as having passed.

**Counts only by default, and that is load-bearing here rather than conventional.** A run directory lives under `scratch/` or `output/` and is a patient record. Nothing it prints without `--show` is a measured value, so its output is safe to paste into a ticket; **`--show` output is PHI on `harvest_review.py`'s terms** — read it, do not paste it.

**Three rows are graded now**, and two of them are [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s ruling of 2026-08-17: `fixtures/day-b` **B13** (no two notes share a filled height-and-weight pair), **B17** (filled pressures may not land not-normal far more often than a fair split explains) and **B18** (every filled height's clause names an age and a sex). **Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a violation, **2 for every way of not having scanned**, including **no note declaring a filled height or a filled pressure**. That last limb is `scratch/day-a-run-2`'s real shape — eleven notes, nothing filled — and without it such a run reports a clean set of rows it was never measured by. **Where a violation and an ungraded set both hold, 1 wins**, on `differential_scan.py`'s ordering.

**#97's own objection was that no N could be grounded, and that was true of a count and false of a false-alarm rate.** The corpus splits about evenly at 130/80, so an honest set of filled pressures should land like that many coin flips; what the clinician chose was **how often an honest run may be failed for nothing** — 2%, putting the cut at 8 of 9. **Six of nine passes deliberately**: it is a coin-flip outcome one time in four, and a bar failing it fires on an honest set at the rate warnings stop being read. **The height half needed no threshold and got none** — repetition is still not graded, because `clinical-note` blesses it where the encounter supplies no habitus datum *and* forbids the only remedy a repetition bar would leave.

**Five vital classes are counted and not graded, and that gap is [#69](https://github.com/mshamblin5150-code/clinical-skills/issues/69)'s.** That ruling turned entirely on a filled temperature and two filled saturations while this tool read neither. It now counts temperature, heart rate, respiratory rate, saturation and pain score — **36 values across the twelve committed notes, against the 27 the graded rows read**, the severity being the one class none of the twelve declares — and grades none of them, the corpus offering no even split to ground a cutoff the way 130/80 grounds the pressure one. Everything else it prints stays R5.

**Run it against `fixtures/filled-anchor/notes` and it exits 1, which is worth knowing before reading a non-zero as breakage.** **5 of its 9 heights name no age and sex and the other 4 already write the compliant form**, two with a percentile; its pressures clear B17, so the exit is the heights alone. **The obvious explanation is wrong and was published wrong first** — that set is day-b run 1, predating drift row 19, so the prediction was that all nine fail. Four do not. The prediction came from two notes during #97's grilling and was corrected by running the scanner over twelve, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) a further time and is why the compliant form is worth naming: **B18 asks for something this skill has already produced unprompted.**

Covered by `tools/test_filled_vitals_census.py`, which runs against the twelve committed notes and pins the figures #67, #69 and #97 rest on, so editing that run record fails a test rather than quietly voiding an argument.

### Specificity scan

The filled-vitals census reads a `clinical-note` run. This one reads an **`icd10-cpt` run**, and it is `fixtures/filled-anchor` **C5** made runnable — [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56).

```bash
python tools/specificity_scan.py <a run directory>
```

**Two tests, neither of which needs a reader.** A `SPECIFICITY` flag must carry substance beyond its keyword — a bare `complete` and a bare `needs:` both fail — and a code whose **official descriptor** says `unspecified` or `not specified` may not read `complete` at all. The first is there because *the reason is the evidence the check happened*: nobody writes `Z98.51 has no further axis` without having looked at `Z98.51`'s axes, and anybody can write `complete`.

**The second test rests on C2 and is worth knowing about before trusting a clean scan.** It reads the descriptor sitting beside the flag, which is only meaningful because C2 requires that string be the **verbatim official** one. Against a paraphrase it is a question about the run's wording rather than about the code set, so a run that failed C2 and passed C5 has not been graded on anything.

**Counts only by default**, on `filled_vitals_census.py`'s terms and for its reason — a run directory under `scratch/` or `output/` is a patient record, and a code with its descriptor is a diagnosis attached to an encounter. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a C5 failure, **2 for every way of not having scanned**: no directory, no worksheets in it, no argument. That is `guidelines_search.py`'s arrangement rather than `filled_vitals_census.py`'s, because a run whose output landed elsewhere would otherwise report a clean set of flags.

Covered by `tools/test_specificity_scan.py`, which builds synthetic worksheets in this file and a temp directory. **That used to be because there was no committed `icd10-cpt` run to test against, and since [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) there is** — `fixtures/filled-anchor/run-2/`, twelve worksheets. The tests stay synthetic anyway, on `test_icd10.py`'s reasoning: a test reading the run its own row graded would pass for two reasons, one of them being that the run and the scanner are wrong together. What the committed run buys is that **C5's figure is re-derivable rather than cited** — one command over a directory a reader can open. One test reads `skills/icd10-cpt/SKILL.md` and asserts the template says what the scanner checks, on `test_spelling_scan.py`'s reasoning: a scanner that has drifted from the file a reader opens is worse than none, because it reads as agreement.

### Differential scan

The specificity scan reads an `icd10-cpt` run. This one reads a **`clinical-note`** run, and it is drift row 22's mechanical limb made runnable — [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68), rebuilt on [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

```bash
python tools/differential_scan.py <a run directory>
```

**One test, and it needs no reader.** No code marked `NOT CODED` anywhere in a note may sit in an entry's **code slot** — the position after the hyphen that pins a code to its label. #68 was filed over a naming question and closed a hole that was not about naming: one run produced three renderings of one rule, **all three kept the refused code out of the slot, and nothing required them to.** A fourth putting `M86.9` after the hyphen with the refusal in a footnote would have satisfied every row this repo had while asserting a disease nobody established.

**What it cannot reach is row 22 itself, and that is permanent rather than pending.** Deciding whether `Pain in right leg` is what `M79.604` says is a comparison of a label to a descriptor, and paraphrase is permitted — `Mild dyspnea - R06.02` and `Shortness of breath - R06.02` are both correct. **A clean scan is not a walked row**, `skills/clinical-note/SKILL.md` says so beside the command, and a test asserts that sentence is still there.

**A refusal is the welded pair `NOT CODED: <code> <descriptor>, <reason>`, and nothing else is read as one.** #153 is why, and the first version's rule — *the last code before the mark on the same physical line* — was a guess that failed in both directions. Hard-wrap a rationale and the refusal became **invisible**: `codes marked NOT CODED 0`, exit 0, a silent pass. Write a drift-row-22 verdict *about* the rule and the note was read as refusing its own final diagnosis: exit 1, and the finding false. **Describing the rule was what broke it**, which is `phi_scan`'s self-exemption problem inverted. Four things carry the fix and dropping any one reopens a symptom — the welded pair; **a pipe table skipped outright** because in a note a table is the drift matrix and never an entry; **a form inside backticks read as a mention rather than a use**, which is `spelling_scan.py`'s rule adopted whole and is the limb that reaches a loose *sentence* about row 22 rather than a table (without it symptom 2 stops being a false exit 1 and becomes a false exit 2, which is quieter rather than fixed — caught in review); and **a conclusion read by position rather than punctuation**.

**The form was not invented for the fix.** `icd10-cpt` step 4 has always written it, and all twelve worksheets in `fixtures/filled-anchor/run-2/` use it and nothing else; `clinical-note` was the outlier writing the code first. Checked before the ruling rather than assumed.

**A run in the retired form exits 2, and a real run is why that limb had to be *any* bare mark.** The guard first fired only where a run had no welded refusal at all; a `day-a` run cleared it on a handful of welded refusals while the rest went unread beneath a printed `row 22 - refused code in a slot  0`. That is the partial-coverage-reading-as-complete shape, not a partial success, and it was caught by pointing the tool at a real run rather than by a fixture. **The counts are stated once, in `fixtures/day-a/assertions.md`, and deliberately nowhere else** — they were measured against a directory under `scratch/`, so nothing committed re-derives them, and [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is what one unre-derivable figure copied into many files becomes. The behavior is pinned by a test instead.

**It no longer grades `fixtures/hedged-dx` run 1's case 2, and that is a reclassification rather than a lost finding.** That note is the shape #68 was filed over and the scanner used to catch it; its refusal is in the retired form, so the run now reads as unscanned. **N1 is still failed by that run**, by a reader, and `fixtures/hedged-dx/assertions.md` records which.

**Counts only by default**, on `filled_vitals_census.py`'s and `specificity_scan.py`'s terms and for their reason: a run directory under `scratch/` or `output/` is a patient record, and an entry label is a diagnosis attached to an encounter. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a row 22 violation, **2 for every way of not having scanned**, including **no differential entry in any note read, and any bare `NOT CODED` mark**. Those two limbs are the ones that matter: a run whose differential was written in a shape the parser does not read, or whose refusals are written in the form row 22 retired, would otherwise report zero violations and look like a pass. **Where a violation and an incomplete scan both hold, 1 wins** — returning 2 would file the strongest thing known about the run under the weakest heading — and the exit-1 message names the unwelded count so the finding reads as a floor rather than the whole. That ordering is deliberate and it is the one limb here that departs from `block_scan.py`'s, where 2 is reserved for total absence.

**Run it against `fixtures/filled-anchor/notes` and it exits 2, which is correct and worth knowing before reading it as breakage.** **Zero of the twelve use the `label - CODE` slot form**, so there is nothing for a slot test to read and the tool says so rather than reporting a clean run. Measured 2026-08-15, re-derived 2026-08-16, and **pinned by a test**, because it is the claim the tool's own limits rest on. **All twelve do carry a `Final diagnosis` line and none carries a `NOT CODED` of either kind**, which is why the conclusion count is kept apart from the differential count: a single total would have let those conclusion lines rescue the set into looking scanned, turning a documented exit 2 into a silent exit 0. **Their `malformed slot pins` would read as every conclusion code in the set**, because those notes pin with an em dash throughout — so on that set the count carries no signal, and it is never printed there anyway since the exit-2 limb fires first.

**The obvious explanation for that is wrong, and it was published wrong here first.** This paragraph originally said the twelve carry *no ICD-10 code at all* on a differential entry. **Four of them do** — case 7 carries 13 in its differential block and case 8 nine, in the form `**COVID-19 (U07.1) — FAVORED.**`, with the code in **parentheses** rather than pinned by a hyphen. Six of the twelve carry no `Differential` heading at all; cases 1, 2, 9 and 10 head one and write entries carrying almost no codes. **So the set is not uniformly pre-#19 and it is not uniform at all** — which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s subject, and a third split for it. What is uniform is only the thing measured above: **nobody uses the hyphen**. A sweep by one reader produced the wrong generalization from two notes; a second reader caught it, and the figure was re-derived before this sentence was rewritten.

Covered by `tools/test_differential_scan.py`, which builds synthetic notes in that file and a temp directory — **there is no committed `clinical-note` run whose differential this could be tested against**, for the reason in the paragraph above. Two shapes are pinned deliberately. A compliant entry carries its own slot code and its refusals on a single line, so anything treating every code on a `NOT CODED` line as refused flags the slot and fails the skill's own worked example. And **a refusal clause stops at the end of its line**, because a clause running to the end of the paragraph would swallow the entry written below it and hide a violation on that one — the mirror of the bug the clause exists to fix.

### Anchor scan

The differential scan reads a `clinical-note` run. This one reads an **`icd10-cpt`** run again, and it is `fixtures/filled-anchor`'s **ANCHOR** class reduced to the part a machine can settle — [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124).

```bash
python tools/anchor_scan.py <a run directory>
```

**Two tests, neither of which needs a reader.** The mark and the listing must agree — every code carrying `SOURCE: filled` appears under `CODED, ANCHOR WAS FILLED`, and every code that block lists carries `SOURCE: filled` on its own entry. **Either direction alone is the failure**, which is `skills/icd10-cpt/SKILL.md`'s *"Both, not one instead of the other"* made runnable. And a pediatric `Z68.5-` may not read `verified against ICD-10-CM FY2026`: the repo ships the codes without the CDC growth charts, so the band is recalled however carefully the number was checked. [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) retires that second test by shipping the charts.

**A listing is a line format, not a substring** — `<code> - <value>`, the code pinned at the start of its line by a dash. That is deliberate and it is `fixtures/filled-anchor`'s own *Still unresolved* bullet: a run can write *"`Z68.25` needs no `SOURCE` line, the inputs were given"* **inside** the block, which puts the string exactly where a substring search looks.

**The pre-#46 heading is not this block, and the lookbehind that says so is the load-bearing line in the parser.** Run 1 refused every filled anchor and wrote them under `NOT CODED, ANCHOR WAS FILLED`. A scanner reading that as the new block would report a clean pass for the exact behavior #46 reversed; this one reads a run reproducing run 1 as having **marked nothing** and exits 2.

**A clean scan is not a walked row, and what it cannot reach is most of ANCHOR.** Whether a note's BMI had a filled input, whether `I10` was rightly absent on a filled pressure, whether case 4's `Z68.25` rests on two given values — each compares a worksheet to a note, and **the note is not in the run directory**. A3 in particular is invisible: a run that stopped coding the family altogether marks nothing and reads as unscanned.

**Counts only by default**, on `specificity_scan.py`'s and `differential_scan.py`'s terms and for their reason: a run directory under `scratch/` or `output/` is a patient record, and a code with the value it rests on is a measurement attached to an encounter. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for an ANCHOR violation, **2 for every way of not having scanned**, including **no marked code, no listed code and no pediatric band in any worksheet read**.

Covered by `tools/test_anchor_scan.py`, which builds synthetic worksheets in that file and a temp directory. **Unlike its two siblings it now has a committed run to point at as well** — `fixtures/filled-anchor/run-2/`, the first `icd10-cpt` run this repo has kept — but the tests stay synthetic on `test_icd10.py`'s reasoning: a test reading the run it graded would pass for two reasons, one of them being that the run and the grader are wrong together.
### Block scan

The differential scan reads a `clinical-note` run's differential. This one reads the same run's **tier block**, and it is `fixtures/day-a`'s **F1, F2 and F3** made runnable — [#120](https://github.com/mshamblin5150-code/clinical-skills/issues/120), whose own comment asks for it by name: *put any grader in `tools/`*, because the four graders that scored `filled-anchor` run 1 were written into the run directory and went with it when the worktree was removed.

```bash
python tools/block_scan.py <a run directory>
```

**Three tests, none of which needs a reader.** `Primary Payment Method` and start-and-end times never open a `GAPS` entry — both are filled or estimated by design, and a GAPS line for either is the block teaching the clinician to skim. `Race/Ethnicity` appears under `FILLED·asserted` and never opens a GAPS entry; **that row has two limbs**, and the second is why it is not the first row's twin: a declared administrative value is a claim about the patient, so a block naming it nowhere has dropped it rather than passed by omission.

**A row fires on what opens an entry, never on a mention inside one, and that is what makes it safe to run unattended.** A GAPS entry reading *"Site and preceptor. Not in the source. The site also decides the payment method above."* is **compliant** — its subject is the site, and the sentence explains a dependency. The first version of this scanner matched any mention and called three such sentences failures on day-a run 2; every one was prose about the rule. **Every violation these rows describe opens an entry, and nothing that opens an entry is prose about the rule.**

**What it cannot reach is F4, and that is permanent rather than pending.** Deciding whether a `FLAG` names both the finding and the omitted action is reading a sentence, not matching a string — `BP 151/93 undiscussed` passes and `vitals not addressed` fails. F5, F6 and F7 turn on one case's age and sex and are questions about an **input** this never sees. All four stay counted by a reader.

**The entry boundary is a reading, and [#127](https://github.com/mshamblin5150-code/clinical-skills/issues/127) is why it has to be.** An entry opens at a label line or a bullet; every other indented line is a **wrap**. That is right for a run repeating the label per entry, which is what day-a run 2 does, and a **floor** on the canonical aligned-continuation form where several entries share one label. So the wrap count is printed beside the findings, and an aligned line that *would* have opened a matching entry is reported as a **candidate** rather than a failure — counted, `--show`-able, and outside the exit status, on the arrangement `specificity_scan.py` uses for a flag on a `NOT FOR ENTRY` line.

**Counts only by default**, on `filled_vitals_census.py`'s and `specificity_scan.py`'s terms and for their reason: a run directory under `scratch/` or `output/` is a patient record, and a GAPS entry names what an encounter did not supply about a person. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for an F1 to F3 violation, **2 for every way of not having scanned**, including **no tier block in any note read**. That last limb is the one that matters, and it is the limb `differential_scan.py` was given for the same reason.

**Run it against `fixtures/filled-anchor/notes` and it exits 0 over twelve notes, which is worth knowing before reading a later non-zero as breakage** — `differential_scan.py`'s precedent, and unlike that tool this one can read the set, because F1 to F3 live in the tier block rather than in a differential. Measured 2026-08-16 and **pinned by a test**, which is the whole reason it is written here: **both of this scanner's parser bugs were caught by pointing it at that directory**, and neither by the synthetic fixtures. The first version matched a label case-insensitively, so `Unknown whether the patient smokes.` opened a section; the second allowed a label at any indent, so case 11's wrapped `DERIVED line. Lands in the overweight band` re-opened a section and swallowed the `Race/Ethnicity` line 32 lines below, scoring two F3 failures on a set that has none.

Covered by `tools/test_block_scan.py`, which builds synthetic blocks in that file and a temp directory — **there is no committed `clinical-note` *run* whose tier block this could be tested against, and there will not be one**, so `fixtures/filled-anchor/notes` is the one real set it is pointed at. Two shapes are pinned deliberately, because the whole reading rests on telling them apart: an entry that **opens** with a field name, and a wrapped line that merely mentions one. One class reads `skills/clinical-note/SKILL.md` and asserts the rules it checks are still written there, on `test_spelling_scan.py`'s reasoning.

### Word documents, both directions

`practicum-case-study` reads faculty material that arrives as a `.docx` and submits a `.docx`, so the pair exists. **Both are stdlib only** — a `.docx` is a zip of XML parts, which `zipfile` and `xml.etree` open for nothing.

```bash
python tools/docx_read.py <file.docx> [--normalize] [--outline]
python tools/docx_write.py <in.md> <out.docx>
```

**PyMuPDF was the obvious guess and it is the wrong tool**, asked and answered once so it is not re-litigated: PyMuPDF reads and writes PDFs, and no PDF library authors a Word document. The five tools here that carry a dependency all open a PDF; this is not a sixth. **That matters because a consumer runs Python on this path** — [AGENTS.md](AGENTS.md)'s point about `icd10_lookup.py`, arriving at a second skill.

**`--normalize` is the limb worth knowing about, and it exists because the evidence dump is booby-trapped.** UpToDate salts its rendered pages with homoglyphs — a Cyrillic `с` inside `cervicitis`, a Greek `ο` inside `infection` — so a paste of a topic is not searchable by the words it visibly contains. A `grep` for `cervicitis` over a paste of the cervicitis topic misses most of its occurrences **and reports a clean zero rather than an error**, which is this repo's recurring shape one more time: a search that could not have worked, answering like a settled negative. The map is deliberately narrow — letters only, and only the ones observed in the corpus — because folding every confusable would corrupt genuine non-Latin text.

**The writer's Markdown subset is small on purpose**, and the one rule in it that is not cosmetic is that a heading beginning `References` — or the singular `Reference` — switches every following paragraph to a 0.5 inch hanging indent, and itself centers and opens a new page. That is APA 7, and the rubric gives APA format 5 of 100 points. **The rule and its manual section live in [apa7.md](skills/practicum-case-study/reference/apa7.md), not here** — that sheet is verified against apastyle.apa.org and carries the caveat that the *Publication Manual*'s own section numbers are pointers rather than checked claims, because the manual is not in this repo. Restating a section number here would drop the caveat and leave a citation nothing re-derives, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143). Page setup is Times New Roman 12 pt, double spaced, one inch margins, with a page number top right from `word/header1.xml`, and every heading level at body size distinguished the way APA distinguishes them.

**That table held nine rows then, and five of them landed on [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217), which was filed asking for three.** The count is bound to #217's own table on purpose — it is eleven applied and four unapplied today, and stating a live figure here is what the paragraph below is about. The other two are the ones worth keeping: the singular `Reference` was **a gap the APA sheet created** — `apa7.md` §1 blesses it for a one-entry list while the renderer matched `references\b` and silently dropped the indent — and the heading-size row was filed as *worth a decision rather than a fix*, went to the clinician, and came back wider than the row. **The measurement discipline is the reusable part**: every row on that ticket, in both directions, was taken by rendering a document and reading `word/document.xml` and `word/styles.xml` rather than by reading the source, and the table in `apa7.md` §6 says so beside itself. What the renderer still does not do is written down in the same two places — because *"Page setup is APA 7 student paper"* standing unqualified in a docstring is what let three rows sit unnoticed.

**[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) closed both halves of that on 2026-08-19, and the second half is the reusable one.** Its two mechanical rows landed — a 0.5 inch first-line indent on body paragraphs and nowhere else, and APA's horizontal rules on a table instead of a grid, ruled unconditional by the clinician rather than switchable because the only consumer of this renderer is an APA document. But *"the same two places"* was the defect: a code regression fails a behavior test, and **a prose edit to either copy failed nothing**, so the two could disagree silently and the reader misled was whichever one checked the file nearer to hand. The list is `docx_write.NOT_APPLIED` now, one object, on `REFERENCE_HEADING`'s precedent, and a test asserts `apa7.md` §6 names the same items in both directions. **What that cannot reach is whether a row's verdict is true** — a row moved into the *applied* table while the renderer still does not apply it is invisible to it, and stays a behavior test's job, which is why both new rows got one. **The count of what is left is deliberately not stated here**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms: it is `NOT_APPLIED`'s to say, and this paragraph is a fourth place for it to go stale in.

**Adding the header part is what those tests were built for, and it moved them.** A part that is referenced and missing, or present and undeclared in `[Content_Types].xml`, is a file Word declines to open and nothing else here can see — so `test_docx.py` now walks both directions between the archive and its content types, and resolves every `r:id` in `word/document.xml` against `word/_rels/document.xml.rels`. **`docx_read.py` reads `word/document.xml` and no other part**, so the header is invisible to it; that costs nothing only because a `PAGE` field is not prose, and a test pins the round trip still returning every word the writer was given.

**Exit status distinguishes not having read from having found nothing** — 0 for text, **2 for every way of not having read**: no argument, no file, a file that is not a zip, a zip with no `word/document.xml`. A document whose text lived in a part the reader does not know about would otherwise print nothing and read as an empty document.

`docx_read` prints whatever the document held and there is no `--show`, because there is nothing general to redact — the caller knows what it opened. Where that is faculty material about a patient, its output is PHI on `harvest_review.py`'s terms.

Covered by `tools/test_docx.py`, one file for the pair the way `test_icd10.py` covers its builder and reader together. **The round trip is the test**: a `.docx` Word refuses to open is byte-for-byte indistinguishable from a good one until Word opens it, and there is no Word here — so what the tests assert is that the archive carries the parts the format requires, that every part parses as XML, and that the reader gets back what the writer was given. That catches the failure that actually happens, an unescaped `&` or a malformed part, and does not catch the one that cannot be checked without Word.

### Research ledger

The five tools above that take `<a run directory>` read a finished run. This one reads a `practicum-case-study` run's
**working file**, before the draft exists, and it is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) — the research fan-out made a mechanism rather than an instruction.

```bash
python tools/research_ledger.py <a ledger file>
```

**The ticket's own framing is what shaped it.** The first run wrote four unsourced claims into a
graded document and listed them in `PROPOSED` with **verify this** against each; the clinician's
ruling is that such a claim gets researched, one agent per claim, in parallel. `SKILL.md` already
said so. **What a written instruction cannot do is fail**, so the fan-out now writes one record per
claim into `scratch/case-study-claims.md` and this grades them.

**The rows belong to three rulings.** #214's contract: every field present, `STATUS` one
of two branches, an `unsourced` record saying what was searched, no citation field on an unsourced
record, a restatement that is not the claim pasted back, and a numeric claim answered with a number.
#215's amended recency rule: `RECENCY` one of four dispositions, a reference stating a year, an old
one saying why it stands, and the excuse carrying a reason. #231's citation rows, below. The report
prints the ticket beside each row, and **`skills/practicum-case-study/SKILL.md` step 3 writes every one of them out in a table** —
a test keyed on the module's own tuple fails if the next one arrives without one, because `AGENTS.md`
classes this as a tool a skill *names* rather than one it depends on, and that class is defined by
the instruction being complete without the command.

**An unrecognized `STATUS` is a failure, and that departs from `specificity_scan.py`'s third-branch
rule deliberately.** There the keyword picks a message and policing a third would be inventing a
rule the skill does not state. Here it picks **which tests run** — so a record reading
`STATUS: pending` skips every row below it and prints as clean, which is the silent-pass shape the
whole directory exists for.

**The numbers are deliberately not compared, and that is the sharpest limit.** The restatement is
written in the source's own terms *by design*, so a claim about a white count of 15,000 is rightly
answered with a range in `10^9/L`, and a digit-matching test would refuse the correct answer. What
the row can reach is that a numeric claim came back **quantified at all** — the wrong-citation
failure at its most expensive, and the one form of it a string test sees. Whether the source is
reputable and whether it says what the record says it says are both readings. **A clean scan is not
a checked claim**, and `skills/practicum-case-study/SKILL.md` says so beside the command.

**Counts only by default**, on `specificity_scan.py`'s and `block_scan.py`'s terms and for their
reason: the ledger lives under `scratch/` and a claim is transcribed from faculty material about a
patient. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a
violation, **2 for every way of not having scanned**: no argument, no file, no `## CLAIM:` record,
and **no `DATE:` header**. That last limb is the one that matters and it is `filled_vitals_census.py`'s
reasoning: the five-year window is measured against the day the paper is written, so a ledger with no
date was never measured by it and a clean report would read as though it had been. **Two rows need
that date since #231**, not one — the window, and whether a source was read after the paper was
written. **Where a
violation and a missing `DATE` both hold, 1 wins**, on `differential_scan.py`'s ordering, and the
banner prints beside it so the finding reads as a floor. **The first version returned 2 there** —
found by review, and it was the one place this departed from both siblings without saying so.

**Two more rows came out of that review and are worth keeping.** An unrecognized `RECENCY` was
passing silently while an unrecognized `STATUS` failed, and the argument for the second is the
argument for the first — the field gates the row below it. And `n.d.` was refused outright, **a rule
the clinician never made**; the escape hatch is now the one he did make, so an undated source
carrying `nothing newer` or `guideline in force` with a reason stands.

**Open question 2 is settled on [#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231),
and the answer is that no tool here touches the network.** The *format* half already had a written
standard from #211 ([apa7.md](skills/practicum-case-study/reference/apa7.md), walked by `practicum-case-study` step 7 and by
#218). For the *truth* half the ticket proposed `threshold_sheet.py`'s two-tier arrangement — a
resolver opting into the network, skipping with a banner. **Two findings killed it, and the second is
the clinician's.** UpToDate **dominates** this corpus's references and is subscription-gated, so
a fetch reaches a login wall rather than the topic page `apa7.md` §2 takes the date element from:
every such entry would fail outright, or **pass on a 200 from a login form**, which is the silent-pass
shape this whole directory exists to refuse. And the clinician hands the topics over wholesale, so
wherever a source is in the evidence dump there was never anything to resolve.

**So the checking moved to where the reading already happens, in two halves.** The agent that
researched a claim was on the page, so it records what it opened and when (`RESOLVED`) and the year
the page itself carries and where (`PAGE-YEAR`); a **second** agent, briefed to *refute* rather than
to confirm — because an agent asked *is this right?* says yes — records what the attempt found
(`REFUTATION`). Ten rows grade the three fields offline. The residue this reaches is the
**non-UpToDate** references: a `practicum-case-study` step-3 record only exists because the evidence dump did *not* cover
the claim, so the sources here are the ones nobody has.

**A wall is not an absence, and the clinician split decision 4 on that line, 2026-08-19.** A locator
that 404s or names a document a search cannot find is `refuted` and **fails**. A live page whose
title and authors match the entry, body behind a subscription, is `paywalled` and **passes** — the
URL resolving to the right document is itself evidence it exists, which is most of what a fabricated
citation cannot do. **It is the weakest disposition that passes**, so the report counts those
records on their own line rather than letting a clean exit stand for them. The alternative fails
every UpToDate record, which is most of this corpus and the reason there is no resolver here.

**How dominant is measured once, and deliberately not restated in the four places this reasoning
appears.** [style.md](skills/practicum-case-study/reference/style.md) §10 puts it at *roughly* nine
in ten across ten graded submissions, and that working set is **gitignored** — so nothing committed
re-derives the figure and no test pins it. It is load-bearing here, being the reason no resolver was
built and the reason `paywalled` passes, which is why the hedge travels with it. This branch first
published it flat in five new places and was caught by its own tracker sweep: [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
shape arriving inside the change that cites #143.

**Not exempt by source class, and that was decided rather than defaulted into.** `tertiary reference`
is UpToDate, which the clinician has wholesale — but for exactly the reason above, an UpToDate
reference reaching *this file* is a topic he does not have. Exempting the class would exempt the
records that need the rows most.

**What the two halves buy is not the same thing.** `RESOLVED` and `PAGE-YEAR` **narrow** the hole:
an agent can write a URL it never opened, but it has to commit to specifics a reader can be caught on
in one click, where a correctly formatted APA entry is checkable only by going and looking. The
refutation pass is the only **verification** in the arrangement — **and it does not happen in this
module.** The pass is a second agent; what the module does is refuse a record where the pass did not
answer, answered in a third word, or answered by pasting the restatement back. **No row can see that
the refuter was a different agent**, or that it opened anything, which is #214's *what a written instruction cannot do is fail* binding its
own successor. The one shape a row reaches is a refutation that is the restatement pasted back.
**This module still checks that a year is stated and that two records agree about it. It opens
nothing.**

**Nothing committed can be pointed at it, and there will not be one** — a ledger is a patient record
by `scratch/`'s own terms, which is `differential_scan.py`'s position exactly. So
`tools/test_research_ledger.py` builds synthetic ledgers, and the one thing it reads from the tree is
**the skill's own worked example, which it runs the scanner over**. A documented record shape the
grader would refuse teaches the next run to write a ledger that fails, and every substring test in
that class would still be green.

### Reference scan

The research ledger reads a `practicum-case-study` run's working file before the draft exists. This one reads the **finished draft**, and it is [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s mechanical half.

```bash
python tools/reference_scan.py <a draft .md> --as-of <YYYY-MM-DD>
```

**The ticket's third decision asked whether the post-draft checks should be a fan-out or a tool, and answered itself: an agent is only needed where the check is a reading.** Differential ordering and discriminator quality are readings and stay agents, spawned by `skills/practicum-case-study/SKILL.md` step 9. A reference list mostly is not, so it is this — #214's *both* arrangement arriving at the second half of the same skill: the rules are written out in full in `skills/practicum-case-study/SKILL.md` step 7's defect table, **and** a command grades them.

**How many rows is `reference_scan.KINDS`'s to say and is deliberately not restated here** — a count in prose that nothing re-derives is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143), and this section had one before the sweep that wrote it caught it. What is worth knowing is that **two of the rows exist because the renderer created the failure.** Since [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217) the heading is what *applies* the hanging indent, centers the label and breaks the page — so a wrong label is no longer only a grader's deduction, it silently changes the layout, and the failure is one a reader of the Markdown cannot see. And `docx_write.body_xml` sets **every non-blank line as its own paragraph**, so a hard-wrapped entry renders as two paragraphs and the second hangs on nothing. This parser reads the list the way the renderer will, which is what lets a wrap be reported rather than absorbed.

**That sentence read *exactly the way the renderer will* and was false when it was written, which is the finding worth more than the fix.** The parser treated a deeper heading as a note inside the list and `body_xml` ends the list on **any** heading, so a list split by a `### Note` was read as two entries and graded clean while the renderer set the second one flush with no indent — the silent layout failure the heading row exists for, passing as clean, under a sentence asserting it could not. And detection was a hand-typed list of labels rather than the import, so `References and Resources`, which the renderer *does* style, exited 2 as *no reference list found*. Both were found by the tracker sweep on [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) — whose subject is exactly a generalization made from the files a pass had open — and both were re-derived by **rendering a document and counting the styled paragraphs**, not by reading the renderer's source. A test now asserts the two agree on where a list ends by running both.

**The heading matcher is imported from the renderer rather than restated**, and that is the load-bearing line. `docx_write.REFERENCE_HEADING` is a module constant now; a scanner holding its own copy of that rule could pass a document the renderer sets wrong, which is the one failure the row exists to catch. A test asserts the two are the same object.

**Two rows are narrowed on purpose, and both narrowings are visible in the code.** A retrieval date is refused only on an entry carrying a **DOI** — the work stating that an archived version of itself exists, which is APA's own test failing. A society guideline PDF also takes no retrieval date and nothing in a URL distinguishes one from a page designed to change, so that direction stays a reading. And the database name is matched as a **word and never as a hostname**: `uptodate.com` in a URL is not the name being set in the entry. That second one was wrong first — the lookahead refused any following period, so `UpToDate. Retrieved ...`, which is the ordinary compliant form, read as no name at all and the italics row could never fire. Caught by the test written for it.

**What no row here reaches** is whether the source exists, whether it says what the sentence citing it says, and whether the year on the page is the year in the entry. That last is [#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231), and it is **answered before the draft exists rather than here** — `research_ledger.py` grades the year an agent read off the page against the year in the entry. **It needed no network**, which is the opposite of what this sentence said when the two branches were written a day apart: a fetch reaches UpToDate's login wall and passes on a 200. So neither module sprouts a URL fetcher, and not because the work was deferred. **A clean scan is not a checked reference list**, `skills/practicum-case-study/SKILL.md` step 7 says so beside the command, and a test asserts that sentence is still there.

**That list is `reference_scan.NOT_REACHED` now rather than a paragraph, and it is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s repair arriving one artifact over** — [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241). It sat in this module's docstring *and* in [apa7.md](skills/practicum-case-study/reference/apa7.md) §7, and a **prose** edit to either failed nothing, so the reader who was misled was the one who checked the file nearer to hand. One object, and a test asserts the sheet names the same items in both directions. **How many rows is that tuple's to say and is deliberately not restated here**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. What it cannot reach is whether a row's verdict is *true*: a row moved out while the command still gained nothing is invisible to it, and stays a behavior test's job.

**#241's own row was ruled a permanent reading rather than left open, and the declined option is the part worth keeping.** A retrieval date belongs only on a work designed to change that is cited unarchived, so a guideline PDF, a journal article, a USPSTF statement and a textbook take none — and the command refuses one **only on a DOI**, which is that test failing in the one place an entry string states it. The proposal was to join each entry to its `research_ledger.py` record and read the `SOURCE` class off it, the only candidate needing no new authored data, since a record's `REFERENCE` field *is* the APA entry. **It was priced and declined on a measurement rather than on cost**: `peer-reviewed` and `society guideline` map onto that list cleanly, while `government` covers a USPSTF statement, which takes no retrieval date, and a public-health page designed to change, which takes one, and `tertiary reference` covers UpToDate and a textbook, which take opposite answers. **A row keyed on either of those two fails a correct entry**, which is `guidelines_catalog.py --draft`'s refusal to derive a population arriving at a second artifact — *a guessed answer here is worse than a blank one*. **How many of the classes settle it is `reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`'s to say and is deliberately not counted here** — this sentence stated the number, and so did the sheet and the module's docstring, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside the change whose subject is a list that had been copied into two. **The same change withheld the row count one sentence earlier on #143's terms and then stated this one**, which is the finding rather than the fix, and it was caught by `/code-review` and by the tracker sweep independently. A test asserts that mapping's keys are exactly `research_ledger.SOURCE_CLASSES`, so a fifth class fails rather than leaving a ruling made over four standing unqualified in three files.

**What makes that a ruling rather than a shrug is that the reading is graded, and the mechanism landed while the ticket sat.** [#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240) put `checks_ledger.py` in front of `skills/practicum-case-study/SKILL.md` step 9's fan-out, and its `EXPECTED_CHECKS` already carried the row `the reference list, the part no command reaches` — so naming this direction in that row's reader column is a one-line edit that makes a run fail when it returns no verdict on it. #214's *what a written instruction cannot do is fail*, which is the objection option 3 had to answer before it could be closed rather than deferred. **A test pins the chain end to end** — the sheet names the reading, the step names it in the row, and the grader expects that row by name — because a rename in any one of the three would otherwise rot the arrangement in silence.

**Counts only by default**, on `research_ledger.py`'s and `block_scan.py`'s terms — and **`--show` output is safe to paste**, which is the only `--show` in `tools/` whose output may be pasted whole — every sibling scanner's is PHI, and `guidelines_recs.py`'s is restrained instead by copyright, *a line into a ticket, never a table*. Ruled by the clinician on 2026-08-19, #218's decision 1 and the last thing that ticket was open on; the provisional posture here was the stricter of the two taken whole, and it is retired.

**It is not a carve-out from standing rule 1; it is a statement about where the label attaches.** The subagent rule above attaches PHI to the *file* a subagent read. The scanner's case is different in a way that is checkable: **its output cannot contain patient data, because of what the code is able to draw from** — every finding detail is a reference entry, a heading, a date, or a cited author's surname and year. **That was measured rather than argued**, twice and against two different drafts: the clinician's own probe, a draft carrying an age, a last menstrual period, a temperature and a differential entry with every body line salted, and then the committed one — a draft built to fire **every row the module has**, every body line salted, run through `format_report(..., show=True)`. Zero occurrences of the marker in either. **The count is deliberately not stated and the test asserts a floor rather than an equality**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms: a sixteenth row this draft does not happen to fire is not a reason for the suite to go red, and a number here would be stale the day it arrives.

**There is exactly one aperture onto the body and it is named rather than left implied**, because the unqualified form of the claim is a notch stronger than the measurement. The two citation rows emit a **citation key**, and a key is the first word of anything the body writes in the shape `(Word, 2024)` — so one capitalized token of the draft's prose does reach the report. It is a citation author by construction and never the sentence around it, which is the element the ruling blesses in as many words, and a test drives the marker through it and pins that what comes out is a token and a year.

**So the property is pinned rather than described, because the ruling rests on it.** `reference_scan.BODY_ROWS` declares the rows that read the draft's prose at all, and both directions are asserted against it: every declared row fires on the salted draft, and no `Finding(...)` in the module carrying a literal `"body"` is missing from the tuple. **A fifth body row cannot arrive quietly**, which is where the next author reads the ruling.

**The completeness half is an AST walk, and it is a walk because the first version was not.** Both directions were measured against *the rows one fixture happened to fire* — so a fifth body row that was neither declared nor written into that draft left every assertion green, a check that could not have seen the thing it was named for while reading as a settled negative. That is `test_console_codec.py`'s instrument adopted for `test_console_codec.py`'s reason, and it reads `where` positionally **and** by keyword, since either spelling builds the same finding. Caught by `/code-review` on the branch that landed the ruling, and mutation-tested in both spellings before it was believed.

**And it does not widen.** A reader spawned by [practicum-case-study](skills/practicum-case-study/SKILL.md) step 9 is a language model summarizing clinical prose in its own words, with no equivalent guarantee available, so it still reports **where and what** is wrong and never the sentence — ruled unchanged on the same day. `research_ledger.py` is untouched: a ledger record is a claim transcribed from faculty material about a patient. **Nor is `checks_ledger.py`, which grades those same readers' records** — the reader's own words, one file later, so the ruling that does not reach the reader does not reach the file it writes into either. Nor does it reach `block_scan.py`, `specificity_scan.py`, `differential_scan.py`, `anchor_scan.py` or `filled_vitals_census.py`, which all read note text or measured values directly; their `--show` output stays PHI.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a defect, **2 for every way of not having scanned**: no argument, no file, an unreadable `--as-of`, **no reference list found in the document**, and **a heading with nothing under it**. Those last two are the limbs that matter, and they are `differential_scan.py`'s reasoning: a draft whose list was headed something this cannot recognize would otherwise report zero defects and read as a clean list.

**`--as-of` is the exam date and a missing one is exit 2**, which is `research_ledger.py`'s dateless-ledger arrangement rather than a new rule. One row needs it — the retrieval date must be on or after the day the paper is written — and the window is measured against that day and never against the clock, so a draft graded twice a year apart grades the same both times. **Where a defect and a missing exam date both hold, 1 wins**, on `differential_scan.py`'s ordering, and the banner prints beside it so the finding reads as a floor.

Covered by `tools/test_reference_scan.py`, which builds synthetic drafts in that file and a temp directory — **there is no committed case study and there will not be one**, because a finished draft lives under `output/` and is written about a patient, which is `differential_scan.py`'s position exactly. The one thing it reads from the tree is **the skill's own worked reference list, which it runs the scanner over**: a documented list the scanner would refuse teaches the next run to write one that fails, and every substring test in that class would still be green.

### Post-draft checks

The reference scan reads a `practicum-case-study` draft. This one reads **the record of the readers who read it** — `scratch/case-study-checks.md`, the second fan-out's file — and it is [#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240).

```bash
python tools/checks_ledger.py <a checks file>
```

**The ticket is an asymmetry rather than a defect, and that is the whole argument for building it.** That skill has two fan-outs and they are one mechanism: N agents, one record each, into one Markdown file, headings written first, one writer. **[practicum-case-study](skills/practicum-case-study/SKILL.md) step 3's fan-out got a grader on [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) and [practicum-case-study](skills/practicum-case-study/SKILL.md) step 9's did not**, so the second one's record shape was held by exactly what the first one's was held by before `research_ledger.py` existed — a sentence saying so, and a line in a by-eye checklist. #214's *what a written instruction cannot do is fail* transfers whole, and it transfers to the fan-out with **less** protection.

**Two cheaper answers were priced first and both were refused.** Extending `research_ledger.py` shares no field name with it — `CLAIM`/`STATUS`/`SOURCE` against `CHECK`/`VERDICT`/`FINDINGS` — so the module would have to dispatch on which file it was handed, and its exit-2 *no `## CLAIM:` record* limb would stop distinguishing an unreadable ledger from a checks file. Declaring the absence in `SKILL.md` on [#164](https://github.com/mshamblin5150-code/clinical-skills/issues/164)'s terms costs one sentence and leaves the three silent-pass shapes standing. The clinician ruled the tool, 2026-08-19.

**One of its rows is stronger than anything `research_ledger.py` has, and how many rows there are is `checks_ledger.KINDS`'s to say rather than this paragraph's.** That grader has no expected count and says so, so three records where eight claims went out grade clean. Here the check table in `skills/practicum-case-study/SKILL.md` step 9 **fixes the set**, so a reader nobody spawned is a finding rather than a hole. The other four are the sibling's arguments arriving one file later: no check recorded twice, every heading carrying a `VERDICT`, `VERDICT` one of two words — a third is a failure because the field picks which rows run — and a `defect` saying what and where, which is `specificity_scan.py`'s substance test.

**The vocabulary is held in the module and derived in the test**, because a run directory is not a checkout and nothing at run time can read `SKILL.md`. `tools/test_checks_ledger.py` parses that table and asserts the tuple is it, which is `spelling_scan.py`'s arrangement with the conventions table and is there for its reason: a scanner holding a different answer than the file a reader opens is worse than none, because it reads as agreement.

**One shape the ticket names is deliberately not a row, and it is named rather than left implied.** `VERDICT: clean` with an empty `FINDINGS` is [#182](https://github.com/mshamblin5150-code/clinical-skills/issues/182)'s *a block satisfies the gate by existing*, and no string test reaches it — a check that ran and found nothing writes what a check that reported nothing writes. #240 concedes it in the word *indistinguishable*. Reaching it means requiring a `clean` to say what it examined, which is a change to what the step asks a reader to write rather than a grader of what it already asks.

**Counts only by default and `--show` is PHI**, on `research_ledger.py`'s terms — the file lives under `scratch/` and a finding describes a draft written about a patient. **The one thing the default report names is a missing check**, and the string comes from the module's own tuple rather than from the file, so it draws on nothing the run wrote; a heading **outside** the table is counted and never named, because that string is the run's own text. That is `reference_scan.py`'s *what the code can draw on is bounded* used at the narrowest width it has been used at, and it is not this tool's `--show` becoming safe to paste.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a violation, **2 for every way of not having scanned**: no argument, no file, and **no `## CHECK:` record in it**. That last limb is `differential_scan.py`'s reasoning, and there is no dateless limb here because nothing in this file is measured against a date — the one row of `research_ledger.py`'s arrangement that does not transfer.

**What it cannot reach is every verdict in the file.** Whether the differential's `1.` is what would kill first, whether an MDM entry's discriminator is from this case, whether the reader opened the draft at all. A well-formed `clean` from a reader that skimmed is what a well-formed `clean` from a reader that read looks like. **A clean scan is not a checked draft**, `skills/practicum-case-study/SKILL.md` says so beside the command, and a test asserts that sentence is still there.

Covered by `tools/test_checks_ledger.py`, which builds synthetic checks files in that file and a temp directory — **there is no committed checks file and there will not be one**, on `test_differential_scan.py`'s position: a reader's findings describe a draft written about a patient. The one thing it reads from the tree is **the skill's own worked record, which it runs the scanner over**.
### Tracker scan

Every tool above reads something this repo wrote into a file. This one reads **what a public flip publishes that a file scanner does not**, and it is [#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212)'s remaining surface made runnable. `phi_scan --all` walks `git ls-files`, which is the tip and nothing else; #212's ruling comment was blocked on issue and pull-request text, pull-request diffs, and commit messages, and [#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104) records the last of those as scanned by nothing.

```bash
gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" > scratch/tracker-issues.json
gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" > scratch/tracker-comments.json
gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" > scratch/tracker-reviews.json
python tools/tracker_scan.py --harvest scratch/tracker-*.json

git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"
python tools/tracker_scan.py --commits --history --paths
```

**It opens no socket**, which is `research_ledger.py`'s ruling adopted whole rather than a fresh one: the fetch is a documented `gh` command whose output is a file, so the scanner stays offline, stdlib-only and testable, and the harvest is a thing a reader can keep and re-scan.

**Into `scratch/`, and that is not tidiness.** The harvest is the tracker's entire text, so a finding is *in the file you just wrote*. `scratch/` is the firewall's own directory — gitignored, and `phi_scan`'s path layer refuses to commit from it even under `git add -f`. Anywhere else in the tree it is a file full of tracker prose one `git add -A` from being tracked with no net under it, which is [#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176) and [#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223)'s subject arriving on a file this tool tells you to create.

**Four limbs against #212's three surfaces, and the mapping is deliberately not one-to-one.** `--history` reads every **blob** reachable from a ref, and that is the pull-request limb: a merged pull request's diff is made of blobs, every one reachable once the merge lands. It is also the limb `phi_scan` cannot reach at all, because a file deleted or rewritten five commits ago is not in `git ls-files` — **which is why #212's own scan had to be hand-written and why the figures it published were re-derivable by nothing.** `--paths` is the fourth and #212 never asks for it; it is here because a filename is published too and costs one `rev-list` to read.

**A record cannot exempt itself and a file can, which is the one asymmetry here that is not `phi_scan`'s.** `scan_lines` was split out of `scan_text` for it. A blob **was** a file that somebody reviewed, so `--history` honors a `phi-scan: synthetic` declaration exactly as `phi_scan` does; an issue body was typed by whoever opened the issue and may not. The argument is not hypothetical — **the finding this tool was built to catch is a ticket about the `dob` shape that quotes a real one**, so the record most likely to carry an identifier is exactly the record that would have carried the pragma. `Record.is_file` is which, and it is the only thing that field decides.

**Reachability is the boundary of publication, and it cuts both ways.** #212's scan walked `git cat-file --batch-all-objects` — every object in the local database, including ones no ref reaches. Those were never pushed, so a finding in one is not an exposure, and here the unreachable set carries findings the reachable set does not. **And the same walk under-reads**: a pull request whose branch was deleted after merging keeps its head at `refs/pull/N/head` on GitHub, which an ordinary clone does not fetch. **So a default clone is wrong in both directions at once and both directions are silent** — which is why `--commits` and `--history` refuse until a pull-head ref is present, printing the fetch command, and why `--history` prints the unreachable blob count beside the reachable one. **The figures are deliberately not restated here**: they are what the command prints, they move on the next commit and on the next `git gc`, and one such number copied into prose is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) and [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) at once. A first draft of this section stated them and was caught in review.

**What it cannot reach, named rather than left to be discovered, and two limbs of it have already cost something.** A commit pushed and then force-pushed away is reachable by SHA on GitHub and by nothing here. A harvest goes stale the moment anybody comments. **GitHub keeps a previous revision of every edited issue and comment and serves it to anyone with read access, and the API exposes no way to read or delete one** — so a redaction this tool prompts is not the same as the text being gone, which was found *after* the flip and ruled acceptable by the clinician on 2026-08-19. And **a date rewritten into a format the corpus does not hold escapes the corpus layer entirely**: one real day file's date, with slashes and a four-digit year, sits in two commit messages where it reads as an ordinary shape hit beside a hundred census ratios. **That was found by reading the shape-layer output, not by the corpus layer**, and no widening of the literal set fixes it — the corpus holds the string that was typed, and a paraphrase of a date is still a date. **Writing the literal into this paragraph was the first draft and the hook refused the commit**, which is `differential_scan.py`'s #153 and `spelling_scan.py`'s homoglyph map a third time: describing the defect reproduced it.

**Counts only by default**, on `phi_scan.py`'s terms and for its reason: a finding here is a patient identifier. **`--show` output is PHI**: read it, do not paste it. Deliberately **not** `reference_scan.py`'s exception — that module's output is bounded by what its code can draw from, and this one's is bounded by nothing, because it reads whatever anybody typed.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a finding, **2 for every way of not having scanned**: no surface named, a harvest file absent or not a JSON list, no record in any surface, a git command that failed, no pull-head ref without the acknowledgment, and no corpus without `--allow-no-corpus` or `clinical.phiAllowNoCorpus`. **Where a finding and a not-scanned limb both hold, 1 wins**, on `phi_scan.py`'s own ordering — and **the first version got that backwards for the corpus limb**, returning 2 before scanning at all, so a real `dob` hit was suppressed and reported as *did not scan*. Its own test class stubbed the corpus check out, so nothing in the suite could see it; `/code-review` found it. A `git` failure gets its own exception for the same reason: `for-each-ref` returning nothing because it failed reads exactly like a repository nobody has fetched the pull heads into.

Covered by `tools/test_tracker_scan.py`, which builds synthetic harvest files and throwaway checkouts in a temp directory on `test_skills_mirror.py`'s arrangement. **The real tracker is deliberately not a fixture** — it is fetched over the network and changes every time anybody comments, and #212 carries three sweeps whose surface figures disagree with each other for exactly that reason. A test keyed on it would be measuring the day it ran, so no count of issues, pull requests or blobs is asserted anywhere in it.

### Tracker bodies

The tracker scan reads what the tracker *says*. This one reads **whether a record says anything at all**, and it is [#130](https://github.com/mshamblin5150-code/clinical-skills/issues/130) — eight records in this repo whose body is the literal two characters `@-`.

```bash
gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" > scratch/tracker-issues.json
gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" > scratch/tracker-comments.json
python tools/tracker_bodies.py scratch/tracker-issues.json scratch/tracker-comments.json
```

**It opens no socket and writes into `scratch/`**, both on `tracker_scan.py`'s terms and for its reasons: the fetch is a documented `gh` command whose output is a file, and that file is the tracker's entire text.

**The ticket's decision 2 was answered in prose four days before it was asked, and the bodies kept being lost.** `docs/agents/issue-tracker.md` has carried `--body-file -` and the read-back since 2026-08-11; #130 was filed on the 15th, and comment 17 records four *more* bodies destroyed on 2026-08-19 through a second door — `gh api -f body=@-`, where `-f` takes a literal and only `-F` resolves `@`, so `gh` writes the two characters and exits 0. That is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written instruction cannot do is fail*, arriving at the tracker. **Decision 3 — is a body ever legitimately empty — was ruled by the clinician on 2026-08-19: it is not**, so an empty body is a row rather than a counted-and-passed line.

**Three rows, and they are one question asked three ways: did text land.** The literal `@-`; an empty, whitespace-only, absent or JSON-null body; and a body that is one bare `@token`, which is what `--body @notes.md` writes. **The third row has zero instances across the tracker** and is grounded in the trap `issue-tracker.md` documents beside `@-` rather than in a measurement — which is exactly why it is the narrowest of the three and fires only when the *whole* body is one token, leaving `@someone please look` alone.

**Reading the `issues` REST payload rather than `gh issue list` is the ticket's own finding, and it is the reusable part.** That command **excludes pull requests**. Two of the eight are pull requests — #98 and #71 — so **every sweep that ran #130's own reproduce command re-derived *six, not eight*, and concluded the ticket's title was stale.** Thirteen comments say so. The title was right; the instrument could not see two of its members and had no way to report that it could not. This repo's recurring shape once more — a search that could not have worked, answering like a settled negative — arriving on the tracker rather than on a file, and surviving longer than any other instance of it here because each re-derivation *agreed with the last*.

**`tracker_scan.records_from_github` cannot be reused, and a test asserts why rather than the docstring claiming it.** That parser drops a body that is empty or whitespace — correct for a PHI scan, since there is no text to find — and that is precisely the record this module exists to report. So the duplication stays justified rather than merely inherited, and if the sibling ever starts keeping those records the test says so.

**No `--show`, because there is nothing to show, and the report is safe to paste.** Two rows fire on a body drawn from a fixed set and the third on a single token; a finding prints the row's own name and the record's URL and never the body. That is `reference_scan.py`'s *bounded by what the code can draw from* at the narrowest width it has been used at — **pinned by driving a marker through every aperture rather than argued**, and `format_report` is asserted to take no parameter that could widen it. **The first version of that assertion was a substring search for `--show` over the module and failed on the docstring paragraph explaining why there is no `--show`** — `spelling_scan.py`'s mention-versus-use problem arriving on a test instead of on prose, which is the third time describing a rule has broken the thing checking it here.

**Each branch of `grade` names its own row rather than assigning one to a variable**, which looks like repetition and is what makes the row set checkable: the completeness walk in the test reads `Finding(...)`'s first argument by AST, and a local variable is opaque to it. The first version assigned, so the walk went green on a set containing nothing but `None` — a check that could not see the thing it was named for, caught before it merged and mutation-tested in both the positional and the keyword spelling.

**What it cannot reach, named rather than left to be discovered.** **A body that landed and is wrong** — truncated at a shell metacharacter, half a heredoc, the right words about the wrong ticket — is a body with text in it and passes every row. A **double-encoded** body is [#155](https://github.com/mshamblin5150-code/clinical-skills/issues/155)'s cohort, and #130's own comment records the two as one class — *the CLI accepted something malformed and said nothing* — but that ticket is `grilling` with its row unruled, so it is a seam here and not a row. A harvest goes stale the moment anybody files. And a record edited to remove its body after filing reads identically to one that never had one. **A clean scan is not a body worth reading**, `docs/agents/issue-tracker.md` says so beside the command, and a test asserts that sentence is still there.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a lost body, **2 for every way of not having scanned**: no argument, a harvest file absent or unreadable, a payload that is neither a JSON list nor a JSON object, and **no record in any file read**. That last limb is `differential_scan.py`'s reasoning: an empty payload would otherwise report zero lost bodies and read exactly like a tracker that has none. **One unreadable file among several is 2 and not a partial scan**, on the same grounds.

**It is also the read-back, and that is one accepted shape rather than a second mode.** It takes a single JSON object as well as a list, so `gh issue view <n> --json number,body,url` piped in grades one record — which catches what `--jq '.body | length'` does not, since a lost body has a length of 2 and reads as a number rather than as a failure.

Covered by `tools/test_tracker_bodies.py`, which builds synthetic harvests in that file and a temp directory. **The real tracker is deliberately not a fixture**, on `test_tracker_scan.py`'s position: it is fetched over the network and changes every time anybody comments, so a test keyed on it would be measuring the day it ran. **No count of issues, pull requests or lost bodies is asserted anywhere in it** — the eight is what the command prints. One class reads `docs/agents/issue-tracker.md` and asserts the rules it checks are still written there, on `test_spelling_scan.py`'s reasoning.

### Skills mirror

`.claude/skills/` is how Claude Code loads these skills natively, and each entry is meant to be a **junction to `skills/<name>/`** so the mirror cannot hold a different answer than the skill does. It is gitignored, so nothing git does checks it.

```bash
python tools/skills_mirror.py            # report; exits 1 if anything is not linked
python tools/skills_mirror.py --repair   # relink everything
```

**Read the mirror and you may be reading a retired rule.** A junction that has become a copy looks exactly like a working install — same names, same files, same frontmatter — and it answers with whatever the skill said the day the copy was made. `.claude/skills/clinical-note/SKILL.md` in one worktree still carried *a known hypertensive seen for a productive cough gets a hypertensive pressure and a raised respiratory rate* after #23 removed it, and had no drift row 14. An agent that opened it instead of `skills/clinical-note/SKILL.md` would have followed the rule the ticket existed to delete.

**`git worktree` is how that happens here.** It materializes `.claude/` by copying, and the copy follows the junctions instead of recreating them, so a fresh worktree starts out holding frozen skills. **Every worktree needs its own `--repair`.** The pre-commit hook runs `--quiet` and warns, but the warning is **advisory and never changes the exit status** — this scanner cannot refuse a commit.

It reports paths and status words, never file contents, so its output is safe to paste. `--verbose` names the differing files and still prints none of them. Covered by `tools/test_skills_mirror.py`, which builds throwaway checkouts in a temp directory and never inspects or repairs the real one.

### Spelling scan

Standing rule 4 — American English, always — with a command in front of it. The table lives in [clinical-note](skills/clinical-note/SKILL.md) under *Conventions*; `tools/spelling_scan.py` is that table made runnable, and `tools/test_spelling_scan.py` parses the skill's copy and asserts the two agree, so the scanner cannot start holding a different answer than the file a reader opens.

```bash
python tools/spelling_scan.py --all      # every tracked .md
python tools/spelling_scan.py --record   # the preserved run record, form by form
```

**A form inside backticks is a mention; a form in running prose is a use.** That is the whole exemption mechanism, and it is deliberately not `phi_scan`'s: the unit is the span rather than the file, so **nothing can exempt itself by explaining the rule** — which two files once did to `phi_scan` merely by documenting its pragma near the top.

**One directory is exempt by path**: `fixtures/filled-anchor/notes/case-*.md`, which is day-b run 1 byte for byte **apart from two site names, redacted** — [the set's README](fixtures/filled-anchor/notes/README.md) states that edit once, with the count, and it is the whole of it. Its British spellings are the evidence for [#73](https://github.com/mshamblin5150-code/clinical-skills/issues/73) and are counted rather than refused — **the number is `--record`'s to state and deliberately not restated here**, because it moved twice on 2026-08-18 while the record stayed byte-identical — `--record` is what the set's README cites instead of restating, and the totals are pinned by a test so a tidy fails rather than quietly voiding the argument. The set's own README is **not** exempt: it is prose about the record, so it takes the mention rule like any prose.

**Advisory in the pre-commit hook**, alongside `skills_mirror.py` and on the same reasoning: a spelling is not worth refusing a commit over.

**Two things can refuse a commit here, and this is not one of them.** Standing rule 1 via `phi_scan.py`, and — since #83 — `threshold_sheet.py`, but only when a `reference/thresholds/*.md` is staged. This sentence and two others said *"standing rule 1 remains the only thing that refuses a commit here"* for one merge after that stopped being true, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape applied to a rule rather than a figure: the branch that added the second refuser did not sweep for prose asserting there was only one.

It prints a path, a line number and its own table's entry — **never the text it matched** — so its output is safe to paste, and there is no `--show`. Two limits worth knowing: it reads **Markdown only**, so commit messages and filenames are outside it, and it holds the table rather than the language, so a clean scan means no *listed* form was used.

### The run record's one exception

The claim the section above rests on — `fixtures/filled-anchor/notes/` is day-b run 1 byte for byte — was written unqualified across a dozen committed files, and the exception was stated in exactly one of them. `tools/test_run_record_claim.py` is [#221](https://github.com/mshamblin5150-code/clinical-skills/issues/221) made runnable: **every block that makes the claim must also say two site names were redacted.** No command; it is a test only.

**The count and the command that re-derives it live in [the set's own README](fixtures/filled-anchor/notes/README.md) and deliberately nowhere else**, which is why every qualifier this added names the redaction and not a number. Restating a figure in a dozen new places while repairing a claim copied into a dozen would be [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside its own repair, which is what `7fa8041` did one merge earlier.

**How wide the surface was is stated in the module's own docstring and deliberately not here**, for a reason the first draft of this section demonstrated: it published *sixteen blocks in twelve files*, and **this section's own paragraphs are blocks about the set**, so the figure needed mental subtraction the moment it was written and moves again on the next qualifier added. That is [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) inside the repair for #221 — caught by review, not by a check.

**The instrument is the finding here, and it is #221's own thesis landing on #221.** That ticket counted five files by grepping one spelling in one file type; a comment re-derived fifteen with `git grep -ln`. Both undercount, because a `git grep` for a phrase cannot see it **hard-wrapped across a line** — `tools/test_filled_vitals_census.py` opens with one — and cannot see it **split across two string literals**, which is how `spelling_scan.py` prints it to stdout, where no edit to a Markdown file reaches. So the comparison is against a whitespace-and-quote-normalized **block** rather than a line, and the real surface was wider than either count.

**A bare `run 1` was in the subject test and had to come out.** It matched `test_differential_scan.py`'s *"hedged-dx run 1's case 2 … it is a byte-for-byte run record"* — a **different** set, which commits no notes at all, so nothing was ever redacted from it and the claim there is true as written. What it cannot reach is written in the module docstring: a block naming neither `filled-anchor` nor `day-b` is invisible, two such blocks existed, and both were rewritten to name what they are about.

### A cited step has to exist

A skill's steps are numbered headings — `### 4. Draft the body` — and reference sheets, other skills and `tools/` docstrings cite them **by number**. Insert a step and every one of those citations is wrong, silently, and a reader following a cross-reference lands on a different step and gets a coherent, wrong answer. `EveryCitedStepResolvesToADeclaredStep` in `tools/test_skill_agreement.py` is [#233](https://github.com/mshamblin5150-code/clinical-skills/issues/233) made runnable. No command; it is a test only, on `test_run_record_claim.py`'s terms.

**Two renumberings in a week and only one was clean**, which is the argument for it. `setup-clinical-skills`'s silently redirected `reference/voice.md`'s citation. `practicum-case-study`'s on #214 moved seven citations across five files and all seven re-derive correct **because the author went looking with a `grep`** — nothing required that, and nothing would have failed if one had been missed.

<!-- unresolved-step-citations: 1 -->

**The resolver has three limbs and every one was forced by a real line.** A skill named immediately before the words wins; otherwise a bare `step N` carries the subject of the citation before it, **unless another skill was named in between**; otherwise it is the skill whose directory the file sits in. **Both simpler rules were tried against the tree first and both fail** — nearest-name-anywhere fails two correct lines in `setup-clinical-skills/SKILL.md`, and adjacency with no carry fails `clinical-note/GLOSSARY.md`'s *"on the same terms as the voice model in step 8"*. That is `differential_scan.py`'s first version exactly: a positional guess that failed in both directions, and here a false alarm on a correct citation would be worse than no check at all.

**A citation with no skill named beside it, in a file outside `skills/`, is unresolved and is never failed.** `anchor_scan.py` cited `icd10-cpt` step 4 six times with no skill beside the words — **as it stood before #238, so do not go looking for it** — and no rule could know which skill it meant; guessing was the alternative. The counts per limb are pinned as **floors well under the measurement** rather than as figures, because a figure here is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) and would fail on the next paragraph anybody writes.

<!-- unresolved-step-citations: 1 -->

**`tools/` is out of that gap now, and the fix was prose rather than a parser change** — [#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238). Naming the skill once per paragraph moved every unresolved citation in the directory into the `beside` limb, with **not one line of the resolver touched**; that is what the ticket meant by cheap, and it is also why nothing held it. `test_every_citation_in_tools_resolves` holds it, because a reword that dropped a name would put those citations back beyond reach in silence. **The cost is named beside it rather than discovered later**: a `tools/` docstring writing *step 2 of the rebuild* — a step of something that is not a skill — now fails with no remedy but a reword, and the rule is a bet that the next `step N` written there will be a skill's, as all of today's are. **That example is itself an unresolved citation**, and backticks would not have helped it either, since the resolver has no mention-versus-use rule the way `spelling_scan.py` does. It is left standing rather than reworded around — the cheapest demonstration of what the `tools/` rule costs is a sentence that would fail it — and since #246 the paragraph holding it **declares** it, which is the marker below.

<!-- unresolved-step-citations: 1 -->

**The rule earned itself at the merge, which is the one place nothing else was watching.** While #238 was open, another branch made the same repair in `research_ledger.py` in passing — `e36b5f4`, titled *three step citations named no skill* — and wrote it as ``` ``practicum-case-study``'s ``SKILL.md`` step 3 ```. **That form does not resolve.** The `beside` limb reads a skill name with only its own punctuation between it and the words, and there is a space here, so all three came back `unresolved` exactly as before. Nothing on `main` could have said so, because `main` had no test for it; the branch's own suite was green and so was `main`'s. **It surfaced only when the two trees met** — [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the merge is the unguarded moment*, arriving for the third time, and the first time on a rule built after that lesson was written down. The repair a reader should copy is the path form, ``` ``skills/practicum-case-study/SKILL.md`` step 3 ```, because a link or a path ending in the skill's own name satisfies the limb and an apostrophe does not.

**The `fixtures/` prose is deliberately not repaired, and that is the ticket's own scoping.** Several of those sentences name a skill **as it stood at run time**, so rewording one to resolve risks making a historical statement read as a current one — a judgment rather than a mechanical fix. **The repo root is no longer left with it** — see below. **No count of what is left is stated here**, on the class docstring's own reasoning: #233's first draft published *38 unresolved* and it was stale before it merged, moved by two tickets with nothing to do with it.

**What it cannot reach is the sharper half, and it is permanent.** It catches a citation to a step that **does not exist** — not one to a step that still exists and now means something else. Insert a step at the top and only citations at or above the old maximum come back missing: on #214, the four citations to `practicum-case-study` step 9 would have fired and the `step 5`, `6` and `7` ones would have resolved silently to the wrong step. **A green run is not a walked citation.** That #214 case is what the class asserts — the check is pointed at a renumbering that has not happened, because asserting the tree is clean today proves only that the walk found nothing.

**`fixtures/` is excluded bar its own `README.md` and `assertions.md`, and the reason is that a record cannot be edited to fix a stale citation.** A note under `fixtures/filled-anchor/notes/` cites the skill **as it stood when the run happened** — that is what makes it evidence — so grading one would refuse a faithful record and the only repair available would be to falsify it. The default under `fixtures/` is to exclude, so a new kind of record lands outside the check rather than inside it.

**The repo root is gated too since [#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246), and the two documents are ruled apart rather than together.** That ticket put `AGENTS.md` and `CLAUDE.md` in one row of one table; they are not one kind of document. `AGENTS.md` is short and it is a contract — it tells a consumer which skills need which tools, every citation in it is a genuine cross-reference, and it takes **no escape hatch at all**, so nobody can quietly buy their way out of the one file a consumer reads. `CLAUDE.md` is an order of magnitude longer and is where every checker in this repo gets described, so it is structurally where *every* rule's mention-versus-use problem lands — and this file already records three earlier arrivals — `spelling_scan` died on the paragraph documenting its own homoglyph map, `differential_scan`'s #153 broke on prose describing the row it grades, and two files exempted themselves from `phi_scan` merely by explaining its pragma near the top.

**The ticket priced the repair as #238's and it was that for nine of twelve.** Eight were renamed for two words each and one was **de-cited** — *"a reader following a cross-reference"* says everything the bare number said, and that is the cheaper repair wherever the number was never the point. The other three are all in this section and every one is a **quotation**: `clinical-note`'s `GLOSSARY.md` line, quoted as the evidence for the `carried` limb; the *rebuild* example the paragraph above calls a deliberate demonstration; and the apostrophe form #238 caught at the merge, quoted **because it does not resolve**. **Naming the three without quoting them is itself the point** — this paragraph would need a marker of its own if it pasted them back, which is how cheap the de-citing repair usually is. Naming a skill beside any of them falsifies the quotation, which is `differential_scan.py`'s #153 arriving on a document instead of a parser.

**No figure is stated for that asymmetry, and a draft of this section stated two.** One counted this file's own lines, which the very commit writing it changed — and restating the pair here would be the same defect a third time. The other quoted a match count with no pattern beside it, so the two reviews re-deriving it reasonably got a different number than each other. Both are [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside the change whose subject is #143, which is the third time that has happened in this file. `TheTwoRootDocumentsAreNotOneKind` pins the asymmetry as a **floor** instead and holds the pattern in code, so *describes a checker* means one thing rather than whatever a reader's `grep` happens to spell.

**So those three are declared rather than repaired**, with the narrow marker #246 itself named as the honest remedy:

```
<!-- unresolved-step-citations: 1 -->
```

**It declares a count, and that is the difference between an opt-out and an off switch.** A fourth citation wandering into a declared paragraph fails exactly as it would anywhere else; a marker left behind by a rewrite fails too, because it reports a count nothing meets. It sits **on its own line**, comment punctuation aside, on `phi_scan.py`'s pragma reasoning — a marker mentioned mid-sentence is not a marker, which is why this paragraph does not declare itself. It covers the **next paragraph only**, on `spelling_scan.py`'s: the unit is the span, so no document can exempt itself. A marker glued to its paragraph is not read as one at all, and the paragraph stays graded — the safe direction. And `: 0` exempts nothing, so the smallest number is not the widest license.

**`EXEMPT_CEILING` caps the whole hatch just above what is declared today**, deliberately close, so a fourth has to be argued for in a diff rather than typed. Without a ceiling the marker is a wholesale opt-out and the gate is theater.

**#246 refused the other candidate and the reason is worth keeping.** `spelling_scan.py`'s mention-versus-use rule reads a form inside backticks as a mention — which does not transfer, because this repo writes a backticked citation meaning a real one all over the tree, so adopting it would silently stop grading the citations most likely to be precise. A declared marker grades them all and lets a person name the three exceptions.

**What it cannot reach is the same sharper half `tools/` has**, and `docs/adr/` is outside it — one citation in a ratified record, left where #238 left it.

### ICD-10-CM code set

`reference/icd10cm-2026.sqlite` is **committed**, unlike everything else generated here, and that was decided rather than drifted into: `icd10-cpt` sits on the consumer's critical path, so a database that had to be built before the skill worked would make the skill's Markdown insufficient on its own. 13.6 MB on disk, **2.68 MB as a git object** — measured 2026-08-11, one time.

Rebuild it from the CMS release zips — downloaded, left unextracted — when a new fiscal year lands:

```bash
python tools/icd10_build.py "C:/codeing/david_2/icd-10-cm"
```

98,186 codes and 22,988 tabular notes from the FY2026 April 1 2026 revision. `meta.release` inside the database names the zip it was built from, because the tabular's own `<version>` reads `2026` and is equally true of two revisions that code differently.

**It holds the tabular, not the index.** So it verifies a code and never finds one: `tools/icd10_lookup.py --find` is a substring match over descriptors, which is a weaker thing than the alphabetic index and must not be read as one. The index, the neoplasm table and the drug table are all deliberately out — see the module docstring for what that costs.

Its parsers are covered by `tools/test_icd10.py`, which runs against the excerpts in `tools/testdata/` and **never against the shipped database** — a test that read the real one would pass for two reasons, one of them being that the builder and the test are wrong together.

### Guideline text extraction

The 179 society guideline PDFs are the source for everything in the #80 series, and nothing downstream reads a PDF — they read the `.txt` this produces.

```bash
python tools/guidelines_extract.py "C:/codeing/guidelines-src"
```

**The corpus stays outside the repo, and so does the output.** Source is 410 MB and mostly society-copyrighted ([#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87)); output defaults to a sibling of it, `guidelines-text`. The script **refuses to write inside any git checkout**, walking up from the output directory for a `.git` entry rather than only comparing against its own repo root — run from a worktree, that root is the worktree and says nothing about the main clone's `reference/`.

**One of the five tools here that is not stdlib** — see *Corpus census* above for why there are five and where that gets reconciled:

```bash
python -m pip install pymupdf
```

That is affordable because it is maintainer-only and runs once per corpus refresh, and the script checks for it up front rather than recording 179 identical failures.

**It read the corpus with `pypdf` until #83, and this paragraph used to argue for that.** The argument was: *`fitz` is roughly six times faster and loses the spaces between words on the USPSTF files — whole sentences come back as `primarycarebecauseofitshighsensitivity`, and 90 of the 179 documents are USPSTF.* **The observation was true and the conclusion drawn from it was wrong**, which is worth keeping visible rather than quietly deleting. It was measured against `page.get_text()`, one of several things PyMuPDF will do, and the glued words are not lost information — the *geometry* still carries the boundary. On a glued USPSTF line the gap inside a word measures −0.036 pt and the gap at a word boundary measures 1.145 pt, at an 8.48 pt font.

So `rebuild_text` walks the per-character boxes and inserts a space where the gap **stands out against its own line's spacing**. Measured over **all 179 documents and all 7,733 pages**, 2026-08-16, zero read errors from either library:

| reader | words | glued >25 chars | wrongly split | time |
| --- | --- | --- | --- | --- |
| `pypdf` | 5,340,439 | 4,168 | — | 342 s |
| `fitz` `get_text` (default) | 5,319,299 | 6,568 | — | — |
| `fitz` + `rebuild_text` | **5,369,614** | **719** | 6,881 | **195 s** |

**Against the line and not against the font size, and that is the whole algorithm.** A typesetter who tracks a heading out widens *every* gap on it, so an absolute threshold reads each one as a word break: KDIGO's section header `contents` came back as `c o n t e n t s`. Measured on that line every gap is 1.475 pt with a spread of **zero**; on a genuinely glued USPSTF line the median is −0.036 and the maximum 1.145, a spread of 1.181. **Tracking shifts the whole distribution and a word break is an outlier within it**, so the rule compares a gap to its line's median. It is better on every axis than the absolute rule — 4,285 more words, 130 fewer glued, 1,694 fewer wrongly split.

**These figures replace a 14-document, 4-page-each sample, and the sample was wrong in the direction that matters.** It reported 117 glued words for `pypdf` against a real 4,168, and put the splitting cost at *"11 out of 11,522"* when the corpus figure is three orders of magnitude larger. Worse, **the tuning table it produced named 0.14 as the value that splits nothing — over the whole corpus 0.14 leaves 5,094 glued runs, which is worse than the library it replaced.** A reader trusting that table would have picked the one setting that loses to `pypdf`. It was published here and caught by being asked to read every document rather than a selection, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape one more time.

**What it costs was isolated rather than left as a bound, and the isolating matters more than the number.** The 6,881 is a set difference and counts every short glued run the rebuild correctly broke apart as damage — `seethe` → `see the` is in it. So every split was recorded as `run -> pieces` and classified against a lexicon built from tokens **the PDF itself delimited with real space glyphs**: no outside dictionary, and the inference under test cannot define its own ground truth.

| class | n | % | verdict |
| --- | ---: | ---: | --- |
| glued run fixed | 9,622 | 70.3% | correct, the point |
| punctuation, tab or bullet | 3,179 | 23.2% | harmless separation |
| digit-break | 390 | 2.8% | damage, all in citations |
| letter-spaced word | **306** | 2.2% | **the real cost** |
| word broken, pieces not all single | 188 | 1.4% | mostly a footnote marker |

13,685 occurrences over 10,731 distinct shapes, all 179 documents, 2026-08-16.

**The number that matters here is zero.** Of the 390 digit-breaks, every distinct run is citation apparatus — a year (`2009;`, 158 of them), supplement page ranges (`S131–S155`), a superscript reference marker welded to its word (`al,23`). **Not one carries a clinical unit**, so no threshold value is broken anywhere in the corpus. That was the risk worth measuring: a repo whose subject is numbers cannot afford a reader that splits them.

So the true cost is **306** letter-spaced words in readable text, or 696 counting the citation digit-breaks, against 6,881 by set difference. The trade favors the body over the front matter, which is the right way round: what splits is display type in headings and reference lists, what is repaired is running prose, and a threshold lives in the prose.

**284 of those 696 are one running footer in one document, and finishing it is [#178](https://github.com/mshamblin5150-code/clinical-skills/issues/178).** `span_baselines` exists because a rendered page showed that footer being split character by character — a line of three spans, one tracked tightly and one normally, where a single median across both made every normal gap look like a word break. It fixed the 16 pages where the footer is three spans and not the 142 where it is one. **Rendering the page is how that was found, and no text metric had reached it in three rounds of tuning**: `page.get_pixmap(dpi=140)`, then actually open the image. The same four renders showed that `c o n t e n t s` really is letter-spaced on the page, so the extractor had been faithful and the question was semantic rather than a defect.

179 documents, 7,733 pages, **39,397,589 characters**, 1 page with no text layer, no failures — measured 2026-08-16. `manifest.json` carries a per-document entry: page count, characters, codec, document class, and **the exact strings stripped from it**, so a removal can be read back rather than believed. **The four fields #84 reads all survived the switch, checked rather than assumed**: 179 documents, 147 with a title, 0 missing a society, 176 `guideline` and 3 `print-capture`.

**Parallel since #83, and `--jobs 1` still runs in this process.** A pool of one is all of the overhead and none of the benefit, and serial is the mode a traceback is readable in. `map` yields in submission order so the manifest stays in source order and a rebuild diffs clean.

**`manifest.json` is also [#84](https://github.com/mshamblin5150-code/clinical-skills/issues/84)'s input, and its shape is a contract.** `tools/guidelines_index.py` reads four fields per entry — `doc_id`, `society`, `title`, `document_class` — and matches documents by `doc_id`, which is the source path with the suffix dropped. **Top-level `documents` must be the list of entries.** The first version of this writer emitted `"documents": 179` as a count, which `read_manifest` refuses outright rather than reading as empty; the run totals now live under `totals`. That refusal is the contract working, and `TheIndexerCanReadWhatThisWrites` in `tools/test_guidelines_extract.py` pins the handoff on this side, where the shape is owned.

`title` is the PDF's own `/Title`, verbatim and unfiltered — 147 of the 179 carry one and they are real guideline titles, measured 2026-08-12. The rest include the usual `Microsoft Word - ...` debris; curating that is the catalog's job (#81), and a junk heuristic invented here would be an unreviewable rule sitting between the PDF and the record.

**What it strips and what it cannot.** A line on 75% or more of a document's sampled pages goes, which catches `Downloaded from http://ahajournals.org by on August 12, 2026` on every AHA/ACC file. **Two rules run, and their figures have to be kept apart** — measured 2026-08-16:

| | documents | characters |
| --- | ---: | ---: |
| the literal 75% rule alone | **167** of 179 | **921,093** |
| with [#100](https://github.com/mshamblin5150-code/clinical-skills/issues/100)'s margin rule | **174** of 179 | **954,088** |

**Summing `chars_stripped` over `manifest.json` gives the second row and does not say so**, which is how the first row's figures came to be published as the second's — see [#184](https://github.com/mshamblin5150-code/clinical-skills/issues/184). The literal-rule row is re-derived by running this module's own functions over `guidelines-src` with `MARGIN_LINES = 0`, which is the only way to get it.

**That was 150 of 179 and 554,372 characters under `pypdf`, and the 17 documents it gained are the reader change showing up where it was predicted.** The old note said a running head with the page number folded into it differs on every page and is therefore invisible to the rule. `pypdf` did the folding; PyMuPDF keeps the folio on its own line wherever the typesetter set it there, so the head repeats verbatim and the rule sees it. **The ACIP captures are the worked case** — a capture contributed one page-repeated line and now contributes three, the stamp and the title and the URL each on their own.

**#100 is settled, and it settled smaller than it was filed.** Inside **2 lines** of either end of a page a line's digits are masked before it is counted; outside the margins nothing is masked, on the way in or on the way out. That adds **27 of 179** documents and **2,649 distinct lines** — 2,382 bare folios and 267 lines of the only two welded running heads left in the corpus. Documents with nothing stripped by either rule fall from **12 to 5**.

**The restriction is the safety property and not a tuning knob, and the damage it avoids is measured rather than feared.** Masked corpus-wide, the rule takes 466 lines out of `KDIGO-2024-CKD-Guideline`, every one a cell in a risk table; it clears the contents page of `KDIGO-2021-Blood-Pressure-in-CKD`, whose `S3` and `S7` entries mask exactly like the `S37` folio at the foot of 87 pages; and it takes the axis labels off Figure 2 of the USPSTF colorectal statement. Restricted to the margins it takes none of them — a running head lives at a page edge and a table row does not, which is #100's own option 1 and what the clinician ruled.

**Two is measured, not chosen.** N=1 and N=2 remove bare folios and the two welded heads **and nothing else at all**. N=3 removes 574 more lines across 11 documents, mostly real folios — but it flips `KDIGO-2013-Lipids-Guideline` from stripping nothing to stripping its own **figure axis**: page 23 opens `20 / 10 / 5 / 2` and N=3 takes the `20` and the `10`. N=2 over N=1 because `KDIGO-2009-Transplant-Recipient` and `USPSTF/idachildrenfinal` set the folio one line in from the foot. `tools/test_guidelines_extract.py` pins the boundary at N=2 **and** at N=3, in both directions.

**That boundary was published wrong once, and the mistake is the reusable part.** It first read *"N=3 begins taking `0000000000001122`, a DOI, out of the colorectal references"* — measured over the **already-stripped `.txt` corpus** rather than over the PDFs, so it answered a different question than the one it was quoted for and came out both wrong and plausible. It was quoted to the clinician in the table the N=2 ruling was made from. The ruling survives on the re-derived evidence, which is worse for N=3 rather than better; **the process failure is that a figure measured against the wrong input reads exactly like one measured against the right one.** Every figure in this section is now re-derived by running `guidelines_extract`'s own functions over `guidelines-src`.

**Both documents #100 names as true negatives stay true negatives** — the CDC opioid MMWR, a web-page print with no running head, and the 2-page `IDSA/ciab275` erratum. The other three of the five are `KDIGO-2013-Lipids`, `KDIGO-2017-Living-Kidney-Donors` and `USPSTF/rhrs`, whose folios sit deeper than the second line in.

**A folio set in roman numerals is not masked and will not be.** `GOLD-REPORT-2026` loses its disclaimer head on 236 pages and keeps it on the 10 front-matter pages foliated `i` to `x`, plus one page carrying no folio. Masking roman numerals means masking the letters i, v, x, l, c, d and m, which are letters in words; the residue is **11 lines of 247 in one document** and the cure is worse than it.

**The rule is narrowed in exactly one place, and it is not the margin question.** A line must also appear on at least 3 pages, because every line of a one-page document appears on 100% of its pages and the percentage alone would strip such a document to nothing and record it as clean. That floor is arithmetically inert above 3 sampled pages.

**A margin pattern that removed nothing is not recorded, and that is a reporting fix worth knowing about.** `© 2021 American Medical Association` clears the margin rule on 68 USPSTF files and the literal rule has already taken every member of it — within one document the year does not vary. Recorded anyway, it put **168 of 195** manifest entries against no removal at all, which reads as a rule doing seven times the work it does.

**A re-run overwrites and never deletes.** Rename a source and its old `.txt` stays behind, claimed by no manifest entry; the summary names orphans and leaves them, because #84 will index the directory rather than the manifest and would otherwise pick a stale copy up.

Its parsers are covered by `tools/test_guidelines_extract.py` against committed `.txt` page excerpts in `tools/testdata/`, never against a PDF — `*.pdf` is globally gitignored and stays that way. `rebuild_text` is testable there too because it takes PyMuPDF's `rawdict` **dictionary** rather than a page, so the suite still opens nothing.

**The ACIP excerpt has now been wrong in both directions, and the reason is the same one both times: the shape is the test.** It first put the browser print timestamp on a line of its own; that was corrected to the folded form because `pypdf` welds the page title in after the stamp, and the classifier had been passing the fixture while finding zero print-captures in the corpus. #83 moved the extractor to PyMuPDF, the four header parts land on four lines again, and the fixture was corrected back — **rebuilt from the real file on 2026-08-16 rather than edited into the shape expected**, which is precisely what the previous round failed to do. All three ACIP files re-checked as `print-capture` afterwards.
### USPSTF recommendation table

`reference/guidelines-uspstf.md` is **committed**, and for a different reason than the ICD-10 database: USPSTF recommendation statements are federal work and genuinely public domain, so unlike the other eight societies in the guideline corpus their content may be redistributed in full. 143 recommendations from all 90 USPSTF documents, one row each — topic, population, grade, interval, year, source file, page.

Rebuild it when the corpus is refreshed:

```bash
python tools/uspstf_table.py "C:/codeing/guidelines-src/USPSTF"
```

**One of the three tools here that is not stdlib-only** — see *Corpus census* above. It needs PyMuPDF — `pip install pymupdf`, imported as `fitz`. The import is deliberately inside `read_pdf` rather than at module scope, so importing the module — which the tests do — needs nothing installed, and **nothing a consumer runs imports it at all**. The `--out` default writes into the repo regardless of the working directory, the way `icd10_build.py` anchors on `REPO_ROOT`.

**The corpus lives outside this repo** at `C:\codeing\guidelines-src` — 179 PDFs, 410 MB, most of them society-copyrighted — and stays there. [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) is why, and the source PDFs are closed rather than deferred: no consumer needs them, they need the derived facts.

**It reads the PDFs directly rather than [#80](https://github.com/mshamblin5150-code/clinical-skills/issues/80)'s extracted text**, which #82 nominally depends on. #80 was unbuilt when this landed and its output format was not fixed, so coupling to it would have been a guess — the same reason `guidelines_catalog.py` re-extracts. `read_pdf` is the only function in the module that opens a file, and every parser takes a list of page strings, so redirecting it is a one-function change.

**#80 has since landed on its branch, and the one thing that would have blocked that swap is not a problem after all.** `read_pdf` returns the PDF's *metadata* title as well as its pages, because three documents take their topic from it: a print-to-PDF web capture whose first page is browser chrome, the 2000s AHRQ layout that opens with the recommendation instead of a title, and one whose title extracts with no space glyphs. #80's manifest was specified without a `title` field — but it emits one anyway, verbatim `/Title` for 147 of 179 PDFs, **and all three of those documents are among them** (verified against `C:/codeing/guidelines-text/manifest.json`, 2026-08-13). So this is now a genuine one-function redirect rather than a claimed one, and [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) — where `guidelines_catalog.py`'s duplicate extractor gets reconciled — is where this one belongs too. **One extractor too many is now two.**

**The grade marker is the anchor, not any section heading.** A USPSTF document states each recommendation two to four times and the renderings differ, so the builder scores every candidate region — structured abstract, summary section, page-1 figure — and picks the one stating the most recommendations, breaking ties on whether extraction kept the space glyphs. Two documents extract a whole paragraph as `TheUSPSTFrecommendsscreening...`; the figure states the same recommendations cleanly and wins.

**`population` and `interval` are derived, not quoted.** The table says so at the top, and `not stated` means the rule found nothing rather than that the document is silent — for `interval` that is the ordinary case, since an I statement has no interval to have. Every row carries `filename` and `page`, and that jump is the check.

Covered by `tools/test_uspstf_table.py`, which runs against six page excerpts in `tools/testdata/uspstf/` — one per document layout the corpus contains — and **never against the shipped table**, for `test_icd10.py`'s reason. The excerpts are public domain; author names, affiliations and correspondence addresses are stripped from them anyway.

### Guideline catalog

`reference/guidelines-catalog.md` is **committed**, and lists the 179-document guideline corpus one row per document: society, filename, title, topic, population, year, page count, class. The corpus itself is 410 MB of mostly society-copyrighted PDFs at `C:/codeing/guidelines-src` and **stays outside this repo** — that limb of [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) is settled rather than deferred, though the ticket itself is still open on the index. The catalog exists because at 179 documents nothing can navigate the corpus by reading it, and choosing *which document* is a metadata problem rather than a retrieval one.

```bash
python tools/guidelines_catalog.py                              # audit the committed catalog
python tools/guidelines_catalog.py --draft C:/codeing/guidelines-src   # scaffold to curate from
```

**The catalog is curated and the tool audits it, which is the opposite of `icd10_build.py`.** `--draft` fills only what a machine can settle — society, filename, page count, class — and takes a run at title and year; it leaves `topic` and `population` blank on purpose, because a rule that reads those off a title page is guessing and **a guessed population is worse than a blank one**: it is the field that decides whether a threshold applies to the patient at all. So the committed Markdown is the source of truth, and the default run re-derives the mechanical columns and refuses a catalog that has drifted — a dropped row, a wrong page count, a row for a file that is gone, a `?` nobody listed in the closing comment.

**43 cells are `?` today, 36 of them `population`**, and that is the rule working rather than the catalog being unfinished. Every one is named at the bottom of the file with why.

It reports filenames, column names and counts, never document text, so its output is safe to paste. Covered by `tools/test_guidelines_catalog.py`, which runs against fixtures in `tools/testdata/` and **never against the corpus or the shipped catalog**, and which opens no PDF — so `pypdf`/`fitz` are needed to build a draft and not to run the suite.

**It opens the PDFs itself, which is one extractor too many now that #84 has landed.** `tools/guidelines_index.py` reads #80's extracted text; this one still re-extracts. Worse, the two disagree by construction — the `year` column is derived from exactly the page-repeated lines #80 exists to strip. [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) is where that gets reconciled, and the `year` column is the part of it that cannot be fixed by swapping the reader alone: `Kidney International (2021) 99, S1-S87` is where that column reads a year from, and #83's literal rule already strips it from the extracted text. #100's margin rule widens the same gap by two documents rather than opening it. So #108 has to move the year derivation as well, and the catalog is only unaffected today because it opens the PDF itself.

### Guideline full-text index

Candidate selection across 179 society documents needs search. `tools/guidelines_index.py` builds an SQLite FTS5 index over the extracted text, and `tools/guidelines_search.py` queries it.

```bash
python tools/guidelines_index.py <text-dir> [<db-path>]
python tools/guidelines_search.py "urine culture" "urine cultures"
```

Both are **stdlib only, and neither opens a PDF** — FTS5 is compiled into the `sqlite3` that ships with Python, so querying costs no dependency. This pair is the only part of the guideline tooling that reads #80's extracted text rather than re-extracting; the catalog and the USPSTF table both still open PDFs, which is [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108).

**Keyword search rather than embeddings, and that was decided rather than defaulted into.** A full-text hit is a literal string on a literal page, checkable in one jump. An embedding hit is a similarity score, and in a repo where `ANCHOR` means *quote the text or it is not a code*, similarity is the wrong currency. Nine societies with overlapping scope spanning 2009 to 2026 means a fuzzy match can return the right concept from the wrong society, wrong year or wrong population **with a citation attached**, and more documents makes that likelier rather than less.

**What that costs, measured rather than argued.** `130-139 mmHg` returns nothing. `130-139 mm Hg` returns the AHA/ACC 2025 hypertension guideline and KDIGO 2021, because the page writes the unit with a space. The tool cannot bridge that and does not pretend to — the agent knows the synonyms and fires both, which is why `guidelines_search.py` takes several queries in one run. A query is a **phrase** by default; `--fts` opts into FTS5's own `OR`, `NEAR` and `term*`.

**The text-directory contract is written down in the builder's docstring, and #80 met it.** One layout: one `.txt` per document, form feeds between pages, `manifest.json` keyed by `doc_id`. It used to read a second layout — per-page files at `<text-dir>/<doc-id>/page-0007.txt` — which existed only because no producer had landed. **Deleting it removed a whole class of ambiguity along with the branch:** an all-digit stem read as a page number collapses `USPSTF/2021.txt` and `USPSTF/2022.txt` into one document called `USPSTF` carrying pages 2021 and 2022, two documents lost and two citations invented with nothing downstream able to tell. That was a live bug, fixed by requiring a `page` prefix; with one layout there are no page files and the question cannot be asked.

**The database is written outside every checkout, and there is a guard rather than a convention.** It defaults to `<parent of the main checkout>/guidelines-index/guidelines.sqlite` — `C:\codeing\guidelines-index\` here, beside the sources — overridable with `CLINICAL_GUIDELINES_INDEX` or a positional argument. `ensure_outside_repo` refuses any target inside the main checkout **or inside the worktree you are standing in**, and those are two different tests: `Path(__file__).parent.parent` is the *worktree*, so defaulting relative to it would drop 65 MB under `.claude/worktrees/` while reading as outside the repo. The tools are committed and the index is not. This is deliberately **not** the `icd10cm-2026.sqlite` arrangement, and [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) — blocked — is where that gets revisited.

179 documents, 7,733 pages, **39,270,212 characters**, **61,415,424 bytes on disk** — measured 2026-08-16 against the PyMuPDF extraction with #100's margin rule, and **re-derivable**.

**The size is in bytes because stating it in "MB" is how the last two figures here went wrong.** That file is 61.42 MB counted in millions and 58.57 MiB counted in 1024s, and **both numbers have been published in this repo for the same file** — 61.4 in this paragraph and 58.6 in #83's closing comment. Neither was a measurement error and the file never changed. A byte count cannot be read in two conventions, so it is what goes here. **Two independent sweeps caught this within a day of each other**, on #83's branch and on #100's, which says the unit is a genuine trap here rather than one person's slip.

**Three earlier figure sets are retired, and the reasons differ.** 40.7 M characters and 64.7 MB, measured 2026-08-12 against a throwaway extraction written because #80 had not landed — provisional, and retired when #80 landed. Then 39.8 M and 60.8 MB, measured 2026-08-13 against the `pypdf` extractor — **correct when taken and retired because the reader changed**, not because it was wrong. Then 39,305,877 characters, measured after #83 moved the extractor to PyMuPDF, and retired the same day when #100's margin rule stripped a further 32,995 on top of it.

**Whether the index grew or shrank across the reader change is not known, and the sentence that said it grew was withdrawn rather than corrected.** It read *"60.8 MB to 61.4 MB, while stripping 400 KB more boilerplate"*, and offered a mechanism: recovering the spaces `get_text()` loses turns glued runs into real words, so the term count rises faster than stripping cuts it. **The comparison was between a figure counted in 1024s and one counted in millions** — 58.57 MiB against 61.42 MB, the same 61,415,424 bytes — and the `pypdf` index those 60.8 were measured from no longer exists, so its convention cannot be checked either. The mechanism may well be real; **it was reasoned backwards from a difference that may be entirely unit**, which is the move this repo does not accept, and it was published here before a sweep caught it.

**Two character counts in this file disagree on purpose, and neither is wrong.** `guidelines_extract.py` reports 39,397,589 and this reports 39,270,212. They measure different stages of the same corpus, and the gap reconciles exactly — every row below is a measurement, and the last one equals `meta.characters` in the built database:

| | |
| --- | --- |
| extractor `chars` — line contents, **before** stripping | 39,397,589 |
| less `chars_stripped`, both rules together | −954,088 |
| plus the newline written between every line | +826,711 |
| plus the form feed written between pages (7,733 pages − 179 documents) | +7,554 |
| = characters in the `.txt` files on disk | 39,277,766 |
| less those same form feeds, which the indexer splits on and does not store | −7,554 |
| **= what the indexer counts** | **39,270,212** |

**This table has been published not balancing twice, in two different ways, and both are worth more than the arithmetic.**

**Its figures went stale in-branch.** It read 921,093 / +829,381 / 39,305,877, taken at roughly 14:00 on 2026-08-16 — and the reader was fixed twice after that, at 14:06 and 14:36, with the corpus re-extracted and reindexed at 15:21. The figures were correct when written and stale ninety minutes later, in the same branch, because **a measurement's expiry date is the next commit to the thing it measures.** `chars` did not move, which is exactly why nothing looked wrong: it is counted before stripping and so is blind to a change in the stripping rule.

**And it was missing a row the whole time.** The form feed is written into the files and then split back off, so it has to appear twice; with only the subtraction, `= characters in the .txt files on disk` sat 7,554 above what the rows above it summed to, while the paragraph beneath claimed the chain reconciled exactly. **The structure built so two figures could check each other did not check them**, through every rewrite above, because nobody added the column up. Found by review on #100's branch.

**The obvious explanation for the 127,377 between the two figures is wrong, and it is wrong in a way that looks right.** It is not line separators: it is the stripped boilerplate *minus* the newlines, because the extractor's figure is pre-strip and the indexer's is post-strip. The form feeds net out. Subtracting one figure from the other and naming the remainder is exactly the move this repo does not accept.

**The four manifest fields arrive intact**, checked against the built index rather than assumed: 176 `guideline` and 3 `print-capture`, 147 of 179 with a title, and no document missing a society. `--class print-capture shingles` returns only the ACIP captures, which is the entire reason that column exists.

**A missing index is not zero hits, and the exit status says which.** 0 for hits, 1 for a genuine zero, and 2 for every way of not having searched — no index, a file that is not one, one built by another schema version, or a query that would not parse. An index that had quietly failed to build would otherwise answer every clinical question with silence and look like a settled negative.

Its output is guideline text, so nothing here is PHI and standing rule 1 is not in play — but it *is* a society's copyrighted expression. Paste a line into a ticket, never a page.

Covered by `tools/test_guidelines.py` — one file for the pair, the way `tools/test_icd10.py` covers its builder and reader together — which builds a throwaway text directory and a throwaway index in a temp directory the way `tools/test_skills_mirror.py` builds throwaway checkouts. It never reads the real corpus or the real index: one is 179 copyrighted PDFs outside the repo, the other is a build artifact that may not exist on the machine running the tests.

### Recommendation extraction

The index finds a page. This reads a guideline's **recommendations** into machine-readable records, and it is [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83) gate 2's input.

```bash
python tools/guidelines_recs.py <pdf> [--json <path>] [--show]
```

**It exists because one measurement falsified the ticket's own premise.** #83 ruled that a recommendation count could only ever be a bound — *"it over-counts by nature, the way `HEDGE` does in `corpus_census.py`"* — and that was reasoned from a flattened text stream, where the `COR` token appears 68 times in that document. Read the **ruled tables** instead and the AHA/ACC 2025 hypertension guideline yields **103 numbered recommendations, with zero rows whose Class-of-Recommendation cell fails to parse**, and 103 unique identifiers. Measured 2026-08-16, **re-derived 2026-08-16** from the PDF by a second reader. **An exact count can be enforced and a bound cannot**, so this distinction is what decides whether a gate may refuse a commit.

**The table figure beside it was wrong in both places it was written, and the recommendation count was not.** This paragraph and `reference/thresholds/hypertension.md` both said *33 tables*; the tool prints **27**, and 27 itself counts two `(Continued)` continuations as tables, so the guideline presents **25**. 33 is the number of `Recommendations for` heading *occurrences* in the extracted text, which counts a header reprinted after a page break again. Nothing rested on it — coverage keys on `rec_id`, and 53 cited plus 50 scoped out still reconciles to 103 exactly — which is precisely why it survived two files and a review: **[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape is a figure nobody's gate re-derives**, and the fix is to state the one the tool prints and name what it is not. *(This sentence cited #94 and #96 when it was written, which are allergy-slot rulings — the miscitation `2525118` had removed from three places in this file one commit earlier, reintroduced by the session fixing a stale figure. #165 predicted exactly that: the wrong citation is the one a new sentence copies.)*

**Two modes, and the whole honesty of the module is telling them apart.** `exact` is a table whose header row is `COR | LOE`, where every row is one recommendation and the class is a cell rather than a guess. `bound` is a marker matched in running text — KDIGO's `Recommendation 3.1.1` and `Practice Point` — which also hits tables of contents and cross references, so it **over-reports** and is labeled as one. **No source is silently promoted**: a document with no ruled table comes back `bound` even when the marker count looks tidy, because what makes a count exact is the table structure and not the tidiness of the answer.

**Both the caption and the header are required**, and neither alone is enough. The caption alone matches a continuation table's repeated heading; the header alone appears in the front-matter legend explaining what the classes mean. And the caption is read **only to the end of its first rendered line** — AHA/ACC sets a sentence under it inside the same merged cell, which the first version welded into every identifier a reader has to type.

Its output is guideline text, so standing rule 1 is not in play — but a recommendation is the society's own **expression**. Stdout prints counts and identifiers only, `--show` prints the text, and the JSON is refused anywhere inside a git checkout on `guidelines_index.py`'s terms. Covered by `tools/test_guidelines_recs.py`, which builds synthetic tables in that file and **opens no PDF**.

### Threshold sheets

The distilled artifact the whole #80 series is for, and the gates that keep it honest — [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83). Per topic, the decision points only. `reference/thresholds/` holds the sheets and [its README](reference/thresholds/README.md) holds the format; `tools/threshold_sheet.py` grades them.

```bash
python tools/threshold_sheet.py --all
```

**`reference/thresholds/hypertension.md` is the first, and it is one topic out of a 179-document corpus.** 74 rows from the AHA/ACC 2025 hypertension guideline, citing 53 of its 103 recommendations, with the other 50 scoped out by identifier — 103 accounted for exactly. An empty directory entry is not a negative finding about a guideline.

**The population column is load-bearing and it came from the clinician rather than from the corpus.** A draft of this called KDIGO's `SBP <120` and AHA/ACC's `<130/80` a cross-society contradiction; they are not, because KDIGO's is CKD-only. So a conflict is keyed on **quantity and population together**, the key is drawn from a fixed vocabulary the sheet declares, and the guideline's own wording sits beside it — a machine can only compare strings, and a mis-keyed row is a wrong *word* a reader can see rather than a silent miss. Checking ADA 2026 afterwards found it **agrees** with AHA/ACC at `<130/80`: once population is respected the contradiction the ticket predicted mostly evaporates.

**Citation resolution is two tiers, which is the whole answer to what happens when the sources are absent.** Tier 1 needs nothing and runs everywhere: the number in a row's value must appear in that row's snippet. Tier 2 needs the 410 MB of PDFs and checks the snippet is on the cited page. **There is no machine on which citation checking drops to zero**, tier 2 skipping prints a banner that survives `--quiet`, and the sheet itself records the date tier 2 last really ran — so the artifact says so and not only the console. That is `phi_scan.py`'s corpus-layer hole, answered rather than repeated.

**Gate 3 was wrong first, and it was found by pointing it at the real sheet.** It matched a sanity bound by substring against the row's *quantity name* and graded every number in the value against it; on the first real sheet that produced ten failures and **all ten were correct rows** — the `2` in `kg/m2`, `>=7 days` in a row whose name contains `bp`, `15% in 24 h`, `within 30 to 60 min`. Bounds are keyed on the **unit** now. Both of `block_scan.py`'s parser bugs were found the same way, and the synthetic tests came afterwards.

**What no gate here reaches is written in the README and in the module docstring, the same day they were built.** The largest: **a sheet whose numbers are all real and all filed under the wrong heading passes every gate in the directory.**

### Build artifacts stay out of the tree, and now there are two nets

Three tools write outside every checkout and each carries its own guard — [#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176). `.gitignore` now covers the same artifacts by name, and the split of labor is the point: **a guard refuses the write, and the ignore rule only stops the result being committed if a guard is missed.** Neither replaces the other.

```
*-text/
guidelines-index/
recs-*.json
```

**The reason it was worth adding is a change of premise rather than a new defect.** `guidelines_index.py`'s guard compares against known roots — this worktree and the clone that owns it — so it misses a **sibling worktree and any other repo nearby**, which the `.git`-walk in `guidelines_extract.py` and `guidelines_recs.py` catch. In a private repo a mis-typed `--out` was clutter, and #176's *"Not urgent"* was ruled on that footing. Public, the same slip is publication of society-copyrighted page text, and `phi_scan` will never flag it because guideline text is not PHI. Re-priced on [#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223), 2026-08-18; **the consolidation itself stays debt**, because it is the half that does not reduce exposure.

**`tools/test_build_artifacts_ignored.py` derives two of the three names from the tools' own defaults** rather than repeating them — `guidelines_extract.default_output` and `guidelines_index.default_database`. A list typed into a test goes stale the first time a default moves and reads as coverage while it does. **The third is typed and the test says so**: `guidelines_recs.py` has no default `--json` path to derive from, so `recs-<stem>.json` is read off `threshold_sheet.py`'s tier-2 lookup by hand, and a rename there would leave the check passing.

**Its first version passed three of four assertions against a check that says yes to everything**, and that is the part worth keeping. `git check-ignore` asked about `tools/` answers *ignored*, citing a blank line in `.gitignore` — so any query written with a **trailing slash** comes back true. Every query is a file path now, and `TheInstrumentIsLive` asserts an uncovered path comes back false before anything else runs. This repo's recurring shape with the sign flipped: not a search that could not have worked answering like a settled negative, but one answering like a settled positive. **Which blank line is deliberately not stated** — the draft of this paragraph said 29, and the block above pushed it to 33 in the same commit, so the figure was stale before it was committed. **The PHI firewall itself is asserted rather than described**: `scratch/`, `output/`, `cases/` and `patients/` all match their own lines on real file paths, in `TheInstrumentIsLive`.

**One rule that is deliberately absent**: a bare `*.sqlite`. It would catch a stray index anywhere and it would also hide `reference/icd10cm-2026.sqlite`, which is committed on purpose. `TheNetDoesNotSwallowWhatIsCommitted` walks `git ls-files` and asserts no tracked file is ignored, so a wider pattern fails rather than quietly hiding one.

### Continuous integration

`.github/workflows/checks.yml`, one job, on `windows-latest` at Python `3.14` — [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86), ruled in [ADR 0002](docs/adr/0002-ci-runs-the-suite-at-the-merge.md). It runs the suite and `phi_scan --all`, and it installs nothing.

**The subject is the merge, not the commit.** Everything else here fires at `git commit` in one clone. Git does not run `pre-commit` for an automatic merge commit **at all**, and where a merge is hand-resolved the result is a tree neither parent ever had — so `main` can hold a combination nobody ran the suite against. **Two branches have already broken it that way**, both recorded under *Console codec* above: `anchor_scan.py` against #150's rule, and `block_scan.py` one merge later against the mechanism built to stop it. A third came close — #179's merged tree ran tests neither side had run and was green, and nothing required anyone to look. That near-miss is recorded in [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s comments and **not** in *Console codec*; this sentence claimed it was, one commit after being written, which is the cross-reference going stale faster than the figure beside it.

**What it buys is the guarantee that the detection ran, and not detection.** Every defect this repo has caught was caught by a discretionary pass — `/code-review`, a tracker sweep, somebody running the suite after merging because they had been told to align a checkout. Those keep working. What none of them is, is obligatory.

**Advisory, ruled rather than defaulted into.** Nothing here is a required status check, so a red run reports and blocks nothing, and `git merge --no-ff` followed by `git push origin main` stays the way changes land — which is how #142 landed, and a required check would have made that push impossible. Escalating is a repository setting rather than a rewrite; ADR 0002 names *require branches to be up to date* as the first thing to turn on if it ever is.

**Both triggers, because `main` is reached two ways.** `pull_request` checks out the **merge result** rather than the branch head, which is the tree the whole ticket is about. `push` to `main` catches the local-merge-and-push route the merge button is never in. Neither alone is a guard, and even together there is a hole: GitHub recomputes a PR's merge commit when the **branch** moves, not when `main` moves, so a PR opened before another lands and merged after it can go green about a merge that no longer exists — which is the `anchor_scan` shape exactly. The `push` trigger catches that on the way in rather than before.

**The PHI step states its own coverage, and the statement is derived rather than typed.** `python tools/phi_scan.py --layers` prints which of the path, corpus and shape layers actually ran, computed from the scanner's own inputs, and adds `A clean result here is NOT "no PHI"` whenever one did not. The job prints it into the step summary, so it sits on the page the checkmark is attached to. **A banner written into the YAML would have been a claim about `phi_scan` that `phi_scan` does not make and nothing re-derives**, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

That was the sharpest risk in the ticket and it is answered rather than closed: `scratch/` is gitignored PHI that must never reach a runner, so **in CI the corpus layer is dead on every run that will ever happen**, and the `--all` mode leaves the path layer inapplicable too. Two of three layers dark, on the rule that matters most. It is scanned anyway because the shape layer caught a real date of birth on #64, and because **CI is not the weak configuration — it is the ordinary one**: agents commit from worktrees, where the corpus layer is already dead ([#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)).

**`windows-latest` because a red run has to mean the maintainer's machine would go red.** The platform-shaped code here is Windows-shaped — #150's cp1252 console, and `skills_mirror.py`'s `mklink /J` branch, which is the one this repo executes. A Linux runner would exercise the `os.symlink` branch nobody uses. Python 3.14 for the same reason: it matches the machine every commit here is made from.

**"No consumer runs these tools" was written here and in ADR 0002 and it is false.** [AGENTS.md](AGENTS.md) says `icd10-cpt` and — since #46 — `clinical-note` both look codes up by running `tools/icd10_lookup.py`, so *"an agent that cannot run the script is working from recall."* **A consumer runs Python on the critical path.** The three modules a consumer reaches — `icd10_lookup.py`, `icd10_build.py`, `console_codec.py` — are cleaner than the tooling around them: all three take the future import, none calls `zip(strict=)`, and all three parse at 3.7. So **there are two floors here, the consumer path's and the tooling's, and this job measures neither.**

**The floor is 3.10, and the reason first published here was wrong.** This sentence read *"`int | None` is PEP 604 and there is no 3.11-or-later syntax anywhere in `tools/`, checked rather than assumed."* PEP 604 binds almost nowhere: **almost every module in `tools/` carries `from __future__ import annotations`**, so their annotations are never evaluated. **How many is deliberately not stated, and the figure that used to stand here is why** — it read *29 of the 39 modules*, in this file and in [ADR 0002](docs/adr/0002-ci-runs-the-suite-at-the-merge.md), and by 2026-08-19 both halves were wrong by twenty: the directory holds more modules than that and more of them carry the line. Nothing re-derived it, and it decayed without either copy being edited — [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) by accretion, which is the generator [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s list does not name. **The clause beside it survived intact**, because it counts the exceptions rather than the total: the modules without the line are test modules, and `test_console_codec.py` is one of them. What pins 3.10 is `zip(COLUMNS, cells, strict=True)` at `tools/guidelines_catalog.py:148` — a runtime API no future import can defuse — and one evaluated `-> ast.If | None` at `tools/test_console_codec.py:105`. **And *checked rather than assumed* was overstated**: the check was a grep over a hand-picked list, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s partial instrument, and `ast.parse(feature_version=(3, 9))` is blind here because `int | None` is valid grammar everywhere and fails only at runtime. **The only interpreter on this machine is 3.14**, so the suite has never run on 3.10 and the floor is inferred rather than measured. See [ADR 0002](docs/adr/0002-ci-runs-the-suite-at-the-merge.md).

Covered by `tools/test_ci_workflow.py`, in **two tiers, and the split is a dependency decision rather than a taste one** — `tools/` is stdlib only and the cost argument above depends on that, so nothing there may require PyYAML. The floor reads the workflow as text and runs everywhere: it pins the runner, the Python version, the test command and the PHI step's honesty against this file, so the workflow and the prose cannot drift apart, and it catches tab characters. Above it, `TheFileIsValidYaml` parses the file and checks the job's shape **when PyYAML happens to be importable, and skips when it is not**.

**That tier is the one that matters, and it deliberately runs where CI does not.** A syntax error means GitHub declines to run the workflow, so the PR page shows **no failing check at all** rather than a red one — this ticket's own failure mode arriving through the mechanism built to fix it, and something no test inside the job could ever report, because the job would not exist. Validating on the machine the commit is made from is the only place the check is not circular. **On a machine without PyYAML the tab test is the whole guard**, and neither tier can tell you the job passed. **The first push is still the only end-to-end check.**

### PHI pre-commit hook

Standing rule 1 is enforced rather than remembered. **Git does not clone hooks, so every clone needs this once:**

```bash
git config core.hooksPath tools/hooks
```

After that, `tools/hooks/pre-commit` runs `tools/phi_scan.py` on every commit in that clone — yours, an agent's, anything.

**Standing rule 1 is no longer the only thing that can refuse a commit here, and that changed deliberately.** Since #83 a staged `reference/thresholds/*.md` also runs `tools/threshold_sheet.py --all --quiet`, and a failing gate refuses. The reasoning is narrow: a fabricated citation in a threshold sheet is a number a clinician may act on, the checks that catch one are deterministic, and a warning in a hook is read past. **It costs nothing on any commit that does not touch a sheet** — which is what keeps it from becoming the check people learn to `--no-verify` around — and `phi_scan.py` is no longer `exec`ed but has its status OR-ed in, so nothing above can suppress it. `skills_mirror.py` and `spelling_scan.py` stay advisory.

**Two layers, and the asymmetry between them is the design.**

- **Path layer** — anything staged from `scratch/`, `output/`, `cases/` or `patients/`. Those are gitignored, so a staged path there means someone reached for `git add -f`.
- **Corpus layer** — every patient name and date literal appearing in `scratch/`. **No file can exempt itself from this.**
- **Shape layer** — things that look like PHI whatever the corpus says: a `dob` token followed by a date, SSN, phone, MRN plus digits, an `M-D-YY`-style short date. ISO dates are deliberately not flagged, since the skill files are full of `measured 2026-08-11`.

A file that genuinely needs PHI-shaped literals — `tools/test_corpus_census.py` tests a date-of-birth extractor — declares `phi-scan: synthetic` near its top, **alone on its own line**, comment or docstring punctuation aside. **That exempts the shape rules only.** A file may say its dates are invented; no file may say its patient names are fine.

The own-line requirement is why this paragraph does not exempt this file: mentioning the pragma mid-sentence is not declaring it. It used to be a bare substring test, and README.md and `tools/phi_scan.py` both exempted themselves just by explaining the rule near the top.

Findings are redacted by default so hook output is safe to paste. Reveal them with:

```bash
python tools/phi_scan.py --show
```

Audit everything already committed with `python tools/phi_scan.py --all`.

#### Corpus resolution

`scratch/` is gitignored, so `git worktree` does not bring it. Every tool that reached for it resolved through `Path(__file__).resolve().parent.parent`, which in a worktree is **the worktree** — a tree that has never had a corpus. [#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93).

`tools/repo_root.py` is the one place that resolves it now. `main_repo_root()` reads the worktree's `.git` pointer file and walks up to the clone that owns it; `scratch_root()` is that plus `scratch/`. **Run `python tools/phi_scan.py --layers` from a worktree and the corpus line reads `ACTIVE`** — the figures beside it are counted from `scratch/` and are deliberately not restated here, on `differential_scan.py`'s terms: nothing committed can re-derive a number measured against a directory under `scratch/`, and [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is what one such figure copied into many files becomes. They match what a dozen by-hand workarounds recorded on the ticket, which is the check worth making.

**Two tools shared the line and failed differently, and the difference is why one cost a firewall and the other a ticket.** `corpus_census.py` degraded *loudly* — it named the path it looked at and stopped — so #78 got its figures by typing the main checkout's path as an argument. `phi_scan.py` degraded *silently*: the corpus layer went quiet, the shape layer kept passing, and the commit went through on two thirds of its evidence. `harvest_review.py` imports `phi_scan` and inherits whatever it does, which is now the fix.

**The count of modules repeating that line is not a to-do list**, and the ticket thread invites reading it as one — it has been posted there as 11, corrected to 14, re-derived as 20, and this paragraph first said 21 and was **23 by the time the branch it was written on finished**. That is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape happening inside the paragraph warning about it, which is why no number is stated here now. The durable claim is the qualitative one: **most of those callers want the worktree** — a test reading `fixtures/`, `scan_all` walking the files being committed, `_git` choosing a working directory — and **moving them would make a worktree scan somebody else's tree**, which is worse than the bug. Only a caller reaching for `scratch/` wants the main checkout. `phi_scan` holds both roots as two named constants for exactly that reason.

**An absent corpus is exit 2 — *did not scan*.** That is `guidelines_search.py`'s convention, already copied into `specificity_scan`, `differential_scan`, `anchor_scan` and `block_scan`, and #93 names the defect it fixes in its own comments: *those two exit-0s mean different things and nothing in the status distinguishes them*. The hook needed no edit — it already ORs any non-zero into its status. **Where a finding and a dead corpus both hold, 1 wins**, on `differential_scan.py`'s reasoning, and the layer report prints above it so the refusal reads as a floor.

**Two doors out, for the two places an absent corpus is expected rather than a fault**, and they are different doors because the callers differ. A person committing has nowhere to put a flag — the hook is what invokes the scanner — so a clone that holds no patient material says so once, alongside the `core.hooksPath` line it already needs:

```bash
git config clinical.phiAllowNoCorpus true
```

CI invokes the scanner directly and gets `--allow-no-corpus`, written into `.github/workflows/checks.yml` where a reader can see the job knowingly runs a layer short. **Not `if ($LASTEXITCODE -eq 2)` in the YAML**: that would be a judgment about `phi_scan` that `phi_scan` does not make and nothing re-derives, which is the objection the layer-report step next to it already exists to answer.

**Neither door buys silence, and that is what makes them safe.** Both convert the status and neither suppresses the report — `PATIENT NAMES ARE NOT CHECKED` prints either way. Same shape as `errors="replace"` in the console codec: the fix is about the exit status, not about the glyph.

**What it does not reach is CI, permanently.** `scratch/` is gitignored PHI that must never touch a runner, so there is no common dir holding a corpus anywhere on that machine and no resolution can find one. The ticket's own *Related* note — *a check that runs in CI would not care where the working tree is* — is backwards, and #86 landing is what settled it.

**The skills mirror stays advisory, and that was ruled here rather than left open.** #93's first comment routed the decision to this ticket on the grounds that the two failures are the same shape — same cause, same environment, both warning without failing — and that *"filing the mirror separately would split one decision across two tickets."* The shape is genuinely the same and the answer is still different, because **what the two degradations put at risk is not.** A dead corpus layer lets a patient's name reach a commit; a stale mirror lets an agent read a rule that was deleted. One harms the patient, the other harms the reader — and the reader is the party who can notice, which is exactly what happened when a worktree copy of `clinical-note` was caught still carrying the hypertensive-pressure rule after #23 removed it. **A stale mirror is also self-healing in one command and has no legitimate form**, so it needs no escape hatch and no ruling about who may commit; the corpus case needed both. Standing rule 1 is the rule this repo does not treat as advisory, and standing rule 1 is not what the mirror enforces.

So `skills_mirror.py --quiet` keeps its `|| true` in the hook. **Every worktree still needs its own `--repair`**, and nothing will ask.

#### Ruling on what the harvester found

The corpus layer harvests names from `scratch/name-index.json`. `win[0]` is a name's own line, so harvesting it is sound; `win[1..3]` are the shorthand lines that follow, and clinical shorthand is full of two-word letters-only phrases that look exactly like names. Those get indexed, and each one eventually refuses a fixture containing no PHI at all — `fixtures/day-b/shorthand/case-10.md` was refused for exactly this. The reverse also happens: a real name the index only ever caught mid-note.

**Nothing can tell those apart, so a human rules on them one at a time.** On a `corpus-name` refusal the hook prints how many are still unruled — a count only, so its output stays safe to paste. To see them:

```bash
python tools/harvest_review.py
```

**That output is PHI. Never paste it anywhere** — it is the deliberate opposite of `corpus_census.py`. Use `--count` when a number will do.

It writes nothing. Each string is either vocabulary, which you add lowercase to `NOT_NAMES` in `tools/phi_scan.py`, or a real name, which you add to `scratch/harvest-reviewed.json` — gitignored, because it is a list of patient names. **Anything you do neither to keeps being scanned for and keeps refusing**, so an abandoned review leaves the firewall at full strength.

Why it is not automated is recorded in the module docstring, including the two discriminators that were tried and rejected. The short version: recurrence would classify your most-seen patient as vocabulary.

**What this does not do.** It is a seatbelt, not a vault:

- `git commit --no-verify` bypasses it, as it bypasses any hook.
- The corpus layer needs `scratch/` present. Where it is genuinely absent that layer finds nothing and only the shape layer remains — but since #93 that **refuses** rather than warns, so it can no longer happen quietly. See *Corpus resolution* below.
- **Binary files are skipped entirely**, so nothing inside `reference/icd10cm-2026.sqlite` is read. Its contents are the public ICD-10-CM release and carry no patient data — but a tracked binary that *could* carry PHI would go unexamined and unmentioned.
- A patient name that appears nowhere in the corpus and is not date-shaped is caught by neither layer. All PHI here originates in the corpus, so the hole is narrow — but it is real, and it is why the rule still has to be read.
- **It has no concept of the account profile, and that hole is the wider one.** A site name, a preceptor, a payer mapping: none is a patient name, a corpus date or a PHI shape, so no layer matches one. Committed fixture notes have carried practicum site names through this scanner without a word — found by a reviewer who thought to grep. [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50) ruled that **acceptable rather than unnoticed** and built no fourth layer, so do not refile it. **The reasoning it kept instead is [fixtures/README.md](fixtures/README.md)'s** — a fixture built from another skill's *output* inherits that skill's whole context — which is wider than a site list and is why the list was not worth writing. The counts and the ruling's grounds live there and in that set's own README, once each. **[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) found it a second time and re-ruled it the same way on 2026-08-18**, against the changed premise that made it worth asking again — the clinician wants the repo public so Actions is free, and #50 was decided about a private one. Still no fourth layer, and the historical blobs stay: a placement and a preceptor are facts about him, not about a patient. **What #212 did change is the tree, and not on de-identification grounds** — `reference/medatrax-fields.md` was carrying the preceptor and site picklists, which [setup-clinical-skills](skills/setup-clinical-skills/SKILL.md) already says belong in the profile. That is a broken split rather than a leak, and fixing it is what emptied the tree. **A clean `git grep` here is not this scanner having gained a layer.** **Nor is [#222](https://github.com/mshamblin5150-code/clinical-skills/issues/222)'s gate**, which is the check that split had none of until 2026-08-18: `reference/medatrax-fields.md` declares the exact set of fields it holds values for and `tools/test_skill_agreement.py` asserts the file holds those and no others. **It reaches a field label and not a value** — a site name appended to a declared list, or a rule keyed on a site in prose, both still pass — and the reference and the test say so rather than reading as coverage. Building it found the split broken a second way: `setup-clinical-skills` step 4 called Case Type and the Patient Time bands per-account while the reference held both as universal, and each file read as coherent alone. **And a reader found it broken a third way within the hour** — [#226](https://github.com/mshamblin5150-code/clinical-skills/issues/226), ruled 2026-08-19: `reference/medatrax-fields.md` was carrying one clinician's degree plan under `## The requirement` — course codes, an institution's Canvas URL, term dates, an hours table and a planning target, an area breakdown, and one program's handbook quoted verbatim. **The abstracted version stays and the numbers moved**, because the deadline that block held is described across this repo as *the constraint the whole toolchain exists to satisfy*, and deleting the paragraph outright would have taken the reason the tooling exists out of the file a second clinician inherits. **Its check, `TheReferenceHoldsNoOneProgramsEnrollment`, is deliberately narrower than the defect** and reaches literal shapes only — a course code, an LMS vendor's host, a term date, and since #235 an accumulated hours total — leaving **almost** every per-program *figure* in that block to a reader, which is #222's ceiling holding rather than moving. **Almost, and the qualifier is load-bearing**: the hours total is the one figure from that block a check does reach, and this sentence said *every* for the length of #235's branch after the same commit added the limb that made it false. **How much it passes is stated in the class docstring and deliberately not counted here**: a draft of this sentence said *three of eight tells* and the ticket's own enumeration reads nine, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside the sentence arguing for honest proportion. Most of its patterns are narrower than their names, every narrowing measured against the tracked tree rather than guessed, and **two of them were found by the standards axis of the review after the first version shipped a term-date limb that fired on this very paragraph.** **The count of patterns is deliberately not stated here either, and it has already moved once** — [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235) added a fourth on 2026-08-19 and this sentence said *three* for the length of that branch, which is the cross-reference going stale one paragraph from the warning about stale cross-references.

**#235 is that class's ceiling being tested rather than raised, and it is worth knowing which way it went.** The ticket found a per-account *figure* in the reference — one account's portal totals published under *single source of truth for the Medatrax NP portal* — and asked whether a figure is checkable at all. Three candidate shapes were measured over the tracked tree: a sampled-day breakdown sits on 28 lines of legitimate fixture prose and was refused, a totals table row was keyable but escapable by writing the same number as a sentence and was refused, and an accumulated `HH:MM` hours total survived at three hour digits. **So one shape was found and the class was not**, and #50's declined name vocabulary is still declined. The figures behind that live on the pattern itself rather than here, and the first draft of them measured `*.md` while claiming *tree-wide* — a figure taken against the wrong haystack, which reads exactly like one taken against the right one.

**[#244](https://github.com/mshamblin5150-code/clinical-skills/issues/244) is the third instance of that shape and the ceiling held, which is the ruling worth keeping rather than the residue it was filed over.** #235 swept the section its own ticket named and not the file, so two of the seven totals survived under other headings — a patient-and-visit pair carrying an argument, and a form count carrying a portal behavior. **Neither was deletable the way the seven were**, because each was doing work the table was not: the clinician ruled on 2026-08-19 that the reference states the *method* and the *inference* and points at [setup-clinical-skills](skills/setup-clinical-skills/SKILL.md) step 6 for the reading, so the **raw pair** survives outside a run record exactly once, already declared as one account's. **The pair and not every figure, and the distinction is the honest form of this claim rather than a hedge on it**: the reference still says *about ten more visits than patients* and *fifteen Patient Detail pages*, because those two are what the inference is made of and abstracting them is what would cost it. Both are per-account and neither has a shape — a first draft of this paragraph claimed the figures survive once, which the class it describes already concedes is false, since a restatement in words escapes every assertion in it. The behavior example took no placeholder — the sentence names what the panel does instead of counting what it returned. **A bare integer still has no shape**, so no fifth pattern was added and #50's name vocabulary is still declined; what `TheWorkedReadingBehindTheDuplicateArgumentLivesInOnePlace` reaches, it reaches only because another file declares those two figures and the check reads its needles out of that file rather than holding them. **Scoped to the reference on purpose**: the same two integers are live in three notes under `fixtures/filled-anchor/notes/`, so a tree-wide version would fail in files nobody is allowed to fix. **The verdicts are the finding and the count is not**, which is #244's own comment being taken at its word — a `git grep` of either figure lands in a preserved run record, in the skill that is the pattern to copy, and in unrelated prose that happens to carry the digits, and only one of those was ever a fix. **No count is stated here**, because the one a first draft stated was measured on the pair before this change removed one of its files and was already wrong for a bare `582` when it was written.
