# JANUS TRUMP R48U — Constant Width Implies Root-Polynomial Pressure

Date: 2026-09-04

Status: **SYMBOLIC BRIDGE THEOREM; UNIVERSAL WIDTH COVERAGE REMAINS OPEN**

## Statement

Let `F_0` be a valid root formula with at most `V_0` variables. Fix one root-independent constant `W`.

Assume `F` and a certified nonterminal successor `G` are canonical, tautology-free persisted states such that:

1. `vars(F), vars(G) subseteq vars(F_0)`;
2. `max_width(F) <= W`;
3. `max_width(G) <= W`;
4. `DeltaV = V(F)-V(G) >= 1`.

Then the weighted-pressure requirement of the step is bounded by a polynomial depending only on the root:

\[
 a_{req}(F\to G)
 =\left\lceil\frac{\max(0,C(G)-C(F))}{\Delta V}\right\rceil
 \le U_W(V_0),
\]

where

\[
U_W(V_0)=\sum_{k=0}^{W}2^k\binom{V_0}{k}.
\]

For constant `W`, `U_W(V_0)=O(V_0^W)=N_0^{O(1)}`.

## Proof

A canonical tautology-free clause of exact width `k` is determined by:

- choosing `k` variables from the root variable universe;
- choosing one of two signs for each selected variable.

Therefore the total number of distinct canonical clauses of width at most `W` over the root variables is at most

\[
U_W(V_0)=\sum_{k=0}^{W}2^k\binom{V_0}{k}.
\]

Hence

\[
C(G)\le U_W(V_0).
\]

Since clause count is nonnegative,

\[
\max(0,C(G)-C(F))\le C(G)\le U_W(V_0).
\]

And because `DeltaV>=1`,

\[
 a_{req}(F\to G)
 \le \left\lceil\frac{U_W(V_0)}{1}\right\rceil
 =U_W(V_0).
\]

This bound is explicitly root-controlled and therefore avoids the R48J circularity barrier.

## Corollary 1 — width coverage subsumes the weighted-pressure envelope

Suppose the R48N premise holds for a fixed constant `W`: every reachable persisted nonterminal state has a certified terminal or a variable-decreasing no-fresh-variable successor whose persisted width remains at most `W`.

Then every selected nonterminal transition automatically satisfies

\[
\Delta C\le U_W(V_0)\Delta V.
\]

Thus the R48B potential

\[
\Phi(F)=C(F)+U_W(V_0)V(F)
\]

is nonincreasing on selected nonterminal transitions.

So constant-width coverage is not merely a separate route to polynomial representation; it also supplies a valid **root-polynomial pressure coefficient** for free.

## Corollary 2 — explicit W=4 bound

For `W=4`,

\[
U_4(V_0)=
1+2V_0+4\binom{V_0}{2}+8\binom{V_0}{3}+16\binom{V_0}{4}
=O(V_0^4).
\]

For the sealed R48O root with `V_0=22`,

\[
U_4(22)=130329.
\]

This number is deliberately crude; the actual observed formulas are vastly smaller. Its role is theorem-safety: it is an explicit root-polynomial ceiling independent of current representation growth.

## Important asymmetry

The converse does not follow.

A root-polynomial pressure bound can allow clauses of growing width while still controlling total clause count. Therefore

\[
\boxed{CONSTANT\ WIDTH\ COVERAGE\Rightarrow ROOT\text{-}POLYNOMIAL\ PRESSURE}
\]

but not necessarily

\[
ROOT\text{-}POLYNOMIAL\ PRESSURE\Rightarrow CONSTANT\ WIDTH\ COVERAGE.
\]

## Consequence for the current attack

If R48Q/R48S or a future theorem establishes universal constant-width persisted coverage, the weighted-pressure bootstrap problem is already solved as a corollary.

Conversely, finding states with larger `a_*` does not threaten polynomiality while a universal constant-width cap still holds: the coefficient may grow within the root-polynomial universe bound.

Therefore the fronts should now be prioritized as:

1. falsify or prove constant persisted width coverage;
2. only if constant width fails, return to the more general root-polynomial pressure/compression route.

## Canonical law

\[
\boxed{WIDTH\ CAP\ IS\ A\ ROOT\text{-}POLYNOMIAL\ PRESSURE\ CERTIFICATE.}
\]

## Firewalls

- `UNIVERSAL_WIDTH_4_COVERAGE = NOT_PROVED`.
- `UNIVERSAL_CONSTANT_WIDTH_COVERAGE = NOT_PROVED`.
- `UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
