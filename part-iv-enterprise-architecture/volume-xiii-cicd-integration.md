# Volume XIII — CI/CD Integration

**Status:** confirmed (v0.1).

*Question answered:* How AQEF plugs into a deployment pipeline.

Chapter 6 already anticipated this Volume directly: "the same Gate is what a Report
surfaces for human visibility (Volume XI) and what a CI/CD pipeline queries to decide
whether a deployment may proceed (Volume XIII) — one mechanism, viewed from two places,
not two different things wearing the same name." This Volume specifies that second view:
how a Quality Gate's status reaches an external CI/CD platform, how Approval Workflow's
override path (Volume XII) surfaces there when a Gate fails, and the four platforms
named below as the concrete integrations most Projects will actually use.

## GitHub Actions

A GitHub Actions integration runs AQEF as a workflow step — typically a published
Action wrapping the CLI or REST API surface Volume XIV specifies — triggered the same
way Chapter 5's Scheduling already names CI/CD triggering: on a pull request, a merge,
or a schedule defined in the workflow file itself, not by AQEF. The step's exit status
and any Quality Gate results it produces surface through GitHub's own status-check
mechanism, which is how a Quality Gate failure actually blocks a merge — GitHub's status
check is the platform-native primitive AQEF's Gate result gets translated into, not a
second, competing gate.

## GitLab

A GitLab integration runs the equivalent way, as a job within a pipeline definition,
surfacing through GitLab's own pipeline status and merge-request approval rules. The
integration pattern is identical to GitHub Actions' in every respect that matters to
AQEF — what changes is only which platform-native status mechanism the Quality Gate
result gets translated into.

## Azure DevOps

Azure DevOps ships its own native feature literally called a "release gate." This is
not the same thing as AQEF's Quality Gate (Chapter 6), and the two MUST NOT be
conflated: AQEF's Quality Gate is defined once, platform-agnostically, in Chapter 6; an
Azure DevOps release gate is that platform's own native primitive, which an AQEF
integration can wire a Quality Gate's result into, the same way a GitHub status check or
a GitLab approval rule can — but the AQEF concept does not inherit Azure's name, and an
Azure-specific release gate configured to check something other than an AQEF Quality
Gate is not thereby an AQEF concern.

## Jenkins

A Jenkins integration runs as a pipeline stage, typically via a plugin or a direct CLI
invocation, surfacing through Jenkins' own build status and stage-result mechanisms —
the same translation pattern as the three platforms above, with Jenkins' own vocabulary
standing in for GitHub's status checks or Azure's release gates.

## Pipelines

What the four platforms above share is not incidental: every CI/CD integration reduces
to the same shape — an external pipeline invoking AQEF at a defined point, reading back
a Quality Gate result, and acting on it through whatever native gating primitive that
platform offers. This is why the four sections above are short: the platform-specific
work is translation, not reimplementation, and a platform not named above — any CI/CD
system capable of running a CLI step and reading an exit code or an API response —
integrates the same way without AQEF needing to specify it individually. A Pipeline
invocation is, from AQEF's own side, simply one more entry point into Scheduling (Volume
III); Chapter 5 already named "triggering on demand from a CI/CD pipeline" as one of
Scheduling's legitimate trigger sources, not a separate execution mechanism requiring
its own mechanics. "Pipeline" here always means the external platform's own build/deploy
pipeline — distinct from AQEF's own internal "___ Pipeline" terms (Execution Pipeline,
Validator Pipeline, Decision Pipeline), which always carry a qualifier.

## Quality Gates

This section specifies only the CI/CD-facing translation, not the Gate itself, which
remains Chapter 6's. A Pipeline invocation reads a Quality Gate's pass/fail/override
status — Volume XI already specifies how that status is surfaced generally — and
translates it into whatever native primitive the platform offers, so a failing Quality
Gate blocks the Pipeline the same way any other native pipeline failure would, without a
person needing to check AQEF's own Report or Dashboard separately to know a deployment
was blocked. Where a Quality Gate failed but Approval Workflow (Volume XII) logged an
explicit override, the Pipeline MUST reflect the override's outcome, not the underlying
Gate's raw failure — a Pipeline showing a red status for a deployment Governance has
already, explicitly approved would misrepresent a decision that was actually made, the
same silent-versus-explicit distinction Approval Workflow exists to keep from getting
lost downstream.

---

With Volume XIII, a Quality Gate's status reaches as far as a deployment pipeline, not
just a Report or a Dashboard — the same signal, Chapter 6 already insisted, viewed from a
third place now. Volume XIV (SDK & APIs) is next: it specifies the CLI and API surface
every integration in this Volume has been invoking without yet having a defined shape.
