# Stage C.2 — Normative Execution Traceability & Evidence Hardening

C.2 extends the conditionally accepted C.1. **Neither mock tests nor successful CI establish real SUT conformance.**

## Slices

1. **C.2.1 / introduced here** — case-level execution records with immutable commit, execution scope, assertions, evidence paths and SHA-256 verification; fail-closed negative tests.
2. **C.2.2 / implemented, CI validated** — bind every claimed normative case to the published inventory and actual runner observations; enforce unique case identity and expected predicates.
3. **C.2.3 / metadata verifier implemented** — fail-closed finding inventory, source-run/commit bindings, evidence SHA-256, reviewer metadata. Source-log semantic verification and authenticated sign-off remain pending; C.1 reconciliation is unchanged.
3a. **C.2.3.5 / structured execution gate implemented** — `closure_integration.py` checks finding-to-test mapping, trusted source run/commit, exact structured JSON test result and finding claim, with positive and negative tests. Outputs `OPEN` or `EVIDENCE_VERIFIED`, never authenticated `CLOSED`. Existing C.1 artifact remains immutable; adoption into a new C.2 closure workflow with verified production records remains outstanding.
4. **C.2.4 / verifier implemented, operational provisioning pending** — Ed25519 signature verification bound to manifest contents, commit SHA, CI run, signer identity, independent trust store and validity/rotation window. Private signing keys, externally maintained public-key trust store and actual signed CI artifact are NOT provisioned. Demo tests use ephemeral keys only.
4a. **C.2.4.5 / implemented, provisioning pending** — protected manual workflow `.github/workflows/cts-c245-trusted-signing.yml`, operational Ed25519 signing tool, separate externally provisioned trust store, verification before artifact upload. Requires GitHub Environment `aqef-attestation`, secret `AQEF_SIGNING_KEY_PEM`, secret `AQEF_TRUST_STORE_JSON`, vars `AQEF_SIGNING_KEY_ID` and `AQEF_SIGNER_IDENTITY`. Do not copy the signing key or replace external trust roots with dynamically generated in-run roots. This workflow produces a **mock-only CI statement**, not signed historical C.1 evidence or real SUT conformance. Until externally provisioned and run, operational attestation is **NOT ESTABLISHED**.
5. **C.2.5 / implemented, CI pending** — verbose unittest accounting for total/executed/passed/failed/errors/skipped, zero-skip default, SHA-256 log binding and 423-case C.1 baseline in CI. Results remain unit-only, not CTS conformance.
6. **C.2 Final Exit Audit / pending** — validate all slices, historical provenance, remaining gaps and real-SUT separation.

## Scope discipline

A verified C2-1 ledger proves that **supplied local files match the claimed evidence hashes**, not that the observation actually came from a real SUT. The origin must be established by a trusted executor / attestation at a later slice. Not-run cases must never be counted as passed.

Run: `python -m unittest discover -s conformance-tests/stage_c2 -p 'test_*.py' -v`

## C.2.R1 — historical evidence recovery (in progress)

Run `python conformance-tests/stage_c2/r1_recovery.py` to produce `r1_recovery_matrix.json`. It retains the 14 historical C.1 findings and immutable source runs but intentionally marks all as `NOT_ESTABLISHED` until finding-specific execution evidence is independently evaluated. Historical logs are available from GitHub Actions; availability of logs is not finding-level closure. The original C.1 `reconcile()` is preserved and must not be treated as verified finding disposition.
