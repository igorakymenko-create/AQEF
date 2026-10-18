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
