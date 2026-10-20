# 11. Execution and Evidence

Tests in this section run `cts-suite` against `cts-env` and observe the Executions,
Conversations, and Artifacts that result, and the calls the scripted subject received.

### CT-EXE-001 — Every Execution runs in exactly one Environment

- **Capability:** core
- **Requirement:** Volume II, Environment: "every Execution MUST run inside exactly one
  Environment."
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite` against `cts-env`.
- **Expected:** The Execution record names exactly one Environment, `cts-env`.
- **Fails if:** The record names no Environment, more than one, or a different one.

### CT-EXE-002 — Variable interpolation is deterministic

- **Capability:** core
- **Requirement:** Volume III, Variables: "the same Variables and the same Prompt
  template MUST produce the same literal Prompt text every time."
- **Method:** Automated, Harness
- **Fixture:** F-BASE; scripted subject `SR-ECHO`.
- **Action:** Execute `cts-suite` twice.
- **Expected:** The scripted subject receives the literal Prompt `Hello` on both calls,
  and both Conversations record it identically.
- **Fails if:** The two Prompts differ in any character, or differ from `Hello`.

### CT-EXE-003 — An infrastructure failure before a Response is retried, and leaves no Conversation

- **Capability:** core
- **Requirement:** Volume III, Retry: "A retried Execution of this kind produces no
  Conversation on the failed attempt and MUST NOT be treated as if it had; only the
  successful attempt is the Execution that produces a Result."
- **Method:** Automated, Harness
- **Fixture:** F-BASE; add `execution: { retry: { max_attempts: 2, on:
  infrastructure_failure } }` to the Project; scripted subject `SR-503-THEN-OK`.
- **Action:** Execute `cts-suite`.
- **Expected:** The scripted subject receives two calls. One Execution of `s-greeting`
  is recorded, with one Conversation containing the `SR-OK` Response, and its Results.
- **Fails if:** A Conversation, Result, or Execution is recorded for the failed attempt;
  or no Execution is recorded.

### CT-EXE-004 — A genuine Response is never retried

- **Capability:** core
- **Requirement:** Volume III, Retry: a re-run because "a Result later came back failing
  or low-Confidence ... is not a Retry"; Appendix B §B.3, Retry scope: "RetryConfig MUST
  NOT trigger on Result-level failures."
- **Method:** Automated, Harness
- **Fixture:** As CT-EXE-003, with scripted subject `SR-EMPTY`.
- **Action:** Execute `cts-suite`.
- **Expected:** The scripted subject receives exactly one call. The schema Constraint's
  Result is `verdict: fail`.
- **Fails if:** The subject receives a second call within the same Execution, or the
  failing Result is absent or replaced.

### CT-EXE-005 — A later Execution does not replace an earlier Result

- **Capability:** core
- **Requirement:** Volume III, Retry: "the original Execution's Result stands and MUST
  be recorded, not discarded in favor of a more favorable second attempt."
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite` with scripted subject `SR-EMPTY`; then execute it
  again with `SR-OK`.
- **Expected:** Two Executions are recorded. The first keeps its failing schema Result,
  unchanged; the second has its own, passing one.
- **Fails if:** The first Execution's Result is removed, modified, or marked superseded.

### CT-EXE-006 — Parallel Executions do not share state

- **Capability:** core
- **Requirement:** Volume III, Parallelization: "Executions running in parallel MUST NOT
  share mutable Context ... or Variables state with one another."
- **Method:** Automated, Harness
- **Fixture:** F-MULTI; add `execution: { parallelization: 3 }`; scripted subject
  `SR-ECHO`.
- **Action:** Execute `cts-suite`.
- **Expected:** Each of `s-1`, `s-2`, `s-3` has a Conversation whose Prompt and Response
  are its own `query` (`One`, `Two`, `Three`), and nothing else.
- **Fails if:** Any Conversation contains another Scenario's value.

### CT-EXE-007 — Two Executions of one Scenario run in an identical harness

- **Capability:** core
- **Requirement:** Volume I, Chapter 3, Deterministic Infrastructure: "Two Executions of
  the same Scenario in the same Environment MUST go through an identical harness";
  Volume III, Runtime.
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite` twice.
- **Expected:** Both Execution records show the same resolved configuration: Environment
  (`model_version`, `prompt_version`, `tool_configuration`, `infra_target`), the
  Contract (its version, or its content where it is inline), and the Prompt template.
- **Fails if:** Any of these differs between the two records, or is not recorded.

### CT-EXE-008 — Evidence is captured with every Execution

- **Capability:** core
- **Requirement:** Volume I, Chapter 4, Logical Layers (Evidence); §8, Execution: "An
  Execution produces exactly one Conversation, zero or more Artifacts"; Volume III,
  Artifact Collection.
- **Method:** Automated
- **Fixture:** F-BASE.
- **Action:** Execute `cts-suite`.
- **Expected:** The Execution has exactly one retrievable Conversation, containing the
  Prompt `Hello` and the `SR-OK` Response exactly as the subject returned it. Any
  Artifacts the implementation records for the turn are retrievable with it.
- **Fails if:** The Conversation is missing, there is more than one, or its content
  differs from what was sent and returned.

### CT-EXE-009 — Why an Execution ran when it did can be reconstructed

- **Capability:** core
- **Requirement:** Volume III, Scheduling: "*why* a given Execution ran when it did MUST
  be reconstructable."
- **Method:** Inspection
- **Fixture:** F-MULTI.
- **Action:** Execute `cts-suite`. From the implementation's records alone, establish
  for each of the three Executions what triggered it and its position in the order.
- **Expected:** The reviewer can state both for every Execution, citing the records used.
- **Fails if:** For any Execution, the trigger or the order cannot be established from
  the records.

### CT-EXE-010 — An Execution draws rows from the Dataset version it names

- **Capability:** core
- **Requirement:** Volume IV, Versioning: "a specific Execution's Variable Resolution
  (Volume III) is only reproducible if the Dataset row it drew from is pinned to a
  specific version."
- **Method:** Automated, Harness
- **Fixture:** F-BASE with `variables` removed from `s-greeting` and `dataset:
  ds-1@1.0.0`, where `ds-1@1.0.0` is CT-CFG-011's Dataset (one row, `query: "Hi"`);
  scripted subject `SR-ECHO`.
- **Action:** Execute `cts-suite`. Register `ds-1@1.1.0` with one row, `query: "Bye"`.
  Execute `cts-suite` again without changing the Scenario.
- **Expected:** The scripted subject receives the Prompt `Hi` both times, and each
  Execution record names `ds-1@1.0.0` and the row `r1`.
- **Fails if:** The second Execution uses `Bye`, or either record does not identify the
  Dataset version and row.

### CT-EXE-011 — The Conversation Engine is deterministic given the same Responses

- **Capability:** core
- **Requirement:** Volume III, Conversation Engine: its own logic, "how it decides a
  Conversation is complete, how it constructs the next turn's Prompt given the Context
  accumulated so far — MUST itself be deterministic given the same Context and Responses
  so far."
- **Method:** Harness
- **Fixture:** F-BASE, scripted subject `SR-ECHO`. Where the implementation runs
  multi-turn Scenarios, the tester also uses one of its own documented multi-turn
  Scenarios, with the scripted subject returning the same fixed sequence of Responses
  on every run.
- **Action:** Execute each Scenario twice. Compare, call by call, every request the
  scripted subject received.
- **Expected:** Both runs send the same number of requests, and each request is
  identical, character for character, to its counterpart in the other run, apart from
  identifiers of the Execution itself. Both Conversations end after the same turn.
- **Fails if:** The runs differ in the number of turns or in any request.

### CT-EXE-012 — Infrastructure facts of a turn are captured as they happened

- **Capability:** core
- **Requirement:** Volume III, Artifact Collection: what it "records about the
  infrastructure-level facts of a turn — the exact request a tool call sent, the exact
  latency observed — MUST itself be captured deterministically."
- **Method:** Automated, Harness
- **Fixture:** F-BASE; scripted subject `SR-SLOW-200`. Add to the Scenario's
  Constraints:
  ```yaml
  - validator: latency
    target: artifacts.duration_ms
    expected: { max: 100 }
  ```
  (or the implementation's documented path for observed latency).
- **Action:** Execute `cts-suite`; retrieve the Artifacts and the latency Constraint's
  Result. Then switch to `SR-OK` and execute again.
- **Expected:** The first Execution's Artifacts record a latency of at least 200 ms and
  the request exactly as the harness received it; its latency Result is `fail`. The
  second Execution's latency Result is `pass`. If the harness log shows that the harness
  itself took 100 ms or more to answer the second Execution, that Execution is repeated,
  up to three times; if none is answered in under 100 ms, the test is `NOT_RUN`, with the
  harness's times as the reason.
- **Fails if:** The recorded latency is below what the harness observed, the recorded
  request differs from the one received, or either latency Result contradicts the
  harness log.
