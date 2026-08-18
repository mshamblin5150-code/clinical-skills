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

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH_SHIFT = REPO_ROOT / "skills" / "batch-shift" / "SKILL.md"
CLINICAL_NOTE = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
SETUP = REPO_ROOT / "skills" / "setup-clinical-skills" / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"
MEDATRAX = REPO_ROOT / "reference" / "medatrax-fields.md"
BLOCK_SCAN = REPO_ROOT / "tools" / "block_scan.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def names_the_same_field(claimed: str, field: str) -> bool:
    """Does a phrase from ``setup``'s per-account sentence name a declared field?

    The two files write one field differently on purpose: ``setup`` pluralizes
    (*case types*) and qualifies (*Patient Time bands*) in running prose, while
    the reference uses the bare dropdown label. So the comparison strips one
    trailing ``s`` and matches **in both directions** -- a one-way containment
    test read *Patient Time bands* correctly and would have missed a bare
    *case*, which the spec axis of #222's review found by trying it.

    Deliberately blunt, and it can only ever produce a **false alarm**: two
    documents disagreeing about one field, reported for a person to settle. That
    is the safe direction here, and the alternative is the name vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build.
    """
    def norm(value: str) -> str:
        value = value.strip().lower()
        return value[:-1] if value.endswith("s") else value

    a, b = norm(claimed), norm(field)
    return a == b or a in b or b in a


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




class ThePerAccountPicklistsAreNotInTheReference(unittest.TestCase):
    """#212's ruling, and the one half of it a reader can check without a name.

    ``setup-clinical-skills`` states the split this repo runs on -- *this file
    holds the universal Medatrax behavior and the profile holds everything about
    them* -- and ``reference/medatrax-fields.md`` inlined the preceptor and site
    picklists anyway, for the whole life of the file. That is what #212 found
    while scanning for a public flip, and the tree was cleared on the broken
    split rather than on de-identification: **#212 re-ruled #50 the same way**,
    no site layer and the historical blobs stay.

    **These assertions name no site and no preceptor, deliberately.** A test
    holding the strings would put them back in the tree the ruling just emptied,
    which is ``spelling_scan``'s mention-versus-use problem with the sign
    flipped -- here the mention is the leak. So each check is structural: the
    reference must *point at* the profile, and the two skills that consume the
    rules must not send a reader to the file that no longer holds them.

    What no test here can reach is a *new* per-account value arriving in the
    reference under some other heading. #50 ruled that hole acceptable and #212
    left it ruled; nothing below is a fourth ``phi_scan`` layer.
    """

    def test_the_reference_points_at_the_profile_for_both_picklists(self):
        text = read(MEDATRAX)
        self.assertIn("Preceptor and Location / Site are per-account", text)
        self.assertIn("scratch/medatrax-profile.md", text)

    def test_the_reference_keeps_the_format_it_gave_up_the_values_for(self):
        # The move is only safe if the universal half survives it. ``Last,First``
        # with no space is Medatrax behavior on every account, and an entry
        # written with a space does not match the picklist.
        self.assertIn("`Last,First` with no space", read(MEDATRAX))

    def test_the_payer_rule_is_not_claimed_to_live_in_the_reference(self):
        # ``clinical-note`` step 5 read *The rules live in the reference; do not
        # restate them here* while one of the two rules keys on a site name. A
        # reader following that sentence after the move finds nothing and has to
        # guess, which is the failure #212's move would otherwise have created.
        note = read(CLINICAL_NOTE)
        self.assertNotIn("The rules live in the reference", note)
        self.assertIn("keys on the site, which makes it per-account", note)

    def test_no_consumer_still_addresses_the_payer_rule_to_the_reference(self):
        # **The first pass of this class checked one consumer and there were
        # three**, which is #137's partial instrument arriving on the sweep meant
        # to prevent it. ``block_scan.py`` grades the F1 row that rests on this
        # rule and its docstring gave the old address; ``setup-clinical-skills``
        # step 1 asserted the per-account content was *written into* the
        # reference, eighty lines above the rule this branch added saying it must
        # not be. Both read as coherent alone, which is this file's whole subject.
        self.assertNotIn(
            "**declared rule** in ``reference/medatrax-fields.md``",
            read(BLOCK_SCAN),
        )
        self.assertNotIn(
            "all of it is currently written into", read(SETUP)
        )

    def test_setup_rules_where_a_site_keyed_rule_belongs(self):
        # The durable half. Without it the next declared default keyed on a
        # placement lands back in the reference and the split breaks again.
        self.assertIn(
            "keys on a preceptor or a site is per-account", read(SETUP)
        )


class TheReferenceDeclaresWhichFieldsItHoldsValuesFor(unittest.TestCase):
    """#222's ruling of 2026-08-18: a declared inventory, and it states its own gap.

    #212 emptied the per-account picklists out of the reference and left nothing
    that would notice a new one arriving. The ticket offered three ways to fix
    that and the clinician took the middle one: **the reference names, once, the
    exact set of fields it holds values for**, and this class asserts the file
    holds values for exactly those and no others. So a ninth picklist cannot land
    quietly -- it forces a one-line diff in a sentence whose entire subject is
    *is this universal?*, which is a better review surface than the whole file.

    **What it reaches is a field label; what it cannot reach is a value, and the
    reference says so beside the inventory.** The preceptor and site lists were
    fenced values under a bold label, so they are reachable wherever in the file
    they land. A site name appended to the ``Case Type`` list is not, and neither
    was the ``Primary Payment Method`` rule -- a **pipe table keyed on site
    names** under a different heading. No structural test tells one site name
    from one payer string without exactly the vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build and #212 re-ruled. **A green run here is not a walked
    file**, which is ``differential_scan.py``'s *a clean scan is not a walked
    row* arriving on a document instead of a run.

    **The decision 2 the ticket proposed was weaker than this and would have
    caught neither defect.** It asked the reference to declare an allow-list of
    *headings* it owns -- and both defects arrived under headings the reference
    legitimately owns, the picklists under *Picklists* and the payer table under
    *Field selection rules*. The unit had to drop to the field for the check to
    have any grip at all. Re-derived from ``c588e2f`` rather than taken from the
    ticket body.

    **The inventory names fields, never values**, so nothing here puts an account
    back in the tree that ``ThePerAccountPicklistsAreNotInTheReference`` above
    just emptied.
    """

    #: The inventory sentence's opener. Held once because the parse and the
    #: presence check must key on the same string, and two copies is how they
    #: drift apart.
    INVENTORY_OPENER = "**This file holds values for exactly these fields"

    def declared_fields(self):
        for line in read(MEDATRAX).splitlines():
            if line.startswith(self.INVENTORY_OPENER):
                _, _, tail = line.partition(":**")
                return [part.strip() for part in tail.split("·") if part.strip()]
        raise AssertionError(
            "reference/medatrax-fields.md declares no field inventory under Picklists"
        )

    def labeled_fields(self):
        """Every ``**Field:**`` line opener in the file, bar the inventory itself.

        A value line is bold, colon-terminated **inside** the bold span, and at
        the start of its line. The pointer paragraph -- *Preceptor and Location /
        Site are per-account* -- and the override sweep both end their bold span
        with a period rather than a colon, so neither is read as a field. Checked
        against the real file rather than assumed.

        **The whole file, and a first version of this read one section.** The
        ticket's hole is a per-account value arriving *under some other heading*,
        so a bounded read answers a narrower question than the one asked -- and
        worse, it was escapable by adding a heading, since the terminator matched
        ``###`` as well as ``##``. The paragraph fenced off behind such a heading
        is reworded now instead. Found by the spec axis of the review.

        **Prose that does open that way is read as a field, and the reference says
        so beside the inventory.** The paragraph naming what this check cannot
        reach tripped it while being written, which is ``differential_scan``'s
        *describing the rule broke the tool that checks the rule* arriving a third
        time. The parse stays blunt anyway: telling a label from a sentence is a
        judgment, and a judgment is the seam a ninth picklist would come through.
        """
        found = []
        for line in read(MEDATRAX).splitlines():
            if line.startswith(self.INVENTORY_OPENER):
                continue
            match = re.match(r"\*\*([^*]+):\*\*", line)
            if match:
                found.append(match.group(1).strip())
        return found

    def test_the_inventory_and_the_value_lines_agree(self):
        declared = self.declared_fields()
        labeled = self.labeled_fields()
        self.assertEqual(
            len(set(declared)), len(declared), "the inventory names a field twice"
        )
        undeclared = sorted(set(labeled) - set(declared))
        self.assertEqual(
            undeclared,
            [],
            "reference/medatrax-fields.md holds values for a field its inventory "
            "does not declare. Add it to the inventory sentence if it really is a "
            "Medatrax dropdown every account renders; move it to "
            "scratch/medatrax-profile.md if it is one account's; or reword it if "
            "it is prose that opened with a bold span ending in a colon, which is "
            f"the field-label form and cannot be told apart from one: {undeclared}",
        )
        stale = sorted(set(declared) - set(labeled))
        self.assertEqual(
            stale,
            [],
            f"the inventory declares a field the file no longer holds values for: {stale}",
        )

    def test_the_inventory_states_the_shape_it_cannot_reach(self):
        # **The load-bearing half of the ruling.** A gate that reaches one of two
        # shapes and does not say so reads as coverage it does not have, which is
        # the failure this repo names in every scanner it ships. Asserting the
        # sentence is what stops a tidy quietly upgrading the claim.
        text = read(MEDATRAX)
        self.assertIn("does not reach", text)
        self.assertIn("keyed on a site", text)

    def test_setup_does_not_call_an_inventoried_field_per_account(self):
        """The cross-file half, and the defect that was live when #222 was built.

        ``setup-clinical-skills`` step 4 read *Preceptors, sites, case types and
        Patient Time bands are per-account picklists* while the reference held
        Case Type's values and the Patient Time bands as universal. Both
        files read as coherent alone, which is this module's whole subject, and
        no assertion in the class above could see it. The clinician ruled
        2026-08-18 that the reference is right: Medatrax renders the same two
        dropdowns on every account, and what varies is the program's hour
        breakdown across the bands -- a different fact, in a different file.
        """
        sentences = [
            line for line in read(SETUP).splitlines()
            if "are per-account picklists" in line
        ]
        # **Every such line, not exactly one.** Requiring a single line would
        # report a rewrite of step 4 into two sentences as a contradiction, which
        # is the failure this module's own docstring rules against -- *a test
        # asserting a paragraph verbatim fails on every rewrite and teaches the
        # next session to delete it*. Caught by the standards axis of the review.
        self.assertTrue(
            sentences,
            "setup-clinical-skills no longer names which picklists are per-account",
        )
        for sentence in sentences:
            head = sentence.split("are per-account picklists")[0]
            claimed = [
                part.strip(" *`")
                for chunk in head.split(",")
                for part in chunk.split(" and ")
                if part.strip(" *`")
            ]
            for item in claimed:
                for field in self.declared_fields():
                    self.assertFalse(
                        names_the_same_field(item, field),
                        f"setup-clinical-skills calls {item!r} per-account while "
                        "reference/medatrax-fields.md holds its values as universal. "
                        "One of the two files is wrong",
                    )


if __name__ == "__main__":
    unittest.main()
