# Volume XIV — SDK & APIs

**Status:** confirmed (v0.1).

*Question answered:* How AQEF gets called, from anything other than itself.

Volume XIII's closing paragraph already named this Volume directly: every CI/CD
integration in Volume XIII invoked "the CLI or REST API surface Volume XIV specifies"
without that surface yet existing. This Volume specifies it: the REST API as AQEF's
single canonical surface, and the CLI and five language SDKs as clients built on top of
it, not independent implementations of AQEF's own logic — the same anti-drift reasoning
Volume VII's Contract Language already applied to YAML and JSON Schema (Appendix A, B),
extended here to every way a person or a system actually calls AQEF.

## REST API

The REST API is AQEF's single canonical programmatic surface: every operation this
specification has described — triggering an Execution, defining a Contract, approving a
Baseline, querying a Report, overriding a Quality Gate through Approval Workflow — is
expressed here first, as a resource or action a caller invokes directly. The concrete
endpoints, request and response schemas, and authentication model are specified in
Appendix C — REST API Specification, generated from the same Domain Model entities
(Volume II) and Contract Language (Volume VII) this Volume relies on, not authored
independently, for the same reason Appendix A and B already state for YAML and JSON
Schema. This section's role is narrower: establishing that the REST API is what every
other surface below is built from, not one option among equals.

## CLI

The CLI is a thin client over the REST API, packaged for shell and script use — the
surface Volume XIII's CI/CD integrations invoke directly, and the natural entry point
for a Pipeline step that has no need for a full language SDK. A CLI command MUST
correspond to a REST API call it makes on the caller's behalf, not a separate
implementation of the operation it names; a CLI capability with no REST API counterpart
behind it would be exactly the drift this principle rules out.

## Python SDK

A generated or thin-wrapper client over the REST API, idiomatic to Python — the SDK most
likely to sit inside a Dataset Engine (Volume IV) generation script, a notebook
exploring a Report's underlying Metrics, or a Custom Validator's own implementation
(Volume V) calling back into AQEF. Nothing about being Python-idiomatic — async support,
type hints, whatever the ecosystem expects — licenses it to expose an operation, or a
behavior, the REST API itself does not define.

## Java SDK

A generated or thin-wrapper client over the REST API, idiomatic to Java — the SDK most
likely to appear inside an enterprise Project's own JVM-based tooling, or a Custom
Validator or Judge plugin (Volume XVI) built for a JVM-hosted Environment. Same
constraint as every other SDK in this Volume: no operation or behavior beyond what the
REST API itself defines.

## C#

A generated or thin-wrapper client over the REST API, idiomatic to C# — the natural
counterpart to the Java SDK for a .NET-based enterprise Project's own tooling and
plugins, under the same constraint.

## JavaScript/TypeScript

A generated or thin-wrapper client over the REST API, idiomatic to JavaScript and
TypeScript — the SDK Volume XV's Reference UI is expected to be built on, since a
browser-based Dashboard (Volume XI) or Visual Test Designer (Volume XV) calls AQEF's
REST API from exactly this surface. Under the same constraint as every other SDK: the UI
layer consumes what the REST API defines, it does not extend AQEF's own logic
client-side.

## Go

A generated or thin-wrapper client over the REST API, idiomatic to Go — a natural fit
for infrastructure-facing tooling, including a Distributed Execution worker (Volume III)
or the CLI's own implementation, under the same constraint as every other SDK in this
Volume.

---

With Volume XIV, every surface Volumes XIII and XV rely on — a CI/CD Pipeline's CLI
step, a Reference UI's browser-based calls, a Custom Validator's own script — now has a
specified, single source of truth behind it: the REST API (Appendix C), not seven
independently maintained implementations of the same logic. Volume XV (Reference UI) is
next, and the last Volume in Part IV: it specifies the Visual Test Designer, Test
Explorer, Validator Designer, Judge Configuration, and Reporting UI this Volume's
JavaScript/TypeScript SDK is expected to be built on.
