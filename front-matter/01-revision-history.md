# 1. Revision History

**Status:** current through v0.31.

| Version | Date | Author | Summary |
|---|---|---|---|
| 0.1 | 2026-07 | Igor Akymenko | Initial Working Draft. All 17 Volumes and Appendices A–J drafted. |
| 0.1.1 | 2026-07 | Igor Akymenko | Minor fixes and formatting improvements to visual elements (diagrams, text flows) and PDF compilation logic. |
| 0.2 | 2026-07 | Igor Akymenko | Added Appendix K (Quick Start Guide). Removed all internal development references from published document. Version bump to 0.2. |
| 0.25 | 2026-08 | Igor Akymenko | Fix consistency issues found in v0.2 audit: Result schema, Human Reviewer binding, terminology cleanup. |
| 0.26 | 2026-08 | Igor Akymenko | Scope, Conformance, and Document Status extended to state non-goals explicitly: single authorship with no consensus claimed; testing process, roles, and organizational structure out of scope; Conformance not a property of a person, team, or process. |
| 0.27 | 2026-08 | Igor Akymenko | Clause-level weighting added to Contract Policies; Expectations required to be authored at one-clause-one-Result granularity; Judge Results over composite criteria required to declare aggregation. Arising from external review feedback. |
| 0.28 | 2026-09 | Igor Akymenko | Seeded Controls added (Volume VIII): Scenarios with planted, known defects that verify an Oracle can still detect a defect class in the current run; a missed Seeded Control makes that Oracle's Results in the run inconclusive and blocks Quality Gates on them. Arising from external practitioner feedback. |
| 0.29 | 2026-09 | Igor Akymenko | Seeded Controls refined: a missed control now invalidates only Results sharing its defect class by default, with full-run invalidation as an explicit, reasoned Project decision; authorship and rotation of Seeded Controls SHOULD be independent of whoever tunes the Oracle they test. Arising from external review feedback. |
| 0.30 | 2026-09 | Igor Akymenko | Seeded Controls given a machine-readable schema: `seeded_control` on Scenario (Appendix A/B), defect-class-scoped vs. full-run invalidation reporting and a difficulty prior in the REST API (Appendix C); a difficulty prior MUST distinguish "not yet established" from 0 and is anchored exclusively to Human Reviewer assessment, never to the tested Oracle's own history. |
| 0.30.1 | 2026-10 | Igor Akymenko | Editorial cleanup: per-file status lines removed (document version is stated only in Document Status and Revision History); appendix count corrected in Scope; internal drafting notes removed from Appendix E and the Master Index. No normative change. |
| 0.31 | 2026-10 | Igor Akymenko | Aggregate Basis added (Volume I, Chapter 6): every aggregate a Quality Gate reads states how many Results, Scenarios and Executions it rests on; a Gate may declare a minimum basis. Confidence explicitly distinguished from a statistical confidence level (§8, Appendix D). Schema and API updated (Appendix A, B, C). |
