# Volume VII — Quality Contracts

**Status:** confirmed (v0.1).

*Question answered:* How expected quality is specified.

Chapter 3 named Contracts over Assertions as a founding principle, and the Glossary
already defines a Quality Contract as a declarative specification stating which Oracles
MUST be applied, what constitutes a passing Result under each, and what Confidence
threshold makes a Result actionable. Every Volume since has referred to "a Contract
clause" or "what the Contract requires" without specifying what a Contract actually
looks like as an authored artifact. This Volume closes that gap: the language a Contract
is written in, the two kinds of clause it can contain, how a Confidence threshold
attaches to one of them, the policies that govern how a Contract's own clauses combine,
how several Contracts compose into one, and how a Contract gets authored once and reused
broadly. "Contract" and "Quality Contract" remain the same entity throughout — schema-
level name and prose name for one thing, not two.

| Section | Role |
|---|---|
| Contract Language | The declarative grammar a Contract is expressed in; concrete serialization lives in Appendix A/B |
| Constraints | Validator-bound clauses — deterministic, no Confidence |
| Expectations | Judge-bound clauses — criteria-based, Confidence-qualified |
| Confidence | The threshold a Contract sets per Expectation, consumed by Chapter 6's Confidence Model |
| Policies | Composition/weighting rules governing how a Contract's own clauses combine |
| Contract Composition | Combining clauses from multiple Contracts/fragments into one effective Contract (Chapter 7 — Hybrid Systems) |
| Reusable Contracts | Authored once, attached to many Scenarios/Suites/Projects (Chapter 3 — Contracts over Assertions) |

## Contract Language

A Quality Contract is a declarative specification, not executable code (Chapter 3 —
Contracts over Assertions): its language describes what MUST hold, not how to check it.
Concretely, a Contract is a named collection of clauses — Constraints and Expectations,
below — each binding to one or more Oracles, plus the Policies that govern how those
clauses combine. This Volume specifies that conceptual grammar; the concrete
serialization a Contract is actually written in — its YAML form (Appendix A) and the
JSON Schema that validates it (Appendix B) — is generated from the entities this Volume
and Volume II define, not authored independently, for the same reason Appendix A already
states: authoring the schema by hand alongside the prose risks exactly the drift Chapter
3 warns against for inline assertions.

## Constraints

A Constraint is a Contract clause bound to a Validator: a deterministic, rule-based
expectation — a required schema, a forbidden pattern, a latency ceiling — that either
holds or does not, with no Confidence value attached, because the Validator checking it
carries none (Volume V). Constraints are how Functional and Operational Quality, and the
hard half of Safety (Chapter 2), get expressed in Contract language. A Constraint MUST
name the Validator, built-in or custom (Volume V), it binds to and what that Validator's
Result must show to count as passing; a Constraint that cannot be phrased this
concretely is not yet specific enough to be one — it belongs instead as an Expectation,
below, or as a Requirement that has not yet reached Test Design (Chapter 5).

## Expectations

An Expectation is a Contract clause bound to a Judge, or, where the Contract requires
it, a Human Reviewer: a criteria-based statement about subjective or semantic quality —
faithfulness, helpfulness, appropriate tone, reasoning quality — that the Oracle assesses
and reports a Confidence-qualified verdict against (Volume VI). Expectations are how
Semantic and Business Quality, and the contextual half of Safety, get expressed in
Contract language. An Expectation MUST state its criteria explicitly enough for a
Judge's Architecture (Volume VI) to make them inspectable — the same "Contracts over
Assertions" requirement that governs Constraints applies here too, just applied to
criteria an Oracle assesses rather than a rule a Validator checks.

An Expectation SHOULD be authored narrowly enough that one clause yields exactly one
Result. A criterion broad enough to span several independent assertions — "the response
is faithful to the retrieved context", over a response making a dozen separable claims —
forces the Judge to reduce many internal verdicts into a single score before any Contract
mechanism can act on them, and that reduction is an unweighted mean the Contract never
specified and no consumer can see. Where the assertions differ in what their failure
costs, they belong in separate Expectations, each independently weightable under Policies
below. Where a broad criterion genuinely cannot be decomposed, Volume VI requires the
Judge's Result to declare itself an aggregate rather than present the score as an atomic
verdict.

## Confidence

Confidence, in Contract language, is the threshold an Expectation clause sets for when a
Judge's Result is actionable at face value rather than routed to Human Review — the same
threshold Chapter 6's Confidence Model reads and Volume VI's Confidence section
describes a Judge producing. A Constraint never carries a Confidence threshold, because a
Validator's Result carries no Confidence value to threshold in the first place —
"Everything has Confidence" requires a Validator to declare
Confidence inapplicable, not to have a threshold applied to an absent value. Setting a
Confidence threshold is therefore a property exclusively of Expectations; a Contract
Language that allowed one on a Constraint would be describing something Volume V's
Validator Architecture cannot actually produce.

## Policies

A Policy is a Contract-level rule governing how the Contract's own clauses combine,
rather than a clause in its own right. Two mechanisms already specified in earlier
Volumes are, in Contract terms, Policies authored here and executed there: Validator
Composition's AND / OR / hard-veto rules (Volume V) are a Policy stating how multiple
Constraints bound to the same Execution combine into one verdict; a Scenario's Business
Quality weight or criticality (Chapter 2), which the Aggregation Model (Chapter 6) reads
when combining Results across many Executions, is a Policy stating how much this
Contract's failures should move an aggregate relative to others. A Policy does not
itself produce a Result — it configures how Results produced elsewhere get combined,
which is why it is specified here, alongside the clauses it governs, rather than in
Volume V, VI, or Chapter 6, where it is actually applied.

A Policy MAY set weight or criticality on an individual clause rather than on the
Scenario as a whole. Scenario-level weighting answers "how much does this situation
matter relative to others" and is what the Aggregation Model (Chapter 6) reads across
Executions; clause-level weighting answers a different question — "within this one
response, which expectations are load-bearing" — and Scenario-level weighting cannot
express it, because every clause in a Contract attaches to the same Scenario. A Contract
covering a response that must be both factually exact and appropriately worded is
mis-specified if a wrong figure and an awkward register carry equal weight, and no
Scenario-level criticality can separate them.

## Contract Composition

Contract Composition combines the Constraints, Expectations, and Policies of two or more
contributing Contracts — or Reusable Contract fragments, below — into one effective
Contract for a Scenario, Suite, or Project. This is the mechanism Chapter 7 already
relies on for Hybrid Systems: a Scenario combining RAG, Tool Calling, and
Human-in-the-loop composes each pattern's relevant clauses rather than requiring one
Contract authored from scratch. Composition is additive by default — every contributing
Contract's Constraints and Expectations apply, an implicit AND across contributing
Contracts, consistent with how Validator Composition already combines multiple
Constraints within one Contract (Volume V). Where two contributing Contracts specify
genuinely conflicting values for the same clause — different Confidence thresholds on
the same Expectation, for instance — Composition MUST surface the conflict explicitly
rather than silently resolve it; silently picking one value would hide exactly the kind
of drift Chapter 3 requires a Contract to remain auditable against.

## Reusable Contracts

A Reusable Contract, or Contract fragment, is authored once and attached to many
Scenarios, Suites, or Projects (Glossary), rather than rewritten per Scenario. This is
what makes Contract Composition practical at scale: a Project maintains a library of
fragments per recurring concern — a standard Safety Constraint set, a standard RAG
Faithfulness Expectation — and composes them into an effective Contract per Scenario
rather than authoring each one from nothing. Reusable Contracts carry their own version
history, distinct from a Dataset's (Volume IV) but serving the same
underlying purpose: a specific Execution's Result is only auditable against the exact
Contract that produced it if that Contract's own content is pinned to a specific
version, not silently mutable underneath it. This is precisely the "versioned...
audited for drift over time" property Chapter 3 requires of a Contract in the first
place — Reusable Contracts are what make that property survive reuse at scale rather
than only holding for a Contract nobody shares.

---

With Volume VII, a Contract clause stops being something every earlier Volume merely
referred to and becomes something with a specified shape: two kinds of clause, one
Confidence-bearing and one not, governed by Policies that earlier Volumes already
executed without this Volume having named them as such. Volume VIII (Test Design) is
where Scenarios and the Contracts attached to them get authored together in practice;
this Volume specifies what gets authored, Volume VIII specifies how.
