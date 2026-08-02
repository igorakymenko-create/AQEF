# Appendix E — UML Diagrams

**Status:** confirmed (v0.1).

This appendix provides UML class diagrams visualizing the structural relationships
defined across the specification. Each diagram restates — in visual form — what the
referenced Volumes specify in prose; the Volumes remain authoritative. Diagrams use
Mermaid syntax for inline rendering.

## E.1 — Domain Model: Core Entities

The complete entity graph from Volume II. Arrows read as "owns," "produces," or
"references."

```mermaid
classDiagram
    class Project { +name : String }
    class Suite { +name : String; +purpose : String }
    class Scenario { +name : String }
    class Contract { +name : String }
    class Dataset { +name : String; +version : String; +source : DatasetSource }
    class Prompt { +template : String }
    class Environment { +name : String; +model_version : String; +prompt_version : String; +tool_configuration : Map; +infra_target : String }
    class Variables { +values : Map }
    class Execution { +id : String; +timestamp : DateTime }
    class Conversation { +turns : List~Turn~ }
    class Artifact { +type : String; +data : Any }
    class Result { +verdict : PassFail; +confidence : Float; +evidence : Any }
    class Metric { +name : String; +value : Float; +dimension : QualityDimension }
    class Baseline { +approved_by : String; +approved_at : DateTime }
    class Report { +id : String; +frozen_at : DateTime }
    class Snapshot { +release_label : String; +captured_at : DateTime }

    Project "1" --> "1..*" Suite : owns
    Suite "1" --> "1..*" Scenario : contains
    Scenario "1" --> "1" Contract : governed by
    Scenario "1" --> "0..1" Dataset : instantiated by
    Dataset "1" --> "1" Variables : supplies
    Prompt "1" --> "0..*" Variables : interpolates
    Scenario "1" --> "1..*" Execution : realized by
    Execution "1..*" --> "1" Environment : runs in
    Execution "1" --> "1" Conversation : produces
    Execution "1" --> "0..*" Artifact : captures
    Execution "1" --> "1..*" Result : yields
    Result "0..*" --> "0..1" Metric : aggregates into
    Result "0..1" --> "0..1" Baseline : designated as
    Metric "0..*" --> "1" Report : presented in
    Baseline "0..*" --> "0..1" Snapshot : composed into
    Report "0..1" --> "0..1" Snapshot : may reference
```

## E.2 — Oracle Hierarchy

The three concrete Oracle types and their relationship to Contracts, Results, and
Confidence (Volume II, Volume V, Volume VI).

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
        +reviewer : Person
        +evaluate(evidence) Result
    }
    class Result {
        +verdict : PassFail
        +confidence : Float
    }
    class Contract { +name : String }

    Oracle <|-- Validator
    Oracle <|-- Judge
    Oracle <|-- HumanReviewer
    Oracle "1" --> "1" Result : produces
    Result "1" --> "0..1" Float : confidence (Validator: none)
    Contract "1" --> "1..*" Oracle : specifies
```

*Note: a rendering error in the source draft left this diagram blank in v0.2 — corrected
here.*

## E.3 — Quality Dimensions

The six Quality Dimensions (Volume I, Chapter 2), their primary assessment mechanism,
and their role in the Aggregation Model.

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
    Dataset "1" --> "0..*" CoverageMechanism : applies
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
        +evaluate(evidence) Result
    }
    class SchemaValidator { +expected_schema : JSONSchema }
    class ToolCallValidator { +allowed_tools : List~String~; +argument_schemas : Map }
    class StructuralValidator { +expected_steps : List~Step~; +allow_intermediate : Boolean }
    class ForbiddenContentValidator { +patterns : List~String~; +veto : Boolean }
    class LatencyValidator { +max_ms : Integer }
    class CostValidator { +max_tokens : Integer; +max_cost : Float }
    class CustomValidator { +implementation : Function }

    Validator <|-- SchemaValidator
    Validator <|-- ToolCallValidator
    Validator <|-- StructuralValidator
    Validator <|-- ForbiddenContentValidator
    Validator <|-- LatencyValidator
    Validator <|-- CostValidator
    Validator <|-- CustomValidator
```

## E.6 — Multi-Judge Configuration

Two distinct purposes for running multiple Judges (Volume VI).

```mermaid
classDiagram
    class MultiJudge { +purpose : Purpose }
    class IndependenceConfig { +judges : List~Judge~ }
    class StabilityConfig { +judge : Judge; +samples : Integer }
    class Judge
    class Consensus
    class Voting { +threshold : VotingThreshold }
    class ConfidenceWeightedMean { +min_agreement : Float }

    MultiJudge <|-- IndependenceConfig
    MultiJudge <|-- StabilityConfig
    IndependenceConfig "1" --> "1..*" Judge : composes
    StabilityConfig "1" --> "1" Judge : samples
    MultiJudge "1" --> "1" Consensus : resolves via
    Consensus <|-- Voting
    Consensus <|-- ConfidenceWeightedMean
```

## E.7 — Governance Model

Teams, Roles, Permissions, and the Approval Workflow (Volume XII).

```mermaid
classDiagram
    class Person { +name : String; +email : String }
    class Team { +name : String }
    class Role { +name : String }
    class Permission { +action : PermissionAction }
    class GovernedAction {
        <<enumeration>>
        DEFINE_CONTRACT
        APPROVE_BASELINE
        OVERRIDE_GATE
        RELEASE_DECISION
    }
    class ApprovalWorkflow {
        +action : GovernedAction
        +requested_by : Person
        +reviewed_by : Person
        +decision : ApprovalDecision
        +timestamp : DateTime
    }

    Person "1..*" --> "1" Team : belongs to
    Person "1" --> "1" Role : assigned
    Role "1" --> "1..*" Permission : bundles
    Team "1" --> "1..*" Role : governs
    Permission "1" --> "1" GovernedAction : authorizes
    ApprovalWorkflow "1" --> "1" GovernedAction : requires
```
