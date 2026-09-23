# JANUS GLOBAL PRE-MATH NO-DUPLICATION GATE

Date: 2026-09-24

Authority: GLOBAL_RESEARCH_GOVERNANCE__MANDATORY_FOR_ALL_POST_ACTIVATION_P_VS_NP_WORK

Activation baseline commit:
`a3413bcb3bb4a5192166212ef81b7506f2a440ca`

This policy promotes the earlier local E8 corpus-first / anti-duplication doctrine into a repository-wide mandatory gate.

## 1. What this rule guarantees

This rule does NOT guarantee that a mathematical idea succeeds.

It DOES guarantee a process invariant:

NO NEW THEOREM / CANDIDATE / FRONTIER / EXPERIMENTAL MECHANISM MAY BEGIN OR BE PROMOTED UNTIL ITS PRE-MATH AUDIT IS COMPLETE.

The purpose is to prevent JANUS from repeatedly:

- rediscovering external literature under a new vocabulary;
- rediscovering earlier JANUS results under new notation;
- proving a special case already covered by a stronger known theorem;
- building a checker for an object whose canonical form is already classified;
- mistaking a normal-form translation for new algorithmic progress.

## 2. Mandatory order

For every post-activation mathematical object, execute these gates in order.

### G0 — Freeze the exact object

Write the mathematical contract before searching:
- domain / input class;
- output / decision problem;
- exact semantics;
- allowed transformations;
- witness reconstruction contract;
- complexity target;
- exact claim being considered.

No vague phrase such as 'new quotient', 'new symmetry', or 'new compression' is audit-ready.

### G1 — Internal anti-duplication search

Search Janus-Fundamentum, relevant registries, historical docs and known sibling repositories using:
- current JANUS name;
- algebraic/graph/CSP aliases;
- structural synonyms;
- older terminology;
- the intended theorem conclusion rather than only the current object name.

Record search terms and every materially close internal artifact.

If an existing JANUS theorem/candidate already covers the object, STOP and reuse/bind it.

### G2 — Canonical external naming

Translate the object into standard mathematical vocabulary BEFORE inventing new mathematics.

Record at least:
- canonical problem/object name;
- at least three useful aliases / neighboring formulations when they exist;
- the external field(s) in which the object lives.

Examples:
- three-translate exact cover -> perfect code / efficient domination / group tiling;
- row-side potential -> gain/voltage graph potential;
- two-permutation action -> Cayley/Schreier/permutation digraph;
- exact Boolean relation -> CSP relation / polymorphism language.

### G3 — Public-source exhaustion

Search current primary literature under the canonical names.

Minimum audit for a mathematical NEW_MATH request:
- at least three distinct external queries;
- at least two primary or authoritative sources when available;
- one search for stronger/general results;
- one search for lower bounds / impossibility / complexity classification;
- one search for the exact special class JANUS currently has.

Secondary sources may help discovery but cannot be the sole scientific authority when a primary source is accessible.

### G4 — Collision matrix

Classify every close result as one of:

`EXACT_COLLISION`
`STRONGER_KNOWN_RESULT`
`SPECIAL_CASE_COLLISION`
`JANUS_REDERIVATION`
`KNOWN_DONOR_ONLY`
`KNOWN_BARRIER_ONLY`
`SCOPED_GAP_SURVIVES`
`NO_CLOSE_RESULT_FOUND`.

Required action:
- EXACT_COLLISION / STRONGER_KNOWN_RESULT -> STOP new theorem; source-bind the known result;
- JANUS_REDERIVATION -> keep only as independent replay/corollary, never novelty;
- SPECIAL_CASE_COLLISION -> narrow the JANUS scope explicitly;
- audit uncertainty -> HOLD; do not promote;
- only SCOPED_GAP_SURVIVES / NO_CLOSE_RESULT_FOUND may authorize genuinely new mathematics.

## 3. Promotion labels

Every new post-activation artifact must carry one of these classifications:

`SOURCE_BOUND`
`JANUS_REDERIVATION`
`JANUS_COROLLARY`
`JANUS_NEGATIVE_CONTROL`
`JANUS_NEW_CANDIDATE_AFTER_AUDIT`
`JANUS_NEW_BARRIER_AFTER_AUDIT`
`EDITORIAL_OR_IMPLEMENTATION_ONLY`.

Do not call something JANUS_NEW_* unless a completed audit explicitly authorizes that scope.

## 4. Hard STOP rules

STOP new mathematics immediately if:

1. a known theorem already resolves the current object at equal or greater scope;
2. an older JANUS artifact already resolves it under another representation;
3. the object is only a normal-form translation of a known problem and the translation has not exposed a strictly new algorithmic obligation;
4. the canonical external name is still unknown;
5. the literature audit status is HOLD / INCOMPLETE;
6. a source claims a complete classification of the exact class and has not yet been read/audited;
7. novelty status is being inferred from failure to find the current JANUS terminology.

## 5. Re-audit triggers

The pre-math audit MUST be repeated when any of these change materially:
- canonical object / external vocabulary;
- input class or promise;
- representation/interface;
- theorem scope;
- complexity claim;
- a new source appears that may dominate the current result;
- an internal artifact is discovered that may be a predecessor.

An old audit cannot silently authorize mathematics about a newly recognized canonical object.

## 6. Machine-enforced ledger

All post-activation changes under research/, registry/, and experiments/ must be accounted for in:

`registry/JANUS_P_VS_NP_PREMATH_AUDIT_LEDGER_2026-09-24_v1.0.json`.

The validator compares the current tree against the activation baseline.

Every changed scientific artifact must be either:
- explicitly governance-exempt;
- classified as editorial/implementation-only;
- a source-audit artifact;
- or linked to a completed audit receipt that authorizes new mathematics.

Unaccounted scientific files make CI fail.

## 7. Audit decision states

`HOLD_NEW_MATH` — canonicalization/source exhaustion incomplete; only source-audit work allowed.

`SOURCE_BOUND_REUSE` — known result covers the object; bind source and do not rederive as novelty.

`INTERNAL_REUSE` — earlier JANUS artifact covers the object.

`PASS_SCOPED_GAP_CONFIRMED` — no known result closes the precisely frozen scope; new math allowed only on that scope.

`PASS_NEW_BARRIER_SCOPE_CONFIRMED` — new falsifier/barrier work allowed on the precise scoped statement.

`EDITORIAL_ONLY` — no mathematical content change.

## 8. Current application

The current E9 object has been canonically recognized as a directed perfect-code / efficient-domination problem on a two-permutation Cayley/Schreier-style digraph.

Therefore:

`R5_E9_DIRECTED_PERFECT_CODE_KNOWN_METHOD_AUDIT_V1`

is placed in HOLD_NEW_MATH until known-method exhaustion is complete.

No further higher-representation / tiling theorem may be promoted before that audit resolves.

## 9. Scientific ceiling

`P_VS_NP = OPEN`

`D1 = EMPTY`

`PREMATH_NO_DUPLICATION_GATE = GLOBAL_MANDATORY_POST_ACTIVATION`

`NO_AUDIT = NO_NEW_MATH`
