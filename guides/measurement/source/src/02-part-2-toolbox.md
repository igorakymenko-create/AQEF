# PART 2 · TOOLBOX: ORACLES, CHECKS AND THRESHOLDS

## 2.1 Kinds of Oracle

| Oracle family          | Strongest use                                      | Primary weakness                    | How to challenge                              |
|------------------------|----------------------------------------------------|-------------------------------------|-----------------------------------------------|
| Structural Validator   | Required fields, IDs, formats, tool arguments      | No semantic understanding           | Positive/negative fixtures; unavailable path  |
| Evidence Validator     | Retrieved IDs, trajectory facts, explicit outcomes | Incomplete capture                  | Missing-artifact fixture; equivalence classes |
| Single-criterion Judge | One interpretive property                          | Prompt and context sensitivity      | Reference labels; defect + clean controls     |
| Multi-criterion Judge  | Several related semantic properties                | Mixed criteria mask errors          | Per-criterion results and controls            |
| Multi-Judge panel      | Disputed semantics                                 | Correlated judge errors and expense | Admission of members; disagreement review     |
| Human Review           | Reference labels and escalations                   | Review variance and scale           | Written rubric, blind overlaps, calibration   |

A Validator is not synonymous with simple. A complex rule can use captured structured state, but its decision must be explicit and inspectable. Conversely, a Judge that returns a number is not automatically more objective. Identify the decision procedure before deciding which instrument is cheapest.

Oracle configuration is part of what is trusted. Changing a Judge’s instructions can change the measured construct. Changing normalization rules can change a Validator’s equivalence classes. Keep configuration identity next to the Result and make trust evidence traceable to that identity.

## 2.2 Four check techniques

### Reference checking

Compare one Execution to an independently established expected property or answer. It is useful for required document IDs, authorized tool choices, and labelled refusal cases. Trap: treating one preferred phrasing as the only valid semantic answer. Prefer property-level reference labels where valid outputs vary.

### Metamorphic checking

Alter one controlled input and specify which outputs may change. Example: change a refund request from an eligible to an ineligible date, holding other fields constant; eligibility should respond, while customer identity should not. Trap: assuming a transformation preserves meaning when it changes relevant policy context.

### Differential checking

Run the same controlled case on two versions, prompts, or knowledge-base revisions and compare the same property. Identify the baseline and population; a different answer is not necessarily a regression. Trap: reusing an old oracle label after policy changed legitimately.

### Consistency checking

Repeat an equivalent input under recorded operating conditions and assess semantic stability or an explicit dispersion measure. Identical wording is not the goal unless the contract requires it. Trap: combining runs across model revisions, temperature settings, or changed retrieval content as if conditions were constant.

## 2.3 Per-Execution and set-level properties

A claim-supported verdict belongs to an Execution or to claims within it. Context recall can be computed as a set-level ratio over labelled required items. Consistency requires repeated executions. An escalation share is a property of a set, not a failure label on a single answer. Do not fabricate per-Execution pass/fail labels from a set-only metric simply to make a Gate appear uniform.

For ratios, show numerator and denominator. For repeated-run properties, show scenario count, repetitions per scenario, and how an Execution family was grouped. For conditional properties, show coverage of triggering cases. Averages must be accompanied by distributions or critical-case counts when the mean could hide a severe miss.

## 2.4 Choosing a threshold without borrowing a magic number

> 1\. Start with the consequence of a miss and the risk appetite already approved for the workflow.
>
> 2\. Validate that the chosen instrument can discriminate the relevant defect class at the proposed decision boundary.
>
> 3\. Define the target population and minimum evidence basis before testing.
>
> 4\. Document whether a result is blocking, advisory, or a trigger for Human Review; record the owner and rationale.
>
> 5\. Treat revisions to thresholds, oracle configurations, and baselines as controlled changes, not post-hoc fixes for a failing run.

Illustration only: a team might distinguish a zero-tolerance unauthorized tool action from a service-latency trend reviewed against a historical baseline. This illustrates different consequence models; it prescribes no numeric threshold or universal policy.

For a subjective property such as tone or helpfulness, a Project can justify a threshold against agreement among independent human reviewers on the Project’s Reference Set. Record reviewer agreement before arbitration, sample size, the cost of false alarms and misses, and the rationale for the chosen boundary. For objectively checkable claims, reviewer disagreement calls for corrected labelling or arbitration; it is not a natural ceiling on quality.

## 2.5 Tuning a Judge Is Not Admitting It

| Mechanism       | Question / evidence                                                   | When assessed                   |
|-----------------|-----------------------------------------------------------------------|---------------------------------|
| Tuning          | Improve development-set alignment; not independent trust evidence     | Before freeze                   |
| Admission       | Frozen Judge vs human Reference Set; raw + chance-corrected agreement | Before relying on configuration |
| Calibration     | Reported Confidence vs observed accuracy                              | Over time                       |
| Seeded Controls | Detect known defect and pass clean controls in current run            | Run-local                       |

Tuning is a preparatory improvement activity, not AQEF Judge Admission. A common practice is to label examples with humans, adjust a Judge prompt or rubric until agreement improves, calculate agreement in code, and ask people to approve the result. This can expose ambiguous criteria, raise consistency and preserve human control. The limitation arises when the same examples used to choose the configuration are also offered as independent evidence that the final configuration is trustworthy.

Four different questions must remain separate. TUNING: Which prompt, rubric, examples or model configuration performs better on a development set? ADMISSION (AQEF Volume VI): Does the frozen configuration agree sufficiently with independently established human verdicts on a Reference Set, with a predeclared threshold and both raw and chance-corrected agreement? CALIBRATION (Volume VI): Does reported Confidence track observed accuracy over time? SEEDED CONTROLS (Volume VIII): In this run, can the Oracle detect planted defects and avoid false alarms on clean cases?

Recommended operating sequence (Guide recommendation, not a newly imposed AQEF MUST): Tune on development items → freeze model, prompt, criteria, scale and examples → prepare an independent, versioned Reference Set → run and record Admission for that configuration → exercise defect and clean Seeded Controls in relevant runs → monitor calibration and drift → if retuning changes model, prompt or criteria, treat the result as a new configuration requiring its own Admission evidence.

Seven failure modes to examine: (1) reusing tuning cases as admission evidence; (2) allowing tuners to see Reference Set items; (3) changing human reference labels in response to Judge outputs; (4) reporting only raw agreement when class prevalence makes it misleading; (5) selecting the decision threshold after seeing outcomes; (6) treating confidence calibration or same-run controls as substitutes for Admission; (7) carrying the Admission of an earlier model/prompt/criteria version forward after a material change.

AQEF Volume VI states that Reference Set verdicts SHOULD come from Human Reviewers independent of tuners; an item exposed to someone tuning that Judge SHOULD NOT be used to admit it again. Independent initial labels, recorded arbitration, coverage of multiple sources, and versioning are also SHOULD-level safeguards. These recommendations must not be silently rewritten as universal MUSTs. Volume VI, Admission, states: “The record MUST state the Reference Set and its version, how many items were scored and how their correct verdicts were distributed, the raw agreement, and an agreement measure corrected for chance, by name and value.” The Project chooses the measure and threshold. Volume VI, Admission, states: “A Project MAY require admission before a Judge's Results count”. The Gate setting is `require_admitted_judges` (Appendix A §A.10).

Illustrative Aster faithfulness experiment (invented values, not observed performance). Working-set tuning items: 25; the prior configuration agreed with human labels on 19/25 = 76%, and the tuned configuration on 22/25 = 88%. Neither 88% nor the increase proves independent Admission: these items influenced configuration choice.

Freeze the tuned Judge. On a distinct, blinded 60-item Admission Reference Set with 30 human-positive and 30 human-negative labels, suppose TP=25, FN=5, FP=6, TN=24. Then raw agreement=(25+24)/60=49/60=81.67%. Predicted positive=31 and negative=29; chance agreement Pe=(30×31 + 30×29)/60²=0.50. Cohen κ=(49/60−0.50)/(1−0.50)=0.6333. If κ ≥ 0.70 was predeclared, verdict: NOT ADMITTED. The raw score may look strong while the chance-corrected decision fails. This κ threshold is illustrative, not prescribed by AQEF.

Small-set uncertainty note (illustrative): 17 agreements among 20 cases gives 85% raw agreement, but one case changes it by five percentage points. For p = 17/20 = 0.85, n = 20 and z = 1.96, the two-sided Wilson interval is (p + z²/(2n) ± z√(p(1−p)/n + z²/(4n²))) / (1 + z²/n) ≈ [0.6396, 0.9476]. Do not present one rounded percentage from a tiny working set as a robust Admission conclusion. The calculation quantifies uncertainty in the proportion; it is not an AQEF-prescribed Admission threshold.

Seeded Controls are not extra admission examples. Volume VIII defines defect and clean controls (caught/missed and passed/false_alarm), same-run invalidation by shared defect class on a miss, and exclusion of control Results from Aggregation. Its coverage and order rules use SHOULD where stated; a clean-control false alarm is treated as a miss for invalidation. These runtime checks cannot retrospectively make an exposed Admission set independent.

Before a Reference Set is used for Judge Admission, compare independent reviewers before arbitration. If their chance-corrected agreement is weak, revisit criteria and labelling first. An uncertain human reference cannot establish a trustworthy Judge score. A Judge cannot reasonably be required to outperform the reproducibility of a disputed reference without resolving its ambiguity.

For a predeclared threshold, the Project should consider the lower confidence bound of its chance-corrected agreement estimate, not just the point value. Name the interval construction (for example a declared resampling method), how repeats or correlated items were handled, and the number of independent reference items. Choose that number before scoring, using the intended interval width, expected agreement and the planned mix of verdicts. Record the planned independent item count and the smallest lower bound that would support the decision. The Wilson interval for a binomial proportion shown above is not automatically an interval for Cohen’s κ.

A criterion that says “accept unless we prove this Judge worse than a person” is unsafe when data are scarce: failure to reject inferiority does not prove adequacy. If statistical non-inferiority or equivalence is used, state the direction, margin and method before admission runs. These are measurement recommendations, not new AQEF requirements.

Tuning is Selection: trying several prompts or configurations on working data does not establish independent Admission. Part 6 defines what is frozen, what reference material must remain independent, and how to precommit the decision rule.

## 2.6 Result states and the no-silent-pass principle

Distinguish property-level “not applicable/not assessed” from a subject failure, and from the formal `oracle_unavailable` Result when a Validator or Judge cannot reach a verdict (Volume V, Validator SDK; Appendix C §C.7). Where a Gate relies on unavailable or non-actionable Results, AQEF’s effective-state and Aggregate Basis rules apply. Do not silently recode these categories as pass or fail.

Editorial state vocabulary: NOT_ASSESSED denotes a guide-level absence of an eligible unit, and is not a product PASS or FAIL; UNAVAILABLE denotes missing evidence or an Oracle that cannot produce a trustworthy verdict. These reader-facing labels are not additional normative AQEF dispositions. Record the actual AQEF disposition (`not_assessed`, `oracle_unavailable`, `inconclusive`, `awaiting_review`, or `actionable`) separately when it applies. PASS and FAIL here are property-level assessments, not AQEF dispositions.

A reviewable result record should allow a reader to recover: scenario and Execution identity; evidence artifact identities; Oracle type/configuration; verdict and rationale; trust/reference status; target dimension; grouping/aggregation basis; and Gate outcome. This is a guide-level checklist and must not be mistaken for the normative AQEF schema.

**Guide-level result state mapping (informative; not a normative AQEF state table)**

| Guide label     | Status / disposition interpretation                                                                                |
|-----------------|--------------------------------------------------------------------------------------------------------------------|
| PASS / FAIL     | Guide-level assessed property outcome; not AQEF dispositions                                                       |
| NOT_ASSESSED    | No eligible unit; when applicable record AQEF `not_assessed`                                                     |
| UNAVAILABLE     | Oracle or evidence cannot support assessment; record `oracle_unavailable` when that exact AQEF condition applies |
| INCONCLUSIVE    | Unresolved property decision; use AQEF `inconclusive` when applicable                                            |
| AWAITING_REVIEW | Use AQEF `awaiting_review` when assigned for Human Review                                                        |
| ACTIONABLE      | AQEF `actionable` disposition; not a synonym for Guide-level PASS                                                |

## 2.7 One run is not a measurement

The outcome of one probabilistic subject Execution or Judge assessment is a sample. It cannot justify a claim of stability at N = 1. Repeat the same controlled Scenario under recorded conditions, keep each Execution, and report k of N occurrences for every outcome category. A case that passes six times and fails four times is divergent (6/10 pass, 4/10 fail), not “mostly passed”. Do not select only a convenient run or average away the disagreement.

An Execution that never reached the behavior being measured supplies no verdict for that check. An empty page, navigation failure or evaluator timeout may mean “could not measure”, neither pass nor fail. If the subject caused the failure, write a separate property and finding for that subject behavior. This follows the no-silent-pass discussion in §2.6; measurement unavailability must not silently count as success.

One variant, one row: two phrasings of the same underlying ticket test robustness to wording, not two independent use cases. Capture run identity, model version, configuration, sampling parameters, tool and knowledge-source versions for both the subject and the Judge. When a difference cannot be isolated, report “cause not isolated” rather than guessing.

Guide practice under AQEF 1.0: run the Suite N times, retain every Execution and its Result, then report k of N alongside the Gate outcome. AQEF 1.0 has no field for requesting repeated Executions, and Appendix A §A.11 Baselines refer to a Result from one Execution. A Regression Gate continues to compare individual Results. §2.2 discusses consistency checking; M-34 reports repeated pass behavior as a specific metric. This section concerns the reliability of every check, not only consistency.

Budget extra sampling for consequential or divergent cases. Additional runs consume time and money; the Project decides the repeat count and uncertainty it can tolerate, before seeing the outcomes.
