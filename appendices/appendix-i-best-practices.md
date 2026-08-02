# Appendix I — Best Practices

**Status:** confirmed (v0.1).

This appendix collects the practical guidance, common pitfalls, and SHOULD-level
recommendations distributed across all seventeen Volumes into a single,
practitioner-oriented reference. Each practice cites the Volume or Chapter where its
normative basis lives; that source — not this appendix — is authoritative. Nothing here
introduces a new requirement; everything here restates, in a more actionable form,
something a Volume already specifies.

For concrete YAML examples demonstrating many of these practices, see Appendix H
(Reference Examples).

## I.1 — Contract Design

**Express expectations as Contracts, not inline assertions.** Quality expectations
MUST be expressed as declarative Quality Contracts (Volume VII), not scattered
assertions inside test scripts. A Contract separates what to check from how the test is
written, making expectations reusable across Scenarios, auditable by Governance (Volume
XII), and impossible to silently weaken by editing a test's source code without anyone
noticing (Volume I, Chapter 3 — Contracts over Assertions).

**State Judge criteria explicitly enough to be inspectable.** An Expectation clause
(Volume VII) MUST contain criteria a human auditor can read and understand what the
Judge is being asked to assess. A criteria field that says "check quality" is not
inspectable; one that says "the response is grounded in the retrieved documents and
does not introduce unsupported facts" is. If a criteria cannot be stated precisely, the
behavior it checks is not yet well enough understood to automate — route it to Human
Review instead.

**Use Reusable Contracts for cross-cutting concerns.** Safety checks, forbidden-content
rules, and latency budgets that apply to every Scenario in a Project SHOULD be authored
once as Reusable Contracts (Volume VII) and attached at the Suite or Project level,
rather than duplicated in each Scenario. This keeps the rules consistent and updatable
from a single place.

**Surface composition conflicts — never resolve them silently.** When two contributing
Contracts specify different values for the same clause — different Confidence
thresholds on the same Expectation, for instance — Contract Composition (Volume VII)
MUST make the conflict explicit rather than silently picking one. A silently overridden
threshold is exactly the kind of drift Chapter 3 requires a Contract to remain
auditable against.

**Separate Constraints from Expectations deliberately.** Every clause in a Contract
belongs to exactly one of two kinds: a Constraint (deterministic, Validator-bound, no
Confidence) or an Expectation (criteria-based, Judge-bound, Confidence-qualified). If
you find yourself wanting a "Constraint with a Confidence threshold" or an "Expectation
that always returns the same result," the clause is misclassified — reclassify it
before it reaches production.

## I.2 — Validators and Judges

**Run Validators before Judges — always.** This is the Validation before Evaluation
principle (Volume I, Chapter 3), enforced by the Execution Pipeline (Volume III) and
the Validator Pipeline (Volume V). Validators are deterministic, fast, and cheap;
running a Judge on a Response that fails basic schema validation wastes inference
budget and risks producing misleadingly confident semantic verdicts on structurally
broken output.

**Order Validators cheapest-first.** Within the Validator Pipeline, Validators SHOULD
execute in ascending cost order — regex-based Forbidden-Content before a Schema
Validator, a Schema Validator before a Structural Validator that must parse the full
Conversation. This fail-fast ordering avoids running an expensive check when a cheap
one would have caught the failure (Volume V — Execution Order).

**Never label a probabilistic check as a Validator.** A Custom Validator that
internally calls an LLM, a semantic similarity model, or any other probabilistic
process is structurally a Judge regardless of what it is labeled (Volume V). The Plugin
Architecture (Volume XVI) mechanically enforces this by running a candidate Validator
Plugin against a fixed input multiple times at registration — any variance rejects it.
If you need probabilistic judgment, model it as a Judge and give it a Confidence value.

**Use independent Judges.** A Judge MUST NOT share the same model family, weights, or
decision process as the AI system it evaluates (Volume I, Chapter 3 — Independent
Oracles). A GPT-4o system assessed by a GPT-4o Judge risks correlated blind spots where
both miss the same failure mode. Use a different model family — if the subject is
GPT-4o, assess with Gemini or Claude (see Appendix H, example H.2).

**Declare Multi-Judge purpose explicitly.** Running multiple Judges against the same
Conversation serves either of two distinct purposes that MUST be stated: independence
(different model families to catch blind spots) or stability (repeated sampling to
reduce noise). These are not interchangeable — stability says nothing about correlated
blind spots, and independence says nothing about sampling noise (Volume VI).

**Calibrate Judges against Human Review.** A Judge's Confidence is only useful if it
tracks reality. Calibration (Volume VI) periodically compares a Judge's verdicts
against Human Reviewer ground truth to verify that stated Confidence values are
numerically meaningful. A Judge whose Confidence says 0.95 but whose actual accuracy is
0.70 is worse than useless — it produces confidently wrong evidence.

**Monitor Judge Drift.** Even a well-calibrated Judge can change over time (Volume VI —
Judge Drift). If a model provider updates what a stable model identifier resolves to,
or if the Judge's own prompt version changes, its verdicts may shift. Track Judge Drift
separately from subject drift — the same Semantic Regression symptom has two different
causes, and they require different responses.

## I.3 — Dataset Management

**Version every Dataset.** Every Dataset — Static, Synthetic, Generated, Production
Replay — MUST be versioned (Volume IV). Variable Resolution (Volume III) is only
reproducible if the exact rows that fed a past Execution can be recovered. A Dataset
whose content can silently change between runs makes every Baseline comparison
meaningless.

**Use independent sources for Generated and Adversarial Datasets.** When using a model
to generate test data, that model SHOULD NOT be from the same family as the system
under test (Volume IV). A GPT-4o system tested with GPT-4o-generated adversarial inputs
risks the generator sharing the subject's blind spots — the generated attacks may
systematically avoid the exact weaknesses they should be probing.

**Distinguish Data Mutation from Fuzzing.** Both produce inputs beyond the original
Dataset, but they serve different purposes and MUST NOT be conflated:

- Data Mutation is intent-preserving — paraphrasing a query, transliterating a name —
  and tests generalization under legitimate variation (Reliability).
- Fuzzing is not intent-preserving — injecting random Unicode, truncating input — and
  tests for breaking points under adversarial or malformed input.
- Edge Cases are human-identified, named boundary conditions — not random, not
  intent-preserving, but targeted.

**Anonymize Production Replay Datasets.** When capturing real production Conversations
to fold back in as test Scenarios, Compliance (Volume XII) requirements for data
privacy MUST be met. Anonymization, sampling strategies, and data retention policies
are a Project-level Governance decision, not something a Dataset configuration silently
skips.

## I.4 — Execution and Runtime

**Keep infrastructure deterministic.** The Deterministic Infrastructure principle
(Volume I, Chapter 3) means everything surrounding the AI system — Variable
Resolution, Prompt Construction, Artifact Collection, evidence storage — MUST produce
the same behavior for the same input. The subject is probabilistic; the harness is not.

**Isolate parallel Executions.** Concurrent Executions MUST NOT share mutable Context
or Variable state (Volume III — Parallelization). An Execution's outcome must depend
only on its own Scenario and Environment, never on which other Executions happened to
run alongside it or which physical worker hosted it.

**Never discard a genuine Result in favor of a better re-run.** Retry (Volume III) is
strictly for infrastructure-level failures that occurred before the subject produced a
genuine Response — a network timeout, a 503, a connection reset. If the subject
responded and the Result is unfavorable, that Result stands and MUST be recorded.
Re-running until a favorable result appears and discarding the originals is data
falsification, not quality engineering.

**Set Timeouts as infrastructure safeguards, not quality checks.** A Timeout (Volume
III) aborts an Execution before it can produce a Conversation — a timed-out Execution
has no evidence to assess. Latency as a quality concern is a Latency Validator (Volume
V) applied to a completed Execution's recorded duration. These are different
mechanisms at different layers.

## I.5 — Regression and Baselines

**Designate Baselines explicitly — never infer them.** A Baseline (Volume X) is a
specific Execution's Result explicitly approved through the Approval Workflow (Volume
XII) as the reference standard for a Scenario. It is never the "last run" or the "most
recent passing result" — silent Baseline drift is exactly the kind of untracked change
the regression system exists to catch.

**Make Baselines reproducible.** A Baseline is only useful if the Execution it points
to can be reconstructed: the exact Dataset version, Contract version, Environment
configuration, and prompt version that produced it must be recoverable (Volume X). If
any of these changed between the Baseline Execution and the comparison Execution, the
regression signal may be caused by the changed input, not by the subject.

**Detect regressions by meaning, not by literal text.** A probabilistic system will
rarely reproduce identical output (Front Matter §8 — Semantic Regression). Detecting
regressions by character-for-character string comparison will produce constant false
positives. Use Oracles (Judges checking intent, Validators checking structure) to
assess whether the meaning of the output degraded, not whether its text changed.

**Surface Model Drift even when nothing visible changed.** A model provider can
silently update what a stable-looking model identifier resolves to (Volume X). When a
Regression Suite detects a Semantic Regression but the Environment shows no
configuration change, Model Drift is the most likely cause. A Regression Suite MUST be
capable of surfacing this — Deterministic Infrastructure guarantees the harness is
reproducible, not that the subject behind a stable API endpoint is fixed.

**Distinguish subject drift from Judge Drift.** Both produce the same visible symptom —
a Result that now diverges from its Baseline. Check whether Human Reviewer agreement
moved together with the Judge's verdicts: if only the Judge shifted while Human
agreement held steady, the Judge drifted, not the subject.

## I.6 — Governance

**Log every override explicitly.** Quality Gate overrides, Baseline approvals,
Contract modifications, and Release Decisions MUST pass through the Approval Workflow
(Volume XII) and be logged with the acting person, their Role, and the timestamp. A
silent override is invisible to Audit and breaks the Traceability chain a Release
Decision depends on.

**Separate Teams from Roles.** Teams scope what a person can see (which Projects and
Suites they have access to); Roles scope what they can do within that scope. These are
orthogonal, not nested — a person can hold one Role across multiple Teams, or different
Roles in different Teams.

**Make Permissions the unit of enforcement, not Roles.** A Role is a named convenience
for assigning Permissions; the system checks Permissions at the moment an action is
attempted. If Governance logic is written against Roles instead of Permissions,
changing a Role's Permission set can silently grant or revoke capabilities without
anyone noticing (Volume XII).

**Do not loosen a Contract to "fix" a failing Suite.** A Contract that is loosened to
restore a green build MUST be treated as a recorded Requirements or Risk decision, not
a quiet fix (Volume I, Chapter 1; Volume VIII — Test Maintainability). The loosened
threshold is now the Project's stated quality bar; if that bar is lower than intended,
the Contract change — not the failing Suite — is the defect.

## I.7 — CI/CD Integration

**Translate Quality Gate results, don't redefine them.** A CI/CD integration (Volume
XIII) translates an AQEF Quality Gate's pass/fail into a platform's native blocking
primitive — a GitHub status check, a GitLab pipeline status, an Azure release gate, a
Jenkins stage result. The AQEF Quality Gate (Volume I, Chapter 6) is defined once,
platform-agnostically; the native primitive is the translation, not a second
definition.

**Reflect Governance overrides in pipeline status.** If a Quality Gate failed but
Governance explicitly overrode it through the Approval Workflow, the CI/CD pipeline
status MUST reflect the override decision, not the raw failure (Volume XIII). Blocking
a deployment that Governance has explicitly approved misrepresents the actual Release
Decision made.

**Use the REST API as the single source of truth.** The CLI and every language SDK
(Volume XIV) are thin wrappers over the REST API — they MUST NOT independently
reimplement logic, add operations the API doesn't support, or behave differently from
each other for the same operation. If a CI/CD script works through the CLI but fails
through the Python SDK for the same inputs, the SDK has diverged from the API.

## I.8 — Extensibility

**Verify Validator Plugin determinism mechanically.** The Extension Lifecycle (Volume
XVI) MUST run a candidate Validator Plugin against a fixed input multiple times at
registration and reject it on any variance. This is not a test the plugin author runs
manually — it is an automated enforcement step the platform performs.

**Accept that Judge Plugin independence cannot be mechanically verified.** Unlike
Validator determinism, a Judge's independence from the system under test (Volume I,
Chapter 3) is a design-time and Contract-time judgment, not something the Plugin
Architecture can test at registration. A Judge Plugin's structure can be checked (does
it produce Confidence? are its criteria inspectable?), but whether it shares blind
spots with the subject is a Risk Analysis question, not an automated one.

**Never invalidate historical Results by deprecating a plugin.** A deprecated plugin's
Results remain valid historical evidence — including as a Baseline (Volume X) — even
after that plugin version is no longer installed. The same reasoning applies to Dataset
versions and Contract versions: changing the present MUST NOT retroactively rewrite the
past (Volume XVI).

**Version plugins like Datasets.** Every Execution's Result must be traceable to the
exact plugin version that produced or assessed it (Volume XVI). If a Validator Plugin
is updated and the new version produces different verdicts, the change should be
visible in the version history, not silently applied to ongoing comparisons.

## I.9 — Common Mistakes

The following mistakes are explicitly prohibited by the specification. Each is common
enough in practice to warrant direct naming.

| Mistake | Why It Fails | Source |
|---|---|---|
| Discarding a bad Result and re-running until the test passes | Retry is for infra failures only. The original Result MUST stand. | Volume III |
| Labeling an LLM-based check as a Validator | Probabilistic checks are Judges. Validators MUST be deterministic. | Volume V |
| Using the same model family for subject and Judge | Correlated blind spots. Independent Oracles MUST use different families. | Volume I, Ch. 3 |
| Skipping the Confidence Model and aggregating raw pass/fail | Discards Oracle uncertainty, treating guesses as facts. | Volume I, Ch. 6 |
| Averaging Safety failures into a weighted score | Safety is a hard veto. A good Semantic score cannot outvote a Safety violation. | Volume I, Ch. 6 |
| Detecting regressions by literal string comparison | Probabilistic subjects produce different text for the same intent. Use Semantic Regression. | Volume X |
| Silently overriding a Quality Gate without logging | Breaks the Traceability chain. Overrides MUST go through Approval Workflow. | Volume XII |
| Running the same model for "independence" in Multi-Judge | Repeated sampling tests stability, not independence. Purpose MUST be declared. | Volume VI |
| Loosening a Contract threshold to "fix" a failing test | The lowered bar is now the stated quality standard. Treat it as a Requirements decision. | Volume VIII |
| Letting a UI bypass Validator/Judge constraints | A UI that lets a user configure a Validator with Confidence contradicts Volume V. | Volume XV |
