# R5 E25 — Toroidal Long-Trade Firewall

Date: 2026-10-02

Status:
`EXACT_CARRIER_SPECIFIC_LINEAR_SUPPORT_TRADE_FIREWALL__LOCAL_AUGMENTATION_NOT_UNIVERSAL__GLOBAL_STRUCTURE_REQUIRED`

Scientific ceiling:

```text
THIS NOTE KILLS THE NAIVE TRADE-DESCENT HOPE THAT EVERY NON-BOOLEAN INTEGER
SOLUTION ADMITS A SMALL-SUPPORT IMPROVING KERNEL MOVE.

ON THE R5 E10 TOROIDAL SAT FAMILY WITH 3|k, EVERY NONZERO INTEGER KERNEL
TRADE HAS SUPPORT AT LEAST 2n/3, AND THIS BOUND IS ATTAINED.

A NON-BOOLEAN INTEGER SOLUTION IS BOOLEANIZED BY SUCH A LINEAR-SUPPORT TRADE.
THEREFORE CONSTANT- OR LOG-SUPPORT TRADE ENUMERATION CANNOT BE A UNIVERSAL
AUGMENTATION THEOREM, EVEN ON SAT SQUARE+CUBIC+LINEAR CARRIERS.

P_VS_NP = OPEN.
```

## 1. Toroidal carrier

Use the R5 E10 family with variables

```text
x_{i,j},  i,j in Z_k
```

and clauses

```text
C_{i,j}={x_{i,j},x_{i+1,j},x_{i,j+1}}.
```

For `3|k`, R5 E10 proves

```text
n=k^2,
rank_Q(A_k)=n-2,
nullity_Q(A_k)=2,
```

and gives an explicit Exact-One witness by residue class of `i-j mod 3`.

The family is square, cubic and linear.

## 2. Exact kernel structure

For a triple

```text
u=(u_0,u_1,u_2)
```

with

```text
u_0+u_1+u_2=0,
```

define

```text
y_{i,j}=u_{i-j mod 3}.
```

Every clause sees the three residue classes exactly once, so its row sum is

```text
u_0+u_1+u_2=0.
```

Thus this residue-constant space is contained in `ker_Q(A_k)` and has dimension
two.

R5 E10 already gives

```text
nullity_Q(A_k)=2,
```

therefore the inclusion is equality:

```text
boxed:
ker_Q(A_k)
=
{ y_{i,j}=u_{i-j mod 3} : u_0+u_1+u_2=0 }.
```

## 3. Integer kernel trades have linear support

Let

```text
z in ker_Z(A_k)
```

be nonzero.

By the exact kernel description, `z` has constant integer values

```text
(a,b,c)
```

on the three residue classes and

```text
a+b+c=0.
```

A nonzero triple with sum zero cannot have only one nonzero entry.  Hence at least
two residue classes are nonzero.

Each residue class contains exactly

```text
n/3
```

variables.  Therefore

```text
boxed:
|supp(z)| >= 2n/3
```

for every nonzero integer trade.

The bound is attained by

```text
(a,b,c)=(1,-1,0).
```

So the minimum nonzero integer-kernel support is exactly

```text
boxed:
trade_support_min(A_k)=2n/3.
```

## 4. Explicit non-Boolean integer solution

Assign residue-class values

```text
(2,-1,0).
```

Every clause contains one coordinate of each residue class, hence has sum

```text
2+(-1)+0=1.
```

Thus

```text
x_bad in Z^n,
A_k x_bad=1.
```

It is not Boolean.

Its R5 E24 defect is

```text
Phi(x_bad)
= (n/3)*2*(2-1)
  + (n/3)*(-1)*(-2)
= 4n/3.
```

## 5. Booleanization requires a global move

The standard Boolean witness uses residue-class values

```text
(1,0,0).
```

The difference is

```text
x_sat-x_bad=(-1,+1,0),
```

which is an integer kernel trade with support exactly

```text
2n/3.
```

It reduces

```text
Phi: 4n/3 -> 0.
```

Because every nonzero integer kernel trade has support at least `2n/3`, there is no
smaller-support augmentation at all.

Therefore any descent rule of the form

```text
if x is non-Boolean, search all kernel moves supported on at most f(n) variables
```

fails on this SAT family whenever

```text
f(n) < 2n/3.
```

In particular, no universal constant-support or logarithmic-support theorem is
possible.

## 6. Why this matters after R5 E24

R5 E24 suggested attacking the integer-to-Boolean gap by convex defect descent over
integer kernel trades.

E25 shows the descent direction may be intrinsically global even on a highly
structured, explicitly solvable SAT family.

So a valid polynomial trade-descent theorem cannot rely on

```text
bounded support,
small local circuit radius,
or brute enumeration of primitive local trades.
```

It must exploit a compact global representation of the trade space.

For the torus, that compact representation is precisely the R5 E13 commuting /
translation normal form: the huge support move is specified by only the three
residue values `(-1,+1,0)`.

This strongly supports a router philosophy:

```text
large-support trade
need not mean hard
if it has low-description global structure.
```

## 7. New target parameter

Support size is therefore the wrong complexity measure for a trade.

A more useful target is **trade description complexity**:

```text
How many global degrees of freedom are needed to specify an improving kernel move?
```

Examples already in Fundamentum:

```text
commuting torus:
  support Theta(n), description dimension 2;

E16 block ring:
  large raw support possible, but bounded interfaces expose compact block states;

E17 hardness gadget:
  large raw nullity collapses after local-gauge quotient;

post-E23 generic hard core:
  description complexity still unknown.
```

This suggests the next theorem target:

```text
TRADE-COMPRESSION DICHOTOMY

For every projectively reduced integer-feasible square+cubic+linear carrier,
either
  (A) produce an improving trade from a polynomial-size global description,
  (B) produce an exact polynomial UNSAT certificate for min Phi>0,
  (C) decompose / quotient the carrier,
  or
  (D) expose a genuinely high-description trade core.
```

The last branch is now the correct firewall target.

## 8. What E25 does not say

The toroidal family is SAT and already polynomially solved by R5 E13-style global
algebraic structure.

Therefore E25 is **not** evidence that trade descent is impossible in general.  It
only proves that local-support enumeration is the wrong implementation of it.

The remaining possibility is a polynomial algorithm that recognizes and manipulates
large trades symbolically.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e25_toroidal_long_trade_firewall.py
```
