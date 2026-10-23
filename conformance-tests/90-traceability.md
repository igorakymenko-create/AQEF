# 90. Traceability

This section maps every requirement in the MUST inventory of AQEF Working Draft 0.41.1
to the tests that check it, or says why no test does. The inventory is
`_inventory/must-inventory.md` (391 rows, extracted from Working Draft 0.36) together
with `_inventory/must-inventory-v037-additions.md` (28 rows added by 0.37),
`_inventory/must-inventory-v038-additions.md` (12 rows added by 0.38), and
`_inventory/must-inventory-v041-additions.md` (10 rows added by 0.40 to 0.41.1), 441
rows in all, identified `R-nnnn`. It lists every sentence containing MUST or MUST NOT,
and every field Appendix A or C marks as required, so a few rows are definitions or
restatements rather than requirements of their own. Seventeen rows whose text 0.37 to
0.41.1 revised keep their IDs and are marked.

## 90.1 Status values

| Status | Meaning |
|---|---|
| Tested | Checked by the tests named, or by the cases named where a test has cases (1.2). |
| Restates | Says again what another row says; it is covered wherever that row is. Mostly the Glossary (Appendix D), Best Practices (Appendix I), and reference examples. |
| Field | A field Appendix A or C marks as required, whose absence no test checks separately. None in this draft: CT-CFG-025 checks each required configuration field of Appendix A, one case per field, and the tests named check the fields of runtime records. |
| Scoped | Belongs to a capability a Conformance Statement may claim (§10) and has no test in this draft. |
| Not testable | A definition, an introduction to a list, or a statement about people or practice rather than about an implementation. |
| Not yet covered | A requirement on every implementation that this draft has no test for. Listed again in 90.4 when there is any. |

## 90.2 Summary

| Status | Rows |
|---|---|
| Tested | 368 |
| Restates | 44 |
| Field | 0 |
| Scoped | 0 |
| Not testable | 29 |
| Not yet covered | 0 |
| **Total** | **441** |

## 90.3 Requirement → test

| ID | Source | Status | Tests or note |
|---|---|---|---|
| R-0001 | §0, Authorship and Consensus | Not testable | scope of normative language |
| R-0002 | Revision history | Restates | R-0092 (CT-SCT-005) |
| R-0003 | Revision history | Restates | R-0090 (CT-SCT-003, CT-SCT-004) |
| R-0004 | §8 | Restates | R-0080 |
| R-0005 | §8 | Tested | CT-ASM-012 |
| R-0006 | §8 | Tested | CT-ASM-003, CT-ASM-009 |
| R-0007 | §8 | Tested | CT-ASM-004 |
| R-0008 | §9 | Not testable | definition |
| R-0009 | §9 | Not testable | definition |
| R-0010 | §9 | Not testable | definition |
| R-0011 | §9, Why Not the Full RFC 2119 Vocabulary | Not testable | definition |
| R-0012 | §9, Why Not the Full RFC 2119 Vocabulary | Not testable | editorial |
| R-0013 | §9, Scope of Normative Force | Not testable | definition |
| R-0014 | §10, What Conformance Requires | Not testable | definition of Conformance |
| R-0015 | §10, What Conformance Requires | Tested | CT-REL-024 |
| R-0016 | §10, Conformance Statement | Tested | CT-REL-027 |
| R-0017 | §10, The Non-Negotiable Core | Tested | CT-REL-026 |
| R-0018 | §10, The Non-Negotiable Core | Tested | CT-REL-026 |
| R-0019 | §10, Deviating from a SHOULD | Not testable | editorial |
| R-0020 | Vol I, Evolution of Software Testing | Not testable | background |
| R-0021 | Vol I, Validation before Evaluation | Tested | CT-ASM-001, CT-ASM-002 |
| R-0022 | Vol I, Independent Oracles | Tested | CT-CFG-006 |
| R-0023 | Vol I, Deterministic Infrastructure | Tested | CT-EXE-007, CT-EXE-008 |
| R-0024 | Vol I, Deterministic Infrastructure | Tested | CT-EXE-007 |
| R-0025 | Vol I, Everything has Confidence | Tested | CT-ASM-003 |
| R-0026 | Vol I, Everything has Confidence | Tested | CT-ASM-003 |
| R-0027 | Vol I, Everything has Confidence | Tested | CT-ASM-003 |
| R-0028 | Vol I, Requirements | Not testable | applies to Requirements people write |
| R-0029 | Vol I, Execution | Tested | CT-EXE-007 |
| R-0030 | Vol I, Validation | Tested | CT-ASM-002 |
| R-0031 | Vol I, Decision Pipeline | Tested | CT-DEC-006 |
| R-0032 | Vol I, Confidence Model | Tested | CT-ASM-005, CT-HRV-004 |
| R-0033 | Vol I, Aggregation Model | Not testable | introduces R-0034 and R-0035 |
| R-0034 | Vol I, Aggregation Model | Tested | CT-DEC-020 |
| R-0035 | Vol I, Aggregation Model | Tested | CT-DEC-019 |
| R-0036 | Vol I, Aggregate Basis | Tested | CT-DEC-002 |
| R-0037 | Vol I, Aggregate Basis | Tested | CT-DEC-002 |
| R-0038 | Vol I, Aggregate Basis | Tested | CT-DEC-021 |
| R-0039 | Vol I, Quality Gates | Tested | CT-REL-001, CT-REL-003 |
| R-0040 | Vol I, Quality Gates | Tested | CT-DEC-015, CT-DEC-017, CT-SCT-011, CT-SCT-015 |
| R-0041 | Vol I, Quality Gates | Tested | CT-DEC-004 |
| R-0042 | Vol I, Quality Gates | Tested | CT-REL-001, CT-REL-002 |
| R-0043 | Vol I, Quality Gates | Tested | CT-REL-002, CT-REL-006 |
| R-0044 | Vol I, Quality Gates | Tested | CT-REL-007 |
| R-0045 | Vol I, Quality Gates | Tested | CT-DEC-006, CT-DEC-007, CT-DEC-011 |
| R-0046 | Vol I, Quality Gates | Tested | CT-REL-010 |
| R-0047 | Vol I, AI Agent | Tested | CT-TTP-002 |
| R-0048 | Vol II, Entities | Tested | CT-EXE-001 |
| R-0049 | Vol III, Runtime | Tested | CT-EXE-007 |
| R-0050 | Vol III, Action Boundary | Tested | CT-ABD-001, CT-ABD-005 |
| R-0051 | Vol III, Action Boundary | Tested | CT-ABD-003 |
| R-0052 | Vol III, Action Boundary | Tested | CT-ABD-007 |
| R-0053 | Vol III, Scheduling | Tested | CT-EXE-009 |
| R-0054 | Vol III, Parallelization | Tested | CT-EXE-006 |
| R-0055 | Vol III, Retry | Tested | CT-EXE-003 |
| R-0056 | Vol III, Retry | Tested | CT-EXE-004, CT-EXE-005 |
| R-0057 | Vol III, Variables | Tested | CT-EXE-002 |
| R-0058 | Vol III, Conversation Engine | Tested | CT-EXE-011 |
| R-0059 | Vol III, Artifact Collection | Tested | CT-EXE-012 |
| R-0060 | Vol III, Artifact Collection | Tested | CT-ABD-003, CT-ABD-004 |
| R-0061 | Vol IV, Generated Datasets | Not testable | explains why Volume IV uses SHOULD |
| R-0062 | Vol IV, Production Replay | Not testable | defers to Project policy |
| R-0063 | Vol IV, Versioning | Tested | CT-CFG-017, CT-EXE-010, CT-DSR-003 |
| R-0064 | Vol V, Validator Architecture | Tested | CT-ASM-009 |
| R-0065 | Vol V, Validator Architecture | Tested | CT-ASM-010 |
| R-0066 | Vol V, Validator Architecture | Tested | CT-ASM-003 |
| R-0067 | Vol V, Execution Order | Tested | CT-ASM-001 |
| R-0068 | Vol V, Custom Validators | Tested | CT-ASM-016 |
| R-0069 | Vol V, Custom Validators | Tested | CT-ASM-017 |
| R-0070 | Vol V, Validator SDK | Tested | CT-ASM-016 |
| R-0071 | Vol V, Validator SDK | Tested | CT-ASM-018 |
| R-0072 | Vol VI, Judge Architecture | Tested | CT-ASM-004 |
| R-0073 | Vol VI, Judge Architecture | Tested | CT-ASM-011 |
| R-0074 | Vol VI, Single Judge | Tested | CT-ASM-019; text revised in v0.37 or later |
| R-0075 | Vol VI, Multi Judge | Tested | CT-MJG-001 |
| R-0076 | Vol VI, Consensus | Tested | CT-ASM-013, CT-MJG-005, CT-MJG-006 |
| R-0077 | Vol VI, Confidence | Tested | CT-MJG-007 |
| R-0078 | Vol VI, Human Review | Tested | CT-HRV-003, CT-HRV-005; text revised in v0.37 or later |
| R-0079 | Vol VI, Human Review | Tested | CT-ASM-008, CT-ASM-015, CT-DEC-013 |
| R-0080 | Vol VII | Not testable | definition of Quality Contract |
| R-0081 | Vol VII, Contract Language | Not testable | property of the Contract language |
| R-0082 | Vol VII, Constraints | Tested | CT-CFG-019 |
| R-0083 | Vol VII, Expectations | Tested | CT-ASM-011 |
| R-0084 | Vol VII, Contract Composition | Tested | CT-CFG-007 |
| R-0085 | Vol VIII, Test Design Process | Not testable | applies to Test Design, a human activity |
| R-0086 | Vol VIII, AI Test Patterns | Not testable | describes a test pattern |
| R-0087 | Vol VIII, Seeded Controls | Tested | CT-SCT-007 |
| R-0088 | Vol VIII, Seeded Controls | Tested | CT-DEC-016, CT-SCT-010 |
| R-0089 | Vol VIII, Seeded Controls | Tested | CT-SCT-001; text revised in v0.40 or later |
| R-0090 | Vol VIII, Seeded Controls | Tested | CT-SCT-003, CT-SCT-004 |
| R-0091 | Vol VIII, Seeded Controls | Tested | CT-SCT-006 |
| R-0092 | Vol VIII, Seeded Controls | Tested | CT-SCT-005 |
| R-0093 | Vol VIII, Test Maintainability | Not testable | describes practice |
| R-0094 | Vol X, Baselines | Tested | CT-REL-021 |
| R-0095 | Vol X, Model Drift | Tested | CT-TTP-001 |
| R-0096 | Vol X, Dataset Drift | Restates | R-0063 (CT-CFG-017, CT-EXE-010, CT-DSR-003) |
| R-0097 | Vol XI, Reports | Tested | CT-REL-035 |
| R-0098 | Vol XI, Quality Gates | Tested | CT-REL-003, CT-REL-029 |
| R-0099 | Vol XI, Quality Gates | Tested | CT-REL-029 |
| R-0100 | Vol XI, Quality Gates | Tested | CT-REL-029 |
| R-0101 | Vol XI, KPIs | Tested | CT-REL-036 |
| R-0102 | Vol XII, Permissions | Tested | CT-REL-032 |
| R-0103 | Vol XII, Principals | Tested | CT-REL-019 |
| R-0104 | Vol XII, Principals | Tested | CT-REL-033 |
| R-0105 | Vol XII, Principals | Tested | CT-REL-017 |
| R-0106 | Vol XII, Principals | Tested | CT-REL-020 |
| R-0107 | Vol XII, Principals | Tested | CT-REL-018 |
| R-0108 | Vol XII, Traceability | Tested | CT-REL-022 |
| R-0109 | Vol XII, Compliance | Not testable | scope of Compliance |
| R-0110 | Vol XII, Approval Workflow | Not testable | describes Approval Workflow; its four cases are tested separately |
| R-0111 | Vol XII, Approval Workflow | Tested | CT-REL-007 |
| R-0112 | Vol XIII, Azure DevOps | Tested | CT-REL-037 |
| R-0113 | Vol XIII, Quality Gates | Tested | CT-REL-024 |
| R-0114 | Vol XIII, Quality Gates | Tested | CT-REL-025 |
| R-0115 | Vol XIV, CLI | Tested | CT-SDK-001 |
| R-0116 | Vol XV, Visual Test Designer | Tested | CT-RUI-001 |
| R-0117 | Vol XV, Validator Designer | Tested | CT-RUI-002 |
| R-0118 | Vol XV, Validator Designer | Tested | CT-RUI-002 |
| R-0119 | Vol XV, Judge Configuration | Tested | CT-RUI-003 |
| R-0120 | Vol XV, Reporting UI | Tested | CT-RUI-004 |
| R-0121 | Vol XVI | Tested | CT-PLG-005 |
| R-0122 | Vol XVI, Validator Plugins | Tested | CT-PLG-001 |
| R-0123 | Vol XVI, Validator Plugins | Tested | CT-PLG-002 |
| R-0124 | Vol XVI, Dataset Plugins | Tested | CT-PLG-006 |
| R-0125 | Vol XVI, Report Plugins | Tested | CT-PLG-007 |
| R-0126 | Vol XVI, Plugin Invocation | Tested | CT-PLG-003 |
| R-0127 | Vol XVI, Extension Lifecycle | Tested | CT-PLG-004 |
| R-0128 | App A | Tested | CT-CFG-001 |
| R-0129 | App A, A.1 — Project | Tested | CT-CFG-025.01 |
| R-0130 | App A, A.1 — Project | Tested | CT-CFG-020 |
| R-0131 | App A, A.1 — Project | Restates | R-0130 (CT-CFG-020) |
| R-0132 | App A, A.1 — Project | Tested | CT-CFG-025.25; the source line is DefectClassConfig `name`, which the inventory labels Project.name |
| R-0133 | App A, A.1 — Project | Tested | CT-SCT-005 |
| R-0134 | App A, A.1 — Project | Tested | CT-SCT-005 |
| R-0135 | App A, A.1 — Project | Tested | CT-SCT-005 |
| R-0136 | App A, A.1 — Project | Tested | CT-SCT-006 |
| R-0137 | App A, A.2 — Environment | Tested | CT-CFG-025.02 |
| R-0138 | App A, A.2 — Environment | Tested | CT-CFG-025.03 |
| R-0139 | App A, A.2 — Environment | Tested | CT-CFG-025.04 |
| R-0140 | App A, A.2 — Environment | Tested | CT-CFG-025.05 |
| R-0141 | App A, A.2 — Environment | Tested | CT-ABD-001 |
| R-0142 | App A, A.2 — Environment | Tested | CT-CFG-025.06 |
| R-0143 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0144 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0145 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0146 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0147 | App A, A.2 — Environment | Tested | CT-ABD-006 |
| R-0148 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0149 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0150 | App A, A.2 — Environment | Tested | CT-ABD-002 |
| R-0151 | App A, A.3 — Suite | Tested | CT-CFG-025.07 |
| R-0152 | App A, A.3 — Suite | Tested | CT-CFG-021 |
| R-0153 | App A, A.3 — Suite | Restates | R-0152 (CT-CFG-021) |
| R-0154 | App A, A.3 — Suite | Tested | CT-CFG-009 |
| R-0155 | App A, A.4 — Scenario | Tested | CT-CFG-025.08 |
| R-0156 | App A, A.4 — Scenario | Tested | CT-CFG-002 |
| R-0157 | App A, A.4 — Scenario | Tested | CT-CFG-002 |
| R-0158 | App A, A.4 — Scenario | Tested | CT-CFG-022, CT-DSR-004 |
| R-0159 | App A, A.4 — Scenario | Not testable | states what is permitted; the prohibition is R-0160 |
| R-0160 | App A, A.4 — Scenario | Tested | CT-CFG-011 |
| R-0161 | App A, A.4 — Scenario | Tested | CT-CFG-022 |
| R-0162 | App A, A.4 — Scenario | Tested | CT-EXE-002 |
| R-0163 | App A, A.4 — Scenario | Tested | CT-CFG-008 |
| R-0164 | App A, A.4 — Scenario | Tested | CT-SCT-001 |
| R-0165 | App A, A.4 — Scenario | Tested | CT-SCT-005 |
| R-0166 | App A, A.4 — Scenario | Tested | CT-SCT-001, CT-SCT-009; text revised in v0.40 or later |
| R-0167 | App A, A.4 — Scenario | Tested | CT-SCT-001 |
| R-0168 | App A, A.4 — Scenario | Tested | CT-SCT-002 |
| R-0169 | App A, A.4 — Scenario | Tested | CT-SCT-002 |
| R-0170 | App A, A.4 — Scenario | Tested | CT-SCT-002 |
| R-0171 | App A, A.5 — Quality Contract | Restates | R-0080 |
| R-0172 | App A, A.5 — Quality Contract | Tested | CT-CFG-023 |
| R-0173 | App A, A.5 — Quality Contract | Tested | CT-CFG-003 |
| R-0174 | App A, A.5 — Quality Contract | Tested | CT-CFG-019 |
| R-0175 | App A, A.5 — Quality Contract | Tested | CT-CFG-025.09 |
| R-0176 | App A, A.5 — Quality Contract | Tested | CT-CFG-025.10 |
| R-0177 | App A, A.5 — Quality Contract | Tested | CT-CFG-025.11 |
| R-0178 | App A, A.5 — Quality Contract | Tested | CT-CFG-004 |
| R-0179 | App A, A.5 — Quality Contract | Tested | CT-CFG-004 |
| R-0180 | App A, A.5 — Quality Contract | Tested | CT-CFG-004 |
| R-0181 | App A, A.5 — Quality Contract | Tested | CT-CFG-005 |
| R-0182 | App A, A.5 — Quality Contract | Tested | CT-CFG-004 |
| R-0183 | App A, A.5 — Quality Contract | Tested | CT-HRV-001 |
| R-0184 | App A, A.5 — Quality Contract | Tested | CT-HRV-002 |
| R-0185 | App A, A.6 — JudgeConfig | Tested | CT-CFG-025.12 |
| R-0186 | App A, A.6 — JudgeConfig | Tested | CT-CFG-006 |
| R-0187 | App A, A.6 — JudgeConfig | Tested | CT-CFG-025.13 |
| R-0188 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-001 |
| R-0189 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-001 |
| R-0190 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-002 |
| R-0191 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-002, CT-MJG-006 |
| R-0192 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-002, CT-MJG-006 |
| R-0193 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-003 |
| R-0194 | App A, A.7 — MultiJudgeConfig | Tested | CT-MJG-003 |
| R-0195 | App A, A.8 — Dataset | Tested | CT-CFG-025.19 |
| R-0196 | App A, A.8 — Dataset | Tested | CT-CFG-017 |
| R-0197 | App A, A.8 — Dataset | Restates | R-0063 (CT-CFG-017, CT-EXE-010, CT-DSR-003) |
| R-0198 | App A, A.8 — Dataset | Tested | CT-CFG-025.20 |
| R-0199 | App A, A.8 — Dataset | Tested | CT-CFG-025.21 |
| R-0200 | App A, A.8 — Dataset | Tested | CT-DSR-001 |
| R-0201 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0202 | App A, A.8 — Dataset | Tested | CT-CFG-025.22 |
| R-0203 | App A, A.8 — Dataset | Tested | CT-CFG-025.23 |
| R-0204 | App A, A.8 — Dataset | Tested | CT-DSR-001 |
| R-0205 | App A, A.8 — Dataset | Tested | CT-DSR-001 |
| R-0206 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0207 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0208 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0209 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0210 | App A, A.8 — Dataset | Tested | CT-DSR-002 |
| R-0211 | App A, A.8 — Dataset | Tested | CT-CFG-025.24 |
| R-0212 | App A, A.9 — ExecutionConfig | Tested | CT-EXE-006 |
| R-0213 | App A, A.9 — ExecutionConfig | Tested | CT-CFG-025.18 |
| R-0214 | App A, A.9 — ExecutionConfig | Tested | CT-CFG-010 |
| R-0215 | App A, A.9 — ExecutionConfig | Tested | CT-CFG-010 |
| R-0216 | App A, A.10 — Quality Gates | Tested | CT-CFG-025.14 |
| R-0217 | App A, A.10 — Quality Gates | Tested | CT-CFG-025.15 |
| R-0218 | App A, A.10 — Quality Gates | Tested | CT-CFG-025.16 |
| R-0219 | App A, A.10 — Quality Gates | Tested | CT-CFG-025.17 |
| R-0220 | App A, A.10 — Quality Gates | Tested | CT-REL-002, CT-REL-003 |
| R-0221 | App A, A.10 — Quality Gates | Tested | CT-CFG-024 |
| R-0222 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0223 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0224 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0225 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0226 | App A, A.11 — Baseline | Tested | CT-REL-017, CT-REL-021 |
| R-0227 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0228 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0229 | App A, A.11 — Baseline | Tested | CT-REL-021 |
| R-0230 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0231 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0232 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0233 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0234 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0235 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0236 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0237 | App A, A.12 — Release Decision | Tested | CT-REL-001, CT-REL-018 |
| R-0238 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0239 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0240 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0241 | App A, A.12 — Release Decision | Tested | CT-REL-001 |
| R-0242 | App A, A.12 — Release Decision | Tested | CT-REL-010 |
| R-0243 | App A, A.12 — Release Decision | Tested | CT-DEC-001 |
| R-0244 | App A, A.12 — Release Decision | Tested | CT-DEC-001 |
| R-0245 | App A, A.12 — Release Decision | Tested | CT-DEC-001 |
| R-0246 | App A, A.12 — Release Decision | Tested | CT-DEC-001, CT-DEC-017 |
| R-0247 | App A, A.12 — Release Decision | Tested | CT-DEC-001, CT-REL-014 |
| R-0248 | App A, A.12 — Release Decision | Tested | CT-DEC-001 |
| R-0249 | App A, A.12 — Release Decision | Tested | CT-DEC-001, CT-REL-006 |
| R-0250 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0251 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0252 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0253 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0254 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0255 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0256 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0257 | App A, A.13 — Snapshot | Tested | CT-REL-013 |
| R-0258 | App B | Not testable | introduces B.2 |
| R-0259 | App B | Not testable | introduces B.2 |
| R-0260 | App B, B.1 — Schema Structure Overview | Not testable | introduces B.1 |
| R-0261 | App B, B.2 — Property Constraints | Not testable | introduces B.2 |
| R-0262 | App B, B.2 — Property Constraints | Tested | CT-SCT-005 |
| R-0263 | App B, B.2 — Property Constraints | Tested | CT-SCT-005 |
| R-0264 | App B, B.2 — Property Constraints | Tested | CT-SCT-002 |
| R-0265 | App B, B.2 — Property Constraints | Tested | CT-SCT-002 |
| R-0266 | App B, B.2 — Property Constraints | Tested | CT-CFG-003 |
| R-0267 | App B, B.2 — Property Constraints | Tested | CT-CFG-004 |
| R-0268 | App B, B.2 — Property Constraints | Tested | CT-MJG-002 |
| R-0269 | App B, B.2 — Property Constraints | Tested | CT-MJG-002 |
| R-0270 | App B, B.2 — Property Constraints | Tested | CT-MJG-004 |
| R-0271 | App B, B.2 — Property Constraints | Tested | CT-CFG-010 |
| R-0272 | App B, B.2 — Property Constraints | Restates | R-0221 (CT-CFG-024) |
| R-0273 | App B, B.2 — Property Constraints | Tested | CT-DEC-005, CT-DEC-008 |
| R-0274 | App B, B.3 — Cross-Type Validation Rules | Not testable | introduces B.3 |
| R-0275 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-006 |
| R-0276 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-002 |
| R-0277 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-007, CT-CFG-012, CT-CFG-013; text revised in v0.37 or later |
| R-0278 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-009 |
| R-0279 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-022, CT-DSR-004 |
| R-0280 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-008 |
| R-0281 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-004, CT-CFG-005 |
| R-0282 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-018, CT-DSR-003 |
| R-0283 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-010, CT-EXE-004 |
| R-0284 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-034 |
| R-0285 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-007; text revised in v0.37 or later |
| R-0286 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ASM-006, CT-ASM-007 |
| R-0287 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ASM-006 |
| R-0288 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-SCT-006 |
| R-0289 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-SCT-003, CT-SCT-004, CT-SCT-012, CT-SCT-013; text revised in v0.40 or later |
| R-0290 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-015 |
| R-0291 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ASM-013, CT-MJG-008 |
| R-0292 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-MJG-008, CT-MJG-009 |
| R-0293 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-002 |
| R-0294 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-004 |
| R-0295 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ABD-001 |
| R-0296 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ABD-003, CT-ABD-004 |
| R-0297 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ABD-006 |
| R-0298 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-022 |
| R-0299 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-012, CT-DEC-014, CT-DEC-018, CT-SCT-008, CT-SCT-014 |
| R-0300 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-012 |
| R-0301 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-010 |
| R-0302 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-015, CT-SCT-011 |
| R-0303 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ASM-014 |
| R-0304 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-005, CT-DEC-008, CT-ADM-007 |
| R-0305 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-006, CT-DEC-007, CT-SCT-011; text revised in v0.40 or later |
| R-0306 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-006, CT-REL-008; text revised in v0.37 or later |
| R-0307 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-007 |
| R-0308 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-004 |
| R-0309 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-010, CT-REL-011, CT-REL-012 |
| R-0310 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-005 |
| R-0311 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-001, CT-REL-016, CT-REL-021 |
| R-0312 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-017 |
| R-0313 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-020 |
| R-0314 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-018 |
| R-0315 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-013 |
| R-0316 | App C | Tested | CT-SDK-001, CT-SDK-002 |
| R-0317 | App C, C.1 — Design Principles | Tested | CT-EXE-007 |
| R-0318 | App C, C.3 — Operations by Resource | Tested | CT-CFG-017 |
| R-0319 | App C, C.3 — Operations by Resource | Tested | CT-DEC-015, CT-SCT-010, CT-SCT-011 |
| R-0320 | App C, C.3 — Operations by Resource | Tested | CT-DEC-017, CT-SCT-015 |
| R-0321 | App C, C.3 — Operations by Resource | Tested | CT-SCT-007 |
| R-0322 | App C, C.3 — Operations by Resource | Tested | CT-SCT-007 |
| R-0323 | App C, C.3 — Operations by Resource | Tested | CT-REL-008; text revised in v0.37 or later |
| R-0324 | App C, C.3 — Operations by Resource | Tested | CT-DEC-001, CT-DEC-002 |
| R-0325 | App C, C.3 — Operations by Resource | Tested | CT-DEC-003 |
| R-0326 | App C, C.3 — Operations by Resource | Tested | CT-REL-005, CT-REL-010 |
| R-0327 | App C, C.4 — Authentication and Authorization | Tested | CT-REL-028 |
| R-0328 | App C, C.4 — Authentication and Authorization | Tested | CT-REL-019, CT-REL-028 |
| R-0329 | App C, C.4 — Authentication and Authorization | Tested | CT-REL-008, CT-REL-009, CT-REL-015, CT-REL-016, CT-REL-030 |
| R-0330 | App C, C.4 — Authentication and Authorization | Tested | CT-REL-008, CT-REL-009, CT-REL-015, CT-REL-016, CT-REL-030 |
| R-0331 | App C, C.6 — Pagination and Filtering | Tested | CT-API-001 |
| R-0332 | App C, C.6 — Pagination and Filtering | Tested | CT-API-001 |
| R-0333 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0334 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0335 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0336 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0337 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006, CT-ASM-012 |
| R-0338 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0339 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0340 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0341 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006 |
| R-0342 | App C, C.7 — Result Response Shape | Tested | CT-ASM-013 |
| R-0343 | App C, C.7 — Result Response Shape | Tested | CT-ASM-008, CT-DEC-007 |
| R-0344 | App C, C.7 — Result Response Shape | Tested | CT-DEC-006, CT-DEC-007, CT-DEC-009 |
| R-0345 | App C, C.8 — Deletion and Referential Integrity | Tested | CT-PLG-004 |
| R-0346 | App C, C.8 — Deletion and Referential Integrity | Tested | CT-REL-022 |
| R-0347 | App C, C.8 — Deletion and Referential Integrity | Tested | CT-REL-022 |
| R-0348 | App C, C.8 — Deletion and Referential Integrity | Tested | CT-API-002 |
| R-0349 | App C, C.8 — Deletion and Referential Integrity | Tested | CT-API-002 |
| R-0350 | App D | Restates | R-0036 (CT-DEC-002) |
| R-0351 | App D | Restates | R-0042 (CT-REL-001, CT-REL-002) |
| R-0352 | App D | Tested | CT-SDK-002 |
| R-0353 | App D | Restates | R-0016 (CT-REL-027) |
| R-0354 | App D | Restates | R-0084 (CT-CFG-007) |
| R-0355 | App D | Restates | R-0081 |
| R-0356 | App D | Restates | R-0007 (CT-ASM-004) |
| R-0357 | App D | Restates | R-0075 (CT-MJG-001) |
| R-0358 | App D | Restates | R-0080 |
| R-0359 | App D | Tested | CT-SDK-002 |
| R-0360 | App D | Restates | R-0007 (CT-ASM-004) |
| R-0361 | App D | Restates | R-0316 (CT-SDK-001, CT-SDK-002) |
| R-0362 | App D | Restates | R-0090 (CT-SCT-003, CT-SCT-004); text revised in v0.40 or later |
| R-0363 | App D | Restates | R-0006 (CT-ASM-003, CT-ASM-009) |
| R-0364 | App H, H.4 — Contract Composition and Reusable Contracts | Restates | R-0084 (CT-CFG-007); text revised in v0.37 or later |
| R-0365 | App H, H.5 — Multi-Judge: Independence vs. Stability | Restates | R-0189 (CT-MJG-001) |
| R-0366 | App H, H.5 — Multi-Judge: Independence vs. Stability | Restates | R-0189 (CT-MJG-001) |
| R-0367 | App H, H.9 — Human Reviewer Binding and Non-Actionable Dispositions | Restates | R-0045 (CT-DEC-006, CT-DEC-007, CT-DEC-011) |
| R-0368 | App I, I.1 — Contract Design | Restates | R-0081 |
| R-0369 | App I, I.1 — Contract Design | Restates | R-0083 (CT-ASM-011) |
| R-0370 | App I, I.1 — Contract Design | Restates | R-0084 (CT-CFG-007) |
| R-0371 | App I, I.2 — Validators and Judges | Restates | R-0022 (CT-CFG-006) |
| R-0372 | App I, I.2 — Validators and Judges | Restates | R-0075 (CT-MJG-001) |
| R-0373 | App I, I.3 — Dataset Management | Restates | R-0063 (CT-CFG-017, CT-EXE-010, CT-DSR-003) |
| R-0374 | App I, I.3 — Dataset Management | Not testable | describes practice |
| R-0375 | App I, I.3 — Dataset Management | Restates | R-0062 |
| R-0376 | App I, I.4 — Execution and Runtime | Restates | R-0023 (CT-EXE-007, CT-EXE-008) |
| R-0377 | App I, I.4 — Execution and Runtime | Restates | R-0054 (CT-EXE-006) |
| R-0378 | App I, I.4 — Execution and Runtime | Restates | R-0056 (CT-EXE-004, CT-EXE-005) |
| R-0379 | App I, I.5 — Regression and Baselines | Tested | CT-TTP-001 |
| R-0380 | App I, I.6 — Governance | Restates | R-0110 |
| R-0381 | App I, I.6 — Governance | Not testable | applies to people |
| R-0382 | App I, I.7 — CI/CD Integration | Restates | R-0113 (CT-REL-024) |
| R-0383 | App I, I.7 — CI/CD Integration | Tested | CT-SDK-001, CT-SDK-002 |
| R-0384 | App I, I.8 — Extensibility | Tested | CT-PLG-001 |
| R-0385 | App I, I.8 — Extensibility | Restates | R-0282 (CT-CFG-018, CT-DSR-003) |
| R-0386 | App I, I.9 — Common Mistakes | Restates | R-0056 (CT-EXE-004, CT-EXE-005) |
| R-0387 | App I, I.9 — Common Mistakes | Restates | R-0064 (CT-ASM-009) |
| R-0388 | App I, I.9 — Common Mistakes | Restates | R-0022 (CT-CFG-006) |
| R-0389 | App I, I.9 — Common Mistakes | Restates | R-0043 (CT-REL-002, CT-REL-006) |
| R-0390 | App I, I.9 — Common Mistakes | Restates | R-0189 (CT-MJG-001) |
| R-0391 | App K, Step 6 — Evaluation (Semantic Check) | Restates | R-0022 (CT-CFG-006) |
| R-0392 | App A, A.4 — Scenario | Tested | CT-CFG-014; added in v0.37 |
| R-0393 | App A, A.5 — Quality Contract | Tested | CT-CFG-016; added in v0.37 |
| R-0394 | App A, A.12 — Release Decision | Tested | CT-REL-001; added in v0.37 |
| R-0395 | App A, A.12 — Release Decision | Tested | CT-REL-018; added in v0.37 |
| R-0396 | App A, A.12 — Release Decision | Tested | CT-DEC-001; added in v0.37 |
| R-0397 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0398 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0399 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0400 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0401 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0402 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0403 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0404 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0405 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0406 | App A, A.14 — Release Policy | Tested | CT-REL-031; added in v0.37 |
| R-0407 | App A, A.14 — Release Policy | Tested | CT-REL-018; added in v0.37 |
| R-0408 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-015; added in v0.37 |
| R-0409 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-011, CT-CFG-014; added in v0.37 |
| R-0410 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-CFG-016; added in v0.37 |
| R-0411 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-DEC-022, CT-DEC-023; text revised in v0.37 or later; added in v0.37 |
| R-0412 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-REL-018; added in v0.37 |
| R-0413 | App C, C.3 — Operations by Resource | Tested | CT-DEC-012, CT-DEC-013, CT-DEC-018; added in v0.37 |
| R-0414 | App C, C.3 — Operations by Resource | Tested | CT-DEC-012, CT-HRV-002, CT-HRV-005; text revised in v0.37 or later; added in v0.37 |
| R-0415 | App C, C.3 — Operations by Resource | Tested | CT-DEC-013, CT-DEC-018, CT-SCT-008, CT-SCT-014; text revised in v0.40 or later; added in v0.37 |
| R-0416 | App C, C.3 — Operations by Resource | Tested | CT-REL-031; added in v0.37 |
| R-0417 | App C, C.3 — Operations by Resource | Tested | CT-REL-031; added in v0.37 |
| R-0418 | App C, C.7 — Result Response Shape | Tested | CT-ASM-006; added in v0.37 |
| R-0419 | Vol I, Quality Gates | Tested | CT-DEC-022, CT-DEC-023, CT-REL-012; added in v0.37 |
| R-0420 | App A, A.5 — Quality Contract | Tested | CT-HRV-006; added in v0.38 |
| R-0421 | App A, A.5 — Quality Contract | Tested | CT-HRV-006; added in v0.38 |
| R-0422 | App B, B.2 — Property Constraints | Tested | CT-HRV-006; added in v0.38 |
| R-0423 | App C, C.3 — Operations by Resource | Tested | CT-SCT-004, CT-SCT-013; text revised in v0.40 or later; added in v0.38 |
| R-0424 | App C, C.3 — Operations by Resource | Tested | CT-SCT-008, CT-SCT-014; text revised in v0.40 or later; added in v0.38 |
| R-0425 | App C, C.7 — Result Response Shape | Tested | CT-ASM-019; added in v0.38 |
| R-0426 | App C, C.10 — Report Response Shape | Tested | CT-REL-029; added in v0.38 |
| R-0427 | App C, C.10 — Report Response Shape | Tested | CT-REL-029; added in v0.38 |
| R-0428 | App C, C.10 — Report Response Shape | Tested | CT-REL-029; added in v0.38 |
| R-0429 | App C, C.10 — Report Response Shape | Tested | CT-REL-029; added in v0.38 |
| R-0430 | App C, C.10 — Report Response Shape | Tested | CT-REL-029; added in v0.38 |
| R-0431 | App C, C.10 — Report Response Shape | Tested | CT-REL-029, CT-REL-035; added in v0.38 |
| R-0432 | App A, A.4 — Scenario | Tested | CT-SCT-009; added in v0.40 to v0.41.1 |
| R-0433 | App B, B.2 — Property Constraints | Tested | CT-SCT-009; added in v0.40 to v0.41.1 |
| R-0434 | App B, B.2 — Property Constraints | Tested | CT-SCT-009; added in v0.40 to v0.41.1 |
| R-0435 | Vol VI, Admission | Tested | CT-ADM-001; added in v0.40 to v0.41.1 |
| R-0436 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ADM-001, CT-ADM-002, CT-ADM-003, CT-ADM-004; added in v0.40 to v0.41.1 |
| R-0437 | App C, C.3 — Operations by Resource | Tested | CT-ADM-001; added in v0.40 to v0.41.1 |
| R-0438 | App C, C.3 — Operations by Resource | Tested | CT-ADM-003; added in v0.40 to v0.41.1 |
| R-0439 | App C, C.3 — Operations by Resource | Tested | CT-ADM-001, CT-ADM-002; added in v0.40 to v0.41.1 |
| R-0440 | App C, C.3 — Operations by Resource | Tested | CT-ADM-002, CT-ADM-003; added in v0.40 to v0.41.1 |
| R-0441 | App B, B.3 — Cross-Type Validation Rules | Tested | CT-ADM-004, CT-ADM-005, CT-ADM-006, CT-ADM-007; added in v0.40 to v0.41.1 |

## 90.4 Not yet covered

None. Every testable requirement in the inventory, core and scoped, has at least one test.

This is a statement about the tests written, not about any implementation. A requirement
whose tests or cases are all `NOT_RUN` or `NOT_APPLICABLE` in a test run was not verified in that
run; the test report lists it (1.7).

## 90.5 Test → requirement

| Test | Requirements |
|---|---|
| CT-CFG-001 | R-0128 |
| CT-CFG-002 | R-0156, R-0157, R-0276 |
| CT-CFG-003 | R-0173, R-0266 |
| CT-CFG-004 | R-0178, R-0179, R-0180, R-0182, R-0267, R-0281 |
| CT-CFG-005 | R-0181, R-0281 |
| CT-CFG-006 | R-0022, R-0186, R-0275 |
| CT-CFG-007 | R-0084, R-0277, R-0285 |
| CT-CFG-008 | R-0163, R-0280 |
| CT-CFG-009 | R-0154, R-0278 |
| CT-CFG-010 | R-0214, R-0215, R-0271, R-0283 |
| CT-CFG-011 | R-0160, R-0409 |
| CT-CFG-012 | R-0277 |
| CT-CFG-013 | R-0277 |
| CT-CFG-014 | R-0392, R-0409 |
| CT-CFG-015 | R-0408 |
| CT-CFG-016 | R-0393, R-0410 |
| CT-CFG-017 | R-0063, R-0196, R-0318 |
| CT-CFG-018 | R-0282 |
| CT-CFG-019 | R-0082, R-0174 |
| CT-CFG-020 | R-0130 |
| CT-CFG-021 | R-0152 |
| CT-CFG-022 | R-0158, R-0279, R-0161 |
| CT-CFG-023 | R-0172 |
| CT-CFG-024 | R-0221 |
| CT-CFG-025 | By case: .01 R-0129; .02 R-0137; .03 R-0138; .04 R-0139; .05 R-0140; .06 R-0142; .07 R-0151; .08 R-0155; .09 R-0175; .10 R-0176; .11 R-0177; .12 R-0185; .13 R-0187; .14 R-0216; .15 R-0217; .16 R-0218; .17 R-0219; .18 R-0213; .19 R-0195; .20 R-0198; .21 R-0199; .22 R-0202; .23 R-0203; .24 R-0211; .25 R-0132 |
| CT-EXE-001 | R-0048 |
| CT-EXE-002 | R-0057, R-0162 |
| CT-EXE-003 | R-0055 |
| CT-EXE-004 | R-0056, R-0283 |
| CT-EXE-005 | R-0056 |
| CT-EXE-006 | R-0054, R-0212 |
| CT-EXE-007 | R-0023, R-0024, R-0029, R-0049, R-0317 |
| CT-EXE-008 | R-0023 |
| CT-EXE-009 | R-0053 |
| CT-EXE-010 | R-0063 |
| CT-EXE-011 | R-0058 |
| CT-EXE-012 | R-0059 |
| CT-ASM-001 | R-0021, R-0067 |
| CT-ASM-002 | R-0021, R-0030 |
| CT-ASM-003 | R-0006, R-0025, R-0026, R-0027, R-0066 |
| CT-ASM-004 | R-0007, R-0072 |
| CT-ASM-005 | R-0032 |
| CT-ASM-006 | R-0286, R-0287, R-0333, R-0334, R-0335, R-0336, R-0337, R-0338, R-0339, R-0340, R-0341, R-0418 |
| CT-ASM-007 | R-0286 |
| CT-ASM-008 | R-0079, R-0343 |
| CT-ASM-009 | R-0006, R-0064 |
| CT-ASM-010 | R-0065 |
| CT-ASM-011 | R-0073, R-0083 |
| CT-ASM-012 | R-0005, R-0337 |
| CT-ASM-013 | R-0076, R-0291, R-0342 |
| CT-ASM-014 | R-0303 |
| CT-ASM-015 | R-0079 |
| CT-ASM-016 | R-0068, R-0070 |
| CT-ASM-017 | R-0069 |
| CT-ASM-018 | R-0071 |
| CT-ASM-019 | R-0074, R-0425 |
| CT-DEC-001 | R-0243, R-0244, R-0245, R-0246, R-0247, R-0248, R-0249, R-0324, R-0396 |
| CT-DEC-002 | R-0036, R-0037, R-0293, R-0324 |
| CT-DEC-003 | R-0325 |
| CT-DEC-004 | R-0041, R-0294 |
| CT-DEC-005 | R-0273, R-0304 |
| CT-DEC-006 | R-0031, R-0045, R-0305, R-0344 |
| CT-DEC-007 | R-0045, R-0305, R-0343, R-0344 |
| CT-DEC-008 | R-0273, R-0304 |
| CT-DEC-009 | R-0344 |
| CT-DEC-010 | R-0301 |
| CT-DEC-011 | R-0045 |
| CT-DEC-012 | R-0299, R-0300, R-0413, R-0414 |
| CT-DEC-013 | R-0079, R-0413, R-0415 |
| CT-DEC-014 | R-0299 |
| CT-DEC-015 | R-0040, R-0290, R-0302, R-0319 |
| CT-DEC-016 | R-0088 |
| CT-DEC-017 | R-0040, R-0246, R-0320 |
| CT-DEC-018 | R-0299, R-0413, R-0415 |
| CT-DEC-019 | R-0035 |
| CT-DEC-020 | R-0034 |
| CT-DEC-021 | R-0038 |
| CT-DEC-022 | R-0411, R-0419 |
| CT-DEC-023 | R-0411, R-0419 |
| CT-REL-001 | R-0039, R-0042, R-0311, R-0230, R-0231, R-0232, R-0233, R-0234, R-0235, R-0236, R-0237, R-0238, R-0239, R-0240, R-0241, R-0394 |
| CT-REL-002 | R-0042, R-0043, R-0220 |
| CT-REL-003 | R-0039, R-0098, R-0220 |
| CT-REL-004 | R-0308 |
| CT-REL-005 | R-0310, R-0326 |
| CT-REL-006 | R-0043, R-0249, R-0306 |
| CT-REL-007 | R-0044, R-0111, R-0307 |
| CT-REL-008 | R-0323, R-0329, R-0330, R-0306 |
| CT-REL-009 | R-0329, R-0330 |
| CT-REL-010 | R-0046, R-0242, R-0309, R-0326 |
| CT-REL-011 | R-0309 |
| CT-REL-012 | R-0309, R-0419 |
| CT-REL-013 | R-0250, R-0251, R-0252, R-0253, R-0254, R-0255, R-0256, R-0257, R-0315 |
| CT-REL-014 | R-0247 |
| CT-REL-015 | R-0329, R-0330 |
| CT-REL-016 | R-0311, R-0329, R-0330 |
| CT-REL-017 | R-0105, R-0226, R-0312 |
| CT-REL-018 | R-0107, R-0237, R-0314, R-0395, R-0412, R-0407 |
| CT-REL-019 | R-0103, R-0328 |
| CT-REL-020 | R-0106, R-0313 |
| CT-REL-021 | R-0094, R-0311, R-0222, R-0223, R-0224, R-0225, R-0226, R-0227, R-0228, R-0229 |
| CT-REL-022 | R-0108, R-0298, R-0346, R-0347 |
| CT-REL-023 | None in the inventory: Volume XII, Traceability, states this without MUST |
| CT-REL-024 | R-0015, R-0113 |
| CT-REL-025 | R-0114 |
| CT-REL-026 | R-0017, R-0018 |
| CT-REL-027 | R-0016 |
| CT-REL-028 | R-0327, R-0328 |
| CT-REL-029 | R-0098, R-0099, R-0100, R-0426, R-0427, R-0428, R-0429, R-0430, R-0431 |
| CT-REL-030 | R-0329, R-0330 |
| CT-REL-031 | R-0397, R-0398, R-0399, R-0400, R-0401, R-0402, R-0403, R-0404, R-0405, R-0406, R-0416, R-0417 |
| CT-REL-032 | R-0102 |
| CT-REL-033 | R-0104 |
| CT-REL-034 | R-0284 |
| CT-REL-035 | R-0097, R-0431 |
| CT-REL-036 | R-0101 |
| CT-REL-037 | R-0112 |
| CT-ADM-001 | R-0435, R-0436, R-0437, R-0439 |
| CT-ADM-002 | R-0436, R-0439, R-0440 |
| CT-ADM-003 | R-0436, R-0438, R-0440 |
| CT-ADM-004 | R-0436, R-0441 |
| CT-ADM-005 | R-0441 |
| CT-ADM-006 | R-0441 |
| CT-ADM-007 | R-0304, R-0441 |
| CT-API-001 | R-0331, R-0332 |
| CT-API-002 | R-0348, R-0349 |
| CT-HRV-001 | R-0183 |
| CT-HRV-002 | R-0184, R-0414 |
| CT-HRV-003 | R-0078 |
| CT-HRV-004 | R-0032 |
| CT-HRV-005 | R-0078, R-0414 |
| CT-HRV-006 | R-0420, R-0421, R-0422 |
| CT-MJG-001 | R-0075, R-0188, R-0189 |
| CT-MJG-002 | R-0190, R-0191, R-0192, R-0268, R-0269 |
| CT-MJG-003 | R-0193, R-0194 |
| CT-MJG-004 | R-0270 |
| CT-MJG-005 | R-0076 |
| CT-MJG-006 | R-0076, R-0191, R-0192 |
| CT-MJG-007 | R-0077 |
| CT-MJG-008 | R-0291, R-0292 |
| CT-MJG-009 | R-0292 |
| CT-SCT-001 | R-0089, R-0164, R-0166, R-0167 |
| CT-SCT-002 | R-0168, R-0169, R-0170, R-0264, R-0265 |
| CT-SCT-003 | R-0090, R-0289 |
| CT-SCT-004 | R-0090, R-0289, R-0423 |
| CT-SCT-005 | R-0092, R-0133, R-0134, R-0135, R-0165, R-0262, R-0263 |
| CT-SCT-006 | R-0091, R-0136, R-0288 |
| CT-SCT-007 | R-0087, R-0321, R-0322 |
| CT-SCT-008 | R-0299, R-0415, R-0424 |
| CT-SCT-009 | R-0166, R-0432, R-0433, R-0434 |
| CT-SCT-010 | R-0088, R-0319 |
| CT-SCT-011 | R-0040, R-0302, R-0305, R-0319 |
| CT-SCT-012 | R-0289 |
| CT-SCT-013 | R-0289, R-0423 |
| CT-SCT-014 | R-0299, R-0415, R-0424 |
| CT-SCT-015 | R-0040, R-0320 |
| CT-ABD-001 | R-0050, R-0141, R-0295 |
| CT-ABD-002 | R-0143, R-0144, R-0145, R-0146, R-0148, R-0149, R-0150 |
| CT-ABD-003 | R-0051, R-0060, R-0296 |
| CT-ABD-004 | R-0060, R-0296 |
| CT-ABD-005 | R-0050 |
| CT-ABD-006 | R-0147, R-0297 |
| CT-ABD-007 | R-0052 |
| CT-DSR-001 | R-0200, R-0204, R-0205 |
| CT-DSR-002 | R-0201, R-0206, R-0207, R-0208, R-0209, R-0210 |
| CT-DSR-003 | R-0063, R-0282 |
| CT-DSR-004 | R-0158, R-0279 |
| CT-PLG-001 | R-0122, R-0384 |
| CT-PLG-002 | R-0123 |
| CT-PLG-003 | R-0126 |
| CT-PLG-004 | R-0127, R-0345 |
| CT-PLG-005 | R-0121 |
| CT-PLG-006 | R-0124 |
| CT-PLG-007 | R-0125 |
| CT-SDK-001 | R-0115, R-0316, R-0383 |
| CT-SDK-002 | R-0316, R-0352, R-0359, R-0383 |
| CT-RUI-001 | R-0116 |
| CT-RUI-002 | R-0117, R-0118 |
| CT-RUI-003 | R-0119 |
| CT-RUI-004 | R-0120 |
| CT-TTP-001 | R-0095, R-0379 |
| CT-TTP-002 | R-0047 |
