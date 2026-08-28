# A references label is a per-pipeline source spelling for one rendered outcome

The clinician bolds the literal `References` label on the board — stated 2026-08-23, *"i bold the literal section that says References"*. `skills/discussion-reply/SKILL.md:147` instructs the opposite: *"End with a plain `References` label, not a Markdown heading"*. [#495](https://github.com/mshamblin5150-code/clinical-skills/issues/495) is that contradiction, and it is a `bug` rather than a prose note because of what `tools/discussion_reply_scan.py` does with the bolded form: one real run graded twice, differing only in four asterisks, moved from 0 findings to **10**, and not one of the ten names the cause.

Grilled on 2026-08-26 against `d13f818`. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement came first and reversed the ticket's own scope

The ticket, and two tracker sweeps on it, treat the label as **one vocabulary spelled inconsistently across three artifacts**. [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438)'s sweep states the conclusion in as many words: *"The two discussion graders require mutually exclusive label forms, and neither accepts the house style."* Driven in process at `d13f818` the string facts hold:

| form | `discussion_reply_scan` | `discussion_post_scan` | `docx_write.REFERENCE_HEADING.match` |
| --- | --- | --- | --- |
| `References` | matches | no | matches |
| `**References**` | no | no | no |
| `## References` | no | matches | no |

**The conclusion drawn from that table is false, and it is false because the table stops at the string.** The two skills reach the LMS by different paths, and the label's *rendered* outcome is what the house style is about.

`skills/discussion-post/SKILL.md:240` renders the Markdown through `docx_write.py --bold-headings` and `:250` says why: *"The clinician pastes from Word because direct bold on each heading survives as inline bold in the LMS."* Rendering all three forms through that command and reading `word/document.xml`:

| post-path source | rendered |
| --- | --- |
| `## References` | **bold**, no named heading style |
| `**References**` | **bold**, no named heading style |
| `References` | **plain** |

So `## References` **is** how the post pipeline writes a bold label. It arrives on the board bolded. The post grader is not a second instance of this defect; it is correct, and #438's *"neither accepts the house style"* is a true string comparison and a wrong reading of the pipeline.

`skills/discussion-reply/SKILL.md:185` is the other path: *"type the reply into the LMS rather than pasting it."* **No renderer at all.** The reply artifact's spelling is what the typist reads and reproduces, so on that path plain `References` is the one form that reaches the board unbolded — and it is what the skill mandates. **The defect is one grader, not three.**

### A shared permissive rule would have introduced the defect on the other skill

The obvious repair — one pattern in `discussion_artifact.py` accepting all three forms, on `docx_write.REFERENCE_HEADING` → `reference_scan.py`'s import precedent — was recommended in round 1 of the grilling and withdrawn in round 2 on the rendering measurement. It would let a post ship with a **plain** label, unbolded on the board, with the grader reporting clean: the exact defect #495 exists to close, relocated.

### The post path has a third consumer the reply path does not

`skills/discussion-post/SKILL.md:216` runs `tools/reference_scan.py` on the Markdown and requires exit 0. That module imports the renderer's rule — `tools/reference_scan.py:236`, `from docx_write import REFERENCE_HEADING as RENDERER_HEADING` — and `.match`es it at `:735` and `:859`. Run against a one-entry document:

```
## References     -> exit 1   (list found and graded)
**References**    -> exit 2   no reference list found
References        -> exit 2   no reference list found
```

The layout follows the same line. `## References` centers the label and drops the body first-line indent from the entries; `**References**` leaves every entry carrying `w:firstLine="720"` — the reference list rendered as ordinary body paragraphs, with no APA hanging indent.

`skills/discussion-reply/SKILL.md` runs neither `reference_scan.py` nor `docx_write.py`. Its only commands are `research_ledger.py` on `claims.md` — without `--draft`, so `reference_scan.read_document` is never reached — and `discussion_reply_scan.py`. **Nothing on the reply path would refuse `**References**`.**

### The failure is worse than a missed row and the shape is already named

`discussion_artifact.split_references` (`tools/discussion_artifact.py:61`) returns `(text, ())` when the pattern does not match, so a refused label is indistinguishable from a document with no references. In `discussion_reply_scan.survey`, **every row except `addressed-name` reads `reply.body` or `reply.references`** — `word-floor`, `reference-minimum`, `unresolved-citation`, `untraced-number` and `respent-source`. A refused label does not degrade one row; it makes five of six uncomputable while they keep printing numbers.

That is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s partial instrument arriving on a report rather than on a matcher, and it is the reachable-by-one-colon shape: `References:` and `Reference` both reproduce it in full.

*(Corrected in place 2026-08-26, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. This sentence originally named `REFERENCES` as a third form. It is not one: the pattern carries `(?mi)`, so IGNORECASE is on and `REFERENCES` **matches** and is already accepted. The ruling is unaffected — the conclusion rests on the other two — but a builder writing ruling 2's recognizer tests would have driven `REFERENCES` expecting a refusal and got a match. Found by the tracker sweep the same day the record was ratified.)*

## Ruling 1 — a grader's accepted set is exactly the set that renders bold on its own pipeline

Not one vocabulary, and not one object. The **rule** is shared and written into both modules; the **pattern** is not.

- `discussion_reply_scan.REFERENCE_LABEL` accepts `**References**` and rejects plain `References` and `## References`. Nothing renders a reply, so the artifact's spelling is the board's spelling; `*References*` is italic and is rejected; trailing whitespace stays accepted, as today.
- `discussion_post_scan.REFERENCE_HEADING` is **unchanged**. `## References` is correct on two independent grounds — it is what renders bold, and it is the only form `reference_scan.py` can read.

**The only pattern that changes in this ruling is `tools/discussion_reply_scan.py:53`.**

This makes the ticket's option 1 — *accept both, leave two spellings live forever* — wrong rather than merely cheap: on a path with no renderer, blessing plain forever blesses the one form that arrives unbolded. It selects option 2, and re-prices the cost option 2 was declined over.

### Rejected: one shared pattern in `discussion_artifact.py`

Measured above. It relocates the defect onto `discussion-post` and breaks `reference_scan.py` on that path. `research_ledger.py` and `checks_ledger.py`'s precedent applies and cuts the other way from the intuition: *what transfers is the rule, and a shared helper would forbid the divergence two scanners with different populations are entitled to.*

### Rejected: widen the post grader to accept `**References**` as well

Both render bold, so the invariant appears to admit it. `reference_scan.py` exits 2 on it and the APA hanging indent is lost. The post path's accepted set is the intersection of *renders bold* and *`reference_scan` can read it*, and that intersection is `## References` alone.

## Ruling 2 — a label the grader refuses is a not-scanned condition, and its dependent rows report `not graded`

`discussion_artifact.py` gains a **recognizer**: a broad pattern matching any line that is plainly a `References` label in some spelling. It encodes no policy, so it is genuinely shared; the accepted sets stay per module, which is ruling 1.

- Recognizer matches, accepted pattern does not → the label exists and is refused. Exit **2**. The boundary-dependent rows print `not graded` rather than a number, stderr names the offending line.
- Neither matches → there is no label. Unchanged: `reference-minimum`, exit 1.

The two cases are separated **exactly**, with no heuristic about whether the document's tail looks reference-shaped. The recognizer is a declared superset of each accepted pattern and a test asserts the containment, so the pair cannot drift into a state where an accepted form is unrecognized.

`not graded` rather than `0` is `research_ledger.py`'s arrangement and its reason: *a zero beside a row that never ran is indistinguishable from a row that passed.* The house rule that **1 wins over 2** does not apply, because the findings that would have outranked the 2 are exactly the ones that could not be computed.

**This preserves `tools/test_discussion_reply_scan.py:144`'s asserted contract.** `test_a_reply_without_its_own_reference_list_fails` writes a reply with no label at all and asserts exit 1 with `reference-minimum`. That case has no recognizer match and is unaffected.

**It applies to both graders.** The post path is protected today only by `SKILL.md:216`'s step ordering putting `reference_scan.py` ahead of `discussion_post_scan.py`. That is a property of a neighboring line in a Markdown file, not of the grader, whose own docstring promises *"2 means it did not completely scan"*. `test_ls_files_coverage.py`'s position: a guarantee that holds because of who happens to call you is a floor, not a property.

## Ruling 3 — the skill-to-code bind drives the stated form through the pipeline

Nothing binds the prose to the pattern today. `grep -rn REFERENCE_LABEL tools/test_*.py` returns nothing, and each grader's tests use only the form that grader already accepts — so both suites stay green whichever way this is ruled.

The bind extracts the label form from each `SKILL.md`, builds a minimal document carrying it, and drives it through **that skill's own commands**:

- the reply form is accepted by `discussion_reply_scan`;
- the post form is accepted by `discussion_post_scan`, read by `reference_scan.py` at exit 0, and renders bold with no named heading style in the `.docx`.

Every measurement in this record becomes a test.

### Rejected: a string bind

Parsing the form out of each `SKILL.md` and asserting the grader's pattern matches it is cheaper and catches a prose edit. It is too weak on the post path, where **three** consumers depend on one stated form: a string bind to any one of them passes while the other two disagree, which is the state the tree is in right now. [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s lesson is exactly this — *an identity test passed while two implementations still disagreed*.

It also fails to defend the ruling. The reason the post grader stays `##`-only is a rendering fact and a `reference_scan` fact; only the pipeline bind goes red when either stops being true, and only it stops a later author "unifying" the two patterns and going green.

## Ruling 4 — `skills/discussion-post/SKILL.md` states its label form

That file states no label form anywhere. Its `##` requirement has never been written down, which is why two sweeps read it as a defect.

## Ruling 5 — the four pre-ruling run artifacts are left as written

Three reply artifacts and one post artifact, across the `nur5042-m2-discussion` and `nur5144-m1-discussion` run keys, all carry a plain `References` and all become non-compliant under ruling 1. None is committed and none is graded by the suite, so leaving them costs nothing operationally. **They are named by run key rather than by file here** — a reply artifact's filename carries the addressed classmate's first name, which `discussion_reply_scan.py`'s own docstring classes as *"private working material"* that must not be pasted, and this record is committed.

They were written to the instruction in force on 2026-08-23. A re-grade failing them is a true statement about them. This is the repo's standing position on records — `fixtures/` is excluded from the cited-step check precisely because a note cites the skill *as it stood when the run happened*, and the only available repair would be to falsify it.

### Rejected: correct them to the bolded form

It is editing evidence to satisfy a rule made after it, and it is worse here than usual: **nothing can corroborate the edit in either direction.** Every artifact in both run directories records a plain `References`, including the two captured boards *and the classmates' posts* — which is what gives it away. The board capture flattens formatting, so a bolded label comes back as plain text. Correcting the artifact would assert a fact rather than repair one.

## What none of this reaches

**The reply path's provenance record cannot state the label's formatting as posted.** The capture flattens it, so the artifact can record the intended form and nothing captured from the LMS can corroborate it. This is a limit on what a reply-path run record can ever assert, it is true independently of how #495 is ruled, and it is filed separately rather than folded in.

**A run that types something other than the artifact.** The reply is typed by hand; nothing checks that what reached the board is what the artifact says.

**Whether a bolded label is what the rubric rewards.** The house style is the clinician's stated preference and is taken as given here.

*(Corrected in place 2026-08-28, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. The link in the 2026-08-26 correction named an ADR 0016 filename absent from the index; its target now uses the record's tracked filename. No ruling changed.)*
