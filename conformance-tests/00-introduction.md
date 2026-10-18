# AQEF Conformance Test Specification

**Status:** Working Draft 5. Tests for AQEF Working Draft 0.38; valid for 0.39, which
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
| 1 | Conventions: test format, outcomes, verification methods, test harness |
| 2 | Fixtures: the base configuration and the scripted subject and Judge |
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
