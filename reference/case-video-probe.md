# Case video capture: historical build probe

Observed October 19, 2026 on Windows with Python 3.11.9 in a fresh, separate environment
installed from `tools/case-video-requirements.txt`. This is a historical synthetic probe, not a
claim about every consumer machine or a transcription accuracy benchmark.

The probe made a narrated video from Windows SAPI speech and three slide states: cough for three
days, then a temperature of 101 F, then pneumonia. The spoken teaching sentence also proposed
five milligrams. The images were white with black text, held for five seconds each and encoded
with H.264 video at ten frames per second and AAC audio. No course recording or patient material
was used or committed. The temporary media were discarded after the checks.

The public `case_video.py prepare` command first used a whole-image mean-difference threshold
of 0.015 and retained only the opening frame. This failed the known slide-build population.
The implemented detector instead counts pixels changing by more than sixteen grayscale levels
in a 160-by-90 image. With its threshold of 0.001, the same command decoded 150 frames and
retained all three known states at 0, 5 and 10 seconds. All retained images were opened and read.
These are tuning measurements on this sample, not a guarantee of distinct-slide completeness.

After the frame read, `case_video.py transcribe` ran `medium.en` and `small.en` locally with
the same slide vocabulary, CPU int8 and four threads. The retained capture manifest reported
10.766 seconds for the medium pass and 3.485 seconds for the small pass, including loading the
cached models. Both passes covered the synthetic narration. Their one disagreement was the
spelling `five` versus `5`, which the tool retained for confirmation. Neither agreement nor this
synthetic voice establishes clinical accuracy.

The same `prepare` and `transcribe` commands were then repeated with `--models large-v3 small.en`.
The three frame files matched the images already read byte for byte. The first large-model pass
took 95.188 seconds including its initial model download. A fresh capture with the now-cached
models took 16.937 seconds for `large-v3` and 3.390 seconds for `small.en`; the repository suite
was running concurrently. The large and small readings had no disagreement on this sample.
The largest supported size therefore ran within twice the synthetic video's duration once cached,
the build's practical starting criterion. The default is `large-v3` with `small.en`; a consumer
records its own size rationale and adjusts the pair when that machine cannot run it acceptably.
This does not measure long-lecture throughput or promise the same speed on another machine.

The consumer wrapper was also exercised without the separate interpreter and refused rather
than importing a heavy package or claiming a capture. The stdlib tests exercise changed media,
unread images, changed drafts, omitted disagreement records, missing clinician answers,
clinician-typed capture and document-only cases. The YouTube acquisition branch was not exercised
against a faculty video; a consumer download failure still takes the recorded WinX-file route
or the clinician's repair-or-type choice.

Dependency API references used for this build: [faster-whisper](https://github.com/SYSTRAN/faster-whisper),
[PyAV video API](https://pyav.basswood.io/docs/stable/api/video.html), and
[yt-dlp embedding](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp). The ordinary suite imports none
of the heavy packages. The command's complete coverage ceiling belongs to `case_video.DECLARED_LIMITS`.
