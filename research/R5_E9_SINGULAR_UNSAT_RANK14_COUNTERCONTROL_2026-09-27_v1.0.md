# R5 E9 — Singular UNSAT Rank-14 Countercontrol

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_COUNTERCONTROL__SINGULARITY_NOT_SUFFICIENT_FOR_EXACT_ONE`

Scientific ceiling:

```text
FULL RANK => UNSAT remains valid.
SINGULAR => SAT is FALSE.
NO UNIVERSAL POLYNOMIAL DECIDER IS CLAIMED.
P_VS_NP = OPEN.
```

## 1. Purpose

The Hoffman / rational-kernel normal form proves that every Exact-One witness
`x` gives

```text
w = 3x-1 in {-1,2}^n,
A w = 0 over Q.
```

Hence full rational rank is a polynomial UNSAT certificate.  A tempting
converse would be

```text
A singular over Q => Exact-One SAT.
```

This note falsifies that converse inside the exact connected linear cubic
carrier.

## 2. Explicit normalized carrier

Take `n=15` and

```text
p = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4].
```

Let

```text
A = I + P + Q
```

where `P,Q` are the corresponding permutation matrices.

The row triples are therefore

```text
{0,5,12}
{1,7,9}
{2,9,14}
{3,10,11}
{3,4,13}
{1,5,10}
{6,7,14}
{2,3,7}
{1,4,8}
{0,6,9}
{2,10,12}
{5,11,13}
{6,8,12}
{0,8,13}
{4,11,14}
```

Every row has size three. Since `I,P,Q` are permutations, every column has
size three. Direct pair-intersection checking shows that two distinct rows
share at most one variable, so the carrier is linear. The Levi graph is
connected.

## 3. Exact rational kernel

Exact Gaussian elimination gives

```text
rank_Q(A)=14,
nullity_Q(A)=1.
```

A primitive generator of the one-dimensional kernel is

```text
g =
(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

Direct multiplication gives

```text
A g = 0.
```

Thus this is genuinely singular, not a numerical-rank artifact.

## 4. Exact UNSAT proof

Assume an Exact-One Boolean witness `x` exists. The already-proved rational
kernel-word identity gives

```text
w = 3x-1 in {-1,2}^15
```

and

```text
A w = 0.
```

Because `ker_Q(A)=span_Q{g}`, there is a scalar `lambda in Q` with

```text
w=lambda g.
```

But `g` has coordinates with values `1`, `4`, and `-2`.

If `lambda g` were contained in `{-1,2}^15`, then from a coordinate where
`g=1` we would have `lambda in {-1,2}`. For either choice, a coordinate where
`g=4` would equal `-4` or `8`, neither of which belongs to `{-1,2}`.

Contradiction. Therefore no Exact-One witness exists:

```text
A is singular over Q
AND
A is Boolean Exact-One UNSAT.
```

No exhaustive SAT search is used in the theorem proof.

## 5. Consequence

The exact one-sided terminal

```text
rank_Q(A)=n => UNSAT
```

cannot be promoted to the determinant dichotomy

```text
rank_Q(A)<n => SAT.
```

Equivalently, the mere existence of the `-3` eigenspace / nonzero rational
kernel does not imply that it contains the required `{-1,2}`-valued vector.

Freeze the anti-loop rule:

```text
DO NOT REOPEN
SINGULARITY_IFF_SAT
OR
LAMBDA_MIN_MINUS3_IFF_HOFFMAN_TIGHTNESS.
```

The remaining algorithmic content is exactly the discrete slice inside the
kernel / equivalent affine-cycle constraint, not kernel existence.

## 6. Checker

Executable regression:

`experiments/r5_e9_singular_unsat_rank14_countercontrol.py`

It verifies exactly:

- P,Q are permutations;
- cubic row/column degrees;
- pairwise linearity;
- Levi connectedness;
- exact rational rank 14 using fraction-free Gaussian elimination;
- `A g=0`;
- the kernel is one-dimensional;
- the kernel generator cannot scale to a `{-1,2}` vector;
- an independent finite Boolean replay finds zero witnesses (control only).

## 7. Ceiling

```text
FULL_RANK_UNSAT_TERMINAL = VALID
SINGULARITY_SUFFICIENT_FOR_SAT = FALSIFIED
EXPLICIT SINGULAR LINEAR-CUBIC UNSAT = PASS
UNIVERSAL_POLYNOMIAL_DECIDER = NOT YET PROVED
P_VS_NP = OPEN
```
