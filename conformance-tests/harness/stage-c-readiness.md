# Harness Contract — open questions and Stage C criteria

Stage C builds a harness and a reference adapter to this contract and runs selected CTS
tests, first against a mock implementation, then, if one is available, against a real
one. It tests the harness, not AQEF conformance.

## 1. Open questions

| ID | Question | Needed before | Proposed |
|---|---|---|---|
| Q-01 | Arguments and normalized results of the 32 operations not typed in 0.3. | Slices S4, S5 | Type each when its first test is automated; derive result shapes from Appendix B's schema types (Result, GateResult, Basis, Release Decision, Snapshot). |
| Q-02 | How the runner reads values out of SUT responses for **Expected** (for example `basis.results`). | S1 | A field-path map per surface, kept with the adapter, from Appendix B and C names to the surface's fields. |
| Q-03 | Machine form of setup checks in `fixtures/`. | S3 | Each check as an operation, a JSON pointer, and an expected value, beside its words. |
| Q-04 | Signature mechanism for review records. | Manual suite | A detached signature over the JCS form of the record, or a record in an authenticated system. |
| Q-05 | Default drain time and grace periods. | S2 | Measured during the S0 self-test; the defaults of §9.2 and §11 until then. |
| Q-06 | Base of the schemas' `$id`: under the AQEF repository (0.3) or a vendor domain (v0.2). | Publication | Repository-based, as in 0.3. For the author to decide. |
| Q-07 | Where harness and adapter code live. | S0 | Outside the specification repository; this folder holds only the contract, schemas, examples, recipes, and the validator. For the author to decide. |
| Q-08 | Machine form of each test's **Expected**. | S1 to S3 | For the tests of the slices only, as predicates over the field paths of Q-02, kept with the runner and reviewed against the CTS text. |

## 2. Entry criteria

1. Harness Contract 0.3 and CTS Working Draft 7 published together.
2. `tools/validate.py` passes on the published package.
3. Q-06 and Q-07 decided.
4. A run profile template exists: budgets and grace periods, drain time, allowlisted
   instance, credential references, retention.

## 3. Slices

| Slice | Tests | Shows |
|---|---|---|
| S0 Self-test | CTS 2.8 through `self_test`; two sessions in parallel | Every behavior as defined; resets isolated (I-05). |
| S1 Configuration | CT-CFG-001; CT-CFG-025.01, .05, .25 | Case outcomes; `NOT_APPLICABLE` for an unclaimed capability (I-11); rejection as an outcome (I-03). |
| S2 Execution and assessment | CT-EXE-003, CT-EXE-008, CT-ASM-001, CT-ASM-014 | Stimuli versus failures (I-06); negative assertions after closure (I-04); honest `NOT_RUN`. |
| S3 Decision | CT-DEC-006, CT-DEC-012, CT-REL-006 | Postcondition fixtures; Gate and resolution observations. |
| S4 Extensions | CT-HRV-003, CT-PLG-003, CT-SDK-001 | Waiting budgets; test plugins; a capability adapter. |
| S5 Reporting | the runs of S0 to S4 | A schema-valid report whose algebra the validator recomputes. |

## 4. Exit criteria

1. S0 passes, and two parallel sessions share no counter, behavior, or log.
2. At least ten CTS cases, from S1 to S3, run against a mock implementation.
3. Deliberately broken mock behavior gives `FAIL`; a setup the harness cannot provide
   gives `NOT_RUN`; an unclaimed capability gives `NOT_APPLICABLE`; CT-CFG-025 with one
   case `NOT_RUN` gives the test `NOT_RUN` (I-09).
4. For a negative harness assertion: a closed log gives `PASS`, an unclosed one
   `NOT_RUN`, a mock that calls late `FAIL` (I-04).
5. Changing or removing one raw evidence object is detected (I-08).
6. At least five contract tests of the adapter itself pass, including rejected
   envelopes (I-01) and a wrong contract version.
7. The report validates, and `tools/validate.py` recomputes its test and requirement
   states without difference.
8. If an implementation is available, one end-to-end run through the Appendix C REST
   adapter, reported apart from the mock runs. No mock run is presented as a
   conformance result.
