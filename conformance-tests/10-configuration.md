# 10. Configuration and Definition

Tests in this section load a configuration and observe whether it is accepted. None of
them needs an Execution.

### CT-CFG-001 — A complete, valid configuration is accepted

- **Capability:** core
- **Requirement:** Appendix A, introduction: "A conformant implementation MUST accept
  configurations expressible within this specification."
- **Method:** Automated
- **Fixture:** F-BASE, unchanged.
- **Action:** Load the configuration.
- **Expected:** Loaded without error.
- **Fails if:** Rejected, or loaded with any field of F-BASE ignored or altered.

### CT-CFG-002 — A Scenario with no effective Contract is rejected

- **Capability:** core
- **Requirement:** Appendix B §B.3, Effective Contract: the composition of Project,
  Suite, and Scenario Contracts "MUST contain at least one clause"; Appendix A §A.4,
  `contract`.
- **Method:** Automated
- **Fixture:** F-BASE; in `suites[0].scenarios[0]`, remove `contract`. No `contracts` at
  Project or Suite level.
- **Action:** Load the configuration.
- **Expected:** Rejected; the error identifies `s-greeting`.
- **Fails if:** Loaded, or `s-greeting` can be executed.

### CT-CFG-003 — A Contract with no clauses is rejected

- **Capability:** core
- **Requirement:** Appendix B §B.2, Contract: "at least one of `constraints` or
  `expectations` MUST be non-empty"; Appendix A §A.5.
- **Method:** Automated
- **Fixture:** F-BASE; in the Scenario's `contract`, set `constraints: []` and
  `expectations: []`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded.

### CT-CFG-004 — An Expectation must bind exactly one Oracle

- **Capability:** core
- **Requirement:** Appendix B §B.2, Expectation: "Exactly one of `judge`,
  `multi_judge`, or `human_reviewer` MUST be present"; Volume VII, Contract Language.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE. (a) In the Expectation, remove `judge`. (b) In
  the Expectation, add `human_reviewer: { role: reviewer }` alongside `judge`.
- **Action:** Load each variant.
- **Expected:** Both rejected.
- **Fails if:** Either is loaded.

### CT-CFG-005 — A Judge-bound Expectation needs a Confidence threshold

- **Capability:** core
- **Requirement:** Appendix B §B.3, Expectation Oracle exclusivity:
  "`confidence_threshold` is REQUIRED" for `judge` and `multi_judge`.
- **Method:** Automated
- **Fixture:** F-BASE; in the Expectation, remove `confidence_threshold`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, or loaded with a default threshold supplied silently.

### CT-CFG-006 — A Judge identical to the subject is rejected

- **Capability:** core
- **Requirement:** Volume I, Chapter 3, Independent Oracles: "An Oracle MUST NOT be the
  same system, weights, or decision process as the AI system it evaluates"; Appendix B
  §B.3, Independent Oracle — identity.
- **Method:** Automated
- **Fixture:** F-BASE; set the Judge's `model` to `cts-scripted-subject@1`.
- **Action:** Load the configuration.
- **Expected:** Rejected; the error names the identity of Judge and subject.
- **Fails if:** Loaded.

### CT-CFG-007 — A composition conflict is surfaced, not resolved silently

- **Capability:** core
- **Requirement:** Volume VII, Contract Composition: "Composition MUST surface the
  conflict explicitly rather than silently resolve it"; Appendix B §B.3, Effective
  Contract: "A lower level MUST NOT remove or weaken a clause contributed by a higher
  one. Two clauses are the same clause only when they declare the same `id`; the same
  `id` with differing content is a composition conflict."
- **Method:** Automated
- **Fixture:** F-BASE, with `id: greets` added to the Scenario's Expectation, plus a
  Project-level Contract carrying an Expectation with the same `id` and
  `confidence_threshold: 0.9`:
  ```yaml
  project:
    contracts:
      - expectations:
          - id: greets
            criteria: "The response greets the user."
            judge:
              model: cts-scripted-judge@1
              confidence_source: self_rating
            confidence_threshold: 0.9
  ```
  The Scenario keeps `confidence_threshold: 0.8`.
- **Action:** Load the configuration; if it loads, attempt to execute `cts-suite`.
- **Expected:** The conflict between 0.9 and 0.8 is reported, naming the clause and both
  values. Either the configuration is rejected, or `s-greeting` is not assessed under
  that clause until the conflict is resolved.
- **Fails if:** `s-greeting` is assessed with either threshold without the conflict
  having been reported.

### CT-CFG-008 — A Prompt that references an unsupplied Variable is rejected

- **Capability:** core
- **Requirement:** Appendix B §B.3, Prompt presence: "Every Variable a
  `prompt.template` references MUST be supplied"; Appendix A §A.4, PromptDef.
- **Method:** Automated
- **Fixture:** F-BASE; set the template to `"{{query}} {{name}}"`. `name` is not in
  `variables`.
- **Action:** Load the configuration, or, if the implementation checks templates only
  when an Execution is requested, request one.
- **Expected:** Rejected before any call reaches the scripted subject.
- **Fails if:** The subject receives a call, or receives a Prompt with the placeholder
  unfilled or filled with an empty value.

### CT-CFG-009 — Quality Gate names are unique across a Project and its Suites

- **Capability:** core
- **Requirement:** Appendix B §B.3, Gate name uniqueness; Appendix A §A.3,
  `quality_gates`.
- **Method:** Automated
- **Fixture:** F-BASE; add to `suites[0]` a `quality_gates` list with a Gate named
  `functional-gate` (same name as the Project's) and `threshold: 0.5`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, whichever of the two Gates the implementation would use.

### CT-CFG-010 — Retry may be configured only for infrastructure failure

- **Capability:** core
- **Requirement:** Appendix B §B.2, RetryConfig: `on` is `infrastructure_failure`; "A
  schema MUST reject any other value"; Appendix B §B.3, Retry scope.
- **Method:** Automated
- **Fixture:** F-BASE; add `execution: { retry: { max_attempts: 2, on: result_failure } }`
  to the Project.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded.

### CT-CFG-011 — A Scenario cannot take both a Dataset and Variables

- **Capability:** core
- **Requirement:** Appendix A §A.4: a Scenario "MUST NOT specify both" `dataset` and
  `variables`.
- **Method:** Automated
- **Fixture:** F-BASE, plus a Static Dataset in the Project's `datasets`:
  ```yaml
  project:
    datasets:
      - name: ds-1
        version: "1.0.0"
        source: static
        rows:
          - id: r1
            variables:
              query: "Hi"
  ```
  In the Scenario, add `dataset: ds-1@1.0.0` and keep `variables`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, whichever source the implementation would use.

### CT-CFG-012 — The same clause contributed twice, identically, is one clause

- **Capability:** core
- **Requirement:** Appendix A §A.5, `id`: "Two contributed clauses are the same clause
  only when they declare the same `id`: identical content is one clause"; Volume VII,
  Contract Composition.
- **Method:** Automated, Harness
- **Fixture:** As CT-CFG-007, with the Project-level Expectation's
  `confidence_threshold` set to `0.8`, so that both are identical.
- **Action:** Load the configuration; execute `cts-suite`.
- **Expected:** Loaded with no conflict reported. `s-greeting` has exactly one
  Expectation Result, and the scripted Judge receives one call.
- **Fails if:** A conflict is reported, or two Expectation Results are produced.

### CT-CFG-013 — Clauses without an `id` are never the same clause

- **Capability:** core
- **Requirement:** Appendix A §A.5, `id`: "A clause without `id` is never the same clause
  as another, and simply applies"; Volume VII, Contract Composition.
- **Method:** Automated, Harness
- **Fixture:** As CT-CFG-007, with `id` removed from both Expectations (thresholds stay
  `0.9` and `0.8`).
- **Action:** Load the configuration; execute `cts-suite` with scripted Judge
  `J-PASS-90`.
- **Expected:** Loaded with no conflict reported. `s-greeting` has two Expectation
  Results, both `actionable` (0.9 meets both thresholds), and the scripted Judge
  receives two calls.
- **Fails if:** A conflict is reported, or the two clauses are merged into one.

### CT-CFG-014 — A Dataset reference without a version is rejected

- **Capability:** core
- **Requirement:** Appendix A §A.4, `dataset`: "The version MUST be given"; Appendix B
  §B.3, Dataset reference.
- **Method:** Automated
- **Fixture:** As CT-CFG-011, with `variables` removed from the Scenario and `dataset:
  ds-1` (no version).
- **Action:** Load the configuration.
- **Expected:** Rejected. The same configuration with `dataset: ds-1@1.0.0` is loaded.
- **Fails if:** The configuration without a version is loaded, or the one with it is
  rejected.

### CT-CFG-015 — A clause `id` is unique within its Contract

- **Capability:** core
- **Requirement:** Appendix B §B.3, Clause identity: "A clause `id` MUST be unique within
  the Contract that declares it."
- **Method:** Automated
- **Fixture:** F-BASE; give the schema Constraint `id: c1`, and add a second Constraint
  to the same Contract with the same `id`:
  ```yaml
  - id: c1
    validator: forbidden-content
    target: response
    expected:
      patterns:
        - regex: "error"
  ```
- **Action:** Load the configuration.
- **Expected:** Rejected; the error names `c1`.
- **Fails if:** Loaded.

### CT-CFG-016 — A Custom Validator's clause must declare its dimension

- **Capability:** core
- **Requirement:** Appendix B §B.3, Clause dimension: "A Constraint bound to a Custom
  Validator MUST declare `dimension`"; Appendix A §A.5.
- **Method:** Automated
- **Fixture:** F-BASE; add a Constraint `validator: cts-len` (Section 2.5),
  `target: response`, `expected: {}`, with no `dimension`. Setup check: `cts-len` is
  registered (2.5). If the implementation offers no Custom Validators, the outcome is
  `NOT_RUN`, with that reason.
- **Action:** Load the configuration. Then add `dimension: functional` to that
  Constraint and load it again.
- **Expected:** The first load is rejected; the second is accepted.
- **Fails if:** The first is loaded, or the second is rejected.

### CT-CFG-017 — A Dataset without a version is rejected

- **Capability:** core
- **Requirement:** Volume IV, Versioning: "Every Dataset, regardless of source, MUST be
  versioned"; Appendix A §A.8, `version`; Appendix C §C.3: "Create a Dataset (version
  MUST be specified)."
- **Method:** Automated
- **Fixture:** As CT-CFG-011, with `variables` removed from the Scenario, `dataset:
  ds-1@1.0.0` kept, and `version` removed from `ds-1`.
- **Action:** (a) Load the configuration. (b) Separately, `POST
  /projects/cts-base/datasets` with the same Dataset and no `version`.
- **Expected:** Both rejected.
- **Fails if:** Either is accepted.

### CT-CFG-018 — One name and version always means the same rows

- **Capability:** core
- **Requirement:** Appendix B §B.3, Dataset version immutability: "Two configurations
  referencing the same Dataset name + version MUST resolve to identical rows."
- **Method:** Automated
- **Fixture:** CT-CFG-011's `ds-1` at version `1.0.0`, registered with the
  implementation.
- **Action:** Register, or load in a second configuration, a Dataset `ds-1` at version
  `1.0.0` whose only row has `query: "Bye"`. Then retrieve the rows of `ds-1@1.0.0`.
- **Expected:** The second definition is rejected. The rows of `ds-1@1.0.0` are
  unchanged: one row, `query: "Hi"`.
- **Fails if:** The second definition is accepted, or the rows changed.

### CT-CFG-019 — A Constraint names a Validator the implementation has

- **Capability:** core
- **Requirement:** Volume VII, Constraints: "A Constraint MUST name the Validator,
  built-in or custom (Volume V), it binds to"; Appendix A §A.5, `validator`.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE. (a) Remove `validator` from the schema
  Constraint. (b) Set it to `cts-no-such-validator`, which is not registered.
- **Action:** Load each variant.
- **Expected:** Both rejected.
- **Fails if:** Either is loaded.

### CT-CFG-020 — A Project needs at least one Environment

- **Capability:** core
- **Requirement:** Appendix A §A.1, `environments`: "At least one Environment MUST be
  defined."
- **Method:** Automated
- **Fixture:** F-BASE with `environments: []`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded.

### CT-CFG-021 — A Suite needs at least one Scenario

- **Capability:** core
- **Requirement:** Appendix A §A.3, `scenarios`: "At least one Scenario MUST be
  present."
- **Method:** Automated
- **Fixture:** F-BASE with `suites[0].scenarios: []`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded.

### CT-CFG-022 — A Scenario needs a Prompt with a template

- **Capability:** core
- **Requirement:** Appendix B §B.3, Prompt presence: "A Scenario MUST carry `prompt`
  unless its `dataset` is a `production_replay` Dataset or it carries `evidence`";
  Appendix A §A.4, PromptDef `template`.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE. (a) Remove `prompt` from `s-greeting`. (b) Keep
  `prompt` but remove its `template`.
- **Action:** Load each variant.
- **Expected:** Both rejected.
- **Fails if:** Either is loaded.

### CT-CFG-023 — A Reusable Contract needs a name

- **Capability:** core
- **Requirement:** Appendix A §A.5, `name`: "MUST (if reusable)."
- **Method:** Automated
- **Fixture:** None beyond F-BASE.
- **Action:** `POST /projects/cts-base/contracts` as `P-APPROVER` (Section 14.1) with
  F-BASE's Contract and no `name`.
- **Expected:** Rejected.
- **Fails if:** Accepted.

### CT-CFG-024 — A minimum basis must state what it counts

- **Capability:** core
- **Requirement:** Appendix A §A.10, MinBasis: "At least one of the two MUST be present";
  Appendix B §B.2, MinBasis.
- **Method:** Automated
- **Fixture:** F-BASE; give `functional-gate` `min_basis: {}`.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, or loaded with a default minimum supplied silently.

### CT-CFG-025 — A configuration missing a required field is rejected

- **Capability:** core; case `CT-CFG-025.25`: `seeded_controls`
- **Requirement:** Appendix A, every field marked MUST in the tables of §A.1 to §A.10
  that the cases below name; Appendix A, introduction: "A conformant implementation MUST
  accept configurations expressible within this specification", which a configuration
  lacking a required field is not.
- **Method:** Automated
- **Fixture:** Four starting configurations, each a setup check: it must load (for
  F-BASE, CT-CFG-001). If a starting configuration is rejected, the cases that use it are
  `NOT_RUN`, with that reason; the other cases still run.
  - F-BASE.
  - F-RETRY: F-BASE with `execution: { retry: { max_attempts: 2, on:
    infrastructure_failure } }` on the Project.
  - F-DS: CT-CFG-011's configuration with `variables` removed from the Scenario, so that
    `s-greeting` draws on `ds-1@1.0.0`; for case `CT-CFG-025.24`, `ds-1` also given
    `mechanisms: [ { type: edge_cases } ]`.
  - F-SEED (Section 13.1).
- **Action:** For each case, remove the one field named from its starting configuration,
  change nothing else, and load the result. Each case runs in a Project of its own and
  has its own outcome (1.2, Cases).

| Case | Inventory row | Start | Field removed |
|---|---|---|---|
| `CT-CFG-025.01` | R-0129 | F-BASE | `project.name` |
| `CT-CFG-025.02` | R-0137 | F-BASE | `environments[0].name` |
| `CT-CFG-025.03` | R-0138 | F-BASE | `environments[0].model_version` |
| `CT-CFG-025.04` | R-0139 | F-BASE | `environments[0].prompt_version` |
| `CT-CFG-025.05` | R-0140 | F-BASE | `environments[0].tool_configuration` (the key itself; with the value `null`, F-BASE loads) |
| `CT-CFG-025.06` | R-0142 | F-BASE | `environments[0].infra_target` |
| `CT-CFG-025.07` | R-0151 | F-BASE | `suites[0].name` |
| `CT-CFG-025.08` | R-0155 | F-BASE | `suites[0].scenarios[0].name` |
| `CT-CFG-025.09` | R-0175 | F-BASE | the schema Constraint's `target` |
| `CT-CFG-025.10` | R-0176 | F-BASE | the schema Constraint's `expected` |
| `CT-CFG-025.11` | R-0177 | F-BASE | the Expectation's `criteria` |
| `CT-CFG-025.12` | R-0185 | F-BASE | the Expectation's `judge.model` |
| `CT-CFG-025.13` | R-0187 | F-BASE | the Expectation's `judge.confidence_source` |
| `CT-CFG-025.14` | R-0216 | F-BASE | `quality_gates[0].name` |
| `CT-CFG-025.15` | R-0217 | F-BASE | `quality_gates[0].aggregate` |
| `CT-CFG-025.16` | R-0218 | F-BASE | `quality_gates[0].threshold` |
| `CT-CFG-025.17` | R-0219 | F-BASE | `quality_gates[0].on_failure` |
| `CT-CFG-025.18` | R-0213 | F-RETRY | `execution.retry.max_attempts` |
| `CT-CFG-025.19` | R-0195 | F-DS | `datasets[0].name` |
| `CT-CFG-025.20` | R-0198 | F-DS | `datasets[0].source` |
| `CT-CFG-025.21` | R-0199 | F-DS | `datasets[0].rows` (the Dataset is `static`) |
| `CT-CFG-025.22` | R-0202 | F-DS | `datasets[0].rows[0].id` |
| `CT-CFG-025.23` | R-0203 | F-DS | `datasets[0].rows[0].variables` |
| `CT-CFG-025.24` | R-0211 | F-DS | `datasets[0].mechanisms[0].type` |
| `CT-CFG-025.25` | R-0132 | F-SEED | `defect_classes[0].name` |

- **Expected:** In each case, the configuration is rejected, with an error that
  identifies what was wrong (1.5): the missing field, or what its absence left
  unresolved. `CT-CFG-025.25` is `NOT_APPLICABLE` unless `seeded_controls` is claimed.
  (The other branch of `CT-CFG-025.21`, a Dataset that is not `static` loading without
  `rows`, belongs to `dataset:<source>`, Section 24.)
- **Fails if:** A case is `FAIL` when its configuration loads, including with a default
  supplied silently for the missing field, or when it is rejected with no error that
  identifies what was wrong. The test's own outcome summarizes its cases (1.2).
