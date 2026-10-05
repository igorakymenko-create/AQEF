# AQEF — AI Quality Engineering Framework
### Master Index (Working Draft v0.31)

Legend: ✅ drafted & confirmed · 🟨 partially drafted · ⬜ not yet drafted

Structure: one file per Front Matter section / Volume / Appendix, so any future edit
touches a single small file rather than the whole document. Working, non-reader-facing
notes live in `_project-notes/` (currently: `decisions-log.md`).

---

## Front Matter

- ✅ [0. Document Status](front-matter/00-document-status.md)
- ✅ [1. Revision History](front-matter/01-revision-history.md)
- ✅ [2. Contributors](front-matter/02-contributors.md)
- ✅ [3. License](front-matter/03-license.md)
- ✅ [4. Preface](front-matter/04-preface.md)
- ✅ [5. Purpose](front-matter/05-purpose.md)
- ✅ [6. Scope](front-matter/06-scope.md)
- ✅ [7. Intended Audience](front-matter/07-intended-audience.md)
- ✅ [8. Terminology](front-matter/08-terminology.md)
- ✅ [9. Normative Language](front-matter/09-normative-language.md)
- ✅ [10. Conformance](front-matter/10-conformance.md)

---

## Part I — Foundations

- ✅ [Volume I — Architecture & Concepts](part-i-foundations/volume-i-architecture-concepts.md)
- ✅ [Volume II — Domain Model](part-i-foundations/volume-ii-domain-model.md)

## Part II — Execution

- ✅ [Volume III — Execution Engine](part-ii-execution/volume-iii-execution-engine.md)
- ✅ [Volume IV — Dataset Engine](part-ii-execution/volume-iv-dataset-engine.md)
- ✅ [Volume V — Validator Engine](part-ii-execution/volume-v-validator-engine.md)
- ✅ [Volume VI — Judge Engine](part-ii-execution/volume-vi-judge-engine.md)

## Part III — Testing Methodology

- ✅ [Volume VII — Quality Contracts](part-iii-testing-methodology/volume-vii-quality-contracts.md)
- ✅ [Volume VIII — Test Design](part-iii-testing-methodology/volume-viii-test-design.md)
- ✅ [Volume IX — Test Types](part-iii-testing-methodology/volume-ix-test-types.md)
- ✅ [Volume X — Regression & Baselines](part-iii-testing-methodology/volume-x-regression-baselines.md)

## Part IV — Enterprise Architecture

- ✅ [Volume XI — Reporting & Analytics](part-iv-enterprise-architecture/volume-xi-reporting-analytics.md)
- ✅ [Volume XII — Governance](part-iv-enterprise-architecture/volume-xii-governance.md)
- ✅ [Volume XIII — CI/CD Integration](part-iv-enterprise-architecture/volume-xiii-cicd-integration.md)
- ✅ [Volume XIV — SDK & APIs](part-iv-enterprise-architecture/volume-xiv-sdk-apis.md)
- ✅ [Volume XV — Reference UI](part-iv-enterprise-architecture/volume-xv-reference-ui.md)

## Part V — Extensibility

- ✅ [Volume XVI — Plugin Architecture](part-v-extensibility/volume-xvi-plugin-architecture.md)
- ✅ [Volume XVII — Reference Implementations](part-v-extensibility/volume-xvii-reference-implementations.md)

---

## Appendices

- ✅ [Appendix A — AQEF YAML Specification](appendices/appendix-a-yaml-specification.md)
- ✅ [Appendix B — AQEF JSON Schema](appendices/appendix-b-json-schema.md)
- ✅ [Appendix C — REST API Specification](appendices/appendix-c-rest-api-specification.md)
- ✅ [Appendix D — Glossary](appendices/appendix-d-glossary.md)
- ✅ [Appendix E — UML Diagrams](appendices/appendix-e-uml-diagrams.md)
- ✅ [Appendix F — Sequence Diagrams](appendices/appendix-f-sequence-diagrams.md)
- ✅ [Appendix G — C4 Model](appendices/appendix-g-c4-model.md)
- ✅ [Appendix H — Reference Examples](appendices/appendix-h-reference-examples.md)
- ✅ [Appendix I — Best Practices](appendices/appendix-i-best-practices.md)
- ✅ [Appendix J — Migration Guide](appendices/appendix-j-migration-guide.md)
- ✅ [Appendix K — Quick Start Guide](appendices/appendix-k-quick-start-guide.md)

---

## Working notes (not part of the published document)

- [_project-notes/decisions-log.md](_project-notes/decisions-log.md) — cross-cutting
  terminology/model decisions every Volume must stay consistent with.

---

**Milestone:** the entire specification is now drafted — all 11 Front Matter sections,
all seventeen Volumes, and all eleven Appendices (A–K). 43 cross-cutting decisions are
recorded in `_project-notes/decisions-log.md`.
