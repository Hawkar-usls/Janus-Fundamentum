# R5 E24 — Integer-to-Boolean Energy Gap and Affine Kernel CVP Form

Date: 2026-10-02

Status:
`EXACT_INTEGER_DEFECT_IDENTITY__AFFINE_KERNEL_CVP_REFORMULATION__UNIVERSAL_GAP_18__PG15_SHARPNESS_FIREWALL`

Scientific ceiling:

```text
THIS NOTE IDENTIFIES THE POST-E23 INTEGER-TO-BOOLEAN GAP WITH AN EXACT
CLOSEST-VECTOR PROBLEM IN ONE CONGRUENCE CLASS OF THE INTEGER KERNEL.

FOR EVERY INTEGER-FEASIBLE SQUARE+CUBIC SOURCE, SAT IS EQUIVALENT TO
ATTAINING SQUARED NORM 2n.  IF THE INSTANCE IS INTEGER-FEASIBLE BUT
BOOLEAN-UNSAT, THE SQUARED NORM IS AT LEAST 2n+18.

THE FROZEN PG15_UNSAT CONTROL ATTAINS 2n+18 EXACTLY, SO THE ADDITIVE GAP 18
IS SHARP.

THIS IS A STRUCTURAL REFORMULATION, NOT A POLYNOMIAL CVP ALGORITHM.
P_VS_NP = OPEN.
```

## 1. Integer-feasible survivor

After R5 E23, consider a square+cubic Exact-One source

```text
A in {0,1}^{n x n},
A 1 = A^T 1 = 3 1,
```

for which

```text
A x = 1
```

has at least one integer solution.

Every integer solution obeys

```text
3 sum_i x_i = 1^T A x = n,
```

hence

```text
sum_i x_i = n/3.
```

In particular integer feasibility already implies `3|n`.

## 2. Boolean defect

Define

```text
Phi(x) = sum_i x_i(x_i-1).
```

For an integer `m`,

```text
m(m-1) >= 0
```

with equality exactly for

```text
m in {0,1}.
```

Moreover `m(m-1)` is always even.

Therefore for every integer vector `x`,

```text
Phi(x) in 2 Z_{>=0},
```

and

```text
boxed:
Phi(x)=0
iff
x in {0,1}^n.
```

On the affine integer solution lattice of `A x=1`, Exact-One SAT is therefore
exactly the question whether the minimum defect is zero.

## 3. Centered kernel identity

Put

```text
y = 3x - 1.
```

Then

```text
A y = 3 A x - A 1 = 0,
```

so every integer solution gives

```text
y in ker_Z(A),
y == -1 mod 3 coordinatewise.
```

Conversely every such `y` yields

```text
x=(y+1)/3 in Z^n
```

with `A x=1`.

Now expand the squared norm:

```text
||y||^2
= sum_i (3x_i-1)^2
= 9 sum_i x_i^2 - 6 sum_i x_i + n.
```

Since

```text
sum_i x_i^2
= Phi(x) + sum_i x_i
= Phi(x) + n/3,
```

we obtain

```text
boxed:
||y||^2 = 2n + 9 Phi(x).
```

## 4. Universal norm gap

Because `Phi(x)` is an even nonnegative integer,

```text
Phi(x) in {0,2,4,6,...}.
```

Hence the centered squared norms in the integer-feasible congruence class are
quantized as

```text
||y||^2 in {2n, 2n+18, 2n+36, ...}.
```

Therefore:

### Theorem BOX-GAP

For an integer-feasible square+cubic source,

```text
A is Exact-One SAT
iff
min { ||y||^2 :
      y in ker_Z(A),
      y == -1 mod 3 } = 2n.
```

If the instance is Exact-One UNSAT, then

```text
boxed:
min ||y||^2 >= 2n+18.
```

The lower bound `2n` is attained exactly by vectors with coordinates in

```text
{-1,2},
```

because `Phi=0` is exactly the Boolean condition.

## 5. Affine-lattice CVP form

Assume R5 E23 supplies one integer solution `x_0`, and put

```text
y_0 = 3 x_0 - 1.
```

Let

```text
L = ker_Z(A).
```

Any other integer solution is

```text
x=x_0+z,
z in L.
```

Therefore its centered vector is

```text
y = y_0 + 3 z.
```

So the entire integer-feasible congruence class is the affine lattice coset

```text
boxed:
y_0 + 3 L.
```

The remaining decision problem is exactly

```text
find the shortest vector in the coset y_0+3L
and test whether its squared norm is 2n.
```

Thus the post-E23 frontier may be written as an exact closest-vector problem in the
integer kernel lattice.

This does not make it polynomial: general CVP is precisely the sort of global
integer geometry that the earlier rational/local relaxations avoided.

## 6. PG15_UNSAT attains the gap exactly

For the frozen PG15_UNSAT source, R5 E23 uses the primitive kernel generator

```text
z = (1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

One integer solution is

```text
x_0 = (1,3,1,1,-1,-1,1,-1,-1,-1,-1,1,1,1,1).
```

Shift once along the integer kernel:

```text
x_* = x_0 - z
```

and obtain

```text
x_* = (0,-1,0,0,1,1,0,1,1,1,1,0,0,0,0).
```

Direct exact verification gives

```text
A x_* = 1.
```

Its defect is

```text
Phi(x_*) = (-1)(-2) = 2,
```

all other coordinates contributing zero.

Hence for `n=15`,

```text
||3x_*-1||^2
= 2*15 + 9*2
= 48
= 2n+18.
```

Because PG15_UNSAT has one-dimensional integer kernel, the objective along the
whole affine lattice is an explicit convex quadratic in the single integer step.
The companion checker verifies that `x_*` is the exact nearest integer solution.

Therefore the universal additive gap is sharp:

```text
boxed:
INTEGER-FEASIBLE UNSAT CAN OCCUR AT THE VERY FIRST POSSIBLE LEVEL 2n+18.
```

## 7. Consequence for approximation strategies

The SAT and first UNSAT thresholds are

```text
2n
vs
2n+18.
```

Their multiplicative ratio is

```text
1 + 9/n.
```

Thus any strategy that only provides a coarse constant-factor or fixed-epsilon
approximation to the affine-lattice norm cannot distinguish the two regimes for
large `n`.

A successful lattice route must exploit exact carrier structure, an exact dual
certificate, or an exact descent/compression theorem.  The gap cannot simply be
widened: PG15 proves it is already optimal.

## 8. Trade / augmentation form

Integer solutions form

```text
x_0 + ker_Z(A).
```

An integer kernel vector is a balanced trade: adding it preserves every Exact-One
row sum over the integers.

For `z in ker_Z(A)`,

```text
Phi(x+z)-Phi(x)
= 2 x^T z + ||z||^2,
```

because `1^T z=0` follows from `A z=0` and `1^T A=3 1^T`.

More generally, along an integer multiple `t z`,

```text
Phi(x+t z)
= Phi(x) + 2t x^T z + t^2 ||z||^2.
```

So Booleanization can be viewed as exact convex descent over the integer trade
lattice.

This suggests the next structural target:

```text
TRADE-DESCENT THEOREM:
for every projectively reduced integer-feasible non-Boolean source,
find in polynomial time either
  * a kernel trade that strictly lowers Phi,
  * a polynomial UNSAT certificate proving min Phi>0,
  * or an exact decomposition/quotient.
```

A proof that repeated descent always reaches `Phi=0` on SAT instances and certifies
positive minimum on UNSAT instances would close the remaining box gap.

No such universal theorem is claimed here.

## 9. Updated frontier

After R5 E24, the unresolved hard core is an instance for which

```text
integer feasibility passes,
all cheap projective/KLOC/circuit reductions pass or saturate,
no bounded-interface quotient applies,
and the affine kernel coset y_0+3 ker_Z(A)
has unknown exact minimum norm.
```

The next attack should focus on the structure of primitive integer kernel trades
and exact convex defect descent, rather than increasing a fixed local KLOC radius.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e24_integer_box_energy_gap.py
```
