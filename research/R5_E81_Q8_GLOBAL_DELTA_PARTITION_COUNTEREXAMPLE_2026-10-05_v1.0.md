# R5 E81 — q=8 Counterexample to Static Global Delta Vertex Partition

Date: 2026-10-05

Status:
`STATIC_GLOBAL_DELTA_VERTEX_PARTITION_FALSIFIED_ON_SQUARE_CUBIC_LINEAR_RXC3_Q8`

Scientific ceiling:

```text
E81 FALSIFIES THE PARTICULAR UNIVERSAL DECOMPOSITION THEOREM TARGETED BY E77/E78:
A DISJOINT TANNER-VERTEX PARTITION INTO NONEMPTY EXACT DELTA-MATROID BOUNDARY MODULES
DOES NOT EXIST FOR EVERY RXC3 HARD-TARGET SOURCE.

E78'S CONDITIONAL EQUALITY-GLUING META-THEOREM REMAINS CORRECT.
ITS UNIVERSAL EXISTENCE PREMISE IS FALSE.

P_VS_NP = OPEN.
```

## 1. Why this experiment is decisive

E77 and E78 isolated the prospective theorem

```text
For every square-cubic-linear RXC3/E12 hard target, construct a Tanner-vertex
partition into exact boundary modules that are linear/projected-linear
Delta-matroids.
```

E78 then proved that such a represented partition would be sufficient for a
randomized polynomial Exact-One solver.

Until E81, all frozen complete controls happened to admit such partitions:

```text
q=6  : [1,1,10]
q=9  : [1,1,1,15]
q=10 : [1,1,1,17]
```

Those positive controls do not imply universal existence.  E81 tests the missing
existence implication directly on the cyclic q=8 member of the same
square-cubic-linear family.

## 2. q=8 source

Let source column `j` meet checks

```text
{j, j+1, j+3} mod 8.
```

Thus the source matrix is square `8 x 8`.  Direct replay verifies:

```text
* every row has weight 3;
* every column has weight 3;
* every two columns intersect in at most one row;
* therefore the Tanner graph is C4-free / source-linear;
* the Tanner graph is connected.
```

This is a valid square-cubic-linear RXC3 control, not a nonlinear exceptional
source.

## 3. Exhaustive connected-cluster catalogue

The Tanner graph has 16 vertices.  E81 enumerates all

```text
2^16 - 1 = 65,535
```

nonempty Tanner-vertex subsets.

Exactly

```text
18,043
```

induce connected clusters.

For every connected cluster, the checker constructs the **exact** projected
boundary relation under the same `ExactOne_3 / Equality_3` semantics as
E74–E80 and tests Bouchet symmetric exchange.

Exactly

```text
200
```

connected clusters have nonempty delta-matroid boundary support.

Their complete size distribution is

```text
size 1  :   8
size 12 :  48
size 13 : 120
size 14 :  24
```

There are no connected delta-support clusters of sizes 2 through 11, 15, or 16.

E79 reconstruction independently succeeds on every one of the 200 relations:

```text
200 / 200 are even binary.
```

So the obstruction is not failure of binary representability.  It is failure of
**coverability by disjoint delta modules**.

## 4. Exact nonexistence proof for a full partition

The eight size-one delta modules are exactly the eight **check vertices**.
Singleton variable vertices carry `Equality_3`, whose boundary relation is not a
delta-matroid.

Every nontrivial delta module has at least 12 vertices.

Therefore two disjoint nontrivial delta modules cannot occur in a partition of
16 Tanner vertices, because

```text
12 + 12 > 16.
```

Consequently, any full delta-module partition would have to consist of:

```text
one nontrivial delta module containing every variable vertex
+
some singleton check vertices.
```

But the exhaustive catalogue contains

```text
zero
```

delta-support clusters containing all eight variable vertices.

Hence such a partition cannot exist.

The checker also performs an independent exact-cover dynamic search over all 200
available delta-cluster masks and obtains

```text
FULL DELTA PARTITION EXISTS = FALSE.
```

Thus

```text
boxed:
THE CYCLIC q=8 SQUARE-CUBIC-LINEAR RXC3 TANNER GRAPH
HAS NO DISJOINT EXACT DELTA-MODULE VERTEX PARTITION.
```

## 5. Why restricting the catalogue to connected modules is without loss

Suppose a proposed module is disconnected in the induced Tanner graph, with
connected components `K_1,...,K_r`.  Local constraints do not couple different
components, and their boundary grounds are disjoint.  Therefore its exact
boundary relation is the direct product/direct sum of the exact component
relations.

If this disconnected relation were a nonempty delta-matroid, fixing a feasible
boundary state on all components except `K_i` and deleting/contracting those
coordinates recovers the exact relation of `K_i` as a delta-matroid minor.
Hence every connected component would itself have to be a delta-matroid module.

So any disconnected delta module can be refined into connected delta modules.
Therefore failure of a partition using the complete connected catalogue implies
failure of **every** disjoint Tanner-vertex delta partition.

## 6. What exactly is falsified

Falsified:

```text
STATIC GLOBAL DELTA-DECOMPOSITION THEOREM

Every RXC3 hard target admits a disjoint Tanner-vertex partition whose exact
projected boundary relations are delta-matroids (hence, on the frozen controls,
linear/binary delta-matroids).
```

A fortiori, the stronger statement requiring all pieces to be linear or
projected-linear is false in this static-partition form.

Not falsified:

```text
* E78 equality-gluing identity for a partition when such a partition exists;
* recursive decompositions whose intermediate modules overlap or are obtained
  after contractions/projections rather than from one static vertex partition;
* branch/parse decompositions with algebraic state compression;
* elimination schemes that temporarily use non-delta local pieces but produce
  represented delta interfaces after composition;
* a completely different polynomial Exact-One algorithm.
```

## 7. Consequence for the P vs NP route

E81 is an anti-overclaim result.  The route

```text
arbitrary RXC3
 -> find static disjoint delta partition
 -> E78 delta-sum
 -> polynomial solver
```

cannot be the universal proof because its first implication is false.

This does **not** establish any lower bound for Exact-One, SAT, NP, or P vs NP.
It only closes this particular decomposition conjecture.

## 8. Correct next frontier

The decomposition object has to be generalized.

The next admissible target is not another static partition conjecture, but a
**recursive represented elimination/decomposition** in which one may:

```text
1. combine adjacent regions before requiring a delta interface;
2. contract/project internal boundary coordinates;
3. allow overlapping bags / branch-decomposition style separators;
4. maintain a polynomial-size represented state even though primitive
   Equality_3 regions are not themselves delta-matroids.
```

The q=8 instance is now the mandatory regression target: any proposed global
construction must succeed on it without silently assuming a static delta
partition.

A useful killer-test for the next construction is therefore:

```text
Can the q=8 counterexample be solved by a recursive sequence of local
composition + projection steps whose INTERMEDIATE represented interfaces remain
linear/projected-linear and polynomially bounded?
```

If not, the exterior/delta route needs a deeper pivot.

## 9. Companion checker

```text
experiments/r5_e81_q8_global_delta_partition_counterexample.py
```

Frozen assertions:

```text
all nonempty subsets             = 65,535
connected subsets                = 18,043
connected delta-support clusters = 200
by size                           = {1:8,12:48,13:120,14:24}
all delta relations binary-even  = yes
all-variable delta module        = none
full disjoint delta partition    = false
```

Scientific status:

```text
E81 = PROVED FINITE COUNTEREXAMPLE TO STATIC GLOBAL DELTA VERTEX PARTITION.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED.
RECURSIVE/OVERLAPPING REPRESENTED DECOMPOSITION = OPEN.
UNIVERSAL POLYNOMIAL EXACT_ONE SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
```
