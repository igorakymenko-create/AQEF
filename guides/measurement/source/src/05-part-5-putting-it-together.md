# PART 5 · PUTTING IT TOGETHER

## 5.1 A starting set: ten checks, not ten magic numbers

Begin from consequential failures: wrong refund policy; unsupported or mis-cited claims; inappropriate refusal; wrong tool or falsely claimed completion; unsafe obedience to untrusted text; prohibited actions; and operational regression. Aster’s example corpus contains versioned refund and delivery policies; its tools can look up an order and submit a refund in a sandbox after authorization. The example assumes those instruments and permissions exist. A different product must redo this selection.

A useful first suite is not necessarily ten different metrics. Some checks are paired to separate causes, and every proposed check names exactly which Evidence it needs. An instrument that cannot see the failure cannot produce a meaningful pass.

| \# / Risk | Check and measurement                                                          | Oracle and Evidence                                                                       | Proposed treatment                                         |
|-----------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 · R-01  | Required governing passage present in captured retrieval                       | Validator; document IDs, effective version, retrieved Artifact                            | Functional blocking for policy-critical scenarios          |
| 2 · R-02  | Critical factual claims supported by captured passages (M-01)                  | Admitted single-criterion Judge; answer + same-Execution context                          | Semantic blocking after Oracle trust                       |
| 3 · R-03  | Cited ID resolves to a captured eligible passage                               | Validator; citation IDs and captured source identifiers                                   | Functional blocking for required citations                 |
| 4 · R-04  | Correct abstention on no-answer trap rows                                      | Validator for coded outcome, Judge otherwise; dataset answerability labels                | Semantic blocking for unsupported high-impact answers      |
| 5 · R-04  | No over-refusal on paired answerable rows (M-04)                               | Admitted Judge; answerable reference and response                                         | Advisory initially; reassess by business consequence       |
| 6 · R-06  | Correct tool choice and protected arguments (M-10, M-11)                       | Validators; captured tool calls and scenario constraints                                  | Functional blocking for transactional calls                |
| 7 · R-07  | Claimed completion matches successful recorded tool outcome                    | Validator for status plus Judge for nuanced assertions; response + trajectory             | Functional / semantic blocking                             |
| 8 · R-09  | Untrusted document/tool-output instructions do not redirect behavior           | Boundary Validator plus admitted Judge for semantic redirection; channel-marked artifacts | Safety: validator hard veto; context findings separately   |
| 9 · R-11  | No attempt to cross action boundary or touch Tripwire                          | Boundary Validator; enforced boundary + denied-attempt logs                               | Safety hard veto for deterministic prohibited routes       |
| 10 · R-12 | Latency, cost and subject stability against a named baseline (M-32, M-35–M-37) | Validators; timings, cost units, repeat groups, baseline scope                            | Operational / regression Gate chosen by service obligation |

The list is deliberately selective. R-05 (stale policy), R-08 (conversation memory) and R-10 (content/privacy safety) are not “covered for free”: Aster’s initial scope must explicitly say whether those risks are release-critical. If they are, promote additional checks into the first suite rather than preserving a ceremonial count of ten. Aster can use a versioned effective-policy row as an early R-05 expansion.

### 5.1.1 Order of implementation

**First, capture Evidence.** Before defining a score, store question, response, retrieved passages with version and rank, citation anchors, tool calls/results, action-boundary events, elapsed time and cost with collection scope. Preserve the exact Evidence used by an Oracle.

**Second, implement deterministic checks.** Start with retrieval IDs, citation existence, schema/argument restrictions, action routes and tool-result status. These predicates are inspectable; document their inability-to-run behavior as oracle_unavailable, not product failure (AQEF Volume V, Validator SDK).

**Third, qualify one semantic Judge.** Choose a single high-consequence property such as critical-claim grounding. Construct an independently labelled Reference Set, record Admission against a Project threshold, and seed one defect control and one clean control for that defect class. If a Gate uses require_admitted_judges, non-admitted Judge Results cannot make it pass. Admission belongs to the exact model/prompt/criteria configuration (Volume VI, Admission).

**Fourth, grow only by coverage need.** Additional Judges increase calibration work and correlated-error risk. Use Human Review for ambiguous and high-stakes cases rather than implicitly equating agreement between models with truth.

### 5.1.2 Miniature dataset design

Each row records scenario ID, intent, authorized actions, policy snapshot/effective date, expected source IDs, critical fact or required behavior, answerability, evidence-capture expectation, and a defect class. Pair a clean customer question with an otherwise identical trap: missing source, superseded policy, changed refund amount, misleading citation, forged tool success, untrusted document instruction or blocked endpoint. Maintain varied wording; do not use the planted controls as production outcome samples.

Illustration only: an ordinary return eligible under the current policy is a clean row; a response replacing the recorded refund amount with another amount is a planted grounding defect. Independently verify the synthetic “correct” label before using it as a control. The amount and threshold are not AQEF defaults.

## 5.2 From checks to Quality Gates

Aster’s checks produce Results; only effective, actionable Results can support aggregation and Gates. Gate configuration specifies dimensions and weights; an aggregate is not simply a count of responses. Each Gate reads a declared Aggregate Basis with actionable and non-actionable Results plus distinct Scenarios and Executions (AQEF Volume I, Chapter 6). Seeded Controls do not enter product aggregates.

| Proposed Gate          | Consumes                                                                                    | Release role / caveat                                                                                     |
|------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Safety Boundary        | R-09 deterministic boundary events; R-11 prohibited attempts                                | Blocking; Validator-enforced Safety failures are hard vetoes                                              |
| Functional Transaction | R-01 source presence; R-03 ID resolution; R-06 tool choice/arguments; R-07 confirmed action | Blocking where these transactions are in release scope                                                    |
| Semantic Policy        | R-02 grounded critical claims; R-04 justified abstention; later R-05 current-policy answers | Blocking by Aster’s chosen risk; Judge findings are confidence-qualified, not unconditional Safety vetoes |
| Regression             | Per-scenario comparison with approved Baseline or Snapshot                                  | Blocking or advisory depending on accepted regression budget and configuration                            |
| Operational Service    | Latency, cost, subject completion and stability within a defined cohort                     | Blocking for contractual SLOs, advisory for exploratory cost trends                                       |

A fifth or sixth Gate is reasonable if separable ownership or evidence warrants it. Do not create one Gate per metric mechanically. Conversely, do not merge a hard safety constraint into an average from which an unrelated good score could compensate for it.

### 5.2.1 Decision examples (illustrative, no recommended thresholds)

**Case A — trusted system failure.** Aster’s captured refund instruction contains the wrong amount. The admitted Judge labels the critical claim contradicted, and its current-run controls pass. The relevant Result is actionable and fails the Project’s Semantic Policy condition. A blocking Gate does not pass because of a product finding.

Case B — broken instrument, not a proven product failure. The Judge misses a planted amount-change defect, or falsely flags the clean paraphrase. Results sharing that Oracle and defect class are invalidated for the run (the Project may separately elect reason-recorded full-run invalidation); a false alarm on a clean Seeded Control has the same invalidation consequence; a Gate relying on those Results cannot pass for seeded_control_miss or seeded_control_false_alarm, not because Aster failed. Requalification can reassess stored Evidence (AQEF Volume VIII, Seeded Controls; Volume I, Result Resolution).

**Case C — too little basis.** All sampled answers look good, but the declared minimum Aggregate Basis is not met. The Gate cannot pass, with insufficient basis recorded as the reason. A Project chooses whether to declare a minimum; AQEF does not impose a universal sample size (Volume I, Chapter 6).

**Case D — Oracle unavailable.** The citation Validator times out. That creates no product verdict: oracle_unavailable is not fail. Evidence remains available for reassessment. If the aggregate has no actionable Result, the Gate cannot pass (Volumes V and I).

Note on Safety: AQEF’s hard veto applies to Validator-enforced Safety constraints. Contextual Safety findings from Judges/Human Reviewers follow the weighted Result and Gate model rather than automatically receiving the same unconditional veto. Aster can choose suitably conservative blocking thresholds without rewriting the specification.

### 5.2.2 The trustworthy decision record

For every Gate report its scope, source Suite or Project, clause IDs, dimensions and Contract weights ( `policies.weight` , Volume VII and Appendix A §A.5), threshold direction, whether blocking or advisory, configured admission policy (including whether `require_admitted_judges` is set), Baseline/Snapshot version where relevant, and minimum basis if declared. Judge Admission is configuration-specific, and a Judge not admitted becomes a Gate blocker by that rule only where the Gate requires admission; Reports still disclose non-admitted Judges. The recorded outcome identifies the effective Results used, how many were non-actionable, seeded-control status and the reason it did not pass. Never restate unknown or not-assessed as fail or pass to simplify dashboards.

## 5.3 When the measurement set grows

Aster’s coverage evolves when policies, tools, users or observed incidents change. A new check should start from a new or altered risk statement, then move through observable symptom, Evidence capture, property, Oracle, independent trust evidence, dimension and Gate. Adding a metric because a library exposes it reverses the decision logic.

| Change trigger       | Example adaptation                                                  | Required review                                                                 |
|----------------------|---------------------------------------------------------------------|---------------------------------------------------------------------------------|
| New policy version   | Add R-05 effective-date transition rows and version-selection check | Capture snapshot and effective policy; differentiate retrieval from application |
| New tool / action    | Add R-06/R-11 argument and boundary scenarios                       | Update allowed routes, Tripwires, side-effect recording                         |
| Longer conversations | Add R-08 corrected-fact retention and contradiction rows            | Measure required fact opportunities, not only full transcript count             |
| Safety incident      | Add R-10 category-specific output/privacy checks                    | Separate categories, permitted disclosures, and unknown outcomes                |
| Observed drift       | Add M-32 consistency and scoped operational baselines               | Approve cohort, sampling, clock/cost definition and baseline                    |

### 5.3.1 Change control and retirement

A changed Judge model, prompt or criteria is a new configuration for Admission (Volume VI). A changed policy snapshot, metric denominator or threshold changes the meaning of a trend: record the change and why, rerun relevant Reference Set and controls, and label cross-version charts rather than splicing incompatible series. Baseline revisions require approved governance as defined by the applicable AQEF mechanisms (Volumes X and XII).

Retire a check when the risk disappears, the property becomes redundant, or the Oracle no longer represents the system’s operating boundary—not when the score becomes inconvenient. Archive its objective, historical Results, decision impact and approval. This retirement workflow is guidance from this companion, not an additional AQEF MUST.

## 5.4 Reading a red result

“Red” is not a diagnosis. Use the following decision path before opening a product defect or making a release decision.

| Step           | Question                                                                                                | If not satisfied                                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| 1 · Instrument | Was this Oracle available, admitted where configured, and qualified for the relevant class in this run? | Stop interpreting product quality; record unavailable/non-admitted/invalidation reason and requalify or re-assess stored Evidence. |
| 2 · Basis      | Is the effective Aggregate Basis sufficient, with denominator, scope and distinct scenarios reported?   | Collect additional independent cases or change the Gate only through approved governance; do not count unassessed cases as passes. |
| 3 · Currency   | Are policy snapshot, data version, Judge configuration and Baseline the expected versions?              | Correct stale test Evidence or perform an explicit version-aware re-evaluation; do not erase prior Results.                        |
| 4 · Subject    | Does the trusted, current, sufficiently based Result show a real failure of the AI system?              | If yes, localize to retrieval, generation, citation, tool, authorization or operations; open a defect with captured Evidence.      |

### 5.4.1 Worked incident: the refund that was not completed

Aster tells the customer, “Your refund was completed,” but the captured tool response reports a rejected request. R-07 flags the mismatch. Diagnose in this order: verify the trajectory Artifact is complete; run the outcome-to-claim Validator against the stored tool result; confirm the Oracle’s known-good and seeded-defect controls; inspect whether a successful alternative transaction occurred; only then conclude that the claim is false. R-06 may pass simultaneously if the selected tool and parameters were correct. This is why tool correctness and outcome honesty remain independent properties.

If the refund tool failed due to the subject’s dependency, treat that as behavior of the system being tested, not an excuse to discard a bad response. AQEF Volume III Retry applies only to infrastructure failures before a genuine subject Response and creates no Conversation for the failed attempt. A second Execution after an unfavorable verdict retains the first Result; Evaluation-stage Oracle unavailability is handled separately under Volume VI, not by rerunning the subject to obtain a favorable answer.

## 5.5 A minimal weekly decision practice

An Aster release review reads the five Gate outcomes with their bases and instrument status; inspects any blocking failure, seeded-control miss and source/Oracle drift; compares meaningful cohorts to the approved baseline; and records disposition, owner and justification. It does not celebrate a “green” aggregate that excludes every difficult case, nor count a sampled control as proof that the product is safe.

The practitioner should leave with four auditable objects: a versioned risk-to-property map; captured Evidence and reproducible measurement procedures; independently qualified Oracles; and a release decision supported by actionable aggregate results. This is the point of the guide: not to gather more numbers, but to know what a number can actually support.

## 5.6 When to measure again

### 5.6.1 Changes and the evidence to renew

Check which validated inputs changed before deciding what to measure again. The following is a practical change-to-action map; the Source column names the relevant AQEF context, not a new release requirement.

| Change                                                                  | What becomes invalid or suspect                                 | Action                                                           | AQEF source                             |
|-------------------------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------|
| Environment (model version, prompts used by subject, tools, parameters) | Results produced under a different Environment than the Snapshot are stale | Re-run affected Executions and reevaluate Gates                  | Volume I, Chapter 6 — stale Results     |
| Contract clause matched by id                                           | Results from the changed clause                                 | Re-run affected clauses; without ids, reassess whole Contract    | Volume I, Chapter 6                     |
| Quality Gate definition                                                 | Gate assessment or Release Decision; Results may remain current | Re-evaluate Gates, without unnecessary new Execution             | Volume I, Chapter 6 — Decision Pipeline |
| Dataset version                                                         | Scenarios bound to that Dataset                                 | Re-run affected Scenarios; document the changed input            | Volume IV — Versioning                  |
| Judge configuration (model, prompt, criteria, parameters)               | Judge Admission                                                 | New Admission; use current run controls                          | Volume VI — Admission                   |
| Seeded Control miss or false alarm                                      | Trust in the affected defect class                              | Diagnose, requalify on fresh controls, reassess affected Results | Volume VIII — Seeded Controls           |
| Reference labels, reviewers or criteria                                 | Reference Set trust and prior Admission                         | Re-establish independent reference and admit again               | Volume VI — Reference Set               |
| Provider/model drift invisible to AQEF                                  | Apparent stability of prior Results                             | Run scheduled regression independent of visible changes          | Volume X — Regression                   |
| Before Release Decision                                                 | Gate assessment for current configuration                       | Evaluate Gates on current Results                                | Volume I, Chapter 6 — Release Decision  |

In AQEF 1.0, changing a Prompt template or Dataset version does not by itself make an existing Result stale under the  Chapter 6 matching rule. The Project should still rerun impacted Scenarios and record the action. Separately, a RAG corpus or knowledge source behind a tool can change without any visible Environment change; record its version or content digest outside the AQEF Result schema and rerun relevant Scenarios when it changes. Volume I, Chapter 6, “Quality Gates,” states: “A Gate MUST NOT pass on an aggregate that includes a stale Result”. The Gate records `stale_results` (Appendix A §A.12). The same section states: “A Release Decision is valid only for the configuration its Gates were evaluated under.”

### 5.6.2 Example cadences, not AQEF requirements

On every relevant code, prompt, data or tool change: re-run the Scenarios touched by that change. Before every release: evaluate the Quality Gates on current Results. On a risk-selected schedule: repeat regression checks to detect silent provider drift. For Judges: revisit calibration and Admission on a planned schedule and immediately after a drift signal, configuration change or Seeded Control failure. These are illustrative cadences, not a universal schedule.

Connect this with the minimal weekly decision practice in §5.5: a regular review is useful only when it can detect evidence that has become old, incomplete or no longer representative.
