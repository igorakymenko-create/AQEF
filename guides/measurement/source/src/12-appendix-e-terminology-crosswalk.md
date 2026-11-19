# Appendix E — Terminology crosswalk

Readers from model evaluation and post-training meet the ideas of this Guide under other names. The table maps AQEF terms to terms common in that field and says where the meanings part. Usage outside AQEF varies between teams and publications, so the middle column lists terms, not definitions. The AQEF definitions are those of the specification (Appendix C of this Guide says where to find them).

| AQEF term | Terms used elsewhere | Where the meanings part |
|---|---|---|
| Judge | LLM-as-a-judge; LLM evaluator; autorater; model-based grader | An AQEF Judge assesses one Contract clause for one Execution and returns `pass` or `fail` with a Confidence. Comparing two outputs is a different task (M-31). |
| Validator | programmatic grader; rule-based check; unit-test grader; deterministic metric | A Validator is deterministic and carries no Confidence. A check that calls a model is a Judge, whatever it is called (Volume V). |
| Reference Set | golden set; gold labels; human-labelled evaluation set; meta-evaluation set | Its verdicts come from Human Reviewers independent of whoever tunes the Judge. It is versioned, and an item a tuner has seen is not used to admit that Judge again (Volume VI). |
| Admission | meta-evaluation; judge validation; human-agreement study | Admission is a recorded decision about one frozen configuration, against a threshold the Project declared, on a chance-corrected measure stated with the raw agreement and the verdict distribution. A correlation reported once is not an Admission. |
| Chance-corrected agreement | inter-rater or inter-annotator agreement; kappa; alpha | The same idea. AQEF requires the measure to be named, and the raw agreement and verdict distribution stated beside it (§2.5). |
| Calibration | calibration; expected calibration error; reliability diagram | AQEF Calibration compares a Judge's stated Confidence with Human Reviewer verdicts over time. It does not show that the Judge detects defects; Admission does (§2.5, §6.1). |
| Seeded Control (defect control) | canary; known-answer item; planted error; fault injection or mutation testing applied to the evaluator | It runs in the same batch as the Results it qualifies, and its planted defect is confirmed to be in the Evidence. A miss invalidates that Oracle's Results for the same defect class in that run (Volume VIII). |
| Clean control | negative control; known-good item | A false alarm on a clean control counts as a miss, so a Judge that fails everything is caught (Volume VIII). |
| Multi Judge, `purpose: independence` | jury; panel of LLM evaluators; ensemble of judges | Judges from different model families. How their verdicts combine is declared, and the Result states how many Judges were configured and how many counted (Volume VI). |
| Multi Judge, `purpose: stability` | self-consistency; repeated sampling | Repeated samples of one Judge reduce its sampling noise; they do nothing for blind spots the samples share (Volume VI). |
| Judge Drift | evaluator drift; judge drift | Detected over time against Human Reviewer agreement. A model that changes behind an unchanged identifier is a different Judge and needs its own Admission (Volume VI). |
| Exposure of a Reference Set item | data contamination; test-set leakage; overfitting to the evaluation | In AQEF an item is exposed when someone who tunes the Judge has seen it. An item that may have reached a model's training data is a further risk for the Project to weigh. |
| Selection, then Admission | development and test split; held-out evaluation; prompt tuning on a development set | Choosing among models and prompts is Selection, on working items. Admission uses a Reference Set held out from that choice (§6.1). |
| Semantic Regression | evaluation regression; quality regression | Judged by meaning against an approved Baseline, not by equal text (Volume X). |
| Human Reviewer | human rater; annotator; labeller; human evaluation | An Oracle in its own right, and the reference for Admission and Calibration. A Human Reviewer is not itself admitted (Volume VI). |
| — | reward model | No AQEF counterpart: a scorer trained to steer optimisation. Used to assess Evidence, it is a Judge configuration and needs Admission like any other. |
