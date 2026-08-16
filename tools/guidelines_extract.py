"""Extract per-page text from the guideline PDF corpus and strip page-repeated boilerplate.

phi-scan: synthetic

The pragma is here because PRINT_CAPTURE_STAMP's comment quotes the browser print
header off a public CDC page, and that header is date-shaped. Writing it in pieces
to slip past the scanner would dodge the rule without declaring anything. The
corpus layer is untouched by this and still applies.

    python tools/guidelines_extract.py <source-directory> [--out <directory>]

``<source-directory>`` is the corpus as downloaded: one subdirectory per society,
PDFs inside. It lives outside this repo and stays there -- 179 files, 410 MB, most
of them society-copyrighted. Issue #87 rules on that and is not reopened here.

**Nothing this writes goes inside the repo, and the script refuses to.** Output
defaults to a sibling of the source directory (``guidelines-src`` next door becomes
``guidelines-text``). ``reference/`` and ``scratch/`` are both wrong for it for the
same reason: tracked files are materialized in every worktree and gitignored ones
are copied into every worktree, and there are six live.

**Maintainer-only, and that is what buys the dependency.** Everything else in
``tools/`` is stdlib. This reads PDFs, so it needs ``pypdf``, and it runs once per
corpus refresh rather than on anything a consumer does. The dependency must not
leak: the artifacts downstream tickets read are the ``.txt`` files this emits.

**Why pypdf and not PyMuPDF.** Both are importable here and ``fitz`` is roughly six
times faster. It also loses the spaces between words on the USPSTF files -- whole
sentences come back as ``primarycarebecauseofitshighsensitivity`` -- and 90 of the
179 documents are USPSTF. Reading order and word spacing decide whether a threshold
survives; six minutes against four does not.

**The boilerplate rule.** A line appearing on 75% or more of a document's sampled
pages is boilerplate, is stripped from every page, and is recorded per document so
the removal can be audited rather than believed. This is the point of the whole
script: every AHA/ACC file carries ``Downloaded from http://ahajournals.org by on
August 12, 2026``, and strings like it sit in the page's reading order -- they can
land between a table row's label and its number, which is the one thing a threshold
sheet cannot survive.

**Known limits, stated so nobody reads more into the output than is there.**

- **A running head carrying its own page number is not caught.** ``pypdf`` folds
  the folio into the head line, so the string differs page to page. Masking digits
  would catch it and would also reach a repeated table row, which is the trade this
  refuses to make.
- **Hyphenation at a line break is left alone.** ``speci-`` / ``ficity`` stays two
  lines. Rejoining it needs a lexicon to avoid welding real compounds together, and
  the indexer (#84) is a better place to decide that than the extractor.
- **A page whose text layer is empty is recorded, not repaired.** No OCR anywhere;
  the survey found every sampled document carries an extractable layer.
- **The output is derived and lossy, and the PDFs stay the source of record.**
  ``normalize`` deletes soft hyphens and icon glyphs and folds curly quotes to
  ASCII, none of which can be undone from the text. Anything downstream that needs
  the page as typeset has to go back to the PDF.
- **A re-run overwrites but never deletes.** Rename a source file and the old
  ``.txt`` stays behind, claimed by no manifest entry. The summary names orphans
  rather than removing them: this is the maintainer's directory, and a tool that
  deletes from it on the strength of a glob is a worse trade than a printed list.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent

# Written with an explicit codec on every call and recorded in the manifest. This
# is not ceremony: the en dash in "130-139 mm Hg" survives extraction intact and
# then dies on the way out, because the default encoding on a Windows console is
# cp1252 and cannot represent it. A recorded codec is how that stays visible.
OUTPUT_CODEC = "utf-8"

PAGE_SEPARATOR = "\f"
MANIFEST_NAME = "manifest.json"

# A line has to clear both bars. The percentage is #80's rule verbatim.
#
# **The occurrence floor is a deliberate departure from that rule, and the only
# one.** Every line of a one-page document appears on 100% of its pages, so the
# percentage alone strips such a document to nothing and records it as clean. The
# floor binds only where 75% of the sampled pages is fewer than 3 -- documents of
# 1, 2 or 3 pages -- and is arithmetically inert above that. Corpus impact at the
# time of writing is one 2-page file. #100 holds the question of widening the rule;
# this narrows it, in the one place where not narrowing it destroys a document.
BOILERPLATE_THRESHOLD = 0.75
MINIMUM_OCCURRENCES = 3

# Sample evenly across the document rather than off the front: covers, contents
# and reference pages carry no running head, so a front-loaded sample of a
# 400-page report concludes there is no boilerplate in it.
#
# #80's floor is 8 pages. SAMPLE_SIZE sits well above it because sampling costs
# nothing here -- the pages are already extracted and in memory by the time the
# rule runs -- and a wider sample puts the measured rate closer to the true one.
SAMPLE_SIZE = 32
MINIMUM_SAMPLE = 8

CLASS_GUIDELINE = "guideline"
CLASS_PRINT_CAPTURE = "print-capture"
# For a document that was never read. It is not a guideline; nobody knows what it
# is, and recording it as the default class would let a failure read as a finding.
CLASS_UNKNOWN = "unknown"

# The three ACIP/ files are browser print-to-PDF captures of CDC schedule pages
# rather than guideline documents, and this header is what says so. The URL and
# the "n of m" folio come with it, but a guideline PDF can carry a repeated URL
# footer -- KDIGO does -- so only the timestamp is allowed to decide.
#
# Anchored at the start of the line and not at both ends. pypdf folds the page
# title in after the stamp, so the real line reads "8/12/26, 10:25 AM Recommended
# Vaccinations for Adults | ... | CDC". Requiring the whole line matched the
# fixture and none of the three real files, which is what the fixture now looks
# like. Still anchored at the front: a date and time part way through a sentence
# is prose, and this must not read a guideline as a browser capture.
PRINT_CAPTURE_STAMP = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\b")

# Characters that are noise or that render as something else, replaced explicitly
# rather than by a normalization form. NFKC would do most of this and would also
# turn a superscript footnote marker into a digit, which next to a threshold reads
# as part of the number.
#
# Written as code points, never as literals. Most of these are invisible and the
# rest are eight dashes nothing in a monospace editor tells apart, so a literal here
# is a constant nobody can review. Each one is asserted by number in
# test_guidelines_extract.py rather than taken on trust.
_DASHES = (
    0x2010, 0x2011,  # hyphen, non-breaking hyphen
    0x2012, 0x2013, 0x2014, 0x2015,  # figure dash, en dash, em dash, horizontal bar
    0x2212, 0x2043,  # minus sign, hyphen bullet
)
_SPACES = (
    0x00A0, 0x1680,  # no-break space, ogham space mark
    *range(0x2000, 0x200B),  # the en quad through hair space family
    0x202F, 0x205F, 0x3000,  # narrow no-break, medium mathematical, ideographic
)
_DELETED = (
    0x00AD,  # soft hyphen: invisible, and splits a word the index needs whole
    0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF,  # zero-width space, joiners, word joiner, BOM
    *range(0x200E, 0x2010), *range(0x202A, 0x202F),  # bidi controls
)
_LIGATURES = {
    0xFB00: "ff",
    0xFB01: "fi",
    0xFB02: "fl",
    0xFB03: "ffi",
    0xFB04: "ffl",
    0xFB05: "st",  # long s with t
    0xFB06: "st",
}
_QUOTES = {
    0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'", 0x2032: "'",
    0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"', 0x2033: '"',
}

_TRANSLATION = {
    **{code: "-" for code in _DASHES},
    **{code: " " for code in _SPACES},
    **{code: None for code in _DELETED},
    **_LIGATURES,
    **_QUOTES,
    0x2026: "...",  # horizontal ellipsis
    0x0009: " ",  # tab
}

# Whole ranges that come out empty rather than mapped. The controls are extractor
# debris -- U+0008 turns up after the issue date on every AHA/ACC page. The private
# use areas are icon-font glyphs: a chevron or a padlock, carrying no text at all.
#
# U+000A survives because page_lines splits on it. U+000C does not need to: the page
# separator is written by build_document, not carried through normalize.
_DISCARDED_RANGES = (
    (0x0000, 0x0008), (0x000B, 0x001F), (0x007F, 0x009F),  # C0 and C1, keeping U+000A
    (0xE000, 0xF8FF),  # private use area
    (0xF0000, 0x10FFFF),  # supplementary private use areas A and B
)
_DISCARDED = re.compile(
    "[" + "".join(f"{re.escape(chr(lo))}-{re.escape(chr(hi))}" for lo, hi in _DISCARDED_RANGES) + "]"
)

_WHITESPACE = re.compile(r"[ \t]+")


def normalize(text: str) -> str:
    """One page of extracted text, with its typography made searchable.

    Every mapping here is deliberate and none of them touch a character a
    threshold is written with: the comparison operators, the degree sign, the micro
    sign and the plus-minus sign all pass through untouched, with a test for each.
    """
    text = _DISCARDED.sub("", text.translate(_TRANSLATION))
    text = unicodedata.normalize("NFC", text)
    return _WHITESPACE.sub(" ", text).strip()


def page_lines(page_text: str) -> list[str]:
    """A page as its non-empty normalized lines.

    Blank lines are dropped rather than kept, because a blank line matches every
    other blank line: left in, ``""`` is the most frequent line in every document
    and therefore boilerplate in all of them.
    """
    return [line for line in (normalize(raw) for raw in page_text.splitlines()) if line]


def clean_pages(raw_pages: list[str]) -> list[list[str]]:
    return [page_lines(page) for page in raw_pages]


def sample_indexes(page_count: int) -> list[int]:
    """Which pages the boilerplate rule looks at. Evenly spaced, or all of them."""
    size = max(SAMPLE_SIZE, MINIMUM_SAMPLE)
    if page_count <= size:
        return list(range(page_count))
    step = page_count / size
    return sorted({int(index * step) for index in range(size)})


def find_boilerplate(pages: list[list[str]]) -> list[str]:
    """The lines this document repeats on 75% or more of its sampled pages.

    Sorted, because the result is recorded in a manifest that gets diffed across
    rebuilds and set iteration order would make every rebuild look like a change.
    """
    sampled = sample_indexes(len(pages))
    if not sampled:
        return []
    counts: dict[str, int] = {}
    for index in sampled:
        # A page votes once per distinct line. Otherwise a two-column page whose
        # column headers repeat reads as two pages' worth of evidence.
        for line in set(pages[index]):
            counts[line] = counts.get(line, 0) + 1
    floor = max(MINIMUM_OCCURRENCES, BOILERPLATE_THRESHOLD * len(sampled))
    return sorted(line for line, count in counts.items() if count >= floor)


def strip(pages: list[list[str]], boilerplate: list[str]) -> list[list[str]]:
    """Every page with the boilerplate lines removed, and no page removed."""
    removed = set(boilerplate)
    return [[line for line in page if line not in removed] for page in pages]


def classify(pages: list[list[str]]) -> str:
    """Whether this is a guideline document or a browser print-to-PDF capture.

    Counted over the sampled pages directly rather than read off the boilerplate
    set. Those look interchangeable on the three real captures, where the stamp is
    on every page and clears every bar -- but reading the boilerplate set makes the
    class a side effect of boilerplate detection, so a capture short enough to trip
    MINIMUM_OCCURRENCES, or one whose stamp missed the threshold by a page, would
    come back a guideline with nothing saying otherwise.
    """
    sampled = sample_indexes(len(pages))
    if not sampled:
        return CLASS_GUIDELINE
    stamped = sum(
        1
        for index in sampled
        if any(PRINT_CAPTURE_STAMP.match(line) for line in pages[index])
    )
    if stamped >= BOILERPLATE_THRESHOLD * len(sampled):
        return CLASS_PRINT_CAPTURE
    return CLASS_GUIDELINE


@dataclass(frozen=True)
class Record:
    """One document's manifest entry. ``output`` is None exactly when it failed.

    Everything but ``doc_id`` defaults to the nothing-was-read state, so a failure
    is ``Record(doc_id=..., error=...)`` and a field added later does not have to
    be spelled out twice in two constructors that must not disagree.

    ``doc_id``, ``society``, ``title`` and ``document_class`` are the four fields
    #84's indexer reads (`tools/guidelines_index.py`), and ``doc_id`` is the key it
    matches a document by. The rest is this tool's own audit trail. A failed
    document still gets an entry with a ``doc_id``: the indexer reports a manifest
    entry it found no text for on stderr, which is exactly this tool's recorded
    extraction failure surfacing rather than a silent skip on either side.
    """

    doc_id: str
    society: str | None = None
    title: str | None = None
    source: str = ""
    output: str | None = None
    document_class: str = CLASS_UNKNOWN
    pages: int = 0
    empty_pages: int = 0
    chars: int = 0
    chars_stripped: int = 0
    sampled_pages: int = 0
    codec: str = OUTPUT_CODEC
    boilerplate: list[str] = field(default_factory=list)
    error: str | None = None


def document_id(relative: Path) -> str:
    """The key #84 matches a document by: the relative path, no suffix, posix.

    Its first segment is the society, which is how a hit names a file that can be
    opened beside the PDF of the same name.
    """
    return relative.with_suffix("").as_posix()


def society_of(doc_id: str) -> str | None:
    return doc_id.split("/")[0] if "/" in doc_id else None


def build_document(
    relative: Path, raw_pages: list[str], out_root: Path, title: str | None = None
) -> Record:
    """Normalize, strip, write one text file, and describe what was done to it."""
    pages = clean_pages(raw_pages)
    boilerplate = find_boilerplate(pages)
    kept = strip(pages, boilerplate)

    chars = sum(len(line) for page in pages for line in page)
    chars_kept = sum(len(line) for page in kept for line in page)

    destination = out_root / relative.with_suffix(".txt")
    destination.parent.mkdir(parents=True, exist_ok=True)
    body = ("\n" + PAGE_SEPARATOR + "\n").join("\n".join(page) for page in kept)
    destination.write_text(body + "\n", encoding=OUTPUT_CODEC, newline="\n")

    doc_id = document_id(relative)
    return Record(
        doc_id=doc_id,
        society=society_of(doc_id),
        title=title,
        source=relative.as_posix(),
        output=relative.with_suffix(".txt").as_posix(),
        document_class=classify(pages),
        pages=len(pages),
        empty_pages=sum(1 for page in pages if not page),
        chars=chars,
        chars_stripped=chars - chars_kept,
        sampled_pages=len(sample_indexes(len(pages))),
        codec=OUTPUT_CODEC,
        boilerplate=boilerplate,
        error=None,
    )


def failed_document(relative: Path, error: str) -> Record:
    """A document that could not be read. Recorded, never skipped."""
    doc_id = document_id(relative)
    return Record(
        doc_id=doc_id,
        society=society_of(doc_id),
        source=relative.as_posix(),
        error=error,
    )


def extract_pages(path: Path) -> tuple[list[str], str | None]:
    """Every page of a PDF as raw text in reading order, and its embedded title.

    A page that raises comes back as an empty string rather than taking the
    document down with it -- the manifest counts it, and one unreadable page in a
    250-page report is not a failed extraction.

    The title is ``/Title`` verbatim, or None. **Verbatim and unfiltered**: 147 of
    the 179 carry one and they are real guideline titles, measured 2026-08-12, but
    the rest include the usual ``Microsoft Word - ...`` debris. Inventing a
    junk-detection heuristic here would put an unreviewable rule between the PDF
    and the record; curating them is the catalog's job (#81).
    """
    import pypdf  # imported here so the pure functions above stay importable without it

    reader = pypdf.PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001 - any per-page failure degrades to an empty page
            pages.append("")

    try:
        title = ((reader.metadata or {}).get("/Title") or "").strip() or None
    except Exception:  # noqa: BLE001 - a broken metadata dictionary is not a failed read
        title = None
    return pages, title


def _engine_version() -> str:
    try:
        import pypdf

        return f"pypdf {pypdf.__version__}"
    except ImportError:
        return "pypdf (not installed)"


def require_pypdf() -> None:
    """Fail once, up front, rather than 179 times.

    Every per-document failure is caught and recorded, which is what #80 asks for
    -- so without this an uninstalled ``pypdf`` reads as 179 unreadable PDFs and a
    manifest full of identical ImportErrors, next to a summary line cheerfully
    reporting the engine as not installed.
    """
    try:
        import pypdf  # noqa: F401
    except ImportError:
        raise SystemExit(
            "pypdf is not installed. This is the one tool in tools/ that is not "
            "stdlib, because it is the only one that reads a PDF:\n"
            "    python -m pip install pypdf"
        ) from None


def orphaned_outputs(out_root: Path, records: list[Record]) -> list[Path]:
    """Text files under the output root that no record in this run claims.

    A re-run overwrites what it writes and knows nothing about what it wrote last
    time, so renaming a source file leaves its old ``.txt`` behind. #84 will index
    the directory, not the manifest, and would pick the stale copy up.
    """
    claimed = {(out_root / record.output) for record in records if record.output}
    return sorted(path for path in out_root.rglob("*.txt") if path not in claimed)


def write_manifest(out_root: Path, records: list[Record], source_root: Path) -> Path:
    """The audit trail, and #84's input. One entry per document, in source order.

    ``documents`` is the **list of entries**, which is the shape
    ``guidelines_index.read_manifest`` requires -- it does ``data.get("documents")``
    and raises unless what comes back is a list. The run totals live under
    ``totals`` for that reason: ``"documents": 179`` as a count read as a manifest
    of the wrong shape, and the indexer raised rather than indexing 179 documents
    with no title, society or class. That refusal is the contract working.
    """
    manifest = {
        "source": str(source_root),
        "codec": OUTPUT_CODEC,
        "engine": _engine_version(),
        "boilerplate_threshold": BOILERPLATE_THRESHOLD,
        "minimum_occurrences": MINIMUM_OCCURRENCES,
        "totals": {
            "documents": len(records),
            "failures": sum(1 for record in records if record.error),
            "pages": sum(record.pages for record in records),
            "chars": sum(record.chars for record in records),
        },
        "documents": [asdict(record) for record in records],
    }
    path = out_root / MANIFEST_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding=OUTPUT_CODEC,
        newline="\n",
    )
    return path


def default_output(source: Path) -> Path:
    """A sibling of the source directory, never a child of the repo."""
    name = source.name
    stem = name[: -len("-src")] if name.endswith("-src") else name
    return source.parent / f"{stem}-text"


def check_outside_repo(out_root: Path) -> None:
    """Refuse an output directory inside any git checkout, not just this one.

    ``REPO_ROOT`` alone is not enough. Run from a worktree it is the worktree, so
    it says nothing about the main clone's ``reference/`` -- and that is one of the
    two directories #80 names by name. Walking up for a ``.git`` entry catches the
    main clone, every sibling worktree, and any other repo the maintainer keeps
    nearby. A worktree's ``.git`` is a file rather than a directory, so this tests
    for existence and not for a directory.
    """
    resolved = out_root.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / ".git").exists():
            raise SystemExit(
                f"refusing to write inside a git checkout: {resolved}\n"
                f"  {candidate} is a repository.\n"
                "Tracked files are materialized in every worktree and gitignored ones "
                "are copied into every worktree. Pick a directory outside it."
            )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="directory holding the guideline PDFs")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory, outside the repo (default: a sibling of <source>)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="summary only, no per-document line"
    )
    args = parser.parse_args(argv)

    if not args.source.is_dir():
        raise SystemExit(f"not a directory: {args.source}")
    require_pypdf()

    source_root = args.source.resolve()
    out_root = (args.out or default_output(source_root)).resolve()
    check_outside_repo(out_root)

    pdfs = sorted(source_root.rglob("*.pdf"), key=lambda p: p.relative_to(source_root).as_posix())
    if not pdfs:
        raise SystemExit(f"no PDFs under {source_root}")

    records: list[Record] = []
    for path in pdfs:
        relative = path.relative_to(source_root)
        try:
            raw_pages, title = extract_pages(path)
            records.append(build_document(relative, raw_pages, out_root, title))
        except Exception as error:  # noqa: BLE001 - a failure is recorded, never skipped
            records.append(failed_document(relative, f"{type(error).__name__}: {error}"))
        if not args.quiet:
            # `use_utf8` in `__main__` is what keeps a society directory or a file
            # name outside cp1252 from taking the run down at the print, having
            # already done the work. This used to encode by hand through
            # `sys.stdout.buffer`, which did the same job for this one line and left
            # every other print in the file exposed -- issue #150. `flush` stays: it
            # is progress output over 179 documents, not encoding.
            print(f"  {records[-1].source}", flush=True)

    manifest = write_manifest(out_root, records, source_root)

    failures = [record for record in records if record.error]
    captures = sum(1 for r in records if r.document_class == CLASS_PRINT_CAPTURE)

    print()
    print(f"source      {source_root}")
    print(f"output      {out_root}")
    print(f"engine      {_engine_version()}, codec {OUTPUT_CODEC}")
    print(f"documents   {len(records):,}  ({captures} print-capture)")
    print(
        f"pages       {sum(r.pages for r in records):,}  "
        f"({sum(r.empty_pages for r in records):,} with no text layer)"
    )
    print(
        f"chars       {sum(r.chars for r in records):,}  "
        f"({sum(r.chars_stripped for r in records):,} stripped as boilerplate)"
    )
    print(
        f"boilerplate {sum(1 for r in records if r.boilerplate):,} of {len(records):,} "
        "documents carry a page-repeated line"
    )
    print(f"manifest    {manifest}")

    orphans = orphaned_outputs(out_root, records)
    if orphans:
        print()
        print(f"ORPHANED {len(orphans)} text file(s) no source in this run claims.")
        print("Left in place deliberately -- delete them yourself once you have looked:")
        for path in orphans:
            print(f"  {path.relative_to(out_root).as_posix()}")

    if failures:
        print()
        print(f"FAILED {len(failures)}:")
        for record in failures:
            print(f"  {record.source}: {record.error}")
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
