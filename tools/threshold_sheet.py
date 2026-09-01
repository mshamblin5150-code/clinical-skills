"""Grade a distilled threshold sheet against the guideline it claims to come from.

    python tools/threshold_sheet.py <sheet.md> [--recs <key>=<recs.json> ...] [--pdf-root <dir>]
    python tools/threshold_sheet.py <sheet.md> --brief --span <name>
    python tools/threshold_sheet.py <sheet.md> --second-read <read.json>
    python tools/threshold_sheet.py --all

This is #83's gate set. A threshold sheet is the deliverable of the #80 series: per
topic, the decision points only -- drug, dose, duration, target number, referral and
follow-up threshold, staging cutoff. Facts are not copyrightable and expression is,
so a restated staging table is a thing this repo may hold and a dumped PDF is not.

**The failure being defended against is the one this repo trusts least**: an agent
producing fluent, plausible, confident text from a source only it has read. Nothing
here checks that a guideline was *understood*. Each gate eliminates one way a sheet
can be confidently wrong.

The gates, and what each one can and cannot see
------------------------------------------------

**It was four until [#174](https://github.com/mshamblin5150-code/clinical-skills/issues/174).**
#83 listed five under *"Independent, worth building"* and built three; the two below
marked gate 4 and gate 5 are the rest of that list, and the ``RENDERED:`` marker had
been shipping the *declaration* half of gate 4 since #83 with nothing detecting that a
row needed it.

``SCHEMA``  refuses
    Structural. Every row has all eight columns, a population key drawn from the
    sheet's own declared vocabulary, no non-ASCII comparison character in its value,
    and a source key that the Sources table defines. Every source carries its catalog
    source class, a version, a publication date, an HTTP(S) Download address, and its
    ruled Download basis. The sheet has a ``## Scope`` section saying both
    what was read and what was **not**. **And the conflict rule**: two rows sharing a
    quantity key AND a population key with different values must be covered by a
    ``CONFLICT`` block for that quantity. Needs nothing but the sheet, so it runs
    everywhere and always.

    **The conflict floor reads the block's prose.** Every distinct conflicting row
    value must appear there, with ordinary inequality wording (for example, ``below``
    for ``<``) normalized before comparison. This does not verify that the explanation
    is clinically correct; it prevents an empty block, ``TODO``, or a paragraph that
    names only one side from discharging the structural rule.

``PAGE COVERAGE`` refuses, and prints the remainder on every run
    The union of each source's named span ranges covers ``1..page_count`` from the
    committed guideline catalog. Overlap is allowed. An unresolved count is not
    graded rather than passed. The check catches an omitted span, not a boundary
    drawn around the wrong pages; ``PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES``
    declares that limit beside the code.

``CITATION`` refuses, in three tiers
    Tier 0 checks that every recommendation snippet from an exact source is a
    substring of its own recommendation record. For a narrative locator it runs in
    reverse and refuses when the page transcription is already inside a
    recommendation record on the same page. It reports ``NOT RUN`` on a bound source
    and never passes one. Tier 1 runs everywhere: the number in a row's ``value`` must
    appear in that row's ``snippet``. Tier 2 runs only where the PDFs are present: the
    snippet must appear on the cited page. There is no machine on which citation
    checking drops to zero. Its resolution declaration is required in both tier 2
    states; a live verdict also refuses when that declaration names a different corpus
    or a future date, while a skipped verdict cannot check its content. Tier 0 is a
    provenance floor, not a reading: it cannot decide whether the snippet is the right
    text for the row.

``COVERAGE`` refuses on an exact source, warns on a bound
    #83 gate 2, the omission check: *"everything else checks what was written, only
    this checks what was not."* Every recommendation identifier the source carries
    is a recommendation row or is scoped out by ``rec_id``. A narrative source
    locator sits outside that index and cannot discharge an omission. On an exact
    source, a recommendation identifier absent from its record refuses too. Whether
    omission may refuse is decided by ``guidelines_recs.py``'s mode and never by this
    module: an exact count can be enforced, a marker bound over-reports and can only
    warn. Every run prints the narrative qualifier because the span table, rather than
    any prose denominator, is what bounds those rows.

    **One recommendation record per SOURCE, not per sheet** --
    [#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177). It took
    one ``--recs`` for the whole sheet and never filtered ``known`` by ``row.source``,
    so a sheet citing two societies had the named source's omissions checked and the
    other's silently not; the count that would have surfaced it was derived from
    ``recs is None`` and could not exceed 1 however many sources were skipped. #83
    decision 3 makes multi-source the normal case -- one row per society with a
    ``CONFLICT`` block where they disagree -- so the first sheet carrying ADA beside
    AHA/ACC would have hit it, and hit it reading green. ``--recs`` is
    ``<source key>=<path>`` now. Without it, the sweep alias resolves
    ``<doc_id>.json`` first and ``--recs-root`` fills a gap with exact
    ``recs-<source key>.json`` lookup. A record absent from both warns loudly and exits
    0 on #181's ruling; an explicit path that does not resolve, an unreadable record,
    or any refusal from a record that is present remains non-zero.

``WATERMARK`` refuses, and skips loudly where the extracted corpus is absent
    #83 gate 4: *"If a string stripped by #80 appears inside an extracted table row,
    that row is suspect and must be read off the rendered page. Cannot verify a
    reading; flags every place the text stream was interleaved."* The strings are
    read from ``manifest.json`` -- **both** ``boilerplate`` and ``margin_stripped``,
    because a detector reading only the first misses #100's whole margin rule, which
    is this gate's own failure shape arriving in this gate's input.

    **A stripped string is a usable probe only where it does not otherwise occur in
    the document's own body**, and that discrimination is measured rather than
    chosen -- see ``usable_probes`` for why no length or letter-run cut point can
    do it. A declared ``RENDERED:`` row is exempt and counted: reading it off the
    rendered page is the remedy #83 names, and refusing a row that applied it would
    leave the gate unsatisfiable.

    **Refuses until a working agent checks the rendered page.** The clinician ruled
    on [#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296) that
    routine visual confirmation belongs to the agent rather than becoming a
    clinician bottleneck. The agent renders the cited page, confirms the row, and
    records that check with ``RENDERED:``; an incorrect or ambiguous row stays
    refusing until it is corrected.

``NULL SPAN`` refuses
    A span retired on ``read YYYY-MM-DD`` claims that its read found no decision
    point. The same cell must carry ``; blind YYYY-MM-DD`` to record the required
    cold corroboration. The dates may be equal. The gate reports both its retired-span
    denominator and how many carry corroboration on every run; ``exempt:`` spans are
    outside that population because retirement by class is not a read.

``SECOND READ`` refuses on a disagreement, and runs only when one is handed to it
    #83 gate 5: *"A subagent extracts the same table with no access to the sheet;
    the diff is the gate. The only mechanism that catches misreading rather than
    miscitation."* ``--brief --span`` prints the work order -- document, span name,
    and page range and nothing else from the sheet -- and ``--second-read`` diffs the
    result against that span.

    **The two directions are deliberately asymmetric.** A value found in a span the
    sheet retired as null refuses. A reader miss where the sheet carries a row warns,
    because the row already carries a snippet located by the citation gates and a
    second reader's miss must not overturn it.

    **#83's caveat is a build instruction and #174 says so**: correlated error --
    same model, same PDF, same mangling, same wrong answer -- means the *pass* is
    cheap. It does not mean the *fail* is, because correlation does not manufacture
    a disagreement. So a disagreement refuses, and ``SECOND_READ_IS_A_SMOKE_TEST``
    prints on a clean run, which is the only run anybody could mistake for proof.

    **The diff is on numbers and the misreading limb is a pairing nobody grades.**
    The row's ``quantity`` and ``population`` are printed beside what the
    independent reader said the number was **about**, for a reader to compare. That
    is the hole named two sections down, narrowed to a reading rather than closed.

``RANGE``   refuses
    Per-quantity bounds. A BP target of 1300, an eGFR of 450, a dose three orders of
    magnitude off. Decimal-place and unit errors are the highest-consequence
    extraction failures and the cheapest to catch, because catching them needs no
    understanding of the guideline at all. **It also refuses a value carrying a
    character that is not a comparison operator** -- a Symbol-font ``\u00a3`` or
    ``\u2021`` where the source meant ``<=`` or ``>=``. The mis-encoded slots are
    imported from ``guidelines_extract.SYMBOL_FONT_OPERATORS`` rather than listed
    here. Destructive C0 slots are refused from the raw sheet before ``splitlines`` or cell
    trimming can erase them; the rest are refused from the parsed value.

What no gate here reaches, stated the same day the gates were built
--------------------------------------------------------------------

The complete module-wide inventory is ``threshold_sheet.DECLARED_LIMITS``; this
docstring points there and copies no row. Its population was derived by an end-to-end
read of this module and its ratified records on 2026-08-30. A limit written only as
later prose remains reader-owned.

**Deliberately not built, because it would pass for the wrong reason**: any gate
that re-extracts a value and compares it to the sheet through the path that wrote
the sheet. ``tools/test_icd10.py`` runs against committed excerpts and never against
the shipped database for precisely this reason. It is the most natural check to
write here and it is worthless.

**``SECOND READ`` is the exception that proves that rule rather than a breach of
it, and the line between them is the only thing holding it.** It re-extracts, and
what makes it worth anything is that this module **does not perform the read** --
``gate_second_read`` grades a record somebody else produced and there is no code
path here that can produce one. A ``--second-read`` this module generated would be
the same code over the same page, which is the check named worthless above; that is
why ``--brief --span`` prints a work order for a reader instead of doing the work.

Exit status
-----------

``0`` no refusing finding. This includes a recommendation record that was never built
under ``--recs-root``: COVERAGE prints ``NOT RUN`` through ``--quiet`` and calls the
result a warning, never a clean COVERAGE pass. ``1`` a gate that refuses found
something. ``2`` every other way of not having graded -- no sheet, a zero-row sheet
with no declaration, an
unreadable Sources table, no record lookup requested, an explicit ``--recs`` path that
does not resolve, an unreadable record, a ``--recs`` argument naming a source the sheet
does not declare, a ``--second-read`` that was asked for and did not load, **and one
that loaded and diffed no row at all** -- a record whose entries all land on pages the
sheet cites nowhere made every row *uncovered* and printed ``0 refusing, 0 warning``,
which is byte for byte what a clean diff prints.
**An absent extracted corpus is deliberately NOT one of them**: ``WATERMARK`` skips
with a banner on ``CITATION`` tier 2's terms rather than ``COVERAGE``'s, because
making it a refusal would add a second reason the pre-commit hook turns away someone
fixing a prose typo -- a cost ``reference/thresholds/README.md`` already names as
landing on people who have done nothing wrong. A sheet whose rows were written in a shape the parser does not read
would otherwise report zero violations and look like a pass, which is
`differential_scan.py`'s ruling and the shape #153 caught in the wild at 2.4%
coverage reading green.

Where 1 and 2 both hold, **1 wins**, and the message names every source that was not
graded so the finding reads as a floor rather than the whole.

Stdlib only. Tier 2 needs ``pymupdf`` and says ``SKIPPED`` without it rather than
failing, which is the same hole -- named here rather than discovered later.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import NamedTuple

import guidelines_extract
import guidelines_manifest
import guidelines_catalog
import artifact_provenance
from console_codec import use_utf8
from guidelines_recs import (
    EvidenceDisposition,
    MODE_BOUND,
    MODE_EXACT,
    RecommendationRecordLocation,
    RecommendationRecordOrigin,
    UntrustedRecommendationRecord,
    locate_recommendation_record,
    load_recommendation_record,
    record_built_from_another_document,
)


@dataclass(frozen=True)
class BoundRecommendationRecords:
    records: dict[str, dict | None]
    why_not: dict[str, str]
    errors: list[str]
    missing_records: set[str]
    untrusted_records: set[str]
    locations: dict[str, RecommendationRecordLocation]

    @property
    def origins(self) -> dict[str, str]:
        return {
            key: location.description for key, location in self.locations.items()
        }

    def __iter__(self):
        yield self.records
        yield self.why_not
        yield self.errors
        yield self.missing_records

REPO_ROOT = Path(__file__).resolve().parent.parent
SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_PDF_ROOT = Path("C:/codeing/guidelines-src")

# Where `recs-<key>.json` is looked for when `--recs-root` is not given. A module
# constant rather than an inline default so the literal can be graded: an env var
# can change what `parse_args` produces, and a test reading that would be measuring
# the machine it ran on.
DEFAULT_RECS_ROOT = "C:/codeing/guidelines-index"
DEFAULT_RECS_ALIAS = str(Path(DEFAULT_RECS_ROOT).parent / "guidelines-recs")
RECS_ALIAS_ENV = "CLINICAL_GUIDELINES_RECS_ALIAS"

# **This module takes no write guard, and #176 asked for that to be a decision
# rather than an absence** -- its own first comment: *"an absent guard is easy to
# read as an oversight when it is a choice."* Ruled during the limit consolidation
# on 2026-08-19.
#
# The three writers and `name_index` all refuse a *write* inside a checkout. This
# module only ever reads: `bind_recs` opens `<doc_id>.json` from the sweep alias or
# `recs-<key>.json` from the recs root, and nothing here creates either. Guarding a
# read would refuse a record that already exists, which
# prevents nothing -- whatever put it there was the guarded step, and refusing to
# read it turns one module's escaped artifact into a second module's failure.
#
# **What is enforceable is the default, and one property of it is.** A *relative*
# default resolves against the working directory, and the working directory when
# these tools are run is a checkout -- so a relative default is the convention
# encoded wrong, silently, in the one place the ticket named as encoding it
# without enforcing it. `test_write_guards.py` grades that.
#
# **What is not enforceable is the value.** `DEFAULT_RECS_ROOT` names a directory
# on the maintainer's machine, and asserting `enclosing_checkout` finds no
# checkout above it would be asserting a fact about *that* machine -- on a POSIX
# runner the drive-letter form resolves under the working directory and the check
# would fail for a reason that has nothing to do with the convention. Declared
# rather than half-checked.
WHY_NO_WRITE_GUARD = (
    "threshold_sheet reads recs-<key>.json and never writes one, so it takes no "
    "write guard. What it shares with the other write-guarded commands is the "
    "convention about where such a record lives, and the enforceable half of that "
    "is that its default is absolute -- a relative one would resolve inside the "
    "checkout the command was run from."
)

# A text-marker record is a bound in both directions: it over-reports when prose
# happens to match the marker, and it can under-report a real recommendation whose
# wording does not. Absence from that record therefore proves nothing about a row's
# identifier. The clinician ruled #270 on 2026-08-20, following #298's shape: narrow
# membership enforcement to the source class where absence is dispositive, then
# refuse there; leave every other class alone rather than turning an extractor
# limitation into a sheet finding.
WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED = (
    "A text-marker recommendation record can under-report a recommendation the "
    "sheet author read in the PDF. Membership is graded only for exact records, "
    "where an absent identifier is dispositive."
)

SCHEMA_MARKER = "<!-- schema: threshold-sheet/2 -->"

# Page coverage proves that every page was assigned to a named span. It cannot prove
# that the boundary was drawn correctly: a references span beginning one page too
# late can still leave that page covered by the preceding, wrongly named span.
PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES = (
    "page coverage catches an omitted span, not a misdrawn one"
)

# The escape hatch #83 asks for by name: *"Table-derived values need an escape hatch
# on the `phi-scan: synthetic` pattern: a per-row annotation meaning read off the
# rendered page, extraction garbles this table. Declaring it is a deliberate act that
# leaves a trace."*
#
# A snippet beginning with this marker means the value was read off the PAGE AS
# TYPESET and not out of the text layer, so tier 2 cannot resolve it -- the string on
# the rendered page is not the string extraction produces, which is the whole reason
# the row needs the hatch. Those rows are counted and printed rather than passed
# silently, which is the "leaves a trace" half.
#
# **Modeled on `phi-scan: synthetic` and narrowed the same way it was.** That pragma
# has to sit alone on its own line because a bare substring test let two files exempt
# themselves merely by explaining the rule. Here the marker must START the snippet
# cell, so a row discussing the hatch in its own text cannot claim it.
RENDERED_MARKER = "RENDERED:"
NARRATIVE_KIND = "narrative"
_SOURCE_LOCATOR = re.compile(
    r"^p(?P<page>\d+)/(?P<kind>[^/\s]+)/(?P<identifier>[^/\s]+)$"
)

# The section headings are part of the sheet format's production interface. The
# draft scaffolder imports these names so it cannot emit a section the auditor does
# not read after a heading rename.
SOURCES_HEADING = "## Sources"
SOURCE_COLUMNS = (
    "key",
    "society",
    "document",
    "source class",
    "version",
    "published",
    "url",
    "basis",
    "mode",
)
SCOPE_HEADING = "## Scope"
POPULATIONS_HEADING = "## Populations"
QUANTITIES_HEADING = "## Quantities"
THRESHOLDS_HEADING = "## Thresholds"
NONE_DECLARATION = (
    "**No decision point.** Every span in `## Scope` has left the unread list and "
    "this source states no quantity that changes what is done to a patient."
)
NON_SOURCE_DECLARATION = (
    "**Declared non-source.** Every span in `## Scope` has left the unread list and "
    "this source is a scope of work that states what a future guideline will cover."
)
DECLARED_NON_SOURCE_CLASSES = frozenset({"scope-of-work"})
CONFLICTS_HEADING = "## Conflicts"
COVERAGE_HEADING = "## Coverage"
SECTION_HEADINGS = (
    SOURCES_HEADING,
    SCOPE_HEADING,
    POPULATIONS_HEADING,
    QUANTITIES_HEADING,
    THRESHOLDS_HEADING,
    CONFLICTS_HEADING,
    COVERAGE_HEADING,
)

# The eight columns of a threshold row, in order. Named here rather than positionally
# in the parser so a column added later fails loudly in one place.
ROW_COLUMNS = ("quantity", "population", "value", "snippet", "source", "page", "rec", "class")

# The comparison operators a value may carry. ASCII only, and that is a rule about
# the corpus rather than about taste: two fonts in it render a comparison operator
# through a slot their own encoding does not describe, so what a reader hands back
# is a pound sign, a double dagger or a control code. A sheet is allowed to hold
# the fact and must not hold the mis-encoding, because those sort and compare
# differently from `<=` and only one of them is readable back to a clinician.
#
# **The mis-encoded slots are imported rather than listed**, on
# `test_spelling_scan.py`'s reasoning: `guidelines_extract` is where they are
# measured and where a sixth would be added, and a gate holding its own copy of
# that list is one that reads as agreement while covering less.
#
# **It covered less until #172.** Written by hand, it blocked `\u00a3` and `\u00b3` -- and
# `\u00b3` is a slot the corpus does not contain, while the double dagger carrying most
# of that corpus's greater-or-equal signs was not blocked at all. So the guard #172
# was told to rely on refused the character the ticket named and passed the one the
# ticket had missed. **Every count behind that sentence lives on
# `SYMBOL_FONT_OPERATORS` and none is restated here** -- a first draft of this
# comment copied two of them in, which is #143 arriving inside the paragraph
# arguing that a copied list reads as agreement while covering less.
#
# `\u00b3` stays. It is the Symbol font's greater-or-equal slot decoded through cp1252,
# which is what a *different* reader on a *different* machine would hand back from
# the same PDFs -- a sheet is transcribed by a person who may not be using this
# module's extraction at all.

# The extractor's destructive C0 slots must be refused before parsing. Their behavior is Python's
# doing rather than this module's, and `RawInputOperatorGate` in
# `tools/test_threshold_sheet.py` demonstrates each rather than asserting it:
#
#   U+001F  `str.strip()` counts U+001C to U+001F as whitespace, so `_cells`
#           removes it and the row reads as a bare number -- the corpus defect
#           reproduced inside the artifact built to refuse it.
#   U+001E  `str.splitlines()` breaks on it, so the row is two half-lines, neither
#           is a table row, and the sheet parses clean with the row simply gone.
#           That is worse than a wrong value: nothing is left to be wrong.
#
# #285 repairs neither Python operation. It refuses only these known operator slots
# in the raw input, preserving the sheet line and its source/page cells for an agent
# to verify against a rendered PDF page. It never guesses which operator was meant.
FORBIDDEN_IN_RAW_TEXT = {
    "\u001e": "line splitting would erase it with its row",
    "\u001f": "cell trimming would erase it",
}
# A blocklist and deliberately not an allowlist. An allowlist of operators was
# written here first and never referenced by any gate, while the docstring claimed
# it was enforced -- which is `test_spelling_scan.py`'s failure mode exactly: a rule
# that has drifted from the file a reader opens reads as agreement. It was removed
# rather than wired up, because a value legitimately carries no operator at all
# (`81 mg/day`, `monthly`, `3-6 months`) and an allowlist would have to permit the
# empty case, at which point it permits everything.
# How each of the extractor's replacements is written in ASCII, which is the form a
# value cell must use. A plain lookup rather than a conditional inside the message,
# for two reasons. A conditional labels every future replacement as whichever branch
# is the `else`, silently; a lookup raises. And a backslash inside an f-string
# *expression* is a syntax error before 3.12 -- the first version of this wrote
# `f"{'<=' if replacement == '\u2264' else '>='}"`, which parses here and would not
# have parsed on the 3.10 floor ADR 0002 sets. `ast.parse(feature_version=(3, 10))`
# does not see it, which is the same blindness CLAUDE.md already records for
# `int | None`, and the only interpreter on this machine is 3.14. Caught by review.
ASCII_OPERATOR = {"\u2264": "<=", "\u2265": ">="}

FORBIDDEN_IN_VALUE = {
    "\u2264": "a Unicode <=; write the ASCII <=",
    "\u2265": "a Unicode >=; write the ASCII >=",
    "\u00b3": "a Symbol-font mis-encoding of >=; write >=",
    **{
        glyph: f"a Symbol-font mis-encoding of {ASCII_OPERATOR[replacement]}; "
               f"write {ASCII_OPERATOR[replacement]}"
        for mapping in guidelines_extract.SYMBOL_FONT_OPERATORS.values()
        for glyph, replacement in mapping.items()
    },
}

# Sanity bounds are normally keyed only on the UNIT a number is written in. These
# are deliberately WIDE: the gate exists to catch a decimal
# point in the wrong place and a unit confusion, not to second-guess a society. 1300
# for a systolic pressure and 450 for an eGFR are the failures #83 names, and both
# are an order of magnitude out.
#
# **Keyed on the unit because keying on the quantity was wrong, and it was wrong in
# the direction that matters.** The first version matched the bound by substring
# against the quantity name and then graded every number in the value against it. On
# the first real sheet it produced ten failures and all ten were false: `>=27 kg/m2`
# failed because the `2` in `m2` was read as a BMI, `>=7 days` and `15% in 24 h`
# failed because their quantity names contain `bp`, and `<160/110 mm Hg within 30 to
# 60 min` failed on the minutes. A value legitimately carries numbers in several
# units and only some of them are the threshold.
#
# Every one of those was found by running the gate against a real sheet rather than
# against the synthetic cases in tools/test_threshold_sheet.py, which is the same way
# block_scan.py's two parser bugs were found. The synthetic cases came afterwards and
# now pin each shape.
UNIT_BOUNDS = {
    "mm hg": (40.0, 250.0),
    "mg/d": (1.0, 6000.0),
    "mg/day": (1.0, 6000.0),
    "mg/g": (1.0, 6000.0),
    "mg/kg": (0.01, 1000.0),
    "mg": (1.0, 6000.0),
    "ml/min": (1.0, 150.0),
    "kg/m2": (10.0, 70.0),
    "%": (0.0, 100.0),
    "drink/d": (0.0, 10.0),
    "drinks/d": (0.0, 10.0),
    "year": (0.0, 120.0),
    "years": (0.0, 120.0),
}

# These quantities use the same pressure unit as blood pressure but have
# source-valid values below its 40 mm Hg floor. Keep the semantic exceptions
# explicit so ordinary pressure rows retain the wider gate's bound.
QUANTITY_UNIT_BOUNDS = {
    ("acute-kidney-injury-and-acute-kidney-disease.md", "aki-scr-absolute-definition", "mg"): (0.3, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "aki-scr-stage-c1", "mg"): (0.3, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "neonatal-aki-scr-absolute", "mg"): (0.3, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "neonatal-scr-stage-c1", "mg"): (0.3, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "terlipressin-bolus", "mg"): (0.5, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "norepinephrine-hrs", "mg"): (0.5, 6000.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "norepinephrine-hrs", "mm hg"): (10.0, 250.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "adult-rrt-modality-parameters", "ml/min"): (1.0, 500.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "irrt-dialysate-flow", "ml/min"): (1.0, 300.0),
    ("acute-kidney-injury-and-acute-kidney-disease.md", "adult-rrt-catheter-flow", "ml/min"): (1.0, 250.0),
    ("acute-coronary-syndromes.md", "nitroglycerin-sl-dose", "mg"): (0.3, 6000.0),
    ("acute-coronary-syndromes.md", "nitroglycerin-iv-dose", "mm hg"): (30.0, 250.0),
    ("acute-coronary-syndromes.md", "pericarditis-treatment-dose", "mg"): (0.5, 6000.0),
    ("acute-coronary-syndromes.md", "chronic-colchicine-dose", "mg"): (0.5, 6000.0),
    ("acute-pulmonary-embolism.md", "normotensive-shock-creatinine-increase", "mg"): (0.3, 6000.0),
    ("anemia-in-chronic-kidney-disease.md", "severe-reaction-epinephrine", "mg"): (0.5, 6000.0),
    ("atrial-fibrillation.md", "rate-control-dose", "mg"): (0.25, 6000.0),
    ("blood-pressure-in-chronic-kidney-disease.md", "standardized-bp-inflation", "mm hg"): (20.0, 250.0),
    ("blood-pressure-in-chronic-kidney-disease.md", "standardized-bp-deflation", "mm hg"): (2.0, 250.0),
    ("blood-pressure-in-chronic-kidney-disease.md", "combination-therapy-distance", "mm hg"): (20.0, 250.0),
    ("cardiovascular-kidney-metabolic-syndrome.md", "pulmonary-pressure", "mm hg"): (35.0, 250.0),
    ("chronic-kidney-disease.md", "acute-gout-dose", "mg"): (0.6, 6000.0),
    ("diabetes-related-foot-infection.md", "severe-grade", "mm hg"): (32.0, 250.0),
    ("diabetes-in-chronic-kidney-disease.md", "rasi-trandolapril-dose", "mg/day"): (0.5, 6000.0),
    ("healthcare-associated-ventriculitis-and-meningitis.md", "intraventricular-dose-intraventricular-doses", "mg"): (0.01, 6000.0),
    ("hepatitis-c-in-chronic-kidney-disease.md", "hepatic-venous-pressure", "mm hg"): (10.0, 250.0),
    ("hepatitis-c-in-chronic-kidney-disease.md", "transplant-liver-severity", "mm hg"): (10.0, 250.0),
    ("heart-failure.md", "digoxin-dose-level", "mg"): (0.125, 6000.0),
    ("heart-failure.md", "oral-loop-diuretic-dose", "mg"): (0.5, 6000.0),
    ("heart-failure.md", "cardiogenic-shock-hemodynamic-definition", "mm hg"): (15.0, 250.0),
    ("heart-failure.md", "hfpef-score-inputs", "mm hg"): (35.0, 250.0),
    ("heart-failure.md", "structural-ventricular-thresholds", "mm hg"): (35.0, 250.0),
    ("heart-failure.md", "cardiogenic-shock-scai-stage-b", "mm hg"): (30.0, 250.0),
    ("heart-failure.md", "cardiogenic-shock-scai-stage-c", "mm hg"): (15.0, 250.0),
    ("kidney-transplant-recipient-care.md", "formal-165", "mm hg"): (35.0, 250.0),
    ("hypertrophic-cardiomyopathy.md", "historical-exercise-bp-response", "mm hg"): (20.0, 250.0),
    ("hypertrophic-cardiomyopathy.md", "lvoto-present-gradient", "mm hg"): (30.0, 250.0),
    ("lower-extremity-peripheral-artery-disease.md", "toe-pressure-severe-ischemia", "mm hg"): (30.0, 250.0),
    ("lower-extremity-peripheral-artery-disease.md", "tcpo2-healing-threshold", "mm hg"): (30.0, 250.0),
    ("valvular-heart-disease.md", "as-severity-definition", "mm hg"): (20.0, 250.0),
    ("valvular-heart-disease.md", "ms-severity-definition", "mm hg"): (5.0, 250.0),
    ("valvular-heart-disease.md", "indexed-p23-timing-of-intervention-of-as-6", "mm hg"): (10.0, 250.0),
    ("valvular-heart-disease.md", "indexed-p45-intervention-for-rheumatic-ms-5", "mm hg"): (15.0, 250.0),
    ("cardiac-arrest-and-life-threatening-toxicity-due-to-poisoning.md", "atropine-brady-initial-adult", "mg"): (0.1, 6000.0),
    ("cardiac-arrest-and-life-threatening-toxicity-due-to-poisoning.md", "digoxin-fab-acute", "mg"): (0.1, 6000.0),
    ("bradycardia-and-cardiac-conduction-delay.md", "digoxin-fab-vial-binding", "mg"): (0.1, 6000.0),
    ("cardiac-arrest-and-life-threatening-toxicity-due-to-poisoning.md", "flumazenil-initial-adult", "mg"): (0.1, 6000.0),
    ("cardiac-arrest-and-life-threatening-toxicity-due-to-poisoning.md", "naloxone-initial-adult", "mg"): (0.1, 6000.0),
}

# A run of numbers sharing one trailing unit. The separators are what make
# `140-159/90-109 mm Hg` four graded numbers rather than one, and `<160/<110 mm Hg`
# two -- a comparison operator may sit between them, which is how a guideline writes
# a paired systolic and diastolic bound.
#
# Units that carry NO bound above are matched anyway and then skipped, deliberately:
# matching `24 to 48 hours` is what stops those numbers being attributed to the mm Hg
# that appears earlier in the same value.
_UNIT_ALTERNATION = (
    r"mm\s*Hg|mg/d(?:ay)?|mg/g|mg/kg|mg|mL\s*/\s*min|kg/m2|kg|%|drinks?/d|"
    r"days?|weeks?|months?|years?|hours?|h|min(?:utes)?"
)
_MEASURED = re.compile(
    r"(?P<numbers>\d+(?:[.,]\d+)?(?:\s*(?:to|and|[-/])\s*[<>]?=?\s*\d+(?:[.,]\d+)?)*)"
    r"\s*(?P<unit>" + _UNIT_ALTERNATION + r")\b",
    re.IGNORECASE,
)

_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
_ROW_PIPE = re.compile(r"^\s*\|(?P<body>.+)\|\s*$")
_CONFLICT = re.compile(r"^\s*\*{0,2}CONFLICT\*{0,2}:\s*(?P<quantity>[a-z0-9-]+)\b(?P<rest>.*)$", re.IGNORECASE)
_OUT_LINE = re.compile(r"^\s*-\s*`(?P<rec_id>[^`]+)`\s*[-\u2014:]\s*(?P<reason>.+?)\s*$")
_RESOLVED = re.compile(r"citations resolved against\s+(?P<corpus>\S+)\s+on\s+(?P<date>\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_EXTRACTION_IDENTITY = re.compile(
    r"^extraction identity:\s*producer\s+(?P<commit>[0-9a-f]{40});\s*"
    r"tools/guidelines_extract\.py\s+sha256\s+(?P<sha256>[0-9a-f]{64})\s*$",
    re.IGNORECASE,
)
_SPAN_SOURCE = re.compile(
    r"^\s*\*{0,2}Source:\s*`?(?P<source>[a-z0-9-]+)`?\*{0,2}\s*$",
    re.IGNORECASE,
)
_SPAN_RANGE = re.compile(r"^p?(?P<first>\d+)(?:\s*-\s*p?(?P<last>\d+))?$", re.I)
_DATED_SPAN_READ = re.compile(
    r"^read\s+(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?:;\s*blind\s+(?P<blind_date>\d{4}-\d{2}-\d{2}))?$",
    re.I,
)
_SPAN_EXEMPTION = re.compile(r"^exempt:\s*(?P<reason>\S.+)$", re.I)
_DATED_DOWNLOAD_BASIS = re.compile(
    r"^(?:digest|gated)\s+(?P<date>\d{4}-\d{2}-\d{2})$"
)

_INEQUALITY_WORDS = (
    (r"\b(?:less than or equal to|at or below|no more than)\b", "<="),
    (r"\b(?:greater than or equal to|at or above|at least)\b", ">="),
    (r"\b(?:less than|below)\b", "<"),
    (r"\b(?:greater than|above|more than)\b", ">"),
)


@dataclass
class GateResult:
    """One gate's named outcome; every finding remains plain text."""

    gate: str
    findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    pairings: list[str] = field(default_factory=list)
    undiffed: list[str] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)
    skip_reason: str | None = None
    rendered: int = 0
    ungraded: int = 0
    ungraded_sources: list[str] = field(default_factory=list)
    unprobed_sources: list[str] = field(default_factory=list)
    report: tuple[str, ...] = ()
    stdout: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()
    tier2_skip_diagnostics: tuple[str, ...] = ()
    not_graded: bool = False
    fatal: bool = False
    report_after_stdout: tuple[str, ...] = ()
    stdout_before_footer: bool = False

@dataclass(frozen=True)
class Row:
    quantity: str
    population: str
    value: str
    snippet: str
    source: str
    page: int | None
    rec: str
    klass: str
    line: int


@dataclass(frozen=True)
class SourceLocator:
    """The page, kind, and identifier carried by one threshold-row locator."""

    page: int
    kind: str
    identifier: str

    @property
    def is_narrative(self) -> bool:
        return self.kind == NARRATIVE_KIND


def source_locator(value: str) -> SourceLocator | None:
    """Parse ``p<digits>/<kind>/<id>`` without inferring an unknown kind."""

    match = _SOURCE_LOCATOR.fullmatch(value)
    if match is None:
        return None
    return SourceLocator(
        page=int(match.group("page")),
        kind=match.group("kind"),
        identifier=match.group("identifier"),
    )


@dataclass(frozen=True)
class Span:
    source: str
    name: str
    first_page: int
    last_page: int
    read: str
    line: int

    @property
    def is_unread(self) -> bool:
        return self.read.casefold() == "no"

    @property
    def has_dated_marker(self) -> bool:
        match = _DATED_SPAN_READ.fullmatch(self.read)
        if match is None:
            return False
        for group in ("date", "blind_date"):
            value = match.group(group)
            if value is None:
                continue
            try:
                date.fromisoformat(value)
            except ValueError:
                return False
        return True

    @property
    def blind_read_date(self) -> date | None:
        match = _DATED_SPAN_READ.fullmatch(self.read)
        if match is None or not self.has_dated_marker:
            return None
        value = match.group("blind_date")
        return date.fromisoformat(value) if value is not None else None

    @property
    def exemption_reason(self) -> str | None:
        match = _SPAN_EXEMPTION.fullmatch(self.read)
        return match.group("reason") if match else None


@dataclass(frozen=True)
class ExtractionIdentity:
    """The two manifest fields a sheet binds its extracted-text reading to."""

    producer_commit: str
    extractor_sha256: str


def extraction_identity_from_manifest(
    root: Path,
    *,
    allow_untrusted_provenance: bool = False,
) -> tuple[ExtractionIdentity | None, list[str]]:
    """Read identity through the extracted corpus's validated manifest owner."""

    handoff = guidelines_manifest.read(
        root,
        allow_untrusted_provenance=allow_untrusted_provenance,
    )
    path = handoff.root / guidelines_manifest.MANIFEST_NAME
    producer = handoff.provenance.producer if handoff.provenance else None
    if not isinstance(producer, dict):
        problems = [problem.message for problem in handoff.problems]
        return None, problems or [f"{path} has no validated producer record"]
    commit = producer.get("commit")
    inputs = producer.get("inputs")
    extractor = next(
        (
            item.get("sha256")
            for item in inputs
            if isinstance(item, dict)
            and item.get("path") == "tools/guidelines_extract.py"
        ),
        None,
    ) if isinstance(inputs, list) else None
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        return None, [f"{path} producer has no 40-character commit"]
    if not isinstance(extractor, str) or re.fullmatch(r"[0-9a-f]{64}", extractor) is None:
        return None, [f"{path} validated producer has no extractor SHA-256"]
    return ExtractionIdentity(commit, extractor), []


def render_extraction_identity(identity: ExtractionIdentity) -> str:
    """Render the declaration shared by the draft producer and sheet parser."""

    return (
        f"extraction identity: producer {identity.producer_commit}; "
        f"tools/guidelines_extract.py sha256 {identity.extractor_sha256}"
    )


@dataclass
class Sheet:
    """A parsed sheet. ``ok`` is false when it could not be read as one at all."""

    path: Path
    rows: list[Row] = field(default_factory=list)
    sources: dict[str, dict[str, str]] = field(default_factory=dict)
    populations: dict[str, str] = field(default_factory=dict)
    quantities: dict[str, str] = field(default_factory=dict)
    conflicts: dict[str, str] = field(default_factory=dict)
    scoped_out: dict[str, str] = field(default_factory=dict)
    spans: list[Span] = field(default_factory=list)
    span_problems: list[str] = field(default_factory=list)
    # The prose of the ``## Scope`` section, and nothing from anywhere else. Kept as
    # its own field rather than searched for over the whole document because the two
    # phrases that satisfy it are ordinary English: a threshold row whose snippet
    # quotes "not read" would otherwise discharge the sheet's honesty clause.
    scope: str = ""
    thresholds: str = ""
    has_scope_section: bool = False
    resolved_corpus: str | None = None
    resolved_date: str | None = None
    extraction_identity: ExtractionIdentity | None = None
    accepted_distrust: artifact_provenance.AcceptedDistrust | None = None
    accepted_distrust_problems: tuple[str, ...] = ()
    ok: bool = True
    why_not: str | None = None


def _rows_cited_within_span(sheet: Sheet, span: Span) -> list[Row]:
    """Return rows whose source and cited page fall within ``span``."""
    return [
        row for row in sheet.rows
        if row.source == span.source
        and row.page is not None
        and span.first_page <= row.page <= span.last_page
    ]


@dataclass
class Scan:
    """A completed sheet survey whose output has not been emitted."""

    sheet: Sheet
    results: tuple[GateResult, ...] = ()
    status: int = 0
    diagnostics: tuple[str, ...] = ()
    reportable: bool = True


def format_report(scan: Scan) -> str:
    """Render only the suppressible report carried by a completed survey."""
    if not scan.reportable:
        return ""

    lines = _report_opening(scan.sheet)
    if not scan.sheet.ok:
        return "\n".join(lines) + "\n"

    for result in scan.results:
        lines.extend(result.report)
        if result.stdout_before_footer:
            lines.extend(result.stdout)
        lines.extend(result.report_after_stdout)
    lines.extend(_report_footer(scan.sheet))
    return "\n".join(lines) + "\n"


def _report_opening(sheet: Sheet) -> list[str]:
    """The report prefix shared by pure formatting and streamed CLI emission."""
    lines = [f"== {sheet.path.name}"]
    if sheet.ok:
        lines.extend(
            (
                f"  rows            {len(sheet.rows)}",
                f"  sources         {len(sheet.sources)}",
                f"  populations     {len(sheet.populations)}",
                f"  quantities      {len(sheet.quantities)}",
                f"  scoped out      {len(sheet.scoped_out)}",
                "",
            )
        )
    return lines


def _report_footer(sheet: Sheet) -> tuple[str, ...]:
    """The resolution line that closes every parsed-sheet report."""
    if sheet.resolved_date:
        return (
            f"  last resolved   {sheet.resolved_date} against {sheet.resolved_corpus}",
        )
    return (
        "  last resolved   NOT RECORDED -- the sheet does not say when tier 2 last ran",
    )


def _document_of(sheet: "Sheet", row: "Row") -> str:
    """The source document a row cites, or ``""`` where its source is undeclared.

    One walk rather than four spellings of it. It was written out at every call site
    first -- ``sheet.sources.get(row.source, {}).get("document", "")`` in three places
    and ``sheet.sources[row.source].get("document", "")`` in a fourth, which is the
    same chain with a different failure mode on an undeclared key. Every gate that
    reaches for a row's document is really asking this one question, and SCHEMA has
    already refused the row where the answer is empty.
    """
    return sheet.sources.get(row.source, {}).get("document", "")


def _cells(line: str) -> list[str] | None:
    """A Markdown table row as its cells, or None if the line is not one."""
    match = _ROW_PIPE.match(line)
    if not match:
        return None
    return [cell.strip() for cell in match.group("body").split("|")]


def _is_rule(cells: list[str]) -> bool:
    """The ``| --- | --- |`` line under a header."""
    return all(set(cell) <= set("-: ") and cell for cell in cells)


def _normalized_conflict_claim(text: str) -> str:
    """Normalize the bounded inequality wording a conflict may use in prose.

    The row remains the source of truth. This only makes ``below 180`` comparable
    with ``<180``; it does not attempt to interpret arbitrary clinical prose.
    """
    normalized = text.casefold()
    for phrase, operator in _INEQUALITY_WORDS:
        normalized = re.sub(phrase, operator, normalized)
    normalized = re.sub(r"(<=|>=|<|>)\s*", r"\1", normalized)
    normalized = re.sub(r"\s*/\s*", "/", normalized)
    return " ".join(normalized.split())


def _unnamed_conflict_values(values: set[str], conflict: str) -> list[str]:
    """Return row values that have no distinct, bounded mention in the prose."""
    claim = _normalized_conflict_claim(conflict)
    normalized_values = [(value, _normalized_conflict_claim(value)) for value in values]
    # Longest first prevents one longer mention from donating its prefix to a second
    # value. Each value gets its own span: evidence that two sides were compared must
    # occur twice, not be two interpretations of the same characters.
    normalized_values.sort(key=lambda item: (-len(item[1]), item[1]))
    used: list[tuple[int, int]] = []
    missing: list[str] = []
    for value, normalized in normalized_values:
        pattern = re.compile(r"(?<!\w)" + re.escape(normalized) + r"(?!\w)")
        available = next(
            (
                match
                for match in pattern.finditer(claim)
                if not any(match.start() < end and start < match.end() for start, end in used)
            ),
            None,
        )
        if available is None:
            missing.append(value)
        else:
            used.append(available.span())
    return sorted(missing)


def parse(text: str, path: Path) -> Sheet:
    """Read a sheet into its parts.

    Sections are found by heading, and a row is only read inside the section that
    owns it. **That is the load-bearing choice in here.** A sheet's prose discusses
    its own rules -- this file's docstring is full of pipe characters and quantity
    keys -- and a parser matching a row shape anywhere would read the explanation of
    a conflict as a conflict. ``block_scan.py`` learned the same rule the hard way:
    a row fires on what opens a section, never on a mention inside one.
    """
    sheet = Sheet(path=path)
    raw_findings = [
        (offset, character, why)
        for character, why in FORBIDDEN_IN_RAW_TEXT.items()
        if (offset := text.find(character)) != -1
    ]
    if raw_findings:
        offset, character, why = min(raw_findings)
        line = text.count("\n", 0, offset) + 1
        sheet.ok = False
        sheet.why_not = (
            f"{path.name}:{line} contains U+{ord(character):04X}, a mis-encoded "
            f"comparison operator that {why}; render the cited PDF page (for example "
            "with PyMuPDF), visually verify the operator, and replace it with ASCII "
            "<= or >="
        )
        return sheet
    if SCHEMA_MARKER not in text:
        sheet.ok = False
        sheet.why_not = f"no {SCHEMA_MARKER} marker"
        return sheet

    section: str | None = None
    source_columns: list[str] = []
    span_source: str | None = None
    reading_span_table = False
    for number, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^\s*#{1,6}\s+(?P<name>.+?)\s*$", line)
        if heading:
            section = heading.group("name").strip().lower()
            if section == SCOPE_HEADING.removeprefix("## ").lower():
                sheet.has_scope_section = True
                span_source = None
                reading_span_table = False
            continue

        if section == SCOPE_HEADING.removeprefix("## ").lower():
            sheet.scope += line + "\n"
            source_match = _SPAN_SOURCE.match(line)
            if source_match:
                span_source = source_match.group("source")
                reading_span_table = False
            resolved = _RESOLVED.search(line)
            if resolved:
                sheet.resolved_corpus = resolved.group("corpus")
                sheet.resolved_date = resolved.group("date")
            extraction_identity = _EXTRACTION_IDENTITY.fullmatch(line.strip())
            if extraction_identity:
                sheet.extraction_identity = ExtractionIdentity(
                    extraction_identity.group("commit").lower(),
                    extraction_identity.group("sha256").lower(),
                )

        if section == THRESHOLDS_HEADING.removeprefix("## ").lower():
            sheet.thresholds += line + "\n"

        if section == CONFLICTS_HEADING.removeprefix("## ").lower():
            conflict = _CONFLICT.match(line)
            if conflict:
                sheet.conflicts[conflict.group("quantity").lower()] = conflict.group("rest").strip()
            continue

        if section == COVERAGE_HEADING.removeprefix("## ").lower():
            out = _OUT_LINE.match(line)
            if out:
                sheet.scoped_out[out.group("rec_id")] = out.group("reason")
            continue

        cells = _cells(line)
        if cells is None or _is_rule(cells):
            continue

        if (
            section == SCOPE_HEADING.removeprefix("## ").lower()
            and [cell.casefold() for cell in cells] == ["span", "pages", "read"]
        ):
            reading_span_table = True
            continue

        if section == SCOPE_HEADING.removeprefix("## ").lower() and reading_span_table:
            if len(cells) != 3:
                sheet.span_problems.append(
                    f"{path.name}:{number} span row has {len(cells)} cells, expected 3"
                )
                continue
            source = span_source
            if source is None and len(sheet.sources) == 1:
                source = next(iter(sheet.sources))
            if source is None:
                sheet.span_problems.append(
                    f"{path.name}:{number} span table in a multi-source sheet has no "
                    "preceding 'Source: `<source key>`' line"
                )
                continue
            page_match = _SPAN_RANGE.fullmatch(cells[1])
            if page_match is None:
                sheet.span_problems.append(
                    f"{path.name}:{number} span '{cells[0]}' has invalid page range '{cells[1]}'"
                )
                continue
            first = int(page_match.group("first"))
            last = int(page_match.group("last") or first)
            if first < 1 or last < first:
                sheet.span_problems.append(
                    f"{path.name}:{number} span '{cells[0]}' has invalid page range '{cells[1]}'"
                )
                continue
            sheet.spans.append(Span(source, cells[0], first, last, cells[2], number))
            continue

        if section == SOURCES_HEADING.removeprefix("## ").lower() and not source_columns:
            if cells != list(SOURCE_COLUMNS):
                sheet.ok = False
                sheet.why_not = (
                    f"{path.name}:{number} unreadable '## Sources' header; expected "
                    + " | ".join(SOURCE_COLUMNS)
                )
                return sheet
            source_columns = list(SOURCE_COLUMNS)
            continue

        if (
            section == SOURCES_HEADING.removeprefix("## ").lower()
            and len(cells) == len(SOURCE_COLUMNS)
            and cells[0] != "key"
        ):
            named = dict(zip(source_columns, cells, strict=True))
            sheet.sources[cells[0]] = {
                column: named[column]
                for column in SOURCE_COLUMNS
                if column != "key"
            }
        elif (
            section == POPULATIONS_HEADING.removeprefix("## ").lower()
            and len(cells) >= 2
            and cells[0] != "key"
        ):
            sheet.populations[cells[0]] = cells[1]
        elif (
            section == QUANTITIES_HEADING.removeprefix("## ").lower()
            and len(cells) >= 2
            and cells[0] != "key"
        ):
            sheet.quantities[cells[0]] = cells[1]
        elif (
            section == THRESHOLDS_HEADING.removeprefix("## ").lower()
            and len(cells) >= len(ROW_COLUMNS)
            and cells[0] != "quantity"
        ):
            page = re.sub(r"^p", "", cells[5], flags=re.IGNORECASE)
            sheet.rows.append(
                Row(
                    quantity=cells[0],
                    population=cells[1],
                    value=cells[2],
                    snippet=cells[3].strip('"'),
                    source=cells[4],
                    page=int(page) if page.isdigit() else None,
                    rec=cells[6],
                    klass=cells[7],
                    line=number,
                )
            )

    declaration_text = " ".join(sheet.thresholds.split())
    has_null_declaration = declaration_text in {
        " ".join(NONE_DECLARATION.split()),
        " ".join(NON_SOURCE_DECLARATION.split()),
    }
    if not sheet.rows and not has_null_declaration:
        sheet.ok = False
        sheet.why_not = "no row under a '## Thresholds' heading"
    sheet.accepted_distrust, sheet.accepted_distrust_problems = (
        artifact_provenance.parse_accepted_distrust(sheet.scope)
    )
    return sheet


def gate_schema(
    sheet: Sheet, catalog_source_classes: dict[str, str] | None = None
) -> GateResult:
    """Structure, provenance, scope, declared vocabulary, and the conflict rule."""
    failures: list[str] = []
    failures.extend(
        f"{sheet.path.name}  {problem}" for problem in sheet.accepted_distrust_problems
    )
    declaration_text = " ".join(sheet.thresholds.split())
    has_none_declaration = declaration_text == " ".join(NONE_DECLARATION.split())
    has_non_source_declaration = declaration_text == " ".join(
        NON_SOURCE_DECLARATION.split()
    )
    all_sources_declared_non_source = bool(sheet.sources) and all(
        source.get("source class") in DECLARED_NON_SOURCE_CLASSES
        for source in sheet.sources.values()
    )
    if not sheet.rows and all_sources_declared_non_source and has_none_declaration:
        failures.append(
            f"{sheet.path.name}  none declaration cannot describe declared non-source classes"
        )
    if not sheet.rows and not all_sources_declared_non_source and has_non_source_declaration:
        failures.append(
            f"{sheet.path.name}  non-source declaration requires every source class to be declared non-source"
        )

    # #83 lists the scope line among the things a sheet *carries*, and gives the
    # reason: *"so that 'absent from the sheet' is never misread as 'absent from the
    # guideline'"*. Both limbs are required and the second does the work -- `Read:`
    # alone lists coverage, only `Not read:` bounds the claim. Graded against the
    # `## Scope` section alone, never the whole document, so a row quoting either
    # phrase in its snippet cannot discharge it.
    if not sheet.has_scope_section:
        failures.append(f"{sheet.path.name}  no '## Scope' section, so nothing bounds what this sheet claims")
    else:
        scope = sheet.scope.lower()
        # The lookbehind is the whole rule, not a refinement: `not read:` CONTAINS
        # `read:`, so a plain substring test was discharged by the very sentence that
        # should have failed it -- a sheet declaring only what it skipped read as
        # having declared both.
        if not re.search(r"(?<!not )read:", scope):
            failures.append(f"{sheet.path.name}  '## Scope' never says what was read")
        if "not read:" not in scope:
            failures.append(
                f"{sheet.path.name}  '## Scope' never says what was NOT read, so an absent "
                "number cannot be told from an unread section"
            )
        if sheet.extraction_identity is None:
            failures.append(
                f"{sheet.path.name}  '## Scope' has no extraction identity, so tier 0 "
                "and tier 1 cannot be tied to the extracted text they read"
            )

    failures.extend(sheet.span_problems)
    if not sheet.spans:
        failures.append(f"{sheet.path.name}  '## Scope' has no required span table")
    seen_spans: set[tuple[str, str]] = set()
    for span in sheet.spans:
        where = f"{sheet.path.name}:{span.line}"
        identity = (span.source, span.name.casefold())
        if identity in seen_spans:
            failures.append(
                f"{where} duplicate span '{span.name}' for source '{span.source}'"
            )
        seen_spans.add(identity)
        if span.source not in sheet.sources:
            failures.append(f"{where} span source '{span.source}' is not declared under '## Sources'")
        read = span.read.casefold()
        if read not in {"yes", "no"} and not span.has_dated_marker and span.exemption_reason is None:
            failures.append(
                f"{where} span '{span.name}' has invalid read value '{span.read}'"
            )
            continue
        if span.exemption_reason is not None and span.name.casefold() != "references":
            failures.append(
                f"{where} only a references span may carry a class exemption"
            )
        rows = _rows_cited_within_span(sheet, span)
        if read == "yes" and not rows:
            failures.append(
                f"{where} read span '{span.name}' has neither rows nor a dated marker"
            )

    unread_null_spans = [span.name for span in sheet.spans if span.is_unread]
    if not sheet.rows and unread_null_spans:
        failures.append(
            f"{sheet.path.name}  zero-row sheet still has unread span(s): "
            + ", ".join(unread_null_spans)
        )

    # A threshold with no edition behind it is the failure the format exists to
    # prevent: societies revise, and 2017's number under 2025's heading is wrong in
    # the most expensive way. These three cells were parsed past until they were not.
    for key, source in sheet.sources.items():
        for column in ("source class", "version", "published", "url", "basis"):
            if not source.get(column):
                failures.append(f"{sheet.path.name}  source '{key}' has no {column}")
        url = source.get("url", "")
        if url and re.fullmatch(r"https?://\S+", url) is None:
            failures.append(
                f"{sheet.path.name}  source '{key}' download address must be an HTTP(S) address"
            )
        basis = source.get("basis", "")
        basis_match = _DATED_DOWNLOAD_BASIS.fullmatch(basis)
        valid_basis = basis in {"stated", "chosen"}
        if basis_match is not None:
            try:
                basis_date = date.fromisoformat(basis_match.group("date"))
            except ValueError:
                pass
            else:
                valid_basis = basis_date <= date.today()
        if basis and not valid_basis:
            failures.append(
                f"{sheet.path.name}  source '{key}' has invalid download basis '{basis}'"
            )
        document = source.get("document", "")
        expected_class = (catalog_source_classes or {}).get(document)
        if expected_class is not None and source.get("source class") != expected_class:
            failures.append(
                f"{sheet.path.name}  source '{key}' source class "
                f"'{source.get('source class', '')}' disagrees with catalog class "
                f"'{expected_class}' for '{document}'"
            )

    for row in sheet.rows:
        where = f"{sheet.path.name}:{row.line}"
        if row.quantity not in sheet.quantities:
            failures.append(
                f"{where}  quantity key '{row.quantity}' is not declared under '## Quantities'"
            )
        if row.population not in sheet.populations:
            failures.append(
                f"{where}  population key '{row.population}' is not declared under '## Populations'"
            )
        if row.source not in sheet.sources:
            failures.append(f"{where}  source key '{row.source}' is not declared under '## Sources'")
        elif sheet.sources[row.source].get("source class") in DECLARED_NON_SOURCE_CLASSES:
            failures.append(
                f"{where}  declared non-source source '{row.source}' cannot carry a threshold row"
            )
        if row.page is None:
            failures.append(f"{where}  no page number")
        locator = source_locator(row.rec)
        if locator is None:
            failures.append(
                f"{where}  rec '{row.rec}' is not a source locator shaped "
                "p<digits>/<kind>/<id>"
            )
        elif row.page is not None and row.page != locator.page:
            failures.append(
                f"{where}  source locator page p{locator.page} does not match "
                f"page column p{row.page}"
            )
        if row.page is not None and not any(
            span.source == row.source
            and span.read.casefold() == "yes"
            and span.first_page <= row.page <= span.last_page
            for span in sheet.spans
        ):
            failures.append(
                f"{where}  page p{row.page} is not covered by any '## Scope' span "
                "whose read cell is read: yes; a dated null marker or exemption cannot "
                "support a cited row"
            )
        if not row.snippet:
            failures.append(f"{where}  no snippet, so tier 1 citation cannot run on this row")
        for character, why in FORBIDDEN_IN_VALUE.items():
            if character in row.value:
                failures.append(f"{where}  value contains {character!r}: {why}")

    not_read_items = _not_read_scope_items(sheet.scope)
    if not_read_items is not None:
        for span in sheet.spans:
            left_unread_list = (
                span.read.casefold() == "yes"
                or span.has_dated_marker
                or span.exemption_reason is not None
            )
            if left_unread_list and span.name.casefold() in not_read_items:
                failures.append(
                    f"{sheet.path.name}:{span.line} span '{span.name}' has left the unread "
                    "list but is still named under 'Not read:'"
                )

    # The conflict rule. Keyed on quantity AND population together, because two rows
    # measuring the same thing in different patients are not a disagreement -- KDIGO
    # targets SBP <120 in CKD and AHA/ACC targets <130/80 in general adults, and
    # calling that a contradiction would be the sheet inventing one. That ruling is
    # the clinician's; this is the mechanism it asked for.
    seen: dict[tuple[str, str], set[str]] = {}
    for row in sheet.rows:
        seen.setdefault((row.quantity, row.population), set()).add(row.value)
    for (quantity, population), values in sorted(seen.items()):
        if len(values) <= 1:
            continue
        conflict = sheet.conflicts.get(quantity.lower())
        if conflict is None:
            failures.append(
                f"{sheet.path.name}  quantity '{quantity}' for population '{population}' "
                f"has {len(values)} different values ({', '.join(sorted(values))}) "
                f"and no 'CONFLICT: {quantity}' block under '## Conflicts'"
            )
            continue
        missing = _unnamed_conflict_values(values, conflict)
        if missing:
            failures.append(
                f"{sheet.path.name}  'CONFLICT: {quantity}' for population '{population}' "
                f"does not name every distinct value; missing {', '.join(missing)}"
            )
    return GateResult(
        "SCHEMA",
        failures,
        report=(f"  SCHEMA          {len(failures)}",),
    )


def gate_null_span(sheet: Sheet) -> GateResult:
    """Refuse a span's null claim until it carries dated corroboration."""

    retired = [span for span in sheet.spans if span.has_dated_marker]
    uncorroborated = [span for span in retired if span.blind_read_date is None]
    failures = [
        f"{sheet.path.name}  span '{span.name}' was retired on a marker without "
        "a dated blind-read token"
        for span in uncorroborated
    ]
    corroborated = len(retired) - len(uncorroborated)
    line = (
        f"  NULL SPAN       {len(failures)} refusing over {len(retired)} "
        "span(s) retired on a marker"
    )
    if retired:
        line += f", {corroborated} corroborated"
    return GateResult("NULL SPAN", failures, report=(line,))


def gate_extraction_identity(
    sheet: Sheet,
    current: ExtractionIdentity | None,
    problems: list[str] | tuple[str, ...] = (),
) -> GateResult:
    """Warn when the sheet and current extracted corpus name different builds."""

    if current is None:
        reason = "; ".join(problems) or "no extracted-corpus identity was available"
        message = f"EXTRACTION IDENTITY NOT RUN -- {reason}"
        return GateResult(
            "EXTRACTION IDENTITY",
            skip_reason=reason,
            report=(f"  {message}",),
            diagnostics=(f"  {message}",),
        )
    warnings: list[str] = []
    if sheet.extraction_identity is not None and sheet.extraction_identity != current:
        warnings.append(
            f"{sheet.path.name}  was read against a different extraction than the "
            "current manifest"
        )
    return GateResult(
        "EXTRACTION IDENTITY",
        warnings=warnings,
        report=(f"  EXTRACTION IDENTITY {len(warnings)} warning",),
    )


def _not_read_scope_items(scope: str) -> set[str] | None:
    """Return normalized items from the first ``Not read:`` sentence."""
    prose = "\n".join(
        line for line in scope.splitlines() if not line.lstrip().startswith("|")
    )
    match = re.search(
        r"\*\*not read:\*\*\s*(?P<limb>.*?(?:\.(?=\s|$)|$))",
        prose,
        flags=re.I | re.S,
    )
    if match is None:
        return None
    sentence = " ".join(match.group("limb").split()).rstrip(".")
    return {
        item.strip().casefold()
        for item in re.split(
            r"\s*(?:,|;)\s*(?:and\s+)?|\s+and\s+",
            sentence,
            flags=re.I,
        )
        if item.strip()
    }


def _page_runs(pages: set[int]) -> str:
    """Compact a page set without hiding any member of the remainder."""
    if not pages:
        return "none"
    ordered = sorted(pages)
    runs: list[str] = []
    start = previous = ordered[0]
    for page in ordered[1:]:
        if page == previous + 1:
            previous = page
            continue
        runs.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = page
    runs.append(str(start) if start == previous else f"{start}-{previous}")
    return ", ".join(runs)


def gate_page_coverage(sheet: Sheet, page_counts: dict[str, int]) -> GateResult:
    """Require each source's span union to cover its independently counted pages."""
    findings: list[str] = []
    stdout: list[str] = []
    unresolved: list[str] = []
    for source_key, source in sheet.sources.items():
        document = source.get("document", "")
        page_count = page_counts.get(document)
        if page_count is None:
            unresolved.append(document or source_key)
            stdout.append(
                f"  PAGE COVERAGE  {source_key} page_count: NOT RESOLVED; "
                "unaccounted pages: NOT GRADED "
                f"(page_count unresolved for {document or source_key})"
            )
            continue
        covered = {
            page
            for span in sheet.spans
            if span.source == source_key
            for page in range(span.first_page, span.last_page + 1)
        }
        expected = set(range(1, page_count + 1))
        remainder = expected - covered
        stdout.append(
            f"  PAGE COVERAGE  {source_key} page_count: {page_count}; "
            f"unaccounted pages: {_page_runs(remainder)}"
        )
        if remainder:
            findings.append(
                f"{sheet.path.name} source '{source_key}' leaves page(s) "
                f"{_page_runs(remainder)} unaccounted for"
            )
        outside = {page for page in covered if page > page_count}
        if outside:
            findings.append(
                f"{sheet.path.name} source '{source_key}' assigns page(s) "
                f"{_page_runs(outside)} beyond page_count {page_count}"
            )
    reason = (
        "page_count unresolved for " + ", ".join(unresolved)
        if unresolved else None
    )
    return GateResult(
        "PAGE COVERAGE",
        findings,
        skip_reason=reason,
        not_graded=bool(unresolved),
        stdout=tuple(stdout),
        report=(f"  PAGE COVERAGE   {len(findings)}",),
    )


@dataclass(frozen=True)
class CatalogFacts:
    rows: tuple[guidelines_catalog.Row, ...]
    page_counts: dict[str, int]
    source_classes: dict[str, str]
    parse_problems: tuple[str, ...]
    page_count_problems: tuple[str, ...]

    @property
    def problems(self) -> tuple[str, ...]:
        return self.parse_problems + self.page_count_problems


def load_catalog_facts(path: Path = DEFAULT_CATALOG) -> CatalogFacts:
    """Resolve the catalog facts threshold-sheet gates consume in one parse."""
    try:
        rows, _, problems = guidelines_catalog.parse_catalog(path.read_text(encoding="utf-8"))
    except OSError as error:
        return CatalogFacts((), {}, {}, (str(error),), ())
    counts: dict[str, int] = {}
    source_classes: dict[str, str] = {}
    page_count_problems: list[str] = []
    for row in rows:
        document = f"{row.society}/{Path(row.filename).stem}"
        source_classes[document] = row.cls
        if row.page_count.isdigit():
            counts[document] = int(row.page_count)
        else:
            page_count_problems.append(
                f"catalog source '{document}' has unresolved page_count '{row.page_count}'"
            )
    return CatalogFacts(
        tuple(rows),
        counts,
        source_classes,
        tuple(problems),
        tuple(page_count_problems),
    )


def load_catalog_page_counts(path: Path = DEFAULT_CATALOG) -> tuple[dict[str, int], list[str]]:
    """Resolve source document ids to the catalog's independently derived count."""
    facts = load_catalog_facts(path)
    return facts.page_counts, list(facts.problems)


def load_catalog_source_classes(
    path: Path = DEFAULT_CATALOG,
) -> tuple[dict[str, str], list[str]]:
    """Resolve source document ids to the catalog's declared document form."""
    facts = load_catalog_facts(path)
    return facts.source_classes, list(facts.parse_problems)


def gate_citation_tier1(sheet: Sheet) -> GateResult:
    """Every number in a row's value must appear in that row's snippet.

    Runs on every machine, which is the point. Tier 2 needs source PDFs that live
    outside this repo, so on a fresh clone it has nothing to resolve -- and a gate
    that silently drops to zero there is the same hole `phi_scan.py`'s corpus layer
    documents and that #93 watched fire for real.
    """
    if not sheet.rows:
        return GateResult(
            "CITATION tier 1",
            report=("  CITATION tier 1 NO ROWS",),
        )
    failures: list[str] = []
    for row in sheet.rows:
        wanted = _NUMBER.findall(row.value)
        if not wanted:
            continue
        present = set(_NUMBER.findall(row.snippet))
        missing = [number for number in wanted if number not in present]
        if missing:
            failures.append(
                f"{sheet.path.name}:{row.line}  value '{row.value}' has "
                f"{', '.join(missing)} which the snippet does not contain"
            )
    return GateResult(
        "CITATION tier 1",
        failures,
        report=(f"  CITATION tier 1 {len(failures)}",),
    )


def gate_citation_tier0(
    sheet: Sheet,
    records: dict[str, dict | None],
    why_not: dict[str, str],
) -> GateResult:
    """Grade recommendation snippets and narrative transcriptions on exact sources.

    This is a provenance floor, not a clinical reading. A recommendation row proves
    only that its record states the snippet. A narrative row proves only that no
    recommendation record on the same page states its transcription. Neither can
    prove that the passage answers the row's quantity or applies to its population.

    ``bound`` recommendation records are deliberately not graded. Their running-text
    windows can truncate before the value a row cites, so a mismatch is evidence
    about the extractor rather than the sheet. The result says ``NOT RUN`` instead of
    turning that limitation into either a pass or a refusal.
    """
    failures: list[str] = []
    rendered = 0
    ungraded_sources: list[str] = []
    bound_reports: list[str] = []

    for source_key in sorted(sheet.sources):
        record = records.get(source_key)
        if record is None:
            ungraded_sources.append(
                f"{source_key} ({why_not.get(source_key, 'no recommendation record')})"
            )
            continue

        mode = str(record.get("mode") or sheet.sources[source_key].get("mode") or "")
        if mode != MODE_EXACT:
            reason = "source mode is 'bound'" if mode == MODE_BOUND else f"source mode is {mode!r}"
            ungraded_sources.append(f"{source_key} ({reason})")
            if mode == MODE_BOUND:
                source_rows = [row for row in sheet.rows if row.source == source_key]
                recommendation_rows = [
                    row
                    for row in source_rows
                    if (locator := source_locator(row.rec)) is not None
                    and not locator.is_narrative
                ]
                rendered_rows = [
                    row for row in source_rows if row.snippet.startswith(RENDERED_MARKER)
                ]
                rendered_recommendations = [
                    row for row in recommendation_rows if row.snippet.startswith(RENDERED_MARKER)
                ]
                bound_reports.append(
                    f"{source_key} ({reason}: {len(source_rows)} row(s) ungraded here; "
                    f"{len(recommendation_rows)} cite a recommendation identifier and lose "
                    "its membership pin, and their class cell is ungraded because a bound "
                    f"record carries no class; all {len(source_rows)} keep tier 1, and tier 2 "
                    f"grades all but the {len(rendered_rows)} bound-source row(s) that "
                    f"declare {RENDERED_MARKER} -- "
                    f"{len(rendered_recommendations)} of those {len(recommendation_rows)})"
                )
            continue

        source_rows = [candidate for candidate in sheet.rows if candidate.source == source_key]
        narrative_rows = [
            row
            for row in source_rows
            if (locator := source_locator(row.rec)) is not None and locator.is_narrative
        ]
        recommendations: dict[str, list[dict]] = {}
        recommendation_texts_by_page: dict[int, list[str]] = {}
        incomplete_narrative_population = 0
        for item in record.get("recommendations", []):
            if not isinstance(item, dict):
                incomplete_narrative_population += 1
                continue
            if item.get("rec_id"):
                recommendations.setdefault(str(item["rec_id"]), []).append(item)
            page = item.get("page")
            text = str(item.get("text") or "")
            if isinstance(page, int) and text.strip():
                recommendation_texts_by_page.setdefault(page, []).append(text)
            else:
                incomplete_narrative_population += 1

        ungraded_reasons: list[str] = []
        if narrative_rows and incomplete_narrative_population:
            ungraded_reasons.append(
                "narrative negative check could not read page and text for "
                f"{incomplete_narrative_population} recommendation record item(s)"
            )
        present_rows = [row for row in source_rows if row.rec in recommendations]
        all_present_text_absent = bool(present_rows) and all(
            all(not str(item.get("text") or "").strip() for item in recommendations[row.rec])
            for row in present_rows
        )
        if all_present_text_absent:
            ungraded_reasons.append(
                "recommendation text is absent for "
                f"{len({row.rec for row in present_rows})} cited rec(s)"
            )
        if ungraded_reasons:
            ungraded_sources.append(
                f"{source_key} ({'; '.join(ungraded_reasons)})"
            )

        for row in source_rows:
            locator = source_locator(row.rec)
            is_rendered = row.snippet.startswith(RENDERED_MARKER)
            if is_rendered:
                # Deliberately per graded (exact) source: bound and missing records
                # continued above, so their rows are not in tier 0's denominator.
                rendered += 1
            if locator is not None and locator.is_narrative:
                transcription = (
                    row.snippet.removeprefix(RENDERED_MARKER).strip()
                    if is_rendered
                    else row.snippet
                )
                if any(
                    _normalize(transcription) in _normalize(record_text)
                    for record_text in recommendation_texts_by_page.get(row.page or -1, ())
                ):
                    failures.append(
                        f"{sheet.path.name}:{row.line}  narrative page transcription "
                        f"is already a verbatim run in a recommendation record on p{row.page}; "
                        "use that recommendation locator instead"
                    )
                continue
            if is_rendered:
                continue
            if all_present_text_absent and row.rec in recommendations:
                continue
            occurrences = recommendations.get(row.rec)
            if occurrences is None:
                failures.append(
                    f"{sheet.path.name}:{row.line}  rec '{row.rec}' is not in the exact "
                    f"recommendation record for source '{source_key}'"
                )
                continue
            record_texts = [
                str(item.get("text") or "")
                for item in occurrences
                if str(item.get("text") or "").strip()
            ]
            if not record_texts:
                failures.append(
                    f"{sheet.path.name}:{row.line}  rec '{row.rec}' in exact source "
                    f"'{source_key}' has no text for CITATION tier 0"
                )
                continue
            if not any(_normalize(row.snippet) in _normalize(text) for text in record_texts):
                failures.append(
                    f"{sheet.path.name}:{row.line}  snippet is not in its recommendation "
                    f"record '{row.rec}' for source '{source_key}'"
                )

    if ungraded_sources:
        detailed = bound_reports + [
            source
            for source in ungraded_sources
            if not source.endswith("(source mode is 'bound')")
        ]
        report = [
            "  CITATION tier 0 NOT RUN -- " + "; ".join(detailed),
        ]
        if failures:
            report.append(
                f"                  {len(failures)} refusal(s) on exact source(s) that did run"
            )
    else:
        report = [f"  CITATION tier 0 {len(failures)}"]
    if rendered:
        report.append(
            f"                  {rendered} row(s) on graded exact source(s) declared "
            f"{RENDERED_MARKER} "
            "and were read off the rendered page; recommendation rows skipped tier 0 "
            "and narrative rows ran its same-page negative check"
        )

    return GateResult(
        "CITATION tier 0",
        failures,
        rendered=rendered,
        ungraded=len(ungraded_sources),
        ungraded_sources=ungraded_sources,
        report=tuple(report),
        not_graded=bool(ungraded_sources),
    )


def _citation_tier2_not_run(reason: str) -> GateResult:
    """One unmistakable result for either reason tier 2 could not start."""
    return GateResult(
        "CITATION tier 2",
        skip_reason=reason,
        report=(f"  CITATION tier 2 SKIPPED -- {reason}",),
        stdout=(
            "",
            "  " + "=" * 66,
            "  CITATION TIER 2 DID NOT RUN. This sheet has NOT been checked against",
            "  the source PDFs on this machine. Tier 1 proved each value is in its",
            "  own snippet; nothing here proved the snippet is on the page it cites.",
            "  " + "=" * 66,
        ),
    )


def _hold_tier2_resolution_declaration(
    sheet: Sheet,
    result: GateResult,
    pdf_root: Path | None,
) -> GateResult:
    """Hold tier 2's declaration in both its skipped and live states."""
    if not sheet.resolved_corpus or not sheet.resolved_date:
        result.findings.append(
            f"{sheet.path.name}  CITATION tier 2 has no resolution declaration in "
            "## Scope. A corpus-free reader cannot tell checked once from never checked."
        )
    elif result.skip_reason is None:
        assert pdf_root is not None  # A live tier-2 result can only come from a real root.
        if Path(sheet.resolved_corpus).resolve() != pdf_root.resolve():
            result.findings.append(
                f"{sheet.path.name}  CITATION tier 2 resolved against {pdf_root}, but its "
                f"## Scope declaration names {sheet.resolved_corpus}: a different corpus."
            )
        if sheet.resolved_date > date.today().isoformat():
            result.findings.append(
                f"{sheet.path.name}  CITATION tier 2 resolution date "
                f"{sheet.resolved_date} is in the future."
            )
    if result.skip_reason is None:
        result.report = (f"  CITATION tier 2 {len(result.findings)}", *result.report[1:])
    return result


def gate_citation_tier2(sheet: Sheet, pdf_root: Path | None) -> GateResult:
    """Every snippet must appear on the page it cites.

    The result names failures, the skip reason, and rows declared RENDERED separately.
    That separation is deliberate: "tier 2 did not run at all" and "tier 2
    ran and 3 rows opted out of it" are different events, and a sentinel smuggled
    through the skip channel would have made a sheet that declared every row rendered
    indistinguishable from one graded cleanly.

    A skip is returned rather than raised, and the caller prints it as a banner. The
    whole design of decision 2 is that this **must not be readable as passing**.
    """
    if not sheet.rows:
        return GateResult(
            "CITATION tier 2",
            report=("  CITATION tier 2 NO ROWS",),
        )
    if pdf_root is None or not pdf_root.is_dir():
        return _hold_tier2_resolution_declaration(
            sheet,
            _citation_tier2_not_run(f"source PDFs not found at {pdf_root}"),
            pdf_root,
        )
    try:
        import pymupdf
    except ImportError:
        return _hold_tier2_resolution_declaration(
            sheet,
            _citation_tier2_not_run("pymupdf is not installed"),
            pdf_root,
        )

    failures: list[str] = []
    rendered = 0
    cache: dict[tuple[str, int], str] = {}
    for row in sheet.rows:
        if row.snippet.startswith(RENDERED_MARKER):
            # A page transcription is licensed by a declared render-and-read, not by
            # verbatim identity with the text stream. Tier 2 therefore has no snippet
            # claim to check even when the transcription happens to extract cleanly.
            rendered += 1
            continue
        source = sheet.sources.get(row.source)
        if not source or row.page is None:
            continue  # already a SCHEMA failure; not counted twice
        relative = source["document"]
        key = (relative, row.page)
        if key not in cache:
            path = pdf_root / f"{relative}.pdf"
            if not path.is_file():
                failures.append(f"{sheet.path.name}:{row.line}  no such PDF: {path}")
                cache[key] = ""
                continue
            document = pymupdf.open(str(path))
            try:
                page = document[row.page - 1]
                raw = page.get_text("rawdict")
                operators = guidelines_extract.rendered_operator_map_for_page(page, raw)
                cache[key] = _normalize(guidelines_extract.rebuild_text(raw, operators))
            except Exception as error:  # noqa: BLE001
                failures.append(f"{sheet.path.name}:{row.line}  page {row.page} unreadable: {error}")
                cache[key] = ""
            finally:
                document.close()
        page_text = cache[key]
        if page_text and _normalize(row.snippet) not in page_text:
            failures.append(
                f"{sheet.path.name}:{row.line}  snippet not on {relative} p.{row.page}"
            )
    report = [f"  CITATION tier 2 {len(failures)}"]
    if rendered:
        report.append(
            f"                  {rendered} row(s) declared {RENDERED_MARKER} "
            "and were read off the rendered page, so tier 2 skipped them"
        )
    return _hold_tier2_resolution_declaration(
        sheet,
        GateResult(
            "CITATION tier 2",
            failures,
            rendered=rendered,
            report=tuple(report),
        ),
        pdf_root,
    )


def _normalize(text: str) -> str:
    """Whitespace-flattened and dash-folded, for comparing a snippet to a page.

    A snippet is copied out of a table cell and the page sets the same words with a
    line break in the middle of them; comparing raw would fail on typography rather
    than on the citation. Nothing here touches a digit.
    """
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
    text = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()



# The owner returns valid documents and problems together. WATERMARK is the tolerant
# consumer: one bad sibling no longer discards every probe, while the count printed
# below makes the weaker posture visible on every run.
read_extraction = guidelines_manifest.read


def usable_probes(entry: guidelines_manifest.Record, body: str) -> dict[str, str]:
    """The strings #80 stripped from this document that can serve as probes.

    Returns ``{normalized probe: the string as the manifest records it}``.

    **The discrimination is measured and there is deliberately no constant in it.**
    A stripped string is a usable probe only where it does *not* otherwise occur in
    the document's own extracted body -- because a string the extractor removes in
    one place and keeps in another proves nothing at all by appearing in a snippet.

    That rule replaced two heuristics that were tried against the corpus first and
    both fail, which is why it is written down rather than left as taste. Keying on
    length, or on the longest run of letters, cannot separate ``JAMA`` -- stripped as
    a running head from seventeen AHA/ACC documents and occurring up to 52 times in
    the body of one of them -- from ``Jones et al``, which is the same shape and is
    the welded running head gate 4 exists to find. The same threshold has to keep a
    document's own title, stripped as a page-repeated line while the body states it
    too, and drop a bare folio like ``S37``. No cut point does all three; the body
    test does all three by construction. #83's own lesson from
    ``SPACE_ADVANCE_FRACTION`` is that naming a value at an edge is how a constant
    goes wrong, and the value here is that there is no constant to name.

    **Those two counts are stated here and deliberately nowhere else.** They are
    measured against a corpus outside this repo, so nothing committed
    re-derives them, and a copy in ``CLAUDE.md`` or in ``reference/thresholds/README.md``
    is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) --
    which is what the first draft of this change did, in three places each, inside a
    paragraph asserting the figure was stated once. Re-derive by running
    ``tools/guidelines_extract.py`` and counting over ``manifest.json``.

    **Both fields, which is #100 and #174's own comment.** ``boilerplate`` holds what
    the literal 75% rule took and ``margin_stripped`` what the margin rule took; a
    detector reading only the first misses the whole margin rule and reports a clean
    gate, which is gate 4's failure shape arriving in gate 4's input. **How much that
    is, and which documents lose a welded running head rather than a folio, are
    `guidelines_extract.py`'s figures to state** -- CLAUDE.md already rules them not
    to be repeated, and prose is what interleaves, which is the part that matters
    here.

    Matching is substring on both sides and through ``_normalize``, so the body test
    and the row test are the same test asked of two different strings -- a probe that
    only ever occurs inside a longer word in the body is dropped by the same rule
    that would have fired on it in a snippet.
    """
    normalized_body = _normalize(body)
    probes: dict[str, str] = {}
    for field_name in ("boilerplate", "margin_stripped"):
        for stripped in getattr(entry, field_name) or ():
            probe = _normalize(str(stripped))
            if probe and probe not in normalized_body:
                probes[probe] = str(stripped)
    return probes


def _watermark_not_run(
    reason: str,
    *,
    diagnostics: tuple[str, ...],
    tier2_skip_diagnostics: tuple[str, ...] = (),
    fatal: bool = False,
) -> GateResult:
    """Build the shared absent-corpus result while retaining its distinct metadata."""
    return GateResult(
        "WATERMARK",
        skip_reason=reason,
        report=(f"  WATERMARK       NOT RUN -- {reason}",),
        stdout=(
            "",
            "  " + "=" * 66,
            "  WATERMARK DID NOT RUN. Nothing checked whether a string #80 stripped",
            "  as page-repeated text was interleaved into a row. Rebuild the",
            "  extracted corpus with tools/guidelines_extract.py, or pass --text-root.",
            "  " + "=" * 66,
        ),
        diagnostics=diagnostics,
        tier2_skip_diagnostics=tier2_skip_diagnostics,
        fatal=fatal,
    )


def gate_watermark(
    sheet: Sheet,
    text_root: Path | None,
    *,
    allow_untrusted_provenance: bool = False,
) -> GateResult:
    """Gate 4. A row carrying a string #80 stripped is a row the text stream interleaved.

    The result names findings, the skip reason, rows declared RENDERED, and source
    keys not probed.

    #83 states it: *"If a string stripped by #80 appears inside an extracted table
    row, that row is suspect and must be read off the rendered page. Cannot verify a
    reading; flags every place the text stream was interleaved."* The ``RENDERED:``
    marker shipped with #83 as the **declaration** half. This is the detection half,
    and until [#174](https://github.com/mshamblin5150-code/clinical-skills/issues/174)
    nothing told a writer that a given row needed it.

    **It refuses until a working agent confirms the rendered page.** The clinician
    ruled the posture on
    [#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296): a
    vision-capable agent, rather than the clinician, renders the cited page and
    confirms that the label and value belong together. ``RENDERED:`` records that
    visual check. An incorrect or ambiguous row remains refusing until corrected.

    **How much a refusal would change is smaller than this said**, and the overstated
    version was a stated ground for deferring, which is what makes it worth recording
    rather than quietly correcting. It read *"the third thing in this repo that can
    refuse a commit"*, in four files. ``tools/hooks/pre-commit`` already calls
    ``threshold_sheet.py`` **the second thing in this repo that can refuse a commit**,
    invoked once under one staging condition -- so a gate-4 refusal adds no tool, no
    invocation and no exit path, only another **reason** an existing refuser exits
    non-zero. One figure copied into four files, inside a change whose own prose cites
    #143 twice; found by the tracker sweep on
    [#111](https://github.com/mshamblin5150-code/clinical-skills/issues/111).

    **Every probe that hits, not the first.** #83 asks for *every place*, and a row
    can carry two stripped strings -- a running head and a folio land on one line
    often enough that stopping at the first would report one and read as the whole.

    **A declared row is exempt and counted, not refused.** The remedy #83 names for a
    suspect row *is* to read it off the rendered page, so refusing a row that says it
    did would leave the gate unsatisfiable. The count is printed on tier 2's terms:
    the trace the hatch exists to leave is worth nothing if the run honoring it stays
    silent. **That does mean one marker buys out of two gates**, which is named here
    rather than discovered -- both exemptions are counted and both print.

    **An absent corpus is a skip and never a pass**, on ``gate_citation_tier2``'s
    arrangement rather than ``gate_coverage``'s, and the asymmetry is deliberate. The
    extracted text lives outside every checkout, so a fresh clone, a worktree and CI
    all have nothing to probe; making that a refusal would add a second reason the
    pre-commit hook turns away someone fixing a prose typo, which
    ``reference/thresholds/README.md`` already names as a cost landing on people who
    have done nothing wrong. The caller prints a banner it is meant to be hard to
    read past.

    **A source that was reached but could not be probed is neither.** A document with
    no manifest entry, no extracted text on disk, or no usable probe at all is
    returned in the fourth value and printed, because a sheet citing one is a sheet
    this gate said nothing about. A silent zero there is the shape
    ``differential_scan.py`` and every scanner after it exists to refuse. **How many
    have no usable probe is stated once, in
    ``reference/thresholds/README.md``**, where the command that re-derives it sits
    beside it -- it is measured against a corpus outside this repo, so a second copy
    is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).
    """
    if not sheet.rows:
        return GateResult(
            "WATERMARK",
            report=("  WATERMARK       NO ROWS",),
        )
    if text_root is None:
        reason = f"extracted corpus not found at {text_root}"
        return _watermark_not_run(
            reason,
            diagnostics=("  WATERMARK       1 manifest problem(s)",),
        )
    text_root = Path(text_root)
    handoff = read_extraction(
        text_root,
        allow_untrusted_provenance=allow_untrusted_provenance,
    )
    manifest_diagnostic = (
        f"  WATERMARK       {len(handoff.problems)} manifest problem(s)"
    )
    manifest = handoff.documents
    if not manifest:
        reason = (
            "; ".join(problem.message for problem in handoff.problems)
            or f"no {guidelines_manifest.MANIFEST_NAME} under {text_root}"
        )
        fatal = text_root.is_dir()
        return _watermark_not_run(
            reason,
            diagnostics=(manifest_diagnostic,),
            tier2_skip_diagnostics=(f"  WATERMARK       NOT RUN -- {reason}",),
            fatal=fatal,
        )

    probes_for: dict[str, dict[str, str]] = {}
    unprobed: list[str] = []
    for key in sorted(sheet.sources):
        document = guidelines_manifest.normalize_doc_id(
            sheet.sources[key].get("document", "")
        )
        entry = manifest.get(document)
        if entry is None:
            unprobed.append(key)
            continue
        pages = handoff.pages.get(document)
        if pages is None:
            unprobed.append(key)
            continue
        probes = usable_probes(entry, "\f".join(pages))
        if not probes:
            unprobed.append(key)
            continue
        probes_for[key] = probes

    findings: list[str] = []
    rendered = 0
    for row in sheet.rows:
        probes = probes_for.get(row.source)
        if not probes:
            continue
        if row.snippet.startswith(RENDERED_MARKER):
            rendered += 1
            continue
        # Both cells, because #83 says *inside an extracted table row* and both of
        # them are transcribed off the same page.
        transcribed = _normalize(f"{row.value} {row.snippet}")
        for probe, recorded in sorted(probes.items()):
            if probe in transcribed:
                findings.append(
                    f"{sheet.path.name}:{row.line}  the row carries {recorded!r}, which #80 "
                    f"stripped from {_document_of(sheet, row)} as "
                    f"page-repeated text. The text stream was interleaved here, so read "
                    f"this row off the rendered page and declare {RENDERED_MARKER}."
                )
    declaration_verdict = artifact_provenance.grade_accepted_distrust(
        sheet.accepted_distrust,
        handoff.root,
        handoff.provenance,
        passed=not findings and not unprobed,
    )
    findings.extend(declaration_verdict.failures)
    report = [f"  WATERMARK       {len(findings)} refusing"]
    if declaration_verdict.not_graded:
        report = [
            "  WATERMARK       NOT GRADED -- the untrusted pass is not declared in "
            "the sheet's ## Scope",
        ]
    if rendered:
        report.append(
            f"                  {rendered} row(s) declared {RENDERED_MARKER}, "
            "so the interleave test skipped them"
        )
    if unprobed:
        report.append(
            f"                  NOT PROBED for {len(unprobed)} of {len(sheet.sources)} "
            f"source(s): {', '.join(unprobed)} -- so the count above is a floor"
        )
    diagnostics = (manifest_diagnostic,) + tuple(
        f"  WATERMARK       NOT PROBED for source '{key}' -- no manifest entry, no "
        "extracted text, or no string stripped from it that could serve as a probe"
        for key in unprobed
    )
    if declaration_verdict.not_graded:
        diagnostics += (
            "  WATERMARK       NOT GRADED -- add this declaration under ## Scope:\n"
            + str(declaration_verdict.expected),
        )
    return GateResult(
        "WATERMARK",
        findings,
        rendered=rendered,
        unprobed_sources=unprobed,
        report=tuple(report),
        diagnostics=diagnostics,
        not_graded=declaration_verdict.not_graded,
    )


# The line gate 5 prints on every run it makes, clean or not. #83 states the caveat
# in the same breath as the gate -- *"weakness is correlated error, same model, same
# PDF, same mangling, same wrong answer, so it is a strong smoke test and must be
# documented as one, never as proof"* -- and #174 calls that a build instruction.
#
# **It prints on a clean run too, which is the only run where anybody would mistake
# it for proof.** A caveat that appears beside a failure is a caveat nobody needs.
SECOND_READ_IS_A_SMOKE_TEST = (
    "a second read is a smoke test and never proof: the same model over the same PDF "
    "mangles it the same way, so agreement is cheap"
)

BLIND_READ_IS_A_SMOKE_TEST = (
    "a blind read is a smoke test in the clean direction: two readers can miss the "
    "same decision point"
)


class DeclaredLimit(NamedTuple):
    """One named coverage boundary and how its evidence is maintained."""

    key: str
    limit: str
    evidence: EvidenceDisposition


# The complete coverage inventory, derived by an end-to-end read of this module and
# its ratified records on 2026-08-30. Later prose-only boundaries remain reader-owned.
# The ADR 0046 rows stay contiguous so its surviving view can select one key-bounded
# span instead of maintaining the same membership a second time.
DECLARED_LIMITS = (
    DeclaredLimit(
        "unread spans omitted from Not read",
        "Nothing checks that the summary names every unread span; this is the "
        "direction in which a wrong summary misleads a clinician.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "compound span labels",
        "A compound span label such as X and Y is split at and, so the complete "
        "label is never compared as one item.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "sentences after the first",
        "Only the first sentence after Not read is parsed as the list; later "
        "sentences are outside the comparison.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "unread spans named under Read",
        "An unread span named under Read is not graded, and no committed sheet "
        "provides an instance on which to key that mirror rule.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "class-retirement placement",
        "Putting class-retired material under Read is a convention only; correct "
        "sheets may describe a reference list without repeating its span label.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "items that are not span labels",
        "A scope-summary item that is not a span label is compared in neither "
        "direction and remains a reading.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "null-sheet wording",
        "The ruled null-sheet wording is not a span label and is compared in neither "
        "direction. On a legal null sheet, any real span named under Not read refuses.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "misdrawn span boundaries",
        PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES,
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "row-source-meaning-unverified",
        "No gate can prove that a threshold row says what its cited source passage says.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "population-key-correctness-unverified",
        "SCHEMA checks that a population key is declared, never that the key describes "
        "the right patients.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "scope-out-reason-ungraded",
        "COVERAGE requires a scope-out reason but cannot grade whether the reason is sound.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "bound-record-membership-ungraded",
        WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED,
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "duplicate-rec-id-occurrences-ungraded",
        "COVERAGE grades recommendation identifier membership, not separate occurrences "
        "that repeat one identifier.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "source-free-scope-out-membership-ungraded",
        "A source-free scope-out is not membership-graded when any declared source is "
        "bound or ungraded.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "second-read-agreement-unproven",
        SECOND_READ_IS_A_SMOKE_TEST,
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "null-span-token-grades-claim-only",
        "NULL SPAN grades the committed token claiming corroboration and never the "
        "read that token describes.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "blind-read-independence-unverified",
        "Nothing checks that the blind reader was a second reader, was briefed cold, "
        "or did not open the threshold sheet.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "blind-read-shared-miss-unverified",
        BLIND_READ_IS_A_SMOKE_TEST,
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "null-span-coverage-auditor-unreached",
        "The NULL SPAN refusal is outside threshold_coverage.py, whose threshold-sheet "
        "report reads gate_schema findings only.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "transcribed-blind-token-accuracy-unverified",
        "A blind token transcribed from a sheet's prose is only as accurate as the "
        "reader-authored sentence it copies.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "download-address-reachability-unverified",
        "SCHEMA checks that a Download address is an HTTP(S) address but never opens it, "
        "so a clean run proves neither reachability nor resistance to link rot.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "download-basis-evidence-not-replayed",
        "SCHEMA validates the Download basis vocabulary and date shape but does not "
        "replay a fetch, authenticated-route attempt, or digest comparison. Byte "
        "identity is sufficient for a match and byte inequality does not prove that "
        "the content differs.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "cross-topic-source-membership-unchecked",
        "No gate checks whether a source document belongs to the sheet's topic. "
        "threshold_draft reports near-miss documents at draft time only, and only where "
        "the typed topic words appear in the other row's topic or title. A source added "
        "after drafting, or one from an unrelated topic, is surfaced by nothing.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "recommendation-alias-provenance-unverified",
        "The recommendation-record alias carries no artifact record, so a read site "
        "cannot verify that the alias it opened came from the build.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "rowless-source-invisible",
        "A source that yields no threshold rows is invisible to every sheet gate; a "
        "later source version that made its correction relevant would surface nothing.",
        EvidenceDisposition.DECLARED_READING,
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


def _declared_limit_span(first_key: str, last_key: str) -> tuple[DeclaredLimit, ...]:
    """Select one contiguous key-bounded view without copying its membership."""

    keys = tuple(row.key for row in DECLARED_LIMITS)
    first = keys.index(first_key)
    last = keys.index(last_key, first)
    return DECLARED_LIMITS[first:last + 1]


SCOPE_SUMMARY_NOT_REACHED = tuple(
    (row.key, row.limit)
    for row in _declared_limit_span(
        "unread spans omitted from Not read",
        "misdrawn span boundaries",
    )
)

# The fields a second-read entry has to carry. Named here rather than read
# positionally, on `ROW_COLUMNS`' reasoning: an entry short of one is a reader who
# answered a different question, and a `.get` default would file that under agreement.
SECOND_READ_FIELDS = ("document", "page", "value", "about")


@dataclass(frozen=True)
class BriefedSpan:
    """The exact source span assigned to an independent reader."""

    document: str
    span: str
    first_page: int
    last_page: int


@dataclass
class SecondRead:
    """An independent extraction of the pages a sheet cites. ``ok`` is false when it
    could not be read as one at all."""

    path: Path
    values: list[dict] = field(default_factory=list)
    briefed: BriefedSpan | None = None
    read_on: str | None = None
    ok: bool = True
    why_not: str | None = None


def load_second_read_record(loaded: object, path: Path) -> SecondRead:
    """Read a second-read record, or say why it is not one.

    **Every way of being present and unusable is the same event**, which is
    ``bind_recs``' ruling and is here for its reason: ``[]`` and ``{}`` are valid
    JSON and arrive through a door that looks legitimate, and a record understood as
    empty would grade every row against nothing and print a number.

    ``read_on`` is required on ``research_ledger.py``'s dateless-ledger reasoning. A
    read carries no trace of which extraction of the corpus it was taken against, and
    this repo has watched three review agents read one shared build directory that a
    second branch had overwritten -- so a read with no date cannot be told from one
    taken against a corpus that has since moved.
    """
    if not isinstance(loaded, dict):
        return SecondRead(
            path=path, ok=False,
            why_not=f"the file holds a JSON {type(loaded).__name__}, not a second-read record",
        )
    if "values" not in loaded:
        return SecondRead(path=path, ok=False, why_not="no 'values' key, so nothing was read")
    values = loaded.get("values")
    if not isinstance(values, list):
        return SecondRead(
            path=path, ok=False,
            why_not=f"'values' is a {type(values).__name__}, not a list of entries",
        )
    briefed = loaded.get("briefed")
    if not isinstance(briefed, dict):
        return SecondRead(
            path=path, ok=False,
            why_not="no 'briefed' block naming document, span, and page range",
        )
    missing_briefed = [
        name for name in ("document", "span", "pages")
        if not str(briefed.get(name, "")).strip()
    ]
    if missing_briefed:
        return SecondRead(
            path=path, ok=False,
            why_not=f"'briefed' has no {', '.join(missing_briefed)}",
        )
    briefed_range = _SPAN_RANGE.fullmatch(str(briefed["pages"]).strip())
    if briefed_range is None:
        return SecondRead(
            path=path, ok=False,
            why_not=f"'briefed.pages' is not a page range: {briefed['pages']!r}",
        )
    read_on = loaded.get("read_on")
    if not read_on:
        return SecondRead(
            path=path, ok=False,
            why_not="no 'read_on' date, so which extraction of the corpus this was "
                    "taken against is unknowable",
        )
    for position, entry in enumerate(values, start=1):
        if not isinstance(entry, dict):
            return SecondRead(path=path, ok=False, why_not=f"entry {position} is not an object")
        missing = [name for name in SECOND_READ_FIELDS if not str(entry.get(name, "")).strip()]
        if missing:
            return SecondRead(
                path=path, ok=False,
                why_not=f"entry {position} has no {', '.join(missing)}",
            )
        if not _PAGE_DIGITS.search(str(entry["page"])):
            # `_citation` is tolerant of how a page is spelled and this is why it can
            # afford to be: a page with no digit in it is not a page, and letting one
            # through would put the entry under a key no row can ever carry -- which
            # reads as the reader having gone off the brief.
            return SecondRead(
                path=path, ok=False,
                why_not=f"entry {position} has no page number in {entry['page']!r}",
            )
    briefed_first = int(briefed_range.group("first"))
    briefed_last = int(briefed_range.group("last") or briefed_first)
    return SecondRead(
        path=path,
        values=values,
        briefed=BriefedSpan(
            document=str(briefed["document"]).strip(),
            span=str(briefed["span"]).strip(),
            first_page=briefed_first,
            last_page=briefed_last,
        ),
        read_on=str(read_on),
    )


def load_second_read(path: Path) -> SecondRead:
    """``load_second_read_record`` off disk. A path that does not resolve is a typo."""
    if not path.is_file():
        return SecondRead(path=path, ok=False, why_not=f"no such file: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return SecondRead(path=path, ok=False, why_not=f"unreadable: {error}")
    return load_second_read_record(loaded, path)


_PAGE_DIGITS = re.compile(r"\d+")


def _citation(document: str, page: object) -> tuple[str, str]:
    """A ``(document, page)`` key, from either side of the second-read boundary.

    **The page is read as its digits**, which matters only on the untrusted side. A
    sheet's page came through ``parse`` and is an ``int``; a second-read record was
    typed by whoever did the read, off a brief that prints locators as ``p.41`` --
    and ``lstrip("pP")`` left the dot, so a reader copying what the brief showed them
    produced ``.41``, matched no row, and got their work reported as **read off the
    brief**. Blaming a reader for covering exactly what it was sent to is the worst
    failure this gate has, because it is the one that looks like a finding.
    ``load_second_read_record`` refuses an entry whose page carries no digit at all,
    so this is tolerant of a spelling and never of an absence.
    """
    digits = _PAGE_DIGITS.search(str(page))
    return (
        guidelines_manifest.normalize_doc_id(str(document)),
        digits.group(0) if digits else str(page).strip(),
    )


def cited_citations(sheet: Sheet) -> set[tuple[str, str]]:
    """Every ``(document, page)`` a sheet's rows cite.

    Shared by ``brief`` and ``gate_second_read`` rather than written twice, because
    the two have to agree exactly: the brief is what a reader is sent to, and the
    diff decides what that reader covered. Two copies of this comprehension could
    drift into a work order naming a page the grader then reports as off-brief.
    """
    return {
        _citation(_document_of(sheet, row), row.page)
        for row in sheet.rows
        if row.page is not None
    }


def _named_span(sheet: Sheet, name: str) -> Span:
    """Resolve one human span name without guessing between source documents."""
    source, separator, span_name = name.partition(":")
    if not separator:
        source, span_name = "", name
    matches = [
        span for span in sheet.spans
        if span.name.casefold() == span_name.strip().casefold()
        and (not source or span.source.casefold() == source.strip().casefold())
    ]
    if len(matches) != 1:
        qualifier = "<source>:<span>" if len(matches) > 1 else "a declared span"
        raise ValueError(f"{name!r} does not identify exactly one span; name {qualifier}")
    return matches[0]


def _span_pages(span: Span) -> str:
    return (
        str(span.first_page)
        if span.first_page == span.last_page
        else f"{span.first_page}-{span.last_page}"
    )


def brief(sheet: Sheet, span_name: str) -> str:
    """The work order for a second independent read: what to open, and what to write.

    #83 asks for a read *"with no access to the sheet"*. This is what that reader is
    handed, and it carries **document, span, and page range and nothing else** -- no quantity, no
    value, no snippet, no population. A test drives a distinctive string through every
    one of those cells and asserts none of them comes out here.

    **Naming the pages is a leak and it is named rather than left implied.** A page
    number is a locator and not an answer, and without one the second reader has a
    hundred-page guideline to search, at which point the diff measures how thoroughly
    it searched rather than what it read. The narrower a locator gets the more the
    read is steered, and page is the widest one that makes the task finite.
    """
    span = _named_span(sheet, span_name)
    document = sheet.sources[span.source]["document"]
    pages = _span_pages(span)
    lines = [
        "== a second independent span read",
        "",
        f"  document: {document}",
        f"  span: {span.name}",
        f"  pages: {pages}",
        "",
        "Open the page range above in the source PDF and extract EVERY threshold, target,",
        "cutoff, dose and interval it states. Do not consult the threshold sheet: this",
        "read is worth what its independence is worth.",
    ]
    lines += [
        "",
        "Write the result as JSON:",
        "",
        '  {"read_on": "<YYYY-MM-DD>",',
        '   "briefed": {"document": "<as above>", "span": "<as above>",',
        '                "pages": "<as above>"},',
        '   "values": [{"document": "<as above>", "page": <n>,',
        '               "value": "<the threshold as the page states it>",',
        '               "about": "<what this number is the threshold FOR, in your own',
        '                          words, from the page and not from any sheet>"}]}',
        "",
        f"  {SECOND_READ_IS_A_SMOKE_TEST}.",
    ]
    return "\n".join(lines) + "\n"


def gate_second_read(
    sheet: Sheet, read: SecondRead | None
) -> GateResult:
    """Gate 5, with each outcome carried in a named ``GateResult`` field.

    #83: *"A subagent extracts the same table with no access to the sheet; the diff
    is the gate. The only mechanism that catches misreading rather than
    miscitation."*

    **Correlated error weakens the pass and not the fail, and that is why a
    disagreement may refuse.** #83's caveat -- same model, same PDF, same mangling,
    same wrong answer -- says that two readers agreeing is cheap. It does not say
    that two readers disagreeing is cheap, because correlation is not something that
    manufactures a disagreement. So the refusal is sound and the *clean* result is
    the weak half, which is why ``SECOND_READ_IS_A_SMOKE_TEST`` prints on a clean run.

    **The diff is on numbers and never on words**, which is ``gate_citation_tier1``'s
    instrument and ``research_ledger.py``'s ruling arriving together. The second
    reader writes in the source's own terms by design, so a string comparison would
    refuse the correct answer; what a row asserts that a machine can check is its
    numbers, at the citation it names.

    **The misreading limb is a pairing and is deliberately not graded.** The hole
    this module's own docstring names -- *a sheet whose numbers are all real and all
    filed under the wrong heading passes every gate here* -- is closed by comparing
    the row's ``quantity`` and ``population`` to what the independent reader said the
    number was **about**. Those are two free-text descriptions and comparing them is
    a reading, so they are set side by side and neither is graded. A green gate 5 is
    not a read pairing list.

    **An unmatched second-read value only warns**, on ``gate_coverage``'s bound rule:
    the independent reader has no access to ``## Coverage``, so it cannot know what
    was scoped out and it over-reports by construction.

    **A row whose value carries no number is returned as undiffed rather than
    passed** -- ``monthly``, ``at every visit``. ``gate_range`` returns its ungraded
    count for the same reason: a gate that grades four of a sheet's numbers and
    reports a clean run is #153's shape.

    **A citation the read did not cover at all is uncovered and never a refusal**,
    which is the fifth value and was wrong in the first version. A read of three
    pages of a sheet citing thirty refused sixty-odd rows for values it had never
    looked for -- a confident finding about pages nobody opened, which is #153's
    shape with the sign flipped and is exactly how a gate gets learned around. A
    refusal now needs the read to have **been on that page**; anything else is
    reported, counted, and makes the refusal count a floor. Found by running the gate
    against the committed sheet rather than by a fixture, which is where both of
    ``gate_range``'s false alarms came from too.
    """
    if read is None:
        return GateResult(
            "SECOND READ",
            report=(
                "  SECOND READ     NOT RUN -- no --second-read given; --brief --span prints the work order",
            ),
        )
    if not read.ok:
        reason = str(read.why_not)
        return GateResult(
            "SECOND READ",
            report=(f"  SECOND READ     NOT RUN -- {reason}",),
            diagnostics=(f"  SECOND READ     NOT RUN -- {read.path}: {reason}",),
            not_graded=True,
        )

    assert read.briefed is not None
    briefed_document = guidelines_manifest.normalize_doc_id(read.briefed.document)
    matching_spans = [
        span for span in sheet.spans
        if guidelines_manifest.normalize_doc_id(sheet.sources.get(span.source, {}).get("document", ""))
        == briefed_document
        and span.name.casefold() == read.briefed.span.casefold()
        and span.first_page == read.briefed.first_page
        and span.last_page == read.briefed.last_page
    ]
    if len(matching_spans) != 1:
        reason = "the 'briefed' block does not name exactly one declared span"
        return GateResult(
            "SECOND READ",
            report=(f"  SECOND READ     NOT RUN -- {reason}",),
            diagnostics=(f"  SECOND READ     NOT RUN -- {read.path}: {reason}",),
            not_graded=True,
        )
    span = matching_spans[0]

    refusals: list[str] = []
    warnings: list[str] = []
    pairings: list[str] = []
    undiffed: list[str] = []
    uncovered: list[str] = []

    cited = {
        _citation(briefed_document, page)
        for page in range(span.first_page, span.last_page + 1)
    }
    by_citation: dict[tuple[str, str], list[dict]] = {}
    for entry in read.values:
        key = _citation(entry["document"], entry["page"])
        if key not in cited:
            warnings.append(
                f"{read.path.name}  a value was read on {key[0]} p.{key[1]}, which this "
                f"sheet cites nowhere: {entry['value']!r} -- read off the brief, so "
                "nothing here diffs it"
            )
            continue
        by_citation.setdefault(key, []).append(entry)

    # By position rather than by ``id()``: two entries of a read can be equal dicts,
    # and identity is not what "this entry answered a row" means.
    matched: set[tuple[tuple[str, str], int]] = set()
    span_rows = _rows_cited_within_span(sheet, span)
    # A dated marker is the span's explicit null claim. Page ranges may overlap, so
    # a row on one of these pages can belong to another span and must not silently
    # turn this marker into a positive read.
    null_span = span.has_dated_marker or span.exemption_reason is not None
    if null_span:
        for key in sorted(by_citation):
            for entry in by_citation[key]:
                refusals.append(
                    f"{sheet.path.name} span '{span.name}' was retired as null, but the "
                    f"independent read found {entry['value']!r} on {key[0]} p.{key[1]}"
                )

    for row in (() if null_span else span_rows):
        wanted = _NUMBER.findall(row.value)
        where = f"{sheet.path.name}:{row.line}"
        if not wanted:
            undiffed.append(f"{where}  value {row.value!r} carries no number to diff")
            continue
        if row.page is None:
            continue  # already a SCHEMA failure; not counted twice
        key = _citation(_document_of(sheet, row), row.page)
        if key not in by_citation:
            warnings.append(
                f"{where}  the independent reader found nothing matching value "
                f"{row.value!r} in briefed span '{span.name}'"
            )
            continue
        found = None
        # **Every entry a row satisfies is marked, not only the one it pairs with.**
        # A guideline states one threshold in two places on a page and a sheet carries
        # it as two rows for two populations, so the read comes back with duplicate
        # values at one citation. Marking only the entry the loop broke on left the
        # duplicates unconsumed and reported them as "no row carries this" -- 20 false
        # warnings on the committed sheet against a read built from its own rows.
        # Marking all of them is the direction that adds no false refusal: the row is
        # still paired with the first, and an entry stays unmatched only where NO row
        # accounts for it, which is what the warning claims.
        for position, entry in enumerate(by_citation.get(key, ())):
            present = set(_NUMBER.findall(str(entry["value"])))
            if all(number in present for number in wanted):
                matched.add((key, position))
                if found is None:
                    found = entry
        if found is None:
            warnings.append(
                f"{where}  the independent reader did not find value {row.value!r} "
                f"on {key[0]} p.{key[1]} in briefed span '{span.name}'"
            )
            continue
        pairings.append(
            f"{where}  {row.quantity} / {row.population}  ||  {found['about']}"
        )

    for key in sorted(by_citation):
        for position, entry in enumerate(by_citation[key]):
            if (key, position) not in matched:
                warnings.append(
                    f"{read.path.name}  {key[0]} p.{key[1]} states {entry['value']!r} "
                    f"({entry['about']}) and no row carries it -- the independent read "
                    "cannot see '## Coverage', so this over-reports"
                )
    report = (
        f"  SECOND READ     {len(refusals)} refusing, {len(warnings)} warning "
        f"over {len(read.values)} value(s) read on {read.read_on}",
        f"                  span '{span.name}' pages {_span_pages(span)}; "
        f"{len(undiffed)} row(s) carried no number to diff",
    )
    stdout = (f"                  {SECOND_READ_IS_A_SMOKE_TEST}",)

    return GateResult(
        "SECOND READ",
        refusals,
        warnings,
        pairings,
        undiffed,
        uncovered,
        report=report,
        stdout=stdout,
        not_graded=False,
        report_after_stdout=tuple(
            f"                  {pairing}" for pairing in pairings
        ),
        stdout_before_footer=True,
    )

def bind_recs(
    sheet: Sheet,
    arguments: list[str],
    recs_root: Path | None,
    *,
    allow_untrusted_provenance: bool = False,
    recs_alias: Path | None = None,
    corpus_documents: set[str] | frozenset[str] = frozenset(),
) -> BoundRecommendationRecords:
    """Which recommendation record answers for each source the sheet declares.

    Returns ``({source key: record or None}, {source key: why there is none},
    [argument errors], {source keys whose lookup-root record was never built})``.

    **Per source and not per sheet, which is #177.** A sheet citing two societies used
    to be graded against whichever single record ``--recs`` named, and the other
    source's omissions went unchecked with nothing saying so -- the ungraded signal
    was derived from ``recs is None`` and so could not exceed 1 however many sources
    were skipped. The `source` column exists because #83 decision 3 makes
    multi-source the normal case: one row per society, with a ``CONFLICT`` block where
    they disagree.

    An argument is ``KEY=PATH``, or a bare path **only** where the sheet declares
    exactly one source. A bare path on a two-source sheet is an error rather than a
    guess, because guessing which source a record answers for is the defect this
    function exists to remove.

    **The lookup stays outside the repo.** The sweep alias resolves ``<doc_id>.json``
    first, then ``recs_root`` fills a gap with exact ``recs-<key>.json`` lookup. There
    is deliberately no fallback to the sheet's own directory: a record holds the
    society's recommendation text in full, which is the copyrighted expression the
    sheet format exists to avoid committing. A convenience that looked beside the
    sheet would quietly invite someone to put one there to make ``--all`` work.
    """
    errors: list[str] = []
    explicit: dict[str, Path] = {}
    for argument in arguments or ():
        key, separator, raw = str(argument).partition("=")
        if not separator:
            if len(sheet.sources) != 1:
                errors.append(
                    f"--recs {argument} names no source key, and the sheet declares "
                    f"{len(sheet.sources)} sources ({', '.join(sorted(sheet.sources)) or 'none'}), "
                    "so which source it answers for is unknowable. Write --recs <key>=<path>."
                )
                continue
            key, raw = next(iter(sheet.sources)), argument
        if key not in sheet.sources:
            errors.append(
                f"--recs names source '{key}', which the sheet does not declare under "
                f"'## Sources' ({', '.join(sorted(sheet.sources)) or 'none'}). A record "
                "bound to nothing checks nothing."
            )
            continue
        if key in explicit:
            errors.append(f"--recs names source '{key}' twice")
            continue
        explicit[key] = Path(raw)

    records: dict[str, dict | None] = {}
    why_not: dict[str, str] = {}
    missing_records: set[str] = set()
    untrusted_records: set[str] = set()
    locations: dict[str, RecommendationRecordLocation] = {}
    for key in sorted(sheet.sources):
        path = explicit.get(key)
        named = path is not None
        if path is None:
            location = locate_recommendation_record(
                document=sheet.sources[key].get("document", ""),
                key=key,
                recs_alias=recs_alias,
                recs_root=recs_root,
                corpus_documents=corpus_documents,
            )
            path = location.path
            locations[key] = location
        else:
            locations[key] = RecommendationRecordLocation(
                path,
                RecommendationRecordOrigin.EXPLICIT_ARGUMENT,
            )
        records[key] = None
        if path is None:
            why_not[key] = "no --recs given for this source, so omission was not checked"
        elif not path.is_file():
            # The typo and the never-built record are not the same event, which is
            # `TheExitStatusSaysWhichKindOfNotGraded`'s finding read one level down: a
            # path somebody typed that does not resolve is a mistake, and a record
            # nobody has built yet is a machine without the corpus.
            why_not[key] = (
                f"no such file: {path}" if named else f"no recommendation record at {path}"
            )
            if not named:
                missing_records.add(key)
        else:
            try:
                loaded = load_recommendation_record(
                    path, allow_untrusted=allow_untrusted_provenance
                )
            except UntrustedRecommendationRecord as error:
                why_not[key] = f"untrusted record: {'; '.join(error.reasons)}"
                untrusted_records.add(key)
            except (OSError, ValueError) as error:
                why_not[key] = f"unreadable recommendation record {path}: {error}"
            else:
                # **A file that parses and is not a record is the same event as one
                # that does not parse**, and it arrives through a door that looks
                # legitimate: `null` and `[]` are valid JSON. Untyped, `null` left
                # `records[key]` None with no `why_not` entry and the report raised a
                # KeyError, and `[]` reached `gate_coverage` and raised there. A
                # traceback out of the pre-commit hook is not a verdict.
                if isinstance(loaded, dict):
                    records[key] = loaded
                else:
                    why_not[key] = (
                        f"unreadable recommendation record {path}: "
                        f"the file holds a JSON {type(loaded).__name__}, not a record"
                    )
    # **The invariant the report reads is that every absent record says why**, and it
    # is pinned by a test rather than asserted here: it was false for one branch --
    # the JSON `null` above -- and the symptom was a KeyError in `grade` rather than
    # anything a reader could act on. `EveryAbsentRecordSaysWhy` walks all four ways
    # of not having one.
    return BoundRecommendationRecords(
        records,
        why_not,
        errors,
        missing_records,
        untrusted_records,
        locations,
    )


def gate_coverage(
    sheet: Sheet,
    records: dict[str, dict | None],
    why_not: dict[str, str] | None = None,
    recs_errors: list[str] | tuple[str, ...] = (),
    missing_records: set[str] | frozenset[str] = frozenset(),
    untrusted_records: set[str] | frozenset[str] = frozenset(),
) -> GateResult:
    """Gate 2, naming refusals, warnings, and ungraded source keys in its result.

    Refuses on an ``exact`` source and warns on a ``bound`` one, and **the mode is
    read off the recommendation record rather than decided here** -- what makes a
    count enforceable is that the recommendations were ruled into a table, not that
    the number looked tidy.

    **Every row check in here is per source since #177**: ``known`` is filtered to
    the rows citing that source, the mode cross-check compares a source's declaration
    against its own record, and the class check reads the record of the source the row
    cites. Scope-outs have no source key, so their membership is checked against the
    union only when every source record is exact. Records can repeat a ``rec_id``
    within one document, and separate documents can share one too. This gate grades
    identifier-level accounting per source; it does not claim occurrence-level
    coverage for duplicate identifiers.
    """
    refusals: list[str] = []
    warnings: list[str] = []
    ungraded: list[str] = []

    narrative_rows = [
        row
        for row in sheet.rows
        if (locator := source_locator(row.rec)) is not None and locator.is_narrative
    ]
    rendered_narrative_rows = [
        row for row in narrative_rows if row.snippet.startswith(RENDERED_MARKER)
    ]
    for row in sheet.rows:
        locator = source_locator(row.rec)
        if locator is None:
            continue
        class_is_narrative = row.klass.strip().casefold() == NARRATIVE_KIND
        if locator.is_narrative and not class_is_narrative:
            refusals.append(
                f"{sheet.path.name}:{row.line}  a narrative source locator must carry "
                "class 'narrative'"
            )
        elif not locator.is_narrative and class_is_narrative:
            refusals.append(
                f"{sheet.path.name}:{row.line}  class 'narrative' is reserved for a "
                "narrative source locator"
            )

    for key in sorted(sheet.sources):
        recs = records.get(key)
        if recs is None:
            ungraded.append(key)
            continue

        mode = recs.get("mode")
        known = {record["rec_id"] for record in recs.get("recommendations", ())}
        rows = [row for row in sheet.rows if row.source == key]
        unaccounted = sorted(known - {row.rec for row in rows} - set(sheet.scoped_out))

        narrative_collisions = sorted(
            rec_id
            for rec_id in known
            if (locator := source_locator(str(rec_id))) is not None
            and locator.is_narrative
        )
        for rec_id in narrative_collisions:
            refusals.append(
                f"{sheet.path.name}  source '{key}' recommendation record collision: "
                f"'{rec_id}' uses the reserved narrative kind"
            )

        # **Structural findings, and they refuse whatever the mode is.** The
        # refuse-or-warn split exists because a marker COUNT over-reports; it says
        # nothing about whether a sheet's own declarations are self-consistent.
        # Routing these through it would let a bound source declare itself exact and
        # carry a mis-pinned class unremarked.

        # **The sheet's declared mode must agree with the record's, and a disagreement
        # is a refusal rather than a preference for one of them.** README.md tells a
        # reader that `mode` is what decides whether omissions are refused or warned
        # about; a sheet declaring `exact` over a `bound` record would make that
        # sentence false while every gate passed. Neither value is trusted over the
        # other because only the disagreement is knowable -- what produced it is not.
        built_from = record_built_from_another_document(
            recs, sheet.sources[key].get("document", "")
        )
        if built_from:
            refusals.append(
                f"{sheet.path.name}  source '{key}' names document "
                f"'{sheet.sources[key].get('document', '').strip()}' but its recommendation "
                f"record was built from '{built_from}'. A record bound to the wrong source "
                "grades that source against another guideline."
            )

        declared = sheet.sources[key].get("mode", "").strip().lower()
        if declared and mode and declared != mode:
            refusals.append(
                f"{sheet.path.name}  source '{key}' declares mode '{declared}' but its "
                f"recommendation record is '{mode}'. README.md says mode decides whether "
                f"omission refuses or warns, so these cannot disagree."
            )

        if mode == MODE_EXACT:
            for row in rows:
                locator = source_locator(row.rec)
                if locator is not None and locator.is_narrative:
                    continue
                if row.rec not in known:
                    refusals.append(
                        f"{sheet.path.name}:{row.line}  source '{key}' cites {row.rec}, "
                        "which its exact recommendation record does not carry"
                    )

        # A row's class must be the class of the recommendation it cites. This is the
        # one thing here that catches a row pinned to the WRONG recommendation --
        # every other gate would pass such a row, because its number is real and its
        # snippet is on the page it names. It is not a substitute for reading: a row
        # can cite the right recommendation and still describe it wrongly, which stays
        # in the holes list.
        classes = {
            record["rec_id"]: str(record.get("cor") or "").lower()
            for record in recs.get("recommendations", ())
        }
        for row in rows:
            expected = classes.get(row.rec)
            if expected and row.klass.strip().lower() != expected:
                refusals.append(
                    f"{sheet.path.name}:{row.line}  class '{row.klass}' does not match "
                    f"{row.rec}, which is class '{expected}'"
                )

        # The #153 lesson, from this ticket's own comment: count the unread and put it
        # in the exit status, and fire on ANY unread item rather than on total
        # absence. A gate that only fires when nothing was covered reads green over
        # 2.4% coverage.
        if not unaccounted:
            continue

        message = (
            f"{sheet.path.name}  source '{key}': {len(unaccounted)} of {len(known)} "
            f"recommendation identifiers in {recs.get('doc_id')} are neither a row "
            "nor scoped out: "
            + ", ".join(unaccounted[:6])
            + (f", and {len(unaccounted) - 6} more" if len(unaccounted) > 6 else "")
        )
        if mode == MODE_EXACT:
            refusals.append(message)
        else:
            warnings.append(message + "  (source mode is 'bound', so this over-reports)")

    # Scope-outs carry no source key. Membership can therefore be graded only when
    # every declared source has a loaded exact record: a bound record may have missed
    # the identifier, and an absent record may have carried it. Under the all-exact
    # condition, however, an identifier no record carries is inert work presented as
    # completed work, the same fabrication surface as an unresolvable row citation.
    loaded_records = [records.get(key) for key in sorted(sheet.sources)]
    if loaded_records and all(
        record is not None and record.get("mode") == MODE_EXACT
        for record in loaded_records
    ):
        known_anywhere = {
            recommendation["rec_id"]
            for record in loaded_records
            for recommendation in record.get("recommendations", ())
        }
        for rec_id in sorted(set(sheet.scoped_out) - known_anywhere):
            refusals.append(
                f"{sheet.path.name}  ## Coverage scopes out {rec_id}, but no exact "
                "recommendation record carries it"
            )

    why_not = why_not or {}
    total_sources = len(sheet.sources)
    if not total_sources:
        report = "  COVERAGE        NOT RUN -- the sheet declares no source to check against"
    elif ungraded and len(ungraded) == total_sources:
        report = (
            f"  COVERAGE        NOT RUN -- omission was not checked for any of "
            f"{total_sources} source(s): {', '.join(ungraded)}"
        )
    elif ungraded:
        report = (
            f"  COVERAGE        NOT RUN for {len(ungraded)} of {total_sources} "
            f"sources ({', '.join(ungraded)}) -- {len(refusals)} refusing, "
            f"{len(warnings)} warning over the rest, so that is a floor"
        )
    else:
        report = f"  COVERAGE        {len(refusals)} refusing, {len(warnings)} warning"

    diagnostics = [f"  COVERAGE        NOT RUN -- {message}" for message in recs_errors]
    diagnostics.extend(
        f"  COVERAGE        NOT RUN for source '{key}' -- {why_not.get(key, 'no record')}"
        for key in ungraded
    )
    if missing_records:
        diagnostics.append(
            "  The missing recommendation record(s) above are a warning, not a clean "
            "COVERAGE pass."
        )
    blocking_ungraded = [key for key in ungraded if key not in missing_records]
    untrusted_blocking = [key for key in blocking_ungraded if key in untrusted_records]
    if untrusted_blocking:
        diagnostics.append(
            "  The ordinary remedy for the untrusted recommendation record(s) above "
            "is a recommendation sweep rebuild, which publishes to "
            f"--recs-alias {DEFAULT_RECS_ALIAS}, if the source PDF is still available. "
            "A rebuild is not guaranteed when the source has left the corpus."
        )
    other_blocking = [key for key in blocking_ungraded if key not in untrusted_records]
    if other_blocking or recs_errors:
        diagnostics.extend(
            (
                "  Omission was not checked for the source(s) above. A source with no",
                "  recommendation record is not a source that passed, and a --recs path",
                "  that does not resolve is a typo rather than a decision.",
            )
        )

    narrative_qualifier = (
        f"                  {len(narrative_rows)} narrative row(s) sit outside the "
        "recommendation index; "
        f"{len(rendered_narrative_rows)} page transcription(s) declare "
        f"{RENDERED_MARKER}. The ## Scope span table is the only bound on which "
        "prose was read."
    )

    return GateResult(
        "COVERAGE",
        refusals,
        warnings,
        ungraded_sources=ungraded,
        report=(report, narrative_qualifier),
        diagnostics=tuple(diagnostics),
        not_graded=bool(blocking_ungraded or recs_errors or not sheet.sources),
    )


def gate_range(sheet: Sheet) -> GateResult:
    """Unit-keyed sanity bounds, naming failures and the ungraded-number count.

    The ungraded count is returned and printed rather than swallowed. A gate that
    silently grades 4 of a sheet's 200 numbers and reports a clean run is the shape
    #153 caught reading green over 2.4% coverage, and the fix there was the same:
    put the unread count where the verdict is.
    """
    if not sheet.rows:
        return GateResult(
            "RANGE",
            report=("  RANGE           NO ROWS",),
        )
    failures: list[str] = []
    ungraded = 0
    for row in sheet.rows:
        graded_spans: list[tuple[int, int]] = []
        for match in _MEASURED.finditer(row.value):
            graded_spans.append(match.span("numbers"))
            unit = re.sub(r"\s+", " ", match.group("unit").strip().lower())
            bounds = QUANTITY_UNIT_BOUNDS.get(
                (sheet.path.name, row.quantity, unit), UNIT_BOUNDS.get(unit)
            )
            if bounds is None:
                # A recognized unit with no bound -- hours, days, weeks. Matching it
                # is the point: it stops those numbers being attributed to whatever
                # unit appears elsewhere in the same value.
                ungraded += len(_NUMBER.findall(match.group("numbers")))
                continue
            low, high = bounds
            for raw in _NUMBER.findall(match.group("numbers")):
                number = float(raw.replace(",", ""))
                if not low <= number <= high:
                    failures.append(
                        f"{sheet.path.name}:{row.line}  {row.quantity} value {raw} "
                        f"{match.group('unit')} is outside the sanity range "
                        f"{low:g} to {high:g}"
                    )
        for number in _NUMBER.finditer(row.value):
            if not any(start <= number.start() < end for start, end in graded_spans):
                ungraded += 1
    return GateResult(
        "RANGE",
        failures,
        ungraded=ungraded,
        report=(
            f"  RANGE           {len(failures)}  "
            f"({ungraded} numbers carried no unit this grades)",
        ),
    )


def survey(
    sheet_path: Path,
    recs_arguments: list[str] | None,
    pdf_root: Path | None,
    recs_root: Path | None = None,
    text_root: Path | None = None,
    second_read_path: Path | None = None,
    allow_untrusted_provenance: bool = False,
    page_counts: dict[str, int] | None = None,
    recs_alias: Path | None = None,
    catalog_source_classes: dict[str, str] | None = None,
) -> Scan:
    """Read and grade one sheet without emitting either report or findings."""

    if not sheet_path.is_file():
        return Scan(
            Sheet(path=sheet_path, ok=False, why_not="not a file"),
            status=2,
            diagnostics=(f"not a file: {sheet_path}",),
            reportable=False,
        )

    sheet = parse(sheet_path.read_text(encoding="utf-8"), sheet_path)
    if not sheet.ok:
        return Scan(
            sheet,
            status=2,
            diagnostics=(
                f"  NOT GRADED  {sheet.why_not}",
                "  Nothing was checked. This is not a clean sheet.",
            ),
        )

    # **Why the missing-file case is separated from the not-asked-for case.** They
    # produce the same absent record and they are not the same event: one is a run
    # that never intended to check omission, the other is a run that meant to and
    # silently did not. The first version collapsed them by testing `recs_path is
    # None` at the bottom, so `--recs <a path that does not exist>` graded four gates,
    # printed nothing about the fifth, and exited 0. That is this ticket's own #153
    # lesson failing on this ticket's own gate, and it was found by review rather than
    # by a test -- so `TheExitStatusSaysWhichKindOfNotGraded` now pins all three.
    # Since #177 the distinction is drawn per source, in `bind_recs`, and kept in
    # `why_not` so the report can say which source and which of the two it was.
    catalog_problems: list[str] = []
    if page_counts is None:
        catalog_facts = load_catalog_facts()
        page_counts = catalog_facts.page_counts
        catalog_source_classes = catalog_facts.source_classes
        catalog_problems = list(catalog_facts.problems)

    bound_records = bind_recs(
        sheet,
        recs_arguments or [],
        recs_root,
        allow_untrusted_provenance=allow_untrusted_provenance,
        recs_alias=recs_alias,
        corpus_documents=frozenset(page_counts),
    )
    records, why_not, recs_errors, missing_records = bound_records

    schema = gate_schema(sheet, catalog_source_classes)
    null_span = gate_null_span(sheet)
    current_extraction, identity_problems = (
        extraction_identity_from_manifest(
            text_root,
            allow_untrusted_provenance=allow_untrusted_provenance,
        )
        if text_root is not None
        else (None, ["no --text-root was available"])
    )
    extraction_identity = gate_extraction_identity(
        sheet,
        current_extraction,
        identity_problems,
    )
    page_coverage = gate_page_coverage(sheet, page_counts)
    if catalog_problems:
        page_coverage.not_graded = True
        page_coverage.skip_reason = "; ".join(catalog_problems)
        page_coverage.diagnostics = tuple(
            f"  PAGE COVERAGE   NOT GRADED -- {problem}" for problem in catalog_problems
        )
    tier0 = gate_citation_tier0(sheet, records, why_not)
    tier1 = gate_citation_tier1(sheet)
    tier2 = gate_citation_tier2(sheet, pdf_root)
    coverage = gate_coverage(
        sheet,
        records,
        why_not,
        recs_errors,
        missing_records,
        bound_records.untrusted_records,
    )
    ranges = gate_range(sheet)
    watermark = gate_watermark(
        sheet,
        text_root,
        allow_untrusted_provenance=allow_untrusted_provenance,
    )
    # **Gate 5 runs only when a read is handed to it, and never runs itself.** The
    # independence is the whole instrument: a second read this module produced would
    # be the same code path over the same page, which is the check `test_icd10.py`
    # calls worthless and this module's own docstring refuses by name.
    second_read = load_second_read(second_read_path) if second_read_path else None
    second_read_result = gate_second_read(sheet, second_read)
    # An argument naming a source the sheet does not declare, or naming one twice, is
    # a typo and never a decision -- and it is a way of not having graded even when
    # every declared source resolved from `--recs-root`, because the run asked for
    # something and got nothing.
    # A sheet declaring no source has nothing for COVERAGE to iterate, which is a way
    # of not having graded and not a clean gate. SCHEMA refuses it too, so 1 wins --
    # this is what keeps the *report* from saying otherwise.
    # **A read that covered none of this sheet's citations did not grade it**, and
    # that is `gate_coverage`'s NOT RUN case one gate over rather than a new rule. A
    # well-formed record whose entries all land on pages the sheet cites nowhere made
    # every row `uncovered` and printed `0 refusing, 0 warning` -- byte for byte what
    # a clean diff prints -- and exited 0. Every fixture handed the gate a read that
    # covered at least one citation, so nothing in the suite could see it; the tracker
    # sweep did. Partial coverage stays a floor and is reported as one.
    not_graded = (
        coverage.not_graded
        or watermark.not_graded
        or second_read_result.not_graded
        or page_coverage.not_graded
    )

    results = (
        schema,
        null_span,
        extraction_identity,
        page_coverage,
        tier0,
        tier1,
        tier2,
        coverage,
        ranges,
        watermark,
        second_read_result,
    )

    refusals = (
        schema.findings
        + null_span.findings
        + extraction_identity.findings
        + page_coverage.findings
        + tier0.findings
        + tier1.findings
        + tier2.findings
        + coverage.findings
        + ranges.findings
        + watermark.findings
        + second_read_result.findings
    )
    diagnostics = list(page_coverage.diagnostics)
    diagnostics.extend(
        f"  RECOMMENDATION RECORD source '{key}' -- {origin}"
        for key, origin in sorted(bound_records.origins.items())
    )
    diagnostics.extend(extraction_identity.diagnostics)
    diagnostics.extend(watermark.diagnostics[:1])
    diagnostics.extend(f"  FAIL  {message}" for message in refusals)
    diagnostics.extend(
        f"  WARN  {message}"
        for message in (
            extraction_identity.warnings
            + coverage.warnings
            + second_read_result.warnings
        )
    )
    diagnostics.extend(
        f"  NOT DIFFED  {message}"
        for message in second_read_result.undiffed + second_read_result.uncovered
    )
    diagnostics.extend(watermark.diagnostics[1:])
    diagnostics.extend(second_read_result.diagnostics)
    diagnostics.extend(coverage.diagnostics)
    if tier2.skip_reason:
        diagnostics.extend(watermark.tier2_skip_diagnostics)

    if any(result.fatal for result in results):
        status = 2
    elif refusals:
        # 1 wins over 2 where both hold, and the message names the ungraded part so
        # the finding reads as a floor rather than the whole. Returning 2 would file
        # the strongest thing known about the sheet under the weakest heading --
        # `differential_scan.py`'s ordering, for its reason.
        if not_graded:
            diagnostics.append(
                "  note: PAGE COVERAGE, CITATION tier 0, COVERAGE, or SECOND READ "
                "did not run completely, so the count above is a floor.",
            )
        status = 1
    elif not_graded:
        status = 2
    else:
        status = 0
    return Scan(sheet, results, status, tuple(diagnostics))


def _emit_scan(scan: Scan, *, quiet: bool) -> int:
    """Emit one completed survey under the command's quiet contract."""
    early_stdout = tuple(
        result for result in scan.results if result.stdout_before_footer
    )
    if not quiet:
        print(format_report(scan), end="")
    elif quiet:
        for result in early_stdout:
            for line in result.stdout:
                print(line)
    for result in scan.results:
        if result.stdout_before_footer:
            continue
        for line in result.stdout:
            print(line)
    for line in scan.diagnostics:
        print(line, file=sys.stderr)
    return scan.status


def build_parser() -> argparse.ArgumentParser:
    """The command line, built apart from ``main`` so a test can read its defaults.

    `TheRecordsStayOutsideTheRepo` asserts against ``--recs-root``'s default here, and
    a default only a running command can observe is one no test pins.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sheet", type=Path, nargs="?", help="the sheet to grade")
    parser.add_argument("--all", action="store_true", help="grade every sheet in reference/thresholds/ (resolves from the sweep alias, then --recs-root; takes no --recs)")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the report; findings and the tier-2 banner still print",
    )
    parser.add_argument(
        "--recs",
        action="append",
        metavar="KEY=PATH",
        default=None,
        help=(
            "guidelines_recs.py JSON for one source, keyed by its '## Sources' key. "
            "Repeatable. A bare path is accepted only where the sheet declares exactly "
            "one source."
        ),
    )
    parser.add_argument(
        "--recs-root",
        type=Path,
        default=Path(os.environ.get("CLINICAL_GUIDELINES_RECS", DEFAULT_RECS_ROOT)),
        help="where recs-<source key>.json is looked for (outside the repo, always)",
        # Deliberately NOT a spelling of guidelines_index.py's
        # CLINICAL_GUIDELINES_INDEX, which names a database file. This names a
        # directory of recommendation records, and two env vars one word apart that
        # mean different kinds of thing is how the wrong one gets set.
    )
    parser.add_argument(
        "--recs-alias",
        type=Path,
        default=Path(os.environ.get(RECS_ALIAS_ENV, DEFAULT_RECS_ALIAS)),
        help=(
            "published recommendation sweep containing <doc_id>.json records; "
            f"defaults from {RECS_ALIAS_ENV}"
        ),
    )
    parser.add_argument(
        "--pdf-root",
        type=Path,
        default=DEFAULT_PDF_ROOT,
        help="corpus root for citation tier 2 (absent is reported, never passed)",
    )
    parser.add_argument(
        "--text-root",
        type=Path,
        default=(
            Path(os.environ["CLINICAL_GUIDELINES_TEXT"])
            if os.environ.get("CLINICAL_GUIDELINES_TEXT")
            else None
        ),
        help=(
            "#80's extracted-text directory, holding manifest.json, for WATERMARK. "
            "Defaults from CLINICAL_GUIDELINES_TEXT, then derives from --pdf-root "
            "when neither is given (absent is reported, never passed)"
        ),
    )
    parser.add_argument(
        "--allow-untrusted-provenance",
        action="store_true",
        help=(
            "grade against a dirty, foreign, or unstamped extracted corpus; "
            f"{artifact_provenance.FLAG_HELP_EFFECT}"
        ),
    )
    parser.add_argument(
        "--second-read",
        type=Path,
        default=None,
        help=(
            "an independent extraction of one declared span, to diff against it. "
            "See --brief --span for the work order and record shape"
        ),
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="print the work order for --span and grade nothing",
    )
    parser.add_argument(
        "--span",
        default=None,
        help="span to brief, or <source>:<span> where two sources reuse a name",
    )
    return parser


def text_root_for(args: argparse.Namespace) -> Path:
    """Where the extracted corpus is: ``--text-root``, else derived from ``--pdf-root``.

    Derived through ``guidelines_extract.default_output`` rather than typed, so the
    rule about where #80 writes lives in #80 and a rename there moves this. A second
    literal path here is what would let the two go quietly out of step -- and the
    default is not a constant this module may state, since ``--pdf-root`` can move it.
    """
    return args.text_root or guidelines_extract.default_output(args.pdf_root)


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    text_root = text_root_for(args)

    if args.brief:
        # Grades nothing and says so by exiting 2 on a sheet it could not read: the
        # brief is derived from the sheet's citations, so an unreadable sheet yields
        # a work order for nowhere.
        if not args.sheet:
            parser.error("--brief needs a sheet")
        if not args.sheet.is_file():
            print(f"not a file: {args.sheet}", file=sys.stderr)
            return 2
        sheet = parse(args.sheet.read_text(encoding="utf-8"), args.sheet)
        if not sheet.ok:
            print(f"  NOT GRADED  {sheet.why_not}", file=sys.stderr)
            return 2
        if not args.span:
            parser.error("--brief needs --span <name>")
        try:
            work_order = brief(sheet, args.span)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 2
        print(work_order, end="")
        return 0

    if args.all:
        # **`--all` takes no `--recs`, and refusing is cheaper than explaining.** A
        # bare path binds to *the* source of a one-source sheet, so one society's
        # record would bind to every sheet that cites one source; a keyed one binds by
        # a key that is sheet-local, so it lands on every sheet declaring that key and
        # exits 2 on every sheet that does not. Neither is a thing anybody means. The
        # directory mode resolves automatically from the sweep alias and recs root.
        if args.recs:
            parser.error(
                "--all resolves from the sweep alias and --recs-root and takes no "
                "--recs: a source key is sheet-local, so which sheet's source a "
                "record answers for is unknowable across a directory. Name the sheet, "
                "or point --recs-root at the records."
            )
        # **And no `--second-read`, for the same reason one level sharper.** A read
        # is a set of values at a set of (document, page) citations, so pointed at a
        # directory it would diff one sheet's read against every sheet's rows -- and
        # against a sheet citing another guideline entirely it refuses every row,
        # which is a confident finding about nothing.
        if args.second_read:
            parser.error(
                "--all takes no --second-read: a read answers for one sheet's "
                "citations, so which sheet it grades is unknowable across a directory."
            )

        sheets = sorted(SHEET_ROOT.glob("*.md"))
        sheets = [
            path
            for path in sheets
            if path.name.lower() not in {"readme.md", "coverage.md"}
        ]
        if not sheets:
            print(f"no sheet under {SHEET_ROOT}", file=sys.stderr)
            return 2
        worst = 0
        affected_extractions: list[str] = []
        for path in sheets:
            scan = survey(
                path,
                [],
                args.pdf_root,
                args.recs_root,
                text_root,
                None,
                args.allow_untrusted_provenance,
                recs_alias=args.recs_alias,
            )
            worst = max(
                worst,
                _emit_scan(scan, quiet=args.quiet),
            )
            if any(
                result.gate == "EXTRACTION IDENTITY" and result.warnings
                for result in scan.results
            ):
                affected_extractions.append(path.name)
        if affected_extractions:
            print(
                f"  WARN  EXTRACTION IDENTITY {len(affected_extractions)} affected "
                f"sheet(s): {', '.join(affected_extractions)}",
                file=sys.stderr,
            )
        return worst

    if not args.sheet:
        parser.error("give a sheet, or --all")
    # `--recs-root` applies here too, and it did not before #177: `--all` resolved a
    # record and a named sheet did not, so the same sheet graded differently depending
    # on which way it was reached. One rule, and the root stays outside the repo --
    # see `bind_recs` for why there is no fallback beside the sheet.
    return _emit_scan(
        survey(
            args.sheet,
            args.recs,
            args.pdf_root,
            args.recs_root,
            text_root,
            args.second_read,
            args.allow_untrusted_provenance,
            recs_alias=args.recs_alias,
        ),
        quiet=args.quiet,
    )


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
