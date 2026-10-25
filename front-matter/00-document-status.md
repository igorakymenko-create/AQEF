# 0. Document Status

**Status:** Candidate Recommendation 1.

**AQEF — AI Quality Engineering Framework**

| Property | Value |
|---|---|
| Status | Candidate Recommendation |
| Version | 1.0-CR1 |
| Date | 2026-10 |
| Maturity | Candidate Recommendation — implementers invited to build and report issues |

## What "Candidate Recommendation" Means

The content of this version is believed complete. Implementers are invited to build
against it, run the AQEF Conformance Test Specification (CTS), and report every place
where the text could not be followed as written. A Candidate Recommendation is not a
Standard: it may still change, under the rules below, in response to what implementing
it shows.

This version enters Candidate Recommendation on this evidence:

- A reference implementation, written from the specification text alone by a party that
  had not seen the CTS, claims Conformance to the non-negotiable core and to
  `human_review`, `multi_judge`, and `seeded_controls`. The CTS finds no failure against
  it. The implementation, the harness that ran the tests, the run, and its evidence are
  public.
- Every testable MUST in the requirement inventory has at least one CTS test (CTS,
  Section 90).
- The capabilities no implementation has yet built were read independently, as an
  implementer would read them. Their defects were corrected in this version, or the
  capability is reserved (below).

## Features at Risk

These capabilities have no implementation yet. Each stays in this version during
Candidate Recommendation. A feature at risk that has no implementation passing its CTS
tests when Candidate Recommendation ends is removed from 1.0, or moved to a later
version. Removing it does not restart Candidate Recommendation.

- `action_boundary` (Volume III, Action Boundary)
- `dataset:generated`, `dataset:production_replay` (Volume IV)
- `plugins:validator`, `plugins:judge`, `plugins:dataset`, `plugins:report` (Volume XVI)
- `ci_cd:<platform>` (Volume XIII)
- `sdk:<language>`, `cli` (Volume XIV)
- `reference_ui` (Volume XV)

## Reserved

These capabilities are named but not specified in this version. No implementation can
claim them, and every implementation rejects a configuration that uses them (Appendix A
§A.8). They are to be specified in a later version.

- `dataset:synthetic` (Volume IV, Synthetic Datasets)
- `dataset_mechanism:<type>` (Volume IV, Data Mutation, Fuzzing, Edge Cases, Adversarial)

## Reporting Issues

Report an issue at https://github.com/igorakymenko-create/AQEF/issues. Quote the text,
and say what you could not decide from it or what you would have built differently.
Every issue is answered, and the answer recorded: accepted with a change, accepted as
editorial, or declined with reasons.

The review period for this Candidate Recommendation runs for at least eight weeks from
its publication.

## Changes During Candidate Recommendation

- An editorial change, which changes no requirement, is published as a patch: 1.0-CR1.1.
- A normative change to a feature that is not at risk is published as a new Candidate
  Recommendation, 1.0-CR2, with the CTS revised to match.
- A feature at risk may be removed without a new Candidate Recommendation.
- No new feature is added. New features go to version 1.1.

## Authorship and Consensus

This specification is the work of a single author. It has not been produced by a
standards body, a working group, or an industry consortium, and it does not represent a
consensus position of the software testing profession — no such consensus on AI quality
currently exists, and this document does not claim to speak for one.

What it offers instead is an argument made explicitly enough to be disagreed with
precisely. The design decisions behind the terminology and the model were made
deliberately, the text gives their reasons where a reader needs them, and each is open
to being shown wrong. Where this document uses normative language (§9), MUST and SHOULD
constrain an implementation that chooses to claim Conformance (§10) — they are not a
claim of authority over how any person, team, or organization ought to work.

## Maturity Progression

| Stage | Meaning |
|---|---|
| Working Draft | Content is directionally stable but subject to structural change. Versions 0.1 to 0.41.5. |
| **Candidate Recommendation** ← current | Content is believed complete. Implementers are invited to build and report issues. |
| Proposed Standard | Every capability that is not at risk has at least two independent implementations, each passing the CTS with no failure and with its reviews signed. Every feature at risk has one such implementation, or has been removed. The review period has ended with every issue answered. A third party has repeated at least one published CTS run from its published harness and evidence. No normative issue is open. |
| Standard | Specification is stable and versioned for production use. |
