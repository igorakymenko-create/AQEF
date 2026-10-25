# 10. Conformance

Conformance is a property of an AQEF *implementation* — the engine, tooling, or
platform executing this specification — not of any AI system under test. An AI system
does not "conform to AQEF"; it is assessed by an AQEF-conformant engine, and how well it
performs against that assessment (its Release Decision, its Quality Gate status) is a
completely separate question from whether the engine doing the assessing correctly
implements this specification. This section defines the latter only.

Conformance is likewise not a property of a person, a team, a process, or an
organization. There is no such thing as a conformant tester, a conformant test strategy,
or a conformant QA department under this specification, and no part of this document
provides a basis for assessing one. A tool can be measured against the requirements
below; a practitioner's judgment cannot, and this specification offers no criteria by
which anyone could attempt it. Where a Project or a contract wishes to impose obligations
on how people work, those obligations are its own — Governance (Volume XII) gives it the
mechanism to express and audit them, without this specification supplying their content.

## What Conformance Requires

An implementation is AQEF-conformant if it satisfies every applicable MUST-level
requirement across the Volumes whose capability it actually offers — see "Deviating
from a SHOULD," below, for how SHOULD-level requirements bear on Conformance separately.
Conformance is scoped to claimed capability, not universal completeness: an
implementation that does not integrate with
CI/CD is not non-conformant for lacking Volume XIII's behavior, because Volume XIII's
rules simply do not apply to a capability it does not claim. An implementation that does
integrate with CI/CD MUST follow Volume XIII's rules for it. The same scoping applies to
specific SDKs (Volume XIV), Reference UI (Volume XV), Plugin Architecture (Volume XVI),
Dataset sources beyond Static (Volume IV), Multi Judge and Human Review (Volume VI),
Seeded Controls (Volume VIII), and subjects that act through tools (Action Boundary,
Volume III).

## Conformance Statement

Because Conformance is scoped to claimed capability, a claim of Conformance says nothing
until it says which capabilities it covers. An implementation that claims AQEF
Conformance MUST publish a **Conformance Statement** stating:

- the version of this specification it conforms to;
- the capabilities it claims, from the scoped set above, using the identifiers below;
  the non-negotiable core (next section) is part of every claim and is not listed;
- how it binds Projects and Suites to Teams, or that it binds none (Volume XII, Teams).

It MAY also state capabilities it deliberately does not offer, and SHOULD-level
requirements it deviates from (see Deviating from a SHOULD, below).

| Identifier | Capability |
|---|---|
| `dataset:<source>` | A Dataset source beyond Static: `generated`, `production_replay` (Volume IV). `dataset:synthetic` is reserved (Document Status). |
| `dataset_mechanism:<type>` | Reserved (Document Status): a Dataset mechanism, `data_mutation`, `fuzzing`, `edge_cases`, `adversarial` (Volume IV; Appendix A §A.8). Cannot be claimed in this version. |
| `multi_judge` | Multi Judge, Consensus, Voting (Volume VI) |
| `human_review` | Human Reviewer as an Oracle and Human Review (Volume VI) |
| `seeded_controls` | Seeded Controls, including fixed Evidence (Volume VIII) |
| `action_boundary` | Subjects that act through tools (Volume III) |
| `ci_cd:<platform>` | A CI/CD integration (Volume XIII) |
| `sdk:<language>` | A language SDK (Volume XIV) |
| `cli` | A command-line interface (Volume XIV) |
| `reference_ui` | Reference UI (Volume XV) |
| `plugins:<type>` | Plugin Architecture: `validator`, `judge`, `dataset`, `report` (Volume XVI) |

The form of the statement is the implementation's choice; this one is recommended:

```yaml
aqef_conformance:
  specification_version: "1.0-CR1"
  implementation: "Example Engine 1.2"
  capabilities:
    - human_review
    - seeded_controls
    - dataset:generated
    - ci_cd:github_actions
  not_offered:
    - multi_judge
    - plugins:judge
```

A Conformance Statement says what is to be checked. It does not show that the checks
pass.

## The Non-Negotiable Core

Two things bind every conformant implementation regardless of scope, and cannot be
reduced away by claiming a smaller capability set:

- **The five logical layers** (Chapter 4 — Definition, Execution, Evidence, Assessment,
  Decision) MUST each be met somewhere. An implementation that cannot define a Scenario
  and Contract, execute it, capture evidence, assess it with at least one Oracle, and
  reach some Decision has not implemented a partial slice of AQEF — it has not
  implemented AQEF's basic loop at all.
- **Chapter 3's seven principles** — Contracts over Assertions, Validation before
  Evaluation, Independent Oracles, Deterministic Infrastructure, Probabilistic Subject,
  Everything is a Test, Everything has Confidence — bind unconditionally. They are not
  one Volume's capability that scope can exempt an implementation from; every other MUST
  in this specification is, in some form, an application of one of these seven.

## Topology Is Not a Conformance Axis

Minimal Engine and Enterprise Engine, Cloud and Self-hosted Architecture (Volume XVII)
are implementation choices, not conformance levels. Both satisfy the identical normative
bar through different mechanisms — a Minimal Engine's single-click Approval Workflow and
an Enterprise Engine's multi-Role review chain are equally conformant realizations of
the same Governance requirement (Volume XII), not a stricter and a looser version of it.
This section only confirms that Conformance itself is not a second place where that
question could be reopened.

## Deviating from a SHOULD

Normative Language (§9) defines what MUST, SHOULD, and MAY mean precisely; this section
states only how deviation bears on Conformance. A conformant implementation MAY deviate
from a SHOULD-level requirement — Validators SHOULD run cheapest-first (Volume V), a
Generated Dataset SHOULD draw on an independent source (Volume IV) — without losing
Conformance, but such a deviation ought to be a deliberate, traceable choice, not a
silent gap: the same Traceability (Volume XII) that reconstructs why a Baseline was
approved or a Quality Gate overridden is the natural place a SHOULD-level deviation's
own justification would live, if a Project chooses to record one. Conformance does not
require recording that justification; it requires only that the deviation was a choice,
not an oversight nobody noticed.
