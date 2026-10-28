# AQEF — AI Quality Engineering Framework

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**An open specification for AI Quality Engineering as an engineering discipline.**

Version 1.0-CR1 · 2026-10 · Candidate Recommendation, open for review · by Igor Akymenko

📖 **[Read the specification](index.md)** · 📄 **[Download PDF](https://github.com/igorakymenko-create/AQEF/releases/latest)** · 💬 **[Open an issue](https://github.com/igorakymenko-create/AQEF/issues)**

---

## The problem

Software testing rests on one assumption: a program computes a specific function, and a
test compares the output it produced against the output it was specified to produce.
Everything classical testing knows how to do — unit, integration, property-based, fuzz,
snapshot — is a variation on where and how often that comparison happens.

Generative AI systems break the assumption. The same input can legitimately produce
different, equally correct outputs. Non-determinism isn't noise to be engineered away;
it's a property of the thing under test.

Applied without adaptation, classical practice fails in a predictable pattern:

- Exact-match assertions fail on paraphrase, producing false failures teams learn to ignore
- Coverage models built for code branches have no equivalent for a prompt
- Flaky tests get "fixed" by loosening assertions until they assert nothing — a green build
  with no check behind it, which is worse than no test, because it's mistaken for one
- Binary results can't express partial certainty — no way to separate "this passed" from
  "this technically matched but I wouldn't trust it"
- Literal output diffing breaks on the first model update, whether or not behaviour regressed

## What exists now

**Evaluation tooling** — benchmark harnesses, LLM-as-judge scoring, rubric frameworks — is
genuinely useful and solves a real part of the problem. But a benchmark run in isolation
has no contract defining what "acceptable" means for a specific behaviour, no requirement
that its oracle be independent of the system it judges, no confidence attached to its
verdicts, and no tie to a baseline or a release decision. It produces a score, not a
governed quality gate.

**Governance and risk frameworks** operate at the level of organisational policy. They
say what must be assured. They don't specify how a test is defined, executed, judged, or
compared against a reference.

The gap between them is where AQEF sits.

## What AQEF is

A specification of the engineering discipline in that gap: a domain model, a set of
principles, a reference architecture, and a conformance model — deliberately independent
of any tool.

17 volumes across 5 parts, plus front matter and 11 appendices.

## Conformance Test Specification

`conformance-tests/` holds the AQEF Conformance Test Specification: tests that check
whether an implementation meets the requirements it claims in its Conformance Statement
(§10). It is a separate, non-normative document, versioned on its own; where a test and
the specification disagree, the specification is right. `conformance-tests/_inventory/`
lists every requirement the tests trace to. Each release carries it as its own PDF.

## Reference implementation

[aqef-reference-engine](https://github.com/igorakymenko-create/aqef-reference-engine)
(Apache 2.0) is a minimal engine built to show that this specification can be
implemented as written. An agent that never saw the Conformance Test Specification
wrote it from the specification text alone, one slice at a time. The tests were run
against every slice; each failure was traced to the engine, the tests, or the
specification, and the specification's share was fixed in releases 0.41.2 to 0.41.5.

Its [Conformance Statement](https://github.com/igorakymenko-create/aqef-reference-engine/blob/main/docs/CONFORMANCE-STATEMENT.md)
claims Conformance to Version 1.0-CR1 for the core, `human_review`, `multi_judge`, and
`seeded_controls`. Conformance Tests WD9 against it: 189 passed, none failed, 33 not
applicable to the capabilities it claims or the features it offers, and one that this
engine cannot be driven to (a crashing Validator). The eight Inspection and Declaration
tests were decided by a named external reviewer, under CTS 1.8.

The tests were run with [aqef-cts-harness](https://github.com/igorakymenko-create/aqef-cts-harness)
(Apache 2.0). It drives the Conformance Test Specification against any engine through
the REST API of Appendix C, and plays the system under test and its Judges. The
repository holds the final run, with every exchange recorded as evidence, the review
records, and a self-test against a known-answer mock engine. Anyone can repeat the run.

The engine is a feasibility proof, not a product: one process, SQLite, a scripted HTTP
interface for the system under test and its Judges.

## Companion material

Informative documents that explain or apply this specification. They add no requirement;
where they differ from the specification, the specification is right.

- **[AQEF Textbook](https://github.com/igorakymenko-create/aqef-textbook)** — the theory
  behind AQEF, chapter by chapter. CC BY 4.0.
- **[AQEF Measurement Guide](guides/measurement/)** — from a risk to a trusted measurement,
  with a reference of common metrics and how to tell whether their results can be trusted.

## Core concepts

| Concept | What it is |
|---|---|
| **Quality Contract** | A declarative, reviewable artifact stating which Oracles apply, what passing means, and at what confidence a result becomes actionable |
| **Oracle** | The abstract role of deciding whether behaviour satisfies a Contract — realised as a Validator, a Judge, or a Human Reviewer |
| **Validator** | Deterministic, rule-based. Same input, same result. Carries no Confidence value |
| **Judge** | Probabilistic, criteria-based. Its Result carries a Confidence reflecting its own uncertainty |
| **Scenario / Execution / Conversation** | Definition, runtime event, and resulting data — three separate things, kept separate |
| **Confidence** | An axis independent of the verdict. Failing-at-low-confidence and passing-at-high-confidence are different outcomes |
| **Baseline** | A per-Scenario approved reference, used to detect Semantic Regression |
| **Semantic Regression** | A degradation judged by meaning and intent, not literal text equality |

## How it differs

**From classical testing** — expectations live in Contracts rather than inline assertions;
Oracles judge meaning rather than diff text; results carry confidence rather than assert a
certainty a probabilistic system can't offer.

**From evaluation tooling** — evaluation is one technique operating inside a lifecycle,
not the lifecycle itself. AQEF adds the contract, the independence requirement, the
confidence model, the baseline, and the tie to an explicit release decision.

**From a process standard** — AQEF specifies a model and a vocabulary, not a mandated
process. It doesn't say who should test, how much, in what order, or with what
documentation. Conformance is scoped to claimed capability over a small non-negotiable
core; it is not a pass/fail badge over the whole document, and it is not a property of a
person, a team, or an organisation — a Project's own Governance rules decide how people
work, not this specification. The intent is to make disagreement precise, not to settle
it — see [Scope](front-matter/06-scope.md) and
[Conformance](front-matter/10-conformance.md) for the full position.

## Status

Candidate Recommendation 1. The content is believed complete, and implementers are
invited to build against it and report issues, for a review period of at least eight
weeks. Some capabilities are marked at risk, and two are reserved for a later version;
see [Document Status](front-matter/00-document-status.md).

Nothing here is settled by authority — where a decision is contested, the argument for it
is written down and can be attacked on its merits. The design decisions behind the
terminology are recorded and reviewable rather than assumed. This is the work of a
single author, produced by no standards body or working group, and it does not claim to
represent a consensus of the software testing profession — see
[Document Status](front-matter/00-document-status.md) for the full position.

## Who this is for

- Engineers and QA specialists building test infrastructure for LLM-based systems
- Teams that have outgrown ad hoc eval scripts and need a model to organise around
- Tool authors wanting a vendor-neutral vocabulary to map their tool onto
- Anyone who thinks this is the wrong approach and can say precisely why

## Contributing

Disagreement is more useful than agreement right now. The most valuable contributions are:

- A concept that's missing, wrong, or collapses two things that should stay separate
- A place where the specification claims more consensus than actually exists
- A real system whose quality problem the model fails to describe

[Open an issue](https://github.com/igorakymenko-create/AQEF/issues) or start a discussion. Prose
contributions welcome once the structure has stabilised.

## Citing this work

If you reference or build on AQEF, please credit:

> Igor Akymenko, *AQEF — AI Quality Engineering Framework*, Candidate Recommendation 1.0-CR1,
> https://github.com/igorakymenko-create/AQEF

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
