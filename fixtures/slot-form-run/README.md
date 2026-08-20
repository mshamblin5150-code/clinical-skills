# slot-form-run

Six finished `clinical-note` notes on the Comprehensive SOAP branch, produced 2026-08-18. **This is the first committed `clinical-note` run whose differential is written in the slot form [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) mandates**, and that is the whole reason the directory exists — [#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162).

## What it is for

`tools/differential_scan.py` grades drift row 22's mechanical limb: no code marked `NOT CODED` may sit in an entry's code slot. Until this landed, **every committed directory the scanner could be pointed at was refused before it read anything** — `fixtures/filled-anchor/notes` pins no code with a hyphen, and `fixtures/filled-anchor/run-2` is an `icd10-cpt` worksheet set the tool is pointed away from by design. So the check ran against synthetic notes in `tools/test_differential_scan.py` and against nothing else, and CI graded no real output.

**Every one of these six carries both halves of a row-22 violation** — differential entries in the slot form *and* welded refusals — so the failure path is reachable on committed material rather than only on a note a test wrote. `differential_scan.NOT_VALIDATED_AGAINST`'s first row is what states the part that is still not reached, and it is re-derived by an assertion rather than written down twice.

## Where they came from

Produced by `clinical-note` over **six committed, already-de-identified fixture shorthand cases**, one note each. The filename records the source:

| This file | Source shorthand |
| --- | --- |
| `day-a-case-06.md` | [day-a/shorthand/case-06.md](../day-a/shorthand/case-06.md) |
| `day-b-case-02.md` | [day-b/shorthand/case-02.md](../day-b/shorthand/case-02.md) |
| `day-b-case-07.md` | [day-b/shorthand/case-07.md](../day-b/shorthand/case-07.md) |
| `day-b-case-11.md` | [day-b/shorthand/case-11.md](../day-b/shorthand/case-11.md) |
| `hedged-dx-case-03.md` | [hedged-dx/shorthand/case-03.md](../hedged-dx/shorthand/case-03.md) |
| `peds-bp-case-05.md` | [peds-bp/shorthand/case-05.md](../peds-bp/shorthand/case-05.md) |

**The selection is not this ticket's and there is no curation to defend.** These six are [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96)'s allergy-placement ruling cohort, chosen by [#201](https://github.com/mshamblin5150-code/clinical-skills/issues/201) months before anything here was about a scanner, and scored in the four sets' own `assertions.md`. **A set chosen after reading the notes would be a set chosen knowing which ones pass**, which is the objection `filled-anchor/notes` answers by being a whole shift; this one answers it by predating the question.

The run's working copies live in `scratch/ticket-201-run/` and are gitignored. These are byte-for-byte copies **apart from the two site names *De-identification* below records** — one note of the six, and the only edit ever made.

## The commit this belongs to

Made on #201's branch against base `48ac3ca`, merged as `6934db9` ([PR #210](https://github.com/mshamblin5150-code/clinical-skills/pull/210), 2026-08-18). `skills/clinical-note/SKILL.md` was last moved by `2bcbb32` before the run.

**The slot form predates it and that is what makes the set usable here.** #153's ruling landed 2026-08-16; the run is from the 18th. Nothing was written to suit this directory, which did not exist.

## De-identification

**One note named both practicum sites, and no scanner in this repo would have caught it.** `hedged-dx-case-03.md`'s `PRIMARY PAYMENT METHOD` line reasoned from the site rule and named the two sites to do it. Both are now `[SITE-A]` and `[SITE-B]`, on [filled-anchor/notes](../filled-anchor/notes/README.md)' committed mapping — **`[SITE-A]` implies `Self-pay/other`, `[SITE-B]` implies `Medicaid`** — checked against that set before the edit, so the two committed runs cannot disagree about which is which.

This is [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)'s finding arriving a second time, from the same direction, on a different skill run: **a generated note's provenance is its whole context, not its prompt.** All six inputs were already de-identified; the generating skill read the account profile in `scratch/` for a payer and had the site names whether or not its encounter input did.

**`phi_scan` returns zero findings over these six, before the edit and after it.** A site name is not a patient name and no shape rule matches one — the hole is listed among that scanner's known limits and it is not fixed by this directory. Recompute both figures rather than trusting this paragraph:

```bash
grep -c '\[SITE-A\]\|\[SITE-B\]' fixtures/slot-form-run/*.md
```

**Visit date, site and preceptor are `GAPS` in all six**, inherited from inputs that already had them removed; nothing here had a date to strip. Names are `[PT]` under [standing rule 1](../../AGENTS.md). Ages and findings stay, because they are what the run is.

| | Removed by | Where |
| --- | --- | --- |
| Patient names | the source sets, already `[PT]` | standing rule 1 |
| Visit date | the source sets, before commit | [fixtures/README](../README.md) |
| Site name | **here, on the way across** | [fixtures/README](../README.md) |
| Ages, findings, course code | kept | `filled-anchor/notes`' precedent, which keeps all three |

## What it is not

**It is not a reference and it is not correct output.** It is what the skill did on one day at one commit. Where a note is wrong, that is a fact about the run.

**It is not a scored set and it has no `assertions.md`.** The rows that graded these six live in [day-a](../day-a/assertions.md), [day-b](../day-b/assertions.md), [hedged-dx](../hedged-dx/assertions.md) and [peds-bp](../peds-bp/assertions.md); this directory is the run record, on [filled-anchor/run-2](../filled-anchor/run-2/README.md)'s arrangement. Adding rows here would score the same run twice under two denominators.

**A clean scan is not a walked row.** `differential_scan.py` settles whether a refused code sits in a slot. Whether a label is what its descriptor says — row 22 proper — is a reading, and paraphrase is permitted. Nothing here has walked that.

**And it must not be tuned.** These six exit 0 and that is the honest outcome; a run edited until the checker fires is material written to make a check pass its own test, which is the trap [#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162)'s own CI comment names. The exit-1 branch is exercised by **mutating** a copy of this material in `tools/test_differential_scan.py`, where the mutation is visible in the test rather than baked into the record.

## Figures, and the commands that recompute them

**Nothing here is restated in `CLAUDE.md` or in the module**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. Run the command.

| | Recomputed by |
| --- | --- |
| Notes, coverage, entries, refusals, exit status | `python tools/differential_scan.py fixtures/slot-form-run` |
| Site-name markers | the `grep` above |
| Per-note entries and refusals | pinned by `TheCommittedSlotFormRunIsReadable` in `tools/test_differential_scan.py` |

The scanner's counts are **not** copied into this file for the reason that section gives: a figure a reader can regenerate in one command should not also exist as a number somebody typed.
