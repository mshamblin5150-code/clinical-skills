"""Cover the Code-set database reader check and its digest-pin support."""

from __future__ import annotations

import hashlib
import io
import tempfile
import unittest
from pathlib import Path

import code_set_database_reader_check as check
from code_set_database_test_support import assert_code_set_database_digest


class ACodeSetDatabaseDigestPin(unittest.TestCase):
    def test_matching_bytes_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "codes.sqlite"
            database.write_bytes(b"committed reference bytes")

            assert_code_set_database_digest(
                database,
                hashlib.sha256(database.read_bytes()).hexdigest(),
                "example Code-set database",
            )

    def test_moved_bytes_name_the_database_and_the_required_re_derivation(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "codes.sqlite"
            database.write_bytes(b"rebuilt reference bytes")

            with self.assertRaisesRegex(
                AssertionError,
                "example Code-set database was rebuilt.*hand-typed expectations.*constant moves",
            ):
                assert_code_set_database_digest(
                    database,
                    "0" * 64,
                    "example Code-set database",
                )


class TheReaderPopulationAndThePinsMustAgree(unittest.TestCase):
    def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self):
        with tempfile.TemporaryDirectory() as directory:
            tools = Path(directory) / "tools"
            reference = Path(directory) / "reference"
            tools.mkdir()
            reference.mkdir()
            (reference / "icd10.sqlite").write_bytes(b"reference")
            (tools / "icd10_lookup.py").write_text(
                "from pathlib import Path\n"
                "DEFAULT_DATABASE = Path(__file__).parent.parent / 'reference' / 'icd10.sqlite'\n"
                "def open_database(path=DEFAULT_DATABASE):\n"
                "    return path.read_bytes()\n",
                encoding="utf-8",
            )
            (tools / "procedure_codes_lookup.py").write_text(
                "from pathlib import Path\n"
                "DEFAULT_DATABASE = Path(__file__).parent.parent / 'reference' / 'procedure.sqlite'\n"
                "def open_database(path=DEFAULT_DATABASE):\n"
                "    return path.read_bytes()\n",
                encoding="utf-8",
            )
            (tools / "code_set_database_test_support.py").write_text(
                "ICD10_DATABASE_SHA256 = 'digest'\n"
                "def assert_code_set_database_digest(*args): pass\n",
                encoding="utf-8",
            )
            (tools / "test_missing_default.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_missing_named.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self):\n"
                "        icd10_lookup.open_database(icd10_lookup.DEFAULT_DATABASE)\n",
                encoding="utf-8",
            )
            (tools / "test_stale.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "from code_set_database_test_support import (\n"
                "    ICD10_DATABASE_SHA256, assert_code_set_database_digest,\n"
                ")\n"
                "assert_code_set_database_digest('path', ICD10_DATABASE_SHA256, 'name')\n"
                "class Nonreader(unittest.TestCase):\n"
                "    def test_something_else(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            (tools / "test_counterfeit.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "def assert_code_set_database_digest(*args): pass\n"
                "assert_code_set_database_digest('path', 'digest', 'name')\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_shadowed_direct.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "from code_set_database_test_support import assert_code_set_database_digest\n"
                "def assert_code_set_database_digest(*args): pass\n"
                "assert_code_set_database_digest('path', 'digest', 'name')\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_shadowed_module.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "import code_set_database_test_support as pins\n"
                "class Counterfeit:\n"
                "    @staticmethod\n"
                "    def assert_code_set_database_digest(*args): pass\n"
                "pins = Counterfeit()\n"
                "pins.assert_code_set_database_digest('path', 'digest', 'name')\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_dynamic_digest.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "from code_set_database_test_support import assert_code_set_database_digest\n"
                "assert_code_set_database_digest('path', 'digest', 'name')\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_shadowed_helper_attribute.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "import code_set_database_test_support as pins\n"
                "def fake(*args): pass\n"
                "pins.assert_code_set_database_digest = fake\n"
                "pins.assert_code_set_database_digest(\n"
                "    'path', pins.ICD10_DATABASE_SHA256, 'name',\n"
                ")\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )
            (tools / "test_shadowed_digest_attribute.py").write_text(
                "import unittest\nimport icd10_lookup\n"
                "import code_set_database_test_support as pins\n"
                "pins.ICD10_DATABASE_SHA256 = 'digest'\n"
                "pins.assert_code_set_database_digest(\n"
                "    'path', pins.ICD10_DATABASE_SHA256, 'name',\n"
                ")\n"
                "class Reader(unittest.TestCase):\n"
                "    def test_read(self): icd10_lookup.open_database()\n",
                encoding="utf-8",
            )

            result = check.audit(tools)

            self.assertEqual(
                frozenset(
                    {
                        "test_counterfeit",
                        "test_dynamic_digest",
                        "test_missing_default",
                        "test_missing_named",
                        "test_shadowed_direct",
                        "test_shadowed_digest_attribute",
                        "test_shadowed_helper_attribute",
                        "test_shadowed_module",
                    }
                ),
                result.unpinned_readers,
            )
            self.assertEqual(frozenset({"test_stale"}), result.stale_pins)

    def test_the_repository_reader_population_and_pins_agree(self):
        output = io.StringIO()

        status = check.main([], tools=Path(__file__).resolve().parent, stream=output)

        self.assertEqual(0, status, output.getvalue())
        self.assertIn("reaching test modules:", output.getvalue())
        self.assertIn("Code-set database reader pins: clean", output.getvalue())


if __name__ == "__main__":
    unittest.main()
