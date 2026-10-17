# Appendix E — UML Diagrams

This appendix provides UML class diagrams visualizing the structural relationships
defined across the specification. Each diagram restates — in visual form — what the
referenced Volumes specify in prose; the Volumes remain authoritative. Diagrams use
Mermaid syntax for inline rendering.

## E.1 — Domain Model: Core Entities

The complete entity graph from Volume II, with the levels at which Contracts and Quality
Gates attach (Appendix A §A.1, §A.3). Arrows read as "owns," "produces," or
"references." `Result`'s fields are abbreviated here for diagram readability — Appendix
C §C.7 is the authoritative shape. A Result may name, in `resolves`, an earlier Result
for the same Execution and clause (Volume I, Chapter 6 — Result Resolution).

```mermaid
classDiagram
    class Project {
        +name : String
    }
    class Suite {
        +name : String
    }
    class Scenario {
        +name : String
    }
    class Contract {
        +name : String
    }
    class Dataset {
        +name : String
        +version : String
        +source : DatasetSource
    }
    class Prompt {
        +template : String
    }
    class Environment {
        +name : String
        +model_version : String
        +prompt_version : String
        +tool_configuration : ToolConfig
        +action_boundary : ActionBoundary
        +infra_target : String
    }
    class Variables {
        +values : Map
    }
    class Execution {
        +id : String
    }
    class Conversation {
        +turns : List~Turn~
    }
    class Artifact {
        +type : String
        +data : Any
    }
    class Result {
        +id : String
        +clause : String
        +oracle : String
        +resolves : String
        +verdict : PassFail
        +confidence : Float
        +disposition : Disposition
        +recorded_at : DateTime
    }
    class Metric {
        +name : String
        +value : Float
    }
    class QualityGate {
        +name : String
        +aggregate : String
        +on_failure : String
    }
    class Baseline {
        +approved_by : String
        +approved_at : DateTime
    }
    class Report {
        +id : String
        +generated_at : DateTime
    }
    class Snapshot {
        +id : String
        +captured_at : DateTime
    }

    Project --> Suite : owns
    Project --> Environment : owns
    Project --> Dataset : holds
    Project --> Contract : attaches
    Suite --> Contract : attaches
    Project --> QualityGate : declares
    Suite --> QualityGate : declares
    Suite --> Scenario : contains
    Scenario --> Contract : governed by
    Scenario --> Prompt : sends
    Scenario --> Dataset : instantiated by
    Dataset --> Variables : supplies
    Prompt --> Variables : interpolates
    Scenario --> Execution : realized by
    Execution --> Environment : runs in
    Execution --> Conversation : produces
    Execution --> Artifact : captures
    Execution --> Result : yields
    Result --> Metric : aggregates into
    Result --> Baseline : designated as
    Metric --> Report : presented in
    QualityGate --> Report : shown in
    Baseline --> Snapshot : composed into
    Report --> Snapshot : may reference
```

## E.2 — Oracle Hierarchy

The three concrete Oracle types and their relationship to Contracts, Results, Seeded
Controls, and requalification (Volume II, Volume V, Volume VI, Volume VIII).

```mermaid
classDiagram
    class Oracle {
        <<abstract>>
        +evaluate(evidence) Result
    }
    class Validator {
        +target : String
        +evaluate(evidence) Result
    }
    class Judge {
        +criteria : String
        +confidence_source : String
        +evaluate(evidence) Result
    }
    class HumanReviewer {
        +role : String
        +evaluate(evidence) Result
    }
    class Result {
        +oracle : String
        +verdict : PassFail
        +confidence : Float
        +disposition : Disposition
        +assertions : Integer
        +resolves : String
    }
    class Contract {
        +name : String
    }
    class SeededControl {
        +defect_class : String
        +confirmed_by : String
    }
    class Requalification {
        +oracle : String
        +defect_class : String
    }

    Oracle <|-- Validator
    Oracle <|-- Judge
    Oracle <|-- HumanReviewer
    Oracle --> Result : produces
    Contract --> Oracle : specifies
    SeededControl --> Oracle : tests
    Requalification --> Oracle : returns to use
```

## E.3 — Quality Dimensions

The six Quality Dimensions (Volume I, Chapter 2), their primary assessment mechanism,
and their role in the Aggregation Model. A clause's `dimension` (Appendix A §A.5) places
its Results in one of the first four.

```mermaid
classDiagram
    class QualityDimension { <<enumeration>> }
    class Functional { +aggregation : standard }
    class Semantic { +aggregation : standard }
    class Operational { +aggregation : standard }
    class Safety { +aggregation : hard_veto }
    class Reliability { +aggregation : standard }
    class Business { +aggregation : weighting }

    QualityDimension <|-- Functional
    QualityDimension <|-- Semantic
    QualityDimension <|-- Operational
    QualityDimension <|-- Safety
    QualityDimension <|-- Reliability
    QualityDimension <|-- Business
```

## E.4 — Dataset Taxonomy

Dataset source types and coverage mechanisms (Volume IV).

```mermaid
classDiagram
    class Dataset { +name : String; +version : String; +rows : List~Row~ }
    class StaticDataset
    class SyntheticDataset { +template : String; +rule : String }
    class GeneratedDataset { +model : String; +seed : Int; +instruction : String }
    class ProductionReplayDataset { +capture_source : String; +date_range : DateRange; +sampling : SamplingConfig }
    class CoverageMechanism
    class DataMutation
    class Fuzzing
    class EdgeCases
    class Adversarial

    Dataset <|-- StaticDataset
    Dataset <|-- SyntheticDataset
    Dataset <|-- GeneratedDataset
    Dataset <|-- ProductionReplayDataset
    Dataset --> CoverageMechanism : applies
    CoverageMechanism <|-- DataMutation
    CoverageMechanism <|-- Fuzzing
    CoverageMechanism <|-- EdgeCases
    CoverageMechanism <|-- Adversarial
```

## E.5 — Validator Engine: Built-in Types

The built-in Validator types and their specialization (Volume V).

```mermaid
classDiagram
    class Validator {
        +target : String
        +dimension : String
        +evaluate(evidence) Result
    }
    class SchemaValidator {
        +expected_schema : JSONSchema
    }
    class ToolCallValidator {
        +allowed_tools : List~String~
        +argument_schemas : Map
    }
    class StructuralValidator {
        +expected_steps : List~Step~
        +allow_intermediate : Boolean
    }
    class ForbiddenContentValidator {
        +patterns : List~Pattern~
    }
    class LatencyValidator {
        +max_ms : Integer
    }
    class CostValidator {
        +max_tokens : Integer
        +max_cost : Float
    }
    class BoundaryValidator {
        +attempts : Integer
        +tripwire_touches : Integer
    }
    class CustomValidator {
        +implementation : Function
    }

    Validator <|-- SchemaValidator
    Validator <|-- ToolCallValidator
    Validator <|-- StructuralValidator
    Validator <|-- ForbiddenContentValidator
    Validator <|-- LatencyValidator
    Validator <|-- CostValidator
    Validator <|-- BoundaryValidator
    Validator <|-- CustomValidator
```

## E.6 — Multi-Judge Configuration

Two distinct purposes for running multiple Judges, their Consensus, and the panel a
Result reports (Volume VI).

```mermaid
classDiagram
    class MultiJudge {
        +purpose : Purpose
        +min_qualified : Integer
    }
    class IndependenceConfig {
        +judges : List~Judge~
    }
    class StabilityConfig {
        +judge : Judge
        +samples : Integer
    }
    class Judge
    class Consensus {
        +on_disagreement : DisagreementPolicy
    }
    class Voting {
        +threshold : VotingThreshold
    }
    class ConfidenceWeightedMean {
        +min_agreement : Float
    }
    class Panel {
        +configured : Integer
        +counted : Integer
    }

    MultiJudge <|-- IndependenceConfig
    MultiJudge <|-- StabilityConfig
    IndependenceConfig --> Judge : composes
    StabilityConfig --> Judge : samples
    MultiJudge --> Consensus : resolves via
    Consensus <|-- Voting
    Consensus <|-- ConfidenceWeightedMean
    MultiJudge --> Panel : reports
```

## E.7 — Governance Model

Principals, Teams, Roles, Permissions, the Approval Workflow, and standing release
policies (Volume XII).

```mermaid
classDiagram
    class Principal {
        <<abstract>>
        +name : String
    }
    class Person
    class ServiceAccount {
        +owner : Person
    }
    class Team {
        +name : String
    }
    class Role {
        +name : String
    }
    class Permission {
        +action : PermissionAction
    }
    class GovernedAction {
        <<enumeration>>
        contract_define
        baseline_approve
        gate_override
        release_decide
    }
    class ApprovalWorkflow {
        +action : GovernedAction
        +requested_by : Principal
        +reviewed_by : Person
        +decision : ApprovalDecision
        +timestamp : DateTime
    }
    class ReleasePolicy {
        +suites : List~String~
        +environments : List~String~
        +revoked_at : DateTime
    }

    Principal <|-- Person
    Principal <|-- ServiceAccount
    ServiceAccount --> Person : owned by
    Principal --> Team : belongs to
    Principal --> Role : assigned
    Role --> Permission : bundles
    Team --> Role : governs
    Permission --> GovernedAction : authorizes
    ApprovalWorkflow --> GovernedAction : requires
    Person --> ReleasePolicy : approves
    ReleasePolicy --> ServiceAccount : authorizes
```

## E.8 — From Results to a Release Decision

The records the Decision Pipeline produces and reads (Volume I, Chapter 6; Appendix A
§A.12–A.14; Appendix C §C.3, §C.10).

```mermaid
classDiagram
    class Result {
        +id : String
        +resolves : String
        +disposition : Disposition
    }
    class SeededControlResult {
        +outcome : String
        +invalidation_scope : String
    }
    class Requalification {
        +oracle : String
        +defect_class : String
    }
    class QualityGate {
        +name : String
        +threshold : Float
    }
    class GateResult {
        +id : String
        +status : PassFail
        +blocking : Boolean
        +reasons : List~Reason~
        +basis : Basis
    }
    class Override {
        +justification : String
    }
    class Snapshot {
        +id : String
        +captured_at : DateTime
    }
    class Report {
        +id : String
        +generated_at : DateTime
        +signals : Signals
    }
    class ReleaseDecision {
        +id : String
        +decision : String
    }
    class ReleasePolicy {
        +id : String
    }

    SeededControlResult --> Result : invalidates
    Requalification --> Result : permits re-assessment of
    Result --> GateResult : aggregated into
    QualityGate --> GateResult : evaluated as
    GateResult --> Snapshot : evaluated under
    GateResult --> Override : may carry
    ReleaseDecision --> GateResult : contains
    ReleaseDecision --> Snapshot : references
    ReleaseDecision --> Report : references
    ReleaseDecision --> ReleasePolicy : may act under
```
