# blind-run

Seven finished `clinical-note` notes on the Comprehensive SOAP branch, produced 2026-08-20 by seven passes that **were not told what was being measured**. That is the property the set is named for and the only reason it is evidence — [#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162), where the run was asked for, and [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67), which is what it found.

## Why it exists

[#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162) owed *a real run `differential_scan.py` fails*. That cannot be manufactured — a run edited until a checker fires is material written to make the checker fire, which is the trap that ticket's own CI comment names. It can only be looked for. So a run was made and scanned once, and whatever it said was the answer.

**It said the scanner passes.** `differential_scan.py` exits 0. The owed item is still owed, and this set is the second untuned run to decline to supply it.

**And it failed a different scanner.** `filled_vitals_census.py` exits 1 on B13.

## Where they came from

Seven passes, one per case, over the seven committed shorthand cases in [duration-span](../duration-span/shorthand/) and [obesity-bmi](../obesity-bmi/shorthand/) — **the two sets [fixtures/README](../README.md) recorded as never run.** Nothing in them had ever been graded, so nothing had been shaped toward or away from any rule here. The filename records the source.

**The selection is the two sets entire.** There is no curation to defend: every case in both sets was run.

## How it was made

**One directory per pass**, at `scratch/ticket-162-run/pass-N/`, each holding only that pass's input and output. No pass could read another's work. **`fixtures/` was closed to every pass for any purpose**, including the links `SKILL.md`, `AGENTS.md` and `CLAUDE.md` carry into it, and the inputs were copied to neutral paths so there was no inputs directory to be curious about.

**No pass was told a scanner was involved**, which is the load-bearing constraint. A pass that knew drift row 22 was the subject is a pass that would have tuned toward passing it, and the result would be worth nothing.

**The scan was run once, at the end, by a pass that authored nothing** — [#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s option 2. Deliberately not partway through: a scan of a directory several passes are still writing reports on a state that will not exist when they finish, which is the drift recorded in [slot-form-run](../slot-form-run/README.md).

**Every pass was asked afterwards what it read and ran. All seven reported opening nothing under `fixtures/`.** Four ran per-note scanners over an isolated copy of their own file and said so. That audit is a self-report and cannot be made anything better; the defense is the withholding rather than the asking.

## De-identification: no edit was required, and that is not the same as none being needed

**Checked, not inherited.** `phi_scan` reports zero findings over the seven. Every capitalized phrase in them absent from the committed tree was listed and read: all of it is drug names, exam signs and field labels. No date literal of any shape appears. Visit date, site and preceptor are `GAPS` throughout; names are `[PT]` under [standing rule 1](../../AGENTS.md).

**[slot-form-run](../slot-form-run/README.md) needed an edit and this did not, from the same generator on the same profile** — there, one note reasoned from the site rule to choose a payer and named both sites to do it; here the passes wrote the payer without naming a site. **So the leak is a property of how a pass words a decision, not of the input**, and [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)'s rule stands undiminished: a generated note's provenance is its whole context, and the check is run every time rather than reasoned about.

## What it found

**`differential_scan.py` — exit 0.** 7 of 7 notes carry a differential entry; zero unwelded marks, zero malformed slot pins, zero refused codes in a slot.

**`filled_vitals_census.py` — exit 1, B13.** One note shares a filled body with another, and the filled heights collapse onto far fewer values than there are notes. That is #67's subject, reproducing nine days after the committed evidence in [filled-anchor/notes](../filled-anchor/notes/), on different encounters and a later skill text. **The pressure half is clean on this run**, so the two halves of #67 did not move together — which the older evidence cannot show, because there both were in scope at once.

**`block_scan.py` — exit 0.**

**Every note that can contribute to B13 passes alone.** Measured one note per directory: the four notes declaring a filled body each exit 0 by themselves, the three declaring none exit 2, and the run exits 1. **Two passes ran that very tool over their own note during generation and got exit 0** — correctly, because B13 is cross-note and a set of one cannot fail it. The defect is invisible to the pass that commits it even when that pass checks for it with the right instrument.

**The figures are not restated here.** Run the commands, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms:

```bash
python tools/differential_scan.py fixtures/blind-run
python tools/filled_vitals_census.py fixtures/blind-run
python tools/block_scan.py fixtures/blind-run
```

## The prediction, reproduced unedited

Written to `scratch/` **before the run was scanned**, so it could not be adjusted to fit. **Nothing in git proves that ordering** — the whole record arrives in one commit — and the claim is mine rather than the history's. It is reproduced because a prediction stated after the measurement is not one, and because it was partly wrong:

> **The scanner exits 0.** Every prior run this repo can point at does, and the skill mandates the welded form in three places.
>
> **Confidence is not high, and the reason it is not is #97.** A rule written against an untuned real set *split* there — five failing, four already compliant — and the prediction that all nine would fail came from reading two notes. So the honest statement is that exit 0 is likelier than exit 1 and neither is surprising.
>
> **What I expect to be wrong about, if anything:** the exit-2 limbs, not the exit-1 one. A pass that heads no `Differential` or writes entries without pinning a code with a hyphen produces *no parseable entry*, which is exit 2 rather than a clean run — and `fixtures/filled-anchor/notes` is twelve notes doing exactly that. Partial coverage across seven passes is the outcome I would bet on ahead of either clean or failing.

**The headline was right and the hedge was pointed at the wrong risk.** Coverage was total: not one pass headed no differential, not one failed to pin with a hyphen, not one wrote a refusal in the form row 22 retired. **The thing predicted as the likely surprise did not happen at all, and the actual surprise — B13 — was not in scope of the prediction.**

## What it is not

**It is not a reference and it is not correct output.** It is what the skill did on one day at one commit.

**It is not a scored set and has no `assertions.md`.** It is a run record, on [filled-anchor/run-2](../filled-anchor/run-2/README.md)'s and [slot-form-run](../slot-form-run/README.md)'s arrangement. `duration-span` and `obesity-bmi` still read **never run** in [fixtures/README](../README.md)'s table, and that is correct: scoring those sets means walking their rows, which nobody has done. **This run is evidence, not a score**, and treating it as one would fill in two `Last run` cells that nothing has earned.

**It must not be tuned or corrected.** It exits 0 on one scanner and 1 on another, and both are the honest outcome. Editing it in either direction destroys the only thing it is for.

**A clean `differential_scan.py` is not a walked row 22**, and a failing `filled_vitals_census.py` is not a diagnosis — B13 says two notes share a filled body, not which pass was wrong to invent it.

## Standing rule 4

This set is **not** exempt from the spelling scan, on [slot-form-run](../slot-form-run/README.md)'s reasoning and subject to the same unresolved tension — [#321](https://github.com/mshamblin5150-code/clinical-skills/issues/321). It holds no listed form today.
