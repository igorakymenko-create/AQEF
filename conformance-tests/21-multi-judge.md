# 21. Capability: Multi Judge

Tests in this section apply to an implementation whose Conformance Statement claims
`multi_judge` (§10). For any other, they are `NOT_APPLICABLE`. CT-ASM-013 also belongs to
this capability.

**F-PANEL.** As F-BASE with `semantic-gate` (Section 13.1), with the Expectation's
`judge` replaced by a three-Judge panel:

```yaml
multi_judge:
  purpose: independence
  judges:
    - model: cts-scripted-judge-a@1
      confidence_source: self_rating
    - model: cts-scripted-judge-b@1
      confidence_source: self_rating
    - model: cts-scripted-judge-c@1
      confidence_source: self_rating
  consensus:
    method: voting
    threshold: majority
    on_disagreement: fail
```

Each identifier resolves to the scripted Judge, which the tester can set separately for
each. Unless a test says otherwise, all three behave as `J-PASS-90`.

### CT-MJG-001 — A panel declares its purpose

- **Capability:** `multi_judge`
- **Requirement:** Volume VI, Multi Judge: "a Multi Judge configuration MUST be explicit
  about which it is providing"; Appendix A §A.7, `purpose`: "MUST be declared
  explicitly."
- **Method:** Automated
- **Fixture:** F-PANEL with `purpose` removed.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, or loaded with a purpose supplied silently.

### CT-MJG-002 — Each purpose has its own shape

- **Capability:** `multi_judge`
- **Requirement:** Appendix B §B.2, MultiJudgeConfig: for `independence`, "`judges`
  REQUIRED, `judge`/`samples` MUST NOT appear"; for `stability`, "`judge` and `samples`
  REQUIRED, `judges` MUST NOT appear."
- **Method:** Automated
- **Fixture:** Four variants of F-PANEL. (a) `independence` with `judges` removed.
  (b) `independence` with `samples: 3` added. (c) `purpose: stability` with `judges`
  kept and no `judge` or `samples`. (d) `purpose: stability` with `judge` and
  `samples: 3`, and `judges` kept.
- **Action:** Load each variant.
- **Expected:** All four rejected.
- **Fails if:** Any is loaded.

### CT-MJG-003 — A panel declares how it reaches Consensus

- **Capability:** `multi_judge`
- **Requirement:** Appendix A §A.7: `consensus` and its `method` are required.
- **Method:** Automated
- **Fixture:** Two variants of F-PANEL. (a) `consensus` removed. (b) `consensus.method`
  removed.
- **Action:** Load each variant.
- **Expected:** Both rejected.
- **Fails if:** Either is loaded.

### CT-MJG-004 — A voting threshold is a number above one half, and only for voting

- **Capability:** `multi_judge`
- **Requirement:** Appendix B §B.2, ConsensusConfig: "A numeric threshold MUST be a
  number, not a string"; `threshold` is "greater than 0.5 and at most 1.0" and valid
  "only when `method` is `voting`"; `on_disagreement` is `human_review` or `fail`.
- **Method:** Automated
- **Fixture:** Four variants of F-PANEL. (a) `threshold: "0.75"` (a string).
  (b) `threshold: 0.5`. (c) `method: confidence_weighted_mean` with `threshold: 0.75`.
  (d) `on_disagreement: flag`, a value v0.38 removed.
- **Action:** Load each variant.
- **Expected:** All four rejected. F-PANEL with `threshold: 0.75` is loaded.
- **Fails if:** Any variant is loaded, or the valid one is rejected.

### CT-MJG-005 — Votes are counted against the threshold, rounding up

- **Capability:** `multi_judge`
- **Requirement:** Volume VI, Voting: "A verdict is reached when the pass votes, or the
  fail votes, number at least the threshold times that count, rounded up ... Where
  neither side reaches the threshold ... the Consensus's `on_disagreement` policy
  applies"; Appendix A §A.7.
- **Method:** Automated, Harness
- **Fixture:** F-PANEL with `cts-scripted-judge-c@1` behaving as `J-FAIL-90`.
- **Action:** Execute `cts-suite` with `threshold: majority`; then with
  `threshold: 0.75`.
- **Expected:** Each run calls all three Judges once. With `majority`, two pass votes of
  three reach a verdict: `verdict: pass`, `panel: { configured: 3, counted: 3 }`. With
  `0.75`, three votes are needed and neither side has them, so `on_disagreement: fail`
  applies: `verdict: fail`.
- **Fails if:** Either verdict differs, or `panel` is absent or wrong.

### CT-MJG-006 — A stability panel samples one Judge the declared number of times

- **Capability:** `multi_judge`
- **Requirement:** Appendix A §A.7, `judge` and `samples` (stability); Appendix C §C.7,
  `panel`: "In a stability configuration, samples configured (`samples`) and samples
  counted."
- **Method:** Automated, Harness
- **Fixture:** F-PANEL with `purpose: stability`, `judges` replaced by `judge:
  { model: cts-scripted-judge-a@1, confidence_source: self_rating }` and `samples: 3`.
- **Action:** Execute `cts-suite`; count the calls `cts-scripted-judge-a@1` received;
  retrieve the Results for the Expectation; evaluate the Gates.
- **Expected:** Three calls. Exactly one effective Result for the Expectation's clause
  in this Execution, with `verdict: pass` and `panel: { configured: 3, counted: 3 }`.
  `semantic-gate` counts that one Result (`basis.results: 1`). Records of the
  individual samples, if the implementation keeps them, are not effective Results for
  the clause and are not counted by any Gate.
- **Fails if:** The number of calls is not 3; there is not exactly one effective Result
  for the clause; `panel` differs; or `semantic-gate` counts more than one Result.

### CT-MJG-007 — Agreement between Judges is not presented as a Judge's own Confidence

- **Capability:** `multi_judge`
- **Requirement:** Volume VI, Confidence: agreement across Judges "conflates with
  Consensus and MUST be treated as a distinct signal, not a substitute for a Judge's own
  stated Confidence."
- **Method:** Automated, Inspection
- **Fixture:** F-PANEL with `cts-scripted-judge-c@1` behaving as `J-FAIL-90`.
- **Action:** Execute `cts-suite`; retrieve the Result and whatever per-Judge records
  the implementation keeps. Review how agreement is reported.
- **Expected:** Each Judge's own Confidence (0.9) remains visible as such. Where the
  implementation reports agreement (here two of three), it is labelled as agreement,
  not as any Judge's Confidence.
- **Fails if:** The Judges' own Confidence values are lost, or agreement is presented
  as a Judge's Confidence.

### CT-MJG-008 — Below the quorum, the panel does not assess

- **Capability:** `multi_judge` together with `seeded_controls`
- **Requirement:** Appendix B §B.3, Panel reporting: "Below `min_qualified` (or below the
  full panel when it is absent), the panel's Results for the affected clauses MUST be
  `not_assessed`."
- **Method:** Automated
- **Fixture:** F-PANEL plus F-SEED's `s-control` (Section 13.1), whose Expectation uses
  the same panel; `s-control` placed first in `cts-suite`, and `execution: { scheduling:
  sequential }`, so that the miss is known before `s-greeting` is assessed. `cts-scripted-judge-a@1` behaves as `J-PASS-90` (it misses the
  control); `-b` and `-c` behave as `J-CATCH`. Two variants: (a) no `min_qualified`;
  (b) `min_qualified: 2`.
- **Action:** Execute `cts-suite` for each variant; retrieve `s-greeting`'s Expectation
  Result.
- **Expected:** (a) The Result is `not_assessed`, `verdict: null`. (b) The Result has a
  verdict (`pass`) and `panel: { configured: 3, counted: 2 }`.
- **Fails if:** (a) has a verdict, or (b) is `not_assessed` or counts Judge `a`.
