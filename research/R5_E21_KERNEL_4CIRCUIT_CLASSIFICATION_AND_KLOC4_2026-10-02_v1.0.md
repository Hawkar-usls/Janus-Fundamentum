# R5 E21 — Kernel 4-Circuit Classification and KLOC-4 Frontier

Date: 2026-10-02

Status:
`EXACT_4CIRCUIT_RELATION_CLASSIFICATION__KLOC3_STRICTNESS_FIREWALL__KLOC4_POLYNOMIAL_TERMINAL__THREE_NONTRIVIAL_SURVIVOR_FAMILIES`

Scientific ceiling:

```text
THIS NOTE CLASSIFIES EVERY MINIMAL FOUR-ROW KERNEL CIRCUIT OVER THE
CENTERED BOOLEAN ALPHABET {-1,2}.

UP TO PERMUTING THE FOUR COORDINATES THERE ARE EXACTLY 17 POSSIBLE
LOCAL BOOLEAN RELATION TYPES.

KLOC-3 IS STRICTLY WEAKER THAN KLOC-4 EVEN FOR A THREE-DIMENSIONAL
RATIONAL KERNEL SUBSPACE.

AFTER EMPTY / FORCED / EQUALITY / COMPLEMENT PROPAGATION, THE ONLY
NONTRIVIAL FOUR-CIRCUIT RELATION FAMILIES THAT REMAIN ARE:

  SIGNED EXACT-ONE,
  SWITCH4,
  BALANCE4.

THIS DOES NOT PROVE THAT KLOC-4 IS UNIVERSAL.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic+linear Exact-One source after the exact reductions of
R5 E17--E20.  Let

```text
K = ker_Q(A),
B in Q^{n x d},
col(B)=K,
```

and write `b_i` for row `i` of `B`.

Every Boolean witness is equivalent to

```text
y = B t,
y_i in Sigma={-1,2}.
```

A minimal four-row kernel circuit is a set `{i,j,k,l}` with

```text
rank{b_i,b_j,b_k,b_l}=3
```

and every three-row subset independent.  Its unique dependence, up to nonzero
scaling, is

```text
c_1 b_i+c_2 b_j+c_3 b_k+c_4 b_l=0,
```

where minimality is equivalent to

```text
c_1 c_2 c_3 c_4 != 0.
```

Therefore every Boolean witness must satisfy

```text
c_1 y_i+c_2 y_j+c_3 y_k+c_4 y_l=0,
y_* in {-1,2}.
```

The induced local relation is

```text
R(c)={y in {-1,2}^4 : c^T y=0}.
```

In Boolean coordinates `y=3x-1`, the same relation is

```text
3 c^T x = sum(c).
```

## 2. Why the classification is finite

There are only sixteen centered Boolean vectors in `Sigma^4`.

For fixed nonzero `c`, `R(c)` is exactly the set of those sixteen points lying in
the rational hyperplane

```text
H_c = c^perp.
```

Let

```text
H = span_Q(R(c)).
```

Then

```text
dim(H)<=3
```

and

```text
R(c)=H intersect Sigma^4.
```

Conversely, let `H` be any rational subspace spanned by at most three alphabet
points.  A generic vector

```text
c in H^perp
```

is orthogonal to exactly the alphabet points already lying in `H`.

The four-circuit minimality condition `c_i != 0` for every coordinate is possible
exactly when `H^perp` is not contained in any coordinate hyperplane.  Equivalently,
`H` contains no standard basis vector `e_i`.

Thus the infinite coefficient problem reduces exactly to a finite enumeration:

```text
1. enumerate every span of <=3 points of Sigma^4;
2. discard spans containing some e_i;
3. take R = H intersect Sigma^4;
4. quotient the resulting relations by S_4 coordinate permutations.
```

The companion exact checker performs precisely this enumeration with rational
`Fraction` arithmetic.

## 3. Exact count

The checker finds

```text
114 labelled realizable four-circuit relations
```

with all four circuit coefficients nonzero.

Modulo coordinate permutation there are exactly

```text
17 orbits.
```

Their distribution by number of allowed Boolean patterns is

```text
|R|=0 : 1 orbit
|R|=1 : 3 orbits
|R|=2 : 5 orbits
|R|=3 : 5 orbits
|R|=4 : 2 orbits
|R|=6 : 1 orbit
```

No other relation size occurs.

Canonical orbit representatives are:

```text
|R|=0
  {}

|R|=1
  {0001}
  {0011}
  {0111}

|R|=2
  {0000,1111}
  {0001,0111}
  {0011,0101}
  {0011,1101}
  {0111,1011}

|R|=3
  {0001,0010,1100}
  {0001,0111,1011}
  {0011,0101,0110}
  {0011,0101,1110}
  {0111,1011,1101}

|R|=4
  {0000,0011,1100,1111}
  {0001,0010,0111,1100}

|R|=6
  {0000,0011,0101,1010,1100,1111}
```

## 4. Immediate polynomial actions

Every four-circuit is found and classified using exact rational arithmetic.
For fixed arity four, exhaustive enumeration costs

```text
O(n^4 poly(n)).
```

The first relation classes are immediately reducible.

### EMPTY

```text
R={}
```

is a short exact UNSAT certificate.

### SINGLETON

A one-pattern relation fixes all four Boolean variables.

### TWO-PATTERN

Any relation containing exactly two bit strings has at most one Boolean degree of
freedom.  Choose one differing coordinate as a representative bit; every other
coordinate is then one of

```text
fixed 0,
fixed 1,
equal to the representative,
complement of the representative.
```

So every two-pattern four-circuit reduces to ordinary forcing plus equality /
complement union-find.

No branching is required.

## 5. Three-pattern relations collapse to signed Exact-One

The five three-pattern orbits are not five new hard languages.  Each reduces to
one signed Exact-One relation plus only forcing/equality/complement information.

Representative reductions are:

```text
{0001,0010,1100}
  <=> x1=x2
      AND ExactOne(x1,x3,x4)

{0001,0111,1011}
  <=> x4=1
      AND ExactOne(x1,x2,not x3)

{0011,0101,0110}
  <=> x1=0
      AND ExactOne(not x2,not x3,not x4)

{0011,0101,1110}
  <=> x4=not x1
      AND ExactOne(x1,not x2,not x3)

{0111,1011,1101}
  <=> x4=1
      AND ExactOne(not x1,not x2,not x3)
```

Hence the three-pattern layer adds signed/literal polarity, but no genuinely new
arity-four relation.

This does **not** make the signed Exact-One remainder polynomial by itself; it is
retained as a hard relation family.

## 6. The two four-pattern orbits

The first four-pattern orbit is pure quotient structure:

```text
{0000,0011,1100,1111}
  <=> x1=x2 AND x3=x4.
```

It is removed by equality propagation.

The second orbit is genuinely four-ary:

```text
SWITCH4 = {0001,0010,0111,1100}.
```

One coefficient representative is

```text
c=(2,-1,1,1),
```

so in Boolean coordinates

```text
2 x1 - x2 + x3 + x4 = 1.
```

Equivalently:

```text
if (x1,x2)=(0,0), then x3+x4=1;
if (x1,x2)=(0,1), then x3=x4=1;
if (x1,x2)=(1,1), then x3=x4=0;
(x1,x2)=(1,0) is forbidden.
```

This relation is retained explicitly as `SWITCH4` rather than being silently
called tractable.

## 7. The six-pattern orbit

The unique six-pattern relation is

```text
BALANCE4 = {0000,0011,0101,1010,1100,1111}.
```

A coefficient representative is

```text
c=(1,-1,-1,1),
```

hence

```text
boxed:
x1+x4 = x2+x3.
```

This is a genuine pair-sum conservation law.  It is retained as `BALANCE4`.

Therefore, after the cheap quotient/forcing actions, the four-circuit frontier is
reduced to only

```text
SIGNED_EXACT_ONE,
SWITCH4,
BALANCE4.
```

## 8. Strictness firewall: KLOC-3 < KLOC-4

KLOC-3 cannot be promoted to a complete kernel-alphabet test even abstractly.

Take the three-dimensional subspace

```text
K={y in Q^4 : y1+y2+y3+y4=0}.
```

A basis matrix is

```text
B =
[ 1  0  0 ]
[ 0  1  0 ]
[ 0  0  1 ]
[-1 -1 -1 ].
```

Every three rows of `B` are independent.  Therefore every three-coordinate
projection of `K` is all of `Q^3`, and in particular intersects `{-1,2}^3`.
Thus every KLOC-3 test passes.

But a full alphabet vector with `k` coordinates equal to `2` has total sum

```text
-4 + 3k,
```

which is never zero for integer `k in {0,1,2,3,4}`.

Hence

```text
K intersect {-1,2}^4 = empty.
```

So KLOC-4 rejects while all KLOC-3 projections pass:

```text
boxed:
KLOC-3 is strictly weaker than KLOC-4.
```

This is an abstract kernel firewall.  It is **not** claimed here that this exact
four-coordinate subspace is already realized as a standalone square+cubic+linear
source.  Carrier realization is a separate structural question.

## 9. Router update

The post-E20 kernel router becomes:

```text
K0  exact rational kernel
K1  KLOC-1 / zero-row UNSAT
K2  KLOC-2 / projective ratio rules
K3  equality / complement / forced propagation and quotient
K4  rerun cheap exact source terminals
K5  bounded-interface / local-gauge quotient
K6  KCIRC3 saturation
K7  KCIRC4 / KLOC-4 saturation
      EMPTY       -> UNSAT
      singleton   -> force
      two-pattern -> one-bit equality/complement propagation
      three-pattern -> signed Exact-One + propagation
      four-pattern equality -> quotient
      SWITCH4     -> retain exact table
      BALANCE4    -> retain exact equation
K8  optional higher fixed KLOC-s / moment terminals
```

Every step through K7 is polynomial.

## 10. New universal frontier

A genuine post-E21 hard core must survive all earlier E20 conditions and, in
addition, every minimal four-circuit must avoid the terminating/quotient classes.
After saturation, all surviving four-circuit information is expressible using only

```text
signed Exact-One constraints,
SWITCH4 constraints,
BALANCE4 constraints.
```

This gives two concrete next attacks:

```text
A. Determine whether SWITCH4 and BALANCE4 close under polynomial propagation /
   decomposition together with signed Exact-One on this kernel-matroid carrier.

B. Construct a square+cubic+linear UNSAT family surviving complete KLOC-4
   saturation; such a family would be the required firewall before considering
   KLOC-5.
```

No claim is made that any fixed local radius is universally sufficient.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e21_kernel_4circuit_classification.py
```
