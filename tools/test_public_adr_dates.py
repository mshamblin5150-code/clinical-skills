"""Exact public metadata proof controls for the PHI date view.

phi-scan: synthetic

All names, dates and Git documents here are invented fixtures.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import phi_scan as ps


class PublicAdrDates(unittest.TestCase):
    METADATA = (
        "**Point 3 is narrowed rather than overruled — see [ADR 0026](0026-public.md), 1988-04-17.**",
        "dated record of what was decided on 1988-04-17",
        "**Corrected in place on 1988-04-17:**",
        "Correction, 1988-04-17, on [#1058](https://github.com/mshamblin5150-code/clinical-skills/issues/1058)'s",
    )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = "0001-public-metadata.md"
        self.path = "docs/adr/" + self.name
        self.original = "*Superseded in part 1988-04-17.* Public wording recorded 1988-04-17."
        self.normalized = "*Superseded 1988-04-17.* Public wording recorded 1988-04-17."
        self.source = "# Public fixture\n\n" + self.original + "\n\n" + "\n\n".join(self.METADATA) + "\n"
        full = self.root / self.path
        full.parent.mkdir(parents=True)
        full.write_bytes(self.source.encode())
        self.git("init", "-q")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "public synthetic fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.git("update-ref", "refs/remotes/origin/main", self.revision)
        digest = hashlib.sha256(self.source.encode()).hexdigest()
        self.report = {
            "revision": self.revision,
            "records": [{"path": self.name, "sha256": digest}],
            "unresolved_legacy_markers": [{
                "record": self.name, "source_text": self.source,
                "source_sha256": digest, "original_marker": self.original,
                "normalized_marker": self.normalized,
                "reason": "Unattributed public fixture", "follow_up": 1,
            }],
            "pairs": [{"later_path": self.path, "earlier_path": self.path,
                       "evidence": [self.original], "reason": "1988-04-17"}],
        }

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              check=True).stdout.decode()

    def view(self, text, path=None, report=None):
        return ps.public_adr_date_text(text, self.path if path is None else path,
            root=self.root, report=self.report if report is None else report)

    def test_opening_span_only_without_proof(self):
        text = self.normalized + " Patient date 1988-04-17."
        view = self.view(text, report={})
        self.assertEqual(len(text), len(view))
        self.assertEqual(view.count("1988-04-17"), 2)
        self.assertEqual(self.view(text, path="other.md", report={}), text)

    def test_exact_public_body_not_appended_patient_date(self):
        text = self.normalized + "\nPatient date 1988-04-17."
        view = self.view(text)
        self.assertEqual(len(view), len(text))
        self.assertEqual(view.count("1988-04-17"), 1)
        self.assertEqual(view.splitlines()[1], text.splitlines()[1])

    def test_json_field_context_and_literal_offsets(self):
        text = json.dumps(self.report, indent=2)
        view = self.view(text, path=ps.PUBLIC_ADR_REPORT)
        self.assertEqual(len(view), len(text))
        self.assertEqual(view.count("1988-04-17"), 1)  # reason remains scanned
        self.assertEqual(view.count("\n"), text.count("\n"))

    def test_retained_old_account_is_attested_inside_canonical_marker_only(self):
        marker = "*Superseded 1988-04-17.* New quote. Original account: " + self.original
        text = marker + "\n\nPatient date 1988-04-17."
        self.assertEqual(self.view(text).count("1988-04-17"), 1)
        self.assertEqual(self.view(self.original), self.original)

    def test_closed_governance_tokens_need_same_record_public_proof(self):
        for metadata in self.METADATA:
            with self.subTest(metadata=metadata):
                text = "*Superseded 1988-04-17.* New account. " + metadata + " Patient date 1988-04-17."
                self.assertEqual(self.view(text).count("1988-04-17"), 1)
                self.assertEqual(self.view(metadata), metadata)
                unattested = metadata.replace("1988-04-17", "1989-04-17")
                self.assertIn("1989-04-17", self.view("*Superseded 1988-04-17.* " + unattested))
                self.assertEqual(self.view(text, report={}).count("1988-04-17"), 2)

    def test_mutated_source_hash_revision_and_public_remote_fail_closed(self):
        for mutate in (
            lambda r: r["records"][0].update(sha256="0" * 64),
            lambda r: r.update(revision="0" * 40),
            lambda r: r["unresolved_legacy_markers"][0].update(source_text=self.source + "x"),
        ):
            report = copy.deepcopy(self.report)
            mutate(report)
            text = json.dumps(report)
            view = self.view(text, path=ps.PUBLIC_ADR_REPORT)
            # A mismatched retained source cannot acquire an exemption even
            # if its manifest still attests the separate immutable Git blob.
            source_token = json.dumps(report["unresolved_legacy_markers"][0]["source_text"])
            self.assertIn(source_token, view)
        self.git("update-ref", "-d", "refs/remotes/origin/main")
        text = json.dumps(self.report)
        self.assertEqual(self.view(text, path=ps.PUBLIC_ADR_REPORT), text)

    def test_no_git_provides_no_public_quote_exemption(self):
        with mock.patch.object(ps.subprocess, "run", side_effect=OSError("unavailable")):
            text = json.dumps(self.report)
            self.assertEqual(self.view(text, path=ps.PUBLIC_ADR_REPORT), text)

    def test_name_and_shape_checks_keep_original_surface(self):
        text = self.normalized + "\nJordan Vance DOB 4/17/88 MRN 123456"
        index = ps.build_index({"Jordan Vance"}, {"4/17/88"})
        with mock.patch.object(ps, "REPO_ROOT", self.root):
            (self.root / ps.PUBLIC_ADR_REPORT).write_text(json.dumps(self.report))
            findings = ps.scan_file_text(text, self.path, index)
        rules = [finding.rule for finding in findings]
        self.assertIn("corpus-name", rules)
        self.assertIn("corpus-date", rules)
        self.assertIn("dob-with-date", rules)
        self.assertIn("mrn-with-digits", rules)

    def test_changed_quote_and_same_date_by_value_are_not_attested(self):
        report = copy.deepcopy(self.report)
        report["pairs"][0]["evidence"] = ["Patient date 1988-04-17."]
        text = json.dumps(report)
        self.assertIn(json.dumps(report["pairs"][0]["evidence"][0]),
                      self.view(text, path=ps.PUBLIC_ADR_REPORT))
        report["pairs"][0]["evidence"] = ["1988-04-17"]
        text = json.dumps(report)
        self.assertIn(json.dumps("1988-04-17"),
                      self.view(text, path=ps.PUBLIC_ADR_REPORT))


if __name__ == "__main__":
    unittest.main()
