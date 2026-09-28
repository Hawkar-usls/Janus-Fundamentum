# R5 E9 — Kernel-Tope Greedy Local-Minimum Barrier

Date: 2026-09-28

Status: `JANUS_EXACT_GREEDY_DEPTH_DESCENT_FALSIFIER__PG15_SAT_R11__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_kernel_tope_greedy_local_minimum_barrier.py`

Scientific ceiling:

```text
THE SOURCE-KERNEL DEPTH QUOTIENT IS EXACT,
BUT SINGLE-COORDINATE GREEDY DESCENT ON THE TOPE GRAPH IS NOT.

A FROZEN SAT CONTROL HAS A STRICTLY NON-GLOBAL LOCAL MINIMUM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

For a cubic square Exact-One source `A`, choose a rational kernel basis

```text
B in Q^{n x d},
ker_Q(A) = { B alpha : alpha in Q^d }.
```

Every full-support kernel vector gives a tope sign vector

```text
t(alpha)_i = sign((B alpha)_i) in {-,+}.
```

Let

```text
p(t) = # positive coordinates of t.
```

The already-proved depth theorem gives

```text
p(t) >= n/3
```

for every source-valid full-support kernel tope, and

```text
A SAT iff some tope has p(t)=n/3.
```

Because the tope graph of a realizable oriented matroid connects chambers that differ in one sign coordinate, the most natural greedy candidate is:

```text
while an adjacent tope has smaller p:
    move to it.
```

If every local minimum were global, this would be a potentially powerful route to the exact `n/3` boundary.

The theorem below kills that shortcut exactly.

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

The checker verifies `AB=0` and linear independence of the four columns.

## 3. A non-global local minimum

Take

```text
alpha = (-7, 8, 8, -8)^T.
```

Then

```text
y = B alpha
  = (-1,-1,2,-17,-1,-1,15,-7,9,9,-8,-7,8,8,-8)^T.
```

Hence the tope is

```text
t = --+---+-++--++-
```

with positive coordinates

```text
{3,7,9,10,13,14}
```

in 1-based indexing, so

```text
p(t)=6.
```

Since `n=15`, the exact SAT boundary is

```text
n/3=5.
```

Thus this chamber is not globally optimal if the instance is SAT. We now prove it is nevertheless a local minimum under every single improving sign flip.

## 4. Exact no-improving-neighbor certificates

Write `b_i` for row `i` of `B`. For a desired sign vector `s in {-,+}^15`, define the signed normal

```text
c_i = s_i b_i.
```

A chamber with sign vector `s` exists iff there is some `alpha` with

```text
c_i dot alpha > 0
```

for all `i`.

If a subset of signed normals has a positive dependence

```text
lambda_1 c_i1 + ... + lambda_r c_ir = 0,
lambda_j > 0,
```

then such an `alpha` cannot exist, because dotting with `alpha` would give a strictly positive sum equal to zero.

For each positive coordinate of `t`, flip only that coordinate from `+` to `-` and keep all other signs fixed. The following exact three-term positive dependences certify that every such proposed improving neighbor is infeasible.

Indices below are 1-based.

```text
flip 3:
    c_1 + c_2 + c_3 = 0

flip 7:
    c_7 + c_8 + c_11 = 0

flip 9:
    c_2 + c_9 + c_11 = 0

flip 10:
    c_1 + c_10 + c_11 = 0

flip 13:
    c_1 + c_8 + c_13 = 0

flip 14:
    c_2 + c_8 + c_14 = 0
```

All coefficients are exactly `+1`.

Therefore no tope differing from `t` in exactly one positive coordinate has `p=5`.

So `t` is a genuine local minimum of `p` in the tope graph.

## 5. It is strictly non-global

The same frozen source has exact Boolean witnesses; for example

```text
S={1,5,7,9,14}
```

in 1-based indexing satisfies `Ax=1`.

Then

```text
y*=3x-1
```

lies in `ker_Q(A)`, has full support, and has exactly five positive coordinates.

Hence

```text
h(A)=5
```

while the local-minimum chamber above has

```text
p(t)=6.
```

This is a strict non-global local minimum on a SAT instance.

## 6. Defect interpretation

For any full-support kernel tope of a cubic source,

```text
#(++- source rows)=3p-n.
```

Therefore the local trap has

```text
3*6-15=3
```

unavoidable `++-` rows in that chamber, while the global SAT boundary has defect zero.

An improving adjacent chamber would have to reduce `p` by one and therefore remove exactly three defects at once. The six positive coordinates of the trap all fail that coordinated three-defect cancellation condition.

So the obstruction is not merely graph-theoretic: it is source-semantic.

## 7. Consequence

The following implication is false even on the frozen positive control:

```text
SOURCE DEPTH FLOOR = n/3
AND SAT BOUNDARY EXISTS
=> EVERY NONBOUNDARY TOPE HAS AN ADJACENT LOWER-p TOPE.
```

Therefore this algorithm is forbidden as a universal proof route:

```text
pick any rational-kernel chamber
repeat a single-coordinate p-decreasing chamber flip
until no improvement
accept iff p=n/3.
```

It can stop at `p=6` although the same instance has `p=5` witnesses.

## 8. What remains open

This barrier kills only naive one-edge greedy descent. It does not rule out:

- bounded-radius multi-flip augmentation;
- nonlocal pivot rules;
- globally optimized tope search using source structure;
- closure-enhanced kernel arrangements where exact constraints remove traps;
- a potential different from raw `p` or raw defect count;
- polynomial decomposition of the arrangement induced by source triples.

The next admissible descent question is therefore not `is there always an improving neighbor?`, but:

```text
is there a polynomially bounded augmentation radius / source-local exchange
that escapes every nonboundary local minimum?
```

Any such claim must survive this PG15 trap and the frozen singular UNSAT controls.

## 9. Prior-art interaction

General halfspace-depth / densest-hemisphere optimization in variable dimension is not a generic polynomial donor. The source-specific `1/3` floor remains the useful theorem; the present result shows that local chamber adjacency alone does not exploit it strongly enough.

No literature novelty claim is made for the existence of local traps in arbitrary arrangements. The scientific content here is the exact binding of such a trap to the frozen cubic Exact-One source geometry and its rational kernel quotient.

## 10. Ceiling

```text
PG15_SAT_R11 GLOBAL DEPTH
= 5/15 = 1/3

EXPLICIT SOURCE-KERNEL TOPE
= --+---+-++--++-

ITS POSITIVE COUNT
= 6

SINGLE-FLIP IMPROVING NEIGHBORS
= 0, EXACT POSITIVE-DEPENDENCE CERTIFICATES

NON-GLOBAL LOCAL MINIMUM
= PROVED

NAIVE TOPE-GREEDY DESCENT
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