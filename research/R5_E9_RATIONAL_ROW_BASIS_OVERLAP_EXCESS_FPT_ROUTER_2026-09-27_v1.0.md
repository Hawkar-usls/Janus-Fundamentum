# R5 E9 — Rational Row-Basis Overlap-Excess FPT Router

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_FPT_ROUTER_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_rational_row_basis_overlap_excess_fpt_router.py`

Parents:
- `R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS A SECOND EXACT FPT ISLAND FOR CUBIC EXACT-ONE.
IT DOES NOT COVER THE MIDDLE-NULLITY BAND.
IT DOES NOT PROVE A UNIVERSAL POLYNOMIAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

have every row and every column of Hamming weight exactly three.  The associated
Boolean Exact-One problem asks for

```text
x in {0,1}^n
such that
A x = 1_n
```

over the integers.

Write

```text
r = rank_Q(A),
k = n-r = nullity_Q(A).
```

The parent nullity router gives an exact `2^k poly(n,L)` algorithm by
parameterizing the rational kernel.  This note gives a second exact router from
the opposite end of the possible nullity range.

## 2. Choose an actual-row rational basis

Choose indices

```text
i_1,...,i_r
```

such that the corresponding **actual rows of A** form a basis of the rational
rowspace.  Let

```text
B in {0,1}^{r x n}
```

be this row-basis matrix.

This can be done deterministically in polynomial bit complexity by exact
Gaussian elimination over `Q` while retaining original row indices.

### Lemma RBO-1 — every column is covered by the basis rows

Every column of `B` contains at least one `1`.

### Proof

Suppose column `j` were zero in every basis row.  Every row of `A` is a rational
linear combination of the basis rows, so every row of `A` would then also be
zero in column `j`.  This contradicts the hypothesis that column `j` of `A` has
weight three. QED.

Because every basis row has exactly three ones, the `r` basis rows contain
exactly `3r` incidences and cover all `n` columns.  Therefore

```text
n <= 3r
```

and hence

```text
k=n-r <= 2n/3.
```

So `2n/3` is an unconditional upper bound on the rational nullity of every
square row/column-weight-three incidence matrix.

## 3. Exact overlap-excess parameter

For each variable/column `j`, let

```text
m_j = number of basis rows containing j.
```

By Lemma RBO-1,

```text
m_j >= 1.
```

Since the basis contains `r` rows of weight three,

```text
sum_j m_j = 3r.
```

Define the **row-basis overlap excess**

```text
delta := 3r-n.
```

Then exactly

```text
delta = sum_j (m_j-1).
```

Using `r=n-k`,

```text
delta
= 3(n-k)-n
= 2n-3k.
```

Thus

\[
\boxed{\delta=3\operatorname{rank}_{\mathbb Q}(A)-n
      =2n-3\nu_{\mathbb Q}(A).}
\]

Let

```text
H = {j : m_j >= 2}
```

be the variables shared by two or more basis rows.  Every member of `H`
contributes at least one unit to the excess, so

```text
|H| <= delta.
```

Every variable outside `H` occurs in exactly one basis row and is called
**private**.

## 4. Why solving only the basis rows is exact

The crucial point is that `B x = 1_r` is not merely a relaxation.

### Lemma RBO-2 — affine right-hand side is preserved by the row span

For every real vector `x`,

```text
A x = 1_n
iff
B x = 1_r.
```

### Proof

The forward direction is immediate because every row of `B` is an actual row
of `A`.

For the reverse direction, take any row `a_i` of `A`.  Since the rows of `B`
span the rational rowspace, there is a rational coefficient vector `lambda_i`
such that

```text
a_i = lambda_i^T B.
```

Every row of `A`, including every row of `B`, has row sum exactly three.  Hence

```text
3
= a_i 1
= lambda_i^T B 1
= 3 lambda_i^T 1.
```

Therefore

```text
lambda_i^T 1 = 1.
```

If `B x = 1_r`, then

```text
a_i x
= lambda_i^T B x
= lambda_i^T 1_r
= 1.
```

This holds for every row `a_i`, so `A x=1_n`. QED.

The constant row sum is essential: it is what turns arbitrary rational row-span
coefficients into an affine combination with coefficient sum one.

## 5. Exact `2^delta` solver

Enumerate only the Boolean values of the shared variables `H`.  There are at
most

```text
2^|H| <= 2^delta
```

patterns.

Fix one pattern.  Consider a basis row.  Its shared variables already have
values.  Let their sum be `s`.

There are only three cases:

1. `s >= 2`:
   the row can never sum to exactly one; reject this shared pattern.

2. `s = 1`:
   set every private variable of the row to zero.

3. `s = 0`:
   - if the row has no private variable, reject the pattern;
   - otherwise set one canonical private variable of that row to one and all
     other private variables of the row to zero.

Private variables are contained in exactly one basis row.  Therefore the
completion chosen in one basis row cannot change any other basis equation.

If every basis row is completed successfully, the resulting Boolean vector
satisfies

```text
B x = 1_r.
```

By Lemma RBO-2 it therefore satisfies

```text
A x = 1_n.
```

Conversely, every Exact-One solution induces one of the enumerated shared
patterns, so the procedure is complete.

### Theorem RBO-3 — overlap-excess FPT router

Cubic square Exact-One is decidable, with a witness constructible, in

\[
\boxed{2^{\delta}\operatorname{poly}(n,L)}
\]

bit operations, where

\[
\boxed{\delta=3r-n=2n-3k.}
\]

Here `L` denotes the exact-arithmetic encoding budget incurred by rational
Gaussian elimination.  For a 0/1 `n x n` matrix this budget remains polynomial
in `n` by standard determinant/bit-length bounds.

Witness verification and reconstruction are linear in the incidence size once
a successful shared pattern is found.

## 6. Maximal-nullity terminal

From Lemma RBO-1,

```text
k <= 2n/3.
```

If equality holds, then

```text
k = 2n/3,
r = n/3,
delta = 0.
```

Since

```text
delta=sum_j(m_j-1)=0
```

and every `m_j>=1`, every variable occurs in exactly one basis row.  Thus the
basis rows partition all variables into disjoint triples.

Choose one variable in each basis row and set all other variables to zero.
Then `B x=1`, hence by Lemma RBO-2 also `A x=1`.

Therefore:

\[
\boxed{
\nu_{\mathbb Q}(A)=2n/3
\Longrightarrow
\text{Exact-One is SAT, with a deterministic polynomial witness.}
}
\]

This extremal theorem does not require linearity or connectedness.  The checker
uses `J_3` as the smallest cubic extremal control.

## 7. Combined two-sided rational-nullity router

Let

```text
k = nullity_Q(A),
delta = 2n-3k.
```

The parent theorem and RBO-3 yield two independent exact routes:

```text
Route LOW-k:
    2^k poly(n,L)

Route HIGH-k / LOW-delta:
    2^delta poly(n,L)
```

Hence a deterministic implementation may use

\[
\boxed{
T(A)
=
2^{\min(k,\,2n-3k)}\operatorname{poly}(n,L).
}
\]

In particular both are polynomial islands:

```text
k = O(log n)
```

and

```text
delta = 2n-3k = O(log n).
```

Equivalently, the second island contains nullities within `O(log n)` of the
maximum `2n/3`.

## 8. Exact residual band after both routers

Any cubic Exact-One family that remains outside both polynomial islands must
satisfy simultaneously

```text
k = omega(log n)
```

and

```text
2n-3k = omega(log n).
```

Thus the next representation/global-progress theorem does not need to cover
the low-nullity end or the near-maximal-nullity end.

Freeze the surviving gate as

```text
R5_E9_MID_NULLITY_DUAL_PARAMETER_GLOBAL_QUOTIENT_GATE_V1
```

with parameter regime

\[
\boxed{
\nu_{\mathbb Q}(A)=\omega(\log n),
\qquad
2n-3\nu_{\mathbb Q}(A)=\omega(\log n).
}
\]

A future universal route still needs a deterministic polynomial theorem for
this middle band or another representation that bypasses it.

## 9. Relation to existing SAT/X3C algorithms

This theorem does not claim that Exact Cover by 3-Sets is generally tractable.
X3C is a standard NP-complete problem, and general exact-cover procedures such
as Algorithm X/Dancing Links remain exponential in worst-case families.

The present parameter `delta` is source-specific: it is extracted from an
**actual-row rational basis of a square cubic incidence matrix**, and the proof
uses both row weight three and column support coverage plus the constant-row-sum
affine-span identity.

A literature/branch anti-duplication pass performed before materialization did
not locate this exact `delta=3r-n=2n-3k` router formulation.  This is not a
novelty claim; it records only the scope of the search performed for JANUS.

## 10. Finite replay

The executable checker uses exact `fractions.Fraction` arithmetic and retains
actual basis row indices.  It validates:

```text
delta = 3r-n = 2n-3k,
every column covered by the row basis,
sum_j(m_j-1)=delta,
|H|<=delta,
constructed witness => Ax=1.
```

Frozen controls:

- `FANO7`;
- satisfiable `AFFINE_3X3`;
- connected linear cubic `UNSAT9`;
- `J3_MAX_NULLITY`, where `k=2n/3` and `delta=0`.

Brute-force comparison is confined to these tiny controls and is explicitly
`OFFLINE_FALSIFIER_ONLY`.

## 11. Ceiling

```text
RATIONAL NULLITY UPPER BOUND
k <= 2n/3
= PROVED

OVERLAP EXCESS
delta = 3r-n = 2n-3k
= PROVED

EXACT ROUTER
2^delta poly(n,L)
= PROVED

MAXIMAL NULLITY
k=2n/3 => SAT + POLY WITNESS
= PROVED

COMBINED ROUTER
2^min(k,2n-3k) poly(n,L)
= PROVED

MIDDLE NULLITY BAND
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
