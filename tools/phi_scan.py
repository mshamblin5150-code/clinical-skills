"""Refuse to commit PHI. Standing rule 1, enforced instead of remembered.

Installed as a pre-commit hook (see CLAUDE.md), so it binds every commit in this
clone regardless of who or what makes it.

Two layers, and the difference between them is the whole design:

- **Corpus layer.** Every patient name and every date literal appearing in the
  gitignored corpus under ``scratch/``. This is the layer that catches real PHI,
  and **nothing can exempt a file from it.**
- **Shape layer.** Things that look like PHI whatever the corpus says: a ``dob``
  token followed by a date, an SSN, a phone number, an MRN followed by digits, a
  US-style ``2-30-99`` date. A file may exempt itself from this layer only, by
  declaring ``phi-scan: synthetic`` near the top -- which ``test_corpus_census``
  does, because testing a date extractor requires date-shaped literals.

The asymmetry is deliberate. A file can say "my dates are invented"; no file can
say "my patient names are fine".

Known limits, stated so nobody mistakes this for a guarantee:

- ``git commit --no-verify`` bypasses it, as it bypasses any hook.
- The corpus layer is only as good as ``scratch/``. On a fresh clone there is no
  corpus, so that layer finds nothing and the shape layer is all that remains.
- A patient name that appears nowhere in the corpus and is not date-shaped is
  caught by neither layer. All PHI here originates in the corpus, so this is a
  narrow hole, but it is a real one.
- **Binary files are skipped entirely**, so nothing inside ``reference/
  icd10cm-2026.sqlite`` is scanned. Its contents are the public ICD-10-CM
  release and carry no patient data. If a binary that could carry PHI is ever
  tracked here, this scanner will not say so.

Usage:

    python tools/phi_scan.py              # scan staged changes (what the hook runs)
    python tools/phi_scan.py --all        # scan every tracked file
    python tools/phi_scan.py --show       # reveal matches instead of redacting
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories the PHI firewall in .gitignore already covers -- scratch/ is working
# files, output/ is finished notes and case studies. Staging anything under them
# means someone reached for `git add -f`.
PHI_DIRECTORIES = ("scratch/", "output/", "cases/", "patients/")

# A file declaring this near its top is exempt from the SHAPE layer only.
SYNTHETIC_PRAGMA = "phi-scan: synthetic"
PRAGMA_SEARCH_CHARS = 4000

SHAPE_RULES = {
    # Requires an actual date after the token, so a `dob` field named in a
    # documentation table does not trip it.
    "dob-with-date": r"(?i)\bd\.?o\.?b\.?\b[^\n]{0,4}\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    "mrn-with-digits": r"(?i)\bmrn\b[^\n]{0,6}\d",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b",
    # US short dates. ISO dates (2026-08-10) do not match: "2026" cannot be the
    # one-or-two-digit first field, and there is no word boundary mid-number.
    "us-short-date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
}

# Clinical phrases the name harvester mistakes for names. These are vocabulary,
# not identifiers, and they are already committed.
#
# The labeled forms are here because the bare token is not enough: the filter
# below tests the WHOLE harvested string, and the harvester really does index
# "allergy NKDA" and "allergies nkda" as two-word names, so "nkda" alone exempts
# neither. fixtures/day-b/shorthand/case-10.md writes it without a colon and was
# refused on exactly this. Only a form written without punctuation can be
# harvested at all -- "allergies: nkda" fails the fullmatch in _looks_like_a_name
# -- which is why day-a never tripped it.
#
# **Curate this by hand, one entry at a time.** 26 of the harvested names contain
# clinical vocabulary, and two of those are longer strings with a real patient
# name inside them. Exempting the class wholesale would open a hole in the layer
# that nothing else closes.
NOT_NAMES = {
    "african american",
    "sore throat",
    "vaccs utd",
    "nkda",
    "allergy nkda",
    "allergies nkda",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    match: str

    def render(self, show: bool) -> str:
        shown = self.match if show else _redact(self.match)
        return f"  {self.path}:{self.line}  [{self.rule}]  {shown}"


def _redact(text: str) -> str:
    return text[0] + "*" * (len(text) - 1) if text else ""


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=REPO_ROOT,
    ).stdout


def corpus_identifiers() -> tuple[set[str], set[str]]:
    """Patient names and date literals harvested from the gitignored corpus."""
    names: set[str] = set()
    dates: set[str] = set()

    index = REPO_ROOT / "scratch" / "name-index.json"
    if index.is_file():
        try:
            entries = json.loads(index.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []
        for entry in entries:
            if entry.get("name"):
                names.add(entry["name"].strip())
            for line in entry.get("win", []):
                candidate = line.strip()
                if _looks_like_a_name(candidate):
                    names.add(candidate)

    corpus = REPO_ROOT / "scratch" / "day-file-text"
    if corpus.is_dir():
        for path in corpus.glob("*.txt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            dates.update(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))

    names = {n for n in names if len(n) > 5 and n.lower() not in NOT_NAMES}
    return names, dates


def _looks_like_a_name(text: str) -> bool:
    return bool(
        len(text) > 5
        and re.fullmatch(r"[A-Za-z][A-Za-z'\-]+(?: [A-Za-z][A-Za-z'\-.]+){1,2}", text)
    )


def declares_synthetic(text: str) -> bool:
    return SYNTHETIC_PRAGMA in text[:PRAGMA_SEARCH_CHARS]


def scan_text(
    text: str, path: str, names: set[str], dates: set[str], line_offset: int = 0
) -> list[Finding]:
    """Corpus layer always runs. Shape layer runs unless the file opts out."""
    findings: list[Finding] = []
    lines = text.splitlines()
    shapes_apply = not declares_synthetic(text)

    for number, line in enumerate(lines, start=1 + line_offset):
        for name in names:
            if re.search(r"\b" + re.escape(name) + r"\b", line, re.I):
                findings.append(Finding(path, number, "corpus-name", name))
        for date in dates:
            if date in line:
                findings.append(Finding(path, number, "corpus-date", date))
        if shapes_apply:
            for rule, pattern in SHAPE_RULES.items():
                for match in re.finditer(pattern, line):
                    findings.append(Finding(path, number, rule, match.group(0)))
    return findings


def staged_paths() -> list[str]:
    out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [p for p in out.splitlines() if p.strip()]


def staged_additions() -> dict[str, list[tuple[int, str]]]:
    """Added lines per file, with their line numbers in the new file."""
    return parse_diff(_git("diff", "--cached", "--unified=0", "--diff-filter=ACMR"))


def parse_diff(diff: str) -> dict[str, list[tuple[int, str]]]:
    """Added lines per file, keyed by path.

    A binary file contributes nothing: git prints ``Binary files ... differ``
    with no ``+++ b/`` header and no ``+`` lines, so the path never enters this
    map. That is what keeps ``scan_staged`` from pulling the 13 MB code set
    through ``git show`` on every commit, and ``test_phi_scan`` pins it down.
    """
    additions: dict[str, list[tuple[int, str]]] = {}
    path = ""
    number = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            additions.setdefault(path, [])
        elif line.startswith("@@"):
            header = re.search(r"\+(\d+)", line)
            number = int(header.group(1)) if header else 0
        elif line.startswith("+") and not line.startswith("+++") and path:
            additions[path].append((number, line[1:]))
            number += 1
    return additions


def scan_staged(names: set[str], dates: set[str]) -> list[Finding]:
    findings: list[Finding] = []

    for path in staged_paths():
        if any(path.startswith(directory) for directory in PHI_DIRECTORIES):
            findings.append(Finding(path, 0, "phi-directory", path))

    for path, added in staged_additions().items():
        if any(path.startswith(directory) for directory in PHI_DIRECTORIES):
            continue  # already reported, and its contents must not be echoed
        whole = _git("show", f":{path}")
        shapes_apply = not declares_synthetic(whole)
        for number, text in added:
            findings.extend(
                _scan_line(text, path, number, names, dates, shapes_apply)
            )
    return findings


def _scan_line(
    text: str, path: str, number: int, names: set[str], dates: set[str], shapes: bool
) -> list[Finding]:
    findings: list[Finding] = []
    for name in names:
        if re.search(r"\b" + re.escape(name) + r"\b", text, re.I):
            findings.append(Finding(path, number, "corpus-name", name))
    for date in dates:
        if date in text:
            findings.append(Finding(path, number, "corpus-date", date))
    if shapes:
        for rule, pattern in SHAPE_RULES.items():
            for match in re.finditer(pattern, text):
                findings.append(Finding(path, number, rule, match.group(0)))
    return findings


def looks_binary(data: bytes) -> bool:
    """A NUL byte in the first block. The same test git itself uses.

    Deliberately not an extension list: this repo tracks a ``.sqlite`` today and
    an allowlist would need editing for whatever it tracks next, silently
    scanning the new thing as text until someone noticed.
    """
    return b"\x00" in data[:8192]


def read_text_if_text(path: Path) -> str | None:
    """The file's text, or None where it is binary and there is nothing to scan.

    Decoding a binary with ``errors="replace"`` and running the shape rules over
    it produces findings that are neither true nor false -- bytes that happened
    to match a phone number. Every finding this scanner prints has to be worth
    reading, or the hook becomes something people learn to skip.
    """
    data = path.read_bytes()
    if looks_binary(data):
        return None
    return data.decode("utf-8", errors="replace")


def scan_all(names: set[str], dates: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    for path in _git("ls-files").splitlines():
        full = REPO_ROOT / path
        if not full.is_file():
            continue
        text = read_text_if_text(full)
        if text is None:
            continue
        findings.extend(scan_text(text, path, names, dates))
    return findings


def main(argv: list[str]) -> int:
    show = "--show" in argv
    names, dates = corpus_identifiers()

    if not names and not dates:
        print(
            "phi-scan: no corpus under scratch/ -- the corpus layer is inactive, "
            "only PHI-shaped patterns will be caught.",
            file=sys.stderr,
        )

    findings = scan_all(names, dates) if "--all" in argv else scan_staged(names, dates)
    if not findings:
        return 0

    print("\nphi-scan: refusing the commit. Standing rule 1: no PHI is ever committed.\n",
          file=sys.stderr)
    for finding in findings:
        print(finding.render(show), file=sys.stderr)
    print(
        "\nMatches are redacted. Re-run with --show to reveal them:\n"
        "    python tools/phi_scan.py --show\n"
        "\nIdentifiers become placeholders -- [PT], [DOB], [MRN]. If a value is\n"
        "genuinely synthetic and the file needs PHI-shaped literals, declare\n"
        f"'{SYNTHETIC_PRAGMA}' near the top of that file. That exempts the shape\n"
        "rules only; real corpus names and dates are still refused.\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
