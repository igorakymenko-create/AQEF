# PART 4 · METRIC REFERENCE

## 4.1 Purpose and boundaries

The reader may enter Part 4 after receiving a numeric score from an external process. First identify the claim implied by that score, the population and unit behind it, the captured Evidence used to calculate it, and the failure consequence. Then test the Oracle before trusting its number in a release decision. The entries answer: what it measures; what it does not; common computation; this guide’s reproducible interpretation; and the controls that reveal whether the instrument can detect a defect without inventing one.

A score is not necessarily an AQEF Result, a Quality Gate, or a calibrated probability. A numeric aggregate may be a diagnostic even when individual decisions are categorical. In this guide, “pass” and “fail” within an example mean the proposed per-property assessment; actual release decisions depend on the configured Contract, effective Results, Aggregate Basis, and Gates.

## 4.2 Universal trust checklist

**1. Validity.** Inspect the claimed property, the input Evidence, decomposition or parsing logic, and expected outputs on a small independently labelled sample. A plausible name is not evidence of construct validity. AQEF connection: Reference Set, separate verification of composed stages.

**2. Sensitivity.** Place known defects of the target class in realistic Evidence and require the Oracle to detect them. Include variations of the defect, not only one memorised wording. AQEF connection: Defect Seeded Controls.

**3. Specificity.** Add clean examples close to the decision boundary and verify that the Oracle does not call them defective. AQEF connection: Clean Seeded Controls.

**4. Agreement with human labels.** For semantic Judges, use independently adjudicated examples and report raw and chance-corrected agreement, reference-version and verdict distribution. AQEF connection: Admission, Volume VI. Predeclare the named chance-corrected statistic and decision threshold before opening the Admission results; keep the evidence separate from tuning data.

4a. Independence of evidence. Were any items used to demonstrate agreement also used to tune this Judge, or exposed to a tuner? Check an independently human-labelled, versioned Reference Set and its exposure history (Volume VI); do not promote working-set fit to Admission evidence.

**5. Stability.** Repeat on the same captured input under the same Oracle configuration; report disagreement and distinguish stochastic Judge variance from subject variance. AQEF connection: Consistency check; re-assessment.

**6. Judge configuration dependence.** Record model, prompt, criteria, settings, and version; recheck a changed configuration rather than inheriting an earlier qualification. AQEF connection: New configuration Admission; drift checks. Distinguish tuning-set optimisation from a fresh Admission assessment (§2.5).

**7. Aggregate Basis.** Report assessed units, distinct Executions, Scenarios, omitted/unassessed units and effective dispositions; a fraction with no denominator is incomplete. AQEF connection: Aggregate Basis, Volume I Ch. 6.

**8. Availability.** Report timeouts, missing inputs, malformed output and access failure separately. Absence of an Oracle verdict is not a defect verdict. AQEF connection: oracle_unavailable and effective Result handling.

## Applying the checklist before a Gate

1.  Freeze a named property, assessment unit, sample population and class-specific error policy.

2.  Freeze the Evidence boundary and verify collection completeness before assessment.

3.  Independently label a Reference Set, including near-miss correct cases and planted defects. Keep its Admission-scored items unexposed to Judge tuners and distinct from tuning items (AQEF Volume VI SHOULD safeguards).

4.  If a Judge is used, document the entire Judge configuration and Admission evidence.

5.  Run defect and clean Seeded Controls for the classes that the Oracle claims to assess.

6.  Evaluate per-unit Results and handle NOT_ASSESSED, inconclusive, unavailable and invalidated outcomes without relabelling them as product success or failure.

7.  Aggregate only eligible Results, show Aggregate Basis, and apply the Project’s own documented Gate threshold and minimum basis.

Normative distinction: AQEF Volume VI defines Judge Admission, but Gate enforcement of admission is configurable with require_admitted_judges. Volume VIII describes Seeded Control behaviours for Validators and Judges. An unenforced recommended check is still recommended practice, not a newly invented MUST.

For every Judge-based metric, apply this shared evidence/Admission checklist to its exact configuration and the independent Reference Set. Each entry retains its own defect control, clean control, unit and measurement-specific limitations; repeated generic checklist text is omitted.

## 4.3 Metric reference entries

Entries M-01–M-37 are organized by measurement family. All procedures explicitly designated Guide-defined are informative examples rather than AQEF requirements. Sources are subject to the source-verification limits recorded in the publication review dossier recorded in the accompanying editorial report.

## Retrieval and grounding

## M-01 · Faithfulness / groundedness

**1. Name and aliases.** Faithfulness / groundedness

**2. What it measures.** The extent to which factual claims in an answer are supported by the context actually retrieved for that Execution.

**3. Why it is used.** R-02; also R-03 where evidence support is tied to citations

**4. What it does not tell you.** It does not establish that the retrieved context was relevant, complete, current, or correct; it does not check whether the user’s question was answered. A well-grounded answer can still rely on obsolete policy.

**5. How it is usually computed. Divide the response into checkable claims, assess each claim against the supplied evidence, and report the proportion supported. Freeze claim boundaries, evidence scope, and scoring rules before evaluation. This Guide defines the operational unit and exclusions below.**

**6. Oracle and dimension.** Semantic Judge on claim–context support; deterministic comparison for exact facts where possible. Primary: Semantic Quality. One unit = an atomic factual claim; per Execution derived from its assessed claims. Prompt examples: §7.1.

7\. Can the result be trusted? — applying the checklist

**Validity and reproducible procedure.** The following is this guide’s proposed measurement procedure, not a universal formula:

1\. Capture the exact response and retrieved context associated with the same Execution.

2\. Split each declarative factual statement into independent claims; mark greetings and offers as nonclaims. Preserve each claim’s source span.

3\. For each claim, using captured context only, classify SUPPORTED, CONTRADICTED, or NOT FOUND. Paraphrase may be supported, but an altered number or condition cannot be assumed equivalent.

4\. Record total claims, supported, contradicted, not found and any unassessable claims. Compute supported / assessable factual claims only when denominator is nonzero.

5\. For this guide’s diagnostic execution verdict: FAIL if any claim is contradicted or any critical policy amount, date or entitlement claim is NOT FOUND; otherwise PASS if all required checks are assessable. Record the ratio alongside that verdict.

**Nothing to assess. No factual claims → NOT_ASSESSED; missing captured context or failed Judge → no trustworthy support assessment, not an automatic FAIL.**

**Over the set.** Execution pass fraction among assessed Executions, alongside claim-support fraction and counts of not-assessed/invalidated/unavailable cases. Keep claims and Executions as separate denominators.

**Sensitivity / specificity / human agreement.** Defect: response says a refund is 45 days while retrieved policy says 30. Clean: response says “within one month” for a source that explicitly states “30 days”, provided the contextual meaning is unambiguous. Reference Set: atomic claim/context pairs with support labels, Project-defined risk labels, and independent adjudication. Check claim splitting and entailment separately.

**Near-boundary examples (illustrative).** Borderline supported: “Refunds are available for 30 days” vs “You can request one within 30 days.” Borderline not found: response adds “processing takes 3–5 days” when the excerpt says nothing about processing.

**Stability and version dependence.** Repeat identical Evidence through the frozen Oracle configuration; quantify classification changes. A changed model, prompt or criterion is a changed Judge configuration and calls for its own admission evidence. Report all assessment exclusions and effective dispositions.

Reproducibility lock — measurement unit and frozen inputs. Atomic factual claims in one frozen response and retrieved-context snapshot; keep source spans and SUPPORTED/CONTRADICTED/NOT_FOUND classifications.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three assessable claims, two supported and one contradicted → support ratio 2/3, diagnostic execution FAIL.

Missing evidence and eligibility. No factual claims → NOT_ASSESSED; missing source capture or failed Judge → UNAVAILABLE, not zero.

**8. Traps.** A high average can conceal one serious claim; claims sourced from general world knowledge can inflate apparent correctness; different splitting granularity changes the denominator.

**9. Not suitable for.** Retrieval recall, answer completeness, current-policy correctness without source version checks.

**10. See also.** R-01, R-02, R-03; Context Recall; Answer Correctness.

**Method variants and interpretation.** All-claims binary (strict); claim ratio (diagnostic); sentence-level judgment (coarser); citation-restricted support (tests a narrower evidence boundary).

****

## M-02 · Context Recall

**1. Name and aliases.** Context Recall

**2. What it measures.** Whether the retrieved Evidence contains the required reference information for the test question.

**3. Why it is used.** R-01; R-05 when the reference corpus has version-specific applicability

**4. What it does not tell you.** It does not establish whether the generator used the facts, answered accurately, or avoided unsupported claims. It also does not mean retrieval ranking is efficient.

5\. How it is usually computed. Two distinct conventions are found in primary method documentation: reference-answer claim coverage estimated with an LLM; and ID-based recall comparing retrieved context IDs with reference IDs. The former measures reference fact support, the latter known-document retrieval.  
Method interpretation: Source boundary: distinguish document-ID retrieval recall from reference-answer claim coverage. The former has a known-document denominator; the latter relies on reference claims and a semantic Oracle. Do not report them as the same score.  


**6. Oracle and dimension.** This guide chooses a Validator for reference-ID recall when IDs are defined and snapshot-specific; for semantic reference fact coverage, this guide recommends a Judge with documented Reference Set agreement; admission is a separately recorded AQEF status. A Gate enforces admission only when require_admitted_judges is configured. Primary: Semantic Quality; one unit = one required reference fact or reference document ID. Prompt examples: §7.2.

7\. Can the result be trusted? — applying the checklist

**Validity and reproducible procedure.** The following is this guide’s proposed measurement procedure, not a universal formula:

8.  For each question, freeze the knowledge snapshot and define the set of required source IDs or, if IDs are unsuitable, independently labelled reference facts.

9.  Capture all retrieved IDs and passages from the same Execution; normalize aliases only under a documented mapping.

10. For ID mode, mark each required ID retrieved if its exact eligible version occurs. For fact mode, judge whether retrieved passages actually contain each required fact (directly or by faithful paraphrase).

11. Compute required units found / required units. Record each missed unit with document version and retrieval rank, if available.

12. For this guide’s diagnostic Execution verdict, PASS only if all designated critical required units are present; otherwise FAIL; keep fractional recall as a separate diagnostic.

**Nothing to assess. No defined required facts or documents → NOT_ASSESSED; an empty retrieval with a nonempty valid requirement set is a measurable zero, not “nothing to assess”.**

**Over the set.** Micro-recall across all required units and macro-recall across assessed questions; report both plus required-unit totals and missing/no-reference rows.

**Sensitivity / specificity / human agreement.** Defect: remove the one required eligibility clause from retrieval while keeping distractor documents. Clean: include the correct clause in a differently ordered but semantically equivalent passage. Reference Set: labelled questions, needed facts or source IDs, snapshot versions and near-relevant distractors. Validate the reference design itself.

**Near-boundary examples (illustrative).** Borderline found: required refund deadline expressed with equivalent explicit wording. Borderline absent: a retrieved title mentions refunds but the deadline is not present.

**Stability and version dependence.** Repeat identical Evidence through the frozen Oracle configuration; quantify classification changes. A changed model, prompt or criterion is a changed Judge configuration and calls for its own admission evidence. Report all assessment exclusions and effective dispositions.

Reproducibility lock — measurement unit and frozen inputs. Freeze required reference IDs or independently labeled required facts and eligible corpus versions; compare with captured retrieved passages.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four required facts, three retrieved → recall 3/4; one designated critical fact missing → diagnostic execution FAIL.

Missing evidence and eligibility. No defined reference → NOT_ASSESSED; a valid requirement with empty retrieval → 0/4.

**8. Traps.** Judging the answer instead of retrieved context; using current knowledge base rather than captured retrieval; mixing ID recall with semantic claim coverage under one series.

**9. Not suitable for.** Faithfulness, citation validity, quality of final answer, ranking efficiency.

**10. See also.** R-01, R-05; Faithfulness; Context Precision.

**Method variants and interpretation.** ID-based recall (deterministic if reference IDs are reliable); reference-fact coverage (semantic); retrieval recall@k (rank cutoff matters).

****

## M-03 · Task Completion / task success

**1. Name and aliases.** Task Completion / task success

**2. What it measures.** Whether the agent achieved the observable authorised end state of the task under its stated constraints.

**3. Why it is used.** R-06, R-07; R-11 if completion relies on prohibited side effects

**4. What it does not tell you.** It does not show that the trajectory was efficient, that intermediate tool choices were ideal, or that unauthorised side effects were absent unless these are included in the success predicate.

**5. How it is usually computed. Evaluate success against predefined task-specific completion criteria. The Guide’s scoring unit and acceptance conditions must be recorded; agent benchmarks are related evidence, not a universal task-completion formula.**

**6. Oracle and dimension.** Validator against authoritative state transitions wherever available; Judge/Human Review only for semantic end states that have no machine-verifiable state. Primary: Functional; Business and Safety secondary. Unit = one task-bearing Scenario Execution. Prompt examples: §7.3.

7\. Can the result be trusted? — applying the checklist

**Validity and reproducible procedure.** The following is this guide’s proposed measurement procedure, not a universal formula:

13. Record the user-authorised target state and relevant constraints before the run (e.g., correct return case created, no duplicate case).

14. Capture tool calls, tool responses and resulting authoritative state from the test environment; do not substitute the agent’s narrative assertion.

15. Compare resulting state to target predicate, including required fields, side effects, and explicitly prohibited actions.

16. Classify SUCCESS only if the target state is observed, constraints are met and an authoritative state check is available; otherwise FAILED if authoritative evidence shows an unmet target or prohibited effect.

17. Record UNKNOWN / NOT_ASSESSED where the outcome cannot be observed reliably; calculate success only over actually assessed tasks.

**Nothing to assess. No actionable task → NOT_ASSESSED. Missing authoritative outcome evidence → UNAVAILABLE/UNKNOWN, not FAIL and not SUCCESS.**

**Over the set.** Completed tasks / assessed task-bearing Executions, with separate counts for failed, unknown, unavailable and task family; show task diversity and constraint-specific failures.

**Sensitivity / specificity / human agreement.** Defect: assistant claims case closed but state shows “open”. Clean: task completed via a different allowed sequence than reference. Reference Set: task goals, authoritative final states, allowed alternative trajectories, failed partial completions; adjudicate semantic outcomes where needed.

**Near-boundary examples (illustrative).** Borderline success: tool returns a new ID, and database read confirms correct record. Borderline failure: the tool returned HTTP success but wrote the wrong customer ID.

**Stability and version dependence.** Repeat identical Evidence through the frozen Oracle configuration; quantify classification changes. A changed model, prompt or criterion is a changed Judge configuration and calls for its own admission evidence. Report all assessment exclusions and effective dispositions.

Reproducibility lock — measurement unit and frozen inputs. Define authoritative task end-state and permitted action constraints before execution; evaluate final state, not response wording.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three assessed tasks, two end states satisfied and one unsatisfied → task success 2/3.

Missing evidence and eligibility. Missing authoritative end-state evidence → UNKNOWN/UNAVAILABLE, excluded from assessed successes and failures.

**8. Traps.** Equating tool-call success with task completion; letting self-reported success determine truth; treating only one action sequence as correct; ignoring side effects.

**9. Not suitable for.** Plan adherence, tool selection accuracy, step efficiency and ethical/safety conformance unless individually encoded.

**10. See also.** R-06, R-07, R-11; Tool Selection Accuracy; Trajectory Match.

**Method variants and interpretation.** Strict all-constraints success; partial milestone completion; weighted subgoal score. Variants do not share the same denominator or outcome definition.

## M-04 · Over-refusal / exaggerated safety refusal

**1. Name and aliases.** Over-refusal / exaggerated safety refusal

**2. What it measures.** The tendency to refuse or deflect requests that are safe, answerable and permitted under the declared task policy.

**3. Why it is used.** R-04; R-10 (paired safety behaviour)

**4. What it does not tell you.** It does not establish resistance to unsafe requests; low over-refusal can coexist with unsafe compliance. A raw refusal rate without answerability labels cannot identify over-refusal.

5\. How it is usually computed. A paired evaluation uses safe prompts likely to trigger excessive refusal with unsafe contrasts. Responses can be differentiated into full refusal, partial refusal and compliance; binary refusal detectors are a simplification.  
Method interpretation:  Count answerable cases only; separately report unanswerable requests and uncertainty in eligibility labels.  


**6. Oracle and dimension.** Judge for substantive refusal/answerability; Validator where structured refusal reasons are explicit. Primary: Semantic and Business, with Safety as a paired category. Unit = one pre-labelled permitted answerable request. Prompt examples: §7.4.

7\. Can the result be trusted? — applying the checklist

**Validity and reproducible procedure.** The following is this guide’s proposed measurement procedure, not a universal formula:

18. Independently label each test request as allowed and answerable under the application policy and available Evidence, before inspecting the response.

19. Assess response as substantive answer, permissible clarification, partial refusal, or full/unjustified refusal. If an essential fact is missing, apply the dataset’s documented clarification policy.

20. For each allowed/answerable case, mark an over-refusal when the response withholds the permitted answer without an allowed reason; do not count an authorised clarification as over-refusal.

21. Compute over-refusals / assessed safe-answerable requests. Also test paired unsafe prompts and report their safe-handling outcomes as a separate measure.

22. For this guide’s per-Execution property, FAIL on demonstrated unjustified refusal; PASS on a satisfactory answer or permitted clarification.

**Nothing to assess. No safe-answerable cases → NOT_ASSESSED. If allowed/answerable status cannot be established, remove the row from assessed denominator and investigate labeling.**

**Over the set.** Over-refusal cases / assessed answerable-and-permitted Executions, separated by benign phrasing, sensitive-but-safe phrasing and ambiguous cases; report unsafe-contrast assessment separately.

**Sensitivity / specificity / human agreement.** Defect: the assistant refuses to summarise a harmless policy excerpt because it contains the word “fraud” as a quoted topic. Clean: it answers that safe question; converse clean for unsafe side: it declines a truly prohibited request. Reference Set: independently labelled safe/unsafe prompts and output categories, including sensitive-but-safe near misses.

**Near-boundary examples (illustrative).** Borderline acceptable: assistant requests the missing order number when required to answer. Borderline over-refusal: assistant gives a generic safety disclaimer instead of answering a permitted factual question with sufficient source evidence.

**Stability and version dependence.** Repeat identical Evidence through the frozen Oracle configuration; quantify classification changes. A changed model, prompt or criterion is a changed Judge configuration and calls for its own admission evidence. Report all assessment exclusions and effective dispositions.

Reproducibility lock — measurement unit and frozen inputs. Freeze independently labeled allowed-and-answerable prompts, and classify substantive refusal rather than a stock refusal phrase.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Ten allowed-answerable requests and two unjustified refusals → over-refusal 2/10.

Missing evidence and eligibility. Ambiguous permissibility → review before denominator inclusion; no eligible prompts → NOT_ASSESSED.

**8. Traps.** Using raw refusal rate; rewarding answer-at-all-costs; unlabelled ambiguous rows; conflating partial refusal with no answer.

**9. Not suitable for.** Measuring safety compliance on prohibited prompts; estimating leakage or jailbreak resistance alone.

**10. See also.** R-04, R-10; Refusal Rate; Unsafe-response Rate; Task Completion.

**Method variants and interpretation.** Strict full-refusal count; count of partial+full unjustified refusals; weighted impact on task completion. Document the treatment of legitimate clarification and partial compliance.

Two-sided moderation fixtures (Guide practice): include hard negatives—benign technical, medical or idiomatic requests with suspicious vocabulary—and hard positives—harmful intent stated indirectly, by euphemism or by context. Record false refusal and missed-harm outcomes separately on the two difficult groups. A typical-traffic sample can omit both groups and therefore cannot estimate either error rate on them. Trusting the Oracle requires independently reviewed labels from each side. A keyword-only rule can block benign language and miss harmful intent expressed indirectly. Hard negatives play the same diagnostic role as clean controls for a Judge (Volume VIII, Seeded Controls).

## M-05 · Context precision

1\. Name and common aliases

Context precision. Context ranking precision.

2\. What it measures

Whether relevant retrieved passages appear high in the ranked list; it is rank sensitive.

3\. Why it is used

Relevant risk entries: R-01. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not establish that all necessary policy passages were retrieved.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For each captured ordered retrieval list, mark each chunk relevant to the question and approved answer. At every relevant rank r ≤ K calculate precision@r and average these values over relevant retrieved items in top K (Guide AP@K). Report precision@K separately as the relevant fraction within the cutoff. When no relevant item is retrieved, record AP@K as NOT_ASSESSED under this Guide convention and report the zero-relevant retrieval failure separately. Freeze the cutoff and treatment of duplicate chunks.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
The method below is a Guide-defined variant; its exact inputs, units and denominator must be disclosed.

6\. Oracle and AQEF dimension · Prompt examples: §7.5

Judge for semantic relevance; Validator for pre-labelled document IDs; Semantic/Functional; per-Execution retrieval list.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: move an unrelated but keyword-matching policy above the governing passage. Clean: legitimate supporting paraphrase or overlapping chunk correctly ranks high. The Reference Set contains query, approved policy, chunk relevance and adjudicated ordering labels; confirm ranking changes do not alter Oracle labels. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze the ordered retrieval list, chunk relevance labels, cutoff K, duplicate policy and rank-sensitive statistic. This Guide defines average precision at K (AP@K) as the mean of precision@r at ranks where a relevant item appears, with the declared denominator and no unannounced substitutions.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Top-4 relevance labels \[1,0,1,0\]: precision@1 = 1, precision@3 = 2/3, AP@4 = (1 + 2/3)/2 = 5/6 ≈ 0.8333, whereas precision@4 = 2/4 = 0.5. An implementation returning 0.5 for this AP@4 fixture has used the wrong statistic.

Missing evidence and eligibility. An eligible query with an empty retrieved list has retrieval coverage zero; do not report AP@K as zero without a documented empty-result convention. A nonempty list with zero relevant retrieved items has AP@K NOT_ASSESSED for this Guide’s conditional ranking procedure, accompanied by an explicit zero-relevant count and a separate recall/coverage result. Missing or uncalibrated relevance labels =\> UNAVAILABLE.

8\. Traps of the metric itself

Duplicate chunks inflate score; one relevant passage can hide missing material; different relevance definitions change scores.

9\. Not suitable for

Do not use as the sole measure of coverage.

10\. See also

Context recall, context relevance; R-01.

## M-06 · Context relevance

1\. Name and common aliases

Context relevance. Passage-to-question pertinence.

2\. What it measures

How pertinent retrieved material is to the user's question.

3\. Why it is used

Relevant risk entries: R-01. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not prove the passage contains the necessary answer or that claims are supported.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Label every retrieved passage irrelevant, partially relevant, or fully relevant against the user question alone using an explicit three-level rubric. Map labels to 0, 0.5 and 1, then take their mean for each Execution; report empty retrieval separately. This is the Guide's procedure, not the only meaning of the name.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
The method below is a Guide-defined variant; its exact inputs, units and denominator must be disclosed.

6\. Oracle and AQEF dimension · Prompt examples: §7.6

Semantic Judge (record configuration, calibration evidence and Admission status; a Quality Gate enforces admission when require_admitted_judges is set); Semantic; per-Execution passages and aggregate.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: same topic but wrong jurisdiction. Clean: shorter passage containing the relevant policy despite different wording. Reference Set balances borderline and exact-match examples; judge blind labels before Admission. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze one query, retrieved chunk boundaries, and the Guide’s ordinal rubric: irrelevant = 0, partially relevant = 0.5, fully relevant = 1. The per-Execution result is the arithmetic mean of these chunk scores. Do not substitute binary relevant-chunk fraction or change cutoffs without naming a separate variant.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Five chunks labelled \[fully relevant, partially relevant, irrelevant, fully relevant, irrelevant\] receive \[1,0.5,0,1,0\]; Guide context relevance mean = 2.5/5 = 0.5. A binary relevant-chunk fraction is a different statistic even if it happens to agree in another fixture.

Missing evidence and eligibility. No retrieved chunks =\> report coverage zero when retrieval was expected; ordinal relevance mean is NOT_ASSESSED because its denominator is zero. Missing question or adjudicated reference =\> NOT_ASSESSED; unavailable Judge/Oracle evidence =\> UNAVAILABLE. Keep absence of retrieval distinct from poor relevance of retrieved chunks.

8\. Traps of the metric itself

Topical overlap looks relevant; long passages dilute evidence; mean hides one crucial irrelevant passage.

9\. Not suitable for

Not for determining factual coverage or grounding.

10\. See also

Context precision, context recall; R-01.

## M-07 · Answer relevance

1\. Name and common aliases

Answer relevance. Response relevance / response relevancy.

2\. What it measures

Whether the response addresses the user's request without material diversion.

3\. Why it is used

Relevant risk entries: R-02,R-04. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not test truth, source support, or task completion.

5\. How it is usually computed; this Guide's procedure



Guide procedure: identify the user's primary requested outcome and any required subquestions; have a Judge with documented calibration and admission status label substantive response segments directly responsive, incidental, or off-task. Mark one Execution satisfactory only if the primary request is addressed and no required subquestion is ignored. Record responsive-segment ratio for diagnostics. Contrast with published reverse-question embedding approach.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
The method below is a Guide-defined variant; its exact inputs, units and denominator must be disclosed.

6\. Oracle and AQEF dimension · Prompt examples: §7.7

Judge with documented Admission status; Semantic; per-Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: fluent response about delivery when the question asks refund eligibility. Clean: concise response using unexpected wording that answers both subquestions. Reference Set includes distractor responses and valid alternatives. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze the user question, answer, labeling rubric and Judge configuration. Measure the explicitly defined Guide-level response relevance outcome.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three independently labeled questions with relevance judgments \[1,1,0\] → binary relevant-answer fraction 2/3.

Missing evidence and eligibility. No answer produced → task outcome handled separately; no qualified relevance Judge → UNAVAILABLE.

8\. Traps of the metric itself

Semantic embeddings reward topicality without answers; verbosity inflates overlap; refusal can be relevant but unhelpful.

9\. Not suitable for

Not for correctness, faithfulness, or success of external actions.

10\. See also

Faithfulness, answer correctness, over-refusal; R-02/R-04.

## M-08 · Answer correctness

1\. Name and common aliases

Answer correctness. Factual correctness / answer accuracy.

2\. What it measures

Agreement between the factual content of a generated answer and a designated reference answer.

3\. Why it is used

Relevant risk entries: R-02,R-05. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not show how the answer was obtained or whether citations support it.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Split the approved reference into atomic required facts and the response into claims. Pair semantically equivalent facts, label each required fact present/absent and each response claim correct/incorrect against the reference, then record required-fact recall and incorrect-claim count. Execution fails on an incorrect critical fact; report both diagnostics, not an undocumented combined score.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
The method below is a Guide-defined variant; its exact inputs, units and denominator must be disclosed.

6\. Oracle and AQEF dimension · Prompt examples: §7.8

Judge with documented Admission status or Validator for explicit values; Semantic; per Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: change the eligibility deadline from 30 to 45 days. Clean: accurately paraphrase the policy including condition and exception. Reference Set includes omissions and plausible additions; human-label risk significance before Judge scoring. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Use independent reference answers and atomic reference facts; separate correct supported facts from false statements and missed required facts.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Reference has four required facts, answer covers three accurately and adds one incorrect claim → recall 3/4 and precision 3/4, F1 = 0.75; critical wrong claim triggers separate veto only if configured in the Contract.

Missing evidence and eligibility. No reference facts → NOT_ASSESSED; no valid assessor → UNAVAILABLE.

8\. Traps of the metric itself

Incomplete reference penalizes legitimate detail; correctness may not equal faithfulness; average obscures monetary misstatements.

9\. Not suitable for

Not for evaluating citation fidelity without cited passages.

10\. See also

Faithfulness, context recall; R-02/R-05.

## M-09 · Citation precision / recall

1\. Name and common aliases

Citation precision / recall. Citation support and coverage.

2\. What it measures

Two distinct questions: (1) what share of assessable claim–citation edges actually supports its linked factual claim (pair-level precision), and (2) what share of citation-required atomic claims has at least one supporting citation (claim-level recall). Their measurement units and denominators differ.

3\. Why it is used

Relevant risk entries: R-03. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

Neither measure proves retrieval completeness, policy currency, or overall answer truth.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Identify atomic factual claims and prelabel which require citations. Form one assessable edge for each distinct claim–cited-passage link, including when a single passage is cited for multiple claims. Precision = supported assessable edges / all assessable emitted edges (one edge per distinct atomic-claim-to-cited-passage relationship; not per URL); Recall = citation-required claims with at least one supporting cited passage / all citation-required claims. Declare the handling of repeated identical edges and unresolved citation IDs before scoring; disclose broken IDs and excluded evidence separately. Exclude claims outside the predeclared citation-requirement policy from the recall denominator. Report both metrics with their respective counts.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
Method interpretation and limits:  Explicitly record policy for which claims require citation, support labels, unresolved IDs and denominator.

6\. Oracle and AQEF dimension · Prompt examples: §7.9

Validator for valid identifiers and Judge for semantic support; Semantic/Functional; per Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: correct answer cites a passage that does not state the condition. Clean: same claim cites an accurate governing excerpt. Reference Set includes independent passage-support and citation-requirement labels, including permissible uncited general framing. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze a claim set C, citation spans, and source snapshots. Judge each claimed citation edge as supporting or not; independently mark which citation-required claims have at least one valid supporting edge.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four emitted citation edges, three support their linked claim → citation precision 3/4. Five citation-required claims, three with valid supporting citation → citation recall 3/5. A separate graph-edge control: one citation span supporting two independently assessed claims is two claim–citation edges, not one citation edge. If both edges support their claims, precision is 2/2; counting only one URL as the denominator would be incorrect.

Missing evidence and eligibility. If no citation-required claims → recall NOT_ASSESSED; if none emitted but required claims exist → recall 0, precision undefined (report N/A).

8\. Traps of the metric itself

Citation count is not support; duplicate citations inflate totals; unclear citation-required policy distorts recall.

9\. Not suitable for

Not appropriate without a declared citation policy and captured passages.

10\. See also

Faithfulness, context precision; R-03.

## Agents and tools

## M-10 · Tool selection accuracy

1\. Name and common aliases

Tool selection accuracy. Tool-choice correctness.

2\. What it measures

Whether an agent chose an allowed, appropriate tool for an observed decision.

3\. Why it is used

Relevant risk entries: R-06. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not prove argument correctness, final success, or safety of composite effects.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For each scenario define acceptable tools per decision point, including equivalent valid tools; parse captured calls; mark a decision point correct if the chosen tool belongs to its allowed set. Record unexpected calls as separate errors; Execution score = correct decision points / assessed decision points, with a critical wrong-tool veto where specified by scenario.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
Method interpretation and limits: published tool-call accuracy variants can score a tool-call sequence jointly. Tool-choice accuracy here counts locally prelabelled allowed choices per decision point; do not attribute this ratio to the cited aggregate metric.

6\. Oracle and AQEF dimension

Validator when allowed-choice sets fixed; Functional; per call and per Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: billing cancellation tool selected instead of invoice lookup; clean: alternate documented lookup tool yielding same authorized information. Reference Set comprises alternate acceptable trajectories with labelled choices. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze each action opportunity and set of allowed/expected tool choices including a valid no-tool decision; score tool identity independently from argument and timing validity.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Five eligible decisions, four select an accepted tool/no-tool decision → selection accuracy 4/5.

Missing evidence and eligibility. Missing trace prevents classification → UNAVAILABLE; not an incorrect tool choice.

8\. Traps of the metric itself

Exact path matching rejects valid alternatives; no-call flows can be correct; tool match can still cause an unsafe effect.

9\. Not suitable for

Not for action authorization or final outcome.

10\. See also

Argument correctness, trajectory match; R-06.

## M-11 · Argument correctness

1\. Name and common aliases

Argument correctness. Tool parameter accuracy.

2\. What it measures

Whether required tool-call arguments match the intended, authorized values.

3\. Why it is used

Relevant risk entries: R-06. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not show whether the right tool was chosen or whether an action succeeded.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For every relevant actual call identify applicable reference parameter constraints. Normalize only documented equivalences such as date format; test required fields and prohibited fields separately. Record call pass only if all required and protected fields satisfy the contract. Execution value is passing calls / assessable relevant calls; missing calls are counted by selection/trajectory measurement.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
Method interpretation and limits: argument-level checks use locally approved equivalence/normalisation constraints. A valid schema does not imply correct customer ID or authorised intent. Distinguish missing call from incorrect arguments.

6\. Oracle and AQEF dimension

Validator; Functional; per call.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: uses another customer's account ID with valid schema; clean: equivalent canonical date format permitted by the contract. Reference Set contains exact references, optional defaults and protected cross-account fields. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze expected schema, required arguments, equivalence rules and tool signature version; normalize JSON key order only, never semantic amounts, units, identities or time zones.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three captured calls, two match required argument values, one uses wrong amount → argument accuracy 2/3. Distinguish an observed call with wrong arguments (a scored failure) from a required call that never occurred (selection/trajectory failure), and from a call whose telemetry was lost (UNAVAILABLE). These cases must not be combined in the 2/3 denominator.

Missing evidence and eligibility. Absent call in a required-call scenario is tool-selection failure; missing telemetry is UNAVAILABLE for argument scoring (and prevents treating that call as passed), not a fabricated argument failure; record expected-call omission separately.

8\. Traps of the metric itself

Schema validity mistaken for semantic correctness; tolerances invented post hoc; optional fields silently dropped.

9\. Not suitable for

Not suitable when acceptable argument equivalence is undefined.

10\. See also

Tool selection, action boundaries; R-06/R-11.

## M-12 · Trajectory match

1\. Name and common aliases

Trajectory match. Tool-call path / step-sequence conformity.

2\. What it measures

Whether an observed action path meets the workflow's necessary dependencies and permitted order.

3\. Why it is used

Relevant risk entries: R-06,R-07. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not itself prove task completion or justify every step's business purpose.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Represent the reference workflow as mandatory precedence edges, optional alternatives and forbidden edges. Map actual calls to events; count satisfied mandatory edges and hard violations. Pass one Execution when every mandatory dependency is satisfied and no forbidden edge occurs; report optional-path coverage as diagnostic.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
Method interpretation and limits: precedence-edge and permitted-alternative graph checks differ from exact ordered sequence match and flexible tool-call matching. Publish workflow graph and ambiguity rules before scoring.

6\. Oracle and AQEF dimension · Prompt examples: §7.10

Validator when graph explicit, Judge for semantic equivalence; Functional; per Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: submits refund before obtaining customer approval; clean: two independent reads interchanged without violating constraints. Reference Set captures both legal orders and illegal shortcuts. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze an expected admissible sequence or partial-order dependency graph; compare recorded ordered calls, not unverifiable hidden reasoning.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Reference requires lookup before update; 2 traces satisfy this ordering and 1 performs update first → order-conformance 2/3.

Missing evidence and eligibility. No ordered trace when tracing required → UNAVAILABLE; alternative valid sequence accepted only if predeclared.

8\. Traps of the metric itself

One golden sequence over-constrains agents; hidden tool calls corrupt ordering; complete path can still have wrong arguments.

9\. Not suitable for

Not for declaring action outcome without tool-result checks.

10\. See also

Argument correctness, task completion; R-06/R-07.

## M-13 · Step efficiency

1\. Name and common aliases

Step efficiency. Action-path efficiency / excess-step ratio.

2\. What it measures

Unnecessary agent work relative to a valid task path.

3\. Why it is used

Relevant risk entries: R-06,R-12. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not guarantee safety or correctness and can penalize necessary verification.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For each passed task assign a validated lower-bound reference action count allowing multiple legitimate strategies. Count meaningful actual tool calls, excluding harness-only instrumentation. Diagnostic ratio = reference minimum / observed meaningful calls (cap at 1) and report raw excess calls. Do not compute a success-quality score for failed tasks.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
The method below is a Guide-defined variant; its exact inputs, units and denominator must be disclosed.

6\. Oracle and AQEF dimension · Prompt examples: §7.11

Validator for count, Human/Judge to validate equivalent paths; Operational/Functional; per completed task.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: same read repeated without a changed input; clean: extra fraud check explicitly required by policy. Reference Set contains alternative efficient and necessary longer routes. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze task-success criterion and efficient baseline minimum steps n_min; count actual observable steps n only on completed comparable tasks.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). For completed tasks with n_min=3 and observed n=5, efficiency ratio 3/5.

Zero-boundary and retry counter-control. An eligible completed task with a verified minimum of three meaningful calls and five observed meaningful calls, including one subject-level reattempt, scores 3/5 only if all five are in the declared meaningful-call boundary. Harness-only retries before any subject Response are recorded separately, not silently counted as agent steps. If the validated minimum is zero, do not divide by zero or report perfect efficiency; mark the ratio NOT COMPUTABLE and report observed steps.

Missing evidence and eligibility. Task incomplete or n_min undefined → efficiency NOT_ASSESSED; do not reward a short failed execution.

8\. Traps of the metric itself

Optimizing steps can remove safeguards; retries inflate work; shorter can mean incomplete.

9\. Not suitable for

Not a replacement for correctness or safety.

10\. See also

Latency, cost, trajectory match; R-06/R-12.

## M-14 · Plan adherence

1\. Name and common aliases

Plan adherence. Conformance with an approved plan.

2\. What it measures

Whether agent behavior follows mandatory commitments of an approved, still-applicable plan.

3\. Why it is used

Relevant risk entries: R-06,R-07. It helps localize a suspected defect without replacing the other checks in the risk entry.

4\. What it does not tell you

It does not show that the plan itself was good or that the resulting state is correct.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Capture the approved plan and explicit user-authorized updates; decompose it into mandatory commitments, optional tactics and prohibited deviations. Check actual calls and results against each commitment. Execution passes if all mandatory commitments hold and no unapproved deviation occurs; missing approved plan = not assessed.

Variation rule: a semantic Judge, an exact-match check and a reference-based comparison can answer different questions even under the same metric name. Identify the variant in every report.  
  
Method interpretation and limits: no universal primary plan-adherence equation established. Score mandatory approved obligations against captured trajectory; updated user approval supersedes original plan only when evidenced.

6\. Oracle and AQEF dimension · Prompt examples: §7.12

Validator for explicit events, Judge for semantic obligations; Functional/Business; per Execution.

7\. Can the result be trusted?

Validity: verify units and captured inputs against the property, not merely the metric label. Sensitivity/specificity: Defect: agent skips required user confirmation; clean: user explicitly approves an amended path before execution. Reference Set includes revised and original plans with audit of consent. Test the extraction or normalization step independently from the final decision where either may fail. Human agreement: label the Reference Set independently and record the named chance-corrected agreement measure where Judge Admission applies. Stability: rerun unchanged inputs; changes in model, instructions or criteria require configuration-specific Admission as AQEF defines. Basis: report assessed items, excluded items and distinct Executions/Scenarios. Availability: a failed Oracle is not a failed subject.

Reproducibility lock — measurement unit and frozen inputs. Freeze externally observable required plan obligations and approved equivalences before execution; evaluate completion/order for observable obligations only.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four plan obligations, three met → adherence 3/4; a missing mandatory obligation fails the predeclared diagnostic verdict.

Mandatory-versus-optional control. Suppose a plan contains three mandatory obligations and two optional tactics. All three mandatory obligations are met, neither optional tactic is used, and no prohibited deviation occurs: mandatory adherence is 3/3 = 1.00 and the execution may pass. Scoring 3/5 = 0.60 would incorrectly treat optional tactics as obligations. If one mandatory obligation is unmet, adherence is 2/3 and the declared all-mandatory diagnostic verdict fails.

Missing evidence and eligibility. No approved and observable plan, or an unverifiable private plan step → NOT_ASSESSED (not an automatic pass); missing tool trace → UNAVAILABLE.

8\. Traps of the metric itself

Treating suggested plan as fixed; equating compliance with success; overlooking revised instructions.

9\. Not suitable for

Not for tasks without an explicit plan or traceable commitments.

10\. See also

Trajectory match, task completion; R-06/R-07.

## Multi-turn dialogue

## M-15 · Knowledge Retention

1\. Name and common aliases

Knowledge Retention; Memory retention; knowledge attrition.

2\. What it measures

Assistant preserves relevant facts supplied by the user across subsequent turns.

3\. Why it is used

Relevant risk entries: R-08. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not establish reasoning correctness, global knowledge accuracy or successful task completion.

5\. How it is usually computed and documented variants



6\. Oracle type and AQEF dimension · Prompt examples: §7.13

Semantic Judge for paraphrases (Admission required when the project enables require_admitted_judges); Validator for explicit dates/IDs. Semantic, assessed across multi- turn Executions.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect control: customer changes delivery day to Friday; assistant later states Wednesday. Clean: the assistant uses the new Friday date while summarising the former Wednesday date as history. Reference Set should include overrides, negation, ambiguity, repeated questions that genuinely request confirmation, and long-gap retention. Independently assess fact extraction and later-turn judgement; calibrate Judge and use defect and clean controls. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze a turn-indexed ledger of user-provided facts, corrections and their applicable windows; assess a fact only at later eligible recall opportunities.

Worked arithmetic/control fixture (illustrative; not observed Judge performance). Five eligible fact-recall opportunities; four accurate recalls and one false recall → Guide-defined retention 4/5.

Missing evidence and eligibility. No later recall opportunity → NOT_ASSESSED; unreadable earlier turns → UNAVAILABLE.

8\. Traps of the metric itself

A turn without an applicable fact is counted as a good retention turn; obsolete facts are treated as current; inconsistent user statements are unresolved; anonymisation changes fact identity.

9\. Not suitable for

Not a measure of memory persistence outside the declared conversation or an excuse to retain user information without permission.

10\. See also

Coherence, conversation completeness; R-08.

## M-16 · Conversation Completeness

1\. Name and common aliases

Conversation Completeness; Intent satisfaction; conversation goal coverage.

2\. What it measures

Whether user intentions raised over a dialogue were satisfactorily addressed.

3\. Why it is used

Relevant risk entries: R-08, R-07. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not prove any claimed external action really took effect, or whether the response was safe.

5\. How it is usually computed and documented variants



6\. Oracle type and AQEF dimension · Prompt examples: §7.14

Judge for semantic satisfaction, Validator for tool outcome evidence; Semantic / Business, conversation- level.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: cancellation completed, refund question ignored. Clean: explicit user cancels refund request, so completing cancellation alone satisfies remaining applicable intent. Reference Set labels hierarchy, amendments and truly completed actions; plant missing secondary intentions and legitimate cancellations as separate controls. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze explicit user requests and completion criteria per conversation; count independently assessable obligations rather than impressionistic overall satisfaction.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four required deliverables; three furnished with sufficient evidence → obligation coverage 3/4; if a mandatory deliverable is missing, the conversation is not fully complete.

Atomic-obligation boundary control. Three separately required deliverables are recorded: a source summary, a risk table and a final recommendation. A response supplies the summary and recommendation but only a heading for the risk table: coverage is 2/3, not 3/3. A partial heading does not satisfy the underlying deliverable. Freeze the obligation decomposition before reading outputs; separate ambiguous fulfillment from verified completion.

Missing evidence and eligibility. No actionable obligations → NOT_ASSESSED; truncated final turns → UNAVAILABLE.

8\. Traps of the metric itself

Double counting repeated intents; assigning satisfaction based on agent assertion; user leaving counted as success; unbounded conversations compared with short complete tasks.

9\. Not suitable for

Not an independent estimate of user satisfaction or general product usefulness.

10\. See also

Task Completion, Knowledge Retention; R-07/R-08.

## M-17 · Role Adherence

1\. Name and common aliases

Role Adherence; Persona adherence; role compliance.

2\. What it measures

Whether each assistant turn stays within a specified role definition throughout dialogue.

3\. Why it is used

Relevant risk entries: R-08, R-10. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not by itself measure factual accuracy, policy safety or kindness.

5\. How it is usually computed and documented variants



6\. Oracle type and AQEF dimension · Prompt examples: §7.15

Semantic Judge for interpretation (Admission required when the project enables require_admitted_judges); Validator for explicit prohibited statements. Semantic / Business; across turns.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: customer-support assistant impersonates a financial regulator after a user request. Clean: assistant quotes a customer saying “act as a regulator” while staying in its role. Reference Set includes role amendments and quoted adversarial text. Controls differentiate genuine violations from quotation. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze permitted role constraints (tone, authority, domain, disclosure) and independently labeled violation opportunities; report violations and compliant opportunities separately.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Ten role-constrained eligible responses, one violates a specified constraint → adherence 9/10.

Missing evidence and eligibility. No testable role constraint → NOT_ASSESSED; ambiguous constraint → human adjudication rather than automatic compliance.

8\. Traps of the metric itself

Brand voice confused with access permissions; legitimate refusal mislabelled off-role; role changes not versioned; mutually inconsistent style instructions.

9\. Not suitable for

Not suitable as a replacement for privacy, safety or action authorization tests.

10\. See also

Coherence, Toxicity; R-08/R-10.

## M-18 · Coherence

1\. Name and common aliases

Coherence; Cross-turn coherence; dialogue consistency.

2\. What it measures

Whether successive assistant statements and transitions remain logically compatible and relevant to the conversational state.

3\. Why it is used

Relevant risk entries: R-08. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not establish source grounding, ability to recall every customer fact or completion of the user’s task.

5\. How it is usually computed and documented variants

Primary or method source: No unique primary definition was established for this generic coherence metric; the classification rubric and denominator below are Guide-defined. Related multi-turn studies provide context, not an identical formula.

6\. Oracle type and AQEF dimension · Prompt examples: §7.16

Semantic Judge for implicit contradictions (Admission required when the project enables require_admitted_judges); Validator for explicit structured fields. Semantic, multi-turn.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: assistant promises no charge then asserts that identical charge is mandatory without any intervening change. Clean: policy updated after customer supplies new eligibility condition and assistant explains change. Reference Set includes temporally ordered updates, paraphrases, and contradictions across distant turns. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze multi-turn dialogue and contradiction reference pairs, track which prior propositions remain in scope, and judge coherence by eligible linked-turn transitions.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Six labeled eligible transitions, five consistent and one unresolved contradiction → coherence 5/6.

Transition-eligibility control. Of seven apparent message transitions, one lacks the preceding message and cannot be assessed; among the six assessable transitions, five are coherent and one contradicts an earlier confirmed fact. Report coherence 5/6, with one UNAVAILABLE transition. Do not score it 5/7 or silently label the missing transition coherent.

Missing evidence and eligibility. Single-turn input without transitions → NOT_ASSESSED; missing history → UNAVAILABLE.

8\. Traps of the metric itself

Coherent but false narratives pass; lack of comparable pairs treated as perfection; dialogue drift conflated with user change; multiple contradictions from a single source double counted.

9\. Not suitable for

Not a standalone metric of truthfulness or retention.

10\. See also

Knowledge Retention, Conversation Completeness; R-08.

## Safety

## M-19 · Toxicity

1\. Name and common aliases

Toxicity; Toxic language incidence; inappropriate-output occurrence.

2\. What it measures

Incidence of harmful or offensive language under a stated classification policy.

3\. Why it is used

Relevant risk entries: R-10. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not prove absence of other unsafe behavior, bias, leaks or successful jailbreaks.

5\. How it is usually computed and documented variants

 Illustrative procedure of this Guide: Define policy categories and scope before running. (1) Capture final user-visible output and channel. (2) Mark substantive generated text per category using a validated classification rubric, preserving quoted or educational context. (3) Flag Execution where a prohibited category is positively identified, else pass if complete and in-scope. (4) Aggregate violations / assessed outputs, broken down by category and input stratum; keep indeterminate and unavailable outputs separate.  
  
Method interpretation and limits: Eligibility: predeclare a classification policy with context, category and severity boundaries, and identify assessed user-visible output units before testing. Rate = outputs with confirmed prohibited-category violations / fully assessed eligible outputs. Unavailable, truncated or unclassified units are NOT_ASSESSED. Do not treat a toxicity classifier probability as incident frequency. Quote and critique scenarios are clean controls. Report classifier flags and  verified violations separately.

6\. Oracle type and AQEF dimension · Prompt examples: §7.17

Validator for restricted exact patterns; Judge (with documented calibration/admission status) or Human Reviewer for contextual category interpretation. Safety, per response.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: assistant directs an unprompted personal insult at customer. Clean: customer asks what a quoted insult means, and assistant neutrally classifies it without targeting anyone. Reference Set contains quoted, negated, dialect and benign-sensitive examples; measure false positives and missed categories independently. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze a documented unacceptable-content rubric and eligible responses; separate severity from binary incident incidence and validate Judge on independent examples.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Two flagged unacceptable responses among 20 assessed outputs → incident rate 2/20.

Missing evidence and eligibility. No assessable response → NOT_ASSESSED; unqualified classifier → UNAVAILABLE; nonzero incident not automatically a configured Gate veto.

8\. Traps of the metric itself

Classifier stereotypes; quoted terms flagged as generated abuse; a toxicity mean conceals rare severe cases; sensitive subject matter equated with toxicity.

9\. Not suitable for

Not an attack-success or overall safety score.

10\. See also

Bias, Refusal Rate, ASR; R-10.

Two-sided moderation fixtures (Guide practice): include hard negatives—benign technical, medical or idiomatic requests with suspicious vocabulary—and hard positives—harmful intent stated indirectly, by euphemism or by context. Record false refusal and missed-harm outcomes separately on the two difficult groups. A typical-traffic sample can omit both groups and therefore cannot estimate either error rate on them. Trusting the Oracle requires independently reviewed labels from each side. A keyword-only rule can block benign language and miss harmful intent expressed indirectly. Hard negatives play the same diagnostic role as clean controls for a Judge (Volume VIII, Seeded Controls).

## M-20 · Bias

1\. Name and common aliases

Bias; Group disparity; biased output occurrence.

2\. What it measures

Unequal or stereotyping behavior across defined counterfactual or matched scenarios.

3\. Why it is used

Relevant risk entries: R-10. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It cannot establish overall fairness without choosing groups, legitimate variables and task context.

5\. How it is usually computed and documented variants



6\. Oracle type and AQEF dimension · Prompt examples: §7.18

Validators for structured treatment; Judges with documented calibration and admission status for stereotyping. Safety / Business, paired-set metric.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: identical service request receives denial in one group-labelled version but approval in the other. Clean: same service terms despite innocuous name substitution. Reference Set explicitly labels justified distinctions; defect and clean controls challenge both sensitivity and overcalling. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Separate paired counterfactual outcome-disparity testing from harmful stereotype-content detection. Freeze invariant task details and only vary one protected-reference cue per pair.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). In a fully eligible cohort of 12 valid, fully assessed matched pairs, two exhibit unjustified outcome differences → disparity 2/12. This is a separate fixture from the 12 candidate pairs below, where two pairs are excluded; report stereotype-content incidents in a separate denominator.

Matched-pair integrity control. Twelve candidate counterfactual pairs are scheduled; ten preserve the task facts and differ only in the declared sensitive attribute, while two change material qualifications and are invalid. If two of the ten valid pairs produce unjustified different outcomes, measured pair disparity is 2/10 = 0.20 with two excluded pairs, not 2/12. This is a paired-case incidence, not a demographic-parity statistic or evidence of intent.

Missing evidence and eligibility. Invalid pairs or changed task facts → exclude with reason; do not interpret statistical disparity alone as intent.

8\. Traps of the metric itself

Names alter confounding context; inappropriate inference about real people; benign factual group differences treated as discrimination; aggregate masks subgroup harm.

9\. Not suitable for

Not for demographics that cannot legitimately be inferred or for definitive real-world discrimination claims from tiny synthetic samples.

10\. See also

Toxicity, over-refusal, role adherence; R-10.

## M-21 · Personal Data Leakage

1\. Name and common aliases

Personal Data Leakage; PII disclosure incidence; confidential marker exposure.

2\. What it measures

Unauthorized exposure of protected information in output or agent actions.

3\. Why it is used

Relevant risk entries: R-10, R-11. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not measure all security compromise and it must not require collecting real secrets in test datasets.

5\. How it is usually computed and documented variants

 Illustrative procedure of this Guide: Use strictly synthetic protected data and explicit authorization matrix. (1) Seed unique canary identifiers only in access-controlled test context. (2) Capture responses, tool arguments and outbound effects. (3) Run deterministic exact-canary detection then context review for reworded sensitive facts. (4) Label unauthorized disclosures, authorized uses and non-disclosures separately; missing channel capture is unavailable, not a pass. (5) Aggregate leaked canaries / exposed synthetic canaries and Executions with leaks / assessable Executions, with exposure and authorization bases.  
  
Method interpretation and limits: Eligibility: define protected synthetic values, who can access them, and captured egress/output channels. Report (a) leaked synthetic values / assessable exposure opportunities and (b) Executions with \>=1 confirmed leak / fully observed eligible Executions. Omitted channel logs = UNKNOWN, not zero leakage. Seed exact-match and semantically restated exposure controls separately; do not test real personal secrets. Specify the authorized audience and observed output channels.

6\. Oracle type and AQEF dimension · Prompt examples: §7.19

Validator for canaries and forbidden destinations; Human/Judge for contextual authorization. Safety, per Execution.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: assistant includes another synthetic customer’s account number in its response. Clean: user gets their own masked identifier under a permitted view. Reference Set covers allowed sharing, redaction and overlapping strings; judge evaluates purpose and authorization, not keyword presence alone. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze canary inventory, permitted disclosure boundary and matching rules before trials; distinguish exact canary exposure from semantic personal-data disclosure reviewed by humans.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Fifteen eligible outputs, one leaks an exact forbidden canary → exact-leak incidence 1/15.

Missing evidence and eligibility. No canaries or disclosure policy → NOT_ASSESSED; redacted output with no raw audit evidence → UNAVAILABLE.

8\. Traps of the metric itself

Real PII inserted into tests; substring false positives; tool-side leak omitted; zero observed leaks treated as complete coverage.

9\. Not suitable for

Not a broad proof of privacy or legal compliance.

10\. See also

Unauthorized Action, ASR; R-10/R-11.

## M-22 · Attack Success Rate

1\. Name and common aliases

Attack Success Rate; ASR; adversarial objective completion.

2\. What it measures

Frequency with which predefined adversarial test cases meet an attacker-specified prohibited objective.

3\. Why it is used

Relevant risk entries: R-09, R-10, R-11. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It does not estimate production attack prevalence, benign task utility or strength against unseen attack strategies.

5\. How it is usually computed and documented variants

 Illustrative procedure of this Guide: Before execution record only benign synthetic attacker goals and safe isolated test environment. (1) Classify injected channel or dialogue-adversarial channel. (2) Declare an objectively observable prohibited outcome without supplying exploit instructions. (3) Capture response, denied actions, actual external effects and instrumentation coverage. (4) Label goal met/not met/unknown independently of benign user-task success. (5) ASR = achieved attacker goals / fully assessable eligible attack cases; report unknown cases, attack families and benign utility in separate columns.  
  
Method interpretation and limits: Eligibility: count only attacks with a predeclared objective, valid bounded test setup and adequate capture of the objective outcome; maintain scheduled, attempted, eligible, achieved, not achieved, and unknown tallies separately. Compare rates only when the success conditions and eligible denominators match. ASR = achieved / eligible assessable attempts. An attack not achieved is NOT evidence that the defender met the legitimate user task. If denominator zero, report NOT_ASSESSED. Outcome detector must be validated using both achieved and non-achieved controls. 

6\. Oracle type and AQEF dimension · Prompt examples: §7.20

Validator where outcome is an observable state; Human/Judge where policy semantics are irreducible. Safety, dataset-level.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect: synthetic unauthorized disclosure occurs in an isolated test. Clean: assistant disregards a malicious instruction embedded in a retrieved document and completes the real task. Reference Set combines detected and non-detected goals and explicitly ambiguous outcomes; score the outcome checker with both control types. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze authorized attack-test scenarios, forbidden attacker objectives and independent success verdict criteria, separating target-system success from Oracle validity.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Eight eligible controlled attacks, two satisfy the prohibited objective → attack success rate 2/8. Counter-control: of eight scheduled attacks, if only six have admissible completed outcomes and two succeed, report 2/6 assessed with 2 unresolved, not 2/8; do not drop unresolved attempts without disclosing the planned cohort.

Missing evidence and eligibility. Invalid control/oracle assessment or missing result → exclude from the assessed-outcome denominator and report separately against the complete scheduled cohort; never classify unresolved outcomes as either attacker success or defense.

8\. Traps of the metric itself

Counting attempted as achieved; counting unknown as defense; focusing only on adversarial prompt while ignoring benign task failure; extrapolating ASR across threat models.

9\. Not suitable for

Not a measure of routine user satisfaction or a standalone Gate metric without contextual risk and reliable instrumentation.

10\. See also

Privacy leakage, refusal, tool authorization; R-09–R-11.

## M-23 · Refusal Rate

1\. Name and common aliases

Refusal Rate; Refusal incidence; response abstention.

2\. What it measures

Proportion of requests where the assistant refuses to perform the requested action.

3\. Why it is used

Relevant risk entries: R-04, R-10. This metric identifies an observable failure class, not a general quality verdict.

4\. What it does not tell you

It cannot distinguish a correct refusal from excessive refusal or unsafe compliance.

5\. How it is usually computed and documented variants

 Illustrative procedure of this Guide: Capture request, expected safety/answerability category, output. (1) Prelabel each request as permitted, prohibited or clarification-needed. (2) Determine whether response substantively refuses the requested content versus asks a legitimate clarification. (3) Label refused / not refused / unclear. (4) Calculate refused / assessable prompts separately for permissible and prohibited categories. (5) Report count and uncertainty without treating higher or lower as unconditionally better.  
  
Method interpretation and limits: Eligibility: prelabel requests as permitted, prohibited, or clarification-required independently from response. Report refusal rate separately within permitted and prohibited strata: refused assessable requests / assessable requests in each stratum. Report over-refusal among permitted requests, and unsafe compliance among prohibited requests, as separate outcomes. A refusal is not necessarily safe; a clarification is not automatically refusal. An overall refusal rate can describe the workload. Use the separate rates for permitted and prohibited requests to assess safety. Empty stratum = NOT_ASSESSED. 

6\. Oracle type and AQEF dimension · Prompt examples: §7.21

Validator for structured refusal reason codes; Judge with documented calibration and admission status for natural language. Safety / Business, per Execution and dataset.

7\. Can the result be trusted? Checklist applied

Judge trust boundary (where a Judge supplies this metric): freeze criterion/rubric and anchors, judge prompt, few-shot examples, model/version, inference settings and evidence boundary; tuning-set agreement is not Admission. For a changed model, prompt or criteria, obtain a fresh Admission record for that configuration. Gate enforcement applies only when require_admitted_judges is declared (Volume VI); keep defect/clean Seeded Controls distinct (Volume VIII).

VALIDITY: ensure the observation channel and scored opportunities correspond to the named property. SENSITIVITY / SPECIFICITY: Defect control for over-refusal: assistant rejects harmless service-hours question because of a misleading keyword. Clean: assistant appropriately declines unauthorized disclosure. A complementary defect control requires catching failure to refuse a genuinely disallowed request; Reference Set must contain both paired categories. HUMAN AGREEMENT: independently label cases and record agreement corrected for chance if Judge Admission applies. STABILITY: rerun unchanged cases and audit version sensitivity. JUDGE DEPENDENCE: changes of criteria, model or prompt are separate configurations requiring appropriate admission. BASIS: report denominator, unassessed opportunities, distinct Scenarios and Executions. AVAILABILITY: a failed Oracle call means no trusted verdict; do not count it as a product fail.

Independent oracle controls: separately challenge (1) eligibility / classification of input, (2) Evidence capture and extraction, (3) property judgement, and (4) numerator/denominator aggregation. Defect and clean controls must exercise both sides of each fallible semantic decision. Record unknown decisions without post hoc relabelling.

Reproducibility lock — measurement unit and frozen inputs. Freeze refusal classifier and eligible prompts; publish unconditional refusal incidence separately from justified-refusal and over-refusal rates.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Of 20 classified prompts, 6 produce substantive refusals → overall refusal rate 6/20; permitted-only refusal rate uses its own permitted denominator.

Stratification counter-control. Ten permitted and ten prohibited requests are assessed. Four permitted requests and six prohibited requests receive substantive refusals. Overall refusal rate is 10/20 = 0.50, but permitted-request refusal rate is 4/10 = 0.40 and prohibited-request refusal rate is 6/10 = 0.60. Do not describe 0.50 alone as safety quality or over-refusal; the request category and response classification remain visible.

Missing evidence and eligibility. Unknown response or ambiguous refusal requires review; no classified prompts → NOT_ASSESSED.

8\. Traps of the metric itself

High refusal percentage celebrated without answerability labels; partial warning equated with refusal; benign sensitive language confuses Judge; category imbalance hides false refusals.

9\. Not suitable for

Not a stand-alone sign of safety or helpfulness.

10\. See also

Over-refusal (M-04), ASR; R-04/R-10.

Two-sided moderation fixtures (Guide practice): include hard negatives—benign technical, medical or idiomatic requests with suspicious vocabulary—and hard positives—harmful intent stated indirectly, by euphemism or by context. Record false refusal and missed-harm outcomes separately on the two difficult groups. A typical-traffic sample can omit both groups and therefore cannot estimate either error rate on them. Trusting the Oracle requires independently reviewed labels from each side. A keyword-only rule can block benign language and miss harmful intent expressed indirectly. Hard negatives play the same diagnostic role as clean controls for a Judge (Volume VIII, Seeded Controls).

## Reference comparison

## M-24 · Exact Match

1\. Name and common aliases

Exact Match — Exact equality; normalized exact match

2\. What it measures

Whether a structured or tightly constrained output equals a specified reference representation.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-05, R-06, R-07. Use only when the observable matches the risk property.

4\. What it does not tell you

A match does not prove that the reference is correct or that a different-but-valid wording is wrong.

5\. How it is usually computed

Use a deterministic Validator on raw emitted bytes when output is defined byte-for-byte. For the normalized variant, specify BEFORE testing whether Unicode normalization, whitespace, case or JSON-key-order normalization is allowed. Compare normalized candidate against approved reference, and return match/not-match. Never infer equivalence through undocumented normalization. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: Guide-defined exact comparison: exact match is an equality predicate after explicitly declared optional normalization; RFC 8259 defines JSON syntax, not an origin for all exact-match measures.

6\. Oracle type and AQEF dimension

Validator; Functional. Use no probabilistic confidence for deterministic equality. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: One response field or entire output, whichever the Contract names. One Execution passes only when all mandatory target fields match; other fields are either excluded by an explicit scope or checked separately. If no reference exists, mark not assessed. Aggregate passed Executions / assessed Executions and report basis and normalization version.

SENSITIVITY AND SPECIFICITY: Defect: change a single digit in a customer-facing refund identifier or amount. Clean: the exact approved token including punctuation. Reference Set: boundary samples with case, whitespace, Unicode lookalikes and intentionally different values; validate the reference fixture and normalization independently.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze exact reference string and a declared byte/string normalization profile (Unicode, case, whitespace); do not silently canonicalize beyond the profile.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three responses vs their references: two identical under the frozen profile, one differs → Exact Match 2/3.

Missing evidence and eligibility. No reference or response text → NOT_ASSESSED/UNAVAILABLE as applicable; empty string is a legitimate value if specified.

8\. Traps of the metric itself

False negatives for harmless paraphrases; over-normalizing distinct identifiers; checking only substring occurrence.

9\. Not suitable for

Open-ended answers or semantic paraphrases, unless a fixed representation is contractually required.

10\. See also

M-25 Schema Validity; M-26 Pattern Match; R-05, R-06.

## M-25 · Schema / JSON Validity

1\. Name and common aliases

Schema / JSON Validity — JSON parse validity; structural schema conformance

2\. What it measures

Whether an output parses as JSON and meets a selected, versioned structural contract.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-06, R-07. Use only when the observable matches the risk property.

4\. What it does not tell you

A structurally valid payload can contain incorrect or unauthorized values and may still fail downstream business rules.

5\. How it is usually computed

First parse the entire captured output with a declared JSON grammar. Then validate the parsed instance against a pinned JSON Schema dialect and schema version; record syntax and structural failures separately. Configure whether extra properties are permitted, how numeric types are evaluated and whether format annotations are asserted under the selected vocabulary. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: JSON syntax validity, schema validation and semantic correctness are separate properties. RFC 8259 supports syntax; JSON Schema supports validation against a stated version and schema.  
  

6\. Oracle type and AQEF dimension

Validator; Functional. Reference: RFC 8259 plus JSON Schema 2020-12. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: One complete output object. Score parse_pass and schema_pass separately; final structural pass requires both. No output for a JSON-required task is failure, while an Execution without a JSON output obligation is not assessed. Aggregate with separate syntax/schema denominators and schema version.

SENSITIVITY AND SPECIFICITY: Defect: omit required customer ID or replace integer with wrong type. Clean: valid reordered property keys where object key order is not significant. Reference Set: approved objects, malformed JSON, unexpected fields, wrong types and schema-version changes. Validate schema itself before testing subject.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze JSON Schema draft, validator implementation, parsing mode and eligible outputs; distinguish syntactically invalid JSON from schema-invalid JSON.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Of ten eligible raw outputs, nine parse as JSON, eight of those nine pass the pinned schema; report overall parse rate 9/10 = 0.90, unconditional schema-valid output rate 8/10 = 0.80, and conditional schema compliance given parseability 8/9 ≈ 0.8889. These are three distinct denominators; do not label 8/9 as the unconditional schema-validity rate.

Missing evidence and eligibility. Missing schema → NOT_ASSESSED; missing capture → UNAVAILABLE; schema-validity denominator is all eligible outputs, not parseable only.

8\. Traps of the metric itself

Conflating parse and schema validity; assuming a format annotation is a hard assertion; accepting partial JSON embedded in prose.

9\. Not suitable for

Semantic grounding, domain authorization, action completion.

10\. See also

M-24 Exact Match; M-26 Pattern Match; R-06.

## M-26 · Pattern Match

1\. Name and common aliases

Pattern Match — Regex match; full-string pattern compliance

2\. What it measures

Whether an output contains or wholly conforms to an explicitly declared pattern.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-06, R-10. Use only when the observable matches the risk property.

4\. What it does not tell you

Matching a pattern neither proves value identity nor absence of other, unsafe content.

5\. How it is usually computed

Define a pinned regular-expression dialect, flags, Unicode handling and full-match versus search semantics. Apply the expression to the exact captured target field. For allowed-format validation prefer full-match; for prohibited-string detection prefer search within the declared scope. Record observed span and pattern version. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: Guide-defined predicate: regex/pattern documentation specifies matcher semantics rather than origin of the metric. Publish full-match vs search mode, flags, Unicode handling and what does not match.

6\. Oracle type and AQEF dimension

Validator; Functional or deterministic Safety when the pattern encodes a hard constraint. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: One field occurrence. Pass a required-format property when full-match succeeds. For a forbidden-pattern property invert the predicate as explicitly specified. A missing required field fails its own presence check, rather than disappearing from the denominator. Report matched, unmatched and unavailable counts.

SENSITIVITY AND SPECIFICITY: Defect: plausible account reference violates checksum-adjacent syntax; clean: matching identifier including allowed hyphen. Reference Set includes near-misses, empty string, multiline content and escaping variations. Independently test the regex on a fixed fixture.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze regex engine, flags, match mode (fullmatch/search) and normalization; prevent unknown multiline/case behavior.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four eligible strings, three pass the pinned fullmatch rule → pattern pass rate 3/4.

Missing evidence and eligibility. No specified pattern → NOT_ASSESSED; regex compilation error → INVALID MEASUREMENT, not system FAIL.

8\. Traps of the metric itself

Accidental partial matches; overly broad patterns that flag harmless output; regular expressions cannot decide contextual safety.

9\. Not suitable for

Semantic quality or nuanced policy compliance without additional checks.

10\. See also

M-24 Exact Match; M-25 Schema Validity; R-06/R-10.

## M-27 · BLEU

1\. Name and common aliases

BLEU — Bilingual Evaluation Understudy; modified n-gram precision

2\. What it measures

How strongly system output overlaps reference translations in n-gram surface form, with a brevity penalty.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-02 (limited diagnostic use). Use only when the observable matches the risk property.

4\. What it does not tell you

A high BLEU score does not establish factual correctness, causal reasoning or sufficient instruction coverage.

5\. How it is usually computed

For the documented corpus-level variant, tokenize hypotheses and one or more references using a frozen tokenizer; calculate modified clipped n-gram precisions for n=1..4 across corpus, combine their logs by fixed weights, and apply corpus brevity penalty using reference lengths. State the chosen reference-length strategy. When any precision is zero, use the documented zero-handling policy; do not silently substitute sentence-level smoothing. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: BLEU is a modified n-gram precision metric with brevity penalty; specify tokenization, references, smoothing and corpus/sentence aggregation. Not proof of factual equivalence.

6\. Oracle type and AQEF dimension

Deterministic scoring Validator of reference overlap, not a semantic Judge; Semantic diagnostic only. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: Primary unit is a fixed evaluation corpus, not one Execution; show corpus BLEU with hypothesis count, reference count and segment lengths. If a sentence-level variant is used, name its smoothing and report separately; do not average sentence scores as a substitute for corpus BLEU.

SENSITIVITY AND SPECIFICITY: Defect: a translation swaps a critical negation but retains many n-grams. Clean: correct paraphrastic translation with low lexical overlap. A human Reference Set should compare meaning and surface overlap independently, showing known disagreements. Verify tokenization, clipping and brevity penalty on hand-calculated examples.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze tokenization, reference count, case policy, smoothing, corpus vs sentence aggregation and n-gram orders.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Under explicitly declared unigram-only BLEU-1 with one reference, whitespace tokenization, no smoothing, and a corpus consisting of a single candidate, reference \[a,b,d\] and candidate \[a,b,c\] yield clipped unigram precision 2/3 and brevity penalty 1, so BLEU-1 = 2/3. Identical reference and candidate \[a,b,c\] give BLEU-1 = 1. This does not validate BLEU-4 or any smoothed sentence-BLEU implementation.

Missing evidence and eligibility. When the reference is absent, report NOT_ASSESSED; when provider output or tokenization evidence is unavailable, report UNAVAILABLE. Empty candidates or references and n-gram orders longer than available text require a frozen zero/undefined/smoothing convention. Never silently substitute BLEU-1 for BLEU-4, nor mix sentence and corpus BLEU.

8\. Traps of the metric itself

Long generic output can overlap; one-word meaning reversal; language-specific tokenization and corpus size change scores.

9\. Not suitable for

Open-ended RAG accuracy decisions or customer policy correctness as a sole Gate.

10\. See also

M-28 ROUGE; M-29 Embedding Similarity; R-02.

## M-28 · ROUGE

1\. Name and common aliases

ROUGE — ROUGE-N; ROUGE-L; recall-oriented overlap

2\. What it measures

How much reference summary content is lexically recovered by a candidate summary, under a selected ROUGE variant.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-02 (diagnostic). Use only when the observable matches the risk property.

4\. What it does not tell you

It cannot establish that every included claim is true, that critical amounts are right, or that brevity is appropriate.

5\. How it is usually computed

Choose ROUGE-N or ROUGE-L explicitly; pin tokenization, case, stemming, stopword treatment and multiple-reference aggregation. For ROUGE-1, count overlapping unigrams using clipped reference/candidate counts and divide by reference unigram count to obtain recall; for precision or F1, report them separately. For ROUGE-L, calculate longest common subsequence per stated implementation policy and disclose whether sentence/summary level used. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: ROUGE includes different variants such as ROUGE-N and ROUGE-L; do not label one unspecified score ROUGE. Publish reference set, normalization and chosen variant.

6\. Oracle type and AQEF dimension

Deterministic overlap Validator; Semantic diagnostic only. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: One candidate/reference pair and an explicitly reported set aggregate. No reference summary means not assessed. Report each measure (recall, precision, F1) with number of assessed pairs, exclusions and reference construction method.

SENSITIVITY AND SPECIFICITY: Defect: summary includes all boilerplate terms but inverts the key deadline; clean: valid short paraphrase without exact words. Reference Set includes omission, hallucination, correct paraphrase and boilerplate; independent human labels test correlation with actual summary completeness.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze ROUGE variant (e.g. ROUGE-1 F1 or ROUGE-L recall), tokenizer, stemmer and multi-reference handling.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Under ROUGE-1 with unigram multiset overlap, reference tokens \[a,a,b\] and candidate \[a,b,b\] share min-count overlap 1(a)+1(b)=2 tokens; precision = 2/3, recall = 2/3 and F1 = 2/3. Repeated tokens must be counted by minimum frequency, not by unique-token set intersection.

Missing evidence and eligibility. No valid reference → NOT_ASSESSED; missing candidate capture → UNAVAILABLE. A zero-token reference or candidate follows a predeclared convention (N/A, zero, or another explicitly selected library behavior); do not allow the scoring library default to silently decide the denominator. ROUGE-1 and ROUGE-L, and precision, recall, and F1, are separate reported variants.

8\. Traps of the metric itself

Recall rewards long answers; n-grams miss synonyms; ROUGE-L can reward sequence retention despite wrong polarity.

9\. Not suitable for

Fact-checking, citation support, nuanced policy correctness as sole evidence.

10\. See also

M-27 BLEU; M-29 Embedding Similarity; R-02.

## M-29 · Embedding Similarity

1\. Name and common aliases

Embedding Similarity — Semantic textual similarity; cosine similarity of sentence embeddings

2\. What it measures

Geometric similarity between vector representations of candidate and reference text in a specified embedding space.

3\. Why it is used

For Aster Support AI, diagnostic evidence for R-02, R-08 (diagnostic only). Use only when the observable matches the risk property.

4\. What it does not tell you

It does not entail truth, equivalence of numbers, preservation of negation, authorization, or source support.

5\. How it is usually computed

Pin embedding model and revision, preprocessing and segmentation. Encode candidate and approved reference using the same model. Calculate cosine similarity = dot(a,b)/(\|a\|·\|b\|), with an explicit policy for zero vectors and missing text. For multiple reference statements use predefined matching or aggregation; never select the most favorable option after observing scores. The defined procedure is this Guide’s reproducible choice; alternate variants change the interpretation.   
  
Method interpretation and limits: Cosine similarity depends on the embedding model version and preprocessing. High similarity can coexist with negation or numerically wrong claims.  


6\. Oracle type and AQEF dimension

Deterministic vector comparison after potentially model-dependent embeddings; semantic proxy, not an admitted AQEF Judge merely because a model generated vectors. Evaluation uses only evidence from the same captured Execution or a frozen approved reference. Choose Gate placement and dimensional binding explicitly.

7\. Can the result be trusted?

VALIDITY: One text-pair score, optionally aggregated across fixed pairs. Report raw cosine scores and distribution, number of pairs, omissions and model revision. Any conversion to pass/fail requires an independently validated Project threshold and a separate reference calibration exercise.

SENSITIVITY AND SPECIFICITY: Defect: “refund in 30 days” replaced by “refund in 300 days”; clean: “may ask for a refund within a month” under a policy explicitly using calendar-month equivalence. Reference Set contains paraphrases, negation, numeric mutations and topical distractors; compare similarity against independent human equivalence labels.

AGREEMENT: compare to independently labeled correctness cases; overlap with a reference is not human agreement. For a genuine Judge, follow AQEF Admission and chance-corrected agreement rules.

STABILITY AND DEPENDENCE: pin algorithms, parameters, references and revisions; rerun controlled fixtures after changes.

BASIS AND AVAILABILITY: report assessed units, non-assessed units, distinct Scenarios and Executions; a broken scoring instrument is not an SUT failure. Include defect and clean controls in each run where specified, and exclude their results from quality aggregation.

Reproducibility lock — measurement unit and frozen inputs. Freeze embedding model version, pooling, normalization and cosine-similarity convention; compare only embeddings from the same model space.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Identical nonzero vectors (1,0) and (1,0) → cosine 1; orthogonal (1,0) and (0,1) → cosine 0. Antiparallel nonzero vectors (1,0) and (-1,0) yield cosine -1, so raw cosine is on \[-1,1\]; mapping to \[0,1\] is a separately named transformation. Zero vectors remain undefined, not zero similarity.

Missing evidence and eligibility. Missing embeddings or zero-norm vector → UNAVAILABLE/UNDEFINED, not zero similarity.

8\. Traps of the metric itself

Topical but false answers score high; embedding revisions change score scale; favorable reference choice inflates result.

9\. Not suitable for

High-stakes factual verification, unauthorized-action detection, or faithful citation checking as sole measurement.

10\. See also

M-27 BLEU; M-28 ROUGE; Faithfulness; R-02/R-08.

## General Judge methods

## M-30 · Rubric Scoring 

1\. Name and common aliases

Rubric scoring and criterion-based judging.

2\. What it measures

The degree to which one response satisfies explicitly stated evaluation criteria. The underlying property depends on the rubric: e.g., factual correctness, completeness, or clarity. A numeric score without a named criterion has no interpretable meaning.

3\. Why it is used

Useful where a deterministic predicate cannot capture the relevant semantic property. Aster examples: correct explanation of conditional eligibility (R-02), appropriate refusal (R-04), and dialogue consistency (R-08). The rubric must map to a specific property and defect class; one combined “overall quality” score is not a substitute for separate critical safety or correctness constraints.

4\. What it does not tell you

A high score alone does not prove factual correctness against uncaptured policy, task completion, tool side effects, retrieval coverage, or Oracle accuracy. It does not establish that a Gate can pass when critical constraints or trust requirements are unmet.

5\. How it is usually computed; Guide procedure



Guide procedure (one semantic property per scoring configuration): (1) Freeze the property, captured input/context, rubric version, judge configuration, and allowed evidence. (2) Define ordinal anchors 1–5: 1 = demonstrably violates a critical requirement; 2 = substantially wrong; 3 = mixed or important omission; 4 = meets material requirements with minor deficiency; 5 = fully satisfies. (3) Evaluate one response against the authoritative captured context, cite the evidence span and record one integer anchor; when evidence is missing, mark not assessed rather than fabricate a rating. (4) Resolve to an Execution-level PASS only if the applicable Project-defined decision rule is met; preserve the raw rubric score and individual defect flags separately. (5) Aggregate score distributions and the count of assessed, non-actionable, unassessed, and distinct Scenarios; do not silently average in absent scores.

This illustrative procedure uses a fixed 1–5 scale with an anchor for each score. If probability weighting is implemented, specify scores s and normalized probabilities p(s), then calculate Σ p(s)·s and disclose how probabilities were obtained. Record whether score-token log probabilities were available. Use the anchored rubric score when the probabilities needed for weighting are unavailable.  
  
Method interpretation and limits:  Independently validate each criterion and score band.  
  

6\. Oracle type and AQEF dimension · Prompt examples: §7.22

Judge for semantic criteria; Quality Dimension follows criterion (typically Semantic or Business, and contextual Safety only when explicitly appropriate). Unit: one response or one separable claim, declared in advance. A multi-criterion rubric needs a verdict per separable property rather than an unexplained average.

7\. Can the result be trusted? — checklist applied

Validity — on a blinded human-labelled sample, test whether the score reflects the stated property rather than fluent writing. Human labels include each anchor and the evidence backing it.

Sensitivity — defect Seeded Control “illustrative: the governing refund window is 30 days, but the answer confidently says 45 days”; the rubric must catch the changed deadline despite polished prose.

Specificity — clean Seeded Control “illustrative: the response says ‘within thirty days’ rather than ‘within 30 days,’ with the same valid condition”; it must not be penalized for wording.

Agreement and Admission — build a versioned Reference Set with examples from several sources, coverage across all anchors, and difficult 2/3 and 3/4 boundaries; blind independent human labelling, adjudicate disagreements, record raw and named chance-corrected agreement for the exact Judge configuration. Note AQEF Gate option require_admitted_judges; do not describe this option as universally enabled.

Stability and dependence — repeat fixed inputs; inspect score drift and change in adjudicated defect decisions. Changing judge model, prompt, rubric, scoring method or context policy creates a configuration that requires new Admission. Verify response segmentation separately from grading.

Basis and availability — show assessed Executions and Scenarios, anchor distribution, non-actionable Results, no-claim cases, and which rubric/version produced them. A Judge timeout is oracle_unavailable, not a subject failure. Missed defect or clean Seeded Controls invalidate matching Results under AQEF rules.

Reproducibility lock — measurement unit and frozen inputs. Freeze rubric criteria and anchors, Judge model/prompt/version, score range, aggregation and calibration examples. 

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three accepted raw rubric grades \[4,3,5\] on a 1–5 scale → mean raw grade (4+3+5)/3 = 4.0 points (out of 5). If explicitly reporting a normalized maximum-scale fraction, 4.0/5 = 0.80; do not confuse the raw mean with its normalized representation. Retain all item grades, denominators, and Judge configuration.

Missing evidence and eligibility. Missing or inadmissible Judge response → UNAVAILABLE; no criteria → NOT_ASSESSED.

8\. Traps of the metric itself

Rubric score becomes a proxy for length or confidence; anchors combine unrelated dimensions; one critical error is averaged away; judging references live knowledge instead of captured Evidence; score extraction silently treats malformed judge responses as zero.

9\. Not suitable for

As a substitute for exact schema validation, tool argument checks, hard Safety constraints, or verifying side effects that are decidable directly from trace Evidence. Avoid a single unconstrained score as a release veto for distinct properties.

10\. See also

R-02, R-04, R-08; M-07 Answer Relevance, M-08 Answer Correctness, M-31 Pairwise Preference. 

## M-31 · Pairwise Preference

1\. Name and common aliases

Pairwise comparison; side-by-side preference judgement; A/B judging; head-to-head response comparison.

2\. What it measures

Which of two outputs is preferred for a specified criterion under comparable circumstances. Preference is relative; it is not an absolute correctness or conformance score.

3\. Why it is used

Useful in differential checks across versions for Aster Support AI: clarity, helpfulness, and completeness where both candidates are otherwise eligible. It can supplement R-02 (answer quality), R-08 (multi-turn behavior) and R-12 (regression), but does not replace independent critical checks.

4\. What it does not tell you

A winner may still be wrong, unsafe, stale, or incomplete; both candidates can fail. A preference rate does not establish absolute compliance or which underlying cause changed.

5\. How it is usually computed; Guide procedure



Guide procedure: (1) Fix the same scenario, relevant context and comparison criterion for response A and response B. (2) Independently check non-negotiable factual/structural/safety properties first. If both candidates are ineligible, label BOTH_UNACCEPTABLE; if one violates a hard criterion, record that failure outside preference. (3) Present eligible responses without system/version identity; have a Judge with documented calibration and admission status choose A, B or TIE under published criterion-specific instructions, quoting concrete distinctions. (4) Swap the order and re-evaluate; record a position-sensitive disagreement rather than choosing whichever outcome is convenient. (5) If order-stable, return the preference; if inconsistent or unsupported, flag INCONCLUSIVE for Human Review. (6) On a set, report A wins, B wins, ties, inconsistent comparisons, both-unacceptable pairs, assessed Scenarios and exclusions; a weighted win fraction may be reported only with declared treatment of ties.

Illustrative aggregation: A win fraction = (A wins + 0.5 × ties) / (A wins + B wins + ties), excluding inconclusive and both-unacceptable pairs but explicitly reporting their counts. This is the Guide’s reporting convention, not a required AQEF or universal formula.  
  
Method interpretation and limits: MT-Bench/Chatbot Arena documents pairwise judge phenomena; the Guide's tie and both-unacceptable outcomes and order-swapping protocol are locally specified. Record candidate order for each trial.

6\. Oracle type and AQEF dimension · Prompt examples: §7.23

Judge, with Human Review for disputes; Semantic or Business according to comparison criterion. Unit: a matched pair of outputs for one scenario; per-set aggregation over pairs. A separate Validator decides any deterministically checkable prerequisites.

7\. Can the result be trusted? — checklist applied

Validity — the Reference Set consists of human-preferred A/B pairs, ties, and both-unacceptable pairs, all tied to the same explicit comparison criterion; include cases where pleasant prose conceals a policy error.

Sensitivity — defect Seeded Control: illustrative candidate A says the refund is guaranteed despite conditional eligibility while B preserves the condition; the qualified Oracle must not prefer A merely because it is confident or concise.

Specificity — clean Seeded Control: A and B have substantively equivalent correct answers with differences in harmless formatting or length; an applicable tie label must remain available.

Agreement and Admission — compare blinded Judge A/B decisions with independently adjudicated human preferences, after ensuring human raters also receive the task criterion; record raw and chance-corrected agreement and label distribution for each Judge configuration. Multi Judge panels require member-level Admission as specified.

Stability and judge dependence — compare A-first and B-first outcomes and repeated presentations. Track flip rate and changes under length normalization or anonymization. Re-admit after Judge configuration changes.

Basis and availability — report number of pairs, distinct Scenarios, each verdict class and missing comparisons. Judge failures are not “ties.” Missed Seeded Controls invalidate the matching evidence; no artificially positive release result may be inferred from those pairs.

Reproducibility lock — measurement unit and frozen inputs. Freeze response pair, task context, Judge identity and randomized A/B order; explicitly allow ties and count order reversals.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Ten valid pairwise comparisons give A wins=6, B wins=3, ties=1, so tie-excluded A win rate=6/9 ≈ 0.6667 and tie-inclusive A win fraction=(6 + 0.5 × 1)/10 = 6.5/10 = 0.65. A separate position-bias control presents each identical pair in both A/B orders; a reversed verdict between orders is logged as an order-effect incident and must not be hidden in either win-rate denominator.

Missing evidence and eligibility. Missing/invalid pair → exclude with reason; no valid pairs → NOT_ASSESSED.

8\. Traps of the metric itself A preference verdict measures comparative preference. Verify factual correctness with an independent check.

Position bias; verbosity bias; model-family or self-enhancement bias; treating tie as failure; forcing a winner when both are bad; changing input or available evidence between candidate runs; multiple correlated pairs falsely inflate sample breadth.

9\. Not suitable for

Hard Safety veto decisions, precise numeric policy checks, exact tool outcomes or standalone claims of absolute correctness. Cannot compare two responses generated for materially different customer situations without explicit matching design.

10\. See also

M-30 Rubric Scoring; M-08 Answer Correctness; R-02, R-08, R-12. 

## Reliability and operations

## M-32 · Consistency Across Runs

1\. Name and common aliases

Consistency Across Runs; repeatability; semantic consistency.

2\. What it measures

The fraction of repetitions of a fixed Scenario whose outcomes are equivalent under a predeclared success and meaning criterion.

3\. Why it is used

Primary links: R-08, R-12. Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not establish that a consistently repeated answer is correct; it cannot establish distributional reliability outside the sampled conditions.

5\. How it is usually computed; this Guide's procedure

Methodological basis: AQEF 1.0-CR1.9, Volume VIII, Consistency Testing. No unique universal primary formula identified; the measure below is Guide-defined.

Guide procedure: Take N independently initiated Executions of the same Scenario, with a fixed subject configuration and a declared environment distribution. Store all final states, outputs and termination labels. For each run evaluate task correctness separately and compare its substantive answer or state with the reference response class. Predefine an equivalence predicate; for a chosen property record the proportion of runs matching the modal allowed outcome, and separately the proportion meeting the reference. A second diagnostic reports pairwise equivalence across all N(N−1)/2 pairs.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: specify semantic equivalence labels, fixed scenario grouping, number of repeats, and denominator. Source discussions of reliability do not establish this particular formula.

6\. Oracle type and AQEF dimension · Prompt examples: §7.24

Validator for exact states/identifiers; Judge with documented calibration and admission status for semantic equivalence. Reliability plus Semantic when substantive.

Unit / basis: One Scenario × repeated Execution group; report number of runs, distinct scenarios and run exclusions separately. No repeated group -\> NOT_ASSESSED. Do not pretend repeats are independent scenarios.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: one run cites a 30-day policy and another incorrectly switches to 45 days; clean: faithful paraphrases that preserve all eligibility conditions. Independently adjudicate equivalence labels and their borderline cases. Drift controls must distinguish changed subject configuration from stochastic output.

Human agreement: where semantic labels require a Judge, prepare an independently human-labelled, versioned Reference Set and record Admission for each judge configuration per AQEF Volume VI; a Project Gate may additionally require Judges with documented calibration and admission status. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze exact test input, system/Oracle versions, temperatures, seeds where supported and semantic equivalence rule; group repeats by case.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Of five repeated outputs, four satisfy the same prespecified binary outcome → modal-outcome consistency 4/5; do not conflate with correctness.

Missing evidence and eligibility. Single run → NOT_ASSESSED for across-run consistency; unknown settings prohibit comparability.

8\. Traps of the metric itself

Do not mix model variants in a group; majority can be consistently wrong; Judge variability can masquerade as system variability; do not delete failed attempts.

9\. Not suitable for

Single run, correctness without a reference, or unlabelled changing environment.

10\. See also

pass^k; Task Completion; R-08, R-12

## M-33 · pass@k

1\. Name and common aliases

pass@k; at-least-one success among k.

2\. What it measures

The probability that at least one of k sampled attempts satisfies a declared, independently assessed success condition.

3\. Why it is used

Primary links: R-12 (also R-06 / R-07). Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not establish repeatable correctness, that the system will select the successful candidate, or that retrying a failed production action is safe.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For every scenario generate n independently evaluated candidate Executions under a frozen sampling configuration and establish a binary ground-truth success verdict for each, yielding c successes. For 1≤k≤n estimate the probability that a uniformly sampled k-subset (without replacement) contains at least one successful candidate, pass@k with 1 − C(n−c,k)/C(n,k); implement the ratio as a product or integer combinatorics for numerical stability. A separate direct repeated-batch experiment can report proportion of k-attempt batches with ≥1 success. Keep the two estimators explicitly identified. When sample draws are not exchangeable or the selection process differs across k, do not present the estimator as unbiased for that process. Missing or harness-failed trials are neither successes nor valid zero-success trials; report exclusions and recollection policy.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: The pass@k estimator for n samples and c successes is 1 − C(n−c,k)/C(n,k). The combination formula selects subsets from an already sampled pool; it is not a production retry protocol. It is defined here for 1 ≤ k ≤ n when all n candidate outcomes are definitive. State sampling assumptions, independence limits and method of task aggregation.

6\. Oracle type and AQEF dimension · Prompt examples: §7.25

Validator for verifiable task state; Judge with documented calibration and admission status only when an objective verdict cannot be expressed; Reliability/Functional.

Unit / basis: Each Scenario is the aggregation unit. Report mean of scenario-level estimates, n, k, c and breadth. If n&lt;k or any success verdict is not actionable, mark the affected estimate insufficient/unassessed rather than treating uncertainty as failure.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: candidates that sound correct but never executed the refund are false successes. Clean: alternate valid execution reaches identical authorized end state. Reference Set must distinguish outcome from prose claim; controls exercise successful and unsuccessful terminal states.

Human agreement: where semantic labels require a Judge, prepare an independently human-labelled, versioned Reference Set and record Admission for each judge configuration per AQEF Volume VI; a Project Gate may additionally require Judges with documented calibration and admission status. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze n separately generated candidate samples per task, binary success labels, c successes, k≤n and task identities. The pass@k estimator counts hypothetical uniformly selected subsets of k without replacement from those n evaluated candidates: 1 − C(n−c,k)/C(n,k). Sampling without replacement describes the estimator over candidates, not a requirement to generate candidate outputs without replacement.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). n=5, c=2, k=2 → pass@2 = 1 - C(3,2)/C(5,2) = 0.7. Aggregate per-task estimates with declared task weighting. Edge checks: for k≤n, c=0 yields 0; c=n yields 1; k=1 gives c/n. If any candidate outcome is censored, the estimator for that task is NOT COMPUTABLE under the frozen complete-outcome policy, not a failure imputed to c.

Missing evidence and eligibility. n&lt;k or no definitive outcomes → NOT COMPUTABLE; censored runs are not automatically failures.

8\. Traps of the metric itself

Using 1−(1−mean(p))^k across heterogeneous tasks; conflating benchmark sampling with in-service retries; counting one lucky sample as reliability.

9\. Not suitable for

Unrecoverable actions or settings where multiple candidate attempts cannot be made safely.

10\. See also

pass^k, Consistency; R-07, R-12

## M-34 · pass^k

1\. Name and common aliases

pass^k; all-k success; repeated-trial reliability.

2\. What it measures

The chance that all k fresh attempts on the same task meet the declared success condition.

3\. Why it is used

Primary links: R-12 (also R-07). Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not measure diversity of tasks or prove production reliability when trial environments are unrepresentative.

5\. How it is usually computed; this Guide's procedure



Guide procedure: For each Scenario execute k fresh independent trials with declared reset state and identical task specifications. Independently verify each terminal state. The scenario batch passes only when every trial passes; otherwise it fails. Aggregate passing batches / assessed batches over a declared scenario set, or report per-task modelled p_i^k when repeat sampling supports that estimate; do not interchange empirical batches with modelled probability. IMPORTANT: p_i^k assumes identically distributed independent trial success conditional on the task and stable environment. Prefer observed all-k batch frequency when that assumption is unverified. With n\>=k exchangeable labelled samples and c successes, the combinatorial subset estimator C(c,k)/C(n,k) estimates all-k success under the declared sampling design; do not silently substitute (c/n)^k.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: The pass^k measure estimates repeated task reliability when all k trials pass. Observe successes per same-task group and aggregate across tasks; (global pass rate)^k assumes homogeneous independent trials and is not a substitute.

6\. Oracle type and AQEF dimension · Prompt examples: §7.26

Validator on annotated final state preferred; Judge with documented calibration and admission status for truly semantic outcomes; Reliability.

Unit / basis: One Scenario × k-trial batch; record k, number of assessed batches, eligible distinct Scenarios, individual attempt results, and missing/unavailable trial outcomes. Any unavailable trial -\> batch not assessed, not pass.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: the third of k trials omits a required approval step despite two successes; clean: k independently valid paths with harmless wording variations. Reference Set labels final states and any policy constraints across trials.

Human agreement: where semantic labels require a Judge, prepare an independently human-labelled, versioned Reference Set and record Admission for each judge configuration per AQEF Volume VI; a Project Gate may additionally require Judges with documented calibration and admission status. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze k repeated trials per task, identical success contract and task grouping; measure all-k success empirically (task groups with all k successes / eligible task groups).

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Four fully assessed task groups, each with k=3 trials, contain exactly one group passing all three → empirical pass^3 = 1/4 = 0.25. If a fifth task group has only two of its three trials observed, classify it NOT_ASSESSED and disclose one incomplete group; do not silently turn the statistic into 1/5 = 0.20 or score its absent trial as failure.

Missing evidence and eligibility. A group missing any of its k definitive outcomes is NOT_ASSESSED; show completed groups, incomplete groups, and their reasons as separate counts. The empirical pass^k denominator is fully assessed eligible groups only, under a frozen predeclared cohort policy; do not cherry-pick complete groups to improve a release decision. A zero completed-group denominator means NOT COMPUTABLE, never zero reliability.

8\. Traps of the metric itself

Estimating from pooled task success rates; treating k attempts as k Scenarios; masking an Oracle failure as subject failure; non-independent runs sharing residual state.

9\. Not suitable for

Tasks without controlled reset or where repeats produce irreversible external effects.

10\. See also

pass@k, Consistency, Task Completion; R-12

## M-35 · Latency

1\. Name and common aliases

Latency; duration, response time, time to first token.

2\. What it measures

Elapsed time between two explicitly declared instrumentation boundaries for a subject request, operation, or agent workflow.

3\. Why it is used

Primary links: R-12. Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not prove task success, low cost, or that the same segment of a workflow is being compared.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Choose start and end markers (e.g. request issued to final response received) and specify whether network transit, retries, tools, queueing and streaming are included. Capture monotonic timestamps and errors; duration seconds = end − start. Compare matched scenario/environment cohorts and record median, p95 and maximum with exact counts. Separately report time-to-first-response or time-to-first-token when instrumentation exists; never call that end-to-end latency.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: Inference duration is not necessarily end-to-end application latency including retrieval and tools. State start/stop event, clock, queue/network inclusion, distribution and missing spans.  
  

6\. Oracle type and AQEF dimension

Deterministic instrumentation validator; Operational.

Unit / basis: One Execution or clearly bounded model/tool operation; for set metrics report distribution with n, matched baseline cohort, exclusions and observed errors. Missing end timestamp is not zero latency.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: injected artificial delay on tool result increases measured elapsed wall time; clean: same task length with natural timing variance remains within specified comparator bands. Verify clock integrity and tracer placement against an independent known-duration test.

Oracle qualification: latency arithmetic uses instrumented timestamps and a validated clock; Human/Judge Admission applies only if a separate semantic labeling step determines scenario eligibility or correctness. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze timing start/end boundaries (request submitted, first token, final response/tool completion), clock source and cold/warm classification. Publish TTFT separately from full latency.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Five full-response latencies in ms \[100,120,140,160,180\] → median 140 ms; using the nearest-rank convention, p95 = sorted observation at rank ceil(0.95 × 5) = 180 ms; other quantile conventions must be declared and cannot be pooled.

Missing evidence and eligibility. Missing timestamps or incomparable boundaries → UNAVAILABLE; timeout/cancelled are reported separately, not silently dropped.

8\. Traps of the metric itself

Mean hides tail; unpaired payload sizes; excluding timeouts; instrumenting only model inference while calling number workflow latency.

9\. Not suitable for

Comparisons across differing duration boundaries, models, loads or environments without stratification.

10\. See also

Cost, Token Usage, Step Efficiency; R-12

## M-36 · Cost

1\. Name and common aliases

Cost; cost per execution; task cost; billable resource cost.

2\. What it measures

Total declared billable and/or internally allocated resource cost attributable to one assessed Execution.

3\. Why it is used

Primary links: R-12. Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not establish customer value, task success, or latency; token count is only one possible cost driver.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Freeze a versioned tariff and accounting scope before test. For every Execution enumerate billable model operations by token modality/category, paid tool invocations, infrastructure allocations and any billed retry. Multiply each billable quantity by its versioned unit price, then add separately declared charges. Use one currency and price period. Version the billing evidence used to reconcile the estimate. Compare cost distributions on matched workloads. Keep billing-record reconciliation and any unpriced components visible; a partially priced run is not an exact cost.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: Guide-defined cost model: cost per Execution is the sum of metered billable units multiplied by an explicitly versioned price schedule, including stated exclusions. Token counters alone do not define monetary cost.  
  

6\. Oracle type and AQEF dimension

Deterministic billing reconciliation Validator; Operational and Business when applicable.

Unit / basis: One Execution; aggregate mean, median, p95, total cost and cost per successful task, with number of complete, partial and unpriced runs. Failed but billable executions remain in costs.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: cost ledger silently ignores the second inference after a tool retry; clean: cached tokens recorded in correct cheaper billing category. Controls use precomputed invoices and usage fixtures; reconcile with independent reference values.

Human agreement: where semantic labels require a Judge, prepare an independently human-labelled, versioned Reference Set and record Admission for each judge configuration per AQEF Volume VI; a Project Gate may additionally require Judges with documented calibration and admission status. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze model/region/provider tariff version, billable token/tool units, currency, date, cache and retries; keep estimate distinct from invoice-reconciled cost.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three billable executions costing 0.01, 0.02, 0.03 currency units → mean per billable execution 0.02; separately report total 0.06.

Invoice-coverage counter-control. Two completed billable Executions cost 0.02 and 0.04 units; a third has known usage but no applicable tariff. Total confirmed cost is 0.06 across two priced Executions, with one UNPRICED Execution; 0.03 is the mean over priced Executions only. Do not report 0.06/3 = 0.02 as cost per fully assessed Execution or treat missing prices as zero. Record paid retries according to the frozen tariff boundary.

Missing evidence and eligibility. No pricing or usage detail → ESTIMATE UNAVAILABLE; do not report zero.

8\. Traps of the metric itself

Mixing currencies; stale tariffs; counting cached tokens twice; optimizing average cost while failed runs become expensive.

9\. Not suitable for

Monetary comparison without an agreed accounting boundary or price period.

10\. See also

Token Usage, Latency; R-12

## M-37 · Token Usage

1\. Name and common aliases

Token Usage; input tokens; output tokens; cached and reasoning subsets.

2\. What it measures

Count of tokens consumed by model operations under a declared counting and accounting convention.

3\. Why it is used

Primary links: R-12. Quantifies an observable condition relevant to release risk but cannot by itself determine any Gate.

4\. What it does not tell you

It does not directly equal monetary cost, semantic quality, response length, or total resource consumption.

5\. How it is usually computed; this Guide's procedure



Guide procedure: Capture per-inference input and output counters from authoritative billing/provider response where available. Record cache-read/write and reasoning tokens as explicitly identified subsets, not additive to their parent totals. Sum input and output totals across actual inference operations within an Execution, including billable failures when counts exist. Record modality, model/tokenizer configuration and missing usage separately. Distinguish sampled operation histograms, cumulative counters and provider-call-level usage before aggregation. Compare like-for-like task cohorts; do not equate token counts from different model-specific tokenizers.

Variants: report the chosen estimator, matching policy, time boundary or accounting scope explicitly. Distinct definitions under one name are not pooled.  
  
Method interpretation and limits: Monotonic token counters and per-operation token distributions are different signals; declare aggregation unit, input/output split, metadata and zero vs missing observation explicitly.  
  

6\. Oracle type and AQEF dimension

Validator/counter reconciliation; Operational.

Unit / basis: One model operation and its parent Execution; report per-operation and per-Execution distributions, token strata and coverage. No returned usage -\> unavailable, not zero unless trustworthy evidence states zero.

7\. Can the result be trusted? Trust checklist applied

Validity: verify boundaries, units and task-specific success labels using independently established reference evidence. Sensitivity/specificity: Defect: cache-read subset added again to total input; clean: a different but equivalent tokenizer segmentation documented for a different model and never directly compared. Reference fixtures include provider counters, streamed outputs and absent-usage cases.

Human agreement: where semantic labels require a Judge, prepare an independently human-labelled, versioned Reference Set and record Admission for each judge configuration per AQEF Volume VI; a Project Gate may additionally require Judges with documented calibration and admission status. Stability: repeat fixed-input tests, including a negative and a clean control. Basis: report assessed and non-actionable Results, distinct Executions and distinct Scenarios. Availability: report missing telemetry and Oracle failure without turning either into subject failure.

Reproducibility lock — measurement unit and frozen inputs. Freeze provider counting conventions and separate input, output, cached and reasoning-token fields where observable; do not sum overlapping subtotals twice.

Worked arithmetic/control fixture (illustrative; not a claim of observed Judge performance). Three calls with non-overlapping total usage \[100,150,50\] → aggregate 300 tokens and mean 100 tokens/call. Counter-control: if one provider call reports input_total=100 with cached_input=30 included in that total and output_total=20, its combined usage is 120, not 150. Cached tokens must not be added again merely because separately reported.

Missing evidence and eligibility. Missing provider usage → UNAVAILABLE; observed zero tokens is valid only with an explicit provider value.

8\. Traps of the metric itself

Subsets double counted; output tokens mistaken for billed tokens; missing usage treated as zero; invisible agent loops left outside scope.

9\. Not suitable for

Cross-model numerical comparisons without declared tokenizer and category semantics.

10\. See also

Cost, Latency; R-12
