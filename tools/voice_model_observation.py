"""One canonical-model observation shared by coursework completion readers."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

import repo_root


DECLARED_LIMITS = {
    "recorded-image-format": "Recorded images are complete blockquotes or double-quoted spans in Imagery's How an image works for the writer and Scale and consequence subsections; prose outside those quoted entries is not an image inventory.",
    "recorded-image-meaning": "Quoted-entry membership does not establish whether an image fits a point; the independent Voice reader judges that.",
    "model-observation": "The observation binds its decoded text to its own raw-byte digest; other identity readers may independently read the model, and no single physical read for the command is claimed.",
}

_IMAGE_PARTS = ("How an image works for the writer", "Scale and consequence")
_SECTION = re.compile(r"^## Imagery[ \t]*\r?$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
_QUOTED = re.compile(r'(?P<block>(?:^[ \t]*>[ \t]?.*(?:\n|$))+)|["“](?P<inline>[^"”\n]+)["”]', re.MULTILINE)


@dataclass(frozen=True)
class ImagePopulation:
    images: tuple[str, ...]
    candidates: int
    unread: int
    missing: bool = False


@dataclass(frozen=True)
class ModelObservation:
    path: Path
    sha256: str | None
    text: str | None
    imagery: ImagePopulation
    absent: bool = False

    @property
    def unread(self) -> int:
        """The canonical model is one member, regardless of failed consumers."""
        return int(self.text is None or self.imagery.missing or self.imagery.unread > 0)


def read_images(text: str) -> ImagePopulation:
    """Derive quoted entries independently of any selected match record."""
    sections = tuple(_SECTION.finditer(text))
    if len(sections) != 1:
        return ImagePopulation((), 0, len(sections), True)
    body = sections[0].group("body")
    images: list[str] = []
    candidates = unread = 0
    missing = False
    for name in _IMAGE_PARTS:
        parts = tuple(re.finditer(rf"^### {re.escape(name)}[ \t]*\r?$\n(?P<body>.*?)(?=^### |\Z)", body, re.MULTILINE | re.DOTALL))
        if len(parts) != 1:
            missing = True
            unread += len(parts)
            continue
        entries = tuple(_QUOTED.finditer(parts[0].group("body")))
        candidates += len(entries)
        if not entries:
            missing = True
        for entry in entries:
            block = entry.group("block")
            value = "\n".join(re.sub(r"^[ \t]*>[ \t]?", "", line).rstrip("\r") for line in block.splitlines()) if block is not None else entry.group("inline")
            if value.strip():
                images.append(value.strip())
            else:
                unread += 1
    return ImagePopulation(tuple(dict.fromkeys(images)), candidates, unread, missing)


def observe(resolution: repo_root.VoiceModelResolution | None = None) -> ModelObservation:
    """Read only the resolved canonical model, never infer a second model path."""
    resolved = resolution if resolution is not None else repo_root.canonical_voice_model()
    if not resolved.exists:
        return ModelObservation(resolved.path, None, None, ImagePopulation((), 0, 0, True), True)
    try:
        raw = resolved.path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError):
        return ModelObservation(resolved.path, None, None, ImagePopulation((), 0, 0, True))
    return ModelObservation(resolved.path, hashlib.sha256(raw).hexdigest(), text, read_images(text))
