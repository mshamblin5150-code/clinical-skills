# A gated row set is derived from its sentinel and guarded by a walk in its own module

[#571](https://github.com/mshamblin5150-code/clinical-skills/issues/571) was filed against a
`research_ledger.py` with no declared-limits object; #535's merge then bound the two existing gated
sets' coverage consequence, and [ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md)
rulings 4 and 5 put a #258-governed row set in a second module. Grilled 2026-08-29 against
`origin/main` at `3ef2e74`. **Five decisions, all the clinician's, all on that date.** Nothing is
built here.

## What is ruled

1. **The scope is module-local.** The guard lands in `research_ledger.py`'s suite only. The
   convention is live in four modules in three shapes — `research_ledger.py`'s flag-gated
   `int | None` sentinels, `differential_scan.py`'s population-gated `NOT RUN` strings ruled correct
   by ADR 0063, and the two discussion scanners' boolean gates with inline-literal exempt sets — and
   ruling the shape for four modules from a ticket scoped to one would decide
   [#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550)'s open question by side
   effect. The discussion scanners' unguarded copies are filed as their own ticket, pointed at #550.
2. **The guard is #571's option 3, a test, and the set of gated row sets is derived from the
   sentinel.** A conformance class in `tools/test_research_ledger.py` walks `Scan` for `int | None`
   fields and asserts, for each: a named row-set tuple that `format_report`'s not-graded
   substitution reads; a `BEHAVIOR` row in `DECLARED_LIMITS` — which the existing `HANDLERS`
   identity pin then forces a blind-spot test and a live positive control for; and, driven through
   `main`, `not graded` printed for its rows without the gating flag and counts with it. No second
   object is built: option 1's gated-row-set structure would leave two objects each knowing part of
   a gated set.
3. **The ceiling is declared, not closed.** An author who types a plain `int` and prints `0` has
   declared nothing the walk can see, and no mechanical rule distinguishes an executed zero from an
   omitted group. That is [ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
   ruling 13's ceiling arriving at a row set, and it is stated beside the test.
4. **The #258 reasoning's home is already built, and the prose copies stay at their code points.**
   The rule's statement is the `draft-rows-optional` and `evidence-rows-optional` rows in
   `DECLARED_LIMITS`; its enforcement is the walk of ruling 2. The reasoning sentences at the group
   comment, the sentinel field comments and `format_report` are commentary on ADR 0053 ruling 6's
   terms — no pointed-at reasoning constant is created, because that is the shape ruling 6 already
   declined for the same module.
5. **#571 is relabeled `enhancement`**, aligned with #535 deliberately: both are a module holding a
   rule with no binding guard, and nothing is broken today.

## Why #253's refusal does not transfer within the module and does transfer across modules

[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) refused extracting the
`keyword_of` helper that `research_ledger.py` and `checks_ledger.py` had written the same way, on
the ground that a helper two modules happen to have written the same way is not one that exists to
be depended on, and a test pinning the agreement would forbid the divergence the copy exists to
permit. #571's *Done when* requires whichever option lands to say whether that transfers.

**It does not transfer within one module.** `research_ledger.py`'s gated sets follow one rule, the
copies are not entitled to diverge, and a walk forcing them into one kit forbids nothing
legitimate.

**It does transfer at the cross-module width, and that is why ruling 1 is scoped as it is.**
`differential_scan.py`'s `NOT RUN` strings are gated on whether a limb had a population, not on a
flag, and ADR 0063 ruling 7 refused a second limit object there while #550 is open;
`discussion_post_scan.py` and `discussion_reply_scan.py` gate on booleans carried by the `Scan`
itself. Each shape stands on its own measured grounds. A shared object, or a
`grader_conformance.py` assertion that every grader's gated set uses the `int | None` sentinel,
would fail `differential_scan` for a shape an ADR just ruled correct — forbidding divergence those
modules are entitled to, which is #253's refusal exactly.

## The walk has a finding on day one, and it is the guard working rather than a false alarm

`Scan.uptodate_citations` is `int | None`, and `format_report` keys both evidence lines off
`evidence_topics` alone — the third sentinel carries no not-graded limb of its own. Ruling 2's walk
forces it to either join `EVIDENCE_ROWS`' kit explicitly or be re-typed. Which of those is correct
is the builder's to derive from what the field means, not this record's to guess.

## What was overtaken between filing and grilling

The ticket's premise — *nothing binds them* — was true at `13ebd20` and half-false at `3ef2e74`:
#535 landed the two `DECLARED_LIMITS` rows and `HANDLERS` binds each to a blind-spot test and a
live positive control. What #535 did not absorb is the convention itself: nothing walks `Scan`'s
fields, and a third gated set that declares nothing arrives green. That half was verified rather
than assumed before it was ruled on, and it is the half ruling 2 closes down to ruling 3's ceiling.

The ticket's forecast that the third set arrives in `research_ledger.py` was also overtaken: ADR
0063 put it in `differential_scan.py`, in a shape a module-local object could never have reached —
which is what made ruling 1 a live decision rather than a default.
