# R5 E70 — Dual Binary-Rank / Nullity Exact Envelope

Date: 2026-10-04

Status:
`EXACT_2_TO_MIN_RANK_NULLITY_ENVELOPE__SYNDROME_DP_ON_RANK_SIDE__E58_ENUMERATION_ON_NULLITY_SIDE__MIDDLE_BAND_REMAINS_OPEN`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

THE TARGET REMAINS A UNIVERSAL, PROVABLE POLYNOMIAL-TIME ALGORITHM FOR THE
SQUARE-CUBIC-LINEAR EXACT-ONE HARD CORE.  P_VS_NP REMAINS OPEN.

E70 SHRINKS THE PARAMETRIC FRONTIER:

    Exact-One is exactly decidable in

        2^min(r,d) poly(n),

    where

        r = rank_F2(A),
        d = nullity_F2(A) = n-r.

THEREFORE BOTH EXTREME EDGES OF THE BINARY-RANK SPECTRUM ARE POLYNOMIAL WHEN
min(r,d)=O(log n).  THE UNRESOLVED REGION IS THE MIDDLE BAND IN WHICH BOTH
BINARY RANK AND BINARY NULLITY ARE SUPERLOGARITHMIC.
```

## 1. Anti-loop: what was already in Fundamentum

E56 proved that for every square-cubic binary carrier and every binary parity
solution

```text
A x = 1 mod 2,
```

rows contain either one or three selected columns and

```text
3|x| = n + 2 t_3.
```

Hence, when `3|n`,

```text
boxed:
Exact-One SAT
iff min{|x| : A x = 1 mod 2} = n/3.
```

E58 rewrote the same affine syndrome class as

```text
x = 1 + k,
k in ker_F2(A),
```

and proved

```text
boxed:
Exact-One SAT
iff max{|k| : k in ker_F2(A)} = 2n/3.
```

E69 then showed that large binary nullity does not force bounded/logarithmic
Levi treewidth.

Before recording E70, repository file search and commit search were run for
`syndrome`, `dynamic programming`, `coset leader`, rank/nullity envelopes and
related phrases.  E56 was found, but no existing Fundamentum statement of the
rank-side syndrome-state DP or the combined `2^min(r,d)` envelope was found.

## 2. Open-literature anti-loop

The rank-side problem is the classical **syndrome decoding / coset leader**
problem: given a binary parity-check matrix `H` and syndrome `b`, find a
minimum-Hamming-weight vector `x` with

```text
H x = b.
```

Berlekamp, McEliece and van Tilborg proved the general syndrome-decoding problem
NP-complete:

* E. R. Berlekamp, R. J. McEliece, H. C. A. van Tilborg,
  "On the Inherent Intractability of Certain Coding Problems",
  IEEE Transactions on Information Theory 24(3), 384-386 (1978),
  DOI `10.1109/TIT.1978.1055873`.

Thus E70 does **not** claim a new general polynomial syndrome decoder.  The
`2^r` algorithm below is the elementary exact finite-state dynamic program over
all syndromes when the check rank `r` is the parameter.

The standard coding-theory interpretation also identifies minimum syndrome
weight with the coset leader of the corresponding affine code coset.  E70's
novelty within this project is the exact pairing of that rank-parameterized
algorithm with E58's nullity-side enumeration and the resulting frontier
shrinkage for the square-cubic Exact-One route.

## 3. Binary rank and nullity

Let

```text
r = rank_F2(A),
d = n-r.
```

Because every row has odd weight three,

```text
A 1 = 1 mod 2,
```

so the syndrome class `A x=1` is always nonempty.

If `3` does not divide `n`, Exact-One is immediately impossible because every
Exact-One solution would select exactly `n/3` columns.  Hence below the
interesting case is `3|n`.

## 4. Nullity-side exact algorithm

This is E58 in algorithmic form.

Enumerate every

```text
k in K = ker_F2(A).
```

There are exactly `2^d` such words.  Since

```text
x = 1+k,
```

we have

```text
|x| = n-|k|.
```

Thus the minimum parity-solution weight is

```text
n - max_{k in K}|k|.
```

The cost is

```text
2^d poly(n).
```

This decides Exact-One by testing whether the minimum is `n/3`, equivalently
whether the maximum kernel weight is `2n/3`.

## 5. Rank-side exact syndrome DP

Choose `r` linearly independent **original** rows of `A`.  Call their indices

```text
i_1,...,i_r.
```

For every column `j`, form its compressed syndrome signature

```text
s_j = (A_{i_1 j},...,A_{i_r j}) in F2^r.
```

Each selected original row has right-hand side `1`.  Therefore a subset `S` of
columns satisfies these basis equations exactly when

```text
xor_{j in S} s_j = b,

b = (1,...,1) in F2^r.
```

Why is satisfying only the independent original rows sufficient?  Every omitted
row is an F2-linear combination of the chosen rows.  If

```text
a = sum_h c_h a_{i_h},
```

then dotting with the all-ones vector gives

```text
1 = a 1 = sum_h c_h (a_{i_h} 1) = sum_h c_h,
```

because every cubic row has odd weight.  Therefore the same combination sends
the chosen right-hand sides `1` to the omitted right-hand side `1`.  The
compressed system is exactly equivalent to `A x=1`.

Now run subset DP over the `2^r` possible syndrome states:

```text
dp[0] = 0,
dp[sigma] = infinity otherwise.
```

For each column signature `s_j`, update

```text
new[sigma] = min(
    dp[sigma],
    1 + dp[sigma xor s_j]
).
```

After all columns,

```text
dp[b]
```

is the exact minimum Hamming weight among all solutions of `A x=1`.

Time:

```text
O(n 2^r)
```

up to polynomial rank-preprocessing factors, with `O(2^r)` memory.

By E56,

```text
boxed:
Exact-One SAT iff dp[b] = n/3.
```

## 6. Combined exact envelope

Choose the cheaper of the two exact algorithms:

```text
nullity side: 2^d poly(n),
rank side:    2^r poly(n).
```

Therefore

```text
boxed:
T(A) = 2^min(r,d) poly(n).
```

In particular,

```text
min(r,d)=O(log n)
```

implies polynomial time.

This sharpens the post-E69 frontier.  It is not enough to say "large nullity is
hard": if

```text
d = n-O(log n),
```

then `r=O(log n)` and the syndrome DP is polynomial.

The unresolved rank/nullity band must satisfy

```text
boxed:
r = omega(log n)
and
d = omega(log n).
```

No claim is made that every instance in this middle band is hard.

## 7. A simple rank floor from linearity

For a simple square-cubic-linear carrier, every full column is nonzero and any
two columns are distinct.

Restriction to a row basis is injective on columns.  Indeed, if two compressed
column signatures were equal, their difference would vanish on the basis rows;
since every row is a combination of the basis rows, it would vanish on every
row, so the two full columns would be identical.

Likewise no compressed column signature is zero, because that would make the
full column zero.

There are only

```text
2^r-1
```

nonzero vectors in `F2^r`.  Hence

```text
boxed:
n <= 2^r-1,
```

so

```text
boxed:
r >= ceil(log2(n+1)).
```

Thus the rank-side polynomial regime `r=O(log n)` lies near the smallest binary
rank compatible with `n` distinct nonzero columns.  This is a structural
constraint, not a universal solver.

## 8. Relation to E69

E69's torus family has

```text
d = sqrt(n)-1,
r = n-sqrt(n)+1.
```

It therefore lies outside both logarithmic edges of E70.  E70 does not explain
its tractability; E69's Fourier/group-algebra compression is genuinely
additional structure.

This is useful: it shows that the remaining universal program needs more than
rank/nullity size alone.  The exact envelope handles the spectrum edges; the
middle band still requires dependency-algebra, quotient, recurrence, or another
polynomial mechanism.

## 9. Replay controls

Companion checker:

```text
experiments/r5_e70_dual_rank_nullity_exact_envelope.py
```

It compares three independent decision routes on small frozen controls:

```text
* rank-side syndrome DP;
* nullity-side E58 kernel enumeration;
* direct Exact-One brute force.
```

Fixtures:

```text
SAT12          : binary rank 10, nullity 2, SAT;
E57 UNSAT12    : binary rank 11, nullity 1, UNSAT;
E17 RXC3 q=6   : binary rank 6,  nullity 0, UNSAT;
E69 torus m=3  : binary rank 7,  nullity 2, SAT.
```

The checker also verifies distinct/nonzero compressed column signatures and
`n <= 2^r-1` on every fixture.

## 10. Universal frontier after E70

The exact rank/nullity envelope suggests a stricter E71 target:

```text
MIDDLE-BAND THEOREM

Given a connected square-cubic-linear carrier with

    rank_F2(A)  = omega(log n),
    nullity_F2(A) = omega(log n),

prove a polynomial structural compression or construct a polynomial Exact-One
certificate/solver.
```

Any such proposal must be attacked against:

```text
* the E12/RXC3 hardness bridge after exact quotienting;
* E64/E65 transpose controls;
* E67/E68 hierarchy firewalls;
* E69 high-width algebraically-compressible torus family.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
