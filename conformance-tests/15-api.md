# 15. API Behavior

Tests in this section check behavior of the REST API (Appendix C) that belongs to no
single layer.

### CT-API-001 — List operations are paginated, the same way everywhere

- **Capability:** core
- **Requirement:** Appendix C §C.6: "List operations (GET on collection endpoints) MUST
  support pagination for unbounded collections"; "The pagination mechanism is
  implementation-defined ... but MUST be consistent across all endpoints."
- **Method:** Automated
- **Fixture:** F-MULTI, with `s-1`'s Contract given further schema Constraints, each a
  copy of the first, so that one Execution of `s-1` has more than `p` Results, where `p`
  is the smallest page size the implementation allows (the tester states `p`).
- **Action:** Execute `cts-suite` as many times as it takes for the Project to hold more
  than `p` Executions. As `P-APPROVER`, make governed changes (14.1) to `semantic-gate`'s
  `threshold`, alternating `0.9` and `1.0`, until the audit log holds more than `p`
  entries. With page size `p`, request `GET /projects/cts-base/executions`,
  `GET .../executions/{execution}/results` for one Execution of `s-1`, and
  `GET /projects/cts-base/audit` (as `P-ADMIN`, who holds `audit_read`). Follow each to
  its last page. Separately, request each
  collection unpaginated or with the largest page size allowed, as the reference set.
- **Expected:** Each of the three collections is returned in at least two pages, and the
  next page is reached the same way on all three (the same parameters and the same
  mechanism). For each, the items over all pages are exactly the reference set: none
  missing, none repeated, in a stable order.
- **Fails if:** Any of the three returns more than `p` items on one page or is not
  paginated; the mechanism differs between them; or an item is missing or repeated
  across pages.

### CT-API-002 — Deleting a Project does not silently delete its history

- **Capability:** core
- **Requirement:** Appendix C §C.8: "`DELETE /projects/{project}` MUST NOT be permitted
  while the Project has Baselines, Reports, or audit records unless the caller
  explicitly requests their retention or their deletion is separately, explicitly
  authorized"; Governance "MUST be able to distinguish which one a request is actually
  asking for."
- **Method:** Automated
- **Fixture:** F-BASELINED (2.7), so that `cts-base` has a Baseline and audit records.
- **Action:** As `P-ADMIN` (Section 14.1): (a) `DELETE /projects/cts-base` with no
  further statement; (b) the same, asking for the history to be deleted, without any
  separate authorization; (c) the same, asking for the history to be retained, in the
  form the implementation documents. After (c), query the retained Baseline and audit
  records through whatever the implementation documents for retained history.
- **Expected:** (a) and (b) are rejected and nothing is deleted. (c) is either rejected,
  with nothing deleted, or accepted. Where it is accepted, the Baseline and the audit
  records, including the record of the deletion itself, are still retrievable, and the
  record shows which kind of deletion was requested. (The specification forbids deletion
  without one of these conditions; it does not require an implementation to delete a
  Project once one is met.)
- **Fails if:** (a) or (b) deletes anything; (c) deletes anything while being rejected;
  an accepted (c) loses the Baseline or any audit record; or the record of an accepted
  (c) does not distinguish deleting the configuration from deleting the history.

### CT-API-003 — A published JSON Schema meets Appendix B

- **Capability:** core
- **Requirement:** Appendix B, introduction: "The MUSTs of B.1 and B.2 that say what 'a
  conformant JSON Schema' defines bind such an artifact: an implementation that
  publishes one MUST make it meet them."
- **Method:** Inspection
- **Fixture:** None.
- **Action:** Establish whether the implementation publishes a JSON Schema as the
  artifact Appendix B describes. A schema it publishes only as documentation of its
  API, and says so, is not that artifact. If it publishes one, compare it with B.1 and
  B.2.
- **Expected:** The schema defines every top-level type B.1 lists, and enforces for each
  the property constraints B.2 gives. If the implementation publishes no such schema,
  the outcome is `NOT_APPLICABLE` (1.2).
- **Fails if:** A published schema lacks a type B.1 lists, or a constraint B.2 gives.
