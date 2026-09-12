#!/usr/bin/env python3
"""Derive the repository's consumer and tooling Python floors.

The vocabulary is deliberately finite.  ``syntax`` and resolved ``api``
witnesses grade; ``api-heuristic`` witnesses are reported without changing the
verdict.  Exit 0 means the declared floors hold, 1 means a graded floor finding,
and 2 means the tracked population could not be walked completely.

What a clean run does not establish is declared once in ``NOT_REACHED`` rather
than copied into prose.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import sys

from console_codec import require_python_floor, use_utf8
import git_paths


CONSUMER_FLOOR = (3, 10)
TOOLING_FLOOR = (3, 10)
GRADING_TIERS = {"syntax", "api"}


@dataclass(frozen=True)
class Feature:
    name: str
    version: tuple[int, int]
    tier: str


# This object is the declared ceiling of the static instrument.  A clean run
# means no feature outside this vocabulary was measured.
FEATURES = (
    Feature("match statement", (3, 10), "syntax"),
    Feature("except*", (3, 11), "syntax"),
    Feature("type statement", (3, 12), "syntax"),
    Feature("evaluated PEP 604 annotation", (3, 10), "api"),
    Feature("pathlib.Path.unlink(missing_ok=)", (3, 8), "api"),
    Feature("pathlib.Path.is_relative_to", (3, 9), "api"),
    Feature("zip(strict=)", (3, 10), "api"),
    Feature("contextlib.chdir", (3, 11), "api"),
    Feature("tomllib", (3, 11), "api"),
    Feature("enum.StrEnum", (3, 11), "api"),
    Feature("typing.Self", (3, 11), "api"),
    Feature("datetime.UTC", (3, 11), "api"),
    Feature("itertools.batched", (3, 12), "api"),
    Feature("pathlib.Path.walk", (3, 12), "api"),
    Feature("typing.override", (3, 12), "api"),
    Feature("os.process_cpu_count", (3, 13), "api"),
    Feature("unresolved .walk", (3, 12), "api-heuristic"),
)

FEATURE_BY_NAME = {feature.name: feature for feature in FEATURES}
REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE = (3, 7)
SKILL_COMMAND = re.compile(r"(?<![A-Za-z0-9_/])python[ \t]+tools/([A-Za-z_][A-Za-z0-9_]*)\.py\b")
DECLARED_LIMITS = (
    "Features outside the declared vocabulary are not detected.",
    "Dynamic calls and imports are not executed by the static walk.",
    "Deferred annotations evaluated only on an untested path may raise later.",
    "Dependency and platform branches not exercised by the floor job stay unknown.",
    "Heuristic API matches are reported but never set a floor.",
    "Untracked Python and untracked skill instructions are outside git ls-files.",
)
NOT_REACHED = tuple(DECLARED_LIMITS)


@dataclass(frozen=True)
class Witness:
    feature: Feature
    path: str
    line: int


@dataclass(frozen=True)
class ScopeBindings:
    imports: dict[str, str]
    assigned: frozenset[str]


SCOPE_NODES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _scope_bindings(scope: ast.AST) -> ScopeBindings:
    imports: dict[str, str] = {}
    assigned: set[str] = set()
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        arguments = (*scope.args.posonlyargs, *scope.args.args, *scope.args.kwonlyargs)
        assigned.update(argument.arg for argument in arguments)
        if scope.args.vararg:
            assigned.add(scope.args.vararg.arg)
        if scope.args.kwarg:
            assigned.add(scope.args.kwarg.arg)

    def visit(node: ast.AST) -> None:
        if node is not scope and isinstance(node, SCOPE_NODES):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                assigned.add(node.name)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name.split(".")[0]] = alias.name
            return
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name != "*":
                    imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
            return
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            assigned.add(node.id)
        for child in ast.iter_child_nodes(node):
            visit(child)

    if isinstance(scope, ast.Module):
        for statement in scope.body:
            visit(statement)
    elif isinstance(scope, ast.Lambda):
        visit(scope.body)
    else:
        for statement in scope.body:
            visit(statement)
    return ScopeBindings(imports, frozenset(assigned))


class Resolver:
    def __init__(self, tree: ast.Module):
        self.parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        scopes = [tree] + [node for node in ast.walk(tree) if node is not tree and isinstance(node, SCOPE_NODES)]
        self.bindings = {scope: _scope_bindings(scope) for scope in scopes}

    def name(self, node: ast.AST, name: str) -> tuple[str, str | None]:
        cursor: ast.AST | None = node
        while cursor is not None:
            if cursor in self.bindings:
                scope = self.bindings[cursor]
                if name in scope.assigned:
                    return "shadowed", None
                if name in scope.imports:
                    return "import", scope.imports[name]
            cursor = self.parents.get(cursor)
        return "unbound", None


def _qualified_name(node: ast.AST, resolver: Resolver) -> str | None:
    if isinstance(node, ast.Name):
        kind, qualified = resolver.name(node, node.id)
        return qualified if kind == "import" else None
    if isinstance(node, ast.Attribute):
        base = _qualified_name(node.value, resolver)
        return f"{base}.{node.attr}" if base else None
    if isinstance(node, ast.Call):
        return _qualified_name(node.func, resolver)
    return None


def _path_names(tree: ast.Module, resolver: Resolver) -> set[str]:
    names: set[str] = set()

    def is_path(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in names
        if isinstance(node, ast.Call):
            qualified = _qualified_name(node.func, resolver)
            if qualified == "pathlib.Path":
                return True
            return (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"absolute", "expanduser", "resolve", "with_name", "with_suffix"}
                and is_path(node.func.value)
            )
        if isinstance(node, ast.Attribute) and node.attr in {"parent", "parents"}:
            return is_path(node.value)
        return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and is_path(node.left)

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                continue
            if not is_path(node.value):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in names:
                    names.add(target.id)
                    changed = True
    return names


def _is_path_expression(node: ast.AST, resolver: Resolver, names: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, ast.Call):
        qualified = _qualified_name(node.func, resolver)
        if qualified == "pathlib.Path":
            return True
        return (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"absolute", "expanduser", "resolve", "with_name", "with_suffix"}
            and _is_path_expression(node.func.value, resolver, names)
        )
    if isinstance(node, ast.Attribute) and node.attr in {"parent", "parents"}:
        return _is_path_expression(node.value, resolver, names)
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and _is_path_expression(node.left, resolver, names)
    )


def _annotation_nodes(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                yield node.returns
            arguments = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            for argument in arguments:
                if argument.annotation is not None:
                    yield argument.annotation
            if node.args.vararg and node.args.vararg.annotation is not None:
                yield node.args.vararg.annotation
            if node.args.kwarg and node.args.kwarg.annotation is not None:
                yield node.args.kwarg.annotation
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation


def scan_source(source: str, path: str) -> tuple[Witness, ...]:
    """Return the declared version witnesses in one Python source file."""

    tree = ast.parse(source, filename=path)
    resolver = Resolver(tree)
    path_names = _path_names(tree, resolver)
    future_annotations = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )
    found: dict[tuple[str, int], Witness] = {}

    def add(name: str, line: int) -> None:
        feature = FEATURE_BY_NAME[name]
        found[(name, line)] = Witness(feature, path, line)

    match_statement = getattr(ast, "Match", ())
    try_star = getattr(ast, "TryStar", ())
    type_alias = getattr(ast, "TypeAlias", ())
    for node in ast.walk(tree):
        if match_statement and isinstance(node, match_statement):
            add("match statement", node.lineno)
        elif try_star and isinstance(node, try_star):
            add("except*", node.lineno)
        elif type_alias and isinstance(node, type_alias):
            add("type statement", node.lineno)

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imported = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif node.module:
                imported = [f"{node.module}.{alias.name}" for alias in node.names]
                imported.append(node.module)
            for qualified in imported:
                for name in (
                    "tomllib",
                    "contextlib.chdir",
                    "enum.StrEnum",
                    "typing.Self",
                    "datetime.UTC",
                    "itertools.batched",
                    "typing.override",
                ):
                    if qualified == name:
                        add(name, node.lineno)

        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "zip"
                and resolver.name(node, "zip")[0] == "unbound"
                and any(keyword.arg == "strict" for keyword in node.keywords)
            ):
                add("zip(strict=)", node.lineno)
            qualified = _qualified_name(node.func, resolver)
            if qualified in FEATURE_BY_NAME and FEATURE_BY_NAME[qualified].tier == "api":
                add(qualified, node.lineno)
            if isinstance(node.func, ast.Attribute):
                if (
                    node.func.attr == "unlink"
                    and any(keyword.arg == "missing_ok" for keyword in node.keywords)
                    and _is_path_expression(node.func.value, resolver, path_names)
                ):
                    add("pathlib.Path.unlink(missing_ok=)", node.lineno)
                if (
                    node.func.attr == "is_relative_to"
                    and _is_path_expression(node.func.value, resolver, path_names)
                ):
                    add("pathlib.Path.is_relative_to", node.lineno)

        if isinstance(node, ast.Attribute):
            qualified = _qualified_name(node, resolver)
            if qualified in FEATURE_BY_NAME and FEATURE_BY_NAME[qualified].tier == "api":
                add(qualified, node.lineno)
            elif node.attr == "walk" and qualified is None:
                add("unresolved .walk", node.lineno)

    if not future_annotations:
        for annotation in _annotation_nodes(tree):
            for node in ast.walk(annotation):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                    add("evaluated PEP 604 annotation", node.lineno)

    return tuple(sorted(found.values(), key=lambda row: (row.line, row.feature.name)))


def invoked_roots(files: tuple[tuple[str, str], ...]) -> set[str]:
    """Return modules named by literal ``python tools/X.py`` skill commands."""

    return {
        match.group(1)
        for _path, text in files
        for match in SKILL_COMMAND.finditer(text)
    }


def _local_imports(source: str, known: set[str]) -> set[str]:
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    return imported & known


def import_closure(roots: set[str], sources: dict[str, str]) -> set[str]:
    """Close tool roots over imports that resolve to another local tool module."""

    missing = roots - sources.keys()
    if missing:
        raise ValueError("invoked tool module is not tracked: " + ", ".join(sorted(missing)))
    closure: set[str] = set()
    pending = list(sorted(roots, reverse=True))
    known = set(sources)
    while pending:
        module = pending.pop()
        if module in closure:
            continue
        closure.add(module)
        pending.extend(sorted(_local_imports(sources[module], known) - closure, reverse=True))
    return closure


@dataclass(frozen=True)
class Report:
    consumer_floor: tuple[int, int]
    tooling_floor: tuple[int, int]
    consumer_roots: tuple[str, ...]
    consumer_closure: tuple[str, ...]
    tracked_python: tuple[str, ...]
    undeclared_roots: tuple[str, ...]
    witnesses: tuple[Witness, ...]
    unread: tuple[str, ...]

    @property
    def finding(self) -> bool:
        return (
            self.consumer_floor != CONSUMER_FLOOR
            or self.tooling_floor > TOOLING_FLOOR
        )


def _floor(witnesses: tuple[Witness, ...]) -> tuple[int, int]:
    versions = [
        witness.feature.version
        for witness in witnesses
        if witness.feature.tier in GRADING_TIERS
    ]
    return max(versions, default=BASELINE)


def scan_repository(root: Path) -> Report:
    """Walk every tracked Python file and derive both ruled populations.

    The population comes from ``git ls-files``. A clean result means no tracked
    file fails the declared floor rules; an untracked or unstaged file is
    invisible until it enters the index.
    """

    unread: list[str] = []
    try:
        python_paths = git_paths.read_path_records(
            root, "ls-files", "--cached", "-z", "--", "*.py"
        )
        skill_paths = git_paths.read_path_records(
            root, "ls-files", "--cached", "-z", "--", "skills"
        )
    except (git_paths.GitPathError, ValueError) as failure:
        raise RuntimeError(str(failure)) from failure

    sources_by_path: dict[str, str] = {}
    for relative in python_paths:
        try:
            sources_by_path[relative] = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as failure:
            unread.append(f"{relative}: {failure}")

    skill_files: list[tuple[str, str]] = []
    for relative in skill_paths:
        suffix = PurePosixPath(relative).suffix.lower()
        if suffix not in {".md", ".json"}:
            continue
        try:
            skill_files.append(
                (relative, (root / relative).read_text(encoding="utf-8"))
            )
        except (OSError, UnicodeError) as failure:
            unread.append(f"{relative}: {failure}")

    tool_sources = {
        PurePosixPath(relative).stem: source
        for relative, source in sources_by_path.items()
        if len(PurePosixPath(relative).parts) == 2
        and PurePosixPath(relative).parts[0] == "tools"
    }
    roots = invoked_roots(tuple(skill_files))
    try:
        closure = import_closure(roots, tool_sources)
    except (SyntaxError, ValueError) as failure:
        unread.append(str(failure))
        closure = roots & tool_sources.keys()

    witnesses: list[Witness] = []
    for relative, source in sources_by_path.items():
        try:
            witnesses.extend(scan_source(source, relative))
        except SyntaxError as failure:
            unread.append(f"{relative}: {failure.msg} at line {failure.lineno}")

    all_witnesses = tuple(
        sorted(witnesses, key=lambda row: (row.path, row.line, row.feature.name))
    )
    consumer_witnesses = tuple(
        witness
        for witness in all_witnesses
        if PurePosixPath(witness.path).parts[:1] == ("tools",)
        and PurePosixPath(witness.path).stem in closure
    )
    agents_text = ""
    try:
        agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as failure:
        unread.append(f"AGENTS.md: {failure}")
    undeclared = tuple(
        sorted(
            module
            for module in roots
            if not re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(module)}(?:\.py)?(?![A-Za-z0-9_])",
                agents_text,
            )
        )
    )
    return Report(
        consumer_floor=_floor(consumer_witnesses),
        tooling_floor=_floor(all_witnesses),
        consumer_roots=tuple(sorted(roots)),
        consumer_closure=tuple(sorted(closure)),
        tracked_python=tuple(sorted(python_paths)),
        undeclared_roots=undeclared,
        witnesses=all_witnesses,
        unread=tuple(unread),
    )


def _version(version: tuple[int, int]) -> str:
    return ".".join(str(part) for part in version)


def render(report: Report) -> str:
    """Render a pasteable report whose populations are present on every run."""

    grading = tuple(w for w in report.witnesses if w.feature.tier in GRADING_TIERS)
    heuristic = tuple(w for w in report.witnesses if w.feature.tier == "api-heuristic")
    lines = [
        "python-floor: consumer floor "
        f"declared={_version(CONSUMER_FLOOR)} derived={_version(report.consumer_floor)}; "
        f"consumer roots={len(report.consumer_roots)} consumer closure={len(report.consumer_closure)}",
        "python-floor: tooling floor "
        f"declared={_version(TOOLING_FLOOR)} derived={_version(report.tooling_floor)}; "
        f"tracked Python={len(report.tracked_python)}",
        "python-floor: witnesses "
        f"grading={len(grading)} api-heuristic={len(heuristic)}",
        "python-floor: skill-command roots undeclared in AGENTS.md="
        f"{len(report.undeclared_roots)}",
    ]
    lines.append("python-floor: consumer root modules")
    lines.extend(f"  ROOT tools/{module}.py" for module in report.consumer_roots)
    lines.append("python-floor: consumer closure modules")
    lines.extend(f"  CLOSURE tools/{module}.py" for module in report.consumer_closure)
    lines.append("python-floor: tracked Python population")
    lines.extend(f"  TRACKED {path}" for path in report.tracked_python)
    lines.extend(f"  tools/{module}.py" for module in report.undeclared_roots)
    for witness in report.witnesses:
        lines.append(
            f"  {witness.path}:{witness.line} [{witness.feature.tier}] "
            f"{witness.feature.name} -> {_version(witness.feature.version)}"
        )
    lines.extend(f"  UNREAD {item}" for item in report.unread)
    if report.unread:
        lines.append("python-floor: DID NOT WALK the complete tracked population")
    elif report.finding:
        lines.append("python-floor: FINDING -- a derived floor does not satisfy its declaration")
    else:
        lines.append("python-floor: CLEAN")
    return "\n".join(lines)


def main() -> int:
    try:
        report = scan_repository(REPO_ROOT)
    except RuntimeError as failure:
        print(f"python-floor: DID NOT WALK -- {failure}", file=sys.stderr)
        return 2
    print(render(report), file=sys.stderr if report.unread else sys.stdout)
    if report.unread:
        return 2
    return 1 if report.finding else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
