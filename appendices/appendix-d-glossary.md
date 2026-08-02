# Appendix D — Glossary

**Status:** confirmed (v0.1).

This appendix is the complete alphabetical glossary of AQEF terminology. It extends
Front Matter §8 (Terminology), which defines twelve core Domain Model terms in
dependency order. Where a term defined in §8 appears below, its entry provides a brief
restatement for quick reference and directs the reader to §8 for the full, authoritative
definition. All other entries cite the Volume or Chapter where the term is
authoritatively specified.

Tags used throughout: **§8** — full definition in Front Matter §8. **(Principle)** —
one of Volume I, Chapter 3's seven Fundamental Principles. **(Dimension)** — one of
Volume I, Chapter 2's six Quality Dimensions. **(Layer)** — one of Volume I, Chapter 4's
five logical layers. **(Pattern)** — one of Volume I, Chapter 7's architectural
patterns.

---

**Acceptance** — A Test-Cycle type (Volume IX) whose passing is the direct input to a
Release Decision, encoding what "good enough to ship" means for the Scenarios it
covers.

**Adversarial Dataset** — A Dataset (Volume IV) deliberately constructed to defeat the
system under test's Safety or Functional boundaries, used to verify resilience under
hostile input. SHOULD draw on an independent source.

**Agent** — A Pattern-Focused test type (Volume IX) testing AI-Agent-pattern-specific
behavior — tool selection, argument construction, and reasoning trajectory — distinct
from the AI Agent architectural pattern (Volume I, Chapter 7) it targets.

**Aggregation Model** — The mechanism (Volume I, Chapter 6) that combines individual
Results into per-dimension aggregates while preserving Business Quality weights and
Safety's hard-veto behavior, feeding Quality Gates. Distinct from Validator
Composition, which combines Validators within a single clause.

**AI Agent (Pattern)** — An architectural pattern (Volume I, Chapter 7) involving
multi-turn, multi-step branching where intermediate steps — tool calls, reasoning
traces, sub-agent coordination — fall under Functional Quality. Distinct from the Agent
test type (Volume IX).

**AI Quality Engineering §8** — The engineering discipline concerned with
establishing, executing, and governing confidence that an AI system's behavior meets
defined quality expectations. See Front Matter §8 for the full definition.

**AI Test Pattern** — A named, reusable strategy (Volume VIII) for writing an
Expectation or Constraint that checks a relationship or invariant — Metamorphic,
Differential, or Consistency — rather than an exact expected output. Distinct from
architectural patterns (Volume I, Chapter 7) and test types (Volume IX).

**Approval Workflow** — The single mechanism (Volume XII) — request, role-based review,
explicit decision, log — governing all four Governance-controlled actions: defining a
Contract, approving a Baseline, overriding a Quality Gate, and authorizing a Release
Decision.

**Artifact** — Auxiliary data (Volume II) captured during an Execution beyond the
Conversation transcript itself — logs, token-usage records, tool-call traces,
intermediate reasoning — used as additional evidence by Oracles.

**Artifact Collection** — The concurrent capture of Artifacts (Volume III) alongside the
Conversation Engine as an Execution runs.

**Assessment Layer (Layer)** — The logical layer (Volume I, Chapter 4) where Oracles
evaluate Evidence against a Contract to produce Results.

**Audit** — The retrospective query capability (Volume XII) over historical
Governance-controlled actions, answering a broad "what happened" across a Team, action
type, or time range. Distinct from Traceability, which answers a narrow "how did we get
to this specific outcome."

**Baseline §8** — A specific past Execution's Result for a given Scenario, explicitly
approved as the reference standard of acceptable behavior. See Front Matter §8 for the
full definition; see Volume X for the mechanics of Baseline approval and comparison.

**Bias** — A Safety-Adjacent output category (Volume IX) where the system produces
systematically unfair or discriminatory output, checked for regardless of how elicited.

**Boundary Analysis** — A test design technique (Volume VIII) that turns an Edge Cases
Dataset into Scenarios probing a specific, named boundary of the input or output space.

**Business Quality (Dimension)** — The Quality Dimension (Volume I, Chapter 2)
capturing whether the system's behavior serves its actual outcome, dictating how much
weight a failure carries in the Aggregation Model.

**Calibration** — The process (Volume VI) of evaluating whether a Judge's stated
Confidence values accurately track its real performance against ground truth, typically
established by Human Review. Distinct from Judge Drift, which measures change over
time rather than current accuracy.

**Chaos** — An Operational test type (Volume IX) testing the system under test's
behavior when its own dependencies fail unexpectedly.

**CLI** — A thin command-line client (Volume XIV) over the REST API, used primarily by
CI/CD integrations and scripting. MUST NOT introduce logic independent of the REST API.

**Cloud Architecture** — A deployment model (Volume XVII) leveraging managed cloud
infrastructure, independent of whether the topology is Minimal Engine or Enterprise
Engine.

**Compliance** — The verification (Volume XII) of external privacy, regulatory, or
policy requirements, enforced through AQEF's access controls and audit trails. AQEF
makes compliance obligations verifiable without enumerating what a Project must comply
with (see Scope, §6).

**Confidence §8** — A normalized score expressing how certain an Oracle is in the
Result it produced, independent of the pass/fail verdict itself. See Front Matter §8
for the full definition.

**Confidence Model** — The step within the Decision Pipeline (Volume I, Chapter 6) that
decides whether a Result's Confidence is high enough to trust at face value, low enough
to route to Human Review, or ambiguous enough to flag.

**Confidence Threshold** — The minimum Confidence value (Volume VII) an Expectation
clause sets for when a Judge's Result is actionable at face value. A property of
Expectations only — Constraints carry no Confidence to threshold.

**Conformance** — A property of an AQEF implementation — the engine, tooling, or
platform executing this specification — not of any AI system under test (Conformance,
§10). Scoped to claimed capability with a non-negotiable core: the five logical layers
(Volume I, Chapter 4) and the seven Fundamental Principles (Volume I, Chapter 3) bind
every conformant implementation regardless of scope.

**Consensus** — The mechanism (Volume VI) for resolving disagreement among a Multi
Judge configuration's individual Results into a single verdict for an Execution.

**Consistency Testing** — An AI Test Pattern (Volume VIII) that runs the same Scenario
repeatedly within one Environment and checks that outcomes stay within acceptable
bounds of each other, testing Reliability.

**Constraint** — A Quality Contract clause (Volume VII) bound to a Validator,
representing a deterministic, rule-based requirement with no Confidence value attached.
Distinct from Expectation.

**Context** — The accumulating state (Volume III) an Execution builds turn by turn —
prior Prompts, Responses, retrieved documents, tool outputs, agent state — distinct
from Variables (fixed before Execution starts) and Environment (which does not
accumulate at all).

**Contract Composition** — The combination (Volume VII) of Constraints, Expectations,
and Policies from two or more contributing Contracts into one effective Contract.
Conflicting clause values MUST be surfaced, not silently resolved.

**Contract Language** — The declarative grammar (Volume VII) in which a Quality
Contract is expressed, describing what MUST hold rather than how to check it.

**Contracts over Assertions (Principle)** — The principle (Volume I, Chapter 3) that
quality expectations must be expressed as declarative, inspectable Contracts rather
than inline code assertions or ad hoc checks.

**Conversation §8** — The concrete, ordered transcript of turns produced when a
Scenario is realized by an Execution. See Front Matter §8 for the full definition.

**Conversation Engine** — The sub-component (Volume III) that deterministically
orchestrates the Conversation turns based on the Context accumulated so far.

**Cost** — An Operational test type (Volume IX) checking the system's resource or
token cost under normal and adverse conditions.

**Cost Validator** — A built-in Validator (Volume V) checking a completed Execution's
token usage or resource cost against a declared threshold.

**Custom Validator** — A Project-defined deterministic check (Volume V) adhering
strictly to the Validator constraints: same input always produces the same Result, no
Confidence value. A check that internally relies on probabilistic judgment is
structurally a Judge, regardless of labeling.

**Dashboard** — A live, continuously updating view (Volume XI) of Metrics built for
ongoing monitoring. Distinct from a Report, which is frozen at a point in time.

**Data Mutation** — Controlled, intent-preserving transformations (Volume IV) applied
to existing Dataset rows to test generalization under legitimate variation. Distinct
from Fuzzing (non-intent-preserving) and Edge Cases (human-identified boundaries).

**Dataset** — A named, versioned collection (Volume II) of input data used to
instantiate Scenarios at scale through Variable interpolation.

**Dataset Drift** — A change in the Dataset (Volume X) supplying Variables to a
Scenario, correlated with a Semantic Regression.

**Dataset Plugin** — A plugin (Volume XVI) providing new Dataset sources or coverage
mechanisms while adhering to strict versioning requirements.

**Dataset Versioning** — The mechanism (Volume IV) that pins every Dataset's content
over time to ensure reproducible Variable Resolution. Distinct from a Snapshot, which
freezes a wider per-release state.

**Decision Layer (Layer)** — The logical layer (Volume I, Chapter 4) that turns
aggregated Results into Metrics, Reports, and actionable Release Decisions through the
Decision Pipeline.

**Decision Pipeline** — The sequence (Volume I, Chapter 6) that turns computed Metrics
into a Release Decision by applying the Confidence Model, Aggregation Model, and
Quality Gates in order.

**Definition Layer (Layer)** — The logical layer (Volume I, Chapter 4) responsible for
defining what to test and what "acceptable" means — housing Scenarios, Contracts, and
Datasets.

**Deterministic Infrastructure (Principle)** — The principle (Volume I, Chapter 3) that
everything surrounding the AI system — triggering, context assembly, evidence capture,
and storage — must be fully reproducible, even though the AI system itself is
probabilistic.

**Differential Testing** — An AI Test Pattern (Volume VIII) that runs the same Scenario
across two Environments and checks that any behavioral difference is an intentional,
reviewed change rather than an unnoticed regression.

**Distributed Execution** — Parallelization (Volume III) scaled across multiple
machines while maintaining Deterministic Infrastructure guarantees, ensuring no shared
mutable state between Execution processes.

**Drift Detection** — The diagnostic practice (Volume X) of identifying which input
changed to cause a Semantic Regression: Prompt Drift, Model Drift, Dataset Drift, or
Judge Drift (Volume VI). Distinguishing subject drift from Judge Drift requires
checking Human Reviewer agreement.

**Edge Cases Dataset** — A Dataset (Volume IV) deliberately covering human-identified
boundary conditions of the input space, used as input to Boundary Analysis. Distinct
from Fuzzing (undirected) and Data Mutation (intent-preserving).

**Enterprise Engine** — A deployment topology (Volume XVII) running AQEF's logical
layers as independently scaled services. Satisfies the same normative requirements as
a Minimal Engine through different mechanisms.

**Environment** — A named runtime configuration (Volume II) bound to a specific model
version, prompt version, tool set, and infrastructure target. An Environment is
referenced, not modified, during an Execution.

**Evaluation §8** — The process of applying Judges to a Conversation to assess
subjective/semantic quality. Distinguished from Validation (the process of applying
Validators). See Front Matter §8 for the full definition.

**Evidence Layer (Layer)** — The logical layer (Volume I, Chapter 4) responsible for
capturing what actually happened during an Execution — housing Conversations and
Artifacts.

**Everything has Confidence (Principle)** — The principle (Volume I, Chapter 3) that
every Result must explicitly declare its Confidence value or explicitly state that
Confidence is inapplicable (as Validators do), so "unrated" and "deterministically
certain" can never be confused.

**Everything is a Test (Principle)** — The principle (Volume I, Chapter 3) that any
Conversation a Contract can be applied to — including production traffic — is treated
as a valid test, not limited to synthetic lab runs.

**Execution §8** — The runtime event of running a Scenario inside a specific
Environment at a specific time, producing exactly one Conversation, zero or more
Artifacts, and one or more Results. See Front Matter §8 for the full definition.

**Execution Layer (Layer)** — The logical layer (Volume I, Chapter 4) responsible for
reproducibly running Scenarios within an Environment.

**Execution Order** — The principle (Volume V) that Validators run before Judges, and
cheaper Validators run before more expensive ones, to fail-fast and avoid unnecessary
probabilistic assessment.

**Execution Pipeline** — The five-stage internal sequence (Volume III) that turns a
Scenario into a Conversation and Artifacts: Variable Resolution → Prompt Construction →
Conversation Engine → Artifact Collection → handoff to Validators.

**Expectation** — A Quality Contract clause (Volume VII) bound to a Judge or Human
Reviewer, representing a criteria-based statement about subjective or semantic quality
that carries a Confidence-qualified verdict. Distinct from Constraint.

**Exploratory AI Testing** — Unscripted, human-led probing (Volume VIII) of the system
under test to surface failure modes no pre-authored Scenario covers, potentially
producing new Scenarios retroactively.

**Extension Lifecycle** — The process (Volume XVI) governing a plugin from
installation and registration through versioning to deprecation, ensuring deprecated
plugins do not invalidate historical Results they produced.

**Forbidden-Content Validator** — A built-in Validator (Volume V) checking for
disallowed strings, patterns, or tokens as a deterministic safety rule.

**Functional** — A Test-Cycle type (Volume IX) whose Contracts are built almost
entirely from Constraints, checking schema conformance, tool-call correctness, or step
ordering.

**Functional Gate** — A Quality Gate (Volume I, Chapter 6) checking the Functional
Quality aggregate against a defined threshold.

**Functional Quality (Dimension)** — The Quality Dimension (Volume I, Chapter 2)
capturing the structural, mechanically checkable correctness of a response — schema
conformance, required steps, tool-call validity — assessed primarily through
Validators.

**Fuzzing** — Randomized or automated perturbation (Volume IV) of inputs to surface
unexpected behavior or breaking points, without preserving the original input's
intent. Distinct from Data Mutation (intent-preserving) and Edge Cases (targeted).

**Generated Dataset** — A Dataset (Volume IV) expanded or created by an AI model.
SHOULD draw on an independent source to avoid correlated blind spots with the system
under test.

**Hallucination** — A Safety-Adjacent output category (Volume IX) where the system
produces content unsupported by or contradicting its context or facts. Sits primarily
under Semantic Quality (faithfulness) but MAY also be Safety-relevant depending on
domain; a Contract decides which dimension(s) a Hallucination check binds to.

**Hard Veto** — A Validator Composition rule (Volume V) where a single Validator's
failure unconditionally fails the composed result regardless of other Validators'
verdicts. Also applied at the Aggregation Model level for Safety (Volume I, Chapter 6).

**Historical Analysis** — The investigative capability (Volume XI) used to determine
why a Trend moved, by correlating Metric changes against Environment, Dataset, and
Contract version history over time. Distinct from Trend, which shows movement without
explaining it.

**Human Review** — The process (Volume VI) of invoking a Human Reviewer Oracle,
triggered by Contract rules, low Confidence, Consensus disagreement, or Calibration
needs.

**Human Reviewer** — A concrete Oracle (Volume II) — a human performing assessment for
high-stakes decisions, ambiguous cases, or establishing ground truth for Judge
Calibration. Distinct from Human-in-the-loop, which describes a human inside the
system under test's own runtime.

**Human-in-the-loop (Pattern)** — An architectural pattern (Volume I, Chapter 7) where
a human participates in the system under test's own runtime loop — approving actions,
supplying missing information. Unrelated to Human Reviewer despite sharing the word
"Human."

**Hybrid Systems (Pattern)** — An architectural pattern (Volume I, Chapter 7) combining
two or more other patterns — RAG, AI Agent, Tool Calling, Human-in-the-loop — in a
single system under test, composed non-exclusively.

**Independent Oracles (Principle)** — The principle (Volume I, Chapter 3) that an
Oracle must not use the same system, weights, or decision process as the AI system it
evaluates, to avoid correlated blind spots. Extended as a SHOULD to Dataset generation
sources.

**Jailbreak** — A Safety-Adjacent elicitation technique (Volume IX) attempting to
bypass safety boundaries through direct conversational manipulation. Distinguished from
Prompt Injection by channel: Jailbreak manipulates through the primary conversation;
Prompt Injection arrives through untrusted secondary content.

**Judge §8** — A concrete Oracle performing probabilistic, criteria-based assessment
of subjective or semantic qualities, whose Result MUST carry a Confidence value. See
Front Matter §8 for the full definition.

**Judge Drift** — A change (Volume VI) in a Judge's verdicts or Confidence behavior
over time when compared against a reference point. Distinct from Calibration, which
assesses current accuracy rather than temporal change.

**Judge Plugin** — A plugin (Volume XVI) extending the Judge Engine with custom
assessment models, verified for Confidence production and criteria inspectability but
not for determinism (since Confidence variation is expected). Independence remains a
Contract-time judgment.

**KPI** — A curated selection (Volume XI) of existing Metrics elevated to prominent,
ongoing visibility. Must remain traceable back to underlying Results.

**Latency Validator** — A built-in Validator (Volume V) checking a completed
Execution's recorded duration against a declared threshold. Distinct from a Timeout,
which aborts an Execution before completion.

**Load** — An Operational test type (Volume IX) testing the system under test's
behavior under expected-to-high concurrent usage volume.

**Memory** — A Pattern-Focused test type (Volume IX) testing whether the system
correctly retains, recalls, and prioritizes information accumulated in Context (Volume
III) across turns.

**Metamorphic Testing** — An AI Test Pattern (Volume VIII) checking that a defined
relationship holds between an original input and a Data-Mutated variant of it, without
needing a fixed expected output.

**Metric** — A quantified, aggregated measure (Volume II) derived from many Results
across Executions — pass rate, mean Confidence, hallucination rate, cost per Execution,
and so on.

**Minimal Engine** — A simplified deployment topology (Volume XVII) collapsing AQEF's
logical layers into a single process. Satisfies all normative requirements through
simpler mechanisms, not relaxed ones.

**Model Drift** — A change (Volume X) in the underlying model an Environment resolves
to, correlated with a Semantic Regression. May occur with no AQEF-visible Environment
change if a model provider silently updates what a stable identifier resolves to.

**Multi Judge** — A configuration (Volume VI) running more than one Judge against the
same Conversation, serving either of two distinct purposes that MUST be declared:
independence (different model families to catch blind spots) or stability (repeated
sampling to reduce noise). Conflating these produces misleading signals.

**Multi-Agent (Pattern)** — An architectural pattern (Volume I, Chapter 7) where
multiple AI subsystems interact, producing complex Conversations that may require
reconciling results across sub-agents.

**Multi-Turn** — A Pattern-Focused test type (Volume IX) testing dialogue coherence
across many turns. Renamed from "Conversation" to avoid collision with the core Domain
Model noun.

**Multimodal** — A cross-cutting tag (Volume IX) for a Scenario involving image, audio,
or video input/output, composing non-exclusively with other test types.

**Negative Testing** — A test design technique (Volume VIII) deliberately probing what
the system should refuse, decline, or reject, rather than what it should correctly do.

**Operational Quality (Dimension)** — The Quality Dimension (Volume I, Chapter 2)
capturing the system's behavior as a piece of running infrastructure — latency, cost,
throughput — assessed primarily through Validators.

**Oracle §8** — The abstract role of "the mechanism that determines whether a
Conversation satisfies a Quality Contract," realized as a Validator, Judge, or Human
Reviewer. See Front Matter §8 for the full definition.

**Parallelization** — Running multiple Executions concurrently (Volume III) within a
Runtime pool without sharing mutable Context or Variable state between them.

**Performance** — An Operational test type umbrella (Volume IX) covering Load, Stress,
Chaos, and Cost as sub-types.

**Permission** — The atomic capability (Volume XII) to perform one specific, named
Governance-controlled action — such as approving a Baseline or overriding a Quality
Gate. The unit of enforcement, bundled into Roles for convenience.

**Pipeline (CI/CD)** — An external CI/CD platform's own build/deploy pipeline (Volume
XIII) that invokes AQEF and consumes its Quality Gate status. Distinct from AQEF's own
internal pipelines (Execution Pipeline, Validator Pipeline, Decision Pipeline), which
always carry a qualifier.

**Policy** — A Contract-level rule (Volume VII) governing how a Contract's own clauses
combine — Validator Composition logic, Business Quality weighting — rather than a
clause in its own right. Produces no Result of its own.

**Probabilistic Subject (Principle)** — The principle (Volume I, Chapter 3) that the AI
system under test is inherently non-deterministic, and quality tooling must
accommodate rather than restrict this variability.

**Production Replay Dataset** — A Dataset (Volume IV) built by capturing real
production Conversations and folding them back in as Scenarios, enabling the
"Everything is a Test" principle.

**Project** — The top-level container (Volume II) for a single AI system under
quality governance, grouping its Environments, Suites, Datasets, and Contracts.

**Prompt** — The atomic unit of stimulus (Volume II) sent to the AI system within a
Conversation, often populated by Variables at Execution time.

**Prompt Construction** — The Execution Pipeline stage (Volume III) that assembles
resolved Variables into the final Prompt(s) before the Conversation begins.

**Prompt Drift** — A change (Volume X) in the prompt or instructions an Environment
resolves to, correlated with a Semantic Regression.

**Prompt Injection** — A Safety-Adjacent elicitation technique (Volume IX) attempting
to hijack behavior through embedded instructions in untrusted secondary content — a
RAG-retrieved document, a tool's output. Distinguished from Jailbreak by channel.

**Quality Contract §8** — A declarative specification stating which Oracles MUST be
applied, what constitutes a passing Result under each, and what Confidence threshold
makes a Result actionable. See Front Matter §8 for the full definition.

**Quality Gate** — A named, thresholded check (Volume I, Chapter 6) against aggregated
Metrics that must pass to authorize a release. Distinct from a CI/CD platform's own
native gating primitive even where the vendor uses the same word.

**RAG (Architectural Pattern) (Pattern)** — Retrieval-Augmented Generation (Volume I,
Chapter 7): an architectural pattern that retrieves context before generation,
requiring separation of retrieval failures from grounding failures in quality
assessment.

**RAG (Test Type)** — A Pattern-Focused test type (Volume IX) testing RAG-pattern-
specific behavior — retrieval correctness, grounding faithfulness. Distinct from the
RAG architectural pattern it targets.

**Regression** — A Test-Cycle type (Volume IX) whose Suite exists specifically to be
compared against a Baseline to catch a Semantic Regression. Distinct from Semantic
Regression itself, which names the detection mechanism.

**Regression Gate** — A Quality Gate (Volume I, Chapter 6) comparing current Metrics
against a Baseline or Snapshot to detect regressions before release.

**Reliability (Dimension)** — The Quality Dimension (Volume I, Chapter 2) capturing
the stability of the system's behavior across repeated Executions and across time.

**Release Decision** — The culminating output (Volume I, Chapter 6) of the Decision
Pipeline: a go/no-go judgment backed by a Report, Quality Gate results, and an
Approval Workflow record, not merely a claim.

**Report** — A structured, point-in-time presentation (Volume II, Volume XI) of
Metrics and Results. A Report is frozen once generated, making it valid as attached
evidence for a Release Decision. Distinct from a Dashboard, which updates continuously.

**Report Plugin** — A plugin (Volume XVI) introducing new Metric types or visual
formats while maintaining strict traceability back to underlying Results.

**Requirements** — Explicit statements (Volume I, Chapter 5) of expected behavior that
serve as the origin for Quality Contract clauses, produced during the earliest
lifecycle stage.

**REST API** — AQEF's single canonical programmatic surface (Volume XIV) from which
the CLI and all language SDKs are derived. SDKs MUST NOT introduce independent logic
not present in the REST API.

**Result** — The verdict (Volume II) produced by one Oracle applying one Contract
clause to an Execution's evidence. A Result from a Validator carries no Confidence; a
Result from a Judge MUST carry Confidence.

**Retry** — A re-attempt (Volume III) triggered by an infrastructure-level failure
that occurred before the subject produced a genuine Response. Re-running because a
Result came back failing or low-Confidence is strictly prohibited — the original
Result stands.

**Reusable Contract** — A Quality Contract (Volume VII) authored once and attached to
many Scenarios, Suites, or Projects rather than rewritten per Scenario, supporting Test
Maintainability.

**Risk Analysis** — The lifecycle stage (Volume I, Chapter 5) that prioritizes which
behaviors need the most scrutiny before Scenarios are authored. Distinct from
Risk-Based Testing, which acts on that prioritization.

**Risk-Based Testing** — A test design technique (Volume VIII) that concentrates
Scenarios and tighter thresholds on high-stakes behaviors as identified by Risk
Analysis. Distinct from Risk Analysis itself.

**Role** — A named, reusable bundle (Volume XII) of Permissions assigned to a person,
defining what they can do within the scope of a Team. Orthogonal to Team, which
defines what they can see.

**Runtime** — The concrete process (Volume III) that hosts one Execution while it
runs, isolating its state from other Executions. Distinct from Environment, which is
the named configuration the Runtime resolves.

**Safety (Dimension)** — The Quality Dimension (Volume I, Chapter 2) capturing whether
the system stays within acceptable bounds regardless of prompting. Also an umbrella
test-type category (Volume IX) covering Jailbreak, Prompt Injection, Bias, Toxicity,
and Hallucination.

**Safety Gate** — A Quality Gate (Volume I, Chapter 6) checking the Safety aggregate,
typically acting as a hard veto that cannot be overridden without explicit Governance
logging.

**Scalability** — The defined migration path (Volume XVII) allowing a Project to move
from a Minimal Engine to an Enterprise Engine over time without altering historical
Results or Baselines.

**Scenario §8** — The static, reusable definition of one testable situation: an
intent, the Prompt(s) or Variables that instantiate it, and the Quality Contract that
governs it. See Front Matter §8 for the full definition.

**Scheduling** — The layer (Volume III) deciding when and in what order a Suite's
Scenarios are triggered as Executions.

**Schema Validator** — A built-in Validator (Volume V) checking a Response or
tool-call argument against an expected structural format.

**SDK** — Any of the language-specific thin clients (Volume XIV) — Python, Java, C#,
JavaScript/TypeScript, Go — derived from the REST API. SDKs MUST be generated from or
validated against the REST API specification, not hand-authored independently.

**Self-hosted Architecture** — A deployment model (Volume XVII) on infrastructure a
Project itself controls, often driven by Compliance requirements for data that cannot
leave a Project's own systems. Independent of topology choice.

**Semantic Quality (Dimension)** — The Quality Dimension (Volume I, Chapter 2)
capturing whether the meaning of a response is correct and appropriate for the
Scenario's intent, assessed via probabilistic judgment (Judges).

**Semantic Regression §8** — A degradation found by comparing a current Execution's
Result against its Baseline, in which a Conversation now fails an Oracle it previously
passed — judged by meaning, not literal text equality. See Front Matter §8 for the
full definition.

**Single Judge** — The baseline Judge configuration (Volume VI) of one Judge assessing
one Conversation to produce one Confidence-qualified Result.

**Single LLM (Pattern)** — The baseline architectural pattern (Volume I, Chapter 7): a
single-turn Conversation where all Quality Dimensions apply directly without
architectural decomposition.

**Smoke** — A Test-Cycle type (Volume IX): a minimal Suite checking that the system
responds at all, providing fast, cheap confirmation that nothing is fundamentally
broken.

**Snapshot** — A frozen, point-in-time capture (Volume II) of a Project's wider state —
many Baselines plus configuration — used for release-to-release Snapshot Comparison.
Distinct from Dataset Versioning, which tracks one Dataset's own content over time.

**Snapshot Comparison** — Comparing (Volume X) a Project's current state against a
prior Snapshot to detect release-to-release drift across an entire Suite or Project.

**Static Dataset** — A fixed, versioned collection (Volume IV) of rows authored
directly and changed only through explicit, versioned edits.

**Stress** — An Operational test type (Volume IX) testing the system under test's
behavior at or beyond its stated capacity limits.

**Structural Validator** — A built-in Validator (Volume V) ensuring multi-step
Conversations include all required steps in valid order.

**Suite** — A named, curated collection (Volume II) of Scenarios grouped by testing
purpose — such as Smoke, Regression, or Acceptance.

**Synthetic Dataset** — A Dataset (Volume IV) created by mechanically expanding a
template or rule without using an AI model in the loop.

**Team** — An organizational grouping (Volume XII) of people defining the scope of
working access to a Project's Scenarios, Suites, or Contracts. Orthogonal to Role,
which defines what a person can do within that scope.

**Test Maintainability** — The practice (Volume VIII) of keeping a growing Suite
auditable without drifting into loosened assertions, achieved through Reusable
Contracts and Dataset/Contract Versioning.

**Timeout** — An infrastructure safeguard (Volume III) that aborts an Execution
exceeding an expected duration before it can produce a Conversation. A timed-out
Execution produces no evidence to assess. Distinct from a Latency Validator, which
checks a completed Execution's recorded duration.

**Tool Calling (Pattern)** — An architectural pattern (Volume I, Chapter 7) where the
AI system invokes external tools during a Conversation, producing tool-call Artifacts
that fall under Functional Quality via the Tool-Call Validator.

**Tool-Call Validator** — A built-in Validator (Volume V) verifying that a tool
invocation selected a valid tool and supplied conforming arguments.

**Toxicity** — A Safety-Adjacent output category (Volume IX) where the system produces
harmful, offensive, or otherwise inappropriate content, checked for regardless of how
elicited.

**Traceability** — The capability (Volume XII) to reconstruct the full authorization
and provenance chain behind one specific artifact or decision — from a Release
Decision back through its Quality Gate, Report, and underlying Results to the Oracles
and Contracts that produced them. Distinct from Audit, which answers broadly rather
than tracing one chain.

**Trend** — A Metric (Volume XI) plotted across a time range rather than read at a
single point, often surfacing the symptom that Historical Analysis then diagnoses.

**Validation §8** — The process of applying Validators to a Conversation to verify
deterministic, rule-based requirements. Always runs before Evaluation. See Front
Matter §8 for the full definition.

**Validation before Evaluation (Principle)** — The principle (Volume I, Chapter 3)
that cheap, deterministic Validators must run and pass before costly, probabilistic
Judges are invoked, ensuring obvious failures are caught without incurring Judge
overhead.

**Validator §8** — A concrete Oracle performing deterministic, rule-based
verification whose Result MUST NOT carry a Confidence value. See Front Matter §8 for
the full definition.

**Validator Composition** — The combination (Volume V) of multiple Validators'
pass/fail outputs into one boolean verdict for a given Contract clause, using AND, OR,
or Hard Veto logic. Distinct from the Aggregation Model, which combines Results across
Executions and dimensions.

**Validator Pipeline** — The concrete sequence (Volume V) of resolving, ordering, and
composing Validators to produce a Result or short-circuit further assessment.

**Validator Plugin** — A plugin (Volume XVI) extending built-in Validators with a
Project-specific deterministic check, mechanically verified at registration by running
against a fixed input multiple times to confirm determinism.

**Variable Resolution** — The first stage (Volume III) of the Execution Pipeline,
resolving Dataset rows and Scenario-level parameters into concrete named values before
Prompt Construction begins.

**Variables** — Named parameters (Volume II) interpolated into Prompts at Execution
time, sourced from Datasets or Scenario configuration, fixed before the Execution
starts. Distinct from Context, which accumulates during Execution.

**Voting** — A specific Consensus mechanism (Volume VI) that combines Judges' discrete
pass/fail verdicts by majority or plurality count.
