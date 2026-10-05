# R5 E80 — Exact q=10 Binary-Delta Universality Attack

Date: 2026-10-05

Status:
`Q10_EXHAUSTIVE_DELTA_CATALOGUE_IS_BINARY_EVEN__NEAR_GLOBAL_PARTITION_PERSISTS__GLOBAL_THEOREM_STILL_OPEN`

Scientific ceiling:

```text
E80 DOES NOT PROVE P=NP.
E80 DOES NOT PROVE THE GLOBAL BINARY-DELTA CONSTRUCTIBILITY THEOREM.

IT EXTENDS THE E79 BINARY-EVEN PHENOMENON TO A THIRD, LARGER, EXACTLY
EXHAUSTED SQUARE-CUBIC-LINEAR RXC3 CONTROL AND PROVES A GENERAL BOUNDARY-PARITY
IDENTITY THAT SHARPENS THE NEXT THEOREM TARGET.

P_VS_NP = OPEN.
```

## 1. Source family

Use the cyclic square-cubic source on `q=10` source variables/checks

```text
column j meets checks {j, j+1, j+3} mod 10.
```

Equivalently, this is the natural cyclic continuation of the frozen q=6 source
used in E17/E53/E77.  The q=10 Tanner graph has 20 vertices.

Direct checks give:

```text
* every source column has degree 3;
* every source check has degree 3;
* every two columns meet in at most one row;
* hence the Tanner graph is C4-free / source-linear;
* the Tanner graph is connected.
```

So q=10 is a genuine square-cubic-linear RXC3 control rather than a small
nonlinear artefact.

## 2. General boundary-parity identity

Let a connected Tanner cluster contain check set `C` and variable set `V`.
Write

```text
a = |C|.
```

For an internal variable assignment `y`, let `d_j` be the number of internal
cluster checks incident with variable `j`.  Feasibility requires every internal
ExactOne check to contain at most one selected internal variable.

For any exact projected boundary state `F` induced by `y`:

* a selected internal variable `j` contributes all `3-d_j` of its variable-side
  boundary stubs;
* an internal check contributes one check-side boundary stub exactly when none
  of its internal incident variables is selected.

Since the number of internally satisfied checks equals

```text
sum_j d_j y_j,
```

the boundary Hamming weight is exactly

```text
|F|
 = sum_j (3-d_j)y_j + a - sum_j d_j y_j
 = a + sum_j (3-2d_j)y_j.
```

Therefore, modulo two,

```text
boxed:
|F| = a + sum_j y_j  (mod 2).
```

This identity is universal for every ExactOne_3/Equality_3 Tanner cluster.

Consequences:

```text
1. Boundary evenness is not an arbitrary matrix phenomenon: it is equivalent
   to all locally extendible internal variable assignments having one parity,
   after quotienting assignments that induce the same boundary state.

2. To prove a universal linear/even-delta theorem, it is enough to understand
   why symmetric exchange would forbid opposite-parity extendible assignments.

3. An opposite-parity pair is therefore a direct target for an obstruction
   search: if the boundary relation were nevertheless a delta-matroid, it would
   give an odd-delta witness and kill the current even-linear conjecture.
```

E80 does not yet prove that symmetric exchange forces one assignment parity in
all RXC3 clusters.  It converts that issue into a sharply stated local theorem.

## 3. Complete q=10 enumeration

The companion checker enumerates all

```text
2^20 - 1 = 1,048,575
```

nonempty Tanner-vertex subsets.

Exactly

```text
180,537
```

are connected induced clusters.

For each connected cluster E80 computes the exact projected boundary relation
under the same ExactOne_3 / Equality_3 semantics as E74–E79 and tests Bouchet
symmetric exchange.

The exact delta-support count is

```text
1,845.
```

Distribution by cluster size:

```text
size 1  : 10
size 12 : 10
size 13 : 80
size 14 : 300
size 15 : 530
size 16 : 540
size 17 : 340
size 18 : 35
```

There are no connected delta-support clusters at sizes 2 through 11, 19, or 20.

## 4. E79 binary reconstruction on all 1,845 relations

For every one of the 1,845 delta-support clusters, E80 applies the constructive
E79 test:

```text
* choose a feasible seed S;
* twist by S;
* verify one boundary parity;
* reconstruct the zero-diagonal GF(2) matrix from all feasible pair flips;
* enumerate all principal nonsingular sets of that matrix;
* require exact equality with the original twisted boundary family.
```

Result:

```text
boxed:
1,845 / 1,845 q=10 delta-support relations are even binary.
```

There are

```text
0
```

binary-reconstruction failures and

```text
0
```

odd delta-matroid witnesses.

Together with E79:

```text
q=6 :   99 /   99 delta clusters binary even
q=9 :  412 /  412 delta clusters binary even
q=10: 1845 / 1845 delta clusters binary even
---------------------------------------------
TOTAL: 2356 / 2356 exact catalogued delta clusters binary even.
```

This is still finite evidence, not a universal theorem.

## 5. Exact complete-partition stress test

E80 solves exactly the same min-max partition problem as E77:

```text
partition all Tanner vertices into disjoint connected clusters
whose exact boundary supports are delta-matroids,
minimizing the largest cluster size.
```

For q=10:

```text
boxed:
minimum maximum piece size = 17 out of 20 vertices.
```

One optimum has part sizes

```text
1,1,1,17.
```

The size-17 piece has singleton boundary support.

The currently frozen exact sequence is therefore

```text
q=6  : 10/12 = 2q-2
q=9  : 15/18 = 2q-3
q=10 : 17/20 = 2q-3.
```

This does not prove an asymptotic lower bound, but it strengthens the warning
against a bounded-radius tiling theorem: every exact complete decomposition seen
so far is dominated by a near-global piece.

## 6. What E80 proves and what it does not

### Proved

```text
A. Universal boundary-parity identity:
       |F| = |C| + sum_j y_j mod 2.

B. Exact q=10 exhaustive catalogue:
       1,845 connected delta-support clusters.

C. Every q=10 delta-support cluster is even binary.

D. Exact q=10 min-max complete delta partition is 17/20.
```

### Not proved

```text
A. Delta exchange => evenness for every RXC3 exact boundary relation.
B. Delta exchange => binary representability for every RXC3 exact boundary.
C. Polynomial construction of a complete decomposition on arbitrary input.
D. Polynomial local extension / pair-flip membership access.
E. P=NP.
```

## 7. Sharpened theorem target

The strongest plausible next structural lemma is now:

```text
RXC3 DELTA-EVENNESS LEMMA

For every connected induced Tanner cluster of a square-cubic-linear RXC3
source, if its exact projected ExactOne_3/Equality_3 boundary relation satisfies
Bouchet symmetric exchange, then every feasible boundary set has one parity.
```

By Section 2, this is equivalent to ruling out opposite-parity locally
extendible variable assignments inside a delta-support cluster.

After that, one still needs:

```text
RXC3 DELTA-BINARY LEMMA

Every such even delta-support relation avoids the Bouchet-Duchamp excluded
minors for binary delta-matroids (equivalently, its E79 pair-reconstructed
GF(2) matrix regenerates the complete relation).
```

E79 then turns binary existence into explicit matrix construction once a seed
and pair-flip membership oracle are available.

## 8. Next killer-test

Do not broaden to arbitrary q blindly.  Attack the first theorem directly.

Search for a connected square-cubic-linear RXC3 cluster with:

```text
1. two exact boundary states of opposite parity;
2. Bouchet symmetric exchange still holding.
```

Such a witness immediately disproves `RXC3 DELTA-EVENNESS`.

If no witness is found on q=11/q=12 controls, record the smallest
opposite-parity boundary family and its first explicit symmetric-exchange
failure.  The pattern of that failure is the object from which a general proof
should be extracted.

In parallel, for even delta-support relations, run the Bouchet-Duchamp excluded
minor/reconstruction test rather than assuming binary representability.

## 9. Companion checker

```text
experiments/r5_e80_q10_binary_delta_universality_attack.py
```

Frozen assertions:

```text
all subsets             = 1,048,575
connected subsets       = 180,537
delta-support clusters  = 1,845
binary failures         = 0
odd-delta witnesses     = 0
min-max partition       = 17/20
optimal part sizes      = [1,1,1,17]
```

Scientific status:

```text
E80 = PROVED GENERAL BOUNDARY-PARITY IDENTITY
      + EXACT q=10 EXHAUSTIVE BINARY-EVEN CONTROL
      + STRONGER NEAR-GLOBAL PARTITION EVIDENCE.

GLOBAL_BINARY_DELTA_CONSTRUCTIBILITY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACT_ONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```
