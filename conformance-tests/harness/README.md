# AQEF CTS Harness Contract

The interfaces of the test infrastructure that runs the AQEF Conformance Test
Specification: the runner, the adapter to the implementation under test, the scripted
subject and Judge, evidence, manual review, and the run report.

This is a separate, non-normative document, versioned on its own. It adds no
requirement to AQEF and no test to the CTS: where it disagrees with either, they are
right. Its normative words bind a harness, an adapter, or a runner, never an AQEF
implementation. The version and the CTS draft it serves are stated at the top of
`harness-contract.md`.

| Path | Content |
|---|---|
| `harness-contract.md` | The contract |
| `decisions.md` | How each audit finding was decided |
| `stage-c-readiness.md` | Open questions; criteria for Stage C |
| `schemas/` | JSON Schema 2020-12 for every envelope and record |
| `examples/` | Valid examples; `examples/invalid/` must be rejected |
| `fixtures/` | Recipes for the postcondition fixtures of CTS 2.7 |
| `tools/validate.py` | Checks the package and its agreement with the CTS; verifies a run's report with its evidence |
| `tools/test_validate.py` | Unit tests of every check |

To check the package: `pip install jsonschema`, then, from the repository root:

```
python3 conformance-tests/harness/tools/validate.py
python3 conformance-tests/harness/tools/test_validate.py
```

To verify a run: `validate.py --report REPORT --manifest MANIFEST --evidence-root DIR`.
The workflow `.github/workflows/cts-harness.yml` runs both checks on every change.

## License

CC BY 4.0, as the specification.
