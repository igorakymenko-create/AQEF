# 4. Preface

**Status:** confirmed (v0.1).

Chapter 1 already makes the case this document exists to make: that generative AI
systems break the assumption classical software testing has relied on since testing
existed — a fixed, deterministic oracle against which a single expected output can be
checked — and that neither narrowing "correct" to a single string nor abandoning precise
checking altogether resolves what actually changed. This Preface does not restate that
argument; it exists only to say what kind of document you are holding, and how it is
built.

The AI Quality Engineering Framework (AQEF) is a specification, not a product
recommendation or a survey of existing tools. It defines a Domain Model (Volume II), a
set of Fundamental Principles (Volume I, Chapter 3), and seventeen Volumes' worth of
mechanism built from them — Execution, Datasets, Validators, Judges, Testing
Methodology, Enterprise Architecture, Extensibility — because a discipline this
consequential needs more than a shared vocabulary to actually govern behavior. It needs
the vocabulary to cash out in specific, checkable requirements an implementation either
satisfies or does not (Conformance, §10).

The document is organized so that any future edit touches one small file rather than
the whole specification: Front Matter, then five Parts of Volumes — Foundations,
Execution, Testing Methodology, Enterprise Architecture, Extensibility — then
Appendices. Its cross-references are meant to be followed, not decorative: where a
Volume says another Volume specifies something, that something is specified there, not
gestured at and left for the reader to reconstruct. Where a term risked meaning two
different things in two different places — and across a document this size, several did
— that tension was resolved deliberately, once, rather than left for a reader to notice
later and wonder whether the difference was intentional.

Read in order, the seventeen Volumes build one continuous argument, each depending only
on what came before it. Read out of order — as most readers actually will, arriving at
a single Volume because of a specific question — every cross-reference should still
resolve: to a Chapter, a Volume, a decision already made, never to a promise that
something is specified "elsewhere" without saying where.
