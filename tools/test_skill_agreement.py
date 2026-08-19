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

**One class here is not a named pair, and it is the reason the file grew a
walker.** [#233](https://github.com/mshamblin5150-code/clinical-skills/issues/233)
is the same defect with the second document unknown in advance: a skill's steps
are numbered headings and other files cite them **by number**, so inserting a
step silently redirects every citation. The pairs above are enumerated because
somebody noticed them; this one cannot be, because the whole point is that
nobody notices. So ``EveryCitedStepResolvesToADeclaredStep`` walks the tracked
tree instead of naming files, and the ruling it asserts -- *a cited step
exists* -- is the one thing about a cross-reference that holds without reading
either end.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from typing import Iterator, NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SKILLS_DIR = REPO_ROOT / "skills"
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


#: A skill's own step heading -- ``### 4. Draft the body``. Two to four hashes
#: because the skills are not uniform about depth and the number is the subject.
STEP_HEADING = re.compile(r"^#{2,4}\s+(\d+)\.\s")

#: A citation of one. ``steps?`` for the plural opener of *steps 1 and 2*, which
#: this reads as a citation of 1 and misses the 2 -- a floor rather than a
#: ceiling, on ``differential_scan.py``'s terms. The separator admits any
#: whitespace so a **hard-wrapped** citation is still seen. That costs nothing
#: today -- it finds not one match the single-space form misses, measured
#: 2026-08-19 -- and ``test_run_record_claim`` is where a wrapped phrase went
#: unread by the very check written to find it.
STEP_CITATION = re.compile(r"\bsteps?[-‑\s]+(\d+)\b", re.IGNORECASE)

#: Under ``fixtures/``, these two names are prose about a run and everything
#: else is the run. See ``graded_files``.
FIXTURE_PROSE = {"README.md", "assertions.md"}


def skill_names() -> list[str]:
    """Every ``skills/<name>/`` holding a ``SKILL.md``, longest name first.

    Longest first so an alternation cannot match a shorter name inside a longer
    one. No pair overlaps today; the ordering is here so that a sixth skill
    called ``clinical-note-lite`` could not quietly resolve as ``clinical-note``.
    """
    names = [path.name for path in SKILLS_DIR.iterdir() if (path / "SKILL.md").is_file()]
    return sorted(names, key=lambda name: (-len(name), name))


def declared_steps(name: str) -> set[int]:
    """The numbered step headings ``skills/<name>/SKILL.md`` declares."""
    return {
        int(found.group(1))
        for line in read(SKILLS_DIR / name / "SKILL.md").splitlines()
        for found in [STEP_HEADING.match(line)]
        if found
    }


def paragraphs(text: str) -> Iterator[tuple[int, str]]:
    """Blocks of consecutive non-blank lines, with the line each one opens on.

    The paragraph is the resolution scope rather than the line, because this
    repo hard-wraps its prose: a subject named at the end of one line is carried
    by the next, and a line-scoped reader would drop it.
    """
    block: list[str] = []
    start = 1
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not block:
                start = number
            block.append(line)
        elif block:
            yield start, "\n".join(block)
            block = []
    if block:
        yield start, "\n".join(block)


class Citation(NamedTuple):
    """One ``step N``, and whose step N it turned out to be."""

    line: int
    number: int
    skill: str | None
    how: str


def step_citations(text: str, owner: str | None, names: list[str]) -> Iterator[Citation]:
    """Every ``step N`` in ``text``, resolved to the skill it names -- or to nothing.

    **Three limbs, and they are how a person reads one rather than a heuristic.**

    - ``beside`` -- a skill is named immediately before the words, with nothing
      but its own link or path punctuation in between. ``[clinical-note](../
      clinical-note/SKILL.md) step 5`` and ```icd10-cpt`` step 4`` are both this,
      and it is the only limb that can name a skill other than the file's own.
    - ``carried`` -- a bare ``step N`` continues the subject of the citation
      before it, **unless another skill has been named in between**. That last
      clause is the whole of it: *"[clinical-note] step 2 and [batch-shift], for
      step 9's shorthand"* is ``setup-clinical-skills``'s own step 9, and
      dropping the clause resolves it to ``batch-shift`` and fails a correct line.
    - ``owner`` -- otherwise, the skill whose directory the file sits in.

    **Both simpler rules were tried against the tree first and both failed.**
    Nearest-name-anywhere fails two correct lines in
    ``setup-clinical-skills/SKILL.md``; adjacency with no carry fails
    ``clinical-note/GLOSSARY.md``'s *"on the same terms as the voice model in
    step 8"*, which continues a ``setup-clinical-skills`` subject set earlier in
    the same sentence. Three limbs is what it took to reach zero false alarms,
    and each was added because a real line demanded it.

    **A file outside ``skills/`` with nothing beside the citation is unresolved,
    and stays that way.** ``anchor_scan.py`` said ``step-4`` six times meaning
    ``icd10-cpt``, and no rule here could know that. The alternative is a guess,
    and ``differential_scan.py``'s first version is what a positional guess
    costs: it failed in both directions. Unresolved citations are counted and
    reported; they are never failed -- which is what made
    [#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238)'s
    repair safe to make: naming the skill beside those six converted them with no
    change here. What is left unresolved is ``fixtures/`` prose and the repo-root
    documents.
    """
    beside = re.compile("(" + "|".join(re.escape(name) for name in names) + r")\S*\s*$")
    anywhere = re.compile("|".join(re.escape(name) for name in names))
    for start, block in paragraphs(text):
        previous: str | None = None
        end = 0
        for found in STEP_CITATION.finditer(block):
            before = block[: found.start()]
            adjacent = beside.search(before)
            if adjacent:
                skill, how = adjacent.group(1), "beside"
            elif previous and not anywhere.search(block[end : found.start()]):
                skill, how = previous, "carried"
            else:
                skill, how = owner, "owner"
            previous, end = skill, found.end()
            yield Citation(start + before.count("\n"), int(found.group(1)), skill, how)


def owning_skill(path: Path, names: list[str]) -> str | None:
    """The skill whose directory ``path`` sits in, if any."""
    try:
        parts = path.resolve().relative_to(SKILLS_DIR).parts
    except ValueError:
        return None
    return parts[0] if parts and parts[0] in names else None


def graded_files() -> list[Path]:
    """Tracked ``.md`` and ``.py``, minus the preserved run records.

    **``fixtures/`` is excluded bar its own prose, and the reason is that a
    record cannot be edited to fix a stale citation.** A note under
    ``fixtures/filled-anchor/notes/`` cites the skill **as it stood when the run
    happened** -- that is what makes it evidence -- so grading one would refuse a
    faithful record, and the only repair available would be to falsify it. The
    two prose names are graded because they are maintained documents *about* a
    run, and a stale ``step 7`` in one is an ordinary defect.

    **The default under ``fixtures/`` is to exclude**, so a new kind of record
    lands outside the check rather than inside it. What that costs is measured:
    140 of the 164 citations under ``fixtures/`` are in records, and every one of
    them is unresolved anyway -- so today the exclusion drops nothing the
    resolver could have graded. It is here for the record that arrives tomorrow
    naming its skill.

    **This module is dropped too, and it is the only other exclusion.** The
    resolver's own test cases are deliberately hostile strings -- a link labelled
    for one skill pointing at another, a citation to a step that does not exist
    -- and grading them would fail the file for containing its own fixtures. The
    cost is real and narrow: a genuine ``step N`` citation written into the prose
    *here* is the one the tree-wide walk cannot see. It is asserted below rather
    than only described, because ``test_run_record_claim.py`` carried this exact
    exemption in its docstring for one round while the walk had no filter wired.
    """
    finished = subprocess.run(
        ["git", "ls-files", "--cached", "--", "*.md", "*.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    kept = []
    for line in finished.stdout.splitlines():
        if not line.strip():
            continue
        path = REPO_ROOT / line
        if line.startswith("fixtures/") and path.name not in FIXTURE_PROSE:
            continue
        if path.resolve() == SELF:
            continue
        kept.append(path)
    return kept


def walk_citations() -> list[tuple[Path, Citation]]:
    """Every ``step N`` in every graded file, paired with the file it is in.

    Three tests in ``EveryCitedStepResolvesToADeclaredStep`` want this walk under
    different filters -- the per-limb floors, the unresolved report, and #238's
    ``tools/`` rule -- and the third is what made repeating it worth removing.
    ``stale_citations`` deliberately does **not** use this: it takes ``declared``
    as a parameter so the check can be pointed at a renumbering that has not
    happened, and deriving the skill names from that map rather than from the
    tree is the whole of how that works.
    """
    names = skill_names()
    return [
        (path, cite)
        for path in graded_files()
        for cite in step_citations(read(path), owning_skill(path, names), names)
    ]


def stale_citations(declared: dict[str, set[int]]) -> list[str]:
    """Every resolved ``step N`` naming a step ``declared`` does not hold.

    ``declared`` is a parameter rather than a lookup so the check can be pointed
    at a **renumbering that has not happened**. Asserting the tree is clean today
    proves the walk found nothing; asserting it goes red when a step is taken
    away proves the walk would find something. Only the second is evidence.
    """
    names = sorted(declared, key=lambda name: (-len(name), name))
    stale = []
    for path in graded_files():
        owner = owning_skill(path, names)
        for cite in step_citations(read(path), owner, names):
            if cite.skill is None or cite.number in declared[cite.skill]:
                continue
            where = path.relative_to(REPO_ROOT).as_posix()
            stale.append(f"{where}:{cite.line} cites {cite.skill} step {cite.number} ({cite.how})")
    return stale


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


class TheStepResolverIsLive(unittest.TestCase):
    """A resolver that named nothing would pass every assertion in the class below.

    Each case here is a shape taken off the real tree rather than invented, and
    the two marked *false alarm* are lines a simpler rule failed. They are the
    reason the resolver has three limbs instead of one.
    """

    NAMES = ["setup-clinical-skills", "practicum-case-study", "clinical-note", "batch-shift"]

    def resolve(self, text: str, owner: str | None = None) -> list[Citation]:
        return list(step_citations(text, owner, self.NAMES))

    def test_a_step_heading_is_read_and_a_numbered_list_is_not(self) -> None:
        """The hashes are load-bearing, and a list item must not inflate the set.

        Relax ``STEP_HEADING`` to tolerate a missing ``#`` and every ordinary
        numbered list in a ``SKILL.md`` registers as a declared step. The set
        inflates, and every stale citation then resolves clean -- the silent-pass
        shape, arriving through the half of the check nobody looks at.
        """
        self.assertEqual(declared_steps("icd10-cpt"), {1, 2, 3, 4, 5})
        self.assertEqual(declared_steps("setup-clinical-skills") & {0}, {0})
        for not_a_heading in ("1. Read the chart", "  ### 2. Indented", "##### 3. Too deep"):
            with self.subTest(line=not_a_heading):
                self.assertIsNone(STEP_HEADING.match(not_a_heading))
        self.assertEqual(STEP_HEADING.match("### 4. Draft the body").group(1), "4")

    def test_a_link_beside_the_words_names_the_skill(self) -> None:
        cite, = self.resolve("See [batch-shift](../batch-shift/SKILL.md) step 6.", "clinical-note")
        self.assertEqual((cite.skill, cite.number, cite.how), ("batch-shift", 6, "beside"))

    def test_a_backticked_name_beside_the_words_names_the_skill(self) -> None:
        """``anchor_scan.py`` and ``corpus_census.py`` cite this way, from ``tools/``."""
        cite, = self.resolve("``clinical-note`` step 1 rests on whole day files.")
        self.assertEqual((cite.skill, cite.how), ("clinical-note", "beside"))

    def test_a_bare_path_beside_the_words_names_the_skill(self) -> None:
        """``docx_write.py``'s form, and it is one of the citations #233 was filed over."""
        cite, = self.resolve("``skills/practicum-case-study/SKILL.md`` step 9's sentence.")
        self.assertEqual((cite.skill, cite.number), ("practicum-case-study", 9))

    def test_a_bare_citation_takes_the_skill_whose_file_it_is(self) -> None:
        cite, = self.resolve("| **Neither** | Report it -- see step 4 |", "batch-shift")
        self.assertEqual((cite.skill, cite.how), ("batch-shift", "owner"))

    def test_a_second_citation_carries_the_first_ones_subject(self) -> None:
        """``voice.md``'s *"step 5, before drafting, and step 9"*.

        The first resolves by ``owner`` rather than ``beside``, and that is the
        point of the case: a **relative** link back to the skill's own file
        spells no skill name anywhere, so only the directory settles it. The
        second then carries the first's subject.
        """
        first, second = self.resolve(
            "[SKILL.md](../SKILL.md) step 5, before drafting, and step 9, where the draft is read.",
            "practicum-case-study",
        )
        self.assertEqual((first.skill, first.how), ("practicum-case-study", "owner"))
        self.assertEqual((second.skill, second.how), ("practicum-case-study", "carried"))

    def test_a_relative_self_link_is_not_a_named_skill(self) -> None:
        """``[SKILL.md](../SKILL.md)`` names nothing, so outside ``skills/`` it is unresolved."""
        cite, = self.resolve("[SKILL.md](../SKILL.md) step 5, before drafting.", None)
        self.assertIsNone(cite.skill)

    def test_the_subject_carries_across_a_hard_wrap(self) -> None:
        """The paragraph is the scope, so a wrapped line does not restart it."""
        first, second = self.resolve(
            "[setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects it,\n"
            "on the same terms as the voice model in step 8.",
            "clinical-note",
        )
        self.assertEqual(first.skill, "setup-clinical-skills")
        self.assertEqual((second.skill, second.line, second.how), ("setup-clinical-skills", 2, "carried"))

    def test_a_hard_wrapped_citation_is_still_read(self) -> None:
        """No line in the tree wraps between the word and the number. One will."""
        cite, = self.resolve("...which is [batch-shift](../batch-shift/SKILL.md) step\n3.", "clinical-note")
        self.assertEqual((cite.skill, cite.number), ("batch-shift", 3))

    def test_a_name_in_between_breaks_the_carry(self) -> None:
        """False alarm 1, from ``setup-clinical-skills/SKILL.md``.

        *"[clinical-note] step 2 and [batch-shift], for step 9's shorthand"* --
        the ``step 9`` is ``setup``'s own, and both a nearest-name rule and a
        carry with no interruption clause resolve it to a skill with 7 steps and
        fail a correct line.
        """
        first, second = self.resolve(
            "**Hard** -- [clinical-note](../clinical-note/SKILL.md) step 2 and "
            "[batch-shift](../batch-shift/SKILL.md), for step 9's shorthand.",
            "setup-clinical-skills",
        )
        self.assertEqual(first.skill, "clinical-note")
        self.assertEqual((second.skill, second.how), ("setup-clinical-skills", "owner"))

    def test_a_sentence_boundary_does_not_carry_a_stale_subject(self) -> None:
        """False alarm 2, the other ``setup-clinical-skills`` line a nearest-name rule failed."""
        cites = self.resolve(
            "[clinical-note](../clinical-note/SKILL.md) expands shorthand at step 2. Read it\n"
            "before asking; it is not restated here, on step 8's arrangement.",
            "setup-clinical-skills",
        )
        self.assertEqual(cites[-1].skill, "setup-clinical-skills")

    def test_a_bare_citation_outside_a_skill_stays_unresolved(self) -> None:
        """``anchor_scan.py``'s ``step-4`` meant ``icd10-cpt`` and nothing here could know it.

        The line is that module's, as it stood before #238 named the skill beside
        it. Kept verbatim: the shape is what this grades, and a repaired tree is
        not a reason to stop testing the shape it was repaired out of.
        """
        cite, = self.resolve("# Step 4's heading. The lookbehind is load-bearing.", None)
        self.assertIsNone(cite.skill)

    def test_the_plural_opener_is_a_floor_and_says_so(self) -> None:
        """*steps 1 and 2* is read as a citation of 1. The 2 is missed, deliberately."""
        self.assertEqual([c.number for c in self.resolve("if steps 1 and 2 move", "batch-shift")], [1])


class EveryCitedStepResolvesToADeclaredStep(unittest.TestCase):
    """#233: a ``step N`` citation must point at a step that exists.

    **Two renumberings in a week, and correctness rested on somebody
    remembering.** ``setup-clinical-skills``'s silently redirected ``voice.md``'s
    citation; ``practicum-case-study``'s on #214 moved seven citations across
    five files and all seven re-derive correct only because the author went
    looking with a ``grep``. Nothing required that, and nothing would have failed
    if one had been missed. A reader following *"see step 7"* to the wrong step
    gets a coherent, wrong answer, which is worse than landing on nothing.

    **What it reaches, and the gap is the sharper half.** It catches a citation
    to a step that does not exist. It cannot catch a citation to a step that
    still exists and now **means something else** -- insert a step at the top and
    every number below it shifts, and only citations at or above the old maximum
    come back missing. On #214, steps 3 to 8 became 4 to 9: the four ``step 9``
    citations would have fired and the ``step 5``, ``6`` and ``7`` ones would
    have resolved silently to the wrong step. **A green run here is not a walked
    citation**, which is ``differential_scan.py``'s *a clean scan is not a walked
    row* arriving on a cross-reference.

    **A minority of citations are unresolved and are never failed.** Guessing
    would have been the alternative, and this class asserts a floor on each limb
    below so that a resolver quietly falling back to *unresolved* for everything
    cannot read as a clean run.

    **``tools/`` is no longer among them, and that half is now a rule.**
    [#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238)
    priced the repair -- ``anchor_scan.py`` alone said ``step-4`` six times
    meaning ``icd10-cpt`` -- and it was prose, not a parser change.
    ``test_every_citation_in_tools_resolves`` keeps it, because a reword that
    dropped a name would put those citations back out of reach in silence. What
    stays unresolved is ``fixtures/`` prose and the repo-root documents, and the
    fixture half is left deliberately: several of those sentences name a skill
    **as it stood at run time**.

    **No count is stated here, and the reason is that the first draft's went
    stale before it was merged.** It read *38 unresolved* against a tree that had
    120 resolved; merging ``origin/main`` the same day -- #226 and #228, neither
    of which has anything to do with this ticket -- moved both, because every
    paragraph either adds carries a citation or does not. That is
    [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)
    exactly: **a measurement's expiry date is the next commit to the thing it
    measures**, and here the thing measured is the whole tracked tree. Anything
    wanting the live numbers runs this module's own ``step_citations`` over
    ``graded_files()``, which is one loop and cannot go stale.
    """

    def declared(self) -> dict[str, set[int]]:
        return {name: declared_steps(name) for name in skill_names()}

    def test_the_walk_reaches_the_repo(self) -> None:
        files = graded_files()
        self.assertGreater(len(files), 50, "git ls-files returned too little to be a checkout")
        self.assertIn(REPO_ROOT / "CLAUDE.md", files)
        self.assertIn(CASE_STUDY_VOICE, files)

    def test_the_walk_grades_fixture_prose_and_not_the_records(self) -> None:
        """A record cites the skill as it stood at run time and may not be edited."""
        walked = {path.relative_to(REPO_ROOT).as_posix() for path in graded_files()}
        self.assertIn("fixtures/README.md", walked)
        self.assertIn("fixtures/filled-anchor/assertions.md", walked)
        self.assertNotIn("fixtures/filled-anchor/notes/case-01.md", walked)
        self.assertNotIn("fixtures/filled-anchor/run-2/case-01.md", walked)

    def test_the_walk_drops_this_module_and_only_this_module(self) -> None:
        """Asserted rather than described, on ``test_run_record_claim.py``'s lesson."""
        walked = graded_files()
        self.assertNotIn(SELF, [path.resolve() for path in walked])
        self.assertIn(REPO_ROOT / "tools" / "test_run_record_claim.py", walked)

    def test_every_skill_declares_steps(self) -> None:
        """A heading pattern that matched nothing would grade every citation clean.

        The floor is 3 and not the 5 the shortest skill happens to declare today.
        ``icd10-cpt`` has exactly five steps, so a floor of 5 would go red the
        first time somebody folded its E/M step into the one above -- a content
        decision with nothing to do with #233, reported as a broken regex.
        """
        for name in skill_names():
            with self.subTest(skill=name):
                self.assertGreaterEqual(len(declared_steps(name)), 3)

    def test_each_limb_of_the_resolver_carries_real_citations(self) -> None:
        """Floors, not counts. A limb that stopped firing must not read as clean.

        **Deliberately well below what the tree holds**, and the margin is the
        whole design: a figure pinned at the measurement is
        [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
        and would fail on the next paragraph anybody writes. That is not
        hypothetical here -- the numbers this docstring first quoted were stale
        within the day, moved by a merge from two tickets unrelated to this one.
        The floors were not, which is the argument for stating a bound rather
        than a measurement.
        """
        seen = {"beside": 0, "carried": 0, "owner": 0, "unresolved": 0}
        for _path, cite in walk_citations():
            seen[cite.how if cite.skill else "unresolved"] += 1
        for limb, floor in (("beside", 20), ("carried", 5), ("owner", 25)):
            with self.subTest(limb=limb):
                self.assertGreaterEqual(seen[limb], floor)

    def test_the_unresolved_limb_is_reported_and_never_floored(self) -> None:
        """The gap is counted, and deliberately has **no** floor under it.

        A floor on ``unresolved`` would assert that the gap persists, so teaching
        ``anchor_scan.py`` to name ``icd10-cpt`` beside its six ``step-4``
        mentions -- which is exactly the repair #233 invited -- would have turned
        the suite red for an improvement. **#238 then made that repair**, so this
        is no longer a hypothetical: an early draft carrying a floor here would
        have gone red on it. The three limbs above are what keep a resolver that
        quietly resolved *nothing* from reading as a clean run.
        """
        unresolved = [cite for _path, cite in walk_citations() if cite.skill is None]
        self.assertEqual([cite for cite in unresolved if cite.how != "owner"], [])

    def test_every_citation_in_tools_resolves(self) -> None:
        """#238: a ``tools/`` module names the skill whose step it cites.

        **The repair was prose, and nothing held it.** A bare ``step-4`` cited a
        skill whose steps could be renumbered tomorrow with nothing to notice,
        because unresolved is never failed. Naming the skill once per paragraph
        converted every such citation in the directory with **no change to the
        resolver**, which is why #238 priced it as cheap -- and it is why a
        reword dropping a name would put them straight back, in silence. So the
        state is pinned rather than described. **The ticket enumerated ten in
        three modules and the directory held more**; no figure is repeated here,
        because the count moves with the next docstring anybody writes.

        **Scoped to ``tools/`` because that is where #238 stopped.** The
        citations still unresolved are in ``fixtures/`` prose and the repo-root
        documents. The fixture half is left deliberately: several of those
        sentences name a skill **as it stood at run time**, and rewording one to
        resolve risks making a historical statement read as a current one. That
        is a judgment rather than a mechanical fix, and it is not this test's.

        **What it costs, stated because it is real.** A ``tools/`` docstring
        writing *step 2 of the rebuild* -- a step of something that is not a
        skill at all -- fails here, and the only remedy is a reword. Every
        ``step N`` in ``tools/`` today is a skill's step, so the rule costs
        nothing now; it is a bet that the next one will be too, and the ticket's
        own *not worth doing at all* fork is the argument against it.

        **The whole subtree, and ``tools/testdata/`` carved out of it.** The
        first version tested ``path.parent`` and so reached the top level only:
        a ``tools/<subdir>/module.py`` would have escaped in silence, with both
        floors below still green, and it costs nothing today because no graded
        file sits below ``tools/`` bar one -- which is exactly why nobody would
        have noticed. ``tools/testdata/`` is then excluded on ``graded_files``'s
        own reasoning about ``fixtures/``: a sample of a catalog is a record of
        what one looks like, and editing it to name a skill would falsify the
        sample rather than fix a citation. It holds no ``step N`` today; the
        carve-out is for the sample that arrives tomorrow.
        """
        def in_scope(path: Path) -> bool:
            tools = REPO_ROOT / "tools"
            return tools in path.parents and (tools / "testdata") not in path.parents

        walked = [path for path in graded_files() if in_scope(path)]
        cites = [(path, cite) for path, cite in walk_citations() if in_scope(path)]
        # The instrument is live, on ``test_build_artifacts_ignored.py``'s
        # reasoning: a directory filter that selected nothing, or a directory
        # that stopped citing steps at all, would report a clean run and be
        # indistinguishable from one. ``anchor_scan.py`` is named because it is
        # the module #238 was filed over, and the floors are far under today's.
        self.assertGreater(len(walked), 20, "the tools/ filter selected too little")
        self.assertGreater(len(cites), 10, "no step citation in tools/ was read at all")
        self.assertIn(REPO_ROOT / "tools" / "anchor_scan.py", walked)
        self.assertEqual(
            [
                f"{path.relative_to(REPO_ROOT).as_posix()}:{cite.line} step {cite.number}"
                for path, cite in cites
                if cite.skill is None
            ],
            [],
            "a 'step N' in tools/ names no skill, so nothing checks it survives a "
            "renumbering. Name the skill beside the words -- once per paragraph is enough",
        )

    def test_a_citation_to_a_step_that_does_not_exist_is_caught(self) -> None:
        """#214's renumbering, run backwards. This is the whole evidence for the class.

        Take ``practicum-case-study`` back to the eight steps it had before #214
        and the four surviving ``step 9`` citations come back stale -- in
        ``apa7.md``, ``style.md``, ``voice.md`` and ``tools/docx_write.py``, which
        is four of the five files the ticket names.
        """
        declared = self.declared()
        declared["practicum-case-study"] = declared["practicum-case-study"] - {9}
        stale = stale_citations(declared)
        self.assertGreaterEqual(len(stale), 4)
        for expected in (
            "skills/practicum-case-study/reference/apa7.md",
            "skills/practicum-case-study/reference/style.md",
            "skills/practicum-case-study/reference/voice.md",
            "tools/docx_write.py",
        ):
            with self.subTest(file=expected):
                self.assertTrue(
                    any(line.startswith(expected + ":") for line in stale),
                    f"{expected} cites practicum-case-study step 9 and was not caught",
                )

    def test_no_citation_in_the_tree_is_stale(self) -> None:
        stale = stale_citations(self.declared())
        self.assertEqual(
            stale,
            [],
            "a 'step N' citation points at a step its skill does not declare. "
            "Either the citation or the skill's numbering moved and the other did not",
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


class TheWorkedReadingBehindTheDuplicateArgumentLivesInOnePlace(unittest.TestCase):
    """#244's decision 1, ruled by the clinician 2026-08-19. **Not** a
    per-account detector, and decision 3 declined to make it one.

    #235 deleted seven per-account totals from ``## Current state`` and swept
    that section rather than the file. Two survived under other headings: the
    patient-and-visit pair in *The identity problem*, and a form count in
    *Navigating the portal*. The pair is the harder one because it is the
    **premise of an argument** rather than a standing -- ten more visits than
    patients, fifteen Patient Detail pages all reading ``1 Visit(s)``,
    therefore most of that gap is duplicates already made.

    **The ruling was to abstract and point rather than to qualify in place.**
    The ticket's own comment recommended adopting ``setup-clinical-skills``'s
    sentence -- *"On one account the figures were ..."* -- into the reference,
    which is the honest per-account form. The clinician ruled the other way:
    the reference states the **method** and the **inference** and points at
    ``setup-clinical-skills`` step 6, so the reading survives **as a sentence
    a reader can follow** in exactly one place, the file whose job is
    collecting one account's setup. That keeps #235's ruling intact in the
    file it was ruled about.

    **As a sentence, and not as the figures**, which is a narrowing this
    docstring stated for one commit by not stating it. The two integers are
    also in three notes under ``fixtures/filled-anchor/notes/``, welded into a
    hyphenated clause -- so *survives once* is true of the form and false of
    the numbers, and the paragraph below saying those notes must not be edited
    is what makes the difference matter. The same overclaim was caught in
    ``CLAUDE.md`` by the standards axis of the review and repaired there; it
    survived one level down, in the docstring describing the repair.

    **The needles are read out of ``setup-clinical-skills`` and never typed
    here.** A checker asserting the reference states no portal totals must not
    become a file that states them -- ``phi_scan``'s *no file may exempt
    itself* arriving on a test, which
    ``TheReferenceHoldsNoOneProgramsEnrollment`` above records being caught
    twice already. Reading them from the one file allowed to carry them also
    means the check follows a re-measurement instead of pinning a figure, which
    is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

    **The haystack is one file, and that is a safety property rather than
    tidiness.** Those same two integers are live in three notes under
    ``fixtures/filled-anchor/notes/``, which are day-b run 1 byte for byte
    apart from two redacted site names and are the evidence #73 rests on. A
    tree-wide check would fail in files nobody is allowed to fix -- exactly the
    exposure ``tools/test_corpus_census.py`` documents at ``RETIRED_ANYWHERE``,
    where one of these two figures is named among the bare 5xx literals those
    notes already carry as clinical values. **A ``git grep`` of either figure
    is not a to-do list**, and the verdicts are the finding rather than the
    count: the hits are a preserved run record, the skill that is the pattern
    to copy, and prose that happens to carry the digits. **No count is stated
    here** -- #244's comment put the pair in five files, this change removed
    one of them, and a bare ``582`` was never five to begin with.

    **A green run here is not a swept file**, and the limits are the ones #244
    decision 3 declined to move. A bare integer has no shape, so nothing here
    generalizes to *a per-account figure*; these two are reachable only because
    another file declares them. A restatement in words, or a differently
    phrased form count, escapes every assertion below.
    """

    #: The worked reading, as ``setup-clinical-skills`` step 6 writes it. The
    #: **shape** is typed and the **figures** are not, which is the whole
    #: reason this class can assert their absence without holding them.
    WORKED_READING = re.compile(r"\b(\d+) patients against (\d+) visits\b")

    #: The form count #235's table carried as ``1. FNP: H & P``, as
    #: *Navigating the portal* item 2 used to state it. A floor, and a low
    #: one: it keys on the sentence rather than on the integer, so any
    #: rephrasing that reintroduces a count escapes it.
    COUNTED_POSTBACK = re.compile(r"\ball \d+ in a single postback\b")

    def setUp(self):
        self.reference = read(MEDATRAX)
        self.setup_skill = read(SETUP)

    def spans(self, pattern):
        """The distinct spans ``pattern`` matches in the reference.

        ``TheReferenceHoldsNoOneProgramsEnrollment.assert_reference_is_free_of``
        above exists to justify this shape and is a method on that class; this
        is the same reasoning rather than a second opinion -- the haystack is a
        reference document, so a failure reports **what matched** and never the
        file it matched in.
        """
        return sorted({found.group(0) for found in pattern.finditer(self.reference)})

    #: The residue note #235 left in the reference for #244 to settle, keyed on
    #: the clause that made it a *record* rather than a fix. A floor: a rewrite
    #: that kept the sense in other words escapes it.
    RESIDUE_NOTE = "recorded rather than fixed"

    def test_the_instrument_is_live(self):
        """Every needle below matches something, on
        ``TheReferenceHoldsNoOneProgramsEnrollment.test_the_instrument_is_live``'s
        reasoning and ``test_build_artifacts_ignored.py``'s before it.

        **Two of these three are asserted only in the negative**, and that is
        what makes this method load-bearing rather than ceremonial: the
        sentences they were written against are **deleted by this very
        change**, so nothing else in the suite exercises them again. A typo in
        ``COUNTED_POSTBACK`` or a drifted ``RESIDUE_NOTE`` leaves its test green
        forever and indistinguishable from a rule being kept.

        **Synthetic throughout.** The positive cases are written here rather
        than quoted from the strings this change removed -- a checker asserting
        the reference states no portal totals must not become the file that
        states them, which is the self-exemption the class above records being
        caught twice.
        """
        self.assertTrue(
            self.WORKED_READING.search("the figures were 111 patients against 222 visits"),
            "WORKED_READING matches nothing, so every needle it supplies is empty "
            "and this class passes on a reference that restates both figures",
        )
        self.assertTrue(
            self.COUNTED_POSTBACK.search("clicking Search returns all 7 in a single postback."),
            "COUNTED_POSTBACK matches nothing, so #244 decision 2 is unchecked "
            "and a reinstated per-account count would read as clean",
        )
        self.assertIn(
            self.RESIDUE_NOTE,
            "two of the seven are recorded rather than fixed",
            "RESIDUE_NOTE no longer matches the clause it was written against",
        )
        # The negative half: the behavior sentence #244 replaced the count with
        # must not itself trip the pattern that forbids the count.
        self.assertFalse(
            self.COUNTED_POSTBACK.search(
                "returns the whole matching set in a single postback rather than paging it."
            ),
            "COUNTED_POSTBACK fires on the countless form #244 decision 2 chose, "
            "so the rule refuses its own remedy",
        )

    def test_setup_still_carries_the_worked_reading(self):
        """The instrument-is-live half, and it is load-bearing rather than
        ceremonial: every assertion below takes its needles from this match, so
        a ``setup-clinical-skills`` that stopped stating the figures would turn
        the whole class green while the reference kept them.

        On ``test_build_artifacts_ignored.py``'s ``TheInstrumentIsLive``
        reasoning.
        """
        # ``assertTrue`` rather than ``assertRegex`` throughout this class: the
        # haystacks are two whole documents, and an assertion that prints one on
        # failure is a failure nobody reads. Same reasoning as
        # ``test_setup_collects_what_the_reference_now_defers`` above.
        self.assertTrue(
            self.WORKED_READING.search(self.setup_skill),
            "skills/setup-clinical-skills/SKILL.md no longer states the "
            "patient-against-visit reading, so the reference points at a step "
            "that carries nothing and every assertion in this class is vacuous",
        )

    def test_setup_declares_the_reading_as_one_accounts(self):
        """The pattern the reference was ruled to point at rather than copy.

        A step that stated the pair flat would be the defect relocated, not the
        honest form -- so what makes ``setup-clinical-skills`` the right home is
        the qualifier, not the file name.

        **This is a constraint on a file #244 scoped out, and it is named
        rather than assumed harmless.** That ticket's second comment calls
        ``setup-clinical-skills`` *"the pattern to copy, not a sixth thing to
        fix"*. Pinning its wording is not fixing it, and the reason it is worth
        the reach is that the reference now **points** there: a step that
        dropped the qualifier would turn this file's abstraction into a pointer
        at a second unqualified figure, which is the defect moved rather than
        removed.
        """
        found = self.WORKED_READING.search(self.setup_skill)
        assert found is not None  # the test above is the guard
        opening = self.setup_skill[max(0, found.start() - 120) : found.start()]
        self.assertTrue(
            "On one account" in opening,
            "skills/setup-clinical-skills/SKILL.md states the figures without "
            "declaring them as one account's reading, which is the form "
            "reference/medatrax-fields.md was ruled to point at",
        )

    def test_the_reference_restates_neither_figure(self):
        """#244 decision 1. The figures are read off the file allowed to carry
        them, never typed here -- see the class docstring.

        **The cost is named rather than engineered around**: this reaches a
        bare integer, so an unrelated future number in the reference that
        happened to equal one of them would fail. That is the trade for a check
        that holds no copy of what it forbids.
        """
        found = self.WORKED_READING.search(self.setup_skill)
        assert found is not None  # the instrument-is-live test above is the guard
        restated = sorted(
            {figure for figure in found.groups() if figure in self.reference}
        )
        self.assertEqual(
            restated,
            [],
            "reference/medatrax-fields.md restates one account's portal totals "
            "in a file that opens 'single source of truth for the Medatrax NP "
            "portal'. The method and the inference belong here; the worked "
            "reading belongs in setup-clinical-skills step 6",
        )

    def test_the_reference_keeps_the_argument_it_gave_up_the_figures_for(self):
        """The half a delete would have lost, on #235's
        ``test_the_reference_keeps_the_why_it_gave_up_the_numbers_for``
        reasoning.

        The ticket's own objection to abstracting was that **the numbers are
        the inference** -- the gap, the sampled Patient Detail pages, and the
        conclusion drawn from both. Dropping the figures is the ruling; dropping
        the argument with them is not, and a later tidy that shortened this to a
        bare pointer would do exactly that with nothing to notice.
        """
        for kept in ("1 Visit(s)", "duplicates already made", "studentoverview.aspx"):
            self.assertTrue(
                kept in self.reference,
                f"reference/medatrax-fields.md dropped {kept!r} along with the "
                "figures. #244 abstracted the reading, not the argument it "
                "supports",
            )

    def test_the_reference_points_at_the_worked_reading(self):
        """The cross-file half. A pointer is the whole of decision 1's remedy,
        so an abstraction that points nowhere is worse than the figure it
        replaced: it reads as a split that was made.

        ``EveryCitedStepResolvesToADeclaredStep`` above is what keeps the step
        **number** honest; this only asserts the pointer is there at all.
        """
        opens = self.reference.find("### The identity problem")
        self.assertNotEqual(
            opens,
            -1,
            "reference/medatrax-fields.md has no '### The identity problem' "
            "heading, so #244's abstracted paragraph has no section to sit in",
        )
        section = self.reference[opens:]
        section = section[: section.find("\n#", 1)]
        self.assertTrue(
            "setup-clinical-skills" in section,
            "reference/medatrax-fields.md abstracts the patient-against-visit "
            "reading without naming where the worked one lives",
        )

    def test_the_navigation_example_states_no_per_account_count(self):
        """#244 decision 2, the cheapest of the three.

        The lower panel returning its whole filtered set in one postback rather
        than paging is the behavior worth recording, and any integer carries
        it. The one that was here happened to be one account's form count --
        the ``1. FNP: H & P`` row of the table #235 deleted.
        """
        self.assertEqual(
            self.spans(self.COUNTED_POSTBACK),
            [],
            "reference/medatrax-fields.md states one account's form count as "
            "the worked example of a portal behavior any integer would carry",
        )
        self.assertTrue(
            "single postback" in self.reference,
            "reference/medatrax-fields.md dropped the no-paging behavior along "
            "with the count. #244 decision 2 replaced the integer, not the rule",
        )

    def test_the_residue_note_does_not_outlive_the_residue(self):
        """#235 left a paragraph in the reference naming this residue and
        pointing here, explicitly for #244 to remove or rewrite. Leaving it
        standing after the fix is the stale-cross-reference shape #235 was
        itself filed about.
        """
        self.assertFalse(
            self.RESIDUE_NOTE in self.reference,
            "reference/medatrax-fields.md still says the residue is recorded "
            "rather than fixed, after #244 fixed it",
        )


if __name__ == "__main__":
    unittest.main()
