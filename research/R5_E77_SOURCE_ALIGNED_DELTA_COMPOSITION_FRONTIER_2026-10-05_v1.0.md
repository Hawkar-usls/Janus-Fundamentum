# R5 E77 — Source-Aligned Linear-Delta Composition Frontier

Date: 2026-10-05

Status:
`SOURCE_ALIGNED_LINEAR_DELTA_CLUSTERS_EXIST__E53_LIFT_PRESERVES_LINEAR_DELTA_PRODUCT__FULL_CONTROL_PARTITIONS_REQUIRE_NEAR_GLOBAL_PIECES`

Scientific ceiling:

```text
E77 DOES NOT CONSTRUCT A UNIVERSAL POLYNOMIAL SOLVER.

IT TURNS THE E76 EXTERIOR/MATCHING ESCAPE INTO A SOURCE-ALIGNED OBJECT ON THE
RXC3 QUOTIENT AND IDENTIFIES THE NEXT NECESSARY THEOREM: A POLYNOMIAL-TIME
GLOBAL DELTA-DECOMPOSITION WITH POLYNOMIALLY CONSTRUCTIBLE REPRESENTATIONS.

P_VS_NP = OPEN.
```

## 1. Why E77 is different from E76

E74 showed that the primitive Equality_3 star and the complete one-gadget E53
quotient are non-delta. E75 extended this obstruction to every connected C4-free
Tanner cluster through nine vertices. E76 then produced an explicit 13-vertex
C4-free cluster whose projected boundary support is a genuine linear even
delta-matroid.

The remaining concern was source alignment: the E76 motif does not occur as an
induced cluster in the frozen E12 `N=102` target, so it cannot simply be tiled
across the hard image.

E77 therefore moves the search to the quotient that E53 proves exact. We study
connected Tanner clusters of the RXC3 source relation itself, where check
vertices carry ExactOne_3 and variable vertices carry Equality_3. Any useful
source relation can then be lifted through the exact E53 gadget quotient.

## 2. External composition machinery

Koana and Wahlström prove that linear delta-matroids are closed under union and
under delta-sum, and that a representation of the result can be constructed in
randomized `O(n^omega)` field operations:

* Tomohiro Koana and Magnus Wahlström,
  "Faster Algorithms on Linear Delta-Matroids",
  STACS 2025, LIPIcs 327, Article 62,
  DOI `10.4230/LIPIcs.STACS.2025.62`.

For set systems on a common ground set, delta-sum has feasible family

```text
{F1 xor F2 : F1 in F1, F2 in F2}.
```

This is exactly the algebraic operation naturally suggested by gluing Boolean
boundary states: equal memberships on a shared edge cancel in symmetric
difference. Thus a decomposition into explicitly represented linear-delta
boundary modules would be algorithmically meaningful rather than merely a
classification exercise.

E77 does not yet prove that an arbitrary hard target admits such a decomposition
or that it can be found efficiently. Those are the missing global statements.

## 3. Frozen RXC3 q=6 exhaustive quotient scan

Use the frozen E17/E53 source triples

```text
(0,1,3)
(1,2,4)
(2,3,5)
(0,3,4)
(1,4,5)
(0,2,5).
```

The source Tanner graph has 12 vertices. The E77 checker exhausts all `2^12`
vertex subsets, keeps connected induced clusters, computes their exact projected
boundary support, and tests Bouchet symmetric exchange.

Exactly 99 connected clusters have delta-matroid support, distributed by cluster
size as

```text
size 1  : 6
size 7  : 6
size 8  : 21
size 9  : 30
size 10 : 36.
```

There are no connected delta-support clusters of sizes 2 through 6, 11, or 12
(the full source is UNSAT and hence has empty closed support).

### 3.1 First nontrivial source-aligned cluster

A canonical size-seven cluster uses source checks

```text
{0,1,4}
```

and source variables

```text
{0,1,3,4}.
```

It has eight internal Tanner edges, five boundary stubs, and exact boundary
family

```text
boxed:
F = {5,17}.
```

Twisting by feasible set 5 gives

```text
F * 5 = {0,20}.
```

Since `20` has exactly two active coordinates, this is represented by a single
2x2 skew-symmetric block embedded in the five boundary coordinates. Therefore
this is a genuine linear even delta-matroid.

This is the first positive **source-aligned** exterior object in the R5 hard
route.

## 4. Exact lift through E53

E53 proves that each E12 gadget has two independent Boolean quotient bits

```text
a = common state on its three unprimed ports,
b = common state on its three primed ports,
```

and every pair `(a,b)` is locally realizable.

Therefore if a source cluster has exact support `F` in one copy, taking the same
source cluster in both unprimed and primed quotient copies gives boundary support

```text
F x F.
```

For the canonical q=6 cluster above, twisting `F x F` by `(5,5)` leaves the
principal-nonsingularity family of two disjoint 2x2 skew blocks. The checker
constructs this representation explicitly.

Thus E77 is not merely finding a delta relation in an auxiliary source graph:
it supplies an exact linear-even representation for the corresponding paired
E12 quotient boundary relation.

## 5. Linear q=9 control

To prevent the positive result from depending only on source C4s, E77 also uses
the connected square-cubic-linear source

```text
(0,5,8)
(0,1,4)
(1,2,3)
(0,3,7)
(4,7,8)
(1,5,6)
(2,4,6)
(2,5,7)
(3,6,8).
```

Its Tanner graph has 18 vertices and is C4-free. The checker exhausts all
`2^18=262144` vertex subsets.

Exactly 412 connected clusters have delta support:

```text
size 1  : 9
size 12 : 2
size 13 : 36
size 14 : 99
size 15 : 148
size 16 : 99
size 17 : 18
size 18 : 1.
```

The family-size refinement is

```text
(size 1,  family 3): 9
(size 12, family 1): 2
(size 13, family 1): 36
(size 14, family 1): 93
(size 14, family 2): 6
(size 15, family 1): 136
(size 15, family 2): 12
(size 16, family 1): 93
(size 16, family 2): 6
(size 17, family 1): 18
(size 18, family 1): 1.
```

Hence the first nontrivial connected delta boundary beyond singleton ExactOne
checks appears at size 14. There are six such clusters. Every one has exactly two
feasible boundary sets whose symmetric difference has size two, so after twisting
by either feasible set it is exactly one embedded 2x2 skew block.

Thus source-aligned linear-delta cancellation is not restricted to non-linear
source Tanner graphs, but on this C4-free control it emerges only at a much larger
scale.

## 6. Full delta-cluster partition stress test

A single positive cluster is not enough. E77 therefore solves exactly the
following finite optimization problem on both controls:

```text
partition all Tanner vertices into disjoint connected clusters
whose exact boundary supports are delta-matroids,
minimizing the largest cluster size.
```

For frozen q=6:

```text
boxed:
minimum maximum piece size = 10 out of 12 vertices.
```

An optimal partition has piece sizes

```text
1,1,10.
```

The size-ten piece has a singleton boundary family.

For linear q=9:

```text
boxed:
minimum maximum piece size = 15 out of 18 vertices.
```

An optimal partition has piece sizes

```text
1,1,1,15.
```

Again the large piece has singleton boundary support.

So the first complete delta decompositions of these quotient controls are
**near-global**. This is the key anti-overclaim: the existence of useful local
linear-delta clusters does not yet provide a bounded-radius or sublinear-width
universal decomposition.

## 7. What is genuinely new after E77

The exterior/matching route is no longer purely negative:

```text
E74/E75:
    primitive and all <=9 C4-free clusters are non-delta.

E76:
    one explicit 13-vertex C4-free linear-delta boundary cluster exists.

E77:
    exact source-aligned linear-delta clusters exist on the RXC3 quotient;
    E53 lifts them exactly into paired E12 quotient relations;
    linear-source controls also contain such clusters.
```

At the same time, the exhaustive partition stress tests isolate the actual
missing theorem:

```text
GLOBAL DELTA-DECOMPOSITION THEOREM

For every E12 hard target, construct in polynomial time a decomposition into
modules whose exact projected boundary relations have polynomial-size
linear/projected-linear delta-matroid representations, and whose composition
can be carried out in polynomial total time.
```

A proof of this statement would be a serious candidate route to the desired
universal polynomial solver. E77 does not prove it.

## 8. Replay

Companion checker:

```text
experiments/r5_e77_source_aligned_delta_composition_frontier.py
```

It independently verifies:

```text
* all 4095 q=6 source Tanner subsets;
* the exact count 99 and size distribution;
* F={5,17} and its one-skew-block representation;
* the paired E53 lift F x F and its two-skew-block representation;
* all 262143 q=9 source Tanner subsets;
* the exact count 412 and family-size distribution;
* the six first nontrivial size-14 linear-even relations;
* exact minimum-max full delta partitions 10/12 and 15/18.
```

Scientific status:

```text
E77 = PROVED POSITIVE SOURCE-ALIGNED LINEAR-DELTA FRONTIER.
GLOBAL_POLYNOMIAL_DELTA_DECOMPOSITION = OPEN.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```
