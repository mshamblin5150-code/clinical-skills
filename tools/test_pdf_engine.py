"""The PDF engine is acquired lazily through one declared seam.

The AST walks below see direct imports and calls carrying an engine name as a
literal.  They cannot see a name assembled at run time or a constant passed to
``importlib``; that is the declared ceiling of this claim.  The tree reader
reports how many non-test modules it opened and every unread remainder rather
than silently treating an unread file as clean.  Issue #837.
"""

from __future__ import annotations

import ast
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import page_text
import page_image
import pdf_engine
import guidelines_recs


TOOLS = Path(__file__).resolve().parent
ENGINE_NAMES = frozenset({"pymupdf", "fitz", "PyMuPDF"})


def acquisition_lines(source: str) -> list[int]:
    """Direct engine acquisitions visible to the bounded AST walk."""
    tree = ast.parse(source)
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            if any(name.split(".")[0] in {"pymupdf", "fitz"} for name in names):
                found.add(node.lineno)
        if not isinstance(node, ast.Call):
            continue
        function = ast.unparse(node.func)
        if function not in {
            "importlib.import_module",
            "importlib.metadata.version",
            "metadata.version",
        }:
            continue
        supplied = list(node.args) + [keyword.value for keyword in node.keywords]
        if any(
            isinstance(argument, ast.Constant) and argument.value in ENGINE_NAMES
            for argument in supplied
        ):
            found.add(node.lineno)
    return sorted(found)


def tree_sources() -> tuple[dict[str, str], tuple[str, ...]]:
    """Read every non-test module and retain the unread remainder."""
    sources: dict[str, str] = {}
    unread: list[str] = []
    for path in sorted(TOOLS.glob("*.py")):
        if path.name.startswith("test_"):
            continue
        try:
            sources[path.name] = path.read_text(encoding="utf-8")
        except OSError:
            unread.append(path.name)
    return sources, tuple(unread)


def acquiring_modules(sources: dict[str, str]) -> dict[str, list[int]]:
    return {
        name: lines
        for name, source in sorted(sources.items())
        if (lines := acquisition_lines(source))
    }


def sole_acquirer_is(sources: dict[str, str], expected: str) -> bool:
    return set(acquiring_modules(sources)) == {expected}


def module_scope_acquisition_lines(source: str) -> list[int]:
    """Acquisitions reachable while executing a module body."""
    found: list[int] = []

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
            fragment = ast.unparse(node)
            if acquisition_lines(fragment):
                found.append(node.lineno)
                return
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(ast.parse(source))
    return sorted(set(found))


def acquisition_is_lazy(source: str) -> bool:
    return bool(acquisition_lines(source)) and not module_scope_acquisition_lines(source)


def adapter_importers(sources: dict[str, str]) -> set[str]:
    """Non-adapter modules importing any one of the three PDF seams."""
    seams = {"pdf_engine", "page_text", "page_image"}
    holders = {f"{name}.py" for name in seams}
    found: set[str] = set()
    for name, source in sources.items():
        if name in holders:
            continue
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import) and any(
                alias.name.split(".")[0] in seams for alias in node.names
            ):
                found.add(name.removesuffix(".py"))
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in seams:
                found.add(name.removesuffix(".py"))
    return found


def roles_are_complete(sources: dict[str, str], roles: set[str]) -> bool:
    return adapter_importers(sources) == roles


class PdfEngineIsTheOnlyAcquirer(unittest.TestCase):
    def test_the_walk_rejects_zero_and_partial_match_mutants(self):
        self.assertFalse(
            sole_acquirer_is({"other.py": "value = 1\n"}, "pdf_engine.py")
        )
        self.assertFalse(
            sole_acquirer_is(
                {
                    "pdf_engine.py": "def acquire():\n    import pymupdf\n",
                    "other.py": "def open_pdf():\n    import fitz\n",
                },
                "pdf_engine.py",
            )
        )

    def test_pdf_engine_is_the_tree_s_only_acquirer(self):
        sources, unread = tree_sources()
        acquired = acquiring_modules(sources)
        unexpected = {
            name: lines for name, lines in acquired.items() if name != "pdf_engine.py"
        }
        report = (
            f"walked {len(sources)} modules; unread remainder {list(unread)}; "
            f"unexpected acquiring modules {unexpected}"
        )
        self.assertGreater(len(sources), 0, report)
        self.assertEqual(unread, (), report)
        self.assertTrue(sole_acquirer_is(sources, "pdf_engine.py"), report)


class PdfEngineAcquisitionIsLazy(unittest.TestCase):
    def test_module_scope_walk_detects_the_forbidden_shape(self):
        self.assertFalse(acquisition_is_lazy("value = 1\n"))
        self.assertFalse(acquisition_is_lazy("import pymupdf\n"))
        self.assertTrue(
            acquisition_is_lazy("def acquire():\n    import pymupdf\n")
        )

    def test_the_only_acquisition_is_below_a_function_boundary(self):
        sources, unread = tree_sources()
        report = f"walked {len(sources)} modules; unread remainder {list(unread)}"
        self.assertEqual(unread, (), report)
        self.assertTrue(acquisition_is_lazy(sources["pdf_engine.py"]), report)


class EveryPdfConsumerDeclaresItsRole(unittest.TestCase):
    def test_role_walk_detects_missing_and_stale_rows(self):
        sources = {
            "page_text.py": "import pdf_engine\n",
            "one.py": "import page_text\n",
            "two.py": "import page_image\n",
        }
        self.assertFalse(roles_are_complete({}, {"one", "two"}))
        self.assertFalse(roles_are_complete(sources, {"one"}))
        self.assertFalse(roles_are_complete(sources, {"one", "two", "stale"}))
        self.assertTrue(roles_are_complete(sources, {"one", "two"}))

    def test_roles_are_complete_in_both_directions(self):
        sources, unread = tree_sources()
        report = f"walked {len(sources)} modules; unread remainder {list(unread)}"
        self.assertEqual(unread, (), report)
        self.assertTrue(roles_are_complete(sources, set(pdf_engine.ROLES)), report)


class ConsumersImportWithoutTheEngine(unittest.TestCase):
    def test_all_declared_consumers_import_with_engine_imports_blocked(self):
        modules = sorted(
            set(pdf_engine.ROLES) | {"pdf_engine", "page_text", "page_image"}
        )
        program = (
            "import importlib, sys\n"
            "class Block:\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname in {'pymupdf', 'fitz'}:\n"
            "            raise ImportError(f'blocked {fullname}')\n"
            "        return None\n"
            "sys.meta_path.insert(0, Block())\n"
            f"modules = {modules!r}\n"
            "for module in modules:\n"
            "    importlib.import_module(module)\n"
        )
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=TOOLS,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


class PdfEngineResidueIsDeclared(unittest.TestCase):
    def test_declared_limits_name_every_ticket_residue(self):
        self.assertEqual(
            {
                "role-correctness",
                "engine-object-leakage",
                "image-probe-window",
                "decode-resolution",
                "guidelines-extract-split",
                "consumer-contract",
                "threshold-gates",
            },
            set(pdf_engine.DECLARED_LIMITS),
        )


class GuidelinesRecommendationsConvertsAbsence(unittest.TestCase):
    def test_an_absent_engine_is_a_did_not_scan_status_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.pdf"
            source.touch()
            stderr = io.StringIO()
            with (
                mock.patch.object(guidelines_recs, "curated_rows_for", return_value=[]),
                mock.patch.object(
                    page_text.pdf_engine,
                    "acquire",
                    side_effect=pdf_engine.EngineUnavailable(),
                ),
                redirect_stderr(stderr),
            ):
                status = guidelines_recs.main([str(source)])
        self.assertEqual(status, 2)
        self.assertIn(pdf_engine.REMEDY, stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


class PageTextKeepsTheDocumentOpen(unittest.TestCase):
    def test_page_capabilities_do_not_expose_the_engine_page(self):
        class Pixmap:
            samples = b"gray"
            width = 2
            height = 3

        class EngineTable:
            def extract(self):
                return [["cell"]]

        class EnginePage:
            def get_text(self, kind="text"):
                return {"blocks": []} if kind == "rawdict" else "plain"

            def get_pixmap(self, **_arguments):
                return Pixmap()

            def find_tables(self):
                return type("Found", (), {"tables": (EngineTable(),)})()

        class Document:
            metadata = {"title": "  Title  "}

            def __init__(self):
                self.closed = False
                self.page = EnginePage()

            def __len__(self):
                return 1

            def __iter__(self):
                return iter((self.page,))

            def __getitem__(self, index):
                return (self.page,)[index]

            def close(self):
                self.closed = True

        document = Document()
        engine = type(
            "Engine",
            (),
            {
                "open": staticmethod(lambda _path: document),
                "Matrix": staticmethod(lambda x, y: (x, y)),
                "Rect": staticmethod(tuple),
                "csGRAY": "gray",
            },
        )()
        with mock.patch.object(page_text.pdf_engine, "acquire", return_value=engine):
            with page_text.open_document(Path("source.pdf")) as opened:
                self.assertEqual(opened.title, "Title")
                self.assertEqual(opened.page_count, 1)
                page = opened.page(1)
                self.assertEqual(page.number, 1)
                self.assertEqual(page.rawdict, {"blocks": []})
                self.assertEqual(page.plain_text(), "plain")
                self.assertEqual(page.tables(), ([["cell"]],))
                self.assertEqual(page.render_glyph((1, 2, 3, 4)), (b"gray", 2, 3))
                self.assertFalse(hasattr(page, "page"))
        self.assertTrue(document.closed)


class PageImageOwnsRasterizationAndTheProbe(unittest.TestCase):
    def test_document_failures_after_open_become_typed_read_failures(self):
        class Document:
            def __init__(self, failure_at):
                self.failure_at = failure_at

            def __enter__(self):
                return self

            def __exit__(self, *_arguments):
                if self.failure_at == "close":
                    raise OSError("close failed")

            def __len__(self):
                if self.failure_at == "length":
                    raise OSError("length failed")
                return 1

            def __iter__(self):
                if self.failure_at == "iteration":
                    raise OSError("iteration failed")
                return iter(())

        class Engine:
            failure_at = ""

            @classmethod
            def open(cls, _path):
                return Document(cls.failure_at)

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            page_image.pdf_engine, "acquire", return_value=Engine
        ):
            root = Path(directory)
            for failure_at, operation in (
                ("length", lambda: page_image.export_page_count(root / "export.pdf")),
                (
                    "iteration",
                    lambda: page_image.rasterize(
                        root / "export.pdf", root, name="page"
                    ),
                ),
                ("close", lambda: page_image.export_page_count(root / "export.pdf")),
            ):
                with self.subTest(failure_at=failure_at):
                    Engine.failure_at = failure_at
                    with self.assertRaises(pdf_engine.SourceUnreadable) as caught:
                        operation()
                    self.assertIn("failed", str(caught.exception))

    def test_rasterize_stages_each_page_and_probe_rejects_a_renamed_pdf(self):
        import tempfile

        class Pixmap:
            def save(self, path):
                Path(path).write_bytes(page_image.PNG_SIGNATURE + b"pixels")

        class Page:
            def get_pixmap(self, **_arguments):
                return Pixmap()

        class Document:
            def __len__(self):
                return 2

            def __iter__(self):
                return iter((Page(), Page()))

            def __enter__(self):
                return self

            def __exit__(self, *_arguments):
                return None

        engine = type("Engine", (), {"open": staticmethod(lambda _path: Document())})()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            export = root / "export.pdf"
            export.write_bytes(b"pdf")
            with mock.patch.object(page_image.pdf_engine, "acquire", return_value=engine):
                self.assertEqual(
                    page_image.rasterize(export, root, name="page"),
                    2,
                )
            self.assertEqual(
                sorted(path.name for path in root.glob("*.png")),
                ["page-1.png", "page-2.png"],
            )
            renamed = root / "renamed.png"
            renamed.write_bytes(b"%PDF-1.7")
            self.assertEqual(
                page_image.page_read_error(renamed),
                "does not carry a PNG signature",
            )


if __name__ == "__main__":
    unittest.main()
