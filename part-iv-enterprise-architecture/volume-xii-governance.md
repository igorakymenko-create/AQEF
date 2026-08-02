# Volume XII — Governance

**Status:** confirmed (v0.1).

*Question answered:* Who is allowed to do what, and how that stays provable.

Chapter 4 already framed Governance as wrapping around AQEF's data flow rather than
sitting inside it — "the layer that determines who is permitted to trigger, approve, or
override any step within it" — and named four specific actions it controls: defining a
Contract, approving a Baseline, overriding a Quality Gate, and authorizing a Release
Decision. This Volume specifies the mechanism: who can act (Teams, Roles, Permissions),
how what happened gets verified after the fact (Audit, Traceability, Compliance), and
the single workflow (Approval Workflow) that ties both together for the four actions
Chapter 4 already named.

## Teams

A Team is an organizational grouping of people who share ownership of, or working access
to, a Project's Scenarios, Suites, or Contracts — a scope, not a capability. A person's
Team membership determines which Projects and Suites they can see and act within at all;
it says nothing yet about which specific actions they are permitted to take once inside
that scope, which is Roles' and Permissions' job, below. A Team is the natural unit
Reusable Contracts (Volume VII) and Dashboards (Volume XI) are typically scoped to as
well — the same organizational boundary recurring across what a group shares, not a
separate concept invented for Governance alone.

## Roles

A Role is a named, reusable bundle of Permissions (below) assigned to a person, not an
independent governance primitive of its own. Where Teams answer "what can this person
see," Roles answer "what can this person do" once inside that scope — the two are
orthogonal: a person's Team scopes their access, their Role scopes their capability, and
a Project typically needs both dimensions specified before a specific action is actually
authorized.

## Permissions

A Permission is the atomic unit Roles are built from: the capability to perform one
specific, named action — define a Contract, approve a Baseline, override a Quality Gate,
authorize a Release Decision (Chapter 4's own list), or a Project-specific action beyond
those four. A Permission MUST be checkable independently of any Role that happens to
include it, the same way a Constraint (Volume VII) MUST be checkable independently of
which Contract happens to reference it — a Role is a convenience for assignment, not the
unit Governance actually enforces at the moment an action is attempted.

## Audit

Audit is the retrospective review capability: querying the historical record of
Governance-controlled actions broadly — everything a Team did, everything of a given
action type, everything within a time range — for verification or investigation after
the fact. Audit answers "what happened," at whatever scope the question is asked,
without needing to already know which specific decision to look for; Traceability,
below, is the narrower counterpart for when the specific decision is already known and
what's needed is its full chain.

## Traceability

Traceability is the capability to reconstruct the full authorization chain behind one
specific artifact or decision — which Report a Release Decision relied on, which Quality
Gates it read, which Baseline a Regression Gate compared against, who approved that
Baseline and when. Where Audit answers a broad "what happened," Traceability answers a
narrow "how did we get to this specific outcome" — the same underlying logged records,
queried differently. A Release Decision that cannot be traced this far back is not
meaningfully audited, no matter how complete the Audit log around it otherwise is.

## Compliance

Compliance is where Governance meets policy AQEF does not itself author — the privacy
and data-handling requirements Volume IV's Production Replay already deferred to, along
with any regulatory, contractual, or internal-policy requirement outside AQEF's own
remit. AQEF's role is not to define what a Project MUST comply with, but to make
compliance verifiable: Permissions restrict who can access sensitive data (Production
Replay Datasets, Volume IV, chief among them), and Audit and Traceability provide the
record a Compliance review actually checks against. A Project's specific compliance
obligations are configuration Governance enforces, not content this Volume specifies.

## Approval Workflow

Approval Workflow is the single mechanism — a request, review by someone holding an
appropriate Role, an explicit approve-or-deny decision, logged for Audit and
Traceability — that Chapter 4's four named actions all go through: defining a Contract,
approving a Baseline, overriding a Quality Gate, and authorizing a Release Decision.
These are four configurations of the same workflow, not four separate mechanisms — what
differs between them is which Permission a Role must hold to review the request, not the
shape of the request-review-decision-log sequence itself. This is also what makes every
"MUST be explicit, not silent" requirement earlier Volumes already stated enforceable
rather than aspirational: a Quality Gate override (Chapter 6), a Baseline designation
(Volume X), and a Contract Composition conflict escalated for resolution (Volume VII)
all resolve through this one workflow, which is why none of those earlier Volumes needed
to invent an approval mechanism of their own — Approval Workflow was always the
mechanism they were deferring to.

---

With Volume XII, every action earlier Volumes described as Governance-controlled now has
a specified mechanism behind it — Chapter 4's four named actions, and the Contract
Composition and Baseline cases besides, all resolve through the same Approval Workflow,
reviewed by a Role holding the right Permission, within the scope a Team defines, and
recorded for the Audit and Traceability Compliance depends on. Part IV's remaining two
Volumes specify how AQEF gets built on and integrated: Volume XIII (CI/CD Integration)
covers how a Quality Gate's status actually reaches a deployment pipeline, and Volume XIV
(SDK & APIs) covers the programmatic surface everything specified so far is exposed
through.
