# Appendix A — AQEF YAML Specification

**Status:** confirmed (v0.1).

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

## A.3 — Suite

A named, curated collection of Scenarios grouped by testing purpose (Volume II).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Unique within the Project. |
| `scenarios` | List of Scenario | MUST | At least one Scenario MUST be present. |

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
| `contract` | Contract (inline) or String (reference) | MUST | Quality Contract governing this Scenario. |
| `dataset` | String (reference) | MAY | Reference to a named Dataset for data-driven instantiation. |
| `variables` | Map of String → Any | MAY | Fixed Variables when no Dataset is used. |

A Scenario MUST specify either `dataset` or `variables` (or neither, for Scenarios that
need no input beyond the Prompt template). It MUST NOT specify both — a Dataset
supplies Variables; specifying both creates an ambiguous resolution order.

```yaml
scenarios:
  - name: greeting-response
    dataset: greeting-inputs
    contract:
      constraints: [...]
      expectations: [...]
      policies: {...}
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
| `validator` | String | MUST | Validator type: `schema`, `tool-call`, `structural`, `forbidden-content`, `latency`, `cost`, or a Custom Validator name. |
| `target` | String | MUST | What to inspect: `response`, `conversation`, `artifacts.*`, or a specific path. |
| `expected` | Any | MUST | The threshold, schema, pattern(s), or rule the Validator checks against — for example, a `forbidden-content` Constraint's `patterns` list lives *inside* `expected`, not as a sibling field. Structure varies by validator type. |
| `veto` | Boolean | MAY | If true, failure of this Constraint is a Hard Veto (Volume V). Default: `false`. |

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
| `on_timeout` | String | MAY | `block` or `escalate`. Default: `block` — an unresolved review is never silently treated as a pass. |

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
| `threshold` | String | MAY | For voting: `majority`, `unanimous`, or a numeric fraction. |
| `min_agreement` | Float | MAY | For confidence-weighted: minimum proportion of samples that must agree. |
| `on_disagreement` | String | MAY | Action on unresolved disagreement: `human_review`, `fail`, or `flag`. Default: `human_review`. |

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
| `base_dataset` | String | MAY | Reference to a parent Dataset for Data Mutation or Fuzzing. |
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

Default execution settings applied at the Project or Suite level (Volume III).

| Field | Type | Required | Description |
|---|---|---|---|
| `timeout` | Duration | MAY | Maximum time before an Execution is aborted. A Timeout is an infrastructure safeguard, not a quality check. |
| `retry` | RetryConfig | MAY | Infrastructure-level retry policy. |
| `scheduling` | String | MAY | Ordering strategy: `sequential`, `parallel`, or implementation-defined. |
| `parallelization` | Integer | MAY | Maximum concurrent Executions. Concurrent Executions MUST NOT share mutable state (Volume III). |

**RetryConfig**

| Field | Type | Required | Description |
|---|---|---|---|
| `max_attempts` | Integer | MUST | Maximum retry count. |
| `on` | String | MUST | MUST be `infrastructure_failure`. Retrying after a genuine Response is strictly prohibited. |

## A.10 — Quality Gates

Quality Gate definitions for the Decision Pipeline (Volume I, Chapter 6).

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | MUST | Gate identifier. |
| `aggregate` | String | MUST | Quality Dimension or Metric to check: `safety`, `functional`, `semantic`, `operational`, `regression`, or implementation-defined. |
| `threshold` | Float or ThresholdMap | MUST | Pass/fail threshold. A ThresholdMap allows multiple named sub-thresholds under one Gate (e.g. several Operational metrics). |
| `compare_against` | String | MAY | For a Regression Gate (`aggregate: regression`): which Baseline or Snapshot to compare against — a named Baseline, or `latest_approved` (Volume X). |
| `on_failure` | String | MUST | `block_release` or `warn`. |
| `override_requires` | String | MAY | Permission name required to override this Gate (Volume XII). MAY be a project-defined Permission (e.g. `safety_override`) distinct from the four canonical governed actions (`contract_define`, `baseline_approve`, `gate_override`, `release_decide`) — a Project MAY require a stricter, Gate-specific Permission in addition to `gate_override`. |

```yaml
quality_gates:
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
| `approved_by` | String | MUST | Person who approved the Baseline (Governance). |
| `approved_at` | DateTime | MUST | Timestamp of approval. |
| `approval_role` | String | MUST | Role the approver held. MUST have `baseline_approve` Permission. |

## A.12 — Release Decision

The traceable output of the Decision Pipeline (Volume I, Chapter 6; Volume XII).

| Field | Type | Required | Description |
|---|---|---|---|
| `project` | String | MUST | Project name. |
| `environment` | String | MUST | Environment evaluated. |
| `suite` | String | MUST | Suite that was run. |
| `execution_batch_id` | String | MUST | Batch identifier for the Execution set. |
| `gates` | Map of String → GateResult | MUST | Per-gate pass/fail/warn status with aggregate values. |
| `decision` | String | MUST | `approved`, `rejected`, or `overridden`. |
| `approved_by` | String | MUST | Person who made the decision. |
| `approved_at` | DateTime | MUST | Timestamp. |
| `approval_role` | String | MUST | Role held. |
| `report_id` | String | MUST | Reference to the frozen Report (Volume XI). |
| `notes` | String | MAY | Free-text justification, especially for overrides. |

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
