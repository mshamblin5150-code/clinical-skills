"""Recovered unchanged refusal parser and discovery seams; no benchmark main.

Source: 4711d30b9c6f547cfe628dd463798f4ba367f371. Profiling is excluded.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

AUDIT_PATH = "tools/code_set_database_reader_check.py"
AUDIT_HASH = "386758808f5b6479ca3d2dad0bf35671e5a4db39651d5a0c2c83b064bd819d08"
PAYLOAD_HASH = "83ffec3f4a7700d6d382c3c773a2b08ad88b2b075b39b5b919941b7072abd9d9"
MARKER = "CODE_SET_DATABASE_OPEN_REFUSED"
RESULT_PREFIX = "LAZY_PROOF_RESULT:"
LOCK_VARIABLES = ("CLINICAL_SKILLS_LOCK_ROOT", "CLINICAL_SKILLS_TEST_LOCK_ROOT")

class Refused(RuntimeError):
    """A literal observer reason, never child output."""

def require(condition, reason):
    if not condition:
        raise Refused(reason)

def normalized_bytes(path):
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def original_payload(repo):
    source = normalized_bytes(repo / AUDIT_PATH)
    require(digest(source) == AUDIT_HASH, "audit_source_hash_mismatch")
    tree = ast.parse(source.decode("utf-8"))
    assignments = {
        node.targets[0].id: node.value for node in tree.body
        if isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    }
    require(ast.literal_eval(assignments["REFUSAL_MARKER"]) == MARKER,
            "refusal_marker_changed")
    expression = assignments["_SUBPROCESS"]
    require(isinstance(expression, ast.JoinedStr), "payload_shape_changed")
    pieces = []
    for value in expression.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            pieces.append(value.value)
        else:
            require(
                isinstance(value, ast.FormattedValue)
                and isinstance(value.value, ast.Name)
                and value.value.id == "REFUSAL_MARKER"
                and value.conversion == -1 and value.format_spec is None,
                "payload_interpolation_changed",
            )
            pieces.append(MARKER)
    payload = "".join(pieces)
    require(digest(payload.encode("utf-8")) == PAYLOAD_HASH, "payload_hash_mismatch")
    return payload

def parse_child(result):
    rows = [line[len(RESULT_PREFIX):] for line in result["stdout"].splitlines()
            if line.startswith(RESULT_PREFIX)]
    require(result["returncode"] == 0 and len(rows) == 1, "observer_child_failed")
    row = json.loads(rows[0])
    require(isinstance(row, dict), "observer_child_report_invalid")
    return row

def classify_probe(result, expected_count):
    report = result["stdout"] + result["stderr"]
    # Same precedence as _readers_under_refusal: marker first, then return code.
    classification = "reader" if MARKER in report else "error" if result["returncode"] else "nonreader"
    counts = re.findall(r"(?m)^Ran (\d+) tests? in [0-9.]+s\s*$", report)
    clean_footer = re.findall(r"(?m)^OK\s*$", report)
    count = int(counts[0]) if len(counts) == 1 else None
    completed = count == expected_count and len(clean_footer) == 1
    return {
        "classification": classification, "refusal_marker_present": MARKER in report,
        "module_tests_run": count, "module_tests_expected": expected_count,
        "completed_test_result": completed,
        "valid": classification == "nonreader" and result["returncode"] == 0 and completed,
    }

def child(action, repo):
    """Untimed observation children. The timed probes do not call this wrapper."""
    import unittest

    tools = repo / "tools"
    sys.path.insert(0, str(tools))
    if action == "validate-temp":
        import repo_root
        require(not any(name in os.environ for name in LOCK_VARIABLES), "child_inherited_lock_override")
        for name in ("TEMP", "TMP"):
            if os.environ.get(name):
                repo_root.ensure_outside_checkout(os.environ[name])
        repo_root.ensure_outside_checkout(tempfile.gettempdir())
        row = {"outside_checkout_temp": True, "temp_environment_unchanged": True}
    elif action == "discover":
        loader = unittest.TestLoader()
        def cases(member):
            if isinstance(member, unittest.TestSuite):
                for nested in member:
                    yield from cases(nested)
            else:
                yield member
        # Import output is captured by the parent, never forwarded into public logs.
        discovered = tuple(cases(loader.discover(start_dir=tools, top_level_dir=tools)))
        failed = sum(type(test).__name__ == "_FailedTest" and type(test).__module__ == "unittest.loader"
                     for test in discovered)
        require(not loader.errors and failed == 0 and discovered, "discovery_failed")
        ids = sorted(test.id() for test in discovered)
        require(len(set(ids)) == len(ids), "duplicate_discovered_ids")
        module_count = sum(test.id().startswith("test_suite_ids.") for test in discovered)
        require(module_count > 0, "measured_module_missing")
        row = {"test_count": len(ids), "sorted_ids_sha256": digest(json.dumps(
            ids, ensure_ascii=True, separators=(",", ":")).encode("utf-8")),
            "loader_error_count": 0, "module_test_count": module_count,
            "executed_test_count": 0, "ids_encoding": "sorted JSON array, ASCII escaped, compact"}
    else:
        raise Refused("unknown_child_action")
    print(RESULT_PREFIX + json.dumps(row, sort_keys=True))
