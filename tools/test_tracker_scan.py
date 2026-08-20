"""``tracker_scan`` reads the surface a public flip publishes and files do not.

[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212).
Synthetic harvest files and throwaway checkouts in a temp directory, on
``test_skills_mirror.py``'s arrangement -- **the real tracker is not a fixture**.
Its text is fetched over the network, it changes every time anybody comments,
and the surface figures three separate sweeps published on #212 disagree with
each other for exactly that reason. A test keyed on it would be measuring the
day it ran, so **no count of issues, pull requests or blobs is asserted here**.

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


def scan(*texts, is_file=False):
    records = [
        tracker_scan.Record("body", f"r{n}", t, is_file) for n, t in enumerate(texts)
    ]
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


class ARecordCannotExemptItselfAndAFileCan(unittest.TestCase):
    """The pragma is a **file**'s to declare, and a ticket is not a file.

    This is the whole reason `phi_scan.scan_lines` was split out of
    `phi_scan.scan_text`. A ticket about the ``dob`` shape quotes a ``dob``, and
    a ticket about the pragma quotes the pragma -- so reading the exemption out
    of the text being scanned lets the record most likely to carry a real
    identifier be the one that turns the detector off.

    A blob is the other case and takes the opposite answer: it **was** a file,
    reviewed as one, so ``--history`` honours what it declares.
    """

    PRAGMA_AND_A_SHAPE = f"{phi_scan.SYNTHETIC_PRAGMA}\n\nseen dob 3-04-88\n"

    def test_the_pragma_alone_on_a_line_does_not_silence_a_record(self):
        rules = {f.rule for f in scan(self.PRAGMA_AND_A_SHAPE)}
        self.assertIn("dob-with-date", rules)

    def test_the_same_text_in_a_blob_is_exempt_because_a_blob_is_a_file(self):
        rules = {f.rule for f in scan(self.PRAGMA_AND_A_SHAPE, is_file=True)}
        self.assertNotIn("dob-with-date", rules)

    def test_the_two_paths_agree_with_phi_scan_about_which_is_which(self):
        self.assertTrue(phi_scan.declares_synthetic(self.PRAGMA_AND_A_SHAPE))
        rules = {
            f.rule
            for f in phi_scan.scan_text(self.PRAGMA_AND_A_SHAPE, "a.py", index())
        }
        self.assertNotIn("dob-with-date", rules)

    def test_the_corpus_layer_runs_on_a_record_either_way(self):
        text = f"{phi_scan.SYNTHETIC_PRAGMA}\n\n{NAME} was seen {DATE}\n"
        for is_file in (False, True):
            rules = {f.rule for f in scan(text, is_file=is_file)}
            self.assertLessEqual({"corpus-name", "corpus-date"}, rules)


class TheReportCountsAndDoesNotReveal(unittest.TestCase):

    def records(self):
        return [tracker_scan.Record("body", "r0", f"{NAME} was seen")]

    def test_the_default_report_carries_no_match_text(self):
        findings = scan(f"{NAME} was seen")
        report = tracker_scan.format_report(findings, self.records(), [], [], False)
        self.assertNotIn(NAME, report)
        self.assertIn("corpus-name", report)
        self.assertIn("--show", report)

    def test_show_reveals_and_says_which_record(self):
        findings = scan(f"{NAME} was seen")
        report = tracker_scan.format_report(findings, self.records(), [], [], True)
        self.assertIn(NAME, report)
        self.assertIn("r0", report)

    def test_a_clean_report_says_so_and_counts_by_kind(self):
        records = [
            tracker_scan.Record("body", "a", "x"),
            tracker_scan.Record("commit", "b", "y"),
        ]
        report = tracker_scan.format_report([], records, [], [], False)
        self.assertIn("no finding", report)
        self.assertIn("body records", report)
        self.assertIn("commit records", report)


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

    def configure_pull_refspec(self):
        self._run(
            "config", "--add", "remote.origin.fetch",
            "+refs/pull/*/head:refs/remotes/origin/pr/*",
        )


class ATempRepo(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "checkout"
        self.repo.mkdir()
        self.checkout = GitCheckout(self.repo)
        self.addCleanup(self.tmp.cleanup)


class TheGitLimbsReadWhatWasPublished(ATempRepo):

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
        paths = [r.text for r in tracker_scan.path_records(self.repo)]
        self.assertIn("notes/one.md", paths)

    def test_a_pull_head_ref_is_recognized_by_either_spelling(self):
        self.checkout.commit("a.md", "x", "one")
        self.assertEqual(tracker_scan.pull_head_refs(self.repo), [])
        self.checkout.make_pull_ref()
        self.assertTrue(tracker_scan.pull_head_refs(self.repo))

    def test_a_git_failure_is_an_error_and_not_an_empty_answer(self):
        """The dead-corpus distinction one tool over.

        ``for-each-ref`` returning nothing because it failed reads exactly like
        a repository nobody has fetched the pull heads into, and that difference
        decides whether the banner says *fetch them* or *something is wrong*.
        """
        with self.assertRaises(tracker_scan.GitError):
            tracker_scan.pull_head_refs(Path(self.tmp.name) / "not-a-repo")


class TheHistoryLimbIsThePullRequestLimb(ATempRepo):
    """A merged pull request's diff is blobs, and `phi_scan` reads none of them.

    ``git ls-files`` is the tip. A file deleted three commits ago is published
    and unreadable to every other checker here, which is why #212's own scan had
    to be written by hand and why the figures it published were re-derivable by
    nothing.
    """

    def test_a_blob_deleted_from_the_tip_is_still_read(self):
        self.checkout.commit("gone.md", f"{NAME} was here", "add")
        self.checkout._run("rm", "-q", "gone.md")
        self.checkout._run("commit", "-q", "-m", "remove")
        texts = " ".join(r.text for r in tracker_scan.blob_records(self.repo))
        self.assertIn(NAME, texts)

    def test_a_blob_record_is_a_file_so_it_may_declare_the_pragma(self):
        self.checkout.commit(
            "t.py", f"{phi_scan.SYNTHETIC_PRAGMA}\ndob 3-04-88\n", "add"
        )
        records = tracker_scan.blob_records(self.repo)
        self.assertTrue(records)
        self.assertTrue(all(r.is_file for r in records))
        rules = {f.rule for f in tracker_scan.scan_records(records, index())}
        self.assertNotIn("dob-with-date", rules)

    def test_a_binary_blob_is_skipped_rather_than_decoded(self):
        (self.repo / "b.bin").write_bytes(b"\x00\x01binary")
        self.checkout._run("add", "b.bin")
        self.checkout._run("commit", "-q", "-m", "binary")
        refs = [r.ref for r in tracker_scan.blob_records(self.repo)]
        self.assertFalse(any("b.bin" in ref for ref in refs))

    def test_an_unreachable_blob_is_counted_and_never_read(self):
        """The count is what makes the refusal to read them legible."""
        self.checkout.commit("a.md", "kept", "first")
        self.checkout.commit("a.md", f"{NAME} was here", "second")
        self.checkout._run("reset", "-q", "--hard", "HEAD~1")
        reachable, outside = tracker_scan.blob_counts(self.repo)
        self.assertGreaterEqual(outside, 1)
        self.assertGreaterEqual(reachable, 1)
        texts = " ".join(r.text for r in tracker_scan.blob_records(self.repo))
        self.assertNotIn(NAME, texts)


class MainInATempRepo(ATempRepo):
    """Every limb driven through ``main``, with the real repo root swapped out."""

    def setUp(self):
        super().setUp()
        self.checkout.commit("a.md", "x", "an ordinary message")
        self._root = phi_scan.REPO_ROOT
        self._missing = phi_scan.missing_corpus_sources
        self._identifiers = phi_scan.corpus_identifiers
        phi_scan.REPO_ROOT = self.repo
        phi_scan.missing_corpus_sources = lambda: []
        phi_scan.corpus_identifiers = lambda: ({NAME}, {DATE})
        self.addCleanup(self._restore)

    def _restore(self):
        phi_scan.REPO_ROOT = self._root
        phi_scan.missing_corpus_sources = self._missing
        phi_scan.corpus_identifiers = self._identifiers

    def harvest(self, name, payload):
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def run_main(self, *argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = tracker_scan.main(list(argv))
        return status, buffer.getvalue()


class ExitStatusSaysWhichOfThreeThingsHappened(MainInATempRepo):
    """0 clean, 1 found, 2 did not scan."""

    def test_naming_no_surface_is_not_a_clean_scan(self):
        self.assertEqual(self.run_main()[0], tracker_scan.NOT_SCANNED)

    def test_a_missing_harvest_file_is_not_a_clean_scan(self):
        gone = str(Path(self.tmp.name) / "gone.json")
        self.assertEqual(self.run_main("--harvest", gone)[0],
                         tracker_scan.NOT_SCANNED)

    def test_a_harvest_file_that_is_not_a_list_is_not_a_clean_scan(self):
        path = self.harvest("bad.json", {"message": "Bad credentials"})
        self.assertEqual(self.run_main("--harvest", path)[0],
                         tracker_scan.NOT_SCANNED)

    def test_a_harvest_of_nothing_is_not_a_clean_scan(self):
        path = self.harvest("empty.json", [])
        self.assertEqual(self.run_main("--harvest", path)[0],
                         tracker_scan.NOT_SCANNED)

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
        self.assertNotIn(NAME, self.run_main("--harvest", path)[1])


class TheGitSurfaceRefusesUntilPullHeadsArePersistentAndPresent(MainInATempRepo):
    """A scan of half the published objects is not a clean scan.

    A pull request whose branch was deleted after merging keeps its head at
    ``refs/pull/N/head`` on GitHub and an ordinary clone does not fetch it, so a
    run without them is the silent partial coverage this directory exists to
    refuse. A one-off fetch is not enough: its refs may be stale and an ordinary
    prune removes them. **How many merged pull requests this repository has is
    deliberately not stated** -- it moved three times during the session that
    wrote this.
    """

    def test_no_pull_head_ref_is_not_a_clean_scan(self):
        status, out = self.run_main("--commits")
        self.assertEqual(status, tracker_scan.NOT_SCANNED)
        self.assertIn("DID NOT SCAN", out)
        self.assertIn("refs/pull", out)

    def test_it_gates_the_history_limb_too(self):
        self.assertEqual(self.run_main("--history")[0], tracker_scan.NOT_SCANNED)

    def test_a_pull_head_ref_without_the_persistent_refspec_is_not_clean(self):
        self.checkout.make_pull_ref()
        status, out = self.run_main("--commits")
        self.assertEqual(status, tracker_scan.NOT_SCANNED)
        self.assertIn("remote.origin.fetch", out)

    def test_no_pull_refs_cannot_acknowledge_refs_that_are_present(self):
        self.checkout.make_pull_ref()
        status, out = self.run_main("--commits", "--no-pull-refs")
        self.assertEqual(status, tracker_scan.NOT_SCANNED)
        self.assertIn("remote.origin.fetch", out)
        self.assertNotIn("--no-pull-refs", out)

    def test_a_persistent_refspec_and_pull_head_ref_let_it_scan(self):
        self.checkout.configure_pull_refspec()
        self.checkout.make_pull_ref()
        status, out = self.run_main("--commits")
        self.assertEqual(status, tracker_scan.CLEAN)
        self.assertIn("commit records", out)

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

    def test_the_history_limb_prints_what_it_did_not_read(self):
        self.checkout.configure_pull_refspec()
        self.checkout.make_pull_ref()
        _, out = self.run_main("--history")
        self.assertIn("blobs never pushed, unread", out)


class ADeadCorpusDoesNotSuppressAFinding(MainInATempRepo):
    """`phi_scan.main`'s ordering, and the first version of this got it backwards.

    A corpus that is not on disk kills the corpus layer and leaves the shape
    layer working. Returning *did not scan* before scanning threw away a real
    ``dob`` hit and reported the strongest thing known about the surface under
    the weakest heading -- and **this file's own stub of
    ``missing_corpus_sources`` is what hid it**, so the stub is lifted here
    rather than left set everywhere. Found by review, not by the suite.
    """

    def setUp(self):
        super().setUp()
        phi_scan.missing_corpus_sources = lambda: ["name-index.json"]
        phi_scan.corpus_identifiers = lambda: (set(), set())
        self._allows = phi_scan.allows_no_corpus
        phi_scan.allows_no_corpus = (
            lambda argv: phi_scan.ALLOW_NO_CORPUS_FLAG in argv
        )
        self.addCleanup(lambda: setattr(phi_scan, "allows_no_corpus", self._allows))

    def a_shape_hit(self):
        return self.harvest(
            "hit.json", [{"number": 9, "title": "t", "body": "seen dob 3-04-88"}]
        )

    def test_a_shape_finding_still_exits_one(self):
        status, out = self.run_main("--harvest", self.a_shape_hit())
        self.assertEqual(status, tracker_scan.FOUND)
        self.assertIn("dob-with-date", out)

    def test_the_banner_prints_beside_the_finding(self):
        _, out = self.run_main("--harvest", self.a_shape_hit())
        self.assertIn("CORPUS LAYER DID NOT RUN", out.upper())

    def test_no_finding_and_no_corpus_is_not_a_clean_scan(self):
        path = self.harvest("ok.json", [{"number": 1, "body": "nothing here"}])
        self.assertEqual(self.run_main("--harvest", path)[0],
                         tracker_scan.NOT_SCANNED)

    def test_the_acknowledgment_converts_that_status_and_buys_no_silence(self):
        path = self.harvest("ok.json", [{"number": 1, "body": "nothing here"}])
        status, out = self.run_main("--harvest", path,
                                    phi_scan.ALLOW_NO_CORPUS_FLAG)
        self.assertEqual(status, tracker_scan.CLEAN)
        self.assertIn("CORPUS LAYER DID NOT RUN", out.upper())


class TheModuleTakesTheDirectorysStandingRules(unittest.TestCase):

    def test_it_puts_the_console_on_utf8_from_main(self):
        source = Path(tracker_scan.__file__).read_text(encoding="utf-8")
        self.assertIn("from console_codec import use_utf8", source)
        self.assertIn("use_utf8()", source)

    def test_it_names_show_output_as_phi(self):
        self.assertIn("--show`` output is PHI", tracker_scan.__doc__)

    def test_it_tells_you_to_write_the_harvest_where_the_firewall_is(self):
        """The harvest is the tracker's whole text, so it is PHI on arrival."""
        self.assertIn("scratch/", tracker_scan.__doc__)


if __name__ == "__main__":
    unittest.main()
