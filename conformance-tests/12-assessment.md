# 12. Assessment

Tests in this section observe the Results Oracles produce for one Execution, and the
calls the scripted Judge receives.

### CT-ASM-001 — A failing Validator short-circuits before any Judge

- **Capability:** core
- **Requirement:** Volume I, Chapter 3, Validation before Evaluation: "Validators MUST
  run before Judges for a given Execution"; Volume V, Execution Order.
- **Method:** Automated, Harness
- **Fixture:** F-BASE; scripted subject `SR-EMPTY`.
- **Action:** Execute `cts-suite`.
- **Expected:** The schema Constraint's Result has `verdict: fail`. The scripted Judge
  receives no call for this Execution.
- **Fails if:** The scripted Judge receives any call for this Execution.

### CT-ASM-002 — A Judge is invoked only after Validation has passed

- **Capability:** core
- **Requirement:** as CT-ASM-001; Volume I, Chapter 5, Validation: Validation "MUST do
  so before Evaluation runs."
- **Method:** Automated, Harness
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite`; retrieve both Results and compare their
  `recorded_at` (Appendix C §C.7).
- **Expected:** The scripted Judge receives exactly one call. The schema Constraint's
  Result has an earlier `recorded_at` than the Expectation's.
- **Fails if:** The Judge is called more than once, or the Validator Result's
  `recorded_at` is not earlier than the Judge Result's.

### CT-ASM-003 — A Validator Result declares Confidence inapplicable

- **Capability:** core
- **Requirement:** Volume I, Chapter 3, Everything has Confidence: a Validator's Result
  "MUST instead explicitly declare that Confidence does not apply"; Volume V, Validator
  Architecture; Appendix C §C.7.
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite`; retrieve the schema Constraint's Result.
- **Expected:** `oracle_type: validator`; `confidence: "not_applicable"`;
  `verdict: pass`; `disposition: actionable`; `oracle` names the schema Validator and
  its version.
- **Fails if:** `confidence` is a number, is absent, or is bare `null`; or `oracle` is
  absent.

### CT-ASM-004 — A Judge Result carries the Judge's Confidence

- **Capability:** core
- **Requirement:** §8, Judge: "A Judge's Result MUST carry a Confidence value"; Volume
  VI, Judge Architecture.
- **Method:** Automated
- **Fixture:** F-BASE; scripted Judge `J-PASS-90`.
- **Action:** Execute `cts-suite`; retrieve the Expectation's Result.
- **Expected:** `oracle_type: judge`; `verdict: pass`; `confidence: 0.9`;
  `disposition: actionable` (0.9 meets the 0.8 threshold).
- **Fails if:** `confidence` is not `0.9`, or `disposition` is anything but
  `actionable`.

### CT-ASM-005 — Below the threshold, a Result is inconclusive and keeps its verdict

- **Capability:** core
- **Requirement:** Volume I, Chapter 6, Confidence Model: below the threshold, "a
  Result's disposition is `inconclusive` — it MUST NOT be silently counted as an
  ordinary pass or fail."
- **Method:** Automated
- **Fixture:** F-BASE; scripted Judge `J-PASS-60`.
- **Action:** Execute `cts-suite`; retrieve the Expectation's Result.
- **Expected:** `verdict: pass`; `confidence: 0.6`; `disposition: inconclusive`.
- **Fails if:** `disposition` is `actionable`, or the verdict is changed or dropped.
  (That an `inconclusive` Result is not counted is checked at the Gate, CT-DEC-005.)

### CT-ASM-006 — Every Result has the required shape

- **Capability:** core
- **Requirement:** Appendix C §C.7, Result Response Shape; Appendix B §B.3, Result
  disposition validity: "`verdict` MUST be `null` when `disposition` is
  `awaiting_review`, `oracle_unavailable`, or `not_assessed`, and MUST be `pass` or
  `fail` otherwise. `confidence` MUST NOT be bare `null` under any disposition."
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite` four times, with scripted Judge `J-PASS-90`,
  `J-PASS-60`, `J-FAIL-90`, and `J-DOWN` in turn; retrieve every Result.
- **Expected:** Every Result has `id`, `execution`, `clause`, `oracle_type`, `oracle`,
  `verdict`, `confidence`, `disposition`, `supporting_evidence`, and `recorded_at`, and
  satisfies the rule quoted above.
- **Fails if:** Any Result lacks one of those fields or breaks the rule.

### CT-ASM-007 — An unreachable Judge produces `oracle_unavailable`

- **Capability:** core
- **Requirement:** Volume VI, Human Review: an Oracle that cannot be reached "produces a
  Result with disposition `oracle_unavailable` rather than a low-Confidence verdict";
  Appendix C §C.7.
- **Method:** Automated
- **Fixture:** F-BASE; scripted Judge `J-DOWN`.
- **Action:** Execute `cts-suite`; retrieve the Expectation's Result; count the calls
  the scripted Judge received.
- **Expected:** `disposition: oracle_unavailable`; `verdict: null`;
  `confidence: "not_applicable"`. Its `supporting_evidence` records one attempt for each
  call the scripted Judge received (Volume VI, Human Review).
- **Fails if:** No Result is recorded for the Expectation; it has a verdict; it is
  recorded as `fail` or as a low-Confidence Result; or the attempts recorded do not
  match the calls received.

### CT-ASM-008 — A re-attempt after a transport failure is recorded, not silent

- **Capability:** core
- **Requirement:** Volume VI, Human Review: a call that fails in transport before any
  verdict "MAY be re-attempted within the same assessment ... Every attempt is recorded
  in the Result's `supporting_evidence`"; an Oracle that could not be reached "MUST NOT
  be silently retried until a favorable verdict appears."
- **Method:** Automated, Harness
- **Fixture:** F-BASE; scripted Judge `J-DOWN-THEN-PASS-90`.
- **Action:** Execute `cts-suite`; count the calls the scripted Judge received;
  retrieve every Result for the Expectation.
- **Expected:** One of two outcomes. (a) The implementation does not re-attempt: one
  call, and an `oracle_unavailable` Result. (b) It re-attempts: two calls, and one
  Result with `verdict: pass` whose `supporting_evidence` records both attempts,
  including the failed one.
- **Fails if:** The Judge received more than one call and no Result records the failed
  attempt; or more than one Result was recorded for the Expectation within this
  Execution without `resolves`.

### CT-ASM-009 — A Validator returns the same Result for the same input

- **Capability:** core
- **Requirement:** §8, Validator: "A Validator MUST return the same Result for the same
  input"; Volume V, Validator Architecture.
- **Method:** Automated
- **Fixture:** F-BASE; scripted subject `SR-OK`.
- **Action:** Execute `cts-suite`. If the implementation offers a re-check of a Validator
  on stored Evidence (Volume V, Validator SDK), re-check the schema Constraint on that
  Execution's stored Evidence and compare the re-check's Result with the recorded one.
  Otherwise, execute `cts-suite` a second time, confirm from the two Conversations that
  the Response, the only input the schema Constraint reads, is identical, and compare
  the two schema Constraint Results. The report states which path was taken.
- **Expected:** The two Results have the same `verdict`, `confidence`, `disposition`,
  `clause`, and `oracle`, and the same `supporting_evidence` apart from references to
  their own Execution. `id`, `execution`, and `recorded_at` are not compared.
- **Fails if:** Any compared field differs.

### CT-ASM-010 — Built-in Validators depend only on evidence and configuration

- **Capability:** core
- **Requirement:** Volume V, Validator Architecture: "a Validator's Result MUST depend
  only on its target evidence ... and on the Validator's own versioned configuration —
  not on the clock, a random source, a network call, or any other state."
- **Method:** Declaration
- **Fixture:** None.
- **Action:** Ask the implementation to state, for each built-in Validator it offers,
  what inputs its result depends on.
- **Expected:** For every built-in Validator, the statement names only target evidence
  and versioned configuration.
- **Fails if:** Any statement names, or the reviewer finds, a dependency on the clock,
  randomness, the network, or other mutable state.

### CT-ASM-011 — A Judge receives the Contract's criteria explicitly

- **Capability:** core
- **Requirement:** Volume VI, Judge Architecture: "A Judge's architecture MUST make its
  criteria explicit and inspectable"; Volume VII, Expectations.
- **Method:** Harness
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite`; read the request the scripted Judge received.
- **Expected:** The request contains the Expectation's `criteria` text, `The response
  greets the user.`, and the Response being assessed.
- **Fails if:** The criteria text is absent from what the Judge received.

### CT-ASM-012 — Every Result traces to exactly one Oracle

- **Capability:** core
- **Requirement:** §8, Oracle: "Every Result MUST be traceable to exactly one Oracle";
  Appendix C §C.7, `oracle`.
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite`; retrieve every Result.
- **Expected:** Each Result has exactly one `oracle` and one `oracle_type`, and each
  Result's `oracle` matches the Validator or Judge configured for its `clause`.
- **Fails if:** Any Result names no Oracle, several, or one not configured for its
  clause.

### CT-ASM-014 — A Validator that cannot complete produces `oracle_unavailable` and stops Evaluation

- **Capability:** core
- **Requirement:** Appendix B §B.3, Validator unavailable: "A Validator that cannot
  complete its check MUST produce `oracle_unavailable`, never `fail`, and Validation for
  that Execution has not passed"; Appendix C §C.7, `oracle_unavailable`.
- **Method:** Automated, Harness
- **Fixture:** F-BASE; add to the Contract's `constraints`:
  ```yaml
  - validator: cts-crash
    target: response
    expected: {}
  ```
  `cts-crash` is a Custom Validator (Volume V) that raises an error on every call and
  returns no Result. If the implementation offers no way to define one, the outcome is
  `NOT_RUN`, with that reason. No built-in Validator can be made to fail on demand
  through configuration alone, so the requirement is then not verified for that
  implementation, and the test report lists it as such (1.7).
- **Action:** Execute `cts-suite`; retrieve every Result.
- **Expected:** The `cts-crash` Result has `oracle_type: validator`,
  `disposition: oracle_unavailable`, `verdict: null`, and `confidence:
  "not_applicable"`. The scripted Judge receives no call for this Execution.
- **Fails if:** The `cts-crash` Result is `fail`, `pass`, or absent; or the scripted
  Judge is called.

### CT-ASM-015 — Once a verdict arrives, it stands

- **Capability:** core
- **Requirement:** Volume VI, Human Review: "Once any response carrying a verdict
  arrives, it stands, whatever it says"; Volume III, Retry.
- **Method:** Automated, Harness
- **Fixture:** F-BASE; scripted Judge `J-FAIL-THEN-PASS-90`.
- **Action:** Execute `cts-suite`; count the calls the scripted Judge received;
  retrieve the Expectation's Result.
- **Expected:** One call. The Result has `verdict: fail`, `confidence: 0.9`, and
  `disposition: actionable`.
- **Fails if:** The Judge receives a second call, or the Result is `pass`.

### CT-ASM-013 — A panel's Result states how many Judges were configured and counted

- **Capability:** `multi_judge`
- **Requirement:** Volume VI, Consensus: "a Result produced by a panel MUST state how many
  Judges were configured and how many were counted"; Appendix B §B.3, Panel reporting.
- **Method:** Automated
- **Fixture:** F-BASE; in the Expectation, replace `judge` with:
  ```yaml
  multi_judge:
    purpose: independence
    judges:
      - model: cts-scripted-judge-a@1
        confidence_source: self_rating
      - model: cts-scripted-judge-b@1
        confidence_source: self_rating
    consensus:
      method: voting
      threshold: unanimous
  ```
  Both identifiers resolve to the scripted Judge, which behaves as `J-PASS-90` for each.
- **Action:** Execute `cts-suite`; retrieve the Expectation's Result.
- **Expected:** `oracle_type: judge`; `verdict: pass`; `panel: { configured: 2,
  counted: 2 }`. The scripted Judge received one call for each identifier.
- **Fails if:** `panel` is absent or its counts differ.

### CT-ASM-016 — A Custom Validator's Result has a Validator's shape

- **Capability:** core
- **Requirement:** Volume V, Custom Validators: "A Custom Validator MUST satisfy the same
  constraints as a built-in one: the same input MUST always produce the same Result, and
  it MUST NOT carry a Confidence value"; Volume V, Validator SDK: a Validator that
  completes its check "MUST return a Result carrying a pass/fail verdict, an explicit
  Confidence-inapplicable declaration, and supporting evidence sufficient for a Report
  ... to explain the verdict without re-running the check."
- **Method:** Automated
- **Fixture:** F-BASE; add a Constraint `validator: cts-len`, `target: response`,
  `expected: {}`, `dimension: functional`.
- **Action:** Execute `cts-suite` twice; retrieve the `cts-len` Results.
- **Expected:** Each has `oracle_type: validator`, `verdict: pass`,
  `confidence: "not_applicable"`, `disposition: actionable`, an `oracle` naming
  `cts-len` and its version, and non-empty `supporting_evidence`. The two Results have
  the same `oracle_type`, `oracle`, `clause`, `verdict`, `confidence`, and
  `disposition`, and the same `supporting_evidence` apart from references to their own
  Execution. `id`, `execution`, and `recorded_at` are not compared.
- **Fails if:** `confidence` is a number; `supporting_evidence` is empty; or any compared
  field differs.

### CT-ASM-017 — A check that calls a model is not accepted as a Validator

- **Capability:** core
- **Requirement:** Volume V, Custom Validators: a check that calls a model to decide
  pass or fail "is structurally a Judge (Volume VI) and MUST be modeled as one."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** Review how the implementation lets a Custom Validator be defined, and
  attempt to register one whose check calls `cts-scripted-judge@1` to decide its
  verdict.
- **Expected:** The implementation prevents it: registration is refused, the Validator's
  runtime gives it no way to reach a model, or the implementation's documentation
  requires such a check to be configured as a Judge and the attempt fails accordingly.
  The reviewer states which.
- **Fails if:** The model-calling check is registered and runs as a Validator, with a
  Validator's short-circuit and no Confidence.

### CT-ASM-018 — A re-check that disagrees is reported as a Validator defect

- **Capability:** core
- **Requirement:** Volume V, Validator SDK: an implementation "MAY re-check a Validator
  at any time by running it again on stored Evidence; a Result that differs from the one
  recorded is a defect in the Validator, not in the subject, and MUST be reported as
  such."
- **Method:** Automated
- **Fixture:** F-BASE; add a Constraint `validator: cts-flaky`, `target: response`,
  `expected: {}`, `dimension: functional`.
- **Action:** Execute `cts-suite`. Ask the implementation to re-check `cts-flaky` on the
  stored Evidence.
- **Expected:** The re-check produces `fail` where the recorded Result was `pass`, and
  the implementation reports this as a defect in `cts-flaky`, not as a failure of the
  subject. The recorded Result is unchanged. If the implementation offers no re-check,
  which the specification permits but does not require, the outcome is
  `NOT_APPLICABLE` (1.2).
- **Fails if:** The disagreement is reported as a subject failure or not reported at
  all; or the recorded Result is changed.

### CT-ASM-019 — A Judge Result over several assertions says it is an aggregate

- **Capability:** core
- **Requirement:** Volume VI, Single Judge: where a criterion spans multiple independent
  assertions, "the Result MUST state that it is an aggregate over multiple assertions
  rather than present its score as an atomic verdict on a single one"; Appendix C §C.7,
  `assertions`.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE. (a) The Expectation's `criteria` set to `"The
  response greets the user, offers help, and names no product."` (b) F-BASE unchanged.
- **Action:** Execute `cts-suite` for each; retrieve the Expectation's Result.
- **Expected:** (a) The Result has `assertions`, an integer greater than 1; the test
  report records its value. (b) The Result has no `assertions`. (How the Judge splits a
  criterion into assertions is the implementation's; the specification requires only
  that a Result over several assertions says so, so any count above one meets it.)
- **Fails if:** (a) has no `assertions`, or a value that is not an integer greater than
  1; or (b) has one.
