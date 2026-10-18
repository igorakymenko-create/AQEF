# 22. Capability: Seeded Controls

Tests in this section apply to an implementation whose Conformance Statement claims
`seeded_controls` (§10). For any other, they are `NOT_APPLICABLE`. CT-DEC-015 to
CT-DEC-018 also belong to this capability. F-SEED, `J-CATCH`, and `semantic-gate` are
defined in Section 13.1.

**Further scripted subject behavior.**

| Code | Behavior |
|---|---|
| `SR-BYE` | Returns the Response `"Goodbye."`. |

**F-SEED-V.** As F-SEED, with `s-control` confirmed by a Validator instead of by
construction: `evidence` removed, and

```yaml
seeded_control:
  defect_class: greeting-missing
  planted_defect: "The response does not greet the user."
  confirmed_by: validator
  confirmation:
    validator: forbidden-content
    target: response
    expected:
      patterns:
        - regex: "Goodbye"
variables:
  query: "Hello"
prompt:
  template: "{{query}}"
```

Here the "planted defect" is a farewell instead of a greeting; the confirmation passes
only if the Response the Judge receives contains it.

### CT-SCT-001 — A Seeded Control states its class, its defect, and how it is confirmed

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: "A Seeded Control MUST record the defect
  it plants (`planted_defect`)"; Appendix A §A.4, SeededControlConfig: `defect_class`,
  `planted_defect`, and `confirmed_by` are required.
- **Method:** Automated
- **Fixture:** Three variants of F-SEED, each with one of `defect_class`,
  `planted_defect`, `confirmed_by` removed from `s-control`.
- **Action:** Load each variant.
- **Expected:** All three rejected.
- **Fails if:** Any is loaded.

### CT-SCT-002 — Each confirmation method has its own shape

- **Capability:** `seeded_controls`
- **Requirement:** Appendix B §B.2, SeededControlConfig: "`confirmation` is REQUIRED when
  `confirmed_by` is `validator` and MUST NOT appear otherwise. When `confirmed_by` is
  `construction`, the Scenario MUST carry `evidence` and MUST NOT carry `prompt`,
  `dataset`, or `variables`"; Appendix B §B.3, Fixed Evidence scope.
- **Method:** Automated
- **Fixture:** Five variants. (a) F-SEED-V without `confirmation`. (b) F-SEED with
  F-SEED-V's `confirmation` added. (c) F-SEED without `evidence`. (d) F-SEED with
  `variables` and `prompt` added. (e) F-BASE with F-SEED's `evidence` added to
  `s-greeting`, which is not a Seeded Control.
- **Action:** Load each variant.
- **Expected:** All five rejected.
- **Fails if:** Any is loaded.

### CT-SCT-003 — An unconfirmed planted defect makes the control invalid

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: a control's outcome "MUST therefore be
  `invalid` for the run ... unless the presence of its planted defect in that Evidence
  has been confirmed"; Appendix B §B.3, Seeded Control confirmation.
- **Method:** Automated
- **Fixture:** F-SEED-V with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Run 1: execute `cts-suite` with scripted subject `SR-OK` for every
  Scenario; evaluate the Gates. Run 2: execute it with `SR-BYE` for `s-control` and
  `SR-OK` for `s-greeting`; evaluate the Gates.
- **Expected:** Run 1: the confirmation fails, `s-control`'s outcome is `invalid`,
  `invalidation_scope: none`, and `semantic-gate` passes, since nothing is invalidated.
  Run 2: the confirmation passes, the Judge passes `Goodbye.`, the outcome is `missed`,
  and `semantic-gate` fails with `seeded_control_miss`.
- **Fails if:** Run 1 reports `caught` or `missed`, or invalidates anything; or run 2
  reports anything but `missed`.

### CT-SCT-004 — A control confirmed by a Human Reviewer is invalid until confirmed

- **Capability:** `seeded_controls` together with `human_review`
- **Requirement:** as CT-SCT-003; Appendix A §A.4, `confirmed_by: human_reviewer`: "a
  Human Reviewer confirms it per run."
- **Method:** Automated
- **Fixture:** F-SEED-V with `confirmed_by: human_reviewer` and `confirmation` removed;
  scripted subject `SR-BYE` for `s-control`, `SR-OK` for `s-greeting`; scripted Judge
  `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Attempt the confirmation as
  `SA-CI` (Section 14.1), then make it as `P-REVIEWER`, with
  `POST .../executions/{execution}/seeded-controls/s-control/confirm` (Appendix C §C.3).
  Retrieve the Execution again; evaluate the Gates again.
- **Expected:** `SA-CI`'s attempt is rejected (the Principal must be a Person). Before
  confirmation, the outcome is `invalid` and the first evaluation of
  `semantic-gate` passes. After it, the outcome is `missed`, the second evaluation of
  `semantic-gate` fails with `seeded_control_miss`, and the first GateResult is still
  recorded unchanged.
- **Fails if:** The outcome is `caught` or `missed` before confirmation; it stays
  `invalid` after; or the first GateResult is altered.

### CT-SCT-005 — A difficulty prior is "not established" until it has a basis

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: "A prior MUST state how many control
  instances it was established on, and a class or control with no such history MUST be
  represented as 'not yet established', not as zero"; Appendix A §A.1,
  DefectClassConfig.
- **Method:** Automated
- **Fixture:** Two variants of F-SEED. (a) `greeting-missing` with
  `difficulty_prior: 0.9` and no `prior_basis` or `prior_source`. (b) F-SEED unchanged:
  no prior.
- **Action:** Load (a). Load (b), execute `cts-suite`, and retrieve the defect class and
  every record in which the implementation reports a prior for it.
- **Expected:** (a) rejected. (b) Wherever the prior is reported, it reads
  `"not_established"`, never `0` or `0.0`.
- **Fails if:** (a) is loaded, or (b) reports the prior as a number.

### CT-SCT-006 — A prior comes from Oracles independent of the one under test

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: "A prior MUST be established from
  reference Oracles independent of the Oracle under test ... and MUST NOT be updated
  from how the Oracle under test performs against the controls"; Appendix A §A.1,
  `reference_oracles`: "Each MUST satisfy Independent Oracles ... with respect to every
  Oracle the class's controls test."
- **Method:** Automated
- **Fixture:** (a) F-SEED with `greeting-missing` given `difficulty_prior: 0.9`,
  `prior_basis: 50`, `prior_source: reference_oracles`, and `reference_oracles` holding
  `cts-scripted-judge@1`, the very Judge the controls test. (b) The same with
  `reference_oracles` holding `cts-reference-judge@1` instead.
- **Action:** Load (a). Load (b); execute `cts-suite` with `J-PASS-90`, so that the
  Judge misses `s-control`; retrieve the defect class.
- **Expected:** (a) rejected. (b) After the miss, the prior is still `0.9` on a basis of
  `50`.
- **Fails if:** (a) is loaded, or the miss changed the prior or its basis.

### CT-SCT-007 — Full-run invalidation needs a reason and a Permission

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: full-run invalidation "is a deliberate
  decision, not the default, and MUST record a reason"; Appendix C §C.3, invalidate:
  "Body MUST include a non-empty `reason`"; `seeded_control_invalidate` "is an ordinary
  checked Permission."
- **Method:** Automated
- **Fixture:** As CT-DEC-015, after its Action. `P-INVALIDATE` is a Person holding
  `read` and `seeded_control_invalidate`.
- **Action:** `POST .../executions/{execution}/seeded-controls/s-control/invalidate`
  (a) as `P-INVALIDATE` with `reason: ""`; (b) as `P-NOPERM` with a non-empty reason;
  (c) as `P-INVALIDATE` with `reason: "Judge prompt changed today"`. Evaluate the Gates.
  Query the audit log for the action.
- **Expected:** (a) and (b) rejected. (c) accepted: the entry's `invalidation_scope`
  becomes `full_run` and `reason` holds the text given. Both Gates now fail with
  `seeded_control_miss`, `functional-gate` included. The audit log records (c), naming
  `P-INVALIDATE`.
- **Fails if:** (a) or (b) is accepted; (c) leaves the scope at `defect_class` or the
  reason empty; `functional-gate` passes; or (c) is not in the audit log.

### CT-SCT-008 — A requalified Oracle may resolve what its miss invalidated

- **Capability:** `seeded_controls`
- **Requirement:** Volume I, Chapter 6, Result Resolution: a Result "from a requalified
  Oracle re-assessing stored Evidence ... only once the Oracle has been requalified for
  every defect class whose miss reached that Result"; Volume VIII, Requalification:
  "Without that record, the Oracle is not requalified"; Appendix C §C.3,
  Requalification: the request "MUST be rejected unless each named control is of that
  class, was `caught` by that Oracle configuration, and is not a control any Oracle
  missed in a run whose Results the requalification will be used to re-assess."
- **Method:** Automated
- **Fixture:** As CT-DEC-015, after its Action, with `s-greeting`'s Result invalidated
  (not `not_assessed`; if the implementation left it `not_assessed`, the same steps
  apply to that Result). A corrected Judge configuration: model
  `cts-scripted-judge@2`, behaving as `J-CATCH`, with the same criteria. A fresh control
  `s-control-2`: as `s-control`, with the fixed Response `"Bye now."`, which `J-CATCH`
  also fails.
- **Action:** (a) Request that `cts-scripted-judge@2` re-assess `s-greeting`'s stored
  Evidence. (b) Run `s-control` and `s-control-2` against `cts-scripted-judge@2`.
  (c) `POST /projects/cts-base/requalifications` for `cts-scripted-judge@2` and
  `greeting-missing`, naming its Result on `s-control`. (d) The same, naming its Result
  on `s-control-2`. (e) Repeat request (a). (f) Evaluate the Gates again for the original
  batch.
- **Expected:** (a) rejected: no Requalification record yet. (b) Both controls are
  `caught`. (c) rejected: `s-control` is the control missed in the run to be
  re-assessed. (d) accepted, and the record names the Oracle, the class, and the
  `s-control-2` Result. (e) accepted: a new Result from `cts-scripted-judge@2` with
  `resolves` naming the invalidated one and `verdict: pass`; the scripted subject is not
  called. (f) `semantic-gate` passes; the earlier GateResult stays recorded.
- **Fails if:** (a) or (c) is accepted; (d) or (e) is rejected; (e) calls the subject; or
  (f) fails.
