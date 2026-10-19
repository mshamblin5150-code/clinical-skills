#!/usr/bin/env python3
"""Private, two-stage case video capture and its coursework completion gate.

The ordinary interpreter uses only the standard library. Heavy imports run only
in the explicitly selected environment. See DECLARED_LIMITS for the ceiling.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from difflib import SequenceMatcher
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
from urllib.parse import urlsplit

import completion_checks
import artifact_lock
from console_codec import require_python_floor, use_utf8
import coursework_run


EXPECTED_ROW = "the case video capture"
MODELS = ("tiny.en", "base.en", "small.en", "medium.en", "large-v2", "large-v3")
DECLARED_LIMITS = (
    ("shared-engine", "Agreement between passes is not proof; both can mishear alike."),
    ("frame-distinctness-unproven", "Frame count is a floor, not proof every slide was distinct or detected."),
    ("file-identity", "A fingerprint binds the local file, not what YouTube serves later."),
    ("narration-classification-reader-owned", "The run decides which drug names, doses and numbers are absent from slides."),
    ("reader-record", "Recorded frame reads, clinician answers and quotation locations are declarations, not observed listening or semantic verification."),
    ("case-kind", "A false non-video declaration or unrecorded quotation cannot be detected from prose."),
    ("av-offsets-unmeasured", "Timestamps locate decoded media; unusual audio/video offsets and word timing errors require a video check."),
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
    try:
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def inside(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError("path escapes its private directory")
    return path


def private_run(path: Path) -> Path:
    path = path.resolve()
    if not path.is_dir() or not any(parent.name == "scratch" for parent in path.parents):
        raise ValueError("capture needs an existing run directory under scratch")
    return path


def checked_files(root: Path, files: dict) -> None:
    if not isinstance(files, dict) or not files:
        raise ValueError("capture has no file fingerprints")
    for name, expected in files.items():
        if digest(inside(root, name)) != expected:
            raise ValueError("capture file is missing or changed")


def disagreements(first: list[dict], second: list[dict]) -> list[dict]:
    """Align the entire token sequences, including second-pass-only speech.

    Segment boundaries do not vote on agreement. Punctuation differences remain
    visible, a conservative choice rather than silently normalizing a dose.
    """
    def tokens(segments):
        return [(word, segment["start"], segment["end"])
                for segment in segments for word in segment["text"].split()]

    a, b = tokens(first), tokens(second)
    result = []
    for tag, i, j, k, l in SequenceMatcher(
        None, [w[0] for w in a], [w[0] for w in b], autojunk=False,
    ).get_opcodes():
        if tag == "equal":
            continue
        population = a[i:j] + b[k:l]
        result.append({
            "id": f"D{len(result) + 1}",
            "start": min(w[1] for w in population),
            "end": max(w[2] for w in population),
            "first": " ".join(w[0] for w in a[i:j]),
            "second": " ".join(w[0] for w in b[k:l]),
        })
    return result


def valid_capture(root: Path, *, transcribed: bool = False) -> dict:
    record = read_json(root / "capture.json")
    checked_files(root, record["files"])
    if record["route"] not in {"youtube", "local", "winx"}:
        raise ValueError("unknown acquisition route")
    frames = record["frames"]
    if not frames or len({row["file"] for row in frames}) != len(frames):
        raise ValueError("frame population is empty or duplicated")
    for frame in frames:
        if frame["file"] not in record["files"] or not math.isfinite(frame["seconds"]):
            raise ValueError("frame is not fingerprinted or timestamped")
    if record["video"] not in record["files"]:
        raise ValueError("video is not fingerprinted")
    if transcribed:
        if record["state"] != "transcribed":
            raise ValueError("two transcription passes have not completed")
        models = record["models"]
        if len(models) != 2 or any(model not in MODELS for model in models) or models[0].split("-")[0] == models[1].split("-")[0]:
            raise ValueError("transcription requires different model sizes")
        for name in ("pass-1.json", "pass-2.json", "disagreements.json", "transcript.md", "slide-terms.json"):
            if name not in record["files"]:
                raise ValueError("transcription evidence is not fingerprinted")
        terms = read_json(root / "slide-terms.json")
        if sorted(terms["frames_read"]) != sorted(row["file"] for row in frames) or not nonempty(terms["terms"]) or not nonempty(terms["model_reason"]):
            raise ValueError("slide vocabulary or the complete pre-transcription read is missing")
        expected = disagreements(read_json(root / "pass-1.json"), read_json(root / "pass-2.json"))
        if read_json(root / "disagreements.json") != expected:
            raise ValueError("disagreement population does not match the two passes")
    return record


def prepare(args, root: Path) -> None:
    """Heavy environment only: acquire one video and retain changed frames."""
    import av
    import numpy as np

    url = urlsplit(args.source)
    if url.scheme in {"https", "http"} or "://" in args.source:
        if url.scheme not in {"https", "http"} or url.hostname not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
            raise ValueError("only a YouTube link or a local video file is accepted")
        import yt_dlp
        options = {
            "outtmpl": str(root / "video.%(ext)s"), "noplaylist": True,
            "format": "best[ext=mp4]/best", "quiet": True,
            "writesubtitles": False, "writeautomaticsub": False,
        }
        with yt_dlp.YoutubeDL(options) as download:
            info = download.extract_info(args.source, download=True)
            video = Path(download.prepare_filename(info)).resolve()
        route = "youtube"
    else:
        source = Path(args.source).resolve()
        video = root / ("video" + source.suffix.lower())
        shutil.copyfile(source, video)
        route = args.route
    # Read only the acquired file; subtitle streams are never consumed.
    frames = []
    files = {video.name: digest(video)}
    (root / "frames").mkdir()
    with av.open(str(video)) as container:
        if not container.streams.video or not container.streams.audio:
            raise ValueError("the file must contain video and audio streams")
        previous = None
        decoded = 0
        for frame in container.decode(video=0):
            decoded += 1
            if frame.time is None:
                raise ValueError("a decoded frame has no timestamp")
            pixels = frame.reformat(width=160, height=90, format="gray").to_ndarray().astype(np.int16)
            # Count visibly changed pixels, so a new bullet is not diluted by
            # a mostly white slide. Ignore low-contrast codec noise.
            change = 1.0 if previous is None else float(np.count_nonzero(np.abs(pixels - previous) > 16)) / pixels.size
            if change < args.threshold:
                continue
            name = f"frames/frame-{len(frames) + 1:06d}.png"
            # PyAV's image conversion requires Pillow, isolated with the worker.
            frame.to_image().save(root / name)
            frames.append({"file": name, "seconds": float(frame.time)})
            files[name] = digest(root / name)
            previous = pixels
    if not frames:
        raise ValueError("no video frames were decoded")
    write_json(root / "capture.json", {
        "state": "prepared", "route": route, "source": args.source,
        "video": video.name, "files": files, "frames": frames,
        "decoded_frames": decoded, "threshold": args.threshold,
    })


def transcribe(args, root: Path) -> None:
    """Heavy environment only: read frames first, then run both local models."""
    from faster_whisper import WhisperModel

    record = valid_capture(root)
    if record["state"] != "prepared":
        raise ValueError("use a new capture directory for another transcription")
    terms = read_json(Path(args.terms))
    names = [row["file"] for row in record["frames"]]
    if sorted(terms["frames_read"]) != sorted(names) or not isinstance(terms["terms"], str) or not terms["terms"].strip() or not terms["model_reason"].strip():
        raise ValueError("read every frame and supply its vocabulary and the model-size rationale")
    models = args.models
    if models[0].split("-")[0] == models[1].split("-")[0]:
        raise ValueError("choose models of different sizes")
    write_json(root / "slide-terms.json", terms)
    passes = []
    timings = []
    for number, size in enumerate(models, 1):
        started = time.monotonic()
        model = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=args.threads)
        segments, _ = model.transcribe(
            str(root / record["video"]), language="en", beam_size=5,
            initial_prompt=terms["terms"], condition_on_previous_text=False,
        )
        rows = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
        if not rows or not any(row["text"] for row in rows):
            raise ValueError("a transcription pass returned no speech")
        passes.append(rows)
        write_json(root / f"pass-{number}.json", rows)
        timings.append(time.monotonic() - started)
        del model
        gc.collect()
    differences = disagreements(*passes)
    write_json(root / "disagreements.json", differences)
    text = "# Machine transcription — no human listened to verify this text\n\n"
    text += "Working material checked against the video; quote slide data from the slide.\n\n"
    text += "\n".join(f"[{s['start']:.3f}–{s['end']:.3f}] {s['text']}" for s in passes[0]) + "\n"
    (root / "transcript.md").write_text(text, encoding="utf-8")
    for name in ("pass-1.json", "pass-2.json", "disagreements.json", "transcript.md", "slide-terms.json"):
        record["files"][name] = digest(root / name)
    record.update(state="transcribed", models=list(models), pass_seconds=timings)
    write_json(root / "capture.json", record)


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_review(run: Path, key: str, draft: bytes | str | None) -> tuple[int, int]:
    """Check the declared source route and all owed confirmations for one draft."""
    review = read_json(run / "case-video" / f"{key}.json")
    if review["kind"] == "none":
        if not nonempty(review["reason"]):
            raise ValueError("non-video declaration needs a reason")
        return 0, 0
    if isinstance(draft, str):
        draft = draft.encode("utf-8")
    if draft is None or hashlib.sha256(draft).hexdigest() != review["draft_sha256"]:
        raise ValueError("video review does not bind the current draft")
    if review["kind"] == "typed":
        if not all(nonempty(review[field]) for field in ("failure", "clinician_reply")):
            raise ValueError("typed route needs the failure and clinician's choice")
        if digest(inside(run, review["file"])) != review["sha256"]:
            raise ValueError("typed capture is missing or changed")
        return 0, 0
    if review["kind"] != "machine":
        raise ValueError("unknown case capture kind")
    root = inside(run, review["capture"])
    record = valid_capture(root, transcribed=True)
    if digest(root / "capture.json") != review["manifest_sha256"]:
        raise ValueError("capture manifest changed after review")
    frames = [row["file"] for row in record["frames"]]
    if sorted(review["frames_read"]) != sorted(frames):
        raise ValueError("frame reading is incomplete")
    if not nonempty(review["narration_review"]):
        raise ValueError("narration-only clinical-data review is missing")
    first = read_json(root / "pass-1.json")
    narration = " ".join(row["text"] for row in first)
    extras = review["narration_only"]
    if not isinstance(extras, list):
        raise ValueError("narration-only entries must be a list, including when empty")
    extra_ids = []
    for row in extras:
        if not nonempty(row["id"]) or not row["id"].startswith("N") or row["kind"] not in {"drug", "dose", "number"}:
            raise ValueError("narration-only entry is invalid")
        if not nonempty(row["quote"]) or row["quote"] not in narration or not math.isfinite(row["seconds"]) or row["seconds"] < 0:
            raise ValueError("narration-only quotation or timestamp is invalid")
        extra_ids.append(row["id"])
    if len(set(extra_ids)) != len(extra_ids):
        raise ValueError("narration-only entries are duplicated")
    owed = {row["id"] for row in read_json(root / "disagreements.json")} | set(extra_ids)
    answers = review["answers"]
    if not isinstance(answers, dict) or set(answers) != owed or not all(nonempty(value) for value in answers.values()):
        raise ValueError("a confirmation-list entry has no clinician answer or the list changed")
    if not isinstance(review["uses"], list):
        raise ValueError("quotation and fault locations must be recorded, including when empty")
    for use in review["uses"]:
        if use["id"] not in owed or not nonempty(use["location"]):
            raise ValueError("a quoted or faulted datum has no confirmed entry")
    return len(frames), len(owed)


def completion_gate(run: Path, submission: str | None, drafts: dict[str, bytes | str] | None = None) -> tuple[bool, str]:
    frozen = completion_checks.exemption(run, submission, "case_video", EXPECTED_ROW)
    if frozen is not None:
        return False, frozen
    if submission is None:
        return False, f"{EXPECTED_ROW}: not graded - --submission was not supplied"
    try:
        keys = coursework_run.submission_keys(submission)
        counts = [check_review(run, key, (drafts or {}).get(key)) for key in keys]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError):
        return True, f"{EXPECTED_ROW}: finding - missing, changed or incomplete capture review; inspect the private record and capture files"
    return False, f"{EXPECTED_ROW}: clean; frames read {sum(c[0] for c in counts)}; confirmations {sum(c[1] for c in counts)}"


def apply_completion_gate(grade, run: Path, submission: str | None, drafts: dict[str, bytes | str]):
    failed, report = completion_gate(run, submission, drafts)
    return replace(grade, findings_failed=grade.findings_failed or failed, reports=grade.reports + (report,))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "transcribe", "check"))
    parser.add_argument("run", type=Path)
    parser.add_argument("--capture", default="case-video/capture")
    parser.add_argument("--python", type=Path, help="Python in the separate capture environment")
    parser.add_argument("--source")
    parser.add_argument("--route", choices=("local", "winx"), default="local")
    parser.add_argument("--terms", type=Path)
    parser.add_argument("--models", nargs=2, choices=MODELS, default=("large-v3", "small.en"))
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--threshold", type=float, default=0.001)
    parser.add_argument("--submission")
    parser.add_argument("--draft", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        run = private_run(args.run)
        if args.action == "check":
            if not args.submission:
                raise ValueError("check requires --submission")
            drafts = {args.submission: args.draft.read_bytes()} if args.draft else {}
            failed, report = completion_gate(run, args.submission, drafts)
            print(report)
            return int(failed)
        root = inside(run, args.capture)
        if not math.isfinite(args.threshold) or not 0 < args.threshold <= 1 or args.threads < 1:
            raise ValueError("invalid frame threshold or thread count")
        if args.action == "prepare" and not args.source:
            raise ValueError("prepare requires --source")
        if args.action == "transcribe" and not args.terms:
            raise ValueError("transcribe requires --terms after reading the slides")
        if not args.worker:
            # A POSIX venv executable commonly symlinks to the base Python;
            # comparing resolved binaries would reject a valid isolated env.
            if args.python is None or not args.python.is_file() or args.python.absolute() == Path(sys.executable).absolute():
                raise ValueError("supply --python from a separate capture environment")
            if args.action == "prepare":
                root.mkdir(parents=True, exist_ok=False)
            else:
                valid_capture(root)
            # Keep the read/modify/write sequence exclusive, including the
            # worker. The worker inherits this operation, not a second lock.
            with artifact_lock.hold(root, "case video capture"):
                with (root / f"{args.action}.log").open("w", encoding="utf-8") as log:
                    result = subprocess.run([str(args.python), "-E", "-s", str(Path(__file__).resolve()), *argv, "--worker"], stdout=log, stderr=log)
            if result.returncode:
                raise ValueError("capture failed; private worker log retained. Choose repair or clinician-typed capture; a failed download can use a WinX-saved file")
        elif args.action == "prepare":
            prepare(args, root)
        else:
            transcribe(args, root)
        record = valid_capture(root, transcribed=args.action == "transcribe")
        print(f"Case video capture: {record['state']}; frames {len(record['frames'])}")
        if args.action == "transcribe":
            print(f"disagreeing spans {len(read_json(root / 'disagreements.json'))}; clinician review required")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, ImportError) as failure:
        # Error messages from decoders and downloaders may carry private text.
        if args.worker:
            print(f"capture worker failed: {type(failure).__name__}: {failure}", file=sys.stderr)
        else:
            print("Case video capture: did not complete; inspect the private log and inputs, then choose repair or clinician-typed capture", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
