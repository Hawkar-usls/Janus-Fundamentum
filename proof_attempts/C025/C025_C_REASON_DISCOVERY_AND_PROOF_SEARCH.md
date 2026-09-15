# C025-C — Deterministic Reason Discovery and Proof-Search Cost

**Status:** cache-query theorem derived; executable parity pending; new-reason generation and global proof search remain open.

**Claim ceiling:** no polynomial-SAT or P-vs-NP conclusion follows from this document.

## C1 — existing certified-reason query

For partial assignment `rho`, let `FALSE(rho)` contain the unique false literal of every assigned variable. A certified clause reason `C` applies iff

```text
C subseteq FALSE(rho).
```

Maintain for every cached reason `C_i`

```text
false_count[i] = |C_i intersect FALSE(rho)|
```

and for every literal `l` an occurrence list of reason ids containing `l`. Assignment of a variable touches exactly the occurrence list of the literal made false. A reason is applicable iff `false_count[i] = |C_i|`.

### Lemma C1 — exactness

The counter index reports a reason iff the current assignment falsifies every literal of that reason. □

### Lemma C2 — monotone update bound

Let `M = sum_i |C_i|` be total explicit reason-cache literal volume. Along a monotone assignment path where each variable is assigned at most once, total forward counter updates are at most `M`.

**Proof.** Each stored literal occurrence can be touched only when its variable receives the unique value falsifying that literal, hence at most once. □

Trail rollback performs exactly the inverse touched updates.

Therefore cached-reason applicability is polynomial in explicit cache volume `M`.

## Input-relative boundary

This does **not** imply polynomial lookup in original input size `N` unless C025-E / Issue #212 independently proves `M <= N^a` (or an equivalent polynomial representation theorem).

```text
FAST_INDEX_IN_M != M_IS_POLYNOMIAL_IN_N
```

## C2 — new-reason generation / global proof search

Still open: given no applicable cached reason, prove the frozen deterministic Policy-0B discovers useful conflicts/reasons in total `poly(N)` work, or refute that policy with an explicit infinite family.

A short proof or proof-system p-simulation is not enough:

```text
SHORT_PROOF_EXISTS != DETERMINISTIC_POLICY_FINDS_IT_IN_POLYTIME
```

All failed branches/states, inference work, propagation, reason construction, indexing, rollback, certificate materialization and verification must be charged.

## Coupled frontier

```text
C025_C1_CACHE_QUERY_CORRECTNESS          = PROVED
C025_C1_COST_IN_EXPLICIT_CACHE_VOLUME    = PROVED
C025_C1_COST_IN_ORIGINAL_INPUT_N         = CONDITIONAL_ON_C025_E
C025_C2_NEW_REASON_GENERATION            = OPEN
C025_C2_GLOBAL_DETERMINISTIC_PROOF_SEARCH = OPEN
C025_E_TOTAL_REASON_CACHE_AND_DAG_SIZE   = OPEN
P_VS_NP                                  = OPEN
```

Canonical design/process source: `Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_C_REASON_DISCOVERY_AND_PROOF_SEARCH.md`.
