# 8. Terminology

**Status:** confirmed (v0.1).

Conceptual definitions, in dependency order (each term uses only terms already defined).
Structural relationships for these same nouns are specified in Volume II — Domain
Model.

**AI Quality Engineering**
The engineering discipline concerned with establishing, executing, and governing
confidence that an AI system's behavior meets defined quality expectations, given that
such systems are probabilistic subjects run on deterministic infrastructure. It differs
from classical software testing (deterministic input→output equivalence) by requiring
independent Oracles and Confidence-qualified Results, and from ad hoc "AI evaluation"
by requiring a lifecycle, Contracts, and governance rather than one-off benchmarking.

**Quality Contract**
A declarative specification — attached to a Scenario, Suite, or Project — stating which
Oracles MUST be applied to a Conversation, what constitutes a passing Result under each,
and what Confidence threshold makes a Result actionable. A Quality Contract defines what
"quality" means for a piece of behavior; it does not itself check anything.

**Oracle**
The abstract role of "the mechanism that determines whether a Conversation satisfies a
Quality Contract." Oracle is never instantiated directly — it is realized as a
Validator, a Judge, or a Human Reviewer. Every Result MUST be traceable to exactly one
Oracle.

**Validator**
A concrete Oracle performing deterministic, rule-based verification (schema conformance,
forbidden content, structural constraints, latency/cost thresholds). A Validator MUST
return the same Result for the same input, and MUST NOT carry a Confidence value — it
has no uncertainty about its own verdict.

**Judge**
A concrete Oracle performing probabilistic, criteria-based assessment of subjective or
semantic qualities (helpfulness, reasoning correctness, tone, faithfulness). A Judge's
Result MUST carry a Confidence value, reflecting the Judge's own uncertainty in the
verdict — separate from the verdict itself.

**Scenario**
The static, reusable definition of one testable situation: an intent, the Prompt(s) or
Variables that instantiate it, and the Quality Contract that governs it. A Scenario
produces no data by itself; it is realized by an Execution.

**Conversation**
The concrete, ordered transcript of turns (Prompts sent, Responses received) produced
when a Scenario is realized by an Execution. A single-turn Scenario yields a one-turn
Conversation; a multi-turn or agentic Scenario yields a multi-turn Conversation.

**Execution**
The runtime event of running a Scenario (or a Suite of Scenarios) inside a specific
Environment at a specific time. An Execution produces exactly one Conversation, zero or
more Artifacts, and — once Oracles have run — one or more Results.

**Baseline**
A specific past Execution (or its Result) for a given Scenario, explicitly approved as
the reference standard of acceptable behavior. Later Executions of the same Scenario are
compared against it to detect Semantic Regression.

**Semantic Regression**
A degradation, found by comparing a current Execution's Result against its Baseline, in
which a Conversation now fails an Oracle it previously passed — judged by meaning and
intent, not literal text equality, because a correctly-behaving probabilistic system will
rarely reproduce identical output.

**Confidence**
A normalized score, independent of the pass/fail verdict itself, expressing how certain
an Oracle (typically a Judge) is in the Result it produced. Verdict and Confidence are
two separate axes — a Judge can report a failing verdict with low Confidence, or a
passing verdict with high Confidence, and each combination is treated differently when
Results are aggregated into a release-level decision (Volume I, Chapter 6).

**Evaluation**
The process of applying Judges to a Conversation to assess subjective/semantic quality,
producing Confidence-qualified Results. Evaluation is distinguished from **Validation**
(the process of applying Validators): per the Validation-before-Evaluation principle,
Validation always runs first — it is deterministic and cheap — and Evaluation runs after,
since Judges are comparatively slow, costly, and themselves fallible.
