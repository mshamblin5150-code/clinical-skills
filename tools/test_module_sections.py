"""Every command-bearing module in ``tools/`` is documented under a named section.

#743. ``CLAUDE.md`` gave a ``###`` section to most of the directory and named nine
command-bearing modules only in passing, or not at all. The obligation is now
derived and bound rather than remembered.

**Candidacy is derived; membership is declared.** That is ADR 0092 ruling 4's
arrangement, adopted here because the same thing defeats a purely mechanical
rule in both places. Candidacy is a property of the file -- a top-level
``__main__`` guard, which is what makes a module a command a person types rather
than a library another module imports. Membership cannot be derived, and three
measurements say so:

* **Title normalization reaches a minority of sections.** The house writes prose
  titles -- *Filled-vitals census*, *Word documents, both directions*, *Post-draft
  checks* -- so keying on a normalized heading finds only the sections whose title
  happens to be a module name.
* **"The section shows how to run it" has false negatives.** Several modules own a
  section that never prints a ``python tools/<name>.py`` line.
* **It also has false positives, and one is live.** ``Tracker scan`` shows a
  ``phi_scan`` invocation while ``PHI pre-commit hook`` is the section that
  documents it. A derived answer picks the wrong one.

So the map below is a person's ruling, one row per command, and the walk grades
whether the ruling is complete and whether every section it names exists.

**What this does not establish** is that a named section describes its module
*well*, or that it states the module's exit statuses, coverage boundary, or what a
clean run does not establish. Those are readings. This is a floor on the
obligation having been discharged at all, which is the failure #707 recorded
twice on its own thread.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
TOOLS = REPO_ROOT / "tools"

MAIN_GUARD = re.compile(r'(?m)^if __name__ == ["\']__main__["\']')
SECTION = re.compile(r"(?m)^### (.+)$")

# One row per command module. The value is the ``###`` section that documents it.
# A module described inside a section that also documents its artifact keeps that
# section's name; the row is the ruling that the arrangement is deliberate.
DECLARED_SECTIONS = {
    "adr_next": "ADR number allocation",
    "anchor_scan": "Anchor scan",
    "block_scan": "Block scan",
    "case_study_scan": "Case study house style",
    "cdc_percentile": "CDC BMI-for-age table",
    "checks_ledger": "Post-draft checks",
    "closing_keyword_scan": "Closing keyword scan",
    "corpus_census": "Corpus census",
    "differential_scan": "Differential scan",
    "discussion_post_scan": "Discussion post grading",
    "discussion_post_render": "Discussion post grading",
    "discussion_reply_scan": "Discussion reply grading",
    "docx_read": "Word documents, both directions",
    "docx_word_probe": "Word documents, both directions",
    "docx_write": "Word documents, both directions",
    "filled_vitals_census": "Filled-vitals census",
    "guidelines_build": "Guideline text extraction",
    "guidelines_catalog": "Guideline catalog",
    "guidelines_extract": "Guideline text extraction",
    "guidelines_index": "Guideline full-text index",
    "guidelines_recs": "Recommendation extraction",
    "guidelines_search": "Guideline full-text index",
    "harvest_review": "PHI pre-commit hook",
    "icd10_build": "ICD-10-CM code set",
    "icd10_lookup": "ICD-10-CM code set",
    "map_scan": "Implementation map disagreement scan",
    "name_index": "PHI pre-commit hook",
    "phi_scan": "PHI pre-commit hook",
    "reference_scan": "Reference scan",
    "refusal_scan": "Refusal scan",
    "research_ledger": "Research ledger",
    "scratch_census": "Scratch census",
    "skills_mirror": "Skills mirror",
    "specificity_scan": "Specificity scan",
    "spelling_scan": "Spelling scan",
    "split_census": "Split census",
    "threshold_coverage": "Threshold coverage registry",
    "threshold_draft": "Threshold sheet drafting",
    "threshold_sheet": "Threshold sheets",
    "tracker_bodies": "Tracker bodies",
    "tracker_branch_scope": "Tracker branch scope",
    "tracker_freshness": "Tracker freshness",
    "tracker_merge_receipt": "Tracker merge receipt",
    "tracker_publish_hook": "Tracker publish hook",
    "tracker_scan": "Tracker scan",
    "uspstf_interval_reach": "USPSTF interval reach",
    "uspstf_table": "USPSTF recommendation table",
    "voice_corpus": "The corpus a voice model is built from",
    "voice_model_scan": "Voice model shape",
}


def command_modules(root: Path | None = None) -> set[str]:
    """Every module in ``tools/`` that a person can run as a command."""

    directory = TOOLS if root is None else root
    return {
        path.stem
        for path in directory.glob("*.py")
        if not path.stem.startswith("test_")
        and MAIN_GUARD.search(path.read_text(encoding="utf-8"))
    }


def section_titles(text: str | None = None) -> set[str]:
    source = CLAUDE_MD.read_text(encoding="utf-8") if text is None else text
    return {match.group(1).strip() for match in SECTION.finditer(source)}


class EveryCommandModuleIsDeclared(unittest.TestCase):
    def test_every_command_module_has_a_declared_section(self):
        undeclared = sorted(command_modules() - set(DECLARED_SECTIONS))

        self.assertFalse(
            undeclared,
            "command-bearing modules with no declared CLAUDE.md section: "
            + ", ".join(undeclared)
            + ". Write the section, then add the row. A module described inside "
            "another section keeps that section's name, and the row is the ruling "
            "that the arrangement is deliberate.",
        )

    def test_no_declared_row_outlives_its_module(self):
        stale = sorted(set(DECLARED_SECTIONS) - command_modules())

        self.assertFalse(
            stale,
            "declared rows for modules that are not commands: " + ", ".join(stale),
        )

    def test_every_declared_section_exists(self):
        titles = section_titles()
        missing = sorted(
            {
                f"{module} -> {title}"
                for module, title in DECLARED_SECTIONS.items()
                if title not in titles
            }
        )

        self.assertFalse(missing, "declared sections absent from CLAUDE.md: " + ", ".join(missing))

    def test_the_derivation_is_live(self):
        """A walk that found nothing would pass all three assertions above."""

        modules = command_modules()

        self.assertGreater(len(modules), 40)
        self.assertIn("phi_scan", modules)
        self.assertNotIn("repo_root", modules)
        self.assertNotIn("console_codec", modules)


class TheDerivationIsNotSatisfiedByAMention(unittest.TestCase):
    """The three shapes that defeat a derived answer, pinned as cases."""

    def test_a_prose_titled_section_still_owns_its_module(self):
        self.assertEqual(
            DECLARED_SECTIONS["map_scan"], "Implementation map disagreement scan"
        )
        self.assertNotIn("map_scan", section_titles())

    def test_a_section_that_merely_shows_an_invocation_does_not_own_the_module(self):
        text = CLAUDE_MD.read_text(encoding="utf-8")
        tracker_scan = re.split(r"(?m)^### ", text)
        body = next(s for s in tracker_scan if s.startswith("Tracker scan\n"))

        self.assertIn("tools/phi_scan.py", body)
        self.assertEqual(DECLARED_SECTIONS["phi_scan"], "PHI pre-commit hook")

    def test_a_module_may_share_a_section_with_its_artifact(self):
        for module in ("icd10_lookup", "icd10_build"):
            with self.subTest(module=module):
                self.assertEqual(DECLARED_SECTIONS[module], "ICD-10-CM code set")


if __name__ == "__main__":
    unittest.main()
