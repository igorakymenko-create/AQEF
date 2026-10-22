# AQEF Repository & Verification Architecture Review
**Date:** 2026-10-22  
**Status:** Architecture review / proposed decisions; **not** an implementation approval or certification.  
**Source:** `igorakymenko-create/AQEF`, Draft PR #2, branch `stage-c2-traceability-hardening`, audited HEAD `bf701e8b9eed187fcf682a1f0b4069e70a6ddd2e`.  
**Scope:** Repository tree; normative purpose/scope/conformance; current CTS/harness/selected mock implementations; stage C.1/C.2 audits and CI; current license declarations; public licensing guidance. This is a **group-level architecture audit**, not a line-by-line audit of all test methods and not independent legal advice.

## Executive decision
**REFRAME AND PAUSE C.2.R2/R3 pending architecture acceptance.** AQEF needs to establish reproducible **feasibility of its five-layer engineering lifecycle**, not prove the trustworthiness of every adopter's CI. The project presently mixes (a) the AQEF text specification, (b) the non-normative CTS test specification, (c) a harness contract and reusable validator, (d) stage-specific mock engineering unit tests, (e) internal audit closure and (f) optional infrastructure provenance/signature mechanics.

None of these is inherently worthless, but they must not be merged into one blanket 'AQEF verified' claim. Preserve history; don't delete anything or alter license grants before ownership and consumer-scope review.

## 1. Observable inventory and baseline
- 265 tracked files at audited HEAD (GitHub recursive tree, not truncated); 29 GitHub Actions workflow files.
- Historical C.1 regression baseline: **423 Python unittest checks in 16 named suites**; these verify selected mock and engineering components, **NOT 423 normative CTS cases executed against an independent implementation**.
- C.2: **99 methods named `test_*` across 12 Python test files** by source inspection at audited HEAD. Counts are inventory statistics, not a claim of independently executed normative CTS cases.
- CTS `90-traceability.md` labels **431 requirement inventory rows**: 358 'Tested', 44 'Restates', 29 'Not testable', 0 'Not yet covered'. This is **planned traceability coverage** and cannot be equated to implemented/executed evidence.
- Main specification and `front-matter/00-document-status.md`: AQEF Working Draft **0.40**, explicitly *not for conformant implementation*. `conformance-tests/00-introduction.md`: CTS WD7 for **0.38**, compatible with 0.39 by stated lack of normative changes. `harness/harness-contract.md`: contract 0.4 for 0.38–0.39. Normative changes in 0.40 (clean seeded controls, judge admission, gate admission policy) are not yet traced in the published CTS.
- `conformance-tests/00-introduction.md` itself states no tests in that draft have been executed against an implementation; mock/unit tests in the repository do not contradict that limitation.
- `front-matter/06-scope.md`: native CI/CD platform primitives are outside AQEF. `front-matter/10-conformance.md`: conformance concerns a **claimed AQEF implementation**, *not* an AI subject under test, a person, or an organization.
- GitHub's PR remains Draft. The original PR title `Stage C.2.1 — Case-level execution traceability` no longer summarizes its actual content.

## 2. Four distinct assurance targets
| Target | Question | Evidence needed | Owner |
|---|---|---|---|
| A. Specification consistency | Are requirements coherent and implementable? | Normative/version review, examples, schema checks | AQEF maintainers |
| B. Harness correctness | Can tests detect good and deliberately broken behavior, with honest results? | Mock positive/negative, independent oracles, schema/report checks | AQEF CTS developers |
| C. AQEF feasibility | Can a **separate minimal AQEF implementation** execute a complete Definition → Execution → Evidence → Assessment → Decision loop? | End-to-end runner, contracts, observations, gates, report | AQEF reference project |
| D. CI/source authenticity | Does an adopter accept its execution environment's provenance/security? | Organization-defined trust policy, optional attestations | Adopter / deployment owner |

A green Python unit suite primarily contributes to target B, **not** proof of C or D. Nor does proving C establish empirically useful AI quality performance (a later, separate field validation).

## 3. Path disposition: proposed product boundary
| Path or family | Consumer value | Proposed disposition | Conditions |
|---|---|---|---|
| `front-matter/`, `part-*/`, `appendices/`, `index.md` | Canonical spec | **KEEP PUBLIC** | CC BY 4.0 for documentation; version consistency |
| `conformance-tests/00-26*.md`, `90-traceability.md`, `_inventory/` | Independent test definitions, traceability | **KEEP PUBLIC** | Non-normative CTS; update coverage for v0.40; distinguish drafted from executed |
| `conformance-tests/harness/harness-contract.md`, schema definitions, fixture descriptions | Portable harness interface | **KEEP PUBLIC** | Clearly distinguish harness obligations from requirements on implementation |
| `conformance-tests/harness/tools/validate.py` and its tests | Reusable reporting/evidence checks | **KEEP AS SOFTWARE / REFACTOR** | Maintain generic, implementation-neutral input/outputs |
| `harness/s02_harness/` | Scripted subject/Judge, synchronization, fixtures | **KEEP AS INTERNAL/REFERENCE SUPPORT** | Extract portable harness interface; document fixture limits |
| `s1_configuration`, `s2_*`, `s3_*`, `s35_*`, `s355_closure` | Local mock component tests and development experiments | **KEEP HISTORIC; CONSOLIDATE LATER** | No claim of third-party conformance; avoid hard-coded mock imports in reusable adapters |
| `s4_cli`, `s4_plugins`, `s4_human_review` | Demonstration of **claimed optional capabilities** | **KEEP OPTIONAL PROFILES** | No unconditional gate on projects that don't claim them; no self-authored reference dictionary treated as independent published inventory |
| `s5_reporting` | Honest report/manifest generation | **KEEP AND REUSE** | Preserve distinction between mock evidence and real observations |
| `stage_c_closure/`, `stage_c2/r1_*.py`, `r11_*`, `r12_*`, `r13_*` | Internal provenance/findings history | **MOVE TO INTERNAL AUDIT CATEGORY (FUTURE)** | Preserve all prior statuses; do not require closure of historic mock findings for every adopter |
| `stage_c2/traceability.py`, `inventory_binding.py`, `regression_accounting.py` | Execution identity, honest count, evidence integrity | **REFACTOR TO REUSABLE CORE VALIDATION** | Trust as explicit input/policy; don't reject REAL_SUT solely for missing vendor attestation; avoid historic fixed 423 count |
| `stage_c2/attestation.py`, `operational_signing.py`, `r2_bundle.py` and trusted-signing workflow | Authenticated artifact provenance | **OPTIONAL PROFILE; NO MANDATORY EXIT GATE** | Keep source and tests while reviewing compatibility; no key setup needed for standard feasibility |
| `.github/workflows/cts-*.yml` (29 files) | CI regression and development history | **RETAIN, THEN CONSOLIDATE** | Target a compact core check, feasibility demo, optional extensions, optional attestations; do not remove unique checks accidentally |
| `LICENSE`, license language in READMEs | Current attribution grant | **REWORK SCOPE PROSPECTIVELY** | No silent retrospective relicensing; review rights and prior distribution |

**Public availability is not the same as conformance requirement.** Reusable implementations can be published openly, but should carry their own explicit software terms. A future separate reference repository is optional, not a prerequisite; splitting now risks breaking links, historical evidence and workflows before product boundaries stabilize.

## 4. Findings, severity, disposition
### RV-01 / HIGH — verification claim confusion
423 accepted regression unittests and 99 C.2 test methods are engineering checks; published CTS status table says 358 requirements 'Tested', which is not proof they were executed against a separate AQEF implementation. **Action:** three independently labeled counters: `engineering_unit_checks`, `normative_cts_cases_executed`, `reference_end_to_end_scenarios`. Fail publication if categories are merged or `NOT_RUN` counted as PASS.

### RV-02 / HIGH — minimal independent reference implementation is missing
The current `S1Adapter` directly imports `MockSUT` and supports only `load_config`; `s35_integration/pipeline.py` is a unified **mock** and scenario-specific. S5 already supports explicit observation-based reports. **Action:** implement an independent miniature AQEF engine behind a generic adapter. Use existing scripted subject/Judge; run a complete five-layer loop, with positive and fault-injected negative cases. No external AI service required for feasibility.

### RV-03 / HIGH — specification/test-version drift
Spec 0.40 versus CTS 0.38–0.39, contract 0.4. **Action:** create normative delta inventory for 0.40; update source references, capability claims, and identify unimplemented coverage before claiming v0.40 conformance.

### RV-04 / HIGH — ambiguous mixed-media licensing
Top-level CC BY 4.0 and CTS READMEs imply common license over documentation and Python code; no separate code license is declared in tree. CC recommends a dedicated software license. **Action:** inventory ownership of each code/fixture/workflow, check third-party dependencies and any contributors, then **prospectively** designate code under Apache-2.0 or MIT with precise coverage and SPDX tags; retain CC BY 4.0 for written spec/CTS. Existing CC-BY permissions cannot be silently withdrawn.

### RV-05 / MEDIUM — user-owned CI trust conflated with AQEF semantics
C.2 `inventory_binding.py` rejects `REAL_SUT` when external origin attestation is missing; R2 signing requires controlled keys. **Action:** separate `consumer_trusted_executor` (standard profile; declared trust policy), and optional independently attested provenance. Both still require truthful, internally consistent observations. An SHA-256 entry alone cannot authenticate the author of both file and hash.

### RV-06 / MEDIUM — historic audit becoming consumer product requirement
14 historical C.1 findings, R1 mappings, and signature closure thresholds serve internal audit accountability; **0/14 finding closures** remain externally demonstrated. **Action:** retain historical OPEN state in internal audit, but do not block an unrelated adopter's local AQEF evaluation on this historic administrative condition. Do not declare old finding closed solely because architecture scope changed.

### RV-07 / MEDIUM — coupled adapters/expected predicates
Mock-specific adapter imports and selected S4 CLI dictionary assertions weaken portability and independence. **Action:** extract generic transport/adapter contract, review normative expected predicates against CTS text, and demonstrate one independent good implementation plus at least one deliberately faulty implementation.

### RV-08 / MEDIUM — CI maintenance/traceability sprawl
29 action workflow definitions and successive one-off slice stages increase cost/noise. **Action:** migration after test mapping with no lost coverage and no weaker failure semantics. CI hygiene != normative conformance.

### RV-09 / LOW — project status/PR metadata needs refresh
PR #2 title/body centered on C.2.1; conformance draft status explicitly warns against building a certified conformant product. **Action:** update messaging only after architecture decision.

## 5. Feasibility demonstration without live AI
**Important separation:** The CTS **SUT is an implementation of AQEF**, not the generative AI system being evaluated by AQEF. For a reference engine, existing scripted subject and judge are sufficient to test orchestrated behaviors. A second product-facing example can use scripted non-deterministic responses and later be swapped with a real RAG+Agent; it must not be advertised as empirical validation of real-world LLM quality.

**Suggested minimum independent reference contract (not a new normative demand):**
1. Declare `aqef_version`, `capabilities`, `implementation_id`, scripted test profile, and explicit trust/observation source.
2. Configure one Project/Environment/Suite/Scenario with Contract and blocking Gate; change versioned contract.
3. Run a scenario with scripted subject behavior, record Execution and a readable immutable Evidence object.
4. Apply deterministic Validator before the scripted Judge, compute Result disposition/confidence explicitly.
5. Evaluate Gate and record a Release Decision; produce native CTS-compatible report, including explicit provenance and all four outcomes (`PASS`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`) as applicable.
6. Inject a wrong response, a missing evidence object and/or an unavailable judge; show appropriate non-success outcomes. Assert assessor is independent of mutated subject.
7. Verify a small, preselected **named** subset of core CTS cases against this separate engine, with a real report/manifest and counts **separate from Python unittest results**.
8. Document limitations: mock subject/Judge, unproven external AI performance, no 0.40 full conformance, adopter-owned CI trust.

**Minimal entry/exit gate:** Reproducible clean checkout & dependency install; independently executed named CTS cases; positive + negative + unavailable-capability paths; an independently checked report/manifest; explicit untested count and known limitations; no secrets, signing service or external API required. L3 live-model pilot remains a follow-on validation, not a blocker to L2 feasibility.

## 6. License / distribution decision proposal
- **Documentation:** `CC-BY-4.0` for the original AQEF specification, CTS *prose*, diagrams and associated prose.
- **Software:** propose `Apache-2.0` for *eligible author-owned* Python, CI workflows and reusable reference components, after ownership/third-party review. Apache has an explicit contributor patent grant (scope limited by its terms); MIT is a simpler viable alternative.
- **Mixed files:** JSON schemas, fixtures, test vectors, generated reports and PDF/source assets require explicit ownership and per-file policy; don't assume all are software or all are CC docs.
- **Recommended packaging:** a `LICENSING.md` scope table; `LICENSES/CC-BY-4.0.txt`, `LICENSES/Apache-2.0.txt` if adopting REUSE conventions; file-level SPDX headers or appropriate `.license` sidecars for non-commentable binaries. Preserve notices and attribution. Verify existing GitHub public history and any external contributions before authorizing a new grant.
- **Current grant and future grant:** CC BY 4.0 is not invalid simply because it's suboptimal for code; prior grants remain effective for already licensed copies. Author-controlled works can be offered with an *additional* software license, but don't assert rights over third-party material.
- **Publication packaging:** preferred now: single repository with visible categories `specification`, `cts`, `tools`, `examples`, `internal-audits` as conceptual boundaries **without immediate moving files**. Revisit dedicated reference repo only after a working example exists.

Supporting policy sources:
- https://creativecommons.org/faq/ (Creative Commons advises against using CC for software)
- https://www.apache.org/licenses/LICENSE-2.0 (Apache 2.0 full terms)
- https://reuse.software/spec/ (mixed-license per-file metadata)
- https://spdx.dev/learn/handling-license-info/ (SPDX IDs and compound expressions)

## 7. Decision sequence and acceptance
| Order | Next activity | Tangible deliverable | Exit criterion |
|---|---|---|---|
| 0 | Accept/update this review | Architecture decision record (ADR) and claim taxonomy | Explicit approvals for public/internal boundary, optional trust, and no real-AI requirement for L2 |
| 1 | Version alignment | 0.39→0.40 normative delta + updated CTS traceability plan | No unsupported claims of v0.40 coverage |
| 2 | Minimal feasibility fixture | Independent AQEF reference implementation with scripted subject+Judge | End-to-end Definition→Decision, good/bad/missing outcome distinctions, honest report |
| 3 | Verification realignment | Three separate counters and reproducible CI job | Named CTS cases executed, no unit-test-to-CTS promotion |
| 4 | License scoping | Rights inventory, proposed licenses and file-level assignment | No unknown third-party code retroactively assigned; legal review as appropriate |
| 5 | Repository consolidation | Migration map for stage test code & workflows | No regression loss, links/history preserved, existing audits still accessible |
| 6 | Revisit Stage C.2 exit | Re-scoped audit to new bounded architecture | An explicit, signed-off decision about old findings; no silent status promotion |

## 8. Actions deferred — not performed by this review
No code deletion, file relocation, CI rewiring, relicense, operational signing, secret creation, PR merge or historical finding status promotion. Keep PR #2 Draft. R2/R3 as previously framed are **on hold**, with earlier audit records preserved.

**Review recommendation:** Prioritize a minimal separately testable AQEF reference engine and source-to-CTS v0.40 alignment, while making authentic CI attestation an opt-in deployment profile. Revisit license declarations before distributing test code as a reusable software package, but do not make external keys a prerequisite for feasibility.
