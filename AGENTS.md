# Clinical skills

Agent-agnostic skills for a nurse practitioner student's written work — clinical documentation from ER-style shorthand, and graded coursework from faculty material and live course boards. Each skill is a folder under `skills/` holding a `SKILL.md` — plain Markdown with YAML frontmatter, readable by any agent.

## How to use a skill

**Read the skill file before starting the task.** Do not work from the one-line summary below — it is an index, not the instructions.

| Skill | Read | Use when |
| --- | --- | --- |
| clinical-note | [skills/clinical-note/SKILL.md](skills/clinical-note/SKILL.md) | Encounter shorthand needs to become a comprehensive SOAP or an FNP H&P |
| batch-shift | [skills/batch-shift/SKILL.md](skills/batch-shift/SKILL.md) | A day file — one shift's shorthand, scanned — needs splitting into encounters |
| icd10-cpt | [skills/icd10-cpt/SKILL.md](skills/icd10-cpt/SKILL.md) | A documented encounter needs ICD-10-CM or CPT codes proposed |
| setup-clinical-skills | [skills/setup-clinical-skills/SKILL.md](skills/setup-clinical-skills/SKILL.md) | **Run once first.** A new clinician's portal, program, picklists and patient identity map need configuring |
| practicum-case-study | [skills/practicum-case-study/SKILL.md](skills/practicum-case-study/SKILL.md) | A graded course case study needs writing up from faculty material, and submitting as a `.docx` |
| discussion-post | [skills/discussion-post/SKILL.md](skills/discussion-post/SKILL.md) | One live LMS board needs a researched, evidence-backed initial post, except when its prompt asks for a worked clinical case |
| discussion-reply | [skills/discussion-reply/SKILL.md](skills/discussion-reply/SKILL.md) | One live LMS discussion topic needs ranking, evidence-backed classmate replies, and explicit approval before each post |
| course-assignment | [skills/course-assignment/SKILL.md](skills/course-assignment/SKILL.md) | A live course assignment declares a graded PowerPoint deck or rich Word document |
| vitalsource-chrome | [skills/vitalsource-chrome/SKILL.md](skills/vitalsource-chrome/SKILL.md) | An authenticated VitalSource or Bookshelf chapter must be read completely by any browser agent |
| aar | [skills/aar/SKILL.md](skills/aar/SKILL.md) | A scoped clinical skill has reached a submission and its mandatory after-action review must classify and land observed corrections |
| peer-critique | [skills/peer-critique/SKILL.md](skills/peer-critique/SKILL.md) | A classmate's case study needs the graded eight-heading peer clinical critique written against it |

<!-- Additional skills are appended here as they are written. -->

**Two skills are no longer Markdown alone, and it used to be one.** `icd10-cpt` ships the ICD-10-CM code set at `reference/icd10cm-2026.sqlite` and queries it with `tools/icd10_lookup.py`, so a code is looked up rather than recalled. **`clinical-note` now depends on the same pair**, because [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) made it write codes into the Medatrax diagnosis fields and drift row 20 requires those codes verified rather than recalled. **The lookup still needs nothing installed** — the database is in this repo and `sqlite3` is in the Python standard library — but an agent that cannot run the script is working from recall, and every code it proposes must carry `verify this number`.

**`icd10-cpt` also ships a licensed procedure-code database.**
`reference/procedure-codes-2026.sqlite` is queried with
`tools/procedure_codes_lookup.py` on the encounter's service date. Its HCPCS
Level II rows are built from CMS's complete quarterly Alpha-Numeric public-use
file; its CPT rows enter through `tools/procedure_codes_build.py`'s normalized
licensed CSV seam. The database names the maintainer's 2026 CPT and HCPCS
VitalSource editions as its book authorities and records completeness by code
system. An incomplete-system miss establishes nothing and routes the reader to
the rendered book page under `vitalsource-chrome`; the database never turns a
partial import into a false refusal. The database verifies identity, descriptor,
modifier identity, and date status, not book instructions or whether the
encounter earns the code.

**One code family takes a second committed lookup.** A pediatric `Z68.5-` is a CDC growth-chart percentile, so `clinical-note` and `icd10-cpt` run `tools/cdc_percentile.py` against `reference/cdc-bmi-for-age-2022.csv` as well as checking the returned codes against ICD-10-CM. Where only whole-year age is known, the tool fills and discloses a midpoint month rather than withholding the band. An agent that cannot run it is working from recall, and every pediatric BMI code it proposes must carry `verify this number`. [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123).

**`clinical-note` also depends on committed guideline artifacts, and they need no tool at all.** `reference/guidelines-uspstf.md` holds 143 USPSTF recommendation statements; `reference/thresholds/` holds the numeric decision points for distilled topics, and `reference/thresholds/coverage.md` records every catalog topic as `sheet`, `none`, `non-source`, or `unread`. Shipped artifacts are derived from that registry by `python tools/threshold_coverage.py`, never maintained as a prose count. **A run joins a threshold sheet on the `artifact` column, whatever the row's state.** An artifact on an `unread` row is partial; artifacts on `sheet`, `none`, and `non-source` rows record completed sweeps of different kinds. Where a sheet covers what a Plan item asserts, the skill consults it rather than recalling it, and the citation goes in the tier block and never in the note body. **They are Markdown in this repo, so a consumer opens them with the same reader they opened the skill with** — the corpus behind them stays outside ([#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87)) and nothing needs it. Drift row 24, and *Guideline sheets* in the skill. **The two sheet families' silences do not mean the same thing** and the skill says so at length: USPSTF is 90 of 90 documents so a missing row is a real negative finding — though it says the *USPSTF* has issued no statement, never that the item is unindicated — while a missing threshold row is not a negative finding at all. The registry makes the directory-level distinction explicit: `none` records a completed read with no decision point, `non-source` records a completed read of a declared non-source form, and `unread` establishes nothing. [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85), [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429).

**The tier is what skipping a command costs.** A **Required command** is one a skill cannot skip without changing what the run can claim: the skill requires its clean exit, the command produces the deliverable, or it produces the readback a required check reads. A **Named command** changes no claim when skipped; it only saves a reading by eye or records where a figure came from. `clinical-note` names `tools/corpus_census.py` and `tools/filled_vitals_census.py` as provenance for figures it states, and names `tools/spelling_scan.py` as a convenience for the spelling rule the skill states in full. The writing-sample use of `tools/docx_read.py` in the shared voice reference is likewise an ordinary named reading rather than a required claim.

**The note skills require their terminal graders.** `batch-shift` uses `tools/filled_vitals_census.py`, `clinical-note` uses `tools/differential_scan.py`, and `icd10-cpt` uses `tools/specificity_scan.py`. Their skills require the `--submission` run to exit 0 before completion. The shift and standalone-note graders also verify that the Medatrax posted reading's `SUBMISSION-SHA256` still matches the note bytes; the coding worksheet uses the owning note's submission key and writes no second posted reading. After an install has been tried, a consumer without the command can walk the written checks by eye but cannot call the run mechanically verified.

**`tools/aar_scan.py` is a Required command for `aar`.** It extracts the run and grades the after-action record; the invoking skill resumes its completion grader only after exit 0. After an install has been tried, a consumer without the command can walk the same rows by eye but cannot call the after-action review mechanically verified.

**`tools/anchor_scan.py` is a Required command for `icd10-cpt` and for the descriptor-agreement steps inherited by `clinical-note` and `batch-shift`.** Its ordinary mode grades worksheet anchors. Its agreement-brief mode produces the answer-free note/code brief, and its agreement-read mode grades the separated reader's record and the bidirectional note/worksheet code bind. Without a clean required run, descriptor agreement and the paired code populations are not mechanically verified.

**`tools/coding_freshness.py` is a Required command for a finalized `clinical-note` coding worksheet and for `batch-shift`'s Review sheet.** It checks each batch against the live CDC ICD-10-CM and CMS HCPCS release pages, binds CPT to the private edition-and-fingerprint receipt and committed MDM sheet, checks database completeness and every selected code on the service date, and refuses an office patient status without both an identity-map-or-Medatrax label and a SHA-256 fingerprint of that private evidence. ED encounters carry a stated ED setting and no new/established status axis. Its detailed JSON receipt stays private; only `Coding freshness: PASS` is rendered. A consumer without network access or the private CPT receipt cannot call the batch current or final and cannot render a Review sheet ready for approval.

**`tools/entry_copy.py` is a Required command before Medatrax note entry on `clinical-note` and `batch-shift`.** Given a finished note, it writes `entry-copies/<note filename>` beneath the note's directory after removing welded `NOT CODED:` clauses, checking the four Plan labels, and applying measured portal-character substitutions to pasted sections. An unmeasured non-ASCII character there refuses. A refusal writes no Entry copy and blocks posting. The saved note form is compared with that copy; `SUBMISSION-SHA256` still hashes the finished note. It accepts a relabeled note returned to an existing run.

**`tools/form_sections.py` is a Required command before Medatrax note entry on `clinical-note` and `batch-shift`.** It reads each Entry copy, partitions every line into preamble, `S`, `O`, `A`, `P`, and tail, and writes `private/form-sections/note-N.json` only when absent. An existing record is compared and any divergence is reported without changing exit status or overwriting the evidence; replacement requires `--replace`. A refusal blocks posting; a divergence does not.

**`tools/cpt_mdm_sheet.py` is a Required command for the committed CPT E/M MDM sheet.** Its comparison mode requires distinct transcript paths and records exact two-reader agreement, printed-page locators, date, and per-entry SHA-256; its ordinary and `--staged` modes refuse missing coverage or changed entries. The pre-commit hook runs the staged mode when an edition sheet changes. Its `--write-receipt` mode derives the private CPT source identity and edition boundary from the procedure database into this checkout's `scratch/sessions/<key>/`. The sheet in `reference/cpt-em-mdm-2026.md` supplies the licensed MDM grid and dependent definitions, not other CPT instructions. `coding_freshness.py` requires a passing sheet whose line-ending-normalized content matches `HEAD` and whose edition covers the service date for a finalized ED or office E/M selection.

**`tools/peer_critique_scan.py` and `tools/voice_model_scan.py` are Required commands for `peer-critique`.** The first is its completion grader; after an install has been tried, a consumer without it can walk the same rows by eye but cannot call the run mechanically verified. The second is required before drafting against the clinician's model; without it the draft is not written against the model. `tools/voice_model_scan.py` is a Required command for `discussion-reply` and `setup-clinical-skills` on the same terms.

**`practicum-case-study` requires its committed readers, graders, and producers.**
`tools/research_ledger.py`, `tools/reference_scan.py`, `tools/checks_ledger.py`, and
`tools/case_study_scan.py` grade required stages of the run. After an install has been tried, a
consumer without any of them can walk the same rows by eye but cannot call the run mechanically
verified. Without `tools/docx_read.py --normalize`, an evidence search can miss words the page
contains and read that miss as a settled negative; without `--numbering`, the numbering check has
no readback. `tools/docx_write.py` produces the Word document; without it there is no document.
`tools/case_study_render.py` produces a bounded Word export
and retained page pixels, and `tools/render_scan.py` grades mechanical rendered-page coverage.
`practicum-case-study` step 9 writes the retained-pass layout, route order, numerator, denominator, final-pass
rule and exit meanings in full, so after the install has been tried a consumer without Python can walk the same evidence by eye; it
cannot call the render or coverage mechanically verified. The commands do not replace
`tools/checks_ledger.py`: `case_study_render.py` produces the pass, `render_scan.py` grades that
canonical retained passes contain readable pixels for the final export's pages, and
`checks_ledger.py` grades the reader's substantiated `the rendered document` verdict.

**`discussion-reply` depends on `tools/discussion_reply_scan.py`.** The CLI is the deterministic
grader for the roster name, word floor, reference minimum, citation resolution, numeric-claim
trace, source reuse, empty-or-self-restating invoked-property refusal, and the invoked-source and pre-#496 marker counts.
A consumer that cannot run it can walk the
same checks from [discussion-reply](skills/discussion-reply/SKILL.md) step 4, but cannot call the
run mechanically verified. Its claim records use `tools/research_ledger.py` on the same full written contract as
`practicum-case-study` step 3. `tools/voice_model_scan.py` is required before the reply is drafted
against the clinician's model; without it the draft is not written against the model. Its posting step builds the submission with `tools/post_html.py`, which
writes every reference URL as a link; a consumer that cannot run it types the reply, makes every
reference URL a link with the editor's link control, and confirms the links in the posted reading.

**`discussion-post` depends on committed graders.** It uses `tools/research_ledger.py` and
`tools/reference_scan.py` unchanged, then `tools/discussion_post_scan.py` grades the signed word
floor, reference minimum, body-number trace and citation-to-record trace while counting the ceiling,
invoked sources, unfilled invoked properties, and pre-#496 markers without grading them. A consumer
that cannot run the new command can, after the install has been tried, walk the same rows
from [discussion-post](skills/discussion-post/SKILL.md) step 6, but cannot call the run mechanically
verified. Its submission HTML comes from `tools/post_html.py`, which writes every reference URL as a
link, and `tools/docx_write.py` produces its archival Word document. Without that producer there is
no archival document. Its declared limits remain reader-owned and live in
`discussion_post_scan.NOT_REACHED` rather than in a second prose copy.

**`tools/discussion_post_render.py` is Required after an observed Composer message-size refusal
on `discussion-post`.** It retains a page-faithful Word export, page pixels, and the checked
Markdown fingerprint for the attachment fallback. Without its clean exit and a visually checked
page reading, the attached `.docx` cannot receive the fallback go-ahead or pass the terminal grader.

**The shared UpToDate path depends on committed store and sheet tools.**
`tools/uptodate_store.py` ingests one deliberately supplied dump into `scratch/uptodate/`, writes
its per-dump manifest and FTS5 index, searches the accumulated store, and reports unfiled
topic-shaped material without ingesting it. `tools/uptodate_sheet.py` grades staged
`reference/uptodate/` topic sheets against that private source. A consumer without these commands
can read the manifest and the complete rules in
[reference/uptodate/README.md](reference/uptodate/README.md), but cannot call the store searchable
or the sheet mechanically verified. `research_ledger.py` widens its evidence-membership join from
the current dump to that accumulated manifest population and applies the signed publisher-review
window, waived only by the account answer in the profile.

**`course-assignment` depends on committed artifact adapters and graders.**
`tools/course_assignment_scan.py` dispatches the signed artifact to `tools/deck_scan.py` or
`tools/assignment_docx_scan.py`. `tools/deck_render.py` retains PowerPoint's page-faithful export
and slide pixels; `tools/assignment_docx.py` produces the rich Word package and
`tools/assignment_docx_render.py` retains Word's page-faithful export and page pixels.
`tools/render_scan.py` grades final-pass coverage, and `tools/research_ledger.py` grades the per-run
source-class and recency policy. After the install has been tried, a consumer without those
commands can walk the selected branch's rows and the documented research-record contract in
[course-assignment](skills/course-assignment/SKILL.md), but cannot call the run mechanically
verified.

**`vitalsource-chrome` depends on its committed Codex Chrome patcher.**
`skills/vitalsource-chrome/scripts/patch_codex_chrome.py` installs the reviewed stable top-level
attachment and XHTML document classification into both the bundled Chrome cache and active desktop browser runtime. It preserves the
first pre-patch bytes and refuses a bundle whose reviewed seams have drifted. A Codex consumer who
cannot run it can still read the complete screenshot-verification contract in
[vitalsource-chrome](skills/vitalsource-chrome/SKILL.md), but cannot call the Codex Jigsaw
compatibility mechanically installed. A refusal starts the skill's verified-attempt, repair,
Claude-handoff, and unreadable-source route. Other browser agents use their own native lifecycle
and do not run the Codex patcher, while the skill's visible-page reading standard binds them too.

**Run `/setup-clinical-skills` before the others.** Everything about *which* clinician — courses, hour targets, preceptors, sites, payer distribution, and which patient is which — is per-account and lives in `scratch/`, gitignored. `reference/medatrax-fields.md` holds how Medatrax behaves; the profile holds who you are. Where they disagree, the profile wins.

**`tools/guidelines_search.py` is a named command.** It needs a guideline index built locally outside the repository; without one it reports that it did not search. `reference/guidelines-catalog.md` remains the committed way to find a document.

**PDF engine prerequisites.** The consumer floor is Python 3.10. The `batch-shift`, `practicum-case-study`, `discussion-post`, and `course-assignment` skills need the PDF engine, PyMuPDF, on the machine that runs them; no other skill needs a Python package. Run `python tools/pdf_engine.py` to check whether it is present and to print the install line when it is not. `setup-clinical-skills` step 0 runs that check and asks before installing, and each of the four skills runs it again before the step that needs the engine. `batch-shift` step 2 then runs `python tools/day_file_text.py`; skipping that command costs the shift's text reaching the PHI name check. Its step 3 runs `python tools/name_index.py --write`; skipping that command leaves the shift's patient names out of the PHI name check, and the skill's exit rules remain unchanged. When the engine cannot be installed, the coursework skills walk their documented rows by eye and report that the run is not mechanically verified; `batch-shift` instead reads every page with the agent's own PDF reader. On Windows, `practicum-case-study` and `course-assignment` use Microsoft Word or PowerPoint for automatic page export; without the applicable application the clinician exports by hand, and a submission with no page-faithful export stops.

## Standing rules

These bind every skill in this repo.

1. **No PHI is ever committed.** Identifiers become placeholders (`[PT]`, `[DOB]`, `[MRN]`) the moment they are read. Anything committed for testing is a **fixture** — derived from a working file with the visit date and site removed, never a copy of one. See [fixtures/README.md](fixtures/README.md).

   **Two gitignored directories, split by stage.** Working material — day files, the identity map, the account profile — lives in `scratch/`. **Anything finished and handed over — a note, a batch document, a case study — is written to `output/`.** Never write a finished note anywhere else, and never into the repo root: everywhere else is tracked, and a note written there is a committed patient record one `git add -A` later.

   A pre-commit hook enforces this rather than trusting it to be remembered (`tools/phi_scan.py`; setup in [README.md](README.md)). It is a seatbelt, not a vault — it does not replace reading this rule.
2. **Every line is given, derived, or filled.** These are academic notes against a school rubric, so sections the shorthand cannot supply are generated — but **filled content is unremarkable unless one of the two narrow exceptions below applies**. Every abnormal finding, lab value, imaging result, and diagnosis traces to the source. Filled lines are listed for the clinician to confirm before submission. Full rules in [clinical-note](skills/clinical-note/SKILL.md).

   **Exception — vitals, body measurements and the OLDCARTS pain score.** These qualify by a test rather than by sitting on a list: a box demands a value, and the shorthand constrains none. A missing one is filled with the value that patient most plausibly had, worked up in the note if it lands abnormal (drift row 4, which grants it no exemption for being generated), and disclosed in the FILLED block like everything else generated. **No exam finding, symptom, or result is ever filled, however plausible** — a severity scores a complaint the shorthand already documents and never supplies one, and where the shorthand documents no pain the 0/10 is a given.

   **Exception — assignment of a given family-disease bundle.** When the shorthand names diseases in the family but omits which relative had each one, the diseases remain given and only their relative-to-disease relationships are filled. Those relationships may be positive, are declared in `FILLED·asserted`, add no disease to the bundle, and never support a patient diagnosis, finding, or result.

3. **Proposals are labeled.** Any clinical reasoning the agent contributes — a differential, a code, a plan item — appears under `PROPOSED (verify before use)`, outside the document body, for the clinician to accept or drop.

   **Exception — finalized Review-sheet coding.** After the supervised Medatrax handoff has been incorporated, the note path may assert final codes only in its one-line E/M statement and separated `Coding worksheet`, and only when account-backed patient status, the authenticated CPT MDM read, descriptor agreement, and `tools/coding_freshness.py` all pass. The private anchored worksheet keeps its proposal and provenance grammar. This exception is for the selected codes only; it does not turn a generated differential, diagnosis, or plan action into a given.
4. **American English, always. No British spelling ever reaches the output.** `dyspnea`, `edema`, `cesarean`, `sulfate`, `nebulizer`, `liter`, `gray`, `labeled` — and drug names take the United States generic: `acetaminophen`, `epinephrine`, `albuterol`. These are notes for an American program read by American faculty, and a reader given the other drug name has to translate it before they can check a dose.

   **This rule has the widest surface.** Rules 1 to 3 govern the finished note; this one governs everything the repo emits and everything it contains — note bodies, tier blocks, Medatrax fields, filenames, commit messages, ticket text, and prose about the skills including this file. There is nowhere a British spelling is correct here, so there is nowhere to carve out.

   **Two exemptions, both narrow, and the rule is unusable without them.**

   **A mention is not a use.** Naming a wrong spelling in order to rule against it is how the rule gets written down at all — this paragraph, the table below, issue #73 and the commit that landed all of it are each full of British spellings and each correct. `tools/corpus_census.py` writes `apnoea` in a comment explaining that the spelling is deliberately *not* matched; correcting it would destroy the sentence. A sweep that greps for the strings will hit these, so the test is whether the text is **using** the spelling or **reporting** it.

   **A run record is evidence.** A preserved record stays byte for byte what its run produced apart from the redactions its own README declares, and keeps any British spellings the run emitted because editing them would falsify the thing it exists to prove. **How many is a question for `python tools/spelling_scan.py --record`, never for this sentence.** The record's identity, counts and dated changes stay in its withheld fixture files under [fixtures/README](fixtures/README.md)'s blind-instruction rule. Issue #73.

   The full table, and what was already found by it, is in [clinical-note](skills/clinical-note/SKILL.md) under *Conventions*.

   **A scanner reads the same table** (`tools/spelling_scan.py`), and it is **advisory** where rule 1's is not — a spelling never refuses a commit here. It found a British spelling in a skill file that the hand sweep writing this rule had missed, which is the argument for having it. Since #104 it scans staged or tracked Markdown and Python contents plus filenames, and `tools/hooks/commit-msg` scans the local commit message; ticket and PR text remain the manual surface. A counted `# spelling-scan: mentions N` immediately above one Python statement is the Python equivalent of a code span, and a stale count fails rather than widening the exemption. It still holds the table rather than the language, which is the argument for still reading this rule.

   *(This sentence read "standing rule 1 stays the only thing that refuses a commit here" until 2026-08-16. Standing rule 1 can refuse a commit; this spelling scanner cannot. The current inventory and staging conditions live in `tools/hooks/pre-commit`. Rule 1's two checks are still the only ones binding **every** commit, which is the part that mattered to this rule and the reason the sentence survived a merge after it stopped being true.)*
5. **Delete an exact figure unless its value changes a reader's decision.** A useful current figure derived from a tracked source stays only when the same change binds it to that source with an equality-backed test. The test derives the value independently and compares the current claim or the property it supports; another hand-kept copy is not a source of truth.

   **An untracked source cannot support a current figure.** A measurement from `scratch/`, `output/`, a gitignored build artifact, or an out-of-repo source that the suite cannot inspect is removed from current prose. It may survive only as an explicitly historical measurement that states its date, units, and derivation command or other provenance. A rebuild time or file modification time does not establish which code produced an artifact. Shared-artifact ownership and producer identity belong to #184 and #276; this rule is #180's boundary for published prose.

6. **Parallel work has one writer per artifact and one private output location per writer.** Worktrees do not supply this isolation: subagents in one task share a worktree, and fixed paths outside every worktree are shared by all of them. Before a fan-out starts, the orchestrating context gives every writing pass a new run-unique file or directory that no sibling can read or write. Parallel passes never append to one file, write into one directory, or use a fixed external output path. Where several results belong in one artifact, passes return them and the orchestrating context is the sole writer.

   **Browser tabs are private output locations too.** Each context acts only on an **Owned tab**: one it opened, or one the clinician handed it in chat; the main agent never hands a tab to a subagent. The orchestrating context states this tab rule in every brief that may reach a browser, and no skill file copies it. Every page action names the owned tab's id. Where a tool cannot name a tab by id, browsing passes run one at a time, each opens a fresh tab before its first page action and acts only while no other context is acting in the browser; the record states that tabs were not addressed by id and that the clinician switching tabs mid-pass is unprotected. A subagent closes its tabs before returning, and the main agent closes its tabs after its terminal step. A tab kept at the clinician's request or one that failed to close is named in the report, so silence means none remain.

   **Briefing surfaces apply their kind's floor.** Before a **Fan-out brief** starts, the orchestrating context writes the destination file's heading for every expected record, and every refutation leg is briefed to refute rather than confirm. If parallelism is unavailable, it may work those same briefs one at a time and records that the refutation leg was self-authored. A **Second reader** does not complete when no second context is available. A **Grader handoff** may degrade to the author running its committed command only when the raw result is preserved and reported verbatim rather than summarized.

   **Authors do not check or tune their own generated artifacts.** A writing pass returns its output without running a scanner over it. After every writer has finished, the orchestrating context gathers the results and a non-authoring context runs the per-file and whole-set checks over that completed state. If a check fails, the orchestrator records the original finding before asking the author to correct it; a fresh non-authoring context checks the correction again. An author's self-report is never substituted for either read.

   **A run-unique path is temporary, not a growing archive.** Never reuse it. After the final artifacts have been written and the independent checks have completed, the orchestrator removes every private path. An aborted run cleans its private paths before it exits. If cleanup fails, the exact remaining path is reported; silence means no temporary artifact was left behind. This rule binds paths under `scratch/` and `output/` and paths outside every checkout alike. Fixture generation applies the concrete sequence in [fixtures/README.md](fixtures/README.md). Issue #206.
