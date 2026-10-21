"""Synthetic public-command coverage of live drug filing and absorbed pages."""
import contextlib
import io
import json
from datetime import date
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_lock_test_support
import uptodate_store as store
from prose_bind import bind, NAMING
from test_uptodate_store import topic


def drug(*, pediatric=False, folded=False, empty=False):
    title = 'Example: Pediatric drug information' if pediatric else 'Example: Drug information'
    group = 'Pediatric' if pediatric else 'Adult'
    state = 'false' if folded else 'true'
    body = '' if empty else '<p>Oral: 5 mg once daily.</p>'
    return f'<h1>{title}</h1><h2>Dosing: {group}</h2><span class="collapsible-indication-title" aria-expanded="{state}">Example indication</span>{body}<h2>References</h2><p>Example reference.</p><div>Topic 123 Version 4.0</div>'


class DrugCommands(unittest.TestCase):
    def test_damaged_drug_read_date_is_unreadable_not_an_absent_date(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status, output = self.run_ingest(root, drug(), '--drug-page', '--read-on', date.today().isoformat())
            self.assertEqual(status, 0, output)
            path = root / 'store' / 'dumps' / 'sample' / 'manifest.json'
            manifest = json.loads(path.read_text(encoding='utf-8'))
            for changed in ({**manifest, 'read_on': 'not a date'}, {**manifest, 'topics': []},
                            {**manifest, 'source_sha256': 'not a digest'},
                            {**manifest, 'supersedes': {}},
                            {**manifest, 'topics': [{**manifest['topics'][0], 'authors': None}]},
                            {**manifest, 'topics': [{**manifest['topics'][0], 'last_updated': None}]}):
                with self.subTest(changed_fields=changed.keys()):
                    path.write_text(json.dumps(changed), encoding='utf-8')
                    with contextlib.redirect_stderr(io.StringIO()) as error:
                        self.assertEqual(store.main(['--store', str(root / 'store'), 'report']), 2)
                    self.assertIn('unreadable', error.getvalue())

    def test_filing_limits_are_named_at_the_maintainer_pointer(self):
        text = (Path(__file__).resolve().parents[1] / 'CLAUDE.md').read_text(encoding='utf-8')
        self.assertEqual(bind(store.DECLARED_LIMITS, text, mode=NAMING), ())

    def test_report_and_sweep_count_drugs_without_counting_topic_versions_as_drugs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status, output = self.run_ingest(root, drug(), '--drug-page', '--read-on', date(2000, 1, 1).isoformat())
            self.assertEqual(status, 0, output)
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(store.main(['--store', str(root / 'store'), 'report']), 0)
            self.assertIn('drug pages: 1; past one year: 1', output.getvalue())
            scan = root / 'scan'
            scan.mkdir()
            (scan / 'drug.html').write_text(drug(pediatric=True), encoding='utf-8')
            (scan / 'topic.txt').write_text(topic('Example topic') + '\nTopic 101 Version 1.0\n', encoding='utf-8')
            report = store.sweep_unfiled(scan, root / 'store')
            self.assertEqual(report.files, 2)
            self.assertEqual(report.topic_bodies, 2)

    def test_observed_rendered_structure_with_synthetic_text(self):
        # The live title is a div/role heading, not h1. The measured article
        # uses drugH1 h2 headings, nested indication spans and separate body
        # containers; all clinical words below are invented synthetic content.
        html = ('<div id="topic-title" role="heading" aria-level="1">Example: Pediatric drug information</div>'
                '<div id="topicArticle"><h2 class="drugH1">Dosing: Pediatric</h2>'
                '<div><span class="collapsible-indication-title" aria-expanded="true">'
                'Example <i>indication</i></span><div class="collapsible-indication-content">'
                '<p>Oral: 5 mg once daily.</p></div></div>'
                '<h2 class="drugH1">Dosing: Kidney Impairment: Pediatric</h2><p>No adjustment required.</p></div>'
                '<div id="topicVersionRevision">Topic 123 Version 4.0</div>')
        for content, expected in ((html, 0), (html.replace('aria-expanded="true"', 'aria-expanded="false"'), 2),
                                  (html.replace('<p>Oral: 5 mg once daily.</p>', ''), 2)):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                status, output = self.run_ingest(Path(temporary), content, '--drug-page', '--read-on', date.today().isoformat())
                self.assertEqual(status, expected, output)

    def test_shared_brief_keeps_every_required_route(self):
        brief = (Path(__file__).resolve().parents[1] / 'skills/_shared/reference/uptodate-pull.md').read_text(encoding='utf-8')
        for required in ('word for word', '--query-readback', 'every Expand All', 'adult and pediatric',
                         'Open the actual topic or drug page', 'Sign In button', 'signed-out',
                         'service-unavailable', 'no-match', 'page-unreadable', '--page-url',
                         '--sign-in-tried', '--results-read', '--second-method'):
            self.assertIn(required, brief)

    def run_ingest(self, root, content, *extra):
        source = root / 'source.txt'
        source.write_text(content, encoding='utf-8')
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = store.main(['--store', str(root / 'store'), 'ingest', str(source), '--dump-id', 'sample', '--module', 'synthetic', '--received-on', date.today().isoformat(), *extra])
        return status, output.getvalue()

    def test_adult_and_separate_pediatric_sources_search_by_indication(self):
        for pediatric in (False, True):
            with self.subTest(pediatric=pediatric), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                status, output = self.run_ingest(root, drug(pediatric=pediatric), '--drug-page', '--read-on', date.today().isoformat())
                self.assertEqual(status, 0, output)
                hits = store.search(root / 'store', '"Example indication"')
                self.assertEqual(len(hits), 1)
                self.assertEqual(hits[0].section, 'Example indication')
                self.assertIn('5 mg', hits[0].body)
                self.assertEqual(hits[0].version, '4.0')
                self.assertEqual(hits[0].read_on, date.today().isoformat())

    def test_folded_or_empty_adult_and_pediatric_indications_refuse(self):
        for pediatric in (False, True):
            for mutation in ({'folded': True}, {'empty': True}):
                with self.subTest(pediatric=pediatric, mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                    status, _output = self.run_ingest(Path(temporary), drug(pediatric=pediatric, **mutation), '--drug-page', '--read-on', date.today().isoformat())
                    self.assertEqual(status, 2)

    def test_absorbed_drug_signals_refuse_but_quoted_cross_reference_passes(self):
        good = topic('Example topic') + '\nTopic 101 Version 1.0\n'
        for content in (good + 'Topic 102 Version 2.0\n', 'Topic 102 Version 2.0\n' + good,
                        good + 'Example: Drug information\n', good + 'Example: Pediatric drug information\n', good + 'UpToDate Lexidrug\n'):
            with self.subTest(content=content[-40:]), tempfile.TemporaryDirectory() as temporary:
                self.assertEqual(self.run_ingest(Path(temporary), content)[0], 2)
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(self.run_ingest(Path(temporary), good + '(See "Example: Drug information".)\n')[0], 0)

    def test_complete_topics_with_version_lines_remain_topics(self):
        with tempfile.TemporaryDirectory() as temporary:
            content = topic('First') + '\nTopic 101 Version 1.0\n' + topic('Second') + '\nTopic 102 Version 2.0\n'
            status, output = self.run_ingest(Path(temporary), content)
            self.assertEqual(status, 0, output)


if __name__ == '__main__':
    unittest.main()
