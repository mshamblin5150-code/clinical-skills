# A clinician upload completes through the posted reading and a status line ends every reply of an approved run

**Measured at:** ba6bc7f002945b34941370bbd343fb61f24f159d

*Re-declared 2026-09-26 from `7cf0dab` for the supersession marker at the end alone. Since that
commit `tools/assignment_submission.py` and `skills/course-assignment/SKILL.md` changed with
#1398's build, so the measured sentence that a clinician upload can never grade clean no longer
describes `main`; nothing was re-measured.*

[#1398](https://github.com/mshamblin5150-code/clinical-skills/issues/1398) was filed from the
after-action review of a course-assignment run, 2026-09-22: the clinician uploaded the reviewed deck
himself, said so, and the agent answered that the deck was submitted. It wrote no posted reading and
ran no after-action review until he asked whether it had done one. It had also removed the scratch
workspace holding the revision's review records before he uploaded. Grilled against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**The terminal rule was already written and already graded.** `skills/course-assignment/SKILL.md`
step 6 required the posted reading, the after-action review and the `--submission` completion grade
before completion, and [#1037](https://github.com/mshamblin5150-code/clinical-skills/issues/1037)
had given that grader its review row. Every instrument existed. What failed is that nothing ran
them: *submitted* was a sentence the agent typed.

**Since #1396 a clinician upload can never grade clean.** `assignment_submission.completion_gate`
passes only when the durable record carries `gate2_confirmed`, and only `confirm` writes it — a call
the agent makes after it drives the upload itself. The ticket asks that a manual upload resume at the
posted reading and reach a clean grade; at this commit those two cannot both hold.

**The revision's records were outside the run directory.** The run directory named by this run's key
holds its independent review, visual read and render passes from the first sitting, early September,
and no rendered-pages record at all. The 2026-09-22 revision's renders and review records were
written to a separate scratch workspace, which is what was cleaned. The completion grader reads the
run directory alone, so the early deletion removed evidence from a place the grader never looks.

## Ruling 1 — a clinician upload is its own recorded route after the same approval

The clinician uploads only after he has looked at the artifact and given his OK, and that OK is the
approval the durable record already holds. When he reports that he uploaded it, the agent records a
**clinician upload** in place of its own upload confirmation, downloads the posted file, and writes
the posted reading as step 6 already specifies: filename population, attachment count and SHA-256
against the approved artifact. The completion grader accepts either route. A clinician upload with no
recorded approval cannot grade clean.

**What the route gives up is timing.** `upload_is_allowed` refuses a wrong file before the submit
click; on a clinician upload that check never runs, and a wrong file is found only by the posted
reading, after a submission Canvas cannot withdraw. Leaving the clinician's upload outside the gate so
every such run ends not clean was refused: an always-expected red is one a reader learns to skip.
Asking him not to upload himself was refused as a rule nothing enforces.

## Ruling 2 — every reply of an approved run ends with a run status line, checked in both harnesses

Once a run's approval is recorded, every assistant reply in a session that touches that run ends with
exactly one line:

```
Run status: awaiting upload
Run status: awaiting posted reading
Run status: awaiting AAR
Run status: stopped - <reason>
Run status: complete
```

A check at the end of each reply, in Claude Code and in Codex on the grilling guard's precedent,
retracts a reply that lacks the line, one that says `complete` while the run's `--submission`
completion grade is not clean, and one whose `stopped` carries no reason. Waiting on the clinician
stays legal, because `awaiting upload` is an honest status, so the check does not fire while he
reviews the artifact.

Skill wording alone was refused: it is what failed. A report at the start of the next session was
refused because the clinician would still have been told *submitted* in the session where it was
false.

## Ruling 3 — a stopped run says so and stays open

`stopped - <reason>` is the status for every point where the skill hands the run back to the
clinician: a posted reading that diverges, a Composer refusal, or his decision not to submit this
version. It is accepted without a clean grade and requires a written reason. A stopped run stays
stopped on every later reply that touches it until it is completed or approved again; there is no
separate close. Mapping those moments onto the nearest waiting status was refused as a status line
that describes a wait that is not happening.

## Ruling 4 — review records live only in the run directory, and approval requires them there

A revision of a finished artifact writes its render passes and review records into the run directory
named by the run key, as new numbered passes and updated records. Per-context scratch workspaces hold
work in progress only. **Recording the clinician's approval is refused unless the pre-upload grade is
clean against the run directory**, so records left anywhere else stop the run before the artifact is
shown to him rather than after it is posted. Per-context paths may be removed once approval is
recorded.

Keeping every scratch workspace until the terminal grade passes was refused: it leaves the grader
reading the same run directory with the records still elsewhere, and adds days of clutter while the
clinician reviews.

## Ruling 5 — course-assignment now, with the open-run rule read from a per-skill table

The check covers `course-assignment`'s deck and DOCX branches, which already share the durable
submission-gate record. It reads what opens a run and which grader closes it from a table keyed by
skill, with one row. The other seven skills in `aar_scan.SCOPED_SKILLS` keep separate approval records
and were not observed failing; they are
[#1421](https://github.com/mshamblin5150-code/clinical-skills/issues/1421), so joining one is adding
a row rather than rebuilding the check.

## What this record does not settle

**Whether the status line is true beyond `complete`.** The check grades `complete` against the grader
and the presence of a reason on `stopped`. An agent writing `awaiting posted reading` after the
reading was written, or a thin reason, is read by the clinician and not by the check.

**A clinician upload the agent is never told about.** The route starts from his report. A run left at
`awaiting upload` after he submitted elsewhere stays open until a session touches it again.

---

**Superseded in part 2026-09-26 by
[ADR 0277](0277-the-run-status-check-covers-every-posting-skill-through-one-approval-record.md), and left as
written.** Ruling 2's status `awaiting upload` is `awaiting posting`, and its *exactly one line* is
exactly one line per touched run, each naming its run key. The glossary term **Clinician upload** is
**Clinician posting**. Every other ruling here stands.
