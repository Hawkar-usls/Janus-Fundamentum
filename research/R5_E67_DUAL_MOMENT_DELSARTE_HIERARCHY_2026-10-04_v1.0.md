# R5 E67 — Dual-Moment / Delsarte Top-Shell Hierarchy

Date: 2026-10-04

Status:
`LOW_ORDER_DUAL_MOMENTS_CAN_CERTIFY_TOP_SHELL_CEILING__T12_WORKS_ON_TUTTE12_BASE__T12_FAILS_ON_CONNECTED_GIRTH12_2LIFT`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT TESTS THE POST-E66 IDEA THAT ORIENTATION-SENSITIVE LOW-ORDER
MACWILLIAMS / DELSARTE DATA MIGHT CERTIFY THE BINARY-KERNEL TOP-SHELL
CEILING WITHOUT ENUMERATING THE FULL KERNEL.

THERE IS A GENUINE POSITIVE RESULT:

    THE FIRST 12 DUAL WEIGHT COUNTS CERTIFY THE UNSAT TUTTE-12
    ORIENTATION BY AN EXACT DEGREE-12 NONNEGATIVE ANNIHILATOR.

BUT LEVEL 12 IS NOT UNIVERSAL:

    A CONNECTED 126 x 126 SQUARE-CUBIC-LINEAR GIRTH-12 2-LIFT IS UNSAT,
    YET AN EXPLICIT RATIONAL DELSARTE-FEASIBLE PSEUDODISTRIBUTION MATCHES
    THE TRUE FIRST 12 DUAL MOMENTS AND STILL HAS POSITIVE MASS AT THE
    SAT TOP WEIGHT 84.

SO THE PROMISING OBJECT IS A HIERARCHY IN THE MOMENT ORDER t, NOT A
PROOF THAT A FIXED SMALL t SOLVES THE WHOLE HARD CORE.

P_VS_NP = OPEN.
```

## 1. Top-shell formulation carried forward from E58/E66

For a square cubic binary incidence matrix `A` of order `n`, let

```text
C(A) = ker_F2(A).
```

E58 proved

```text
|k| <= 2n/3   for every k in C(A),
```

and

```text
Exact-One SAT
iff
exists k in C(A) with |k| = 2n/3.
```

Write the binary-kernel weight enumerator as

```text
A_w = #{ k in C(A) : |k| = w }.
```

The decision question is exactly

```text
A_{2n/3} > 0 ?
```

E66 showed that simply enumerating the top shell is orientation-sensitive but
exponential in the kernel dimension.  E67 asks whether low-order dual moments
can certify the absence of the top shell polynomially.

## 2. MacWilliams / Krawtchouk coordinates

Let

```text
B_j = #{ u in C(A)^perp : |u| = j }.
```

For a binary linear code, MacWilliams gives

```text
boxed:
|C| B_j = sum_w A_w K_j(w),
```

where `K_j` is the binary Krawtchouk polynomial of degree `j`.

Therefore the first `t` dual counts

```text
B_0,...,B_t
```

fix all linear moments of the weight distribution against polynomials of degree
at most `t`.

This is algorithmically meaningful for fixed `t`: `C(A)^perp` is the rowspace
of `A`.  For each `j <= t`, one may enumerate the `binom(n,j)` candidate supports
and test rowspace membership by Gaussian elimination.  Hence all `B_j` for
fixed `j <= t` are computable in

```text
n^{O(t)}
```

time.  A fixed-order moment LP is therefore polynomial-time, although the
exponent is large.

## 3. The level-t Delsarte relaxation used here

For a known dimension `d=dim_F2 C(A)`, a level-`t` top-shell relaxation uses
variables

```text
A_w >= 0,
```

for the allowed even weights

```text
0 <= w <= 2n/3,
```

with

```text
A_0 = 1,
sum_w A_w = 2^d,
```

and exact MacWilliams constraints

```text
sum_w A_w K_j(w) = 2^d B_j,
j=1,...,t.
```

For all higher Krawtchouk coordinates it keeps the standard Delsarte
nonnegativity condition

```text
sum_w A_w K_j(w) >= 0,
j=t+1,...,n.
```

The objective is to maximize the putative top-shell mass

```text
A_{2n/3}.
```

If this LP forces the optimum to zero, UNSAT is certified.  A positive optimum
is only `INCONCLUSIVE`; it does not imply SAT.

## 4. Positive result: t=12 exactly certifies the Tutte-12 UNSAT orientation

For the E64-E66 Tutte-12 UNSAT orientation `R`, the exact kernel weight
distribution is

```text
W_R(z) =
    1
  + 126 z^16
  + 1596 z^24
  + 2880 z^28
  + 7497 z^32
  + 4032 z^36
  + 252 z^40.
```

Thus the positive weight support is exactly

```text
S = {16,24,28,32,36,40}.
```

Define

```text
P(w) = product_{s in S} (w-s)^2.
```

Then:

```text
deg P = 12,
P(w) >= 0 for all real w,
P(s) = 0 for every s in S,
P(42) = 618173337600 > 0.
```

Since `deg P=12`, it has an exact Krawtchouk expansion

```text
P(w) = sum_{j=0}^{12} c_j K_j(w).
```

Hence `sum_w A_w P(w)` is determined completely by `B_0,...,B_12`.
For the true Tutte-12 code all positive support lies at roots of `P`, so

```text
sum_w A_w P(w) = P(0)
               = 245472842848665600.
```

Now consider any nonnegative pseudo weight distribution with

```text
A_0=1
```

and the same first 12 dual moments.  It must have the same `P`-moment.  But the
weight-zero term already contributes the entire value `P(0)`.  Since every
other term is nonnegative, every positive weight with `P(w)>0` must have zero
mass.  In particular

```text
boxed:
A_42 = 0.
```

So level 12 supplies an exact polynomially-checkable UNSAT certificate for this
63 x 63 post-quotient instance, with no `2^14` search required by the
certificate itself.

The exact first dual counts replayed by the checker are

```text
B_0  = 1,
B_1  = 0,
B_2  = 0,
B_3  = 63,
B_4  = 189,
B_5  = 756,
B_6  = 6300,
B_7  = 39987,
B_8  = 238077,
B_9  = 1407532,
B_10 = 7682724,
B_11 = 37482291,
B_12 = 163210593.
```

This is the first E61-E67 route that replaces exhaustive kernel search by a
finite polynomial certificate on the frozen Tutte-12 UNSAT orientation.

## 5. Why degree 12 appears

The certificate is not mysterious.  The UNSAT kernel happens to have only six
distinct positive weights.  Squaring one linear factor per positive support
weight gives a nonnegative annihilator of degree

```text
2 * 6 = 12.
```

More generally, if an UNSAT kernel has `r` distinct positive weights, the
squared support-annihilator has degree at most `2r`.  Thus the first `2r` dual
moments always suffice to reconstruct this particular support certificate.

That observation is useful, but it is not yet universal: `r` may grow with the
instance size.

## 6. Immediate anti-loop: a connected 2-lift defeats level 12

To test whether `t=12` might accidentally be universal, E67 does not move to a
weaker gadget representation.  It stays inside the same post-quotient target
class.

Take the 126-vertex Tutte-12 incidence graph and perform the deterministic
binary 2-lift frozen by the companion checker (`seed=1`).  Its new incidence
matrix `L` has size

```text
126 x 126.
```

The checker proves:

```text
row weight    = 3,
column weight = 3,
linearity     = true,
connected     = true,
Levi girth    = 12,
dim_F2 ker L  = 16.
```

Its exact kernel weight enumerator is

```text
1
+ 4 z^16
+ 2 z^28
+ 160 z^32
+ 346 z^40
+ 190 z^44
+ 2800 z^48
+ 2796 z^52
+ 8396 z^56
+ 8770 z^60
+ 20531 z^64
+ 11380 z^68
+ 9034 z^72
+ 798 z^76
+ 328 z^80.
```

Thus

```text
max kernel weight = 80 < 84 = 2*126/3,
```

so the lift is Exact-One UNSAT.

Crucially, its positive support is already much richer than the six-weight base
code.

## 7. Exact level-12 Delsarte pseudodistribution

E67 supplies an explicit rational pseudo distribution `A'_w` supported on

```text
0,16,18,34,36,48,50,58,60,66,68,74,76,84
```

with

```text
A'_0  = 1,
A'_84 = 10158992251 / 334748700 > 30,
sum_w A'_w = 2^16.
```

The companion checker verifies exactly, using rational arithmetic, that

```text
for j=0,...,12:
    sum_w A'_w K_j(w) / 2^16 = B_j(L),
```

where the right side is the true dual weight count of the lift.

It then verifies for every remaining degree

```text
j=13,...,126
```

that

```text
sum_w A'_w K_j(w) / 2^16 >= 0.
```

Thus the pseudo distribution satisfies the full Delsarte positivity system
while matching the exact first 12 orientation-sensitive dual moments, yet it
places positive mass at the forbidden SAT top weight `84`.

Therefore

```text
boxed:
level 12 cannot certify this connected linear UNSAT instance.
```

This is a stronger anti-loop than a disconnected direct sum or a bounded-gadget
inflation example.

## 8. Frozen E12/RXC3 quotient sanity check

The user-requested hardness-bridge regression is also included.

For the frozen E17 q=6 RXC3 source fixture

```text
C_i = {i, i+1, i+3} mod 6,
```

with duplicate set entries removed exactly as in E17, the source matrix has

```text
dim_F2 ker R = 0.
```

Hence

```text
W_R(z)=1,
```

and `A_4=0` is already forced by `A_0=sum_w A_w=1` before any higher moment is
needed.  This regression passes, but it is intentionally classified as a
small-fixture sanity check, not evidence that level 12 handles the whole RXC3
hardness family.

The connected 2-lift firewall in Section 6 is the relevant universality test.

## 9. External anti-loop anchors

The machinery used here is standard coding-theory machinery:

* MacWilliams identities identify the Krawtchouk transform of a binary linear
  code's weight distribution with the weight distribution of its dual.
* Delsarte's LP relaxes actual code distributions to nonnegative
  Krawtchouk-feasible quasicodes.

Useful modern documentation includes Sage's implementation of Delsarte bounds,
which explicitly uses Krawtchouk constraints and nonnegative dual transforms,
and the coding-theory literature on Delsarte quasicodes.

These sources justify the external framework only.  The Tutte-12 annihilator,
2-lift, exact pseudo distribution, and all numerical identities above are
replayed self-contained in Fundamentum.

## 10. What survives E67

E67 changes the frontier in an important way.

We now have a genuine polynomially-checkable **one-sided hierarchy**:

```text
choose moment order t;
compute B_0,...,B_t;
solve / certify the Delsarte top-shell relaxation;
if A_{2n/3} is forced to zero -> UNSAT certificate;
otherwise -> UNKNOWN at level t.
```

For every fixed `t`, the low dual counts are computable in polynomial time
`n^{O(t)}`.

But `t=12` is not universal even on a connected cubic-linear girth-12 carrier.
Therefore the next research question is not

```text
Does level 12 solve everything?
```

It is

```text
Can the required moment order be bounded by O(1) or O(log n)
for all post-quotient square-cubic-linear carriers?
```

or, failing that,

```text
Can a stronger orientation-sensitive SDP / localizing-matrix hierarchy
compress the needed order polynomially?
```

The correct E68 stress test is to build a tower of connected covers/lifts and
measure how the minimum certificate order grows, while simultaneously checking
frozen RXC3 hardness quotients.

Scientific status remains

```text
P_VS_NP = OPEN.
```

## 11. Replay

Companion checker:

```text
experiments/r5_e67_dual_moment_delsarte_hierarchy.py
```

It verifies:

```text
* the full 2^14 Tutte-12 kernel enumerator;
* the six positive base weights;
* the exact degree-12 annihilator and its Krawtchouk expansion;
* the exact B_0,...,B_12 base dual counts;
* the connected cubic-linear girth-12 deterministic 2-lift;
* its full 2^16 kernel weight enumerator and max weight 80;
* the explicit rational pseudo distribution;
* equality of its first 12 dual moments with the true lift;
* all remaining Delsarte nonnegativity inequalities through j=126;
* the frozen E17/E12 q=6 RXC3 quotient sanity check.
```
