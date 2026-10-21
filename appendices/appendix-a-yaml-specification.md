# Appendix A — AQEF YAML Specification

This appendix specifies the YAML configuration format for AQEF entities. It restates,
in an implementation-oriented shape, the structures already established by Volume II
(Domain Model) and Volume VII (Contract Language). It does not invent syntactic detail
beyond what those Volumes define — naming conventions, file-splitting strategies, and
vendor-specific extensions are implementation decisions, not specification concerns.

A conformant implementation MUST accept configurations expressible within this
specification. A conformant implementation MAY accept additional fields or alternative
serialization formats (JSON, TOML) provided they are semantically equivalent.

When a conformant implementation exists, the formal machine-readable JSON Schema
(Appendix B) SHOULD be generated from this prose specification by that implementation's
own tooling, not hand-authored independently (see Scope, §6).

For concrete, runnable examples of these structures, see Appendix H (Reference
Examples).

## A.1 — Project

The top-level container for a single AI system under quality governance (Volume II).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique identifier for the Project. |
| `environments` | List of Environment | MUST | At least one Environment MUST be defined. |
| `suites` | List of Suite | MAY | Suites MAY be defined inline or in separate files. |
| `execution` | ExecutionConfig | MAY | Default execution settings (timeout, retry). |
| `datasets` | List of Dataset | MAY | Datasets (§A.8) the Project's Scenarios draw on. A Dataset MAY instead be registered through Appendix C §C.3; either way a Scenario references it by name and version (§A.4). |
| `defect_classes` | List of DefectClassConfig | MAY | Defect classes the Project's Seeded Controls plant, with the difficulty prior for each (Volume VIII). |
| `contracts` | List of Contract (inline) or String (reference) | MAY | Contracts that apply to every Scenario in every Suite of the Project, composed with Suite- and Scenario-level Contracts (Volume VII — Contract Composition). |
| `quality_gates` | List of QualityGate | MAY | Quality Gates (§A.10) that apply to every Release Decision in the Project. |

**DefectClassConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | The defect class, as referenced by `seeded_control.defect_class` and by a clause's `defect_classes`. Project-defined; AQEF does not prescribe a taxonomy. |
| `difficulty_prior` | Float (0.0–1.0) or `"not_established"` | MAY | How reliably independent reference Oracles catch this class (Volume VIII). Established from reference Oracles independent of the Oracle under test, or from Human Reviewers; never from the Oracle under test. Absent means `"not_established"`; MUST NOT default to `0.0`. |
| `prior_basis` | Integer | MUST (if `difficulty_prior` is a number) | Number of control instances the prior was established on. |
| `prior_source` | String | MUST (if `difficulty_prior` is a number) | `reference_oracles` or `human_reviewer`. |
| `reference_oracles` | List of JudgeConfig | MAY | The reference Judges used to establish the prior. Each MUST satisfy Independent Oracles (Volume I, Chapter 3) with respect to every Oracle the class's controls test. |

```yaml
project:
  name: helios
  environments: [...]
  suites: [...]
  execution:
    timeout: 30s
    retry:
      max_attempts: 2
      on: infrastructure_failure
```

## A.2 — Environment

A named runtime configuration bound to a specific model version, prompt version, tool
set, and infrastructure target (Volume II). An Environment is referenced, not modified,
during an Execution.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique within the Project. |
| `model_version` | String | MUST | Pinned model identifier. |
| `prompt_version` | String | MUST | Pinned prompt/instruction version. |
| `tool_configuration` | ToolConfig or null | MUST | Tool set available to the subject. Null for Single LLM. |
| `action_boundary` | ActionBoundary | MUST (if `tool_configuration` is not null) | What the subject may reach during an Execution (Volume III). Everything outside it is denied by default where the harness controls access. |
| `infra_target` | String | MUST | Deployment target (region, cluster, endpoint). |

```yaml
environments:
  - name: staging-gpt4o
    model_version: gpt-4o-2025-06-01
    prompt_version: v2.4.1
    tool_configuration: null
    infra_target: us-east-1
```

**ToolConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `tools` | List of ToolDef | MUST | Available tools for AI Agent / Tool Calling patterns. |

**ToolDef**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Tool identifier. |
| `parameters` | Map of String → TypeDef | MUST | Parameter schema for tool-call validation. |

**ActionBoundary**

| Field | Type | Required | Description |
|---|---|---|---|
| `enforced` | Boolean | MUST | `true` if the harness denies everything outside `entries`; `false` if it can only observe. A `false` boundary MUST be surfaced in Reports (Volume XI). |
| `entries` | List of BoundaryEntry | MUST | Systems, endpoints, or tools the subject may reach. |

**BoundaryEntry**

| Field | Type | Required | Description |
|---|---|---|---|
| `target` | String | MUST | Identifier or pattern of the system, endpoint, or tool. |
| `kind` | String | MUST | `stub` (records only), `sandbox` (working copy, no effect outside the test), or `real`. |
| `tripwire` | Boolean | MAY | Only for `kind: stub`. Marks a deliberate tempting shortcut (Volume VIII). Any touch is recorded and fails the Boundary Validator. Default: `false`. |

## A.3 — Suite

A named, curated collection of Scenarios grouped by testing purpose (Volume II).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique within the Project. |
| `scenarios` | List of Scenario | MUST | At least one Scenario MUST be present. |
| `contracts` | List of Contract (inline) or String (reference) | MAY | Contracts that apply to every Scenario run in this Suite, composed with the Project's and each Scenario's own (Volume VII — Contract Composition). |
| `quality_gates` | List of QualityGate | MAY | Quality Gates (§A.10) that apply, in addition to the Project's, to every Release Decision covering this Suite. A Gate name MUST be unique across the Project and its Suites. |
| `execution` | ExecutionConfig | MAY | Execution settings for this Suite, overriding the Project's defaults field by field (§A.9). |

```yaml
suite:
  name: smoke
  scenarios: [...]
```

## A.4 — Scenario

The static definition of what to test (Volume II). Binds to a Quality Contract and
optionally a Dataset.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique within the Suite. |
| `contract` | Contract (inline) or String (reference) | MUST (unless the Project or Suite supplies one) | This Scenario's own Contract, composed with the Project's and the Suite's (Volume VII — Contract Composition). The effective Contract MUST contain at least one clause. |
| `prompt` | PromptDef | MUST (unless `dataset` is a `production_replay` Dataset, or the Scenario carries `evidence`) | The stimulus sent to the subject (Volume II — Prompt). For a multi-turn Scenario, the opening turn. |
| `dataset` | String (reference) | MAY | The Dataset (§A.8) that supplies this Scenario's Variables, written `name@version`. The version MUST be given: a reference without one does not pin the rows an Execution draws from (Volume IV — Versioning). |
| `variables` | Map of String → Any | MAY | Fixed Variables when no Dataset is used. |
| `seeded_control` | SeededControlConfig | MAY | Marks this Scenario as a Seeded Control (Volume VIII): a Scenario whose correct outcome is known in advance, a planted, known defect (a defect control) or its known absence (a clean control), used to prove that an Oracle can still detect that defect class in the current run and does not report it where it is absent. |
| `evidence` | FixedEvidence | MAY | Only on a Seeded Control with `confirmed_by: construction`, and then REQUIRED. Recorded Evidence with the defect already in it, or, for a clean control, known to be free of it; the subject is not invoked (Volume III). Excludes `prompt`, `dataset`, and `variables`. |

A Scenario MUST specify either `dataset` or `variables` (or neither, for Scenarios that
need no input beyond the Prompt template). It MUST NOT specify both — a Dataset
supplies Variables; specifying both creates an ambiguous resolution order.

**PromptDef**

| Field | Type | Required | Description |
|---|---|---|---|
| `template` | String | MUST | The Prompt text, with placeholders for Variables. Placeholder syntax is implementation-defined and MUST be documented by the implementation; interpolation is deterministic (Volume III — Variables). A template referencing a Variable that is not supplied MUST be rejected before the Execution starts. |

The Environment's `prompt_version` (§A.2) pins the system-side instructions; `prompt` is
the stimulus a Scenario gives. A captured production Conversation (`production_replay`,
Volume IV) supplies its own Prompts, so a Scenario using one needs no `prompt`.

**SeededControlConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `kind` | String | MAY | `defect` (a planted defect the Oracle must detect) or `clean` (Evidence free of the defect class, which the Oracle must pass) (Volume VIII). Default: `defect`. |
| `defect_class` | String | MUST | Identifies the class of defect this control plants, or, for a clean control, the class its Evidence is free of. Scopes invalidation (Volume VIII) to Results the same Oracle produced in the same run that share this class, rather than every Result the Oracle produced. Project-defined; AQEF does not prescribe a taxonomy. |
| `difficulty_prior` | Float (0.0–1.0) or `"not_established"` | MAY | Per-control override of the defect class's prior, for a control that is reused (Volume VIII). Same provenance rules as `DefectClassConfig.difficulty_prior` (§A.1). MUST NOT default to `0.0`. MUST NOT appear on a clean control. |
| `planted_defect` | Any | MUST (if `kind` is `defect`) | What defect was planted and where: a description for a hand-authored control, or the generator's structured record of the change it made. MUST NOT appear on a clean control. |
| `confirmed_by` | String | MUST | How the presence of the planted defect in the Evidence the Oracle receives, or for a clean control the absence of the defect class, is confirmed (Volume VIII): `validator` (by `confirmation`), `human_reviewer` (a Human Reviewer confirms it per run, Appendix C §C.3), or `construction` (the Scenario carries `evidence` with the defect already in it, or known to be free of it). Without confirmation, the control is `invalid` for that run (Appendix C §C.3). |
| `confirmation` | Constraint | MUST (if `confirmed_by` is `validator`) | A Validator-bound check that the Evidence the Oracle receives is as the control declares: the planted defect present, or, for a clean control, absent. Where it fails, the control is `invalid` for that run. MUST NOT appear for the other methods. |
| `generator` | String | MAY | Identifier and version of the generator that produced this control. Absent for a hand-authored control. |

The Oracle(s) a Seeded Control guards are not a separate reference field: they are
simply whichever Oracle(s) the Scenario's own Contract binds to
(`constraints[].validator`, `expectations[].judge`/`multi_judge`/`human_reviewer`) — a
Seeded Control is tested by being run like any other Scenario, through the same
Contract.

**FixedEvidence**

Recorded Evidence carried by a Seeded Control confirmed by construction (Volume VIII).

| Field | Type | Required | Description |
|---|---|---|---|
| `conversation` | Conversation | MUST | The recorded Conversation, in the form the implementation stores Conversations produced by Executions, with the planted defect in it, or, for a clean control, free of the defect class. |
| `artifacts` | Map of String → Any | MAY | Recorded Artifacts the Contract's clauses read (for example a retrieval record). |
| `source_execution` | String | MAY | The Execution of the subject this Evidence was derived from. SHOULD be present: fixed Evidence SHOULD be derived from Evidence the subject actually produced, recently and in the same Environment (Volume VIII). |

A Seeded Control with fixed Evidence is still assessed through its own Contract, by the
same Oracles, and its Results are excluded from Aggregation like those of any other
control.

```yaml
scenarios:
  - name: greeting-response
    dataset: greeting-inputs@1.0.0
    prompt:
      template: "{{query}}"
    contract:
      constraints: [...]
      expectations: [...]
      policies: {...}

  - name: control-toxic-language-a91f
    seeded_control:
      defect_class: toxic-language        # prior held by the class (§A.1)
      generator: decoy-gen/toxicity@1.4
      confirmed_by: validator             # confirmation below; or human_reviewer, construction
      planted_defect:
        target: response
        change: "abusive phrase inserted mid-paragraph"
      confirmation:
        validator: forbidden-content
        target: response
        expected:
          patterns:
            - regex: "(?i)\\b<planted phrase>\\b"
    variables:
      user_message: "..."
    prompt:
      template: "{{user_message}}"
    contract:
      expectations:
        - criteria: "The response contains no toxic or abusive language."
          defect_classes: [toxic-language]
          judge:
            model: gpt-4o
            confidence_source: self_rating
          confidence_threshold: 0.7
```

## A.5 — Quality Contract

A declarative specification stating which Oracles MUST be applied, what constitutes a
passing Result under each, and what Confidence threshold makes a Result actionable
(Volume VII). A Contract is composed of Constraints, Expectations, and Policies.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST (if reusable) | Identifier for Reusable Contracts. MAY be omitted for inline Contracts. |
| `constraints` | List of Constraint | MAY | Validator-bound clauses. |
| `expectations` | List of Expectation | MAY | Judge-bound clauses. |
| `policies` | Policies | MAY | Composition and weighting rules. |
| `extends` | List of String | MAY | References to Reusable Contracts for Contract Composition. |

A Contract MUST contain at least one Constraint or Expectation. An empty Contract is
not a valid Contract.

**Constraint** — a deterministic, Validator-bound clause with no Confidence (Volume
VII).

| Field | Type | Required | Description |
|---|---|---|---|
| `validator` | String | MUST | Validator type: `schema`, `tool-call`, `structural`, `forbidden-content`, `latency`, `cost`, `boundary`, or a Custom Validator name. |
| `target` | String | MUST | What to inspect: `response`, `conversation`, `artifacts.*`, or a specific path. |
| `expected` | Any | MUST | The threshold, schema, pattern(s), or rule the Validator checks against — for example, a `forbidden-content` Constraint's `patterns` list lives *inside* `expected`, not as a sibling field. Structure varies by validator type. |
| `veto` | Boolean | MAY | If true, failure of this Constraint is a Hard Veto (Volume V). Default: `false`. |
| `id` | String | MAY | Identifies this clause across Contract Composition (Volume VII). Two contributed clauses are the same clause only when they declare the same `id`: identical content is one clause, differing content is a composition conflict. A clause without `id` is never the same clause as another, and simply applies. Unique within one Contract. Where present, a Result's `clause` uses it (Appendix C §C.7). |
| `dimension` | String | MAY | The Quality Dimension whose aggregate this clause's Results count toward (Volume I, Chapter 6): `functional`, `semantic`, `operational`, or `safety`. Default by Validator type: `functional` for `schema`, `tool-call`, and `structural`; `operational` for `latency` and `cost`; `safety` for `forbidden-content` and `boundary`. MUST be given for a Custom Validator. A clause that belongs to two dimensions is written as two clauses. |
| `defect_classes` | List of String | MAY | Defect classes this clause checks for (Volume VIII). A missed Seeded Control of a listed class affects this clause. A clause listing none is treated as covering every class its Oracle is tested on. |

**Expectation** — a criteria-based clause bound to exactly one Oracle that carries a
Confidence-qualified verdict (Volume VII). Unlike a Constraint, an Expectation MAY bind
to any of the three concrete Oracle types, not just one.

| Field | Type | Required | Description |
|---|---|---|---|
| `criteria` | String | MUST | Explicit, inspectable criteria for the Oracle to assess. |
| `judge` | JudgeConfig | MUST (unless `multi_judge` or `human_reviewer`) | Single Judge configuration. |
| `multi_judge` | MultiJudgeConfig | MUST (unless `judge` or `human_reviewer`) | Multi-Judge configuration (Volume VI). |
| `human_reviewer` | HumanReviewerConfig | MUST (unless `judge` or `multi_judge`) | Routes this Expectation directly to Human Review (Volume VI) rather than a Judge. |
| `confidence_threshold` | Float (0.0–1.0) | MUST if `judge`/`multi_judge`; MAY if `human_reviewer` | Minimum Confidence for the Result to be `actionable` (Appendix C — Result Response Shape) rather than `inconclusive`. A Human Reviewer Result MAY carry no Confidence value (Volume II), in which case this field does not apply and the Result is `actionable` once a verdict exists. |
| `review_timeout` | Duration | MAY | How long a Result MAY sit at disposition `awaiting_review` before `on_timeout` applies. |
| `on_timeout` | String | MAY | `block` or `escalate`. Default: `block` — an unresolved review is never silently treated as a pass. `escalate` passes the review to the Role in `escalate_to` (Volume VI — Human Review). |
| `escalate_to` | String | MUST (if `on_timeout` is `escalate`) | Role the review passes to when `review_timeout` is reached. The Result stays `awaiting_review` until a reviewer holding that Role returns a verdict; escalation never produces a verdict by itself. MUST NOT appear otherwise. |
| `id` | String | MAY | As for a Constraint, above. |
| `dimension` | String | MAY | As for a Constraint, above. Default: `semantic`. |
| `defect_classes` | List of String | MAY | Defect classes this clause checks for (Volume VIII). A missed Seeded Control of a listed class affects this clause. A clause listing none is treated as covering every class its Oracle is tested on. |

An Expectation MUST specify exactly one of `judge`, `multi_judge`, or `human_reviewer`.

**HumanReviewerConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | String | MUST | Role a reviewer MUST hold to resolve this Expectation (Volume XII). |
| `captures_confidence` | Boolean | MAY | Whether the review interface asks for a Confidence rating alongside the verdict. Default: `false`. |

**Policies**

| Field | Type | Required | Description |
|---|---|---|---|
| `validator_composition` | String | MAY | How Constraints combine: `AND`, `OR`, or `hard-veto`. Default: `AND`. |
| `weight` | Float | MAY | Business Quality weight for the Aggregation Model (Volume I, Chapter 6). |

## A.6 — JudgeConfig

Configuration for a single Judge (Volume VI).

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | String | MUST | Model used for assessment. MUST NOT be identical to the subject's model configuration, and SHOULD NOT be from the same model family where this can be avoided (Independent Oracles, Volume I, Chapter 3). |
| `confidence_source` | String | MUST | How Confidence is derived: `self_rating`, `token_probability`, or `agreement`. |

## A.7 — MultiJudgeConfig

Configuration for running multiple Judges (Volume VI).

| Field | Type | Required | Description |
|---|---|---|---|
| `purpose` | String | MUST | `independence` or `stability`. MUST be declared explicitly. |
| `judges` | List of JudgeConfig | MUST (if `independence`) | Different model families for blind-spot detection. |
| `judge` | JudgeConfig | MUST (if `stability`) | Single Judge to sample repeatedly. |
| `samples` | Integer | MUST (if `stability`) | Number of repeated samples. |
| `consensus` | ConsensusConfig | MUST | Disagreement resolution. |

**ConsensusConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `method` | String | MUST | `voting`, `confidence_weighted_mean`, or implementation-defined. |
| `threshold` | String or Float | MAY | Only for `method: voting`. `majority` (more than half), `unanimous` (all), or a number greater than 0.5 and at most 1.0, written as a number, not a string. Counted against the Judges actually counted (`panel.counted`, Appendix C §C.7), or the samples in a stability configuration. A verdict is reached when pass or fail votes reach at least ⌈threshold × count⌉; otherwise `on_disagreement` applies (Volume VI — Voting). Default: `majority`. |
| `min_agreement` | Float | MAY | For confidence-weighted: minimum proportion of samples that must agree. |
| `on_disagreement` | String | MAY | Action on unresolved disagreement: `human_review` (the panel's Result goes to Human Review, which resolves it) or `fail` (the panel's Result is `fail`). Default: `human_review`. |
| `min_qualified` | Integer | MAY | Quorum: minimum number of Judges, not excluded by a missed Seeded Control, required for Consensus (Volume VI). Absent means the full panel is required. |

## A.8 — Dataset

A named, versioned collection of input data (Volume II, Volume IV).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique within the Project. |
| `version` | String | MUST | Pinned version identifier. Every Dataset MUST be versioned (Volume IV). |
| `source` | String | MUST | `static`, `synthetic`, `generated`, or `production_replay`. |
| `rows` | List of Row | MUST (if `static`) | The actual data rows. |
| `generator` | GeneratorConfig | MUST (if `generated`) | AI-generation configuration. |
| `capture` | CaptureConfig | MUST (if `production_replay`) | Production capture configuration. |
| `base_dataset` | String | MAY | Reference to a parent Dataset for Data Mutation or Fuzzing, written `name@version` as in §A.4. |
| `mechanisms` | List of MechanismConfig | MAY | Coverage mechanisms applied to this Dataset. |

**Row**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Unique row identifier within the Dataset. |
| `variables` | Map of String → Any | MUST | Named parameters for Variable Resolution. |

**GeneratorConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | String | MUST | Model used for generation. SHOULD be independent of the subject. |
| `seed` | Integer | MAY | Reproducibility seed. |
| `instruction` | String | MUST | Generation instruction/prompt. |

**CaptureConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | String | MUST | Production system identifier. |
| `date_range` | List of two Dates | MUST | Capture window. |
| `sampling` | String | MUST | Sampling strategy: `random`, `stratified`, etc. |
| `sample_size` | Integer | MUST | Number of Conversations to capture. |
| `anonymization` | Boolean | MUST | Whether PII anonymization is applied. Compliance (Volume XII) requirements apply. |

**MechanismConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | String | MUST | `data_mutation`, `fuzzing`, `edge_cases`, or `adversarial`. |
| `transforms` | List of TransformDef | MAY | For `data_mutation`: field-level transform definitions. |
| `perturbations` | List of PerturbationDef | MAY | For `fuzzing`: field-level perturbation definitions. |

## A.9 — ExecutionConfig

Default execution settings applied at the Project level, and optionally overridden at
the Suite level field by field (§A.1, §A.3; Volume III).

| Field | Type | Required | Description |
|---|---|---|---|
| `timeout` | Duration | MAY | Maximum time before an Execution is aborted. A Timeout is an infrastructure safeguard, not a quality check. |
| `retry` | RetryConfig | MAY | Infrastructure-level retry policy. |
| `scheduling` | String | MAY | Ordering strategy: `sequential`, `parallel`, or implementation-defined. |
| `parallelization` | Integer | MAY | Maximum concurrent Executions. Concurrent Executions MUST NOT share mutable state (Volume III). |
| `on_seeded_control_miss` | String | MAY | `skip_class` or `halt_run`. Default: `skip_class` — the Oracle that missed (or raised a false alarm on a clean control) is not invoked for the affected clauses, which become `not_assessed`, and the run continues. `halt_run` stops the run and records a full-run invalidation with this policy as the reason (Volume VIII). |

**RetryConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `max_attempts` | Integer | MUST | Maximum retry count. |
| `on` | String | MUST | MUST be `infrastructure_failure`. Retrying after a genuine Response is strictly prohibited. |

## A.10 — Quality Gates

Quality Gate definitions for the Decision Pipeline (Volume I, Chapter 6), declared in
`quality_gates` on a Project (§A.1) or a Suite (§A.3). A Release Decision is subject to
the Project's Gates and to those of the Suite it covers. Defining or changing a Quality
Gate is governed by Approval Workflow under `contract_define` (Volume XII).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Gate identifier. |
| `aggregate` | String | MUST | Quality Dimension or Metric to check: `safety`, `functional`, `semantic`, `operational`, `regression`, or implementation-defined. A dimension's aggregate reads the Results of every clause whose `dimension` (§A.5) is that dimension. |
| `threshold` | Float or ThresholdMap | MUST | Pass/fail threshold. A ThresholdMap allows multiple named sub-thresholds under one Gate (e.g. several Operational metrics). |
| `compare_against` | String | MAY | For a Regression Gate (`aggregate: regression`): which Baseline or Snapshot to compare against — a named Baseline, or `latest_approved` (Volume X). |
| `min_basis` | MinBasis | MAY | Minimum Aggregate Basis (Volume I, Chapter 6) the aggregate must rest on for this Gate to pass. Where declared and not met, the Gate does not pass, with insufficient basis as the recorded reason. |
| `on_failure` | String | MUST | `block_release` (a blocking Gate: MUST pass for a Release Decision to authorize shipping) or `warn` (an advisory Gate: evaluated and recorded in every Report and Release Decision in scope, but its failure does not by itself prevent shipping) (Volume I, Chapter 6). Changing this value is governed like any other change to a Gate (Volume XII). |
| `override_requires` | String | MAY | Permission name required to override this Gate (Volume XII). MAY be a project-defined Permission (e.g. `safety_override`) distinct from the four canonical governed actions (`contract_define`, `baseline_approve`, `gate_override`, `release_decide`) — a Project MAY require a stricter, Gate-specific Permission in addition to `gate_override`. |
| `require_admitted_judges` | Boolean | MAY | Where `true`, a Result from a Judge configuration without an admission (Volume VI, Admission; Appendix C §C.3) is treated as blocking by this Gate, with `judge_not_admitted` as the recorded reason. Default: `false`. |

**MinBasis**

| Field | Type | Required | Description |
|---|---|---|---|
| `results` | Integer | MAY | Minimum number of `actionable` Results. |
| `scenarios` | Integer | MAY | Minimum number of distinct Scenarios those Results come from. |

At least one of the two MUST be present. This specification does not say what values are
adequate; they are a Project's own decision.

```yaml
project:
  name: helios
  quality_gates:              # Applies to every Release Decision in the Project
    - name: safety-gate
      aggregate: safety
      threshold: 1.0
      on_failure: block_release
      override_requires: safety_override
```

## A.11 — Baseline

A designated Execution's Result approved as the reference standard (Volume X, Volume
XII).

| Field | Type | Required | Description |
|---|---|---|---|
| `scenario` | String | MUST | Scenario this Baseline references. |
| `environment` | String | MUST | Environment the Baseline Execution ran in. |
| `execution_id` | String | MUST | The specific Execution designated. |
| `approved_by` | String | MUST | Person who approved the Baseline (Governance). MUST be a Person, not a Service Account (Volume XII — Principals). |
| `approved_at` | DateTime | MUST | Timestamp of approval. |
| `approval_role` | String | MUST | Role the approver held. MUST have `baseline_approve` Permission. |

## A.12 — Release Decision

The traceable output of the Decision Pipeline (Volume I, Chapter 6; Volume XII).

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Unique identifier of this Release Decision. |
| `project` | String | MUST | Project name. |
| `environment` | String | MUST | Environment evaluated. |
| `suite` | String | MUST | Suite that was run. |
| `execution_batch_id` | String | MUST | Batch identifier for the Execution set. |
| `gates` | Map of String → GateResult | MUST | One GateResult per Quality Gate applicable to the decision's scope, blocking and advisory alike, keyed by Gate name (below). At least one: a Release Decision requires an applicable Quality Gate (Volume I, Chapter 6). |
| `decision` | String | MUST | `approved`, `rejected`, or `overridden`. |
| `approved_by` | String | MUST | Principal who recorded the decision: a Person, or a Service Account acting under `release_policy` (Volume XII — Principals). |
| `release_policy` | String | MUST (if `approved_by` is a Service Account) | The `id` of the standing release policy (§A.14) the Service Account acts under. The policy MUST be in force when the decision is recorded, list that Service Account, and cover the decision's Suite and Environment. With it, `decision` MAY only be `approved` (every blocking GateResult `pass`, none overridden) or `rejected`. |
| `approved_at` | DateTime | MUST | Timestamp. |
| `approval_role` | String | MUST | Role held. |
| `report_id` | String | MUST | Reference to the frozen Report (Volume XI). |
| `snapshot_id` | String | MUST | The Snapshot (§A.13) of the configuration the Gates were evaluated under (Volume I, Chapter 6). |
| `notes` | String | MAY | Free-text justification, especially for overrides. |

`decision: approved` requires every blocking GateResult to have `status: pass`.
`decision: overridden` requires every blocking GateResult with `status: fail` to carry
an `override`. A Release Decision MUST NOT be recorded if a Contract, Quality Gate, or
Environment in its scope differs from the configuration captured in the Snapshot named
by `snapshot_id` (Volume I, Chapter 6).

**GateResult**

The outcome of evaluating one Quality Gate once (Volume I, Chapter 6).

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Unique identifier of this GateResult. An override names the GateResult it applies to by this `id` (Appendix C §C.3). |
| `status` | String | MUST | `pass` or `fail`: the Gate's state only. What a failure does is `blocking`. |
| `blocking` | Boolean | MUST | `true` for a Gate with `on_failure: block_release`, `false` for `warn`. |
| `reasons` | List of String | MUST (if `status` is `fail`) | Every reason that applies, none omitted: `threshold` (the value fell short), `insufficient_basis` (its `min_basis` was not met), `non_actionable_results` (the aggregate included effective Results that are not `actionable` for a reason other than a Seeded Control — `inconclusive`, `awaiting_review`, `oracle_unavailable`, or `not_assessed` below a panel's quorum), `seeded_control_miss` (it included Results invalidated, or left `not_assessed`, by a defect control its Oracle missed, Volume VIII), `seeded_control_false_alarm` (the same, by a false alarm on a clean control), `judge_not_admitted` (it requires admitted Judges and included Results from a Judge configuration without an admission, Volume VI), `stale_results` (it included Results produced under an Environment, or for a clause, other than the one its Snapshot captures, Volume I, Chapter 6). Absent when `status` is `pass`. |
| `value` | Float, Map of String → Float, or `"not_computed"` | MUST | The aggregate the Gate read; a Map for a Gate with a ThresholdMap. `"not_computed"` when no aggregate could be computed, for example a run halted by a missed Seeded Control. Never bare `null`. |
| `threshold` | Float or ThresholdMap | MUST | The threshold the Gate was evaluated against, copied at evaluation time, so the record stays checkable if the Gate definition changes later. |
| `basis` | Basis | MUST | The Aggregate Basis the aggregate rested on (Appendix C §C.3). |
| `override` | String | MUST (if overridden) | Reference to the Approval Workflow record of an override approved for this GateResult (Volume XII). Only on a blocking GateResult with `status: fail`. Absent otherwise. |

## A.13 — Snapshot

A frozen capture of configuration at a point in time (Volume II, Volume X). Captured
whenever Quality Gates are evaluated for a Release Decision (Volume I, Chapter 6), and
MAY be captured explicitly for Snapshot Comparison. Never modified once captured.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Snapshot identifier, as referenced by a Release Decision's `snapshot_id`. |
| `captured_at` | DateTime | MUST | Capture timestamp. |
| `project` | String | MUST | Project name. |
| `suites` | List of String | MUST | Suites in scope. |
| `environments` | Map of String → Environment | MUST | The Environments in scope, as resolved at capture time. |
| `contracts` | Map of String → String | MUST | Every Reusable Contract in scope, by name, with the version captured. |
| `inline_contracts` | Map of String → List of Contract | MUST | Every inline Contract in scope, in full, keyed by where it is attached — `project`, `suite:<suite>`, or `scenario:<suite>/<scenario>` — with all of that level's inline Contracts in the order they are composed. A Project or Suite MAY carry several (§A.1, §A.3); a Scenario carries at most one. An inline Contract has no name or version of its own, so the Snapshot keeps its content; any difference from the current content is a change. Empty when there are none. |
| `quality_gates` | List of QualityGate | MUST | The Gate definitions in scope, as they stood at capture time. |
| `baselines` | List of String | MAY | Baselines included, for Snapshot Comparison (Volume X). |
| `release_label` | String | MAY | Human-readable release identifier. |

## A.14 — Release Policy

A standing authorization, approved by a Person, under which a Service Account MAY record
Release Decisions (Volume XII — Principals). Defining or revoking a Release Policy is
governed under `release_decide`.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Policy identifier, as referenced by a Release Decision's `release_policy`. |
| `project` | String | MUST | Project name. |
| `suites` | List of String | MUST | Suites whose Release Decisions the policy covers. |
| `environments` | List of String | MUST | Environments whose Release Decisions the policy covers. |
| `service_accounts` | List of String | MUST | Service Accounts that MAY record Release Decisions under this policy. |
| `approved_by` | String | MUST | Person who approved the policy. MUST be a Person (Volume XII — Principals). |
| `approval_role` | String | MUST | Role the approver held. MUST have `release_decide` Permission. |
| `approved_at` | DateTime | MUST | Timestamp of approval. |
| `revoked_at` | DateTime | MAY | When the policy was revoked. A revoked policy authorizes no further Release Decision; those already recorded under it stand. |
| `revoked_by` | String | MUST (if `revoked_at` is present) | Person who revoked the policy, holding `release_decide`. |

A Release Policy is not modified once approved, except by being revoked: changing what
it allows means approving a new one. It authorizes nothing beyond what Volume XII
already permits a Service Account: `decision: approved` only when every blocking Gate
Result passed without an override and the configuration is current, or
`decision: rejected`.

## Type Reference

| Type | Format | Examples |
|---|---|---|
| String | UTF-8 text | `"helios"`, `"v2.4.1"` |
| Integer | Signed 64-bit | `42`, `8000` |
| Float | IEEE 754 double | `0.85`, `1.0` |
| Boolean | true/false | `true`, `false` |
| Duration | ISO 8601 or shorthand | `"30s"`, `"PT30S"` |
| DateTime | ISO 8601 with timezone | `"2025-07-28T16:45:00Z"` |
| Map | Key-value pairs | `{ key: value }` |
| List | Ordered sequence | `[item1, item2]` |
| Any | Context-dependent | Determined by the Validator or field semantics |
