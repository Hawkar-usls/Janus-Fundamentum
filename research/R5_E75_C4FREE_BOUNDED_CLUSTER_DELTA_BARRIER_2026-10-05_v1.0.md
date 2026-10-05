# R5 E75 — Bounded C4-Free Cluster Delta Barrier

Date: 2026-10-05

Status:
`ALL_CONNECTED_C4FREE_TANNER_CLUSTERS_UP_TO_9_VERTICES_ARE_NON_DELTA_EXCEPT_SINGLE_EXACTONE_CHECK`

Scientific ceiling:

```text
THIS IS A FINITE-RADIUS FIREWALL, NOT A UNIVERSAL POLYNOMIAL ALGORITHM.
P_VS_NP REMAINS OPEN.
```

## 1. Motivation

E73 localizes the remaining nonlinear atom to the variable-side all-or-none
constraint

```text
Equality_3 = {000,111} = degree list {0,3}.
```

E74 proves that one Equality_3 star, the E63 strong-C5 boundary relation, and
the complete E53 one-gadget quotient are non-delta, so none has a direct
support-preserving compilation into the standard linear-delta-matroid/matching
world.

A natural escape is to group several nearby Tanner vertices first.  The hope
would be that the projected boundary support of a small connected cluster
becomes a delta-matroid even though the individual Equality_3 atom is not.

E75 tests that escape exhaustively on every local topology that can occur in a
linear square-cubic carrier through nine Tanner vertices.

## 2. Why C4-free is the exact local carrier condition

For a square-cubic incidence matrix A, the Tanner graph is bipartite and
3-regular.  If A is linear, any two columns occur together in at most one row.
Equivalently, the Tanner graph contains no 4-cycle.

Therefore every connected induced local cluster in the R5 linear target is a
connected simple bipartite C4-free graph whose internal degrees are at most
three.  Missing incident edges become dangling boundary stubs so that every
Tanner vertex still has ambient degree three.

## 3. Cluster signature

For each local topology H:

```text
check vertices    carry ExactOne_3,
variable vertices carry Equality_3.
```

Internal edges are existentially quantified.  The relation retained on the
boundary stubs is the exact projected support of all internal assignments
satisfying every local signature.

Equality_3 permits an efficient exact enumeration: each internal variable
vertex has one Boolean state y_j shared by all three incident edges.  For each
check vertex, the selected internal-neighbour sum can only be zero or one.  If
it is one, every dangling check bit is forced to zero; if it is zero, exactly
one dangling check bit is selected.

No relaxation is used.

## 4. Exhaustive topology universe

For every total cluster size s=1,...,9, the checker enumerates every labelled
connected simple bipartite graph with:

```text
* s vertices,
* internal degree <=3,
* no C4.
```

The complete counts are:

```text
s=1 :      2
s=2 :      1
s=3 :      2
s=4 :      6
s=5 :     24
s=6 :    135
s=7 :    972
s=8 :   8628
s=9 :  91440
----------------
total: 101210
```

Every projected support is nonempty.

## 5. Exact delta-matroid result

For each projected boundary family F, the checker evaluates Bouchet's symmetric
exchange axiom directly:

```text
for X,Y in F and e in X xor Y,
there must exist f in X xor Y such that
X xor {e,f} is again feasible
(with f=e allowed in the standard formulation).
```

Results:

```text
s=1:
  singleton ExactOne_3 : delta-matroid
  singleton Equality_3 : NON-delta

s=2,...,9:
  EVERY connected C4-free cluster : NON-delta
```

Thus among all 101210 labelled topologies there is exactly one delta support,
the trivial single ExactOne_3 check.

Hence:

```text
boxed:
On a linear square-cubic Tanner graph, no connected cluster of 2..9 vertices
admits a support-preserving delta-matroid boundary compilation.
```

The variable-side singleton is already non-delta, so the result also includes
size one whenever the cluster contains the hard Equality_3 atom.

## 6. Relation to matching / projected-linear approaches

Linear and projected-linear delta-matroids are subclasses of delta-matroids.
Recent algorithmic work shows that many parity, coverage, intersection and
matching-type tasks become polynomial once a linear/projected-linear
delta-matroid representation is available; see e.g. Koana and Wahlstroem,
"Faster Algorithms on Linear Delta-Matroids", STACS 2025,
DOI 10.4230/LIPIcs.STACS.2025.62.

Likewise, the Boolean edge-CSP tractability theory of even delta-matroids
(Kazda--Kolmogorov--Rolinek) depends on the symmetric-exchange structure.

E75 therefore rules out the simplest bounded-cluster route into those toolboxes
through radius nine on the actual C4-free carrier class.

It does NOT prove that every possible matchgate/holographic transformation must
preserve raw support, and it does NOT rule out weighted cancellations whose
support-level relation is non-delta.

## 7. Why this is stronger than an E12 fixture check

E75 does not enumerate subgraphs of one frozen source.  It enumerates the full
local topology universe determined only by:

```text
bipartite,
connected,
C4-free,
maximum internal degree 3,
ambient Tanner degree 3.
```

Therefore the result applies to every linear square-cubic R5 target, including
the E12 hardness image, regardless of which RXC3 source produced it.

## 8. Replay

Companion checker:

```text
experiments/r5_e75_c4free_cluster_delta_barrier.py
```

It freezes the exact topology counts, exact projected supports and exact
symmetric-exchange verdicts through nine vertices.

## 9. What remains alive

E75 removes the entire class of support-preserving connected cluster
compilations with cluster size at most nine.

The live escape routes are now sharper:

```text
1. connected clusters of size >=10;
2. cluster size growing with n / genuinely unbounded global cancellation;
3. weighted or signed cancellation not visible from Boolean support alone;
4. a non-support-preserving holographic transform that exploits the special
   global source alignment;
5. a completely different polynomial invariant/algorithm.
```

The next useful experiment is therefore not another singleton gadget test.  It
is to search for the first C4-free cluster size at which a delta/projected-linear
boundary relation can actually occur, and, if one exists, test whether such
clusters can cover arbitrary E12 target Tanner graphs with polynomially
controlled interfaces.

Scientific status:

```text
P_VS_NP = OPEN.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED.
E75 = PROVED FINITE-RADIUS FIREWALL.
```
