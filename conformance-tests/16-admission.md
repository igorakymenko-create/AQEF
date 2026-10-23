# 16. Admission of Judges

Tests in this section check Admission (Volume VI; Appendix C §C.3, Admission): the
record of a Judge configuration's agreement with a Reference Set, and its effect on
Quality Gates and Reports. Admission is not a scoped capability in §10, so these tests
are core, except where a test names another capability. Section 13.1 applies here:
"evaluate the Gates" and `semantic-gate` have its meanings. The Principals are those of
Section 14.1.

## 16.1 Fixtures

**Recording an Admission.** "Record `ADM-PASS`" means `POST
/projects/cts-base/admissions` (Appendix C §C.3) with the body below, made by
`P-REVIEWER` unless the test says otherwise. "The Admission records" are what `GET
/projects/cts-base/admissions` returns.

**`ORACLE-1`.** The `oracle` value (Appendix C §C.7) on the Result of `s-greeting`'s
Expectation in a setup Execution of the test's fixture. Every Admission request below
names it, unless the test says otherwise. Setup check: the Result carries an `oracle`.

**`ADM-PASS`.** An Admission request that meets its threshold:

```yaml
oracle: ORACLE-1
reference_set: cts-greetings@1
items: 20
verdict_distribution: { pass: 14, fail: 6 }
raw_agreement: 0.90
measure: cohen_kappa
chance_corrected_agreement: 0.76
threshold: 0.70
admitted: true
labelled_by: [cts-labeller-1, cts-labeller-2]
```

**`ADM-FAIL`.** As `ADM-PASS`, with `raw_agreement: 0.80`,
`chance_corrected_agreement: 0.52`, and `admitted: false`.

**`SA-REVIEW`.** A Service Account owned by `P-REVIEWER`, holding `read` and `review`.

**`gate-admitted`.** `semantic-gate` with `require_admitted_judges: true` added.

## 16.2 Tests

### CT-ADM-001 — A Person records an Admission, and the implementation sets its identity

- **Capability:** core
- **Requirement:** Appendix C §C.3, `POST /projects/{project}/admissions`: "The
  Principal MUST be a Person"; "The implementation sets `id`, `recorded_at`, and
  `recorded_by`"; Volume VI, Admission: "The record MUST state the Reference Set and its
  version, how many items were scored and how their correct verdicts were distributed,
  the raw agreement, and an agreement measure corrected for chance, by name and value."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`; `SA-REVIEW`.
- **Action:** Record `ADM-PASS` (a) as `SA-REVIEW`; (b) as `P-NOPERM`; (c) as
  `P-REVIEWER`. Retrieve the Admission records as `P-NOPERM`.
- **Expected:** (a) rejected: a Service Account, though it holds `review`. (b) rejected:
  `P-NOPERM` lacks `review`. (c) accepted. The records hold exactly one record, with
  every field of `ADM-PASS` as sent, and with `id`, `recorded_at`, and `recorded_by`
  set by the implementation, `recorded_by` naming `P-REVIEWER`.
- **Fails if:** (a) or (b) is accepted or leaves a record; any field differs from the
  request; or `id`, `recorded_at`, or `recorded_by` is missing.

### CT-ADM-002 — An incomplete or inconsistent Admission record is rejected

- **Capability:** core
- **Requirement:** Appendix C §C.3, Admission: "a request that supplies any of them
  [`id`, `recorded_at`, `recorded_by`] MUST be rejected. Every other field is required
  except `arbitrations`. ... `labelled_by` names at least one reviewer. `items` is at
  least 1, the counts in `verdict_distribution` are not negative and add up to `items`,
  and `raw_agreement` lies between 0 and 1. `chance_corrected_agreement` is a number or
  `"not_computed"`, never `null` ... A request that breaks any of these MUST be
  rejected."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`.
- **Action:** Record each variant of `ADM-PASS`, in a fresh Project each:
  - Rejected variants: (a) to (j) each omit one of `oracle`, `reference_set`, `items`,
    `verdict_distribution`, `raw_agreement`, `measure`, `chance_corrected_agreement`,
    `threshold`, `admitted`, `labelled_by`; (k) `labelled_by: []`; (l) `items: 0` with `verdict_distribution: {}`;
    (m) `verdict_distribution: { pass: 15, fail: 6 }`, which adds up to 21;
    (n) `verdict_distribution: { pass: 21, fail: -1 }`, which adds up to 20;
    (o) `raw_agreement: 1.2`; (p) `raw_agreement: -0.1`;
    (q) `chance_corrected_agreement: null`; (r) `id: adm-1` added;
    (s) `recorded_at: 2030-01-01T00:00:00Z` added; (t) `recorded_by: P-REVIEWER` added.
  - Accepted variants: (u) `ADM-PASS` unchanged, which has no `arbitrations`;
    (v) `arbitrations: []` added.
  - After each, retrieve the Admission records.
- **Expected:** (a) to (t) rejected, each leaving no record. (u) and (v) accepted, each
  leaving one record; (u)'s has no `arbitrations` and (v)'s has an empty one.
- **Fails if:** Any of (a) to (t) is accepted or leaves a record; (u) or (v) is
  rejected; or (u)'s record shows an empty `arbitrations`, or (v)'s none.

### CT-ADM-003 — `admitted` agrees with the threshold, on the chance-corrected value

- **Capability:** core
- **Requirement:** Appendix C §C.3, `POST /projects/{project}/admissions`: "MUST be
  rejected if `admitted` is `true` while `chance_corrected_agreement` is below
  `threshold`, or `false` while it meets it"; Admission: "where it is `"not_computed"`,
  `admitted` is `false`. A value meets `threshold` when it is equal to it or above it."
- **Method:** Automated
- **Fixture:** F-BASE with `semantic-gate`.
- **Action:** Record each variant of `ADM-PASS`, in a fresh Project each:
  (a) `chance_corrected_agreement: 0.70`, `admitted: true`;
  (b) `chance_corrected_agreement: 0.70`, `admitted: false`;
  (c) `chance_corrected_agreement: 0.69`, `admitted: false`;
  (d) `chance_corrected_agreement: 0.69`, `admitted: true`;
  (e) `raw_agreement: 0.95`, `chance_corrected_agreement: 0.40`, `admitted: true`;
  (f) `verdict_distribution: { pass: 20 }`, `raw_agreement: 1.0`,
  `chance_corrected_agreement: "not_computed"`, `admitted: false` (every item has one
  correct verdict, and the Judge gave it every time, so Cohen's kappa is undefined);
  (g) as (f) with `admitted: true`.
- **Expected:** (a), (c), and (f) accepted. (b), (d), (e), and (g) rejected, each leaving
  no record.
- **Fails if:** (a) is rejected (a value equal to the threshold meets it); (e) is
  accepted on its raw agreement; or any other variant has the other outcome.

### CT-ADM-004 — The most recent Admission record decides, at the Gate and in the Report

- **Capability:** core
- **Requirement:** Appendix B §B.3, Gate reasons: "A Gate declaring
  `require_admitted_judges` whose aggregate includes a Result from a Judge configuration
  that is not admitted MUST fail, with `judge_not_admitted`"; Admission record: "The most
  recent record for a Judge configuration, the one the implementation accepted last,
  decides whether it is admitted"; Appendix C §C.3: "a later record with `admitted:
  false` withdraws an earlier admission"; "An Admission record is never modified";
  Appendix C §C.10, `unadmitted_judges`.
- **Method:** Automated
- **Fixture:** F-BASE with `gate-admitted`; scripted Judge `J-PASS-90`. Setup: execute
  `cts-suite` and read `ORACLE-1` (16.1).
- **Action:** Each step is made only after the previous one has returned.
  - (a) Evaluate the Gates for the setup batch; retrieve a Report for the batch
    generated after the evaluation.
  - (b) Record `ADM-PASS`; evaluate the Gates; retrieve a Report.
  - (c) Record `ADM-FAIL`; evaluate the Gates; retrieve a Report.
  - (d) Record `ADM-PASS` again; evaluate the Gates; retrieve a Report.
  - (e) Retrieve the Admission records, and the GateResults of (a) to (c).
- **Expected:**
  - (a) `semantic-gate` fails with `judge_not_admitted`, with `basis.results: 0` and
    `basis.not_actionable: 1`; `functional-gate` passes; `signals.unadmitted_judges`
    lists `ORACLE-1`.
  - (b) `semantic-gate` passes; `unadmitted_judges` is empty.
  - (c) `semantic-gate` fails with `judge_not_admitted`; `unadmitted_judges` lists
    `ORACLE-1`.
  - (d) `semantic-gate` passes; `unadmitted_judges` is empty.
  - (e) Three records, each exactly as returned when it was recorded. The GateResults of
    (a) to (c) are recorded unchanged.
- **Fails if:** (c) passes, so that an earlier record with `admitted: true` outweighs a
  later one; (d) fails; a Report disagrees with the Gate on whether `ORACLE-1` is
  admitted; or any record or earlier GateResult was changed.

### CT-ADM-005 — A changed Judge configuration needs its own admission

- **Capability:** core
- **Requirement:** as CT-ADM-004; Volume VI, Admission: "Admission belongs to one Judge
  configuration ...: a changed model, prompt, or criteria is a different Judge and needs
  its own admission."
- **Method:** Automated
- **Fixture:** F-BASE with `gate-admitted`; scripted Judge `J-PASS-90`. Setup: execute
  `cts-suite`, read `ORACLE-1`, and record `ADM-PASS`.
- **Action:** As a governed change (14.1), set the Expectation's `judge.model` to
  `cts-scripted-judge@2`, which behaves as `J-PASS-90`. Execute `cts-suite` again; read
  the `oracle` on the new Result of the Expectation (`ORACLE-2`). Evaluate the Gates for
  the new batch; retrieve a Report for it.
- **Expected:** `ORACLE-2` differs from `ORACLE-1`. `semantic-gate` fails with
  `judge_not_admitted`. `signals.unadmitted_judges` lists `ORACLE-2`, and not
  `ORACLE-1`, whose Results are not in scope.
- **Fails if:** `ORACLE-2` equals `ORACLE-1`; or `semantic-gate` passes on `ORACLE-1`'s
  admission.

### CT-ADM-006 — A panel is admitted only when every Judge in it is

- **Capability:** `multi_judge`
- **Requirement:** as CT-ADM-004; Volume VI, Admission: "A Multi Judge panel is admitted
  when every Judge configuration in it is."
- **Method:** Automated
- **Fixture:** F-PANEL (Section 21), with `semantic-gate` given
  `require_admitted_judges: true`; all three Judges behave as `J-PASS-90`. A panel
  member with the same model and criteria configuration as a single Judge is the same
  Judge configuration (Appendix C §C.7, `oracle`), so each member's identifier is read
  from a single-Judge run. Setup, in the test's Project: bind `s-greeting`'s
  Expectation to `cts-scripted-judge-a@1` alone, with `confidence_source: self_rating`
  and the criteria and `confidence_threshold` of F-BASE; execute `cts-suite` and read
  the `oracle` on the Expectation's Result (`ORACLE-A`). Do the same for `-b` and `-c`
  (`ORACLE-B`, `ORACLE-C`), each bound as a governed change (14.1). Then bind the
  Expectation to F-PANEL's panel, as a governed change, and execute `cts-suite`; the
  Gates below are evaluated for this batch. Setup check: the three identifiers
  differ.
- **Action:** (a) Record `ADM-PASS` for `ORACLE-A` and for `ORACLE-B`; evaluate the
  Gates. (b) Record `ADM-PASS` for `ORACLE-C`; evaluate the Gates. (c) Record
  `ADM-FAIL` for `ORACLE-B`; evaluate the Gates.
- **Expected:** (a) `semantic-gate` fails with `judge_not_admitted`. (b) It passes.
  (c) It fails with `judge_not_admitted`.
- **Fails if:** (a) or (c) passes; or (b) fails.

### CT-ADM-007 — A Gate that lacks admitted Judges lists every other reason too

- **Capability:** core
- **Requirement:** Appendix B §B.3, Gate reasons: "A failed GateResult MUST list every
  applicable reason. ... A Gate declaring `require_admitted_judges` whose aggregate
  includes a Result from a Judge configuration that is not admitted MUST fail, with
  `judge_not_admitted`."
- **Method:** Automated
- **Fixture:** F-BASE with `gate-admitted`, given `min_basis: { results: 2 }`; scripted
  Judge `J-PASS-90`; no Admission record.
- **Action:** Execute `cts-suite`; evaluate the Gates.
- **Expected:** `semantic-gate` fails, and `reasons` contains both `judge_not_admitted`
  and `insufficient_basis`.
- **Fails if:** Either reason is missing.
