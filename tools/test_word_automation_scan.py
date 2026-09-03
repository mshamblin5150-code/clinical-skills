"""The measured Word export methods stay on their ruled invocation route."""

import tempfile
import unittest
from pathlib import Path

import word_automation_scan as scan


class MeasuredWordMethodsUseTypedLateBinding(unittest.TestCase):
    def test_the_declared_object_names_its_methods_and_ceiling(self):
        self.assertEqual(
            ("ExportAsFixedFormat2", "SaveAs2"),
            scan.LATE_BOUND_WORD_METHODS.methods,
        )
        self.assertIn("measured on one machine", scan.LATE_BOUND_WORD_METHODS.ceiling)
        self.assertIn("listed methods", scan.LATE_BOUND_WORD_METHODS.ceiling)

    def test_the_committed_powershell_corpus_is_clean(self):
        self.assertEqual((), scan.survey(Path(scan.__file__).resolve().parent))

    def test_a_dynamic_call_to_a_listed_method_is_a_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "probe.ps1").write_text(
                "$document.SaveAs2($output, 18)\n", encoding="utf-8"
            )

            findings = scan.survey(root)

        self.assertEqual(1, len(findings))
        self.assertEqual("SaveAs2", findings[0].method)
        self.assertEqual("probe.ps1", findings[0].path)

    def test_typed_invoke_member_is_not_a_dynamic_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "probe.ps1").write_text(
                '[void]$document.GetType().InvokeMember("SaveAs2", '
                "[Reflection.BindingFlags]::InvokeMethod, $null, $document, "
                "[object[]]@([string]$output, [int32]18))\n",
                encoding="utf-8",
            )

            self.assertEqual((), scan.survey(root))


if __name__ == "__main__":
    unittest.main()
