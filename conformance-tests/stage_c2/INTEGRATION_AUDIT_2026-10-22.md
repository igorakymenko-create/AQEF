# Stage C.2 — Integration Audit (2026-10-22)

**Audited head:** `960f580bdc75deca382870712ead7b4b333eafde`
**PR:** https://github.com/igorakymenko-create/AQEF/pull/2
**Verdict:** **CONDITIONAL PASS for engineering components / INTEGRATION EXIT NOT MET**
**Scope:** mock-only engineering evidence. No real-SUT conformance claims.

## Observed CI

- CTS Stage C.2.1 Traceability — https://github.com/igorakymenko-create/AQEF/actions/runs/39799363709 — SUCCESS
- CTS harness checks — https://github.com/igorakymenko-create/AQEF/actions/runs/39799363736 — SUCCESS
- CTS Mutation Regression — https://github.com/igorakymenko-create/AQEF/actions/runs/39799363679 — SUCCESS

These runs confirm automated checks on the audited head, not that externally signed or historic finding-closure evidence was supplied.

## Findings

| ID | Severity | Disposition | Evidence | Required closure |
|---|---|---|---|---|
| C2-IA-01 | HIGH | OPEN | `stage_c_closure/closure.py:reconcile()` still emits statuses from `FINDINGS` without invoking `stage_c2/closure_integration.py:reconcile_strict()`. | Add a separate C.2 closure runner consuming actual historical evidence, preserving unresolved findings. Explicit finding-to-test provenance and CI artifact required. |
| C2-IA-02 | HIGH | OPEN | `cts-c245-trusted-signing.yml` is `workflow_dispatch` only; it signs a newly generated `ci-statement.json`, not historic C.1 closure evidence. No authenticated completed signed-evidence package demonstrated during this audit. | Provision independent signer/trust roots, produce and externally verify a signed package tied to a named evidence run and a stable trust policy. |
| C2-IA-03 | HIGH | OPEN | No integrated flow proved `normative inventory -> case execution -> evidence -> finding reconciliation -> signed manifest -> regression accounting` using the *same* evidence package. | Add fail-closed end-to-end integration fixture and real CI artifact, including tampering negative tests. |
| C2-IA-04 | MEDIUM | OPEN | C.2.2 validates predicate identity and case references, but does not fully interpret each free-text normative expected predicate. | Explicitly scope unsupported normative predicates; forbid claims of verified normative conformance for unsupported predicates. |
| C2-IA-05 | MEDIUM | OPEN | C.2.5 derives passed/skipped from verbose unittest text and cross-checks `Ran N tests`, but the system does not yet authenticate the execution producer, nor count normative CTS cases. | Keep unit-only scope; require trusted machine-readable result provenance for externally relied-upon claims. |
| C2-IA-06 | LOW | OPEN | PR #2 title/body still describe the initial C.2.1 slice and imply later slices are outstanding. | Update PR description to reflect actual implemented scope and remaining exit blockers. |

## Acceptance accounting

- **C.2.1/2:** implemented and CI-tested, mock-only bounds.
- **C.2.3/3.5:** validators and unit tests pass; operational historic evidence reconciliation is not closed.
- **C.2.4/4.5:** Ed25519 unit tests pass; trusted operational signing and evidence custody remain unproven.
- **C.2.5:** unit regression accounting integrated with CI, zero skips by default.
- **Real SUT:** not evaluated; cannot infer conformance from a mock harness.

## Decision and exit gates

**DO NOT approve or merge PR #2 based on this Integration Audit.** Final Exit Audit should not be declared PASS until C2-IA-01 through C2-IA-03 are closed with inspectable evidence, and remaining medium issues are either resolved or formally accepted with explicit restrictions.

The audit itself is evidence of review, **not** remediation of the findings.
