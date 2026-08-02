# Volume I — Architecture & Concepts

**Status:** confirmed (v0.1) — all 8 chapters drafted and consistent with the confirmed
Glossary/Domain Model.

*Question answered:* How should AI Quality Engineering be understood as an engineering
discipline?

---

## Chapter 1 — Why AI Quality Engineering Exists

### Evolution of Software Testing

Software testing has always rested on one assumption: a program computes a specific,
enumerable function, and a test is a boolean comparison between the output that function
actually produced and the output it was specified to produce. Manual testing, unit
testing, integration testing, and end-to-end testing differ in *scope* — how much of the
system is exercised at once — but not in *kind*. Even techniques built to handle large or
unpredictable input spaces stay inside this assumption: property-based testing replaces a
single expected output with an invariant ("output MUST always satisfy property P"), fuzz
testing searches for inputs that violate such an invariant, and snapshot testing defers
the "expected output" decision to a stored artifact instead of an inline literal — but in
every case, a fixed, deterministic oracle exists somewhere, and the test's job is to catch
the moment execution diverges from it. The testing pyramid, contract testing, and
performance/load testing are all refinements of *where* and *how often* this comparison
happens, not a different way of deciding correctness.

### From Deterministic Systems to Probabilistic Systems

Generative AI systems break the assumption that testing has relied on. The same input can
legitimately produce different, equally correct outputs on two separate calls — not
because of a bug, but because sampling, context sensitivity, model updates, and (for
agents) branching decisions are intrinsic to how the subject works. Non-determinism here
is not noise to be engineered away; it is a property of the thing under test. A testing
approach built on "one input, one correct output" has no way to represent this: it either
narrows the definition of "correct" down to a single string (and then fails on harmless
paraphrase or formatting variance), or it abandons precise checking altogether. Neither
resolves the actual problem, which is that the *infrastructure* around the subject —
how a run is triggered, recorded, and judged — can and should stay fully deterministic
and reproducible, even while the subject inside it is not. Keeping that boundary intact
is the basis of the Deterministic Infrastructure / Probabilistic Subject principle
(Chapter 3) and, downstream, of why AQEF separates Execution (a deterministic, reproducible
event) from Conversation (its non-deterministic output).

### Why Traditional QA Fails for AI

Applying classical QA practice to AI systems without adapting it produces a consistent
set of failure modes, not occasional edge cases:

- **Exact-match assertions on natural-language output** fail on any paraphrase, tone
  shift, or formatting change that has no bearing on correctness — producing constant
  false failures that teams learn to ignore.
- **Coverage models built for code branches** do not transfer to a system whose behavior
  emerges from model weights and context rather than enumerable code paths; there is no
  equivalent of "branch coverage" for a prompt.
- **Flaky tests get "fixed" by loosening assertions** until they stop asserting anything
  meaningful (a regex that matches almost any string) — this restores a green build
  without restoring any actual check, which is a worse state than no test at all because
  it is mistaken for one.
- **Classical results are binary**, with no place to express partial certainty. A
  reviewer cannot distinguish "this almost certainly passed" from "this technically
  matched the check but I wouldn't trust it," which is exactly the distinction that
  matters most for a probabilistic subject.
- **Regression detection via literal output diffing** breaks on the first prompt or
  model update, whether or not behavior actually regressed — so teams either drown in
  false regressions or disable regression testing for AI features precisely where a
  safety net is needed most.

Each of these is a direct consequence of trying to run a deterministic testing model
against a probabilistic subject, not a tooling gap that better test frameworks alone can
close.

### AI Evaluation vs AI Quality Engineering

"AI evaluation" — benchmarking a model's outputs against a rubric or reference set,
often via LLM-as-judge scoring — is frequently treated as if it were the whole of AI
quality assurance. It is not; it is one technique that AI Quality Engineering makes use
of, not a substitute for it. A benchmark run in isolation has no Contract defining what
"acceptable" means for a specific piece of behavior, no requirement that its Oracle be
independent of the system it is judging, no Confidence attached to its verdicts, and no
tie to a Baseline or a Release Decision — it produces a score, not a governed quality
gate. AI Quality Engineering is the discipline that wraps evaluation techniques (among
others) inside a lifecycle: a Quality Contract specifies what must hold, one or more
Oracles — Validators, Judges, or Human Reviewers — independently check whether it holds,
each Result carries a Confidence appropriate to its Oracle, and the aggregate feeds an
explicit Release Decision (Chapter 6). Evaluation, in this sense, is a component that can
run *inside* AI Quality Engineering; it is not sufficient by itself to constitute it.

*Terminology note:* this section uses "AI evaluation" in its common industry sense — the
general practice of benchmarking model outputs. This is distinct from the Glossary term
**Evaluation** (`front-matter/08-terminology.md`), which denotes specifically the act of
applying Judges within AQEF's governed lifecycle. The two share a word because the
latter often reuses the techniques of the former (LLM-as-judge, rubric scoring); they are
not otherwise the same thing.

---

## Chapter 2 — Quality Model for AI Systems

### Dimensions of AI Quality

Classical software quality models (functional suitability, performance, reliability,
security, and so on) assume that "correct" is a structural, rule-checkable property of
output. For AI systems, a meaningful share of what makes a response good or bad is a
property of its *meaning* relative to intent — something no fixed rule enumerates in
advance. AQEF's quality model therefore splits AI quality into six dimensions, chosen so
that each maps onto a distinct class of Oracle and a distinct class of check, rather than
folding everything into one undifferentiated "quality score":

| Dimension           | Concern                                                              | Typical Oracle                     |
|---------------------|-----------------------------------------------------------------------|--------------------------------------|
| Functional Quality  | Structural correctness — format, schema, tool calls, required steps   | Validator                            |
| Semantic Quality    | Correctness of meaning relative to intent — accuracy, faithfulness, relevance, tone | Judge                  |
| Operational Quality | Quality as running infrastructure — latency, cost, throughput         | Validator                            |
| Safety              | Staying within acceptable bounds regardless of how the system is prompted | Validator + Judge/Human Reviewer |
| Reliability         | Stability of behavior across repeated Executions and over time        | Metric, aggregated over many Results |
| Business Quality    | How much a given behavior's correctness matters to the outcome it serves | Judge/Human Reviewer + Contract-level weighting |

These dimensions are not mutually exclusive — Safety in particular draws on mechanisms
from both Functional and Semantic Quality — but each requires a different kind of
Oracle and produces a different kind of Result, which is why AQEF treats them as
distinct rather than as one undifferentiated notion of "quality." Chapter 6 (Quality
Decision Model) specifies how Results from different dimensions are aggregated into a
single Release Decision.

### Functional Quality

The structural, mechanically checkable correctness of a response: conformance to an
expected schema or format, correct selection of and correct arguments for a tool call,
presence of all required fields, valid ordering of steps in a multi-step agentic
process. Functional Quality is the dimension classical QA technique transfers to most
directly, because "correct" here is enumerable and rule-based even though the system
producing it is probabilistic — which is exactly why a Validator, not a Judge, is the
appropriate Oracle for it.

### Semantic Quality

Whether the *meaning* of a response is correct and appropriate for the Scenario's
intent: factual accuracy, faithfulness to the context it was given (not introducing
unsupported claims), relevance, coherence, appropriate tone and register, and — for
agentic Scenarios — the quality of the reasoning that produced the final action.
Semantic Quality cannot be reduced to a fixed string or a simple rule; it is the
dimension that motivates the Judge concept in the first place, and its Results
necessarily carry Confidence rather than a bare pass/fail.

### Operational Quality

The quality of the system's behavior as a piece of running infrastructure, independent
of the content it produces: latency, cost per Execution, throughput under concurrent
load, resource consumption, and infrastructure-level error or retry rates. Operational
Quality is deterministically measurable — a latency threshold is a Validator concern,
not a Judge concern — and is where AI Quality Engineering most directly overlaps with
classical performance and load testing (Volume IX).

### Safety

Whether the system's behavior stays within acceptable bounds regardless of how it is
prompted: refusing harmful requests, resisting prompt injection and jailbreak attempts,
avoiding disallowed content categories. Safety is unusual among these six dimensions in
that it typically needs both concrete Oracle types working together — hard,
non-negotiable rules that a Validator can enforce unconditionally, and nuanced,
context-dependent judgment of borderline cases that only a Judge, often backed by a
Human Reviewer for high-stakes Scenarios, can supply. Treating Safety as purely a Judge
criterion underweights the cases that need a Validator's unconditional guarantee;
treating it as purely a Validator's job underweights the cases that need contextual
judgment. Both are necessary, and Volume IX (Safety, Jailbreak, Prompt Injection) draws
on both.

### Reliability

Not the correctness of any single response, but the stability of the system's behavior
across repeated Executions of the same Scenario and across time. A system can produce
an excellent response on one Execution and a poor one on the next with no change to the
input at all — Reliability is the dimension that asks whether that variance itself
stays within acceptable bounds. It is necessarily a Metric-level property, computed by
aggregating many Results rather than by inspecting one, and it is the dimension most
directly tied to Baseline comparison: a Semantic Regression is, by definition, a
Reliability failure detected against a specific reference point (Volume X).

### Business Quality

Whether the system's behavior serves the actual outcome it exists to produce, weighted
by how much that specific behavior matters to the people or business relying on it. Not
every Scenario carries equal stakes: an incorrect response in a rarely-used edge case
and an incorrect response in the system's single most common request are functionally
identical failures but very different Business Quality failures. This dimension is what
lets a Quality Contract express priority rather than a flat pass/fail — attaching a
weight or criticality to a Scenario so that Aggregation and Quality Gates (Chapter 6)
can treat failures differently depending on what is actually at stake, instead of
counting every failing Scenario equally.

---

## Chapter 3 — Fundamental Principles

The seven principles below are what every design decision elsewhere in this
specification can be checked against — where a later Volume's mechanism seems
arbitrary, it should trace back to one of these.

### Contracts over Assertions

Classical testing embeds expectations as inline assertions inside test code —
`assert response == expected` — which couples *what* to check with *how the test
happens to be written*, making expectations hard to reuse, hard to audit independently
of code, and easy to weaken silently (the loosened-regex failure mode from Chapter 1).
AQEF requires expectations to be expressed as a Quality Contract: a declarative,
inspectable artifact, separate from any Execution's implementation, that can be
attached to many Scenarios, reviewed by someone who never touched the test code,
versioned, and audited for drift over time. An inline assertion cannot do any of this
without first being turned into something that is, in substance, already a Contract.

### Validation before Evaluation

Validators MUST run before Judges for a given Execution. Validators
are cheap and deterministic; Judges are comparatively slow, costly, and themselves
fallible — a Judge's own Result carries a Confidence precisely because it can be wrong.
Running Judges first wastes cost and latency assessing Conversations that already fail
a cheap, hard check, and worse, risks producing a misleadingly confident Semantic
Quality verdict on a response that is Functionally broken — a well-reasoned answer
wrapped in a malformed payload nothing downstream can parse. Validation-first is a
fail-fast pattern applied specifically to the split between deterministic and
probabilistic Oracles.

### Independent Oracles

An Oracle MUST NOT be the same system, weights, or decision process as the AI system it
evaluates, and SHOULD NOT share failure modes with it where this can be avoided. A
Judge built from the same model family and prompted similarly to the system under test
risks correlated blind spots: it may fail to notice exactly the errors that system is
prone to, because both draw on the same underlying weaknesses. Independence is what
gives a Result evidentiary value — an Oracle that could plausibly share the fault it is
checking for is not verifying anything; it is echoing.

### Deterministic Infrastructure

Everything surrounding the AI system — how an Execution is triggered, which
Environment it runs in, how a Conversation and its Artifacts are captured, how a
Contract is resolved, how a Result is stored — MUST be fully deterministic and
reproducible. Two Executions of the same Scenario in the same Environment MUST go
through an identical harness, differing only in what the probabilistic subject itself
produces. This is what makes it possible to isolate the true source of any observed
difference: if the infrastructure were not reproducible, an apparent Semantic
Regression could just as easily be an artifact of the harness as a real behavior
change, with no way to tell which.

### Probabilistic Subject

The AI system under test is not required, and generally SHOULD NOT be expected, to
produce identical output for identical input. AQEF does not attempt to make the
subject deterministic — that would mean testing something other than the system
actually being shipped. Every other principle in this chapter instead builds rigor
around a subject that isn't deterministic: Contracts define acceptable variation
rather than a single expected string, Oracles judge meaning rather than diff text, and
Confidence expresses how sure an Oracle is rather than asserting a certainty a
probabilistic system cannot offer.

### Everything is a Test

Any Conversation that a Contract can be applied to is worth treating as a test,
whether or not it originated from a deliberately authored Scenario. Production
traffic, exploratory sessions, and incidental interactions all produce Conversations;
AQEF treats the line between "a test" and "an observed interaction" as a matter of
whether a Contract was applied to it, not a matter of whether a Scenario was written
in advance. This is why Production Replay (Volume IV) treats captured production
interactions as a legitimate Dataset source: folding them back in as Scenarios and
Executions after the fact is the normal path under this principle, not a special case.

### Everything has Confidence

Every Result MUST be explicit about whether Confidence applies to it and, if so, what
value it carries — no Result may simply omit the question and leave a consumer to
guess whether it should be trusted at face value or weighed as one data point among
several. For a Judge or Human Reviewer, this means an actual Confidence score
reflecting genuine uncertainty in the verdict. For a Validator, whose check is
deterministic and carries no epistemic uncertainty to quantify, this means the Result
MUST instead explicitly declare that Confidence does not apply — stating its absence
rather than omitting the field, so "unrated" and "deterministically certain" are never
ambiguous with each other. This is consistent with, not a revision of, the Validator
definition in the Glossary: a Validator still MUST NOT carry a Confidence *value*; its
Result MUST simply be explicit that none applies.

---

## Chapter 4 — AQEF Reference Architecture

### Architectural Overview

AQEF's reference architecture is a closed loop, not a one-way pipeline. Scenarios,
Suites, and Contracts are defined; Executions run them inside an Environment;
Conversations and Artifacts are captured as evidence; Oracles assess that evidence
against its Contract and produce Results; Results aggregate into Metrics, get compared
against Baselines and Snapshots, and feed Reports and Release Decisions. The loop closes
when a Decision-layer output feeds back into the Definition layer — a failure mode
surfaced by a Release Decision should produce a new Scenario or a revised Contract, not
only a report nobody acts on. An architecture that only flows forward is good at
detecting problems; closing the loop is what makes it capable of correcting for them.

### Logical Layers

| Layer | Responsibility | Primary entities | Covered in |
|---|---|---|---|
| Definition | What to test, and what "acceptable" means | Project, Suite, Scenario, Dataset, Contract | Volume II, VII, VIII |
| Execution | Running a Scenario reproducibly | Execution, Environment | Volume III |
| Evidence | Capturing what actually happened | Conversation, Artifact | Volume III |
| Assessment | Deciding whether the Contract was satisfied | Validator, Judge, Human Reviewer, Result | Volume V, VI |
| Decision | Turning many Results into an action | Metric, Baseline, Snapshot, Report | Volume X, XI, Ch. 6 |

These layers are logical, not necessarily physical. A Minimal Engine (Volume XVII) may
collapse several into one process, while an Enterprise Engine may run each as a
separate service; Conformance (Front Matter §10) does not require any particular
physical separation, only that each layer's responsibility is met somewhere.

### Core Components

- **Execution Engine** (Volume III) — triggers Executions, manages runtime concerns
  (scheduling, parallelization, retry, timeouts), produces Conversations via a
  Conversation Engine sub-component, and collects Artifacts.
- **Dataset Engine** (Volume IV) — manages Datasets (static, synthetic, generated,
  production-replay) and supplies Variables to Scenarios at Execution time.
- **Validator Engine** (Volume V) — executes Validators against Evidence per a
  Contract, in the Execution Order that Validation-before-Evaluation requires.
- **Judge Engine** (Volume VI) — executes Judges (single or multi-Judge, with
  Consensus/Voting) and routes to a Human Reviewer where the Contract requires it;
  tracks Judge Drift and Calibration over time.
- **Reporting & Analytics** (Volume XI) — aggregates Results into Metrics, compares
  them against Baselines and Snapshots, and produces Reports.
- **Governance** (Volume XII) — cross-cutting: Teams, Roles, Permissions, and Approval
  Workflow controlling who may define a Contract, approve a Baseline, or authorize a
  Release Decision.

### Component Relationships

The Dataset Engine feeds the Execution Engine with Variables and Prompts. The
Execution Engine produces Evidence (Conversation plus Artifacts), which the Validator
Engine consumes first; only if Validation passes does the Judge Engine run against the
same Evidence (Chapter 3 — Validation before Evaluation). Both engines' Results flow
into Reporting & Analytics, whose output can trigger a Release Decision (Chapter 6)
and/or feed back into the Definition layer — a discovered failure becoming a new
Scenario, consistent with "Everything is a Test" (Chapter 3). Governance does not sit
inside this flow as an information-processing stage; it wraps around it, constraining
who can change a Contract, approve a Baseline, or override a Quality Gate.

### Information Flow

```
Dataset Engine ──(Variables)──► Execution Engine ──► [Environment: runs the Scenario]
                                       │
                                       ├──► Conversation (via Conversation Engine)
                                       └──► Artifact Collection
                                              │
                                              ▼
                                    Validator Engine (runs first)
                                       │
                         fail ◄────────┴────────► pass
                    Result recorded,                │
                    short-circuits here              ▼
                                          Judge Engine (Single/Multi Judge,
                                          Human Reviewer if the Contract requires it)
                                              │
                                              ▼
                                   Reporting & Analytics
                            (Metrics; Baseline/Snapshot comparison)
                                              │
                                              ▼
                                 Report ──► Release Decision
                                              │
                            (new Scenario / revised Contract)
                                              │
                                              ▼
                              back to Dataset Engine / Definition layer
```

Governance is not shown as a stage in this diagram — it is the layer that determines
who is permitted to trigger, approve, or override any step within it.

---

## Chapter 5 — Quality Lifecycle

### The Lifecycle as a Temporal View of the Architecture

Chapter 4 described AQEF's reference architecture as five logical layers — Definition,
Execution, Evidence, Assessment, Decision — and the components occupying each. That
description is deliberately static: it says what exists and how the pieces relate, not
the order in which a specific piece of work moves through them over time. The Quality
Lifecycle is the same architecture read as a process: the sequence of stages a quality
expectation passes through, from the moment it is first identified to the moment a
Release Decision is made — and, per the closed-loop architecture and the "Everything is
a Test" principle (Chapter 3), back again.

The eight stages below do not correspond one-for-one with the five layers, because a
layer is a responsibility and a stage is a unit of process, and one responsibility can
span more than one step in time:

| Stage | Layer (Ch. 4) | Produces |
|---|---|---|
| Requirements | Definition | An explicit statement of expected behavior |
| Risk Analysis | Definition | Prioritization of which behaviors need the most scrutiny |
| Test Design | Definition | Scenarios, Datasets, and attached Quality Contracts |
| Execution | Execution | Triggered Executions inside an Environment |
| Validation | Evidence → Assessment | Validator Results against captured Evidence |
| Evaluation | Assessment | Judge / Human Reviewer Results |
| Reporting | Decision | Metrics, Baseline/Snapshot comparisons, Reports |
| Release Decision | Decision | A go/no-go action, and feedback into the next Requirements pass |

This mapping is what lets Conformance (Front Matter §10) check an implementation against
the architecture without insisting on eight literally separate process steps — an
implementation MAY, for instance, fold Requirements and Risk Analysis into one planning
activity, as long as both responsibilities are met somewhere before Test Design begins.

### Requirements

The lifecycle begins before any Scenario exists: with an explicit statement of what the
AI system's behavior is expected to do, drawn from product intent, policy constraints,
and prior incident history. AQEF does not prescribe a requirements-elicitation
technique — this stage draws on ordinary product and engineering practice, not a novel
AI-specific method — but it does prescribe the destination: a Requirement's role in
AQEF is to eventually become one or more clauses of a Quality Contract (Volume VII), not
to remain a standalone document nothing else checks against. A Requirement that cannot,
even in principle, be phrased as something a Validator, Judge, or Human Reviewer could
assess is not yet specific enough to enter the lifecycle. Requirements need not be
exhaustive or final at this stage — Risk Analysis and Test Design routinely surface gaps
that loop back here — but they MUST be concrete enough to distinguish an acceptable
behavior from an unacceptable one, because that distinction is exactly what a later
Contract clause formalizes.

### Risk Analysis

Not every Requirement deserves equal scrutiny, and Risk Analysis decides how much each
one gets, before Scenarios are authored rather than after. It draws directly on the
Business Quality dimension (Chapter 2): a behavior's likelihood of going wrong and the
severity of the consequence if it does, taken together, determine how many Scenarios
cover it, how tight its Confidence thresholds are, and whether its Contract requires a
Human Reviewer rather than a Judge alone. The output of this stage is prioritization,
not Scenarios — that is Test Design's job — which is worth distinguishing from a
similarly-named but narrower technique: Risk-Based Testing (Volume VIII) is the concrete
practice of authoring Scenario suites using this prioritization as input. Risk Analysis
decides what matters most; Risk-Based Testing is one of the places that decision gets
acted on.

### Test Design

Test Design turns prioritized Requirements into the Definition-layer entities the rest
of AQEF operates on: Scenarios, the Datasets that instantiate them at scale, and the
Quality Contracts attached to each one specifying which Oracles apply and what threshold
makes a Result actionable. This is also where "Everything is a Test" (Chapter 3) has its
most direct consequence: Test Design is not limited to hand-authoring novel Scenarios
from a blank page — folding a captured production Conversation back in as a Scenario,
with a Contract now applied to it retroactively, is an equally valid path through this
stage, not an exception to it (Volume IV — Production Replay). Volume VIII covers the
process, patterns, and specific techniques (boundary analysis, negative testing,
exploratory AI testing) used within this stage in depth; this chapter is concerned only
with Test Design's place in the sequence — after Risk Analysis has set priority, before
any Execution runs.

### Execution

Execution is the first stage where the Probabilistic Subject (Chapter 3) actually runs:
the Execution Engine (Volume III) triggers a Scenario inside a specific Environment,
producing exactly one Conversation and zero or more Artifacts. Everything about *how*
this stage happens — scheduling, retries, timeouts, parallelization — is governed by the
Deterministic Infrastructure principle and MUST be reproducible regardless of what the
subject itself produces. This is the stage at which a Scenario, previously only a
definition, becomes data: the Scenario → Execution → Conversation distinction Volume II
insists on keeping as three separate entities is precisely the distinction between the
previous stage (Test Design), this one, and this one's own output.

### Validation

Once a Conversation and its Artifacts exist, the Validator Engine (Volume V) checks them
against the Functional and Operational Quality clauses of the attached Contract —
deterministically, cheaply, and MUST do so before Evaluation runs, per the
Validation-before-Evaluation principle (Chapter 3). A Conversation that fails
Validation short-circuits here, exactly as Chapter 4's Information Flow diagram shows:
there is no value, and real risk of a misleadingly confident semantic verdict, in asking
a Judge to assess a response a cheap deterministic check has already shown to be
malformed.

### Evaluation

Conversations that pass Validation proceed to the Judge Engine (Volume VI), which
assesses the Semantic Quality clauses of the Contract and, jointly with Validation, the
Safety clauses, producing Confidence-qualified Results. Where the Contract requires it —
high Business Quality stakes, safety-critical Scenarios, or Judge Calibration needs —
this stage also routes to a Human Reviewer, per the Domain Model's treatment of Human
Reviewer as a third concrete Oracle alongside Judge, not a replacement for one. This is
the stage where "AI evaluation" in the informal industry sense (Chapter 1) is actually
performed inside AQEF — but only after Validation has already run, and only within the
boundary a Quality Contract set during Test Design, which is precisely what distinguishes
a governed Evaluation stage from an ungoverned benchmark run.

### Reporting

Results produced by Validation and Evaluation feed Reporting & Analytics (Volume XI),
which aggregates them into Metrics, compares the current Execution's Result against its
Baseline for the same Scenario (Semantic Regression, Volume X), and, at wider scope,
against a Snapshot capturing many Baselines plus configuration at a prior release point.
This stage's output, a Report, is a human-facing artifact and — per Chapter 4 — the
primary evidence Governance (Volume XII) consumes downstream. Reporting is also where
Metric-level properties like Reliability (Chapter 2) first become visible at all, since
Reliability cannot be read off a single Result the way a Functional or Semantic Quality
verdict can.

### Release Decision

The lifecycle's explicit decision point: given a Report, does the AI system's current
behavior meet the bar required to ship? Chapter 6 (Quality Decision Model) specifies the
mechanics of this stage in full — the Aggregation Model that combines Results across
dimensions and Scenarios, and the Quality Gates that turn an aggregate into a ship/no-ship
action — this chapter is concerned only with the stage's place in the sequence: the point
where a Report becomes an action, made under Governance's Approval Workflow (Volume XII),
rather than left as a document nobody acts on. Per Chapter 4's closed-loop architecture,
a Release Decision's output is not only "ship" or "don't ship": a discovered failure mode
SHOULD produce a new Requirement or a revised Contract, feeding back into the next pass
through this same lifecycle — "Everything is a Test" applied at the scale of an entire
Project, not a single Conversation.

### The Lifecycle as a Loop

```
Requirements ──► Risk Analysis ──► Test Design ──► Execution
                                                        │
                                                        ▼
                                                   Validation
                                    fail ◄──────────────┴──────────────► pass
                          Result recorded,                                  │
                          short-circuits here                               ▼
                                                                        Evaluation
                                                                             │
                                                                             ▼
                                                                        Reporting
                                                                             │
                                                                             ▼
                                                                    Release Decision
                                                                             │
                                              (new Requirement / revised Contract)
                                                                             │
                                                                             ▼
                                                 back to Requirements / Risk Analysis
```

The loop is what makes the lifecycle a lifecycle rather than a pipeline: Chapter 4
already established that the architecture's Decision layer feeds back into its
Definition layer, and this diagram is that same statement made concrete at the level of
process stages rather than components. A Project that runs this sequence once and stops
has performed a single quality assessment; a Project that lets Release Decision's output
re-enter Requirements and Risk Analysis is doing AI Quality Engineering in the sense
Chapter 1 defines it — governed, cumulative, and closed-loop rather than a one-off
benchmark.

---

## Chapter 6 — Quality Decision Model

### From Results to a Decision

Chapters 4 and 5 established what exists (Results, Metrics, Reports) and when it gets
produced (the Reporting stage feeding Release Decision). Neither specifies *how* a large
number of individual, heterogeneous Results — spanning multiple Oracles, multiple
Quality dimensions (Chapter 2), and potentially hundreds of Scenarios — collapse into
one ship/no-ship action. That mechanics is this chapter's job: a Decision Pipeline that
runs each Result through a Confidence Model, combines the outcome through an Aggregation
Model, and checks it against one or more Quality Gates, whose combined outcome
constitutes the Release Decision.

### Decision Pipeline

The Decision Pipeline is the specific sequence, inside the Reporting stage (Chapter 5),
that turns already-computed Metrics (Volume XI) into a Release Decision for a given
scope — a Suite, a Project, or a specific release candidate:

1. **Read Metrics** already aggregated by Reporting & Analytics for the scope under
   decision.
2. **Apply the Confidence Model** to the Results underlying those Metrics, so that how
   much each Result is trusted is decided before, not during, aggregation.
3. **Apply the Aggregation Model** to combine Confidence-weighted Results across
   Scenarios and Quality dimensions into per-dimension and overall aggregates.
4. **Evaluate Quality Gates** against those aggregates.
5. **Render the Release Decision** — ship, don't ship, or ship with an explicit,
   Governance-logged exception.

Each step consumes only the output of the one before it; a Decision Pipeline MUST NOT
skip the Confidence Model and aggregate raw pass/fail counts directly, because doing so
would silently discard exactly the information — how sure each Oracle was — that
"Everything has Confidence" (Chapter 3) requires every Result to carry
in the first place.

### Confidence Model

A Validator's Result carries no Confidence value, by definition (Glossary), and the
Confidence Model treats it accordingly: fully binding, with no probabilistic discount,
because the Result already declares Confidence inapplicable rather than merely absent —
there is nothing left to model. A Judge or Human Reviewer's Result
carries a genuine Confidence value, and the Confidence Model is what decides what that
number *does*, not merely what it records:

- At or above the Confidence threshold set on the relevant Contract clause, a Result is
  counted at face value in the Aggregation Model that follows.
- Below that threshold, a Result MUST NOT be silently counted as an ordinary pass or
  fail. It MAY instead be treated as inconclusive and routed to Human Review (Volume VI)
  before it is allowed to affect an aggregate, since a Judge that is not confident in its
  own verdict is exactly the case a Human Reviewer exists to resolve.
- A cluster of low-Confidence Results concentrated on one Scenario or one Judge, rather
  than spread evenly, is itself a signal worth surfacing to Reporting independently of
  any individual Result's disposition — it is frequently the first visible symptom of
  Judge Drift (Volume VI), not merely noise to threshold away.

This is the point in the lifecycle where Confidence stops being a property of one
Result and becomes an input to a decision about many Results at once: the same
Confidence value means something different depending on what surrounds it, which is
precisely why the Confidence Model has to be a distinct step and not folded silently
into Aggregation.

### Aggregation Model

The Aggregation Model combines Confidence-modeled Results — first within a Quality
dimension (Chapter 2), then, where a Quality Gate requires it, across dimensions — into
the aggregates a Quality Gate actually checks. Two properties of the six-dimension model
carry directly into how this combination MUST work:

- **Business Quality weighting.** A Contract's weight or criticality on a given Scenario
  (Chapter 2) determines how much one failing Result there moves an aggregate. A failure
  on a Scenario marked high-stakes MUST count for more than an equally-sized failure on
  a low-stakes one; a flat, unweighted failure count would erase exactly the
  distinction Business Quality exists to preserve.
- **Safety's dual enforcement.** Safety draws on both a Validator's unconditional rules
  and a Judge's or Human Reviewer's contextual judgment (Chapter 2). The Aggregation
  Model MUST keep these two enforcement modes separate rather than blending them into one
  weighted score: a Validator-enforced Safety failure acts as a hard veto on the
  aggregate regardless of how well everything else scored, while Judge- or Human
  Reviewer-assessed Safety findings enter the same weighted combination as other Semantic
  and Business Quality Results. Collapsing the two would let a sufficiently good aggregate
  score outvote a hard safety rule that was never meant to be negotiable in the first
  place.

Aggregation produces one aggregate per Quality dimension, plus, where a Quality Gate
spans more than one dimension, a further combination across those per-dimension
aggregates. Which dimensions a given Gate reads, and at what weight, is a property of
that Gate's own configuration, not a fixed formula this chapter imposes uniformly on
every Suite or Project.

### Quality Gates

A **Quality Gate** is a named, thresholded check against one or more aggregated Metrics
— attached to a Suite, Project, or a specific release candidate — that MUST pass for a
Release Decision to authorize shipping. This chapter is its authoritative definition.

A Project typically runs several Quality Gates, each reading a different aggregate:

- A **Safety Gate**, reading the hard-veto Safety aggregate from the previous section —
  ordinarily configured to allow no exception without an explicit, logged Governance
  override (Volume XII — Approval Workflow).
- A **Regression Gate**, comparing current Metrics against a Baseline (per-Scenario) or
  a Snapshot (the wider, per-release aggregate of Baselines plus configuration) —
  which of the two a given comparison uses is a Regression Gate's own configuration
  detail (Volume X), not a distinction this chapter needs to invent.
- A **Functional Gate**, reading the Functional Quality aggregate — ordinarily the
  strictest and cheapest to evaluate, consistent with Validation-before-Evaluation
  (Chapter 3).
- A **Cost/Operational Gate**, reading Operational Quality aggregates such as latency
  or cost per Execution.

A Release Decision requires every Quality Gate applicable to its scope to pass. Where
one fails, the Decision Pipeline does not silently continue — Governance's Approval
Workflow (Volume XII) is the only path through which a failing Gate can still result in
a "ship" outcome, and any such exception MUST be recorded as an explicit, auditable
override rather than a quiet pass. The same Gate is what a Report surfaces for human
visibility (Volume XI) and what a CI/CD pipeline queries to decide whether a deployment
may proceed (Volume XIII) — one mechanism, viewed from two places, not two different
things wearing the same name.

### The Decision Pipeline as a Whole

```
Metrics (Volume XI)
     │
     ▼
Confidence Model ──── low-Confidence Results below the Contract's
     │                 threshold routed to Human Review (Volume VI)
     │                 instead of counted directly
     ▼
Aggregation Model ─── Business Quality weight applied per Scenario (Ch. 2);
     │                 Safety: Validator failures act as a hard veto,
     │                 kept separate from the weighted combination elsewhere
     ▼
Quality Gate(s) ───── e.g. Safety Gate, Regression Gate (vs. Baseline/
     │                 Snapshot, Volume X), Functional Gate, Cost Gate
     │
  fail ◄──────────────────────┴──────────────────────► pass (all applicable Gates)
     │                                                        │
     ▼                                                        ▼
Release Decision: don't ship                       Release Decision: ship
  (or: Governance-logged                                       │
   override, Volume XII)                                       │
     │                                                          │
     └───────────────────────► feedback into Requirements ◄─────┘
                                 / Risk Analysis (Chapter 5)
```

A Quality Gate that fails is not the end of the lifecycle any more than a failing
Validation was in Chapter 5 — it is, again, a fail-fast short-circuit, and per Chapter
4's closed-loop architecture and Chapter 5's own closing loop, its most useful output is
not the "no" itself but what that "no" turns into: a new Requirement, a revised
Contract, or a corrected Baseline, feeding the next pass through the lifecycle rather
than a report that gets read once and set aside.

---

## Chapter 7 — Architectural Patterns

### One Architecture, Several Shapes

Everything specified so far — the Domain Model (Volume II), the Quality Model (Chapter
2), the Fundamental Principles (Chapter 3), the Reference Architecture (Chapter 4), the
Quality Lifecycle (Chapter 5), and the Quality Decision Model (Chapter 6) — is written to
hold regardless of what kind of AI system a Scenario targets. This chapter adds no new
principle and no new Domain Model entity; it walks through seven common shapes an AI
system takes and, for each, asks the same question: given everything already specified,
what does this shape change about which Quality dimensions matter most, what an
Execution's Conversation and Artifacts actually contain, and where a Quality Gate needs
pattern-specific configuration rather than a one-size-fits-all default?

| Pattern | Conversation / Execution shape | What changes |
|---|---|---|
| Single LLM | One-turn Conversation | Baseline case — all six dimensions apply directly |
| RAG | One-turn (or few) Conversation + retrieved-context Artifact | Faithfulness to retrieved context becomes a first-class Semantic Quality concern |
| AI Agent | Multi-turn, multi-step, branching Conversation | Functional Quality covers intermediate steps; Semantic Regression compares trajectories |
| Multi-Agent | Inter-agent sub-conversations + user-facing Conversation | Coordination/handoff correctness; Independent Oracles risk compounds |
| Human-in-the-loop | Turns interleave AI and human input | The system's *own* use of human input becomes testable |
| Tool Calling | Turns include tool-call Artifacts | Tool selection/arguments are Validator-checkable; call cost/latency is Operational Quality |
| Hybrid Systems | Composition of the above | No new dimension or entity — Contract Composition (Volume VII) combines existing clauses |

### Single LLM

The simplest pattern, and the one the rest of this document has implicitly assumed by
default: a Scenario that produces exactly one Prompt and receives exactly one Response,
yielding a one-turn Conversation (Volume II). All six Quality dimensions (Chapter 2)
apply without modification, and Reliability analysis is comparatively simple, since
there is no intermediate trajectory to account for — only the final Response varies
across repeated Executions of the same Scenario. Every other pattern below is naturally
described as "Single LLM plus one added mechanism," which is why it is worth naming
explicitly rather than leaving implicit.

### RAG (Retrieval-Augmented Generation)

RAG adds a retrieval step ahead of generation: before producing a Response, the AI
system retrieves supporting context from an external source, and that retrieved content
becomes part of the Execution's evidence — captured as an Artifact alongside the
Conversation, not folded silently into the Response itself. This matters because it
splits what would otherwise look like one failure into two independently diagnosable
ones: a **retrieval failure** (the wrong or incomplete context was retrieved, checkable
by a Validator against the retrieved Artifact directly) and a **grounding failure** (the
right context was retrieved, but the Response is not faithful to it — a Semantic Quality
concern requiring a Judge to compare the Response against the Artifact, not against
general world knowledge). Faithfulness, already named as a Semantic Quality concern in
Chapter 2, is the dimension RAG relies on most heavily, precisely because it is the
dimension that distinguishes "correct" from "merely plausible-sounding" once a specific,
inspectable context has been supplied.

*Terminology note:* "RAG" here names an architectural pattern — what kind of system is
under test. Volume IX's planned "RAG" test type names a testing technique — how such a
system gets tested. The pattern motivates the technique; they are not the same thing,
the same relationship Chapter 1 draws between "AI evaluation" and "Evaluation."

### AI Agent

An AI Agent Scenario is realized by a multi-turn or multi-step Execution: the Domain
Model already anticipates this directly — "a multi-turn or agentic Scenario yields a
multi-turn Conversation" (Volume II) — and this pattern is where that clause actually
applies. Two consequences follow that do not arise for Single LLM or RAG:

- **Functional Quality extends inward.** It is no longer only the final Response that
  must conform to a schema or complete a required step; intermediate tool selections,
  argument construction, and step ordering are themselves Functional Quality concerns,
  exactly as Chapter 2 anticipated ("valid ordering of steps in a multi-step agentic
  process").
- **Semantic Regression compares trajectories, not literal sequences.** Because
  branching decisions are intrinsic to how an agent works (Chapter 1 — Probabilistic
  Subject), two Executions of the same Scenario MAY legitimately reach an equally
  acceptable outcome by different intermediate paths. A Baseline comparison (Volume X)
  for an AI Agent Scenario MUST therefore be capable of judging the outcome and the
  reasoning quality of a trajectory as a whole, not require step-for-step identity with
  the Baseline's own path — the same Probabilistic Subject principle applied one level
  up, from output text to output trajectory.

*Terminology note:* the same distinction as RAG applies here — "AI Agent" names the
pattern; Volume IX's planned "Agent" test type names the testing technique for it.

### Multi-Agent

Multi-Agent extends AI Agent by having more than one AI subsystem cooperate — or
compete — within a single Execution. What one Execution produces is no longer a single
Conversation in the simple sense: it typically includes a user-facing Conversation plus
one or more inter-agent sub-conversations, all captured as Artifacts (or sub-
conversations) of that same Execution, so that a Validator or Judge can inspect not just
the final user-facing outcome but which agent produced which intermediate contribution.
This pattern is also where the Independent Oracles principle (Chapter 3) is most likely
to be violated by accident: if several of the cooperating agents, and the Judge
assessing their combined output, are drawn from the same underlying model family, a
correlated blind spot can now occur at two levels simultaneously — between agents, and
between the agents and their own Oracle — which is exactly the failure mode Independent
Oracles exists to rule out.

### Human-in-the-loop

Human-in-the-loop describes an AI system whose own operational loop includes a human —
approving an action before it executes, supplying information the system is missing, or
resolving an ambiguity the system surfaces rather than guesses at. This is deliberately
a different concept from the **Human Reviewer** Oracle (Volume II): a Human Reviewer is
part of *AQEF's own assessment process*, evaluating a Conversation from outside, after
the fact; the human in a Human-in-the-loop *pattern* is part of the system under test's
own runtime behavior, and their input becomes a Prompt or an Artifact within the
Conversation being assessed, not an Oracle assessing it. The two can coexist without
conflict — a Human Reviewer MAY be the Oracle used to assess a Conversation that itself
contains human-in-the-loop turns — but the document must not use "human" to mean either
one loosely.

Quality-wise, this pattern shifts part of the system's correctness onto a human
judgment AQEF does not directly govern, but it does not put the AI system's own behavior
out of scope: whether the system correctly incorporates the human's correction,
correctly recognizes when it should request human input rather than proceed on low
confidence in its own reasoning, and correctly resumes afterward are all Functional and
Semantic Quality concerns like any other turn in the Conversation.

### Tool Calling

Tool Calling describes an AI system that invokes external tools or functions — APIs,
code execution, database lookups — as part of producing a Response. Each tool
invocation and its result is captured as an Artifact (Volume II's Artifact definition
already names "tool-call traces" as a canonical example), which makes tool selection and
argument construction directly Validator-checkable, and the cost or latency of external
calls a straightforward Operational Quality concern. Tool Calling is not a subset of AI
Agent, nor the reverse: a Single LLM Scenario MAY include exactly one deterministic tool
call within an otherwise one-turn interaction, and an AI Agent's multi-step reasoning
does not strictly require any external tool at all. The two patterns commonly combine —
most AI Agents call tools — but AQEF treats them as independent concerns so that a
Scenario can specify precisely which mechanisms actually apply to it, rather than
inheriting an entire pattern's worth of assumptions from a superficially similar one.

### Hybrid Systems

Real systems routinely combine several of the above within a single Project, or even a
single Scenario — an AI Agent that uses RAG for a research step, calls a tool to execute
the resulting plan, and pauses for human approval before a high-stakes action. AQEF does
not need a new Quality dimension, a new Domain Model entity, or a new Oracle type to
cover this case: a hybrid Scenario's Quality Contract simply composes the relevant
clauses from each pattern it draws on, which is precisely what Contract Composition
(Volume VII) exists for. That Hybrid Systems requires no new mechanism, only
configuration of the ones already specified, is itself a check on whether the
architecture (Chapter 4) and the Quality Model (Chapter 2) were pitched at the right
level of abstraction in the first place — if hybrid systems had required new machinery,
that would have been a sign the earlier chapters drew their boundaries in the wrong
place.

---

## Chapter 8 — Summary

This Volume set out to answer one question: how should AI Quality Engineering be
understood as an engineering discipline? The seven chapters above answer it in order,
each depending only on what came before:

| Ch. | Question | Answer in one line |
|---|---|---|
| 1 | Why does AI Quality Engineering exist? | Classical testing assumes a deterministic subject; generative AI breaks that assumption, not by accident but by design |
| 2 | What does "quality" mean for an AI system? | Six distinct dimensions — Functional, Semantic, Operational, Safety, Reliability, Business — each needing a different kind of Oracle |
| 3 | What rules bind every later Volume? | Seven principles: Contracts over Assertions, Validation before Evaluation, Independent Oracles, Deterministic Infrastructure, Probabilistic Subject, Everything is a Test, Everything has Confidence |
| 4 | How do the pieces fit together? | Five layers — Definition, Execution, Evidence, Assessment, Decision — and a closed loop, not a one-way pipeline |
| 5 | In what order does work move through it? | Eight stages, Requirements through Release Decision, feeding back into Requirements again |
| 6 | How does a pile of Results become one decision? | A Confidence Model, then an Aggregation Model, then one or more Quality Gates |
| 7 | Does this hold for every kind of AI system? | Yes — Single LLM, RAG, AI Agent, Multi-Agent, Human-in-the-loop, Tool Calling, and Hybrid Systems all configure the same mechanism rather than requiring new ones |

Two things are worth naming explicitly about what kind of answer this Volume gives.
First, nothing in Chapters 2 through 7 is independent of Chapter 3: the six dimensions,
the five layers, the eight stages, the three-part Decision Pipeline, and the seven
patterns are all applications of the same seven principles, not separate ideas that
happen to coexist. Second, this Volume is deliberately conceptual, not operational: it
does not specify a YAML or JSON schema (Appendices A, B), a REST API (Appendix C), or a
reference implementation (Volume XVII). Those choices — how a Quality Gate's threshold
is expressed as data, which Validators ship built-in, what a Suite looks like as a file
— are exactly the kind of thing Chapter 3's principles constrain without dictating, and
they belong in the Volumes and Appendices built to make them, not here.

Volume II gives these same concepts their structural form — the entities, not the
argument for why they take this shape. Between the two, Part I (Foundations) is now
complete: the discipline has been argued for, its quality model fixed, its principles
named, its architecture, lifecycle, and decision model laid out, its patterns checked,
and its nouns given precise relationships. Everything from Part II onward — the
Execution, Dataset, Validator, and Judge Engines; the testing methodology; the
enterprise and extensibility concerns — is this same foundation made concrete, one
component at a time, and is expected to stay accountable to it rather than reopen it.

The distinctions drawn along the way are not restated here, but they are part of what
this Volume actually committed to — later Volumes touching the same terms (Risk-Based
Testing, Quality Gates, Agent and RAG test types, Human Reviewer) inherit them, not just
the prose above.
