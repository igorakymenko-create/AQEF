# PART 1 · METHOD: FROM RISK TO A TRUSTED MEASUREMENT

## 1.1 The chain from risk to decision

Risk → observable symptom → property → Oracle → evidence of Oracle trust → quality dimension and clause → aggregate → Gate. A weak link invalidates conclusions downstream. A precise metric applied to the wrong symptom cannot answer the risk; a strong judge run without an adequate reference and controls cannot responsibly determine a release outcome.

Consider Aster Support AI, a fictional customer-service assistant that retrieves refund policies and may initiate approved customer-service actions. Aster is used throughout this guide; all customers, records, thresholds, policies, and measurements are illustrative. A realistic evaluation requires Aster-specific policies, capture contracts, owners, and risk approvals.

| Link      | Question to ask                        | Minimum work product               |
|-----------|----------------------------------------|------------------------------------|
| Risk      | What failure would a customer notice?  | Failure statement + affected party |
| Symptom   | Where would it appear?                 | Evidence inventory                 |
| Property  | What exact proposition can be checked? | Per-unit criterion                 |
| Oracle    | Can a deterministic rule decide?       | Validator or Judge design          |
| Trust     | How do we catch wrong verdicts?        | Reference sample + controls        |
| Dimension | What sort of harm is this?             | Dimension and treatment            |
| Aggregate | How much evidence exists?              | Numerator, denominator, exclusions |
| Gate      | What action follows?                   | Documented release rule            |

## 1.2 Step 1 — State a failure, not a quality slogan

“Answers are good” is not testable. “Aster tells a customer that a refund of $120 is available when the governing policy permits only $90” names an observable failure. Describe the triggering context, the party affected, the incorrect behavior, and the potential consequence. Keep likelihood and severity separate: the same observable defect can be rare but unacceptable or common but minor.

A useful risk card has five fields: customer-facing failure; trigger or scenario family; expected authorized behavior; consequence; and system boundary. Do not prematurely select a score such as accuracy. First identify whether the failure is a retrieval miss, a fabricated policy statement, a wrong tool call, or an unconfirmed action. Each calls for different evidence.

## 1.3 Step 2 — Find symptoms in captured Evidence

A measurement only sees its inputs. For policy selection, store the document identifiers and revisions retrieved during the Execution. For supported claims, capture the exact context surfaced to generation, not merely the knowledge base in its latest state. For tool behavior, capture requested tool, normalized arguments, invocation order, outcome, and whether the outcome was confirmed. For operational risk, capture timing boundaries and consumption data with measurement provenance.

If an artifact is absent, do not silently infer it. Distinguish “the system did not retrieve” from “the evaluator did not receive retrieval evidence”. The former may be a subject failure; the latter may make the Oracle unavailable or the property unassessable. Recording that distinction is essential to trustworthy denominators.

## 1.4 Step 3 — Specify separate properties

One failure statement often contains more than one causal proposition. “Wrong refund advice” may arise from selecting an obsolete document, omitting an eligibility condition, stating an unsupported deadline, or misreporting the outcome of a transaction. Splitting these properties improves localization and prevents a single average from hiding a critical failure.

Formulate each property with an explicit population and unit. “Every factual claim in a customer-facing answer is supported by the context actually supplied” is more precise than “faithfulness ≥ target”. A numeric property such as response latency also needs start and stop boundaries, units, timeout treatment, and lower-is-better direction.

## 1.5 Step 4 — Choose the least interpretive competent Oracle

Prefer a Validator for schema, allowed IDs, existence, exact arguments, authorization rules, and captured trajectory facts. Prefer a Judge where the property is semantic and no reliable rule can express it. Use Human Review to establish or challenge reference labels, for disputed interpretations, and where stakes or instrument uncertainty warrant escalation. This ordering is practical guidance consistent with the idea of Validation before Evaluation; it does not imply that every semantic judgment can be replaced by a rule.

A semantic Judge should receive exactly the evidence needed for its criterion. A grounding Judge should not read the current external knowledge base, because it might reward a statement absent from the context supplied to Aster. An outcome Judge should not assume a tool call succeeded simply because it was requested. If a Judge applies multiple criteria, preserve criterion-level verdicts instead of relying only on a blended score.

## 1.6 Step 5 — Establish trust in the instrument

Validator trust starts with a reviewed rule, complete input capture, representative positive and negative fixtures, and explicit behavior when a dependency cannot be evaluated. A rule that checks the wrong field can be deterministic and still invalid.

Judge trust should be supported by a human-reviewed, versioned Reference Set representative of the target decision space, including difficult borderline cases. Where Admission is performed, record the required AQEF Volume VI evidence; a Gate blocks non-admitted Judge Results only when require_admitted_judges is configured. Examine agreement with human reference labels, sensitivity to planted defects, and specificity on clean controls. These are Guide design recommendations unless a referenced AQEF rule explicitly makes them mandatory. Keep tuning items separate from independent Admission evidence; see §2.5, “Tuning a Judge Is Not Admitting It.”

Keep two kinds of failures distinct: the subject system may be wrong, or the measuring Oracle may be wrong. If the latter is not controlled, higher apparent coverage can increase unwarranted confidence. Retest the instrument when its criterion, prompt, model, reference labels, context packaging, or relevant operating distribution changes.

For a Judge configuration, Part 6 separates candidate Selection, independent Admission and per-run Seeded Controls. Treat the configuration and its Evidence capture, not an abstract model name, as the instrument. See Part 7 for metric-specific L1 prompt illustrations and marked L2 variants.

## 1.7 Step 6 — Place the check into a decision system

Assign each property to a Quality Dimension; choose blocking or advisory Gates based on consequence. Under AQEF Volume I, Chapter 6, a Validator-enforced Safety failure is a hard veto, while contextual Safety findings from Judges or Human Reviewers are aggregated with weighting rather than automatically vetoing. Business weighting and Gate thresholds are determined by the Project and its configuration.

Report the assessed population and exclusions clearly, distinguishing an illustrative measurement denominator from AQEF’s normative Aggregate Basis. Under Volume I, Chapter 6, the Gate-facing Aggregate Basis reports actionable and non-actionable Results, and distinct Scenario and Execution counts; Seeded Control Results are excluded. A perfect measured rate over two assessable responses out of a hundred is not a reliable blanket claim of quality.

Minimum basis is an acceptance condition for evidence adequacy, not an excuse to turn unassessed cases into passes. Establish the basis before observing test results, record why it is sufficient, and change it through governance rather than in response to an inconvenient red result.

## 1.8 Worked end-to-end example — Wrong refund amount

Risk statement. Aster tells a customer that $120 will be refunded although current policy and account information authorize only $90. The harm is misleading advice and potentially an incorrect financial transaction. The scenario belongs to an illustrative returns workflow; neither amount is a recommended industry value.

Evidence. Capture the customer request, applicable policy revision, eligibility inputs and calculations, retrieved chunks as presented to generation, Aster response, every relevant tool request and result, and the final customer-facing confirmation.

Properties. P1: required current policy facts are present in retrieved context. P2: each stated amount and eligibility condition is supported by that context and authorized account data. P3: the tool arguments request the expected authorized amount. P4: Aster confirms the outcome only after an appropriate success indication.

Oracles. P1 can use an ID/fact validator against scenario-labelled targets. P2 may need claim extraction and a single-criterion evidence-restricted Judge. P3 is a normalized argument Validator. P4 combines a trajectory Validator with a semantic check of the response when outcome phrasing is not rigidly structured.

Trust design. For P1, include a wrong-revision retrieval and a current-document retrieval. For P2, seed a changed amount, and retain a clean case with a faithful paraphrase. For P3, swap the amount or account ID; retain a correctly authorized call. For P4, plant “refund completed” after an unsuccessful tool result and a clean “refund requested but not confirmed” after the same result. Review reference labels independently of the test candidate.

Aggregation. Report each property separately with its assessed basis; do not average wrong amount, unsupported claim, and unconfirmed action into a single correctness number. Any critical amount or unauthorized-action failure can inform the relevant blocking Gate if the project has approved that rule. A failed Oracle or missing Evidence calls for a trust/basis decision, not an automatic subject failure.
