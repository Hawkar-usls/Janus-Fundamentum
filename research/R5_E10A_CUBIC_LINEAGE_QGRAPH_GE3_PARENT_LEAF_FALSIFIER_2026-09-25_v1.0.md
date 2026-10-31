# R5 E10A — Cubic-Lineage q_graph >= 3 Parent-Leaf Falsifier

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_ACTUAL_LINEAGE_FALSIFIER_AFTER_PA0012__UNIVERSAL_TWO_ROW_COVERAGE_FALSIFIED__GLOBAL_SOLVER_PROMOTION_HOLD`

Authorizing audit:
`PA-0012-E10-END-TO-END-DECOMPOSITION-SOLVER-COMPOSITION-COVERAGE`

Parent gate:
`R5_E10A_CUBIC_LINEAGE_LIVE_TORSO_GRAPHIC_LIFT_CODIMENSION_COVERAGE_GATE_V1`

Checker:
`experiments/r5_e10a_cubic_lineage_qgraph_ge3_parent_leaf_falsifier.py`

## 1. Purpose

PA-0012 left exactly two exits:

A. prove constructive `q_graph<=2` for every actual unresolved cubic-lineage leaf; or  
B. exhibit one actual cubic-origin, source-valid terminal leaf with `q_graph>=3`.

This artifact closes exit B.

It does **not** prove a solver for the higher-lift leaf and does not promote the global E10 solver.

## 2. Explicit cubic parent

Take `n=15` and the cyclic permutation matrix `P). Define

```
H = I + P + P^4   over GF(2)
f = 1
M = M([H|f]).
```

The shifts `0,1,4` are distinct modulo 15, so every row and every column of `H` has weight exactly three. This is therefore an exact cubic positive Exact-One parent of the frozen lineage.

The checker obtains

```
|E(M)| = 16
r(M)   = 11
g*(M)  = 4.
```

The weight-four cocycles are consistent with the NM-0010 cubic star.

## 3. q_graph >= 3 certificate

If `q_graph(M)<=2`, then `C*(M)` contains a graphic cut subspace of dimension at least `r(M)-2`.

Choose a reduced incidence basis for that graphic cut space. Every basis row is a nonzero cocycle of `M`, hence has weight at least `g*(M)`, while every ground-set column contributes to at most two incidence rows. Therefore

```
(r(M)-2) g*(M) <= 2 |E(M)|.
```

For this parent,

```
(11-2)*4 = 36 > 32 = 2*16.
```

Hence

```
q_graph(M) >= 3.
```

This is a theorem-level obstruction; no recognition search is hidden in the certificate.

## 4. Source-valid terminal-leaf status

The checker exhaustively evaluates the binary connectivity function

```
lambda(X)=r(X)+r(E-X)-r(M).
```

It finds:

```
1/2-separations = 0
exact 3-separations with both sides >=3 = 0.
```

Thus `M` is 3-connected and has no further standard exact 3-separation on which the source-valid binary 3-sum decomposition can split it.

So the cubic parent itself is a legitimate terminal leaf; no external leaf materializer is needed for this falsifier.

Truemper's binary 3-sum language source-binds the equivalence between suitable exact 3-separations and nontrivial 3-sums in the 3-connected binary setting.

## 5. Explicit S8 minor

Label the fifteen ordinary columns `x0,...,x14` and the distinguished column `f`.

Contract

```
C={x0,x1,x2,x3,x4,x5,x7}
```

and delete

```
x8.
```

Retain, in order,

```
(x6,x9,x10,x11,x12,x13,x14,f).
```

In an explicit quotient basis the eight retained columns are

```
(1,4,8,2,7,12,9,15) in GF(2)^4.
```

For the standard S8 point set

```
(1,2,4,8,14,13,11,15),
```

the invertible linear map whose basis images are

```
(e1,e2,e3,e4) -> (1,4,15,2)
```

maps that set exactly onto the retained quotient set.

Therefore `M` contains an `S8` minor.

## 6. Source-bound terminal lanes are not the explanation

### no-S8

Excluded immediately by the explicit S8 minor.

### graphic / even-cycle

An even-cycle representation is a one-row lift of a graphic matroid. Since this leaf has `q_graph>=3`, it is neither graphic nor even-cycle.

This uses only the canonical source language: even-cycle matroids are elementary one-row lifts of graphic matroids.

### graft

A supplied graft representation has one distinguished graft column whose deletion leaves a graphic matroid.

For every element `e` of this parent, the checker proves

```
r(M\e)=11
g*(M\e)=3.
```

If `M\e` were graphic, simplicity and `r=11,m=15` would give a simple graph with `v-c=11`. Its average degree is below three, so some non-isolated vertex has degree at most two; its incident cut contains a bond of size at most two. That would force cogirth at most two, contradicting `g*=3`.

Thus no single-element deletion is graphic, so the graft terminal lane does not apply.

### even-cut / cographic-side elementary lift

An even-cut representation has row space

```
cycle(G) + span{S}.
```

Therefore `cycle(G)` would be a subspace of `C*(M)` of dimension at least `r(M)-1=10`.

Since `g*(M)=4`, that graph can have no loop, parallel pair, or triangle; it is simple and triangle-free. With 16 edges and cycle-space dimension at least 10, its graphic cut rank is at most six.

For a simple triangle-free graph with total component rank at most six, the componentwise Mantel bound gives at most 12 edges. The checker verifies the finite integer partition maximum:

```
max edges = 12 < 16.
```

Contradiction. Hence the leaf is not even-cut. Cographic is the special `T=empty` case and is excluded as well.

## 7. Gate verdict

Freeze:

```
R5_E10A_CUBIC_LINEAGE_LIVE_TORSO
_GRAPHIC_LIFT_CODIMENSION_COVERAGE_GATE_V1

EXIT A:
UNIVERSAL CONSTRUCTIVE q_graph<=2
=
FALSIFIED

EXIT B:
ACTUAL CUBIC-ORIGIN SOURCE-VALID TERMINAL LEAF
WITH q_graph>=3
=
PASS
```

Equivalently,

```
CUBIC LINEAGE
DOES NOT STAY
INSIDE THE TWO-ROW GRAPH-LIFT CLASS.
```

This does not invalidate NM-0013--NM-0016. Those remain exact deterministic polynomial solvers for the two-row covered branch. It proves only that they are not end-to-end coverage for all cubic-origin leaves.

## 8. New scientific frontier

The object has changed. No further mathematics on the `q_graph>=3` live-leaf class is authorized without a new source audit.

Freeze next required audit:

```
PA-0013
CUBIC-LINEAGE HIGHER-LIFT
LIVE-LEAF SOURCE AUDIT
```

Required before new mathematics:

- canonical algorithms/recognition for fixed `m>=3` lifts of graphic matroids;
- whether the present explicit parent has a smaller alternative tractable representation not captured by `q_graph`;
- whether cubic-star structure gives a bounded higher-lift solver currency;
- whether a source hardness/tractability result already covers the exact distinguished lower-bound-tight objective.

## 9. Scientific ceiling

```
ACTUAL LINEAGE q_graph>=3 LEAF
=
PROVED

UNIVERSAL TWO-ROW COVERAGE
=
FALSIFIED

NM-0013..NM-0016
=
VALID CONDITIONAL BRANCH

HIGHER-LIFT LEAF SOLVER
=
NOT AUDITED

GLOBAL E10 SOLVER PROMOTION
=
HOLD

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
