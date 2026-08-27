# Clinical skills

Turning ER-style clinical shorthand into academic documentation — comprehensive SOAP notes and FNP H&Ps against a school rubric, plus the portal fields that record the clinical hours.

## Language

### The work

**Shorthand**:
Raw ER-style scratch for one encounter, written at the bedside, typo-ridden and incomplete.
_Avoid_: notes, scribbles, raw text

**Encounter**:
One patient seen once. The atomic unit of the domain.
_Avoid_: visit, case, patient

**Day file**:
One shift's shorthand in a single document, holding many encounters under a header naming the date and preceptor.
_Avoid_: shift file, batch, dump

**Note**:
The finished document produced from one encounter's shorthand.
_Avoid_: writeup, report

**Branch**:
Which template a note is written against — FNP H&P or comprehensive SOAP.
_Avoid_: format, type, form

### Coursework

**Board**:
One LMS discussion topic, holding its prompt, the clinician's own contribution and every classmate's, replies nested beneath. The authoritative copy of what a classmate actually read.
_Avoid_: thread, forum, discussion

**Initial post**:
The clinician's own first, graded, substantive contribution to a board. Its required shape is set by the individual discussion rather than by the course or the genre — one asks for a worked case, the next for a policy essay, and the one after that may ask for neither.
_Avoid_: main post, discussion post, original post

**Reply**:
A short conversational answer to one named classmate's initial post. A separate graded artifact with its own word floor, and never a second initial post.
_Avoid_: response, comment, peer review

**Graded artifact**:
One thing a course marks on its own — a board, a case study, a quiz. What identifies it is the artifact, not the module it sits in: a module normally holds several, so a module number names where something is rather than what it is.
_Avoid_: assignment, deliverable, submission

**Sitting**:
One occasion of working on a graded artifact. An artifact is usually written over several, days apart, and each produces its own submission. A sitting is provenance and never identity.
_Avoid_: session (in the agent sense — see **Session**), attempt, revision

**Session**:
One agent's working pass over this repo — the unit that opens a branch, sweeps the tracker, and writes residue into the scratch root. Distinct from a **Sitting**, which is a person's occasion of working on a graded artifact; that entry's _Avoid_ rejects `session` as a name for *a sitting*, not as a name for this. Two senses, one word, and the collision is recorded here rather than left latent.
_Avoid_: run, pass, sweep

**Run key**:
The identity of a graded artifact, as course, module and artifact — every part read off the live LMS or off which skill is running, and no part typed. It names the directory holding that artifact's whole provenance record, and prefixes the filename of every submission made from it.
_Avoid_: slug, run id, folder name

**Prompt**:
The board's own statement of what one initial post must answer. It supplies that discussion's shape and does not necessarily supply its bar.
_Avoid_: question, assignment, instructions

**Bar**:
The stated minimum a graded contribution must meet — words, references, source recency, required elements. Written on the course syllabus rather than on the board, so a run that reads only the topic page has not read it.
_Avoid_: rubric, requirements, spec

### Tiers

Every line of a finished note is a given, a derived value, or a filled one.

**Given**:
Content present in the shorthand or the portal entry, passing through unchanged — numbers, doses, results, stated findings, quoted speech.
_Avoid_: source, actual, real

**Derived**:
A value computed from a given by a rule with exactly one right answer, such as a BMI, an age, or a duration.
_Avoid_: calculated, inferred

**Filled**:
Content generated to satisfy the rubric where shorthand cannot supply it. Always unremarkable — normal, absent, or not reported.
_Avoid_: generated, invented, made up

**Asserted**:
A filled claim about the patient's past, such as a medication they already take or a condition they already carry.
_Avoid_: history, background

**Proposed**:
A filled forward action, such as a drug started, a test ordered, or a referral made.
_Avoid_: recommendation, suggestion

**Declared**:
A value fixed by a stated rule rather than observed. Either a constant, which always holds, or a default, which is overridable on sight.
_Avoid_: assumed, hardcoded

### Defects

**Drift**:
A finding documented in the shorthand, carried into the Objective, and absent from both the Assessment and the Plan. A drifting note reads perfectly well, which is why it survives.
_Avoid_: omission, miss, oversight

**Flag**:
A defect raised for the clinician's eye before submission, naming the finding and what was not done with it. Most often an instance of drift.
_Avoid_: warning, issue, note

**Gap**:
Something the rubric needs that the encounter genuinely did not supply.
_Avoid_: missing, hole, TODO

**Unknown token**:
A shorthand token matching no glossary entry.
_Avoid_: unrecognized, garbage, typo

### Artifacts

**Working file**:
The complete, identified record of a day's encounters, used to enter the portal. Never leaves the machine it was made on.
_Avoid_: draft, local copy

**Claim ledger**:
The record of every new factual claim a graded document makes, one entry per claim, each naming what was searched, what was found, the page read and the date it was read on, and the result of an independent attempt to refute it. Written before the document that rests on it.
_Avoid_: sources file, bibliography, notes

**Stated expiry**:
The date a source prints on itself as the day it ceases to have effect. Read off the document, never derived from how often its publisher reissues — a source with a known replacement schedule and no printed date has none, and a claim ledger records that it has none rather than leaving the question unasked.
_Avoid_: expiration, sunset, shelf life, validity window

**Citation key**:
The pair of a normalized author phrase and a year that a citation and a reference entry must both produce before the citation counts as resolved. It is a name rather than an identity — one entry may yield several, and a yearless one resolves against any year.
_Avoid_: reference id, source id, match key

**Legal reference entry**:
A reference for a regulation. Its name is the name of the regulation and its section is the locator, so an entry carrying only a section names nothing and is not one.
_Avoid_: statute reference, citation entry, regulation cite

**Legal citation**:
An in-text reference to a regulation, spelled with the regulation's name and year. The section is a locator and may stand in the same slot, but it is not what names the source.
_Avoid_: statute citation, section reference

**Run directory**:
The one place a graded artifact's provenance is kept — its bar, its board snapshots, its claim and check ledgers, and the evidence it was handed. Named by the run key, so it carries no date and outlives every sitting.
_Avoid_: run folder, workspace, scratch dir

**Submission**:
The finished document handed to the course, and the only artifact here a course marks. One per sitting, named by its run key and the date it was written, living in the checkout a person looks in rather than in whichever tree a run stood in.
_Avoid_: final, output, deliverable

**Evidence dump**:
The topics the clinician was handed wholesale, and the whole of what was read without going looking. A claim it does not cover is one nobody opened, which is why it belongs to the run that was handed it rather than to the account.
_Avoid_: sources, corpus, articles

**Fixture**:
A regression set derived from a working file with the visit date and site removed, committed so a skill's behavior can be checked after an edit.
_Avoid_: test data, sample, example

**Assertion**:
A claim in the clinician's own words about what a correct run must contain.
_Avoid_: expectation, check, test case

**Ruling cohort**:
The assertions across one or more fixtures that express one clinician ruling and share one promotion boundary. Its members move together or not at all.
_Avoid_: batch, group, wave

**Valid score**:
A pass or a fail on an assertion, read from output produced while the rule that assertion states was already in force. Unscoreable is not one.
_Avoid_: result, grade, reading

**Promoted assertion**:
An assertion whose bar has become binary, kept in place as its own history and naming the enforced successor that now carries its subject.
_Avoid_: upgraded row, migrated row, replacement

**Targeted scoring**:
Grading one assertion against every encounter it names, or against the whole set where its subject is the set. Complete evidence for that assertion, and not a run.
_Avoid_: partial run, spot check, sample

**Patient Time band**:
The hours bucket an encounter accrues against. The one administrative field where a wrong value has a real consequence.
_Avoid_: age group, category

**Patient Reference**:
The opaque identifier Medatrax generates for a patient, such as `40EEE8DB06FB466`. The portal's only handle on a person; it never accepts or stores a name.
_Avoid_: patient ID, MRN, reference number

**Identity map**:
The clinician's private table joining a patient name to their Patient Reference, so a returning patient is found rather than created again. Lives beside the working files and never leaves the machine.
_Avoid_: patient list, roster, lookup table

**Duplicate**:
A second Patient Reference for a person who already had one, created because the encounter reached the portal without a name to match on. Indistinguishable from a new patient afterwards.
_Avoid_: dupe, repeat, double entry

**Writing sample**:
One piece of the clinician's existing prose, chosen by them and handed over on its own, from which a register is read. Selection is the consent — they know what each one contains.
_Avoid_: writing example, submission, document

**Export**:
The whole of what a clinician typed into an assistant, handed over as one container. Unlike a writing sample nothing in it was chosen, so its contents are unreviewed by the person supplying it and unknown to the person reading it.
_Avoid_: chat history, archive, dump

**Invoked source**:
A domain the writer reaches outside the immediate subject for -- a mechanism, a discipline, a named authority -- whose real behavior is then spent as the argument. What makes one load-bearing is that the claim rides on what the domain actually does; a decorative one names nothing it is spending. The domain is open by construction, because the same domain can be invoked in one sentence and used literally in the next, so nothing keyed on a list of domains recognizes an instance.
_Avoid_: metaphor, figure, imagery, amplification, craft metaphor

**Publish**:
Writing a build-derived artifact to a path inside a git checkout, as against writing one outside every checkout. Only a publish can reach a commit, so it is the step a trust rule attaches to; writing the same bytes elsewhere is not one.
_Avoid_: write, output, emit, save

**Trust floor**:
The inputs whose change makes a found artifact no longer believable — the files that decide what the artifact *contains*, never the ones that decide how it is stamped. Usually code, and not only code: committed data a producer lifts content from is in the floor on the same test. Trust is settled by comparing what is recorded against what is on disk, so a reader can re-derive it; a producing commit only ever approximates it.
_Avoid_: producer code, producer paths, unchanged paths, provenance list

**Cache identity**:
Everything a content-addressed build hashes to decide whether it may reuse an earlier artifact instead of producing one again. Deliberately wider than the trust floor, because the price of a miss is a rebuild and the price of a wrong hit is a stale answer.
_Avoid_: build key, fingerprint, producer identity

**Held declaration**:
A claim a curated artifact makes about a check its reader may be unable to re-run. The run that *can* re-run it is the only thing enforcing the claim — refusing where it is absent, and refusing where it describes a different run than the one that just happened. Never checked against elapsed time, because no artifact knows what its reader's machine holds. Which claims qualify is enumerated by hand, never inferred.
_Avoid_: provenance line, status line, audit note, metadata

**Accepted distrust**:
A held declaration for a verdict a command produced while knowingly reading an artifact whose provenance check failed. It is a property of the run rather than of the artifact read, and where the verdict reaches a curated file by way of a person it is the artifact's own declaration — naming the source, the date and the reasons — that holds the verdict; a superseding trusted run retires it.
_Avoid_: provenance stamp, taint, untrusted flag

**Paste box**:
The rich-text field a graded post is submitted through, as distinct from a file upload. It keeps the tags of what is pasted and discards every style, class and stylesheet, so a document's appearance never predicts it.
_Avoid_: editor, text field, LMS box

**Clipboard courier**:
A rendered `.docx` that exists only to be opened and copied from, never uploaded and never graded. Its own layout is inspected by a person and reaches no reader.
_Avoid_: submission copy, output document, export

**Direct formatting**:
A run or paragraph property written onto the element itself rather than inherited from a named style. The only form that survives the clipboard, because a style is carried by reference and the reference is what a paste target drops.
_Avoid_: inline style, hard formatting, manual formatting

**Dated observation**:
A committed measurement of a third party this repo cannot re-derive, carrying the date, the instrument and the scope it was taken at in its own fields. Evidence that something behaved a certain way once, never a claim that it still does.
_Avoid_: fixture, baseline, snapshot


### Guidelines

**Corpus**:
The society guideline PDFs every derived artifact here is built from. It lives outside every checkout and is not going into one, so nothing committed re-derives a figure counted against it and no runner ever sees it. It grows by a person putting a file into it, which is an event no artifact in the tree witnesses.
_Avoid_: sources, library, guidelines, documents

**Guideline catalog**:
One curated row per corpus document — society, filename, title, topic, population, year, page count, class. Its mechanical columns are re-derived and audited; its judgment columns are read by a person. It is the denominator every downstream population is counted from, so a corpus document with no row is invisible to all of them.
_Avoid_: index, manifest, inventory, document list

**Audit ledger**:
The committed record of the blind second read of the catalog, holding one row per corpus document with the SHA-256 of the bytes that were read. Its subject is file identity, which is what distinguishes it from the catalog, whose subject is metadata about documents. It is the only place the tree states which exact bytes a reading rests on.
_Avoid_: audit file, digest file, hash list, checksums

**Stated citation**:
The way a corpus document identifies itself on its own page, so that a person could obtain it again — a DOI, a URL the document prints, or a journal citation line. It is read off the page and never found by searching, so a document that prints no such thing has none rather than acquiring one. It says what this copy states, which is a fact about the copy: a co-published guideline prints one DOI and may be correctly cited by another, so a difference from the address a threshold sheet sends a reader to is not a defect. Nothing in the tree has opened one.
_Avoid_: locator, url, doi, link, source

**Corpus drift**:
The corpus and the tree's record of it having come apart — a document added, removed, or reissued under an unchanged filename. It is not a defect and nothing refuses it; what is a defect is a tree that carries on answering without saying it happened.
_Avoid_: staleness, desync, corpus change, mismatch

**Threshold sheet**:
The distilled decision points of one clinical topic, drawn from every guideline in the corpus that addresses it. Curated Markdown that a tool audits, never a generated artifact.
_Avoid_: summary, digest, extract, cheat sheet

**Topic**:
The subject a threshold sheet is keyed to, such as hypertension. The unit a clinician cites; a guideline document is not one, and several documents may address the same topic.
_Avoid_: condition, subject, area

**Recommendation record**:
The machine-readable extraction of one guideline document's recommendations, keyed to the document it was read from. Which lookup root holds it decides how it is found: where records are fed in one document at a time the filename is a claim rather than a fact, so a record is resolved by exact name and then checked against the document it says it came from; where a sweep published them it is addressed by the document, the name having been ruled incapable of distinguishing one document from another across the whole corpus. The producer guarantees that everything it writes makes the claim, never that everything making the claim came from it.
_Avoid_: recs file, extraction, recommendations JSON

**Lookup root**:
One of the two places a reader looks for a recommendation record. A recommendation sweep publishes one of them, holding one record per document and answered first because a verified build is the stronger evidence; the other is fed a document at a time by hand and answers only where the first has nothing. Which one answered is named every time a record is read, because one sheet graded against the two is graded against different evidence, and a record named explicitly on the command line outranks both.
_Avoid_: records directory, records folder, recs directory

**Sweep alias**:
The lookup root a recommendation sweep publishes for readers, holding one record per document and named from the document rather than from any sheet's key. It is a transport and not a claim: the copy carries no evidence that a verified build produced it, so what a reader checks is the trust each record carries in itself.
_Avoid_: published records, recs mirror, alias directory

**Recommendation sweep**:
The production of one recommendation record for every document in the guideline corpus as a single verified build, rather than a document at a time. A document the sweep read and found no recommendation in still gets a record, and that record says so — which is a claim about what the reader matched, never a claim that the guideline states no recommendation.
_Avoid_: batch run, corpus pass, recs build

**Source key**:
The name a threshold sheet binds a recommendation record by. It is sheet-local, so two sheets may pick one key for different guidelines, and it resolves a filename rather than identifying a document.
_Avoid_: source id, record key, slug

**Source mode**:
How completely a guideline's recommendations could be read, and therefore how strongly a claim about them can be gated. `exact` where every recommendation was counted from a ruled table or the curated federal table; `bound` where they were matched by marker in running prose, which over-reports and can truncate.
_Avoid_: confidence, quality, extraction mode

**Snippet**:
The shortest verbatim fragment of a guideline that carries a decision point, quoted in the row that cites it. Verbatim is what makes a fabricated citation detectable, so a paraphrase is not one.
_Avoid_: quote, excerpt, evidence, text

**Recommendation label**:
The text a recommendation carries to say which recommendation its identifier names. On a `bound` source it is a fixed-length window of the page around the marker, so it is an aid to a reader and never a quotation — a **snippet** on such a source is read off the page instead. On an `exact` source the same field is the ruled-table cell or curated statement itself and may be quoted.
_Avoid_: snippet, quote, record text, excerpt

**Marker anchor**:
Which end of a recommendation a text marker sits on, and therefore which way its **recommendation label** reads. A marker naming the recommendation sits at the start and reads forward; a GRADE parenthetical sits at the end and reads backward. A marker with no anchor declared is a failure rather than a default.
_Avoid_: direction, position, offset

**Changelog record**:
A marker hit on prose that names a recommendation rather than stating one, such as a front-matter summary of what changed since last year. It is a real marker hit and inside a `bound` count's over-report contract; it is censused on a floor and never filtered, because the editorial vocabulary is open and filtering would drop real recommendations.
_Avoid_: false positive, spurious record, noise

**Decision point**:
A quantity a guideline attaches a value to that changes what is done to a patient — a dose, a period, a cutoff, or a target. It is read from what the guideline states, never inferred from a catalog or recommendation index. A recommendation carrying no such quantity has none.
_Avoid_: threshold, recommendation, criterion

**Interval**:
How often a recommended service recurs, which is the question the USPSTF recommendation table's
`Interval` column answers. A period where the recommendation names one, and a bare recurrence or a
count where it does not — a recommendation may say a service repeats without saying how often, or
that it happens once. A dose frequency is not one there: a supplement taken daily recurs, and the
service does not. Elsewhere a threshold sheet's quantity key names its own subject, so a dosing,
titration or withholding period filed under an `-interval` key is a narrower claim rather than a
contradiction of this.
_Avoid_: schedule, periodicity, cadence

**Quantity key**:
The stable name for what a threshold row measures. A method-dependent value names the method in this key, so the method is neither mistaken for a patient population nor reported as a conflict.
_Avoid_: metric, field, variable

**Coverage registry**:
The one-row-per-topic record of the threshold-sheet sweep. Its topic population is derived from the guideline catalog, and each row names whether the topic has a sheet, was read and had no decision point, or remains unread.
_Avoid_: checklist, index, inventory

**Sweep state**:
One of `sheet`, `none`, or `unread`. `none` means the guideline was read and states no decision point; `unread` establishes nothing. It describes the read behind a sheet and never whether a run may open one, which is the shipped artifact's question. What `sheet` asserts is that every page of the source sits in a read span — it is derived from the sheet's own span table rather than typed, and the registry refuses a disagreement in either direction.
_Avoid_: status, result, disposition

**Shipped artifact**:
The sheet a coverage-registry row names in its artifact column. This is what a run joins on and may consult, whatever the row's sweep state; an artifact on an `unread` row is a real sheet whose full-document read is pending, and every sheet's own scope names what it did not read. Reading it settles no less than reading any other — a missing row means the sheet does not settle the question, in a partial sheet and a complete one alike.
_Avoid_: partial sheet, draft sheet, provisional sheet, candidate sheet

**Span**:
One named part of a source document with a page range, such as its clinical considerations or its reference list. The unit a sheet's unread list is written in, and the unit a blind second reader is briefed on. Spans may overlap, because a page can carry two of them.
_Avoid_: section, chapter, part, region

**Section read**:
Reading one span for decision points. It leaves the rows that span holds and a narrowed unread list, and it is the unit of work — a sheet is completed one span at a time, never in a single promotion. A span leaves the unread list when it yields rows, when a blind independent read agrees it holds none, or when it is a reference list retired by class with that reason recorded.
_Avoid_: sweep, pass, promotion, full read

**Scope summary**:
The two prose limbs above a sheet's span table, `Read:` and `Not read:`, in which a person states in their own words what the read covered. [ADR 0025](docs/adr/0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md) point 4 keeps it deliberately as the human summary of a machine-graded table, which makes it a second statement of one claim. Only one direction is graded against the table: a span that has left the unread list may not be named in the summary as unread. That the summary names every unread span is not graded and cannot be — the summary may compound and pluralize spans, and every sheet does.
_Avoid_: unread list — that names the span table, which is the graded copy. Also avoid prose limb and human summary for the term itself; both describe it and neither says which copy is which.

**Page coverage**:
The requirement that the read and unread spans of a sheet together account for every page of its source, counted against the guideline catalog's own page count. It catches a span nobody listed; it does not catch a span whose page range is drawn wrong.
_Avoid_: coverage — unqualified, that word names three different things here: the `## Coverage` section inside a sheet is which recommendation identifiers were accounted for, the coverage registry is the per-topic sweep record, and this is the per-page document read. Always say which.

**Scoped out**:
A recommendation the sheet's source states and the sheet deliberately does not carry, named by identifier so the omission is recorded rather than silent.
_Avoid_: excluded, skipped, filtered, ignored

**Glued run**:
Several words reaching the extracted text with no space between them, because the PDF positioned the glyphs and set no space glyph. The information is not lost — the geometry still carries the boundary — so a glued run is a reconstruction failure and never an absence.
_Avoid_: run-on, mangled word, concatenation

**Recommendation**:
One recommendation lifted out of a guideline by `tools/guidelines_recs.py`, carrying its identifier, page, text and the mode that says how it was counted. It is the unit a threshold row cites and the unit a citation gate resolves against, so a recommendation the reader never built is invisible to every check downstream of it.
_Avoid_: rec, extraction, entry, hit

**Reader limb**:
One of the three paths a recommendation record is built through — curated verification, ruled table, or text marker. The limb is what decides which reader saw the page, and therefore what a gate over that record is able to see, so a limit stated about records in general is a limit stated about the wrong unit.
_Avoid_: path, mode, branch, route

**Shared-reader blindness**:
A check whose two sides are produced by the same reader, so it cannot see a defect that reader introduces — the damaged text agrees with itself and the check passes. It is a property of the comparison rather than of either side, so it is not fixed by repairing one of them; it is fixed by a second reader, or it is declared.
_Avoid_: tautology, circular check, self-comparison

**Dropped recommendation**:
A recommendation the source states and no record carries, because the reader damaged the marker that would have matched it. Distinct from a **glued run**, which is damage a reader of the record can see: this one leaves nothing behind, so no check over the output can reach it and the count it corrupts is a denominator.
_Avoid_: missed rec, gap, omission, undercount

**Digit-break**:
A space the reconstruction inserted with a digit on at least one side of it. The class matters because a quantity broken apart is the one extraction defect this repo cannot afford, and it is graded by boundary class rather than in aggregate — a boundary between two digits is a different risk from one beside a decimal point.
_Avoid_: number split, bad break

**Orphaned figure**:
A published measurement whose producing instrument no longer exists, so no command will ever print it again. It is a declared limit rather than a stale figure — nothing will make it decay and nothing will make it re-derivable — and it is named in one object that prose points at rather than copies.
_Avoid_: historical figure, legacy number, dated result

**Declared limit**:
A boundary of what a mechanism reaches, held as a named object beside that mechanism rather than as prose about it. Prose points at the object and copies no row of it, so a limit that stops being true fails a check instead of standing as a claim nobody re-derives.
_Avoid_: caveat, known issue, disclaimer

**Underived count**:
A figure stating the size of a population that is sitting in code and was never consulted. The remedy is to derive it or to drop it; the corrected number is as underived as the wrong one. Distinct from an **orphaned figure**, whose instrument no longer exists at all — that one is declared, this one is repaired.
_Avoid_: stale count, off-by-one, magic number

### Checks

**Prose bind**:
An assertion that a phrase is present in, or absent from, a document the repo tracks. It is what couples a rule written in one file to the check that holds it, so a bind that passes for a formatting reason is a rule nothing is holding.
_Avoid_: assertion, string check, doc test

**Needle**:
The phrase a bind looks for. Written by the author of the check, so it is the half a rule can be stated in.
_Avoid_: pattern, search term, target

**Haystack**:
The text a bind looks in. Whether it is a tracked document or something the code under test produced is the property that decides whether a bind can fail silently, so it is the half that is graded.
_Avoid_: source, corpus, subject

**Prose mark**:
Emphasis, comment and quotation punctuation that a document's formatting may add or drop without changing what it says. Removed from both halves of a bind so hard wrapping and emphasis cannot decide the outcome. Distinct from a **glued run**, which is an extraction failure rather than a formatting choice.
_Avoid_: glue, noise, markup

**Declared limit**:
A boundary of what a mechanism reaches, held as a named object beside that mechanism rather than as prose about it. Prose points at the object and copies no row of it, so a limit that stops being true fails a check instead of standing as a claim nobody re-derives.
_Avoid_: caveat, known issue, disclaimer

**Underived count**:
A figure stating the size of a population that is sitting in code and was never consulted. The remedy is to derive it or to drop it; the corrected number is as underived as the wrong one. Distinct from an **orphaned figure**, whose instrument no longer exists at all — that one is declared, this one is repaired.
_Avoid_: stale count, off-by-one, magic number

**Second route**:
The access path or instrument a refuting pass used that the pass it is checking did not — a different rendering, a different access path, an independent corroborating source. It is written as two halves so the pair can be compared, and a check fires when they match, because an agent briefed as both passes has only one route to name. Distinct from a **declared limit**, which says what a mechanism does not reach: this is the thing one mechanism does reach, and independence is what it still does not establish.
_Avoid_: verification, second opinion, double-check, independence
