# An AAR quotation stretch already on main is not run material

**Measured at:** 7147b01c9e9960987a0b45996ee20ea22c944416

[#1465](https://github.com/mshamblin5150-code/clinical-skills/issues/1465) was filed from the
after-action review of a `batch-shift` run. A `skill-file` ticket proposed changing one line of a
`clinical-note` exam template, and `skills/aar/SKILL.md` requires such a ticket to carry the exact
proposed diff. The run's notes had copied that template line word for word, so the publish hook's
quotation gate refused the body as a copied private-run span. The workaround cut the diff down to
the changed phrase and a file reference, which gave up the exactness the skill asks for. Grilled
2026-10-08 against `main`, where the freshness gate read `FRESH`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The gate compares stretches and knows only one source.** `tools/tracker_publish_hook.py`
`_quotes_run_material` normalizes whitespace and case, then refuses an AAR publication when any
`AAR_QUOTE_SPAN_CHARS`-character stretch of its body also occurs in a `.md`, `.txt` or `.json`
file under the run directory outside `aar/`. That length is 80, measured under
[ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 13. The gate has no notion of where a matching stretch originated.

**A template line is long enough to trip it alone.** In `skills/clinical-note/SOAP.md`, the GI
normal-exam line is 102 characters and the cardiovascular line is 148, so a diff quoting either
line whole contains at least one 80-character stretch that a note copying the template also holds.

**The two proposals the ticket offered.** Exempt stretches that also occur verbatim in a tracked
repository file, or have the AAR skill name a reduced diff form of file, line number and changed
phrase.

## Ruling 1 — the gate gives way, not the AAR skill

The quotation gate exempts a matched stretch that also occurs word for word, after the gate's own
normalization, in text the repository already publishes. The AAR skill keeps its requirement of
the exact proposed diff. The gate's subject is run material, and a template line a note copied is
the repository's text rather than the run's. The comparison stays per stretch, so a stretch carrying
anything the run filled in, such as a patient's values written into a template line, matches no
published file and is still refused.

The reduced diff form was declined because the clinician would rule on a skill change without seeing
the whole old and new lines, a line number goes stale when the file moves, and a changed phrase with
its context can still reach 80 characters and be refused anyway. Doing both was declined because the
reduced form becomes an escape hatch the exemption makes unnecessary.

## Ruling 2 — already public means every text file on origin/main

The exemption reads the text files of the local `origin/main` reference, the branch the repository
publishes. It is consulted only after a run stretch has matched, so an ordinary publication and an
AAR body that copies nothing pay nothing for it. Text merged but not yet fetched does not match, and
the gate refuses as it does today; that is the safe direction.

Restricting it to `skills/` was declined because every file on `main` is equally public, and the
same refusal would recur for a diff to a reference sheet or threshold sheet a note copied. Reading the
tracked files of the checkout running the hook was declined because an unpushed or staged change
would then count as public when it is not, which is the one direction this gate must not fail in.

## Ruling 3 — the report states the exemption on every run

The gate's report line always states how many matched stretches it let through as already on
`main`. When `origin/main` cannot be read, the exemption is not applied, the gate refuses on the
unexempted match, and the report says the exemption was not applied and why. Printing the clause
only when the exemption fires was declined because a report without it reads the same as one from a
hook with no exemption. Leaving the report unchanged was declined because an exempted stretch would
pass in silence.

## What this does not reach

A stretch that the run produced independently and that happens to equal published text is exempt,
because the gate cannot tell coincidence from copying; republishing text already on `main` discloses
nothing new. A paraphrase of run material still passes, as ADR 0109 ruling 13 already declares. A
template reformatted on `main` after the run copied it no longer matches and is refused; the remedy
is the same rewrite the gate already asks for.
