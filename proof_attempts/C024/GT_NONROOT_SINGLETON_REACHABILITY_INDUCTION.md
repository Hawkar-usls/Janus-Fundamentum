# C024 — Non-root singleton reachability: exact-key induction route

Status: **CYCLE/TREE EXCHANGE, GRAPH GROWTH, AND ABSORPTION PROVED / TWO GT-SPECIFIC GATES OPEN**  
Scope: the remaining non-root branch handoff in exact Policy-0A on graph tautologies.

This document does not claim the global graph-tautology cache lower bound, an unrestricted Resolution or SAT lower bound, or a resolution of `P` versus `NP`.

## 1. Temporal induction

The induction is over exact cache keys:

```text
K   exact entry key after pre-units
R   K plus frozen one-pass Resolution outputs
P   post-unit residual
B   raw child after the selected branch
K'  next exact key after child pre-units
```

Temporary clauses in `R/P` may be structurally deeper than their `K` parents. The invariant is return to normal form at `K'`, not pointwise monotonicity at every temporary stage.

## 2. Proved dependencies

```text
FROZEN_FRESH_SIDE_BARRIER                         PROVED
POST_UNIT_TOTAL_COMPONENT_COLLAPSE                PROVED
ROOT_BRANCH_HANDOFF                               PROVED_ARBITRARY_N
TREE_EXCHANGE_CUT_PRESERVATION                    PROVED
TWO_NODE_TAIL_WING_HANDOFF                        PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION            PROVED
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE               PROVED
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH                 PROVED
MARKED_SINGLETON_EDGE_ABSORPTION                  PROVED
```

The earlier `553 post-unit births` interpretation is retired. Exact replay finds zero post-unit births of new same-cut complementary bridge pairs.

## 3. K-normal exact-key invariant

A simple rooted in-arborescence is **K-normal** when it is a star or a one-subdivision star:

```text
height <= 2
non-star edge count <= 1
```

The original root component-spanning in-arborescence clauses are stars. K-normality is therefore the base case and an inductive conclusion, not an independent arbitrary-`n` premise.

## 4. Directed-cycle/tree resolvent exact exchange — proved

Let `D` be the simple external graph of one legal Resolution parent and suppose `D` is an in-arborescence with root `r`. Let its pivot be

```text
p = a -> b.
```

Suppose the other parent contains the complementary literal `b->a` and a directed cycle. If the simple external resolvent `R` has an underlying tree, then:

1. every directed cycle in the cycle parent must use `b->a`; otherwise a pivot-avoiding cycle survives in `R`;
2. deleting `b->a` from such a cycle leaves a directed path from `a` to `b`;
3. `D-p` is a two-component forest with `|V|-2` edges while tree `R` has `|V|-1`, so exactly one cycle-parent edge can be new relative to the forest;
4. the first path edge out of `a` must be that unique new edge because `a` has no outgoing edge after deleting `p`;
5. every later path edge and every additional external cycle-parent edge duplicates an existing tree edge with the same orientation.

Therefore

```text
R = (D - {p}) union {l}
```

for one unique new external edge `l`, and `R` is an in-arborescence with the same root `r`.

```text
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N = PROVED
```

This theorem is uniform in the number of quotient components and does not require the cycle parent to be a triangle or the tree parent to be K-normal.

Independent simple-cycle-path falsification gate through six vertices:

```text
tree parents                    1440
directed cycle paths          422418
legal resolvents              203816
non-tree resolvents           196020
tree resolvents                 7796
new edge at first path position 7796
violations                         0
```

The earlier transitivity-triangle theorem is the length-two path corollary. Its separate gate covers 18,247 tree parents, 531,732 triangle instances, 76,676 tree resolvents, and zero violations.

Exact exchange and common-root preservation are therefore no longer GT-specific proof obligations. GT reachability only has to establish the cycle-parent/tree-parent/tree-result hypotheses.

## 5. K-normal one-edge exchange growth — proved

For a K-normal in-arborescence `D` and a same-root exact exchange

```text
Q = (D - p) + l,
```

we have

```text
nonstar(Q) <= 2
height(Q)  <= 3.
```

If `Q` is not K-normal, contracting either non-star edge returns a K-normal tree.

```text
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N = PROVED
```

Independent labelled gate through eight vertices:

```text
K-normal sources                 119
exact one-edge exchanges        3920
K-normal results                1316
non-K-normal results            2604
marked contractions             5208
violations                         0
```

Canonical result shapes are exactly `(1,0,false)`, `(2,1,true)`, `(2,2,false)`, and `(3,2,false)`. Every marked contraction of a non-K-normal result has shape `(2,1,true)`.

## 6. Marked singleton-edge absorption — proved

A **one-step marked extension** replaces one edge of a K-normal tree by a two-edge path and marks either new half-edge `e`. Contracting `e` recovers the K-normal source tree.

If the marked edge is selected and its endpoint relation components are singleton sets, then:

```text
marked literal satisfied
    -> clause extinct

marked literal falsified
    -> delete marked literal
    -> identify singleton endpoints
    -> graph contraction T/e
    -> recover the K-normal source tree
```

Additional child pre-units can only simplify further.

```text
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N = PROVED
```

Independent labelled gate:

```text
source stars                       7
source one-subdivision stars     112
marked extensions                672
marked half-edge branches       1344
violations                         0
```

## 7. Finite exact-key handoff

Complete non-root exact-exchange replay through `GT_8`:

```text
source exact-key shapes
  star                    63
  one-subdivision         34

raw/post shapes
  star                    49
  one-subdivision         45
  transient deep           3

child exact-key shapes
  star                    42
  one-subdivision         25
  deep                     0
```

The three transient deep clauses are

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

Each has source shape `(2,1,true)`, raw/post shape `(3,2,false)`, selected literal `-8`, and selected component sizes `(1,1)`. One polarity makes the clause extinct; the other deletes/contracts `-8` and returns the child exact-key shape to `(2,1,true)`.

This is finite evidence for the two arbitrary-`n` GT-specific gates below, not their proof.

## 8. Selector-origin evidence

For the three deep rows:

```text
selected variable       8
selected frequency     75
competitor frequencies 67,68,68
strict margins          8,7,7
source delta            0,0,0
```

With origin coordinates

```text
ROOT_NON_MINIMALITY,
ROOT_TRANSITIVITY,
LOCAL_RESOLVENT,
INHERITED_DERIVED,
OTHER_DERIVED,
```

the selected-minus-competitor vectors are

```text
(0,2,10,-4,0)
(0,2,10,-5,0)
(0,2,10,-5,0)
```

The tracked clause itself gives no selector advantage. The strict margin is generated by the frozen local block and partially offset by inherited derived clauses.

The complete 42-lineage finite profile is heterogeneous and contains both strict margins and least-index ties. Component-pair frequency factorization and a universal origin-vector formula are false. An arbitrary-`n` selector proof must retain clause history, polarity, vertex identity, and exact tie-breaking.

## 9. Two remaining arbitrary-n GT gates

### Gate A — cycle/tree/tree-result producer reachability

```text
NONROOT_UNSHIELDED_CYCLE_TREE_TREE_RESULT_REACHABILITY_ARBITRARY_N = OPEN
```

Every arbitrary-`n` reachable non-root immediate-local unshielded producer must be shown either to fall into an already proved safe route or to have:

1. one legal directed-cycle parent carrying the complementary pivot;
2. one simple K-normal component-spanning in-arborescence parent;
3. a simple external resolvent whose underlying graph is a tree.

Under these three hypotheses, exact same-root one-edge exchange follows automatically from the proved cycle/tree theorem. No triangle ancestry, sibling normal form, direct exact-exchange proof, or separate common-root proof is required.

### Gate B — exposed-subdivision selector dominance

```text
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
```

For every reachable non-root immediate-local unshielded state, exact Policy-0A must select either:

1. a variable whose branch is already covered by a proved safe route; or
2. a marked exposed comparison joining two singleton relation components.

A falsifier is a reachable state whose exact maximum-frequency/least-index variable avoids every established safe route and is not such a marked singleton comparison.

## 10. Exact-key induction after the two gates

Assuming Gate A and Gate B:

```text
K
  relevant tree parents are K-normal by induction

K -> R
  dangerous producer has cycle parent + K-normal tree parent + tree result
  -> cycle/tree theorem gives same-root exact one-edge exchange
  -> growth theorem gives K-normal or one marked transient layer

R -> P
  post-units do not create new same-cut pairs
  extinct or otherwise safe clauses leave the tracked route

P -> B
  selector takes a proved safe diversion or the marked singleton edge

B -> K'
  satisfying polarity kills the clause
  falsifying polarity contracts the marked edge
  -> absorption theorem restores K-normal form
```

Thus K-normality propagates from one exact key to the next.

After both gates close:

```text
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = PROVED
T3_EXACT_KEY_TEMPORAL_INDUCTION                    = DIRECT
```

Neither conclusion may be promoted earlier.

## 11. Current boundary

```text
TREE_EXCHANGE_CUT_PRESERVATION                              PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION                      PROVED
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N             PROVED
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N               PROVED
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N                PROVED
FINITE_TREE_EXCHANGE_HANDOFF                                 GREEN
FINITE_DEEP_SHAPE_ABSORPTION                                 GREEN
FINITE_DEEP_SELECTOR_ORIGIN                                  GREEN

NONROOT_UNSHIELDED_CYCLE_TREE_TREE_RESULT_REACHABILITY_ARBITRARY_N OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N                 OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N                  OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION                                   PENDING_NONROOT_ONLY
GLOBAL_CACHE_DAG_LOWER_BOUND                                      OPEN
P_VS_NP                                                           OPEN
```
