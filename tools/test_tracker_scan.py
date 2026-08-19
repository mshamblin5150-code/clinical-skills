"""``tracker_scan`` reads the surface a public flip publishes and files do not.

[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212).
Synthetic harvest files and throwaway checkouts in a temp directory, on
``test_skills_mirror.py``'s arrangement -- **the real tracker is not a fixture**.
Its text is fetched over the network, it changes every time anybody comments,
and the figures three separate sweeps published on #212 moved between them; a
test keyed on it would be measuring the day it ran.

The corpus index is synthetic too, built from `phi_scan.build_index` with names
and dates invented here, so nothing in this file reads ``scratch/``.

phi-scan: synthetic

Testing a scanner whose whole subject is date- and name-shaped text requires
date- and name-shaped literals, so this file takes the shape layer's one
sanctioned door on ``test_corpus_census.py``'s terms. **It exempts the shape
rules only** -- every literal below is invented, and a real corpus name or date
would still be refused here. Which is the same asymmetry
`tracker_scan.scan_records` refuses to let a *record* have, one layer up.
"""

from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import phi_scan
import tracker_scan


NAME = "Quilliam Threadgold"
DATE = "9-9-99"


def index():
    return phi_scan.build_index({NAME}, {DATE})


def scan(*texts):
    records = [tracker_scan.Record("body", f"r{n}", t) for n, t in enumerate(texts)]
    return tracker_scan.scan_records(records, index())


class OneCodePathReadsIssuesPullRequestsAndComments(unittest.TestCase):
    """The three payload shapes differ only in which keys are present."""

    def test_an_issue_yields_a_title_record_and_a_body_record(self):
        records = tracker_scan.records_from_github(
            [{"number": 212, "html_url": "https://x/issues/212",
              "title": "going public", "body": "the body"}],
            "issues.json",
        )
        self.assertEqual([r.kind for r in records], ["title", "body"])
        self.assertEqual([r.text for r in records], ["going public", "the body"])

    def test_a_comment_has_no_title_and_yields_one_record(self):
        records = tracker_scan.records_from_github(
            [{"id": 5256998963, "html_url": "https://x/issues/9#c-1",
              "body": "a comment"}],
            "comments.json",
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].kind, "body")

    def test_the_label_is_the_url_a_reader_can_open(self):
        records = tracker_scan.records_from_github(
            [{"id": 7, "html_url": "https://x/issues/9#c-1", "body": "b"}],
            "comments.json",
        )
        self.assertIn("https://x/issues/9#c-1", records[0].ref)

    def test_a_payload_with_no_url_falls_back_to_the_number(self):
        records = tracker_scan.records_from_github(
            [{"number": 41, "body": "b"}], "issues.json"
        )
        self.assertIn("41", records[0].ref)

    def test_an_empty_body_contributes_no_record(self):
        records = tracker_scan.records_from_github(
            [{"number": 1, "title": "t", "body": ""},
             {"number": 2, "title": "t2", "body": None}],
            "issues.json",
        )
        self.assertEqual([r.kind for r in records], ["title", "title"])

    def test_a_payload_that_is_not_a_list_is_a_harvest_error(self):
        with self.assertRaises(tracker_scan.HarvestError):
            tracker_scan.records_from_github({"message": "Not Found"}, "x.json")


class ARecordCannotExemptItself(unittest.TestCase):
    """The pragma is a **file**'s to declare, and a ticket is not a file.

    This is the whole reason `phi_scan.scan_lines` was split out of
    `phi_scan.scan_text`. A ticket about the ``dob`` shape quotes a ``dob``, and
    a ticket about the pragma quotes the pragma -- so reading the exemption out
    of the text being scanned lets the ticket most likely to carry a real
    identifier be the one that turns the detector off.
    """

    def test_the_pragma_alone_on_a_line_does_not_silence_the_shape_layer(self):
        text = f"{phi_scan.SYNTHETIC_PRAGMA}\n\nseen dob 3-04-88 on the form\n"
        rules = {f.rule for f in scan(text)}
        self.assertIn("dob-with-date", rules)

    def test_the_same_text_in_a_file_would_have_been_exempt(self):
        text = f"{phi_scan.SYNTHETIC_PRAGMA}\n\nseen dob 3-04-88 on the form\n"
        self.assertTrue(phi_scan.declares_synthetic(text))
        rules = {f.rule for f in phi_scan.scan_text(text, "a-file.py", index())}
        self.assertNotIn("dob-with-date", rules)

    def test_the_corpus_layer_runs_on_a_record_either_way(self):
        text = f"{phi_scan.SYNTHETIC_PRAGMA}\n\n{NAME} was seen {DATE}\n"
        rules = {f.rule for f in scan(text)}
        self.assertLessEqual({"corpus-name", "corpus-date"}, rules)


class TheReportCountsAndDoesNotReveal(unittest.TestCase):

    def test_the_default_report_carries_no_match_text(self):
        findings = scan(f"{NAME} was seen")
        report = tracker_scan.format_report(findings, [], [], show=False)
        self.assertNotIn(NAME, report)
        self.assertIn("corpus-name", report)
        self.assertIn("--show", report)

    def test_show_reveals_and_says_which_record(self):
        findings = scan(f"{NAME} was seen")
        report = tracker_scan.format_report(findings, [], [], show=True)
        self.assertIn(NAME, report)
        self.assertIn("r0", report)

    def test_a_clean_report_says_so(self):
        report = tracker_scan.format_report([], [("tracker records", 3)], [], False)
        self.assertIn("no finding", report)
        self.assertIn("3", report)


class GitCheckout:
    """A throwaway repository, on ``test_skills_mirror.py``'s arrangement."""

    def __init__(self, root: Path):
        self.root = root
        self._run("init", "-q", "-b", "main")
        self._run("config", "user.email", "t@example.com")
        self._run("config", "user.name", "T")
        self._run("config", "commit.gpgsign", "false")

    def _run(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )

    def commit(self, path: str, text: str, message: str):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        self._run("add", path)
        self._run("commit", "-q", "-m", message)

    def make_pull_ref(self):
        head = self._run("rev-parse", "HEAD").stdout.strip()
        self._run("update-ref", "refs/remotes/origin/pr/1", head)


class TheGitLimbsReadWhatWasPublished(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "checkout"
        self.repo.mkdir()
        self.checkout = GitCheckout(self.repo)
        self.addCleanup(self.tmp.cleanup)

    def test_a_commit_message_is_a_record(self):
        self.checkout.commit("a.md", "x", f"seen {NAME} on the ward")
        records = tracker_scan.commit_records(self.repo)
        self.assertEqual(len(records), 1)
        self.assertIn(NAME, records[0].text)

    def test_an_unreachable_commit_message_is_not_a_record(self):
        """Never pushed, so making the repository public does not publish it."""
        self.checkout.commit("a.md", "x", "first")
        self.checkout.commit("a.md", "y", f"amended over {NAME}")
        self.checkout._run("reset", "-q", "--hard", "HEAD~1")
        texts = " ".join(r.text for r in tracker_scan.commit_records(self.repo))
        self.assertNotIn(NAME, texts)

    def test_every_path_ever_committed_is_read_including_deleted_ones(self):
        self.checkout.commit("notes/one.md", "x", "one")
        self.checkout._run("rm", "-q", "notes/one.md")
        self.checkout._run("commit", "-q", "-m", "removed")
        record = tracker_scan.path_records(self.repo)[0]
        self.assertIn("notes/one.md", record.text.splitlines())

    def test_a_pull_head_ref_is_recognised_by_either_spelling(self):
        self.checkout.commit("a.md", "x", "one")
        self.assertEqual(tracker_scan.pull_head_refs(self.repo), [])
        self.checkout.make_pull_ref()
        self.assertTrue(tracker_scan.pull_head_refs(self.repo))


class ExitStatusSaysWhichOfThreeThingsHappened(unittest.TestCase):
    """0 clean, 1 found, 2 did not scan -- and 1 wins over 2."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self._corpus_missing = phi_scan.missing_corpus_sources
        self._identifiers = phi_scan.corpus_identifiers
        phi_scan.missing_corpus_sources = lambda: []
        phi_scan.corpus_identifiers = lambda: ({NAME}, {DATE})
        self.addCleanup(self._restore)

    def _restore(self):
        phi_scan.missing_corpus_sources = self._corpus_missing
        phi_scan.corpus_identifiers = self._identifiers

    def harvest(self, name, payload):
        path = self.dir / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def run_main(self, *argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = tracker_scan.main(list(argv))
        return status, buffer.getvalue()

    def test_naming_no_surface_is_not_a_clean_scan(self):
        status, _ = self.run_main()
        self.assertEqual(status, tracker_scan.NOT_SCANNED)

    def test_a_missing_harvest_file_is_not_a_clean_scan(self):
        status, _ = self.run_main("--harvest", str(self.dir / "gone.json"))
        self.assertEqual(status, tracker_scan.NOT_SCANNED)

    def test_a_harvest_file_that_is_not_a_list_is_not_a_clean_scan(self):
        path = self.harvest("bad.json", {"message": "Bad credentials"})
        status, _ = self.run_main("--harvest", path)
        self.assertEqual(status, tracker_scan.NOT_SCANNED)

    def test_a_harvest_of_nothing_is_not_a_clean_scan(self):
        path = self.harvest("empty.json", [])
        status, _ = self.run_main("--harvest", path)
        self.assertEqual(status, tracker_scan.NOT_SCANNED)

    def test_a_clean_harvest_exits_zero(self):
        path = self.harvest(
            "ok.json", [{"number": 1, "title": "a title", "body": "no identifier"}]
        )
        status, out = self.run_main("--harvest", path)
        self.assertEqual(status, tracker_scan.CLEAN)
        self.assertIn("no finding", out)

    def test_a_finding_exits_one(self):
        path = self.harvest(
            "hit.json", [{"number": 9, "title": "t", "body": f"dob {DATE}"}]
        )
        status, out = self.run_main("--harvest", path)
        self.assertEqual(status, tracker_scan.FOUND)
        self.assertIn("corpus-date", out)

    def test_the_default_run_prints_no_match_text(self):
        path = self.harvest(
            "hit.json", [{"number": 9, "title": "t", "body": f"{NAME} seen"}]
        )
        _, out = self.run_main("--harvest", path)
        self.assertNotIn(NAME, out)


class TheCommitLimbRefusesUntilThePullHeadsArePresent(unittest.TestCase):
    """A scan of half the published commits is not a clean scan.

    A pull request whose branch was deleted after merging keeps its head at
    ``refs/pull/N/head`` on GitHub and an ordinary clone does not fetch it. This
    repository has 90 merged pull requests, so a ``--commits`` run without them
    is the *silent partial coverage* shape the whole directory exists to refuse.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "checkout"
        self.repo.mkdir()
        self.checkout = GitCheckout(self.repo)
        self.checkout.commit("a.md", "x", "an ordinary message")
        self.addCleanup(self.tmp.cleanup)

        self._root = phi_scan.REPO_ROOT
        self._corpus_missing = phi_scan.missing_corpus_sources
        self._identifiers = phi_scan.corpus_identifiers
        phi_scan.REPO_ROOT = self.repo
        phi_scan.missing_corpus_sources = lambda: []
        phi_scan.corpus_identifiers = lambda: ({NAME}, {DATE})
        self.addCleanup(self._restore)

    def _restore(self):
        phi_scan.REPO_ROOT = self._root
        phi_scan.missing_corpus_sources = self._corpus_missing
        phi_scan.corpus_identifiers = self._identifiers

    def run_main(self, *argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = tracker_scan.main(list(argv))
        return status, buffer.getvalue()

    def test_no_pull_head_ref_is_not_a_clean_scan(self):
        status, out = self.run_main("--commits")
        self.assertEqual(status, tracker_scan.NOT_SCANNED)
        self.assertIn("DID NOT SCAN", out)
        self.assertIn("refs/pull", out)

    def test_a_pull_head_ref_lets_it_scan(self):
        self.checkout.make_pull_ref()
        status, out = self.run_main("--commits")
        self.assertEqual(status, tracker_scan.CLEAN)
        self.assertIn("commit messages", out)

    def test_the_acknowledgment_converts_the_status_and_still_prints(self):
        status, out = self.run_main("--commits", "--no-pull-refs")
        self.assertEqual(status, tracker_scan.CLEAN)
        self.assertIn("NOT in this run", out)

    def test_a_finding_beats_an_unscanned_limb_and_the_banner_still_prints(self):
        self.checkout.commit("b.md", "y", f"{NAME} was on the list")
        status, out = self.run_main("--commits", "--no-pull-refs")
        self.assertEqual(status, tracker_scan.FOUND)
        self.assertIn("corpus-name", out)
        self.assertIn("NOT in this run", out)


class TheModuleTakesTheDirectorysStandingRules(unittest.TestCase):

    def test_it_puts_the_console_on_utf8_from_main(self):
        source = Path(tracker_scan.__file__).read_text(encoding="utf-8")
        self.assertIn("from console_codec import use_utf8", source)
        self.assertIn("use_utf8()", source)

    def test_it_names_show_output_as_phi(self):
        self.assertIn("--show`` output is PHI", tracker_scan.__doc__)


if __name__ == "__main__":
    unittest.main()
