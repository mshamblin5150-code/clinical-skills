# Clinical skills

A set of agent-agnostic skills for converting ER-style clinical shorthand into documentation. Each skill is a folder under `skills/` holding a `SKILL.md` — plain Markdown with YAML frontmatter, readable by any agent.

## How to use a skill

**Read the skill file before starting the task.** Do not work from the one-line summary below — it is an index, not the instructions.

| Skill | Read | Use when |
| --- | --- | --- |
| clinical-note | [skills/clinical-note/SKILL.md](skills/clinical-note/SKILL.md) | Encounter shorthand needs to become a comprehensive SOAP or an FNP H&P |
| batch-shift | [skills/batch-shift/SKILL.md](skills/batch-shift/SKILL.md) | A whole shift is pasted at once and needs splitting into encounters |
| icd10-cpt | [skills/icd10-cpt/SKILL.md](skills/icd10-cpt/SKILL.md) | A documented encounter needs ICD-10-CM or CPT codes proposed |
| setup-clinical-skills | [skills/setup-clinical-skills/SKILL.md](skills/setup-clinical-skills/SKILL.md) | **Run once first.** A new clinician's portal, program, picklists and patient identity map need configuring |

<!-- Additional skills are appended here as they are written. -->

**One skill is no longer Markdown alone.** `icd10-cpt` ships the ICD-10-CM code set at `reference/icd10cm-2026.sqlite` and queries it with `tools/icd10_lookup.py`, so a code is looked up rather than recalled. **There is still nothing to install** — the database is in this repo and `sqlite3` is in the Python standard library — but an agent that cannot run the script is working from recall, and every code it proposes must carry `verify this number`.

**Other skills name a tool without depending on one, and the difference is worth keeping straight.** `clinical-note` cites `tools/corpus_census.py` and `tools/filled_vitals_census.py` as the provenance of figures it states, and `batch-shift` offers the second as a faster way to do a check its own step describes in prose. **Skip every one of them and the skill still works** — the instruction is complete without the command, which is what makes `icd10-cpt` the one exception rather than the first of several. A citation that stopped being optional would need this paragraph rewritten.

**Run `/setup-clinical-skills` before the others.** Everything about *which* clinician — courses, hour targets, preceptors, sites, payer distribution, and which patient is which — is per-account and lives in `scratch/`, gitignored. `reference/medatrax-fields.md` holds how Medatrax behaves; the profile holds who you are. Where they disagree, the profile wins.

## Standing rules

These bind every skill in this repo.

1. **No PHI is ever committed.** Identifiers become placeholders (`[PT]`, `[DOB]`, `[MRN]`) the moment they are read. Anything committed for testing is a **fixture** — derived from a working file with the visit date and site removed, never a copy of one. See [fixtures/README.md](fixtures/README.md).

   **Two gitignored directories, split by stage.** Working material — day files, the identity map, the account profile — lives in `scratch/`. **Anything finished and handed over — a note, a batch document, a case study — is written to `output/`.** Never write a finished note anywhere else, and never into the repo root: everywhere else is tracked, and a note written there is a committed patient record one `git add -A` later.

   A pre-commit hook enforces this rather than trusting it to be remembered (`tools/phi_scan.py`; setup in [README.md](README.md)). It is a seatbelt, not a vault — it does not replace reading this rule.
2. **Every line is given, derived, or filled.** These are academic notes against a school rubric, so sections the shorthand cannot supply are generated — but **filled content is always unremarkable**. Every abnormal finding, lab value, imaging result, and diagnosis traces to the source. Filled lines are listed for the clinician to confirm before submission. Full rules in [clinical-note](skills/clinical-note/SKILL.md).

   **Exception — vitals, body measurements and the OLDCARTS pain score.** These are the single exception to *filled content is unremarkable*, and they qualify by a test rather than by sitting on a list: a box demands a value, and the shorthand constrains none. A missing one is filled with the value that patient most plausibly had, worked up in the note if it lands abnormal (drift row 4, which grants it no exemption for being generated), and disclosed in the FILLED block like everything else generated. **No exam finding, symptom, or result is ever filled, however plausible** — a severity scores a complaint the shorthand already documents and never supplies one, and where the shorthand documents no pain the 0/10 is a given.

3. **Proposals are labeled.** Any clinical reasoning the agent contributes — a differential, a code, a plan item — appears under `PROPOSED (verify before use)`, outside the document body, for the clinician to accept or drop.
4. **American English, always. No British spelling ever reaches the output.** `dyspnea`, `edema`, `cesarean`, `sulfate`, `nebulizer`, `liter`, `gray`, `labeled` — and drug names take the United States generic: `acetaminophen`, `epinephrine`, `albuterol`. These are notes for an American program read by American faculty, and a reader given the other drug name has to translate it before they can check a dose.

   **This is the widest of the four.** Rules 1 to 3 govern the finished note; this one governs everything the repo emits and everything it contains — note bodies, tier blocks, Medatrax fields, filenames, commit messages, ticket text, and prose about the skills including this file. There is nowhere a British spelling is correct here, so there is nowhere to carve out.

   **Two exemptions, both narrow, and the rule is unusable without them.**

   **A mention is not a use.** Naming a wrong spelling in order to rule against it is how the rule gets written down at all — this paragraph, the table below, issue #73 and the commit that landed all of it are each full of British spellings and each correct. `tools/corpus_census.py` writes `apnoea` in a comment explaining that the spelling is deliberately *not* matched; correcting it would destroy the sentence. A sweep that greps for the strings will hit these, so the test is whether the text is **using** the spelling or **reporting** it.

   **A run record is evidence.** `fixtures/filled-anchor/notes/` is a byte-for-byte copy of what one run produced and keeps the eight British spellings that run emitted, because editing it would falsify the thing it exists to prove. Issue #73.

   The full table, and what was already found by it, is in [clinical-note](skills/clinical-note/SKILL.md) under *Conventions*.
