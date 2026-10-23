# Harness Contract — audit decisions

How the Harness Contract answers the independent audit of the CTS. Parts A to E are
the decisions of version 0.3, on Stage A (Feasibility Audit of CTS Working Draft 6,
findings FEA-001 to FEA-008), Stage B (Harness Contract v0.1, its Technical Review with
findings HB-R01 to HB-R08 and engineering decisions HB-01 to HB-08, Harness Contract
v0.2, and the v0.2 JSON Schema package), and the Consolidated Decision Register of 18
October 2026. Part F holds the decisions of version 0.4, on the Contract Verification
Audit of version 0.3 (findings CV-01 to CV-06).

Every decision was checked against AQEF Working Draft 0.39 and the CTS. None of them
changes AQEF: the audit found no defect in it, and nothing here was changed in AQEF for
the harness's convenience.

**Accepted:** taken as proposed. **Modified:** the need is accepted, the solution
differs, for the reason given. **Rejected:** not taken, for the reason given. "§" refers
to `harness-contract.md`; "CTS" to the Conformance Test Specification.

## A. Stage A findings

| Finding | Decision | Reason | Where |
|---|---|---|---|
| FEA-001 · High · No portable adapter binding | Modified | Accepted as a blocker. v0.2's envelopes kept; the operation catalog extended to every operation the CTS uses (v0.2 lacked Baselines, Reports, Release Policies, deletion, pagination, unauthenticated requests); arguments typed for the 24 operations of slices S0 to S3; endpoint binding per session added, since correlation depends on it. Closure needs Stage C: three reference tests through an adapter. | §4, §5, §6, §8.2; `schemas/adapter-*.schema.json` |
| FEA-002 · Medium · No reproducible rubric for 21 Inspection and Declaration tests | Accepted | The checklist, evidence per item, named reviewer, and blind second review are now CTS 1.8; the record format is §13. | CTS 1.8; §13; `manual-review.schema.json` |
| FEA-003 · High · CT-ASM-014 `NOT_RUN` without a way to crash a Validator | Modified | The stage A wording, a "certified fault-injection profile", is not taken: the CTS certifies nothing, and AQEF §10 makes conformance a property of an implementation only. CT-ASM-014 may use a test plugin or a hook the SUT documents; without either it stays `NOT_RUN` and its requirement is reported unverified. No implementation is asked to offer a hook. | CTS CT-ASM-014 (WD7); §9.1 |
| FEA-004 · Medium · Unbounded, possibly flaky timing tests | Accepted | Waiting budgets and event-based waiting are in CTS 1.6; clocks and grace periods in §9.2. | CTS 1.6; §9.2 |
| FEA-005 · Medium · No portable way to request regeneration | Modified | CT-DSR-003 now names the operation. Where the implementation offers no regeneration, the outcome is `NOT_APPLICABLE`, not `NOT_RUN` as proposed: AQEF does not require regeneration, so its absence is an optional feature not offered (CTS 1.2), shown by a probe. | CTS CT-DSR-003 (WD7); §6; §16 |
| FEA-006 · Medium · Ten equal verdicts are not proof of determinism | Accepted | CT-PLG-005 calls them a sampled check; the report marks such evidence `sampled`. | CTS CT-PLG-005 (WD7); §14.4 |
| FEA-007 · Medium · CLI, CI/CD, UI evidence not standardized | Accepted | Minimum evidence per capability adapter; details per platform in Stage C. | §16 |
| FEA-008 · Low · Static review is not execution | Accepted | A limitation, not a defect. Stage C separates mock runs from runs against an implementation, and a mock report says what it is. | §15; `stage-c-readiness.md` |

## B. Stage B Technical Review findings

| Finding | Decision | Reason | Where |
|---|---|---|---|
| HB-R01 · High · Payloads illustrative, not typed | Modified | v0.2's envelope schemas kept. Added: shared definitions; typed arguments for 24 operations; `operation` echoed in the response so that a successful SUT operation can be required to carry the SUT's outcome. Arguments of the other 32 operations remain a Stage C profile (Q-01): typing them before an adapter exists would fix guesses. | §5; `adapter-operation.schema.json`; `adapter-response.schema.json` |
| HB-R02 · High · Harness failure not distinguishable from SUT failure | Modified | v0.2's `origin` and `phase` kept. v0.2 left open whether an SUT rejection is an error; 0.3 makes it an outcome (`data.sut.outcome: rejected`), since many tests expect one. A complete attribution table decides every case: an SUT server error in the action phase is `FAIL`; a network failure or timeout without response is `NOT_RUN`; any setup error is `NOT_RUN` (CTS 1.6). | §5.3, §5.4, §7 |
| HB-R03 · High · No completeness barrier for negative call assertions | Modified | v0.2's lifecycle, watermark, and drain kept. Added: correlation depends on session-scoped endpoints, and without them cases run one at a time with `CORRELATION_UNCERTAIN` as fallback; a late call before the report is finalized turns a decided absence into `FAIL`. | §8.2, §11 |
| HB-R04 · Medium · No separate raw and redacted digests | Modified | v0.2's digests kept. v0.2 referred to an evidence manifest but defined none: `evidence-manifest.schema.json` added, with RFC 8785 canonicalization and a verification rule. v0.2 required a raw digest on every event, which a reset or watermark event has no payload for: now required only for events that carry a payload. | §12; `evidence-manifest.schema.json`; `harness-event.schema.json` |
| HB-R05 · Medium · Reset, switch, and clock ownership informal | Accepted | Reset and switch are atomic and per session; a switch answers from the next request; counters per endpoint and session; every reading names its clock (`clock_id` added). | §8.3, §9.2 |
| HB-R06 · Medium · Manual review lacks finality | Modified | v0.2's signed record kept. v0.2's schema dropped v0.1's per-item checklist; restored, since CTS 1.8 decides from it. Added: blind second review, a reviewer not affiliated with the implementation for disputes it raises, and no deadline that turns a pending review into a decision. The schema rejects a `PASS` with an undecided item. | CTS 1.8; §13; `manual-review.schema.json` |
| HB-R07 · Medium · An "unsupported" flag is not proof the SUT lacks an operation | Accepted | Probe evidence required; an adapter gap is `NOT_RUN`; a missing required operation is `FAIL` only on a probe. | §6; §7 rows 6, 7 |
| HB-R08 · Medium · Requirement coverage not derivable | Modified | v0.2's algebra adopted, with three corrections: requirements are traced to cases where Section 90 does so (v0.2's schema allowed only test IDs, which would lose CT-CFG-025's trace); a traced case missing from the run counts as `NOT_RUN`; Restates rows inherit their source row's state. CTS 1.7 is aligned to this algebra. | §14; CTS 1.7; `cts-report.schema.json` |

## C. Engineering decisions HB-01 to HB-08

| Decision | Disposition | Reason |
|---|---|---|
| HB-01 Transport | Modified | HTTPS with JSON envelopes. The review's "byte-for-byte" equivalence for in-process bindings is rejected: key order and whitespace carry no meaning; equality of the parsed, schema-valid JSON is required instead (§4). |
| HB-02 Time | Accepted | Monotonic clocks per `clock_id`; a virtual clock only for the harness's own timers (§9.2). |
| HB-03 Fixtures | Accepted | Recipes for all eight postcondition fixtures of CTS 2.7, checked against it by `tools/validate.py` (§10). |
| HB-04 Evidence | Accepted | Raw and redacted digests, manifest (§12). |
| HB-05 Manual review | Accepted | §13. |
| HB-06 Faults | Accepted | Optional, with the mechanism stated per profile (§9.1). |
| HB-07 Reports | Accepted | JSON Schema 2020-12, with the algebra recomputed by the validator (§14, §15). |
| HB-08 Adapters | Accepted | Appendix C REST first; an equivalent surface only with equivalence evidence (§6). |

## D. Version 0.1 against version 0.2

v0.2 was not taken over automatically. Each change it made to v0.1, and what v0.2
left out:

| Topic | v0.1 | v0.2 | 0.3 | Reason |
|---|---|---|---|---|
| Status and precedence | Not part of AQEF | Same, stated more strongly | Kept; normative words bind the harness only | Both right. |
| Envelope | Illustrative JSON | Schema, with session, correlation, timeout | v0.2 kept and extended | HB-R01. |
| Operation result | Six statuses, incl. `rejected_by_sut` | `success` plus typed error; rejection's place unclear | `success` plus error; rejection is `data.sut.outcome` | v0.1 was right that a rejection is not a failure; v0.2's envelope is cleaner. |
| Error vocabulary | Eight codes with handling (Appendix A) | Free-form `code` | v0.1's codes restored as an enum, plus reason codes for outcomes | A free code cannot drive §7. |
| Manifest and Conformance Statement | `conformance_statement_ref`; warns the manifest is not the Statement | `capabilities_claimed` in the manifest | v0.2's `capabilities_claimed` rejected; v0.1's reference restored | Claims belong to the Statement (AQEF §10); copying them into a test-side file invites drift. |
| Operation catalog | Groups, partly named | 36 operations | 56 operations, each mapped to Appendix C and to the tests using it | v0.2 missed operations the CTS uses. |
| Observation lifecycle | Principle only | States, watermark, drain | Kept; correlation and late calls added | HB-R03. |
| Evidence | Event with hash | Raw and redacted digests | Kept; manifest schema added | HB-R04. |
| Manual review | Checklist, per-test notes | Signed record, no checklist | Both: v0.1's checklist and notes restored | CTS 1.8 decides from the checklist. |
| Aggregation | Test level only | Test and requirement algebra | v0.2 kept, three corrections | HB-R08. |
| Behavior registry, fault table, security, slices, Stage C exit | Present | Dropped | Restored (§8.1, §9.1, §17; `stage-c-readiness.md`) | Still needed; v0.2 did not say they were replaced. |
| Invariants | — | I-01 to I-10 | I-01 to I-13 | Added: rejection as outcome, empty-review rule, recipes agree with the CTS. |
| `case_id` pattern | — | `CT-[A-Z]+-nnn(.nn)` | `CT-[A-Z]{3}-nnn(.nn)` | Every CTS area code has three letters. |
| Event digest | One hash | Raw digest required on every event | Required only where an event carries a payload | A reset or watermark has no payload. |
| Report provenance | AQEF, CTS, adapter, harness | SUT and adapter IDs only | v0.1's provenance restored, plus contract version and drain time | Replayability (§3). |
| Schema `$id` | — | `https://alternateqa.com/cts-harness/v0.2/...` | Identifiers under the AQEF repository | An open specification's artifacts should not be identified by a vendor's domain; identifiers need not resolve. Open for decision (Q-06). |

## E. Changes outside the harness

To the CTS only (Working Draft 7):

- 1.4: the Harness Contract is named as the specification of the harness.
- 1.6: sessions and observation closure refer to the contract.
- 1.7: requirement states follow the algebra of §14.3, and the report format is the
  contract's.
- 1.8: the review record is the contract's.
- 2.7 and 2.8: recipes and the self-test operation.
- 0.5, 0.6, README: the `harness/` folder.

To AQEF: none.

## F. Contract Verification Audit of version 0.3

The audit was a static reading of the repository on 19 October 2026; it did not run the
validator. Each finding was checked against the code and confirmed.

| Finding | Decision | Reason | Where |
|---|---|---|---|
| CV-01 · P1 · Report completeness and uniqueness not verified | Accepted | Confirmed: results were keyed by case ID, so a duplicate overwrote silently, and a consistent subset of a run validated. The report now carries its `plan` (full or partial); the validator compares the report with the CTS it names: every planned case and test exactly once, each test with the CTS's case list, every requirement with Section 90's trace, case-to-test bindings, the CTS revision. The example report is now complete: 29 cases, 5 tests, 395 requirements. Missing and duplicate entries are among the unit tests. | §15 Completeness; I-14; `cts-report.schema.json` `plan`; `tools/validate.py` `check_report` |
| CV-02 · P1 · RFC 8785 claimed, not implemented | Accepted | Confirmed: keys were sorted by code point, not by UTF-16 code units, and numbers were not formatted as ECMAScript does. The validator now implements RFC 8785 as published, refuses what it cannot canonicalize (integers beyond ±2^53, NaN, infinities), and checks itself on every run against the examples of RFC 8785 §3.2.2 and §3.2.3 and edge cases, including the audit's U+E000 against U+1F600. Restricting the identifier to a custom form was not chosen: an independent verifier should be able to use any RFC 8785 implementation. | §12 Canonicalization; I-16; `jcs`, `JCS_VECTORS` |
| CV-03 · P1 · Evidence bytes not checked | Accepted | Confirmed: only the manifest's own digest was recomputed. The validator now resolves every raw and redacted object, compares digests and size, checks that every evidence reference of the report is in the manifest, refuses references outside the store, and fails closed on a missing object. `--report` cannot be run without the evidence. The example report has real evidence objects; unit tests change a byte, truncate, remove, and misstate. Whether a real store's resolver does the same is a Stage C exit criterion. | §12 Verification; I-08, I-17; `check_manifest`; `examples/evidence/` |
| CV-04 · P2 · Setup checks not machine-verifiable | Accepted, deferred | Already open as Q-03. The machine form needs the field paths of Q-02, which do not exist before an adapter; writing them now would fix guesses. The audit's closure criterion is taken into Q-03, before any postcondition fixture is automated. | `stage-c-readiness.md` Q-03 |
| CV-05 · P2 · 32 operations untyped | Accepted, deferred | Declared scope of 0.3, as the audit notes. The closure criterion is taken into Q-01: a profile, examples, and a contract test before the first test that uses each operation. | `stage-c-readiness.md` Q-01 |
| CV-06 · P2 · No negative cases for critical report shapes | Accepted | `tools/test_validate.py`: 49 unit tests, every static check on a valid case and on cases built to break it: duplicates, omissions, wrong traces and states, capability against the Conformance Statement, revision, evidence closure, tampering, canonicalization, recipes. A CI workflow runs the validator and the tests on every change to `conformance-tests/`. The two report examples in `examples/invalid/` were replaced by these tests, which build each broken report from the complete valid one. | `tools/test_validate.py`; `.github/workflows/cts-harness.yml`; I-14 to I-17 |

The audit's next steps 1, 2, and 5 are now entry and exit criteria in
`stage-c-readiness.md`: CI on the published commit with its SHA and output recorded,
evidence verified on a real store, and every report run from an immutable checkout
whose commit it records.

To AQEF and to the CTS: no change.

