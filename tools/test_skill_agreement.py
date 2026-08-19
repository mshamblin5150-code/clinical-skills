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
CASE_STUDY = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"
CASE_STUDY_STYLE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "style.md"
CASE_STUDY_VOICE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "voice.md"


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


class TheVoiceModelIsPerAccountAndTheMethodIsNot(unittest.TestCase):
    """#213's build, on the rule #212 settled and this class already pins above.

    **The ticket asked for one file and the answer is two**, so the thing most
    likely to go wrong later is a tidy that collapses them back. ``voice.md`` is
    the *method* and travels in ``reference/``; the *model* it builds is
    ``scratch/voice-model.md``, gitignored, one per clinician. Shipping a
    register in ``reference/`` would make every other user of the skill sound
    like this one, **which #213 names as worse than no model at all** -- so the
    failure is not a leak the way the picklists were, it is a skill that is
    silently wrong for everybody except its author.

    **Three files have to agree and each reads as coherent alone**, which is this
    module's whole subject. ``SKILL.md`` sends a run to the model, ``style.md``
    §11 sends a reader from the mechanics to the register, and ``voice.md`` says
    which of the two it is. A single-file reader sees no contradiction in any
    arrangement of them.

    **Nothing here quotes a sample or names the clinician**, on
    ``ThePerAccountPicklistsAreNotInTheReference``'s reasoning one step out: a
    test holding a line of his writing would put it in the tree that the split
    exists to keep it out of.
    """

    def test_the_method_travels_and_the_model_does_not(self):
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("This file is the method. It is not the model.", voice)
        self.assertIn("scratch/voice-model.md", voice)

    def test_the_skill_sends_a_run_to_the_gitignored_model(self):
        # Not to ``reference/voice.md``, which holds no register and never will.
        self.assertIn("scratch/voice-model.md", read(CASE_STUDY))

    def test_the_unmodeled_declaration_survives_the_build(self):
        # The rule predates the file and is the one thing a run does when there
        # are no samples. A build that quietly dropped it would leave a run
        # claiming a register it was never given.
        for path in (CASE_STUDY, CASE_STUDY_VOICE):
            self.assertIn("the voice is unmodeled", read(path))

    def test_the_declaration_is_per_register(self):
        # ``voice.md`` §7. A whole-document declaration reads as complete
        # coverage the moment one register is modeled, which is this repo's most
        # repeated defect wearing a new hat.
        self.assertIn("declaration is per register", read(CASE_STUDY))
        self.assertIn("fewer than two samples", read(CASE_STUDY_VOICE))

    def test_the_style_sheet_hands_the_register_off_rather_than_claiming_it(self):
        # §11 was written by reading finished documents for what they *do*, and
        # a run satisfied every bullet while reading as a stranger. The sheet has
        # to say so where the bullets are, or the next reader takes the list for
        # the whole answer -- which is exactly what happened.
        style = read(CASE_STUDY_STYLE)
        self.assertIn("These are the mechanics", style)
        self.assertIn("[voice.md](voice.md)", style)

    def test_setup_is_the_collector_and_does_not_restate_the_spec(self):
        # The clinician's ruling of 2026-08-18 on the one question #213 left
        # open. It is the same shape step 4 of ``setup`` already runs on with
        # ``batch-shift``'s lookup order -- **collecting the answer and deciding
        # what to ask for are two jobs**, and #90 is what happens when one rule
        # gets written into both files. So ``setup`` must point at the spec, and
        # must not carry the counts that would go stale against it.
        setup = read(SETUP)
        self.assertIn("practicum-case-study/reference/voice.md", setup)
        self.assertIn("not restated here on purpose", setup)
        self.assertNotIn("Ask for 5 at minimum", setup)

    def test_the_skill_names_the_collector_rather_than_collecting(self):
        # The other direction. A run drafting against a deadline that stopped to
        # elicit eight writing samples would be doing setup's job at the worst
        # possible moment, and the clinician may not even be at the keyboard.
        case_study = read(CASE_STUDY)
        self.assertIn("setup-clinical-skills", case_study)
        self.assertIn("this run does not stop to build one", case_study)

    def test_the_model_is_confirmed_by_the_clinician_before_it_is_written(self):
        # **Caught in review, on this branch, after the collector ruling landed.**
        # Step 8 added a third artifact and steps 1 and 9 still enumerated two,
        # so the model was built with no re-run check in front of it and no
        # confirmation behind it. That is the wrong artifact to drop: ``voice.md``
        # §9 says a model cannot be verified by the run that built it, which
        # makes *Confirm, then write* the only verification that exists.
        setup = read(SETUP)
        self.assertIn("`scratch/voice-model.md` and `scratch/shorthand.md`", setup)
        self.assertIn("Let the clinician edit before writing", setup)
        self.assertIn("this step is the whole verification", setup)

    def test_a_rerun_looks_for_the_model_before_it_asks(self):
        # Step 1 owns re-run detection. Without the model on its list a returning
        # clinician is asked for writing he already handed over, or asked again
        # after declining -- and the refusal step 8 records in the profile is
        # only ever read here.
        self.assertIn("`writing-samples/` or `shorthand.md` already exist", read(SETUP))

    def test_the_quote_rule_names_its_audience_rather_than_its_channel(self):
        # **The first build of a real model is what caught this.** The rule read
        # *never leaves scratch/, not into a summary handed back in conversation*,
        # which forbids the *Confirm, then write* step outright -- and §9 says that
        # confirmation is the only verification a voice model has. A rule that
        # bans the one check reads as caution and leaves the model unverifiable.
        #
        # **The first version of this test failed on the file it was written
        # for**, and the reason is worth keeping: it asserted the retired
        # wording was absent, and the paragraph recording the retirement quotes
        # it. That is ``spelling_scan.py``'s mention-versus-use distinction
        # arriving in an assertion -- a rule stated and a rule quoted as retired
        # are not the same string in the same role. So the check is that the new
        # rule is stated and that the old one appears only in its retirement.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("never goes anywhere the author is not the audience", voice)
        self.assertIn("It read *never leaves", voice)

    def test_the_paired_version_and_the_co_written_sample_are_both_written_down(self):
        # Two things the samples taught the method rather than the other way
        # round, and neither was predicted. A paired document yields a pair whose
        # generic half is **attested** rather than composed; a co-written one
        # models the co-author, which is §6's trap with the sign flipped and is
        # harder to see because the result reads better rather than worse.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("where both halves are attested", voice)
        self.assertIn("a sample somebody else helped write", voice)

    def test_the_default_is_full_voice_and_damping_is_not_a_register(self):
        # **This rule was written backwards first and the clinician reversed it
        # within the hour**, which is why it is pinned rather than left to prose.
        # Two damped documents were read as evidence of a register he uses for
        # academic audiences, and the correction was *"i don't want this to be
        # tame because that is not me, those were outliers."*
        #
        # **The failure it now guards runs one way and is the worse one.** A
        # model that treats damping as a register produces a tame draft **and can
        # cite the author's own corpus in its defense** -- which is #213 closed by
        # institutionalizing the defect it was filed on. So the assertion is on
        # the default, on the named-constraint limb that is the only way down
        # from it, and on the damped samples being pairs rather than targets.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("The default is full voice", voice)
        self.assertIn("Intensity is only ever reduced against a constraint the author names", voice)
        self.assertIn("Constraints on the setting", voice)

    def test_the_defect_list_is_cited_rather_than_copied(self):
        # #143: a list restated in two files goes stale in one of them. §12 owns
        # the mechanical defects; ``voice.md`` §6 is the rule that a model must
        # not imitate them, which is a different claim and needs no second copy.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("deliberately not restated here", voice)
        self.assertNotIn("isvery commonand", voice)

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


class TheReferenceHoldsNoOneProgramsEnrollment(unittest.TestCase):
    """#226's ruling of 2026-08-19. **Not** a per-account detector.

    #222 ruled the same day that the prose-and-table shape is a person's job,
    because telling one account's site name from a universal payer string needs
    the name vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build and #212 re-ruled. **That ruling stands and nothing here
    reverses it.** What this class reaches is four *literal* shapes that can
    never be universal Medatrax behavior: a course code, a learning-management
    vendor's host, a term date, and an accumulated hours total. The first three
    catch #226's own material arriving back; the fourth is
    [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235)'s,
    and it reaches one figure of the seven that ticket removed because it is
    the only one with a shape. Nothing wider.

    **A per-account *figure* still has no shape in general, and #235 measured
    that rather than assuming it.** Of three candidates it weighed, a
    sampled-day breakdown (``eight of eleven``) sits on 28 lines of legitimate
    fixture prose and was refused; a totals table row was keyable but escapable
    by writing the same figure as a sentence, and was refused too. Only the
    hours shape survived. **One shape having been found does not make the class
    a per-account detector**, and #222's ceiling is where it was.

    **A green run here is not a read file**, and what it passes is the larger
    half. The block #226 emptied out of ``reference/medatrax-fields.md`` also
    carried an hours table, a planning target above the documented figure, a
    prior-coursework ruling, a five-row area breakdown and an evaluation
    cadence -- five kinds of per-program **figure**, none of which has a shape a
    regex can key on, and all of which stay a reader's job. *Field selection
    rules* is a reader's job too. **No count of them is stated here**: the
    ticket's own enumeration and a draft of this docstring disagreed on it,
    which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
    arriving inside the paragraph arguing for honest proportion.

    **Every pattern is exercised against synthetic material, never against the
    strings the ticket removed.** A checker asserting the reference holds no LMS
    host must not become the one file that holds one -- which a first version of
    this class did, with the real institution's host and both real term dates
    typed into its own assertions. That is ``phi_scan``'s *no file may exempt
    itself* arriving on a test, and it was caught by the standards axis of the
    review rather than by anything here.

    **Three of the four patterns are narrower than their names**, and every
    narrowing is measured rather than guessed:

    - A four-digit number reading as a year, or zero-padded, is **not** a course
      code. Without that the pattern fires on ``ADR 0001``, ``AHA/ACC 2025``,
      ``GOLD 2026``, ``ADA 2026`` and ``IDSA 2023`` -- society-plus-year
      citations and this repo's own ADR links, seven distinct shapes across the
      tracked tree. What it costs is a course genuinely numbered ``0100`` or
      ``2026``, which is invisible.
    - A term date is a date with a term word **beside** it, not merely on the
      same line. A bare ISO date cannot be the trigger at all -- this repo
      writes ``read 2026-08-09`` and ``measured 2026-08-11`` everywhere, which
      is ``phi_scan.py``'s own reason for not flagging one in its shape layer.
      Same-line proximity was not enough either: it fired on seven lines across
      the tree including **this ticket's own new prose in CLAUDE.md**, green
      only because the reference is the sole haystack. Within 40 characters and
      no sentence break, it fires on **zero** lines tree-wide and still catches
      the shape the block was written in. Measured 2026-08-19.
    - An hours total needs **three** hour digits, not two. The per-pattern
      figures and the false alarm this one does *not* exclude are on
      ``ACCUMULATED_HOURS`` itself, where the regex a reader is checking sits.

    ``test_the_instrument_is_live`` carries a positive case for every pattern
    and a negative for every false alarm above, on
    ``test_build_artifacts_ignored.py``'s reasoning -- four patterns that
    matched nothing would report a clean file and be indistinguishable from
    four patterns aimed at the wrong thing.

    **Every false-alarm case is quoted verbatim from the tracked tree**, and
    that is not decoration: a case stitched together from a real clause and an
    invented one reads as a measured false alarm while being a sentence nobody
    wrote. Three such cases shipped in #235's first draft and were caught by
    the standards axis of the review.
    """

    #: Letters then four digits, excluding a year and a zero-padded number.
    COURSE_CODE = re.compile(r"\b[A-Z]{3,4} ?(?!19\d\d\b|20\d\d\b|0)\d{4}\b")

    #: Vendor hosts, never a bare product name. An earlier draft matched
    #: ``canvas\.`` and would have fired on any sentence ending in the word
    #: *Canvas*, which is a check that has to be worked around on the day it
    #: lands. A floor: a vendor not listed here is invisible.
    LMS_HOST = re.compile(
        r"\b(?:instructure|blackboard|brightspace|canvaslms|moodle|d2l)\.[a-z]{2,}",
        re.IGNORECASE,
    )

    #: An accumulated hours total, as the portal renders one under *Hours to
    #: Date* or *Total time log*. Three or more hour digits, and the
    #: narrowing is measured rather than guessed. **Over every tracked file
    #: at the base commit**, two digits sits on **84** lines and almost all
    #: are real -- a visit time is ``0:35``, a shift is ``12:00``, a recorded
    #: portal time is ``19:20``. Three digits sits on **3**: the two
    #: [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235)
    #: removed, and one that is **not** an hours total at all.
    #:
    #: **The haystack is named because a first draft of this line measured a
    #: different one.** It read *67 tree-wide*, counted over ``*.md`` only,
    #: and the sentence claiming *tree-wide* read exactly like one that had
    #: been. That is ``guidelines_extract``'s retired N=3 boundary arriving
    #: on a regex -- a figure measured against the wrong input is not
    #: distinguishable from a right one by looking at it. Caught by the
    #: standards axis of the review. Re-derived 2026-08-19.
    #:
    #: **The third hit is a false alarm this pattern does not exclude**, and
    #: it is named rather than engineered around: ``Ann Intern Med.
    #: 2015;162:35-45`` in ``tools/testdata/uspstf/``, a volume-and-page
    #: citation. It costs nothing because the haystack is one reference file
    #: that carries no journal citation -- checked, not assumed -- and a
    #: narrowing to exclude it would be tuning against a file the check
    #: never reads.
    #:
    #: **A floor, and a low one**: a bare count of visits is an integer and
    #: has no shape at all, which is why this limb is not a per-account
    #: detector and #222's ceiling is not moved by it.
    ACCUMULATED_HOURS = re.compile(r"\b\d{3,}:[0-5]\d\b")

    #: A term word, then within 40 characters and no sentence break, a date.
    TERM_DATE = re.compile(
        r"\b(?:start|starts|starting|due|deadline|semester|end date|term date)\b"
        r"[^.]{0,40}?\b20\d{2}-\d{2}-\d{2}\b",
        re.IGNORECASE,
    )

    def assert_reference_is_free_of(self, pattern, holds, remedy):
        """Assert ``reference/medatrax-fields.md`` matches ``pattern`` nowhere.

        One helper for all four limbs rather than four near-identical bodies,
        and it reports the **matched spans** rather than the whole file: the
        haystack is a reference document, and a failure that prints it is a
        failure nobody reads.
        """
        found = sorted({match.group(0) for match in pattern.finditer(read(MEDATRAX))})
        self.assertEqual(
            found, [], f"reference/medatrax-fields.md {holds}. {remedy}: {found}"
        )

    def test_the_instrument_is_live(self):
        # Synthetic throughout -- see the docstring. The vendor host is real
        # because the pattern is about vendors; the institution in front of it
        # is not.
        self.assertTrue(self.COURSE_CODE.search("ABC 1234 - a course, across the lifespan"))
        self.assertTrue(self.COURSE_CODE.search("prior coursework (ABC1234, ABC1235)"))
        self.assertTrue(self.LMS_HOST.search("https://example.instructure.com/courses/1/pages/x"))
        self.assertTrue(self.LMS_HOST.search("https://learn.blackboard.com/hours"))
        self.assertTrue(self.LMS_HOST.search("https://example.moodle.org/course/view.php"))
        self.assertTrue(self.TERM_DATE.search("Both courses start **2019-01-07**, due **2019-05-03**."))
        self.assertTrue(self.TERM_DATE.search("Documentation deadline 2019-05-10."))
        # Synthetic hours, deliberately not the two #235 removed -- see the
        # docstring. A checker asserting the reference states no hours total
        # must not become the one file that states one.
        self.assertTrue(self.ACCUMULATED_HOURS.search("| Total time log | 100:00 |"))
        self.assertTrue(self.ACCUMULATED_HOURS.search("Hours to Date reads 987:04."))

        # And every false alarm the review found. **Each case below is quoted
        # verbatim from the tracked tree** -- checked, not remembered. A first
        # version of the two hours cases stitched a real clause to an invented
        # one and to a hyphen where the source writes an en dash, which reads
        # as a measured false alarm and is a sentence nobody ever wrote.
        for citation in ("ADR 0001", "AHA/ACC 2025", "GOLD 2026", "ADA 2026", "IDSA 2023"):
            self.assertIsNone(
                self.COURSE_CODE.search(citation),
                f"{citation} is a citation or an ADR link, not a course code",
            )
        self.assertIsNone(self.LMS_HOST.search("the program's hours breakdown on Canvas."))
        for duration in (
            "Visit Time 0:35 = 08:35 - 08:00, both estimated.",
            "0:30 to 0:45 across one sampled day, a flat 0:15 across another",
            "The portal has case 10 at 19:20–19:50",
        ):
            self.assertIsNone(
                self.ACCUMULATED_HOURS.search(duration),
                f"a clock time or a visit duration is not an hours total: {duration}",
            )
        for measurement in (
            "The offsets are one-based over the LF form, measured 2026-08-11",
            "The reference was read 2026-08-11",
            "**#69 was ruled on 2026-08-16 and moved no digit, so one of the two remains.**",
        ):
            self.assertIsNone(
                self.TERM_DATE.search(measurement),
                "a measurement date is not a term date",
            )

    def test_the_reference_names_no_course(self):
        self.assert_reference_is_free_of(
            self.COURSE_CODE,
            "names a course code, which is one clinician's enrollment rather "
            "than Medatrax behavior",
            "setup-clinical-skills step 3 collects it and "
            "scratch/medatrax-profile.md holds it",
        )

    def test_the_reference_links_no_learning_management_system(self):
        self.assert_reference_is_free_of(
            self.LMS_HOST,
            "links one institution's learning-management system",
            "the authoritative-source rule is universal and belongs here; the "
            "URL is per-program and belongs in the profile",
        )

    def test_the_reference_states_no_hours_to_date_total(self):
        """#235's decision 4, ruled 2026-08-19, and it reaches one figure.

        #226 moved the **ruling** about the hours-to-date figure to the profile
        and left the figure itself thirty lines above where its explanation had
        been -- an unexplained account-specific integer where an explained one
        had stood, which is worse than either end state. This is the only one
        of that section's seven totals with a shape, and it is the one the
        ticket calls the sharp one.

        **The figure is not quoted here, and that is the rule rather than
        fastidiousness.** A first version of this docstring named it, which put
        the removed string back into the repo inside the check built to keep it
        out -- the same self-exemption the class docstring above records being
        caught once already, arriving one method lower.
        """
        self.assert_reference_is_free_of(
            self.ACCUMULATED_HOURS,
            "states an hours-to-date total, which is what one account had "
            "accrued on one afternoon rather than Medatrax behavior",
            "the figure and the ruling about what it does and does not carry "
            "both belong in scratch/medatrax-profile.md",
        )

    def test_the_reference_states_no_term_date(self):
        self.assert_reference_is_free_of(
            self.TERM_DATE,
            "states a term date",
            "course start and end dates are collected by setup-clinical-skills "
            "step 3 and live in scratch/medatrax-profile.md",
        )

    def test_the_reference_keeps_the_why_it_gave_up_the_numbers_for(self):
        """Decision 1's whole point, and the half a delete would have lost.

        The documentation deadline is described across this repo as *the
        constraint the whole toolchain exists to satisfy*. Moving the number to
        the profile is the ruling; moving the motivation with it is not, and a
        later tidy that shortened the abstracted block to a bare pointer would
        do exactly that with nothing to notice.
        """
        text = read(MEDATRAX)
        self.assertIn("the constraint this whole toolchain exists to satisfy", text)
        self.assertIn("area breakdown", text)
        self.assertIn("Objectives page", text)

    def test_setup_collects_what_the_reference_now_defers(self):
        """The cross-file half. A pointer at a step that collects nothing is
        worse than the leak it replaced, because it reads as a split that was
        made.

        **Scoped to the collecting steps, and that is not tidiness.** Checking
        the whole file passed ``evaluation`` on step 2's sentence about the
        ``evaluations.medatrax.com`` host -- green for the wrong reason, on a
        fact step 3 did not collect until #226 added it.
        """
        setup = read(SETUP)
        start = setup.find("### 3. Program and hours")
        self.assertNotEqual(
            start, -1, "setup-clinical-skills has no step 3 heading to read from"
        )
        end = setup.find("### 5.", start + 1)
        self.assertNotEqual(
            end,
            -1,
            "setup-clinical-skills has no step 5 heading, so steps 3 and 4 have "
            "no end. Renumbering a step redirects every citation to it -- see "
            "that skill's own step 10",
        )
        collecting = setup[start:end]
        for asked in (
            "hour requirement",
            "area breakdown",
            "start and end dates",
            "documentation deadline",
            "evaluation schedule",
            "Women's Health",
        ):
            # ``assertTrue`` rather than ``assertIn``: the haystack is two whole
            # steps, and a failure that prints them is a failure nobody reads.
            self.assertTrue(
                asked in collecting,
                f"reference/medatrax-fields.md defers {asked!r} to "
                "setup-clinical-skills steps 3 and 4, which do not collect it",
            )


if __name__ == "__main__":
    unittest.main()
