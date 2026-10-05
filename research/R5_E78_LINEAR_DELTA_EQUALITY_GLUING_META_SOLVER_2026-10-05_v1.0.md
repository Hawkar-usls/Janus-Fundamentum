# R5 E78 — Linear-Delta Equality-Gluing Meta-Solver

Date: 2026-10-05

Status:
`EXACT_TANNER_MODULE_GLUING_IS_ITERATED_DELTA_SUM__REPRESENTED_LINEAR_DELTA_DECOMPOSITION_IS_A_SUFFICIENT_RANDOMIZED_POLYNOMIAL_SOLVER_CRITERION`

Scientific ceiling:

```text
E78 IS A CONDITIONAL POLYNOMIAL SOLVER THEOREM.

IT DOES NOT PROVE THAT EVERY E12 HARD TARGET HAS A POLYNOMIALLY CONSTRUCTIBLE
LINEAR-DELTA MODULE DECOMPOSITION.

THAT DECOMPOSITION THEOREM IS NOW THE SINGLE MISSING IMPLICATION ON THIS ROUTE.

P_VS_NP = OPEN.
```

## 1. Starting point

E73 localized the hard local atom to

```text
ExactOne_3 on check vertices,
Equality_3 on variable vertices.
```

E74/E75 showed that primitive and small C4-free boundary modules are generally
non-delta. E76 produced a genuine nontrivial linear even delta boundary module.
E77 then found source-aligned linear-delta modules on the RXC3 quotient and
showed that the exact E53 quotient lifts them into the E12 route.

What E77 did not yet prove was that composing represented linear-delta boundary
modules actually solves the original Boolean gluing problem in polynomial time.
E78 supplies that missing meta-lemma.

## 2. Exact module semantics

Let the Tanner graph vertices be partitioned into disjoint modules

```text
M_1,...,M_s.
```

For each module `M_t`, let

```text
E_t
```

be the incidence edges crossing from `M_t` to another module.  Let

```text
D_t=(E_t,F_t)
```

be the **exact projected boundary relation**: `F in F_t` iff the local
ExactOne_3 / Equality_3 constraints inside `M_t` admit an extension whose
selected crossing edges are exactly `F`.

Because Tanner vertices are partitioned, every cut incidence edge belongs to
exactly two boundary grounds: one at each endpoint module.

A tuple

```text
F_1 in F_1,...,F_s in F_s
```

is globally consistent iff the two modules incident with every cut edge assign
the same Boolean value to that edge.

## 3. Equality gluing equals symmetric-difference cancellation

Consider one cut edge `e`.  It appears in exactly two sets among

```text
F_1,...,F_s.
```

The two local boundary bits agree iff either both contain `e` or both omit it.
That is equivalent to `e` occurring an even number of times, hence to

```text
e notin F_1 xor F_2 xor ... xor F_s.
```

Applying this simultaneously to every cut edge gives the exact identity

```text
boxed:
(F_1,...,F_s) is globally consistent
iff
F_1 xor ... xor F_s = empty.
```

Therefore, after loop-extending each module relation to the common cut-edge
ground set,

```text
boxed:
GLOBAL EXACT-ONE SAT
iff
empty is feasible in D_1 delta D_2 delta ... delta D_s.
```

Here `delta` is delta-sum: its feasible sets are all symmetric differences of
feasible sets of the operands.

For partial two-module gluing with a shared interface `I` and external grounds
`U,V`, the same statement may be written as

```text
Glue(F1,F2)
 = { H - I : H in F1 delta F2, H cap I = empty }.
```

So ordinary equality of shared Boolean boundary bits is exactly delta-sum plus
zero restriction on the glued coordinates.

## 4. Algorithmic closure theorem from the literature

Koana and Wahlström prove that the union and delta-sum of linear delta-matroids
are again linear delta-matroids and that a representation of the result can be
constructed in randomized `O(n^omega)` field operations (with the standard
field-size/error-probability qualification):

* Tomohiro Koana and Magnus Wahlström,
  "Faster Algorithms on Linear Delta-Matroids",
  STACS 2025, LIPIcs 327, Article 62,
  DOI `10.4230/LIPIcs.STACS.2025.62`.

Their contraction representation also gives polynomial-time matrix algorithms
for fundamental optimization/feasibility operations on represented linear and
projected-linear delta-matroids.

Thus the E78 Boolean gluing identity combines with a genuine polynomial
representation closure theorem; this is not merely a semantic analogy.

## 5. Conditional polynomial meta-solver theorem

Suppose that, for every input square-cubic-linear carrier `A`, a procedure can
construct in polynomial time a Tanner-vertex partition

```text
M_1,...,M_s
```

such that:

```text
1. the exact projected boundary relation D_t of every module is a linear
   delta-matroid;

2. a linear representation of every D_t is produced in polynomial total time
   and polynomial total size;

3. all representations use a compatible field, or are converted to one with
   polynomial overhead under the applicable representation theorem.
```

Then Exact-One is decidable by:

```text
* loop-extend every D_t to the common cut-edge ground;
* iteratively construct D = D_1 delta ... delta D_s;
* test whether empty is feasible in D.
```

The cut ground has at most the number of Tanner edges, namely `3n`.  The number
of modules is at most `2n`.  Repeated randomized `O(N^omega)` representation
operations therefore give polynomial total running time under the three
assumptions above.

Hence

```text
boxed:
POLYNOMIALLY CONSTRUCTIBLE REPRESENTED LINEAR-DELTA DECOMPOSITION
    =>
RANDOMIZED POLYNOMIAL EXACT-ONE SOLVER.
```

This implication is universal for the carrier class.  The unproved premise is
exactly the new frontier.

E78 does **not** infer `P=NP` from the conditional theorem.

## 6. Replay on the E77 q=6 UNSAT partition

The frozen q=6 RXC3 quotient has an E77 optimal delta-support vertex partition
with piece sizes

```text
1,1,10.
```

E78 relabels every projected boundary relation by the actual global Tanner edge
`(check,variable)`.  Every cut edge appears in exactly two module boundary
grounds.

The checker enumerates the product of the three exact boundary relations and
requires agreement on every cut edge.  It finds

```text
compatible boundary tuples = 0.
```

Independently, direct Exact-One enumeration of the q=6 source gives zero
solutions.

Equivalently,

```text
empty is NOT feasible in the iterated set-system delta-sum.
```

So the gluing criterion returns UNSAT exactly.

## 7. Replay on the linear q=9 SAT partition

The connected square-cubic-linear q=9 control has the E77 optimal partition

```text
1,1,1,15.
```

Again every cut edge has exactly two boundary copies.  Exact relation-product
enumeration gives

```text
compatible boundary tuples = 1.
```

Direct Exact-One enumeration independently gives exactly one solution, with
selected source columns

```text
{1,7,8}.
```

The induced boundary tuple is the unique compatible tuple, and

```text
empty IS feasible in the iterated set-system delta-sum.
```

Thus the meta-solver identity agrees with the original Boolean problem on both
an UNSAT and a SAT source-aligned control.

## 8. What E78 changes

Before E78, the exterior route still had two logically separate gaps:

```text
A. useful linear-delta modules might exist;
B. even if they exist, perhaps their gluing leaves the tractable class.
```

E76/E77 answer A positively on concrete source-aligned controls.
Koana-Wahlström closure plus the E78 cancellation identity answers B:
represented linear-delta modules can be composed by a polynomial algebraic
primitive.

The remaining obstacle is therefore sharper:

```text
UNIVERSAL DECOMPOSITION PROBLEM

Given an arbitrary E12 hard target (equivalently its exact source quotient),
construct in polynomial time a partition/decomposition whose exact projected
boundary relations all have polynomial-size constructible linear-delta
representations.
```

E77's finite controls warn that naive bounded-local partitions are not yet such
a theorem: their best complete partitions are near-global (10/12 and 15/18).

## 9. Replay

Companion checker:

```text
experiments/r5_e78_linear_delta_equality_gluing_meta_solver.py
```

It verifies:

```text
* the two-module identity: equality gluing = delta-sum + zero restriction;
* global cut-edge multiplicity exactly two under a Tanner-vertex partition;
* q=6 optimal E77 partition: delta-sum has no empty feasible set and direct
  Exact-One count is zero;
* q=9 optimal E77 partition: delta-sum contains empty, exactly one compatible
  boundary tuple exists, and direct Exact-One count is one with support
  {1,7,8}.
```

Scientific status:

```text
E78 = PROVED CONDITIONAL RANDOMIZED-POLYNOMIAL META-SOLVER THEOREM.
UNIVERSAL_LINEAR_DELTA_DECOMPOSITION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACT_ONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```
