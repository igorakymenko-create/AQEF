# 25. Capability: Plugins

Tests in this section apply to an implementation whose Conformance Statement claims
`plugins:<type>` for the type named in each test (§10). For a type it does not claim, the
test is `NOT_APPLICABLE`. The Custom Validators of Section 2.5 are registered here as
Validator Plugins.

**Further plugin.** `cts-probe`: a Validator Plugin that records everything it receives
in the harness log and returns `pass`; when its configuration has `malformed: true`, it
returns a Result with no `verdict` field at all.

### CT-PLG-001 — A Validator Plugin whose output varies is not registered

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI, Validator Plugins: registration "MUST run a candidate
  Validator Plugin against a fixed test input more than once and reject registration if
  its output varies."
- **Method:** Automated, Harness
- **Fixture:** None beyond Section 2.5.
- **Action:** Register `cts-flaky` as a Validator Plugin; then register `cts-len`.
- **Expected:** `cts-flaky` is rejected, the harness log showing it was called more than
  once on the same input. `cts-len` is registered.
- **Fails if:** `cts-flaky` is registered, or `cts-len` is rejected.

### CT-PLG-002 — Registration is not reported as proof of determinism

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI, Validator Plugins: "A successful registration MUST NOT be
  reported as proof of determinism."
- **Method:** Inspection
- **Fixture:** The registration of `cts-len` in CT-PLG-001.
- **Action:** Read what the implementation reports for the registration, in its
  response, records, and documentation.
- **Expected:** It reports a repeatability check that passed, not that the plugin was
  shown to be deterministic.
- **Fails if:** Anything presents the passed check as proof of determinism.

### CT-PLG-003 — A plugin receives the logical inputs, and a malformed Result assesses nothing

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI, Plugin Invocation: "What every implementation MUST hold to
  is the logical shape of one assessment": the Evidence its clause names, the clause's
  content, its versioned configuration, and the Execution and clause identifiers, and
  "A Validator Plugin receives nothing else"; a Result that fails validation is
  `oracle_unavailable`, "never `fail`."
- **Method:** Automated, Harness
- **Fixture:** F-BASE; add two Constraints bound to `cts-probe`, `target: response`,
  `dimension: functional`: the first with `expected: { marker: 1 }`, the second with
  `expected: { marker: 2 }` and configuration `malformed: true`.
- **Action:** Execute `cts-suite`; read what `cts-probe` received; retrieve both
  Results.
- **Expected:** For each call, `cts-probe` received the Response, its clause's
  `expected`, its configuration, and the Execution and clause identifiers, and nothing
  else. The first Result is `pass` with `oracle` naming `cts-probe` and its version. The
  second is `oracle_unavailable`, `verdict: null`, and the scripted Judge receives no
  call.
- **Fails if:** `cts-probe` received anything beyond those inputs; the first Result does
  not name the plugin and version; or the second is recorded as `fail` or with the
  malformed content.

### CT-PLG-004 — Deprecating a plugin keeps what it produced

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI, Extension Lifecycle: "Deprecating a plugin MUST NOT
  silently invalidate Baselines or Results a retired version already produced."
- **Method:** Automated
- **Fixture:** F-BASE with a Constraint bound to the registered `cts-len`.
- **Action:** Execute `cts-suite`; designate the Execution as a Baseline (as
  `P-APPROVER`, Section 14.1). Deprecate `cts-len`'s version. Retrieve the Results and
  the Baseline.
- **Expected:** Both are retrievable and unchanged; the `cts-len` Result still names the
  deprecated version in `oracle`.
- **Fails if:** Either is lost, altered, or marked invalid.

### CT-PLG-005 — A Custom Validator gets nothing beyond its evidence and configuration

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI: "a Custom Validator's determinism and absence of a
  Confidence value MUST be enforced at the SDK level, not merely documented as a
  convention."
- **Method:** Declaration, Harness
- **Fixture:** A Validator Plugin `cts-reach` that tries, in order, to read the clock,
  draw a random number, open a network connection to the harness, and return a
  Confidence value, and records in its Result's evidence which attempts succeeded.
- **Action:** Ask the implementation to state how its Validator SDK withholds the clock,
  randomness, the network, and Confidence. Register and run `cts-reach`; read the harness
  log.
- **Expected:** Each attempt fails or is refused at registration, and no Confidence
  value appears on the Result.
- **Fails if:** The harness receives a connection from `cts-reach`, or its Result
  carries a Confidence value. (Clock and randomness may not be observable from outside;
  the statement covers them.)

### CT-PLG-006 — A Dataset Plugin's output is versioned

- **Capability:** `plugins:dataset`
- **Requirement:** Volume XVI, Dataset Plugins: "every Dataset a plugin produces MUST be
  versioned, the same as one from a built-in source."
- **Method:** Automated
- **Fixture:** A Dataset Plugin the tester registers that produces one row,
  `query: "Plugin-1"`.
- **Action:** Produce a Dataset with it; retrieve the Dataset.
- **Expected:** The Dataset has a version, and a Scenario can reference it as
  `name@version`.
- **Fails if:** The Dataset has no version.

### CT-PLG-007 — A Report Plugin's Metric traces back to its Results

- **Capability:** `plugins:report`
- **Requirement:** Volume XVI, Report Plugins: "a Metric a Report Plugin introduces MUST
  be traceable back to the Results it was computed from."
- **Method:** Inspection
- **Fixture:** A Report Plugin the tester registers that introduces a Metric: the share
  of Results with Confidence below 0.7.
- **Action:** Run the batch of CT-REL-035; generate a Report with the plugin; follow
  the Metric to the Results behind it.
- **Expected:** The reviewer reaches the individual Results from the Metric.
- **Fails if:** The Metric cannot be traced to its Results.
