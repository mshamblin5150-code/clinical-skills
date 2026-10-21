# Word repagination before fixed-format export

Issue [#1586](https://github.com/mshamblin5150-code/clinical-skills/issues/1586)
reported intermittent numbered-list restarts in a case-study export. The shared
Word route now calls `Document.Repaginate()` after opening the document and before
choosing PDF or XPS. This also applies to assignment documents and discussion-post
documents, whose renderers use the same script.

The call stays inside each caller's existing owned-process timeout. Export
methods retain their typed late binding, and document cleanup and process
ownership are unchanged. Repaginate is not added to
`word_automation_scan.LATE_BOUND_WORD_METHODS`: the measurement below did not
observe it hanging dynamically. This follows ADR 0111's per-method rule.

## Historical measurement: October 21, 2026

Measured from base `8c43d7368189080850273d4e0b0b9b17e30a4de9` on the
maintainer's Windows machine. A private Python runner copied `word_export.ps1`
into three variants: unchanged control, ordinary `$opened.Repaginate()`, and
late-bound `InvokeMember("Repaginate", ..., [object[]]@())`. Apart from the
repagination call and an absolute path to the unchanged `office_process.ps1`,
each variant used the production script. Each ran through `powershell.exe
-NoProfile -ExecutionPolicy Bypass -File`, with piped handles and
`office_process.run_owned_process` enforcing the case-study caller's existing
20-second bound. Each arm used a freshly created, owned Word process.

Inputs were a synthetic document with a numbered list and the original Module 4
case-study document associated with the report. The original was opened read-only;
its raw file fingerprint was checked before and after all its arms. No source
document was rewritten. Each input was exported twice per binding and format.
The runner opened each PDF or XPS with PyMuPDF, counted pages, and compared SHA-256
digests of the complete extracted page text, including rendered list labels.
Private source text and exports are not published here.

All 24 invocations returned successfully within the bound. These are historical
whole-invocation elapsed times, including startup and cleanup, not isolated
repagination timings or a calibrated performance bound:

| Document | Repagination arm | Successful exports | Elapsed range (seconds) |
| --- | --- | --- | --- |
| Synthetic control | None | 4 of 4 | 5.018–19.878 |
| Synthetic control | Dynamic | 4 of 4 | 4.778–6.580 |
| Synthetic control | Late-bound | 4 of 4 | 4.988–6.545 |
| Original case study | None | 4 of 4 | 5.776–7.781 |
| Original case study | Dynamic | 4 of 4 | 6.384–14.618 |
| Original case study | Late-bound | 4 of 4 | 10.167–11.911 |

Every synthetic export contained 2 pages and every original-document export
contained 45 pages. Each document had exactly one extracted-text digest across
all its exports. No numbering difference was observed between the control and
either repagination arm. No Word process remained after the final arm.

## Interpretation

The comparison does not establish that missing repagination caused the historical
restart. The unchanged control did not reproduce it, so successful repaginated
exports cannot prove that repagination prevents it. The causal hypothesis remains
unresolved, rather than falsified. If a later export restarts numbering despite
repagination, investigation must continue beyond this hypothesis.

This change explicitly completes layout before both export routes. It does not
replace the existing visual inspection of retained rendered pages, or claim that
matching extracted text proves visual equivalence or future numbering correctness.
