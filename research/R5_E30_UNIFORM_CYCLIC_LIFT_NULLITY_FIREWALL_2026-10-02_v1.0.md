# R5 E30 — Uniform Cyclic-Lift Nullity Firewall

Date: 2026-10-02

Status:
`EXACT_LAURENT_DETERMINANT_FIREWALL__FIXED_BASE_UNIFORM_CYCLIC_LIFTS_HAVE_BOUNDED_NULLITY__HIGH_NULLITY_REQUIRES_NONUNIFORM_OR_GROWING_STRUCTURE`

Scientific ceiling:

```text
THIS NOTE RULES OUT A NATURAL CONSTRUCTION ROUTE FOR THE POST-E29
NONCOMMUTATIVE HIGH-NULLITY FRONTIER.

TAKE ANY FIXED FINITE PERMUTATION BASE P0,Q0 AND FORM A CYCLIC LIFT
WITH UNIFORM GENERATOR VOLTAGES a,b:

  P = P0 tensor S^a,
  Q = Q0 tensor S^b.

FOR FIXED BASE AND FIXED INTEGER SHIFTS, THE NULLITY OF

  A_r = I + P + Q

IS BOUNDED BY A CONSTANT INDEPENDENT OF THE CYCLIC LIFT SIZE r.

SO THIS STANDARD TENSOR/VOLTAGE TRICK CANNOT CREATE THE REQUIRED
Theta(n) EFFECTIVE KERNEL.

P_VS_NP = OPEN.
```

## 1. Lift model

Let `P0,Q0` be permutation matrices of size `m`, with no assumption that they
commute.

Let `S_r` be the cyclic shift permutation on `Z_r`.
Fix integers `a,b` independent of `r` and define

```text
P_r = P0 tensor S_r^a,
Q_r = Q0 tensor S_r^b,
A_r = I + P_r + Q_r.
```

The total matrix size is

```text
n = m r.
```

This includes genuinely noncommuting bases whenever

```text
P0 Q0 != Q0 P0.
```

## 2. Fourier reduction in the cyclic coordinate

Over `C`, diagonalize the cyclic shift.  For every `r`th root of unity `z`, the
corresponding Fourier block of `A_r` is

```text
M(z) = I_m + z^a P0 + z^b Q0.
```

Therefore

```text
nullity_C(A_r)
=
sum_{z^r=1} nullity_C(M(z)).
```

Define the Laurent determinant

```text
f(z)=det(I_m + z^a P0 + z^b Q0).
```

A Fourier block can be singular only at a zero of `f`.

## 3. The determinant is never identically zero

Consider the three exponent levels

```text
E={0,a,b}.
```

### Case 1: one exponent is a unique maximum

Suppose `e_max` is achieved by exactly one of the three matrices

```text
I_m, P0, Q0.
```

In the determinant expansion, the largest possible Laurent exponent is

```text
m e_max.
```

To attain it, every selected matrix entry must come from the unique
`e_max`-matrix.  Hence the coefficient of `z^(m e_max)` is exactly the determinant
of that matrix:

```text
det(I_m)=1,
det(P0)=+-1,
or det(Q0)=+-1.
```

It is nonzero.

### Case 2: the maximum exponent is tied

If two exponent levels tie for the maximum, then the remaining exponent is the
unique minimum unless all three levels are equal.

Apply the same argument to the smallest Laurent exponent.  Its coefficient is the
determinant of the unique minimum-level permutation matrix and is nonzero.

If all three exponent levels are equal, then

```text
a=b=0
```

and `f` is simply the constant determinant

```text
det(I_m+P0+Q0).
```

If that constant is zero, every lift is just `r` disconnected identical copies of
the same base operator; this is a decomposition case, not a growing connected
phase mechanism.  For every genuine phase lift, at least two exponent levels are
distinct and the unique-extreme argument applies.

Therefore, for every genuine uniform cyclic phase lift,

```text
boxed:
f(z) is a nonzero Laurent polynomial.
```

## 4. Uniform bound on the number of singular Fourier modes

Let

```text
Delta = max{0,a,b} - min{0,a,b}.
```

After multiplying `f(z)` by a monomial, we obtain an ordinary nonzero polynomial of
degree at most

```text
m Delta.
```

Hence it has at most

```text
m Delta
```

distinct complex roots.

Only those roots can coincide with `r`th roots of unity and produce singular
Fourier blocks.

Each block has size `m`, so

```text
nullity_C(A_r) <= m * (m Delta).
```

Thus

```text
boxed:
nullity_Q(A_r)=nullity_C(A_r) <= m^2 Delta.
```

The right side depends only on the fixed base and fixed voltage shifts, not on `r`.

Therefore

```text
boxed:
fixed-base + fixed-uniform-cyclic-voltage
cannot produce growing rational nullity.
```

## 5. Consequence for projective diversity and E28

Since

```text
d = O(1)
```

for this lift scheme, the old R5 E10 rational-nullity terminal already solves the
family in

```text
O(2^d poly(n)) = poly(n).
```

So such families cannot realize the post-E29 target

```text
large effective nullity
+
large projective diversity
+
large projective-quotient width.
```

This remains true even when the finite base itself is noncommutative.

## 6. What construction routes remain alive

E30 does not rule out cyclic or covering ideas in general.  It rules out the
simplest fixed-base uniform-voltage version.

A growing-nullity construction must use at least one ingredient outside this
regime, for example:

```text
1. a base size m that itself grows with n;
2. voltage shifts whose description/degree grows with r;
3. nonuniform row-dependent voltages;
4. several coupled fibers with a determinant relation not reducible to one fixed
   Laurent polynomial;
5. a non-lift construction altogether.
```

Each surviving route must still preserve square+cubic+linear structure and survive
the E17--E29 exact quotient/obstruction branches.

## 7. Updated construction frontier

After E29 and E30, the desired first genuine high-description carrier must be

```text
connected,
genuinely noncommutative,
not a fixed-base uniform cyclic lift,
large effective nullity,
large q,
large projective-quotient width,
large adhesion,
KPROJ/KLOC-clean at the current levels,
integer-feasible,
and outside all known commuting/separator/normal-form branches.
```

This is a much narrower construction target than the pre-E28 search.

```text
P_VS_NP = OPEN.
```
