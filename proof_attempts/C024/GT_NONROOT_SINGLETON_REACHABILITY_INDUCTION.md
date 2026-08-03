# C024 — Non-root singleton reachability: exact-key induction route

Status: **GRAPH GROWTH AND ABSORPTION PROVED / TWO REACHABILITY GATES OPEN**  
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

Temporary clauses in `R/P` may be structurally deeper than their `K` parents. The required invariant is therefore return to normal form at `K'`, not pointwise monotonicity at every temporary stage.

## 2. Proved dependencies

```text
FROZEN_FRESH_SIDE_BARRIER                         PROVED
POST_UNIT_TOTAL_COMPONENT_COLLAPSE                PROVED
ROOT_BRANCH_HANDOFF                               PROVED_ARBITRARY_N
TREE_EXCHANGE_CUT_PRESERVATION                    PROVED
TWO_NODE_TAIL_WING_HANDOFF                        PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION            PROVED
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

The original root component-spanning in-arborescence clauses are stars. Thus K-normality is the base case.

K-normality is no longer treated as an independent arbitrary-`n` premise. It is the inductive conclusion obtained from the two remaining reachability/selector lemmas together with the proved graph lemmas below.

## 4. K-normal one-edge exchange growth — proved

Let `D` be a finite simple K-normal in-arborescence rooted at `r`, and let

```text
Q = (D - p) + l
```

be an exact one-edge exchange which is again a simple in-arborescence with the same root.

Deleting `p` cannot increase the number of non-star edges, and adding `l` contributes at most one. Therefore

```text
nonstar(Q) <= 2.
```

Every root-directed path of length `h` has exactly `h-1` non-star edges, hence

```text
height(Q) <= 3.
```

If `Q` is not K-normal, then it has exactly two non-star edges. Contracting either non-star edge leaves at most one non-star edge and height at most two, so the contracted tree is K-normal.

```text
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N = PROVED
```

Independent labelled falsification gate through eight vertices:

```text
K-normal sources                 119
exact one-edge exchanges        3920
K-normal results                1316
non-K-normal results            2604
marked contractions             5208
violations                         0
```

Canonical result shapes are exactly:

```text
(1,0,false)
(2,1,true)
(2,2,false)
(3,2,false)
```

Every marked contraction of a non-K-normal result has shape `(2,1,true)`.

This theorem controls shape growth only after the exact same-root one-edge-exchange hypotheses are established.

## 5. Marked singleton-edge absorption — proved

A **one-step marked extension** replaces one edge of a K-normal tree by a two-edge path and marks either new half-edge `e`. Contracting `e` recovers the K-normal source tree.

Assume the marked edge is selected and its endpoint relation components are singleton sets. Then:

```text
marked literal satisfied
    -> clause extinct

marked literal falsified
    -> delete marked literal
    -> identify its singleton endpoints
    -> graph contraction T/e
    -> recover the K-normal source tree
```

Additional child pre-units can only simplify further.

```text
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N = PROVED
```

Independent labelled falsification gate:

```text
source stars                       7
source one-subdivision stars     112
marked extensions                672
marked half-edge branches       1344
violations                         0
```

## 6. Finite exact-key handoff

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

Each has source shape `(2,1,true)`, raw/post shape `(3,2,false)`, selected literal `-8`, and selected component sizes `(1,1)`. One branch polarity makes the clause extinct; the other deletes/contracts `-8` and returns the child exact-key shape to `(2,1,true)`.

This is finite evidence for the arbitrary-`n` reachability statements below, not their proof.

## 7. Selector-origin evidence

For the three deep rows:

```text
selected variable       8
selected frequency     75
competitor frequencies 67,68,68
strict margins          8,7,7
source delta            0,0,0
```

With coordinates

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

The complete 42-lineage finite profile is heterogeneous and contains both strict margins and least-index ties. Therefore component-pair frequency factorization and a universal origin-vector formula are false. Any arbitrary-`n` selector proof must retain clause history, polarity, vertex identity, and exact tie-breaking.

## 8. Two remaining arbitrary-n gates

### Gate A — exact-exchange producer reachability

```text
NONROOT_UNSHIELDED_EXACT_EXCHANGE_REACHABILITY_ARBITRARY_N = OPEN
```

Every arbitrary-`n` reachable non-root immediate-local unshielded producer must be shown either to fall into an already proved safe route or to have:

1. one directed-cycle parent;
2. one K-normal component-spanning in-arborescence parent;
3. a unique external tree pivot;
4. the same root before and after Resolution;
5. a resolvent obtained by deleting that pivot edge and adding exactly one external edge.

Only then does the proved K-normal one-edge growth theorem apply.

### Gate B — exposed-subdivision selector dominance

```text
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
```

For every reachable non-root immediate-local unshielded state, exact Policy-0A must select either:

1. a variable whose branch is already covered by a proved safe route; or
2. a marked exposed comparison joining two singleton relation components.

A falsifier is a reachable state whose exact maximum-frequency/least-index variable avoids every established safe route and is not such a marked singleton comparison.

## 9. Exact-key induction after the two gates

Assuming Gate A and Gate B:

```text
K
  relevant tree parents are K-normal by the induction hypothesis

K -> R
  an unsafe producer is an exact same-root one-edge exchange
  -> proved growth theorem yields K-normal or one marked transient layer

R -> P
  post-units do not create new same-cut pairs
  extinct or otherwise safe clauses leave the tracked route

P -> B
  selector takes a proved safe diversion or the marked singleton edge

B -> K'
  satisfying polarity kills the clause
  falsifying polarity contracts the marked edge
  -> proved absorption theorem restores K-normal form
```

Therefore K-normality propagates from one exact key to the next. It is an inductive consequence, not a third open hypothesis.

After both gates close:

```text
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = PROVED
T3_EXACT_KEY_TEMPORAL_INDUCTION                    = DIRECT
```

Neither conclusion may be promoted earlier.

## 10. Current boundary

```text
TREE_EXCHANGE_CUT_PRESERVATION                         PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION                 PROVED
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N          PROVED
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N           PROVED
FINITE_TREE_EXCHANGE_HANDOFF                            GREEN
FINITE_DEEP_SHAPE_ABSORPTION                            GREEN
FINITE_DEEP_SELECTOR_ORIGIN                             GREEN

NONROOT_UNSHIELDED_EXACT_EXCHANGE_REACHABILITY_ARBITRARY_N OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N         OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N          OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION                           PENDING_NONROOT_ONLY
GLOBAL_CACHE_DAG_LOWER_BOUND                              OPEN
P_VS_NP                                                   OPEN
```
