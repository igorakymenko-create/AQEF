# AQEF CTS Harness Contract

**Version:** 0.7. **For:** AQEF Conformance Test Specification Working Draft 10; AQEF
Working Draft 0.41.5.

**Status:** Draft. Harnesses built to versions 0.5 and 0.6 ran CTS Working Drafts 8 and 9
against a reference implementation; this version carries what those runs showed.

**License:** CC BY 4.0, as the specification.

## 0. Status and precedence

This document specifies the test infrastructure that runs the AQEF Conformance Test
Specification (CTS): a runner, an adapter between the runner and the implementation
under test, the scripted subject and Judge, and the records they keep. It is a separate,
non-normative document, versioned on its own.

It adds nothing to what AQEF requires of an implementation, and nothing to what a CTS
test checks:

- **Precedence.** Where this document and AQEF disagree about what an implementation
  must do, AQEF is right. Where this document and the CTS disagree about what a test
  checks or how its outcome is decided, the CTS is right. A disagreement is reported
  and resolved by correcting this document, never by reinterpreting AQEF.
- **Normative words.** In this document, MUST, SHOULD, and MAY bind a harness, an
  adapter, or a runner. They never bind an AQEF implementation.
- **Optional hooks.** Where this document mentions a hook an implementation could
  offer (a fault hook, a clock), the hook is optional. Its absence is never a failure of
  the implementation; at most, it leaves a requirement unverified (CTS 1.7).

## 1. Scope

In scope: orchestration of CTS tests, the adapter interface, the scripted subject and
Judge, fault and time control, fixtures and isolation, identities, evidence and its
integrity, manual review, outcome attribution, and the run report.

Out of scope: the design of an AQEF implementation; certification of anything or
anyone (AQEF §10: conformance is a property of an implementation, never of a person);
any interface an implementation must offer beyond what AQEF already specifies; the
code of a harness or adapter.

Running a test with a harness that meets this contract does not show conformance. A
test report shows how the tests came out for one implementation, against its own
Conformance Statement (CTS 0.2).

## 2. Architecture and terms

```
CTS runner ─► fixture builder ─► adapter ─► SUT (the AQEF implementation)
     │                                         │
     │                                         ▼  model calls
     └──────────── harness ◄──────── scripted subject / Judge / generator / tools
                      │
                      ▼
               evidence store ◄─── manual review desk (Inspection, Declaration)
```

| Term | Meaning |
|---|---|
| SUT | The AQEF implementation under test. |
| Runner | Schedules tests and cases, isolates them, decides outcomes, writes the report. |
| Adapter | Maps the runner's operations (§5.5) to the SUT's surface: Appendix C REST, or an equivalent surface (§6). |
| Harness | Hosts the scripted subject, Judge, generator, and tool targets; records every call; injects faults; keeps time. |
| Session | One case's harness state: behaviors, counters, call log. |
| Namespace | One case's Project in the SUT, its session, and its correlation IDs. |
| Probe | A recorded request that shows whether the SUT offers an operation (§6). |
| Observation | A record the runner reads to decide an outcome: an SUT response or a harness event. |
| Run profile | The run's settings: budgets, drain time, allowlists, credential references. |

## 3. Principles

1. **No hidden PASS.** When setup or observation cannot be completed, the outcome is
   `NOT_RUN`, never `PASS` (§7).
2. **SUT outcomes are kept, not judged, by the adapter.** The adapter reports what the
   SUT did, accepted or rejected, with the raw response. Only the runner, applying the
   test's **Expected**, decides `PASS` or `FAIL`.
3. **Adapter neutrality.** Mapping may rename fields; it never changes a verdict,
   disposition, status, error, or count, and never hides an SUT response.
4. **Replayable.** Every run records the versions of AQEF, the CTS, this contract, the
   harness, the adapter, and the SUT, and every behavior and fixture used.
5. **Negative claims need closed observation.** "The Judge was not called" is shown by a
   closed, complete call log for the case (§11), not by the absence of a sample.
6. **Isolation.** No state is shared between cases (§10).
7. **Safety.** Faults, destructive operations, and outbound calls run only against a
   test instance the run profile names (§17).

## 4. Package, versions, transport

| File | Content |
|---|---|
| `harness-contract.md` | This document. |
| `schemas/common.schema.json` | Shared definitions: IDs, outcomes, operations, reason codes. |
| `schemas/adapter-operation.schema.json` | Request envelope (§5.1), with typed arguments (§5.5). |
| `schemas/adapter-response.schema.json` | Response envelope (§5.2), with the SUT exchange (§5.3). |
| `schemas/adapter-error.schema.json` | Error with origin and phase (§5.4). |
| `schemas/adapter-manifest.schema.json` | What an adapter and harness offer (§6). |
| `schemas/harness-event.schema.json` | One observation in the event log (§11, §12). |
| `schemas/evidence-manifest.schema.json` | Index and digests of all evidence of a run (§12). |
| `schemas/fixture-recipe.schema.json` | Machine form of a CTS fixture (§10). |
| `schemas/manual-review.schema.json` | One reviewer's decision (§13). |
| `schemas/cts-report.schema.json` | The run report (§15). |
| `examples/` | Valid examples; `examples/invalid/` holds envelopes that must be rejected; `examples/evidence/` holds the evidence objects of the example report. |
| `fixtures/` | Recipes for the postcondition fixtures of CTS 2.7. |
| `tools/validate.py` | Checks the package, and verifies a run's report against the CTS and its evidence (§18). |
| `tools/test_validate.py` | Unit tests of every check of `validate.py`, on valid cases and on cases built to break it. |

- **Schemas** use JSON Schema 2020-12. Their `$id`s are identifiers, not download
  locations, and carry the contract version.
- **Versioning.** This contract is versioned on its own, as `major.minor`. Every
  envelope, record, and report carries `contract_version` (or `schema_version`). While
  the major version is 0, a runner MUST reject a document whose version differs from
  its own, before any SUT call. Each version names the CTS draft and AQEF versions it
  was written for (front matter); §19 lists what changed.
- **Transport.** The reference transport is HTTPS with one JSON envelope per request
  and per response. An in-process binding MAY be used if it exchanges the same
  envelopes, each valid against the schemas; equality is of the parsed JSON, not of its
  bytes.

## 5. Adapter protocol

### 5.1 Request

Every request carries `contract_version`, `operation`, `run_id`, `case_id`,
`session_id`, `correlation_id`, `timeout_ms`, and `arguments`; it MAY carry
`actor_ref` (the Principal the SUT request is made as, CTS 14.1) and
`idempotency_key`. `case_id` is a CTS test ID or case ID (CTS 1.2, Cases). `timeout_ms`
bounds one operation; a test's waiting budget (CTS 1.6, Waiting) is separate and can
span many operations. An invalid request is rejected before anything is sent to the
SUT.

### 5.2 Response

A response echoes `operation` and `correlation_id`, and carries `success` and exactly
one of `data` or `error`. `success: true` means the adapter obtained an outcome from the
SUT, or the harness carried out its own operation. It says nothing about whether that
outcome is the one the test expects.

### 5.3 The SUT exchange

For every operation that reaches the SUT, `data.sut` records:

| Field | Content |
|---|---|
| `outcome` | `accepted` (the SUT carried out the request) or `rejected` (it refused, with an error of its own). |
| `status` | The HTTP status, or the equivalent surface's code. |
| `error_code` | The SUT's own error code, if it returned one. |
| `body_ref`, `body_sha256` | The unmodified SUT response, stored as evidence before any mapping (§12). |
| `resource_refs` | References to what the request created or returned. |

A rejection is an outcome, not an error: many tests expect one (a configuration missing
a required field, a Principal without a Permission). `data.normalized` MAY add
field-name aliases for the runner; it never changes meaning.

### 5.4 Errors

An error means that no SUT outcome was obtained. It carries `origin` (`harness`,
`adapter`, `network`, `sut`), `phase` (`preflight`, `setup`, `action`, `observation`,
`cleanup`), a `code`, a message, and whether a retry could help. Codes:

| Code | Origin | Meaning |
|---|---|---|
| `CONTRACT_VERSION_MISMATCH` | adapter | Envelope version differs from the adapter's. |
| `SCHEMA_INVALID` | adapter | Envelope or arguments fail their schema. |
| `ADAPTER_SURFACE_UNSUPPORTED` | adapter | The adapter has no mapping for the operation. Not evidence about the SUT (§6). |
| `ADAPTER_MAPPING_FAILED` | adapter | The mapping exists but failed. |
| `CREDENTIAL_UNAVAILABLE` | adapter | The actor's credentials could not be obtained. |
| `HARNESS_SETUP_FAILED` | harness | A harness prerequisite could not be established. |
| `HARNESS_SELF_TEST_FAILED` | harness | A behavior failed its self-test (CTS 2.8). |
| `HARNESS_INTERNAL` | harness | Any other harness fault. |
| `SUT_TRANSPORT_FAILED` | network | The connection to the SUT failed before any response. |
| `SUT_TIMEOUT` | sut | No response within `timeout_ms`. |
| `SUT_SERVER_ERROR` | sut | The SUT answered with a server error (5xx or equivalent) instead of an outcome. |
| `SUT_MALFORMED_RESPONSE` | sut | The SUT answered, but not in a form the surface defines. |
| `OBSERVATION_INCOMPLETE` | harness | The observation a request needed could not be completed. |
| `OPERATION_TIMEOUT` | adapter | The adapter's own processing exceeded `timeout_ms`. |

Further codes MAY be added with the prefix `X-`; a runner treats an unknown code by its
origin and phase.

### 5.5 Operation catalog

Every operation the CTS needs, with the SUT operation it maps to on the Appendix C
surface. "Typed" operations have their arguments fixed in
`adapter-operation.schema.json` (`$defs/args`).

| Operation | SUT operation (Appendix C) | Used by | Typed |
|---|---|---|---|
| `describe` | — (returns the manifest) | every run | yes |
| `begin_case` | — (allocates namespace and session) | every case | yes |
| `end_case` | — | every case | yes |
| `cleanup` | deletes what the case created | every case | yes |
| `provision_principal` | `POST /roles`, `POST /teams`, and the identity provider | CTS 14.1 | yes |
| `load_config` | `POST /projects` or `PUT /projects/{project}` | Section 10; every fixture | yes |
| `get_config` | `GET` on the resource | CT-REL-030 | |
| `update_config` | `PUT`/`POST` on the changed resource, with Approval Workflow | "a governed change", CTS 14.1 | |
| `delete_resource` | `DELETE` on the resource | CT-REL-022, CT-REL-034 | |
| `register_dataset` | `POST /projects/{project}/datasets` | CT-CFG-017 | |
| `create_dataset_version` | `POST .../datasets/{dataset}/versions` | CT-REL-034 | |
| `generate_dataset` | as the implementation documents | CT-DSR-003 | |
| `get_dataset` | `GET .../datasets/{dataset}`, `.../rows` | Section 24 | |
| `execute` | `POST /projects/{project}/executions` | every run | yes |
| `poll_execution` | `GET .../executions/{execution}` until terminal | every run | yes |
| `list_executions` | `GET /projects/{project}/executions` | CT-API-001 | |
| `get_execution` | `GET .../executions/{execution}` | `seeded_control_results`, scheduling records | |
| `get_conversation` | `GET .../executions/{execution}/conversation` | Section 11 | yes |
| `get_artifacts` | `GET .../executions/{execution}/artifacts` | CT-EXE-012, Section 23 | |
| `get_results` | `GET .../executions/{execution}/results` | Sections 12, 13 | yes |
| `review_result` | `POST .../results/{result}/review` | Section 20; CT-DEC-010 to 012 | yes |
| `reassess_result` | `POST .../results/{result}/reassess` | CT-DEC-013, 014, 018; CT-SCT-008, 014 | yes |
| `recheck_validator` | as the implementation documents (Volume V permits it) | CT-ASM-009, CT-ASM-018 | |
| `confirm_control` | `POST .../seeded-controls/{scenario}/confirm` | CT-SCT-004, 013 | |
| `invalidate_control` | `POST .../seeded-controls/{scenario}/invalidate` | CT-SCT-007 | |
| `requalify_oracle` | `POST /projects/{project}/requalifications` | CT-SCT-008, 014 | |
| `list_requalifications` | `GET /projects/{project}/requalifications` | CT-SCT-008, 014 | |
| `record_admission` | `POST /projects/{project}/admissions` | CTS Section 16 | |
| `list_admissions` | `GET /projects/{project}/admissions` | CTS Section 16 | |
| `evaluate_gates` | `POST /projects/{project}/gates/check` | Sections 13, 14 | yes |
| `get_gate_results` | the GateResults of an evaluation or a Release Decision | CT-REL-014 | |
| `override_gate` | `POST .../gates/{gate}/override` | CT-REL-006 to 009 | yes |
| `get_snapshot` | `GET .../snapshots/{snapshot}` | CT-REL-013 | |
| `designate_baseline` | `POST .../baselines` | CT-REL-021, CT-PLG-004 | |
| `list_baselines` | `GET .../baselines` | CT-REL-021 | |
| `get_report` | `GET .../reports/{report}` | CT-REL-029, CT-REL-035; CT-ADM-004, 005 | yes |
| `record_release` | `POST .../releases` | Section 14 | yes |
| `list_releases` | `GET .../releases` | CT-REL-018 | |
| `approve_policy` | `POST .../release-policies` | `RP-1`, CT-REL-031 | |
| `revoke_policy` | `POST .../release-policies/{policy}/revoke` | CT-REL-018 | |
| `get_policy` | `GET .../release-policies/{policy}` | CT-REL-031 | |
| `audit_query` | `GET .../audit` | CT-REL-015, 019, 028, 038; CT-API-001 | |
| `list_approvals` | `GET .../approvals` | CT-REL-020 | |
| `approve_change` | Approval Workflow, as the implementation documents | "a governed change", CTS 14.1 | |
| `register_plugin` | `POST /plugins` | CTS 2.5; Section 25 | |
| `deprecate_plugin` | `POST /plugins/{plugin}/deprecate` | CT-PLG-004 | |
| `run_cli` | the CLI (§16) | CT-SDK-001 | |
| `run_sdk` | a language SDK (§16) | CT-SDK-002 | |
| `run_pipeline` | the CI/CD platform (§16) | CT-REL-024, 025, 037 | |
| `capture_ui` | the Reference UI (§16) | Section 26, `RUI` | |
| `raw_request` | any Appendix C path, sent exactly as given | CT-REL-028, CT-API-001, CT-API-002 | yes |
| `configure_behavior` | — (harness) | every test naming a behavior | yes |
| `reset_harness` | — | every case | yes |
| `read_call_log` | — | every Harness-method test | yes |
| `inject_failure` | — (or an SUT-documented hook, §9) | §9 | yes |
| `clock_capabilities` | — | timing tests | yes |
| `self_test` | — | CTS 2.8 | yes |
| `close_observation` | — | every negative harness assertion (§11) | yes |

`raw_request` with `unauthenticated: true` sends no credentials (CT-REL-028).

### 5.6 References between steps

In a fixture recipe or a runner script, `${project_id}` is the case's Project, and
`${step_id.path}` is a value from an earlier step's response (for example
`${b1.exec.batch_id}`). A reference that cannot be resolved fails the step.

## 6. Discovery and attribution

- **Applicability comes from the Conformance Statement.** The manifest
  (`adapter-manifest.schema.json`) points to the SUT's published Conformance Statement
  (`conformance_statement_ref`); the runner reads claimed capabilities there. The
  manifest itself never claims capabilities for the SUT.
- **Operation status.** For each operation, the manifest gives `supported`,
  `unsupported`, `not_configured`, or `unknown`, and, for an SUT operation, the SUT
  operation it maps to.
- **An adapter gap is not an SUT gap.** `unsupported` or `not_configured` describes the
  adapter. A test that needs such an operation is `NOT_RUN` (`ADAPTER_GAP`) unless a
  probe shows that the SUT offers neither the operation nor an equivalent. A probe is a
  recorded, authenticated request with the documentation consulted; it is kept as
  evidence (`probe_ref`).
- **A missing required operation fails.** Where the CTS says the absence of an operation
  fails a test (CTS 13.1, `reassess`), and a probe shows the SUT offers neither it nor an
  equivalent, the test is `FAIL` (`REQUIRED_OPERATION_MISSING`).
- **A missing optional feature is not applicable** where the CTS test says so (CTS 1.2;
  for example CT-ASM-018, CT-REL-036, CT-DSR-003), on the same probe evidence
  (`OPTIONAL_FEATURE_ABSENT`).
- **Equivalent surfaces.** An adapter for a surface other than Appendix C REST MUST
  provide `equivalence_evidence_ref`: for each mapped operation, the Appendix C
  operation it corresponds to and how. The report names the surface for every case
  (CTS 1.3).

## 7. Outcome attribution

The runner decides every case by this table, in this order. The first row that applies
decides.

| # | Observation | Outcome | `reason_code` |
|---|---|---|---|
| 1 | The test's capability is not in the Conformance Statement. | `NOT_APPLICABLE` | `CAPABILITY_NOT_CLAIMED` |
| 2 | The test checks an optional feature, says that its absence is not applicable, and a probe shows it absent. | `NOT_APPLICABLE` | `OPTIONAL_FEATURE_ABSENT` |
| 2a | The test checks what an implementation does when it does not claim a capability, and the capability is in the Conformance Statement (CTS 1.2). | `NOT_APPLICABLE` | `CAPABILITY_CLAIMED` |
| 2b | A manual review decides `NOT_APPLICABLE` (§13). | `NOT_APPLICABLE` | `OPTIONAL_FEATURE_ABSENT` |
| 3 | A behavior the test uses failed its self-test. | `NOT_RUN` | `HARNESS_SELF_TEST_FAILED` |
| 4 | A fixture the tester supplies (a test plugin, a pipeline, a reviewer) cannot be provided. | `NOT_RUN` | `FIXTURE_UNAVAILABLE` |
| 5 | Any error, of any origin, in phase `setup`, or a failed setup check. | `NOT_RUN` | `SETUP_FAILED` |
| 6 | The adapter has no mapping for an operation of the **Action**, and no probe shows the SUT lacks it. | `NOT_RUN` | `ADAPTER_GAP` |
| 7 | The CTS says the absence of the operation fails, and a probe shows the SUT offers neither it nor an equivalent. | `FAIL` | `REQUIRED_OPERATION_MISSING` |
| 8 | An error of origin `harness` or `adapter` in phase `action` or `observation`. | `NOT_RUN` | `HARNESS_FAILURE` |
| 9 | An error of origin `network`, or `SUT_TIMEOUT`, in phase `action` or `observation`. | `NOT_RUN` | `TRANSPORT_FAILED` |
| 10 | `SUT_SERVER_ERROR` or `SUT_MALFORMED_RESPONSE` in phase `action`: the SUT itself answered, but neither carried out nor properly rejected the request. | `FAIL` | `SUT_ERROR` |
| 11 | A negative harness assertion before `observation_closed` (§11), or calls that cannot be attributed to the case. | `NOT_RUN` | `OBSERVATION_INCOMPLETE` or `CORRELATION_UNCERTAIN` |
| 12 | The waiting budget ended, and the test says this is `NOT_RUN` (CTS 1.6, Waiting). | `NOT_RUN` | `BUDGET_EXCEEDED` |
| 13 | Evidence the outcome rests on is missing or fails its digest (§12). | `NOT_RUN` | `EVIDENCE_INTEGRITY_FAILED` |
| 14 | A manual review is pending, or disputed and unresolved (§13). | `NOT_RUN` | `MANUAL_REVIEW_PENDING` or `REVIEW_DISPUTED` |
| 15 | All observations are in: they meet **Expected**. | `PASS` | `EXPECTED_MET` |
| 16 | All observations are in: one contradicts **Expected** (CTS 1.1, 1.2). | `FAIL` | `EXPECTED_VIOLATED` |

Notes:

- **Stimuli are not failures.** A scripted stand-in that fails on purpose (`J-DOWN`,
  `SR-503-THEN-OK`, a fault injected under §9) is the test's input. What the SUT does
  with it is observed and judged by rows 15 and 16.
- **A budget is not always a reason to stop.** Where **Expected** says what must have
  happened by the end of the budget (CT-REL-025: the pipeline must have failed), the end
  of the budget is an observation, judged by rows 15 and 16.
- **Cleanup** errors never change an outcome. They set `cleanup_status: failed` and are
  listed under `harness_findings`.
- Every `NOT_RUN` and `NOT_APPLICABLE` carries a `reason` in words, as CTS 1.7 requires.

## 8. Scripted services

### 8.1 Behavior registry

The harness implements every behavior the CTS defines, exactly as defined there:

| Source | Behaviors |
|---|---|
| CTS 2.2 | `SR-OK`, `SR-EMPTY`, `SR-503-THEN-OK`, `SR-ECHO`, `SR-SLOW-200` |
| CTS 2.3 | `J-PASS-90`, `J-PASS-60`, `J-FAIL-90`, `J-DOWN`, `J-DOWN-THEN-PASS-90`, `J-FAIL-THEN-PASS-90`, `J-PASS-90-A3` |
| CTS 13.1 | `J-MAP(a, b, c)`, `J-CATCH` |
| CTS 22 | `SR-BYE`, `SR-HI`, `J-ALARM` |
| CTS 23 | `SR-CALL(url)`, and the tool targets `cts-stub.example`, `cts-trip.example`, `cts-outside.example`, hosted by the harness |

The CTS text is the definition; a harness that differs from it is wrong.

### 8.2 Endpoints, binding, correlation

Each model identifier the CTS uses (`cts-scripted-subject@1`, `cts-scripted-judge@1`,
`cts-scripted-judge@2`, `cts-scripted-judge-a@1` to `-c@1`, the generator of
CT-DSR-003) is a separate endpoint, configured separately. The harness serves them per
session, at `{harness_base}/sessions/{session_id}/{kind}/{endpoint_id}`.

The adapter makes each case's model identifiers resolve to that case's session; how
the SUT maps an identifier to an endpoint is its own concern (CTS 1.4). The manifest
says which is achieved (`model_binding`):

- `per_project`: every call is attributed to its case by the endpoint it arrives at.
  Cases may run in parallel.
- `global`: identifiers resolve to the same endpoints for every Project. Cases whose
  outcome reads the harness log then run one at a time, each followed by the drain of
  §11. A call that arrives outside every case window makes the neighboring cases
  `NOT_RUN` (`CORRELATION_UNCERTAIN`).

Every call is recorded as a `call_received` event, and every answer as `response_sent`,
with the session, endpoint, behavior, sequence number, and the raw request and
response (§12).

### 8.3 Configure, switch, reset

- `reset_harness` clears the session's call log, counters, and behaviors, and sets the
  defaults of CTS 2.2 and 2.3. It is atomic and affects that session only.
- `configure_behavior` sets one endpoint's behavior. `applies: now` (before the case's
  first call) or `next_call` (a switch during an **Action**, CTS 1.6): the new behavior
  answers the next request; a request already being answered finishes under the old
  one. A switch never clears counters.
- "First call" in a behavior's definition means the first call of the session. Counters
  are per endpoint and per session.
- Calls made while building a postcondition fixture are recorded with
  `attributes.phase: setup` and excluded from the test's harness observations (CTS
  1.6).

### 8.4 Harness-local behaviors

Where the CTS describes a scripted behavior in words without a code, the harness gives
it a code beginning `H-`. Such a code restates the CTS text and adds nothing:

| Code | CTS source | Behavior |
|---|---|---|
| `H-REL-035-SUBJECT` | CT-REL-035, F-SIGNALS | As `SR-ECHO`, except that the first call for `s-1` fails as the first call of `SR-503-THEN-OK` does. |
| `H-GEN-DSR-003` | CT-DSR-003 | A scripted generator: the first call returns one row, `query: "Gen-1"`; every later call one row, `query: "Gen-2"`. |

### 8.5 Test plugins

`cts-len`, `cts-flaky`, `cts-crash` (CTS 2.5), `cts-probe`, and `cts-reach`
(Section 25) run inside the SUT, not in the harness. The tester builds them for the
SUT's own plugin or Custom Validator mechanism and registers them as setup (CTS 2.5).
Where they report to the harness (`cts-probe`, `cts-reach`), they call a session
endpoint of kind `plugin`. A test plugin that cannot be built or registered for the
SUT makes its tests `NOT_RUN` (`FIXTURE_UNAVAILABLE`).

### 8.6 Self-test

`self_test` carries out CTS 2.8 against the harness directly, without the SUT, and
records one `self_test` event per behavior. A behavior that fails is marked unusable
for the run; every case using it is `NOT_RUN` (`HARNESS_SELF_TEST_FAILED`).

## 9. Faults and time

### 9.1 Fault profiles

| Profile | Injected event | Mechanism | CTS tests |
|---|---|---|---|
| `subject.pre_response_503` | HTTP 503 before any Response, then a Response | harness (`SR-503-THEN-OK`) | CT-EXE-003, CT-REL-035 |
| `judge.unreachable` | Refused connection, no verdict | harness (`J-DOWN`) | CT-ASM-006, CT-ASM-007, CT-ASM-008, CT-DEC-007, CT-DEC-014 |
| `validator.crash` | A Validator raises before any Result | test plugin `cts-crash`, or a hook the SUT documents | CT-ASM-014 |
| `validator.malformed` | A Validator Result without `verdict` | test plugin `cts-probe` | CT-PLG-003 |
| `subject.latency` | A delay before the Response | harness (`SR-SLOW-200`) | CT-EXE-012 |
| `review.timeout` | A review left unanswered past `review_timeout` | none: the runner does not answer | CT-HRV-003, CT-HRV-005, CT-REL-025 |
| `tool.boundary_attempt` | A tool call outside the Action Boundary | harness (`SR-CALL(url)`) | Section 23 |

The manifest lists the profiles available and, for each, its `mechanism`
(`harness_only`, `test_plugin`, or `sut_documented_hook`). No implementation is
expected to offer a hook. Where neither a test plugin nor a documented hook can make a
Validator fail, CT-ASM-014 is `NOT_RUN` and its requirement is reported unverified
(CTS 1.7).

### 9.2 Time

- **Clocks.** Every event records `observed_monotonic_ns` from a named monotonic clock
  (`clock_id`); durations are computed only between readings of the same clock.
  `observed_at` (RFC 3339, UTC) is for audit only and never used for durations.
- **Harness time is not SUT time.** A virtual clock (`clock_profile:
  injected_for_harness_only`) MAY drive the harness's own timers, such as a scripted
  delay. It never stands for the SUT's clock, and no test assumes that changing it
  moves an SUT deadline.
- **Scripted delays** are at least as long as defined (`SR-SLOW-200`: never less than
  200 ms, measured at the harness), and the measured delay is recorded.
- **Waiting budgets** follow CTS 1.6: the run profile states, per test that waits, the
  configured duration and the grace period; the runner watches for the event the test
  names (polling with `poll_execution`, `get_results`, or the pipeline's records) and
  stops at the end of the budget. The grace period SHOULD be at least 10% of the
  duration and at least 5 s.

## 10. Fixtures, identities, isolation

- **Namespaces.** `begin_case` allocates a Project ID and a session for each test, each
  numbered case, and each lettered variant of a **Fixture** (CTS 1.6). The report maps
  the symbolic `cts-base` to the real Project ID. A Project is never reused by another
  case.
- **Principals.** The Principals of CTS 14.1, and any a test adds, are provisioned for
  each Project with `provision_principal`, with credentials held by reference
  (`actor_ref`, `secret://`). Permissions are never emulated by editing responses or
  by mocking authorization in the adapter.
- **Recipes.** Every postcondition fixture of CTS 2.7 has a recipe in `fixtures/`
  (`fixture-recipe.schema.json`): a base fixture and its changes, behaviors, steps in
  dependency order, setup checks, and cleanup. The recipe is a machine form of CTS 2.7;
  where they differ, CTS 2.7 is right, and `tools/validate.py` reports the difference.
  Setup checks are stated in words.
- **Setup.** A recipe runs in the case's own Project, in phase `setup`. A failed step or
  check makes the case `NOT_RUN` (§7, row 5); the behavior that failed is reported by
  the test that checks it, not by this one (CTS 1.6).
- **Destructive operations** (`delete_resource`, `raw_request` with `DELETE`) are sent
  only to Projects the run created, on an instance the run profile's allowlist names.
- **Cleanup** runs in reverse dependency order after the outcome is recorded. Its
  failure is recorded (`cleanup_status`) and blocks reuse of the instance until
  resolved; it does not change the outcome.

## 11. Observation lifecycle

A case passes through these states:

`prepared` → `running` → `sut_terminal_observed` → `draining` → `observation_closed` →
`decided` → `cleanup_complete`

- **Terminal.** `sut_terminal_observed` is recorded when the adapter has observed the
  terminal state of everything the **Action** started: every Execution of the batch
  terminal, every asynchronous operation answered. If the SUT gives no way to observe
  this, the adapter says so, and negative harness assertions of the case are
  `NOT_RUN` (`OBSERVATION_INCOMPLETE`).
- **Drain.** The runner then calls `close_observation` with the run's drain time
  (`drain_ms`, in the run profile and the report). The harness waits that long, records
  an `observation_watermark` naming the highest sequence number received for the
  session, and then `observation_closed`.
- **Negative assertions.** "No call", "exactly one call", and other counts are decided
  over the calls up to the watermark, and only after `observation_closed`. Before it,
  such an assertion is `NOT_RUN`, never `PASS`.
- **Late calls.** A call to a session after its closure is recorded as `late_call`.
  The report is finalized only after a final drain for the whole run; a late call
  that contradicts a decided outcome changes it to `FAIL` (`EXPECTED_VIOLATED`), with
  the late call as evidence.
- The drain time SHOULD be at least 5 s and at least twice the longest SUT-to-harness
  delay measured during the self-test.

## 12. Evidence and integrity

- **Capture before mapping.** Every SUT request and response, every harness call and
  answer, every probe, configuration loaded, review, screenshot, and pipeline or CLI
  log is stored raw, before redaction or mapping, in restricted, append-only storage.
- **Digests.** `raw_sha256` is SHA-256 over the exact bytes captured. Where a redacted
  copy is published, `redacted_sha256` is SHA-256 over the exact bytes published, and
  the pair is kept together.
- **Manifest.** Every evidence object of a run is listed once in the evidence manifest
  (`evidence-manifest.schema.json`), with both digests, size, case, collection time,
  and redaction policy. `manifest_sha256` is SHA-256 over the UTF-8 bytes of the
  RFC 8785 (JCS) serialization of the manifest without that field. The report carries
  the manifest's reference and digest.
- **Canonicalization** is RFC 8785 as published: object keys sorted by their UTF-16
  code units, numbers written as ECMAScript writes them, strings escaped only where
  RFC 8785 requires. An implementation MUST pass the examples of RFC 8785 §3.2.2 and
  §3.2.3; `validate.py` carries them, with further edge cases, and checks itself
  against them on every run. A document holding an integer beyond ±2^53, NaN, or an
  infinity cannot be canonicalized and is refused.
- **Verification** fails closed. A verifier, with access to the evidence store:
  1. checks the manifest against its schema, its entries for duplicates, and
     `manifest_sha256`;
  2. resolves every `raw_ref` and `redacted_ref`, reads the object, and compares its
     SHA-256 and, for raw objects, its size with the manifest;
  3. checks that every evidence reference in the report (each case's `evidence_refs`,
     every review's checklist, the Conformance Statement used) is listed in the
     manifest, and that the report names the manifest's digest and run.

  A missing object, a mismatch, or an unlisted reference invalidates every outcome that
  rests on it (§7, row 13); a manifest that does not verify invalidates the report.
  `validate.py --report R --manifest M --evidence-root D` does all of this for a
  directory store, where `evidence://name` is the file `D/name` and nothing outside
  `D` resolves. Another store needs a resolver that makes the same checks.
- **Redaction** removes secrets and personal data from published copies; it never
  removes a field an assertion depends on. Where such a field is sensitive, the
  assertion is verified against the raw copy by a reviewer with access, and the report
  says so.
- **Retention** of raw and redacted evidence is stated in the manifest (`retention`).

## 13. Manual review

This section is the record format for CTS 1.8.

- **Who.** Every review names its reviewer (`reviewer.id`, `role`, and, where relevant,
  `affiliation`). A review is never anonymous.
- **Checklist.** One item per statement of **Expected**, quoted verbatim; each answered
  `met`, `not_met`, or `undecided`, with the evidence used.
- **Decision.** `PASS` only if every item is `met` with evidence; `FAIL` if an item is
  `not_met` with evidence; `NOT_APPLICABLE` only where the test's **Expected** names
  that outcome for what the reviewer found (for example, a feature the specification
  leaves optional and the implementation does not offer), with `reason_code`
  `NOT_OFFERED` and evidence for the item that establishes it; otherwise `NOT_RUN`. The
  schema enforces this. A record's free-text remarks go in `notes`, or in an item's
  `note`.
- **Method.** `inspection` or `declaration`. A Declaration is recorded as a statement
  (`declaration_ref`), never as a measurement, and only where the test's method
  includes Declaration (CTS 1.3).
- **Disputes.** A disputed decision goes to a second reviewer, a different person, who
  decides from the same evidence without seeing the first record (`second_review.blind:
  true`). Until both agree, the case is `NOT_RUN` (`REVIEW_DISPUTED`), and both records
  stay in the report. A dispute raised by the implementation's side goes to a reviewer
  not affiliated with it.
- **Pending.** A review still pending when the report is finalized makes its case
  `NOT_RUN` (`MANUAL_REVIEW_PENDING`). No deadline turns a pending review into a
  decision.
- **Signature.** `signature_ref` points to a signature over the JCS serialization of the
  record without that field, or to an authenticated record that identifies the
  reviewer. A reviewer that cannot sign, such as an AI system, has its records signed by
  the person who commissioned the review. That person's authenticated attestation names
  the reviewer, the records, and the run they apply to, and states that the records are
  unchanged. An authenticated commit that adds the records and the attestation to a
  repository is one such record.
- **Per test.** For CT-REL-023, the reviewer follows the actual record links and cites
  each. For CT-ABD-007 and every Declaration, the report states that the evidence is a
  statement. For Section 26 `RUI` tests, screenshots show the URL and a visible time.

## 14. Results and aggregation

### 14.1 Cases

A test without numbered cases is reported as one case whose ID is the test ID. A test
with numbered cases (CTS 1.2) is reported case by case; each case gets its own
namespace and outcome.

### 14.2 Tests

A test's outcome summarizes its cases, as CTS 1.2 states: `FAIL` if any case is
`FAIL`; otherwise `NOT_RUN` if any is `NOT_RUN`; otherwise `PASS` if any is `PASS`;
otherwise `NOT_APPLICABLE`.

### 14.3 Requirements

The report lists every row of CTS Section 90 whose status is Tested or Restates.

- A Tested row is traced to the tests and cases Section 90 names (to cases, where it
  names cases).
- A Restates row takes the state and trace of the row it restates (`derived_from`).
- Rows that are Not testable are not listed, nor are Restates rows that restate one.

The state of a requirement, over the cases it is traced to, leaving out those
`NOT_APPLICABLE`, and counting a traced case that the run did not include as
`NOT_RUN`:

| Cases | State |
|---|---|
| Any `FAIL` | `violated` |
| Otherwise any `NOT_RUN` | `unverified` |
| Otherwise at least one `PASS` | `verified` |
| Otherwise (every case `NOT_APPLICABLE`) | `not_applicable` |

A requirement is therefore verified only when every applicable case traced to it
passed: a `PASS` in one test never covers a `NOT_RUN` in another. Coverage figures are
taken over the requirements that are not `not_applicable`.

### 14.4 Evidence grades

Each case records the grades of the evidence it rests on: `observed` (Automated or
Harness), `sampled` (a finite repetition used as a check, such as CT-PLG-005's ten
runs), `inspected` (Inspection), `declared` (Declaration). A requirement shows the
grades of the cases that decided it. A grade is information for the reader; it does not
change an outcome.

### 14.5 Truth table

| Cases of CT-CFG-025 | Test | R-0129 (case .01) | R-0213 (case .18) | R-0132 (case .25) |
|---|---|---|---|---|
| .01 `PASS`, .18 `NOT_RUN`, .25 `NOT_APPLICABLE` | `NOT_RUN` | `verified` | `unverified` | `not_applicable` |
| .01 `PASS`, .18 `PASS`, .25 `NOT_APPLICABLE` | `PASS` | `verified` | `verified` | `not_applicable` |
| .01 `FAIL`, .18 `NOT_RUN`, .25 `PASS` | `FAIL` | `violated` | `unverified` | `verified` |

`examples/cts-report--algebra.json` is a full report built this way, and
`tools/validate.py` recomputes every test and requirement state in it.

## 15. Report

The run report (`cts-report.schema.json`) holds:

- **plan:** what the run set out to do: `scope: full` (every CTS test) or
  `scope: partial` (the tests listed, with the reason);
- **provenance:** AQEF version, CTS revision and commit, contract version, harness and
  adapter versions, SUT name and version, the Conformance Statement used, the
  capabilities it claims, and the drain time;
- **summary:** counts of cases, tests, and requirements by outcome or state;
- **cases:** for each, its test, capability, outcome, reason code and reason, evidence,
  evidence grades, setup and cleanup status, surface, and reviews;
- **tests** and **requirements**, derived as §14 states;
- **manual_reviews**, every record, including disputed ones;
- **harness_findings:** failures of the harness, adapter, or network, apart from any
  outcome of the SUT;
- the evidence manifest's reference and digest.

**Completeness.** A report is complete when it holds every case of every planned test
exactly once, each test of the plan exactly once with the case IDs the CTS gives it,
and every requirement of §14.3 exactly once, with the trace Section 90 gives it. A
report that is internally consistent but omits a planned case, or reports one twice, is
invalid: `validate.py` compares the report with the CTS it names, not only with itself.
A partial run is valid, and says so: requirements traced to unplanned tests stay
unverified.

A human-readable report SHOULD be produced from the JSON and show the same figures,
every `NOT_RUN` with its reason, every unverified requirement, and harness findings
apart from SUT failures. A report from a mock implementation says so in its title and
provenance, and is never presented as a conformance result.

## 16. Capability adapters

Tests of a CLI, an SDK, a CI/CD platform, a Reference UI, or a Dataset generator need
evidence beyond the REST surface. Minimum evidence:

| Adapter | Operation | Minimum evidence |
|---|---|---|
| CLI | `run_cli` | The command line and its output; a recording proxy's log of every REST call the command made, correlated to the command (CT-SDK-001). |
| SDK | `run_sdk` | The SDK and language versions; the calls made; a recording proxy's log of the REST traffic; the SDK's error, as status and code (CT-SDK-002). |
| CI/CD | `run_pipeline` | The pipeline definition, run ID, and logs; the outcome of the gate step; the platform's own record of the run (CT-REL-024, 025, 037). |
| Reference UI | `capture_ui` | Screenshots showing URL and time; the steps taken; with the consent and scope the run profile states (Section 26, `RUI`). |
| Dataset generator | `generate_dataset` | The documented operation used, its request and response, and the versions read before and after (CT-DSR-003). |

Where an adapter is not available, the tests are `NOT_RUN` (`ADAPTER_GAP`), or, where
the test is an Inspection, they follow §13.

## 17. Security and privacy

- Run only on a non-production instance, or a test tenant the run profile names and the
  operator has authorized. Faults and destructive operations are never sent elsewhere.
- Credentials are held in a secrets store and passed by reference. No report, log, or
  published evidence contains a secret.
- Tool targets of Section 23 are hosted by the harness under the reserved `.example`
  domain; no test sends traffic to a real third-party system.
- Raw evidence is stored with access limits, a retention period, and an access log.
- Negative authorization tests use separately provisioned Principals.

## 18. Contract invariants

Each invariant is checked statically by `tools/validate.py`.

| ID | Invariant | Checked |
|---|---|---|
| I-01 | A schema-invalid or wrong-version request is rejected before any SUT call. | static (`examples/invalid/`); Stage C |
| I-02 | A response has exactly one of `data` and `error`; its `correlation_id` matches the request. | static; Stage C |
| I-03 | A successful SUT operation always records the SUT's outcome and raw body; a rejection is an outcome, not an error. | static; Stage C |
| I-04 | A negative harness assertion cannot `PASS` before `observation_closed`; a late call turns it to `FAIL`. | Stage C |
| I-05 | Resets are per session; parallel cases share no counter, behavior, or log. | Stage C |
| I-06 | A deliberately failing stand-in is a stimulus, not a harness failure. | Stage C |
| I-07 | An absent SUT operation is decided from a probe, never from the manifest alone. | Stage C |
| I-08 | Changing one byte of raw or redacted evidence, misstating its size, removing it, or referring outside the store is detected by verification. | static (unit tests on the example evidence); Stage C on a real store |
| I-09 | A test with cases `PASS` and `NOT_RUN` is `NOT_RUN`; `FAIL` dominates. | static |
| I-10 | A requirement is `verified` only when every applicable traced case passed. | static |
| I-11 | An unclaimed capability gives `NOT_APPLICABLE`, never `FAIL`. | Stage C |
| I-12 | A manual review with an undecided item, or an unresolved dispute, never yields `PASS`. | static |
| I-13 | Every recipe in `fixtures/` matches CTS 2.7, and every behavior code is defined in the CTS or §8.4. | static |
| I-14 | A report is complete and its identifiers unique: planned cases, tests, and requirements each exactly once, with the CTS's case lists and Section 90's traces. | static |
| I-15 | A case's capability is the CTS's; `CAPABILITY_NOT_CLAIMED` only where the Conformance Statement used does not claim it, and an unclaimed capability is always `NOT_APPLICABLE`. | static |
| I-16 | Canonicalization matches RFC 8785, including its published examples and UTF-16 key order. | static |
| I-17 | Every evidence reference of a report is in its manifest, and the report names the manifest's digest and run. | static |

`tools/test_validate.py` exercises every static check, each on a valid case and on
cases built to break it.

## 19. Version history

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-10-18 | external audit, Stage B | First draft: adapter boundary, outcomes, evidence, manual review, fault and clock profiles, security, slices. |
| 0.2 | 2026-10-18 | external audit, Stage B | Envelope schemas, error origin and phase, observation lifecycle, digests, aggregation algebra, invariants. |
| 0.3 | 2026-10-19 | integrated into the AQEF repository | v0.1 and v0.2 merged and checked against AQEF 0.39 and CTS WD7. |
| 0.4 | 2026-10-20 | after the Contract Verification Audit | Run plan and report completeness; RFC 8785 canonicalization as published; evidence verified byte by byte; unit tests of every check. |
| 0.5 | 2026-10-23 | for CTS WD8 | Written for CTS WD8 and AQEF 0.41.1. Operations `record_admission` and `list_admissions` for the Admission tests (CTS Section 16); the tests of clean controls added to the operations they use. The history above is restored: 0.3 and 0.4 had been merged into one row. |
| 0.6 | 2026-10-24 | for CTS WD9 | Written for CTS WD9 and AQEF 0.41.4, after the first run of WD8 against a reference implementation. Behavior registry completed (`SR-HI`, `J-ALARM` were missing) and `J-PASS-90-A3` added; `audit_query` serves CT-REL-038. Reason code `CAPABILITY_CLAIMED` (§7, row 2a). |
| 0.7 | 2026-10-24 | for CTS WD10 | Written for CTS WD10 and AQEF 0.41.5, after the review of WD9's Inspection and Declaration tests. A review record may decide `NOT_APPLICABLE` (`NOT_OFFERED`) where the test names it (§13; §7, row 2b); a reviewer that cannot sign is signed for by the person who commissioned the review (§13). Version numbers in schemas and examples, left at 0.5 in 0.6, read 0.7; schema `$id`s move to `/schemas/0.7/`. |
