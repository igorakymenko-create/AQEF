# PART 6 · CHOOSING AND ADMITTING A JUDGE

“May this model act as our Judge?” has no general answer. The question the Project can answer is: “Is this frozen configuration admitted for this property, this Evidence and this decision context?” Choosing a promising candidate, admitting it independently, and confirming that it remains qualified in each run are distinct undertakings. This Part is a Guide explanation of how to carry them out without inventing AQEF requirements.

## 6.1 Three stages: selection, admission, controls

| Stage            | Question                                                        | Evidence                                                            | Normative status                           |
|------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|--------------------------------------------|
| Selection        | Which configuration deserves a proper assessment?               | Candidate comparison on working/development items                   | Guide practice (§6, Scope) |
| Admission        | Is the frozen configuration fit for the property?               | Independent, versioned Reference Set and chance-corrected agreement | AQEF Volume VI — Admission                 |
| Per-run controls | Did it detect a known defect without inventing one in this run? | Defect and clean Seeded Controls in the relevant classes            | AQEF Volume VIII — Seeded Controls         |

Selection includes the tuning described in §2.5. A candidate can be improved using working items and several prompts. For Admission, use a  Reference Set held out from candidate and rubric selection. Reusing the working set measures  fit  to the material used for selection.

The unit of trust is the Judge configuration: model version, prompt or rubric, criteria, generation parameters, evidence access and any agent tooling. Pin model versions rather than floating aliases where possible. A provider may change the implementation behind an unchanged alias, making a previously measured Judge different in operation even if the visible name remains stable.  Volume X, “Model Drift,” states that a Regression Suite “MUST be able to surface Model Drift even when nothing AQEF-visible changed.”  See §2.5 for the fields in the Admission record and how to interpret its agreement measures. Volume VI, Admission, states that “Raw agreement alone misleads”. Which measure and threshold suffice are Project decisions; this Guide does not turn example values into obligations.

## 6.2 Default diligence: what the Judge checks without prompting

Default diligence is a descriptive Guide term, not an AQEF field or formal construct. It is the extent of checking a Judge or evaluator-agent undertakes without being told how deeply to investigate. It matters especially when an agent gathers its own Evidence by navigating an application; it is less meaningful for an AQEF Judge given a fixed Evidence bundle.

Observe the instrumentation rather than trusting a self-report. For an interactive application, compare the proportion of pages, endpoints or workflow stages actually touched; whether the agent tried boundary and malformed inputs, an independent arithmetic recomputation, or a narrow layout; and whether it issued an approval while explicitly stating that a consequential area had not been checked.

This is a screening signal, not a measure of defect detection. An agent can make many irrelevant calls while overlooking a basic omission, or generate false positives after extensive exploration. The relevant outcome remains actual confirmed defects found and clean cases passed. Default diligence changes with the model, prompt, application and tool permissions; record it per configuration and retest after change.

Scope boundary. An agent that decides what to inspect is doing exploratory testing. AQEF 1.0 Scenarios determine what is checked and AQEF Judges assess supplied Evidence. Findings made by an exploratory agent can be converted to Scenarios, reference Evidence and Contracts. Acceptance still rests on the Contract, evidence qualification and Quality Gate, not on the exploratory agent’s unverified approval.

## 6.3 Prompt levels and sensitivity

| Level                           | What is supplied                                                      | What it reveals                                   |
|---------------------------------|-----------------------------------------------------------------------|---------------------------------------------------|
| L0 — role only                  | The role and task, without an explicit standard                       | Unprompted diligence and default leniency         |
| L1 — role and standard          | A defect criterion, product/user need and allowed approval conditions | Ability to apply a known standard without methods |
| L2 — role, standard and methods | L1 plus explicit checks and procedures                                | Performance with extensive process support        |

These levels are experimental conditions, not official AQEF prompt types. A role-only prompt can reveal default behavior. The L0-to-L1 difference shows how much specifying an acceptance standard changes decisions. L2 approximates an instructed operating condition, not a universal upper bound: good models may still miss a defect and explicit methods can sometimes distract.

No prompt is neutral. “It is entirely your call” grants discretion and can encourage leniency; “assume a problem exists” may inflate false alarms. Compare detected defects, misses and false alarms against independent reference labels, not obedience to a prescribed checklist. Include seeds both inside and outside the prompted checks to observe initiative.

A claim about a model rather than a single configuration requires treating prompting as an experimental factor: change framing, verdict shape, evidence visibility and ordering of explanation and judgement. Compare a common prompt with prompts tuned separately under equal effort. A small number of distinct paraphrases per cell can separate fragile wording from the substantive effect. Do not claim robustness if all experiments share one phrasing.

No finite prompt set proves prompt-independence. Three useful stopping checks are: an independent new prompt family no longer changes the estimate or candidate order beyond a predeclared margin; prompt-to-prompt spread is small compared with differences between candidates; and a prompt authored independently after conclusions were fixed does not reverse the result. If the result changes materially with the prompt, the honest result is “depends on the prompt”. Prompt sensitivity is itself a property of the instrument.

Choosing among prompts belongs to Selection (§2.5). Freeze the selected version before Admission; a later changed prompt creates a different Judge configuration and needs renewed Admission (AQEF Volume VI). Part 7’s base prompts are L1 examples in this sense; variants marked L2 add explicit checks.

## 6.4 Constructing a credible fixture

A fixture is the subject material and its reference defects. For a Judge assessing fixed Evidence, use a versioned Reference Set under Volume VI. For an exploratory evaluator-agent, use an application held in a known state and accompanied by reproduced reference findings. Keep the two regimes distinct: independent Admission of an Evidence-bound Judge is not conferred by an exploratory testing demonstration.

For each illustrative application prepare three variants: (1) as built, containing natural defects that a reviewer reproduced; (2) seeded, adding known defects with documented manifestations; and (3) clean, with every known defect corrected and the correction checked. Only the clean variant can establish that an evaluator does not simply report defects in every case. For AQEF Seeded Controls use `kind: defect` and `kind: clean` as specified in Volume VIII, with evidence confirmation through `validator`, `human_reviewer` or `construction` as applicable.

Describe defect difficulty by the observed performance of independent reference examiners, not by author intuition. Volume VIII’s difficulty prior concerns how reliably independent reference Oracles detect a defect class. Volume VIII, Seeded Controls, says that reviewers “SHOULD NOT know which items are controls, or of which kind, where this can be arranged”. See Appendix A §A.1 for `difficulty_prior` , `prior_basis` , and `prior_source` . Report the reference miss share as the complement of the observed catch share.

An illustrative difficulty ladder has six conditions: a crash on malformed input; a boundary value; a stateful sequence; a plausible wrong calculation requiring independent recomputation; an inconsistency between two views; and an omitted capability against a user need. It is not a standard scale. The easiest category is only a screen: detecting an obvious problem proves little, while missing it raises concern. Difficult categories carry more diagnostic value.

Give surface quality a stratum of its own. A Judge may favour a response that is longer, more confident or better formatted, whatever its correctness; treat this as a risk to test, not an assumed rate. Build items in which the two pull apart: a fluent, well-structured answer with one material error beside a short, plain answer that is correct, and an answer that looks thorough but does not do what the clause asks. Count misses and false alarms in this stratum separately (§6.6). A Judge that passes the polished wrong answer and fails the plain correct one shows the bias, not the property.

Keep seeding separate from the evaluated Judge: use a human or an independent construction process. Start with at least three fresh sessions  per configuration and variant as a Guide example. Use a larger independent sample when the decision calls for  a tighter uncertainty bound. Choose applications that exercise different tasks and evidence sources. Three to five distinct fixtures is an illustrative starting range.

Illustrative sampling calculation: with zero misses among n independent failing items, the approximate one-sided 95% upper bound on miss probability is 3/n (“rule of three”). For n = 20, 3/20 = 0.15 or 15%. For n = 30, 3/30 = 0.10 or 10%. The exact binomial upper bound is 1 − 0.05^(1/n): for n = 20 it is about 13.9%; for n = 30 about 9.5%. These depend on independence and the assumed sampling model. Zero misses in a small sample is not proof of near-perfect sensitivity; stratify counts by defect difficulty.

## 6.5 Are seeded defects representative of real defects?

Detecting everything planted is not the same as detecting unknown natural defects. The gap can be explored but never removed by a finite collection of controls. Prefer seeding previously discovered and repaired defects from the Project’s own history; restore them deliberately in a controlled fixture so the reference is concrete.

On a subset of applications, conduct an independent human audit to document natural defects and compare each candidate Judge’s detection of natural versus seeded defects. A positive relationship across configurations supports the utility of the seeds for that context; it does not prove that all unseen defects are represented. If seeded and natural findings diverge, revise defect classes, difficulty priors and selection criteria.

A rough two-examiner estimate illustrates how much a reference list may miss: suppose reviewer A finds 12 distinct defects, reviewer B finds 10, and four overlap. The simple capture–recapture estimate is (12 × 10) / 4 = 30 total defects. The observed union is 12 + 10 − 4 = 18; the estimate suggests 30 − 18 = 12 potentially unseen. This is illustrative and unreliable when overlap is tiny, finding probabilities differ greatly, or the examiners’ misses are dependent. Do not treat 30 as an established ground truth.

Every escaped defect that can be reproduced should become a new regression Scenario and, where valid, a fresh seeded fixture. Report Admission only within the domain and classes actually represented by the Reference Set. Controls remain useful in individual runs because previous admission cannot guarantee that the instrument still detects those classes today.

## 6.6 Predeclared admission decision rule

The Project writes the decision rule before viewing Admission results and keeps it with the frozen Judge configuration. A Guide example combines these checks: no miss in the easiest defect category; a detection floor in each significant harder category; a false-alarm ceiling on passing items in each category; no approval accompanied by an admission that a material area was unexamined; and a separately declared repeated-verdict stability requirement.

Guide starting points for this illustrative rule: 1.00 detection for the easiest category; 0.80 detection for each higher-risk harder category; and at most 0.10 false alarms among clean passing items in each category. These are not reference values and carry no claim of being enough. Replace them with thresholds justified by domain consequences, the costs of missed defects and false alarms, and the amount of independent evidence in each category (§6.4).

Floors must be paired with ceilings. A Judge that fails every item appears to detect 100% of defects yet has a 100% false-alarm rate. Neither high detection alone nor high raw agreement alone establishes an acceptable instrument.

AQEF 1.0 Admission records contain aggregate required fields; they do not have separate per-stratum floors, ceilings or count fields. Guide practice is to retain a supplementary worksheet with each stratum’s caught and missed failing items, and correct and incorrectly failed passing items. This worksheet is not a new AQEF field or a newly mandatory Admission artifact.

Volume VI, Admission, states that “a changed model, prompt, or criteria is a different Judge and needs its own admission.” In Guide practice, an agent or generation-parameter change also creates a new configuration to admit. Repeat current controls after change, and use §5.6 to decide what measurements need renewal.

AQEF 1.0-CR1.6 added two practices to Appendix I §I.2 that bear on this Part. Where a Multi Judge panel looks for defects, `threshold: unanimous` prevents two Judges that missed a defect from outvoting the one that found it; `on_disagreement` then decides, with `fail` or with Human Review (Volume VI, Voting; Appendix A §A.7). Because a changed model is a different Judge, prepare for the change before it comes: name a dated model version, keep Reference Set items and Seeded Controls in reserve, admit a successor while the current version is still in use, and count the configurations tried against one Reference Set version, since among many attempts one may reach the threshold by chance.

## 6.7 Worked example — Aster faithfulness Judge (illustrative)

Two configurations, A and B, are frozen after Selection. The independent Admission Reference Set contains 120 items: 40 easy, 40 medium and 40 hard. Each stratum has 20 failing and 20 passing items. Easy failures change a source amount substantially; medium failures invent a source condition; hard failures hide a small rounding difference or omit a material exception.

| Stratum | A: failing caught | A: passing failed | B: failing caught | B: passing failed |
|---------|-------------------|-------------------|-------------------|-------------------|
| Easy    | 20 / 20           | 0 / 20            | 20 / 20           | 3 / 20            |
| Medium  | 17 / 20           | 1 / 20            | 18 / 20           | 3 / 20            |
| Hard    | 9 / 20            | 2 / 20            | 17 / 20           | 4 / 20            |

Candidate A: true failure detections = 20 + 17 + 9 = 46; missed failing items = 60 − 46 = 14; incorrectly failed passing items = 0 + 1 + 2 = 3; correctly passed items = 60 − 3 = 57. Raw agreement = (46 + 57)/120 = 103/120 = 0.8583 (85.83%). Candidate B: detected failures = 20 + 18 + 17 = 55; missed failures = 60 − 55 = 5; incorrect failures on passing items = 3 + 3 + 4 = 10; correct passes = 60 − 10 = 50. Raw agreement = (55 + 50)/120 = 105/120 = 0.8750 (87.50%).

For both candidates, the reference has 60 failing and 60 passing items. A predicts 46 + 3 = 49 failures and 120 − 49 = 71 passes. B predicts 55 + 10 = 65 failures and 120 − 65 = 55 passes. Chance agreement is (60 × 49 + 60 × 71)/120² = 0.50 for A and (60 × 65 + 60 × 55)/120² = 0.50 for B. κ = (observed agreement − 0.5)/(1 − 0.5). Thus κ_A = (103/120 − 0.5)/0.5 = 0.7167 (about 0.72); κ_B = (105/120 − 0.5)/0.5 = 0.7500 (0.75). Both would pass the illustrative κ ≥ 0.70 rule from §2.5 if it were used alone.

Per-stratum detection shares: A easy 20/20 = 1.00, medium 17/20 = 0.85, hard 9/20 = 0.45. B easy 20/20 = 1.00, medium 18/20 = 0.90, hard 17/20 = 0.85. False-alarm shares: A easy 0/20 = 0, medium 1/20 = 0.05, hard 2/20 = 0.10. B easy 3/20 = 0.15, medium 3/20 = 0.15, hard 4/20 = 0.20.

Against §6.6’s illustrative floors and ceilings, A is not admitted: hard detection 0.45 falls below 0.80. B is not admitted: false alarms of 0.15, 0.15 and 0.20 exceed 0.10. Aggregate agreement masks opposite failure profiles: A overlooks difficult defects; B over-calls on clean items. Neither candidate is acceptable under this predeclared illustrative rule.

Uncertainty matters. With only 20 failing examples per stratum, even 20/20 detection leaves an approximate upper miss bound 3/20 = 15% (exact about 13.9%); these floors are coarse, not universal quality standards. A real Admission decision needs a reference size, uncertainty method and risk rationale that match its consequences. These numbers, candidates and verdicts are wholly illustrative.
