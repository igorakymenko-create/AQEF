# 7. Intended Audience

**Status:** confirmed (v0.1).

This specification addresses two distinct audiences, and conflating them is a common way
a document like this gets misread: those who *use* an AQEF-conformant implementation to
test AI systems, and those who *build* one.

## Users

**AI Quality Engineers** author Scenarios and Quality Contracts (Volume VII, VIII),
design Suites, and interpret Reports (Volume XI) — the primary audience for Part I
through Part III.

**AI/ML Engineers** building the system under test need to understand what an
Environment (Volume II) captures about their system's configuration, which Quality
dimensions (Chapter 2) their system is assessed against, and what a failing Quality Gate
(Chapter 6) means for their release — without necessarily authoring Contracts
themselves.

**Governance, Compliance, and Risk teams** are the direct audience for Volume XII: Teams,
Roles, Permissions, Approval Workflow, Audit, Traceability, and Compliance exist
specifically to give this audience a mechanism, not just a policy document.

**Engineering leadership and Release Managers** consume Reports, Dashboards, and KPIs
(Volume XI) and act on Release Decisions (Chapter 6) without necessarily engaging with
the mechanism that produced them.

**CI/CD and DevOps engineers** integrate AQEF into a deployment pipeline (Volume XIII)
and consume a Quality Gate's status as a native pipeline primitive.

## Implementers

A separate audience builds AQEF-conformant tooling itself — a Minimal or Enterprise
Engine (Volume XVII), the REST API and SDKs (Volume XIV), a Plugin Architecture
extension point (Volume XVI) — and reads this specification as a normative bar to
satisfy (Conformance, §10), not as end-user documentation. Most of Part II, Part IV, and
Part V is written primarily for this audience; a Quality Engineer authoring a Contract
does not need to know how the Execution Engine (Volume III) is internally implemented,
only that it satisfies what Part II specifies.

---

No single reader needs the whole document at once. Which Volumes matter to a given
reader follows directly from which of these two audiences, and which role within it,
they belong to — the Master Index groups Volumes by Part precisely so a reader can find
their own entry point rather than starting at Volume I regardless of role.
