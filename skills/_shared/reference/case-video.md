# Case video capture

For a video case in `practicum-case-study` or `peer-critique`, run
`python tools/case_video.py` before drafting. The capture is private working material;
the faculty video remains the **Case material**. Follow the narration rules in
[Sourcing](sourcing.md#case-video-narration). The command's complete ceiling belongs to
`case_video.DECLARED_LIMITS`.

## Prepare, read, transcribe

Use an existing run under `scratch/`. Keep all video, audio, still images, logs and text there.
Confirm the video link in the Sanity Check. Set up a separate environment once, using a Python
version supported by the pinned packages, then pass its interpreter explicitly. Python 3.11 was
used for the [historical build probe](../../../reference/case-video-probe.md). For example on
Windows, with that Python installed:

```powershell
py -3.11 -m venv <scratch>/sessions/<environment-key>/env
<scratch>/sessions/<environment-key>/env/Scripts/python.exe -m pip install -r tools/case-video-requirements.txt
python tools/case_video.py prepare <run> --python <environment-python> --source <youtube-link>
```

The wrapper remains at the consumer Python floor. It launches the heavy imports only in the
separate interpreter. It downloads the video itself, including audio, without subtitles. If that
download fails, tell the clinician; he can supply a file saved with WinX YouTube Downloader:

```powershell
python tools/case_video.py prepare <run> --python <environment-python> --source <video-file> --route winx --capture case-video/winx-capture
```

Use a new capture directory for each attempt. `capture.json` records the acquisition route,
source, video SHA-256, every retained frame's timestamp and fingerprint, and the decoded frame
count. Read every image under `frames/`, including near-duplicates from slide builds. Show the
retained count and the unread remainder; transcription waits for zero unread images. If a
transition obscures a slide or a visible build was missed, lower `--threshold` and prepare a new
capture. A talking-head or animated video may produce many images; read them rather than silently
reducing the population.

Write `<run>/slide-terms.json` after that read:

```json
{
  "frames_read": ["frames/frame-000001.png", "frames/frame-000002.png"],
  "terms": "Drug names and clinical terms read from the slides, or an explicit statement that none appear",
  "model_reason": "Why the primary model is the largest that runs acceptably on this machine, and why the other size was chosen"
}
```

The example frame list is replaced by the entire retained population, exactly once each.
Run both local passes with the same slide vocabulary:

```powershell
python tools/case_video.py transcribe <run> --python <environment-python> --terms <run>/slide-terms.json --models large-v3 small.en
```

Use `--capture` again if preparation used a nondefault directory. Select the largest model that
runs acceptably on this machine and a second model of another size; `--models` lists the supported
choices. The CPU route uses int8 and bounded threads; adjust `--threads` if necessary. The defaults
are a starting pair, not evidence of an optimal size on a consumer's machine. Keep each pass's
elapsed time in `capture.json` and revisit the choice if a larger model runs acceptably.

Read the whole `transcript.md`, both `pass-*.json` files, and `disagreements.json`. The transcript
retains the primary pass's words with timestamps and a machine-transcription label. Token alignment
compares the full passes independently of their segment boundaries, including speech appearing
only in the second pass. Every differing span has a `D` identifier and the two readings. Quote
data that also appear on a slide from that slide.

## One confirmation list, then a bound review

Compare the complete narration with the images. Add every narration-only drug name, dose and
number to the disagreement population, giving each added item a unique `N` identifier, exact
primary-pass quotation and timestamp. Show the clinician this one combined list. He listens to
the video during capture; retain his confirmation or correction for every entry. Wait for his
answers before quoting an entry or using it to fault anyone, and before the go-ahead.

Write `<run>/case-video/<submission-key>.json`, using the exact key the completion grader takes
(for example `critique.md` for peer critique). This is the record shape for a machine capture:

```json
{
  "kind": "machine",
  "capture": "case-video/capture",
  "manifest_sha256": "SHA-256 of capture.json after both passes",
  "draft_sha256": "SHA-256 of the final draft's raw bytes",
  "frames_read": ["frames/frame-000001.png", "frames/frame-000002.png"],
  "narration_review": "What was compared across the whole narration and every slide for drug names, doses and numbers",
  "narration_only": [{"id": "N<entry>", "kind": "dose", "quote": "exact primary-pass words", "seconds": 12.5}],
  "answers": {"D<entry>": "Clinician's full confirmation or correction", "N<entry>": "Clinician's full confirmation or correction"},
  "uses": [{"id": "N<entry>", "location": "Draft heading and sentence quoting or faulting this datum"}]
}
```

Replace example populations with the actual populations. Empty `narration_only`, `answers` and
`uses` are explicit empty collections when nothing belongs there. Every disagreement and added
narration-only entry needs an answer, including an entry dropped from the paper. Record every
quotation or fault location; carry a clinician's correction into the paper and preserve the
machine text unchanged. Compute fingerprints with `python tools/file_digest.py <file>`.
After any draft change, reread its use of the confirmed data and update the draft fingerprint.

```powershell
python tools/case_video.py check <run> --submission <key> --draft <final-draft>
```

A clean exit is required before handoff and by both skills' submission graders. The check reads
the retained video, frames, terms, passes and disagreement list again; changed or missing files,
incomplete recorded frame reads, or an unanswered entry are findings. Output contains counts and
status only. Open the private files to repair a finding; never paste their text into a public log.

## Capture cannot run

Stop and show the failure. The clinician chooses repair or typing the case from listening. Record
his whole answer. For the typed route, retain his file under the run and write the keyed record:

```json
{
  "kind": "typed",
  "failure": "Observed capture failure; capture did not run to completion",
  "clinician_reply": "The clinician's answer choosing to type the case",
  "file": "typed-case.md",
  "sha256": "SHA-256 of his typed capture",
  "draft_sha256": "SHA-256 of the final draft's raw bytes"
}
```

Every quotation then points at his typed capture made by listening, with him as its human check.
The record never calls this machine transcription. Use the same `check` command. For a case
supplied entirely in a document, the keyed record is `{"kind":"none","reason":"The faculty case is a document, with no video narration"}`,
with the actual reason. Neither route uses auto-captions. Exit 1 is a review finding; exit 2 means
the capture could not complete or its inputs could not be read. Resolve either before proceeding.
