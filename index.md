# AQEF — AI Quality Engineering Framework
### Master Index (Working Draft v0.26)

Legend: ✅ drafted & confirmed · 🟨 partially drafted · ⬜ not yet drafted

Structure: one file per Front Matter section / Volume / Appendix, so any future edit
touches a single small file rather than the whole document. Working, non-reader-facing
notes live in `_project-notes/` (currently: `decisions-log.md`).

**Note on file organization:** Claude Projects flatten uploaded folders to a single
level, so the working copies in this Project's knowledge base are flat (no
`front-matter/`, `part-i-foundations/`, etc. prefixes) even though this index links to
nested paths. This archive (and its `.zip`) is the canonical nested structure — treat it
as the source of truth for organization (e.g., in a git repo or local folder), and
re-flatten filenames only when re-uploading individual files into the Project's
knowledge base.

**Note on sync (2026-07-30):** this working copy was synchronized against
`AQEF-Specification-v0.2.md` (uploaded as PDF) to bring Front Matter §0–3 and all
Appendices up to date with the parallel drafting session. See the note at the bottom of
this file for what that sync did and did not carry over.

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
all seventeen Volumes, and all eleven Appendices (A–K). 32 cross-cutting decisions are
recorded in `_project-notes/decisions-log.md`.

**Sync note (2026-07-30):** Front Matter §0–3 and Appendices A–K were pulled from
`AQEF-Specification-v0.2.md` (a parallel drafting session, reconciled via its exported
PDF), not drafted fresh in this thread. In reconstructing them from PDF text extraction,
five categories of leftover artifacts from that session's own "remove internal
development references" cleanup pass were found and corrected here:

1. Appendix H's intro referenced "Appendix A (YAML Specification, when drafted)" even
   though Appendix A exists in the same document — stale cross-reference, fixed.
2. Volume I, Chapter 7 (RAG terminology note) retained a bare `(decision 6)` citation —
   the one place the source's cleanup pass missed; not carried over here.
3. Appendix B's cross-validation table and Appendix I's "Common Mistakes" table
   retained bare `#13` / `#15` / `#16` / `#17` / `#25` fragments next to Volume
   citations — not carried over; reconstructed as plain Volume references.
4. Appendix D (Glossary) had four sentences ending in a dangling "per." where
   "decisions-log #N" had been stripped but the sentence wasn't re-closed — fixed.
5. Front Matter §6 (Scope)'s status line and Appendix D's own status line each had a
   truncated sentence fragment from the same regex-based stripping — this thread's own
   §6 and Appendix D were written independently and do not carry the defect.

**Remaining task this sync has not yet completed:** none. The decisions-log citation
cleanup across Volumes I–XVII and Front Matter §4–10 is complete — all ~70 inline
`decisions-log #N` / bare `decision N` citations found across 21 files have been
removed from reader-facing prose, file by file, preserving any reader-facing content in
the same sentence rather than deleting it wholesale. `decisions-log.md` itself remains
untouched as the working record; it is simply no longer cited by number from within the
published prose, consistent with decisions-log #29's own scope note and with how the
parallel v0.2 session treated it.

**Recommended next step:** none strictly required — the specification is complete end
to end (Front Matter, 17 Volumes, 11 Appendices) and internally consistent. Natural
follow-ups if continuing: (a) a final read-through of Appendices E–G's Mermaid diagrams
to confirm they render as intended in whatever viewer will display them, since they
were reconstructed from a PDF where the originals rendered as images; (b) reconciling
this thread's decisions-log.md (32 entries) against whatever the parallel v0.2 session's
own working notes contain, if that session is still active, since the two have been
resolving overlapping questions independently.
