# A faculty or classmate file is identified on the live page and matched by fingerprint before a run reads it

**Measured at:** e3ee68db1f3caf0dbbd2bfa5ee1b35b47035ba6e

[#1491](https://github.com/mshamblin5150-code/clinical-skills/issues/1491) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 10) on 2026-10-01. That review's
population included a `course-assignment` sitting in which the in-app browser failed and the run
searched the disk for the downloaded faculty document before opening the live assignment. The
clinician directed it to open the course link first. Grilled 2026-10-11; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Only one coursework skill says anything about links, and none says anything about files.**
`skills/course-assignment/SKILL.md` step 1 says to follow links and report access failures. The
first steps of `discussion-post`, `discussion-reply`, `peer-critique` and `practicum-case-study`
carry no such sentence, and none of the five says to identify a linked file on the live page before
looking for a local copy. `practicum-case-study` is the likeliest to meet one, because its faculty
material often arrives as an attached Word document.

**The clinician's browser asks where to save every download.** His main Chrome profile records
`download.prompt_for_download` as true. A download the run starts therefore opens a save dialog
only he can answer, and the run cannot learn where he put the file unless he says.

**A page script can read a linked file's bytes, through one route only.** Measured live on
2026-10-11 against a course assignment page in his signed-in Chrome. Fetching the page's own
`/download` link fails, because the course site redirects it to a separate storage host the page may
not read. Fetching the `url` field of the course site's own file record, with credentials, returns
the whole file: the byte count equalled the record's `size`, and the page computed the SHA-256 of
the bytes itself.

**Those bytes cannot be carried into the run directory reliably.** The browser tool truncates each
returned value near 1,000 characters and blocks encoded file data. Hex split across many fields gets
through, but the bytes would then pass through the model's own retyping, which is not byte-exact.

**A linked file can change after the run reads it.** On the measured assignment the file the run
had read on 2026-10-01, and whose local copy was byte-identical to it, was replaced on 2026-10-02 by
a revised document of a different size whose text shares a minority of its paragraphs with the
first. The assignment still linked one file; only the course site's file record showed which.

## Ruling 1 — one shared sheet governs all five coursework skills

The rule is written once, in `skills/_shared/reference/lms-attachments.md`, and the first step of
`course-assignment`, `discussion-post`, `discussion-reply`, `peer-critique` and
`practicum-case-study` points to it in one line. Keeping it in `course-assignment` alone was
declined because the failure is the same in every skill that reads a live page and then needs a
file. A second ticket for the other four was declined because it would write one rule twice on two
schedules. The sheet stands apart from `sourcing.md`, which is host-neutral, and from
`canvas-editor.md`, which governs the posting box rather than what a run reads.

## Ruling 2 — the page is read first, and the disk only after it

A run identifies every **Faculty file** and **Classmate file** the live page links, from the course
site's own record of each, before it looks for a local copy. It then searches the clinician's usual
save locations for a match. A local copy is a convenience and never the authority: a filename on
disk does not identify the file, and a filename that differs from the page's is noted once and is
never a stop. When nothing matches, the run asks the clinician once to save the file and say where.

## Ruling 3 — identity is a fingerprint the page computes, with size as the fallback

A local copy stands for a linked file only when its SHA-256 equals the digest the page computes from
the bytes the course site serves. When the page script cannot read the file, the record's byte size
is the fallback and the record says which test was used. A copy the clinician opened and re-saved in
Word does not match, correctly, since it is no longer the supplied bytes, and the run asks him for
the original.

Matching by size alone was declined because a fingerprint is strictly stronger and was measured to
work on the clinician's course site. Requiring name and size together, the ticket's own proposal,
was declined because a correct file with a drifted name would stop the run.

## Ruling 4 — the identity is recorded at the sitting and re-checked at completion

The assignment snapshot records, per linked file, the course site's file id, name, size, digest,
the local path read, and whether the run found it or the clinician supplied the location. A page
with no linked file records `ATTACHMENTS: none`, so an absent record cannot pass as a page with no
files. Each scoped skill's completion grader re-fingerprints the recorded local copies against that
record. A missing record or a mismatch is a finding.

The check compares against the sitting's record and never re-reads the live page, because the page
can change after the run. Its declared limits: it cannot see a linked file the run never recorded,
and it cannot show that the page was read before the disk search. A written instruction alone was
declined because both earlier safeguards against this slip were written instructions and neither
was applied.

## Ruling 5 — no browser download route

The run does not download a linked file through the browser. With the clinician's settings every
download needs his answer to a save dialog, and the page-script route can read the bytes but cannot
deliver them byte-exactly. The page script is used to compute the digest, not to carry the file.

## Ruling 6 — no re-check of the page before submitting

The run does not re-read the page's linked files at the go-ahead. The page is the instructor's to
get right before it opens, and a revision after that is not the clinician's to chase. The measured
revision on the Module 10 assignment received no ticket and no action, on the same ruling. A standing
watch of an assignment after submission was not adopted.

## Build checklist

- `skills/_shared/reference/lms-attachments.md`: the order, the fingerprint match and its size
  fallback, the record lines including `ATTACHMENTS: none`, the measured Canvas route (the file
  record's `url` with credentials, never the page's `/download` link), and the declared limits.
- The first step of each of the five coursework skills: a one-line pointer to the sheet.
- The first search location is derived per account rather than written as one clinician's folder.
- A shared completion row, enabled by `--submission` in each scoped completion grader, that
  re-fingerprints recorded local copies, with `DECLARED_LIMITS` holding the two limits above.
- Tests that drive a recorded match, a changed local copy, a missing record and `ATTACHMENTS: none`
  through the public command.
