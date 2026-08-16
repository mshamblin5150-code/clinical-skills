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

### Corpus census

Several claims in [clinical-note](skills/clinical-note/SKILL.md) are counts over the clinician's shorthand corpus, and rulings have turned on them. `tools/corpus_census.py` recomputes all of them:

```bash
python tools/corpus_census.py
```

It reads `scratch/day-file-text/` — gitignored PHI — and **prints counts only, never matched text**, so its output is safe to paste into a ticket. Run it before relying on a figure again, and whenever the corpus grows.

Its extractors are covered by `tools/test_corpus_census.py`, which runs against the committed PHI-free fixtures and never touches `scratch/`:

```bash
python -m unittest discover -s tools -t tools
```

Stdlib only — no package manager, no lockfile, no CI in this repo, and the census is not worth introducing any.

**Three tools are now exceptions, and they are the three that open a PDF.** `tools/guidelines_extract.py` needs `pypdf`; `tools/uspstf_table.py` needs PyMuPDF; `tools/guidelines_catalog.py` prefers PyMuPDF and falls back to `pypdf`. Reading a PDF is not something the standard library does, so `tools/icd10_build.py`'s *"Stdlib only, like everything in `tools/`"* is no longer true of the directory.

**That there are three is the finding, not the arrangement.** All three extract text from the same 179 files, and two of them exist only because #80 had not landed when they were written. [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) is where that gets reconciled down to one. Each import sits inside the function that opens the file rather than at module scope, so the test suite needs nothing installed — and **nothing a consumer runs imports any of them.**

### Filled-vitals census

The corpus census reads the clinician's shorthand. This one reads **a run's finished notes**, and it exists because [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67) is a defect no single note contains: nine notes each filling a plausible vital set, and one patient described nine times.

```bash
python tools/filled_vitals_census.py <a run directory>
python tools/filled_vitals_census.py fixtures/filled-anchor/notes   # the committed evidence
```

It counts only what a tier block **declares filled** — `clinical-note`'s own `BP 142/88 filled` form — so given vitals stay out of the numbers, and a run that stops writing values into the block reads as having filled nothing rather than as having passed.

**Counts only by default, and that is load-bearing here rather than conventional.** A run directory lives under `scratch/` or `output/` and is a patient record. Nothing it prints without `--show` is a measured value, so its output is safe to paste into a ticket; **`--show` output is PHI on `harvest_review.py`'s terms** — read it, do not paste it.

**It exits non-zero when two notes share a filled height-and-weight pair**, which is `fixtures/day-b` B13. Everything else it prints is R5, counted rather than graded, because the corpus gives a direction and not a threshold.

Covered by `tools/test_filled_vitals_census.py`, which runs against the twelve committed notes and pins the two figures #67 rests on, so editing that run record fails a test rather than quietly voiding an argument.

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

The specificity scan reads an `icd10-cpt` run. This one reads a **`clinical-note`** run, and it is drift row 22's mechanical limb made runnable — [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68).

```bash
python tools/differential_scan.py <a run directory>
```

**One test, and it needs no reader.** No code marked `NOT CODED` anywhere in a note may sit in an entry's **code slot** — the position after the hyphen that pins a code to its label. #68 was filed over a naming question and closed a hole that was not about naming: one run produced three renderings of one rule, **all three kept the refused code out of the slot, and nothing required them to.** A fourth putting `M86.9` after the hyphen with the refusal in a footnote would have satisfied every row this repo had while asserting a disease nobody established.

**What it cannot reach is row 22 itself, and that is permanent rather than pending.** Deciding whether `Pain in right leg` is what `M79.604` says is a comparison of a label to a descriptor, and paraphrase is permitted — `Mild dyspnea - R06.02` and `Shortness of breath - R06.02` are both correct. **A clean scan is not a walked row**, `skills/clinical-note/SKILL.md` says so beside the command, and a test asserts that sentence is still there.

**It fails `fixtures/hedged-dx` run 1's case 2**, which is the rule being new rather than the run being newly wrong — that note was compliant with everything written down when it was generated.

**Counts only by default**, on `filled_vitals_census.py`'s and `specificity_scan.py`'s terms and for their reason: a run directory under `scratch/` or `output/` is a patient record, and an entry label is a diagnosis attached to an encounter. **`--show` output is PHI**: read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing** — 0 clean, 1 for a row 22 violation, **2 for every way of not having scanned**, including **no differential entry in any note read**. That last limb is the one that matters: a run whose differential was written in a shape the parser does not read would otherwise report zero violations and look like a pass.

**Run it against `fixtures/filled-anchor/notes` and it exits 2, which is correct and worth knowing before reading it as breakage.** **Zero of the twelve use the `label - CODE` slot form**, so there is nothing for a slot test to read and the tool says so rather than reporting a clean run. Measured 2026-08-15 and **pinned by a test**, because it is the claim the tool's own limits rest on.

**The obvious explanation for that is wrong, and it was published wrong here first.** This paragraph originally said the twelve carry *no ICD-10 code at all* on a differential entry. **Four of them do** — case 7 carries 13 in its differential block and case 8 nine, in the form `**COVID-19 (U07.1) — FAVORED.**`, with the code in **parentheses** rather than pinned by a hyphen. Six of the twelve carry no `Differential` heading at all; cases 1, 2, 9 and 10 head one and write entries carrying almost no codes. **So the set is not uniformly pre-#19 and it is not uniform at all** — which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s subject, and a third split for it. What is uniform is only the thing measured above: **nobody uses the hyphen**. A sweep by one reader produced the wrong generalization from two notes; a second reader caught it, and the figure was re-derived before this sentence was rewritten.

Covered by `tools/test_differential_scan.py`, which builds synthetic notes in that file and a temp directory — **there is no committed `clinical-note` run whose differential this could be tested against**, for the reason in the paragraph above. One test pins the parser against the shape that breaks a naive one: a compliant entry carries its own slot code and its refusals on a single line, so anything treating every code on a `NOT CODED` line as refused flags the slot and fails the skill's own worked example.

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

### Skills mirror

`.claude/skills/` is how Claude Code loads these skills natively, and each entry is meant to be a **junction to `skills/<name>/`** so the mirror cannot hold a different answer than the skill does. It is gitignored, so nothing git does checks it.

```bash
python tools/skills_mirror.py            # report; exits 1 if anything is not linked
python tools/skills_mirror.py --repair   # relink everything
```

**Read the mirror and you may be reading a retired rule.** A junction that has become a copy looks exactly like a working install — same names, same files, same frontmatter — and it answers with whatever the skill said the day the copy was made. `.claude/skills/clinical-note/SKILL.md` in one worktree still carried *a known hypertensive seen for a productive cough gets a hypertensive pressure and a raised respiratory rate* after #23 removed it, and had no drift row 14. An agent that opened it instead of `skills/clinical-note/SKILL.md` would have followed the rule the ticket existed to delete.

**`git worktree` is how that happens here.** It materializes `.claude/` by copying, and the copy follows the junctions instead of recreating them, so a fresh worktree starts out holding frozen skills. **Every worktree needs its own `--repair`.** The pre-commit hook runs `--quiet` and warns, but the warning is **advisory and never changes the exit status** — standing rule 1 remains the only thing that refuses a commit here.

It reports paths and status words, never file contents, so its output is safe to paste. `--verbose` names the differing files and still prints none of them. Covered by `tools/test_skills_mirror.py`, which builds throwaway checkouts in a temp directory and never inspects or repairs the real one.

### Spelling scan

Standing rule 4 — American English, always — with a command in front of it. The table lives in [clinical-note](skills/clinical-note/SKILL.md) under *Conventions*; `tools/spelling_scan.py` is that table made runnable, and `tools/test_spelling_scan.py` parses the skill's copy and asserts the two agree, so the scanner cannot start holding a different answer than the file a reader opens.

```bash
python tools/spelling_scan.py --all      # every tracked .md
python tools/spelling_scan.py --record   # the preserved run record, form by form
```

**A form inside backticks is a mention; a form in running prose is a use.** That is the whole exemption mechanism, and it is deliberately not `phi_scan`'s: the unit is the span rather than the file, so **nothing can exempt itself by explaining the rule** — which two files once did to `phi_scan` merely by documenting its pragma near the top.

**One directory is exempt by path**: `fixtures/filled-anchor/notes/case-*.md`, which is day-b run 1 byte for byte. Its eight British spellings are the evidence for [#73](https://github.com/mshamblin5150-code/clinical-skills/issues/73) and are counted rather than refused — `--record` is what the set's README cites instead of restating, and the totals are pinned by a test so a tidy fails rather than quietly voiding the argument. The set's own README is **not** exempt: it is prose about the record, so it takes the mention rule like any prose.

**Advisory in the pre-commit hook**, alongside `skills_mirror.py` and on the same reasoning: standing rule 1 remains the only thing that refuses a commit here.

It prints a path, a line number and its own table's entry — **never the text it matched** — so its output is safe to paste, and there is no `--show`. Two limits worth knowing: it reads **Markdown only**, so commit messages and filenames are outside it, and it holds the table rather than the language, so a clean scan means no *listed* form was used.

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

**One of the three tools here that is not stdlib** — see *Corpus census* above for why there are three and where that gets reconciled:

```bash
python -m pip install pypdf
```

That is affordable because it is maintainer-only and runs once per corpus refresh, and the script checks for it up front rather than recording 179 identical failures. `fitz` is roughly six times faster and loses the spaces between words on the USPSTF files — whole sentences come back as `primarycarebecauseofitshighsensitivity`, and 90 of the 179 documents are USPSTF.

179 documents, 7,733 pages, 39.5 M characters, no failures — measured 2026-08-12. `manifest.json` carries a per-document entry: page count, characters, codec, document class, and **the exact strings stripped from it**, so a removal can be read back rather than believed.

**`manifest.json` is also [#84](https://github.com/mshamblin5150-code/clinical-skills/issues/84)'s input, and its shape is a contract.** `tools/guidelines_index.py` reads four fields per entry — `doc_id`, `society`, `title`, `document_class` — and matches documents by `doc_id`, which is the source path with the suffix dropped. **Top-level `documents` must be the list of entries.** The first version of this writer emitted `"documents": 179` as a count, which `read_manifest` refuses outright rather than reading as empty; the run totals now live under `totals`. That refusal is the contract working, and `TheIndexerCanReadWhatThisWrites` in `tools/test_guidelines_extract.py` pins the handoff on this side, where the shape is owned.

`title` is the PDF's own `/Title`, verbatim and unfiltered — 147 of the 179 carry one and they are real guideline titles, measured 2026-08-12. The rest include the usual `Microsoft Word - ...` debris; curating that is the catalog's job (#81), and a junk heuristic invented here would be an unreviewable rule sitting between the PDF and the record.

**What it strips and what it cannot.** A line on 75% or more of a document's sampled pages goes, which catches `Downloaded from http://ahajournals.org by on August 12, 2026` on every AHA/ACC file. It finds a repeated line in **150 of the 179** — measured 2026-08-12 — not the 168 #80 estimated: a running head with the page number folded into it differs on every page, and a head that alternates recto and verso splits its votes. Masking digits would catch both and would also make `130-139 mm Hg` and `140-159 mm Hg` the same line — [#100](https://github.com/mshamblin5150-code/clinical-skills/issues/100) holds that decision open and it is not to be fixed in passing.

**The rule is narrowed in exactly one place, and it is not #100's question.** A line must also appear on at least 3 pages, because every line of a one-page document appears on 100% of its pages and the percentage alone would strip such a document to nothing and record it as clean. That floor is arithmetically inert above 3 sampled pages.

**A re-run overwrites and never deletes.** Rename a source and its old `.txt` stays behind, claimed by no manifest entry; the summary names orphans and leaves them, because #84 will index the directory rather than the manifest and would otherwise pick a stale copy up.

Its parsers are covered by `tools/test_guidelines_extract.py` against committed `.txt` page excerpts in `tools/testdata/`, never against a PDF — `*.pdf` is globally gitignored and stays that way. **Those excerpts have to match what `pypdf` actually emits.** The ACIP fixture originally put the browser print timestamp on a line of its own, which is what `fitz` does and what no real file does; the document classifier passed against it while finding zero print-captures in the corpus.
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

**It opens the PDFs itself, which is one extractor too many now that #84 has landed.** `tools/guidelines_index.py` reads #80's extracted text; this one still re-extracts. Worse, the two disagree by construction — the `year` column is derived from exactly the page-repeated lines #80 exists to strip. [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) is where that gets reconciled, and [#100](https://github.com/mshamblin5150-code/clinical-skills/issues/100)'s boilerplate misses land on this column too.

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

179 documents, 7,733 pages, 39.8 M characters, **60.8 MB on disk**, built in 1.7 s warm and answering a query in about 0.14 s — measured 2026-08-13, and **re-derivable**, which the previous set was not.

**The earlier figures were provisional and are now retired.** 40.7 M characters and 64.7 MB, measured 2026-08-12 against a throwaway extraction written to exercise this tool because #80 had not landed. #80 has landed, so the whole set was re-measured against the committed extractor. Boilerplate stripping is most of the 3.9 MB the index lost.

**Two character counts in this file disagree on purpose, and neither is wrong.** `guidelines_extract.py` reports 39,562,745 and this reports 39,780,017. They measure different stages of the same corpus, and the gap reconciles exactly:

| | |
| --- | --- |
| extractor `chars` — line contents, **before** stripping | 39,562,745 |
| less `chars_stripped` | −554,372 |
| plus the newline written between every line | +771,644 |
| **= characters in the `.txt` files, less the form feeds the indexer splits on** (7,733 pages − 179 documents = 7,554) | **39,780,017** |

**The obvious explanation for the 217,272 between the two is wrong, and it is wrong in a way that looks right.** It is not line separators: it is the newlines *minus* the stripped boilerplate, because the extractor's figure is pre-strip and the indexer's is post-strip. Subtracting one from the other and naming the remainder is exactly the move this repo does not accept — the figure above is derived from the manifest and the index meta, and the last row is checkable against the files on disk.

**The four manifest fields arrive intact**, checked against the built index rather than assumed: 176 `guideline` and 3 `print-capture`, 147 of 179 with a title, and no document missing a society. `--class print-capture shingles` returns only the ACIP captures, which is the entire reason that column exists.

**A missing index is not zero hits, and the exit status says which.** 0 for hits, 1 for a genuine zero, and 2 for every way of not having searched — no index, a file that is not one, one built by another schema version, or a query that would not parse. An index that had quietly failed to build would otherwise answer every clinical question with silence and look like a settled negative.

Its output is guideline text, so nothing here is PHI and standing rule 1 is not in play — but it *is* a society's copyrighted expression. Paste a line into a ticket, never a page.

Covered by `tools/test_guidelines.py` — one file for the pair, the way `tools/test_icd10.py` covers its builder and reader together — which builds a throwaway text directory and a throwaway index in a temp directory the way `tools/test_skills_mirror.py` builds throwaway checkouts. It never reads the real corpus or the real index: one is 179 copyrighted PDFs outside the repo, the other is a build artifact that may not exist on the machine running the tests.

### PHI pre-commit hook

Standing rule 1 is enforced rather than remembered. **Git does not clone hooks, so every clone needs this once:**

```bash
git config core.hooksPath tools/hooks
```

After that, `tools/hooks/pre-commit` runs `tools/phi_scan.py` on every commit in that clone — yours, an agent's, anything.

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
- The corpus layer needs `scratch/` present. On a fresh clone it finds nothing and only the shape layer remains.
- **Binary files are skipped entirely**, so nothing inside `reference/icd10cm-2026.sqlite` is read. Its contents are the public ICD-10-CM release and carry no patient data — but a tracked binary that *could* carry PHI would go unexamined and unmentioned.
- A patient name that appears nowhere in the corpus and is not date-shaped is caught by neither layer. All PHI here originates in the corpus, so the hole is narrow — but it is real, and it is why the rule still has to be read.
- **It has no concept of the account profile, and that hole is the wider one.** A site name, a preceptor, a payer mapping: none is a patient name, a corpus date or a PHI shape, so no layer matches one. Committed fixture notes have carried practicum site names through this scanner without a word — found by a reviewer who thought to grep. [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50) ruled that **acceptable rather than unnoticed** and built no fourth layer, so do not refile it. **The reasoning it kept instead is [fixtures/README.md](fixtures/README.md)'s** — a fixture built from another skill's *output* inherits that skill's whole context — which is wider than a site list and is why the list was not worth writing. The counts and the ruling's grounds live there and in that set's own README, once each.
