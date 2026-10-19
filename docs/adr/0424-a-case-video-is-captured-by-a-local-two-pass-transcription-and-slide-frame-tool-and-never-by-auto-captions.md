# A case video is captured by a local two-pass transcription and slide-frame tool and never by auto-captions

**Measured at:** 981f63f73146f5e072f485a716a8f8c32804c7d1

[#1865](https://github.com/mshamblin5150-code/clinical-skills/issues/1865) was filed from the
grilling of [#1793](https://github.com/mshamblin5150-code/clinical-skills/issues/1793), where
[ADR 0400](0400-the-case-material-is-the-faculty-source-and-a-recorded-image-is-matched-before-drafting.md)
ruling 4 had a narration-only datum quoted from the course site's auto-caption and confirmed by the
clinician, because no committed tool transcribes audio. Grilled 2026-10-19 against `main` at the
commit above, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

The clinician's reason for building changed what the tool is for. It is not a per-datum check: he
wants the whole of what the instructor said, read beside the slides, so the run understands the case
and he no longer types the case out. He listens to the video while the capture runs, gives his live
differentials, then pulls his UpToDate dump.

## Measured before ruling

**Nothing in `tools/` transcribes audio or reads a video.** A search of the non-test modules for
speech, audio, Whisper and yt-dlp finds three hits, none of them audio handling: a screening topic
name in `corpus_census.py`, the podcast reference form in `reference_scan.py`, and a chat-export
content type in `voice_corpus.py`.

**ADR 0400 ruling 4 is not yet in any skill.** No file under `skills/` carries an auto-caption or
unconfirmed-narration rule; the one narration hit is `style.md`'s conflict rule. #1793, the build
that would write ruling 4 into `skills/_shared/reference/sourcing.md`, is open and labeled
`ready-for-agent`.

**The case videos are hosted on YouTube**, stated by the clinician in the grilling and consistent
with the 2026-10-12 `peer-critique` run, whose source was a `youtube.com` recording. The video
link is already a confirmation in his Sanity Check (`skills/_shared/reference/style.md`).

**A prior run already used the route ruled below, by hand.** That 2026-10-12 run, read from its own
transcript's tool calls and not re-run here, downloaded only the audio with yt-dlp into a throwaway
Python 3.11 environment, decoded it with PyAV, and transcribed it twice with faster-whisper's
`small.en` and `medium.en` models. Both models remain in the maintainer machine's Hugging Face
cache. The clinician recorded the lesson as a memory: never use the platform's auto-captions as the
record.

**The agent cannot hear audio.** The Messages API reference lists `text`, `image`, `document`,
`search_result` and tool content blocks and no audio block, and Claude Code's Read tool documents
text, images, PDFs and notebooks. Claude Code's voice dictation transcribes the user's microphone
and exposes nothing an agent can call. These are documented facts, not driven; whether another
agent harness takes audio was not checked. So a speech model must turn the audio into text before
any agent reads it.

**WinX YouTube Downloader is installed on the clinician's machine** at
`C:\Program Files (x86)\Digiarty\WinX YouTube Downloader`, a desktop application that ships its own
ffmpeg. Whether it has a command-line interface was not checked.

**YouTube's Terms of Service forbid downloading** except through a download control YouTube
provides or with YouTube's and the rights holder's permission. The case videos offer no such
control. The clause was stated to the clinician from the terms as known; the terms page was not
re-read for this record.

## Ruling 1 — build the capture

A committed tool captures a case presented by video: the whole narration, transcribed, and every
slide. Its output is the **Case video capture**. It replaces the case material the clinician used to
type, and it is used as the run's working reading of the whole case, not only for single data.

Not building it was declined. The clinician's confirmation closed the per-datum defect at about a
minute each, but the defect the clinician named is the typing and the missing context, which a
confirmation step does not reach.

## Ruling 2 — the course site's auto-caption is never the record

No auto-caption, from YouTube or the course site, is quoted, relied on for a datum, or used to fault anyone.
The capture replaces it wholesale. This supersedes ADR 0400 ruling 4.

## Ruling 3 — the capture is used as written, except one confirmation list

The **Case video capture** is working material under ADR 0400 ruling 1: checked against the video,
never the case. Within that, its transcript is quoted as written, labeled as machine transcription
that no human listened to. A datum a slide also shows is quoted from the slide. When the capture
finishes, the run shows the clinician one list, and he confirms or corrects each entry before it is
quoted or used to fault anyone:

- every drug name, dose or number that exists only in the narration and on no slide;
- every line where the two transcription passes of ruling 5 disagree.

He listens to the video during the capture, so the list is checked while the narration is fresh.

**Trusting the transcript outright was declined**: a misheard dose is written with full confidence
and nothing marks it, and a graded paper or a fault charged to a classmate is where it costs.
**Confirming every narration datum was declined** as spending his minute on ordinary speech that a
second pass and the slides already bound.

## Ruling 4 — slides are timestamped still images from the downloaded video

The tool downloads the video, pulls a still image wherever the picture changes, stamps each with its
time in the video on the transcript's own timeline, and keeps the images with the run. The run reads
each image. The tool reports how many images it pulled, so an unread slide is a visible count rather
than a silent skip; a slide that builds bullet by bullet yields near-duplicates the run reads too.

**Seeking through the video in the signed-in browser was declined**: slow, nothing is kept, and
nothing shows every slide was reached. The browser keeps its place in the Sanity Check, confirming
the link.

## Ruling 5 — two local Whisper passes with the slides' terms as a vocabulary hint

The narration is transcribed on the user's own machine by Whisper, twice, with two models of
different sizes: the largest that runs acceptably, and a second of another size. Both passes are
given the slides' own drug names and terms as a vocabulary hint, so the slide images are read before
the narration is transcribed. Agreement between the passes is never treated as proof, because they
share an engine and can mishear alike; disagreement is evidence that at least one is wrong, which is
why disagreeing lines join ruling 3's list.

**A cloud transcription service was declined**: each user would need an account and an API key the
agent may not enter, it bills per minute, it sends the instructor's recording to a third party, and
it fails when the service or key does. **Making the cloud an optional engine was declined** as two
routes to build and keep honest. A local command works with any agent that can run a command, which
is what the clinician asked for when he asked that the tool not depend on which AI the user has.
**One pass was declined** because a misheard ordinary line would have nothing pointing at it.

## Ruling 6 — required for the two skills that read a case video

The capture is a **Required command** for `practicum-case-study` and `peer-critique` whenever the
case material is a video. It runs in its own Python environment, so `discussion-post`,
`discussion-reply` and `course-assignment` gain no dependency and `peer-critique` gains none outside
that environment. It never falls back to an auto-caption.

**An optional command was declined**: a run that skipped it cannot be told from one that used it.
**Maintainer-only was declined**: every case-video run would depend on someone remembering to run it.

## Ruling 7 — the input is the YouTube link or a video file

The tool takes either the video's link or a local video file. Where its own download fails, the
clinician saves the video with WinX YouTube Downloader and hands the run the file, and the capture
proceeds identically. The run records which route supplied the video and the file's SHA-256, so the
transcript traces to exact bytes.

**The run driving WinX on his screen was declined**: slow, fragile, it takes his desktop while he is
listening, and an automated click through a third-party application is an action this repository
keeps in his hands.

## Ruling 8 — when the capture cannot run, the clinician chooses

When the tool cannot run, the run stops and says so. The clinician then chooses to fix it or to type
the case as before. A typed case's run records that the capture did not run and that the case came
from his own capture, so nothing reads as machine-transcribed when it was not; every quotation then
points at his typed capture, made by listening, and he is its human check.

**Waiting until the tool works was declined**: a tool fault would decide whether a submission can be
made.

## Ruling 9 — the download is accepted for the clinician's own study, and the media stay private

The clinician accepts the YouTube terms risk for his own study of a video his course assigned. The
audio, video, still images and transcripts live only in the run's private directory under
`scratch/`, are never committed, and nothing from them is published beyond the quotations a paper
needs. The public repository carries the tool and never the media.

**Asking the instructor first was declined** as a per-course delay for a use that is the same as
listening and typing. **Recording browser playback was declined** as harder, less reliable, and no
different on the terms question.

## Ruling 10 — a differential only the UpToDate dump carries is his, and is proposed

A differential that appears in the clinician's UpToDate dump and not in his live differentials is
his research, so it is never described as the run's or the faculty's. Choosing it out of the dump is
still the run's selection, so it goes on `practicum-case-study`'s proposed list with the dump topic
it came from, and he keeps or cuts it at the go-ahead he already gives. His live differentials are
his draft.

**Treating the dump's differentials as his draft was declined**: the dump covers far more conditions
than belong in one case, so the run would decide the differential with the clinician never seeing
the choice.

## Build checklist

- A capture command under `tools/`, required as ruling 6 states, named in `AGENTS.md` with a
  prerequisite paragraph for its separate environment. Its own command path calls `use_utf8()` and
  `require_python_floor()` and parses at the consumer floor; the heavy packages (yt-dlp, PyAV,
  faster-whisper) live only in the separate environment it launches. Two stages, because ruling 5
  needs the slide terms first: fetch and pull frames; then, given the run's slide-terms file,
  transcribe twice and write the disagreement lines. Outputs stay under the run directory. Counts by
  default; the transcript and the images are private working material. The measurements left to
  the build are which model sizes run acceptably, how sensitive frame-change detection is, and which
  Python version the separate environment needs.
- A `DECLARED_LIMITS` object for the command: agreement between passes is not proof; the frame count
  is a floor, not proof every slide was distinct; a fingerprint binds the file, not the video
  YouTube serves later; whether a confirmation-list entry is narration-only is the run's reading of
  the slide images.
- `skills/_shared/reference/sourcing.md`: the narration rule of rulings 2 and 3, in the place ADR
  0400 ruling 3 assigned, replacing the auto-caption sentence #1793's checklist would have written.
  The capture line ADR 0400 ruling 2 adds names whichever capture the run used and its route.
- `skills/practicum-case-study/SKILL.md` and `skills/peer-critique/SKILL.md`: the capture step for a
  video case, the confirmation-list stop, ruling 8's choice, and in the case study ruling 10's
  proposed-list attribution.
- A record of the confirmation list and the clinician's answers, read by those two skills'
  completion graders: a quoted narration-only datum or disagreeing line without a confirmation is a
  finding.
- `CONTEXT.md`: **Case video capture**, written with this record.

## Supersedes

- [ADR 0400](0400-the-case-material-is-the-faculty-source-and-a-recorded-image-is-matched-before-drafting.md)
  ruling 4, whole. The course site's auto-caption is never quoted or used; the narration comes from
  the Case video capture under rulings 2, 3 and 5 of this record, or from the clinician's typed
  capture under ruling 8. That a narration-only datum the work depends on is confirmed by the
  clinician before it is quoted or used to fault anyone still stands, narrowed to ruling 3's list.
- [ADR 0400](0400-the-case-material-is-the-faculty-source-and-a-recorded-image-is-matched-before-drafting.md)
  ruling 2, the words "A new optional header line names the clinician's transcription file". The
  line names whichever capture the run used, the Case video capture or the clinician's typed
  capture, and the route that produced it. The line's existence, its fingerprint, its working-material
  label, and the `CASE-MATERIAL` address form still stand.
