"""ADR 0356 filing keys from the committed ICU/CLDR primary-weight table.

Secondary accent differences and tertiary case differences are disregarded.
The Latin repertoire is fixed by the builder; characters outside it retain their
NFKD letters. Printed names are never modified. English folding also owns citation
equality in every paper language. German awaits its own ruling.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from repo_root import scratch_root, scratch_path

TABLE = json.loads((Path(__file__).resolve().parent.parent / "reference" / "reference-alphabets.json").read_text(encoding="utf-8"))
ALIASES = {
    "english": "en", "danish": "da", "norwegian bokmål": "nb",
    "norwegian bokmal": "nb", "norwegian": "nb", "no": "nb",
    "swedish": "sv", "finnish": "fi", "icelandic": "is", "polish": "pl",
    "czech": "cs", "turkish": "tr", "spanish": "es",
}
LANGUAGE_LINE = re.compile(r"^PAPER-LANGUAGE:[ \t]*(.*?)[ \t]*$", re.M)


def language_name(language: str | None) -> str:
    """Resolve named answers and BCP 47 variants without inventing an alphabet."""
    if not language:
        return "unspecified"
    name = language.strip().casefold()
    return ALIASES.get(name, name.split("-")[0] if "-" in name else name)


def paper_language(override: str | None = None, profile: Path | None = None) -> str | None:
    """Explicit paper override wins; silence or duplicate profile answers is unread."""
    if override is not None:
        return override
    profile = profile if profile is not None else scratch_path(scratch_root(), "medatrax-profile.md")
    try:
        answers = LANGUAGE_LINE.findall(profile.read_text(encoding="utf-8"))
    except OSError:
        return None
    return answers[0] if len(answers) == 1 and answers[0] else None


def matching(text: str) -> str:
    """Plain letters for citation equality, preserving punctuation for the caller."""
    folded = unicodedata.normalize("NFKD", text.casefold())
    return "".join(TABLE["english_fold"].get(c, c) for c in folded if not unicodedata.combining(c))


def ordering(text: str, language: str = "en") -> str:
    """Spacing/punctuation-free primary filing key; longest contractions first."""
    name = language_name(language)
    row = TABLE["languages"][name]
    if name == "en":
        return "".join(c for c in matching(text) if c.isalnum())
    # Turkish's two I's must survive case folding; NFC accepts decomposed spellings.
    text = unicodedata.normalize("NFC", text)
    if name == "tr":
        text = text.replace("I", "ı").replace("İ", "i")
    text = "".join(c for c in text.casefold() if c.isalnum())
    result: list[str] = []
    position = 0
    while position < len(text):
        token = next((c for c in row["contractions"] if text.startswith(c, position)), text[position])
        weight = row["weights"].get(token)
        if weight is None:
            weight = "".join(row["weights"].get(c, c) for c in matching(token) if c.isalnum())
        result.append(weight)
        position += len(token)
    return "".join(result)
