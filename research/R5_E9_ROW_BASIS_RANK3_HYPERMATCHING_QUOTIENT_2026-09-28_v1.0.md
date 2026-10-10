# R5 E9 — Row-basis rank-3 hypermatching quotient

Date: 2026-09-28

Status:
`JANUS_DERIVED_EXACT_SEMANTIC_QUOTIENT_AND_FPT_ROUTER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_EQ3_MID_NULLITY_HARDNESS_SLAB_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_row_basis_rank3_hypermatching_quotient.py`

Scientific firewall:

```text
THIS IS AN EXACT GLOBAL SEMANTIC QUOTIENT.
IT IMPROVES THE HIGH-k / OVERLAP ROUTER BUT DOES NOT CLOSE THE NP-COMPLETE
CONSTANT-RATIO HARDNESS SLAB.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Basis hypergraph

Let `A` be the `n x n` cubic Exact-One incidence matrix and choose any actual-row
rational basis

```text
B in {0,1}^{r x n},
r = rank_Q(A),
k = n-r.
```

As proved by the parent row-basis theorem,

```text
Ax=1 over Boolean x
iff
Bx=1 over Boolean x.
```

Create a hypergraph `H_B` whose vertex set is the `r` basis rows.  For each
variable/column `j`, create one hyperedge

```text
E_j = {basis rows containing column j}.
```

Every column is covered by at least one basis row, and every original column has
total degree three, so

```text
1 <= |E_j| <= 3.
```

Every basis row contains exactly three variables, hence every vertex of `H_B`
has hypergraph degree exactly three.

If the original carrier is linear, then `H_B` is linear as well: two distinct
column-hyperedges cannot meet in two basis-row vertices, because that would mean
two original clauses share two variables.

## 2. Exact-cover equivalence

For Boolean `x`, the equation on a basis row says that exactly one column
incident with that row has value one.  Therefore

```text
Bx=1
iff
{E_j : x_j=1} is a family of pairwise disjoint hyperedges covering every
basis-row vertex exactly once.
```

Thus the entire rational row-basis core is exactly a perfect-matching / exact-
cover problem in a linear rank-at-most-three hypergraph.

This quotient is semantic: no clause, variable, or Boolean feasibility condition
is relaxed.

## 3. Multiplicity census

Let

```text
p = number of columns with |E_j|=1,
s = number of columns with |E_j|=2,
t = number of columns with |E_j|=3.
```

Then

```text
p+s+t = n.
```

Counting incidences in the `r` basis rows gives

```text
p+2s+3t = 3r = 3(n-k).
```

Therefore

\[
\boxed{3k=2p+s.}
\]

The overlap-excess parameter from the parent theorem is

```text
delta = sum_j(|E_j|-1) = s+2t,
```

so

\[
\boxed{\delta=s+2t.}
\]

Subtracting gives the useful exact identity

\[
\boxed{t-p=n-3k.}
\]

These identities hold for every actual-row rational basis, although the
individual values `p,s,t` may depend on which basis is chosen.

## 4. Fixing only the genuine rank-3 choices

Let `T` be the set of the `t` size-three hyperedges.
Enumerate the Boolean selected/unselected state of only these hyperedges.
There are `2^t` states.

For one state:

1. reject if two selected size-three hyperedges intersect;
2. let `C` be the basis-row vertices covered by selected size-three hyperedges;
3. delete `C`, all size-one/size-two hyperedges meeting `C`, and all unselected
   size-three hyperedges.

The remaining instance contains only:

```text
size-one hyperedges (singletons),
size-two hyperedges (ordinary graph edges).
```

Let `U` be the remaining vertices and let

```text
M = {u in U : u has no available singleton hyperedge}.
```

Vertices in `M` must be covered by size-two edges.  Vertices outside `M` may be
covered by a size-two edge or left unmatched and then covered by a singleton.

## 5. Polynomial residual by weighted matching

Build the ordinary graph on `U` whose edges are the remaining size-two
hyperedges.  Give an edge `uv` weight

```text
w(uv) = 1[u in M] + 1[v in M].
```

For any graph matching, its total weight is exactly the number of mandatory
vertices in `M` that the matching covers, because matching edges are disjoint.

Therefore a completion exists iff a maximum-weight matching has weight exactly

```text
|M|.
```

Maximum-weight matching in a general graph is polynomial-time solvable.  If the
weight reaches `|M|`, use the matching edges as selected size-two variables and
cover every remaining unmatched optional vertex by one of its singleton
variables.

This reconstructs a full exact cover of the basis-row vertices and hence, by the
row-span theorem, a Boolean witness for `Ax=1`.

## 6. Exact FPT theorem

### Theorem RHQ-1

For any chosen actual-row rational basis `B`, cubic Exact-One is decidable and
witness-constructible in

\[
\boxed{2^{t_B}\operatorname{poly}(n,L)}
\]

bit operations, where `t_B` is the number of columns that occur in all three of
their original rows inside that basis.

The algorithm is sound and complete by Sections 2, 4 and 5.

Since

```text
delta = s+2t,
```

we always have

```text
t <= delta/2.
```

Thus this router strictly subsumes the raw `2^delta` shared-variable enumeration
as an exponential upper bound for the same chosen row basis:

\[
2^t \le 2^{\delta/2} \le 2^\delta.
\]

In particular

```text
t_B = O(log n)
```

is another exact polynomial island.

## 7. Why basis optimization cannot rescue the hard slab

From

```text
t-p=n-3k
```

and `p>=0`, every actual-row basis obeys

\[
\boxed{t_B\ge n-3k.}
\]

The existing EQ3 hardness-slab theorem gives, on every image instance,

```text
n/10 <= k <= n/6.
```

Therefore every actual-row basis of every such hard image satisfies

\[
\boxed{t_B\ge n/2.}
\]

So the following escape route is impossible on that slab:

```text
choose a clever rational row basis so that only O(log n) size-three
hyperedges remain, then solve the rest by graph matching.
```

The obstruction is basis-independent and linear-density.

This does not prove that no different semantic quotient exists.  It proves that
the most direct rank-3-to-graph-matching collapse cannot become universal merely
by rechoosing the actual-row basis.

## 8. Sharpened residual

The current exact front end may now use

```text
2^k poly(n,L),
2^t_B poly(n,L),
```

with `t_B<=delta/2`; the old `2^delta` route remains valid but is no longer the
best exponent supplied by the row-basis representation.

A surviving family for a fixed deterministic basis rule must satisfy

```text
k = omega(log n),
t_B = omega(log n).
```

On the NP-complete EQ3 hardness slab the stronger basis-independent condition is
already

```text
t_B >= n/2 for every actual-row basis.
```

Freeze the next global target as

```text
R5_E9_LINEAR_DENSITY_RANK3_HYPERMATCHING_GLOBAL_QUOTIENT_GATE_V1
```

The new target is not local degree stripping.  It is a polynomial exact rule for
the linear-density family of size-three hyperedges while preserving the graph-
matching residual semantics.

## 9. Ceiling

```text
ROW-BASIS CORE
= EXACT RANK<=3 HYPERGRAPH PERFECT MATCHING
= PROVED

MULTIPLICITY IDENTITIES
3k=2p+s
delta=s+2t
t-p=n-3k
= PROVED

FIX SIZE-3 CHOICES
=> POLYNOMIAL WEIGHTED-MATCHING RESIDUAL
= PROVED

EXACT ROUTER
2^t_B poly(n,L)
= PROVED

HARD SLAB
k<=n/6 => t_B>=n/2 FOR EVERY BASIS
= PROVED

GRAPH-MATCHING COLLAPSE BY BASIS RECHOICE
= FALSIFIED ON THE HARD SLAB

LINEAR-DENSITY SIZE-3 GLOBAL QUOTIENT
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```