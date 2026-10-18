# 1. Conventions

## 1.1 Test format

Every test has the same fields:

| Field | Meaning |
|---|---|
| **ID** | `CT-<area>-<nnn>`. Areas: `CFG` configuration, `EXE` execution, `ASM` assessment, `DEC` decision, `REL` release and governance, `API` API behavior not tied to one layer; for scoped capabilities, `HRV` Human Review, `MJG` Multi Judge, `SCT` Seeded Controls, `ABD` Action Boundary, `DSR` Dataset sources, `PLG` Plugins, `SDK` SDKs and CLI, `RUI` Reference UI, `TTP` Test Types. IDs are never reused. |
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

## 1.3 Verification methods

| Method | Meaning |
|---|---|
| **Automated** | The outcome is read from the implementation's own records or responses: the Results, Gate Results, Release Decisions, Execution records, and errors it produces. |
| **Harness** | The outcome is read from the test harness (1.4): which calls the subject and the Judge actually received, in what order, how many times. |
| **Inspection** | A reviewer examines the implementation's documentation, configuration, or records and states what was found. Used where a requirement cannot be observed from outside, such as how scheduling decisions are recorded. |
| **Declaration** | The implementation states how it meets the requirement, and the reviewer records the statement and whether it is plausible. Used only where neither of the above can reach, such as whether a Validator is pure in the sense of Volume V. A Declaration is evidence of intent, not of behavior, and a report says so. |

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
  session. Calls are logged against the test and variant they belong to, and a harness
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

## 1.7 Test report

A test report gives, for each test, its outcome and, for `NOT_RUN` and
`NOT_APPLICABLE`, the reason. It also lists every requirement of Section 90 whose tests
were all `NOT_RUN` or `NOT_APPLICABLE` for that implementation: those requirements were
not verified, and a summary of the run says so rather than counting them as covered.

