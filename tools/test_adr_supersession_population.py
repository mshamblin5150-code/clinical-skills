"""Exercise citation union, its planted blind form, and stale reader evidence."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import adr_supersession_population as population
from prose_bind import NAMING, bind, section


def fixture():
    return population.derive_records([
        ("0001-first.md", b"# Original ruling\n"),
        ("0002-second.md", b"ADR 0001: this is that question, answered.\n"),
        ("0003-third.md", b"The [earlier ruling](0001-first.md) is narrowed.\n"),
    ])


def classified(report):
    return {
        "records_sha256": report["records_sha256"],
        "pairs": [
            {"later": pair["later"], "earlier": pair["earlier"],
             "classification": "neither", "reason": "A citation alone proves no withdrawal.",
             "evidence": ["Original ruling", "this is that question, answered"]}
            for pair in report["pairs"]
        ],
    }


class PopulationTests(unittest.TestCase):

    def test_command_documentation_names_its_declared_limits(self):
        documentation = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(encoding="utf-8")
        surface = section(documentation, "### ADR supersession binding")
        self.assertEqual((), bind(population.DECLARED_LIMITS, surface, mode=NAMING))
    @unittest.skipUnless(shutil.which('git'), 'Git is required for the immutable-byte fixture.')
    def test_revision_digest_reads_raw_blob_bytes_despite_autocrlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True).stdout
            git('init')
            git('config', 'core.autocrlf', 'false')
            directory = root / 'docs' / 'adr'
            directory.mkdir(parents=True)
            raw = b'# Original\n\nA raw LF record.\n'
            (directory / '0001-first.md').write_bytes(raw)
            git('add', 'docs/adr/0001-first.md')
            hooks = root / 'empty-hooks'
            hooks.mkdir()
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=' + str(hooks),
                'commit', '-m', 'Immutable fixture')
            revision = git('rev-parse', 'HEAD').decode('ascii').strip()
            reports = []
            for setting in ('true', 'false'):
                git('config', 'core.autocrlf', setting)
                reports.append(population.derive_revision(root, revision))
                self.assertEqual(setting, git('config', 'core.autocrlf').decode('ascii').strip())
                self.assertEqual(raw, git('show', revision + ':docs/adr/0001-first.md'))
                self.assertEqual(hashlib.sha256(raw).hexdigest(), reports[-1]['records'][0]['sha256'])
            self.assertEqual(reports[0], reports[1])

    def test_legacy_paragraph_read_normalizes_lines_but_digest_keeps_raw_crlf(self):
        original = '*Superseded grounding marked 2026-09-12.* The old ground\nwas replaced; its decision stands.'
        normalized = original.replace('Superseded grounding marked', 'Superseded')
        source = ('# Record\n\n## Ground\n\n' + original + '\n').replace('\n', '\r\n')
        report = population.derive_records([('0039-old.md', source.encode('utf-8'))])
        report['revision'] = 'a' * 40
        report['unresolved_legacy_markers'] = [dict(
            record='0039-old.md', original_marker=original, normalized_marker=normalized,
            source_text=source, source_sha256=hashlib.sha256(source.encode('utf-8')).hexdigest(),
            follow_up=12, reason='The exact historical ground has no ordinal.',
        )]
        records = {'0039-old.md': source.replace('\r\n', '\n').replace(original, normalized)}
        findings, allowed = population.legacy_marker_findings(report, records)
        self.assertEqual([], findings)
        self.assertEqual({('0039-old.md', normalized)}, allowed)
        self.assertNotEqual(hashlib.sha256(source.replace('\r\n', '\n').encode('utf-8')).hexdigest(), report['records'][0]['sha256'])
        report['unresolved_legacy_markers'][0]['source_text'] = source.replace('\r\n', '\n')
        self.assertTrue(population.legacy_marker_findings(report, records)[0])

    def test_closed_legacy_families_preserve_every_original_character(self):
        examples = (
            '**Superseded by [ADR 0187](0187-floor.md) ruling 1.** The maintainer job stands.',
            'Superseded in part, 2099-09-12: ADR 0187 ruling 14 replaces the floor.',
            '**The key gained a third component on 2099-08-22**; all other words stand.',
            '*(Superseded the same day. Both were read and both take it — ADR 0056, ruled 2099-08-27.)*',
            '## Superseded in part by ADR 0216, 2026-09-13',
            '*(Corrected in place 2026-09-11, per ADR 0016. This note held while `written-before-publish` was a kind.)*',
        )
        dated_footer = '\nSuperseded in part, 2026-09-12: ADR 0187 ruling 14 replaces the floor.\n'
        for original in examples:
            with self.subTest(original=original):
                normalized = population.normalize_legacy_opening(original, original + dated_footer)
                self.assertIsNotNone(normalized)
                self.assertTrue(normalized.endswith(original))
                self.assertRegex(normalized, r'^\*Superseded \d{4}-\d{2}-\d{2}\.\* ')
        self.assertIsNone(population.normalize_legacy_opening('Unrelated 2026-09-12 annotation.', dated_footer))
        self.assertIsNone(population.normalize_legacy_opening(examples[0], examples[0]))

    def test_wrapped_text_citation_stays_in_the_population(self):
        report = population.derive_records([
            ("0001-first.md", b"Original"),
            ("0002-second.md", b"Following ADR\n0001 ruling 5, the rule continues."),
        ])
        self.assertEqual(1, report["distinct_pairs"])
        self.assertEqual(["text"], report["pairs"][0]["forms"])
        self.assertEqual([1], report["pairs"][0]["citation_lines"])

    def test_union_reaches_verb_free_text_and_path_only_reference(self):
        report = fixture()
        self.assertEqual(3, report["records_read"])
        self.assertEqual([], report["unread_remainder"])
        self.assertEqual([("0002", "0001"), ("0003", "0001")], [
            (pair["later"], pair["earlier"]) for pair in report["pairs"]
        ])
        self.assertEqual(["path"], report["pairs"][1]["forms"])

    def test_distinct_pair_ignores_duplicates_self_future_and_absent_record(self):
        report = population.derive_records([
            ("0001-first.md", b"ADR 0002 ADR 0001"),
            ("0002-second.md", b"ADR 0001 ADR 0001 (0001-first.md) ADR 0099\nADR 0001"),
        ])
        self.assertEqual(1, report["distinct_pairs"])
        self.assertEqual(["path", "text"], report["pairs"][0]["forms"])
        self.assertEqual([1, 2], report["pairs"][0]["citation_lines"])

    def test_planted_alternative_form_demonstrates_declared_floor(self):
        report = population.derive_records([
            ("0001-first.md", b"The original ruling."),
            ("0002-second.md", b"ADR #0001 is withdrawn; the first decision is replaced."),
        ])
        self.assertEqual(2, report["records_read"])
        self.assertEqual(0, report["distinct_pairs"])
        self.assertIn("neither ADR NNNN text nor a NNNN- record path", population.DECLARED_LIMITS[0])

    def test_unread_source_and_duplicate_identity_are_not_silently_clean(self):
        report = population.derive_records([
            ("0001-first.md", b"Good"), ("0001-other.md", b"Duplicate"),
            ("0002-second.md", b"\xff"),
            ("0003-third.md", OSError("cannot read")),
        ])
        self.assertEqual(1, report["records_read"])
        self.assertEqual(3, len(report["unread_remainder"]))

    def test_cli_reports_population_and_floor_beside_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "0001-first.md").write_text("Original", encoding="utf-8")
            (root / "0002-second.md").write_text("ADR 0001", encoding="utf-8")
            output = root / "population.json"
            printed = io.StringIO()
            with redirect_stdout(printed):
                status = population.main(["--directory", str(root), "--json", str(output)])
            self.assertEqual(0, status)
            self.assertIn("Records read: 2", printed.getvalue())
            self.assertIn("Distinct pairs: 1", printed.getvalue())
            self.assertIn("Unread remainder: 0", printed.getvalue())
            self.assertIn(population.DECLARED_LIMITS[0], printed.getvalue())
            self.assertEqual(1, json.loads(output.read_text(encoding="utf-8"))["distinct_pairs"])

    def test_missing_revision_exits_unread_without_live_fallback(self):
        import subprocess
        with mock.patch.object(population, "derive_revision", side_effect=subprocess.CalledProcessError(128, "git")), mock.patch.object(population, "derive_population") as live:
            with redirect_stdout(io.StringIO()) as printed:
                status = population.main(["--revision", "a" * 40])
            self.assertEqual(2, status)
            self.assertIn("Unread revision:", printed.getvalue())
            live.assert_not_called()


class ClassificationTests(unittest.TestCase):
    def test_banner_pair_requires_its_disposition_without_a_pair_declaration(self):
        report = population.derive_records([
            ('0001-first.md', b'# First\n\n*Superseded 2099-10-11.* Every ruling in "First" is withdrawn by [ADR 0343](0343-retired.md) ruling 1.\n\n## Decision\n\nOld.\n'),
            ('0002-second.md', b'ADR 0001 was replaced.\n'),
        ])
        reading = classified(report)
        row = reading['pairs'][0]
        row.update(classification='overturned', disposition='adr-0343-banner')
        self.assertEqual([], population.classification_findings(report, reading))
        del row['disposition']
        self.assertTrue(any('no declaration or banner disposition' in finding for finding in population.classification_findings(report, reading)))

    def test_complete_classification_is_digest_bound(self):
        report = fixture()
        self.assertEqual([], population.classification_findings(report, classified(report)))
        changed = population.derive_records([
            ("0001-first.md", b"Changed ruling"),
            ("0002-second.md", b"ADR 0001"), ("0003-third.md", b"ADR 0001"),
        ])
        self.assertTrue(any("digest" in item for item in population.classification_findings(changed, classified(report))))

    def test_missing_duplicate_extra_and_unread_verdict_are_findings(self):
        report = fixture()
        reading = classified(report)
        reading["pairs"] = [reading["pairs"][0], copy.deepcopy(reading["pairs"][0]),
                            {"later": "0009", "earlier": "0001", "classification": "completed", "reason": ""}]
        findings = "\n".join(population.classification_findings(report, reading))
        for phrase in ("missing classification", "duplicate classification", "extra classification", "unread classification", "no reason"):
            self.assertIn(phrase, findings)

    def test_malformed_pair_identity_remains_a_finding_with_banner_metadata(self):
        report = fixture()
        reading = classified(report)
        reading['pairs'][0]['earlier'] = []
        self.assertIn('classification pair IDs must be strings', population.classification_findings(report, reading))

    def test_historical_coverage_has_explicit_boundary_and_does_not_grade_digest(self):
        report = fixture()
        reading = classified(report)
        reading.update(revision="a" * 40, through="0003", records_sha256="historical bytes")
        current = population.derive_records([
            ("0001-first.md", b"Changed by the repair"),
            ("0002-second.md", b"ADR 0001"), ("0003-third.md", b"ADR 0001"),
            ("0004-new.md", b"ADR 0001 ADR 0002"),
        ])
        self.assertEqual([], population.classification_findings(current, reading, historical_coverage=True))
        reading.pop("through")
        self.assertTrue(population.classification_findings(current, reading, historical_coverage=True))

    def test_historical_coverage_refuses_a_new_pair_inside_its_boundary(self):
        report = fixture()
        reading = classified(report)
        reading.update(revision="a" * 40, through="0003")
        current = population.derive_records([
            ("0001-first.md", b"Original"), ("0002-second.md", b"ADR 0001"),
            ("0003-third.md", b"ADR 0001 and ADR 0002"),
        ])
        self.assertIn("missing classification: 0003 -> 0002", population.classification_findings(current, reading, historical_coverage=True))


if __name__ == "__main__":
    unittest.main()
