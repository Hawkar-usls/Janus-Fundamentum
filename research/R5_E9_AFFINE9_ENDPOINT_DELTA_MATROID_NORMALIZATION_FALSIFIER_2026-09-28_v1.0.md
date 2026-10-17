# R5 E9 — AFFINE_3X3 Endpoint Delta-Matroid Normalization Falsifier

Date: 2026-09-28

Status: `JANUS_EXHAUSTIVE_FINITE_HOSTILE_CONTROL__DIRECT_ENDPOINT_PROJECTED_DM_NORMALIZATION_ROUTE_FALSIFIED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_CYCLE_SYNDROME_HOMOLOGY_DELTA_MATROID_BOUNDARY_2026-09-28_v1.0.md`
- `research/R5_E9_MATCHING_NORMALIZED_CYCLE_2FACTOR_EXACTONE_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_affine9_endpoint_delta_matroid_normalization_falsifier.py`

Scientific ceiling:

```text
THIS IS A COMPLETE FINITE FALSIFIER OVER EVERY PERFECT-MATCHING NORMALIZATION
OF ONE FROZEN SAT 9_3 CONTROL.
IT DOES NOT RULE OUT EVERY POSSIBLE GLOBAL AUXILIARY DELTA-MATROID REDUCTION.
IT DOES RULE OUT THE DIRECT ENDPOINT-FAMILY ROUTE RESCUED MERELY BY CHOOSING
A DIFFERENT MATCHING NORMALIZATION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen SAT control

Use the affine `9_3` configuration consisting of the three row classes, three
column classes, and three slope-`+1` classes of `Z_3^2`.

Its incidence matrix is square, linear and cubic, and has exactly three Boolean
Exact-One witnesses.

## 2. Enumerate every matching normalization

A matching normalization chooses a perfect matching of the cubic bipartite Levi
graph and relabels the matched row/column pairs as the identity part of

```text
A = I + P + Q.
```

The checker exhaustively enumerates all perfect matchings of this frozen Levi
graph.  There are exactly

```text
42
```

of them.

For each normalization, form the unmatched-pair graph `C_M`.  Linearity makes it
a simple 2-factor.

The complete census is

```text
36 normalizations: C_M is one 9-cycle;
 6 normalizations: C_M is three disjoint 3-cycles.
```

## 3. Convert exact witnesses to matching endpoint sets

On each cycle component choose an orientation and identify each `C_M` vertex with
the correspondingly indexed edge of an isomorphic cycle.  An independent set in
`C_M` then becomes a graph matching.

For every one of the three Exact-One witnesses, record the set of endpoints of
the corresponding matching.  Call the resulting family `F_endpoint(M)` for the
chosen perfect-matching normalization `M`.

Every source witness has three selected variables, so every endpoint set has size
six.  Consequently, if `F_endpoint(M)` were a delta-matroid then, because all its
feasible sets are equicardinal, it would in fact be the basis family of a matroid.
The checker tests the stronger delta-matroid symmetric-exchange axiom directly.

## 4. Exhaustive result

For every one of the 42 perfect-matching normalizations,

```text
F_endpoint(M)
is NOT a delta-matroid.
```

Equivalently,

```text
normalizations checked             = 42
normalizations with DM endpoint set = 0
```

For each normalization the checker produces an explicit pair `X,Y` of endpoint
sets and `e in X triangle Y` for which no allowed symmetric exchange returns a
feasible endpoint set.

Thus the proposed rescue

```text
choose a favorable perfect matching M
-> convert cycle independence to matching
-> encode the exact syndrome solely as a projected-linear-delta-matroid family
   on the matching endpoints
-> invoke polynomial projected-linear-DM matching
```

already fails on this 9-variable satisfiable source control for **every** choice
of `M`.

Because projection of a delta-matroid remains a delta-matroid, a non-delta-
matroid endpoint family cannot itself be a projected linear delta-matroid.

## 5. Scope of the falsifier

This does not exclude a more elaborate polynomial construction that:

- enlarges the matching graph;
- introduces auxiliary elements whose interaction with matching is essential;
- uses a different ground set rather than the literal endpoint family; and
- proves an exact polynomial reconstruction theorem.

Such a construction would be genuinely new.  What is closed is the direct
endpoint-constraint interpretation and the idea that a different 1-factorization
alone can make it projected-linear-DM.

## 6. Ceiling

```text
AFFINE_3X3 EXACT-ONE MODELS
= 3

PERFECT MATCHINGS OF FROZEN LEVI GRAPH
= 42 EXACTLY

C_M TYPES
= 36 x C9
+ 6 x (C3 + C3 + C3)

ENDPOINT-SYNDROME FEASIBLE FAMILY
= NOT A DELTA-MATROID FOR ALL 42 NORMALIZATIONS

DIRECT ENDPOINT PROJECTED-LINEAR-DM ROUTE
= FALSIFIED ON FROZEN SAT CONTROL

GLOBAL AUXILIARY / REPRESENTATION-CHANGING ROUTE
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
