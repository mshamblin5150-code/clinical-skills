"""Classify every limits object, every object-free module, and every no-copy bind.

ADR 0167. The disk walk reads exact declared names and no row shape. It cannot
find a limit under an unrelated name, validate either classification reason,
judge whether a bind uses the right prose, read non-string limits, or resolve
runtime assembly, ``getattr`` access, and loop variables. Test modules without
limits objects remain outside the module-classification and warning walks.
"""

from __future__ import annotations

import ast
import re
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from prose_bind import LIMIT_CONSTANTS, NAMING, bind
from test_claude_pointers import pointer_occurrences


TOOLS = Path(__file__).resolve().parent
LIMITS_LOOKING = re.compile(r"(?<!DE)LIMIT|CEILING|LIMBS|ORPHAN|NOT_REACHED")


class ObjectRef(NamedTuple):
    module: str
    name: str


# An absence here is a decision, not proof that the module has no limitation.
NO_LIMITS = {
    "anchor_scan": "#1038 owns whether this run grader earns a limits object",
    "artifact_lock_test_support": "test support for artifact-lock fixtures, not a public checker",
    "assertion_record": "shared assertion-record data structures with no independent coverage claim",
    "block_scan": "#1038 owns whether this run grader earns a limits object",
    "case_study_render": "the renderer produces retained evidence and does not grade its coverage",
    "cdc_percentile": "a deterministic table lookup whose source and fallback disclosures are explicit outputs",
    "console_codec": "a narrow console-encoding adapter with no asserted population walk",
    "corpus_census": "a corpus counter whose reported population is named by its command output",
    "coursework_run": "shared run-directory naming and validation helpers, not an independent grader",
    "deck_render": "the renderer produces retained evidence and does not grade its coverage",
    "discussion_post_render": "the renderer formats already graded discussion-post content",
    "docx_read": "a document-reading adapter with no independent completeness claim",
    "docx_word_probe": "a Word automation probe that reports only the operation it performs",
    "filled_vitals_census": "#1038 owns whether this run grader earns a limits object",
    "git_ancestry": "shared ancestry predicates with no declared repository-population conclusion",
    "git_paths": "a byte-preserving Git path adapter with no independent completeness claim",
    "guidelines_build": "build orchestration over contracts declared by the guideline tools it calls",
    "guidelines_index": "an index builder whose schema and input contract define its reach",
    "guidelines_index_artifact": "shared index-artifact validation rather than an independent walk",
    "guidelines_manifest": "a manifest reader whose lexical discovery vocabulary is separately classified",
    "guidelines_manifest_test_support": "test support for guideline-manifest fixtures, not a public checker",
    "guidelines_recs_test_support": "test support for recommendation fixtures, not a public checker",
    "guidelines_search": "a bounded query command whose result limit is separately classified",
    "harvest_review": "an interactive review helper that makes no exhaustive population claim",
    "icd10_build": "a database builder whose input and schema checks define its work",
    "icd10_lookup": "an exact local database lookup rather than a completeness grader",
    "name_index": "a generated heading index whose producer contract owns completeness",
    "office_process": "a process-control adapter with no independent artifact-coverage claim",
    "page_image": "a page-image conversion adapter with no independent coverage claim",
    "page_text": "a page-text extraction adapter with no independent coverage claim",
    "phi_scan": "a staged-content safety gate whose scanned surfaces are explicit in its implementation",
    "post_html": "an HTML construction helper rather than a content-completeness grader",
    "prose_bind": "the shared binding instrument; its exact name vocabulary is separately classified",
    "reference_class_census": "a source-class census whose counted inputs are stated by its report",
    "render_pass": "shared retained-pass data structures rather than an independent grader",
    "repo_root": "checkout-root resolution helpers with no population assertion",
    "scratch_work": "ticket-directory path and lifecycle helpers with no population assertion",
    "shell_reader": "a subprocess text adapter with no independent completeness claim",
    "skills_mirror": "a mirror command whose orphan output path is separately classified",
    "specificity_scan": "#1038 owns whether this run grader earns a limits object",
    "spelling_scan": "an advisory spelling matcher whose vocabulary is its explicit boundary",
    "split_census": "a diagnostic census whose display limit is separately classified",
    "subject_ledger": "a ledger validator whose accepted row grammar defines its reach",
    "threshold_coverage": "a registry derivation whose catalog and filesystem joins define its reach",
    "threshold_draft": "a scaffold builder rather than a verification command",
    "threshold_grammar": "shared parsing grammar with no independent coverage conclusion",
    "tracker_records": "tracker-record data parsing shared by commands that declare their own limits",
    "tracker_scan": "an orchestrator whose nonstandard grader shape is classified by run_grader",
    "uptodate_store": "a private-store command whose manifest and unfiled reports state its reach",
    "uspstf_interval_reach": "a focused interval-analysis helper whose input table is explicit",
    "uspstf_table": "a source-table parser with no independent completeness conclusion",
    "word_automation_scan": "a focused automation census whose searched syntax is explicit",
}


# These names look like limits objects to the warning pattern but are not new
# authored objects. Reasons are declarations; this walk does not verify them.
NOT_LIMITS = {
    "apa7_coverage.MEDIA_LIMITS": "historical per-section image and table counts",
    "apa7_coverage.SECTION_LIMITS": "historical last-section numbers by chapter",
    "differential_scan.EXIT_2_LIMBS": "the command's classified exit-2 outcomes",
    "guidelines_manifest.DISCOVERY_CEILING": "tokens used by the lexical consumer-discovery walk",
    "guidelines_search.DEFAULT_LIMIT": "the default number of search results to display",
    "map_scan.LIMITS_POINTER": "the literal qualified pointer required in the implementation map",
    "peer_critique_scan.EXIT_2_LIMBS": "the command's classified exit-2 outcomes",
    "peer_critique_scan.WORD_CEILING_COUNT": "the course's reported, ungraded word expectation",
    "prose_bind.LIMIT_CONSTANTS": "the exact object-name vocabulary consumed by both limits walks",
    "render_scan.EXIT_2_LIMBS": "the command's classified exit-2 outcomes",
    "scratch_census.EXIT_2_LIMBS": "the command's classified exit-2 outcomes",
    "skills_mirror.ORPHANS": "the output directory for unmatched skill copies",
    "split_census.DEFAULT_LIMIT": "the default number of census rows to display",
    "threshold_sheet.SCOPE_SUMMARY_NOT_REACHED": "a view assembled through the declared-limit span helper",
    "voice_model_scan.EXIT_2_LIMBS": "the command's classified exit-2 outcomes",
}


DECLARED_LIMITS = (
    "A limit stored under an unrelated constant name is outside the warning pattern.",
    "Classification reasons are required but their truth is not established.",
    "A no-copy bind does not prove that it is attached to the right prose surface.",
    "Limits with no string leaves cannot be evaluated by the prose binding instrument.",
    "Test modules without limits objects are outside the module and warning classifications.",
    "Runtime assembly, getattr access, and loop-variable binds are invisible to this AST walk.",
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _assignments(path: Path) -> dict[str, ast.expr]:
    found: dict[str, ast.expr] = {}
    for node in _tree(path).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found[target.id] = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        ):
            found[node.target.id] = node.value
    return found


def _all_assignments(root: Path) -> dict[ObjectRef, ast.expr]:
    return {
        ObjectRef(path.stem, name): value
        for path in root.glob("*.py")
        for name, value in _assignments(path).items()
    }


def _bare_references(value: ast.AST) -> set[str]:
    return {node.id for node in ast.walk(value) if isinstance(node, ast.Name)}


def declared_bindings(root: Path = TOOLS) -> dict[ObjectRef, ast.expr]:
    return {
        ref: value
        for ref, value in _all_assignments(root).items()
        if ref.name in LIMIT_CONSTANTS
    }


def declares_limits(path: Path) -> bool:
    return bool(set(_assignments(path)) & set(LIMIT_CONSTANTS))


def declarers(root: Path = TOOLS) -> set[str]:
    return {ref.module for ref in declared_bindings(root)}


def authored_objects(root: Path = TOOLS) -> set[ObjectRef]:
    return {
        ref
        for ref, value in declared_bindings(root).items()
        if not (_bare_references(value) & set(LIMIT_CONSTANTS))
    }


def module_classification_findings(
    root: Path = TOOLS, no_limits: dict[str, str] = NO_LIMITS
) -> tuple[set[str], set[str], set[str]]:
    modules = {path.stem for path in root.glob("*.py") if not path.stem.startswith("test_")}
    with_objects = {module for module in declarers(root) if not module.startswith("test_")}
    declared_absent = set(no_limits)
    return (
        modules - with_objects - declared_absent,
        declared_absent - modules,
        with_objects & declared_absent,
    )


def limits_looking_candidates(root: Path = TOOLS) -> set[str]:
    candidates: set[str] = set()
    for path in root.glob("*.py"):
        if path.stem.startswith("test_"):
            continue
        assignments = _assignments(path)
        listed = {
            name: value for name, value in assignments.items() if name in LIMIT_CONSTANTS
        }
        referenced_by_listed = {
            reference
            for value in listed.values()
            for reference in _bare_references(value)
        }
        for name, value in assignments.items():
            if (
                name in LIMIT_CONSTANTS
                or not name.isupper()
                or not LIMITS_LOOKING.search(name)
                or name in referenced_by_listed
                or _bare_references(value) & set(LIMIT_CONSTANTS)
            ):
                continue
            candidates.add(f"{path.stem}.{name}")
    return candidates


def _sources_for(
    ref: ObjectRef,
    assignments: dict[ObjectRef, ast.expr],
    seen: set[ObjectRef] | None = None,
) -> set[ObjectRef]:
    if ref not in assignments:
        return set()
    visited = set() if seen is None else seen
    if ref in visited:
        return set()
    visited.add(ref)
    value = assignments[ref]
    references = {
        ObjectRef(ref.module, name)
        for name in _bare_references(value)
        if ObjectRef(ref.module, name) in assignments and name in LIMIT_CONSTANTS
    }
    if ref.name in LIMIT_CONSTANTS and not references:
        return {ref}
    if not references:
        return set()
    return set().union(
        *(_sources_for(reference, assignments, visited) for reference in references)
    )


def _imports(tree: ast.Module) -> tuple[dict[str, str], dict[str, ObjectRef]]:
    modules: dict[str, str] = {}
    objects: dict[str, ObjectRef] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                objects[alias.asname or alias.name] = ObjectRef(node.module, alias.name)
    return modules, objects


@dataclass
class ResolutionContext:
    current_module: str
    module_aliases: dict[str, str]
    object_aliases: dict[str, ObjectRef]
    local_aliases: dict[str, ObjectRef]

    def reference(self, expression: ast.expr) -> ObjectRef | None:
        if isinstance(expression, ast.Name):
            if expression.id in self.local_aliases:
                return self.local_aliases[expression.id]
            if expression.id in self.object_aliases:
                return self.object_aliases[expression.id]
            if expression.id in LIMIT_CONSTANTS:
                return ObjectRef(self.current_module, expression.id)
        if (
            isinstance(expression, ast.Attribute)
            and isinstance(expression.value, ast.Name)
            and expression.value.id in self.module_aliases
        ):
            return ObjectRef(
                self.module_aliases[expression.value.id], expression.attr
            )
        return None

    def proven_view(self, expression: ast.expr) -> ObjectRef | None:
        direct = self.reference(expression)
        if direct is not None:
            return direct
        if not (
            isinstance(expression, ast.Call)
            and isinstance(expression.func, ast.Name)
            and expression.func.id in {"frozenset", "list", "set", "tuple"}
            and len(expression.args) == 1
            and not expression.keywords
        ):
            return None
        source = self.reference(expression.args[0])
        if source is not None:
            return source
        if not isinstance(expression.args[0], (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return None
        comprehension = expression.args[0]
        if len(comprehension.generators) != 1 or comprehension.generators[0].ifs:
            return None
        source = self.reference(comprehension.generators[0].iter)
        target_names = {
            node.id
            for node in ast.walk(comprehension.generators[0].target)
            if isinstance(node, ast.Name)
        }
        if not (
            source is not None
            and isinstance(comprehension.elt, ast.Name)
            and comprehension.elt.id in target_names
        ):
            return None
        return source

    def is_prose_bind_call(self, function: ast.expr, expected: str) -> bool:
        if isinstance(function, ast.Name):
            return self.object_aliases.get(function.id) == ObjectRef(
                "prose_bind", expected
            )
        return (
            isinstance(function, ast.Attribute)
            and function.attr == expected
            and isinstance(function.value, ast.Name)
            and self.module_aliases.get(function.value.id) == "prose_bind"
        )

    def is_naming_mode(self, expression: ast.expr) -> bool:
        if isinstance(expression, ast.Constant):
            return expression.value == NAMING
        if isinstance(expression, ast.Name):
            return self.object_aliases.get(expression.id) == ObjectRef(
                "prose_bind", "NAMING"
            )
        return (
            isinstance(expression, ast.Attribute)
            and expression.attr == "NAMING"
            and isinstance(expression.value, ast.Name)
            and self.module_aliases.get(expression.value.id) == "prose_bind"
        )


def bound_objects(root: Path = TOOLS) -> set[ObjectRef]:
    assignments = _all_assignments(root)
    authored = authored_objects(root)
    found: set[ObjectRef] = set()
    claude = root.parent / "CLAUDE.md"
    if claude.is_file():
        for pointer in pointer_occurrences(claude.read_text(encoding="utf-8")):
            found.update(_sources_for(ObjectRef(pointer.module, pointer.constant), assignments))

    for path in root.glob("test_*.py"):
        tree = _tree(path)
        module_aliases, object_aliases = _imports(tree)
        resolver = ResolutionContext(path.stem, module_aliases, object_aliases, {})
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                reference = resolver.proven_view(node.value)
                if reference is not None:
                    resolver.local_aliases[node.targets[0].id] = reference
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            copied = resolver.is_prose_bind_call(call.func, "copied_leaves")
            naming_bind = resolver.is_prose_bind_call(call.func, "bind")
            if (not copied and not naming_bind) or len(call.args) < 2:
                continue
            if naming_bind:
                mode = next(
                    (keyword.value for keyword in call.keywords if keyword.arg == "mode"),
                    None,
                )
                if mode is None or not resolver.is_naming_mode(mode):
                    continue
            if isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, str):
                continue
            reference = resolver.reference(call.args[0])
            if reference is not None:
                found.update(_sources_for(reference, assignments))
    return found & authored


class EveryLimitsDeclarationIsClassified(unittest.TestCase):
    def test_every_non_test_module_has_an_object_or_a_reason(self):
        missing, stale, conflicting = module_classification_findings()
        self.assertEqual(set(), missing, "modules with neither an object nor a reason")
        self.assertEqual(set(), stale, "no-limits entries whose module is missing")
        self.assertEqual(set(), conflicting, "no-limits entries whose module has an object")

    def test_every_no_limits_reason_is_nonempty(self):
        self.assertTrue(all(reason.strip() for reason in NO_LIMITS.values()))

    def test_every_authored_object_has_a_no_copy_bind(self):
        self.assertEqual(
            set(),
            authored_objects() - bound_objects(),
            "authored limits objects with no resolvable no-copy bind",
        )

    def test_every_limits_looking_constant_is_deliberately_classified(self):
        self.assertEqual(set(NOT_LIMITS), limits_looking_candidates())
        self.assertTrue(all(reason.strip() for reason in NOT_LIMITS.values()))

    def test_the_walks_own_limits_are_bound_to_the_module_docstring(self):
        self.assertEqual((), bind(DECLARED_LIMITS, __doc__, mode=NAMING))

    def test_the_candidacy_derivation_reads_every_declared_name(self):
        population = declarers()
        self.assertIn("case_study_scan", population)
        self.assertIn("differential_scan", population)
        self.assertIn("reference_scan", population)
        self.assertIn("test_glossary_collisions", population)


class TheClassificationInstrumentIsLive(unittest.TestCase):
    def write(self, root: Path, name: str, source: str) -> None:
        (root / name).write_text(source, encoding="utf-8")

    def test_a_qualified_listed_name_joins_the_population(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "LEGAL_READER_NOT_REACHED = ('outside',)\n")
            self.assertEqual({"sample"}, declarers(root))

    def test_a_module_without_an_object_or_reason_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "VALUE = 1\n")
            missing, stale, conflicting = module_classification_findings(root, {})
            self.assertEqual({"sample"}, missing)
            self.assertEqual(set(), stale | conflicting)

    def test_a_stale_no_limits_entry_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            missing, stale, conflicting = module_classification_findings(
                root, {"sample": "the old absence decision"}
            )
            self.assertEqual(set(), missing | stale)
            self.assertEqual({"sample"}, conflicting)

    def test_an_unbound_object_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")},
                authored_objects(root) - bound_objects(root),
            )

    def test_an_arbitrary_transformation_is_not_a_view(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "alias = discard(sample.DECLARED_LIMITS)\n"
                "def test_bind():\n"
                "    assert not bind(alias, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_fabricated_comprehension_is_not_a_view(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "alias = tuple('fabricated' for _ in sample.DECLARED_LIMITS)\n"
                "def test_bind():\n"
                "    assert not bind(alias, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_planted_limits_looking_constant_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "FOO_CEILING = ('outside',)\n")
            self.assertEqual({"sample.FOO_CEILING"}, limits_looking_candidates(root))

    def test_a_row_referenced_by_the_listed_object_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "sample.py",
                "FOO_CEILING = 'outside'\nDECLARED_LIMITS = (FOO_CEILING,)\n",
            )
            self.assertEqual(set(), limits_looking_candidates(root))

    def test_a_view_passes_and_its_bind_belongs_to_the_authored_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "sample.py",
                "DECLARED_LIMITS = ('outside',)\n"
                "NOT_REACHED = tuple(DECLARED_LIMITS)\n",
            )
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    assert not bind(sample.NOT_REACHED, surface, mode=NAMING)\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, authored_objects(root)
            )
            self.assertEqual(authored_objects(root), bound_objects(root))


if __name__ == "__main__":
    unittest.main()
