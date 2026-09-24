# R5 E10A — Two-Row Graph Lift to Group-Constrained Circulation

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_BRIDGE_AFTER_AUDIT__SOURCE_BOUND_RANDOMIZED_TERMINAL__NOVELTY_NOT_CLAIMED__DETERMINISTIC_GAP_OPEN`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Parent gate:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_two_row_lift_gcc_bridge.py`

## 1. Exact input object

Let

```
A =
[ B_G ]
[ S   ],
```

where `B_G` is a reduced binary vertex-edge incidence matrix and
`S in GF(2)^(r x E)`.  The audited first open deterministic rung has `r=2`.

Write

```
lambda(e) in GF(2)^r
```

for the label of edge `e`.

For a distinguished ordinary edge `f=uv`, a set `J subseteq E-{f}`
spans `f` exactly when

```
boundary(J) = {u,v}
and
XOR_{e in J} lambda(e) = lambda(f).
```

Thus

```
shortest_f(M)
=
1 +
minimum-cardinality {u,v}-join
with prescribed GF(2)^r label.
```

This artifact proves an exact witness-preserving reduction of that problem to
group-constrained circulation.

## 2. Directed GCC construction

Let `Gamma=GF(2)^r` and augment it by one forcing bit:

```
Gamma' = Gamma x GF(2).
```

For every undirected edge `e=ab` other than `f`, create two directed arcs

```
a -> b,
b -> a,
```

each with

- capacity one;
- length `w(e)>0`;
- group label `(lambda(e),0)`.

Add one special arc

```
v -> u
```

with

- capacity one;
- length zero;
- group label `(0,1)`.

Ask for a minimum-length circulation whose total group label is

```
(lambda(f),1).
```

Because the last coordinate can only be contributed by the special arc, every
feasible circulation uses that arc exactly once.

## 3. Forward map: T-join to circulation

Let `J` be a feasible `{u,v}`-join with the required group label.

Every connected component of `J` other than the component containing
`u,v` is Eulerian.

The `u,v` component has exactly two odd vertices and hence admits an Euler trail
from `u` to `v`.

Orient:

- that Euler trail from `u` to `v`;
- every other Eulerian component as a directed Euler tour.

Then add the special arc `v -> u`.

The result is a circulation. Its ordinary-arc group sum is exactly the label of
`J`, and the special arc contributes the forcing bit. Its length equals
`w(J)`.

Therefore:

```
OPT_GCC <= OPT_TJOIN.
```

The map is constructive and linear in the selected subgraph.

## 4. Reverse map: circulation to T-join

Take an optimal feasible circulation.

Suppose it contains both orientations of one ordinary undirected edge
`e=ab`.

Deleting those two opposite arcs:

- preserves flow balance at `a,b`;
- changes the group sum by
  `2(lambda(e),0)=0`, because `Gamma'` has exponent two;
- removes positive length `2w(e)`.

Hence no optimum uses both orientations of one ordinary edge.

Remove the forced special arc.

The remaining directed ordinary edges have imbalance:

```
+1 at u,
-1 at v,
0 elsewhere.
```

Consequently their underlying undirected edge set has odd-degree boundary
exactly `{u,v}`.

Its group label is `lambda(f)`, because the special arc carries zero in the
first `r` coordinates.

Thus it is a feasible labelled T-join of equal cost, giving

```
OPT_TJOIN <= OPT_GCC.
```

Therefore:

```
boxed(
OPT_TJOIN = OPT_GCC
)
```

with polynomial witness conversion in both directions.

## 5. Why path-only is not exact

A labelled T-join need not be only one labelled `u-v` path.

The checker contains an explicit control:

- the only `u-v` path has label zero;
- a disjoint 3-cycle has nonzero group label;
- the required target is the cycle label.

The unique feasible optimum is

```
u-v path
+
disjoint labelled cycle.
```

So a shortest group-labelled path algorithm alone does not solve this object.

The GCC bridge keeps those Eulerian label-correction components exactly.

## 6. Source-bound algorithmic consequence

Nägele et al., *Advances on strictly Delta-modular IPs*, formulate
group-constrained circulation as the network-matrix base block of
group-constrained TU optimization.

Their Theorem 31 gives a strongly polynomial **randomized** algorithm for
group-constrained TU optimization with unary encoded objectives and network
matrices, for any fixed finite abelian group.  The paper explains that the
randomization enters through exact-length circulation / exact-cost perfect
matching machinery.

For the audited two-row lift,

```
Gamma' = GF(2)^3,
|Gamma'| = 8,
```

a fixed group, and unit edge lengths are unary.

Hence:

```
TWO-ROW GRAPH-LIFT SHORTEST-f
=
RANDOMIZED POLYNOMIAL
```

via the exact bridge above and the source-bound GCC algorithm.

More generally, for every fixed number `r` of signature rows,

```
Gamma' = GF(2)^(r+1)
```

has constant size, so the same source-backed randomized-polynomial lane applies.

## 7. Deterministic firewall

This result is **not** a deterministic polynomial algorithm.

The source explicitly traces its randomization to exact-length circulation /
exact-cost perfect matching machinery, closely related to the longstanding
Exact Matching derandomization issue.

JANUS does not claim that the present `GF(2)^2`-labelled T-join is equivalent
in difficulty to general Exact Matching.

Therefore the surviving question is narrower:

```
R5_E10A_GF2_SQUARED_TJOIN_DETERMINIZATION_GATE_V1
```

Input:

```
undirected G,
T={u,v},
unit positive weights,
lambda:E->GF(2)^2,
target g in GF(2)^2.
```

Known:

```
randomized polynomial exact solver
=
SOURCE-BOUND.
```

Required:

```
deterministic polynomial exact solver
OR
strict exact contraction specific to this subclass.
```

Forbidden:

- assuming a generic Exact Matching derandomization;
- storing the full trellis/min-plus syndrome table;
- replacing the T-join by only a path;
- confusing row-lift dimension with additive perturbation rank.

## 8. Universal-algorithm interpretation

The graph-lift ladder is now:

```
r=0
graphic
-> deterministic P

r=1
one signature row / even-cycle
-> deterministic P

r=2
two signature rows
-> randomized P by GCC
-> deterministic exact status remains open in this audit

fixed r
-> randomized P by the same finite-group GCC mechanism
```

So increasing lift dimension is still a meaningful JANUS compression coordinate,
but **existence of a polynomial randomized solver is no longer the missing
mechanism at fixed r**.

The exact next brick is deterministic multiplicity destruction / derandomization
for the first nontrivial two-label-bit T-join class.

## 9. Claim ceiling

```
TWO-ROW -> LABELLED T-JOIN
=
EXACT

LABELLED T-JOIN -> GCC
=
EXACT

WITNESS RECONSTRUCTION
=
POLYNOMIAL

FIXED-r RANDOMIZED POLY
=
SOURCE-BOUND

DETERMINISTIC r=2
=
OPEN IN THIS AUDIT

P_VS_NP
=
OPEN
```
