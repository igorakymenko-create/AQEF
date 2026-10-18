# MUST inventory — additions in AQEF Working Draft 0.38

Rows added for v0.38, compiled by hand from the v0.38 change block in the form of `must-inventory.md`; line numbers are not given. IDs continue from R-0419. Rows whose text v0.38 revised keep their IDs: R-0074, R-0078, R-0411, R-0414, R-0415.

| ID | File | Section | Line | Kind | Text |
|---|---|---|---|---|---|
| R-0420 | appendix-a-yaml-specification.md | A.5 — Quality Contract | — | FIELD | Quality Contract.escalate_to is REQUIRED (MUST (if `on_timeout` is `escalate`)) |
| R-0421 | appendix-a-yaml-specification.md | A.5 — Quality Contract | — | MUST NOT | Quality Contract.escalate_to: MUST NOT appear otherwise. |
| R-0422 | appendix-b-json-schema.md | B.2 — Property Constraints | — | MUST NOT | `escalate_to` is REQUIRED when `on_timeout` is `escalate` and MUST NOT appear otherwise. |
| R-0423 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | POST `.../executions/{execution}/seeded-controls/{scenario}/confirm` Record a Human Reviewer's confirmation that the planted defect is present in the Evidence the Oracle received, for a control with `confirmed_by: human_reviewer` (Volume VIII). The Principal MUST be a Person. |
| R-0424 | appendix-c-rest-api-specification.md | C.3 — Operations by Resource | — | MUST | POST `/projects/{project}/requalifications` Record that an Oracle configuration is requalified for a defect class (Volume VIII — Requalification). Body names the `oracle`, the `defect_class`, and the Seeded Control Results it rests on. MUST be rejected unless each named control is of that class, was `caught` by that Oracle configuration, and is not a control any Oracle missed in a run whose Results the requalification will be used to re-assess. |
| R-0425 | appendix-c-rest-api-specification.md | C.7 — Result Response Shape | — | FIELD | Result Response Shape.assertions is REQUIRED (MUST (Judge Result over several assertions); absent otherwise) |
| R-0426 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.id is REQUIRED |
| R-0427 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.generated_at is REQUIRED |
| R-0428 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.scope is REQUIRED |
| R-0429 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.gates is REQUIRED |
| R-0430 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.metrics is REQUIRED |
| R-0431 | appendix-c-rest-api-specification.md | C.10 — Report Response Shape | — | FIELD | Report Response Shape.signals is REQUIRED |
