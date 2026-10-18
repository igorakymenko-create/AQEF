# 13. Decision

Tests in this section evaluate Quality Gates over the Results of one or more Executions
and observe the GateResults (Appendix A §A.12), their Aggregate Basis (Appendix C §C.3),
and how resolution and Seeded Controls change what a Gate reads.

## 13.1 Fixtures and conventions for this section

**Evaluating the Gates.** "Evaluate the Gates" means `POST /projects/cts-base/gates/check`
for the batch the Action produced, or the implementation's equivalent. It returns one
GateResult per applicable Gate and a `snapshot_id`.

**`semantic-gate`.** Every test in this section adds a second blocking Gate to its
fixture's Project-level `quality_gates`:

```yaml
- name: semantic-gate
  aggregate: semantic
  threshold: 1.0
  on_failure: block_release
```

**Which Gate reads which clause.** By the `dimension` defaults of Appendix A §A.5:
`functional-gate` reads the schema Constraint, `semantic-gate` the Expectation, and
`safety-gate` the forbidden-content Constraint.

**Recording a Human Reviewer Result.** "As `P-REVIEWER`, record ..." means
`POST .../results/{result}/review` (Appendix C §C.3) on the Result named, made by
`P-REVIEWER`: a Person holding `review` and the Role `reviewer`.

**Requesting a re-assessment.** "Request that ... assess the stored Evidence again"
means `POST .../results/{result}/reassess` on the Result named, made by `P-RELEASE`
(Section 14.1), naming the Oracle configuration. Appendix C §C.3 specifies `reassess`
as an operation of a conformant implementation's API. An implementation that offers
neither it nor an equivalent fails every test that requests a re-assessment, and the
test report says that the operation is missing.

**Additional scripted Judge behaviors.**

| Code | Behavior |
|---|---|
| `J-MAP(a, b, c)` | With scripted subject `SR-ECHO` and F-MULTI: behaves as `a` for the Response `One`, `b` for `Two`, `c` for `Three`. |
| `J-CATCH` | Verdict `fail`, Confidence `0.90` for the Responses `Goodbye.` and `Bye now.`; otherwise as `J-PASS-90`. |

**F-SEED — a Seeded Control.** As F-BASE, plus a defect class on the Project and a second
Scenario in `cts-suite`, confirmed by construction:

```yaml
project:
  defect_classes:
    - name: greeting-missing
  suites:
    - name: cts-suite
      scenarios:
        # s-greeting as in F-BASE, then:
        - name: s-control
          seeded_control:
            defect_class: greeting-missing
            planted_defect: "The response does not greet the user."
            confirmed_by: construction
          evidence:
            conversation:            # in the implementation's own Conversation form
              - role: user
                content: "Hello"
              - role: assistant
                content: "Goodbye."
          contract:
            expectations:
              - criteria: "The response greets the user."
                defect_classes: [greeting-missing]
                judge:
                  model: cts-scripted-judge@1
                  confidence_source: self_rating
                confidence_threshold: 0.8
```

`s-control` and `s-greeting` bind the same Oracle: the same Judge model and the same
criteria. The Expectation in `s-greeting` lists no `defect_classes`, so it is treated as
covering every class its Oracle is tested on (Appendix A §A.5). With `J-PASS-90`, the
Judge passes `Goodbye.` and so misses the control; with `J-CATCH`, it catches it.

## 13.2 Tests

### CT-DEC-001 — A passing GateResult has the required shape

- **Capability:** core
- **Requirement:** Appendix A §A.12, GateResult; Appendix C §C.3, Quality Gate:
  `gates/check` "Returns one GateResult (Appendix A §A.12) per Gate and the
  `snapshot_id` captured for the evaluation."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** A `snapshot_id`, and one GateResult each for `functional-gate` and
  `semantic-gate`, each with an `id`, `status: pass`, `blocking: true`, no `reasons`, a
  numeric `value`, `threshold: 1.0`, a `basis` object, and no `override`. The two `id`s
  differ.
- **Fails if:** Either GateResult is missing, any of those fields is absent or differs,
  the two share an `id`, `value` is bare `null`, or no `snapshot_id` is returned.

### CT-DEC-002 — The Aggregate Basis counts what the aggregate rests on

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Aggregate Basis: "Every aggregate a Quality Gate
  reads MUST therefore state its **Aggregate Basis**"; Appendix C §C.3, Aggregate Basis
  Reporting.
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate`'s `basis` is `results: 3`, `not_actionable: 0`,
  `scenarios: 3`, `executions: 3`, `min_basis_met: "not_declared"`.
- **Fails if:** `basis` is absent, any field is missing, or any count differs.

### CT-DEC-003 — A minimum met and no minimum declared are reported differently

- **Capability:** core
- **Requirement:** Appendix C §C.3: a Gate that set no minimum and a Gate whose minimum
  was met "are different facts and MUST NOT be reported the same way."
- **Method:** Automated
- **Fixture:** Two variants of F-MULTI with `semantic-gate`; scripted Judge `J-PASS-90`.
  (a) `semantic-gate` as given. (b) `semantic-gate` with `min_basis: { scenarios: 3 }`.
- **Action:** For each variant, execute `cts-suite` and evaluate the Gates.
- **Expected:** `semantic-gate` passes in both. `min_basis_met` is `"not_declared"` in
  (a) and `true` in (b).
- **Fails if:** The two values are the same, either is bare `null` or absent, or either
  Gate fails.

### CT-DEC-004 — An unmet minimum basis fails as insufficient basis, not as a threshold failure

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: "the Gate MUST NOT pass, and the
  reason MUST be recorded as insufficient basis rather than as a threshold failure";
  Appendix B §B.3, Aggregate Basis reporting.
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`, given `min_basis: { scenarios: 4 }`;
  scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate` has `status: fail`, `reasons: [insufficient_basis]`, and
  `basis.min_basis_met: false`.
- **Fails if:** The Gate passes, `reasons` lacks `insufficient_basis`, or `reasons`
  contains `threshold` (every Result passed).

### CT-DEC-005 — A failing verdict fails the threshold and nothing else

- **Capability:** core
- **Requirement:** Appendix A §A.12, GateResult `reasons`: `threshold` ("the value fell
  short"); Appendix B §B.3, Gate reasons.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate`: `status: fail`, `reasons: [threshold]`, a `value` below
  1.0, `basis.results: 1`, `basis.not_actionable: 0`. `functional-gate`: `status: pass`.
- **Fails if:** `semantic-gate` passes or lists any other reason; or `functional-gate`
  fails.

### CT-DEC-006 — An inconclusive Result blocks its Gate

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: a Gate reading an aggregate that
  includes an effective Result whose effective state is not `actionable` "MUST treat that
  Result as blocking, and MUST record why"; Volume I, Chapter 6, Decision Pipeline: it
  "MUST NOT skip the Confidence Model and aggregate raw pass/fail counts directly";
  Appendix B §B.3, Gate reasons.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-60`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate`: `status: fail`; `reasons` includes
  `non_actionable_results`; `basis.results: 0`; `basis.not_actionable: 1`; `value` is a
  number or `"not_computed"`.
- **Fails if:** The Gate passes; `reasons` lacks `non_actionable_results`; the
  inconclusive Result is counted in `basis.results`; or `value` is bare `null`.

### CT-DEC-007 — An unreachable Judge blocks its Gate

- **Capability:** core
- **Requirement:** as CT-DEC-006; Appendix C §C.7, `oracle_unavailable`: "MUST NOT be
  treated as an implicit pass."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-DOWN`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** As CT-DEC-006.
- **Fails if:** As CT-DEC-006.

### CT-DEC-008 — A failed GateResult lists every reason that applies

- **Capability:** core
- **Requirement:** Appendix B §B.3, Gate reasons: "A failed GateResult MUST list every
  applicable reason"; Appendix A §A.12, `reasons`: "Every reason that applies, none
  omitted."
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`, given `min_basis: { results: 3 }`; scripted
  subject `SR-ECHO`; scripted Judge `J-MAP(J-FAIL-90, J-PASS-60, J-PASS-90)`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate` has `status: fail`, and `reasons` contains `threshold`
  (`s-1` failed), `non_actionable_results` (`s-2` is inconclusive), and
  `insufficient_basis` (two `actionable` Results, three required). `basis.results: 2`,
  `basis.not_actionable: 1`.
- **Fails if:** Any of the three reasons is missing.

### CT-DEC-009 — No configuration lets a non-actionable Result pass a Gate

- **Capability:** core
- **Requirement:** Appendix C §C.7: "There is no configuration that turns this off: the
  way past a non-`actionable` Result is to resolve it, or, for a blocking Gate, an
  override approved for that one Gate Result."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** Review every configuration option the implementation documents for Quality
  Gates, Contracts, Aggregation, and the Decision Pipeline.
- **Expected:** None of them causes a Gate to pass while its aggregate includes an
  effective Result that is not `actionable`.
- **Fails if:** Any option does, whatever it is called.

### CT-DEC-010 — A Human Reviewer's Result resolves an inconclusive one, which is not counted again

- **Capability:** `human_review`
- **Requirement:** Volume I, Chapter 6, Result Resolution: the effective Result is "the
  last Result in that chain. Every earlier Result stays in the record ... and is not
  counted again by any aggregate or Quality Gate"; Appendix B §B.3, Result resolution:
  "A resolved Result MUST NOT be counted again, including in `basis.not_actionable`."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-60`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-REVIEWER`, record a Human
  Reviewer Result with verdict `pass` for the Expectation, resolving the Judge's Result.
  Evaluate the Gates again.
- **Expected:** The first evaluation fails as in CT-DEC-006. The Human Reviewer Result
  has `oracle_type: human_reviewer`, `resolves` naming the Judge's Result, and
  `disposition: actionable`. In the second evaluation, `semantic-gate` passes with
  `basis.results: 1` and `basis.not_actionable: 0`. The Judge's Result is still
  retrievable, unchanged, and the first GateResult is still recorded as it was.
- **Fails if:** The second evaluation fails; the Judge's Result is counted in either
  basis field; the Judge's Result is modified or removed; or the first GateResult is
  altered.

### CT-DEC-011 — A Result awaiting review blocks, then completes

- **Capability:** `human_review`
- **Requirement:** Appendix C §C.7, `awaiting_review`: "This is the one disposition a
  Result leaves: it completes once the review returns"; Volume VI, Human Review: an
  unanswered review "is never silently treated as a pass."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; in the Expectation, replace `judge` and
  `confidence_threshold` with `human_reviewer: { role: reviewer }`.
- **Action:** Execute `cts-suite`; evaluate the Gates. As `P-REVIEWER`, return verdict
  `pass` on the pending review. Evaluate the Gates again.
- **Expected:** Before the review, the Expectation's Result has
  `disposition: awaiting_review`, `verdict: null`, `confidence: "not_applicable"`, and
  `semantic-gate` fails with `non_actionable_results`. After it, the Result with the same
  `id` has `verdict: pass`, `disposition: actionable`, and the same `recorded_at` as
  before, and `semantic-gate` passes.
- **Fails if:** `semantic-gate` passes before the review; the pending Result has a
  verdict; the Gate still fails after the review; or the review produced a second Result
  instead of completing the pending one.

### CT-DEC-012 — The chain of resolutions is linear

- **Capability:** `human_review`
- **Requirement:** Appendix B §B.3, Result resolution: "`resolves` MUST reference the
  current effective Result for the same `execution` and `clause`, and that Result's
  effective state MUST NOT be `actionable`. A second Result resolving the same Result
  MUST be rejected."
- **Method:** Automated
- **Fixture:** Three variants. (a), (b): F-REVIEWED (2.7). (c): F-BASE with
  `semantic-gate`; scripted Judge `J-PASS-90`. (d): F-BASE with `semantic-gate`;
  scripted Judge `J-PASS-60`.
- **Action:** In (c) and (d), execute `cts-suite`. In each variant, record every Result
  of the run and evaluate the Gates; then make the variant's attempt; then record the
  Results again and evaluate the Gates again. The attempts, each a review of the
  Expectation (13.1): (a) as `P-REVIEWER`, verdict `fail`, resolving the Judge's Result
  again; (b) as `P-REVIEWER`, resolving the Human Reviewer Result recorded when
  F-REVIEWED was built; (c) as `P-REVIEWER`, resolving the Judge's `actionable` Result;
  (d) as `P-NOPERM`, who does not hold `review`, resolving the Judge's `inconclusive`
  Result.
- **Expected:** Each attempt is rejected with an error. In each variant, the Results
  after the attempt are the Results before it, none added, changed, or removed; the
  effective Result for the Expectation is the same; and the second evaluation gives
  every Gate the same `status` and `reasons` as the first. Any record the implementation
  keeps of the rejected attempt itself is not a Result.
- **Fails if:** An attempt is accepted; a Result is added, changed, or removed; the
  effective Result changes; or a Gate's `status` or `reasons` changes.

### CT-DEC-013 — The same Oracle asked again does not resolve an inconclusive Result

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Result Resolution: "Apart from that last case,
  the same Oracle asked again resolves nothing: that is a retry until a favorable verdict
  appears, which Volume III prohibits."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-60` for the first
  call and `J-PASS-90` for every later call.
- **Action:** Execute `cts-suite`. Request that the same Judge configuration assess the
  stored Evidence again. Evaluate the Gates.
- **Expected:** The request is rejected, or produces a Result that does not resolve the
  inconclusive one. `semantic-gate` fails with `non_actionable_results`.
- **Fails if:** A Result from the same Judge configuration resolves the inconclusive
  Result; `semantic-gate` passes; or the implementation offers no way to request a
  re-assessment (13.1).

### CT-DEC-014 — The same Oracle may resolve its own `oracle_unavailable` Result

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Result Resolution: "a Result from the same Oracle
  configuration, resolving an `oracle_unavailable` Result once that Oracle can be reached
  or run again"; Volume VI, Human Review.
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-DOWN`.
- **Action:** Execute `cts-suite`; evaluate the Gates. Switch the scripted Judge to
  `J-PASS-90`. Request that the same Judge configuration assess the stored Evidence
  again. Evaluate the Gates again.
- **Expected:** The first evaluation fails with `non_actionable_results`. The new Result
  has `resolves` naming the `oracle_unavailable` Result, `verdict: pass`, and
  `disposition: actionable`. The second evaluation passes with
  `basis.not_actionable: 0`. The scripted subject received one call in total.
- **Fails if:** The new Result does not resolve the old one; the second evaluation
  fails; the subject is called again; or the implementation offers no way to request a
  re-assessment (13.1).

### CT-DEC-015 — A missed Seeded Control invalidates its defect class without changing any Result

- **Capability:** `seeded_controls`
- **Requirement:** Volume I, Chapter 6, Quality Gates: "A Quality Gate MUST NOT pass on
  any aggregate to which an Oracle contributed Results sharing a missed Seeded Control's
  defect class (Volume VIII) in that run"; Appendix B §B.3, Invalidation is derived: "A
  missed Seeded Control MUST NOT change any recorded Result"; Appendix C §C.3, Seeded
  Control Reporting.
- **Method:** Automated
- **Fixture:** F-SEED with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; retrieve the Execution records and every Result;
  evaluate the Gates.
- **Expected:**
  - `seeded_control_results` has one entry for `s-control`: `defect_class:
    greeting-missing`, `outcome: missed`, `confirmed_by: construction`,
    `invalidation_scope: defect_class`, `reason: null`.
  - The scripted subject received exactly one call (for `s-greeting`; `s-control` uses
    its fixed Evidence).
  - `s-greeting`'s Expectation either has a recorded Result with `verdict: pass` and
    `disposition: actionable` whose `invalidated_by` lists `{ scenario: s-control,
    defect_class: greeting-missing }`, or, if the Judge was no longer invoked for it, a
    Result with `disposition: not_assessed` and `verdict: null`.
  - `semantic-gate` fails, with `seeded_control_miss` in `reasons`. Its `basis` counts
    no Result of `s-control`.
  - `functional-gate` passes: the schema Constraint's Oracle missed no control.
- **Fails if:** `semantic-gate` passes; `reasons` lacks `seeded_control_miss`; the
  invalidated Result's recorded `verdict` or `disposition` was changed; an `s-control`
  Result is counted in any `basis` field; or `functional-gate` fails.

### CT-DEC-016 — A caught Seeded Control is excluded from Aggregation and invalidates nothing

- **Capability:** `seeded_controls`
- **Requirement:** Volume VIII, Seeded Controls: "Seeded Control Results themselves MUST
  be excluded from Aggregation."
- **Method:** Automated
- **Fixture:** F-SEED with `semantic-gate`; scripted Judge `J-CATCH`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `s-control`'s entry has `outcome: caught` and `invalidation_scope:
  none`. `semantic-gate` passes with `basis.results: 1` and `basis.scenarios: 1`.
- **Fails if:** The failing `s-control` Result is counted, so that `semantic-gate`
  fails or `basis` counts two Results or two Scenarios.

### CT-DEC-017 — Full-run invalidation reaches every Gate of the run

- **Capability:** `seeded_controls`
- **Requirement:** Volume I, Chapter 6, Quality Gates: full-run invalidation "widens the
  rule, it never lifts it"; Appendix C §C.3: "Under `full_run`, no Result of that run
  counts as `actionable` for any Quality Gate, whatever its defect class"; Appendix A
  §A.12, GateResult `value`: "Never bare `null`."
- **Method:** Automated
- **Fixture:** F-SEED with `semantic-gate`; add `execution: { on_seeded_control_miss:
  halt_run }` to the Project; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `s-control`'s entry has `outcome: missed`, `invalidation_scope:
  full_run`, and a non-empty `reason`. Both `functional-gate` and `semantic-gate` fail,
  each with `seeded_control_miss` in `reasons`, and each `value` is a number or
  `"not_computed"`.
- **Fails if:** Either Gate passes; either lacks `seeded_control_miss`; `reason` is
  empty or `null`; or a `value` is bare `null`.

### CT-DEC-018 — An Oracle that has not been requalified cannot resolve an invalidated Result

- **Capability:** `seeded_controls`
- **Requirement:** Volume I, Chapter 6, Result Resolution: a requalified Oracle may
  resolve "only once the Oracle has been requalified for every defect class whose miss
  reached that Result"; Volume VIII, Requalification.
- **Method:** Automated
- **Fixture:** F-SEED-MISSED (2.7). The Judge configuration is unchanged and has caught
  no fresh control of `greeting-missing`.
- **Action:** Request that the same Judge configuration assess `s-greeting`'s stored
  Evidence again. Evaluate the Gates.
- **Expected:** The request is rejected, or produces a Result that does not resolve the
  invalidated or `not_assessed` one. `semantic-gate` still fails with
  `seeded_control_miss`.
- **Fails if:** A Result from that Judge configuration resolves the earlier Result;
  `semantic-gate` passes; or the implementation offers no way to request a
  re-assessment (13.1).

### CT-DEC-019 — A Validator-enforced Safety failure vetoes its aggregate

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Aggregation Model: "a Validator-enforced Safety
  failure acts as a hard veto on the aggregate regardless of how well everything else
  scored"; Appendix A §A.5, Constraint `veto`.
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`; scripted subject `SR-ECHO`. Add to the
  Project:
  ```yaml
  contracts:
    - constraints:
        - validator: forbidden-content
          target: response
          expected:
            patterns:
              - regex: "Three"
          veto: true
  ```
  and add to its `quality_gates`:
  ```yaml
  - name: safety-gate
    aggregate: safety
    threshold: 0.5
    on_failure: block_release
  ```
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** The forbidden-content Constraint passes for `s-1` and `s-2` and fails for
  `s-3`. `safety-gate` fails, although two of three Results passed and its threshold is
  0.5.
- **Fails if:** `safety-gate` passes.

### CT-DEC-020 — A weighted failure counts for more than an unweighted one

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Aggregation Model: "A failure on a Scenario marked
  high-stakes MUST count for more than an equally-sized failure on a low-stakes one";
  Appendix A §A.5, Policies `weight`.
- **Method:** Automated
- **Fixture:** F-MULTI with `semantic-gate`; scripted subject `SR-ECHO`. In `s-1`'s
  `contract`, add `policies: { weight: 3.0 }`; in `s-2`'s and `s-3`'s, add
  `policies: { weight: 1.0 }`.
- **Action:** Run A: execute `cts-suite` with scripted Judge
  `J-MAP(J-FAIL-90, J-PASS-90, J-PASS-90)`; evaluate the Gates. Run B: execute it with
  `J-MAP(J-PASS-90, J-FAIL-90, J-PASS-90)`; evaluate the Gates.
- **Expected:** `semantic-gate` fails in both runs, and its `value` in Run A is lower
  than in Run B.
- **Fails if:** The two values are equal, or Run A's is higher.

### CT-DEC-021 — A statistical interval is not labelled Confidence

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Aggregate Basis: "An implementation MAY report
  such an interval alongside an aggregate; it MUST NOT label it Confidence."
- **Method:** Inspection
- **Fixture:** Two variants: CT-DEC-002's configuration and CT-DEC-008's.
- **Action:** In each, execute `cts-suite` and evaluate the Gates. Review how every
  aggregate is presented in the GateResults and in any Report or Dashboard the
  implementation produces for those runs, and any interval, margin of error, or similar
  figure reported with it.
- **Expected:** Where an interval appears, it is not called Confidence. The word
  Confidence is used only for an Oracle's certainty in one verdict.
- **Fails if:** Any interval or aggregate-level figure is labelled Confidence.

### CT-DEC-022 — Results from a changed Environment are stale

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: "A Gate MUST NOT pass on an
  aggregate that includes a stale Result, and records the reason as `stale_results`";
  Appendix B §B.3, Stale Results.
- **Method:** Automated, Harness
- **Fixture:** F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite` (batch 1); evaluate the Gates. As a governed change
  (Section 14.1), set `cts-env`'s `prompt_version` to `cts-prompt@2`. Evaluate the Gates
  again for batch 1. Then execute `cts-suite` again (batch 2) and evaluate the Gates for
  it.
- **Expected:** The first evaluation passes. The second captures a new `snapshot_id`,
  and both `functional-gate` and `semantic-gate` fail with `stale_results` in `reasons`;
  the stale Results are counted in `basis.not_actionable`, not in `basis.results`. The
  evaluation for batch 2 passes.
- **Fails if:** Either Gate passes in the second evaluation; `reasons` lacks
  `stale_results`; or the evaluation for batch 2 fails.

### CT-DEC-023 — Only Results for a changed clause are stale

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Quality Gates: a Result is stale when "its clause
  differs from that clause in the Snapshot. A clause is matched by its `id` ... A clause
  without an `id` cannot be matched across versions, so any change in its Contract makes
  its Results stale"; Appendix B §B.3, Stale Results.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`.
  (a) The schema Constraint has `id: schema-1` and the Expectation `id: greets`. (b) No
  `id`s.
- **Action:** For each: execute `cts-suite`; evaluate the Gates. As a governed change,
  set the Expectation's `confidence_threshold` in `s-greeting`'s inline Contract to
  `0.85`. Evaluate the Gates again for the same batch.
- **Expected:** (a) In the second evaluation, `semantic-gate` fails with `stale_results`
  and `functional-gate` passes, its clause unchanged. (b) Both fail with
  `stale_results`.
- **Fails if:** (a) `semantic-gate` passes, or `functional-gate` fails; (b) either Gate
  passes, or either lacks `stale_results`.
