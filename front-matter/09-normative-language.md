# 9. Normative Language

**Status:** confirmed (v0.1).

This specification uses RFC 2119 keywords, restricted to a deliberately small set: five
core words and two synonyms, not the full RFC 2119 vocabulary.

**MUST** — An absolute requirement. Conformance (§10) treats every MUST as binding on
whichever capability of an implementation it applies to.

**MUST NOT** — An absolute prohibition, the negation of MUST, with the same binding
force.

**SHOULD** (synonym: **RECOMMENDED**) — A strong expectation that MAY be deviated from,
but only as a deliberate, understood choice. Conformance (§10) does not require a SHOULD
to be followed, only that deviating from one is a choice, not an oversight nobody
noticed.

**SHOULD NOT** — The negation of SHOULD, with the same allowance for deliberate,
understood deviation.

**MAY** (synonym: **OPTIONAL**) — Genuinely discretionary. An implementation is equally
conformant whether or not it takes the option.

## Why Not the Full RFC 2119 Vocabulary

RFC 2119 also offers SHALL, SHALL NOT, and REQUIRED as synonyms for MUST and MUST NOT.
This specification does not use them: every Volume and Appendix uses MUST and MUST NOT
exclusively for that meaning, so a reader is never left wondering whether SHALL was
chosen deliberately to signal something MUST does not. This section records that pattern
rather than imposing a new one — it was already true of how every Volume used these
keywords before this section existed to confirm it.

## Scope of Normative Force

A MUST, SHOULD, or MAY carries the same force wherever it appears in a Volume or
Appendix's own prose — Front Matter, a Volume's main text, and a Chapter within Volume I
are not different tiers of obligation. It does not carry that force in
`_project-notes/decisions-log.md` or in `index.md`'s own status notes, both of which
index.md already marks as working records, not part of the published document: where a
decisions-log entry restates a requirement using MUST, it is cross-referencing an
obligation that lives in the Volume it cites, not creating a second, independent one.

---

With Normative Language defined, Conformance's (§10) own forward reference to this
section is resolved. Preface (§4), Purpose (§5), and Scope (§6) remain the natural next
sections — each can now draw on the complete
seventeen-Volume argument instead of pre-stating it.
