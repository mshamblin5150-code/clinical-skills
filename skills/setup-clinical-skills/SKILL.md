---
name: setup-clinical-skills
description: Configure this repo for one clinician's Medatrax account and program — portal access, program hours, picklists, declared field defaults, and the patient identity map. Run once before first use of the other clinical skills.
disable-model-invocation: true
---

# Setup clinical skills

The skills in this repo carry two kinds of knowledge and only one of them travels.

**Universal** — how a SOAP note is structured, what drift is, that `Patient Detail` renders a visit read-only, that a positive Rovsing's sign has to be addressed. True for anyone.

**Per-clinician** — which courses, how many hours, which preceptors, which sites, what the payer mix actually looks like in *their* portal, and which patient is which. None of it transfers, and all of it is currently written into [reference/medatrax-fields.md](../../reference/medatrax-fields.md) from one account.

This skill collects the second kind. It is prompt-driven, not a script: explore, present what you found, confirm, then write.

**Nothing collected here is committed.** Preceptor names, site names and the identity map are all identifying. They are written under `scratch/`, which is gitignored — see standing rule 1 in [AGENTS.md](../../AGENTS.md).

## Process

### 0. Arm the PHI firewall — before collecting anything

Everything after this step writes identifying data to disk. Do this first, in this order, and do not proceed past a failure.

**Enable the pre-commit hook.** Git does not clone hooks, so a fresh clone has none and every commit is unguarded:

```bash
git config core.hooksPath tools/hooks
```

Verify it took, and verify it actually fires — a hook that is configured but silently not running is worse than none, because it reads as protection:

```bash
git config --get core.hooksPath        # must print: tools/hooks
python tools/phi_scan.py --all         # must exit 0 against what is committed today
```

If `python` is not on PATH the hook degrades to a warning and lets the commit through by design. Say so out loud rather than leaving the clinician believing they are covered.

**Create the two gitignored directories and confirm both are ignored:**

```bash
mkdir -p scratch output/notes output/case-studies
git check-ignore scratch output
```

That last command must print **both** `scratch` and `output`. It lists only the paths git is ignoring, so a missing line means that directory is tracked. (Do not add `-q` — it accepts a single pathname and errors on two.)

**If either line is missing, stop and fix `.gitignore` first.** Everything below, and every note the other skills write afterwards, depends on it.

### 1. Explore before asking

- `scratch/` — does `medatrax-profile.md` or `identity-map.md` already exist? If so this is a re-run; read them and confirm rather than re-collect.
- `output/` — already populated? A re-run must not overwrite finished work.
- `reference/medatrax-fields.md` — read it. Much of what you need may already be recorded from a previous account; present it as *someone else's values to overwrite*, never as defaults to accept.
- Is a browser tool available that reaches the clinician's real logged-in session? Portal steps need one.

### 2. Portal access

Confirm the host. `np.medatrax.com` is the NP portal; `medatrax.com` is a different, anesthesia-defaulted login; evaluations live on `evaluations.medatrax.com`. A clinician in another program may be on a different host entirely.

**The agent never types credentials.** The clinician signs in themselves, or the password manager fills the form in their own browser. Confirm the session with `/login/patient.aspx` — the patient list means signed in, a bounce back to the form means signed out. `default.aspx` renders the same public page either way and proves nothing.

### 3. Program and hours

Ask, and record the answers rather than deriving them:

- Which courses, and the documented hour requirement for each. **Medatrax's own Objectives page is not authoritative** — it was stale by 100 hours on one account. The program's own hours breakdown is.
- The area breakdown, if the course has one: family practice, pediatrics, obstetrics, gynecology, geriatrics.
- Whether prior hours carry, or the count starts from zero.
- Course start and end dates, and any documentation deadline. One program removes students from clinical if they fall more than 48 hours behind.
- The minimum number of H&P forms before SOAP becomes the clinician's choice.

### 4. Picklists — read them, do not assume them

Preceptors, sites, case types and Patient Time bands are per-account picklists. Read them off the portal and record the strings **character for character** — one account carries `Wyoming County Health Dept.` with a trailing period and `New River Health - Oak Hill` with a spaced hyphen. A near-miss string does not match.

Also collect the **preceptor name mapping**: day files name preceptors by first name, Medatrax wants `Last,First`. Ask for the mapping directly.

**A name that maps to nobody is a question, not a defect.** The person a day file names may be a physician the clinician rounded with who is not on the picklist at all — in which case nothing is missing from the record and nothing needs mapping. Ask what goes in the box instead, and **write the ruling into the profile**. **Never guess a nearest surname match**: that is how a shift's hours get attributed to someone who was not there, and nothing downstream will catch it.

**This step collects the answer; it does not decide what to do with one.** [batch-shift](../batch-shift/SKILL.md) step 1 owns that — the lookup order, and why a clinician entering his own preceptor of record is a different act from an agent guessing a surname. **Stated there and not restated here on purpose**, so the two cannot drift apart again.

*(This paragraph read "A name that maps to nobody is reported, never substituted" until 2026-08-16, which welded those two acts into one prohibition. [#91](https://github.com/mshamblin5150-code/clinical-skills/pull/91) separated them in `batch-shift` on 2026-08-12 and did not sweep for this second copy, so the two skills gave opposite instructions on one rule for four days. #90.)*

### 5. Declared field defaults — measure, do not inherit

Some fields are never visible at the bedside and need a declared value: `Primary Payment Method`, `Race/Ethnicity`.

**Measure them against this clinician's own record.** Open one full day of existing encounters and count. Do not carry another account's default across — on one account `Medicaid` was recorded as a safe constant and turned out to be six of eleven, with three Commercial and two Medicare beside it.

Record the measured distribution alongside the default, and say how often the default is wrong. A default that is wrong two times in five belongs under `FILLED·asserted` for confirmation; one that is wrong one time in twenty can be filled silently. The number decides, not the habit.

### 6. The identity map — the part that prevents duplicates

**Medatrax never stores a patient name.** It generates a Patient Reference such as `40EEE8DB06FB466` and that is its only handle on a person. So a returning patient can only be found by something the clinician holds outside the portal.

**An encounter entered without matching an existing patient creates a new one.** There is no warning and no merge. Afterwards the two records are indistinguishable, and every visit split across them counts as a separate patient.

Check for it directly: compare total patients against total visits on `studentoverview.aspx`. On one account the figures were **582 patients against 592 visits** — ten repeat visits in a year of family practice, which is not what family practice looks like. That gap is the duplicate count.

Set up the map:

- It lives at `scratch/identity-map.md`, gitignored, and never leaves the machine.
- One row per patient: the name the clinician writes in the day file, the Medatrax Patient Reference, the date first seen, and anything else needed to disambiguate two people with the same name.
- Seed it from the existing record where possible: the clinician's day files carry the names, and the portal carries the references — matching on visit date plus age plus recorded vitals is usually unambiguous.
- Where a day file has **no name against a note**, that encounter cannot be matched and will create a new patient. Record it as unmatched rather than guessing. This is the case worth naming out loud, because it is the mechanism by which the duplicates already in the record were made.

Write the map's format and location into `scratch/medatrax-profile.md` so the other skills know where to look.

### 7. Day files and the Times convention

- Where day-file scans live, and whether they carry a text layer or are image-only.
- The naming convention, and whether the preceptor appears in the filename, in a header, or both.
- Typical shift start and length, which the Times convention uses to estimate visit times.

### 8. Confirm, then write

Show a draft of `scratch/medatrax-profile.md` and `scratch/identity-map.md` and let the clinician edit before writing. Then write both, and tell them:

- That finished notes and case studies are written to `output/`, working material to `scratch/`, and that both are gitignored — so nothing they produce ever reaches GitHub.
- That the pre-commit hook from step 0 is now armed in this clone only, and a clone on another machine needs `git config core.hooksPath tools/hooks` again.
- Which skills read the profile.
- That `reference/medatrax-fields.md` holds the universal Medatrax behavior and the profile holds everything about them — and that where the two disagree, **the profile wins.**
- That re-running this skill is only needed to change accounts, courses or program; the files can be edited directly otherwise.

## Which skills need this

Following the same split as [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s reasoning about load-bearing dependencies:

**Hard dependency — wrong without it, not merely vague.** Any skill emitting a Medatrax entry block, choosing a `Patient Time` band, naming a preceptor or site, or matching a patient to an existing record. That is [clinical-note](../clinical-note/SKILL.md) step 5 and [batch-shift](../batch-shift/SKILL.md) step 6.

**Soft dependency.** The note body itself. A SOAP note is a SOAP note; it is sharper with the program's rubric in view and it does not become wrong without it.
