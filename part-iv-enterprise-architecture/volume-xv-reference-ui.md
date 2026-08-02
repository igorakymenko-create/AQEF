# Volume XV — Reference UI

**Status:** confirmed (v0.1).

*Question answered:* What a person actually looks at.

Volume XIV's closing paragraph already named this Volume as the last in Part IV, built
on the JavaScript/TypeScript SDK it specifies. This Volume's five sections are a
presentation and authoring layer over the REST API (Appendix C), not a parallel
implementation of AQEF's own logic — every section below enforces or faithfully presents
a constraint an earlier Volume already established, rather than introducing a UI-specific
shortcut around it.

## Visual Test Designer

The Visual Test Designer is where a person authors a Scenario and its Quality Contract
(Volume VII) without writing YAML or JSON directly (Appendix A, B) — the visual
counterpart to Test Design's forward-authoring entry point (Volume VIII). It produces
the same underlying Contract Language artifact any other authoring path produces, not a
UI-specific representation that would need separate translation before an Oracle could
act on it; a Scenario authored visually and one authored by hand in YAML MUST be
indistinguishable once saved. Test Design's other two entry points — Production Replay
and Exploratory sessions (Volume VIII) — surface here too, as the same "fold a captured
Conversation back in as a Scenario" action, not a separate feature requiring its own
design.

## Test Explorer

The Test Explorer is a browsing interface over existing Scenarios, Suites, and
Projects — read access to the same resources the REST API exposes, distinct from the
Visual Test Designer's authoring role the way Volume XII's Audit is distinct from an
action that changes state. A Test Explorer entry surfaces a Scenario's current status —
whether it has a Baseline (Volume X), which Suite(s) it belongs to, its most recent
Result — without exposing a path to silently edit that state outside the Visual Test
Designer's own authoring flow.

## Validator Designer

The Validator Designer configures built-in Validators (Volume V) and defines Custom
Validators through the same UI, and it MUST enforce the constraint Volume V already
states rather than let a UI make it easy to violate: a Validator configured here MUST be
deterministic and MUST NOT carry a Confidence value. A person attempting to configure a
check that calls a model to decide pass/fail is configuring a Judge (Volume VI), and the
Validator Designer MUST surface that distinction rather than silently accept the
configuration under the wrong label — the same requirement Volume V already
places on a Custom Validator's SDK, enforced here at the point of authorship rather than
left to be discovered later.

## Judge Configuration

Judge Configuration sets up Single Judge or Multi Judge, Consensus and Voting rules,
Confidence thresholds, and Calibration review (Volume VI) through the same UI. Where a
person configures Multi Judge, this section MUST require an explicit choice of which
purpose it serves — independence or stability — rather than default silently to one; a Judge Configuration screen that lets "add another Judge" stand in
for that choice would reintroduce exactly the undifferentiated signal of rigor Volume VI
already rules out.

## Reporting UI

The Reporting UI presents Reports, Dashboards, Trends, KPIs, and Historical Analysis
(Volume XI) — and it MUST visually distinguish a Report's frozen, point-in-time state
from a Dashboard's live, continuously-updating one, rather than
present both through one undifferentiated view a person could mistake for the other.
This is also where a Quality Gate's status (Chapter 6, surfaced per Volume XI) is shown
to a human directly, as opposed to Volume XIII's translation of that same status into a
CI/CD platform's native primitive — one signal, now visible from a third and final
place, a person looking at it rather than a pipeline consuming it.

---

With Volume XV, Part IV — Enterprise Architecture is complete: Reporting & Analytics,
Governance, CI/CD Integration, SDK & APIs, and Reference UI together specify how AQEF is
operated, not just how it is architected. Part V — Extensibility is what remains: Volume
XVI (Plugin Architecture) specifies how a Project extends AQEF's built-in Validators,
Judges, Datasets, and Reports beyond what this specification enumerates by name, and
Volume XVII (Reference Implementations) closes the document with the Minimal and
Enterprise Engine shapes Chapter 4 already distinguished.
