# R5 E9 — Exact Bidirected Cycle-Kernel Binet / B-Matching Router

Date: 2026-09-29

Status:
`JANUS_EXACT_POLYNOMIAL_SOLVER_ISLAND__BIDIRECTED_CYCLE_KERNEL_WITH_CONSTRUCTIVE_BINET_RECOGNITION`

## 1. Purpose

The companion theorem

```text
R5_E9_EXACT_CYCLE_KERNEL_FLOW_SOLVER_AND_NETWORK_RECOGNITION_ROUTER
```

solves Exact-One when the rational kernel is exactly the cycle space of an ordinary directed graph.

This note strictly enlarges that branch from ordinary node-arc incidence matrices to **bidirected** node-edge incidence matrices.  The resulting integer feasibility problem is a capacitated bidirected-flow problem, equivalently a capacitated `b`-matching problem, and is polynomially solvable by classical matching machinery.

Recognition/recovery is supplied by polynomial **binet-matrix recognition**, the bidirected analogue of network-matrix recognition.

This is a polynomial solver island.  It is not a universal SAT solver.

## 2. Bidirected incidence convention

A bidirected edge has independently signed ends.  Its incidence column can therefore contain

```text
(+1,-1)   ordinary directed edge,
(+1,+1)   two-head link,
(-1,-1)   two-tail link,
```

with the two nonzeros at distinct vertices.  Standard bidirected models may also admit one-ended edges and signed loops, giving columns with one nonzero `+/-1` or one nonzero `+/-2`; the theorem below allows the standard node-edge incidence class returned by the constructive binet recognizer.

Let

```text
D in Z^{r x n}
```

be a full-row-rank bidirected node-edge incidence matrix, with its `n` columns identified coordinate-for-coordinate with the Exact-One variables.

## 3. Exact kernel premise

Let

```text
A in {0,1}^{m x n}
```

have exactly three `1`s in every source row.  Hence

```text
A * ((1/3)1_n) = 1_m.
```

Assume

```text
ker_Q(A) = ker_Q(D).
```

Equivalently,

```text
row_Q(A)=row_Q(D).
```

Call this the `EXACT_BIDIRECTED_CYCLE_KERNEL` premise.

## 4. Boolean Exact-One = integer bidirected flow

### Theorem BCKF-1

Under `EXACT_BIDIRECTED_CYCLE_KERNEL`, for every Boolean vector `x`,

```text
A x = 1_m
```

if and only if

```text
D x = (1/3) D 1_n.
```

### Proof

Since every source row has size three,

```text
A x = 1
iff A(x-(1/3)1)=0
iff x-(1/3)1 in ker_Q(A)
iff x-(1/3)1 in ker_Q(D)
iff D x=(1/3)D1.
```

QED.

Thus define

```text
b=(1/3)D1.
```

If any coordinate of `b` is nonintegral, then no Boolean solution exists because `Dx` is integral for every Boolean `x`.

If `b` is integral, Exact-One is exactly the integer feasibility problem

```text
D x=b,
0 <= x <= 1,
x integral.
```

This is a unit-capacity bidirected-flow problem.

## 5. Polynomial integer solver

A critical firewall is required here:

```text
DO NOT replace the integer problem by the raw LP and invoke total unimodularity.
```

General bidirected incidence / binet systems need not be totally unimodular; their LP relaxations can be half-integral.

Instead use the classical integer algorithmic route: capacitated bidirected network flow is polynomially reducible to capacitated perfect `b`-matching / general matching.  Therefore feasibility of

```text
D x=b,
0 <= x <= 1,
x integral
```

is decidable in polynomial time, and a feasible integral `x` is constructible in polynomial time.

By BCKF-1, such an `x` is exactly an Exact-One witness.  If the bidirected-flow / `b`-matching instance is infeasible, return Exact-One `UNSAT` with the matching/flow infeasibility certificate supplied by the donor algorithm.

## 6. Exact constructive recognition via binet matrices

The exact premise can itself be recognized and a compatible `D` recovered in polynomial time.

Compute an exact rational row basis

```text
R in Q^{r x n},
row(R)=row(A),
r=rank_Q(A).
```

Choose any set `T` of `r` linearly independent columns.  Reorder columns so `T` is first and form

```text
F = R_T^{-1} R = [I_r | N].
```

### Theorem BCKF-BINET-2

The following are equivalent.

1. There exists a full-row-rank bidirected incidence matrix `D` with

```text
ker_Q(A)=ker_Q(D).
```

2. The normalized nonbasis block `N` is a binet matrix: there exist a nonsingular square basis block `B` and a nonbasis block `N_D` such that

```text
D=[B | N_D]
```

is the node-edge incidence matrix of a bidirected graph and

```text
N = B^{-1} N_D.
```

### Proof: (1) => (2)

If `row(R)=row(D)`, then for some invertible rational `S`,

```text
R=S D.
```

The selected pivot columns are independent in `R`, hence the corresponding columns `B=D_T` are independent in `D`.  Thus `B` is nonsingular and

```text
R_T^{-1}R
=(S B)^{-1} S [B|N_D]
=B^{-1}[B|N_D]
=[I|B^{-1}N_D].
```

Therefore the normalized nonbasis block is binet.

### Proof: (2) => (1)

Suppose constructive binet recognition returns `B,N_D` with

```text
N=B^{-1}N_D
```

and `D=[B|N_D]` a full-row-rank bidirected incidence matrix.  Then

```text
F=[I|N]=B^{-1}D,
```

so

```text
row(A)=row(R)=row(F)=row(D).
```

Hence

```text
ker_Q(A)=ker_Q(D).
```

QED.

The equality is coordinate-exact.  No arbitrary projective column scaling is accepted.

## 7. Constructive polynomial router

```text
INPUT: Exact-One source matrix A with source-row weight exactly 3

1. Compute an exact rational row basis R and rank r.
2. Select r independent pivot columns T.
3. Form F=R_T^{-1}R=[I|N].
4. Run a constructive polynomial binet-matrix recognizer on N.

   if REJECT:
       return NOT_IN_EXACT_BIDIRECTED_CYCLE_KERNEL_BRANCH
       (no SAT/UNSAT conclusion).

   if ACCEPT:
       recover B,N_D and D=[B|N_D] with F=B^{-1}D.

5. Compute b=(D1)/3.
6. If b is nonintegral, return UNSAT.
7. Solve integer unit-capacity bidirected flow
       D x=b, 0<=x<=1, x integral
   through a polynomial reduction/algorithm for capacitated b-matching.
8. If infeasible, return UNSAT.
9. If feasible, return the integral x and directly verify A x=1.
```

All exact linear-algebra and reconstruction steps are polynomial.  The external donor algorithms provide polynomial binet recognition and polynomial integer bidirected-flow / `b`-matching feasibility.

## 8. Strict SAT control outside the ordinary network branch: Petersen

Let `G` be the Petersen graph.  Let `A` be its ordinary **unsigned** vertex-edge incidence matrix.

```text
vertices = 10
edges    = 15
```

Every vertex has degree three, so every source row of `A` has weight three.

Interpret each graph edge as a bidirected edge with **two heads**.  Then its bidirected incidence matrix is simply

```text
D=A.
```

Therefore

```text
ker_Q(A)=ker_Q(D)
```

trivially.  Since the Petersen graph is connected and nonbipartite, exact elimination gives

```text
rank_Q(A)=10,
nullity_Q(A)=5.
```

Also

```text
D1=3*1,
b=1.
```

Thus the bidirected-flow problem asks for a `0/1` edge set of degree exactly one at every vertex: a perfect matching.  The five spokes of the standard Petersen presentation give such a matching, so this Exact-One source is SAT.

This control is **strictly outside the ordinary network/TU normalization**.  For the deterministic Gaussian pivot basis used by the checker, the normalized matrix `[I|N]` contains a `3 x 3` minor with determinant `-2`.  Hence it is not totally unimodular and cannot be an ordinary network matrix, while it is binet by construction.

So the new branch is a genuine extension of the ordinary cycle-kernel router.

## 9. Strict UNSAT control: 16-vertex three-balloon cubic graph

Construct a connected cubic graph `G_16` as follows.

Start with one central vertex `c`.  For each of three disjoint copies of `K4`:

1. choose one edge `uv`;
2. subdivide it by a new vertex `w`, replacing `uv` by `u-w-v`;
3. join `w` to the central vertex `c`.

The resulting graph has

```text
16 vertices,
24 edges,
all degrees = 3.
```

Let `A` again be the unsigned vertex-edge incidence matrix and interpret every edge as a two-head bidirected link, so `D=A`.

Exact rational elimination gives

```text
rank_Q(A)=16,
nullity_Q(A)=8.
```

As in the Petersen control,

```text
b=(D1)/3=1.
```

Hence Exact-One is equivalent to a perfect matching.

But deleting the central vertex leaves exactly three connected components, each with five vertices.  Thus for `S={c}` the graph has

```text
3 odd components > |S|=1.
```

By the exact perfect-matching parity/Tutte obstruction, no perfect matching exists.  Therefore the source is Exact-One UNSAT.

The checker also performs an independent exact recursive perfect-matching replay.

This control too lies strictly outside the ordinary network branch: its deterministic pivot normalization contains a `2 x 2` minor of determinant `2`.

## 10. Literature binding

External donor results used here are classical and are not JANUS novelty claims.

### Binet recognition

Antoine Musitelli, *Recognition of generalized network matrices* (thesis / arXiv:0807.3541), gives a polynomial algorithm for deciding whether a rational matrix is binet.  The stated complexity is `O(r^6 s)` for an `r x s` matrix, and on acceptance the algorithm constructs nonsingular `B` and `N_D` such that `[B N_D]` is a full-row-rank bidirected node-edge incidence matrix and the input equals `B^{-1}N_D`.

### Integer bidirected flow

The classical Edmonds / Edmonds-Johnson bidirected-network framework unifies ordinary network flow and matching.  Integer bidirected flow with bounds is polynomially reducible to general / perfect `b`-matching.  Later formulations, including Hochbaum's work on linear programs with at most two nonzeros per column, explicitly record polynomial solvability of the capacitated case by this matching reduction.

The JANUS-specific synthesis is the exact source-kernel identity

```text
Ax=1
iff
Dx=(D1)/3
```

and the coordinate-exact pivot-normalization bridge from a source matrix to constructive binet recognition.

## 11. Relation to the current representation router

We now have a strict hierarchy of exact rational-kernel representation islands:

```text
EXACT COBBOUNDARY / CUT KERNEL
    ker(A)=col(H)
    -> Z3 phase propagation.

EXACT ORDINARY CYCLE KERNEL
    ker(A)=ker(D_directed)
    -> unit-capacity transshipment.

EXACT BIDIRECTED CYCLE KERNEL
    ker(A)=ker(D_bidirected)
    -> integer bidirected flow / b-matching.
```

The third branch strictly contains the second and reaches non-TU examples with large rational kernel.

## 12. Scope firewall

Do not promote:

```text
bidirected LP relaxation is always integral                     FALSE
binet matrix => totally unimodular                              FALSE
vector-matroid/projective equivalence => Exact-One semantics    FALSE
all post-RKPR source kernels are binet                          NOT PROVED
bidirected router => universal polynomial SAT solver            FALSE
```

The exact promotion is:

```text
IF the exact rational kernel is coordinate-compatibly bidirected-cycle,
THEN Exact-One is polynomial-time solvable,
AND this premise is polynomially recognizable/recoverable by binet recognition.
```

## 13. New live gate

The correct next question is no longer whether nullity is small.  It is whether the residual source kernels can be decomposed into polynomially solvable exact representation pieces.

```text
R5_E9_KERNEL_REPRESENTATION_DECOMPOSITION_BEYOND_BINET_GATE_V1
```

Immediate stress targets:

```text
PG15
post-RKPR SAT 2-lift controls
strong odd-cycle controls
linear high-girth controls
augmented nonregular F7/F7* carriers
```

The next admissible promotion must either recognize a strictly larger exact representation class with a polynomial Boolean solver, or give a source-specific polynomial decomposition into already solved classes with exact witness lifting.

## 14. Ceiling

```text
EXACT BIDIRECTED-CYCLE SOLVER = POLYNOMIAL
CONSTRUCTIVE BINET RECOGNITION / RECOVERY = POLYNOMIAL DONOR
STRICT NON-TU SAT CONTROL = PETERSEN / PASS
STRICT NON-TU UNSAT CONTROL = G_16 / PASS
UNIVERSAL BINET COVERAGE = NOT PROVED
UNIVERSAL REPRESENTATION DECOMPOSITION = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
