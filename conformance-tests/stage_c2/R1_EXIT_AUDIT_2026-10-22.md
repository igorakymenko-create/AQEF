# C.2.R1 — Exit Audit (2026-10-22)

**Decision: CONDITIONAL PASS (fail-closed engineering mechanism only)**

- PR: https://github.com/igorakymenko-create/AQEF/pull/2 (Draft)
- Reviewed source branch HEAD: `8a48a39795d809f055603d9646a9ad91d68437fc`
- Verified pull_request CI checkout/merge commit: `659107cf552f50d9bc957029b1a9e68306e96dfd` (distinct from branch HEAD)
- C.2 workflow: https://github.com/igorakymenko-create/AQEF/actions/runs/39814209674 — SUCCESS
- Harness: https://github.com/igorakymenko-create/AQEF/actions/runs/39814209711 — SUCCESS
- Mutation regression: https://github.com/igorakymenko-create/AQEF/actions/runs/39814209692 — SUCCESS
- C.2 register artifact ID `12441446729`; `c2-r13-finding-register-659107cf552f50d9bc957029b1a9e68306e96dfd`, available, not expired (artifact was not independently byte-for-byte revalidated as part of this audit).
- CI log confirms 423 executed / 423 passed / 0 skipped (UNIT TESTS, NOT normative CTS cases).
- R1.3 CI log: 14 historical findings, 13 PARTIAL, 1 NOT_ESTABLISHED, 0 VERIFIED/CLOSED.

## Gate assessment

| Gate | Status | Rationale |
|---|---|---|
| Source inventory completeness | PASS | 14 C.1 findings reconciled |
| Candidate unit-test discovery | PASS (identity only) | Named test candidates observed in historical logs |
| Assertion semantic qualification | PARTIAL | 13 partial; S4-F05 not established |
| Fail-closed C.2 disposition | PASS | All remain unresolved; C.1 claims not promoted |
| Historic finding evidence authenticity | NOT ESTABLISHED | No independently preserved per-finding signed structured execution logs |
| Formal historical finding closure | FAIL/OPEN | 0/14 verified/closed |
| Artifact publishing | PASS for publication, authenticity review pending | CI confirms upload, audit did not check artifact bytes |
| Real-SUT conformance | NOT ESTABLISHED | Out of mock engineering acceptance scope |

## Critical remaining gaps

- **R1-EX-01 / HIGH / OPEN:** `r13_reconciliation.py` invokes `reconcile_strict()` with intentionally empty evidence arrays. It proves fail-closed handling, not positive historical evidence reconciliation. Before claiming C2-IA-01 CLOSED, consume authentic historic source-run evidence with credible per-finding mapping and independently checked content.
- **R1-EX-02 / MEDIUM / OPEN:** Historical `source_commit` is derived from `HISTORIC_RUNS` rather than independently recovered evidence, and no external authentication root is supplied. The CI run on a pull-request merge SHA must be distinguished from branch HEAD in provenance and policy.
- **R1-EX-03 / MEDIUM / OPEN:** `r12_qualification.py` checks qualified status/rationale structure, not semantic correctness of findings or source assertions. Qualifying another finding requires reviewer review and independently collected traces.
- **R1-EX-04 / LOW / OPEN:** Published register artifact presence confirmed in GitHub Actions metadata, but its ZIP contents/hashes were not independently retrieved and revalidated by this exit audit.

## Decision

**Accept R1 as a working, fail-closed mock-scoped reporting mechanism with explicit residual open findings. Do NOT close integration finding C2-IA-01**, which requires independently qualified historical evidence, nor assert that the 14 findings were remediated. The R1 engineering substage can end conditionally while the actual evidence-closure obligation remains open and blocking unconditional C.2 exit.

Next: R2 trusted signing infrastructure and R3 linked evidence integration, including remediation for R1-EX-01..04. Draft PR #2 remains unapproved and unmerged.
