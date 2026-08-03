# C024 — Non-root singleton reachability: exact-key induction route

Status: **GRAPH SURGERY PROVED / GT LINEAGE, TREE-RESULT, AND SELECTOR GATES OPEN**  
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

Let `D` be the simple external graph of one legal Resolution parent and suppose `D` is an in-arborescence with root `r`. Let its pivot be `p=a->b`. Suppose the other parent contains the complementary literal `b->a` and a directed cycle. If the simple external resolvent `R` has an underlying tree, then the cycle pivot deletion leaves a directed path from `a` to `b`.

The forest `D-p` has `|V|-2` edges while tree `R` has `|V|-1`, so exactly one cycle-parent edge can be new. The first path edge out of `a` must be that unique edge because `a` has no outgoing tree edge after deleting `p`; every later path edge and every additional external cycle-parent edge duplicates an existing tree edge with the same orientation.

Therefore

```text
R = (D - {p}) union {l}
```

for one unique new edge `l`, and `R` is an in-arborescence with the same root.

```text
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N = PROVED
```

Independent replay:

```text
tree parents                    1440
directed cycle paths          422418
legal resolvents              203816
non-tree resolvents           196020
tree resolvents                 7796
new edge at first path position 7796
violations                         0
```

Exact exchange and common-root preservation are no longer GT-specific proof obligations. GT reachability only has to establish the parent classes and tree result.

## 5. K-normal one-edge exchange growth — proved

For a K-normal in-arborescence `D` and a same-root exact exchange `Q=(D-p)+l`:

```text
nonstar(Q) <= 2
height(Q)  <= 3.
```

If `Q` is not K-normal, contracting either non-star edge returns a K-normal tree.

```text
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N = PROVED
```

Independent labelled gate:

```text
K-normal sources                 119
exact one-edge exchanges        3920
K-normal results                1316
non-K-normal results            2604
marked contractions             5208
violations                         0
```

Canonical result shapes are exactly `(1,0,false)`, `(2,1,true)`, `(2,2,false)`, and `(3,2,false)`.

## 6. Marked singleton-edge absorption — proved

A one-step marked extension replaces one edge of a K-normal tree by a two-edge path and marks either new half-edge `e`. If the marked edge is selected and its endpoint relation components are singleton sets, then:

```text
marked literal satisfied
    -> clause extinct

marked literal falsified
    -> delete marked literal
    -> identify singleton endpoints
    -> graph contraction T/e
    -> recover the K-normal source tree
```

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

## 7. Complete finite Gate-A profile

All 77 fresh non-tail bridge occurrences in exact `GT_4,...,GT_8` replay were classified without assuming exact exchange:

```text
fresh non-tail occurrences                 77
directed-cycle parent                      77
simple in-arborescence spanning parent     51
simple tree/in-arborescence result         69
non-root immediate-local unshielded         3
```

The complete cell table is:

```text
spanning tree  cycle parent  tree result  unshielded  count
false          true          false        false          8
false          true          true         false         18
true           true          true         false         48
true           true          true         true           3
```

Thus every finite non-root unshielded occurrence satisfies the cycle-parent, tree-parent, and tree-result hypotheses. Every finite violation of tree-parent or tree-result is shielded. This is a finite localization certificate, not an arbitrary-`n` theorem.

The 77 occurrences arise from 37 distinct Resolution events; 20 events create more than one fresh bridge occurrence.

## 8. Abstract obstruction: mixed-parent necessity is not graph-theoretic

The finite GT replay has one directed-cycle parent in all 77 fresh non-tail births. However, this cannot be promoted from quotient graph semantics alone.

Exhaust every legal branch-safe directed clause on 3 and 4 singleton quotient vertices, every complementary pivot pair, and every component-spanning resolvent. A bridge occurrence is fresh when the same directed edge was not a bridge in either parent containing it.

The exact result is:

```text
fresh bridge occurrences                 13,896
fresh non-tail occurrences                7,380
fresh tail-singleton occurrences          6,516
```

Fresh non-tail parent pairs:

```text
COMPONENT_SPANNING x COMPONENT_SPANNING    5,304
COMPONENT_SPANNING x DIRECTED_CYCLE         2,076
```

Therefore

```text
ABSTRACT_FRESH_BRIDGE_MIXED_PARENT_NECESSITY = FALSIFIED
```

Legality, connectedness, bridge freshness, and non-tail cut geometry do not imply a directed-cycle parent. Any arbitrary-`n` proof of the GT mixed-parent property must retain exact Policy-0A information:

```text
GT clause origin
frozen Resolution ancestry
pivot schedule
literal polarity
proof provenance
cache-key reachability
```

A proof that forgets this history and keeps only the abstract quotient clause graph is incomplete.

## 9. Finite exact-key handoff and selector evidence

Complete non-root handoff through `GT_8`:

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

Each has source shape `(2,1,true)`, raw/post shape `(3,2,false)`, selected literal `-8`, and selected component sizes `(1,1)`. One polarity makes the clause extinct; the other contracts `-8` and returns shape `(2,1,true)`.

Their selector cell is:

```text
selected frequency       75
competitor frequencies   67,68,68
strict margins            8,7,7
source delta              0,0,0
```

Origin vectors are `(0,2,10,-4,0)` once and `(0,2,10,-5,0)` twice in coordinates `ROOT_NON_MINIMALITY`, `ROOT_TRANSITIVITY`, `LOCAL_RESOLVENT`, `INHERITED_DERIVED`, `OTHER_DERIVED`.

The complete 42-lineage profile is heterogeneous and contains strict margins and least-index ties. Component-pair factorization and a universal origin-vector formula are false.

## 10. Remaining conceptual gates

### Gate A — producer reachability

Gate A is now split into two GT-specific subgates.

#### A1 — mixed-parent lineage reachability

```text
GT_NONROOT_UNSHIELDED_MIXED_PARENT_REACHABILITY_ARBITRARY_N = OPEN
```

Show that every reachable non-root immediate-local unshielded producer is safe or has one legal directed-cycle parent and one component-spanning parent.

This must use GT lineage/history. The abstract spanning-by-spanning counterexamples rule out a pure graph proof.

#### A2 — tree parent/result reachability

```text
GT_NONROOT_UNSHIELDED_TREE_PARENT_RESULT_REACHABILITY_ARBITRARY_N = OPEN
```

Given a reachable mixed-parent producer, show that the spanning parent is a simple K-normal in-arborescence and the external resolvent is a simple tree, or else an existing shield/safe route applies.

After A1 and A2:

```text
NONROOT_UNSHIELDED_CYCLE_TREE_TREE_RESULT_REACHABILITY_ARBITRARY_N
```

follows, and the proved cycle/tree theorem supplies exact same-root exchange automatically.

### Gate B — exposed-subdivision selector dominance

```text
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
```

Every reachable non-root immediate-local unshielded state must select either an already proved safe route or a marked exposed comparison joining singleton relation components.

## 11. Exact-key induction after A1, A2, and B

```text
K
  relevant tree parents are K-normal by induction

K -> R
  A1 gives cycle x spanning parents
  A2 gives K-normal tree parent and tree result
  -> cycle/tree theorem gives same-root exact one-edge exchange
  -> growth theorem gives K-normal or one marked transient layer

R -> P
  post-units do not create new same-cut pairs

P -> B
  Gate B selects a safe diversion or the marked singleton edge

B -> K'
  satisfying polarity kills the clause
  falsifying polarity contracts the marked edge
  -> absorption theorem restores K-normal form
```

Only after all three open subgates close may the following be promoted:

```text
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = PROVED
T3_EXACT_KEY_TEMPORAL_INDUCTION                    = DIRECT
```

## 12. Current boundary

```text
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N             PROVED
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N               PROVED
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N                PROVED
FINITE_GATE_A_PROFILE                                       GREEN
ABSTRACT_FRESH_BRIDGE_MIXED_PARENT_NECESSITY                FALSIFIED

GT_NONROOT_UNSHIELDED_MIXED_PARENT_REACHABILITY_ARBITRARY_N OPEN
GT_NONROOT_UNSHIELDED_TREE_PARENT_RESULT_REACHABILITY_ARBITRARY_N OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N          OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N           OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION                             PENDING_NONROOT_ONLY
GLOBAL_CACHE_DAG_LOWER_BOUND                                OPEN
P_VS_NP                                                     OPEN
```
