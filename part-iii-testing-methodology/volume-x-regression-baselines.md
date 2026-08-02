# Volume X — Regression & Baselines

**Status:** confirmed (v0.1).

*Question answered:* How degradation over time is detected.

Chapter 1 already rejected literal output diffing as a regression check — it "breaks on
the first prompt or model update, whether or not behavior actually regressed." This
Volume specifies what AQEF checks instead: what a Semantic Regression actually is once
detected, how a Baseline gets approved and kept meaningful over time, and the
diagnostic work — Drift Detection, and its three specific causes — that explains why a
Regression happened once one is found, up to the wider, per-release comparison
reserved for Snapshot Comparison rather than Baselines.

## Semantic Regression

The Glossary already fixes what Semantic Regression is: a degradation, found by
comparing a current Execution's Result against its Baseline, in which a Conversation now
fails an Oracle it previously passed — judged by meaning and intent, not literal text
equality. This is the direct alternative to the literal diffing Chapter 1 already
rejected: not whether today's Response is character-for-character identical to the
Baseline's, but whether the same Oracle, applying the same Contract, now returns a
different verdict on behavior that means the same thing it always did. For an AI Agent
Scenario, this comparison operates on the trajectory as a whole rather than step-for-step
(Chapter 7) — the Probabilistic Subject principle applied one level up, from output text
to output trajectory. A Semantic Regression is, by Chapter 2's own framing, a Reliability
failure: detected by comparison against a specific reference point, not read off any
single Execution in isolation.

## Baselines

A Baseline (Volume II) does not become one automatically — an Execution's Result MUST be
explicitly designated as the reference standard, not inferred from simply being the
first or the most recent Execution of a Scenario. Designating a Baseline is ordinarily a
Governance-controlled action (Approval Workflow, Volume XII), the same kind of explicit,
logged decision Chapter 6 already requires of a Quality Gate override: a Baseline
silently replaced by whatever the last Execution happened to produce would let a genuine
regression get absorbed into the reference standard instead of caught against it. A
Baseline is only meaningful if it is reproducible back to the exact Dataset version
(Volume IV) and Contract version (Volume VII — Reusable Contracts) that produced it —
without both pinned, "the same Scenario" is ambiguous about which Variables and which
clauses actually applied, and a comparison against it would not isolate the subject's
behavior from a quiet change somewhere else in the pipeline.

## Drift Detection

A Semantic Regression is a symptom; Drift Detection is the diagnosis. Once a Result now
fails what it previously passed, Drift Detection is the practice of identifying which of
three inputs to the Execution changed to explain it — Prompt Drift, Model Drift, or
Dataset Drift, below — rather than treating every regression as an undifferentiated
"something changed." This distinction matters because the fix differs by cause: a Prompt
Drift is corrected by reverting or re-reviewing a prompt change, a Model Drift by pinning
or re-qualifying a model version, a Dataset Drift by reconciling a Dataset's own version
history. Drift Detection also has to rule out a fourth possibility that looks identical
in a Report: the Oracle changed, not the subject. Judge Drift (Volume VI) produces the
same visible symptom — a Result that now differs from what a Baseline expects — for a
completely different reason: the two are distinguished by checking whether Human
Reviewer agreement moved together with the Judge's — if only the Judge's verdicts
shifted while Human Reviewer agreement with the subject held steady, the Judge drifted;
if both shifted together, the subject did.

## Prompt Drift

Prompt Drift is a change in the prompt or instructions an Environment (Volume II)
resolves to, correlated with a Semantic Regression. Where the prompt is versioned
directly as part of the Environment's own configuration, Prompt Drift is ordinarily
visible just by diffing Environment versions across the two Executions being compared.
It is less visible, and more dangerous, when a prompt is sourced from a shared library
or template outside the Environment's own version record — Reusable Contracts (Volume
VII) and Prompt Construction (Volume III) both depend on exactly this kind of shared,
potentially silently-edited resource, which is why Drift Detection cannot assume Prompt
Drift will always show up as an explicit version bump.

## Model Drift

Model Drift is a change in the underlying model an Environment resolves to, correlated
with a Semantic Regression. The straightforward case — an Environment's model version is
deliberately upgraded — is the case Differential Testing (Volume VIII) exists to check
on demand, comparing behavior across the old and new Environment before the change is
adopted. The harder case is a model provider silently updating what a stable-looking
model identifier actually resolves to, with no change visible in AQEF's own Environment
configuration at all. This is a real limit on Deterministic
Infrastructure rather than a gap in it, and a Regression Suite (Volume IX) MUST be
able to surface Model Drift even when nothing AQEF-visible changed.

## Dataset Drift

Dataset Drift is a change in the Dataset (Volume IV) supplying Variables to a Scenario,
correlated with a Semantic Regression. Because every Dataset MUST be versioned (Volume
IV), Dataset Drift is ordinarily the most directly diagnosable of the
three: a Regression correlated with a Dataset version bump is Dataset Drift by
construction. Production Replay Datasets (Volume IV) carry a subtler version of this same
risk even between explicit version bumps — the distribution of real production traffic
feeding a Production Replay Dataset can shift gradually on its own, changing what a
"representative" row looks like well before anyone captures a new version.

## Snapshot Comparison

Snapshot Comparison is to a Project what Baseline comparison is to a Scenario — the same
underlying logic, one level up in scope. Where a Baseline is a single
Execution/Result pinned as the reference for one Scenario, a Snapshot freezes the wider
state of many Baselines plus configuration at a release point (Volume II); Snapshot
Comparison checks a Project's current state against a prior Snapshot to detect
release-to-release drift across an entire Suite or Project, not one Scenario at a time.
This is what a Regression Gate (Chapter 6) configured against a Snapshot rather than an
individual Baseline actually performs: not "did this one Scenario regress" but "did this
release, taken as a whole, regress relative to the last one" — a question no amount of
per-Scenario Baseline comparison, run one at a time, directly answers on its own.

---

With Volume X, Part III — Testing Methodology is complete: Volume VII specified what a
Contract is, Volume VIII specified how a Scenario and Contract get authored, Volume IX
named the categories of behavior a Contract checks for, and this Volume specifies how a
Result gets compared against history once produced. Every mechanism a Regression Suite
(Volume IX) relies on now has a specified source, from what counts as a Baseline to
which of four causes — Prompt, Model, Dataset, or the Oracle itself — a Report should
suspect first.
