# 22. Capability: Seeded Controls

Tests in this section apply to an implementation whose Conformance Statement claims
`seeded_controls` (§10). For any other, they are `NOT_APPLICABLE`. CT-DEC-015 to
CT-DEC-018 also belong to this capability. F-SEED, `J-CATCH`, and `semantic-gate` are
defined in Section 13.1. CT-SCT-001 to CT-SCT-008 use defect controls; CT-SCT-009 to
CT-SCT-015 use clean controls.

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
    validator: schema
    target: response
    expected: { type: string, pattern: "Goodbye" }
variables:
  query: "Hello"
prompt:
  template: "{{query}}"
```

Here the "planted defect" is a farewell instead of a greeting; the confirmation passes
only if the Response the Judge receives contains it.

**Clean controls.** A clean control (`kind: clean`, Appendix A §A.4) carries Evidence
free of its defect class, which the Oracle is expected to pass. The tests below use two
more scripted behaviors and two fixtures.

| Code | Behavior |
|---|---|
| `SR-HI` | Returns the Response `"Hi there! What do you need?"`. |
| `J-ALARM` | Verdict `fail`, Confidence `0.90` for the Response `Hi there! What do you need?`; otherwise as `J-PASS-90`. |

`Hi there! What do you need?` greets the user, so a Judge that fails it raises a false
alarm on the class `greeting-missing`. `J-ALARM` passes `s-greeting`'s Response.

**F-CLEAN.** As F-SEED, with `s-control` replaced by a clean control, confirmed by
construction:

```yaml
- name: s-clean
  seeded_control:
    kind: clean
    defect_class: greeting-missing
    confirmed_by: construction
  evidence:
    conversation:            # in the implementation's own Conversation form
      - role: user
        content: "Hello"
      - role: assistant
        content: "Hi there! What do you need?"
  contract:
    expectations:
      - criteria: "The response greets the user."
        defect_classes: [greeting-missing]
        judge:
          model: cts-scripted-judge@1
          confidence_source: self_rating
        confidence_threshold: 0.8
```

**F-CLEAN-V.** As F-CLEAN, with `s-clean` confirmed by a Validator instead of by
construction: `evidence` removed, and

```yaml
seeded_control:
  kind: clean
  defect_class: greeting-missing
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

The confirmation passes only if the Response the Judge receives does not contain the
farewell that `greeting-missing` stands for here.

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
- **Fixture:** F-SEED-MISSED (2.7). `P-INVALIDATE` is a Person holding `read` and
  `seeded_control_invalidate`.
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
  class, was `caught` (a defect control) or `passed` (a clean control) by that Oracle
  configuration, and is not a control any Oracle missed or raised a false alarm on in a
  run whose Results the requalification will be used to re-assess."
- **Method:** Automated
- **Fixture:** F-SEED-MISSED (2.7), with `s-greeting`'s Result invalidated (not
  `not_assessed`; if the implementation left it `not_assessed`, the same steps apply to
  that Result). A corrected Judge configuration: model `cts-scripted-judge@2`, behaving
  as `J-CATCH`, with the same criteria. A fresh control `s-control-2`: as `s-control`,
  with the fixed Response `"Bye now."`, which `J-CATCH` also fails (13.1). Setup check:
  `J-CATCH` passed its self-test for `Goodbye.` and `Bye now.` (2.8).
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

### CT-SCT-009 — A clean control carries no planted defect and no prior

- **Capability:** `seeded_controls`
- **Requirement:** Appendix A §A.4, SeededControlConfig: `planted_defect` is required
  "if `kind` is `defect`" and "MUST NOT appear on a clean control"; `kind` is `defect` or
  `clean`; Appendix B §B.2: "`planted_defect` is REQUIRED when `kind` is `defect` or
  absent, and MUST NOT appear when it is `clean`; `difficulty_prior` MUST NOT appear when
  `kind` is `clean`."
- **Method:** Automated
- **Fixture:** Five variants. (a) F-CLEAN unchanged. (b) F-CLEAN with
  `planted_defect: "The response does not greet the user."` added to `s-clean`.
  (c) F-CLEAN with `difficulty_prior: not_established` added to `s-clean`. (d) F-CLEAN
  with `kind: unknown`. (e) F-SEED with `kind: defect` added to `s-control` and its
  `planted_defect` removed.
- **Action:** Load each variant.
- **Expected:** (a) loaded. (b), (c), (d), and (e) rejected.
- **Fails if:** (a) is rejected for lacking `planted_defect`; or any of (b) to (e) is
  loaded.

### CT-SCT-010 — A clean control the Oracle passes invalidates nothing and is not aggregated

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: "Seeded Control Results themselves MUST
  be excluded from Aggregation"; Appendix C §C.3, Seeded Control Reporting: "`GET
  .../executions/{execution}` MUST include a `seeded_control_results` array, one entry per
  Seeded Control Scenario in that run", with `kind`, and `outcome` "`passed` or
  `false_alarm` for a clean control".
- **Method:** Automated
- **Fixture:** F-CLEAN with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; retrieve the Execution records; evaluate the Gates.
- **Expected:** `seeded_control_results` has one entry for `s-clean`: `kind: clean`,
  `defect_class: greeting-missing`, `outcome: passed`, `confirmed_by: construction`,
  `invalidation_scope: none`, `reason: null`. The scripted subject received exactly one
  call. Both Gates pass; `semantic-gate` has `basis.results: 1` and `basis.scenarios: 1`.
- **Fails if:** The entry is missing, lacks `kind`, or reports `caught`; anything is
  invalidated; the `s-clean` Result is counted in any `basis` field; or either Gate
  fails.

### CT-SCT-011 — A false alarm invalidates its class and is reported as a false alarm

- **Capability:** `seeded_controls`
- **Requirement:** Volume I, Chapter 6, Quality Gates: "A Quality Gate MUST NOT pass on
  any aggregate to which an Oracle contributed Results sharing a missed Seeded Control's
  defect class"; Appendix B §B.3, Clean control: a false alarm "is a miss for every rule
  on missed Seeded Controls ..., reported as `false_alarm`, with
  `seeded_control_false_alarm` on an affected GateResult"; Gate reasons: such a Gate
  "MUST fail, with `non_actionable_results`, `seeded_control_miss`, or
  `seeded_control_false_alarm`"; Invalidation is derived: a missed control "MUST NOT
  change any recorded Result."
- **Method:** Automated
- **Fixture:** F-CLEAN with `semantic-gate`; scripted Judge `J-ALARM`.
- **Action:** Execute `cts-suite`; retrieve the Execution records and every Result;
  evaluate the Gates.
- **Expected:**
  - The entry for `s-clean` has `kind: clean`, `outcome: false_alarm`,
    `invalidation_scope: defect_class`, `reason: null`.
  - `s-greeting`'s Expectation either has a recorded Result with `verdict: pass` and
    `disposition: actionable` whose `invalidated_by` lists `{ scenario: s-clean,
    defect_class: greeting-missing }`, or, if the Judge was no longer invoked for it, a
    Result with `disposition: not_assessed` and `verdict: null`.
  - `semantic-gate` fails with `seeded_control_false_alarm` in `reasons`, and without
    `seeded_control_miss`. Its `basis` counts no Result of `s-clean`.
  - `functional-gate` passes.
- **Fails if:** `semantic-gate` passes; its `reasons` reports the false alarm as
  `seeded_control_miss` or omits `seeded_control_false_alarm`; the outcome is `missed`
  or `caught`; a recorded `verdict` or `disposition` was changed; or `functional-gate`
  fails.

### CT-SCT-012 — A clean control is invalid unless its cleanness is confirmed

- **Capability:** `seeded_controls`
- **Requirement:** Appendix B §B.3, Seeded Control confirmation: "A control's outcome
  MUST be reported as `invalid` for that run, not as `caught`, `missed`, `passed`, or
  `false_alarm`, unless what it declares about the Evidence the Oracle received ... was
  confirmed"; Appendix A §A.4, `confirmation`: "the planted defect present, or, for a
  clean control, absent. Where it fails, the control is `invalid` for that run."
- **Method:** Automated
- **Fixture:** F-CLEAN-V with `semantic-gate`; scripted Judge `J-ALARM`.
- **Action:** Run 1: execute `cts-suite` with scripted subject `SR-BYE` for `s-clean` and
  `SR-OK` for `s-greeting`; evaluate the Gates. Run 2: execute it with `SR-HI` for
  `s-clean` and `SR-OK` for `s-greeting`; evaluate the Gates.
- **Expected:** Run 1: the confirmation fails, since the Response contains the farewell;
  `s-clean`'s outcome is `invalid`, `invalidation_scope: none`, and `semantic-gate`
  passes. Run 2: the confirmation passes, `J-ALARM` fails `Hi there! What do you need?`,
  the outcome is `false_alarm`, and `semantic-gate` fails with
  `seeded_control_false_alarm`.
- **Fails if:** Run 1 reports `passed` or `false_alarm`, or invalidates anything; or run
  2 reports anything but `false_alarm`.

### CT-SCT-013 — A clean control confirmed by a Human Reviewer is invalid until confirmed

- **Capability:** `seeded_controls` together with `human_review`
- **Requirement:** as CT-SCT-012; Appendix C §C.3, `POST
  .../seeded-controls/{scenario}/confirm`: "Record a Human Reviewer's confirmation that
  the planted defect is present (or, for a clean control, that the defect class is
  absent) ... The Principal MUST be a Person."
- **Method:** Automated
- **Fixture:** F-CLEAN-V with `semantic-gate`, `s-clean` given `confirmed_by:
  human_reviewer` and its `confirmation` removed; scripted subject `SR-HI` for
  `s-clean`, `SR-OK` for `s-greeting`; scripted Judge `J-ALARM`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Attempt the confirmation as
  `SA-CI`, then make it as `P-REVIEWER`, with `POST
  .../executions/{execution}/seeded-controls/s-clean/confirm`. Retrieve the Execution
  again; evaluate the Gates again.
- **Expected:** `SA-CI`'s attempt is rejected. Before confirmation, the outcome is
  `invalid` and the first evaluation of `semantic-gate` passes. After it, the outcome is
  `false_alarm`, the second evaluation of `semantic-gate` fails with
  `seeded_control_false_alarm`, and the first GateResult is still recorded unchanged.
- **Fails if:** The outcome is `passed` or `false_alarm` before confirmation; it stays
  `invalid` after; `SA-CI`'s attempt is accepted; or the first GateResult is altered.

### CT-SCT-014 — After a false alarm, requalification rests on passed clean controls

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Requalification: the corrected Oracle "catches fresh
  defect controls of that class, or, after a false alarm, passes fresh clean controls of
  it"; Appendix C §C.3, Requalification: the request "MUST be rejected unless each named
  control is of that class, was `caught` (a defect control) or `passed` (a clean control)
  by that Oracle configuration, and is not a control any Oracle missed or raised a false
  alarm on in a run whose Results the requalification will be used to re-assess";
  `reassess`: "MUST be rejected ... for an Oracle without a Requalification record
  (below) for every defect class in the Result's `invalidated_by`, resting on controls
  of the kind that failed: caught defect controls after a miss, passed clean controls
  after a false alarm".
- **Method:** Automated
- **Fixture:** F-CLEAN with `semantic-gate`; scripted Judge `J-ALARM`. Setup: execute
  `cts-suite` and evaluate the Gates; setup check: `s-clean`'s entry has `outcome:
  false_alarm`. `s-greeting`'s Result is invalidated; if the implementation left it
  `not_assessed`, the same steps apply to that Result. A corrected Judge configuration: model `cts-scripted-judge@2`, behaving
  as `J-CATCH`, with the same criteria. Two fresh controls of `greeting-missing`:
  `s-clean-2`, as `s-clean` with the fixed Response `"Hello, what can I do for you?"`,
  and `s-control-2`, as F-SEED's `s-control` with the fixed Response `"Bye now."`.
- **Action:** (a) Run `s-clean`, `s-clean-2`, and `s-control-2` against
  `cts-scripted-judge@2`. (b) `POST /projects/cts-base/requalifications` for
  `cts-scripted-judge@2` and `greeting-missing`, naming its Result on `s-control-2`.
  (c) Request that `cts-scripted-judge@2` re-assess `s-greeting`'s stored Evidence from
  the setup run. (d) Request a requalification as in (b), naming its Result on
  `s-clean`. (e) The same, naming its Result on `s-clean-2`. (f) Repeat request (c).
  (g) Evaluate the Gates again for the setup batch.
- **Expected:** (a) `s-clean` and `s-clean-2` are `passed`, `s-control-2` is `caught`.
  (b) accepted: a defect control the Oracle caught. (c) rejected: the Result was
  invalidated by a false alarm, and the only Requalification rests on a defect control.
  (d) rejected: `s-clean` raised the false alarm in the run to be re-assessed.
  (e) accepted. (f) accepted: a new Result from `cts-scripted-judge@2` with `resolves`
  naming the invalidated one and `verdict: pass`; the scripted subject is not called.
  (g) `semantic-gate` passes; the setup GateResult stays recorded.
- **Fails if:** (b) or (e) is rejected; (c) or (d) is accepted; (f) is rejected or calls
  the subject; or (g) fails.

### CT-SCT-015 — Under `halt_run`, a false alarm invalidates the whole run

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Clean controls: a false alarm "is a miss in every rule of
  this specification that speaks of a missed Seeded Control"; Appendix A §A.9,
  `on_seeded_control_miss`: "`halt_run` stops the run and records a full-run
  invalidation with this policy as the reason"; Appendix C §C.3: "Under `full_run`,
  no Result of that run counts as `actionable` for any Quality Gate, whatever its defect
  class"; `reason` "MUST be present and non-empty when `invalidation_scope` is
  `full_run`".
- **Method:** Automated
- **Fixture:** F-CLEAN with `semantic-gate`; add `execution: { on_seeded_control_miss:
  halt_run }` to the Project; scripted Judge `J-ALARM`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `s-clean`'s entry has `outcome: false_alarm`, `invalidation_scope:
  full_run`, and a non-empty `reason`. Both `functional-gate` and `semantic-gate` fail,
  each with `seeded_control_false_alarm` in `reasons`.
- **Fails if:** Either Gate passes; either lacks `seeded_control_false_alarm`; or
  `reason` is empty or `null`.
