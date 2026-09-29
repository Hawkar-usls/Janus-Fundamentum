# R5 E9 — Integer L1 circuit-augmentation barrier

Date: 2026-09-29

Status: `JANUS_EXACT_FINITE_HOSTILE_CONTROL__ALL_RATIONAL_CIRCUIT_LINES_LOCAL__GLOBAL_INTEGER_L1_GAP__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_INTEGER_LATTICE_L1_GRAVER_AUGMENTATION_GATE_2026-09-29_v1.0.md`
- `research/R5_E9_ONE_EDGE_TWIST_2LIFT_DISSOCIATED_NULLITY_AMPLIFIER_2026-09-27_v1.0.md`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE A LOWER BOUND FOR INTEGER PROGRAMMING OR SAT.
IT FALSIFIES THE SPECIFIC UNIVERSAL PROPOSAL THAT SUPPORT-MINIMAL
RATIONAL KERNEL CIRCUITS PLUS EXACT INTEGER LINE SEARCH SUFFICE FOR THE
LIVE ODD-COSET L1 OPTIMIZATION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen source

Use the frozen unique-model `18_3` source from the trade-free theorem, with
unique Exact-One model

```text
x*=(1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0).
```

Its rational kernel has dimension two. One integer basis is

```text
k1=(0,0,-2,-2,3,3,1,2,-3,0,-1,-1,-3,-1,3,0,1,0),
k2=(-2,-2,0,3,-2,-5,0,-1,4,-2,2,-1,4,2,-2,1,0,1).
```

Define the complement feasible integer point

\[
z^c=\mathbf1-2x^*.
\]

The complement theorem gives

\[
Az^c=\mathbf1,
\qquad
F(z^c)=\sum_i|2z_i^c-1|=30,
\]

whereas

\[
F(x^*)=18.
\]

Thus `z^c` is not globally optimal.

## 2. Complete circuit enumeration in a two-dimensional kernel

A rational circuit of `A` is a nonzero kernel vector with inclusion-minimal
support.

Because `ker_Q(A)` has dimension two, every circuit direction is obtained by
intersecting the kernel plane with a coordinate hyperplane `v_i=0`: any
full-support vector cannot be support-minimal because a nonzero coordinate
functional on a two-dimensional kernel has a one-dimensional zero set.

For each coordinate `i`, the vector

\[
k2_i k1-k1_i k2
\]

therefore generates the candidate circuit line whenever nonzero. Removing
scalar duplicates gives exactly nine projective circuit directions.

Primitive integer representatives, with first nonzero coordinate positive, are:

```text
c1=(0,0,2,2,-3,-3,-1,-2,3,0,1,1,3,1,-3,0,-1,0)
c2=(2,2,-2,-5,5,8,1,3,-7,2,-3,0,-7,-3,5,-1,1,-1)
c3=(2,2,0,-3,2,5,0,1,-4,2,-2,1,-4,-2,2,-1,0,-1)
c4=(2,2,4,1,-4,-1,-2,-3,2,2,0,3,2,0,-4,-1,-2,-1)
c5=(4,4,2,-4,1,7,-1,0,-5,4,-3,3,-5,-3,1,-2,-1,-2)
c6=(4,4,6,0,-5,1,-3,-4,1,4,-1,5,1,-1,-5,-2,-3,-2)
c7=(6,6,4,-5,0,9,-2,-1,-6,6,-4,5,-6,-4,0,-3,-2,-3)
c8=(6,6,8,-1,-6,3,-4,-5,0,6,-2,7,0,-2,-6,-3,-4,-3)
c9=(6,6,10,1,-9,0,-5,-7,3,6,-1,8,3,-1,-9,-3,-5,-3)
```

This list is complete up to nonzero rational scaling.

## 3. Exact integer line search

For one primitive circuit `c`, define

\[
f_c(t)=F(z^c+t c),\qquad t\in\mathbb Z.
\]

`f_c` is a convex sequence because it is a sum of absolute values of affine
functions of `t`. Therefore `t=0` is a global integer minimizer whenever

\[
f_c(-1)\ge f_c(0)\le f_c(1).
\]

Exact evaluation gives:

```text
           F(zc+c)   F(zc-c)
c1            62        66
c2           108       130
c3            56        92
c4            58        92
c5            80       130
c6            82       130
c7           118       174
c8           118       174
c9           154       196
```

while

```text
F(zc)=30.
```

Hence for every rational circuit line and every integer step `t`,

\[
\boxed{F(z^c+t c)\ge30.}
\]

Yet the feasible Boolean point `x*` has objective `18`.

### Theorem ICA-1

The frozen connected linear-cubic Exact-One source contains an integer feasible
point that is locally optimal along **every** support-minimal rational kernel
circuit under exact integer line search, but is not globally optimal for the
odd-coset L1 objective.

Therefore circuit augmentation cannot replace Graver/global augmentation in the
universal solver merely by adding exact line search.

## 4. Scope

This theorem does not say that every Graver direction is hard to find. It does
not rule out a polynomial symbolic algorithm that constructs a non-circuit
integer trade. It does not prove a lower bound for arbitrary representations.

It closes only:

```text
rational oriented-matroid circuits
+ exact integer line search
=> universal odd-coset L1 solver
```

The live target remains construction of a genuinely global improving integer
trade or a polynomial global-optimality certificate.

## 5. Ceiling

```text
KERNEL DIMENSION
= 2

ALL RATIONAL CIRCUIT DIRECTIONS
= 9 EXACTLY

EXACT LINE SEARCH FROM zc
= NO STRICT IMPROVEMENT ON ANY CIRCUIT

GLOBAL FEASIBLE IMPROVEMENT
= 30 -> 18

CIRCUIT-ONLY AUGMENTATION
= FALSIFIED

GRAVER / NON-CIRCUIT GLOBAL TRADE
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
