# 1. Conventions

## 1.1 Test format

Every test has the same fields:

| Field | Meaning |
|---|---|
| **ID** | `CT-<area>-<nnn>`. Areas: `CFG` configuration, `EXE` execution, `ASM` assessment, `DEC` decision, `REL` release and governance, `ADM` Admission of Judges, `API` API behavior not tied to one layer; for scoped capabilities, `HRV` Human Review, `MJG` Multi Judge, `SCT` Seeded Controls, `ABD` Action Boundary, `DSR` Dataset sources, `PLG` Plugins, `SDK` SDKs and CLI, `RUI` Reference UI, `TTP` Test Types. IDs are never reused. |
| **Capability** | The Conformance Statement identifier the test belongs to (§10). `core` for the non-negotiable core. |
| **Requirement** | Where the requirement is stated, by Volume or Appendix and section, with the operative words quoted. |
| **Method** | How the outcome is observed (1.3). |
| **Fixture** | The configuration to start from: a fixture from section 2, and the changes to it. |
| **Action** | What the tester does. |
| **Expected** | What an implementation that meets the requirement does. |
| **Fails if** | The departures from **Expected** most likely to occur, named to make them easy to check. The list is not exhaustive: any observation that contradicts **Expected** fails the test (1.2). |

## 1.2 Outcomes

| Outcome | Meaning |
|---|---|
| `PASS` | The implementation behaved as **Expected**. Where **Expected** allows alternatives, any one of them is a `PASS`. |
| `FAIL` | The implementation did not behave as **Expected**: one of the **Fails if** observations was made, or any other observation that contradicts **Expected**. |
| `NOT_APPLICABLE` | The test's capability is not claimed in the implementation's Conformance Statement; or the test checks a feature the specification leaves optional (MAY), the implementation does not offer it, and the test says that this outcome applies. |
| `NOT_RUN` | The test could not be carried out, with the reason stated: for example, its setup could not be built (1.6), a fixture the tester supplies could not be provided or registered, or the harness failed its self-test (2.8). A `NOT_RUN` is not a `PASS`. |

**Cases.** A test whose **Action** lists numbered cases gives each case an identifier of
its own, the test's ID followed by the case number (`CT-CFG-025.07`), and each case has
its own outcome, decided by the table above as if it were a test. The test report gives
every case's outcome, and Section 90 traces requirements to cases, not to the test as a
whole. The test's own outcome only summarizes its cases: `FAIL` if any case is `FAIL`;
otherwise `NOT_RUN` if any case is `NOT_RUN`; otherwise `PASS` if any case is `PASS`;
otherwise `NOT_APPLICABLE`. A summary `PASS` therefore never stands for a case that did
not run, and a test with any case `NOT_RUN` is not reported as passed.

## 1.3 Verification methods

| Method | Meaning |
|---|---|
| **Automated** | The outcome is read from the implementation's own records or responses: the Results, Gate Results, Release Decisions, Execution records, and errors it produces. |
| **Harness** | The outcome is read from the test harness (1.4): which calls the subject and the Judge actually received, in what order, how many times. |
| **Inspection** | A reviewer, following 1.8, examines the implementation's documentation, configuration, or records and states what was found. Used where a requirement cannot be observed from outside, such as how scheduling decisions are recorded. |
| **Declaration** | The implementation states how it meets the requirement, and the reviewer records the statement and whether it is plausible, following 1.8. Used only where neither of the above can reach, such as whether a Validator is pure in the sense of Volume V. A Declaration is evidence of intent, not of behavior, and a report says so. |

Tests are written against observable behavior. Where an implementation exposes it
through the REST API (Appendix C), the API is the natural place to observe it; where it
uses another surface, the test report names that surface.

## 1.4 Test harness

A test checks the engine, not a model. Every fixture therefore points the engine at two
stand-ins the tester controls:

- a **scripted subject**: an endpoint the Environment's `model_version` resolves to,
  which returns a fixed Response chosen per test (section 2.2), or fails in a stated way;
- a **scripted Judge**: an endpoint a JudgeConfig's `model` resolves to, which returns a
  fixed verdict and Confidence chosen per test (section 2.3), or fails in a stated way.

Both record every call they receive. How an implementation maps a model identifier to an
endpoint is its own concern; the tester configures it so that these identifiers reach the
harness. Neither stand-in is a probabilistic subject or a real Judge, and the
specification does not require one to be: the subject is whatever its Environment points
to (Volume II), and a scripted Judge still satisfies Independent Oracles, since its
identifier differs from the subject's.

The interfaces of the harness, the adapter between tester and implementation, the
records a run keeps, and the format of the test report are specified in the **Harness
Contract** (`harness/`), a separate, non-normative document versioned on its own. It
binds a harness, never an implementation, and adds no test: where it and this document
disagree, this document is right.

## 1.5 Notation

- Fixture changes are written as YAML fragments with a path, e.g. *in
  `suites[0].scenarios[0]`, remove `contract`*.
- `{{name}}` in a prompt template is illustrative. The specification leaves placeholder
  syntax to the implementation (Appendix A §A.4, PromptDef); the tester substitutes the
  implementation's own.
- "Loaded" means accepted at configuration load time, before any Execution. "Rejected"
  means refused at that point, with an error that identifies what was wrong.

## 1.6 Isolation

Every test can be run on its own, in any order, and gives the same outcome whichever
tests ran before it.

- **A Project of its own.** Each test runs in a Project no other test uses. The text
  calls it `cts-base`; the tester may give it a unique name per test, such as
  `cts-base-CT-DEC-012`. The Principals of Section 14.1 are set up for it. Where a
  **Fixture** gives variants, (a), (b), ..., each variant runs in a Project of its own;
  the steps of one **Action** share one Project.
- **A harness session of its own.** Before the test starts, the scripted subject and
  Judge are reset: their call logs are emptied, their scripted behaviors set to the
  defaults of Sections 2.2 and 2.3 or to what the test names, and every counter cleared,
  so that a "first call" is the first call within this test. Each variant gets its own
  session. (Harness Contract §8.2 and §8.3.) Calls are logged against the test and variant they belong to, and a harness
  observation counts only those. A test that switches a behavior during its **Action**
  changes it from the next call on, without clearing the counters.
- **Setup.** A test whose **Fixture** names a postcondition fixture (2.7) builds it in
  its own Project as setup, then checks the fixture's setup checks. Calls made during
  setup are not counted in any harness observation of the test. If the setup cannot be
  built or a check fails, the test is `NOT_RUN`, with the step that failed as its
  reason: the behavior that failed belongs to the test that checks it, which reports it
  as a `FAIL` there.
- **Reusing a configuration.** "As CT-xxx" in a **Fixture**, without "after", reuses that
  test's configuration only. No test relies on another test having run.
- **Waiting.** Where a test waits for something to happen (a review timeout, a pipeline
  timeout), the tester states a budget before the run: the configured duration plus a
  grace period. The tester watches for the event the test names, such as a record or a
  change of state, rather than sleeping for a fixed time, and stops at the end of the
  budget. If the shortest duration the implementation accepts is longer than the run can
  wait, the test is `NOT_RUN`, with that reason. Durations are measured by the harness
  on a monotonic clock; the harness's time is never taken as the implementation's.

## 1.7 Test report

A test report gives, for each test and each case (1.2), its outcome and, for `NOT_RUN`
and `NOT_APPLICABLE`, the reason. It also gives every requirement of Section 90 a state,
from the tests and cases Section 90 traces it to, leaving out those `NOT_APPLICABLE`:

| Tests and cases traced | State |
|---|---|
| Any `FAIL` | violated |
| Otherwise any `NOT_RUN`, or any the run left out | unverified |
| Otherwise at least one `PASS` | verified |
| Otherwise | not applicable |

A requirement is therefore verified only when every applicable test or case traced to
it passed: a `PASS` in one test never covers a `NOT_RUN` in another, and a requirement
traced to a case is decided by that case, never by the outcome of the test it belongs
to. A row of status Restates takes the state of the row it restates. A summary of the
run lists every unverified requirement rather than counting it as covered. The report's
format is the Harness Contract's (§14, §15).

## 1.8 Review of Inspection and Declaration tests

A test whose method is Inspection or Declaration is decided by a named reviewer, in a
way a second reviewer can repeat:

- The reviewer turns **Expected** into a checklist, one item per statement, and records
  for each item whether it is met and the evidence used: an identifier of the record,
  document, response, or screen, kept with the test report.
- The test is `PASS` only when every item is met and has its evidence recorded. An item
  without evidence, or one the reviewer cannot decide, makes the test `NOT_RUN`, never
  `PASS`. An item shown not to be met makes it `FAIL`.
- Where the outcome is disputed, a second reviewer decides from the same evidence
  without seeing the first decision. Until both agree, the test is `NOT_RUN`, and the
  report keeps both records.

The record of a review is specified in the Harness Contract (§13).

