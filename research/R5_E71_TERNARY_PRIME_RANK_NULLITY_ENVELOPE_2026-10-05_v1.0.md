# R5 E71 — Ternary / Fixed-Prime Rank-Nullity Exact Envelope

Date: 2026-10-05

Status:
`EXACT_BOOLEAN_SUBSET_SUM_OVER_Fp_FOR_p_GE_3__p_TO_MIN_RANK_NULLITY_ENVELOPE__COMBINES_WITH_E70__NOT_UNIVERSAL`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

P_VS_NP REMAINS OPEN.

E71 ADDS A NEW PARAMETRIC AXIS TO THE EXISTING E70 BINARY ENVELOPE:
FOR EVERY FIXED PRIME p >= 3,

    Exact-One is exactly decidable in

        p^min(r_p,d_p) poly(n),

where

    r_p = rank_Fp(A),
    d_p = n-r_p.

THE VALUE OF THE PARAMETER CAN CHANGE STRONGLY WITH THE FIELD.
SOME E69 LARGE-BINARY-NULLITY TORUS CONTROLS COLLAPSE TO TINY TERNARY
NULLITY, WHILE E64 AND E12 CONTROLS SHOW THAT TERNARY NULLITY IS NOT
UNIVERSALLY SMALL.
```

## 1. Anti-loop: E60 already had the ternary representation

R5 E60 already recorded the exact F3 representation.  For Boolean `x`, put

```text
r = 1+x in F3^n.
```

Because every cubic row has sum three,

```text
A 1 = 0 over F3.
```

Hence

```text
A r = A(1+x) = A x over F3.
```

Moreover

```text
r_i in F3* = {1,2}
iff
x_i in {0,1}.
```

Thus E60's statement

```text
Exact-One
iff exists r in (F3*)^n with A r = 1
```

is equivalent to the direct Boolean statement

```text
Exact-One
iff exists x in {0,1}^n with A x = 1 over F3.
```

E71 does **not** claim discovery of this equivalence.  Its new project-level
content is the exact rank/nullity algorithmic envelope and the cross-field
comparison with E70.

## 2. External literature anti-loop

The ternary subset-sum encoding is explicitly present in the literature.
Lohrey, Rosowski and Zetzsche reduce Exact 3-Hitting Set / positive 1-in-3-SAT
to Boolean subset sum in the elementary abelian group `Z_3^d`: incidence
vectors `X_i` are chosen with coefficients `y_i in {0,1}` and target
`(1,...,1)`.

Reference:

* Markus Lohrey, Andreas Rosowski, Georg Zetzsche,
  "Membership problems in finite groups",
  Journal of Algebra 675 (2025), 23-58,
  DOI: `10.1016/j.jalgebra.2025.03.011`.
  Earlier version: arXiv `2206.11756` / MFCS 2022.

This is important in both directions:

```text
* it independently confirms the direct F3 Boolean-subset-sum representation;
* it prevents the false conclusion that moving to F3 by itself makes the
  problem polynomial, because dimension d is part of the input in their
  hardness reduction.
```

Finite-abelian-group subset sum is also a standard object in additive
combinatorics; E71's rank-side DP is simply the finite-state dynamic program on
the group `F_p^{r_p}`, not a claim of a new general subset-sum algorithm.

## 3. Why every fixed prime p >= 3 works

Let one cubic row contain exactly `s` selected Boolean variables.  Since the row
has size three,

```text
s in {0,1,2,3}.
```

For every prime `p >= 3`,

```text
s == 1 mod p
iff
s = 1 as an integer.
```

For `p=3` the residue table is

```text
s : 0 1 2 3
    0 1 2 0 mod 3,
```

so only `s=1` hits residue one.  For `p>3`, the four integers are already
distinct modulo `p`.

Therefore for every fixed prime `p>=3`,

```text
boxed:
integer Exact-One A x = 1, x Boolean
iff
A x = 1 over F_p, x Boolean.
```

This differs sharply from `p=2`, where both row sums `1` and `3` are congruent
to one.  That is why E70 needed the minimum-weight parity layer on the binary
side.

## 4. Rank-side algorithm over F_p

Let

```text
r_p = rank_Fp(A).
```

Row-reduce the augmented system

```text
[A | 1]
```

over `F_p`.

If a row

```text
[0 ... 0 | c], c != 0
```

appears, the system has no F_p solution and therefore Exact-One is immediately
UNSAT.

Otherwise retain the `r_p` independent reduced equations.  For each original
column `j`, let

```text
s_j in F_p^{r_p}
```

be its coefficient vector in those equations, and let

```text
b in F_p^{r_p}
```

be the reduced right-hand side.

A Boolean vector `x` is exactly a subset of the columns, and it solves the
system iff

```text
sum_{j:x_j=1} s_j = b in F_p^{r_p}.
```

Run the standard subset-sum DP over all `p^{r_p}` group states:

```text
reachable_0 = {0},
reachable_{j+1} = reachable_j union (reachable_j + s_j).
```

After all columns, accept iff `b` is reachable.

Complexity:

```text
O(n p^{r_p} poly(r_p))
```

and `O(p^{r_p})` state space.

## 5. Nullity-side algorithm over F_p

If `A x=1` is consistent, Gaussian elimination gives one affine solution `x0`
and a basis of

```text
K_p = ker_Fp(A),
d_p = dim K_p = n-r_p.
```

Every field solution is

```text
x = x0 + sum_{i=1}^{d_p} c_i k_i,
c_i in F_p.
```

There are exactly

```text
p^{d_p}
```

field solutions.  Enumerate them and accept iff one has every coordinate in

```text
{0,1}.
```

By Section 3, that Boolean field solution is exactly an integer Exact-One
solution.

Complexity:

```text
p^{d_p} poly(n).
```

## 6. Fixed-prime exact envelope

Choose the cheaper of the rank and nullity sides:

```text
boxed:
T_p(A) = p^min(r_p,d_p) poly(n)
```

for every fixed prime `p>=3`.

Hence

```text
min(r_p,d_p)=O(log n)
```

is a polynomial regime for that fixed field.

For a simple square-cubic-linear carrier, nonzero distinct columns remain
nonzero and distinct after restriction to a row-space basis.  Consequently

```text
n <= p^{r_p}-1,
```

so

```text
r_p >= ceil(log_p(n+1)).
```

As in E70, low rank is structurally near the smallest rank compatible with `n`
distinct nonzero columns.

## 7. Combine E70 and E71 instead of choosing one field globally

E70 gives the binary exact envelope

```text
2^min(r_2,d_2) poly(n),
```

where the rank side computes the minimum weight in the parity syndrome class.

E71 gives, in particular, the ternary Boolean envelope

```text
3^min(r_3,d_3) poly(n).
```

Therefore every instance can use the cheaper certified route:

```text
boxed:
T(A) <= poly(n) * min(
    2^min(r_2,d_2),
    3^min(r_3,d_3)
).
```

More generally any fixed prime `p>=3` may be added as another exact route.

This does **not** imply that scanning arbitrarily many primes is polynomial;
E71 makes only fixed-prime claims.  No integer-factorization or all-primes
optimization assumption is introduced.

## 8. E69 torus: field change can collapse the parameter

For the E69 family

```text
A_m = I + P_x + P_y,
m=2^r-1,
n=m^2,
```

E69 proved over F2

```text
d_2 = m-1 = Theta(sqrt(n)).
```

The E71 checker computes over F3:

```text
m=3  : d_3=3,
m=7  : d_3=1,
m=15 : d_3=3.
```

Additional exploratory replay also gives

```text
m=31 : d_3=1.
```

Thus the same matrices can be difficult for the binary-nullity parameter and
trivial for the ternary-nullity parameter.

This is a genuine new lesson for the universal search: **rank/nullity must be
studied as a field-dependent profile, not as one binary scalar.**

No general formula for the entire torus family's ternary nullity is claimed in
E71; only the replayed levels are frozen here.

## 9. E64 firewall: ternary nullity is not always small

The connected high-girth E64 controls give:

```text
GQ(2,2), q=15:
    d_2=5,
    d_3=5.

GH(2,2), q=63:
    d_2=14,
    d_3=14.
```

Therefore changing to F3 does not automatically collapse connected
square-cubic-linear configurations, even with strong symmetry and large girth.

The q=63 GH(2,2) orientation remains the important frozen UNSAT control.

## 10. E12 / RXC3 hardness bridge stress test

For the frozen `q=6` RXC3 source:

```text
binary rank/nullity : r_2=6, d_2=0,
ternary rank/nullity: r_3=5, d_3=1.
```

For its `102 x 102` E12 gadget target:

```text
binary rank/nullity : r_2=90, d_2=12,
ternary rank/nullity: r_3=82, d_3=20.
```

Thus the hardness bridge does **not** collapse to tiny ternary nullity on the
frozen target.  In fact this control moves in the opposite direction:

```text
d_3 > d_2.
```

This is exactly the kind of anti-overclaim control E71 needs.  A universal
argument cannot assume that F3 is always the better field.

The external X3HS-to-`Z_3^d` hardness reduction gives the same conceptual
warning: ternary Boolean subset sum remains hard when the group dimension grows.

## 11. Replay checker

Companion checker:

```text
experiments/r5_e71_ternary_prime_rank_nullity_envelope.py
```

It performs:

```text
* exact F3 rank-side subset-sum DP;
* exact F3 nullity-side affine enumeration;
* direct integer Exact-One brute force on small controls;
* p=5 sanity controls for the fixed-prime generalization;
* E69 ternary-rank/nullity checks;
* E64 ternary-rank/nullity stress checks;
* E12 target ternary-rank/nullity stress check;
* simple-column bound n <= 3^r-1.
```

Frozen expected values include:

```text
SAT12          : r3=10, d3=2, SAT;
E57 UNSAT12    : r3=10, d3=2, UNSAT;
RXC3 source q6 : r3=5,  d3=1, UNSAT;
E69 torus m3   : r3=6,  d3=3, SAT;
E69 torus m7   : r3=48, d3=1, UNSAT;
E69 torus m15  : r3=222,d3=3, SAT;
E64 GQ22       : r3=10, d3=5;
E64 GH22       : r3=49, d3=14;
E12 target q6  : r3=82, d3=20.
```

## 12. Frontier after E71

The strongest exact rank/nullity envelope now available is multi-field:

```text
binary:
    2^min(r_2,d_2) poly(n),

ternary:
    3^min(r_3,d_3) poly(n),

fixed p>=5:
    p^min(r_p,d_p) poly(n).
```

A remaining universal hard-core candidate must evade **all fixed fields that we
actually exploit**.  In particular, the next structural search should focus on
instances for which both binary and ternary profiles lie in their middle bands:

```text
min(r_2,d_2) = omega(log n),
min(r_3,d_3) = omega(log n),
```

while still surviving the E12/RXC3 quotient and the E64/E65 transpose controls.

That is a stricter target than the pre-E71 binary-only middle band.

Scientific status:

```text
P_VS_NP = OPEN.
```
