# 14. Release and Governance

Tests in this section record Release Decisions, overrides, Baselines, and configuration
changes, and observe what is accepted, what is rejected, and what is recorded.

## 14.1 Fixtures and conventions for this section

Section 13.1 applies here as well: "evaluate the Gates", `semantic-gate`, `P-REVIEWER`,
and the clause-to-Gate mapping.

**Principals.** The tester sets up the following in the implementation, with Team
membership giving each access to `cts-base`. Role names are illustrative; what matters is
the Permissions each Role holds.

| Principal | Kind | Permissions |
|---|---|---|
| `P-RELEASE` | Person | `read`, `execute`, `release_decide` |
| `P-APPROVER` | Person | `read`, `execute`, `contract_define`, `gate_override`, `baseline_approve`, `environment_edit`, `scenario_edit`, `environment_delete` |
| `P-NOPERM` | Person | `read`, `execute` |
| `P-EDITOR` | Person | `read`, `project_edit`, `scenario_edit` |
| `P-REVIEWER` | Person | `read`, `review`; holds the Role `reviewer` |
| `P-ADMIN` | Person | `read`, `project_delete`, `audit_read` |
| `SA-CI` | Service Account, owned by `P-RELEASE` | `read`, `execute`, `release_decide`, `gate_override`, `baseline_approve`, `contract_define` |

`SA-CI` deliberately holds Permissions it may not use for every action: what a Service
Account may do is limited by what it is, not only by what it holds (Volume XII,
Principals).

**`RP-1`.** A Release Policy (Appendix A §A.14) approved by `P-RELEASE` through
`POST /projects/cts-base/release-policies`:

```yaml
id: RP-1
project: cts-base
suites: [cts-suite]
environments: [cts-env]
service_accounts: [SA-CI]
```

**Recording a Release Decision.** "Record a Release Decision" means
`POST /projects/cts-base/releases`, or the implementation's equivalent, with this body
unless the test says otherwise:

```yaml
project: cts-base
environment: cts-env
suite: cts-suite
execution_batch_id: "<the batch the Action produced>"
gates: "<every GateResult the latest evaluation returned, keyed by Gate name>"
decision: approved
approved_by: "<the acting Principal>"
approved_at: "<now>"
approval_role: "<a Role of the acting Principal that holds release_decide>"
report_id: "<the Report the implementation produced for the batch>"
snapshot_id: "<the snapshot_id the latest evaluation returned>"
```

**Overriding.** "Override `<gate>`" means
`POST /projects/cts-base/gates/<gate>/override` naming that Gate's GateResult from the
latest evaluation by its `id`, with the batch's `execution_batch_id` and the
justification `"CTS override"`, made by `P-APPROVER` unless the test says otherwise.

**A governed change.** A change to a Gate, an inline Contract, or an Environment made by
`P-APPROVER` through the operation Appendix C §C.3 lists for it, approved where Approval
Workflow governs it.

## 14.2 Tests

### CT-REL-001 — A Release Decision is recorded when every blocking Gate passes

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: "A blocking Gate MUST pass for a
  Release Decision to authorize shipping"; Appendix A §A.12, Release Decision; Appendix B
  §B.3, Approval Permissions: "a Release Decision's [`approval_role`] MUST hold
  `release_decide`."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision. Retrieve it.
- **Expected:** Accepted. The stored decision has an `id` and every field of the body
  above, with `decision: approved`, `approved_by` naming `P-RELEASE`, and a `gates` map holding the
  GateResults for `functional-gate` and `semantic-gate`, unchanged.
- **Fails if:** Rejected, or any field is missing or altered.

### CT-REL-002 — A failed blocking Gate prevents an approval

- **Capability:** core
- **Requirement:** Appendix A §A.12: "`decision: approved` requires every blocking
  GateResult to have `status: pass`"; Volume I, Chapter 6, Quality Gates: "the Decision
  Pipeline does not silently continue."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision (a) with `decision: approved`, then (b) with `decision: rejected`.
- **Expected:** (a) rejected; (b) accepted.
- **Fails if:** (a) is accepted, or (b) is rejected.

### CT-REL-003 — A failed advisory Gate is recorded and does not prevent an approval

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: an advisory Gate's "result is
  recorded in every Report and Release Decision whose scope it covers, but its failure
  does not by itself prevent shipping"; Appendix A §A.10, `on_failure: warn`.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`, given `on_failure: warn`; scripted Judge
  `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision. Retrieve it and the Report it names.
- **Expected:** Accepted with `decision: approved`. Its `semantic-gate` GateResult has
  `status: fail`, `blocking: false`, `reasons: [threshold]`, and no `override`. The
  Report shows `semantic-gate` as failed.
- **Fails if:** The decision is rejected; the advisory GateResult is missing, shown as
  passed, or carries `blocking: true`; or the Report omits it.

### CT-REL-004 — A Release Decision must carry every applicable Gate

- **Capability:** core
- **Requirement:** Appendix B §B.3, Release Decision coverage: "`gates` MUST contain a
  GateResult for every Quality Gate, blocking or advisory, applicable to the decision's
  scope"; Appendix A §A.10: "A Release Decision is subject to the Project's Gates and to
  those of the Suite it covers."
- **Method:** Automated
- **Fixture:** F-BASE; add to `suites[0]`:
  ```yaml
  quality_gates:
    - name: suite-gate
      aggregate: semantic
      threshold: 0.5
      on_failure: warn
  ```
  Scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision whose `gates` holds only the `functional-gate` GateResult.
- **Expected:** The evaluation returns GateResults for `functional-gate` and
  `suite-gate`. The Release Decision is rejected; the error names `suite-gate`.
- **Fails if:** The evaluation omits `suite-gate`, or the Release Decision is accepted.

### CT-REL-005 — No Release Decision without an applicable Gate

- **Capability:** core
- **Requirement:** Appendix B §B.3, Release Decision requires a Gate: "A Release Decision
  MUST NOT be recorded for a scope to which no Quality Gate applies"; Appendix C §C.3,
  `POST /projects/{project}/releases`.
- **Method:** Automated
- **Fixture:** F-BASE; remove `quality_gates`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision with `gates: {}` and whatever `snapshot_id` the evaluation returned, if any.
- **Expected:** The evaluation returns no GateResult. The Release Decision is rejected.
- **Fails if:** The Release Decision is accepted.

### CT-REL-006 — An approved override lets a failed blocking Gate result in a release

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: an exception "MUST be recorded as
  an explicit, auditable override rather than a quiet pass"; Appendix A §A.12:
  "`decision: overridden` requires every blocking GateResult with `status: fail` to
  carry an `override`"; Appendix B §B.3, Gate Result override.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-RELEASE`, record a Release
  Decision with `decision: overridden`. Override `semantic-gate`. Without evaluating the
  Gates again, retrieve the `semantic-gate` GateResult and record the Release Decision
  with `decision: overridden` once more.
- **Expected:** The first attempt is rejected (no override yet). The override is
  approved and recorded against that GateResult, which now carries `override` naming the
  Approval Workflow record; the GateResult keeps `status: fail`. The second attempt is
  accepted. The override record names `P-APPROVER` and the justification.
- **Fails if:** The first attempt is accepted; the GateResult's `status` becomes
  `pass`; the override record omits the approving Person or the justification; or the
  second attempt is rejected.

### CT-REL-007 — An override applies to one Gate Result only

- **Capability:** core
- **Requirement:** Volume XII, Approval Workflow: an override "MUST NOT be applied to any
  other evaluation, including a later evaluation of the same Gate for a different
  batch"; Appendix B §B.3: "One override record MUST NOT be referenced by more than one
  GateResult."
- **Method:** Automated
- **Fixture:** F-OVERRIDDEN (2.7).
- **Action:** Execute `cts-suite` again (a new batch) with `J-FAIL-90`; evaluate the
  Gates. As `P-RELEASE`, record a Release Decision for the new batch with
  `decision: overridden`, its `semantic-gate` GateResult carrying the `override`
  reference recorded when F-OVERRIDDEN was built.
- **Expected:** The new `semantic-gate` GateResult carries no `override`. The Release
  Decision is rejected.
- **Fails if:** The new GateResult shows the earlier override, or the Release Decision
  is accepted.

### CT-REL-008 — An override needs a Permission, a justification, and a failed blocking Gate

- **Capability:** core
- **Requirement:** Appendix C §C.3, override: "Body MUST name the GateResult by its
  `id` ..., give its `execution_batch_id`, and include a non-empty justification";
  Appendix B §B.3, Gate Result override; Appendix A §A.12,
  `override`: "Only on a blocking GateResult with `status: fail`"; Appendix C §C.4:
  "If the Principal lacks the required Permission, the API MUST reject the request."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Attempt to override:
  (a) `semantic-gate` as `P-NOPERM`; (b) `semantic-gate` as `P-APPROVER` with an empty
  justification; (c) `semantic-gate` as `P-APPROVER` with no GateResult `id`;
  (d) `functional-gate`, which passed, as `P-APPROVER`; (e) `semantic-gate` as
  `P-APPROVER`, naming the `id` of the `functional-gate` GateResult.
- **Expected:** All five are rejected, and no GateResult carries an `override`.
- **Fails if:** Any of the five is accepted.

### CT-REL-009 — A Gate-specific override Permission is enforced

- **Capability:** core
- **Requirement:** Appendix A §A.10, `override_requires`: a Project "MAY require a
  stricter, Gate-specific Permission in addition to `gate_override`"; Appendix C §C.4.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`, given `override_requires: safety_override`;
  scripted Judge `J-FAIL-90`. `P-APPROVER` does not hold `safety_override`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Override `semantic-gate`.
- **Expected:** Rejected.
- **Fails if:** Accepted.

### CT-REL-010 — A Gate changed after the Snapshot blocks the Release Decision until re-evaluated

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: "If any of that configuration
  changed after the Snapshot was captured, the Release Decision MUST NOT be recorded
  until its Gates are evaluated again ... Where only a Gate definition changed, no new
  Execution is needed"; Appendix B §B.3, Release Decision currency.
- **Method:** Automated, Harness
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As a governed change, set
  `semantic-gate`'s `threshold` to `0.9`. As `P-RELEASE`, record a Release Decision with
  the first evaluation's `snapshot_id`. Then evaluate the Gates again for the same batch
  and record the Release Decision with the new `snapshot_id`.
- **Expected:** The first attempt is rejected, naming `semantic-gate` as changed. The
  second evaluation returns a new `snapshot_id` and a `semantic-gate` GateResult with
  `threshold: 0.9`; the second attempt is accepted. The scripted subject and Judge
  received no further calls after the first Execution.
- **Fails if:** The first attempt is accepted; the second is rejected; or the
  re-evaluation started new Executions.

### CT-REL-011 — An inline Contract changed after the Snapshot blocks the Release Decision

- **Capability:** core
- **Requirement:** Appendix B §B.3, Release Decision currency: "any Contract (Reusable or
  inline)"; Appendix A §A.13, `inline_contracts`: "any difference from the current
  content is a change."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As a governed change, set the
  Expectation's `confidence_threshold` in `s-greeting`'s inline Contract to `0.85`. As
  `P-RELEASE`, record a Release Decision with the evaluation's `snapshot_id`.
- **Expected:** Rejected, naming the changed Contract.
- **Fails if:** Accepted.

### CT-REL-012 — An Environment changed after the Snapshot blocks the Release Decision

- **Capability:** core
- **Requirement:** Appendix B §B.3, Release Decision currency: "any Contract (Reusable or
  inline), Quality Gate, or Environment in its scope"; Appendix B §B.3, Stale Results.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As a governed change, set
  `cts-env`'s `prompt_version` to `cts-prompt@2`. As `P-RELEASE`, record a Release
  Decision with the evaluation's `snapshot_id`. Then evaluate the Gates again for the
  same batch, without new Executions, and record the Release Decision with the new
  `snapshot_id`.
- **Expected:** Both attempts are rejected: the first because `cts-env` changed since
  its Snapshot; the second because the new evaluation's blocking GateResults fail with
  `stale_results` (CT-DEC-022).
- **Fails if:** Either attempt is accepted.

### CT-REL-013 — A Snapshot captures the configuration in scope and is never modified

- **Capability:** core
- **Requirement:** Appendix A §A.13, Snapshot: "Never modified once captured"; Appendix B
  §B.3, Snapshot immutability: "A Snapshot MUST NOT be modified after `captured_at`."
- **Method:** Automated
- **Fixture:** F-CONTRACT-CHANGED (2.7).
- **Action:** Retrieve the Snapshot named by the evaluation's `snapshot_id`.
- **Expected:** It has `id`, `captured_at`, `project: cts-base`, `suites: [cts-suite]`,
  `environments` holding `cts-env` as defined in F-BASE, `contracts: {}`,
  `inline_contracts` holding `s-greeting`'s Contract in full under
  `scenario:cts-suite/s-greeting` with `confidence_threshold: 0.8`, and `quality_gates`
  holding both Gate definitions. It is unchanged by the later governed change.
- **Fails if:** Any of these is missing or differs, or the Snapshot reflects the change.

### CT-REL-014 — A GateResult keeps the threshold it was evaluated against

- **Capability:** core
- **Requirement:** Appendix A §A.12, GateResult `threshold`: "copied at evaluation time,
  so the record stays checkable if the Gate definition changes later."
- **Method:** Automated
- **Fixture:** F-GATE-CHANGED (2.7).
- **Action:** Retrieve the `semantic-gate` GateResult from evaluation 1.
- **Expected:** `threshold: 1.0`.
- **Fails if:** It shows `0.9`, or the earlier GateResult can no longer be retrieved.

### CT-REL-015 — Defining or changing a Gate is governed under `contract_define`

- **Capability:** core
- **Requirement:** Appendix A §A.10: "Defining or changing a Quality Gate is governed by
  Approval Workflow under `contract_define`"; Volume I, Chapter 6: changing a Gate from
  blocking to advisory "is governed like any other change to a Gate"; Appendix C §C.5.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`.
- **Action:** As `P-NOPERM`, attempt (a) to define a new Gate and (b) to set
  `semantic-gate`'s `on_failure` to `warn`. Then make change (b) as `P-APPROVER`. Query
  the audit log for action type `contract_define`.
- **Expected:** (a) and (b) as `P-NOPERM` are rejected. The change as `P-APPROVER` goes
  through Approval Workflow and appears in the audit log as `contract_define`, naming
  `P-APPROVER`.
- **Fails if:** Either attempt by `P-NOPERM` takes effect, or the change by
  `P-APPROVER` is not logged as `contract_define`.

### CT-REL-016 — Recording a Release Decision needs `release_decide`

- **Capability:** core
- **Requirement:** Appendix C §C.4: "Every mutating operation MUST check the resolved
  Principal's Permissions before executing"; Appendix B §B.3, Approval Permissions.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Record a Release Decision as
  `P-NOPERM`, giving as `approval_role` a Role it holds.
- **Expected:** Rejected.
- **Fails if:** Accepted.

### CT-REL-017 — A Service Account cannot approve an override or a Baseline

- **Capability:** core
- **Requirement:** Volume XII, Principals: "`gate_override` and `baseline_approve` MUST
  be approved by a Person"; Appendix A §A.11, `approved_by`: "MUST be a Person, not a
  Service Account."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `SA-CI`, attempt (a) to
  override `semantic-gate` and (b) to designate the `s-greeting` Execution as a
  Baseline.
- **Expected:** Both rejected, although `SA-CI` holds `gate_override` and
  `baseline_approve`. No override and no Baseline is recorded.
- **Fails if:** Either is accepted.

### CT-REL-018 — A Service Account records a Release Decision only under a standing policy

- **Capability:** core
- **Requirement:** Appendix B §B.3, Automatic release: "A Release Decision whose
  `approved_by` is a Service Account MUST carry `release_policy`, and its `decision` MUST
  be `approved` (every blocking GateResult `pass`, no `override`) or `rejected`"; Volume
  XII, Principals: "The record MUST reference the policy."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`, plus a second Environment `cts-env-2`
  identical to `cts-env` except for its name; `RP-1` in place.
- **Action:** Batch 1, with `J-PASS-90`: execute, evaluate the Gates, and as `SA-CI`
  record a Release Decision (a) without `release_policy`, then (b) with
  `release_policy: RP-1`. Batch 2, with `J-FAIL-90`: execute, evaluate, override
  `semantic-gate` as `P-APPROVER`, and as `SA-CI` with `release_policy: RP-1` record
  (c) `decision: overridden` and (d) `decision: rejected`. Batch 3, against
  `cts-env-2` with `J-PASS-90`: execute, evaluate, and as `SA-CI` record (e) `approved`
  with `release_policy: RP-1`. Then, as `P-RELEASE`, revoke `RP-1`; batch 4, against
  `cts-env` with `J-PASS-90`: execute, evaluate, and as `SA-CI` record (f) `approved`
  with `release_policy: RP-1`.
- **Expected:** (a) rejected; (b) accepted, and the stored decision references `RP-1`;
  (c) rejected; (d) accepted; (e) rejected, since `RP-1` does not cover `cts-env-2`;
  (f) rejected, since `RP-1` is revoked. The decisions (b) and (d) are still recorded
  after the revocation. `RP-1`, retrieved after it, has `revoked_at` and `revoked_by`
  naming `P-RELEASE`, and its other fields unchanged.
- **Fails if:** (a), (c), (e), or (f) is accepted; (b) or (d) is rejected; (b)'s record
  does not reference `RP-1`; the revocation removed (b) or (d); or the revoked `RP-1`
  lacks `revoked_at` or `revoked_by`.

### CT-REL-019 — Audit records which kind of Principal acted

- **Capability:** core
- **Requirement:** Volume XII, Principals: a Service Account "MUST have an owning Person
  accountable for what it does. Audit records which kind of Principal acted."
- **Method:** Automated, Inspection
- **Fixture:** F-SA-DECISIONS (2.7).
- **Action:** Query the audit log for action type `release_decide`. Retrieve `SA-CI`'s
  details. If the implementation lets a Service Account be created, attempt to create one
  with no owning Person.
- **Expected:** The entries for (b) and (d) name `SA-CI` as a Service Account; any entry
  for a Person's action names a Person. `SA-CI`'s details name `P-RELEASE` as owner. The
  Service Account with no owner is rejected.
- **Fails if:** An entry does not state the kind of Principal; no owner is recorded for
  `SA-CI`; or the owner-less Service Account is created.

### CT-REL-020 — A Service Account applies `contract_define` only with a named approver and review

- **Capability:** core
- **Requirement:** Appendix B §B.3, Human approval: "A `contract_define` applied by a
  Service Account MUST name the approving Person and reference the external review";
  Volume XII, Principals.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`.
- **Action:** As `SA-CI`, set `semantic-gate`'s `threshold` to `0.9` (a) with no
  approver or review reference; (b) naming `P-APPROVER` as approver and a review
  reference `review-cts-1`. Retrieve the Approval Workflow record for (b).
- **Expected:** (a) rejected; (b) accepted, and its record names `P-APPROVER` and
  `review-cts-1`.
- **Fails if:** (a) takes effect, or (b)'s record lacks either reference.

### CT-REL-021 — A Baseline is designated explicitly, by a Person holding `baseline_approve`

- **Capability:** core
- **Requirement:** Volume X, Baselines: "an Execution's Result MUST be explicitly
  designated as the reference standard, not inferred from simply being the first or the
  most recent Execution of a Scenario"; Appendix A §A.11; Appendix B §B.3, Approval
  Permissions.
- **Method:** Automated
- **Fixture:** F-BASE; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite` twice. List Baselines. Then designate the first
  Execution of `s-greeting` as a Baseline (a) as `P-NOPERM`, (b) as `P-APPROVER`. List
  Baselines again.
- **Expected:** The first listing is empty. (a) is rejected. (b) is accepted, and the
  Baseline has `scenario: s-greeting`, `environment: cts-env`, `execution_id` of the
  first Execution, `approved_by` naming `P-APPROVER`, `approved_at`, and an
  `approval_role` holding `baseline_approve`.
- **Fails if:** A Baseline exists before (b); (a) is accepted; or any field of (b) is
  missing or wrong.

### CT-REL-022 — Deleting a referenced Environment does not break history

- **Capability:** core
- **Requirement:** Appendix C §C.8: "`DELETE` MUST NOT silently invalidate a Baseline, a
  Snapshot, a Report, or an audit record that references the deleted entity"; Volume XII,
  Traceability.
- **Method:** Automated
- **Fixture:** F-BASELINED (2.7).
- **Action:** As `P-APPROVER`, `DELETE` `cts-env`. Retrieve the Baseline and the
  Snapshot.
- **Expected:** Either the deletion is rejected, or both the Baseline and the Snapshot
  remain retrievable with `cts-env` preserved as a frozen record.
- **Fails if:** The deletion succeeds and either record is lost, or its reference to
  `cts-env` no longer resolves.

### CT-REL-023 — A Release Decision can be traced back to its evidence

- **Capability:** core
- **Requirement:** Volume XII, Traceability: reconstruct "which Report a Release Decision
  relied on, which Snapshot pinned the configuration it was evaluated under, which
  Quality Gates it read ... who approved"; "A Release Decision that cannot be traced
  this far back is not meaningfully audited."
- **Method:** Inspection
- **Fixture:** F-OVERRIDDEN (2.7); its Release Decision.
- **Action:** From the implementation's records alone, follow the chain from the
  Release Decision to its Report, Snapshot, GateResults, the override and its approver,
  the Results each Gate read, their Executions, and each Execution's Conversation.
- **Expected:** The reviewer reaches every link, citing the record used at each step.
- **Fails if:** Any link cannot be followed.

### CT-REL-024 — An overridden Gate is reflected as overridden in the pipeline

- **Capability:** `ci_cd:<platform>`
- **Requirement:** Volume XIII, Quality Gates: "the Pipeline MUST reflect the override's
  outcome, not the underlying Gate's raw failure."
- **Method:** Automated
- **Fixture:** CT-REL-006's configuration, run from a pipeline on the claimed platform.
- **Action:** Run the pipeline to the point where it checks the Gates; override
  `semantic-gate`; let the pipeline continue.
- **Expected:** Before the override, the pipeline's Gate check fails. After it, the
  pipeline shows the overridden outcome, distinguishable from a plain pass.
- **Fails if:** The pipeline stays failed after the override, or shows it as a plain
  pass.

### CT-REL-025 — An unanswered review fails the pipeline instead of hanging it

- **Capability:** `ci_cd:<platform>` together with `human_review`
- **Requirement:** Volume XIII, Quality Gates: "a Pipeline that times out waiting on an
  unset `review_timeout` MUST fail the same way it would for any other blocking Gate, not
  hang."
- **Method:** Automated
- **Fixture:** As CT-DEC-011's fixture, with no `review_timeout`, run from a pipeline on
  the claimed platform with a pipeline timeout the tester sets.
- **Action:** Run the pipeline; do not answer the review.
- **Expected:** When the pipeline's timeout is reached, the pipeline fails as for a
  failed blocking Gate.
- **Fails if:** The pipeline passes, or is still waiting when its timeout plus the grace
  period of the waiting budget (1.6) has passed.

### CT-REL-026 — The basic loop runs end to end through all five layers

- **Capability:** core
- **Requirement:** §10, The Non-Negotiable Core: "The five logical layers ... MUST each
  be met somewhere. An implementation that cannot define a Scenario and Contract,
  execute it, capture evidence, assess it with at least one Oracle, and reach some
  Decision has not implemented ... AQEF's basic loop at all."
- **Method:** Automated
- **Fixture:** F-BASE; scripted Judge `J-PASS-90`.
- **Action:** In one sequence, with no step outside the implementation: load F-BASE;
  execute `cts-suite`; retrieve the Conversation; retrieve the Results; evaluate the
  Gates; as `P-RELEASE`, record a Release Decision.
- **Expected:** Each step succeeds: Definition (CT-CFG-001), Execution (CT-EXE-001),
  Evidence (CT-EXE-008), Assessment (CT-ASM-003, CT-ASM-004), Decision (CT-DEC-001,
  CT-REL-001), each as its own test describes.
- **Fails if:** Any layer cannot be reached within the implementation.

### CT-REL-027 — A Conformance Statement is published

- **Capability:** core
- **Requirement:** §10, Conformance Statement: "An implementation that claims AQEF
  Conformance MUST publish a **Conformance Statement** stating: the version of this
  specification it conforms to; the capabilities it claims ... using the identifiers
  below."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** Obtain the implementation's published Conformance Statement.
- **Expected:** It states a specification version and lists its claimed capabilities
  using §10's identifiers. It is the statement this test run uses to decide which tests
  are `NOT_APPLICABLE`.
- **Fails if:** No statement is published, it states no version, or a claimed
  capability is not given by a §10 identifier.

### CT-REL-028 — Every operation is authenticated and resolves to a Principal

- **Capability:** core
- **Requirement:** Appendix C §C.4: "All API operations MUST be authenticated" and the
  mechanism "MUST resolve to a Principal — a Person or a Service Account with an owning
  Person."
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** With no credentials, request `GET /projects/cts-base` and
  `POST /projects/cts-base/executions`. Then, as `P-NOPERM`, request
  `POST /projects/cts-base/executions` and query the audit log for that action.
- **Expected:** Both unauthenticated requests are rejected and start no Execution. The
  authenticated request is accepted, and the record of it names `P-NOPERM` as a Person.
- **Fails if:** Either unauthenticated request succeeds, or the authenticated one cannot
  be attributed to `P-NOPERM`.

### CT-REL-029 — A Report shows each Gate's status, basis, and why it did not pass

- **Capability:** core
- **Requirement:** Volume XI, Quality Gates: every applicable Gate "MUST show its current
  status — pass, fail, or a Governance-logged override ... and, where it failed, which
  aggregate and threshold it failed against"; "A Gate's displayed status MUST include
  the Aggregate Basis"; Appendix C §C.10, `gates`.
- **Method:** Automated
- **Fixture:** Two variants. (a) F-OVERRIDDEN (2.7). (b) CT-DEC-004's configuration.
- **Action:** In (b), execute `cts-suite` and evaluate the Gates. In each, retrieve the
  Report the implementation produced for the batch after its Gates were evaluated, in
  (a) including any Report produced after the override.
- **Expected:** Each Report has the fields of Appendix C §C.10. In (a), `gates` holds
  `semantic-gate`'s GateResult with `status: fail`, its `threshold`, `basis`, and
  `override`. In (b), `semantic-gate`'s GateResult has `reasons:
  [insufficient_basis]` and its `basis`.
- **Fails if:** A §C.10 field is missing; `semantic-gate` is absent from `gates`; (a)
  lacks the `override`; or (b) reports `threshold` as a reason.

### CT-REL-030 — Changing a Contract or Gate through any operation needs `contract_define`

- **Capability:** core
- **Requirement:** Appendix B §B.3, Governed configuration change: "Creating or changing
  a `contract`, `contracts`, or `quality_gates` value, through whatever operation, is
  `contract_define`"; Appendix C §C.5.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`.
- **Action:** As `P-EDITOR`, who holds `scenario_edit` and `project_edit` but not
  `contract_define`: (a) replace `s-greeting` with `PUT .../scenarios/s-greeting`,
  changing only `variables.query` to `"Hi"`; (b) replace it again, changing its
  Expectation's `confidence_threshold` to `0.5`; (c) replace the Project with
  `PUT /projects/cts-base`, changing `semantic-gate`'s `threshold` to `0.5`. Then query
  the audit log for action type `contract_define`.
- **Expected:** (a) accepted. (b) and (c) rejected, and the configuration keeps
  `confidence_threshold: 0.8` and `threshold: 1.0`. Made by `P-APPROVER` instead, (b)
  goes through Approval Workflow and is logged as `contract_define`.
- **Fails if:** (a) is rejected; (b) or (c) takes effect for `P-EDITOR`; or the change by
  `P-APPROVER` is not logged as `contract_define`.

### CT-REL-031 — A Release Policy is approved by a Person and never modified

- **Capability:** core
- **Requirement:** Appendix C §C.3, Release Policy: approving and revoking a policy
  require that "The Principal MUST be a Person"; "No operation modifies a Release
  Policy"; Appendix A §A.14.
- **Method:** Automated
- **Fixture:** F-BASE; `RP-1` in place.
- **Action:** Retrieve `RP-1`. As `SA-CI`, which holds `release_decide`, attempt to
  approve a policy `RP-2` with the same content, and to revoke `RP-1`. As `P-RELEASE`,
  attempt to change `RP-1`'s `environments` through any operation the implementation
  offers.
- **Expected:** `RP-1` has `id`, `project`, `suites`, `environments`,
  `service_accounts`, `approved_by` naming `P-RELEASE`, an `approval_role` holding
  `release_decide`, and `approved_at`. Both attempts by `SA-CI` are rejected. No
  operation changes `RP-1`'s content; it is unchanged when retrieved again.
- **Fails if:** A field is missing; an attempt by `SA-CI` is accepted; or `RP-1`'s
  content changes.

### CT-REL-032 — A Permission is checked, not a Role name

- **Capability:** core
- **Requirement:** Volume XII, Permissions: "A Permission MUST be checkable
  independently of any Role that happens to include it"; Appendix C §C.4: "Permission
  checks are against the atomic Permission, not the Role."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`. Two further
  Persons: `P-ROLE-A`, holding only a Role named `release_manager` that grants `read`
  and `execute`; and `P-ROLE-B`, holding only a Role named `observer` that grants `read`,
  `execute`, and `release_decide`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Record a Release Decision with the
  body of 14.1, made (a) by `P-ROLE-A` with `approved_by: P-ROLE-A` and
  `approval_role: release_manager`, then (b) by `P-ROLE-B` with
  `approved_by: P-ROLE-B` and `approval_role: observer`. Every other field is the same in
  both. Query the audit log, or the error returned, for the reason of (a).
- **Expected:** (a) is rejected because `P-ROLE-A` lacks the Permission
  `release_decide`: the error or the audit record says so, and does not report the body
  as malformed. (b) is accepted, and the stored decision names `observer` as
  `approval_role`.
- **Fails if:** (a) is accepted; (a) is rejected for a reason other than the missing
  Permission; or (b) is rejected. Either of the first two means that the Role's name,
  not its Permissions, decided.

### CT-REL-033 — A Service Account is never presented as a Person

- **Capability:** core
- **Requirement:** Volume XII, Principals: "A Service Account is not a stand-in for a
  person and MUST NOT be set up to look like one."
- **Method:** Automated, Inspection
- **Fixture:** F-SA-DECISIONS (2.7).
- **Action:** Retrieve decision (b), its audit entry, and `SA-CI`'s
  Principal record. Review whether the implementation lets a Service Account be created
  or presented with a Person's attributes (a personal name, a personal e-mail login, or
  a flag marking it as a Person).
- **Expected:** Wherever `SA-CI` appears, it is identified as a Service Account. The
  implementation offers no way to mark a Service Account as a Person.
- **Fails if:** `SA-CI` appears anywhere as, or indistinguishable from, a Person; or a
  Service Account can be set up as one.

### CT-REL-034 — A Baseline's Dataset and Contract versions stay recoverable

- **Capability:** core
- **Requirement:** Appendix B §B.3, Baseline reproducibility: "A Baseline MUST reference
  a Dataset version and Contract version that are still recoverable"; Appendix C §C.8.
- **Method:** Automated
- **Fixture:** CT-EXE-010's fixture, with `s-greeting`'s Contract moved into a Reusable
  Contract `cts-contract` (version 1) that the Scenario references by name.
- **Action:** Execute `cts-suite`; as `P-APPROVER`, designate the Execution as a
  Baseline. As a governed change, publish version 2 of `cts-contract` with
  `confidence_threshold: 0.85`, and register `ds-1@1.1.0`. Attempt to delete
  `ds-1@1.0.0` and version 1 of `cts-contract`, by whatever operations the
  implementation offers. Retrieve the Baseline, the Dataset version, and the Contract
  version it references.
- **Expected:** The Baseline names `ds-1@1.0.0` and version 1 of `cts-contract`, and
  both can still be retrieved with their original content; any deletion was rejected or
  left them preserved as frozen records.
- **Fails if:** The Baseline does not identify both versions, or either can no longer be
  retrieved as it was.

### CT-REL-035 — A Report surfaces what earlier Volumes flagged

- **Capability:** core
- **Requirement:** Volume XI, Reports: "a Report MUST surface the specific signals
  earlier Volumes have already flagged as worth including"; Appendix C §C.10, `signals`.
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`; add `execution: { scheduling: sequential,
  retry: { max_attempts: 2, on: infrastructure_failure } }`; scripted subject
  `SR-ECHO`, except that its first call for `s-1` fails as in `SR-503-THEN-OK`;
  scripted Judge `J-MAP(J-PASS-60, J-PASS-60, J-PASS-90)`.
- **Action:** Execute `cts-suite`; evaluate the Gates; retrieve the Report the
  implementation produced for the batch.
- **Expected:** `signals.retries` shows one Retry for `s-1`. `signals.low_confidence`
  shows, for `cts-scripted-judge@1`, two `inconclusive` Results of three. `signals.
  multi_judge`, `unenforced_boundaries`, and `boundary_attempts` are present and empty.
  `gates` holds both Gates, `semantic-gate` with `non_actionable_results`, each with its
  `basis`.
- **Fails if:** `signals` or any of its five lists is missing, or any count above is
  wrong.

### CT-REL-036 — A KPI decomposes into the Metrics and Results behind it

- **Capability:** core
- **Requirement:** Volume XI, KPIs: "a KPI MUST be traceable back to the Metric(s) it is
  drawn from."
- **Method:** Inspection
- **Fixture:** F-SIGNALS (2.7), and a KPI the tester defines in the implementation: the
  pass rate of `cts-suite`.
- **Action:** From the KPI as displayed, follow it to the Metric(s) it is drawn from
  and from them to the Results.
- **Expected:** The reviewer reaches the Metric and the individual Results from the KPI
  (for a Metric shown in a Report, through its entry in `metrics`, Appendix C §C.10),
  citing the records used. If the implementation offers no KPIs, which the
  specification does not require, the outcome is `NOT_APPLICABLE` (1.2).
- **Fails if:** The KPI is offered but cannot be traced to its Metric or Results.

### CT-REL-037 — A platform's native gate is not an AQEF Quality Gate

- **Capability:** `ci_cd:<platform>`
- **Requirement:** Volume XIII: an AQEF Quality Gate and a platform's own gating primitive
  "MUST NOT be conflated: AQEF's Quality Gate is defined once, platform-agnostically."
- **Method:** Inspection
- **Fixture:** CT-REL-024's configuration and pipeline.
- **Action:** Carry out CT-REL-024's Action. Review the integration's configuration and
  the platform's records for the pipeline run.
- **Expected:** The Gates are defined and evaluated in the implementation; the platform's
  native primitive only carries their outcome. Changing the platform's primitive does
  not change any Gate definition, and the reverse.
- **Fails if:** A Gate is defined, evaluated, or changed in the platform rather than in
  the implementation.

## 14.3 Core coverage

Not tests: a map of which tests exercise each part of the non-negotiable core (§10).
Only tests whose capability is `core` are listed. A part of the core with no `PASS`
among its tests has not been shown to be met.

| Core part | Tests |
|---|---|
| Layer: Definition | CT-CFG-001…025 |
| Layer: Execution | CT-EXE-001…007, CT-EXE-009…011 |
| Layer: Evidence | CT-EXE-003, CT-EXE-008, CT-EXE-012 |
| Layer: Assessment | CT-ASM-001…012, CT-ASM-014…019 |
| Layer: Decision | CT-DEC-001…009, CT-DEC-013, CT-DEC-014, CT-DEC-019…023, CT-REL-001…023, CT-REL-029…036 |
| Conformance Statement | CT-REL-027 |
| Principle: Contracts over Assertions | CT-CFG-002, CT-CFG-003, CT-CFG-004, CT-CFG-007, CT-CFG-012, CT-CFG-013, CT-CFG-015, CT-CFG-019, CT-ASM-011, CT-ASM-019, CT-REL-036 |
| Principle: Validation before Evaluation | CT-ASM-001, CT-ASM-002, CT-ASM-014, CT-ASM-017 |
| Principle: Independent Oracles | CT-CFG-006, CT-ASM-012 |
| Principle: Deterministic Infrastructure | CT-EXE-002, CT-EXE-006, CT-EXE-007, CT-ASM-009, CT-ASM-010, CT-ASM-016, CT-ASM-018, CT-EXE-010…012, CT-DEC-022, CT-DEC-023, CT-REL-010…014, CT-REL-034 |
| Principle: Probabilistic Subject | CT-EXE-003, CT-EXE-004, CT-EXE-005, CT-ASM-008, CT-ASM-015, CT-DEC-013 |
| Principle: Everything is a Test | None in this version |
| Principle: Everything has Confidence | CT-ASM-003…007, CT-DEC-002…008, CT-DEC-021 |
| The whole loop | CT-REL-026 |

"Everything is a Test" has no test yet. Its clearest observable forms, assessing a
captured production Conversation or one from an exploratory session, depend on
`dataset:production_replay` or on surfaces outside this version's scope.
