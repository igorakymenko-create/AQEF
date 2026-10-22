# Stage C.2 — Normative Execution Traceability & Evidence Hardening

C.2 extends the conditionally accepted C.1. **Neither mock tests nor successful CI establish real SUT conformance.**

## Slices

1. **C.2.1 / introduced here** — case-level execution records with immutable commit, execution scope, assertions, evidence paths and SHA-256 verification; fail-closed negative tests.
2. **C.2.2 / implemented, CI validated** — bind every claimed normative case to the published inventory and actual runner observations; enforce unique case identity and expected predicates.
3. **C.2.3 / initial verifier implemented** — fail-closed finding inventory, source-run/commit bindings, evidence SHA-256, reviewer metadata. Source-log semantic verification and authenticated sign-off remain pending; C.1 reconciliation is unchanged.
4. **C.2.4 / pending** — external attestation/signing of the closure manifest, root-of-trust policy, verified signature, and expiry/rotation handling.
5. **C.2.5 / pending** — executed/passed/skipped/failed test-count policy and regression integration.
6. **C.2 Final Exit Audit / pending** — validate all slices, historical provenance, remaining gaps and real-SUT separation.

## Scope discipline

A verified C2-1 ledger proves that **supplied local files match the claimed evidence hashes**, not that the observation actually came from a real SUT. The origin must be established by a trusted executor / attestation at a later slice. Not-run cases must never be counted as passed.

Run: `python -m unittest discover -s conformance-tests/stage_c2 -p 'test_*.py' -v`
