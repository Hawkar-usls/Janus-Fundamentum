# R5 E9 — Rank-One AND Relation Delta-Matroid Local Barrier

Date: 2026-09-23

Authority:
`DERIVED_FINITE_LOCAL_BARRIER__DIRECT_DELTA_MATROID_ROUTE_ONLY__NO_D1_PROMOTION`

Parents:

- `R5_E9_NONLOCAL_RANK1_JOINT_CONTRACTION_PIVOT_GATE_V1`
- `R5_B1B1C5B2B2_E8_6I_RANK1_POLY_DEFECT_BASIS_PASS_R2_SHIFT_2026-09-23_v1.0.md`
- `JANUS_KEYMASTER_DIRECT_DELTA_MATROID_OCCURRENCE_SPLIT_BARRIER_2026-09-23_v1.0`

Checker:

`research/tools/r5_e9_rank1_and_delta_matroid_local_barrier_checker.py`

## 1. Local rank-one defect relation

One multiplicative rank-one identity is

```text
p = x y
```

over Boolean values.

Its graph is

```text
R_AND
=
{000,010,100,111}.
```

Identify a tuple with the subset of coordinates set to one on ground set

```text
E={x,y,p}.
```

The feasible family is

```text
F
=
{
  empty,
  {y},
  {x},
  {x,y,p}
}.
```

## 2. Symmetric-exchange failure

A delta-matroid must satisfy the symmetric exchange axiom:

for all feasible `X,Y` and every `e in X triangle Y`, there exists
`f in X triangle Y` such that

```text
X triangle {e,f}
```

is feasible.

Take

```text
X = empty
Y = {x,y,p}
e = p.
```

The only possible exchanges produce

```text
{p},
{x,p},
{y,p}.
```

None is feasible.

Therefore:

```text
R_AND
IS NOT A DELTA-MATROID RELATION.
```

The checker exhaustively verifies the failure.

## 3. Twist cannot repair it directly

Delta-matroid status is preserved under twisting.

Hence if any twist of `R_AND` were a delta-matroid, twisting back would make
`R_AND` a delta-matroid, contradiction.

The checker also enumerates all eight twists directly and confirms that every
one fails symmetric exchange.

Thus:

```text
DIRECT TWIST NORMALIZATION
OF RANK-ONE AND DEFECT
TO A DELTA-MATROID
=
IMPOSSIBLE.
```

## 4. Source donor context

Kazda, Kolmogorov and Rolínek prove a polynomial algorithm for Boolean edge CSP
when every constraint relation is an even delta-matroid; the algorithm uses
augmentations and contractions.

Geelen, Iwata and Murota give polynomial algorithms for linear delta-matroid
parity.

Recent linear-delta-matroid work gives efficient contraction representations
and polynomial algorithms for several linear/projection operations.

These remain valuable **methodological contraction donors**.

But the current FULL product defect `p=xy` does not satisfy the local
delta-matroid hypothesis itself.

## 5. Consequence

The following route is blocked:

```text
take current FULL rank-one defects
as delta-matroid constraints
+
apply existing delta-matroid
augmentation/contraction algorithm directly.
```

This is independent of occurrence-coherence issues from the earlier direct
three-sheet delta-matroid barrier.

The obstruction now occurs already in one local rank-one defect.

## 6. Scope firewall

Blocked:

- direct local identification of `p=xy` with a delta-matroid constraint;
- any pure twist of that three-coordinate relation;
- direct invocation of even/linear delta-matroid edge-CSP solvers on the
  unchanged rank-one defect language.

Still open:

- an extended gadget whose **projected** behavior is `p=xy` while the larger
  relation lies in a tractable delta-matroid class;
- a nonlocal grouped representation of many product defects as one linear
  delta-matroid object;
- blossom-style contraction used only as a pattern donor;
- a hybrid quotient whose correctness does not require each local AND graph to
  be a delta-matroid.

## 7. Ceiling

```text
RANK1 LOCAL AND RELATION
=
NOT DELTA-MATROID

ALL DIRECT TWISTS
=
NOT DELTA-MATROID

DIRECT DELTA-MATROID SOLVER TRANSFER
=
BLOCKED

REPRESENTATION-CHANGING
NONLOCAL CONTRACTION
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
