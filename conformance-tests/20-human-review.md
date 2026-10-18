# 20. Capability: Human Review

Tests in this section apply to an implementation whose Conformance Statement claims
`human_review` (§10). For any other, they are `NOT_APPLICABLE`. CT-DEC-010 to CT-DEC-012
and CT-REL-025 also belong to this capability.

**F-HR.** As F-BASE with `semantic-gate` (Section 13.1), with the Expectation bound to a
Human Reviewer instead of the Judge:

```yaml
expectations:
  - criteria: "The response greets the user."
    human_reviewer:
      role: reviewer
```

`P-REVIEWER` (Section 14.1) holds the Role `reviewer`. `P-REVIEWER-2` is a Person who
holds `review` but only a Role named `qa`.

### CT-HRV-001 — A Human-Reviewer-bound Expectation names the Role that resolves it

- **Capability:** `human_review`
- **Requirement:** Appendix A §A.5, HumanReviewerConfig `role`: required; "Role a
  reviewer MUST hold to resolve this Expectation."
- **Method:** Automated
- **Fixture:** F-HR with `role` removed.
- **Action:** Load the configuration.
- **Expected:** Rejected.
- **Fails if:** Loaded.

### CT-HRV-002 — Only a reviewer holding the named Role resolves the Expectation

- **Capability:** `human_review`
- **Requirement:** Appendix A §A.5: the Role "a reviewer MUST hold to resolve this
  Expectation"; Appendix C §C.3, review: the Principal "MUST be a Person holding
  `review` and, where the clause names a `human_reviewer.role` ..., that Role."
- **Method:** Automated
- **Fixture:** F-HR.
- **Action:** Execute `cts-suite`. Review the pending Result with verdict `pass` as
  `P-REVIEWER-2`; retrieve the Result. Then review it with verdict `pass` as
  `P-REVIEWER`; retrieve it again, and evaluate the Gates.
- **Expected:** `P-REVIEWER-2`'s review is rejected with an error, and the Result is
  unchanged: `disposition: awaiting_review`, `verdict: null`, and no second Result for
  the Expectation. `P-REVIEWER`'s review is accepted and completes the same Result: the
  same `id`, `verdict: pass`, `disposition: actionable`, and `supporting_evidence`
  naming `P-REVIEWER` as the reviewing Person. `semantic-gate` passes.
- **Fails if:** `P-REVIEWER-2`'s review is accepted or changes the Result; a second
  Result is recorded for the Expectation; `P-REVIEWER`'s review is rejected or leaves the
  Result `awaiting_review`; the completed Result names `P-REVIEWER-2`, or no reviewer;
  or `semantic-gate` fails.

### CT-HRV-003 — A review that times out never becomes a pass

- **Capability:** `human_review`
- **Requirement:** Volume VI, Human Review: awaiting review "MUST NOT persist
  indefinitely ... after which the Contract's `on_timeout` policy applies"; Appendix A
  §A.5, `on_timeout`: "Default: `block` — an unresolved review is never silently treated
  as a pass."
- **Method:** Automated
- **Fixture:** F-HR, with `review_timeout` set to the shortest duration the
  implementation accepts and no `on_timeout`.
- **Action:** Execute `cts-suite`. Wait until `review_timeout` has passed; do not review.
  Evaluate the Gates.
- **Expected:** The Result has no verdict and is not `actionable`, and `semantic-gate`
  fails with `non_actionable_results`. The implementation's records show that the
  timeout was reached and `block` applied.
- **Fails if:** The Result gains a verdict without a review, `semantic-gate` passes, or
  nothing records that the timeout was reached.

### CT-HRV-004 — A reviewer's Confidence, where captured, is held to the threshold

- **Capability:** `human_review`
- **Requirement:** Volume I, Chapter 6, Confidence Model: below the threshold, "a
  Result's disposition is `inconclusive` — it MUST NOT be silently counted as an
  ordinary pass or fail"; Appendix A §A.5, `confidence_threshold` and
  `captures_confidence`; Appendix C §C.7, `confidence`.
- **Method:** Automated
- **Fixture:** Two variants of F-HR. (a) `captures_confidence: true` and
  `confidence_threshold: 0.8`. (b) `captures_confidence: false` and no threshold.
- **Action:** For (a), execute and review with verdict `pass` and Confidence `0.6`. For
  (b), execute and review with verdict `pass`.
- **Expected:** (a) The Result has `confidence: 0.6` and `disposition: inconclusive`.
  (b) The Result has `confidence: "not_applicable"` and `disposition: actionable`.
- **Fails if:** (a) is `actionable`, or (b) has a numeric Confidence or is not
  `actionable`.

### CT-HRV-005 — An escalated review passes to the named Role and never decides itself

- **Capability:** `human_review`
- **Requirement:** Volume VI, Human Review: "`escalate` passes the review to the Role
  named in `escalate_to`, and the Result stays `awaiting_review` until a reviewer holding
  that Role returns a verdict. Neither policy ever produces a verdict by itself";
  Appendix C §C.3, review: "or the `escalate_to` Role once the review has been
  escalated."
- **Method:** Automated
- **Fixture:** F-HR with `review_timeout` set to the shortest duration the implementation
  accepts, `on_timeout: escalate`, and `escalate_to: lead`. `P-LEAD` is a Person holding
  `review` and only the Role `lead`.
- **Action:** Execute `cts-suite`. Before the timeout, attempt the review as `P-LEAD`.
  Wait until the timeout has passed; evaluate the Gates. Review with verdict `pass` as
  `P-LEAD`; evaluate the Gates again.
- **Expected:** The review before the timeout is rejected. After the timeout, the Result
  is still `awaiting_review`, with no verdict, and `semantic-gate` fails with
  `non_actionable_results`. `P-LEAD`'s review is then accepted, and `semantic-gate`
  passes.
- **Fails if:** `P-LEAD` can review before escalation; the Result gains a verdict without
  a review; or `P-LEAD`'s review after escalation is rejected.

### CT-HRV-006 — `escalate_to` appears exactly when escalation is configured

- **Capability:** `human_review`
- **Requirement:** Appendix A §A.5, `escalate_to`: "MUST (if `on_timeout` is
  `escalate`)" and "MUST NOT appear otherwise"; Appendix B §B.2, Expectation.
- **Method:** Automated
- **Fixture:** Two variants of F-HR. (a) `on_timeout: escalate` with no `escalate_to`.
  (b) `on_timeout: block` with `escalate_to: lead`.
- **Action:** Load each variant.
- **Expected:** Both rejected.
- **Fails if:** Either is loaded.

