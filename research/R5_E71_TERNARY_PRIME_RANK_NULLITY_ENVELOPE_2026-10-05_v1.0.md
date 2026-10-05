# R5 E71 — Ternary / Fixed-Prime Rank-Nullity Exact Envelope

Date: 2026-10-05

Status:
`EXACT_BOOLEAN_SUBSET_SUM_OVER_Fp_FOR_p_GE_3__p_TO_MIN_RANK_NULLITY_ENVELOPE__TERNARY_CONSISTENCY_GATE__COMBINES_WITH_E70__NOT_UNIVERSAL`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.
P_VS_NP REMAINS OPEN.
```

E71 adds a field-dependent exact envelope to E70.  For every fixed prime
`p>=3`, with

```text
r_p = rank_Fp(A),
d_p = n-r_p,
```

Exact-One is decidable in

```text
p^min(r_p,d_p) poly(n),
```

after the ordinary affine-consistency check.  The important new project-level
lesson is that rank/nullity must be treated as a **multi-field profile** rather
than one binary scalar.

## 1. Anti-loop: E60 already contained the ternary representation

E60 already proved the exact `F3` representation.  For Boolean `x`, put

```text
r = 1+x in F3^n.
```

Since every cubic row has sum three,

```text
A 1 = 0 over F3,
```

so

```text
A r = A x.
```

Also `r_i in F3*={1,2}` iff `x_i in {0,1}`.  Therefore E60's

```text
exists r in (F3*)^n : A r = 1
```

is exactly the direct Boolean equation

```text
exists x in {0,1}^n : A x = 1 over F3.
```

E71 does **not** claim discovery of that equivalence.  The new content is the
rank/nullity algorithmic envelope and its comparison across fields.

## 2. External literature anti-loop

Lohrey, Rosowski and Zetzsche explicitly reduce Exact 3-Hitting Set / positive
1-in-3-SAT to Boolean subset sum in `Z_3^d`: incidence vectors `X_i` are given
Boolean coefficients `y_i` and target `(1,...,1)`.

Reference:

* Markus Lohrey, Andreas Rosowski, Georg Zetzsche,
  "Membership problems in finite groups",
  Journal of Algebra 675 (2025), 23-58,
  DOI `10.1016/j.jalgebra.2025.03.011`;
  earlier version arXiv `2206.11756` / MFCS 2022.

Thus the ternary encoding is externally confirmed and is **not** by itself a
polynomialization: the dimension grows in the hardness reduction.

## 3. Exact fixed-prime equivalence

For one cubic row and Boolean `x`, the integer selected count is

```text
s in {0,1,2,3}.
```

For every prime `p>=3`,

```text
s == 1 mod p  iff  s=1 as an integer.
```

For `p=3` the residues are `0,1,2,0`; for `p>3` the four possible integer
counts are already distinct modulo `p`.

Hence

```text
boxed:
Exact-One
iff
exists x in {0,1}^n with A x = 1 over F_p
```

for every fixed prime `p>=3`.

The binary field is different: row counts `1` and `3` both equal one modulo two,
which is why E70 needed the minimum-weight parity layer.

## 4. Ternary consistency lemma for square-cubic carriers

A square-cubic carrier has both row and column sums equal to three.  Therefore
over `F3`,

```text
A 1 = 0,
1^T A = 0.
```

If

```text
A x = 1 over F3
```

is consistent, left multiplication by `1^T` gives

```text
0 = 1^T A x = 1^T 1 = n mod 3.
```

Thus

```text
boxed:
F3 consistency of A x=1 => 3 divides n.
```

This is the field-linear form of the obvious Exact-One size divisibility, but it
is algorithmically useful because an inconsistent instance is rejected before
any `3^d` affine enumeration.

The first E71 gate caught exactly this issue: E69 torus `m=7` has

```text
n=49,
r_3=48,
d_3=1,
```

but `A x=1 over F3` is inconsistent since `49 != 0 mod 3`.  The theorem was not
wrong; the first checker incorrectly discarded rank/nullity metadata when the
affine system was inconsistent.  The corrected checker freezes this case.

## 5. Rank-side exact algorithm

Row-reduce the augmented system

```text
[A | 1]
```

over `F_p`.  If it is inconsistent, reject.  Otherwise keep `r_p` independent
reduced equations.  Every original column becomes a signature

```text
s_j in F_p^{r_p},
```

and the reduced right-hand side is a target `b in F_p^{r_p}`.

A Boolean vector is a subset of columns, so the problem is exactly

```text
sum_{j:x_j=1} s_j = b.
```

Standard finite-state subset-sum DP over `F_p^{r_p}` has

```text
O(n p^{r_p} poly(r_p))
```

time and `O(p^{r_p})` states.

## 6. Nullity-side exact algorithm

If the system is consistent, Gaussian elimination returns one solution `x0` and
a kernel basis

```text
K_p = ker_Fp(A),
d_p = dim K_p.
```

Every field solution is

```text
x0 + sum_i c_i k_i,
c_i in F_p.
```

There are exactly `p^{d_p}` field solutions.  Enumerate them and accept iff one
is Boolean.  By Section 3, any Boolean field solution is exactly an integer
Exact-One solution.

Thus

```text
boxed:
T_p(A) = p^min(r_p,d_p) poly(n)
```

for every fixed prime `p>=3`.

For a simple square-cubic-linear carrier, distinct nonzero columns remain
distinct and nonzero on a row-space basis, so

```text
n <= p^{r_p}-1,
r_p >= ceil(log_p(n+1)).
```

## 7. Combine E70 and E71

E70 gives

```text
2^min(r_2,d_2) poly(n),
```

while E71 gives in particular

```text
3^min(r_3,d_3) poly(n).
```

Therefore every instance can use the cheaper exact route:

```text
boxed:
T(A) <= poly(n) * min(
    2^min(r_2,d_2),
    3^min(r_3,d_3)
).
```

More fixed primes can be added one at a time.  E71 does not assume that
searching all primes or factoring arbitrary Smith invariants is polynomial.

## 8. Frozen cross-field controls

### E69 torus

E69 proved for `m=2^r-1`, `n=m^2`:

```text
d_2 = m-1 = Theta(sqrt(n)).
```

E71 freezes:

```text
m=3  : r_3=6,   d_3=3, consistent, SAT;
m=7  : r_3=48,  d_3=1, inconsistent, UNSAT;
m=15 : r_3=222, d_3=3, consistent, SAT.
```

Exploratory rank replay also gives `d_3=1` for `m=31`; no general closed formula
for the full torus family's ternary nullity is claimed here.

### E64 connected controls

```text
GQ(2,2), q=15 : d_Q=5,  d_2=5,  d_3=5;
GH(2,2), q=63 : d_Q=14, d_2=14, d_3=14.
```

So ternary nullity is not universally small.

### E12 / RXC3 hardness bridge

Frozen `q=6` source:

```text
r_2=6, d_2=0;
r_3=5, d_3=1.
```

Its `102 x 102` E12 target:

```text
r_2=90, d_2=12;
r_3=82, d_3=20.
```

Thus the hardness bridge does not collapse to tiny ternary nullity; here the
ternary nullity is actually larger than the binary nullity.

This agrees with the external `Z_3^d` hardness picture: field change alone does
not remove the hard core.

## 9. Replay checker

Companion checker:

```text
experiments/r5_e71_ternary_prime_rank_nullity_envelope.py
```

It verifies:

```text
* exact F3 rank-side subset-sum DP;
* exact F3 nullity-side affine enumeration;
* direct integer Exact-One brute force on small controls;
* p=5 fixed-prime sanity controls;
* the F3 square-cubic consistency gate;
* E69 field-profile controls;
* E64 ternary-rank/nullity stress controls;
* E12 target ternary-rank/nullity stress control;
* simple-column bound n <= 3^r-1.
```

## 10. Frontier after E71

A candidate universal hard core must now survive at least both middle-band tests

```text
min(r_2,d_2) = omega(log n),
min(r_3,d_3) = omega(log n),
```

while still surviving the E12/RXC3 hardness bridge and E64/E65 transpose
controls.

That is strictly narrower than the binary-only frontier after E70.

The next structural attack should therefore be on the **simultaneous field-rank
profile**, naturally via integer/Smith-type dependency structure, not another
separator-only hypothesis.

Scientific status:

```text
P_VS_NP = OPEN.
```
