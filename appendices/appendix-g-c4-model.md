# Appendix G — C4 Model

**Status:** confirmed (v0.1).

This appendix provides C4-style architectural views of an AQEF-conformant system at
four levels of abstraction: Context, Container, Component, and Deployment. The C4 model
(Simon Brown) uses progressively deeper views to show what a system is, what it is made
of, and how it is deployed. Diagrams use Mermaid flowchart syntax with subgraphs for
broad rendering compatibility.

These diagrams visualize the Reference Architecture (Volume I, Chapter 4), the Engine
specifications (Volumes III–VI, XI–XVI), and the Deployment Topologies (Volume XVII).

## G.1 — Level 1: System Context

Who uses an AQEF-conformant system, and what external systems does it interact with?

```mermaid
graph TB
    QE["Quality Engineer<br/>Authors Scenarios, Contracts,<br/>Datasets; reviews Results"]
    EM["Engineering Manager<br/>Reviews Reports, makes<br/>Release Decisions"]
    CA["Compliance / Audit<br/>Queries audit trail,<br/>verifies traceability"]
    CICD["CI/CD Pipeline<br/>GitHub Actions, GitLab CI,<br/>Jenkins, Azure DevOps"]

    AQEF["AQEF Engine<br/>Executes Scenarios, applies Oracles,<br/>produces Reports and Quality Gate decisions"]

    AI["AI System Under Test<br/>Probabilistic Subject (LLM, RAG, Agent)"]
    IDP["Identity Provider<br/>SSO / OAuth authentication"]

    QE -->|"Authors & reviews via UI/SDK"| AQEF
    EM -->|"Reviews Reports, approves Releases"| AQEF
    CA -->|"Queries audit trail"| AQEF
    CICD -->|"Triggers Suites, reads Gate status"| AQEF
    AQEF -->|"Sends Prompts, receives Responses"| AI
    AQEF -->|"Authenticates users, resolves Roles"| IDP
```

## G.2 — Level 2: Container Diagram

What are the major runtime containers inside the AQEF Engine? Containers map to the
five logical layers (Volume I, Chapter 4) plus supporting infrastructure.

```mermaid
graph TB
    QE["Quality Engineer"]
    CICD["CI/CD Pipeline"]

    subgraph AQEF["AQEF Engine (System Boundary)"]
        subgraph Frontend["Frontend & API Layer"]
            UI["Reference UI<br/>Visual Test Designer, Test Explorer, Reporting UI"]
            API["REST API<br/>Single canonical programmatic surface"]
        end

        subgraph Engines["Execution & Assessment Engines"]
            EE["Execution Engine<br/>Pipeline, Var Resolution, Conversation, Artifacts"]
            VE["Validator Engine<br/>Deterministic checks, cheapest-first"]
            JE["Judge Engine<br/>Probabilistic Judges, Consensus, Calibration"]
            DE["Decision Engine<br/>Confidence Model, Aggregation, Quality Gates"]
        end

        subgraph Mgmt["Management & Governance"]
            RE["Reporting Engine<br/>Reports, Dashboards, Trends, KPIs"]
            GE["Governance Engine<br/>Teams, Roles, Permissions, Workflows, Audit"]
            PR["Plugin Registry<br/>Plugin Lifecycle & Verification"]
        end

        DS[("Data Store<br/>Projects, Datasets, Contracts,<br/>Executions, Results, Reports")]
    end

    AI["AI System Under Test"]

    QE -->|UI / CLI/SDK| Frontend
    CICD -->|"Triggers & reads Gates"| API
    API --> EE
    EE -->|"Hands off"| VE
    VE -->|"On pass"| JE
    JE -->|Results| DE
    DE -->|Metrics| RE
    Engines --> DS
    Mgmt --> DS
    EE -->|"Prompts / Responses"| AI
```

## G.3 — Level 3: Component Diagram — Execution Engine

Zooming into the Execution Engine container to show its internal components (Volume
III).

```mermaid
graph TB
    subgraph EEC["Execution Engine Container"]
        SCHED["Scheduler<br/>Triggers Suite Scenarios"]
        POOL["Runtime Pool<br/>Isolated Runtimes"]
        VR["Variable Resolver<br/>Dataset rows to parameters"]
        PC["Prompt Constructor<br/>Assembles final Prompts"]
        CE["Conversation Engine<br/>Orchestrates turns & context"]
        AC["Artifact Collector<br/>Captures traces & metrics"]
    end

    DSTORE[("Dataset Store<br/>Versioned Datasets")]
    AI["AI System Under Test"]
    ESTORE[("Evidence Store<br/>Conversations + Artifacts")]
    VENG["Validator Engine"]

    SCHED --> POOL
    POOL --> VR
    VR -->|"Reads pinned version"| DSTORE
    VR --> PC
    PC --> CE
    CE -->|"Prompts / Responses"| AI
    CE --> AC
    AC -->|"Writes Conversation"| ESTORE
    AC -->|"Writes Artifacts"| ESTORE
    ESTORE -->|"Hands off on completion"| VENG
```

## G.4 — Level 3: Component Diagram — Assessment Engines

Zooming into the Validator Engine (Volume V) and Judge Engine (Volume VI) to show their
internal components and the handoff between them.

```mermaid
graph TB
    subgraph VEng["Validator Engine (Volume V)"]
        VRes["Validator Resolver<br/>Resolves Constraints"]
        EO["Execution Order<br/>Sorts cheapest-first"]
        Built["Built-in Validators<br/>Schema, Latency, Cost, etc."]
        Custom["Custom Validators<br/>Plugin checks"]
        VComp["Validator Composition<br/>AND / OR / Hard Veto"]
    end

    subgraph JEng["Judge Engine (Volume VI)"]
        JRes["Judge Resolver<br/>Resolves Expectations"]
        MJO["Multi-Judge Orchestrator<br/>Independence / Stability"]
        SJ["Single Judge<br/>One Judge + Confidence"]
        CE["Consensus Engine<br/>Voting & Weighted Mean"]
        CT["Calibration Tracker<br/>Tracks accuracy over time"]
        HR["Human Review<br/>Low Confidence / Disagreement"]
    end

    ResultStore[("Result Store")]

    VRes --> EO
    EO --> Built
    EO --> Custom
    Built --> VComp
    Custom --> VComp
    VComp -->|"Store Validator Results"| ResultStore
    VComp -->|"On pass: hand off"| JRes
    JRes --> MJO
    MJO --> SJ
    MJO --> CE
    SJ -->|"Store Judge Results"| ResultStore
    CE -->|"Store consensus Results"| ResultStore
    CE -->|"On disagreement / low confidence"| HR
    HR -->|"Ground truth comparison"| CT
    HR --> ResultStore
```

## G.5 — Deployment: Minimal Engine vs. Enterprise Engine

Two deployment topologies (Volume XVII). Both satisfy the same normative requirements;
they differ in how the logical layers are physically hosted.

**Minimal Engine**

```mermaid
graph TB
    subgraph Server["Single Server (Physical / VM / Container) — Single Process"]
        API["REST API"] --- EE["Execution Engine"] --- VE["Validator Engine"] --- JE["Judge Engine"] --- DE["Decision Engine"] --- RE["Reporting Engine"] --- GE["Governance Engine"]
        DB[("Embedded Database<br/>SQLite / File-based")]
    end
    AI["AI System Under Test (External)"]

    Server -->|HTTPS| AI
    Server --- DB
```

**Enterprise Engine**

```mermaid
graph TB
    CICD["External CI/CD Pipeline"]

    subgraph Infra["Cloud / Data Center Infrastructure"]
        subgraph APITier["API Tier"]
            LB["REST API (Load-balanced)"]
            UI["Reference UI"]
        end

        subgraph ExecTier["Execution Tier (Auto-scaled)"]
            W1["Execution Worker 1"]
            W2["Execution Worker 2"]
            WN["Execution Worker N"]
        end

        subgraph AssessTier["Assessment Tier"]
            VE["Validator Engine"]
            JE["Judge Engine"]
        end

        subgraph DecTier["Decision Tier"]
            DE["Decision Engine"]
            RepE["Reporting Engine"]
            GovE["Governance Engine"]
        end

        subgraph DataTier["Data Tier"]
            DBC[("Database Cluster")]
            AS[("Artifact Store (S3/Object)")]
        end
    end

    AI["AI System Under Test"]

    CICD -->|"Triggers / Reads Gates"| LB
    LB -->|"Distributes Executions"| ExecTier
    W1 -->|HTTPS| AI
    W2 -->|HTTPS| AI
    WN -->|HTTPS| AI
    ExecTier -->|"Hands off"| VE
    VE -->|"On pass"| JE
    JE -->|Results| DecTier
    DecTier --> DataTier
```

## Reading Guide

| If you want to understand... | Start with |
|---|---|
| What AQEF is and who uses it | G.1 (Context) |
| What the major subsystems are | G.2 (Container) |
| How an Execution flows internally | G.3 (Execution components) |
| How Validators and Judges interact | G.4 (Assessment components) |
| How to deploy AQEF | G.5 (Minimal vs Enterprise) |
| What the entity relationships look like | Appendix E (UML) |
| What the temporal flows look like | Appendix F (Sequence) |
