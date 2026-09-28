# R5 E9 — Graphic-Kernel Z3 Phase Exact Solver Island

Date: 2026-09-29

Status:
`JANUS_EXACT_POLYNOMIAL_SOLVER_ISLAND__GRAPHIC_COBBOUNDARY_KERNEL`

## 1. Setting

Let `A` be any Exact-One source matrix with exactly three 1s in every source row, so

```text
A * (1/3) 1 = 1.
```

The number of rows need not equal the number of variables for the theorem below.

Assume the rational kernel has an exact oriented-graph coboundary representation.
There is a directed graph `G=(V,E)` whose edges are in one-to-one correspondence with the variables/columns of `A`, and an edge-vertex incidence matrix

```text
H in {-1,0,1}^{E x V}
```

with row

```text
h_(u->v) = e_v-e_u
```

such that

```text
ker_Q(A) = col_Q(H).
```

Call this the `EXACT_GRAPHIC_KERNEL` premise.

## 2. Theorem

### Theorem GKZ3-1

Under `EXACT_GRAPHIC_KERNEL`, the following are equivalent:

```text
(1) A x = 1 for some x in {0,1}^E.

(2) There exists phi: V -> Z_3 such that
        phi(v)-phi(u) = -1 (mod 3)
    for every oriented edge u->v.
```

Moreover, condition (2) can be decided and a Boolean witness reconstructed in

```text
O(|V|+|E|)
```

arithmetic/graph operations once `H` is supplied.

Thus Exact-One is deterministically polynomial-time solvable on the exact graphic-kernel island, regardless of the dimension of the rational kernel.

## 3. Soundness: Boolean witness implies phase

Assume

```text
A x = 1,
x in {0,1}^E.
```

Set

```text
y = x-(1/3)1.
```

Then `A y=0`, so by the premise there is `alpha in Q^V` with

```text
y_(u->v) = alpha_v-alpha_u.
```

Let

```text
beta = 3 alpha.
```

For every edge,

```text
beta_v-beta_u
= 3 x_(u->v)-1
in {-1,2}.
```

These differences are integers. On each connected component subtract the value at one root vertex. Every remaining `beta_v` then becomes an integer because it is a sum of integer edge differences along a path.

Reduce those integer potentials modulo 3. Both allowed edge increments satisfy

```text
-1 = 2 (mod 3),
```

so

```text
phi(v)-phi(u) = -1 (mod 3)
```

on every oriented edge.

## 4. Completeness: phase constructs a Boolean witness

Assume a phase labeling

```text
phi:V -> Z_3
```

satisfying the edge equations.

Choose the canonical integer representatives

```text
beta_v in {0,1,2}
```

of `phi(v)`.

For any edge `u->v`, the integer difference `beta_v-beta_u` lies between `-2` and `2` and is congruent to `-1 mod 3`. Therefore the only possibilities are

```text
beta_v-beta_u in {-1,2}.
```

Define

```text
x_(u->v) = (beta_v-beta_u+1)/3.
```

Then `x_(u->v) in {0,1}`.

Set `alpha=beta/3`. We have

```text
x-(1/3)1 = H alpha in ker_Q(A).
```

Therefore

```text
A x
= A((1/3)1) + A H alpha
= 1.
```

So `x` is an Exact-One witness.

## 5. Linear-time phase algorithm

For every connected component choose an arbitrary root and assign

```text
phi(root)=0.
```

Traverse the underlying graph. For an oriented edge `u->v`, propagate

```text
phi(v)=phi(u)-1 mod 3.
```

If a previously assigned endpoint disagrees, return UNSAT for the island. The traversal simultaneously returns a conflicting cycle as a checkable certificate.

If no conflict occurs, use the canonical representatives `{0,1,2}` and the formula in Section 4 to construct `x`.

Runtime after `H` is available is linear in the graph size; verification `A x=1` remains polynomial.

## 6. Cycle characterization

The phase condition is equivalent to a signed cycle congruence.

Traverse any undirected cycle and count each edge as `+1` when traversal follows its orientation and `-1` otherwise. A phase exists iff every cycle has

```text
sum signed_edge_steps = 0 (mod 3).
```

Thus a single violating cycle is a compact UNSAT certificate on this island.

For the Paley minus-two family, every fixed difference class contains a consistently oriented cycle of prime length `q`, so the obstruction is simply

```text
q != 0 (mod 3).
```

This recovers its cycle-sum UNSAT proof as an instance of GKZ3-1.

## 7. Why this is stronger than low-nullity enumeration

The Paley family has

```text
nullity_Q(A_q)=q-1 > sqrt(2n)-1,
```

so `2^nullity` is superpolynomial. Nevertheless its exact root-potential kernel puts it inside GKZ3-1 and it is solved by one graph traversal.

Therefore

```text
kernel dimension != kernel algorithmic complexity.
```

A structural representation of the kernel can dominate its dimension.

## 8. Recognition boundary

The theorem above assumes `H` is supplied or has already been recovered with the exact equality

```text
ker_Q(A)=col_Q(H).
```

This equality is stronger than merely saying that the vector matroid of a kernel basis is graphic. Ordinary graphic-matroid representations are defined up to row transformations and projective column scalings; arbitrary coordinate-wise scalings need not preserve the exact kernel subspace used by the Boolean embedding.

There are classical polynomial algorithms for graphic matroid / graph realization and network-matrix recognition, and modern implementations use SPQR representations to compactly encode realization ambiguity. They are promising donors, but they do not by themselves discharge the exact coordinate-compatibility obligation in this theorem.

Therefore the new live gate is

```text
R5_E9_EXACT_GRAPHIC_KERNEL_RECOGNITION_AND_RECOVERY_GATE_V1
```

with obligations:

```text
INPUT: rational kernel basis B of A

OUTPUT one of:
  (a) exact oriented incidence H with col(H)=ker_Q(A), or
  (b) a sound rejection that no such H exists,

TOTAL COST: polynomial in the bit-size of A.
```

A successful polynomial recognizer makes GKZ3-1 a directly usable branch of the universal solver.

## 9. Scope firewall

Do not promote:

```text
graphic matroid alone => GKZ3 premise             NOT YET PROVED
network-matrix recognition => exact H recovery     NOT AUTOMATIC
every post-RKPR kernel is graphic                  FALSE / NOT CLAIMED
GKZ3 solver island => P=NP                         FALSE
```

The exact promotion is:

```text
IF ker_Q(A) is exactly a graph coboundary space and H is available,
THEN Exact-One SAT is equivalent to a Z3 potential test and is polynomial.
```

## 10. Ceiling

```text
GKZ3 SOUNDNESS = PROVED
GKZ3 COMPLETENESS = PROVED
GKZ3 TERMINATION = PROVED
GKZ3 POLY GIVEN H = PROVED
EXACT H RECOGNITION / RECOVERY = OPEN
UNIVERSAL COVERAGE = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
