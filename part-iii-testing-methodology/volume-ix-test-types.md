# Volume IX — Test Types

**Status:** confirmed (v0.1).

*Question answered:* Standard AI testing taxonomy.

Several of the categories below share vocabulary with concepts already defined
elsewhere in AQEF, and needed the same resolution pass Oracle/Validator/Judge already
received before this Volume could be drafted in prose. What follows is a catalog, not an argument: unlike
Chapters 1–7 and Volumes III–VIII, which each build one continuous case, a test-type
taxonomy is a reference list, and the point is to let someone name the check they need
quickly — the same reference style Volume II's Entities section already established.

## Test-Cycle Types

These four name a Suite's purpose and scope — when and why it runs — not a category of
behavior.

**Smoke** — A minimal Suite checking that the system responds at all: the Environment
resolves, an Execution completes, a Response is produced in the expected shape. Its
Contract is deliberately thin; the purpose is fast, cheap confirmation that nothing is
fundamentally broken, run before anything more expensive.

**Functional** — A Suite whose Contracts are built almost entirely from Constraints
(Volume VII) — schema conformance, tool-call correctness, step ordering. This maps
closely to the Functional Quality dimension (Chapter 2), since Functional Quality's
checks are inherently Validator-bound, exactly what a Functional Suite groups together.

**Regression** — A Suite that exists specifically to be compared against history: every
Scenario in it has, or is expected to acquire, a Baseline (Volume II), and its purpose
is catching a Semantic Regression (Volume X) — a Result that now fails what it
previously passed. Regression names the Suite's purpose; Semantic Regression names the
mechanism such a Suite is built to detect.

**Acceptance** — A Suite whose passing is the direct input to a Release Decision
(Chapter 5, Chapter 6): its Contracts encode what "good enough to ship" means for a
Project, drawing on Business Quality weighting (Chapter 2) more heavily than any other
test-cycle type.

## Pattern-Focused Types

These four target the specific mechanisms Chapter 7's architectural patterns and Volume
III's Execution Pipeline introduce — the behavior built on a mechanism, not the
mechanism or the pattern itself.

**Memory** — Tests whether the system correctly retains, recalls, and prioritizes
information across turns: does it still know what the user said three turns ago, does
it weigh recent information appropriately over stale information, does it avoid
inventing a "memory" of something never said. Memory tests the *behavior*; Context
(Volume III) is the *mechanism* that behavior depends on.

**Multi-Turn** *(named "Conversation" in the original outline; renamed)* — Tests dialogue coherence specifically across many turns: topic tracking,
appropriate reference to earlier turns, consistent persona or stance. Distinguished from
Memory by focus: Multi-Turn is about coherence and consistency of the dialogue itself;
Memory is about correct recall of specific prior content.

**Agent** — Tests AI-Agent-pattern-specific behavior (Chapter 7): tool selection
correctness, argument construction, step ordering, and reasoning-trajectory quality.
Distinct from "AI Agent," the architectural pattern itself — this is
the test type that targets it.

**RAG** — Tests RAG-pattern-specific behavior (Chapter 7): retrieval correctness and
grounding faithfulness, checked independently per the retrieval-failure/grounding-
failure split Chapter 7 already drew. Distinct from "RAG," the architectural pattern.

## Safety-Adjacent Types

**Safety** is the umbrella — already a full Quality dimension (Chapter 2), not a sibling
to the five types below it. The other five split into two roles: elicitation technique
(how a bad outcome might get induced) and output category (what the outcome looks like
once produced).

**Jailbreak** *(elicitation technique)* — Attempts to bypass the system's safety
boundaries through direct conversational manipulation: reframing, roleplay, hypothetical
framing, or gradual multi-turn erosion of an initial refusal. Draws on Adversarial
Datasets (Volume IV) and Negative Testing (Volume VIII).

**Prompt Injection** *(elicitation technique)* — Attempts to hijack the system's
behavior through instructions embedded in untrusted secondary content it consumes but
did not receive directly from its primary conversational partner: a retrieved document
(RAG, Chapter 7), a tool's output (Tool Calling, Chapter 7). Distinguished from
Jailbreak by channel, not intent — both aim to induce a boundary violation, but Prompt
Injection's payload arrives through content the system was supposed to trust less than
it apparently did.

**Bias** *(output category)* — The system produces systematically unfair or
discriminatory output, whether or not any adversarial elicitation was involved; Bias can
emerge from an entirely benign Conversation.

**Toxicity** *(output category)* — The system produces harmful, offensive, or otherwise
inappropriate content — the same non-adversarial caveat as Bias.

**Hallucination** *(output category, primarily Semantic Quality)* — The system produces
content unsupported by, or contradicting, the context it was given or the facts of the
matter; RAG's grounding failure (Chapter 7) is a Hallucination instance. Hallucination
sits primarily under Semantic Quality rather than Safety, but MAY be Safety-relevant
depending on domain and consequence — a hallucinated medical dosage is not the same
stakes as a hallucinated release date — so a Contract decides which dimension(s) a given
Hallucination check binds to.

## Operational Types

**Performance** is the umbrella (Operational Quality, Chapter 2); the four below are
sub-types. All four test the *system under test's* behavior under adverse operating
conditions — none describe AQEF's own test-running infrastructure, even where the
vocabulary overlaps.

**Load** — The system's behavior under expected-to-high concurrent usage volume. Not to
be confused with Volume III's Parallelization, which is how AQEF itself runs many
Executions concurrently to test faster — Load tests whether the *subject* holds up
under concurrent traffic, independent of how AQEF happens to be running its own Suite.

**Stress** — The system's behavior at or beyond its stated capacity limits, the point
past which degraded or failing behavior is expected; the concern is whether that
degradation is graceful (an appropriate error, a clear refusal) rather than silent or
unsafe.

**Chaos** — The system's behavior when its own dependencies fail: a tool it calls times
out, a retrieval service errors, an upstream API is unavailable. Not to be confused with
Volume III's Retry, which is how AQEF recovers from a failure in its *own* harness —
Chaos deliberately induces a failure in the *subject's* dependencies to check how the
subject itself responds.

**Cost** — The system's resource or token cost under normal and adverse conditions,
checked against the same threshold a Cost Validator (Volume V) enforces per Execution,
aggregated here at Suite scope.

## Multimodal

Multimodal is a cross-cutting tag, not a sixth category alongside the four above: a
Scenario involving image, audio, or video input or output is typically also Functional,
Safety-adjacent, or another type at the same time, composing rather than replacing it —
the same non-exclusive relationship Hybrid Systems (Chapter 7) already established for
architectural patterns. A Multimodal Scenario's Contract binds the same way any other
Scenario's does; what changes is only the modality of the evidence a Validator or Judge
inspects, not the taxonomy this Volume specifies.

---

Every test type above binds to a Quality dimension Chapter 2 already named and an Oracle
Volumes V and VI already specified — this Volume adds no new Oracle and no new Domain
Model entity, only names for the recurring shapes a Contract's Constraints and
Expectations already take. Volume X (Regression & Baselines) is next: it specifies the
mechanism the Regression type above relies on in full.
