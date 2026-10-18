# AQEF Conformance Test Specification

Tests that check whether an implementation of AQEF meets the requirements it claims in
its Conformance Statement (AQEF §10).

This is a separate, non-normative document. It contains no requirements of its own:
where a test and the specification disagree, the specification is right and the test is
wrong. It is versioned on its own; the status line of `00-introduction.md` states which
draft this is and which version of the specification its tests were written for.

## Contents

| File | Content |
|---|---|
| `00-introduction.md` | Purpose, what a test result means, scope, versioning |
| `01-conventions.md` | Test format, outcomes, verification methods, test harness |
| `02-fixtures.md` | Base configuration, scripted subject and Judge |
| `10-…` to `15-…` | Tests of the non-negotiable core |
| `20-…` to `26-…` | Tests of scoped capabilities, one section per capability |
| `90-traceability.md` | Every requirement of the specification, and the tests that check it |
| `_inventory/` | The requirement inventory the traceability refers to (`R-nnnn`) |

Each release of the specification carries this document as its own PDF, built from the
numbered files above. This README and `_inventory/` are not part of the PDF.

## License

CC BY 4.0, as the specification.
