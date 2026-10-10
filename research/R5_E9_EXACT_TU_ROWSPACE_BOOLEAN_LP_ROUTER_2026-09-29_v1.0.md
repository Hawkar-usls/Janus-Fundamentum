# R5 E9 — Exact Totally-Unimodular Row-Space Boolean LP Router

Date: 2026-09-29

Status:
`JANUS_EXACT_POLYNOMIAL_SOLVER_ISLAND__TU_ROWSPACE`

## 1. Purpose

The current representation program already contains exact graph-coboundary, ordinary cycle-space and bidirected-cycle-space solver islands.  This note removes the need for any graph realization when the **exact rational row space itself admits a totally unimodular representation**.

The result is a deterministic polynomial Exact-One router based on exact pivot normalization, polynomial total-unimodularity recognition, and one rational linear program.

It is not a universal SAT solver.

## 2. Source setting

Let

```text
A in {0,1}^{m x n}
```

have exactly three `1`s in every source row.  Therefore

```text
A ((1/3)1_n)=1_m.
```

Let

```text
r=rank_Q(A).
```

Compute any exact full-row-rank rational row basis

```text
R in Q^{r x n},
row_Q(R)=row_Q(A).
```

Choose any set `T` of `r` independent columns and form

```text
F=R_T^{-1}R=[I_r | N].
```

Call this the exact pivot-normalized row-space representation.

## 3. Recognition theorem

### Theorem TUR-1

The following are equivalent.

1. There exists a full-row-rank totally unimodular matrix `U` with

```text
row_Q(U)=row_Q(A).
```

2. The exact pivot normalization `F` is totally unimodular.

Moreover, if the property holds then it holds for the normalization obtained from **any** rational pivot basis `T`.

### Proof: (2) => (1)

Immediate: take `U=F`.

### Proof: (1) => (2)

Since `R` and `U` have the same row space and full row rank, there is an invertible rational matrix `S` such that

```text
R=S U.
```

The chosen columns `T` are independent in `R`, hence `U_T` is nonsingular.  Since `U` is totally unimodular,

```text
det(U_T)=+/-1.
```

Therefore

```text
F=R_T^{-1}R
 =(S U_T)^{-1}S U
 =U_T^{-1}U.
```

This is the standard basis normalization of a totally unimodular representation.  Every square minor of `[I|N]=U_T^{-1}U` is, up to sign, a basis-exchange minor of `U` divided by `det(U_T)=+/-1`; hence every minor lies in `{0,+1,-1}`.

Thus `F` is totally unimodular. QED.

So exact TU-rowspace recognition requires no exponential search over row bases: normalize once and test `F` for total unimodularity.

## 4. Exact Boolean embedding

Because `row(A)=row(F)`,

```text
ker_Q(A)=ker_Q(F).
```

For every Boolean vector `x`,

```text
A x=1
iff A(x-(1/3)1)=0
iff x-(1/3)1 in ker_Q(A)
iff x-(1/3)1 in ker_Q(F)
iff F x=(1/3)F1.
```

Define

```text
b=(1/3)F1.
```

### Immediate integer obstruction

If any coordinate of `b` is nonintegral, then Exact-One is UNSAT because `F` is integral under the TU premise and therefore `Fx` is integral for Boolean `x`.

## 5. Polynomial LP solver

Assume `b` is integral.  Solve the feasibility LP

```text
F x=b,
0 <= x <= 1.
```

Since `F` is totally unimodular and `b`, the lower bounds and the upper bounds are integral, the bounded polyhedron is integral.  Therefore:

```text
LP infeasible
    => no Boolean x exists
    => Exact-One UNSAT.

LP feasible
    => the polyhedron has an integral vertex x
    => x in {0,1}^n
    => Exact-One SAT.
```

A polynomial rational LP algorithm constructs such a vertex/witness, and direct multiplication by the original integer matrix `A` verifies `Ax=1`.

Thus Exact-One is deterministically polynomial-time solvable on the exact TU-rowspace island.

## 6. Constructive router

```text
INPUT: Exact-One source matrix A, every source row of weight 3

1. Compute exact rational row basis R and rank r.
2. Choose r independent pivot columns T.
3. Form F=R_T^{-1}R=[I|N].
4. Run a polynomial total-unimodularity recognizer on F.

   if REJECT:
       return NOT_IN_EXACT_TU_ROWSPACE_BRANCH
       (no SAT/UNSAT conclusion).

5. Compute b=(F1)/3.
6. If b is nonintegral, return UNSAT.
7. Solve LP: F x=b, 0<=x<=1.
8. If infeasible, return UNSAT.
9. If feasible, return an integral LP vertex x and verify A x=1.
```

All exact linear-algebra, TU-recognition, LP, reconstruction and verification costs are polynomial in the rational input bit-size.

## 7. Relation to existing branches

This theorem is not the same premise as the existing augmented-regular-matroid terminal

```text
M_F2([A|1]) regular.
```

That branch solves a binary affine minimum-weight circuit problem in an augmented matroid.  The present branch instead asks whether the **rational row space of the original source** has a coordinate-exact TU representative and then uses the affine shift `(1/3)1` directly.

It also does not require a graph/bidirected realization.  Any exact TU row-space representation is sufficient.

## 8. SAT control: K3,3 source

Let `A` be the unsigned vertex-edge incidence matrix of `K_{3,3}`.  It has six source rows, nine variables and row weight three.

Multiplying all rows on one shore by `-1` converts its row space to an ordinary directed incidence row space.  Hence the exact row space admits a TU representation.

The Boolean Exact-One solutions are exactly perfect matchings; a diagonal matching supplies a SAT witness.

This control is also covered by the ordinary cycle-space router, as expected.

## 9. UNSAT control: nonintegral TU demand

Reuse the six-variable ordinary-cycle control from

```text
R5_E9_EXACT_CYCLE_KERNEL_FLOW_SOLVER_AND_NETWORK_RECOGNITION_ROUTER.
```

Its source matrix is

```text
A =
[1 1 1 0 0 0]
[1 0 0 1 1 0]
[1 0 0 0 1 1]
[0 1 0 1 1 0]
[0 0 1 1 1 0].
```

Its rational row space equals that of a reduced directed incidence matrix, hence the pivot-normalized row space is TU.  But the corresponding exact affine demand has a nonintegral coordinate, so no Boolean witness exists.

The finite checker independently verifies UNSAT by exhaustive Boolean replay.

## 10. Negative routing control: PG15

For the canonical PG15 SAT source,

```text
rank_Q(A)=11.
```

Exact row reduction followed by the deterministic first-pivot normalization yields `[I_11|N]` with an entry `-2`; more strongly it contains a `2 x 2` minor of determinant `-2`.

Therefore the normalized row-space representation is not TU, and TUR-1 proves that **no** exact TU representative of the same rational row space exists.

So the router soundly rejects PG15 without making a false SAT/UNSAT conclusion.

This is an important boundary: the new branch is polynomial and exact, but it does not dissolve the known hard positive control.

## 11. External algorithmic donors

Polynomial recognition of totally unimodular matrices is classical through Seymour/Truemper decomposition machinery.  Modern constructive implementations such as the CMR library implement a polynomial decomposition-based TU test (the documented regular/TU implementation is based on Walter--Truemper).

Polynomial rational LP is standard.  The only JANUS-specific step here is the exact affine source embedding through the coordinate-preserving row-space normalization.

## 12. Scope firewall

Do not promote:

```text
regular binary matroid == exact TU rowspace             FALSE / DIFFERENT PREMISE
arbitrary unimodular row operations preserve TU         FALSE IN GENERAL
PG15 is covered                                         FALSE
all source rowspaces admit TU representations           NOT PROVED
TU-rowspace router => universal SAT solver              FALSE
```

The exact promotion is:

```text
EXISTS exact TU representative of row_Q(A)
iff one pivot-normalized F is TU,
and on that recognized branch Exact-One is polynomial by LP.
```

## 13. New structural frontier

The current exact representation portfolio now contains:

```text
TU rowspace                 -> integral box LP
ordinary cycle rowspace     -> network flow
bidirected cycle rowspace   -> integer b-matching
coboundary kernel           -> Z3 phase propagation
augmented binary regularity -> regular-matroid circuit LP
```

The remaining question is not another scalar nullity bound.  It is a polynomial decomposition/recognition theorem for residual source rowspaces/kernels outside these classes, with exact Boolean witness lifting.

## 14. Ceiling

```text
EXACT TU-ROWSPACE RECOGNITION = POLYNOMIAL
EXACT-ONE ON TU ROWSPACE = POLYNOMIAL
SAT / UNSAT CONTROLS = PASS
PG15 TU-ROWSPACE = REJECTED
UNIVERSAL COVERAGE = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
