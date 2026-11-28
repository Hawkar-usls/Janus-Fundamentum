# R5 Parity — Superincreasing deterministic isolation and valuation terminal

Date: 2026-10-10

Status: PROVED LOCAL THEOREM / UNIVERSAL SOLVER STILL OPEN

P_VS_NP = OPEN.

## Theorem: deterministic isolation with polynomial bit-length weights

Index the n target variables/hyperedges by i=0,...,n-1 and assign

    W_i = 2^i.

For two distinct Boolean assignments x != y,

    sum_i W_i x_i != sum_i W_i y_i,

because binary expansion is unique.

Therefore every nonempty feasible Exact-One solution family has a unique
minimum-weight solution and a unique maximum-weight solution under W.

The largest weight has n bits and the complete weight vector has O(n^2) input
bits. Thus deterministic isolation itself is trivial if exponentially large
numeric values but polynomial encoding length are allowed.

## Why this does not yet give the universal solver

The current parity-isolation terminal used polynomially bounded numeric weights
so that all possible total weights T could be enumerated in polynomial time and
an exact-weight parity routine queried for each T.

With W_i=2^i, the possible total-weight range is exponential. Exact-weight
parity at a supplied T is therefore insufficient by itself: scanning all T is
not polynomial, and parity over a prefix/range can cancel.

Hence the genuine obstruction is more precise than "deterministic isolation":

1. construct a polynomial-value isolating family; OR
2. compute the valuation (lowest nonzero exponent) of the parity generating
   polynomial directly in time polynomial in n and the binary weight length.

Define over F_2

    Z_F(z) = sum_{x in Sol(F)} z^(sum_i W_i x_i).

Under W_i=2^i, every feasible assignment has a distinct exponent. Therefore
every nonzero coefficient of Z_F is exactly 1, and

    F SAT  iff  Z_F(z) != 0.

Moreover, if F is SAT, the lowest nonzero exponent is exactly the weight of the
unique minimum solution.

## New deterministic terminal

A polynomial-time procedure

    LowestParityExponent(F, W)

that, for binary-encoded W, returns NONE when Z_F=0 and otherwise the least
exponent with odd coefficient, would give a deterministic polynomial-time
SolveLinearCubicXSAT by using W_i=2^i and then reading the unique minimum
assignment from the binary expansion of the returned exponent.

This terminal needs only polynomial bit complexity: the returned exponent has
O(n) bits.

## Claim boundary

DETERMINISTIC_ISOLATION_WITH_POLY_BIT_WEIGHTS = PROVED.
POLYNOMIAL_VALUE_ISOLATING_FAMILY = OPEN.
LOWEST_PARITY_EXPONENT_ALGORITHM = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
