# Appendix C — REST API Specification

**Status:** confirmed (v0.1).

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

**Governance-integrated.** Every mutating operation checks the acting user's
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

**Triggering:** `POST /executions` accepts a body specifying `suite`, `environment`,
and optional `gates` to check after completion. The response returns a batch
identifier for tracking. Executions are asynchronous — the caller polls or subscribes
for completion.

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
| POST | `/projects/{project}/gates` | Define a Quality Gate. | `gate_define` |
| POST | `/projects/{project}/gates/check` | Evaluate Gates against a set of Results. | `execute` |
| POST | `/projects/{project}/gates/{gate}/override` | Override a failed Gate. Governed by Approval Workflow. | `gate_override` |

**Report and Release Decision**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/reports` | List Reports. | `read` |
| GET | `/projects/{project}/reports/{report}` | Retrieve a frozen Report. | `read` |
| POST | `/projects/{project}/releases` | Record a Release Decision. Governed by Approval Workflow. | `release_decide` |
| GET | `/projects/{project}/releases` | List Release Decisions. | `read` |

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
| POST | `/plugins` | Register a plugin. Triggers mechanical verification for Validator Plugins. | `plugin_register` |
| GET | `/plugins/{plugin}` | Retrieve plugin details and version history. | `read` |
| POST | `/plugins/{plugin}/deprecate` | Deprecate a plugin version. Historical Results remain valid. | `plugin_admin` |

## C.4 — Authentication and Authorization

All API operations MUST be authenticated. The authentication mechanism is
implementation-defined (API key, OAuth 2.0, etc.) but MUST resolve to a Person with
Team membership and Role assignments (Volume XII).

Every mutating operation MUST check the resolved Person's Permissions before
executing. If the Person lacks the required Permission, the API MUST reject the
request. Permission checks are against the atomic Permission, not the Role — Roles are
convenience groupings, Permissions are the enforcement unit.

## C.5 — Governance Side Effects

The following operations produce Governance audit log entries as a side effect. These
log entries are not separate API calls — they are automatically generated by the
operation itself and queryable through `GET /projects/{project}/audit`. The Governed
Action column uses the same identifiers as the Permission columns in §C.3 — these are
the same four actions Chapter 4 and Volume XII name, not a fifth: creating and modifying
a Contract are both instances of `contract_define`, since both are the same
Governance-controlled act of setting what a Contract requires.

| Operation | Governed Action (Volume XII) |
|---|---|
| `POST /contracts` | `contract_define` |
| `PUT /contracts/{contract}` | `contract_define` |
| `POST /baselines` | `baseline_approve` |
| `POST /gates/{gate}/override` | `gate_override` |
| `POST /releases` | `release_decide` |

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
| `oracle_type` | String | MUST | `validator`, `judge`, or `human_reviewer`. |
| `verdict` | String or `null` | MUST | `pass` or `fail`. `null` only when `disposition` is `awaiting_review` or `oracle_unavailable` — no verdict has been reached yet. |
| `confidence` | Float (0.0–1.0) or `"not_applicable"` | MUST | Never omitted and never bare `null`. `"not_applicable"` for every Validator Result (Volume V) and for any Result with no verdict yet. |
| `disposition` | String | MUST | `actionable`, `inconclusive`, `awaiting_review`, or `oracle_unavailable`. See below. |
| `supporting_evidence` | Any | MUST | What the Oracle based its judgment on — the Conversation, Artifacts, or specific excerpts, per Oracle type. |

**Disposition** is what closes the gap between "a Result exists" and "a Result is safe
to use in the Aggregation Model" — the distinction Chapter 6 already requires but never
previously named as a field:

- **`actionable`** — Confidence (where applicable) meets the Contract's threshold, or
  the Result is a Validator's, which is always actionable. The Aggregation Model MAY use
  this Result at face value.
- **`inconclusive`** — a Judge or Human Reviewer Result whose Confidence is below the
  Contract's `confidence_threshold` (Volume I, Chapter 6). Terminal for that specific
  Result; it MAY trigger Human Review, which produces a separate Result under the Human
  Reviewer Oracle, not a mutation of this one.
- **`awaiting_review`** — a Human Reviewer Result has been requested (Volume VI — Human
  Review) but not yet returned. `verdict` and `confidence` are absent because no
  judgment has been made yet. Volume XII's Approval Workflow governs how long this MAY
  persist; a Contract SHOULD specify a `review_timeout` (Appendix A) and an
  `on_timeout` policy so an unattended pipeline (Volume XIII) cannot block indefinitely.
  The default `on_timeout` policy, absent an explicit one, is to treat the Result as
  blocking — the same fail-safe posture Deterministic Infrastructure and Independent
  Oracles already assume elsewhere: an unresolved Oracle is not evidence of quality.
- **`oracle_unavailable`** — the Judge or Human Reviewer could not be reached, or did
  not respond, during Evaluation — a network timeout, a rate-limit response, a crash in
  the Judge Engine itself, occurring after Validation already passed. This is the
  Evaluation-stage counterpart to the infrastructure-level Retry Volume III already
  scopes to the Execution stage; the same prohibition applies without exception: an
  Oracle that could not be reached MUST NOT be silently retried until a favorable
  verdict appears, and MUST NOT be treated as an implicit pass. `verdict` is absent.

A Quality Gate (Volume I, Chapter 6) reading an aggregate that includes any Result whose
`disposition` is not `actionable` MUST treat that Result as blocking by default, unless
the Gate's own configuration explicitly states otherwise.

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
