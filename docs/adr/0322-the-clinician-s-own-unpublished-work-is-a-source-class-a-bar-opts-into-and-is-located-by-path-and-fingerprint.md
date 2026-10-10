# The clinician's own unpublished work is a source class a bar opts into and is located by path and fingerprint

**Measured at:** fa8143ee654a2d480ac69eacd9a59c6dfce1afb6

[#1489](https://github.com/mshamblin5150-code/clinical-skills/issues/1489) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 10) on 2026-10-01. The clinician
asked that run to cite a policy he wrote, an unpublished document kept in his OneDrive, and
`research_ledger.py` could not represent it honestly. Grilled 2026-10-10 against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**The source-class vocabulary has no member for the clinician's own work.**
`research_ledger.SOURCE_CLASS_VOCABULARY` holds `society guideline`, `peer-reviewed`, `government`,
`tertiary reference` and `market source`. The Module 10 run filed the policy under `society
guideline` and wrote a note calling that a misfit; an earlier run filed the clinician's unpublished
capstone under `peer-reviewed`. Each was a false statement in the working record.

**The locator accepts only a URL or a DOI.** `research_ledger.LOCATOR` matches `http(s)://` or a
bare `10.` DOI, so a retained local path fails `unresolvable-locator`. The run recorded a OneDrive
web search address that returns the file in the clinician's signed-in account. That address proves
neither which file was read nor which version.

**A misreading of the clinician's own document has already happened.** The same Module 10 run said
the clinician drafted Welch Community Hospital's emergency response policy, taken from the
document's first line after reading only keyword-matching lines. He wrote it for the Rural Health
Clinic, which the hospital owns but which is a separate entity. That error is the evidence that a
reading of his own work needs the same independent check as any other source.

**Each bar already selects its permitted classes.** `SOURCE-CLASSES` in a run's `bar.md` is parsed
by `research_ledger.py`; `market source` is admitted only where a course-assignment deck bar signs
it (ADR 0110). The `discussion-post` and `practicum-case-study` bar templates list the other four.
With no bar, `research_ledger.py` defaults to `SOURCE_CLASS_VOCABULARY[:-1]`, a positional slice
that drops whichever member is last.

**A fingerprinted local read has a precedent.** `tools/project_context.py` hashes the bytes of each
retrieved file with SHA-256, re-hashes at completion, and treats a moved item as incomplete
coverage rather than a finding (ADR 0272).

**The APA sheet has no unpublished-manuscript form.** `skills/_shared/reference/apa7.md` carries a
published DNP project form (section 27) and no section for an unpublished manuscript.
`reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE` maps each class to whether its entries take a
retrieval date and has no row for a new class.

## Ruling 1 — the clinician's own unpublished work gets a ledger record

A claim drawn from the clinician's own unpublished work is a sourced ledger record graded like
every other: a restatement, a passage, a recency disposition, a locator, a page year and an
independent refutation. The refuter opens the same document and tries to show the claim wrong.

Citing such work with no ledger record was declined because nothing would then check that the
draft read the document correctly, and the one recorded misreading is exactly that. Keeping the
existing classes and admitting only a local locator was declined because runs would go on filing
the work under a class it is not, which is the defect #1489 was filed over.

## Ruling 2 — `clinician's own work` is a class a bar opts into

`research_ledger.SOURCE_CLASS_VOCABULARY` gains the member `clinician's own work`. No bar template
lists it by default. A run admits it only when the clinician allows it for that assignment: at bar
signing, or when he asks for the citation partway through a run, in which case the bar is signed
again and his request is that signing's go-ahead. A record of that class under a bar that does not
sign it fails as an unknown source class, and the run stops to ask.

Admitting it by default on every coursework bar was declined because a run could then substitute
the clinician's own work where a grader expects published evidence, without anyone deciding the
assignment allows it. Admitting it everywhere except the case study was declined as a second rule
to keep in step with the list of coursework skills.

The build replaces the positional `SOURCE_CLASS_VOCABULARY[:-1]` default with a named set, because
appending the new member would otherwise silently admit `market source` to a run with no bar.

## Ruling 3 — the locator is the absolute path and a fingerprint of the bytes read

For a `clinician's own work` record, `RESOLVED` carries the document's absolute path, the lowercase
SHA-256 of the exact bytes read, and the read date. At completion the grader hashes the file again.
A file that is absent, or whose bytes no longer match, leaves the record not completely checked:
exit 2 with the shared unread remainder, never a finding, and a finding on the same run still wins.
The refuter opens the same path and reports the digest it read, and `SECOND-ROUTE` records that the
two digests agree. Every other class keeps the URL-or-DOI locator unchanged.

A OneDrive share link was declined because creating one grants access to anyone holding it, which
is a publishing act, and it does not identify the version read. A path alone was declined because
nothing would then show which version the claim was checked against.

## Ruling 4 — recency applies unchanged

A `clinician's own work` record takes the same recency dispositions and window as any other class.
A work older than the bar's window needs `nothing newer` or `guideline in force` with a reason, for
example that no later version of the clinic policy exists.

Exempting the class from recency was declined because it would create the one source that can go
stale unflagged, and the one a run is least likely to question because the clinician asked for it.

## Ruling 5 — the reference entry follows APA, and the year has a fixed order of sources

`skills/_shared/reference/apa7.md` gains an unpublished-manuscript reference form, verified
against APA's primary source rather than written from recall. The clinician's standing form for
his policy set already follows it: `Shamblin, J. (2025). *Title* (Rural Health Clinic Policy No.
0NN) [Unpublished manuscript]. Rural Health Clinic, Welch Community Hospital.`
`reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE` gains a row for the class, set from what that
verified APA form says about retrieval dates.

The entry's year, and the record's `PAGE-YEAR`, come from the first of these that exists:

- a year the document states about itself, in a header, date line or similar;
- the last-modified date in the document's own internal metadata, such as Word's core document
  properties or a PDF's modification date, which changes only when the document is saved;
- the clinician's answer when asked, recorded as his.

`PAGE-YEAR` names which of the three supplied the year. The file system's modified date is never
used, because OneDrive sync and opening the file can change it without any save.

`n.d.` was declined as the default for an undated document because it discards a year that is
known and forces a recency excuse on every citation.

## Build checklist

- `tools/research_ledger.py`: the new vocabulary member, the named no-bar default, the local
  locator branch with re-hash at grading, and the `PAGE-YEAR` source vocabulary for the class.
- `tools/reference_scan.py`: the retrieval-date row for the class, after the APA form is verified.
- `skills/_shared/reference/apa7.md`: the unpublished-manuscript form, with its primary source.
- `skills/_shared/reference/sourcing.md`: the refuter's same-path digest check and `SECOND-ROUTE`
  wording for the class.
- The bar sections of `discussion-post`, `discussion-reply`, `peer-critique`, `course-assignment`
  and `practicum-case-study`: how the class is admitted at signing or by a mid-run re-signing.
- Tests that drive a planted local document through the ledger's public command, including a moved
  file, a changed file and a record under a bar that does not sign the class.
