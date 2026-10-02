# R5 E18 — Schur-Square UNSAT Terminal and Kernel-Projective Quotient

Date: 2026-10-02

Status:
`SOUND_POLYNOMIAL_SCHUR_SQUARE_TERMINAL__D1_COMPLETE__EXPLICIT_Q2_FIREWALL__PROJECTIVE_KERNEL_QUOTIENT_IDENTIFIED`

Scientific ceiling:

```text
THIS NOTE ADDS A NEW POLYNOMIAL UNSAT TERMINAL AND A NEW EXACT KERNEL QUOTIENT.
IT ALSO CONSTRUCTS AN EXPLICIT 42-VARIABLE SQUARE+CUBIC+LINEAR UNSAT INSTANCE
THAT PASSES THE SCHUR-SQUARE/Q2 NECESSARY CONDITION.

THEREFORE Q2 IS NOT A UNIVERSAL ALGORITHM.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be square, cubic and linear, and write

```text
K = ker_Q(A).
```

As in R5 E10/E15, Exact-One is equivalent to

```text
y in K intersect {-1,2}^n,
```

via

```text
y = 3x - 1.
```

For vectors `u,v in Q^n`, write `u star v` for coordinatewise product.
Define the Schur square

```text
K^(star 2) = span_Q {u star v : u,v in K}.
```

## 2. Q2 / Schur-square necessary condition

Every Exact-One witness `y` obeys coordinatewise

```text
y star y - y = 2 * 1.
```

Since `y in K` and `y star y in K^(star 2)`, SAT implies

```text
boxed:
2 * 1 in K + K^(star 2).
```

Therefore:

### Theorem SCHUR-2

If

```text
2 * 1 notin K + K^(star 2),
```

then `A` is Exact-One UNSAT.

This is polynomial-time decidable by exact Gaussian elimination.  Given a basis
`b_1,...,b_d` of `K`, it is enough to test membership of `2*1` in the span of

```text
b_i,
b_i star b_j  (i<=j).
```

A dual certificate is any rational vector `c` satisfying

```text
c orthogonal to K,
c orthogonal to K^(star 2),
c^T 1 != 0.
```

All checks are polynomial.

## 3. Nullity-one completeness

When

```text
dim_Q K = 1,
```

SCHUR-2 is not merely necessary: it is complete.

Let `K=<b>`.  Q2 feasibility means there exist scalars `T,Z` such that for every
coordinate `i`

```text
b_i^2 Z - b_i T = 2.
```

If some `b_i=0`, this gives `0=2`, so Q2 rejects.
Otherwise every `b_i` is a root of the same quadratic polynomial

```text
Z s^2 - T s - 2.
```

Hence the coordinates of `b` take at most two nonzero values.  They cannot take
only one value because each source row contains three coordinates summing to zero.
Let the two values be `a,c`.  In every source row the zero-sum condition is either

```text
a + 2c = 0
```

or

```text
2a + c = 0.
```

Both row types cannot coexist unless `a=c=0`.  Thus one relation holds globally,
and after scaling

```text
b in {-1,2}^n.
```

Therefore:

```text
boxed:
nullity_Q(A)=1
=>
Q2 feasible iff Exact-One SAT.
```

This explains the frozen PG15_UNSAT control structurally rather than empirically.

## 4. Explicit Q2 firewall on 42 variables

The companion checker constructs the following exact instance.

Take all directed arcs

```text
i -> j,  i != j,
```

of `K_7`.  There are 42 variables.

There are 70 directed 3-cycles.  Remove two disjoint directed-triangle
decompositions `D1,D2`, each containing 14 cycles and covering every directed arc
exactly once.  The remaining 42 directed cycles are the source rows.

Because every directed arc originally lies in five directed 3-cycles and one cycle
from each decomposition is removed, every column has weight three.  Every row has
weight three.  Two distinct directed triangles share at most one directed arc.
Thus the resulting incidence matrix `A_42` is square+cubic+linear.

The checker verifies exactly

```text
rank_Q(A_42)    = 36,
nullity_Q(A_42) = 6.
```

## 5. Root kernel

Associate to arc `i->j` the root

```text
r_ij = e_i - e_j in Q^7.
```

Every directed triangle satisfies

```text
r_ij + r_jk + r_ki = 0.
```

Hence each of the seven coordinate functions of these roots is a kernel vector.
Their span has dimension six.  Since the full kernel also has dimension six,

```text
boxed:
K = { y_ij = t_i - t_j }.
```

## 6. Exact UNSAT but Q2 PASS

For every kernel vector,

```text
y_ji = -y_ij.
```

But the target alphabet is

```text
{-1,2},
```

and it contains no value `a` for which `-a` is also in the alphabet.  Therefore

```text
boxed:
A_42 is Exact-One UNSAT.
```

On the other hand every root has squared norm two:

```text
sum_c r_ij(c)^2 = 2.
```

The seven coordinate kernel vectors `u_c` therefore satisfy

```text
sum_c (u_c star u_c) = 2 * 1.
```

Thus

```text
boxed:
2 * 1 in K^(star 2),
```

so SCHUR-2/Q2 accepts the instance.

This is an explicit finite firewall:

```text
Q2 PASS does not imply SAT,
```

even for a square+cubic+linear source with `3 | n` and nonzero rational nullity.

## 7. Kernel-projective quotient

Let `B` be any basis matrix for `K`, with row vectors `b_i`.
Every centered Boolean witness has

```text
y_i = b_i t in {-1,2}.
```

Suppose two rows are proportional:

```text
b_j = lambda b_i.
```

Then necessarily

```text
y_j = lambda y_i.
```

The only possible ratios between two values from `{-1,2}` are

```text
1, -2, -1/2.
```

Therefore the following exact polynomial rules hold.

### KPROJ-0

If

```text
b_i = 0,
```

then the instance is UNSAT, because every rational solution has centered coordinate
`y_i=0`, which is outside `{-1,2}`.

### KPROJ-BAD-RATIO

If nonzero proportional rows have

```text
lambda notin {1,-2,-1/2},
```

then the instance is UNSAT.

The 42-variable root firewall is caught immediately because

```text
b_ji = - b_ij,
```

and `-1` is a forbidden ratio.

### KPROJ-EQUALITY

If

```text
lambda = 1,
```

then every Boolean witness satisfies

```text
x_i = x_j.
```

The two variables may be identified exactly and all source rows rewritten on the
quotient.

### KPROJ-FORCED

If

```text
lambda = -2
```

or

```text
lambda = -1/2,
```

then the two centered values are forced to `(-1,2)` or `(2,-1)` respectively,
so the corresponding Boolean variables are fixed to `(0,1)` or `(1,0)`.

These rules are basis-invariant because proportionality and its scalar ratio are
unchanged by invertible changes of kernel coordinates.

## 8. Router update

The post-E17 algebraic router should now include, before expensive kernel
enumeration:

```text
K0  compute exact rational kernel basis
K1  zero-row test
K2  projective-row ratio test
K3  propagate forced {-2,-1/2} classes
K4  quotient equal-row classes
K5  rerun cardinality/rank/AF3/clique/commuting/separator terminals
K6  SCHUR-2 membership test
```

The Q2 firewall shows that SCHUR-2 is a terminal, not a complete algorithm.
The KPROJ rules remain exact and survive the firewall.

## 9. New frontier

The relevant hard core must now survive all of:

```text
no zero kernel rows,
no forbidden projective ratios,
no useful equality quotient,
no forced projective assignments,
SCHUR-2 feasible,
large effective kernel after local quotient,
no bounded-interface decomposition,
no clique-LP/source-aligned obstruction,
no commuting or near-commuting terminal.
```

A universal polynomial theorem is still missing.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e18_schur_square_projective_kernel.py
```
