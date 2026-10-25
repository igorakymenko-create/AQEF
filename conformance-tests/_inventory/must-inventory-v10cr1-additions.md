# MUST inventory — additions in AQEF 1.0-CR1

Rows added by 1.0-CR1, compiled from its text in the form of `must-inventory.md`; line numbers are not given. IDs continue from R-0453. Rows whose text 1.0-CR1 revised keep their IDs: R-0051 (what an enforced Action Boundary covers), R-0113 (an override in a Pipeline), R-0443 (Dataset mechanisms reserved).

| ID | File | Section | Line | Kind | Text |
|---|---|---|---|---|---|
| R-0454 | appendix-a-yaml-specification.md | A.2 — Environment | — | MUST | BoundaryEntry `target`: Pattern syntax is implementation-defined and MUST be documented by the implementation; matching is deterministic. |
| R-0455 | appendix-a-yaml-specification.md | A.8 — Dataset | — | MUST | `source`: `synthetic` is reserved: it is specified in a later version, and an implementation MUST reject a Dataset with `source: synthetic` when the configuration is loaded. |
| R-0456 | volume-iv-dataset-engine.md | Generated Datasets | — | MUST | A generation that fails, or whose output includes anything that is not a valid Row, MUST produce no Dataset version, and the implementation reports the failure. It MUST NOT repair, complete, or drop rows to make a version out of such output. |
