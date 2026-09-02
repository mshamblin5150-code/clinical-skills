# The course assignment produces no artifact in tree and its bar signs the container rules and source classes per run

[#821](https://github.com/mshamblin5150-code/clinical-skills/issues/821) was filed over
NUR 5042 Module 5's 250-point PowerPoint business plan, due 2026-09-27, with four
decisions declared open: the assignment's inverted font rule, whether a `.pptx` writer
belongs in `tools/`, where image generation lives, and whether costed figures get a
ledger.

Grilled 2026-09-02. **Ten decisions, ruled by the clinician on that date.** Nothing is
built here; this is the record the build reads.

## Measured before ruling

Freshness gate `FRESH` at both checkpoints. The branch was brought forward from
`a5aec24` to `92a429d` mid-session when the gate reported `STALE`, and every claim below
was taken or re-taken against the merged tree.

**Four facts read live from the assignment page**, `/courses/9229/assignments/348713`,
on 2026-09-02:

| read | result |
| --- | --- |
| the linked example `NP_Health_Office_Business_Plan.docx` | **Access Denied** |
| rubric controls and rubric DOM nodes | **zero of each** |
| any APA, reference or citation requirement | **none stated anywhere** |
| the 10 20 30 and 6x6 block | **verbatim as the ticket quoted it** |

The example's `href` is `/courses/6641/files/4343728/download?download_frd=1` — a course
the clinician is not enrolled in. The ticket asked for this to be established early
rather than on the 27th; it is established, and the answer is that the input does not
exist. The rubric absence means the 250 points have no published breakdown, so every bar
element comes from the prompt's own prose.

**PowerPoint 16.0 is installed and COM-reachable** on the maintainer's machine, checked
rather than assumed, which is what makes ruling 9 cheap.

**The ticket's own container claim is false.** It states that *"Six words cannot carry a
costed line item."* A costed line item is a label and a number, which is what six words
is good at — `Build-out: $47,000 for 2,400 sq ft` is exactly six. What does not fit in
the deck's 360-word ceiling is the narrative: the market analysis, the justification, and
the reason a number is that number. That correction is what moved ruling 6 from *the
container is impossible* to *the container is tight and the narrative goes in the notes*.

**The site archive is mostly generated imagery and nothing in it says so.** Measured
2026-09-02 against `C:\Archives\DATA\Axion`, which is outside this repository, so
**nothing committed re-derives these figures and they are stated once, here**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. Of 21
files in `24k building mockups`, **19 carry a UUID filename at exactly 1024x1024,
1024x1536 or 1536x1024** — canonical image-model output dimensions. **Two are 1024x768
JPEGs with realtor-listing hash names and stripped EXIF**, and those are the genuine
photographs of the actual building. `Front_Dimensions.png` and `Back_Dimensions.png`,
which the ticket calls *"exterior dimension studies"*, are 1024x1536 and are generated
too. The `Conceptual Interiors` directory the ticket cites as site material is
`bridge 1-4`, `observation lounge` and `ready room` — Star Trek sets from an unrelated
project, not clinic interiors.

**The claim ledger already carries the dollar row and lacks only the source.**
`research_ledger.NUMERIC_CLAIM_UNQUANTIFIED` already forces a numeric claim to be restated
with a number. `SOURCE_CLASSES` is four members, every one of them clinical-literature
shaped, and a commercial lease listing or a vendor quote is none of them.
`ORDINARY_WINDOW_YEARS` is 5. `tools/test_reference_scan.py` asserts
`reference_scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`'s keys are exactly
`research_ledger.SOURCE_CLASSES`, so a fifth class fires that tripwire — which is the
mechanism working rather than a cost.

**The dependency gate is open.** `scratch/runs/nur5042-m5-discussion/bar.md` is signed
2026-09-02 and its `posts/` directory is empty. The gap statement the plan must site and
cost does not exist, and its post is due 2026-09-10.

## Ruled 2026-09-02

**1. The artifact is produced agent-side and this repository only grades it.** The model
authoring the run generates the `.pptx`, and generates or fetches its images. No `.pptx`
writer is built in `tools/`, on stdlib or on a library. The asymmetry is the reason:
writing a `.pptx` PowerPoint will open is hard and fails invisibly until somebody opens
the file, while reading one is a zip and a namespace lookup. The graders take the easy
direction of that asymmetry.

**2. The skill is `course-assignment` — a general spine with artifact-specific graders.**
The spine is `discussion-post`'s and is not deck-shaped: read the page live, transcribe
verbatim, sign `bar.md`, record precedence notes, research against a ledger, produce,
grade, render, submit. `ARTIFACT` selects the grader. **`deck` is the only value accepted
on day one**, declared as the only value, exiting 2 on anything else; a second member is
argued for in a diff when a second assignment arrives. This is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s discipline
applied in advance: a dispatcher built for four artifact types nobody has read is a
generalization made from the files the pass had open.

**3. Three passes, three distinct subjects, orchestrated by the agent running the skill.**
Research produces records. Refutation attacks records that exist, unchanged from
[#231](https://github.com/mshamblin5150-code/clinical-skills/issues/231). **The
adversarial pass attacks the artifact for records that do not exist** — it reads the
finished deck as the investor the assignment names and returns unbacked assertions keyed
to slide number. That third subject is
[#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289) generalized: a
refuter is handed a record and asks whether it holds, so a figure never entered in the
ledger is invisible to every row, and `research_ledger.py` says in as many words that it
has no expected count of its own. **Each pass can fail while the other two pass.**

**4. `docx` and APA are capabilities the deck run draws on, not artifact types.**
`ARTIFACT: paper` is held back. `practicum-case-study` already is the paper pipeline, and
shipping a second thinner paper grader beside a mature one puts the ownership of those
rows in question. The seam gets argued when a non-case-study paper assignment lands.

**5. `FONT-DIRECTION: ceiling`, `FONT-POINTS: 30`, and the deck is produced at 28pt.** The
page renders Kawasaki's third element backwards — his rule sets 30 points as a floor and
the page writes *"lower than 30 points in size"* — in the same sentence-block that says
*"PuppowerPoint."* The professor grades the deck and the professor wrote the page, so the
page wins. The two readings are `>=30` and `<30` and the practical gap is two points: a
28pt deck is visually indistinguishable from a Kawasaki-compliant one and fails no stated
rule, while a 32pt deck fails the page as literally written. **One reading costs nothing
if it is wrong and the other costs a stated rule.** That is the reverse of
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect rather
than a repeat of it.

**6. Speaker notes are outside 6x6 and inside the claim rows.** Two rows over two
populations: the container rows read the slide face alone, `ppt/slides/`; the claim rows
read the slide face **and** `ppt/notesSlides/`. 6x6 is a legibility rule and notes are
never projected, so exempting them costs nothing. The claim rows are a truth rule, and a
fabricated figure in a speaker note is one the clinician will say out loud to a room he is
asking for money — strictly worse than one on a slide, because nobody reads it in advance.
Exempting notes from both would leave a hole exactly the size of the narrative, which is
where every unsourced justification naturally goes once the slide face has no room.

**7. The image rule is a caption convention and its hole is a declared limit.** A
generated image may appear anywhere in the deck **except standing in for the actual
site**. A generated image of a space carries a visible caption naming it conceptual. The
site slide takes one of the two listing photographs, or one the agent fetches. Ruled
against the ledger option: the deck carries roughly five images, and a provenance record
would be the author's own word about the author's own file with nothing able to check it —
a gate that exists to look like a gate. **`image-provenance-unverified` is declared day
one**: nothing in the file distinguishes a photograph from a generated image, no
mechanical row catches a generated site image, and the rule rests on the adversarial pass
and on the clinician not preferring the prettier picture.

**8. `research_ledger.py` is widened, and the permitted source classes move into the
bar.** A dollar and a clinical fact are the same kind of claim with different sources —
both need a source, a restatement and a hostile second read, and the refutation pass is
identical in shape — so a second ledger would be a second copy of that mechanism with
nothing failing when the copies drift. **`SOURCE-CLASSES` and `RECENCY-WINDOW-YEARS`
become signed `bar.md` fields** rather than global constants, because widening a shared
vocabulary for one skill otherwise loosens it for the other: `practicum-case-study` signs
its four classes and a five-year window, and a deck signs five classes and a one- or
two-year window. A commercial listing must not become sourceable for a clinical claim.

**9. The render pass ships day one as `deck_render.py`, on
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
unchanged.** One page-faithful export plus one PNG per slide into `render/pass-N/`, only
the last pass graded for completeness, clinician-supplied export as the escalation. The
XML cannot see what a slide looks like, and ruling 5 creates the specific defect it cannot
see: **28pt body text in a placeholder laid out for 18pt overflows or autofits, while
passing every container row** — six bullets, six words each, correct size. That is
[ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md)'s
recorded defect in a deck. It is also what makes ruling 3 possible at all: the adversarial
agent cannot read a `.pptx`, it reads slide images. `Presentation.ExportAsFixedFormat` is
one application over from the route `discussion_post_render.py` already drives.

**10. #821 splits.** The tooling has no gate and starts now; the deliverable is gated on a
gap statement that does not exist. `docs/agents/triage-labels.md` rules that a ticket with
an independently startable piece is not wholly blocked, and here the startable piece is
most of the work.

## Consequences

`tools/test_reference_scan.py`'s key-equality assertion moves when the fifth source class
lands. It should: it is a designed tripwire and this is the change it exists to make
somebody argue for in a diff.

`SOURCE-CLASSES` and `RECENCY-WINDOW-YEARS` become required `bar.md` fields for every
consumer of `research_ledger.py`, including `practicum-case-study`. A run that does not
sign them cannot be graded, on `discussion_post_scan.py`'s existing arrangement where a
missing field raises `SourceError` rather than defaulting.

Office reaches the run path for a second skill. ADR 0008's rule that consumers must never
need Office is satisfied the way `discussion-post` satisfies it — the clinician-supplied
export is the escalation, so PowerPoint is the fast path and never the only one.

**The skill is not on the critical path for having a deck.** Because production is
agent-side, a tooling slip past 2026-09-27 still leaves the clinician with a generated
`.pptx` and images. What a slip costs is the grading, not the artifact.

## What none of it reaches

`image-provenance-unverified`, above, and its neighbors: nothing proves the refuter was a
different agent or opened anything, which `research_ledger.DECLARED_LIMITS` already
carries as `refutation-independence-unverified`.

**`adversarial-completeness-unverified` is declared day one alongside it.** The
adversarial pass is the only one of the three whose output has no closed expected set, so
it can always return that the deck looks fine and nothing can prove it did not look. That
is the refutation limit one level up, and it is written down at the outset rather than
discovered after a run leans on it.

Whether a signed `FONT-DIRECTION` matches what the professor grades. The bar records the
clinician's reading of a page that contradicts the rule it cites; it does not establish
which reading will be marked.

Whether a dollar figure is the right dollar figure. The chain reaches *this number joins a
record and that record has a source that survived a hostile read*. Whether the lease
comparable is comparable, and whether the staffing model is the right staffing model,
remain clinical and commercial judgment.
