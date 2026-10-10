# R5 E9 — Row-Basis Rank-3 Matching Router

Date: 2026-09-28

Status:
`JANUS_DERIVED_EXACT_FPT_ROUTER_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_1IN3_DUAL_HYPERGRAPH_MATCHING_THRESHOLD_2026-09-23_v1.0.md`

Checker:
- `experiments/r5_e9_row_basis_rank3_matching_router.py`

Scientific firewall:

```text
THIS STRICTLY IMPROVES THE CURRENT EXACT FPT ROUTER FOR THE CUBIC SQUARE CARRIER.
IT DOES NOT GIVE A POLYNOMIAL DECIDER WHEN THE NEW RANK-3 BASIS PARAMETER IS LARGE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

have every row and column of Hamming weight exactly three.  Let

```text
r = rank_Q(A),
k = n-r.
```

Choose `r` actual rows of `A` forming a rational row basis and let `B` be the resulting `r x n` matrix.  The existing row-basis theorem proves

```text
A x = 1_n  iff  B x = 1_r
```

for every real vector `x`, because every source row has the same row sum three.

For each column `j`, let

```text
m_j = number of basis rows containing j.
```

Every column is covered by the basis and every source column has total occurrence three, hence

```text
m_j in {1,2,3}.
```

Write

```text
N_t = {j : m_j=t},
n_t = |N_t|,
h = n_3.
```

Thus `N_1` are private variables, `N_2` are pair variables, and only `N_3` retain genuine rank-three occurrence in the basis system.

## 2. Exact counting identities

Because the basis has `r` rows of weight three,

```text
n_1+n_2+n_3 = n,
n_1+2n_2+3n_3 = 3r.
```

Subtracting gives

```text
n_2+2n_3 = 3r-n.
```

Using `r=n-k`, the existing overlap excess is

```text
delta = 3r-n = 2n-3k.
```

Therefore

\[
\boxed{\delta=n_2+2h}
\]

and in particular

\[
\boxed{h\le \delta/2 = n-\tfrac32 k.}
\]

The previous `2^delta` router branches on every shared variable in `N_2 union N_3`.  The theorem below shows that this is unnecessary: the complete `N_2` layer can be solved globally by ordinary matching after only `N_3` is fixed.

## 3. Fix only the rank-three basis variables

Enumerate an assignment

```text
alpha in {0,1}^{N_3}.
```

For every basis row `i`, define the residual demand

```text
b_i = 1 - sum_{j in N_3 intersect row(i)} alpha_j.
```

If `b_i` is negative, reject this branch.  Otherwise `b_i` is `0` or `1`.

All remaining variables occur in at most two basis rows:

- `j in N_2` occurs in exactly two basis rows;
- `j in N_1` occurs in exactly one basis row.

Thus the residual is an occurrence-`<=2` Positive Exact-One instance, but it is useful to spell out the exact matching projection because some rows already have residual demand zero.

## 4. Residual matching instance

Construct a graph `G_B(alpha)` whose vertices are the basis rows.

For each `j in N_2`, put one graph edge between the two basis rows containing `j`.  (For the linear source this graph is simple; the proof does not need simplicity.)

Let

```text
p_i = number of N_1 private variables in basis row i.
```

Classify basis-row vertices after fixing `alpha`:

```text
FORBIDDEN:  b_i=0,
MANDATORY:  b_i=1 and p_i=0,
OPTIONAL:   b_i=1 and p_i>0.
```

A residual satisfying assignment can select at most one `N_2` edge at any row, because the residual row demand is at most one.  Hence the selected `N_2` variables form a matching.

Rows behave exactly as follows:

- a FORBIDDEN row must be unmatched;
- a MANDATORY row must be matched, because it has no private variable available;
- an OPTIONAL row may be matched, or may remain unmatched and satisfy its unit residual demand by setting one of its private `N_1` variables to one.

Therefore the branch is feasible iff the graph induced by non-FORBIDDEN rows has a matching saturating every MANDATORY row.

Finding a matching saturating a prescribed vertex set is polynomial by ordinary general-graph matching.  Equivalently, give each graph edge weight equal to the number of its mandatory endpoints (`0,1,2`) and compute a maximum-weight matching; the branch succeeds iff the optimum weight is exactly the number of mandatory vertices.

## 5. Exact reconstruction

Given a saturating matching `M`:

1. keep the fixed values `alpha` on `N_3`;
2. set `x_j=1` exactly for `N_2` variables whose graph edge is in `M`;
3. for every unmatched OPTIONAL row, set one canonical private `N_1` variable of that row to one;
4. set every other `N_1 union N_2` variable to zero.

Then every basis row has sum exactly one, so

```text
B x = 1_r.
```

By the row-basis affine-span theorem,

```text
A x = 1_n.
```

Thus witness reconstruction is deterministic and polynomial after the branch assignment.

## 6. Correctness theorem

### Theorem RBR3-1 — exact `2^h` router

For every cubic square source matrix `A` and every actual-row rational basis `B`, Boolean Exact-One satisfiability is decidable in

\[
\boxed{2^h\operatorname{poly}(n,L)}
\]

where `h` is the number of columns occurring in all three of their source rows inside the chosen basis (`m_j=3`).

### Proof

Completeness: let `x` satisfy `B x=1`.  Restrict it to `N_3`; the corresponding enumerated branch is reached.  The selected `N_2` variables form a matching because no basis row can contain two selected residual variables.  Every MANDATORY row has residual demand one and no private variable, so it is saturated by that matching.  Hence the matching test accepts.

Soundness: if a branch matching saturating all MANDATORY rows exists, the reconstruction in Section 5 produces a Boolean vector satisfying every basis row exactly once.  The affine row-span theorem then upgrades `Bx=1` to `Ax=1`.

Termination and complexity: there are exactly `2^h` branch assignments.  Each branch performs polynomial bookkeeping plus one polynomial general-graph matching computation.  Reconstruction and direct verification are polynomial. QED.

## 7. Strict improvement over the overlap-excess router

Since

```text
delta = n_2 + 2h,
```

we have

```text
h <= delta/2.
```

Therefore the row-basis side now has the exact bound

\[
\boxed{T_{basis}(A)\le 2^{\delta/2}\operatorname{poly}(n,L).}
\]

This strictly dominates the previous generic `2^delta` enumeration whenever `delta>0`.

In particular:

```text
h=0       -> deterministic polynomial matching terminal,
h=O(log n)-> deterministic polynomial-time branch-and-match router.
```

The `h=0` case is the exact basis-level occurrence-`<=2` collapse to matching.

## 8. Universal exact exponential bound

The existing rational-kernel router gives

\[
T_{ker}(A)=2^k\operatorname{poly}(n,L).
\]

Run the better of the kernel router and RBR3-1.  Since

\[
h\le \frac{2n-3k}{2}=n-\frac32k,
\]

we obtain

\[
T(A)
\le
2^{\min(k,h)}\operatorname{poly}(n,L)
\le
2^{\min(k,n-\frac32 k)}\operatorname{poly}(n,L).
\]

For `0<=k<=2n/3`, the maximum of the final exponent occurs where

```text
k = n - 3k/2,
```

namely

```text
k = 2n/5.
```

Hence

\[
\boxed{T(A)\le 2^{2n/5}\operatorname{poly}(n,L).}
\]

This replaces the previous worst-case `2^{n/2}` consequence of `min(k,delta)` by `2^{2n/5}`.

This is a genuine universal exact-algorithm improvement, but remains exponential and therefore is not a D1/P=NP promotion.

## 9. Sharpened residual

The old middle-nullity residual

```text
k = omega(log n)
and
delta = omega(log n)
```

is no longer the sharp frontier.

After this theorem, polynomial failure of the two current universal routers requires

```text
k = omega(log n)
and
h = omega(log n),
```

where `h` counts only basis columns with multiplicity three.

All multiplicity-two overlap can be absorbed globally by matching rather than branched.

The next admissible target is therefore not generic shared-variable compression.  It is specifically the all-or-none coupling carried by the surviving `m_j=3` columns, or a different global carrier that bypasses them.

Freeze candidate gate:

```text
R5_E9_ROW_BASIS_RANK3_GLOBAL_COUPLING_GATE_V1
```

PASS requires one of:

1. polynomial absorption/contraction of the `m_j=3` basis columns;
2. a polynomially constructible basis with `h=O(log n)` for every source instance;
3. another exact polynomial terminal for the residual;
4. a stronger exact router with a strictly smaller universal exponent and a proved progress measure.

Forbidden pseudo-progress:

- branch on all `N_2` variables;
- reintroduce `2^delta` enumeration after the matching projection;
- replace one `m_j=3` variable by three independent pair edges;
- call the new `2^{2n/5}` exact algorithm polynomial.

## 10. Ceiling

```text
ROW-BASIS MULTIPLICITY PARTITION N1/N2/N3 = PROVED
N2 RESIDUAL AFTER FIXING N3 = ORDINARY MATCHING = PROVED
EXACT ROUTER 2^h poly(n) = PROVED
h <= delta/2 = PROVED
UNIVERSAL EXACT BOUND 2^(2n/5) poly(n) = PROVED

POLYNOMIAL ABSORPTION OF GENERAL N3 COUPLING = OPEN
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```