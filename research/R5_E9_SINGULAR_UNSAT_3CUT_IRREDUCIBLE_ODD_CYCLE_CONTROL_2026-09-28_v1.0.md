# R5 E9 — Singular-UNSAT 3-cut-irreducible strong-odd-cycle control

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_HOSTILE_CONTROL__CURRENT_RESIDUAL_IS_NONEMPTY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`
- `research/R5_E9_THREE_EDGE_CUT_BOUNDARY_ALGEBRA_2026-09-28_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS IS ONE FINITE EXACT HOSTILE CONTROL INSIDE THE CURRENT RESIDUAL.
IT DOES NOT PROVE NP-HARDNESS OF THE 3-CUT-IRREDUCIBLE SUBCLASS.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen carrier

Use the connected linear cubic `15_3` carrier

```text
p = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
A = I + P + Q.
```

Its row supports are

```text
0:  {0,5,12}
1:  {1,7,9}
2:  {2,9,14}
3:  {3,10,11}
4:  {3,4,13}
5:  {1,5,10}
6:  {6,7,14}
7:  {2,3,7}
8:  {1,4,8}
9:  {0,6,9}
10: {2,10,12}
11: {5,11,13}
12: {6,8,12}
13: {0,8,13}
14: {4,11,14}.
```

The parent theorem already proves exactly

```text
rank_Q(A)=14,
nullity_Q(A)=1,
Exact-One(A)=UNSAT.
```

The primitive rational-kernel generator is

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1),
```

and no scalar multiple of `g` belongs to `{-1,2}^15`, so UNSAT does not rely on exhaustive SAT search.

## 2. Exact edge-cut census of the Levi graph

Let `L(A)` be the bipartite Levi graph with 15 row vertices and 15 column vertices. Since `A` is cubic on both shores,

```text
|V(L)|=30,
|E(L)|=45.
```

The executable certificate exhausts every subset of one, two, and three Levi edges and recomputes connected components exactly.

The result is

```text
number of 1-edge cuts = 0,
number of 2-edge cuts = 0,
number of 3-edge cuts = 30.
```

Moreover every one of the 30 three-edge cuts is exactly

```text
delta(v)
```

for one Levi vertex `v`; deleting it isolates precisely that single vertex and leaves the other 29 vertices connected.

Since there are exactly 30 Levi vertices, these are all vertex-star cuts and there are no others.

### Theorem SU3C-1

The frozen `15_3` control has no nontrivial edge cut of size at most three.

Equivalently, in the current JANUS sense it is already a

```text
3-CUT-IRREDUCIBLE CORE.
```

Its edge-connectivity is exactly three only because a cubic vertex star is always a 3-edge cut.

This is stronger than mere connectedness and shows that the new exact `<=3`-edge separator composition router cannot decompose this instance except by the explicitly forbidden trivial atom cuts.

## 3. Exact strong odd-cycle / balancedness obstruction

Restrict `A` to rows

```text
R={0,12,13}
```

and columns

```text
C={0,8,12}.
```

In the column order `(0,8,12)` the submatrix is

```text
[1 0 1]
[0 1 1]
[1 1 0].
```

This is a square matrix of odd order three with exactly two ones in every selected row and every selected column.

Therefore it is a forbidden balanced-matrix submatrix. In Levi language it is the chordless 6-cycle

```text
r0 - c12 - r12 - c8 - r13 - c0 - r0.
```

Hence `A` is unbalanced and the new balanced set-partitioning terminal correctly routes this control to the residual rather than incorrectly declaring the hard core solved.

### Theorem SU3C-2

The frozen `15_3` control simultaneously satisfies

```text
connected,
linear,
cubic,
3-cut-irreducible,
unbalanced with an explicit strong odd cycle,
rank_Q(A)=14,
Exact-One UNSAT.
```

## 4. Consequence for the current universal route

The present preprocessing stack now includes two exact polynomial simplifiers:

```text
(A) compose every genuine nontrivial <=3-edge separation;
(B) if the remaining incidence matrix is balanced, output SAT + witness.
```

The frozen `15_3` control survives both:

```text
(A) finds no nontrivial <=3-edge separation;
(B) finds the explicit strong odd cycle above and returns UNBALANCED;
instance remains UNSAT.
```

Therefore the post-preprocessing residual is provably nonempty.

The following shortcuts are hence forbidden:

```text
3-cut-irreducible + singular => SAT,
3-cut-irreducible => balanced,
unbalanced core => SAT,
separator exhaustion + rank deficiency => witness.
```

The control does not prove the residual NP-hard. It proves only that the residual contains a concrete nontrivial UNSAT member and therefore needs a genuine solver/contraction theorem.

## 5. New hostile benchmark

Freeze this exact object as the mandatory first hostile replay for

```text
R5_E9_UNBALANCED_3CUT_IRREDUCIBLE_GLOBAL_CONTRACTION_GATE_V1.
```

Any proposed universal rule acting on the unbalanced, separator-resistant core must correctly return

```text
UNSAT
```

on this instance without relying on exponential search.

Admitted next progress must be one of:

1. an exact polynomial contraction using the certified strong odd cycle and its third-incidence attachments;
2. a source-specific polynomial syndrome/coordinate representation that proves UNSAT here and remains polynomial on arbitrary residuals;
3. a different proved polynomial terminal covering this and all instances in its certified class.

## 6. Checker

Executable regression:

`experiments/r5_e9_singular_unsat_3cut_irreducible_odd_cycle.py`

It verifies exactly:

- row/column degree three;
- linearity and connectedness;
- rational rank 14 and the frozen kernel vector;
- no Boolean Exact-One witness (finite replay only; theorem UNSAT remains kernel-based);
- all edge cuts of size 1,2,3;
- exactly 30 size-three cuts and every one a one-vertex star;
- the explicit forbidden odd `3 x 3` submatrix.

## 7. Ceiling

```text
FROZEN 15_3 EXACT-ONE STATUS = UNSAT
RATIONAL NULLITY = 1
NONTRIVIAL <=3-EDGE CUT = NONE
BALANCED = FALSE
EXPLICIT STRONG ODD CYCLE = YES
CURRENT PREPROCESSING RESIDUAL NONEMPTY = PROVED BY CONTROL
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
