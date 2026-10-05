# R5 E87 — p=1,h=1 Residual Exchange Graph Killer at t=3

Date: 2026-10-06

Status:
`P1_H1_CONDITIONED_U24_EXCLUDED_THROUGH_T3__RESIDUAL_EDGE_HALFEDGE_NORMAL_FORM_PROVED`

Scientific ceiling:

```text
E87 DOES NOT EXCLUDE ALL CONDITIONED U2,4 MINORS.

IT CLOSES THE p=1,h=1 LANE THROUGH
    t=3 -> 10 checks / 9 variables,
USING AN EXACT RESIDUAL EXCHANGE-GRAPH NORMAL FORM.

THE FIRST OPEN SIZE IN THIS LANE IS
    t=4 -> 13 checks / 12 variables.

OTHER ZERO-HOLE ORIENTATIONS REMAIN OPEN.

P_VS_NP = OPEN.
```

## 1. Why E86 should not be scaled naively

E86 directly generated C4-free bipartite incidence matrices and excluded the
(p=1,h=1) lane for (tle2).

At (t=3) the raw incidence search grows rapidly.  The right move is to use
one of the six hypothetical conditioned (U_{2,4})-twist states as a
reference exact cover, as E84 did for the direct lane.

The E85 arithmetic gives

[
a=3t+1,qquad b=3t.
]

For (t=3):

[
a=10,qquad b=9.
]

Every feasible four-port state selects exactly (t=3) active variables.

## 2. Reference state

Freeze a target state with

```text
variable survivor bit = 1,
check survivor A = 1,
check survivor B = 1,
check survivor C = 0.
```

If the unique zero hole overlaps one of the three survivor checks, relabel the
survivors so that the overlap is on A.  Because the target family is symmetric
under permutation of the three check-side survivor coordinates, this loses no
generality.

The reference cover therefore selects exactly three variables:

* the unique boundary variable (x), whose variable-side survivor bit is 1;
* two ordinary cubic reference variables.

The boundary variable (x) has two internal Tanner checks.  Each ordinary
reference variable has three.

Thus the selected reference variables account for

[
2+3+3=8
]

internally covered checks.

The two externally satisfied checks A and B account for the remaining two of
the ten checks.

## 3. Six residual variables

The remaining

[
b-t=9-3=6
]

variables are unselected in the reference state.

Every one of them is an ordinary cubic active variable with no pinned
incidence, by the E85 propagation theorem.

Remove the three selected reference-cover variables conceptually and examine
how each Tanner check meets the six residual variables.

## 4. Exactly eight edges and two half-edges

For an ordinary internally covered cubic check, removal of its one selected
reference variable leaves two residual variable neighbours.  This becomes an
ordinary residual edge.

Two exceptional checks have only one residual variable neighbour.

### Distinct-hole case

The zero hole is on a check distinct from A,B,C.

Then:

* A and B are externally satisfied survivor checks and each leaves two residual
  neighbours;
* C is internally covered, has one free survivor boundary incidence, and leaves
  one residual neighbour;
* the zero-hole check is internally covered, loses one incidence to the pinned
  zero, and leaves one residual neighbour;
* every other check leaves two residual neighbours.

Hence C and H are the two half-edges.

### Overlap case

The zero hole overlaps A, chosen externally satisfied in the reference state.

Then:

* A has one free survivor port, one pinned-zero hole, and one residual internal
  neighbour: it becomes one half-edge;
* C is internally covered with one survivor port and becomes the other
  half-edge;
* B and all remaining checks become ordinary residual edges.

Thus in both cases:

[
oxed{
	ext{six residual vertices, eight ordinary edges, two half-edges.}
}
]

Every residual vertex has degree exactly three when the half-edges are counted.

## 5. C4-freeness becomes simplicity plus matching blocks

An ordinary residual edge records a Tanner check shared by its two residual
variables.

If two residual variables were joined by two ordinary residual edges, they
would share two Tanner checks, giving a Tanner C4.

Therefore the eight ordinary residual edges form a **simple graph**.

Now consider one selected reference variable.  Its incident Tanner checks
become a set of residual edge/half-edge objects.

If two of those objects shared a residual endpoint, that residual variable and
the selected reference variable would share two Tanner checks, again giving a
Tanner C4.

Therefore every selected reference variable induces a **matching block** in
the residual object graph.

The check objects split as:

```text
A,B                         : two distinguished external checks
boundary reference variable: one size-2 matching block
two core reference variables: two size-3 matching blocks
```

The two size-3 blocks are unordered.

## 6. Exact normalized residual graph census

The half-edge C is attached to some residual vertex.  By residual-vertex
relabeling, fix that endpoint to vertex 0.

Let the second half-edge endpoint be any of vertices 0,...,5.

For a vertex incident with (r) half-edges, its degree in the ordinary simple
graph must be (3-r).

E87 enumerates every simple 8-edge graph on six labeled residual vertices with
exactly those degree requirements.

The complete normalized count is:

[
oxed{300	ext{ residual graphs}.}
]

No graph-isomorphism heuristic is used.  The list is generated exhaustively
from the 15 possible simple edges.

## 7. Complete matching-role enumeration

For each residual graph E87 enumerates all allowed reference-cover partitions.

### Overlap case

The second half-edge is A itself.

Choose B as one ordinary residual edge.

The remaining eight check objects are partitioned into:

* one distinguished size-2 matching block for the boundary variable;
* two unordered size-3 matching blocks for the two core reference variables.

Exact total:

[
oxed{6,600	ext{ overlap configurations}.}
]

### Distinct case

The two half-edges are C and the zero-hole check H.

Choose ordered distinct ordinary edges A and B.

The remaining eight objects are again partitioned into one size-2 and two
unordered size-3 matching blocks.

Exact total:

[
oxed{103,800	ext{ distinct-hole configurations}.}
]

Grand total:

[
oxed{110,400}.
]

## 8. Residual exact semantics

Let (S) be the set of residual variables selected relative to the reference
cover.

Because an ordinary residual edge is an ExactOne check after removal of the
reference-cover variable, (S) must be independent in the ordinary residual
graph.

For each residual check object, define its crossing value as whether exactly
one residual endpoint is selected.  A half-edge crosses iff its unique residual
endpoint is selected.

For each reference-variable matching block, the common Equality state of that
reference variable must be compatible with every check in the block.

The size-2 block state is exactly the free variable-side survivor bit.

A and B are external checks, so their free boundary bits are the complement of
their crossing values.

C is a block check with a free boundary bit, so its bit fills the remaining
ExactOne demand.

In the distinct case H is the block check carrying the fixed-zero hole.

These equations compute the complete four-port family without any SAT oracle.

## 9. Independent semantic cross-check

To guard the residual reduction itself, E87 contains a second evaluator.

It explicitly reconstructs the nine Tanner variable truth values:

* six residual variables;
* boundary reference variable (x);
* two core reference variables.

It then checks every ExactOne condition directly and derives the four free
boundary bits.

For the first 100 deterministic configurations, the direct evaluator and the
residual crossing evaluator agree exactly.

This check is independent of the residual state-transition implementation.

## 10. Exact result

Across all

[
110,400
]

C4-free residual configurations:

[
oxed{
{1,2,4,11,13,14}
	ext{ occurs zero times.}
}
]

Therefore:

[
oxed{
p=1, h=1, t=3
	ext{ cannot realize the conditioned }U_{2,4}	ext{ family.}
}
]

Combined with E86:

[
oxed{
p=1,h=1	ext{ is excluded for }t=1,2,3.
}
]

## 11. First remaining p=1,h=1 size

The next size is

[
t=4:
qquad
a=13,qquad b=12.
]

The same reference-cover argument would leave

[
2t=8
]

residual variables.

The residual object graph has:

[
3t-1=11
]

ordinary edges and two half-edges, with degree three at every residual vertex
counting half-edges.

The reference-cover partition becomes:

```text
2 external distinguished checks
1 size-2 matching block
3 size-3 matching blocks
```

The graph topology count is still manageable, but the matching partition count
will rise substantially.

## 12. Toward an induction invariant

E84 and E87 now show the same repeated pattern:

1. choose a feasible reference cover;
2. unselected variables become residual vertices;
3. checks become edges/half-edges;
4. C4-freeness makes the residual graph simple;
5. selected reference variables become matching blocks;
6. the exact boundary family is determined by cut/crossing behavior of
   independent residual sets.

This strongly suggests that the desired universal binary theorem, if true,
should be proved as a structural statement about **matching partitions of
simple subcubic residual graphs**, not by enumerating Tanner graphs directly.

The next target should therefore search for a parity/cut invariant that rules
out the six-state (U_{2,4})-twist relation for every (t), using E87 as the
base case.

## 13. Next killer-test — E88

```text
P1_H1 ALL-t PARITY KILLER

In the E87 residual graph-plus-matching-block model, prove that the four-port
relation cannot equal the p=1 U2,4 twist for any t.

Candidate invariants:
  * GF(2) parity of valid independent-set cut patterns;
  * circuit/cocircuit parity in the induced boundary basis matroid;
  * parity of matching-block crossing vectors;
  * an induction under deletion of a residual vertex / matching block.

If a universal parity proof fails, run the exact t=4 residual census as the
next counterexample search.
```

## 14. Companion replay

```text
experiments/r5_e87_p1_h1_residual_exchange_graph_killer.py
```

Frozen assertions:

```text
normalized residual graphs = 300
overlap configurations = 6,600
distinct configurations = 103,800
total configurations = 110,400
direct semantic crosschecks = 100
conditioned p=1 U2,4 hits = 0
```

Scientific status:

```text
E87 = EXACT P1_H1 EXCLUSION THROUGH T=3
      + RESIDUAL EDGE/HALF-EDGE MATCHING-BLOCK NORMAL FORM.

P1_H1_T1_T2_T3 = EXCLUDED.
P1_H1_T4_PLUS = OPEN.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
