# A course figure is run supplied and title page credentials are an account setting

**Measured at:** 6d33ca2a2687d7c5b07a0dffff0b63717c0a8a6e

[#1498](https://github.com/mshamblin5150-code/clinical-skills/issues/1498) and
[#1492](https://github.com/mshamblin5150-code/clinical-skills/issues/1492) record the same
`tools/assignment_docx.py` defects, filed 49 minutes apart by two after-action reviews of the
NUR 5042 Module 10 sitting. Grilled 2026-10-11 against `main`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. #1498 carries the rulings and the
build, and #1492 closes as its duplicate. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The figure is blank at the source.** `_relationship_png` fills pixel rows with the standard
library and writes the PNG bytes itself: three outlined rectangles and two arrows, with no text,
because nothing in the standard library draws a glyph. The caption beneath it names three nodes
that appear nowhere in the image. The NUR 5042 Module 9 submission shipped the same image, and its
visual read did not report it.

**The caption is one line.** `_body` writes `"Figure 1 " + " to ".join(spec.relationship_labels)`
in the `Caption` style, which `_styles` sets italic, 10 pt and colored `30343B`. APA 7 puts a bold
figure number on its own line and an italic title-case title on the next.

**The title page departs from APA in three places.** `_styles` sets `Title` bold at 16 pt and
`Subtitle`, the author line's style, colored `30343B`. The title sits at the top margin. The text
does not repeat the paper title, and the NUR 5042 Module 11 run inserted a heading-only first
section to work around it.

**The credential line was a departure nobody ruled.** `skills/course-assignment/references/docx.md`
says the title page supports "a long credential line as one fitted line", and
`skills/_shared/reference/apa7.md` says to "preserve authors' chosen names without credentials".
Neither file says which governs. The Module 11 run accepted the line, the gray author line, the
16 pt title and the top-margin placement without a ruling.

**The clinician's credential strings also sit in shared files.** `practicum-case-study`'s
*Credentials* table and three passages of `_shared/reference/style.md` carry his signature and
prescribing-role strings, so a second clinician would sign them. That is
[#1682](https://github.com/mshamblin5150-code/clinical-skills/issues/1682)'s subject and is
ruled there, not here.

**A rendered-page test cannot run in the suite.** Only Word draws a `.docx` the way a grader sees
it; CI runners carry no Office, and PyMuPDF's free edition does not open Word files.
[ADR 0008](0008-word-is-a-one-time-calibration-instrument.md) settled the same constraint for
the case-study renderer.

## Ruling 1. The producer embeds a run-supplied figure image and draws none

`_relationship_png` is removed. A spec that carries a figure supplies an image file, a figure
title, and alt text together, or none of the three; one without the others is refused. The
producer embeds the image at its own proportions within the text width. The three-label field and
the generated sentence beginning "The figure connects" are removed, and the run's own prose calls
the figure out.

The caption follows APA 7: a bold `Figure 1` on its own line, then the italic title-case title on
the next, at text size and in black, above the image.

## Ruling 2. The image method is open and every label is proofread

The `course-assignment` skill leaves the method of making the image to the run: image generation,
a script, an export from another application, or a drawing the clinician supplies. The run records
which method it used. Whatever the method, the visual reader confirms that every label in the image
matches the caption and the text exactly. An image made by a generative tool carries the credit APA
requires in the figure note, worded from APA's published guidance at build time rather than from
memory.

## Ruling 3. Whether a title page carries credentials is an account setting

The account profile that `setup-clinical-skills` writes records whether title pages carry a
credential line and what it says. The setting governs Word title pages and slide title slides. It
does not govern `practicum-case-study`'s `Signed by:` and `Rx:` strings, which are clinical role
signatures and are #1682's.

`setup-clinical-skills` asks the question at install. When a run reaches a title page and the
profile is silent, the run stops once, asks, and writes the answer into the profile; it does not
default. `apa7.md` and `docx.md` describe the setting beside the APA rule, so a reader that reports
the line is answered by the profile rather than by an unruled acceptance. The clinician's profile
records a credential line.

## Ruling 4. The rest of the title page follows APA 7

The title is bold, title case, at text size. The author line is black. The title block sits three
to four lines below the top margin, a distance the build confirms against the *Publication Manual*
before writing it into `apa7.md` or the producer. The paper title is repeated at the start of the
text.

## Ruling 5. Word calibrates the new shapes once, and the suite guards them

The build follows ADR 0008: a maintainer-only probe renders the new title page, caption and embedded
figure through installed Word once, commits what Word reports with the date and Word version, and
the suite fails when the producer's shapes leave the measured set. The per-submission visual read
remains the second net.

## Rejected options

**A built-in table drawn as a three-node diagram.** It needed no dependency and rendered alike in
every viewer, and it was the recommendation. The clinician chose a run-supplied image, which does
not confine a figure to a straight chain.

**Native Word drawing shapes.** The most complex XML in the producer, and Canvas's document preview
draws shapes unreliably.

**A PyMuPDF-drawn image.** It puts a non-standard-library dependency on producing the document,
and its labels remain unselectable pixels.

**Removing the figure feature.** An assignment whose rubric asks for a figure would have no route.

**Image generation as the only method.** A session without an image service would have no figure.
**Forbidding generated images.** It rules out the method that prompted the decision.

**Credentials as a house rule in shared files.** The choice is one clinician's, and a second
clinician inheriting the skills would carry it. **Asking every assignment.** It adds a question to
every run and leaves papers inconsistent. **APA by default for a silent profile.** A clinician who
wanted the line would lose it silently until rerunning setup.

**Moving the signature strings under #1498.** It would tie a small producer fix to a change across
three skills; #1682 carries those rulings instead.

**A Word render inside the suite.** It fails on every machine without Office, CI included, which
ADR 0008 already refused.

## Consequences

**A figure's labels are read by eye on every run that carries one**, whatever made the image.

**A clinician's title page reflects that clinician's choice**, and a visual reader's report of the
credential line has a recorded answer.

## What this does not reach

**Whether a figure is the right figure.** The proofreading rule checks that labels match the
caption and text, not that the diagram represents the argument correctly.

**What Word draws after the calibration date.** Ruling 5 binds the producer's shapes to a dated
measurement; a later Word release changing its drawing of the same shapes is outside it.
