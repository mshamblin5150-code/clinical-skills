# A peer critique posts to the peer-review comment and its ampersand is typed literally

**Measured at:** b9456cc262c0c102a285935d05d4e201638e0207

[#991](https://github.com/mshamblin5150-code/clinical-skills/issues/991) reports that Canvas's
submission comment box turns a literal `&` into a visible `&amp;`, and that the damage lands in an
APA reference list, where the ampersand is mandatory. It offered four remedies and could not choose
among them. Grilled 2026-09-12; the clinician ruled every point below on the same day. Freshness gate
`FRESH` at `58b3bb8c`, then `STALE` before publication when `main` advanced to `b9456cc2`, a
correction to ADR guide grounding that touches nothing measured here; the branch was rebased and
the record re-declared against it. Nothing is built here; this is the record the build reads.

**The session's first framing was wrong, and the clinician corrected it twice.** It proposed moving
the critique to the board and leaving a one-line notice in the box, on the ground that
`skills/peer-critique/SKILL.md` step 6 calls the board *"the graded surface"* and the box
*"bookkeeping"*. He rejected the premise: the box accepts an `&`, a one-line notice is not how he
responds to a classmate, and the discussion reply and the peer critique are two artifacts that both
carry references. Everything below was measured after that correction, against his own M1 record.

## Measured before ruling

All readings were taken read-only on 2026-09-12 against the NUR 5144 M1 case-study assignment through
the clinician's signed-in Canvas session. Counts only; no classmate text is reproduced.

### The box stores the character and one page displays it twice escaped

The critique posted on 2026-09-09 carries three ampersands, all in its reference list. Four readings
of that one comment:

| instrument | real `&` | single-escaped `&amp;` | double-escaped `&amp;amp;` |
| --- | ---: | ---: | ---: |
| REST `submission_comments[].comment`, the stored text | 3 | 0 | 0 |
| GraphQL `htmlComment`, Canvas's own formatted HTML | 0 | 3 | 0 |
| server HTML of the legacy peer-review submission page | 0 | 0 | 3 |
| `document.body.innerText` of that page, what a reader sees | 0 | 3 visible | 0 |

**The instrument discriminates.** Had the box stored an entity, the first row would read 0 and 3;
had Canvas's formatter escaped twice, the second row would carry the 3 in its last column. Both read
the other way, and only the legacy page's server render adds the second escape. #991's own
measurement was the fourth row alone, which cannot tell a storage defect from a display one.

### The 2026-09-09 run loaded a real ampersand

That session's transcript shows the critique set into the textarea as plain text carrying the three
literal `&` characters, with no entity anywhere in the loaded value. The input was correct. #991's
body never said otherwise, but its title and its option 1 read naturally as *the box will not take
an `&`*, which is the reading the clinician objected to.

### The clinician's own posting pattern

- **Reply**: one board reply to the reviewed classmate, posted 2026-08-24, addressed by first name
  and carrying a reference list.
- **Peer critique**: posted 2026-09-09 as a comment on that classmate's submission, the eight-heading
  artifact with its own references. It is not on the board.
- Before 2026-09-09 the only comment on that submission was the instructor's. Canvas reported the
  peer review unfinished until the critique was posted, so the board reply did not finish it.

All five NUR 5144 case-study assignments have peer reviews enabled. Only M1's is finished.

## Ruled 2026-09-12

### 1. The Reply and the Peer critique are two artifacts on two surfaces

The **Reply** goes on the board, threaded beneath the classmate's initial post. The **Peer critique**
goes in the **Peer-review comment** on that classmate's submission. Both carry references. The peer
critique is not also posted to the board.

**`peer-critique` step 6 is wrong on this and is corrected by the build.** Its *"the spec calls the
critique a discussion board reply, so the board is the graded surface"* was an inference: the master
spec topic asks for *one scholarly response to a classmate* and names no surface. Its *"its comment
box is bookkeeping"* inverts the clinician's practice. Its instruction to ask the clinician, on every
run, which surface carries the reference list is retired, because this ruling answers it.

### 2. The ampersand is typed literally, and the text loaded is plain

The peer-review comment carries a real `&` in correct APA 7. The text loaded into the textarea is
plain text built from the critique's Markdown source, never the HTML that `tools/post_html.py`
builds for a **Composer**: that HTML deliberately escapes `&` to `&amp;`, and a plain textarea stores
whatever it is given, so an entity loaded there would be stored as five characters and damaged on
every surface.

This is #991's option 4, narrowed by the measurement: what is accepted is not *a mangled reference
list* but one legacy page's display of a correctly stored one.

### 3. The legacy page's `&amp;` is an expected observation, not a defect

The **Posted reading** of a peer critique is taken off Canvas's stored comment and compares its
ampersand count with the source's. A disagreement there is a defect and is recorded and filed under
the standing rule that nothing on the LMS is edited after posting. The legacy page showing `&amp;`
where the stored text holds `&` is recorded as the known display behavior and is not filed again.

### 4. #991's premise is corrected at respec

The box accepts an `&`; the storage and Canvas's formatted HTML are correct; the damage is one page's
render. The four contrast pointers in its body are all closed and are retired rather than repaired.

## Rejected options

**Write `and` for `&`.** #991's option 1. Displays correctly everywhere and is an APA error in the
graded reference list, traded for a display artifact on one page.

**Substitute a lookalike code point.** #991's option 2. Not an ampersand, so a reader copying the
citation carries a broken string, and it is wrong in the stored text that every correct surface shows.

**Put the reference list on the board and a notice in the box.** #991's option 3, and the session's
first recommendation. Refused on the clinician's practice: the board carries the Reply, the box
carries the Peer critique, and a notice is not a response to a classmate.

**Attach the rendered `.docx` to the comment as a clean copy.** Offered and declined. It adds a second
copy of a correctly stored artifact to work around a display the clinician accepts.

## What none of this reaches

- **Which screen the instructor grades from.** SpeedGrader is not visible to a student account, so
  whether the grader reads the legacy page or a view built from `htmlComment` is unmeasured.
- **Which page the reviewed classmate reads.** The legacy page's URL is the submission's own, so it is
  plausibly the classmate's view too; that was not observed from their account.
- **`<` and `>`.** Only `&` was measured. A clinical threshold written `<130/80` in a critique's body
  would presumably take the same second escape on the legacy page, and ruling 2 covers it on the same
  terms, but no posted comment carrying one exists to read.
- **A course that assigns no peer review.** Every NUR 5144 case study assigns one. Where a course does
  not, ruling 1 names no surface, and the run asks the clinician.
- **One institution, one Canvas instance, one account, one date**, the disclosure ADR 0013 made about
  itself, unchanged.
