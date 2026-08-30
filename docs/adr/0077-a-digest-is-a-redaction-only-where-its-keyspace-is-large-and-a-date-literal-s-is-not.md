# A digest is a redaction only where its keyspace is large and a date literal's is not

[#646](https://github.com/mshamblin5150-code/clinical-skills/issues/646) is the first live
`corpus-date` finding this repository has recorded on the public tracker. `phi_scan`'s corpus layer
is the only layer that can see one, and it can only ever run on the maintainer's clone: `scratch/`
is gitignored PHI that must never reach a runner, so
[#260](https://github.com/mshamblin5150-code/clinical-skills/issues/260)'s Actions trigger passes
`--allow-no-corpus` and is correct about everything it measures while being structurally unable to
measure this.

Grilled 2026-08-30. **Seven rulings, made by the clinician on that date.** Almost nothing is built
here; this is the record the builds read. One repair landed in the session and is ruling 1.

## What the grilling found that the ticket did not

**The finding was a coincidence, and two exhaustive sweeps confirmed it without establishing that.**
The firing token is a **federal regulation's annual codification date**, inside the worked example of
a closed ticket arguing about that regulation's revision cycle. It collides with a `scratch/` date
literal by calendar coincidence and carries no patient, no encounter and no linkage. Both sweeps on
#646 verdicted **HOLDS** and both say in as many words that they re-derived in redacted mode and
read no value — so *HOLDS* meant *the scanner still fires*, never *a patient date is still exposed*.
Those are different claims. This is
[#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) ruling 10 again: the two
raw captures were caught by **opening** the files rather than by reading their filenames. A redacted
re-derivation is the right reporting default and it is not a reading.

**And the ticket's structural claim is narrower than it states.** #646 says the only machine that can
see a corpus collision is the one that is not in the publishing path. That is true of the GitHub web
UI and false of everything else: essentially all tracker text here is written by agents running
`gh issue create|comment|edit` **on the maintainer's clone**, which is exactly where the corpus layer
is live. The publishing path and the corpus-bearing machine are the same machine for agent-authored
text.

## Ruled 2026-08-30

**1. A record whose corpus collision is coincidental is repaired by de-citing, never by falsifying.**

Three repairs were priced against the record the finding sits in. Substituting a synthetic date makes
a closed ticket state something false about a checkable federal artifact, which is the shape
`fixtures/day-b/assertions.md` already forbids — a gate firing on a sentence the file forbids fixing,
whose only available repair is to falsify the record. Leaving it standing keeps a value on the served
copy. **De-citing** — dropping the literal and keeping the sentence that carries the argument — costs
the record nothing, because the surrounding prose already implies the value for any reader who needs
it.

**That last clause is the honest price and it is why this ruling is narrow.** De-citing removes the
literal from the scanner's view and barely from a reader's. It is worth doing because it is free, and
it is not what closes the exposure; ruling 2 is.

Landed in the session: the record now reads `` `DATE` and `ORIGINALDATE` recording that edition's own
revision date ``, one line changed, verified by a pre-flight scan before publishing, a
`tracker_bodies.py` read-back of the served copy, and a re-scan at a refreshed base — clean, exit 0,
all three. **The retained pre-edit revision still carries the value**, which
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) established has no API to
read or delete and which was ruled acceptable on 2026-08-19. Nothing here reopens that, and no repair
in this record may be read as promising the value is gone.

**2. A ruling on a PHI-layer finding is keyed on the record and the containing line, never on the
match.**

The name side of this problem is solved and does not transfer. `NOT_NAMES` holds *non-names* —
ordinary vocabulary, safe to commit — and `scratch/harvest-reviewed.json` holds *real names* and is
therefore gitignored. A date ruling has neither home available: a value-side list publishes a corpus
date into a public repository, and there is no third place for it to live.

So the ruling is keyed on a **locator plus a digest of the containing line**. The locator carries no
PHI and is already public. The line digest is what makes the ruling *expire*: rule a location clean
today and a bare locator lets a later edit to that line inherit the exemption silently, which is a
record exempting itself by position — the failure `spelling_scan.py`'s span rule and `phi_scan.py`'s
own-line pragma requirement both exist to refuse.

**The digest unit is the whole of this ruling and it is where a rebuild will go wrong.** Digesting the
*match* looks equivalent to digesting the line and is not, which is ruling 3.

**3. A digest is a redaction only where its keyspace is large, and a date literal's is not.**

An unsalted SHA-256 of a value drawn from an enumerable set is an index into that set, not a
concealment of it. A date has at most a few tens of thousands of plausible renderings across the
numeric, written-English and ISO families
[#261](https://github.com/mshamblin5150-code/clinical-skills/issues/261) declares, and this corpus
holds a few hundred date literals; the enumeration is seconds of work for anyone holding the public
repository. A whole line of prose is not enumerable and is therefore a sound digest unit.

**This is not a new ruling. It is [ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)'s,
restated because a shipped artifact contradicts it.** That record already priced and refused the
mechanism, for a value class with a *larger* keyspace than the one at issue here — *"Hashing the names
was considered and is worse. A short filename is a dictionary away from its hash, the hash would be
published irrevocably"* — and named #212's retained revisions as the reason a later redaction would
not retract it.

**4. `reference/tracker-scan-rulings.json` carries the refused mechanism and is repaired rather than
removed.**

[#264](https://github.com/mshamblin5150-code/clinical-skills/issues/264) built the ruled-hit ledger
this repository needed and keyed each row on `hashlib.sha256(finding.match...)` — unsalted, unkeyed,
uniterated — in a **tracked file in a public repository**. The module docstring states the intent in
as many words: the ledger digests because *a copied literal could itself be PHI*. So the digest was
chosen to do redaction work, and for this value class it does not do it.

**`phi_scan` cannot see it, and that is the property that makes it worth an ADR rather than a
ticket alone.** A 64-character hex string matches no rule in any of the three layers, so the firewall
reports clean over the one file in the tree that carries a recoverable form of what the firewall
exists to keep out. Run with the corpus live, `--all` finds nothing.

The repair is ruling 2's keying applied to the existing ledger, with the rows regenerated from a
corpus-live clone. **Removing the ledger is refused**: it is the mechanism that stops a growing
history surface from re-triaging itself forever, which is #264's whole subject and is a real cost
this repository measured across four dated runs. **Stripping the digests alone is refused too** — it
returns the commit surface to a standing exit 1 and touches no history, which is cost with no
benefit.

**The prose reason fields were checked and are clean.** The only date-shaped token in any of them is
the public #212 ruling date, which is not a corpus literal.

**5. A pre-publish tracker check exists, is a `PreToolUse` hook, and is advisory.**

#260 declined a pre-publish check on the ground that *a comment is published without a push*. That
reasoning is correct about **git** hooks and reaches no further: a `PreToolUse` hook on Bash fires at
the publish itself, and `.claude/settings.json` is neither tracked nor ignored here, so one can be
committed and travels to every clone and worktree. The heredoc body of the documented
`--body-file -` form is inline in the command string the hook receives.

**Advisory rather than refusing, and the measurement is what decided it.** The refusal argument is the
one this repository normally makes — standing rule 1 refuses a commit, and a tracker publish is worse
than a commit, being public and unretractable. It loses here on two grounds. The single live
`corpus-date` in this repository's history was a coincidence, so a refuser's first act would have been
to **block a legitimate ticket** over a federal register date: one for one on live instances. And the
release valve does not exist — ruling 2's lane keys on a record locator, and a record being *created*
has no locator yet, so the lane structurally cannot clear a pre-publish block on a new issue or
comment. Building a second adjudication surface with different keying, to serve one hook, is more
mechanism than the measured problem carries.

**What advisory buys is named rather than assumed**: it converts the failure mode from *a value goes
up unnoticed* to *a value goes up with a decision recorded*. The standing objection — that an advisory
check which crashed is indistinguishable from one that passed, which this repository has already paid
for once when `spelling_scan`'s staged run died and a listed form reached a skill file — is answered
by making the hook's own failure loud, not by making it refuse.

**6. The periodic full harvest is a dated marker plus an age notice, and it names no threshold.**

Today's answer is a one-time hand pass recorded in prose, which is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written instruction
cannot do is fail* — and it did fail: the 2026-08-20 result stood as a current claim for ten days
while the record that falsifies it was published under it.

So the harvest writes a marker recording when it last really ran and what it found — a date and
counts, no values, safe to commit — and `phi_scan` states that marker's **age** on the commit path.
It goes in `shortfall_notice`'s home and **not** in `layer_report`: that function's own docstring
records why, because #141's first version put the notice there, the hook runs the scanner bare, and
the feature printed on no commit at all while prose claimed it printed on every one.

**It states the age and names no threshold.** There is nothing to ground a cut point on — the corpus
offers no split the way 130/80 grounded
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s, so any number of days would
be a value named at an edge, which is `SPACE_ADVANCE_FRACTION`'s recorded failure. It is also the
honest form: what makes a harvest stale is how much tracker text was published since, not how much
time passed.

**7. `CLAUDE.md`'s harvest sentence splits — the reasoning stays in prose, the result becomes a
pointer.**

That sentence does two jobs. The reasoning half — `scratch/` may never reach a runner, so the corpus
layer is dead in CI on every run that will ever happen — is durable and is the most load-bearing
sentence in its section. The result half is a **measurement**, and
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s discipline is that a
measurement is cheapest to keep true where the code that produces it lives.

**The sweep's framing correction is adopted.** #646's decision 4 says the sentence reads as a current
property; it is already dated. What it lacks is a **status**, and this session establishes something
stronger than an absent one — the clean result it reports is superseded, because the record carrying
the collision postdates it. Appending a status was refused: it is correct for one commit and then
decays exactly as the sentence it replaces did, which is the generator #143 names.

## Consequences

**Four builds, on four tickets, and none of them is built here.** Ruling 2's lane extended to the
harvest surface, which the shipped ledger does not reach — its rows key on a commit id and an issue
body has none. Rulings 3 and 4's re-keying of that ledger. Ruling 5's hook. Ruling 6's marker, which
carries ruling 7's prose repair, because the pointer has nothing to point at until the marker exists.

**Ruling 3 is the one to read before touching any of them.** It is stated here rather than left in
#264's implementation notes because the mechanism it refuses is the one a rebuild reaches for first,
and because a ratified record already refused it once and a shipped artifact adopted it anyway.

**What none of it reaches.** The retained pre-edit revision of any edited record, permanently, per
#212. The GitHub web UI, which ruling 5's hook does not bind. And whether a `corpus-date` collision is
a coincidence or a disclosure, which is a **reading** — the scanner reports that a corpus literal
appears, and only a person opening the record can say what it is. The two sweeps that confirmed this
finding without opening it are the standing evidence for how easily that step is skipped.
