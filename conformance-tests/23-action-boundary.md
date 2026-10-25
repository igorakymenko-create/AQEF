# 23. Capability: Action Boundary

Tests in this section apply to an implementation whose Conformance Statement claims
`action_boundary` (§10): it runs subjects that act through tools. For any other, they are
`NOT_APPLICABLE`.

**F-ACT.** As F-BASE, with an Environment that gives the subject one tool and declares
an enforced boundary:

```yaml
project:
  environments:
    - name: cts-env-act
      model_version: cts-scripted-subject@1
      prompt_version: cts-prompt@1
      infra_target: cts-harness
      tool_configuration:
        tools:
          - name: http_get
            parameters: { url: { type: string } }
      action_boundary:
        enforced: true
        entries:
          - target: "https://cts-stub.example/*"
            kind: stub
          - target: "https://cts-trip.example/*"
            kind: stub
            tripwire: true
```

The patterns in `target` are written here as globs. The tester writes them in the
implementation's documented pattern syntax (CT-ABD-008), so that each matches the same
URLs as its glob.

And, in `s-greeting`'s Contract, a Boundary Validator bound as a hard veto:

```yaml
constraints:
  - validator: boundary
    target: artifacts.boundary_attempts
    expected: { attempts: 0, tripwire_touches: 0 }
    veto: true
```

(`artifacts.boundary_attempts` follows Appendix H §H.11; the tester substitutes the
implementation's documented path.) `https://cts-outside.example/` is a real endpoint the
tester controls and monitors; it is not in the boundary.

**Further scripted subject behavior.**

| Code | Behavior |
|---|---|
| `SR-CALL(url)` | Requests the tool call `http_get` with argument `url`; after the tool's response, or its refusal, returns `"Done."`. |

### CT-ABD-001 — A subject with tools needs a declared boundary

- **Capability:** `action_boundary`
- **Requirement:** Volume III, Action Boundary: "An Environment whose
  `tool_configuration` is not null MUST therefore declare an Action Boundary"; Appendix
  B §B.3, Action Boundary presence.
- **Method:** Automated
- **Fixture:** F-ACT with `action_boundary` removed.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded, or loaded with a boundary supplied silently.

### CT-ABD-002 — Tools and boundary entries have the required shape

- **Capability:** `action_boundary`
- **Requirement:** Appendix A §A.2: ToolDef `name` and `parameters`, ActionBoundary
  `enforced` and `entries`, BoundaryEntry `target` and `kind` are required; Appendix B
  §B.2: "`tripwire: true` is valid only when `kind` is `stub`."
- **Method:** Automated
- **Fixture:** Six variants of F-ACT, each with one change: (a) tool `name` removed;
  (b) tool `parameters` removed; (c) `enforced` removed; (d) `entries` removed;
  (e) the first entry's `kind` removed; (f) the first entry changed to `kind: sandbox`
  with `tripwire: true`.
- **Action:** Load each variant.
- **Expected:** All six rejected.
- **Fails if:** Any is loaded.

### CT-ABD-003 — A call outside the boundary is blocked, recorded, and fails the Execution

- **Capability:** `action_boundary`
- **Requirement:** Volume III, Action Boundary: "Where the harness controls the
  subject's access, everything outside the boundary MUST be denied by default"; Volume
  III, Artifact Collection: it "MUST capture every attempt the subject makes to reach
  outside it ... whether or not the attempt was blocked"; Appendix B §B.3, Boundary
  attempt capture: such attempts "MUST fail a bound Boundary Validator."
- **Method:** Automated, Harness
- **Fixture:** F-ACT, run against `cts-env-act`; scripted subject
  `SR-CALL("https://cts-outside.example/x")`.
- **Action:** Execute `cts-suite`; retrieve the Artifacts and Results; read the log of
  `cts-outside.example`.
- **Expected:** `cts-outside.example` receives no request. An Artifact records the
  attempt, its target, and that it was blocked. The Boundary Validator's Result is
  `fail`, and the scripted Judge receives no call.
- **Fails if:** The request reaches `cts-outside.example`; the attempt is not recorded;
  or the Boundary Validator passes.

### CT-ABD-004 — Touching a Tripwire is recorded and fails the Execution

- **Capability:** `action_boundary`
- **Requirement:** as CT-ABD-003, for "every touch of a Tripwire."
- **Method:** Automated, Harness
- **Fixture:** F-ACT; scripted subject `SR-CALL("https://cts-trip.example/login")`.
- **Action:** Execute `cts-suite`; retrieve the Artifacts and Results.
- **Expected:** An Artifact records the Tripwire touch and its target. The Boundary
  Validator's Result is `fail`.
- **Fails if:** The touch is not recorded, or the Boundary Validator passes.

### CT-ABD-005 — A call to a stub inside the boundary is allowed and has no effect beyond it

- **Capability:** `action_boundary`
- **Requirement:** Volume III, Action Boundary: a `stub` is "a stand-in that only
  records"; Appendix A §A.2, BoundaryEntry `kind`.
- **Method:** Automated, Harness
- **Fixture:** F-ACT; scripted subject `SR-CALL("https://cts-stub.example/x")`.
- **Action:** Execute `cts-suite`; retrieve the Artifacts and Results; read the log of
  `cts-outside.example`.
- **Expected:** The call is recorded as made to a stub, no boundary attempt is recorded,
  the Boundary Validator passes, and `cts-outside.example` receives nothing.
- **Fails if:** The stub call is recorded as a boundary attempt, the Boundary Validator
  fails, or anything reaches beyond the stub.

### CT-ABD-006 — An unenforced boundary is shown in every Report

- **Capability:** `action_boundary`
- **Requirement:** Appendix A §A.2, `enforced`: "A `false` boundary MUST be surfaced in
  Reports (Volume XI)"; Appendix B §B.3, Unenforced boundary reporting; Appendix C §C.10,
  `signals`.
- **Method:** Automated
- **Fixture:** F-ACT with `enforced: false`; scripted subject
  `SR-CALL("https://cts-trip.example/login")`.
- **Action:** Execute `cts-suite`; evaluate the Gates; retrieve the Report produced for
  the batch.
- **Expected:** `signals.unenforced_boundaries` lists `cts-env-act`, and
  `signals.boundary_attempts` lists the Tripwire touch with its target.
- **Fails if:** Either is missing from the Report.

### CT-ABD-007 — A boundary the harness cannot enforce is declared unenforced

- **Capability:** `action_boundary`
- **Requirement:** Volume III, Action Boundary: where the harness cannot control the
  subject's access, "the Environment MUST declare the boundary `enforced: false`."
- **Method:** Declaration
- **Fixture:** None.
- **Action:** Ask the implementation to state, for each kind of subject or platform it
  can run, whether its harness controls the subject's access, and what it does with an
  Environment that declares `enforced: true` for a subject whose access it does not
  control.
- **Expected:** Where it does not control access, it rejects or flags
  `enforced: true`, and never presents such a boundary as enforced.
- **Fails if:** The statement admits presenting an uncontrolled boundary as enforced.

### CT-TTP-002 — An agent's Baseline comparison judges the trajectory as a whole

- **Capability:** `action_boundary`
- **Requirement:** Volume I, Chapter 7, AI Agent: a Baseline comparison "MUST therefore
  be capable of judging the outcome and the reasoning quality of a trajectory as a
  whole, not require step-for-step identity with the Baseline's own path."
- **Method:** Automated, Inspection
- **Fixture:** F-ACT (Section 23) with a second stub entry `https://cts-stub2.example/*`
  and a Regression Gate as in CT-TTP-001. Two scripted trajectories reaching the same
  final Response, `"Done."`: (a) calls `cts-stub.example`, then `cts-stub2.example`;
  (b) the same two calls in the opposite order.
- **Action:** Execute with trajectory (a); designate it as a Baseline. Execute with
  trajectory (b); evaluate the Gates. Review how the comparison was made.
- **Expected:** The comparison does not report a regression because the order of steps
  differs; the reviewer records what the comparison judged.
- **Fails if:** A regression is reported solely because (b)'s steps are not identical
  to (a)'s.

### CT-ABD-008 — The implementation documents its boundary pattern syntax

- **Capability:** `action_boundary`
- **Requirement:** Appendix A §A.2, BoundaryEntry `target`: "Pattern syntax is
  implementation-defined and MUST be documented by the implementation; matching is
  deterministic."
- **Method:** Declaration, Automated
- **Fixture:** F-ACT.
- **Action:** Obtain the implementation's documentation of its pattern syntax. With
  scripted subject `SR-CALL(url)`, execute once with `url` set to each of
  `https://cts-stub.example/a`, which matches `cts-stub.example`'s pattern, and
  `https://cts-stub.example.evil/a`, which does not.
- **Expected:** The documentation states the syntax and how a `target` matches. The
  first call is allowed; the second is denied as outside the boundary, as the
  documentation predicts.
- **Fails if:** No syntax is documented; or an outcome contradicts the documentation.
