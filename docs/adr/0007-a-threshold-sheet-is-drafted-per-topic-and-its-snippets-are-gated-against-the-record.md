# A threshold sheet is drafted per topic, and its snippets are gated against the record

[#403](https://github.com/mshamblin5150-code/clinical-skills/issues/403) was filed about placement — `reference/thresholds/hypertension.md` is committed and the 266 lines that build it live in a gitignored build-artifact directory outside every checkout. Grilling it on 2026-08-22 moved the question twice, because the clinician's reason for the machinery existing is not the reason the ticket assumed.

His words: *"I do not want to be the bottleneck — the whole point was to get an agent to read whatever guideline it was and know what it says, so we can use said guideline in our references and in our paper."*

The clinician ruled, 2026-08-22:

1. **A threshold sheet is drafted, not hand-transcribed.** `tools/threshold_draft.py` emits a skeleton with the machine-settleable cells filled and every judgment cell blank, on `guidelines_catalog.py --draft`'s arrangement. It prints to stdout.
2. **The scaffolder is a separate module from the auditor.** `threshold_sheet.py` grades; it does not make.
3. **A new `CITATION tier 0` gates every snippet against its own recommendation record** — refusing on an `exact` source, reporting `NOT RUN` on a `bound` one.
4. **The sweep is not bounded by copyright.** Every PDF in the corpus was publicly available and unpaywalled; none is excluded.
5. **The unit is the topic, not the document**, and only where the topic has decision points.

## What was measured

**The generator still runs, and reproduces the sheet's data exactly.** Run to a target outside every checkout: `rows 74  distinct recs cited 53  scoped out 50  total accounted 103`. Normalized for line endings, the diff against the committed sheet is **two prose blocks and nothing else** — every threshold row, population, conflict and coverage line is byte-identical.

**Both differing blocks are regressions, and nothing in the repo would catch either.** It drops the #223 quoting-posture paragraph, and it regresses the Scope block to `all 33 Recommendations for ... tables` — the figure `hypertension.md` itself records as wrong and corrected to 27 headings / 25 tables. No test asserts either block. `TheQuotingPostureFiguresAreReDerived` reads the *rows* from the sheet and the *figures* from `README.md`; the sheet's own claim that a test protects it is protected by nothing.

**The sheet's rows have never been hand-edited.** Three commits in its life: the build, and those two prose corrections. The curated artifact has been curated only in prose.

**`recs-<key>.json` carries the full recommendation `text`, and no gate reads it.** The only comparison of record text to anything is `gate_citation_tier2`, which opens the 410,197,235 bytes of source PDFs and skips wherever they are absent. So the snippet — the one cell whose purpose is to make a fabricated citation detectable — was checked against the PDFs or against nothing.

**Tier 0 is free where it can run.** Snippet-is-a-substring-of-its-own-record, measured over both shipped sheets under three folds including `threshold_sheet._normalize` and `guidelines_recs.fold`:

| sheet | source mode | result |
| --- | --- | --- |
| `hypertension.md` | `exact` / ruled-table | **74 of 74**, identical under every fold |
| `diabetes.md` | `bound` / text-marker | 12 of 23, plus 2 `RENDERED:`-exempt |

The fold made **zero** difference to either, so the diabetes misses are not typography. The cause is structural: ADA `bound` record texts are a fixed window — min 93, median 157, **max 160 characters, and 0 of 126 end in a sentence terminator**. Every one is truncated mid-sentence, frequently before the threshold the row cites. AHA/ACC `exact` records run to 451 characters and are whole recommendations. *(Those record figures are counted against `recs-*.json` files outside every checkout; nothing committed re-derives them, and they move with the next extraction.)*

**Tier 0 reaches 112 of 179, not 22.** `CuratedRow.statement` carries the sentence each `reference/guidelines-uspstf.md` row was cut from, and **141 of 143 end in a sentence terminator**, lengths 72–1024, median 173 — re-derivable from a committed file. So the gate runs on the 22 ruled-table documents *and* the 90 curated ones, and cannot run on the 48 `bound` ones. That is the existing refuse/warn line, which is why tier 0 needs no new policy: it inherits one.

**The corpus is 179 documents and 169 distinct topic cells.** Only 9 topics carry more than one document. Societies: USPSTF 90, IDSA 41, AHA/ACC 23, KDIGO 18, ACIP 3, and one each of ADA, CDC, GINA, GOLD.

## Considered options

**Leave the generator outside and declare the limit** — the ticket's own no-move branch, on [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s *declare the coverage*. Rejected once the disk argument was measured against the right object. `guidelines-src` is **410,197,235 bytes** and stays outside on [#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87)'s terms, untouched by this. `build_htn_sheet.py` is **23.7 KB**, and all seven scripts together are 48 KB — about four orders of magnitude. Keeping the corpus out saves what the clinician wanted saved; keeping the script out saves nothing and costs the four things the ticket lists.

**Freehand authoring, on `diabetes.md`'s precedent.** Rejected, and it was the closest call, because it is the only option with a shipped instance: [#186](https://github.com/mshamblin5150-code/clinical-skills/issues/186) produced `reference/thresholds/diabetes.md` on 2026-08-20 with no generator at all — an agent read the guideline and wrote the committed Markdown, gates green. What decided against it is that freehand makes a language model **retype the snippet**, which is the one cell that exists to be un-retypeable, once per row for as many topics as get swept.

**The draft without the gate.** Rejected, and recording why matters because the draft alone is the intuitive answer. A scaffolder that lifts the verbatim text is a convenience; nothing stops the agent editing the cell afterwards and no gate would notice. `--draft` plus tier 0 is what makes a fabricated snippet fail at commit rather than in a reviewer's hands. **The draft helps an agent type; the gate catches an agent that typed something the guideline does not say.**

**`threshold_sheet.py --draft`, one module for both jobs.** Rejected, against the `guidelines_catalog.py` precedent that the ticket cites and that this session first leaned on. That precedent is weaker than it looks: the catalog's two modes take *the same input and produce the same artifact*. A threshold draft does not — the auditor takes a finished sheet and grades it, while the draft takes a **topic**, joins `guidelines-catalog.md` to find which documents address it, and pulls each one's records. Folding it in teaches the auditor about the catalog, which it currently knows nothing about, and cuts against [#410](https://github.com/mshamblin5150-code/clinical-skills/issues/410), which had just split the gates out. The separate module is also the **first production importer of `threshold_sheet`**, which turns `ROW_COLUMNS` and the section headings into a real shared interface rather than a restated one — `reference_scan.py` importing `docx_write.REFERENCE_HEADING`, for that module's reason.

**Bound the sweep to the 90 public-domain USPSTF documents and take the other 89 on demand.** Rejected by the clinician: *"Every last pdf is publicly available, they were not behind any paywall — all I did was gather them up together in one place."* The arithmetic this session offered against it was also wrong and is recorded here so it is not re-derived: it summed quoted words **across** 169 different works, and the fraction taken from **each** work is what the question turns on. `hypertension.md` quotes 773 words from a 105-page guideline in 6-to-15-word attributed fragments — well under 1% of it.

**One sheet per document.** Rejected. It yields three separate sheets for `hypertrophic cardiomyopathy` and leaves reconciling them to the reader, and it never exercises `CONFLICT` or per-source `COVERAGE`, which were built for exactly the multi-source case and have **never once run** — both shipped sheets cite one source. It also produces near-empty sheets for the many documents carrying no decision point, and [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85) ruled that a missing row earns `sheet does not settle it` and never `no guideline applies`. A directory of 169 near-empty sheets is what would teach a reader to read that silence as the stronger claim.

## The curated line does not move, and this is where it would have

[#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83) and the `guidelines_catalog.py` arrangement both turn on the committed Markdown being the source of truth and a tool auditing it. A scaffolder in `tools/` is where that would most easily be lost, and #403's own *What must not come out of this* says so.

It holds for a reason that is checkable rather than promised: **the draft emits blanks where the judgment lives.** `quantity` and `population` are the cells a reader has to choose, and a guessed population is worse than a blank one — it is the field that decides whether a threshold applies to the patient at all, which is `guidelines_catalog.py --draft`'s own ruling about the same column. What the draft fills is what a machine can settle: the `## Sources` rows, and each row's `rec`, `page`, `class` and verbatim `snippet`, every one lifted from the record rather than composed.

**The auditor stays a stranger to the thing it grades.** That is why the split is structural rather than tidiness: a module that both scaffolds a sheet and grades it can, at some future edit, come to agree with itself — the same reason a run's own grader cannot verify it, which this repo rules on in four places.

## The cost this accepts

**A topic join can be silently partial.** The draft's first job is selecting documents by the catalog's `topic` cell, and a topic worded differently across two documents yields a one-source sheet that reads as complete. The draft prints its candidate set and the rows it rejected, on this repo's usual terms, rather than letting a partial join read as a whole one.

**Tier 0 cannot run on 48 documents and must say so.** Reporting `NOT RUN` rather than passing is what keeps `diabetes.md` from reading as 25 verified rows when 11 were never checked.

**Tier 0 is a floor and not a reading.** It establishes that a snippet is text the source states. It cannot establish that the snippet is the *right* text for the row's quantity, or that the row's population is what the recommendation scopes — [#174](https://github.com/mshamblin5150-code/clinical-skills/issues/174)'s gate 5 narrows that and does not close it, and a clean tier 0 is not a read sheet.

**A comprehensive directory changes what an absent sheet means.** #85's `sheet does not settle it` was argued from a directory holding one topic of 179. A sweep moves that argument, and it moves the literal words **one topic** in `skills/clinical-note/SKILL.md` and `AGENTS.md`, and the directory pin at `tools/test_guideline_sheets.py:384`.

**The quoting posture's ground changes and the prose does not yet say so.** `reference/thresholds/README.md` names public domain only about USPSTF. After a sweep it would read as covering the corpus, when for the other 89 documents the posture rests on short attributed quotation instead. That paragraph is owed.

**`build_htn_sheet.py` is a live hazard until it is retired.** Running it today reinstates a retired figure and deletes a #223 ruling with the suite green. Its `RAW` block is also a second, unbound copy of 74 clinical values, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape carrying thresholds instead of prose. It is superseded by `threshold_draft.py` rather than preserved.

Correction, 2026-08-23: the two corpus-size statements formerly read `392 MB`, and the script-to-corpus comparison read `about 8000:1`. The size was corrected to bytes to follow #87, and the moving ratio was replaced with its decision-relevant order of magnitude. The ruling itself is unchanged.
