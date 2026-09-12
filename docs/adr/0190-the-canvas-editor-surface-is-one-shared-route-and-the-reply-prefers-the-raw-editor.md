# The canvas editor surface is one shared route and the reply prefers the raw editor

[#948](https://github.com/mshamblin5150-code/clinical-skills/issues/948) was split out of
[#817](https://github.com/mshamblin5150-code/clinical-skills/issues/817) on 2026-09-07 by
[ADR 0147](0147-the-post-loads-as-html-through-the-raw-editor-and-the-submit-gate-moves-to-the-rendered-box.md)
ruling 9, which moved `discussion-post` onto Canvas's raw HTML editor, declined to carry
`discussion-reply` with it, and filed *"does the reply box expose a raw editor at all?"* as that
ticket's first item. Nothing in this repository has answered it in the five days since.

Grilled 2026-09-12 to an empty frontier. **Nine rulings, by the clinician, on that date.** Two of
the eight questions put to him turned out to be measurements rather than decisions, and both were
taken live and read-only during the session. Nothing is built here; this is the record the build
reads.

## Measured before ruling, at `084152c3` and re-derived at `81b96373`

Freshness gate `FRESH` at `084152c3` before any ticket was read. It reported `STALE` at the session
tail; `main` had gained ADR 0188 and a Python-floor module across 75 files. The branch was merged
forward and every citation and every command result below was re-derived at `81b96373` before
anything was written. Two line numbers moved by one and are recorded at their current values; no
measurement moved.

### The composers, measured live and read-only

Bluefield **NUR 5144 M2 Discussion**, `/courses/9232/discussion_topics/123776`, 2026-09-12 —
deliberately the same board the ambiguous 2026-09-08 calibration entry names. Nothing was typed,
both composers were cancelled, the tab was closed. No board write and no publication, on ADR 0147
ruling 8's terms.

Two composers sit on one page and Canvas labels both of them *Reply*:

| | topic-level composer | threaded reply composer |
| --- | --- | --- |
| opened by | `Reply` at topic level | `Reply to post from <name>` beneath an entry |
| TinyMCE editor id | `message-body-root` | `message-body-499382` |
| raw-HTML toggle | `data-btn-id="rce-edit-btn"`, title *"Click or shift-click for the html editor."* | present, identical |
| content interface | `setContent`, `getContent`, `insertContent` | the same, plus `getBody` |

**The toggle was exercised rather than inferred from the control's presence.** Toggled on the
threaded composer, the rich toolbar disappears and what is exposed is a plain visible
`<textarea id="message-body-499382">` with **zero CodeMirror instances**, offering *"Switch to pretty
HTML Editor"*. That is Canvas's **raw** editor, the plain textarea, and not its pretty one.

**So the answer to #948's first item is yes**, and the discriminator the session went looking for is
the editor id: `message-body-root` is the topic-level composer and a **numeric** suffix is a threaded
one. *That the number is the entry's own id is an inference and was not checked; the discriminator
does not rest on it.*

**This retires the ambiguity rather than resolving it in either direction.** The 2026-09-08 entry in
`skills/discussion-post/reference/canvas-paste-calibration.json` records
`"observed_in": ["reply box before submission"]` on this same board. Both composers carry the toggle,
so that reading is **true of either surface** — it was never wrong, and no amount of re-reading it
could have separated them. The schema had no field that could.

### The ampersand, measured read-only on already-posted entries

[#991](https://github.com/mshamblin5150-code/clinical-skills/issues/991) measured Canvas's
**submission comment box** double-escaping a literal `&`, and its option 3 said the board box *"needs
measuring first, since it may share the defect"*. #991 had to post in order to measure, because no
posted comment carrying an ampersand existed. On a board they already existed and nobody had looked.

Two NUR 5042 boards, every posted entry read through Canvas's own view API and then rendered and read
back as text — #991's instrument:

| board | entries | with an `&` | stored `&amp;` | stored `&amp;amp;` | renders as `&` | renders as `&amp;` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M3, `123723` | 35 | 27 | 45 | **0** | 45 | **0** |
| M2, `123724` | 33 | 17 | 36 | **0** | 34 | **0** |

81 ampersands, **zero double-escaped and zero reaching a reader as a visible `&amp;`**. The M2 row
reconciles exactly: 34 render in text and the remaining 2 sit inside `href` attribute values, which
`innerText` does not surface. #991's box returned three literal `&amp;` and zero real ampersands, so
the two surfaces behave oppositely.

**The limit is declared rather than left to be found.** This covers the routes that actually produced
those 68 entries, which is typing and pasting by many people over a term. **Both boards predate
#817**, so no entry here is known to have arrived through the raw editor, and this does not establish
that a raw-editor load specifically survives. What it establishes is that the box does not
double-escape, which is the thing #991 said it needed.

### The label spellings, driven rather than read

```
'**References**' <p><strong>References</strong></p>
'## References'  <p><strong>References</strong></p>
'References'     <p>References</p>
'*References*'   <p><em>References</em></p>
```

`post_html.render` produces **byte-identical output** for the two bolded spellings. It writes `&` as
a single-escaped `&amp;`, which is exactly what all 81 board ampersands store and what renders as a
real `&`.

### What the reply path was doing, and the hole in it

`skills/discussion-reply/SKILL.md:258-272`. The reply builds its HTML with `tools/post_html.py` and
loads it *"through the editor's own content interface"*. **That phrase appears four times in this
repository and is defined in none of them** — `:267`, `:270`, ADR 0050 `:343`, ADR 0036 `:37`. No
control, no property, no tool. Compare `skills/discussion-post/SKILL.md:348` and `:361`, which name
the toggle and the switch exactly. Two consequences: the injection route is invented fresh each
sitting, and the skill's own fallback — *"If the editor exposes no content interface"* — cannot be
evaluated, because nothing says what would count as one.

And the sequence has no reader in it that is not the author. The single gate at `:257` fires
**before** the build at `:261` and before the load at `:267`; the only post-load check is the
authoring agent reading its own work at `:268`.

**That is not a hypothetical.**
[#1039](https://github.com/mshamblin5150-code/clinical-skills/issues/1039) records a reply posted on
2026-09-10 whose first reference URL reached the board as plain text, *"A posted Canvas entry cannot
be edited, so that reply stays as posted"* — and, decisively, *"The posted-reading record for the
reply recorded the one linked URL as a harmless rendering difference."* The path's only post-load
check looked straight at the defect and wrote it off.

## Ruling 1 — the measurement names the load route, not only the toggle

#948's first item was scoped on 2026-09-07, when the answer to *how does the reply get into the box*
was *the agent types it* — fully specified, nothing to name. That stopped being true on 2026-09-10
and the measurement's scope was never revisited. It widens: the same sitting records whether the
toggle exists, **what mechanism the load actually uses**, named concretely enough that the next agent
performs the same act rather than inventing one, and what would count as *no content interface* for
the fallback clause.

**The record gains a field that names the surface.** The 2026-09-08 entry gets one too, marked as the
unresolved reading it is rather than silently re-read as either composer.

## Ruling 2 — the reply keeps one gate and the readback becomes a graded comparison

ADR 0147 ruling 6 exempted this skill on a premise its own document contradicts four pages later:
*"A reply is short and typed."* It is no longer typed, and the exemption was never amended.

**No second clinician gate.** Instead, before submit the agent writes the editor's serialized HTML
into the run directory, and `discussion_reply_scan` gains a row comparing it against the built
`.html`: same paragraph text, same anchors, same count. **A non-clean comparison stops and returns to
the clinician**; the agent never re-routes or retries on its own, which is ADR 0147 ruling 6's *"The
agent never adjudicates its own paste"* transferring unchanged.

**Why a grader answers ADR 0147's ground where a second reader would not.** That ruling reached for a
human because *"every record in this pipeline is agent-written and self-attesting"*, and the only
alternative it weighed was **another agent-written record**. A grader comparing two files is neither:
it is code, it cannot write itself a pass, and #1039 is precisely the defect it catches — one anchor
present and one absent in a two-entry list.

The maximal answer — the post's two gates, with captures and a told-loaded-and-unsubmitted
disclosure — was put to the clinician with its argument stated fairly and declined, on the ground
that its cost lands on him rather than on the tree, twice per reply and four times per board, for an
artifact whose exemption rests on being short. **The residue is named in *What none of this
reaches*.**

## Ruling 3 — the route is toggle, then content interface, then typing

Chosen **before** the load, declared to the clinician at the single gate that already exists with
what it costs, and **never switched after a bad comparison** — ADR 0147 ruling 7's shape, which
already governs the sibling skill.

The rung that was hypothetical is real and it is the plain-textarea kind, so it carries no parser and
nothing live between the bytes and the box. The content interface stays as rung 2 and is now
nameable. **It is the only one of the three that needs a documented workaround to function** — the
editor does not register the change without a keystroke, and that keystroke autolinks the token in
front of it, which `:269-270` steers around by rule. #1039's surviving board entry is that
workaround's recorded cost.

**Three rungs is not the third rung ADR 0147 ruling 7 refused.** That refusal was aimed at the Word
paste, which produces a *visibly wrong* post. All three of these produce a correct one.

**The route is confirmed by reading which editor you landed in, never by having clicked the toggle.**
Canvas has two HTML editors — raw, a textarea, and pretty, a CodeMirror that reformats markup — and
it remembers the last-used mode per user. A plain click landed in **raw** on this account on this
date, and that is a fact about this account rather than about Canvas. The status bar states it: it
offers *"Switch to pretty HTML Editor"* when you are in raw. **`discussion-post` carries the same
unguarded assumption at `skills/discussion-post/SKILL.md:361` and is corrected in this record's
diff**, on ADR 0147 ruling 9's own precedent of fixing a false line in the file it was already
editing.

## Ruling 4 — the rule lives in one shared reference sheet

`skills/_shared/reference/canvas-editor.md`, beside `apa7.md`, `style.md`, `voice.md` and
`sourcing.md`.

The thing measured here is a property of **Canvas's rich content editor**, not of a reply box, and
five skills load authored bytes into it: `discussion-post`, `discussion-reply`, `peer-critique`, and
— the clinician's own widening on 2026-09-12, *"in some instances course-assignment as well but not
always"* and *"practicum-case-study similarly"* — those two, conditionally. A ruling scoped to
`discussion-reply` would be wrong about its own subject, and five copies of one rule is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) with nothing between them.

The sheet owns the surface: the two composers and the `message-body-root` versus numeric-suffix
discriminator, this record's route order, the raw-versus-pretty confirmation, and the readback. Each
skill points at it and states **only its own trigger**. The calibration record from ruling 1 belongs
beside the sheet rather than inside `skills/discussion-post/reference/`, where the 2026-09-08 entry
was mis-read for four days.

**What the sheet deliberately does not own:** whether a given assignment goes into a box at all. That
is a per-skill judgment with its own evidence. The sheet owns **how bytes reach a Canvas editor and
how you confirm they landed**; each skill owns **whether this submission uses one**.

## Ruling 5 — a skill reads its submission type mechanically and declares the selected route

`practicum-case-study` renders a `.docx` at step 8 and treats it as the deliverable, with no step
anywhere that reads how the assignment is submitted. In NUR 5144 the case study **is** a Canvas
discussion topic — five of them at 80 points, 400 of the course's 1000 — so the skill's silence is
wrong for 400 points and has been repaired by hand each sitting.

The submission type is read off the LMS before rendering and **the read selects the route**. The
selected route is declared at the approval gate the skill already has, **not as a new gate** — ADR
0147 ruling 7's sentence with *submission type* in place of *toggle control*: *"That is not a new
gate; gate 1 already exists, and this is information the clinician needs in order to give it."*
Asking every sitting buys nothing the declaration does not already buy.

**What follows the selection on the box branch is not ruled here** and is filed instead. The
clinician's own record has Module 2 refused by Canvas at 73,029 bytes and Module 3 accepted at
52,824, so the inline attempt can fail on size and the attachment fallback carries its own
verification. That belongs to `practicum-case-study`, with its own measurements, and not to a ticket
about a reply box.

## Ruling 6 — the reply gains no `output/` artifact

The built HTML stays in `scratch/runs/<run-key>/` beside the serialized-editor readback that ruling 2
grades against it.

`CONTEXT.md` already answers it. **Submission** is *"the document a course marks"*, and the **Posted
reading** entry says that *"a reply has no submission, so the posted reading is the only account of
what will be marked."* What a course marks for a reply is the board entry; the HTML is the vehicle
that carries it there. `skills/discussion-post/SKILL.md:57` states the partition — *"`output/` holds
the submission and its renders; provenance stays in the run directory."*

`peer-critique` is the control and it agrees: a board-only graded artifact, referencing `output/`
**zero times**. The three skills that do write there each produce a file that exists independently of
a board.

**And the post's own `output/` directory is a vestige of the bottleneck the reply never had.** Before
#817 the post was written there because the clinician went and collected it and pasted it. #817
removed the human paste and the directory stayed. ADR 0050 established that the agent posts the
reply, so there is no handover for a handover directory to serve. Adopting it would be copying a
shape rather than a reason, which #948's own *What must not come out of this* forbids.

## Ruling 7 — the ampersand measurement discharges the pointer and unblocks #991 without ruling it

`skills/peer-critique/SKILL.md:266` — *"Whether the board's reply box shares the defect is unmeasured,
which is #948's open question"* — is false as of 2026-09-12 and is corrected to state the
measurement. The observation goes into ruling 4's calibration record, and the figures and the
raw-editor limit are handed to #991.

**This does not rule #991.** Its option 3 is *"never put a reference list in this box; put it on the
board"*, and whether the peer critique's substantive body moves to the board is a decision about that
artifact's shape, for the clinician, on that ticket. All that changes is that the *needs measuring
first* condition it was sitting behind is spent.

**The fork this ticket was carrying is gone rather than answered.** Its 2026-09-10 sweep framed the
choice as *either #948 widens to own a posted-and-read measurement, or the skill's pointer moves to
#991*. Neither branch was needed, because the evidence was already on the board.

## Ruling 8 — ADR 0036's ground is corrected in place and no pattern moves

[ADR 0036](0036-a-references-label-is-a-per-pipeline-source-spelling-for-one-rendered-outcome.md)
ruling 1 states a rule — *"a grader's accepted set is exactly the set that renders bold on its own
pipeline"* — and justifies the reply's spelling with *"Nothing renders a reply, so the artifact's
spelling is the board's spelling."* That ground is dead, and the 2026-09-10 correction recorded the
new outcome while leaving the reasoning standing.

**Applied to today's tree the rule gives a different answer than the ruling it justified**:
`## References` renders bold on the reply's pipeline now, byte-identically, and
`discussion_reply_scan` rejects it.

**No pattern moves.** The rejection has an independent ground that ADR 0036 could not have stated
because it predates the renderer: `skills/discussion-reply/SKILL.md:204` says **"Do not add a
heading."** `## References` is a heading in the source whatever it renders as, so the grader is
enforcing the no-heading instruction rather than a rendering fact. **That is the ground the
correction records.**

Two things stay straight in the doing. Ruling 1's refusal of *"accept both"* rests on *"blessing
plain forever blesses the one form that arrives unbolded"* — that is about **plain** `References`,
which the run above confirms still arrives unbolded, so the refusal survives untouched and does not
reach `## References`. And ruling 2 already handles the case legibly: recognizer matches, accepted
pattern does not, exit 2, dependent rows `not graded`, stderr naming the line. Nothing is silent.

Leaving it alone is the option that costs something: the next session applies ruling 1's stated rule,
gets the widened grader, and either builds it or files a defect against the tree.

## Ruling 9 — `CONTEXT.md` gains two terms, `Composer` and `Load route`

**`Composer`** is the term this ticket cost four days for the want of. Canvas labels both of its
editors *Reply*, the repository inherited that ambiguity in the phrase *reply box*, and the one
measurement in the tree that used it is readable as either surface. The term is filed in
`### Coursework` immediately after **Reply**, on
[ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)'s rule that a term is filed
with the term it is defined against: a composer is defined by which contribution it composes.

**`Load route`** names what ruling 3 orders. It is the mechanism that carries a finished contribution
into a composer, and it is distinct from the **Submission** it carries and from the **Posted
reading** taken afterwards.

Both carry `_Avoid_` rows, and `reply box` is on the first one's, because that is the spelling the
term exists to retire.

## Alternatives refused

- **Taking #948's measurement as scoped in September.** It answers a question asked before the route
  changed underneath it and would leave a live skill's fallback branch untestable.
- **A second clinician gate on the reply.** Put fairly and declined; see ruling 2 and the residue
  below.
- **Content interface as the primary route.** It is the only rung needing a workaround to function,
  and that workaround has a posted, unrepairable artifact behind it.
- **Widening the reply grader to accept `## References`.** What the rule literally demands and still
  wrong, because the reply forbids headings.
- **An `output/` artifact for the reply.** Copying the post's shape without the post's reason.
- **Moving `peer-critique`'s pointer to #991.** Proposed by this ticket's own sweep and now
  unnecessary — the question is measured, not reassigned.

## What none of this reaches

- **Whether a raw-editor load survives the board's ampersand handling.** Both measured boards predate
  #817. The box does not double-escape on the routes that produced those 68 entries; a raw-editor
  load specifically is unmeasured.
- **Whether the reply is right.** Ruling 2 buys a mechanical comparison of what was loaded against
  what was built. **It is not a checked reply, and a clean comparison establishes nothing about
  substance, voice or the board.** ADR 0050's *"Do not read a clean `reread.md` as a checked post"*
  applies unchanged.
- **The residue ruling 2 accepted.** No human who is not the author sees the loaded box before
  submit. A defect the comparison cannot express — a correct artifact loaded into the wrong entry's
  composer, or a rendering fault visible only on the page — reaches the board and is caught only by
  the posted reading, after submission, when nothing on the LMS is edited.
- **Whether a given assignment uses a Canvas box.** Ruling 5 requires the read; it does not settle
  what happens when the inline attempt is refused for size.
- **Any of #991's decision.** Ruling 7 spends a precondition and rules nothing about where a
  reference list belongs.
- **That the composer discriminator is stable.** It is one institution, one Canvas instance, one
  theme, one date — the disclosure ADR 0013 made about itself, unchanged.
