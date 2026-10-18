# 26. Capabilities: SDKs and CLI, Reference UI, Test Types

Each test applies only where the implementation claims the capability it names (§10).

### CT-SDK-001 — A CLI command is a REST API call

- **Capability:** `cli`
- **Requirement:** Volume XIV, CLI: "A CLI command MUST correspond to a REST API call it
  makes on the caller's behalf, not a separate implementation of the operation it
  names"; Appendix C, introduction: the CLI and the SDKs "are thin wrappers over this API
  and MUST NOT independently reimplement logic" (the CLI's half of that requirement;
  CT-SDK-002 checks the SDKs').
- **Method:** Harness, Inspection
- **Fixture:** F-BASE. The tester routes the CLI's traffic through a recording proxy.
- **Action:** With the CLI, load F-BASE, execute `cts-suite`, and evaluate the Gates.
  Then list the CLI's documented commands and the REST operations of Appendix C.
- **Expected:** Each of the three commands appears in the proxy log as the matching
  Appendix C operation, and every documented CLI command maps to a REST operation.
- **Fails if:** A command acts without the matching REST call, or a command has no REST
  counterpart.

### CT-SDK-002 — An SDK behaves as the REST API does

- **Capability:** `sdk:<language>`
- **Requirement:** Appendix C, introduction: the SDKs "are thin wrappers over this API
  and MUST NOT independently reimplement logic" (the SDKs' half of that requirement;
  CT-SDK-001 checks the CLI's).
- **Method:** Automated
- **Fixture:** The configurations of CT-CFG-002, CT-DEC-006, and CT-REL-002.
- **Action:** Carry out each of those three tests once through the REST API and once
  through the SDK of each claimed language, each run in a Project of its own (1.6).
- **Expected:** Each test reaches the same outcome on every surface. Where the REST API
  returns an error, the SDK reports the same error in substance: the same HTTP status
  or error code, and the same field or entity named, however the SDK represents it, as
  an exception or otherwise. The Results and GateResults recorded agree in every field
  but identifiers, `execution`, references to their own Execution, and times. Message
  text, exception classes, and stack traces are not compared.
- **Fails if:** An outcome differs; an error differs in status, code, or what it names;
  an SDK succeeds where the API returns an error, or the reverse; or a compared field of
  a recorded Result or GateResult differs.

### CT-RUI-001 — A Scenario authored visually is the same as one written in YAML

- **Capability:** `reference_ui`
- **Requirement:** Volume XV, Visual Test Designer: "a Scenario authored visually and one
  authored by hand in YAML MUST be indistinguishable once saved."
- **Method:** Automated
- **Fixture:** F-BASE's `s-greeting`.
- **Action:** Author `s-greeting` in the Visual Test Designer, as `s-visual`, with the
  same content. Retrieve both Scenarios through the REST API.
- **Expected:** Apart from their names, the two are identical.
- **Fails if:** They differ in any other field or in structure.

### CT-RUI-002 — The Validator Designer does not let a Validator carry Confidence or call a model

- **Capability:** `reference_ui`
- **Requirement:** Volume XV, Validator Designer: "a Validator configured here MUST be
  deterministic and MUST NOT carry a Confidence value"; a check that calls a model "is
  configuring a Judge ... and the Validator Designer MUST surface that distinction."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** In the Validator Designer, try to give a Validator a Confidence value or
  threshold, and try to configure a Validator whose check calls a model.
- **Expected:** The first cannot be done. The second is refused or redirected to Judge
  configuration, with the reason shown.
- **Fails if:** Either is saved as a Validator.

### CT-RUI-003 — The UI asks which purpose a Multi Judge panel serves

- **Capability:** `reference_ui` together with `multi_judge`
- **Requirement:** Volume XV, Judge Configuration: it "MUST require an explicit choice of
  which purpose it serves — independence or stability — rather than default silently to
  one."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** Configure a second Judge on an Expectation through the UI without
  choosing a purpose, and try to save.
- **Expected:** The UI does not save until a purpose is chosen.
- **Fails if:** It saves with a purpose it chose itself.

### CT-RUI-004 — A Report and a Dashboard cannot be mistaken for each other

- **Capability:** `reference_ui`
- **Requirement:** Volume XV, Reporting UI: it "MUST visually distinguish a Report's
  frozen, point-in-time state from a Dashboard's live, continuously-updating one."
- **Method:** Inspection
- **Fixture:** F-SIGNALS (2.7), and a Dashboard over the same Suite.
- **Action:** Open the Report and the Dashboard in the UI.
- **Expected:** Each states what it is; the Report shows the moment it was frozen.
- **Fails if:** A viewer could take either for the other from what the UI shows.

### CT-TTP-001 — A Regression Suite surfaces drift with nothing AQEF-visible changed

- **Capability:** `test_type:regression`
- **Requirement:** Volume X, Model Drift: "a Regression Suite (Volume IX) MUST be able to
  surface Model Drift even when nothing AQEF-visible changed."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`, plus a Regression Gate:
  ```yaml
  - name: regression-gate
    aggregate: regression
    compare_against: latest_approved
    threshold: 0
    on_failure: block_release
  ```
  Scripted Judge `J-CATCH` (Section 13.1).
- **Action:** Execute `cts-suite` with scripted subject `SR-OK`; as `P-APPROVER`,
  designate the Execution as a Baseline. Without changing any configuration, switch the
  scripted subject to `SR-BYE` (Section 22); execute again; evaluate the Gates.
- **Expected:** `regression-gate` fails, and the implementation's records show that no
  Environment, Contract, or Dataset changed between the two Executions.
- **Fails if:** `regression-gate` passes.

### CT-TTP-002 — An agent's Baseline comparison judges the trajectory as a whole

- **Capability:** `test_type:agent` together with `action_boundary`
- **Requirement:** Volume I, Chapter 7, AI Agent: a Baseline comparison "MUST therefore
  be capable of judging the outcome and the reasoning quality of a trajectory as a
  whole, not require step-for-step identity with the Baseline's own path."
- **Method:** Automated, Inspection
- **Fixture:** F-ACT (Section 23) with a second stub entry `https://cts-stub2.example/*`
  and a Regression Gate as in CT-TTP-001. Two scripted trajectories reaching the same
  final Response, `"Done."`: (a) calls `cts-stub.example`, then `cts-stub2.example`;
  (b) the same two calls in the opposite order.
- **Action:** Execute with trajectory (a); designate it as a Baseline. Execute with
  trajectory (b); evaluate the Gates. Review how the comparison was made.
- **Expected:** The comparison does not report a regression because the order of steps
  differs; the reviewer records what the comparison judged.
- **Fails if:** A regression is reported solely because (b)'s steps are not identical
  to (a)'s.
