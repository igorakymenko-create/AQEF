# 25. Capability: Plugins

Tests in this section apply to an implementation whose Conformance Statement claims
`plugins:<type>` for the type named in each test (§10). For a type it does not claim, the
test is `NOT_APPLICABLE`. The Custom Validators of Section 2.5 are registered here as
Validator Plugins.

**Further plugin.** `cts-probe`: a Validator Plugin that records everything it receives
in the harness log and returns `pass`; when its configuration has `malformed: true`, it
returns a Result with no `verdict` field at all.

`cts-judge-probe`: a Judge Plugin that returns verdict `pass` with Confidence `0.90`;
when its configuration has `no_confidence: true`, it returns a Result with a verdict and
no `confidence` field.

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
- **Fixture:** None beyond Section 2.5.
- **Action:** Register `cts-len` as a Validator Plugin. Read what the implementation
  reports for the registration, in its response, records, and documentation.
- **Expected:** It reports a repeatability check that passed, not that the plugin was
  shown to be deterministic.
- **Fails if:** Anything presents the passed check as proof of determinism.

### CT-PLG-003 — A plugin receives the logical inputs, and a malformed Result assesses nothing

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI, Plugin Invocation: "What every implementation MUST hold to
  is the logical shape of one assessment": the Evidence its clause names, the clause's
  content, its versioned configuration, and the Execution and clause identifiers, and
  "A Validator Plugin receives no other input to its assessment ... Data that only
  carries or authenticates the invocation, such as transport headers or credentials, is
  not an input to the assessment"; a Result that fails validation is
  `oracle_unavailable`, "never `fail`."
- **Method:** Automated, Harness
- **Fixture:** Two variants of F-BASE, each with one Constraint bound to `cts-probe`,
  `target: response`, `dimension: functional`. (a) `expected: { marker: 1 }`.
  (b) `expected: { marker: 2 }` and configuration `malformed: true`.
- **Action:** In each, execute `cts-suite`; read what `cts-probe` received; retrieve the
  `cts-probe` Result.
- **Expected:** (a) `cts-probe` received the Response, its clause's `expected`, its
  configuration, and the Execution and clause identifiers, and no other input to its
  assessment; data that only carries or authenticates the call is not compared. Its
  Result
  is `pass`, with `oracle` naming `cts-probe` and its version. (b) The `cts-probe`
  Result is `oracle_unavailable`, with `verdict: null`, and the scripted Judge receives
  no call. (The two cases run separately because the specification does not fix the
  order in which a Contract's Validators run, and a Validation that has not passed
  stops there.)
- **Fails if:** In (a), `cts-probe` received any other input to its assessment, or the
  Result
  does not name the plugin and version; in (b), the Result is recorded as `fail` or with
  the malformed content, or the Judge is called.

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

### CT-PLG-005 — A Custom Validator's determinism and lack of Confidence are enforced, not documented

- **Capability:** `plugins:validator`
- **Requirement:** Volume XVI: "a Custom Validator's determinism and absence of a
  Confidence value MUST be enforced at the SDK level, not merely documented as a
  convention"; Volume V, Custom Validators: "the same input MUST always produce the same
  Result, and it MUST NOT carry a Confidence value." Volume V, Validator SDK, adds that
  the SDK "SHOULD NOT give it a clock, a random source, or network access": a SHOULD,
  which this test reports on but does not fail.
- **Method:** Declaration, Automated, Harness
- **Fixture:** F-BASE with a Constraint bound to `cts-reach`, `target: response`,
  `dimension: functional`. `cts-reach` is a Validator Plugin that tries, in order, to
  read the clock, draw a random number, and open a network connection to the harness;
  records in its Result's evidence which attempts succeeded; returns `pass` if the
  random number it drew (or, where randomness is withheld, the clock reading in
  milliseconds) is even, `fail` if it is odd, and `pass` if neither is available; and
  adds a Confidence value of `0.5` to its Result.
- **Action:** Ask the implementation to state how its Validator SDK enforces determinism
  and the absence of Confidence. Register `cts-reach`. If it is registered, execute
  `cts-suite` ten times and retrieve the `cts-reach` Results; read the harness log.
- **Expected:**
  - The statement describes enforcement by the SDK or the Plugin Architecture, not only
    documentation or a convention for plugin authors.
  - Either registration is refused, or every `cts-reach` Result carries no Confidence
    value (`confidence: "not_applicable"`, or the Result is `oracle_unavailable` because
    the returned Confidence made it malformed), and the ten Results have the same
    `verdict` or are all `oracle_unavailable`.
  - Ten equal verdicts are a sampled consistency check, not a proof of determinism: the
    report labels them so, and rests any claim of enforcement on the statement.
  - Reported, not judged: which of the clock, randomness, and network `cts-reach`
    reached, from its evidence and the harness log; any of them reached is a deviation
    from Volume V's SHOULD, which the report names.
- **Fails if:** The statement describes no enforcement beyond documentation; a
  `cts-reach` Result carries a numeric Confidence; or the ten Results differ in
  `verdict`.

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
- **Action:** Build F-SIGNALS (2.7); generate a Report for its batch with the plugin;
  follow the Metric to the Results behind it.
- **Expected:** The reviewer reaches the individual Results from the Metric.
- **Fails if:** The Metric cannot be traced to its Results.

### CT-PLG-008 — A Judge Plugin's Result without Confidence assesses nothing

- **Capability:** `plugins:judge`
- **Requirement:** Volume XVI, Plugin Invocation: "The implementation validates the
  Result before recording it"; a plugin that "returns a Result that fails validation has
  assessed nothing: the recorded Result is `oracle_unavailable`, never `fail`"; Volume
  XVI, Judge Plugins: what can be checked is "does a Judge Plugin's Result carry a
  Confidence value at all"; Appendix C §C.7, `confidence`.
- **Method:** Automated
- **Fixture:** Two variants of F-BASE, with the Expectation's Judge replaced by
  `cts-judge-probe`. (a) As is. (b) With configuration `no_confidence: true`.
- **Action:** In each, execute `cts-suite` and retrieve the Expectation's Result.
- **Expected:** (a) The Result is `pass`, with Confidence `0.90` and `oracle` naming
  `cts-judge-probe` and its version. (b) The Result is `oracle_unavailable`, with
  `verdict: null`.
- **Fails if:** (b) is recorded with the plugin's verdict, or as `fail`, or with a
  Confidence the plugin did not return.
