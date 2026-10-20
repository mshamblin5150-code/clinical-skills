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
            "test_tool_record_aar.ToolWrittenAarRecords.test_unopenable_existing_records_have_the_same_public_failure",
            "test_tool_record_context.ToolRecords.test_context_writer_reports_shared_open_failure_before_parsing",
            "test_record_writer_commands.NativeWriterTransactions.test_opener_directory_failure_is_safe_and_preserves_prior_record",
            "test_record_writer_commands.NativeWriterTransactions.test_opener_record_and_answer_commands_share_the_transaction",
            "test_record_writer_commands.NativeWriterTransactions.test_signer_command_retains_history_bar_and_copies_after_both_refusals",
            "test_record_writer_commands.NativeWriterTransactions.test_signer_native_copy_failure_and_collision_are_safe_and_preserve_prior_evidence",
            "test_tool_record_writers_aar.WriterTransactions.test_each_native_aar_writer_refuses_held_and_interrupted_record_publication",
            "test_tool_record_writers_aar.WriterTransactions.test_extract_directory_failure_is_safe_and_preserves_prior_round",
            "test_tool_record_writers_aar.WriterTransactions.test_native_rebuild_sanitizes_archive_publication_failure",
            "test_tool_record_writers_approval.ApprovalFamilyWriters.test_pre_replace_failure_keeps_every_native_record_and_removes_partial",
            "test_tool_record_writers_approval.ApprovalFamilyWriters.test_prepare_directory_failure_is_classified_and_preserves_receipt",
            "test_tool_record_writers_context.ContextWriters.test_machine_directory_failures_are_safe_and_preserve_evidence",
            "test_bar_signatures.SharedBarSigning.test_native_success_keeps_another_creators_reused_temporary_name",
            "test_bar_signatures.SharedBarSigning.test_shared_signer_native_refusals_preserve_each_new_skill_history",
            "test_approval_record.ApprovalRecordContract.test_note_approval_checks_every_source_before_recording",
            "test_filled_vitals_census.EveryBehaviorLimitHasALiveControl",
            "test_visit_times.PublicCommands",
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
