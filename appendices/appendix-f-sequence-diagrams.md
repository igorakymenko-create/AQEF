# Appendix F — Sequence Diagrams

**Status:** confirmed (v0.1).

This appendix provides sequence diagrams for the key runtime flows defined in the
specification. Each diagram visualizes — in temporal order — what the referenced
Volumes specify in prose; the Volumes remain authoritative. Diagrams use Mermaid syntax
for inline rendering.

## F.1 — Execution Pipeline

The five-stage pipeline that turns a Scenario into a Conversation, Artifacts, and
Results (Volume III). Note the strict ordering: Validators run before Judges
(Validation before Evaluation, Volume I, Chapter 3).

```mermaid
sequenceDiagram
    participant S as Scenario
    participant D as Dataset
    participant EP as Execution Pipeline
    participant AI as AI System (Subject)
    participant VP as Validator Pipeline
    participant JE as Judge Engine
    participant RS as Result Store

    S->>EP: Trigger Execution
    EP->>D: Resolve Variables
    D-->>EP: Variable values (pinned version)
    EP->>EP: Prompt Construction (interpolate Variables)
    EP->>AI: Send Prompt (Turn 1)
    AI-->>EP: Response (Turn 1)
    EP->>EP: Update Context
    opt Multi-turn Scenario
        EP->>AI: Send Prompt (Turn N)
        AI-->>EP: Response (Turn N)
        EP->>EP: Update Context
    end
    EP->>EP: Artifact Collection (token usage, latency, tool traces)
    EP->>RS: Store Conversation + Artifacts
    EP->>VP: Validation (deterministic, no Confidence)
    VP->>VP: Run Validators (cheapest-first)
    VP->>RS: Store Validator Results
    alt Any Validator fails
        VP-->>EP: Short-circuit — skip Judges
    else All Validators pass
        VP->>JE: Proceed to Evaluation
        JE->>JE: Run Judges (probabilistic, with Confidence)
        JE->>RS: Store Judge Results (with Confidence)
    end
```

## F.2 — Decision Pipeline

The sequence from computed Results through the Confidence Model, Aggregation Model,
Quality Gates, to a Release Decision (Volume I, Chapter 6).

```mermaid
sequenceDiagram
    participant R as Results
    participant CM as Confidence Model
    participant AM as Aggregation Model
    participant QG as Quality Gates
    participant HR as Human Review
    participant RD as Release Decision

    R->>CM: Submit all Results
    CM->>CM: For each Result, evaluate Confidence
    alt Confidence >= threshold
        CM->>AM: Trust at face value
    else Confidence < threshold
        CM->>HR: Route to Human Review
        HR-->>CM: Human verdict (ground truth)
        CM->>AM: Forward human-qualified Result
    else Confidence ambiguous
        CM->>CM: Flag for audit trail
    end
    AM->>AM: Group Results by Quality Dimension
    AM->>AM: Apply Business Quality weights
    AM->>AM: Enforce Safety hard veto
    AM->>QG: Per-dimension aggregates
    QG->>QG: Safety Gate (hard veto, threshold=1.0)
    QG->>QG: Functional Gate (threshold)
    QG->>QG: Regression Gate (compare vs Baseline)
    QG->>QG: Operational Gate (latency, cost)
    alt All gates pass
        QG->>RD: Recommend: approve
    else Any blocking gate fails
        QG->>RD: Recommend: block
    end
    RD->>RD: Attach Report + Gate results
    RD->>RD: Log through Approval Workflow
```

## F.3 — Baseline Approval and Regression Detection

Two related flows: designating a Baseline (approval path) and detecting a Semantic
Regression (comparison path). See Volume X and Volume XII.

```mermaid
sequenceDiagram
    participant QE as Quality Engineer
    participant AW as Approval Workflow
    participant BS as Baseline Store
    participant EP as Execution Pipeline
    participant RDT as Regression Detection

    note over QE,BS: Baseline Approval (Volume X, Volume XII)
    QE->>AW: Request Baseline designation (Execution ID)
    AW->>AW: Check requester has baseline_approve Permission
    AW->>AW: Log request + reviewer + decision
    AW->>BS: Designate Execution as Baseline
    BS->>BS: Pin Dataset version, Contract version, Environment

    note over EP,RDT: Regression Detection (Volume X)
    EP->>RDT: New Execution of same Scenario
    EP-->>RDT: Current Results
    RDT->>BS: Retrieve approved Baseline Results
    RDT->>RDT: Compare current vs baseline (by meaning, not text)
    alt Current passes Oracles that Baseline passed
        RDT->>RDT: No regression
    else Current fails Oracle that Baseline passed
        RDT->>RDT: Semantic Regression detected
        RDT->>RDT: Drift Analysis — check Prompt Drift, Model Drift, Dataset Drift, Judge Drift
    end
```

## F.4 — Multi-Judge Consensus

How a Multi-Judge configuration resolves disagreement into a single verdict (Volume
VI). Shows the independence purpose; stability uses repeated sampling of the same Judge
with the same flow.

```mermaid
sequenceDiagram
    participant C as Conversation
    participant JA as Judge A (Model Family 1)
    participant JB as Judge B (Model Family 2)
    participant CO as Consensus
    participant HR as Human Review
    participant RS as Result Store

    par Independence: different model families
        C->>JA: Assess against criteria
        JA-->>CO: Result A (verdict + confidence)
    and
        C->>JB: Assess against criteria
        JB-->>CO: Result B (verdict + confidence)
    end
    CO->>CO: Apply Consensus method (e.g. Voting)
    alt Judges agree
        CO->>RS: Store consensus Result
    else Judges disagree
        CO->>HR: Route to Human Reviewer
        HR-->>RS: Store human-qualified Result
        note over HR,RS: Human verdict serves as ground truth for Calibration
    end
```

## F.5 — CI/CD Integration

How an AQEF Quality Gate result flows through a CI/CD pipeline (Volume XIII).
Platform-agnostic — shows the logical flow, not a specific vendor.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant CI as CI/CD Pipeline
    participant AQ as AQEF Engine
    participant QG as Quality Gates
    participant AW as Approval Workflow
    participant Dep as Deployment

    Dev->>CI: Push code / Open PR
    CI->>AQ: Run Suite (via CLI / REST API)
    AQ->>AQ: Execute all Scenarios
    AQ->>AQ: Run Validators, then Judges
    AQ-->>CI: Aggregated Results
    CI->>QG: Evaluate all Gates
    alt All blocking gates pass
        QG-->>CI: Status: PASS
        CI->>Dep: Proceed with deployment
    else Blocking gate fails
        QG-->>CI: Status: FAIL (with Report)
        CI->>Dev: Block deployment, show Report
        opt Governance override
            Dev->>AW: Request override (with justification)
            AW->>AW: Role-based review
            AW->>AW: Override logged
            AW-->>CI: Status: PASS (overridden)
            note over CI: Pipeline status reflects the override decision, not the raw failure
            CI->>Dep: Proceed with deployment
        end
    end
```

## F.6 — Plugin Registration

The Extension Lifecycle for a Validator Plugin, showing mechanical determinism
verification (Volume XVI).

```mermaid
sequenceDiagram
    participant PA as Plugin Author
    participant PR as Plugin Registry
    participant VE as Verification Engine
    participant PS as Plugin Store

    PA->>PR: Submit Validator Plugin (v1.0.0)
    PR->>VE: Verify determinism
    VE->>VE: Run plugin against fixed input (N times)
    VE->>VE: Compare all N outputs
    alt All outputs identical
        VE-->>PR: Determinism confirmed
        PR->>PS: Register plugin (version-pinned)
        PS-->>PA: Plugin available for use
        note over PS: Historical Results produced by v1.0.0 remain valid even if v2.0.0 is later registered or v1.0.0 is deprecated.
    else Any output differs
        VE-->>PR: REJECTED — not deterministic
        PR-->>PA: Rejection with evidence
    end
```
