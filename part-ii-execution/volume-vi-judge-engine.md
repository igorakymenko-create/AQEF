# Volume VI — Judge Engine

**Status:** confirmed (v0.1).

*Question answered:* How subjective quality is evaluated.

Chapter 4 named the Judge Engine as the component that executes Judges (single or
multi-Judge, with Consensus/Voting) and routes to a Human Reviewer where the Contract
requires it, tracking Judge Drift and Calibration over time (Volume I). This Volume
specifies the mechanics: what a Judge is architecturally, how one or many Judges combine
into a verdict, how a Judge produces and maintains a trustworthy Confidence value, and
when a Human Reviewer — the same entity Volume II defines, not a separate ad hoc
concept — takes over. Everything here runs only after Validation has already passed
(Validation before Evaluation, Chapter 3); the Judge Engine picks up exactly where
Volume V's Validator Pipeline hands off.

| Section | Role |
|---|---|
| Judge Architecture | What a Judge consists of; Independent Oracles applies at its strictest here |
| Single Judge | Baseline case — one Judge, one Conversation, one Confidence-qualified Result |
| Multi Judge | More than one Judge assesses the same Conversation — for independence, or for stability; not the same purpose |
| Consensus | How disagreement among Multi Judge Results gets resolved into one verdict |
| Voting | One specific Consensus mechanism — majority/plurality counting of discrete verdicts |
| Confidence | How a Judge produces its own Confidence value (production, not consumption — Chapter 6 covers consumption) |
| Calibration | Whether a Judge's stated Confidence actually tracks its accuracy, against a reference |
| Human Review | Where the Human Reviewer Oracle gets invoked — by Contract, low Confidence, disagreement, or as calibration ground truth |
| Judge Drift | What Semantic Regression (Volume X) is to the subject, Judge Drift is to the Oracle |

## Judge Architecture

A Judge, architecturally, mirrors a Validator's three parts with one difference that
changes everything downstream: a probabilistic assessment process (typically an AI
model, given specific criteria drawn from a Quality Contract clause, Volume VII), a
target — Conversation and/or Artifacts, same as a Validator — and a binding to the
Contract clauses it assesses. Unlike a Validator, a Judge's Result MUST carry a
Confidence value (Glossary), because its check is not a pure deterministic function of
its input the way a Validator's is. This is also where Independent Oracles (Chapter 3)
applies at its strictest: a Judge assessing Semantic or Business Quality is exactly the
case that principle was written for, since a Judge drawn from the same model family as
the system under test risks failing to notice precisely the errors that family is prone
to. A Judge's architecture MUST make its criteria explicit and inspectable, for the same
reason Chapter 3 requires Contracts over Assertions: a Judge whose criteria live only
inside an opaque model prompt is no more auditable than an inline assertion buried in
test code.

## Single Judge

The baseline case, the same role Single LLM plays among architectural patterns (Chapter
7): one Judge assesses one Conversation against one Contract clause, producing one
Confidence-qualified Result. Every other section below is naturally described as
"Single Judge plus one added mechanism" — Multi Judge adds more Judges, Consensus and
Voting add a way to reconcile them, Calibration and Judge Drift add tracking over time,
and Human Review adds a different kind of Oracle entirely. Single Judge alone already
satisfies everything the Glossary and Chapter 3 require of a Judge; nothing below is
required for correctness, only for the specific concerns — independence, disagreement,
drift — that scale introduces.

## Multi Judge

Multi Judge runs more than one Judge against the same Conversation, but the reason
matters, and the two common reasons are not interchangeable. Running genuinely different
Judges — different model families, different criteria phrasings — is what actually
delivers on Independent Oracles: it is the only version of Multi Judge that can catch a
blind spot a single Judge, however carefully prompted, structurally cannot see on its
own. Running the same Judge multiple times (repeated sampling of one model, one prompt)
instead reduces sampling noise — it makes one Judge's own verdict more stable, but does
nothing for correlated blind spots, since every sample still shares the same underlying
weaknesses. A Contract that specifies Multi Judge for independence and one that
specifies it for stability are asking for different things, and a Multi Judge
configuration MUST be explicit about which it is providing.

## Consensus

Consensus is how disagreement among a Multi Judge configuration's individual Results
gets resolved into one verdict for the Execution. Disagreement itself is informative,
not merely noise to average away: a Conversation that genuinely independent Judges
assess differently is evidence that the Conversation sits in ambiguous territory, the
same signal Chapter 6's Confidence Model already treats a single low-Confidence Result
as — and for the same reason, unresolved Consensus disagreement is a legitimate trigger
for Human Review (below), not just a mechanical tie-break. What Consensus resolves and
how differs by the reason Multi Judge was configured (above): disagreement among
independent Judges says something about the Conversation; variance among repeated
samples of the same Judge says something about that Judge's own stability instead, and
the latter is closer to a Calibration concern than a Consensus one.

## Voting

Voting is one specific Consensus mechanism: converting several Judges' discrete
pass/fail verdicts into one Result by majority or plurality count. It is not the only
way to reach Consensus — an alternative is combining Judges' Confidence-qualified scores
directly, such as a Confidence-weighted average, rather than counting discrete verdicts
— but Voting is the simplest and most auditable, since a Report (Volume XI) can state a
vote count plainly without needing to explain a weighting formula. Voting requires an
odd number of Judges or an explicit tie-breaking rule to avoid an unresolved verdict;
routing a tie to Human Review is the natural choice, consistent with Consensus's
treatment of disagreement above.

## Confidence

Chapter 6 already specified what a Result's Confidence value is used for once it exists
— the Confidence Model that decides whether a Result counts at face value or gets
routed to Human Review. This section specifies how a Judge produces that value in the
first place. A Judge's Confidence MAY come from several sources: the underlying model's
own token-level probability on its verdict, an explicit self-rating the Judge's criteria
instruct it to produce alongside its verdict, or — in a Multi Judge configuration — the
degree of agreement observed across Judges as an indirect signal, though this conflates
with Consensus and MUST be treated as a distinct signal, not a substitute for a Judge's
own stated Confidence. Regardless of source, the Glossary's constraint holds: Confidence
reflects the Judge's own uncertainty in its verdict, not the underlying Quality
dimension's importance (Business Quality weighting, Chapter 2) and not how many other
Judges agreed with it (Consensus).

## Calibration

Calibration checks whether a Judge's stated Confidence values actually track its real
accuracy over time — whether a Judge that reports 90% Confidence is right about 90% of
the time it says so, evaluated against a reference. Unlike Consensus, which resolves
disagreement at assessment time for one Conversation, Calibration operates across many
historical Results, comparing a Judge's own verdicts and Confidence values against
ground truth — ordinarily Human Reviewer Results designated for exactly this purpose
(Volume II — Human Reviewer "MAY be designated as the reference against which a Judge's
Confidence and Judge Drift are measured"). A Judge whose stated Confidence turns out not
to track its accuracy is miscalibrated regardless of how often it is individually
correct — miscalibration is an error in the second axis Chapter 6 named (verdict and
Confidence are separate), not a correctness problem in the first.

## Human Review

Human Review is the process that invokes the Human Reviewer Oracle (Volume II) — this
Volume does not define a separate concept. Four distinct triggers converge on the same
Oracle: a Contract MAY require Human Review routinely for a given Scenario
(safety-critical or high-stakes Business Quality cases, Chapter 2); Chapter 6's
Confidence Model routes a Judge Result below its Contract's Confidence threshold to
Human Review before it is allowed to affect an aggregate; unresolved Consensus
disagreement among independent Judges is itself grounds for Human Review, above; and a
Human Reviewer's Results serve as the reference Calibration and Judge Drift (below)
measure against. A Human Reviewer's own Result MAY carry a Confidence value (Volume II),
assessed the same way a Judge's is, but a Human Reviewer is never itself subject to
Calibration or Judge Drift tracking — those measure a Judge against a Human Reviewer as
ground truth, not the reverse.

## Judge Drift

Judge Drift is to a Judge what Semantic Regression (Volume X) is to the system under
test: a change in behavior, detected against a reference point over time — just applied
one level up, to the Oracle rather than the subject it assesses. Where Calibration asks
whether a Judge's Confidence values are accurate right now, Judge Drift asks whether the
Judge's verdicts or Confidence behavior have changed from what they used to be — whether
yesterday's Judge would still agree with today's Judge on the same evidence. A cluster
of low-Confidence Results concentrated on one Judge, already named in Chapter 6 as a
signal worth surfacing independently of any individual Result, is frequently the first
visible symptom of Judge Drift rather than noise; a sustained divergence from Human
Reviewer agreement over time is a stronger, slower-forming one. Judge Drift is a
Reporting-level concern (Volume XI) in the same way Semantic Regression is: it is
detected by comparison across many Results over time, not read off any single Execution.

---

Together with Volume V, this Volume completes both concrete Oracles the Glossary names —
Validator and Judge — and, through Human Review, brings in the third. Every Result the
Decision Pipeline (Chapter 6) aggregates, regardless of which Oracle produced it, now has
a fully specified origin: deterministic and unconfident by construction (Volume V), or
probabilistic and Confidence-qualified by construction (this Volume), or human and
possibly either (Human Review, above). Part II — Execution is complete once this Volume
is confirmed: Volumes III through VI together specify how a Scenario becomes a Result,
from triggering an Execution to producing the evidence Chapter 6 turns into a decision.
