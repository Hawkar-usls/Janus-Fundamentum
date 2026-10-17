# R5 E9 — Cubic-Linear Spectral Rational-Nullity Bounds

Date: 2026-09-27

Status:
`JANUS_DERIVED_SPECTRAL_ROUTER_THEOREM_CANDIDATE__SOURCE_BOUND_PRIOR_ART__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_cubic_linear_girth10_spectral_nullity_bound.py`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_POLYSIZE_2GROUP_FIXED_GIRTH_COVER_THEOREM_2026-09-26_v1.0.md`
- `research/R5_E9_PRESCRIBED_C10_POLYSIZE_2GROUP_COVER_THEOREM_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS A RANK/NULLITY BOUND AND AN EXPONENTIAL-BASE IMPROVEMENT.
IT IS NOT A POLYNOMIAL SAT ALGORITHM.
NO NOVELTY OR PRIORITY CLAIM IS MADE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

be the edge/vertex incidence matrix of a connected cubic 3-uniform linear
hypergraph: every row and every column has exactly three ones, and two distinct
rows meet in at most one column.

Write

```text
k = nullity_Q(A),
r = rank_Q(A) = n-k.
```

The associated Tanner graph has adjacency matrix

\[
C=\begin{pmatrix}0&A\\A^T&0\end{pmatrix}.
\]

It is connected, bipartite and 3-regular.  Moreover

```text
nullity_Q(C)=2k.
```

The parent rational-kernel router solves cubic Exact-One exactly in
`2^k poly(n,L)` bit operations.  The purpose of this note is to bound `k` from
pure incidence geometry.

## 2. General connected cubic-linear bound

Put

\[
M=AA^T.
\]

Because every row has weight three,

\[
\operatorname{tr} M=3n.
\]

Linearity implies that every off-diagonal entry of `M` is either zero or one.
Fix a row of `A`.  Its three incident columns each occur in two additional
rows.  Linearity makes these six additional rows distinct.  Hence every row of
`M` has diagonal entry `3` and exactly six off-diagonal entries equal to `1`.
Therefore

\[
\operatorname{tr}M^2=15n.
\]

Also `A 1=3 1` and `A^T 1=3 1`, so

\[
M1=9 1.
\]

Since the Tanner graph is connected, the row-intersection graph is connected;
`M` is irreducible and Perron-Frobenius makes the eigenvalue `9` simple.

Let the positive eigenvalues of `M` be

\[
9=\lambda_1,\lambda_2,\ldots,\lambda_r>0.
\]

Then

\[
\sum_{i=2}^r\lambda_i=3n-9,
\qquad
\sum_{i=2}^r\lambda_i^2=15n-81.
\]

Cauchy-Schwarz gives

\[
(3n-9)^2\le (r-1)(15n-81).
\]

Substituting `r=n-k` and simplifying yields

\[
\boxed{
 k(5n-27)\le 2n(n-7)
}
\]

and hence, for the nontrivial connected regime,

\[
\boxed{
\nu_{\mathbb Q}(A)
\le
\frac{2n(n-7)}{5n-27}
=\left(\frac25+o(1)\right)n.
}
\]

This strictly improves the generic cubic square bound `k<=2n/3` used by the
row-basis overlap-excess router.

## 3. Girth at least ten: exact local tree moments

Assume now that the Tanner graph has girth at least ten.

Every closed walk of length at most eight is then supported on a tree: any
non-tree contribution would contain a cycle of length at most eight.  Thus the
per-vertex closed-walk counts agree with the infinite 3-regular tree through
length eight:

\[
m_0=1,
\quad m_2=3,
\quad m_4=15,
\quad m_6=87,
\quad m_8=543.
\]

Equivalently,

\[
\frac1{2n}\operatorname{tr}C^{2j}=m_{2j},
\qquad 0\le j\le4.
\]

The checker derives these moments by an exact distance-state walk recurrence;
they are not inserted as floating-point data.

## 4. A degree-four spectral certificate

Define

\[
q(t)=1-\frac9{16}t^2+\frac1{16}t^4.
\]

Squaring,

\[
q(t)^2
=1-\frac98t^2+\frac{113}{256}t^4
 -\frac9{128}t^6+\frac1{256}t^8.
\]

Using the exact tree moments,

\[
\begin{aligned}
\frac1{2n}\operatorname{tr}q(C)^2
&=1-\frac98(3)+\frac{113}{256}(15)
  -\frac9{128}(87)+\frac1{256}(543)\\
&=\frac14.
\end{aligned}
\]

Therefore

\[
\boxed{\operatorname{tr}q(C)^2=\frac n2.}
\]

## 5. Girth-ten rational-nullity theorem

Every zero eigenvalue of `C` contributes

\[
q(0)^2=1
\]

to `tr q(C)^2`.  There are exactly `2k` zero eigenvalues.

Because `C` is connected and 3-regular, `+3` is a simple eigenvalue.  Because
`C` is bipartite, `-3` is also simple.  The chosen polynomial satisfies

\[
q(3)=q(-3)=1.
\]

All remaining terms in `tr q(C)^2` are nonnegative.  Consequently

\[
2k+2\le\frac n2.
\]

Thus:

### Theorem CLG10-SN-1

For every connected square cubic incidence matrix whose Tanner graph has girth
at least ten,

\[
\boxed{
\nu_{\mathbb Q}(A)\le \frac n4-1.
}
\]

For integer nullity this means

```text
k <= floor(n/4 - 1).
```

No satisfiability assumption is used.

## 6. Exact-algorithm corollary

The existing rational-kernel router gives an exact solver with running time

\[
2^k\operatorname{poly}(n,L).
\]

Combining it with CLG10-SN-1 gives, on the connected cubic girth-at-least-ten
carrier,

\[
\boxed{
T(A)\le 2^{\lfloor n/4-1\rfloor}\operatorname{poly}(n,L).
}
\]

This is a genuine arbitrary-size reduction of the worst-case enumeration
exponent on this carrier.  It remains exponential and therefore does not cross
E8-D1.

## 7. Relation to the prescribed-C10 family

The prescribed-C10 cover program intentionally produces cubic incidence
carriers of girth exactly ten while retaining one designated 10-cycle.
Whenever its other hypotheses are met and the resulting connected component is
used, CLG10-SN-1 applies immediately.

Thus the high-girth construction no longer carries an unconstrained rational
nullity: its rational kernel dimension is at most one quarter of the square
incidence dimension, up to the endpoint correction above.

This does not by itself solve the signed-kernel or signed-trade discovery gate.
It only reduces the dimension available to those search spaces.

## 8. Prior-art and anti-loop boundary

This note makes no claim that incidence-matrix rank or regular-tree spectral
moments are new.

Source-bound donors checked before materialization include:

- A. Bjoerner and J. Karlander, *The mod p Rank of Incidence Matrices for
  Connected Uniform Hypergraphs*, European Journal of Combinatorics 14 (1993),
  151-155, DOI `10.1006/eujc.1993.1021`.  That paper gives a general rank formula
  in characteristic `p`, including characteristic zero, for connected uniform
  hypergraphs.
- Kesten-McKay regular-tree spectral theory; standard references identify its
  moments with closed-walk counts in the infinite regular tree.
- C. Cooper and A. Frieze, *Rank of the Vertex-Edge Incidence Matrix of r-Out
  Hypergraphs*, SIAM J. Discrete Math. 36 (2022), 2238-2257, DOI
  `10.1137/21M1467572`, for a random sparse-incidence rank comparison.
- S. Parui, *On the Incidence matrices of hypergraphs*, arXiv:2409.16055, for
  modern incidence-rank/null-space context.

The exact JANUS value of this note is the explicit specialization

```text
cubic + linear + connected
    -> trace/Cauchy nullity bound
cubic + connected + Tanner girth >= 10
    -> q(C) certificate
    -> k <= n/4 - 1
    -> direct binding to the existing exact 2^k router.
```

A checked-source search did not locate this exact packaged inequality/router
statement.  That observation is not a novelty or priority claim; the 1993 rank
formula may subsume the rank information at a more general level.

## 9. Next gate

The result sharpens but does not remove the exponential frontier.

The active constructive problem remains:

```text
R5_E9_SIGNED_TRADE_POLY_DISCOVERY_OR_MIXED_CARRIER_CLOSURE_GATE_V1
```

with the additional spectral constraint that on the prescribed high-girth
carrier the rational kernel has dimension at most `n/4-1`.

A second mathematical direction is now well-defined: optimize polynomial
certificates `p(C)` using higher regular-tree moments.  For girth exceeding the
corresponding walk length, such certificates may further reduce the admissible
zero-eigenvalue mass.  No asymptotic hierarchy is promoted until an arbitrary
order formula is proved.

## 10. Ceiling

```text
CONNECTED CUBIC-LINEAR GENERAL NULLITY
k <= 2n(n-7)/(5n-27)
= PROVED IN THIS NOTE

CONNECTED CUBIC TANNER GIRTH >= 10
k <= n/4 - 1
= PROVED IN THIS NOTE

GIRTH10 EXACT ROUTER
2^(n/4-1) poly(n,L)
= DERIVED FROM EXISTING 2^k ROUTER

POLYNOMIAL TRADE DISCOVERY
= OPEN

MIXED-CARRIER GLOBAL CLOSURE
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
