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

### Skills mirror

`.claude/skills/` is how Claude Code loads these skills natively, and each entry is meant to be a **junction to `skills/<name>/`** so the mirror cannot hold a different answer than the skill does. It is gitignored, so nothing git does checks it.

```bash
python tools/skills_mirror.py            # report; exits 1 if anything is not linked
python tools/skills_mirror.py --repair   # relink everything
```

**Read the mirror and you may be reading a retired rule.** A junction that has become a copy looks exactly like a working install — same names, same files, same frontmatter — and it answers with whatever the skill said the day the copy was made. `.claude/skills/clinical-note/SKILL.md` in one worktree still carried *a known hypertensive seen for a productive cough gets a hypertensive pressure and a raised respiratory rate* after #23 removed it, and had no drift row 14. An agent that opened it instead of `skills/clinical-note/SKILL.md` would have followed the rule the ticket existed to delete.

**`git worktree` is how that happens here.** It materializes `.claude/` by copying, and the copy follows the junctions instead of recreating them, so a fresh worktree starts out holding frozen skills. **Every worktree needs its own `--repair`.** The pre-commit hook runs `--quiet` and warns, but the warning is **advisory and never changes the exit status** — standing rule 1 remains the only thing that refuses a commit here.

It reports paths and status words, never file contents, so its output is safe to paste. `--verbose` names the differing files and still prints none of them. Covered by `tools/test_skills_mirror.py`, which builds throwaway checkouts in a temp directory and never inspects or repairs the real one.

### ICD-10-CM code set

`reference/icd10cm-2026.sqlite` is **committed**, unlike everything else generated here, and that was decided rather than drifted into: `icd10-cpt` sits on the consumer's critical path, so a database that had to be built before the skill worked would make the skill's Markdown insufficient on its own. 13.6 MB on disk, **2.68 MB as a git object** — measured 2026-08-11, one time.

Rebuild it from the CMS release zips — downloaded, left unextracted — when a new fiscal year lands:

```bash
python tools/icd10_build.py "C:/codeing/david_2/icd-10-cm"
```

98,186 codes and 22,988 tabular notes from the FY2026 April 1 2026 revision. `meta.release` inside the database names the zip it was built from, because the tabular's own `<version>` reads `2026` and is equally true of two revisions that code differently.

**It holds the tabular, not the index.** So it verifies a code and never finds one: `tools/icd10_lookup.py --find` is a substring match over descriptors, which is a weaker thing than the alphabetic index and must not be read as one. The index, the neoplasm table and the drug table are all deliberately out — see the module docstring for what that costs.

Its parsers are covered by `tools/test_icd10.py`, which runs against the excerpts in `tools/testdata/` and **never against the shipped database** — a test that read the real one would pass for two reasons, one of them being that the builder and the test are wrong together.

### Guideline full-text index

Candidate selection across 179 society documents needs search. `tools/guidelines_index.py` builds an SQLite FTS5 index over the extracted text, and `tools/guidelines_search.py` queries it.

```bash
python tools/guidelines_index.py <text-dir> [<db-path>]
python tools/guidelines_search.py "urine culture" "urine cultures"
```

Both are **stdlib only, and neither opens a PDF** — FTS5 is compiled into the `sqlite3` that ships with Python, so querying costs no dependency, and the PDF library stays entirely on the extraction side (#80).

**Keyword search rather than embeddings, and that was decided rather than defaulted into.** A full-text hit is a literal string on a literal page, checkable in one jump. An embedding hit is a similarity score, and in a repo where `ANCHOR` means *quote the text or it is not a code*, similarity is the wrong currency. Nine societies with overlapping scope spanning 2009 to 2026 means a fuzzy match can return the right concept from the wrong society, wrong year or wrong population **with a citation attached**, and more documents makes that likelier rather than less.

**What that costs, measured rather than argued.** `130-139 mmHg` returns nothing. `130-139 mm Hg` returns the AHA/ACC 2025 hypertension guideline and KDIGO 2021, because the page writes the unit with a space. The tool cannot bridge that and does not pretend to — the agent knows the synonyms and fires both, which is why `guidelines_search.py` takes several queries in one run. A query is a **phrase** by default; `--fts` opts into FTS5's own `OR`, `NEAR` and `term*`.

**The text-directory contract is written down in the builder's docstring, and #80 has to meet it or change it.** Per-page files at `<text-dir>/<doc-id>/page-0007.txt`, or one `.txt` per document with form feeds between pages; `manifest.json` optional, keyed by `doc_id`. **A bare `0007.txt` is deliberately not read as a page** — `USPSTF/2021.txt` and `USPSTF/2022.txt` would otherwise collapse into one document called `USPSTF` carrying pages 2021 and 2022, which is two documents lost and two citations invented with nothing downstream able to tell. When #80 lands, delete whichever layout it does not emit.

**The database is written outside every checkout, and there is a guard rather than a convention.** It defaults to `<parent of the main checkout>/guidelines-index/guidelines.sqlite` — `C:\codeing\guidelines-index\` here, beside the sources — overridable with `CLINICAL_GUIDELINES_INDEX` or a positional argument. `ensure_outside_repo` refuses any target inside the main checkout **or inside the worktree you are standing in**, and those are two different tests: `Path(__file__).parent.parent` is the *worktree*, so defaulting relative to it would drop 65 MB under `.claude/worktrees/` while reading as outside the repo. The tools are committed and the index is not. This is deliberately **not** the `icd10cm-2026.sqlite` arrangement, and [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87) — blocked — is where that gets revisited.

179 documents, 7,733 pages, 40.7 M characters, **64.7 MB on disk**, built in 2.7 s warm and answering a query in under 0.3 s.

**Those figures are provisional and nobody can re-derive them yet**, which is the opposite of how every other number in this file works. They were measured 2026-08-12 against a throwaway extraction written to exercise this tool, because #80 had not landed — so there is no committed extractor to reproduce them with. Re-measure the whole set when #80 does land: boilerplate stripping removes a line from nearly every page of 168 documents, so the character count and the file size both move.

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
