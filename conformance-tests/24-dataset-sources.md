# 24. Capability: Dataset Sources

Tests in this section apply to an implementation whose Conformance Statement claims
`dataset:<source>` for the source named in each test (§10). For a source it does not
claim, the test is `NOT_APPLICABLE`. Static Datasets are core (Sections 10 and 11).

### CT-DSR-001 — A Generated Dataset declares how it is generated

- **Capability:** `dataset:generated`
- **Requirement:** Appendix A §A.8: `generator` is required when `source` is
  `generated`; GeneratorConfig `model` and `instruction` are required.
- **Method:** Automated
- **Fixture:** Three variants of a Dataset `ds-gen` (version `1.0.0`, `source:
  generated`) in the Project's `datasets`: (a) no `generator`; (b) a `generator` with no
  `model`; (c) a `generator` with no `instruction`.
- **Action:** Load each variant.
- **Expected:** All three rejected.
- **Fails if:** Any is loaded.

### CT-DSR-002 — A Production Replay Dataset declares its capture

- **Capability:** `dataset:production_replay`
- **Requirement:** Appendix A §A.8: `capture` is required when `source` is
  `production_replay`; CaptureConfig `source`, `date_range`, `sampling`, `sample_size`,
  and `anonymization` are required.
- **Method:** Automated
- **Fixture:** Six variants of a Dataset `ds-replay` (version `1.0.0`, `source:
  production_replay`): (a) no `capture`; (b)–(f) a complete `capture` with one of its
  five fields removed.
- **Action:** Load each variant.
- **Expected:** All six rejected.
- **Fails if:** Any is loaded.

### CT-DSR-003 — Generating rows again makes a new version, never changes an old one

- **Capability:** `dataset:generated`
- **Requirement:** Volume IV, Versioning: "Every Dataset, regardless of source, MUST be
  versioned"; Appendix B §B.3, Dataset version immutability.
- **Method:** Automated, Harness
- **Fixture:** A complete `ds-gen@1.0.0` whose `generator.model` resolves to a scripted
  generator returning one row, `query: "Gen-1"`, and on any later call one row,
  `query: "Gen-2"`. `s-greeting` uses `dataset: ds-gen@1.0.0` instead of `variables`;
  scripted subject `SR-ECHO`.
- **Action:** Generate `ds-gen@1.0.0`; execute `cts-suite`. Ask the implementation to
  generate `ds-gen` again, by the operation it documents for that (through the REST API,
  `POST .../datasets/ds-gen/versions`, where that triggers generation); retrieve
  `ds-gen@1.0.0` and every version the request produced; execute `cts-suite` again. If
  the implementation documents no way to generate a Dataset again, which the
  specification does not require, the outcome is `NOT_APPLICABLE` (1.2).
- **Expected:** Both Executions send the Prompt `Gen-1`. The second generation, if
  accepted, produced a new version; the rows of `ds-gen@1.0.0` are unchanged.
- **Fails if:** The second Execution sends `Gen-2`, or `ds-gen@1.0.0`'s rows changed.

### CT-DSR-004 — A Production Replay Dataset supplies its own Prompts

- **Capability:** `dataset:production_replay`
- **Requirement:** Appendix B §B.3, Prompt presence: a Scenario "MUST carry `prompt`
  unless its `dataset` is a `production_replay` Dataset"; Appendix A §A.4.
- **Method:** Automated
- **Fixture:** A complete `ds-replay@1.0.0` holding one captured Conversation whose user
  turn is `"Hello"`. `s-greeting` with `dataset: ds-replay@1.0.0` and no `prompt` or
  `variables`.
- **Action:** Load the configuration; execute `cts-suite`.
- **Expected:** Loaded. The scripted subject receives the captured Prompt, `Hello`.
- **Fails if:** The configuration is rejected for the missing `prompt`, or the subject
  receives anything else.
