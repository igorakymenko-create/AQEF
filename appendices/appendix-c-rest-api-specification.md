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
| GET | `/projects` | List all Projects the caller has access to. | Read |
| POST | `/projects` | Create a new Project. | Project create |
| GET | `/projects/{project}` | Retrieve Project details with Environments and Suites. | Read |
| PUT | `/projects/{project}` | Replace Project configuration. | Project edit |
| DELETE | `/projects/{project}` | Delete a Project and all its data. | Project delete |

**Environment**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/environments` | List Environments. | Read |
| POST | `/projects/{project}/environments` | Create an Environment. | Environment create |
| GET | `/projects/{project}/environments/{env}` | Retrieve Environment details. | Read |
| PUT | `/projects/{project}/environments/{env}` | Replace Environment configuration. | Environment edit |
| DELETE | `/projects/{project}/environments/{env}` | Delete an Environment. | Environment delete |

**Suite and Scenario**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/suites` | List Suites. | Read |
| POST | `/projects/{project}/suites` | Create a Suite. | Suite create |
| GET | `.../suites/{suite}` | Retrieve Suite with Scenarios. | Read |
| GET | `.../suites/{suite}/scenarios/{scenario}` | Retrieve a Scenario. | Read |
| POST | `.../suites/{suite}/scenarios` | Add a Scenario. | Scenario create |
| PUT | `.../suites/{suite}/scenarios/{scenario}` | Replace a Scenario. | Scenario edit |
| DELETE | `.../suites/{suite}/scenarios/{scenario}` | Remove a Scenario. | Scenario delete |

**Contract**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/contracts` | List Reusable Contracts. | Read |
| POST | `/projects/{project}/contracts` | Create a Contract. Governed by Approval Workflow. | Contract define |
| GET | `/projects/{project}/contracts/{contract}` | Retrieve a Contract. | Read |
| PUT | `/projects/{project}/contracts/{contract}` | Replace a Contract. Governed by Approval Workflow. | Contract define |

**Dataset**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/datasets` | List Datasets. | Read |
| POST | `/projects/{project}/datasets` | Create a Dataset (version MUST be specified). | Dataset create |
| GET | `/projects/{project}/datasets/{dataset}` | Retrieve Dataset metadata. | Read |
| GET | `/projects/{project}/datasets/{dataset}/rows` | Retrieve Dataset rows (paginated). | Read |
| POST | `/projects/{project}/datasets/{dataset}/versions` | Create a new version. | Dataset create |

**Execution**

| Method | Path | Description | Permission |
|---|---|---|---|
| POST | `/projects/{project}/executions` | Trigger Execution(s) for a Suite × Environment. | Execute |
| GET | `/projects/{project}/executions/{execution}` | Retrieve Execution status and metadata. | Read |
| GET | `.../executions/{execution}/conversation` | Retrieve the Conversation transcript. | Read |
| GET | `.../executions/{execution}/artifacts` | List Artifacts. | Read |
| GET | `.../executions/{execution}/results` | List Results (Validator + Judge). | Read |

**Triggering:** `POST /executions` accepts a body specifying `suite`, `environment`,
and optional `gates` to check after completion. The response returns a batch
identifier for tracking. Executions are asynchronous — the caller polls or subscribes
for completion.

**Baseline**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/baselines` | List approved Baselines. | Read |
| POST | `/projects/{project}/baselines` | Designate an Execution as Baseline. Governed by Approval Workflow. | Baseline approve |
| GET | `/projects/{project}/baselines/{baseline}` | Retrieve Baseline details. | Read |

**Quality Gate**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/gates` | List Gate definitions. | Read |
| POST | `/projects/{project}/gates` | Define a Quality Gate. | Gate define |
| POST | `/projects/{project}/gates/check` | Evaluate Gates against a set of Results. | Execute |
| POST | `/projects/{project}/gates/{gate}/override` | Override a failed Gate. Governed by Approval Workflow. | Gate override |

**Report and Release Decision**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/projects/{project}/reports` | List Reports. | Read |
| GET | `/projects/{project}/reports/{report}` | Retrieve a frozen Report. | Read |
| POST | `/projects/{project}/releases` | Record a Release Decision. Governed by Approval Workflow. | Release decide |
| GET | `/projects/{project}/releases` | List Release Decisions. | Read |

**Governance**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/teams` | List Teams. | Team read |
| POST | `/teams` | Create a Team. | Team admin |
| GET | `/roles` | List Roles and their Permissions. | Role read |
| POST | `/roles` | Create a Role. | Role admin |
| GET | `/projects/{project}/audit` | Query audit log (filtered by action type, date, actor). | Audit read |
| GET | `/projects/{project}/approvals` | List Approval Workflow records. | Audit read |

**Plugin**

| Method | Path | Description | Permission |
|---|---|---|---|
| GET | `/plugins` | List registered plugins. | Read |
| POST | `/plugins` | Register a plugin. Triggers mechanical verification for Validator Plugins. | Plugin register |
| GET | `/plugins/{plugin}` | Retrieve plugin details and version history. | Read |
| POST | `/plugins/{plugin}/deprecate` | Deprecate a plugin version. Historical Results remain valid. | Plugin admin |

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
operation itself and queryable through `GET /projects/{project}/audit`.

| Operation | Governed Action (Volume XII) |
|---|---|
| `POST /contracts` | Contract definition |
| `PUT /contracts/{contract}` | Contract modification |
| `POST /baselines` | Baseline approval |
| `POST /gates/{gate}/override` | Gate override |
| `POST /releases` | Release Decision |

## C.6 — Pagination and Filtering

List operations (GET on collection endpoints) MUST support pagination for unbounded
collections. The pagination mechanism is implementation-defined (cursor-based,
offset-based, etc.) but MUST be consistent across all endpoints.

List operations SHOULD support filtering by common fields:

- Executions: by suite, environment, date range, status.
- Results: by execution, oracle type, verdict.
- Audit log: by action type, actor, date range.
- Baselines: by scenario, environment.

## C.7 — Downstream Generation

This prose specification is the source from which a conformant implementation
generates:

1. A formal OpenAPI document — the machine-readable schema for the API surface.
2. Language SDKs — thin clients generated from the OpenAPI document (Volume XIV).
3. CLI commands — mapping directly to API operations (Volume XIV).

This generation chain ensures that the CLI, SDKs, and API cannot drift from each other
or from this specification. The generation step itself is an implementation concern,
not specified by AQEF.
