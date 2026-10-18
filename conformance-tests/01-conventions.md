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
| **Fails if** | The observations that make the test fail. Anything not listed here and not contradicting **Expected** does not. |

## 1.2 Outcomes

| Outcome | Meaning |
|---|---|
| `PASS` | The implementation behaved as **Expected**. |
| `FAIL` | One of the **Fails if** observations was made. |
| `NOT_APPLICABLE` | The test's capability is not claimed in the implementation's Conformance Statement. Not available for `core`. |
| `NOT_RUN` | The test could not be carried out, with the reason stated. A `NOT_RUN` is not a `PASS`. |

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
