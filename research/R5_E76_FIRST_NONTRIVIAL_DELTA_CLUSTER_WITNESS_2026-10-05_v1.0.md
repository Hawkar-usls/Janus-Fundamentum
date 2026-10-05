# R5 E76 — First Nontrivial Delta-Cluster Witness Beyond the E75 Radius

Date: 2026-10-05

Status:
`EXPLICIT_13_VERTEX_C4FREE_CLUSTER_HAS_LINEAR_DELTA_BOUNDARY__E75_BARRIER_IS_FINITE_RADIUS_NOT_UNIVERSAL`

Scientific ceiling:

```text
E76 IS A POSITIVE LOCAL ALGEBRAIC WITNESS, NOT A UNIVERSAL POLYNOMIAL SOLVER.
P_VS_NP REMAINS OPEN.
```

## 1. Why E76 matters

E74 proved that the single Equality_3 star, the canonical strong-C5 interface,
and the complete E53 one-gadget quotient are non-delta.  E75 then exhausted
101210 connected C4-free cluster topologies through nine Tanner vertices and
found no nontrivial delta boundary support.

A natural conjecture was that every proper connected cluster containing the
Equality_3 atom might remain non-delta.  E76 disproves that conjecture with an
explicit finite witness.

## 2. The 13-vertex cluster

Take seven check vertices `C0,...,C6` and six variable vertices `V0,...,V5`
with internal edges

```text
(6,3), (2,1), (4,4), (0,3), (0,5), (3,4), (1,4), (3,1),
(1,0), (1,3), (4,5), (0,1), (5,2), (6,2), (4,2), (5,0).
```

The graph is connected, bipartite, simple, C4-free, and has internal degree at
most three.  Missing incidences are boundary stubs, exactly as in E75.

With ExactOne_3 on the check side and Equality_3 on the variable side, exact
projection to the seven boundary stubs gives

```text
boxed:
F = {117,118}.
```

The two masks differ only on boundary bits zero and one:

```text
117 xor 118 = 3.
```

Thus the boundary relation is genuinely nontrivial but has only one binary
degree of freedom.

## 3. It is a linear even delta-matroid

Twist by feasible set 117:

```text
F * 117 = {0,3}.
```

On a seven-element ground set, let `M` be zero except for the 2x2 skew block
on coordinates 0 and 1,

```text
[ 0  1]
[-1  0].
```

The nonsingular principal submatrices occur exactly on

```text
empty set,
{0,1}.
```

Hence the principal-nonsingularity delta-matroid of `M` is exactly `{0,3}`.
Twisting back by 117 recovers `{117,118}`.

Therefore the E76 cluster boundary is not merely a delta-matroid: it is an
explicit **linear even delta-matroid** in the standard skew-symmetric sense.

This is algorithmically meaningful because linear delta-matroids support
polynomial matrix algorithms; see Koana and Wahlstroem, STACS 2025,
DOI `10.4230/LIPIcs.STACS.2025.62`.

## 4. Realization inside a genuine square-cubic-linear carrier

The checker freezes the following 9x9 incidence matrix:

```text
0 1 0 1 0 1 0 0 0
1 0 0 1 1 0 0 0 0
0 1 0 0 0 0 1 1 0
0 1 0 0 1 0 0 0 1
0 0 1 0 1 1 0 0 0
1 0 1 0 0 0 1 0 0
0 0 1 1 0 0 0 1 0
1 0 0 0 0 0 0 1 1
0 0 0 0 0 1 1 0 1
```

Every row and column has weight three, every pair of columns meets in at most
one row, and the Tanner graph is connected.  The induced subgraph on rows
0..6 and columns 0..5 is exactly the 13-vertex E76 cluster above.

So the witness is not an abstract topology that fails to complete to the R5
carrier class: it occurs inside an actual connected square-cubic-linear
instance.

The full 9x9 carrier is Exact-One UNSAT by exhaustive replay.  Therefore a local
linear-delta repair does not by itself imply global satisfiability.

## 5. Relation to E75

E75 remains correct exactly as stated: it is a finite-radius barrier through
nine Tanner vertices.  E76 shows that one must not extrapolate it to all bounded
clusters.

The current picture is therefore:

```text
size <= 9:
    no nontrivial delta boundary cluster;

size 13:
    explicit nontrivial linear-delta boundary cluster exists.
```

E76 does not claim that 13 is minimal.  Sizes 10--12 have not been exhaustively
classified by this theorem.

## 6. What this opens

For the first time after E74/E75, the exterior/matching direction has a positive
local object rather than only obstructions.

The useful question is no longer whether every bounded cluster is non-delta.
It is whether clusters of the E76 type can be composed so that an arbitrary
E12 hardness target is covered or reduced while keeping total interface rank
polynomially controlled.

Three requirements are mandatory:

```text
1. every contraction step must preserve Exact-One support exactly;
2. the residual boundary relation must remain represented by polynomial-size
   linear/projected-linear delta-matroid data;
3. the decomposition/selection of clusters must itself be polynomial-time on
   every E12 target.
```

A single useful cluster is not enough.  A universal polynomial proof would need
a global covering/composition theorem.

## 7. Replay

Companion checker:

```text
experiments/r5_e76_first_nontrivial_delta_cluster_witness.py
```

It verifies:

```text
* exact projected relation F={117,118};
* Bouchet symmetric exchange;
* twist F*117={0,3};
* exact 2x2 skew-symmetric principal-minor representation;
* square/cubic/linear/connected 9x9 completion;
* induced occurrence of the cluster in that completion;
* full completion Exact-One UNSAT by exhaustive search.
```

Scientific status:

```text
E76 = PROVED POSITIVE LOCAL LINEAR-DELTA WITNESS.
GLOBAL_POLYNOMIAL_COMPOSITION = OPEN.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```
