# Volume XI — Reporting & Analytics

**Status:** confirmed (v0.1).

*Question answered:* How Results become visibility.

Chapter 4 named Reporting & Analytics as the component that aggregates Results into
Metrics, compares them against Baselines and Snapshots, and produces Reports (Volume I);
nearly every Volume since has forward-referenced it as the place a specific signal "is
worth surfacing." This Volume specifies the mechanics: how a Metric (Volume II) gets
computed from Results in general — distinct from Chapter 6's Aggregation Model, which is
a further, decision-specific combination of a subset of those same Results built for
Quality Gates, not a synonym for Metric computation itself — and the six consumers of
that computation: Reports, Dashboards, Trends, Quality Gates (as surfaced here, not as
defined — that remains Chapter 6's), KPIs, and Historical Analysis.

## Reports

A Report (Volume II) is a structured, point-in-time presentation of Metrics and Results
for a Suite, Project, or time range — frozen at the moment it is generated, which is
what makes it suitable as attached evidence for a Release Decision (Chapter 5, Chapter
6) rather than something that silently changes underneath a decision already made.
Beyond the Metrics and Results Volume II already names, a Report MUST surface the
specific signals earlier Volumes have already flagged as worth including, not buried in
raw data a reader would have to reconstruct by hand:

- an unusual concentration of infrastructure-level Retries on one Scenario (Volume III),
  as a Reliability signal independent of any individual attempt's eventual Result;
- a cluster of low-Confidence Results concentrated on one Scenario or one Judge (Volume
  VI), independent of any individual Result's disposition;
- which purpose — independence or stability — a Multi Judge configuration was providing
  (Volume VI), not "ran more than one Judge" as an undifferentiated
  signal of rigor;
- the status of every Quality Gate applicable to the Report's scope (Chapter 6),
  including which Gates passed, failed, or triggered a Governance-logged override.

A Report that omits these is not wrong, but it is incomplete in a way a reader has no way
to notice from the Report alone — precisely the failure mode surfacing them by name is
meant to prevent.

## Dashboards

Where a Report is frozen at generation time, a Dashboard is a live view of the same
underlying Metrics that updates as new Results arrive, built for ongoing monitoring
(Volume II) rather than as evidence attached to one Release Decision. A Dashboard MAY
present the same content a Report would, but its defining property is that it has no
fixed "as of" moment — a Report generated from a Dashboard's current state at a specific
time is a snapshot of it, not the other way around. Volume XV's Reference UI specifies
the concrete interface a Dashboard is presented through; this Volume specifies only that
the underlying Metrics and their live update are Reporting & Analytics' responsibility,
not the UI layer's.

## Trends

A Trend is a Metric plotted across a time range rather than read at a single point —
pass rate over the last ten releases, mean Confidence over the last month — and is
ordinarily a Dashboard's primary content, since a Trend only means something while it
keeps updating. A Trend is also the first-visible symptom for most of what Volume X's
Drift Detection and Volume VI's Judge Drift exist to diagnose: a Trend shows *that*
something is moving, not *why* — determining why is Historical Analysis's job, below,
once a Trend has flagged that something is worth investigating.

## Quality Gates

Quality Gate is defined in full in Chapter 6, not here; this section specifies only how
a Gate's status gets surfaced once computed. Every Quality Gate applicable to a Report's
or Dashboard's scope MUST show its current status — pass, fail, or a Governance-logged
override (Volume XII) — and, where it failed, which aggregate and threshold it failed
against, so a reader is never left inferring a Release Decision's outcome from the
underlying Metrics themselves. A Dashboard's Quality Gate display is live in the same
sense the rest of its content is; a Report's is frozen at generation time, which is
exactly why a Quality Gate override MUST be logged rather than silently applied — a
Report generated after the fact needs to be able to show that an override happened, not
just a passing Gate indistinguishable from one that never failed.

## KPIs

A KPI is not a new kind of measurement — it is a curated, typically small selection of
existing Metrics (Volume II) a Project elevates to prominent, ongoing visibility: an
overall pass rate, a mean Confidence, a Semantic Regression rate. Choosing what counts as
a KPI is a Project-level decision, not something this Volume prescribes universally, but
a KPI MUST be traceable back to the Metric(s) it is drawn from — a KPI that cannot be
decomposed back into the Results and Metrics behind it would be exactly the kind of
opaque, unauditable summary Chapter 3's Contracts over Assertions principle already
rules out at the Contract level, applied here to reporting instead.

## Historical Analysis

Historical Analysis is the deeper, investigative counterpart to a Trend: where a Trend
shows that a Metric is moving, Historical Analysis is what a person or process uses to
determine why, by correlating that movement against Environment, Dataset, and Contract
version history over the same time range. This is the capability Volume X's Drift
Detection and Volume VI's Judge Drift both depend on directly — neither is read off any
single Execution; both require exactly the across-many-Results-over-time comparison
Historical Analysis provides. In particular, distinguishing subject drift from Judge
Drift requires Historical Analysis to correlate a Judge's own
verdict history against Human Reviewer agreement over the same range, not just the
subject's Metrics against their Baseline — the same underlying capability applied to the
Oracle instead of the system under test.

---

With Volume XI, every signal earlier Volumes asked to be "surfaced to Reporting" now has
a specified home: Reports and Dashboards for what is visible now, Trends and Historical
Analysis for what only shows up by comparison over time, KPIs for what a Project has
chosen to elevate, and Quality Gates for what a Release Decision already depends on.
Volume XII (Governance) is next: it specifies who is allowed to approve a Baseline,
override a Quality Gate, or act on a Report at all — the layer Chapter 4 already
described as wrapping around this one rather than sitting inside its data flow.
