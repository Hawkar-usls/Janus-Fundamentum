# R5 E9 — Kernel-Tope Greedy Local-Minimum Barrier

Date: 2026-09-28

Status: `JANUS_EXACT_GREEDY_DEPTH_DESCENT_FALSIFIER__PG15_SAT_R11__PARALLEL_CLASS_REPAIRED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_kernel_tope_greedy_local_minimum_barrier.py`

Scientific ceiling:

```text
THE SOURCE-KERNEL DEPTH QUOTIENT IS EXACT,
BUT GREEDY DESCENT BY ADJACENT ARRANGEMENT CHAMBERS IS NOT.

A FROZEN SAT CONTROL HAS A STRICTLY NON-GLOBAL GEOMETRIC LOCAL MINIMUM.

PARALLEL / COINCIDENT KERNEL HYPERPLANES ARE HANDLED EXPLICITLY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup and adjacency convention

For a cubic square Exact-One source `A`, choose a rational kernel basis

```text
B in Q^{n x d},
ker_Q(A) = { B alpha : alpha in Q^d }.
```

Every full-support kernel vector gives a chamber sign vector

```text
t(alpha)_i = sign((B alpha)_i) in {-,+}.
```

Let

```text
p(t) = # positive coordinates of t.
```

The depth theorem gives

```text
p(t) >= n/3
```

for every source-valid full-support kernel chamber, and

```text
A SAT iff some chamber has p(t)=n/3.
```

Important degeneracy rule: if several rows of `B` are proportional, they define the same geometric hyperplane. Crossing that hyperplane may flip the signs of the entire projective row class at once. Therefore geometric chamber adjacency is by one **projective hyperplane class**, not necessarily one raw coordinate.

The greedy candidate tested here is the correct geometric one:

```text
while an adjacent arrangement chamber has smaller p:
    move to it.
```

The theorem below falsifies this shortcut exactly.

## 2. Frozen positive control

Use the frozen SAT control `PG15_SAT_R11`, with source rows

```text
(1,2,3)
(1,10,11)
(1,12,13)
(2,9,11)
(2,12,14)
(3,4,7)
(3,5,6)
(4,9,13)
(4,10,14)
(5,8,13)
(5,10,15)
(6,8,14)
(6,9,15)
(7,8,15)
(7,11,12)
```

It has

```text
rank_Q(A)=11,
nullity_Q(A)=4.
```

One exact integer kernel basis is given by the columns of

```text
B =
[-1 -1  0  0]
[-1  0 -1  0]
[ 2  1  1  0]
[-1 -1 -1  1]
[-1 -1  0  0]
[-1  0 -1  0]
[-1  0  0 -1]
[ 1  0  0  0]
[ 1  0  1 -1]
[ 1  1  0 -1]
[ 0  0  0  1]
[ 1  0  0  0]
[ 0  1  0  0]
[ 0  0  1  0]
[ 0  0  0  1].
```

The non-singleton projective row classes are

```text
{1,5}, {2,6}, {8,12}, {11,15}
```

in 1-based indexing. Every other row is a singleton class.

## 3. A non-global chamber

Take

```text
alpha = (-7, 8, 8, -8)^T.
```

Then

```text
y = B alpha
  = (-1,-1,2,-17,-1,-1,15,-7,9,9,-8,-7,8,8,-8)^T.
```

Hence

```text
t = --+---+-++--++-
```

with positive coordinates

```text
{3,7,9,10,13,14}
```

and therefore

```text
p(t)=6.
```

All six positive coordinates belong to singleton projective hyperplane classes. The four non-singleton projective classes listed above are entirely negative in `t`.

Since `n=15`, the exact SAT boundary is `n/3=5`.

## 4. Exact blocking certificates for every potentially improving adjacent class

Write `b_i` for row `i` of `B`. For a desired sign vector `s`, define the signed normal

```text
c_i = s_i b_i.
```

If

```text
lambda_1 c_i1 + ... + lambda_r c_ir = 0,
lambda_j > 0,
```

then no `alpha` can realize all desired strict signs.

Because every positive projective class of `t` is a singleton, an adjacent chamber can lower `p` only by crossing one of the six singleton hyperplanes at coordinates

```text
3,7,9,10,13,14.
```

For each such attempted flip, the following exact positive dependence blocks the chamber:

```text
flip 3:   c_1 + c_2 + c_3 = 0
flip 7:   c_7 + c_8 + c_11 = 0
flip 9:   c_2 + c_9 + c_11 = 0
flip 10:  c_1 + c_10 + c_11 = 0
flip 13:  c_1 + c_8 + c_13 = 0
flip 14:  c_2 + c_8 + c_14 = 0
```

All coefficients are exactly `+1`.

Crossing any of the four non-singleton projective classes flips only negative coordinates of `t` to positive coordinates and therefore strictly increases `p`.

Thus **every geometrically adjacent chamber has larger `p`**, while every potentially decreasing adjacent class is infeasible.

Therefore `t` is a genuine strict local minimum of `p` in the actual arrangement chamber graph.

## 5. It is strictly non-global

The same source is SAT. For example, the 1-based set

```text
S={1,5,7,9,14}
```

satisfies `Ax=1`.

Then

```text
y*=3x-1
```

lies in `ker_Q(A)`, has full support, and has exactly five positive coordinates. Hence

```text
h(A)=5
```

while the local trap has `p(t)=6`.

So this is a strict non-global geometric local minimum on a frozen SAT instance.

## 6. Defect interpretation

For every full-support kernel chamber of a cubic source,

```text
#(++- source rows)=3p-n.
```

The trap therefore has

```text
3*6-15=3
```

`++-` defects, whereas the SAT boundary has defect zero.

An improving move from `p=6` to `p=5` must remove all three defects net. No adjacent projective hyperplane crossing can do so.

## 7. Distance audit

Exact chamber enumeration of this rank-4 arrangement gives the following distinction:

```text
minimum raw Hamming distance from the trap to a p=5 chamber = 5,
minimum geometric chamber-graph distance to a p=5 chamber = 4.
```

The values differ because coincident/projectively parallel kernel rows can flip together in one geometric crossing.

Therefore future augmentation claims must state which distance they use. The scientific route should use geometric chamber-graph distance or explicitly quotient proportional kernel rows first.

## 8. Consequence

The following implication is false:

```text
SOURCE DEPTH FLOOR = n/3
AND SAT BOUNDARY EXISTS
=> EVERY NONBOUNDARY CHAMBER HAS AN ADJACENT LOWER-p CHAMBER.
```

So the universal algorithm

```text
pick any rational-kernel chamber
repeat a p-decreasing adjacent chamber move
accept iff p=n/3
```

is falsified.

## 9. What remains open

This barrier does not rule out:

- bounded-radius geometric augmentation;
- nonlocal pivot / augmenting-path rules;
- globally optimized chamber search using source triple structure;
- closure-enhanced kernel arrangements that remove traps;
- potentials stronger than raw `p` or raw defect count;
- decomposition of the projective kernel arrangement.

The next live question is:

```text
is there a polynomially bounded source-specific augmentation rule that escapes
every nonboundary local minimum and strictly lowers p?
```

Any candidate must survive this PG15 trap, the singular UNSAT controls, and the high-nullity exact source families.

## 10. Prior-art interaction

General halfspace-depth / densest-hemisphere optimization in variable dimension is not a generic polynomial donor. The source-specific `1/3` floor remains the useful theorem; this result shows that ordinary chamber adjacency does not exploit it strongly enough.

No literature-novelty claim is made for arbitrary arrangement local minima. The JANUS contribution claimed here is only the exact source-bound falsifier and its certificates.

## 11. Ceiling

```text
PG15_SAT_R11 GLOBAL DEPTH
= 5/15 = 1/3

EXPLICIT SOURCE-KERNEL CHAMBER
= --+---+-++--++-

ITS POSITIVE COUNT
= 6

ALL GEOMETRICALLY ADJACENT LOWER-p MOVES
= BLOCKED EXACTLY

NON-SINGLETON PARALLEL CLASSES
= ALL NEGATIVE AT THE TRAP; CROSSING THEM INCREASES p

STRICT NON-GLOBAL GEOMETRIC LOCAL MINIMUM
= PROVED

MIN HAMMING DISTANCE TO BOUNDARY
= 5

MIN CHAMBER-GRAPH DISTANCE TO BOUNDARY
= 4

NAIVE ADJACENT-CHAMBER GREEDY DESCENT
= FALSIFIED

BOUNDED-RADIUS / NONLOCAL AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```