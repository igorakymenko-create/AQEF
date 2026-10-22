# P1 — CTS v0.40 Normative Delta Matrix

**Date:** 2026-10-22  
**Status:** REVIEW COMPLETE — normative delta identified; CTS implementation and full v0.40 conformance NOT verified.  
**Authority:** [ADR-0001](../docs/adr/ADR-0001-verification-scope-consumer-managed-trust.md)  
**Baseline:** CTS Working Draft 7 / AQEF v0.38–0.39, Harness Contract 0.4.  
**Target:** AQEF v0.40 (Working Draft — not yet a conformance certification target).  
**Reviewed PR HEAD before work:** `9d1942109d24b4315f68ef156f95278a235cfaba`.

## Method and limitation

Compared the published v0.40 revision-history entry with operative v0.40 passages in Volume VI, VIII, XI and Appendices A/B/C; searched the CTS WD7 test definitions in sections 12, 13, 22 and its `90-traceability.md` for new constructs. These are **semantic requirement clusters**, not independently assigned new `R-nnnn` IDs; existing `R-nnnn` inventory covers an earlier specification and must not be silently interpreted as exhaustive coverage for 0.40. No claim of a complete old-vs-new line-level diff across every volume is made here; follow-up full inventory extraction and cross-reference validation remain required.

## Findings summary

| ID | v0.40 change or normative behavior | Source | Existing CTS coverage | Delta disposition | Proposed test work |
|---|---|---|---|---|---|
| P1-01 | SeededControlConfig `kind=defect\|clean`, default defect, clean carries no planted defect or difficulty prior; confirm absence | Volume VIII; Appendix A §A.4; B | CT-SCT-001/002 cover historical defect controls only | **GAP** | Add CT-SCT-009: schema acceptance/rejection and default handling for both kinds |
| P1-02 | Clean controls result in `passed` or `false_alarm`, not `caught/missed`; without confirmed absence outcome `invalid` | Volume VIII; Appendix C §C.3 | CT-SCT-003/004/005 assumptions focus planted defects | **GAP** | CT-SCT-010: three-way result semantics and confirmation methods; no fake PASS |
| P1-03 | `false_alarm` has miss-equivalent consequences: class invalidation, skip/halt, quorum, effective Results, resolution and blocked gate reason `seeded_control_false_alarm` | Volume VIII; Appendix A §A.12; B; C §C.3 | CT-DEC-015/017/018 test older `missed` branches only | **GAP** | CT-DEC-024..026: class-scoped false alarm, full-run mode, gate reasons and downstream panel behavior |
| P1-04 | Clean control is excluded from aggregation like all seeded controls; correctly passed clean control leaves ordinary Results unaffected | Volume VIII; Appendix C | CT-DEC-016 covers caught defect control | **PARTIAL / EXTEND** | Add CT-DEC-027, pass-clean exclusion and no invalidation |
| P1-05 | Requalification after false alarm must pass fresh clean controls (and after dual failure fresh controls of both kinds) | Volume VIII; Appendix C §C.3 | CT-SCT-008 tests historic missed-defect case | **GAP** | CT-SCT-011: requalification preconditions, fresh clean controls, wrong-kind rejection |
| P1-06 | Project SHOULD maintain at least one clean control per gate-feeding Judge; reviewer SHOULD NOT know which items are controls where practical | Volume VIII | CTS records normative SHOULD but non-observation may not be nonconformance | **ADVISORY / REVIEW** | Inspection/declaration checklist and reasoned deviation; do not make SHOULD a blanket MUST |
| P1-07 | Judge Admission based on human-labelled versioned Reference Set, raw + named chance-corrected agreement, sample count/distribution, explicit threshold, immutable record | Volume VI Admission; Appendix C §C.3 | No `Admission` or `admitted` tests in CTS WD7 | **GAP** | CT-ADM-001..003: record shape, validation, immutability, reference set versions |
| P1-08 | Admission record creation by Person, `review` permission; threshold/agreement must agree with `admitted`; GET available | Appendix C §C.3 Admission | No Admission REST tests | **GAP** | CT-ADM-004..005: auth principal, mismatch rejection, recorded value and readback |
| P1-09 | Judge admission tied to exact Judge configuration; panel admission iff every Judge admitted | Volume VI | No matching CTS coverage | **GAP** | CT-ADM-006: changed config invalidates reuse; panel mixed-admission coverage |
| P1-10 | Optional `require_admitted_judges` Gate (default false): unadmitted Judge blocks; reason `judge_not_admitted`; Basis accounts accordingly | Volume VI; Appendix A §A.10/12; B; C §C.7 | CT-DEC-004..009 handle other gate failures, not admission | **GAP** | CT-DEC-028..029: true/false/default, multiple applicable reasons and Basis |
| P1-11 | Every Report includes unadmitted Judges in scope even without gate admission requirement | Volume VI; XI; Appendix C §C.10 | Existing reporting tests do not check `unadmitted_judges` | **GAP** | CT-REL-0XX: explicit population/empty array/cross-scope rules; allocate next free ID after inventory check |
| P1-12 | Reference Set reviewer independence, blinding/consensus and exposure guidance use SHOULD | Volume VI Admission | No admission review protocol | **ADVISORY / REVIEW** | Human review inspection checklist; explain what cannot be decided automatically; preserve deviation semantics |

**Summary:** 12 semantic clusters: **9 GAP, 1 PARTIAL/EXTEND, 2 ADVISORY/REVIEW**. These are **not** 12 new normative MUST statements or 12 normative CTS cases. Cluster-level granularity is intentional; each may require multiple individually named cases.

## Version/inventory alignment

1. `front-matter/00-document-status.md` and `README.md` identify AQEF Working Draft **0.40**.
2. `front-matter/01-revision-history.md` describes v0.40 as introducing clean seeded controls, Judge Admission, `require_admitted_judges`, `judge_not_admitted`, and report additions.
3. `conformance-tests/00-introduction.md` asserts WD7 tests target **0.38** and are valid for **0.39**, not 0.40. `harness/harness-contract.md` targets 0.38/0.39.
4. `conformance-tests/90-traceability.md` counts **431 requirement inventory rows**, with 358 `Tested`, 44 `Restates`, 29 `Not testable` as **test-definition mapping**, not executed normative case evidence. Its status must not be propagated to new v0.40 MUSTs without rewriting the inventory.
5. Appendix B `seeded_control_false_alarm` and `judge_not_admitted` additions need actual machine-readable schema and fixture review; presence in narrative text is not proof that current harness JSON schemas accept them.

## Proposed implementation phases (not executed in P1)

| Phase | Work | Exit criterion |
|---|---|---|
| P1a | Extract 0.40 normative deltas into fresh requirement inventory with stable IDs, reconcile Appendix A/B/C | Every new/changed MUST traced to owning normative paragraph and test definition, or explicitly marked `NOT_YET_COVERED` |
| P1b | Define new CTS case texts and outcomes for CT-SCT-009..011, CT-DEC-024..029, CT-ADM-001..006 plus uniquely allocated reporting IDs | Fixture, Action, Expected, Fails if, and Capability specified for every case |
| P1c | Update harness contracts/schemas/fixtures for `kind=clean`, `false_alarm`, admission resources and gate reasons | Schema positive/negative checks, no old fixture regressions |
| P1d | Extend CTS §90 traceability and compatibility statement | Coverage reflects source version 0.40 and clearly distinguishes unexecuted cases |
| P1e | Prepare independent reference engine readiness profile | Minimal L2 feasibility may exercise the five-layer core without claiming all optional v0.40 capabilities |

## Explicit scope and normative handling

- The **five-layer core** remains the immediate demonstration objective under ADR-0001. `seeded_controls`, `multi_judge` and `human_review` are scoped capabilities under §10. The new optional gate `require_admitted_judges` is required when offered/enabled, not necessarily in the minimum feasibility slice.
- `SHOULD` guidance is recorded, not automatically converted into failure of conformance absent a justified deviation.
- Do **not** treat scripted subject/Judge outcomes, green Python tests, or draft CTS 'Tested' labels as verified LLM quality or full implementation conformance.
- The 0.40 normative document is explicitly a Working Draft not yet approved for claims of certified conformance.

## Decision

**P1 DELTA DISCOVERY: PASS (scoped document review).**  
**CTS v0.40 coverage closure: NOT ACHIEVED.**  
**Recommendation:** perform P1a–P1d in a dedicated CTS update before any v0.40 coverage claim; develop P2 minimal independent feasibility fixture against the five-layer core in parallel only if its unsupported capabilities are explicitly labelled. Preserve all pre-existing C.1/C.2 audit findings unchanged and keep Draft PR #2 unmerged.
