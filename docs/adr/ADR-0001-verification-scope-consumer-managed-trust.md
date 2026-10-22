# ADR-0001 — Separate AQEF Feasibility, Conformance, and Deployment Trust

- **Status:** ACCEPTED — architectural direction; publication on `main` remains pending Draft PR review
- **Decision date:** 2026-10-22
- **Decision authority:** AQEF project owner
- **Applies to:** AQEF engineering verification, CTS tooling, reference implementations, CI integration, public distribution planning
- **Does not amend:** AQEF normative specification, its version, existing issued licenses, historical audit outcomes
- **Basis:** [Repository & Verification Architecture Review](../../reviews/AQEF_REPOSITORY_AND_VERIFICATION_ARCHITECTURE_REVIEW_2026-10-22.md)
- **Related:** [Stage C.2 Integration Audit](../../conformance-tests/stage_c2/INTEGRATION_AUDIT_2026-10-22.md), [R1 Exit Audit](../../conformance-tests/stage_c2/R1_EXIT_AUDIT_2026-10-22.md)

## Context

AQEF's Working Draft 0.40 defines an AI quality-engineering architecture and capability-scoped conformance for **implementations of AQEF**, not a certification of AI subjects, testers, organizations, or their CI platforms. Its CI/CD volume describes integration with **consumer-owned** pipelines; the platform's own native security primitives are out of scope.

The repository currently contains a textual specification, a non-normative Conformance Test Specification (CTS), a harness contract and validator, stage-specific mock engineering checks, historical audit closure scripts, optional attestation code, and many CI workflows. The previously verified 423-test Python regression is **not** execution of 423 normative CTS cases against an independent AQEF implementation. Similarly, the C.2 Python checks are engineering tests, not proof of SUT conformance.

The current CTS WD7 targets AQEF 0.38 and claims compatibility with 0.39. Version 0.40 introduces normative additions, so coverage against 0.40 requires an explicit delta review. Existing document status warns against claims of conformant implementations of this working draft.

## Decision

### D1 — Define four non-interchangeable claims

1. **Specification consistency:** the written requirements, schemas and examples can be interpreted without contradictory obligations.
2. **Harness and component correctness:** the harness, adapters, validators and reports react correctly to positive, negative and incomplete inputs, under known mock/test fixtures.
3. **AQEF implementation feasibility:** an **independently bounded minimal AQEF reference engine** can execute a complete `Definition → Execution → Evidence → Assessment → Decision` lifecycle and produce verifiable, appropriately limited output.
4. **Operational provenance and empirical validation:** trust in an actual CI executor is governed by its operator; real-model effectiveness is assessed separately in future pilots. Neither is implied by claims 1–3.

No dashboard, README, CI gate, or release report may combine these into one undifferentiated `AQEF VERIFIED`/conformance badge. Specifically, three counters must be kept separate: `engineering_unit_checks`, `normative_cts_cases_executed`, and `reference_end_to_end_scenarios`. `NOT_RUN`, `NOT_APPLICABLE`, and mock-only checks cannot be counted as passed normative conformance cases.

### D2 — Make reproducible feasibility the immediate goal

A separately testable minimal AQEF engine, exercised by an independent CTS/harness runner, must demonstrate the complete five-layer core with: an explicit Contract and Scenario; execution; inspectable Evidence; Validator-then-Judge assessment and confidence/disposition handling; Quality Gate; Release Decision; report and manifest; positive, negative and unavailable/incomplete paths; and fail-closed reporting.

**No externally hosted AI or user-owned production AI system is required for this feasibility gate.** Scripted subject and Judge fixtures are permitted if their limitations and boundaries are clearly stated and the test oracle is independent of the implementation being tested. A scripted subject is not evidence of empirical accuracy or value on real-world AI workloads. A future live AI/RAG/Agent pilot is valuable but **not a prerequisite** for this feasibility demonstration.

Do not describe a bundled mock that shares its own expected-value logic with the assessor as independent proof. Keep the engine, runner, and observation oracle separable.

### D3 — Adopt consumer-managed CI trust

Organizations using AQEF choose and secure their CI/CD executors and define what sources of evidence they accept. AQEF requires explicit source/trust metadata, consistent observations, bounded evidence references, valid formats, and honest case outcomes; it does **not** require AQEF-maintained signing keys or a separate external attestation to demonstrate basic feasibility.

Define two profiles:
- **STANDARD / CONSUMER_MANAGED:** executor accepted by the consuming organization's documented trust policy, with validation of evidence structure, linkage, integrity and claims. It is **not** an independent authenticity guarantee; declaring trusted provenance cannot turn nonexistent observations into PASS.
- **ATTESTED / OPTIONAL:** additional cryptographic signatures and independently configured trust roots according to an organization's policy. Existing Ed25519 tools remain available as experimental optional components pending review.

The `REAL_SUT` validation path must no longer be rejected **solely because** independent cryptographic signing is absent when the adopted standard trust policy permits it. Any future change here must preserve strict observation/evidence checks and accurate scope labels.

### D4 — Draw a public product boundary without deleting history

- **Public documentation:** core AQEF specification, appendices, textual CTS, requirements inventory, harness-contract text, and other openly reusable explanatory material.
- **Potential reusable software:** schema/report validators, generic adapters, scripted fixtures and example runners, offered under explicitly defined software licensing after a rights review.
- **Internal engineering archive:** S1–S5 stage-specific implementations and regressions, C.1/C.2 finding closure history, historical CI workflows, and project-specific evidence recovery. These remain available and reproducible until a separate cleanup/change plan is approved.
- **Optional extensions:** human-review, plugin, CLI and attestation implementations and their tests. Scope is based on claimed implementation capabilities, not universal obligation.

Public visibility of internal engineering files does **not** imply that a consumer must run them, and does not automatically imply a claim of normative CTS conformance. Prefer keeping the current repository until a reference engine and stable module interfaces exist. A separate repository is a future option, **not a decision made here**.

### D5 — Explicitly separate documentation and software licensing

Keep **CC BY 4.0** as the intended license for author-owned textual AQEF specification and CTS prose. Adopt **separate software licensing as a policy direction**, with **Apache-2.0 as the preferred candidate** for eligible author-owned code and MIT as an alternative; **the specific software license grant and its file scope are NOT yet approved or applied**.

Before any grant or file reassignment: inventory ownership and contributions, identify dependencies/third-party material and generated artifacts, choose code/schema/fixture scopes, prepare `LICENSING.md` and file-level SPDX or appropriate notices, and obtain legal review where needed. Previous CC BY 4.0 grants are not retroactively withdrawn. Do not alter `LICENSE`, remove notices, or claim unsupported rights under this ADR.

### D6 — Keep CTS non-normative; align it to the current specification

The AQEF specification takes precedence over the CTS and harness contract. Track the 0.39 → 0.40 requirement delta; re-evaluate CTS case mappings, `Expected` predicates, capabilities and fixtures against the new normative content. Treat the existing '358 Tested requirement rows' as **specified/test-mapped coverage**, not proof that executable case runs have occurred. No full 0.40 conformance claim until appropriate implementation-specific tests and evidence exist.

### D7 — Rebaseline Stage C.2; do not rewrite its history

**PAUSE the old mandatory C.2.R2 operational-signing and C.2.R3 signed-bundle integration acceptance plan.** Its original security-driven exit criteria are to be reviewed against D1–D6; do not mark them PASS simply because they cease to be required for standard feasibility.

The prior 14 C.1 findings and C2-IA-01/02/03, R1-EX findings, reports, provenance limitations and historical verdicts remain part of the archival engineering audit record. **Zero historical findings are newly declared CLOSED by this ADR.** Any future supersession, scoped acceptance or closure requires a written mapping from the original concern to its revised obligation and supporting evidence, rather than silent status changes.

Keep Draft PR #2 **Draft**; no approval, merge, code deletion, CI deletion, key provisioning, license change, or certified-conformance claim follows automatically.

## Consequences and trade-offs

- **Benefit:** removes unnecessary trust infrastructure from the minimum technical feasibility claim; clarifies what green unit tests do and do not prove; enables fully local reproducible demos.
- **Cost:** a standalone reference implementation and a CTS v0.40 delta review must be built; compatibility of the existing adapters and harness will need work.
- **Residual risk:** trusting the consumer's CI does not protect against a compromised consumer runner; this is an explicitly accepted deployment trust boundary, not a claim that forgery is impossible.
- **Residual risk:** a scripted subject and Judge show architecture and testability but cannot measure real-world LLM utility, reliability, calibration or generalization. A later real-AI pilot is still needed for such claims.
- **Scope:** no change to the seven foundational principles or MUST/SHOULD/MAY language of AQEF's published Working Draft is authorized here.

## Execution plan, in decision order

| Priority | Deliverable | Acceptance evidence |
|---|---|---|
| P0 | ADR indexed and engineering claims taxonomy adopted | This ADR accepted in the branch; all new reports distinguish unit, normative CTS, and end-to-end counts |
| P1 | **CTS 0.40 Delta Matrix** | Inventory of added/changed requirements, specific missing case IDs/expectations, and honest untested status |
| P2 | **Minimal AQEF Reference Engine / Feasibility Demo** | Separate engine + harness; independently observed named CTS cases and successful good/bad/unavailable examples; report and manifest |
| P3 | **Verification realignment** | Consistent scoped provenance metadata, accurate counts, support for consumer trust policy; independent negative tests |
| P4 | **Software rights and license assignment review** | Author/contributor/third-party inventory, candidate Apache-2.0/MIT decision and explicitly scoped future grant |
| P5 | **CI & repository consolidation** | Traceable old→new migration with no regression coverage loss or historical audit erasure |
| P6 | **C.2 re-scoped exit review** | Formal accounting of old findings vs revised obligations; no automatic status promotion |

## Acceptance boundary

**Accepted now:** D1–D7 architectural policy and phased priorities.  
**Not accepted now:** any new software license grant; deletion or splitting; a certified implementation; unqualified historical closure; approval/merge of PR #2; mandatory external key infrastructure.  
**Next action:** P1 — CTS 0.40 Delta Matrix, followed by P2 — an independent minimum viable reference engine.
