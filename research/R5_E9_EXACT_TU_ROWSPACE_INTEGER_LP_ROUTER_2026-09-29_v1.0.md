# R5 E9 — Exact TU Row-Space Integer-LP Router

Date: 2026-09-29

Status:
`JANUS_EXACT_POLYNOMIAL_SOLVER_ISLAND__TOTALLY_UNIMODULAR_ROWSPACE`

## 1. Purpose

The existing R5 E9 representation router already contains exact network/cycle and
bidirected/binet polynomial islands.  This note adds a representation branch that
does not require recovering any graph at all.

For an Exact-One source `A`, normalize its exact rational row space on any column
basis.  If the resulting matrix is totally unimodular (TU), then the Boolean source
is exactly an integral linear feasibility problem whose LP relaxation is integral.
The branch is polynomially recognizable and polynomially solvable.

This is a solver island, not a universal solver.

## 2. Setup

Let

```text
A in {0,1}^{m x n}
```

and assume every source row has exactly three ones.  Therefore

```text
A * ((1/3) 1_n) = 1_m.
```

Let

```text
r = rank_Q(A)
```

and compute an exact full-row-rank basis

```text
R in Q^{r x n},
row_Q(R)=row_Q(A).
```

Choose any set `T` of `r` linearly independent columns.  Reorder columns so `T`
comes first and define

```text
F = R_T^{-1} R = [I_r | N].
```

Call `F` the exact pivot-normalized row-space representation.

## 3. Exact recognition theorem

### Theorem TUR-1

The following are equivalent.

1. There exists a full-row-rank totally unimodular matrix `D` with the same
   coordinate row space as `A`:

```text
row_Q(D)=row_Q(A).
```

2. The exact pivot-normalized matrix

```text
F=R_T^{-1}R
```

is totally unimodular.

Hence exact TU-row-space membership is decidable in polynomial time by exact
Gaussian elimination followed by a polynomial TU-recognition algorithm.

### Proof: (2) => (1)

Immediate: take `D=F`.

### Proof: (1) => (2)

Assume `row(D)=row(R)`.  Then

```text
R=S D
```

for some invertible rational `S`.

The chosen columns `T` are independent in `R`, hence in `D`.  Therefore `D_T` is
nonsingular.  Since `D` is TU,

```text
det(D_T) in {+1,-1}.
```

Moreover

```text
F
= R_T^{-1}R
= (S D_T)^{-1} S D
= D_T^{-1}D.
```

Pivoting a TU matrix on a nonzero entry preserves total unimodularity.  Reducing
the TU basis block `D_T` to the identity by a sequence of basis pivots therefore
produces exactly `D_T^{-1}D=[I|N]`, which is TU.

Thus (1) implies (2).  QED.

The statement is coordinate-exact.  No column scaling or projective equivalence is
silently admitted.

## 4. Exact-One equivalence on the TU branch

Because `row(F)=row(A)`, the two matrices have the same rational kernel.  For every
Boolean vector `x`,

```text
A x=1
iff A(x-(1/3)1)=0
iff x-(1/3)1 in ker_Q(A)
iff x-(1/3)1 in ker_Q(F)
iff F x = (1/3)F1.
```

Define

```text
b=(1/3)F1.
```

### Theorem TUR-2

If `F` is TU, Exact-One on `A` is equivalent to

```text
F x=b,
0 <= x <= 1,
x integral.
```

If `b` is not integral, return `UNSAT` immediately because `F` is integral and
`Fx` is integral for every Boolean `x`.

If `b` is integral, solve the LP relaxation

```text
F x=b,
0 <= x <= 1.
```

The inequality matrix can be written

```text
[ F ]
[-F ]
[ I ]
[-I ],
```

which is TU because TU is preserved by row negation and adjoining unit rows.  The
right-hand side is integral.  By the Hoffman-Kruskal integrality theorem, every
vertex of the feasible polytope is integral.  The box makes the polytope bounded,
so if it is nonempty it has an integral vertex; that vertex lies in `{0,1}^n`.

Therefore ordinary polynomial-time linear programming decides the branch and
constructs a Boolean witness whenever one exists.

## 5. Constructive router

```text
INPUT: row-weight-3 Exact-One source A

1. Compute exact row rank and a full row basis R.
2. Select r pivot columns T.
3. Form F=R_T^{-1}R=[I|N].
4. Run a polynomial exact TU recognizer on F.

   REJECT:
       return NOT_IN_EXACT_TU_ROWSPACE_BRANCH
       (no SAT/UNSAT conclusion).

   ACCEPT:
       compute b=(F1)/3.

5. If b is nonintegral, return UNSAT.
6. Solve F x=b, 0<=x<=1 by polynomial LP.
7. If infeasible, return UNSAT.
8. If feasible, recover an integral LP vertex x in {0,1}^n.
9. Verify A x=1 exactly and return SAT witness.
```

All algebra is exact and all stages are polynomial in the bit-size of `A`.

## 6. Relation to existing R5 E9 islands

The branch is deliberately representation-based.

```text
ordinary directed cycle kernel
    -> normalized network matrix
    -> TU
    -> admitted here.
```

Thus the new router subsumes the ordinary cycle-kernel flow island at the level of
decision, although the graph-flow solver remains a more explicit combinatorial
certificate route.

The bidirected/binet branch remains independently necessary: binet matrices need
not be TU and can have determinant-2 minors.  The Petersen unsigned-incidence
control from the binet theorem is an explicit source-side example rejected by the
TU branch while accepted by bidirected `b`-matching.

The graphic/coboundary kernel branch is kept separately as well because its natural
certificate is a `Z_3` phase system on a recovered graph.

## 7. Controls

### SAT control: K3,3 unsigned incidence

Let `A` be the `6 x 9` unsigned vertex-edge incidence matrix of `K3,3`.  Every row
has weight three.  After orienting all edges from left to right, row sign changes
turn `A` into a directed node-arc incidence matrix, so the normalized row-space
matrix is TU.

Here `b=(F1)/3` is integral and a perfect matching gives a Boolean Exact-One
witness.

### UNSAT control: nonintegral demand network source

Reuse the six-variable nonzero-cycle-space UNSAT control from
`R5_E9_EXACT_CYCLE_KERNEL_FLOW_SOLVER_AND_NETWORK_RECOGNITION_ROUTER`.
Its row space is an ordinary network row space and hence TU, but `(F1)/3` is
nonintegral.  TUR-2 returns exact `UNSAT` before LP search.

### TU rejection / binet acceptance control: Petersen

For the Petersen unsigned incidence source, the deterministic pivot normalization
contains a `3 x 3` minor of determinant `-2`.  Therefore the TU recognizer rejects.
The existing exact bidirected/binet router accepts the same source and reconstructs
a perfect-matching witness.

This confirms that the TU and binet routes must be kept as a union rather than
mistakenly identifying one with the other.

## 8. Prior art / donor algorithms

External donors are classical and are not JANUS novelty claims:

- Hoffman and Kruskal: integral polyhedra defined by TU matrices and integral
  right-hand sides;
- Seymour/Truemper and later implementations: polynomial recognition of total
  unimodularity / regular-matroid structure;
- polynomial-time linear programming.

Recent integer-programming literature continues to treat bounded-subdeterminant
classes beyond TU as a major frontier; in particular, the general fixed-Delta
problem is not known polynomial for arbitrary constant Delta.  Therefore this
router is intentionally frozen at exact TU and does not extrapolate to arbitrary
bounded minors.

## 9. Scientific consequence

The representation hierarchy now contains at least

```text
EXACT TU ROW SPACE
    -> polynomial LP integrality

EXACT BIDIRECTED / BINET ROW SPACE
    -> polynomial integer bidirected flow / b-matching

EXACT GRAPHIC COBBOUNDARY KERNEL
    -> polynomial Z3 phase
```

so kernel dimension itself is even less relevant than before.  The universal
frontier is the residual class whose exact pivot-normalized row/kernel
representations are neither handled by TU nor by the already frozen binet/network
routers.

Recommended next gate:

```text
R5_E9_EXACT_REPRESENTATION_ROUTER_RESIDUAL_AFTER_TU_BINET_GATE_V1
```

with two immediate questions:

1. can source-compatible 1/2/3-sum decomposition route the residual into solved
   TU/binet pieces with polynomial interface state;
2. can the exact augmented constraint matrix fall into another polynomial integer
   programming class (for example a safely recognized bimodular subclass) without
   importing an unproved recognition step.

## 10. Firewall

Do not promote:

```text
F not TU => source UNSAT                         FALSE
regular matroid up to column scaling => exact   FALSE
all binet matrices are TU                        FALSE
bounded determinants Delta>2 => polynomial IP   OPEN in general
TU router => universal Exact-One solver          FALSE
```

Exact promotion only:

```text
IF exact pivot-normalized row space is TU,
THEN Exact-One SAT/UNSAT and witness construction are polynomial.
```

## 11. Ceiling

```text
EXACT TU ROW-SPACE RECOGNITION      = POLYNOMIAL
EXACT-ONE ON TU ROW SPACE           = POLYNOMIAL
SAT / UNSAT CONTROLS                = PROVIDED
ORDINARY NETWORK CYCLE BRANCH       = COVERED
NON-TU BINET CASES                  = ROUTED SEPARATELY
RESIDUAL AFTER TU + BINET           = OPEN
UNIVERSAL POLYNOMIAL SOLVER         = NOT PROVED
E8_D1                               = EMPTY
P_VS_NP                             = OPEN
```
