# C025-E2R — Narrow-ER extension-count reduction

**Status:** `REDUCTION_PROVED`, using the external theorem `ER3 p-simulates ER`.

Let `F` be an UNSAT CNF of explicit encoded length `N`, with `n0 <= N` root variables and `m <= N` root clauses. Suppose an `ER3` refutation of `F` uses `K` extension variables. Put `V=n0+K`.

Every extension contributes three width<=3 definitional clauses, and every Resolution-derived clause in `ER3` has width<=3. The number of distinct width<=3 clauses over `V` variables is at most

```text
1 + 2V + C(2V,2) + C(2V,3) = O(V^3).
```

For any finite refutation, retain only the earliest derivation of each distinct clause and redirect later uses to it. This preserves validity and acyclicity. Therefore some DAG refutation exists with size

```text
O(m + K + V^3)
= O(N + K + (N+K)^3)
```

up to ordinary logarithmic encoding factors.

Hence if every UNSAT CNF has some `ER3` refutation with `K(F) <= N^c`, then every UNSAT CNF has a polynomial-size ER/B2 certificate.

Conversely, if global B2/ER p-boundedness holds, transform a polynomial-size ER proof to `ER3` using the known p-simulation. The transformed proof has polynomial size and therefore only polynomially many extension-definition steps/variables.

Thus, up to polynomial translations,

```text
GLOBAL B2/ER P-BOUNDEDNESS
<=>
UNIVERSAL POLYNOMIAL EXTENSION-COUNT BOUND IN SOME ER3 REFUTATION.
```

This refactors E2 into the structural target

```text
Does there exist fixed c,N0 such that every UNSAT CNF F of length N>=N0
admits some ER3 refutation with K(F) <= N^c extension variables?
```

The target remains open and is equivalent to the global strong-proof-system frontier, but the undifferentiated proof-size resource has been reduced to a single explicit resource: extension count.

Status:

```text
C025_E2A_B2_ER_P_EQUIVALENCE            = PROVED
C025_E2R_ER3_NORMALIZATION              = EXTERNAL_THEOREM
C025_E2R_CLAUSE_UNIVERSE_BOUND          = PROVED
C025_E2R_DUPLICATE_ELIMINATION          = PROVED
C025_E2R_POLY_K_IMPLIES_POLY_PROOF      = PROVED
C025_E2R_GLOBAL_EQUIVALENCE             = PROVED
C025_E2R_UNIVERSAL_POLY_EXTENSION_COUNT = OPEN
P_VS_NP                                 = OPEN
```
