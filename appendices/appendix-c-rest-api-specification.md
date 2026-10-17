# Appendix C — REST API Specification

This appendix specifies the REST API surface for an AQEF-conformant implementation. It
restates, in API-oriented terms, the operations implied by the Domain Model (Volume
II), the Execution Engine (Volume III), the Decision Pipeline (Volume I, Chapter 6),
Governance (Volume XII), and the SDK/API requirements (Volume XIV).

This is a prose specification, not a machine-readable OpenAPI document. A conformant
implementation's formal OpenAPI artifact SHOULD be generated from this specification by
that implementation's own tooling (see Scope, §6). The CLI and all language SDKs
(Python, Java, C#, JavaScript/TypeScript, Go) are thin wrappers over this API and MUST
NOT independently reimplement logic (Volume XIV).

## C.1 — Design Principles

**Single canonical surface.** The REST API is the only programmatic interface. The CLI,
SDKs, and Reference UI (Volume XV) are clients of this API, not independent systems.

**Resource-oriented.** Each Domain Model entity (Volume II) maps to a REST resource.
Operations follow standard HTTP semantics: GET for reads, POST for creation, PUT for
full replacement, PATCH for partial update, DELETE for removal.

**Governance-integrated.** Every mutating operation checks the acting Principal's
Permissions (Volume XII) before executing. Audit-relevant operations produce Governance
log entries as a side effect.

**Deterministic Infrastructure.** API operations that trigger Executions MUST produce
deterministic infrastructure behavior — the same API call with the same parameters and
the same Environment MUST produce comparable Execution conditions, even if the
subject's output varies (Volume I, Chapter 3).

## C.2 — Resource Model

**Primary Resources**

| Resource | Path | Volume | Description |
|---|---|---|---|
| Project | `/projects` | II | Top-level container. |
| Environment | `/projects/{project}/environments` | II | Runtime configuration. |
| Suite | `/projects/{project}/suites` | II | Scenario collection. |
| Scenario | `/projects/{project}/suites/{suite}/scenarios` | II | Test definition. |
| Contract | `/projects/{project}/contracts` | VII | Reusable Quality Contracts. |
| Dataset | `/projects/{project}/datasets` | IV | Versioned input data. |

**Execution Resources**

| Resource | Path | Volume | Description |
|---|---|---|---|
| Execution | `/projects/{project}/executions` | III | Runtime events. |
| Conversation | `/projects/{project}/executions/{execution}/conversation` | II | Produced transcript. |
| Artifact | `/projects/{project}/executions/{execution}/artifacts` | II | Captured auxiliary data. |
| Result | `/projects/{project}/executions/{execution}/results` | II | Oracle verdicts. |

**Decision Resources**

| Resource | Path | Volume | Description |
|---|---|---|---|
| Baseline | `/projects/{project}/baselines` | X | Designated reference Executions. |
| Snapshot | `/projects/{project}/snapshots` | X | Frozen release-point state. |
| Metric | `/projects/{project}/metrics` | II, XI | Aggregated measures. |
| Report | `/projects/{project}/reports` | XI | Frozen presentations. |
| Quality Gate | `/projects/{project}/gates` | I, Ch. 6 | Thresholded checks. |
| Release Decision | `/projects/{project}/releases` | I, Ch. 6; XII | Go/no-go records. |
| Release Policy | `/projects/{project}/release-policies` | XII | Standing authorizations for Release Decisions recorded by a Service Account. |
| Requalification | `/projects/{project}/requalifications` | VIII | Records that an Oracle configuration is requalified for a defect class. |

**Governance Resources**

| Resource | Path | Volume | Description |
|---|---|---|---|
| Team | `/teams` | XII | Organizational groupings. |
| Role | `/roles` | XII | Permission bundles. |
| Approval | `/projects/{project}/approvals` | XII | Workflow records. |
| Audit Log | `/projects/{project}/audit` | XII | Retrospective queries. |

**Extensibility Resources**

| Resource | Path | Volume | Description |
|---|---|---|---|
| Plugin | `/plugins` | XVI | Registered extensions. |

## C.3 — Operations by Resource

**Project**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects` | List all Projects the caller has access to. | `read` |
| POST | `/projects` | Create a new Project. | `project_create` |
| GET | `/projects/{project}` | Retrieve Project details with Environments and Suites. | `read` |
| PUT | `/projects/{project}` | Replace Project configuration. | `project_edit` |
| DELETE | `/projects/{project}` | Delete a Project and all its data. | `project_delete` |

**Environment**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/environments` | List Environments. | `read` |
| POST | `/projects/{project}/environments` | Create an Environment. | `environment_create` |
| GET | `/projects/{project}/environments/{env}` | Retrieve Environment details. | `read` |
| PUT | `/projects/{project}/environments/{env}` | Replace Environment configuration. | `environment_edit` |
| DELETE | `/projects/{project}/environments/{env}` | Delete an Environment. | `environment_delete` |

**Suite and Scenario**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/suites` | List Suites. | `read` |
| POST | `/projects/{project}/suites` | Create a Suite. | `suite_create` |
| GET | `.../suites/{suite}` | Retrieve Suite with Scenarios. | `read` |
| GET | `.../suites/{suite}/scenarios/{scenario}` | Retrieve a Scenario. | `read` |
| POST | `.../suites/{suite}/scenarios` | Add a Scenario. | `scenario_create` |
| PUT | `.../suites/{suite}/scenarios/{scenario}` | Replace a Scenario. | `scenario_edit` |
| DELETE | `.../suites/{suite}/scenarios/{scenario}` | Remove a Scenario. | `scenario_delete` |

**Contract**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/contracts` | List Reusable Contracts. | `read` |
| POST | `/projects/{project}/contracts` | Create a Contract. Governed by Approval Workflow. | `contract_define` |
| GET | `/projects/{project}/contracts/{contract}` | Retrieve a Contract. | `read` |
| PUT | `/projects/{project}/contracts/{contract}` | Replace a Contract. Governed by Approval Workflow. | `contract_define` |

**Dataset**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/datasets` | List Datasets. | `read` |
| POST | `/projects/{project}/datasets` | Create a Dataset (version MUST be specified). | `dataset_create` |
| GET | `/projects/{project}/datasets/{dataset}` | Retrieve Dataset metadata. | `read` |
| GET | `/projects/{project}/datasets/{dataset}/rows` | Retrieve Dataset rows (paginated). | `read` |
| POST | `/projects/{project}/datasets/{dataset}/versions` | Create a new version. | `dataset_create` |

**Execution**

| Method | Path | Description | Permission |
|---|---|---|---|
| POST | `/projects/{project}/executions` | Trigger Execution(s) for a Suite × Environment. | `execute` |
| GET | `/projects/{project}/executions/{execution}` | Retrieve Execution status and metadata. | `read` |
| GET | `.../executions/{execution}/conversation` | Retrieve the Conversation transcript. | `read` |
| GET | `.../executions/{execution}/artifacts` | List Artifacts. | `read` |
| GET | `.../executions/{execution}/results` | List Results (Validator + Judge). | `read` |
| POST | `.../executions/{execution}/results/{result}/review` | Record a Human Reviewer's verdict on this Result: completes it if it is `awaiting_review`, otherwise records a new Human Reviewer Result that resolves it. | `review` |
| POST | `.../executions/{execution}/results/{result}/reassess` | Have an Oracle assess the stored Evidence again for this Result's clause, as a new Result that resolves it. The subject is not invoked. | `execute` |

**Review and re-assessment** carry out Result Resolution (Volume I, Chapter 6); both
MUST be rejected where it does not allow the resolution requested.

- `review`: the body gives `verdict`, `confidence` where the review captures one, and
  `supporting_evidence`. The Principal MUST be a Person holding `review` and, where the
  clause names a `human_reviewer.role` (Appendix A §A.5), that Role, or the
  `escalate_to` Role once the review has been escalated. A Result that is
  neither `awaiting_review` nor open to resolution by a Human Reviewer is not reviewed.
- `reassess`: the body names the `oracle` configuration to use. It MUST be rejected for
  the same Oracle configuration unless the Result is `oracle_unavailable`, and for an
  Oracle without a Requalification record (below) for every defect class in the
  Result's `invalidated_by` (Volume VIII).

**Triggering:** `POST /executions` accepts a body specifying `suite`, `environment`,
and optional `gates` to check after completion. The response returns a batch
identifier for tracking. Executions are asynchronous — the caller polls or subscribes
for completion.

**Seeded Control Reporting:** whenever an Execution ran one or more Seeded Controls
(Volume VIII), `GET .../executions/{execution}` MUST include a `seeded_control_results`
array, one entry per Seeded Control Scenario in that run:

| Field | Type | Description |
|---|---|---|
| `scenario` | String | The Seeded Control Scenario. |
| `defect_class` | String | From Appendix A §A.4's `SeededControlConfig`. |
| `outcome` | String | `caught`, `missed`, or `invalid` (presence of the planted defect not confirmed: confirmation failed, or not yet recorded, Volume VIII). |
| `confirmed_by` | String | The control's declared method: `validator`, `human_reviewer`, or `construction` (Appendix A §A.4). |
| `invalidation_scope` | String | `none` (when `outcome` is `caught` or `invalid`), `defect_class`, or `full_run`. |
| `reason` | String or `null` | MUST be present and non-empty when `invalidation_scope` is `full_run` (Volume VIII); `null` otherwise. |

This is deliberately how a missed Seeded Control is surfaced, rather than as a change to
the Results it affects: the Results an Oracle produced in the run for the affected
clauses are invalidated (Volume VIII), but every one of them stays exactly as recorded.
`seeded_control_results` is where the invalidation is recorded, once, and what tells a
caller *why* and at *what scope*; each affected Result's derived `invalidated_by` field
(§C.7) points back to the entry here.

Where the Oracle was not invoked for clauses after a miss (Volume VIII, failing fast),
their Results carry `not_assessed` (§C.7). Where the Project's `on_seeded_control_miss`
is `halt_run` (Appendix A §A.9), the entry's `invalidation_scope` is `full_run` and its
`reason` is set automatically to the configured policy. Under `full_run`, no Result of
that run counts as `actionable` for any Quality Gate, whatever its defect class (Volume
VIII).

| Method | Path | Description | Permission |
|---|---|---|---|
| POST | `.../executions/{execution}/seeded-controls/{scenario}/invalidate` | Declare full-run invalidation for a Seeded Control missed in this Execution. Body MUST include a non-empty `reason`. | `seeded_control_invalidate` |
| POST | `.../executions/{execution}/seeded-controls/{scenario}/confirm` | Record a Human Reviewer's confirmation that the planted defect is present in the Evidence the Oracle received, for a control with `confirmed_by: human_reviewer` (Volume VIII). The Principal MUST be a Person. Until it is recorded, the control is `invalid` for the run. | `review` |

`seeded_control_invalidate` is an ordinary checked Permission, not one of Governance's
four Approval-Workflow-gated actions (Volume XII) — full-run invalidation is a per-miss
judgment call, not a standing configuration, and Volume VIII keeps its governance at
SHOULD, not MUST. A logged call to this endpoint is queryable like any other
Governance-controlled action through `GET /projects/{project}/audit`.

**Requalification**

| Method | Path | Description | Permission |
|---|---|---|---|
| POST | `/projects/{project}/requalifications` | Record that an Oracle configuration is requalified for a defect class (Volume VIII — Requalification). Body names the `oracle`, the `defect_class`, and the Seeded Control Results it rests on. MUST be rejected unless each named control is of that class, was `caught` by that Oracle configuration, and is not a control any Oracle missed in a run whose Results the requalification will be used to re-assess. | `execute` |
| GET | `/projects/{project}/requalifications` | List Requalification records. | `read` |

| Field | Type | Description |
|---|---|---|
| `id` | String | Identifier of the record. |
| `oracle` | String | The Oracle configuration requalified, as in a Result's `oracle` (§C.7). |
| `defect_class` | String | The class it is requalified for. |
| `controls` | List of String | The Seeded Control Results, by Result `id`, it rests on. |
| `recorded_at` | DateTime | When the record was made. |
| `recorded_by` | String | The Principal who made it. |

A Requalification record is never modified. An Oracle is requalified for a class only
where such a record exists; `reassess` (above) relies on it.

**Snapshot**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/snapshots` | List Snapshots. | `read` |
| GET | `/projects/{project}/snapshots/{snapshot}` | Retrieve a Snapshot (Appendix A §A.13). | `read` |
| POST | `/projects/{project}/snapshots` | Capture a Snapshot explicitly, for Snapshot Comparison (Volume X). | `snapshot_create` |

A Snapshot is also captured automatically by `POST .../gates/check` (below). No
operation modifies or replaces a Snapshot.

**Baseline**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/baselines` | List approved Baselines. | `read` |
| POST | `/projects/{project}/baselines` | Designate an Execution as Baseline. Governed by Approval Workflow. | `baseline_approve` |
| GET | `/projects/{project}/baselines/{baseline}` | Retrieve Baseline details. | `read` |

**Quality Gate**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/gates` | List Gate definitions. | `read` |
| POST | `/projects/{project}/gates` | Define a Quality Gate. Governed by Approval Workflow. | `contract_define` |
| PUT | `/projects/{project}/gates/{gate}` | Change a Quality Gate (threshold, `min_basis`, `on_failure`). Governed by Approval Workflow. | `contract_define` |
| POST | `/projects/{project}/gates/check` | Evaluate Gates against a set of Results. Returns one GateResult (Appendix A §A.12) per Gate and the `snapshot_id` captured for the evaluation. | `execute` |
| POST | `/projects/{project}/gates/{gate}/override` | Override one failed blocking GateResult. Body MUST name the GateResult by its `id` (Appendix A §A.12), give its `execution_batch_id`, and include a non-empty justification. Applies to that GateResult only. Governed by Approval Workflow. | `gate_override` |

**Aggregate Basis Reporting:** the response to `POST /projects/{project}/gates/check`,
and every per-gate entry in a Release Decision, MUST include a `basis` object for the
aggregate that Gate read (Volume I, Chapter 6):

| Field | Type | Description |
|---|---|---|
| `results` | Integer | Effective Results whose effective state is `actionable` that the aggregate was computed from. |
| `not_actionable` | Integer | Effective Results in the same scope whose effective state is not `actionable` (§C.7), invalidated ones included, and stale ones (Volume I, Chapter 6). |
| `scenarios` | Integer | Distinct Scenarios those Results came from. |
| `executions` | Integer | Distinct Executions those Results came from. |
| `min_basis_met` | Boolean or `"not_declared"` | Whether the Gate's `min_basis` (Appendix A §A.10) was met. `"not_declared"` when the Gate sets none. Never bare `null`. |

`"not_declared"` follows the same pattern as `"not_applicable"` for Confidence (§C.7) and
`"not_established"` for a difficulty prior: a Gate that set no minimum and a Gate whose
minimum was met are different facts and MUST NOT be reported the same way. Seeded Control
Results are not counted in any field above.

**Report and Release Decision**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/reports` | List Reports. | `read` |
| GET | `/projects/{project}/reports/{report}` | Retrieve a frozen Report, in the shape of §C.10. | `read` |
| POST | `/projects/{project}/releases` | Record a Release Decision. MUST be rejected if a Contract, Quality Gate, or Environment in its scope differs from its `snapshot_id`, or if no Quality Gate applies to its scope (Volume I, Chapter 6). Governed by Approval Workflow. | `release_decide` |
| GET | `/projects/{project}/releases` | List Release Decisions. | `read` |

**Release Policy**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/release-policies` | List Release Policies, revoked ones included. | `read` |
| POST | `/projects/{project}/release-policies` | Approve a Release Policy (Appendix A §A.14). The Principal MUST be a Person. Governed by Approval Workflow. | `release_decide` |
| GET | `/projects/{project}/release-policies/{policy}` | Retrieve a Release Policy. | `read` |
| POST | `/projects/{project}/release-policies/{policy}/revoke` | Revoke a Release Policy. The Principal MUST be a Person. | `release_decide` |

No operation modifies a Release Policy; a different policy is approved as a new one.

**Governance**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/teams` | List Teams. | `team_read` |
| POST | `/teams` | Create a Team. | `team_admin` |
| GET | `/roles` | List Roles and their Permissions. | `role_read` |
| POST | `/roles` | Create a Role. | `role_admin` |
| GET | `/projects/{project}/audit` | Query audit log (filtered by action type, date, actor). | `audit_read` |
| GET | `/projects/{project}/approvals` | List Approval Workflow records. | `audit_read` |

**Plugin**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/plugins` | List registered plugins. | `read` |
| POST | `/plugins` | Register a plugin. Triggers the repeatability check for Validator Plugins (Volume XVI). | `plugin_register` |
| GET | `/plugins/{plugin}` | Retrieve plugin details and version history. | `read` |
| POST | `/plugins/{plugin}/deprecate` | Deprecate a plugin version. Historical Results remain valid. | `plugin_admin` |

## C.4 — Authentication and Authorization

All API operations MUST be authenticated. The authentication mechanism is
implementation-defined (API key, OAuth 2.0, etc.) but MUST resolve to a Principal — a
Person or a Service Account with an owning Person — with Team membership and Role
assignments (Volume XII — Principals).

Every mutating operation MUST check the resolved Principal's Permissions before
executing. If the Principal lacks the required Permission, the API MUST reject the
request. Approving `baseline_approve` or `gate_override` additionally requires the
Principal to be a Person; a Service Account MAY apply `contract_define` only with a
reference to an external review approved by a Person, and MAY record a Release Decision
only under a standing release policy (Volume XII). Permission checks are against the atomic Permission, not the Role — Roles are
convenience groupings, Permissions are the enforcement unit.

## C.5 — Governance Side Effects

The following operations produce Governance audit log entries as a side effect. These
log entries are not separate API calls — they are automatically generated by the
operation itself and queryable through `GET /projects/{project}/audit`. The Governed
Action column uses the same identifiers as the Permission columns in §C.3 — these are
the same four actions Chapter 4 and Volume XII name, not a fifth: creating and modifying
a Contract are both instances of `contract_define`, since both are the same
Governance-controlled act of setting what a Contract requires, and so are defining and
changing a Quality Gate, which sets what a release must show (Volume XII).

| Operation | Governed Action (Volume XII) |
|---|---|
| `POST /contracts` | `contract_define` |
| `PUT /contracts/{contract}` | `contract_define` |
| `POST /gates` | `contract_define` |
| `PUT /gates/{gate}` | `contract_define` |
| `POST /baselines` | `baseline_approve` |
| `POST /gates/{gate}/override` | `gate_override` |
| `POST /releases` | `release_decide` |
| `POST /release-policies` | `release_decide` |
| `POST /release-policies/{policy}/revoke` | `release_decide` |

The table names the operations made for these actions, not the only ones that can carry
them. Any operation that creates or changes a `contract`, `contracts`, or
`quality_gates` value, on whatever resource (a Project, a Suite, or a Scenario), is
`contract_define` as well as that operation's own Permission, and is governed and logged
the same way.

## C.6 — Pagination and Filtering

List operations (GET on collection endpoints) MUST support pagination for unbounded
collections. The pagination mechanism is implementation-defined (cursor-based,
offset-based, etc.) but MUST be consistent across all endpoints.

List operations SHOULD support filtering by common fields:

- Executions: by suite, environment, date range, status.
- Results: by execution, oracle type, verdict.
- Audit log: by action type, actor, date range.
- Baselines: by scenario, environment.

## C.7 — Result Response Shape

Every Oracle produces a Result (Volume II), and Chapter 6's Decision Pipeline depends on
distinctions this specification states in prose — an explicit Confidence-inapplicable
declaration (Volume I, Chapter 3 — "Everything has Confidence"), and a Result that is
not yet actionable (Volume I, Chapter 6 — Confidence Model) — without previously giving
Result a concrete shape anywhere. This section is that shape; Appendix A and B specify
configuration entities, but Result is runtime output, so it belongs here.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Unique identifier of this Result. |
| `execution` | String | MUST | The Execution whose Evidence was assessed. |
| `clause` | String | MUST | The Contract clause applied: a stable reference to the clause within the Contract version in force for that Execution, using the clause's `id` (Appendix A §A.5) where it declares one. |
| `resolves` | String | MAY | The `id` of an earlier Result for the same `execution` and `clause` that this Result resolves (Volume I, Chapter 6 — Result Resolution). Absent otherwise. |
| `oracle_type` | String | MUST | `validator`, `judge`, or `human_reviewer`. |
| `oracle` | String | MUST | Which Oracle configuration produced this Result, with its version: a Validator's name and version (a plugin's included), a Judge's model and criteria configuration, or, for a Human Reviewer, the review role. The reviewing Person is recorded in `supporting_evidence`. What "the same Oracle" and "a requalified Oracle" mean (Volume I, Chapter 6; Volume VIII) is decided against this field. |
| `verdict` | String or `null` | MUST | `pass` or `fail`. `null` only when `disposition` is `awaiting_review`, `oracle_unavailable`, or `not_assessed` — no verdict has been reached. |
| `confidence` | Float (0.0–1.0) or `"not_applicable"` | MUST | Never omitted and never bare `null`. `"not_applicable"` for every Validator Result (Volume V), for a Human Reviewer Result whose review captures no Confidence (Volume II; Appendix A §A.5, `captures_confidence`), and for any Result with no verdict yet. |
| `disposition` | String | MUST | `actionable`, `inconclusive`, `awaiting_review`, `oracle_unavailable`, or `not_assessed`. See below. |
| `supporting_evidence` | Any | MUST | What the Oracle based its judgment on — the Conversation, Artifacts, or specific excerpts, per Oracle type. |
| `recorded_at` | DateTime | MUST | When this Result was recorded. A Result that completes from `awaiting_review` keeps it; when the review returned is in `supporting_evidence`. |
| `panel` | Object | MUST (Multi Judge Results); absent otherwise | `{ configured: Integer, counted: Integer }` — Judges configured in the panel, and Judges whose verdicts were counted after exclusions (Volume VI). In a stability configuration, samples configured (`samples`) and samples counted. |
| `assertions` | Integer | MUST (Judge Result over several assertions); absent otherwise | The number of independent assertions the Judge's criterion spans, where it spans more than one (Volume VI — Single Judge). Its presence declares the verdict and Confidence an aggregate over those assertions; its absence declares them a verdict on a single one. |
| `invalidated_by` | List of `{ scenario: String, defect_class: String }` | Read-only, derived | Present in a response when one or more missed Seeded Controls invalidate this Result for its run: one entry per control (§C.3, `seeded_control_results`). The Result stays invalidated while any entry remains applicable; it leaves that state only by being resolved (Volume I, Chapter 6). Never stored on the Result, and never set by a client. |

**Disposition** is what closes the gap between "a Result exists" and "a Result is safe
to use in the Aggregation Model" — the distinction Chapter 6 already requires but never
previously named as a field:

- **`actionable`** — Confidence (where applicable) meets the Contract's threshold, or the Result is a Validator's that reached a verdict, which is always actionable. The Aggregation Model MAY use
  this Result at face value.
- **`inconclusive`** — a Judge or Human Reviewer Result whose Confidence is below the
  Contract's `confidence_threshold` (Volume I, Chapter 6). Terminal for that specific
  Result; it MAY trigger Human Review, which produces a separate Result under the Human
  Reviewer Oracle, not a mutation of this one. That Result resolves this one
  (`resolves`, above).
- **`awaiting_review`** — a Human Reviewer Result has been requested (Volume VI — Human
  Review) but not yet returned. No judgment has been made yet: `verdict` is
  `null` and `confidence` is `"not_applicable"`, markers that no judgment exists, never a
  default verdict or a zero score. This is the one disposition a Result leaves: it
  completes once the review returns. Volume XII's Approval Workflow governs how long this MAY
  persist; a Contract SHOULD specify a `review_timeout` (Appendix A) and an
  `on_timeout` policy so an unattended pipeline (Volume XIII) cannot block indefinitely.
  The default `on_timeout` policy, absent an explicit one, is to treat the Result as
  blocking — the same fail-safe posture Deterministic Infrastructure and Independent
  Oracles already assume elsewhere: an unresolved Oracle is not evidence of quality.
- **`oracle_unavailable`** — the Oracle could not be reached, did not respond, or could
  not complete its check — a network timeout, a rate-limit response, a crash in the
  Judge Engine, in a Validator, or in a plugin (Volume XVI — Plugin Invocation). For a
  Judge or Human Reviewer this happens during Evaluation, after Validation passed; for a
  Validator, during Validation, which then has not passed (Volume V — Validator SDK). This is the
  Evaluation-stage counterpart to the infrastructure-level Retry Volume III already
  scopes to the Execution stage; the same prohibition applies without exception: an
  Oracle that could not be reached MUST NOT be silently retried until a favorable
  verdict appears, and MUST NOT be treated as an implicit pass. `verdict` is `null`.
  Re-attempting a call that failed before any verdict was returned is not such a retry
  (Volume VI — Human Review); `oracle_unavailable` is what remains when every attempt
  failed.
- **`not_assessed`** — the Oracle was deliberately not invoked: it had missed a Seeded
  Control of the clause's defect class earlier in the same run (Volume VIII), or a Multi
  Judge panel fell below its quorum (Volume VI). `verdict` is `null`. The Evidence is
  kept, and a requalified Oracle MAY assess it later as a new Result, which resolves this
  one; this Result is not modified.

A Result's **effective state** is `invalidated` when `invalidated_by` has at least one
entry, and its `disposition` otherwise (Volume I, Chapter 6 — Result Resolution). A Quality Gate
reading an aggregate that includes any effective Result whose effective state is not
`actionable` MUST treat that Result as blocking. There is no configuration that turns
this off: the way past a non-`actionable` Result is to resolve it, or, for a blocking
Gate, an override approved for that one Gate Result (Volume XII). A Result that another
Result `resolves` is not counted again.

## C.8 — Deletion and Referential Integrity

Volume XVI already states the correct principle for one case: deprecating a plugin "MUST
NOT silently invalidate Baselines or Results a retired version already produced." The
same reasoning applies without exception to every `DELETE` operation this Appendix
exposes, not only to plugin deprecation:

- **`DELETE` MUST NOT silently invalidate a Baseline, a Snapshot, a Report, or an audit
  record that references the deleted entity.** A Baseline's Traceability chain (Volume
  XII) depends on being able to reconstruct the exact Environment, Dataset version, and
  Contract version an Execution ran under — deleting an Environment a Baseline still
  references MUST be rejected, or the reference MUST be preserved as a frozen historical
  record (implementation-defined which, but not silently broken).
- **`DELETE /projects/{project}` MUST NOT be permitted while the Project has Baselines,
  Reports, or audit records unless the caller explicitly requests their retention or
  their deletion is separately, explicitly authorized.** Deleting a Project's live
  configuration and deleting its history are different, separately consequential
  actions, and Governance (Volume XII) MUST be able to distinguish which one a request
  is actually asking for.
- **Every destructive operation in this Appendix requires a Permission** (Volume XII):
  `project_delete`, `environment_delete`, `scenario_delete`, in addition to the
  create/edit Permissions already listed per resource in §C.3.

## C.9 — Downstream Generation

This prose specification is the source from which a conformant implementation
generates:

1. A formal OpenAPI document — the machine-readable schema for the API surface.
2. Language SDKs — thin clients generated from the OpenAPI document (Volume XIV).
3. CLI commands — mapping directly to API operations (Volume XIV).

This generation chain ensures that the CLI, SDKs, and API cannot drift from each other
or from this specification. The generation step itself is an implementation concern,
not specified by AQEF.

## C.10 — Report Response Shape

A Report (Volume XI) is retrieved through the API in this shape. How it is rendered for
people is the implementation's choice; what it contains is not. It is frozen when
generated: no field changes afterwards.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | String | MUST | Report identifier, as referenced by a Release Decision's `report_id`. |
| `generated_at` | DateTime | MUST | When the Report was generated and frozen. |
| `scope` | Object | MUST | `{ project, suites, environments, execution_batch_ids }`: what the Report covers. |
| `snapshot_id` | String | MAY | The Snapshot of the evaluation its GateResults come from, where Gates were evaluated. |
| `gates` | Map of String → GateResult | MUST | For every Quality Gate applicable to the scope, the latest GateResult (Appendix A §A.12) at generation time, with its `basis`, `reasons`, and `override`. Empty only where no Gate applies. |
| `metrics` | List of Object | MUST | Each Metric shown, with its definition and the `id`s of the Results it was computed from, or a query that returns exactly them. |
| `signals` | Signals | MUST | The signals Volume XI requires a Report to surface (below). |

**Signals.** Each field is a list, empty when nothing applies, and never omitted.

| Field | Content |
|---|---|
| `retries` | Per Scenario, the number of infrastructure-level Retries (Volume III) in scope. |
| `low_confidence` | Per Scenario and per Oracle, the number of `inconclusive` Results and the number of Results in scope. |
| `multi_judge` | Per clause assessed by a Multi Judge panel, its `purpose` (`independence` or `stability`). |
| `unenforced_boundaries` | Every Environment in scope whose Action Boundary declares `enforced: false`. |
| `boundary_attempts` | Every recorded attempt to cross an Action Boundary and every Tripwire touch: Execution, target, whether blocked, whether a Tripwire. |
