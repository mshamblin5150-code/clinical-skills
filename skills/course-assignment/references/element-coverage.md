# Element coverage read

[ADR 0441](../../../docs/adr/0441-a-course-assignment-reaches-gate-1-only-after-an-element-coverage-read.md)
governs this read for `course-assignment`, deck and DOCX alike. It is the first read of each
built artifact, before rendering, heading review, and voice review. Every later artifact change,
including layout repair, takes a new coverage read before the other reads repeat.

## Capture before drafting

Copy the live rubric verbatim to `<run>/rubric.json`: each criterion has its stable `id`,
`criterion`, full-credit `descriptor`, and decimal-string `points`. Capture the assignment's
point value independently as `assignment_points`. `points_exception` is empty unless the faculty
rubric legitimately does not sum to that value; then state the specific reason, such as an
unscored criterion. An exception never makes malformed or negative points valid.

```json
{
  "assignment_points": "10",
  "criteria": [
    {"id": "<rubric-row-id>", "criterion": "Comparison", "descriptor": "Explain the comparison.", "points": "10"}
  ],
  "points_exception": ""
}
```

When the live assignment has no rubric, use an empty `criteria` list and add the explicit line
`"no_rubric": "The assignment has no rubric."` in this object. Still capture its point value.
An unread rubric is an access failure, never a no-rubric declaration.

Before drafting, the drafting agent writes `<run>/elements.md`, one identified requirement per
line, from the assignment page, syllabus, linked faculty documents and rubric. Use this grammar:

```text
- <draft-element-id>: Explain the comparison.
```

Blank lines and a `# ` title are allowed. Identifiers begin with a letter and contain letters,
digits, hyphens or underscores. They are unique within their list.
Replace the angle-bracket identifiers in these schema examples with the run's own identifiers.

## Independent read, then reconciliation

This fresh **Second reader** applies [standing rule 6](../../../AGENTS.md). Give it the captured
assignment page, relevant syllabus, every retained linked faculty document, `rubric.json`, the
signed `bar.md`, and the built artifact. It first builds its own required-element list without
seeing `elements.md`, mapping each requirement to its answering place. Then give it `elements.md`;
it reconciles every drafting identifier to one or more of its own elements, adding elements it
missed. A second context is required: without one, write no completed record and give no go-ahead.
Keep the heading reader source-blind; this is a separate read.

The reader writes `<run>/element-coverage.json`. Use raw file SHA-256 values, not projected text
digests. `inputs_sha256` names every captured document the reader used, including the assignment
snapshot, syllabus where applicable, all faculty files, rubric, bar and drafting list. Paths are
relative to the run and remain inside it. At least one `assignment-<date>.md` snapshot and the
three fixed inputs `rubric.json`, `elements.md` and `bar.md` are required. The grader rehashes each
named input; it does not discover an omitted faculty document.

```json
{
  "artifact": "course-module-course-assignment-2026-10-28.docx",
  "artifact_sha256": "<raw SHA-256 of the built artifact>",
  "inputs_sha256": {
    "assignment-2026-10-28.md": "<raw SHA-256>",
    "rubric.json": "<raw SHA-256>",
    "elements.md": "<raw SHA-256>",
    "bar.md": "<raw SHA-256>"
  },
  "elements": [
    {
      "id": "<coverage-element-id>",
      "requirement": "Explain the comparison.",
      "origin": "rubric",
      "rubric_id": "<rubric-row-id>",
      "status": "answered",
      "location": "body paragraph 1",
      "bar_quote": "",
      "remark": ""
    }
  ],
  "reconciliation": [{"draft_id": "<draft-element-id>", "element_ids": ["<coverage-element-id>"]}]
}
```

`origin` is `prompt`, `faculty`, or `rubric`; only rubric elements carry a nonempty `rubric_id`.
Every rubric identifier must appear. Every drafting identifier is reconciled exactly once to
existing coverage element identifiers. The reader may map several requirements to one answering
place. Use slide bullets or speaker-note sentences for decks, and body paragraphs, captions or
figure notes for DOCX.

`status` is `answered`, `thin`, `missing`, or `omitted`. An answered or thin element needs its
specific answering `location`. Thin coverage also needs a substantive `remark`; it is shown as an
ordinary numbered reader remark and does not change the verdict. A missing answer refuses the
grade, including a rubric full-credit descriptor answered nowhere.

For `omitted`, leave `location` empty and put the exact whole signed-bar omission line in
`bar_quote`. The existing signing command must have retained the current bar and its signature;
matching text in an unsigned or subsequently changed bar is insufficient. The reader judges
whether that line permits this element's omission. Otherwise follow the existing changed-bar
showing and re-signing route; Gate 1 cannot approve over a known missing element.

## Before Gate 1

The existing `course_assignment_scan.py` dispatches the shared read through both branch graders,
including direct branch invocations and pre-approval grades without `--submission`. It refuses
missing or invalid records, stale artifact/input hashes, unreconciled identifiers, and unapproved
omissions. Pre-check approvals report `not graded` under the dated completion registry.

Prepare the paired grade and show its element coverage counts, every named omission and all
numbered thin-coverage remarks with proposed outcomes through the existing reader-remarks route.
The approval verifier checks those lines were shown. Keep the full element-to-location map in the
run and show it on request. A changed record or artifact takes a fresh paired grade and ask.

The complete mechanical boundary belongs to `element_coverage.DECLARED_LIMITS`.
