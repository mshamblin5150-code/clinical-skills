"""Public-command tests for the threshold-subject evidence ledger."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "subject_ledger.py"


def coverage(first: str = "?", second: str = "?", third: str = "?") -> str:
    return f"""# Threshold-sheet coverage

<!-- schema: threshold-coverage/3 -->

| topic | subject | state | artifact | record |
| --- | --- | --- | --- | --- |
| cervical cancer | {first} | unread |  | pending |
| high blood pressure | {second} | unread |  | pending |
| hypertension screening | {third} | unread |  | pending |
"""


EMPTY_LEDGER = """# Threshold-sheet subject ledger

<!-- schema: threshold-subjects/1 -->

No subject records have been authored. A `?` in the coverage registry is unruled.
"""


def record(members: tuple[str, ...] = ("high blood pressure", "hypertension screening")) -> str:
    member_rows = "\n".join(f"- {member}" for member in members)
    evidence_rows = "\n".join(
        f"- {member}: the guideline's scope and recommendations address this clinical subject"
        for member in members
    )
    return f"""# Threshold-sheet subject ledger

<!-- schema: threshold-subjects/1 -->

## SUBJECT: high blood pressure
DATE: 2026-09-01
ELECTED: high blood pressure
ELECTION: this catalog wording is the clearest member name
REFUTATION: the independent refuting pass found no population or scope distinction that defeats the merge

### MEMBERS
{member_rows}

### EVIDENCE
{evidence_rows}
"""


class SubjectLedgerCli(unittest.TestCase):
    def run_cli(self, coverage_text: str, ledger_text: str | None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            coverage_path = root / "coverage.md"
            ledger_path = root / "subjects.md"
            coverage_path.write_text(coverage_text, encoding="utf-8")
            if ledger_text is not None:
                ledger_path.write_text(ledger_text, encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--coverage",
                    str(coverage_path),
                    "--ledger",
                    str(ledger_path),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

    def test_empty_ledger_is_clean_when_the_column_has_no_multi_member_group(self):
        result = self.run_cli(coverage(), EMPTY_LEDGER)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "records      0\nruled cells  0 / 3\n")

    def test_a_fenced_record_shape_is_documentation_not_a_record(self):
        documented = EMPTY_LEDGER + """

```markdown
## SUBJECT: example
DATE: <YYYY-MM-DD>
```
"""
        result = self.run_cli(coverage(), documented)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "records      0\nruled cells  0 / 3\n")

    def test_missing_file_is_not_a_scan(self):
        result = self.run_cli(coverage(), None)

        self.assertEqual(result.returncode, 2)
        self.assertIn("subjects.md", result.stderr)

    def test_multi_member_group_requires_one_matching_record(self):
        grouped = coverage("?", "high blood pressure", "high blood pressure")
        missing = self.run_cli(grouped, EMPTY_LEDGER)
        complete = self.run_cli(grouped, record())

        self.assertEqual(missing.returncode, 1)
        self.assertIn("missing record for subject 'high blood pressure'", missing.stderr)
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertEqual(complete.stdout, "records      1\nruled cells  2 / 3\n")

    def test_record_members_must_equal_the_column_group(self):
        result = self.run_cli(
            coverage("?", "high blood pressure", "high blood pressure"),
            record(("high blood pressure",)),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("members disagree with coverage.md", result.stderr)

    def test_record_shape_requires_date_election_refutation_and_member_evidence(self):
        malformed = record().replace("DATE: 2026-09-01\n", "").replace(
            "- hypertension screening: the guideline's scope and recommendations address this clinical subject",
            "",
        )
        result = self.run_cli(
            coverage("?", "high blood pressure", "high blood pressure"), malformed
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("has no DATE", result.stderr)
        self.assertIn("has no evidence for member 'hypertension screening'", result.stderr)

    def test_one_cell_can_belong_to_two_subjects(self):
        ledger = record() + """

## SUBJECT: hypertension screening
DATE: 2026-09-01
ELECTED: hypertension screening
ELECTION: this catalog wording distinguishes the screening group
REFUTATION: the independent refuting pass found the overlap is not transitive

### MEMBERS
- cervical cancer
- hypertension screening

### EVIDENCE
- cervical cancer: the guideline comparison supports this synthetic overlap
- hypertension screening: the guideline comparison supports this synthetic overlap
"""
        result = self.run_cli(
            coverage(
                "hypertension screening",
                "high blood pressure",
                "high blood pressure, hypertension screening",
            ),
            ledger,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "records      2\nruled cells  3 / 3\n")


if __name__ == "__main__":
    unittest.main()
