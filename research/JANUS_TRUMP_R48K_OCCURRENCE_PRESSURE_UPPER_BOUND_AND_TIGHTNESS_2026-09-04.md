# JANUS TRUMP R48K — Occurrence-Pressure Upper Bound and Tightness

Date: 2026-09-04

Status: **SYMBOLIC LOCAL BOUND + EXPLICIT RAW-TIGHT FAMILY; FULL NORMALIZED O4 REMAINS OPEN**

## Local raw exact-DP upper bound

For a pivot variable `v`, let

- `p_v` be the number of positive parent clauses,
- `n_v` be the number of negative parent clauses,
- `d_v=p_v+n_v` be its total occurrence degree.

Exact Davis–Putnam removes `d_v` parent clauses and considers at most `p_v n_v` positive-negative parent pairs. Before subsumption, each pair contributes at most one distinct non-tautological resolvent.

Therefore

\[
\Delta C_{raw}(v)\le p_vn_v-p_v-n_v.
\]

For fixed `d_v`, the product is maximized when the two polarities are as balanced as possible:

\[
p_vn_v\le \left\lfloor\frac{d_v^2}{4}\right\rfloor.
\]

Hence

\[
\boxed{\Delta C_{raw}(v)\le \left\lfloor\frac{d_v^2}{4}\right\rfloor-d_v.}
\]

Canonicalization, subsumption, and the frozen normalization stack can only improve clause count relative to this raw pair-count ceiling; this is therefore a valid local worst-case ceiling, not a lower bound on the normalized successor.

## Minimum-degree corollary

Let `L(F)` be literal mass and `V(F)` the number of variables. Since

\[
\sum_v d_v=L(F),
\]

some variable satisfies

\[
d_v\le \left\lfloor\frac{L(F)}{V(F)}\right\rfloor.
\]

Thus raw exact-DP always has some pivot whose pre-subsumption clause pressure is bounded by the quadratic function of the current average occurrence degree.

This remains a **current-state** bound and therefore does not solve the R48J root-bootstrap problem.

## Tightness on the R48I clean cyclic bipolar family

R48I constructs a cyclic family with `p_v=n_v=r` for every pivot and pairwise-disjoint cross-polarity difference geometry.

For every pivot:

- `d_v=2r`;
- all `r^2` parent pairs survive as distinct non-tautological raw resolvents;
- no raw resolvent duplicates an unaffected base clause;
- exact raw clause pressure is

\[
\Delta C_{raw}=r^2-2r.
\]

But

\[
\frac{d_v^2}{4}-d_v
=\frac{(2r)^2}{4}-2r
=r^2-2r.
\]

Therefore the generic occurrence-degree upper bound is attained with equality:

\[
\boxed{\Delta C_{raw}=\frac{d_v^2}{4}-d_v.}
\]

Moreover all pivots have the same balanced occurrence degree, so a strategy that relies only on selecting a lower-degree or more polarity-unbalanced pivot has no escape on this raw family.

## Consequence for the O4 attack

The universal wall cannot be broken by merely sharpening the algebra

`p*n <= d^2/4`

or by saying “choose the minimum-degree pivot” without an additional root-controlled density theorem.

Any universal improvement over this tight raw family must exploit at least one genuinely stronger mechanism:

1. guaranteed subsumption repayment;
2. R33/RUP/SA-BVE normalization repayment;
3. a global structural invariant that bounds the minimum reachable occurrence density in root parameters;
4. a compact representation that avoids materializing the complete bipartite resolvent product;
5. a different root-controlled potential.

R48I's executable finite ladder measures mechanism (1)/(2). R48J proves that a bound merely polynomial in the current density/size is not enough unless its root bootstrap closes.

## What this does NOT prove

- It does not prove normalized pressure grows like `r^2`.
- It does not prove pressure is unbounded along reachable TRUMP trajectories.
- It does not refute a root-polynomial pressure bound.
- It does not prove any SAT complexity separation.

## Firewalls

- `UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_a_EXISTS = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
