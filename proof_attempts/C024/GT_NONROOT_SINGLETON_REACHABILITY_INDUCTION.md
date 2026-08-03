# C024 — Non-root singleton reachability: exact-key induction route

Status: **INDUCTION ARCHITECTURE FROZEN / FINAL SELECTOR SUBLEMMA OPEN**  
Scope: the remaining non-root branch handoff in exact Policy-0A on graph
tautologies.

This document does not claim the global graph-tautology lower bound, an
unrestricted Resolution lower bound, a SAT lower bound, or a resolution of
`P` versus `NP`.

## 1. Temporal stages

The induction is over exact cache keys, not over individual frozen Resolution
events.

```text
K   exact entry key after pre-units
R   K plus the frozen one-pass Resolution outputs
P   post-unit residual
B   raw child after the selected branch polarity
K'  next exact key after child pre-units
```

A clause may become structurally more complicated inside `R` or `P`.  The
required invariant is therefore not pointwise monotonicity at every temporary
stage.  It is a return invariant from one exact key to the next.

## 2. Already proved local barriers

The following layers are independent of the remaining selector theorem.

```text
FROZEN_FRESH_SIDE_BARRIER                 PROVED
POST_UNIT_TOTAL_COMPONENT_COLLAPSE        PROVED
ROOT_BRANCH_HANDOFF                       PROVED_ARBITRARY_N
TREE_EXCHANGE_CUT_PRESERVATION            PROVED
TWO_NODE_TAIL_WING_HANDOFF                PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION    PROVED
```

In particular, if the exact selected comparison joins two singleton relation
components, one branch restriction cannot create a new co-eligible same-cut
complementary double-bridge pair from a branch-safe source family.

## 3. Exact-key tree normal form suggested by the complete finite handoff

For a simple component-spanning in-arborescence, record

```text
(height, non-star edge count, one-subdivision-star flag).
```

The complete non-root exact-exchange handoff through `GT_8` gives:

```text
source exact-key shapes
  star                     (1,0,false)   63
  one-subdivision          (2,1,true)    34

raw/post exchange shapes
  star                     (1,0,false)   49
  one-subdivision          (2,1,true)    45
  transient deep           (3,2,false)    3

child exact-key shapes
  star                     (1,0,false)   42
  one-subdivision          (2,1,true)    25
  deep                                      0
```

Thus the naive statement

```text
Resolution never creates a deeper tree
```

is false.  The finite evidence supports the weaker exact-key invariant:

### K-normal form

Every relevant in-arborescence parent present in an exact key is a star or a
one-subdivision star.

```text
K_TREE_NORMAL_FORM_ARBITRARY_N = OPEN
```

The finite handoff is a falsification gate, not an arbitrary-`n` proof.

## 4. Transient one-step growth

An exact transitivity/tree exchange may replace one edge of a one-subdivision
parent and temporarily produce a height-three tree with two non-star edges.
The exact `GT_8` deep cell consists of three resolvents:

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

All three have:

```text
source shape                     (2,1,true)
raw/post shape                   (3,2,false)
selected variable                8
selected literal                 -8
selected component sizes         (1,1)
```

A general induction route needs the following bounded-growth statement rather
than global shape monotonicity:

### One-exchange growth

Starting from a K-normal relevant tree parent, every exact local
transitivity/tree exchange is either already safe or creates at most one marked
transient subdivision layer whose exposed comparison is identifiable in the
resolvent.

```text
ONE_EXCHANGE_MARKED_GROWTH_ARBITRARY_N = OPEN
```

Tree-exchange cut preservation is already proved, but it does not by itself
bound the number of subdivision layers.

## 5. Singleton-edge shape absorption

For every finite deep row, the selected comparison is the marked literal in the
resolvent and joins two singleton relation components.  The two branch
polarities have the exact fates

```text
selected literal satisfied
    -> CLAUSE_EXTINCT

selected literal falsified
    -> delete the selected literal
    -> contract its singleton endpoints
    -> child exact-key tree shape (2,1,true)
```

Hence the deep layer is transient and the next exact key returns to the
one-subdivision normal form.

This motivates the pure graph/encoding sublemma:

### Marked singleton-edge absorption

Let a branch-safe marked in-arborescence contain the selected comparison as the
exposed edge of the additional transient subdivision layer.  If its endpoints
are singleton relation components, then one branch polarity makes the clause
extinct and the other deletes/contracts the marked edge, reducing the marked
tree complexity before `K'`.

The finite transcript instantiates this statement three times.  The arbitrary-
`n` theorem under a fully formal marked-tree definition remains to be written.

```text
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N = OPEN
FINITE_DEEP_SHAPE_ABSORPTION                  = GREEN
```

This sublemma is stronger than ordinary same-cut noncreation because it also
controls the tree shape transported to the next exact key.

## 6. Selector-origin evidence

The final obstacle is not the branch operation.  It is proving that exact
Policy-0A selects the marked singleton comparison, or selects another variable
whose route is already covered by a proved safety template.

For the three deep `GT_8` rows:

```text
selected variable       8
selected frequency     75
strongest competitors  67,68,68
strict margins          8,7,7
```

With origin coordinates ordered as

```text
ROOT_NON_MINIMALITY,
ROOT_TRANSITIVITY,
LOCAL_RESOLVENT,
INHERITED_DERIVED,
OTHER_DERIVED,
```

the selected-minus-competitor vectors are

```text
(0,2,10,-4,0)   once
(0,2,10,-5,0)   twice.
```

The tracked deep clause itself gives no frequency advantage:

```text
source_delta = 0
```

The strict selector margin instead comes from the frozen local block:
`ROOT_TRANSITIVITY + LOCAL_RESOLVENT`, partially offset by inherited derived
clauses.

The complete 42-lineage finite profile is heterogeneous.  It includes strict
margins and lexicographic ties, with many different origin vectors.  Therefore
one universal component-pair or one universal origin-vector formula is false.
Any arbitrary-`n` theorem must retain clause history, polarity, vertex identity,
and exact tie-breaking.

## 7. Final selector theorem

The minimal remaining reachability statement can be formulated as follows.

### Exposed-subdivision selector dominance or safe diversion

For every arbitrary-`n` reachable non-root immediate-local unshielded
occurrence, exact Policy-0A does one of the following:

1. selects a variable whose branch is already covered by a proved safe route;
2. selects the marked exposed comparison of the transient tree, and that
   comparison joins two singleton relation components.

Equivalently, a falsifier must provide a reachable non-root unshielded state in
which every selected route avoids the existing safety templates and the exact
maximum-frequency/least-index variable is not a singleton marked comparison.

```text
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
```

This theorem is history-sensitive.  Quotient-component sizes alone cannot prove
it because component-pair frequency factorization has an exact finite
counterexample.

## 8. Exact-key induction after the selector theorem

Assuming the three pending arbitrary-`n` sublemmas

```text
K_TREE_NORMAL_FORM_ARBITRARY_N
ONE_EXCHANGE_MARKED_GROWTH_ARBITRARY_N
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N
```

and the marked singleton-edge absorption lemma, the non-root induction is:

```text
K
  relevant trees are K-normal

K -> R
  frozen Resolution preserves existing safe routes;
  an exact exchange may create only a marked transient layer

R -> P
  post-units cannot create a new same-cut pair;
  extinct/safe clauses leave the tracked route

P -> B
  selector takes a proved safe diversion or the marked singleton edge

B -> K'
  satisfying polarity kills the clause;
  falsifying polarity contracts the marked singleton edge;
  the transported tree returns to K-normal form
```

Then

```text
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = PROVED
T3_EXACT_KEY_TEMPORAL_INDUCTION                    = DIRECT
```

Neither conclusion may be promoted before every pending sublemma has an
independent proof or complete replayable certificate.

## 9. Current boundary

```text
TREE_EXCHANGE_CUT_PRESERVATION             PROVED
SINGLETON_BRANCH_SAME_CUT_PRESERVATION     PROVED
FINITE_TREE_EXCHANGE_HANDOFF                GREEN
FINITE_DEEP_SHAPE_ABSORPTION                GREEN
FINITE_DEEP_SELECTOR_ORIGIN                 GREEN

K_TREE_NORMAL_FORM_ARBITRARY_N              OPEN
ONE_EXCHANGE_MARKED_GROWTH_ARBITRARY_N      OPEN
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION             PENDING_NONROOT_ONLY
GLOBAL_CACHE_DAG_LOWER_BOUND                OPEN
P_VS_NP                                     OPEN
```
