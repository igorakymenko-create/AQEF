# 15. API Behavior

Tests in this section check behavior of the REST API (Appendix C) that belongs to no
single layer.

### CT-API-001 — List operations are paginated, the same way everywhere

- **Capability:** core
- **Requirement:** Appendix C §C.6: "List operations (GET on collection endpoints) MUST
  support pagination for unbounded collections"; "The pagination mechanism is
  implementation-defined ... but MUST be consistent across all endpoints."
- **Method:** Automated
- **Fixture:** F-MULTI.
- **Action:** Execute `cts-suite` four times. Request, with the smallest page size the
  implementation allows: `GET /projects/cts-base/executions`, `GET .../executions/
  {execution}/results` for one Execution, and `GET /projects/cts-base/audit`. Follow
  each to its last page.
- **Expected:** Each returns its collection in pages, using the same mechanism (the same
  parameters and the same way of reaching the next page) on all three endpoints.
  Following the pages returns every item exactly once: 12 Executions in all.
- **Fails if:** Any of the three is not paginated; the mechanism differs between them;
  or an item is missing or repeated across pages.

### CT-API-002 — Deleting a Project does not silently delete its history

- **Capability:** core
- **Requirement:** Appendix C §C.8: "`DELETE /projects/{project}` MUST NOT be permitted
  while the Project has Baselines, Reports, or audit records unless the caller
  explicitly requests their retention or their deletion is separately, explicitly
  authorized"; Governance "MUST be able to distinguish which one a request is actually
  asking for."
- **Method:** Automated
- **Fixture:** As CT-REL-021, after its Action, so that `cts-base` has a Baseline and
  audit records.
- **Action:** As `P-ADMIN` (Section 14.1): (a) `DELETE /projects/cts-base` with no
  further statement; (b) the same, asking for the history to be deleted, without any
  separate authorization; (c) the same, asking for the history to be retained, in the
  form the implementation documents. After (c), query the retained Baseline and audit
  records through whatever the implementation documents for retained history.
- **Expected:** (a) and (b) are rejected and nothing is deleted. (c) is accepted; the
  Baseline and the audit records, including the record of the deletion itself, are
  still retrievable, and the record shows which kind of deletion was requested.
- **Fails if:** (a) or (b) deletes anything; (c) loses the Baseline or any audit record;
  or the record does not distinguish deleting the configuration from deleting the
  history.
