"""A re-derived direct JSON/Markdown read floor, not a census of indirect I/O.

This recognizes json.loads(...read_text(...)) and
read_posted_readings(...read_text(...)) in non-test tools. Built-in open,
intermediate variables, aliases and computed parsers are outside this floor.
Every visible remaining route must have a declared non-tool-run-record owner.
"""
import ast
from pathlib import Path
import unittest


# Classifications are explanations of exceptions, never the reader population.
EXCEPTIONS = {
    "adr_supersession_population.main": "maintainer classifications input",
    "browser_tab_hook._load_tool_schemas": "installed tool schemas, outside run directories",
    "claude_output_access.main": "user settings",
    "guidelines_build._recs_coverage": "maintainer corpus inventory",
    "guidelines_build._read_catalog_unlocked": "maintainer corpus catalog",
    "guidelines_build._verify_artifact": "maintainer corpus derivation record",
    "guidelines_build._existing": "maintainer corpus catalog",
    "guidelines_manifest.stamp": "maintainer source manifest",
    "guidelines_manifest._read_locked": "maintainer source manifest",
    "guidelines_manifest.load": "maintainer source manifest",
    "guidelines_recs.peek_recommendation_source": "maintainer source record",
    "guidelines_recs.load_recommendation_record": "maintainer source record",
    "guidelines_recs.locate_recommendation_record": "maintainer source record",
    "install_grilling_guard.install": "user hook settings",
    "install_run_status_guard.install": "user hook settings",
    "name_index.load_index": "account corpus index, outside run directories",
    "phi_scan._load_json": "account corpus inputs",
    "phi_scan.tracker_harvest_notice": "maintainer PHI tracker receipt",
    "phi_scan.tracker_publish_notice": "maintainer PHI tracker receipt",
    "phi_scan.public_adr_date_text": "maintainer public ADR report",
    "procedure_codes_build._verify_cpt_agreement": "maintainer licensed corpus agreement",
    "reference_alphabets.<module>": "committed reference configuration",
    "suite._weight_plan": "maintainer suite timings",
    "threshold_sheet.load_second_read": "independent reader-authored threshold read",
    "tracker_event_checks.grade_event_path": "external tracker event payload",
    "tracker_filed_from.main": "external tracker issue input",
    "tracker_scan.load_rulings": "maintainer tracker rulings",
    "voice_corpus.load_export": "account conversation export",
}


def direct_reads(root):
    found = set()
    for path in root.glob("*.py"):
        if path.name.startswith("test_"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            parser = node.func
            recognized = (
                isinstance(parser, ast.Attribute) and parser.attr == "loads"
                and isinstance(parser.value, ast.Name) and parser.value.id == "json"
            ) or isinstance(parser, ast.Name) and parser.id == "read_posted_readings"
            if not recognized or not any(
                isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr == "read_text" for call in ast.walk(node)
            ):
                continue
            owner = node
            while owner in parents and not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                owner = parents[owner]
            found.add(f"{path.stem}.{getattr(owner, 'name', '<module>')}")
    return found


class ToolRecordReadFloor(unittest.TestCase):
    def test_every_visible_direct_route_has_a_non_run_or_handwritten_owner(self):
        visible = direct_reads(Path(__file__).parent)
        self.assertEqual(set(), visible - EXCEPTIONS.keys(), "unclassified direct record reader")
        self.assertEqual(set(), EXCEPTIONS.keys() - visible, "stale read-route classification")

    def test_new_direct_json_and_markdown_routes_enter_the_floor(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "synthetic.py").write_text(
                "def json_route(path):\n return json.loads(path.read_text())\n"
                "def markdown_route(path):\n return read_posted_readings(path.read_text())\n",
                encoding="utf-8",
            )
            self.assertEqual({"synthetic.json_route", "synthetic.markdown_route"}, direct_reads(root))


if __name__ == "__main__":
    unittest.main()
