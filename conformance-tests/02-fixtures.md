# 2. Fixtures

## 2.1 F-BASE — the base configuration

Every test starts from F-BASE unless it says otherwise. F-BASE is complete and valid
under Appendix A: one Environment, one Suite, one Scenario with one Constraint and one
Expectation, and one blocking Quality Gate.

```yaml
project:
  name: cts-base
  environments:
    - name: cts-env
      model_version: cts-scripted-subject@1
      prompt_version: cts-prompt@1
      tool_configuration: null
      infra_target: cts-harness
  quality_gates:
    - name: functional-gate
      aggregate: functional
      threshold: 1.0
      on_failure: block_release
  suites:
    - name: cts-suite
      scenarios:
        - name: s-greeting
          variables:
            query: "Hello"
          prompt:
            template: "{{query}}"
          contract:
            constraints:
              - validator: schema
                target: response
                expected: { type: string, minLength: 1 }
            expectations:
              - criteria: "The response greets the user."
                judge:
                  model: cts-scripted-judge@1
                  confidence_source: self_rating
                confidence_threshold: 0.8
```

F-BASE's clauses declare no `id` and no `dimension`, so the defaults of Appendix A §A.5
apply: the schema Constraint counts toward Functional, the Expectation toward Semantic.

## 2.2 Scripted subject responses

| Code | Behavior |
|---|---|
| `SR-OK` | Returns the Response `"Hello! How can I help?"`. |
| `SR-EMPTY` | Returns the Response `""`, which fails the F-BASE schema Constraint (`minLength: 1`). |
| `SR-503-THEN-OK` | First call: HTTP 503 before any Response. Second call: as `SR-OK`. |
| `SR-ECHO` | Returns the Prompt it received, verbatim. |
| `SR-SLOW-200` | As `SR-OK`, after waiting 200 ms. |

Unless a test says otherwise, the scripted subject behaves as `SR-OK`.

## 2.3 Scripted Judge responses

| Code | Behavior |
|---|---|
| `J-PASS-90` | Verdict `pass`, Confidence `0.90`. |
| `J-PASS-60` | Verdict `pass`, Confidence `0.60` (below F-BASE's 0.8 threshold). |
| `J-FAIL-90` | Verdict `fail`, Confidence `0.90`. |
| `J-DOWN` | Refuses the connection on every call; no verdict. |
| `J-DOWN-THEN-PASS-90` | First call as `J-DOWN`; every later call as `J-PASS-90`. |
| `J-FAIL-THEN-PASS-90` | First call as `J-FAIL-90`; every later call as `J-PASS-90`. |

Unless a test says otherwise, the scripted Judge behaves as `J-PASS-90`.

## 2.4 F-MULTI — several Scenarios

Used where a test needs counts. As F-BASE, with `cts-suite` holding three Scenarios,
`s-1`, `s-2`, `s-3`, each identical to `s-greeting` except for its name and
`variables.query` (`"One"`, `"Two"`, `"Three"`).

## 2.5 Custom Validators

Some tests need a Custom Validator (Volume V). The tester registers these through
whatever means the implementation provides. Where it offers none, those tests are
`NOT_RUN`, with that reason.

| Name | Behavior |
|---|---|
| `cts-len` | `pass` if the Response is at least one character long, otherwise `fail`. Reads only the Response. |
| `cts-flaky` | Returns `pass` the first time it is called and `fail` every later time, whatever the input. Deliberately impure. |
| `cts-crash` | Raises an error on every call and returns no Result (CT-ASM-014). |

A test that uses one registers it as setup, unless its **Action** is the registration
itself, and the registration is a setup check (1.6).

## 2.6 Fixtures defined in later sections

| Fixture or behavior | Defined in |
|---|---|
| `semantic-gate`, `J-MAP`, `J-CATCH`, F-SEED | 13.1 |
| Principals (`P-RELEASE`, `P-APPROVER`, `P-NOPERM`, `P-EDITOR`, `P-REVIEWER`, `P-ADMIN`, `SA-CI`), `RP-1` | 14.1 |
| F-HR, `P-REVIEWER-2` | 20 |
| F-PANEL | 21 |
| `ORACLE-1`, `ADM-PASS`, `ADM-FAIL`, `SA-REVIEW`, `gate-admitted` | 16 |
| `SR-BYE`, F-SEED-V, `SR-HI`, `J-ALARM`, F-CLEAN, F-CLEAN-V | 22 |
| F-ACT, `SR-CALL(url)` | 23 |
| `cts-probe` | 25 |

## 2.7 Postcondition fixtures

Some tests start from the state another sequence of steps leaves behind: a reviewed
Result, a missed Seeded Control, an override. Each such state is named here, with the
steps that build it and the checks that confirm it was built. A test builds it in its
own Project as setup (1.6); it never relies on another test having run. Words such as
"evaluate the Gates", "override", and "a governed change" have the meanings of Sections
13.1 and 14.1. A machine form of each, for a harness, is in `harness/fixtures/`; where it
differs from this table, this table is right.

| Fixture | Built by | Setup checks |
|---|---|---|
| F-REVIEWED | F-BASE with `semantic-gate`; scripted Judge `J-PASS-60`. Execute `cts-suite`; evaluate the Gates. As `P-REVIEWER`, record a Human Reviewer Result with verdict `pass` for the Expectation, resolving the Judge's Result. | The Human Reviewer Result is recorded, with `resolves` naming the Judge's Result. |
| F-SEED-MISSED | F-SEED with `semantic-gate`; scripted Judge `J-PASS-90`. Execute `cts-suite`; evaluate the Gates. | `s-control`'s entry in `seeded_control_results` has `outcome: missed`. |
| F-OVERRIDDEN | F-BASE with `semantic-gate`; scripted Judge `J-FAIL-90`. Execute `cts-suite`; evaluate the Gates. Override `semantic-gate`. As `P-RELEASE`, record a Release Decision with `decision: overridden`. | The `semantic-gate` GateResult carries `override`; the Release Decision is accepted. |
| F-GATE-CHANGED | F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`. Execute `cts-suite`; evaluate the Gates (evaluation 1). As a governed change, set `semantic-gate`'s `threshold` to `0.9`. Evaluate the Gates again for the same batch (evaluation 2). | Evaluation 2's `semantic-gate` GateResult has `threshold: 0.9`. |
| F-CONTRACT-CHANGED | F-BASE with `semantic-gate`; scripted Judge `J-PASS-90`. Execute `cts-suite`; evaluate the Gates. As a governed change, set the Expectation's `confidence_threshold` in `s-greeting`'s inline Contract to `0.85`. | `s-greeting`, retrieved, has `confidence_threshold: 0.85`. |
| F-SA-DECISIONS | F-BASE with `semantic-gate`; `RP-1` in place. Batch 1, with `J-PASS-90`: execute, evaluate the Gates, and as `SA-CI` record decision (b): `decision: approved`, `release_policy: RP-1`. Batch 2, with `J-FAIL-90`: execute, evaluate the Gates, and as `SA-CI` record decision (d): `decision: rejected`, `release_policy: RP-1`. Then, as `P-RELEASE`, revoke `RP-1`. | Decisions (b) and (d) and the revocation are accepted. |
| F-BASELINED | F-BASE; scripted Judge `J-PASS-90`. Execute `cts-suite` twice. As `P-APPROVER`, designate the first Execution of `s-greeting` as a Baseline. Evaluate the Gates for the first batch, so that a Snapshot references `cts-env`. | The Baseline is recorded; the evaluation returned a `snapshot_id`. |
| F-SIGNALS | CT-REL-035's configuration. Execute `cts-suite`; evaluate the Gates. | A Report for the batch can be retrieved. |

## 2.8 Harness self-test

Before a test run, and after any change to the harness, the tester calls each scripted
behavior directly, without the implementation (Harness Contract §8.6), and checks that it does what Sections
2.2, 2.3, 13.1, 22, and 23 say: each subject code returns its Response or fails as
stated; each Judge code returns its verdict and Confidence; `J-MAP` follows its
mapping; `J-CATCH` returns `fail` with Confidence `0.90` for `Goodbye.` and for
`Bye now.`, and `pass` with `0.90` for `Hello! How can I help?`; `J-ALARM` returns
`fail` with `0.90` for `Hi there! What do you need?` and `pass` with `0.90` for
`Hello! How can I help?`; and every first-call
behavior changes after its first call and starts afresh after a reset (1.6). The
Custom Validators of 2.5 are checked the same way: `cts-len` passes `"a"` and fails
`""`; `cts-flaky` passes, then fails; `cts-crash` raises an error. Every test that uses a
behavior that failed its self-test is `NOT_RUN`, with that reason.
