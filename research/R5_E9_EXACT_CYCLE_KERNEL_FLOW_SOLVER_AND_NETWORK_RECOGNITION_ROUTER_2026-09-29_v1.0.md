# R5 E9 — Exact Cycle-Kernel Flow Solver and Network-Recognition Router

Date: 2026-09-29

Status:
`JANUS_EXACT_POLYNOMIAL_SOLVER_ISLAND__CYCLE_SPACE_KERNEL_WITH_CONSTRUCTIVE_RECOGNITION`

## 1. Purpose

The existing graphic-kernel router solves the case where

```text
ker_Q(A) = col_Q(H)
```

is a graph coboundary / potential space.  This note closes the natural dual case where the rational kernel itself is a graph cycle space:

```text
ker_Q(A) = ker_Q(D)
```

for an oriented node-arc incidence matrix `D` whose columns are the Exact-One variables.

The resulting solver is not a kernel enumeration.  It is a unit-capacity transshipment problem and is polynomial regardless of the dimension of `ker_Q(A)`.

This is a genuine additional router branch, not a universal SAT algorithm.

## 2. Setting

Let

```text
A in {0,1}^{m x n}
```

have exactly three `1`s in every source row.  Hence

```text
A * ((1/3) 1_n) = 1_m.
```

Assume there exists an oriented graph `G=(V,E)`, with `E` identified coordinate-for-coordinate with the `n` columns of `A`, and a reduced full-row-rank node-arc incidence matrix

```text
D in {-1,0,1}^{r x n}
```

such that

```text
ker_Q(A) = ker_Q(D).
```

Call this the `EXACT_CYCLE_KERNEL` premise.

Equivalently,

```text
row_Q(A) = row_Q(D).
```

## 3. Exact flow equivalence

### Theorem ECKF-1

Under `EXACT_CYCLE_KERNEL`, for `x in {0,1}^n`,

```text
A x = 1_m
```

if and only if

```text
D x = (1/3) D 1_n.
```

### Proof

Because every source row has size three,

```text
A x = 1
iff A (x-(1/3)1) = 0
iff x-(1/3)1 in ker_Q(A).
```

By the exact cycle-kernel premise this is equivalent to

```text
D (x-(1/3)1) = 0,
```

i.e.

```text
D x = (1/3)D1.
```

QED.

Thus the Boolean Exact-One problem on this representation class is exactly a graph-flow feasibility problem with unit capacities.

## 4. Polynomial solver

Restore the omitted redundant vertex row in each graph component if desired and define

```text
b = (1/3) D 1.
```

If any entry of `b` is nonintegral, return `UNSAT`: the left side `Dx` is integral for every Boolean `x`.

Otherwise solve

```text
D x = b,
0 <= x <= 1.
```

A directed node-arc incidence matrix is totally unimodular.  Therefore, for integral `b`, every nonempty face of the bounded flow polytope contains an integral vertex.  Equivalently, ordinary feasible-transshipment / max-flow machinery constructs an integral feasible point.

Since the capacity interval is `[0,1]`, every integral feasible point satisfies

```text
x in {0,1}^n.
```

By ECKF-1 that `x` is exactly an Exact-One witness.

Hence, once `D` is supplied, decision and witness construction are deterministic polynomial time.

## 5. Exact recognition and recovery

The representation can itself be recognized in polynomial time by the same exact pivot-normalization principle used by the companion graphic-kernel router, but applied to the row space of `A` rather than to the transpose of a kernel basis.

Compute an exact rational row basis

```text
R in Q^{r x n},
row(R)=row(A),
r=rank_Q(A).
```

Choose any `r` linearly independent columns `T`.  Let `R_T` be the corresponding nonsingular `r x r` submatrix and normalize

```text
F = R_T^{-1} R = [ I_r | N ].
```

### Theorem ECKF-NET-2

The following are equivalent.

1. `A` has an exact cycle-kernel representation `ker(A)=ker(D)` by a reduced oriented incidence matrix `D`.
2. The normalized nonbasis block `N` is a network matrix: there is a graph and spanning forest with reduced incidence partition

```text
D = [D_T | D_N]
```

such that

```text
N = D_T^{-1} D_N.
```

### Proof: (1) => (2)

If `ker(A)=ker(D)`, then `row(R)=row(D)`.  Since both have row rank `r`,

```text
R = S D
```

for an invertible rational `S`.

The pivot columns `T` are independent in `R`, hence in `D`; for a reduced incidence representation they form a spanning forest.  Thus `D_T` is nonsingular and

```text
R_T^{-1}R
= (S D_T)^{-1} S D
= D_T^{-1}D
= [I | D_T^{-1}D_N].
```

So `N` is a network matrix.

### Proof: (2) => (1)

If an exact network recognizer returns `D_T,D_N` with

```text
N=D_T^{-1}D_N,
```

then

```text
F=[I|N]=D_T^{-1}D.
```

Hence

```text
row(A)=row(R)=row(F)=row(D),
```

and therefore

```text
ker_Q(A)=ker_Q(D).
```

QED.

No coordinate-wise projective scaling is admitted: the network realization must match the exact pivot-normalized matrix `N`.

## 6. Constructive router

```text
INPUT: Exact-One source matrix A with row weight 3

1. Compute exact rational row rank and a full row basis R.
2. Choose pivot columns T and form F=R_T^{-1}R=[I|N].
3. Run polynomial exact network-matrix recognition on N.

   REJECT:
       return NOT_IN_EXACT_CYCLE_KERNEL_BRANCH
       (no SAT/UNSAT conclusion).

   ACCEPT:
       recover a coordinate-compatible oriented incidence D;
       compute b=(D1)/3.

4. If b is not integral, return UNSAT with the offending vertex demand.
5. Solve unit-capacity transshipment Dx=b, 0<=x<=1.
6. If infeasible, return UNSAT with the standard flow/cut certificate.
7. If feasible, return the integral x and verify A x=1 directly.
```

All steps are polynomial in the input bit-size.

## 7. SAT control: K3,3

Let `A` be the ordinary unsigned vertex-edge incidence matrix of `K_{3,3}`.  It has six rows, nine variables, and every row has weight three.

Orient every edge from the left shore to the right shore.  The signed node-arc incidence `D` differs from the unsigned incidence rows only by multiplying all left-shore rows by `-1`.  Hence

```text
ker_Q(A)=ker_Q(D).
```

The flow demand is

```text
b_v=-1  on the left shore,
b_v=+1  on the right shore.
```

A unit-capacity feasible transshipment is exactly a perfect matching.  For example the three diagonal left-right edges give an Exact-One witness.

The kernel dimension is four, so this is already a nonzero-cycle-space control rather than a full-rank terminal.

## 8. UNSAT control with nonzero cycle space

Take six graph vertices and the directed edges

```text
(0,3), (1,2), (1,3), (1,4), (1,5), (4,5),
```

oriented as written.  Delete the redundant row for vertex `5` from its node-arc incidence matrix `D`.

Let

```text
A =
[1 1 1 0 0 0]
[1 0 0 1 1 0]
[1 0 0 0 1 1]
[0 1 0 1 1 0]
[0 0 1 1 1 0].
```

Every source row has weight three.  Exact rational elimination gives

```text
rank_Q(A)=rank_Q(D)=5,
row_Q(A)=row_Q(D),
```

so the one-dimensional rational kernel is exactly the graph cycle space.

But

```text
D1 = (-1,-4,1,2,0)^T,
```

so `(D1)/3` is nonintegral.  The flow router therefore returns `UNSAT` immediately.  Exhaustive Boolean replay on the six variables confirms that no `Ax=1` witness exists.

This control shows that the theorem is not merely a restatement of the regular-bipartite perfect-matching case.

## 9. Relation to the graphic-kernel island

The two constructive branches are dual in representation, but their algorithms are different:

```text
EXACT_GRAPHIC_KERNEL:
    ker(A) = coboundary/potential space
    -> Z3 phase propagation on vertices.

EXACT_CYCLE_KERNEL:
    ker(A) = graph cycle/flow space
    -> unit-capacity transshipment.
```

Both can be recognized through exact network normalization, and both tolerate arbitrarily large kernel dimension.

This strengthens the new strategic lesson from the Paley family:

```text
kernel dimension alone is not the right complexity currency;
recognizable representation class can be decisive.
```

## 10. Prior-art binding

The external donors are classical and are not claimed as new:

- node-arc incidence matrices are totally unimodular;
- feasible integral transshipment / circulation with integral demands and capacities is polynomial;
- exact network-matrix / graph realization is polynomial (e.g. Bixby-Wagner and later constructive implementations).

The JANUS-specific statement is the exact Boolean embedding

```text
Ax=1
iff
Dx=(D1)/3
```

under equality of the rational kernels, plus its coordinate-exact recognition router.

## 11. Scope firewall

Do not promote any of the following:

```text
vector-matroid equivalence alone => exact cycle kernel       FALSE / INSUFFICIENT
projective column scaling => semantics preserved             FALSE
all source kernels are graphic or cycle-space                NOT PROVED
regular-matroid terminal => this theorem is redundant        NOT ESTABLISHED
cycle-kernel router => universal polynomial SAT solver       FALSE
```

The exact promotion is:

```text
IF ker_Q(A) is exactly the cycle space of a coordinate-compatible graph,
THEN Exact-One is polynomial-time solvable,
AND that premise is polynomially recognizable/recoverable by exact network normalization.
```

## 12. New frontier

We now have two large-kernel polynomial representation islands:

```text
CUT / COBBOUNDARY kernel  -> Z3 phase
CYCLE / FLOW kernel       -> unit-capacity transshipment
```

The next legitimate gate is to go beyond pure network spaces without losing exact Boolean semantics:

```text
R5_E9_KERNEL_REPRESENTATION_DECOMPOSITION_BEYOND_NETWORK_DUAL_GATE_V1
```

Immediate candidates are exact signed-graphic / bidirected representations and source-compatible 2/3-sum composition, with explicit witness lifting and polynomial total cost.

## 13. Ceiling

```text
EXACT CYCLE-KERNEL SAT/UNSAT = POLYNOMIAL
EXACT CYCLE-KERNEL RECOGNITION = POLYNOMIAL
EXACT D RECOVERY = POLYNOMIAL
NONZERO-KERNEL SAT + UNSAT CONTROLS = PROVIDED
UNIVERSAL REPRESENTATION COVERAGE = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
