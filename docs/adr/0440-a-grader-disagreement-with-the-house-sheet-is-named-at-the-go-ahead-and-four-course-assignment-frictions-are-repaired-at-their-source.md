# A grader disagreement with the house sheet is named at the go-ahead and four course-assignment frictions are repaired at their source

**Measured at:** 98ab2476570e1024ae1de28deb9842070199c64d

[#2038](https://github.com/mshamblin5150-code/clinical-skills/issues/2038) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M6), 2026-10-23. It listed four friction
points whose causes rested only on the orchestrator's own account. Grilled 2026-10-23 and
2026-10-24. Before any ruling, the sitting's main transcript was reread item by item, and each cause
below was re-derived from the transcript and the code. The clinician ruled every point below, against
`main` at the commit above, where the freshness gate read `FRESH`. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**Item 1: the grader was wrong, and the draft was right.** The draft cited two agencies in one
citation. Its first citation gave each full name with its abbreviation in brackets, and later
citations used the abbreviations alone, which is `skills/_shared/reference/apa7.md`'s group-author
rule. The reference list gave the full names throughout. `assignment_docx_scan.py` reported 5
reference defects and 4 untraced citations. Only the agency that ended the citation passed.

A driver reproduced the exact finding set, and it isolated two separate gaps:
- `discussion_artifact.GROUP_DEFINITION` reads a bracketed abbreviation only when a comma and year
  follow it, so a bracketed abbreviation followed by `& <second agency>` is never read as a
  definition.
- A joint citation in abbreviations (`CMS & NCHS, 2026`) is looked up as one phrase. In
  `reference_scan.citation_phrase_key` and `_citation_findings`, and in
  `discussion_artifact.citation_occurrence_keys`, abbreviations expand only for a single-author
  citation. That form is still refused when each abbreviation was introduced on its own earlier.

The single-agency form passes, so the driver's control is live. The orchestrator spelled both
names out, which is also correct APA, and recorded no disagreement. Neither `reference_scan`'s
limits nor `apa7.md`'s limits table names the gap.

**Item 2: the image record pins a hand-typed time to the microsecond.** For a `proposed-and-approved`
image, `imagery_proposals` calls `approval_record.verify_clinician_reply` with a lower bound just
below the record's hand-entered `reply_at`. It then refuses unless the matched message's timestamp
equals `reply_at` within 0.000001 s. Transcript timestamps carry milliseconds, so the typed value
has to be exact. In M6 the record was refused three times:
- a rounded minute;
- the right second;
- the timestamp of the queue row 25 ms before the clinician's message.

Each refusal printed the same sentence, which does not say whether the reply was missing or was
found at another time. The value was then read by a throwaway script calling the grader's own
lookup. Every other record carrying the clinician's word stores the matched time itself, from his
reply alone: `bar_signatures`, `assignment_bar`, `approval_record.approve` and
`assignment_submission`. `imagery_proposals` has no writer command.

**Item 3: the orchestrator invited a paraphrase of the tool-printed wording.** At Gate 1 the reader
remarks surface printed `reader_remarks.leave_request`'s exact forms. Below them, the orchestrator
wrote its own line inviting a reply "something like" one of them. The clinician replied
"Approved leave. Them all". That reply passed the whole-message check and failed
`reader_remarks._left_numbers`, whose pattern needs `leave`, `keep` or `accept` followed directly
by whitespace and its object. The refusal named the 56 unanswered remark numbers but not the
accepted forms, and he resent the exact phrase. The same matcher serves every coursework go-ahead
and the clinical approvals. A range such as `leave 1-56` reads as remark 1 only.

**Item 4: one hook refuses five conditions with one message.** The sitting had 29 hook refusals:

| Hook | Refusals |
|---|---|
| scanner pipe | 13 |
| staging | 7 |
| doubled backslash | 5 |
| heredoc | 3 |
| publish | 1 |

Every refusal from the other hooks was corrected on the next call. `subagent_staging_hook.refuse`
returns one fixed message for five conditions:
- a recognized temp or scratchpad location, including inside a prohibition;
- a relative staging path with no absolute cwd;
- a staging token that is not an existing folder, such as a file inside the staging folder;
- a run brief with no staging folder;
- an unreadable checkout list.

The retries were targeted. Twice, though, the orchestrator found the cause only by reading the
hook's source. All 11 staging refusals counted, the sitting's and this grilling session's own, were
fixable from the condition alone, without any brief text.

## Ruling 1 — the citation reader reads abbreviated agencies inside a joint citation

The shared citation reader treats a bracketed abbreviation as a group-author definition wherever it
sits in a citation naming several groups. A joint citation written in abbreviations resolves each
abbreviation to its own reference entry, whether the abbreviations were introduced jointly or one
at a time. Tests are driven by the M6 forms and by the separately introduced variant. The
single-agency form and the existing refusals of genuinely unlisted citations stay green as the
controls.

Declaring the gap and steering drafts toward spelled-out names was declined. A grader that cannot
see something may say so; this one refuses the sheet's own blessed form, and declaring that would
teach every run to rewrite correct work. Banning the abbreviated joint form until the repair lands
was declined as a skill rule that would only have to be removed again.

## Ruling 2 — a grader disagreement is named at the go-ahead

When a grader refuses a form a shared reference sheet blesses, the run may change the draft only to
another form the sheet also blesses. It names the **Grader disagreement** at the go-ahead, with the
sheet section and the grader's finding. This is one standing sentence in [AGENTS.md](../../AGENTS.md),
and every skill inherits it.

Halting for the clinician's choice was declined: the answer is nearly always to rewrite to the other
blessed form, and the sitting would stall on a defect he cannot fix there. Leaving it to the
after-action review was declined as the status quo that made the M6 cause unverifiable.

## Ruling 3 — the image reply time is written by a command from the transcript

A recording command, modeled on `bar_signatures.sign`, takes the clinician's whole reply and the
shown-draft time. It finds the reply through `approval_record.verify_clinician_reply`, stores the
matched time itself, and refuses with a reason that distinguishes no matching message from an
unreadable transcript. This refines who writes the time recorded under
[ADR 0394](0394-a-proposed-image-is-ruled-at-its-own-stop-before-any-grade-render-or-reader-and-the-ruling-is-the-clinician-s-verified-reply.md)
ruling 6, and leaves that ruling's verification standing. Records approved before the command's
start keep today's exact-time grading through the completion-check start table.

Grading from the reply alone with no stored time was declined: the record would still have no
writer, and the agent would still hand-build it. Keeping the hand-typed time with a refusal that
prints the found value was declined: it keeps the step that failed three times.

## Ruling 4 — Gate 1's leave wording is fixed on both sides

- The go-ahead ask repeats the tool-printed leave forms word for word. The skill text forbids
  inviting approximate wording.
- A leave refusal prints the accepted forms beside the unanswered numbers.
- `_left_numbers` tolerates punctuation between the leave verb and an explicit `all` or number
  object, and reads a numeric range as every number in it.
- The explicit-object requirement of
  [ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md) ruling 3
  stands unchanged, and so does the guard that a negation voids every leave. The M6 reply named
  "them all", which already met that ruling's bar.

Tests are driven by the refused M6 reply and by the range form. Fixing only the ask was declined
because a clear reply with a stray period would still fail. Widening only the matcher was declined
because it leaves the invitation to paraphrase in place.

## Ruling 5 — the staging hook names the failing condition and never the text

The staging hook's refusal names which of its conditions failed. Where a staging token failed, it
also gives the token's ordinal among the brief's staging tokens and its shape, such as a last part
that looks like a file. Where a temp pattern matched, it names the pattern by its fixed vocabulary
name. It never repeats brief or path text, and the existing test that brief text never appears in
a response stands. Each condition gets a test driven by its refused shape.

Echoing a failing path under `scratch/sessions/` was declined: an agent names that folder and could
build the name from run material, which reopens the patient-name exposure
[ADR 0375](0375-a-subagent-launch-hook-refuses-a-patient-work-brief-that-names-temp-or-no-existing-staging-folder.md)
avoids. Leaving the message unchanged was declined because it cost a read of the hook's source
twice in one sitting.

## Found while grilling

`run_status_stop_hook.RUN_PATH` lets its optional drive-letter prefix run across spaces. A brief
reading `Repo checkout: C:/... Run directory: C:/.../scratch/runs/<run>` is therefore read as one
path spanning the prose between the two. The token also keeps a trailing sentence period, which the
staging hook strips. In this grilling session that produced five touched "runs" that Windows
refuses to open, under two keys, so no set of status lines could satisfy the hook, and every reply
was refused once before its retry warned. It is filed as
[#2042](https://github.com/mshamblin5150-code/clinical-skills/issues/2042); nothing here rules its
fix.

## Done when

- The M6 joint-citation forms grade clean through `reference_scan` and the assignment trace, and the
  single-agency and unlisted-citation controls still behave as before.
- `AGENTS.md` carries ruling 2's sentence, and the glossary defines **Grader disagreement**.
- A recording command writes an approved image's reply time from the transcript, and a pre-start
  record still grades under the exact-time rule.
- The refused M6 Gate 1 reply and a range reply each answer every leave, a negated reply still
  answers none, the ask text forbids paraphrase, and a leave refusal prints the accepted forms.
- Each staging-hook condition refuses with its own named condition, and no response contains brief
  text.
