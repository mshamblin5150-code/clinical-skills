# The reply word bar is the clinician's house floor and a stated ceiling is never honored

[#725](https://github.com/mshamblin5150-code/clinical-skills/issues/725) was filed after a live run
against the NUR_5042 M3 board on 2026-08-31. `skills/discussion-reply/SKILL.md` required at least
100 words; the board's own prompt asked for a reply *"consisting of 50-100 words."* The two bars
overlap at one value, and both replies on that run were written to the ceiling before the clinician
said, mid-run, *"I never apply the ceiling... in general all of my replies are far longer."*

**One reply was posted at that compressed length. The other was rewritten at full length once he
said so, and the full-length version caught two defects the compressed one had papered over** — the
word `narcotic` was missing from a reply whose entire legal argument turns on it, and a board power
was asserted without the complaint-process qualifier its source attaches. That is the finding the
ticket exists to record: a word ceiling applied to evidence-bearing prose does not remove
adjectives, it removes the clauses that bound a claim, because those are the clauses that read as
optional.

Grilled 2026-09-01. **Eight decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `02b4068`

Freshness gate `FRESH` at both checkpoints. The base moved mid-session and every anchor below was
re-derived after the merge rather than carried across it.

**The sibling skill had already ruled the ceiling, in the weaker form.**
`skills/discussion-post/SKILL.md:109-110` reads *"The word floor is graded. The ceiling is counted
and never graded: the clinician deliberately exceeds stated maxima."* Neither discussion skill
contains the word `trim` anywhere, so no rule anywhere said what to do instead of trimming.

**The glossary already said the number that caused the trim was not a bar.** `CONTEXT.md` defines
**Prompt** as *"The board's own statement of what one initial post must answer. It supplies that
discussion's shape and does not necessarily supply its bar"*, and **Bar** as *"The stated minimum a
graded contribution must meet... Written on the course syllabus rather than on the board."* The
`50-100` came off the board prompt.

**Both halves of that Bar entry are wrong against the tree.** `discussion_post_scan` parses a
`WORD-CEILING` field out of `bar.md`, so a bar is not only a minimum; and the M3 prompt stated a
range, so a bar is not only on the syllabus.

**The figure has four homes, and two tracker sweeps counted three.**
`skills/discussion-reply/SKILL.md:12` and `:218`, `tools/discussion_reply_scan.py:66` in the row
text, and **`tools/discussion_reply_scan.py:268` as a bare `if count < 100:` with no named
constant.** Both sweeps recorded the fourth as *enforcement* rather than as a home.

**The counting method moves the number by tens of words, and this session got it wrong first.** An
initial count of the corpus used the wrong reference-label pattern and counted reference lists as
body words, returning figures around sixty words high. The enforced method is
`strip_discussion_markers` over the body `read_reference_section` returns — reference list out,
invisible working markers out.

**By that enforced method, the reply corpus is five files:**

| | |
| --- | --- |
| enforced word counts | `109  253  287  291  642` |
| the `109` | is the reply the ticket names as trimmed |
| refused by today's floor of 100 | **0 of 5** |
| refused by any floor from 110 to 253 | **1 of 5** — that one |
| plateau width | **144**, midpoint 181 |

**The initial-post figures on disk understate the range.** Two records hold 793 and 844 words; the
clinician states his initial posts sometimes exceed 2,000. The two measured values are a floor on
the range and not the range, and no ruling here rests on them.

**`AGENTS.md:29-35` classes `discussion-reply` as depending on its grader while requiring the same
checks be walkable by eye from step 4.** So `SKILL.md:218` is a by-eye walk surface rather than a
redundant copy of the figure.

**The shared test fixture is three words under the new floor.** `test_discussion_reply_scan.BODY`,
imported by `test_discussion_post_skill.py`, measures 147 enforced words.

## Ruled 2026-09-01

### 1. The floor is the clinician's, not the course's

It is board-independent. A board stating a lower minimum does not lower it, and a board stating a
higher one is a separate question this record does not reach.

**Reading it off the board was refused.** The initial-post skill does read its bar off the syllabus,
transcribes it into `bar.md` and has the clinician sign it — and that machinery is the weight this
skill deliberately does not carry. More decisively, the corpus shows the figure has never bound his
writing: adopting a course's lower number would install a bar beneath every reply he has written, on
the authority of a board. That is the trim's own failure with the sign flipped.

### 2. The floor is 150

**Not invented, and not a raise against his writing.** Every value from 110 to 253 refuses exactly
one reply of five, and that reply is the compressed one this ticket is about — so the corpus offers
a 144-wide plateau where the answer does not move.
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s precedent is met: the cut
point is grounded where the corpus offers one.

**Set toward the low edge of the plateau rather than at its midpoint**, which departs from
`SPACE_ADVANCE_FRACTION`'s midpoint rule deliberately. That constant's two directions cost the same;
a floor's do not. Too high refuses writing the clinician would stand behind, too low lets a thin
reply through, so a floor belongs near the bottom of its plateau and the midpoint of 181 is a worse
answer than 150.

**It converts the ticket's defect from invisible to refused.** The trimmed reply scored 109 and
cleared the floor of 100, so no gate in the repository saw it. Under 150 it is a finding.

**The evidence ceiling is stated rather than implied.** The population is five, of which the shortest
is the known defect; on the remaining four the minimum is 253, so 150 is conservative against every
sample the clinician would defend. Any later re-derivation should re-measure the plateau rather than
inherit the number.

### 3. No stated maximum is honored, and the remedy is named

The header carries a prohibition with a remedy rather than a permission:

> No stated maximum is honored. Never trim a drafted reply to fit a word ceiling: the clauses a
> ceiling removes first are the ones that bound a claim, because those are the clauses that read as
> optional. Where a reply genuinely runs long, cut a whole point rather than the qualifiers on a
> point you are keeping.

**The permission form was refused.** The run's failure was not that it honored a ceiling — it was
*how* it shortened: it kept every claim and shaved words off each one, which is exactly how a legal
argument lost the word its case turned on. A rule that only says the ceiling is unscored says
nothing to the next run with some other reason to shorten. **The second sentence is the half that
holds when no ceiling is in play at all.**

### 4. The same rule lands on `discussion-post`

`skills/discussion-post/SKILL.md` gains the same sentence beside `:109`, and one test binds the two
copies so neither can be edited alone.

**The initial post is the worse exposure, not the equal one.** It is the longer artifact, so there is
more qualifier to lose; and its ceiling is not a number glimpsed on a board but one the run
**transcribes into `bar.md` and the clinician signs**, which is a far stronger pull toward writing to
it. *Counted and never graded* tells that run the ceiling is unscored; it does not tell it not to
write to it.

**Leaving it unfixed was refused** on [#271](https://github.com/mshamblin5150-code/clinical-skills/issues/271)'s
precedent inverted: there a second site carrying an identical defect was deliberately left and filed,
because fixing it exceeded the ruling. Here the ruling is about the mechanism rather than about one
skill, so the second site is inside it.

### 5. A stated maximum below the house floor is surfaced once, before drafting

Where step 1 reads a stated maximum below 150, the run tells the clinician the number and that it is
writing past it, then drafts. No approval gate; one line, and only on boards that state a low
maximum.

**Silence was refused because the clinician takes the grade and the run does not.** A stated maximum
is a thing faculty wrote down, and a run knowingly writing past it is a decision with a cost that
lands on a person — who may want to answer it in the post, raise it with the instructor, or on one
board decide it is not worth the fight. Deciding a length question about his graded work without
telling him is the trim's own posture.

**The cost is named:** it puts a length number in front of him at the moment this record says length
is not the target. That is accepted, because the alternative hides a conflict rather than resolving
it.

### 6. Raising the floor was reopened and the ticket's option 1 is adopted

The ticket offered raise, declare, or say nothing, and this record takes **raise and declare
together** — which is [#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275)'s
shape: declare the limit being kept, and fix the thing actually named.

**The session's own first reading of #97 was wrong and is recorded as wrong.** It concluded *refuse*
from the spread of the corpus without measuring the plateau. The corpus did offer a cut point; only
the measurement showed it.

### 7. One owner, three bound restatements, and the method is stated

`discussion_reply_scan.WORD_FLOOR_COUNT` owns the figure. The row text and the enforcement derive
from it, and a test in `tools/test_discussion_post_skill.py` — which already reads both skill files —
asserts `skills/discussion-reply/SKILL.md:12` and `:218` carry the constant's value.

**De-citing the step 4 copy was refused**, which reverses this session's own first plan. `AGENTS.md`
requires that step's checks be walkable by eye, so the number is load-bearing where it stands; and
`:12` is read by the drafting context, which never reaches step 4. Both restatements have a distinct
reader.

**Step 4 also states what is counted** — the reference list and the invisible working markers are
excluded. A by-eye walk that counts the reference list disagrees with the grader by tens of words,
which this session demonstrated on itself.

### 8. The initial post gets no house floor

Its floor stays the signed `bar.md` value. A house floor of 150 is inert against an artifact written
at 793 to 2,000-plus words, and it would duplicate a mechanism that already exists and already works.

**So `House floor` has a population of one.** The term is worth its entry anyway, because the
distinction it carries — the clinician's own minimum against a course's stated one — is the whole
subject of this record, and collapsing the two into one word is what let a run read `50-100` off a
prompt and treat it as binding.

## What this does not reach

**Whether a reply that clears the floor says anything.** Every ruling here is about length, and
length is a proxy the record itself says is not the target. A fluent 200-word reply that answers
nothing passes the row. `specificity_scan.py`'s R2 limit, inherited by every substance test in this
repository.

**A board stating a minimum *above* 150.** Ruling 1 settles that a lower stated minimum does not
lower the house floor and is deliberately silent on the other direction; no board in evidence states
one, so no rule is written for it.

**Whether the surfaced notice in ruling 5 is acted on.** It is a line printed before drafting, with
no gate behind it, so a run that prints it and drafts on is indistinguishable from one the clinician
read and waved through.

**Whether 150 survives a larger corpus.** The plateau is measured over five replies, one of which is
the defect. The number should be re-derived rather than inherited once the corpus reaches double
digits, and the plateau is the thing to re-measure — not the number.

**The counting method's edges.** The enforced count excludes the reference list and the working
markers and includes everything else, so a reply padded with block quotations or a long signature
clears the floor on words the clinician did not write.

**Whether the trim happened for the reason recorded.** The prompt stated `50-100` and the skill's
first word about length was `short`, and both are removed here. Neither is proven to be the cause;
they are the two instructions a run would have read.
