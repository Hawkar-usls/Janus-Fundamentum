# R5 E57 — Hoffman Endpoint / Real-Kernel Full Support Is Not Sufficient

Date: 2026-10-03

Status:
`NEGATIVE_CONTROL__LAMBDA_MIN_MINUS_3_AND_FULL_SUPPORT_REAL_KERNEL_DO_NOT_IMPLY_EXACT_ONE`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A POLYNOMIAL ALGORITHM.

IT CLOSES A TEMPTING GLOBAL SHORTCUT CREATED BY THE GRAM-HOFFMAN FORM.

FOR A LINEAR SQUARE CUBIC CARRIER A, LET

    G = A^T A - 3 I.

THEN G IS THE 6-REGULAR SIMPLE CONFLICT GRAPH AND

    lambda_min(G) >= -3.

AN EXACT-ONE SOLUTION FORCES

    lambda_min(G) = -3,

BECAUSE IF A x = 1 AND A 1 = 3 1, THEN

    A(1-3x)=0.

HOWEVER THE CONVERSE IS FALSE EVEN UNDER A STRONGER CONDITION:

THERE EXISTS A SIMPLE LINEAR n=12 CARRIER WITH

    rank_R(A)=11,
    ker_R(A) CONTAINING A FULL-SUPPORT VECTOR,
    lambda_min(G)=-3,

BUT

    alpha(G)=3 < 4=n/3,

SO EXACT-ONE IS UNSAT.

THUS SINGULARITY, THE HOFFMAN ENDPOINT, AND EVEN FULL SUPPORT OF THE REAL
KERNEL ARE ONLY NECESSARY FILTERS.  THE UNIVERSAL SOLVER MUST RECOGNIZE THE
SPECIAL TWO-LEVEL BOOLEAN KERNEL POINT, NOT MERELY A NONZERO / FULL-SUPPORT
REAL NULL VECTOR.

P_VS_NP = OPEN.
```

## 1. Gram/Hoffman setup

For a simple linear square cubic carrier `A`, every column has weight 3 and any two
columns meet in at most one row.  Therefore

```text
A^T A = 3 I + Adj(G),
```

where `G` is the conflict graph on columns.

Every column meets two other columns in each of its three rows, so `G` is 6-regular.
Since `A^T A` is positive semidefinite,

```text
boxed:
lambda_min(G) >= -3.
```

If `x` is an Exact-One solution, then

```text
A x = 1.
```

Because every row has weight 3,

```text
A 1 = 3 1.
```

Hence

```text
A(1-3x)=0.
```

The centered Boolean vector

```text
z = 1-3x
```

has coordinates in

```text
{1,-2}
```

and is nonzero.  Therefore `A` is singular, and

```text
(A^T A - 3I) z = -3 z.
```

Thus SAT implies

```text
lambda_min(G)=-3.
```

This is the spectral necessity behind the Hoffman endpoint.

## 2. Hoffman bound

For a 6-regular graph with least eigenvalue `tau`, Hoffman's ratio bound gives

```text
alpha(G) <= n * (-tau)/(6-tau).
```

Since `tau >= -3`,

```text
alpha(G) <= n/3.
```

For the carrier conflict graph, an independent set of size `n/3` is exactly an Exact-One
cover: the selected columns are pairwise row-disjoint, each covers three rows, and `n/3`
columns therefore cover all `n` rows.

Hence

```text
boxed:
Exact-One SAT
iff
alpha(G)=n/3.
```

If equality holds, Hoffman is tight and `tau=-3`.

The unresolved converse question is whether merely reaching the spectral endpoint
`tau=-3` forces a tight coclique.  E57 gives an explicit NO.

## 3. Explicit n=12 counterexample

Normalize one matching and use the permutation rows

```text
P = [6,3,7,10,11,1,4,8,9,5,2,0]
Q = [3,4,5,8,7,0,9,6,2,11,1,10].
```

The carrier is

```text
A = I + P + Q
```

in the row convention used by the companion checker.

It has

```text
n=12,
row weight=3,
column weight=3,
```

and is linear: every off-diagonal entry of `A^T A` is `0` or `1`.

An explicit integer full-support null vector is

```text
z = (-1,-1,2,-1,2,2,2,-4,2,-4,-1,2).
```

Direct replay gives

```text
A z = 0.
```

Every coordinate of `z` is nonzero.

A rank computation modulo 5 gives rank 11.  Because the explicit null vector already
shows real rank at most 11, this proves

```text
boxed:
rank_R(A)=11.
```

Thus the real kernel is one-dimensional and full-support.

## 4. Spectral endpoint is reached exactly

Set

```text
G=A^T A-3I.
```

The checker verifies that `G` is a simple 6-regular adjacency matrix.

From `A z=0`,

```text
G z=-3z.
```

Since `G+3I=A^T A` is positive semidefinite, no eigenvalue lies below `-3`.
Therefore

```text
boxed:
lambda_min(G)=-3.
```

So this instance reaches the exact Gram/Hoffman spectral endpoint.

## 5. But the Hoffman bound is not tight

Exhaustive replay on the 12-vertex conflict graph gives

```text
boxed:
alpha(G)=3.
```

Yet

```text
n/3=4.
```

Therefore

```text
alpha(G)<n/3,
```

and no Exact-One solution exists.

So we have simultaneously

```text
A singular,
ker_R(A) has a full-support vector,
lambda_min(G)=-3,
Hoffman upper bound = n/3,
```

but

```text
Exact-One = UNSAT.
```

## 6. What exactly failed

For a SAT instance, the nullspace must contain not merely a nonzero vector or a
full-support vector.  It must contain the special two-level vector

```text
z in {1,-2}^n
```

with exactly `n/3` coordinates equal to `-2`.

Equivalently,

```text
x=(1-z)/3
```

must be Boolean.

The E57 kernel generator instead uses three magnitudes:

```text
{-4,-1,2}
```

up to scaling.  It reaches the correct eigenspace but misses the Boolean two-level
slice.

Thus the hard object is now sharply separated:

```text
NOT:
  detect the -3 eigenspace.

BUT:
  decide whether the affine / projective -3 eigenspace contains the prescribed
  two-level Boolean pattern.
```

That is the same discrete extraction barrier exposed by E56 from the binary syndrome
side.

## 7. Connection to E56

E56 says Exact-One is equivalent to finding a minimum-weight representative of the
binary parity coset at the exact floor `n/3`.

E57 says the real Gram/Hoffman relaxation can also reach its exact spectral floor while
the Boolean optimum still fails.

Therefore both global relaxations isolate the same missing mechanism:

```text
continuous / linear feasibility is easy;
Boolean extremal extraction is the unresolved step.
```

A universal polynomial solver must bridge that extraction gap rather than stopping at

```text
Gaussian elimination,
real nullspace,
singularity,
or the Hoffman eigenvalue endpoint.
```

## 8. Next global target

The next attack should combine the three exact views rather than treating any one as
sufficient:

```text
BINARY:
  x+Px+Qx=1 mod 2,
  seek coset weight n/3.

REAL / SPECTRAL:
  ker_R(A) contains z=1-3x in {1,-2}^n.

TERNARY:
  A r=1 over F_3,
  seek r_i != 0 for every i.
```

A useful universal theorem would be a polynomially checkable invariant forcing these
three projections to correspond to the same Boolean point.

Until such an invariant is proved:

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e57_hoffman_endpoint_not_sufficient.py
```
