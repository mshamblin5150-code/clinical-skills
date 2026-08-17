"""Pin the cross-file agreements [#90](https://github.com/mshamblin5150-code/clinical-skills/issues/90) settled.

**Every defect this file guards is one document contradicting another**, which is
the shape #90 turned out to be twice over. ``batch-shift``'s ``description`` said
the input was a pasted shift while the first third of the same file opened a PDF;
and ``setup-clinical-skills`` kept the unmapped-preceptor sentence
[#91](https://github.com/mshamblin5150-code/clinical-skills/pull/91) had already
retired in ``batch-shift``, so for four days two skills stated one rule at
different strengths.

**Different strengths, not opposite ones, and the distinction is the finding.**
The retired sentence -- *reported, never substituted* -- was **stricter** than
what replaced it, and both forbid an agent guessing a surname. What #91 separated
out was the clinician's own deliberate substitution, which the old wording swept
in alongside the guess. A reader of ``setup-clinical-skills`` alone would not have
done anything unsafe; they would have refused something that was not theirs to
refuse. **Calling it a contradiction overstates it**, and this paragraph said so
before a review caught it.

**A single-file reader cannot see either.** Both read as coherent on their own
page, which is why they survived a review that opened one file at a time and why
the check has to name pairs rather than rules.

There is nothing to run here and no scanner to keep parity with -- this is
``test_spelling_scan.py``'s *the scanner must not drift from the file a reader
opens*, with the second reader being another Markdown file rather than a tool.

**Substrings, deliberately, and phrased as the ruling rather than as the
sentence.** A test asserting a paragraph verbatim fails on every rewrite and
teaches the next session to delete it; these assert the load-bearing clause, so
the prose around them stays free.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH_SHIFT = REPO_ROOT / "skills" / "batch-shift" / "SKILL.md"
CLINICAL_NOTE = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
SETUP = REPO_ROOT / "skills" / "setup-clinical-skills" / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_description(path: Path) -> str:
    """The ``description:`` line of a skill's YAML frontmatter.

    Read by line rather than with a YAML parser because the frontmatter is three
    keys and the repo is stdlib-only. A skill whose description wrapped onto a
    second line would return only the first, so the assertions below check for
    what must be **absent** on the whole file as well.
    """
    for line in read(path).splitlines():
        if line.startswith("description:"):
            return line
    raise AssertionError(f"{path} has no description line in its frontmatter")


class BatchShiftHasOneEntryPointAndItIsAFile(unittest.TestCase):
    """#90 decision 2, ruled 2026-08-16: a day file, and no second input shape.

    The clinician still scans each shift to a PDF, so steps 1 and 2 fire on live
    work -- and a whole shift never arrives as a paste, because a paste is one or
    two encounters and those are ``clinical-note``'s. **Both halves are asserted**:
    without the second, a description naming a day file *and* a paste would pass
    while re-opening the exact ambiguity the ruling closed.
    """

    def test_the_description_names_a_day_file(self):
        self.assertIn("day file", frontmatter_description(BATCH_SHIFT))

    def test_the_description_does_not_offer_a_pasted_shift(self):
        # **The description line, not the file.** The first version of this test
        # searched the whole file and failed on the skill's own paragraph
        # recording what the description used to say -- a **mention**, quoted in
        # order to rule against it, which is ``spelling_scan``'s distinction
        # arriving uninvited in a third place. Widening the search would force
        # the next session to delete the sentence explaining the ruling in order
        # to satisfy a test guarding that ruling.
        self.assertNotIn("pastes a whole shift", frontmatter_description(BATCH_SHIFT))

    def test_the_description_routes_a_small_paste_to_clinical_note(self):
        self.assertIn("clinical-note", frontmatter_description(BATCH_SHIFT))

    def test_the_agents_index_row_agrees_with_the_description(self):
        row = [
            line for line in read(AGENTS).splitlines()
            if line.startswith("| batch-shift ")
        ]
        self.assertEqual(len(row), 1, "AGENTS.md must carry exactly one batch-shift row")
        self.assertIn("day file", row[0])
        self.assertNotIn("pasted", row[0])

    def test_the_skill_says_the_steps_fire_on_live_work(self):
        # The whole ruling in one clause. Deleting the paragraph that explains
        # *why* steps 1 and 2 stay is how the question gets reopened by a session
        # that reads them as archaeology, which is what #90 was filed on.
        self.assertIn("still scans each shift", read(BATCH_SHIFT))


class TheBranchIsNamedBeforeAShiftIsWritten(unittest.TestCase):
    """#90 decision 4: ``clinical-note`` standalone picks its own branch.

    ``fixtures/day-a`` run 2 is the evidence: given the shorthand with no branch
    stated, several passes chose the FNP H&P unprompted and were discarded. **The
    count is in ``fixtures/day-a/assertions.md`` and deliberately not repeated
    here**, because it was measured against a directory under ``scratch/`` and
    nothing committed re-derives it.

    **This docstring restated that count until a sweep caught it**, on the same
    branch as the two skill paragraphs that forbid restating it -- so the rule and
    its violation shipped together, which is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
    thesis demonstrated by the change that cites it. A ``.py`` docstring reads as
    exempt from a rule about prose, and it is not.

    The fix is two lines in two files and **neither works alone**: the default
    makes a shift uniform, and the confirm block is where a wrong default is
    caught on note one instead of note eleven.
    """

    def test_the_confirm_block_prints_the_branch(self):
        self.assertIn("Branch for the whole shift", read(BATCH_SHIFT))

    def test_clinical_note_defaults_to_soap_when_nobody_named_one(self):
        text = read(CLINICAL_NOTE)
        self.assertIn("write SOAP, say which you chose", text)

    def test_clinical_note_forbids_defaulting_silently(self):
        # The default is wrong during the first six encounters of a course, so
        # announcing it is the entire mitigation. A run that defaults quietly has
        # kept the behavior and dropped the thing that makes it survivable.
        self.assertIn("Never silently default", read(CLINICAL_NOTE))

    def test_a_named_branch_still_wins(self):
        self.assertIn("Where a branch was named, that is the branch", read(CLINICAL_NOTE))

    def test_a_named_branch_does_not_suspend_the_program_rule(self):
        # The first version of this ruling read "the rule above is not consulted",
        # which contradicted the *first six encounters must be H&P* rule four
        # lines above it -- and the current course started from zero, so it was
        # live rather than theoretical. Caught by the spec axis of the review.
        self.assertIn("This does not suspend the rule above", read(CLINICAL_NOTE))

    def test_the_shift_default_does_not_reach_step_5_as_a_choice(self):
        # **The seam, and the hole the first version of this work left open.**
        # Step 4 defaulting to SOAP and step 5 reading it as *the branch the user
        # named* would hand ``clinical-note`` a named branch, so its offer-to-redo
        # would never fire and the mitigation would be silently defeated for a
        # whole shift. Step 4 stops for confirmation anyway, which is what makes
        # the default survivable -- so the two clauses have to stay welded.
        text = read(BATCH_SHIFT)
        self.assertIn("must not reach step 5 disguised as a choice", text)
        self.assertIn("on the branch step 4 settled", text)
        self.assertNotIn("on the branch the user named", text)


class BothSkillsRuleTheSameWayOnAnUnmappedPreceptor(unittest.TestCase):
    """#91's ruling, and the copy of it #91 did not sweep for.

    The retired sentence welded two acts together: an agent guessing a nearest
    surname match, which is forbidden, and the clinician entering his own
    preceptor of record where the picklist has no row for the physician he
    rounded with, which is his call and already made. **Only the first is an
    agent's to refuse.**
    """

    def test_neither_skill_carries_the_retired_sentence_as_a_rule(self):
        # Both files may *report* the old wording -- ``setup-clinical-skills``
        # does, in a parenthetical recording what it replaced -- so the check is
        # that neither states it as an instruction. A mention is not a use, which
        # is ``spelling_scan``'s distinction reused rather than reinvented.
        for path in (BATCH_SHIFT, SETUP):
            for line in read(path).splitlines():
                if "reported, never substituted" not in line:
                    continue
                self.assertTrue(
                    line.lstrip().startswith("*("),
                    f"{path.name} states the retired rule rather than reporting it: {line}",
                )

    def test_both_skills_forbid_guessing_a_surname(self):
        for path in (BATCH_SHIFT, SETUP):
            self.assertIn(
                "guess a nearest surname match",
                read(path),
                f"{path.name} dropped the prohibition that survived #91",
            )

    def test_the_two_skills_split_collecting_the_answer_from_using_it(self):
        # **A bare ``"profile" in text`` passed with the ruling deleted**, because
        # both files name ``scratch/medatrax-profile.md`` for unrelated reasons --
        # the vacuous-row problem ``fixtures/README.md`` names, caught in review.
        # So each side is pinned to its own half: setup **writes** the ruling,
        # batch-shift **reads** it, and neither restates the other's.
        self.assertIn("write the ruling into the profile", read(SETUP))
        self.assertIn("Read the profile", read(BATCH_SHIFT))

    def test_setup_does_not_restate_the_lookup_order_it_points_at(self):
        # The cure for a copy that drifted cannot be a second copy. #91 fixed one
        # of two near-identical paragraphs and the other went stale; duplicating
        # the ruling again would rebuild exactly that.
        self.assertIn("not restated here on purpose", read(SETUP))


if __name__ == "__main__":
    unittest.main()
