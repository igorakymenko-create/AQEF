# Appendix B — Metric source register

The register identifies the kind of method behind each metric. Part 4 gives the measurement unit, scoring procedure and limits used in this Guide. A published metric family, standard or convention supplies context for the local procedure.

|Metric|Method provenance|
|---|---|
|M-01 — Faithfulness / groundedness|Published metric-family reference|
|M-02 — Context Recall|Published metric-family reference|
|M-03 — Task Completion / task success|Related methodological reference|
|M-04 — Over-refusal / exaggerated safety refusal|Related methodological reference|
|M-05 — Context precision|Related methodological reference|
|M-06 — Context relevance|Related methodological reference|
|M-07 — Answer relevance|Related methodological reference|
|M-08 — Answer correctness|Related methodological reference|
|M-09 — Citation precision / recall|Related methodological reference|
|M-10 — Tool selection accuracy|Related methodological reference|
|M-11 — Argument correctness|Related methodological reference|
|M-12 — Trajectory match|Related methodological reference|
|M-13 — Step efficiency|Guide-defined procedure; AQEF Volume VIII agent-testing context|
|M-14 — Plan Adherence|Related methodological reference|
|M-15 — Knowledge Retention|Related methodological reference|
|M-16 — Conversation Completeness|Related methodological reference|
|M-17 — Role Adherence|Related methodological reference|
|M-18 — Coherence|Guide-defined rubric; no unique primary metric definition established|
|M-19 — Toxicity|Related methodological reference|
|M-20 — Bias|Related methodological reference|
|M-21 — Personal Data Leakage|Related methodological reference|
|M-22 — Attack Success Rate|Related methodological reference|
|M-23 — Refusal Rate|Related methodological reference|
|M-24 — Exact Match|Related implementation reference|
|M-25 — Schema / JSON Validity|Underlying validation standard / operation|
|M-26 — Pattern Match|Underlying validation standard / operation|
|M-27 — BLEU|Published metric-family reference|
|M-28 — ROUGE|Published metric-family reference|
|M-29 — Embedding Similarity|Related methodological reference|
|M-30 — Rubric Scoring|Related methodological reference|
|M-31 — Pairwise Preference|Related methodological reference|
|M-32 — Consistency Across Runs|Guide-defined consistency measure; AQEF Volume VIII Consistency Testing|
|M-33 — pass@k|Published metric-family reference|
|M-34 — pass^k|Related methodological reference|
|M-35 — Latency|Related observability convention|
|M-36 — Cost|Related observability convention|
|M-37 — Token Usage|Related observability convention|

## Appendix B.1 — Foundational methods and definitions

- **Grounding and citations (M-01, M-02, M-09).** Compare claims, required facts and cited passages with captured source material. Specify the comparison unit and how to handle missing support.
- **Refusal (M-04, M-23).** Use independently labelled permitted and prohibited requests. Report the two error directions with separate denominators.
- **Structured output (M-25).** Separate parsing from schema validation. Pin the grammar and schema dialect used for the check.
- **Text and semantic similarity (M-27–M-29).** Choose a lexical-overlap or vector-similarity procedure. Record the variant, preprocessing and aggregation.
- **Rubric scoring (M-30).** Anchor each score to observable criteria and validate the rubric against an independent Reference Set.
- **Repeated outcomes (M-33, M-34).** Distinguish the chance of at least one success from the share of cases that succeed on every repeat. State the sampling assumptions.
- **Operational measures (M-35–M-37).** Define latency boundaries, usage units and cost calculation. Keep versions of the measurement convention and tariff with the configuration.

Record the version and retrieval date of any standard or convention adopted by the Project alongside the metric configuration.
