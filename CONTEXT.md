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
