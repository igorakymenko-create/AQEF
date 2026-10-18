# AQEF Conformance Test Specification

**Status:** Working Draft 6. Tests for AQEF Working Draft 0.38; valid for 0.39, which
makes no normative change.

**License:** CC BY 4.0, as the specification.

## 0. Introduction

### 0.1 Purpose

The AQEF specification states what a conformant implementation MUST do. This document
states how to check it. Each test names the requirement it checks, the configuration to
start from, what to do, and what an implementation that meets the requirement does in
response.

This document contains no requirements of its own. Where a test and the specification
disagree, the specification is right and the test is wrong. Its normative words (MUST,
SHOULD, MAY) appear only inside quotations from the specification.

### 0.2 What a test result means

A test that passes shows that an implementation behaved as the specification requires
in that one situation. It does not show that the implementation is conformant: no finite
set of tests can. A test that fails shows that it did not. An implementation's
Conformance Statement (AQEF §10) says which capabilities it claims; this document says
how each claim can be checked, and a test report says how the checks came out.

No test in this draft has yet been run against an implementation. Tests may be revised
once they are.

### 0.3 Scope of this draft

This draft covers the non-negotiable core of AQEF Conformance (§10): the five logical
layers and the seven Fundamental Principles, and the path every conformant
implementation takes from a configuration to a Release Decision. It also covers every
scoped capability (§10, Conformance Statement), in Sections 20 to 26, each test tagged
with the capability's identifier; CI/CD tests are in Section 14. Section 90 shows,
requirement by requirement, what is covered.

### 0.4 Versioning

This document is versioned separately from the specification. Each version names the
specification version its tests were written against. A test is revised, not reused,
when the requirement it checks changes.

### 0.5 Structure

| Section | Content |
|---|---|
| 1 | Conventions: test format, outcomes, verification methods, test harness, isolation, test report |
| 2 | Fixtures: the base configuration, the scripted subject and Judge, postcondition fixtures, harness self-test |
| 10 | Configuration and Definition |
| 11 | Execution and Evidence |
| 12 | Assessment |
| 13 | Decision: aggregation, Quality Gates, Result Resolution |
| 14 | Release Decision and Governance |
| 15 | API behavior: pagination, deletion |
| 20 | Capability `human_review` |
| 21 | Capability `multi_judge` |
| 22 | Capability `seeded_controls` |
| 23 | Capability `action_boundary` |
| 24 | Capabilities `dataset:<source>` |
| 25 | Capabilities `plugins:<type>` |
| 26 | Capabilities `cli`, `sdk:<language>`, `reference_ui`, `test_type:<name>` |
| 90 | Traceability: requirement → test |

### 0.6 Changes from Working Draft 5

Working Draft 6 answers an external review of Working Draft 5 (20 findings). No
requirement of the specification changed; the tests did.

- **Outcomes.** **Fails if** is no longer a closed list: any departure from **Expected**
  fails a test (1.1, 1.2). A test that needs an operation Appendix C specifies and the
  implementation lacks now fails instead of passing (13.1). A test of an optional
  feature the implementation does not offer is `NOT_APPLICABLE`, not `PASS`.
- **Isolation.** Every test runs in a Project and a harness session of its own (1.6).
  States that tests used to take over from other tests are built as named postcondition
  fixtures (2.7), and the harness is checked before a run (2.8).
- **Fixtures.** `J-CATCH` fails both `Goodbye.` and `Bye now.`, as CT-SCT-008 requires.
  CT-CFG-016 uses `cts-len` instead of an undefined Validator.
- **Tests revised.** CT-ASM-009, CT-ASM-014, CT-ASM-016, CT-ASM-018, CT-ASM-019,
  CT-DEC-012, CT-DEC-013, CT-DEC-014, CT-DEC-018, CT-REL-018, CT-REL-032, CT-REL-036,
  CT-API-001, CT-API-002, CT-HRV-002, CT-MJG-006, CT-PLG-003, CT-PLG-005, CT-SDK-001,
  CT-SDK-002; and the fixtures of the tests that took over another test's state.
- **Tests added.** CT-CFG-025, one case per required configuration field of Appendix A,
  so that no row of Section 90 is left as Field.
- **Test reports** list every requirement whose tests did not run (1.7).

