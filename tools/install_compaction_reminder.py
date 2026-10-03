#!/usr/bin/env python3
"""Install Codex's written compaction rule from AGENTS.md. #1206.

Live attempt, 2026-10-03, codex-cli 0.159.0-alpha.12.1: a PostCompact
additionalContext probe was offered in a disposable project and /compact was
invoked in the TUI. The live admission screen said 'Hooks need review' and
'Continue without trusting (hooks won't run)'. Clinician review/trust through
/hooks was unavailable during this build. Delivery to the model was therefore
not established; this installer takes ADR 0281's written-rule fallback. The
probe does not establish that an admitted PostCompact hook cannot deliver text.
No Codex hook is registered by this installer.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

from console_codec import require_python_floor, use_utf8
from repo_root import main_repo_root


SOURCE_ROOT = Path(__file__).resolve().parent.parent
BLOCK_START = "<!-- clinical-skills:compaction-rule:start -->"
BLOCK_END = "<!-- clinical-skills:compaction-rule:end -->"


def _read_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def rule_text(root: Path) -> str:
    text = _read_exact(root / "AGENTS.md").replace("\r\n", "\n")
    matches = list(re.finditer(r"(?m)^7\. \*\*After a compaction,", text))
    if len(matches) != 1:
        raise ValueError("AGENTS.md must contain one compaction standing rule 7")
    tail = text[matches[0].start():]
    first, remainder = tail.split("\n", 1)
    return first + "\n" + re.split(r"(?m)^\d+\. |^#", remainder, maxsplit=1)[0].rstrip() + "\n"


def _install_block(existing: str, rule: str) -> str:
    block = BLOCK_START + "\n" + rule + BLOCK_END
    if existing.count(BLOCK_START) != existing.count(BLOCK_END) or existing.count(BLOCK_START) > 1:
        raise ValueError("the Codex AGENTS file has malformed compaction block markers")
    if BLOCK_START in existing:
        match = re.search(re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END), existing, re.DOTALL)
        if match is None:
            raise ValueError("the Codex AGENTS file has reversed compaction block markers")
        return existing[:match.start()] + block + existing[match.end():]
    return existing + ("\n\n" if existing else "") + block + "\n"


def install(*, home: Path, source_root: Path, owning_checkout: Path) -> None:
    rule = rule_text(owning_checkout)
    if rule != rule_text(source_root):
        raise ValueError("update the owning checkout before installing standing rule 7")
    # Resolve the repository-relative ADR link for the user-level installed copy.
    rule = rule.replace("(docs/adr/", f"({owning_checkout.resolve().as_posix()}/docs/adr/")
    agents = home / ".codex" / "AGENTS.md"
    existing = _read_exact(agents) if agents.exists() else ""
    updated = _install_block(existing, rule)
    agents.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=agents.parent, delete=False) as stream:
        stream.write(updated)
        temporary = Path(stream.name)
    temporary.replace(agents)


def main() -> int:
    try:
        install(home=Path.home(), source_root=SOURCE_ROOT,
                owning_checkout=main_repo_root(SOURCE_ROOT / "tools"))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print("Codex received the written rule only; compaction hook delivery was not established.")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
