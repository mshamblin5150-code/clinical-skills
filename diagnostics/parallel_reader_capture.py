"""Bounded, private capture analysis for the unchanged refusal payload.

Marker-first remains the original classification. A separate screen refuses
unrelated or unread failure frames; it never silently changes a reader to clean.
The parser recognizes stock unittest text, not every possible custom reporter.
"""

from __future__ import annotations

import hashlib
import ast
import io
from pathlib import Path
import re

from parallel_reader_scheduler import MARKER


LINE_LIMIT = 65536
FRAME_LIMIT = 65536
FRAME_COUNT = 8
RAN = re.compile(r"^Ran (\d+) tests? in [0-9.]+s\s*$")
FAILED = re.compile(r"^FAILED \(([^)]*)\)\s*$")
OK = re.compile(r"^OK(?: \(([^)]*)\))?\s*$")
EXCEPTION = re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*):(?: (.*))?$")
SAFE_EXCEPTION_TYPES = frozenset({"AssertionError", "ValueError", "RuntimeError", "TypeError", "OSError",
    "FileNotFoundError", "FileExistsError", "PermissionError", "ImportError", "ModuleNotFoundError",
    "AttributeError", "KeyError", "IndexError", "TimeoutError", "UnicodeDecodeError", "SyntaxError"})
QUALIFIED_ANCHOR_SHA256 = "8d0a2570665b20e855a091d43c84c309e5fa3e5e1adff85efb0bf8d90620cf16"
QUALIFIED_WRAPPER_HEADER = (
    "FAIL: test_each_behavior_subject_names_a_passing_control "
    "(test_anchor_scan.EveryBehaviorLimitHasALiveControl.test_each_behavior_subject_names_a_passing_control)")
QUALIFIED_WRAPPER_PREFIX = (
    "False is not true : note-side ICD-10 database membership: "
    "[(<test_anchor_scan.AgreementModes "
    "testMethod=test_vitamin_b12_in_final_diagnosis_is_counted_but_not_bound>, ")


def qualified_nested_refusal(header, terminal, lookup):
    """Exactly one source-qualified wrapper; never eval a TestCase object repr.

The original anchor source at QUALIFIED_ANCHOR_SHA256 supplies this contract.
Specificity's similar wrapper is deliberately not qualified. Hidden/suppressed
exceptions and arbitrary custom reports remain outside this visible-text screen.
"""
    if header != QUALIFIED_WRAPPER_HEADER or terminal is None or terminal[0] != "AssertionError":
        return False
    message = terminal[1]
    if not message.startswith(QUALIFIED_WRAPPER_PREFIX) or not message.endswith(")]"):
        return False
    literal = message[len(QUALIFIED_WRAPPER_PREFIX):-2]
    if not literal or len(literal.encode("utf-8")) >= LINE_LIMIT:
        return False
    try:
        expression = ast.parse(literal, mode="eval").body
        if not isinstance(expression, ast.Constant) or not isinstance(expression.value, str):
            return False
        nested = ast.literal_eval(expression)
        # Stock repr is one canonical string literal, not adjacent literals,
        # an expression, an object repr, or another accepted Python spelling.
        if repr(nested) != literal or len(nested.encode("utf-8")) >= FRAME_LIMIT:
            return False
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return False
    lines = nested.splitlines()
    expected = "AssertionError: " + MARKER + ":" + lookup
    return (len(lines) >= 3 and nested.endswith("\n")
            and lines[0] == "Traceback (most recent call last):"
            and lines[-1] == expected
            and sum(line == "Traceback (most recent call last):" for line in lines) == 1
            and sum(EXCEPTION.fullmatch(line) is not None for line in lines) == 1
            and all(not line or line.startswith(("  ", "\t")) for line in lines[1:-1]))


def summary_counts(text, *, successful):
    counts = {}
    permitted = ({"skipped", "expected failures"} if successful else
                 {"failures", "errors", "skipped", "expected failures", "unexpected successes"})
    if text is not None:
        for part in text.split(", "):
            key, value = part.split("=", 1) if "=" in part else (part, "")
            if key not in permitted or key in counts or not value.isdigit():
                counts["unread"] = 1
            else:
                counts[key] = int(value)
    return counts


def analyze_capture(stdout_path, stderr_path, returncode, lookup, *, private_frames=None, module=None,
                    capture_bytes=None):
    # A caller with coherently verified bytes must not reopen mutable paths.
    if capture_bytes is not None and (type(capture_bytes) is not tuple or len(capture_bytes) != 2
                                     or any(type(raw) is not bytes for raw in capture_bytes)):
        raise ValueError('invalid capture bytes')
    marker = False
    carry = ""
    ran = []
    summaries = []
    frames = []
    active = None
    failure_frames = 0
    unrelated_frames = 0
    unread_frames = 0
    orphan_traceback_count = 0
    output_bytes = 0
    exception_counts = {}
    qualified_wrapper_frames = 0
    digest = hashlib.sha256()

    def finish_frame():
        nonlocal active, failure_frames, unrelated_frames, unread_frames, qualified_wrapper_frames
        if active is None:
            return
        if not active["orphan"]:
            failure_frames += 1
        terminal = active["terminal"]
        structured_frame = (active["terminal_count"] == 1 and active["traceback_count"] == 1
                            and not active["truncated"] and not active["trailing_content"])
        nested_refusal = (module == "test_anchor_scan" and structured_frame
                          and qualified_nested_refusal(active["header"], terminal, lookup))
        if active["orphan"] or terminal is None or not structured_frame:
            unread_frames += 1
        elif terminal != ("AssertionError", MARKER + ":" + lookup) and not nested_refusal:
            unrelated_frames += 1
        if nested_refusal:
            qualified_wrapper_frames += 1
        if terminal is not None:
            kind = terminal[0] if terminal[0] in SAFE_EXCEPTION_TYPES else "OtherException"
            exception_counts[kind] = exception_counts.get(kind, 0) + 1
        if len(frames) < FRAME_COUNT:
            frames.append(bytes(active["bytes"]))
        active = None

    sources = (Path(stdout_path), Path(stderr_path)) if capture_bytes is None else capture_bytes
    for source in sources:
        with (source.open("rb") if capture_bytes is None else io.BytesIO(source)) as stream:
            while True:
                data = stream.readline(LINE_LIMIT)
                if not data:
                    break
                output_bytes += len(data)
                digest.update(data)
                text = data.decode("utf-8", errors="replace")
                marker = marker or MARKER in carry + text
                carry = (carry + text)[-len(MARKER):]
                line = text.rstrip("\r\n")
                if line.startswith(("FAIL: ", "ERROR: ")):
                    finish_frame()
                    active = {"terminal": None, "bytes": bytearray(), "header": line,
                              "terminal_count": 0, "traceback_count": 0,
                              "truncated": False, "trailing_content": False, "orphan": False}
                if line == "Traceback (most recent call last):" and (active is None or active["orphan"]):
                    orphan_traceback_count += 1
                    if active is None:
                        active = {"terminal": None, "bytes": bytearray(), "header": "",
                                  "terminal_count": 0, "traceback_count": 0,
                                  "truncated": False, "trailing_content": False, "orphan": True}
                if active is not None:
                    remaining = FRAME_LIMIT - len(active["bytes"])
                    if remaining > 0:
                        active["bytes"].extend(data[:remaining])
                    if len(data) == LINE_LIMIT and not data.endswith(b"\n"):
                        active["truncated"] = True
                    if line == "Traceback (most recent call last):":
                        active["traceback_count"] += 1
                    terminal = EXCEPTION.fullmatch(line)
                    if terminal and terminal.group(1) not in ("FAIL", "ERROR"):
                        active["terminal_count"] += 1
                        active["terminal"] = (terminal.group(1), terminal.group(2) or "")
                    elif active["terminal"] is not None and line and set(line) not in ({"-"}, {"="}) and not RAN.fullmatch(line):
                        active["trailing_content"] = True
                match = RAN.fullmatch(line)
                if match:
                    finish_frame()
                    ran.append(int(match.group(1)))
                match = FAILED.fullmatch(line)
                if match:
                    summaries.append(("FAILED", summary_counts(match.group(1), successful=False)))
                elif (match := OK.fullmatch(line)) is not None:
                    summaries.append(("OK", summary_counts(match.group(1), successful=True)))
    finish_frame()
    # Preserve the original marker-over-exit-status classification exactly.
    classification = "reader" if marker else "error" if returncode else "nonreader"
    structured = len(ran) == 1 and ran[0] > 0 and len(summaries) == 1
    counts = summaries[0][1] if len(summaries) == 1 else {}
    failures, errors = counts.get("failures", 0), counts.get("errors", 0)
    if classification == "reader":
        valid = (structured and returncode == 1 and summaries[0][0] == "FAILED"
                 and failure_frames > 0 and failure_frames == failures + errors
                 and unrelated_frames == 0 and unread_frames == 0
                 and orphan_traceback_count == 0
                 and not counts.get("unread") and not counts.get("unexpected successes"))
    else:
        valid = (classification == "nonreader" and structured and returncode == 0
                 and summaries[0][0] == "OK" and failure_frames == 0 and orphan_traceback_count == 0
                 and not counts.get("unread"))
    if not valid and private_frames is not None:
        private_frames = Path(private_frames)
        private_frames.mkdir(parents=True, exist_ok=False)
        for index, frame in enumerate(frames):
            (private_frames / ("failure-%02d.txt" % index)).write_bytes(frame)
        # Never publish these frames, their text, or arbitrary path names.
    return {
        "classification": classification, "unexpected": not valid,
        "test_count": ran[0] if len(ran) == 1 else None,
        "skipped": counts.get("skipped", 0), "expected_failures": counts.get("expected failures", 0),
        "failures": failures, "errors": errors, "marker_present": marker,
        "failure_frame_count": failure_frames, "unrelated_failure_frames": unrelated_frames,
        "unread_failure_frames": unread_frames, "structured_result_read": structured,
        "orphan_traceback_count": orphan_traceback_count,
        "output_bytes": output_bytes, "output_sha256": digest.hexdigest(),
        "contaminated": marker and not valid,
        "failure_exception_type_counts": exception_counts,
        "source_qualified_nested_refusal_frames": qualified_wrapper_frames,
    }
