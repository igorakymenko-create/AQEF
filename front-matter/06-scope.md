# 6. Scope

**Status:** confirmed (v0.1).

## In Scope

Everything specified across this document's five Parts and ten Appendices: the Domain
Model and Fundamental Principles (Part I); how a Scenario becomes a Result (Part II);
what gets tested, how, and against what history (Part III); how AQEF is operated,
reported on, and governed (Part IV); how it extends and how it gets built (Part V); and
the concrete artifacts — schemas, API surface, diagrams, examples — the Appendices
generate from that content rather than author independently.

All of it applies specifically to testing the behavior of a Probabilistic Subject
(Volume I, Chapter 3) — an AI system whose output legitimately varies for the same
input. AQEF does not replace classical software testing for a product's deterministic
components; it governs the parts of a system where that assumption no longer holds.

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
