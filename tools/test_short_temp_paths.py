"""Filesystem refusal fixtures keep their meaning under Windows temp aliases."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tree_walk_test_support import short_alias


@unittest.skipUnless(os.name == "nt", "Windows short temp paths")
class ShortTempPathRefusals(unittest.TestCase):
    def test_consumers_refuse_the_same_faults_under_both_temp_spellings(self):
        tests = (
            "test_run_status_stop_hook.RunStatusContract.test_unreadable_subdirectory_requires_a_status_line",
            "test_run_status_stop_hook.RunStatusContract.test_failed_file_stat_requires_a_status_line",
            "test_tracker_publish_hook.ACommandFilePregradeMatchesTheHook.test_unread_run_material_denies_command_without_revealing_names",
            "test_uptodate_store.SweepWalkBoundary.test_unreadable_subdirectory_refuses_and_zero_links_print",
            "test_guidelines_walks.CorpusWalkTests.test_manifest_never_reads_a_document_through_a_linked_society",
            "test_guidelines_walks.CorpusWalkTests.test_public_refusers_exit_two_for_an_unlisted_society",
            "test_guidelines_walks.CorpusWalkTests.test_public_refusers_exit_two_for_native_directory_denial",
        )
        with tempfile.TemporaryDirectory(prefix="clinical skills temp alias ") as temporary:
            long_root = Path(temporary).resolve()
            alias = short_alias(long_root)
            self.assertEqual(alias.resolve(), long_root)
            for root in (long_root, alias):
                with self.subTest(temp=root):
                    # A fresh interpreter makes tempfile read TEMP/TMP afresh.
                    result = subprocess.run(
                        [sys.executable, "-m", "unittest", *tests],
                        cwd=Path(__file__).resolve().parent,
                        env={**os.environ, "TEMP": str(root), "TMP": str(root)},
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    if "skipped=" in result.stderr:
                        self.skipTest("consumer probe has incomplete platform coverage:\n" + result.stderr)
