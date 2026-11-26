# 6. Scope

## In Scope

Everything specified across this document's five Parts and eleven Appendices: the Domain
Model and Fundamental Principles (Part I); how a Scenario becomes a Result (Part II);
what gets tested, how, and against what history (Part III); how AQEF is operated,
reported on, and governed (Part IV); how it extends and how it gets built (Part V); and
the concrete artifacts — schemas, API surface, diagrams, examples — the Appendices
generate from that content rather than author independently.

All of it applies specifically to testing the behavior of a Probabilistic Subject
(Volume I, Chapter 3) — an AI system whose output legitimately varies for the same
input. AQEF does not replace classical software testing for a product's deterministic
components; it governs the parts of a system where that assumption no longer holds.

## Applicability

AQEF rests on five assumptions. Where all five hold, it applies as specified. Where one
breaks, parts of it still apply and others do not fit; this subsection says which, so
that the specification claims no more than it covers. It is informative and adds no
requirement.

| # | Assumption | Where it breaks | Why | What still applies |
|---|---|---|---|---|
| 1 | A verdict exists for each case when the test runs | Credit scoring, hiring, insurance, forecasting | The true outcome arrives later, after months or a year | Contracts, Baselines, Quality Gates, Traceability. A Result whose Oracle arrives later is not defined |
| | | Fairness, probability calibration | The property belongs to a population, not to one case | Quality Gates on aggregates. A Result, as the unit of checking, does not fit |
| | | Recommendation, search, ranking | No single correct answer; quality shows in what users do | Validators, Regression Suites. The main evaluation is an online experiment, which AQEF does not specify |
| 2 | Interaction is a Conversation: a request, a Response, actions | Robotics, drones, vehicles, real-time control, automated trading | A continuous stream of decisions with feedback; no discrete Conversation to assess | The ideas of a Contract and of Seeded Controls, not the Execution model |
| 3 | The boundary is a software sandbox | Robotics, vehicles, medical devices | Consequences are physical and may be irreversible; a simulation is not the world | The Action Boundary as an idea. Physical containment is a different engineering discipline |
| 4 | Release is a decision taken before deployment | Recommender and advertising systems, systems that learn online | The model changes in production; a version is not fixed | Drift Detection, Production Replay. A Release Decision as a single event loses its meaning |
| 5 | No stricter certification regime applies | Road vehicles, aviation, medical devices | A mandatory life cycle, safety case and audit of their own | AQEF can supply evidence inside such a process, never replace it |

AQEF fits best today:

- text and multimodal generative systems;
- retrieval-augmented generation;
- agents acting in software environments;
- classifiers with labelled cases, where a verdict for each case is meaningful;
- assistive systems in which a person takes the decision.

Within a system that breaks an assumption, a component may still satisfy all five: a
perception model that labels one camera frame, a planner choosing one manoeuvre in a
fixed simulated situation, an interviewer holding one conversation with a candidate.
Each gives a verdict for each case, even where the driving of the vehicle or the hiring
decision as a whole does not. AQEF can apply to that component; it does not thereby
assess the whole system.

Where AQEF is used inside a regulated or certified process, it is one source of evidence
for that process. Passing AQEF Quality Gates is not evidence of compliance with any
standard, regulation or certification scheme (see "Specific regulatory or legal
requirements" below).

## Out of Scope

- **Model training and fine-tuning.** AQEF assesses an AI system's behavior; it does not
  specify how that system is built, trained, or fine-tuned. An Environment (Volume II)
  references a model version as configuration to test against, not a training procedure
  this specification governs.

- **Prompt engineering technique.** AQEF specifies how a Prompt gets versioned,
  interpolated with Variables (Volume III), and how drift in it gets detected (Volume X
  — Prompt Drift); it does not specify how to write an effective prompt for the system
  under test. That remains a system-design decision Test Design (Volume VIII) exercises
  judgment about, not a rule this specification prescribes.

- **The AI system's own business logic or product design.** AQEF is agnostic to what an
  AI system does — a customer-service Agent and a code-generation tool are tested by the
  same mechanism — because Scenario, Contract, and Quality Gate configuration is where a
  Project's actual product concerns belong, not this specification.

- **Specific regulatory or legal requirements.** Compliance (Volume XII) makes
  obligations verifiable — through Permissions, Audit, and Traceability — without AQEF
  itself enumerating what a Project must comply with. Which laws or contractual terms
  apply to a given Project's data is a question this specification defers to entirely,
  not one it answers.

- **Underlying AI infrastructure.** Model hosting, inference serving, and the runtime
  the AI system itself executes on are outside this specification; an Environment
  (Volume II) references that infrastructure by version and configuration, not by
  specifying how to build or operate it.

- **Model selection or ranking.** AQEF gives a Project the mechanism to compare behavior
  across Environments — Differential Testing (Volume VIII), Model Drift (Volume X) —
  for its own Scenarios and Contracts. It does not rank models in the abstract or
  recommend one model over another outside that context; it is not a benchmark or a
  leaderboard.

- **Testing process, roles, and organizational structure.** AQEF specifies a model and a
  vocabulary, not a methodology. It does not prescribe who performs testing, what
  qualifications they hold, how a team is organized, how much testing is enough, what
  documentation must be produced, or in what sequence a project's work should proceed.
  Governance (Volume XII) specifies the mechanism by which a Project *can* express such
  constraints — Roles, Permissions, Approval Workflow — precisely so that each Project
  decides its own, rather than inheriting one from this specification.

- **Judgment about what is worth testing.** A Quality Contract records an expectation
  once someone has decided it matters; it does not decide that for them. Which Scenarios
  are worth writing, which risks deserve attention, and when exploratory work will reveal
  more than a codified check are questions of skill and context that Test Design (Volume
  VIII) supports with technique and deliberately does not replace with rules. A
  specification can make an expectation explicit, reviewable, and comparable over time;
  it cannot supply the judgment that produced the expectation in the first place, and
  AQEF does not attempt to.

- **A CI/CD platform's or cloud provider's own native features.** Volume XIII names four
  platforms' integration patterns and Volume XVII names Cloud and Self-hosted
  Architecture as deployment choices, but a platform's own native primitives — a status
  check, a release gate, a specific cloud service — remain that platform's own
  specification, not AQEF's.

---

Where this specification is silent on something not listed here, that silence should be
read as an open question this document has not yet reached, not as an implicit
exclusion — Scope names what AQEF deliberately does not cover, not everything it simply
has not addressed yet.
