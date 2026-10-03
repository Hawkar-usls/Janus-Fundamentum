# R5 E51 — Complementary Two-Claw Permutation Propagation

Date: 2026-10-03

Status:
`EXACT_ALL_TWO_COMPLEMENTARY_CLAW_POLYNOMIAL_TERMINAL__EDGEWISE_S3_STATE_PROPAGATION__AT_MOST_THREE_STATES_PER_CONNECTED_COMPONENT`

Scientific ceiling:

```text
THIS NOTE APPLIES TO THE FROZEN ALL-POSITIVE SQUARE+CUBIC+LINEAR E12 CARRIER.

ASSUME EVERY ACTIVE CONFLICT VERTEX v HAS EXACTLY TWO INDUCED CLAWS AND THEY
ARE COMPLEMENTARY:

  N(v)=T_v^0 DISJOINT_UNION T_v^1.

THEN EACH v HAS EXACTLY THREE LOCAL WITNESS STATES:

  C_v : v ITSELF IS SELECTED;
  0_v : v IS UNSELECTED AND T_v^0 IS THE SELECTED-NEIGHBOR CLAW;
  1_v : v IS UNSELECTED AND T_v^1 IS THE SELECTED-NEIGHBOR CLAW.

FOR EVERY CONFLICT EDGE vu, THE STATE OF v DETERMINES THE STATE OF u BY A
BIJECTION OF THESE THREE STATES.  THEREFORE EACH CONNECTED COMPONENT IS
SOLVED BY TRYING THREE ROOT STATES AND PROPAGATING EDGE PERMUTATIONS.

THIS GIVES A DETERMINISTIC LINEAR-TIME TERMINAL AFTER THE CLAW SETS ARE KNOWN.

P_VS_NP = OPEN.
```

## 1. Setting

Let `G_A` be the conflict graph of a square+cubic+linear all-positive Exact-One
carrier.

Assume exhaustive R5 E48--E50 closure has reached a component in which every vertex
has exactly two claw leaf sets and they are complementary.  For each vertex choose
an arbitrary ordering

```text
N(v)=T_v^0 disjoint_union T_v^1,
|T_v^0|=|T_v^1|=3.
```

Because the two claws are complementary, every neighbor belongs to exactly one side.

## 2. Three local witness states

In any Exact-One witness exactly one of the following holds at `v`:

```text
C_v:
  x_v=1,
  every neighbor of v is 0.

0_v:
  x_v=0,
  exactly the vertices of T_v^0 are selected among N(v).

1_v:
  x_v=0,
  exactly the vertices of T_v^1 are selected among N(v).
```

There are no other possibilities because an unselected vertex must see one of its
two claw leaf sets as its three selected neighbors.

Thus each vertex carries a three-state local variable.

## 3. Edge transition rule

Take an edge

```text
vu in E(G_A).
```

Let

```text
u in T_v^a,
v in T_u^b,
```

where `a,b in {0,1}`.

We determine the state of `u` from the state of `v`.

### If v is in state C_v

Then `v` is selected, so `u` is unselected.  Since `v` is a selected neighbor of
`u`, the selected-neighbor claw of `u` must be the unique side containing `v`, namely

```text
T_u^b.
```

Hence

```text
C_v -> b_u.
```

### If v is in state a_v

Then `u in T_v^a` is selected. Therefore `u` itself is in center state:

```text
a_v -> C_u.
```

### If v is in state (1-a)_v

Then `u` is unselected, and `v` is also unselected. Therefore the selected-neighbor
claw of `u` cannot be the side containing `v`; it must be the opposite side:

```text
(1-a)_v -> (1-b)_u.
```

So every edge carries the transition

```text
boxed:
C_v       -> b_u,
a_v       -> C_u,
(1-a)_v   -> (1-b)_u.
```

The three outputs are distinct, so this is a permutation of the three local states.

## 4. Bidirectional consistency

Applying the same rule from `u` back to `v` gives the inverse permutation. Therefore
an undirected conflict edge carries a well-defined bijective state constraint.

Consequently, once one vertex state is fixed, every state encountered along a path
is uniquely determined by composing edge permutations.

A cycle is consistent exactly when the composed permutation fixes the propagated
root state.

## 5. Exact propagation algorithm

For each connected component:

```text
1. choose a root r;
2. try the three possible root states C_r,0_r,1_r;
3. BFS/DFS through the component;
4. propagate the unique state across every traversed edge;
5. if a previously assigned vertex receives a different state, reject that root
   state;
6. otherwise reconstruct x_v=1 exactly for vertices in state C_v;
7. verify the original Exact-One rows.
```

Each root trial is linear in the component size, so the total work is linear up to a
constant factor after claw enumeration.

## 6. Soundness

Every genuine Exact-One witness induces the local state at each vertex.
Section 3 proves that these states satisfy every edge permutation constraint.
Therefore the propagation algorithm cannot reject a genuine witness root state.

## 7. Completeness

Conversely suppose one root state propagates consistently through a connected
component.

Set

```text
x_v=1 iff v is in state C_v.
```

Take any vertex `v`.

If `v` is in center state, every neighbor is propagated to a side state, so no
neighbor is selected.

If `v` is in side state `a`, every neighbor in `T_v^a` is propagated to center state
and every neighbor in `T_v^(1-a)` to a side state. Thus exactly the three vertices of
`T_v^a` are selected among `N(v)`.

Now consider any source triangle containing `v`. Its other two vertices form one of
the three source-pairs inside `N(v)`. Because each claw contains exactly one vertex
from every such pair:

```text
if v is selected -> neither partner is selected;
if v is unselected -> exactly one partner is selected.
```

Hence every source row contains exactly one selected variable.

Therefore the propagated state assignment reconstructs a genuine Exact-One witness.

So propagation is exact.

## 8. Theorem TWO-CLAW-PERMUTATION

```text
boxed:
If every vertex of a connected square+cubic+linear all-positive carrier has exactly
two complementary induced claws, Exact-One is decidable by three-state permutation
propagation in deterministic polynomial time.
```

For a connected component there are at most three consistent global state
assignments, one per root state.  Each consistent state assignment gives one witness.

For disconnected carriers, solve the components independently.

## 9. Relation to earlier branches

R5 E48 handles zero-claw vertices.

R5 E49 handles unique-claw vertices.

R5 E50 removes overlapping two-claw ambiguity by forcing common leaves and
outside-union zeros.

E51 closes the remaining **pure two-claw complementary** sector completely.

Therefore after exhaustive E48--E51 closure, every unresolved active connected
component must contain at least one vertex with **three or more** induced claws.

This is a genuine reduction of the hard core.

## 10. Finite control

The companion checker uses the 3x3 toroidal square+cubic+linear carrier.
Every conflict vertex has exactly two complementary claw leaf sets.

The three root states propagate consistently and reconstruct exactly the three
Exact-One witnesses of the carrier.

Thus the terminal is replayed on a nontrivial SAT family member rather than merely
on a synthetic state graph.

## 11. Scope caveat

As with E48--E50, the proof relies on the all-positive E12 conflict graph and the
independent-set interpretation of selected variables.  It is not automatically a
theorem for arbitrary signed-literal co-occurrence graphs.

## 12. Updated frontier

The local conflict-graph ambiguity hierarchy is now:

```text
0 claws  -> E48 forcing;
1 claw   -> E49 forcing/parity;
2 claws with overlap -> E50 forcing/parity;
2 complementary claws everywhere in a component -> E51 exact 3-state propagation;
>=3 claws -> unresolved local core.
```

Thus any post-E51 hard survivor must retain genuine three-or-more-way claw ambiguity
somewhere after all exact propagation and quotienting.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e51_two_claw_permutation_propagation.py
```
