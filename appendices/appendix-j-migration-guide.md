# Appendix J — Migration Guide

**Status:** confirmed (v0.1).

This appendix describes how an organization adopts AQEF incrementally — from informal
AI evaluation to a governed, specification-conformant quality process. It is organized
as a sequence of stages, each self-contained: a team that stops at any stage still has
a coherent, useful quality posture; it simply has not yet exercised the later Volumes.

Nothing in this guide introduces new requirements beyond what the Volumes already
specify. It orders existing requirements into an adoption path that reflects how teams
actually build capability — starting with what hurts most (no reproducibility, no
regression detection) and ending with what matters most at scale (Governance, CI/CD
gates, plugin ecosystems).

For concrete YAML examples at each stage, see Appendix H (Reference Examples). For the
practices each stage should follow, see Appendix I (Best Practices).

## Stage 0 — Baseline: Ad Hoc Evaluation

Most teams begin here. Characteristics:

- Quality checks are manual and unstructured — someone runs the system, reads the
  output, and decides subjectively whether it "looks right."
- No formal Scenarios, Contracts, or Datasets exist. Test cases live in spreadsheets,
  Slack threads, or individual engineers' heads.
- Regressions go undetected until a user reports them. There are no Baselines.
- Model updates are untested. A provider updates a model version and the team
  discovers the impact in production.
- Results are not reproducible. Running the same input twice may produce different
  output, and there is no mechanism to determine whether the difference is expected
  (probabilistic variance) or a defect (Semantic Regression).

AQEF exists to replace this state with an engineering discipline (Volume I, Chapter 1).
The migration path below moves incrementally away from each of these characteristics.

## Stage 1 — Foundation: Scenarios, Contracts, and a Minimal Engine

**Goal:** Establish the basic AQEF loop — Definition → Execution → Evidence →
Assessment → Decision (Volume I, Chapter 4) — on a single Project using a Minimal
Engine (Volume XVII).

**What to do**

1. Define a Project and at least one Environment. Pin the model version, prompt
   version, and any tool configuration so that Executions are reproducible (Volume
   II).
2. Author 5–15 Scenarios covering the highest-risk behaviors. Use Risk Analysis
   (Volume I, Chapter 5) to prioritize: which failures would cause the most damage if
   they reached production? Start there, not with comprehensive coverage.
3. Write a Quality Contract for each Scenario. Begin with Constraints only — Schema
   Validators, Forbidden-Content Validators, and Latency Validators are deterministic,
   cheap, and immediately useful (Volume V). Add Expectations (Judge-bound clauses)
   once the Validator layer is stable.
4. Create a Static Dataset with 3–10 representative inputs per Scenario (Volume IV).
   Version it from the start — even a v1.0.0 tag is enough.
5. Run the Suite and review Results. At this stage, the "Decision" is a human reading
   a Report — there are no Quality Gates yet. The goal is to establish the habit of
   evidence-based quality assessment.

**What this achieves**

- Reproducibility. The same Scenario, Environment, and Dataset produce comparable
  Executions, even if the subject's output varies (Deterministic Infrastructure).
- Structural visibility. Failures are no longer subjective impressions; they are
  traceable Results produced by specific Oracles against specific Contracts.
- A foundation for everything that follows. Stages 2–5 extend this foundation; they do
  not replace it.

**Relevant Volumes:** I (Chapters 1–5), II, III, IV (Static only), V (built-in
Validators), XVII (Minimal Engine).

## Stage 2 — Assessment: Adding Judges and Baselines

**Goal:** Extend the basic loop with probabilistic assessment (Judges) and historical
comparison (Baselines).

**What to do**

1. Add Expectations to existing Contracts. Write criteria for the semantic qualities
   that matter most — helpfulness, faithfulness, tone — and bind them to a Judge from
   a different model family than the system under test (Volume VI, Independent
   Oracles).
2. Calibrate Judges against Human Review. Run a sample of Executions through both a
   Judge and a Human Reviewer. Compare their verdicts. If the Judge's Confidence does
   not track its actual accuracy, adjust the Confidence threshold or switch to a
   different Judge (Volume VI — Calibration).
3. Approve initial Baselines. For each Scenario, designate a specific Execution's
   Result as the reference standard through an explicit approval action (Volume X).
   This is the first Governance-controlled act — even a lightweight one-person
   approval satisfies the requirement.
4. Run the Suite again and compare against Baselines. The first comparison will
   establish whether the current system meets, exceeds, or falls short of the
   reference. This is where Semantic Regression detection begins.

**What this achieves**

- Semantic quality visibility. Judges surface subjective quality dimensions
  (helpfulness, safety, faithfulness) that Validators cannot assess.
- Regression detection. Baselines make degradation visible before users report it.
- Confidence-qualified evidence. Every Result now states not just a verdict but how
  much that verdict should be trusted.

**Relevant Volumes:** VI, VII (Constraints + Expectations), X (Baselines, Semantic
Regression).

## Stage 3 — Automation: Quality Gates and CI/CD

**Goal:** Turn manual report review into automated, pipeline-integrated Quality Gates
that block or warn before deployment.

**What to do**

1. Define Quality Gates for the dimensions that matter most (Volume I, Chapter 6).
   Start with: a Safety Gate (hard veto, no override without explicit Governance
   logging), a Regression Gate (comparing against approved Baselines), and an optional
   Operational Gate (latency, cost) set to warn, not block.
2. Integrate with CI/CD. Add an AQEF step to the deployment pipeline that runs the
   Regression Suite and checks Quality Gate results (Volume XIII). The CLI translates
   AQEF's Gate status into the platform's native blocking primitive — a GitHub status
   check, a GitLab pipeline status, or equivalent (Appendix H, example H.7).
3. Establish the Approval Workflow for overrides. A failing Quality Gate should not
   silently block deployments forever. Define who can override which Gates, under what
   conditions, and ensure every override is logged (Volume XII — Approval Workflow).

**What this achieves**

- Automated release protection. Deployments are blocked by evidence, not by someone
  remembering to check a spreadsheet.
- Governance trail. Every release — including overrides — is traceable through the
  Approval Workflow.
- Shift-left quality. Developers see quality failures in their pull request, not in
  production.

**Relevant Volumes:** I (Chapter 6 — Decision Pipeline), XI (Reporting), XII
(Governance), XIII (CI/CD Integration).

## Stage 4 — Scale: Datasets, Drift, and Multi-Judge

**Goal:** Expand test coverage, improve assessment reliability, and detect silent
degradation.

**What to do**

1. Expand Datasets beyond Static. Add Generated Datasets for broader coverage,
   Production Replay to test against real-world input, and Adversarial Datasets for
   safety probing (Volume IV). Apply Data Mutation and Fuzzing mechanisms to existing
   Datasets.
2. Deploy Multi-Judge configurations. Use independence-mode Multi-Judge (different
   model families) for high-stakes Expectations where a single Judge's blind spots are
   unacceptable. Use stability-mode Multi-Judge (repeated sampling) where noise
   reduction matters more than blind-spot detection (Volume VI).
3. Monitor Drift. Add Prompt Drift, Model Drift, and Dataset Drift detection to the
   Regression Suite (Volume X). Monitor Judge Drift separately (Volume VI). When a
   regression appears with no AQEF-visible configuration change, investigate Model
   Drift first.
4. Expand Test Types. Move beyond Smoke and Functional Suites. Add RAG-specific Suites
   (retrieval + grounding), Agent-specific Suites (tool-call sequences), and
   Safety-Adjacent Suites (Jailbreak, Prompt Injection, Bias, Toxicity) as the
   system's architectural patterns and risk profile require (Volume IX).

**What this achieves**

- Broader and deeper coverage. The test surface expands from a handful of hand-written
  cases to systematically generated, production-derived, and adversarially crafted
  inputs.
- More reliable assessment. Multi-Judge configurations reduce both noise and blind
  spots.
- Proactive drift detection. Silent degradation is caught by the regression system,
  not by user complaints.

**Relevant Volumes:** IV (full Dataset Engine), VI (Multi-Judge, Judge Drift), VIII
(Test Design patterns), IX (Test Types taxonomy), X (full Drift Detection).

## Stage 5 — Enterprise: Governance, Plugins, and Federation

**Goal:** Operate AQEF across multiple teams, Projects, and organizational boundaries.

**What to do**

1. Implement full Governance. Define Teams, Roles, and Permissions (Volume XII).
   Separate organizational boundaries (Teams scope access) from capabilities (Roles
   scope actions). Ensure every Governance-controlled action — Baseline approval, Gate
   override, Contract modification, Release Decision — flows through the Approval
   Workflow.
2. Deploy Custom Plugins. Build Validator Plugins for domain-specific deterministic
   checks (e.g., regulatory compliance patterns) and Judge Plugins for domain-specific
   semantic assessment (e.g., medical accuracy). Follow the Extension Lifecycle (Volume
   XVI) — register, verify, version, deprecate without invalidating history.
3. Scale the engine. If the Minimal Engine can no longer handle the Execution volume,
   migrate to an Enterprise Engine topology (Volume XVII). The migration changes
   topology — single process to distributed services — but does not loosen any
   normative requirements.
4. Federate across Projects. Use Reusable Contracts at the organization level (Volume
   VII) to enforce consistent quality bars across Projects. Use Snapshot Comparison
   (Volume X) to track quality trends across releases and across Projects.
5. Integrate Reporting. Deploy Dashboards for live monitoring and frozen Reports for
   Release Decisions (Volume XI). Elevate the most important Metrics to KPIs. Ensure
   every KPI is traceable back to underlying Results.

**What this achieves**

- Organizational quality governance. Quality is managed across teams and Projects, not
  just within individual engineering efforts.
- Extensibility without fragmentation. Custom Plugins extend AQEF's capabilities while
  maintaining the same Conformance bar (§10).
- Scalable infrastructure. The engine grows with the organization's needs without
  requiring a specification rewrite.

**Relevant Volumes:** XII (Governance), XIV (SDK & APIs), XV (Reference UI), XVI
(Plugin Architecture), XVII (Reference Implementations).

## Migration Anti-Patterns

The following adoption mistakes are common enough to name explicitly.

| Anti-Pattern | What Goes Wrong | What To Do Instead |
|---|---|---|
| Big-bang adoption — implementing all 17 Volumes simultaneously | Overwhelms the team. Nothing works until everything works. | Adopt incrementally, stage by stage. Each stage is self-contained. |
| Skipping Validators and going straight to Judges | Judges run on structurally broken output, producing misleading Confidence on malformed responses. | Always establish Validators first (Stage 1), Judges second (Stage 2). |
| Treating Baselines as "the last run" | Silent Baseline drift absorbs regressions. The reference standard erodes without anyone noticing. | Designate Baselines explicitly through Approval Workflow. |
| Automating CI/CD gates before having Baselines | Gates have nothing to compare against. Regression Gates pass vacuously. | Establish Baselines (Stage 2) before automating gates (Stage 3). |
| Deploying an Enterprise Engine before needing one | Unnecessary operational complexity. A Minimal Engine satisfies every requirement. | Start with Minimal Engine. Migrate when volume or team structure requires it. |
| Writing Contracts after building the test harness | The harness encodes implicit quality expectations in code, not in inspectable Contracts. | Write Contracts first. The harness implements them. |

## Mapping Stages to Conformance

Every stage from Stage 1 onward produces a conformant AQEF implementation —
Conformance (§10) is scoped to claimed capability, not universal completeness. A
Minimal Engine at Stage 1 that implements the basic loop (Definition → Execution →
Evidence → Assessment → Decision) and respects the seven Fundamental Principles is
conformant for the capability it offers. Each subsequent stage extends the claimed
capability set, and with it the Volumes whose requirements become applicable.

| Stage | Claimed Capability | Applicable Volumes |
|---|---|---|
| 1 | Basic loop, Validators only | I, II, III, IV (Static), V, XVII |
| 2 | + Judges, Baselines | + VI, VII, X |
| 3 | + Quality Gates, CI/CD | + XI, XII, XIII |
| 4 | + Full Datasets, Multi-Judge, Drift | + IV (full), VIII, IX |
| 5 | + Governance, Plugins, Enterprise | + XIV, XV, XVI, XVII (Enterprise) |
