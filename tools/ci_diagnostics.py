"""Bounded, diagnostic-only CI receipts. No decision here controls execution.

Edited-event contract: octokit/webhooks at
aa80c24a3f55354465b8b1438d33dd5602956d0d,
payload-schemas/api.github.com/pull_request/edited.schema.json.
The classifier accepts only the title/body subset of that schema; base edits
always require FULL. Prior values in that subset must be strings.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path

MAX_BYTES = 16 * 1024
MAX_EVENT_BYTES = 2 * 1024 * 1024
ROOT = Path(__file__).resolve().parent.parent


def _sha(value):
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) else None


def _number(value):
    if isinstance(value, str) and re.fullmatch(r"[1-9][0-9]{0,19}", value):
        return int(value)
    return None


def classify_event(event, event_name, attempt, identity=None):
    """Return FULL unless a first-attempt, identified metadata edit is strict.

    CANDIDATE is only an observation; the full suite always runs.
    Unknown or malformed changes fail closed, including a null prior body.
    """
    if event_name != "pull_request" or attempt != "1" or not isinstance(event, dict):
        return "FULL"
    if event.get("action") != "edited":
        return "FULL"
    changes = event.get("changes")
    if not isinstance(changes, dict) or not changes or not changes.keys() <= {"title", "body"}:
        return "FULL"
    for value in changes.values():
        if not isinstance(value, dict) or set(value) != {"from"} or not isinstance(value["from"], str):
            return "FULL"
    pr = event.get("pull_request")
    repository = event.get("repository")
    if not isinstance(pr, dict) or not isinstance(repository, dict):
        return "FULL"
    number = event.get("number")
    if type(number) is not int or number <= 0 or type(pr.get("number")) is not int or pr["number"] != number:
        return "FULL"
    if type(repository.get("id")) is not int or repository["id"] <= 0:
        return "FULL"
    for side in ("head", "base"):
        endpoint = pr.get(side)
        if not isinstance(endpoint, dict) or not _sha(endpoint.get("sha")):
            return "FULL"
        repo = endpoint.get("repo")
        if not isinstance(repo, dict) or type(repo.get("id")) is not int or repo["id"] <= 0:
            return "FULL"
    if pr["base"]["repo"]["id"] != repository["id"] or not _sha(pr.get("merge_commit_sha")):
        return "FULL"
    if not isinstance(identity, dict):
        return "FULL"
    for field in ("checkout_sha", "event_sha", "head_sha", "base_sha", "merge_sha", "workflow_sha"):
        if not _sha(identity.get(field)):
            return "FULL"
    for field in ("workflow_digest", "suite_digest", "diagnostics_digest"):
        value = identity.get(field)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            return "FULL"
    if (type(identity.get("run_id")) is not int or identity["run_id"] <= 0
            or type(identity.get("attempt")) is not int or identity["attempt"] != 1
            or identity.get("job_role") not in ("suite", "canary", "floor")
            or identity.get("event") != event_name):
        return "FULL"
    if any(not _label(identity.get(field)) for field in
           ("python_release", "python_implementation", "os", "architecture")):
        return "FULL"
    head, base, merge = pr["head"]["sha"], pr["base"]["sha"], pr["merge_commit_sha"]
    if (identity["checkout_sha"] != merge or identity["event_sha"] != merge
            or identity["merge_sha"] != merge or identity["head_sha"] != head
            or identity["base_sha"] != base or identity.get("checkout_parents") != [base, head]):
        return "FULL"
    return "CANDIDATE"


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def read_event(path):
    """Read a bounded event locally; retain no event text in the receipt."""
    try:
        with Path(path).open("rb") as handle:
            raw = handle.read(MAX_EVENT_BYTES + 1)
        if len(raw) > MAX_EVENT_BYTES:
            return {}
        event = json.loads(raw, object_pairs_hook=_unique_object)
        return event if isinstance(event, dict) else {}
    except (OSError, ValueError, TypeError, RecursionError):
        return {}


def _git_sha(*args):
    try:
        result = subprocess.run(
            ["git", "rev-parse", *args], cwd=ROOT, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=5, check=False,
        )
        return _sha(result.stdout.strip()) if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _digest(relative):
    try:
        return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    except OSError:
        return None


def _label(value):
    # Only short machine labels, never paths or free-form event content.
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value) else None


def provenance(env, event):
    pr = event.get("pull_request")
    pr = pr if isinstance(pr, dict) else {}
    sides = {}
    for side in ("head", "base"):
        value = pr.get(side)
        sides[side] = _sha(value.get("sha")) if isinstance(value, dict) else None
    return {
        "checkout_sha": _git_sha("HEAD"),
        "checkout_parents": [_git_sha("HEAD^1"), _git_sha("HEAD^2")],
        "event_sha": _sha(env.get("GITHUB_SHA")),
        "head_sha": sides["head"], "base_sha": sides["base"],
        "merge_sha": _sha(pr.get("merge_commit_sha")),
        "workflow_sha": _sha(env.get("GITHUB_WORKFLOW_SHA")),
        "workflow_digest": _digest(".github/workflows/checks.yml"),
        "suite_digest": _digest("tools/suite.py"),
        "diagnostics_digest": _digest("tools/ci_diagnostics.py"),
        "event": env.get("GITHUB_EVENT_NAME") if env.get("GITHUB_EVENT_NAME") in {"pull_request", "push", "workflow_dispatch"} else None,
        "run_id": _number(env.get("GITHUB_RUN_ID")),
        "attempt": _number(env.get("GITHUB_RUN_ATTEMPT")),
        "job_role": env.get("GITHUB_JOB") if env.get("GITHUB_JOB") in {"suite", "canary", "floor"} else None,
        "python_release": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "os": _label(platform.system()), "architecture": _label(platform.machine()),
        "hosted_image": _label(env.get("ImageOS")),
        "hosted_image_version": _label(env.get("ImageVersion")),
    }


def encode_receipt(receipt):
    raw = (json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("receipt exceeds size cap")
    return raw


def write_receipt(metrics, *, env=None):
    """Write only an opted-in receipt; errors propagate to the suite boundary."""
    env = os.environ if env is None else env
    target = env.get("CI_DIAGNOSTIC_RECEIPT")
    if not target:
        return
    event = read_event(env.get("GITHUB_EVENT_PATH"))
    identity = provenance(env, event)
    receipt = {
        "schema_version": 1,
        "classification": classify_event(event, env.get("GITHUB_EVENT_NAME"), env.get("GITHUB_RUN_ATTEMPT"), identity),
        "provenance": identity,
        "execution": metrics,
    }
    raw = encode_receipt(receipt)
    Path(target).write_bytes(raw)
    summary = env.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write(
                "\n### CI diagnostics (full suite always runs)\n\n"
                f"Event classification: {receipt['classification']}. "
                f"Suite exit: {metrics['exit_code']}; "
                f"discovered: {metrics['discovered']}; "
                f"unaccounted: {metrics['unaccounted']}.\n"
            )
