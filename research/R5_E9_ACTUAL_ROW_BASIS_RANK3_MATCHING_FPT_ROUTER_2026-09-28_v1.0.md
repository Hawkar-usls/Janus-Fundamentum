# R5 E9 — Actual-Row-Basis Rank-3 Matching FPT Router

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_FPT_ROUTER__RANK3_BASIS_CORE_ENUMERATION_PLUS_MATCHING__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS ADDS AN EXACT SOLVER PARAMETER FOR THE ACTUAL-ROW-BASIS CORE.
IT DOES NOT PROVE THAT THE PARAMETER IS O(log n) ON ALL INSTANCES.
IT DOES NOT SUPPLY A UNIVERSAL POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_1IN3_DUAL_HYPERGRAPH_MATCHING_THRESHOLD_2026-09-23_v1.0.md`
- `research/R5_E9_DEFECT_FREE_TWO_EDGE_UNSAT_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_actual_row_basis_rank3_matching_router.py`

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

have every row and column of weight exactly three. Let

```text
r = rank_Q(A),
k = n-r.
```

Choose `r` **actual rows of A** forming a rational row basis and let

```text
B in {0,1}^{r x n}
```

be the resulting matrix.

The parent row-basis theorem proves two facts used below:

1. every column of `B` has positive support;
2. for every real vector `x`,

```text
A x = 1_n  iff  B x = 1_r.
```

The second statement uses the constant row sum three: every omitted row is an affine combination of the retained actual rows with coefficient sum one.

Therefore solving Boolean Exact-One for `A` is exactly the same decision/search problem as solving

```text
B x = 1_r,
x in {0,1}^n.
```

## 2. The actual-row-basis hypergraph

For each column `j`, define its basis multiplicity

```text
m_j = |supp(B[:,j])|.
```

Because `B` consists of actual rows of the cubic source and every column is covered,

```text
m_j in {1,2,3}.
```

Let

```text
C1 = {j : m_j=1},
C2 = {j : m_j=2},
C3 = {j : m_j=3},

a=|C1|,
b=|C2|,
c=|C3|.
```

Interpret the `r` retained rows as vertices and each source column `j` as a hyperedge consisting of the rows in which it occurs in `B`. Then:

```text
B x = 1_r
```

iff the columns with `x_j=1` form an exact partition of the `r` basis-row vertices by hyperedges of sizes 1, 2 and 3.

Thus the actual-row-basis semantic core is an exact-cover instance of rank at most three, with the rank-3 columns isolated explicitly as `C3`.

## 3. Counting identities

Every source column belongs to exactly one of `C1,C2,C3`, so

```text
a+b+c=n.
```

Every retained basis row has exactly three incidences, so

```text
a+2b+3c=3r.
```

Using `r=n-k`, subtraction gives

```text
2a+b=3k.
```

The parent overlap-excess parameter is

```text
delta = 3r-n = 2n-3k.
```

Combining with the same identities gives

```text
b+2c=delta.
```

Hence

\[
\boxed{
2a+b=3k,
\qquad
b+2c=2n-3k.
}
\]

These identities are exact for every actual rational row basis.

## 4. Fixing the rank-3 columns leaves ordinary matching

Enumerate a candidate subset

```text
T subseteq C3
```

of rank-3 columns to be selected.

Reject `T` immediately if two selected 3-columns share a basis-row vertex. Otherwise let

```text
U_T
```

be the basis rows covered by `T` and remove those rows from the residual problem.

Any rank-2 column touching `U_T` is now forbidden, because selecting it would cover an already covered row twice. The remaining rank-2 columns form an ordinary graph

```text
G_T=(V_T,E_T),
V_T = basis rows \ U_T.
```

A residual row `v in V_T` is called **optional** if it has at least one rank-1 column in `C1`; otherwise it is **mandatory**.

Let

```text
M_T = {mandatory residual rows}.
```

### Lemma RB3-1

The fixed choice `T` extends to an Exact-One solution iff `G_T` has a matching saturating every vertex in `M_T`.

### Proof

Suppose an Exact-One completion exists. Its selected rank-2 columns are pairwise vertex-disjoint and cannot touch `U_T`, hence form a matching in `G_T`. Every mandatory residual row has no rank-1 escape, so it must be covered by that matching. Thus the matching saturates `M_T`.

Conversely, let `M` be a matching of `G_T` saturating `M_T`. Select the rank-2 columns corresponding to `M`. Every residual row not covered by `M` is optional by definition, so choose one canonical rank-1 column incident with that row. Rank-1 columns cover no other basis row, hence these choices cannot conflict. Together with `T`, every basis row is covered exactly once. Therefore `Bx=1`, and by the actual-row-basis affine-span theorem also `Ax=1`. QED.

Finding a matching saturating a prescribed vertex set is polynomial-time solvable, for example by standard general-graph matching machinery (equivalently by a maximum-weight matching formulation assigning sufficiently large endpoint weight to prescribed vertices).

## 5. Exact `2^c` algorithm

Algorithm:

```text
1. Compute an actual rational row basis B.
2. Partition columns into C1,C2,C3.
3. For every T subseteq C3:
     a. reject T if its 3-hyperedges are not vertex-disjoint;
     b. delete the rows covered by T;
     c. build G_T from surviving rank-2 columns;
     d. mark residual rows without rank-1 columns mandatory;
     e. find a matching saturating all mandatory rows;
     f. if found, fill each unmatched optional row by a canonical rank-1 column
        and return the resulting Exact-One witness.
4. If no T succeeds, return UNSAT.
```

There are exactly `2^c` candidate subsets. Every residual matching instance and every reconstruction step has polynomial bit/time complexity. Therefore:

### Theorem RB3-2

Cubic square Exact-One is decidable, with a witness constructible, in

\[
\boxed{2^c\operatorname{poly}(n,L)}
\]

where `c` is the number of multiplicity-3 columns in an actual rational row basis and `L` is the exact-arithmetic encoding budget for constructing that basis.

The algorithm is sound and complete by Lemma RB3-1 and by `Bx=1 iff Ax=1`.

## 6. Polynomial terminal at c=O(log n)

If

```text
c = O(log n),
```

the algorithm is polynomial. In particular

```text
c=0
```

reduces the entire actual-row-basis core to one prescribed-vertex matching problem with rank-1 fill-ins.

This is a genuine new polynomial island. It is different from the parent routers:

```text
LOW-k route:        2^k poly(n,L)
OVERLAP route:      2^(b+c) <= 2^delta poly(n,L)
RANK3 route:        2^c poly(n,L)
```

The rank-3 route does not enumerate multiplicity-2 columns; matching handles them globally.

## 7. Why this does not yet close the universal bottleneck

No theorem currently proves

```text
c=O(log n)
```

for an arbitrary hard residual or for an optimally chosen actual row basis.

Indeed the exact identities permit all of `k`, `delta`, and `c` to be linear simultaneously. The source class itself is NP-complete, and rank-3 exact cover is the known first hard rank above ordinary matching. Therefore the existence of the compact rank-3 parameter must not be confused with a universal polynomial bound on it.

The next universal obligation is consequently **not** to enumerate `C3` faster by another disguised Boolean branch. It is to eliminate/contract rank-3 basis columns globally, or to prove a polynomially constructible basis/representation in which the non-matching residue collapses without enumerating its states.

## 8. Basis-complement interpretation

Let `R` be the selected row basis and `O` its omitted-row complement, so `|O|=k`. A source column belongs to `C3` exactly when none of its three incident rows lies in `O`.

Because every omitted row has source degree three, the omitted rows contribute exactly `3k` incidences into source columns. Since the retained basis covers every column, no source column can have all three incident rows in `O`.

For a linear source, if `a` columns meet `O` twice, each such column corresponds to one pair of omitted rows that intersect in that column. The identity

```text
c = n-3k+a
```

is another form of Section 3.

Thus choosing an actual row basis to minimize `c` is equivalently a constrained basis-complement coverage problem: choose a dual row-matroid basis `O` that hits as many source-column triples as possible while minimizing double hits. No polynomial optimizer for this source-specific objective is assumed here.

## 9. Updated frontier

Freeze:

```text
R5_E9_ACTUAL_ROW_BASIS_RANK3_GLOBAL_ELIMINATION_GATE_V1
```

Input:

```text
actual-row-basis exact-cover core,
rank-1 columns handled for free,
rank-2 columns handled by ordinary matching,
rank-3 columns C3 remaining.
```

Target: deterministically and in polynomial total time do at least one of:

1. contract a nonempty set of rank-3 columns while preserving exact SAT equivalence and polynomial witness reconstruction;
2. transform the whole rank-3 layer into a proved polynomial carrier without an exponential selector;
3. construct an actual row basis with `c=O(log n)` for every source-valid residual;
4. produce a different global certificate that decides the component directly.

Forbidden:

- enumerate `2^c` and call it polynomial when `c` is linear;
- replace one 3-hyperedge by independent graph edges;
- hide the same three-way selection behind a fresh local matching selector;
- assume that a favorable row basis exists without a polynomial construction theorem.

## 10. Ceiling

```text
ACTUAL ROW BASIS EXACT-COVER CORE
= PROVED

COUNTS
2a+b=3k,
b+2c=delta
= PROVED

FIXED RANK-3 SELECTION
=> PRESCRIBED-VERTEX MATCHING
= PROVED

EXACT ROUTER
2^c poly(n,L)
= PROVED

c=O(log n) TERMINAL
= POLYNOMIAL

UNIVERSAL RANK-3 ELIMINATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```