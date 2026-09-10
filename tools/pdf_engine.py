"""The single lazy acquisition seam for the repository's PDF engine."""

from __future__ import annotations

from types import ModuleType


REMEDY = (
    "pymupdf is not installed. This is one of the tools in tools/ that is "
    "not stdlib, because it reads a PDF:\n"
    "    python -m pip install pymupdf"
)
RENDER_UNAVAILABLE = "PyMuPDF is unavailable"
TIER2_UNAVAILABLE = "pymupdf is not installed"


class EngineUnavailable(Exception):
    """The PDF engine cannot be imported in this process."""

    def __init__(self) -> None:
        super().__init__(REMEDY)


class SourceUnreadable(Exception):
    """The engine could not open a supplied document or image."""


def acquire() -> ModuleType:
    """Import the engine only when a caller starts a PDF operation."""
    try:
        import pymupdf
    except ImportError as failure:
        raise EngineUnavailable() from failure
    return pymupdf


def engine_version() -> str | None:
    """Return the importable engine's version, or ``None`` when unavailable."""
    try:
        return str(getattr(acquire(), "__version__", "unknown"))
    except EngineUnavailable:
        return None


PRIMARY_SOURCE = "primary source, refuse"
OPTIONAL_SECONDARY = "optional secondary, degrade and state the narrowing"

ROLES = {
    "case_study_render": (PRIMARY_SOURCE, "produces retained case-study page evidence"),
    "deck_render": (PRIMARY_SOURCE, "produces retained slide evidence"),
    "discussion_post_render": (PRIMARY_SOURCE, "produces retained initial-post page evidence"),
    "guidelines_extract": (PRIMARY_SOURCE, "reads the guideline corpus"),
    "split_census": (PRIMARY_SOURCE, "reads the corpus split census"),
    "guidelines_recs": (PRIMARY_SOURCE, "reads recommendation source documents"),
    "guidelines_build": (PRIMARY_SOURCE, "builds the guideline corpus artifacts"),
    "threshold_sheet": (OPTIONAL_SECONDARY, "uses PDF reading only for tier 2 corroboration"),
    "render_scan": (OPTIONAL_SECONDARY, "grades retained render evidence"),
    "discussion_post_scan": (OPTIONAL_SECONDARY, "grades retained post images"),
}


DECLARED_LIMITS = {
    "role-correctness": "A declaration does not establish that a consumer has the right role.",
    "engine-object-leakage": "The AST walk does not establish that an adapter never leaks an engine object.",
    "image-probe-window": "The inherited 60-byte image-probe acceptance window is not closed.",
    "decode-resolution": "A decode at the probe DPI does not establish decoding at reading resolution.",
    "guidelines-extract-split": "Guidelines extraction still owns PDF extraction and page reconstruction.",
    "consumer-contract": "The consumer-facing install contract is not changed here.",
    "threshold-gates": "The three unlocked threshold_sheet gates in issue #410 remain out of scope.",
}
