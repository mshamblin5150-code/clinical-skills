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
    "artifact_lock_test_support": "test support for artifact-lock fixtures, not a public checker",
    "assertion_record": "shared assertion-record data structures with no independent coverage claim",
    "case_study_render": "the renderer produces retained evidence and does not grade its coverage",
    "cdc_percentile": "a deterministic table lookup whose source and fallback disclosures are explicit outputs",
    "console_codec": "a narrow console-encoding adapter with no asserted population walk",
    "corpus_census": "a corpus counter whose reported population is named by its command output",
    "coursework_run": "shared run-directory naming and validation helpers, not an independent grader",
    "deck_render": "the renderer produces retained evidence and does not grade its coverage",
    "discussion_post_render": "the renderer formats already graded discussion-post content",
    "docx_read": "a document-reading adapter with no independent completeness claim",
    "docx_word_probe": "a Word automation probe that reports only the operation it performs",
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
    "spelling_scan": "an advisory spelling matcher whose vocabulary is its explicit boundary",
    "split_census": "a diagnostic census whose display limit is separately classified",
    "subject_ledger": "a ledger validator whose accepted row grammar defines its reach",
    "threshold_coverage": "a registry derivation whose catalog and filesystem joins define its reach",
    "threshold_draft": "a scaffold builder rather than a verification command",
    "threshold_grammar": "shared parsing grammar with no independent coverage conclusion",
    "worksheet_grammar": "shared worksheet grammar with no independent coverage conclusion",
    "tracker_records": "tracker-record data parsing shared by commands that declare their own limits",
    "tracker_population": "a deterministic probe adapter whose accepted input schemas define its reach",
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
    "prose_bind.PATH_COORDINATE_CEILING": "the shared coordinate recognizer, whose bounded coverage is declared by its consuming grader",
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
    assignments = _all_assignments(root)
    return {
        ref
        for ref, value in declared_bindings(root).items()
        if not _view_sources(ref, value, assignments)
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


def _projection_from(expression: ast.expr, target_names: set[str]) -> bool:
    if isinstance(expression, ast.Name):
        return expression.id in target_names
    if isinstance(expression, ast.Attribute):
        return _projection_from(expression.value, target_names)
    if isinstance(expression, ast.Subscript):
        return _projection_from(expression.value, target_names)
    if isinstance(expression, (ast.List, ast.Tuple)):
        return bool(expression.elts) and all(
            _projection_from(item, target_names) for item in expression.elts
        )
    return False


def _view_sources(
    ref: ObjectRef, value: ast.expr, assignments: dict[ObjectRef, ast.expr]
) -> set[ObjectRef]:
    listed = {
        ObjectRef(ref.module, name)
        for name in LIMIT_CONSTANTS
        if ObjectRef(ref.module, name) in assignments
    }
    if isinstance(value, ast.Name) and ObjectRef(ref.module, value.id) in listed:
        return {ObjectRef(ref.module, value.id)}
    if not (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id in {"frozenset", "list", "set", "tuple"}
        and len(value.args) == 1
        and not value.keywords
    ):
        return set()
    argument = value.args[0]
    if isinstance(argument, ast.Name) and ObjectRef(ref.module, argument.id) in listed:
        return {ObjectRef(ref.module, argument.id)}
    if (
        isinstance(argument, ast.Call)
        and isinstance(argument.func, ast.Attribute)
        and argument.func.attr in {"items", "keys", "values"}
        and isinstance(argument.func.value, ast.Name)
        and not argument.args
        and not argument.keywords
        and ObjectRef(ref.module, argument.func.value.id) in listed
    ):
        return {ObjectRef(ref.module, argument.func.value.id)}
    if not isinstance(argument, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        return set()
    if len(argument.generators) != 1 or argument.generators[0].ifs:
        return set()
    generator = argument.generators[0]
    if not isinstance(generator.iter, ast.Name):
        return set()
    source = ObjectRef(ref.module, generator.iter.id)
    if source not in listed:
        return set()
    target_names = _bound_names(generator.target)
    return {source} if _projection_from(argument.elt, target_names) else set()


def _bind_view_sources(
    ref: ObjectRef, value: ast.expr, assignments: dict[ObjectRef, ast.expr]
) -> set[ObjectRef]:
    listed = {
        ObjectRef(ref.module, name)
        for name in LIMIT_CONSTANTS
        if ObjectRef(ref.module, name) in assignments
    }
    if isinstance(value, ast.Name) and ObjectRef(ref.module, value.id) in listed:
        return {ObjectRef(ref.module, value.id)}
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id in {"frozenset", "list", "set", "tuple"}
        and len(value.args) == 1
        and not value.keywords
        and isinstance(value.args[0], ast.Name)
        and ObjectRef(ref.module, value.args[0].id) in listed
    ):
        return {ObjectRef(ref.module, value.args[0].id)}
    return set()


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
    classified_views = _view_sources(ref, value, assignments)
    references = _bind_view_sources(ref, value, assignments)
    if ref.name in LIMIT_CONSTANTS and not references:
        return set() if classified_views else {ref}
    if not references:
        return set()
    return set().union(
        *(_sources_for(reference, assignments, visited) for reference in references)
    )


def _bound_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.List, ast.Tuple)):
        return set().union(*(_bound_names(item) for item in target.elts))
    if isinstance(target, ast.Starred):
        return _bound_names(target.value)
    return set()


def _imports(tree: ast.Module) -> tuple[dict[str, str], dict[str, ObjectRef]]:
    modules: dict[str, str] = {}
    objects: dict[str, ObjectRef] = {}
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    events = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(
                node,
                (
                    ast.Import,
                    ast.ImportFrom,
                    ast.Name,
                    ast.ExceptHandler,
                    ast.MatchAs,
                    ast.MatchStar,
                    ast.MatchMapping,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            )
            and not any(
                isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))
                for ancestor in _ancestors(node, parents)
            )
        ),
        key=lambda node: (node.lineno, getattr(node, "col_offset", 0)),
    )
    for node in events:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                if parents.get(node) is tree:
                    modules[name] = alias.name
                    objects.pop(name, None)
                else:
                    modules.pop(name, None)
                    objects.pop(name, None)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                name = alias.asname or alias.name
                if parents.get(node) is tree:
                    objects[name] = ObjectRef(node.module, alias.name)
                    modules.pop(name, None)
                else:
                    modules.pop(name, None)
                    objects.pop(name, None)
        else:
            rebound = ScopeBindings()
            rebound.visit(node)
            for name in rebound.names:
                modules.pop(name, None)
                objects.pop(name, None)
    return modules, objects


@dataclass
class ResolutionContext:
    current_module: str
    module_aliases: dict[str, str]
    object_aliases: dict[str, ObjectRef]

    def reference(
        self, expression: ast.expr, blocked: set[str] | frozenset[str] = frozenset()
    ) -> ObjectRef | None:
        if isinstance(expression, ast.Name):
            if expression.id in blocked:
                return None
            if expression.id in self.object_aliases:
                return self.object_aliases[expression.id]
            if expression.id in LIMIT_CONSTANTS:
                return ObjectRef(self.current_module, expression.id)
        if (
            isinstance(expression, ast.Attribute)
            and isinstance(expression.value, ast.Name)
            and expression.value.id not in blocked
            and expression.value.id in self.module_aliases
        ):
            return ObjectRef(
                self.module_aliases[expression.value.id], expression.attr
            )
        return None

    def is_prose_bind_call(
        self, function: ast.expr, expected: str, blocked: set[str]
    ) -> bool:
        if isinstance(function, ast.Name):
            if function.id in blocked:
                return False
            return self.object_aliases.get(function.id) == ObjectRef(
                "prose_bind", expected
            )
        return (
            isinstance(function, ast.Attribute)
            and function.attr == expected
            and isinstance(function.value, ast.Name)
            and function.value.id not in blocked
            and self.module_aliases.get(function.value.id) == "prose_bind"
        )

    def is_naming_mode(self, expression: ast.expr, blocked: set[str]) -> bool:
        if isinstance(expression, ast.Constant):
            return expression.value == NAMING
        if isinstance(expression, ast.Name):
            if expression.id in blocked:
                return False
            return self.object_aliases.get(expression.id) == ObjectRef(
                "prose_bind", "NAMING"
            )
        return (
            isinstance(expression, ast.Attribute)
            and expression.attr == "NAMING"
            and isinstance(expression.value, ast.Name)
            and expression.value.id not in blocked
            and self.module_aliases.get(expression.value.id) == "prose_bind"
        )


def _argument_names(arguments: ast.arguments) -> set[str]:
    names = {
        argument.arg
        for group in (arguments.posonlyargs, arguments.args, arguments.kwonlyargs)
        for argument in group
    }
    if arguments.vararg:
        names.add(arguments.vararg.arg)
    if arguments.kwarg:
        names.add(arguments.kwarg.arg)
    return names


class ScopeBindings(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.names.add(node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.names.add(node.name)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.add(node.name)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_DictComp(self, node: ast.DictComp) -> None:
        return

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        return

    def visit_ListComp(self, node: ast.ListComp) -> None:
        return

    def visit_SetComp(self, node: ast.SetComp) -> None:
        return

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names.add(node.id)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self.names.add(node.name)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name:
            self.names.add(node.name)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name:
            self.names.add(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest:
            self.names.add(node.rest)
        self.generic_visit(node)


class ModuleBindings(ScopeBindings):
    def __init__(self, tree: ast.Module) -> None:
        super().__init__()
        self.visit(tree)

    def visit_Import(self, node: ast.Import) -> None:
        return

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        return


class LocalBindings(ScopeBindings):
    def __init__(
        self, function: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
    ) -> None:
        super().__init__()
        self.names = _argument_names(function.args)
        if isinstance(function, ast.Lambda):
            self.visit(function.body)
        else:
            for statement in function.body:
                self.visit(statement)

    def visit_Import(self, node: ast.Import) -> None:
        self.names.update(alias.asname or alias.name.split(".")[0] for alias in node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.names.update(alias.asname or alias.name for alias in node.names)

class ClassBindings(LocalBindings):
    def __init__(self, class_: ast.ClassDef) -> None:
        ScopeBindings.__init__(self)
        for statement in class_.body:
            self.visit(statement)


def _local_imports_before(
    call: ast.Call, parents: dict[ast.AST, ast.AST]
) -> tuple[dict[str, str], dict[str, ObjectRef]]:
    scope = next(
        (
            node
            for node in _ancestors(call, parents)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
        ),
        None,
    )
    if scope is None:
        return {}, {}
    modules: dict[str, str] = {}
    objects: dict[str, ObjectRef] = {}
    events = sorted(
        (
            node
            for node in ast.walk(scope)
            if getattr(node, "lineno", call.lineno) < call.lineno
            and _nearest_function(node, parents) is scope
            and isinstance(
                node,
                (
                    ast.Import,
                    ast.ImportFrom,
                    ast.Name,
                    ast.ExceptHandler,
                    ast.MatchAs,
                    ast.MatchStar,
                    ast.MatchMapping,
                ),
            )
        ),
        key=lambda node: (node.lineno, getattr(node, "col_offset", 0)),
    )
    for node in events:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                modules[name] = alias.name
                objects.pop(name, None)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                name = alias.asname or alias.name
                objects[name] = ObjectRef(node.module, alias.name)
                modules.pop(name, None)
        else:
            names = ScopeBindings()
            names.visit(node)
            for name in names.names:
                modules.pop(name, None)
                objects.pop(name, None)
    return modules, objects


def _ancestors(node: ast.AST, parents: dict[ast.AST, ast.AST]):
    node = parents.get(node)
    while node is not None:
        yield node
        node = parents.get(node)


def _nearest_function(
    node: ast.AST, parents: dict[ast.AST, ast.AST]
) -> ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | None:
    return next(
        (
            ancestor
            for ancestor in _ancestors(node, parents)
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
        ),
        None,
    )


def _contains(container: ast.AST, node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    return container is node or container in set(_ancestors(node, parents))


def _comprehension_bindings_at_call(
    expression: ast.DictComp | ast.GeneratorExp | ast.ListComp | ast.SetComp,
    call: ast.Call,
    parents: dict[ast.AST, ast.AST],
) -> set[str]:
    bound: set[str] = set()
    for generator in expression.generators:
        if _contains(generator.iter, call, parents):
            return bound
        bound.update(_bound_names(generator.target))
        if any(_contains(condition, call, parents) for condition in generator.ifs):
            return bound
    return bound


def _blocked_at_call(call: ast.Call, parents: dict[ast.AST, ast.AST]) -> set[str]:
    blocked: set[str] = set()
    inside_function = False
    node: ast.AST | None = call
    while node is not None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            blocked.update(LocalBindings(node).names)
            inside_function = True
        elif isinstance(node, ast.ClassDef) and not inside_function:
            blocked.update(ClassBindings(node).names)
        elif isinstance(node, (ast.DictComp, ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            blocked.update(_comprehension_bindings_at_call(node, call, parents))
        node = parents.get(node)
    local_modules, local_objects = _local_imports_before(call, parents)
    blocked.difference_update(local_modules)
    blocked.difference_update(local_objects)
    return blocked


def _empty_literal(node: ast.AST) -> bool:
    return isinstance(node, (ast.Tuple, ast.List, ast.Set)) and not node.elts


def _is_enforced_no_copy_call(
    call: ast.Call, parents: dict[ast.AST, ast.AST]
) -> bool:
    test_scope = next(
        (
            node
            for node in _ancestors(call, parents)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ),
        None,
    )
    if test_scope is None or not test_scope.name.startswith("test_"):
        return False
    scope_parent = parents.get(test_scope)
    unittest_class = isinstance(scope_parent, ast.ClassDef) and any(
        (
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "unittest"
            and base.attr == "TestCase"
        )
        or (isinstance(base, ast.Name) and base.id == "TestCase")
        for base in scope_parent.bases
    )
    argument_names = [
        argument.arg
        for group in (
            test_scope.args.posonlyargs,
            test_scope.args.args,
            test_scope.args.kwonlyargs,
        )
        for argument in group
    ]
    pytest_function = isinstance(scope_parent, ast.Module) and not {
        "self",
        "cls",
    }.intersection(argument_names)
    pytest_class = (
        isinstance(scope_parent, ast.ClassDef)
        and scope_parent.name.startswith("Test")
        and bool(argument_names)
        and argument_names[0] == "self"
    )
    if not (unittest_class or pytest_function or pytest_class):
        return False
    containing_statement = next(
        (
            statement
            for statement in test_scope.body
            if _contains(statement, call, parents)
        ),
        None,
    )
    if containing_statement is None:
        return False
    if any(
        isinstance(statement, (ast.Return, ast.Raise))
        for statement in test_scope.body[: test_scope.body.index(containing_statement)]
    ):
        return False
    for ancestor in _ancestors(call, parents):
        if ancestor is test_scope:
            break
        if isinstance(ancestor, ast.If) and isinstance(ancestor.test, ast.Constant):
            in_body = any(_contains(statement, call, parents) for statement in ancestor.body)
            if (not ancestor.test.value and in_body) or (
                ancestor.test.value
                and any(_contains(statement, call, parents) for statement in ancestor.orelse)
            ):
                return False
        if isinstance(ancestor, ast.While) and isinstance(ancestor.test, ast.Constant):
            if not ancestor.test.value:
                return False
        if isinstance(ancestor, (ast.For, ast.AsyncFor)) and _empty_literal(
            ancestor.iter
        ):
            return False
    for ancestor in _ancestors(call, parents):
        if ancestor is test_scope:
            break
        if isinstance(ancestor, ast.Assert):
            if isinstance(ancestor.test, ast.UnaryOp) and isinstance(
                ancestor.test.op, ast.Not
            ):
                return ancestor.test.operand is call
            if isinstance(ancestor.test, ast.Compare) and any(
                isinstance(operator, (ast.Eq, ast.Is))
                for operator in ancestor.test.ops
            ):
                operands = [ancestor.test.left, *ancestor.test.comparators]
                return any(
                    isinstance(operator, (ast.Eq, ast.Is))
                    and (
                        (left is call and _empty_literal(right))
                        or (right is call and _empty_literal(left))
                    )
                    for left, operator, right in zip(
                        operands, ancestor.test.ops, operands[1:]
                    )
                )
        if isinstance(ancestor, ast.Call) and isinstance(ancestor.func, ast.Attribute):
            if not unittest_class or not (
                isinstance(ancestor.func.value, ast.Name)
                and ancestor.func.value.id == "self"
            ):
                continue
            if ancestor.func.attr in {"assertFalse", "assertEmpty"}:
                return bool(ancestor.args) and ancestor.args[0] is call
            if ancestor.func.attr in {"assertEqual", "assertSequenceEqual"}:
                return call in ancestor.args and any(
                    _empty_literal(argument) for argument in ancestor.args
                )
    return False


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
        parents = {
            child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
        }
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            if not _is_enforced_no_copy_call(call, parents):
                continue
            local_modules, local_objects = _local_imports_before(call, parents)
            resolver = ResolutionContext(
                path.stem,
                module_aliases | local_modules,
                object_aliases | local_objects,
            )
            blocked = _blocked_at_call(call, parents)
            copied = resolver.is_prose_bind_call(call.func, "copied_leaves", blocked)
            naming_bind = resolver.is_prose_bind_call(call.func, "bind", blocked)
            if (not copied and not naming_bind) or len(call.args) < 2:
                continue
            if naming_bind:
                mode = next(
                    (keyword.value for keyword in call.keywords if keyword.arg == "mode"),
                    None,
                )
                if mode is None or not resolver.is_naming_mode(mode, blocked):
                    continue
            if isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, str):
                continue
            reference = resolver.reference(call.args[0], _blocked_at_call(call, parents))
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

    def test_attribute_and_subscript_targets_do_not_create_view_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    bind(tuple(holder for holder.slot in sample.DECLARED_LIMITS), surface, mode=NAMING)\n"
                "    bind(tuple(holder for holder[0] in sample.DECLARED_LIMITS), surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_reassigned_alias_does_not_keep_an_old_object_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "alias = sample.DECLARED_LIMITS\n"
                "alias = ('fabricated',)\n"
                "def test_bind():\n"
                "    assert not bind(alias, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_reassigned_module_import_does_not_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "source = object()\n"
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    bind(source.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_function_parameter_shadows_an_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind(source):\n"
                "    bind(source.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_function_parameter_shadows_the_bind_machinery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind(bind):\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_an_outer_parameter_shadows_an_import_inside_a_nested_function(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def outer(source):\n"
                "    def test_bind():\n"
                "        bind(source.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_comprehension_target_shadows_an_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "values = ()\n"
                "calls = [bind(source.DECLARED_LIMITS, surface, mode=NAMING) for source in values]\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_fabricated_listed_name_transformation_is_an_authored_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "sample.py",
                "DECLARED_LIMITS = (('label', 'actual limit'),)\n"
                "NOT_REACHED = tuple('fabricated' for _ in DECLARED_LIMITS)\n",
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
                {
                    ObjectRef("sample", "DECLARED_LIMITS"),
                    ObjectRef("sample", "NOT_REACHED"),
                },
                authored_objects(root),
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")},
                authored_objects(root) - bound_objects(root),
            )

    def test_a_projected_view_does_not_claim_identity_bind_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "sample.py",
                "DECLARED_LIMITS = (('label', 'actual limit'),)\n"
                "NOT_REACHED = tuple(reason for _label, reason in DECLARED_LIMITS)\n",
            )
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'label only'\n"
                "def test_bind():\n"
                "    assert not bind(sample.NOT_REACHED, surface, mode=NAMING)\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, authored_objects(root)
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_view_of_labels_does_not_bind_the_limit_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(
                root,
                "sample.py",
                "DECLARED_LIMITS = (('label', 'actual limit'),)\n"
                "NOT_REACHED = tuple(label for label, _reason in DECLARED_LIMITS)\n",
            )
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'label only'\n"
                "def test_bind():\n"
                "    assert not bind(sample.NOT_REACHED, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_an_ignored_bind_result_does_not_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'outside copied here'\n"
                "def test_bind():\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_wrapped_or_unreachable_bind_result_does_not_count(self):
        bodies = {
            "wrapped": (
                "def test_bind(self):\n"
                "    self.assertEqual((), ignore(bind(sample.DECLARED_LIMITS, surface, mode=NAMING)))\n"
            ),
            "unreachable": (
                "def test_bind(self):\n"
                "    if False:\n"
                "        self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "after_return": (
                "def test_bind(self):\n"
                "    return\n"
                "    self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "empty_loop": (
                "def test_bind(self):\n"
                "    for _ in ():\n"
                "        self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "nested_test": (
                "def helper():\n"
                "    def test_bind(self):\n"
                "        self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "arbitrary_receiver": (
                "def test_bind():\n"
                "    Sink().assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "uncollected_class": (
                "class Sink:\n"
                "    def test_bind(self):\n"
                "        self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "top_level_self": (
                "def test_bind(self):\n"
                "    self.assertEqual((), bind(sample.DECLARED_LIMITS, surface, mode=NAMING))\n"
            ),
            "unrelated_comparison": (
                "def test_bind():\n"
                "    assert bind(sample.DECLARED_LIMITS, surface, mode=NAMING) < 0 == ()\n"
            ),
        }
        for name, body in bodies.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
                self.write(
                    root,
                    "test_sample.py",
                    "import sample\n"
                    "from prose_bind import NAMING, bind\n"
                    "surface = 'outside copied here'\n"
                    "def ignore(_value):\n"
                    "    return ()\n"
                    + body,
                )
                self.assertEqual(set(), bound_objects(root))

    def test_a_nested_module_import_prevents_stale_alias_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "if True:\n"
                "    import fake as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "class Test:\n"
                "    def test_bind(self):\n"
                "        self.assertEqual((), bind(source.DECLARED_LIMITS, surface, mode=NAMING))\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_an_import_after_a_module_reassignment_resolves(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "sample = object()\n"
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    assert not bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, bound_objects(root)
            )

    def test_a_local_direct_import_resolves(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    from sample import DECLARED_LIMITS\n"
                "    from prose_bind import NAMING, bind\n"
                "    assert not bind(DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, bound_objects(root)
            )

    def test_a_first_generator_iterable_precedes_its_target_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import unittest\n"
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "class Test(unittest.TestCase):\n"
                "    def test_bind(self):\n"
                "        return [item for source in (self.assertEqual((), bind(source.DECLARED_LIMITS, surface, mode=NAMING)) or ())]\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, bound_objects(root)
            )

    def test_pytest_fixture_parameters_remain_collectible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind(tmp_path):\n"
                "    assert not bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(
                {ObjectRef("sample", "DECLARED_LIMITS")}, bound_objects(root)
            )

    def test_a_lambda_parameter_shadows_an_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "result = (lambda source: bind(source.DECLARED_LIMITS, surface, mode=NAMING))(object())\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_local_import_shadows_the_bind_machinery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "def test_bind():\n"
                "    from helper import bind\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_a_class_binding_shadows_an_import_in_the_class_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
            self.write(
                root,
                "test_sample.py",
                "import sample as source\n"
                "from prose_bind import NAMING, bind\n"
                "surface = 'indirect prose'\n"
                "class Test:\n"
                "    source = object()\n"
                "    result = bind(source.DECLARED_LIMITS, surface, mode=NAMING)\n",
            )
            self.assertEqual(set(), bound_objects(root))

    def test_exception_pattern_and_delete_bindings_shadow_imports(self):
        bodies = {
            "exception": (
                "def test_bind():\n"
                "    try:\n"
                "        pass\n"
                "    except Exception as bind:\n"
                "        pass\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n"
            ),
            "pattern": (
                "def test_bind(value):\n"
                "    match value:\n"
                "        case {'x': bind}:\n"
                "            pass\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n"
            ),
            "delete": (
                "def test_bind():\n"
                "    del bind\n"
                "    bind(sample.DECLARED_LIMITS, surface, mode=NAMING)\n"
            ),
        }
        for name, body in bodies.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write(root, "sample.py", "DECLARED_LIMITS = ('outside',)\n")
                self.write(
                    root,
                    "test_sample.py",
                    "import sample\n"
                    "from prose_bind import NAMING, bind\n"
                    "surface = 'indirect prose'\n"
                    + body,
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
