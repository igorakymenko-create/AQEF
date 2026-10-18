# MUST inventory — additions in AQEF Working Draft 0.37

Rows added to `must-inventory.md` for v0.37. Compiled by hand from the v0.37 change block, in the same form; line numbers are not given. IDs continue from R-0391 and are never reused. Rows of `must-inventory.md` whose text v0.37 revised keep their IDs: R-0277, R-0285, R-0306, R-0323, R-0364.

| ID | File | Section | Line | Kind | Text |
|---|---|---|---|---|---|
| R-0392 | appendix-a-yaml-specification.md | A.4 — Scenario | — | MUST | Scenario.dataset: The version MUST be given: a reference without one does not pin the rows an Execution draws from (Volume IV — Versioning). |
| R-0393 | appendix-a-yaml-specification.md | A.5 — Quality Contract | — | MUST | Constraint.dimension: MUST be given for a Custom Validator. |
| R-0394 | appendix-a-yaml-specification.md | A.12 — Release Decision | — | FIELD | Release Decision.id is REQUIRED |
| R-0395 | appendix-a-yaml-specification.md | A.12 — Release Decision | — | MUST | Release Decision.release_policy: The policy MUST be in force when the decision is recorded, list that Service Account, and cover the decision's Suite and Environment. |
| R-0396 | appendix-a-yaml-specification.md | A.12 — Release Decision | — | FIELD | Release Decision.id is REQUIRED (the GateResult table; the extractor names GateResult fields after section A.12, as in R-0243 to R-0249) |
| R-0397 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.id is REQUIRED |
| R-0398 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.project is REQUIRED |
| R-0399 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.suites is REQUIRED |
| R-0400 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.environments is REQUIRED |
| R-0401 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.service_accounts is REQUIRED |
| R-0402 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.approved_by is REQUIRED |
| R-0403 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | MUST | Release Policy.approved_by: MUST be a Person (Volume XII — Principals). |
| R-0404 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.approval_role is REQUIRED |
| R-0405 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | MUST | Release Policy.approval_role: MUST have `release_decide` Permission. |
| R-0406 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.approved_at is REQUIRED |
| R-0407 | appendix-a-yaml-specification.md | A.14 — Release Policy | — | FIELD | Release Policy.revoked_by is REQUIRED (MUST (if `revoked_at` is present)) |
| R-0408 | appendix-b-json-schema.md | B.3 — Cross-Type Validation Rules | — | MUST | Clause identity Volume VII A clause `id` MUST be unique within the Contract that declares it. |
| R-0409 | appendix-b-json-schema.md | B.3 — Cross-Type Validation Rules | — | MUST | Dataset reference Volume IV A Scenario's `dataset` and a Dataset's `base_dataset` MUST name a version (`name@version`) that resolves to a Dataset in the Project's `datasets` or one registered through Appendix C §C.3. |
| R-0410 | appendix-b-json-schema.md | B.3 — Cross-Type Validation Rules | — | MUST | Clause dimension Volume I, Ch. 6 A Constraint bound to a Custom Validator MUST declare `dimension`. |
| R-0411 | appendix-b-json-schema.md | B.3 — Cross-Type Validation Rules | — | MUST | Stale Results Volume I, Ch. 6 A Gate whose aggregate includes a Result produced under an Environment, or for a clause of a Contract, other than the one the evaluation's Snapshot captures MUST fail, with `stale_results`. |
| R-0412 | appendix-b-json-schema.md | B.3 — Cross-Type Validation Rules | — | MUST | Release policy Volume XII A Release Decision's `release_policy` MUST name a Release Policy in force when the decision is recorded, approved by a Person holding `release_decide`, that lists the acting Service Account and covers the decision's Suite and Environment. |
| R-0413 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | Review and re-assessment carry out Result Resolution (Volume I, Chapter 6); both MUST be rejected where it does not allow the resolution requested. |
| R-0414 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | The Principal MUST be a Person holding `review` and, where the clause names a `human_reviewer.role` (Appendix A §A.5), that Role. |
| R-0415 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | It MUST be rejected for the same Oracle configuration unless the Result is `oracle_unavailable`, and for an Oracle not requalified for every defect class in the Result's `invalidated_by` (Volume VIII). |
| R-0416 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | POST `/projects/{project}/release-policies` Approve a Release Policy (Appendix A §A.14). The Principal MUST be a Person. |
| R-0417 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | POST `/projects/{project}/release-policies/{policy}/revoke` Revoke a Release Policy. The Principal MUST be a Person. |
| R-0418 | appendix-c-rest-api-specification.md | C.7 — Result Response Shape | — | FIELD | Result Response Shape.recorded_at is REQUIRED |
| R-0419 | volume-i-architecture-concepts.md | Quality Gates | — | MUST NOT | A Gate MUST NOT pass on an aggregate that includes a stale Result, and records the reason as `stale_results` (Appendix A §A.12). |
