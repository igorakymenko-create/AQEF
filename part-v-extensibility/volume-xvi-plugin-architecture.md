# Volume XVI — Plugin Architecture

*Question answered:* How a Project extends AQEF without forking it.

Volume XV's closing paragraph already named this Volume: how a Project extends AQEF's
built-in Validators, Judges, Datasets, and Reports beyond what this specification
enumerates by name. The governing constraint is already set — a plugin, like
every SDK and the CLI, consumes AQEF's own REST API surface rather than reimplementing
AQEF's logic independently — and one requirement was already made explicit
before this Volume existed to enforce it: a Custom Validator's determinism and absence
of a Confidence value MUST be enforced at the SDK level, not merely documented as a
convention. This Volume specifies how: four plugin types, how a plugin is invoked, the
Authentication every one of them operates under, and the Extension Lifecycle that
governs how a plugin is installed, verified, and retired.

## Validator Plugins

A Validator Plugin extends Volume V's built-in set with a Project-specific check, and it
inherits Volume V's constraints exactly — deterministic, no Confidence value — not as
documentation a plugin author is trusted to follow, but as a requirement the Plugin
Architecture checks as far as a check can reach. Extension Lifecycle's registration step
(below) MUST run a candidate Validator Plugin against a fixed test input more than once
and reject registration if its output varies. This check is necessary, not sufficient:
a plugin that passes it has shown that it repeats itself on that input, not that it is
deterministic on every input — it could still read the clock, a random source, or an
external service. A successful registration MUST NOT be reported as proof of
determinism. The plugin remains bound by Volume V's definition of a pure Validator
throughout its use, and an implementation MAY re-check it later on stored Evidence
(Volume V — Validator SDK).

## Judge Plugins

A Judge Plugin extends Volume VI's Judge Engine with a Project-specific assessment model
or criteria set, and it carries an asymmetry Validator Plugins do not: a Judge's
defining property is that its Result carries a Confidence value reflecting genuine
uncertainty, which is not something a registration-time check can probe the way
repeatability can — running a Judge Plugin against a fixed input twice and getting
different Confidence values is expected, not a failure to catch. What the Plugin
Architecture can check mechanically stops at structure — does a Judge Plugin's Result
carry a Confidence value at all, does it declare the criteria it assesses inspectably
(Volume VI — Judge Architecture) — while Independent Oracles' actual substance, whether a
Judge Plugin's underlying model shares blind spots with the system it will assess,
remains a Contract-time and Risk Analysis judgment (Chapter 5), not something this Volume
can verify by running the plugin in isolation.

## Dataset Plugins

A Dataset Plugin extends Volume IV's Dataset Engine with a new source, or a new
coverage-shaping mechanism, beyond the eight this specification names. It inherits
Volume IV's Versioning requirement without exception — every Dataset a plugin produces
MUST be versioned, the same as one from a built-in source — and, where the plugin
generates or mutates rows using another AI model, the same SHOULD-level Independent
Oracles reasoning Volume IV already applies to Generated and Adversarial
Datasets applies to it too, for the same correlated-blind-spot reason.

## Report Plugins

A Report Plugin extends Volume XI's Reporting & Analytics with a new Metric type,
visualization, or Report format. It inherits the same auditability requirement Volume
XI's KPI section already states for any summary: a Metric a Report Plugin introduces
MUST be traceable back to the Results it was computed from, the same way a KPI MUST be —
a Report Plugin that presents an opaque score with no path back to underlying Results
would be exactly the unauditable summary Chapter 3's Contracts over Assertions already
rules out, regardless of how the plugin computed it.

## Plugin Invocation

How an implementation hosts a plugin — in its own process, as a separate process, as a
remote service — is its own choice, and so is the transport between them. Portability
of a plugin from one AQEF implementation to another is not a goal of this specification.
What every implementation MUST hold to is the logical shape of one assessment:

- **Input.** The plugin receives the target Evidence its clause names (the
  Conversation, Artifacts, or both — Volume II), the clause's own content (a
  Constraint's `expected`, an Expectation's `criteria`), its own versioned configuration,
  and the identifiers of the Execution and clause it is assessing. A Validator Plugin
  receives nothing else (Volume V — Validator SDK).
- **Output.** A Result for exactly that Execution and clause, in the shape Appendix C
  §C.7 specifies, with `oracle` naming the plugin and its version. The implementation
  validates the Result before recording it.
- **Failure.** A plugin that crashes, times out, or returns a Result that fails
  validation has assessed nothing: the recorded Result is `oracle_unavailable`, never
  `fail`. A broken check is not evidence about the subject.
- **Scope.** While assessing, a plugin changes nothing in AQEF other than the Result it
  returns.

A Dataset or Report Plugin follows the same pattern for its own output: a versioned
Dataset (Volume IV), or a Metric traceable to the Results it was computed from (Volume
XI).

## Authentication

A plugin authenticates against AQEF the same way any other caller of the REST API does
(Volume XIV) — there is no separate, plugin-specific authorization system, only the same
Permissions a Team and Role already grant (Volume XII) applied to whatever Principal the
plugin runs under — ordinarily a Service Account with an owning Person (Volume XII —
Principals). A plugin never approves a governed action. A plugin's own code MAY be trusted by whoever installed it, but that
trust does not extend its Permissions beyond what Governance has actually granted the
account it authenticates as; a plugin requesting an action its account's Role does not
permit fails the same Approval Workflow check any other caller would.

## Extension Lifecycle

Extension Lifecycle governs how a plugin moves from installation to retirement:
installation, registration — including the repeatability check Validator Plugins
above require — versioning, update, and deprecation. A plugin's own version is tracked
the same way a Dataset's or a Reusable Contract's is (Volume IV, Volume VII), for the
same reason: so a specific Execution's Result can be traced back to the exact plugin
version that produced or assessed it, not just the plugin's name. Deprecating a plugin
MUST NOT silently invalidate Baselines or Results a retired version already produced;
those remain valid historical evidence even after the plugin that produced them is no
longer installed, the same way a Dataset's older versions remain part of its history
rather than being erased when a newer version is captured. This is one instance of a
principle Appendix C §C.8 states generally for every destructive operation this
specification exposes, not a rule specific to plugins.

---

With Volume XVI, everything this specification has enumerated by name — Validators,
Judges, Datasets, Reports — is extensible without a Project needing to fork AQEF itself,
and every extension point inherits the same constraints its built-in counterpart already
carries, mechanically where that's possible and by Contract-time judgment where it
isn't. Volume XVII (Reference Implementations) closes the document: it specifies the
Minimal Engine and Enterprise Engine shapes Chapter 4 already distinguished, and how the
seventeen Volumes and eleven Appendices this specification comprises actually come together
as running software.
