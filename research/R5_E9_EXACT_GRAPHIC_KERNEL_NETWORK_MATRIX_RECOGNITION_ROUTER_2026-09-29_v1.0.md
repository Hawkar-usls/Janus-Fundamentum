# R5 E9 — Exact Graphic-Kernel Network-Matrix Recognition Router

Date: 2026-09-29

Status:
`JANUS_CONSTRUCTIVE_POLYNOMIAL_ROUTER__EXACT_GRAPHIC_KERNEL_RECOGNITION_CLOSED`

## 1. Purpose

The companion theorem

```text
R5_E9_GRAPHIC_KERNEL_Z3_PHASE_EXACT_SOLVER_ISLAND
```

proves that Exact-One is polynomial-time solvable once the rational kernel is supplied as an exact graph coboundary space

```text
ker_Q(A)=col_Q(H).
```

This note closes the recognition/recovery obligation by reducing it to standard network-matrix recognition.

The result creates a fully constructive polynomial router branch. It is **not** a universal SAT solver: sources whose kernel fails the network test are passed onward to the remaining open branch.

## 2. Input kernel representation

Compute a rational kernel basis of `A` and place the basis vectors as columns of

```text
B in Q^{n x d},
col(B)=ker_Q(A),
d=nullity_Q(A).
```

Transpose:

```text
R = B^T in Q^{d x n}.
```

Thus

```text
row_Q(R)=ker_Q(A)^T
```

as a coordinate subspace on the `n` variables.

The `d=0` terminal and a zero coordinate functional are already handled separately by the existing rational-kernel router. Below assume `d>0` and no zero coordinate row of `B`.

## 3. Pivot normalization

Using exact Gaussian elimination, choose any set `T` of `d` linearly independent columns of `R`. Let

```text
R_T
```

be the resulting nonsingular `d x d` submatrix. Reorder columns so `T` comes first and compute

```text
F = R_T^{-1} R = [ I_d | N ].
```

All operations are rational and polynomial in the bit-size of `A`.

## 4. Exact recognition theorem

### Theorem EGK-NET-1

The following are equivalent.

#### (A) Exact graphic kernel

There exists an oriented graph `G=(V,E)` with variables identified with its edges, and an edge-vertex incidence matrix `H`, such that

```text
ker_Q(A)=col_Q(H).
```

After deleting one redundant vertex row from each connected component, let

```text
D = H^T_reduced
```

be a full-row-rank vertex-edge incidence matrix.

#### (B) Network normalization

The normalized nonbasis matrix `N` is a network matrix: there exists a directed graph with a spanning forest whose reduced incidence matrix partitions as

```text
D = [ D_T | D_N ]
```

with `D_T` nonsingular and

```text
N = D_T^{-1} D_N.
```

Hence exact graphic-kernel recognition and recovery reduce to network-matrix recognition.

## 5. Proof: exact graphic kernel => network matrix

Assume (A). Since `R` and `D` have the same row space and the same row rank `d`, there is an invertible rational matrix `S` such that

```text
R = S D.
```

The chosen columns `T` are independent in `R`, hence independent in `D`. In a graphic matroid a full column basis of a reduced incidence matrix is a spanning forest, so `D_T` is nonsingular.

Therefore

```text
R_T = S D_T
```

and

```text
R_T^{-1} R
= (S D_T)^{-1} S D
= D_T^{-1} D
= [ I | D_T^{-1}D_N ].
```

Thus

```text
N=D_T^{-1}D_N
```

is a network matrix.

This argument works for **any** pivot basis `T`; no exponential search over kernel bases is required.

## 6. Proof: network matrix => exact graphic kernel

Assume a network-matrix recognizer returns a graph and spanning forest representation

```text
N=D_T^{-1}D_N.
```

Then

```text
F=[I|N]
 = D_T^{-1}[D_T|D_N]
 = D_T^{-1}D.
```

Therefore

```text
row(F)=row(D).
```

Left multiplication by the nonsingular `R_T^{-1}` does not change row space, so

```text
row(R)=row(F)=row(D).
```

Transposing back gives exactly

```text
ker_Q(A)=col_Q(D^T).
```

Restore one redundant incidence row per component if desired and set `H=D^T`. This is the exact coordinate-compatible coboundary representation required by GKZ3-1.

No coordinate-wise projective scaling is being silently accepted: the equality is an equality of rational row spaces after the actual pivot normalization.

## 7. Polynomial algorithm

The router is:

```text
INPUT: Exact-One source matrix A

1. Compute exact rational kernel basis B.
2. Handle d=0 / zero-coordinate terminals already known to the router.
3. Set R=B^T.
4. Select d pivot columns T by Gaussian elimination.
5. Compute F=R_T^{-1}R=[I|N].
6. Run a polynomial network-matrix recognition algorithm on N.

   if REJECT:
       return NOT_IN_GRAPHIC_KERNEL_BRANCH
       (do not conclude SAT/UNSAT)

   if ACCEPT with graph/forest representation:
       recover incidence H with col(H)=ker_Q(A)
       run the GKZ3 phase algorithm
       return its exact SAT/UNSAT result and witness/cycle certificate.
```

Network-matrix recognition is a classical polynomial problem. Constructive algorithms and modern implementations explicitly return graph realizations; this is the only external algorithmic donor required by Step 6.

## 8. Complexity contract

Let `L` be the bit-size of the input matrix.

```text
kernel basis / rank / pivots      polynomial(L)
rational normalization            polynomial(L)
network-matrix recognition        polynomial(L)
incidence recovery                polynomial(L)
Z3 phase traversal                O(|V|+|E|)
witness reconstruction/verify     polynomial(L)
```

Therefore the recognized branch satisfies

```text
D1-SOUND      PASS on admitted branch
D1-COMPLETE   PASS on admitted branch
D1-TERMINATES PASS on admitted branch
D1-POLY       PASS on admitted branch
```

The universal D1 contract remains open because `NOT_IN_GRAPHIC_KERNEL_BRANCH` instances still require another polynomial route.

## 9. Positive control: Paley minus-two family

For every member of

```text
R5_E9_PALEY_MINUS2_ORBIT_POST_RKPR_SQRT_NULLITY_FAMILY
```

the theorem already proves

```text
ker_Q(A_q)=col_Q(H_q).
```

Therefore pivot normalization must be a network representation. On the `q=11` member, an arbitrary rational nullspace basis normalized on Gaussian pivot columns yields only `0,±1` entries and exactly matches the normalized reduced incidence representation of the selected Paley graph.

The router thus recognizes a family with

```text
nullity_Q(A_q)=q-1 > sqrt(2n)-1,
```

showing that the branch is not merely a low-nullity special case.

## 10. Negative control: PG15

Use the canonical PG15 rational kernel basis already stored in the R5 E9 controls. Pivot normalization gives a `4 x 15` matrix whose entries happen all to lie in `0,±1`; that entry test alone is therefore insufficient.

For the four pivot/tree rows, an exhaustive small-control realization check over

```text
5^(5-2)=125 labelled trees
x 2^4=16 tree orientations
```

finds no directed-tree path realization for all normalized columns. Hence the PG15 kernel is not admitted by this exact network branch under that control.

This is desirable: the router extracts a genuine structural island rather than silently reclassifying the known hard positive control.

## 11. Literature binding

Polynomial graph/network realization is classical. Relevant donor lines include:

- Bixby and Wagner, *An Almost Linear-Time Algorithm for Graph Realization*, Mathematics of Operations Research 13(1), 1988.
- Musitelli, *Recognition of generalized network matrices*, 2008, including polynomial recognition procedures for network/binet representations.
- van der Hulst and Walter, *A Row-wise Algorithm for Graph Realization*, 2024/2025.
- CMR / MATREC implementations of graphic and network matrix recognition.

The JANUS-specific step is the pivot-normalization equivalence connecting those algorithms to the **exact rational kernel subspace** needed by the Exact-One Boolean embedding.

## 12. New live frontier

The old route

```text
make nullity small after RKPR
```

is closed by the Paley family.

The new structural router now solves

```text
arbitrarily large exact graphic/coboundary kernels.
```

The remaining universal question becomes:

```text
Can every post-RKPR source kernel be routed in polynomial time into
  (a) network/graphic coboundary,
  (b) another polynomially recognizable representation class,
  or (c) a polynomial obstruction/certificate class,
without an exponential residual?
```

Recommended next gate:

```text
R5_E9_KERNEL_REPRESENTATION_DECOMPOSITION_BEYOND_NETWORK_GATE_V1
```

with immediate donors:

```text
regular/TU decomposition
signed-graphic / binet / bidirected representations
source-specific 2/3-sum composition
```

subject to the permanent Exact-One semantic firewall.

## 13. Ceiling

```text
EXACT GRAPHIC-KERNEL RECOGNITION = POLYNOMIAL
EXACT H RECOVERY = POLYNOMIAL
GKZ3 SAT/UNSAT ON RECOGNIZED BRANCH = POLYNOMIAL
HIGH-NULLITY PALEY FAMILY = COVERED
PG15 = NOT COVERED BY THIS ROUTER
UNIVERSAL REPRESENTATION DECOMPOSITION = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
