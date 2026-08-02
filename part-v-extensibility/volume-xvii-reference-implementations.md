# Volume XVII — Reference Implementations

**Status:** confirmed (v0.1).

*Question answered:* How this specification becomes running software.

Volume XVI's closing paragraph already named this Volume as the one that closes the
document: the Minimal Engine and Enterprise Engine shapes Chapter 4 and Volume III
already distinguished without yet specifying, and how the seventeen Volumes this
specification comprises actually come together as running software. Two independent
axes structure this Volume — topology (Minimal or Enterprise Engine) and deployment
environment (Cloud or Self-hosted Architecture) — plus Scalability, which specifies how
a Project moves along the first axis over time.

## Minimal Engine

A Minimal Engine collapses Chapter 4's five logical layers — Definition, Execution,
Evidence, Assessment, Decision — into a single process, typically one deployable service
sitting behind the REST API (Volume XIV) with no separately-scaled Execution Engine,
Validator Engine, or Judge Engine. This is a topology choice, not a reduced normative
bar: every MUST and SHOULD across all seventeen Volumes still applies. Governance's
Approval Workflow (Volume XII) still governs approving a Baseline or overriding a
Quality Gate, even where the Team is one person and the "review" is a single click;
Deterministic Infrastructure (Chapter 3) still holds, even where every Execution runs on
the same machine that triggered it. What a Minimal Engine is free to simplify is scale
and physical separation — a single SQLite-class datastore instead of a distributed one,
synchronous Scheduling instead of a priority queue across a worker fleet — never which
rule applies.

## Enterprise Engine

An Enterprise Engine runs Chapter 4's five layers as genuinely separate services, each
independently scaled: a Dataset Engine, an Execution Engine capable of Distributed
Execution (Volume III) across many workers, Validator and Judge Engines running as their
own services, and Reporting & Analytics and Governance as cross-cutting services the
others call into rather than embed. The same normative bar from Minimal Engine applies
unchanged — an Enterprise Engine satisfies no requirement a Minimal Engine does not, it
simply satisfies all of them at a scale and organizational complexity (multiple Teams,
differentiated Roles, CI/CD Integration as a first-class expectation rather than an
optional add-on, Volume XIII) a Minimal Engine's simpler topology was never built to
carry.

## Cloud Architecture

Cloud Architecture describes deployment on managed cloud infrastructure — an axis
independent of Minimal versus Enterprise, not a synonym for Enterprise: a Minimal Engine
MAY run as a single container on a single cloud instance, gaining managed infrastructure
without adopting Enterprise-scale topology, exactly as easily as an Enterprise Engine can
run its many separate services across a cloud provider's own distributed
infrastructure.

## Self-hosted Architecture

Self-hosted Architecture describes deployment on infrastructure a Project itself
controls, independent of scale in the same way Cloud Architecture is: a Minimal Engine
self-hosted on a single on-prem server and an Enterprise Engine self-hosted across an
organization's own cluster are both legitimate. Self-hosting is most often chosen for
Compliance (Volume XII), not simplicity — a Project whose Production Replay Datasets
(Volume IV) cannot leave its own infrastructure has a Compliance reason to self-host
regardless of whether its topology is Minimal or Enterprise.

## Scalability

Scalability specifies how a Project moves along the topology axis over time, not a fixed
choice made once: a Project MAY start as a Minimal Engine and grow into an Enterprise
Engine as its Suites, Datasets, and Teams grow past what a single process comfortably
carries, without that migration changing any Result, Baseline, or Report already on
record — the same normative bar held throughout means a migration changes topology, not
history. Appendix J — Migration Guide specifies the concrete steps; this section
specifies only that such a migration is a legitimate, anticipated path, not a rebuild.

---

With Volume XVII, all seventeen Volumes of AQEF are drafted: Part I argued for the
discipline and gave it a Domain Model; Part II specified how a Scenario becomes a
Result; Part III specified what gets tested, how, and against what history; Part IV
specified how AQEF is operated, reported on, and governed; Part V specified how it
extends and how it actually gets built. Front Matter beyond Terminology — Document
Status, Revision History, Contributors, License, Preface, Purpose, Scope, Intended
Audience, Normative Language, and Conformance — and all eleven Appendices are drafted
as well, completing the specification end to end.
