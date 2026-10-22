# AQEF CTS Harness Contract

This directory contains the non-normative harness contract that accompanies the
[AQEF Conformance Test Specification](../README.md). It describes the interfaces
between a CTS runner, an adapter to an AQEF implementation under test, scripted
subject and Judge fixtures, evidence collection, manual review, and run reporting.

The Harness Contract is versioned separately from AQEF and the CTS. It does not
introduce requirements for an AQEF implementation or new CTS tests. In case of a
disagreement, the AQEF specification takes precedence for implementation requirements,
and the CTS takes precedence for test expectations. See
[harness-contract.md](harness-contract.md) for the contract version and supported
CTS/AQEF drafts.

## Contents

| Path | Purpose |
|---|---|
| [`harness-contract.md`](harness-contract.md) | Harness interfaces, reporting rules, and evidence requirements |
| [`schemas/`](schemas/) | JSON Schema 2020-12 definitions for harness and report records |
| [`examples/`](examples/) | Example records and evidence, including invalid examples for negative validation |
| [`fixtures/`](fixtures/) | Machine-readable recipes for CTS §2.7 postcondition fixtures |
| [`tools/validate.py`](tools/validate.py) | Validates the contract package or a CTS report with its evidence |
| [`tools/test_validate.py`](tools/test_validate.py) | Unit tests for the validator |

## Local validation

Requires Python 3 and `jsonschema` (with its dependencies):

```sh
python -m pip install jsonschema
python conformance-tests/harness/tools/validate.py
python conformance-tests/harness/tools/test_validate.py
```

Run these commands from the repository root. To validate a generated CTS run:

```sh
python conformance-tests/harness/tools/validate.py \
  --report REPORT.json \
  --manifest MANIFEST.json \
  --evidence-root EVIDENCE_DIRECTORY
```

These tools validate document structures, declared case outcomes, and evidence
consistency within their supported scope. A successful local validation does **not**
establish that any CTS case was executed against an independent AQEF implementation
or that an AI system conforms to AQEF.

This repository does not currently provide an automated GitHub Actions workflow for
these checks.

## License

The repository currently declares CC BY 4.0. Licensing terms specific to reusable
software tools have not yet been separately established.
