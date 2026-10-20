"""A direct-read floor over non-test tools, not proof of all indirect I/O.

Recognizes JSON parser/read_text compositions through the existing shared
classification, and literal handwritten filenames flowing through simple local
assignments to read_text/read_bytes/open. Aliases, computed names, callbacks,
interprocedural flow and external inputs are outside this floor, except the
explicit reversal_candidates_path constructor below. The full
population is also reviewed by writer/source ownership; a basename alone never
establishes ownership.
"""
import ast
from collections import Counter
from pathlib import Path
import tempfile
import unittest

import test_tool_record_routes as machine_floor


RECORD_NAMES = frozenset({
    'bar.md', 'claims.md', 'heading-read.md', 'checks.md', 'reread.md',
    'rendered.md', 'adversarial.md', 'intent.md', 'project-context.md',
    'shift-summary.md', 'delegated-answers.md', 'shift-values.json',
    'imagery-proposals.json', 'handling.json', 'attachments.md',
})

# Counts preserve each reviewed occurrence; an extra raw read in the same
# function still enters the floor rather than inheriting a blanket exemption.
RAW_ROUTES = {
    'bar_signatures._sign:bar.md': (2,
        'Canonical callback reads bytes once for shared same-owned-text validation '
        'before mutation, then compares raw bytes to detect a concurrent source change.'),
}


def direct_literal_reads(root: Path) -> Counter:
    found = Counter()
    for path in root.glob('*.py'):
        if path.name.startswith('test_'):
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for owner in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            assignments = {}
            for node in ast.walk(owner):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assignments[target.id] = node.value
            def filename(node, seen=frozenset()):
                if isinstance(node, ast.Name) and node.id in assignments and node.id not in seen:
                    return filename(assignments[node.id], seen | {node.id})
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    return node.value if node.value in RECORD_NAMES else None
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    return filename(node.right, seen)
                if isinstance(node, ast.Call) and node.args and isinstance(node.func, ast.Name) and node.func.id == 'Path':
                    return filename(node.args[0], seen)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'reversal_candidates_path':
                    return '<round>.reversal-candidates.md'
                return None
            for node in ast.walk(owner):
                if not isinstance(node, ast.Call):
                    continue
                nearest = parents.get(node)
                while nearest is not None and not isinstance(nearest, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nearest = parents.get(nearest)
                if nearest is not owner:
                    continue
                target = None
                if isinstance(node.func, ast.Attribute) and node.func.attr in {'read_text', 'read_bytes', 'open'}:
                    target = node.func.value
                elif isinstance(node.func, ast.Name) and node.func.id == 'open' and node.args:
                    target = node.args[0]
                if target is not None and (name := filename(target)):
                    found[f'{path.stem}.{owner.name}:{name}'] += 1
    return found


class HandwrittenReadRoutes(unittest.TestCase):
    def test_remaining_direct_json_routes_have_declared_non_handwritten_owners(self):
        visible = machine_floor.direct_reads(Path(__file__).parent)
        self.assertEqual(set(machine_floor.EXCEPTIONS), visible)

    def test_literal_filename_routes_are_owned_and_counted(self):
        self.assertEqual(Counter({key: value[0] for key, value in RAW_ROUTES.items()}),
                         direct_literal_reads(Path(__file__).parent))

    def test_planted_unshared_text_byte_and_stream_routes_enter_the_floor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'synthetic.py').write_text(
                "def read(run):\n p = run / 'claims.md'\n return p.read_text()\n"
                "def bytes(run):\n return (run / 'reread.md').read_bytes()\n"
                "def stream(run):\n return open(run / 'heading-read.md').read()\n", encoding='utf-8')
            self.assertEqual(Counter({'synthetic.read:claims.md': 1,
                'synthetic.bytes:reread.md': 1, 'synthetic.stream:heading-read.md': 1}), direct_literal_reads(root))

    def test_explicit_computed_candidate_constructor_enters_the_bounded_floor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'synthetic.py').write_text(
                "def read(run):\n path = reversal_candidates_path(run, 'key', 1)\n return path.read_text()\n",
                encoding='utf-8')
            self.assertEqual(Counter({'synthetic.read:<round>.reversal-candidates.md': 1}),
                             direct_literal_reads(root))
