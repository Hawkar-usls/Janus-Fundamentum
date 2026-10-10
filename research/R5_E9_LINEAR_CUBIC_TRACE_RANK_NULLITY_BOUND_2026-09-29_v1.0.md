# R5 E9 — Linear Cubic Trace Rank / Nullity Bound

Date: 2026-09-29

Status:
`JANUS_EXACT_THEOREM__LINEAR_CUBIC_RATIONAL_NULLITY_AT_MOST_2_OVER_5_ASYMPTOTIC`

## 1. Setting

Let `A` be the `n x n` 0/1 incidence matrix of a symmetric `n_3` configuration, equivalently a square cubic linear Exact-One source:

```text
every row sum    = 3
every column sum = 3
any two distinct columns occur together in at most one row
```

(The dual row-intersection condition follows as well for a symmetric configuration, but the proof below only needs the column condition.)

Set

```text
B = A^T A.
```

## 2. Exact moment identities

Every diagonal entry of `B` equals 3. Therefore

```text
tr(B)=3n.
```

Fix a column `j` of `A`. It occurs in three source rows. Each such row contains two other columns. Linearity prevents any one of those six partners from repeating. Hence row `j` of `B` has

```text
B_jj = 3
exactly six off-diagonal entries equal to 1
all other entries equal to 0.
```

Therefore

```text
tr(B^2) = sum_{i,j} B_ij^2 = n(3^2+6) = 15n.
```

Also `A 1 = 3 1`, hence

```text
B 1 = A^T A 1 = 9 1.
```

So 9 is a nonzero eigenvalue of `B`.

## 3. Theorem

### Theorem LCT-1

For every square cubic linear source with `n>=7`,

```text
rank_Q(A) >= 1 + (3n-9)^2/(15n-81)
```

and hence

```text
nullity_Q(A)
<= floor( 2n(n-7)/(5n-27) ).
```

In particular,

```text
rank_Q(A) >= 3n/5
nullity_Q(A) <= 2n/5
```

by the coarser all-eigenvalue trace bound, and asymptotically the refined bound is

```text
nullity_Q(A) <= (2/5)n + O(1).
```

### Proof

Let the positive eigenvalues of the positive-semidefinite matrix `B=A^T A` be

```text
mu_1,...,mu_r,
```

where `r=rank(B)=rank(A)`. Reserve one known eigenvalue `mu_1=9`. The remaining `r-1` positive eigenvalues satisfy

```text
sum_{i=2}^r mu_i   = 3n-9
sum_{i=2}^r mu_i^2 = 15n-81.
```

Cauchy-Schwarz gives

```text
(3n-9)^2 <= (r-1)(15n-81).
```

Thus

```text
r >= 1 + (3n-9)^2/(15n-81).
```

Since `nu=n-r`, algebra gives

```text
nu <= 2n(n-7)/(5n-27).
```

`nu` is an integer, yielding the floor form.

The coarser bound follows directly from

```text
rank(B) >= tr(B)^2 / tr(B^2)
        = (3n)^2/(15n)
        = 3n/5.
```

Because `A` is rational/integer, its rank over `Q`, `R`, and `C` is the same. QED.

## 4. Spectral reformulation

Let `X` be the column-intersection graph: columns of `A` are vertices and two columns are adjacent iff they occur in one source row. Linearity makes `X` a simple 6-regular graph and

```text
A^T A = 3I + Adj(X).
```

Therefore

```text
nullity_Q(A) = multiplicity_X(-3).
```

The theorem is equivalently an upper bound on the `-3` eigenspace multiplicity in this triangle-decomposed 6-regular source graph.

Every source row contributes an edge-disjoint triangle of `X`, and the `n` source triangles partition `E(X)`.

## 5. Consequence for the live nullity router

The existing exact rational-nullity solver costs `2^nu * poly(n)` on this branch. LCT-1 changes the unconditional worst-case exponent from the trivial `nu<=n` to

```text
nu <= floor(2n(n-7)/(5n-27)) ~ 0.4n.
```

This is a genuine global structural restriction on all linear cubic sources, but it is still exponential and therefore does **not** establish a polynomial algorithm.

For the existing `PG15_SAT_R11` control,

```text
n=15
bound = floor(2*15*8/(75-27)) = 5
actual nullity_Q = 4.
```

So the theorem is compatible with the known post-RKPR positive hard control while leaving only one unit of slack there.

## 6. External context / anti-loop

A symmetric `n_3` configuration is exactly a 3-uniform 3-regular linear hypergraph; its Levi graph is cubic bipartite of girth at least six. This is a large classical class, not a finite exceptional family. The present proof is self-contained and does not depend on a classification theorem.

Do not infer any of the following:

```text
nu <= 0.4n => polynomial enumeration       FALSE
linearity => nu=O(log n)                   NOT PROVED
post-RKPR => stronger trace moments         NOT PROVED
-3 multiplicity bound => P=NP              FALSE
```

## 7. Next exact gate

The live strengthening question becomes:

```text
Can post-RKPR projective simplicity + source triangle structure
force a sublinear (ideally O(log n)) bound on the -3 eigenspace,
or yield a polynomial quotient without enumerating that eigenspace?
```

A counterfamily must simultaneously satisfy:

```text
linear n_3 source
connected
noncommuting two-permutation normalization
post-RKPR hostile
large rational nullity.
```

## 8. Ceiling

```text
LINEAR-CUBIC TRACE MOMENTS = EXACT
RANK >= 3n/5 = PROVED
REFINED NULLITY BOUND = PROVED
POST-RKPR SUBLINEAR NULLITY = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```
